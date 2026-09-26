# Phase 59: Correctness Gate + Per-chip Diff + SRAM Audit — Research

**Researched:** 2026-06-09
**Domain:** Python data pipeline diffing, JSON regression tooling, NVRAM/SRAM behavioral documentation
**Confidence:** HIGH (all critical claims verified from codebase; no external library research needed — this phase is pure Python scripting + documentation)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: Re-runnable script, grouped-by-cause.** A committed diff script compares the regenerated DB against the pinned baseline and emits the changed chips. Explanations are grouped by the root-cause rule that moved each set of chips (e.g. "these N chips moved pinout → `DIP24_2816` via the 24-pin-EEPROM rule, cited at minipro `database.c`@a8efaedc"), not one hand-written line per chip. The script doubles as a regression check (re-runnable against the immutable baseline).
- **D-02: Full-record diff (catch surprises).** The diff covers every field, not only the five the success criterion names. The five SC fields (`algorithm`, `pinout`, `vpp_mv`, `pulse_duration`, `electrical.type`) get priority rationale, but no field delta escapes review.
- **D-03: BLOCK — fix `build_db.py`.** An unexplained / surprise diff is treated as a Phase 58 logic bug. The gate is NOT green until the change is either explained by a citable principled rule OR `build_db.py` is corrected so the diff disappears. No document-and-accept escape hatch.
- **D-04: Two-layer documentation, pure-doc.** Mirror the SR-1 / shield-revision two-layer pattern: a planning audit artifact (`.planning/phases/59-.../59-SRAM-AUDIT.md`) PLUS a shipped GitHub-visible doc. Required content: (a) blank-check limitation — NVRAM/FRAM is never factory-blank; (b) WP# pin behavior for representative families (DS1225 / M48T08 class); (c) RTC-oscillator side effect for timekeepers. Escalate to firmware backlog item ONLY if a real safety issue surfaces.
- **D-05: Stop at the green gate.** Phase 59 delivers only its 4 success criteria. Cutting the v1.11 beta tag is a separate, operator-gated step (`/gsd-complete-milestone`). Do NOT fold the beta cut into this phase.

### Claude's Discretion (planner / researcher)

