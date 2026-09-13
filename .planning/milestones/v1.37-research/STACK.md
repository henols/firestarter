# Stack Research — v1.36 `dev test` Fidelity

**Domain:** Host-only Python CLI change (`firestarter_app`) — conditional test-harness operations, a
versioned JSON diagnostic-report schema bump (1.7 → 1.8) under a hash-continuity gate, and a structural
test over a derived plan object
**Researched:** 2026-09-02
**Confidence:** **HIGH** on everything measured on this tree (every count, timing, hash and plan-shape
figure below was produced by running the code at HEAD, transcribed verbatim). **HIGH** on the package
version facts (queried directly from the PyPI JSON registry API, the canonical publisher of that
metadata — see *Sources* for why this is not a Context7 lookup). **MEDIUM** on the syrupy 6.0.0
breaking-change list (single vendor source, GitHub releases page).
**Tree measured:** `firestarter_app` @ `0a93999` (branch `gsd/v1.35-documentation-consolidation-wiki-migration`),
`firestarter/__version__ = 3.0.0b33`, `SCHEMA_VERSION = "1.7"`.
**Measurement environment:** `firestarter_app/.venv/ci-replica/` (CPython 3.11.x, the CI-parity venv) —
*not* the devcontainer's default 3.12, which masks app CI.

---

## Bottom line up front

**Recommendation: add exactly one thing, and it is a version bound, not a library.**

| Question asked | Verdict | One-line reason |
|---|---|---|
| (a) Property/structural testing over `derive_plan` | **ADD NOTHING** | The input domain is finite and *tiny*: 677 distinct part numbers × 3 write scopes = 2,031 plans, which collapse to **9** distinct `(scope, op-sequence, is_uv)` classes. An exhaustive sweep of the entire domain costs **4.22 s** against a suite that already runs **737 s**. There is nothing for a generative tester to discover. |
| (b) Versioned JSON schema evolution / frozen-fixture parsing | **ADD NOTHING** | The consumer (`tools/parse_devtest_issue.py`) already matches `schema_version` **by presence, not by value** (`tests/test_parse_devtest_issue.py:151`), and two frozen schema-1.1/1.2 bodies already prove it. A JSON Schema validator would be a *third* declaration of a shape that `to_dict()` and the fixtures already pin twice. |
| (c) Stable content-addressed hashing across schema changes | **ADD NOTHING** — but the milestone has **two proven re-key hazards it has not accounted for** | `dedup_fingerprint()` never reads `to_dict()`. It hashes a hand-picked `"|"`-joined field list, so it is immune to schema evolution *by construction* — no canonicalizer (RFC 8785 / `jcs`) has anything to do. The danger is elsewhere and is **measured below**: two named v1.36 deliverables each change the fingerprint today. |
| **The one real stack change** | **ADD `syrupy>=5.0,<7`** (or `<6`) | `syrupy` is pinned unbounded at `>=5.0`; the CI replica holds **5.5.3**, but PyPI now serves **6.0.0** (2026-08-22), whose headline breaking change is that **stdlib dataclasses are serialized natively by the Amber serializer**. `Plan`, `Step`, `Fingerprint` and the report classes are all `@dataclass`. A fresh CI run today already resolves 6.0.0. |

Everything below is the evidence.

---

## Recommended Stack

### Core Technologies — all already installed, no change

| Technology | Version (measured in CI replica) | Purpose | Why it stays, unchanged |
|---|---|---|---|
| CPython | **3.11** in CI (`ci.yml` sets `python-version: '3.11'`); `requires-python = ">=3.9"`; mypy targets `3.10` | Runtime | Nothing in this milestone needs a newer feature. Do not touch `requires-python` — it is published PyPI metadata and an operator-level decision (`pyproject.toml` D-13 note). |
| pytest | **9.1.1** | The whole test surface | Already carries 1,952 passing tests, including the exhaustive whole-DB sweep idiom this milestone needs (`test_erase_flag_invariants.py`, `test_sdp_db_invariant.py`, `test_page_size_invariants.py`). |
| `hashlib` (stdlib) | — | `dedup_fingerprint` sha256 | Already the implementation. See §(c). |
| `dataclasses` (stdlib) | — | `Plan` / `Step` / `Fingerprint` / report structures | `dataclasses.asdict()` gives a fully comparable structure for free — this is the entire "schema-driven approach" a plan-shape test needs. |
| `json` (stdlib) | — | Report serialization + fixture comparison | `json.dumps(..., sort_keys=True)` is sufficient for every comparison this milestone performs. |
| ruff | **0.16.4** (pinned `>=0.15.14`) | Lint + format, `select = ["E","F","I","UP"]` | Note the standing trap: `select` excludes `BLE`, so every `# noqa: BLE001` in the tree is inert. Do not rely on one. |
| mypy | **2.3.1** (pinned `>=2.1.0,<3`) | Watermark gate, `tools/check_mypy_watermark.py` | `firestarter.chip_test` and `firestarter.diagnostic_report` are in **neither** strict-island override list in `pyproject.toml` — they contribute only to the watermark count, not to a strict gate. Adding typed helpers there is free; it will not trip a new gate. |
| pytest-cov | **7.1.0** | `--cov-fail-under=70` | Deleting dead fields (`voltage.vpp_mv`, `banner.locked_steps`) *removes* lines; coverage can only go up. No risk. |

