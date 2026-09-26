# Milestone v1.41 — Project Summary: Verification Moves to the Host

**Generated:** 2026-09-25
**Purpose:** Team onboarding and project review
**Status:** CLOSED 2026-09-24 · **not shipped** — nothing from v1.41 is on any remote in any of the
three repositories. Tagged `v1.41` on the meta repository as a **bare tag** (never a GitHub Release).
**Sources:** `milestones/v1.41-{ROADMAP,REQUIREMENTS,CLOSE-RECORD,MILESTONE-AUDIT,MILESTONE-REAUDIT}.md`,
`milestones/v1.41-phases/*/` (SUMMARY, VERIFICATION, CONTEXT, RESEARCH, REVIEW, REVIEW-FIX),
`RETROSPECTIVE.md § v1.41`, `PROJECT.md`, git history of all three repositories.

---

## 1. Project Overview

**Firestarter** programs EPROM, EEPROM, Flash and SRAM/FRAM parts with an Arduino and the RURP shield.
It has two halves: a Python host CLI (`firestarter_app/`) that owns the chip database and drives every
operation over serial, and Arduino firmware (`firestarter_fw/`) that drives the bus. This meta repository
tracks both as submodules plus the GSD planning record.

**What v1.41 set out to do, in one sentence:** *the Arduino programs; the host decides whether it
worked.* Before v1.41, the firmware decided whether a chip was blank or matched an image, and
`memory_verify_execute` stopped at the first bad byte and reported one address. Meanwhile `dev test`'s
host-side `classify_fingerprint` had, since v1.21, named *why* a compare failed (blank/contact,
address-line, match, indeterminate) with total and bad counts. So `dev test` was strictly more
informative than `firestarter verify`, and AVR flash — the scarcest resource on the board — was paying
for a byte comparison the host can do for free.

**What it delivered:**

- **One streaming comparison engine on the host** (`firestarter_app/firestarter/compare.py`). `verify`,
  `blank`, `write --verify`, `erase -b` and `dev test` all use it. It compares each chunk as the read
  arrives, stops at the first mismatch by default, reports every mismatching range under `--full`,
  names a `classify_fingerprint` bucket, and exits `0` match / `1` mismatch / `2` transport or hardware
  failure.
- **A host write guard** (`write_blank_guard.py`) on exactly the five protocol families the firmware used
  to blank-check before a write, pinned by a test that fails if the set narrows **or** widens.
- **The firmware lost what the host gained:** `CMD_VERIFY` (6) and `CMD_BLANK_CHECK` (4) with their
  ordinals reserved, the write-init and erase-end pre-flight blank checks, their machinery, and the
  `FLAG_SKIP_BLANK_CHECK` (0x08) wire bit. Leonardo flash went **24134 → 23314 B (−820 B)**.
- **`dev test` on one leased serial session per plan** — measured **15.1 %** faster on real silicon
  against a threshold of 15.0 % set before the measurement, and kept.
- **Both repositories at `3.1.0b1`**, in one commit pair, with the breaking change documented on the wiki.

**What it deliberately did not remove (D-7):** verification *inside* the programming algorithms. The
per-pulse verify in the EPROM program loop, `memory_verify_execute` (called for
`VERIFY_PER_PULSE_PLUS_FINAL` on protocols `0x07`/`0x08`), `eeprom28c_verify_page_readback`,
`flash_util_verify_operation` and `MSG_ERR_VERIFY` (0xAF) all stay. A UV program loop cannot decide
whether to pulse again without its verify. *Removing a command surface is not removing verification.*

**Headline non-claim:** *the host now decides, and no user has it yet.* `3.1.0b1` exists only at the
milestone branch tips. Shipping is `/gsd-ship`, operator-gated.

## 2. Architecture & Technical Decisions

### The ordering rule — the milestone's central safety property

The host gained each capability **one phase before** the firmware lost it. At no phase boundary is
there a window where neither side checks.

```
202  host can verify/blank by read-back   ──►  204  firmware loses CMD_VERIFY / CMD_BLANK_CHECK
203  host write guard in place             ──►  205  firmware loses the write-init / erase-end pre-flights
         (redundant with firmware for one phase — by design)
```

