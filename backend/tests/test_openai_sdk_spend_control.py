"""Regression tests for the OpenAI SDK upgrade.

The app's only OpenAI call site is a chat completion. Upgrading the SDK must
keep that request shape intact, and the app must never send Managed Agents
``spend_control`` even though upstream re-added the property in openai 3.58.0.
"""

import types
from unittest.mock import patch

import pytest

from app.services.ai_reviewer import AIReviewer


class _FakeMessage:
    content = '{"summary": "Looks good.", "findings": []}'


class _FakeChoice:
    message = _FakeMessage()


class _FakeResponse:
    choices = [_FakeChoice()]


class _FakeCompletions:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        return _FakeResponse()


class _FakeAsyncOpenAI:
    last_instance = None

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.chat = types.SimpleNamespace(completions=_FakeCompletions())
        _FakeAsyncOpenAI.last_instance = self


@pytest.mark.asyncio
async def test_openai_review_request_never_sends_spend_control():
    with patch("openai.AsyncOpenAI", _FakeAsyncOpenAI):
        reviewer = AIReviewer()
        result = await reviewer._call_openai("diff --git a/x.py b/x.py")

    instance = _FakeAsyncOpenAI.last_instance
    assert instance is not None
    assert len(instance.chat.completions.calls) == 1

    call = instance.chat.completions.calls[0]
    assert call["model"]
    assert call["temperature"] == 0.1
    assert call["response_format"] == {"type": "json_object"}
    assert [m["role"] for m in call["messages"]] == ["system", "user"]
    assert "spend_control" not in call
    assert result == {"summary": "Looks good.", "findings": []}


def test_openai_sdk_session_spend_control_matches_supported_sdk():
    try:
        from openai.types.beta.agents.session_create_params import (
            SessionCreateParamsBase,
        )
    except ModuleNotFoundError:
        pytest.fail(
            "OpenAI SDK is too old: managed-agent session params are unavailable, "
            "so the spend_control contract cannot be verified"
        )

    # openai 3.58.0 re-introduced session spending limits. The app-level test
    # above still guarantees the reviewer never opts into them.
    assert "spend_control" in SessionCreateParamsBase.__annotations__
