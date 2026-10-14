# Contributing

Thanks for taking the time. This project keeps a small, predictable shape.

## Setup

```
pip install -r requirements-dev.txt
```

## Before you open a pull request

- Keep public API in `src/busdays/__init__.py`; internals live in `_`-prefixed modules.
- Add a test for the behaviour you change. Tests inject time, disk and network; they
  never touch the real thing.
- Run `scripts/check.ps1` (format, lint, types, tests) and make sure it passes.
- One logical change per commit, imperative subject line.

## Upstream sources and the slow tests

`python scripts/fetch_upstream.py` downloads the numpy and QuantLib reference pages and the
GOV.UK holiday list named in `data/upstream/MANIFEST.json` into that folder; they are not
committed, and the tests that read them skip until they are fetched. numpy is a test-only
oracle. `pytest -m e2e` builds the wheel and the sdist and drives the installed script.

Open an issue first if the change is large or shifts the public API.
