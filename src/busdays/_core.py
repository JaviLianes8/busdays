"""Module-level functions: each builds a ``Calendar`` from ``weekend`` and ``holidays``."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from datetime import date

from busdays._calendar import DEFAULT_WEEKEND, Calendar
from busdays._roll import Roll


def is_business_day(
    day: date, *, weekend: Iterable[int] = DEFAULT_WEEKEND, holidays: Iterable[date] | None = None
) -> bool:
    """Return whether ``day`` is a working day given the weekend and holidays."""
    return Calendar(weekend, holidays).is_business_day(day)


def add_business_days(
    start: date,
    n: int,
    *,
    weekend: Iterable[int] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
    roll: Roll | str | None = None,
) -> date:
    """Return the date ``n`` business days from ``start``; see ``Calendar.add_business_days``."""
    return Calendar(weekend, holidays).add_business_days(start, n, roll=roll)


def business_days_between(
    a: date,
    b: date,
    *,
    weekend: Iterable[int] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
) -> int:
    """Count business days in the half-open interval ``[a, b)``; negative when ``b < a``."""
    return Calendar(weekend, holidays).business_days_between(a, b)


def next_business_day(
    day: date, *, weekend: Iterable[int] = DEFAULT_WEEKEND, holidays: Iterable[date] | None = None
) -> date:
    """Return the first business day strictly after ``day``."""
    return Calendar(weekend, holidays).next_business_day(day)


def prev_business_day(
    day: date, *, weekend: Iterable[int] = DEFAULT_WEEKEND, holidays: Iterable[date] | None = None
) -> date:
    """Return the last business day strictly before ``day``."""
    return Calendar(weekend, holidays).prev_business_day(day)


def roll(
    day: date,
    convention: Roll | str = Roll.FOLLOWING,
    *,
    weekend: Iterable[int] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
) -> date:
    """Move ``day`` to a business day by ``convention``; a business day stays put."""
    return Calendar(weekend, holidays).roll(day, convention)


def business_days(
    start: date,
    stop: date,
    *,
    weekend: Iterable[int] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
) -> Iterator[date]:
    """Yield the business days in ``[start, stop)`` in order."""
    return Calendar(weekend, holidays).business_days(start, stop)


def first_business_day(
    year: int,
    month: int,
    *,
    weekend: Iterable[int] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
) -> date:
    """Return the first business day of the month."""
    return Calendar(weekend, holidays).first_business_day(year, month)


def last_business_day(
    year: int,
    month: int,
    *,
    weekend: Iterable[int] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
) -> date:
    """Return the last business day of the month."""
    return Calendar(weekend, holidays).last_business_day(year, month)
