# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-01

### Stable

- The eleven public exports, their argument names/defaults, calendar normalization,
  half-open antisymmetric counts, offsets, roll conventions and CLI commands.
- Runnable public docstrings, full API guide, seeded reference comparisons, wheel
  installation and upgrade checks, and a typed, dependency-free distribution.

### Changed

- `Roll` normalizes string contents without invoking a subclass's `lower` override,
  preventing unexpected exceptions or selection of a different convention.
- Regression tests enforce the CLI argument limit through process arguments and
  real module invocations, including rejection before help output.
- Invalid `Roll` construction rejects deeply nested values with a bounded `ValueError`
  without formatting the input, preserving convention names, aliases and enum members.
- CLI invocations accept at most 4096 arguments, excluding the executable name,
  and reject larger inputs before parsing to bound repeated-option copying. Use
  holiday files for larger date sets; file contents have no new date-count limit.
- The `Calendar.holidays` docstring imports `date` so ordinary doctest execution works.
- Regression tests enforce aggregation and validation of every repeated holiday file.
- Integer-like arguments are annotated `SupportsIndex`, matching existing runtime
  support. Month helpers now use the normalized month when checking their result,
  fixing `__index__` objects that do not also compare equal to a plain integer.
- `first_business_day` rejects a fully closed month even when the next working date
  falls in the same month of a later year, rather than returning that later date.
- Invalid roll/weekmask values and type names are no longer echoed in validation
  messages. CLI errors omit invalid arguments and holiday file paths; malformed
  holiday files report the line number, and unreadable files report a UTF-8 error.
- Huge CLI offsets fail with a bounded date-range diagnostic, without echoing the
  integer. Leading zeros work even beyond Python's integer-string conversion limit.
- Closed output pipes replace stdout with an in-memory sink, avoiding another failing
  shutdown flush and an open file descriptor. Embedded callers must restore stdout
  before reuse.
- `Calendar` and `Roll` identify their public module as `busdays`; old calendar
  pickles remain readable. The accidental `annotations` export is removed.
- Source archives contain library code and consumer documentation, excluding tests,
  development tools and the upstream manifest. Those remain in the repository.

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
