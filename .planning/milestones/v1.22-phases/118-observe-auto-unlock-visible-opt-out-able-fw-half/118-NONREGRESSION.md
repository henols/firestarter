# Phase 118 Non-Regression Sweep — the enumerated OBS-05 exception record

**Written:** 2026-07-28 (Plan 118-06)
**Firmware phase base:** `f8d10a5` (`firestarter`) · **Host phase base:** `9dd11a9` (`firestarter_app`)
**Firmware HEAD at this sweep:** `1880054` · **Host HEAD at this sweep:** `d3f9128`

This is the single artifact a later reader should open to answer "what did Phase 118 change,
and what did it prove unchanged". It aggregates and re-derives (never merely copies) the claims
made in `118-01`..`118-05`'s SUMMARYs, executes the full three-repo non-regression sweep, and
closes **OBS-01** and **OBS-05**.

---

## 1. The OBS-05 claim, stated precisely

REQUIREMENTS.md states OBS-05 as: *"With no new flag set, `write` behaviour is byte-identical to
`3.0.0b11` apart from the corrected emitter and the added report lines."*

That claim is **two-layered**, and the two layers are asserted differently:

- **The recorded BUS stream** (the ordered `(LSB, MSB, data, /CE-pulse)` sequence the Phase-116
  recorder captures) is asserted **byte-identical** — proven below by golden blob-SHA identity
  (§3) plus Plan 118-05's `test_case10_flag_absent_emits_full_unlock_stream`, which drives
  PRODUCTION `eeprom28c_write_init` and asserts the full `SDP_FIXED_DIP28_28C256` stream.
- **The serial channel** carries a **named, enumerated exception** — the two new report frames
  this phase exists to add. The word "byte-identical" does **not** stand unqualified anywhere in
  this document; every use of it below is scoped explicitly to the bus stream.

This is the reasoning D-07 required and Plan 118-05's frame-enumeration case
(`test_case12_flag_absent_emits_exactly_two_report_frames`) machine-checks: golden identity plus
flash delta plus prose alone would have left the frame *count* unverified. This document cites
that case rather than re-running it — Plan 118-05 already ran and committed it (`de12c79`), and
this sweep's own Leg 1 (`pio test -e native`, 112/112) re-confirms it still passes today.

---

## 2. The enumerated serial-channel exception — the whole list, in one table

| Id | Hex | Path | Condition |
|----|-----|------|-----------|
| `MSG_INFO_SDP_UNLOCK` | `0x5E` | flag-absent (default) path | Unconditional, emitted **before** the unlock sequence |
| `MSG_INFO_SDP_UNLOCK_DONE_US` | `0x5F` | flag-absent (default) path | Unconditional, emitted **after** the sequence; carries the `micros()`-measured emit duration |
| `MSG_WARN_SDP_UNLOCK_SKIPPED` | `0x86` | `FLAG_SKIP_SDP_UNLOCK` (`0x100`) path only | Emitted **in place of** the pair above — never in addition to |
| `MSG_WARN_SDP_TBLC_EXCEEDED` | `0x87` | flag-absent path only | Only when the measured emit duration exceeds `sdp_seq_len × AT28C_TBLC_MAX_US`; expected **never** to fire on a 16 MHz AVR under the post-117 bare `set_data` loop (`pulse_delay = 0`) |

On a default write (no flag set, under-budget emit), **exactly two** frames are added to the
serial channel: `MSG_INFO_SDP_UNLOCK` then `MSG_INFO_SDP_UNLOCK_DONE_US`. The machine check for
this is `test_case12_flag_absent_emits_exactly_two_report_frames`
(`firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`, Plan 118-05, commit
`de12c79`) — it enumerates the captured frame ids on both the flag-absent path (exactly the two
INFO ids, neither WARN id) and the skip path (exactly one WARN id, neither INFO id) in the same
case.

**No general-purpose serial-frame baseline recorder was built.** Per D-07, that class of harness
work was explicitly rejected for this phase (see §8). The per-case `captured_frames` capture Plan
118-05 added inside `test_eeprom28c_sdp.cpp`'s own `setUp` (reusing `test_rurp_log_id.cpp`'s
`AlwaysDo` idiom) is a one-suite, per-case mechanism — it is not that recorder, and nothing was
added to `test/native/avr/_shared/` to support it (confirmed below, §3).

---

