"""Business-day arithmetic with a configurable weekend mask and an optional holiday set."""

from __future__ import annotations

from busdays._core import (
    add_business_days,
    business_days_between,
    is_business_day,
    next_business_day,
    prev_business_day,
)

__version__ = "0.1.0"

__all__ = [
    "add_business_days",
    "business_days_between",
    "is_business_day",
    "next_business_day",
    "prev_business_day",
]
