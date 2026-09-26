# Phase 107: DOCS + GATE — Documentation & Non-Regression Close - Context

**Gathered:** 2026-07-02
**Status:** Ready for planning
**Mode:** `--auto` (single-pass; all gray areas auto-resolved to recommended defaults)

<domain>
## Phase Boundary

Milestone-closing phase for **v1.20 Protocol-Only Dispatch**. Two jobs, no new
behavior:

1. **DOCS (DOC-01):** Scrub the now-deleted `type`/`mem_type` axis out of the
   firmware documentation, and record — for future readers and pre-v1.20
   hosts — that the wire contract broke (the `type` field is gone) and that
   **every chip entry now requires a usable `algorithm`**.
2. **GATE (GATE-01, GATE-02, SAFE-01):** Re-run every non-regression gate and
   confirm green at close — proving the `mem_type` fallback removed in Phases
   105 (firmware) and 106 (host) was dead code for every real chip, and that
   over-voltage stays blocked.

**In scope:** documentation edits + verification runs only.
**Out of scope (do NOT change code behavior here):** any firmware/host logic
change; regenerating golden baselines; `FLAG_VPE_AS_VPP (0x10)` removal
(LEGACY-01, v2); `EPROM_LEGACY` naming (LEGACY-02, v2); the v1.16 canonical
`electrical.type` STRING (unrelated to numeric `mem_type` — must be preserved);
phantom / named-infeasibility dispatch arms.

</domain>

<decisions>
## Implementation Decisions

### Breaking-change record location
- **D-01:** Record the breaking wire-contract change (`type` field removed) and
  the "every chip entry needs a usable `algorithm`" requirement as a **dedicated
  section in both sub-repo READMEs** (`firestarter/README.md`,
  `firestarter_app/README.md`), plus a note in the agent-facing
  `firestarter/CLAUDE.md` / `firestarter_app/CLAUDE.md`. **Do NOT create new
  CHANGELOG.md files** — neither sub-repo has one; README is the established
  public-facing surface (roadmap wording: "sub-repo READMEs/changelog").

### Doc-scrub surface & depth
- **D-02:** The `type`/`mem_type` scrub is confined to **`firestarter/CLAUDE.md`**
  (dispatch narrative ~lines 21–62 describing steps 7–11 + the legacy `type`
  wire-field bullet ~line 90) and **`firestarter/doc/PROTOCOLS.md`**. Grep
  confirmed `firestarter/README.md`, `firestarter_app/CLAUDE.md`, and
  `firestarter_app/README.md` carry **no** `type`/`mem_type` wire references —
  those are verify-only (they still receive the D-01 breaking-change note, but
  need no scrub).
- **D-03:** In `firestarter/CLAUDE.md`, delete steps 7–11 and rewrite the
  dispatch narrative so `protocol == 0` (and any unrecognized arm) fail-closes
  to `configure_not_implemented()` (0xBB) — no `mem_type` fallback described.
  **Preserve the v1.16 `electrical.type` STRING semantics** (INV-08/INV-09 and
  the `electrical.type == "EEPROM"` derivations in PROTOCOLS.md are OUT of scope
  — do not touch them; only the *numeric* `mem_type` / `type`-wire references go).

### Gate-failure disposition
- **D-04:** If ANY non-regression gate surfaces a real regression — `diff_db.py`
  value change on a real chip, `check_dispatch.py` violation, golden-trace /
  dispatch-mirror mismatch, or a failing native/host test — **STOP and surface
  it as a blocking finding.** Do NOT auto-fix, silence, or regenerate baselines.
  The phase's entire purpose is to *prove* zero regressions; a red gate means
  Phase 105/106 introduced a defect that needs its own fix, not a close-phase
  paper-over.

### Golden-trace / baseline handling
- **D-05:** Golden register traces (`firestarter/tests/golden/stable-*.h`) +
  the dispatch-mirror guard are **RUN as-is for re-verification only — never
  regenerated** in this phase. Regenerating would erase the non-regression
  signal GATE-01 / SAFE-01 depend on.
  - **Naming clarification (from RESEARCH.md):** `stable-*.h` are VERSION-string
    fixtures; the real frozen dispatch vectors live in `test_frame_vectors.cpp`,
    run inside `pio test -e native`. `check_dispatch.py`'s own `_ALGO_MEM_TYPE`
    is an intentional verification-tool artifact — do NOT flag it stale.

