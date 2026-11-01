"""Regression contracts for invalid inputs and repeated holiday options."""

from __future__ import annotations

from pathlib import Path

import pytest

from busdays import Roll
from busdays._cli import main


def test_deeply_nested_roll_input_has_a_bounded_value_error() -> None:
    value: object = []
    for _ in range(100_000):
        value = [value]
    with pytest.raises(ValueError, match="unknown roll") as error:
        Roll(value)
    assert len(str(error.value)) < 100


def test_invalid_roll_does_not_call_repr() -> None:
    class InvalidName(str):
        def __repr__(self) -> str:
            raise AssertionError("invalid values must not be represented")

    with pytest.raises(ValueError, match="unknown roll"):
        Roll(InvalidName("invalid"))


@pytest.mark.parametrize("option", ["--holiday=2026-01-06", "--holidays=unused.txt"])
def test_cli_rejects_excess_arguments_before_parsing(
    option: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def unexpected_parse(*args: object, **kwargs: object) -> None:
        pytest.fail("excess arguments reached argparse")

    monkeypatch.setattr("argparse.ArgumentParser.parse_args", unexpected_parse)
    with pytest.raises(SystemExit) as error:
        main(["is", "2026-01-05"] + [option] * 4095)
    assert error.value.code == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert "at most 4096 arguments" in output.err
    assert option not in output.err


def test_cli_accepts_the_argument_limit(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["is", "2026-01-05"] + ["--holiday=2026-01-06"] * 4094) == 0
    assert capsys.readouterr() == ("yes\n", "")


def test_repeated_holiday_files_contribute_all_dates(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    first, second = tmp_path / "first.txt", tmp_path / "second.txt"
    first.write_text("2026-01-05\n", encoding="utf-8")
    second.write_text("2026-01-06\n", encoding="utf-8")
    assert (
        main(["add", "2026-01-02", "1", "--holidays", str(first), "--holidays", str(second)]) == 0
    )
    assert capsys.readouterr() == ("2026-01-07\n", "")


def test_malformed_later_holiday_file_is_rejected(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    first, second = tmp_path / "first.txt", tmp_path / "second.txt"
    first.write_text("2026-01-05\n", encoding="utf-8")
    second.write_text("2026-01-06\ninvalid\n", encoding="utf-8")
    assert (
        main(["add", "2026-01-02", "1", "--holidays", str(first), "--holidays", str(second)]) == 2
    )
    output = capsys.readouterr()
    assert output.out == ""
    assert "holiday file line 2" in output.err
