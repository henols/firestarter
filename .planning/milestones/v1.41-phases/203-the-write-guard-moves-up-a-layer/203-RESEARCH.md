# Phase 203: The write guard moves up a layer - Research

**Researched:** 2026-09-21
**Domain:** Host-side pre-write blank guard + `write --verify`, in `firestarter_app` (Python 3.11 CLI). App-only, bench-no.
**Confidence:** HIGH for every mechanical fact (all read from live source this session); MEDIUM for the derived session-cost arithmetic; the design forks are reported, not decided.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Copied verbatim from `.planning/phases/203-the-write-guard-moves-up-a-layer/203-CONTEXT.md`.
**Do not re-derive or re-litigate these. Seventeen decisions, D-01..D-17.**

- **D-01:** **The guard's coverage is defined by what the firmware pre-flights today, not by
  `FLAG_CAN_ERASE` alone.** … **The guard therefore applies to exactly: `0x07`, `0x08`, `0x0B`,
  `0x06`, `0x10`** — and within those, a part whose erase actually ran is exempt. SRAM/FRAM and
  `0x05` are **named** exemptions with their reasoning at the site, not accidents of a flag test.
  — **Reversibility:** costly — the predicate is the whole safety net after Phase 205, and its test
  is the only thing that detects a later drift.
- **D-02:** **WRITE-02 must be amended before planning** … The replacement obligation is **stronger,
  not weaker**: the test pins the **exact guarded set** and fails if it **narrows or widens**. Amend
  both `.planning/REQUIREMENTS.md` WRITE-02 and `.planning/ROADMAP.md` Phase 203 success criterion 2.
  *(Both amendments are ALREADY LANDED — commit `7e0901e4`, verified this session. Nothing left to do.)*
- **D-03:** **`--skip-erase` re-arms the guard on an erase-capable part.** The exemption's whole
  premise is "the erase immediately above the check already guarantees blank". `--skip-erase` makes
  that premise false while leaving `FLAG_CAN_ERASE` set. … This narrows the exemption, which D-02's
  test permits by construction.
- **D-04:** **The guard reads the write's region only, on every guarded family.** `address` →
  `address + len(input_file)`. This deliberately **diverges from** `flash_nor_unlock.cpp` /
  `flash_intel.cpp`, which blank-check the whole device today. Record it as a deliberate, measured
  improvement in the phase record — not as an incidental difference.
- **D-05:** **An unclassifiable part is guarded, not exempted.** A wire dict with no `algorithm` key
  or an unrecognised protocol id **fails closed** — it gets the read. This follows
  `jp5_gate.require_acknowledged` and `sdp_capability`, and deliberately **not**
  `flash4_erase_gate.is_flash4`. The reason the polarities differ must be stated at the site.
- **D-06:** **The policy lives in a new pure-predicate module**, following the four in-repo siblings
  `jp5_gate.py`, `flash4_erase_gate.py`, `sdp_capability.py` and `page_size_gate.py`: a wire dict in,
  a decision out, no I/O, no serial, no environment reads. … Reuse
  `flash4_erase_gate.FLASH4_PROTOCOL_ID` rather than introducing a second 0x05 constant.
  — **Reversibility:** reversible — a module boundary, not a contract.
- **D-07:** **The guard lives inside `EpromOperator.write_eprom`**, not in `cli_handlers.write`.
  Every caller inherits it. Consequences: `dev write-cycle` erases before every write → exempt;
  `dev test` already passes `FLAG_SKIP_BLANK_CHECK` for its monotonic-masked UV targets, so **its UV
  write shortcut keeps working unchanged** provided the guard honours that flag host-side; the
  `dev test`-vs-`write` divergence is thereby **preserved exactly**, neither widened nor closed.
- **D-08:** **The guard runs after every pure pre-connect gate and before the write's own
  `_operation_context`.** Existing order: `require_acknowledged` → `require_page_size` →
  `require_page_alignment` → `os.path.getsize` → connect. The guard is a serial operation, so it
  cannot join the pure gates; it sits immediately after them.
- **D-09:** **`-f`/`--force` does not bypass the guard.** `-b`/`--no-blank-check` is the documented
  way past it, per WRITE-03. Preserving today's behaviour.
- **D-10:** **Host-voiced, one line, no remedy clause, address and value included.** Shape:
  `Refusing write to W27C512: not blank at 0x008000, v: 0xAB.` — exact wording and capitalisation are
  Claude's discretion within that content. Three properties are decided: it names the **host** as the
  refuser; it carries the **first non-blank address and its value** (a deliberate, recorded exception
  to Phase 202's D-13); it carries **no remedy clause** — no mention of `-b`.
- **D-11:** **The refusal prints that line and nothing else.** The guard aborts at the first non-blank
  byte, so the range is always one byte and the bucket would be classified from a one-byte sample.
  Terse output is also a standing operator preference (v1.40 Phase 200 UAT, commit `b3a777e`).
- **D-12:** **The refusal text belongs in the predicate module**, built from a format constant so a
  test asserts the exact sentence rather than a substring of a log line.
- **D-13:** **`--verify` opts the invocation into Phase 202's `0` / `1` / `2` exit-code contract;
  plain `write` keeps `0` / `1` unchanged.** Plain `write`: a guard refusal exits **1**; a transport
  failure exits 1, as today. `write … --verify`: **0** verified, **1** write failed or comparison
  mismatched, **2** transport or hardware failure anywhere in the invocation, including the guard
  read. The cost — one command with two contracts — is accepted and **must be stated in the
  `--verify` help text**. — **Reversibility:** one-way.
- **D-14:** **One combined verdict line under `--verify`; the word "successful" never appears on a
  `--verify` run.** `--verify` suppresses the plain `Write to X successful (t).` line and prints a
  single terminal line — verified / landed-but-did-not-verify / failed. Exact wording is Claude's
  discretion; the three-way distinction is not.
- **D-15:** **`write --verify` accepts `--full`**, with the same meaning it has on `verify` and
  `blank`.
- **D-16:** **`--verify` compares the written region only** — the same `address` → `address + len`
  region the write touched and the guard read. Not the whole chip.
- **D-17:** **Three open/reset cycles per guarded `write --verify` are accepted for this phase, and
  the added wall-clock is measured and recorded.** **203 must record the measured added wall-clock in
  its phase record**, so Phase 206's SESS-02 has a real before-figure.

### Claude's Discretion

- Exact wording and capitalisation of the refusal line (within D-10's content) and of the three
  `--verify` verdict lines (within D-14's three-way distinction).
- The predicate module's name, and whether the guarded set is expressed as a protocol allowlist or as
  a named predicate over the wire dict — provided D-02's pin-the-exact-set test holds.
- Whether the guard read shows a progress bar.
- Whether the measured session cost in D-17 is taken from a bench run or a harnessed
  connect-cost measurement (`tests/test_connect_cost_harness.py` exists).
- The mechanism of the refusal — a typed exception through `map_typed_errors` (the shape the four
  sibling gates use) versus a `False` return — provided D-13's exit codes come out right.

### Folded Todos

- **`2026-09-16-reject-negative-write-start-address.md`** — fold the **host half only**. The firmware
  half (`simple_strtoul`) is a `firestarter_fw` change and this phase is app-only and bench-no.

### Deferred Ideas (OUT OF SCOPE)

- **Collapsing the three port opens into one leased session.** Best home: Phase 206, SESS-01.
- **The firmware half of the negative-address todo.** Best home: Phase 205.
- **CLI-wide exit-code consistency.** Backlog.
- Not in this phase: removing `FLAG_SKIP_BLANK_CHECK`, `mem_util_blank_check*` or `MSG_ERR_NOT_BLANK`
  (Phase 205); the serial session lease (Phase 206); making `--verify` the default (REQUIREMENTS D-3);
  wiki documentation (REL-04, Phase 207).
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description (from REQUIREMENTS.md, WRITE-02 as amended 2026-09-21) | Research Support |
|----|-------------|------------------|
| WRITE-01 | before writing to a part that does not carry `FLAG_CAN_ERASE`, the host reads the target region and refuses the write if it is not blank, naming the first non-blank address and its value. | §4 (the guard's placement and region), §5 **the byte value is NOT available from `CompareResult` today** — this is the single hardest mechanical fact in the phase. |
| WRITE-02 | the guard applies to exactly `0x07`, `0x08`, `0x0B`, `0x06`, `0x10`; within those a part whose erase actually ran is exempt; SRAM/FRAM and `0x05` are named exemptions; a test pins that exact guarded set and fails if it **narrows or widens**. | §3 (firmware table re-verified line-by-line), §6 (database protocol census — the pinning test's real population), §7 fork A (allowlist vs denylist; the D-01/D-05 boundary case) |
| WRITE-03 | `write -b` / `--no-blank-check` skips the host check and still does not skip erase. | §4.3 (`_build_op_flags` polarity, `FLAG_SKIP_BLANK_CHECK = 0x08`), §4.4 (effective-flags derivation) |
| WRITE-04 | `write --verify` runs a read-back comparison of the written region through the CMP engine, and reports through it. | §5 (`_drive_region_compare` contract), §7 fork C (CLI-tier vs operator-tier placement) |
| WRITE-05 | a `write --verify` whose comparison fails exits non-zero and says the write landed but did not verify — never "successful". | §7 fork C, §8.2 (`ClickException.exit_code == 1` cannot express D-13's exit 2 — decides the refusal-mechanism fork) |
| WRITE-06 | a non-blank, non-erasable part accepts a region write into a blank region … the test must exercise the host path and fail if the host refuses a blank region on a non-blank part. | §2 — **the whole of it.** The two tests that claim this today exercise zero product code. |
</phase_requirements>

---

## Summary

Every mechanical claim below was read from live source in this session, not recalled. The tree is
green at the start of the phase: `ruff check`, `ruff format --check` and `mypy` on the strict list all
pass, and `pytest tests/` is **2216 passed in 196 s** on `.venv311` (Python 3.11.16), with **85.80 %**
coverage against a 70 % floor.

Three findings dominate the plan.

**First, and most expensive: the value in "not blank at 0x008000, v: 0xAB" does not exist anywhere in
Phase 202's engine.** `CompareResult` (`firestarter/compare.py:95-160`) carries `first_offset` but no
actual byte, and `render_compare_lines` states in its own docstring that it "Emits no expected value
and no actual value anywhere". The `expected(offset, length)` pull callback never sees the actual
payload, so no closure trick recovers it. WRITE-01 and D-10 therefore require either a new field on
the accumulator or a second compare implementation — and the second option is forbidden by the
standing one-divergence-implementation rule. §5 lays out the three routes.

**Second: `_drive_region_compare` cannot be "reused unchanged" and still satisfy D-11.** It
unconditionally does `for line in render_compare_lines(result): logger.info(line)`
(`eprom_operations.py:2316-2317`), and default log level is `INFO`
(`cli_handlers.py:113`). A guard refusal would therefore print `Mismatch 0x008000-0x008000 (1 bytes)`
plus a bucket line before the host's own refusal — exactly the three-line output D-11 forbids.

**Third: `tests/fake_chip.py` is worse than CONTEXT describes, in a way that changes the fix.**
`FakeChip` does **not** subclass `EpromOperator` — it is a standalone duck-typed replacement for the
whole operator (`fake_chip.py:47`). `WriteInitPreflightChip.write_eprom` (`:282`) therefore does not
"override" the real method; the real `write_eprom` is simply never on the call graph, and
`super().write_eprom(...)` at `:310` resolves to `FakeChip.write_eprom` at `:138`. The two tests that
WRITE-06 and criterion 5 name — `test_write_into_blank_region_of_non_blank_part_succeeds`
(`tests/test_eprom_operations.py:342`) and `test_write_into_non_blank_region_is_still_refused`
(`:369`) — test the double against itself and execute zero lines of `firestarter/`. The fix is not
"stop shadowing the method"; it is "build a second harness that drives the real operator", and §2
shows there are already three working examples of exactly that harness in the suite.

**Primary recommendation:** plan the guard as (1) a new pure-predicate module keyed **only on
`algorithm` and `flags`** — the wire dict carries nothing else this phase can use (§4.2) — (2) an
additive `first_actual` field on `CompareAccumulator`/`CompareResult` plus an additive
render-suppression switch on `_drive_region_compare`, and (3) a WRITE-06 test built on the
`_drive_write_eprom_for_ack_check` harness shape (`tests/test_eprom_operations.py:2244`), which
already drives the genuine `EpromOperator.write_eprom` through a `_FakeSerial` and gives the
command-ordering assertion criterion 1 needs for free.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Deciding *whether* a part is guarded | Pure predicate module (new, 5th sibling) | — | D-06; wire dict in, decision out, no I/O. The four siblings establish the tier. |
| Deciding *whether this invocation* is exempt (erase ran / `-b`) | Same predicate module | `write_eprom` supplies effective flags | The flag derivation is `db flags | operation_flags` and belongs beside the protocol test, not scattered. |
| Performing the guard read | `EpromOperator.write_eprom` (operator tier) | `_drive_region_compare` | D-07/D-08. It is a serial operation; it cannot live in a pure module and must not live in the CLI tier. |
| Comparing bytes | `compare.py` `CompareAccumulator` | — | Standing rule: exactly one divergence implementation. |
| Rendering the refusal sentence | Predicate module (format constant) | — | D-12, following `flash4_erase_gate.refusal_text`. |
| Mapping the verdict to a process exit code | `cli_handlers.write` | `map_typed_errors` | D-13. `sys.exit(...)` only ever appears in the CLI tier. |
| `--verify` comparison | `_drive_region_compare` via operator tier | `verify_eprom` (if the CLI-tier fork is taken) | D-15/D-16 — one call, same engine. |
| Refusing a negative start address | Pure gate, pre-connect | — | Folded todo; it is an input-validation refusal and must fire before the port opens. |

---

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md` and `firestarter_app/CLAUDE.md`, both read this session.

| # | Directive | Source | Bearing on this phase |
|---|-----------|--------|-----------------------|
| C-1 | Milestone work forks off `beta`; **never commit to `beta` or `main`**. Current branch is `gsd/v1.41-verification-moves-to-the-host-activated-2026-09-20`. | `/workspaces/CLAUDE.md` § Milestone close | Every commit in this phase lands on the milestone branch, inside the `firestarter_app` submodule. |
| C-2 | **A push to `beta` in `firestarter_app` PUBLISHES to PyPI.** No path filter; a docs-only push publishes. A PyPI version can never be reused. | `/workspaces/CLAUDE.md`; `firestarter_app/CLAUDE.md` § What CI runs | No plan task may push `beta`. |
| C-3 | CI = Python **3.11**, `ruff check firestarter/ tests/`, `ruff format --check firestarter/ tests/`, `pytest tests/ --cov=firestarter --cov-fail-under=70`, entry-point smoke test. | `.github/workflows/ci.yml` (read verbatim) | The exact gate the plan's verification legs must reproduce. |
| C-4 | **`mypy` is NOT a CI gate.** It runs only in the local `pre-commit` config (`ruff-check` → `ruff-format` → `mypy`). | `firestarter_app/CLAUDE.md:39-40`; `.pre-commit-config.yaml` | CONTEXT says "mypy is strict on `cli_handlers`" — true as *config*, but a mypy break will **not** be caught by CI. The plan must run mypy explicitly if it wants the guarantee. |
| C-5 | `ruff` selection is `E, F, I, UP` with `E501` ignored; a `# noqa` for any other code is **inert**. Line length 88, `target-version = "py311"`. | `pyproject.toml [tool.ruff.lint]` | No `# noqa: B…`, `# noqa: SIM…` etc. `# noqa: E501` and `# noqa: UP…` are the only live forms seen in-tree. |
| C-6 | Comments in product source are **allowed again** (rule removed 2026-09-19). | `/workspaces/CLAUDE.md` | D-01, D-03, D-05, D-10 and amended WRITE-02 all require reasoning **at its site in the code**. This is now permitted and required. |
| C-7 | Never write GSD/`.planning` provenance into product source visible to users; Click docstrings **are** user-facing `--help` text. | memory `reference_click_docstrings_are_user_facing_help_text` | The `write` docstring edit is a user-facing change pinned by two snapshots. |
| C-8 | Firmware source is read as **evidence only**; no firmware file is modified. | phase brief; CONTEXT `<domain>` | §3's firmware table is evidence. No `firestarter_fw` commit belongs in this phase. |

---

## 1. Verified starting state

| Fact | Value | Provenance |
|---|---|---|
| Full suite, Python 3.11 | **2216 passed in 196.44 s** | `[VERIFIED: .venv311/bin/python -m pytest tests/ -o addopts="" -q`, run this session] |
| Coverage | **85.80 %** TOTAL, 6371 statements, 905 missed; floor 70 % | `[VERIFIED: pytest --cov=firestarter --cov-fail-under=70`, run this session] |
| `ruff check firestarter/ tests/` | `All checks passed!` | `[VERIFIED: .venv311/bin/ruff check`, this session] |
| `ruff format --check` | `147 files already formatted` | `[VERIFIED: this session]` |
| `mypy` on `cli_handlers`, `compare`, `flash4_erase_gate` | `Success: no issues found in 3 source files` | `[VERIFIED: .venv311/bin/python -m mypy`, this session] |
| Interpreter | `.venv311` = **Python 3.11.16**; devcontainer default `python3` = **3.12.14** | `[VERIFIED: --version`, this session] |
| Tool versions in `.venv311` | ruff 0.16.8, mypy 2.3.1, pytest 9.1.1, click 8.5.0, syrupy present | `[VERIFIED: this session]` |
| `.venv311` install mode | editable, resolving to `/workspaces/firestarter_app/firestarter/__init__.py`, version `3.0.0b48` | `[VERIFIED: python -c "import firestarter"`, this session] |
| `.venv` | **broken** — `bin/` exists but no `bin/python`. Do not use it. | `[VERIFIED: ls .venv/bin`, this session] |
| `.planning/config.json` | `workflow.nyquist_validation: false` → no Validation Architecture section; `parallelization: false`; `commit_docs: true` | `[VERIFIED: .planning/config.json]` |
| Knowledge graph | **STALE** — built 2026-09-18, 73 h old, **221 commits behind** `7e0901e`. Treat any graph-derived relationship as approximate. Nothing in this document comes from it. | `[VERIFIED: gsd-tools graphify status`, this session] |

