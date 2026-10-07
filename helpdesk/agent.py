import os

from google.adk.agents import LlmAgent

from .prompts import COORDINATOR_INSTRUCTION

MODEL = "gemini-2.5-flash"

if not os.environ.get("GOOGLE_API_KEY"):
    raise RuntimeError("GOOGLE_API_KEY is not set. Copy .env.example to helpdesk/.env and add your AI Studio key.")

root_agent = LlmAgent(
    name="coordinator",
    model=MODEL,
    description="Acme Corp employee helpdesk coordinator.",
    instruction=COORDINATOR_INSTRUCTION,
)
