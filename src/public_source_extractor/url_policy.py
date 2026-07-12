from __future__ import annotations

import ipaddress
import re
import urllib.parse

from .errors import InputRejected


BLOCKED_HOSTS = {
    "accounts.google.com",
    "calendar.google.com",
    "docs.google.com",
    "drive.google.com",
    "mail.google.com",
    "search.google.com",
    "twitter.com",
    "x.com",
}

LOCAL_SUFFIXES = (".local", ".localhost", ".internal", ".home", ".lan")

BLOCKED_PATH_RE = re.compile(
    r"(^|/)(wp-admin|wp-login\.php|admin|login|logout|oauth|callback)(/|$)",
    re.IGNORECASE,
)

DENIED_QUERY_NAMES = {
    "access_key",
    "access_token",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "code",
    "cookie",
    "credential",
    "credentials",
    "key",
    "passwd",
    "password",
    "refresh_token",
    "secret",
    "session",
    "sessionid",
    "token",
}

DENIED_QUERY_SEGMENTS = {
    "auth",
    "authorization",
    "cookie",
    "credential",
    "credentials",
    "key",
    "passwd",
    "password",
    "secret",
    "session",
    "signature",
    "token",
}


def _decode_repeated(value: str, rounds: int = 3) -> str:
    decoded = value
    for _ in range(rounds):
        next_value = urllib.parse.unquote(decoded)
        if next_value == decoded:
            break
        decoded = next_value
    return decoded


def _query_name_is_sensitive(name: str) -> bool:
    decoded = _decode_repeated(name).lower()
    canonical = re.sub(r"[^a-z0-9]+", "_", decoded).strip("_")
    if canonical in DENIED_QUERY_NAMES:
        return True
    segments = {segment for segment in canonical.split("_") if segment}
    return bool(segments & DENIED_QUERY_SEGMENTS)


def _validate_host(host: str) -> None:
    if not host or any(ord(char) > 127 for char in host):
        raise InputRejected()
    if "%" in host or "\\" in host:
        raise InputRejected()

    normalized = host.lower().rstrip(".")
    if normalized in {"localhost", "local"} or normalized.endswith(LOCAL_SUFFIXES):
        raise InputRejected()
    if normalized in BLOCKED_HOSTS or any(
        normalized.endswith(f".{blocked}") for blocked in BLOCKED_HOSTS
    ):
        raise InputRejected()

    try:
        ip = ipaddress.ip_address(normalized)
    except ValueError:
        ip = None

    if ip is not None:
        if not ip.is_global:
            raise InputRejected()
        return

    # Reject legacy integer, octal, and hex IPv4 spellings instead of relying on resolver behavior.
    if re.fullmatch(r"[0-9.]+", normalized) or normalized.startswith(("0x", "0X")):
        raise InputRejected()
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?", normalized):
        raise InputRejected()
    if ".." in normalized or "." not in normalized:
        raise InputRejected()


def validate_public_url(raw_url: str) -> urllib.parse.ParseResult:
    if not raw_url or any(char in raw_url for char in ("\r", "\n", "\x00")):
        raise InputRejected()

    parsed = urllib.parse.urlparse(raw_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or not parsed.hostname:
        raise InputRejected()
    if parsed.username or parsed.password or parsed.fragment:
        raise InputRejected()

    try:
        port = parsed.port
    except ValueError as exc:
        raise InputRejected() from exc
    expected_port = 443 if parsed.scheme == "https" else 80
    if port is not None and port != expected_port:
        raise InputRejected()

    raw_host = parsed.netloc.rsplit("@", 1)[-1]
    if raw_host.startswith("["):
        raw_host = raw_host[1 : raw_host.find("]")]
    else:
        raw_host = raw_host.rsplit(":", 1)[0] if ":" in raw_host else raw_host
    if "%" in raw_host or any(ord(char) > 127 for char in raw_host):
        raise InputRejected()
    _validate_host(parsed.hostname)

    decoded_path = _decode_repeated(parsed.path or "/").replace("\\", "/")
    if BLOCKED_PATH_RE.search(decoded_path):
        raise InputRejected()

    try:
        query_pairs = urllib.parse.parse_qsl(
            parsed.query,
            keep_blank_values=True,
            strict_parsing=False,
            max_num_fields=100,
        )
    except ValueError as exc:
        raise InputRejected() from exc
    for name, _value in query_pairs:
        if _query_name_is_sensitive(name):
            raise InputRejected()

    return parsed


def validate_provider_resolved_url(raw_url: object) -> str | None:
    if raw_url is None:
        return None
    if not isinstance(raw_url, str):
        raise InputRejected()
    validate_public_url(raw_url)
    return raw_url