### Supporting Libraries

| Library | Version | Purpose | Verdict |
|---|---|---|---|
| syrupy | installed **5.5.3**, PyPI current **6.0.0** (2026-08-22), pinned `>=5.0` **unbounded** | Snapshot assertions; 32 snapshots currently pass, all in `tests/__snapshots__/test_characterization.ambr` | **Constrain the pin.** See §"The one real stack change". |

### Development Tools

| Tool | Purpose | Notes for this milestone |
|---|---|---|
| `tools/check_diagnostic_report_claims.py` | AST string-literal claim scanner over `diagnostic_report.py` | It scans **exactly** that one file. Every new report string literal v1.36 adds (new field labels, the `divergence` metric label, the `elapsed` label) passes through it. Its 14-entry `FORBIDDEN_PATTERNS` table is forked verbatim from the meta-repo gate — do not diverge the vocabulary. |
| `tools/check_devtest_orchestrator.py` | Orchestrator-contract gate | `dev_test` must not open extra connections. R4's "32 serial connects" work runs straight through this gate's subject matter. |
| `.venv/ci-replica/` + `tools/ci_replica_venv.sh` | py3.11 CI-parity venv | **Use it for every measurement.** The devcontainer default is 3.12 and has been *proven* to hide breakage that reddens beta CI. |

## Installation

```bash
# Nothing new is installed. The only change is a tightened bound in
# firestarter_app/pyproject.toml, in [project.optional-dependencies].test:
#
#   -    "syrupy>=5.0",
#   +    "syrupy>=5.0,<7",     # or <6 — see the decision note below
#
# Verify against the CI-parity interpreter, never the devcontainer default:
cd firestarter_app
bash tools/ci_replica_venv.sh          # (re)build the py3.11 replica
.venv/ci-replica/bin/python -m pip install -e '.[test]'
.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q
```

**No change to `[project].dependencies`.** The shipped runtime dependency set stays exactly
`pyserial, requests, tqdm, click, rich, packaging`. Every candidate discussed in this document is a
*test-time* concern, and even those are declined.

---

## (a) Structural / property testing over `derive_plan` — **ADD NOTHING**

### The measurement that settles it

`derive_plan(name, db, *, write_scope)` at `firestarter/chip_test.py:486` is a **pure, deterministic
function of two enumerable inputs**: a chip name from the shipped database, and one of exactly three
`write_scope` values (`_WRITE_SCOPES`; anything else raises `ValueError`, never silently falls back).

Measured on the py3.11 CI replica at HEAD:

| Fact | Measured value |
|---|---|
| Rows in `chip_database.json` | **746** |
| **Distinct** `part_number` values (69 rows duplicate a part number across vendors) | **677** |
| Full input domain (677 × 3 scopes) | **2,031** plans |
| Wall-clock to derive **all 2,238** plans (746 rows × 3, i.e. the *superset* including duplicates) | **4.22 s** |
| Wall-clock to derive all 2,031 and compute a shape census | **~5.3 s** |
| Current full suite runtime, py3.11 | **737.37 s** (1,952 passed, 3 failed) |
| Cost of an exhaustive sweep as a share of the suite | **0.57 %** |
| Distinct plan shapes including `region_policy` + `cycle_payload` | **23** |
| Distinct `(scope, op-sequence, is_uv)` classes | **9** |

The nine classes, verbatim, with their populations:

```
scope    is_uv   n     op sequence
-------  -----   ---   ------------------------------------------------------------
none     False   304   id->read->blank-check
none     True    270   id->read->blank-check->erase
none     False   103   id->read->blank-check->erase
full     False   304   id->read->write->verify->erase->blank-check->write-baseline-b->
                       write-baseline-a->sdp-lock->write-inhibited->sdp-unlock->write-restored
full     True    270   id->read->blank-check->write->verify->erase->write-baseline-b->
                       write-baseline-a->sdp-lock->write-inhibited->sdp-unlock->write-restored
full     False   103   id->read->blank-check->write->verify->erase->write-baseline-b->
                       write-baseline-a->sdp-lock->write-inhibited->sdp-unlock->write-restored
partial  False   304   id->read->write-partial->verify->erase->blank-check->write-baseline-b->...
partial  True    270   id->read->blank-check->write-partial->verify->erase->write-baseline-b->...
partial  False   103   id->read->blank-check->write-partial->verify->erase->write-baseline-b->...
```

