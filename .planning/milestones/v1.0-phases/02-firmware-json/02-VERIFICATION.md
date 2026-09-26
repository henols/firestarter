---
phase: 02-firmware-json
verified: 2026-05-12T09:57:00Z
status: passed
score: 1/1 must-haves verified
overrides_applied: 0
requirements_verified:
  - REQ-SER-02
---

# Phase 02: Firmware JSON Protocol Extension — Verification Report

**Phase Goal:** "Extend the firmware JSON parser to forward-compatibly tolerate new Python wire fields without aborting or corrupting the parse. Any unrecognised JSON key — at the top level or inside a nested `bus-config` object — must be skipped cleanly and parsing must continue, so future Python-side additions never break older firmware."
**Verified:** 2026-05-12T09:57:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The firmware JSON parser silently skips unknown keys at BOTH parse sites (top-level `json_parse` and nested `parse_bus_config`) without aborting or corrupting state (REQ-SER-02) | VERIFIED | Top-level skip at `firestarter/src/json_parser.c:316-318` (`} else { // Unknown field — skip key + value token (forward-compatible with new Python fields) ⏎ token_idx += 2; }`); nested skip at `:251-255` (`} else { // Unknown key — skip key + value tokens ⏎ total_consumed_tokens += 2; ⏎ current_token_idx += 2; }`). Both sites advance by exactly 2 tokens (key + value) and continue the parse loop — no `return -1`, no `goto error`. |

**Score:** 1/1 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/src/json_parser.c` | Unknown-key skip in `json_parse` (top-level) and `parse_bus_config` (nested) | VERIFIED | Both skip blocks live in the file; `grep -n "Unknown" firestarter/src/json_parser.c` returns the two lines `:129` (top-level comment) and `:252` (nested comment), each followed by `token_idx += 2;` / `current_token_idx += 2;` token-advance. Function entry points: `json_parse` at `:77`, `parse_bus_config` at `:193`. |

The single-file delivery is intentional — REQ-SER-02's entire scope is the unknown-key-skip behavior inside the firmware parser; no cross-file wiring is in play.

---

### Key Link Verification

(No cross-file link rows — REQ-SER-02 is a single-file behavioral guarantee inside the firmware parser. Future Python wire-field additions exercise the skip; the wiring runs `Python emitter → JSON text → firmware tokenizer → unknown-key branch` and is verified end-to-end every time `check_dispatch.py` runs against the current DB.)

---

### Behavioral Spot-Checks

(All commands cited from existing verification artifacts — Phase 3 does not re-run per CONTEXT.md D-09 / RESEARCH.md Pitfall #3.)

| Behavior | Command | Result | Cited From |
|----------|---------|--------|------------|
| `pio test -e native` Unity dispatch suite (15 cases) — exercises `json_parse` indirectly via test setup | `cd firestarter && pio test -e native -f "*test_dispatch*"` | 15/15 PASS | `12-VERIFICATION.md` Truth #6 |
| Native Phase 1 suite (25/25 PASS) — confirms parser + post-SAF-04/05 helpers all link/run together with the unknown-key skip in place | `pio test -e native` (full) | 25/25 PASS | `01-VERIFICATION.md` (v1.1) Truth #5 |
| `check_dispatch.py` PASS on 743 chips — every wire-payload Python emits round-trips through the parser, including any forward-compat field | `python3 firestarter_app/tools/check_dispatch.py` | exit 0 | `02-VERIFICATION.md` (v1.1) SC4 + `12-VERIFICATION.md` Truth #5 |
| `pio run -e uno`, `pio run -e leonardo` — confirms the parser compiles clean with the skip branches retained | `cd firestarter && pio run -e uno` / `... -e leonardo` | both SUCCESS | `12-VERIFICATION.md` Truth #7 |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-SER-02 | 02-01 | Unknown JSON keys are skipped at both parse sites (top-level + nested `bus-config`) without aborting the parse | SATISFIED | Top-level skip at `firestarter/src/json_parser.c:316-318`; nested skip at `:251-255`. Both blocks advance exactly 2 tokens and continue. Live `check_dispatch.py` PASS + `pio test` 25/25 PASS (cited) confirm forward-compat is intact under real wire-payload + nested `bus-config` shapes. |

REQ-SER-02 is the only Phase 02 requirement; SATISFIED.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | — | — | — | No debt markers introduced by Phase 02. The unknown-key skip is the established forward-compat idiom and matches the same pattern used by the C++ JSON parsers in other PlatformIO embedded projects. |

Note: the `_mv`-suffix wire-key flip at `:62`, `:74`, and `:309` (PROGMEM literal + dispatch-table row + getter body) is v1.1 Plan 02-01 milestone scope (WIRE-01) — out of the v1.0 Phase 02 scope captured here. v1.1 Phase 2's own `02-VERIFICATION.md` records that closure.

---

### Gaps Summary

No gaps. REQ-SER-02 is SATISFIED against the current source tree. The unknown-key skip pattern is identical at both parse sites and has not regressed across v1.1 Phase 1 (SAF-04/05 helper additions in sibling handler files) or Phase 2 (WIRE-01 wire-key flip in this same file). No `Cross-Milestone Closure` subsection is needed — REQ-SER-02 was PARTIAL in `v1.0-MILESTONE-AUDIT.md` only for verification-gap reasons (the audit lacked a formal `02-VERIFICATION.md` artifact); the wiring itself was always intact, as confirmed by current-tree grep.

---

_Verified: 2026-05-12T09:57:00Z_
_Verifier: Claude (gsd-verifier)_
