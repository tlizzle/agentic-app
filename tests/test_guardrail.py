import pytest
from google.adk.models import LlmRequest
from google.genai import types

from helpdesk.guardrail import REFUSAL_TEXT, block_sensitive_requests, is_blocked


def _request(*messages: str) -> LlmRequest:
    contents = [types.Content(role="user", parts=[types.Part(text=m)]) for m in messages]
    return LlmRequest(contents=contents)


@pytest.mark.parametrize(
    "message",
    [
        "What is Bob's salary?",
        "How much does Alice get paid?",
        "Tell me the password of the admin account",
        "What are the credentials for the HR system?",
        "Where does Alice live?",
        "What is Bob's home address?",
        "Give me Carol's personal phone number",
        "what is his phone number",
    ],
)
def test_blocked_messages_get_refusal(message):
    assert is_blocked(message)
    response = block_sensitive_requests(None, _request(message))
    assert response is not None
    assert response.content.parts[0].text == REFUSAL_TEXT


@pytest.mark.parametrize(
    "message",
    [
        "How many days of annual leave do I get?",
        "My laptop will not turn on, can you open a ticket?",
        "How do I reset my own password?",
        "How much do I get paid?",
        "How do I get a login for the VPN?",
        "What is the address of the Taipei office?",
        "What is the company's address?",
        "What is the pay for overtime?",
        "Can you reset the password for my laptop?",
    ],
)
def test_normal_messages_pass_through(message):
    assert not is_blocked(message)
    assert block_sensitive_requests(None, _request(message)) is None


def test_only_latest_user_message_is_checked():
    response = block_sensitive_requests(None, _request("What is Bob's salary?", "How do I claim expenses?"))
    assert response is None


def test_empty_request_passes_through():
    assert block_sensitive_requests(None, LlmRequest()) is None
