# Phase 160: RIG — Dual-Arm Build, Flash Provenance & the Shared Cell Procedure - Research

**Researched:** 2026-08-26
**Domain:** AVR build reproducibility · avrdude flash read-back provenance · dual-arm Python venv isolation · bench-record substrate
**Confidence:** HIGH on everything measurable in the devcontainer; **MEDIUM/LOW on the three on-device read-back chains, which are UNPROVEN — no board is attached and `flash:r` has never been invoked in this project's history.**

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Flash proof & arm identity (RIG-01)**

- **D-01:** **A flash is proven by an independent avrdude read-back, not by avrdude's own verify pass.** After upload completes, a separate `avrdude -U flash:r:<file>:r` invocation reads the device back and the result is SHA-compared against the image that was uploaded. Rejected: relying on avrdude's built-in `-U flash:w:<hex>:i` verify (the upload tool judging its own upload — RIG-01 SC#2 exists to push past exactly that), and a per-arm build marker such as bumping `include/version.h` on one arm (it would make the handshake self-identifying at the cost of mutating the image under test, so the thing on the bench would no longer be the PR head — Phase 145 D-16's "measure the built image, do not modify it").

- **D-02:** **The judged compare is the `.hex`'s own address extent; the whole-flash SHA is recorded but not judged.** Normalize the `.hex` to a binary of exactly its address span and compare that span of the read-back. Separately record the SHA of the full 32768 B read-back as an **unjudged provenance datum**. Rationale: `board_upload.maximum_size = 32768` on all three envs means the linker no longer protects the bootloader region, so a full-flash read spans regions the `.hex` never covers (optiboot 512 B / urclock 384 B / Caterina 4096 B). Pinning three bootloader base addresses as exclusion windows was rejected as inviting spurious diffs from a differing installed bootloader build; recording the raw whole-flash figure costs nothing and leaves Phase 165 something to examine if a Caterina-overwrite hypothesis ever arises.

- **D-03:** **The wrong-arm detection is proven able to fail by a real deliberate cross-flash on all three targets.** On each of `uno` / `uno328pb` / `leonardo` during bring-up: flash the *other* arm, run the read-back compare against the *intended* arm's hex, **observe and record the MISMATCH**, then flash the correct arm and observe the match. Both the mismatch and the correction are recorded. Rationale: the upload+read-back chain genuinely differs per target (urclock / arduino / avr109), so a single-target proof leaves two chains taken on the comparator's word; and a comparator-only proof (SHA-comparing a good read-back against the other arm's hex) is close to a tautology — it proves two different files hash differently and never exercises the read-back path at all. Standing memory: bench boards are a firmware-flash testbed, so extra flash cycles need no per-flash approval.

- **D-04:** **All six built images are committed.** `.planning/v1.34/images/` holds the six `.hex` files (2 arms × 3 targets, ~450 KB total) with a `SHA256SUMS.txt`, alongside the two source SHAs and the pinned toolchain versions. Rationale: guarantees the exact bytes stay re-flashable regardless of later PlatformIO toolchain resolution, and makes RIG-05's "re-run from the record alone" literally true. Phase 145 set this precedent with its own committed images + `SHA256SUMS.txt`. Measured at discussion time: no `__DATE__` / `__TIME__` / `__FILE__` appears anywhere in `firestarter/src/` or `firestarter/include/`, so byte-identical rebuilds are plausible against the baseline's pinned toolchain — but SC#1's reproduce-or-record-the-divergence clause stays live, not assumed away.

- **D-05:** **The read-back proof runs at every cell's flash, not only at bring-up.** Decided mechanically, not asked: Phase 161's BOARD-02 SC#2 already mandates that "the firmware arm on the board is confirmed by the RIG-01 on-device read-back rather than assumed from the flash command — so a cell whose arm was mis-flashed is caught at the cell, not at the close."

**Host-arm switching (RIG-01, RIG-02)**

- **D-06:** **Two git worktrees off `firestarter_app`, each with its own venv and its own `pip install -e`.** *(Claude's call — the user answered "You decide".)* The arm is named by the invoked binary path, so it appears verbatim in the recorded command line RIG-05 requires; both arms stay callable without a checkout step; and `firestarter.__file__` gives a positive per-invocation proof, which matters more than usual because `--version` reports `3.0.0b32` on both arms. Rejected: in-place `git checkout` in `/workspaces/firestarter_app` (zero setup and the existing editable install follows — but the active arm is implicit in the working tree, nothing in the command line says which arm ran, and a forgotten checkout silently mis-arms a cell); two full clones (same isolation, heavier on disk and two remotes to keep straight).

  **Two mandatory bring-up checks on this decision.** First: an editable install does **not** follow a worktree (standing memory: `reference_firestarter_app_worktree_editable_install_trap`), so each venv must be installed against its own tree and verified by printing `firestarter.__file__`. Second: a user-site editable install already exists at `/home/vscode/.local/lib/python3.12/site-packages` pointing at `/workspaces/firestarter_app`, so **bare `firestarter` on PATH resolves to a third, un-named arm.** PROCEDURE.md forbids bare `firestarter` on the bench; every bench command uses the arm venv's absolute binary path.

- **D-07:** **One frozen shared `FIRESTARTER_CONFIG_DIR` for both arms.** Seeded once at bring-up, its content SHA recorded in every cell's provenance block and re-verified unchanged after each cell. Rationale: keeps the A/B variable to the code alone, and turns any config write by either arm into a visible, recorded event rather than an invisible drift. Rejected: a separate config dir per arm (no cross-contamination, but the two dirs can legitimately diverge over the milestone — one caching a port or an avrdude path, the other not — quietly adding a second variable to a comparison that is supposed to have exactly one), and leaving the default `~/.firestarter` unmanaged. `firestarter/config.py` honours `FIRESTARTER_CONFIG_DIR` as a deliberate isolation seam, resolved at the process boundary. No `~/.firestarter` exists yet — clean slate.

- **D-08:** **The per-cell host-arm proof is a triple: SHA + porcelain + `__file__`.** `git -C <worktree> rev-parse HEAD` names the arm; `git status --porcelain` must be **empty**, proving the tree is the named commit and nothing more; `python -c 'import firestarter; print(firestarter.__file__)'` run from the arm's own venv proves the venv resolves into that worktree rather than the user site-packages install. Dropping the porcelain check was rejected — a stray uncommitted edit would ride into a cell invisibly and RIG-01 SC#1's "named source state" would stop being provably what ran.

- **D-09:** **Both arms run on one interpreter, and that is stated as a non-claim.** Decided mechanically: the devcontainer is Python 3.12.13 while app CI targets 3.11. Both arms run on the same interpreter, so it is not an A/B confound — but the interpreter version is recorded once and Phase 166's honesty ledger states that v1.34 ran on py3.12, not the py3.11 CI floor.

**The W→R→V oracle (RIG-04)**

- **D-10:** **`dev consistency-check` produces the read artifacts; a phase-owned script judges them.** `dev consistency-check --runs 3 --output-dir <cell> --keep-files` produces the per-run binaries in one command (its `--keep-files` default is already `True`); a script under `.planning/v1.34/tools/` then computes SHA-256 over the **full device size** and compares against the written image. The app's own 3-way verdict (`0=PASS 1=FAIL 2=hw-error`) is **recorded alongside as an unjudged datum**, and any disagreement between it and the SHA verdict is itself flagged as a finding. This satisfies RIG-04 ("never an exit code") and Phase 145 D-06 ("the thing under test and the thing judging it must not be the same code path") — which bites harder here than in v1.31, because the host app is itself an arm variable. Rejected: plain `read ×N` (would exercise only the user-facing read path — a real argument, since `dev consistency-check` is beta-channel-gated and stable users do not have it — but costs N invocations and loses the tool's own divergence report), and running both paths per cell (roughly doubles read time across 20 positions).

  **Noted for the honesty ledger:** the judged evidence chain runs through a dev-tools-gated command that stable-channel users do not have. Both arms are pre-release builds (`3.0.0b32` parses as a PEP 440 pre-release), so `channel.py`'s gate leaves the `dev` commands registered on both.

- **D-11:** **N=3 on the v1.33 arm always; the control arm's N=3 is conditional on a v1.33 disagreement.** RIG-04's letter is N=3 on the v1.33 arm only; this exceeds it without adding a new capability. The control arm takes a single read normally, and N=3 fires **only** where the v1.33 arm's three reads disagree — arbitrating whether the instability is new or was always there. Mirrors CHIP-04's own established shape, "a control re-run for every divergence and for no other". Symmetric N=3 everywhere was rejected on cost (40 extra reads, 10 of them on the 256 KiB W29C020); RIG-04's bare letter was rejected because a v1.33-arm read-stability finding would then be unattributable, which is the precise "did this fail, or has it always failed here" gap this milestone exists to close.

  Any N=3 disagreement is **recorded as a disagreement, never retried away** (RIG-04's own wording).

- **D-12:** **A distinct, address-attributable image per (cell × chip × arm) — 20 images, seed-derived.** Derived from a recorded seed so any one image is reproducible from the record alone.

  **This is the decision most load-bearing against a false green.** Standing memory (`reference_devtest_write_repeat_emits_no_pulses_27c`): `dev test`'s second write emits **zero** pulses on 329/746 parts because LOOP-06 skips already-correct bytes. If the control arm writes image X and the v1.33 arm then writes the same image X to the same seated chip, the v1.33 write can be a near-no-op and still verify green — on the milestone's headline arm. An erase almost certainly neutralises this (plain `write` does erase the W27C512, and W29C020's alg 5 auto-erases), but that is exactly the assumption Phase 145's D-03 refused to make on this bench. Distinct images make the question moot instead of answered-by-hope, and they make an address-attribution fault visible: a read-back matching the wrong cell's image is instantly recognisable. `firestarter_app/tools/gen_test_image.py` exists as a candidate generator (Phase 145 used it for the same purpose).

**Per-cell record shape (RIG-02, RIG-05)**

- **D-13:** **A phase-owned `capture_provenance.py` emits one JSON block per cell.** It gathers every machine-readable field itself — board signature, the port's `controller:` string, firmware read-back SHA, host worktree SHA + porcelain + `__file__`, config-dir SHA, chip part + package — and takes the **operator-declared shield revision as a required argument, refusing to run without it**. Rationale: RIG-05's "zero fields sourced from session memory" is discharged by a mechanism rather than by a transcriber's discipline; a hand-filled checklist would make the falsification test measure diligence, and a mistyped SHA would be indistinguishable from a real one.

- **D-14:** **Board identity by signature uses a phase-owned probe; the pending todo stays pending.** Decided mechanically. RIG-02 requires board identity **by signature, never by handshake**. The bench-verified mechanism already exists, written up in `.planning/todos/pending/avrdude-mcu-detection-fallback.md`: passing avrdude a deliberately wrong `-p` makes it name the actual part in stderr (`connected part ATmega328PB differs in signature`), with `(probably mXXX)` as a second parse route — confirmed live on the operator's 328PB-Uno in 2026-05-21. v1.34 **reuses that mechanism in its own tool** and does **not** fold the todo into `firestarter_app/firestarter/firmware.py`: that would be a product-code change untraceable to a v1.33-caused regression, which REQUIREMENTS.md lists under Out of Scope. The todo is annotated "mechanism reused by v1.34 Phase 160; product-side `--detect-mcu` still pending" and stays open.

- **D-15:** **`.planning/v1.34/bench/EVIDENCE.jsonl` is canonical; `EVIDENCE.md` is rendered from it.** One append-only row per evidence position, with `locked_columns` pinned here at Phase 160. The human table is generated by a phase-owned renderer and **never hand-edited**. Rationale: Phase 166's CLOSE-01 reconciliation ("results + named absences = 20 positions", shown as arithmetic) becomes a script over the rows, so a silent gap is structurally impossible rather than something a reader has to notice. Rejected: hand-maintaining a paired `EVIDENCE.{md,json}` in the v1.15 / v1.18 shape (proven twice in this project, but the two can drift and CLOSE-01 is then only as good as the last sync), and Markdown-primary with ~20 per-cell JSON sidecars (Phase 145's shape scaled up — the merge itself becomes a step that can be got wrong).

  Carry forward from the v1.15 record's shape: `locked_columns`, a per-cell preconditions block, and a **negative control recorded as FIRED** rather than as configured.

- **D-16:** **Artifact layout — everything rig-shaped lives at the milestone level.** Decided mechanically; SC#3 already mandates `.planning/v1.34/PROCEDURE.md`, and the `.planning/v1.15/bench/` and `.planning/v1.18/bench/` precedent puts bench evidence at the milestone level because it spans phases. Phase directories keep only GSD artifacts (PLAN / SUMMARY / VERIFICATION).

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

- **D-17:** **SC#5's falsification test = a per-cell script gate PLUS one fresh-context reconstruction.** The script gates every cell record — every required field present and non-null, every recorded command line re-parsing into the set PROCEDURE.md prescribes. Separately, **once, against the bring-up record before any sweep cell executes**, a fresh context given *only* the record and the procedure emits the command set and physical setup it would use, and that output is diffed against the prescription. The script proves completeness; the reconstruction proves the property SC#5 actually names. Neither alone suffices: a script-only gate proves the record has all its fields, not that someone holding only that record could rebuild the rig; a reconstruction-only proof leaves cells 2 through 20 unchecked, so a field that quietly stops being captured mid-sweep goes unnoticed until the close.

**Outcome taxonomy**

- **D-18:** **Two axes, not one — and Phase 145's D-14 is not being relaxed.** Decided mechanically. Phase 145 fixed a two-state taxonomy and explicitly banned the word *inconclusive*; v1.34's RCA-04 requires it. These are different axes and PROCEDURE.md says so:
  - **Cell outcome** (Phases 160–163) stays **two-state**: `validated` or `skipped-with-reason`. Anything that is not a clean pass is a **fail**; anything not attempted is a **skip**. There is no third state.
  - **Triage classification** (Phase 165, RCA-01) is the three-state axis: `v1.33-caused` / `pre-existing` / `inconclusive`, applied to a *failure* after the fact.

  A cell result may therefore never be recorded as `inconclusive`. Only a Phase 165 classification may.

### Claude's Discretion

- **D-06** (host-arm switching mechanism) was answered "You decide". Claude chose two worktrees + two venvs. The planner may substitute two full clones if the worktree route hits an obstacle — the load-bearing property is that **the arm appears in the invoked binary path**, not the worktree mechanism itself. In-place `git checkout` does not satisfy that property and is not a permitted substitution.
- Open and left to research/planning: PROCEDURE.md's exact step ordering (mount → identity → pot → erase/write/read/verify → teardown, and the two-chip rotation within a cell); the halt policy when a read-back or oracle goes red mid-sweep (Phase 145's D-13 halted the phase and handed to `/gsd-debug`; v1.34 has Phase 165 as the designated triage owner instead, so the policy needs restating rather than inheriting); and whether write duration is wall-clock around the command or scraped from the app's own reporting. Both bench chips declare `vpp_mv 12000`, so **no pot re-adjustment is needed between chips within a cell** — the procedure should exploit that.

### Deferred Ideas (OUT OF SCOPE)

- **Product-side `firestarter fw -i --detect-mcu`** — the deliverable half of the folded todo. v1.34 reuses its mechanism in a phase tool only (D-14). The todo stays `pending`.
- **Neutralizing the user-site editable install** rather than relying on PROCEDURE.md forbidding bare `firestarter` — raised, not adopted, to avoid disturbing the dev environment mid-milestone. If a bare-`firestarter` slip is ever detected in a cell record, revisit.
- **Building the two arm venvs on py3.11 to match CI** rather than the devcontainer's 3.12 — raised, not adopted (D-09). Both arms share one interpreter so it is not an A/B confound; it becomes an honesty-ledger line in Phase 166 instead.
- **Full-flash compare with pinned bootloader exclusion windows** (D-02's rejected third option) — would also catch an over-Caterina overwrite. Not adopted; the raw whole-flash SHA is recorded so the question stays answerable later without a re-run.
- **Symmetric N=3 on both arms at every position** (D-11's rejected option) — available as an escalation if conditional arbitration proves insufficient in Phase 161.
- Reviewed and **not** folded: Photograph Modified Rev 0 / MODIFICATIONS.md rework trace (both are Phase 164); "prove the PlatformIO dev-tools build flag fails CLOSED" (`-D DEV_TOOLS` is at `[env]` scope so both arms carry it identically — not an A/B variable); AT28C256 gh#20, W29C040 / AM27C020 / FM1608 / 2516 defects, COBS frame-deadline, CONFIG_VERSION bump, pinout/page-floor DB items, GSD tooling items.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description (verbatim from REQUIREMENTS.md) | Research Support |
|----|-------------|------------------|
| **RIG-01** | Operator can flash either named arm — control (fw `8695ee5`) or v1.33 (fw#56 head) — to any of the three AVR targets, with the flashed image confirmed by device read-back, so no cell can silently run the wrong firmware | §Exact SHAs (both PR heads read off the branches, agree with CONTEXT); §Build chain (verified cold rebuild is byte-identical); §The read-back chain, per target (the `-A` flag, the urclock vector-patch hazard, the Leonardo bootloader-window hazard); §Code Examples 1–5 |
| **RIG-02** | Every cell run records, before any test step executes: board identity **by signature** (never by handshake), the port's `controller:` identity, the operator-declared shield revision, firmware build SHA, host app SHA, and chip part + package | §Signature probe (both parse routes, exact invocation, memory-confirmed on this bench); §`controller:` capture (`firmware.py:223` / `FW: <ver>:<board>`); §Chip facts (DB-verified sizes/packages/vpp); §Record substrate |
| **RIG-03** | One written per-cell procedure exists that both arms follow identically, so any A/B delta is attributable to the firmware and to nothing else | §**Arm-agnosticism is MEASURED**: an AST diff of all 25 Click commands + their full option/argument name sets is EMPTY between `6bfa645` and `cb189a9`; §Pattern 4 (the step-list diff gate); §PROCEDURE.md step ordering derived from standing bench rules |
| **RIG-04** | The write→read→verify oracle is read-back SHA equality against the written image over the **full device size**, never an exit code; the v1.33 arm additionally carries a read-stability check of N=3 reads resolving to one SHA | §`dev consistency-check` mechanics (exact artifact names `run_NN.bin`, exact verdict-block strings, both arms identical, early-return-on-hw-error means <N files); §Chip facts (65536 / 262144 DB-verified); §Pitfall 6 (the app's PASS means reads agree with EACH OTHER, never with the written image) |
| **RIG-05** | Any single cell can be re-run from the written record alone, without reconstructing context from the session that produced it | §Record substrate (`locked_columns` v1.15/v1.18 precedent + the v1.34 extension set); §Pattern 5 (`capture_provenance.py` shape); §Pitfall 1 (the `import firestarter` → `None` trap that would silently null a required field) |
</phase_requirements>

---

## Summary

Everything this phase needs on the **host side** is present, and I measured it rather than assumed it. The two firmware arms differ across 126 files but their `platformio.ini` has **zero non-comment differences**, so both arms build through an identical configuration. A cold rebuild (`rm -rf .pio/build/uno` then one `pio run -e uno`) of the v1.33 arm reproduced a **byte-identical** `firestarter_uno.hex` in 2.04 s — SC#1's reproducibility claim holds on the target I tested, and no `__DATE__`/`__TIME__`/`__FILE__` exists on either arm to break it. The two host arms are even more strongly identical than CONTEXT claims: an AST comparison of the full Click surface (25 commands with their complete option and argument name sets) is **empty** between `6bfa645` and `cb189a9`, which is the strongest available evidence that SC#3's "no step whose text differs between the arms" is achievable rather than aspirational. The D-06 worktree+venv mechanism I built and tore down end to end: `git worktree add --detach`, `uv venv --python 3.12`, `uv pip install -e .`, and `firestarter.__file__` correctly resolved into the worktree while `dev consistency-check` was registered — the editable install *does* follow a worktree when installed against it.

The **flash read-back** — the phase's central mechanism — is where the risk lives, and it is larger than CONTEXT anticipated. Three findings, each of which will silently break D-01/D-02 if the plan does not address it. (1) `avrdude(1)` truncates a flash read to strip trailing `0xFF`, so `-U flash:r:out.bin:r` does **not** yield 32768 B; the fix is `-A`, which is engaged by default **only** for `-c arduino` and must be passed explicitly on `-c urclock` and `-c avr109`. (2) On a **vector** urboot bootloader, avrdude's urclock programmer **patches the reset vector and one designated interrupt vector** before writing and applies the same patch to its own verification — so on `uno328pb` an independent read-back compare against the raw `.hex` will produce a **false RED at address 0x0000 on every single flash**, and `-xshowvector` must be run at bring-up before the compare is trusted. (3) `flash:r` has **never been invoked in this project's history** — I searched every `.planning` document — so all three read chains are unproven, and no board is currently attached (`/dev/ttyACM*` absent), meaning I could not measure any of them.

The **record substrate** is well-precedented and cheap to build. `locked_columns` is byte-identical between `.planning/v1.15/bench/EVIDENCE.json` and `.planning/v1.18/bench/EVIDENCE.json`, giving a stable nine-column core to extend. Phase 145's `gen_addr_image.py` — **not** `firestarter_app/tools/gen_test_image.py`, which CONTEXT names in error — is the address-attributable generator D-12 actually wants, and it already carries the exact "never copy this into a sub-repo" boundary comment D-16 needs; its one real limitation is that its stamp encodes only the low 16 bits of the address, so on the 256 KiB W29C020 the pattern repeats every 64 KiB and an A16/A17 aliasing fault would be invisible.

**Primary recommendation:** treat the flash read-back chain as the phase's single load-bearing unknown and front-load it — a bring-up plan that, on each target in turn, probes the bootloader (`-xshowall` / `-xshowvector` / signature), performs one `-A` read of a *known* arm, and only then arms the comparator; and let PROCEDURE.md's step order fall out of the standing bench rules (chip OUT for the whole flash+read-back window on Uno-class, chip seated for it on Leonardo) rather than being invented.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Build the six firmware images | **PlatformIO / avr-gcc in devcontainer** | — | `pio run -e <env>` from `/workspaces/firestarter`; PROGNAME comes from `name_firmware.py`. No product-code tier involved. |
| Flash an arm to a board | **avrdude (upload chain)** | PlatformIO `-t upload` wraps it | The upload chain differs per target (arduino / urclock / avr109) and PIO already supplies the per-target flags (`-xnometadata`, 1200-baud touch, port-wait) the host app does not. |
| Prove the flashed arm on-device | **Rig tooling (`.planning/v1.34/tools/`)** driving avrdude directly | — | D-01: the judge must not be the uploader. A phase-owned script owns the read, the `.hex`→bin normalization and the SHA compare. |
| Board identity by signature | **Rig tooling** driving avrdude with a deliberately-wrong `-p` | — | D-14/RIG-02: signature, never handshake. Must NOT be folded into `firmware.py` (Out of Scope). |
| Port `controller:` identity | **Host CLI arm** (`firestarter -v -p <port> hw`) | — | This is the firmware's self-report; it is a *port-identity* datum, deliberately distinct from the authoritative signature. |
| Select the host arm | **Arm venv absolute binary path** | git worktree state | D-06: the arm must appear in the recorded command line, so path-selection is the mechanism and the worktree is only its substrate. |
| Produce the N read artifacts | **Host CLI arm** (`dev consistency-check`) | — | D-10: the arm under test produces; it must not judge. |
| Judge W→R→V | **Rig tooling** (SHA over full device size vs written image) | app's 0/1/2 verdict recorded unjudged | D-10 + Phase 145 D-06: judge ≠ subject, and disagreement is itself a finding. |
| Generate the 20 written images | **Rig tooling** (copied `gen_addr_image.py`) | — | D-12 + D-16: rig tooling in the meta repo, seed/mask recorded so any image is reproducible from the record. |
| Capture per-cell provenance | **Rig tooling** (`capture_provenance.py`) | operator (declared shield rev, as a required arg) | D-13: RIG-05 is discharged by a mechanism, not by a transcriber. |
| Physical acts (seat/unseat chip, silkscreen, pot, DMM, photos) | **Operator only** | — | Phase 145 D-19, standing memories. Claude drives serial/CLI only. |
| Evidence table + close arithmetic | **Rig tooling** (`EVIDENCE.jsonl` → renderer) | — | D-15: CLOSE-01 must be a script over rows, never a human count. |

---

## Exact SHAs — read off the branches (Research Question 7)

All four read directly from the repositories on 2026-08-26. **They agree with CONTEXT.md's table exactly.**

| Arm | Repo | Short | Full SHA | Provenance of the read |
|-----|------|-------|----------|------------------------|
| Control | firmware | `8695ee5` | `8695ee52c27a4bee4387c5c489afd5f3d7275e8a` | `git merge-base origin/beta gsd/v1.33-…` — **is** the merge-base, verified [VERIFIED: git] |
| v1.33 | firmware | `5759dc8` | `5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463` | local tip == `origin/…` tip == `gh pr view 56 --json headRefOid` [VERIFIED: git + gh] |
| Control | host app | `6bfa645` | `6bfa6453d1bac232eb81ab35fa7f14b50b0b291a` | `git merge-base origin/beta gsd/v1.33-…` [VERIFIED: git] |
| v1.33 | host app | `cb189a9` | `cb189a9b001e9e34fb7651535de339761301d061` | local tip == `origin/…` tip == `gh pr view 54 --json headRefOid` [VERIFIED: git + gh] |

- `fw#56` is **OPEN**, `MERGEABLE`, base `beta`, head branch `gsd/v1.33-source-hygiene-firmware-size-reduction` [VERIFIED: `gh pr view 56`].
- `app#54` is **OPEN**, `MERGEABLE`, base `beta`, same head branch name [VERIFIED: `gh pr view 54`].
- Commit distance: firmware `8695ee5..5759dc8` = **35 commits**; app `6bfa645..cb189a9` = **7 commits**. PROJECT.md's "35 and 7 commits behind" is exact [VERIFIED: `git rev-list --count`].
- **The indistinguishability premise is re-confirmed.** `include/version.h` on both firmware commits contains the identical single line `#define VERSION "3.0.0b22"` (byte-identical files). `firestarter/__init__.py` on both app commits contains the identical `__version__ = "3.0.0b32"` [VERIFIED: `git show`].

**Planner note.** Both local branches are *already* at the PR heads and `origin/…` is not stale, so a worktree can be created directly from the short SHA. Do **not** rely on that staying true — the plan should re-read `gh pr view <n> --json headRefOid` at execution time and fail loudly on a mismatch, because the standing memory `reference_tag_push_safe_but_local_beta_lags_origin` records that local refs in this repo set do drift.

---

## Standard Stack

### Core — all already installed, all versions measured

| Tool | Version (measured) | Path | Purpose | Why standard |
|------|--------------------|------|---------|--------------|
| PlatformIO Core | **6.1.19** | `/usr/local/bin/pio` | build the six images | Exactly the `platformio_core` pin in `firestarter/scripts/baseline/size_baseline.json` [VERIFIED: `pio --version`] |
| platform `atmelavr` | **5.2.0** | `~/.platformio/platforms/atmelavr/.piopm` | AVR builder + board JSONs + upload chain | Matches the `platform_atmelavr` pin [VERIFIED: `.piopm`] |
| `toolchain-atmelavr` | **1.70300.191015** (avr-gcc **7.3.0**) | `~/.platformio/packages/toolchain-atmelavr/bin/` | compiler; also supplies `avr-objcopy` | Matches both `toolchain_atmelavr` and `avr_gcc` pins [VERIFIED: `avr-gcc --version`] |
| `framework-arduino-avr` | **5.3.0** | `~/.platformio/packages/` | uno / leonardo core | Matches the pin [VERIFIED: `package.json`] |
| `framework-arduino-avr-minicore` | **3.1.2** | `~/.platformio/packages/` | uno328pb (MiniCore) core | Matches the pin [VERIFIED: `package.json`] |
| `avr-objcopy` | GNU binutils **2.26.20160125** | `~/.platformio/packages/toolchain-atmelavr/bin/avr-objcopy` | `.hex` → binary of exactly its address span (D-02) | The only hex→bin tool present; `srec_cat` is ABSENT [VERIFIED: `--version`, `command -v srec_cat`] |
| avrdude (system) | **7.1** | `/usr/bin/avrdude` | the read-back and signature probes | What `which avrdude` returns, therefore what the host app resolves [VERIFIED: `avrdude -v`] |
| avrdude (PlatformIO) | **8.1** (`tool-avrdude` 1.80100.0) | `~/.platformio/packages/tool-avrdude/avrdude` | what `pio run -t upload` invokes | Ships its own `avrdude.conf`, which PIO passes with `-C` [VERIFIED: `avrdude -v`, `builder/main.py:205-215`] |
| Python | **3.12.14** | `/usr/bin/python3` → `/usr/local/bin/python3.12` | rig tooling + both arm venvs | Only interpreter available; `requires-python = ">=3.9"` so the app is satisfied [VERIFIED: `python3 --version`] |
| `uv` | **0.12.6** | `/usr/local/bin/uv` | create the two arm venvs + editable install | Fastest route; used successfully in my worktree test [VERIFIED: `uv --version`] |
| `pyserial` | **3.5** | system `site-packages` **and** each arm venv | 1200-baud touch helper for the Leonardo | Present system-wide, so a rig tool can use it without a venv [VERIFIED: `import serial`] |
| `sha256sum` | coreutils | `/usr/bin/sha256sum` | the `SHA256SUMS.txt` convention | Phase 145 / Phase 99 precedent [VERIFIED] |

### Supporting — reuse, do not rewrite

| Asset | Location | Purpose | When to use |
|-------|----------|---------|-------------|
| `gen_addr_image.py` | `.planning/phases/145-bench-validation/images/gen_addr_image.py` | word-stamped **address-attributable** image generator | **This is D-12's generator.** Copy into `.planning/v1.34/tools/`. See the correction below. |
| `dev consistency-check` | `cli_handlers.py:1469` (v1.33 arm) / `:1561` (control arm) | produces `run_NN.bin` × N | RIG-04's read artifacts, both arms |
| avrdude signature probe | `.planning/todos/pending/avrdude-mcu-detection-fallback.md` | board identity by signature | RIG-02 / D-14. Mechanism only — the todo stays `pending`. |
| `extract_frames.py` | `.planning/phases/145-bench-validation/tools/extract_frames.py` | stderr frame extraction | Only if write-duration ends up scraped (see the recommendation against it) |
| `check_verdict.py` etc. | `.planning/v1.18/bench/check_*.py` | the project's gate-script shape (`def main() -> int` + `sys.exit(main())`, plain `python3`, no test framework) | The template for D-17's record gate and D-15's renderer |
| `EVIDENCE.json` `locked_columns` | `.planning/v1.15/bench/` and `.planning/v1.18/bench/` | the nine-column core | Pin `locked_columns` here at Phase 160 as an extension of this set |

### Correction to CONTEXT.md — `gen_test_image.py` is the wrong generator

CONTEXT.md D-12 and §Reusable Assets both state that "`firestarter_app/tools/gen_test_image.py` exists as a candidate generator (Phase 145 used it for the same purpose)". **Phase 145 did not use it, and explicitly rejected it.** `gen_addr_image.py`'s own module docstring says so in as many words:

> "…what makes a mismatched byte decodable back to a source address — a property `firestarter_app/tools/gen_test_image.py`'s pseudo-random data does NOT have (a mismatch there is detectable but not attributable to an address), which is exactly why D-05 rejects it and requires this generator instead. The distinction is the one that root-caused Phase 97's pin-31 (A18-aliasing) defect: an address-line fault must be traceable to which address line aliased, not merely counted as 'N bytes differ'."
> — `.planning/phases/145-bench-validation/images/gen_addr_image.py:16-25` [VERIFIED: read]

D-12 asks for images that are both **distinct** and **address-attributable**. `gen_test_image.py` (`random.Random(seed)` per byte, `firestarter_app/tools/gen_test_image.py:38-50`) delivers only the first. `gen_addr_image.py` delivers both:

```
stamp(N) = (N & 0xFF)         if N is even   (low address byte)
         = ((N >> 8) & 0xFF)  if N is odd     (high address byte)
byte(N)  = stamp(N) ^ mask
```
— `gen_addr_image.py:19-25`. Interface: `gen_addr_image.py <size_bytes> <mask_hex_or_dec> <output_path>`, printing `<path>: <size> bytes, mask=0xNN, sha256=<hex>, 0xFF_count=<n>`. The **mask is the seed** D-12 asks to record; 8 bits gives 256 distinct images, comfortably covering 20.

**Its one real limitation, which the plan must state:** the stamp encodes only the low 16 bits of the address, so on the 256 KiB **W29C020** the pattern repeats every 65536 bytes. An A16/A17 aliasing fault on that part would be **invisible** to address attribution (though still visible as a SHA mismatch if a distinct mask is used per position, which D-12 already guarantees). Two options for the planner: extend the stamp to a 4-byte word carrying all 18 address bits, or record the limitation explicitly as a stated non-claim. Either is defensible; silently inheriting the 16-bit stamp on a 18-bit part is not.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `avr-objcopy -I ihex -O binary` for D-02's normalization | a pure-Python Intel-hex parser in the rig tool | objcopy is verified exact here (see below) and is one line; a hand-rolled parser is one more thing to be wrong. **But** objcopy lives in the PIO package tree, so its path must be recorded, not assumed on `PATH` (it is **not** on `PATH`). A ~30-line parser has no path dependency. Recommend objcopy with the path recorded. |
| `pio run -t upload` for the flash | direct `avrdude` invocation built by the rig tool | PIO already supplies the three per-target subtleties the host app does not (`-xnometadata`, `TouchSerialPort(1200)`, `WaitForNewSerialPort`). A direct invocation gives a fully literal recorded command line (better for RIG-05) at the cost of re-implementing those three. **Recommend `pio run -t upload -e <env> --upload-port <port>` for the write and a direct `avrdude -A … flash:r` for the read**, and record both literal command lines. |
| `firestarter fw -i` for the flash | — | **Do not use it.** It requires a firmware handshake (so the D-03 cross-flash and any recovery case is blocked), standing memory records that `fw --install` flashes the attached board ignoring `--board`, and `avr_tool.py` does **not** pass `-xnometadata` — so on `uno328pb` it writes urclock metadata that PIO's path does not. Two different flash paths ⇒ two different flash contents on that target. |
| `uv venv` + `uv pip install -e .` | stdlib `venv` + `pip install -e .` | Both work. `uv` needs `UV_CACHE_DIR` overridden (see Environment Availability); `pip` is not installed into a bare `uv venv` by default. Whichever is chosen, record it. |

**Installation:** none. **This phase installs no new external package.** The two arm venvs install `firestarter` itself in editable mode from a local worktree, which pulls the sub-repo's own already-declared dependency set (`firestarter_app/pyproject.toml:43-50`).

**Version verification performed:** `pio --version`, `avrdude -v` (both binaries), `avr-gcc --version`, `avr-objcopy --version`, `python3 --version`, `uv --version`, and the `.piopm` / `package.json` manifests for every PlatformIO package. No version was taken from training data or from planning prose.

---

## Package Legitimacy Audit

This phase recommends **no new package**. The audit below covers the six transitive dependencies that `uv pip install -e .` actually resolved in my live worktree test, because they are installed as a side effect of D-06. All six are declared in the sub-repo's own `pyproject.toml` and predate this milestone; none is a choice this research is making.

| Package | Registry | Age (first→latest publish) | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `click` | PyPI | latest `2026-08-26` | unknown | github.com/pallets/click | **[SUS]** (`too-new`, `unknown-downloads`) | Approved — pre-existing app dependency (`click>=8.1`, `pyproject.toml:47`); `too-new` fires because a release landed today |
| `pyserial` | PyPI | latest `2020-11-23` | unknown | github.com/pyserial/pyserial | **[SUS]** (`unknown-downloads`) | Approved — pre-existing (`pyserial>=3.5`) |
| `requests` | PyPI | latest `2026-05-14` | unknown | github.com/psf/requests | **[SUS]** (`unknown-downloads`) | Approved — pre-existing (`requests>=2.20`) |
| `rich` | PyPI | latest `2026-04-12` | unknown | github.com/Textualize/rich | **[SUS]** (`unknown-downloads`) | Approved — pre-existing (`rich>=14.0`) |
| `tqdm` | PyPI | — | unknown | (tqdm/tqdm) | **[SUS]** (`unknown-downloads`) | Approved — pre-existing (`tqdm>=4.60`) |
| `packaging` | PyPI | — | unknown | (pypa/packaging) | **[SUS]** (`unknown-downloads`) | Approved — pre-existing (`packaging>=21.0`) |

**Honest reading of these verdicts:** every one of the six came back `SUS`, and in every case the reason set reduces to `unknown-downloads` — the PyPI JSON API exposes no download counter, so the seam cannot score it and fails to the cautious side. `click`'s additional `too-new` reason is a same-day upstream release, not a new package. Treating six of the Python ecosystem's most-depended-upon packages as suspicious would be a false positive; treating the *verdict* as meaningless would be the opposite error. The correct disposition is the one recorded above: these are not this phase's package choices at all — they are the pinned dependency set of a sub-repo that is itself the thing under test, resolved from its own `pyproject.toml`. [VERIFIED: `gsd-tools query package-legitimacy check --ecosystem pypi`, `firestarter_app/pyproject.toml:43-50`]

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS] requiring a `checkpoint:human-verify`:** none on this phase's account. The planner should **not** insert install-gating checkpoints for the six above; gating a sub-repo's own declared dependency set would be ceremony. If the planner wants a real guard, the useful one is different: **record the resolved version of each of the six in the arm-venv provenance block**, because a version drift between the two arm venvs *would* be a genuine second A/B variable and nothing currently prevents it (see Pitfall 8).

---

## Architecture Patterns

### System Architecture Diagram

```
                     ┌─────────────────────────────────────────────┐
   OPERATOR ────────▶│ mount shield · seat/unseat chip · read      │
   (physical only)   │ silkscreen · set pot · DMM · photos         │
                     └──────────────────┬──────────────────────────┘
                                        │ declares shield rev (required arg)
                                        ▼
 ┌──────────────────┐          ┌────────────────────────────────────┐
 │ fw @ 8695ee5     │          │  RIG TOOLING  .planning/v1.34/tools│
 │ fw @ 5759dc8     │          │                                    │
 └────────┬─────────┘          │  capture_provenance.py             │
          │ pio run -e <env>   │  gen_addr_image.py   (copied)       │
          ▼                    │  judge_readback.py                  │
 ┌──────────────────┐          │  judge_wrv.py                       │
 │ 6 × .hex         │          │  render_evidence.py                 │
 │ + SHA256SUMS.txt │          │  gate_record.py                     │
 │ .planning/v1.34/ │          └───┬───────────────┬─────────────┬──┘
 │        images/   │              │               │             │
 └────────┬─────────┘              │ avrdude       │ avrdude     │ SHA over
          │                        │ (wrong -p)    │ -A flash:r  │ full size
          │ pio run -t upload      ▼               ▼             │
          │ --upload-port          signature    32768 B          │
          ▼                        (RIG-02)     read-back        │
 ┌───────────────────────────────────────────────┐               │
 │            THE THREE AVR TARGETS              │               │
 │  uno      atmega328p  -c arduino  b115200     │               │
 │           optiboot 512B · -A is DEFAULT       │               │
 │  uno328pb atmega328pb -c urclock  b115200     │               │
 │           urboot 384B · -xnometadata          │               │
 │           ⚠ VECTOR-PATCH HAZARD @ 0x0000      │               │
 │  leonardo atmega32u4  -c avr109   b57600      │               │
 │           Caterina 4096B · 1200-baud touch    │               │
 │           ⚠ SHORT BOOTLOADER WINDOW           │               │
 └───────────────────┬───────────────────────────┘               │
                     │ RURP shield bus                           │
                     ▼                                           │
        ┌──────────────────────────┐                             │
        │ W27C512  DIP28 65536 B   │                             │
        │ W29C020  DIP32 262144 B  │  both vpp_mv 12000          │
        └──────────┬───────────────┘                             │
                   │                                             │
     ┌─────────────┴──────────────┐                              │
     │  HOST ARM (one of exactly  │                              │
     │  two absolute venv paths)  │                              │
     │  <arm>/.venv/bin/firestarter                              │
     │    write <chip> <image>     │──── written image ───────────┤
     │    dev consistency-check    │──── run_01..NN.bin ──────────┤
     │      --runs 3 --output-dir  │──── exit 0/1/2 (UNJUDGED) ───┤
     │  FIRESTARTER_CONFIG_DIR ────┤ shared, frozen, SHA'd        │
     └────────────────────────────┘                              │
                                                                 ▼
                              ┌──────────────────────────────────────┐
                              │ .planning/v1.34/bench/               │
                              │   EVIDENCE.jsonl  (canonical)        │
                              │   EVIDENCE.md     (rendered only)    │
                              │   cells/<cell-id>/ …                 │
                              └──────────────┬───────────────────────┘
                                             │ script arithmetic
                                             ▼  Phase 166 CLOSE-01
```

Two boundaries in that diagram are the phase's whole point. The **upload chain never touches the judging path** (D-01): avrdude writes, a separate avrdude reads, and a rig script — not avrdude, not the app — compares. And the **host arm produces read artifacts but never judges them** (D-10): `dev consistency-check` emits `run_NN.bin` files and an exit code, and only the files feed the verdict while the exit code is recorded unjudged beside it.

### Recommended layout

```
.planning/v1.34/
├── PROCEDURE.md              # SC#3
├── images/
│   ├── firestarter_uno.control.hex        # naming must carry the arm — see Pattern 1
│   ├── firestarter_uno.v133.hex
│   ├── … (6 total)
│   └── SHA256SUMS.txt
├── tools/
│   ├── gen_addr_image.py     # copied from Phase 145, with its D-16 boundary comment intact
│   ├── capture_provenance.py # D-13
│   ├── judge_readback.py     # D-01/D-02: hex-extent compare + whole-flash datum
│   ├── judge_wrv.py          # D-10/RIG-04: full-device SHA over run_NN.bin vs written image
│   ├── probe_board.py        # D-14 signature probe (+ -xshowvector on uno328pb)
│   ├── touch_1200.py         # Leonardo bootloader entry (pyserial)
│   ├── render_evidence.py    # D-15
│   └── gate_record.py        # D-17 per-cell script gate
└── bench/
    ├── EVIDENCE.jsonl
    ├── EVIDENCE.md
    └── cells/<cell-id>/{provenance.json,flash_readback.bin,run_*.bin,logs/*}
```

`.gitignore` check: `/workspaces/.gitignore` anchors `/*.bin` to the repo root only and ignores `firestarter-runs/`, `.pio/` and `platformio.ini`. There is **no** pattern that would block `.planning/v1.34/**` binaries, and no `.planning/v1.34/**` rule of the kind that exists for `.planning/v1.7/**`. So committing `.hex` and `.bin` under `.planning/v1.34/` works as-is [VERIFIED: read `/workspaces/.gitignore`].

### Pattern 1: The arm must be in the filename, not only in a sibling manifest

**What:** `name_firmware.py` sets `PROGNAME = "firestarter_<RURP_BOARD_NAME>"` (`firestarter/name_firmware.py:76`), so **both arms build to the identical artifact name** — `.pio/build/uno/firestarter_uno.hex` on the control arm and on the v1.33 arm alike.
**When to use:** always, at the moment an image is copied out of `.pio/build/`.
**Why:** this is the same indistinguishability that motivates the whole phase, reproduced at the filesystem layer. Two files with the same name in the same build tree, one overwriting the other, is precisely how a wrong-arm cell happens — and `SHA256SUMS.txt` catches it only *after* the fact. Disambiguate at copy time.

```bash
# Verified: PROGNAME derives from the build flag, not from the env name
# firestarter/name_firmware.py:76 →  env.Replace(PROGNAME="firestarter_%s" % board_name)
# so BOTH arms produce .pio/build/uno/firestarter_uno.hex
cp .pio/build/uno/firestarter_uno.hex \
   "$V134/images/firestarter_uno.${ARM}.hex"     # ARM ∈ {control,v133}
```

### Pattern 2: Normalize the `.hex` to its own address extent with `avr-objcopy`

**What:** `avr-objcopy -I ihex -O binary <hex> <bin>` emits exactly the hex's contiguous span, starting at its lowest address.
**When to use:** D-02's judged compare, on every target.
**Measured on all three current images** [VERIFIED: run in this session]:

| env | hex records | lo | hi | span (B) | objcopy bin size | gaps | `flash_used` in `size_baseline.json` |
|-----|------------|----|----|---------|------------------|------|-------------------------------------|
| `uno` | 1436 | `0x0000` | `0x59A7` | 22952 | **22952** | **none** | 22952 ✓ |
| `uno328pb` | 1440 | `0x0000` | `0x59D7` | 23000 | **23000** | **none** | 23000 ✓ |
| `leonardo` | 1571 | `0x0000` | `0x6209` | 25098 | **25098** | **none** | 25098 ✓ |

Three properties fall out and all three matter. `lo == 0x0000` on every target, so the judged span is simply `[0, span)` and `head -c $span` of a full read-back is the comparable region — no offset arithmetic. There are **no gaps** in any of the three hexes, so objcopy's zero-fill-the-holes behaviour can never manufacture a false mismatch against a device that reads `0xFF` in a hole. And each span equals the recorded `flash_used`, which independently confirms these build artifacts are the tree they claim to be.

```bash
OBJCOPY=~/.platformio/packages/toolchain-atmelavr/bin/avr-objcopy   # NOT on PATH — record this path
"$OBJCOPY" -I ihex -O binary "$HEX" "$WORK/expected.bin"
SPAN=$(stat -c%s "$WORK/expected.bin")
head -c "$SPAN" "$WORK/readback_32768.bin" > "$WORK/actual_span.bin"
cmp -s "$WORK/expected.bin" "$WORK/actual_span.bin" && echo MATCH || echo MISMATCH
```

### Pattern 3: `dev consistency-check` produces, a rig script judges

**What:** the exact artifact contract, read off the source on both arms.
**When to use:** every W→R→V position.

Measured contract [VERIFIED: `firestarter_app/firestarter/eprom_operations.py:937-1136` on `cb189a9`, and the same block on `6bfa645`]:

- Artifacts: `<output_dir>/run_01.bin`, `run_02.bin`, … `run_{N:02d}.bin`. Two-digit zero-padded. **Identical filename format on both arms** (`run_{i:02d}.bin` at `eprom_operations.py:1010` v1.33 / `:1120` control).
- Each read spans `cmd_data["address"]` → `cmd_data["memory-size"]` and the writer seeks `address - start`, so with `address == 0` the file is the **full device size** from byte 0 — exactly what RIG-04 needs.
- Per-run log line: `Run {i}/{N}: SHA-256 {sha}  bytes={n}  elapsed={s:.2f}s`.
- Verdict block, printed to **stdout** (the pinned substrings): `Consistency check: PASS|FAIL` / `Chip: {chip}  Board: unknown-board  Port: {port}` / `Runs: N={n}` / `Distinct SHAs: {k}` / `Output dir: {dir}/`.
- Exit code `0` all-N-identical, `1` divergence, `2` hardware/serial error. **Not** bool-to-int wrapped, by explicit contract.
- `--keep-files` defaults **True**; `--no-keep-files` `shutil.rmtree`s the whole output dir.
- `--runs` minimum is 2 (`runs < 2` returns 2 before any state-machine call).

**Two traps in that contract the judge must handle.** On a hardware error the function returns `2` **early**, from inside the run loop — so fewer than N `run_NN.bin` files exist and the judge must *count the files* rather than assume N. And `Board: unknown-board` is a **hardcoded literal** in the print (`eprom_operations.py:1093`), not a lookup — so the verdict block carries no board identity at all and nothing in it can be used for provenance.

### Pattern 4: Prove the two arms' step lists diff empty by construction, then by diff

**What:** SC#3's "no step whose text differs between the arms" is satisfiable because the two host arms expose an identical CLI surface.
**Measured** [VERIFIED: AST comparison run in this session]: parsing `firestarter/cli_handlers.py` at `6bfa645` and at `cb189a9` and extracting every `@cli.command` / `@dev.command` / `@click.group` together with the complete set of `@click.option` and `@click.argument` names yields **25 commands on each arm and a set difference of exactly zero in both directions**.

Two consequences. PROCEDURE.md can be written with a single command vocabulary and one `$ARM_BIN` substitution, and the "side-by-side diff of the two arms' step lists is empty" criterion becomes trivially true rather than something to negotiate. But the *stronger* gate is available almost free and the planner should take it: render each arm's `--help` for every command from its own venv and diff those, because that catches a divergence in **help text** — and therefore in behaviour the source-level name comparison cannot see. Standing memory `reference_click_docstrings_are_user_facing_help_text` records that this project has already been bitten by Click docstrings being user-facing; the app-arm diff includes a commit literally titled *"fix(cli): restore Click command docstrings"*, so help text **has** moved between these two arms even though option names have not.

### Pattern 5: `capture_provenance.py` — required-argument-or-refuse

**What:** D-13's shape. Every machine-readable field gathered by the tool; the one human field (`--shield-rev`) is a required argument with no default.
**When to use:** once per cell, **before** the first test step (RIG-02's "before any test step executes").

```python
# .planning/v1.34/tools/capture_provenance.py  (shape only)
ap.add_argument("--shield-rev", required=True,
                choices=["Rev 2.0", "Rev 2.2", "Modified Rev 0"])   # operator-declared, no default
ap.add_argument("--cell-id",    required=True)
ap.add_argument("--arm",        required=True, choices=["control", "v133"])
ap.add_argument("--port",       required=True)
ap.add_argument("--chip",       required=True)
# everything below is gathered, never accepted as an argument:
#   board signature        ← avrdude wrong-`-p` probe (two parse routes)
#   controller: string     ← <arm>/bin/firestarter -v -p <port> hw   | grep '^I: FW: '
#   firmware readback sha  ← judge_readback.py's recorded verdict for this flash
#   host arm sha           ← git -C <worktree> rev-parse HEAD
#   host arm porcelain     ← git -C <worktree> status --porcelain   (MUST be empty)
#   host arm __file__      ← <arm>/bin/python -P -c 'import firestarter; print(firestarter.__file__)'
#   config dir sha         ← sha256 over the sorted file tree of $FIRESTARTER_CONFIG_DIR
#   interpreter            ← <arm>/bin/python --version
#   dep versions           ← <arm>/bin/python -m pip freeze     (see Pitfall 8)
```

The `-P` on that `__file__` line is not stylistic. See Pitfall 1 — without it the field is `None`.

### Pattern 6: Per-cell step order is *derived*, not invented

The open question "PROCEDURE.md's exact step ordering" is largely determined by two standing rules colliding with D-05.

Standing rule (`feedback_chip_out_before_sideload`, as corrected by the operator 2026-06-03): the chip must be out of the socket before any `pio run -t upload` / `avrdude` / `fw -i` **on the two Uno-class boards only** — the Leonardo is exempt and is flashed with the chip seated. An avrdude **read** is the same electrical situation as a write (bootloader active, the AVR's shield-wired GPIO lines exercised), so the chip-out window must cover the flash **and** its read-back proof, not just the flash. That makes the derived order:

1. Operator mounts the shield on the board; **declares the shield revision** (silkscreen is authoritative — `hw_revision` cannot distinguish 2.0 / 2.2 / Modified Rev 0).
2. Re-verify port identity for **this** cell: signature probe (authoritative) + `controller:` string. Never inherited from a previous task — `/dev/ttyACM*` numbering shuffles across replug.
3. **Uno-class only:** operator removes the chip and confirms.
4. Flash arm A. Read back with `-A`. Judge against arm A's hex extent. Record both the judged verdict and the whole-flash datum.
5. **Uno-class only:** operator seats chip 1 (W27C512, DIP28) and confirms.
6. Pot: state the target (VPP in band for `vpp_mv 12000`), operator sets it and reports, **one** confirming read. No monitor loop.
7. Chip 1: write the position's own image → `dev consistency-check` → rig judge over 65536 B.
8. Operator swaps chip 1 → chip 2 (W29C020, DIP32). **No pot re-adjustment** — both chips declare `vpp_mv 12000` (DB-verified below).
9. Chip 2: same, over 262144 B.
10. Arm switch: back to step 3 for arm B.
11. Teardown; record final board/arm state.

Two things this ordering buys. The pot is set **once per cell**, not once per chip, because the DB agrees on 12000 mV for both parts — CONTEXT asked the procedure to exploit that and this is where it lands. And the flash+read-back proof sits inside the chip-out window on Uno-class boards, so D-05's per-cell read-back costs no extra chip handling.

### Anti-Patterns to Avoid

- **Using `firestarter fw -i` to flash.** Needs a handshake (blocks the D-03 cross-flash), ignores `--board` (standing memory), and omits `-xnometadata` on urclock — a different flash content from PIO's path on `uno328pb`.
- **Reading back without `-A`.** Yields a truncated, variable-length file on urclock and avr109. See Pitfall 2.
- **Comparing a `uno328pb` read-back against the raw `.hex` before probing for a vector bootloader.** See Pitfall 3 — false RED on every flash.
- **Running any `import firestarter` provenance probe with `cwd=/workspaces`.** See Pitfall 1 — silently yields `None`.
- **Running any `pio` command with `cwd=/workspaces`.** See Pitfall 4 — hard crash from a malformed generated `platformio.ini`.
- **Copying `gen_addr_image.py` (or any rig tool) into a sub-repo.** Its own docstring forbids it; D-16 and the Out-of-Scope table forbid it.
- **Judging W→R→V on `dev consistency-check`'s exit code.** RIG-04 forbids it, and Pitfall 6 explains why a `0` there does not mean what it looks like.
- **Scraping the app's `Write to X successful (N.NNs)` line as the sole write-duration source.** It is not emitted on failure. See the BOARD-04 recommendation.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| `.hex` → binary of its address span | an Intel-hex parser | `avr-objcopy -I ihex -O binary` (path recorded) | Verified exact on all three images, gaps confirmed absent. One line. |
| Address-attributable bench image | a new generator | `.planning/phases/145-bench-validation/images/gen_addr_image.py`, copied | Already carries the D-16 boundary comment and the decode helper that root-caused Phase 97's A18 aliasing. |
| N reads of a chip | a read loop calling `read` N times | `dev consistency-check --runs N --keep-files` | Reuses the production read state machine verbatim (its own docstring forbids a parallel implementation), keeps the binaries, and reports divergence offsets. |
| Board identity | a handshake parser | the avrdude wrong-`-p` signature probe | RIG-02 forbids handshake identity, and the handshake is exactly the weak oracle that produced this project's v1.5 board-identity confusion. |
| Per-target flash flags | your own avrdude command | `pio run -t upload -e <env>` | PIO already supplies `-xnometadata` for urclock, the 1200-baud touch and the port-wait for avr109, and the `-C <its own avrdude.conf>` pairing. |
| Evidence-table arithmetic | a hand-maintained Markdown table | `EVIDENCE.jsonl` + a renderer | v1.15/v1.18 proved the paired-file shape drifts; D-15 makes CLOSE-01 a script. |
| A test framework for the rig tools | pytest (not installed) | the project's own gate-script shape: `def main() -> int` + `sys.exit(main())`, run with plain `python3`, asserted by exit code | `.planning/v1.18/bench/check_*.py` is the precedent; the meta repo has no `pyproject.toml`, no `pytest.ini`, no `tests/`. |

**Key insight:** almost nothing in this phase is new capability. Every mechanism it needs already exists somewhere in this repo set — the read-stability harness, the address-stamped generator, the signature probe, the evidence schema, the gate-script convention, the committed-artifact + `SHA256SUMS.txt` convention. The phase's real work is *composition plus one genuinely unproven mechanism* (the flash read-back), and the plan's risk should be concentrated there rather than spread evenly.

---

## Runtime State Inventory

Not a rename phase, but this phase is built **on top of** live runtime state that nothing in the plan creates and several parts of the plan will silently inherit. Each row was checked, and where nothing was found that is stated rather than left blank.

| Category | Items found | Action required |
|----------|-------------|------------------|
| **Stored data / device state** | Arduino EEPROM holds `rurp_configuration_t` (R1/R2 calibration, hw_revision override) on each of the three boards. A flash-only `-D -U flash:w:` leaves it untouched (standing memory `feedback_bench_boards_are_fw_flash_testbed`). Not read in this session — no board attached. | **None** for the flash path; but PROCEDURE.md should record the calibration values per cell, because they are an electrical input to every VPP reading and they are *not* in git. |
| **Installed editable package (host)** | `/home/vscode/.local/lib/python3.12/site-packages/__editable__.firestarter-3.0.0b32.pth` + `__editable___firestarter_3_0_0b32_finder.py` with `MAPPING = {'firestarter': '/workspaces/firestarter_app/firestarter'}`. `/home/vscode/.local/bin/firestarter` exists and resolves to it → **a third, un-named arm on `PATH`**. Confirmed live: `firestarter --version` → `Firestarter, version 3.0.0b32` from `/workspaces/firestarter_app`. | **Code/procedure**: PROCEDURE.md forbids bare `firestarter`; D-17's record gate must **reject** any recorded command line whose first token is not one of the two absolute arm binary paths. Neutralizing the install is explicitly deferred. |
| **Stale venvs in the app repo** | `/workspaces/firestarter_app/.venv` — `pyvenv.cfg` says `version = 3.13.5`, `home = /bin`, `command = /bin/python -m venv /home/henrik/dev/henrik/git/firestarter_app/.venv`; `bin/python → /bin/python` which **does not exist**. `.venv/ci-replica` — uv-managed cpython-3.11 whose interpreter is also gone. **Both are broken and non-executable here.** | **None** — but CONTEXT.md §Reusable Assets cites these as "precedent for per-purpose venvs". They exist; they do not work. Do not reuse or extend either; create the arm venvs fresh, outside the app repo tree (`.venv/` is gitignored in the app repo, so a nested arm venv would vanish from provenance). |
| **Generated `platformio.ini` at the meta-repo root** | `/workspaces/platformio.ini`, 292 lines, **untracked**, generated by `.devcontainer/gen-platformio-ini.py`, gitignored. It is **malformed**: a duplicate `[platformio]` section at line 26 makes every `pio` invocation with `cwd=/workspaces` abort with `DuplicateSectionError`. Reproduced: even `pio --version` crashes there. | **Procedure**: every `pio` command must run with `cwd=/workspaces/firestarter` (or `-d`/`-c` pointing there). Do **not** "fix" the generated file — it is devcontainer runtime state, regenerated by post-create, and outside this phase's boundary. |
| **PlatformIO package tree (unpinned)** | `~/.platformio/platforms/atmelavr/.piopm` records `"requirements": null` — the platform was installed with **no version constraint**, and `firestarter/platformio.ini` writes a bare `platform = atmelavr` with no `@version`. The versions in `size_baseline.json` are **documentation, not enforcement**. Currently installed versions all match the pins. | **Record, do not change.** D-04's whole point is that the committed `.hex` bytes survive a toolchain move. The plan should snapshot the five package versions into the images manifest (I have them; see Standard Stack) and state that nothing enforces them. |
| **Two avrdude installations** | `/usr/bin/avrdude` **7.1** (uses `/etc/avrdude.conf`; the host app resolves this one via `which`, and passes no `-C` because `avr_tool.py:50` only supplies a conf below version 7.0) and `~/.platformio/packages/tool-avrdude/avrdude` **8.1** (PIO passes `-C <its own avrdude.conf>`). A third, stale `tool-avrdude@1.60300.200527` = avrdude **6.3**. | **Pin one, record it.** The rig's read-back must always name its avrdude binary **and** its conf explicitly, or a chain-version mismatch becomes an invisible variable across cells. |
| **Secrets / env vars** | `FIRESTARTER_CONFIG_DIR` — currently **unset**, and `~/.firestarter` does **not** exist (clean slate, as CONTEXT states). `UV_CACHE_DIR` — unset, and `/home/vscode/.cache` is **root-owned `drwxr-xr-x`**, so `uv` fails with `Permission denied` until it is set. No SOPS key, no token, no CI variable is involved in this phase. | **Create + record**: seed `FIRESTARTER_CONFIG_DIR` once, SHA it, re-verify after each cell (D-07). **Set `UV_CACHE_DIR`** (or chown the cache dir) or the venv creation step fails. |
| **Build artifacts** | `/workspaces/firestarter/.pio/build/{uno,uno328pb,leonardo}` currently hold **v1.33-arm** images dated 2026-08-25, whose spans equal `size_baseline.json`'s `flash_used`. There are also 11 `core.NNNNN` crash dumps totalling ~7 MB in the firmware repo root (untracked litter, unrelated). | **Procedure**: `.pio/build/<env>/firestarter_<board>.hex` is **overwritten by the other arm's build with the identical name** (Pattern 1). Copy out to an arm-tagged filename immediately after each build, and prefer `rm -rf .pio/build/<env>` between arms so a failed build cannot leave the previous arm's artifact in place looking fresh. |

---

## Common Pitfalls

### Pitfall 1 — `import firestarter` resolves to the *firmware* directory and yields `__file__ = None`

**What goes wrong:** D-08's third leg — `python -c 'import firestarter; print(firestarter.__file__)'` — prints `None` instead of a path, on **every** interpreter including the arm venv's own, whenever the working directory is `/workspaces`.

**Measured** [VERIFIED: run in this session]:

```
$ cd /workspaces && $ARM_VENV/bin/python -c "import firestarter; print(repr(firestarter.__file__)); print(firestarter.__path__)"
None
_NamespacePath(['/workspaces/firestarter'])
```

**Why it happens:** `/workspaces` is the meta-repo root and it contains a directory literally named `firestarter` — the **firmware** repo. With `python -c`, `sys.path[0]` is the cwd, so `/workspaces/firestarter` is discovered as a PEP 420 namespace package portion. Namespace packages have no `__file__`. The setuptools editable finder is *appended* to `sys.meta_path`, i.e. it runs **after** the default `PathFinder`, so it loses.

**How to avoid:** spell the probe `$ARM_VENV/bin/python -P -c '…'` or set `PYTHONSAFEPATH=1`. Both were verified to restore the correct path:

```
$ cd /workspaces && $ARM_VENV/bin/python -P -c "import firestarter; print(firestarter.__file__)"
'/…/arm-control/firestarter/__init__.py'
```

**Warning signs:** a provenance JSON with `"host_arm_file": null`, or a `capture_provenance.py` that crashes on `.startswith()` against `None`. Note the console-script entry point is **not** affected — `$ARM_VENV/bin/firestarter --version` works fine from `/workspaces` — so the symptom appears only in the one place D-08 puts it, which is exactly the shape of trap this project's memory keeps recording.

### Pitfall 2 — `avrdude -U flash:r:out.bin:r` does **not** produce 32768 bytes

**What goes wrong:** D-02's "SHA of the full 32768 B read-back" is not what the command returns. The file is a variable length that depends on where the last non-`0xFF` byte happens to sit, so its SHA is not a stable provenance datum and `head -c $SPAN` on it may read past the end.

**Why it happens — the authoritative text**, from the locally-installed man page for the exact avrdude in use:

> "When reading any kind of flash memory area (including the various sub-areas in Xmega devices), the resulting output file will be **truncated to not contain trailing 0xFF bytes** which indicate unprogrammed (erased) memory. Thus, if the entire memory is unprogrammed, this will result in an output file that has no contents at all."
> — `avrdude(1)`, `-U` section [VERIFIED: `man avrdude` on avrdude 7.1, `/usr/share/man/man1/avrdude.1.gz`]

**How to avoid — `-A`:**

> "**-A** Disable the automatic removal of trailing-0xFF sequences in file input that is to be programmed to flash **and in AVR reads from flash memory**. … **-A is engaged by default when specifying -c arduino.**"
> — same man page [VERIFIED]

So `-A` gives a fixed 32768 B read. It is **already the default on `-c arduino` (uno) and is NOT the default on `-c urclock` (uno328pb) or `-c avr109` (leonardo)**. Passing `-A` explicitly on all three normalizes the three chains to one 32768 B artifact — which is also what SC#3's arm-agnostic single-command-vocabulary needs. `-A` was confirmed to parse on avrdude 7.1 (it failed at port-open, not at option parsing, whereas an invalid `-Z` is rejected as `invalid option`) [VERIFIED: run in this session].

**Warning signs:** a `flash_readback.bin` whose size is not exactly 32768; a whole-flash SHA that changes between two reads of an unchanged board.

### Pitfall 3 — on `uno328pb`, avrdude urclock may patch the reset vector, producing a **false RED at 0x0000 on every flash**

**What goes wrong:** the judged compare starts at `0x0000` on all three targets (Pattern 2). If the operator's urboot on the 328PB is a **vector** bootloader, avrdude's urclock programmer rewrites the application's reset vector and one designated interrupt vector *before* writing, so the flash contents at those addresses will never equal the `.hex` bytes. The independent read-back compare would report MISMATCH on a correctly-flashed board, every single time — and because urclock applies the same patch to its own verification, avrdude's built-in verify would still pass. That is D-01's premise inverted: the independent check is the one that lies.

**Why it happens:**

> "The interrupt vector table of every application burned with a vector bootloader needs to be patched before being uploaded: the designated interrupt vector needs to be a copy of the original reset vector with the application start, and the reset vector then needs to be modified to jump to the start of the bootloader. Avrdude's urclock programmer will patch the application automatically and will apply the patch for upload and verification automatically."
> [CITED: github.com/stefanrueger/urboot — docs; corroborated by `avrdude(1)`'s `-xrestore` text, which says patching is what `-xrestore` *suppresses*]

Supporting local evidence: `avrdude -c urclock -x?` on 7.1 lists `-xshowvector  Show vector bootloader vector # and name and exit` and `-xvectornum=<arg>  Treat bootloader as vector b/loader using this vector` — the probes exist precisely because this distinction is real [VERIFIED: run in this session]. Circumstantially, the 384 B bootloader size this project has recorded for `uno328pb` does not align to any ATmega328PB hardware boot-section boundary, which is characteristic of a vector bootloader rather than a BOOTRST one.

**How to avoid:** at bring-up, **before** arming the comparator on this target, run `avrdude -c urclock -p atmega328pb -b 115200 -P <port> -xshowall` and `-xshowvector` and record the output. Then choose, and record the choice:
- **not** a vector bootloader → judge `[0, span)` unchanged;
- **is** a vector bootloader → either apply the same patch to the reference before hashing, or exclude the two patched words from the judged span and state the exclusion. The latter is SC#2's own escape hatch ("a named alternative check that is itself falsifiable and whose limits are stated") and it stays falsifiable: 23000 bytes minus 4 still differ enormously between the two arms, so D-03's cross-flash still detects a wrong arm.

**Related, separate urclock hazard — metadata.** urclock writes a filename + **date** block into flash below the bootloader unless `-xnometadata` is given. PlatformIO's builder already appends it (`~/.platformio/platforms/atmelavr/builder/main.py:219-220`: `if upload_protocol == "urclock": env.Append(UPLOADERFLAGS=["-xnometadata"])`) — but the host app's `avr_tool.py` does **not**. Two consequences: use PIO's path, not the app's; and if metadata ever is written, the *whole-flash* SHA becomes date-dependent and non-reproducible while the judged span (which ends at `0x59D7`, far below the metadata) stays clean. [VERIFIED: read `builder/main.py`, `firestarter/avr_tool.py:139-146`]

### Pitfall 4 — any `pio` command with `cwd=/workspaces` crashes

**What goes wrong:** `pio --version` — never mind `pio run` — aborts with `InvalidProjectConfError … 'section 'platformio' already exists'` plus a second traceback from the telemetry atexit hook.
**Why:** `/workspaces/platformio.ini` (generated, untracked, gitignored) concatenates a `[platformio]` path-mapping header onto a copy of the firmware `platformio.ini`, which has its own `[platformio]` at line 26. `configparser` refuses duplicate sections.
**How to avoid:** always `cd /workspaces/firestarter` first, or pass `-d /workspaces/firestarter`. Record the invocation with its working directory, since the same command string succeeds or fails depending on cwd — which is precisely the kind of implicit input RIG-05 exists to eliminate. [VERIFIED: reproduced in this session]

### Pitfall 5 — the Leonardo bootloader window, and the fact that `flash:r` has never run on this bench

**What goes wrong:** on `leonardo` the read-back may simply not complete. Caterina must be entered by a 1200-baud open/close touch, it exits back to the sketch after roughly 8 s of inactivity, and on many boards it enumerates as a *different* `/dev/ttyACM*` than the sketch does.
**What is actually known here:**
- PlatformIO handles this for uploads by doing `TouchSerialPort($UPLOAD_PORT, 1200)` and then `WaitForNewSerialPort(before_ports)` — i.e. it expects a **new** port (`builder/main.py:84-88`) [VERIFIED].
- The host app handles it differently: `avr_tool.py:117-124` opens the port at 1200 baud, closes it, sleeps 2 s, and then uses **the same port** — no wait-for-new. And on this operator's bench that has **worked**: `.planning/debug/resolved/fw-update-blocked-release-fw.md:283` records `fw --install | leonardo / ttyACM0 | b17 → b19 OK — -p atmega32u4 -c avr109 -b 57600, 5.51s`. So on this specific Leonardo, Caterina comes back on the same node and a 5.51 s avr109 session fits inside the window. [VERIFIED: read]
- avrdude's own device table for avr109/32u4 reports flash as paged, 32768 B total / 128 B blocks / 256 pages with a `ReadBack` column, and identifies the Caterina programmer as `CATERIN` with auto-address-increment — so avrdude believes it can read. I found **no authoritative statement** that a full 32 KiB `flash:r` succeeds against Caterina. [LOW confidence — websearch only]
- **And the decisive negative:** `flash:r` (or `flash:v`) appears **nowhere** in this project's history. A grep of every `.md` under `.planning/` returns two hits, both of them Phase 160's own CONTEXT and discussion log. No cell, no debug session, no bench record has ever read an AVR's flash back. [VERIFIED: `grep -rn "flash:r\|flash:v" --include=*.md .planning/`]

**How to avoid:** treat the read chain as unproven on **all three** targets and prove them one at a time at bring-up, cheapest first (`uno`, where `-A` is already default and the chain is plain STK500v1), then `uno328pb`, then `leonardo`. For the Leonardo read specifically: reuse the app's proven 1200-baud-then-same-port shape in a small `touch_1200.py` (pyserial 3.5 is available system-wide), start avrdude promptly, and if the window proves too short, fall back to SC#2's named-alternative check with its limits stated rather than forcing the full read.

**Warning signs:** `butterfly_recv(): programmer is not responding`; a read that returns 0 bytes; a read that succeeds only on the first attempt after a power cycle.

### Pitfall 6 — `dev consistency-check` exit 0 does **not** mean the chip holds what was written

**What goes wrong:** the natural reading of `Consistency check: PASS` is "the read-back matched". It does not mean that. The verdict is `0 if len({sha per run}) == 1 else 1` (`eprom_operations.py:1084-1086`) — it compares the N reads **to each other**, never to the written image. A chip that reliably returns the *wrong* bytes passes.
**Why it matters here more than usual:** this is the exact false green D-12 is insuring against. If LOOP-06 skips already-correct bytes and the v1.33 arm's write is a near-no-op over the previous arm's image, three stable reads of the *previous* arm's content produce `PASS` with `Distinct SHAs: 1`.
**How to avoid:** exactly what D-10 and RIG-04 prescribe, and the plan must not soften it — the rig judge computes SHA-256 over the full device size for each `run_NN.bin` and compares against the **written image's** SHA. The app's `0/1/2` is recorded beside it, unjudged, and a disagreement is a finding. Distinct masks per (cell × chip × arm) make a stale-content pass detectable rather than plausible.

### Pitfall 7 — write duration is not reportable the same way on both arms *and* both outcomes

**What goes wrong:** BOARD-04 needs "a measured write duration" for all 12 positions, including cell A2 where the write is **expected to fail on both arms**. The app's own figure — `Write to {CHIP} successful ({t:.2f}s).` at `eprom_operations.py:1934` — is emitted **only on success**. A failed write produces no duration line at all, so 4 of the 12 positions would have a blank where a number is required.
**Also relevant:** intra-block progress frames (`MSG_DATA_PROGRESS`) are, by the firmware's own documentation, **compiled out on `SERIAL_ON_IO` targets** — i.e. present on `leonardo` and native only, absent on `uno` and `uno328pb` (`firestarter/CLAUDE.md`, 0x07/0x08/0x0B rows). So a frame-scraping approach is not available on two of the three boards either.
**Recommendation for the open question:** **wall-clock around the command** is the only measure that exists for every arm, every target and every outcome, and it is trivially arm-agnostic (one procedure step, no per-arm text). Record the app's own `(N.NNs)` figure **alongside** it when present, as a second unjudged datum — the same "two oracles recorded separately, disagreement visible" shape as Phase 145 D-06. Note explicitly that wall-clock includes process start-up and serial handshake, so it is comparable A-to-B but is **not** comparable to v1.31's 0.37 s figure unless that figure was taken the same way; BOARD-04 asks for exactly that comparison, so the plan must resolve which measure v1.31's 0.37 s was.

### Pitfall 8 — the two arm venvs can resolve *different* dependency versions

**What goes wrong:** the app pins its dependencies as floors, not pins (`pyserial>=3.5`, `requests>=2.20`, `tqdm>=4.60`, `click>=8.1`, `rich>=14.0`, `packaging>=21.0` — `pyproject.toml:43-50`). Creating the two arm venvs at different moments, or with a cold cache versus a warm one, can resolve different versions into them. That silently adds a **second** variable to a comparison whose entire premise is one variable.
**Concrete evidence this is live:** `click` published a release **today** (`2026-08-26`), per the legitimacy check. A venv created before and after that release differ.
**How to avoid:** create both arm venvs in the **same** step, then assert equality — `diff <(armA/bin/python -m pip freeze | grep -v '^firestarter') <(armB/bin/python -m pip freeze | grep -v '^firestarter')` must be **empty** — and record the freeze output in each cell's provenance block. This is cheap, and it is the same class of check as D-08's porcelain leg.

### Pitfall 9 — `uv` fails on a root-owned cache directory

**What goes wrong:** `uv venv` aborts with `Failed to initialize cache at /home/vscode/.cache/uv: Permission denied (os error 13)`.
**Why:** `/home/vscode/.cache` is `drwxr-xr-x root root` — the `vscode` user cannot create a subdirectory in it.
**How to avoid:** export `UV_CACHE_DIR` to a writable path (I used a scratch dir successfully), or use stdlib `venv` + `pip`. Whichever, record it: a venv-creation step that only works with an env var set is exactly a field RIG-05 requires to be in the record rather than in the session. [VERIFIED: reproduced and worked around in this session]

---

## Code Examples

Every command below was either executed in this session or read directly out of the source/manifest cited. Commands that **cannot** be executed without a board are marked.

### 1. Build one arm's three images and copy them out arm-tagged

```bash
# VERIFIED end-to-end for `uno` in this session (2.04 s, byte-identical result).
cd /workspaces/firestarter                    # MANDATORY — see Pitfall 4
git checkout 8695ee5                          # or 5759dc8; record the sha, assert porcelain empty
git status --porcelain                        # must be EMPTY

for E in uno uno328pb leonardo; do
  rm -rf ".pio/build/$E"                      # cold; both arms build the SAME filename (Pattern 1)
  /usr/local/bin/pio run -e "$E"
  cp ".pio/build/$E/firestarter_$E.hex" \
     "/workspaces/.planning/v1.34/images/firestarter_$E.$ARM.hex"
done
( cd /workspaces/.planning/v1.34/images && sha256sum *.hex > SHA256SUMS.txt )
```

### 2. Reproducibility check — the measured result

```bash
# VERIFIED in this session, on the v1.33 arm at 5759dc8, tree porcelain-clean:
#   cp .pio/build/uno/firestarter_uno.hex /tmp/before.hex
#   rm -rf .pio/build/uno && pio run -e uno        → SUCCESS in 2.04 s
#   sha256sum before/after
# before: 6823e6f939d336754498baafc34d6517675e38102accf625f360e3ca16b0a608
# after : 6823e6f939d336754498baafc34d6517675e38102accf625f360e3ca16b0a608
#   cmp  → BYTE-IDENTICAL
# The prior build was dated 2026-08-25 and this rebuild ran 2026-08-26, so a date
# leak would have shown. It did not. No __DATE__/__TIME__/__FILE__ exists on
# either arm under src/ include/ lib/ (git grep, both SHAs, no matches).
```

### 3. Flash, then read back independently, then judge (`uno`)

```bash
# NOT RUN — no board attached (/dev/ttyACM* and /dev/ttyUSB* both absent this session).
# Command shapes verified from ~/.platformio/platforms/atmelavr/builder/main.py:180-230
# and the boards/*.json manifests.

# --- write (PIO owns the per-target flags) ---
cd /workspaces/firestarter
pio run -e uno -t upload --upload-port /dev/ttyACM1
#   expands to: avrdude -p atmega328p -C ~/.platformio/packages/tool-avrdude/avrdude.conf \
#                       -c arduino -b 115200 -D -P /dev/ttyACM1 \
#                       -U flash:w:.pio/build/uno/firestarter_uno.hex:i

# --- read back INDEPENDENTLY (D-01) ---
AVRDUDE=/usr/bin/avrdude                       # 7.1 — record which binary and which conf
"$AVRDUDE" -A -p atmega328p -c arduino -b 115200 -P /dev/ttyACM1 \
           -U flash:r:$CELL/flash_readback.bin:r
#   -A is already the default for -c arduino, but pass it so the SAME step text
#   works on all three chains (SC#3) and so the 32768 B length is explicit.
test "$(stat -c%s $CELL/flash_readback.bin)" -eq 32768 || echo "FAIL: not 32768 B"

# --- judge (D-02) ---
OBJCOPY=~/.platformio/packages/toolchain-atmelavr/bin/avr-objcopy
"$OBJCOPY" -I ihex -O binary "$IMAGES/firestarter_uno.$ARM.hex" $CELL/expected.bin
SPAN=$(stat -c%s $CELL/expected.bin)                        # uno: 22952
head -c "$SPAN" $CELL/flash_readback.bin > $CELL/actual_span.bin
JUDGED_EXPECT=$(sha256sum $CELL/expected.bin    | cut -d' ' -f1)
JUDGED_ACTUAL=$(sha256sum $CELL/actual_span.bin | cut -d' ' -f1)
WHOLE_FLASH=$(sha256sum $CELL/flash_readback.bin | cut -d' ' -f1)   # UNJUDGED datum
```

### 4. Per-target parameter table — read off the manifests, not from memory

```
# ~/.platformio/platforms/atmelavr/boards/uno.json           → mcu atmega328p , protocol arduino, speed 115200
# ~/.platformio/platforms/atmelavr/boards/ATmega328PB.json    → mcu atmega328pb, protocol urclock, speed 115200,
#                                                               build.core MiniCore, upload.maximum_size 32768
# ~/.platformio/platforms/atmelavr/boards/leonardo.json       → mcu atmega32u4 , protocol avr109 , speed 57600,
#                                                               use_1200bps_touch, wait_for_upload_port,
#                                                               disable_flushing
# All three ALSO carry `board_upload.maximum_size = 32768` from firestarter/platformio.ini,
# and uno328pb additionally needs zero_bootloader_reserve.py to zero MiniCore's 384 B
# urclock subtraction (a bare INI override does NOT reach the ceiling there).
```
[VERIFIED: read all three board JSONs, `firestarter/platformio.ini`, `firestarter/zero_bootloader_reserve.py`]

### 5. Bring-up probes on `uno328pb` — run these BEFORE arming the comparator

```bash
# NOT RUN — no board attached. Option names verified from `avrdude -c urclock -p m328pb -x?`.
AV=/usr/bin/avrdude ; P=/dev/ttyUSB0
"$AV" -c urclock -p atmega328pb -b 115200 -P "$P" -xshowall        # everything at once
"$AV" -c urclock -p atmega328pb -b 115200 -P "$P" -xshowvector     # ← THE Pitfall-3 question
"$AV" -c urclock -p atmega328pb -b 115200 -P "$P" -xshowbootsize
"$AV" -c urclock -p atmega328pb -b 115200 -P "$P" -xshowversion    # bootloader caps incl. read
```

### 6. Board identity by signature (D-14 / RIG-02) — both parse routes

```bash
# Mechanism from .planning/todos/pending/avrdude-mcu-detection-fallback.md, bench-confirmed
# 2026-05-21 and re-confirmed 2026-08-19 (memory: project_uno328pb_correction).
# Route 1 — deliberately WRONG -p, no -U:
avrdude -c urclock -P /dev/ttyUSB0 -b 115200 -p m328p -n 2>&1 \
  | grep -oP 'connected part \K\w+'                      # → ATmega328PB
# Route 2 — verbose, correct -p:
avrdude -c urclock -P /dev/ttyUSB0 -b 115200 -p m328pb -n -v 2>&1 \
  | grep -oP 'device signature = \K0x[0-9a-f]+'          # → 0x1e9516
# Known-good mapping on THIS bench (2026-08-19, direct measurement):
#   0x1e950f = m328p   (uno)        0x1e9516 = m328pb (uno328pb)   0x1e9587 = m32u4 (leonardo)
# NOTE: -c arduino against the 328PB board fails "unable to open programmer" — itself a signal.
```

### 7. Build the two host arms (D-06) — this whole block was executed and verified

```bash
# VERIFIED end-to-end in this session against the CONTROL sha, then torn down.
export UV_CACHE_DIR=/some/writable/path        # MANDATORY — Pitfall 9

git -C /workspaces/firestarter_app worktree add --detach "$ARMS/control" 6bfa645
git -C /workspaces/firestarter_app worktree add --detach "$ARMS/v133"    cb189a9

for A in control v133; do
  ( cd "$ARMS/$A" \
    && uv venv --python 3.12 .venv \
    && uv pip install --python .venv/bin/python -e . )
done

# --- the three D-08 legs, all three verified working ---
git -C "$ARMS/$A" rev-parse HEAD                     # → 6bfa645…  (names the arm)
git -C "$ARMS/$A" status --porcelain                 # → EMPTY     (observed empty)
"$ARMS/$A/.venv/bin/python" -P -c \
  'import firestarter; print(firestarter.__file__)'  # → …/$A/firestarter/__init__.py
#                     ^^ the -P is load-bearing. Without it: None. See Pitfall 1.

# --- confirmations ---
"$ARMS/$A/.venv/bin/firestarter" --version                     # → Firestarter, version 3.0.0b32
"$ARMS/$A/.venv/bin/firestarter" dev consistency-check --help  # → registered on BOTH arms
diff <("$ARMS/control/.venv/bin/python" -m pip freeze | grep -v ^firestarter) \
     <("$ARMS/v133/.venv/bin/python"    -m pip freeze | grep -v ^firestarter)   # MUST be empty (Pitfall 8)

# teardown, if ever needed:
git -C /workspaces/firestarter_app worktree remove --force "$ARMS/$A"   # verified clean
```

**Where should `$ARMS` live?** Not decided by CONTEXT, and it matters. Under `/workspaces/…` it appears as an untracked directory in the meta repo (and `.planning/v1.34/arms/` would get committed, which nobody wants). Under `/tmp` it does not survive a container restart, which is fatal for a multi-week milestone. **Recommendation:** a sibling directory outside both repos with a one-line meta `.gitignore` entry — e.g. `/workspaces/.v1.34-arms/` plus `/.v1.34-arms/` in `/workspaces/.gitignore` — and the absolute path recorded verbatim in every cell's command lines, which is what RIG-05 wants anyway. Note `firestarter_app/.gitignore` ignores `.venv/`, so a venv **inside** each worktree stays out of the app repo's porcelain — which is what makes D-08's empty-porcelain leg work. That is convenient and should be stated, not discovered.

### 8. The W→R→V position (RIG-04) — command shapes

```bash
# NOT RUN — no board, no chip. Flags and artifact names verified from source.
BIN="$ARMS/$ARM/.venv/bin/firestarter"
export FIRESTARTER_CONFIG_DIR="$V134/config"        # D-07; resolved at process launch

# distinct, address-attributable image per (cell × chip × arm)  — D-12
python3 "$V134/tools/gen_addr_image.py" 65536 0x"$MASK" "$CELL/written.bin"
#   prints: <path>: 65536 bytes, mask=0xNN, sha256=<hex>, 0xFF_count=<n>

"$BIN" -v -p "$PORT" write w27c512 "$CELL/written.bin"        # NO -f, NO -b, NO --skip-erase
"$BIN" -v -p "$PORT" dev consistency-check w27c512 \
       --runs 3 --output-dir "$CELL/reads" --keep-files ; APP_VERDICT=$?
#   leaves $CELL/reads/run_01.bin run_02.bin run_03.bin   (count them — see Pattern 3)

python3 "$V134/tools/judge_wrv.py" \
        --written "$CELL/written.bin" --reads "$CELL/reads" \
        --expect-size 65536 --app-verdict "$APP_VERDICT"     # 262144 for w29c020
```

`--force` is forbidden anywhere in this milestone (Phase 145 D-17, carried forward). `-b` / `--no-blank-check` and `--skip-erase` are both present and **identical on both arms**, and neither belongs in a normal position — `--skip-erase` in particular corrupts a non-blank electrically-erasable chip while still reporting success (standing memory `reference_write_b_skips_erase`, whose `-b` framing is superseded by Phase 153's separate `--skip-erase` flag; the current help text is explicit that `-b` leaves the erase running). [VERIFIED: `cli_handlers.py:516-560` on both arms]

---

## Chip facts — verified against the shipped database

`firestarter_app/firestarter/data/chip_database.json`, keyed by vendor → rows [VERIFIED: parsed in this session]:

| CLI name | DB row `part_number` | Vendor | `size_bytes` | `pin_count` | `vpp_mv` | `algorithm` | `pinout` | `support_status` |
|----------|---------------------|--------|--------------|-------------|----------|-------------|----------|------------------|
| `w27c512` | `W27C512,W27E512` | WINBOND | **65536** | **28** | **12000** | **7** (`0x07`) | `DIP28_27512` | supported |
| `w29c020` | `W29C020,W29C020C,W29C022` | WINBOND | **262144** | **32** | **12000** | **5** (`0x05`) | `DIP32_SST39SF040` | supported |

Four things this settles.

RIG-04's byte counts are right: 65536 and 262144, straight from `electrical.size_bytes`. REQUIREMENTS.md's "DIP28, `0x07`, 64 KiB" and "DIP32, `0x05`, 256 KiB page-write" are both exact. CONTEXT's claim that **both chips declare `vpp_mv 12000`** is confirmed, so the procedure sets the pot **once per cell** and not once per chip — which is the single biggest simplification available to PROCEDURE.md's step list. And the package changes between the two chips (DIP28 → DIP32), so a physical re-seat between chips is unavoidable; combined with the chip-out rule that is what fixes the ordering in Pattern 6.

One thing to carry forward with care: the W27C512 row is shared with **W27E512**, which is one of the four known-dead parts (stuck erase bit @0x3d, D-32 silicon wear). Same DB row, different physical chip. The record must name the physical part, not the row.

And one thing the pot step must anticipate: Phase 145 D-17 records that the W27C512 has historically tripped a `VPP is high: 13.1V > 12.0V` init guard on this bench, that `--force` was previously used to bypass it, and that **the standing permission to do so was withdrawn**. If the guard fires, the pot is adjusted until VPP reads in band and the run restarts clean — the operator sets it himself, one confirming read, no monitor loop.

---

## Record substrate

`locked_columns` is **byte-identical** in `.planning/v1.15/bench/EVIDENCE.json` and `.planning/v1.18/bench/EVIDENCE.json` [VERIFIED: parsed both]:

```json
["chip","family","board","shield","blank_state","op","sha256","verdict","anomalies"]
```

v1.15 additionally carries `evid_extension_columns` — `["read_count","blank_check_result","write_image_seed_A","sha256_image_A","write_image_seed_B","sha256_image_B","cr01_risk"]` — plus a `locked_columns_note` explaining which of the observed keys are extensions. That two-tier shape (a stable locked core + a named, per-milestone extension list) is the pattern D-15 should pin, because it lets Phase 166 assert on the core while Phases 161–163 add what they need.

A v1.34 row has to satisfy RIG-02 and RIG-05, i.e. everything a re-run needs with nothing implicit. Concretely that means the nine locked columns plus at least: `cell_id` (`A1|A2|A3/B2|B1|B3`), `arm` (`control|v133`), `position_id` (cell × arm × chip — the CLOSE-01 primary key), `board_signature`, `controller_string`, `shield_rev_declared`, `fw_sha`, `fw_readback_sha_judged`, `fw_readback_sha_whole_flash`, `host_arm_sha`, `host_arm_porcelain_clean`, `host_arm_file`, `config_dir_sha`, `interpreter`, `image_mask`, `image_sha`, `read_count`, `read_shas` (a list), `app_verdict_unjudged`, `sha_verdict_judged`, `verdict_disagreement`, `write_duration_wallclock_s`, `write_duration_app_reported_s`, `commands` (the literal argv list), and `outcome` restricted to `validated|skipped-with-reason` per D-18.

Three shape conventions to carry across, all visible in the precedents. A negative control is recorded as **FIRED**, not as configured (v1.15's EVID-03) — which is the same discipline D-03 applies to the cross-flash. A blocked reading is `not measured — <blocking reason>` **on the same line**, never blank (v1.18's `dmm_pin1_v` is the canonical example, and it is exactly how the honesty ledger's VPP-under-load non-claim will read). And `verdict` and `anomalies` are prose fields that carry their own citation inline rather than pointing elsewhere.

**Artifact volume — worth a decision before the first cell, not after the twentieth.** D-16 puts read-back `.bin` files under `bench/cells/<cell-id>/`. At N=3 on the v1.33 arm and N=1 on the control arm, a full cell is `3×65536 + 3×262144` (v1.33) `+ 65536 + 262144` (control) ≈ 1.3 MB; five cells ≈ 6.5 MB; plus 20 written images (10×64 KiB + 10×256 KiB) ≈ 3.2 MB; plus 20 flash read-backs at 32768 B ≈ 0.7 MB. **Roughly 10.5 MB of binaries in a planning repo**, against Phase 145's 0.5 MB precedent. Nothing blocks it, but the planner should decide deliberately: commit everything (maximum auditability), or commit the small artifacts (the six `.hex`, the 20 written images, the 20 flash read-backs — about 4 MB) and record only SHAs for the large chip read-backs while keeping the files locally. Either is defensible; discovering the size at cell 18 is not.

---

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|--------------|------------------|--------------|----------------------|
| `write -b` also skips the erase | `-b` skips only the blank check; `--skip-erase` is a **separate** flag that skips the erase | Phase 153 (standalone `CMD_ERASE`) | Standing memory `reference_write_b_skips_erase` is superseded. The current help text is explicit: `-b` = "Skip the blank check before write (**erase still runs** if the chip supports it)". Present and identical on both arms — so it is not an A/B variable, but PROCEDURE.md must not carry the old framing. |
| `size_baseline.json`'s toolchain block treated as a pin | it is **documentation only** — `platform = atmelavr` is unversioned and the installed platform records `"requirements": null` | never enforced | SC#1's "or the divergence is recorded with its measured cause" is the live clause. Currently every installed version matches, so there is no divergence to record — but nothing prevents one. |
| `fw_board_identity: null` in `dev test` reports | fixed in v1.32 Phase 147 | 2026-08 | Not this phase's concern, but Phase 162 depends on it and the fix is why CHIP-02 treats a null as a regression. |
| avrdude 6.3 (`tool-avrdude@1.60300.200527`) | system **7.1** and PIO's **8.1** | — | Both current versions support `urclock`, `arduino` and `avr109`; 6.3 predates `urclock` entirely. The stale 6.3 package is still on disk — do not let a `--avrdude-path` config value point at it. |

**Deprecated / superseded in this project's own record:**
- The v1.7 bench note claiming the `/dev/ttyUSB0` board's "silicon is actually a plain Uno" is **stale**. Direct signature measurement on 2026-08-19 gives `0x1e9516` = ATmega328PB. Memory `project_uno328pb_correction` resolves it: the label referred to two different physical boards across sessions. The bring-up signature probe settles it again for v1.34, which is exactly why RIG-02 demands signature over handshake.
- `firestarter_app/.venv` and `.venv/ci-replica` are both dead in this container (Runtime State Inventory). CONTEXT cites them as precedent; they are not usable infrastructure.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|-------|---------|---------------|
| A1 | Caterina on this Leonardo supports a full 32768 B `flash:r` read via avr109 within its bootloader window | Pitfall 5 | **High.** D-01's mechanism is unavailable on one of three targets; SC#2's named-alternative escape hatch must be exercised, and the Leonardo is the v1.31 reference rig, so it is the cell whose comparability matters most. |
| A2 | The urboot bootloader on this 328PB supports `flash:r` at all | Pitfall 3, Pitfall 5 | **High.** Same as A1 for the second target. A 384 B urboot built without read capability would make avrdude refuse the read. `-xshowversion` answers it in one command. |
| A3 | The installed urboot on this 328PB **is** a vector bootloader (inferred from 384 B not aligning to any ATmega328PB boot-section boundary) | Pitfall 3 | **High, in both directions.** If true and unhandled: false RED on every `uno328pb` flash. If false and the plan pre-emptively excludes the vector words: the judged span is needlessly weakened. `-xshowvector` resolves it; do not guess. |
| A4 | Optiboot on the Uno supports a full 32768 B read via `-c arduino` | Pitfall 5 | Medium. Well-established STK500v1 behaviour and `-A` is already default here, but unproven on this bench. This is the cheapest target to prove first. |
| A5 | A cold rebuild is byte-identical on `uno328pb` and `leonardo` too, not just `uno` | Code Example 2 | Low. `uno` was measured identical and no timestamp macro exists on either arm; the other two share the toolchain and the same `[env]` flags. Cheap to verify (~2 s each) — the plan should just measure all three rather than extrapolate. |
| A6 | `random`/`gen_addr_image.py` output is stable across Python patch releases | Standard Stack | Low. `gen_addr_image.py` uses pure arithmetic, no RNG, so it is version-independent — this risk applies only if the planner reverts to `gen_test_image.py` (which uses `random.Random`). One more reason not to. |
| A7 | The two arm venvs will resolve identical dependency versions if created together | Pitfall 8 | Medium. Not guaranteed by anything; `click` shipped a release today. The `pip freeze` diff assertion converts the assumption into a check. |
| A8 | The `controller:` string is best captured by `firestarter -v -p <port> hw` (grep `I: FW: <ver>:<board>`) rather than by `fw` | Pattern 5 | Low–medium. `fw` is the command whose output literally contains the substring `controller:` (`firmware.py:223`) and is what the standing memory names, but it also resolves a release channel over the network and has a history of deadlocks on old firmware. `hw` is local and cheap and carries the same board string via the firmware log line. The planner should verify which one the record gate expects and pin one. |
| A9 | `avrdude -A … flash:r` returns exactly `maximum_size` (32768) and not the part's full addressable space | Pitfall 2 | Low. The man page's `-A` text is unambiguous about disabling truncation, and all three parts are 32 KiB. Verify on the first successful read by asserting the file size. |

---

## Open Questions

1. **Does a full-flash read-back actually work on each of the three chains?**
   - What we know: the write chains are all proven on this bench with recorded avrdude command lines; `-A` is the flag that makes a read fixed-length; `flash:r` has never been run here; no board is attached now.
   - What's unclear: everything about the read direction, per target.
   - Recommendation: a dedicated bring-up plan that proves the chains **cheapest first** (`uno` → `uno328pb` → `leonardo`), each as its own task with its own recorded artifact, and that treats a failure as SC#2's named-alternative branch rather than as a blocker. Do not sequence the cross-flash falsification (D-03) before the read is known to work at all — a MISMATCH is not evidence of a working detector if the reader is broken.

2. **Is the `uno328pb` urboot a vector bootloader?**
   - What we know: urclock patches the reset vector plus one designated vector on vector bootloaders, for both upload and its own verification; `-xshowvector` reports it; 384 B does not align to a boot-section boundary.
   - What's unclear: the actual answer for this board.
   - Recommendation: make `-xshowvector` / `-xshowall` a **recorded bring-up artifact** on this target, and make the judged-span definition for `uno328pb` a function of its output rather than a constant baked into the tool.

3. **Where do the two arm worktrees live?**
   - What we know: `/tmp` does not survive a restart; anything under `/workspaces` shows up in the meta repo's porcelain unless ignored; `firestarter_app/.gitignore` already ignores `.venv/`, so a venv inside each worktree is invisible to the app repo's porcelain (which D-08's empty-porcelain leg needs).
   - Recommendation: `/workspaces/.v1.34-arms/{control,v133}` plus one `.gitignore` line, absolute paths recorded in every command.

4. **Which avrdude binary + conf pair is the rig's?**
   - What we know: three avrdude installs on disk (7.1 system, 8.1 PIO, 6.3 stale); PIO's upload path uses 8.1 with its own conf; the host app resolves 7.1 with no `-C` at all.
   - Recommendation: use **PIO's chain for the write** (it supplies the per-target flags) and pin **one** binary+conf for the read, recorded per cell. If the write and read use different avrdude versions, say so explicitly — it is a real, if small, second variable.

5. **What measure was v1.31's 0.37 s W27C512 figure?**
   - What we know: BOARD-04 requires the v1.34 figures to be stated *next to* it; the app's own success-only `(N.NNs)` line and a wall-clock measurement are different quantities.
   - Recommendation: Phase 160 should settle the definition and put it in PROCEDURE.md (recommendation: wall-clock judged, app-reported recorded alongside), and the plan should include reading the v1.31 record to determine which measure 0.37 s is. If it cannot be determined, that is an honesty-ledger line, not a silent comparison.

6. **Halt policy when a read-back or oracle goes red mid-sweep.**
   - What we know: Phase 145 D-13 halted the phase and handed to `/gsd-debug`; v1.34 has Phase 165 as the designated triage owner, so the policy cannot simply be inherited. CONTEXT explicitly leaves this to planning.
   - Recommendation: distinguish two failures. A **rig** failure (read-back mismatch on a correctly-flashed board, a judge crash, a provenance field missing) halts and is fixed in-phase, because the rig is this phase's deliverable. A **cell** failure (write fails, N=3 disagree, chip reds) is *recorded and carried* to Phase 165 and the sweep continues — that is what makes RCA-01's classification possible at all. Write both branches into PROCEDURE.md so the distinction is not made under pressure.

7. **Does D-12's address attribution need to survive 18 address bits?**
   - What we know: `gen_addr_image.py`'s stamp encodes 16 bits, so on the 256 KiB W29C020 it repeats every 64 KiB and an A16/A17 fault is unattributable (though still detectable via the per-position mask).
   - Recommendation: either widen the stamp to a 4-byte word for the 32-pin part, or record the limitation as a stated non-claim. Decide before generating the 20 images, because regenerating them invalidates every recorded mask.

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO Core | build the six images | ✓ | 6.1.19 | — |
| platform `atmelavr` + both Arduino cores | build all three targets | ✓ | 5.2.0 / 5.3.0 / 3.1.2 | — |
| `avr-gcc` / `avr-objcopy` | build; `.hex`→bin (D-02) | ✓ | 7.3.0 / binutils 2.26 | not on `PATH` — use the full package path |
| `avrdude` (system) | read-back, signature probe | ✓ | 7.1 | PIO's 8.1 |
| `avrdude` (PIO) | `pio run -t upload` | ✓ | 8.1 | system 7.1 (loses `-C` conf pairing) |
| `srec_cat` | alt hex→bin | ✗ | — | `avr-objcopy` (verified exact) |
| Python 3 | all rig tooling | ✓ | 3.12.14 | — |
| `pyserial` (system) | 1200-baud touch helper | ✓ | 3.5 | each arm venv also has it |
| `uv` | create the arm venvs | ✓ | 0.12.6 | stdlib `venv` + `pip` |
| writable uv/pip cache | `uv venv` / `uv pip` | **✗** | `/home/vscode/.cache` is root-owned `drwxr-xr-x` | **export `UV_CACHE_DIR`** to a writable path (verified working) |
| `git worktree` | D-06 | ✓ | — | two full clones (permitted substitution) |
| `gh` CLI | read PR head SHAs | ✓ | authenticated; `pr view` works | `git ls-remote` |
| `sha256sum` | SHA256SUMS.txt | ✓ | coreutils | `python3 -c hashlib` |
| `pytest` | — | ✗ | — | not needed; project convention is plain `python3` gate scripts (see Validation Architecture) |
| **The three Arduino boards** | **everything on-device** | **✗ NOT ATTACHED** | — | **none.** `/dev/ttyACM*`, `/dev/ttyUSB*` and `/dev/serial/by-id/` are all absent right now. |
| The two bench chips | every W→R→V position | ✗ (operator-held) | — | none |
| Operator (physical acts) | mount, seat, silkscreen, pot, DMM, photos | gated | — | none — Phase 145 D-19 |

**Missing with no fallback — blocking for the on-device half:**
- No board is attached, so **not a single one of the three read-back chains could be measured in this session.** Every on-device claim in this document is marked accordingly. The plan must front-load the bring-up proofs and must not schedule a sweep cell behind an unproven read.
- The two bench chips and every physical act require the operator.

**Missing with a fallback:**
- `srec_cat` → `avr-objcopy`, verified exact on all three images.
- Writable uv cache → `UV_CACHE_DIR`, verified working.
- `pytest` → the project's own gate-script convention.

---

## Validation Architecture

`.planning/config.json` does not set `workflow.nyquist_validation`, so it is treated as enabled.

### Test framework

| Property | Value |
|----------|-------|
| Framework | **None.** The meta repo has no `pyproject.toml`, no `pytest.ini`, no `tests/`, and `pytest` is not importable from `python3`. |
| Established convention | Standalone `python3` gate scripts: `def main() -> int` + `raise SystemExit(main())`, asserted by **exit code**. Precedents: `.planning/v1.18/bench/check_{verdict,graduation,signature,pre01,diff07}.py`, `.planning/phases/145-bench-validation/tools/extract_frames.py`, `.planning/phases/145-bench-validation/images/gen_addr_image.py`. |
| Quick run command | `python3 .planning/v1.34/tools/<gate>.py [args] ; echo rc=$?` |
| Full suite command | a small `.planning/v1.34/tools/run_gates.sh` that runs every gate and fails on the first non-zero — no such runner exists yet; Wave 0 should create it |
| Bin-level oracles | `sha256sum` + `cmp` + `stat -c%s`, exactly as the `SHA256SUMS.txt` precedent does |

### Phase requirements → test map

| Req | Behavior | Test type | Automated command | Exists? |
|-----|----------|-----------|-------------------|---------|
| RIG-01 SC#1 | six images build from named SHAs; each has a recorded hash | integration | `cd /workspaces/firestarter && rm -rf .pio/build/$E && pio run -e $E` then `sha256sum -c SHA256SUMS.txt` | ✅ mechanism verified (`uno`, byte-identical) |
| RIG-01 SC#1 | rebuild reproduces the hash, or the divergence is recorded with a measured cause | integration | `python3 tools/check_rebuild.py --images … --expect SHA256SUMS.txt` | ❌ Wave 0 |
| RIG-01 SC#2 | read-back over the hex extent equals the flashed image | integration, on-device | `python3 tools/judge_readback.py --hex … --readback … --objcopy …` | ❌ Wave 0 |
| RIG-01 SC#2 | the check is **proven able to fail** | falsification, on-device | the D-03 cross-flash: same `judge_readback.py`, **observed** non-zero, artifact committed | ❌ Wave 0 — and it must be **observed red**, not authored |
| RIG-03 SC#3 | the two arms' step lists diff empty | unit | `diff <(render_steps.py --arm control) <(render_steps.py --arm v133)` must be empty | ❌ Wave 0 |
| RIG-03 | the two arms' CLI surfaces are identical | unit | AST/`--help` diff across all 25 commands | ✅ **already measured empty** at source level in this research; the `--help` variant is Wave 0 |
| RIG-04 | full-device SHA equality vs the written image, never an exit code | integration, on-device | `python3 tools/judge_wrv.py --written … --reads … --expect-size 65536\|262144` | ❌ Wave 0 |
| RIG-04 | N=3 resolving to one SHA; a disagreement is recorded as a disagreement | integration, on-device | same tool; must count `run_*.bin` (fewer than N on a hw error) and emit `disagreement` rather than retry | ❌ Wave 0 |
| RIG-02/05 | every required provenance field present and non-null | unit | `python3 tools/gate_record.py <cell>/provenance.json` | ❌ Wave 0 |
| RIG-05 | every recorded command line re-parses into the prescribed set | unit | same gate: assert `argv[0]` ∈ {the two absolute arm binaries}; reject bare `firestarter` | ❌ Wave 0 |
| RIG-05 | reconstruction from the record alone matches the prescription | manual, once | fresh context given only the bring-up record + PROCEDURE.md; output diffed against the prescription (D-17) | ❌ Wave 0 — manual by design; cannot be automated without defeating its purpose |
| D-18 | no cell outcome is ever `inconclusive` | unit | `gate_record.py` asserts `outcome ∈ {validated, skipped-with-reason}` | ❌ Wave 0 |
| D-15 | `EVIDENCE.md` is byte-identical to a fresh render of `EVIDENCE.jsonl` | unit | `render_evidence.py --check` (diff render against the committed file) | ❌ Wave 0 — this is what makes "never hand-edited" enforceable rather than aspirational |
| D-07 | the shared config dir is unchanged after each cell | unit | recompute the tree SHA and compare against the recorded value | ❌ Wave 0 |
| Pitfall 8 | the two arm venvs resolve identical dependency versions | unit | `diff` of the two `pip freeze` outputs must be empty | ❌ Wave 0 |

### Sampling rate

- **Per task commit:** the gate(s) touched by that task, exit code asserted.
- **Per wave merge:** `run_gates.sh` — every gate green.
- **Phase gate:** `run_gates.sh` green **and** the two falsification tests **observed** (D-03 mismatch recorded on all three targets; D-17 reconstruction diffed) before `/gsd-verify-work`.

### Wave 0 gaps

- [ ] `.planning/v1.34/tools/run_gates.sh` — the "full suite" runner; does not exist
- [ ] `tools/judge_readback.py` — RIG-01 SC#2 (`-A` read, objcopy normalize, span compare, whole-flash datum)
- [ ] `tools/judge_wrv.py` — RIG-04 (full-device SHA, file-count guard, app-verdict disagreement flag)
- [ ] `tools/capture_provenance.py` — RIG-02/05 (`--shield-rev` required; `-P` on the `__file__` probe)
- [ ] `tools/gate_record.py` — D-17 script gate (field presence + command re-parse + `outcome` domain)
- [ ] `tools/render_evidence.py` — D-15, with a `--check` mode so "never hand-edited" is enforced
- [ ] `tools/probe_board.py` — D-14 signature probe, both parse routes, plus `-xshowvector` on `uno328pb`
- [ ] `tools/touch_1200.py` — Leonardo bootloader entry (pyserial)
- [ ] `tools/gen_addr_image.py` — copied from Phase 145, D-16 boundary comment intact, stamp-width decision made
- [ ] `tools/check_rebuild.py` — SC#1's reproduce-or-record-the-cause clause

**A note on how these gates should be born.** Standing memory `reference_gate_authored_before_content_can_be_unreachable` and `reference_planted_arm_break_must_avoid_manifest_gate` both record the same lesson: in this project a gate that has been written but never observed to fail proves nothing. Every gate above should be observed **red** against a deliberately broken input (a truncated read-back, a null provenance field, a hand-edited `EVIDENCE.md`, an `outcome: inconclusive`) before it is trusted green — which is the same discipline D-03 and D-17 apply at the phase level, applied one level down.

---

## Security Domain

`security_enforcement` is not set in `.planning/config.json`, so it is treated as enabled. This is a local bench-tooling phase with no network service, no authentication surface and no user-facing input, so most ASVS categories genuinely do not apply — recorded honestly rather than padded.

### Applicable ASVS categories

| ASVS category | Applies | Standard control |
|---------------|---------|------------------|
| V2 Authentication | no | No auth surface. `gh` uses the operator's existing credential; this phase creates no PR, no push, no tag (CLOSE-04 forbids all of it). |
| V3 Session management | no | No sessions. |
| V4 Access control | **partially** | Filesystem only: rig tooling writes under `.planning/v1.34/` and must not write into either sub-repo. Enforced by review + the D-16 boundary comment carried in each copied tool. |
| V5 Input validation | **yes** | Every rig tool takes operator-supplied strings (`--shield-rev`, `--cell-id`, `--port`, `--chip`, mask) that flow into filesystem paths and `subprocess` argv. Use `argparse` `choices=` where the domain is closed, validate `--cell-id` against `^[A-Za-z0-9/_-]+$`, and never build a shell string — always `subprocess.run([...])` with a list. `name_firmware.py:60` is the in-repo precedent: it validates `RURP_BOARD_NAME` against `^[a-zA-Z0-9_-]+$` precisely because the value becomes a filename. |
| V6 Cryptography | **yes, but trivially** | SHA-256 via `hashlib` for integrity only, never for authentication. Do not hand-roll; do not substitute a shorter digest. |
| V7 Error handling & logging | **yes** | A gate that fails must fail **closed** and non-zero. Standing memory `reference_check_permitted_claims_here_resolves_wrong_phase_dir` records a gate in this very repo that scanned nothing and exited 0 — a rig gate that cannot find its input must exit non-zero, never 0. |
| V12 File handling | **yes** | Read-back and image paths are constructed from arguments. Resolve to absolute paths, assert the resolved parent is inside `.planning/v1.34/`, and reject `..` traversal. |
| V14 Configuration | **yes** | `FIRESTARTER_CONFIG_DIR` is a deliberate isolation seam and must be set at process launch (`config.py` computes `HOME_PATH`/`DATABASE_FILE`/`PIN_MAP_FILE` at **import** time from `get_config_dir()`, so setting the variable after import is too late). `UV_CACHE_DIR` likewise. |

### Known threat patterns for this stack

| Pattern | STRIDE | Standard mitigation |
|---------|--------|---------------------|
| Command injection via an operator-supplied cell id / port / mask reaching `subprocess` | Tampering / Elevation | `subprocess.run([...])` list form only; `shell=False`; `argparse choices=` on closed domains; regex-validate the open ones |
| Path traversal via `--output-dir` / `--cell-id` writing outside `.planning/v1.34/` | Tampering | `Path(...).resolve()` then assert `is_relative_to(V134)` |
| A gate that silently no-ops and exits 0 (fail-open) | Repudiation | Assert the input exists and is non-empty **before** judging; exit non-zero on a missing input; observe every gate red once |
| A wrong-arm flash going unrecorded | Repudiation / Spoofing | The entire phase. D-01's independent read-back plus D-03's observed-red cross-flash. |
| Silent overwrite of one arm's image by the other's identically-named build | Tampering | Pattern 1 — arm-tagged filenames at copy time; `rm -rf .pio/build/<env>` between arms; `SHA256SUMS.txt` as the after-the-fact check |
| Accidental product-code mutation while a worktree is checked out | Tampering | D-08's empty-`porcelain` leg on every cell; worktrees created `--detach` so no branch can be advanced by accident |
| Committing a secret into an evidence artifact | Information disclosure | Read-backs are firmware/chip bytes; the config dir is seeded by this phase. Nothing carries a credential. Recorded as a checked non-risk, not assumed. |
| Registry-substitution (slopsquat) on a new dependency | Tampering | Not applicable — this phase adds **no** new package; see Package Legitimacy Audit |

---

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md` (meta repo, binding):

- **This repo tracks only `.planning/` and `.claude/`.** Neither sub-repo is committed here. → Every artifact this phase produces belongs under `.planning/v1.34/`; the two sub-repos are read-only inputs at fixed SHAs. This phase creates **no** sub-repo commit (CONTEXT §Integration Points).
- **Firmware commands run from `firestarter/`; Python-app commands from `firestarter_app/`.** → Reinforces Pitfall 4: `pio` must never run from `/workspaces`.
- **Serial-protocol changes must be kept in sync** between `serial_comm.py` and `firestarter.cpp`; **constants/flag bits are duplicated** between `constants.py` and `firestarter.h` and must change together. → Both are moot here by construction: this phase changes neither file. Worth naming because a plan that found itself editing either would be out of scope by two separate rules.
- **Board differences:** Uno 512-byte data buffer, Leonardo 1024. → Confirmed in `platformio.ini` (`-D DATA_BUFFER_SIZE=1024` on leonardo only). Affects chunked transfer in `eprom_operations.py`, i.e. read/write *timing* differs by board — relevant to BOARD-04's duration figures being compared within a board rather than across boards.
- **Hardware calibration (R1/R2, board revision) is persisted in Arduino EEPROM** via `rurp_configuration_t`. → Runtime state this phase inherits and must record (Runtime State Inventory row 1); a flash-only `-D -U flash:w:` does not disturb it.

From `firestarter/CLAUDE.md`:
- Algorithm `0x07` (W27C512) uses a per-byte pulse-to-verify loop with `max_pulses` 25 and `verify_mode == VERIFY_PER_PULSE_PLUS_FINAL`; `0x0B`'s energy cap is the only reachable `MSG_ERR_ENERGY_CAP` row. Informational — the plan must not "improve" any of it.
- **Intra-block progress emission (`MSG_DATA_PROGRESS`) is compiled out on `SERIAL_ON_IO` targets** (`uno`, `uno328pb`) and exists only on `leonardo`/native. → Directly kills frame-scraping as a portable write-duration source (Pitfall 7).
- `messages.h` is codegen-generated and ID-only — never hand-edited. Moot here; named for completeness.

From `firestarter_app/CLAUDE.md`:
- Tooling gate is `ruff check` + `ruff format --check` + `mypy` (strict on 8 modules) + `pytest --cov-fail-under=70`, enforced in the app repo's CI. → Applies to the **app repo**, which this phase does not modify. It does *not* apply to `.planning/v1.34/tools/`; imposing it there would be scope invented rather than required.

### Project skills

`/workspaces/.claude/skills/` holds `devtest-triage`, `devtest-rootcause`, `find-skills`, `skill-creator`. The two project skills both govern **`dev test` chip-validation triage and the generated `chip_database.json`** — Phase 162's territory, not Phase 160's. Their one binding rule that reaches this phase is a negative: `chip_database.json` is **generated** and must never be hand-edited. This phase only *reads* it (for the two chips' sizes, packages and `vpp_mv`), which is compliant.

---

## Sources

### Primary (HIGH confidence — measured or read in this session)

- `avrdude(1)` man page for the exact installed avrdude 7.1 — `/usr/share/man/man1/avrdude.1.gz`: the `-U` format table, the trailing-`0xFF` truncation paragraph, the `-A` flag and its `-c arduino` default, the `-D` semantics, the urclock overview and the full `-x` extended-parameter text.
- `avrdude -c urclock -p m328pb -x?` (live) — the complete urclock extended-option list including `-xshowvector`, `-xshowall`, `-xshowversion`, `-xnometadata`, `-xrestore`, `-xbootsize`.
- `~/.platformio/platforms/atmelavr/builder/main.py:30-100, 180-230` — the exact upload command construction, `-xnometadata` for urclock at :219-220, the 1200-baud touch and port-wait at :84-88.
- `~/.platformio/platforms/atmelavr/boards/{uno,ATmega328PB,leonardo}.json` — mcu, protocol, speed, bootloader, `maximum_size` per target.
- `~/.platformio/platforms/atmelavr/.piopm` and `~/.platformio/packages/*/package.json` — installed platform and package versions.
- `firestarter/platformio.ini`, `name_firmware.py`, `zero_bootloader_reserve.py`, `scripts/baseline/size_baseline.json`, `include/version.h` (both arms).
- `firestarter_app/firestarter/{cli_handlers.py,eprom_operations.py,config.py,channel.py,avr_tool.py,firmware.py}` and `pyproject.toml` — both arms where relevant.
- `firestarter_app/firestarter/data/chip_database.json` — the two chip rows.
- `.planning/{REQUIREMENTS.md,ROADMAP.md §160-163,PROJECT.md §v1.34,config.json}`; `.planning/phases/160-…/{160-CONTEXT.md,160-DISCUSSION-LOG.md}`.
- `.planning/phases/145-bench-validation/{145-CONTEXT.md,SHA256SUMS.txt,images/gen_addr_image.py}` and its `images/ readbacks/ runs/ logs/ tools/` layout.
- `.planning/v1.15/bench/EVIDENCE.json`, `.planning/v1.18/bench/EVIDENCE.json` + `check_*.py`.
- `.planning/todos/pending/avrdude-mcu-detection-fallback.md`; `.planning/v1.7/bench-evidence-35.md`; `.planning/v1.5-BENCH-RESULTS.md`; `.planning/debug/resolved/fw-update-blocked-release-fw.md:280-320`.
- `/workspaces/CLAUDE.md`, `firestarter/CLAUDE.md`, `firestarter_app/CLAUDE.md`, `/workspaces/.gitignore`.
- Live commands executed: the cold `uno` rebuild + hash comparison; `avr-objcopy` on all three hexes + a hex-record extent/gap analysis; the AST diff of both arms' Click surfaces; the full worktree + `uv venv` + editable-install + `__file__` + `--help` sequence and its teardown; the namespace-shadow reproduction with and without `-P`; `gh pr view 56/54`; `git merge-base` / `rev-list --count` on both repos; the device-node scan.
- Standing memories: `feedback_chip_out_before_sideload`, `feedback_verify_port_identity_each_task`, `feedback_operator_adjusts_pot_solo`, `user_shield_revisions`, `feedback_bench_boards_are_fw_flash_testbed`, `project_uno328pb_correction`.

### Secondary (MEDIUM confidence)

- `github.com/stefanrueger/urboot` docs (vector-bootloader patching) — corroborated by the local man page's `-xrestore` text, which describes patching as the thing `-xrestore` suppresses. Two independent sources agreeing → MEDIUM.

### Tertiary (LOW confidence — websearch only, flagged for bench validation)

- Caterina / AVR109 flash read-back capability and window constraints on the ATmega32U4 (A1). avrdude's own device table implies read support; no authoritative statement found.
- Optiboot full-flash read via `-c arduino` (A4). Well-established in the wider ecosystem, unproven here.

### Sources consulted and reported as empty

- Knowledge graph `.planning/graphs/graph.json`: **STALE** — last built 2026-07-01, 1348 h old, 1873 commits behind (`built_at_commit f4150b8` vs `current dcd9101`). A query for "firmware flash provenance read-back" returned **0 nodes / 0 edges**. It contributed nothing and any semantic relationship from it would be approximate; direct file investigation replaced it.
- Context7: not available in this session (no `mcp__context7__*` tools; `ctx7` CLI absent). The `research-plan` seam routed two questions there; both were answered instead from the locally-installed authoritative man page, which is a *stronger* source for the exact binary in use than any hosted doc snapshot.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|------|-------|--------|
| Exact SHAs (all four) | **HIGH** | Read off branches and cross-checked against `gh pr view` head OIDs; merge-bases verified |
| Build chain + reproducibility | **HIGH** | Cold rebuild measured byte-identical on `uno`; all five toolchain versions read from manifests and matching the recorded pins; no timestamp macro on either arm |
| `.hex` → bin normalization (D-02) | **HIGH** | objcopy output size == hex record span == recorded `flash_used` on all three targets; zero gaps confirmed |
| Host-arm mechanism (D-06/D-08) | **HIGH** | Built and torn down end to end; all three D-08 legs verified working; the `-P` trap reproduced and fixed |
| Arm-agnosticism of the CLI (SC#3) | **HIGH** | AST diff of 25 commands + full option/argument sets is empty in both directions |
| `dev consistency-check` contract | **HIGH** | Read from source on both arms; artifact naming and verdict strings identical |
| Chip facts (sizes, packages, vpp) | **HIGH** | Parsed from the shipped database |
| Record substrate + gate convention | **HIGH** | `locked_columns` byte-identical across two prior milestones; gate-script shape read from four precedents |
| avrdude read semantics (`-A`, truncation, urclock metadata) | **HIGH** | Authoritative man page for the exact installed binary; `-A` acceptance verified live |
| urclock vector-patch hazard | **MEDIUM** | Two independent sources agree the patching happens; whether *this* bootloader is a vector one is unmeasured |
| The three read-back chains actually working on-device | **LOW** | No board attached; `flash:r` never invoked in this project's history; ecosystem evidence only |
| Leonardo bootloader-window fit for a 32 KiB read | **LOW** | Inferred from a 5.51 s write on the same chain; not measured for a read |

**Not measured, with the blocker named on the line:**
- Every on-device behaviour — `not measured` — no board attached (`/dev/ttyACM*`, `/dev/ttyUSB*`, `/dev/serial/by-id/` all absent 2026-08-26).
- Cold-rebuild determinism on `uno328pb` and `leonardo` — `not measured` — only `uno` was rebuilt this session to bound the cost; ~2 s each, so the plan should just measure all three.
- Whether the `uno328pb` urboot is a vector bootloader — `not measured` — requires `-xshowvector` against an attached board.

**Research date:** 2026-08-26
**Valid until:** the host-side findings are stable for ~30 days (no fast-moving dependency). The three LOW-confidence on-device items expire the moment a board is attached and probed — **they should be replaced by measurements in the phase's first plan, not carried forward as research.**
