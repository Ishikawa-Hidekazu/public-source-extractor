from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .errors import OutputFailure
from .provider import FirecrawlKeylessProvider, ProviderResult


def build_success_envelope(
    requested_url: str,
    mode: str,
    result: ProviderResult,
) -> dict[str, Any]:
    warnings = [
        {
            "code": "experimental_provider",
            "message": "Keyless availability and limits are not guaranteed.",
        }
    ]
    if result.resolved_url is None:
        warnings.append(
            {
                "code": "resolved_url_unavailable",
                "message": "The provider did not return redirect metadata for post-checking.",
            }
        )
    return {
        "schema_version": "0.1",
        "ok": True,
        "source": {
            "requested_url": requested_url,
            "resolved_url": result.resolved_url,
            "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
                "+00:00", "Z"
            ),
        },
        "mode": mode,
        "content": result.content,
        "metadata": {
            "title": result.title,
            "description": result.description,
            "content_type": result.content_type,
            "source_http_status": result.source_http_status,
        },
        "provider": {
            "name": FirecrawlKeylessProvider.name,
            "access": FirecrawlKeylessProvider.access,
            "http_status": result.provider_http_status,
            "credits_used": result.credits_used,
            "elapsed_ms": result.elapsed_ms,
        },
        "warnings": warnings,
    }


def render_markdown(envelope: dict[str, Any]) -> str:
    source = envelope["source"]
    metadata = envelope["metadata"]
    provider = envelope["provider"]
    front_matter = {
        "schema_version": envelope["schema_version"],
        "source_url": source["requested_url"],
        "resolved_url": source["resolved_url"],
        "fetched_at": source["fetched_at"],
        "title": metadata["title"],
        "content_type": metadata["content_type"],
        "source_http_status": metadata["source_http_status"],
        "provider": provider["name"],
        "provider_access": provider["access"],
        "provider_credits_used": provider["credits_used"],
        "provider_elapsed_ms": provider["elapsed_ms"],
    }
    lines = ["---"]
    lines.extend(
        f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in front_matter.items()
    )
    lines.extend(["---", "", str(envelope["content"]), ""])
    return "\n".join(lines)


def render_json(envelope: dict[str, Any], pretty: bool) -> str:
    indent = 2 if pretty else None
    return json.dumps(envelope, ensure_ascii=False, indent=indent, separators=None) + "\n"


def write_new_file_atomic(path: Path, content: str) -> None:
    try:
        parent = path.parent.resolve(strict=True)
        _reject_symlink_components(path.parent)
        if not parent.is_dir() or path.exists() or path.is_symlink():
            raise OutputFailure()

        fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=parent)
        temporary = Path(temporary_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.link(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
    except OutputFailure:
        raise
    except (OSError, RuntimeError) as exc:
        raise OutputFailure() from exc


def _reject_symlink_components(path: Path) -> None:
    # Inspect the caller-selected path without resolving it first. macOS exposes
    # /tmp and /var as stable platform aliases, so only those two are exempt.
    platform_aliases = {Path("/tmp"), Path("/var")}
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for component in absolute.parts[1:]:
        current /= component
        if current.is_symlink() and current not in platform_aliases:
            raise OutputFailure()
