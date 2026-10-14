"""Business-day arithmetic with a configurable weekend mask and an optional holiday set."""

from __future__ import annotations

from busdays._calendar import Calendar
from busdays._core import (
    add_business_days,
    business_days,
    business_days_between,
    first_business_day,
    is_business_day,
    last_business_day,
    next_business_day,
    prev_business_day,
    roll,
)
from busdays._roll import Roll

__version__ = "0.2.0"

__all__ = [
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
