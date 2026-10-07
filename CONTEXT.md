# Helpdesk Demo

An employee helpdesk assistant built to show an interviewer, through the ADK web UI, how an agent grounds answers in documents, takes real actions with human approval, and remembers across sessions.

## Language

**Handbook**:
The set of company policy documents the assistant is allowed to answer from.
_Avoid_: knowledge base, KB, FAQ, docs

**Passage**:
One heading-delimited section of a Handbook document, the unit that is retrieved and cited.
_Avoid_: chunk, snippet, document

**Citation**:
The Handbook document and heading a Passage came from, shown with every grounded answer as a `Source:` line.
_Avoid_: reference

**Ticket**:
A support request an Employee opens with the helpdesk, with a title, category, status and id.
_Avoid_: issue, case, request

**Approval**:
The Employee's explicit yes in the UI before the assistant performs a write such as opening a Ticket.
_Avoid_: confirmation, consent, HITL

**Employee**:
The person chatting with the assistant.
_Avoid_: user, customer, requester

**Coordinator**:
The front agent that talks to the Employee, enforces the Guardrail, recalls Memory, and hands off to a specialist.
_Avoid_: root, router, orchestrator

**Knowledge Agent**:
The specialist that answers policy questions only from Handbook Passages, with Citations.
_Avoid_: RAG agent, search agent

**Ticket Agent**:
The specialist that opens and looks up Tickets through the ticket service.
_Avoid_: action agent, MCP agent

**Guardrail**:
A rule that blocks a request before any model sees it, such as asking for another Employee's salary.
_Avoid_: filter, moderation, safety check

**Session**:
One conversation thread in the UI.
_Avoid_: chat, thread

**Memory**:
Facts carried across Sessions for the same Employee, such as which office they sit in.
_Avoid_: long-term memory, history, context

**Handoff**:
The Coordinator passing the turn to a specialist, which answers the Employee directly and passes the turn back when done.
_Avoid_: transfer, delegation, routing

**Eval Case**:
A saved conversation with the expected tool calls and answer, used to check the assistant still behaves.
_Avoid_: test case, golden, fixture
