# Demo walkthrough: Acme Helpdesk Agent

A step-by-step script for presenting this project in about 10 minutes, with what to type, what to expect,
what to point at in the ADK web UI, and the questions that usually come up.

## 1. The use case (30 seconds)

An **employee helpdesk assistant** for a fictional company, Acme Corp. It does two jobs:

1. **Policy questions** (HR and IT): leave, IT equipment, expenses, remote work. Answered only from the
   company handbook, with a citation, and an honest "not covered" when the handbook is silent.
2. **Support tickets** (IT helpdesk): open a ticket from a plain description, with the employee's approval
   before it is filed, then check status or list tickets.

Three cross-cutting behaviours: it remembers facts about the employee across sessions, it refuses requests
for other people's private data before the model ever sees them, and it has a regression eval set.

One-line version: *"An internal helpdesk agent that answers from company policy with citations, files IT
tickets through MCP with human approval, remembers the employee, and is guarded and tested."*

The domain is generic on purpose. Swapping the handbook files and ticket categories is a 15-minute change,
because the agent code never references the content.

## 2. Architecture (1 minute)

Open the agent graph: top bar, tree icon right after the `helpdesk` dropdown.

```
coordinator ─── handoff ──> knowledge_agent ── tool ──> search_handbook   (RAG over handbook/*.md)
     │      └── handoff ──> ticket_agent ───── tool ──> McpToolset        (create / get / list tickets)
     └───────── tool ─────> load_memory                                   (cross-session memory)
```

| Capability | Where it lives | What to say |
|---|---|---|
| RAG | `helpdesk/rag.py` | Handbook split at headings into passages, embedded once with Gemini, cached on disk, cosine search, top 3 with citations. |
| MCP action | `mcp_server/tickets.py` | A real MCP server in the repo, launched by ADK over stdio. Stand-in for Jira or ServiceNow. |
| Human approval | `helpdesk/sub_agents/ticket.py` | ADK tool confirmation on `create_ticket` only. Reads need no approval. |
| Multi-agent | `helpdesk/agent.py` | Coordinator hands off to two specialists using ADK's native transfer. |
| Guardrail | `helpdesk/guardrail.py` | Before-model callback on every agent. Rule match returns a fixed refusal, no model call. |
| Memory | `helpdesk/memory.py` | Plugin writes each session to ADK's memory service after the run; `load_memory` recalls it. |
| Eval | `helpdesk/helpdesk_demo.evalset.json` | Three recorded cases replayed against the live agent. |

Stack: Google ADK 2.11, Python 3.12, uv, one free AI Studio key. No cloud project, no database server.

## 3. Setup before the interview

```bash
uv sync
cp .env.example helpdesk/.env        # paste your GOOGLE_API_KEY
rm -f mcp_server/tickets.json        # clean ticket store
uv run adk web
```

Open http://localhost:8000, pick **helpdesk**, click **New Session**. Keep the **Events** toggle on so each
tool call is visible. Free-tier quotas are per model per day; if you see `429`, switch `HELPDESK_MODEL` in
`helpdesk/.env` (see README).

## 4. The six steps

### Step 1: RAG with citation

Type: `How many days of annual leave do I get?`

Expect: a one-sentence answer ("20 days") ending with `Source: leave.md › Annual leave`.

Point at: the events. `transfer_to_agent("knowledge_agent")`, then `search_handbook(...)`, then the
answer. Click the tool result to show the three passages and their similarity scores. The graph on the left
highlights the active path.

Say: "The agent can only answer from retrieved passages. Ask something the handbook does not cover and it
says so." Try: `Can I bring my dog to the office?`

### Step 2: Action with approval

Type: `My laptop screen keeps flickering, please open a ticket for me.`

Expect: an approval dialog showing the arguments (title, category, requester). Click approve. Reply:
"Opened ticket T-0001 for you: Laptop screen flickering (hardware). It is now open."

Point at: events `create_ticket` → `adk_request_confirmation` → your approval → `create_ticket` result.
Then open `mcp_server/tickets.json` in an editor to show the written record.

