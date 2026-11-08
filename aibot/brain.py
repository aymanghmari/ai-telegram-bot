"""The bot's brain — pure conversation logic, no Telegram, no network.

``ChatBrain`` keeps a short per-user history and turns an incoming message into
a reply via the injected ``LLMProvider``. Because it knows nothing about
Telegram, it can be unit-tested on its own (see tests/test_brain.py).
"""
from __future__ import annotations

from collections import defaultdict, deque

from .llm import LLMProvider, Message

DEFAULT_SYSTEM = (
    "You are a helpful, concise assistant chatting with a user on Telegram. "
    "Keep replies short and friendly."
)


class ChatBrain:
    def __init__(self, provider: LLMProvider, system_prompt: str = DEFAULT_SYSTEM,
                 max_turns: int = 10):
        self._provider = provider
        self._system = Message("system", system_prompt)
        # Keep the last ``max_turns`` user+assistant messages per user.
        self._history: dict[int, deque[Message]] = defaultdict(
            lambda: deque(maxlen=max_turns * 2)
        )

    def handle(self, user_id: int, text: str) -> str:
        """Record the user's message, ask the model, remember the reply."""
        history = self._history[user_id]
        history.append(Message("user", text))

        messages = [self._system, *history]
        reply = self._provider.reply(messages).strip()

        history.append(Message("assistant", reply))
        return reply

    def reset(self, user_id: int) -> None:
        """Forget a user's conversation history."""
        self._history.pop(user_id, None)

    def history_len(self, user_id: int) -> int:
        """Number of stored messages for a user (handy for tests/debugging)."""
        return len(self._history.get(user_id, ()))