204 and 205 were kept as two phases, not one: 204 removed a surface nothing else called, 205 removed a
safety check other code depended on, and a bisect across a merged phase could not tell which one broke a
part.

### Key technical choices

- **Decision:** The engine lives in its own import-light module, `compare.py`.
  - **Why:** It keeps the one-way import graph between `chip_test` and `eprom_operations`.
  - **Phase:** 202 (D-01)
- **Decision:** Exactly one divergence implementation — `classify_fingerprint` delegates to
  `classify_streamed`; `_diff_offsets` is deleted.
  - **Why:** DEVTEST-03 forbids a fingerprint changing meaning. The old code, run out of git, was
    compared with the new over 2922 generated cases across all five buckets, with zero differences.
  - **Phase:** 202 (D-02/D-03)
- **Decision:** The host stops a read in flight by **withholding acks**, not by a new protocol message.
  - **Why:** No abort message exists. The firmware times out after ~1 s and its `command_done()`
    teardown runs on the error path, so the port is left clean. The first-mismatch saving is real
    *time*, not only shorter output. A four-condition check (intent flag + `MSG_ERR_TIMEOUT` inside a
    bounded 3.0 s window) keeps the host's own abort from being mistaken for a fault.
  - **Phase:** 202 (D-06/D-07/D-08), written up in `202-READ-ABORT-ANSWER.md`
- **Decision:** Exit codes `0`/`1`/`2`, as in `diff`/`cmp`, for `verify`, `blank`, `erase -b` and
  `write --verify`. Plain `write` keeps `0`/`1`.
  - **Why:** A transport fault must never read as a chip verdict.
  - **Phase:** 202 (D-10/D-11), 203 (D-13, operator `confirm-d13`), 205 (D-02)
- **Decision:** The write guard covers an **explicit set** of protocol families — `0x06`, `0x07`,
  `0x08`, `0x0B`, `0x10` — not a `FLAG_CAN_ERASE` test. `0x05`, `0x0D` and SRAM/FRAM are named
  exemptions with the reasoning at the exemption site.
  - **Why:** That is what the firmware checked. A flag-only rule would suddenly refuse writes on `0x05`
    and all SRAM/FRAM parts, which the firmware never checked.
  - **Phase:** 203 (D-01/D-02, amended WRITE-02)
- **Decision:** The guard reads only the write's own region, fails closed on an unclassifiable part, and
  sits inside `EpromOperator.write_eprom` so every caller inherits it.
  - **Why:** After 205 the host guard is the *whole* safety net against half-programming a non-blank UV
    part. No second line of defence exists.
  - **Phase:** 203 (D-04/D-05/D-07/D-08)
- **Decision:** The erase exemption is **address-aware** for protocol `0x06`: a write at a non-zero
  address falls back to a region blank check.
  - **Why:** Code review found CR-01 — the firmware erases nothing at a non-zero address on `0x06`, so
    the exemption let an irreversible silent overwrite through on 190 of 190 shipped `0x06` rows. Fixed
    in-phase rather than accepted, because it had no safe failure mode.
  - **Phase:** 205 (D-G2, plan 205-08, `205-CR-01-DECISION.md`)
- **Decision:** Clean protocol break — ordinals 4 and 6 are retired outright and recorded as reserved at
  the gap on both command ladders. No new catalog message; an old host gets `Unknown command: N`.
  - **Why:** A deprecation window keeps the flash that is being reclaimed. A new host is safe against old
    firmware without a version gate, because it only sends `CMD_READ`.
  - **Phase:** activation (D-4), 204 (D-01/D-02/D-05)
- **Decision:** `dev test` host-path reports carry an empty-default `cmp=host` tag on
  `dedup_fingerprint`.
  - **Why:** Keeps new-mechanism reports apart from firmware-path ones without re-keying any already
    filed report. All 19 frozen literals are unmoved.
  - **Phase:** 206 (D-03)
