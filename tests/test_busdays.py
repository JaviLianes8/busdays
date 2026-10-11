from datetime import date

import pytest

from busdays import (
    add_business_days,
    business_days_between,
    is_business_day,
    next_business_day,
    prev_business_day,
)

# Reference calendar: 2026-01-01 is a Thursday.
THU = date(2026, 1, 1)
FRI = date(2026, 1, 2)
SAT = date(2026, 1, 3)
SUN = date(2026, 1, 4)
MON = date(2026, 1, 5)
TUE = date(2026, 1, 6)
WED = date(2026, 1, 7)


def test_add_steps_over_the_weekend() -> None:
    assert add_business_days(FRI, 1) == MON


def test_add_counts_only_landed_business_days() -> None:
    assert add_business_days(THU, 2) == MON


def test_add_zero_returns_the_start_unchanged() -> None:
    assert add_business_days(SAT, 0) == SAT


def test_negative_n_moves_backwards() -> None:
    assert add_business_days(MON, -1) == FRI


def test_custom_weekend_skips_friday_and_saturday() -> None:
    assert add_business_days(THU, 1, weekend=(4, 5)) == SUN


def test_holidays_are_skipped() -> None:
    assert add_business_days(FRI, 1, holidays={MON}) == TUE


def test_between_counts_the_half_open_interval() -> None:
    assert business_days_between(MON, date(2026, 1, 12)) == 5


def test_between_is_negative_when_b_precedes_a() -> None:
    assert business_days_between(date(2026, 1, 12), MON) == -5


def test_between_is_zero_for_equal_dates() -> None:
    assert business_days_between(MON, MON) == 0


def test_between_excludes_holidays() -> None:
    assert business_days_between(MON, date(2026, 1, 12), holidays={WED}) == 4


def test_is_business_day_rejects_the_weekend() -> None:
    assert is_business_day(SAT) is False
    assert is_business_day(MON) is True


def test_is_business_day_rejects_a_holiday() -> None:
    assert is_business_day(MON, holidays={MON}) is False


def test_next_business_day_skips_the_weekend() -> None:
    assert next_business_day(FRI) == MON
    assert next_business_day(SAT) == MON


def test_prev_business_day_skips_the_weekend() -> None:
    assert prev_business_day(MON) == FRI


def test_weekend_day_out_of_range_is_rejected() -> None:
    with pytest.raises(ValueError):
        add_business_days(MON, 1, weekend=(5, 7))


def test_a_full_weekend_leaves_no_business_day() -> None:
    with pytest.raises(ValueError):
        add_business_days(MON, 1, weekend=range(7))
