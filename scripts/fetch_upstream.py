"""Fetch the upstream sources listed in data/upstream/MANIFEST.json.

The files are not part of the repository. Tests that read them skip until this script
has fetched them. Each download is checked against the size and sha256 in the manifest;
the holiday list and the docs are living documents, so ``--accept-new`` stores a changed copy and
records its new size, sha256 and date in the manifest instead of refusing it.

    python scripts/fetch_upstream.py [--accept-new]
"""

from __future__ import annotations

import datetime
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

FOLDER = Path(__file__).resolve().parents[1] / "data" / "upstream"
# Some of the sites refuse requests without a browser-like agent.
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; busdays-fetch)"}


def main(argv: list[str]) -> int:
    accept = "--accept-new" in argv
    path = FOLDER / "MANIFEST.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    failed = 0
    for name, entry in manifest.items():
        request = urllib.request.Request(entry["url"], headers=HEADERS)
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read()
        digest = hashlib.sha256(body).hexdigest()
        if len(body) != entry["size"] or digest != entry["sha256"]:
            if not accept:
                print(f"{name}: got {len(body)} bytes, sha256 {digest}; manifest differs")
                failed += 1
                continue
            entry.update(size=len(body), sha256=digest, fetched=str(datetime.date.today()))
        (FOLDER / name).write_bytes(body)
        print(f"{name}: ok")
    if accept:
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
