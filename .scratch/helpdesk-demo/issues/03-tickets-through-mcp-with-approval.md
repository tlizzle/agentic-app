# 03: Open and read Tickets through MCP with Approval

**What to build:** The Employee describes a problem and asks to open a Ticket. The Coordinator hands off to the Ticket Agent, which calls the create tool on the in-repo MCP ticket service. The ADK web UI shows an Approval dialog first; on yes the Ticket is created and its id is reported, on no nothing is written. The Employee can then ask for the Ticket's status or list their Tickets without any Approval. The JSON file shows the created Ticket.

**Blocked by:** 01 Chat skeleton

**Status:** done

- [ ] MCP server with create_ticket, get_ticket, list_tickets backed by one JSON file, launched by ADK over stdio
- [ ] Ticket fields: id, title, category, status, requester, created time
- [ ] Approval required on create_ticket only
- [ ] Ticket Agent reports the id after creation, reports cancellation plainly when Approval is declined, and hands back
- [ ] One-line reset command documented
- [ ] Pytest: create, get, list and unknown id against a temporary JSON file
