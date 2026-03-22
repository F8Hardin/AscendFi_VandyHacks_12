"""
Agent Communication Bus
=======================
Thread-safe singleton message bus for inter-agent context sharing.

How it works:
  1. After each agent finishes, it publishes a one-sentence summary of its
     findings to the bus (handled automatically by BaseFinancialAgent).
  2. Before each subsequent agent starts, the bus injects available peer
     summaries into the top of the user message so the agent knows what
     other agents have already found.
  3. The Supervisor can read all summaries for cross-agent synthesis.

Usage:
    from agents.agent_bus import bus

    # Read peer context before running (auto-injected by BaseFinancialAgent)
    context_block = bus.get_peer_context_block("Risk Agent")

    # Publish after running (auto-called by BaseFinancialAgent)
    bus.publish("Risk Agent", "risk_assessment", data, summary="67% overdraft risk in 30 days")

    # Read what a specific agent found
    ctx = bus.get_agent_context("Behaviour Agent")

    # Read all peer contexts (used by Supervisor for synthesis)
    all_ctx = bus.get_all_agent_contexts()

    # Set/get session-level data (user profile, income, etc.)
    bus.set_session_data("monthly_income", 5000)
    income = bus.get_session_data("monthly_income")

    # Clear between sessions
    bus.reset()
"""

import threading
import time
from typing import Any, Optional


class AgentBus:
    """
    Thread-safe singleton communication bus for inter-agent information sharing.

    Each message on the bus has:
        sender    – which agent published it
        topic     – message category (e.g. "risk_assessment", "market_signal")
        summary   – one sentence for peer injection
        data      – full structured payload (kept for detailed queries)
        timestamp – epoch float

    The supervisor agent has special access to all_agent_contexts() so it can
    synthesise insights from all specialists in its final response.
    """

    _instance: "Optional[AgentBus]" = None
    _class_lock = threading.Lock()

    def __new__(cls):
        with cls._class_lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance._initialized = False
                cls._instance = instance
            return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._messages: dict[str, list[dict]] = {}       # topic → messages
        self._agent_context: dict[str, dict] = {}        # agent_name → latest
        self._session_data: dict[str, Any] = {}          # free-form session kv
        self._lock = threading.Lock()
        self._initialized = True

    # ── Publishing ─────────────────────────────────────────────────────────────

    def publish(
        self,
        sender: str,
        topic: str,
        data: Any = None,
        summary: str = "",
    ) -> None:
        """
        Publish a finding. Called automatically by BaseFinancialAgent after each run.

        sender:  agent name, e.g. "Risk Agent"
        topic:   category e.g. "risk_assessment", "debt_analysis", "market_signal"
        data:    full payload (dict / list / str) — stored but not injected verbatim
        summary: ≤1 sentence shown to peer agents, e.g. "Overdraft risk 67% in 30 days"
        """
        message = {
            "sender":    sender,
            "topic":     topic,
            "summary":   summary,
            "data":      data,
            "timestamp": time.time(),
        }
        with self._lock:
            self._messages.setdefault(topic, []).append(message)
            # Cap per-topic inbox to avoid memory bloat
            if len(self._messages[topic]) > 20:
                self._messages[topic] = self._messages[topic][-20:]

            # Store latest per-agent context for fast lookup
            self._agent_context[sender] = {
                "summary":   summary,
                "topic":     topic,
                "timestamp": time.time(),
            }

    # ── Reading ────────────────────────────────────────────────────────────────

    def get_topic_messages(self, topic: str, limit: int = 5) -> list[dict]:
        """Return the N most recent messages on a topic."""
        return self._messages.get(topic, [])[-limit:]

    def get_agent_context(self, agent_name: str) -> Optional[dict]:
        """Return the latest context published by a specific agent."""
        return self._agent_context.get(agent_name)

    def get_all_agent_contexts(self) -> dict[str, dict]:
        """Return latest context from all agents (used by Supervisor for synthesis)."""
        with self._lock:
            return dict(self._agent_context)

    def get_peer_context_block(self, requesting_agent: str) -> str:
        """
        Build a formatted text block of peer-agent summaries for injection
        into an agent's user message. Excludes the requesting agent itself.
        Returns empty string when no peer context is available.
        """
        contexts = self.get_all_agent_contexts()
        peers = {
            name: ctx
            for name, ctx in contexts.items()
            if name != requesting_agent and ctx.get("summary")
        }

        if not peers:
            return ""

        lines = [
            "---",
            "Context from peer agents (incorporate into your analysis):",
        ]
        for agent_name, ctx in peers.items():
            lines.append(f"• {agent_name}: {ctx['summary']}")
        lines.append("---")

        return "\n".join(lines)

    # ── Session data ───────────────────────────────────────────────────────────

    def set_session_data(self, key: str, value: Any) -> None:
        """Store session-level data accessible by all agents (e.g. user profile)."""
        with self._lock:
            self._session_data[key] = value

    def get_session_data(self, key: str, default: Any = None) -> Any:
        """Retrieve session-level data."""
        return self._session_data.get(key, default)

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def reset(self) -> None:
        """Clear all messages, context, and session data. Call between user sessions."""
        with self._lock:
            self._messages.clear()
            self._agent_context.clear()
            self._session_data.clear()

    def status(self) -> dict:
        """Return current bus state (useful for debugging)."""
        with self._lock:
            return {
                "agents_with_context": list(self._agent_context.keys()),
                "topics":              list(self._messages.keys()),
                "message_counts":      {t: len(m) for t, m in self._messages.items()},
                "session_keys":        list(self._session_data.keys()),
            }


# ── Global singleton ──────────────────────────────────────────────────────────
# Import this everywhere:  from agents.agent_bus import bus
bus = AgentBus()
