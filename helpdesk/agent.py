from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.tools import load_memory

from .config import MODEL, require_api_key
from .guardrail import block_sensitive_requests
from .memory import MemoryWritePlugin
from .prompts import COORDINATOR_INSTRUCTION
from .sub_agents.knowledge import knowledge_agent
from .sub_agents.ticket import ticket_agent

require_api_key()

root_agent = LlmAgent(
    name="coordinator",
    model=MODEL,
    description="Employee helpdesk coordinator.",
    instruction=COORDINATOR_INSTRUCTION,
    sub_agents=[knowledge_agent, ticket_agent],
    tools=[load_memory],
    before_model_callback=block_sensitive_requests,
)

# adk web prefers an App when one is exported; the plugin writes each session to memory after every run.
app = App(name="helpdesk", root_agent=root_agent, plugins=[MemoryWritePlugin()])
