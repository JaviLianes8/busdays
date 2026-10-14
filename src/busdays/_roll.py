"""Business day conventions: how a date that is not a business day is moved."""

from __future__ import annotations

from datetime import date
from enum import Enum

from busdays._kernel import MAX_ORDINAL, MIN_ORDINAL, Kernel

# numpy spells two of the modes differently; both spellings are accepted.
_ALIASES = {"forward": "following", "backward": "preceding"}


class Roll(str, Enum):
    """A business day convention, named as in numpy where numpy has it.

    ``Roll("modified_following")``, ``Roll("ModifiedFollowing")`` and numpy's
    ``"forward"`` and ``"backward"`` are all accepted.
    """

    FOLLOWING = "following"
    PRECEDING = "preceding"
    MODIFIED_FOLLOWING = "modifiedfollowing"
    MODIFIED_PRECEDING = "modifiedpreceding"
    HALF_MONTH_MODIFIED_FOLLOWING = "halfmonthmodifiedfollowing"
    NEAREST = "nearest"
    UNADJUSTED = "unadjusted"
    RAISE = "raise"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def _missing_(cls, value: object) -> Roll | None:
        if not isinstance(value, str):
            return None
        key = "".join(char for char in value.lower() if char not in "_- ")
        key = _ALIASES.get(key, key)
        return next((member for member in cls if member.value == key), None)


def parse_roll(value: Roll | str) -> Roll:
    if not isinstance(value, str):
        raise TypeError(f"roll must be a Roll or a string, not {type(value).__name__}")
    try:
        return Roll(value)
    except ValueError:
        names = ", ".join(member.value for member in Roll)
        raise ValueError(f"unknown roll {value!r}; expected one of {names}") from None


def _month(ordinal: int) -> tuple[int, int] | None:
    if not MIN_ORDINAL <= ordinal <= MAX_ORDINAL:
        return None
    day = date.fromordinal(ordinal)
    return (day.year, day.month)


def _day(ordinal: int) -> int:
    return date.fromordinal(ordinal).day


def adjust(kernel: Kernel, ordinal: int, roll: Roll) -> int:
    """Apply ``roll`` to ``ordinal``; a business day is returned unchanged."""
    if roll is Roll.UNADJUSTED or kernel.is_business(ordinal):
        return ordinal
    if roll is Roll.RAISE:
        raise ValueError(f"{date.fromordinal(ordinal)} is not a business day")
    if roll in (Roll.PRECEDING, Roll.MODIFIED_PRECEDING):
        earlier = kernel.preceding(ordinal)
        if roll is Roll.PRECEDING or _month(earlier) == _month(ordinal):
            return earlier
        return kernel.following(ordinal)
    later = kernel.following(ordinal)
    if roll is Roll.FOLLOWING:
        return later
    if roll is Roll.NEAREST:
        earlier = kernel.preceding(ordinal)
        # Ties go forward. A side that leaves the supported dates never wins.
        if later > MAX_ORDINAL or (earlier >= MIN_ORDINAL and ordinal - earlier < later - ordinal):
            return earlier
        return later
    same_month = _month(later) == _month(ordinal)
    if roll is Roll.HALF_MONTH_MODIFIED_FOLLOWING and same_month:
        same_month = not (_day(ordinal) <= 15 < _day(later))
    return later if same_month else kernel.preceding(ordinal)
