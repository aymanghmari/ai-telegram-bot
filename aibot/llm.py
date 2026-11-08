"""Provider-agnostic LLM layer.

The bot's brain depends on the ``LLMProvider`` interface, never on a vendor.
``MockProvider`` is offline and deterministic (no key). A single
``OpenAICompatibleProvider`` covers OpenAI, Groq and Ollama — they all speak the
same chat API, only the base URL and key differ — and ``AnthropicProvider``
covers Claude. All adapters import their SDK lazily.
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
    """Offline stand-in: echoes the last user message. No network, no keys."""

    def reply(self, messages: list[Message]) -> str:
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        return f"(demo) You said: {last_user}"


class OpenAICompatibleProvider:
    """Works with any OpenAI-compatible chat API: OpenAI, Groq, Ollama, ...

    Only the base URL and API key change between them; the request is identical.
    """

    def __init__(self, model: str, api_key: str, base_url: str | None = None):
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    def reply(self, messages: list[Message]) -> str:
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=0.6,
        )
        return (resp.choices[0].message.content or "").strip()


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
        return "".join(b.text for b in resp.content if b.type == "text").strip()


def provider_from_env() -> LLMProvider:
    """Pick a provider from AI_PROVIDER (default: mock). AI_MODEL overrides the
    default model for whichever provider is chosen."""
    choice = os.environ.get("AI_PROVIDER", "mock").lower()
    model = os.environ.get("AI_MODEL", "").strip()

    if choice == "openai":
        return OpenAICompatibleProvider(model or "gpt-4o-mini",
                                        os.environ["OPENAI_API_KEY"])
    if choice == "groq":
        return OpenAICompatibleProvider(model or "openai/gpt-oss-20b",
                                        os.environ["GROQ_API_KEY"],
                                        base_url="https://api.groq.com/openai/v1")
    if choice == "ollama":
        # Local, free. Needs `ollama serve` running and the model pulled.
        return OpenAICompatibleProvider(model or "llama3.2",
                                        api_key="ollama",
                                        base_url="http://localhost:11434/v1")
    if choice == "anthropic":
        return AnthropicProvider()
    return MockProvider()