The entire 677-chip catalogue partitions into **three populations — 304 / 270 / 103** — and each
produces one op sequence per scope. That is the whole behaviour space of the function this milestone
wants to constrain.

### Why hypothesis is the wrong tool here, specifically

**hypothesis 6.167.1** (PyPI, released 2026-08-30; `requires-python >=3.10`; core deps
`sortedcontainers>=2.1.0` plus `exceptiongroup` below 3.11) is an excellent library and it is the
wrong one for this job, for four reasons that are not style preferences:

1. **It samples where you can enumerate.** Hypothesis's value is exploring domains too large to
   enumerate. This domain is 2,031 items and enumerates in 4.22 s. A default hypothesis profile draws
   ~100 examples per property — it would examine **5 %** of a domain you can examine *entirely*, and
   would still leave the roadmap unable to state "this holds for every shipped chip."
2. **Generated chips are not shipped chips.** Any hypothesis strategy would either (i) draw from the
   real database — at which point it is a slower, sampling version of the exhaustive loop — or
   (ii) synthesize DB records, at which point it is testing chips that do not exist and cannot fail
   for a customer. The milestone's motivating defects (gh#23/#28/#31) are about **specific real parts**.
3. **It breaks this repo's reachability discipline.** Every whole-DB invariant test in this tree
   records *reachability evidence*: the leg was observed to fail against a named, temporary mutation
   before being trusted (`test_erase_flag_invariants.py` docstring transcribes this for six legs; see
   also `test_sdp_db_invariant.py` legs 4 and 7, its explicit "non-vacuous proof" legs). A randomized
   input makes "this leg failed against mutation M" a probabilistic rather than a categorical claim,
   and a flaky red in a 737-second suite is a gate people learn to re-run.
4. **CI determinism is load-bearing here.** `.github/workflows/ci.yml` runs on **every branch push**.
   A nondeterministic failure in this suite is indistinguishable from the known-flaky
   `test_skip_census.py` failures already present in this environment, and would be triaged as noise.

### What to build instead — three tests, all stdlib + pytest

| Test | Shape | Cost | Precedent in-tree |
|---|---|---|---|
| **1. Plan-class census (the anti-narrowing gate)** | Sweep all 677 × 3, bucket by `(scope, tuple(op for op in steps), is_uv)`, assert the result equals a committed 9-row table **element for element**, naming any chip that moved in either direction. | ~5 s | `test_sdp_db_invariant.py` leg 5 — `_COMMITTED_SDP_ALLOW_ENTRIES` element-wise parity, with the explicit rationale that a committed snapshot is "cheap insurance that costs nothing to keep". |
| **2. The no-information invariant** | Same single sweep (reuse via a module-scoped fixture — pay the 4.22 s **once**, not per leg). For every plan, for every step: assert no step is emitted whose result is empty by construction, and assert **every `write*` step is followed by a `verify` in the same cycle** — the milestone's own named load-bearing dependency. Collect **all** violations and fail once with the full offender list, rather than aborting on the first. | ~0 s marginal | `test_erase_flag_invariants.py` leg 3 — "expressed *from the rule* rather than a snapshot". |
| **3. The closure sentinel** | Derive the op vocabulary from the module's own `OP_*` constants (`{v for n,v in vars(chip_test).items() if n.startswith("OP_") and isinstance(v,str)}`) and assert the enumerated set equals it, so a future tenth op cannot escape by omission. | ~0 s | **Copy `test_shipped_ops_never_reach_sdp_arm` (`tests/test_chip_test_sdp_leg.py:827`) directly** — it already does exactly this, including the "a future eighth shipped op cannot silently escape this sentinel by omission" clause. This is the sentinel the milestone brief names. |

**Use `pytest.mark.parametrize` over the 9 classes, and a plain loop over the 2,031 plans.** Do *not*
parametrize 2,031 cases: pytest collection metadata for 2,031 ids is real overhead for zero diagnostic
gain, and a single loop-and-collect assertion produces a *better* failure message (all offenders at
once). This is exactly what the existing whole-DB sweeps do.

### A finding the milestone brief has not counted: a fifth no-information case

The brief names **four** measured cases of work that is empty by construction. The sweep found a
fifth, and it is the largest:

> **637 of 677 chips (94.1 %) carry six SDP-leg steps in `Plan.steps` that are `supported=False` for
> every one of them.** Only **40** chips have any SDP step supported. Of the 637: **367** are refused
> as "not on the SDP-capable list … pre-SDP generation", and **270** are UV parts refused with "SDP
> lock/unlock applies only to protocol 0x0D parallel EEPROMs (observed protocol 0x0B)".

