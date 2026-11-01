"""Roll normalization uses string contents regardless of subclass overrides."""

from __future__ import annotations

from collections.abc import Iterator
from typing import SupportsIndex

import pytest

from busdays import Roll

_NAMES = [
    ("following", Roll.FOLLOWING),
    ("Forward", Roll.FOLLOWING),
    ("Modified_Following", Roll.MODIFIED_FOLLOWING),
]


@pytest.mark.parametrize(("name", "expected"), _NAMES)
@pytest.mark.parametrize("raises", [False, True], ids=["misleading", "raising"])
def test_roll_ignores_str_override(name: str, expected: Roll, raises: bool) -> None:
    class Name(str):
        def __str__(self) -> str:
            if raises:
                raise RuntimeError("string conversion must not run")
            return "preceding"

    assert Roll(Name(name)) is expected


@pytest.mark.parametrize(("name", "expected"), _NAMES)
@pytest.mark.parametrize("raises", [False, True], ids=["misleading", "raising"])
def test_roll_ignores_iter_override(name: str, expected: Roll, raises: bool) -> None:
    class Name(str):
        def __iter__(self) -> Iterator[str]:
            if raises:
                raise RuntimeError("string iteration must not run")
            return iter("preceding")

    assert Roll(Name(name)) is expected


@pytest.mark.parametrize(("name", "expected"), _NAMES)
@pytest.mark.parametrize("raises", [False, True], ids=["misleading", "raising"])
def test_roll_ignores_replace_override(name: str, expected: Roll, raises: bool) -> None:
    class Name(str):
        def replace(self, old: str, new: str, count: SupportsIndex = -1, /) -> str:
            if raises:
                raise RuntimeError("string replacement must not run")
            return "preceding"

    assert Roll(Name(name)) is expected