### The exact invocations that work in this repo

```bash
cd /workspaces/firestarter_app

# full suite, CI interpreter — DO NOT use the devcontainer's python3 (3.12)
.venv311/bin/python -m pytest tests/ -o addopts="" -q

# a focused subset (1.0 s for the two gate modules)
.venv311/bin/python -m pytest tests/test_flash4_erase_gate.py tests/test_page_size_write_refusal.py -o addopts="" -q

# the CI coverage leg verbatim
.venv311/bin/python -m pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70

# the two lint gates CI runs, verbatim
.venv311/bin/ruff check firestarter/ tests/
.venv311/bin/ruff format --check firestarter/ tests/

# mypy — NOT a CI gate; run it deliberately
.venv311/bin/python -m mypy firestarter/cli_handlers.py firestarter/compare.py
```

`-o addopts=""` matters: `pyproject.toml` sets `addopts = "-ra -q"`, and adding another `-q` on the
command line suppresses the pass/fail count line entirely. `pytest-timeout` is **not installed** —
`--timeout=…` fails with "unrecognized arguments". `[VERIFIED: measured both this session]`

---

## 2. Trap 1 — `tests/fake_chip.py` and the WRITE-06 / criterion-5 test

### 2.1 What the double actually is

CONTEXT says `WriteInitPreflightChip` "overrides `EpromOperator.write_eprom` wholesale". The measured
reality is stronger:

> `class FakeChip:` — `tests/fake_chip.py:47`
> `class WriteInitPreflightChip(FakeChip):` — `tests/fake_chip.py:253`

`[VERIFIED: firestarter_app/tests/fake_chip.py:47,253]`

There is **no inheritance from `EpromOperator` anywhere in the file**. `FakeChip` is a duck-typed
stand-in for the entire operator, injected through `make_app_context(eprom_operator=…)`
(`tests/conftest.py:226-231`, whose signature is typed
`eprom_operator: EpromOperator | Mock | FakeChip | None = None`). `[VERIFIED: tests/conftest.py:226-231]`

So `WriteInitPreflightChip.write_eprom` (`:282-317`) does not shadow the product method — the product
method is simply absent from the call graph. Its `super().write_eprom(...)` at `:310` resolves to
`FakeChip.write_eprom` at `:138`.

The practical consequence is identical to CONTEXT's, but the *fix* is different: there is nothing to
un-shadow. A second harness has to be built.

### 2.2 What it models, and why

`WriteInitPreflightChip.write_eprom` models exactly three firmware behaviours:

1. `self.write_flags_seen.append(operation_flags)` — the UV-03 legs assert on this list.
2. The region-scoped pre-flight: `start = _parse_addr_or_size(address_str) or 0`,
   `end = start + os.path.getsize(input_file_path)`, then
   `if not (operation_flags & FLAG_SKIP_BLANK_CHECK) and not self._is_blank(start, end)`.
3. The **non-raising** refusal contract: it sets `last_firmware_error_code = MSG_ERR_NOT_BLANK` and
   returns `False`, because the real `_run_state_machine` catches `EpromOperationError` and returns
   `(False, str(e))` rather than propagating (`eprom_operations.py:674-681`). The class docstring at
   `:254-266` says this explicitly and calls a raising double "NOT firmware-faithful".

`[VERIFIED: firestarter_app/tests/fake_chip.py:254-317]`

### 2.3 Who depends on it — the blast radius of any change

`WriteInitPreflightChip` is imported by exactly four modules:

| Module | Sites | What it asserts |
|---|---|---|
| `tests/test_eprom_operations.py` | `:38` import; `:354`, `:378` construction | The two BLANK-01/BLANK-03 region tests (`:342`, `:369`) — the ones WRITE-06 names |
| `tests/test_chip_test_uv_slot_write.py` | `:81` import; `:112`, `:139`, `:290`, `:338`, `:431` | UV-03 `write_flags_seen` legs; `:118-121` says in as many words that a non-raising double "match[es] the REAL `EpromOperator.write_eprom` contract" |
| `tests/fixtures/report_shapes.py` | `:98` import; `:658` construction | Report-shape fixtures; `:636` relies on the `False`-plus-`last_firmware_error_code` pair |
| `tests/fake_chip.py` | definition | — |

`[VERIFIED: grep -rn "WriteInitPreflightChip" firestarter_app/tests/`, this session]

Plain `FakeChip` is additionally used by `tests/conftest.py`, `tests/test_chip_test.py`,
`tests/test_chip_test_sdp_leg.py` and `tests/test_dev_test_cmd.py`.

**Implication:** `WriteInitPreflightChip` must keep modelling the *firmware* pre-flight for
`test_chip_test_uv_slot_write.py` and `report_shapes.py`. It cannot simply be deleted or repointed.
Whatever the plan does, the double survives; the new host-path test is **additive**.

### 2.4 The harnesses that DO drive the real `write_eprom`

Three already exist in the suite. All three use the same two fixtures and the same
`find_and_connect` patch:

| Harness | Location | Shape |
|---|---|---|
| `_drive_write_eprom_for_ack_check` | `tests/test_eprom_operations.py:2244-2296` | Feeds `MSG_INIT_DONE → MSG_OK_REQ_DATA → MSG_MAIN_DONE → MSG_END_DONE` into `fake_serial`, patches `SerialCommunicator.find_and_connect` with a `side_effect` returning `make_comm()`, constructs a real `EpromOperator(ConfigManager())`, calls `operator.write_eprom(...)`. |
| `_drive_write_for_pulse_override` | `tests/test_pulse_us_override.py:128-167` | Same shape, "adapted to call `write_eprom` DIRECTLY — no `CliRunner` here" |
| the write-progress driver | `tests/test_write_progress.py:162-262` | Same shape again, plus progress-bar capture |

`[VERIFIED: firestarter_app/tests/test_eprom_operations.py:2244-2296; tests/test_pulse_us_override.py:128-167; tests/test_write_progress.py:162-262]`

The two supporting fixtures:

- `fake_serial` → `_FakeSerial` (`tests/conftest.py:133-192`), a `BytesIO`-backed port with
  `read/readline/in_waiting/write/flush/close` and a test-side `feed(data)`.
- `make_comm` (`tests/conftest.py:195-220`), a factory that builds a `SerialCommunicator` via
  `__new__` (bypassing `__init__`, which would open a real port) and wires it to `fake_serial`.

`[VERIFIED: firestarter_app/tests/conftest.py:133-220]`

**One sharp edge in `_FakeSerial`:** `feed()` and `write()` append to the *same* `BytesIO` at the same
`_write_pos`. Host-sent bytes therefore land in the readable stream behind whatever was fed. Existing
tests survive because they feed every frame up front and the host never reads past them. A new test
that feeds frames *between* host writes will desync. Feed the whole script first.
`[VERIFIED: tests/conftest.py:142-186 — `feed` and `write` both seek `self._write_pos`]`

### 2.5 Options for WRITE-06 / criterion 5, with trade-offs

Two are defensible; a third is listed to be rejected explicitly.

**Option A — a new host-path test module, built on the `_drive_write_eprom_for_ack_check` shape.**
Leave `fake_chip.py` untouched. Add e.g. `tests/test_write_blank_guard.py` that:
(a) drives the real `EpromOperator.write_eprom` against a real programmer dict for a guarded,
non-`CAN_ERASE` part (`M27C512`: `algorithm: 7, flags: 0` — §6);
(b) feeds a READ-phase frame script whose payload is blank across the target region, then the
WRITE-phase script, and asserts the write proceeds (criterion 5 / WRITE-06);
(c) feeds a non-blank payload and asserts refusal with no WRITE command ever composed (criterion 1).

