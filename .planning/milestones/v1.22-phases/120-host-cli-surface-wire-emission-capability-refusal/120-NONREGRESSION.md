# Phase 120 Non-Regression Sweep — the enumerated command-by-protocol exception record

**Written:** 2026-07-29 (Plan 120-12)
**Firmware phase base:** `0048b3d` (`firestarter`, Phase 119's own sweep HEAD — Phase 120 is host-only and never touched firmware) · **Host phase base:** `9ead17f` (`firestarter_app`, Phase 119's own sweep HEAD) · **Meta phase base:** `6857149` (`.planning`, Plan 120-11's amendment commit)
**Firmware HEAD at this sweep:** `0048b3d` (unchanged) · **Host HEAD at this sweep:** `96e0622` · **Meta HEAD at this sweep:** `6857149` (this plan's task commits land on top)

This is the single artifact a later reader should open to answer "what did Phase 120 change,
and what did it prove unchanged". It aggregates and re-derives (never merely copies) the claims
made in `120-01`..`120-11`'s SUMMARYs, re-executes the full nine-row cross-repo gate table plus
the full host suite at the phase's final commit, verifies both frozen-artifact fences, and
discharges the operator's `dev test --submit` repo-target ask as a verification.

---

## 1. The claim, stated precisely

Phase 120 is the milestone's host-only wave: it wires the CLI and serial surface to the
firmware capability Phase 119 already shipped, and adds no new firmware behaviour whatsoever.
The claim is three precise statements, and anything not covered by them is unchanged:

1. **The host now emits `cmd 9` (`CMD_SDP_UNLOCK`) / `cmd 10` (`CMD_SDP_LOCK`) and
   `FLAG_SKIP_SDP_UNLOCK 0x100`**, and firmware and host are proven to agree on every `CMD_*`
   and `FLAG_*` value bidirectionally by a real header-parsing gate with planted-violation
   fixtures (`tests/test_revision_constants_parity.py`, rebuilt by Plan 120-07) — not merely by
   hand-transcribed literals as before this phase.
2. **A fail-closed pre-wire capability refusal keeps SDP commands away from 41 of the 84
   protocol-`0x0D` parts** on **both** the `dev sdp` path (Plan 120-08) and `write`'s automatic
   unlock (D-04, Plan 120-09), with **zero `chip_database.json` change** — the partition lives
   entirely in `firestarter/sdp_capability.py`, derived from `infoic.xml` bit 15.
3. **One class of previously-invisible firmware report lines is now visible at default
   verbosity** (D-09's INFO-band promotion in `_log_rurp_feedback`, closing a whole-phase gap
   where Phase 118's firmware-side work was silently discarded host-side), **and one class of
   previously-silent host failures is now loud and failing** (D-15: a declined unlock that
   firmware never acknowledged now fails the write instead of proceeding silently).

Everything else — the firmware tree itself, every non-`0x0D` protocol's dispatch, the DB, the
catalog codegen ritual — is unchanged, and this document proves that rather than asserting it.

---

## 2. The changed-surface matrix

| Surface | Protocol scope | Before Phase 120 | After Phase 120 |
|---|---|---|---|
| `dev sdp <chip> enable\|disable` | `0x0D` only | Did not exist | New command (Plan 120-08). Gate order: absent-chip hard-fail → capability refusal → support-status → confirm/`-y` → serial. `Confirm.ask` and `find_and_connect` are both proven never-called on any refusal — proven by mock assertion, not exit code. Exhaustive over all nine `adapter-required` `0x0D` parts: each hears the *capability* refusal reason, not the adapter reason (D-08 gate ordering). |
| `write --skip-sdp-unlock` | any (semantics differ by protocol) | Flag bit `0x100` undefined on the host; no CLI surface | Host emits `FLAG_SKIP_SDP_UNLOCK 0x100` (Plan 120-09). On `0x0D`: the intended skip. On non-`0x0D`: D-18 warns ("this chip's protocol does not use software data protection") and proceeds — the bit is still emitted, harmlessly, since firmware only reads it on `0x0D` writes. |
| `write` (no flag) on a capability-*refused* `0x0D` chip | `0x0D`, REFUSE partition (41 of 84) | Firmware's auto-unlock sequence (visible since Phase 118's D-09) always ran | **D-04 auto-sets `FLAG_SKIP_SDP_UNLOCK`** on these chips and prints an unconditional report line. **This is a deliberate host-side behaviour change, never a no-op**: `write` on this 41-chip subset now differs from shipped `3.0.0b11`, on purpose, because attempting the unlock sequence on a part with no SDP command decoder is not inert (HOST-04's rationale for a fail-closed allow-list over the roadmap's literal five-part deny-list). |
| A write with `FLAG_SKIP_SDP_UNLOCK` set, on `0x0D` | `0x0D` only (scoped via `algorithm == SDP_PROTOCOL_ID`, mirroring D-18's predicate) | N/A — bit did not exist | D-15 (Plan 120-10): requires firmware's `MSG_WARN_SDP_UNLOCK_SKIPPED` (`0x86`) ack, read from a new bounded `SerialCommunicator.seen_message_ids` set populated in `_decode_id_frame`. Absent → the write fails loudly, naming `firestarter fw --install` as the remedy. Detects after the fact; does not prevent. |
| INFO-band serial frames (`0x5B`, `0x5E`, `0x5F`, `0x60`, `0x61`, `0x62`) plus `MSG_WARN_SDP_TBLC_EXCEEDED` (`0x87`) | all protocols that can emit them | `_log_rurp_feedback` mapped the entire INFO band to `logging.DEBUG`, invisible at default verbosity, regardless of root logger level | D-09 (Plan 120-03) maps `response.type == "INFO"` to `logging.INFO`. **Six** ids become visible for the first time at default verbosity — not five, because Phase 35's CR-02 hardware-revision warning (`0x5B`) rides the same promotion. `0x87` prints at WARNING and the exit code stays `0` (D-11). |
| `MSG_ERR_UNKNOWN_CMD` on the SDP command path | `0x0D` (or any protocol, if a raw `cmd: 9`/`10` were hand-crafted) | N/A — no CLI path sent cmd 9/10 | D-14 (Plan 120-08) maps this to a firmware-too-old CLI message. **Carried-forward finding, not fixed by this plan (out of file scope):** the real wire-to-CLI propagation path for this error class is dead in production — `EpromOperationError` carrying `MSG_ERR_UNKNOWN_CMD` is swallowed twice, once in `SerialCommunicator.find_and_connect` → `_probe_port`'s `expect_ack()`, and again in `EpromOperator._run_state_machine`'s own `except EpromOperationError` clause. D-14's mapping is unit-proven only via a mocked operator raising the exception directly (see `120-10-SUMMARY.md` "Issues Encountered" for full detail). Recorded here, per this plan's carried-forward-findings instruction, and **not** fixed — repairing it would touch `_probe_port` (ring-fenced version-capture path) and/or `_run_state_machine`'s except clause, both outside every task list in this phase. |
| `dev test --submit` repo target | n/a (host-only tooling) | Already fixed pre-phase, at commit `e615b4c` on this branch / `2b9e8dd` on `beta` — see §5 | Verified, not re-fixed, by this plan (Task 2): `submit.SUBMIT_REPO == "henols/firestarter_prom"` re-confirmed; one new repo-target-specific negative-argv test added (`test_submit_via_gh_argv_targets_the_project_wide_tracker`); `firestarter/submit.py` byte-unchanged. |

**How many existing test expectations moved: zero.** Re-verified this sweep, not merely trusted
from Plan 120-03's own SUMMARY: `git diff --stat 9ead17f..HEAD -- tests/test_serial_comm.py`
shows **105 insertions, 0 deletions** — the D-09 INFO-promotion tests are additions-only. Plan
120-03's own module comment (line 569 area) records that a suite-wide search for level/record-
count assertions on the `SerialComm`/RURP logger found zero hits before this phase, so no
existing case needed to move; this sweep re-confirmed the diff shape rather than trusting that
claim. Across the whole phase's production-code diff (`git diff --stat 9ead17f..HEAD --
firestarter/` inside `firestarter_app`): **750 insertions, 2 deletions** — the two deleted lines
are call-site rewrites adding a keyword argument (`build_flags(..., skip_erase=skip_erase)` →
threading the new keyword-only parameter through), not a behaviour change to any pre-existing
call. That held across the whole phase, and no expectation is named here as having moved for a
reason other than that one, because there is no other one.

**The deliberate `write`-path divergence, restated so it is not read as a no-op:** `write` on the
41-chip capability-refused `0x0D` subset now behaves differently from `3.0.0b11` by design (D-04
auto-set, row 3 above). This is the phase's one intentional default-behaviour change on a command
that existed before this phase; every other row is either a wholly new surface (`dev sdp`,
`--skip-sdp-unlock`) or a visibility change with no serial byte-stream difference (D-09).

---

## 3. The frozen-artifact identity story

`git -C /workspaces/firestarter status --porcelain` is **empty**, and the tip is **`0048b3d`**,
unchanged from Phase 119's own sweep HEAD. This is the honest, **non-vacuous** proof — restating
PROJECT.md FOURTH CORRECTION item 5's warning: a path-scoped `git diff -- <path>` can pass
vacuously against a path this phase never touches or that does not exist under the name a plan
assumes (the `flash_utils.{h,cpp}` trap named there). An empty `status --porcelain` subsumes
every path in the tree and cannot pass vacuously — there is no path it fails to check.

Re-confirmed this sweep:
```
$ git -C /workspaces/firestarter status --porcelain
(empty)
$ git -C /workspaces/firestarter rev-parse --short HEAD
0048b3d
$ grep -n VERSION /workspaces/firestarter/include/version.h
#define VERSION "3.0.0b11"
```

The app-repo fences, also re-run this sweep:
```
$ cd /workspaces/firestarter_app && git diff --stat -- firestarter/data/ firestarter/messages.py tools/build_db.py tools/catalog/
(empty)
```
The shipped chip database, the generated catalog mirror, and `build_db.py` are all untouched;
no `support_status` value changed (re-confirmed by `check_dispatch.py`'s own count, §4 row 9:
746 scanned, 736 supported, 10 confirmed non-dispatchable — identical class counts to prior
phases' sweeps).

**Row 5's generator was actually re-run, not merely assumed idempotent:**
`python3 tools/gen_sdp_bus_config.py` was executed in this sweep, and
`git -C /workspaces/firestarter status --short` was checked **afterward** — empty, proving
idempotence rather than a bare successful exit code.

**The retired `_shared/sdp_expected.h` whole-file blob-SHA shorthand (retired by Phase 119, §3 of
`119-NONREGRESSION.md`) was not reached for in this sweep.** This phase touches no firmware file
at all, so the whole-file-identity question for that file does not even arise here; the correct
proof for a host-only phase is the firmware-tree-wide empty `status --porcelain` above, and that
is what this document uses.

---

## 4. The nine-row gate table, re-run at this plan's final commit

**Why this check exists.** Phase 117 broke four host-side gates that scan firmware source text
while shipping a commit claiming zero `firestarter_app` files changed (PROJECT.md FOURTH
CORRECTION item 4). Every phase from 118 on must re-run this checklist explicitly. Phase 120 is
host-only, but two of its plans (120-08, 120-09) edit `cli_handlers.py` — one of the exact files
row 9's gate scans — so this table is not a formality here either.

All nine rows re-run from `/workspaces/firestarter_app`, at this plan's final commit (Task 2's
commit `96e0622`, immediately before this document and the meta docs commit land):

| # | Gate | Command | Verdict |
|---|------|---------|---------|
| 1 | `tools/check_no_log_in_sdp_window.py` (HIGH-risk row) | `python3 tools/check_no_log_in_sdp_window.py` | **PASS** — `PASS: no logging call in SDP timing window (…/eeprom_28c.cpp, emitter lines 298-314, completion-poll lines 348-361)`, exit 0. Unchanged from Phase 119's sweep since this phase touches no firmware. |
| 2 | `tests/test_check_no_log_in_sdp_window.py` | `python3 -m pytest tests/test_check_no_log_in_sdp_window.py -q` | **PASS** — 7 passed |
| 3 | `tests/test_sdp_table_parity.py` (broken 3× by Phase 117) | `python3 -m pytest tests/test_sdp_table_parity.py -q` | **PASS** — 5 passed |
| 4 | `tools/check_is_memory_cmd_no_ifdef.py` + its pytest | `python3 tools/check_is_memory_cmd_no_ifdef.py` then `python3 -m pytest tests/test_check_is_memory_cmd_no_ifdef.py -q` | **PASS** — `PASS: is_memory_cmd() has no preprocessor conditional and enumerates exactly the eight expected commands (…/firestarter.h, predicate body lines 109-123)`, exit 0; 6 passed |
| 5 | `tools/gen_sdp_bus_config.py` generator idempotence | `python3 tools/gen_sdp_bus_config.py` then `git -C /workspaces/firestarter status --short` | **PASS** — `OK: wrote …/_shared/sdp_bus_config.h`; firmware status **empty** afterward, re-run and re-confirmed in this sweep, not assumed |
| 6 | `tests/test_sdp_bus_config_drift.py` | `python3 -m pytest tests/test_sdp_bus_config_drift.py -q` | **PASS** — 4 passed |
| 7 | `tests/test_revision_constants_parity.py` | `python3 -m pytest tests/test_revision_constants_parity.py -q` | **CHANGED BY DESIGN — 13 passed, not the prior 6.** This row is rebuilt, not merely re-run: Plan 120-07 replaced the prior 8-hardcoded-`FLAG_*`-literal, non-exhaustive gate with a real two-way header-parsing gate (`test_every_firmware_cmd_define_maps_two_way_to_constants_py`, `test_every_firmware_flag_define_maps_two_way_to_constants_py`, `test_every_firmware_cmd_has_a_command_names_entry`, `test_conditionally_compiled_defines_are_exactly_the_dev_tools_pair`) plus four planted-violation legs (`test_planted_value_drift_is_detected`, `test_planted_host_missing_define_is_detected`, `test_planted_firmware_missing_flag_is_detected`, `test_missing_command_names_entry_is_detected`) and a fail-closed leg (`test_gate_fails_closed_on_an_unreadable_header_path`), alongside the pre-existing `CTRL_*`/revision-byte/frame-max/size-max legs. "Unchanged" would be the wrong verdict for this row in this phase; **CHANGED** is recorded honestly, as this plan's own prohibitions require. |
| 8 | `tests/test_dispatch_mirror.py` | `python3 -m pytest tests/test_dispatch_mirror.py -q` | **PASS** — 2 passed |
| 9 | `tools/check_dispatch.py` + `tools/check_devtest_orchestrator.py` + its pytest | `python3 tools/check_dispatch.py` then `python3 tools/check_devtest_orchestrator.py` then `python3 -m pytest tests/test_check_devtest_orchestrator.py -q` | **PASS — the one host-side row genuinely at risk this phase, and it held.** `check_dispatch.py`: `PASS: all 746 chips scanned; 736 supported; 10 chips confirmed non-dispatchable; 0 dispatch regressions; 0 consistency violations`, exit 0 (identical class counts to Phase 119's sweep — DB untouched). `check_devtest_orchestrator.py`: `PASS: scanned ../firestarter/chip_test.py, ../firestarter/cli_handlers.py, ../firestarter/submit.py; 0 VPP-set, 0 raw-wire-dict, 0 --force; firmware untouched (host-only, asserted)`, exit 0 — this is the gate that scans `cli_handlers.py`, which Plans 120-08 and 120-09 both edited (adding `dev sdp` and `--skip-sdp-unlock`), and it stayed green; 14 passed on its own pytest module. |

Every row re-run in this sweep, at this plan's final code commit — no row accepted on the
strength of a prior plan's SUMMARY alone. **Two caveats carried forward from Phase 119, both
still true:** row 5's `_shared/sdp_expected.h` whole-file blob-SHA shorthand stays retired (§3);
`.github/workflows/catalog-sync-check.yml` cannot go green for v1.22 catalog work because it
checks out both sub-repos at `ref: main` — expected-red-until-milestone-merge, not this phase's
damage (§5).

**This table is handed forward to Phases 121 and 122, as Phase 119 handed it to Phase 120.** Any
Phase 121 change to `cli_handlers.py`, `chip_test.py`, or `submit.py` must re-run row 9 in
particular; any change to `is_memory_cmd()` or the eight-command enumeration must re-run row 4;
any change to a `CMD_*`/`FLAG_*` value in either repo must re-run row 7's now-real gate.

**Full tooling gate, also re-run:**
- `ruff check firestarter/ tests/` → **All checks passed!** (exit 0). CI's scope is exactly
  `firestarter/ tests/`, **not** `.` — a bare `ruff check .` reports **4** pre-existing failures,
  all in `tools/` (`.github/scripts/update_version.py` — restated for pattern-matching only,
  actually `tools/catalog/codegen.py`'s import-organize warning, `tools/catalog/codegen_vectors.py`'s
  `UP031` percent-format warning, and one more `tools/` file), identical to the class Phase 119's
  own sweep recorded and unrelated to this phase's diff — a bare run would send a reader chasing
  files this phase never touched.
- `ruff format --check firestarter/ tests/` → **98 files already formatted** (exit 0).
- `python3 tools/check_mypy_watermark.py` → **`mypy errors: 1 (watermark: 35)`**, `INFO: 1 errors
  — 34 below watermark.` The reported error count is **1**, matching the pre-existing
  `firestarter/submit.py:446` assignment error. The watermark's 34 slack means a bare pass is
  **not** evidence of zero new type errors — a new error in `cli_handlers.py` or `serial_comm.py`
  (both edited by this phase) would pass this gate silently as long as the total stayed ≤ 35.
  This sweep names the actual reported count (1) rather than trusting a bare exit code.
- **Derived structural invariants cross-check:**
  `python3 -m pytest tests/test_sdp_capability.py tests/test_dev_sdp_cmd.py tests/test_write_skip_sdp_unlock.py -q`
  → **45 passed.**

---

## 5. Known-and-explained conditions — never silent

**1. `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` is
pre-existing RED and reproduced in this sweep.** Re-confirmed:
```
AssertionError: regenerated matrix drifted from golden fixture; produced 186034 bytes vs golden
184631 bytes; ... At index 1178 diff: b' ' != b'|'
```
A stale golden fixture, not this phase's regression — same failure class Phase 118's and Phase
119's own sweeps recorded (`.planning` memory `reference_audit_coverage_matrix_golden_stale.md`).
Needs a dedicated golden regen in its own plan; not chased here, and not silently tolerated
either — named explicitly, with its cause, every time.

**2. `tests/test_no_programmer_found_read`/`_erase` did NOT fail in this sweep, despite three live
boards attached.** This sweep's environment has `/dev/ttyACM0`, `/dev/ttyACM1` and `/dev/ttyUSB0`
all present (confirmed via `ls`), the exact condition that has previously defeated this test
pair's `comports=[]` monkeypatch — yet, as in Phase 118's and Phase 119's own sweeps, the pair
**passed** (`2 passed` when run in isolation, and included among the 1050 passing cases in the
full run). This is an environment-conditional characterization test, not a regression either way;
recorded by the actual observed state, not forced to match either possible outcome.

**Net, this sweep's full host run:**
`python3 -m pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` →
**1050 passed, 1 failed** (`test_audit_coverage_matrix`, condition 1 above), coverage **82.47%**
(required floor 70%, `firestarter/sdp_capability.py` itself at 97%). Neither of the two named
conditions is this phase's damage; neither is silent.

**3. `.github/workflows/catalog-sync-check.yml` stays expected-red-until-milestone-merge.**
Unchanged from Phase 119's own recorded status — it checks out both sub-repos at `ref: main`,
and v1.22 has not merged to `main` in either sub-repo. Not this phase's damage.

**4. The mypy watermark's 34-slack caveat (restated from §4).** Reported error count is **1**;
the watermark itself is 35. A bare pass on this gate is not, by itself, evidence that
`cli_handlers.py` or `serial_comm.py` — both edited by Plans 120-02/03/06/08/09/10 — gained no
new type error, only that the total stayed at or below 35. The actual count (1, unchanged from
the pre-existing `submit.py:446` baseline) is the load-bearing figure, and it is recorded here.

**5. D-13's residual host-only-CI skip gap on the rebuilt parity gate.** Restated from Plan
120-07's own SUMMARY (not re-derived fresh in this sweep, since this plan does not touch that
gate's design): the rebuilt `test_revision_constants_parity.py` runs only in the host CI job, not
in the firmware repo's own CI, so a firmware-only PR that drifts a `CMD_*`/`FLAG_*` value without
touching `firestarter_app` in the same PR would not trip this gate until the next cross-repo
sweep — an accepted, named gap, not a silent one.

**6. The `--submit` released-artifact finding (Task 2 of this plan).** `firestarter/submit.py:73`
already reads `SUBMIT_REPO = "henols/firestarter_prom"` at commit **`e615b4c`** on this branch and
`2b9e8dd` on `beta` (both confirmed present by `git branch --contains` in this sweep), pinned by
the pre-existing `tests/test_submit.py:237` assertion. **No source change was needed or made.**
The `v1.21` tag — and therefore shipped `3.0.0b11` in the wild — still carries the old
`henols/firestarter_app` target, so **the fix reaches users only at the next beta cut**, not
before; `3.0.0b11` continues to misfile until then. This plan added one repo-target-specific
negative-argv test (`test_submit_via_gh_argv_targets_the_project_wide_tracker`) proving the
`gh issue create` argv carries `--repo henols/firestarter_prom` immediately adjacent, never
`henols/firestarter_app`, with no `shell=True` escape hatch — because `gh issue create --label`
aborts before creating an issue unless the label pre-exists **and** the caller has write access,
which a community tester generally has neither of, making the negative-argv idiom the load-
bearing proof rather than a positive label assertion.

---

## 6. Validation ceiling

Quoted verbatim from `.planning/REQUIREMENTS.md` §"Validation Ceiling (stated before work
begins)":

> **Provable in software:** the emitted address/data/strobe byte-stream is correct per pinout and
> per size band; the sequence contains no logging and its host-side duration is measured;
> lock/unlock is `0x0D`-scoped and fail-closed elsewhere; the admission guard is
> `DEV_TOOLS`-invariant; the other protocol families' traces are byte-identical; the host refuses
> before opening a port.
>
> **NOT provable without an AT28C part:** that silicon actually enters or leaves the protected
> state; that `tBLC` is met *as accepted by the die*; that gh#11's symptom is gone; that the
> curated capability partition is correct per family.
>
> **Permitted claim at close:** *"The SDP lock and unlock sequences are emitted exactly as
> specified, verified byte-exact by golden register trace across all four `0x0D` pinouts, with a
> documented and measured host-side timing assumption."*
>
> **Forbidden claim:** *"SDP lock/unlock works on an AT28C256."*

**This document sits entirely on the permitted side of that line.** This phase makes **no**
affirmative silicon-validation claim. `0x0D` stays **`UNVERIFIED`** in the `PROTOCOL-LEDGER`.
**Zero** chips changed `support_status` (re-confirmed, §3 — `check_dispatch.py`'s 746/736/10
counts are unchanged from Phase 119's own sweep). The **84**-chip count is unchanged. No
`PROTOCOL-LEDGER` entry was added.

**The capability partition is now derived and reproducible — not bench-verified.** It is derived
from `infoic.xml` `<database type="INFOIC2PLUS">` `flags` bit 15 (`0x8000`, `MP_PROTECT_AFTER`) at
minipro commit `a8efaedc236c1d9718bd28299dfbb99536b010ff`, machine-checked total and stable by
`tests/test_sdp_capability.py`, and validated against three independent ground-truth probes
(8/8, 2/2, 4/4 — `120-SDP-PARTITION.md` §2). But the Validation Ceiling still lists "that the
curated capability partition is correct per family" among the things **not provable** this
milestone, and **that remains true**: bit 15 disagrees with `page_size > 1` on 12 of 84 entries
(two are the FRAM parts, correctly on the REFUSE side for an unrelated reason; the remaining
**nine** residual-risk entries are named individually, with what a contradicting bench report
would look like, in `120-WATCHLIST.md`). No AT28C part is on the bench. Nothing in this document
is evidence about AT28C silicon.

---

## 7. The safety argument

No bench byte could lock or unlock a real part in this phase. No AT28C part is on the bench, and
this phase adds **no bench work at all** — every verification in this document is a source-level
gate, a pytest run, or a git-state assertion, run from `/workspaces/firestarter_app` against the
tree, never against a serial port with a chip in the socket.

**The pre-wire refusal means no serial byte is emitted for a refused part**, proven by
`find_and_connect.assert_not_called()` in `tests/test_dev_sdp_cmd.py`'s gate-ordering and
no-port-opened legs — a mock-call assertion, not an exit code, which is the stronger of the two
possible proofs (an exit code cannot distinguish "refused before opening a port" from "opened a
port and then failed").

---

## 8. Deliberately not taken

Recorded here so the next owner **finds** these as explicit decisions, not as inherited silence.

**1. The `dev test` redesign implementation.** Operator-specified (D-20) reversal of three locked
v1.21 decisions (no-flags surface, destructive-only-for-UV-EPROMs, ask-to-submit-every-run,
`gh`-first). Only the ROADMAP/REQUIREMENTS amendment (Plan 120-11: `DEVTEST-02..06`) landed this
phase; the implementation is Phase 121's.

**2. GATE-01's AST capability gate over `sdp_capability.py`.** This phase left the module in a
shape a future AST-based gate can assert against (an import-purity leg already exists in
`tests/test_sdp_capability.py`), but the gate itself is Phase 121's.

**3. `doc/lockable-proms.md` §17's `AT28C16` correction (GATE-02).** Recorded as wrong in
`120-WATCHLIST.md` §4.1 (it lists `AT28C16` as SDP-capable; two of the three named parts are not,
per the derived partition) — the doc fix is Phase 121's.

**4. `MSG_INFO_SDP_UNLOCK_DONE_US`'s (`0x61`) honesty caveat.** `0x61` still lacks the "protection
state is not readable" caveat text that `0x60`/other ids carry; fixing it needs a catalog change
regenerating both sub-repos. Answered host-side instead, this phase, by D-10's symmetric summary
line carrying the caveat on both `enable` and `disable` regardless of the firmware string's own
wording. The catalog fix itself is deferred to Phase 121/122.

**5. `_probe_port`'s version-capture regex widening.** The host structurally cannot distinguish
firmware `3.0.0b11` from a later pre-release because the regex truncates the suffix (D-16).
Deferred: this is a ring-fenced transport path, and D-16 deliberately introduces no version floor
that would depend on fixing it.

**6. The wider CLI flag re-design** (`-f` splitting into distinct flags, `-b`'s polarity, a
project-wide `-y`). Out of scope for this phase; not raised by any HOST-01..06 requirement.

**7. The `0x0D` flag-surface honesty problem** — all 84 `0x0D` chips carry a firmware-inert
`FLAG_CAN_ERASE` regardless of whether `CMD_ERASE` is actually dispatchable for that chip (it
is not, pending DEVTEST-01's host half). Not this phase's scope; named so a future flag-surface
audit does not have to re-discover it.

**8. The `${sysenv.*}` `DEV_TOOLS` gating and `dev sdp`'s release-channel disposition** (backlog
999.15 / gh#8). `dev sdp` is a new dev-tools-adjacent command; its channel disposition under the
eventual stable/beta split is not decided by this phase.

**9. A separate always-on `COMMAND_NAMES` test independent of the rebuilt parity gate.** The
rebuilt `test_revision_constants_parity.py` (row 7, §4) already carries a `COMMAND_NAMES`-
coverage leg (`test_every_firmware_cmd_has_a_command_names_entry`); a standalone duplicate gate
was considered and declined as redundant.

**10. Decoding `infoic.xml` bits 14/15 into the DB itself** (the `page_size` phase, which would
make the SDP allow-set generated from a committed DB field rather than a static allow-list
transcribed once from `infoic.xml` at plan time). Not taken this phase; `sdp_capability.py`'s
allow-list stays a static, machine-checked-total table, and nothing reads `infoic.xml` at runtime
or in CI.

**11. Re-fixing `firestarter/submit.py`.** The operator's `--submit` repo-target ask (§5.6) was
discharged as a **verification**, not a re-implementation — the fix was already present at
`e615b4c`/`2b9e8dd`. Re-touching the file would have re-opened a claim that is already true and
risked masking the real, honest finding (released-artifact misfile, not a live source defect).

---

## Sweep summary

| Gate | Command | Result |
|---|---|---|
| Row 1 | `python3 tools/check_no_log_in_sdp_window.py` | PASS, exit 0 |
| Row 2 | `pytest tests/test_check_no_log_in_sdp_window.py -q` | 7 passed |
| Row 3 | `pytest tests/test_sdp_table_parity.py -q` | 5 passed |
| Row 4 | `check_is_memory_cmd_no_ifdef.py` + its pytest | PASS, exit 0; 6 passed |
| Row 5 | `gen_sdp_bus_config.py` + firmware status check | OK, firmware tree clean afterward (idempotent) |
| Row 6 | `pytest tests/test_sdp_bus_config_drift.py -q` | 4 passed |
| Row 7 | `pytest tests/test_revision_constants_parity.py -q` | **CHANGED BY DESIGN** — 13 passed (was 6 pre-phase) |
| Row 8 | `pytest tests/test_dispatch_mirror.py -q` | 2 passed |
| Row 9 | `check_dispatch.py` + `check_devtest_orchestrator.py` + its pytest | PASS, exit 0 both; 14 passed — the one host-side row at real risk (scans `cli_handlers.py`), held |
| Full host suite | `pytest tests/ --cov=firestarter --cov-fail-under=70` | **1050 passed, 1 failed** (pre-existing `test_audit_coverage_matrix`), coverage **82.47%** |
| Lint (CI-scoped) | `ruff check firestarter/ tests/` / `ruff format --check firestarter/ tests/` | both clean; bare `ruff check .` shows 4 pre-existing, out-of-scope `tools/` findings, not chased |
| Type gate | `python3 tools/check_mypy_watermark.py` | error count **1** (watermark 35, 34 slack) |
| Structural cross-check | `pytest tests/test_sdp_capability.py tests/test_dev_sdp_cmd.py tests/test_write_skip_sdp_unlock.py -q` | 45 passed |
| Firmware fence | `git -C /workspaces/firestarter status --porcelain` + `rev-parse --short HEAD` | empty; `0048b3d` |
| App-repo fence | `git diff --stat -- firestarter/data/ firestarter/messages.py tools/build_db.py tools/catalog/` | empty |
| `version.h` | `grep VERSION` | `3.0.0b11`, unbumped |
| `--submit` verification | `pytest tests/test_submit.py -q` + `SUBMIT_REPO` import check + `firestarter/submit.py` diff | 63 passed; `SUBMIT_REPO == "henols/firestarter_prom"`; source byte-unchanged |
| No-programmer characterization | `pytest -k no_programmer_found -v` (3 live boards attached) | 2 passed — did not reproduce, as in prior phases' sweeps |

**HOST-01 through HOST-06 all read Complete, verified in this sweep, none newly ticked by this
plan. DEVTEST-01..06 stay Pending — their host half (and the new `DEVTEST-02..06` ids) are Phase
121's, per Plan 120-11's amendment. No requirement row was touched by this plan.**
