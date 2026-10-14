"""Business day conventions on hand-labelled dates.

The convention definitions follow QuantLib's ``BusinessDayConvention`` and
``Calendar::adjust`` (https://github.com/lballabio/QuantLib, ql/time/, fetched 2026-10-14);
the dates and expected answers below are written by hand from those definitions.
"""

from __future__ import annotations

import re
from datetime import date

import pytest
from conftest import UPSTREAM, needs

from busdays import Calendar, Roll, add_business_days, roll

WEEK = Calendar()
SAT_JAN_31 = date(2026, 1, 31)  # following is Monday 2 February
SAT_FEB_14 = date(2026, 2, 14)  # following is Monday 16, past the 15th
SAT_AUG_1 = date(2026, 8, 1)  # preceding is Friday 31 July


@pytest.mark.parametrize(
    ("day", "convention", "expected"),
    [
        (SAT_JAN_31, Roll.FOLLOWING, date(2026, 2, 2)),
        (SAT_JAN_31, Roll.PRECEDING, date(2026, 1, 30)),
        (SAT_JAN_31, Roll.MODIFIED_FOLLOWING, date(2026, 1, 30)),
        (SAT_JAN_31, Roll.MODIFIED_PRECEDING, date(2026, 1, 30)),
        (SAT_JAN_31, Roll.HALF_MONTH_MODIFIED_FOLLOWING, date(2026, 1, 30)),
        (SAT_JAN_31, Roll.NEAREST, date(2026, 1, 30)),
        (SAT_JAN_31, Roll.UNADJUSTED, SAT_JAN_31),
        (SAT_AUG_1, Roll.PRECEDING, date(2026, 7, 31)),
        (SAT_AUG_1, Roll.MODIFIED_PRECEDING, date(2026, 8, 3)),
        (SAT_AUG_1, Roll.MODIFIED_FOLLOWING, date(2026, 8, 3)),
        (SAT_FEB_14, Roll.MODIFIED_FOLLOWING, date(2026, 2, 16)),
        (SAT_FEB_14, Roll.HALF_MONTH_MODIFIED_FOLLOWING, date(2026, 2, 13)),
        (date(2026, 2, 15), Roll.HALF_MONTH_MODIFIED_FOLLOWING, date(2026, 2, 13)),
        (date(2026, 3, 1), Roll.HALF_MONTH_MODIFIED_FOLLOWING, date(2026, 3, 2)),
        (date(2026, 1, 3), Roll.NEAREST, date(2026, 1, 2)),
        (date(2026, 1, 4), Roll.NEAREST, date(2026, 1, 5)),
    ],
)
def test_conventions_on_weekends(day: date, convention: Roll, expected: date) -> None:
    assert WEEK.roll(day, convention) == expected


def test_half_month_keeps_a_following_day_that_stays_after_the_15th() -> None:
    # Sunday the 16th rolls to Monday the 17th: it never crossed the 15th.
    assert WEEK.roll(date(2025, 11, 16), Roll.HALF_MONTH_MODIFIED_FOLLOWING) == date(2025, 11, 17)


def test_nearest_breaks_ties_forward() -> None:
    # A Wednesday holiday sits one day from Tuesday and one day from Thursday.
    holiday = Calendar(holidays=[date(2026, 1, 7)])
    assert holiday.roll(date(2026, 1, 7), Roll.NEAREST) == date(2026, 1, 8)


def test_a_business_day_is_never_moved() -> None:
    for convention in Roll:
        assert WEEK.roll(date(2026, 1, 7), convention) == date(2026, 1, 7)


def test_raise_rejects_a_non_business_day() -> None:
    with pytest.raises(ValueError, match="2026-01-03 is not a business day"):
        roll(date(2026, 1, 3), Roll.RAISE)


def test_default_convention_is_following() -> None:
    assert roll(SAT_JAN_31) == date(2026, 2, 2)


