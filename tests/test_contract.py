from __future__ import annotations

import importlib.resources
from datetime import date

import busdays

# The public API. Add every exported name here as the library grows; this list is the
# contract and the test below fails if the module and this list disagree.
PUBLIC_API: list[str] = [
    "Calendar",
    "Roll",
    "add_business_days",
    "business_days",
    "business_days_between",
    "first_business_day",
    "is_business_day",
    "last_business_day",
    "next_business_day",
    "prev_business_day",
    "roll",
]


def test_all_lists_exactly_the_public_api() -> None:
    assert sorted(busdays.__all__) == sorted(PUBLIC_API)


def test_every_exported_name_resolves() -> None:
    for name in busdays.__all__:
        assert hasattr(busdays, name)


def test_version_is_a_three_part_string() -> None:
    parts = busdays.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_the_package_ships_type_information() -> None:
    assert importlib.resources.files("busdays").joinpath("py.typed").is_file()


def test_module_functions_mirror_the_calendar_methods() -> None:
    functions = [name for name in PUBLIC_API if name[0].islower()]
    for name in functions:
        assert callable(getattr(busdays.Calendar, name)), name
    holidays = [date(2026, 1, day) for day in (1, 4, 29)]
    weekend = (4, 5)
    calendar = busdays.Calendar(weekend, holidays)
    first, stop = date(2026, 1, 1), date(2026, 1, 8)
    cases: list[tuple[str, tuple[object, ...], object]] = [
        ("is_business_day", (first,), False),
        ("add_business_days", (first, 1), date(2026, 1, 5)),
        ("business_days_between", (first, stop), 3),
        ("next_business_day", (first,), date(2026, 1, 5)),
        ("prev_business_day", (date(2026, 1, 5),), date(2025, 12, 31)),
        ("roll", (date(2026, 1, 4),), date(2026, 1, 5)),
        ("first_business_day", (2026, 1), date(2026, 1, 5)),
        ("last_business_day", (2026, 1), date(2026, 1, 28)),
    ]
    for name, args, expected in cases:
        assert getattr(busdays, name)(*args, weekend=weekend, holidays=holidays) == expected
        assert getattr(calendar, name)(*args) == expected
    expected_days = [date(2026, 1, day) for day in (5, 6, 7)]
    assert (
        list(busdays.business_days(first, stop, weekend=weekend, holidays=holidays))
        == expected_days
    )
    assert list(calendar.business_days(first, stop)) == expected_days
