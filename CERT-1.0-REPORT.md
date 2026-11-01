# busdays 1.0.0 certification report

Progress:
- [x] Create `release/1.0.0` from main `b24a0b3`; confirm PyPI 0.2.0.
- [x] Review the public API, types, errors and runnable docstrings (items 1 to 5).
- [x] Fetch seven upstream sources on 2026-11-01; verify their hashes (item 7).
- [x] Add parser fuzz, diagnostic and public API contracts (items 6 and 9).
- [x] Update README, GUIDE, CHANGELOG and release metadata (items 11 to 13).
- [ ] Wheel/sdist inspection, external consumers and PyPI upgrade (items 8 and 14).
- [ ] Run every available supported interpreter (item 10).
- [ ] Complete the mutation round and record its results (item 18).
- [ ] Final four gates (item 15).
- [ ] Independent reviewer and five QA lenses (items 16 and 19).
- [ ] Merge and publication (item 17).

## Baseline and scope

The certification log had no busdays 1.0.0 entry. No release branch existed locally
or remotely. The main tree was clean. The live
[PyPI JSON endpoint](https://pypi.org/pypi/busdays/json) reported 0.2.0 on 2026-11-01.
The baseline suite on CPython 3.14 passed 673 tests, skipped seven source-dependent
tests and deselected two packaging tests.

## API review

The eleven exported names, parameter names, defaults and valid built-in date results
are retained. Public examples cover every exported callable and Calendar method and
property. `SupportsIndex` annotations now match accepted integer-like arguments.
Month helpers compare normalized integer months. Validation and command-line errors
omit arbitrary invalid values; huge CLI counts are bounded before conversion.
Class metadata uses the public module. Every change from 0.2.0 is in CHANGELOG 1.0.0
and the GUIDE upgrade section. Standard exception families remain the typed error
contract: TypeError, ValueError and OverflowError.

## Ground truth

All seven sources in `data/upstream/MANIFEST.json` were fetched in this session on
2026-11-01. Their byte counts and SHA-256 digests matched the previously pinned
sources. Copies are kept outside the repository through `BUSDAYS_UPSTREAM` and are
never shipped. The manifest records exact URLs, revisions, dates and licences;
present copies must pass size and hash checks before any test runs.

- Four NumPy reference pages: documented examples and normalization rules.
- QuantLib's business-day convention header and calendar implementation: convention
  definitions, including nearest and half-month modified following.
- GOV.UK bank-holiday JSON: real holiday dates for three jurisdictions, checked by
  the NumPy implementation for annual counts and daily settlement offsets.
- NumPy is executed as an independent oracle on 300 seeded calendars and 20 dates
  per calendar, covering offsets, membership, counts and iteration. Another 40
  seeded calendars check month endpoints. A handwritten reference checks boundary
  dates and additional conventions; it is explicitly labelled as such.

## Pending validation

Packaging, interpreter and mutation results will be recorded here as they complete.
Independent review and the five QA lenses are reserved for subsequent review stages.
