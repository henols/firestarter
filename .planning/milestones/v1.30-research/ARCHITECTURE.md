# Architecture Research — v1.30 SDP Surface Retirement & Behavioral Lock Proof

**Domain:** Host-only Python CLI change inside an established two-repo EPROM-programmer system
**Researched:** 2026-08-03
**Tree verified against:** `firestarter_app` branch `beta` @ `16a313a` (working tree; only `.gitignore` modified + untracked noise)
**Confidence:** HIGH on every integration point (all read from the live tree, most re-measured by execution). MEDIUM on the CI-redness premise (see §7.0) — that one requires a real `workflow_dispatch` to settle.

**Method note.** Every line number below was read out of the live tree in this session, not carried over from the design note. Where the note and the tree disagree, the tree wins and the drift is named. Four of the note's twelve anchors are stale; two are load-bearing for the roadmapper (the delete range and the `dev test` entry point).

---

## 1. Integration points — verified against the live tree

### 1.1 DELETE

| Design-note claim | Live tree | Verdict |
|---|---|---|
| `cli_handlers.py:2095-2227` — `dev_sdp` and its four gates | `@dev.command(name="sdp")` at **2196**; `def dev_sdp(app, eprom, mode, assume_yes)` at **2213**; body runs to **2321 = EOF** (`sys.exit(0 if ok else 1)`). Span is **2196–2321**, 126 lines, and it is the **last function in the file**. Line 2098 is now `click.echo(_ALWAYS_WRITES_NOTICE)` *inside* `dev_test`. | **STALE, actual is `cli_handlers.py:2193-2318`** |
| "its four gates" | Four `# Gate N` comment blocks confirmed: Gate 1 absent-chip (`2234-2240`), Gate 2 capability (`2242-2246`), Gate 3 support-status (`2248-2251`), Gate 4 consent (`2253-2281`). | **VERIFIED** (count and identity) |
| `tests/test_dev_sdp_cmd.py` | Exists, **558 lines**, 12 `runner.invoke(cli, ["dev", "sdp", ...])` cases. | **VERIFIED** |

