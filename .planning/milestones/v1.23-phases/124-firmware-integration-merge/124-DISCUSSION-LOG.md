# Phase 124: Firmware Integration Merge - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-31
**Phase:** 124-firmware-integration-merge
**Areas discussed:** The three MERGE-08 defects

---

## Gray-area selection

Four areas were offered. The operator selected **one**.

| Area | Description offered | Selected |
|------|---------------------|----------|
| Landing shape & surface | Squash vs true merge (criterion 1's proof hangs on it); whether `ad47c3b` lands now or in Phase 128 | |
| ARM build evidence | How the CI run URL + SHA is produced with no local ARM toolchain; MERGE-03 trigger vs Phase 128's `beta-build.yml` fold | |
| Pin-map refusal (MERGE-04) | Where the refusal lives so a native test can prove it; command scope; error id; how the `#error` is proven able to fire | |
| The three MERGE-08 defects | `write_checksums.cmake`; ARM `DEV_TOOLS`-off form; PY32_EXCLUDED population | ✓ |

**Notes:** The three unselected areas were resolved as Claude's-discretion defaults (CONTEXT.md
D-05…D-14), with the reasoning shown to the operator before CONTEXT.md was written. The operator
was offered a second chance to weigh in on any of them at the closing prompt and chose
"I'm ready for context".

---

## The three MERGE-08 defects

### Q1 — `write_checksums.cmake`

| Option | Description | Selected |
|--------|-------------|----------|
| Delete it | Zero consumers; `ad47c3b` already stops publishing checksums as debug output. Cost: re-authored later if the DFU installer wants image integrity. | ✓ |
| Wire it to the install image | Give it one consumer — post-build checksum of the `.hex`/`.bin`, tying into the Phase 127 DFU story. Cost: Phase 124 owns a build-output contract Phase 128 may rewrite. | |
| You decide | Claude picks based on whether the Phase 127 DFU installer actually consumes a checksum. | |

**User's choice:** Delete it
**Notes:** None.

---

### Q2 — ARM `DEV_TOOLS`-off

Context presented: shared code tests `#ifdef DEV_TOOLS`, so `DEV_TOOLS=0` would *enable* dev
tools; and `src/dev_tools.cpp` is absent from the ARM source list, so a `DEV_TOOLS` build would
fail to link.

| Option | Description | Selected |
|--------|-------------|----------|
| Comment only, in the defines block | State the omission is deliberate; the machine-checked half already exists via `check_cmake_manifest.py`'s required PY32_EXCLUDED reason line. | |
| Comment + CMake option, default OFF | `option(FIRESTARTER_DEV_TOOLS ... OFF)` adding both the define and the TU when ON. Cost: a switch that can enable dev tools in an ARM release image. | |
| Comment + hard CMake refusal | `if(DEFINED DEV_TOOLS) message(FATAL_ERROR ...)` — fails closed, produces an exit code. | |
| **Other (free text)** | *"im not sure i fully understand but the test must work in the same way for all platforms, so it must be fixed"* | ✓ |

**User's choice:** None of the three — the mechanism itself must be fixed.
**Notes:** Claude reflected the reading back in plain text before locking it: move from
presence-semantics (`#ifdef DEV_TOOLS`) to value-semantics (`#ifndef DEV_TOOLS / #define
DEV_TOOLS 0` + `#if DEV_TOOLS`), uniform across all four targets, with AVR needing no
`platformio.ini` change because `-D DEV_TOOLS` already expands to `=1`. Two cross-repo hazards
were checked and reported *before* the operator confirmed: `test_revision_constants_parity.py`'s
nesting parser counts `#if`/`#ifdef`/`#ifndef` alike (survives), but its header-guard detector
must be re-verified if the default block sits near the top of `firestarter.h`; and
`check_is_memory_cmd_no_ifdef.py` is unaffected. Operator confirmed the reading with "1, 2, yes".

---

### Q3 — Sequencing of the `#if DEV_TOOLS` conversion

Asked because "yes" to the two-part follow-up was ambiguous.

| Option | Description | Selected |
|--------|-------------|----------|
| Inside Phase 124 | Part of this phase, alongside the merge; MERGE-05/06 byte-identity claims must survive it. | ✓ |
| Merge first, then convert — both in 124 | Same phase, ordered: land + prove AVR unchanged, then convert with its own re-measure. | |

**User's choice:** Inside Phase 124
**Notes:** Recorded in CONTEXT.md D-03 with the mechanical consequence that it still cannot be
*inside* the MERGE-01 landing commit — that content is not on the branch being landed — so it is
necessarily a separate commit after the landing. That is forced by MERGE-01, not a re-litigation
of this answer.

---

### Q4 — `FLASH_ACR_LATENCY_1` → `FLASH_LATENCY_1` proof shape

| Option | Description | Selected |
|--------|-------------|----------|
| Compile-time assertion in `main.cpp` | Tie the chosen latency to the configured clock so a future clock change fails the ARM build. Only fires in CI. | |
| Fix + cited comment | Cite the reference-manual/SDK basis for "48 MHz ⇒ 1 wait state" and why the ACR mask was wrong. No new build machinery. | |
| You decide | Assertion if the SDK exposes the clock as a compile-time constant; cited comment otherwise. | ✓ |

**User's choice:** You decide
**Notes:** Recorded as CONTEXT.md D-04 with the discretion boundary stated explicitly.

---

## Claude's Discretion

- **Q4's proof shape** — assertion vs cited comment, resolved against whether the pinned SDK
  (`0ed2f4b`) exposes the clock as a compile-time constant.
- **The three unselected gray areas** — atomic landing shape (CONTEXT D-05/D-06/D-07), ARM CI
  evidence and its operator gate (D-08/D-09/D-10), and the pin-map refusal design
  (D-11/D-12/D-13/D-14). Each recorded as a locked default with its reasoning so downstream
  agents do not re-ask.
- Plan/wave decomposition and commit granularity; the provisional-macro and fragment-header names.

## Deferred Ideas

- `ad47c3b` (`feature/py32f071-release-assets`) — artifact rename + workflow slimming → Phase 128.
- A dedicated `MSG_ERR_*` id for the provisional-pin-map refusal — costs a meta `messages.toml`
  edit + codegen regen + host parity churn; reuse `MSG_ERR_NOT_SUPPORTED (0xA5)` for now.
- `DATA_BUFFER_SIZE=512` wire-visibility on the py32 (host chunks to 510) — check in Phases 127/128.
- The double ARM build on a `beta` push created by MERGE-03 + Phase 128's fold.
- The stale `[env:native_nodevtools]` "16-entry list" comments (carried from Phase 123).