- *For:* zero churn on the four existing dependants; the exact existing idiom, three precedents;
  drives genuine product code end to end; the same test object gives §9's ordering assertion.
- *Against:* the frame script for a *read* main phase is more involved than the write scripts the
  three precedents use — `_main_phase_read_data` consumes `MSG_DATA_SENDING` / `MSG_DATA_CHUNK`
  frames and acks each one (`eprom_operations.py:915-1000`). The plan must budget a task for
  building and proving that script. `tests/test_eprom_operations.py` already has read-path drives
  worth copying (grep `_main_phase_read_data` in that file).
- *Risk:* a script that is subtly wrong makes the test pass for the wrong reason. Mitigate by first
  proving the *negative* control fails (a deliberately non-blank payload must refuse).

**Option B — teach `WriteInitPreflightChip` to delegate to the real `EpromOperator.write_eprom`.**
Make the double a genuine `EpromOperator` subclass whose serial layer is faked, so both the host guard
and the modelled firmware pre-flight run.

- *For:* the two existing tests at `:342`/`:369` become real without being rewritten; one artefact.
- *Against:* substantial. `EpromOperator.__init__` takes a `ConfigManager`; every one of the ~12 other
  `FakeChip` methods would have to keep working; `test_chip_test_uv_slot_write.py:118-121` explicitly
  documents the current non-raising contract as the thing being modelled, and the four dependants all
  assume the double is cheap and board-free. High chance of collateral breakage across four modules
  and ~15 call sites.
- *Verdict:* larger than it looks. Not recommended unless the plan explicitly budgets for it.

**Option C (reject explicitly) — assert on `WriteInitPreflightChip` with the guard logic copied into
it.** This is what the suite does today and is precisely why WRITE-06 is untested. Copying the guard
into the double makes the test pass whatever the product does. Name this in the plan as rejected so a
later reviewer does not re-propose it.

**Recommended:** Option A, with a companion task that adds a docstring note at `fake_chip.py:253`
recording that this double models the **firmware** pre-flight only and that the **host** guard has its
own test elsewhere — so the next reader does not mistake the double's green for host coverage.

---

## 3. The D-01 firmware table, re-verified line by line

Every row below was re-read from `firestarter_fw` source this session. The table in CONTEXT D-01 is
**correct in every cell.**

| Protocol | Firmware write-init blank check | Verbatim evidence |
|---|---|---|
| `0x07`/`0x08`/`0x0B` (`configure_eprom`) | **yes**, region-scoped | `eprom.cpp:144-145`: `if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) { mem_util_blank_check_region(handle, handle->address, mem_util_operation_end(handle)); }` |
| `0x06` (`configure_flash_nor_unlock`) | **yes**, whole device, after erase | `flash_nor_unlock.cpp:104-106`: `if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) { mem_util_blank_check(handle); }` |
| `0x10` (`configure_flash_intel`) | **yes**, whole device, after erase | `flash_intel.cpp:94-96`: `if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) { mem_util_blank_check(handle); }` |
| `0x05` (+ `0x35`/`0x39`) | **no** | `flash_5v_page.cpp:68-77`: body contains only the `is_operation_in_progress` guard and the comment "No pre-write blank check: flash4 auto-erases per page during the write loop … FLAG_SKIP_BLANK_CHECK is consequently unread on this protocol" |
| `0x0D` (`configure_eeprom28c`) | **no** | not present in the three blank-checking init bodies above |
| `0x0E`/`0x27`/`0x28`/`0x29` (`configure_sram`) | **no** | `memory.cpp:112-116` dispatches all four to `configure_sram`; no blank check |

`[VERIFIED: firestarter_fw/src/proms/eprom.cpp:129-146; flash_nor_unlock.cpp:73-107;
flash_intel.cpp:72-97; flash_5v_page.cpp:68-77; src/proms/memory.cpp:87-117]`

### 3.1 The erase gate — the mechanical form of D-01's "erase actually ran"

All three blank-checking paths gate their erase identically:

- `eprom.cpp:136-141`: `if (is_flag_set(FLAG_CAN_ERASE)) { if (!is_flag_set(FLAG_SKIP_ERASE)) { eprom_internal_erase(handle); } else { LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE); } }`
- `flash_nor_unlock.cpp:93-103`: same shape
- `flash_intel.cpp:91-93`: `if (is_flag_set(FLAG_CAN_ERASE) && !is_flag_set(FLAG_SKIP_ERASE)) { flash_intel_erase_execute(handle); }`

`[VERIFIED: the three files above, this session]`

**So the host-side exemption predicate is exactly `FLAG_CAN_ERASE set AND FLAG_SKIP_ERASE clear`** —
a static, per-invocation derivation from the effective flags, not an observation of anything. This is
the concrete form of D-01's "a part whose erase actually ran is exempt" and of D-03's re-arming. It is
computable inside `write_eprom` before the port opens.

### 3.2 One constant the D-01 table does not mention: protocol `0x34`

`include/proto_constants.h:22` defines `PROTO_EEPROM_8051BUS 0x34`, but `configure_memory`
(`memory.cpp:87-131`) **never dispatches on it** — it falls through every arm to the terminal
`configure_not_implemented(handle)` at `:130`. `[VERIFIED: firestarter_fw/src/proms/memory.cpp:87-131;
include/proto_constants.h:22]`

So the guarded set of five is complete; `0x34` does not blank-check. §6 shows why this matters anyway.

---

## 4. The host path, pinned

CONTEXT's line numbers were checked against live source. **All of CONTEXT's cited ranges are still
correct** except `cli_handlers.write`, which CONTEXT gives as `733-793` and which is actually
`562-793` (the decorator stack starts at 562; `def write` is at 627).

### 4.1 `EpromOperator.write_eprom` — `eprom_operations.py:2080-2229`

```python
def write_eprom(
    self,
    eprom_name: str,
    eprom_data_dict: dict,
    input_file_path: str,
    operation_flags: int = 0,
    address_str: str | None = None,
    pulse_us: int = 0,
    pin1_hazard_acknowledged: bool = False,
) -> bool:
```
`[VERIFIED: firestarter_app/firestarter/eprom_operations.py:2080-2089]`

The existing gate order, exactly as D-08 describes it:

| Order | Statement | Line | Kind |
|---|---|---|---|
| 1 | `if pulse_us: eprom_data_dict = dict(eprom_data_dict); …["pulse-delay"] = pulse_us` | 2110-2113 | pure |
| 2 | `require_acknowledged(eprom_name, eprom_data_dict.get("bus-config"), "write", pin1_hazard_acknowledged)` | 2115-2120 | pure, raises `Pin1HazardRefusedError` |
| 3 | `require_page_size(eprom_name, eprom_data_dict, "write")` | 2121 | pure, raises `PageSizeUnavailableError` |
| 4 | `require_page_alignment(eprom_name, eprom_data_dict, "write", address_str, input_file_path)` | 2122-2124 | pure, raises `PageAlignmentError` |
| 5 | `try: region_length = os.path.getsize(input_file_path) except OSError: region_length = None` | 2131-2134 | filesystem |
| **→** | **D-08 puts the guard HERE** | **between 2134 and 2136** | **serial** |
| 6 | `with self._operation_context(…, COMMAND_WRITE, …, region_length=region_length) as (cmd_data, buf_size, op_name):` | 2136-2143 | connect |
| 7 | `if not cmd_data: return False` | 2144-2145 | setup-failure |
| 8 | `self._run_state_machine(op_name, main_phase_handler=self._main_phase_send_data, …)` | 2158-2164 | the write |
| 9 | the `--skip-sdp-unlock` 0x86 ack check (0x0D only) | 2208-2222 | post-write |
| 10 | `logger.info(f"Write to {…} successful ({…:.2f}s).")` / `logger.error(f"Write to {…} failed.")`; `return is_ok` | 2224-2229 | verdict |

`[VERIFIED: firestarter_app/firestarter/eprom_operations.py:2080-2229, read in full this session]`

Note step 10: the `successful` string D-14 forbids on a `--verify` run lives at line 2225-2227, inside
`write_eprom`, **not** in the CLI tier. Suppressing it requires either a parameter on `write_eprom` or
moving the verdict line out.

Note also that `require_acknowledged` / `require_page_size` / `require_page_alignment` are called
**twice** on the CLI path — once in `cli_handlers.write` (`:770-774`) and again here. That is
pre-existing and out of scope, but it means a guard placed in `write_eprom` runs exactly once while
its pure siblings run twice.

### 4.2 The wire dict is much thinner than it looks — a load-bearing finding

`convert_to_programmer` (`database.py:514-582`) emits **only** these keys:

`memory-size`, `algorithm`, `pin-count`, `vpp_mv`, `pulse-delay`, `flags`, and conditionally
`chip-id`, `bus-config`, `page-size`.
`[VERIFIED: firestarter_app/firestarter/database.py:527-580 — the only `programmer_data[...]` assignments are at 538, 541, 551, 580, plus the literal dict at 527-535]`

Measured, live:

```
W27C512  {'algorithm': 7,  'flags': 2, 'memory-size': 65536,  'electrical-type': None, 'protocol-id': None, ...}
M27C512  {'algorithm': 7,  'flags': 0, 'memory-size': 65536,  'electrical-type': None, 'protocol-id': None, ...}
AT28C256 {'algorithm': 13, 'flags': 2, 'memory-size': 32768,  ...}
W29C020  {'algorithm': 5,  'flags': 0, 'memory-size': 262144, 'page-size': 128, ...}
AM29F040 {'algorithm': 6,  'flags': 2, 'memory-size': 524288, ...}
```
`[VERIFIED: resolve_chip(name, db=EpromDatabase(skip_local_override=True)) executed this session]`

**There is no `electrical-type` key and no `protocol-id` key in the dict `write_eprom` receives.**
The new predicate can read `algorithm`, `flags`, `memory-size` and nothing else of use. This is
exactly why `flash4_erase_gate.is_flash4` and `page_size_gate.requires_page_size` both key on
`algorithm`.

#### 4.2.1 The proof that this matters — a live latent defect to copy *away* from

`check_eprom_blank`'s SRAM/FRAM short-circuit (`eprom_operations.py:2639-2648`) reads:

```python
etype = eprom_data_dict.get("electrical-type", "")
proto = eprom_data_dict.get("protocol-id", 0)
if etype in ("SRAM", "FRAM") or proto in self._SRAM_PROTO_IDS:
```

Both keys are absent from the dict `cli_handlers.blank` passes. Probed directly:

```
SRAM part: DS1220(RW)
wire dict: {'memory-size': 2048, 'algorithm': 40, 'pin-count': 24, 'vpp_mv': 12000,
            'pulse-delay': 0, 'chip-id': 0, 'bus-config': {...}, 'flags': 0}
electrical-type present? False | protocol-id present? False
short-circuit would fire? False
```
`[VERIFIED: probe executed this session against firestarter/data/chip_database.json via resolve_chip]`

**This short-circuit is inert on the CLI path today.** The repository already knows about the class of
bug: `sdp_capability.py:186-195` raises a `KeyError` rather than defaulting, with the comment *"A
silent default here is exactly how `check_eprom_blank`'s `_SRAM_PROTO_IDS` short-circuit became
vacuous in production (RESEARCH F-06); this predicate hard-fails instead."*
`[VERIFIED: firestarter_app/firestarter/sdp_capability.py:186-195]`

**Directive for the plan:** the new predicate module must key **only on `algorithm`/`flags`**, or
hard-fail on a key the programmer dict does not carry. Never `.get(key, default)` on a key that is
structurally absent. Consider filing the dead short-circuit as a separate todo — it is outside this
phase's requirements (it is a `blank` defect, not a `write` one) and should not be folded.

### 4.3 Flags

| Constant | Value | Source |
|---|---|---|
| `FLAG_FORCE` | `0x01` | `constants.py:108` |
| `FLAG_CAN_ERASE` | `0x02` | `constants.py:109` |
| `FLAG_SKIP_ERASE` | `0x04` | `constants.py:110` |
| `FLAG_SKIP_BLANK_CHECK` | `0x08` | `constants.py:111` |
| `FLAG_VPE_AS_VPP` | `0x10` | `constants.py:112` |
| `FLAG_SKIP_SDP_UNLOCK` | `0x100` | `constants.py:132` |

`[VERIFIED: firestarter_app/firestarter/constants.py:108-132]`

`FLAG_CAN_ERASE` derivation (`database.py:575-580`), quoted verbatim:

```python
simple_flags = 0
algo = programmer_data["algorithm"]  # already computed above from protocol-id
if full_eprom_data.get("electrical-type", "") in ("EEPROM", "Flash/EEPROM"):
    if algo not in (5,):
        simple_flags |= FLAG_CAN_ERASE  # FLAG_CAN_ERASE is 0x02
programmer_data["flags"] = simple_flags
```
`[VERIFIED: firestarter_app/firestarter/database.py:575-580]`