def test_modified_following_falls_back_even_when_preceding_leaves_the_month_too() -> None:
    # Every day of February 2026 but none of March is a holiday.
    february = Calendar(holidays=[date(2026, 2, day) for day in range(1, 29)])
    assert february.roll(date(2026, 2, 10), Roll.MODIFIED_FOLLOWING) == date(2026, 1, 30)
    assert february.roll(date(2026, 2, 10), Roll.MODIFIED_PRECEDING) == date(2026, 3, 2)


def test_conventions_at_the_ends_of_the_supported_dates() -> None:
    last = date(9999, 12, 31)  # a Friday
    friday_off = Calendar((4, 5, 6))
    assert friday_off.roll(last, Roll.MODIFIED_FOLLOWING) == date(9999, 12, 30)
    assert friday_off.roll(last, Roll.NEAREST) == date(9999, 12, 30)
    with pytest.raises(OverflowError):
        friday_off.roll(last, Roll.FOLLOWING)
    first = date(1, 1, 1)  # a Monday
    monday_off = Calendar((0, 5, 6))
    assert monday_off.roll(first, Roll.MODIFIED_PRECEDING) == date(1, 1, 2)
    assert monday_off.roll(first, Roll.NEAREST) == date(1, 1, 2)
    with pytest.raises(OverflowError):
        monday_off.roll(first, Roll.PRECEDING)


@pytest.mark.parametrize(
    ("text", "member"),
    [
        ("following", Roll.FOLLOWING),
        ("forward", Roll.FOLLOWING),
        ("backward", Roll.PRECEDING),
        ("modified_following", Roll.MODIFIED_FOLLOWING),
        ("ModifiedPreceding", Roll.MODIFIED_PRECEDING),
        ("half-month modified following", Roll.HALF_MONTH_MODIFIED_FOLLOWING),
        ("NEAREST", Roll.NEAREST),
    ],
)
def test_roll_names_are_forgiving(text: str, member: Roll) -> None:
    assert Roll(text) is member
    assert roll(SAT_JAN_31, text) == roll(SAT_JAN_31, member)


def test_roll_members_print_as_their_value() -> None:
    assert str(Roll.MODIFIED_FOLLOWING) == "modifiedfollowing"
    assert Roll.FOLLOWING == "following"


@pytest.mark.parametrize("bad", ["nat", "modified", "", "followingx"])
def test_unknown_roll_names_are_rejected(bad: str) -> None:
    with pytest.raises(ValueError, match="unknown roll"):
        roll(SAT_JAN_31, bad)


def test_a_non_string_roll_is_a_type_error() -> None:
    with pytest.raises(TypeError):
        roll(SAT_JAN_31, 1)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        add_business_days(SAT_JAN_31, 1, roll=1)  # type: ignore[arg-type]


def test_offset_with_a_roll_rolls_first_then_counts() -> None:
    assert add_business_days(SAT_JAN_31, 0, roll="following") == date(2026, 2, 2)
    assert add_business_days(SAT_JAN_31, 1, roll="following") == date(2026, 2, 3)
    assert add_business_days(SAT_JAN_31, 1, roll="preceding") == date(2026, 2, 2)
    assert add_business_days(SAT_JAN_31, -1, roll="modifiedfollowing") == date(2026, 1, 29)
    with pytest.raises(ValueError):
        add_business_days(SAT_JAN_31, 1, roll="raise")


def test_an_unadjusted_non_business_start_cannot_be_offset() -> None:
    assert add_business_days(SAT_JAN_31, 0, roll="unadjusted") == SAT_JAN_31
    with pytest.raises(ValueError, match="not a business day"):
        add_business_days(SAT_JAN_31, 2, roll="unadjusted")
    assert add_business_days(date(2026, 1, 30), 1, roll="unadjusted") == date(2026, 2, 2)


@needs("quantlib-businessdayconvention.hpp")
def test_every_quantlib_convention_has_a_member() -> None:
    raw = (UPSTREAM / "quantlib-businessdayconvention.hpp").read_text(encoding="utf-8")
    body = raw.split("enum BusinessDayConvention {", 1)[1].split("};", 1)[0]
    body = re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", body, flags=re.S))
    names = re.findall(r"[A-Za-z]+", body)
    assert len(names) == 7, names
    for name in names:
        assert Roll(name).value == name.lower()
