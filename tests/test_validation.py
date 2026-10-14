"""What the API refuses, and how it fails at the ends of the supported dates."""

from __future__ import annotations

from datetime import date, datetime

import numpy as np
import pytest

from busdays import (
    Calendar,
    add_business_days,
    business_days,
    business_days_between,
    is_business_day,
    next_business_day,
    prev_business_day,
)

MON = date(2026, 1, 5)


@pytest.mark.parametrize("weekend", [(True,), (5, False), (5.0,), ("5",), (-1,), (7,), "56", b"5"])
def test_bad_weekends_are_rejected(weekend: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        Calendar(weekend)  # type: ignore[arg-type]


def test_bool_weekend_days_are_type_errors_not_weekdays() -> None:
    with pytest.raises(TypeError, match="not bool"):
        is_business_day(MON, weekend=(True,))


def test_a_weekend_string_points_at_from_weekmask() -> None:
    with pytest.raises(TypeError, match="from_weekmask"):
        Calendar("1111100")  # type: ignore[arg-type]


def test_integer_like_weekend_days_and_counts_are_accepted() -> None:
    assert Calendar((np.int64(5), np.int64(6))) == Calendar()
    assert add_business_days(MON, np.int32(5)) == date(2026, 1, 12)


@pytest.mark.parametrize("n", [1.0, True, "1", None])
def test_counts_must_be_integers(n: object) -> None:
    with pytest.raises(TypeError, match="n must be an integer"):
        add_business_days(MON, n)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [datetime(2026, 1, 5), "2026-01-05", 20260105, None])
def test_dates_must_be_plain_dates(value: object) -> None:
    calls = [
        lambda: is_business_day(value),  # type: ignore[arg-type]
        lambda: add_business_days(value, 1),  # type: ignore[arg-type]
        lambda: add_business_days(value, 0),  # type: ignore[arg-type]
        lambda: business_days_between(value, MON),  # type: ignore[arg-type]
        lambda: business_days_between(MON, value),  # type: ignore[arg-type]
        lambda: next_business_day(value),  # type: ignore[arg-type]
        lambda: list(business_days(MON, value)),  # type: ignore[arg-type]
    ]
    for call in calls:
        with pytest.raises(TypeError):
            call()


@pytest.mark.parametrize("holidays", [[datetime(2026, 1, 5)], ["2026-01-05"], "2026-01-05", MON])
def test_holidays_must_be_an_iterable_of_plain_dates(holidays: object) -> None:
    with pytest.raises(TypeError):
        Calendar(holidays=holidays)  # type: ignore[arg-type]


def test_a_full_weekend_still_answers_questions_that_need_no_business_day() -> None:
    everything = Calendar(range(7))
    assert everything.is_business_day(MON) is False
    assert everything.business_days_between(MON, date(2027, 1, 1)) == 0
    assert list(everything.business_days(MON, date(2027, 1, 1))) == []
    assert everything.add_business_days(MON, 0) == MON


def test_a_full_weekend_cannot_find_a_business_day() -> None:
    everything = Calendar(range(7))
    for call in (
        lambda: everything.add_business_days(MON, 1),
        lambda: everything.add_business_days(MON, -1),
        lambda: everything.roll(MON),
        lambda: everything.first_business_day(2026, 1),
    ):
        with pytest.raises(ValueError, match="no business day exists"):
            call()


def test_stepping_past_the_last_date_is_an_overflow_error() -> None:
    with pytest.raises(OverflowError, match="years 1 to 9999"):
        next_business_day(date(9999, 12, 31))
    with pytest.raises(OverflowError, match="years 1 to 9999"):
        prev_business_day(date(1, 1, 1))
    with pytest.raises(OverflowError):
        add_business_days(MON, 10**12)
    with pytest.raises(OverflowError):
        add_business_days(MON, -(10**12))


def test_the_last_and_first_dates_are_reachable() -> None:
    assert add_business_days(date(9999, 12, 30), 1) == date(9999, 12, 31)
    assert add_business_days(date(1, 1, 2), -1) == date(1, 1, 1)
    # [0001-01-01, 9999-12-31) is 3_652_058 days from a Monday: 521_722 weeks and 4 days.
    assert business_days_between(date(1, 1, 1), date(9999, 12, 31)) == 2_608_614
    assert business_days_between(date(9999, 12, 31), date(1, 1, 1)) == -2_608_614
