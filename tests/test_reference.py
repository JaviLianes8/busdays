"""A day-by-day reference, written by hand from the convention definitions, as a property test.

It covers what the numpy oracle cannot: nearest and half-month modified following, and
dates next to year 1 and year 9999 where numpy's own range is not the question.
"""

from __future__ import annotations

import contextlib
import random
from datetime import date, timedelta

import pytest

from busdays import Calendar, Roll

FIRST, LAST = date.min, date.max


def _step(calendar: Calendar, day: date, direction: int) -> date | None:
    while True:
        if (direction > 0 and day == LAST) or (direction < 0 and day == FIRST):
            return None
        day += timedelta(days=direction)
        if calendar.is_business_day(day):
            return day


def _reference(calendar: Calendar, day: date, roll: Roll) -> date | None:
    if roll is Roll.UNADJUSTED or calendar.is_business_day(day):
        return day
    later, earlier = _step(calendar, day, 1), _step(calendar, day, -1)

    def month(other: date | None) -> bool:
        return other is not None and (other.year, other.month) == (day.year, day.month)

    if roll is Roll.FOLLOWING:
        return later
    if roll is Roll.PRECEDING:
        return earlier
    if roll is Roll.MODIFIED_FOLLOWING:
        return later if month(later) else earlier
    if roll is Roll.MODIFIED_PRECEDING:
        return earlier if month(earlier) else later
    if roll is Roll.HALF_MONTH_MODIFIED_FOLLOWING:
        keep = month(later) and not (later is not None and day.day <= 15 < later.day)
        return later if keep else earlier
    if later is None or earlier is None:
        return earlier if later is None else later
    return later if (later - day) <= (day - earlier) else earlier


def _calendar(rng: random.Random, around: date) -> Calendar:
    mask = [int(rng.random() < 0.5) for _ in range(7)]
    if not any(mask):
        mask[rng.randrange(7)] = 1
    holidays: set[date] = set()
    for _ in range(rng.randrange(40)):
        # A holiday outside the supported dates cannot exist.
        with contextlib.suppress(OverflowError):
            holidays.add(around + timedelta(days=rng.randrange(-60, 60)))
    return Calendar.from_weekmask(mask, holidays)


@pytest.mark.parametrize("seed", range(150))
def test_every_convention_matches_the_reference(seed: int) -> None:
    rng = random.Random(seed)
    around = rng.choice(
        [FIRST + timedelta(days=rng.randrange(20)), LAST - timedelta(days=rng.randrange(20))]
        + [date(2000, 1, 1) + timedelta(days=rng.randrange(20_000))] * 2
    )
    calendar = _calendar(rng, around)
    for _ in range(25):
        shift = rng.randrange(-40, 40)
        try:
            day = around + timedelta(days=shift)
        except OverflowError:
            continue
        for roll in Roll:
            if roll is Roll.RAISE:
                continue
            expected = _reference(calendar, day, roll)
            if expected is None:
                with pytest.raises(OverflowError):
                    calendar.roll(day, roll)
            else:
                assert calendar.roll(day, roll) == expected, (day, roll)


def test_an_offset_counts_from_the_rolled_start_even_past_the_last_date() -> None:
    # Friday 9999-12-31 rolls forward past the last date, yet one business day back
    # from that rolled start is Thursday, as numpy answers. With n == 0 the rolled
    # start itself is the result, which does not exist.
    friday_off = Calendar((4, 5, 6))
    assert friday_off.add_business_days(LAST, -1, roll="following") == date(9999, 12, 30)
    with pytest.raises(OverflowError):
        friday_off.add_business_days(LAST, 0, roll="following")
