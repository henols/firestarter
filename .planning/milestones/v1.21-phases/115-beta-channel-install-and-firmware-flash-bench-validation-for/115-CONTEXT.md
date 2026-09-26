# Phase 115: Beta Install & Firmware-Flash Bench Validation — Community Onboarding (close) - Context

**Gathered:** 2026-07-10
**Status:** Ready for planning

<domain>
## Phase Boundary

The v1.21 **close capstone** — a **VALIDATION + DOCS** phase that proves a
stranger on a fresh machine can go from zero to a working beta stack and reach
`firestarter dev test <chip>`, on real hardware, for every bench board (Uno,
Leonardo, uno328pb).

The full chain being validated: `pip install --pre firestarter` lands the
`3.0.0b11` prerelease → a bare `firestarter fw -i` (no `--stable`, no
`--firmware-version`) auto-routes to the `--pre` channel (D-23/D-24) → pulls the
board-matching `firestarter_<board>.hex` from the GitHub prerelease → avrdude
flashes + verifies → a smoke test (`firestarter fw` reports the beta version +
correct board, plus one minimal live protocol op) confirms the flashed beta
stack is alive.

**The install / flash / channel-select feature already exists and is NOT built
here:** `firmware.py` (`fetch_release_info(channel='pre')` pagination + board
`.hex` asset resolution), `cli_handlers.py` (`fw` 3-way `--pre`/`--firmware-version`/
`--stable` mutex + `_maybe_auto_route_to_pre` bare-`fw -i` auto-route,
D-23/D-24), `avr_tool.py` (avrdude wrapper). This phase runs that path on the
bench and documents it.

**Two deliverable classes:**
1. **Release engineering (Step 0 — this phase drives it):** publish `3.0.0b11`
   publicly on BOTH channels so the community path is reachable at all — land
   v1.20 + v1.21 onto `beta`, bump `3.0.0b10 → 3.0.0b11`, gitlink bump, changelog,
   PyPI `gh` dispatch, and a GitHub prerelease carrying a `firestarter_<board>.hex`
   asset per board. Scoped to the **beta publish only**.
2. **Bench validation + community doc:** per-board install→flash→smoke evidence
   records + a community-facing onboarding doc in `firestarter_app`.

**Explicitly NOT this phase:**
- **NOT** a full chip write/verify — the smoke test proves the stack is *alive*
  and speaks the protocol; proving a *chip* is `dev test`'s job.
- **NOT** the milestone git tag `v1.21`, the final `--no-ff` merge to `beta`, or
  the `/gsd-ship` / `/gsd-complete-milestone` ceremony — those stay a **separate
  operator-gated close step AFTER verification** (D-06).
- **NOT** building/altering the install/flash/channel-select feature (already
  shipped in a prior milestone).

**Requirements:** ONBOARD-01, ONBOARD-02, ONBOARD-03, ONBOARD-04
(`.planning/REQUIREMENTS.md:65-68`).

**Hardware-gated + operator-witnessed** (same shape as Phase 111).

</domain>

<decisions>
## Implementation Decisions

