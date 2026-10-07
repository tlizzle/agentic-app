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

# Private facts about a person. Deliberately no bare "address", "login" or "phone": office addresses and
# VPN logins are legitimate Handbook questions.
_PRIVATE = (
    r"(?:salary|pay|wages?|compensation|password|passcode|credentials"
    r"|home\s+address|(?:personal\s+)?(?:phone|mobile|cell)\s+number)"
)
# Possessives that refer to the Employee themselves or to the company, never to another person.
_NOT_A_PERSON = r"(?!my\b|our\b|the\b|company\b|acme\b|office\b|team\b|it\b)"

RULES = [
    re.compile(p, re.IGNORECASE)
    for p in (
        # "Bob's salary", "Alice's home address" (but not "my salary", "the company's address")
        rf"\b{_NOT_A_PERSON}\w+'s\s+{_PRIVATE}\b",
        # "his pay", "her password", "their home address"
        rf"\b(?:his|her|their)\s+{_PRIVATE}\b",
        # "salary of Bob", "credentials for the HR system" (but not "password for my laptop", "pay for overtime")
        r"\b(?:salary|wages?|compensation|password|passcode|credentials)\s+(?:of|for)\s+(?!my\b|mine\b|me\b|overtime\b)",
        # "how much does Alice get paid / earn / make" (but not "how much do I get paid")
        r"\bhow\s+much\s+(?:does|do)\s+(?!i\b|we\b)\w+\s+(?:get\s+)?(?:paid|earn|make)\b",
        # "where does Alice live"
        r"\bwhere\s+(?:does|do)\s+(?!i\b|we\b)\w+\s+live\b",
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
