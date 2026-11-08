"""Provider-agnostic LLM layer.

The bot's brain depends on the ``LLMProvider`` interface, never on a vendor.
``MockProvider`` is offline and deterministic, so the brain can be tested and
demoed with no API key; the OpenAI and Anthropic adapters are imported lazily.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class Message:
    role: str   # "system" | "user" | "assistant"
    content: str


@runtime_checkable
class LLMProvider(Protocol):
    def reply(self, messages: list[Message]) -> str:
        ...


class MockProvider:
    """Offline stand-in: echoes the last user message. No network, no keys.

    Good enough to prove the Telegram wiring and the conversation flow work
    before you plug in a real model.
    """

    def reply(self, messages: list[Message]) -> str:
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        return f"(demo) You said: {last_user}"


class OpenAIProvider:
    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None):
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key or os.environ["OPENAI_API_KEY"])
        self._model = model

    def reply(self, messages: list[Message]) -> str:
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=0.6,
        )
        return resp.choices[0].message.content or ""


class AnthropicProvider:
    def __init__(self, model: str = "claude-3-5-sonnet-latest", api_key: str | None = None):
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"])
        self._model = model

    def reply(self, messages: list[Message]) -> str:
        system = " ".join(m.content for m in messages if m.role == "system")
        convo = [{"role": m.role, "content": m.content}
                 for m in messages if m.role in ("user", "assistant")]
        resp = self._client.messages.create(
            model=self._model, system=system or None, max_tokens=1024, messages=convo
        )
        return "".join(b.text for b in resp.content if b.type == "text")


def provider_from_env() -> LLMProvider:
    """Pick a provider from the AI_PROVIDER env var (default: mock)."""
    choice = os.environ.get("AI_PROVIDER", "mock").lower()
    if choice == "openai":
        return OpenAIProvider()
    if choice == "anthropic":
        return AnthropicProvider()
    return MockProvider()
