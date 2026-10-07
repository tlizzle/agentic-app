from google.adk.agents import LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService

from helpdesk.memory import MemoryWritePlugin


async def test_after_run_writes_session_to_memory():
    memory = InMemoryMemoryService()
    session = await InMemorySessionService().create_session(app_name="helpdesk", user_id="u1")
    ctx = InvocationContext(
        invocation_id="inv1",
        agent=LlmAgent(name="a", model="gemini-2.5-flash"),
        session=session,
        session_service=InMemorySessionService(),
        memory_service=memory,
    )
    await MemoryWritePlugin().after_run_callback(invocation_context=ctx)
    assert ("helpdesk", "u1") in memory._session_events