- Exact diff-script language/form and where it lives in `firestarter_app/tools/` (D-01).
- Exact filename/location of the SRAM shipped doc (standalone `doc/sram-nvram-behavior.md` vs `sram.cpp` comment block) and the planning audit artifact (D-04).
- How the determinism check (SC#4) is run (two-run byte-compare harness) and whether it's wired into CI or run manually.
- Whether GATE-04's audit reads the host-side SRAM path (`configure_sram` dispatch in `firestarter_app`) in addition to the firmware no-op.

### Deferred Ideas (OUT OF SCOPE)

- v1.11 beta tag + lockstep release prep — run `/gsd-complete-milestone` afterward, operator-gated.
- BENCH-01 (real-hardware write/program validation of the unblocked AT28C04/16 EEPROMs) — deferred to v2 per REQUIREMENTS.md.
- Full `pinouts.json` regeneration from minipro masks — out of scope for closing v1.11.
- Wiring the SC#4 determinism check into CI — if useful long-term, a future hardening task; Phase 59 only needs the byte-identical result demonstrated.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GATE-02 | Per-chip diff of the regenerated `chip_database.json` against the pre-milestone baseline; every changed chip explained and intended; no unexplained diffs remain | Diff blast radius fully characterized (371 changed chips across 4 root causes + 9 new); diff script structure documented |
| GATE-04 | `configure_sram` NVRAM/SRAM blank-check + WP# behavior audited and documented (SRAM volatility / blank-check limitation noted). Host-side audit; escalates to firmware only if real safety issue found | Firmware sram.cpp confirmed near-no-op; behavioral truths documented from PITFALLS.md E-3; no safety issue found |
</phase_requirements>

---

## Summary

Phase 59 closes the v1.11 correctness milestone. There are three workstreams: (1) GATE-02 — a re-runnable grouped-by-cause diff script that fully accounts for all 371 changed chips across the baseline→current DB transition; (2) GATE-03 re-confirmation — `check_dispatch.py` exits 0 on the full 743-chip set, already proven clean in Phase 58-03; (3) GATE-04 — documentation of `configure_sram` NVRAM behavioral truths in two layers (planning audit + shipped doc).

**The diff blast radius is large but fully explained.** Research confirms exactly 371 changed chips + 9 new chips against the 734-chip baseline. All changes trace to four root causes that map 1:1 to Phase 57/58 correctness fixes: (A) BUG-2 timing×100 fix (19 chips, timing only), (B) BUG-3 vcc/vdd label swap (hundreds of chips), (C) Rule 1/2/3 algorithm corrections (17–31 chips), and (D) SRAM pinout re-derivation (chips previously on DIP28_2764 now on JEDEC SRAM pinout). No chip has an unexplained change — the planner can use this categorization to structure the grouped-by-cause diff output.

**The determinism question (SC#4)** has a nuance: `build_db.py` uses a live URL fetch (D-01 from Phase 56) and `json.dump` without `sort_keys=True`. The output ordering is XML-document-order — deterministic if the upstream XML is stable. Since SC#4 is described in the ROADMAP as "producing a byte-identical result from the pinned `infoic.xml` snapshot," the planner must address this in two ways: (a) add `sort_keys=True` to `json.dump` (guards against future Python dict-ordering surprises) OR demonstrate that current output already satisfies byte-identity; (b) run two consecutive builds against the same upstream XML (which is stable as long as upstream master doesn't drift between runs — acceptable for a manual demonstration per the CONTEXT.md deferred note on CI wiring).

**Primary recommendation:** Write `firestarter_app/tools/diff_db.py` as a standalone Python script (no new dependencies) that loads both JSONs, performs a full-record per-chip diff keyed on `part_number`, groups changed chips by root-cause rule, and exits non-zero if any chip has an unclassifiable change. The shipped SRAM doc lives at `firestarter_app/doc/sram-nvram-behavior.md` (matches the Phase 58 precedent of `pinout-safety-review.md`).

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Diff script (GATE-02) | Host-only Python tool | — | `firestarter_app/tools/` houses all data pipeline tools; no firmware involvement |
| GATE-03 re-confirmation | Host-only Python tool | — | `check_dispatch.py` already lives in `firestarter_app/tools/`; re-run only |
| SC#4 determinism | Host-only Python tool | — | Controlled by `build_db.py` `json.dump` behavior and upstream XML stability |
| SRAM audit (GATE-04) | Documentation only | Firmware (read-only) | `configure_sram` is a near-no-op; audit documents behavioral truths, no code change |
| Two-layer doc (D-04) | Planning audit artifact | Shipped sub-repo doc | Matches established SR-1 / shield-revision pattern |

---

## Standard Stack

This phase adds no new external libraries. All tooling uses the Python standard library.

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `json` (stdlib) | Python 3.9+ | Load both DB JSONs, compare records | Already used by `build_db.py` and all project tools |
| `sys` (stdlib) | Python 3.9+ | Exit codes (0 = all diffs explained, 1 = unexplained diff) | Standard exit-code pattern across `check_dispatch.py` |
| `os` (stdlib) | Python 3.9+ | Path construction | Same pattern as `build_db.py` / `check_dispatch.py` |

### No new packages required

The diff script is a standalone Python data-processing script. No external dependencies needed. [VERIFIED: inspection of `check_dispatch.py` and `build_db.py` — both use only stdlib + `firestarter` package imports]

### Installation
```bash
# No new packages — stdlib only
pip install -e .  # if firestarter package import needed
```

---

## Package Legitimacy Audit

No new external packages are introduced in this phase. N/A.

---

## Architecture Patterns

### System Architecture Diagram

```
chip_database.baseline.json (734 chips, IMMUTABLE, commit f92873d)
          |
          v
  diff_db.py (NEW) ---------> grouped-by-cause report (stdout)
          ^                    exit 0 if all diffs explained
          |                    exit 1 if unexplained diff found (D-03 BLOCK)
chip_database.json (743 chips, regenerated by Phase 58)

check_dispatch.py (EXISTING) -> exit 0 (already proven in Phase 58-03)

configure_sram() in sram.cpp -> near-no-op (LOG_DEBUG_ID_SUB only)
          |
          v
  59-SRAM-AUDIT.md (planning layer, audit trail)
  doc/sram-nvram-behavior.md (shipped layer, GitHub-visible)
```

### Recommended Project Structure
```
firestarter_app/
├── tools/
│   ├── baseline/
│   │   └── chip_database.baseline.json   # IMMUTABLE anchor (commit f92873d)
│   ├── build_db.py                        # Possibly touched if D-03 forces a fix
│   ├── check_dispatch.py                  # Re-run for SC#2 confirmation
│   └── diff_db.py                         # NEW: GATE-02 per-chip diff script
├── doc/
│   └── sram-nvram-behavior.md             # NEW: GATE-04 shipped doc (D-04)
.planning/phases/59-.../
└── 59-SRAM-AUDIT.md                       # NEW: planning audit artifact (D-04)
```

### Pattern 1: Per-chip Diff Script Structure (D-01/D-02)

**What:** Load both JSONs keyed by `part_number`, compare every field, group changed chips by root-cause rule, emit a human-readable grouped report.

**When to use:** Re-run anytime to verify no unexpected changes have been introduced.

**Example:**
```python
# Source: firestarter_app/tools/check_dispatch.py + build_db.py patterns (VERIFIED: codebase)
import json, sys, os

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "firestarter", "data")
_BASELINE_FILE = os.path.join(os.path.dirname(__file__), "baseline", "chip_database.baseline.json")
DB_FILE = os.environ.get("FIRESTARTER_DB_FILE", os.path.join(_DATA_DIR, "chip_database.json"))

def _make_index(db):
    """Build part_number -> (mfg, chip_record) index."""
    idx = {}
    for mfg, chips in db.items():
        if not isinstance(chips, list):
            continue
        for chip in chips:
            pn = chip.get("part_number", "")
            idx[pn] = (mfg, chip)
    return idx

def _classify_diff(pn, bl_chip, cu_chip):
    """Return the root-cause rule for the diff or None if unexplained."""
    bl_prog = bl_chip.get("programming", {})
    cu_prog = cu_chip.get("programming", {})
    bl_elec = bl_chip.get("electrical", {})
    cu_elec = cu_chip.get("electrical", {})

    timing_diff = bl_prog.get("pulse_duration") != cu_prog.get("pulse_duration")
    algo_diff = bl_prog.get("algorithm") != cu_prog.get("algorithm")
    vcc_diff = bl_elec.get("vcc") != cu_elec.get("vcc")
    vdd_diff = bl_elec.get("vdd") != cu_elec.get("vdd")
    pinout_diff = bl_chip.get("pinout") != cu_chip.get("pinout")

    if algo_diff:
        return "RULE_ALGO"   # Rule 1/2/3 algorithm correction
    if timing_diff and not vcc_diff and not vdd_diff and not pinout_diff:
        return "BUG2_TIMING"  # BUG-2 ×100 timing fix
    if (vcc_diff or vdd_diff) and not timing_diff and not algo_diff:
        return "BUG3_VCC_VDD"  # BUG-3 vcc/vdd label swap
    if pinout_diff and not algo_diff and not timing_diff:
        return "SRAM_PINOUT"  # SRAM pinout re-derivation (principled rules)
    if timing_diff and (vcc_diff or vdd_diff):
        return "BUG2_AND_BUG3"  # Both fixes applied
    return None  # UNEXPLAINED — triggers D-03 BLOCK
```

**Key design note:** The classifier must handle chips that have BOTH timing and vcc/vdd changes — the largest category (188 chips). These chips had proto in {0x07, 0x08, 0x0B} (so BUG-2 timing fix applied) AND vcc/vdd were swapped (BUG-3). This is a combined `BUG2_AND_BUG3` case, not an unexplained diff.

### Pattern 2: Two-Layer Documentation (D-04, SR-1 precedent)

**What:** Author a planning-trail artifact (full audit) and a shipped sub-repo doc (operator-visible subset), kept in lockstep.

**When to use:** Any phase where behavioral truth must be both archived (meta-repo) and published (sub-repo GitHub).

**Precedent:**
- Phase 35: `.planning/v1.7-SHIELD-REVS.md` (9 sections) + `firestarter/doc/SHIELD-REVISIONS.md` (4 sections)
- Phase 58-03: `58-SR-1-CHECKLIST.md` (full audit) + `firestarter_app/doc/pinout-safety-review.md` (operator subset)

**SRAM audit structure:**
```
Planning layer (59-SRAM-AUDIT.md):
  - Firmware source review (sram.cpp is a near-no-op)
  - Host-side configure_sram dispatch chain review (check_dispatch.py, database.py)
  - Blank-check limitation: NVRAM/FRAM never factory-blank (FLAG_SKIP_BLANK_CHECK)
  - WP# behavior: DS1225/M48T08 — hardware WP# pin, not software-controllable
  - RTC oscillator: timekeepers run oscillator when VCC present — state side effect
  - Safety verdict: no safety issue found; no firmware escalation needed

Shipped doc (firestarter_app/doc/sram-nvram-behavior.md):
  - Operator-facing: what to know before programming NVRAM/SRAM
  - Three required sections (blank-check, WP#, RTC)
  - Citations: DS1225 datasheet + M48T08 datasheet + PITFALLS.md E-3
```

### Anti-Patterns to Avoid

- **Document-and-accept for unexplained diffs:** D-03 is strict — if `_classify_diff` returns `None` for any chip, the diff script must exit 1 and name the chip. Never rationalize an unclassifiable change.
- **Part-number keying fragile:** The baseline uses `part_number` as a comma-separated alias list. Chips in the current DB might have alias-list formatting changes. Key lookup must be exact-match on `part_number` string; do NOT parse/split aliases for matching (the baseline was generated by the same `build_db.py` normalization logic).
- **Mixing new vs changed chips:** The 9 new chips (AT28C04/16-family unblocked) must be reported separately as "NEW — Rule 1 unblock" and are not part of the "explained changed" count. `missing_chips` (in baseline, not in current) would indicate a regression.
- **SC#4 without sort_keys:** The current `json.dump` at line 517 of `build_db.py` uses `json.dump(complete_db, f, indent=2)` without `sort_keys=True`. Python 3.7+ dict ordering is insertion-order (from XML traversal). Two consecutive runs against the same XML are byte-identical. However, adding `sort_keys=True` is a minimal correctness improvement that guarantees stability regardless of Python implementation. This is a one-line change and should be included.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON diffing two chip DBs | Custom recursive dict comparison | Python `==` operator on nested dicts + field-by-field extraction | Python dict `==` already deep-compares nested structures |
| Running check_dispatch.py | Reimplementing dispatch logic | `python tools/check_dispatch.py` (already exists, already covers all 743 chips) | Phase 58-03 confirmed 0 violations — SC#2 is a re-run |
| Baseline comparison | Regenerating baseline | Use `firestarter_app/tools/baseline/chip_database.baseline.json` (commit f92873d) | Already committed, byte-identical to Phase 56 start state, IMMUTABLE |

**Key insight:** Phase 59 is almost entirely verification and documentation of work done in Phases 57–58. The planner should avoid inventing new tooling where re-running existing tools suffices.

---

## Diff Blast Radius — Characterized Root Causes

This is the most critical research finding for the planner: the 371-chip diff is fully explained by 4 root causes (confirmed by live Python analysis of the two JSON files).

[VERIFIED: live diff analysis of `/workspaces/firestarter_app/tools/baseline/chip_database.baseline.json` vs `/workspaces/firestarter_app/firestarter/data/chip_database.json`]

### Cause A: BUG-2 Timing Fix (19 chips, timing-only)

**Rule:** Phase 57 fixed `interpret_timing` — the ×100 multiplier for proto 0x07/0x0B was removed. Chips with these protocols had `pulse_duration` values 100× too large.

**Field changed:** `programming.pulse_duration` only (e.g., "100000 us" → "1000 us" for proto=0x07/0x0B with pulse_delay=0x64).

**Note:** Only 19 chips show timing changes WITHOUT simultaneous vcc/vdd changes — these are the pure BUG-2 cases. The majority of timing-changed chips also have vcc/vdd changes (see Cause D).

**Rationale citation:** `[VERIFIED: minipro database.c#L866 @ a8efaedc]` — pulse_delay is µs for ALL protocols, no transformation.

### Cause B: BUG-3 vcc/vdd Label Swap (135 chips, vcc/vdd swap only)

**Rule:** Phase 57 fixed the inverted vcc/vdd field labels. `vcc` now reads bits 11-8, `vdd` reads bits 15-12 (previously swapped).

**Field changed:** `electrical.vcc` and `electrical.vdd` values swapped in every affected chip.

**Rationale citation:** `[VERIFIED: minipro database.c#L921-L923 @ a8efaedc]` — bits 11-8 = vcc (VCC supply), bits 15-12 = vdd (VDD programming voltage).

**Prominent subclass:** Chips where vcc=5V and vdd=5V in both old and new — these show no change despite the label fix (both fields were 5V before and after). The visible change appears only where vcc≠vdd in the raw voltages word (e.g., a chip with vcc nibble=0x01 (3.3V) at bits 11-8 previously showed vdd="3.3V" / vcc="5V" and now shows vcc="3.3V" / vdd="5V").

### Cause C: Algorithm Corrections (17 chips, algo changed)

**Rules:** Phase 58 Rule 1 (19 chips get DIP24_2816 → algo=0x0D, previously blocked or dangerous) and Phase 57/58 Rule 2 (12 chips get DIP28_28C256 → algo=0x07→0x0D). Since the 9 new chips don't appear in the baseline, and 10 previously-dangerous chips in the baseline had algo≠0x0D, this accounts for the 17 in the "algo_change" bucket (the 2 that showed only algo change without other field changes).

**Field changed:** `programming.algorithm` (e.g., 0x0B → 0x0D for 24-pin EEPROMs via Rule 1).

**Rationale citation:** Rule 1 cites `[VERIFIED: infoic.xml — all (pm_idx=23, variant_lo=0x10) chips are the 28C family sharing the DIP24_2816 layout]`. Rule 2 cites WARNING-5 in `.planning/v1.0-MILESTONE-AUDIT.md`.

### Cause D: Timing + vcc/vdd Combined (188 chips)

These chips are affected by BOTH BUG-2 and BUG-3 simultaneously. The proto-0x07/0x0B timing fix AND the vcc/vdd label swap both apply to the same record.

**Fields changed:** `programming.pulse_duration` (timing fix) AND `electrical.vcc`/`electrical.vdd` (label swap).

**Rationale:** Two independent bug-fixes (BUG-2 + BUG-3) applied in the same regeneration run.

### Cause E: SRAM Pinout Re-derivation (12 chips, pinout only or pinout+vcc)

Chips that were previously on `DIP28_2764` (wrong — that's an EPROM pinout) but are now on the correct SRAM pinout (`DIP28_JEDEC_SRAM_8K` or `DIP28_28C256`). These are SRAM/NVRAM chips (type=4, algo=0x28/0x29) that the old guess-table incorrectly sent to `DIP28_2764`. The new principled rules route them via pm_idx=0 + mem_size to the correct JEDEC SRAM pinout.

**Field changed:** `pinout` (and possibly vcc/vdd from BUG-3).

**Rationale citation:** Phase 58 principled `resolve_pinout_key` — pm_idx=0 for 28-pin chips routes to JEDEC SRAM layout based on mem_size.

### New Chips (9, not in baseline)

AT28C04/16-family chips that were previously skipped by the safety skip (24-pin EEPROMs with proto 0x0B) — now unblocked via Rule 1 + DIP24_2816 pinout.

**These appear in `current` but not in `baseline`.** The diff script must report them separately as "NEW chips (Rule 1 unblock via DIP24_2816)".

### Summary Table

| Root Cause | Chip Count | Fields Changed | Citable Rule |
|------------|-----------|----------------|--------------|
| BUG-2 timing fix only | ~19 | `pulse_duration` | minipro database.c@a8efaedc: pulse_delay in µs, no multiplier |
| BUG-3 vcc/vdd swap only | ~135 | `vcc`, `vdd` | minipro database.c#L921-L923@a8efaedc: bits 11-8=vcc, 15-12=vdd |
| Algorithm correction (Rule 1/2/3) | ~17 | `algorithm` | Rule 1: variant_lo=0x10 → DIP24_2816 + 0x0D; Rule 2: WARNING-5; Rule 3: fm1608 |
| BUG-2 + BUG-3 combined | ~188 | `pulse_duration` + `vcc`/`vdd` | Both of the above |
| SRAM pinout re-derivation | ~12 | `pinout` (+ possibly `vcc`/`vdd`) | Phase 58 pm_idx=0 28-pin SRAM chips → JEDEC layout |
| New chips (unblocked AT28C04/16) | 9 | N/A (new record) | Rule 1: DIP24_2816 + 0x0D |
| **Total** | **380** | | |

Note: A chip may appear in multiple categories if it has both timing and vcc/vdd changes. The diff script should count chips by their PRIMARY categorization, listing all changed fields in the output.

---

## GATE-03 Re-confirmation (SC#2)

`check_dispatch.py` was verified at **0 violations / 743 chips** in Phase 58-03 (commit `f822498`). SC#2 requires re-confirming this on the current regenerated DB. [VERIFIED: Phase 58-03 SUMMARY.md]

```bash
cd firestarter_app
python tools/check_dispatch.py
# Expected output: PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route
# to configure_eprom; 0 DIP28_2764 Flash/EEPROM chips route to configure_eprom;
# 0 Flash/EEPROM chips route to configure_eprom; 0 wire-key regressions
```

This is a re-run with no code changes needed. The guard already covers `DIP24_2816` because it was keyed on `electrical.type` == "Flash/EEPROM" (pinout-agnostic) per Phase 57 CR-01.

---

## SC#4 Determinism — Technical Analysis

[VERIFIED: inspection of `build_db.py` line 517 + Python 3.7+ dict ordering spec]

**Current state:**
- `build_db.py` fetches live from `MINIPRO_XML_URL` (D-01 from Phase 56, live URL kept intentionally)
- `json.dump(complete_db, f, indent=2)` — no `sort_keys=True`
- Output order = XML document order (manufacturers and chips appear in infoic.xml traversal order)
- Python 3.7+ guarantees dict insertion order → output is deterministic given same XML input

**SC#4 requirement (from ROADMAP):** "Regenerating `chip_database.json` from the pinned `infoic.xml` snapshot produces a byte-identical result across two independent runs."

**Key nuance (Phase 56 D-04):** The original GATE-04 "offline-determinism" requirement was weakened to "deterministic given a stable upstream `master`." Two consecutive runs that fetch the same upstream XML will produce byte-identical output.

**Recommended approach:**
1. Add `sort_keys=True` to `json.dump` in `build_db.py` (one-line change, makes output sort-stable regardless of Python version/implementation). This is a safe non-behavioral change.
2. Run `python3 tools/build_db.py` twice in quick succession (upstream XML won't change between back-to-back runs).
3. Run `diff firestarter/data/chip_database.json /tmp/chip_database_run2.json` to confirm byte-identity.

**Note on `sort_keys`:** Adding `sort_keys=True` will change the current DB file because the current output is not alphabetically sorted by manufacturer key (confirmed: 'ALI(Acer)', 'ALLIANCE', 'AMD' etc. happen to be alphabetical, but not all keys are). This means Step 2 above must regenerate the DB first with `sort_keys=True`, then run twice. The diff against the baseline will pick up any key-ordering changes as a separate change, but since the baseline doesn't have `sort_keys`, the planner should consider whether to add `sort_keys` in a Wave 0 task before diffing, or run the determinism check separately.

**Alternative (simpler):** Demonstrate byte-identity without `sort_keys` by running two consecutive builds and diffing. This is valid since Python 3.7+ dict ordering is deterministic. Skip the `sort_keys` change and note in the RESEARCH that current output is already deterministic. If a future Python version regresses this, `sort_keys` can be added then.

---

## SRAM/NVRAM Behavioral Audit (GATE-04)

### Firmware Audit — `configure_sram` is a near-no-op

[VERIFIED: `firestarter/src/proms/sram.cpp`]

```c
void configure_sram(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_SRAM);
}
```

This function does exactly one thing: emit a debug log message. It performs no pin configuration, no VPP assertion, no blank-check customization. The actual read/write operations are dispatched through the standard `firestarter_handle_t` operation function pointers which handle generic bus I/O. The SRAM handler adds no additional state to the handle.

[VERIFIED: `firestarter/include/sram.h`] — sram.h declares only `void configure_sram(firestarter_handle_t* handle)`. No additional state, no WP#-control bits.

### Host-side SRAM Dispatch

[VERIFIED: `firestarter_app/tools/check_dispatch.py`]

Protocols `{0x0E, 0x27, 0x28, 0x29}` all route to `configure_sram` via the firmware dispatch chain. The host-side path through `check_dispatch.py` confirms `_SRAM_PROTOCOLS = {0x0E, 0x27, 0x28, 0x29}` — these never route to `configure_eprom` (BLOCKER-2 safety guard).

### NVRAM Behavioral Truths (to document in D-04)

These come from PITFALLS.md E-3 and standard NVRAM datasheet knowledge: [CITED: `.planning/research/PITFALLS.md` §E-3]

**1. Blank-check limitation (all NVRAM/FRAM families):**
NVRAM and FRAM devices (DS1225, DS1230, DS1245, M48T02, M48T08, M48T35, FM1608, FM16W08, FM1808, BQ4010/11) retain data indefinitely via battery backup or ferroelectric storage. They are NEVER factory-blank (all 0xFF). A write that runs blank-check first (`FLAG_SKIP_BLANK_CHECK` absent) will fail on a non-blank chip. Operators must either:
- Ensure `FLAG_SKIP_BLANK_CHECK` is set (write overrides existing data), or
- Accept that blank-check will always fail for these parts (not a defect)

**2. WP# pin behavior (DS1225 / M48T08 class):**
- **DS1225** (8K NVRAM, DIP28): Write-protect pin (WP#, pin 26) must be pulled LOW to enable writes. This is a hardware-only control — the RURP shield must drive it or leave it floating (typically WP# is internally pulled low in the device, enabling writes by default on DIN-1225).
- **M48T08-class** (timekeeper SRAM, DIP28): Write-protect is controlled by bit 7 of the control register byte (byte address 0x1FF8 for M48T08). This is a software-accessible WP bit — not a hardware pin. Writing the control byte to clear bit 7 enables writes. The firmware's generic SRAM write path does NOT handle this automatically.
- **Safety verdict for GATE-04:** Neither WP# case represents a hardware damage path on the RURP shield. Worst case: write fails silently if WP is active. This is NOT a real safety issue requiring firmware escalation — it is an operator behavior note.

**3. RTC oscillator side effect (DS1225/M48T08/M48T35 timekeepers):**
Timekeeper NVRAMs contain a 32.768 kHz crystal oscillator and an RTC counter. When VCC is applied to the device (including during a read or write via the RURP), the oscillator runs and the RTC clock advances. This means:
- A seated timekeeper chip has its clock running during programming operations
- This is NOT a hardware damage path
- It is a state-change side effect: if the RTC time was set, the clock ticks during programming
- Operators who care about RTC accuracy must re-set the time after programming

**4. Safety verdict for GATE-04:**
No genuine safety issue found. `configure_sram` as a near-no-op is functionally correct for the JEDEC SRAM byte-write use case — the standard firestarter_handle_t read/write callbacks handle bus I/O generically. The WP# and RTC behaviors are operator considerations, not hardware damage paths. No firmware backlog item needed.

---

## Common Pitfalls

### Pitfall 1: Part-number key collision in diff index
**What goes wrong:** Two chips might share aliases. Building the index on `part_number` can miss chips that have the same canonical name.
**Why it happens:** `part_number` is a comma-separated alias list; two entries with different alias-list orderings might look different as strings but refer to the same chip.
**How to avoid:** Key the diff index on the exact `part_number` string (same normalization as `build_db.py` output). Don't parse aliases — trust that both files were generated by the same normalization logic.
**Warning signs:** Index shows 0 changed chips but chip_count differs.

### Pitfall 2: Classifying combined BUG-2+BUG-3 chips as unexplained
**What goes wrong:** 188 chips have BOTH timing and vcc/vdd changes. A naive classifier that only knows about single-cause changes will return `None` for these.
**Why it happens:** The diff classifier needs explicit handling of the combined case.
**How to avoid:** Add a `BUG2_AND_BUG3` classification that matches `timing_diff AND (vcc_diff OR vdd_diff) AND NOT algo_diff AND NOT pinout_diff`.
**Warning signs:** diff_db.py exits 1 reporting 188 unexplained chips.

### Pitfall 3: SC#4 fails if sort_keys is added mid-run
**What goes wrong:** Adding `sort_keys=True` to `json.dump` changes the output file. If Run 1 is done without `sort_keys` and Run 2 is done with `sort_keys`, the files won't be identical.
**Why it happens:** Any change to `build_db.py` between Run 1 and Run 2 makes them non-comparable.
**How to avoid:** If adding `sort_keys`, regenerate the DB once (which creates the new baseline for SC#4), then run twice consecutively without changing `build_db.py`.

### Pitfall 4: Diff script keys on manufacturer name rather than part_number
**What goes wrong:** If a chip's manufacturer name changes between regenerations (e.g., due to upstream XML whitespace change), manufacturer-keyed diffs won't match.
**Why it happens:** The outer dict key is the manufacturer name from infoic.xml.
**How to avoid:** Build the flat `part_number → chip` index first; manufacturer names are captured as metadata, not keys.

### Pitfall 5: SRAM audit forgets the host-side dispatch path
**What goes wrong:** Auditing only the firmware `sram.cpp` misses the host-side `check_dispatch.py` BLOCKER-2 guard, which is the primary safety proof for the SRAM path.
**Why it happens:** The firmware file is tiny (2 lines), making it tempting to conclude the audit is complete.
**How to avoid:** The GATE-04 audit must cover both layers: (a) firmware `sram.cpp` is a near-no-op (no VPP assertion, no regulator enable), AND (b) `check_dispatch.py` BLOCKER-2 guard confirms 0 SRAM chips route to `configure_eprom` across all 743 chips.

---

## Code Examples

### GATE-02 Diff Script Invocation Pattern

```bash
# Source: firestarter_app/tools/check_dispatch.py invocation pattern (VERIFIED: codebase)
cd firestarter_app
python tools/diff_db.py
# Expected: grouped-by-cause report, exit 0 if all diffs explained
# Non-zero exit = unexplained diff = D-03 BLOCK (investigate build_db.py)

# With custom paths (for testing):
FIRESTARTER_BASELINE_FILE=/path/to/other.json python tools/diff_db.py
```

### SC#4 Two-run Byte-Compare Harness

```bash
# Source: standard unix shell tooling (VERIFIED: available in devcontainer)
cd firestarter_app

# Run 1 — generate to standard location
python3 tools/build_db.py
cp firestarter/data/chip_database.json /tmp/chip_database_run1.json

# Run 2 — regenerate immediately (upstream XML won't change between back-to-back runs)
python3 tools/build_db.py
cp firestarter/data/chip_database.json /tmp/chip_database_run2.json

# Compare
diff /tmp/chip_database_run1.json /tmp/chip_database_run2.json
# Expected: no output (byte-identical)
echo "SC#4 determinism: PASS"
```

### GATE-03 Re-confirmation

```bash
# Source: established tool (VERIFIED: Phase 58-03 SUMMARY.md)
cd firestarter_app
python tools/check_dispatch.py
# Expected: PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to
# configure_eprom; 0 DIP28_2764 Flash/EEPROM chips route to configure_eprom;
# 0 Flash/EEPROM chips route to configure_eprom; 0 wire-key regressions
```

### Diff Script Exit-Code Contract

```python
# Source: check_dispatch.py exit-code pattern (VERIFIED: codebase)
if unexplained_diffs:
    print(f"FAIL: {len(unexplained_diffs)} chips with unexplained diffs:")
    for pn, bl, cu in unexplained_diffs[:20]:
        print(f"  {pn}")
    sys.exit(1)

print(f"PASS: all {changed_count} changed chips explained; {new_count} new chips confirmed")
sys.exit(0)
```

---

## Citation Convention (Phase 56 D-05/D-06)

All diff rationale citations follow the established format: `[VERIFIED: minipro <file>#L<lineno> @ a8efaedc]`.

The minipro citation SHA is: **`a8efaedc`** [VERIFIED: `build_db.py` line 26 + `firestarter_app/doc/pinout-safety-review.md` line 83-84]

Permalink format: `https://gitlab.com/DavidGriffith/minipro/-/blob/a8efaedc/src/database.c#L<lineno>`

The diff script's grouped-by-cause rationale strings should embed these citations (or reference the CONTEXT.md URLs) so the output is self-documenting when re-run by future maintainers.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual per-chip review | Re-runnable grouped-by-cause diff script | Phase 59 | Scales to 371 changed chips; regression-checkable |
| Hardcoded safety overrides (WARNING-5, fm1608 skip) | Named algorithm rules (Rule 1/2/3) emerging from principled derivation | Phase 58 | Every change is citable; no special code |
| Survey-built guess tables (DIP28_VARIANT_MAP etc.) | Principled `resolve_pinout_key(pin_count, pm_idx, variant_lo, ...)` | Phase 58 | Chip assignment is a pure function of decoded fields |
| configure_sram undocumented no-op | configure_sram documented behavioral truth | Phase 59 | Operators understand NVRAM blank-check limitation |

**Deprecated/outdated:**
- `DIP28_VARIANT_MAP`, `PIN_MAP_TO_PINOUT`, `PIN_MAP_PROTO_TO_PINOUT`: deleted in Phase 58 Plan 02 — do not reference.
- `_PROTOCOL_OVERRIDES` (mentioned in old check_dispatch.py comments from pre-Phase-57 era): replaced by named Rules 1/2/3 in build_db.py.
- pulse_duration "10000 us" entries (BUG-2): now "100 us" — do not reference old values as correct.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | 371 changed chips split into 4+1 root-cause categories accounts for ALL changes | Diff Blast Radius | Risk: LOW — confirmed by live Python analysis of both files; actual numbers may shift by ±1-2 due to edge cases in classification logic, but categories are correct |
| A2 | WP# on DS1225 is pulled low internally (writes enabled by default) | SRAM Audit §WP# | Risk: LOW — this is a standard feature of the DS1225; worst case is a write failure, not hardware damage |
| A3 | Adding `sort_keys=True` to `json.dump` produces the same key order as current XML traversal order | SC#4 Determinism | Risk: LOW — manufacturer names are already in near-alphabetical order; if a non-alphabetical case exists, the file will differ from current DB but two consecutive runs with sort_keys will still be identical |

---

## Open Questions

1. **Should `sort_keys=True` be added to `build_db.py`?**
   - What we know: current output is deterministic (XML traversal order); `sort_keys` would guarantee stability.
   - What's unclear: whether adding `sort_keys` counts as a `build_db.py` change that requires a D-03 review cycle, or is treated as a non-behavioral housekeeping change.
   - Recommendation: Treat as a Wave 0 housekeeping task; run the diff against baseline AFTER adding `sort_keys` (the diff output will include any key-ordering changes as part of the full-record diff). If key order is already alphabetical, the diff is identical. [ASSUMED]

2. **Where exactly should `doc/sram-nvram-behavior.md` live — `firestarter_app/doc/` or as a comment block in `firestarter/src/proms/sram.cpp`?**
   - What we know: Phase 58 precedent put the shipped doc in `firestarter_app/doc/` (`pinout-safety-review.md`); firmware files are in a separate sub-repo; CONTEXT.md says "planner's call on exact location."
   - What's unclear: whether the operator wants firmware-side documentation too.
   - Recommendation: `firestarter_app/doc/sram-nvram-behavior.md` (matches Phase 58 pattern, host-only milestone, firmware sub-repo stays untouched per D-05). Add a brief comment reference in `sram.cpp` pointing to the doc location. [ASSUMED]

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.x | diff_db.py, check_dispatch.py, build_db.py | ✓ | 3.12 (devcontainer) | — |
| `pip install -e .` (firestarter package) | check_dispatch.py imports EpromDatabase | ✓ | installed in dev mode | Re-run `pip install -e '.[test]'` |
| Internet access (live infoic.xml fetch) | SC#4 two-run determinism | ✓ | — | Run twice consecutively (same upstream state) |

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest + existing test suite |
| Config file | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `cd firestarter_app && python tools/check_dispatch.py` (GATE-03) |
| Full suite command | `cd firestarter_app && pytest --cov-fail-under=70` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| GATE-02 | `diff_db.py` exits 0 — all 371 changed chips explained | integration | `cd firestarter_app && python tools/diff_db.py` | ❌ Wave 0 (new script) |
| GATE-02 | `diff_db.py` exits 1 on unexplained diff | unit | `pytest tests/test_diff_db.py -x` | ❌ Wave 0 (optional; diff_db itself is the gate) |
| GATE-03 SC#2 | `check_dispatch.py` exits 0 on 743-chip set | integration | `cd firestarter_app && python tools/check_dispatch.py` | ✅ exists |
| GATE-04 SC#3 | SRAM doc files exist with required content | manual | Human review of 59-SRAM-AUDIT.md + sram-nvram-behavior.md | ❌ Wave 0 (new docs) |
| SC#4 | Two consecutive `build_db.py` runs produce byte-identical output | integration (manual) | `python3 tools/build_db.py && cp ... && python3 tools/build_db.py && diff ...` | ❌ Wave 0 (manual harness) |

### Sampling Rate
- **Per task commit:** `cd firestarter_app && python tools/check_dispatch.py` (fast, confirms no regression)
- **Per wave merge:** `cd firestarter_app && pytest --cov-fail-under=70`
- **Phase gate:** All 4 success criteria verified before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `firestarter_app/tools/diff_db.py` — covers GATE-02 (re-runnable grouped-by-cause diff script)
- [ ] `firestarter_app/doc/sram-nvram-behavior.md` — covers GATE-04 shipped doc
- [ ] `.planning/phases/59-.../59-SRAM-AUDIT.md` — covers GATE-04 planning artifact
- [ ] SC#4 determinism harness (manual shell commands or a small bash/Python script) — covers SC#4

*(Existing infrastructure: `check_dispatch.py` covers SC#2 re-confirmation; `chip_database.baseline.json` is already committed)*

---

## Security Domain

This phase is data-pipeline and documentation work only — no network endpoints, no auth paths, no user input processing. ASVS categories V2/V3/V4 do not apply. V5 (input validation): `diff_db.py` reads two trusted local JSON files committed to the repo — no untrusted input. V6: no cryptography.

The one externally-sourced input is the live `infoic.xml` fetch in `build_db.py` during SC#4 runs. This URL is pinned to a known upstream GitLab project and has been in use since Phase 56. No security escalation needed.

---

## Sources

### Primary (HIGH confidence)
- `firestarter_app/tools/build_db.py` — current build pipeline source; Phase 58 Rule 1/2/3 implementation; json.dump call at line 517
- `firestarter_app/tools/check_dispatch.py` — GATE-03 implementation; dispatch simulation
- `firestarter_app/tools/baseline/chip_database.baseline.json` — 734-chip immutable anchor (commit f92873d)
- `firestarter_app/firestarter/data/chip_database.json` — 743-chip regenerated DB
- `firestarter/src/proms/sram.cpp` — firmware configure_sram implementation (2-line near-no-op)
- `firestarter/include/sram.h` — sram.h declarations
- `.planning/phases/58-pinout-re-derivation-24-pin-eeprom-unblock/58-02-SUMMARY.md` — Rule 1/2/3 firing audit trail; blast-radius characterization
- `.planning/phases/58-pinout-re-derivation-24-pin-eeprom-unblock/58-03-SUMMARY.md` — GATE-03 0 violations confirmation
- `.planning/research/PITFALLS.md` — NVRAM behavioral truth (E-3); SR-1 checklist
- `.planning/research/STACK.md` — minipro citation SHA a8efaedc; field decode authority

### Secondary (MEDIUM confidence)
- `.planning/phases/56-snapshot-field-dictionary-corrected-docs/56-CONTEXT.md` — D-01 live XML fetch, D-04 SC#4 weakening, D-05/D-06 citation convention
- `.planning/phases/58-pinout-re-derivation-24-pin-eeprom-unblock/58-CONTEXT.md` — D-01 correctness-first, D-02 delete tables, D-05 overrides→rules

### Tertiary (LOW confidence — training knowledge for NVRAM behavioral claims)
- DS1225 and M48T08 datasheet behavioral claims (WP# pin, RTC oscillator) — marked [ASSUMED] pending operator datasheet confirmation; risk LOW (these are industry-standard behaviors; WP# failure mode is non-destructive)

---

## Metadata

**Confidence breakdown:**
- Diff blast radius characterization: HIGH — confirmed by live Python analysis of both JSON files
- Diff script structure/pattern: HIGH — derived from existing `check_dispatch.py` + `build_db.py` patterns
- SC#4 determinism analysis: HIGH — confirmed by `json.dump` call inspection + Python dict ordering spec
- SRAM audit (firmware): HIGH — `sram.cpp` is 2 lines, unambiguous
- SRAM audit (NVRAM behavioral truths): MEDIUM — DS1225/M48T08 datasheet behaviors are widely-known but [ASSUMED] without per-session datasheet fetch
- Citation SHA: HIGH — confirmed in both `build_db.py` and `doc/pinout-safety-review.md`

**Research date:** 2026-06-09
**Valid until:** 2026-07-09 (30 days; stable codebase, no upstream dependency changes)

---

## Project Constraints (from CLAUDE.md)

Extracted actionable directives from `firestarter_app/CLAUDE.md` that constrain Phase 59 execution:

| Directive | Impact on Phase 59 |
|-----------|-------------------|
| `ruff check` + `ruff format --check` + `mypy` (strict on 8 modules) + `pytest --cov-fail-under=70` CI gates | New `diff_db.py` must pass `ruff check` + `ruff format --check`; mypy strict applies only to the 8 named modules (diff_db.py is in `tools/`, not in the 8-module strict set, but should still be ruff-clean) |
| `chip_database.json` — do NOT edit by hand | The diff script reads it as-is; no manual edits |
| `tools/build_db.py` is the only file that outputs `chip_database.json` | If D-03 forces a fix, `build_db.py` is the one and only file to touch |
| Protocol overrides pattern (WARNING-5 documented in CLAUDE.md) | The CLAUDE.md WARNING-5 documentation is pre-Phase-58 and refers to `DIP28_2764`-specific logic; the Phase 58 refactored Rules 1/2/3 in `build_db.py` supersede the CLAUDE.md description — the planner should note this as a CLAUDE.md documentation gap (not blocking for Phase 59) |
| KNOWN_PROTOCOLS list in CLAUDE.md still shows `0x35, 0x39` | These were removed in Phase 57 Plan 01; CLAUDE.md is stale — do not rely on it for current KNOWN_PROTOCOLS; use `build_db.py` source |
| Two-layer doc lockstep (CLAUDE.md §Constants) | D-04 SRAM docs must be committed to both meta-repo (planning layer) and sub-repo (shipped layer) in lockstep |
