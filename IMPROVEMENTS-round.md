# busdays improvement round

Progress:
- [x] Brainstorm ranked improvements (this file)
- [x] Pin the ground truth: upstream copies in a local folder with a tracked manifest
- [x] `Calendar`: validated weekend and holidays, built once, O(log holidays) arithmetic
- [x] Roll conventions: following, preceding, modified, half-month, nearest, unadjusted, raise
- [x] Offsets with an explicit roll (numpy reading) next to the current counting reading
- [x] Ranges: iterate business days, count, first and last of a month
- [x] Strict validation: types, booleans, datetimes, weekmask strings, date range edges
- [x] Command line tool
- [x] Contracts: numpy oracle, QuantLib conventions, GOV.UK bank holidays, README examples
- [x] Docs and packaging: README, CHANGELOG, metadata, installed-wheel e2e test
- [x] Gates: ruff format, ruff check, mypy --strict, pytest
- [x] Mutation run: removing guarded logic makes the suite fail
- [x] Independent review findings fixed with regression tests
- [x] Pull request opened and checked

## Starting point

`0.1.0` (not on PyPI) gives `add_business_days`, `business_days_between`,
`is_business_day`, `next_business_day` and `prev_business_day`, each taking a `weekend`
tuple and an optional holiday iterable. Read as a user who settles trades, computes due
dates or plans payroll:

- Every call walks day by day: adding 250 000 business days or counting across a century
  costs one loop turn per calendar day, and the holiday set is rebuilt on each call.
- No roll conventions. Payment dates in a swap schedule, a bond coupon or an invoice due
  date are adjusted with following, modified following or preceding, and there is no way
  to ask for that. There is also no way to get numpy's "roll first, then offset".
- No reusable calendar object, so a weekend and holiday list must be passed to every call.
- Weak validation: `weekend=(True,)` reads as Tuesday, a float `n` loops forever or fails
  deep inside, a `datetime` holiday silently never matches a `date`, a holiday that is
  not a date is accepted, and stepping past year 9999 leaks the raw `OverflowError`.
- `weekend` must be integers: no numpy style weekmask (`"1111100"`, `"Mon Tue Wed"`).
- No iteration over business days, no "first or last business day of the month".
- No command line tool, no runnable README, no oracle, no installed-wheel test.

## Sources (fetched 2026-10-14)

- numpy reference pages for `busday_offset`, `busday_count`, `is_busday` and
  `busdaycalendar`, https://numpy.org/doc/stable/reference/generated/ (numpy 2.3 docs):
  roll first then offset; roll modes `raise`, `forward`/`following`,
  `backward`/`preceding`, `modifiedfollowing`, `modifiedpreceding`; weekmask as seven
  `0`/`1` characters or three-letter day names; holidays on non-working weekdays are
  dropped; counts are over a half-open range and negative when the end comes first.
- numpy 2.3 itself as a test-only oracle (never a runtime dependency).
- QuantLib `ql/time/businessdayconvention.hpp` and `ql/time/calendar.cpp`
  (https://github.com/lballabio/QuantLib, master): the ISDA conventions following,
  modified following and preceding, and the non-ISDA modified preceding, unadjusted,
  half-month modified following and nearest (ties go forward).
- GOV.UK bank holidays, https://www.gov.uk/bank-holidays.json: real holiday calendars for
  England and Wales, Scotland and Northern Ireland, 2019 to 2028.
- The copies are third-party and are not committed: `scripts/fetch_upstream.py` fetches
  them into a gitignored folder checked against a tracked manifest; tests that read them
  skip when it is absent.

## Ranked improvements

1. **O(log holidays) arithmetic.** Work on day ordinals: business weekdays before an
   ordinal come from whole weeks plus a seven-slot prefix table, holidays from a binary
   search over a sorted tuple. Offsets invert that count with a bounded binary search, so
   a million business days cost the same as one.
2. **`Calendar`.** An immutable, hashable calendar built once from a weekend (or a numpy
   style weekmask) and holidays; weekend holidays dropped and duplicates merged, like
   `numpy.busdaycalendar`. The module functions keep their signatures and use it.
3. **Roll conventions as a `Roll` enum** with numpy aliases accepted as strings:
   following, preceding, modified following, modified preceding, half-month modified
   following, nearest, unadjusted and raise. `roll(day, convention)` adjusts one date.
4. **Offsets with a roll.** `add_business_days(..., roll=...)` rolls the start first and
   then counts, exactly like `numpy.busday_offset`; without `roll` the current reading
   (count only landed days, `0` returns the start) is kept and documented as numpy's
   `backward` roll for forward steps and `forward` roll for backward steps.
5. **Strict validation.** Booleans and floats rejected as weekdays and counts,
   `datetime` rejected where a `date` is meant (it silently never equals a holiday), a
   clear `OverflowError` at the ends of the date range, a `ValueError` for a weekend that
   leaves no working day when one is needed.
6. **Ranges.** `business_days(start, stop)` iterates `[start, stop)` in order (empty
   when `stop <= start`), plus `first_business_day` and `last_business_day` of a month.
7. **Antisymmetric counts, stated.** `business_days_between(a, b) == -business_days_between(b, a)`
   holds; numpy counts a reversed range as `(end, begin]`, so the two differ when an
   endpoint is not a business day. Pinned by a test and written in the README.
8. **Command line tool.** `busdays add|count|roll|is|list` with `--weekend`,
   `--weekmask` and `--holidays` (a file of ISO dates), exit codes 0, 1 (not a business
   day) and 2 (bad input).
9. **Contracts.** numpy as oracle over random weekmasks, holidays and roll modes;
   QuantLib conventions on hand-labelled cases; GOV.UK calendars as real holiday sets;
   every README example executed; `__all__` pinned; an installed-wheel test that builds
   the wheel and drives the console script.
10. **Packaging.** Classifiers, keywords, a console script, sdist without the upstream
    copies, CHANGELOG entry.

Rejected for this round: shipping regional holiday rules (the point of the library is that
the caller brings them), Easter computation, time zones and `datetime` support (business
days are calendar dates; a caller converts first).

## Outcome

- Gates (ruff format, ruff check, mypy --strict, pytest) and the installed-wheel and
  sdist tests green on a clean clone with the upstream copies fetched.
- Mutation run: 59 hand-written mutants over every module, all killed in the final run; `__pycache__` purged before each
  and no bytecode written, the baseline green before and after. The first run left seven
  survivors out of 53; each led to a new test (the day just past either end, nearest next to a
  missing side, a month of holidays after a working day, the hash covering holidays, the
  message for a string holiday list) or, for one redundant guard, to simpler code.
- Independent review: no wrong dates or counts. Fixed, each with a test: holiday files
  with a byte order mark, a repeated `--holidays -`, a reader that closes the pipe early
  (`| head`), numpy arrays and numpy bools as weekmask flags, a day-by-day reference
  property test for every convention including both ends of the supported dates, and the
  rolled-start offset past the last date. Documentation now states that module functions
  build a calendar per call, that day names are read in any case, that an all-zero mask
  is allowed and that numpy's `nat` is refused. `requires-python` stays at 3.10, as on
  `main`.
