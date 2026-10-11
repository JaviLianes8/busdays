"""Business-day arithmetic over a configurable weekend and holiday set."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date, timedelta

_ONE_DAY = timedelta(days=1)
_ALL_WEEKDAYS = frozenset(range(7))

DEFAULT_WEEKEND = (5, 6)


def _normalize_weekend(weekend: Iterable[int]) -> frozenset[int]:
    days = frozenset(weekend)
    if not days <= _ALL_WEEKDAYS:
        raise ValueError("weekend days must be integers in range 0 (Monday) to 6 (Sunday)")
    return days


def _normalize_holidays(holidays: Iterable[date] | None) -> frozenset[date]:
    return frozenset(holidays) if holidays is not None else frozenset()


def _is_business_day(day: date, weekend: frozenset[int], holidays: frozenset[date]) -> bool:
    return day.weekday() not in weekend and day not in holidays


def is_business_day(
    day: date,
    *,
    weekend: Iterable[int] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
) -> bool:
    """Return whether ``day`` is a working day given the weekend and holidays."""
    return _is_business_day(day, _normalize_weekend(weekend), _normalize_holidays(holidays))


def add_business_days(
    start: date,
    n: int,
    *,
    weekend: Iterable[int] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
) -> date:
    """Return the date ``n`` business days from ``start``.

    ``start`` need not be a business day. ``n`` may be negative to move backwards
    and ``0`` returns ``start`` unchanged. Only the days actually landed on are
    counted, so each result is itself a business day whenever ``n`` is non-zero.
    """
    if n == 0:
        return start
    weekend_days = _normalize_weekend(weekend)
    if weekend_days == _ALL_WEEKDAYS:
        raise ValueError("weekend covers every day; no business day exists")
    holiday_set = _normalize_holidays(holidays)
    step = _ONE_DAY if n > 0 else -_ONE_DAY
    remaining = abs(n)
    current = start
    while remaining:
        current += step
        if _is_business_day(current, weekend_days, holiday_set):
            remaining -= 1
    return current


def business_days_between(
    a: date,
    b: date,
    *,
    weekend: Iterable[int] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
) -> int:
    """Count business days in the half-open interval ``[a, b)``.

    ``a`` is included and ``b`` is excluded. The result is negative when ``b``
    precedes ``a`` and ``0`` when the dates are equal.
    """
    if a == b:
        return 0
    weekend_days = _normalize_weekend(weekend)
    holiday_set = _normalize_holidays(holidays)
    (low, high, sign) = (a, b, 1) if b > a else (b, a, -1)
    count = 0
    current = low
    while current < high:
        if _is_business_day(current, weekend_days, holiday_set):
            count += 1
        current += _ONE_DAY
    return sign * count


def next_business_day(
    day: date,
    *,
    weekend: Iterable[int] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
) -> date:
    """Return the first business day strictly after ``day``."""
    return add_business_days(day, 1, weekend=weekend, holidays=holidays)


def prev_business_day(
    day: date,
    *,
    weekend: Iterable[int] = DEFAULT_WEEKEND,
    holidays: Iterable[date] | None = None,
) -> date:
    """Return the last business day strictly before ``day``."""
    return add_business_days(day, -1, weekend=weekend, holidays=holidays)
