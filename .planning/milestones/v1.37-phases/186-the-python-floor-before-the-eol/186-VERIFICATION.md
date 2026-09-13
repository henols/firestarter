---
phase: 186-the-python-floor-before-the-eol
verified: 2026-09-12T09:40:00Z
status: passed
score: 8/8 must-haves verified
covered_files:
  - ".planning/REQUIREMENTS.md"
  - ".planning/ROADMAP.md"
  - ".planning/codebase/CONVENTIONS.md"
  - ".planning/codebase/STACK.md"
  - ".planning/codebase/STRUCTURE.md"
  - ".planning/notes/python-floor-decision.md"
  - ".planning/phases/186-the-python-floor-before-the-eol/186-01-PLAN.md"
  - ".planning/phases/186-the-python-floor-before-the-eol/186-01-SUMMARY.md"
  - ".planning/phases/186-the-python-floor-before-the-eol/186-02-PLAN.md"
  - ".planning/phases/186-the-python-floor-before-the-eol/186-02-SUMMARY.md"
  - ".planning/phases/186-the-python-floor-before-the-eol/186-03-PLAN.md"
  - ".planning/phases/186-the-python-floor-before-the-eol/186-03-SUMMARY.md"
  - ".planning/phases/186-the-python-floor-before-the-eol/186-04-PLAN.md"
  - ".planning/phases/186-the-python-floor-before-the-eol/186-04-SUMMARY.md"
  - ".planning/phases/186-the-python-floor-before-the-eol/186-REVIEW.md"
  - "firestarter_app/.planning/codebase/STACK.md"
  - "firestarter_app/firestarter/address_parser.py"
  - "firestarter_app/firestarter/cli_handlers.py"
  - "firestarter_app/firestarter/codec.py"
  - "firestarter_app/firestarter/config.py"
  - "firestarter_app/firestarter/diagnostic_report.py"
  - "firestarter_app/firestarter/eprom_info.py"
  - "firestarter_app/firestarter/eprom_operations.py"
  - "firestarter_app/firestarter/firmware.py"
  - "firestarter_app/firestarter/hardware.py"
  - "firestarter_app/firestarter/ic_layout.py"
  - "firestarter_app/firestarter/jp5_gate.py"
  - "firestarter_app/firestarter/main.py"
  - "firestarter_app/firestarter/serial_comm.py"
  - "firestarter_app/pyproject.toml"
  - "firestarter_app/tests/test_cap03_ack_layout_parity.py"
  - "firestarter_app/tests/test_dev_gate_reads_no_firmware_source.py"
  - "firestarter_app/tests/test_py32_packaging.py"
  - "firestarter_app/tests/test_python_floor_agreement.py"
  - "firestarter_app/tests/test_runtime_dependencies.py"
covered_digest: "v1:sha256:baaa6fad72128ebc523e33729c6363982879384a868dcca65d664a39bb6916eb"
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Decide whether 186-REVIEW.md's WR-01/WR-02/WR-03 warrant a filed backlog item (following this project's own precedent — 999.53, 999.61, 999.62 were all filed from prior phases' REVIEW.md WARNING findings), and whether the phase objective's overstated 'runtime refusal inside the shipped wheel' claim needs a corrective note anywhere."
    expected: "Either a backlog item is filed (e.g. successor to WR-01/02/03, analogous to 999.61/999.62) or an explicit operator decision is recorded that the pre-existing, out-of-charter entry-point defect is accepted as-is for now."
    why_human: "This is a scope/priority call (file work vs. accept as documented), not a mechanical check — the phase's own must-haves and the four ROADMAP success criteria are satisfied independently of this decision, but the review report currently has no successor artifact, unlike every comparable prior WARNING in this milestone."
---

# Phase 186: The Python Floor, Before the EOL — Verification Report

