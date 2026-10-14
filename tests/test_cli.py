from __future__ import annotations

import io
from pathlib import Path

import pytest

from busdays._cli import main


def _run(capsys: pytest.CaptureFixture[str], *args: str) -> tuple[int, str, str]:
    try:
        code = main(list(args))
    except SystemExit as exc:
        code = int(exc.code or 0)
    out, err = capsys.readouterr()
    return code, out, err


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (("add", "2026-01-02", "1"), "2026-01-05\n"),
        (("add", "2026-01-05", "-3"), "2025-12-31\n"),
        (("add", "2026-01-31", "0", "--roll", "modified_following"), "2026-01-30\n"),
        (("count", "2026-01-05", "2026-01-12"), "5\n"),
        (("count", "2026-01-12", "2026-01-05"), "-5\n"),
        (("roll", "2026-01-31"), "2026-02-02\n"),
        (("roll", "2026-01-31", "preceding"), "2026-01-30\n"),
        (("is", "2026-01-05"), "yes\n"),
        (("list", "2026-01-01", "2026-01-06"), "2026-01-01\n2026-01-02\n2026-01-05\n"),
        (("add", "2026-01-01", "1", "--weekend", "4,5"), "2026-01-04\n"),
        (("add", "2026-01-01", "1", "--weekmask", "Sun Mon Tue Wed Thu"), "2026-01-04\n"),
        (("add", "2026-01-02", "1", "--holiday", "2026-01-05"), "2026-01-06\n"),
        (("count", "2026-01-05", "2026-01-12", "--weekend", ""), "7\n"),
    ],
)
def test_commands(capsys: pytest.CaptureFixture[str], args: tuple[str, ...], expected: str) -> None:
    assert _run(capsys, *args) == (0, expected, "")


def test_not_a_business_day_exits_1(capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(capsys, "is", "2026-01-03") == (1, "no\n", "")


def test_holiday_files_allow_comments_and_blank_lines(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    listing = tmp_path / "holidays.txt"
    listing.write_text("# bank holidays\n\n2026-01-05  # Monday\n2026-01-06\n", encoding="utf-8")
    code, out, _ = _run(capsys, "add", "2026-01-02", "1", "--holidays", str(listing))
    assert (code, out) == (0, "2026-01-07\n")


def test_holiday_files_read_from_standard_input(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("2026-01-05\n"))
    assert _run(capsys, "add", "2026-01-02", "1", "--holidays", "-")[:2] == (0, "2026-01-06\n")


def test_a_bad_line_in_a_holiday_file_names_the_line(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    listing = tmp_path / "holidays.txt"
    listing.write_text("2026-01-05\n05/01/2026\n", encoding="utf-8")
    code, out, err = _run(capsys, "add", "2026-01-02", "1", "--holidays", str(listing))
    assert (code, out) == (2, "")
    assert "holidays.txt:2" in err and "not an ISO date" in err


def test_a_missing_holiday_file_is_reported(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    code, _, err = _run(capsys, "is", "2026-01-05", "--holidays", str(tmp_path / "none.txt"))
    assert code == 2 and err.startswith("busdays: error:")


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (("add", "2026-13-01", "1"), "not an ISO date"),
        (("add", "20260105", "1"), "not an ISO date"),
        (("add", "2026-01-05", "1.5"), "not a whole number"),
        (("roll", "2026-01-03", "sideways"), "unknown roll"),
        (("add", "2026-01-05", "1", "--weekend", "7"), "weekday numbers"),
        (("add", "2026-01-05", "1", "--weekmask", "Funday"), "invalid weekmask"),
        (("add", "2026-01-05", "1", "--weekend", "5", "--weekmask", "1"), "not allowed with"),
        (("add", "9999-12-31", "1"), "years 1 to 9999"),
        (("add", "2026-01-03", "1", "--roll", "raise"), "not a business day"),
        (("add", "2026-01-05", "1", "--weekend", "0,1,2,3,4,5,6"), "no business day exists"),
    ],
)
def test_bad_input_exits_2(
    capsys: pytest.CaptureFixture[str], args: tuple[str, ...], message: str
) -> None:
    code, out, err = _run(capsys, *args)
    assert (code, out) == (2, "")
    assert message in err


def test_a_command_is_required(capsys: pytest.CaptureFixture[str]) -> None:
    assert _run(capsys)[0] == 2


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    import busdays

    assert _run(capsys, "--version") == (0, f"busdays {busdays.__version__}\n", "")