The surrounding comment block (`:554-574`) carries the live 12 V-on-a-5 V-part argument for the
algorithm-5 exclusion, exactly as CONTEXT describes. It is the reason `FLAG_CAN_ERASE` can never be
used as a blank-state signal on 0x05.

`-b`/`--no-blank-check` is a Click `flag_value=False, default=True` option feeding
`_build_op_flags(blank_check=…)` → `build_flags(...)` → `FLAG_SKIP_BLANK_CHECK` when false.
`[VERIFIED: cli_handlers.py:565-573, 318-360]`

### 4.4 Effective flags — the derivation the guard must reproduce

`_setup_operation` composes the wire value at `eprom_operations.py:526`:

```python
command_dict["flags"] = eprom_data_dict.get("flags", 0) | operation_flags
```
`[VERIFIED: firestarter_app/firestarter/eprom_operations.py:526]`

The guard runs **before** `_operation_context`, so no `command_dict` exists yet. It must therefore
compute `eprom_data_dict.get("flags", 0) | operation_flags` itself, from the same two inputs, using
the same expression. Two separate expressions for the same quantity is the drift the plan should
prevent — consider a small shared helper, or a comment at both sites naming the other.

### 4.5 `cli_handlers.write` — `cli_handlers.py:562-793`

| Element | Line |
|---|---|
| `@cli.command(name="write")` | 562 |
| options: `-b/--no-blank-check`, `--skip-erase`, `-f/--force`, `-a/--address`, `--vpe-as-vpp`, `--pulse-us`, `--skip-sdp-unlock` | 565-620 |
| `@click.pass_obj` / `@map_typed_errors` | 625-626 |
| `def write(...)` | 627-639 |
| docstring (the snapshotted help body) | 640-667 |
| `resolve_chip` | 668 |
| `--pulse-us` echo | 677-687 |
| SDP auto-set / warn-and-proceed arms | 689-731 |
| `--skip-erase` on 0x0D warn arm | 733-745 |
| `jp5_gate.confirm_or_refuse` → `sys.exit(1)` | 747-748 |
| `page_size_gate.require_page_size` / `require_page_alignment` | 749-752 |
| `ok = app.eprom_operator.write_eprom(...)` | 775-792 |
| `sys.exit(0 if ok else 1)` | **793** |
| `_region_refusal_exit_code` | 796-899 |
| `verify` command | 906-966 (`sys.exit(verdict)` at 966) |
| `blank` command | 968-1023 (`sys.exit(verdict)` at 1023) |

`[VERIFIED: firestarter_app/firestarter/cli_handlers.py, read 525-1025 this session]`

`_region_refusal_exit_code` returns `int | None` — always `2` on refusal, `None` to proceed — and is
called by `verify` (`:947`) and `blank` (`:1009`) before either touches `EpromOperator`. It performs
two refusals: explicit `--size` longer than the input file, and a region running past the chip's end
(including the CR-01 `start >= mem_size` case, which was fixed during Phase 202). It takes
`input_file: str | None = None`. `[VERIFIED: cli_handlers.py:796-899]`

**It does not refuse a negative start address** — `start = parse_address(address)`, then
`start = start or 0`, then `start >= mem_size` is false for a negative, and
`start + length > mem_size` is also false. See §10.

---

## 5. `_drive_region_compare` and the two problems with "reuse unchanged"

### 5.1 The contract

```python
def _drive_region_compare(
    self,
    cmd_data: dict,
    op_name: str,
    expected: Callable[[int, int], bytes],
    *,
    full: bool,
    region_length: int | None,
) -> int:
```
`[VERIFIED: firestarter_app/firestarter/eprom_operations.py:2230-2237]`

| Element | Line | Behaviour |
|---|---|---|
| `region_start = cmd_data.get("address", 0)` | 2256 | the accumulator's `addr_base` |
| `max_ranges = MAX_RETAINED_RANGES if full else 1` | 2257 | D-16 cap |
| `_process_chunk(address, payload)` → `accumulator.feed(address, expected(address, len(payload)), payload)` | 2260-2261 | the only place `actual` is visible |
| `abort_kwargs["abort_predicate"] = lambda: accumulator.has_mismatch` when `not full` | 2271-2273 | stop-acking at first mismatch |
| `self._read_abort_intended = not full` | 2279 | D-08 discrimination intent |
| `_run_state_machine(op_name, main_phase_handler=self._main_phase_read_data, start_addr=…, end_addr=cmd_data.get("memory-size", 0), process_data_chunk_callback=_process_chunk, **abort_kwargs)` | 2281-2288 | the drive |
| four-condition abort-vs-fault discrimination; `return 2` when not aborted | 2290-2316 | transport failure |
| `result = accumulator.finalise(aborted=aborted)`; `result.total = region_length` | 2318-2320 | verdict |
| **`for line in render_compare_lines(result): logger.info(line)`** | **2321-2322** | **unconditional render** |
| `if result.total > 0 and result.bad == 0 and result.compared == result.total: return 0` else `return 1` | 2331-2333 | 0/1 verdict |

`[VERIFIED: firestarter_app/firestarter/eprom_operations.py:2230-2333, read in full this session]`

The `expected` callback for the guard is already written and module-level:

```python
def _blank_expected_bytes(_offset: int, length: int) -> bytes:
    return b"\xff" * length
```
`[VERIFIED: firestarter_app/firestarter/eprom_operations.py:332-341]`

`region_length` for `--verify` and for the guard is both `address → address + len(input_file)`, which
`write_eprom` already computes at `:2131-2134`. Note that `cmd_data` for a compare drive must be a
**`COMMAND_READ`** dict — `_drive_region_compare` reads `cmd_data["memory-size"]` as the read's
`end_addr`, and `_setup_operation` narrows `memory-size` to `addr + read_size` only when
`cmd == COMMAND_READ and size` (`:518-527`). The guard must therefore open its own
`_operation_context(..., COMMAND_READ, ..., address_str, size_str)` with `size_str` set to the region
length — exactly as `verify_eprom` does at `:2437-2444`. `[VERIFIED: eprom_operations.py:518-527, 2437-2444]`

### 5.2 Problem 1 — D-11 vs the unconditional render

`_setup_logging` sets `log_level = logging.DEBUG if verbose else logging.INFO`
(`cli_handlers.py:113`), so `logger.info` output **is** visible at default verbosity.
`[VERIFIED: firestarter_app/firestarter/cli_handlers.py:105-126]`

A guard refusal that goes through `_drive_region_compare` unchanged therefore prints:

```
Mismatch 0x008000-0x008000 (1 bytes)
blank/contact, 1 bad of N compared of M (0x000000-0x008000)
Refusing write to W27C512: not blank at 0x008000, v: 0xAB.
```

D-11 says one line and nothing else. Routes:

- **(a) an additive keyword on `_drive_region_compare`** — e.g. `render: bool = True`, or
  `on_result: Callable[[CompareResult], None] | None = None` returning the structured result instead
  of logging. Smallest change; keeps the single compare drive; the default keeps `verify` and `blank`
  byte-identical. Phase 202's D-05 built `CompareResult` explicitly so "phase 203's write guard …
  need[s] this structured result without an echoed report" (`compare.py:91-94`), so this is the
  intended shape, and the missing switch is arguably the gap 202 left.
