"""Acme ticket service: an MCP server over stdio, backed by one JSON file.

Run with `python mcp_server/tickets.py`. Set TICKETS_PATH to use a different file.
Reset the store with `rm mcp_server/tickets.json`.
"""

import os
from pathlib import Path

import store  # the script directory is always first on sys.path
from mcp.server.mcpserver import MCPServer

HERE = Path(__file__).resolve().parent

TICKETS_PATH = Path(os.environ.get("TICKETS_PATH", HERE / "tickets.json"))

mcp = MCPServer("acme-tickets")


@mcp.tool()
def create_ticket(title: str, category: str, requester: str) -> dict:
    """Open a new helpdesk ticket and return it, including its new id.

    Args:
        title: Short one-line summary of the problem.
        category: One of "hardware", "software", "access", "other".
        requester: Name of the employee opening the ticket.
    """
    return store.create_ticket(TICKETS_PATH, title, category, requester)


@mcp.tool()
def get_ticket(ticket_id: str) -> dict | None:
    """Look up one ticket by id (for example "T-0001"). Returns null if no such ticket exists."""
    return store.get_ticket(TICKETS_PATH, ticket_id)


@mcp.tool()
def list_tickets(requester: str = "") -> list[dict]:
    """List tickets, newest last. Pass a requester name to see only that employee's tickets; empty lists all."""
    return store.list_tickets(TICKETS_PATH, requester or None)


if __name__ == "__main__":
    mcp.run(transport="stdio")
