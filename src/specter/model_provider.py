from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request as UrlRequest
from urllib.request import urlopen


@dataclass(frozen=True)
class ModelRequest:
    model: str
    prompt: str
    max_tokens: int = 512
    temperature: float | None = None


@dataclass(frozen=True)
class ModelResult:
    text: str
    provider: str
    token_count: int


class ModelProvider:
    def complete(self, request: ModelRequest) -> ModelResult:
        raise NotImplementedError


class ModelProviderError(RuntimeError):
    pass


class OpenAICompatibleHttpProvider(ModelProvider):
    """HTTP provider for Dullahan and other OpenAI-compatible completion APIs."""

    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: float = 120.0,
        api_key: str | None = None,
        api_key_env: str | None = None,
        model_override: str | None = None,
        provider_name: str = "openai-compatible-http",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.api_key = api_key or (os.getenv(api_key_env) if api_key_env else None)
        self.model_override = model_override
        self.provider_name = provider_name

    def complete(self, request: ModelRequest) -> ModelResult:
        payload = {
            "model": self.model_override or request.model,
            "prompt": request.prompt,
            "max_tokens": request.max_tokens,
        }
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        http_request = UrlRequest(
            url=f"{self.base_url}/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urlopen(http_request, timeout=self.timeout_seconds) as response:
                response_body = response.read().decode("utf-8")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ModelProviderError(
                f"model provider failed with HTTP {exc.code}: {detail}"
            ) from exc
        except URLError as exc:
            raise ModelProviderError(f"model provider request failed: {exc.reason}") from exc

        data = json.loads(response_body)
        text = self._extract_text(data)
        usage = data.get("usage", {})
        token_count = usage.get("completion_tokens") or len(text.split())
        return ModelResult(
            text=text,
            provider=self.provider_name,
            token_count=int(token_count),
        )

    def _extract_text(self, data: dict) -> str:
        choices = data.get("choices") or []
        if not choices:
            raise ModelProviderError("model provider response contained no choices")

        first_choice = choices[0]
        if "text" in first_choice:
            return str(first_choice["text"]).strip()

        message = first_choice.get("message")
        if isinstance(message, dict) and "content" in message:
            return str(message["content"]).strip()

        raise ModelProviderError("model provider response contained no text")
