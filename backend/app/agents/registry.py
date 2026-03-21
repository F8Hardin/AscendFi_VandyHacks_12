"""
Agent registry — maps agent names to classes and manages the active agent.

To swap agents at runtime, set the ACTIVE_AGENT env var or call set_active_agent().
To add a new agent: import its class and add it to AGENT_REGISTRY.
"""

import os
from app.agents.base import FinancialAgentBase
from app.agents.claude_agent import ClaudeAgent
from app.agents.lm_studio_agent import LMStudioAgent

AGENT_REGISTRY: dict[str, type[FinancialAgentBase]] = {
    #"claude": ClaudeAgent,
    "lm_studio": LMStudioAgent,
}

_active_agent: FinancialAgentBase | None = None


def get_agent() -> FinancialAgentBase:
    global _active_agent
    if _active_agent is None:
        name = os.getenv("ACTIVE_AGENT", "lm_studio")
        cls = AGENT_REGISTRY.get(name)
        if cls is None:
            raise ValueError(
                f"Unknown agent '{name}'. Available: {list(AGENT_REGISTRY.keys())}"
            )
        _active_agent = cls()
    return _active_agent


def set_active_agent(name: str) -> None:
    global _active_agent
    cls = AGENT_REGISTRY.get(name)
    if cls is None:
        raise ValueError(
            f"Unknown agent '{name}'. Available: {list(AGENT_REGISTRY.keys())}"
        )
    _active_agent = cls()


def list_agents() -> list[str]:
    return list(AGENT_REGISTRY.keys())
