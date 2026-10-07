"""Ticket Agent: opens and looks up Tickets through the in-repo MCP ticket service (stdio)."""

import sys
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

from ..config import MODEL

TICKET_SERVER = Path(__file__).resolve().parents[2] / "mcp_server" / "tickets.py"

TICKET_INSTRUCTION = """You are the Acme Corp helpdesk ticket agent. You open and look up support tickets.

Opening a ticket:
- From the employee's description, write a short one-line title and pick a category:
  hardware, software, access, or other. Ask only if you really cannot tell.
- Use the requester "employee" unless the employee has told you their name.
- Call create_ticket. The employee is asked to approve it first.
- If it was created, report the ticket id (for example "Opened ticket T-0003 for you").
- If the employee declined the approval, say plainly that no ticket was created. Do not retry.

Status and lists:
- Answer "what is the status of T-0001" with get_ticket and "show my tickets" with list_tickets directly.
- If a ticket id does not exist, say so.

After every completed action (ticket created, approval declined, or status answered), transfer back to the
coordinator in the same turn so it handles whatever the employee says next.
"""


def _needs_approval(**args) -> bool:
    """Approval only for create_ticket: it is the one tool that takes a title."""
    return "title" in args


ticket_agent = LlmAgent(
    name="ticket_agent",
    model=MODEL,
    description="Opens support tickets (with employee approval) and reports ticket status or lists.",
    instruction=TICKET_INSTRUCTION,
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(command=sys.executable, args=[str(TICKET_SERVER)]),
                timeout=15,
            ),
            tool_filter=["create_ticket", "get_ticket", "list_tickets"],
            require_confirmation=_needs_approval,
        )
    ],
)
