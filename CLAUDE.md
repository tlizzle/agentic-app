# CLAUDE.md

Guidance for Claude Code in this repo. Keep it short and specific.

## Project Overview

A small Google ADK demo app for interviews: an employee helpdesk agent shown only through `adk web`. Keep it simple and lightweight; no over-design.

## Commands

```bash
uv sync                      # install dependencies
uv run adk web               # run the demo UI on http://localhost:8000
uv run pytest                # unit tests (never call Gemini)
uv run ruff check .          # lint, run before every commit
uv run adk eval helpdesk helpdesk/helpdesk_demo.evalset.json --config_file_path helpdesk/test_config.json
```

Restart `adk web` after code changes; `--reload` does not pick them up.

## Architecture

- `helpdesk/agent.py` wires a coordinator `LlmAgent` with two sub-agents (handoff via `transfer_to_agent`): the knowledge agent (RAG over `helpdesk/handbook/`, citation in every answer) and the ticket agent (MCP toolset, approval required on `create_ticket`).
- Guardrail is a `before_model_callback` on every agent; memory is a plugin that writes each session to ADK's memory service, read back with `load_memory`.
- `mcp_server/` is a stdio MCP server backed by one JSON file; `store.py` holds the logic so it is unit tested.
- Layout and capability table: see `README.md`. Terms: `CONTEXT.md`. Decisions: `docs/adr/`.

## Key Conventions

- Model names and the API key check live in `helpdesk/config.py`; the model is overridable with `HELPDESK_MODEL`. Never commit `helpdesk/.env`.
- Tests sit at module seams only (store, rag split and cosine, guardrail rules, memory plugin) and never call Gemini. Agent behaviour is covered by the eval set, not by end-to-end tests.
- Keep eval cases deterministic: verbatim search query, fixed not-found reply, one or two sentence answers.
- Style is ruff-enforced, line length 120.

## Git Conventions

- Commit messages: short, plain, imperative, one line, no type prefix. Commit when a ticket or a review fix is done.
- Work on `main`; this is a demo repo.

## Behavioral Guidelines

- Think first: state assumptions; if the request is ambiguous or a simpler approach exists, say so before coding.
- Simplicity: write the minimum that solves the task, no speculative features or abstractions.
- Surgical changes: touch only what the task requires and reuse what exists.
- Goal-driven: define a success check (a failing test or an eval case), verify it passes before reporting done.
- Decisions go through the user: propose, ask, then build.

## Agent skills

### Issue tracker

Local markdown under `.scratch/<feature>/` (spec.md plus one file per ticket in issues/). See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context: `CONTEXT.md` at the root and ADRs in `docs/adr/`. See `docs/agents/domain.md`.