## 3. Why the bus stream is genuinely unchanged

Both new report lines and the WARN lines go out via `LOG_ID` / `LOG_ID_U32` / `LOG_WARN_ID` /
`LOG_WARN_ID_U32`, which call `rurp_log_id(...)` → writes to **Serial**. The Phase-116 recorder
(`HOST_STUBS_RECORD_BUS`, `test/native/avr/_shared/host_stubs_common.inc`) observes only three
strobe kinds: `rurp_write_to_register`, `rurp_write_data_buffer`, and `rurp_set_control_pin`. A
`LOG_*` call touches none of them, so it cannot append a strobe to the recorded bus stream — the
separation is structural, not incidental.

**Golden blob-SHA identity, re-derived in this sweep (not copied from Plan 118-05's SUMMARY):**

```
$ cd /workspaces/firestarter && for p in test/native/avr/_shared/sdp_expected.h test/native/avr/_shared/host_stubs_common.inc test/native/avr/_shared/sdp_bus_config.h; do echo "$p base=$(git rev-parse f8d10a5:$p) head=$(git rev-parse HEAD:$p)"; done
test/native/avr/_shared/sdp_expected.h base=b0566b80a360261cf825df5f23ecc05c7d0f885e head=b0566b80a360261cf825df5f23ecc05c7d0f885e
test/native/avr/_shared/host_stubs_common.inc base=675166d3e5383d9ca7afa7911afbaa41b93f52da head=675166d3e5383d9ca7afa7911afbaa41b93f52da
test/native/avr/_shared/sdp_bus_config.h base=e0111e6452dcb1bd8f44c5d36f3f6a67b893f4ad head=e0111e6452dcb1bd8f44c5d36f3f6a67b893f4ad
```

All three `_shared/` files are blob-SHA-identical between the phase base (`f8d10a5`) and this
sweep's `HEAD` (`1880054`). No golden was regenerated; no golden was silently re-blessed. This is
the D-07 proof this document is required to carry, re-run rather than trusted.

---

## 4. Flash and RAM

Both boards re-built and re-measured in this sweep (not copied from an earlier plan's SUMMARY),
using a throwaway `git worktree` checked out at the phase base commit `f8d10a5` so the base
figures are freshly compiled, not quoted:

| Board | Base (`f8d10a5`) | HEAD (`1880054`) | Delta |
|---|---|---|---|
| Leonardo | Flash 25528/28672 (89.0%), RAM 1998/2560 (78.0%) | Flash **25680**/28672 (89.6%), RAM 1998/2560 (78.0%) | **+152 B flash, +0 B RAM** |
| Uno | Flash 23390/32256 (72.5%), RAM 1559/2048 (76.1%) | Flash **23542**/32256 (73.0%), RAM 1559/2048 (76.1%) | **+152 B flash, +0 B RAM** |

Commands: `cd /workspaces/firestarter && pio run -e leonardo` / `pio run -e uno`, run once at
`f8d10a5` (via `git worktree add <path> f8d10a5`, then removed) and once at this sweep's `HEAD`.

**Reference point — Phase 117's measured Leonardo delta was `+204 B`** (`ada4bdc`-base, per
PROJECT.md's FOURTH CORRECTION item 3 and `117-05-SUMMARY.md`). Phase 118's **+152 B** is a
**separate, smaller, additive delta on top of Phase 117's own base** — not a continuation of the
same 204 B, and not judged against the research's predicted net saving (which CORRECTION 4 item 3
records as already contradicted by Phase 117's measurement). Both figures are now on the record
with their provenance so Phase 119's LOCK-06 headroom judgement does not have to re-measure either
one:

- Phase 117: `+204 B` Leonardo, base `ada4bdc` → HEAD of Phase 117 (`117-05-SUMMARY.md`).
- Phase 118: `+152 B` Leonardo (and `+152 B` Uno), base `f8d10a5` → HEAD of Phase 118 (this sweep,
  commit `1880054`).

This document takes no position on what LOCK-06 should conclude from either number — that
judgement belongs to Phase 119/122.

---

## 5. The CORRECTION-4 item-4 gate table

**Why this check exists.** Phase 117 shipped a commit claiming zero `firestarter_app` files
changed while four host gates that scan firmware source text were actually broken
(`test_sdp_table_parity` ×3, `test_check_no_log_in_sdp_window` ×1) — the firmware suite stayed
green throughout, and only the phase's own regression gate caught it (PROJECT.md's FOURTH
CORRECTION, item 4). PROJECT.md mandates an explicit task in every phase from 118 on checking
firmware renames/deletions against these gates. This phase's firmware edits (Plan 118-03's
constants, Plan 118-04's `eeprom28c_write_init` rebuild, Plan 118-05's new test cases) all touch
`src/proms/eeprom_28c.cpp`, the exact file these gates scan — so this table is not a formality.