`run_plan`'s own docstring says "NA steps are recorded without any operator call" — so these six cost
no serial traffic. **But they are not free**, because they *do* produce a `StepResult`, which *does*
enter `report.results`, which *does* enter `dedup_fingerprint`. That makes them the single largest
collision between this milestone's two headline requirements. See §(c), hazard 1.

**Roadmap implication:** the structural test must be written to *permit* the six unsupported SDP steps
to remain in the plan (they are hash ballast, not waste), or the fingerprint gate must be redesigned.
The phase that writes the invariant needs to state which, explicitly, before it writes the assertion.

---

## (b) Versioned JSON schema evolution, 1.7 → 1.8 — **ADD NOTHING**

### What already exists (measured, not assumed)

| Mechanism | Where | What it already guarantees |
|---|---|---|
| Single source of truth for the shape | `diagnostic_report.py:771` `to_dict()` — deliberately **hand-written, not `dataclasses.asdict()` wholesale** ("Pitfall 3") | One place bakes in `schema_version`; `render()` and `to_json_block()` both consume that same dict, so a field cannot exist in JSON but not in the table. |
| Version-tolerant consumer | `tools/parse_devtest_issue.py`, proven by `tests/test_parse_devtest_issue.py:151` `test_detect_schema_version_matched_by_presence_not_exact_value` (the test literally feeds `"9.9-future"` and expects success) | **A 1.8 report parses today, with zero consumer change.** A previous version of that test hardcoded `"1.2"` and broke on the 1.3 bump; the current one imports `SCHEMA_VERSION` rather than restating it (line 116-123). That lesson is already learned and encoded. |
| Frozen old-shape fixtures | `tests/test_parse_devtest_issue.py` — `_B11_BODY` (schema 1.1, populated `fw_board_identity`) and `_NULL_IDENTITY_BODY` (schema **1.2**, `fw_board_identity: null`), both carrying an explicit **"Must NEVER be regenerated from live `to_dict()` output"** instruction | Backward-compatible parsing of the exact shapes v1.36 must keep reading. |

**The 1.2 fixture already contains every field v1.36 deletes** — `voltage.vpp_mv`, `voltage.vpe_mv`,
and `banner.locked_steps` are all present in `_NULL_IDENTITY_BODY`. This is the correct and complete
mechanism for a field deletion, and it already works: **stop producing the field, keep tolerating it on
read.** That producer/consumer asymmetry is the whole of "backward-compatible schema evolution" here.

### Why a JSON Schema validator does not earn its place

`jsonschema` **4.26.0** (PyPI, 2026-01-07; `requires-python >=3.10`; core deps `attrs`,
`jsonschema-specifications`, `referencing`, `rpds-py`) is the obvious candidate. Decline it:

1. **It would be a third declaration of one shape.** `to_dict()` declares it; the frozen fixtures pin
   it; a `.schema.json` would declare it a third time, and the *only* thing keeping the three in sync
   would be a human. The failure mode is a schema file that drifts and silently validates nothing —
   this repo has a documented history of exactly that class of defect (a gate that fails open, a
   selector that iterates the wrong level and passes vacuously).
2. **It solves a problem this project does not have.** JSON Schema earns its place when *untrusted
   third parties produce* documents you must validate. Here `firestarter_app` is the **sole producer**
   and `tools/parse_devtest_issue.py` is the sole consumer, both in the same repo, both under the same
   CI. There is no interop boundary.
3. **`rpds-py` is a compiled Rust extension.** Even as a test extra it adds a wheel-availability and
   platform surface to a repo whose one existing compiled dependency (`pyusb`/libusb) was deliberately
   isolated into its own optional extra *and its own separate CI job* precisely so it could not take
   down the primary gate (`ci.yml`, Phase 127 D-01/D-02). That precedent argues against, not for.

### What to build instead

| Need | Mechanism | Cost |
|---|---|---|
| Prove 1.8 still parses in the consumer | Nothing — already proven by presence-based detection. Add **one** frozen 1.8 body to the existing fixture family for symmetry. | 1 fixture |
| Prove the 1.2 fixtures still parse after the deletions | They already do; add an explicit assertion that the *deleted* keys are still tolerated on read, so the tolerance is a stated contract rather than an accident. | 1 assertion |
| Prove the new fields actually appear | Assert on `to_dict()` keys directly, as `test_diagnostic_report.py` already does. | existing idiom |
| Catch an accidental key rename/removal | A committed sorted key list for `to_dict()`, asserted element-wise — the `_COMMITTED_SDP_ALLOW_ENTRIES` pattern applied to schema keys. This is the *one* genuinely missing gate: no test today pins the full key set of `to_dict()`. | ~20 lines |

---

## (c) Stable content-addressed hashing across schema changes — **ADD NOTHING, but two proven hazards**

### Why no canonicalizer is needed

