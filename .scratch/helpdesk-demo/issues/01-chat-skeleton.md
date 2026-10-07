# 01: Chat skeleton runs in ADK web

**What to build:** From a fresh clone, the Employee runs two commands, adds a free AI Studio key to a dotenv file, opens the ADK web UI, picks the helpdesk app and gets a reply from the Coordinator. A missing key stops startup with a clear message. The README has the setup steps.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] `uv sync` then `uv run adk web` serves the app with no other steps
- [ ] The Coordinator introduces itself as the company helpdesk and answers small talk
- [ ] Startup fails with a one-line message naming the missing key when the dotenv file lacks it
- [ ] README covers prerequisites, key creation, the two commands, and the project layout
- [ ] Ruff and pytest are configured and `uv run pytest` passes with zero tests collected or a trivial test
