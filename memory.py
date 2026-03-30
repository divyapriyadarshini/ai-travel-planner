"""
Conversation Memory — stores past interactions so agents can
adapt based on follow-up requests like "make it cheaper".
"""
from typing import List, Tuple


class ConversationMemory:
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self._history: List[Tuple[str, str]] = []

    def add(self, user_msg: str, assistant_msg: str) -> None:
        self._history.append((user_msg, assistant_msg))
        if len(self._history) > self.max_turns:
            self._history = self._history[-self.max_turns:]

    def get_context(self) -> str:
        if not self._history:
            return "No previous context."
        lines = []
        for i, (u, a) in enumerate(self._history, 1):
            lines.append(f"[Turn {i}]")
            lines.append(f"User: {u}")
            a_short = a[:500] + "..." if len(a) > 500 else a
            lines.append(f"Assistant: {a_short}")
        return "\n".join(lines)

    def clear(self) -> None:
        self._history = []

    def __len__(self) -> int:
        return len(self._history)