`dedup_fingerprint()` (`diagnostic_report.py:186-240`) does **not** hash `to_dict()`. It builds an
explicit list and joins it with `"|"`:

```
parts = [ac.chip, str(ac.protocol)]
    + [f"{r.op}={r.verdict}:{cls}" for r in report.results]
    + [repeat_policy_tag(...)]   # appended only when non-empty
    + [coverage_tag(...)]        # appended only when non-empty
canonical = "|".join(parts)
sha256(canonical.encode("utf-8")).hexdigest()[:12]
```

This is an **allow-list hash over a hand-picked field set**, and it is the correct design. It is
immune to key ordering, key addition, key deletion, float formatting, `None`-vs-absent and every other
canonical-serialization hazard, *because the schema is not its input.*

RFC 8785 (JSON Canonicalization Scheme) and its Python implementation `jcs` are the standard answer
when the hash input **is** the JSON document — sorted keys, ECMAScript number serialization, no
inter-token whitespace. **That is not this design and adopting it would be a regression:** hashing the
canonicalized document would make every additive field in the 1.8 bump re-key every report, which is
precisely the outcome the milestone forbids. **Do not adopt `jcs`. Do not switch to hashing
`to_dict()`.** Record that as a decision, because it is the tempting refactor.

The two existing tag functions (`repeat_policy_tag`, `coverage_tag`) already encode the correct
evolution discipline in-source, and the source comments state it: *compute, then append to `parts`
**only when non-empty**, so the default case stays byte-identical and no historical `count_agreeing`
group is re-keyed.* **Any new discriminator v1.36 adds must follow that exact shape.**

### Hazard 1 — pruning no-information steps re-keys the fingerprint (PROVEN)

Run on this tree at HEAD, `m27c512`, `write_scope="full"`, 12 steps:

```
A) today, all 12 steps                          -> a00791f1c2b4
B) with the 6 unsupported SDP steps pruned      -> 7d1cd4157cfa      B == A ?  False
```

Because `parts` gains one entry **per `StepResult`**, removing an operation from the plan removes an
entry and changes the hash. For the **637 of 677 chips** whose six SDP steps are all `supported=False`,
"stop emitting the operation that cannot tell you anything" and "keep `dedup_fingerprint`
byte-identical" are **directly contradictory** as currently specified.

`PROJECT.md`'s blast-radius statement — *"Not one field being added, filled or deleted is in that hash
today"* — is **true for report fields and does not cover this.** The hazard is at the plan-composition
layer, not the schema layer.

**The resolution that costs nothing:** distinguish *not running* an operation from *not recording*
it. Keep the `StepResult` (op + an NA/skipped verdict + empty classification) so `parts` is unchanged,
and skip only the work. That is already exactly what `run_plan` does for unsupported steps today —
"NA steps are recorded without any operator call." Extending that existing mechanism to the four (five)
newly-identified empty-by-construction cases satisfies both requirements simultaneously. **This should
be a named decision in the first v1.36 phase**, because the naive implementation (drop the step from
`Plan.steps`) is the one that breaks the gate.

### Hazard 2 — canonical chip naming re-keys the fingerprint (PROVEN)

`ac.chip` is `parts[0]`. It is assigned the **raw CLI token** at `cli_handlers.py:2384` (`chip=chip`),
and `db.get_eprom` is case-insensitive.

```
A) chip="m27c512"  (what a user types, and what every open issue title shows)  -> a00791f1c2b4
C) chip="M27C512"  (the canonical database part_number)                       -> a6f6c6354047
C == A ?  False
```

**732 of 746** database rows have a `part_number` that is not equal to its own lowercase form. The six
motivating issues are titled `[dev test] at28c256 — FAIL`, `m27c512`, `w27e257` — all lowercase.
Therefore the "Canonical chip naming" deliverable, implemented as stated, **re-keys essentially every
historical fingerprint in the project**, resetting every `count_agreeing` group and disturbing the same
Phase 114 GRAD-01 no-auto-graduate lock the milestone brief says must not be disturbed.

**Two mutually exclusive resolutions; the roadmap must pick one explicitly:**

| Option | Mechanism | Cost |
|---|---|---|
| **R1 (recommended)** — decouple display from hash | Add a **new** `auto_capture.canonical_part_number` field for the issue title and the report body, and leave `ac.chip` (and therefore `parts[0]`) carrying the raw token. Purely additive; zero re-key. | One field; the issue title reads from the new field. |
| **R2** — normalize `parts[0]` | Feed `parts[0]` a case-folded or canonicalized name. Re-keys history. Only defensible if the operator explicitly accepts a one-time global re-key and the `count_agreeing` reset that follows. | Operator decision, not a phase's to make. |

