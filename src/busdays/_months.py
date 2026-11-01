"""Month endpoints and iteration over a prepared calendar."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from typing import SupportsIndex

from busdays._kernel import MAX_ORDINAL, Kernel
from busdays._validate import check_int


def iterate(kernel: Kernel, first: int, last: int) -> Iterator[date]:
    if not kernel.per_week or first >= last:
        return
    ordinal = kernel.following(first)
    while ordinal < last:
        yield date.fromordinal(ordinal)
        ordinal += 1
        while ordinal < last and not kernel.is_business(ordinal):
            ordinal += 1


def month_day(kernel: Kernel, year: SupportsIndex, month: SupportsIndex, *, last: bool) -> date:
    first = date(check_int(year, "year"), check_int(month, "month"), 1)
    if last:
        end = (
            first.replace(day=31).toordinal()
            if first.month == 12
            else first.replace(month=first.month + 1).toordinal() - 1
        )
        found = kernel.preceding(end)
    else:
        found = kernel.following(first.toordinal())
    if (
        not first.toordinal() <= found <= MAX_ORDINAL
        or date.fromordinal(found).month != first.month
    ):
        raise ValueError(f"{first.year:04d}-{first.month:02d} has no business day")
    return date.fromordinal(found)
