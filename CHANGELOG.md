# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0]

- First release.
- `add_business_days`, `business_days_between`, `is_business_day`,
  `next_business_day` and `prev_business_day`, with a configurable weekend mask
  and an optional holiday set.
- Zero dependencies: unlike `numpy.busday_*`, which needs numpy, and
  `workalendar` or `python-holidays`, which ship their own regional calendars,
  this is the pure primitive where the caller supplies the holidays.
