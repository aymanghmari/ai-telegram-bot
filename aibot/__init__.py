"""ai-telegram-bot — a clean, LLM-powered Telegram chat bot in Python.

The brain (conversation logic) is separate from the Telegram transport, so the
logic is unit-tested offline and the model provider is swappable.
"""
from .brain import ChatBrain
from .llm import AnthropicProvider, LLMProvider, Message, MockProvider, OpenAIProvider

__version__ = "0.1.0"
__all__ = [
    "ChatBrain",
    "LLMProvider", "Message", "MockProvider", "OpenAIProvider", "AnthropicProvider",
]
