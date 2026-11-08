"""ai-telegram-bot — a clean, LLM-powered Telegram chat bot in Python.

The brain (conversation logic) is separate from the Telegram transport, so the
logic is unit-tested offline and the model provider is swappable (OpenAI, Groq,
Ollama, Anthropic, or an offline mock).
"""
from .brain import ChatBrain
from .llm import (
    AnthropicProvider,
    LLMProvider,
    Message,
    MockProvider,
    OpenAICompatibleProvider,
)

__version__ = "0.2.0"
__all__ = [
    "ChatBrain",
    "LLMProvider", "Message", "MockProvider",
    "OpenAICompatibleProvider", "AnthropicProvider",
]
