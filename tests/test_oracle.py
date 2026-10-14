"""numpy's busday functions as an independent oracle; numpy is a test-only dependency.

numpy reads a reversed range as ``(end, begin]`` while this library keeps counts
antisymmetric, so reversed counts are compared through that identity instead.
"""

from __future__ import annotations

import random
from datetime import date, timedelta

import pytest

from busdays import Calendar

np = pytest.importorskip("numpy")

MODES = ("following", "preceding", "modifiedfollowing", "modifiedpreceding", "raise")


def _case(seed: int) -> tuple[Calendar, object, date, random.Random]:
    rng = random.Random(seed)
    mask = [int(rng.random() < 0.6) for _ in range(7)]
    if not any(mask):
        mask[rng.randrange(7)] = 1
    base = date(1900, 1, 1) + timedelta(days=rng.randrange(80_000))
    # Dense holiday clusters make the month-boundary fallbacks and long runs likely.
    holidays = [base + timedelta(days=rng.randrange(-90, 90)) for _ in range(rng.randrange(80))]
    calendar = Calendar.from_weekmask(mask, holidays)
    numpy_calendar = np.busdaycalendar(weekmask=mask, holidays=holidays)
    return calendar, numpy_calendar, base, rng


def _np_date(value: object) -> date:
    result = value.astype(object)  # type: ignore[attr-defined]
    assert isinstance(result, date)
    return result


@pytest.mark.parametrize("seed", range(300))
def test_offsets_counts_and_flags_match_numpy(seed: int) -> None:
    calendar, numpy_calendar, base, rng = _case(seed)
    for _ in range(20):
        day = base + timedelta(days=rng.randrange(-120, 120))
        n = rng.choice([0, 1, -1, rng.randrange(-400, 400)])
        assert calendar.is_business_day(day) == np.is_busday(day, busdaycal=numpy_calendar)
        for mode in MODES:
            try:
                expected = _np_date(np.busday_offset(day, n, roll=mode, busdaycal=numpy_calendar))
            except ValueError:
                with pytest.raises(ValueError):
                    calendar.add_business_days(day, n, roll=mode)
                continue
            assert calendar.add_business_days(day, n, roll=mode) == expected, (day, n, mode)
        if n:
            # Without a roll, a forward step reads as numpy's backward roll and vice versa.
            mode = "backward" if n > 0 else "forward"
            expected = _np_date(np.busday_offset(day, n, roll=mode, busdaycal=numpy_calendar))
            assert calendar.add_business_days(day, n) == expected, (day, n)
        stop = day + timedelta(days=rng.randrange(0, 900))
        count = int(np.busday_count(day, stop, busdaycal=numpy_calendar))
        assert calendar.business_days_between(day, stop) == count
        assert calendar.business_days_between(stop, day) == -count
        listed = list(calendar.business_days(day, stop))
        assert len(listed) == count
        assert all(np.is_busday(listed, busdaycal=numpy_calendar))


@pytest.mark.parametrize("seed", range(40))
def test_month_helpers_match_numpy(seed: int) -> None:
    calendar, numpy_calendar, base, _ = _case(seed)
    month = np.datetime64(f"{base.year:04d}-{base.month:02d}")
    try:
        first = _np_date(np.busday_offset(month, 0, roll="forward", busdaycal=numpy_calendar))
        last = _np_date(
            np.busday_offset(
                month + np.timedelta64(1, "M"), -1, roll="forward", busdaycal=numpy_calendar
            )
        )
    except ValueError:
        return
    if first.month == base.month:
        assert calendar.first_business_day(base.year, base.month) == first
    if last.month == base.month:
        assert calendar.last_business_day(base.year, base.month) == last


def test_numpy_documented_examples() -> None:
    # The examples on the numpy busday_offset and busday_count pages (fetched 2026-10-14,
    # URLs in data/upstream/MANIFEST.json), restated through this API.
    week = Calendar()
    assert week.first_business_day(2011, 10) == date(2011, 10, 3)
    assert week.last_business_day(2012, 2) == date(2012, 2, 29)
    assert Calendar.from_weekmask("Wed").add_business_days(
        date(2011, 1, 1), 2, roll="forward"
    ) == date(2011, 1, 19)
    assert Calendar.from_weekmask("Sun").add_business_days(
        date(2012, 5, 1), 1, roll="forward"
    ) == date(2012, 5, 13)
    assert week.roll(date(2011, 3, 20)) == date(2011, 3, 21)
    assert week.business_days_between(date(2011, 1, 1), date(2011, 2, 1)) == 21
    assert week.business_days_between(date(2011, 1, 1), date(2012, 1, 1)) == 260
    saturdays = Calendar.from_weekmask("Sat")
    assert saturdays.business_days_between(date(2011, 1, 1), date(2012, 1, 1)) == 53
    july = Calendar(holidays=[date(2011, 7, 1), date(2011, 7, 4), date(2011, 7, 17)])
    assert july.holidays == (date(2011, 7, 1), date(2011, 7, 4))


def test_numpy_reads_a_reversed_range_differently() -> None:
    # numpy counts busday_count(Sat, Mon) over (Mon, Sat]: Tuesday to Friday.
    saturday, monday = date(2026, 1, 10), date(2026, 1, 5)
    assert int(np.busday_count(saturday, monday)) == -4
    assert Calendar().business_days_between(saturday, monday) == -5