### Post-research scope additions (operator-decided 2026-07-02)
- **D-06 — 0xAE codegen desync → RECONCILE NOW:** The retired
  `MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE)` constant still lives in the meta
  canonical `tools/catalog/messages.toml` and the host `messages.py` /
  `messages.toml` (firmware already clean from Phase 105). Operator chose to
  reconcile it **in this phase** so v1.20 closes with no `mem_type` residue
  anywhere: edit the canonical `messages.toml` to drop 0xAE, then **regenerate**
  `messages.py`/`messages.h` via `codegen.py` (NEVER hand-edit generated files —
  see [[reference_firmware_messages_h_is_codegen_generated]] /
  [[reference_codegen_ruff_clean_emitter.md]]). Verify the codegen drift gate is
  clean afterward. This is the one sanctioned CODE/codegen change in an otherwise
  docs+gate phase — scoped strictly to removing the dead 0xAE constant.
- **D-07 — GATE-02 pass bar = NO NEW regression vs `beta`:** Host `pytest` is
  not absolute-green on the branch — 1 pre-existing failure
  (`test_golden_file_matches`) plus pre-existing ruff/format dirt, all in files
  v1.20 never touched. GATE-02 passes iff **v1.20 introduced zero new
  failures/lint vs the `beta` baseline** (`git diff beta..HEAD` scope). The
  pre-existing red baseline is documented as prior debt, NOT fixed here.
