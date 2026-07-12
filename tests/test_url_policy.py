from __future__ import annotations

import unittest

from public_source_extractor.errors import InputRejected
from public_source_extractor.url_policy import validate_public_url


class UrlPolicyTests(unittest.TestCase):
    def assert_rejected(self, url: str) -> None:
        with self.assertRaises(InputRejected):
            validate_public_url(url)

    def test_accepts_normal_public_urls(self) -> None:
        for url in (
            "https://example.com/",
            "http://example.com:80/article?topic=code",
            "https://example.com:443/article?product_code=abc",
            "https://8.8.8.8/",
            "https://[2606:4700:4700::1111]/",
        ):
            with self.subTest(url=url):
                validate_public_url(url)

    def test_rejects_fragment(self) -> None:
        self.assert_rejected("https://example.com/article#access_token=value")

    def test_checks_decoded_query_parameter_names_only(self) -> None:
        self.assert_rejected("https://example.com/?api%5Fkey=value")
        self.assert_rejected("https://example.com/?%2574oken=value")
        validate_public_url("https://example.com/?topic=token-security")
        validate_public_url("https://example.com/?product_code=abc")

    def test_rejects_compound_sensitive_query_names(self) -> None:
        names = (
            "client_secret",
            "id_token",
            "oauth_token",
            "password_reset_token",
            "x-amz-credential",
            "x-amz-signature",
            "x-goog-credential",
            "x-goog-signature",
            "session_id",
            "auth-key",
        )
        for name in names:
            with self.subTest(name=name):
                self.assert_rejected(f"https://example.com/?{name}=value")

    def test_allows_normal_compound_query_names(self) -> None:
        for name in ("product_code", "article_id", "page_number", "source_type"):
            with self.subTest(name=name):
                validate_public_url(f"https://example.com/?{name}=value")

    def test_rejects_unicode_and_encoded_hosts(self) -> None:
        self.assert_rejected("https://例え.テスト/")
        self.assert_rejected("https://%65xample.com/")

    def test_rejects_ipv6_zone_id(self) -> None:
        self.assert_rejected("http://[fe80::1%25en0]/")

    def test_rejects_non_default_ports(self) -> None:
        self.assert_rejected("https://example.com:8443/")
        self.assert_rejected("http://example.com:8080/")

    def test_rejects_ambiguous_and_private_ip_forms(self) -> None:
        for url in (
            "http://127.1/",
            "http://2130706433/",
            "http://0177.0.0.1/",
            "http://0x7f000001/",
            "http://10.0.0.1/",
            "http://[::1]/",
            "http://169.254.169.254/",
        ):
            with self.subTest(url=url):
                self.assert_rejected(url)

    def test_rejects_encoded_admin_path(self) -> None:
        self.assert_rejected("https://example.com/%256cogin")
