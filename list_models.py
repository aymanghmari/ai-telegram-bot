"""Diagnostic: list the models your Groq API key can actually access."""
import os
from aibot.config import load_dotenv

load_dotenv()
key = os.environ.get("GROQ_API_KEY", "").strip()
if not key:
    raise SystemExit("No GROQ_API_KEY found in .env")

from openai import OpenAI

client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
try:
    models = client.models.list()
    ids = sorted(m.id for m in models.data)
    print(f"Your Groq key can access {len(ids)} model(s):")
    for i in ids:
        print("  -", i)
except Exception as e:
    print("ERROR listing models:", type(e).__name__, "-", str(e))
