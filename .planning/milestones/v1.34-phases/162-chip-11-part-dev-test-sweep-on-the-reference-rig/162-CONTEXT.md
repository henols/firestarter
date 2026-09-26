# Phase 162: CHIP — 11-Part `dev test` Sweep on the Reference Rig - Context

**Gathered:** 2026-08-27
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase produces **results and one new record shape**, not product behaviour. Phase 160 built
the rig; Phase 161 ran the WRV sweep and left the rig standing; Phase 162 runs a *different
command* on that same standing rig.

It delivers **ten `firestarter dev test` reports** — W27C512, W27E512, SST27SF512, W27E040,
ST M27C512, SST39SF040, W29C040, W29C020, FM1608, AM27C020 — produced on the **v1.33 arm /
Leonardo / Rev 2.0**, plus **one named absence** (2516). Each part's result is placed next to its
most recent recorded disposition in one divergence table, and **every diverging part — and no
other — gets a control-arm re-run**.

**The rig is inherited standing and needs no reconfiguration.** Phase 161's cell A3/B2 teardown
left exactly CHIP-01's required configuration: Leonardo at `/dev/ttyACM0` (`2341:8036`), Rev 2.0
shield, **v1.33 arm already flashed** (fw `5759dc8d`), W27C512 seated, pot in band. The first part
of this sweep therefore costs **zero chip handlings and zero flashes**.

**This phase changes no product code.** Not firmware, not the host app — both submodules stay
byte-unchanged. Everything it builds lives in `.planning/v1.34/`. The milestone lists "any
product-code change not traced to a v1.33-caused regression" as Out of Scope; Phase 162 discovers,
it does not repair. RCA and fixes are Phase 165's and land on the v1.33 PR branch. A plan that
finds itself needing a source edit in either sub-repo must stop and report.

**Everything Phases 160 and 161 locked stays locked.** The planner does not re-open: the standing
bench rules; the halt policy `P-H1`/`P-H2`; the forbidden-invocation table (`--force`/`-f`/`-b`/
`--no-blank-check`/`--skip-erase`, and the bare `firestarter` on PATH as a third un-named arm);
`FIRESTARTER_CONFIG_DIR` inline on every arm-invoking command, never exported; no `--auto`/
`--chain`; a single clean re-seat per position with **both** attempts recorded; "not measured —
`<reason>`" instead of a blank; no hand-transcribed machine fields; a wrong record marked
SUPERSEDED and kept visible.

### The measured facts that shape this phase

Four facts were established during this discussion and were **not** knowable when the roadmap was
written. Each one changes what the planner must do.

1. **`PROCEDURE.md` does not describe this phase.** Its §Scope defines a cell as "both arms
   (`control` then `v133`) and both bench chips (W27C512 DIP28, then W29C020 DIP32) … four
   positions", while simultaneously claiming to be "executed **unchanged** by Phases 161, **162**
   and 163". `P-07`/`P-09` write a pre-computed image from `IMAGE-PLAN.json` and judge a full-device
   SHA — `dev test` does none of that. Roughly half the step list applies verbatim; the other half
   does not apply at all.

2. **`EVIDENCE.jsonl`'s schema is hostile to a `dev test` row**, in three specific ways:
   `position_count_expected: 20`; a `close01_counting_rule` computed over *every* non-`BRINGUP-`
   row; and `gate_record.py` rejecting "a key outside either list", where all 31
   `evid_extension_columns` are WRV artifacts (`image_mask`, `read_shas`, `sha_verdict_judged`,
   `write_duration_*`). The **9 `locked_columns` do map cleanly**, which is what makes a sibling
   file viable.

3. **The VPP guard is asymmetric, and that decides the pot policy.**
   `src/proms/eprom.cpp:530-537`: `vpp_mv > handle->vpp_mv + 500` raises `MSG_ERR_VPP_HIGH` with
   `RESPONSE_CODE_ERROR` (**blocks**, downgraded only by `FLAG_FORCE`, which is forbidden here);
   `vpp_mv < handle->vpp_mv * 95 / 100` raises `MSG_WARN_VPP_LOW` with `RESPONSE_CODE_WARNING`
   (**does not block**). Combined with Phase 161's ratiometric ADC finding (~×1.075 firmware over
   meter), a real 13.0 V rail reads ~13.98 V and **hard-ERRORs**. Chasing spec voltage upward is
   the one thing on this rig that can block a run; running under-voltage cannot.

4. **The sweep is 10 parts, not 11.** The 2516 is unsupported on Rev 2.0 — operator-declared
   2026-08-27: *"only 2.2 and above is supporting and there must be more work done before we can
   test it."* SC#4's arithmetic is therefore **`10 + N`**, stated as such, not the roadmap's
   `11 + N`.

### Command-level facts, verified live this session

- `dev test` takes **one argument and one flag**: `CHIP` and `--fast`. Every v1.21-era flag
  (`--destructive`, `--output-dir`, `-y`, `--submit`) errors as unknown. `--help` is **byte-identical
  on both arms**.
- All ten tokens **resolve in the database**. Two pairs share one DB row: `W27C512`/`W27E512`
  (Winbond `W27C512,W27E512`, chip-id `0xDA08`) and `W27E040` (row `W27C04,W27C040,W27E040`).
  `M27C512` resolves to **SGS-THOMSON**, chip-id `0x203D` — matching v1.15's recorded id.
- `derive_plan` yields the same 12-step shape for every part: `id`, `read`, `write`|`write-partial`,
  `verify`, `erase`, `blank-check`, then **six SDP legs that are NA for all ten** (none is protocol
  0x0D), so the SDP exit floor can never fire in this phase.
