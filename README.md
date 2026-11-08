# ai-telegram-bot

A clean, **LLM-powered Telegram chat bot** in Python. The conversation logic
(the *brain*) is separate from the Telegram transport, so the logic is
unit-tested offline and the model provider is swappable without touching the bot.

## Features

- 💬 Replies to any message using an LLM, with short per-user memory
- 🧩 Commands: `/start`, `/help`, `/reset`
- 🔌 Swappable provider: **mock** (offline, no key), **Groq**, **Ollama**,
  **OpenAI**, or **Anthropic** — all behind one tiny interface
- 🧪 Brain unit-tested with **no network and no API key** (7 passing tests)
- 🔒 Secrets stay in `.env` — never in the code

## Architecture

```
 Telegram  ──►  bot.py  ──►  ChatBrain (brain.py)  ──►  LLMProvider (llm.py)
 (transport)   handlers      history + prompt           mock / groq / ollama / openai / anthropic
```

`bot.py` is the only file that knows about Telegram. Everything worth testing
lives in `brain.py`, which knows nothing about Telegram — that separation is
what makes the project easy to test and extend.

## Setup

**1. Create a bot** — message **@BotFather** on Telegram, send `/newbot`, and
copy the token.

**2. Install**

```bash
pip install -e .            # core: python-telegram-bot
pip install -e ".[openai]"  # needed for Groq / Ollama / OpenAI (OpenAI-compatible)
```

**3. Configure** — copy `.env.example` to `.env`, paste your bot token, and pick
a provider:

```
TELEGRAM_BOT_TOKEN=...from BotFather...
AI_PROVIDER=groq
GROQ_API_KEY=...from console.groq.com...
AI_MODEL=openai/gpt-oss-20b
```

- **Groq** (free, fast): some `llama-*` models are enterprise-gated; a free key
  can use `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, or `qwen/qwen3.8-27b`.
  Run `python list_models.py` to see which models your key can access.
- **Ollama** (free, local): set `AI_PROVIDER=ollama` and `AI_MODEL=llama3.2`
  with Ollama running locally.
- **mock** (default): offline echo, no key — for testing the plumbing.

**4. Run**

```bash
python -m aibot
```

## Tests

```bash
pip install -e ".[dev]"
pytest -q        # 7 passing — brain logic, history, reset, isolation
```

## License

MIT © Ayman Ghmari
