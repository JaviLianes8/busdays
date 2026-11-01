# busdays guide

Import the supported API from `busdays`. Python 3.10 or newer is required.
The package has no runtime dependencies and supplies no regional holiday calendar.

## Calendar and functions

`Calendar(weekend=(5, 6), holidays=None)` consumes its inputs once. Weekdays use
Monday=0 through Sunday=6; duplicates are merged. Holidays on weekend days are
discarded. The `weekend`, `weekmask` and `holidays` properties are read-only,
normalized values. Calendars compare and hash by their working weekdays and holidays.
Private attributes are implementation details and must not be changed.

`Calendar.from_weekmask(weekmask, holidays=None)` accepts seven binary characters,
three-letter English day names (case insensitive, with optional whitespace between
names), or seven integer/bool flags. Empty names are invalid. `"0000000"` is valid.

Every function below also exists as a `Calendar` method. Module functions accept
keyword-only `weekend` and `holidays` and build a calendar per call.

| Function | Contract |
| --- | --- |
| `is_business_day(day)` | True exactly when the weekday works and the date is not a holiday. |
| `add_business_days(start, n, *, roll=None)` | Counts landed business days, excluding the starting date. Zero returns the start. An explicit roll adjusts first, then counts. |
| `business_days_between(a, b)` | Counts `[a, b)`. Reversing the dates negates the forward count. |
| `next_business_day(day)` | First business day strictly after the date. |
| `prev_business_day(day)` | Last business day strictly before the date. |
| `roll(day, convention=Roll.FOLLOWING)` | Adjusts a nonbusiness date by a convention. |
| `business_days(start, stop)` | Iterator over `[start, stop)` in increasing order; empty if stop is not after start. Validates dates before returning the iterator. |
| `first_business_day(year, month)` | First business day within the month. |
| `last_business_day(year, month)` | Last business day within the month. |

```python
from datetime import date
from busdays import Calendar

calendar = Calendar(holidays=[date(2026, 1, 5)])
assert calendar.next_business_day(date(2026, 1, 2)) == date(2026, 1, 6)
assert calendar.business_days_between(date(2026, 1, 2), date(2026, 1, 7)) == 2
assert list(calendar.business_days(date(2026, 1, 7), date(2026, 1, 2))) == []
```

## Roll conventions

`Roll` is a string enumeration. Its values are also accepted directly as strings.
Case, spaces, hyphens and underscores are ignored. `forward` means `following` and
`backward` means `preceding`. Unknown values, including `nat`, raise `ValueError`.

| Member | Adjustment of a nonbusiness date |
| --- | --- |
| `FOLLOWING` | Next business date, including the input if already working. |
| `PRECEDING` | Previous business date. |
| `MODIFIED_FOLLOWING` | Following unless it leaves the month, then preceding. |
| `MODIFIED_PRECEDING` | Preceding unless it leaves the month, then following. |
| `HALF_MONTH_MODIFIED_FOLLOWING` | Following unless it leaves the month or crosses from day 15 or earlier to after day 15, then preceding. |
| `NEAREST` | Closest business date; ties go forward. A date beyond years 1 to 9999 never wins. |
| `UNADJUSTED` | Return the input, even if it is not a business day. |
| `RAISE` | Raise `ValueError` unless the input is a business day. |

The modified conventions can leave the month on their fallback when that entire
month has no business days. Explicit `roll="unadjusted"` with a nonbusiness starting
date permits only offset zero. An intermediate rolled ordinal may leave the supported
range if the final offset brings the result back into range.

## Types and errors

Dates must be `datetime.date`; `datetime.datetime` is rejected. Integer arguments
(counts, weekday numbers, years and months) accept `SupportsIndex`, including NumPy
integers. Booleans are rejected except as weekmask flags. Weekmask sequences accept
seven 0/1 values or bools, including NumPy integer and boolean arrays at runtime.
User-defined iterators and conversion methods are responsible for their own behavior;
exceptions they raise can propagate.

| Exception | When raised |
| --- | --- |
| `TypeError` | Incorrect date or integer type, a string used as a weekend, incorrect holiday container, or a nonstring roll argument to a function. |
| `ValueError` | Bad weekday number, malformed weekmask, unknown `Roll` value, impossible year/month, a month without business days, or a convention that refuses the input. |
| `OverflowError` | The result is outside years 1 to 9999, or a year/month integer exceeds the platform date constructor's integer range. |

An all-weekend calendar can answer membership (false), counts (zero), iteration
(empty), zero offsets and unadjusted rolls. Operations that must find a business day
raise `ValueError`. Library validation messages omit arbitrary input values.
Exact message text is not a compatibility promise.

Building a calendar costs O(H log H) for H holidays. Membership uses a set lookup;
counts use two binary searches; offsets use O(log(H+1)) binary-search probes, each
costing O(log(H+1)). Calendar iteration costs time proportional to the dates traversed.
The date distance does not determine the number of offset probes.

## CLI

Run `busdays --help` or `python -m busdays --help`. Commands are `add`, `count`, `roll`,
`is` and `list`. Dates must use `YYYY-MM-DD`; signed offsets use ASCII decimal digits.
Each command accepts `--weekend`, `--weekmask`, repeated `--holiday` dates and repeated
`--holidays` files. Weekend and weekmask options are mutually exclusive.

Holiday files are UTF-8, optionally beginning with a byte order mark, with one ISO date
per line. Blank lines and text after `#` are ignored. `--holidays -` reads stdin once.
Errors report a line number without echoing the file path or invalid contents.
Exit status is 0 for success, 1 for `is` on a nonbusiness day or a closed output pipe,
and 2 for invalid input. A closed pipe replaces stdout with an in-memory sink before
returning; an embedded caller should restore its stream before invoking the CLI again.

## Upgrading from 0.2.0

The eleven exported names and argument names/defaults remain stable. Date results
are preserved except for the two month-helper corrections below. Integer-like
arguments now have matching type annotations. Month helpers now
compare the normalized integer month, so an object implementing only `__index__`
works consistently. The first-day helper also rejects closed months whose next
working date is in the same month of a later year. Diagnostic text omits invalid
values and file paths. Huge CLI counts fail with a bounded message; arbitrarily many
leading zeros remain valid.
Class metadata and new pickles use the public `busdays` module; existing 0.2.0
calendar pickles still load. The accidental top-level `annotations` attribute is
removed. Source distributions contain only library code and consumer documentation;
tests and source-fetch tools remain in the GitHub repository.

## References and development

The tests compare actual output from
[NumPy business-day functions](https://numpy.org/doc/stable/reference/generated/numpy.busday_offset.html),
read definitions from
[QuantLib](https://github.com/lballabio/QuantLib/blob/master/ql/time/businessdayconvention.hpp),
and use the live [GOV.UK holiday dataset](https://www.gov.uk/bank-holidays.json).
NumPy's reversed counts have a different endpoint rule; busdays deliberately keeps
antisymmetry. Its all-zero weekmask is also allowed here but refused by NumPy.

Install `.[dev]` and run `scripts/check.ps1`. Set `BUSDAYS_UPSTREAM` to a scratch
directory and run `python scripts/fetch_upstream.py` for the pinned reference copies;
`--accept-new` explicitly refreshes their hashes. Tests skip when copies are absent
and fail when present copies do not match the manifest. Run `pytest -m e2e` for wheel,
sdist and PyPI upgrade checks. Set TEMP, TMP and pytest's `--basetemp` to scratch
locations when isolating development artifacts.

See the [CHANGELOG](https://github.com/JaviLianes8/busdays/blob/main/CHANGELOG.md).
