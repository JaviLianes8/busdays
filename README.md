# busdays

[![Lianes8 Certified](https://lianes8studio.com/certified/lianes8-certified-badge.svg)](https://lianes8studio.com/certified)

Zero-dependency business-day arithmetic with a configurable weekend mask and optional
holidays: offsets, counts, roll conventions and month helpers.

## Install

```
pip install busdays
```

## Usage

```python
from datetime import date

from busdays import (
    Calendar,
    Roll,
    add_business_days,
    business_days_between,
    is_business_day,
    next_business_day,
    prev_business_day,
)

friday = date(2026, 1, 2)

add_business_days(friday, 1)  # -> date(2026, 1, 5)
add_business_days(friday, -1)  # -> date(2026, 1, 1)
next_business_day(friday)  # -> date(2026, 1, 5)
prev_business_day(date(2026, 1, 5))  # -> date(2026, 1, 2)
is_business_day(date(2026, 1, 3))  # -> False

# You bring the holidays. Here a Monday holiday is skipped.
add_business_days(friday, 1, holidays={date(2026, 1, 5)})  # -> date(2026, 1, 6)

# Count business days in the half-open interval [a, b).
business_days_between(date(2026, 1, 5), date(2026, 1, 12))  # -> 5
business_days_between(date(2026, 1, 12), date(2026, 1, 5))  # -> -5

# Weekdays are integers, Monday is 0. A Friday and Saturday weekend:
add_business_days(date(2026, 1, 1), 1, weekend=(4, 5))  # -> date(2026, 1, 4)
```

### A calendar, built once

A `Calendar` checks and sorts the weekend and holidays once; after that, counts and
offsets take logarithmic time, so a million business days cost the same as one. The
module-level functions build a calendar on every call, which costs O(H log H) for H
holidays: build a `Calendar` yourself when you ask many questions of the same holidays.
`business_days()` yields one date at a time, so it costs time in the number of days
it covers. Holidays on a
weekend day are dropped and duplicates merged, as `numpy.busdaycalendar` does.

```python
holidays = [date(2026, 12, 25), date(2026, 12, 26), date(2026, 12, 28)]
uk = Calendar(holidays=holidays)
uk.holidays  # -> (date(2026, 12, 25), date(2026, 12, 28))
uk.add_business_days(date(2026, 12, 24), 2)  # -> date(2026, 12, 30)
uk.last_business_day(2026, 12)  # -> date(2026, 12, 31)
uk.first_business_day(2026, 2)  # -> date(2026, 2, 2)
days = uk.business_days(date(2026, 12, 24), date(2026, 12, 31))
[d.day for d in days]  # -> [24, 29, 30]
Calendar().add_business_days(date(2026, 1, 5), 1_000_000)  # -> date(5859, 1, 31)

# numpy style weekmasks: seven 0/1 characters, day names (any case) or seven flags.
gulf = Calendar.from_weekmask("Sun Mon Tue Wed Thu")
gulf.weekend  # -> (4, 5)
gulf.weekmask  # -> '1111001'
```

### Roll conventions

`roll` moves a date that is not a business day; a business day is never moved. The conventions include following, modified following, preceding, modified preceding,
half-month modified following, nearest and unadjusted, as defined by
[QuantLib](https://github.com/lballabio/QuantLib/blob/master/ql/time/businessdayconvention.hpp),
plus `raise`. Names are forgiving: `"modified_following"`, `"ModifiedFollowing"` and
numpy's `"forward"` and `"backward"` all work. numpy's `"nat"` has no `date`
equivalent and is refused.

```python
saturday = date(2026, 1, 31)
uk.roll(saturday)  # -> date(2026, 2, 2)
uk.roll(saturday, Roll.MODIFIED_FOLLOWING)  # -> date(2026, 1, 30)
uk.roll(saturday, "preceding")  # -> date(2026, 1, 30)
uk.roll(date(2026, 2, 14), Roll.HALF_MONTH_MODIFIED_FOLLOWING)  # -> date(2026, 2, 13)
uk.roll(date(2026, 1, 4), Roll.NEAREST)  # -> date(2026, 1, 5)
Roll("forward")  # -> Roll.FOLLOWING

# With roll=, the start is adjusted first and n is counted from it, as numpy does.
uk.add_business_days(saturday, 0, roll="following")  # -> date(2026, 2, 2)
uk.add_business_days(saturday, 1, roll="modifiedfollowing")  # -> date(2026, 2, 2)
```

### Conventions and errors

- Weekday integers follow `date.weekday()`: Monday is `0`, Sunday is `6`, and the default
  weekend is `(5, 6)`.
- Without `roll`, `add_business_days` counts only the days it lands on: the start need
  not be a business day, `0` returns the start unchanged, and any other count lands on a
  business day. That is numpy's `backward` roll for forward steps and `forward` roll for
  backward steps.
- `business_days_between(a, b)` counts `[a, b)` and is antisymmetric: swapping the dates
  negates the count. numpy counts a reversed range as `(b, a]` instead, so the two
  differ when `a` or `b` is not a business day.
- Dates must be `datetime.date`; a `datetime` is refused (`TypeError`) because it never
  equals a `date` holiday. Counts and weekdays must be integers, not `bool` or `float`.
- A result before year 1 or after year 9999 raises `OverflowError`. A weekend covering
  all seven days raises `ValueError` whenever a business day has to be found.

## Command line

```
busdays add 2026-01-02 1                      # 2026-01-05
busdays add 2026-01-31 0 --roll modifiedfollowing
busdays count 2026-01-05 2026-01-12           # 5
busdays roll 2026-01-31 preceding             # 2026-01-30
busdays is 2026-01-03                         # prints "no", exits 1
busdays list 2026-12-01 2026-12-31 --holidays uk.txt
busdays add 2026-01-01 1 --weekmask "Sun Mon Tue Wed Thu"
```

Every command takes `--weekend 5,6` or `--weekmask 1111100`, `--holiday DATE` (repeat
it) and `--holidays FILE` (one ISO date per line, `#` comments allowed, `-` for standard
input). Bad input exits with status 2. `python -m busdays` works too.

## Why

Use busdays when your application already supplies its holidays and needs scalar
`datetime.date` arithmetic without runtime dependencies. NumPy's
[`busday_offset`](https://numpy.org/doc/stable/reference/generated/numpy.busday_offset.html)
and [`busday_count`](https://numpy.org/doc/stable/reference/generated/numpy.busday_count.html)
are a better fit when you already use NumPy arrays or need vectorized operations.
Busdays keeps counts antisymmetric, supports nearest and half-month roll conventions,
and includes a command line interface. It does not discover regional holidays for you.

## Documentation

The [GUIDE](https://github.com/JaviLianes8/busdays/blob/main/GUIDE.md) describes every
contract, error and roll convention. The
[CHANGELOG](https://github.com/JaviLianes8/busdays/blob/main/CHANGELOG.md) records release
changes, including the upgrade from 0.2.0.

## License

MIT. See [LICENSE](https://github.com/JaviLianes8/busdays/blob/main/LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