**Phase Goal:** The advertised Python floor and the type-checker stop disagreeing, decided ahead of the deadline rather than under it.
**Verified:** 2026-09-12T09:15:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `requires-python`, `target-version` and mypy's `python_version` agree, in one direction chosen deliberately | ✓ VERIFIED | `firestarter_app/pyproject.toml:12` `requires-python = ">=3.11"`; `:110` `target-version = "py311"`; `:137` `python_version = "3.11"`. All three CI pins (`ci.yml:53`, `ci.yml:112`, `beta-release.yml:52`) independently re-grepped: `python-version: '3.11'`. Direction (raise, not hold) recorded and justified in `python-floor-decision.md` §1. |
| 2 | The app's CI type-check passes at the chosen floor, measured in py3.11, not the devcontainer's 3.12 | ✓ VERIFIED | Ran `firestarter_app/.venv/ci-replica/bin/python --version` → `Python 3.11.16` (not the devcontainer's 3.12.14), then `.../python tools/check_mypy_watermark.py` → `checked 182 source files` / `mypy errors: 35 (watermark: 35)` / `OK: error count at watermark.` Independently re-run, not merely re-quoted from SUMMARY.md. |
| 3 | The reasoning is recorded somewhere a future reader will find it, not only in a commit message | ✓ VERIFIED | `.planning/notes/python-floor-decision.md` exists (155 lines): `## VERDICT` first, `## 1.` decision + 3 rejected alternatives, `## 2.` evidence (transcribed, matches `186-RESEARCH.md` figures), `## 3.` standing rule, `## 4.` successor (999.67, `2027-10-31`), `## 5.` named residual gap (`py32_dfu.py`). `firestarter_app/.planning/codebase/STACK.md:7` carries a working pointer to it for an app-repo-only reader. |
| 4 | Landed before **2026-10-31** | ✓ VERIFIED | All six phase commits dated 2026-09-12 (`git log` in `firestarter_app` and the meta repo), well ahead of the deadline. |

**Score:** 4/4 ROADMAP success criteria verified.

### Additional Plan-Level Must-Haves (representative sample, independently re-checked)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 5 | Classifier list trimmed to `:: 3.11` / `:: 3.12`, generic `:: 3` kept, no `:: 3.13` minted | ✓ VERIFIED | `grep -n "Programming Language :: Python"` → exactly 3 lines: generic, `3.11`, `3.12`. No `3.13`. |
| 6 | `# mypy_error_watermark = 35` byte-unchanged | ✓ VERIFIED | `pyproject.toml:156` unchanged, matches orchestrator's own measurement. |
| 7 | Runtime guard's two halves (version tuple + message) moved together, `noqa: UP036` survives | ✓ VERIFIED | `main.py:29-34`: `if sys.version_info < (3, 11):  # noqa: UP036` and the matching 3.11 message. Both halves agree with each other and with the metadata — this is the literal must-have text, and it holds. |
| 8 | Four-way fail-closed agreement gate installed, zero comments, no new dependency | ✓ VERIFIED | `tests/test_python_floor_agreement.py`: 7/7 passed (re-run independently), `grep -c '^[[:space:]]*#'` → `0`, `ruff check`/`ruff format --check` both green with the file in scope, `tomllib` import only (no `pyyaml`/`tomli`/`toml`). |

**Score:** 8/8 must-haves verified (4 ROADMAP success criteria + 4 representative plan-level must-haves; the full must-have sets across all four plans were also spot-checked and found consistent with SUMMARY.md claims — see Behavioral Spot-Checks below).

## The WR-01 Question (Specific Settlement Requested)

**Independently confirmed, in the actual codebase, not merely re-quoted from `186-REVIEW.md`:**

- `firestarter_app/firestarter/main.py:20` — `main = cli` (module-level re-export).
- `firestarter_app/pyproject.toml:88` — `firestarter = "firestarter.main:main"` (console-script entry point).
- `firestarter_app/firestarter/main.py:29` — the `sys.version_info < (3, 11)` guard sits inside `if __name__ == "__main__":` (line 29), which only runs when `main.py` is executed as a script — never when `main` (i.e. `cli`, a Click group) is imported and called directly, which is exactly what the generated console-script wrapper does (confirmed by reading the installed `/home/vscode/.local/bin/firestarter` wrapper: `from firestarter.main import main; ... sys.exit(main())` — no guard, no `__main__` block).

**Verdict: WR-01 does NOT falsify any phase must-have or ROADMAP success criterion. It is a true-but-narrower claim, describing a genuine pre-existing defect that is out of this phase's charter.**

Reasoning:

1. **The literal must-have text holds.** Plan 186-01's must-have is precise: *"The runtime guard's two halves move together... The `noqa: UP036` SURVIVES."* This is a claim about the guard's two halves (the version tuple and the message) staying internally consistent with each other and with the raised metadata — and they do, verified directly above. The must-have does not claim the guard is reachable via the packaged entry point.
2. **None of the four ROADMAP success criteria mention runtime-guard reachability, console-script wiring, or entry-point behavior.** They are about the four floor *statements* agreeing, the CI type-check passing at the floor, the reasoning being recorded, and landing before the deadline. WR-01 touches none of these.
3. **The defect predates this phase.** `186-REVIEW.md` itself notes: *"This predates this phase (the block had the same shape at `< (3, 9)` before)"* — confirmed by the shape of the guard (nested in `__main__`) being architecturally unchanged; this phase only changed the version number and message text inside it, which is exactly what its must-have promised.
4. **The phase's own objective prose overreaches.** Plan 186-01's `<objective>` describes wiring "the runtime refusal inside the shipped wheel" end-to-end — that specific clause is not true of the packaged console script, as WR-01 demonstrates. This is a real overstatement in the plan's narrative framing, distinct from its must-haves (which is the binding contract). On a claim-hygiene milestone this distinction matters, but it is prose describing intent, not a must-have or success criterion that was checked and passed falsely.

**What should carry it forward:** This project's own precedent (999.53 from v1.36's close, 999.61/999.62 from Phase 182's `182-REVIEW.md`) is to file a backlog item from an unresolved code-review WARNING rather than let it sit unaddressed. `186-REVIEW.md` (WR-01, WR-02, WR-03) currently has **no successor backlog item** — the review was appended after 186-04 (and hence after `python-floor-decision.md`) had already closed, so the note's own §5 residual-gap section could not have named it, and nothing since has. This is flagged as a human-verification item above: either file a backlog item (recommended, matching precedent) naming WR-01 (guard unreachable via console script) and WR-02 (the guard would crash on import before firing, on any interpreter between 3.9 and 3.10, because of unguarded PEP 604 syntax spread by this phase's own sweep) together, since WR-02 is a direct, if narrow, consequence of this phase's own commit `1ebc548` — or record an explicit operator decision to accept it. Not doing either leaves a genuine, phase-caused gap (WR-02, specifically) less visible than this project's own claim-hygiene standard otherwise holds every other phase to.

Note additionally that WR-02 is a shade sharper than WR-01: WR-01 is fully pre-existing (unreachable guard shape), but WR-02 — a bare `python main.py` on an unguarded-3.10-or-below interpreter now crashes with an unrelated `TypeError` while importing `cli_handlers.py`, before the guard's version check ever runs — is a new, if narrow, side effect of this phase's own `X | None` sweep (no module touched by the sweep declares `from __future__ import annotations`). This does not fail any must-have (no must-have asserts the guard fires correctly below 3.10 via direct script invocation), but it is worth the same human decision as WR-01.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/pyproject.toml` | 3 of 4 floor statements + trimmed classifiers + untouched watermark | ✓ VERIFIED | All confirmed by direct read. |
| `firestarter_app/firestarter/main.py` | Runtime guard, both halves raised, noqa intact | ✓ VERIFIED | Confirmed; see WR-01 discussion for reachability caveat (does not invalidate this artifact's own claim). |
| `firestarter_app/firestarter/cli_handlers.py` | `_load_validation_spec` modernised, noqa removed | ✓ VERIFIED | `grep -n "_load_validation_spec" -A2` shows `-> dict[str, Any]:` with no trailing noqa. |
| `firestarter_app/tests/test_py32_packaging.py` | 7 assertions unchanged, falsified prose gone | ✓ VERIFIED | `pytest` → 7 passed (re-run); `tomllib` count 0. |
| `firestarter_app/tests/test_python_floor_agreement.py` | 4-way gate, zero comments, no new dep | ✓ VERIFIED | Re-run: 7 passed; grep-confirmed zero comments, `tomllib`-only import. |
| `firestarter_app/.planning/codebase/STACK.md` | Corrected floor + pointer to note | ✓ VERIFIED | 3 sites read `3.11`; pointer to `python-floor-decision.md` present. |
| `.planning/notes/python-floor-decision.md` | FLOOR-03 record | ✓ VERIFIED | Read in full; all D-08 required sections present. |
| `.planning/codebase/STACK.md`, `STRUCTURE.md`, `CONVENTIONS.md` | Corrected floor claims | ✓ VERIFIED | Re-grepped; all name 3.11, no residual `3.9`/`py39` in `.planning/codebase/`. |
| `.planning/ROADMAP.md` | Backlog 999.67 with 2027-10-31 | ✓ VERIFIED | Confirmed present, correctly dated, cites the note and the gate. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `pyproject.toml` | `tools/check_mypy_watermark.py` | regex parse of watermark line, mypy run w/ no `--python-version` flag | ✓ WIRED | Independently re-ran; watermark gate reports 35/35 at 182 checked files. |
| `pyproject.toml` | `.github/workflows/ci.yml` | 4th floor statement read by the new gate | ✓ WIRED | `test_python_floor_agreement.py` reads both; 7/7 pass. |
| `firestarter_app/.planning/codebase/STACK.md` | `.planning/notes/python-floor-decision.md` | one-line pointer for an app-repo-only reader | ✓ WIRED | `test -f` confirms the path resolves from repo root. |
| `.planning/notes/python-floor-decision.md` | `.planning/ROADMAP.md` 999.67 | successor citation, both directions | ✓ WIRED | Both files cite each other by name; confirmed by direct read. |
| `pyproject.toml` (`[project.scripts]`) | `firestarter/main.py`'s runtime guard | packaged console-script entry point | ✗ NOT WIRED | See WR-01 discussion — confirmed independently; the guard the phase raised does not execute via the actual shipped entry point. Not a phase must-have failure (see verdict above), but recorded here as a genuine broken link discovered during verification. |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| FLOOR-01 | 186-01, 186-02, 186-03 | Floor and type-checker agree | ✓ SATISFIED | All four statements agree; fail-closed gate installed and green. |
| FLOOR-02 | 186-01, 186-03 | Applied before 2026-10-31 | ✓ SATISFIED | Landed 2026-09-12; proven at floor via `CI-REPLICA` instrument (per 186-03 SUMMARY, not re-run here — 6-8 min full-suite cost; the narrower mypy-watermark and gate-file re-runs above independently corroborate the same floor). |
| FLOOR-03 | 186-04 | Reasoning recorded for a future reader | ✓ SATISFIED | `python-floor-decision.md` verified directly, non-vacuous, all D-08 sections present. |

No orphaned requirements: `.planning/REQUIREMENTS.md` maps FLOOR-01/02/03 to Phase 186 only, and all three are claimed across the four plans' `requirements:` frontmatter fields.

### Anti-Patterns Found

None. `TBD|FIXME|XXX` scan across all 20 phase-modified files: zero hits. No new comments introduced anywhere in the diff (`git diff bffbba8..HEAD -- '*.py'` inspected for added `#` lines — every one is either a pre-existing comment surviving a reflow/relocation, verified against its prior form, or a `# noqa:` directive; the new gate file carries zero comments by design).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| All four floor statements read 3.11 | `grep` across `pyproject.toml` + `.github/workflows/*.yml` | `>=3.11` / `py311` / `3.11` / three `'3.11'` pins | ✓ PASS |
| mypy watermark gate passes at py3.11 | `.venv/ci-replica/bin/python tools/check_mypy_watermark.py` | `checked 182 source files`, `35 (watermark: 35)`, `OK` | ✓ PASS |
| `ruff check`/`ruff format --check` green | `.venv/ci-replica/bin/ruff check firestarter/ tests/`; `... format --check ...` | `All checks passed!`; `180 files already formatted` | ✓ PASS |
| New gate passes standalone | `pytest tests/test_python_floor_agreement.py -o addopts="" -q` | `7 passed` | ✓ PASS |
| Console-script entry point bypasses the guard | read `firestarter/main.py`, `pyproject.toml:88`, installed wrapper at `/home/vscode/.local/bin/firestarter` | `main = cli`; wrapper imports and calls `main()` directly, no `__main__` gate | ✓ PASS (confirms WR-01) |
| No debt markers in phase-touched files | `grep -nE 'TBD|FIXME|XXX'` over all 20 files | no output | ✓ PASS |

Full app test suite (2366 passed, ~6-8 min) not re-run in full during this verification — orchestrator's independent measurement accepted per instructions; the narrower gate/watermark/lint re-runs above corroborate the same floor state without requiring the full-suite cost.

### Probe Execution

Not applicable — this phase has no `scripts/*/tests/probe-*.sh` probes; it is a packaging/config/CI phase.

## Gaps Summary

No must-have gaps. All four ROADMAP success criteria and all sampled plan-level must-haves verify against the actual codebase, independently re-measured (not merely re-quoted from SUMMARY.md). The phase's own commits contain zero unresolved debt markers and zero newly-introduced source comments.

One item is routed to human verification, not because any must-have failed, but because it is a judgment call this phase's artifacts leave open: `186-REVIEW.md`'s WR-01 (pre-existing, guard unreachable via the packaged entry point) and WR-02 (a phase-caused, narrower regression — the sweep's `X | None` syntax now crashes import on sub-3.10 interpreters before the guard's own check runs) have no successor backlog item, unlike every comparable prior finding in this milestone (999.53, 999.61, 999.62). This does not block the phase's stated goal or its four success criteria, which concern the four floor *statements*, not entry-point wiring — but it is the kind of unresolved finding this project's own established practice files forward rather than leaves implicit.

---

_Verified: 2026-09-12T09:15:00Z_
_Verifier: Claude (gsd-verifier)_

## Human Verification Resolved (2026-09-12)

The single `human_verification` item — whether `186-REVIEW.md`'s WR-01/WR-02/WR-03 warrant a filed
successor — was put to the operator, who chose **file a backlog item**, matching this project's own
precedent (999.53, 999.61, 999.62 were each filed from a prior phase's REVIEW.md WARNING).

Resolved by commit `4685606e`:
- **Backlog 999.68** filed in `.planning/ROADMAP.md`, covering all three warnings with their
  measured evidence, an honest scope note on how narrow WR-01's practical exposure is, and the
  instruction to correct or account for the overstated claim when the work is picked up.
- **`186-01-SUMMARY.md`** carries an appended correction retracting the objective's "runtime
  refusal inside the shipped wheel" phrasing, recorded in the SUMMARY rather than by editing the
  plan, per `/workspaces/CLAUDE.md`.

Status advances `human_needed` → `passed`. No gaps.

### Fingerprint re-stamp (2026-09-12T09:40:00Z)

`covered_digest` was re-stamped after the human-verification resolution above, because two covered
inputs changed as a direct result of it: `.planning/ROADMAP.md` (backlog 999.68 filed) and
`186-01-SUMMARY.md` (the appended correction). Measured, not assumed — `git diff --name-only`
against the original verification commit `2ffb8b3c` names only those two covered files plus this
report and the UAT.

**No source file changed.** `firestarter_app` has no commits after `612aa69` and its tree is clean
but for the two pre-existing untracked datasheet PDFs, so every code-level measurement in this
report still stands on the bytes it was taken against. The re-stamp records that the covered set
moved for documentation reasons alone; it is not a re-verification, and none was needed.

Previous digest: `v1:sha256:5fb418ae…cff1cf91`
