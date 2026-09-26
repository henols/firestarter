# Phase 134: The Plan-Derived SDP Oracle in `dev test` — Research

**Researched:** 2026-08-04
**Domain:** Host-only Python (`firestarter_app/`) — test-plan engine, report surface, CLI exit contract
**Confidence:** HIGH (every claim below is either MEASURED against the working tree at
`firestarter_app@57e8eb5` or explicitly marked INFERRED)

**Measurement basis for this whole document:**
`firestarter_app` branch `gsd/v1.30-sdp-surface-retirement` @ **`57e8eb5`** [MEASURED:
`git rev-parse --abbrev-ref HEAD` + `git log --oneline -3`]. Working tree clean of source
modifications (`git status --short` shows only untracked `.coverage`, `.planning/config.json`,
`SECURITY.md`, `write_test_port.sh`, and a modified `.gitignore` — **no tracked source file is
dirty**). Meta repo on `gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof`.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

CONTEXT.md carries **19 locked decisions (D-01…D-19)** plus four measured corrections. This research
does **not** re-derive them and proposes **no alternative to any locked D-NN**. They are the input,
not the subject. Read `134-CONTEXT.md` in full — it is not summarised here, because paraphrasing a
locked decision is how a planner ends up planning against the paraphrase.

### Locked Decisions — index only (authoritative text is CONTEXT.md `<decisions>`)

| ID | One-line | This research's status |
|----|----------|------------------------|
| Correction 1 | `0x86` ack UNOBSERVABLE from `chip_test.py` | **CONFIRMED** — §2.7 |
| Correction 2 | The leg is **SIX** steps, not four | CONFIRMED as consistent; §3 |
| Correction 3 | Exit precedence inverted (`max(1,2)=2`, marginal beats BAD) | **CONFIRMED** — §2.5 |
| Correction 4 | `MIN_CHECKED_SOURCE_FILES` is a FLOOR; adding files is safe | **CONFIRMED** — §5 |
| D-01 | `write_eprom` bool is a PRECONDITION signal, never the verdict | CONFIRMED implementable — §2.7 |
| D-02 | `(False, B)` ⇒ marginal, not BAD | no new finding |
| D-03 | Polarity proof is the full 2×2 cross product | no new finding |
| D-04 | Degenerate read-back: LENGTH ⇒ BAD, CONTENT ⇒ marginal | **CONFIRMED** — §2.2 |
| D-05 | Non-laundering is a TEST; `B`'s `ff_ratio ≈ 0.004` | **CONFIRMED exactly** — §2.1 |
| D-06 | SIX steps; criterion 1's "four" corrected in the record | — |
| D-07 | Two baseline ops, not one; `reason` is console-invisible | **CONFIRMED** — §2.4 |
| D-08 | `_baseline_closes_sdp_gate` in `run_plan`, mirroring `_id_step_closes_gate` | **OQ-1** — §4.1 |
| D-09 | `_ALWAYS_WRITES_NOTICE` stays static; count pinned by a DERIVED test | **⚠ NEW TRAP** — §4.5 |
| D-10 | Named three-valued STRING field, `SCHEMA_VERSION` 1.2→1.3, never a boolean | **⚠ NEW TRAP** — §4.4 |
| D-11 | `dedup_fingerprint` reset for all 43 ALLOW chips ACCEPTED as a cost | CONFIRMED — §2.4 |
| D-12 | Two recovery forms; a line prints on the happy path | no new finding |
| D-13 | LEG-14's gate is a SCOPED pytest over named constants, not a whole-report grep | CONFIRMED — §2.4 |
| D-14 | Fix exit precedence so BAD outranks marginal | **audit DISCHARGED** — §4.6 |
| D-15 | NOT-RUN oracle keeps `SKIPPED` + exit FLOOR of 2 | **CONFIRMED** — §2.6, §4.6 |
| D-16 | gh#20 finding recorded here; public reply is Phase 137's | **triage input MEASURED** — §4.8 |
| D-17 | All six laundering routes tested; R1/R2 synthetic + labelled unreachable | **CONFIRMED** — §2.3 |
| D-18 | SDP leg gated on `write_execute`; all six to `locked_destructive` on `"none"` | CONFIRMED — §2.6 |
| D-19 | Own named generator for `B`; lint-style test that it is not `generate_pattern` | **CONFIRMED** — §2.1 |

### Claude's Discretion (per CONTEXT.md)
D-18 and D-19 only. Both are grounded in this session's measurements and are treated as locked here.

### Deferred Ideas (OUT OF SCOPE — do not plan)
`tools/check_*.py` string-literal scanner (Phase 137 CLOSE-03) · the gh#20 public reply (Phase 137
CLOSE-06) · the underlying AT28C256 write failure (backlog item with a named owner) · the
`dedup_fingerprint` discontinuity's outward description (Phase 137 CLOSE-05) · `write --sdp-relock`
(Backlog 999.28) · ratcheting the mypy watermark · adding this phase's test modules to the mypy
strict island · 133 D-07's forfeited report on Ctrl-C · refreshing `.planning/codebase/TESTING.md` ·
the four pre-existing `ruff` failures in `tools/`.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

**Fourteen, and only fourteen.** LEG-09/10/11/15 are already `[x]` from Phase 133 — do not re-tick or
re-evidence them. (LEG-15's *gate file* must nonetheless be **edited** in this phase — see §4.2 —
without the requirement being re-ticked.)

