# busdays

Zero-dependency business-day arithmetic with a configurable weekend mask and optional holidays.

## Install

```
pip install busdays
```

## Usage

```python
from datetime import date

from busdays import (
    add_business_days,
    business_days_between,
    is_business_day,
    next_business_day,
    prev_business_day,
)

friday = date(2026, 1, 2)

add_business_days(friday, 1)                 # date(2026, 1, 5), the Monday
add_business_days(friday, -1)                # date(2026, 1, 1), moving backwards
next_business_day(friday)                    # date(2026, 1, 5)
prev_business_day(date(2026, 1, 5))          # date(2026, 1, 2)
is_business_day(date(2026, 1, 3))            # False, a Saturday

# You bring the holidays. Here New Year's Monday is skipped.
holidays = {date(2026, 1, 5)}
add_business_days(friday, 1, holidays=holidays)   # date(2026, 1, 6), the Tuesday

# Count business days in the half-open interval [a, b).
business_days_between(date(2026, 1, 5), date(2026, 1, 12))   # 5

# Weekdays are integers, Monday is 0. A Friday and Saturday weekend:
add_business_days(date(2026, 1, 1), 1, weekend=(4, 5))       # date(2026, 1, 4), the Sunday
```

Conventions: weekday integers follow `date.weekday()`, so Monday is `0` and Sunday
is `6`, and the default weekend is `(5, 6)`. `add_business_days` accepts a negative
count to move backwards and returns `start` unchanged for `0`; the start date need
not itself be a business day. `business_days_between(a, b)` counts the half-open
interval `[a, b)`, including `a`, excluding `b`, and is negative when `b` precedes `a`.

## Why

Business-day math keeps getting reinvented because the existing options pull their
weight the wrong way. `numpy.busday_offset` and `busday_count` require numpy for a
few lines of date math. `workalendar` and `python-holidays` are large and opinionated:
they ship their own regional calendars, which is the opposite of what you want when
the holidays come from your own database. `python-networkdays` only counts and lists
days and offers no "add N business days". This library is the small, pure primitive in
between: you pass the weekend mask and the holiday set, it does the arithmetic, and it
depends on nothing but the standard library.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
