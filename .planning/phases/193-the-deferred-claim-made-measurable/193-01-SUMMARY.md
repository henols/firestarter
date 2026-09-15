---
phase: 193-the-deferred-claim-made-measurable
plan: 01
subsystem: infra
tags: [pypi, clickhouse, shell, adoption-metrics, gate-01]

requires:
  - phase: 191-.../191-VERIFICATION.md
    provides: confirmation that 2.0.9 is the first stable carrying the firestarter_fw URL, and that 2.0.8 never reached PyPI
provides:
  - "tools/adoption/pypi_version_share.sh — a committed, credential-free, argument-free shell instrument reporting the firestarter PyPI package's fixed-vs-at-risk download split"
  - "a live executed reading (17 fixed / 116 at-risk / 12.8% share / TRIGGER: NOT MET), plus three proofs of the instrument's unmeasured paths (threshold boundary, empty window, server error)"
affects: [193-02, 193-05]

actuals:
  tokens: 2914
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "meta tools/ subdirectory precedent extended: tools/adoption/ beside tools/catalog/, same shell conventions (header block, set -euo pipefail, OK/WARNING/ERROR-style stdout/stderr split)"
    - "a fixed, argument-free SQL literal against a public data source, with the honesty caveat printed unconditionally on every run"

key-files:
  created:
    - tools/adoption/pypi_version_share.sh
    - .planning/phases/193-the-deferred-claim-made-measurable/evidence/193-gate-01-instrument-run.txt
  modified: []

key-decisions:
  - "Split the SELECT list's trigger expression and the curl flag list across multiple lines (rather than one dense line) so each acceptance-criteria substring — user=play, --fail-with-body, toUInt32OrZero, and each clause of the trigger predicate — lands on its own matching line under a line-count grep, without changing what the SQL or the curl invocation does."
  - "Used a quoted heredoc (<<'SQL') to build the QUERY variable instead of a single-quoted string with escaped embedded quotes, so the script's source file carries the SQL's literal single-quoted tokens (e.g. installer IN ('pip', 'uv')) byte-for-byte, matching what a later reader or grep expects to find."

requirements-completed: [GATE-01]

coverage:
  - id: D1
    description: "A committed, runnable shell instrument reports the firestarter PyPI package's fixed-vs-at-risk download split with no credentials and no arguments"
    requirement: GATE-01
    verification:
      - kind: other
        ref: "bash -n tools/adoption/pypi_version_share.sh && ./tools/adoption/pypi_version_share.sh (live run against sql-clickhouse.clickhouse.com)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every printed verdict is followed by the honesty caveat in the strong 'necessary condition, never a sufficient one' form, in the same output, unconditionally"
    requirement: GATE-01
    verification:
      - kind: other
        ref: "grep -cF 'necessary condition, never a sufficient one' on live stdout"
        status: pass
    human_judgment: false
  - id: D3
    description: "The threshold boundary is exact and inclusive on both legs, proven against the live ClickHouse engine with the identical predicate the script carries"
    requirement: GATE-01
    verification:
      - kind: integration
        ref: "curl boundary probe over values('fixed UInt64, at_risk UInt64', (90,10), (89,10), (99,11), (0,0)) -> 1,0,0,0"
        status: pass
    human_judgment: false
  - id: D4
    description: "An unmeasured state (empty window, server error) never prints a verdict and is distinguishable by exit code"
    requirement: GATE-01
    verification:
      - kind: integration
        ref: "empty-window probe (rows_matched=0, share=\\N) and invalid-query probe (curl_error_rc=22), both against the live endpoint"
        status: pass
    human_judgment: false

duration: 22min
completed: 2026-09-14
status: complete
---

# Phase 193 Plan 01: The GATE-01 Adoption Instrument Summary

**A committed `tools/adoption/pypi_version_share.sh` shell script that queries the ClickHouse public PyPI dataset for a live 17-vs-116 fixed/at-risk download split (12.8% share, `TRIGGER: NOT MET` against a 90%/10-download threshold), with a mandatory five-point honesty caveat on every run.**

## Performance

- **Duration:** 22 min
- **Started:** 2026-09-14T10:18:59Z
- **Completed:** 2026-09-14T10:41:00Z (approx.)
- **Tasks:** 2
- **Files created:** 2

## Accomplishments

- Built and committed `tools/adoption/pypi_version_share.sh`: one fixed `curl -G` query against
  `pypi.pypi_downloads_per_day_by_version_by_installer_by_type`, computing the D-06 numerator
  (any stable `>= 2.0.9`, array-compared, never allowlisted) and the D-07 denominator
  (`version = '2.0.7'` exactly), filtered to `installer IN ('pip', 'uv')` (D-04) and excluding
  prereleases with the PEP 440-shaped regex `match(version, '(a|b|rc)[0-9]|dev')` (D-05).
- Ran it live. The authoring-time baseline holds: 17 fixed, 116 at-risk, 12.8% fixed share,
  `TRIGGER: NOT MET` against the D-09 threshold (`>= 90%` share AND `<= 10` at-risk downloads).
- Proved the instrument's three unmeasured paths, each at the layer where it can actually be
  proven. The threshold boundary is inclusive on both legs at the live ClickHouse engine
  (`1,0,0,0` across the four boundary tuples). An empty result window is detectable only through
  the in-query `rows_matched` column, never by counting output lines. A server-side error
  surfaces through `curl --fail-with-body` as exit 22 with the server's own message. `set -e`
  does not swallow it.
