"""Argument checks shared by the calendar, the module functions and the command line."""

from __future__ import annotations

import operator
import re
from collections.abc import Iterable, Sequence
from datetime import date, datetime

DAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
_NAME_RUN = re.compile(r"\s*([A-Za-z]{3})\s*")


def check_date(value: object, name: str) -> date:
    # A datetime is a date subclass that never compares equal to a plain date, so a
    # datetime holiday would silently never match: refuse it instead.
    if not isinstance(value, date) or isinstance(value, datetime):
        raise TypeError(f"{name} must be a datetime.date, not {type(value).__name__}")
    return value


def check_int(value: object, name: str) -> int:
    if isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, not bool")
    try:
        return operator.index(value)  # type: ignore[arg-type]
    except TypeError:
        raise TypeError(f"{name} must be an integer, not {type(value).__name__}") from None


def weekend_mask(weekend: Iterable[int]) -> tuple[bool, ...]:
    """Working-day mask, Monday first, from the weekday numbers that are days off."""
    if isinstance(weekend, (str, bytes)):
        raise TypeError("weekend must be weekday numbers; use Calendar.from_weekmask for a string")
    off = set()
    for day in weekend:
        number = check_int(day, "a weekend day")
        if not 0 <= number <= 6:
            raise ValueError("weekend days must be integers in range 0 (Monday) to 6 (Sunday)")
        off.add(number)
    return tuple(day not in off for day in range(7))


def parse_weekmask(weekmask: str | Sequence[bool | int]) -> tuple[bool, ...]:
    """Working-day mask from numpy's weekmask forms: "1111100", "Mon Tue", or seven flags."""
    if isinstance(weekmask, str):
        if re.fullmatch(r"[01]{7}", weekmask):
            return tuple(char == "1" for char in weekmask)
        return _parse_day_names(weekmask)
    flags = list(weekmask)
    if len(flags) != 7 or any(not isinstance(flag, int) or flag not in (0, 1) for flag in flags):
        raise ValueError("a weekmask sequence must hold seven 0/1 or bool values, Monday first")
    return tuple(bool(flag) for flag in flags)


def _parse_day_names(text: str) -> tuple[bool, ...]:
    days: set[int] = set()
    position = 0
    while position < len(text):
        match = _NAME_RUN.match(text, position)
        name = match.group(1).capitalize() if match else ""
        if match is None or name not in DAY_NAMES:
            raise ValueError(f"invalid weekmask {text!r}: use 7 digits or names like 'Mon Tue'")
        days.add(DAY_NAMES.index(name))
        position = match.end()
    if not days:
        raise ValueError(f"invalid weekmask {text!r}: it names no day")
    return tuple(day in days for day in range(7))


def holiday_ordinals(holidays: Iterable[date] | None, mask: tuple[bool, ...]) -> tuple[int, ...]:
    """Sorted unique ordinals of the holidays that fall on a working weekday."""
    if holidays is None:
        return ()
    if isinstance(holidays, (str, bytes, date)):
        raise TypeError("holidays must be an iterable of datetime.date values")
    found = set()
    for day in holidays:
        ordinal = check_date(day, "a holiday").toordinal()
        if mask[(ordinal + 6) % 7]:
            found.add(ordinal)
    return tuple(sorted(found))