All nine rows executed in this sweep, from `/workspaces/firestarter_app` unless noted:

| # | Gate | Command | Verdict |
|---|------|---------|---------|
| 1 | `tools/check_no_log_in_sdp_window.py` (rewritten by Plan 118-01 — HIGH-risk row) | `python3 tools/check_no_log_in_sdp_window.py` | **PASS** — `PASS: no logging call in SDP timing window (..., emitter lines 222-238, completion-poll lines 272-285)`, exit 0 |
| 2 | `tests/test_check_no_log_in_sdp_window.py` | `python -m pytest tests/test_check_no_log_in_sdp_window.py -q` | **PASS** — 7 passed |
| 3 | `tests/test_sdp_table_parity.py` (MEDIUM-risk row; broken 3× by Phase 117) | `python -m pytest tests/test_sdp_table_parity.py -q` | **PASS** — 4 passed |
| 4 | `tests/test_dispatch_mirror.py` | `python -m pytest tests/test_dispatch_mirror.py -q` | **PASS** — 2 passed |
| 5 | `tests/test_sdp_db_invariant.py` | `python -m pytest tests/test_sdp_db_invariant.py -q` | **PASS** — 4 passed |
| 6 | `tools/gen_sdp_bus_config.py` (generator) | `python3 tools/gen_sdp_bus_config.py` | **PASS** — `OK: wrote .../_shared/sdp_bus_config.h`; `git status --short` on that path empty afterward (idempotent, no drift) |
| 7 | `tests/test_sdp_bus_config_drift.py` | `python -m pytest tests/test_sdp_bus_config_drift.py -q` | **PASS** — 4 passed |
| 8 | `tests/test_revision_constants_parity.py` (8-literal FLAG block, non-exhaustive) | `python -m pytest tests/test_revision_constants_parity.py -q` | **PASS** — 6 passed; the firmware-only 9th flag (`FLAG_SKIP_SDP_UNLOCK`) does not trip it, confirmed by running, not assumed |
| 9 | `tools/check_dispatch.py` + `tools/build_db.py` (expected untouched by this phase) | `python3 tools/check_dispatch.py` then `python3 tools/build_db.py` | **PASS** — `check_dispatch.py`: `PASS: all 746 chips scanned; ... 0 dispatch regressions; 0 consistency violations`, exit 0. `build_db.py`: exit 0, re-fetched and regenerated `firestarter/data/chip_database.json`; `git status --short` on that path empty afterward — confirmed byte-identical, the negative proven by re-running the tool rather than assumed |

Every row PASS. No row was accepted on the strength of an earlier plan's SUMMARY alone — each
command above was re-run in this sweep.

**Avoiding the vacuous-path trap.** Every check above targets a real, existing tool or test file
(verified present before running); none is a bare `git diff -- <path>` against a path this phase
never touches. This phase's firmware diff from `f8d10a5` is exactly six paths — none of them
`src/flash_utils.h` or any other non-existent shorthand path — so the ROADMAP's
`flash_utils.{h,cpp}` vacuous-path trap named in the plan's context does not arise in this sweep.

---

## 6. Known-and-explained conditions — never silent

**1. Meta `.github/workflows/catalog-sync-check.yml` is expected-red-until-milestone-merge.**
It checks out both `firestarter` and `firestarter_app` at `ref: main` (verified at lines 33 and
40 of the workflow file, not the plan's cited 27/38 — line numbers drift as the workflow file is
edited, but the `ref: main` pinning is exactly as described), then `cmp`s all three
`messages.toml` copies byte-for-byte. Because v1.22 has not merged to `main` in either sub-repo,
this workflow compares this branch's meta catalog against the pre-v1.22 sub-repo `main` copies and
**cannot go green** until the milestone merges. This is expected, not a Phase-118 (or Phase-117 or
Phase-116) regression.

