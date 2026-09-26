---
phase: 151
slug: protection-readability-lock-status
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-20
---

# Phase 151 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `151-RESEARCH.md` §"Validation Architecture" (commit `567169fd`).
> **Dual-repo phase** — two frameworks, two sampling regimes.

---

## Test Infrastructure

| Property | Host (`firestarter_app/`) | Firmware (`firestarter/`) |
|----------|---------------------------|---------------------------|
| **Framework** | pytest 8+ (`syrupy>=5.0`, `pytest-cov>=7.1.0`) | PlatformIO + Unity (native); pytest for `scripts/` checkers |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (`:105-107`) — `testpaths=["tests"]`, `addopts="-ra -q"` | `platformio.ini` (`test_filter` per env); firmware `tests/` has no separate pytest config |
| **Quick run command** | `python3 -m pytest tests/test_<module>.py -x -o addopts=""` | `python3 -m pytest tests/test_check_size_baseline.py -x` |
| **Full suite command** | `python3 -m pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` | `pio test -e native && pio test -e native_nodevtools && pio test -e native_pinmap_provisional` |
| **Install** | `pip install -e '.[test]'` — **never `.[dev]`** (C-15: `dev` is `pytest>=7.0` only and cannot run the gates) | PlatformIO toolchain already present |
| **Estimated runtime** | ~90 s full host suite | ~60 s native; +cold AVR build ~3 min/env |

**Traps that invalidate a green run:**

- Devcontainer python is **3.12**; CI is **3.11 only**. A pass here is not a pass there.
- `addopts` already carries `-q` — doubling it hides the count line. Use `-o addopts=""` when you need the count.
- ArduinoFake macro-redefinition **warning watermark is 1166 with zero headroom**.
- `-D DEV_TOOLS` lives in the shared `[env]` block (`platformio.ini:26`) and is inherited by **all three** AVR targets. There is no free `#ifdef`.

---

## Sampling Rate

- **After every task commit (host):** the one or two suites the task touches — `python3 -m pytest tests/test_<module>.py -x -o addopts=""`
- **After every task commit (firmware):** `pio test -e native -f "*<suite>*"`, plus `python3 -m pytest tests/test_check_size_baseline.py -x` on **any** task that changes firmware bytes
- **After every plan wave (host):** `python3 -m pytest tests/ -o addopts="-ra"`, then `ruff check firestarter/ tests/` + `ruff format --check firestarter/ tests/` + `python tools/check_mypy_watermark.py`
- **After every plan wave (firmware):** all three native envs, plus a **cold** `rm -rf .pio/build/<env>` + `pio run -e <env>` per AVR env on the wave that lands firmware bytes
- **Before `/gsd-verify-work`:** host suite green at `--cov-fail-under=70`; `check_size_baseline.py --policy merge05` exit 0 on all three AVR targets with the decomposition visible in the PASS line; `check_build_warnings.py` OK (AVR `== 0`, native `<= 1166`)
- **Max feedback latency:** 90 s host / 60 s firmware-native

**Codegen path:** if `messages.toml` is edited, the app's CI drift gate (`git diff --exit-code firestarter/messages.py`) is the automated proof the regen ran. **The firmware side has no equivalent drift gate**, so `include/messages.h` must be regenerated and committed in the same change.

---

## Per-Requirement Verification Map

Task IDs are assigned at planning time; this map is the requirement-level contract each task must inherit.