- `_resolve_write_scope` is **unconditional and prompt-free**: UV → one bit-masked 256-byte slot
  (`_UV_WRITE_REGION_LENGTH = 256`, guarded by `_UV_MIN_CLEARED_BITS`/`_UV_MIN_RETAINED_BITS` = 64
  each); everything else → full device, with flash4 (0x05) carving out the first and last 16 KiB
  (`_BOOT_BLOCK_SIZE = 0x4000`).
- The report is persisted **unconditionally** to `<config dir>/reports/dev-test-<chip>.{json,md}` —
  a **fixed path per chip**, so a control-arm re-run overwrites the v1.33 report unless it is copied
  out first.
- `submit_report` is called on **every** run. `sys.stdin.isatty()` is **False** under the executor's
  shell (verified). The read-only `gh issue list` dedup query at `submit.py:683` runs **before** the
  TTY branch at `:685`; off-TTY the function then prints the issue URL and returns — `submit_via_gh`,
  `comment_via_gh` and the confirm prompt are all unreachable. **Nothing is filed.**

</domain>

<decisions>
## Implementation Decisions

### The divergence rule (SC#3 / SC#4)

- **D-01: A row cites every prior sweep that touched the part; `same`/`diverges` is keyed on the write-path headline.**
  *(Claude's call — the user answered "You decide".)* v1.15 alone holds up to
  four dispositions per part (Phase 81 read sweep, 82 A→B write, 83 UV write, 84 FIX-01 re-bench),
  and "PASS" means a different thing in each. Citing all of them costs a table column and discharges
  SC#3's "no row where the v1.15 disposition itself is left unsourced" and SC#5's "cited inline in
  their own row" in one move.

  Rejected: a single write-path headline with the read as fallback (loses that a part can be P81-read
  PASS and P82-write FAIL, which is exactly W27E512's and W27E040's shape); and a **per-operation**
  disposition set (v1.15 measured `erase` and `blank-check` for essentially nothing, so most cells
  would read "no v1.15 disposition" — it manufactures divergences out of *absent* data, and under
  SC#4 every divergence costs a real chip swap and a bench re-run).

- **D-02: `diverges` means any comparable per-step flip, in either direction.** *(User's choice.)*
  Compare `dev test`'s per-step verdicts — `id`, `read`, `write`, `verify`, `erase`, `blank-check` —
  against the prior disposition wherever the prior sweep measured that op. The column **names the
  step and the direction**, e.g. `diverges: write OK→BAD` or `diverges: verify BAD→OK`.

  Rejected: keying on the overall exit code (it is a `max()` over steps, so a part whose `write`
  newly fails while `read` still passes still exits 1 and reads as "same FAIL as v1.15" — hiding a
  regression behind an unchanged headline); and write-path-only (silently forgives a newly-broken
  `id` or `read`).

- **D-03: Where no comparable prior disposition exists, the row reads `diverges: no comparable baseline — <why>`, and the control arm supplies the baseline.**
  *(User's choice.)* This keeps
  SC#3's column at exactly two values while refusing to claim agreement with a measurement that was
  never taken. The control re-run is the right instrument here, not a formality: with no historical
  baseline, the control arm **is** the baseline, so the row still answers "is this arm-dependent?"

  **Known to apply, at minimum three rows:**
  - **W29C040** — `dev test` writes the device minus the first/last 16 KiB; v1.15 failed at
    `0x0000ff`, *inside* the carve-out. Different region.
  - **FM1608** — v1.15's PASS came from `write -b`, a flag now on the forbidden list. Different
    invocation.
  - **ST M27C512** — v1.15 wrote 16 B at `0x0000`; `dev test` writes a bit-masked 256 B slot near
    the top. Different region **and** different pattern semantics (`P = C & D`).
  - **AM27C020 — unresolved, and the planner must settle it.** Its disposition is v1.18's (see
    D-04), whose bench figures are `write#1 60/64, write#2 0/64` — a **64-byte** write against
    `dev test`'s 256-byte masked slot. Read `.planning/v1.18/bench/EVIDENCE.json` and decide
    comparability from the record, not from the summary prose.

  Rejected: `same` unless the run is bad (a green run standing as "agrees with v1.15" when v1.15
  never measured it is precisely the inferred-from-nothing claim Phase 166's honesty ledger exists
  to catch); and a documented third column value (breaks SC#3 as written and forces Phase 166 to
  reconcile a three-state column).

- **D-04:** A row compares against the *most recent* recorded disposition, with v1.15 as the floor, and names which milestone it came from.
  *(User's choice.)* This reads the roadmap's "recorded
  v1.15 disposition" as **naming the sweep, not forbidding a later correction**. It is a deliberate,
  stated interpretation of SC#3 and must be recorded as such so Phase 166 sees the reading rather
  than inheriting it silently.

  **The supersession is narrow but lands on an SC#5 part.** `.planning/v1.18/bench/EVIDENCE.json`
  covers only **AM27C020** and **W27C512** (its differential control). v1.18 Phases 97–99 shipped a
  real fix — a scoped `DIP32_27C020` pinout with `rw-pin:[31]` → `CTRL_READ_WRITE` (0x40) — that
  **refuted v1.15's 0-bits signature**. Comparing `dev test AM27C020` against v1.15 would book a
  guaranteed `diverges` that is v1.18's fix working as designed, and spend a control re-run
  re-confirming a two-milestone-old result.

  Rejected: literal v1.15-only (books that known-false divergence); and carrying both a v1.15 column
  and a superseding column (same re-run count, wider table, a second unsourced-cell risk per row).

- **D-05: Symptom-identity counts as a flip — but only where the record calls the fault deterministic.**
  *(User's choice.)*
  - **Deterministic, so a moved symptom diverges:** W27E512 (`bit 7 @0x3d`), W27E040
    (`bit 4 @0x7db`), W29C040 (`timeout @0x0000ff`) — all three recorded deterministic across
    initial run plus reseats. A changed offset or byte is `diverges: symptom moved <from> → <to>`
    and earns a control re-run, because a stuck bit that **moves** is new silicon behaviour or a new
    addressing fault, not the known one.
  - **Non-deterministic, so symptom variance is expected and never triggers:** AM27C020 (marginal by
    record) and — had it run — 2516. Variance is recorded in `anomalies` instead.

  Rejected: verdict-only (lets a moved stuck bit pass as "same as v1.15"); and symptom-identity
  everywhere (books re-runs on the two parts recorded as unable to arbitrate anything, which are
  guaranteed uninterpretable).

- **D-06: SC#4's arithmetic is stated as `10 + N`, with the deviation from the roadmap's `11 + N` named on the same line.**
  Decided mechanically — it follows from D-14. The reconciliation shown is
  `10 reports + 1 named absence = 11 parts`, and separately `10 primary runs + N control re-runs =
  total runs`. **N is expected to be ≥ 3 before any genuine flip** (D-03), and the planner should
  budget for it rather than discover it.

### Procedure and evidence shape

- **D-07: `PROCEDURE.md` gains Amendment 4 — a parallel `C-01…C-NN` chip-sweep step list in the same file.**
  *(User's choice.)* The chip sweep shares `P-01` (mount and declare), `P-02` (re-verify port
  identity), `P-04` (flash + independent read-back proof), `P-06` (pot) and `P-11` (teardown +
  config-dir check) **by reference, never by copy**, and adds only the steps `dev test` actually
  needs. Amendment 4 must also **correct §Scope**, which currently claims to cover Phase 162 while
  describing only the WRV cell shape.

  Follow the established amendment discipline: (a) what changed, (b) why, (c) which cells ran under
  which text — and **re-confirm the `render_steps.py --arm control` vs `--arm v133` empty-diff gate
  after the edit**, exactly as Amendment 3 did. New text must carry no `$ARM_BIN` token, so the diff
  should stay empty.

  Rejected: a separate `CHIP-PROCEDURE.md` (creates a second document every standing-rule change has
  to be applied to twice — the drift the amendment discipline exists to stop); and citing the
  applicable subset with the sweep's own steps living only in plan files (leaves PROCEDURE.md's
  "executed unchanged by Phase 162" claim standing and false).

- **D-08: The chip sweep's record is a sibling `.planning/v1.34/bench/CHIP-EVIDENCE.jsonl` with its own `_schema`.**
  *(User's choice.)* Same two-tier shape as the WRV file: the **identical 9
  `locked_columns` core** — which Phase 166's CLOSE-01 asserts uniformly across every milestone's
  evidence file — plus a chip-specific extension list for the `dev test` fields (`fw_board_identity`,
  per-step verdicts, `write_coverage`, `run_count`, report artifact path and sha, prior disposition
  and its source milestone, divergence verdict, VPP target/achieved/firmware/shortfall). Its own
  `position_count_expected` and its own reconciliation arithmetic, so **`EVIDENCE.jsonl`'s 20 stays
  20 and is not touched by this phase**.

  Rejected: reusing `EVIDENCE.jsonl` behind a `CHIP-` prefix exclusion (each row would carry all 31
  WRV extension columns as `"not measured — …"`, which is 31 noise fields per row and stretches that
  convention well past what it was built for); and a markdown table only (Phase 166 SC#1 wants the
  chip sweep reconciled as **arithmetic over rows**, and a hand-maintained table is what
  `render_evidence.py` exists to prevent).

- **D-09: Build `append_chip_evidence.py` and `render_chip_evidence.py`; the appender copies the report artifact out.**
  *(User's choice.)* This extends Phase 161's D-05 precedent directly, and the
  argument is stronger here because `dev test` already emits machine-readable JSON — **every machine
  field is derivable, so none is transcribed.** The appender:
  - reads the `dev test` JSON report plus the position's provenance and derives every machine field;
  - **copies `<config dir>/reports/dev-test-<chip>.{json,md}` to a per-position artifact path before
    the next run can overwrite it** — the path is fixed per chip, so the control re-run destroys the
    v1.33 report otherwise;
  - refuses an incomplete position;
  - takes only the genuinely human fields (verdict prose, `anomalies`, the operator's meter reading).

  **Hard constraint:** `run_gates.sh` discovers every `*.py` under `tools/` and **fails the suite** if
  one does not advertise `--selftest`. There are 12 today (12/12 selftests + 5/5 live gates); both new
  tools must ship one, taking the suite to 14/14.

  Rejected: extending `append_evidence.py` with a `--chip` mode (welds two unrelated schemas into one
  tool that is already load-bearing for the 20 WRV positions this phase must not disturb); and an
  appender with no renderer (`EVIDENCE.md` is regenerated and byte-compared throughout this milestone;
  a one-off close-time generator gets no such check).

- **D-10:** The `gh` dedup query is allowed to run, is declared, and nothing-was-filed is *proven*.
  *(User's choice.)* `submit.py` differs **105 lines** between the arms, so suppressing this path
  would skip validating a v1.33-modified file in the middle of a milestone whose entire purpose is
  validating v1.33. Each run records its dedup outcome (found / ran-and-found-nothing /
  could-not-run). For CLOSE-04, capture an **issue-count-before/after for `henols/firestarter_prom`
  as pasted command output**, not an assertion — the criterion explicitly refuses assertions.

  Rejected: shadowing `gh` off PATH (deterministic and zero-network, but exercises the degraded
  branch instead of the real one and would hide a v1.33 regression in the dedup path); and allowing
  it with only a code citation as evidence (a code citation *is* an assertion).

### VPP and the pot

- **D-11: The pot is set per part, from the multimeter.** *(User's choice, made with the
  reachability caveat stated.)* Every part records its **own** VPP figures — target, achieved real
  rail, firmware reading, and the shortfall — rather than inheriting one setting carried across the
  sweep. This is materially better evidence for Phase 166's honesty ledger, where every VPP figure
  must be labelled.

- **D-12: Where the DB target is unreachable, "the setting" is the highest real rail that keeps the firmware reading in band.**
  *(User's choice.)* Set the meter as high as possible while the firmware
  reading stays under `vpp_mv + 500`, because **high is the blocking error and low is only a
  warning** (D-domain fact 3).
  - **12 V group (8 of the 10):** the current setting is already in band; target reachable.
  - **13 V pair (M27C512, AM27C020):** ceiling is 13500 mV firmware-reported → aim ~13.2–13.3 V
    firmware, i.e. a real rail ≈ **12.3–12.4 V** instead of today's 11.44 V. Roughly +0.9 V of real
    rail, still in band, and it lands on the two parts whose writes are irrecoverable.
  - Each part records `vpp_target_mv`, `vpp_real_mv` (meter), `vpp_firmware_mv`, `vpp_shortfall_mv`,
    so an under-voltage failure is attributable rather than mysterious.

  Rejected: leaving the 13 V pair at today's setting (wastes ~0.9 V of *reachable* headroom on the
  two irrecoverable writes); and setting the real rail to the DB target regardless (raises
  `MSG_ERR_VPP_HIGH` and blocks, with `--force` permanently withdrawn by Phase 145 D-17).

- **D-13: One meter reading per pot change, one firmware VPP reading per part.** *(User's choice.)*
  The meter comes out when the pot actually moves — **twice** in this sweep (the 12 V group, then the
  13 V pair). Every part still records its own firmware VPP reading taken at its own seating, so each
  row carries a per-part figure and the meter-to-firmware ratio measured at the group boundary makes
  the real rail derivable per part. **The pot step folds into the chip-swap handover** — one operator
  stop per part, not two — which is what 161 D-02 requires.

  Standing rules that bind: the operator adjusts the pot and reads the meter **solo**; state the
  target, wait, take **one** read; **no live monitor loops**. A blank or `0x303` VPP reading is a
  contact fault, not a voltage measurement.

  Rejected: a fresh meter read for all ten (would independently re-measure the ×1.075 ratio ten times
  — real data, but ten meter sessions on top of nine chip swaps); and metering only at pot changes
  with no per-part firmware read (a contact fault or a drifting rail between parts would be invisible,
  and `0x303`/blank is exactly how a contact fault surfaces on this rig).

### UV parts, run depth and sequencing

- **D-14: The 2516 is a named absence — unsupported hardware on Rev 2.0.** *(User's declaration,
  2026-08-27: "for the 2516 it is only 2.2 and above that is supporting and there must be more work
  done before we can test it.")* It is **not seated, not read, and not written** in this phase. The
  reason recorded is a hardware fact of the same class as SC#1's own "adapter absent" example — not
  a preference, and specifically **not** the "we chose not to run it" shape that 161 D-07 called a
  weak name.

  Corroborating context, recorded but **not** the reason: 2048 B gives it only 8 slots, so one
  `dev test` slot is 12.5% of the part; its DB VPP target is 25000 mV against a shield that reached
  15.3 V in v1.15; and its read produced 3 distinct SHAs on **every** recorded attempt across v1.15
  Phase 81 and Phase 84.

  This supersedes the earlier discussion option of a read-only 2516 observation on this rig. Do not
  re-open it here.

- **D-15: M27C512 and AM27C020 are run — this is the UV masked-write path's first hardware exercise.**
  *(User's choice.)* Both have slots to spare (~256 and ~1024). Running them also
  discharges the standing 260821-wna item that has **zero hardware evidence**: whether `P = C & D`
  behaves as predicted on partially-programmed silicon, and whether slot advance works across
  consecutive runs. Each loses one 256-byte slot, irrecoverably.

  **Record the slot actually written and the count remaining** — the report carries this, and it is
  the disclosure that replaced the removed consent prompt.

  Rejected: holding all three UV parts for a separate operator-initiated session (leaves 3 of 11 rows
  unfilled and defers the divergence table's completeness past this phase).

- **D-16: Default 2-cycle `dev test` on all ten. No `--fast`.** *(User's choice.)* Estimated ~65 min
  of machine time. `--fast` disables the two measurements this phase most needs — an intermittent
  write cannot be reported marginal, and read nondeterminism goes unmeasured — and **read
  nondeterminism is a live open question**: Phase 161 cell A2 produced 3 distinct SHAs on the same
  chip and the same arm, still UNDETERMINED, with A3/B2 supplying a non-resolving counter-data-point.
  Halving the sweep to save ~28 min would blind it to exactly that.

  Rejected: `--fast` on the three 512 KiB parts (two of the three are SC#5 known-carried parts whose
  reds must be distinguishable from new faults, so it degrades the rows most likely to need
  arbitration); and `--fast` everywhere (every report becomes second-class evidence by the tool's own
  documentation — "such reports never count toward community agreement" — under a milestone whose
  output is a merge recommendation).

- **D-17: Control-arm re-runs are interleaved, arbitrated with the chip still seated.** *(User's
  choice.)* When a part diverges: re-flash the Leonardo to the control arm, re-run **that same part
  with the chip unmoved**, then re-flash back to v1.33. Two flashes per divergence, **zero extra chip
  handlings** — trading a pre-authorised free resource for the scarce, operator-only one. Phase 161
  had to record a condition caveat on the shared W27C512 after eight handlings; this keeps the count
  down. It also gives the strongest possible A/B: the part's seating and pot setting are provably
  identical across both arms.

  **Every re-flash carries its own `P-04` read-back proof** — the arm is confirmed by on-device
  read-back, never assumed from the flash command. The Leonardo is **chip-out-exempt**, so the seated
  chip stays put across all of it.

  Note the deliberate inversion: Phase 160 locked "control first, so the control arm never inherits
  the other arm's chip contents". Here **v1.33 runs first**, forced by SC#4 (a control run for every
  part is explicitly forbidden). For `dev test` this is benign — each run writes and verifies its own
  pattern — but on the two UV parts the control re-run will land on the **next slot**, not the same
  one, because slot selection is stateless and keyed on chip content. **Record that, do not fight
  it.**

  Rejected: batching all re-runs after the sweep (one flash, but every divergent part gets two extra
  handlings and the A/B pair no longer shares a proven seating); and interleaving without re-flashing
  back (splits the sweep across arms, so some parts' primary result would be a control result —
  breaking SC#1's "produced on the v1.33 arm").

- **D-18: Part order minimises pot and JP4 movement; the already-seated part runs first.** Decided
  mechanically from D-11/D-13 and the package/VPP groups. **One pot move, two JP4 changes, nine
  seatings:**

  | # | Part | Pkg | VPP | Handover |
  |---|---|---|---|---|
  | 1 | W27C512 | DIP28 | 12 V | *(already seated — zero handling)* |
  | 2 | W27E512 | DIP28 | 12 V | swap *(shares W27C512's DB row — adjacent on purpose)* |
  | 3 | SST27SF512 | DIP28 | 12 V | swap |
  | 4 | FM1608 | DIP28 | 12 V | swap |
  | 5 | W27E040 | DIP32 | 12 V | swap + **JP4 → 32-pin** |
  | 6 | SST39SF040 | DIP32 | 12 V | swap |
  | 7 | W29C040 | DIP32 | 12 V | swap |
  | 8 | W29C020 | DIP32 | 12 V | swap |
  | 9 | AM27C020 | DIP32 | 13 V | swap + **pot → 13 V group** (meter read) |
  | 10 | ST M27C512 | DIP28 | 13 V | swap + **JP4 → 28-pin** |

  The planner may reorder **on evidence** (e.g. a part must move to keep a stall ceiling derivable),
  but not on preference, and any reorder must state its cost in pot/JP4 movements.

### Claude's Discretion

The user answered **"You decide"** on D-01; D-06, D-18 and the items below were decided mechanically
because precedent settles them. The planner may revisit these on evidence, not on preference:

- **`fw_board_identity` pre-flight (SC#2).** A null is a *defect with a named owner*, and Phase 147
  shipped the fix — so a null here is a regression. Discovering it at part 10 wastes the sweep.
  Take one `read_programmer_identity` probe as a **pre-flight bring-up datum, outside the
  `C-01…C-NN` step list**, before any part runs. Mirrors 161 D-10's de-risking argument exactly.
  ~10 s. If it is null, that is a `P-H1` halt and an opened defect, not a carried gap.
- **Halt mapping.** A `dev test` **BAD on a part is a result — `P-H2`**, carried forward; that is
  what the sweep exists to produce. `P-H1` stays reserved for **rig** faults: a null
  `fw_board_identity`, a read-back mismatch after a correct flash, a blank or `0x303` VPP reading
  (contact fault, not a voltage), or a change to `~/.firestarter/config.json`.
- **Stall ceilings, per 161 D-08's pattern.** Derive **4× a measured healthy figure per size class**
  — the first part of each class supplies it (64 KiB from part 1, 512 KiB from part 5, 256 KiB from
  part 8). State a fallback absolute where no healthy figure exists yet. **The logging half is the
  load-bearing half**: a kill runs under a numbered log with full stdout/stderr and the last progress
  frame captured, recorded as `timed out at N s against a measured baseline of M s`. Phase 160's one
  *unlogged* timeout kill is what produced the untraceable `~/.firestarter` contamination.
  Remember write-progress emission is **time-keyed per block with the clock restarting each block**,
  so the last frame names a block, not a byte offset.
- **Wave/gate granularity.** `bash .planning/v1.34/tools/run_gates.sh` is the per-wave gate, with the
  **exit code measured directly, never through a pipe**. A wave is naturally a pot/JP4 group.
- **Per-position paths and artifact volume.** Follow `IMAGE-PLAN.json`'s `artifact_volume_policy`,
  including its **commit-on-failure exception**, for the copied-out `dev test` artifacts.

Still open, and left to research/planning:

- **AM27C020's comparability under D-03** — read `.planning/v1.18/bench/EVIDENCE.json` and settle
  whether a 64-byte v1.18 write is comparable to a 256-byte masked slot. The rule is locked; the
  application to this one row is not.
- **FM1608's `vcc_mv: 3300`.** Every other part in the sweep declares 5000. Whether the Rev 2.0
  shield honours a 3300 mV VCC, ignores it, or the field is decorative is **unresolved** — resolve it
  *before* the part is written, and record the answer either way. It also interacts with the known
  byte-0 defect below.
- **The concrete `append_chip_evidence.py` interface** — arguments, where the human fields enter, how
  it refuses an incomplete position. D-09 locks the properties, not the CLI.
- **Measured duration budget.** The table in D-16 is *extrapolated* from `BRINGUP-wrv`'s 65536 B
  figures and v1.15's SST39SF040 note. Measure rather than trust it; part 1 supplies the first real
  `dev test` figure this project has ever taken on this rig.

### Folded Todos

`todo.match-phase 162` returned **28 matches**. None is folded as *work* — this phase changes no
product code. **One is folded as a citation**, because it changes how a row is read:

- **`fm1608-byte0-write-never-lands-register-cache-elision.md`** (firmware, score 0.9) — a recorded
  firmware defect in which the register cache-skip elides all three shift-register strobes so
  FM1608's byte 0 never lands. FM1608 is part 4 of this sweep with a **full-device** write. If that
  defect manifests, the row must cite this todo as a **known-carried, pre-existing** disposition so
  its red cannot enter Phase 165's failure set or Phase 166's findings as a v1.34 discovery. Folded
  as a citation only; **the fix is not in scope.**

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The rig — binding, produced by Phase 160, amended by Phase 161

- `.planning/v1.34/PROCEDURE.md` — the bench document. Standing bench rules (9), the halt policy
  `P-H1`/`P-H2`, the forbidden-invocation table, the recording discipline, the outcome taxonomy, and
  Amendments 1–3. **§Scope currently describes only the WRV cell while claiming to cover Phase 162 —
  Amendment 4 (D-07) fixes that and adds the `C-01…C-NN` list.**
- `.planning/v1.34/rig-pins.json` — arm binary paths (`arms.v133.venv_bin`, `arms.control.venv_bin`),
  per-target avrdude/programmer policy, `hex_span_expected_by_arm` (**use this, never the legacy
  scalar**), `forbidden_flags`, `forbidden_argv0`, the frozen `config_dir`. **Its `chips` map holds
  only `w27c512` and `w29c020`** — this phase needs nine more parts; decide whether to extend it or
  read the app DB directly.
- `.planning/v1.34/tools/` — `run_gates.sh` (per-wave gate; **exit code measured directly, never
  through a pipe**), `append_evidence.py` (the D-05 precedent this phase extends), `capture_provenance.py`,
  `judge_readback.py`, `probe_board.py`, `gate_record.py`, `render_evidence.py`, `render_steps.py`,
  `check_arms.py`, `touch_1200.py`. **12 tools today; every `*.py` must advertise `--selftest` or the
  suite fails.**
- `.planning/v1.34/bench/EVIDENCE.jsonl` — line 1 `_schema`. **Read it to understand why D-08 needs a
  sibling file**: `locked_columns` (9, reusable), `evid_extension_columns` (31, all WRV),
  `position_count_expected: 20`, `close01_counting_rule`, the `BRINGUP-` exclusion mechanism (the
  model for the sibling's own exclusions), `not_measured_convention`, `negative_control_convention`.
  **This phase does not append to it.**
- `.planning/v1.34/bench/IMAGE-PLAN.json` — `artifact_volume_policy`, including the
  **commit-on-failure exception**, which governs the copied-out `dev test` artifacts.
- `.planning/v1.34/PHASE-160-GATE.md` §6 — the six accepted carry-forward limits. **Disclosed, not
  new gaps; do not re-raise them as findings.**

### Prior phase decisions this phase inherits, not re-opens

- `.planning/phases/161-board-board-sweep-three-boards-on-rev-2-0/161-CONTEXT.md` — D-01…D-12.
  Especially **D-02** (no handover until a real physical action — governs plan authoring directly),
  **D-03** (records written per position), **D-05** (the derive-never-transcribe argument this phase's
  D-09 extends), **D-08** (stall ceilings and the load-bearing kill log), **D-11/D-12** (the
  leave-state this phase inherits).
- `.planning/phases/160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur/160-CONTEXT.md`
  — D-01…D-18. Especially **D-01/D-02** (read-back proof, judged span), **D-05** (the proof runs at
  *every* flash — binds D-17's interleaved re-flashes), **D-15** (JSONL canonical), **D-18** (outcome
  taxonomy).
- `.planning/phases/161-.../161-05-SUMMARY.md` and `.planning/v1.34/bench/cells/A3-B2/POT.md` — the
  **ratiometric VPP-ADC finding** (~+7.5%, range 6.8–8.3%) that D-12 depends on, with its three
  paired firmware-vs-meter readings.

### Prior dispositions — the baselines D-01/D-04 compare against

- `.planning/v1.15/bench/EVIDENCE.md` — **the primary baseline.** Four sweeps: Phase 81 read sweep
  (10 PASS / 1 ANOMALY), Phase 82 A→B write validation, Phase 83 UV write proof, Phase 84 FIX-01
  re-bench. Also `.planning/v1.15/bench/EVIDENCE.json` for the machine-readable form and the
  `locked_columns` origin.
- `.planning/v1.18/bench/EVIDENCE.json` — **supersedes v1.15 for AM27C020** (and carries W27C512 as
  its differential control). The `write#1 60/64, write#2 0/64` figures live here, not in v1.15.
  D-03's open AM27C020 question is settled from this file.
- `.planning/v1.16/ledger/PROTOCOL-LEDGER.md` — per-algorithm standing (`0x05`, `0x06`, `0x07`,
  `0x08`, `0x0B`, `0x40`), including the `0x08` open-defect-carried entry.
- `.planning/todos/pending/fm1608-byte0-write-never-lands-register-cache-elision.md` — the folded
  citation (see Folded Todos).

### Milestone definition (binding)

- `.planning/ROADMAP.md` §"Phase 162" — the goal and **Success Criteria 1–5**, which this phase is
  measured against. **SC#4's `11 + N` is read as `10 + N` per D-06/D-14.**
- `.planning/ROADMAP.md` §"v1.34 — Pre-Merge Hardware Regression Validation" — the failure policy,
  the declared known faults, the merge posture, the branch model.
- `.planning/ROADMAP.md` §"Phase 166" — CLOSE-01's reconciliation ("plus the 11-part chip sweep and
  its divergence re-runs") and CLOSE-04's **pasted-command-output** requirement, which D-10 serves.
- `.planning/REQUIREMENTS.md` — **CHIP-01…05** (lines 57–61) and the Out-of-Scope list.

### The command under test — read the arm's own source, not the repo tip

- `/workspaces/.v1.34-arms/v133/firestarter/cli_handlers.py` — `dev_test` handler (`@dev.command(name="test")`),
  `_resolve_write_scope`, `_is_interactive`, `_chip_id_fields`, the fixed report path.
- `/workspaces/.v1.34-arms/v133/firestarter/chip_test.py` — `derive_plan`, `run_plan`,
  `_WRITE_REGION_LENGTH`/`_UV_WRITE_REGION_LENGTH` (256), `_UV_MIN_CLEARED_BITS`/
  `_UV_MIN_RETAINED_BITS` (64).
- `/workspaces/.v1.34-arms/v133/firestarter/submit.py` — `submit_report` (the off-TTY branch at
  `:685`), `find_prior_report` (the dedup query at `:683`, **before** the TTY branch).
- `/workspaces/.v1.34-arms/v133/firestarter/diagnostic_report.py` — `to_dict`, `dedup_fingerprint`,
  `write_coverage`, the report schema the appender derives from.
- `/workspaces/firestarter/src/proms/eprom.cpp` §`eprom_check_vpp` (lines 512–539) — **the asymmetric
  guard**: `+500 mV` is a blocking ERROR, `−5%` is a non-blocking WARNING.
- `/workspaces/firestarter/include/rurp_hw_rev_utils.h` — `rurp_detect_hardware_revision`, and why
  Rev 2.0/2.1/2.2 bucket together at R41 = 4k7.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **The rig is the reusable asset.** 12 tools behind one gate (12/12 selftests + 5/5 live gates,
  proven to fail closed with exit 1). This phase adds **exactly two** tools (D-09) and **one**
  procedure amendment (D-07). It builds nothing else.
- `append_evidence.py` — the **shape to copy**: derives every machine field from provenance and
  verdict files, takes only human prose, ships `--selftest`. D-09's tool is its sibling, not its
  extension.
- `capture_provenance.py` — takes `--cell-id --position-id --arm --target --port --chip
  --shield-rev`; **hard-refuses without the position's read-back verdict** and **refuses to run
  without an operator-declared shield revision**. Reusable as-is for the chip sweep's positions.
- `judge_readback.py` — runs its own avrdude read with **`-A` explicit** (without it the read-back
  truncates); this is what makes D-17's interleaved re-flashes provable rather than assumed.
- `gate_record.py` — enforces field presence, the `"not measured — <reason>"` shape as a valid
  non-null, the outcome domain, and **rejects forbidden flags by exact token match anywhere in a
  recorded argv**. The sibling JSONL should be gated by it too.
- `render_evidence.py` — the `--check` byte-identical regeneration pattern D-09's renderer copies.

### Established Patterns

- **The judged verdict and the unjudged verdict are recorded separately, and their disagreement is
  itself a finding** — never resolved by preferring one. `dev test` already does this internally:
  `chip_id_actual` is `None` on a pass because the firmware's OK reply carries no id, so the host
  refuses to present its own expected value as a measurement. **Do not "fix" that `None`.**
- **A negative control is recorded as having FIRED, not as having been configured.**
- **Nothing is fabricated.** A blocked reading is `"not measured — <reason>"` on the same line.
- **No SHA is ever transcribed by hand** — computed by a tool and written by that tool. D-09 extends
  this from provenance fields to the chip-evidence row.
- **A wrong record is marked SUPERSEDED and kept visible, never erased.**
- **One clean re-seat per position** (standing bench rule 8) — **both** the discarded attempt and the
  re-run are recorded.
- **`dev test`'s repeat is a CYCLE, not a retry.** The write/verify block runs twice and the cycles
  are compared — it is a rig-health check for rail droop and bad contact. `duration_s` is a **cycle
  sum, not an op cost**; divide by `run_count` before quoting a per-op figure.

### Integration Points

- **Measured rig facts inherited — do not re-derive.** Leonardo → avrdude 6.3, programmer `avr109`,
  `/dev/ttyACM0`, signature `atmega32u4` `0x1e9587`. **The 1200-baud touch returns the SAME node,
  never a new one** — use bare `touch_1200.py`; `--wait-new-port` was empirically refuted.
  Leonardo hex spans: control 28170 / v133 25098.
- **`FIRESTARTER_CONFIG_DIR` is set inline on every arm-invoking command, never exported.**
  `config.py` computes `HOME_PATH`/`DATABASE_FILE`/`PIN_MAP_FILE` as **import-time** constants, so a
  session-level export is a partial fix that *looks* complete. A shell `FOO=bar cmd` prefix is
  stripped before exec and **never reaches argv**, so an argv check cannot detect a missing prefix —
  **asserting `~/.firestarter` unchanged at teardown is the only detector.** Note `get_config_dir()`
  *is* call-time, which is precisely why the `dev test` report path honours it.
- **`~/.firestarter/config.json` has changed (mtime only, content identical) in all three Phase 161
  cells** — a standing `P-H1` finding handed to Phase 165. Expect a fourth recurrence here; record it,
  do not attempt to fix or delete it (the sandbox denies removal).
- **`pio` runs only with cwd `/workspaces/firestarter`** — the generated, gitignored
  `/workspaces/platformio.ini` has a duplicate `[platformio]` section that aborts `configparser`.
- **Every `import firestarter` probe needs `python -P`** — `/workspaces/firestarter` wins as a PEP 420
  namespace portion and the probe silently prints `None` without it. Prefer the arm's own
  `.venv/bin/python`.
- **JP4 governs 28-pin vs 32-pin seating** and moves twice in D-18's order. v1.15 recorded it closed
  for the DIP32 parts.

</code_context>

<specifics>
## Specific Ideas

- **"For the 2516 it is only 2.2 and above that is supporting and there must be more work done
  before we can test it."** — operator, 2026-08-27. This is the reason D-14 records, verbatim, and it
  is a *hardware* reason, not a preference. Nothing in this phase seats that part.
- **"I dont want any handover until a real physical action is needed."** — carried from Phase 161
  D-02 and it governs plan authoring here just as directly. `human-verify` checkpoints belong at the
  chip swap, the JP4 change and the pot adjustment, **and nowhere else**. No artificial park prompts,
  no "continue?" gates. D-13 folds the pot step into the swap handover for exactly this reason.
- **Read every `<automated>` verify leg before trusting it.** Phase 160's hardcoded-arm-agnostic-
  constant defect recurred **four times**; Phase 161 inherited the warning across twelve positions.
  This phase spans ten parts plus re-runs, where one wrong constant is ten false results.
- **This procedure must not run under `--auto` / `--chain` / any auto-advance mode** (standing bench
  rule 7). Those auto-approve the `human-verify` checkpoints every physical step depends on;
  `autonomous: false` on a plan is not self-protecting against that.
- The measured baselines to anchor on rather than guess: **W27C512 write 41.010 s wall / 37.48 s
  app-reported**, **3-run 65536 B read set 53.437 s**, **W29C020 read ≈ 42 s/pass** — the first two
  from `BRINGUP-wrv` on Uno + Rev 2.0. The duration table in D-16 is extrapolation, not measurement.

</specifics>

<deferred>
## Deferred Ideas

- **The 2516, entirely.** It needs a Rev 2.2-or-newer shield **and** further work before it is
  testable. Phase 163 cell B3 does mount the Rev 2.2 shield on this same Leonardo — but "more work
  first" makes this a **backlog item, not a fold into Phase 163**. File it as one; do not schedule it.
- **Fixing anything this phase finds.** Divergences are classified and fixed in **Phase 165**, on the
  **v1.33 PR branch**, not here and not on v1.34's branch. Phase 162 records; it does not repair.
- **The FM1608 byte-0 register cache-elision defect.** Folded here only as a *citation* (see Folded
  Todos). The firmware fix is out of scope in both directions — it is pre-existing, so it is also not
  a v1.33-caused regression Phase 165 would fix.
- **`~/.firestarter/config.json`'s recurring mtime change.** Third recurrence recorded in Phase 161
  (A1, A2, A3/B2); expect a fourth. Handed to Phase 165 under the D-16 boundary. **Do not attempt
  removal** — the sandbox denies it, and Phase 160's one unlogged kill during a removal attempt is
  what contaminated the directory in the first place.
- **Program-window VPP/VCC under load stays unmeasured.** The DTR-reset-on-close tooling gap has
  stood since Phase 97. **Every VPP figure this phase records is an idle firmware-ADC sample or an
  operator multimeter reading — never a program-window measurement.** Phase 166's honesty ledger owns
  the resulting non-claim; v1.34 makes **no electrical claim**.
- **The A2 N=3 read-instability question** remains UNDETERMINED. If a part in this sweep shows read
  nondeterminism, record it as a data point against that question — do not attempt to close it here.
- **Extending `rig-pins.json`'s `chips` map to the full inventory.** Whether the nine new parts get
  pinned there or read live from the app DB is a planning call; if pinned, that pinning is a rig
  asset future phases inherit, and it should not be done casually mid-sweep.
- **Phase 164's Modified Rev 0 work** — the board photograph and the `MODIFICATIONS.md` rework trace.
  Both surfaced again in this phase's todo scan; both need the board Phase 163's cell B1 puts on the
  bench.

### Reviewed Todos (not folded)

`todo.match-phase 162` returned **28 matches**; **one folded as a citation** (FM1608 byte-0, above),
**27 not folded.** Every non-folded match is a product-code item — firmware or host app — and this
phase changes no product code. The matches are keyword coincidences on `chip`, `write`, `blank`,
`check`, `phase`, `dev`, not scope overlaps.

Worth naming, because they are near-misses rather than noise:

- **`2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md`** (firmware, 0.9) —
  genuinely adjacent to D-11/D-12's guard analysis, and the sweep's under-voltage warnings will
  exercise exactly this path. It is still a **product change**, so it stays out. If the sweep produces
  evidence about it, record the evidence on the todo; do not implement.
- **`at28c256-write-path-failure-gh20.md`** (general, 0.6) — a `dev test` failure on a different part
  and a different shield revision. Not in this inventory; not in scope.
- **`photograph-operator-modified-rev0-board.md`** and **`write-full-modifications-md-rework-trace.md`**
  — REV0-01…03 work belonging to **Phase 164**, as recorded in Phase 161's own scan.
- **`avrdude-mcu-detection-fallback.md`** — folded **as mechanism only** by Phase 160 D-14; stays
  `pending` for its product deliverable and is not re-folded here.

</deferred>

---

*Phase: 162-chip-11-part-dev-test-sweep-on-the-reference-rig*
*Context gathered: 2026-08-27*
