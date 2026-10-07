import os

# helpdesk/__init__.py imports agent.py, which refuses to load without a key. Tests never call Gemini.
os.environ.setdefault("GOOGLE_API_KEY", "test-key-not-used")