**Drift cause (for the roadmapper's benefit):** v1.23 inserted ~98 lines above this region (`py32f071` board plumbing, `_BOARD_CHOICES`, the `fw` option block). Expect the same +98 offset on any other `cli_handlers.py` anchor the note carries.

**Two deletion side-effects the note does not mention — both fail CI if missed:**

1. **`tools/check_no_exists_proxy.py:156` names `"tests/test_dev_sdp_cmd.py"` in its literal `_DEFAULT_TARGETS` enumeration, and the gate is fail-closed on a missing target** (`FAIL: scan target(s) not found on disk -- the gate cannot ...`, ~line 331). Deleting the test file without editing that list in the **same commit** turns the gate red. This is the identical failure shape recorded for `git rm REQUIREMENTS.md` at milestone close.
2. `dev_sdp` is the sole in-tree consumer of two imports (`MSG_ERR_UNKNOWN_CMD` → `FirmwareOutdatedError`, the D-14 old-firmware detection at `2283-2306`). Those must be **moved to the `write --sdp-relock` path**, not dropped — both survivors issue CMD 9/10 and both need old-firmware detection. `ruff check` (select `F`) will flag them as unused if merely orphaned.

### 1.2 KEEP — load-bearing for both survivors

| Design-note claim | Live tree | Verdict |
|---|---|---|
| `eprom_operations.py:1736 sdp_unlock` | `def sdp_unlock(` at **1736** | **VERIFIED exactly** |
| `eprom_operations.py:1784 sdp_lock` | `def sdp_lock(` at **1784** | **VERIFIED exactly** |
| `constants.py:72-73` `COMMAND_SDP_UNLOCK`/`COMMAND_SDP_LOCK` | `COMMAND_SDP_UNLOCK = 9` at **72**, `COMMAND_SDP_LOCK = 10` at **73** | **VERIFIED exactly** |
| "and their `COMMAND_NAMES` entries" | Present at `constants.py:90-91` (`COMMAND_SDP_UNLOCK: "SDP_UNLOCK"`, `COMMAND_SDP_LOCK: "SDP_LOCK"`) | **VERIFIED** |
| "dereferenced at `eprom_operations.py:301` and `:377`" | Actual sites: **`:329`** (`operation = COMMAND_NAMES[cmd]`, inside `_setup_operation`) and **`:405`** (`operation_name = COMMAND_NAMES[cmd]`, inside `_operation_context`). Lines 301/377 are unrelated (`_calculate_buffer_size` body / `_operation_context` signature). | **STALE, actual is `:329` and `:405`** |
| `sdp_capability.py` in full; `sdp_capability` at `:266` | `def sdp_capability(chip_name, db)` at **266**; module is **281 lines**; `sdp_capability_for_entry` at **201**; `SDP_PROTOCOL_ID = 13` at **58**; `SDP_CAPABLE_TOKENS` at **70-149**. Docstring (c) states 43 ALLOW / 41 REFUSE / 84 total / 65 tokens. | **VERIFIED exactly** |

**The stale `301`/`377` pair is not confined to the design note — it is baked into three places in the shipped tree** and all three should be corrected while the milestone is here (comment-only, zero behaviour):

- `firestarter/constants.py:69-70` — the source comment that *is* the KeyError warning ("`COMMAND_NAMES[cmd]` is dereferenced at eprom_operations.py:301 and again at :377").
- `tests/test_revision_constants_parity.py:71` and `:526` — the same pair, quoted in the gate's own rationale prose.

The *claim* those references make is still true and still load-bearing: a `COMMAND_NAMES` entry deleted alongside the command would raise `KeyError` at operation setup (`_setup_operation`), not merely omit a log word. Only the coordinates are wrong.

### 1.3 EXTEND

| Design-note claim | Live tree | Verdict |
|---|---|---|
| `chip_test.py:289-295` op vocabulary | `OP_ID = "id"` at **289** … `OP_ERASE = "erase"` at **295**. Exactly seven strings. | **VERIFIED exactly** |
| `chip_test.py:636 _DESTRUCTIVE_OPS` | `_DESTRUCTIVE_OPS = frozenset({OP_WRITE, OP_WRITE_PARTIAL, OP_ERASE})` at **636** | **VERIFIED exactly** |
| `derive_plan` | `def derive_plan(name, db, *, write_scope="none")` at **394**; step-append body `466-573`; `return Plan(...)` at **575-581** | **VERIFIED** |
| `diagnostic_report.py` report rows | `_step_dict` at **406-415**; `render` at **456-528** (per-step rows at **477-482**); `SCHEMA_VERSION = "1.2"` at **55**; `to_dict` at **436-454** | **VERIFIED** |
| `dev test` entry point `dev_test(app, chip)` at `cli_handlers.py:1958` | `@dev.command(name="test")` at **2055**; `def dev_test(app: "AppContext", chip: str)` at **2059**; `derive_plan` call at **2112**; `run_plan` call at **2138**; `submit_report` at **2188**; exit-code computation at **2192** | **STALE, actual is `cli_handlers.py:2056`** (signature itself verified: two parameters, zero options) |

**A fourth extend point the note omits, and it is the one that fails closed on you.** `chip_test.py:654` defines a **second** frozenset, `_MULTI_RUN_OPS = frozenset({OP_WRITE, OP_WRITE_PARTIAL, OP_VERIFY, OP_ERASE})`, and it is the **live dispatch allow-list**, not merely a policy set. Two independent refusals key on it:

- `_dispatch_step` (`901-952`): after the `OP_ID`/`OP_BLANK_CHECK`/`OP_READ` arms, `if step.op in _MULTI_RUN_OPS: return _dispatch_multi_run(...)`, else a `VERDICT_BAD` "matched no dispatch arm — refused fail-closed" (`944-952`).
- `_dispatch_multi_run` (`1082-1092`): a second, hoisted refusal *before* any temp file, pattern, or operator call.

The comment at `637-653` records why, and it is the strongest constraint on the new leg: **"any future op added to the vocabulary MUST be added to both frozensets in this block or it fails closed by construction (proven by a deliberate-break test, plan 121-06 Task 3)."** Before this guard existed, an unmapped op string reached `operator.erase_eprom()` and reported `OK`.

### 1.4 Additional gates that constrain the design (none named in the note)

| Gate | What it does | Constraint on v1.30 |
|---|---|---|
| `tools/check_devtest_orchestrator.py` | Scans **`chip_test.py` and `submit.py` in full**, and `cli_handlers.py` **scoped to a named function set**, for: VPP-set call names (`_VPP_SET_NAMES`, `:159-169`), dict literals carrying ≥2 wire keys (`_WIRE_DICT_KEYS`, `:176-189`), and `force=`/`"--force"` (`:191-193`). | The leg must compose only existing `EpromOperator` methods. **Passing `operation_flags=FLAG_SKIP_SDP_UNLOCK` is on no deny list and is safe.** Constructing a wire dict, or a `force=True`, is not. |
| `tools/check_devtest_orchestrator.py:138-150` `_HANDLER_FUNCTION_NAMES` | 9 names: `dev_test`, `_verdict_code`, `_sanitize_chip_token`, `_is_uv_eprom`, `_resolve_write_scope`, `_default_uv_write_confirm`, `_chip_id_fields`, `_is_interactive`, `_make_sampler`. | **Any new private helper co-located with `dev_test` MUST be added here** or the gate silently under-covers exactly the new code. The comment at `127-137` records that RESEARCH C-4 *proved* this empirically (a violating helper outside the set passes at EXIT=0). `tests/test_check_devtest_orchestrator.py::test_handler_function_names_all_resolve_to_real_callables` enforces the names resolve. |
| `tools/parse_devtest_issue.py:99` | Accepts `schema_version` by **presence only**, never exact value. | A `SCHEMA_VERSION` bump is invisible to the parser — but `tests/test_parse_devtest_issue.py:102` asserts `obj["schema_version"] == "1.2"` and **must be updated**. The frozen legacy `"1.1"` fixture (~`237-272`) must stay untouched by design. |
| `tests/test_revision_constants_parity.py:207`, `_strip_comments` at `:201-217` | Firmware-source scan of `firestarter.h`'s `#ifdef DEV_TOOLS` axis; comment-stripping is load-bearing because `firestarter.h`'s own comments literally contain the strings `constants.py CMD_SDP_*`, `COMMAND_NAMES` and `#ifdef DEV_TOOLS`. | v1.30 touches no firmware, so this gate must simply stay green. **Corollary for item 5: do not build the host channel gate by scanning firmware source** — the recorded hazard is that such gates fail OPEN on a rename. |
| `tests/test_skip_census.py` | Allow-lists every skip reason; asserts its own liveness; explicitly refuses a pinned skip count. | A new leg that ever emits a pytest `skip` needs its reason allow-listed. `VERDICT_SKIPPED` is a report verdict, not a pytest skip — no interaction. |

---

## 2. Where the leg sits in the existing model, and the central design question

### 2.0 System overview, as the leg will see it

```
┌────────────────────────────────────────────────────────────────────────────┐
│  CLI surface — cli_handlers.py                                             │
│  ┌───────────────────────┐            ┌──────────────────────────────────┐ │
│  │ @cli.command "write"  │            │ @dev.command "test"              │ │
│  │   :529-691            │            │   :2055-2193   dev_test(app,chip)│ │
│  │  ITEM 3 lives here    │            │   zero options (P121 D-05)       │ │
│  │  (needs NAME + app.db)│            │  ITEM 2 is derived, not flagged  │ │
│  └───────┬───────────────┘            └────────┬─────────────────────────┘ │
│          │                                     │  derive_plan :2112        │
│  ┌───────┴──────────────────────────────┐      │  run_plan    :2138        │
│  │ @cli.group "dev" :1171 — 9 subcmds   │      │  submit      :2188        │
│  │  membership frozen at IMPORT         │      │                           │
│  │  ITEM 5 hooks here; ITEM 1 removes   │      │                           │
│  │  the 9th (`sdp`, :2196-2321)         │      │                           │
│  └──────────────────────────────────────┘      │                           │
├─────────────────────────────────────────────────┴──────────────────────────┤
│  Orchestration / pure compute (no serial, no VPP, no wire dict)            │
│  ┌──────────────────────────┐  ┌──────────────────────┐  ┌──────────────┐  │
│  │ chip_test.py             │  │ diagnostic_report.py │  │ submit.py    │  │
│  │  derive_plan  :394       │→ │  DiagnosticReport    │→ │ submit_report│  │
│  │  run_plan     :709       │  │  SCHEMA_VERSION :55  │  │              │  │
│  │  _dispatch_*  :901-1182  │  │  dedup_fingerprint   │  │              │  │
│  └───────────┬──────────────┘  └──────────────────────┘  └──────────────┘  │
│              │                  ┌────────────────────────────────────────┐ │
│              │                  │ sdp_capability.py  :266 — pure, 43/41  │ │
│              │                  │ ITEM 2 + ITEM 3 both consume it        │ │
│              │                  └────────────────────────────────────────┘ │
├──────────────┴─────────────────────────────────────────────────────────────┤
│  Operation layer — eprom_operations.py (UNMODIFIED by v1.30)               │
│   write_eprom :1583 · verify_eprom :1673 · read_eprom · erase_eprom        │
│   sdp_unlock  :1736 (CMD 9) · sdp_lock :1784 (CMD 10)                      │
│   COMMAND_NAMES[cmd] deref :329 and :405  ← KeyError risk if names dropped │
├────────────────────────────────────────────────────────────────────────────┤
│  Transport — serial_comm.py (COBS)   ·   FIRMWARE: NOT TOUCHED             │
└────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 What the existing step model already gives the leg for free

| Property the leg needs | Already delivered by | Change needed |
|---|---|---|
| **Strict ordering of the 4 steps** | `Plan.steps` is an ordered `list[Step]` (`:357`); `derive_plan` appends in order; `run_plan` iterates `for step in plan.steps` (`:779`) with no reordering anywhere. | **NONE.** Ordering is not a missing capability — it is the model's default. |
| **Step 4 runs even when step 3 reports BAD** | `_run_step`'s per-step `try/except` (`:883-898`) converts `EpromOperationError` → `VERDICT_BAD` and `ChipNotImplementedError`/`ChipNotFoundError` → `SKIPPED`, then `run_plan` continues the loop. Documented at `:734-737` as Pitfall 1. | **NONE for those three exception types.** |
| **Cross-step state derived from a prior step's verdict** | `destructive_gate_closed` — a plain local `bool` in `run_plan` (`:777`), written from the `OP_ID` result at `:791-792`, read at `:784`. | **NONE — this is the precedent to copy.** |
| **A step that must not be reordered relative to its neighbours** | The `OP_ID`-first rule (SWEEP-03) is exactly this, and it is enforced by nothing but `derive_plan`'s append order. | **NONE.** |
| **All-or-nothing behaviour under the chip-ID gate** | `destructive_gate_closed` is computed once and is constant for the rest of the loop. If it closes, *every* `_DESTRUCTIVE_OPS` member skips together. Put both the lock and the unlock op in `_DESTRUCTIVE_OPS` and they skip as a pair — nothing gets locked, so nothing needs unlocking. | **NONE beyond the frozenset entries.** |

**So the answer to "does the existing step model support an ordered, must-run-cleanup group?" is: it supports the *ordered* half completely, and the *must-run* half for three of the exception classes that can actually occur — but not for the other two, and not for `KeyboardInterrupt`.** Two concrete holes:

**Hole A — the exception set is too narrow, and the missing classes are the likely ones.** `_run_step` catches `EpromOperationError` and `(ChipNotImplementedError, ChipNotFoundError)`. It does **not** catch `SerialError` (`exceptions.py:13`) or its subclasses `SerialTimeoutError` (`:19`), `ProgrammerNotFoundError` (`:25`), `FirmwareOutdatedError` (`:31`), nor `HardwareOperationError` (`:69`) — all are plain `Exception` subclasses, siblings of `EpromOperationError` (`:37`), not descendants. `serial_comm.py` raises them at twelve sites (`153, 162, 171, 173, 368, 377, 409, 424, 439, 484, 791, 824`), including the read-timeout path at `:484`. Today such an exception **propagates out of `run_plan`, out of `dev_test`, into `map_typed_errors` (`cli_handlers.py:191-192`) and becomes a `ClickException`** — so `report.results` is never assigned (`:2139`), the JSON/MD files are never written (`:2160-2185`), `submit_report` never runs (`:2188`), and a locked chip goes back in the envelope with no report line telling anyone. *A cable that half-seats mid-leg is the single most likely field failure and it currently takes out the entire report.*

**Hole B — there is no cleanup path of any kind.** `chip_test.py` contains exactly two `finally:` blocks, at `:1106` and `:1161`, both scoped to unlinking a temp pattern file inside `_dispatch_multi_run`. There is **no** `try/finally` around `run_plan`'s loop, **no** `atexit`, and **no** `KeyboardInterrupt` handling anywhere in `chip_test.py`, `cli_handlers.py`, or `main.py` (grep returns zero hits for `atexit` and `KeyboardInterrupt` across all three).

### 2.2 The proposed mechanism — smallest change that adds a must-run cleanup group without breaking independence

Three additive edits, each with a default that reproduces today's behaviour byte-for-byte.

**Edit 1 — two optional fields on `Step` (`chip_test.py:298-324`).**

```python
@dataclass
class Step:
    op: str
    supported: bool
    reason: str
    destructive: bool = False
    write_region: tuple[int, int] | None = None
    group: str | None = None   # NEW — leg id ("sdp"); None == today's independent step
    role: str = ""             # NEW — "lock" | "cleanup" | ""; "" == no role
```

`group` and `role` are the *only* new state. Every step `derive_plan` emits today keeps `group=None, role=""`.

**Edit 2 — `run_plan` (`chip_test.py:776-794`) gains a cleanup registry and a `try/finally`.** The loop body is unchanged; the additions sit around it:

```python
results: list[StepResult] = []
destructive_gate_closed = False
pending_cleanup: dict[str, Step] = {}        # NEW — group id -> its cleanup Step
cleanup_done: set[str] = set()               # NEW

try:
    for step in plan.steps:
        ...                                   # existing body, unchanged
        result = _run_step(...)
        results.append(result)

        if step.op == OP_ID:
            destructive_gate_closed = _id_step_closes_gate(result)

        # NEW — arm/disarm, both keyed off a VERDICT, exactly like the gate above
        if step.group and step.role == "lock" and result.verdict in _RAN_VERDICTS:
            pending_cleanup[step.group] = _cleanup_step_for(plan, step.group)
        if step.group and step.role == "cleanup":
            pending_cleanup.pop(step.group, None)
            cleanup_done.add(step.group)
finally:
    # NEW — drain any group whose cleanup step was never reached.
    for group, cleanup in pending_cleanup.items():
        results.append(_run_cleanup_out_of_band(plan.name, cleanup, operator, db))
```

Why `finally` rather than `except BaseException: ... raise` — a `finally` runs on `KeyboardInterrupt` and `SystemExit` too, does **not** swallow the original exception, and needs no re-raise. It is both smaller and strictly safer.

**Edit 3 — widen `_run_step`'s except set (`chip_test.py:883-898`)** to `except (SerialError, HardwareOperationError) as exc: -> VERDICT_BAD`, alongside the existing arms. Never a bare `except Exception` (it would swallow the `AssertionError` at `:1130-1132`, whose whole purpose is to be loud), and never `BaseException` (Ctrl-C must stay a Ctrl-C).

**Why this does not break the independence contract for every other step — and how to prove it:**

- For any plan whose steps all carry `group=None`, `pending_cleanup` stays empty and the `finally` body iterates zero times. The returned `list[StepResult]` is **identical**. Assert this directly on a non-`0x0D` chip: same list length, same `(op, verdict, reason, error_code, run_count)` tuples. This is the same "proven no-op" discipline `sampler=None` already carries (`:759-761`) and `locked_destructive`'s advisory-only status carries (`:331-345`).
- The independence contract is *strengthened*, not weakened, by Edit 3: a step that used to abort the run now records a BAD verdict and lets the run finish. That is what `:734-737` says the module is for ("One step's `BAD` verdict or raised exception NEVER aborts the remaining steps") — the contract was written correctly and implemented incompletely.
- **Edit 3 is a behaviour change for every command that reaches `run_plan`** (i.e. `dev test`): a dead cable now yields a full report with BAD transport steps instead of a `Communication error:` ClickException. That is the right direction for a diagnostic whose purpose is capturing failures, and it makes the reports *more* useful — but it is a recorded decision with its own test, not a silent side-effect.

**Rejected alternatives, and why:**

| Alternative | Rejected because |
|---|---|
| A nested `Plan` / sub-plan object for the leg | `count_applicable` (`:1229-1253`), `dedup_fingerprint` (`diagnostic_report.py:183-223`), `_step_dict` (`:406`) and `tools/parse_devtest_issue.py` all consume a **flat** `results` list. Nesting forces a change in four consumers to buy nothing the flat list cannot express. The D-06/D-07 rationale that admitted `OP_WRITE_PARTIAL` says exactly this: encode the distinction **in the op string**, so every `StepResult.op` reader picks it up without learning a new field. |
| A `must_run` boolean on `Step` with no `group` | Cannot express "run *this* step if *that* step ran" — and a per-step `must_run` with no pairing would re-run the unlock on every plan. |
| Move the whole leg into a single composite step | Kills the report. The value of four rows is that a reader can see *which* of baseline / lock / oracle / restore failed. One row collapses Trap 1's entire distinction (write-failed vs bytes-changed) into one verdict. |
| `atexit` | Runs after `sys.exit`, at interpreter teardown, with the operator object possibly already garbage; cannot be tested without process isolation; and it would fire on the *success* path too. `finally` is scoped, ordered and testable. |

### 2.3 The four ops, and where each frozenset entry goes

Recommended vocabulary (kebab-case, matching `"blank-check"`/`"write-partial"`), appended at `chip_test.py:295`:

```python
OP_SDP_BASELINE = "sdp-baseline"          # step 1: write A + verify
OP_SDP_LOCK = "sdp-lock"                  # step 2: CMD 10, emission only
OP_SDP_INHIBITED_WRITE = "sdp-inhibited-write"   # step 3: write B w/ FLAG_SKIP_SDP_UNLOCK, read back — THE ORACLE
OP_SDP_UNLOCK = "sdp-unlock"              # step 4: CMD 9 + write + verify — the must-run cleanup
```

| Frozenset | Add | Rationale |
|---|---|---|
| `_DESTRUCTIVE_OPS` (`:636`) | **all four** | Every one mutates the part, and every one must be gated shut by a chip-ID mismatch. `OP_SDP_LOCK` in particular: emitting a lock sequence onto a misidentified part is worse than a bad write. The comment at `:626-635` already states the principle ("a write-shaped op absent from this frozenset would write to a misidentified chip ungated"). |
| `_MULTI_RUN_OPS` (`:654`) | **none** | These steps are **not** idempotent across runs. Running the lock twice, or interleaving two passes of the sequence, is meaningless at best. `runs=2` is wrong here. |
| **NEW `_SDP_OPS`** frozenset, beside `_MULTI_RUN_OPS` | all four | The new single-run **dispatch allow-list**, mirroring `_MULTI_RUN_OPS`'s role. `_dispatch_step` gets a `if step.op in _SDP_OPS: return _dispatch_sdp(...)` arm **before** the `_MULTI_RUN_OPS` check, so the existing fail-closed refusals at `:944-952` and `:1082-1092` still catch anything unmapped. The deliberate-break test from plan 121-06 Task 3 must be extended to cover the new set. |

### 2.4 Region and pattern-B choice — the one thing the note leaves open

Measured facts that decide this:

- `_resolve_write_scope` (`cli_handlers.py:1990-2032`) returns `"full"` for any non-UV chip **including the AT28C family explicitly** (`:2005-2007`). `derive_plan` therefore takes the `write_scope == _WRITE_SCOPE_FULL` branch at `:459-460`, and because `is_uv_eprom(full)` is False for a `0x0D` EEPROM, `write_region = _DEFAULT_REGION = (0, 256)` (`:816-829`).
- So the **existing** `OP_WRITE` and `OP_VERIFY` steps already write `generate_pattern(0, 256)` at region `(0, 256)`, **twice** (`runs=2`).
- `generate_pattern(start, length)` (`:59-67`) is a **pure function of the region** — `address_fold_byte(start + i)`, no state.

**Recommendation:** give the leg its own region constant, `_SDP_REGION = (256, 256)`, and set it as `Step.write_region` on all four SDP steps. Every `0x0D` part is ≥ 2 KiB (the smallest, `2816`, is 2 KiB), so the window always fits; keep `_top_anchored_or_default`'s defensive-fallback discipline anyway. Two reasons:

1. **Report legibility / evidence hygiene.** With a distinct window, the leg's step-1 baseline is unambiguously the leg's own write. On the shared `(0, 256)` window a sceptical reader cannot tell whether step 3's read-back matched because step 1 wrote A or because the *earlier* `OP_WRITE` step did.
2. **Width still comes from a module constant, never a DB field** — the SC4 rule stated at `:311-315` and `:852-856`. `_SDP_REGION`'s width is a literal; `memory-size` only bounds placement.

**Pattern B** needs a second pure generator beside `generate_pattern`:

```python
def sdp_probe_pattern(start: int, length: int) -> bytes:
    """Pattern B: the bitwise complement of pattern A over the same region."""
    return bytes(b ^ 0xFF for b in generate_pattern(start, length))
```

Complement, not a different region-offset fold, because it guarantees B differs from A at **every single byte** — which is what makes a *partial* change (gh#11's exact symptom) visible as a partial mismatch rather than as a coincidental match. It is also neither all-`0x00` nor all-`0xFF`, so a blank read and a stuck-bus read stay distinguishable from a successful inhibited write.

**The oracle, stated so Trap 1 and Trap 2 are structurally dodged:**

```
actual = read_back(_SDP_REGION)
expected_A = generate_pattern(*_SDP_REGION)        # re-derived, not carried
if actual == expected_A:  verdict = OK             # the lock held
else:                     verdict = BAD            # includes: equals B (lock never reached
                                                   # silicon), partial change (gh#11),
                                                   # all-0xFF (contact fault) — all BAD
fingerprint = classify_fingerprint(expected_A, actual, addr_base=_SDP_REGION[0])
```

Three properties this shape buys, each mapping to a named trap:

- **Trap 1** — the verdict is decided by `actual == expected_A`, a strict bytes comparison. `operator.write_eprom`'s return value is recorded in `reason` for diagnosis and **never** consulted for the verdict. "The write reported failure" cannot produce an OK, and an all-`0xFF` contact fault cannot either (all-`0xFF` ≠ pattern A).
- **Trap 2** — there is no branch from this step to `VERDICT_SKIPPED`/`VERDICT_NA`. An unexpectedly-successful inhibited write lands in the `else` and reads BAD. `SKIPPED`/`NA` for this op is reachable only from `derive_plan`'s capability refusal (before the run) and from the chip-ID destructive gate (before the operator call) — never from a *result*.
- **`classify_fingerprint` is diagnostic only, never the verdict.** Its first bucket is `blank/contact` on `ff_ratio >= 0.98` (`:176-183`), which fires *even when there are zero mismatches* — so a fingerprint-driven verdict could label a genuine all-`0xFF` disaster as "blank/contact" and lose the BAD. Keep the two separate: equality decides, fingerprint explains.

---

## 3. Cross-step state — what must flow, and the mechanism

**Where `dev test` holds cross-step state today: exactly one place.** `run_plan`'s local `destructive_gate_closed: bool` (`chip_test.py:777`), written at `:791-792` from the `OP_ID` `StepResult`, read at `:784`. There is no context object, no `Plan`-level mutable field, no module global. `StepResult` (`:661-682`) is per-step output only, never an input to a later step. `Plan.locked_destructive` (`:359`) is explicitly advisory and `run_plan` is forbidden to iterate it (`:331-337`).

**What must flow between the four SDP steps, and how:**

| State | Mechanism | Why |
|---|---|---|
| **Pattern A's bytes** (step 1 → step 3) | **Nothing flows.** Step 3 re-derives `generate_pattern(*step.write_region)`. `derive_plan` stamps the same `write_region` on all four SDP steps, exactly as it already stamps the write and verify steps with one shared region (`:513`, `:531`, rationale at `:526-528`). | `generate_pattern` is pure (`:59-67`) and `write_region` is already a per-step field whose read-only-downstream discipline is stated at `:315-317`. This is the *zero-plumbing* answer and it is the right one. |
| **"Did the lock step actually emit OK?"** (step 2 → step 3) | A verdict-derived local `bool` in `run_plan`, added beside `destructive_gate_closed`. | Lets step 3 say honestly "the lock was never emitted — this step proves nothing about the lock" instead of reporting a BAD that looks like a lock failure. Same shape, same scope, same idiom as the existing gate. |
| **"Is a cleanup still owed?"** (step 2 → the `finally`) | `pending_cleanup: dict[str, Step]` in `run_plan` (§2.2 Edit 2). | Verdict-derived, armed by `role == "lock"`, disarmed by `role == "cleanup"`. |
| **The leg's own region** | `Step.write_region`, set once by `derive_plan`. | Already the model's mechanism; no new field. |

**Rejected: a payload-carrying field.** Adding `StepResult.data: bytes` or threading a `LegContext` through `_dispatch_step`/`_dispatch_multi_run` was considered and rejected on two grounds. (1) It widens the signature of every dispatch function for one leg. (2) `StepResult` feeds `dedup_fingerprint` (`diagnostic_report.py:217-223`) and `_step_dict` (`:406-415`), and the report body is a **public GitHub issue body** — 256 bytes of pattern in every report is noise at best, and a new field is a live risk of leaking into the dedup id (which is deliberately volatile-field-free, `:191-198`).

**Free win from the flat-op design:** `dedup_fingerprint` hashes `result.op` (`:224`), so the four new op strings enter the dedup id with **zero code change** — the same property `OP_WRITE_PARTIAL` relies on (`:205-218`). An SDP-leg run therefore can never dedup into the same group as a non-SDP run of the same chip, so it can never contribute to another group's N≥2 promotion count. Phase 114's GRAD-01 no-auto-graduate lock holds through the fingerprint, unchanged.

---

## 4. Failure / abort architecture — and what a host-side handler cannot promise

### 4.1 What exists today

| Question | Answer, from the tree |
|---|---|
| Any `try/finally` in `chip_test.py`? | Two, both at `:1106` and `:1161`, both scoped to `Path(tmp_source_path).unlink()` inside `_dispatch_multi_run`. Neither wraps the step loop. |
| Any `atexit`? | **None** in `chip_test.py`, `cli_handlers.py`, or `main.py`. |
| Any `KeyboardInterrupt` handling? | **None** anywhere in those three modules. Ctrl-C during a blocking `serial.read` unwinds straight through `run_plan` and `dev_test`. |
| Any `except Exception`? | One, at `chip_test.py:1035`, inside `_sample` — deliberately scoped to the best-effort voltage sampler, with a `noqa: BLE001` and a rationale ("a diagnostic hook, not part of the write contract"). |
| What happens to `dev_test` if `run_plan` raises? | Everything after `:2138` is skipped: `report.results` unassigned (`:2139`), banner unassigned (`:2140`), `db_diff` uncomputed (`:2153`), `render` never called (`:2155`), the JSON and MD artifacts never written (`:2160-2185`), `submit_report` never reached (`:2188`), and the exit code comes from `map_typed_errors`' `ClickException` rather than the verdict max (`:2192`). |

### 4.2 What should exist

1. **The `finally`-drained cleanup registry** (§2.2 Edit 2). Handles Ctrl-C, `SystemExit`, and any exception that escapes a step — because `finally` runs for all of them.
2. **Widen `_run_step`'s except set** (§2.2 Edit 3). Converts the *likely* aborts (serial timeout, port vanished, hardware read failure) into non-fatal BAD steps, so the ordinary path reaches step 4 through the loop and the report is still produced. This is the single highest-value safety change in the milestone and it is ~3 lines.
3. **Print the recovery instruction unconditionally, up front.** `_ALWAYS_WRITES_NOTICE` (`cli_handlers.py:2042-2049`) is `click.echo`'d at `:2097` — *before* even the SAFE-04 absent-chip hard-fail at `:2104`. Extend that string with the Trap-3 sentence so it is on screen before the leg runs, not only after a failure. Wording must reuse the family fact already in the tree at `chip_test.py:562-565` — "protocol 0x0D (28C family) has no erase operation" — so the recovery is stated as **rewrite**, never erase.
4. **A dedicated report row** carrying the recoverability line, plus an out-of-band-cleanup reason string that says which step ran from the `finally` and why.

### 4.3 What host-side handling cannot guarantee — stated plainly

- **`SIGKILL`, host power loss, OOM kill, container stop.** No Python runs. Nothing is possible, at any price.
- **Cable yank or brownout.** The `finally` *runs*, but the transport it needs is gone. `EpromOperator` opens a fresh transient connection per operation (recorded in `112-02-SUMMARY.md`, cited at `cli_handlers.py:2111-2114`), so the cleanup attempt calls `find_and_connect`, which raises `ProgrammerNotFoundError` (`serial_comm.py:791`, `:824`). The cleanup can only be **reported as attempted-and-failed**. It cannot succeed.
- **A second Ctrl-C during the cleanup.** `KeyboardInterrupt` inside the `finally` aborts it. Nothing short of signal masking prevents that, and masking Ctrl-C in a CLI that drives 12 V onto a socket is a worse idea than the problem it solves.
- **Even a cleanup that returns `True` proves nothing about the silicon.** `sdp_unlock`'s own docstring is explicit (`eprom_operations.py:1750-1760`): a `True` return "is never a claim that silicon actually left the protected state", because protection state is unreadable on this family (Phase 117 D-05, Phase 119 D-12). **"The run ended unlocked" is not provable by this code, ever.** The report must say "an unlock sequence was emitted", never "the part is unlocked" — the same honesty floor `dev_sdp`'s D-10 line held (`cli_handlers.py:2310-2315`), which should be lifted verbatim before that function is deleted.
- **Therefore the leg's safety must not depend on the cleanup, and it does not.** What makes it safe is the pre-existing property from design note §6: any locked `0x0D` part is recovered by a plain `firestarter write`, because firmware auto-unlocks at the start of every `0x0D` write. The cleanup is a courtesy that reduces how often a stranger has to know that; the *documentation* is the actual mitigation. **Record the dependency explicitly** — if auto-unlock's default is ever revisited, both the deletion (item 1) and this leg (item 2) must be revisited with it.

---

## 5. `write --sdp-relock` — the traced call chain and where the hook belongs

### 5.1 The actual chain (verified)

```
cli_handlers.py:529   @cli.command(name="write")  ... 6 existing options ... :558 --skip-sdp-unlock
cli_handlers.py:570   def write(app, eprom, input_file, blank_check, skip_erase, force, address,
                                vpe_as_vpp, skip_sdp_unlock)
              :608      eprom_data = resolve_chip(eprom, db=app.db)          # programmer dict
              :622-625  sdp_entry = app.db.get_eprom(eprom); is_protocol_0x0d = ...
              :626      allowed, sdp_reason = sdp_capability(eprom, app.db)  # ← already computed
              :627-636  D-04 AUTO-SET: 0x0D + not allowed  ⇒  skip_sdp_unlock = True + mandatory echo
              :637-649  D-18 warn-and-proceed: flag passed on a non-0x0D part
              :670-676  D-13 warn-and-proceed: --skip-erase on 0x0D
              :678-690  ok = app.eprom_operator.write_eprom(eprom, eprom_data, input_file,
                                address_str=address, operation_flags=_build_op_flags(...))
              :691      sys.exit(0 if ok else 1)                             # ← END OF HANDLER
                        ↓
eprom_operations.py:1583  write_eprom(...)  → _operation_context(COMMAND_WRITE, flags)
                   :1604    _run_state_machine(...) → is_ok
                   :1653    is_protocol_0x0d = eprom_data_dict.get("algorithm") == SDP_PROTOCOL_ID
                   :1654    if is_protocol_0x0d and (flags & FLAG_SKIP_SDP_UNLOCK):
                   :1655-1666   require MSG_WARN_SDP_UNLOCK_SKIPPED (0x86) ack, else is_ok = False
                   :1676    return is_ok
```

**On the note's `eprom_operations.py:1637`:** line 1637 is a **comment line** inside the D-15/HOST-06 block (`1612-1652`). The executable statements are `:1653` and `:1654`. More importantly, that block is not "where the write path decides auto-unlock" — it is where the host *audits* a `--skip-sdp-unlock` request after the fact. **The host's auto-unlock *decision* is in the CLI handler, at `cli_handlers.py:622-636`.** Verdict: **STALE and mis-attributed; the decision site is `cli_handlers.py:622-636`, the audit site is `eprom_operations.py:1653-1666`.**

### 5.2 The load-bearing finding: `write` never verifies

There is **no** `verify_eprom` call anywhere in the `write` handler. Verification is a separate command (`@cli.command(name="verify")` at `:694` → `verify_eprom` at `eprom_operations.py:1673`). `write_eprom`'s `ok` is firmware's own write/data-poll result plus the 0x86-ack check at `:1655-1666` — **not** a read-back comparison of contents.

So the decided polarity ("verify failure ⇒ skip the relock and report it loudly", operator 2026-08-03) has **no existing hook to observe**. Two designs:

| | Design | Assessment |
|---|---|---|
| **A** | Gate the relock on `ok` from `write_eprom`. | Zero new I/O, but "verify" would be a misnomer and it would relock a chip whose contents were never compared. Contradicts the decided requirement. |
| **B** (recommended) | When `--sdp-relock` is passed, run an explicit `app.eprom_operator.verify_eprom(eprom, eprom_data, input_file, address_str=address)` after a successful write, and gate the relock on **both** results. | Honours the decision literally, reuses an existing method with an identical argument shape, and costs an extra pass **only** on runs that asked for the flag — the default `write` path stays byte-identical. |

### 5.3 Where the hook belongs: the handler, not `write_eprom`

This is settled by the tree's own recorded reasoning, not by preference. `cli_handlers.py:610-612` states that the D-04 auto-set lives "here, in the handler, because this is the last place with both the chip NAME and app.db — resolve_chip's programmer dict carries neither `protocol-id` nor `name`". `sdp_capability(chip_name, db)` needs exactly those two, and `sdp_capability_for_entry` **raises `KeyError` with a diagnostic message** if handed a programmer dict (`sdp_capability.py:220-229`). The relock decision is therefore **structurally handler-resident**, and `eprom_operations.py` stays unmodified by v1.30 — which also keeps the milestone's "no operation-layer change" shape clean.

Insertion point: between `:690` and `:691`, replacing the bare `sys.exit`.

### 5.4 Refusal matrix — reusing the already-computed `allowed, sdp_reason` from `:626`

| Condition | Behaviour |
|---|---|
| `--sdp-relock` on a non-`0x0D` chip | **Refuse loudly** — deliberately *unlike* the D-18 warn-and-proceed arm at `:637-649`. `--skip-sdp-unlock` is a bit firmware ignores off-`0x0D`; `--sdp-relock` would issue a real `CMD_SDP_LOCK` whose magic-address bytes land as **data**. Warn-and-proceed would be a corruption path. |
| `0x0D` and `not allowed` | **Refuse.** The D-04 auto-set already fired at `:627-636` precisely because the part has no SDP command decoder. |
| `0x0D`, allowed, write failed | Relock **SKIPPED**, reported loudly. |
| `0x0D`, allowed, write ok, verify failed | Relock **SKIPPED**, reported loudly — the decided polarity. Leaves the state the user can recover from. |
| `0x0D`, allowed, write ok, verify ok | `app.eprom_operator.sdp_lock(eprom, eprom_data)`; report with emission-only wording lifted verbatim from `dev_sdp`'s D-10 line (`:2313-2318`) before that function is deleted. |
| `--sdp-relock` **and** `--skip-sdp-unlock` together | Legal, no special case: if the part really was locked, the write fails and the relock is skipped anyway. State it in the help text rather than adding a branch. |
| Attached firmware predates CMD 10 | The `MSG_ERR_UNKNOWN_CMD` → `FirmwareOutdatedError` mapping from `dev_sdp:2283-2306` **moves here**. This is the D-14 asymmetry (an unknown *command* errors and is detectable; an unknown *flag bit* is silent). |

**Exit-code decision to make explicitly** (recommended): `1` if the write failed; `1` if verify was run and failed; `1` if the relock was attempted and `sdp_lock` returned `False`; `0` otherwise. A relock skipped *because* verify failed inherits the verify failure, so it is already `1`. A skipped relock must never silently turn a good write into a failure — and a failed relock must never be swallowed into a `0`.

**Docs also owed:** `--sdp-relock` is a new production surface, so `doc/lockable-proms.md` and `doc/protocol-flags.md` are in scope.

---

## 6. Channel gating (999.15 / gh#8) — how the existing gate works and where a `dev` split hooks in

### 6.1 `channel.py` in full (81 lines, read end to end)

| Symbol | Line | Notes |
|---|---|---|
| `BETA_ONLY_BOARDS: tuple[str, ...] = ("py32f071",)` | 34 | "Graduates by deletion from this tuple." |
| `is_prerelease_build() -> bool` | 37 | PEP 440 via `packaging.version.Version(firestarter.__version__).is_prerelease`. **Fails closed** — `InvalidVersion` ⇒ `False` ⇒ gated feature stays hidden. |
| `is_board_available(board) -> bool` | 60 | `True` for anything not in the tuple. |
| `available_boards(boards) -> list[str]` | 68 | Order-preserving filter. |
| `beta_only_message(board) -> str` | 73 | The single explanation every refusal reuses. |

The module docstring records the design rule that should carry straight over to the `dev` split: **"Nothing here reads the environment. A channel gate that can be flipped by an env var is not a gate — the firmware side already learned that `-D X=${sysenv.VAR}` fails OPEN."**

### 6.2 The existing gate is two-layer

1. **Surface layer, import-time.** `cli_handlers.py:35` imports `available_boards`; `:143` `_BOARD_CHOICES: list[str] = available_boards(_ALL_BOARDS)`; `:144` `_PY32_ENABLED`; consumed at `:982` as `type=click.Choice(_BOARD_CHOICES)`. Effect: `fw --help` never advertises a beta-only board on stable.
2. **Library layer, call-time.** `firmware.py` refuses inside `_install_with_dfu()` / `probe_dfu()`, so a non-CLI caller is also gated.

### 6.3 Is the `dev` group's composition import-time? Yes. Does it constrain the design? **No.**

`@cli.group(name="dev")` at `:1171`; the nine `@dev.command(...)` decorators at `:1180, 1211, 1273, 1310, 1400, 1453, 1680, 2055, 2196` all execute at module import and mutate `dev.commands`. So membership is frozen at import, exactly like `_BOARD_CHOICES`.

**But `_BOARD_CHOICES` is import-time under duress, not by choice:** `click.Choice(_BOARD_CHOICES)` is a *decorator argument*, evaluated when the decorator runs, with no later hook. Group **lookup** has two later hooks — `click.Group.list_commands` and `click.Group.get_command` — so the `dev` split is free to be **invocation-time**, and should be. `tests/test_py32_channel_gating.py`'s docstring (lines 11-39) documents the cost of the import-time shape at length: it needs **one subprocess per simulated version** because an in-process monkeypatch of `firestarter.__version__` after import "would pass, but for the wrong reason", and it explicitly rejects a module-reload approach because re-executing the module rebinds command objects while `cli`'s registry still points at the old ones.

### 6.4 Recommended shape

**Policy in `channel.py`**, beside `BETA_ONLY_BOARDS`, pure and unit-testable with no CLI:

```python
STABLE_DEV_COMMANDS: frozenset[str] = frozenset({"read", "test"})   # 999.15 resolved design

def is_dev_command_available(name: str) -> bool:
    return name in STABLE_DEV_COMMANDS or is_prerelease_build()

def dev_beta_only_message(name: str) -> str: ...
```

**Mechanism in `cli_handlers.py`:** a small `class _DevGroup(click.Group)` overriding `list_commands` (filter, so `dev --help` hides them) and `get_command` (return an informative-refusal stub for a gated name on a stable build), used as `@cli.group(name="dev", cls=_DevGroup)` at `:1171`. **Zero change to any of the nine `@dev.command` decorators.**

Three reasons over the simpler alternative (import-time `del dev.commands[name]` after the decorators):

1. **Informative refusal.** Deletion gives only Click's generic `No such command 'sdp'`. The `get_command` override can raise the `dev_beta_only_message` explanation, matching `beta_only_message`'s established "single explanation, reads identically everywhere" pattern.
2. **In-process testability.** Monkeypatching `firestarter.__version__` works — which is precisely what `channel.py`'s docstring prescribes, and which the import-time board gate cannot honour.
3. **No new subprocess harness.** The existing one stays scoped to the board gate, where it is genuinely required.

Trade-off to record honestly: an invocation-time gate is one *behavioural* layer, not a *surface* layer, so it does not benefit from the "frozen at import" argument that Criterion 5 of the py32 roadmap leaned on. If the operator wants the two `dev` gates to be provably identical in shape to the board gate, take the import-time variant and pay the subprocess harness. Recommend the `_DevGroup` subclass.

**Library-layer parity:** the board gate has one (`firmware.py`). The `dev` gate arguably needs none — `dev` subcommands are CLI-only entry points with no library callers. State that explicitly rather than leaving the asymmetry unexplained.

### 6.5 What interacts with deleting a subcommand

- Every `dev` subcommand is a **row in 999.15's classification table**: `read`, `reg`, `addr`, `consistency-check`, `write-cycle`, `fault-inject`, `validate-family`, `test`, `sdp`. Deleting `sdp` removes one row, one test file, and the awkward case — where `constants.py:66-67` documents the *firmware* commands as deliberately **not** DEV_TOOLS-gated "because they are real user-facing operations in every build" while the *host* surface was about to be classified beta-only. That is the exact host/firmware contradiction design note §2 names, and deleting the command dissolves it instead of arbitrating it. **Item 1 must precede item 5.**
- Nothing in `tests/__snapshots__/` or `tests/test_cli_handlers.py` asserts the `dev` subcommand list (grep for `'sdp'`/`"sdp"` in both returns zero hits), so no snapshot churn from the deletion. The only coupling is `tools/check_no_exists_proxy.py:156`.
- **Do not build the gate by scanning firmware source.** Four host gates broke in Phase 117 on firmware renames, and they failed **OPEN**. `channel.py` reads only `firestarter.__version__`; keep it that way.

---

## 7. Suggested build order

### 7.0 First, correct the premise: the primary `ci` job is *vacuously green* on this tree, not red

Measured in this session on `firestarter_app` @ `16a313a` (devcontainer, Python 3.12.13, mypy 2.3.0):

| `ci.yml` step | Result |
|---|---|
| `ruff check firestarter/ tests/` | `All checks passed!` |
| `ruff format --check firestarter/ tests/` | `115 files already formatted` |
| `pytest tests/ -q` | Full suite green, 30 snapshots passed, 0 failures |
| `python tools/check_mypy_watermark.py` | **exit 0** — `mypy errors: 1 (watermark: 35)` → `INFO: 1 errors — 34 below watermark.` |

**The fail-open mechanism, reproduced exactly.** `mypy firestarter/ tests/` emits:

```
pyproject.toml: [mypy]: python_version: Python 3.9 is not supported (must be 3.10 or higher)
/usr/local/lib/python3.12/site-packages/numpy/__init__.pyi:737: error: Type statement is only supported in Python 3.12 and greater  [syntax]
Found 1 error in 1 file (errors prevented further checking)
```

The tool's regex `re.search(r"Found (\d+) errors?", output)` (`check_mypy_watermark.py:64`) matches the **abort** line and returns `1`. The abort marker `errors prevented further checking` is never inspected. Two independent causes stack:

1. **`pyproject.toml:131 python_version = "3.9"`** — mypy ≥ 2 rejects it outright, and the `test` extra pins **`mypy>=2.1.0`** (`pyproject.toml:76`). The mypy config has been unusable since that floor was raised. Note the tension: `requires-python = ">=3.9"` (`:12`) and a `Programming Language :: Python :: 3.9` classifier (`:37`) — moving the mypy target to 3.10 is a **packaging-support decision needing operator sign-off**, not a lint tweak. Mitigating fact: `[tool.ruff] target-version = "py39"` (`:102`) already catches 3.9 *syntax* regressions, so a mypy target of 3.10 leaves only a narrow typing-only gap.
2. **An ambient `numpy`** in this devcontainer's `/usr/local/lib/python3.12/site-packages`, reachable through `tests/conftest.py`'s import graph. Its `__init__.pyi:737` uses a `type` statement, illegal below a 3.12 target ⇒ mypy aborts after one error. **numpy is not a declared dependency of this package** (grep: zero `import numpy` anywhere in `firestarter/`, `tests/`, `tools/`).

**Measured true counts:**

| Invocation | Result |
|---|---|
| `mypy firestarter/` (no `tests/`) | **25 errors in 6 files** — no abort; numpy is not on this import graph |
| `mypy --python-version 3.12 firestarter/ tests/` | **69 errors in 17 files (checked 120 source files)** — v1.23's number, reproduced exactly |
| `mypy firestarter/ tests/` (as CI invokes it) | aborts at 1 → gate passes |

**So PROJECT.md's "primary `ci` job RED" is a claim about *CI*, where numpy is absent, cause 2 does not fire, checking proceeds, and 69 > 35 fails honestly.** That is internally consistent but **not verified here**, and it is the **third** recorded instance of this devcontainer masking a CI-only defect. It must be settled by **one `workflow_dispatch` run of `ci.yml`** (the trigger exists, `ci.yml:24`) before any phase commits to a target number — the same discipline as v1.23 Phase 128's two real dispatches.

**Consequence for ordering.** The mypy item is **not a hard blocker** — every other item can prove local green today. It is the item whose *number moves* when the others land, and the item that decides whether the *later* items' new code is genuinely type-checked. Measured couplings:

- `tests/test_dev_sdp_cmd.py` carries **6 of the 69** errors → **item 1 lowers the honest count 69 → 63 for free.**
- `tests/test_dev_test_cmd.py` **9**, `tests/test_write_skip_sdp_unlock.py` **7**, `tests/test_validate_family_cmd.py` **6** — all the same `AppContext(..., hardware_manager=<object>, ...)` mock-typing class. **New tests for items 2/3/5 written in that same idiom will add errors of exactly that class.** If the watermark is made honest and tightened *after* those tests land, the gate goes red on the new work; if it is tightened *before*, the new tests must use a typed fixture.
- `firestarter/eprom_operations.py` carries **10** and `firestarter/database.py` **6** — production modules v1.30 does *not* otherwise touch. Fixing them is in scope for item 4 and nowhere else.

### 7.1 Recommended order (phases from 131)

| Phase slot | Item | Depends on | Parallelisable? |
|---|---|---|---|
| **A** (first, serial) | **Item 1** — delete `dev sdp` (`cli_handlers.py:2193-2318`), delete `tests/test_dev_sdp_cmd.py`, edit `tools/check_no_exists_proxy.py:156`, relocate the D-14 `MSG_ERR_UNKNOWN_CMD` mapping and the D-10 honesty wording. **All in one commit** — the target-list edit and the file deletion cannot be split without a red gate in between. | nothing | No — must be first. Smallest diff, largest unblocking effect. |
| **B** (second, serial) | **Item 4** — mypy gate-hardening. Make `check_mypy_watermark.py` fail-closed (detect `errors prevented further checking`, detect the `python_version ... is not supported` config rejection, assert a nonzero `checked N source files`, invoke `sys.executable -m mypy` instead of a bare `mypy` off `PATH`); settle the `python_version` / `requires-python` question with the operator; fix the **63** remaining errors; establish a **typed `AppContext` test fixture** in `tests/conftest.py` that later phases must use; set an honest watermark. Prove it with one real `workflow_dispatch` CI run. | **A** (so the count is final at 63, not a moving 69) | No — everything after it benefits from a genuinely-typed tree, and only this phase can produce a number that stays put. |
| **C** (third) | **Item 2** — the `dev test` SDP leg. The big one: `Step.group`/`role`, the `finally` cleanup registry, the widened `_run_step` except set, 4 new ops, 4 dispatch arms, `_DESTRUCTIVE_OPS` + a new `_SDP_OPS`, `_SDP_REGION` + `sdp_probe_pattern`, `derive_plan` capability derivation, `SCHEMA_VERSION` 1.2 → 1.3, `diagnostic_report` rows, `_ALWAYS_WRITES_NOTICE` extension, new-target entries in `check_no_exists_proxy`, `_HANDLER_FUNCTION_NAMES` if a handler helper is added, `doc/community-validation.md`. Likely worth splitting into 2 phases (mechanism + leg). | **B** | **Yes — with D.** Disjoint file regions (see 7.2). |
| **D** (third, alongside C) | **Item 3** — `write --sdp-relock`: the option, the refusal matrix, the post-write verify pass, the relock call, the exit-code rework, the relocated D-14 mapping, `doc/lockable-proms.md` + `doc/protocol-flags.md`. | **B**, and **A** (it inherits `dev_sdp`'s D-10/D-14 material) | **Yes — with C.** Much the smaller of the two. |
| **E** (fourth) | **Item 5** — 999.15 / gh#8 `dev`-group channel gating: `channel.py` policy + `_DevGroup`. | **A** (one fewer row to classify, and the contradiction gone); best after **C**/**D** so `dev test`'s final shape is what gets classified | Only weakly — the classification is keyed on command *names*, not bodies, so it *could* run beside C/D. Recommend after, so `dev --help`'s stable surface is asserted against final content. |
| **F** (last, serial) | **Item 6** — gh#12 outward follow-up + the stale-label fixes (`STATE.md:532`, `PROJECT.md:705`, and the three in-tree `301`/`377` comment references). | **C** and **D** | No. |

### 7.2 Why C and D can run in parallel

**Disjoint file regions.**

- **C** writes `firestarter/chip_test.py`, `firestarter/diagnostic_report.py`, `doc/community-validation.md`, and `cli_handlers.py` **only** in `_ALWAYS_WRITES_NOTICE` (`2045-2052`) and the `dev_test` body (`2059-2193`).
- **D** writes `cli_handlers.py` **only** in the `write` handler (`529-691`), plus two docs C does not touch.
- Neither modifies `eprom_operations.py`, `constants.py`, `sdp_capability.py`, or `channel.py`.
- The single shared file is `cli_handlers.py`, and the two regions are ~1,400 lines apart with no overlap.

If the executor model enforces one-writer-per-file, **serialise D after C** — D is the smaller diff and reordering costs little.

### 7.3 Why item 4 belongs at B, not at A and not at F

- **Not at A.** Its target number depends on A: `tests/test_dev_sdp_cmd.py` carries 6 of the 69 errors. Running it first means fixing 6 errors in a file that is about to be deleted, then re-baselining the watermark — pure waste, and a watermark that moves twice invites the "just bump it again" habit the fail-open originally hid behind.
- **Not at F.** Items 2, 3 and 5 all add test modules in the `AppContext(..., <object>)` idiom that generates 22 of the current 63 errors. Landing the honest gate *after* them means either the gate goes red on brand-new work or the watermark is set high enough to keep hiding things. Landing it *before* them means the typed fixture exists and the new tests are written correctly the first time — and the new code is actually type-checked as it lands, which is the whole point.
- **The "nothing else can prove a green CI until it lands" framing in the milestone brief is too strong for the local tree** (§7.0: `ci` passes locally today, vacuously) but may be exactly right for CI. Settle it with one `workflow_dispatch` in phase B before committing to a watermark. If CI *is* red, then B genuinely is a hard blocker on everything after it and the order above is unchanged — which is the useful property of putting it at B either way.

---

## 8. New vs modified — explicit per file

### 8.1 DELETED

| Path | What |
|---|---|
| `firestarter/cli_handlers.py` **lines 2196-2321** | `@dev.command(name="sdp")` + `dev_sdp` + its four gates. Last function in the file. |
| `tests/test_dev_sdp_cmd.py` | 558 lines, 12 invoke cases. Gate-ordering cases repurposed onto the new leg where they still apply. Also removes **6 of the 69** mypy errors. |

### 8.2 NEW files

| Path | Item | Note |
|---|---|---|
| `tests/test_sdp_leg.py` | 2 | Plan-derivation, the read-back oracle (incl. the equals-B, partial-change and all-`0xFF` cases), the `group=None` byte-identical no-op proof, the `finally` cleanup drain, the extended fail-closed deliberate-break. **Must be added to `tools/check_no_exists_proxy.py::_DEFAULT_TARGETS`** (fail-closed list). |
| `tests/test_write_sdp_relock.py` | 3 | Full refusal matrix + the verify-failure ⇒ skip polarity + the exit-code table. Same target-list obligation. |
| `tests/test_dev_channel_gating.py` | 5 | `list_commands` hiding + `get_command` informative refusal, on both simulated channels. Same target-list obligation. |
| *(optional)* `tests/app_context.py` | 4 | Typed `AppContext` factory, if it is factored out of `conftest.py`. Note `_DEFAULT_TARGETS` already lists non-`test_` helpers (`tests/fw_presence.py`, `tests/scan_paths.py`), so this too needs the entry. |

### 8.3 MODIFIED files

| Path | Item(s) | Specific edits (verified line anchors) |
|---|---|---|
| `firestarter/chip_test.py` | 2 | Op vocabulary `+4` after `:295`; `Step` `+2` fields (`:298-324`); `derive_plan` `+` leg derivation calling `sdp_capability(name, db)` (`:394-581`, appended after the erase branch at `:573`); `_DESTRUCTIVE_OPS` `+4` (`:636`); **new `_SDP_OPS`** beside `_MULTI_RUN_OPS` (`:654`); `run_plan` `+` cleanup registry + `try/finally` + lock-emitted flag (`:776-794`); `_run_step` `+` `(SerialError, HardwareOperationError)` arm (`:883-898`); `_dispatch_step` `+` `_SDP_OPS` arm before the `_MULTI_RUN_OPS` check (`:940`); **new** `_dispatch_sdp_*` helpers; **new** `sdp_probe_pattern` beside `generate_pattern` (`:59-67`); **new** `_SDP_REGION` beside `_DEFAULT_REGION` (`:829`). Imports: currently only `FLAG_CAN_ERASE` from constants (`:38`) — add `FLAG_SKIP_SDP_UNLOCK`; add `SerialError`/`HardwareOperationError` from `exceptions`. |
| `firestarter/diagnostic_report.py` | 2 | `SCHEMA_VERSION` `"1.2"` → `"1.3"` (`:55`) plus a comment in the existing house style; `render` `+` the Trap-3 recoverability row (`:456-528`); `_step_dict` (`:406-415`) only if a group/role column is wanted. **`dedup_fingerprint` needs no change** — it hashes `result.op` (`:224`), so the four new op strings enter the id for free. |
| `firestarter/cli_handlers.py` | 1, 2, 3, 5 | **Delete** `2196-2321`; `_ALWAYS_WRITES_NOTICE` `+` Trap-3 sentence (`2045-2052`); `write` handler `+` `--sdp-relock` option, refusal matrix, post-write verify, relock call, exit-code rework, relocated D-14 mapping (`529-691`); `@cli.group(name="dev")` `+ cls=_DevGroup` (`:1171`); **new** `_DevGroup` class; `+` new `channel` imports (`:35`). |
| `firestarter/channel.py` | 5 | **New** `STABLE_DEV_COMMANDS`, `is_dev_command_available`, `dev_beta_only_message`, beside `BETA_ONLY_BOARDS` (`:34`). No change to `is_prerelease_build`. |
| `firestarter/constants.py` | 6 | **Comment-only** fix at `:69-70`: `eprom_operations.py:301`/`:377` → `:329`/`:405`. Values, `COMMAND_SDP_*` (`:72-73`) and their `COMMAND_NAMES` entries (`:90-91`) all unchanged. |
| `tools/check_mypy_watermark.py` | 4 | `count_mypy_errors` (`:44-73`): detect the `errors prevented further checking` abort marker; detect the `python_version ... is not supported` config-rejection line; assert a nonzero `checked N source files`; invoke `sys.executable -m mypy` instead of the bare `"mypy"` off `PATH` (`:57`). Each new failure mode must exit `2`, not `0`. |
| `pyproject.toml` | 4 | `[tool.mypy] python_version` (`:131`) — **operator decision required**; `# mypy_error_watermark` (`:135`) new number. Possibly `requires-python` (`:12`) and the `Python :: 3.9` classifier (`:37`) if the target moves. |
| `tools/check_no_exists_proxy.py` | 1, 2, 3, 5 | Remove `"tests/test_dev_sdp_cmd.py"` (`:156`) **in the deletion commit** (fail-closed on a missing target); add the three new test modules as they land. |
| `tools/check_devtest_orchestrator.py` | 2 | `_HANDLER_FUNCTION_NAMES` (`:138-150`) — add any new private helper co-located with `dev_test`, or the gate silently under-covers it. (A `write`-handler helper is out of that set's scope by construction; note the resulting coverage gap explicitly rather than widening the set.) |
| `tests/test_parse_devtest_issue.py` | 2 | `:102` `assert obj["schema_version"] == "1.2"` → `"1.3"`. The frozen legacy `"1.1"` fixture (~`237-272`) stays untouched **by design**. |
| `tests/test_check_devtest_orchestrator.py` | 2 | `test_handler_function_names_all_resolve_to_real_callables` if `_HANDLER_FUNCTION_NAMES` grows. |
| `tests/test_revision_constants_parity.py` | 6 | **Comment-only** line references at `:71` and `:526` (`301`/`377` → `329`/`405`). Its firmware-source scan and `_strip_comments` (`:201-217`) must stay untouched. |
| `tests/test_chip_test.py` (1,958 lines) | 2 | Leg derivation + dispatch + cleanup coverage; the `group=None` byte-identical no-op proof. |
| `tests/test_dev_test_cmd.py` (716 lines) | 2, 4 | End-to-end leg rows in the report; also 9 of the 63 mypy errors. |
| `tests/test_diagnostic_report.py` (945 lines) | 2 | Schema bump, new rows, dedup-id divergence for the new op strings. |
| `tests/conftest.py` | 4 | Typed `AppContext` fixture that items 2/3/5's new tests must consume. |
| ~17 test modules + 5 production modules | 4 | The 63 remaining mypy errors. Production side: `eprom_operations.py` (10), `database.py` (6), `firmware.py` (3), `config.py` (3), `ic_layout.py` (2), `submit.py` (1) — **none of which v1.30 otherwise touches**, so this is the only phase that will open them. |
| `doc/community-validation.md` | 2 | Op-vocabulary table (`:31`) and the fingerprint/`write-partial` argument (`:114`) both enumerate op strings. |
| `doc/lockable-proms.md`, `doc/protocol-flags.md` | 3 | `--sdp-relock` is a new production surface. |
| `README.md` | 1, 3 | Only if it names `dev sdp` — grep found no literal hit, so verify at execution time. |

### 8.4 Explicitly NOT modified

`firestarter/eprom_operations.py` · `firestarter/sdp_capability.py` · `firestarter/serial_comm.py` · `firestarter/messages.py` (codegen-generated) · `tools/catalog/messages.toml` · the entire `firestarter/` **firmware** repo · `constants.py` values.

`eprom_operations.py` staying untouched is a deliberate, checkable property of this design: `sdp_lock`/`sdp_unlock`/`write_eprom`/`verify_eprom` already accept everything both survivors need, and the one thing that would have forced a change (`sdp_capability` needing the chip name and `db`) is answered by keeping the decision in the CLI handler, per that file's own recorded reasoning at `cli_handlers.py:610-612`.

---

## 9. Anti-patterns specific to this milestone

**Anti-pattern 1 — reintroducing an option to control the leg.**
*What it looks like:* `dev test --sdp` or `--skip-sdp` "for safety".
*Why it's wrong:* `dev test` takes **zero options** since Phase 121 D-05 — the four v1.21 flags were **removed, not disabled** (`dev_test(app, chip)` at `cli_handlers.py:2056`, verified two parameters). A flag mandatory on every invocation carries no information, and an optional one makes the leg unreachable in exactly the community runs it exists to serve.
*Instead:* derive from `sdp_capability(name, db)` inside `derive_plan`, like every other step.

**Anti-pattern 2 — verdict from the write's return value.**
*What it looks like:* `if not operator.write_eprom(...): verdict = OK  # the lock worked`.
*Why it's wrong:* Trap 1 in its purest form, and the same class as the SAFE-04 absent-chip trap where the real assertion turned out to be `read_hardware_revision_value.assert_not_called()` rather than an exit code. A transport error, brownout, absent chip or blank-check abort all produce the same non-zero result.
*Instead:* `actual == generate_pattern(*region)`. Record the write's return in `reason`, never in the verdict.

**Anti-pattern 3 — letting `classify_fingerprint` decide the verdict.**
*What it looks like:* `if fp.classification == FP_BLANK_CONTACT: verdict = SKIPPED`.
*Why it's wrong:* the blank/contact bucket fires on `ff_ratio >= 0.98` **even with zero mismatches** (`chip_test.py:173-183`), so it would relabel a genuine all-`0xFF` disaster as an inapplicable step — Trap 2 exactly.
*Instead:* equality decides; the fingerprint explains.

**Anti-pattern 4 — adding an op string without both allow-lists.**
*What it looks like:* a new `OP_SDP_LOCK` in the vocabulary and in `_DESTRUCTIVE_OPS`, but in no dispatch allow-list.
*Why it's wrong:* it fails **closed** with a confusing `matched no dispatch arm` BAD (`:944-952`) — which is the good outcome; the *bad* historical outcome, before those guards existed, was an unmapped op reaching `operator.erase_eprom()` and reporting `OK`.
*Instead:* vocabulary + `_DESTRUCTIVE_OPS` + `_SDP_OPS` + a dispatch arm + an extension of the deliberate-break test, in one change.

**Anti-pattern 5 — a bare `except Exception` in `run_plan`/`_run_step`.**
*What it looks like:* "just catch everything so cleanup always runs".
*Why it's wrong:* it swallows the deliberate `AssertionError` at `:1130-1132` whose entire purpose is to be loud about an unreachable branch being reached, and it converts a programming error into a diagnostic verdict.
*Instead:* `try/finally` for the cleanup (runs on `KeyboardInterrupt` too, swallows nothing), plus a **named** `(SerialError, HardwareOperationError)` arm in `_run_step`.

**Anti-pattern 6 — claiming the run "ended unlocked".**
*What it looks like:* a report line reading "SDP disabled — part is unlocked".
*Why it's wrong:* `sdp_unlock`'s own docstring forbids it (`eprom_operations.py:1750-1760`): protection state is unreadable on this family, so no return value can say more than "the sequence was sent and the firmware reported OK". This is the v1.22 C-5 overclaim class.
*Instead:* "an unlock sequence was emitted", plus the recovery sentence ("a plain `firestarter write` auto-unlocks; recovery is a **rewrite** — protocol 0x0D has no erase operation at all").

**Anti-pattern 7 — deleting a file that a fail-closed target list names, in its own commit.**
*What it looks like:* `git rm tests/test_dev_sdp_cmd.py`, push, watch `tools/check_no_exists_proxy.py` go red.
*Why it's wrong:* `_DEFAULT_TARGETS` (`:156`) is a literal, deliberately non-glob enumeration and the gate fails closed on a missing target (~`:331`). Recorded precedent: `git rm REQUIREMENTS.md` at milestone close.
*Instead:* delete the file and edit the list in the **same** commit.

---

## 10. Confidence and open questions

| Area | Confidence | Basis |
|---|---|---|
| Integration-point verification (§1) | **HIGH** | Every anchor read out of the live tree at `16a313a`; four stale ones named. |
| The step-model mechanism (§2) | **HIGH** | `run_plan`/`_run_step`/`_dispatch_*` read in full; `destructive_gate_closed` is a direct in-tree precedent; the missing exception classes confirmed against `exceptions.py`'s class hierarchy and `serial_comm.py`'s raise sites. |
| State flow (§3) | **HIGH** | `generate_pattern`'s purity and `Step.write_region`'s set-once discipline both read directly; the zero-plumbing conclusion follows from them. |
| Abort limits (§4) | **HIGH** on what does not exist (grep: no `atexit`, no `KeyboardInterrupt`, two temp-file `finally`s). **HIGH** on the honesty limits — they are the tree's own recorded position. |
| `write --sdp-relock` chain (§5) | **HIGH** | Handler read end to end; the absence of any `verify_eprom` call in it is a grep-confirmed negative. |
| Channel gating (§6) | **HIGH** | `channel.py` read in full; the nine decorator sites enumerated; the `click.Choice`-forces-import-time distinction is structural. |
| Build order (§7) | **MEDIUM-HIGH** | The dependency argument is solid. The single soft spot is whether CI is red or vacuously green — see below. |
| Per-file new/modified (§8) | **HIGH** | Every path opened or grepped. |

**Open questions for the roadmapper to route:**

1. **Is `ci` actually red in CI?** Locally it is vacuously green (§7.0). Settle with one `workflow_dispatch` run of `ci.yml` in phase B, *before* committing to a watermark number. Cheap, and it decides whether B is a hard blocker or merely the right second phase.
2. **`python_version` / `requires-python`.** Moving the mypy target to `"3.10"` is the mechanically obvious fix, but the package advertises 3.9 support in two places (`pyproject.toml:12`, `:37`). Needs an operator decision. Mitigation available: `[tool.ruff] target-version = "py39"` already guards 3.9 syntax.
3. **Shared or distinct SDP region?** §2.4 recommends `_SDP_REGION = (256, 256)` for evidence hygiene. A phase could legitimately choose the shared `(0, 256)` window for simplicity — but must then explain in the report why step 3's read-back is not confounded by the earlier `OP_WRITE` step.
4. **Invocation-time or import-time `dev` gate?** §6.4 recommends the `_DevGroup` subclass (informative refusal, in-process tests). The import-time variant is more symmetric with the board gate but costs a subprocess harness. Operator/roadmapper choice; either satisfies 999.15.
5. **Exit-code semantics for `write --sdp-relock`** (§5.4). A concrete table is proposed; it needs a decision, not a discovery.
6. **Is `_dispatch_sdp` one function or four?** Four ops, four assertions, but three of them share the write/read-back shape. A single `_dispatch_sdp(op, ...)` with an internal branch mirrors `_dispatch_multi_run`; four small functions read better in the report code. Style call, no correctness content — but whichever is chosen must be reflected in the `_SDP_OPS` deliberate-break test.

---

## Sources

All findings are first-hand reads of, or measurements against, the live tree at `firestarter_app` @ `beta` `16a313a` — no external sources were consulted, and none would be authoritative for a question about this codebase's internal structure.

- `firestarter/chip_test.py` (1,253 lines, read in full across four passes)
- `firestarter/diagnostic_report.py` (532 lines, read in full)
- `firestarter/sdp_capability.py` (281 lines, read in full)
- `firestarter/channel.py` (81 lines, read in full)
- `firestarter/cli_handlers.py` (2,321 lines — `write` handler `529-691`, `_build_op_flags` `295-346`, `map_typed_errors` `180-215`, `dev` group + decorators, `_resolve_write_scope` `1993-2035`, `dev_test` `2045-2193`, `dev_sdp` `2196-2321`)
- `firestarter/eprom_operations.py` (`_setup_operation`/`_operation_context` `315-410`, `write_eprom` `1583-1676`, `sdp_unlock` `1736`, `sdp_lock` `1784`)
- `firestarter/constants.py` (`60-95`), `firestarter/exceptions.py` (class hierarchy), `firestarter/serial_comm.py` (raise sites)
- `tools/check_mypy_watermark.py`, `tools/check_no_exists_proxy.py`, `tools/check_devtest_orchestrator.py`, `tools/check_no_log_in_sdp_window.py`, `tools/check_sdp_capability_invariants.py`, `tools/parse_devtest_issue.py`
- `pyproject.toml`, `.github/workflows/ci.yml`, `.github/workflows/beta-release.yml`
- `tests/test_py32_channel_gating.py` (docstring `11-49`), `tests/test_parse_devtest_issue.py`, `tests/test_revision_constants_parity.py`, `tests/test_skip_census.py`, `doc/community-validation.md`
- Executed measurements: `mypy 2.3.0` under Python 3.12.13 at three targets; `ruff check`; `ruff format --check`; `pytest tests/ -q` (full suite); `python tools/check_mypy_watermark.py`
- `.planning/notes/sdp-surface-retirement-and-behavioral-proof.md` (157 lines, read in full); `.planning/PROJECT.md` §"Current Milestone: v1.30" (`38-154`)

---
*Architecture research for: v1.30 SDP Surface Retirement & Behavioral Lock Proof (host-only, `firestarter_app`)*
*Researched: 2026-08-03*
