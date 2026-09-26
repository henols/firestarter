# Stack Research — v1.30 SDP Surface Retirement & Behavioral Lock Proof

**Domain:** Mature host-only Python CLI (`firestarter_app`), single-repo change
**Researched:** 2026-08-03
**Confidence:** HIGH on everything measured on this tree (the mypy mechanism, the 69-error count and its distribution, every file:line claim, the channel-gating mechanism). MEDIUM on the two external version facts (mypy's minimum-target policy history, Python EOL dates) — both cross-checked against a live source *and* reproduced locally.
**Tree measured:** `firestarter_app` @ `16a313a` (branch `beta`), `firestarter` @ `0933bd7`, meta @ `d1b9ce9e`.

---

## Headline

**Zero new dependencies. Zero new frameworks. Zero version bumps.** Every one of the six scope
items is served by tooling already pinned in `pyproject.toml` and by harnesses already committed
in `tests/`. The only *stack-shaped* decision this milestone owes is a **one-line semantic
correction to `[tool.mypy] python_version`** plus a **rewrite of `count_mypy_errors()`'s
result-interpretation**, and the only *version* decision is whether the project keeps claiming
Python 3.9 support it can no longer type-check.

The one thing that is genuinely different from what the planning record says: **the design note
and PROJECT.md conflate two distinct failures of the mypy gate**, and they occur in *different
environments*. Both are real; neither is what the other describes. §1 separates them.

---

## 1. The mypy gate — mechanism, measured, and the fix

### 1a. What is actually pinned, and what the project actually supports

| Fact | Value | Where | Status |
|------|-------|-------|--------|
| mypy pin | `mypy>=2.1.0` | `pyproject.toml` `[project.optional-dependencies] test` | **Original pin**, added `7acdcf3` "build(37-02)" on 2026-05-27 (Phase 37 / v1.8). Never raised, never lowered. |
| mypy resolved, CI | **2.3.0** (latest; changelog top section is 2.3) | fresh `pip install -e .[test]` | verified in a purpose-built venv |
| mypy resolved, devcontainer | **two of them on `PATH`** — `/home/vscode/.local/bin/mypy` = **2.3.0**, `/usr/local/py-utils/bin/mypy` = **2.1.0** | `which -a mypy` | verified |
| declared target | `python_version = "3.9"` | `pyproject.toml` `[tool.mypy]` | **dead config — has never once taken effect** |
| `requires-python` | `>=3.9` | `pyproject.toml` `[project]` | verified; classifiers list 3.9–3.12 |
| CI interpreter | **3.11** (both jobs) | `.github/workflows/ci.yml` `Set up Python 3.11` | verified — **not 3.12**; the "under Python 3.12" framing in PROJECT.md is a devcontainer fact, not a CI fact |
| devcontainer interpreter | 3.12.13 | `python3 -V` | verified |
| watermark | `35` | `pyproject.toml:` comment `# mypy_error_watermark = 35   # Updated Phase 71-07 …` | verified |
| ruff | `ruff>=0.15.14`, `target-version = "py39"` | `pyproject.toml` `[tool.ruff]` | verified; local ruff is 0.16.0 |

### 1b. (a) Why `python_version = "3.9"` is rejected — answered

**It is a mypy minimum-supported-*target* policy, not a stub conflict and not a distinct
minimum-runtime policy.** Reproduced verbatim on this tree:

```
$ mypy firestarter/ tests/
pyproject.toml: [mypy]: python_version: Python 3.9 is not supported (must be 3.10 or higher)
```

- **mypy 2.0** removed it: *"Mypy no longer supports type checking code with `--python-version 3.9`.
  Use `--python-version 3.10` or newer."* **mypy 1.20** was the last feature release that supported
  3.9 as a target, and separately dropped *running* under 3.9. (Live `python/mypy` `CHANGELOG.md`,
  cross-checked against the reproduced message.)
- The project's floor has been `>=2.1.0` since the pin was first written, so **the 3.9 target has
  never been honoured in this repo's history.** The watermark of 35 was set (Phase 71-07) against a
  checker that was already ignoring the declared target.

**The pyproject comment is wrong in a load-bearing way.** It reads:

> `python_version = "3.9"          # Must be in config file — mypy 2.1.0 rejects --python-version 3.9 via CLI flag`

Half true. Measured on mypy 2.3.0:

| Form | Behaviour | Exit |
|------|-----------|------|
| `--python-version 3.9` on the CLI | `mypy: error: argument --python-version: Python 3.9 is not supported (must be 3.10 or higher)` — argparse usage error, run never starts | **2** |
| `python_version = "3.9"` in the config file | **non-fatal note**, run proceeds, value **silently discarded** | 0/1/2 by content |

So moving the value into the config file did not make it work — it converted a loud refusal into a
silent no-op. **That is the deeper fail-open here** and it is not mentioned anywhere in the planning
record: *the project believes it type-checks against its py3.9 floor and does not, in CI either.*

**What mypy uses instead** (measured, not inferred): it clamps to its **minimum supported target,
3.10** — *not* to the running interpreter. Proved by branch-reachability probe: under the rejected
`3.9` config, `if sys.version_info >= (3, 10):` is analysed while `>= (3, 11)` and `>= (3, 12)` are
not, byte-identical to an explicit `python_version = 3.10`; with **no** config at all mypy uses the
interpreter (3.12) and the same probe reveals 3.12. This matters because the clamped-to-3.10 target
is what makes the numpy stub explode (§1c).

### 1c. The numpy stub conflict — what it actually is, and where it is

**Chain (traced, every hop verified):** `import pytest` (any of the 120 test/source files) →
`pytest` ships `py.typed` → `_pytest/python_api.py:21` `from numpy import ndarray` (under
`TYPE_CHECKING`, for `approx`) → numpy ships `py.typed` → `numpy/__init__.pyi:737`
`type _Falsy = L[False, 0] | bool_[L[False]]` — a **PEP 695 `type` statement**, which mypy only
accepts at target ≥ 3.12. At the clamped 3.10 target it is a **`[syntax]` error, which is
blocking**:

```
/usr/local/lib/python3.12/site-packages/numpy/__init__.pyi:737: error: Type statement is only supported in Python 3.12 and greater  [syntax]
Found 1 error in 1 file (errors prevented further checking)
EXIT=2
```

- **numpy present:** 2.5.1, at `/usr/local/lib/python3.12/site-packages` — a **devcontainer**
  artifact. Nothing in `firestarter_app` references numpy (`grep -rn numpy` over `*.py`/`*.toml`/
  `*.cfg`: **zero hits outside site-packages**).
- **Is it still present?** Yes, locally. **No, in CI.** A fresh `pip install -e .[test]` resolves
  pyserial · requests · tqdm · click · rich · packaging · pytest · syrupy · ruff · mypy ·
  pytest-cov · types-pyserial and pulls **no numpy** (verified by building exactly that venv:
  `import numpy` → `ModuleNotFoundError`).
- It is **not** fixable by a `follow_imports = "skip"` override on `numpy.*` — tried; the stub is
  still *parsed*, so the syntax error fires before any follow-imports policy applies.

### 1d. The two distinct failures — separate them before scoping

| | Devcontainer (py3.12, numpy installed) | CI (`ubuntu-latest`, py3.11, no numpy) |
|---|---|---|
| mypy behaviour | blocking stub syntax error, **run truncated after 1 file** | full run, **120 source files checked** |
| mypy exit | **2** | **1** |
| mypy summary line | `Found 1 error in 1 file (errors prevented further checking)` | `Found 69 errors in 17 files (checked 120 source files)` |
| gate's regex `Found (\d+) errors?` | **matches → returns 1** | matches → returns 69 |
| gate verdict | `1 <= 35` → prints `INFO: … below watermark` → **exit 0, GREEN** | `69 > 35` → **exit 1, RED** |

**Verified against the real CI run.** `gh run view 30708836339` (Host CI, `workflow_dispatch`,
2026-08-01): every step before it green, `X mypy type check (watermark gate)` — *"Process completed
with exit code 1"* — `pytest` and the entry-point smoke test **never ran**. The RED is exactly and
only this gate. It is also *quiet*: `ci.yml`'s `push` trigger is `branches: [main]` only, so pushes
to `beta` fire `beta-release.yml` and never `ci.yml`. The gate is red on PRs and manual dispatch and
invisible otherwise.

### 1e. The real bug in `tools/check_mypy_watermark.py` — one line

The module's docstring and comments *claim* fail-closed ("a broken type checker must fail the gate,
never be mistaken for a clean tree", exit 2 documented). The `sys.exit(2)` arm is real. **It is
simply unreachable on the failure that actually happens**, because the regex is consulted *before*
`result.returncode`:

```python
    output = result.stdout + result.stderr
    m = re.search(r"Found (\d+) errors?", output)
    if m:
        return int(m.group(1))          # <-- returncode never examined
    if result.returncode == 0 or "Success: no issues found" in output:
        return 0
    ...sys.exit(2)
```

mypy emits `Found N errors …` on the truncated path too. So a run that checked **1 of 120 files**
and exited **2** is indistinguishable from a clean-ish tree. The gate cannot tell *"3 errors in a
complete run"* from *"3 errors and then mypy stopped"*.

Two secondary defects in the same function:

- **`["mypy", …]` — a bare `PATH` lookup.** In this devcontainer that is ambiguous: `mypy` resolves
  to 2.3.0 but `/usr/local/py-utils/bin/mypy` (2.1.0) is also on `PATH`. A `PATH` reorder silently
  changes the checker *version*, hence the error population, hence the watermark's meaning. In CI it
  happens to be unambiguous — which is exactly why the defect survived.
- **A `FileNotFoundError` if mypy is absent** propagates as a traceback (non-zero, so fail-closed by
  accident, with a useless message).

### 1f. (c) The fix shape — recommended, with the tradeoff named

**Recommendation: three changes, all inside two files, no new dependency.**

**FIX-1 — `python_version = "3.10"` in `[tool.mypy]`, and say why in the comment.**

*Why this shape and not the others:*

| Option | Verdict |
|--------|---------|
| **`python_version = "3.10"`** ✅ | **Zero behaviour change** — 3.10 is *already* what mypy has been using (measured, §1b). The error count before and after is identical, so it cannot mask or manufacture a single error. It replaces a silent lie with the honest truth and removes the note from every CI log. |
| `--python-version 3.10` on the CLI | Works, but splits the target across two files and reintroduces exactly the confusion the current comment records. Config is the right home. |
| Drop the 3.9 target *by dropping 3.9 support* (`requires-python = ">=3.10"`, drop the 3.9 classifier) | **Defensible and arguably overdue** — Python 3.9 reached EOL **2025-10-31**, nine months ago. But it is a **published-metadata breaking change** for a package on PyPI, orthogonal to this milestone's six items, and it needs an operator decision, not an implementer's. **Recommend: keep `>=3.9` in v1.30, flag it as its own backlog item.** |
| Keep 3.9 and pin `mypy>=1.20,<2` | ❌ Reverses 9 months of tool currency, forfeits mypy 2.x's `--local-partial-types`/`--strict-bytes` defaults, and buys a target for an EOL interpreter. |

**⚠ The honest cost of FIX-1, which must be recorded:** after it, **nothing type-checks against the
py3.9 floor the package still advertises.** The mitigation already exists and should be named
explicitly rather than assumed: **`[tool.ruff] target-version = "py39"`** (verified) carries the
py39 *syntax/idiom* floor — pyupgrade (`UP`) will not rewrite past py39, and py3.10-only syntax is
a ruff error. What ruff cannot catch is a py3.10+ **stdlib API** used on a 3.9 interpreter. That
residual gap is real, is not new (it has existed since 2026-05-27), and its correct closure is
either a py3.9 CI matrix leg or dropping 3.9 — **not** something the mypy config can do any more.
**⚠ And note the treadmill:** Python **3.10 EOLs 2026-10-31**, ~3 months out. A future mypy 3.x
clamping to ≥3.11 will re-fire this exact failure. FIX-2 is what makes that arrive as a red gate
instead of a silent green.

**FIX-2 — make the gate fail CLOSED. Three assertions, in this order.**

```python
    result = subprocess.run(
        [sys.executable, "-m", "mypy", "firestarter/", "tests/"],   # (i)
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    output = result.stdout + result.stderr

    # (ii) mypy's contract: 0 = clean, 1 = errors found, ANYTHING ELSE = the
    # checker did not complete (usage error, bad config, blocking stub error).
    if result.returncode not in (0, 1):
        print(f"ERROR: mypy exited {result.returncode} — the type checker did "
              f"not complete. This is a tool/config failure, not a clean tree.\n"
              + output.strip(), file=sys.stderr)
        sys.exit(2)

    # (iii) require the COMPLETION half of the summary line, not just a count.
    found = re.search(
        r"^Found (\d+) errors? in \d+ files? \(checked (\d+) source files?\)$",
        output, flags=re.MULTILINE)
    clean = re.search(
        r"^Success: no issues found in (\d+) source files?$", output, flags=re.MULTILINE)
    ...
    # (iv) and pin the coverage floor: a run that checked far fewer files than
    #      the tree contains is a truncated run wearing a plausible number.
    if checked < MIN_CHECKED_SOURCE_FILES:   # commit the measured 120
        sys.exit(2)
```

- **(i) `sys.executable -m mypy`** — binds the checker to the interpreter running the gate, killing
  the two-`mypy`-on-`PATH` ambiguity. Zero cost in CI (`pip install -e .[test]` puts both in the
  same env). Also turns "mypy not installed" into a legible `No module named mypy` instead of a
  `FileNotFoundError` traceback.
- **(ii) returncode before regex** — this single reordering is *the* fix. It flips the devcontainer
  from GREEN to exit 2, measured.
- **(iii) require `(checked N source files)`** — the discriminator. Measured: the truncated path
  emits `(errors prevented further checking)` and **no** `checked` clause; a complete run always
  emits `(checked N source files)`. Requiring the completion clause makes the truncated shape
  unparseable → exit 2, *even if* a future mypy returns 1 on it.
- **(iv) `MIN_CHECKED_SOURCE_FILES`** — the belt to (iii)'s braces, and the direct analogue of this
  project's own repeated lesson (`reference_dev_test_absent_chip_false_green_trap`; the gating
  note's own risk R4): **assert the coverage of the check, not just its verdict.** Commit the
  measured **120** with a comment saying it is a floor to be raised, not a target.

**Do NOT switch the gate to `mypy --output json`.** Measured: JSON mode emits one object per
diagnostic and **no summary line at all** — it silently discards the `checked N source files`
signal that (iii) and (iv) depend on, while still exiting 2 on the truncated path. It is strictly
worse for this gate.

**FIX-3 — a fail-provable test for the gate itself.** The gate has no paired pytest today
(`tests/` has `test_check_*` modules for six other `tools/check_*.py` checkers — `check_dispatch`,
`check_no_log_in_sdp_window`, `check_no_exists_proxy`, `check_no_community_support_status_write`,
`check_devtest_orchestrator`, `check_sdp_capability` — and **none** for
`check_mypy_watermark.py`). This is the tool that was fail-open for two months; it earns the
project's own anti-hollow contract. The pattern is committed and reusable: an env-override seam
(`FIRESTARTER_DEVTEST_SRC` in `tools/check_devtest_orchestrator.py`) plus a planted-violation
fixture under `tests/fixtures/`. Here the natural seam is a fake-mypy stub whose stdout is a
canned summary line: feed it the truncated shape and assert **exit 2**; feed it
`Found 200 errors … (checked 120 source files)` and assert **exit 1**; feed it
`Found 3 errors … (checked 4 source files)` and assert **exit 2** on the coverage floor.
`tests/fixtures/` is already `extend-exclude`d from ruff for exactly this purpose (verified,
`[tool.ruff] extend-exclude = ["tests/golden", "tests/fixtures"]`).

**Explicitly NOT recommended: a pinned venv for the gate.** It would make the checker version
reproducible, but CI already gets that from `pip install -e .[test]` in a clean runner, and a second
venv adds an install step, a cache key, and a way for the gate's mypy to drift from the developer's.
`sys.executable -m mypy` gets the determinism that actually matters for a third of the cost.

---

## 2. The 69 errors — re-measured, not repeated

**Measurement method (so it is reproducible):** a purpose-built py3.12 venv installed with exactly
`ci.yml`'s `.[test]` closure and nothing else (therefore **numpy-free**, matching CI), running
`mypy --no-incremental firestarter/ tests/` from the repo root against the committed
`pyproject.toml`. Resolved: mypy 2.3.0, pytest 9.1.1, click 8.4.2, rich 15.0.0, requests 2.34.2,
tqdm 4.70.0, packaging 26.2, pyserial 3.5, syrupy 5.5.3, types-pyserial 3.5.0.20260712.

```
Found 69 errors in 17 files (checked 120 source files)      EXIT=1
```

**69 confirmed independently.** Watermark 35 ⇒ **gap +34**.

**Cross-check that rules out a tooling artefact:** re-running with `--no-local-partial-types
--no-strict-bytes` (the two defaults mypy 2.0 flipped on) yields **exactly 69**. So **none** of the
drift 35 → 69 is a mypy-2.x default change; it is all accreted code. Also measured:
`mypy firestarter/` alone = **25 errors in 6 files (checked 28 source files)** ⇒ **44 of the 69 are
in `tests/`**.

### 2a. Distribution by file

| File | Errors | Class |
|------|-------:|-------|
| `firestarter/eprom_operations.py` | 10 | **structural**, one root cause |
| `tests/test_dev_test_cmd.py` | 9 | 6 cheap + 3 cheap |
| `tests/test_write_skip_sdp_unlock.py` | 7 | cheap |
| `tests/test_write_skip_erase_0x0d.py` | 6 | cheap |
| `tests/test_validate_family_cmd.py` | 6 | cheap |
| **`tests/test_dev_sdp_cmd.py`** | **6** | **cheap — and this milestone DELETES this file** |
| `firestarter/database.py` | 6 | 3 cheap + 3 structural |
| `tests/test_serial_comm.py` | 3 | cheap |
| `tests/test_revision_constants_parity.py` | 3 | cheap |
| `firestarter/firmware.py` | 3 | moderate |
| `firestarter/config.py` | 3 | cheap |
| `firestarter/ic_layout.py` | 2 | 1 cheap + 1 structural |
| `tests/test_provenance.py` · `tests/test_protocol_not_implemented_production_path.py` · `tests/test_eprom_database.py` · `tests/test_characterization.py` · `firestarter/submit.py` | 1 each | cheap |

### 2b. Distribution by error class

| Code | Count | Cheap or structural |
|------|------:|---------------------|
| `[arg-type]` | **39** (36 in `tests/`, 3 in `firestarter/`) | **cheap** — 30 of the 39 are one single pattern |
| `[union-attr]` | **10** (all `eprom_operations.py`) | **structural** — one root cause |
| `[assignment]` | 7 | 4 cheap, 3 structural |
| `[var-annotated]` | 6 | **cheap** — pure annotations |
| `[attr-defined]` | 4 | cheap |
| `[func-returns-value]` | 3 | **cheap** — trivial |

*(28 `[annotation-unchecked]` lines also appear; those are `note:` severity, not errors, and are
correctly excluded from the 69.)*

### 2c. The two clusters that dominate

**Cluster A — 30 errors, one pattern, mechanically cheap.** Exactly **6 per file × 5 files**:
`test_dev_test_cmd.py`, `test_write_skip_sdp_unlock.py`, `test_write_skip_erase_0x0d.py`,
`test_validate_family_cmd.py`, `test_dev_sdp_cmd.py`. Every one is
`Argument "<field>" to "AppContext" has incompatible type "object"; expected "<RealType>"` —
the `make_app_context(**overrides: object)` factory at `tests/test_dev_test_cmd.py:84` (verified)
declares its overrides as `object` and forwards them into a typed dataclass. **One fix — narrow
`overrides` to a `TypedDict`/`Unpack`, or `cast()` at the five forwarding sites — retires all 30.**
The pyproject watermark comment already identifies six of these as "6 AppContext mock-type errors";
it is the same defect replicated five times.

**Cluster B — 10 errors, one root cause, structural *and politically fenced*.** All ten are
`Item "None" of "SerialCommunicator | None" has no attribute …` at
`eprom_operations.py:467, 471, 514, 526, 564, 590, 593, 620, 638, 1655` — an `Optional`
connection attribute that is never narrowed after setup. One decision (assert-once, a non-Optional
accessor property, or a restructure) retires all ten. **But `firestarter.eprom_operations` is
*deliberately* outside the strict island** per D-07's "GATE-1.8d read-path ring-fence, deferred to
v1.9 post-RCA" (verified in `pyproject.toml`'s `follow_imports = "silent"` override block) — so
touching it is a **policy** question, not just a typing one. And **this milestone opens that exact
file anyway** (`sdp_lock`/`sdp_unlock` are declared load-bearing survivors). Decide the ring-fence
question deliberately at scoping; do not let it be answered as a side effect.

### 2d. The watermark arithmetic — and the good news

| Step | Errors | vs watermark 35 |
|------|-------:|----------------:|
| today | **69** | +34 (RED) |
| after deleting `tests/test_dev_sdp_cmd.py` (scope item 1, **free**) | **63** | +28 |
| \+ Cluster A's remaining 24 (one factory fix) | **39** | +4 |
| \+ the 6 `[var-annotated]` annotations (`database.py:174,175,325`, `ic_layout.py`) | **33** | **−2 → GREEN** |
| \+ Cluster B (optional) | **23** | −12 |

**Load-bearing finding for the roadmap: the primary `ci` job can be made GREEN at the *existing*
watermark of 35 without touching the ring-fenced `eprom_operations.py` union-attr cluster at all.**
The path is: the deletion the milestone already does, one test-factory fix, and six annotations.
Cluster B becomes an *optional* extra credit rather than a blocker — which is the difference
between a scoped phase and an open-ended one.

**Sequencing note:** the deletion (item 1) drops the count by 6 **for free**, so land it *before*
re-baselining the watermark, or the new number will be wrong within the same milestone.

**Two smaller measured facts worth recording:**

- The strict-island invocation named in `pyproject.toml`'s own comment (*"so `mypy <strict-list>`
  exits 0"`*) is **no longer true**: running mypy over the eight D-06 strict modules yields
  `Found 1 error in 1 file (checked 8 source files)` — `firestarter/submit.py:666`. `submit.py`,
  `chip_test.py`, `diagnostic_report.py`, `sdp_capability.py`, `channel.py`, `py32_dfu.py` were all
  added after Phase 42 and appear in **neither** override list. There is no CI step behind that
  claim, so it is stale documentation rather than a hole — but the new leg's code lands in
  `chip_test.py` and `diagnostic_report.py`, i.e. squarely in the unclassified set. Assign them.
- Test suite baseline: **1303 tests collected** (`pytest --collect-only`, 0.37s). PROJECT.md's
  "~1293 as of v1.23" is 10 low.

---

## 3. Test tooling for the new SDP leg — everything needed is already committed

### 3a. Can the host reach the Phase 116 trace harness? **No.**

The harness exists and is exactly what the design note says it is:

- `firestarter/test/native/avr/test_sdp_harness/` (Phase 116 Plan 05) — the **always-green** SDP
  suite. Proves the ordered strobe recorder captures production register-cache elision, and that
  it can **tell UNLOCK from LOCK from ERASE** via two index-precise planted-fault negatives
  (TRACE-03a/b). Pins the **production** tables by external linkage:
  `extern const byte_flip_t EEPROM_SDP_ENABLE[3]` and `EEPROM_SDP_DISABLE[6]`.
- `firestarter/test/native/avr/test_eeprom28c_sdp/` (Plan 06) — the **parked, RED-by-design** twin.

But these are **PlatformIO `[env:native]` Unity/C++ binaries in the firmware repo**, one statically
linked executable per directory, run by `pio test -e native`. The host `ci` job installs Python
deps only; there is no `pio`, no C++ toolchain, and **`firestarter` is declared untouched this
milestone**. Conclusion: **the trace harness is reachable only by a firmware-repo command, and is
therefore out of scope as an executable gate for v1.30.** It can be *cited* as the source of the
emission proof (it already shipped that proof in v1.22); it cannot be *run* as part of this
milestone's evidence.

### 3b. Is a *locked part* representable in a host-side stub? **No — and the answer is the same on the firmware side.**

This closes the open question in `research/questions.md`.

- **Firmware native side:** the recorder hooks `rurp_write_data_buffer` + `rurp_set_control_pin` and
  records an ordered *bus stream*. It models the **bus**, never the **die**. There is no state
  machine anywhere in it that would begin refusing writes after observing the lock sequence.
  Representing a locked part would mean authoring a new **stateful 28C die model** — new firmware
  test code, i.e. out of scope.
- **Host side:** there is no bus stub *at all*. `tests/test_dev_test_cmd.py` builds its world from
  `Mock(spec=EpromOperator)` (`make_app_context` at `:84`, `make_clean_operator` at `:110`). A
  "locked part" there is a **scripted return-value sequence** — trivially representable, and
  trivially worthless as silicon evidence.

**State this split in the phase's own words, or the milestone closes claiming a proof it does not
hold** (PROJECT.md already names this as the v1.22 C-5 overclaim class).

### 3c. What *can* carry the inverted assertion — named files, already committed

**The best host-side oracle is the fake-serial seam, not the operator mock.** `tests/conftest.py`
ships (all verified):

| Symbol | Line | What it gives the new leg |
|--------|-----:|---------------------------|
| `build_frame(msg_id, params)` | `tests/conftest.py:96` | assembles a real wire frame — magic ǀ len_u16 ǀ id ǀ params ǀ crc8 ǀ 0x0A |
| `_ref_crc8_ccitt` | `:80` | independent CRC reference (not the production one) |
| `class _FakeSerial` | `:109` | BytesIO-backed `serial.Serial` stand-in |
| `fake_serial` fixture | `:165` | per-test instance |
| `make_comm` fixture | `:172` | a real `SerialCommunicator` over the fake |

`tests/test_dev_sdp_cmd.py` already imports `build_frame` for what its own docstring calls "the one
dedicated real-operator leg" — so **the precedent for driving a genuine `EpromOperator` over a
scripted wire already exists inside the very file being deleted.** The design note's instruction to
"repurpose the gate-ordering cases onto the new leg" should be read to include *this* mechanism,
which is the more valuable half.

**Concretely, the four assertions and where each lives:**

| Leg property to prove | Harness | Proves |
|---|---|---|
| the 4 steps are **plan-derived** for 43 ALLOW chips and `NA`/`SKIPPED`-with-reason for 41 REFUSE | pure `derive_plan(name, db)` unit test; no mocks at all (the pattern `tests/test_sdp_capability.py` + `test_sdp_db_invariant.py` already use) | **plan derivation** |
| **read-back equality** against pattern A is what decides the verdict | `_FakeSerial` + `build_frame`: script the read response to return pattern A; drive a real `EpromOperator` | **the oracle, end to end through the frame codec** |
| **Trap 2 sensitivity** — inhibited write *succeeds* ⇒ verdict **BAD**, never `SKIPPED`/`NA` | same seam, mutated script: read returns pattern **B** | the assertion points the right way. **This is the single highest-value new test in the milestone** and it is pure host Python. |
| **Trap 1** — a *partial* change reads BAD, never OK | feed a half-A/half-B image; assert the verdict and that `classify_fingerprint` (`chip_test.py:138`) does not launder it | gh#11's exact symptom |

`chip_test.py` already ships the pattern generators the leg needs — no new ones:
`generate_pattern(start, length)` (`:59`), `prepass_images(length)` (`:70`, returns a **two-image
tuple** — that is patterns A and B, already), `_diff_offsets` (`:93`), `Fingerprint` (`:128`),
`classify_fingerprint` (`:138`).

### 3d. Integration points the design note under-states

**⚠ `dedup_fingerprint` changes for all 43 ALLOW chips — and the design note says the opposite.**
The note claims the new ops are picked up "without learning a new field", which is true of the
*schema*. But `dedup_fingerprint` (`diagnostic_report.py:183`, verified) hashes
`f"{op}={verdict}:{cls}"` **per step, in order**. Adding four steps to a chip's plan therefore
**changes that chip's fingerprint value**. Consequence: `tools/parse_devtest_issue.py::count_agreeing`
groups *saved* report bodies by the already-embedded fingerprint and never re-hashes, so every
pre-v1.30 community report for a 43-ALLOW chip lands in a **different dedup group** — the N≥2
promotion count for those chips **resets to zero**. That is arguably correct (a different test was
run), but it is a real, user-visible consequence of the leg and it must be a stated decision, not a
discovery.

**Gates the new ops must keep green** (all six have paired fail-provable pytests, verified):

| Gate | Scans | Risk from the new leg |
|------|-------|-----------------------|
| `tools/check_devtest_orchestrator.py` | `chip_test.py`, `cli_handlers.py`'s `dev_test`, `submit.py` in full — **AST walk**, denies VPP-set call sites, raw wire-dict construction, and `force=True` pass-through | **High.** The leg's inhibited write must route through `EpromOperator` and must set `FLAG_SKIP_SDP_UNLOCK` via `build_flags` (`eprom_operations.py:200-209`), **never** by hand-assembling a command dict. Wire keys `cmd`/`flags` in a dict literal in `chip_test.py` = instant gate failure. |
| `tools/check_sdp_capability_invariants.py` | `firestarter/sdp_capability.py` | Low — the predicate is reused, not modified. `tests/fixtures/planted_widenable_allowset.py` and `planted_permit_by_default.py` are its planted negatives. |
| `tools/check_no_community_support_status_write.py` | `diagnostic_report.py` | Medium — new report rows must stay advisory; no DB `support_status` write. |
| `tools/check_no_log_in_sdp_window.py` | `../firestarter/src/proms/eeprom_28c.cpp` (cross-repo) | None — firmware untouched. |
| `tools/check_no_exists_proxy.py` | `tests/` | Medium — do not author a new `.exists()` skip proxy for the new leg; use `tests/fw_presence.py`'s `requires_fw`. |
| `tests/test_sdp_table_parity.py`, `test_sdp_bus_config_drift.py` | cross-repo `eeprom_28c.cpp` / `_shared/sdp_bus_config.h` | None — but they will **hard-fail** (`MissingScanTargetError`), not skip, if firmware paths move. |

**Cross-repo reach, and its one trap.** The host *can* read the sibling firmware repo:
`tests/fw_presence.py` resolves `FW_ROOT = <app>/../firestarter`, keys presence on the `.git`
marker, exposes `requires_fw` and `fw_path()` — and `fw_path()` **hard-fails** on a missing target
under a *present* repo rather than skipping (the Phase 123 BASE-02 fix for the fail-open A-7
defect). `tests/scan_paths.py` is the committed 6-path inventory. **⚠ Every one of these is a
source-text scan; none executes firmware.** And per
`reference_devcontainer_sibling_layout_masks_ci_test_defects`: the devcontainer's sibling layout
makes these pass locally while failing in a standalone CI checkout — point `FIRESTARTER_FW_ROOT` at
an empty dir *before* any `beta` push. Note `FW_ROOT`/`FW_REPO_PRESENT`/`requires_fw` bind **at
import**, so `monkeypatch.setenv` has no effect; a different root needs a **subprocess**.

**Snapshot tooling:** `syrupy>=5.0` is pinned and in use by 6 test modules
(`test_submit`, `test_characterization`, `test_eprom_info`, `test_config`,
`test_audit_coverage_matrix`, `test_serial_comm`). The new report rows and the Trap-3 recoverability
line are a natural snapshot target — **already available, nothing to add.**

---

## 4. Channel gating (999.15 / gh#8) — the mechanism exists; the surface it gates does not

### 4a. What is already built

`firestarter/channel.py` (81 lines, read in full — verified):

| Symbol | Line | Behaviour |
|--------|-----:|-----------|
| `is_prerelease_build()` | 36 | PEP 440 pre-release check on `firestarter.__version__` (currently `3.0.0b15`). **Fails CLOSED** — `InvalidVersion` ⇒ treated as stable ⇒ gated feature stays hidden. |
| `BETA_ONLY_BOARDS` | **33** | `("py32f071",)` — *"graduates by deletion from this tuple"* |
| `is_board_available(board)` | 60 | False only for a beta-only board on a stable build |
| `available_boards(boards)` | 68 | order-preserving filter |
| `beta_only_message(board)` | 73 | the single shared refusal text |

**The module already internalised the `${sysenv.VAR}` lesson, verbatim in its own docstring:**
*"Nothing here reads the environment. A channel gate that can be flipped by an env var is not a
gate — the firmware side already learned that `-D X=${sysenv.VAR}` fails OPEN."* **Do not add an
env-var override to this module.** (Note `tests/fw_presence.py` *does* have one env seam,
`FIRESTARTER_FW_ROOT` — that is a test-harness path seam, a different thing, and it is
deliberately root-only with the marker name hardcoded.)

And the **command-surface** half exists too, in `cli_handlers.py` (verified):
`_ALL_BOARDS:142` → `_BOARD_CHOICES:143` → `_PY32_ENABLED:144`, all **computed once at import
time** ("a wheel's `__version__` is fixed when it is built"), plus `_reject_py32_only_option:147`
called unconditionally at `:1087-1088`.

### 4b. ⚠ The fail-open that 999.15 will walk straight into

**`hidden=` is a `--help` cosmetic. It does not gate anything.** This is not inference — it is
documented in `_reject_py32_only_option`'s own docstring as the HOST-02 bug that helper exists to
close:

> `hidden=not _PY32_ENABLED` on an option's `@click.option` decorator is a `--help` cosmetic only:
> it keeps the option out of the rendered help text, it does not reject the option when a user types
> it anyway. That confusion is exactly the bug HOST-02 exists to close: on a stable build,
> `--usb-id` was accepted (exit 0) while `--dfu-probe` was refused (exit 2), even though both are
> py32-only surface.

`@dev.command(hidden=True)` behaves identically for a **command**: `firestarter dev reg …` stays
fully invokable, just undocumented. **999.15 must gate by not registering the command** — a
channel-derived command set, or a `click.Group` subclass filtering `list_commands`/`get_command` —
so an absent subcommand produces Click's own `No such command` / exit 2. Anything less is
security-by-help-text.

### 4c. What 999.15 needs on top — and how v1.30 shrinks it

Live `dev` group inventory (`cli_handlers.py`, verified). **The gating design note says eight
subcommands; there are now nine** — `sdp` landed after the note was written:

| # | subcommand | `@dev.command` | handler | stable channel (999.15) |
|--:|---|---:|---:|---|
| 1 | `read` | 1180 | 1192 | **KEEP** |
| 2 | `reg` | 1211 | 1253 | gate out |
| 3 | `addr` | 1273 | 1292 | gate out |
| 4 | `consistency-check` | 1310 | 1363 | gate out |
| 5 | `write-cycle` | 1400 | 1424 | gate out |
| 6 | `fault-inject` | 1453 | 1484 | gate out |
| 7 | `validate-family` | 1680 | 1704 | gate out |
| 8 | `test` | 2055 | 2059 | **KEEP** |
| 9 | `sdp` | 2196 | 2213 | **v1.30 DELETES — 999.15 never has to classify it** |

Needed on top of `channel.py`: **(1)** a command-level registration gate (§4b); **(2)** a
`dev`-group analogue of `_reject_py32_only_option`'s *single shared refusal path* for anything that
must refuse rather than vanish; **(3)** a reworded `dev` group docstring — it currently reads
*"Debug command for development purposes. USR button will break command and return."*
(`cli_handlers.py:1172-1175`), which actively warns off the stable users `dev read` + `dev test`
are being kept for.

**The test template is committed and its rationale is already written down.**
`tests/test_py32_channel_gating.py` uses **one subprocess per simulated version**, because
`_BOARD_CHOICES`/`_PY32_ENABLED` are import-time constants and an in-process monkeypatch of
`__version__` after `cli_handlers` is imported yields *"a test that would pass, but for the wrong
reason."* The same is true of any registration-time command gate. **⚠ Two fail-opens in the test
layer specifically:** (i) `is_prerelease_build()` returns **True** for a source checkout
(`2.0.7_dev`, and today's literal `3.0.0b15`), so **the devcontainer and CI always see the beta
surface** — a stable-behaviour test that forgets the subprocess passes **vacuously**; (ii) per the
gating note's own R4, assert on the **registered command set** (`dev.commands.keys()`) and the
`--help` surface, never on an exit code, because absent and present-but-broken exit identically.
Related and convenient: `tests/test_dev_test_cmd.py:185` already introspects `.commands` — and is
one of the 69 mypy errors (`"Command" has no attribute "commands"`, fixed by
`cast(click.Group, …)`).

Also carried forward from the gating note and **still live**: R3, the editable-install trap —
`dev reg 0 0 0x86 -f` is the held-erase-rail DMM proxy and is load-bearing bench tooling; a
source-checkout override must be designed **up front**. `fw --pre` / `--stable` already exist
(`cli_handlers.py:954` / `:969`) so no new firmware-channel flag is needed, and
`FIRMWARE_VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+((b|rc)[0-9]+)?\Z")`
(`firmware.py:52`) needs no widening as long as no `+dev` local-version segment is introduced.

---

## 5. What NOT to add — explicit

| Do NOT add | Why |
|---|---|
| **Any new runtime dependency** | Runtime closure is 6 packages (`pyserial>=3.5`, `requests>=2.20`, `tqdm>=4.60`, `click>=8.1`, `rich>=14.0`, `packaging>=21.0`) plus the optional `[py32] pyusb>=1.3.1,<2`. Every one of the six scope items is host-side logic, Click wiring, or test code. **A CLI that ships to PyPI pays for a new dependency on every user's install, forever, for a diagnostic leg.** |
| **A new test framework / property-based testing / a fake-hardware DSL** | pytest 9.x + `unittest.mock` + syrupy + `_FakeSerial` + `build_frame` cover all four of the leg's assertions (§3c). |
| **`hidden=True` as a gating mechanism** | Documented `--help` cosmetic; the HOST-02 bug class (§4b). |
| **Any env-var override in `channel.py`** | Its docstring forbids it and names the firmware `${sysenv.VAR}` fail-open as the reason. |
| **`mypy --output json` as the gate's input** | Measured: drops the summary line, therefore drops the `(checked N source files)` completion/coverage signal the fix depends on (§1f). |
| **A dedicated venv or a second mypy pin for the gate** | `sys.executable -m mypy` buys the determinism that matters at a fraction of the cost. |
| **Pinning mypy back to `<2`** | Would restore the 3.9 target by reversing 9 months of tool currency, to type-check for an interpreter that EOL'd 2025-10-31. |
| **A new option on `dev test`** | Zero options since Phase 121 D-05; the leg is plan-derived. `derive_plan`'s only kwarg is `write_scope` and `locked_destructive` is already permanently empty in production. |
| **A new `StepResult` field** | `StepResult.op` is the extension axis (D-06/D-07 precedent, `OP_WRITE_PARTIAL`). New op strings only. |
| **A new `mem_type`/`type` axis or a firmware capability bit** | v1.20 removed the legacy axis; the gating note establishes no handshake dev-capability bit is needed. |
| **Raising the watermark to 69** | Records the debt as policy. The measured path to **33 ≤ 35** is three mechanical steps (§2d). |
| **Touching `firestarter/` (firmware)** | Declared out of scope. Consequence: the Phase 116 trace harness cannot be an executable gate here (§3a). |
| **`--python-version` on the CLI** | Splits the target across two files; reintroduces the exact confusion the current stale comment records. |
| **Dropping `requires-python = ">=3.9"` in v1.30** | Correct eventually (3.9 EOL 2025-10-31) but it is published-metadata breakage orthogonal to these six items. **Backlog it.** |

---

## 6. File:line audit — every claim in the planning record, checked

**8 verified · 11 stale.** The design note is dated 2026-07-31; PROJECT.md's own *corrections* of
it are also stale.

| Claim | Source | Live | Status |
|---|---|---|---|
| `dev_sdp` at `cli_handlers.py:2095-2227` | note §7, PROJECT.md:51 | decorator **2196**, `def dev_sdp` **2213**, block ends **2321** (EOF) | **STALE** — off by ~98; the real block is **2196-2321** |
| `dev_test(app, chip)` at `cli_handlers.py:1958` | note §4, PROJECT.md:106 | `@dev.command(name="test")` **2055**, `def dev_test` **2059** | **STALE**, actual 2059 |
| `sdp_capability` at `sdp_capability.py:266` | note §4, PROJECT.md:60 | `def sdp_capability` **272** (266 is inside the preceding helper) | **STALE** by 6 |
| `eprom_operations.py:1736 sdp_unlock` | note §7 | `def sdp_unlock` **1736** | **VERIFIED** |
| `eprom_operations.py:1784 sdp_lock` | note §7 | `def sdp_lock` **1784** | **VERIFIED** |
| `constants.py:72-73` SDP commands | note §7 | `COMMAND_SDP_UNLOCK = 9` **72**, `COMMAND_SDP_LOCK = 10` **73**; `COMMAND_NAMES` entries **90-91**; `FLAG_SKIP_SDP_UNLOCK = 0x100` **121** | **VERIFIED** |
| `COMMAND_NAMES` deref at `eprom_operations.py:301` and `:377` | note §7, PROJECT.md:130 | **329** and **405** | **STALE** — the `KeyError` risk is real, the lines are wrong |
| host-side auto-unlock at `eprom_operations.py:1637` | note §2 | 1637 is a comment; the live gate is `if is_protocol_0x0d and (operation_flags & FLAG_SKIP_SDP_UNLOCK)` at **1654** | **PARTIALLY STALE** |
| `chip_test.py:289-295` op vocabulary | note §7 | `OP_ID` **289** … `OP_ERASE` **295** | **VERIFIED** |
| `chip_test.py:636 _DESTRUCTIVE_OPS` | note §7 | **636** | **VERIFIED** |
| `diagnostic_report.py:183 dedup_fingerprint` | (§3d) | **186** | **VERIFIED** |
| `channel.py` `BETA_ONLY_BOARDS` | scope item 5 | **33** | **VERIFIED** |
| `dev` group at `cli_handlers.py:960`, docstring `:965` | gating note | `def dev()` **1173**, docstring **1174-1177** | **STALE** |
| "**eight** dev subcommands" | gating note | **nine** (`sdp` added after the note) → back to eight after v1.30 | **STALE** |
| `fw --pre` `cli_handlers.py:797`, `--stable` `:810` | gating note | **956** / **969** | **STALE** |
| `firmware.py:47` version regex | gating note | `FIRMWARE_VERSION_RE` **52** (47 is its comment) | **STALE** by 5 |
| `--sdp-relock` deferral at `STATE.md:154` / `PROJECT.md:671` | note §8 | — | **STALE** (note says so itself) |
| `--sdp-relock` deferral at `STATE.md:532` / `PROJECT.md:705` | PROJECT.md:134 (its *own correction*) | live: **`STATE.md:538`** and **`PROJECT.md:823`** | **ALSO STALE** — fix both when the stub is scoped |
| "test suite ~1293" | PROJECT.md | **1303** collected | **STALE** by 10 |

---

## 7. Version pins — the complete decision set

| Package / setting | Current | v1.30 action | Why |
|---|---|---|---|
| `mypy>=2.1.0` | resolves 2.3.0 | **unchanged** | Fine; the gate, not the pin, is broken. Consider a `<3` upper bound so mypy 3.x's next minimum-target clamp lands as a resolver decision rather than a surprise red — optional, and FIX-2 already makes it loud. |
| `[tool.mypy] python_version` | `"3.9"` (silently ignored) | **→ `"3.10"`** | The only honest value mypy 2.x will accept. **Zero error-count change** (measured). |
| `# mypy_error_watermark` | `35` | **keep 35**; re-baseline downward *after* the `dev sdp` deletion | 69 → 33 in three mechanical steps (§2d) |
| `requires-python` | `>=3.9` | **unchanged in v1.30**; backlog the 3.9 drop | 3.9 EOL 2025-10-31; breaking published metadata is its own decision |
| `[tool.ruff] target-version` | `"py39"` | **unchanged — now load-bearing** | It becomes the *only* remaining py39 floor enforcement once mypy targets 3.10 |
| `ruff>=0.15.14` | local 0.16.0 | unchanged | `extend-exclude = ["tests/golden", "tests/fixtures"]` already handles the 0.16 markdown-formatting collision |
| `pytest>=8.0`, `syrupy>=5.0`, `pytest-cov>=7.1.0`, `types-pyserial` | resolve 9.1.1 / 5.5.3 / — / 3.5.0.20260712 | unchanged | pytest 9.x is the source of the numpy stub chain but the chain is inert in CI (no numpy) |
| runtime deps (6) + `[py32] pyusb` | — | **unchanged — add nothing** | §5 |
| CI `Set up Python 3.11` | 3.11 | unchanged | Adding a py3.9 matrix leg would restore real 3.9 coverage — separate decision, not v1.30 |
| `ci.yml` `push: branches: [main]` | main only | **worth revisiting** | `beta` pushes never run `ci.yml`, which is why a RED primary gate went unnoticed for two months |
| coverage floor | `--cov-fail-under=70` | unchanged | pytest never ran in the failing runs; re-verify once the mypy gate passes |

---

## Sources & confidence

| Finding | Method | Confidence |
|---|---|---|
| mypy 2.3.0 rejects `python_version = 3.9` non-fatally and clamps to 3.10; CLI form is a fatal usage error | **reproduced** on this tree with 3 purpose-built probe configs and revealed-type branch analysis | **HIGH** |
| Truncated-run summary `Found 1 error in 1 file (errors prevented further checking)` + exit 2 vs complete `Found 69 errors in 17 files (checked 120 source files)` + exit 1 | **reproduced**; PoC fixed gate flips devcontainer GREEN→exit 2 and reports 69/120 in a CI-like venv | **HIGH** |
| 69 errors, 17 files, 120 checked; 25 in `firestarter/`, 44 in `tests/`; the class/file distributions; `--no-local-partial-types --no-strict-bytes` also = 69 | **measured** in a numpy-free venv reproducing `ci.yml`'s `.[test]` closure | **HIGH** |
| numpy chain `pytest → _pytest/python_api.py:21 → numpy/__init__.pyi:737`; numpy absent from CI's closure | traced hop by hop; venv verified `ModuleNotFoundError: numpy` | **HIGH** |
| CI is RED at exactly the `mypy type check (watermark gate)` step; `ci.yml` never runs on `beta` pushes | `gh run view 30708836339`; `ci.yml` read | **HIGH** |
| Every file:line in §6; `channel.py` in full; the `hidden=`-is-cosmetic finding; `dedup_fingerprint` hashing `op` | read from the live tree | **HIGH** |
| Phase 116 harnesses are `[env:native]` C++/Unity binaries in the firmware repo | `firestarter` @ `0933bd7`: `test/native/avr/test_sdp_harness/`, `test_eeprom28c_sdp/`, `platformio.ini` `[env:native]` | **HIGH** |
| mypy **2.0** removed `--python-version 3.9`; **1.20** was the last release supporting it and dropped running on 3.9; latest changelog section is **2.3**; 2.0 also defaulted `--local-partial-types` / `--strict-bytes` on | live `python/mypy` `CHANGELOG.md` (raw, master) via WebFetch, **cross-checked** against the reproduced error message and the 2.1.0-vs-2.3.0 pair on this box | **MEDIUM** (verified: cross-checked) |
| Python 3.9 EOL **2025-10-31**; Python 3.10 EOL **2026-10-31** | WebSearch, multiple concurring sources incl. endoflife.date | **MEDIUM** (verified: cross-checked) |

Sources:
- [python/mypy CHANGELOG.md (master)](https://raw.githubusercontent.com/python/mypy/master/CHANGELOG.md)
- [Python | endoflife.date](https://endoflife.date/python)
- [Python 3.10 EOL — discuss.python.org](https://discuss.python.org/t/python-3-10-eol-is-there-an-official-end-of-support-date-within-october-2026/108064)
