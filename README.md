# Employee Helpdesk Agent (Google ADK demo)

A small employee helpdesk assistant built on [Google ADK](https://adk.dev) 2.x. It is designed to be shown
entirely through the `adk web` developer UI and to run from a fresh clone with one free API key.

What it shows:

| Capability | How it appears in the demo |
|---|---|
| **RAG** | Policy answers come from handbook files, with a `Source:` citation. Trace shows the `search_handbook` call. |
| **Actions over MCP** | Tickets are created and read through an in-repo MCP server that ADK launches over stdio. |
| **Human approval** | The UI pops an approval dialog before `create_ticket` runs. Decline and nothing is written. |
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
uv run adk web                  # open http://localhost:8000 and pick helpdesk

uv run pytest                   # unit tests, never call Gemini
uv run ruff check .
uv run adk eval helpdesk helpdesk/helpdesk_demo.evalset.json --config_file_path helpdesk/test_config.json
```

Presenter walkthrough (Traditional Chinese, step by step with talking points): [DEMO.md](DEMO.md).

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
  handbook/               four short handbook documents
  helpdesk_demo.evalset.json, test_config.json   eval cases and thresholds
mcp_server/
  tickets.py              MCP server over stdio: create_ticket, get_ticket, list_tickets
  store.py                JSON-file ticket store (unit tested)
tests/                    pytest, never calls Gemini
docs/adr/                 why local-file RAG, why ADK memory over mem0, why an in-repo MCP server
CONTEXT.md                glossary of project terms
```

## Models and free-tier quotas

The model is set by `HELPDESK_MODEL` in `helpdesk/.env` (default `gemini-3.5-flash-lite`, which had the most free-tier headroom when this was built). Free-tier quotas are
**per model per day** and can be small: at the time of writing `gemini-3.5-flash` allowed 20 requests per day,
and one demo turn uses 2 to 4 requests. If you hit `429 RESOURCE_EXHAUSTED`, switch to another model such as
`gemini-3.5-flash` or `gemini-flash-latest` and restart. Check your limits at https://aistudio.google.com/rate-limit. Transient
`503` responses are retried automatically. Embeddings are cached in `.cache/` so the handbook is embedded once.

## How this was built

With Claude Code and the [matt-pocock-skills](https://github.com/mattpocock/skills) flow. Each step's output is the next step's input, and all of it is in the repo.

| Step | Skill | What happens | Input → Output |
|---|---|---|---|
| 1 | `grill-with-docs` | Claude asks one design question at a time until nothing is ambiguous, then records terms and decisions | idea → `CONTEXT.md`, `docs/adr/` |
| 2 | `to-spec` | Writes one spec: scope, non-goals, acceptance criteria | decisions → `.scratch/helpdesk-demo/spec.md` |
| 3 | `to-tickets` | Slices the spec into small tickets that each ship on their own | spec → `.scratch/helpdesk-demo/issues/` |
| 4 | `implement` | One ticket at a time: test first, code, `uv run pytest`, commit | ticket → `helpdesk/`, `mcp_server/`, `tests/` |
| 5 | `code-review` | Reviews the diff against coding standards and against the spec, fixes applied, then live checks in `adk web` | code → fix commits (see git log) |

`CLAUDE.md` holds the rules Claude reads in this repo.
