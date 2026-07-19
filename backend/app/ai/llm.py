"""LLM provider abstraction with Groq as default and OpenRouter as fallback."""
from __future__ import annotations

from collections.abc import AsyncIterator

from app.core.config import settings
from app.core.errors import ServiceUnavailableError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Message format: list of {"role": "system"|"user"|"assistant", "content": str}
Messages = list[dict]

NOT_CONFIGURED_MESSAGE = (
    "AI provider is not configured. Please add GROQ_API_KEY or "
    "OPENROUTER_API_KEY to your environment variables."
)


class LLMProvider:
    """Thin async wrapper around chat-completion providers.

    Prefers Groq (via the OpenAI-compatible endpoint) and falls back to OpenRouter
    when Groq is unavailable or errors out.
    """

    def __init__(self) -> None:
        self._groq = None
        self._openrouter = None
        self._init_clients()

    def _init_clients(self) -> None:
        try:
            from openai import AsyncOpenAI
        except ImportError:  # pragma: no cover - dependency guaranteed in prod
            logger.warning("openai package not installed; LLM disabled")
            return

        if settings.GROQ_API_KEY:
            self._groq = AsyncOpenAI(
                api_key=settings.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
            )
        if settings.OPENROUTER_API_KEY:
            self._openrouter = AsyncOpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL,
            )

    @property
    def available(self) -> bool:
        return self._groq is not None or self._openrouter is not None

    async def complete(
        self,
        messages: Messages,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_json: bool = False,
    ) -> str:
        """Return a full completion string, trying Groq then OpenRouter."""
        temperature = settings.LLM_TEMPERATURE if temperature is None else temperature
        max_tokens = settings.LLM_MAX_TOKENS if max_tokens is None else max_tokens
        kwargs: dict = {"temperature": temperature, "max_tokens": max_tokens}
        if response_json:
            kwargs["response_format"] = {"type": "json_object"}

        if not self.available:
            raise ServiceUnavailableError(NOT_CONFIGURED_MESSAGE)

        last_error: Exception | None = None
        for client, model, name in self._ordered_clients():
            try:
                resp = await client.chat.completions.create(
                    model=model, messages=messages, **kwargs
                )
                return resp.choices[0].message.content or ""
            except Exception as exc:  # noqa: BLE001 - provider errors are opaque
                logger.warning("LLM provider %s failed: %s", name, exc)
                last_error = exc
                continue
        raise ServiceUnavailableError(
            "All configured LLM providers failed."
            + (f" Last error: {last_error}" if last_error else "")
        )

    async def stream(
        self,
        messages: Messages,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """Yield completion token deltas, trying Groq then OpenRouter."""
        temperature = settings.LLM_TEMPERATURE if temperature is None else temperature
        max_tokens = settings.LLM_MAX_TOKENS if max_tokens is None else max_tokens

        if not self.available:
            raise ServiceUnavailableError(NOT_CONFIGURED_MESSAGE)

        last_error: Exception | None = None
        for client, model, name in self._ordered_clients():
            try:
                stream = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                )
                async for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning("LLM stream provider %s failed: %s", name, exc)
                last_error = exc
                continue
        raise ServiceUnavailableError(
            "All configured LLM providers failed while streaming."
            + (f" Last error: {last_error}" if last_error else "")
        )

    def _ordered_clients(self):
        override = settings.MODEL_NAME or None
        clients = []
        if self._groq is not None:
            clients.append((self._groq, override or settings.GROQ_MODEL, "groq"))
        if self._openrouter is not None:
            clients.append((self._openrouter, override or settings.OPENROUTER_MODEL, "openrouter"))
        return clients


_provider: LLMProvider | None = None


def get_llm() -> LLMProvider:
    """Return a lazily-instantiated, process-wide LLM provider."""
    global _provider
    if _provider is None:
        _provider = LLMProvider()
    return _provider