- **Decision:** One leased serial link per `dev test` plan (`EpromOperator.lease()`), default off, one
  call site, one revertible commit (`3853b55`). A `SerialError` drops the held link and the next step
  cold-connects.
  - **Why:** Seed R4 — a guard read, a write and a `--verify` were three separate port opens. Kept only
    because it cleared a pre-registered threshold.
  - **Phase:** 206 (D-05/D-06/D-07)

## 3. Phases Delivered

| Phase | Name | Repo | Bench | Plans | Status | One-liner |
|-------|------|------|-------|-------|--------|-----------|
| 202 | One comparison engine, on the host | app | no | 5 | ✅ passed 8/8 | `compare.py`; `verify`/`blank` read and compare on the host; read-abort answered in writing |
| 203 | The write guard moves up a layer | app | no | 4 | ✅ passed 5/5 | Host guard on five families, pinned both ways; opt-in `write --verify` with `--full` |
| 204 | The command surfaces leave the firmware | both | yes | 5 | ✅ passed 6/6 SC, 8/8 req | Ordinals 6 and 4 retired; in-algorithm verifies pinned by tests; both skew directions on silicon |
| 205 | The pre-flights leave the firmware | both | yes | 8 | ✅ passed 9/9 (after gap closure) | Pre-flights + `FLAG_SKIP_BLANK_CHECK` gone; −496 B flash per AVR target; CR-01 fixed in phase |
| 206 | `dev test` keeps its fidelity, on one session | app | yes | 4 | ✅ passed 10/10 | `cmp=host` discriminator; verdict 2 → SKIPPED+ERROR; lease kept at a measured 15.1 % |
| 207 | The version and the record | both | no | 3 | ✅ passed 4/4 | `3.1.0b1` in both repos; wiki Breaking-Changes + new Writing-and-Verifying page live |
| 207.1 | Address v1.41 tech debt (INSERTED) | both | no | 7 | ✅ passed 22/22 | 26 audit items + 202 WR-02: 14 fixed, 11 accepted, 2 closed on evidence |

**Totals:** 7 phases, 36 plans, 95 tasks. Every phase has a verified `SECURITY.md` with
`threats_open: 0`.

### What each phase did, briefly

- **202** — `verify_eprom` rewritten onto `COMMAND_READ`; memory bound proven with a tracemalloc ceiling
  (peak 776 B – 17,597 B at 512 KiB, flat from 128 KiB); an AST test pins the equality fast path (a
  naive per-byte loop takes ~20 s on 512 KB); `blank` joined the engine against constant `0xFF`; both
  commands gained `-a`/`-s`/`--full`, with region refusals before the port opens. `blank` on SRAM/FRAM is
  now an exit-2 refusal.
- **203** — the guard, its pinning test (perturbation-proven: removing `0x0B` → 1 failure, adding `0x0D`
  → 4), `-b` / `--skip-erase` / `--force` semantics (`--skip-erase` re-arms the guard on an erasable
  part), the host half of the negative-start-address fix, `write --verify`, and hand-edited `--help`
  snapshots.
- **204** — ordinal 6 removed first as a tracer, with ordinal 4 still live as the control; then ordinal 4
  across 11 firmware sites. Two new proof instruments: a brace-matching source contract that fails if the
  `VERIFY_PER_PULSE_PLUS_FINAL` call disappears (RED reproduced), and a native suite
  `test_verify_error_ids` asserting which id each in-algorithm verify raises. Four-role bench matrix; three
  whole-device reads share one SHA-256.
- **205** — `erase -b` rebuilt on the host first; four call sites and five symbols deleted; `0x08`
  retired from both ladders as a commit pair; a firmware `json_parser.c` rule that refuses a negative
  `address` (+22 B); flash/RAM measured per target; bench legs B0–B7; then CR-01's gap closure.
- **206** — research found the routing was already done in 202, so the phase became a verdict-vocabulary
  job: a compare that did not complete now lands on `SKIPPED` + `ERROR` (never `BAD`, which would blame
  the chip for a cable fault); additive `compare_evidence` outside the hash; `setup_command` extracted;
  the lease; the bench measurement.
