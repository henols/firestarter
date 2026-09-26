---
phase: 122-close-honesty-ledger-community-ask-release-decision
plan: 09
subsystem: release-comms
tags: [honesty-ledger, release-notes, claim-scanner, sdp, at28c]
dependency_graph:
  requires:
    - 122-LEDGER.md (permitted-wording source)
    - 122-CUT.md (observed cut tags)
    - 122-CHANNELS.md (verified channel facts)
  provides:
    - 122-RELEASE-NOTES-fw.md (committed, unposted draft)
    - 122-RELEASE-NOTES-app.md (committed, unposted draft)
  affects:
    - 122-11 (D-16 operator wording review reads both bodies)
    - 122-12 (delivery via gh release edit --notes-file)
tech_stack:
  added: []
  patterns:
    - "hand-authored prerelease body as a committed file, delivered later via --notes-file, never an inline string"
key_files:
  created:
    - .planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-RELEASE-NOTES-fw.md
    - .planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-RELEASE-NOTES-app.md
  modified: []
decisions: []
metrics:
  duration_minutes: 12
  tasks_completed: 3
  files_created: 2
  files_modified: 0
  completed_date: "2026-07-30"
status: complete
---

# Phase 122 Plan 09: Hand-Written Prerelease Bodies Summary

Wrote and committed two hand-authored, ceiling-compliant prerelease bodies (firmware and host-app)
carrying the permitted SDP claim, the explicit "no AT28C silicon was tested" caveat, and the
`DIP24_2816` 0-ALLOW/19-REFUSE qualifier — gated green by the Wave 0 claim scanner and a full
ledger-traceability pass; nothing was posted.

## What Was Built

**`122-RELEASE-NOTES-fw.md`** (83 lines) — the firmware prerelease body. Covers, in the plan's
required order: the three `.hex` assets and the `fw --install` path; the two historical defects
fixed (bypassed address-bus remap / inverted success check, and the per-page single-byte
verification conflation); the new standalone lock command and reported auto-unlock; the permitted
claim with measured timing (568/412/424 µs against a 600 µs budget, the separate 572 µs Leonardo
observation cited without averaging); an explicitly marked "What is NOT proven" section carrying
the canonical caveat; the 43/41 allow-refuse capability boundary naming the FRAM parts and the
`2804`/`2816`/`2817` pre-SDP generation; the community-corroborated-defect / fix-not-corroborated
asymmetry; and a feedback ask.

**`122-RELEASE-NOTES-app.md`** (74 lines) — the host-app prerelease body. Covers: the
`pip install --pre` path and the "no attached files, PyPI is the channel" fact; the new `dev sdp
enable|disable` surface and `--skip-sdp-unlock`; the pre-wire refusal with the same 43/41 split;
the reshaped `dev test` (zero options) with the always-writes warning stated prominently and
verbatim as instructed; the report-filing repository fix; the erase-not-applicable fix for this
family; the permitted claim plus the caveat section; and the same community-datapoint asymmetry.

Both bodies use "this prerelease" rather than a hardcoded version string — no `3.0.0b` string
appears in either file, so there is nothing to drift from `122-CUT.md`'s observed `3.0.0b14` tag.

## Claim-Sentence to Ledger-Claim-Class Traceability

### `122-RELEASE-NOTES-fw.md`