- **(b) the guard drives `_run_state_machine` + `CompareAccumulator` itself.** Duplicates the ~30-line
  four-condition D-08 discrimination. **Violates the standing one-compare-drive rule**
  (`_drive_region_compare`'s own docstring at `:2239-2254`). Not recommended.
- **(c) suppress at the logging tier** for the duration of the guard read. Fragile and invisible at
  the call site.

**(a) is the only option that respects both D-11 and 202's D-02/D-05.**

### 5.3 Problem 2 — the byte value does not exist (WRITE-01 / D-10)

`CompareResult` fields, in full: `total`, `compared`, `compared_start`, `compared_end`, `bad`,
`ranges`, `extra_ranges`, `extra_bytes`, `aborted`, `fingerprint`, `ff_count`, `first_offset`,
`bit_set_counts`. `[VERIFIED: firestarter_app/firestarter/compare.py:95-160]`

`MismatchRange` carries `start`, `end`, `count` — addresses only. `[VERIFIED: compare.py:79-89]`

`render_compare_lines`' docstring states: *"Emits no expected value and no actual value anywhere —
D-13 is an operator decision taken twice."* `[VERIFIED: compare.py:~470-490]`

And the `expected` pull callback signature is `Callable[[int, int], bytes]` — `(offset, length)`. **It
never sees `actual`.** A stateful closure passed as `expected` cannot capture the byte, because the
byte is on the other side of the comparison.

So WRITE-01's "and its value" needs one of:

- **(i) An additive `first_actual: int | None` field on `CompareAccumulator`/`CompareResult`.** One
  line in `feed`'s tier-3 branch, beside the existing `self._first_offset = address + offs[0] -
  self._addr_base` (`compare.py:246-247`), plus one line in `finalise` (`:324`) and one dataclass
  field. `render_compare_lines` is untouched, so 202's D-13 "the *compare renderer* prints no byte
  values" stays true by construction — the guard's refusal is not a compare report, exactly as D-10
  argues.
  - **Structural gate to respect:** `tests/test_compare.py:559-606`
    (`test_fast_path_precedes_per_offset_loop`) parses `CompareAccumulator.feed`'s AST and asserts
    that a top-level `if expected == actual: … return` precedes the *first* `for` loop in the
    function. Adding an assignment inside the existing tier-3 branch adds no `for` and does not move
    the fast path — the gate holds. A timing bound (`elapsed < 8.0` over a worst-case 512 KiB stream,
    `:534-545`) and a `PEAK_ALLOCATION_CEILING_BYTES` also live in that module; one int per
    mismatching chunk is negligible against both.
    `[VERIFIED: firestarter_app/tests/test_compare.py:534-606]`
  - **Cost:** `compare.py` is on the mypy strict list (`disallow_untyped_defs` + `check_untyped_defs`),
    so the field needs a full annotation. It also carries an AST import-set invariant
    (`test_compare.py:1359-1394`) — adding a field imports nothing, so that holds too.
- **(ii) The guard passes its own `process_data_chunk_callback` rather than using
  `_drive_region_compare`.** Same duplication objection as §5.2(b).
- **(iii) A second single-byte read at `first_offset` to fetch the value.** Costs a third port open on
  the refusal path, on top of D-17's three. Reject.

**(i) is the recommendation.** It is additive, it is ~4 lines, it keeps one compare implementation, it
survives every gate on `compare.py`, and it is the only route that satisfies D-10's "address and value"
without a second divergence implementation.

---

## 6. The chip database — the real population the D-02 pinning test faces

Measured across all 746 rows of `firestarter/data/chip_database.json` this session.

| `programming.algorithm` | rows | `electrical.type` breakdown | `support_status` | guarded per D-01? |
|---|---|---|---|---|
| `0x05` (5) | 27 | Flash/EEPROM 27 | supported 27 | **no** — named exemption |
| `0x06` (6) | 190 | Flash/EEPROM 190 | supported 190 | **yes** |
| `0x07` (7) | 170 | UV-EPROM 163, EEPROM 7 | supported 170 | **yes** |
| `0x08` (8) | 127 | UV-EPROM 106, EEPROM 21 | supported 127 | **yes** |
| `0x0B` (11) | 32 | UV-EPROM 32 | supported 32 | **yes** |
| `0x0D` (13) | 84 | EEPROM 66, Flash/EEPROM 18 | supported 75, adapter-required 9 | **no** |
| `0x0E` (14) | 20 | SRAM 20 | supported 20 | **no** — named exemption |
| `0x10` (16) | 39 | Flash/EEPROM 39 | supported 39 | **yes** |
| `0x27` (39) | 2 | SRAM 2 | supported 2 | **no** — named exemption |
| `0x28` (40) | 34 | SRAM 34 | supported 34 | **no** — named exemption |
| `0x29` (41) | 20 | SRAM 20 | supported 20 | **no** — named exemption |
| `0x34` (52) | **1** | EEPROM 1 | **protocol-not-implemented 1** | see §7.A |

`[VERIFIED: python3 over firestarter_app/firestarter/data/chip_database.json, this session — 746 rows total]`

**The guarded set covers 558 of 746 rows (74.8 %).**

Useful fixtures for the pinning test, all verified live this session:

| Chip | `algorithm` | `flags` | Meaning for the guard |
|---|---|---|---|
| `M27C512` | 7 | `0` | guarded, **not** exempt — the canonical criterion-1 / criterion-5 fixture |
| `W27C512` | 7 | `2` (`FLAG_CAN_ERASE`) | guarded but exempt — and **re-armed by `--skip-erase`** (D-03). The canonical D-03 fixture. |
| `AM29F040` | 6 | `2` | guarded, exempt unless `--skip-erase` |
| `W29C020` | 5 | `0` | named exemption (0x05); also the folded todo's own repro chip |
| `AT28C256` | 13 | `2` | unguarded (0x0D) |
| `DS1220(RW)` | 40 | `0` | named exemption (SRAM) |

`[VERIFIED: resolve_chip(...) executed this session for each]`

Note `W27C512` carries `algorithm: 7`, not `0x0B` — it is a protocol-0x07 part whose
`electrical.type` is `EEPROM`, which is precisely the "W27C512-class EEPROM rows" case D-01's table
names. The guard's exemption and D-03's re-arming both hang on this one row shape.

---

## 7. The open design forks (report, not decide)

### A. Predicate shape — allowlist vs named-exemption denylist (D-06 discretion, bounded by D-01 + D-05)

There is a real, narrow tension between D-01 ("exactly these five") and D-05 ("an unrecognised
protocol id fails closed — it gets the read"). The two clauses disagree about exactly one thing: a
protocol id that is neither in the five nor in the named exemptions.

| Form | Predicate | `0x34` (52) | absent `algorithm` key | Matches "preserve today's coverage"? |
|---|---|---|---|---|
| **A1 — pure allowlist** | `algorithm in {6,7,8,11,16}` | not guarded | **not** guarded (fails OPEN) | yes, but contradicts D-05's first clause |
| **A2 — allowlist + absent-key fail-closed** | `algorithm in {6,7,8,11,16} or algorithm is None` | not guarded | guarded | yes; honours D-05's absent-key clause, declines its unrecognised-id clause |
| **A3 — named-exemption denylist (literal D-05)** | `algorithm not in {5,13,14,39,40,41}` | **guarded** | guarded | **widens** coverage by one protocol |

**The choice is unobservable on every shipped database row.** The single `0x34` row is
`support_status: "protocol-not-implemented"`, and `chip_resolver.resolve_chip` raises
`ChipNotImplementedError` for any non-`"supported"` status **before any wire dict is built**
(`chip_resolver.py:51-57`). `write_eprom` is therefore unreachable for it.
`[VERIFIED: chip_resolver.py:43-71; the row's `support_status` read from chip_database.json this session]`

Two facts keep D-05's clauses from being purely theoretical:

- `resolve_chip` already refuses an **absent or zero** `algorithm` (`chip_resolver.py:66-71`), so
  D-05's absent-key clause is unreachable from the CLI and is a unit-level property of the predicate,
  not an end-to-end one. It is still worth having as defence in depth for the `dev` and test callers
  that hand-build dicts.
- `resolve_chip`'s own comment states: *"A non-zero-but-unknown algorithm is deliberately NOT refused
  here — it falls through to the firmware's own fail-closed dispatch."* `[VERIFIED: chip_resolver.py:64-66]`
  A user-supplied `~/.firestarter` database override can therefore introduce an unknown non-zero
  algorithm that reaches `write_eprom`. That is the one live path where A1/A2 and A3 differ.

**Recommendation to the planner: pick one and write the reasoning at the site, because D-02's pinning
test has to encode the choice.** A2 is the narrowest reading that satisfies both D-01's "exactly five"
and D-05's stated fail-closed polarity for the case D-05 can actually reach. A3 is defensible on
D-05's literal text but widens coverage onto `0x0D` and SRAM unless those are *also* named — at which
point A3 and A2 differ only on genuinely unknown ids.

Whichever is chosen, the module must also name `0x0D` explicitly. CONTEXT's D-01 prose names only
SRAM/FRAM and `0x05` as exemptions, but its own table lists `0x0D` as unguarded, and `0x0D` is 84
database rows.

Constants available for reuse:

| Constant | Value | Home |
|---|---|---|
| `FLASH4_PROTOCOL_ID` | `5` | `flash4_erase_gate.py:41` — **D-06 mandates reusing this** |
| `SDP_PROTOCOL_ID` | `13` | `sdp_capability.py:31` |
| `_SRAM_PROTO_IDS` | `frozenset({0x0E, 0x27, 0x28, 0x29})` | `eprom_operations.py:2594` **and** `chip_test.py:249` — already duplicated |
| `NO_MECHANISM_PROTOCOL_IDS` | `frozenset({7, 8, 11, 14, 39, 40, 41})` | `protection_readability.py:106` — a precedent for the frozenset-of-ids form, on a *different* axis; do not reuse the set itself |

`[VERIFIED: the four files above, this session]`

⚠ **`eprom_operations.py:138` already defines `_FLASH4_PROTOCOL_ID = 5`** — a third copy of the 0x05
constant that D-06 exists to prevent, used at `:199`. `page_size_gate.py:52` does it correctly
(`from firestarter.flash4_erase_gate import FLASH4_PROTOCOL_ID`). The new module must follow
`page_size_gate`, and the plan may wish to note (not necessarily fix) the `eprom_operations` copy.
`[VERIFIED: eprom_operations.py:138,199; page_size_gate.py:39,52,96]`

### B. Refusal mechanism — typed exception vs return value (Claude's discretion, **constrained**)

The constraint is measured and decides half the question:

- `click.ClickException.exit_code == 1`; `click.UsageError.exit_code == 2`.
  `[VERIFIED: python -c "import click; print(click.ClickException.exit_code)"` on click 8.5.0, this session]
- `map_typed_errors` (`cli_handlers.py:192-233`) maps **every** typed exception — including
  `SerialError`, `SerialTimeoutError`, `EpromOperationError` and its subclasses — to
  `click.ClickException`, hence **always exit 1**. `[VERIFIED: cli_handlers.py:192-233]`
- A transport failure during the guard read never reaches `map_typed_errors` anyway:
  `_setup_operation` catches `(ProgrammerNotFoundError, SerialError)` and returns `(None, 0)`
  (`:507-510`), and `_run_state_machine` catches `(SerialError, SerialTimeoutError)` and returns
  `(False, str(e))` (`:670-672`). `_drive_region_compare` turns that into `return 2`.
  `[VERIFIED: eprom_operations.py:507-510, 670-681, 2290-2316]`

**Therefore:** D-13's "exit **2** for a transport or hardware failure anywhere in the invocation,
including the guard read" **cannot** be delivered by a typed exception. It must be a return value, the
way `verify`/`blank` already do it (`sys.exit(verdict)` at `cli_handlers.py:966` and `:1023`).

A hybrid is available and is what the four sibling gates plus `verify` jointly suggest: a typed
exception for the **not-blank refusal** (exit 1, correct under both contracts, renders the D-10
sentence verbatim through `map_typed_errors` exactly as `PageAlignmentError` does at `:223-224`), and
a **return value** for the transport case. The plan must decide how `write_eprom`'s `-> bool` carries
the tri-state; §7.C is where that lands.

### C. `--verify` placement — CLI tier vs operator tier (open; CONTEXT fixes only the guard's home)

D-07 fixes the *guard* inside `write_eprom`. It says nothing about `--verify`.

| | C1 — CLI tier | C2 — operator tier |
|---|---|---|
| Shape | `write()` calls `write_eprom(...)`, then `verify_eprom(eprom, data, input_file, address_str=address, full=full)`; combines verdicts | `write_eprom(..., verify=True, full=…)` drives a second `_drive_region_compare` internally; returns `int` |
| Region | `verify_eprom` with `size_str=None` uses the input file's length — **exactly D-16's region, for free** (`eprom_operations.py:2386-2413`) | must be composed by hand, same arithmetic |
| Exit codes | natural: `sys.exit(combined)` beside `verify`'s own `sys.exit(verdict)` | needs `write_eprom`'s return type widened |
| D-14 ("successful" never appears) | **hard**: `write_eprom` logs `Write to X successful (t).` at `:2225-2227` and `verify_eprom` logs `Verify for X successful (t).` at `:2453-2456`. Both must be suppressed. | one suppression point |
| Return-type churn | none — `write_eprom` stays `-> bool` | `write_eprom -> int` touches `cli_handlers.py:775`, `eprom_operations.py:1303` (`write_cycle_eprom`), `chip_test.py:3228` and `:3482`, plus ~40 test assertion sites that treat it as a bool |
| Other callers | unaffected | every caller must be audited |

`[VERIFIED: the line references above, read this session; the ~40 test sites from
`grep -rn "write_eprom" firestarter_app/tests/`, this session]`

**Note the return-type blast radius before choosing C2.** `tests/test_chip_test.py` alone has ~30
`operator.write_eprom.return_value = True/False` and `.side_effect = [True, False]` assertions, and
`chip_test.py:3387-3404` documents `write_eprom`'s bool as a deliberate "PRECONDITION signal only"
contract. Widening it to an int is the same migration `verify_eprom` went through in 202-01, which
needed an explicit `== 0` adapter at `chip_test.py:3491` to keep `outcomes` a list of bools.
`[VERIFIED: chip_test.py:3387-3404, 3488-3493]`

A third shape worth naming: `write_eprom` keeps `-> bool` and grows a `verify: bool = False` kwarg
plus an out-parameter-style attribute (e.g. `self.last_write_verify_verdict: int | None`), read by the
CLI tier immediately after the call. It avoids the return-type migration entirely at the cost of a
piece of transient operator state — which is a shape the codebase already uses for
`last_firmware_error_code` / `last_firmware_error_message` / `_read_abort_stopped_at`.

### D. Progress bar on the guard read (Claude's discretion; **not free either way**)

`_main_phase_read_data` calls `progress.start(data_size)` unconditionally when `data_size > 0`
(`eprom_operations.py:956-958`), and `ClassProgressHandler.start` instantiates a `tqdm` bar whenever
`self.progress_callback` is falsy (`:376-385`). So **a progress bar appears by default** on the guard
read; showing none requires an explicit act. `[VERIFIED: eprom_operations.py:369-411, 915-960]`

There is a clean in-repo precedent for suppression, in `consistency_check_eprom`:

```python
# Quiet mode: suppress tqdm by swapping progress_callback to a no-op.
# ClassProgressHandler.__init__ checks `if self.progress_callback:` --
# a truthy no-op short-circuits the tqdm.tqdm() instantiation.
prior_callback = self.progress_callback
if quiet:
    self.progress_callback = lambda *a, **kw: None
...
finally:
    # Restore the operator's progress_callback so subsequent
    # operations are unaffected by --quiet for THIS invocation.
    self.progress_callback = prior_callback
```
`[VERIFIED: firestarter_app/firestarter/eprom_operations.py:1096-1101, 1256-1258]`

`verify_eprom`'s docstring already records the *other* half of the decision — on an abort the bar
"simply stops advancing at the compared byte count … it is never advanced to the region total, since a
bar that completes after a stop would claim progress the compare did not make". Whatever the plan
chooses, that honesty property must be preserved. `[VERIFIED: eprom_operations.py:2358-2370]`

Trade-off: a bar on the guard read gives the operator feedback during a read that can take ~7.5 s on a
64 KiB 0x07 part (§11), but it means a guarded `write --verify` shows **three** bars. A guarded write
that then refuses shows a bar that stops part-way and is then followed by a refusal, which may read as
a failure of the read rather than a refusal of the write.

### E. D-17's session-cost figure, without a bench (Claude's discretion; **the harness cannot do it**)

`tests/test_connect_cost_harness.py` tests `EpromOperator._summarize_connect_samples` (pure, 4 tests),
`measure_connect_cost` (1 test, the no-port refusal), and the `dev fault-inject --mode connect-cost`
CLI dispatch. `[VERIFIED: tests/test_connect_cost_harness.py:1-110]`

`measure_connect_cost` **requires a real board**: it resolves a port or returns `False` without
opening anything (`eprom_operations.py:1867-1874`), then calls `SerialCommunicator.find_and_connect`
`samples` times with `restrict_to_port=True` (`:1886-1903`). The phase is bench-no, so **the harness
route is unavailable.** `[VERIFIED: eprom_operations.py:1837-1907]`

**But the figure already exists, measured on real hardware.** Phase 176 plan 05 recorded it:

| Board class | Samples | Min | Median (`median_low`) | Max | Structural floor | Remainder |
|---|---|---|---|---|---|---|
| Uno-class (512 B, `/dev/ttyACM1`) | 10 | 2.517 s | **2.518 s** | 2.519 s | 2.500 s | 0.018 s |
| Leonardo-class (1024 B, `/dev/ttyACM0`) | 10 | 2.606 s | **2.607 s** | 2.676 s | 2.500 s | 0.107 s |

`[VERIFIED: .planning/milestones/v1.36-phases/176-transport-instrumentation-connect-cost-measurement-partially/176-MEASUREMENT.md §4a, §4b — measured 2026-09-04 against app HEAD `df2978e`]`

`CONNECT_COST_STRUCTURAL_FLOOR_S = CONNECTION_STABILIZE_DELAY + _CONSUME_REMAINING_INPUT_WINDOW_S`
= 2.5 s. `[VERIFIED: eprom_operations.py:93-96]`

So the honest route for D-17 is a **derivation over a recorded measurement**, not a new measurement:

- plain guarded `write` (part is blank): **+1 port open** ≈ 2.518 s (Uno) / 2.607 s (Leonardo), plus
  one full region read.
- guarded `write --verify`: **+2 port opens** ≈ **5.04 s** (Uno) / **5.21 s** (Leonardo), plus two
  full region reads.
- a guarded write that is **refused**: +1 port open, a partial read, plus **≤ 1.0 s** for the
  deliberate abort — the firmware's `op_wait_for_ack` polls at 10 ms to a 1000 ms deadline.
  `[VERIFIED: .planning/phases/202-one-comparison-engine-on-the-host/202-READ-ABORT-ANSWER.md §"The mechanism", fact 2]`

Read time is the other term. The only figures in-repo are from a single Leonardo log: 8.7 KB/s on a
`0x07` 64 KiB part (7.51 s), and a corrected 7.0 KB/s on a `0x08` 256 KiB part (37.2 s).
`[CITED: .planning/notes/dev-test-sequence-cost-model.md § "Measured primitives", which itself warns
"this is a model built on one sample, not a benchmark"]` — record these as cited, single-sample
figures, never as this phase's own measurement.

**Recommendation:** record D-17's figure as a *derived* number with its provenance explicit — connect
term from 176-MEASUREMENT.md, abort term from 202-READ-ABORT-ANSWER.md, read term cited as a
single-sample model — and say in the phase record that no new hardware measurement was taken because
the phase is bench-no. Phase 206 then inherits a real before-figure with an honest error bar, which is
what SESS-02 needs. Alternatively, ask the operator for one bench run; that is an operator decision,
not a planning one.

---

## 8. `write --help` — the two snapshots, and what a hand-edit must touch

| Snapshot | `.ambr` block | Test |
|---|---|---|
| `test_help_write` | lines **363-415** (`# name:` 363, body 364-414, closing `'''` 415, `# ---` 416) | `tests/test_characterization.py:174-177` |
| `test_no_blank_check_polarity` | lines **1394-1446** (body 1395-1445) | `tests/test_characterization.py:469-477` |

`[VERIFIED: firestarter_app/tests/__snapshots__/test_characterization.ambr, line-counted this session]`

**The two bodies are byte-identical**, 51 lines each — confirmed by `diff` of the two extracted
ranges, which reported no differences. `[VERIFIED: diff of sed-extracted ranges, this session]`

Both carry the **entire** help output: the full docstring (7 paragraphs) and all 8 option blocks,
Click-wrapped at 80 columns. `test_no_blank_check_polarity` additionally asserts
`"--no-blank-check" in stdout` before the snapshot comparison.

Both tests run `run_firestarter("write", "--help")` — the same command — so any change to the
docstring or the option list changes **both blocks identically**. A hand-edit is therefore a single
diff applied twice. **Never `--snapshot-update`.**

### 8.1 The docstring sentence that needs re-reading (CONTEXT flags this; it is worse than flagged)

Current text, verbatim from `cli_handlers.py:651-653` and both snapshots:

> On protocols 0x0D and 0x05 the write path performs no pre-write blank check at all, so -b is a
> no-op on those families and is not needed to write a non-blank part. It remains effective on every
> other protocol.

Under D-01 the first clause stays true but is now **incomplete** — the SRAM protocols
(`0x0E`/`0x27`/`0x28`/`0x29`, 76 database rows) are also unguarded, and the last sentence *"It remains
effective on every other protocol"* becomes **false**: after this phase `-b` is a no-op on SRAM too.
`[VERIFIED: cli_handlers.py:640-667; the SRAM row count from §6]`

The sentence also silently changes subject: it described a *firmware* policy and will describe a
*host* policy. Both properties belong in the rewrite.

### 8.2 What the option blocks gain

`--verify` and `--full`, plus D-13's mandated statement that `--verify` changes the exit-code
contract. Click renders option help at 80 columns with a 26-column indent, so each sentence costs
roughly 3-4 snapshot lines. Budget a plan task for the snapshot hand-edit specifically; it is the
kind of mechanical work that is easy to under-scope and impossible to `--snapshot-update` out of.

---

## 9. Trap 2 — the wire-level ordering assertion criterion 1 needs

Criterion 1: *"refused … before the port carries a programming command."*

### 9.1 The seam

`SerialCommunicator.find_and_connect(command_to_send, config_manager, ...)` is where the command frame
first reaches the wire. Its own docstring says so: *"the setup command sent here is the ONLY
corruptible host→fw command frame, so the outgoing fault MUST be injected at connection time, not
after setup."* `[VERIFIED: firestarter_app/firestarter/serial_comm.py:1001-1007]`

`_setup_operation` composes the dict and calls it:

```python
command_dict["cmd"] = cmd                                              # :524
command_dict["flags"] = eprom_data_dict.get("flags", 0) | operation_flags   # :526
...
self.comm = SerialCommunicator.find_and_connect(command_dict, self.config, fault_inject_outgoing=…)  # :560-564
```
`[VERIFIED: firestarter_app/firestarter/eprom_operations.py:502-570]`

So **`command_dict["cmd"]`, captured at `find_and_connect`, is a complete and exact record of every
command ordinal the port carries, in order.** The guard's read is `COMMAND_READ`; the write is
`COMMAND_WRITE`. A refused write must produce `[COMMAND_READ]` and nothing more.

### 9.2 The idiom already in the suite

`tests/test_eprom_operations.py::test_region_end_emitted_on_write` (`:393`) already captures at
exactly this boundary — its own docstring calls it *"the wire boundary (the dict
`SerialCommunicator.find_and_connect` receives), the same boundary `TestSdpOperationsWireShape` above
uses."* `[VERIFIED: tests/test_eprom_operations.py:393-405]`

