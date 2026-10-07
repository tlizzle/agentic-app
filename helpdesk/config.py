import os

MODEL = "gemini-3.8-flash"
EMBEDDING_MODEL = "gemini-embedding-001"


def require_api_key() -> None:
    if not os.environ.get("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is not set. Copy .env.example to helpdesk/.env and add your AI Studio key.")