| Section | Claim | Trace |
|---|---|---|
| "What this prerelease is" | Three `.hex` asset names, `fw --install` behavior | Release-mechanics fact — verified in `122-CUT.md` §6 (asset inventory) |
| "The headline" (bypassed remap, `/WE` held high, inverted check) | Historical defect description | Historical/mechanics fact — sourced from `REQUIREMENTS.md` FIX-01/FIX-02 mechanism text per this task's own read-first list; the Ledger's Class 1 permitted wording presupposes this fix without narrating it, so this paragraph is context the Ledger itself does not carry as a numbered class |
| "A second, separate defect" (per-page single-byte sampling → per-byte verification) | Historical defect description | Historical/mechanics fact — sourced from `REQUIREMENTS.md` FIX-03/FIX-04; not a numbered Ledger claim class |
| "New capability: SDP lock" (standalone lock/unlock, reported auto-unlock) | Feature description | Historical/mechanics fact, supported implicitly by Ledger Class 1 (the lock sequence is part of what Class 1's trace coverage verifies) |
| "What is proven, stated exactly" | Emission byte-exactness across all four pinouts + measured timing (568/412/424 vs 600, 572 cited separately) | **Ledger Class 1** (per-pinout emission byte-exactness) + **Ledger Class 2** (measured host-side timing — the SDP unlock emitter) |
| "What is NOT proven" | Protection state unreadable; caveat; `0x0D` stays unverified | Ledger's global Oracle/caveat statement ("No AT28C silicon was tested... every figure below has a software artifact as its subject") plus the ledger's "What no test, gate or review in this phase can close" section |
| "The capability boundary" | 43/41 split, FRAM + pre-SDP generation named, refusal-is-correct reasoning | **Ledger Class 7** (the host refuses before the wire) + the four-pinout composition table's qualifier section |
| "One honest datapoint" | Defect community-corroborated, fix not | **Ledger Class 8** (`COMMUNITY-CORROBORATED`) |
| "Feedback wanted" | Ask for reports | Release-mechanics fact — no claim |

### `122-RELEASE-NOTES-app.md`

| Section | Claim | Trace |
|---|---|---|
| "How to get it" | `pip install --pre`, no GitHub assets, PyPI is the channel | Release-mechanics fact — verified in `122-CHANNELS.md` §4 (app release presence-only, 0 assets) and `122-CUT.md` §6/§7 (C-7) |
| "New command surface" | `dev sdp enable|disable`, `--skip-sdp-unlock`, re-lock deferred | Historical/mechanics fact (HOST-side feature description); the deferred re-lock traces to the Ledger's "Deferred by decision" section, `SDP-F1` |
| "The refusal, stated before you try it" | Pre-wire refusal, 43/41 split, refusal-is-correct reasoning | **Ledger Class 7** (the host refuses before the wire) |
| "`dev test` changed shape" | Zero options, destructive-handling scope, always-writes warning | Historical/mechanics fact — inherited standing obligation named explicitly in the plan (Phase 121 D-04); not a numbered Ledger claim class, but a required carry-over |
| "A report-filing fix" | Wrong-repo filing bug, fixed in source, effective from this release | Release-mechanics fact — historical bug-fix description |
| "Also in this release" | Erase not-applicable marking; docs correction | Release-mechanics fact — historical bug-fix description |
| "What is proven, and what is not" | Emission byte-exactness across all four pinouts, timing assumption documented; protection state unreadable; caveat; no chip's support status changed | **Ledger Class 1** + **Ledger Class 2** (referenced in substance, no numeric figures repeated) + Ledger's global caveat |
| "The community datapoint, and the ask" | Defect community-corroborated, fix not; ask for a write/verify report | **Ledger Class 8** |

No sentence in either body was found to be an unbacked claim requiring deletion or rewrite; every
substantive claim traces either to a numbered Ledger class or is explicitly labelled a
release-mechanics/historical fact above.

## Gate Results

**Pass 1 — claim scanner**, both files via the env seam:

```
PASS: scanned 122-RELEASE-NOTES-fw.md, 122-RELEASE-NOTES-app.md; 2 file(s) carry the required silicon caveat (this PASS is the mechanizable half of criterion 4 only -- see the module docstring's explicit non-claim)
```

Exit code 0. Both file names appear in the single PASS line. Pattern set (`FORBIDDEN_PATTERNS`,
`REQUIRED_CAVEAT_PATTERN`, `_DEFAULT_TARGETS`) was not modified — confirmed by `git status
--short check_permitted_claims.py` showing no change.

**Pass 2 — ledger traceability.** See tables above.

**Pass 3 — hygiene and consistency**, both files:

- No `/workspaces/` path, no `/dev/tty` device name, no token name (`GITHUB_TOKEN`,
  `PYPI_API_TOKEN`, `PERSONAL_ACCESS_TOKEN`) — `grep` count 0 in both files.
- No GSD-internal identifier (`D-NN`, `C-NN`, plan ids, requirement ids) — `grep` count 0 in both
  files.
- The phrase "all 84" is absent from both files (both use "66 of 84" framing is not applicable
  here since neither body cites a trace-coverage figure directly by that phrasing; both instead
  cite "43 are allowed, 41 are refused" of "the full set of 84 chips this protocol covers" —
  never "all 84").
- No `3.0.0b` version string appears in either file; both use "this prerelease" per the plan's own
  hard constraint, so there is no drift-check needed against `122-CUT.md`'s `3.0.0b14`.
- Fence balance: `grep -c '```'` on both files returns an even count (0 — neither body uses a
  fenced code block).
- Canonical caveat fragment `no AT28C silicon was tested` present in both files, each on a single
  unwrapped line (verified via the plan's own `grep -qi` acceptance check, which requires the
  phrase not be split across a markdown line break — one line break in the firmware draft was
  found and fixed during this pass).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Line-wrapped caveat sentence broke the grep-based acceptance check**
- **Found during:** Task 1 self-verification (running the plan's own automated `<verify>` command)
- **Issue:** The canonical caveat sentence "no AT28C silicon was tested" was authored across a
  markdown line wrap (`...turns on: **no AT28C silicon was` / `tested.** Nobody...`), which is
  visually identical when rendered but fails a literal `grep -qi 'no AT28C silicon was tested'`
  check, since grep matches within a single line by default.
- **Fix:** Reflowed the paragraph so the full caveat sentence sits on one line, with the following
  sentence starting a new paragraph.
- **Files modified:** `122-RELEASE-NOTES-fw.md`
- **Commit:** `8d0627f` (folded into Task 1's commit before it was made — the fix landed before
  the file was ever staged)

No other deviations. Both bodies were written per the plan's nine/eight-point structure, gated
green on the first full scanner run, and no forbidden phrase was ever triggered.

## Delivery Status (explicitly NOT done by this plan)

Both `gh release view <tag> --repo <repo> --json body -q '.body|length'` checks confirm both
release bodies are still length **0** on GitHub. Comment counts on `henols/firestarter_prom#11`
and `#12` are unchanged at **12** and **8** respectively, matching every prior plan's baseline in
this phase. Nothing was posted. Delivery is `gh release edit <observed tag> --repo <repo>
--notes-file <committed path>` in plan 122-12, after the D-16 blocking operator wording review in
plan 122-11, which reads the two traceability tables above.

## Requirements

`requirements: [CLOSE-02, CLOSE-03]` in this plan's frontmatter — **neither ticked**. Both span
multiple plans; CLOSE-02 and CLOSE-03 close only in plan 122-13, after both comments are posted and
both channels re-verified. No `REQUIREMENTS.md` edit was made by this plan.

## Self-Check: PASSED

- `122-RELEASE-NOTES-fw.md` exists: FOUND
- `122-RELEASE-NOTES-app.md` exists: FOUND
- Commit `8d0627f` (firmware body): FOUND in `git log --oneline`
- Commit `d28cd35` (app body): FOUND in `git log --oneline`
- Claim scanner exit code 0 with both files named: CONFIRMED
- Both GitHub release bodies still length 0: CONFIRMED
- Issue 11/12 comment counts unchanged (12/8): CONFIRMED
