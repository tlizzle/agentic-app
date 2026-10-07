# 05: Memory across Sessions

**What to build:** The Employee tells the assistant a fact, such as which office they sit in. In a new Session they ask about it and the Coordinator recalls it through Memory. Memory is written automatically at the end of each run, after any Handoff has finished, following the plugin pattern from the author's earlier ADK projects (ADR 0002).

**Blocked by:** 01 Chat skeleton

**Status:** done

- [ ] Plugin writes the Session to ADK's in-process memory service once per run
- [ ] Coordinator has a load_memory tool and is instructed to use it for questions about the Employee
- [ ] Demo: fact given in Session A is recalled in Session B
