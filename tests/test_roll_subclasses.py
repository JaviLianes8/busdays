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


@pytest.mark.parametrize(("name", "expected"), _NAMES)
@pytest.mark.parametrize("raises", [False, True], ids=["misleading", "raising"])
def test_roll_ignores_getitem_override(name: str, expected: Roll, raises: bool) -> None:
    class Name(str):
        def __getitem__(self, key: SupportsIndex | slice, /) -> str:
            if raises:
                raise RuntimeError("string slicing must not run")
            return "preceding"

    assert Roll(Name(name)) is expected


@pytest.mark.parametrize(("name", "expected"), _NAMES)
@pytest.mark.parametrize("raises", [False, True], ids=["misleading", "raising"])
def test_roll_ignores_strip_override(name: str, expected: Roll, raises: bool) -> None:
    class Name(str):
        def strip(self, chars: str | None = None, /) -> str:
            if raises:
                raise RuntimeError("string stripping must not run")
            return "preceding"

    assert Roll(Name(name)) is expected


@pytest.mark.parametrize(("name", "expected"), _NAMES)
@pytest.mark.parametrize("raises", [False, True], ids=["misleading", "raising"])
def test_roll_ignores_encode_override(name: str, expected: Roll, raises: bool) -> None:
    class Name(str):
        def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
            if raises:
                raise RuntimeError("string encoding must not run")
            return b"preceding"

    assert Roll(Name(name)) is expected


@pytest.mark.parametrize(("name", "expected"), _NAMES)
@pytest.mark.parametrize("raises", [False, True], ids=["misleading", "raising"])
def test_roll_ignores_format_override(name: str, expected: Roll, raises: bool) -> None:
    class Name(str):
        def __format__(self, format_spec: str, /) -> str:
            if raises:
                raise RuntimeError("string formatting must not run")
            return "preceding"

    assert Roll(Name(name)) is expected


@pytest.mark.parametrize(("name", "expected"), _NAMES)
@pytest.mark.parametrize("raises", [False, True], ids=["misleading", "raising"])
def test_roll_ignores_casefold_override(name: str, expected: Roll, raises: bool) -> None:
    class Name(str):
        def casefold(self) -> str:
            if raises:
                raise RuntimeError("string case folding must not run")
            return "preceding"

    assert Roll(Name(name)) is expected


@pytest.mark.parametrize(("name", "expected"), _NAMES)
@pytest.mark.parametrize("raises", [False, True], ids=["misleading", "raising"])
def test_roll_ignores_lstrip_override(name: str, expected: Roll, raises: bool) -> None:
    class Name(str):
        def lstrip(self, chars: str | None = None, /) -> str:
            if raises:
                raise RuntimeError("string left stripping must not run")
            return "preceding"

    assert Roll(Name(name)) is expected


@pytest.mark.parametrize(("name", "expected"), _NAMES)
@pytest.mark.parametrize("raises", [False, True], ids=["misleading", "raising"])
def test_roll_ignores_rstrip_override(name: str, expected: Roll, raises: bool) -> None:
    class Name(str):
        def rstrip(self, chars: str | None = None, /) -> str:
            if raises:
                raise RuntimeError("string right stripping must not run")
            return "preceding"

    assert Roll(Name(name)) is expected


@pytest.mark.parametrize(("name", "expected"), _NAMES)
@pytest.mark.parametrize("raises", [False, True], ids=["misleading", "raising"])
def test_roll_ignores_translate_override(name: str, expected: Roll, raises: bool) -> None:
    class Name(str):
        def translate(self, table: object, /) -> str:
            if raises:
                raise RuntimeError("string translation must not run")
            return "preceding"

    assert Roll(Name(name)) is expected
