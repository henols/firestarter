---
created: 2026-08-31T10:27:45Z
title: Report the chip's exact database name in `dev test` issues, artifacts, and tests
area: host app
files:
  - firestarter_app/firestarter/cli_handlers.py:2345
  - firestarter_app/firestarter/cli_handlers.py:2135-2152
  - firestarter_app/firestarter/cli_handlers.py:2455
  - firestarter_app/firestarter/submit.py:155-165
  - firestarter_app/firestarter/submit.py:679
  - firestarter_app/firestarter/diagnostic_report.py:186-214
  - firestarter_app/firestarter/diagnostic_report.py:598
  - firestarter_app/firestarter/diagnostic_report.py:826
  - firestarter_app/firestarter/database.py:382
  - firestarter_app/firestarter/database.py:446-485
resolves_phase: 181
resolved: 2026-09-09 (resolved by plan 181-05's RPT-F1 -- proposed solution superseded, not implemented as written)
status: resolved
---

## Problem

A `dev test <chip>` run carries the operator's **raw CLI token** end to end — into the
report model, the saved artifacts, and the filed issue title. Nothing on that path ever
maps the token back to the canonical `part_number` of the database row that was actually
matched.

The lookup is deliberately forgiving. `EpromDatabase.get_eprom_config` lower-cases the
query (database.py:469), matches any comma-separated alias, and paren-normalizes mode
annotations (database.py:446-485). So `at28c256`, `AT28HC256L` and `ds1245ab` all resolve
successfully to rows whose `part_number` is a *different string* than what the operator
typed:

| Typed | Matched `part_number` |
|-------|-----------------------|
| `at28c256` | `AT28C256,AT28C256E,AT28C256F,AT28HC256,AT28HC256E,AT28HC256F,AT28HC256L` |
| `w27c512` | `W27C512,W27E512` |
| `ds1245ab` | `DS1245AB(RW),DS1245Y(RW)` |

Four consequences:

1. **Issue titles name a string that may appear nowhere in the database.**
   `build_title` interpolates the token verbatim as `[dev test] {chip} — {VERDICT} ({hash})`
   (submit.py:155-165, called at submit.py:679). Triage (the `devtest-triage` skill) and the
   validated-chip log then key on a spelling `chip_database.json` does not contain.
2. **Dedup groups split silently.** `dedup_fingerprint` hashes `ac.chip` as its first
   component (diagnostic_report.py:186-214, specifically line 211). Two spellings of the
   same physical chip hash to different ids, so the N>=2 agreement count that the promotion
   ladder depends on is divided across groups with no signal that it happened.
3. **Saved artifacts inherit the token.** `dev-test-<chip>.json` / `.md` filenames come from
   `_sanitize_chip_token` (cli_handlers.py:2135-2152) and the report heading from
   cli_handlers.py:2455; the console table title from diagnostic_report.py:826.
4. **The app test suite pins the non-canonical spelling as normal.** `firestarter_app/tests/`
   hardcodes `"at28c256"` (12 occurrences) and `"w27c512"` (6), all lowercase, none matching
   any `part_number`.

## Solution

The canonical name is already available on the resolved record: `db.get_eprom(chip)["name"]`
is the matched row's `part_number` (database.py:382). Resolve once in the `dev test` handler
(cli_handlers.py:2345) and put the canonical name — not the CLI token — into
`AutoCapture.chip`, keeping the operator's raw token as a separate provenance field if it
is worth disclosing.

Two decisions this needs before it can be planned:

- **What "the exact name" means for a multi-alias row.** `part_number` is a comma-joined
  alias list and is unusable verbatim in a title. The likely rule is the first
  comma-separated alias, but that has to be stated, not assumed.
- **Whether to strip the parenthetical mode annotation.** Do NOT strip it blindly: DALLAS
  ships `DS1245AB(RW),DS1245Y(RW)` and `DS1245AB(TEST),DS1245Y(TEST)` as two *distinct*
  rows, so paren-stripping collides them into one name.

Cost to state up front: re-keying `dedup_fingerprint` is a breaking change to report
identity — every already-filed group re-keys once. Either accept that with the cost stated,
or normalize only the display surfaces (title, artifacts, table) and deliberately leave the
hash on the raw token, recording why.

Also in scope: update the app tests to the canonical spellings, so the suite stops
sanctioning the lowercase form.

## RESOLUTION (2026-09-09)

**Resolved by this phase, not implemented as written.** RPT-F1 (plan `181-05`) is this todo itself,
but its own proposed solution above -- put the canonical name **into** `AutoCapture.chip` -- is
**superseded** by D-2's additive decision: `auto_capture.canonical_part_number` is a new, separate
field carrying the matched database `part_number`; `ac.chip` keeps the operator's raw token
unchanged, so `dedup_fingerprint`'s first hashed component (which reads `ac.chip`) never re-keys.
Both open sub-questions this todo left for the planner are answered: "what the exact name means for
a multi-alias row" is D-01's token-match rule (the alias that case-insensitively equals the
operator's raw token; first alias when none matches); "whether to strip the parenthetical mode
annotation" is D-02's answer -- no, the selected alias keeps the mode annotation verbatim, because
paren-stripping collides distinct DALLAS rows. The "also in scope" test-sweep ask (updating the app
test suite to canonical spellings) is **refused with a measurement**, D-04: a sweep would rewrite
`chip="m27c512"` to `chip="M27C512"`, which produces the exact hash Phase 174 froze as
`m27c512-full-canonical-name` specifically to catch a `parts[0]` normalization -- colliding two
frozen shapes and re-keying the milestone's own oracle. What changed instead: assertions on
`build_title()` output and on the rendered headings, per D-04's own scope statement.