- **D-08 — Extend the doc scrub to `firestarter_app/CLAUDE.md`:** RESEARCH found a
  live `"type": 1` wire example there, contradicting the earlier "host docs
  grep-confirmed clean" note. Fold this stale example into the DOC-01 scrub
  (D-02's surface now includes `firestarter_app/CLAUDE.md`). Re-grep both
  sub-repos for any remaining `type`/`mem_type` wire references at close.
- **D-09 — Breaking-change record template:** Both READMEs already carry a
  `## Breaking Changes (v1.10)` section — add a parallel `## Breaking Changes
  (v1.20)` section in the same style (net-new; neither README has a v1.20 entry yet).

### Claude's Discretion
- Exact prose of doc edits and section headings.
- Ordering of the gate runs (native `pio test -e native`, host `pytest`,
  `check_dispatch.py`, `diff_db.py`, golden/dispatch-mirror, constants parity,
  py3.11-target ruff/ruff-format/mypy).
- Whether to leave the **meta-repo** `/workspaces/CLAUDE.md` untouched — default
  is untouched (roadmap DOC-01 names only sub-repo docs); touch only if a
  dangling `mem_type` reference is discovered there.

### Reviewed Todos (not folded)
Three pending todos keyword-matched Phase 107 (score ≥ 0.4) but are **semantically
incompatible** with a docs-only, zero-regression close phase — folding any would
violate the CRITICAL scope guardrail and the milestone's "zero regressions"
mandate. Reviewed and **deferred**, not folded:
- **Skip VPP error/warning checks when VPP unused (reads/blank-checks)** (0.9) —
  a firmware *behavior* change; matched on generic words "gate/check/vpp".
- **avrdude MCU-detection fallback** (0.6) — a host recovery feature; out of scope.
- **COBS decoder frame-level deadline (WR-01)** (0.6) — a firmware transport
  change; out of scope.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Docs to edit / verify (DOC-01)
- `firestarter/CLAUDE.md` — dispatch narrative (steps 7–11 + `protocol == 0`
  fallback description) and JSON Wire Protocol field list (legacy `type` bullet).
  PRIMARY scrub target.
- `firestarter/doc/PROTOCOLS.md` — drop any numeric `type`/`mem_type` wire-field
  references; **preserve all `electrical.type` string content** (INV-08/09, EEPROM
  derivations — out of scope).
- `firestarter/README.md` — add breaking-change + `algorithm`-required record.
- `firestarter_app/README.md` — add breaking-change + `algorithm`-required record.
- `firestarter_app/CLAUDE.md` — verify-only (already `algorithm`-based); optional note.

### Non-regression gate tooling (GATE-01, GATE-02, SAFE-01)
- `firestarter_app/tools/check_dispatch.py` — dispatch-mirror / violation gate (expect 0).
- `firestarter_app/tools/diff_db.py` — `chip_database.json` value-diff gate (expect no real-chip change).
- `firestarter/tests/golden/stable-expected.h`, `firestarter/tests/golden/stable-baseline.h` — v1.16 golden register traces (run-only, D-05).
- `firestarter/CLAUDE.md` §Development Commands — `pio test -e native`, dual-repo constants parity.
- `firestarter_app/CLAUDE.md` — `pytest`, ruff / ruff-format / mypy (py3.11 target).

### Phase / milestone context
- `.planning/ROADMAP.md` — Phase 107 goal + success criteria; v1.20 scope/out-of-scope.
- `.planning/REQUIREMENTS.md` — DOC-01, GATE-01, GATE-02, SAFE-01.
- `.planning/phases/105-*/105-01-SUMMARY.md` — exactly what firmware removed (source of truth for the doc scrub).
- `.planning/phases/106-*/106-01-SUMMARY.md`, `106-02-SUMMARY.md`, `106-03-SUMMARY.md` — exactly what the host removed.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Gate scripts already exist** (`check_dispatch.py`, `diff_db.py`) — this phase
  RUNS them, it does not build them. No new tooling.
- **Golden trace headers** (`tests/golden/stable-*.h`) — run via the existing
  `pio test -e native` golden target; no regeneration (D-05).
- **Phase 105/106 SUMMARY files** are the authoritative list of what was deleted —
  use them to know precisely which doc lines are now stale, rather than re-deriving.

### Established Patterns
- **Dual-repo lockstep + constants parity** (`constants.py` ↔ `firestarter.h`) —
  the parity check is part of GATE-02.
- **py3.12-masks-CI-py3.11 trap** — validate `ruff check` + `ruff format --check`
  against the py3.11 target, not just the devcontainer's 3.12, before claiming CI green.
- **`messages.h` is codegen-generated** — not touched here, but any incidental
  doc reference to messages must not imply hand-editing.

### Integration Points
- Docs live in the two SUB-REPOS (`firestarter/`, `firestarter_app/`) — commits
  land INSIDE the submodules on the v1.20 milestone branch; gitlinks stay PINNED
  (do not bump per-phase). Meta-repo tracks only `.planning/`.

</code_context>

<specifics>
## Specific Ideas

- `firestarter/CLAUDE.md` currently states the `mem_type` chain is "retained as a
  backward-compatibility fallback" and lists steps 7–11 explicitly (lines ~28,
  ~49–62) plus a legacy `type` wire field (~line 90) — these are the exact
  passages now false and must be rewritten to the fail-closed reality.
- The breaking-change note should be explicit that **pre-v1.20 hosts emitting a
  stray `type` key remain safe** (firmware silently skips unknown JSON fields) —
  the break is that `type` no longer *does* anything, and a chip lacking
  `algorithm` is now refused in-host before any serial byte.

</specifics>

<deferred>
## Deferred Ideas

- **Meta-repo `/workspaces/CLAUDE.md` scrub** — out of scope (roadmap names only
  sub-repo docs); revisit only if a dangling `mem_type` ref surfaces there.
- **LEGACY-01 / LEGACY-02 (v2):** `FLAG_VPE_AS_VPP (0x10)` removal and
  `EPROM_LEGACY` naming cleanup — explicitly deferred to v2.

### Reviewed Todos (not folded)
- **Skip VPP error/warning checks when VPP unused (reads/blank-checks)** — firmware
  behavior change; belongs in a firmware milestone, not a docs/gate close.
- **avrdude MCU-detection fallback for blank-chip / wrong-firmware recovery** —
  host recovery feature; own phase.
- **COBS decoder frame-level deadline (WR-01)** — firmware transport hardening; own phase.

</deferred>

---

*Phase: 107-docs-gate-documentation-non-regression-close*
*Context gathered: 2026-07-02*