- **207** — merged `origin/beta` into both sub-repo branches **before** the bump (D-01, so a ship-time
  conflict cannot publish `3.0.0b51` and burn a PyPI version), bumped to `3.1.0b1` in a single-file
  commit pair (fw `a55f2d8` / app `67f93e2`), and pushed the wiki after an operator checkpoint.
- **207.1** — dispositioned every close-audit item: write-path diagnostics that no longer invent a byte,
  read-abort window boundary tests, an `is_connected()` assert in `setup_command`, three owed
  `SECURITY.md` files, record corrections, and a closing ledger (`207.1-LEDGER.md`).

## 4. Requirements Coverage

**34/34 Complete.** None dropped, none deferred. REQUIREMENTS.md checkboxes, the traceability table and
the phase VERIFICATION.md files agree.

| Group | IDs | Phase | Status |
|---|---|---|---|
| CMP — one comparison engine | CMP-01…08 | 202 | ✅ 8/8 |
| WRITE — host write guard | WRITE-01…06 | 203 | ✅ 6/6 |
| FWCMD — command surfaces leave | FWCMD-01…06 | 204 | ✅ 6/6 |
| FWBLANK — pre-flights leave | FWBLANK-01…05 | 205 | ✅ 5/5 |
| DEVTEST — fidelity kept | DEVTEST-01…03 | 206 | ✅ 3/3 |
| SESS — one leased session | SESS-01…02 | 206 | ✅ 2/2 |
| REL — version, compatibility, record | REL-02, REL-03 | 204 | ✅ (bench-proven) |
| | REL-01, REL-04 | 207 | ✅ |

**Three requirements were amended by measurement during the milestone.** Each amendment names its
decision and quotes the text it replaced:

- ⚠️→✅ **CMP-04** (D-13): the default report prints a `start–end` range with a byte count and **no byte
  values**; it previously asked for the expected and actual byte.
- ⚠️→✅ **WRITE-02** (D-01/D-02): an explicit five-family set pinned both ways, instead of a
  `FLAG_CAN_ERASE` exemption pinned only against widening.
- ⚠️→✅ **FWCMD-05** (D-03): pins the id each verify *actually* raises — 0xAF for `memory_verify_execute`
  and `eeprom28c_verify_page_readback`, 0xBD/0xBE for the per-pulse budget exits, 0xB7 for
  `flash_util_verify_operation` (a DQ7 poll that can never raise 0xAF). The original would have been a
  false pin.

**Audit verdict:** close audit + three re-audits; final status `tech_debt` with no blocker. 34/34
requirements, 7/7 phases, 9/9 integration seams wired, 7/7 flows complete. **Closeout type:
`override_closeout`** — not because of any requirement, but because `init.manager` reads every phase
digest as `stale` (the known `covered_digest` mechanism, accepted as 207.1 D-19) and because three
207.1 review warnings were open at close (all fixed the same day — see § 6).

**Future requirements (tracked, not in v1.41):** **CMP-F1** a clean protocol-level stop for a read in
flight (offered at 204 and declined, D-12 — forward-compatible whenever it lands); **CMP-F2** reach or
retire `classify_fingerprint`'s dead `transport` bucket; **PROTO-F1** replace the jsmn/JSON command layer
with binary frames.

## 5. Key Decisions Log

**Activation decisions (operator, 2026-09-20):**

| ID | Decision | Rationale |
|---|---|---|
| D-1 | Both halves: command surfaces **and** in-algorithm pre-flight blank checks leave the firmware | Retires `mem_util_blank_check_region` five weeks after Phase 201 made it; the gate belongs a layer up, which Phase 201's own review (WR-02) pointed to |
| D-2 | Host pre-write check is exempt where an erase actually ran | Only UV parts pay the read; the host check becomes the whole safety net, so its reasoning sits at the exemption site and a test pins it |
| D-3 | `write --verify` is opt-in | Default write time is unchanged |
| D-4 | Clean break: ordinals 4 and 6 retired, not deprecated | Keeping them keeps the flash; a new host only sends `CMD_READ` |
| D-5 | `3.1.0b1` in both repos | Minor bump in the beta series; stable stays operator-gated |
| D-6 | Seed R4 rides along: one leased session per `dev test` plan | This milestone tripled the port opens per write |
| D-7 | Removing a command surface is not removing verification | The UV program loop needs its per-pulse verify |

