"""The Calendar object: construction, normalisation, identity and month helpers."""

from __future__ import annotations

from datetime import date

import pytest

from busdays import Calendar, first_business_day, last_business_day

NEW_YEAR = date(2026, 1, 1)  # a Thursday
SATURDAY = date(2026, 1, 3)


def test_default_weekend_is_saturday_and_sunday() -> None:
    calendar = Calendar()
    assert calendar.weekend == (5, 6)
    assert calendar.weekmask == "1111100"
    assert calendar.holidays == ()


def test_weekend_holidays_are_dropped_and_duplicates_merged() -> None:
    calendar = Calendar(holidays=[date(2026, 1, 2), SATURDAY, NEW_YEAR, date(2026, 1, 2)])
    assert calendar.holidays == (NEW_YEAR, date(2026, 1, 2))


def test_a_generator_of_holidays_is_read_once() -> None:
    calendar = Calendar(holidays=(date(2026, 1, day) for day in (2, 1)))
    assert calendar.holidays == (NEW_YEAR, date(2026, 1, 2))


@pytest.mark.parametrize(
    ("mask", "weekend"),
    [
        ("1111100", (5, 6)),
        ("1111001", (4, 5)),
        ("Mon Tue Wed Thu Fri", (5, 6)),
        ("SunMonTueWedThu", (4, 5)),
        ("  sun mon tue  wed thu ", (4, 5)),
        ("Sun", (0, 1, 2, 3, 4, 5)),
        ([1, 1, 1, 1, 1, 0, 0], (5, 6)),
        ((True, False, True, False, True, False, True), (1, 3, 5)),
        ("0000000", (0, 1, 2, 3, 4, 5, 6)),
    ],
)
def test_from_weekmask_reads_every_numpy_form(mask: object, weekend: tuple[int, ...]) -> None:
    calendar = Calendar.from_weekmask(mask)  # type: ignore[arg-type]
    assert calendar.weekend == weekend


@pytest.mark.parametrize(
    "mask", ["111110", "11111000", "1111102", "Mon Tue Wednesday", "Mo Tu", "", "   ", "Mon,Tue"]
)
def test_from_weekmask_rejects_malformed_strings(mask: str) -> None:
    with pytest.raises(ValueError):
        Calendar.from_weekmask(mask)


@pytest.mark.parametrize("mask", [[1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 0, 2], [1.0] * 7])
def test_from_weekmask_rejects_malformed_sequences(mask: list[object]) -> None:
    with pytest.raises(ValueError):
        Calendar.from_weekmask(mask)  # type: ignore[arg-type]


def test_from_weekmask_keeps_the_holidays() -> None:
    calendar = Calendar.from_weekmask("1111100", [date(2026, 1, 2)])
    assert calendar == Calendar(holidays=[date(2026, 1, 2)])


def test_equal_calendars_hash_alike_and_differ_from_others() -> None:
    first = Calendar((6, 5), [NEW_YEAR, SATURDAY])
    second = Calendar([5, 6, 6], [NEW_YEAR])
    assert first == second and hash(first) == hash(second)
    assert first != Calendar((5, 6))
    assert first != Calendar((4, 5), [NEW_YEAR])
    assert first != "Calendar"
    assert len({first, second}) == 1


def test_the_hash_covers_the_holidays() -> None:
    assert hash(Calendar(holidays=[NEW_YEAR])) != hash(Calendar(holidays=[date(2026, 1, 2)]))


def test_repr_round_trips() -> None:
    calendar = Calendar((4, 5), [NEW_YEAR])
    assert repr(calendar) == "Calendar(weekend=(4, 5), holidays=(datetime.date(2026, 1, 1),))"
    assert eval(repr(calendar), {"Calendar": Calendar, "datetime": __import__("datetime")}) == (
        calendar
    )


def test_calendar_is_immutable() -> None:
    calendar = Calendar()
    with pytest.raises(AttributeError):
        calendar.extra = 1  # type: ignore[attr-defined]


def test_first_and_last_business_day_of_a_month() -> None:
    assert first_business_day(2026, 1) == NEW_YEAR
    assert first_business_day(2026, 1, holidays=[NEW_YEAR]) == date(2026, 1, 2)
    assert first_business_day(2026, 2) == date(2026, 2, 2)
    assert last_business_day(2026, 1) == date(2026, 1, 30)
    assert last_business_day(2026, 2) == date(2026, 2, 27)
    assert last_business_day(2024, 2, weekend=(4, 5)) == date(2024, 2, 29)
    assert last_business_day(2026, 12) == date(2026, 12, 31)
    assert first_business_day(2027, 5) == date(2027, 5, 3)


def test_first_and_last_business_day_at_the_ends_of_the_calendar() -> None:
    assert first_business_day(1, 1) == date(1, 1, 1)
    assert last_business_day(9999, 12) == date(9999, 12, 31)
    assert last_business_day(9999, 12, weekend=(4,)) == date(9999, 12, 30)


def test_a_month_without_business_days_is_an_error() -> None:
    february = [date(2026, 2, day) for day in range(1, 29)]
    with pytest.raises(ValueError, match="2026-02 has no business day"):
        first_business_day(2026, 2, holidays=february)
    with pytest.raises(ValueError, match="2026-02 has no business day"):
        last_business_day(2026, 2, holidays=february)
    december = [date(9999, 12, day) for day in range(1, 32)]
    with pytest.raises(ValueError, match="9999-12 has no business day"):
        first_business_day(9999, 12, holidays=december)


def test_a_month_of_holidays_after_a_working_day_has_no_business_day() -> None:
    # Every day works, so the day before 1 February is a business day of January.
    february = [date(2026, 2, day) for day in range(1, 29)]
    with pytest.raises(ValueError, match="2026-02 has no business day"):
        last_business_day(2026, 2, weekend=(), holidays=february)


@pytest.mark.parametrize(("year", "month"), [(2026, 13), (2026, 0), (0, 1), (10000, 1)])
def test_month_helpers_reject_impossible_months(year: int, month: int) -> None:
    with pytest.raises(ValueError):
        first_business_day(year, month)
    with pytest.raises(ValueError):
        last_business_day(year, month)


def test_month_helpers_reject_non_integers() -> None:
    with pytest.raises(TypeError):
        first_business_day(2026, True)
    with pytest.raises(TypeError):
        last_business_day(2026.0, 1)  # type: ignore[arg-type]
