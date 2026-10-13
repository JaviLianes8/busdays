"""Command line tool: business-day arithmetic on ISO dates."""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from busdays import __version__
from busdays._calendar import Calendar
from busdays._roll import Roll, parse_roll


def _day(text: str) -> date:
    try:
        if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", text):
            return date.fromisoformat(text)
    except ValueError:
        pass
    raise argparse.ArgumentTypeError(f"not an ISO date (YYYY-MM-DD): {text!r}")


def _count(text: str) -> int:
    if not re.fullmatch(r"[+-]?[0-9]+", text):
        raise argparse.ArgumentTypeError(f"not a whole number: {text!r}")
    return int(text)


def _roll(text: str) -> Roll:
    try:
        return parse_roll(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from None


def _weekend(text: str) -> tuple[int, ...]:
    if not re.fullmatch(r"([0-6](,[0-6])*)?", text):
        raise argparse.ArgumentTypeError(f"weekend must be weekday numbers like 5,6: {text!r}")
    return tuple(int(part) for part in text.split(",") if part)


def _common() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    week = common.add_mutually_exclusive_group()
    week.add_argument("--weekend", type=_weekend, help="days off, Monday=0 (default: 5,6)")
    week.add_argument("--weekmask", help='working days, "1111100" or "Sun Mon Tue Wed Thu"')
    common.add_argument(
        "--holidays", type=Path, action="append", default=[], help="file of ISO dates, one per line"
    )
    common.add_argument("--holiday", type=_day, action="append", default=[], help="one ISO date")
    return common


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="busdays", description="Business-day arithmetic.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")
    common = [_common()]
    add = commands.add_parser("add", parents=common, help="add N business days to DATE")
    add.add_argument("date", type=_day)
    add.add_argument("n", type=_count)
    add.add_argument("--roll", type=_roll, help="roll DATE first (following, preceding, ...)")
    count = commands.add_parser("count", parents=common, help="count business days in [A, B)")
    count.add_argument("a", type=_day)
    count.add_argument("b", type=_day)
    adjust = commands.add_parser("roll", parents=common, help="move DATE to a business day")
    adjust.add_argument("date", type=_day)
    adjust.add_argument("convention", type=_roll, nargs="?", default=Roll.FOLLOWING)
    check = commands.add_parser("is", parents=common, help="exit 0 if DATE is a business day")
    check.add_argument("date", type=_day)
    listing = commands.add_parser("list", parents=common, help="list business days in [A, B)")
    listing.add_argument("a", type=_day)
    listing.add_argument("b", type=_day)
    return parser


def _read_holidays(paths: Sequence[Path]) -> list[date]:
    found: list[date] = []
    for path in paths:
        text = sys.stdin.read() if str(path) == "-" else path.read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), 1):
            entry = line.split("#", 1)[0].strip()
            if entry:
                try:
                    found.append(_day(entry))
                except argparse.ArgumentTypeError as error:
                    raise ValueError(f"{path}:{number}: {error}") from None
    return found


def _calendar(args: argparse.Namespace) -> Calendar:
    holidays = [*args.holiday, *_read_holidays(args.holidays)]
    if args.weekmask is not None:
        return Calendar.from_weekmask(args.weekmask, holidays)
    return Calendar((5, 6) if args.weekend is None else args.weekend, holidays)


def _run(args: argparse.Namespace) -> int:
    calendar = _calendar(args)
    if args.command == "add":
        print(calendar.add_business_days(args.date, args.n, roll=args.roll))
    elif args.command == "count":
        print(calendar.business_days_between(args.a, args.b))
    elif args.command == "roll":
        print(calendar.roll(args.date, args.convention))
    elif args.command == "is":
        working = calendar.is_business_day(args.date)
        print("yes" if working else "no")
        return 0 if working else 1
    else:
        for day in calendar.business_days(args.a, args.b):
            print(day)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for ``busdays`` and ``python -m busdays``; returns the exit code."""
    parser = _parser()
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    try:
        return _run(args)
    except (ValueError, OverflowError, OSError) as error:
        print(f"busdays: error: {error}", file=sys.stderr)
        return 2
