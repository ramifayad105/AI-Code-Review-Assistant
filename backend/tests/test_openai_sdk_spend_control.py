"""Regression tests for the OpenAI SDK upgrade.

The app's only OpenAI call site is a chat completion. Upgrading the SDK must
keep that request shape intact, and the removed Managed Agents
``spend_control`` request property must no longer be part of the installed
SDK's session-create parameters.
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


def test_openai_sdk_no_longer_exposes_session_spend_control():
    try:
        from openai.types.beta.agents.session_create_params import (
            SessionCreateParamsBase,
        )
    except ModuleNotFoundError:
        pytest.fail(
            "OpenAI SDK is too old: managed-agent session params are unavailable, "
            "so the removed spend_control property cannot be verified"
        )

    assert "spend_control" not in SessionCreateParamsBase.__annotations__
