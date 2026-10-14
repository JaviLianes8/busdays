"""Access to the upstream copies that scripts/fetch_upstream.py fetches into data/upstream/.

The files are not committed: data/upstream/MANIFEST.json pins their URL, size, sha256 and
licence. Tests that read them skip while they are absent.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

import pytest

UPSTREAM = Path(__file__).resolve().parent.parent / "data" / "upstream"
MANIFEST: dict[str, dict[str, Any]] = json.loads(
    (UPSTREAM / "MANIFEST.json").read_text(encoding="utf-8")
)


def fetched(name: str) -> bool:
    """True when the manifest lists ``name`` and the copy is on disk."""
    return name in MANIFEST and (UPSTREAM / name).is_file()


def needs(name: str) -> pytest.MarkDecorator:
    """Skip a test until ``name`` has been fetched."""
    return pytest.mark.skipif(
        not fetched(name), reason=f"{name} not fetched; run python scripts/fetch_upstream.py"
    )


def upstream_text(name: str) -> str:
    """The fetched file as text; HTML is reduced to its visible words, single-spaced."""
    raw = (UPSTREAM / name).read_text(encoding="utf-8", errors="replace")
    if name.endswith((".html", ".htm")):
        raw = html.unescape(re.sub(r"<[^>]+>", " ", raw))
        raw = raw.replace("\u2019", "'")
    return re.sub(r"\s+", " ", raw)
