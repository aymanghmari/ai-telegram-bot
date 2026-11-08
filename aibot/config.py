"""Configuration, read from environment variables (and an optional .env file).

Secrets never live in the code. Copy .env.example to .env and fill it in, or
export the variables in your shell. See README.md.
"""
from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: str = ".env") -> None:
    """Minimal .env loader (no dependency). Ignores missing files and comments."""
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def telegram_token() -> str:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "TELEGRAM_BOT_TOKEN is not set. Get one from @BotFather on Telegram, "
            "then put it in a .env file or export it. See README.md."
        )
    return token