And `_drive_write_eprom_for_ack_check` (`:2280-2296`) patches it with a `side_effect`:

```python
def _fake_find_and_connect(command_dict, config, **kwargs):
    return make_comm()

with patch(
    "firestarter.serial_comm.SerialCommunicator.find_and_connect",
    side_effect=_fake_find_and_connect,
):
    ok = operator.write_eprom("at28c256", _at28c256_programmer_dict(), str(input_file),
                              operation_flags=operation_flags)
```
`[VERIFIED: tests/test_eprom_operations.py:2280-2296]`

### 9.3 What the ordering test looks like here

Append to a list inside the `side_effect`, then assert on the whole sequence. Sketch, for the plan to
adapt — every value in it appears in a verbatim quote above:

```python
opened: list[int] = []

def _recording_find_and_connect(command_dict, config, **kwargs):
    opened.append(command_dict["cmd"])          # eprom_operations.py:524
    return make_comm()

# ... feed the READ-phase frame script whose payload is NOT blank ...
with patch("firestarter.serial_comm.SerialCommunicator.find_and_connect",
           side_effect=_recording_find_and_connect):
    ok = operator.write_eprom("m27c512", _m27c512_programmer_dict(), str(input_file))

assert ok is False
assert opened == [COMMAND_READ], (
    "the guard must refuse before any COMMAND_WRITE reaches find_and_connect; "
    f"observed command sequence {opened!r}"
)
assert COMMAND_WRITE not in opened
```

Properties worth naming in the plan:

- **It fails if reordered.** Putting the guard after `_operation_context` makes `opened` start with
  `COMMAND_WRITE`, and both assertions fail.
- **It fails if the guard is skipped entirely.** `opened == [COMMAND_WRITE]` fails the equality.
- **`opened == [...]` rather than `COMMAND_WRITE not in opened` alone** — the `not in` form alone
  would pass vacuously if the guard raised before *any* connect (e.g. a pure-gate refusal firing by
  accident), which is a different behaviour wearing the same green.
- **A second, positive test is required** for the pass case: a blank region must yield
  `opened == [COMMAND_READ, COMMAND_WRITE]`, in that order. Without it, a guard that always refuses
  also passes the negative test.

There is **no existing outgoing-frame log** on `_FakeSerial` — `write()` appends to the same buffer
`feed()` writes to, with no separate record (`tests/conftest.py:169-186`). Byte-level assertion is
therefore not available without adding one; the `find_and_connect` capture is strictly better anyway,
because it is command-level and already an established idiom.
`[VERIFIED: tests/conftest.py:133-192]`

---

## 10. The folded todo — negative write start address, host half

### 10.1 The measured state

```python
def parse_address(s: str | None) -> int | None:
    if s is None:
        return None
    return int(s, 16) if "0x" in s.lower() else int(s)
```
`[VERIFIED: firestarter_app/firestarter/address_parser.py:11-18]`

`int("-256")` → `-256`; `int("-0x100", 16)` → `-256`. No sign check anywhere.

`require_page_alignment`'s modulo check: `if start % page_size != 0 or length % page_size != 0:`
(`page_size_gate.py:174`). Python's `%` on a negative dividend returns a non-negative result, so
`-256 % 256 == 0` reads as aligned. `[VERIFIED: page_size_gate.py:136-182]`

### 10.2 The caller audit the todo asks for — completed

`parse_address` has **exactly three production callers**, and **all three already have a `ValueError`
handler**:

| Caller | Line | Existing `ValueError` behaviour |
|---|---|---|
| `EpromOperator._setup_operation` | `eprom_operations.py:530` | `logger.error(f"Invalid address format: {address}")`; `return None, 0` → `_operation_context` yields `(None,None,None)` → `write` returns `False` (exit 1), `verify`/`blank` return 2 |
| `cli_handlers._region_refusal_exit_code` | `cli_handlers.py:839` | `return None` — deliberately defers to `_setup_operation`'s handling |
| `page_size_gate.require_page_alignment` | `page_size_gate.py:163` | raises `PageAlignmentError(f"{chip}: could not parse address {address_str!r}")` |

`[VERIFIED: grep -rn "parse_address" firestarter_app/firestarter/, this session; each handler read in place]`

`tests/test_address_parser.py` has 5 `parse_address` assertions (`:20, 23, 26, 29, 33, 37`) — none
involves a negative. `[VERIFIED: tests/test_address_parser.py:15-38]`

### 10.3 Minimal host-side fix shapes

