# BRINGUP-wrv — D-17 Reconstruction Diff (Plan 13, Task 1)

This diffs `RECONSTRUCTION.md`'s three rounds against the prescription: the command set and
physical setup `PROCEDURE.md` actually prescribes for position `BRINGUP-wrv__v133__w27c512`,
with every argument filled from the artifacts that recorded what really ran — `WRITE.md`,
`POT.md`, `READBACK-VERDICT.json`, `WRV-VERDICT.json`, `check_arms_teardown.json` and
`bench/IMAGE-PLAN.json` — none of which were ever given to the reconstructing context.

## The prescription side (built from the artifacts, never from the reconstruction)

| Step | Prescribed command / action (literal, arguments filled) |
|---|---|
| P-01 | Operator mounts Rev 2.0 shield on the Uno, declares it (`POT.md`, `WRITE.md`) |
| P-02 | `python3 .../probe_board.py --target uno --port /dev/ttyACM0 --pins .../rig-pins.json --out .../BRINGUP-wrv/probe.json` ; `FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -v -p /dev/ttyACM0 hw` (`provenance.json.commands[0..1]`) |
| P-03 | Operator removes ATmega328P before flash + read-back window |
| P-04 | `git -C /workspaces/firestarter checkout 5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463` ; `git -C /workspaces/firestarter status --porcelain` ; `cd /workspaces/firestarter && pio run -t upload -e uno` ; `python3 .../judge_readback.py --target uno --port /dev/ttyACM0 --flashed-arm v133 --expect-arm v133 --out-dir .../BRINGUP-wrv --pins .../rig-pins.json` (`READBACK-VERDICT.json`: `judged_match=true`, `judged_span_bytes=22952`) |
| P-05 | Operator seats W27C512 (DIP28) |
| P-06 | `FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 vpp` — one confirming read, 12.0V (`POT.md`; carried forward for this cell per `WRITE.md`, no new reading taken at this task) |
| P-07 | `python3 .../gen_addr_image.py --stamp-width 16 65536 36 .../written.bin` ; `firestarter -p /dev/ttyACM0 write w27c512 .../written.bin` (41.010s wall-clock) ; `firestarter -p /dev/ttyACM0 dev consistency-check w27c512 --runs 3 --output-dir .../reads --keep-files` ; `judge_wrv.py --written ... --reads ... --expect-size 65536 --app-verdict 0 --position-id BRINGUP-wrv__v133__w27c512 --pins .../rig-pins.json --out .../wrv_verdict.json` (`WRV-VERDICT.json`: `app_verdict_unjudged=0`, `sha_verdict_judged=match`) ; `capture_provenance.py --cell-id BRINGUP-wrv --position-id BRINGUP-wrv__v133__w27c512 --arm v133 --target uno --port /dev/ttyACM0 --chip w27c512 --shield-rev "Rev 2.0" ...` |
| P-08/P-09/P-10 | Not applicable — this position is `w27c512` only; the cell's `w29c020` position and the arm switch belong to other, not-yet-run positions in the same cell |
| P-11 | (Amendment 2, post-fix) `probe_board.py --target uno --port /dev/ttyACM0 --pins .../rig-pins.json --out .../board_probe_teardown.json` ; then `check_arms.py --pins .../rig-pins.json --expect-config-sha 77adfdd2... --out .../check_arms_teardown.json` (`check_arms_teardown.json`; `provenance.json`'s final `commands[]` entry) |

Physical setup prescribed: Uno + Rev 2.0 shield, port `/dev/ttyACM0`, ATmega328P chip-out
before P-04, W27C512 (DIP28) seated at P-05, pot at 12.0V confirmed once for the cell.

---

## Divergence classification

### Record insufficiency — 1 found, 1 fixed

**RI-1: `$MASK` (and `stamp_width`, image `sha256`) were absent from `provenance.json`,
though the run genuinely needed them.**

- **Round found in:** Round 1.
- **Symptom:** Round 1's P-07 command emitted `GUESS/PLACEHOLDER:<mask_value>` in place of
  the mask argument to `gen_addr_image.py`, and explicitly stated it could not proceed with
  the write/read/judge cycle without it.
- **Why this is a record insufficiency, not a prescription ambiguity:** the value is not
  ambiguous in the procedure (`PROCEDURE.md`'s own token table names its source:
  `bench/IMAGE-PLAN.json`, keyed by `$POSITION_ID`) — it is simply **absent from the one
  document the reconstruction was allowed to read**. `provenance.json`'s own `_schema` never
  listed `image_mask` / `image_stamp_width` / `image_sha` as gathered fields, even though a
  **separate, later-stage record** (`bench/EVIDENCE.jsonl`'s `image_mask` /
  `image_stamp_width` / `image_sha` columns, assembled by each plan's own inline evidence-
  append script) already carried the identical values (`36`, `16`,
  `fff15da9f46d04b366b4b8bf42a91cd2f67a8f57a1cfccac26351c5325b35726`) under the same field
  names. The per-cell provenance record — the file this RIG-05 property is actually testing
  — was the one place these values were missing.
- **Fix, at the source, per this task's own instruction ("a divergence feeds back into the
  tool rather than into prose"):**
  1. `.planning/milestones/v1.34-artifacts/tools/capture_provenance.py`: added `image_mask`, `image_stamp_width`,
     `image_sha` to `RECORD_KEYS`; added `resolve_image_plan_fields()` (reads
     `bench/IMAGE-PLAN.json` by `position_id`, zero device I/O — the manifest is a
     pre-computed, milestone-level document, not something requiring a live probe); wired it
     into the normal capture flow; added a new `--patch-image-plan` mode (mirroring the
     existing `--patch-readback` pattern) to retrofit an **already-captured** record without
     re-running any device, git, or serial probe.
  2. Extended `_run_selftest()` with 5 new legs covering the new resolver and patch mode
     (2 positive, 2 negative on `resolve_image_plan_fields`, 1 round-trip + 1 negative on
     `--patch-image-plan`); `python3 .../capture_provenance.py --selftest` exits 0
     (all legs, old and new, PASS).
  3. Re-captured `bench/cells/BRINGUP-wrv/provenance.json` via:
     `python3 .../capture_provenance.py --cell-id BRINGUP-wrv --position-id
     BRINGUP-wrv__v133__w27c512 --arm v133 --target uno --port /dev/ttyACM0 --chip w27c512
     --shield-rev "Rev 2.0" --pins .../rig-pins.json --out .../provenance.json
     --patch-image-plan` — **zero device I/O**: the patch mode reads the existing on-disk
     record and `IMAGE-PLAN.json` only, touches no serial port, and issues no avrdude
     invocation. A `diff` of the before/after record shows **only three lines added**
     (`image_mask: 36`, `image_stamp_width: 16`, `image_sha: fff15da9...`) plus the matching
     `_schema.record_keys` additions — every prior field, every `commands[]` entry, and every
     original timestamp is byte-for-byte unchanged.
  4. Verified the whole record and full gate suite stayed green after the fix:
     `gate_record.py --cell provenance.json` exit 0; `gate_record.py --jsonl EVIDENCE.jsonl`
     exit 0; `render_evidence.py --check` exit 0; `bash run_gates.sh` exit 0 (11/11 tool
     self-tests + 5/5 live gates).
  5. **Re-ran the reconstruction with a fresh context (Round 2)** against the corrected
     record: the `gen_addr_image.py` line now reads `--stamp-width 16 65536 36 ...` with
     **no guess marker** — the fix closed the gap.

### Prescription ambiguity — 1 found, 1 fixed

**PA-1: `P-11`'s teardown re-probe had no literal command block, unlike every other step.**

- **Round found in:** Round 2 (the `provenance.json` fix from RI-1 was already applied; this
  divergence was independent of it).
- **Symptom:** Round 2's P-11 output guessed an `--out` path
  (`board_probe_teardown.json`) for the re-run of `probe_board.py`, self-flagged as a guess
  "inferred from procedure text but not confirmed."
- **Why this is a prescription ambiguity, not a record insufficiency:** `PROCEDURE.md`'s
  `P-11` prose said *what* to do ("re-run `probe_board.py` to confirm the board identity has
  not changed since `P-02`") but, unlike `P-02`/`P-04`/`P-06`/`P-07`/`P-09`, gave **no literal
  command block** — the reconstructing context had to construct one by analogy to `P-02`'s
  shape, inventing an output filename in the process. The procedure was readable only one
  sensible way in substance, but literally silent on the one token (`--out`) that
  distinguishes a genuine re-probe from a silent overwrite of `P-02`'s own artifact.
- **Fix:** amended `PROCEDURE.md`'s `P-11` with a literal command block (mirroring `P-02`'s
  shape) naming an explicit, distinct output path,
  `$CELL_DIR/board_probe_teardown.json`, and recorded the change as **Amendment 2** at the
  bottom of `PROCEDURE.md` (dated, naming what changed, why, and which cells ran under which
  text — per the procedure's own amendment-discipline rule). Re-rendered the step lists and
  reconfirmed the arm-agnostic diff is still empty:
  `diff <(render_steps.py --arm control) <(render_steps.py --arm v133)` — empty, both
  arms render 11 lines, unchanged from before the edit (`probe_board.py` carries no
  `$ARM_BIN` token, so the new text is identical for both arms by construction). Full gate
  suite re-run green after the edit (11/11 + 5/5, exit 0).
- **Confirmed closed in Round 3:** the P-11 output now reads
  `--out .../BRINGUP-wrv/board_probe_teardown.json` with **no guess marker** — the
  reconstructing context read the literal path straight out of the now-unambiguous
  procedure text.
- **A second, distinct fact this same investigation surfaced (disclosed, not backfilled):**
  `BRINGUP-wrv`'s own actual teardown (Phase 160 Plan 12, Task 3) **never executed a
  `probe_board.py` re-run at all** — its task text and its `provenance.json` `commands[]`
  log show only the config-dir check (`check_arms.py`). This is a genuine compliance gap
  between the OLD prose-only `P-11` prescription and what actually ran, not merely an
  ambiguity in how the prose reads. It is **not corrected retroactively here**: doing so
  would require an avrdude signature probe against a board this plan's own constraints
  forbid touching while a chip is seated (`probe_board.py` issues a deliberately-wrong-`-p`
  avrdude invocation to elicit the real signature — device I/O, out of scope for this
  plan). The gap is recorded as an open item, per this project's record-honesty standard
  ("never edit a divergence to agree"), and carried forward to `PHASE-160-GATE.md`'s
  non-claims and to Phase 161 (whose own first cell's `P-11` will run under the amended,
  now-literal text and should not repeat the omission).

### Cosmetic — 6 found across the three rounds, no fix required

1. **Round 2/3: firmware-repo path (`/workspaces/firestarter`) self-flagged as a guess.**
   The value is not actually a gap — `PROCEDURE.md`'s own `P-04` step text states the literal
   path directly (`git -C /workspaces/firestarter checkout ...`). The reconstructing context
   hedged on a value that Input 2 already gave it verbatim. Every round's emitted command
   used the correct path regardless of the hedge.
2. **Round 3: `FIRESTARTER_CONFIG_DIR` path self-flagged as a guess.** Same shape as (1) —
   `PROCEDURE.md`'s own substitution-token table states the literal value directly
   (`$FIRESTARTER_CONFIG_DIR | ... /workspaces/.planning/milestones/v1.34-artifacts/config`). Rounds 1 and 2 used
   this value with no hedge at all; round 3 hedged on the identical, correctly-used value.
   This is intra-run non-determinism in what the reconstructing context chooses to flag as
   uncertain, not a fact about the record's sufficiency — the emitted value was identical
   and correct in all three rounds.
3. **All rounds: `--pins` argument's absolute-vs-relative path spelling.** `provenance.json`'s
   own `commands[]` entries show both forms in different invocations (cwd is always
   `/workspaces` in every recorded command); both spellings resolve identically from that
   cwd. A different but equivalent spelling of the same argument.
4. **Round 1 only: cell-directory pre-existence assumption.** Correctly inferred and
   unremarkable — every tool's `--out` argument is inside an existing, named cell directory
   in every recorded command; no divergence in substance.
5. **Round 2 only: P-06 pot-setting necessity, conditioned on whether the control arm already
   ran this cell.** A genuinely careful, correct branch: the reconstructing context could not
   see cross-position cell history from a single position's provenance file (which is, by
   design, one position's identity capture, not the whole cell's run log), so it named the
   condition explicitly and supplied the correct command for the "not yet set" branch. The
   emitted command is right either way; this is a valid, disclosed reading of an inherently
   under-specified single-position view of a multi-position cell, not a defect to fix.
6. **All rounds: `--app-verdict <exit code>` placeholder.** `PROCEDURE.md`'s own `P-07`/`P-09`
   step text carries this exact same shape as a **literal bracketed runtime placeholder**
   (`--app-verdict <dev consistency-check's own 0/1/2, when it ran>`) — the app-verdict is
   inherently the *output* of a step that has not yet run at the point this argument is
   written, for the original run or for any future re-run alike. No record could pre-supply
   it; the reconstructing context's placeholder is a different but equivalent spelling of the
   procedure's own acknowledged runtime slot, not a gap in the record.

### Not a divergence (informational, no classification needed)

Round 2 asked whether "re-run this exact cell position" should continue through `P-08`–`P-10`
(the second chip, W29C020, and the arm switch). `position_id` in `provenance.json`
(`BRINGUP-wrv__v133__w27c512`) unambiguously names only the `w27c512` position; round 3
correctly stated "not applicable" without treating it as an open question. Not a divergence —
the reconstructing context's own scoping in round 2 was a hedge, not an error, and round 3
resolved it cleanly on the identical inputs.

---

## Bare-application-name and shield-revision checks (named explicitly, per this task's action)

- **Bare application name:** in **no round** did the reconstruction's command set emit a bare
  `firestarter` as a first token. Every invocation of the app used the full absolute venv
  path recorded in `provenance.json`'s own commands
  (`/workspaces/.v1.34-arms/v133/.venv/bin/firestarter`). The record made the arm unambiguous
  in every round; this consequential failure mode never occurred.
- **Shield revision:** in **every round**, the reconstructing context correctly named
  "Rev 2.0" as the shield to mount, sourced from `provenance.json`'s own
  `shield_rev_declared` field. The record placed this field where the reconstruction could
  find it; this did not need a fix.

---

## Conclusion

**Three rounds.** Round 1 (original record, pre-amendment procedure) found 1 record
insufficiency (mask/stamp_width/image-sha absent from `provenance.json`) and 1 cosmetic
non-divergence. Round 2 (record insufficiency fixed) confirmed the fix and surfaced 1
prescription ambiguity (`P-11`'s teardown re-probe had no literal command) plus 5 cosmetic
items. Round 3 (both fixes applied) confirmed both closures and reproduced only cosmetic
self-hedges — items whose actual emitted values were, in every case, already directly
recoverable from the two given inputs, or are runtime-only quantities that `PROCEDURE.md`
itself represents as an explicit placeholder.

**Divergence counts: record insufficiency = 1 (fixed, 1 round of re-verification); prescription
ambiguity = 1 (fixed, confirmed in round 3 without requiring a further round, per this task's
own acceptance criteria); cosmetic = 6; not-a-divergence = 1.**

Round 3's command set and physical setup are equivalent to the prescription with **zero**
values sourced from anywhere but the two inputs (`provenance.json` and `PROCEDURE.md`): every
value round 3 flagged as a guess is, on inspection, either (a) a value stated directly and
literally in `PROCEDURE.md`'s own text (the `FIRESTARTER_CONFIG_DIR` path, the `rig-pins.json`
path form), self-flagged inconsistently across rounds but never actually sourced from outside
the two documents, or (b) the single genuinely runtime-only quantity (`--app-verdict`), which
`PROCEDURE.md` itself represents as an explicit bracketed placeholder rather than a concrete
value — meaning the reconstruction's rendering of it is not a gap but a correct mirror of the
procedure's own acknowledged shape. No command in the final (round 3) reconstruction has a
bare application name as its first token, and the shield revision was correctly resolved from
the record in every round.

One further, distinct finding stands disclosed rather than closed: `BRINGUP-wrv`'s own actual
`P-11` teardown never executed the `probe_board.py` re-run the (old, prose-only) prescription
called for — a genuine compliance gap in what Plan 12 ran, discovered by this exercise,
carried forward rather than backfilled, and named again in `PHASE-160-GATE.md`.
