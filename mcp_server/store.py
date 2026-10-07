"""Tiny JSON-file Ticket store. The whole store is one list of Ticket dicts."""

import json
from datetime import UTC, datetime
from pathlib import Path


def _load(path: Path) -> list[dict]:
    path = Path(path)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save(path: Path, tickets: list[dict]) -> None:
    Path(path).write_text(json.dumps(tickets, indent=2) + "\n")


def create_ticket(path: Path, title: str, category: str, requester: str) -> dict:
    tickets = _load(path)
    ticket = {
        "id": f"T-{len(tickets) + 1:04d}",
        "title": title,
        "category": category,
        "status": "open",
        "requester": requester,
        "created": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    tickets.append(ticket)
    _save(path, tickets)
    return ticket


def get_ticket(path: Path, ticket_id: str) -> dict | None:
    return next((t for t in _load(path) if t["id"] == ticket_id), None)


def list_tickets(path: Path, requester: str | None = None) -> list[dict]:
    tickets = _load(path)
    if requester:
        tickets = [t for t in tickets if t["requester"] == requester]
    return tickets
