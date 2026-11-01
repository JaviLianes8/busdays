"""Regression contracts for invalid inputs and repeated holiday options."""

from __future__ import annotations

import os
import subprocess
import sys
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


@pytest.mark.parametrize("name", ["following", "Forward", "Modified_Following"])
def test_roll_ignores_raising_lower_override(name: str) -> None:
    class Name(str):
        def lower(self) -> str:
            raise RuntimeError("SECRET_SENTINEL")

    assert Roll(Name(name)) is Roll(name)


@pytest.mark.parametrize("name", ["following", "Forward", "Modified_Following"])
def test_roll_ignores_misleading_lower_override(name: str) -> None:
    class Name(str):
        def lower(self) -> str:
            return "preceding"

    assert Roll(Name(name)) is Roll(name)


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


@pytest.mark.parametrize("count", [4096, 4097])
def test_cli_process_arguments_obey_limit(
    count: int, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["busdays", *(["--help"] * count)])
    with pytest.raises(SystemExit) as error:
        main()
    output = capsys.readouterr()
    if count == 4096:
        assert error.value.code == 0
        assert "usage: busdays" in output.out
        assert output.err == ""
    else:
        assert error.value.code == 2
        assert output.out == ""
        assert "at most 4096 arguments" in output.err
        assert len(output.err) < 500


@pytest.mark.parametrize("count", [4096, 4097])
def test_cli_subprocess_arguments_obey_limit(count: int) -> None:
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"))
    result = subprocess.run(
        [sys.executable, "-m", "busdays", *(["--help"] * count)],
        capture_output=True,
        text=True,
        env=env,
        timeout=240,
        check=False,
    )
    if count == 4096:
        assert result.returncode == 0
        assert "usage: busdays" in result.stdout
        assert result.stderr == ""
    else:
        assert result.returncode == 2
        assert result.stdout == ""
        assert "at most 4096 arguments" in result.stderr
        assert len(result.stderr) < 500


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