| Req | Behavior to prove | Test Type | Automated Command | File Exists | Status |
|-----|-------------------|-----------|-------------------|-------------|--------|
| LOCK-01 | Curated table's binding cannot be widened into inference (literal-only, bound once, no mutation) | source-scan AST gate, subprocess-driven | `pytest tests/test_check_<table>_invariants.py -x -o addopts=""` | ❌ W0 — model on `tests/test_check_sdp_capability.py` (9 legs) | ⬜ pending |
| LOCK-01 | Every readable-verdict row carries a `lockable-proms.md` **and** datasheet citation | unit over module AST/comments | same suite, dedicated leg | ❌ W0 | ⬜ pending |
| LOCK-01 | Every curated token maps to a family row that exists in `doc/lockable-proms.md` | invariant-over-doc (126 rows) | `pytest tests/test_<table>_citations.py -x` | ❌ W0 — precedent `tests/test_lockable_proms_doc_claims.py` | ⬜ pending |
| LOCK-02 | Host builds the right wire frame and parses the response | unit, frame-level, no serial | `pytest tests/test_<lockstatus>_wire.py -x` | ❌ W0 | ⬜ pending |
| LOCK-02 | `CMD_*` ↔ `COMMAND_*` parity + `COMMAND_NAMES` key | existing bidirectional parity gate | `pytest tests/test_revision_constants_parity.py -x` | ✅ — **fails OPEN without the sibling repo** | ⬜ pending |
| LOCK-02 | `is_memory_cmd()` admits exactly the intended set over `[0,255]`, in **both** DEV_TOOLS states | firmware-native truth table | `pio test -e native -f "*test_cmd_admission*"` **and** `pio test -e native_nodevtools -f "*test_cmd_admission*"` | ✅ `test_cmd_admission.cpp:66` — literal set `{1,2,3,4,5,6,9,10}` must change | ⬜ pending |
| LOCK-02 | `_EXPECTED_CMD_NAMES` deliberately updated, not drifted | host source-scan gate | `pytest tests/test_check_is_memory_cmd_no_ifdef.py -x` | ✅ | ⬜ pending |
| LOCK-02 | Provisional-pinmap refusal still covers every memory command | firmware-native | `pio test -e native_pinmap_provisional` | ✅ — **runs in NO CI leg (C-12)** | ⬜ pending |
| LOCK-02 | Firmware flash **and RAM** growth inside the newly-extended MERGE-05 allowance; tripwire still fires one byte past | firmware pytest over cold build logs | `pytest tests/test_check_size_baseline.py -x` then `python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log …` | ✅ 14 legs — **8 redden** | ⬜ pending |
| LOCK-03 | Any non-`documented-readable` alias ⇒ refusal **naming that alias and its state** | unit, table-driven | `pytest tests/test_<table>_resolution.py -x` | ❌ W0 | ⬜ pending |
| LOCK-03 | `W29C020,W29C020C,W29C022` refuses naming **`W29C022`** specifically (D-06's own acceptance condition) | unit, one named leg | same suite | ❌ W0 | ⬜ pending |
| LOCK-03 | `W29C040,W29C042` refusal handles a **set** of offending aliases in **different** states (C-6) | unit, one named leg | same suite | ❌ W0 | ⬜ pending |
| LOCK-03 | Pre-command firmware ⇒ `firmware_outdated`, keyed on `MSG_ERR_UNKNOWN_CMD` **id**, with a negative control on a different id | unit, mock-free | `pytest tests/test_sdp_honesty.py -x` | ✅ `:125-150` — **extend, never rewrite** | ⬜ pending |
| LOCK-03 | The `not_readable` caveat is **composed**, never re-authored | unit substring assertion | `pytest tests/test_sdp_honesty.py tests/test_chip_test_sdp_leg.py -k caveat -x` | ✅ — **7 pinning sites + 2 production surfaces (C-4)** | ⬜ pending |
| LOCK-04 | **All 746 DB entries resolve to exactly one of the 8 classes** | invariant-over-DB — **the D-12 test** | `pytest tests/test_<lockstatus>_class_partition.py -x` | ❌ W0 | ⬜ pending |
| LOCK-04 | `protected`/`unprotected` **structurally unreachable** without a silicon read | AST/structural gate + **planted** fixture | same suite | ❌ W0 | ⬜ pending |
| LOCK-04 | Class token **and** exit code asserted together, per class | CLI-surface matrix | `pytest tests/test_<lockstatus>_cli.py -x` | ❌ W0 | ⬜ pending |
| LOCK-04 | `dev lock-status` absent on a simulated stable build, refuses informatively | CLI-surface, real child process | `pytest tests/test_dev_group_channel_gating.py -x` | ✅ — `_GATED_NAMES` 6→7 | ⬜ pending |
| LOCK-04 | `BETA_ONLY_DEV_COMMANDS` deliberately extended | unit exact-tuple | `pytest tests/test_dev_tools_channel_gate.py -x` | ✅ — 6-tuple → 7-tuple at `:150-158` | ⬜ pending |
| LOCK-04 | `dev --help` renders the new command, nothing else changed | syrupy snapshot | `pytest tests/test_characterization.py -k help_dev -x` (regen `--snapshot-update`) | ✅ — snapshot `.ambr:124-150` | ⬜ pending |
| DATA-06 | Doc figures equal the DB (70/746; alg 5 → 27/27; alg 13 → 43; 148/746; 27/77/43/1; 744 of 746 carry the fields) | invariant-over-DB, doc-parsing | `pytest tests/test_<data06>_doc_measurements.py -x` | ❌ W0 — model on `test_b15_page_size_corroboration.py` | ⬜ pending |
| DATA-06 | **No runtime consumer exists** in `firestarter/` | source-scan **test** (not a `tools/check_*`, per D-16) | same suite | ❌ W0 | ⬜ pending |
| DATA-06 | Documented **once**: one authoritative statement, two one-line pointers | doc-parsing unit over three files | same suite | ❌ W0 | ⬜ pending |
| DATA-06 | `sdp_capability.py` untouched; Class 2(b) gate not weakened | untouched-guard + existing gate | `pytest tests/test_check_sdp_capability.py -x` | ✅ gate exists; guard shape at `test_b15_page_size_corroboration.py:246` | ⬜ pending |

---

## Wave 0 Requirements

- [ ] `firestarter_app/firestarter/<protection_table>.py` — the LOCK-01 module (new)
- [ ] `firestarter_app/tools/check_<protection_table>_invariants.py` — LOCK-01's AST gate (new)
- [ ] `firestarter_app/tests/test_check_<protection_table>.py` — subprocess-driven pairing, ≥1 planted fixture per violation class (new)
- [ ] `firestarter_app/tests/fixtures/planted_<table>_permit_by_default.py` and `…_widenable.py` — real planted violations (new)
- [ ] `firestarter_app/tests/test_<lockstatus>_class_partition.py` — **the D-12 invariant** (new)
- [ ] `firestarter_app/tests/test_<lockstatus>_resolution.py` — three-state unanimity + the `W29C022` named leg (new)
- [ ] `firestarter_app/tests/test_<lockstatus>_cli.py` — class-token ⊗ exit-code matrix, `--force` path (new)
- [ ] `firestarter_app/tests/test_<lockstatus>_wire.py` — frame build + response parse (new)
- [ ] `firestarter_app/tests/test_<data06>_doc_measurements.py` — DATA-06's measured proof + consumer-absence (new)
- [ ] **Re-derived** planted fixtures for the moved MERGE-05 band, on a **NEW** family (e.g. `*_v151*`) — four tripwire legs + four clean-control legs. **Never** by editing the `fullflash` family in place.
- [ ] **Re-captured** `captured_build_*` and `captured_test_native*_summary` fixtures from the post-151 cold build
- [ ] Snapshot regeneration for `test_help_dev`
- [ ] Framework install: **none needed** — pytest 8 + syrupy + PlatformIO all present

---

## The D-12 Invariant — Required Assertion Set

The load-bearing test. Drive the **resolution function** `(entry, display_name) -> (class_token, reason)` over every row of the committed `chip_database.json`. Assert on **class tokens**, never on message text.

1. **Exhaustiveness** — all 746 rows resolve into the frozen 8-token set. **Non-vacuous from the first commit:** `XICOR/X88C64P,X88C64S` (`algorithm: 52`) lands in **no** class under D-09's literal enumeration, so this leg is **red today**. Acceptance must read *"seen red on the `0x34` row, then seen green after the class is assigned"* — never *"leg exists"*.
2. **Disjointness / determinism** — exactly one token per row, stable across two calls (the function is pure).
3. **Per-class census pinned as literals** — `not_implemented` = 39 (`0x10`); `no_mechanism` = 405 (`0x07`+`0x08`+`0x0B`+`0x0E`+`0x27`+`0x28`+`0x29`); `not_readable` ⊇ 84 (`0x0D`); the 217 `0x05`+`0x06` rows distributed across readable-derived / `not_readable` / `undocumented_alias`. Pin as literals so a new DB row breaks it — the style `test_sdp_db_invariant.py` uses for `43`/`41`/`84`.
4. **Structural unreachability of `protected`/`unprotected`** — the pure function's signature does not accept a device response, so both tokens are producible only by a second, response-consuming function. AST leg asserts the literals do not appear as return values in the pure module. **Requires a planted fixture that *does* return `"unprotected"` from the pure path**, asserted to fail — without it the leg is decorative.
5. **Citation presence** — every `documented-readable` token has a citation comment, and the cited `lockable-proms.md` row string is actually present in that file.
6. **Robustness** — the two TI rows lacking `protect_on_after`/`protect_off_before` must not raise; the 10 rows with `support_status != "supported"` must still resolve; a **synthetic** row with a novel algorithm must make the exhaustiveness leg **raise, naming the row** (control copied from `test_partition_flags_a_moved_chip_via_db_field_non_vacuous`).

**Not a phase-local checker.** D-12 rules it out and the reason is measured: `check_permitted_claims.py`'s `_HERE` resolves to the *checking* phase's directory, so cross-phase reuse scans nothing and exits 0.

---

## Manual-Only Verifications

Four bench legs, **asymmetric**. Chip handling is operator-only; driving the port is permitted.

| Leg | Behavior | Part | Req | Why Manual | Instructions |
|-----|----------|------|-----|------------|--------------|
| **A** | Product-ID mode entry/exit works — a genuine positive control on `AA/55/90` → read → `AA/55/F0` | `W29C020` | LOCK-02 | Needs silicon | **Available today, zero new code.** `firestarter id W29C020` must return **`0xDA45`** via `CMD_CHECK_CHIP_ID` → `flash_5v_page.cpp:54-57` → `flash_utils.cpp:82-87`. Not gated by D-03, D-06 or D-07. |
| **B** | The `0x05` status read on the documented-readable part | `W29C020` | LOCK-02 | Needs silicon | `dev lock-status W29C020 --force`. `--force` is required **even on the operator's own part** — `W29C022` is undocumented, so D-06's unanimity refuses the entry regardless. A **PROBE**. Record the raw result either way. |
| **C** | The original D-03 leg | `W29C040` | LOCK-03 | Needs silicon | Same `--force` path. A **PROBE**, explicitly capped by D-03. |
| **D** | The `0x06` Autoselect read | — | LOCK-02 | **No bench leg exists** | Not run. `lock-status` on a `0x06` part ships **software-proven and unrun on silicon** and must say so in those words. |

**What leg B establishes, decomposed:**

| Sub-claim | On silicon? | Oracle |
|-----------|-------------|--------|
| (i) Product-ID mode entry/exit works | **YES** | chip-ID reads back `0xDA45` — available via leg A |
| (ii) the status **address** is right | **no** | no ground truth for what is at that address |
| (iii) the `FF`/`FE` **decode** is right | **no** | requires independently knowing the part's true lock state |
| (iv) the boot block **is** locked | **no, not without self-contradiction** | only independent oracle is write→verify — destructive, **and** the *indirect* method `lockable-proms.md:3` excludes from "readable" |

---

## Unsatisfiable Criteria — Do Not Author These

1. **"The sequence is correct."** `infoic.xml` is closed as a source (`config` is the literal `"NULL"` on all 101 `0x05` and all 897 `0x06` entries). Both sequences are **datasheet-derived**, so the strongest available test is a pinned byte table + a `vendor / document / revision / page / §section` citation — **a change detector, not a correctness proof.** The plan must say so in those words.
2. **"The `0x05` read returns the correct status."** Unsatisfiable within D-03. The satisfiable form: *"the probe was run and its raw result recorded, either way, with no validation claim attached."*
3. **"Fixtures byte-unchanged" / "tests byte-unchanged."** Scope to *assertions-unchanged*, or name blob SHAs. The `260820-a7w` and `149-07` severances are the in-tree record of why.
4. **"Parity gate green"** — `test_revision_constants_parity.py` **fails OPEN** without the sibling repo. Non-vacuous form names `commits_land_in:` and requires the gate observed **not** skipped (via `-rs`, or `tests/fw_presence.py`'s `FW_ROOT` resolving).
5. **"CI green" for the pinmap refusal** — `test_pinmap_provisional` runs in **no CI leg**. Must name the local `pio test -e native_pinmap_provisional` invocation.
6. **"CI green" for DATA-06** — a markdown-only commit fires **no** host CI (`paths-ignore: ['**.md']`). DATA-06's proof must be a **Python test**, which is not markdown, so it actually runs.
7. **Any claim of AT28C or `0x0D` silicon validation** — the milestone Evidence Ceiling, unchanged.
8. **Closure of the v1.17 W29C040 RCA** — that RCA asked for a second **W29C040**; a `W29C020` is a different part. The payoff is **partially** reachable, not delivered.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 90 s
- [ ] Every acceptance criterion checked against §"Unsatisfiable Criteria"
- [ ] D-12's leg 1 acceptance phrased as red-then-green, not "leg exists"
- [ ] D-12's leg 4 has a planted fixture, not a bare absence assertion
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
