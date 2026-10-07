# 06: Eval Cases, demo script and why-MCP notes

**What to build:** The interviewer opens the Eval tab or runs one CLI command and sees three Eval Cases pass: a policy question (search tool called, cited answer), a Ticket creation (create tool called), and a blocked request (refusal). The README has the five-step demo script and the short why-MCP talking points.

**Blocked by:** 02, 03, 04, 05

**Status:** done

- [ ] Evalset file with three Eval Cases runnable from the Eval tab
- [ ] `adk eval` command documented and passing locally
- [ ] README demo script: citation, Approval, status, memory recall, Guardrail, eval
- [ ] README why-MCP section

## Comments

- 2026-10-07: The eval runner cannot replay the Approval reply (its function-call id does not exist in a fresh run), so the third Eval Case is a deterministic Ticket lookup over MCP instead of a Ticket creation. Approval stays a live demo step. All three cases pass with tool_trajectory_avg_score (IN_ORDER, names only) and response_match_score >= 0.3.
