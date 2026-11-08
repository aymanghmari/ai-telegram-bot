# ai-telegram-bot

A clean, **LLM-powered Telegram chat bot** in Python. The conversation logic
(the *brain*) is separate from the Telegram transport, so the logic is
unit-tested offline and the model provider (OpenAI, Anthropic, or an offline
mock) is swappable without touching the bot.

## Features

- 💬 Replies to any message using an LLM, with short per-user memory
- 🧩 Commands: `/start`, `/help`, `/reset`
- 🔌 Swappable provider: `mock` (offline, no key), `openai`, or `anthropic`
- 🧪 Brain unit-tested with **no network and no API key** (7 passing tests)
- 🔒 Secrets stay in `.env` — never in the code

## Architecture

```
 Telegram  ──►  bot.py  ──►  ChatBrain (brain.py)  ──►  LLMProvider (llm.py)
 (transport)   handlers      history + prompt           mock / openai / anthropic
```

`bot.py` is the only file that knows about Telegram. Everything worth testing
lives in `brain.py`, which knows nothing about Telegram — that separation is
what makes the project easy to test and extend.

## Setup

**1. Create a bot and get a token** — in Telegram, message **@BotFather**, send
`/newbot`, follow the prompts, and copy the token it gives you.

**2. Install**

```bash
git clone https://github.com/aymanghmari/ai-telegram-bot.git
cd ai-telegram-bot
pip install -e .            # installs python-telegram-bot
```

**3. Configure**

```bash
cp .env.example .env        # Windows: copy .env.example .env
# edit .env and paste your token into TELEGRAM_BOT_TOKEN
```

**4. Run**

```bash
python -m aibot
```

Open Telegram, find your bot, and say hi. With `AI_PROVIDER=mock` (the default)
it echoes your message so you can confirm the plumbing works before adding a
real model.

### Using a real model

Set these in `.env`, then `pip install -e ".[openai]"` (or `".[anthropic]"`):

```
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

## Tests

```bash
pip install -e ".[dev]"
pytest -q        # 7 passing — brain logic, history, reset, isolation
```

## License

MIT © Ayman Ghmari