**Phase decisions (selected):**

| Phase | ID | Decision | Rationale |
|---|---|---|---|
| 202 | D-06/07/08 | Abort by withholding acks; four-condition discrimination | No abort message; `command_done()` leaves the port clean |
| 202 | D-12 | `blank` on SRAM/FRAM → exit-2 refusal | "Not blank" would be a false chip verdict |
| 202 | D-16/17 | `--full` retains ≤ 64 ranges but counts stay exact; conflicting regions refused before the port opens | Bounded memory without lying about totals |
| 203 | D-03 | `--skip-erase` re-arms the guard on an erasable part | The "erase guarantees blank" premise is then false |
| 203 | D-05 | An unclassifiable part is guarded (fail closed) | The guard becomes the only safety net |
| 203 | D-13 | `--verify` exit codes resolved by cause: 0 landed+matched, 1 something decided to stop, 2 something failed | Operator `confirm-d13`; a CLI contract is one-way |
| 204 | D-01 | Remove every site, not just the three named | A minimal removal would force `#define CMD_BLANK_CHECK 4` to stay |
| 204 | D-04 | Proof method follows the claim: existence by source contract, behaviour by native test | No test asserted 0xAF before this phase |
| 204 | D-12 | `DONE`-based clean stop declined (stays CMP-F1) | Firmware half is one line; host half reworks the surface 202 just built |
| 205 | D-04 | `0x08` fully retired; no firmware-version gate | Accepted cost: a post-205 CLI on pre-205 firmware gets `write -b` refused |
| 205 | D-08 | `MSG_ERR_NOT_BLANK` (0xB0) stays in the catalog | The host still receives it from pre-3.1.0 firmware |
| 205 | D-G2 | `0x06` exemption becomes address-aware | CR-01 — no safe failure mode |
| 206 | D-01 | Verdict 2 → `SKIPPED` + `ERROR`, not `BAD`, not a sixth verdict | Don't blame the chip for a cable fault |
| 206 | D-05 | Only `EpromOperator` is leased; `HardwareManager` connects stay | Caps the saving at ~60 % of theoretical — stated before the bench |
| 206 | D-07 | Pre-registered keep/revert: ≥ 15.0 %, > 5× spread, zero verdict divergence | A narrow result means something only if the threshold came first |
| 207 | D-01 | Merge `origin/beta` before the bump | Avoid publishing a stale auto-bumped version at ship |
| 207 | F4 | Wiki headings use the product version, never `v1.41` | `v1.41` parses as PEP 440 `1.41` |
| 207.1 | D-03 | `run_count=1` on a raised step kept as accepted debt | Changing it would re-key filed reports |
| 207.1 | D-19 | Stale verification digests accepted | The `verification fingerprint` verb can fabricate digests; green gate is the mitigation |

## 6. Tech Debt & Deferred Items

### Fixed after the close (2026-09-24, same day)

All three 207.1 code-review warnings were fixed by `/gsd-code-review 207.1 --fix`:

- **WR-02** (`firestarter_app` `8596992`) — a real edge-case defect from Phase 206: the lease's input
  drain ran *outside* the `SerialError` handler, so a mid-run USB unplug left a dead link leased and the
  rest of a `dev test` plan was SKIPPED instead of reconnecting. Now covered by a test.
- **WR-01** (`82bba7a`) — the D-03 comment named one of the two routes to `runs=1`.
- **WR-03** (`11c9a8c`) — `update_version.py --set-version` silently made a stable patch bump on a
  non-beta ref. **The todo stays pending**: the code is fixed, but `update_version.py` still has no
  automated test and sits outside every CI gate.

Also settled after the close: Nyquist validation kept on (`49bc5971`), unrelated working-tree edits
committed or ignored (`edf2d427`), and the operator ruled that the milestone branch's committed version
wins every merge conflict.

