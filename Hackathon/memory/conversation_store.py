"""
Persistent Conversation Memory
================================
Stores conversation history to disk so ARIA remembers past interactions
across sessions — giving the system true continuity between conversations.

Storage location: ~/.financeai/
  - history.json   — all conversation messages with timestamps
  - profile.json   — extracted user financial profile (income, goals, etc.)

Usage:
    from memory.conversation_store import ConversationMemory

    mem = ConversationMemory()
    mem.add_message("user", "My income is $5,000/month")
    mem.add_message("assistant", "Got it. Let me analyse your budget...")
    msgs = mem.get_context_messages()   # [{role, content}, ...]
    print(mem.get_summary_line())       # "12 prior exchanges (last: 2026-03-21)"
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

MEMORY_DIR = Path.home() / ".financeai"
HISTORY_FILE = MEMORY_DIR / "history.json"
PROFILE_FILE = MEMORY_DIR / "profile.json"

# Maximum number of messages included in the live context window.
# Each exchange = 2 messages (user + assistant). 60 = ~30 exchanges.
# Older messages are stored on disk but not sent to Claude to manage tokens.
MAX_CONTEXT_MESSAGES = 60


class ConversationMemory:
    """
    Persistent conversation store for cross-session continuity.

    - Automatically saves to ~/.financeai/ after every turn.
    - Loads prior history on construction so ARIA remembers past sessions.
    - Keeps the last MAX_CONTEXT_MESSAGES messages in the live Claude context.
    - Stores a user financial profile separately for quick injection.
    """

    def __init__(self):
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        self._messages: list[dict] = []         # [{role, content, timestamp}]
        self.user_profile: dict[str, Any] = {}
        self._load()

    # ── Persistence ─────────────────────────────────────────────────────────

    def _load(self):
        if HISTORY_FILE.exists():
            try:
                data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
                self._messages = data.get("messages", [])
            except (json.JSONDecodeError, OSError):
                self._messages = []

        if PROFILE_FILE.exists():
            try:
                self.user_profile = json.loads(
                    PROFILE_FILE.read_text(encoding="utf-8")
                )
            except (json.JSONDecodeError, OSError):
                self.user_profile = {}

    def _save_history(self):
        try:
            HISTORY_FILE.write_text(
                json.dumps(
                    {
                        "messages": self._messages,
                        "last_updated": datetime.now().isoformat(),
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        except OSError:
            pass  # non-fatal

    def _save_profile(self):
        try:
            PROFILE_FILE.write_text(
                json.dumps(self.user_profile, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError:
            pass

    # ── Writing ──────────────────────────────────────────────────────────────

    def add_message(self, role: str, content: str):
        """Append a user or assistant turn and persist to disk immediately."""
        self._messages.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self._save_history()

    def update_profile(self, key: str, value: Any):
        """Store a user financial profile field (e.g. monthly_income, goals)."""
        self.user_profile[key] = value
        self._save_profile()

    # ── Reading ──────────────────────────────────────────────────────────────

    def get_context_messages(self) -> list[dict]:
        """
        Return the most recent messages in Claude API format (role + content only).
        Limited to MAX_CONTEXT_MESSAGES to keep token usage reasonable.
        """
        recent = self._messages[-MAX_CONTEXT_MESSAGES:]
        return [{"role": m["role"], "content": m["content"]} for m in recent]

    def get_profile_block(self) -> str:
        """
        Format the user profile as a readable block for injection into the
        system prompt. Returns empty string if no profile data exists.
        """
        if not self.user_profile:
            return ""
        lines = ["KNOWN USER PROFILE (remembered from prior conversations):"]
        for k, v in self.user_profile.items():
            lines.append(f"  • {k}: {v}")
        return "\n".join(lines)

    def total_exchanges(self) -> int:
        """Number of complete user turns in history."""
        return sum(1 for m in self._messages if m["role"] == "user")

    def total_messages(self) -> int:
        return len(self._messages)

    def last_seen(self) -> str:
        """ISO date string of the most recent message, or empty string."""
        if not self._messages:
            return ""
        return self._messages[-1].get("timestamp", "")[:10]

    def is_empty(self) -> bool:
        return len(self._messages) == 0

    def get_summary_line(self) -> str:
        """One-line status string for display at startup."""
        n = self.total_exchanges()
        if n == 0:
            return "No prior conversations found."
        ls = self.last_seen()
        return f"{n} prior exchange{'s' if n != 1 else ''} remembered (last active: {ls})."

    def get_recent_user_messages(self, n: int = 5) -> list[dict]:
        """Return the last n user messages for the 'history' display command."""
        user_msgs = [m for m in self._messages if m["role"] == "user"]
        return user_msgs[-n:]

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def clear(self):
        """Erase all history and profile data from memory and disk."""
        self._messages = []
        self.user_profile = {}
        self._save_history()
        self._save_profile()
