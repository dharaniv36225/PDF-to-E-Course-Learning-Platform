"""Tests for LLM provider configuration and error messaging."""
from __future__ import annotations

import pytest

from app.ai.llm import NOT_CONFIGURED_MESSAGE, LLMProvider
from app.core.errors import ServiceUnavailableError


def _unconfigured_provider() -> LLMProvider:
    provider = LLMProvider()
    provider._groq = None
    provider._openrouter = None
    return provider


def test_provider_reports_unavailable_without_keys():
    assert _unconfigured_provider().available is False


@pytest.mark.asyncio
async def test_complete_raises_friendly_message_when_not_configured():
    provider = _unconfigured_provider()
    with pytest.raises(ServiceUnavailableError) as exc_info:
        await provider.complete([{"role": "user", "content": "hi"}])
    assert exc_info.value.message == NOT_CONFIGURED_MESSAGE
    assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_stream_raises_friendly_message_when_not_configured():
    provider = _unconfigured_provider()
    with pytest.raises(ServiceUnavailableError) as exc_info:
        async for _ in provider.stream([{"role": "user", "content": "hi"}]):
            pass
    assert exc_info.value.message == NOT_CONFIGURED_MESSAGE
