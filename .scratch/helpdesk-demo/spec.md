# Helpdesk Demo

Status: ready-for-agent

## Problem Statement

An interviewer wants to see, in a few minutes and without reading code, that the author can build a working agent on Google ADK: one that answers from documents with Citations, takes a real action through MCP with human Approval, keeps Memory across Sessions, protects itself with a Guardrail, and can be evaluated. Existing samples are large production repos tied to cloud services, so they cannot be cloned and run on a laptop in a minute.

## Solution

A small Employee helpdesk assistant that runs with two commands from a fresh clone and a free AI Studio key. The Employee chats with a Coordinator in the ADK web UI. Policy questions go to a Knowledge Agent that answers only from Handbook Passages and cites them. Support requests go to a Ticket Agent that opens and reads Tickets through an in-repo MCP ticket service, pausing for Approval before any Ticket is created. The Coordinator blocks sensitive requests before any model call, and remembers facts about the Employee in later Sessions. Three Eval Cases show the behaviour holds.

## User Stories

1. As an Employee, I want to ask a policy question in plain language, so that I get the answer without reading the Handbook.
2. As an Employee, I want every policy answer to carry a Citation, so that I can trust and verify it.
3. As an Employee, I want to be told when the Handbook does not cover my question, so that I am not misled by a guess.
4. As an Employee, I want to open a Ticket by describing my problem, so that I do not fill in a form.
5. As an Employee, I want to approve the Ticket before it is created, so that nothing is filed without my consent.
6. As an Employee, I want to cancel at the Approval step, so that a wrong Ticket is never created.
7. As an Employee, I want to ask for the status of a Ticket by id or by "my ticket", so that I can follow up.
8. As an Employee, I want to list my Tickets, so that I can see what is open.
9. As an Employee, I want the assistant to remember facts I told it in an earlier Session, so that I do not repeat myself.
10. As an Employee, I want requests for other people's private data refused immediately, so that the assistant cannot be misused.
11. As an interviewer, I want to see the Handoff from the Coordinator to a specialist in the trace and agent graph, so that I understand the multi-agent design.
12. As an interviewer, I want to see the Approval dialog appear in the UI, so that I understand the human-in-the-loop control.
13. As an interviewer, I want to open the JSON ticket file after the demo, so that I can see the action really happened.
14. As an interviewer, I want to run the Eval Cases from the Eval tab or one CLI command, so that I see how the agent is tested.
15. As the author, I want setup to be two commands plus one key, so that the demo never fails on environment.
16. As the author, I want a five-step demo script in the README, so that the live demo is rehearsed and predictable.
17. As the author, I want a one-line reset for Tickets, so that each demo starts clean.

## Implementation Decisions

- Runtime is Google ADK 2.11 on Python 3.12 with uv. The app is one ADK package discovered by `adk web`; there is no custom server or frontend.
- Model access is a Gemini API key from Google AI Studio read from a dotenv file. The chat model is a Gemini Flash model; the embedding model is Gemini's free embedding model.
- Agent tree: a Coordinator with two sub-agents, Knowledge Agent and Ticket Agent, using ADK's native Handoff. Specialists are instructed to hand back to the Coordinator when their task is done. The Coordinator owns the Guardrail, the memory recall tool and the Handoff decision.
- Retrieval: Handbook markdown files are split into Passages at headings. Passages are embedded once and the vectors cached on disk keyed by content hash, so restarts are instant and free. A query is embedded and the top three Passages by cosine similarity are returned with Citations. If embedding calls ever cost money, the ranking swaps to BM25 behind the same interface (see ADR 0001).
- Ticket service: an MCP server in the repo, built on the MCP Python SDK that ADK already depends on, spawned by ADK over stdio. It exposes create_ticket, get_ticket and list_tickets. A Ticket has id, title, category, status, requester and created time. Storage is one JSON file next to the server; deleting it resets the demo (see ADR 0003).
- Approval: ADK's tool confirmation is enabled on create_ticket only, so the web UI shows a dialog before the write. Reads need no Approval.
- Guardrail: a before-model callback on the Coordinator matches the latest Employee message against a short rule list (another person's salary, password, home address). On a match it returns a fixed refusal and the model is never called.
- Memory: a plugin writes the Session to ADK's in-process memory service once at the end of each run, after all Handoffs complete. The Coordinator has a load_memory tool scoped to the Employee (see ADR 0002).
- Sessions use ADK web's default local storage; nothing custom.
- Evaluation: one evalset file with three Eval Cases: a policy question expecting the search tool and a cited answer, a Ticket lookup over MCP expecting the get tool (creation needs an Approval reply the eval runner cannot replay), and a blocked request expecting the refusal. Runnable from the Eval tab and from the `adk eval` command.
- Handbook content: three or four short English documents for a fictional company covering leave, IT equipment, expenses and remote work.
- Configuration failures are loud: a missing API key stops startup with a clear message.

## Testing Decisions

- Tests check external behaviour through module boundaries, never implementation details, and never call Gemini. Pytest only.
- Three seams, matching the three modules that hold logic:
  - Retrieval: given Handbook files and a fake embedder, search returns Passages ranked with Citations, and a second run reuses the cache without embedding again.
  - Ticket service: create, get and list work against a temporary JSON file, and get on an unknown id reports not found.
  - Guardrail: a blocked message yields the refusal, a normal message passes through.
- No tests for agent wiring, prompts or the MCP transport. Behaviour with the real model is covered by the Eval Cases, run manually.
- Prior art: the author's earlier ADK repos test tools and memory adapters at the function level with pytest; this follows the same style with less of it.

## Out of Scope

Deployment, authentication, a custom UI, mem0 or any external memory store, voice or live streaming, ADK 2.0 graph workflows, hybrid retrieval, LLM-based guardrails, CI pipelines, and more than three MCP tools.

## Further Notes

- Risk to verify early: ADK docs say tool confirmation is unsupported with database session services, while ADK web now defaults to local SQLite sessions. If the Approval dialog does not appear, the README documents the in-memory session flag as the fallback.
- The user pushes to GitHub themselves; nothing here pushes.
- Demo script for the README: policy question with Citation, open a Ticket with Approval, check its status, tell the assistant your office then recall it in a new Session, trigger the Guardrail, run the Eval Cases.
- README includes a short "why MCP" section for the interviewer: the agent is decoupled from the ticket system, the server is a standard any client can use, writes are gated by Approval while reads stay free, and the ticket logic is testable without a model.

## Comments

- 2026-10-07 code review (standards + spec axes): fixed Guardrail false positives on first-person and company questions; renamed the handbook folder to match the glossary; simplified path handling and the MCP server import; reused the embedding client; removed the placeholder test; default model switched to gemini-3.5-flash-lite because the free tier allowed 20 requests/day on gemini-3.5-flash. Left as-is: the missing-key error is a one-line RuntimeError inside a Python traceback rather than a bare line; Knowledge Agent hand-back is instructed but ADK routes the next message to the Coordinator anyway because the specialist has no sub-agents; the "requester" Ticket field stays as the ticket specified it.