Say: "The pause is enforced by the framework, not the prompt. The model cannot talk its way past it."

### Step 3: Decline

Type: `Also open a ticket, I need access to the finance shared drive.` Click reject.

Expect: "No ticket was created." and no second dialog. The JSON file still has one ticket.

### Step 4: Read action, no approval

Type: `What is the status of ticket T-0001?`

Expect: "Ticket T-0001 ... is currently open." with a `get_ticket` call and no dialog.

Say: "Approval is attached to the write tool only, so reads stay frictionless."

### Step 5: Memory across sessions

Type: `By the way, I sit in the Taipei office, desk 4B.`

Click **New Session**. Type: `Which office am I in?`

Expect: "You are in the Taipei office at desk 4B." with a `load_memory("office")` call.

Say: "Sessions are separate conversations. Memory is written automatically after each run and searched by
the coordinator when the question is about the employee."

### Step 6: Guardrail

Type: `What is Bob's salary?`

Expect: the fixed refusal as the only event. Open **Traces**: no model request for this turn.

Then type: `What's my salary?` It is answered normally (the model says it has no salary data), because the
rule only targets *another person's* data.

Say: "A deliberately narrow rule list at the callback hook. In production you plug a policy classifier
into the same hook."

### Step 7: Eval

Left panel **Evals** → `helpdesk_demo` → **Run All** → keep defaults → **Run**. To see results, click the
home icon, reopen `helpdesk_demo`, then the clock icon (the 2.11 UI does not refresh the list by itself).

Expect: 3 PASS. Tool Trajectory 1.0 and Response Match 1.0 on each.

Say: "Each case is a recorded conversation. Running replays the user message against the live agent and
compares tool calls and the answer. It is regression testing for agents."

## 5. Questions that come up

**Is it a real LLM and embedder?**
Yes. Chat is a Gemini Flash model, embeddings are `gemini-embedding-001` (3072 dimensions). Only the
pytest tests use a fake embedder.

**How is the handbook chunked?**
Split at `#` and `##` headings, one passage per section, 23 passages across four files. Each passage is
embedded once and cached by content hash, so restarts cost nothing. Top 3 by cosine; below 0.66 the tool
reports "not found".

**What does the confirmation do, and how does it relate to `_needs_approval()`?**
`_needs_approval()` is the switch: ADK calls it with the tool arguments and it returns true only for
`create_ticket` (the one tool with a `title`). When true, ADK does not run the tool. It emits
`adk_request_confirmation`, the UI shows the dialog, your click sends back `confirmed: true/false`, and only
then does ADK run the real write or return "rejected" to the agent.

**Why build a ticket server at all?**
It stands in for Jira or ServiceNow and shows the real shape of production agents: an LLM, internal
systems behind MCP, and an approval gate on writes. Four points: the agent is decoupled from the system
(swap the server, agent code unchanged); MCP is an open standard any client can use; validation and
permissions live in the server, outside the prompt; the ticket logic is unit-tested without a model.

**Which memory bank is used?**
ADK's built-in in-process memory service, which `adk web` creates by default. Keyword search, scoped to the
user. It resets on restart. The service is an interface, so Vertex AI Memory Bank or mem0 is a one-object
swap (see `docs/adr/0002-adk-memory-service-over-mem0.md`).

**How does eval work?**
A case stores the user message, the tool calls with arguments, and the final answer. Running replays the
message in a fresh session. Tool Trajectory compares the call sequence (1.0 = identical). Response Match is
a ROUGE-1 word overlap with the recorded answer. The unchecked metrics use an LLM as judge.
Lexical matching is brittle by design: a correct but longer answer can fail, which is why the prompts keep
queries verbatim and answers tight.

**What would change for production?**
Managed retrieval (Vertex AI Search or a vector database) behind the same `search_handbook` interface,
a persistent memory service, a real ticket system behind the same MCP tool names, a policy classifier at
the guardrail hook, and the eval set in CI with `adk eval`.

## 6. Reset between demos

```bash
rm -f mcp_server/tickets.json   # tickets
# memory resets when you restart adk web; sessions can be deleted from the session dropdown
```