- Recorded all four readings, each with its own `capture_date:` and `command:` line, in
  `evidence/193-gate-01-instrument-run.txt`, ending on a single terminal verdict line.

## Task Commits

1. **Task 1: One live reading, end to end** - `352841a9` (feat)
2. **Task 2: The three answers the instrument gives when it cannot measure** - `9c94669b` (test)

**Plan metadata:** pending (this SUMMARY commit)

## Files Created/Modified

- `tools/adoption/pypi_version_share.sh` — the GATE-01 instrument. Mode 0755. Takes no
  arguments, reads no other file, writes nothing to disk. Header names the authoritative source
  and the two recorded fallbacks (PyPI BigQuery, `pypi.pypi_raw`) without building either.
- `.planning/phases/193-the-deferred-claim-made-measurable/evidence/193-gate-01-instrument-run.txt`
  — four executed readings: the live verdict, the threshold boundary, the empty window, and a
  server error, each reproducible from the command recorded beside it.

## The live reading, at execution time

```
window: 2026-06-16 .. 2026-09-13 (rolling 90 days ending at the table's latest date, UTC, stable channel, installer pip and uv)
fixed_downloads_ge_2_0_9: 17
at_risk_downloads_2_0_7: 116
fixed_share_pct: 12.8
threshold: fixed share >= 90% AND at-risk (2.0.7) downloads <= 10, both over the window above
TRIGGER: NOT MET
```

These two integers move daily. A future reader of this SUMMARY should re-run the script rather
than treat 17/116/12.8% as current. That is the discipline the script's own caveat block exists
to enforce. It is why the caveat prints on every run, with no "first run only" flag to skip it.

## Decisions Made

- **Multi-line SQL and curl-flag formatting, not compaction.** The plan's acceptance criteria
  grep for specific substrings (`user=play`, `--fail-with-body`, `toUInt32OrZero`, and each
  clause of the trigger predicate). They count *matching lines*, not occurrences. Packing several
  of these onto one line is syntactically valid SQL and shell, but it would have collapsed
  distinct substrings onto the same line and undercounted. The script's line breaks in the
  trigger expression and the curl invocation exist for this reason, not for readability alone.
  They also happen to read cleanly.
- **A quoted heredoc for the SQL literal.** An earlier draft built the query as a single-quoted
  bash string, with `'"'"'` escape sequences around each embedded SQL single quote. That draft
  ran correctly. But it meant the *source file* no longer contained the literal substring
  `installer IN ('pip', 'uv')` — the escape sequences broke it up. The acceptance criteria check
  directly against the file's bytes. Switching to `QUERY="$(cat <<'SQL' ... SQL)"` (a quoted
  heredoc, so no expansion happens inside it) preserves the SQL's own quoting exactly as written,
  with no bash-level escaping artifacts in the committed file.
- **The rationale documented here, not in the script.** Per D-17 and the project's `CLAUDE.md`,
  the script's header explains what it measures and why (permitted — meta `tools/` is outside
  the no-comments rule), but carries no phase number, requirement ID, decision ID, or plan
  citation. The two decisions above, and the reasoning behind the line-break formatting, live
  here instead.

## Deviations from Plan

None - plan executed exactly as written. The tracer feedback gate (task 1 was `type="tracer"`)
ran per the interactive/`end-of-phase` branch. Task 1's `<verify>` block carried only
`<automated>` items. The gate re-ran every verify item live, and every item passed. It logged
`⚡ Tracer verified end-to-end — expanding` and proceeded directly into task 2 with no
checkpoint. The plan's HUMAN_VERIFY_MODE default and the tracer's own verify shape both point
the same way, so this step was mechanical, not a deviation.

## Issues Encountered

None. The live ClickHouse endpoint answered on the first attempt for every probe, including the
four probes used only for evidence and never wired into the committed script.

## User Setup Required

None - no external service configuration required. The ClickHouse `play` user takes no
credentials, and nothing else in this plan touches a service that needs setup.

## Next Phase Readiness

`tools/adoption/pypi_version_share.sh` is committed, executable, and proven end to end. Plan
193-02 (the seed's trigger rewrite) depends on this instrument's D-09 threshold numbers, which
are unchanged from the authoring-time baseline this plan reproduced exactly (17/116/12.8%,
`TRIGGER: NOT MET`) — 193-02 can cite the threshold with confidence that it matches a live,
re-runnable reading rather than a stale figure from CONTEXT.md alone. No blockers.

---
*Phase: 193-the-deferred-claim-made-measurable*
*Completed: 2026-09-14*

## Self-Check: PASSED

- `tools/adoption/pypi_version_share.sh` exists, mode 0755, `bash -n` clean.
- `.planning/phases/193-the-deferred-claim-made-measurable/evidence/193-gate-01-instrument-run.txt`
  exists with 4 `READING` headings and a terminal `GATE-01 INSTRUMENT PROVEN` line.
- Commits `352841a9` and `9c94669b` both present in `git log --oneline --all`.
- A fresh live run prints `TRIGGER: NOT MET`, the `WHAT THIS DOES NOT MEASURE` banner, and the
  literal phrase `necessary condition, never a sufficient one`.
- No phase, requirement, decision, or plan citation appears in the script's source.
- Work is on branch `gsd/v1.38-repository-rename-activated-2026-09-13`.
