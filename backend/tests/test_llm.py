from types import SimpleNamespace

import pytest

import app.ai.llm as llm_module
from app.ai.llm import LLMProvider, get_llm
from app.core.errors import ServiceUnavailableError


class _FakeCompletions:
    def __init__(self, *, content=None, error=None, stream_tokens=None):
        self.content = content
        self.error = error
        self.stream_tokens = stream_tokens
        self.calls: list[dict] = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        if kwargs.get("stream"):
            return self._make_stream(self.stream_tokens or [])
        message = SimpleNamespace(content=self.content)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])

    @staticmethod
    async def _make_stream(tokens):
        for token in tokens:
            delta = SimpleNamespace(content=token)
            yield SimpleNamespace(choices=[SimpleNamespace(delta=delta)])


def _client(**kwargs):
    completions = _FakeCompletions(**kwargs)
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    return client, completions


def _provider_without_clients() -> LLMProvider:
    provider = LLMProvider.__new__(LLMProvider)
    provider._groq = None
    provider._openrouter = None
    return provider


def test_available_reflects_configured_clients():
    provider = _provider_without_clients()
    assert provider.available is False
    provider._groq, _ = _client(content="x")
    assert provider.available is True


@pytest.mark.asyncio
async def test_complete_returns_groq_result():
    provider = _provider_without_clients()
    provider._groq, groq = _client(content="hello")

    result = await provider.complete([{"role": "user", "content": "hi"}])

    assert result == "hello"
    assert len(groq.calls) == 1


@pytest.mark.asyncio
async def test_complete_falls_back_to_openrouter():
    provider = _provider_without_clients()
    provider._groq, groq = _client(error=RuntimeError("groq down"))
    provider._openrouter, openrouter = _client(content="from openrouter")

    result = await provider.complete([{"role": "user", "content": "hi"}])

    assert result == "from openrouter"
    assert len(groq.calls) == 1
    assert len(openrouter.calls) == 1


@pytest.mark.asyncio
async def test_complete_raises_when_all_providers_fail():
    provider = _provider_without_clients()
    provider._groq, _ = _client(error=RuntimeError("boom"))
    provider._openrouter, _ = _client(error=RuntimeError("bang"))

    with pytest.raises(ServiceUnavailableError):
        await provider.complete([{"role": "user", "content": "hi"}])


@pytest.mark.asyncio
async def test_complete_raises_when_no_providers_configured():
    provider = _provider_without_clients()
    with pytest.raises(ServiceUnavailableError):
        await provider.complete([{"role": "user", "content": "hi"}])


@pytest.mark.asyncio
async def test_complete_sets_json_response_format():
    provider = _provider_without_clients()
    provider._groq, groq = _client(content="{}")

    await provider.complete([{"role": "user", "content": "hi"}], response_json=True)

    assert groq.calls[0]["response_format"] == {"type": "json_object"}


@pytest.mark.asyncio
async def test_stream_yields_tokens():
    provider = _provider_without_clients()
    provider._groq, _ = _client(stream_tokens=["a", "b", "c"])

    tokens = [tok async for tok in provider.stream([{"role": "user", "content": "hi"}])]
    assert tokens == ["a", "b", "c"]


@pytest.mark.asyncio
async def test_stream_raises_when_no_providers():
    provider = _provider_without_clients()
    with pytest.raises(ServiceUnavailableError):
        async for _ in provider.stream([{"role": "user", "content": "hi"}]):
            pass


def test_get_llm_returns_singleton(monkeypatch):
    monkeypatch.setattr(llm_module, "_provider", None)
    assert get_llm() is get_llm()