### Still open

- **207.1 info findings IN-01…IN-06** (style, duplicated boundary tests, no direct test of the refusal
  message, an unhelpful "read 0 of N" message, a hard-coded issue count, `update_version.py` hygiene).
- **206 IN-01** stale docstring detail; **205 IN-01** a stale "premise expires in Phase 205" comment at
  `eprom_operations.py` near the `region-end` key.
- **Orphaned catalog ids:** `DBG_VERIFY_PROM`, `DBG_BLANK_CHECK_PROM`, 0x08, 0x0B, 0x2E — kept and
  annotated. `MSG_ERR_NOT_BLANK` (0xB0) can go only when pre-3.1.0 firmware support ends.
- **Pending todos from this milestone:** `preflight-firmware-version-compat-guard`,
  `blank-check-sram-fram-shortcircuit-is-inert`, `update-version-set-version-ignores-beta-mode` (test
  owed), `platformio-leonardo-buffer-comment-is-stale`.
- **Open artifacts:** 91 disclosed at close, 0 suppressed, none originating in v1.41 except the three
  todos filed there. Treat 91 as a floor.

### Accepted risks and coverage gaps (named, not closed)

- **The host guard is the whole safety net** against half-programming a non-blank UV part. Its pinning
  test is its only drift detector.
- **Version skew:** a **pre-3.1.0 CLI on 3.1.0b1 firmware** lets a write to a non-blank UV EPROM through,
  because neither side checks; its `erase -b` also silently stops checking. An old CLI's bare `fw` will
  recommend 3.1.0b1. **Rule: upgrade the CLI first, then the firmware.** A post-205 CLI on pre-205
  firmware gets `write -b` refused (T-205-10 / T-205-16, both high, operator "Accept all open").
- **Bench coverage is one rig:** every hardware result is a Leonardo + Rev 2.0 shield + one W27C512. No
  Uno-class board ran the 512-byte chunk path; no Intel or NOR flash part ran 205's removals; an erasable
  part stood in for a true UV part. Accepted as 207.1 D-18.
- **The 15.1 % is one rig, one part, one session**, and it cleared its threshold by 0.1 point. The named
  follow-up is to fold the voltage-sampler connects into one monitor read.
- **Nyquist validation is partial:** 202, 204, 207.1 compliant; 203 partial; 205, 206 not validated; 207
  has no VALIDATION.md.
- **Chip-ID probe read `0x1818` instead of `0xda08`** on that rig during 204/205; closed on evidence
  (operator-confirmed part, `0xDA08` on all six 206 runs, probable VPP-monitor routing), not by a fix.

### Deferred to future work

CMP-F1 (clean mid-read stop), CMP-F2 (dead `transport` bucket), PROTO-F1 (binary command frames),
CLI-wide exit-code consistency, collapsing `erase -b`'s second port open, taking the `dev test` verify
fingerprint from the verify's own compare, a configurable read-abort window, and teaching
`devtest-triage` that `Unknown command: 6/4` means a version mismatch.

### Lessons from the retrospective

- **Gain the capability, then remove the alternative — one phase apart.**
- **Pre-register a numeric keep/revert threshold and rehearse the revert before measuring.**
- **Pin a guarded set in both directions**; a narrowed safety set is the worse failure.
- **An exemption is sound only where its premise physically holds** — `FLAG_CAN_ERASE` says a part *can*
  be erased, not that an erase ran under the bytes about to be written.
- **Both Criticals (203 CR-01, 205 CR-01) were found by code review, not planning.**
- **A lesson written in a retrospective is not a process change.** Unfiled review findings recurred
  verbatim from v1.40; it needs a step in the close path.
- **Security records should be written at each phase close,** not collected by an inserted phase.

## 7. Getting Started

- **Branches:** all three repositories are on `v1.41-verification-to-host`. Never commit to `beta` or
  `main` directly — a push to `beta` in a sub-repo **publishes** (GitHub pre-release, and PyPI for the
  app). See root `CLAUDE.md` § Milestone close and branch protection.
