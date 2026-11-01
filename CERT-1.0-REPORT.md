# busdays 1.0.0 certification report

Progress:
- [x] Create `release/1.0.0` from main `b24a0b3`; confirm PyPI 0.2.0.
- [x] Review the public API, types, errors and runnable docstrings (items 1 to 5).
- [x] Fetch seven upstream sources on 2026-11-01; verify their hashes (item 7).
- [x] Add parser fuzz, diagnostic and public API contracts (items 6 and 9).
- [x] Update README, GUIDE, CHANGELOG and release metadata (items 11 to 13).
- [x] Wheel/sdist inspection, external consumers and PyPI upgrade (items 8 and 14).
- [x] Run every available supported interpreter (item 10).
- [x] Complete the mutation round and record its results (item 18).
- [x] Final four gates (item 15).
- [ ] Independent reviewer and five QA lenses (items 16 and 19).
- [ ] Merge and publication (item 17).

## Baseline and scope

The certification log had no busdays 1.0.0 entry. No release branch existed locally
or remotely. The main tree was clean. The live
[PyPI JSON endpoint](https://pypi.org/pypi/busdays/json) reported 0.2.0 on 2026-11-01.
The baseline suite on CPython 3.14 passed 673 tests, skipped seven source-dependent
tests and deselected two packaging tests.

## API review

The eleven exported names, parameter names and defaults are retained. Date results
are preserved except for two documented month-helper corrections. Public examples
cover every exported callable and Calendar method and property. `SupportsIndex` annotations now match accepted integer-like arguments.
Month helpers compare normalized integer months and reject a result in a later year.
Validation and command-line errors omit arbitrary invalid values; huge CLI counts are bounded before conversion.
Class metadata uses the public module. Every change from 0.2.0 is in CHANGELOG 1.0.0
and the GUIDE upgrade section. Standard exception families remain the typed error
contract: TypeError, ValueError and OverflowError.

## Ground truth

All seven sources in `data/upstream/MANIFEST.json` were fetched in this session on
2026-11-01. Their byte counts and SHA-256 digests matched the previously pinned
sources. Copies are kept outside the repository through `BUSDAYS_UPSTREAM` and are
never shipped. The manifest records exact URLs, revisions, dates and licences;
present copies must pass size and hash checks before any test runs.

- Four NumPy reference pages: documented examples and normalization rules. The eight
  offset examples, three count examples and membership example are parsed directly
  from the fetched HTML by `tests/test_spec.py`, including their expected values.
- QuantLib's business-day convention header and calendar implementation: convention
  definitions, including nearest and half-month modified following.
- GOV.UK bank-holiday JSON: real holiday dates for three jurisdictions, checked by
  the NumPy implementation for annual counts and daily settlement offsets.
- NumPy is executed as an independent oracle on 300 seeded calendars and 20 dates
  per calendar, covering offsets, membership, counts and iteration. Another 40
  seeded calendars check month endpoints. A handwritten reference checks boundary
  dates and additional conventions; it is explicitly labelled as such.

## Scorecard

| Item | Status | Evidence |
| --- | --- | --- |
| 1 | PASS | Stable names, signatures and defaults; corrections documented and tested against PyPI 0.2.0. |
| 2 | PASS | Exact `__all__`, no accidental public imports, package-only imports in documentation. |
| 3 | PASS | 24 runnable docstring examples; README and GUIDE examples executed. |
| 4 | PASS | `mypy --strict src tests scripts`; public integer protocols typed; `py.typed` in the wheel. |
| 5 | PASS | Standard typed exceptions documented; bounded library and CLI diagnostics. |
| 6 | PASS | Contracts for exports, options, normalization, dates, boundaries, rolls, CLI and failures. |
| 7 | PASS | Seven live-fetched sources, extracted examples, real NumPy output and UK holidays. |
| 8 | PASS | Isolated installed wheel, console script and module CLI; real PyPI upgrade and old pickle. |
| 9 | PASS | Seeded reference properties, 9,000 parser strings, large inputs and operation-count bounds. |
| 10 | PASS | Seven available runtimes, 705 tests each against the installed wheel; results below. |
| 11 | PASS | Required badge, problem and NumPy comparison, absolute links, strict twine checks. |
| 12 | PASS | CHANGELOG 1.0.0 dated 2026-11-01 with every behavior change. |
| 13 | PASS | Version 1.0.0, stable classifier, Python 3.10+, MIT, URLs and no runtime dependencies. |
| 14 | PASS | Wheel and sdist contents inspected, LICENSE included, no upstream copies or test artifacts. |
| 15 | PASS | Each gate exits zero; 708 tests including the three packaging/upgrade tests. |
| 18 | PASS | 21 of 21 deliberate mutations killed by contracts. |

## Properties and hostile inputs

The existing NumPy oracle uses seeds 0 to 299; the independent day-by-day convention
reference uses seeds 0 to 149. Parser fuzz uses seeds 19, 1729 and 65537, with 3,000
strings per seed including controls, Unicode and lone surrogates. Invalid inputs
raise documented errors with bounded messages; successful weekmasks normalize and
round-trip. CLI tests cover unknown commands, ambiguous options, invalid explicit
arguments, 100,000-digit counts and zero padding. API parser tests reach one million
characters. Large date offsets have deterministic binary-search probe bounds.

Additional scaling measurements on 2026-11-01 (best of three runs, seconds):

| Input | 100,000 characters | 400,000 | 1,600,000 |
| --- | --- | --- | --- |
| Valid roll with separators | 0.015 | 0.042 | 0.182 |
| Repeated valid weekday names | 0.076 | 0.252 | 1.437 |
| Invalid whitespace weekmask | 0.013 | 0.052 | 0.144 |

## Mutation round

Each change below was applied alone in a scratch copy. The complete non-packaging
suite ran with `-x`, a 300-second per-test timeout and no bytecode reuse. Every listed
mutation produced an assertion failure; no mutation survived. The unmodified suite
passed before and after the round. These results cover the implementation preparation
round only; independent contract-strength review is still pending.

| ID | Deliberate bug | First failing contract |
| --- | --- | --- |
| M01 | shift weekday mapping | `tests/test_busdays.py::test_is_business_day_rejects_the_weekend` |
| M02 | invert holiday membership | `tests/test_busdays.py::test_is_business_day_rejects_the_weekend` |
| M03 | add rather than subtract holidays | `tests/test_busdays.py::test_holidays_are_skipped` |
| M04 | reverse count sign | `tests/test_busdays.py::test_between_counts_the_half_open_interval` |
| M05 | offset weekday inverse by one | `tests/test_busdays.py::test_add_steps_over_the_weekend` |
| M06 | drop inverse search endpoint | `tests/test_calendar.py::test_a_month_of_holidays_after_a_working_day_has_no_business_day` |
| M07 | following skips valid input | `tests/test_calendar.py::test_first_and_last_business_day_of_a_month` |
| M08 | preceding excludes valid input | `tests/test_calendar.py::test_first_and_last_business_day_of_a_month` |
| M09 | zero offset loses starting date | `tests/test_busdays.py::test_add_zero_returns_the_start_unchanged` |
| M10 | negative offset off by one | `tests/test_busdays.py::test_negative_n_moves_backwards` |
| M11 | wrapper drops holidays | `tests/test_busdays.py::test_is_business_day_rejects_a_holiday` |
| M12 | iteration includes stop | `tests/test_cli.py::test_commands[args8-2026-01-01\n2026-01-02\n2026-01-05\n]` |
| M13 | month helper forgets year | `tests/test_calendar.py::test_first_business_day_never_returns_the_same_month_in_a_later_year` |
| M14 | nearest ties go backward | `tests/test_reference.py::test_every_convention_matches_the_reference[0]` |
| M15 | half-month misses day fifteen | `tests/test_reference.py::test_every_convention_matches_the_reference[11]` |
| M16 | accept bool integer arguments | `tests/test_calendar.py::test_month_helpers_reject_non_integers` |
| M17 | accept datetime inputs | `tests/test_validation.py::test_dates_must_be_plain_dates[value0]` |
| M18 | accept weekday seven | `tests/test_busdays.py::test_weekend_day_out_of_range_is_rejected` |
| M19 | reverse normalized holidays | `tests/test_calendar.py::test_weekend_holidays_are_dropped_and_duplicates_merged` |
| M20 | wrong membership exit status | `tests/test_cli.py::test_not_a_business_day_exits_1` |
| M21 | echo invalid roll input | `tests/test_hostile.py::test_parser_fuzz_has_only_documented_results[19]` |

## Packaging and upgrade

The sdist builds a wheel successfully with the isolated Hatchling backend. The
wheel has ten Python modules, `py.typed`, metadata, the CLI entry point and LICENSE.
The sdist contains those source files, build configuration and hook, LICENSE,
README, GUIDE, CHANGELOG and CONTRIBUTING. Neither archive contains tests, caches,
reference copies or scratch files. Both pass `twine check --strict`.

The installed-wheel checks run outside the checkout, including an isolated Python
consumer and real subprocess calls to `busdays` and `python -m busdays`. The upgrade
test installs PyPI 0.2.0 first and upgrades that same venv to the locally built wheel.
Its seed 7319 exercises 1,000 calendars with offsets, counts, membership, iteration,
month helpers and every roll convention. Valid results agree, a 0.2.0 calendar pickle
loads and works, the closed-year correction is checked explicitly on both releases,
and diagnostic/class-metadata changes are verified. All five CLI commands are driven
through both entry points; version, help, stdin holidays and failure exits are checked.

## Python matrix

The launcher contains stale paths to removed installations. Actual local runtimes
were discovered separately; duplicate copies of the same version are represented
once. Each matrix environment installs the built wheel, NumPy, pytest-timeout and
mypy. Tests run with `-I`, an empty pytest `pythonpath`, and package import paths
confirmed inside that environment's `site-packages`.

| Runtime | Full suite | Final wrapper contracts |
| --- | --- | --- |
| CPython 3.14.6 | 705 passed, 3 deselected in 12.68s | 5 passed |
| CPython 3.10.22 | 705 passed, 3 deselected in 35.20s | 5 passed |
| CPython 3.11.18 | 705 passed, 3 deselected in 21.91s | 5 passed |
| CPython 3.12.16 | 705 passed, 3 deselected in 10.27s | 5 passed |
| CPython 3.13.18 | 705 passed, 3 deselected in 14.95s | 5 passed |
| CPython 3.14.10 | 705 passed, 3 deselected in 13.75s | 5 passed |
| CPython 3.14.10+freethreaded | 705 passed, 3 deselected in 16.78s | 5 passed |

The available versions cover every advertised Python minor release (3.10 through
3.14). No advertised minor version was unavailable. Python 3.9 and earlier are
below the declared minimum. NumPy 2.2.6 runs on 3.10 and NumPy 2.5.4 on newer runtimes.

## Gates

On CPython 3.14.6 each command returned zero independently:
`ruff format --check .`, `ruff check .`, `mypy --strict src`,
`mypy --strict src tests scripts`, and pytest with the default marker restriction
removed to include packaging: 708 passed. All tests have a 300-second timeout and
explicit scratch paths for temporary files. The strengthened wrapper-option contract
was also rerun after its final edit.

## Independent QA and review

| Stage | Status |
| --- | --- |
| a. API and docs | A-01 fixed; independent re-review pending |
| b. Correctness and ground truth | PENDING |
| c. Adversarial and robustness | C1 and C2 confirmed fixed in round 2; C3 fixed, independent re-review pending |
| d. Packaging and real e2e | PENDING |
| e. Contract strength | E-001 and E-002 confirmed fixed; E-003, E-004 and E-005 fixed in round 3, independent re-review pending |
| Independent reviewer, item 16 | PENDING |
| Merge and publication, item 17 | PENDING |

Preparation does not claim an independent verdict or authorize publication.

### QA fixes, round 1 (2026-11-01)

Reviewed baseline: `dfd438480a7ea661da1a7be0f81f8dd8d91d632b`.
Fix commit: `2417ec5cf9395fd87a2371aac5b9b8f5b486e0a3`
(`fix certification round one findings`).

| Finding | Change and verification |
| --- | --- |
| A-01, low | Import `date` in `Calendar.holidays`. Ordinary `doctest.testmod(busdays)` has a dedicated contract with no injected globals. All 14 module doctests pass. |
| C1, medium | Validate `Roll` construction before Enum formats invalid values. The 100,000-level built-in list and an invalid string with a raising `repr` now produce bounded `ValueError`. Existing aliases, member identity and pickle round trips pass. |
| C2, medium | Reject more than 4096 arguments before argparse runs, as permitted by the finding. The guide, help and changelog document the limit and using files for large holiday sets. Contracts accept the exact limit and reject excess date/file options before parsing. The 64,000-option reproduction exits 2 in 0.073 seconds locally. |
| E-001, medium | Add contracts for combining two holiday files and rejecting malformed input in the second file. Production file aggregation remains unchanged. M52 was applied in a scratch copy; both contracts fail with the expected wrong result and missing error. |

The behavior contracts were run against the original implementation before fixing
C1 and C2 and failed on the reported paths. The standard doctest contract also
failed before the documentation fix. Both E-001 contracts pass against production
and fail against M52; no surviving mutation is claimed as resolved without a failure.

Local validation on CPython 3.14.6: `ruff format --check .`, `ruff check .`,
`mypy --strict src`, and `mypy --strict src tests scripts` each exit zero. The full
suite, with the default marker restriction removed, passes 716 tests including
packaging and upgrade checks. All pytest runs use a 300-second per-test timeout
and temporary directories under the certification scratch directory. The existing
interpreter matrix above describes preparation, not a new matrix for this fix round.

All four reported findings are fixed. No findings are disputed. Independent lens
verdicts remain pending re-review; these checks do not authorize merge or publication.

### QA fixes, round 2 (2026-11-01)

Reviewed baseline: `eae87cba4476cab563e0c010bab1ab62235980f2`.
Fix commit: `fix certification round two findings`, the direct child of that
baseline on `release/1.0.0` containing this section.

| Finding | Change and verification |
| --- | --- |
| C3, medium | Normalize with `str.lower(value)` so string subclasses cannot raise an unexpected exception or select another convention through a `lower` override. Six new contracts cover raising and misleading overrides with canonical, alias and separator-containing names. All six failed against the reviewed baseline and pass after the fix. Early nonstring rejection and bounded diagnostics remain covered. |
| E-002, medium | Add contracts for `main()` through `sys.argv` and real `python -m busdays` subprocesses. Both accept exactly 4096 arguments and reject 4097 repeated `--help` arguments with exit 2, empty stdout and a bounded limit diagnostic. The production CLI already satisfies this behavior and needs no implementation change. |

Mutation verification in a scratch copy:

| Mutation | Result | Detecting contracts |
| --- | --- | --- |
| N06 / E-002: guard the limit with `argv is not None` | Killed; two failures, two passes | `test_cli_process_arguments_obey_limit[4097]` and `test_cli_subprocess_arguments_obey_limit[4097]` in `tests/test_qa_contracts.py` fail because the mutated CLI exits 0. Both 4096-argument boundary cases still pass. |

Local validation on CPython 3.14.6: `ruff format --check .`, `ruff check .`,
`mypy --strict src`, and `mypy --strict src tests scripts` each exit zero. The full
suite with the default marker restriction removed passes 726 tests, including
packaging, upgrade and upstream-reference checks, with no skips. Every pytest run
uses a 300-second per-test timeout and temporary directories under the certification
scratch directory. The interpreter matrix above remains the preparation matrix.

Both round 2 findings are fixed. No findings are disputed. Independent re-review
remains pending; these results do not authorize merge or publication.

### QA fixes, round 3 (2026-11-01)

Reviewed baseline: `cd4e5501c053ce499f2c3e4426423ce7c6b41bba`.
Fix commit: `strengthen roll subclass normalization contracts`, the direct child
of that baseline on `release/1.0.0` containing this section.

All three findings identify missing regression coverage. The production
implementation already satisfies these contracts; no API or behavior change is
needed. E-002 was independently confirmed fixed by lens e in round 3.

`tests/test_roll_subclasses.py` adds 18 cases with handwritten expectations:
canonical `following`, alias `Forward` and mixed-case `Modified_Following`, each
with misleading and raising overrides for the three methods below. All 18 pass
on the reviewed implementation. Each reported mutation was then injected alone
in a scratch copy and tested against the new contracts.

| Finding | Injected replacement for `str.lower(value)` | Detecting contract | Result |
| --- | --- | --- | --- |
| E-003, medium | `str(value).lower()` | `test_roll_ignores_str_override` | Six failures: three wrong conventions and three unexpected exceptions; 12 other cases pass. |
| E-004, medium | `str.lower("".join(value))` | `test_roll_ignores_iter_override` | Six failures: three wrong conventions and three unexpected exceptions; 12 other cases pass. |
| E-005, medium | `str.lower(value.replace("_", ""))` | `test_roll_ignores_replace_override` | Six failures: three wrong conventions and three unexpected exceptions; 12 other cases pass. |

The scratch source was restored byte-for-byte, then all 18 new contracts passed
again. Mutation logs and results are retained under the certification scratch
directory in `fix-r3/logs` and `fix-r3/results.json`.

Local validation on CPython 3.14.6: `ruff format --check .`, `ruff check .`,
`mypy --strict src`, and `mypy --strict src tests scripts` each exit zero. The full
suite with the default marker restriction removed passes 744 tests, including
packaging, upgrade and upstream-reference checks, with no skips. Every pytest run
uses a 300-second per-test timeout and temporary directories under the certification
scratch directory. The interpreter matrix above remains the preparation matrix.

All three round 3 findings are fixed. No findings are disputed. Independent
re-review remains pending; these results do not authorize merge or publication.
