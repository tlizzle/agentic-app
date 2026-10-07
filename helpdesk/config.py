import os

from google.adk.models.google_llm import Gemini
from google.genai import types

# Free-tier quotas are per model per day and small (gemini-3.5-flash: 20 requests/day when this was built).
# Switch models without touching code: HELPDESK_MODEL=gemini-3.5-flash-lite in helpdesk/.env.
MODEL_NAME = os.environ.get("HELPDESK_MODEL", "gemini-3.5-flash-lite")
EMBEDDING_MODEL = "gemini-embedding-001"

# The free tier also returns transient 503/429 under load; retry a few times instead of failing the turn.
MODEL = Gemini(
    model=MODEL_NAME,
    retry_options=types.HttpRetryOptions(attempts=4, initial_delay=1, max_delay=6, http_status_codes=[429, 503]),
)


def require_api_key() -> None:
    if not os.environ.get("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is not set. Copy .env.example to helpdesk/.env and add your AI Studio key.")
