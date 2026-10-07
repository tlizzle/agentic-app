from google.adk.agents import LlmAgent

from .config import MODEL, require_api_key
from .prompts import COORDINATOR_INSTRUCTION

require_api_key()

root_agent = LlmAgent(
    name="coordinator",
    model=MODEL,
    description="Acme Corp employee helpdesk coordinator.",
    instruction=COORDINATOR_INSTRUCTION,
)
