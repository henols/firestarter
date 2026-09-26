# Phase 160: RIG — Dual-Arm Build, Flash Provenance & the Shared Cell Procedure - Context

**Gathered:** 2026-08-25
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase builds the **rig**, not the results. It delivers:

1. Two named, reproducible firmware+host arms for all three AVR targets (6 firmware images, 2 host arms).
2. A flash that is **provable on-device**, not by an upload tool's exit code — with the proof demonstrated able to fail.
3. `.planning/v1.34/PROCEDURE.md` — one arm-agnostic per-cell procedure whose step list is byte-identical between arms.
4. The W→R→V oracle fixed as full-device read-back SHA equality (65536 B W27C512 / 262144 B W29C020), never an exit code.
5. A per-cell record self-sufficient for a re-run, with zero fields sourced from session memory.

**Nothing on the bench may run before this phase closes.** No sweep cell, no chip test, no evidence row.

**This phase changes no product code.** Not firmware, not the host app. Everything it builds is rig
tooling under `.planning/v1.34/tools/`. A plan that finds itself needing a source edit in either
sub-repo must stop and report — v1.34 is a gate, and REQUIREMENTS.md lists "any product-code change
not traced to a v1.33-caused regression" as Out of Scope.

**The measured fact that makes this phase load-bearing rather than ceremonial:**

