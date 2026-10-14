"""Real holiday calendars: the GOV.UK bank holidays for the three UK jurisdictions.

Dates come from https://www.gov.uk/bank-holidays.json (fetched 2026-10-14, pinned in
data/upstream/MANIFEST.json, not committed). The expected answers in the hand-labelled
tests are worked out by hand from a 2026 wall calendar.
"""

from __future__ import annotations

import json
from datetime import date, timedelta

import pytest
from conftest import UPSTREAM, needs

from busdays import Calendar, Roll

np = pytest.importorskip("numpy")
DATASET = "uk-bank-holidays.json"


def _calendars() -> dict[str, list[date]]:
    data = json.loads((UPSTREAM / DATASET).read_text(encoding="utf-8"))
    return {
        region: [date.fromisoformat(event["date"]) for event in body["events"]]
        for region, body in data.items()
    }


@needs(DATASET)
def test_the_dataset_covers_the_three_jurisdictions() -> None:
    regions = _calendars()
    assert sorted(regions) == ["england-and-wales", "northern-ireland", "scotland"]
    assert all(len(days) > 50 for days in regions.values())


@needs(DATASET)
@pytest.mark.parametrize("region", ["england-and-wales", "scotland", "northern-ireland"])
def test_every_year_and_settlement_matches_numpy(region: str) -> None:
    holidays = _calendars()[region]
    calendar = Calendar(holidays=holidays)
    numpy_calendar = np.busdaycalendar(holidays=holidays)
    for year in range(holidays[0].year, holidays[-1].year + 1):
        start, stop = date(year, 1, 1), date(year + 1, 1, 1)
        expected = int(np.busday_count(start, stop, busdaycal=numpy_calendar))
        assert calendar.business_days_between(start, stop) == expected, year
    day = holidays[0] - timedelta(days=10)
    while day <= holidays[-1]:
        for mode in ("following", "modifiedfollowing", "preceding"):
            got = calendar.add_business_days(day, 2, roll=mode)
            want = np.busday_offset(day, 2, roll=mode, busdaycal=numpy_calendar).astype(object)
            assert got == want, (day, mode)
        day += timedelta(days=1)


@needs(DATASET)
def test_easter_2026_differs_between_england_and_scotland() -> None:
    regions = _calendars()
    england = Calendar(holidays=regions["england-and-wales"])
    scotland = Calendar(holidays=regions["scotland"])
    maundy_thursday = date(2026, 4, 2)
    # Good Friday is off in both; Easter Monday only in England and Wales.
    assert england.next_business_day(maundy_thursday) == date(2026, 4, 7)
    assert scotland.next_business_day(maundy_thursday) == date(2026, 4, 6)
    assert england.business_days_between(date(2026, 4, 1), date(2026, 4, 30)) == 19
    assert scotland.business_days_between(date(2026, 4, 1), date(2026, 4, 30)) == 20


@needs(DATASET)
def test_christmas_2026_settlement_in_england() -> None:
    england = Calendar(holidays=_calendars()["england-and-wales"])
    # Christmas is a Friday; Boxing Day falls on Saturday and is moved to Monday 28th.
    assert england.add_business_days(date(2026, 12, 24), 2) == date(2026, 12, 30)
    assert england.roll(date(2026, 12, 26), Roll.MODIFIED_FOLLOWING) == date(2026, 12, 29)
    assert england.roll(date(2026, 12, 26), Roll.PRECEDING) == date(2026, 12, 24)
    assert england.last_business_day(2026, 12) == date(2026, 12, 31)
    assert england.business_days_between(date(2026, 1, 1), date(2027, 1, 1)) == 253


def test_a_friday_and_saturday_weekend() -> None:
    # Hand-labelled: a Sunday to Thursday working week, as in several Gulf states.
    gulf = Calendar.from_weekmask("Sun Mon Tue Wed Thu")
    assert gulf.weekend == (4, 5)
    thursday = date(2026, 1, 1)
    assert gulf.next_business_day(thursday) == date(2026, 1, 4)
    assert gulf.prev_business_day(date(2026, 1, 4)) == thursday
    assert gulf.roll(date(2026, 1, 30), Roll.MODIFIED_FOLLOWING) == date(2026, 1, 29)
    assert gulf.business_days_between(date(2026, 1, 1), date(2026, 2, 1)) == 21
