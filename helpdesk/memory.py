from google.adk.agents.invocation_context import InvocationContext
from google.adk.plugins.base_plugin import BasePlugin


class MemoryWritePlugin(BasePlugin):
    """Writes the Session to Memory once per run.

    Uses after_run_callback because it fires exactly once per run, after the
    Coordinator and every Handoff have finished, so the whole turn is written
    in one shot. Pattern from the author's earlier ADK projects (ADR 0002).
    Skips silently when no memory service is configured.
    """

    def __init__(self) -> None:
        super().__init__(name="memory_write")

    async def after_run_callback(self, *, invocation_context: InvocationContext) -> None:
        memory_service = invocation_context.memory_service
        if memory_service is not None:
            await memory_service.add_session_to_memory(invocation_context.session)
