from __future__ import annotations

import json
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol

from .errors import (
    InputRejected,
    InvalidProviderResponse,
    ProviderFailure,
    ProviderRateLimited,
    ProviderTimeout,
)
from .url_policy import validate_provider_resolved_url


FIRECRAWL_ENDPOINT = "https://api.firecrawl.dev/v2/scrape"
MAX_RESPONSE_BYTES = 10 * 1024 * 1024

STRUCTURED_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "main_argument": {"type": "string"},
        "key_points": {"type": "array", "items": {"type": "string"}},
        "external_sources": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["title", "summary", "main_argument"],
}


@dataclass(frozen=True)
class ProviderResult:
    content: str | dict[str, Any]
    resolved_url: str | None
    title: str | None
    description: str | None
    content_type: str | None
    source_http_status: int | None
    provider_http_status: int
    credits_used: int | None
    elapsed_ms: int


class ExtractionProvider(Protocol):
    def extract(self, url: str, mode: str, timeout_seconds: int) -> ProviderResult: ...


class FirecrawlKeylessProvider:
    name = "firecrawl-keyless"
    access = "experimental"

    def extract(self, url: str, mode: str, timeout_seconds: int) -> ProviderResult:
        formats: list[Any]
        if mode == "markdown":
            formats = ["markdown"]
        else:
            formats = [{"type": "json", "schema": STRUCTURED_SCHEMA}]
        payload = {
            "url": url,
            "formats": formats,
            "onlyMainContent": True,
            "removeBase64Images": True,
            "timeout": timeout_seconds * 1000,
        }
        body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        request = urllib.request.Request(
            FIRECRAWL_ENDPOINT,
            data=body,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "public-source-extractor/0.1.0-alpha.1",
            },
            method="POST",
        )

        started = time.monotonic()
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds + 5) as response:
                status = response.status
                raw = response.read(MAX_RESPONSE_BYTES + 1)
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                raise ProviderRateLimited() from exc
            raise ProviderFailure() from exc
        except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
            reason = getattr(exc, "reason", None)
            if isinstance(exc, (TimeoutError, socket.timeout)) or isinstance(
                reason, (TimeoutError, socket.timeout)
            ):
                raise ProviderTimeout() from exc
            raise ProviderFailure() from exc

        elapsed_ms = round((time.monotonic() - started) * 1000)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise InvalidProviderResponse()
        try:
            document = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InvalidProviderResponse() from exc
        if status != 200 or not isinstance(document, dict) or document.get("success") is not True:
            raise ProviderFailure()

        data = document.get("data")
        if not isinstance(data, dict):
            raise InvalidProviderResponse()
        metadata = data.get("metadata")
        if metadata is None:
            metadata = {}
        if not isinstance(metadata, dict):
            raise InvalidProviderResponse()

        try:
            resolved_url = validate_provider_resolved_url(
                metadata.get("sourceURL") or metadata.get("url")
            )
        except InputRejected as exc:
            raise InvalidProviderResponse() from exc
        content = data.get("markdown") if mode == "markdown" else data.get("json")
        if mode == "markdown" and not isinstance(content, str):
            raise InvalidProviderResponse()
        if mode == "json" and not isinstance(content, dict):
            raise InvalidProviderResponse()

        source_status = metadata.get("statusCode")
        if not isinstance(source_status, int) or isinstance(source_status, bool):
            source_status = None
        credits_used = metadata.get("creditsUsed")
        if not isinstance(credits_used, int) or isinstance(credits_used, bool):
            credits_used = None

        return ProviderResult(
            content=content,
            resolved_url=resolved_url,
            title=_optional_string(metadata.get("title") or metadata.get("og:title")),
            description=_optional_string(
                metadata.get("description") or metadata.get("og:description")
            ),
            content_type=_optional_string(metadata.get("contentType")),
            source_http_status=source_status,
            provider_http_status=status,
            credits_used=credits_used,
            elapsed_ms=elapsed_ms,
        )


def _optional_string(value: object) -> str | None:
    return value if isinstance(value, str) else None