Also note before implementing either: the database's `name` field is a **comma-joined alias list**
(`at28c256` resolves to `"AT28C256,AT28C256E,AT28C256F,AT28HC256,..."`), so "the canonical name" needs
`part_number`, not `name`, and needs a stated rule for which alias an issue title shows.

### Hazard 3 — the byte-identity gate the brief assumes exists, does not

`PROJECT.md` says the gate is *"asserted against the frozen schema-1.2 fixtures."* Measured:

- The frozen 1.2/1.1 fixtures carry `dedup_fingerprint` values `"deadnu11id00"`, `"aaaa11112222"`,
  `"shared0000ab"`, `"b11deadbeef"` — **hand-written tokens, not real hashes.** They prove *parsing*
  and *grouping*, and cannot prove hash continuity.
- Every dedup test in `tests/test_diagnostic_report.py` is **relational**, computed at runtime:
  `dedup_fingerprint(a) == dedup_fingerprint(b)`, or `!=`. A change to the hash **algorithm** passes all
  of them.
- There is **exactly one** frozen expected-hash literal in the whole suite:
  `tests/test_diagnostic_report.py:1377` and `:1381`, both asserting `"a0a50436ae3d"` (added by the
  `coverage_tag` quick task).

**So the first thing v1.36 must build is the gate itself:** a `pytest.mark.parametrize` table of
frozen `(report shape → expected 12-char hash)` pairs, computed **once, at the start of the milestone,
against HEAD before any change lands**, covering at minimum the three populations × three scopes and
both `repeat_policy_tag` / `coverage_tag` states. Stdlib + pytest; no library. Precedent and idiom:
`test_diagnostic_report.py:1377`. Without this, the "blast-radius gate" is a claim, not a check — and
hazards 1 and 2 above are exactly what it would have caught.

---

## The one real stack change: bound `syrupy`

| Fact | Value | Source |
|---|---|---|
| Pin in `pyproject.toml` `[test]` extra | `syrupy>=5.0` — **no upper bound** | measured |
| Resolved in `.venv/ci-replica/` | **5.5.3** | `importlib.metadata` |
| Current on PyPI | **6.0.0**, released **2026-08-22** | PyPI JSON API |
| `syrupy` runtime deps | `pytest>=8.0.0` only | PyPI JSON API |
| 6.0.0 breaking change #1 | *"stdlib dataclasses are now serialized natively by the Amber serializer. The separate `DataclassPlugin` has been removed."* Dataclass snapshots may change from repr-style strings to structured Amber form. | syrupy releases page |
| 6.0.0 breaking change #2 | JSON extension serializes `datetime.date` as `YYYY-MM-DD` instead of a `repr` string. | same |
| 6.0.0 breaking change #3 | `path_value(..., regex=False)` now replaces values at nested paths such as `user.token`. | same |

**Current exposure: zero.** The single `.ambr` file holds only CLI-output strings — a scan for
dataclass-repr blocks returns 0 matches, and all 32 snapshots pass under 5.5.3.

**v1.36 exposure: real.** `Plan`, `Step`, `Fingerprint` and the report structures are all
`@dataclass`, and a milestone about report shape is precisely when someone reaches for
`assert report == snapshot`. Under an unbounded pin, CI resolves 6.0.0 on the next clean install and
that assertion's serialization changes under the milestone's feet, with the diff arriving as a
snapshot mismatch rather than as a dependency change.

