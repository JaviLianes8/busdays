"""Module-level functions: each builds a ``Calendar`` from ``weekend`` and ``holidays``."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from datetime import date
from typing import SupportsIndex

from busdays._calendar import DEFAULT_WEEKEND, Calendar
from busdays._roll import Roll


def is_business_day(
    day: date,
    *,
    weekend: Iterable[SupportsIndex] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
) -> bool:
    """Return whether ``day`` is a working day given the weekend and holidays.

    >>> is_business_day(date(2026, 1, 3))
    False
    """
    return Calendar(weekend, holidays).is_business_day(day)


def add_business_days(
    start: date,
    n: SupportsIndex,
    *,
    weekend: Iterable[SupportsIndex] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
    roll: Roll | str | None = None,
) -> date:
    """Return the date ``n`` business days from ``start``; see ``Calendar.add_business_days``.

    >>> add_business_days(date(2026, 1, 2), 1)
    datetime.date(2026, 1, 5)
    """
    return Calendar(weekend, holidays).add_business_days(start, n, roll=roll)


def business_days_between(
    a: date,
    b: date,
    *,
    weekend: Iterable[SupportsIndex] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
) -> int:
    """Count business days in the half-open interval ``[a, b)``; negative when ``b < a``.

    >>> business_days_between(date(2026, 1, 5), date(2026, 1, 12))
    5
    """
    return Calendar(weekend, holidays).business_days_between(a, b)


def next_business_day(
    day: date,
    *,
    weekend: Iterable[SupportsIndex] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
) -> date:
    """Return the first business day strictly after ``day``.

    >>> next_business_day(date(2026, 1, 2))
    datetime.date(2026, 1, 5)
    """
    return Calendar(weekend, holidays).next_business_day(day)


def prev_business_day(
    day: date,
    *,
    weekend: Iterable[SupportsIndex] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
) -> date:
    """Return the last business day strictly before ``day``.

    >>> prev_business_day(date(2026, 1, 5))
    datetime.date(2026, 1, 2)
    """
    return Calendar(weekend, holidays).prev_business_day(day)


def roll(
    day: date,
    convention: Roll | str = Roll.FOLLOWING,
    *,
    weekend: Iterable[SupportsIndex] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
) -> date:
    """Move ``day`` to a business day by ``convention``; a business day stays put.

    >>> roll(date(2026, 1, 31), "modifiedfollowing")
    datetime.date(2026, 1, 30)
    """
    return Calendar(weekend, holidays).roll(day, convention)


def business_days(
    start: date,
    stop: date,
    *,
    weekend: Iterable[SupportsIndex] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
) -> Iterator[date]:
    """Yield the business days in ``[start, stop)`` in order.

    >>> list(business_days(date(2026, 1, 2), date(2026, 1, 5)))
    [datetime.date(2026, 1, 2)]
    """
    return Calendar(weekend, holidays).business_days(start, stop)


def first_business_day(
    year: SupportsIndex,
    month: SupportsIndex,
    *,
    weekend: Iterable[SupportsIndex] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
) -> date:
    """Return the first business day of the month.

    >>> first_business_day(2026, 2)
    datetime.date(2026, 2, 2)
    """
    return Calendar(weekend, holidays).first_business_day(year, month)


def last_business_day(
    year: SupportsIndex,
    month: SupportsIndex,
    *,
    weekend: Iterable[SupportsIndex] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
) -> date:
    """Return the last business day of the month.

    >>> last_business_day(2026, 1)
    datetime.date(2026, 1, 30)
    """
    return Calendar(weekend, holidays).last_business_day(year, month)
