from __future__ import annotations

import io
import json
import socket
import unittest
from unittest.mock import patch

from public_source_extractor.errors import (
    InvalidProviderResponse,
    ProviderFailure,
    ProviderRateLimited,
    ProviderTimeout,
)
from public_source_extractor.provider import FirecrawlKeylessProvider


class FakeResponse:
    def __init__(self, payload: object, status: int = 200) -> None:
        self.status = status
        self._body = json.dumps(payload).encode()

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self, _limit: int) -> bytes:
        return self._body


class ProviderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = FirecrawlKeylessProvider()

    def test_accepts_markdown_fixture_and_public_redirect_metadata(self) -> None:
        fixture = {
            "success": True,
            "data": {
                "markdown": "# Example",
                "metadata": {
                    "sourceURL": "https://www.example.com/",
                    "statusCode": 200,
                    "contentType": "text/html",
                    "title": "Example",
                    "creditsUsed": 1,
                },
            },
        }
        with patch("urllib.request.urlopen", return_value=FakeResponse(fixture)):
            result = self.provider.extract("https://example.com/", "markdown", 10)
        self.assertEqual(result.content, "# Example")
        self.assertEqual(result.resolved_url, "https://www.example.com/")

    def test_rejects_private_redirect_metadata(self) -> None:
        fixture = {
            "success": True,
            "data": {
                "markdown": "private",
                "metadata": {"sourceURL": "http://127.0.0.1/admin"},
            },
        }
        with patch("urllib.request.urlopen", return_value=FakeResponse(fixture)):
            with self.assertRaises(InvalidProviderResponse):
                self.provider.extract("https://example.com/", "markdown", 10)

    def test_rejects_wrong_content_type_for_mode(self) -> None:
        fixture = {"success": True, "data": {"json": "wrong", "metadata": {}}}
        with patch("urllib.request.urlopen", return_value=FakeResponse(fixture)):
            with self.assertRaises(InvalidProviderResponse):
                self.provider.extract("https://example.com/", "json", 10)

    def test_raw_provider_body_is_not_exposed(self) -> None:
        secret = "do-not-expose-provider-body"
        response = FakeResponse({"success": False, "error": secret})
        with patch("urllib.request.urlopen", return_value=response):
            with self.assertRaises(ProviderFailure) as caught:
                self.provider.extract("https://example.com/", "markdown", 10)
        self.assertNotIn(secret, str(caught.exception))
        self.assertNotIn(secret, json.dumps(caught.exception.envelope()))

    def test_maps_429_without_exposing_body(self) -> None:
        import urllib.error

        error = urllib.error.HTTPError(
            "https://api.firecrawl.dev/v2/scrape",
            429,
            "rate limited with private body",
            {},
            io.BytesIO(b"private body"),
        )
        with patch("urllib.request.urlopen", side_effect=error):
            with self.assertRaises(ProviderRateLimited) as caught:
                self.provider.extract("https://example.com/", "markdown", 10)
        self.assertNotIn("private body", json.dumps(caught.exception.envelope()))

    def test_maps_timeout_without_exposing_network_details(self) -> None:
        with patch("urllib.request.urlopen", side_effect=socket.timeout("private network detail")):
            with self.assertRaises(ProviderTimeout) as caught:
                self.provider.extract("https://example.com/", "markdown", 10)
        self.assertNotIn("private network detail", json.dumps(caught.exception.envelope()))