### Step-0 publish — scope & ordering
- **D-01 (LOCKED): This phase DRIVES the `3.0.0b11` release cut** — it is not a
  verify-only precondition. The phase's plan authors and runs the full
  release-engineering: land v1.20 + v1.21 code onto `beta` (lockstep across all
  three repos), bump `firestarter_app/firestarter/__init__.py` `3.0.0b10 →
  3.0.0b11`, gitlink bump from the PINNED b10, changelog / prerelease notes,
  trigger the PyPI publish (`beta-release.yml` via manual `gh` dispatch), and
  ensure the GitHub prerelease carries a `firestarter_<board>.hex` asset for each
  board (built by the firmware repo's `beta-build.yml`). Rejected: verify-only +
  halt (operator chose to fold the cut into this phase rather than treat it as an
  external precondition).
- **D-02 (LOCKED): Release cut is scoped to the BETA PUBLISH only.** In scope:
  everything needed to make both channels (PyPI `--pre` + GitHub prerelease with
  `.hex` assets) publicly reachable for Step 0. **Out of scope, deferred to a
  separate operator-gated close step:** the `v1.21` git tag, any final `--no-ff`
  merge to `beta`, and the `/gsd-ship` / `/gsd-complete-milestone` ceremony —
  those happen AFTER this phase's verification passes. See D-06.
- **D-03 (LOCKED): Irreversible/outward-facing publish steps get an explicit operator-authorization checkpoint at execution time.** The PyPI `gh` dispatch
  and the GitHub-prerelease publish are outward-facing and hard to reverse (PyPI
  versions cannot be re-used; a prerelease is public). The plan must pause for
  explicit operator go-ahead immediately before each, rather than firing them
  autonomously. (Standing "beta cuts are operator-gated" policy — folding the cut
  into the phase does not remove the human gate on the irreversible act.)
- **D-04 (LOCKED): Doc is draft-first, published in b11, then finalized from bench findings.** Write the ONBOARD-04 doc from known facts BEFORE the cut so
  `3.0.0b11` ships with it; run the per-board validation; fold any
  newly-discovered gotchas back into the doc as a repo update on the `beta`/v1.21
  branch (the community reads docs from GitHub/`beta` regardless of which pip
  build they installed). b11 is complete at publish; the doc still captures live
  findings.

### Per-board scope — uno328pb is best-effort
- **D-05 (LOCKED): Uno + Leonardo are HARD pass/fail gates; uno328pb is best-effort.** A flaky or failed uno328pb run is recorded (with the specific
  failure mode) but does NOT block milestone close — it becomes a known-instability
  note + a FUT item. Rationale: memory documents uno328pb as bench-unstable
  (`project_uno328pb_bench_instability_27_04`: read timeouts + 0xff drift, VPP
  misread, PROGRAM brownout) and once mis-identified as a plain Uno running the
  wrong firmware (`project_uno328pb_correction`). **`.hex` choice:** flash
  `firestarter_uno328pb.hex` (the board's own build env exists in
  `firestarter/platformio.ini`); if the physical third board proves to be a plain
  Uno, note that explicitly in the evidence record and use `firestarter_uno.hex`
  — never silently substitute. (Note: ROADMAP success criteria say "each bench
  board" incl. uno328pb; this decision keeps uno328pb in the sweep but downgrades
  its outcome from a close-blocker to advisory.)

### Milestone close ordering
- **D-06 (LOCKED): Close ceremony is a SEPARATE operator-gated step after verification.** Order within/after the phase: (1) draft doc → (2) release cut
  + publish b11 (D-01/D-02/D-03) → (3) per-board bench validation → (4) finalize
  doc from findings (D-04) → (5) phase verification → (6) **then** the
  operator-gated `v1.21` tag + final merge + ship/complete-milestone (NOT this
  phase's plan).

### Bench validation execution model
- **D-07 (LOCKED): Fresh-venv + `FIRESTARTER_CONFIG_DIR` isolation to make the "stranger on a fresh machine" claim credible.** Each per-board run uses a
  throwaway virtualenv (`pip install --pre firestarter` into it, NOT the
  operator's editable `-e` install) and points `FIRESTARTER_CONFIG_DIR` at a
  clean temp dir so `~/.firestarter` / any local DB override does not contaminate
  the test. Rejected: plain run on the dev bench (the existing `-e` package +
  config weaken the fresh-machine claim); container/VM (higher fidelity but USB
  passthrough friction not warranted — the venv+config-dir seam is sufficient and
  is the established v1.15/v1.21 pattern).
- **D-08 (LOCKED): One evidence record per board.** Each board gets its own
  markdown evidence artifact (e.g. `chip-test/onboard-<board>.md`, mirroring the
  `chip-test/dev-test-w27c512.md` pattern from Phase 112) capturing: the
  `firestarter --version` string (must be `3.0.0b11`, not a stale stable), the
  `fw -i` resolved channel + downloaded asset name, the avrdude flash+verify
  output, and the smoke-op result. Blank/failed fields are recorded honestly
  (never a false green), per the milestone's honest-fallback discipline.

### Community doc shape (ONBOARD-04)
- **D-09 (LOCKED): New standalone doc in `firestarter_app/doc/`** (operator-canonical
  home, two-layer doc pattern), written for a stranger on a fresh machine.
  Suggested name `firestarter_app/doc/beta-testing-install.md` (final name
  planner's call). Contents: exact per-board commands, the avrdude prerequisite,
  the `/dev/ttyACM*` controller-identity gotcha (port numbers shuffle across
  replug — `feedback_verify_port_identity_each_task`), the correct `.hex` per
  board, and the hand-off into `dev test <chip>` (link
  `firestarter_app/doc/community-validation.md`). The README gets a short pointer
  link, NOT a duplicated copy (README is already ~35 KB). Rejected: expanding the
  README install section (buries it in a large file); a section inside
  `community-validation.md` (that doc is the graduation-ladder/taxonomy home — the
  install/flash journey is a distinct concern).

### Smoke-test op (Claude's Discretion — grounded default)
- **Default: `firestarter fw` for version+board, then `firestarter hw` (hardware
  revision read / identify) as the one minimal live protocol op.** Explicitly NOT
  a chip write/verify (ONBOARD-03). Planner may pick `id`/identify instead if
  research shows it's the more universal minimal op. For uno328pb specifically,
  expect possible instability on the live op — record the outcome, don't retry
  into a false green (D-05).

### Claude's Discretion
- Exact venv/`FIRESTARTER_CONFIG_DIR` scaffolding mechanics (temp-dir layout,
  teardown) — planner's call within D-07.
- Evidence-record filename/template details within D-08.
- Doc filename + exact section ordering within D-09.
- Whether the firmware repo needs its own version tag alongside the app b11 cut,
  and how the `beta-build.yml` `.hex` assets attach to the GitHub prerelease —
  **flag as the likely `--research-phase 115` item** (release-mechanics /
  dual-repo lockstep + CI asset provenance).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & scope (this phase)
- `.planning/ROADMAP.md` — Phase 115 section (lines 360-374): goal, depends-on
  Phase 112 + Phase 114, the "Hard external precondition (Step 0)", 5 success
  criteria, and the "VALIDATION + DOCS only — the feature already exists" framing.
- `.planning/REQUIREMENTS.md:65-68` — ONBOARD-01 (fresh-venv `--pre` install +
  version reports b11), ONBOARD-02 (bare `fw -i` auto-route + board `.hex` flash+
  verify), ONBOARD-03 (post-flash smoke test, NOT a chip write), ONBOARD-04
  (community doc in `firestarter_app`).

### Reusable code — the feature being validated (firestarter_app/)
- `firestarter_app/firestarter/firmware.py` — `fetch_release_info(channel='pre')`
  (:226) paginates `/releases`, filters `prerelease=True` / `draft=False`, sorts
  by PEP 440, resolves `firestarter_{board}.hex` (:237); `_fetch_all_releases`
  (:194) pagination cap; `list_releases` (:319) channel filter. This is the
  channel-select machinery Step-0/ONBOARD-02 exercise.
- `firestarter_app/firestarter/cli_handlers.py` — `_maybe_auto_route_to_pre`
  (:200) + `_maybe_auto_route_to_pre_click` (:767): the D-23/D-24 bare-`fw -i`
  auto-route (beta-installed app → `--pre`); `fw` command (:854) 3-way
  `--pre`/`--firmware-version`/`--stable` mutex (:884).
- `firestarter_app/firestarter/avr_tool.py` — avrdude wrapper (`_find_avrdude_path`
  :57, `_get_avrdude_version` :50): the flash+verify executor; grounds the
  "avrdude prerequisite" doc note.
- `firestarter_app/firestarter/__init__.py:1` — `__version__ = "3.0.0b10"` (the
  string D-01 bumps to `3.0.0b11`; drives `firestarter --version`).

### Release engineering (Step 0 — D-01/D-02/D-03)
- `firestarter_app/.github/workflows/beta-release.yml` — the PyPI beta publish
  (manual `gh` dispatch per `reference_betarelease_ci_gotchas_v18`).
- `firestarter/.github/workflows/beta-build.yml` — the firmware per-board `.hex`
  build that feeds the GitHub prerelease assets.
- `firestarter/platformio.ini` — board build matrix: `[env:uno]` (:31),
  `[env:uno328pb]` (:40), `[env:leonardo]` (:57) → the `firestarter_<board>.hex`
  set (D-05 `.hex` selection).

### Doc home + hand-off target (ONBOARD-04)
- `firestarter_app/doc/` — operator-canonical doc directory (two-layer pattern);
  new onboarding doc lands here (D-09).
- `firestarter_app/doc/community-validation.md` — the graduation-ladder / DISP-01
  taxonomy doc (Phase 114); the onboarding doc hands off into it.
- `firestarter_app/README.md` — existing install doc (~35 KB); gets a pointer
  link only, not a duplicate (D-09).

### Analog phase (structure to mirror)
- `.planning/phases/111-measured-voltage-sampler-hardware-gated/111-CONTEXT.md` —
  the other hardware-gated + operator-witnessed phase; its software-complete /
  hardware-deferral framing, evidence discipline, and "isolate the hardware gate"
  shape inform this phase.

### Domain / bench facts (memory)
- `reference_betarelease_ci_gotchas_v18` — codegen drift vs ruff baseline;
  `.[dev]` vs `.[test]`; version/traceback snapshots; **PyPI needs a manual `gh`
  dispatch**; the skipped-version fw tag pattern. Directly grounds D-01.
- `project_uno328pb_correction` + `project_uno328pb_bench_instability_27_04` —
  uno328pb may be a plain Uno w/ wrong FW; bench-unstable (timeouts, 0xff drift,
  VPP misread, PROGRAM brownout). Grounds D-05.
- `feedback_verify_port_identity_each_task` — `/dev/ttyACM*` numbers shuffle
  across replug/board cycle; verify `controller:` identity per task. The doc's
  controller-identity gotcha + a bench-run discipline note.
- `project_v121_submodule_branch_base` + `project_v120_milestone_seed` — v1.21
  forked off v1.20 (NOT beta); v1.20's protocol-only-dispatch code + b11 cut +
  gitlink bump are operator-gated, gitlinks PINNED at b10. The lockstep-base
  context D-01/D-02 resolve.
- `feedback_stable_release_operator_gated` — nothing is stable until the operator
  says so; this phase publishes a BETA, never a stable. Reinforces D-02/D-03.
- `reference_firestarter_app_python_test_env` + the `FIRESTARTER_CONFIG_DIR` seam
  (`project_phase83_shipped`) — the config-dir isolation used in D-07.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **The entire install/flash/channel-select feature is the thing under test, not
  a thing to build** — `firmware.py` channel select + `.hex` asset resolution,
  `cli_handlers.py` `fw` + `_maybe_auto_route_to_pre` (D-23/D-24),
  `avr_tool.py` avrdude wrapper. The plan invokes these on real hardware.
- **`chip-test/` evidence-record pattern** (e.g. `chip-test/dev-test-w27c512.md`
  from Phase 112) — the per-board evidence artifacts (D-08) mirror this shape.
- **`FIRESTARTER_CONFIG_DIR` + fresh-venv seam** — the established way to isolate
  a run from the operator's `-e` install and `~/.firestarter` (D-07).
- **`beta-release.yml` (app, PyPI) + `beta-build.yml` (firmware, `.hex`)** — the
  two CI paths the Step-0 release cut drives.

### Established Patterns
- **Two-layer doc pattern** — operator-canonical docs live in the sub-repo
  (`firestarter_app/doc/`), meta holds investigation-canonical; the onboarding
  doc is operator-canonical (D-09).
- **Operator-gated, hardware-witnessed validation** — same shape as Phase 111;
  the operator adjusts hardware / witnesses runs, Claude drives serial where it
  can (USB passthrough), records honest evidence, never rubber-stamps a hardware
  result.
- **Honest-fallback over false green** — blank/failed evidence fields recorded as
  such; a flaky uno328pb run is a note, not a silent pass (D-05, D-08).
- **Beta cuts are operator-gated + outward-facing publishes get an explicit human
  go-ahead** — folding the cut into the phase does not remove the gate (D-03).

### Integration Points
- **Depends on** Phase 112 (the `dev test` surface the doc hands testers into)
  and Phase 114 (feature close; `community-validation.md` hand-off target).
- **Feeds** the milestone close ceremony (D-06) — which is explicitly OUT of this
  phase's plan.

</code_context>

<specifics>
## Specific Ideas

- The community path must be reachable by a **stranger**, not just re-runnable by
  the operator — hence the fresh-venv + clean-config-dir isolation (D-07). The
  test's whole point is that the operator's already-configured bench does NOT
  leak into the result.
- The smoke test proves "the beta stack is alive and speaks the protocol," a
  deliberately smaller claim than "this chip works." Keep the live op minimal
  (`hw`/identify) so a working stack passes even on a board with no chip seated
  or on flaky uno328pb silicon.
- `3.0.0b11` is the first beta to carry v1.20 (protocol-only dispatch) AND v1.21
  (the `dev test` community-validation surface) — publishing it is what finally
  moves the PINNED-at-b10 gitlinks forward and makes the whole milestone
  reachable by the community.

</specifics>

<deferred>
## Deferred Ideas

- **Milestone close ceremony** — `v1.21` git tag, final `--no-ff` merge to `beta`,
  `/gsd-ship` / `/gsd-complete-milestone`. Deferred to a separate operator-gated
  step after this phase's verification passes (D-02, D-06). NOT this phase's plan.
- **uno328pb as a hard gate** — deferred; if a future bench session stabilizes the
  third board (or confirms its true identity), uno328pb can graduate from
  best-effort to a hard gate (D-05 → FUT item).
- **avrdude MCU-detection fallback** (`avrdude-mcu-detection-fallback.md`) — a
  feature-add to the avrdude recovery path; this phase validates the EXISTING
  path only, so it's out of scope (see Reviewed Todos).

### Reviewed Todos (not folded)
The todo matcher surfaced the **same off-axis set Phase 111 reviewed and
rejected** (1 @ 0.9, several @ 0.6). This is a VALIDATION + DOCS phase touching no
firmware behavior and building no feature; every match is on the
firmware/hardware/bench axis and hit only on generic keywords. **None folded**
(scope guardrail overrides auto-fold):
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md`
  (0.9, firmware) — a firmware VPP-check behavior change; opposite axis (this
  phase changes no firmware).
- `avrdude-mcu-detection-fallback.md` (0.6) — topically adjacent (avrdude +
  wrong-firmware recovery) but a feature-add to the avrdude path, not validation
  of the existing path. Captured as a Deferred Idea above.
- `cobs-decoder-framelevel-deadline-wr01.md`, `decode-infoic-flags-bits-14-15-…`,
  `fix-jp4-labels-and-rev2-revision-block.md`, `photograph-modified-rev-0.md`,
  `remove-dead-json-init-sizeof-pointer-bug.md` (all 0.6) — firmware / DB-decode /
  hardware / bench work; generic-keyword collisions only, none describe the
  beta-install/flash-validation/onboarding-doc work.

</deferred>

---

*Phase: 115-Beta Install & Firmware-Flash Bench Validation — Community Onboarding (close)*
*Context gathered: 2026-07-10*
