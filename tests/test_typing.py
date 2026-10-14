"""The public API is typed: mypy infers results and rejects bad calls."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

api = pytest.importorskip("mypy.api")

SRC = Path(__file__).resolve().parents[1] / "src"

SNIPPET = """
import datetime as dt
import busdays as b
reveal_type(b.add_business_days(dt.date(2026, 1, 1), 2))
reveal_type(b.business_days_between(dt.date(2026, 1, 1), dt.date(2026, 2, 1)))
reveal_type(b.Calendar().business_days(dt.date(2026, 1, 1), dt.date(2026, 2, 1)))
reveal_type(b.Calendar().is_business_day(dt.date(2026, 1, 1)))
reveal_type(b.Roll("forward"))
b.add_business_days("2026-01-01", 2)
b.add_business_days(dt.date(2026, 1, 1), 2.5)
b.Calendar(weekend="56")
b.roll(dt.date(2026, 1, 1), 3)
b.add_business_days(dt.date(2026, 1, 1), 2, (5, 6))
b.roll(dt.date(2026, 1, 1), "modifiedfollowing", holidays=[dt.date(2026, 1, 2)])
"""


@pytest.fixture(scope="module")
def mypy_output(tmp_path_factory: pytest.TempPathFactory) -> str:
    folder = tmp_path_factory.mktemp("typing")
    target = folder / "snippet.py"
    target.write_text(SNIPPET, encoding="utf-8")
    config = folder / "mypy.ini"
    config.write_text(f"[mypy]\nmypy_path = {SRC.as_posix()}\n", encoding="utf-8")
    cache = str(folder / "cache")
    out, err, _ = api.run(
        ["--strict", "--config-file", str(config), "--cache-dir", cache, str(target)]
    )
    return str(out) + str(err)


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        (4, r"datetime\.date"),
        (5, r"(builtins\.)?int"),
        (6, r"typing\.Iterator\[datetime\.date\]"),
        (7, r"(builtins\.)?bool"),
        (8, r"busdays\._roll\.Roll"),
    ],
)
def test_results_are_inferred(mypy_output: str, line: int, expected: str) -> None:
    pattern = rf'snippet\.py:{line}: note: Revealed type is "{expected}"'
    assert re.search(pattern, mypy_output), mypy_output


@pytest.mark.parametrize(
    ("line", "code"), [(9, "arg-type"), (10, "arg-type"), (11, "arg-type"), (12, "arg-type")]
)
def test_wrong_calls_are_rejected(mypy_output: str, line: int, code: str) -> None:
    assert re.search(rf"snippet\.py:{line}: error: .*\[{code}\]", mypy_output), mypy_output


def test_keyword_only_options_reject_positional_use(mypy_output: str) -> None:
    assert re.search(r"snippet\.py:13: error: Too many positional", mypy_output), mypy_output


def test_valid_calls_type_check(mypy_output: str) -> None:
    assert not re.search(r"snippet\.py:14: error", mypy_output), mypy_output
