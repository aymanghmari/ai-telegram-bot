"""Telegram transport — thin wiring around ChatBrain.

This is the only module that imports ``python-telegram-bot``. It registers the
commands and hands plain messages to the brain. Keeping it thin is the point:
all the logic worth testing lives in brain.py.
"""
from __future__ import annotations

import asyncio
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .brain import ChatBrain
from .config import load_dotenv, telegram_token
from .llm import provider_from_env

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s | %(message)s", level=logging.INFO
)
log = logging.getLogger("aibot")

HELP = (
    "I'm an AI chat bot. Just send me a message and I'll reply.\n\n"
    "/start - say hello\n"
    "/help - show this help\n"
    "/reset - forget our conversation so far"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hi! I'm your AI assistant. Ask me anything.")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    brain: ChatBrain = context.application.bot_data["brain"]
    brain.reset(update.effective_user.id)
    await update.message.reply_text("Done - I've cleared our conversation.")


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    brain: ChatBrain = context.application.bot_data["brain"]
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    reply = brain.handle(update.effective_user.id, update.message.text)
    await update.message.reply_text(reply)


def build_app() -> Application:
    load_dotenv()
    app = Application.builder().token(telegram_token()).build()
    app.bot_data["brain"] = ChatBrain(provider_from_env())
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    return app


def _ensure_event_loop() -> None:
    """Python 3.12+ no longer auto-creates an event loop for a bare
    asyncio.get_event_loop() call, and 3.14 raises RuntimeError. PTB's
    run_polling() expects one to exist, so create it here if needed."""
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())


def main() -> None:
    log.info("Starting bot (Ctrl+C to stop)...")
    _ensure_event_loop()
    build_app().run_polling()


if __name__ == "__main__":
    main()
