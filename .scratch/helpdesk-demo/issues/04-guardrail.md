# 04: Guardrail blocks sensitive requests

**What to build:** When the Employee asks for another person's salary, password or home address, the Coordinator refuses immediately with a fixed message and no model call is made. The trace shows the turn with no model request. Normal questions are unaffected.

**Blocked by:** 01 Chat skeleton

**Status:** done

- [ ] Before-model callback on the Coordinator with a short rule list
- [ ] Fixed refusal text that also says what the assistant can help with
- [ ] Pytest: a blocked message yields the refusal, a normal message passes through