| Arm | Firmware | Host app | Self-reported identity |
|---|---|---|---|
| Control | `8695ee5` | `6bfa645` | fw `3.0.0b22` · app `3.0.0b32` |
| v1.33 | `5759dc8` (fw#56 head) | `cb189a9` (app#54 head) | fw `3.0.0b22` · app `3.0.0b32` |

Verified at discussion time: `include/version.h` holds the identical literal on both firmware commits,
and `__version__` is identical on both app commits. **Both arms are indistinguishable in every
self-reported identity string.** A mis-flashed or mis-invoked cell is invisible to every handshake,
every `--version`, and every `fw_board_identity` field. The on-device read-back oracle is not
belt-and-braces — it is the only mechanism that can catch a wrong-arm cell.

</domain>

<decisions>
## Implementation Decisions

### Flash proof & arm identity (RIG-01)

- **D-01:** **A flash is proven by an independent avrdude read-back, not by avrdude's own verify pass.**
  After upload completes, a separate `avrdude -U flash:r:<file>:r` invocation reads the device back and
  the result is SHA-compared against the image that was uploaded. Rejected: relying on avrdude's built-in
  `-U flash:w:<hex>:i` verify (the upload tool judging its own upload — RIG-01 SC#2 exists to push past
  exactly that), and a per-arm build marker such as bumping `include/version.h` on one arm (it would make
  the handshake self-identifying at the cost of mutating the image under test, so the thing on the bench
  would no longer be the PR head — Phase 145 D-16's "measure the built image, do not modify it").

- **D-02:** **The judged compare is the `.hex`'s own address extent; the whole-flash SHA is recorded but
  not judged.** Normalize the `.hex` to a binary of exactly its address span and compare that span of the
  read-back. Separately record the SHA of the full 32768 B read-back as an **unjudged provenance datum**.
  Rationale: `board_upload.maximum_size = 32768` on all three envs means the linker no longer protects
  the bootloader region, so a full-flash read spans regions the `.hex` never covers (optiboot 512 B /
  urclock 384 B / Caterina 4096 B). Pinning three bootloader base addresses as exclusion windows was
  rejected as inviting spurious diffs from a differing installed bootloader build; recording the raw
  whole-flash figure costs nothing and leaves Phase 165 something to examine if a Caterina-overwrite
  hypothesis ever arises.

- **D-03:** **The wrong-arm detection is proven able to fail by a real deliberate cross-flash on all
  three targets.** On each of `uno` / `uno328pb` / `leonardo` during bring-up: flash the *other* arm, run
  the read-back compare against the *intended* arm's hex, **observe and record the MISMATCH**, then flash
  the correct arm and observe the match. Both the mismatch and the correction are recorded. Rationale: the
  upload+read-back chain genuinely differs per target (urclock / arduino / avr109), so a single-target
  proof leaves two chains taken on the comparator's word; and a comparator-only proof (SHA-comparing a
  good read-back against the other arm's hex) is close to a tautology — it proves two different files
  hash differently and never exercises the read-back path at all. Standing memory: bench boards are a
  firmware-flash testbed, so extra flash cycles need no per-flash approval.

- **D-04:** **All six built images are committed.** `.planning/v1.34/images/` holds the six `.hex` files
  (2 arms × 3 targets, ~450 KB total) with a `SHA256SUMS.txt`, alongside the two source SHAs and the
  pinned toolchain versions. Rationale: guarantees the exact bytes stay re-flashable regardless of later
  PlatformIO toolchain resolution, and makes RIG-05's "re-run from the record alone" literally true.
  Phase 145 set this precedent with its own committed images + `SHA256SUMS.txt`. Measured at discussion
  time: no `__DATE__` / `__TIME__` / `__FILE__` appears anywhere in `firestarter/src/` or
  `firestarter/include/`, so byte-identical rebuilds are plausible against the baseline's pinned
  toolchain — but SC#1's reproduce-or-record-the-divergence clause stays live, not assumed away.

- **D-05:** **The read-back proof runs at every cell's flash, not only at bring-up.** Decided mechanically,
  not asked: Phase 161's BOARD-02 SC#2 already mandates that "the firmware arm on the board is confirmed
  by the RIG-01 on-device read-back rather than assumed from the flash command — so a cell whose arm was
  mis-flashed is caught at the cell, not at the close."

### Host-arm switching (RIG-01, RIG-02)

- **D-06:** **Two git worktrees off `firestarter_app`, each with its own venv and its own
  `pip install -e`.** *(Claude's call — the user answered "You decide".)* The arm is named by the invoked
  binary path, so it appears verbatim in the recorded command line RIG-05 requires; both arms stay
  callable without a checkout step; and `firestarter.__file__` gives a positive per-invocation proof,
  which matters more than usual because `--version` reports `3.0.0b32` on both arms. Rejected: in-place
  `git checkout` in `/workspaces/firestarter_app` (zero setup and the existing editable install follows —
  but the active arm is implicit in the working tree, nothing in the command line says which arm ran, and
  a forgotten checkout silently mis-arms a cell); two full clones (same isolation, heavier on disk and
  two remotes to keep straight).

  **Two mandatory bring-up checks on this decision.** First: an editable install does **not** follow a
  worktree (standing memory: `reference_firestarter_app_worktree_editable_install_trap`), so each venv
  must be installed against its own tree and verified by printing `firestarter.__file__`. Second: a
  user-site editable install already exists at `/home/vscode/.local/lib/python3.12/site-packages`
  pointing at `/workspaces/firestarter_app`, so **bare `firestarter` on PATH resolves to a third,
  un-named arm.** PROCEDURE.md forbids bare `firestarter` on the bench; every bench command uses the
  arm venv's absolute binary path.

- **D-07:** **One frozen shared `FIRESTARTER_CONFIG_DIR` for both arms.** Seeded once at bring-up, its
  content SHA recorded in every cell's provenance block and re-verified unchanged after each cell.
  Rationale: keeps the A/B variable to the code alone, and turns any config write by either arm into a
  visible, recorded event rather than an invisible drift. Rejected: a separate config dir per arm (no
  cross-contamination, but the two dirs can legitimately diverge over the milestone — one caching a port
  or an avrdude path, the other not — quietly adding a second variable to a comparison that is supposed
  to have exactly one), and leaving the default `~/.firestarter` unmanaged. `firestarter/config.py`
  honours `FIRESTARTER_CONFIG_DIR` as a deliberate isolation seam, resolved at the process boundary.
  No `~/.firestarter` exists yet — clean slate.

- **D-08:** **The per-cell host-arm proof is a triple: SHA + porcelain + `__file__`.**
  `git -C <worktree> rev-parse HEAD` names the arm; `git status --porcelain` must be **empty**, proving
  the tree is the named commit and nothing more; `python -c 'import firestarter; print(firestarter.__file__)'`
  run from the arm's own venv proves the venv resolves into that worktree rather than the user
  site-packages install. Dropping the porcelain check was rejected — a stray uncommitted edit would ride
  into a cell invisibly and RIG-01 SC#1's "named source state" would stop being provably what ran.

- **D-09:** **Both arms run on one interpreter, and that is stated as a non-claim.** Decided mechanically:
  the devcontainer is Python 3.12.13 while app CI targets 3.11. Both arms run on the same interpreter, so
  it is not an A/B confound — but the interpreter version is recorded once and Phase 166's honesty ledger
  states that v1.34 ran on py3.12, not the py3.11 CI floor.

### The W→R→V oracle (RIG-04)

- **D-10:** **`dev consistency-check` produces the read artifacts; a phase-owned script judges them.**
  `dev consistency-check --runs 3 --output-dir <cell> --keep-files` produces the per-run binaries in one
  command (its `--keep-files` default is already `True`); a script under `.planning/v1.34/tools/` then
  computes SHA-256 over the **full device size** and compares against the written image. The app's own
  3-way verdict (`0=PASS 1=FAIL 2=hw-error`) is **recorded alongside as an unjudged datum**, and any
  disagreement between it and the SHA verdict is itself flagged as a finding. This satisfies RIG-04
  ("never an exit code") and Phase 145 D-06 ("the thing under test and the thing judging it must not be
  the same code path") — which bites harder here than in v1.31, because the host app is itself an arm
  variable. Rejected: plain `read ×N` (would exercise only the user-facing read path — a real argument,
  since `dev consistency-check` is beta-channel-gated and stable users do not have it — but costs N
  invocations and loses the tool's own divergence report), and running both paths per cell (roughly
  doubles read time across 20 positions).

  **Noted for the honesty ledger:** the judged evidence chain runs through a dev-tools-gated command that
  stable-channel users do not have. Both arms are pre-release builds (`3.0.0b32` parses as a PEP 440
  pre-release), so `channel.py`'s gate leaves the `dev` commands registered on both.

- **D-11:** **N=3 on the v1.33 arm always; the control arm's N=3 is conditional on a v1.33 disagreement.**
  RIG-04's letter is N=3 on the v1.33 arm only; this exceeds it without adding a new capability. The
  control arm takes a single read normally, and N=3 fires **only** where the v1.33 arm's three reads
  disagree — arbitrating whether the instability is new or was always there. Mirrors CHIP-04's own
  established shape, "a control re-run for every divergence and for no other". Symmetric N=3 everywhere
  was rejected on cost (40 extra reads, 10 of them on the 256 KiB W29C020); RIG-04's bare letter was
  rejected because a v1.33-arm read-stability finding would then be unattributable, which is the precise
  "did this fail, or has it always failed here" gap this milestone exists to close.

  Any N=3 disagreement is **recorded as a disagreement, never retried away** (RIG-04's own wording).

- **D-12:** **A distinct, address-attributable image per (cell × chip × arm) — 20 images, seed-derived.**
  Derived from a recorded seed so any one image is reproducible from the record alone.

  **This is the decision most load-bearing against a false green.** Standing memory
  (`reference_devtest_write_repeat_emits_no_pulses_27c`): `dev test`'s second write emits **zero** pulses
  on 329/746 parts because LOOP-06 skips already-correct bytes. If the control arm writes image X and the
  v1.33 arm then writes the same image X to the same seated chip, the v1.33 write can be a near-no-op and
  still verify green — on the milestone's headline arm. An erase almost certainly neutralises this (plain
  `write` does erase the W27C512, and W29C020's alg 5 auto-erases), but that is exactly the assumption
  Phase 145's D-03 refused to make on this bench. Distinct images make the question moot instead of
  answered-by-hope, and they make an address-attribution fault visible: a read-back matching the wrong
  cell's image is instantly recognisable. `firestarter_app/tools/gen_test_image.py` exists as a candidate
  generator (Phase 145 used it for the same purpose).

### Per-cell record shape (RIG-02, RIG-05)

- **D-13:** **A phase-owned `capture_provenance.py` emits one JSON block per cell.** It gathers every
  machine-readable field itself — board signature, the port's `controller:` string, firmware read-back
  SHA, host worktree SHA + porcelain + `__file__`, config-dir SHA, chip part + package — and takes the
  **operator-declared shield revision as a required argument, refusing to run without it**. Rationale:
  RIG-05's "zero fields sourced from session memory" is discharged by a mechanism rather than by a
  transcriber's discipline; a hand-filled checklist would make the falsification test measure diligence,
  and a mistyped SHA would be indistinguishable from a real one.

- **D-14:** **Board identity by signature uses a phase-owned probe; the pending todo stays pending.**
  Decided mechanically. RIG-02 requires board identity **by signature, never by handshake**. The
  bench-verified mechanism already exists, written up in
  `.planning/todos/pending/avrdude-mcu-detection-fallback.md`: passing avrdude a deliberately wrong `-p`
  makes it name the actual part in stderr (`connected part ATmega328PB differs in signature`), with
  `(probably mXXX)` as a second parse route — confirmed live on the operator's 328PB-Uno in 2026-05-21.
  v1.34 **reuses that mechanism in its own tool** and does **not** fold the todo into
  `firestarter_app/firestarter/firmware.py`: that would be a product-code change untraceable to a
  v1.33-caused regression, which REQUIREMENTS.md lists under Out of Scope. The todo is annotated
  "mechanism reused by v1.34 Phase 160; product-side `--detect-mcu` still pending" and stays open.

- **D-15:** **`.planning/v1.34/bench/EVIDENCE.jsonl` is canonical; `EVIDENCE.md` is rendered from it.**
  One append-only row per evidence position, with `locked_columns` pinned here at Phase 160. The human
  table is generated by a phase-owned renderer and **never hand-edited**. Rationale: Phase 166's CLOSE-01
  reconciliation ("results + named absences = 20 positions", shown as arithmetic) becomes a script over
  the rows, so a silent gap is structurally impossible rather than something a reader has to notice.
  Rejected: hand-maintaining a paired `EVIDENCE.{md,json}` in the v1.15 / v1.18 shape (proven twice in
  this project, but the two can drift and CLOSE-01 is then only as good as the last sync), and
  Markdown-primary with ~20 per-cell JSON sidecars (Phase 145's shape scaled up — the merge itself
  becomes a step that can be got wrong).

  Carry forward from the v1.15 record's shape: `locked_columns`, a per-cell preconditions block, and a
  **negative control recorded as FIRED** rather than as configured.

- **D-16:** **Artifact layout — everything rig-shaped lives at the milestone level.** Decided
  mechanically; SC#3 already mandates `.planning/v1.34/PROCEDURE.md`, and the `.planning/v1.15/bench/`
  and `.planning/v1.18/bench/` precedent puts bench evidence at the milestone level because it spans
  phases. Phase directories keep only GSD artifacts (PLAN / SUMMARY / VERIFICATION).

  ```
  .planning/v1.34/
    PROCEDURE.md            # SC#3 — arm-agnostic, diff of the two arms' step lists is empty
    images/                 # 6 .hex + SHA256SUMS.txt (D-04)
    tools/                  # capture_provenance.py, the SHA judge, the EVIDENCE renderer, the record gate
    bench/
      EVIDENCE.jsonl        # canonical, append-only (D-15)
      EVIDENCE.md           # rendered, never hand-edited
      cells/<cell-id>/      # provenance JSON, read-back .bin, flash read-back, logs
  ```

- **D-17:** **SC#5's falsification test = a per-cell script gate PLUS one fresh-context reconstruction.**
  The script gates every cell record — every required field present and non-null, every recorded command
  line re-parsing into the set PROCEDURE.md prescribes. Separately, **once, against the bring-up record
  before any sweep cell executes**, a fresh context given *only* the record and the procedure emits the
  command set and physical setup it would use, and that output is diffed against the prescription. The
  script proves completeness; the reconstruction proves the property SC#5 actually names. Neither alone
  suffices: a script-only gate proves the record has all its fields, not that someone holding only that
  record could rebuild the rig; a reconstruction-only proof leaves cells 2 through 20 unchecked, so a
  field that quietly stops being captured mid-sweep goes unnoticed until the close.

### Outcome taxonomy

- **D-18:** **Two axes, not one — and Phase 145's D-14 is not being relaxed.** Decided mechanically.
  Phase 145 fixed a two-state taxonomy and explicitly banned the word *inconclusive*; v1.34's RCA-04
  requires it. These are different axes and PROCEDURE.md says so:
  - **Cell outcome** (Phases 160–163) stays **two-state**: `validated` or `skipped-with-reason`. Anything
    that is not a clean pass is a **fail**; anything not attempted is a **skip**. There is no third state.
  - **Triage classification** (Phase 165, RCA-01) is the three-state axis: `v1.33-caused` /
    `pre-existing` / `inconclusive`, applied to a *failure* after the fact.

  A cell result may therefore never be recorded as `inconclusive`. Only a Phase 165 classification may.

### Claude's Discretion

- The **host-arm switching mechanism** (D-06 above) was answered "You decide". Claude chose two worktrees + two
  venvs. The planner may substitute two full clones if the worktree route hits an obstacle — the
  load-bearing property is that **the arm appears in the invoked binary path**, not the worktree
  mechanism itself. In-place `git checkout` does not satisfy that property and is not a permitted
  substitution.
- Open and left to research/planning: PROCEDURE.md's exact step ordering (mount → identity → pot →
  erase/write/read/verify → teardown, and the two-chip rotation within a cell); the halt policy when a
  read-back or oracle goes red mid-sweep (Phase 145's D-13 halted the phase and handed to `/gsd-debug`;
  v1.34 has Phase 165 as the designated triage owner instead, so the policy needs restating rather than
  inheriting); and whether write duration is wall-clock around the command or scraped from the app's own
  reporting. Both bench chips declare `vpp_mv 12000`, so **no pot re-adjustment is needed between chips
  within a cell** — the procedure should exploit that.

### Folded Todos

- **`avrdude-mcu-detection-fallback`** (`.planning/todos/pending/avrdude-mcu-detection-fallback.md`,
  captured 2026-05-21, area: general). Original problem: the host install flow requires a firmware
  handshake, so a blank chip / wrong firmware cannot be recovered, and a wrong-firmware board is
  re-flashed with the wrong image without complaint. **Folded as mechanism only, per D-14** — its
  bench-verified avrdude signature-probe technique is what RIG-02's "board identity by signature, never
  by handshake" is built on. The todo's *product* deliverable (a `firestarter fw -i --detect-mcu` flag in
  `firmware.py`) is **not** folded and the todo stays `pending`; folding it would be an Out-of-Scope
  product-code change.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone definition (binding)
- `.planning/REQUIREMENTS.md` — RIG-01…05 verbatim, the five-cell table, the control baseline SHAs, and
  the **Out of Scope** table that forbids product-code change untraceable to a v1.33 regression
- `.planning/ROADMAP.md` §"Phase 160: RIG — Dual-Arm Build, Flash Provenance & the Shared Cell Procedure"
  (lines 224–283) — the Goal and the five Success Criteria this phase is judged against
- `.planning/ROADMAP.md` §"Phase 161" (lines 285–299) — BOARD-02 SC#2 mandates the per-cell read-back
  confirmation that D-05 adopts; BOARD-01 SC#1 fixes the 12-position shape the record must hold
- `.planning/PROJECT.md` §"Current Milestone: v1.34" (lines 42–117) — the matrix, the known-faults
  declaration, and the merge posture

### The closest prior art — v1.31 Phase 145 bench validation
- `.planning/phases/145-bench-validation/145-CONTEXT.md` — D-01…D-20. Load-bearing here: **D-06**
  (two oracles recorded separately, disagreement visible), **D-07** (read stability per cycle),
  **D-08** (v1.31 ran **no** control arm — the gap v1.34 exists to fill), **D-09** (one clean re-seat
  allowed, both the discard and the re-run recorded), **D-14** (the two-state taxonomy D-18 preserves),
  **D-16** (measure the built image, change no source), **D-17** (no `--force`, ever), **D-18** (image
  identified by commit, never by version string), **D-19** (Claude drives serial/CLI, operator owns the
  physical), **D-20** (must not run under `--auto` / `--chain`)
- `.planning/phases/145-bench-validation/145-BENCH-LOG.md` — the gate/verification-map-binding record
  shape, and the standing "nothing here is fabricated; a tooling-blocked reading is `not measured` with
  its blocking reason on the same line" discipline
- `.planning/phases/145-bench-validation/SHA256SUMS.txt` — the committed-artifact-hash precedent D-04 follows
- `.planning/phases/145-bench-validation/` `images/` `readbacks/` `runs/` `logs/` — the per-cycle artifact layout

### Evidence-record precedent
- `.planning/v1.15/bench/EVIDENCE.json` — `locked_columns`, `evid_extension_columns`, the per-task
  SAFE-01 preconditions block, and a negative control recorded as **FIRED**
- `.planning/v1.15/bench/EVIDENCE.md` — the rendered human form D-15 generates rather than hand-writes
- `.planning/v1.18/bench/EVIDENCE.{md,json}` — the second application of the same shape

### Firmware build & flash surface
- `firestarter/platformio.ini` — the three AVR envs; `board_upload.maximum_size = 32768` on all three
  (the linker no longer protects optiboot 512 B / urclock 384 B / Caterina 4096 B — the fact behind D-02);
  the leonardo `DATA_BUFFER_SIZE=1024` and `EPROM_OVERPROGRAM_SUPPORTED=0` deltas
- `firestarter/scripts/baseline/size_baseline.json` — pinned toolchain (`platformio_core 6.1.19`,
  `platform_atmelavr 5.2.0`, `avr_gcc 7.3.0`, `framework_arduino_avr 5.3.0`) that D-04's reproducibility
  claim rests on, plus the per-target measured flash figures and the Caterina-cliff headroom note
- `firestarter/name_firmware.py` — PROGNAME derives from `-D RURP_BOARD_NAME`, locking the board-id triple
- `firestarter/include/version.h` — the identical `VERSION "3.0.0b22"` literal on **both** arms
- `firestarter_app/firestarter/firmware.py:500` `_install_with_avrdude` — per-board programmer/baud
  dispatch (leonardo → `atmega32u4` / `avr109` / 57600); the frozen function D-14 declines to extend

### Host app surface
- `firestarter_app/firestarter/channel.py` — `BETA_ONLY_DEV_COMMANDS` includes `consistency-check`;
  `is_prerelease_build()` fails **closed**. Both arms are `3.0.0b32`, so `dev` stays registered — the
  honesty-ledger note under D-10
- `firestarter_app/firestarter/cli_handlers.py:1469` `dev consistency-check` — `--runs` (default 3,
  min 2), `--output-dir`, `--keep-files` (default True), `--max-diffs`; 3-way verdict `0/1/2` that must
  **not** be bool-to-int wrapped
- `firestarter_app/firestarter/cli_handlers.py:485` `read` — `read <eprom> [output_file]`, positional
  output path, **no `-o` flag**
- `firestarter_app/firestarter/config.py:25` — `FIRESTARTER_CONFIG_DIR` isolation seam D-07 uses
- `firestarter_app/tools/gen_test_image.py` — candidate generator for D-12's 20 images

### Deferred mechanism source
- `.planning/todos/pending/avrdude-mcu-detection-fallback.md` — the bench-verified signature-probe
  technique D-14 reuses (both parse routes, confirmed live 2026-05-21 on the operator's 328PB-Uno)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`dev consistency-check --runs N --output-dir --keep-files`** — the N=3 read-stability harness already
  exists and, crucially, **keeps the per-run binaries**. That is what makes D-10's split possible: the
  arm's own tool produces the artifacts, an arm-independent script judges them.
- **`firestarter_app/tools/gen_test_image.py`** — Phase 145 used it for exactly D-12's purpose
  (distinct address-attributable images per cycle).
- **`.planning/phases/145-bench-validation/tools/extract_frames.py`** — the stderr frame-extraction
  approach, if write-duration measurement ends up scraping the app's own output.
- **avrdude and PlatformIO are both present in the devcontainer** (`/usr/bin/avrdude`,
  `/usr/local/bin/pio`), so the arms can be built and flashed without new tooling.
- **`firestarter_app/.venv` and `firestarter_app/.venv/ci-replica`** already exist — precedent for
  per-purpose venvs in this repo.

### Established Patterns
- **Milestone-level `bench/EVIDENCE.{md,json}`** (v1.15, v1.18) — evidence that spans phases lives at
  the milestone level, not in a phase dir. D-15 / D-16 follow this.
- **Committed artifacts with a `SHA256SUMS.txt`** (Phase 145, Phase 99) — the project's standing way of
  making a bench artifact re-checkable.
- **Negative controls recorded as FIRED** (v1.15 EVID-03) — a gate is not credible until it has been
  seen to go red. This is why D-03 insists on a real cross-flash rather than a comparator check, and it
  matches the standing memory that a pre-authored gate leg can be unreachable and that RED proves nothing
  until it is observed.
- **Channel gating is derived from the app's own version and fails closed** — no env var can flip it.
- **The board-id triple** (`RURP_BOARD_NAME` build flag = artifact filename = handshake `<board>` slot)
  has one source of truth in `name_firmware.py`.

### Integration Points
- Nothing integrates into product code. The phase's outputs are `.planning/v1.34/PROCEDURE.md`,
  `.planning/v1.34/images/`, `.planning/v1.34/tools/` and the initialized
  `.planning/v1.34/bench/EVIDENCE.jsonl` with its `locked_columns` pinned.
- The consumers are **Phases 161–166**, which fill the record this phase defines. Pinning
  `locked_columns` here is what lets Phase 166's CLOSE-01 arithmetic be a script rather than a count.
- The v1.34 sub-repo branch posture is deliberately minimal: the two sub-repos are read at fixed SHAs
  (checked out into worktrees for the host app), and per RCA-03 any later fix lands on
  `gsd/v1.33-source-hygiene-firmware-size-reduction`, never on a v1.34 branch. This phase creates no
  sub-repo commits.

</code_context>

<specifics>
## Specific Ideas

- **"Both arms are indistinguishable over the wire."** This measured fact — identical `VERSION` literal,
  identical `__version__` — is the phase's organizing constraint. Every decision above is downstream of
  it. Any plan that reintroduces a version-string or handshake-based arm check has misunderstood the phase.
- **The LOOP-06 no-op hazard (D-12)** is the specific false-green this phase is buying insurance against:
  standing evidence that a second write emits zero pulses on 329/746 parts because already-correct bytes
  are skipped. On the v1.33 arm, in a milestone whose entire premise is that v1.33 changed nothing, that
  failure mode would produce a green that means nothing.
- **The falsification tests must be observed red, not authored.** Both D-03 (wrong-arm cross-flash) and
  D-17 (record reconstruction) exist because this project has repeatedly found that a gate written but
  never seen to fail proves nothing.
- **The A/B is the deliverable.** v1.31 explicitly declined a control run (Phase 145 D-08) and said so.
  Everything about the rig should make the control arm as easy to run as the v1.33 arm — that is why
  PROCEDURE.md's two arm step-lists must diff empty (SC#3), and why the arm lives in the binary path
  rather than in a checkout step.

</specifics>

<deferred>
## Deferred Ideas

- **Product-side `firestarter fw -i --detect-mcu`** — the deliverable half of the folded todo. v1.34
  reuses its mechanism in a phase tool only (D-14). The todo stays `pending`.
- **Neutralizing the user-site editable install** rather than relying on PROCEDURE.md forbidding bare
  `firestarter` — raised, not adopted, to avoid disturbing the dev environment mid-milestone. If a
  bare-`firestarter` slip is ever detected in a cell record, revisit.
- **Building the two arm venvs on py3.11 to match CI** rather than the devcontainer's 3.12 — raised, not
  adopted (D-09). Both arms share one interpreter so it is not an A/B confound; it becomes an
  honesty-ledger line in Phase 166 instead.
- **Full-flash compare with pinned bootloader exclusion windows** (D-02's rejected third option) — would
  also catch an over-Caterina overwrite. Not adopted; the raw whole-flash SHA is recorded so the question
  stays answerable later without a re-run.
- **Symmetric N=3 on both arms at every position** (D-11's rejected option) — available as an escalation
  if conditional arbitration proves insufficient in Phase 161.

### Reviewed Todos (not folded)

`todo.match-phase 160` returned 27 matches; all but one scored on generic keyword overlap
(`read`, `write`, `firmware`, `phase`) rather than on this phase's actual subject. Reviewed and **not**
folded:

- **Photograph operator's Modified Rev 0 board** and **Write full MODIFICATIONS.md rework trace** —
  real, live, and already scoped: they are **Phase 164** (REV0-01…03), which is where they belong.
- **Prove the PlatformIO dev-tools build flag fails CLOSED** — `-D DEV_TOOLS` sits at `[env]` scope in
  `platformio.ini`, so **both** arms carry it identically. It is not an A/B variable and proving it is
  not this phase's job.
- **AT28C256 write-path failure (gh#20)**, **W29C040 / AM27C020 / FM1608 / 2516 defects**, **COBS
  frame-deadline**, **CONFIG_VERSION bump**, **pinout and page-floor database items**, **GSD tooling
  items** — none touch the rig. Several are chip-specific and will be *observed* by Phase 162's sweep,
  but none is scoped here.

</deferred>

---

*Phase: 160-RIG — Dual-Arm Build, Flash Provenance & the Shared Cell Procedure*
*Context gathered: 2026-08-25*