**Recommendation:** `"syrupy>=5.0,<7"`, with a comment in the same style as the existing `mypy<3` and
`pyusb<2` bounds (which is this repo's documented practice: *"Raise the bound deliberately and
re-verify … in the same commit"*). Choose `<7` over `<6` if the milestone first re-runs the 32
snapshots under 6.0.0 and they pass; choose `<6` if it does not want to spend that verification. Either
is defensible; **unbounded is not.**

**Plus one belt-and-braces rule for the phase:** snapshot `report.to_dict()` — a plain `dict` — never
the `DiagnosticReport` dataclass. That sidesteps the 6.0.0 dataclass-serialization change entirely and
keeps the snapshot readable as the JSON that actually ships in the issue body.

---

## Alternatives Considered

| Recommended | Alternative | When the alternative would be right |
|---|---|---|
| Exhaustive sweep over 677 × 3 | **hypothesis 6.167.1** | If `derive_plan` took a continuous or combinatorially large input (address ranges, byte patterns, timing values). It does not. **Reconsider only if a future phase makes plan derivation depend on a wide numeric input** — e.g. arbitrary `write_region` tuples — where 2,031 enumerable cases become 2³² unenumerable ones. |
| Frozen fixtures + committed key list | **jsonschema 4.26.0** | If a third party outside this repo began producing `dev test` reports (a community fork, a different host tool). Then a published schema is the interop contract and worth its weight. Today the producer and the consumer are the same package. |
| Frozen fixtures + committed key list | **pydantic 2.13.5** | If report construction needed *runtime input validation* of untrusted data. It does not — the report is assembled from this program's own execution, and `pydantic` would be a **shipped runtime dependency** with a compiled `pydantic-core`, which is a materially larger ask than any test extra. Hard no. |
| Hand-picked allow-list hash | **`jcs` / RFC 8785 canonical JSON** | If the hash input were the document. Adopting it here would make every additive 1.8 field re-key every report — the exact opposite of the requirement. |
| Loop-and-collect assertion | **pytest-subtests 0.15.0** | If the 2,031 cases each needed independent pass/fail reporting in CI output. They do not — one failure message listing all offending chips is more useful and adds no dependency. |
| Element-wise committed comparison | **deepdiff 9.1.0** (33 requires-dist entries) | Never, for this. `json.dumps(..., sort_keys=True)` plus set difference produces a message that names the chip that moved, which is what a maintainer needs. |
| Element-wise committed comparison | **dirty-equals 0.11** | Marginal. Would make a few assertions terser; adds a dependency to save a helper function. Decline. |

## What NOT to Use

| Avoid | Why, specifically | Use instead |
|---|---|---|
| Any new entry in `[project].dependencies` | This package ships to end users on PyPI. Its runtime dependency set is six well-known libraries; every one of them is needed at runtime by the CLI. Nothing in v1.36 executes at user runtime that stdlib does not already cover. | stdlib `hashlib`, `json`, `dataclasses` |
| `hypothesis` | Samples a domain that enumerates in 4.22 s; makes reachability evidence probabilistic; introduces flake into a 737 s suite that runs on every branch push | exhaustive sweep + the 9-class census |
| `jsonschema` (and `fastjsonschema`) | Third redeclaration of a shape already declared twice; no interop boundary exists; `rpds-py` adds a compiled-extension surface this repo deliberately quarantines | frozen fixtures + a committed `to_dict()` key list |
| `pydantic` | Would be a **runtime** dependency with a compiled core, to validate data this program itself produced | the existing hand-written `to_dict()` |
| `jcs` / hashing `to_dict()` | Would make every additive 1.8 field re-key every historical fingerprint — the precise failure the milestone forbids | keep the hand-picked `parts` allow-list |
| Unbounded `syrupy>=5.0` | 6.0.0 changes dataclass serialization; every report structure is a dataclass; CI resolves it today | `syrupy>=5.0,<7` |
| `dataclasses.asdict()` wholesale in `to_dict()` | `diagnostic_report.py:771` names this "Pitfall 3" — it would leak every internal field into the wire shape automatically, which is how an unreviewed field reaches a stranger's GitHub issue | keep the hand-written dict |
| Dropping unsupported steps from `Plan.steps` | Re-keys the fingerprint for 637 of 677 chips (**proven**: `a00791f1c2b4` → `7d1cd4157cfa`) | keep the `StepResult`, skip only the work |
| Setting `ac.chip` to the canonical `part_number` | Re-keys essentially every historical fingerprint (**proven**: `a00791f1c2b4` → `a6f6c6354047`); 732/746 part numbers differ from their lowercase form | add `canonical_part_number` as a new field (R1) |
| Measuring anything in the devcontainer's default py3.12 | Proven in this project to hide breakage that reddens beta CI | `.venv/ci-replica/` (py3.11) |
| Relying on a `# noqa: BLE001` | `[tool.ruff.lint] select = ["E","F","I","UP"]` — `BLE` is not selected, so every such noqa in this tree is inert | catch the specific exception |

## Stack Patterns by Variant

**If a phase adds a new discriminator to `dedup_fingerprint`:**
- Follow `repeat_policy_tag` / `coverage_tag` exactly — compute it, append to `parts` **only when
  non-empty**, default to `""` for the pre-existing case.
- Because that is the only shape that leaves every already-filed fingerprint byte-identical, and both
  in-source comment blocks say so.

**If a phase removes an operation from a plan:**
- Keep the `StepResult` with an NA/skipped verdict; skip only the work.
- Because `parts` gains one entry per `StepResult`, and `run_plan` already records NA steps without an
  operator call.

**If a phase adds a report field:**
- Add it to `to_dict()` beside the existing keys, extend the committed key list, add nothing to
  `dedup_fingerprint`.
- Because the hash's input is an allow-list, so additive schema change is free by construction.

**If a phase snapshots report output:**
- Snapshot `report.to_dict()`, not the dataclass.
- Because syrupy 6.0.0 changed dataclass serialization and the pin is currently unbounded.

## Version Compatibility

| Package | Version | Compatible with | Notes |
|---|---|---|---|
| pytest 9.1.1 | current | syrupy ≥5.0 (needs pytest ≥8.0.0), pytest-cov 7.1.0 | No conflict. |
| syrupy 5.5.3 → 6.0.0 | **unbounded pin** | pytest ≥8.0.0 | **Action required.** 6.0.0 requires-python ≥3.10; CI runs 3.11, so the floor is fine — the *behaviour* is the problem. |
| mypy 2.3.1 | pinned `<3` | `python_version = "3.10"` | `chip_test` and `diagnostic_report` are in neither strict-island list; new code there is watermark-only. |
| ruff 0.16.4 | pinned `>=0.15.14` | `target-version = "py39"` | `tests/golden` and `tests/fixtures` are excluded; put no new gate input in `tests/golden` expecting it to be formatted. |
| CPython 3.11 (CI) vs 3.9 (`requires-python`) | divergent, deliberately | — | Nothing type-checks against the advertised 3.9 floor (backlog 999.26). Do not use a 3.10+ stdlib API in shipped code without checking. |
| hypothesis 6.167.1 | *not adopted* | requires-python ≥3.10 | Would be compatible; declined on merit, not compatibility. |
| jsonschema 4.26.0 | *not adopted* | requires-python ≥3.10 | Would be compatible; declined on merit. |

## Measurement Reproduction

```bash
cd /workspaces/firestarter_app
.venv/ci-replica/bin/python - <<'PY'
from firestarter.database import EpromDatabase
from firestarter.chip_test import derive_plan
import collections
db = EpromDatabase(skip_local_override=True)
names = sorted({r["part_number"] for _, rows in db.proms.items() for r in rows})
c = collections.Counter()
for nm in names:
    for sc in ("none", "full", "partial"):
        p = derive_plan(nm, db, write_scope=sc)
        c[(sc, tuple(s.op for s in p.steps), p.is_uv)] += 1
print(len(names), "chips ->", len(c), "classes")
PY
```

The two re-key proofs in §(c) are reproduced by constructing a `DiagnosticReport` with one
`StepResult` per plan step and calling `dedup_fingerprint` three times — once as-is, once with the
six NA SDP results removed, once with `chip="M27C512"`.

## Sources

**Primary — this tree, measured 2026-09-02 (confidence HIGH).** Every count, timing, hash and plan
shape above was produced by executing the code at `firestarter_app` @ `0a93999` in
`.venv/ci-replica/` (CPython 3.11), and transcribed verbatim. Files read: `pyproject.toml`,
`.github/workflows/ci.yml`, `firestarter/chip_test.py`, `firestarter/diagnostic_report.py`,
`firestarter/cli_handlers.py`, `tests/test_chip_test_sdp_leg.py`, `tests/test_diagnostic_report.py`,
`tests/test_parse_devtest_issue.py`, `tests/test_erase_flag_invariants.py`,
`tests/test_sdp_db_invariant.py`, `tools/check_diagnostic_report_claims.py`.

**Package versions — PyPI JSON registry API (`https://pypi.org/pypi/<name>/json`), queried
2026-09-02 (confidence HIGH).** The Context7 MCP server is **not available in this runtime** — no
`mcp__context7__*` tool is exposed — so the `research-plan` seam's `context7` route could not be
executed. PyPI's own registry API was used instead. For the specific question asked (*"verify current
versions"*) this is a **stronger** source than Context7: it is the canonical publisher of the version,
release date, `requires-python` and `requires-dist` metadata, not a documentation index of it. Values
transcribed: hypothesis 6.167.1 (2026-08-30), jsonschema 4.26.0 (2026-01-07), syrupy 6.0.0
(2026-08-22), pytest 9.1.1 (2026-06-19), pytest-subtests 0.15.0 (2025-10-20), dirty-equals 0.11
(2025-11-17), deepdiff 9.1.0 (2026-05-15), pydantic 2.13.5 (2026-08-28), fastjsonschema 2.22.2
(2026-08-15).

**syrupy 6.0.0 breaking changes** — `https://github.com/syrupy-project/syrupy/releases`, fetched
2026-09-02. Confidence **MEDIUM** (vendor release notes, single source; the *consequence* for this
repo — 32 snapshots, none dataclass-shaped — was verified locally and is HIGH).

**RFC 8785 / JCS canonical JSON** — `https://www.rfc-editor.org/info/rfc8785/`,
`https://datatracker.ietf.org/doc/html/rfc8785`, `https://pypi.org/project/jcs`. Confidence **LOW**
per the classify-confidence seam for a `websearch` provider; used only to establish that a standard
canonicalizer exists and to explain why it does not apply here — a conclusion that rests on the
locally-measured structure of `dedup_fingerprint`, not on the search.

**Confidence tiers** obtained from `gsd_run query classify-confidence`: `context7` → MEDIUM,
`websearch` → LOW, `webfetch` → LOW.

---
*Stack research for: v1.36 `dev test` Fidelity — host-app-only Python CLI change*
*Researched: 2026-09-02*
