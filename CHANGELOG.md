# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0]

### Added

- `Calendar`: an immutable, hashable weekend and holiday set, built once. Counts take
  O(log holidays) time and offsets O(log(holidays) ** 2), however far apart the dates.
- `Calendar.from_weekmask` reads numpy weekmasks (`"1111100"`, `"Sun Mon Tue Wed Thu"`,
  seven flags); `weekend`, `weekmask` and `holidays` properties.
- `Roll` and `roll()`: following, preceding, modified following, modified preceding,
  half-month modified following, nearest (ties go forward), unadjusted and raise; numpy's
  `forward` and `backward` spellings are accepted.
- `add_business_days(..., roll=...)` rolls the start first and then counts, as
  `numpy.busday_offset` does.
- `business_days()` iterates a half-open range; `first_business_day()` and
  `last_business_day()` of a month.
- A `busdays` command line tool (`add`, `count`, `roll`, `is`, `list`), also run as
  `python -m busdays`.

### Changed

- Counts and offsets no longer walk day by day: once a calendar is built they take
  logarithmic time. Module-level functions build one per call (O(H log H) for H
  holidays).
- Stricter input: `bool` and `float` are refused as weekdays and counts, a `datetime` is
  refused where a `date` is meant, holidays must be dates, and a result outside years 1
  to 9999 raises `OverflowError` with a clear message.

## [0.1.0]

- First release.
- `add_business_days`, `business_days_between`, `is_business_day`,
  `next_business_day` and `prev_business_day`, with a configurable weekend mask
  and an optional holiday set.
- Zero dependencies: unlike `numpy.busday_*`, which needs numpy, and
  `workalendar` or `python-holidays`, which ship their own regional calendars,
  this is the pure primitive where the caller supplies the holidays.
