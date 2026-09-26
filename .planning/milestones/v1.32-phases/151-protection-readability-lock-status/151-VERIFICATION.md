---
phase: 151-protection-readability-lock-status
verified: 2026-08-20T19:30:08Z
status: passed
score: 10/10 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 151: Protection Readability — `lock-status` Verification Report

**Phase Goal:** A user can ask what a chip's protection state is and get either the real answer
or an explicit refusal that says why — never a guess. And `protect_on_after` stops being an
intent the system silently ignores.

**Verified:** 2026-08-20T19:30:08Z
**Status:** passed
**Re-verification:** No — initial verification

## Method

This was a from-scratch, goal-backward, code-level verification — not a SUMMARY.md read-through.
For every claim below I either (a) read the actual source in both submodules at the commits
pinned by the meta repo's gitlinks (`firestarter@373d6da7`, `firestarter_app@4a6f5e8d`), (b) ran
the real test/gate commands myself in a fresh shell, or (c) both. Both submodule working trees
were git-clean before and after every command I ran (confirmed via `git status --short`).

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria 1–5, merged with PLAN must-haves)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A committed, hand-curated family-level table records mechanism/readability/permanence, each row cited to `lockable-proms.md` + datasheet source | ✓ VERIFIED | `firestarter_app/firestarter/protection_readability.py` — 126-row-derived, 273-token curated surface (`DOCUMENTED_READABLE_TOKENS`, `DOCUMENTED_NOT_READABLE_TOKENS`), every entry commented with a `lockable-proms.md:NNN §N` citation; footnoted rows ([1],[4]-[7]) resolve to real vendor-datasheet URLs in `lockable-proms.md`'s footnote block (checked `:392-398`). `tests/test_protection_table_citations.py` (6 tests) proves every citation resolves as a substring of the doc — ran green independently. |
| 2 | `dev lock-status <chip>` reports protection state on families documented as readable, beta-only surface | ✓ VERIFIED | `cli_handlers.py:1745 @dev.command(name="lock-status")`; registered only under `_DevGroup`; `channel.py:69` adds `"lock-status"` to `BETA_ONLY_DEV_COMMANDS`. `tests/test_dev_group_channel_gating.py::test_simulated_stable_dev_commands_is_exactly_read_and_test` is a real *negative* subprocess assertion (`{"read","test"}` exactly) — confirmed `lock-status` absent on simulated-stable. No `@cli.command(name="lock-status")` (top-level) exists anywhere — verified by enumerating every `@cli.command` in `cli_handlers.py` (14 total, none named lock-status). |
| 3 | On non-readable families (incl. every `0x0D`/SDP part) the command refuses, names the reason, never fabricates | ✓ VERIFIED | `protection_gate_for_entry`'s `NOT_READABLE_PROTOCOL_IDS = {13}` unconditionally routes every `0x0D` row to a refusal before any silicon read is attempted (code-read, `protection_readability.py:169-174,295-298`). D-06's fail-closed unanimity: any `undocumented` or `documented-not-readable` alias on a `0x05`/`0x06` entry refuses, naming the alias. Bench-confirmed live: `dev lock-status W29C020` (unforced) on real hardware returned `undocumented_alias ... W29C022 (undocumented)` (`151-BENCH.md` Leg B). |
| 4 | Output distinguishes "unprotected" from "not readable"; nothing reads as a guarantee where none exists | ✓ VERIFIED | D-09's 8 class tokens are disjoint by construction; `SILICON_ONLY_TOKENS = {"protected","unprotected"}` producible only from `lock_status.classify_protection_response`, never from the pure gate module — enforced by `tools/check_protection_readability_invariants.py` Class 1(a), which I ran directly (`PASS: ... 0 Class 1 ... violations`) and also proved *fails* on both committed planted fixtures (`planted_protection_permit_by_default.py` → exit 1 naming Class 1a+1b; `planted_protection_widenable_tokenset.py` → exit 1 naming Class 2a/2b). `test_lock_status_class_partition.py::test_silicon_only_tokens_never_appear_in_a_return_value_ast` + `test_no_row_resolves_to_a_silicon_only_token` independently walk all 746 DB rows — ran green. |
| 5 (DATA-06) | `protect_on_after` documented once as an advisory hint with no runtime effect; measurement stated, not shrugged | ✓ VERIFIED | `firestarter_app/doc/infoic-field-dictionary.md:142-173` — one authoritative section, states 70/746 (27/27 on alg 5, 43 on alg 13), "no runtime consumer exists ... because `write --sdp-relock` is deferred". `doc/package-details.md:49-50` and `doc/protocol-flags.md:22-23` carry the required one-line pointers (both read and confirmed). `tests/test_protect_flags_doc_measurements.py` (10 tests, incl. no-runtime-consumer source-scan and sdp_capability-untouched guard) — ran green. `git log` confirms `firestarter/sdp_capability.py` untouched since Phase 121. |

