"""Regression test for the OpenAI vendor API update.

The upstream spec update removes the Assistants, Conversations, Evals and audio
translation endpoints and replaces several fixed ``type`` enums with ``const``.
The app only uses Chat Completions, so the review request must stay on the
supported ``/chat/completions`` surface while the SDK pin tracks the latest
vendor release.
"""

import importlib.metadata
import types
from unittest.mock import patch

import pytest

from app.services.ai_reviewer import AIReviewer

MIN_OPENAI_VERSION = (3, 59, 0)


def _version_tuple(version: str) -> tuple[int, ...]:
    parts = []
    for chunk in version.split(".")[:3]:
        digits = "".join(character for character in chunk if character.isdigit())
        parts.append(int(digits or 0))
    return tuple(parts)


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
async def test_openai_review_uses_supported_chat_completions_surface():
    installed = importlib.metadata.version("openai")
    assert _version_tuple(installed) >= MIN_OPENAI_VERSION, (
        f"openai {installed} predates the vendor API update; expected at least "
        f"{'.'.join(str(part) for part in MIN_OPENAI_VERSION)}"
    )

    with patch("openai.AsyncOpenAI", _FakeAsyncOpenAI):
        reviewer = AIReviewer()
        result = await reviewer._call_openai("diff --git a/x.py b/x.py")

    instance = _FakeAsyncOpenAI.last_instance
    assert instance is not None
    assert len(instance.chat.completions.calls) == 1

    call = instance.chat.completions.calls[0]
    assert call["response_format"] == {"type": "json_object"}
    assert call["temperature"] == 0.1
    assert [message["role"] for message in call["messages"]] == ["system", "user"]
    assert result == {"summary": "Looks good.", "findings": []}