| Shape | Blast radius | Catches | Tests that move |
|---|---|---|---|
| **F1 — reject in `require_page_alignment` before the modulo** (the todo's own candidate 1) | 1 function | **0x05 writes only** — the gate early-returns for every non-0x05 part (`page_size_gate.py:156-158`). Misses the guarded UV families entirely. | new cases in `tests/test_page_size_alignment_refusal.py` |
| **F2 — reject negatives in `parse_address`** | 3 callers, all already handling `ValueError`; changes `read`/`verify`/`blank` too (a negative `-a` on `read` silently starts at 0 today) | every path | new cases in `tests/test_address_parser.py`; check `tests/test_cli_handlers.py` and `tests/test_characterization.py` for any negative-address expectation (none found) |
| **F3 — a new pure pre-connect gate on the write path** (e.g. beside the other three in `write_eprom`, or a `require_non_negative_address` in the new predicate module) | write path only | every guarded and unguarded write | a new test module, or the new predicate module's own tests |

**Why it genuinely belongs here, restated concretely:** both the guard's region and `--verify`'s region
derive from `address`. With `-a -256`, `CompareAccumulator(addr_base=-256)` would report a negative
`first_offset`, `cmd_data["address"] = -256` goes on the wire, and the firmware's `simple_strtoul`
clamps it to 0 — so the host would compare region `[-256, …)` against bytes the device returned from
`[0, …)`, and the D-10 refusal sentence would name a negative address. The guard makes a latent
wrong-destination defect into a *wrong-evidence* defect.

F2 is the cleanest (every caller is already prepared) but widens behaviour beyond `write`; F3 is the
narrowest that actually covers the guarded families. **F1 alone does not cover this phase's own
guarded set** and should not be chosen on the strength of the todo's wording.

---

## 11. `dev test` and `dev write-cycle` — proving "behaviourally unchanged"

### 11.1 `chip_test.py` — the two `write_eprom` call sites

| Site | Line | Flags passed | Guard outcome |
|---|---|---|---|
| `_dispatch_multi_run`'s `OP_WRITE` / `OP_WRITE_PARTIAL` arm | `chip_test.py:3228-3234` | `write_flags` (positional 4th arg) | `write_flags = FLAG_SKIP_BLANK_CHECK if _is_monotonic_masked_target(resolved_target) else 0` (`:3219-3221`) |
| `_dispatch_sdp_leg` | `chip_test.py:3482-3488` | `flags` — `0` or `FLAG_SKIP_SDP_UNLOCK` (`:3450-3461`) | SDP-leg ops are 0x0D-only (`sdp_capability` gates the leg at `chip_test.py:725`), and `0x0D` is unguarded → no change |

`[VERIFIED: firestarter_app/firestarter/chip_test.py:3219-3234, 3440-3488, 3031-3055, 725]`

`_is_monotonic_masked_target` (`:3031-3055`) returns True only when `target is not None and
target.masked and bool(target.current) and target.current_is_probe_read`. For every other UV target
`write_flags == 0`, so the **host guard will now fire** on `dev test`'s write step where it did not
before — and the firmware would have refused those same writes anyway (§3's table). That is
D-07's claim, and the way to *prove* it is to run `dev test`'s existing test modules unchanged and
show no new failures:

`tests/test_chip_test.py`, `tests/test_chip_test_cycle.py`, `tests/test_chip_test_uv_slot_write.py`,
`tests/test_chip_test_sdp_leg.py`, `tests/test_dev_test_cmd.py`. Note that these drive `FakeChip` /
`Mock` operators, so they do **not** exercise the guard — they prove the dispatch shape is unchanged,
not that the guard behaves. Both statements belong in the plan's verification wording, separately.

### 11.2 `write_cycle_eprom` (`dev write-cycle`)

```python
for i in range(1, runs + 1):
    if not self.erase_eprom(eprom_name, eprom_data_dict, operation_flags):   # :1298
        logger.error(f"Cycle {i}: erase failed."); return 2
    if not self.write_eprom(eprom_name, eprom_data_dict, source_image_path, operation_flags):  # :1303
        logger.error(f"Cycle {i}: write failed."); return 2
```
`[VERIFIED: firestarter_app/firestarter/eprom_operations.py:1296-1307]`

D-07's "erases before every write → exempt" holds, but via the **flag proxy**, not via observation:
the exemption is `FLAG_CAN_ERASE && !FLAG_SKIP_ERASE` on the same `eprom_data_dict`/`operation_flags`
pair `erase_eprom` just used. A part without `FLAG_CAN_ERASE` fails at step (a) and never reaches
`write_eprom`, so the proxy and the truth coincide on every part `write-cycle` can actually run on.
Worth one sentence at the exemption site, because the proxy is not self-evidently equivalent.

---

## 12. Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Byte divergence / first-mismatch detection | a scan loop in the guard | `compare.CompareAccumulator` | Standing one-divergence-implementation rule (`compare.py:326-337`). A second loop is exactly what `diff_summary` was moved to `compare.py` to prevent. |
| Driving a compare over the wire | a second `_run_state_machine` call with a hand-written abort predicate | `_drive_region_compare` (extended additively) | The D-08 abort-vs-fault discrimination is 30 lines of measured reasoning (`:2290-2316`). A copy will drift and will report a deliberate abort as hardware trouble. |
| The blank expected side | `b"\xff" * region_length` materialised up front | `_blank_expected_bytes` (`:332-341`) | Already module-level *specifically* so it is unit-testable; a device-sized buffer is what the pull-callback shape exists to avoid. |
| A 0x05 protocol-id constant | a new `0x05` literal or a fourth copy | `flash4_erase_gate.FLASH4_PROTOCOL_ID` via `from … import`, as `page_size_gate.py:52` does | D-06 mandates it, and `eprom_operations.py:138` shows the drift has already started. |
| The refusal sentence | an f-string assembled at the raise site | a module-level `_REFUSAL_FORMAT` + `refusal_text(...)`, as `flash4_erase_gate.py:43,68-80` | D-12; lets the test assert the whole sentence, not a substring of a log line. |
| Exit-code plumbing | `sys.exit` inside `EpromOperator` | return an int; `sys.exit(verdict)` in the CLI tier | `verify`/`blank` establish it (`cli_handlers.py:966`, `:1023`); `EpromOperator` contains no `sys.exit`. |
| A "was the port opened" assertion | byte-sniffing `_FakeSerial._buf` | patch `find_and_connect` and record `command_dict["cmd"]` | §9; `_FakeSerial` mixes both directions into one buffer, and the command-level record is exact. |
| Progress-bar suppression | a new flag threaded through `_run_state_machine` | swap `self.progress_callback` to a no-op and restore in `finally` | `eprom_operations.py:1096-1101, 1256-1258` already does exactly this. |
| Region resolution for `--verify` | new arithmetic | `verify_eprom` with `size_str=None`, or `write_eprom`'s existing `region_length` at `:2131-2134` | Both already compute `address → address + len(file)`. |

---

## 13. Common Pitfalls

### P-1: Reusing `_drive_region_compare` "unchanged" and breaking D-11
**What goes wrong:** the refusal prints three lines instead of one.
**Why:** `:2321-2322` renders unconditionally, and default log level is INFO (`cli_handlers.py:113`).
**Avoid:** add a render/result switch (§5.2 option a).
**Warning sign:** a test asserting `"Refusing write" in caplog.text` passes while the operator sees a
`Mismatch 0x…` line above it. Assert on the **full** captured output, not a substring.

### P-2: Assuming `CompareResult` carries the byte value
**What goes wrong:** the D-10 sentence gets `0x00` or `None` where `v: 0xAB` belongs, or a second read
is added to fetch it.
**Why:** the field does not exist; the `expected` callback never sees `actual`.
**Avoid:** §5.3 option (i).
**Warning sign:** a plan task that says "format the refusal from `CompareResult`" with no task that
adds a field.

### P-3: Writing the predicate against `electrical-type` or `protocol-id`
**What goes wrong:** the predicate is silently inert — it never fires, and every test that constructs
its own dict passes.
**Why:** §4.2. The programmer dict carries neither key. `check_eprom_blank`'s SRAM short-circuit is
the live proof.
**Avoid:** key on `algorithm`; or hard-fail on an absent key, as `sdp_capability.py:186-195` does.
**Warning sign:** the predicate's unit tests pass but a CLI-level test of the same part does not
refuse. Add at least one test that feeds a dict from the **real** `resolve_chip`, not a literal.

### P-4: Testing the guard through `FakeChip` / `WriteInitPreflightChip`
**What goes wrong:** WRITE-06 and criterion 5 go green having executed zero lines of `firestarter/`.
**Why:** §2.1 — the double replaces the operator entirely.
**Avoid:** §2.5 option A.
**Warning sign:** a test importing from `tests.fake_chip` while claiming to prove a host-path
property. Cross-check with `--cov=firestarter --cov-report=term-missing` on the new module: if the
guard's lines show as missed, the test is theatre.

### P-5: Running the suite on the devcontainer's Python 3.12
**What goes wrong:** a green local run, a red CI.
**Why:** CI pins 3.11; `python3` in this container is **3.12.14**. This has broken beta CI before.
**Avoid:** always `.venv311/bin/python -m pytest …`. `.venv/` has no `bin/python` and will fail
noisily; `.venv-ci-188` is also 3.11.16 if `.venv311` is unavailable.

### P-6: `--snapshot-update`
**What goes wrong:** the two 51-line help snapshots are silently rewritten, destroying the review
signal that is the whole point of pinning them.
**Avoid:** hand-edit both blocks with the diff shown; they are byte-identical, so it is one diff
applied twice (§8).

### P-7: Expecting `map_typed_errors` to deliver exit 2
**What goes wrong:** D-13's transport-failure-under-`--verify` arm exits 1.
**Why:** `ClickException.exit_code == 1` for every mapped type; and transport failures never reach the
decorator anyway because `_setup_operation` and `_run_state_machine` swallow them (§7.B).
**Avoid:** carry the transport case as a return value.

### P-8: Adding a `# noqa` for a code outside `E,F,I,UP`
**What goes wrong:** it is inert and reads as suppression that is not happening.
**Avoid:** `ruff` selection is `["E","F","I","UP"]` with `E501` ignored (`pyproject.toml`). The only
live forms in-tree are `# noqa: E501`, `# noqa: UP006`, `# noqa: UP024`, `# noqa: UP035`, `# noqa: F401`.

### P-9: Widening `write_eprom`'s return type without auditing the ~40 test sites
**What goes wrong:** a long red tail across five test modules.
**Why:** `chip_test.py:3387-3404` documents the bool as a deliberate contract, and
`tests/test_chip_test.py` alone has ~30 bool-valued `return_value`/`side_effect` settings.
**Avoid:** §7.C — choose C1 or the attribute shape, or budget the migration explicitly.

### P-10: Feeding `_FakeSerial` frames between host writes
**What goes wrong:** the host reads back its own outgoing bytes and the frame parser desyncs.
**Why:** `feed()` and `write()` share one `BytesIO` and one `_write_pos` (`tests/conftest.py:142-186`).
**Avoid:** feed the entire response script before the drive, as all three existing harnesses do.

---

## 14. Code Examples (in-repo patterns to follow)

### The fifth sibling gate, shaped after `flash4_erase_gate`

```python
# Source: firestarter_app/firestarter/flash4_erase_gate.py:37-80 (verbatim shape)
from __future__ import annotations

from typing import Any, Mapping  # noqa: UP035

FLASH4_PROTOCOL_ID = 5

_REFUSAL_FORMAT = "Erase not supported for {chip_name}"


def is_flash4(programmer_data: Mapping[str, Any] | None) -> bool:
    if not programmer_data:
        return False
    return programmer_data.get("algorithm") == FLASH4_PROTOCOL_ID


def refusal_text(chip_name: str) -> str:
    return _REFUSAL_FORMAT.format(chip_name=chip_name.upper())
```

Note `# noqa: UP035` on the `typing.Mapping` import — `UP` is in the ruff selection, so this one is
live and must be carried if the same import form is used. `page_size_gate.py:47-52` uses the identical
form. `[VERIFIED: flash4_erase_gate.py:37-80; page_size_gate.py:47-52]`

### The raise-on-refusal gate, shaped after `page_size_gate`

```python
# Source: firestarter_app/firestarter/page_size_gate.py:99-133 + exceptions.py
raise PageSizeUnavailableError(
    _REFUSAL_FORMAT.format(chip_name=chip_name.upper())
)
# ... rendered verbatim by cli_handlers.map_typed_errors:222-225:
#     except PageSizeUnavailableError as e:
#         raise click.ClickException(str(e)) from e
```

A new exception class belongs in `firestarter/exceptions.py`, subclassing `EpromOperationError` (as
`PageSizeUnavailableError` and `PageAlignmentError` both do), **with its own arm added to
`map_typed_errors` above the generic `EpromOperationError` arm at `:226`** — otherwise it is rendered
with the `"Programmer error: "` prefix. `[VERIFIED: exceptions.py:60-112; cli_handlers.py:192-233]`

### The additive accumulator field (§5.3 option i)

```python
# Source: firestarter_app/firestarter/compare.py:245-248 (the existing tier-3 branch)
        if self._first_offset is None:
            self._first_offset = address + offs[0] - self._addr_base
            # + one line here to capture actual[offs[0]] as the first differing byte
        self._bad += len(offs)
```

with the matching field on `CompareResult` beside `first_offset` (`compare.py:147`) and the matching
argument in `finalise`'s constructor call (`compare.py:324`).

---

## 15. State of the Art / what changed recently

| Old | Current | When | Impact on this phase |
|---|---|---|---|
| The firmware compared (`COMMAND_VERIFY`, `COMMAND_BLANK_CHECK`) | The host compares, through `compare.py` | Phase 202 (v1.41), 2026-09-20 | `_drive_region_compare` exists and is this phase's engine |
| `verify_eprom` returned `bool` | returns `int` (0/1/2) | 202-01 | the migration precedent for §7.C |
| `check_eprom_blank` returned `bool` | returns `int` (0/1/2) | 202-05 | ditto |
| Write-init blank check scanned the whole device on 0x07/0x08/0x0B | region-scoped via `mem_util_blank_check_region` | Phase 201 (v1.40) | criterion 5's property; still whole-device on 0x06/0x10, which D-04 improves host-side |
| No-comments-in-source rule | **removed** | 2026-09-19 | D-01/D-03/D-05/D-10 reasoning goes at its site |
| `mypy` watermark CI gate | **retired**; app CI is ruff + pytest --cov only | earlier in v1.4x | mypy must be run deliberately (C-4) |

`[VERIFIED: the first four from source read this session; the last two from /workspaces/CLAUDE.md and
.github/workflows/ci.yml]`

---

## 16. Package Legitimacy Audit

**This phase installs no external packages.** It adds one first-party module, edits five existing
first-party modules, and adds test modules. Every import it needs (`click`, `tqdm`, `pyserial`,
`syrupy`, `pytest`, `ruff`, `mypy`) is already a declared dependency in
`firestarter_app/pyproject.toml` and already resolved in `.venv311`.
`[VERIFIED: pyproject.toml [project].dependencies and [project.optional-dependencies].test, read this session]`

No `package-legitimacy` check was run because no package is being added. If the plan later proposes
one, run the gate before the plan is approved.

---

## 17. Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| Python 3.11 venv | every test/lint leg | ✓ | `.venv311` → 3.11.16 | `.venv-ci-188` (also 3.11.16) |
| `pytest` | all tests | ✓ | 9.1.1 | — |
| `syrupy` | the two help snapshots | ✓ | present in `.venv311` | — |
| `ruff` | CI gates 1-2 | ✓ | 0.16.8 | — |
| `mypy` | pre-commit only (not CI) | ✓ | 2.3.1 | — |
| `click` | CLI | ✓ | 8.5.0 | — |
| `pytest-timeout` | — | ✗ | — | not needed; do not pass `--timeout` |
| `.venv` | — | ✗ **broken** (no `bin/python`) | — | use `.venv311` |
| A real Arduino board | **D-17's harnessed measurement only** | ✗ (phase is bench-no) | — | **derive from 176-MEASUREMENT.md** (§7.E) — this is the recommended route |
| `firestarter_fw` checkout | §3 evidence reading | ✓ | present at `/workspaces/firestarter_fw` | — |

**Missing with no fallback:** none.
**Missing with fallback:** the bench board — §7.E's derivation is the fallback, and it rests on a real
prior measurement rather than a guess.

---

## 18. Security Domain

`security_enforcement` is absent from `.planning/config.json`, so it is enabled. This phase is a local
CLI driving a USB serial device; there is no network surface, no authentication, no session, no
persistence of user data, and no cryptography.

| ASVS category | Applies | Standard control here |
|---|---|---|
| V2 Authentication | no | no identity concept |
| V3 Session Management | no | serial link, no sessions (the Phase 206 "session lease" is a transport-lifetime concept, not a security one) |
| V4 Access Control | no | single local user |
| **V5 Input Validation** | **yes** | `-a`/`--address` and the input file length are the only untrusted inputs. The existing pure gates (`require_page_size`, `require_page_alignment`, `_region_refusal_exit_code`) are the pattern. **The folded negative-address todo is literally a V5 defect** (§10) — an unvalidated signed integer reaching a region computation. |
| V6 Cryptography | no | none used on this path |

| Pattern | STRIDE | Mitigation in this phase |
|---|---|---|
| Out-of-range / signed region arithmetic reaching the device | Tampering | §10's fix; the guard and `--verify` both derive their region from the same validated `address` |
| A refusal message disclosing a workaround that routes around a correct refusal | Information disclosure (of the wrong kind) | D-10's no-remedy-clause rule, following `flash4_erase_gate.refusal_text`'s stated reasoning |
| A guard silently inert because it reads an absent dict key | Tampering / failure of a safety control | §4.2.1 — key on `algorithm`, or hard-fail. This is the highest-consequence security-shaped risk in the phase, because after Phase 205 this guard is the **only** protection against an irreversible UV overwrite. |

The last row deserves emphasis in the plan: D-01 calls the predicate "the whole safety net after Phase
205". A predicate that never fires is indistinguishable from a passing test suite, and
`check_eprom_blank`'s vacuous short-circuit proves that failure mode has already happened once in this
codebase.

---

## 19. Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | Adding a field to `CompareAccumulator`/`CompareResult` does not break `tests/test_compare.py`'s 2922-case corpus-equivalence test. Reasoned from reading the AST gate and the import-set gate, **not** executed — the field does not exist yet. | §5.3 | Low. If wrong, the plan discovers it in the first task's test run; the fix is to construct the corpus comparison on the pre-existing fields only. |
| A2 | The read-phase frame script for a `_FakeSerial`-backed guard read can be built from the idioms already in `tests/test_eprom_operations.py`. Not built and run this session. | §2.5 A | Medium — this is the task most likely to be under-scoped. Budget it as its own task and prove the negative control first. |
| A3 | `dev test`'s existing test modules pass unchanged after the guard lands. Reasoned from the flag analysis in §11.1; not executed against a modified tree. | §11.1 | Medium. They use `FakeChip`/`Mock` operators, so they *should* be immune, but `test_chip_test_uv_slot_write.py`'s `write_flags_seen` legs are the ones to watch. |
| A4 | §7.E's derived session-cost arithmetic (2 × median connect) is what Phase 206's SESS-02 needs. The connect medians are measured; the *addition* is this document's reasoning. | §7.E | Low, if recorded as a derivation with its provenance visible. High, if recorded as "203 measured 5.04 s" — that would be a fabricated measurement. State the derivation explicitly. |
| A5 | The read-rate figures (8.7 KB/s on 0x07, 7.0 KB/s on 0x08) are usable as an order-of-magnitude term. They come from a single operator log and the note itself says "this is a model built on one sample, not a benchmark". | §7.E | Low if cited as single-sample; misleading if quoted as a rate. |
| A6 | `_dispatch_sdp_leg` is reached only for protocol-0x0D parts. Inferred from `sdp_capability`'s gate at `chip_test.py:725` and `sdp_capability_for_entry`'s `protocol_id != SDP_PROTOCOL_ID` refusal; the full `derive_plan` path was not traced end to end. | §11.1 | Low — even if a non-0x0D part reached it, the guard would behave exactly as it does for any other write. |

---

## 20. Open Questions

1. **Which predicate form (A1/A2/A3) does D-02's test pin?**
   - Known: unobservable on every shipped database row (§7.A); differs only for an unknown non-zero
     algorithm from a user override DB.
   - Unclear: whether the operator's "preserve today's coverage" instruction should be read as
     forbidding A3's one-protocol widening even though no shipped row exercises it.
   - Recommendation: planner decides and writes the reasoning at the site; flag it to the operator at
     plan review as a one-line confirmation, not a blocking question.

2. **Does `--verify` live at the CLI tier or inside `write_eprom` (§7.C)?**
   - Known: C1 is far cheaper and reuses `verify_eprom`'s region resolution for free; C2 costs a
     return-type migration across ~40 test sites.
   - Unclear: whether D-14's suppression of **two** "successful" lines under C1 is acceptable, or
     whether the operator would rather see one suppression point.
   - Recommendation: C1 with an explicit suppression parameter, unless the plan-checker objects.

3. **Does the guard read show a progress bar (§7.D)?**
   - Known: it does by default; suppression has a clean precedent; a guarded `write --verify` would
     otherwise show three bars.
   - Recommendation: Claude's discretion per CONTEXT — but state the choice and its reason in the
     code, because "three bars" is exactly the kind of surprise that generates a UAT rejection.

4. **Is the derived D-17 figure acceptable, or does the operator want a bench run?**
   - Known: `measure_connect_cost` requires a board; the phase is bench-no; a real prior measurement
     exists.
   - Recommendation: derive, record the provenance, and offer the bench run as an operator option.

5. **Should `check_eprom_blank`'s vacuous SRAM short-circuit (§4.2.1) be filed?**
   - Known: it is a live defect on `blank`, not on `write`; none of WRITE-01..06 covers it.
   - Recommendation: file a todo, do not fold. It is Phase 205/206 territory at the earliest, and
     folding it would widen this phase.

---

## Sources

### Primary (HIGH confidence — read from live source this session)

- `firestarter_app/firestarter/eprom_operations.py` — `write_eprom` (2080-2229), `_drive_region_compare`
  (2230-2333), `verify_eprom` (2336-2461), `check_eprom_blank` (2596-2683), `_operation_context`
  (582-624), `_setup_operation` (502-570), `_run_state_machine` (632-690), `_main_phase_read_data`
  (915-1000), `ClassProgressHandler` (369-411), `measure_connect_cost` (1837-1907),
  `_summarize_connect_samples` (1797-1835), `write_cycle_eprom` (1296-1307), `_blank_expected_bytes`
  (332-341), `CONNECT_COST_STRUCTURAL_FLOOR_S` (93-96), `READ_ABORT_ACCEPTANCE_WINDOW_S` (99-108)
- `firestarter_app/firestarter/cli_handlers.py` — `write` (562-793), `_region_refusal_exit_code`
  (796-899), `verify` (906-966), `blank` (968-1023), `map_typed_errors` (192-233), `_build_op_flags`
  (318-360), `_setup_logging` (105-126)
- `firestarter_app/firestarter/compare.py` — read in full
- `firestarter_app/firestarter/flash4_erase_gate.py` — read in full
- `firestarter_app/firestarter/page_size_gate.py` (136-182), `sdp_capability.py` (110-205),
  `exceptions.py` (read in full), `address_parser.py` (read in full), `constants.py` (108-132),
  `database.py` (495-582), `chip_resolver.py` (16-73), `serial_comm.py` (970-1015),
  `protection_readability.py` (106-111), `transport_counters.py` (1-50)
- `firestarter_app/firestarter/chip_test.py` — 3031-3055, 3195-3245, 3420-3490, 725
- `firestarter_app/tests/fake_chip.py` — read in full
- `firestarter_app/tests/conftest.py` (133-231), `tests/test_eprom_operations.py` (330-405, 2240-2320),
  `tests/test_compare.py` (534-606, 1359-1394), `tests/test_connect_cost_harness.py` (1-110),
  `tests/test_characterization.py` (165-185, 460-477),
  `tests/__snapshots__/test_characterization.ambr` (363-416, 1394-1447),
  `tests/test_chip_test_blank_check_order.py` (1-60)
- `firestarter_fw/src/proms/eprom.cpp` (120-155), `flash_nor_unlock.cpp` (70-110),
  `flash_intel.cpp` (68-100), `flash_5v_page.cpp` (64-80), `memory.cpp` (40-145);
  `firestarter_fw/include/proto_constants.h` (read in full)
- `firestarter_app/pyproject.toml`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml`,
  `firestarter_app/CLAUDE.md` (§ What CI runs), `/workspaces/CLAUDE.md`
- `firestarter_app/firestarter/data/chip_database.json` — 746 rows, tabulated this session

### Primary (HIGH confidence — measurement executed this session)

- `pytest tests/` on `.venv311` → 2216 passed, 196.44 s
- `pytest --cov=firestarter --cov-fail-under=70` → 85.80 %, 6371 statements
- `ruff check` / `ruff format --check` / `mypy` → clean
- `resolve_chip(...)` for 6 chips → the wire-dict key census (§4.2)
- the SRAM short-circuit probe (§4.2.1) — a falsification attempt that **succeeded in refuting** the
  assumption that the short-circuit is live
- `click.ClickException.exit_code` → 1 (§7.B)
- `diff` of the two `.ambr` snapshot bodies → identical

### Secondary (MEDIUM confidence — prior recorded artefacts, cited not re-measured)

- `.planning/milestones/v1.36-phases/176-…/176-MEASUREMENT.md` §4a/§4b — the connect-cost medians
- `.planning/phases/202-one-comparison-engine-on-the-host/202-READ-ABORT-ANSWER.md` — the ≤1 s abort
  cost and its three firmware facts
- `.planning/phases/202-one-comparison-engine-on-the-host/202-REVIEW.md` — CR-01 (fixed), WR-01
  (3.0 s window untested at its boundary — `write --verify` drives the same discrimination), WR-02,
  IN-01
- `.planning/notes/dev-test-sequence-cost-model.md` — single-sample read/write rates, explicitly
  self-labelled as a one-sample model
- `.planning/todos/pending/2026-09-16-reject-negative-write-start-address.md`,
  `2026-08-30-write-init-blank-check-is-whole-device.md`,
  `2026-09-08-uv-write-shortcut-disclosure-key.md`

### Not used

- No web search was performed. Every question this phase raises is answered by first-party source in
  this repository, which is a strictly more authoritative source than any external one for these
  claims.
- The knowledge graph (`.planning/graphs/graph.json`) is **221 commits behind** and was deliberately
  not used; every relationship in this document comes from direct reads of current source.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| Firmware guarded-set table (§3) | **HIGH** | Every cell re-read from `firestarter_fw` source with the conditional quoted verbatim |
| Host path line numbers and signatures (§4, §5) | **HIGH** | Read from live source this session; the one CONTEXT drift (`write` starts at 562, not 733) is corrected |
| The missing byte value (§5.3) | **HIGH** | The full `CompareResult` field list and the `expected` callback signature were both read; the absence is structural, not inferred |
| The `fake_chip.py` diagnosis (§2) | **HIGH** | Class declarations and the full dependant list read directly |
| The vacuous SRAM short-circuit (§4.2.1) | **HIGH** | A probe was run and it refuted the assumption; the repo's own `sdp_capability.py` comment corroborates independently |
| Database census (§6) | **HIGH** | Computed over all 746 rows this session |
| Toolchain and CI constraints (§1, Project Constraints) | **HIGH** | Every command executed; every config file read |
| Session-cost derivation (§7.E) | **MEDIUM** | The connect medians are real measurements; the arithmetic over them is this document's reasoning, and the read-rate term is a cited single-sample model |
| The design forks (§7) | **N/A — reported, not decided** | CONTEXT assigns these to Claude's discretion; the constraints on each are HIGH-confidence |

**Research date:** 2026-09-21
**Valid until:** ~2026-10-21 for the firmware and requirements facts (stable). **Until the next commit
to `firestarter_app`** for every line number — re-verify before quoting a line in a plan task, since
this phase itself will move most of them.