The **actual in-phase proof**, executed in this sweep and passing:
```
$ cmp tools/catalog/messages.toml firestarter/tools/catalog/messages.toml   # exit 0
$ cmp tools/catalog/messages.toml firestarter_app/tools/catalog/messages.toml  # exit 0
$ python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check   # OK: catalog valid (70 messages, version 1) — both sub-repos
```
Plus regenerate-and-`git diff --exit-code` clean for both `firestarter/include/messages.h` and
`firestarter_app/firestarter/messages.py` (§4-adjacent Leg 6 of this sweep).

**2. Two pre-existing host pytest failures — this sweep observed only ONE, and that divergence is
explained, not force-fitted.**

The plan anticipated two named pre-existing failures. This sweep's full run
(`cd /workspaces/firestarter_app && python -m pytest --tb=no`) returned:

```
1 failed, 974 passed in 35.06s
FAILED tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches
```

- **`test_audit_coverage_matrix::test_golden_file_matches`** — stale golden fixture, pre-existing
  debt unrelated to Phase 118 (confirmed unrelated in `118-01-SUMMARY.md` via stash-and-rerun
  precedent carried from Phase 117's own close). Needs a dedicated golden regen in its own plan.
  **This is the one that actually failed in this sweep**, exactly as in every prior Phase 118
  wave (118-01 through 118-05).
- **`test_no_programmer_found_read` / `test_no_programmer_found_erase`** — these did **NOT** fail
  in this run. Re-run in isolation (`pytest -k test_no_programmer_found -q`): **2 passed**. This is
  an environment-conditional characterization test pair that fails whenever a live board is
  enumerated at `/dev/ttyACM*` and defeats the test's `comports=[]` monkeypatch. **This sweep's
  environment does have live serial devices present** — `/dev/ttyACM0`, `/dev/ttyACM1`, and
  `/dev/ttyUSB0` all exist on this host at the time of this sweep — yet the pair still passed.
  So the divergence from the plan's anticipated two-failure baseline is **not** explained by
  "no board attached"; something about how these devices currently enumerate (or how pytest's
  device-discovery mocking interacts with them) does not defeat the monkeypatch in this run. The
  absence of this failure here means the runtime environment differs from what the plan author
  assumed for the *mechanism*, not that a test vanished or that this phase fixed anything — no
  code in this phase touches `test_no_programmer_found_*` or its fixtures. Both possible outcomes
  (pass or fail) are pre-existing-debt dispositions, not this phase's regression; this document
  records the actual observed state (pass, 2/2) rather than forcing the count to two.

**Net: exactly one pre-existing failure observed in this sweep (`test_audit_coverage_matrix`),
974 passed. Never silently counted as a full pass — the disposition is recorded here by name.**

**3. Python interpreter version — every Python leg in this sweep, disclosed.**

```
$ python3 --version
Python 3.12.13
$ which python3.11
(not found)
```

Both sub-repos' CI pins Python 3.11 (`firestarter/.github/workflows/build.yml:58`,
`firestarter_app/.github/workflows/ci.yml:32`). No `python3.11` binary exists in this devcontainer.
Every Python leg in this sweep — `check_no_log_in_sdp_window.py`, all six pytest gate files, the
full host suite, `ruff check`/`ruff format --check`, `codegen.py --check` and its two
regenerate-and-diff runs, `gen_sdp_bus_config.py`, `check_dispatch.py`, `build_db.py` — ran under
**Python 3.12.13**, and is recorded **CI-PENDING / structurally-green**, per this project's
established Phase-98/Phase-103 precedent. No 3.11 run was fabricated.

---

## 7. Validation ceiling

Quoted verbatim from `.planning/REQUIREMENTS.md` §"Validation Ceiling":

> **Permitted claim at close:** *"The SDP lock and unlock sequences are emitted exactly as
> specified, verified byte-exact by golden register trace across all four `0x0D` pinouts, with a
> documented and measured host-side timing assumption."*
>
> **Forbidden claim:** *"SDP lock/unlock works on an AT28C256."*

