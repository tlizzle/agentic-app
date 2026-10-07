"""Guardrail: block requests for another Employee's private data before any model call."""

from __future__ import annotations

import re

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types

REFUSAL_TEXT = (
    "I can't help with requests for another person's private data such as their salary, "
    "passwords or credentials, home address or personal phone number. "
    "I can help with company policy questions (leave, IT equipment, expenses, remote work) "
    "and with opening or checking support tickets."
)

_PRIVATE = (
    r"(?:salary|pay|wages?|compensation|password|passcode|credentials|login"
    r"|(?:home\s+)?address|(?:personal\s+)?(?:phone|mobile|cell)(?:\s+number)?)"
)

RULES = [
    re.compile(p, re.IGNORECASE)
    for p in (
        # "Bob's salary", "the admin account's password", "Alice's home address"
        rf"\b\w+'s\s+{_PRIVATE}\b",
        # "his pay", "her password", "their home address"
        rf"\b(?:his|her|their)\s+{_PRIVATE}\b",
        # "password of the admin account", "salary for Bob" (but not "password for my laptop")
        rf"\b{_PRIVATE}\s+(?:of|for)\s+(?!my\b|mine\b|me\b)",
        # "how much does Alice get paid / earn / make"
        r"\bhow\s+much\s+(?:does|do|is)\s+\w+\s+(?:get\s+)?(?:paid|earn|make)\b",
        # "where does Alice live"
        r"\bwhere\s+(?:does|do)\s+\w+\s+live\b",
    )
]


def is_blocked(text: str) -> bool:
    return any(rule.search(text) for rule in RULES)


def _latest_user_text(llm_request: LlmRequest) -> str:
    for content in reversed(llm_request.contents):
        if content.role == "user":
            return " ".join(part.text for part in content.parts or [] if part.text)
    return ""


def block_sensitive_requests(callback_context: CallbackContext, llm_request: LlmRequest) -> LlmResponse | None:
    """before_model_callback for the Coordinator: return the refusal instead of calling the model."""
    if is_blocked(_latest_user_text(llm_request)):
        return LlmResponse(content=types.Content(role="model", parts=[types.Part(text=REFUSAL_TEXT)]))
    return None
