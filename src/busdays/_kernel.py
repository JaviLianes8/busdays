"""Counting over day ordinals: whole weeks by arithmetic, holidays by binary search."""

from __future__ import annotations

from bisect import bisect_left
from datetime import date

MIN_ORDINAL = 1
MAX_ORDINAL = date.max.toordinal()
NO_BUSINESS_DAY = "the weekend covers every day, so no business day exists"


def weekday(ordinal: int) -> int:
    # Ordinal 1 (0001-01-01) is a Monday.
    return (ordinal + 6) % 7


def to_date(ordinal: int) -> date:
    if not MIN_ORDINAL <= ordinal <= MAX_ORDINAL:
        raise OverflowError("the result falls outside the supported dates (years 1 to 9999)")
    return date.fromordinal(ordinal)


class Kernel:
    """Business-day counts in O(log holidays); the inverse in O(log(holidays) ** 2)."""

    __slots__ = ("holiday_set", "holidays", "mask", "per_week", "prefix", "slots")

    def __init__(self, mask: tuple[bool, ...], holidays: tuple[int, ...]) -> None:
        # ``holidays`` is sorted, unique and only holds working weekdays, so each one
        # removes exactly one day from the weekday count.
        self.mask = mask
        self.holidays = holidays
        self.holiday_set = frozenset(holidays)
        self.slots = tuple(day for day in range(7) if mask[day])
        self.per_week = len(self.slots)
        prefix = [0]
        for day in range(7):
            prefix.append(prefix[-1] + mask[day])
        self.prefix = tuple(prefix)

    def is_business(self, ordinal: int) -> bool:
        return self.mask[weekday(ordinal)] and ordinal not in self.holiday_set

    def before(self, ordinal: int) -> int:
        """Business days in ``[1, ordinal)``, extended below 1 so differences stay exact."""
        weeks, rest = divmod(ordinal - 1, 7)
        holidays = bisect_left(self.holidays, ordinal)
        return weeks * self.per_week + self.prefix[rest] - holidays

    def count(self, start: int, stop: int) -> int:
        return self.before(stop) - self.before(start)

    def _nth_weekday(self, index: int) -> int:
        weeks, rest = divmod(index - 1, self.per_week)
        return 7 * weeks + self.slots[rest] + 1

    def nth(self, index: int) -> int:
        """The business day ``x`` with ``before(x) == index - 1``."""
        if not self.per_week:
            raise ValueError(NO_BUSINESS_DAY)
        # Ignoring holidays gives a lower bound; at most len(holidays) more weekdays
        # are needed, which gives the upper bound.
        low = self._nth_weekday(index)
        high = self._nth_weekday(index + len(self.holidays))
        while low < high:
            middle = (low + high) // 2
            if self.before(middle + 1) >= index:
                high = middle
            else:
                low = middle + 1
        return low

    def following(self, ordinal: int) -> int:
        """First business day on or after ``ordinal``."""
        return self.nth(self.before(ordinal) + 1)

    def preceding(self, ordinal: int) -> int:
        """Last business day on or before ``ordinal``."""
        return self.nth(self.before(ordinal + 1))
