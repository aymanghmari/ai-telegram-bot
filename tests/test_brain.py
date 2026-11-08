"""Tests for the brain — offline, no Telegram, no network, no API key."""
from aibot import ChatBrain, MockProvider
from aibot.llm import LLMProvider, Message


def _brain(max_turns: int = 10) -> ChatBrain:
    return ChatBrain(MockProvider(), max_turns=max_turns)


def test_reply_uses_provider():
    brain = _brain()
    assert brain.handle(1, "hello") == "(demo) You said: hello"


def test_history_grows_with_each_exchange():
    brain = _brain()
    brain.handle(7, "first")
    brain.handle(7, "second")
    # two exchanges = 4 messages (user+assistant each)
    assert brain.history_len(7) == 4


def test_history_is_capped():
    brain = _brain(max_turns=2)  # keep 2 exchanges = 4 messages max
    for i in range(5):
        brain.handle(1, f"msg {i}")
    assert brain.history_len(1) == 4


def test_users_are_isolated():
    brain = _brain()
    brain.handle(1, "a")
    brain.handle(2, "b")
    assert brain.history_len(1) == 2
    assert brain.history_len(2) == 2


def test_reset_clears_history():
    brain = _brain()
    brain.handle(1, "remember this")
    brain.reset(1)
    assert brain.history_len(1) == 0


def test_system_prompt_is_sent_first():
    captured: list[list[Message]] = []

    class Spy:
        def reply(self, messages):
            captured.append(list(messages))
            return "ok"

    ChatBrain(Spy()).handle(1, "hi")
    assert captured[0][0].role == "system"
    assert captured[0][-1].content == "hi"


def test_mock_provider_satisfies_protocol():
    assert isinstance(MockProvider(), LLMProvider)