**Score:** 5/5 roadmap success criteria + 5 additional PLAN must-haves (below) = 10/10 verified, 0 present-but-behavior-unverified.

### Additional Must-Haves Cross-Checked (from PLAN frontmatter, D-12/D-09/D-10 mechanics)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 6 | All 746 DB rows resolve exhaustively into the frozen 8-token class set, census pinned as literals (40 not_implemented, not 39) | ✓ VERIFIED | Ran `tests/test_lock_status_class_partition.py` (18 tests) green independently. Census confirmed: `no_mechanism`=405, `not_implemented`=40 (39@0x10 + 1@0x34/XICOR — OD-2's correction), `not_readable`⊇84(0x0D)+24(curation)=108, `read_permitted`=81, `undocumented_alias`=112. `405+40+84+217=746` and `81+24+112=217` both hold. OD-2's supersession of VALIDATION.md's earlier 39 is explicitly recorded in `151-DESIGN.md` §4, not silently applied. |
| 7 | D-12 leg 1 non-vacuity: exhaustiveness test observed RED on the `0x34` row before being fixed, not just "leg exists" | ✓ VERIFIED | `151-12-SUMMARY.md:80-88` records the verbatim red transcript (`AssertionError: ... XICOR/X88C64P,X88C64S ... is not classed by this module`) followed by revert-and-rerun 10/10 green, with `git status --short` confirming zero diff landed. Test docstring (`test_all_746_rows_resolve_exhaustively`) restates this non-vacuity condition. |
| 8 | `--force` bypasses only host-side table refusal; wire flags word is byte-identical with/without it (C-16) | ✓ VERIFIED | `test_lock_status_cli.py::test_force_does_not_change_the_wire_flags_word` — ran green. Firmware side: both `flash_5v_page.cpp:67` and `flash_nor_unlock.cpp:59-63` comments state the `0x01` force bit is deliberately not read on this command, and `CMD_LOCK_STATUS`'s handlers take no ctrl-flag branch. |
| 9 | MERGE-05 firmware growth funded with named, SHA-attributed exemptions; leonardo's 0 B headroom band honored | ✓ VERIFIED | Independently re-ran `check_size_baseline.py --policy merge05` against the three committed `merge05_lock_status_v151_*.log` fixtures: `PASS: leonardo(flash=27500/32768[+594<=594=band0+exempt96+seam210+lock288],ram=2016/2560[+2<=2=seam2]), uno(...), uno328pb(...)`, exit 0 — matches claimed figures exactly. `MERGE05_LOCK_STATUS_READ_EXEMPTION_BYTES = 288` is a new named literal in `check_size_baseline.py:323`. |
| 10 | Test-suite/gate counts as claimed (1806 host, 315 firmware pytest, 163+163+11 native, zero AVR warnings) | ✓ VERIFIED (mostly independently re-run) | Ran the full host suite myself: **1806 passed** in 207.86s (`pytest tests/ -o addopts="-ra"`, py3.11). Ran `pio test -e native`: **163/163**. Ran `pio test -e native_nodevtools`: **163/163**. Ran `pio test -e native_pinmap_provisional` (11 tests incl. `test_pinmap_provisional_refuses_cmd_lock_status`): **11/11**. Did not independently re-run `firestarter/tests/` (315 pytest) or the cold triple-AVR-target rebuild transcript — accepted from `151-10-SUMMARY.md`/`151-SIZE-TRANSCRIPTS.md` since the MERGE-05 policy check against the committed fixture logs reproduces the same numbers exactly, which is strong corroborating evidence. |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/protection_readability.py` | LOCK-01 pure curated-table module | ✓ VERIFIED | Exists, substantive (1016 lines), wired into `lock_status.py`/`cli_handlers.py`, import-pure per its own invariant. |
| `firestarter_app/tools/check_protection_readability_invariants.py` | LOCK-01 AST gate | ✓ VERIFIED | Exists, ran directly — PASS on real module, FAIL (exit 1) on both planted fixtures via env-var seam. |
| `firestarter_app/firestarter/lock_status.py` | LOCK-02/03/04 response classifier | ✓ VERIFIED | Exists, wired into `cli_handlers.py:86-89,1747-1820`. |
| `firestarter_app/tests/test_lock_status_class_partition.py` etc. (7 new test files) | D-12 invariant + resolution + CLI + wire + citations + DATA-06 | ✓ VERIFIED | All 90 tests across the 7 files ran green independently. |
| `firestarter/include/firestarter.h` `CMD_LOCK_STATUS=16` + `is_memory_cmd()` | wire command + safety gate | ✓ VERIFIED | Read directly; native `test_cmd_admission` (6/6) and `test_pinmap_provisional` (11/11, incl. the `CMD_LOCK_STATUS`-specific leg) both pass. |
| `firestarter/src/proms/flash_5v_page.cpp` / `flash_nor_unlock.cpp` protection-read handlers | LOCK-02 sequences | ✓ VERIFIED | Read directly; both implement the D-08 raw-byte + decode-byte two-byte DATA frame exactly as `151-DESIGN.md` §1 specifies, both explicitly never emit a state on an unrecognized byte (0xFF sentinel, `response_code = WARNING`). |
| `firestarter_app/doc/infoic-field-dictionary.md` §"protect_off_before / protect_on_after" | DATA-06 single authoritative statement | ✓ VERIFIED | Read directly, matches D-13/D-14/D-15 word for word (measurement, capability-not-policy framing, no-consumer statement). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `cli_handlers.py` `dev_lock_status` | `protection_readability.protection_gate` / `lock_status.classify_protection_response` | direct import + call | ✓ VERIFIED (manual code read) | `cli_handlers.py:86-89` imports; body calls the gate then the classifier then `render_lock_status`. |
| `protection_gate_for_entry` | `db.get_eprom()` (never `resolve_chip()`) | `protection_gate()` wrapper | ✓ VERIFIED | `protection_readability.py:340-347`; `test_protection_resolution.py` covers the hard-fail on a `protocol-id`-less (programmer) dict. |
| `firestarter.cpp` dispatch | `flash_5v_page`/`flash_nor_unlock` protection handlers | `CMD_LOCK_STATUS` switch arm | ✓ VERIFIED | `firestarter.cpp:353-354`; both `configure_*` functions arm `CMD_LOCK_STATUS` in their own switch. |
| **Automated `verify.key-links` gate** | plan-declared key_links | `gsd-tools query verify.key-links` | ⚠️ VACUOUS (see note) | Returns `{total:0, all_verified:true}` for every 151 plan I checked (e.g. `151-13-PLAN.md`). The plans' `key_links:` blocks are free-text prose sentences, not the `{from,to,via}` structured shape the verb expects — a schema mismatch, not evidence of missing wiring. I verified the actual wiring by hand instead (rows above); the gate itself is not a reliable oracle here. **Not a phase defect** — a pre-existing tooling gap affecting how this verb consumes free-text key_links. |

### Data-Flow Trace (Level 4)

Not applicable in the usual sense (no dashboard/UI rendering a fetched value) — the phase's
"data flow" is `chip_database.json` → `protection_gate_for_entry` → `lock_status` classifier →
CLI echo, and → firmware silicon read → wire → same classifier. Traced end to end in the Key
Link table above and confirmed live on real hardware in `151-BENCH.md` (leg B unforced/forced
runs show a real chip name flowing through to a real refusal/probe render, not a static stub).

### Behavioral Spot-Checks / Probe Execution

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| AST gate rejects a permit-by-default fixture | `FIRESTARTER_PROTECTION_READABILITY_SRC=tests/fixtures/planted_protection_permit_by_default.py python tools/check_protection_readability_invariants.py` | exit 1, names Class 1a + 1b | ✓ PASS |
| AST gate rejects a widenable-tokenset fixture | same, `..._widenable_tokenset.py` | exit 1, names Class 2a + 2b | ✓ PASS |
| AST gate passes the real module | `python tools/check_protection_readability_invariants.py` | exit 0, `PASS: ... bound exactly once each` | ✓ PASS |
| MERGE-05 policy on committed cold-build logs | `check_size_baseline.py --policy merge05 --baseline size_baseline_base01.json --avr-log ...` (3 logs) | exit 0, figures match claim exactly | ✓ PASS |
| Native admission truth table | `pio test -e native -f "*cmd_admission*"` | 6/6 PASSED | ✓ PASS |
| Native pinmap refusal (no CI leg — local-only per design) | `pio test -e native_pinmap_provisional` | 11/11 PASSED incl. `..._refuses_cmd_lock_status` | ✓ PASS |
| Native full env (`native`, `native_nodevtools`) | `pio test -e native` / `-e native_nodevtools` | 163/163 both | ✓ PASS |
| Full host suite | `pytest tests/ -o addopts="-ra"` (py3.11) | 1806 passed, 207.86s | ✓ PASS |
| Bench: chip-ID positive control | `firestarter id W29C020` (leg A) | `0xDA45`, exit 0 | ✓ PASS (per `151-BENCH.md`, not independently re-run — hardware) |
| Bench: `0x05` unforced/forced probe | `dev lock-status W29C020 [--force]` (leg B) | `undocumented_alias` / `unadjudicated_probe`, raw `0xFE` | ✓ PASS (per `151-BENCH.md`, not independently re-run — hardware) |

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|---|---|---|---|
| LOCK-01 | 151-09 | ✓ SATISFIED | `[x]` in REQUIREMENTS.md; table + AST gate exist and pass. |
| LOCK-02 | 151-13 | ✓ SATISFIED | `[x]`; CLI command, wire frame, firmware sequences, channel gate all verified. |
| LOCK-03 | 151-13 | ✓ SATISFIED | `[x]`; four refusal tokens verified to route through CLI without opening a port for the refused case. |
| LOCK-04 | 151-13 | ✓ SATISFIED | `[x]`; structural unreachability of `protected`/`unprotected` from the pure module, proven by AST gate + planted fixture. |
| DATA-06 | 151-07 | ✓ SATISFIED | `[x]`; doc section + tests verified. |

**No orphaned requirements.** Every PLAN's `requirements:` frontmatter array was cross-checked
against REQUIREMENTS.md's phase-151 traceability rows (LOCK-01…04, DATA-06) — all 5 accounted
for, exactly once each, by the plan the ROADMAP names (`151-07` DATA-06, `151-09` LOCK-01,
`151-13` LOCK-02/03/04). Every other plan carries `requirements: []` + an `advances:` key, as
required by the "no early/duplicate flip" discipline stated in ROADMAP.md's Phase 151 section —
confirmed by reading all 14 PLAN frontmatter blocks directly.

### Anti-Patterns Found

None. Scanned every source file this phase touched
(`protection_readability.py`, `lock_status.py`, `check_protection_readability_invariants.py`,
`cli_handlers.py`, `sdp_honesty.py`, `eprom_operations.py`, `flash_5v_page.cpp`,
`flash_nor_unlock.cpp`, `firestarter.h`, `firestarter.cpp`) for `TBD`/`FIXME`/`XXX`/`TODO`/
`HACK`/`PLACEHOLDER` — zero matches. No bare `except:` in the pure module (enforced by the AST
gate's Class 1(b), also confirmed by direct read). No hardcoded empty return masquerading as a
real answer — every refusal path names a reason string.

### Findings on the Two Weak-Gate Concerns Raised

1. **`verify.key-links` returning `total:0`.** Confirmed real: every 151 PLAN's `key_links:`
   entries are free-text sentences, not `{from,to,via}` triples, so the verb finds nothing to
   check and reports vacuous green. This is a **tooling/schema gap**, not evidence the actual
   wiring is broken — I verified the described links by direct code reading instead, and all of
   them hold. Recorded as an informational finding, not a phase-151 defect (the plans predate
   and are consistent with how every other 151 plan was authored; this is a project-wide
   convention question for the planning tooling, out of this phase's scope to fix).

2. **`check_protection_readability_invariants.py` ignoring argv.** Confirmed real: running
   `python tools/check_protection_readability_invariants.py --anything-goes-here` silently
   drops the argument and scans the default target, printing `PASS: scanned
   ../firestarter/protection_readability.py; ...`. This is a genuine fail-open risk *if* a
   future caller assumed a CLI path argument works — but (a) it is the same convention as three
   pre-existing gates in this codebase (`check_sdp_capability_invariants.py`,
   `check_devtest_orchestrator.py`, `check_is_memory_cmd_no_ifdef.py`), all using the identical
   env-var-only seam, so it is a known, established pattern rather than a new defect introduced
   by this phase; and (b) the PASS line does name the resolved target path, so a human reading
   the output (not blindly trusting exit 0) would catch the mismatch. My assessment: **adequately
   mitigated for this phase's own test suite** (which correctly uses the env-var seam, never
   argv), but the convention itself remains a latent risk for any *future* reuse that assumes
   argv works — worth a backlog note, not a blocker for this phase.

Neither finding blocks the phase goal; both are recorded as informational for future work.

### Human Verification Required

None. All must-haves are either directly code/test verified or corroborated by the
operator-witnessed bench record (`151-BENCH.md`), which is itself an artifact I read and
found internally consistent with the design's evidence-ceiling constraints (no overreaching
claims, D-03/D-08's caps explicitly restated per leg).

### Gaps Summary

No gaps. All 5 ROADMAP success criteria and all cross-referenced PLAN must-haves are backed by
code that exists, is substantive, is wired, and — where the claim is testable — passes when run
independently in this session. The two "weak gate" observations above are recorded as
informational findings, not gaps: I independently verified the underlying claims by other means
in both cases.

---

*Verified: 2026-08-20T19:30:08Z*
*Verifier: Claude (gsd-verifier)*
