# Acme Helpdesk Agent (Google ADK demo)

A small employee helpdesk assistant built on [Google ADK](https://adk.dev) 2.x. It is designed to be shown
entirely through the `adk web` developer UI and to run from a fresh clone with one free API key.

What it shows:

| Capability | How it appears in the demo |
|---|---|
| **RAG** | Policy answers come from handbook files, with a `Source:` citation. Trace shows the `search_handbook` call. |
| **Actions over MCP** | Tickets are created and read through an in-repo MCP server that ADK launches over stdio. |
| **Human approval** | The UI pops a confirmation dialog before `create_ticket` runs. Decline and nothing is written. |
| **Multi-agent** | A coordinator hands off to a knowledge agent or a ticket agent. Visible in the agent graph and trace. |
| **Guardrail** | Requests for another person's salary, password or address are refused before any model call. |
| **Sessions + memory** | Sessions persist in the UI. A fact told in one session is recalled in a new one via `load_memory`. |
| **Evaluation** | Three eval cases run from the Eval tab or `adk eval`, checking tool trajectory and response. |

## Prerequisites

- Python 3.12 and [uv](https://docs.astral.sh/uv/) (`brew install uv` on macOS)
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey). No credit card needed.

## Run

```bash
uv sync
cp .env.example helpdesk/.env   # paste your key into GOOGLE_API_KEY
uv run adk web
```

Open http://localhost:8000 and pick **helpdesk**.

## Demo script (about 5 minutes)

1. **RAG with citation.** Ask: `How many days of annual leave do I get?`
   The coordinator hands off to the knowledge agent, which searches the handbook and answers with
   `Source: leave.md › Annual leave`. Open the Trace tab to show the handoff and the tool call.
2. **Action with approval.** Say: `My laptop screen keeps flickering, please open a ticket for me.`
   An approval dialog appears. Approve it and the agent reports `T-0001`. Open `mcp_server/tickets.json` to prove the write.
   Try again with another problem and decline: the agent confirms nothing was created.
3. **Read action, no approval.** Ask: `What is the status of that ticket?`
4. **Memory across sessions.** Say: `By the way, I sit in the Taipei office, desk 4B.`
   Create a new session (left panel) and ask: `Which office am I in?` The coordinator calls `load_memory` and answers.
5. **Guardrail.** Ask: `What is Bob's salary?` The refusal arrives with no model call in the trace.
6. **Eval.** Open the Eval tab, select `helpdesk_demo`, run all. Or from the terminal:
   ```bash
   uv run adk eval helpdesk helpdesk/helpdesk_demo.evalset.json --config_file_path helpdesk/test_config.json
   ```

Reset between demos: `rm mcp_server/tickets.json`. Memory resets when the server restarts.

## Why an MCP ticket server?

The ticket server is a stand-in for Jira or ServiceNow, deliberately tiny but a real MCP server.

- **Decoupling.** The agent only sees tool names and schemas. Swap the toy server for the real system and the agent code does not change.
- **A standard, not glue code.** MCP is the open protocol supported across Anthropic, Google and OpenAI tooling. Any MCP client can use the same server.
- **A safe place for control.** Validation and permissions live in the server, outside the prompt. Approval is attached to the write tool only, so reads stay frictionless.
- **Testable without a model.** The ticket logic has its own unit tests, which is how an agent system stays reliable as it grows.

## Layout

```
helpdesk/                 the ADK app that adk web discovers
  agent.py                coordinator, sub-agents, guardrail, memory plugin (exports root_agent and app)
  rag.py                  passage splitting, Gemini embeddings with on-disk cache, cosine search, search_handbook tool
  guardrail.py            before_model_callback with a short rule list
  memory.py               plugin that writes each session to ADK's memory service after the run
  sub_agents/             knowledge_agent (RAG) and ticket_agent (MCP toolset with approval on create)
  knowledge/              four short handbook documents
  helpdesk_demo.evalset.json, test_config.json   eval cases and thresholds
mcp_server/
  tickets.py              MCP server over stdio: create_ticket, get_ticket, list_tickets
  store.py                JSON-file ticket store (unit tested)
tests/                    pytest, never calls Gemini
docs/adr/                 why local-file RAG, why ADK memory over mem0, why an in-repo MCP server
CONTEXT.md                glossary of project terms
```

## Models and free-tier quotas

The model is set by `HELPDESK_MODEL` in `helpdesk/.env` (default `gemini-3.5-flash`). Free-tier quotas are
**per model per day** and can be small: at the time of writing `gemini-3.5-flash` allowed 20 requests per day,
and one demo turn uses 2 to 4 requests. If you hit `429 RESOURCE_EXHAUSTED`, switch to another model such as
`gemini-3.5-flash-lite` and restart. Check your limits at https://aistudio.google.com/rate-limit. Transient
`503` responses are retried automatically. Embeddings are cached in `.cache/` so the handbook is embedded once.

## Develop

```bash
uv run pytest
uv run ruff check .
```