Everything measured in this document sits inside the permitted claim: the emitted register-trace
byte stream (§3), a measured host-side timing assumption via `micros()` (Plan 118-04, re-confirmed
running in this sweep's Leg 1 as `test_case11`/`test_case12`), and a source-scan proof that no
logging occurs inside the timing window (§5, row 1). Nothing in this document claims that `0x0D`
was exercised against real AT28C silicon, that the SDP sequence actually enters or leaves a
protected state on a die, or that gh#11's symptom is resolved on hardware.

`0x0D` stays **`UNVERIFIED`**. Zero chips changed `support_status`. The 84-chip count is
unchanged (this document changes no count and touches no `PROTOCOL-LEDGER`). Every assertion
above has code or a captured byte stream as its subject — a recorded register-trace strobe, a
captured serial frame's id byte, a git blob SHA, a `pio run` size-report line, a pytest exit code.
No sentence in this document is evidence about AT28C silicon state.

---

## 8. Deliberately not taken

Recorded here so the next owner **finds** these as explicit decisions, not as inherited silence.

**1. The declined recorder widening (Phase 117 D-12 / this phase's CONTEXT.md D-07's rejected
option).** Phase 117's `RED-BASELINE.md` §"Declined widening, recorded as an open hook" named
widening the trace recorder to a third strobe kind (data-bus direction:
`rurp_set_data_output`/`rurp_set_data_input`) as *"Phase 118's owner"*. **It was not taken here.**
No requirement in OBS-01..05 needed it, and taking it would have forced regeneration of
`sdp_expected.h` and `test_sdp_harness`'s reference-emitter guards — exactly the golden
regeneration §3's blob-SHA check above proves did **not** happen. Instead, Plan 118-05 built a
narrower, per-case `Serial.write` capture (`captured_frames`) scoped to `test_eeprom28c_sdp.cpp`
alone, reusing `test_rurp_log_id.cpp`'s existing `AlwaysDo` idiom — this was judged Phase-116-class
general-purpose harness work, out of this phase's scope, and the per-case capture satisfies
OBS-05's frame-count claim without it. See `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md`
§"Phase 118 observability baseline" (appended by Plan 118-05) — cited here, not duplicated — for
the full "Declined recorder widening — still NOT taken" restatement.

**2. The unchecked page-load t_BLC budget (D-10).** `eeprom28c_write_execute`'s per-byte
`set_data` loop (the page-load path) shares the **identical** `AT28C_TBLC_MAX_US` physical
constraint the SDP-disable emitter carries — and that per-byte loop is where gh#11's actual defect
lives, per Phase 117's correction (a **conflation** bug: the same read that proves write-completion
also serves, wrongly, as the data-landed proof — not a sampling-rate bug). Plan 118-03 added a
comment-only citation at that loop (`eeprom_28c.cpp`, immediately above the per-byte `for` loop),
naming the shared exposure by constant name, but the **runtime check was deliberately scoped to
the unlock only** (D-09's `sdp_tblc_budget_us` check lives solely in `eeprom28c_write_init`). A
per-byte runtime compare in that hot path would have grown the flash delta further, for a surface
OBS-01..05 does not cover. The citation is the breadcrumb: whichever future phase next revisits
gh#11 on real silicon should aim at the **conflation** Phase 117 identified, never at the sampling
rate — that framing discipline is repeated here deliberately, since PROJECT.md's own history shows
this milestone's framing went wrong twice before the conflation finding corrected it.

---

## Sweep summary

- Firmware native: **112/112**, `test_eeprom28c_sdp` **12/12**, zero `SIGABRT`/`ERRORED`/`FAILED`.
- Leonardo: Flash 25680/28672 (+152 B vs base), RAM 1998/2560 (unchanged).
- Uno: Flash 23542/32256 (+152 B vs base), RAM 1559/2048 (unchanged).
- Host pytest: **974 passed, 1 failed** (`test_audit_coverage_matrix`, pre-existing) —
  `test_no_programmer_found_*` did **not** fail this run despite live boards present (§6.2).
- Host lint: 4 pre-existing `ruff` violations, all confirmed outside this phase's diff.
- Catalog: local three-way `cmp` clean; both `codegen.py --check` gates clean; both
  regenerate-and-diff legs clean; `catalog-sync-check.yml` expected-red-until-merge.
- Three `_shared/` blob SHAs re-derived and matching the phase base.
- All nine CORRECTION-4 gate rows PASS.
- Python: 3.12.13 throughout (no 3.11 binary); CI-PENDING/structurally-green.

**OBS-01 and OBS-05 close with this document. OBS-02, OBS-03 remain Complete (set by Plan
118-05). OBS-04 remains Pending — Plan 118-07's Leonardo measurement.**
