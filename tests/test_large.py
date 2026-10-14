"""Far-apart dates cost a handful of binary-search steps, never a walk over the days."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from busdays import Calendar
from busdays._kernel import Kernel

START = date(2000, 1, 3)  # a Monday


@pytest.fixture
def probes(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    calls: list[int] = []
    original = Kernel.before

    def counted(self: Kernel, ordinal: int) -> int:
        calls.append(ordinal)
        return original(self, ordinal)

    monkeypatch.setattr(Kernel, "before", counted)
    return calls


def test_a_million_business_days_take_a_few_dozen_counts(probes: list[int]) -> None:
    # Five business days from a Monday land on the next Monday, so 1_000_000 is 200_000 weeks.
    result = Calendar().add_business_days(START, 1_000_000)
    assert result == START + timedelta(weeks=200_000)
    assert len(probes) <= 4


def test_offsets_with_many_holidays_stay_logarithmic(probes: list[int]) -> None:
    holidays = [START + timedelta(days=7 * k + 2) for k in range(5000)]  # every Wednesday
    calendar = Calendar(holidays=holidays)
    result = calendar.add_business_days(START, 100_000)
    assert len(probes) <= 2 * 16
    # Four working days a week while the holidays last, five afterwards.
    assert calendar.business_days_between(START, result + timedelta(days=1)) == 100_001
    assert calendar.is_business_day(result)


def test_counts_over_millennia_need_two_lookups(probes: list[int]) -> None:
    assert Calendar().business_days_between(date(1, 1, 1), date(9999, 12, 31)) == 2_608_614
    assert len(probes) == 2


def test_long_offsets_agree_with_a_day_by_day_walk() -> None:
    calendar = Calendar((4, 5), [START + timedelta(days=3 * k) for k in range(400)])
    for n in (1, 7, 365, 1000, -1, -7, -365, -1000):
        day, left, step = START, abs(n), 1 if n > 0 else -1
        while left:
            day += timedelta(days=step)
            left -= calendar.is_business_day(day)
        assert calendar.add_business_days(START, n) == day, n
