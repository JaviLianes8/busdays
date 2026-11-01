"""Public examples and stable call signatures."""

from __future__ import annotations

import doctest
import inspect
from datetime import date

import busdays


def test_every_public_docstring_has_a_passing_example() -> None:
    targets = [(name, getattr(busdays, name)) for name in busdays.__all__]
    for name in dir(busdays.Calendar):
        if not name.startswith("_"):
            value = getattr(busdays.Calendar, name)
            targets.append(
                (f"Calendar.{name}", value.fget if isinstance(value, property) else value)
            )
    finder = doctest.DocTestFinder(recurse=False)
    runner = doctest.DocTestRunner()
    namespace = {**vars(busdays), "date": date}
    for name, value in targets:
        tests = finder.find(value, name=name, globs=namespace)
        assert tests and tests[0].examples, name
        runner.run(tests[0])
    result = runner.summarize()
    assert result.failed == 0
    assert result.attempted >= 24


def test_standard_doctest_execution() -> None:
    result = doctest.testmod(busdays)
    assert result.failed == 0
    assert result.attempted > 0


def test_public_surface_has_no_accidental_imports() -> None:
    assert {name for name in vars(busdays) if not name.startswith("_")} == set(busdays.__all__)


def test_function_parameter_names_defaults_and_kinds_are_stable() -> None:
    leading = {
        "is_business_day": ["day"],
        "add_business_days": ["start", "n"],
        "business_days_between": ["a", "b"],
        "next_business_day": ["day"],
        "prev_business_day": ["day"],
        "roll": ["day", "convention"],
        "business_days": ["start", "stop"],
        "first_business_day": ["year", "month"],
        "last_business_day": ["year", "month"],
    }
    for name, positional in leading.items():
        params = inspect.signature(getattr(busdays, name)).parameters
        trailing = ["weekend", "holidays"] + (["roll"] if name == "add_business_days" else [])
        assert list(params) == positional + trailing
        for key in positional:
            assert params[key].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
            expected = busdays.Roll.FOLLOWING if key == "convention" else inspect.Parameter.empty
            assert params[key].default == expected
        for key in trailing:
            assert params[key].kind is inspect.Parameter.KEYWORD_ONLY
            assert params[key].default == ((5, 6) if key == "weekend" else None)


def test_calendar_properties_are_read_only() -> None:
    import pytest

    calendar = busdays.Calendar()
    for name in ("weekend", "weekmask", "holidays"):
        with pytest.raises(AttributeError):
            setattr(calendar, name, ())
