"""The ``Calendar``: a weekend and a holiday set, checked once and reused."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from datetime import date

from busdays._kernel import MAX_ORDINAL, Kernel, to_date
from busdays._roll import Roll, adjust, parse_roll
from busdays._validate import (
    check_date,
    check_int,
    holiday_ordinals,
    parse_weekmask,
    weekend_mask,
)

DEFAULT_WEEKEND = (5, 6)


class Calendar:
    """An immutable business-day calendar: which weekdays are off, and which dates.

    Holidays that fall on a weekend day are dropped and duplicates merged, as
    ``numpy.busdaycalendar`` does. Counts take O(log holidays) time and offsets
    O(log(holidays) ** 2), however far apart the dates are.
    """

    __slots__ = ("_kernel",)

    def __init__(
        self, weekend: Iterable[int] = DEFAULT_WEEKEND, holidays: Iterable[date] | None = None
    ) -> None:
        mask = weekend_mask(weekend)
        self._kernel = Kernel(mask, holiday_ordinals(holidays, mask))

    @classmethod
    def from_weekmask(
        cls, weekmask: str | Sequence[bool | int], holidays: Iterable[date] | None = None
    ) -> Calendar:
        """Build from a numpy weekmask: ``"1111100"``, ``"Sun Mon Tue Wed Thu"`` or 7 flags."""
        mask = parse_weekmask(weekmask)
        return cls([day for day in range(7) if not mask[day]], holidays)

    @property
    def weekend(self) -> tuple[int, ...]:
        """The weekday numbers that are days off, Monday being 0."""
        return tuple(day for day in range(7) if not self._kernel.mask[day])

    @property
    def weekmask(self) -> str:
        """The working weekdays as seven ``0``/``1`` characters, Monday first."""
        return "".join("1" if working else "0" for working in self._kernel.mask)

    @property
    def holidays(self) -> tuple[date, ...]:
        """The holidays that fall on working weekdays, sorted and without duplicates."""
        return tuple(date.fromordinal(ordinal) for ordinal in self._kernel.holidays)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Calendar):
            return NotImplemented
        return (self._kernel.mask, self._kernel.holidays) == (
            other._kernel.mask,
            other._kernel.holidays,
        )

    def __hash__(self) -> int:
        return hash((self._kernel.mask, self._kernel.holidays))

    def __repr__(self) -> str:
        return f"Calendar(weekend={self.weekend!r}, holidays={self.holidays!r})"

    def is_business_day(self, day: date) -> bool:
        """Return whether ``day`` is neither a weekend day nor a holiday."""
        return self._kernel.is_business(check_date(day, "day").toordinal())

    def add_business_days(self, start: date, n: int, *, roll: Roll | str | None = None) -> date:
        """Return the date ``n`` business days from ``start``.

        Without ``roll``, only the days landed on are counted: ``start`` need not be a
        business day, ``0`` returns it unchanged and any other ``n`` lands on a business
        day. With ``roll``, ``start`` is first adjusted by that convention and ``n`` is
        then counted from it, as ``numpy.busday_offset`` does.
        """
        ordinal = check_date(start, "start").toordinal()
        steps = check_int(n, "n")
        kernel = self._kernel
        if roll is not None:
            rolled = adjust(kernel, ordinal, parse_roll(roll))
            if steps == 0:
                return to_date(rolled)
            if not kernel.is_business(rolled):
                raise ValueError(
                    "the unadjusted start is not a business day, so there is nothing to count from"
                )
            return to_date(kernel.nth(kernel.before(rolled) + 1 + steps))
        if steps == 0:
            return start
        if steps > 0:
            return to_date(kernel.nth(kernel.before(ordinal + 1) + steps))
        return to_date(kernel.nth(kernel.before(ordinal) + steps + 1))

    def business_days_between(self, a: date, b: date) -> int:
        """Count business days in the half-open interval ``[a, b)``.

        The count is antisymmetric: swapping the dates negates it.
        """
        start = check_date(a, "a").toordinal()
        return self._kernel.count(start, check_date(b, "b").toordinal())

    def next_business_day(self, day: date) -> date:
        """Return the first business day strictly after ``day``."""
        return self.add_business_days(day, 1)

    def prev_business_day(self, day: date) -> date:
        """Return the last business day strictly before ``day``."""
        return self.add_business_days(day, -1)

    def roll(self, day: date, convention: Roll | str = Roll.FOLLOWING) -> date:
        """Move ``day`` to a business day by ``convention``; a business day stays put."""
        ordinal = check_date(day, "day").toordinal()
        return to_date(adjust(self._kernel, ordinal, parse_roll(convention)))

    def business_days(self, start: date, stop: date) -> Iterator[date]:
        """Yield the business days in ``[start, stop)`` in order; nothing if ``stop <= start``."""
        first = check_date(start, "start").toordinal()
        last = check_date(stop, "stop").toordinal()
        return self._iterate(first, last)

    def _iterate(self, first: int, last: int) -> Iterator[date]:
        kernel = self._kernel
        if not kernel.per_week:
            return
        ordinal = kernel.following(first)
        while ordinal < last:
            yield date.fromordinal(ordinal)
            ordinal = ordinal + 1
            while ordinal < last and not kernel.is_business(ordinal):
                ordinal += 1

    def first_business_day(self, year: int, month: int) -> date:
        """Return the first business day of the month; ``ValueError`` if it has none."""
        first = date(check_int(year, "year"), check_int(month, "month"), 1).toordinal()
        found = self._kernel.following(first)
        if found > MAX_ORDINAL or date.fromordinal(found).month != month:
            raise ValueError(f"{year:04d}-{month:02d} has no business day")
        return date.fromordinal(found)

    def last_business_day(self, year: int, month: int) -> date:
        """Return the last business day of the month; ``ValueError`` if it has none."""
        first = date(check_int(year, "year"), check_int(month, "month"), 1)
        found = self._kernel.preceding(_month_end(first))
        if found < first.toordinal():
            raise ValueError(f"{year:04d}-{month:02d} has no business day")
        return date.fromordinal(found)


def _month_end(first: date) -> int:
    if first.month == 12:
        return first.replace(day=31).toordinal()
    return first.replace(month=first.month + 1).toordinal() - 1
