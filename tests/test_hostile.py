"""Seeded parser properties and bounded diagnostics for hostile input."""

from __future__ import annotations

import random
from collections.abc import Callable
from datetime import date

import pytest

from busdays import Calendar, Roll, roll
from busdays._cli import main


@pytest.mark.parametrize("seed", [19, 1729, 65537])
def test_parser_fuzz_has_only_documented_results(seed: int) -> None:
    rng = random.Random(seed)
    alphabet = "01MonTueWedThuFriSatSun _-\t\n,\x00\ud800\U0001f600"
    for _ in range(3000):
        text = "".join(rng.choices(alphabet, k=rng.randrange(150)))
        try:
            calendar = Calendar.from_weekmask(text)
        except ValueError as error:
            assert len(str(error)) < 200
        else:
            assert Calendar.from_weekmask(calendar.weekmask) == calendar
        try:
            mode = Roll(text)
        except ValueError as error:
            assert len(str(error)) < 200
        else:
            assert Roll(mode.value) is mode


@pytest.mark.parametrize("size", [100_000, 1_000_000])
def test_large_parsers_and_errors_are_bounded(size: int) -> None:
    secret = "private-token-" + "x" * size
    calls: list[Callable[[], object]] = [
        lambda: Roll(secret),
        lambda: roll(date(2026, 1, 1), secret),
        lambda: Calendar.from_weekmask(secret),
        lambda: Calendar.from_weekmask(" " * size),
    ]
    for call in calls:
        with pytest.raises(ValueError) as caught:
            call()
        assert "private-token" not in str(caught.value)
        assert len(str(caught.value)) < 200
    assert Calendar.from_weekmask("Mon " * (size // 4)).weekmask == "1000000"
    assert Roll("_" * size + "forward") is Roll.FOLLOWING


@pytest.mark.parametrize(
    "args",
    [
        ["secret-token"],
        ["is", "secret-token"],
        ["is", "2026-01-05", "secret-token"],
        ["roll", "2026-01-05", "secret-token"],
        ["add", "2026-01-05", "secret-token"],
        ["add", "2026-01-05", "1", "--weekend", "secret-token"],
        ["add", "2026-01-05", "1", "--weekmask", "secret-token"],
    ],
)
def test_cli_never_echoes_invalid_values(
    args: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    try:
        result = main(args)
    except SystemExit as error:
        result = int(error.code or 0)
    assert result == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert "secret-token" not in output.err
    assert len(output.err) < 1000


def test_cli_huge_counts_and_leading_zeros(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["add", "2026-01-05", "9" * 100_000])
    assert caught.value.code == 2
    assert len(capsys.readouterr().err) < 1000
    assert main(["add", "2026-01-05", "0" * 100_000 + "1"]) == 0
    assert capsys.readouterr().out == "2026-01-06\n"