- **Run the CLI:** `pip install -e '.[test]'` in `firestarter_app/`, then the `firestarter` console
  script (`python -m firestarter` does not work — there is no `__main__.py`). Try
  `firestarter verify <chip> <file> [--full] [-a ADDR -s SIZE]`, `firestarter blank <chip>`,
  `firestarter write <chip> <file> --verify`.
- **Tests:**
  - App: run on **Python 3.11** (`.venv311`) — the devcontainer's 3.12 masks CI-only failures.
    `pytest` → 2373 passed, 86.40 % coverage (floor 70); `ruff check` and `ruff format --check`.
  - Firmware: `pio test -e native` and `-e native_nodevtools` (244/244 each); `pytest tests/` (316).
  - Messages: `tools/catalog/` codegen in the meta repo only — never edit `messages.h` / `messages.py`
    in a sub-repo.
- **Where to look first:**
  - `firestarter_app/firestarter/compare.py` — the engine (`CompareAccumulator`, `CompareResult`,
    `classify_streamed`, `render_compare_lines`).
  - `firestarter_app/firestarter/eprom_operations.py` — `verify_eprom`, `check_eprom_blank`,
    `_drive_region_compare`, `_main_phase_read_data(abort_predicate=…)`, `write_eprom`, `lease()`.
  - `firestarter_app/firestarter/write_blank_guard.py` — the guarded set and its exemptions; read with
    `tests/test_write_blank_guard_pinning.py`.
  - `firestarter_app/firestarter/chip_test.py` — `dev test`, `classify_fingerprint`, `cmp=host`.
  - `firestarter_fw/src/firestarter.cpp` and `include/firestarter.h` — the command ladder with the
    reserved gaps at 4 and 6; `src/proms/eprom.cpp` — the surviving `memory_verify_execute` call.
  - `firestarter_fw/tests/test_verify_survival_source_contract.py` and
    `test/native/avr/test_verify_error_ids/` — the proof that in-algorithm verification survived.
- **Key records:** `milestones/v1.41-CLOSE-RECORD.md` (the full close), `202-READ-ABORT-ANSWER.md`,
  `204-BENCH-MATRIX.md`, `205-FLASH-RAM.md`, `205-CR-01-DECISION.md`, `206-SESSION-COST.md`,
  `207.1-LEDGER.md`; user-facing docs are the wiki pages *Breaking-Changes* (3.1.0b1) and
  *Writing-and-Verifying*.
- **Next steps:** `/gsd-ship` (operator-gated). Before it, rebuild local `beta` from `origin/beta`,
  advance the gitlinks after any further sub-repo commit, and resolve the predicted conflicts (meta
  `REQUIREMENTS.md` / `STATE.md`, app `__init__.py`) in favour of the milestone branch. Merge with merge
  commits, not squashes. Then `/gsd-new-milestone`; phases continue at **208**.

---

## Stats

- **Timeline:** 2026-09-20 (activation, after the `v1.40` tag) → 2026-09-24 (close, tag `v1.41`) —
  5 days; post-close fixes the same day.
- **Phases:** 7 / 7 complete (36 plans, 95 tasks)
- **Commits:** meta 240 (`v1.40..v1.41`) + 4 after the tag; `firestarter_app` 70 ahead of `origin/beta`
  (69 non-merge); `firestarter_fw` 18 ahead (17 non-merge)
- **Files changed:**
  - meta: 186 files (+51,027 / −253) — almost entirely the `.planning/` record
  - `firestarter_app`: 42 files (+11,305 / −831)
  - `firestarter_fw`: 40 files (+2,061 / −1,432)
- **Firmware image:** leonardo 24134 → 23314 B (−820 B); Phase 205 alone −496 B flash / −4 B RAM on
  uno, uno328pb and leonardo
- **Test suites at close:** app 2373 passed (86.40 % coverage); fw native 244/244 ×2; fw `tests/` 316
- **Bench sessions:** 4, all on one Leonardo + Rev 2.0 shield + W27C512
- **Contributors:** Henrik Olsson
