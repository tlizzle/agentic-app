# Acme Helpdesk Agent (Google ADK demo)

A small employee helpdesk assistant built on [Google ADK](https://adk.dev) that shows, through the `adk web` UI:

- **RAG**: answers policy questions from handbook files with citations
- **Actions over MCP**: opens and reads support tickets through an in-repo MCP server
- **Human approval**: the UI asks before any ticket is created
- **Multi-agent**: a coordinator hands off to a knowledge agent and a ticket agent
- **Guardrail**: sensitive requests are refused before any model call
- **Sessions and memory**: facts from one session are recalled in the next
- **Evaluation**: three eval cases runnable from the Eval tab or the CLI

## Prerequisites

- Python 3.12 and [uv](https://docs.astral.sh/uv/) (`brew install uv` on macOS)
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey). No credit card is needed.

## Run

```bash
uv sync
cp .env.example helpdesk/.env   # then paste your key into GOOGLE_API_KEY
uv run adk web
```

Open http://localhost:8000 and pick **helpdesk**.

## Layout

```
helpdesk/        the ADK app that adk web discovers (root_agent lives in agent.py)
mcp_server/      the MCP ticket server ADK launches over stdio
tests/           pytest, no model calls
```

## Develop

```bash
uv run pytest
uv run ruff check .
```
