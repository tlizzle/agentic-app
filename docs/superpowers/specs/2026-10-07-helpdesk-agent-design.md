# Helpdesk Agent Demo: Design

Date: 2026-10-07. Status: draft for review.

## Goal

A small Google ADK app that shows an interviewer, through the `adk web` UI only:

1. RAG over local handbook files
2. Taking action through an MCP server, with human approval before the write
3. Multi-agent routing, a guardrail callback, sessions plus cross-session memory, and an evaluation set

Must stay lightweight: one agent package, one MCP server file, no cloud project, no database server. Runs with `uv sync` and `uv run adk web`. The user pushes to GitHub themselves.

## Scenario

An employee helpdesk assistant for a fictional company. Employees ask about HR and IT policy, and open or check support tickets.

## Stack

- Python 3.12, uv, `google-adk[mcp,eval]==2.11.0`
- Gemini via a Google AI Studio API key in `.env` (`GOOGLE_API_KEY`). Free tier.
- Chat model `gemini-2.5-flash`, embeddings `gemini-embedding-001` through `google-genai` (already an ADK dependency)
- MCP server built on the `mcp` 2.x SDK that ADK already pulls in (`MCPServer`)

## Layout

```
agentic-app/
  helpdesk/                     # the ADK app, discovered by `adk web`
    __init__.py
    agent.py                    # root coordinator + two sub-agents + guardrail
    rag.py                      # chunk, embed, cosine search, search_handbook tool
    guardrail.py                # before_model_callback
    prompts.py
    knowledge/                  # 3 to 4 short markdown handbook files
    helpdesk.evalset.json       # eval cases for the Eval tab
  mcp_server/
    tickets.py                  # MCPServer over stdio; JSON file store
  pyproject.toml
  .env.example
  README.md                     # setup + 5-step demo script
```

## Components

**Coordinator (`root_agent`).** LlmAgent that routes to two sub-agents and owns the `load_memory` tool and the guardrail callback. The agent graph in the UI shows the three nodes.

**Knowledge agent.** Sub-agent with one function tool, `search_handbook(query)`. Instruction: answer only from retrieved chunks, cite the file name, say when nothing is found.

**Ticket agent.** Sub-agent with an `McpToolset` over stdio to `mcp_server/tickets.py`. Tools: `create_ticket`, `get_ticket`, `list_tickets`. `require_confirmation` is set on `create_ticket` only, so ADK web shows the approval dialog before the ticket is written.

**RAG (`rag.py`).** On import: read `knowledge/*.md`, split by heading into chunks, embed them, cache vectors to `.cache/embeddings.json` keyed by content hash so restarts are instant and free. On query: embed, cosine, return top 3 with file name and snippet. Plain Python plus `numpy` is not required; a list comprehension on small vectors is enough.

**MCP server (`tickets.py`).** `MCPServer` with three tools, state in `mcp_server/tickets.json`. Runs as a subprocess spawned by ADK through `StdioConnectionParams`, so no separate terminal.

**Guardrail (`guardrail.py`).** `before_model_callback` on the coordinator. If the latest user message matches a short blocklist (for example asking for another employee's salary or password), return a fixed refusal `LlmResponse` and skip the model. Visible in the trace as a turn with no model call.

**Sessions and memory.** Sessions are ADK web's default SQLite store, shown in the Sessions panel. Memory uses ADK's in-process memory service: an `after_agent_callback` adds the finished session to memory, and the coordinator's `load_memory` tool recalls it in a new session. No cost, resets on restart.

**Evaluation.** `helpdesk.evalset.json` with three cases: a policy question (expects the search tool call and a grounded answer), a ticket creation (expects the create tool call), and a blocked request. Run from the Eval tab or `adk eval`.

## Demo script (README)

1. Ask "How many days of annual leave do I get?" and show the citation and the trace with the search tool call.
2. Say "My laptop screen flickers, open a ticket." Approve the dialog, then show the ticket id.
3. Ask "What is the status of that ticket?" to show a read action.
4. Say "I sit in the Taipei office." Open a new session, ask "Which office am I in?" to show memory.
5. Ask for a colleague's salary to show the guardrail, then run the eval set.

## Error handling

- Missing `GOOGLE_API_KEY`: fail at startup with a clear message.
- MCP server not reachable: ADK surfaces the tool error; the ticket agent is told to report it plainly.
- Empty retrieval: the knowledge agent says it could not find the answer rather than guessing.

## Testing

- Unit tests with pytest for `rag.py` (chunking, cache hit, top-k order with a fake embedder), the guardrail, and the ticket store functions. Tests do not call Gemini.
- Manual check in `adk web` of the five demo steps, including that the confirmation dialog appears with the default SQLite session store. If it does not, document the `--no_use_local_storage` fallback in the README.

## Out of scope

Deployment, auth, a custom frontend, mem0, voice, ADK 2.0 graph workflows.