| ID | Description (abridged from REQUIREMENTS.md) | Research support |
|----|---------------------------------------------|------------------|
| LEG-01 | `dev test` derives the SDP leg from `sdp_capability()`, no new CLI option | §2.3, §2.6 — `derive_plan` signature + `sdp_capability(chip, db)` at `sdp_capability.py:266` |
| LEG-02 | REFUSED chips get NA/SKIPPED steps carrying the refusal reason | §2.6 — `run_plan:877-879` NA path needs **zero** new machinery |
| LEG-03 | Inhibited payload from its own named generator, bitwise complement, differs in **every** byte, neither all-`0x00` nor all-`0xFF` | §2.1 — all five assertions MEASURED true for the real region |
| LEG-04 | Baseline proves a write **transition** (B, verify, A, verify) before any lock | §2.1, §2.4 |
| LEG-05 | Oracle is read-back equality; a merely-failed write is never evidence | §2.2, §2.7 |
| LEG-06 | Write succeeding after the lock ⇒ **BAD**, exit **1** | §2.5 — **unreachable until D-14 lands**; §4.6 |
| LEG-07 | Partial read-back change ⇒ BAD (gh#11) | §2.2 |
| LEG-08 | Degenerate read-back ⇒ BAD or marginal, never equality | §2.2 — P-02 trap MEASURED live |
| LEG-12 | `HELD`/`NOT-HELD`/`NOT-RUN(reason)` in **both** surfaces | §2.4, §4.4 — **inversion-guard constraint** |
| LEG-13 | NA/SKIPPED oracle **drops** the N-of-M ratio | §2.6 — MEASURED: needs a **pinning test only**, no counting logic |
| LEG-14 | "rewrite", never "erase", enforced by a committed grep | §2.4, §4.7 |
| LEG-16 | Committed no-op-write fixture makes the baseline step BAD | §2.1, §3 |
| LEG-17 | Six laundering routes, each asserting `sdp_lock` not called + visible `NOT-RUN` | §2.3, §4.6 |
| LEG-18 | gh#20 triaged against the baseline gate, finding recorded | §4.8 — **live issue body captured** |
</phase_requirements>

---

## Summary

CONTEXT.md did the design work. This research did the **measurement** work, and it found five things
a planner could not have known from the record, three of which will turn the suite RED the moment
the first line of the phase lands:

1. **The op-registration parity gate (`tests/test_op_registration_parity.py`) fires at COLLECTION
   time.** A bare module-level `assert len(_ALL_OPS) == 9` at `:150` — not inside any test — means
   the instant the first new `OP_*` constant is added to `chip_test.py`, all seven tests in that
   module become **collection errors**. CONTEXT.md described this file as needing "five Phase-134
   exemption rows discharged and `_DECLARED_REGISTRY_COUNT` re-asserted". Both details are
   measured-wrong: there is **no symbol named `_DECLARED_REGISTRY_COUNT`**, and only **two** rows are
   dischargeable. The real work is six distinct edits (§4.2).

2. **The parity gate's *inversion guard* structurally constrains D-10 and D-09.**
   `DiagnosticReport` and `_ALWAYS_WRITES_NOTICE` are both declared **non-registries** whose
   zero-op-vocabulary claim is **re-measured by AST every run**. So D-10's `HELD`/`NOT-HELD`/`NOT-RUN`
   value may **not** be derived inside `DiagnosticReport` by comparing op strings, and D-09's
   rewritten notice may **not** contain any hyphenated op literal. Both would fail
   `test_non_registry_still_has_no_ops` with the message *"PROMOTE it to `_POLICED_REGISTRIES`, do
   not loosen this guard."* (§4.4, §4.5)

3. **D-14's blocking audit is DISCHARGED, and the answer is clean.** CONTEXT.md required auditing
   *"every existing test asserting exit 2 on a mixed run"* before changing the exit precedence. I ran
   the actual candidate and measured its verdict set: `test_marginal_disagreement_exits_2` produces
   `[NA, OK, OK, marginal, OK, OK]` — **no BAD anywhere**. There are **zero** existing tests asserting
   exit 2 on a mixed BAD+marginal run. D-14 can land with no test-audit blast radius. (§4.6)

4. **P-01's trap and D-05's arithmetic are both exactly as CONTEXT.md measured them** — verified
   independently: `A = generate_pattern(0,256) = bytes(range(256))`, `B = ~A`, `A≠B`, they differ at
   **all 256** bytes, neither is all-`0x00`/all-`0xFF`, and `B.ff_ratio = 0.00390625` against
   `_FF_RATIO_THRESHOLD = 0.98`. And P-02's trap reproduces live: `classify_fingerprint(A, b"")`
   returns `total=0, bad=0` — an empty read-back reads as **perfect equality**. (§2.1, §2.2)

5. **The anchor drift is small but real: four drifted anchors and one non-existent symbol.**
   `chip_test.py` and `cli_handlers.py` are anchor-perfect (32 of 32 and 11 of 11). The drift is
   concentrated in `constants.py` (+5 on two rows) and `diagnostic_report.py` (`to_dict` is at
   `:436`, not `:444`). (§1)

**Primary recommendation:** Plan `chip_test.py` as a **strictly serial spine** (worktree isolation is
unavailable in the submodule, and every one of LEG-01…08/16 lands in that one file), and make the
**very first plan** in that spine carry the `test_op_registration_parity.py` updates *in the same
commits* — because the collection-time assert means there is no green intermediate state between
"added `OP_WRITE_BASELINE_B`" and "updated the gate".

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Plan derivation (which steps exist, ALLOW vs REFUSE) | Engine (`chip_test.py::derive_plan`) | — | `derive_plan` is the single decision locus (SC4, D-02 precedent); `sdp_capability()` is injected, not re-implemented |
| Pattern A / pattern B generation | Engine (`chip_test.py`) | — | Module constants, never DB fields — the `_WRITE_REGION_LENGTH` precedent |
| The oracle truth table | Engine (`chip_test.py`, a new single-run dispatch fn) | — | P-07: `chip_test.py` is scanned in full; `cli_handlers.py` helpers sit behind a fail-open allow-list |
| The baseline gate | Engine (`run_plan`) | — | Mirrors `_id_step_closes_gate`; `run_plan` is the only place gate flags live |
| Cleanup/unlock guarantee | Engine (`run_plan`'s `finally`) | — | Phase 133 D-06, already built |
| `HELD`/`NOT-HELD`/`NOT-RUN` **derivation** | Engine (`chip_test.py`, new pure fn) | — | **Forced by the inversion guard** (§4.4) — must NOT be derived inside `DiagnosticReport` |
| `HELD`/… **carriage + serialisation** | Report (`diagnostic_report.py`) | — | A plain assigned `str` field; generic, no op comparison |
| Exit code composition | CLI (`cli_handlers.py`) | — | `sys.exit` lives only here; strict mypy island |
| Recovery wording + notice | CLI (`cli_handlers.py` module constants) | `sdp_honesty.py` (call, don't re-author) | D-12/D-13; `sdp_honesty` is Phase 132's forward contract |
| Wire flag (`FLAG_SKIP_SDP_UNLOCK`) | Engine call site → ring-fenced `eprom_operations.py` | — | `write_eprom` already accepts `operation_flags`; zero edits inside the ring-fence |

---

# §1 — CORRECTED ANCHOR TABLE

> CONTEXT.md instructs: *"Re-measure every number at plan time (Phase 132 D-11's discipline — 133's
> anchors drifted twice)."* This is that re-measurement. Every row below was produced by
> `grep -n '<anchor-regex>' <file>` against the working tree at `57e8eb5`.
> **✓ = matches CONTEXT.md · ✗ = DRIFTED · ＋ = not in CONTEXT.md, added here because the phase needs it.**

## 1.1 `firestarter/chip_test.py` — **1544 lines** ✓ (CONTEXT.md: 1544)

**32 of 32 CONTEXT.md anchors are EXACT. Zero drift in this file.**

| Symbol | CONTEXT.md | MEASURED | |
|--------|-----------|----------|---|
| `address_fold_byte` | `:53` | `:53` | ✓ |
| `generate_pattern` | `:64` | `:64` | ✓ |
| `prepass_images` | `:75` | `:75` | ✓ |
| `_diff_offsets` | `:98` | `:98` | ✓ |
| `_FF_RATIO_THRESHOLD` | `:127` | `:127` | ✓ |
| `classify_fingerprint` | `:143` | `:143` | ✓ |
| op constants (7 shipped) | `:294-300` | `:294-300` | ✓ |
| `OP_SDP_LOCK`/`OP_SDP_UNLOCK` | `:309-310` | `:309-310` | ✓ |
| `class Step` | `:314` | `:314` (`@dataclass` at `:313`) | ✓ |
| `class Plan` | `:343` | `:343` (`@dataclass` at `:342`) | ✓ |
| `derive_plan` | `:409-596` | `:409-596` | ✓ |
| `_top_anchored_or_default` | `:599` | `:599` | ✓ |
| `_DESTRUCTIVE_OPS` | `:663` | `:663` | ✓ |
| `_MULTI_RUN_OPS` | `:690` | `:690` | ✓ |
| `_SDP_OPS` | `:703` | `:703` | ✓ |
| `_DESTRUCTIVE_GATE_REASON` | `:705` | `:705-707` | ✓ |
| `class StepResult` | `:711` | `:711` | ✓ |
| `_skip_result` | `:734` | `:734` | ✓ |
| `_resolve_or_none` | `:738` | `:738` | ✓ |
| `run_plan` | `:773-972` | `:773`, body ends `:971` | ✓ |
| `_id_step_closes_gate` | `:974` | `:974` | ✓ |
| `_WRITE_REGION_LENGTH` | `:994` | `:994` | ✓ |
| `_UV_WRITE_REGION_LENGTH` | `:1000` | `:1000` | ✓ |
| `_write_region_for` | `:1009` | `:1009` | ✓ |
| `_run_step` | `:1040` | `:1040` | ✓ |
| `_dispatch_step` | `:1118` | `:1118` | ✓ |
| `_dispatch_multi_run` | `:1277` | `:1277` | ✓ |
| `_dispatch_multi_run` terminal `AssertionError` | `:1368` | `:1368` | ✓ |
| `_dispatch_sdp` | `:1423` | `:1423` | ✓ |
| `_RAN_VERDICTS` | `:1500` | `:1500` | ✓ |
| `count_applicable` | `:1520` | `:1520` | ✓ |

**Anchors this phase needs that CONTEXT.md does not list:**

| Symbol | MEASURED | Why the planner needs it | |
|--------|----------|--------------------------|---|
| `from firestarter.constants import FLAG_CAN_ERASE` | `:37` | The exact import line to extend with `FLAG_SKIP_SDP_UNLOCK` (FEATURES §1.4) | ＋ |
| `FP_BLANK_CONTACT`…`FP_INDETERMINATE` | `:119-122` | D-04's content-degeneracy targets | ＋ |
| `class Fingerprint` | `:133` (`@dataclass` `:132`) | Oracle return payload | ＋ |
| `is_uv_eprom` | `:378` | ALLOW chips are non-UV; D-18 | ＋ |
| `_WRITE_SCOPE_*` / `_WRITE_SCOPES` | `:403-406` | D-18's `write_execute` gate at `:463` | ＋ |
| `write_execute = write_scope in (...)` | `:463` | **The exact line D-18 keys on** | ＋ |
| `VERDICT_OK/BAD/NA/SKIPPED/MARGINAL` | `:635-639` | Truth-table vocabulary | ＋ |
| `_UNLOCK_CLEANUP_SWALLOWED` | `:770` | The drain's narrow except tuple | ＋ |
| `destructive_gate_closed = False` | `:854` | **Where `_baseline_closes_sdp_gate`'s flag is initialised** (D-08) | ＋ |
| `cleanup: list[Callable[[], None]] = []` | `:869` | The registry (Phase 133 D-06) | ＋ |
| the step loop's NA arm | `:877-879` | LEG-02 needs zero new machinery | ＋ |
| the destructive-gate arm | `:881-883` | **Where the baseline gate's guard clause goes** | ＋ |
| the lock→cleanup registration block | `:890-918` | **Where the double-fire de-registration goes** (OQ-2) | ＋ |
| `if step.op == OP_ID: destructive_gate_closed = ...` | `:920-921` | **Structural template for the baseline gate's set** | ＋ |
| the `finally` drain loop | `:967-971` | LEG-10's already-built mechanism | ＋ |
| `_WRITE_REGION_START` / `_DEFAULT_REGION` | `:993` / `:1006` | Region math | ＋ |
| `_dispatch_id` / `_dispatch_read` / `_sample` | `:1193` / `:1216` / `:1264` | Arm neighbours | ＋ |
| `_dispatch_step`'s `_MULTI_RUN_OPS` arm | `:1159-1162` | The arm the new leg dispatcher goes **after** | ＋ |
| `_dispatch_step`'s `_SDP_OPS` arm 5 | `:1180-1181` | Arm 5 today; the new arm becomes 6 (or joins 5) | ＋ |
| `_dispatch_step`'s terminal fail-closed `return` | `:1182-1190` | The refusal every new op must sit above | ＋ |
| `_dispatch_multi_run`'s fail-closed guard | `:1320-1330` | Guard→branch→raise template | ＋ |
| `operator.write_eprom(name, eprom_data, tmp_source_path)` | `:1352` | **The measured proof that no `operation_flags` is passed today** (FEATURES §1.4) | ＋ |
| `_dispatch_sdp` terminal `AssertionError` | `:1471` | Template for the new dispatcher's terminal raise | ＋ |
| `count_applicable`'s `M` computation | `:1536-1538` | LEG-13 — **must not be edited** (§4.4) | ＋ |

## 1.2 `firestarter/diagnostic_report.py` — **532 lines** ✓

| Symbol | CONTEXT.md | MEASURED | |
|--------|-----------|----------|---|
| `SCHEMA_VERSION = "1.2"` | `:55` | `:55` | ✓ |
| `class AutoCapture` | `:82` | `:82` | ✓ |
| `dedup_fingerprint` | `:186` | `:186` | ✓ |
| disposition/ladder constants | `:233-249` | `:233-249` | ✓ |
| `build_db_diff` | `:274` | `:274` | ✓ |
| `class DiagnosticReport` | `:318` | `:318` | ✓ |
| **`to_dict`** | **`:444`** | **`:436`** | **✗ DRIFT −8.** `:444` is the `"schema_version": SCHEMA_VERSION,` *line inside* `to_dict`. Both are useful, but a planner writing `<read_first>` against `:444` for the method definition will miss the `def`. |
| `_step_dict` | (unnumbered) | `:406` | ＋ |
| `_banner_dict` | — | `:417` | ＋ |
| `_db_diff_dict` | — | `:426` | ＋ |
| `render` | (unnumbered) | `:456` | ＋ |
| `render`'s per-step row (op/verdict/error_code/fingerprint **only**) | — | `:477-482` | ＋ **D-07's whole basis, MEASURED** |
| `render`'s banner row (`"{n} of {m} ran"`) | — | `:494-495` | ＋ LEG-13's visible surface |
| `to_json_block` | — | `:530` | ＋ |
| the `to_dict` key list (9 keys) | — | `:443-454` | ＋ D-10 adds a 10th |

## 1.3 `firestarter/cli_handlers.py` — **2219 lines** ✓ · **mypy STRICT island** ✓

**11 of 11 CONTEXT.md anchors are EXACT. Zero drift.**

| Symbol | CONTEXT.md | MEASURED | |
|--------|-----------|----------|---|
| `_VERDICT_EXIT_CODES` | `:1891` | `:1891-1897` | ✓ |
| its comment falsely claiming *"BAD beats marginal via `max`"* | `:1888-1890` | `:1888-1890` | ✓ (correction 3 confirmed) |
| `_verdict_code` | `:1900` | `:1900-1902` (`.get(verdict, 0)` at `:1902`) | ✓ |
| `_resolve_write_scope` | `:2019` | `:2019` | ✓ |
| `_ALWAYS_WRITES_NOTICE` | `:2071` | `:2071-2078` | ✓ |
| `dev_test` | `:2085` | `:2085` (decorators `:2081-2084`) | ✓ |
| docstring exit contract | `:2119-2121` | `:2119-2121` | ✓ (correction 3's second false claim) |
| `click.echo(_ALWAYS_WRITES_NOTICE)` | — | `:2123` | ＋ D-09's printed-FIRST guarantee |
| `derive_plan` call | `:2138` | `:2138` | ✓ |
| `read_hardware_revision_value` | `:2150` | `:2150` | ✓ |
| `run_plan` call | `:2164` | `:2164` | ✓ |
| `count_applicable` call | `:2166` | `:2166` | ✓ |
| `report.render(console)` | — | `:2181` | ＋ D-12's echo site neighbour |
| `json.dumps(report.to_dict(), …)` | — | `:2192` | ＋ LEG-12's JSON artifact |
| the markdown table loop | — | `:2194-2205` | ＋ `reason` reaches here (D-07) |
| exit computation | `:2216-2219` | `:2216-2219` | ✓ **`code = max(_verdict_code(r.verdict) for r in results)` at `:2218`** |

## 1.4 `firestarter/eprom_operations.py` — **1912 lines** · ⚠ **RING-FENCED, read/call only**

| Symbol | CONTEXT.md | MEASURED | |
|--------|-----------|----------|---|
| `build_flags` | — | `:173` (maps `FLAG_SKIP_SDP_UNLOCK` at `:209`) | ＋ |
| `class EpromOperator` | `:285` | `:285` | ✓ |
| `_operation_context` | `:405-416` (as "finally → `_disconnect_programmer`") | `def` at `:376`; `_disconnect_programmer` at `:413` | ✓ (range covers it) |
| `command_dict["flags"] = … \| operation_flags` | — | `:338` | ＋ **proof the flag reaches the wire** |
| `read_eprom` | `:650` | `:650` | ✓ |
| `write_eprom` | `:1583` | `:1583` | ✓ |
| `operation_flags: int = 0` (4th positional) | `:1588` | `:1588` | ✓ |
| the `0x86` ack check | `:1654-1662` | `is_protocol_0x0d` at **`:1653`**, `if` at `:1654`, **`is_ok = False` at `:1665`** | **✗ range under-shoots by 3.** Use `:1653-1665`. |
| `verify_eprom` | `:1675` | `:1675` | ✓ |
| `erase_eprom` | `:1711` | `:1711` | ✓ |
| `sdp_unlock` | `:1736` | `:1736` | ✓ |
| `sdp_lock` | `:1784` | `:1784` | ✓ |

## 1.5 `firestarter/sdp_capability.py` — **281 lines** — all ✓

`SDP_PROTOCOL_ID = 13` `:58` ✓ · `SDP_CAPABLE_TOKENS` `:70` ＋ · `REASON_*` `:180-184` ✓ ·
`split_part_number_tokens` `:187` ＋ · `sdp_capability_for_entry` `:201` ✓ ·
**`sdp_capability(chip_name, db) -> tuple[bool, str]` `:266`** ✓

## 1.6 `firestarter/sdp_honesty.py` — **92 lines** — all ✓ · mypy STRICT island

`unreadable_state_caveat()` `:33` ✓ · `emission_summary(mode, chip_name)` `:45` ✓ ·
`map_unknown_cmd_to_outdated(exc, mode, chip_name)` `:67` ✓

## 1.7 `firestarter/constants.py` — **178 lines** — ✗ **TWO DRIFTED ROWS (+5 each)**

| Symbol | CONTEXT.md | MEASURED | |
|--------|-----------|----------|---|
| `FLAG_SKIP_SDP_UNLOCK = 0x100` | `:137` | `:137` | ✓ |
| **`COMMAND_SDP_UNLOCK = 9` / `COMMAND_SDP_LOCK = 10`** | **`:72-73`** | **`:77-78`** | **✗ DRIFT +5** |
| **their `COMMAND_NAMES` entries** | **`:90-91`** | **`:95-96`** | **✗ DRIFT +5** |

## 1.8 `tests/test_op_registration_parity.py` — **822 lines** — ⚠ **the largest correction**

| Claim | CONTEXT.md | MEASURED | |
|-------|-----------|----------|---|
| Symbol to re-assert | **`_DECLARED_REGISTRY_COUNT`** | **DOES NOT EXIST.** The two real constants are `_POLICED_REGISTRY_COUNT = 6` (`:246`) and `_DECLARED_NON_REGISTRY_COUNT = 6` (`:328`) | **✗ NON-EXISTENT SYMBOL** |
| "five Phase-134 exemption rows must be discharged" | five | **TWO** dischargeable rows: `(OP_SDP_LOCK, "derive_plan")` `:422-424` and `(OP_SDP_UNLOCK, "derive_plan")` `:425-427`. The other three "134" mentions are **not dischargeable**: `:388-394` is LEG-09's **permanent** asymmetry, `:309-314` is a **non-registry** row, `:528` is a docstring aside | **✗ OVERCOUNT (5→2)** |
| collection-time hazard | not mentioned | **`assert len(_ALL_OPS) == 9` at `:150` — a bare MODULE-LEVEL assert.** Adding four op constants makes this fire at import, turning all 7 tests into **collection errors** | **⚠ NEW, BLOCKING** |
| test-7 disposition pins | not mentioned | `("derive_plan", OP_SDP_LOCK): False` and `("derive_plan", OP_SDP_UNLOCK): False` at **`:801-802`** must flip to `True` in the same commit | **⚠ NEW** |
| `_MULTIWORD_OP_VALUES` derivation | not mentioned | `:148` — `frozenset(v for v in _ALL_OPS if "-" in v)`. **All four new ops are hyphenated**, so they auto-join and become forbidden substrings for `_ALWAYS_WRITES_NOTICE` | **⚠ NEW** |
| `_REGISTRY_CONSTANT_NAMES` | not mentioned | `:138-140` — `{"_DESTRUCTIVE_OPS","_MULTI_RUN_OPS","_SDP_OPS"}`. **A new `_SDP_LEG_OPS` frozenset will NOT resolve transitively unless added here** | **⚠ NEW** |

Other measured anchors: `_OP_CONSTANT_NAMES` `:122` · `_ALL_OPS` `:128` · `_op_names_referenced_in`
`:175` · `_POLICED_REGISTRIES` `:231-240` · `_DECLARED_NON_REGISTRIES` `:276-326` ·
`_OP_REGISTRY_EXEMPTIONS` `:375-445` · `_assert_op_parity` `:495` · `_stale_exemption_rows` `:519` ·
`_count_op_vocabulary_references` `:579` · `_measure_op_vocabulary` `:608` · the 7 tests at `:660`,
`:671`, `:693`, `:715`, `:733`, `:753`, `:786`.

## 1.9 Test infrastructure — re-measured (⚠ `.planning/codebase/TESTING.md` is stale; do not read it)

| Fact | CONTEXT.md | MEASURED | |
|------|-----------|----------|---|
| test files | 90 | **86** `tests/test_*.py` (95 `.py` total under `tests/`, incl. `conftest.py` + `fixtures/`) | ✗ DRIFT −4 |
| tests passing | 1338 | **1338 passed in 143.26s** | ✓ |
| coverage | 81.84% | **81.84%** (floor 70%) | ✓ |
| `tests/test_chip_test.py` | 1958 lines | **1958** | ✓ |
| `tests/test_chip_test_sdp_leg.py` | — | 1257 lines | ＋ |
| `tests/test_dev_test_cmd.py` | — | 699 lines | ＋ |
| `tests/test_diagnostic_report.py` | — | (36 173 bytes) | ＋ |
| `tests/conftest.py` | `make_app_context` `:229-237`, `app_context` `:325` | `make_app_context` `:229`, `app_context` `:325`, `build_frame` `:125`, `_FakeSerial` `:138`, `make_comm` `:201` | ✓ |
| `test_dev_test_cmd.py::test_always_writes_notice_is_the_first_line_unconditionally` | — | `:227` | ＋ |
| the `write_eprom.assert_not_called()` idiom D-17 extends | — | `:662` (and `read_hardware_revision_value.assert_not_called()` at `:580`) | ＋ |

## 1.10 The budget — RE-MEASURED, all four CONTEXT.md numbers CONFIRMED

```
$ firestarter_app/tools/ci_replica_venv.sh      → CI-REPLICA: PASS (all 5 legs exit 0)
$ .venv/ci-replica/bin/python tools/check_mypy_watermark.py
  checked 124 source files
  mypy errors: 33 (watermark: 35)
```

| Budget | Value | Headroom |
|--------|-------|----------|
| mypy errors | **33** vs watermark **35** | **2** — do not spend on unasked strengthening |
| checked source files | **124** vs `MIN_CHECKED_SOURCE_FILES = 120` (`tools/check_mypy_watermark.py:48`) | **a FLOOR** — adding source files moves *further above* it. Correction 4 CONFIRMED. |
| coverage | 81.84% vs 70% floor | ~11.8 pts |
| strict islands (`disallow_untyped_defs = true`) | `pyproject.toml:181-193` — `main`, `cli_handlers`, `chip_resolver`, `frame_parser`, `codec`, `address_parser`, `exceptions`, `serial_comm`, **`sdp_honesty`** | `chip_test` and `diagnostic_report` are in **neither** island; global is `disallow_untyped_defs = false`, `check_untyped_defs = false` (`:157-158`) |
| interpreter | CI-replica **Python 3.11.15**, mypy 2.3.0, numpy absent | devcontainer is py3.12 and its own mypy exits 2 against numpy |

**Practical consequence:** every helper added to `cli_handlers.py` (D-09/D-12/D-14/D-15) needs full
annotations or it is an *error*, not a watermark contribution. Helpers added to `chip_test.py` /
`diagnostic_report.py` are unchecked bodies and cost nothing. **Put the logic in `chip_test.py`** —
which is also what P-07 requires for a different reason.

---

# §2 — The exact shapes the planner must instruct against

> Everything in this section is quoted or line-cited from the working tree. Where CONTEXT.md or the
> research spine paraphrased, the *actual* text is given.

## 2.1 `generate_pattern`, the B generator, and P-01 — MEASURED

```python
# chip_test.py:64-72
def generate_pattern(start: int, length: int) -> bytes:
    """Region-parameterized address-derived pattern (D-02). ..."""
    return bytes(address_fold_byte(start + i) for i in range(length))

# chip_test.py:53-61
def address_fold_byte(addr: int) -> int:
    return (addr ^ (addr >> 8) ^ (addr >> 16) ^ (addr >> 24)) & 0xFF
```

**Measured live** (`python3 -c` against the installed module, region `(0, 256)` — the real region for
a non-UV ALLOW chip):

| Property | Measured |
|----------|----------|
| `A = generate_pattern(0, 256)` | `00 01 02 03 04 05 06 07 … fc fd fe ff` — i.e. `bytes(range(256))` |
| `B = bytes(~x & 0xFF for x in A)` | `ff fe fd fc fb fa f9 f8 … 03 02 01 00` |
| `A == B` | **False** |
| differ at **every** byte | **True** (all 256) |
| `A` all-`0x00` / all-`0xFF` | False / False |
| `B` all-`0x00` / all-`0xFF` | False / False |
| `A.count(0xFF)` / ratio | 1 / **0.00390625** |
| `B.count(0xFF)` / ratio | 1 / **0.00390625** |
| `_FF_RATIO_THRESHOLD` | **0.98** (`chip_test.py:127`) |
| `classify_fingerprint(A, B, addr_base=0)` | `indeterminate`, `bad=256`, `ff_ratio=0.00390625` |
| `generate_pattern(0,256) == generate_pattern(0,256)` | **True** ← **P-01's trap, live** |

**D-05 CONFIRMED to the digit.** A fully-B read-back cannot reclassify as `blank/contact`:
`0.0039 << 0.98`. D-19's five assertions are all satisfiable and all non-trivially true.

**P-01 restated as an acceptance criterion, not a nicety:** because `generate_pattern` is pure in
`(start, length)`, `generate_pattern(region) == generate_pattern(region)` — so **any** implementation
that derives B by calling `generate_pattern` again (with the same region, or with a "different seed"
that reduces to the same region) produces `A == B`, and the oracle becomes a tautology that a
reviewer reading the diff will not see. D-19's *"differ at every byte"* assertion — computed against
the **live generators for the real region**, never a byte literal — is the only structural proof.

**LEG-16's fixture, concretely:** `A` is *already* what the shipped `write` step writes (region
`(0,256)`, `runs=2`). So a chip that already holds `A` and whose write is a no-op passes
`write`→`verify` today. The fixture must therefore be: operator double whose `write_eprom` returns
`True` but whose `read_eprom` always yields `A` — then `write-baseline-b`'s read-back is `A`, not
`B`, and that step goes **BAD**. **The B direction is the entire discriminating power** (D-07's
"Why reuse cannot satisfy LEG-16").

## 2.2 `_diff_offsets` / `classify_fingerprint` and P-02 — MEASURED

```python
# chip_test.py:98-110
def _diff_offsets(expected: bytes, actual: bytes) -> tuple[int, list[int], float, int | None]:
    cmp_len = min(len(expected), len(actual))
    diff_offsets = [o for o in range(cmp_len) if expected[o] != actual[o]]
    pct = 100.0 * len(diff_offsets) / cmp_len if cmp_len else 0.0
    first = diff_offsets[0] if diff_offsets else None
    return cmp_len, diff_offsets, pct, first
```

**MEASURED:** `classify_fingerprint(A, b"")` → `classification="indeterminate"`, **`total=0`**,
**`bad=0`**. An empty read-back produces **zero differences** and `pct=0.0`. Any oracle written as
`if fp.bad == 0: OK` reports an empty read-back as **perfect equality** — P-02, reproduced live.

`classify_fingerprint`'s order is LOCKED (`:157-163`): blank/contact → address-line → transport →
indeterminate. Note the address-line arm is **structurally unreachable for a 256-byte region**:
`:199` requires `cmp_len > (1 << 8)` i.e. `> 256`. So for the SDP leg's region, `classify_fingerprint`
can only ever return `blank/contact`, `transport`, or `indeterminate`. **[MEASURED — this narrows
D-04's content-degeneracy arms to two reachable labels, and a test asserting `address-line` for this
region would be unreachable-green.]**

**D-04's split, as an implementable gate order:**
1. `len(actual) != len(expected)` (incl. empty) ⇒ **BAD** — the oracle had no input. *Must be checked
   BEFORE any `_diff_offsets`/`classify_fingerprint` call*, because `_diff_offsets` silently truncates
   to the common prefix and never raises.
2. correct length, content degenerate (all-`0x00`/all-`0xFF`) ⇒ route through `classify_fingerprint`
   ⇒ lands `blank/contact` (ff_ratio ≥ 0.98) or `transport`/`indeterminate` ⇒ **marginal**.
3. correct length, `actual == A` ⇒ OK arm. `actual == B` ⇒ BAD arm (or marginal per D-02 when the
   precondition bool was `False`). anything else ⇒ **partial change ⇒ BAD** (LEG-07 / gh#11).

## 2.3 `_dispatch_sdp` — the frozen signature and terminal raise (VERBATIM)

```python
# chip_test.py:1423-1425
def _dispatch_sdp(
    op: str, name: str, eprom_data: dict[str, Any], operator: Any
) -> StepResult:
```
Docstring (`:1428-1440`) states the contract in terms Phase 134 must honour verbatim:
> *"Signature is a FORWARD CONTRACT (v1.30 Phase 133 D-01, LEG-09) … No keyword-only parameters: SDP
> emissions are single-run (D-03, `_MULTI_RUN_OPS` exclusion above), so `runs` and `sampler` are
> deliberately absent here, not merely omitted by oversight."*

Guard → branch → terminal raise (`:1442-1473`):
```python
    if op not in _SDP_OPS:
        return StepResult(op=op, verdict=VERDICT_BAD, run_count=0, reason=(
            f"op {op!r} is not in the SDP dispatch allow-list "
            "(_SDP_OPS) — refused fail-closed rather than falling "
            "through to an operator mutation method"))
    if op == OP_SDP_LOCK:
        is_ok = operator.sdp_lock(name, eprom_data)
    elif op == OP_SDP_UNLOCK:
        is_ok = operator.sdp_unlock(name, eprom_data)
    else:
        raise AssertionError(f"unreachable: op {op!r} passed the _SDP_OPS guard")
    return StepResult(op=op, verdict=VERDICT_OK if is_ok else VERDICT_BAD, run_count=1)
```
**D-08 forbids changing this signature.** The four new write-shaped ops therefore need their **own**
dispatcher (they need `runs`-free single-run semantics *plus* a source path *plus* a read-back — none
of which fits `_dispatch_sdp`'s four positional params). Clone the same guard→branch→terminal-raise
shape; that is the house idiom (`_dispatch_multi_run:1320-1330` + `:1368`).

**`_dispatch_step`'s arm order (MEASURED, `:1143-1190`):** `OP_ID` → `OP_BLANK_CHECK` → `OP_READ` →
`in _MULTI_RUN_OPS` → `in _SDP_OPS` → **terminal fail-closed `return VERDICT_BAD`** with reason
*"op {op!r} matched no dispatch arm — refused fail-closed rather than falling through to
`_dispatch_multi_run`"*. A new arm must sit **above** that terminal return, and
`test_shipped_ops_never_reach_sdp_arm` (the D-13b sentinel in `test_chip_test_sdp_leg.py`) pins that
the seven shipped ops never evaluate the SDP membership test — **placing the new arm *before* arm 5
could break that sentinel; place it after.**

## 2.4 The report surface — what is and is not visible

**`render()`'s per-step row (`diagnostic_report.py:471-476`), VERBATIM:**
```python
        for step_row in d["steps"]:
            table.add_row(
                f"step: {step_row['op']}",
                f"{step_row['verdict']} (err={step_row['error_code']}, "
                f"fingerprint={step_row['fingerprint']})",
            )
```
**`reason` is absent.** D-07's basis, MEASURED. `reason` reaches only `_step_dict` (`:406-415` → the
JSON) and `cli_handlers.py:2191-2202` (the markdown table).

**`to_dict()`'s nine keys (`:443-454`):** `schema_version`, `generated`, `auto_capture`,
`transport_health`, `steps`, `banner`, `voltage`, `is_submittable`, `dedup_fingerprint`, `db_diff`.
D-10 adds a tenth. `SCHEMA_VERSION = "1.2"` at `:55`.

**`dedup_fingerprint` (`:220-226`), VERBATIM:**
```python
    ac = report.auto_capture
    parts = [ac.chip or "", str(ac.protocol or "")]
    for result in report.results:
        cls = result.fingerprint.classification if result.fingerprint else ""
        parts.append(f"{result.op}={result.verdict}:{cls}")
    canonical = "|".join(parts)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]
```
Six new steps ⇒ six new `parts` entries ⇒ **every ALLOW chip re-keys**. D-11's cost, MEASURED
mechanism. gh#20's orphaned id is **`00e121446ceb`** (§4.8).

**LEG-14's "erase" trap, MEASURED:** the report legitimately contains "erase" in at least three
places — `derive_plan`'s 0x0D NA reason (`chip_test.py:577-580`, *"protocol 0x0D (28C family) has no
erase operation; each page write auto-erases internally"*), the `erase` op string itself in both the
markdown table and JSON, and `_ALWAYS_WRITES_NOTICE`'s *"write/verify/erase step"*
(`cli_handlers.py:2071`). **A whole-report grep is RED on correct text.** D-13's scoped-constant
pytest is the only non-exempting form.

## 2.5 Exit codes — correction 3 CONFIRMED VERBATIM

```python
# cli_handlers.py:1884-1894 — comment and table together
# Per-verdict -> exit-code mapping (D-01): OK/NA/SKIPPED are exit-clean;
# `marginal` is an inconclusive result (exit 2); BAD beats marginal via
# `max` over the whole result set, mirroring dev_validate_family's own
# `if verdict_int > overall_verdict` pattern (cli_handlers.py:1620-1621).
_VERDICT_EXIT_CODES = {
    VERDICT_OK: 0, VERDICT_NA: 0, VERDICT_SKIPPED: 0,
    VERDICT_MARGINAL: 2, VERDICT_BAD: 1,
}

# :1900-1902
def _verdict_code(verdict: str) -> int:
    """Map a single StepResult verdict to its 0/1/2 exit-code contribution."""
    return _VERDICT_EXIT_CODES.get(verdict, 0)

# :2216-2219
    if not results:
        sys.exit(0)
    code = max(_verdict_code(r.verdict) for r in results)
    sys.exit(code)
```
`max(1, 2) = 2` ⇒ **marginal beats BAD**, contradicting the comment at `:1888-1890` *and* the
docstring at `:2119-2121` (*"2 if any step is marginal (and none BAD), 1 if any step is BAD"*).
Both false today. **LEG-06's "exit 1" is unreachable on any marginal-bearing run until D-14 lands**,
and the truth table has three `marginal` arms — so D-14 is a hard prerequisite of LEG-06, not a
side-fix.

Note also `_verdict_code`'s `.get(verdict, 0)` — an unrecognised verdict exits **0**. CONTEXT.md's
"no sixth status" rule is load-bearing for exactly this reason.

## 2.6 `derive_plan` / `run_plan` / `count_applicable` — the NA and counting mechanisms

**`derive_plan`'s NA path (`chip_test.py`):** every NA step is `Step(op=..., supported=False,
reason=<prose>)`; `run_plan:877-879` turns it into `_skip_result(step.op, step.reason,
verdict=VERDICT_NA)` **with no operator call**:
```python
        for step in plan.steps:
            if not step.supported:
                results.append(_skip_result(step.op, step.reason, verdict=VERDICT_NA))
                continue
```
**LEG-02 needs zero new machinery** — only `derive_plan` emitting six `supported=False` steps
carrying `sdp_capability()`'s own reason text.

**`write_execute` (`:463`), the D-18 gate:**
```python
    write_execute = write_scope in (_WRITE_SCOPE_FULL, _WRITE_SCOPE_PARTIAL)
```

**`count_applicable` (`:1536-1539`), VERBATIM:**
```python
    m_applicable = sum(1 for s in plan.steps if s.supported) + len(plan.locked_destructive)
    n_ran = sum(1 for r in results if r.verdict in _RAN_VERDICTS)
```
with `_RAN_VERDICTS = frozenset({VERDICT_OK, VERDICT_BAD, VERDICT_MARGINAL})` at `:1500`.

**MEASURED for a representative ALLOW chip** (`AT28BV64B,AT28LV64B`, `write_scope="full"`):

```
step id           sup=False  → NA        (reason: "no chip-id in DB entry")
step read         sup=True   → counts
step blank-check  sup=True   → counts
step write        sup=True   destr=True  region=(0, 256)
step verify       sup=True               region=(0, 256)
step erase        sup=False  → NA        (0x0D has no erase operation)
locked_destructive = []      →  M = 4    (today's banner: "4 of 4 ran")
```

Adding six `supported=True` SDP steps ⇒ **M = 10**. A `SKIPPED` SDP step is excluded from `N` but
counted in `M`. **D-15's claim CONFIRMED: the ratio already drops; LEG-13 needs a pinning test, not
new counting logic.** (And per §4.4, editing `count_applicable` would actively *break* the parity
gate's inversion guard.)

## 2.7 `write_eprom`'s bool and the `0x86` ack — correction 1 CONFIRMED

```python
# eprom_operations.py:1583-1590
    def write_eprom(self, eprom_name: str, eprom_data_dict: dict, input_file_path: str,
                    operation_flags: int = 0, address_str: Optional[str] = None) -> bool:
```
```python
# eprom_operations.py:1653-1665
            is_protocol_0x0d = eprom_data_dict.get("algorithm") == SDP_PROTOCOL_ID
            if is_protocol_0x0d and (operation_flags & FLAG_SKIP_SDP_UNLOCK):
                if MSG_WARN_SDP_UNLOCK_SKIPPED not in self.comm.seen_message_ids:
                    logger.error(...)
                    is_ok = False
```
Its own comment at `:1621-1625` states the correction-1 mechanism verbatim:
> *"This check MUST read `self.comm.seen_message_ids` here, inside the `_operation_context` `with`
> block: that block's `finally` calls `_disconnect_programmer()`, which sets `self.comm` to None, so
> a read after the block exits would raise or silently see nothing."*

**Two consequences the planner must plan against:**
- The ack is **already folded into the returned bool**. `chip_test.py` cannot read it separately.
  D-01's "precondition signal" reading is the *only* implementable one. Research's truth-table
  branch 5 is not implementable — record it as overturned.
- **The ack path is LIVE for the SDP leg.** MEASURED: ALLOW chips carry `algorithm == 13`
  (`SDP_PROTOCOL_ID`), so `is_protocol_0x0d` is `True`. Setting `FLAG_SKIP_SDP_UNLOCK` on the
  `write-inhibited` step *does* arm the ack requirement. Old firmware ⇒ `is_ok = False` ⇒ D-01's
  marginal arm with the firmware-update instruction. This is the designed behaviour, not a bug.

`sdp_lock`/`sdp_unlock` (`:1784`/`:1736`) both accept `operation_flags: int = 0` and both docstrings
state the emission-only limit explicitly (*"A `True` return means only that the command sequence was
**emitted** over the wire"*). **Do not re-author that wording** — `sdp_honesty.unreadable_state_caveat()`
(`sdp_honesty.py:33`) and `emission_summary(mode, chip_name)` (`:45`) already carry it as Phase 132's
forward contract for exactly this phase's report rows.

---

# §3 — Sequencing and the one-writer-per-file constraint

**Worktree isolation is UNAVAILABLE inside the `firestarter_app` submodule** (v1.23 P129 finding:
absolute-path criteria cross the submodule boundary). So *two plans may never write the same file
concurrently*, and there is no escape hatch.

## 3.1 File → requirement matrix [MEASURED file assignments; INFERRED requirement split]

| File | Requirements landing here | Concurrency |
|------|---------------------------|-------------|
| **`firestarter/chip_test.py`** | LEG-01, 02, 03, 04, 05, 06, 07, 08 (+ D-07, D-08, D-18, D-19; the `HELD` **derivation** per §4.4) | **SERIAL SPINE — 8 of 14 requirements.** Never concurrent with itself. |
| `firestarter/diagnostic_report.py` | LEG-12 (field + `to_dict` + `SCHEMA_VERSION` 1.2→1.3); D-11's cost is passive | parallel with `cli_handlers.py` **only after** the field name is fixed |
| `firestarter/cli_handlers.py` | LEG-12 (render/echo), LEG-14 (constants), D-09, D-12, D-14, D-15 | strict mypy island; D-14 is independent of everything else |
| `firestarter/constants.py` | none (import target only) | — |
| `firestarter/sdp_honesty.py`, `sdp_capability.py` | none (call targets) | — |
| `firestarter/eprom_operations.py` | **none — RING-FENCED** | — |
| **`tests/test_op_registration_parity.py`** | none *ticked* (LEG-15 stays `[x]`) but **must be edited in the same commits as `chip_test.py`** — §4.2 | **coupled to the spine** |
| `tests/test_chip_test_sdp_leg.py` (or a sibling) | LEG-03, 04, 05, 06, 07, 08, 16 proofs | parallel across distinct files |
| `tests/test_dev_test_cmd.py` | LEG-17 (R1–R6 + R7), D-09's derived-count test, D-14/D-15 exit pins | parallel |
| `tests/test_diagnostic_report.py` | LEG-12 JSON + the no-boolean assertion (D-10) | parallel |
| `tests/test_chip_test.py` (1958 lines, 10 `run_plan` call sites) | regression surface for `derive_plan`/`count_applicable` changes | **read-first hazard** — a step-count change ripples here |
| `.planning/phases/134-.../…` + a backlog item | LEG-18 | parallel, no code |

## 3.2 Recommended wave structure

```
WAVE A  (1 plan, SERIAL)   chip_test.py: op constants + B generator + _SDP_LEG_OPS
                            + derive_plan emission (ALLOW 6 steps / REFUSE 6 NA)
        SAME COMMITS ⇒      test_op_registration_parity.py: assert 9→13, +12 exemption rows,
                            −2 derive_plan rows, test-7 pins flip, _REGISTRY_CONSTANT_NAMES widen,
                            _POLICED_REGISTRY_COUNT 6→7 (if _SDP_LEG_OPS is policed)
                            ── LEG-01, LEG-02, LEG-03 ──
        ⚠ There is NO green intermediate state. Do not split this boundary across waves.

WAVE B  (1 plan, SERIAL)   chip_test.py: the leg dispatcher + the no-default truth table
                            + _baseline_closes_sdp_gate in run_plan + cleanup de-registration
                            + FLAG_SKIP_SDP_UNLOCK on write-inhibited only
                            ── LEG-04, LEG-05, LEG-06(engine half), LEG-07, LEG-08 ──

WAVE C  (2 plans, PARALLEL — distinct files)
        C1  diagnostic_report.py  : the HELD/NOT-HELD/NOT-RUN str field, to_dict, SCHEMA_VERSION 1.3
        C2  cli_handlers.py       : D-14 exit precedence ONLY (independent; unblocks LEG-06's exit 1)

WAVE D  (1 plan, SERIAL)   cli_handlers.py: HELD derivation call-through + D-15 exit floor
                            + D-09 notice rewrite + D-12 two recovery forms + LEG-14 constants
                            ── LEG-12, LEG-14, LEG-15-adjacent ── (depends on C1's field name)

WAVE E  (3-4 plans, PARALLEL — distinct test files)
        E1  tests/test_chip_test_sdp_leg.py (or sibling) : 2×2 polarity, 4 degenerate fixtures, LEG-16
        E2  tests/test_dev_test_cmd.py                   : R1–R6 + R7 routes, D-09 derived count,
                                                           D-14/D-15 exit pins
        E3  tests/test_diagnostic_report.py              : LEG-12 JSON + no-boolean assertion
        E4  scoped "rewrite"-not-"erase" pytest + non-vacuity leg (new file — LEG-14)
                            ── LEG-06(exit half), LEG-13, LEG-16, LEG-17 ──

WAVE F  (1 plan)           gh#20 triage record + backlog item with a named owner + the record's
                            two-reading corrections (four vs six steps; exit precedence)
                            ── LEG-18 ──
```

**Serial spine:** A → B → (C1 ‖ C2) → D → E‖ → F. Four of six waves are single-plan because
`chip_test.py` and `cli_handlers.py` each carry multiple requirements and cannot be co-written.

**Dispatch rule (ROADMAP cross-cutting, and this project's 4× premature-tick history):** name the
allowed requirement IDs **per plan** at dispatch, exactly as bracketed above. Explicitly **not**
LEG-09/10/11/15, nor any RELOCK/CHAN/CLOSE row.

---

# §4 — Open implementation questions

CONTEXT.md's five candidates are answered below (confirmed, refuted, or resolved), plus three the
measurement pass found.

## 4.1 OQ-1 — D-08's baseline-gate flag: exactly where, and what happens to `sdp-unlock`

**Where (MEASURED, unambiguous).** `run_plan`'s flags are all created *before* the `try` at `:853-869`
and consulted inside the loop:
```
:854   destructive_gate_closed = False        ← sibling init site for the new flag
:877   if not step.supported:  → NA
:881   if step.op in _DESTRUCTIVE_OPS and destructive_gate_closed:  → SKIPPED(_DESTRUCTIVE_GATE_REASON)
:885   result = _run_step(...)
:890   if step.op == OP_SDP_LOCK and result.verdict == VERDICT_OK:  → register cleanup
:920   if step.op == OP_ID: destructive_gate_closed = _id_step_closes_gate(result)  ← structural template
```
The baseline gate is a **second guard clause immediately after `:883`**, and a **second set clause
immediately after `:921`**. It does **not** interact with the cleanup registry (which keys only on
`OP_SDP_LOCK` + `VERDICT_OK`, and a gated lock never runs).

**It DOES interact with `destructive_gate_closed`, and the order matters.** The four new write ops
must join `_DESTRUCTIVE_OPS` (they mutate). So on a chip-ID mismatch the **existing** guard at `:881`
fires first and they render `_DESTRUCTIVE_GATE_REASON`'s chip-ID wording — which is correct for R1/R2
and is exactly what D-08 wanted to avoid *for the baseline case*. Since the ID gate is vacuous for
all 43 ALLOW chips (§2.6 / §4.3), the baseline gate is the live one in production. Keep both,
ID-gate-first.

**GENUINELY OPEN — the planner must decide and record:** D-08 says the gate closes `sdp-lock`,
`write-inhibited` and `write-restored`, and that *"`sdp-unlock` is never attempted because nothing was
locked."* But `OP_SDP_UNLOCK` is deliberately **absent** from `_DESTRUCTIVE_OPS` (LEG-09), and the
baseline gate as described does not list it — so as literally specified, **`sdp-unlock` would RUN**,
emitting an unlock sequence on a part that was never locked and reporting `OK`. That `OK` is an
emission claim on a step whose premise did not hold, and it is precisely the P-06 shape.

*Recommended resolution [INFERRED]:* include `OP_SDP_UNLOCK` in the **baseline-gate** set and render it
`SKIPPED` with a reason naming *"no lock was emitted — baseline gate closed"*. This does **not**
violate LEG-09: LEG-09 is scoped to the ***destructive*** gate (`_DESTRUCTIVE_OPS` membership,
`chip_test.py:663` + `test_unlock_exempt_from_destructive`), a different mechanism. State that
distinction in the record and pin it with a test asserting a *destructive*-gate closure still never
skips the unlock (the 133 proof stays byte-identically green).

*Measured consequence for gh#20's shape:* `write-baseline-b` BAD → gate closes → five SKIPPED ⇒
N = 5, M = 10 ⇒ banner reads **"5 of 10 ran"** instead of today's misleading "4 of 4".

## 4.2 OQ-2 — the cleanup registry double-fire — RESOLVED, with the exact API

**The registry API (MEASURED, `chip_test.py:869` + `:890-918` + `:967-971`):**
```python
    cleanup: list[Callable[[], None]] = []                        # :869
    ...
            if step.op == OP_SDP_LOCK and result.verdict == VERDICT_OK:   # :890
                def _unlock_cleanup() -> None:                            # :909
                    _run_step(plan.name, Step(op=OP_SDP_UNLOCK, supported=True, reason=""),
                              operator, db, runs=runs)
                cleanup.append(_unlock_cleanup)                            # :918
    finally:
        for cleanup_call in cleanup:                                       # :967
            try:
                cleanup_call()
            except _UNLOCK_CLEANUP_SWALLOWED:
                continue
```
There is **no suppression mechanism today**. With Phase 134's explicit `sdp-unlock` step in the plan,
a successful lock registers a cleanup **and** the plan step runs it ⇒ **two unlock emissions**. 133
D-11 rejected the both-paths shape *because of* the double-count and the endurance notice.

**Resolution [INFERRED, but forced by the measured shape]:** hold a handle and de-register on a
**successful explicit** unlock, sited symmetrically next to the registration block:
```python
    unlock_cleanup: Callable[[], None] | None = None      # beside :869
    ...
            if step.op == OP_SDP_LOCK and result.verdict == VERDICT_OK:
                ...
                unlock_cleanup = _unlock_cleanup
                cleanup.append(_unlock_cleanup)
            if step.op == OP_SDP_UNLOCK and result.verdict == VERDICT_OK and unlock_cleanup is not None:
                cleanup.remove(unlock_cleanup)            # the explicit step already did it
                unlock_cleanup = None
```
Prefer `cleanup.remove(handle)` over `cleanup.clear()`: the registry's own comment at `:855-868`
declares it *"deliberately GENERIC rather than a hardcoded lock-to-unlock window"*, so `.clear()`
would over-reach the moment any other op registers something.

**Three properties a test must pin:** (a) a completed leg emits `sdp_unlock` exactly **once**;
(b) a leg that raises *before* the explicit unlock still emits it **once** via the drain (LEG-10 must
stay green byte-identically); (c) a **failed** explicit unlock (`verdict != OK`) leaves the cleanup
registered, so the drain still retries.

## 4.3 OQ-3 — `FLAG_SKIP_SDP_UNLOCK` plumbing — the minimum change is SMALLER than FEATURES §1.4 says

FEATURES §1.4 frames it as *"passing `operation_flags=` to the existing `write_eprom`"* inside
`_dispatch_multi_run`. **That is not needed.** MEASURED:
- The four new ops are **not** `_MULTI_RUN_OPS` members (single-run, they fold their own read-back),
  so they never reach `_dispatch_multi_run:1352` at all.
- `write_eprom`'s `operation_flags` is already a **4th positional parameter with a default**
  (`eprom_operations.py:1588`) — no ring-fence edit, no new operator method.
- `build_flags` (`:173`, bit mapped at `:209`) and `command_dict["flags"] = … | operation_flags`
  (`:338`) confirm the bit reaches the wire.

**Minimum change:** extend `chip_test.py:37`'s existing constants import
(`from firestarter.constants import FLAG_CAN_ERASE  # 0x02 -- do NOT redefine; import`) to also import
`FLAG_SKIP_SDP_UNLOCK` (`constants.py:136`, `0x100`), and pass it **from the new leg dispatcher, on
the `write-inhibited` step only**. `_dispatch_multi_run` is untouched.

**Two things a test must pin:** (a) `write_eprom` is called with `FLAG_SKIP_SDP_UNLOCK` set on
`write-inhibited`; (b) it is called with the flag **clear** on `write-baseline-b`,
`write-baseline-a`, and **`write-restored`** — setting it on `write-restored` would defeat the
step's whole purpose (it must be allowed to auto-unlock and succeed). Also update `chip_test.py`'s
module docstring contract line (*"sets no VPP, builds no wire dict"*, `:21-25`) to **deliberately
narrow** it rather than silently violate it.

## 4.4 OQ-4 (**NEW, BLOCKING**) — the inversion guard forbids deriving `HELD` inside `DiagnosticReport`

`tests/test_op_registration_parity.py::test_non_registry_still_has_no_ops` (`:733-745`) re-measures,
**by AST, every run**, that each declared non-registry carries **zero** op vocabulary
(`_count_op_vocabulary_references`, `:579-594`): any `ast.Name` whose id is an `OP_*` constant, plus
any non-docstring string literal equal to a **hyphenated** op value. Its failure message is:
> *"A declared non-registry has acquired op vocabulary — PROMOTE it to `_POLICED_REGISTRIES`, do not
> loosen this guard."*

Three declared non-registries are directly in this phase's path (`:276-326`):
`_RAN_VERDICTS/count_applicable` (`function` locator), `dedup_fingerprint` (`function`),
**`diagnostic_report.py renderer` — a `class` locator over the whole `DiagnosticReport` body**, and
**`_ALWAYS_WRITES_NOTICE`** (`constant` locator).

**Therefore:**
- **D-10's field value must be DERIVED OUTSIDE `DiagnosticReport`.** Any `if result.op ==
  OP_SDP_LOCK` / `"sdp-lock"` inside that class body — including inside `to_dict`, `render`, or
  `_step_dict` — makes the guard fail. Recommended: a pure `chip_test.py` function
  (`sdp_hold_state(plan, results) -> str`), assigned by `cli_handlers.py` to a plain `str` field on
  `DiagnosticReport`, which then serialises it generically. This also lands the logic in the module
  P-07 requires (scanned in full) and off the mypy strict island (§1.10).
- **`count_applicable` must NOT be edited.** P-04 prevention 3 suggests extending `M`; D-15 already
  measured that unnecessary — and doing it would add op vocabulary to a declared non-registry and
  trip the guard. **Two independent reasons not to touch it.**
- `dedup_fingerprint` stays generic (it already is) — D-11's re-key happens automatically.

## 4.5 OQ-5 (**NEW**) — D-09's rewritten notice may not contain any hyphenated op literal

`_ALWAYS_WRITES_NOTICE` is a `constant` locator; `_measure_op_vocabulary` (`:613-617`) evaluates
`sum(1 for mw in _MULTIWORD_OP_VALUES if mw in value)` — a plain **substring** test over the live
string. `_MULTIWORD_OP_VALUES` is derived (`:148`) as *every op value containing a hyphen*, today
`{"blank-check", "write-partial", "sdp-lock", "sdp-unlock"}`.

After this phase it becomes **eight**: the four above plus `write-baseline-a`, `write-baseline-b`,
`write-inhibited`, `write-restored` (assuming CONTEXT.md's op names). D-09 asks the notice to
*"name the SDP lock"* — writing **`SDP lock`** (space, prose) is safe; writing **`sdp-lock`** makes
`test_non_registry_still_has_no_ops` go RED. The current notice survives only because
*"write/verify/erase step"* uses single-word ops, which are deliberately excluded (`:142-147`).

Same hazard applies to D-12's two recovery-form constants **if** they are ever declared as
non-registries — they are not today, so they are free; but D-13's scoped grep should assert the
notice/recovery constants contain "rewrite" and not "erase" **and** carry no hyphenated op literal,
which folds both gates into one place.

## 4.6 OQ-6 — D-14's audit — **DISCHARGED**, and D-15's insertion point

**D-14's blocking precondition is satisfied.** MEASURED — every test in the tree asserting
`exit_code == 2`:

| Site | Shape | Affected by D-14? |
|------|-------|-------------------|
| `test_dev_test_cmd.py:202`, `:217` | Click *"no such option"* for removed flags | **No** — Click's own exit 2 |
| `test_dev_test_cmd.py:648` `test_marginal_disagreement_exits_2` | `write_eprom.side_effect=[True, False]` | **No** — see below |
| the parametrised `({"write_eprom.side_effect": [True, False]}, 2)` row | same shape | **No** |
| `test_cli_handlers.py` (7 sites), `test_py32_channel_gating.py` (3), `test_validate_oracle.py:307` | unrelated commands | **No** |

Measured verdict set for the marginal case (reproduced with the real `derive_plan`/`run_plan` and the
test's own operator double):
```
id NA · read OK · blank-check OK · write marginal · verify OK · erase OK
codes [0,0,0,2,0,0] → max = 2 ; MIXED BAD+marginal? False
```
**There are zero existing tests asserting exit 2 on a mixed BAD+marginal run.** D-14 lands with no
test-audit blast radius. Its non-vacuity leg must therefore be a **new** mixed-run test.

**D-15's insertion point (MEASURED, `cli_handlers.py:2213-2216`):** the current expression is
`code = max(_verdict_code(r.verdict) for r in results)`. D-14 replaces the `max` with explicit
precedence (BAD ≻ marginal ≻ clean); D-15 adds **one** non-verdict term *after* it — if the chip is
ALLOW and the field reads `NOT-RUN`, floor the result at 2. Composed, in the same expression:
```
verdict_code = <explicit precedence over results>          # D-14
if <chip is ALLOW> and <hold field == NOT-RUN>:            # D-15
    verdict_code = max(verdict_code, 2)
sys.exit(verdict_code)
```
Order matters and must be pinned: a run that is **both** BAD and NOT-RUN must exit **1**, not 2 —
otherwise D-15's floor re-creates the very laundering D-14 just removed. *[INFERRED — CONTEXT.md
does not state this composition; it is the only ordering consistent with both D-14's "BAD outranks
marginal" and D-15's "at least 2".]* Add it as an explicit acceptance criterion.

Both functions are in the **mypy strict island** — `disallow_untyped_defs = true` — so any new helper
needs full annotations (headroom is 2).

## 4.7 OQ-7 — LEG-14's scoped grep: what it may scan

D-13 locks the mechanism (a scoped pytest over named module-level constants, plus a non-vacuity leg
with a planted "erase" constant). The measured constraint that rules out the literal reading is in
§2.4. One addition [INFERRED]: the constants must be **module-level in `cli_handlers.py`** so
Phase 137's CLOSE-03 scanner can extend rather than duplicate — and P-07's `_HANDLER_FUNCTION_NAMES`
derived-subset gate (landed Phase 131, GATE-10) now catches a new *handler helper*, so keep the
handler-side additions to constants + one thin annotated function.

## 4.8 OQ-8 — gh#20: the triage input, MEASURED live

`gh issue view 20 --repo henols/firestarter_prom` (state **OPEN**, created **2026-07-30T16:44:03Z**,
title *"[dev test] at28c256 — FAIL (00e121446ceb)"*):

| Field | Value |
|-------|-------|
| host | `3.0.0b14` · hw_revision `Rev 2.3` · chip `at28c256` · protocol `13` |
| schema_version | `1.2` |
| steps | `id NA` · `read OK` · **`blank-check BAD`** · **`write BAD`** (fingerprint `indeterminate`) · **`verify BAD`** (`indeterminate`) · `erase NA` |
| banner | **`n_ran 4, m_applicable 4`** — reads as "4 of 4 ran", i.e. complete |
| voltage | vpp 11800 mV / vpe 13700 mV (before == after) |
| dedup_fingerprint | **`00e121446ceb`** ← D-11 orphans this exact id |
| db_diff | `supported` / `community-fail` |

**The finding to record:** gh#20 is the live instance of the dead-write-path hazard. Under this
phase's leg, `write-baseline-b` would go BAD on that bench, D-08's gate would close, and **no lock
would ever be emitted** — whereas a leg without the baseline gate would emit `sdp-lock` at a part
that cannot be rewritten. Its banner would drop from "4 of 4" to **"5 of 10"**. Its
`dedup_fingerprint` `00e121446ceb` is orphaned by the six added steps (D-11) and must be named
explicitly inside the LEG-18 finding, with the cost handed to Phase 137's release notes.
The underlying AT28C256 write/verify/blank-check failure is a **separate, still-open defect** to be
filed as a backlog item **with a named owner** (D-16). The public reply is Phase 137's (CLOSE-06).

---

# §5 — Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---------|-------------|-------------|-----|
| Byte divergence / % / first offset | a second diff loop | `_diff_offsets` (`chip_test.py:98`) | D-04 mandate: **one** divergence primitive tree-wide |
| "why did the compare fail" | ad-hoc heuristics | `classify_fingerprint` (`:143`) — **behind a length gate** | P-02: it reads empty as equality |
| NA steps for REFUSE chips | a new skip mechanism | `Step(supported=False)` → `run_plan:877-879` | zero new machinery; the 41 reasons are already user-facing prose |
| Unlock-on-exception | a `finally` in the new dispatcher | Phase 133's cleanup registry (`:869`, `:967`) | already proven by 6 committed tests; a second one double-fires |
| SDP honesty wording | new sentences | `sdp_honesty.unreadable_state_caveat()` / `emission_summary()` | Phase 132 D-02 built these as **this phase's** forward contract |
| Unknown-command → outdated firmware | a new error map | `sdp_honesty.map_unknown_cmd_to_outdated()` (`:67`) | keyed on message **id**, never text |
| Capability decision | a protocol/pinout heuristic | `sdp_capability(chip, db)` (`sdp_capability.py:266`) | fail-closed, derived, count-pinned at 43/41/84 |
| Applicable-step counting | extending `count_applicable` | nothing — it already works | D-15 measured it; and editing it trips the inversion guard (§4.4) |
| Exit-code vocabulary | a sixth verdict status | the existing five | `_verdict_code`'s `.get(verdict, 0)` exits **0** on an unknown verdict |
| A new pytest skip reason | adding to `ALLOWED_SKIP_REASONS` | **need none** | `tests/test_skip_census.py:110` fails **closed**; P-09 prevention 5 — if a fix wants one, re-examine the fix |
| Planted-violation fixtures | a new idiom | `tests/fixtures/planted_permit_by_default.py`, `planted_widenable_allowset.py` + `tools/check_sdp_capability_invariants.py` | **extend, never bypass** (P-09 D4) |

---

# §6 — Common Pitfalls (ranked by "will ship silently")

### P-01 — the vacuous oracle (**CRITICAL, milestone headline**)
`generate_pattern` is pure in `(start, length)` (§2.1, measured). The idiomatic implementation makes
A and B byte-identical and the milestone's central assertion a tautology that reads as correct in
review. **Warning signs:** B derived by calling `generate_pattern` again; a `!=` assertion phrased as
"differ somewhere"; an assertion against a byte literal instead of the live generators.
**Prevention:** D-19's five assertions, computed for the real region.

### Collection-time RED from the parity gate (**CRITICAL, new**)
`assert len(_ALL_OPS) == 9` at `test_op_registration_parity.py:150` is module-level. The first new
`OP_*` constant errors out all 7 tests at collection. **There is no green intermediate state.**
Fix in the same commit (§4.2, Wave A).

### The inversion guard promoting a "prose-only" file (**HIGH, new**)
D-09's notice and D-10's field are both one careless string away from
`test_non_registry_still_has_no_ops`. §4.4/§4.5.

### P-02 — empty read-back reads as equality (**HIGH**)
MEASURED: `classify_fingerprint(A, b"")` → `bad=0`. Length gate **before** any diff call. D-04.

### P-04/P-09 — laundering and downgrade (**HIGH**)
Six routes to exit 0; eight ways an implementer downgrades a real finding. The truth table must have
**no default arm**, no `NA`/`SKIPPED`/`marginal` inside the OK/BAD decision, and a terminal
`raise AssertionError` (the `_dispatch_sdp:1471` shape). Note R1/R2 are **structurally vacuous in
production** — MEASURED: **all 43 ALLOW chips have `chip-id == 0`**, so `derive_plan:490` emits
`Step(op=OP_ID, supported=False, reason="no chip-id in DB entry")` and `_id_step_closes_gate:985`
(`verdict in (BAD, SKIPPED)`) never fires on an `NA`. D-17's synthetic-nonzero-id fixture is what
makes the causal chain testable; label it unreachable-today in-source and in the record, and **never
claim "the leg is gated by chip ID"** (v1.22 C-5 overclaim class).

### The unreachable `address-line` arm (**MEDIUM, new**)
`classify_fingerprint`'s address-line branch requires `cmp_len > 256` (`:199`). The SDP leg's region
is exactly 256 ⇒ that label is **unreachable** for this leg. A test asserting it would be
unreachable-green — the trap this project has hit before (v1.23 P129/P130).

### `write -b` / "erase" wording (**MEDIUM**)
Protocol `0x0D` has **no erase operation at all**; the recovery word is **"rewrite"**. But the report
legitimately contains "erase" three ways (§2.4) — a whole-report grep is RED on correct text.

### Evidence Ceiling smoothing (**CRITICAL, non-technical**)
A locked die is unrepresentable in either repo's stubs. **No fixture in this phase simulates real
inhibition** — fixtures pin the host's *response* to a scripted read-back. The causal claim *"the lock
inhibited the write"* is **NOT provable this milestone**. Every artifact this phase produces must say
so; `sdp_honesty.unreadable_state_caveat()` exists to carry it.

---

# §7 — Project Constraints (from CLAUDE.md)

**Meta `/workspaces/CLAUDE.md`:** the repo tracks only `.planning/` and `.claude/`; neither sub-repo
is committed here. `firestarter/` (firmware) is **not touched at all** by this phase — host-only, no
lockstep, no `.hex` re-cut. Constants/flag bits are duplicated between
`firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h` — **this phase
adds no wire constant** (the four new op strings are engine-local, per `chip_test.py:302-308`), so no
firmware-header sync is triggered.

**`firestarter_app/CLAUDE.md`:** tooling gate is `ruff check` + `ruff format --check` + `mypy`
(strict on 8 modules per Phase 42 D-06, plus `sdp_honesty` per Phase 132 D-02) +
`pytest --cov-fail-under=70`, all enforced by `.github/workflows/ci.yml`.
`firestarter/data/chip_database.json` is generated — **do not edit by hand**.
`eprom_operations.py` is DELIBERATELY EXCLUDED from the strict island (GATE-1.8d ring-fence) — and is
additionally ring-fenced against *any* edit by the operator decision of 2026-08-03 (`FUT-MYPY-02`).

**Project skills:** `.claude/skills/` is empty in this repo [MEASURED: `ls .claude/skills/` returns
nothing] — no project-skill patterns to account for.

---

# §8 — Validation Architecture

*(`workflow.nyquist_validation` is absent from `.planning/config.json` ⇒ treated as **enabled**.)*

## Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (+ `pytest-cov`, `syrupy` snapshots — 30 snapshots) |
| Config file | `firestarter_app/pyproject.toml` (`[tool.pytest.ini_options]`, `addopts = "-ra -q"`) |
| Quick run | `.venv/ci-replica/bin/python -m pytest tests/<file> -o addopts="" -q` |
| Full suite | `.venv/ci-replica/bin/python -m pytest tests/ -q` — **1338 passed in 143 s**, 81.84 % |
| CI parity | `tools/ci_parity.sh` (4 legs) · `tools/ci_replica_venv.sh` (5 legs, the **only** local path to a real mypy count) |

⚠ **Always pass `-o addopts=""`** — `addopts` is `-ra -q`, and doubling `-q` suppresses the count
line, making a green run look contentless (known trap).
⚠ `tools/ci_parity.sh` has **no no-board leg** — the no-board condition is ambient. Record the board
state; do not claim a leg.
⚠ Leg 1 points `FIRESTARTER_FW_ROOT` at an **empty dir** — the devcontainer's sibling layout otherwise
masks CI-only test defects. Run it before any push.

## Phase Requirements → Test Map

| Req | Behaviour | Type | Automated command | Exists? |
|-----|-----------|------|-------------------|---------|
| LEG-01 | 43 ALLOW chips derive 6 SDP steps; **no new CLI option** | unit | `pytest tests/test_chip_test_sdp_leg.py -k "derive and allow" -o addopts=""` | ❌ Wave A |
| LEG-02 | 41 REFUSE chips get 6 NA steps carrying `sdp_capability()`'s reason | unit | `… -k "derive and refuse"` | ❌ Wave A |
| LEG-03 | A≠B at **every** byte; neither all-`0x00`/all-`0xFF`; B ≠ `generate_pattern(region)` | unit | `… -k "pattern_b"` | ❌ Wave A |
| LEG-04 | B→verify→A→verify before any lock | unit | `… -k "baseline_transition"` | ❌ Wave B |
| LEG-05 | Verdict comes from read-back equality, never the write's bool | unit | `… -k "oracle_readback"` | ❌ Wave B |
| **LEG-06** | write succeeds after lock ⇒ **BAD** ⇒ **exit 1** | unit + CLI | `… -k "lock_leaked"` **and** `pytest tests/test_dev_test_cmd.py -k "exit" -o addopts=""` | ❌ Wave B + C2 + E2 |
| LEG-07 | partial read-back change ⇒ BAD (gh#11) | unit | `… -k "partial_readback"` | ❌ Wave E1 |
| LEG-08 | 4 degenerate fixtures (empty / short / all-`0x00` / all-`0xFF`) never read as equality | unit ×4 | `… -k "degenerate"` | ❌ Wave E1 |
| LEG-12 | `HELD`/`NOT-HELD`/`NOT-RUN(reason)` in **both** surfaces; **no boolean anywhere** in `to_dict()` | unit + CLI | `pytest tests/test_diagnostic_report.py -k "hold" -o addopts=""` | ❌ Wave C1 + E3 |
| LEG-13 | NA/SKIPPED oracle drops N-of-M (M 4→10) | unit | `pytest tests/test_chip_test.py -k "count_applicable and sdp" -o addopts=""` | ❌ Wave E2 (**pin only**) |
| LEG-14 | scoped constants: "rewrite" present, "erase" absent, + planted-violation non-vacuity leg | unit | `pytest tests/test_sdp_recovery_wording.py -o addopts=""` | ❌ Wave E4 (new file) |
| LEG-16 | no-op-write fixture ⇒ baseline step BAD | unit | `… -k "dead_write_path"` | ❌ Wave E1 |
| LEG-17 | R1…R6 (+R7): `sdp_lock.assert_not_called()` **and** a visible `NOT-RUN` reason | CLI ×6 | `pytest tests/test_dev_test_cmd.py -k "laundering" -o addopts=""` | ❌ Wave E2 |
| LEG-18 | gh#20 finding recorded; backlog item filed with an owner | doc | manual — record + `gh issue`/backlog check | ❌ Wave F |
| — | **op-parity gate green** (LEG-15 stays ticked) | unit ×7 | `pytest tests/test_op_registration_parity.py -o addopts=""` | ✅ exists — **must stay green through Wave A** |
| — | Phase 133's LEG-09/10/11 proofs unchanged | unit | `pytest tests/test_chip_test_sdp_leg.py -o addopts=""` | ✅ **regression floor** |

## Sampling rate

- **Per task commit:** `pytest tests/test_chip_test_sdp_leg.py tests/test_op_registration_parity.py -o addopts="" -q` (~10 s). The parity module is in *every* commit's quick set because it fails at **collection**, not at assertion — a slow-to-notice RED otherwise.
- **Per wave merge:** `tools/ci_replica_venv.sh` (all 5 legs). Record `mypy errors: N (watermark: 35)` and `checked N source files` **every time** — headroom is 2.
- **Phase gate:** `tools/ci_parity.sh` **and** `tools/ci_replica_venv.sh` both green, plus the before/after CI-parity record (`134-CI-PARITY.md`, the 131/133 shape), **before** `/gsd-verify-work`.

## Non-vacuity obligations (a pre-authored gate proves nothing until it is seen to pass)

This project has shipped unreachable-green gates twice (v1.23 P129/P130). Each of these must be
observed RED once, then restored **byte-identically**:

1. **P-01:** make B = `generate_pattern(region)` → the every-byte assertion must fail.
2. **LEG-06:** invert the OK/BAD arms → **two** tests must go red (D-03's polarity pin), not one.
3. **LEG-16:** make the fixture's write real → the baseline step must go OK, failing the fixture's test.
4. **LEG-14:** plant a constant saying "erase" → the scoped grep must fail.
5. **D-14:** revert the precedence to `max` → the mixed-run exit-1 test must fail.
6. **D-08:** remove the gate-set membership → a dead-write-path run must be observed emitting `sdp_lock`.
7. **Parity gate:** the existing `test_altered_registry_copy_fails_parity_non_vacuous` (`:753`) already
   covers registries; add nothing, but confirm it still passes after `_ALL_OPS` grows to 13.

## Wave 0 gaps

- [ ] `tests/test_sdp_recovery_wording.py` — LEG-14's scoped constant grep + planted-violation leg (new file)
- [ ] Degenerate-read-back fixtures ×4 and the dead-write-path operator double — LEG-08, LEG-16
- [ ] A synthetic nonzero-`chip-id` DB entry fixture — D-17's R1/R2 causal chain
- [ ] No framework install needed; no `conftest.py` change expected beyond reusing `make_app_context`
      (`tests/conftest.py:229`) and `app_context` (`:325`)

---

# §9 — Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python (devcontainer) | dev loop | ✓ | 3.12 | — (masks CI py3.9/3.11) |
| CI-replica interpreter | trustworthy mypy count | ✓ | **3.11.15**, numpy absent | none — devcontainer mypy exits 2 against numpy |
| mypy | watermark gate | ✓ | **2.3.0** | — |
| ruff | lint/format gate | ✓ | legs 3 green | — |
| pytest + pytest-cov + syrupy | suite | ✓ | 1338 pass, 30 snapshots | — |
| `gh` CLI (read-only) | gh#20 triage | ✓ | issue #20 fetched | — |
| **Arduino hardware / a real AT28C part** | causal proof of inhibition | **✗ and permanently** | — | **None. Evidence Ceiling — not provable this milestone.** |
| firmware repo (`firestarter/`) | — | n/a | — | not touched |

**Missing with no fallback:** real silicon. This is the Evidence Ceiling, not a gap to close.
**Note:** `gh workflow run` (dispatch) is blocked by the auto-mode classifier — read-only `gh run`/
`gh issue view` works. No CI dispatch is needed by this phase.

---

# §10 — Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|-------|---------|---------------|
| A1 | `sdp-unlock` should join the **baseline**-gate set (not the destructive one), rendering SKIPPED when the baseline gate closed | §4.1 | A closed-baseline run emits an unlock at a never-locked part and reports `OK` — a P-06 emission-claim-as-state-claim |
| A2 | The double-fire fix is `cleanup.remove(handle)` on a **successful explicit** unlock | §4.2 | Either two unlock emissions (endurance + 133 D-11's rejected shape) or a stranded lock if the wrong branch de-registers |
| A3 | D-15's floor composes **after** D-14's precedence, and BAD ≻ the NOT-RUN floor | §4.6 | A run that is both BAD and NOT-RUN exits 2, re-creating the laundering D-14 removes; criterion 2's "exit 1" fails |
| A4 | The four new ops all join `_DESTRUCTIVE_OPS` and none join `_MULTI_RUN_OPS`/`_SDP_OPS` | §3, §4.2 | Exemption-row count wrong (12 vs some other N); a write-shaped op ungated by the chip-ID gate |
| A5 | The new leg dispatch arm is placed **after** `_dispatch_step`'s existing `_SDP_OPS` arm 5 | §2.3 | `test_shipped_ops_never_reach_sdp_arm` (133's D-13b sentinel) breaks |
| A6 | A new `_SDP_LEG_OPS` frozenset should be added to `_REGISTRY_CONSTANT_NAMES` and `_POLICED_REGISTRIES` (count 6→7) | §1.8, §4.2 | `_dispatch_step`/`run_plan` appear not to cover the new ops ⇒ 4–8 spurious exemption rows, or the new frozenset silently unpoliced |
| A7 | Op names are exactly `write-baseline-b`, `write-baseline-a`, `write-inhibited`, `write-restored` | throughout | The `_MULTIWORD_OP_VALUES` substring set differs; D-09's forbidden-substring list changes |
| A8 | The `HELD` derivation lives in `chip_test.py` as a pure function called from `cli_handlers.py` | §4.4 | If placed in `DiagnosticReport`, `test_non_registry_still_has_no_ops` goes RED |

---

# §11 — Sources

### Primary (HIGH — measured this session against `firestarter_app@57e8eb5`)
- `firestarter/chip_test.py`, `diagnostic_report.py`, `cli_handlers.py`, `eprom_operations.py`,
  `sdp_capability.py`, `sdp_honesty.py`, `constants.py` — read directly; every line cite verified by
  `grep -n` / `Read`.
- `tests/test_op_registration_parity.py` (822 lines, read in the relevant 5 blocks),
  `tests/test_dev_test_cmd.py`, `tests/conftest.py`, `pyproject.toml`, `tools/check_mypy_watermark.py`,
  `tools/ci_replica_venv.sh`, `tools/ci_parity.sh`.
- Executed: `tools/ci_replica_venv.sh` (PASS, 5/5), `check_mypy_watermark.py` (33/35, 124 files),
  `pytest tests/test_dev_test_cmd.py -k "marginal or exits"` (5 passed), plus three ad-hoc
  measurement scripts (pattern A/B, the ALLOW population + representative plan, the marginal-run
  verdict set).
- `gh issue view 20 --repo henols/firestarter_prom` — full body captured.

### Secondary (HIGH — project record, cited by §/P-number never by phase heading)
- `.planning/phases/134-.../134-CONTEXT.md` (19 decisions, 4 corrections) — the governing input.
- `.planning/REQUIREMENTS.md` §"⚠ Evidence Ceiling" (L14-40), §LEG (L186-276).
- `.planning/research/PITFALLS.md` **P-01** (L39), **P-02** (L82), **P-03** (L131, prevention 4
  OVERTURNED), **P-04** (L176), **P-05** (L227), **P-06** (L255), **P-07** (L287), **P-08** (L317),
  **P-09** (L344), **P-10** (L389).
- `.planning/research/FEATURES.md` §1.1-1.4 (L40-108), §2.1-2.6 (L112-172), §3.1-3.2 (L176-199).
  ⚠ **§1.4's "minimal extension" framing is superseded by §4.3 of this document.**
  ⚠ **§1.1's "step 1 should NOT get a new op" is overturned by CONTEXT.md D-07.**
- `.planning/research/STACK.md` §"Trap 1" (L422).
- ⚠ `.planning/research/SUMMARY.md`'s phase headings are **OFF BY ONE** — its §"Phase 133" IS this
  phase. Never cite it by phase heading.

### Not used (deliberately)
- `.planning/codebase/TESTING.md` — severely stale ("the project has **no** Python unit tests",
  `/home/henrik/dev/...` paths). Measured instead: 86 test files, 1338 passing.
- `.planning/notes/sdp-surface-retirement-and-behavioral-proof.md` — step table invalidated by
  research; line numbers superseded.

---

# §12 — Metadata

**Confidence breakdown**

| Area | Level | Reason |
|------|-------|--------|
| Corrected anchor table | **HIGH** | Every row produced by `grep -n` against the working tree; 4 drifts + 1 non-existent symbol identified |
| Exact code shapes | **HIGH** | Quoted verbatim from the files, not paraphrased |
| Budget (mypy 33/35, 124 files, 1338 tests, 81.84%) | **HIGH** | `ci_replica_venv.sh` executed; all four CONTEXT.md numbers reproduced |
| P-01 / P-02 / D-05 arithmetic | **HIGH** | Executed against the installed module |
| D-14 audit discharge | **HIGH** | Full `exit_code == 2` census + the marginal case's verdict set reproduced |
| Parity-gate findings (§1.8, §4.2, §4.4, §4.5) | **HIGH** | Read the mechanism (`_measure_op_vocabulary`, `_op_names_referenced_in`, the module-level assert) directly |
| Wave structure / file→req matrix | **MEDIUM** | File assignments MEASURED; the requirement split within a file is INFERRED |
| OQ-1 (`sdp-unlock` under the baseline gate) | **MEDIUM** | Mechanism measured; the *choice* is a genuine open decision (A1) |
| OQ-2 (de-registration shape) | **MEDIUM** | Registry API measured exactly; the fix shape is INFERRED (A2) |
| Op names | **LOW** | Taken from CONTEXT.md D-06; not yet in code (A7) |

**Research date:** 2026-08-04
**Valid until:** the next commit to `firestarter_app` on `gsd/v1.30-sdp-surface-retirement`. Every
line number in §1 is anchored to **`57e8eb5`** — re-run the `grep -n` census if HEAD moves before
planning completes.
