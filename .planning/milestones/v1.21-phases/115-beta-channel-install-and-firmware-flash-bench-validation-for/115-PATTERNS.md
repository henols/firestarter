# Phase 115: Beta Install & Firmware-Flash Bench Validation — Community Onboarding (close) - Pattern Map

**Mapped:** 2026-07-10
**Files analyzed:** 3 artifact classes (1 doc + N evidence records + Step-0 checklist)
**Analogs found:** 2 / 2 real files (the 3rd "file" is not a code artifact — see below)

## Scope note (read first)

This is a **VALIDATION + DOCS close phase**. It builds **zero source modules**.
The install/flash/channel-select feature (`firmware.py`, `cli_handlers.py`,
`avr_tool.py`, `config.py`) already exists and is only *invoked*, never modified.
The only new files are:

1. A community-facing markdown doc (`firestarter_app/doc/beta-testing-install.md`) — **create**.
2. Per-board bench evidence records (`chip-test/onboard-<board>.md`) — **create**, one per board.
3. The "Step-0 reachability check" is **NOT a code file** — it is a sequence of
   existing CLI commands (`pip index versions firestarter --pre`,
   `firestarter fw --list --pre -b <board>`). No script analog is forced; if the
   planner wants it captured, it belongs as a checklist section inside the doc or
   an evidence-record header, not a new `tools/` module.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/doc/beta-testing-install.md` | doc (operator-canonical) | transform (facts → onboarding narrative) | `firestarter_app/doc/community-validation.md` | exact (same doc home, two-layer pattern, hand-off target) |
| `chip-test/onboard-<board>.md` (×3: uno, leonardo, uno328pb) | evidence record | batch (capture bench run) | `chip-test/dev-test-w27c512.md` | role-match (evidence-record shape; content axis differs) |
| `firestarter_app/README.md` (§ pointer link) | doc (modify) | — | existing README install/beta section (lines 108–214) | in-place edit, not a new file |
| Step-0 reachability check | (not a file) | request-response | `firestarter fw --list --pre` CLI path | N/A — CLI invocation, no code analog |

## Pattern Assignments

### `firestarter_app/doc/beta-testing-install.md` (doc, create)

**Analog:** `firestarter_app/doc/community-validation.md` — same operator-canonical
doc home, stranger-oriented prose, ends by handing off to a sibling doc. This new
doc hands off INTO `community-validation.md` (the reverse direction, closing the loop).

**Doc-home + two-layer pattern:** all these live in `firestarter_app/doc/`
(operator-canonical); meta holds investigation-canonical. Confirmed dir contents:
`community-validation.md`, `protocol-id.md`, `protocol-flags.md`,
`package-details.md`, etc. New doc lands beside them.

**Structural pattern to copy from `community-validation.md`:**
- Lead paragraph that states the audience and the one-sentence purpose
  (community-validation.md:5-19: "`firestarter dev test <chip>` (v1.21) lets anyone
  with real hardware…").
- Tables for state/step matrices (community-validation.md:24-29, 150-156) — reuse
  for the per-board command/`.hex` matrix.
- Explicit "what this is NOT" framing (community-validation.md:12-19) — mirror for
  "this is not a chip write/verify" (ONBOARD-03 smoke-vs-write boundary).
- Fenced code excerpts for the exact commands a stranger runs.

**Content the doc MUST carry (from RESEARCH Q3/Q4/Q6 + D-09):**
- Per-board command sequence (fresh venv → `pip install --pre` → `fw -i -b <board>`
  → `fw` → `hw`). Source recipe: RESEARCH.md:195-209.
- Board → `.hex` → avrdude partno/programmer/baud table (RESEARCH.md:162-166):
  uno→`firestarter_uno.hex`/atmega328p/arduino/115200;
  leonardo→`firestarter_leonardo.hex`/atmega32u4/avr109/57600;
  uno328pb→`firestarter_uno328pb.hex`/atmega328pb/urclock/115200.
- avrdude prerequisite note: `>=7.0` needs no `-C` config path, `6.3` does;
  app auto-detects on PATH else `--avrdude-path` (RESEARCH.md:230-241).
- `/dev/ttyACM*` controller-identity gotcha — port numbers shuffle across replug
  (`feedback_verify_port_identity_each_task`); re-check which port is which board.
- Hand-off link into `firestarter_app/doc/community-validation.md` (the `dev test`
  graduation-ladder doc) as the closing section.

**README tone/reuse for the beta section** (README.md:108-214): the README already
has an "Installing the Firestarter Python Program", "Beta / Pre-release Channel",
"Channel selection matrix" (README.md:198-203), and a "⚠ No stability guarantees"
callout (README.md:207). Match that voice; do NOT duplicate the matrix — per D-09
the README gets only a **pointer link** to the new doc, not a copy (README is
~35 KB / 34940 bytes).

---

### `chip-test/onboard-<board>.md` (evidence record, create — one per board)

**Analog:** `chip-test/dev-test-w27c512.md` (Phase 112 evidence record). Same
`chip-test/` home, same shape: a human-readable verdict table at the top followed
by a fenced machine-readable JSON block.

**Verdict-table pattern** (dev-test-w27c512.md:1-10):
```markdown
# dev test -- w27c512
| Step | Verdict | Reason |
| ---- | ------- | ------ |
| id | OK | - |
```
Adapt the step column to the onboarding chain: `install`, `--version`,
`fw -i (resolved channel + asset)`, `avrdude flash+verify`, `fw (version+board)`,
`hw (live op)` — one row per ONBOARD-01/02/03 checkpoint.

**Machine-block pattern** (dev-test-w27c512.md:12-95): a fenced JSON object with
`schema_version`, `generated` timestamp, an `auto_capture` block (host_version,
fw_board_identity, hw_revision), and per-step `{op, verdict, reason}` entries.
For onboarding, capture the D-08 mandated fields instead:
- `host_version` — MUST read `3.0.0b11` (never a stale stable). This is the exact
  field the w27c512 record shows reading `"3.0.0b10"` (dev-test-w27c512.md:19) —
  the b11 bump is what this phase proves.
- resolved `fw -i` channel + downloaded asset name (e.g. `firestarter_uno.hex`).
- avrdude flash+verify raw return/output.
- smoke-op (`hw`) result.

**Honest-fallback discipline (D-05/D-08):** blank/failed fields recorded verbatim,
never a false green. The w27c512 record models this with `null` /
`"not measured"` (dev-test-w27c512.md:20-31, 86-88) rather than inventing values.
For uno328pb specifically, record the actual failure mode (timeouts, `0xff` drift,
brownout) and do NOT retry into a green — it is best-effort/advisory, not a gate.

**Note on the `.json` sidecar:** the Phase 112 pattern emits BOTH a `.md` and a
`.json` (`dev-test-w27c512.json`) because `dev test` auto-generates them. This
phase's onboarding records are **hand-authored bench notes**, not `dev test`
output — the planner may keep just the `.md` (with an embedded fenced JSON block
like the analog) rather than a separate `.json` sidecar. Grounded call, not forced.

---

### `firestarter_app/README.md` (modify — pointer link only)

**Not a new file; an in-place edit.** Add a one-line pointer to the new
`doc/beta-testing-install.md` in the existing beta/install area (README.md:108-214,
near the "Beta / Pre-release Channel" section at :123). Do NOT duplicate the
per-board table (D-09). Match the existing markdown-link style already used
throughout the README.

## Shared Patterns

### Operator-canonical two-layer doc home
**Source:** `firestarter_app/doc/` (community-validation.md, protocol-id.md, …)
**Apply to:** the new onboarding doc.
Operator-canonical docs live in the sub-repo `doc/`; meta holds investigation-
canonical. The onboarding doc is operator-canonical → `firestarter_app/doc/`.

### Evidence-record shape (verdict table + fenced JSON)
**Source:** `chip-test/dev-test-w27c512.md:1-95`
**Apply to:** every `chip-test/onboard-<board>.md`.
Top: a `| Step | Verdict | Reason |` table. Bottom: a fenced JSON block with a
`schema_version`, timestamp, capture fields, and per-step records.

### Honest-fallback over false green
**Source:** `chip-test/dev-test-w27c512.md` (`null` / `"not measured"` fields)
**Apply to:** all evidence records — blank/failed fields stay blank/failed; a flaky
uno328pb run is a recorded note (+ FUT item), not a silent pass (D-05).

### Invoke-don't-build (feature under test)
**Source:** `firestarter_app/firestarter/{firmware.py,cli_handlers.py,avr_tool.py,config.py}`
**Apply to:** the whole phase. Every mechanical primitive already exists and is
tested. The plan CALLS `firestarter fw -i -b <board>` / `fw` / `hw` on hardware —
it never edits these modules. (RESEARCH.md "Don't Hand-Roll" table, :279-287.)

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| Step-0 reachability "check" | request-response | — | Not a code file. It is existing-CLI invocations (`pip index versions firestarter --pre`, `firestarter fw --list --pre -b <board>` ×3). Capture as a checklist in the doc/evidence header, not a new module — no code analog is appropriate. |
| Release-cut runbook (Step 0) | ops/CI dispatch | — | Executed via `gh workflow run beta-release.yml` / `beta-build.yml` / `publish.yml` (operator-gated, D-03). CI/ops action, not a repo source file. Analog is the workflows themselves (`firestarter_app/.github/workflows/beta-release.yml`, `firestarter/.github/workflows/beta-build.yml`), which are invoked, not created here. |

## Metadata

**Analog search scope:** `firestarter_app/doc/`, `chip-test/`, `firestarter_app/README.md`,
`firestarter_app/.github/workflows/`, `firestarter/.github/workflows/`.
**Files scanned:** community-validation.md, dev-test-w27c512.md, README.md (grep),
plus RESEARCH.md's already-verified source references (no re-verification needed).
**Pattern extraction date:** 2026-07-10
</content>
</invoke>
