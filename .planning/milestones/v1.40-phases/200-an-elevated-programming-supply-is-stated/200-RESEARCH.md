# Phase 200: An elevated programming supply is stated - Research

**Researched:** 2026-09-19
**Domain:** Python host CLI — display surface, logging mechanism, database census testing
**Confidence:** HIGH (every load-bearing claim measured against the live tree this session)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** **284 of 746 rows need more than 5.0 V to program.** Measured from the live
  `firestarter/data/chip_database.json` during this discussion, not estimated. `vdd_mv` histogram:
  3300 ×20, 5000 ×442, 5500 ×164, 6000 ×8, 6250 ×7, 6500 ×105. `vcc_mv` carries only three values
  (3300 ×18, 5000 ×700, 5500 ×28). Every one of the 284 is `support_status: supported`, spanning 34
  vendors and algorithms 7, 8 and 11. `vdd_mv > vcc_mv` selects 285 rows, of which 284 are also
  above 5000 — so "elevated" and "above the shield's rail" are the same set here, bar one row.
  **This number is the reason for D-02.** A condition that holds for 38% of the database cannot be
  surfaced the way a rare fault is, or it becomes noise and gets tuned out.

- **D-02:** **`info` only. NOT `write`.** `info` is the pre-flight surface — it is where someone
  checks a part before committing. Keeping `write` quiet is what preserves the meaning of the
  warnings `write` does emit. Operator decision, against the alternative of warning on both.
  **Accepted cost, recorded rather than hidden:** an operator who never runs `info` never sees it.
  VCC-01's "before the attempt" is satisfied by `info` being the surface that precedes the attempt,
  not by warning during it.
  — **Reversibility:** reversible — adding the same call at the `write` site later is a one-line
  change; nothing about this decision forecloses it.

- **D-03:** **The predicate is `vdd_mv > 5000`**, with 5000 a named constant standing for the
  shield's fixed supply, phrased as VCC-01 phrases it. Not `vdd_mv > vcc_mv` — the shield delivers a
  fixed rail regardless of what a row's `vcc_mv` says, and the 28 rows at `vcc_mv` 5500 are Phase
  198's D-11 set, deliberately untouched here.

- **D-04:** **A field row AND a warning line.** The row makes the decoded value visible where every
  other electrical value already lives; the warning names both numbers and states what will happen.
  The row alone is too easy to skim past on a 38%-common condition; the warning alone loses the value
  itself. This wording **establishes** the project's shortfall-statement shape — VCC-02 is satisfied
  by defining it, not by matching RAIL-03, which was adjudicated UNMET at the close of Phase 199.
  Shape agreed with the operator:

  ```
  VCC:                5.0v
  Programming VCC:    6.0v
  VPP:                12.5v

  WARNING: this part programs at 6.0 V; the shield supplies a fixed 5.0 V.
  Programming will be attempted at 5.0 V.
  ```

- **D-05:** **State and proceed; refuse nothing.** Milestone D-4 already settled this shape: the
  operation proceeds with a statement naming both numbers rather than refusing silently or attempting
  silently. All 284 rows are `supported` today and nothing measured says 5.0 V actually fails for
  them; refusing would strand 38% of the database on a value that was never applied before this phase
  either. **Nothing that works today stops working.**

- **D-06:** **Fail open.** An absent, null or zero `vdd_mv` produces no field row and no warning.
  Phase 199 established that absent evidence must never raise a warning; manufacturing one from
  missing data is worse than silence. A row whose `vdd_mv` is at or below 5000 likewise produces
  neither.

- **D-07:** **This is host-side work.** `vdd_mv` **does not cross the wire** — measured at
  `firestarter/database.py`, whose wire dict carries `vpp_mv` and `vcc_mv` only — so the firmware
  cannot know a part needs an elevated programming supply. Nor is there anything for it to do: the
  shield's VCC is fixed, so unlike the VPP shortfall there is no second rail to route to. Phase 199's
  D-21 moved a *routing decision* the firmware could already make from data it already held; this is
  neither, so the two decisions do not conflict. **Adding `vdd_mv` to the wire is out of scope** — it
  would be a protocol change across both repos in lockstep, and nothing in this phase needs it.

### Claude's Discretion

- Where exactly the field row sits in the `info` table, and the exact renderer used, so long as it
  matches the existing `VCC:` / `VPP:` row style and the snapshot moves only where expected.
- **Which mechanism carries the warning is genuinely open, because there is no precedent to follow.**
  Verified during this discussion: `info` has NO existing warning path. Support-status problems
  surface as a raised `ClickException` through the `map_typed_errors` decorator in
  `firestarter/cli_handlers.py` — that is a **refusal**, which D-05 forbids here. So this phase
  introduces the first advisory statement on `info`, and the planner picks `logger.warning` or
  `click.echo` on its merits. Note the Phase 199 precedent for the analogous choice: a warning meant
  to be visible at default verbosity went through `click.echo`, because `logger.warning` on a
  non-verbose run may not reach the operator. Confirm that against the live `info` path rather than
  inheriting it.
- Test structure, provided the 284-row count is asserted as an equality derived from the live
  database and not hand-transcribed, and provided the non-vacuity of that count is proved.

### Deferred Ideas (OUT OF SCOPE)

- **Warning on `write` as well as `info`.** Considered and declined for now (D-02). Revisit only with
  evidence about how operators actually use the two surfaces.
- **Tiering by how far above 5.0 V a part sits.** Needs a measurement that does not exist. If ever
  taken up, it needs a bench session, not a guess.
- **Putting `vdd_mv` on the wire** so the firmware could act on it. Out of scope; a protocol change
  in lockstep across both repos, and nothing here needs it.
- **Retrofitting RAIL-03** with this phase's wording once it exists. Explicitly left as a separate
  decision — a host-side VPP warning would require the host to carry the 17380 drop-path ceiling
  again, which is the stale-figure exposure D-21 moved away from. Milder for a warning than for
  routing, but not free.

#### Reviewed Todos (not folded)
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md` — firmware VPP concern,
  this phase is host-side VCC. Not folded.
- `2026-08-27-strip-gsd-provenance-comments-from-source.md` — **OBSOLETE.** The source-comment rule
  was removed outright on 2026-09-19. Flagged for retirement rather than folded.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **VCC-01** | A part that needs a programming VCC above the shield's fixed 5.0 V says so where the operator will see it, rather than carrying a decoded `vdd_mv` that nothing applies. | §B (the injection seam that reaches `vdd_mv` without touching `_map_data` or the wire dict), §C (the warning mechanism, empirically settled), §A-4 (`vdd_mv` is read by **zero** lines of product source today — "nothing applies it" is literally true) |
| **VCC-02** | That statement uses the same warning shape as RAIL-03, so one fact does not get two explanations. — **"same shape as RAIL-03" clause SUPERSEDED by the ROADMAP amendment.** RAIL-03 was adjudicated UNMET at the close of Phase 199; Phase 200 DEFINES the shape. | §D (the in-repo `WARNING: `-prefixed advisory shape that already exists on this exact surface and that the operator's D-04 wording independently matches), §G-1 (the one wording precision issue the planner must resolve before locking the shape) |

</phase_requirements>

## Summary

This phase is smaller in mechanism and larger in nuance than CONTEXT.md anticipated. Every number in
D-01 reproduced **exactly** against the live tree — 746 rows, the `vdd_mv` histogram to the unit, 284
above 5000, all 284 `supported`, 34 vendors, algorithms 7/8/11, and the 285-vs-284 `vdd_mv > vcc_mv`
discrepancy resolving to the single row `FUJITSU/MB85R256H`. D-01 needs no revision and the planner
can build on it directly.

Three CONTEXT.md claims did **not** survive contact with the tree, and all three make the phase
*easier*. First, **`info` already has a warning path** — two of them, in `eprom_info.py`, one of which
(`no_pinout_warning`) is a non-refusing advisory already rendered with the literal `WARNING: ` prefix
the operator's D-04 wording independently arrived at. CONTEXT.md's grep missed this because it
searched `eprom_presenter.py`, **a file that does not exist**; the renderer is `eprom_info.py`.
Second, the `ClickException` refusal CONTEXT.md cites cannot fire on `info` at all: `info` never calls
`resolve_chip`, which is the only raiser. Third, the Phase 199 rationale for preferring `click.echo`
— "`logger.warning` on a non-verbose run may not reach the operator" — is **false on this surface**,
measured by running the real CLI: `_setup_logging` sets the root logger to `INFO`, so `WARNING`
passes, lands on **stdout**, and renders with no level prefix. The `click.echo` precedent it refers to
lives on the `write` path and argues against `logger.info`, not `logger.warning`.

The single finding that should reach the operator before the wording is locked is a **semantic** one,
not a mechanical one. `DECODE-NOTES.md` § 9's standing verdict is that `vdd_mv` "select[s] a
programmer rail index, **not a chip requirement**", and it falsifies the chip-requirement reading by
arithmetic. Measured this session: of the 284 rows, exactly **3** carry a datasheet-grounded `vdd_mv`
(the three Fujitsu override entries); the other **281 carry a decoded rail-table slot**. CONTEXT.md's
own worked example, `FUJITSU/MBM27C1000P,MBM27C1000`, is one of the 281 — its 6000 mV is
`VCC_VOLTAGES[0x0D]`, not a datasheet figure. D-04's wording "this part **programs at** 6.0 V" states
the reading § 9 disproved, for 281 of 284 rows. This is a one-clause wording question, not a design
change, and §G-1 gives three resolutions.

**Primary recommendation:** Inject `vdd_mv` from `raw_config_data` inside
`EpromConsolePresenter.prepare_detailed_eprom_data`, mirroring the `support_status` block six lines
above it; render the row and the warning in `present_eprom_details` with `logger.warning`, using the
`pos = 20` alignment constant rather than a hardcoded pad; test the census with the
`test_vpp_rail_classification.py` template and the fail-open branch with synthetic in-memory rows,
because the live database has **no** row with an absent, null or zero `vdd_mv` to exercise it.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Decide a part's programming supply exceeds the rail | Host CLI (presentation) | — | The predicate's input (`vdd_mv`) exists only host-side; it is absent from the wire dict [VERIFIED: `firestarter/database.py:527-536`] |
| Render the `Programming VCC:` field row | Host CLI (presenter) | — | Every other electrical field row is emitted by `EpromConsolePresenter.present_eprom_details` [VERIFIED: `firestarter/eprom_info.py:231-252`] |
| Emit the shortfall warning | Host CLI (presenter) | — | Advisory text co-located with the row it qualifies; the file already owns two such blocks |
| Deliver 5.0 V to the socket | Shield hardware (fixed) | — | Not routable, not configurable; there is no second VCC rail (D-07) |
| Apply an elevated programming VCC | **Nobody** | — | This is the defect VCC-01 names: the value is decoded and then dropped. Confirmed — `vdd_mv` appears in **zero** lines of `firestarter/` product logic (§A-4) |
| Pin the rendered output | Host test suite (subprocess snapshot) | CliRunner in-process | `tests/test_characterization.py` runs the real entry point; §E measures which snapshots move |

**Tier sanity note for the planner:** there is no firmware tier in this phase. A task that edits
anything under `firestarter_fw/` is out of scope by D-07 and by the ROADMAP's scope facts.

## Project Constraints (from CLAUDE.md)

Both `/workspaces/CLAUDE.md` and `/workspaces/firestarter_app/CLAUDE.md` bind this phase.

| # | Directive | Source | Bearing on this phase |
|---|-----------|--------|----------------------|
| C-1 | **`chip_database.json` is GENERATED. Never hand-edit it.** A wrong value is a decode fault or a missing override, never a row to patch. | meta § Out of Scope; app § Key Files | This phase **reads** the DB only. No regeneration, no override edit. |
| C-2 | **CI runs Python 3.11.** A green run on the devcontainer's later interpreter does not prove a green CI run. | app § Development Commands | Verify on `.venv311` (measured present, Python 3.11.16) or `.venv/ci-replica`. |
| C-3 | CI order: `ruff check firestarter/ tests/` → `ruff format --check firestarter/ tests/` → `pytest tests/ --cov=firestarter --cov-fail-under=70`. | app § What CI runs | Every new/edited file must pass ruff check **and** ruff format. |
| C-4 | **`ruff` selection is `E`, `F`, `I`, `UP`, with `E501` ignored.** A `# noqa` code outside that selection is inert. | app § What CI runs | Do not add `# noqa: BLE001`-class suppressions; they are dead. |
| C-5 | **`mypy` is strict on ten modules** incl. `cli_handlers`. It is **not** a CI gate (pre-commit only). | app § What CI runs | `eprom_info.py` and `ic_layout.py` are **not** on the strict list — but `cli_handlers.py` is. Prefer keeping the change out of `cli_handlers.py`; §B's recommendation does. |
| C-6 | **A push to `beta` PUBLISHES to PyPI.** No path filter; a docs-only push publishes. | meta § Milestone close; app | Phase work stays on `v1.40-program-parameter-fidelity`. All three repos are already on that branch (verified). |
| C-7 | **Milestone work forks off `beta` in all three repos; never commit to `beta` or `main`.** | meta § Milestone close | — |
| C-8 | **`part_number` can hold several names in one comma-joined string.** An exact-string match misses rows; split before matching. | app § Database Pipeline | **This bit me during research** — see §A-5. Any test keying overrides to DB rows must comma-split. |
| C-9 | The source-comment prohibition is **RETIRED** (2026-09-19, all three repos). Comments in product source are allowed again. | meta § Repository Structure | Explanatory comments in `eprom_info.py` are permitted and match the file's dense existing style. |
| C-10 | `firestarter_app/tools/` is outside every CI gate (no ruff, no mypy). | app § What CI runs | Not relevant — this phase touches no `tools/` code. |
| C-11 | Constants duplicated between `constants.py` and three firmware headers must change in the same commit pair. | meta § Cross-repo obligations | **Not triggered.** The 5000 mV constant this phase introduces is host-only and has no firmware counterpart (D-07). Do not put it in `constants.py` for "symmetry"; that block is explicitly the firmware-mirror block. |

**Project skills:** no `.claude/skills/` or `.agents/skills/` directory exists in `/workspaces` or
`/workspaces/firestarter_app` [VERIFIED: filesystem check]. No project-skill patterns apply.

## Standard Stack

This phase adds **no dependencies**. Everything it needs is already installed and already used by the
files it touches.

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `logging` (stdlib) | — | Carries both the field row and the warning | Every line `present_eprom_details` emits already goes through it [VERIFIED: `firestarter/eprom_info.py:231-330`] |
| `click` | installed | CLI framework | Already the entry point; **not needed for this change** under §C's recommendation |
| `pytest` + `syrupy` | `syrupy>=5.0,<7` | Snapshot + unit tests | [VERIFIED: `pyproject.toml:71`] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `json`, `pathlib`, `collections`, `copy` (stdlib) | — | Census test: load DB, histogram, deep-copy mutation | The exact import set `test_vpp_rail_classification.py` uses [VERIFIED: `tests/test_vpp_rail_classification.py:90-93`] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `logger.warning` in `eprom_info.py` | `click.echo` | Introduces a `click` import into a presentation module that currently has none, and **loses** the CliRunner separability §C-3 measured. Rejected. |
| Injecting via `raw_config_data` | Adding `vdd_mv` to `_map_data` | Touches the dict that feeds `convert_to_programmer`, putting the wire-dict equivalence suite at risk for zero benefit. Rejected — see §B-2. |

**Installation:** none. No `pip install` step belongs in this phase's plan.

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.**

The Package Legitimacy Gate was not run because there is nothing to run it against: the change is
confined to `firestarter/eprom_info.py`, `tests/`, and `.planning/`, using only the standard library
and already-pinned dev dependencies declared in `pyproject.toml`. No `npm install`, `pip install`, or
`cargo add` step appears in any recommended task.

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram — the `info` data flow

```
  operator: `firestarter info MBM27C1000`
        │
        ▼
  cli_handlers.cli()  ── -v absent ──▶ _setup_logging(verbose=False)
        │                                  root.setLevel(INFO)
        │                                  handlers = [SingleLineStatusHandler → sys.stdout]
        │                                  formatter = "%(message)s"   ◀── no level prefix
        ▼
  cli_handlers.info()                             [cli_handlers.py:472-503]
        │
        ├── db.get_eprom(name) ──▶ _map_data() ──▶ eprom_details
        │        └─ carries vpp_mv, vcc_mv, pulse-delay …  ✗ NOT vdd_mv
        │
        ├── db.convert_to_programmer(eprom_details) ──▶ wire dict
        │        └─ explicit allow-list: vpp_mv only       ✗ NOT vdd_mv   (D-07 confirmed)
        │
        └── db.get_eprom_config(name) ──▶ raw_config_data
                 └─ the RAW DB record: electrical.vdd_mv IS HERE  ◀══ THE SEAM
                          │
                          ▼
        EpromConsolePresenter.prepare_detailed_eprom_data(…)   [eprom_info.py:95-176]
                 │   existing precedent: support_status injected from raw_config_data,
                 │   gated so a "supported" chip gets no new key          [:138-147]
                 │   ══▶ ADD the vdd_mv injection here, same gate shape
                 ▼
                combined_data ──▶ present_eprom_details(…)     [eprom_info.py:214-330]
                                        │  pos = 20
                                        │  logger.info  → Name/VCC/VPP/Pulse delay rows
                                        │  logger.warning → Support status / Reason   [:241-245]
                                        │  logger.warning → "WARNING: No pinout…"     [:261-266]
                                        │  ══▶ ADD "Programming VCC:" row + WARNING block
                                        ▼
                                   sys.stdout  (stderr stays empty — snapshots pin '')
```

### Pattern 1: Inject from `raw_config_data`, gated so the common case adds no key

**What:** `prepare_detailed_eprom_data` receives both the mapped `eprom_details` and the **raw** DB
record. Fields that `_map_data` drops are reachable from the raw record, and the file already does
exactly this for `support_status`.
**When to use:** any field the display needs that `_map_data` does not carry — which is this phase's
whole situation.
**Why it matters here:** the gate is the mechanism that makes D-06 fail-open structural rather than
remembered, and it is the same gate that keeps the 462 at-or-below-5000 rows snapshot-stable.

```python
# Source: firestarter/eprom_info.py:138-147 — VERBATIM, the precedent to mirror
        # Inject support_status + unsupported_reason into combined_data for
        # non-supported chips. Gated on support_status != "supported"
        # so supported chips get no new line, which would be a snapshot regression.
        if raw_config_data:
            ss = raw_config_data.get("support_status", "supported")
            if ss != "supported":
                combined_data["support_status"] = ss
                combined_data["unsupported_reason"] = raw_config_data.get(
                    "unsupported_reason", ""
                )
```

The comment's own reasoning — *"so supported chips get no new line, which would be a snapshot
regression"* — is the identical argument for gating on `vdd_mv > 5000`.

### Pattern 2: The aligned field row uses a single `pos` constant

**What:** every aligned row in `present_eprom_details` is an f-string using the module-local
`pos = 20`. The width is **computed from one variable, not hard-coded per row** — so adding a row
costs nothing in alignment maintenance, provided you use `pos`.

```python
# Source: firestarter/eprom_info.py:230-252 — VERBATIM excerpt
        pos = 20  # For alignment
        logger.info(f"{'Eprom Info': <{pos}}{chip_data.get('verified_str', '')}")
        logger.info(f"{'Name:': <{pos}}{chip_data.get('name')}")
        ...
        logger.info(f"{'VCC:': <{pos}}{chip_data.get('vcc_str')}")
        if "vpp_str" in chip_data:
            logger.info(f"{'VPP:': <{pos}}{chip_data.get('vpp_str')}")
        if "chip_id_hex" in chip_data:
            logger.info(f"{'Chip ID:': <{pos}}{chip_data.get('chip_id_hex')}")
        if "pulse_delay_us_str" in chip_data:
            logger.info(
                f"{'Pulse delay:': <{pos}}{chip_data.get('pulse_delay_us_str')}"
            )
```

`'Programming VCC:'` is 16 characters, comfortably inside `pos = 20`, so the row aligns with no
change to the constant.

### Pattern 3: Voltage strings always go through `format_mv`

Never format millivolts inline. `format_mv` is the single source of the `6.0v` rendering and its
docstring explicitly names the display call sites it exists to keep consistent.

```python
# Source: firestarter/database.py:115-122 (signature + docstring reference)
def format_mv(mv: int) -> str:
    # one-decimal lowercase-v format: f"{mv / 1000:.1f}v"
    # call sites: ic_layout.py's vcc_str/vpp_str and eprom_info.py's vpp_str
```

`eprom_info.py` **already imports it**: `from firestarter.database import EpromDatabase, format_mv`
[VERIFIED: `firestarter/eprom_info.py:15`]. No new import is needed for the field row.

Note the warning line in D-04 reads `6.0 V` (space, capital V) while the field row reads `6.0v`
(`format_mv`'s format). That asymmetry is in the operator-agreed wording and is presumably
deliberate — prose versus table cell. Flag it for confirmation rather than silently normalising.

### Anti-Patterns to Avoid

- **Hardcoding the row's pad instead of using `pos`.** The two existing warning rows do this and are
  **misaligned by one column** as a result: `"Support status:      "` is 15 characters plus 6 spaces
  = 21, where every `pos`-formatted row puts its value at column 21 (0-indexed 20). Verified in live
  output — the `Support status:` value starts one column right of `Name:`. Do not copy that bug into
  the new row. (Fixing the existing two is **out of scope**: it would move the snapshot for reasons
  unrelated to VCC-01.)
- **Adding `vdd_mv` to `_map_data`.** It works — `convert_to_programmer` builds an explicit
  allow-list so nothing would leak onto the wire [VERIFIED: `firestarter/database.py:527-536`] — but
  it puts `tests/test_wire_dict_equivalence.py` and the `_map_data` direct-indexing contract in the
  blast radius for no gain.
- **Reading `raw_config_data["electrical"]["vdd_mv"]` with direct indexing.** `_map_data` uses direct
  indexing deliberately for `vcc_mv`/`vpp_mv` so a stale user override fails loudly. That argument
  does **not** transfer: D-06 mandates fail-open, and §F-2 shows the user-override database is a real
  source of records lacking the key. Use chained `.get()`.
- **Putting the 5000 mV constant in `constants.py`.** That module is the firmware-mirror block
  (C-11). This constant has no firmware counterpart.
- **Regenerating the whole snapshot file.** See §E.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Rendering mV as `6.0v` | An inline f-string | `format_mv` (already imported) | Its docstring exists specifically to stop the call sites diverging [VERIFIED: `database.py:115-122`] |
| Aligning the new field row | A new pad literal | the existing `pos = 20` | The two hardcoded-pad rows in the same function are already one column out |
| Making the warning visible at default verbosity | `click.echo`, a `print`, a second handler | `logger.warning` | Measured to reach stdout on a default run (§C-1). The problem the alternative solves does not exist here. |
| Proving the 284 count non-vacuously | A bespoke assertion style | the `test_vpp_rail_classification.py` template | It ships census + boundary + three planted-mutation legs + a source-shape guard, all reviewed and green (§H) |
| Exercising the fail-open branch | Editing `chip_database.json` | synthetic in-memory dicts | C-1 forbids hand-editing the DB, **and** there is no qualifying row to find (§F-1) |
| Matching an override key to a DB row | `f"{mfg}/{chip['part_number']}"` | comma-split the part number first | C-8; this exact bug produced a wrong intermediate result during this research (§A-5) |

**Key insight:** the expensive failure mode in this phase is not writing the wrong code — the change
is perhaps twenty lines. It is asserting the wrong *claim*. Three of CONTEXT.md's framing statements
were measurably wrong (§G), and the wording in D-04 states something § 9 of the project's own decode
notes explicitly falsified for 281 of the 284 rows (§G-1). Spend the plan's care on the sentence, not
the mechanism.

---

## Findings

### A. The measurement — D-01 reproduced exactly

Run against `/workspaces/firestarter_app/firestarter/data/chip_database.json` on branch
`v1.40-program-parameter-fidelity` with `.venv311` (Python 3.11.16).

**A-1. Totals and histograms — every D-01 figure confirmed to the unit.**
[VERIFIED: live database, measured this session]

| Claim (CONTEXT.md D-01) | Measured | Agrees |
|---|---|---|
| 746 rows total | `746` | ✅ |
| `vdd_mv` histogram `3300×20, 5000×442, 5500×164, 6000×8, 6250×7, 6500×105` | `{3300: 20, 5000: 442, 5500: 164, 6000: 8, 6250: 7, 6500: 105}` | ✅ exact |
| `vcc_mv` three values `3300×18, 5000×700, 5500×28` | `{3300: 18, 5000: 700, 5500: 28}` | ✅ exact |
| `vdd_mv > 5000` selects 284 | `284` | ✅ |
| all 284 `support_status: supported` | `{'supported': 284}` | ✅ |
| 34 vendors | `34` | ✅ |
| algorithms 7, 8 and 11 | `{7: 161, 8: 102, 11: 21}` | ✅ (per-algorithm split is new) |
| `vdd_mv > vcc_mv` selects 285, one of which is ≤5000 | `285`; the odd row is `FUJITSU/MB85R256H` (`vdd_mv` 5000, `vcc_mv` 3300) | ✅ — and the row is now **named** |

**A-2. Two invariants D-01 did not record, both useful as census assertions.**
[VERIFIED: live database, measured this session]

- **All 284 rows are `electrical.type == "UV-EPROM"`.** Not one EEPROM, Flash/EEPROM, SRAM or FRAM.
  A clean, strongly-typed invariant: the elevated programming supply is, in this database, purely a
  UV-EPROM phenomenon. A census test asserting `{"UV-EPROM": 284}` would catch a decode change that
  swept a 5 V EEPROM into the warned set — a class of regression nothing else here would notice.
- **Pinout spread across nine keys:** `DIP32_27C020: 69`, `DIP28_27256: 62`, `DIP28_2764: 57`,
  `DIP28_27512: 42`, `DIP32_STD: 25`, `DIP24_2732: 11`, `DIP24_2716: 9`, `DIP32_27C801: 8`,
  `DIP24_2532: 1`.

**A-3. The VOLT-03 28-row set is fully disjoint from the 284 — overlap is zero.**
[VERIFIED: live database, measured this session] The 28 rows at `vcc_mv == 5500` carry
`vdd_mv` of `{3300: 16, 5000: 12}`, every one of them at or below 5000. D-03's concern that the
predicate must not disturb Phase 198's D-11 set is **structurally satisfied**, not merely intended.
Worth an explicit test leg: it is the assertion that would catch a future decode change quietly
pulling that group into the warned set.

**A-4. `vdd_mv` is read by ZERO lines of product logic.** A full `/usr/bin/grep` over
`firestarter/*.py` for `vdd` returns exactly one hit, and it is cosmetic:

```python
# firestarter/eprom_info.py:90
            cleaned["voltages"].pop("vdd", None)  # Remove 'vdd' if present
```

— and that touches the legacy string-schema `voltages.vdd` key in the `-c` export cleaner, not
`electrical.vdd_mv`. Every other `vdd` reference in the repository is in `tools/build_db.py`, which
*produces* the field. **VCC-01's "carrying a decoded `vdd_mv` that nothing applies" is therefore
literally, not rhetorically, true** — and the planner can cite this grep as the phase's baseline.

**A-5. Method warning, learned the hard way.** My first override-coverage measurement keyed
`f"{mfg}/{chip['part_number']}"` against `datasheet_overrides.json` and reported
`FUJITSU/MBM27C1000` as unmatched — because the DB row's `part_number` is the comma-joined
`"MBM27C1000P,MBM27C1000"`. This is exactly the trap `firestarter_app/CLAUDE.md` § Database Pipeline
warns about (C-8). The corrected, comma-split measurement is what §G-1 reports. Any plan task that
joins override keys to database rows must split first.

### B. Where the field row goes — the seam, named and costed

**B-1. The renderer.** `EpromConsolePresenter.present_eprom_details`, in
`/workspaces/firestarter_app/firestarter/eprom_info.py`, lines 214-330. The aligned field block is
lines 230-252. The construct is a flat sequence of `logger.info(f"{'Label:': <{pos}}{value}")`
calls with a single module-local `pos = 20`, several of them guarded by `if "<key>" in chip_data:`.

**Cost of inserting one more row:**
- **Alignment width:** zero cost. `pos = 20` is a single variable; `'Programming VCC:'` is 16
  characters and fits. **But** note the anti-pattern above — the two `logger.warning` rows in the
  same function hardcode their pad and are one column out. Use `pos`.
- **Ordering:** free. The operator's D-04 mock-up places it between `VCC:` and `VPP:`, which is a
  three-line insertion at `eprom_info.py:248`, immediately after the `VCC:` row and before the
  `if "vpp_str" in chip_data:` guard. Nothing downstream reads position.
- **Hard-coded widths:** none in this function. (The *list* view, `print_eprom_list_table`, does have
  fixed column widths and a dynamic-name clamp — but this phase does not touch the list view, and
  the list view has no VCC column at all.)

**B-2. The data seam — and why it is not `_map_data`.** `present_eprom_details` renders
`combined_data`, built by `prepare_detailed_eprom_data` from `build_specifications(eprom_details)`.
`eprom_details` comes from `_map_data`, whose output dict is an explicit key list that **does not
include `vdd_mv`** [VERIFIED: `firestarter/database.py:380-395`]. So `build_specifications` cannot
see the field.

But `prepare_detailed_eprom_data` also receives `raw_config_data` — the raw DB record, complete with
`electrical.vdd_mv` — supplied by the `info` handler via `app.db.get_eprom_config(eprom)`
[VERIFIED: `firestarter/cli_handlers.py:486`]. **That is the seam**, and the file already uses it for
exactly this purpose six lines from where the new code goes (Pattern 1).

Adding `vdd_mv` to `_map_data` is the alternative. It would be safe on the wire —
`convert_to_programmer` builds an explicit allow-list of six keys plus three conditional ones
[VERIFIED: `firestarter/database.py:527-551`], so a new `_map_data` key cannot leak into the JSON
command — but it enlarges the blast radius to the wire-dict equivalence suite and the `_map_data`
direct-indexing contract for no benefit. **Recommend the `raw_config_data` route.**

**B-3. mypy exposure is zero.** `eprom_info.py` and `ic_layout.py` are **not** on the ten-module
strict list in `pyproject.toml`; `cli_handlers.py` is (C-5). The recommended change touches neither
`cli_handlers.py` nor `database.py`, so it faces no `disallow_untyped_defs` requirement — though
`mypy` is pre-commit-only regardless.

### C. The warning mechanism — CONTEXT.md's open question, settled by measurement

**C-1. `logger.warning` reaches the operator at default verbosity. Measured, not reasoned.**

`_setup_logging(verbose=False)` sets the **root** logger to `INFO`, installs a single
`SingleLineStatusHandler` writing to **`sys.stdout`**, and formats with a bare `"%(message)s"` —
no level prefix [VERIFIED: `firestarter/cli_handlers.py:103-123`; `firestarter/logging_utils.py:25-27`].
`WARNING` is 30, `INFO` is 20, so warnings pass the level gate by construction.

Confirmed by running the real installed entry point (which resolves to this working tree —
`/usr/local/bin/python3.12 -c "import firestarter; print(firestarter.__file__)"` →
`/workspaces/firestarter_app/firestarter/__init__.py`, i.e. the editable install is live):

```
$ firestarter info AT28C04            # default verbosity, no -v
Eprom Info
Name:               AT28C04,AT28HC04
Manufacturer:       ATMEL
Support status:      adapter-required
Reason:              adapter required: requires a dedicated DIP24 EEPROM adapter …
Number of pins:     24
...
$ firestarter info AT28C04 2>&1 >/dev/null     # stderr
(empty)
```

The `Support status:` and `Reason:` lines are `logger.warning` calls
[VERIFIED: `firestarter/eprom_info.py:241,244`]. They appear, on **stdout**, with no `-v`, with no
`WARNING` level prefix. **The Phase 199 rationale CONTEXT.md asks me to check — "`logger.warning` on
a non-verbose run may not reach the operator" — is false on this surface.**

**C-2. What the Phase 199 / 197 `click.echo` precedent actually says.** The in-repo comment is on the
`write` path, not `info`:

```python
# Source: firestarter/cli_handlers.py:666-670 — VERBATIM
    # can co-fire with either on the same chip. click.echo (never logger.info):
    # this must be visible at DEFAULT verbosity, with no -v needed. Reason:
    # a bench artifact or log captured without the command line beside it
    # cannot otherwise tell you the pulse was not the database's -- and
    # this evidence will be read by strangers.
```

It argues `click.echo` over **`logger.info`**, for a `--pulse-us` provenance line on `write`. It says
nothing about `logger.warning`, and it is not on this surface. CONTEXT.md's paraphrase generalised it
one step too far. There are 10 `click.echo` call sites in `firestarter/`, **all of them in
`cli_handlers.py`** [VERIFIED: grep]; `eprom_info.py` imports `json`, `logging` and `re` and has no
`click` import at all.

**C-3. The decisive argument is testability, and it favours `logger.warning`.** Measured this session
with an in-process `CliRunner` invocation passing `obj=app` (the pattern
`tests/test_cli_handlers.py` uses): because the `cli` group short-circuits before `_setup_logging`
when `ctx.obj` is already an `AppContext` [VERIFIED: `firestarter/cli_handlers.py:437-442`], the root
logger keeps pytest's default level of `WARNING`. Result:

```
exit: 0
output len: 242
has 'Support status' in output: True
first 300 chars: 'Support status:      adapter-required\nReason:  …'
```

**Only the `logger.warning` lines appear. Every `logger.info` field row is filtered out.** That is a
gift: a CliRunner test can assert the shortfall warning fires, on the exact chip, with no field-row
noise in the assertion — and the same test proves the warning survives even when `_setup_logging`
never ran. `click.echo` would appear in both contexts and be inseparable from the info rows in the
subprocess snapshot.

**C-4. Recommendation — `logger.warning`, in `eprom_info.py`.** It reaches the operator at default
verbosity (measured), it is the mechanism every other line on this surface already uses, it requires
no new import, it keeps the change out of the mypy-strict `cli_handlers.py`, and it buys a clean
in-process assertion seam. The `click.echo` precedent does not apply here and its stated premise does
not hold here.

One open sub-question for the planner: the **field row** (`Programming VCC:`) is a field row, not a
warning. Emitting it via `logger.info` keeps it consistent with `VCC:` and `VPP:` — but then it is
invisible under CliRunner while the warning is visible. Emitting it via `logger.warning` makes both
CliRunner-visible and both stdout-visible, at the cost of one field row being nominally
"warning-level". **Recommend `logger.info` for the row and `logger.warning` for the warning block**:
the subprocess snapshot pins the row (§E), so the row does not need CliRunner visibility, and
semantic honesty in the log level is worth more than assertion convenience.

### D. The shape VCC-02 must define — and the in-repo precedent it already matches

RAIL-03 is correctly out as a template: Phase 199 adjudicated it UNMET and recorded why
[VERIFIED: `199-05-SUMMARY.md:204-218`, § "RAIL-03: why it stays Pending"], the verifier concurred,
and `DECODE-NOTES.md` § 10 names the gap as a standing limit
[VERIFIED: `tools/DECODE-NOTES.md:710-715`, "The shortfall warning gap"].

But the project is **not** without a shape. `eprom_info.py` already carries a non-refusing, advisory,
`WARNING: `-prefixed block on this exact surface:

```python
# Source: firestarter/eprom_info.py:260-267 — VERBATIM
        if chip_data.get("no_pinout_warning"):
            logger.warning("")
            logger.warning(
                "WARNING: No pinout defined for this chip — hardware operations will fail."  # noqa: E501
            )
            logger.warning(
                "Add a pin-map entry to ~/.firestarter/pin-maps.json to enable it."
            )
```

Its shape is: **a blank line, then a `WARNING: `-prefixed statement of the condition and its
consequence, then a follow-on line stating what happens next.** The operator's D-04 wording is
structurally identical — blank line, `WARNING: this part programs at 6.0 V; the shield supplies a
fixed 5.0 V.`, then `Programming will be attempted at 5.0 V.`

This is a **strengthening** finding for VCC-02, and the planner should use it: the shape Phase 200
"defines" is not invented from nothing, it is the generalisation of a pattern this file already
uses — which is a far better warrant for "one fact does not get two explanations" than a shape with
no in-repo instance. Note the leading `logger.warning("")` for the blank separator line; copy it.

### E. Snapshot discipline — the measured blast radius is smaller than CONTEXT.md assumed

**E-1. How many entries move: ZERO of the existing ones.**
`tests/__snapshots__/test_characterization.ambr` is 1333 lines with 32 snapshot entries
[VERIFIED: `wc -l`; baseline run reports "32 snapshots passed"]. Exactly **two** render the `info`
surface — `test_info_known_chip` (W27C512) and `test_info_at28c256` (AT28C256) — plus their two
`_stderr` companions, which are both `''`.

Measured: **both of those chips have `vdd_mv == 5000`.**

| Snapshot | Chip | `electrical` |
|---|---|---|
| `test_info_known_chip` | `WINBOND / W27C512,W27E512` | `vcc_mv: 5000, vdd_mv: 5000, vpp_mv: 12000` |
| `test_info_at28c256` | `ATMEL / AT28C256,…` | `vcc_mv: 5000, vdd_mv: 5000, vpp_mv: 12000` |

Under D-03 (`vdd_mv > 5000`) and D-06 (fail open), **neither emits a row and neither emits a warning.
Both existing `info` snapshots are byte-unchanged.** The other snapshot entries are `--help` text,
error paths, `test_list` and `test_search_w27` — none of which renders a VCC column at all.

**So the snapshot change in this phase is purely ADDITIVE**: a new `test_info_<part>` entry for an
above-5.0 V part. `git diff --numstat` on the `.ambr` should therefore show **insertions only, zero
deletions** — a *stronger* and simpler gate than Phase 199's `1 1`. A non-zero deletion count means
something unexpected moved and the plan should fail closed on it.

**E-2. The proven Phase 199 scoped re-record sequence, verbatim.**
[VERIFIED: `.planning/phases/199-what-the-rails-can-actually-deliver/199-01-PLAN.md:203`]

```bash
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest \
  "tests/test_characterization.py::test_list" -o addopts="" -q -p no:randomly \
  --snapshot-update >/dev/null 2>&1; \
  NS=$(git diff --numstat -- tests/__snapshots__/test_characterization.ambr) && \
  printf '%s\n' "$NS" && printf '%s\n' "$NS" | /usr/bin/grep -qP '^1\t1\t'
```

Its `<fails_when>`, also verbatim and worth reusing in spirit: *"zero lines means the snapshot needed
no re-recording, so the rendered voltage never moved… and more than one line-pair means a blanket
update swept in unrelated drift. This leg is deliberately range-free because it is about the
UNCOMMITTED working tree immediately after the re-record; it must run before the commit, and it
reports zero lines if run after."*

Mechanical notes for reuse:
- `.venv/ci-replica/bin/python` **exists** [VERIFIED: `ls -d .venv/ci-replica`]. `.venv311` (Python
  3.11.16) also exists and is the C-2-compliant interpreter. Either works; `.venv/ci-replica` is what
  199 used.
- `-o addopts=""` is required: `pyproject.toml:97` sets `addopts = "-ra -q"`, and adding a second
  `-q` suppresses the count line.
- `-p no:randomly` is defensive; no `pytest-randomly` config was found in `conftest.py`.
- `run_firestarter` invokes `shutil.which("firestarter")`, **the entry point on PATH** — not the venv
  python [VERIFIED: `tests/test_characterization.py:125-145`]. Verified this session that PATH's
  `firestarter` imports from `/workspaces/firestarter_app/firestarter/__init__.py`, so an editable
  source edit is picked up without reinstalling. A plan leg should assert this rather than assume it
  (the sibling-worktree editable-install trap is a known hazard in this project).

**E-3. Baseline is green.** `pytest tests/test_characterization.py -o addopts="" -q` on `.venv311`:
`36 passed`, `32 snapshots passed`, 9.57 s. Re-run before and after to attribute any movement.

### F. Fail-open coverage — the branch has no live data, and that is the finding

**F-1. Not one row in the live database has an absent, null or zero `vdd_mv`.**
[VERIFIED: live database, measured this session]

| Condition | Rows |
|---|---|
| `electrical.vdd_mv` key absent | **0** |
| value is `null` | **0** |
| value is `0` | **0** |
| value is not an `int` | **0** |
| **present as a non-zero int** | **746 / 746** |

`build_db.py` guarantees this by construction: `_d_vdd_mv = VCC_VOLTAGES.get((voltages >> 12) & 0x0F,
5000)` — a `.get` with a **5000 default**, so every row gets a non-zero integer
[VERIFIED: `tools/build_db.py:687`].

**D-06's fail-open branch is therefore unreachable from the shipped database.** The planner must not
plan a test that "finds a row with no `vdd_mv`" — there is none, and C-1 forbids creating one by
hand-editing the DB. **Test it with synthetic in-memory dicts**, which is exactly what the Phase 199
template already does for its boundary and non-vacuity legs
[VERIFIED: `tests/test_vpp_rail_classification.py:246-282`, `test_boundary_is_at_or_above_not_strictly_above`].
Cover at minimum: key absent, `None`, `0`, exactly `5000`, and `5001`.

**F-2. The fail-open branch is nonetheless live in production, via user overrides.** It is not dead
code defended for its own sake. `EpromDatabase` merges `~/.firestarter/database.json` on top of the
packaged DB unless `skip_local_override=True`
[VERIFIED: `firestarter/database.py:152-182`], and `_map_data`'s own comment names *"a stale
string-schema `~/.firestarter/database.json` override missing `vcc_mv`/`vpp_mv`/`pulse_duration_us`"*
as a real, anticipated case [VERIFIED: `firestarter/database.py:375-379`]. A user-supplied record
carrying no `electrical.vdd_mv` is the concrete scenario D-06 protects. Worth one sentence in the
plan's rationale so a reviewer does not read the branch as speculative.

**F-3. Consequence for the predicate's code shape.** Because the key can be absent in the override
case, read it defensively and coerce — the same defensive `int()` shape `build_specifications` uses
for `vpp_mv` [VERIFIED: `firestarter/ic_layout.py:570-573`]:

```python
try:
    _vdd_mv = int((raw_config_data.get("electrical") or {}).get("vdd_mv", 0) or 0)
except (TypeError, ValueError):
    _vdd_mv = 0
if _vdd_mv > _SHIELD_FIXED_VCC_MV:      # 5000
    ...
```

The `or 0` handles `None`; the `try/except` handles a string override; `> 5000` handles zero and the
at-or-below case in one comparison. All four D-06 cases collapse into one guard.

### G. Where the live tree disagrees with CONTEXT.md

Four disagreements. Three make the phase easier. One needs an operator decision.

**G-1. ⚠️ THE ONE THAT NEEDS A DECISION: D-04's wording states the reading § 9 falsified, for 281 of
284 rows.**

`DECODE-NOTES.md` § 9's heading is its verdict:

> **"## 9. The voltage word's two nibbles and VPP byte (VOLT-01, Phase 198 — the two nibbles and the
> VPP byte select a programmer rail index, not a chip requirement)"**
> **"Verdict: the voltage word's two nibbles and the VPP byte select a programmer rail index, not a
> chip requirement.** The value a row's `voltages` field decodes to names which slot in the connected
> programmer model's internal DAC table drives that pin — not a transcription of the part's own
> datasheet figure."
> [VERIFIED: `firestarter_app/tools/DECODE-NOTES.md:371-377`]

§ 9 goes on to falsify the chip-requirement reading three ways: the same index means different volts
on different programmer models; upstream's own comment says the values are *"indices into internal
lookup tables"*; and the arithmetic argument — the three Fujitsu datasheets' band is 5.75–6.25 V
while the two nearest rails are 5.5 V and 6.5 V, so *"a field that cannot represent the datasheet
value is not recording the datasheet value."*

Measured this session, with comma-split key matching (§A-5), against
`tools/datasheet_overrides.json`:

| Of the 284 rows above 5000 mV | Count |
|---|---|
| `electrical.vdd_mv` set by a **datasheet-cited** override | **3** — `FUJITSU/MBM27128`, `FUJITSU/MBM27C1001`, `FUJITSU/MBM27C4001`, all `5500 → 6000`, each citing a vendored PDF |
| `vdd_mv` is a **pure decode** — a `VCC_VOLTAGES` rail-table slot | **281** |

There are 15 override entries touching `electrical.vdd_mv` in total; 12 are `"datasheet":
"UNSOURCED"` (the 1800 mV carve-out, all setting `vdd_mv` to 5000 and therefore **outside** the 284).

**CONTEXT.md's own worked example is one of the 281.** `FUJITSU/MBM27C1000P,MBM27C1000` carries
`vdd_mv: 6000`, but its `datasheet_overrides.json` entry touches only
`programming.pulse_duration_us` (`100 → 500`, citing `datasheets/MBM27C1000.pdf`). Its 6000 mV is
`VCC_VOLTAGES[0x0D] = 6000` [VERIFIED: `tools/build_db.py:129`] — a rail slot, not a datasheet figure.

So D-04's `WARNING: this part programs at 6.0 V` would, on the very part chosen to illustrate it,
assert as the part's requirement a number § 9 established is the programmer model's rail selection.
It is also **directionally unsafe in the understating direction**: § 9 showed the true Fujitsu
requirement (6.0 V ± 0.25 V) sat *above* the 5500 the decode gave, which is why the override exists.
The 164 rows rendering "programs at 5.5 V" may be understating their parts' real needs, and nothing
measured says by how much.

This does not change the design — the row, the warning, the predicate and the 284 set all stand. It
is one clause. Three resolutions for the operator, cheapest first:

1. **Hedge the verb.** `WARNING: this part's programming supply decodes to 6.0 V; the shield supplies
   a fixed 5.0 V. Programming will be attempted at 5.0 V.` One word changed ("programs at" →
   "decodes to"); claims exactly what is known; consistent with § 9; costs nothing.
2. **Keep D-04 verbatim and record the limit.** Ship the operator's wording unchanged and name the
   overstatement as a limit in the phase record, the way § 10 names the shortfall-warning gap. Honest
   in the archive, but the 281 operators reading the CLI still see the stronger claim.
3. **Distinguish the 3 from the 281 in the wording.** Maximally accurate, but it needs a
   provenance channel from the DB to the display that does not exist — and that channel is already
   filed as a deferred future requirement, **OVR-F1** [VERIFIED: `.planning/REQUIREMENTS.md`, Future
   Requirements table]. Out of scope; noted so the planner does not reinvent it.

**Recommend option 1**, and flag it to the operator as a `checkpoint:human-verify` in the plan — the
wording is a locked D-04 decision and only the operator can amend it.

**G-2. ✅ `info` DOES have a warning path. CONTEXT.md's grep searched a file that does not exist.**
CONTEXT.md: *"Measured: `grep support_status` across `cli_handlers.py` and `eprom_presenter.py`
returns one hit, a comment in the `ChipNotImplementedError` arm of `map_typed_errors`."*
There is no `eprom_presenter.py` in `firestarter/` [VERIFIED: directory listing] — the renderer is
`eprom_info.py`, and the attribute is `app.eprom_presenter`, which is presumably where the name came
from. A correct grep returns **six** hits in `eprom_info.py`, including the two `logger.warning`
calls at lines 241 and 244. There are **two** existing advisory warning blocks on this surface
(support-status and `no_pinout_warning`), the second of which is the shape template (§D).

**G-3. ✅ The `ClickException` refusal cannot fire on `info` at all.** `ChipNotImplementedError` is
raised only by `chip_resolver.resolve_chip` [VERIFIED: `firestarter/chip_resolver.py:53-55`], and the
`info` handler never calls it — it goes `db.get_eprom` → `db.convert_to_programmer` →
`db.get_eprom_config` → presenter [VERIFIED: `firestarter/cli_handlers.py:478-503`]. Demonstrated
live: `firestarter info AT28C04` on an `adapter-required` chip exits **0** and prints the full info
block with a warning. The tension CONTEXT.md perceived between the existing handling and D-05 does
not exist; `info` already states-and-proceeds.

**G-4. ✅ `vdd_mv` is absent from the wire dict — confirmed, and it is stronger than stated.** D-07
is right that the wire dict carries `vpp_mv` and `vcc_mv` only. Two refinements:
`convert_to_programmer`'s dict does not carry `vcc_mv` **either** — its voltage payload is `vpp_mv`
alone [VERIFIED: `firestarter/database.py:527-536`] — and the dict is an explicit **allow-list**, so
it is structurally closed against accidental additions. And `vdd_mv` is dropped one stage earlier
still, at `_map_data` (§B-2). The field never leaves the raw record.

### H. The non-vacuity template for the 284-row count

`tests/test_vpp_rail_classification.py` (426 lines, Phase 199) is the pattern to follow, and it is
close to a drop-in structural analogue. Its nine documented legs:

1. Row total **and** value histogram as **equalities** against module-level `_EXPECTED_*` constants.
2. A derived-property histogram with an explicit `_UNMAPPED_*` label, asserted absent.
3. An all-`supported` assertion — *"Nothing in this phase moves a support_status; this is the
   assertion that would catch it if something did."*
4. Per-group shape uniformity.
5. **Boundary**: a synthetic row one unit below the floor is excluded; one exactly on it is counted.
6. **Non-vacuity, injected row**: total shifts 30 → 31.
7. **Non-vacuity, rewritten field**: the histogram shifts.
8. **Non-vacuity, rewritten status**: the all-supported claim breaks.
9. **Source-shape guard**: reads the module's own source, asserts every test exists by name, that
   load-bearing count literals occur exactly once, and that no weakening idiom has crept in.

**The non-vacuity mechanism, verbatim** [VERIFIED: `tests/test_vpp_rail_classification.py:285-313`]:

```python
def test_injecting_a_synthetic_row_makes_the_total_go_to_31() -> None:
    """Non-vacuity, defect class closed: a census helper that silently
    matched anything -- an empty row list, a swallowed exception, a filter
    that never selected -- would pass every other test in this module.
    ...The original database on disk is never written to.
    """
    db = _load_db()
    mutated = copy.deepcopy(db)
    manufacturer = next(iter(sorted(mutated)))
    mutated[manufacturer].append(
        {
            "part_number": "SYNTHETIC-THIRTY-FIRST-ROW",
            "support_status": "supported",
            "electrical": {"vpp_mv": _VPP_CENSUS_FLOOR_MV, "pin_count": 28},
            "programming": {"algorithm": 0x07},
        }
    )
    baseline_rows, _, _, _ = _census(db)
    mutated_rows, _, _, _ = _census(mutated)
    assert len(baseline_rows) == 30
    assert len(mutated_rows) == 31, (...)
```

Two structural rules the planner must carry over or the template breaks:

- **One shared `_census(db)` helper** that every test calls, *"so a failure names which property moved
  rather than which reimplementation disagreed with which."*
- **The source-shape guard's fragments must be `+`-joined.** Its own docstring explains why: *"A
  guard written as one contiguous literal would count or match itself."* Written as
  `"_EXPECTED_TOTAL_ROWS" + " = 284": 1` and `">" + "= 284"`. This is subtle and easy to get wrong.

**Recommended `_EXPECTED_*` constants for Phase 200**, all measured this session:

```python
_SHIELD_FIXED_VCC_MV = 5000
_EXPECTED_TOTAL_ROWS = 284
_EXPECTED_VDD_HISTOGRAM = {5500: 164, 6000: 8, 6250: 7, 6500: 105}
_EXPECTED_ALGORITHM_HISTOGRAM = {7: 161, 8: 102, 11: 21}
_EXPECTED_TYPE_HISTOGRAM = {"UV-EPROM": 284}      # §A-2 — all 284, no exceptions
_EXPECTED_VENDOR_COUNT = 34
```

Plus two legs the Phase 199 template does not have an analogue for, both cheap and both closing a
real class:

- **Disjointness (§A-3):** no row in the `vcc_mv == 5500` VOLT-03 set is in the 284. Currently `0`
  overlap out of 28. This is the assertion that protects Phase 198's D-11 group.
- **Fail-open (§F-1):** synthetic rows with `vdd_mv` absent / `None` / `0` / exactly `5000` all
  produce no row and no warning, asserted against the *predicate helper*, not the renderer.

### I. RAIL-03 — confirmed not a template, and confirmed not retrofitted here

[VERIFIED: `199-05-SUMMARY.md:204-218`] RAIL-03 stays Pending on two measured grounds: the existing
`MSG_WARN_VPP_LOW` trigger is a 5 % window applied to a reading measured ~7.6 % high, so a real
shortfall smaller than that combined margin never fires it — *"precisely the silent attempt RAIL-03
forbids"* — and the number it names is the live ADC reading, not the deliverable maximum. The gap is
recorded as a limit in `DECODE-NOTES.md` § 10 [VERIFIED: `tools/DECODE-NOTES.md:710-715`].

The ROADMAP amendment and CONTEXT.md are consistent with the Phase 199 record. **Do not plan any task
that edits RAIL-03's checkbox or its traceability row.** §D's precedent is a *host display* shape from
`eprom_info.py`, not RAIL-03's firmware warning — using it does not constitute a retrofit.

## Common Pitfalls

### Pitfall 1: Grepping a filename that does not exist, and reading zero hits as evidence of absence
**What goes wrong:** CONTEXT.md concluded "`info` has NO existing warning path" from a grep over
`eprom_presenter.py`. No such file exists; the grep matched nothing and the nothing was read as a
finding. The real file, `eprom_info.py`, has two warning blocks.
**Why it happens:** the Click context attribute is `app.eprom_presenter`, and the class is
`EpromConsolePresenter` — the module name is the one thing that is *not* "presenter".
**How to avoid:** `ls` the path before trusting a zero-hit grep. And use `/usr/bin/grep` or
`git grep`: the devcontainer's `grep` is **ugrep**, which honours `.gitignore` and silently
under-scans.
**Warning signs:** a negative claim resting on a grep that returned nothing at all, rather than on
reading the file.

### Pitfall 2: Copying the hardcoded pad from the neighbouring warning rows
**What goes wrong:** `"Support status:      "` is 15 chars + 6 spaces = 21, where `pos = 20` puts
every other value at column 21 (0-indexed 20). The existing warning rows are one column out. Copying
that idiom puts `Programming VCC:` out of alignment with `VCC:` directly above it — which is exactly
the thing D-04's mock-up shows aligned.
**How to avoid:** `f"{'Programming VCC:': <{pos}}{...}"`. Never a literal pad.
**Warning signs:** a space-run inside a string literal in `present_eprom_details`.

### Pitfall 3: Matching override keys to DB rows without comma-splitting
**What goes wrong:** `part_number` holds comma-joined aliases (`"MBM27C1000P,MBM27C1000"`), so
`f"{mfg}/{row['part_number']}"` misses every multi-alias row. It produced a wrong intermediate
result in this very research session.
**How to avoid:** split on `,`, strip, and test membership as a set intersection. `firestarter_app/CLAUDE.md`
§ Database Pipeline states the rule outright.
**Warning signs:** an override-coverage count that looks suspiciously round or suspiciously low.

### Pitfall 4: Planning a test for a fail-open case the database cannot produce
**What goes wrong:** D-06 names absent / null / zero `vdd_mv`. All three have **zero** live rows
(§F-1), and `build_db.py`'s `.get(..., 5000)` default guarantees they never appear. A test that
searches for such a row either passes vacuously or cannot be written.
**How to avoid:** synthetic in-memory dicts, per the Phase 199 boundary-test pattern. State in the
plan that the branch is unreachable from the shipped DB and live only via user overrides (§F-2), so
a reviewer does not delete it as dead code.

### Pitfall 5: Re-recording the snapshot file wholesale
**What goes wrong:** `--snapshot-update` without a node-id argument rewrites all 32 entries, sweeping
unrelated drift into the commit and destroying the evidence that only the intended line moved.
**How to avoid:** the §E-2 sequence — scope to the node id, then gate on `git diff --numstat` **before
committing**. For this phase the expected numstat is **insertions only, zero deletions** (§E-1); a
non-zero deletion count is a fail-closed signal.
**Warning signs:** a numstat with a large matched pair, or a leg that runs after the commit (it
reports zero and passes vacuously).

### Pitfall 6: Writing the source-shape guard's literals contiguously
**What goes wrong:** the guard reads its own source, so a contiguous `"_EXPECTED_TOTAL_ROWS = 284"`
literal counts itself and inflates every expected count by one; a contiguous `">= 284"` entry in the
weakening list matches its own definition and fails immediately.
**How to avoid:** `+`-join every fragment, as the Phase 199 module does and documents.

### Pitfall 7: Treating a decoded rail index as a datasheet requirement
**What goes wrong:** §G-1 in full. The project spent Phase 198 establishing that `vdd_mv` is a
programmer rail slot; a warning that says "this part programs at X" re-asserts the reading that
phase falsified, for 281 of 284 rows.
**How to avoid:** hedge the verb, or record the limit. Do not let the wording ship unexamined merely
because it is a locked decision — surface it to the operator as a checkpoint.

## Code Examples

### The field-row injection (recommended shape)

```python
# Target: firestarter/eprom_info.py, inside prepare_detailed_eprom_data,
# immediately AFTER the support_status block at lines 138-147.
# Mirrors that block's gate-so-the-common-case-adds-no-key discipline.

        # Elevated programming supply (VCC-01). Gated on vdd_mv > the shield's
        # fixed rail so the 462 rows at or below it add no key -- which is both
        # D-06's fail-open and what keeps every existing info snapshot byte-stable.
        # Read from raw_config_data because _map_data does not carry vdd_mv;
        # chained .get() because a ~/.firestarter/database.json override may omit it.
        if raw_config_data:
            try:
                _vdd_mv = int(
                    (raw_config_data.get("electrical") or {}).get("vdd_mv", 0) or 0
                )
            except (TypeError, ValueError):
                _vdd_mv = 0
            if _vdd_mv > _SHIELD_FIXED_VCC_MV:
                combined_data["programming_vcc_mv"] = _vdd_mv
                combined_data["programming_vcc_str"] = format_mv(_vdd_mv)
```

`format_mv` is already imported at `eprom_info.py:15`. `_SHIELD_FIXED_VCC_MV = 5000` is a new
module-level constant in this file — **not** in `constants.py` (C-11).

### The row and the warning (recommended shape)

```python
# Target: firestarter/eprom_info.py, inside present_eprom_details.
# The row goes immediately after the VCC: line (eprom_info.py:248),
# before the `if "vpp_str" in chip_data:` guard, per D-04's mock-up.

        logger.info(f"{'VCC:': <{pos}}{chip_data.get('vcc_str')}")
        if "programming_vcc_str" in chip_data:
            logger.info(
                f"{'Programming VCC:': <{pos}}{chip_data.get('programming_vcc_str')}"
            )
        if "vpp_str" in chip_data:
            logger.info(f"{'VPP:': <{pos}}{chip_data.get('vpp_str')}")

# ... and the warning block, placed alongside the existing no_pinout_warning
# block (eprom_info.py:260-267) whose three-line shape it copies:

        if "programming_vcc_str" in chip_data:
            logger.warning("")
            logger.warning(
                f"WARNING: this part's programming supply decodes to "
                f"{chip_data['programming_vcc_str']}; the shield supplies a fixed "
                f"{format_mv(_SHIELD_FIXED_VCC_MV)}."
            )
            logger.warning(
                f"Programming will be attempted at "
                f"{format_mv(_SHIELD_FIXED_VCC_MV)}."
            )
```

Two things this skeleton takes a position on, both flagged for the plan rather than assumed:
- It uses §G-1 option 1's hedged verb ("decodes to"). **If the operator keeps D-04 verbatim, change
  it back to "this part programs at".**
- It renders voltages through `format_mv`, giving `6.0v` / `5.0v`. D-04's warning text writes
  `6.0 V` and `5.0 V` (space, capital V). **Confirm which the operator wants in the prose line**;
  the field row is unambiguously `format_mv`.

Both are `checkpoint:human-verify` material, not executor discretion.

### The census test skeleton

```python
# tests/test_programming_vcc_census.py  (name is the planner's call)
import collections, copy, json
from pathlib import Path

_FA_DIR = Path(__file__).parent.parent
_DB_FILE = _FA_DIR / "firestarter" / "data" / "chip_database.json"

_SHIELD_FIXED_VCC_MV = 5000
_EXPECTED_TOTAL_ROWS = 284
_EXPECTED_VDD_HISTOGRAM = {5500: 164, 6000: 8, 6250: 7, 6500: 105}
_EXPECTED_ALGORITHM_HISTOGRAM = {7: 161, 8: 102, 11: 21}
_EXPECTED_TYPE_HISTOGRAM = {"UV-EPROM": 284}

def _load_db() -> dict:
    return json.loads(_DB_FILE.read_text(encoding="utf-8"))

def _all_chips(db: dict):
    for mfg, chips in db.items():
        for chip in chips:
            yield mfg, chip

def _census(db: dict):
    """The one census helper every test in this module calls, so a failure
    names which property moved rather than which reimplementation disagreed."""
    rows = [
        (mfg, chip)
        for mfg, chip in _all_chips(db)
        if (chip.get("electrical", {}).get("vdd_mv") or 0) > _SHIELD_FIXED_VCC_MV
    ]
    return (
        rows,
        dict(collections.Counter(c["electrical"]["vdd_mv"] for _, c in rows)),
        dict(collections.Counter(c["programming"]["algorithm"] for _, c in rows)),
        dict(collections.Counter(c["electrical"]["type"] for _, c in rows)),
        dict(collections.Counter(c.get("support_status") for _, c in rows)),
    )
```

Every literal above was measured this session (§A-1, §A-2).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `vdd_mv` read as the part's datasheet programming voltage | `vdd_mv` read as a **programmer rail-table index**, not a chip requirement | Phase 198 (VOLT-01), `DECODE-NOTES.md` § 9 | Governs how this phase's warning may be phrased (§G-1) |
| `VCC_VOLTAGES` partial (6 indices) | Completed from upstream `xg_vcc_voltages[]` (15 indices incl. `0x0D`=6000, `0x0E`=6250) | Phase 198 | The 6000 and 6250 tiers in the histogram exist *because* of this completion |
| Shortfall stated by the firmware's `MSG_WARN_VPP_LOW` | Adjudicated insufficient for RAIL-03; VPP routing moved to firmware (D-21) | Phase 199 | Why Phase 200 defines a host-side shape from scratch (§D, §I) |
| Exact counts asserted as floors | Exact counts as **equalities**, proved non-vacuous by planted mutation | Phase 199 | The template §H reproduces |
| Source comments forbidden in product source | **Rule RETIRED** in all three repos | 2026-09-19 | Explanatory comments in `eprom_info.py` are allowed (C-9) |

**Deprecated/outdated:**
- `eprom_presenter.py` — never existed. Any reference to it in planning prose is a naming error for
  `eprom_info.py` (§G-2).
- CONTEXT.md's "`logger.warning` on a non-verbose run may not reach the operator" — false on this
  surface (§C-1).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The operator intends the warning's `6.0 V` / `5.0 V` prose spelling to differ from the field row's `format_mv` `6.0v`, rather than it being an informal transcription in the mock-up. | §D, Code Examples | Cosmetic mismatch between the row and the warning in shipped output; caught by the new snapshot at review, but better asked than guessed. |
| A2 | Placing the `Programming VCC:` row between `VCC:` and `VPP:` reflects intent, read from D-04's mock-up ordering. Nothing states it normatively. | §B-1 | Row ordering differs from expectation; trivial to move, but it moves the new snapshot. |
| A3 | `test_list` and `test_search_w27` are unaffected because neither list-view column renders VCC. Verified by reading `print_eprom_list_table`'s column set (Name/Manufacturer/Pins/Chip ID/Type/VPP), **not** by running the phase's change. | §E-1 | An unexpected snapshot deletion appears in the numstat — which the §E-2 gate catches by design. |
| A4 | The plan will scope the snapshot re-record to a single new node id. The §E-1 "insertions only, zero deletions" expectation holds only under that scoping. | §E-1, §E-2 | A blanket `--snapshot-update` would produce a numstat that neither expectation matches. |
| A5 | `pytest-randomly` is not active (no config found in `conftest.py` or `pyproject.toml`); `-p no:randomly` is carried from Phase 199 as harmless defence. | §E-2 | None — the flag is inert if the plugin is absent. |
| A6 | § 9's rail-index verdict is read as applying to `vdd_mv` values generally, including the 6000 and 6250 tiers introduced by the same table completion. § 9's explicit worked evidence is the `0x04`/`0x05` (5500/6500) pair. | §G-1 | If `0x0D`=6000 were somehow datasheet-faithful where `0x04` is not, §G-1's severity drops for 8 rows — but the 164-row 5500 tier, which § 9 addresses head-on, is unaffected. |

## Open Questions

1. **How should D-04's warning verb be resolved against `DECODE-NOTES.md` § 9?**
   - What we know: 3 of 284 rows carry a datasheet-grounded `vdd_mv`; 281 carry a decoded rail
     index. § 9's verdict is explicit and was established by this milestone's own Phase 198.
   - What's unclear: whether the operator, who agreed D-04's wording, weighed it against § 9.
   - Recommendation: **§G-1 option 1** — change "programs at" to "decodes to". Surface as a
     `checkpoint:human-verify` before the wording is implemented; D-04 is a locked decision and only
     the operator may amend it.

2. **Should the `Programming VCC:` row be `logger.info` or `logger.warning`?**
   - What we know: `logger.info` matches every other field row and is snapshot-visible;
     `logger.warning` is additionally CliRunner-visible (§C-3).
   - What's unclear: whether the planner wants an in-process assertion on the row as well as the
     warning.
   - Recommendation: `logger.info` for the row, `logger.warning` for the warning block. The
     subprocess snapshot already pins the row, so CliRunner visibility buys nothing worth a
     semantically wrong log level.

3. **Which part should the new `info` snapshot pin?**
   - What we know: CONTEXT.md nominates `FUJITSU/MBM27C1000P,MBM27C1000` (also gh#70's part, so a
     reporter would recognise it) — but it is one of the 281 rail-index rows (§G-1).
   - What's unclear: whether to pin one of the 3 datasheet-backed rows (e.g. `FUJITSU/MBM27C4001`)
     instead, or both.
   - Recommendation: pin **both** — `MBM27C1000` for recognisability and `MBM27C4001` as a
     datasheet-backed instance. Two additive snapshots cost almost nothing and, if §G-1 is ever
     revisited, the evidence for both classes is already committed.

4. **Should the two existing misaligned warning rows be fixed?**
   - What we know: `Support status:` and `Reason:` sit one column right of every `pos`-formatted row
     (§B-1 anti-patterns).
   - What's unclear: nothing, really — it is simply out of this phase's scope.
   - Recommendation: **do not fix here.** It would move `test_info_*` snapshots for reasons unrelated
     to VCC-01 and muddy the §E-1 zero-deletions gate. File as a backlog item.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11 (CI parity, C-2) | Running the suite as CI will | ✓ | 3.11.16 at `.venv311/bin/python` | `.venv/ci-replica` (also present) |
| `.venv/ci-replica` | The Phase 199 snapshot command verbatim | ✓ | — | `.venv311` |
| `firestarter` entry point on PATH | `run_firestarter` subprocess harness | ✓ | 3.0.0b48, resolving to `/workspaces/firestarter_app/firestarter/__init__.py` (editable, live) | `pip install -e '.[test]'` |
| `chip_database.json` | The census | ✓ | 746 rows | none needed |
| `syrupy` | Snapshot tests | ✓ | `>=5.0,<7` pinned | — |
| `git` in all three repos, on the milestone branch | Committing | ✓ | all on `v1.40-program-parameter-fidelity` | — |
| Knowledge graph (`.planning/graphs/graph.json`) | Optional discovery | ⚠ **STALE** | built 31 h ago at `d11d37e`, **120 commits behind** HEAD `49a897b` | Direct source reading — which is what this research used throughout |
| Serial hardware / a shield | — | n/a | — | **Not required.** This phase is display-only; no bench session, no board, no flash. |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** the knowledge graph is stale by 120 commits; treat any
semantic relationship it reports as approximate. Every finding in this document was obtained by
reading source directly or executing code, not from the graph.

## Security Domain

`security_enforcement` is not set in `.planning/config.json`, so it is treated as enabled.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No identity, no auth surface; a local CLI reading a packaged JSON file |
| V3 Session Management | no | No sessions |
| V4 Access Control | no | No multi-user model or privilege boundary |
| V5 Input Validation | **yes** | The one live concern — see below |
| V6 Cryptography | no | No secrets, no crypto, no hashing in this change |
| V7 Error Handling & Logging | **yes (minor)** | The new lines go to stdout via `logging`; no PII, no secrets, no paths |
| V12 File Handling | no | Reads an existing packaged JSON; writes nothing |

### Known Threat Patterns for this change

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A `~/.firestarter/database.json` user override supplies a non-integer, `None`, or absent `vdd_mv`, crashing `info` on an unhandled `TypeError`/`ValueError` | Denial of Service (local, self-inflicted) | The §F-3 `try/except (TypeError, ValueError)` + `or 0` coercion — the same defensive shape `build_specifications` already uses for `vpp_mv` [VERIFIED: `ic_layout.py:570-573`] |
| A user override supplies an absurd `vdd_mv` (e.g. `99999999`) and the warning renders it as fact | Spoofing / misinformation | Accepted and inherent: the local override file is operator-owned and already authoritative for `vcc_mv` and `vpp_mv`. No new trust boundary is crossed. Worth one line in the phase record. |
| Format-string injection via a part name rendered into the warning | Injection | Not reachable — the recommended wording interpolates only `format_mv(int)` output and a module constant, never `part_number` or any user string |
| The warning is silently dropped, and the operator attempts a write believing the supply is adequate | Repudiation / silent failure | This **is** the defect VCC-01 closes. The §H fail-open and census legs are what keep the predicate from regressing to silence |

**Net:** this is a read-only display change with no new external input, no new file write, no network
call and no new dependency. The only substantive control is input coercion on a field that may be
absent or mistyped when supplied by a local override — already mandated by D-06 for correctness, and
satisfying V5 as a side effect.

## Sources

### Primary (HIGH confidence — read or executed this session)
- `/workspaces/firestarter_app/firestarter/eprom_info.py` — lines 15, 90, 138-147, 214-330 (the
  renderer, `pos = 20`, both existing `logger.warning` blocks, the `support_status` injection
  precedent)
- `/workspaces/firestarter_app/firestarter/cli_handlers.py` — 100-123 (`_setup_logging`), 415-458
  (group entry + the test-mode short-circuit), 472-503 (the `info` handler), 660-690 (the
  `click.echo` precedent comment)
- `/workspaces/firestarter_app/firestarter/database.py` — 115-122 (`format_mv`), 152-182 (the user
  override seam), 347-420 (`_map_data`), 514-580 (`convert_to_programmer`)
- `/workspaces/firestarter_app/firestarter/ic_layout.py` — 505-590 (`build_specifications`, the
  defensive `int()` coercion pattern)
- `/workspaces/firestarter_app/firestarter/logging_utils.py` — 14-53 (`SingleLineStatusHandler`,
  stdout)
- `/workspaces/firestarter_app/firestarter/chip_resolver.py` — 28-55 (the only
  `ChipNotImplementedError` raiser)
- `/workspaces/firestarter_app/tests/test_vpp_rail_classification.py` — all 426 lines (the census
  template)
- `/workspaces/firestarter_app/tests/test_characterization.py` — 1-46 (harness decisions), 125-145
  (`run_firestarter`), 320-351 (the two `info` tests)
- `/workspaces/firestarter_app/tests/__snapshots__/test_characterization.ambr` — 395-500 (both `info`
  snapshots)
- `/workspaces/firestarter_app/tools/DECODE-NOTES.md` — § 9 (lines 371-470), § 10 (lines 710-728)
- `/workspaces/firestarter_app/tools/build_db.py` — 115-137 (`VCC_VOLTAGES`), 687 (the `vdd_mv`
  decode with its 5000 default)
- `/workspaces/firestarter_app/tools/datasheet_overrides.json` — the 15 `electrical.vdd_mv` entries
- `/workspaces/firestarter_app/firestarter/data/chip_database.json` — all 746 rows, measured
- `/workspaces/.planning/phases/199-.../199-05-SUMMARY.md` — 204-218 (RAIL-03 adjudication)
- `/workspaces/.planning/phases/199-.../199-01-PLAN.md` — 201-218 (the scoped re-record command)
- `/workspaces/.planning/phases/198-.../198-VOLT03-DISPOSITION.md` — 1-45 (method, the 28-row set)
- `/workspaces/CLAUDE.md`, `/workspaces/firestarter_app/CLAUDE.md`, `/workspaces/.planning/REQUIREMENTS.md`,
  `/workspaces/.planning/config.json`
- **Executed:** the `vdd_mv`/`vcc_mv` census; the override comma-split join; `firestarter info AT28C04`
  at default verbosity (stdout and stderr separately); a `CliRunner` invocation with `obj=app`;
  `pytest tests/test_characterization.py` (36 passed); `gsd-tools graphify status`

### Secondary (MEDIUM confidence)
- None. No claim in this document rests on a secondary source.

### Tertiary (LOW confidence)
- None. **No web search was performed and none was warranted** — every question this phase raises is
  a fact about this repository, answerable by reading or running it. Introducing external sources
  would have added unverifiable claims to a document whose value is that it is all measured.

## Metadata

**Confidence breakdown:**
- **Standard stack: HIGH** — no new dependencies; every library named was read in the importing file.
- **The 284-row measurement: HIGH** — executed against the live database; reproduces CONTEXT.md's
  D-01 to the unit on every figure, and adds three invariants (all-UV-EPROM, per-algorithm split,
  VOLT-03 disjointness).
- **Architecture / the seam: HIGH** — `_map_data`, `convert_to_programmer`,
  `prepare_detailed_eprom_data` and `present_eprom_details` all read end to end; the wire-dict
  allow-list confirmed by reading its construction.
- **The warning mechanism: HIGH** — settled by running the real CLI and a real `CliRunner`
  invocation, not by reading configuration and inferring.
- **Snapshot blast radius: HIGH** — both `info` snapshot chips' `vdd_mv` measured at 5000; baseline
  suite run green (36 passed / 32 snapshots).
- **Fail-open data availability: HIGH** — all four absence conditions counted at zero across 746
  rows, with the generator's `.get(..., 5000)` default explaining why.
- **§G-1's wording finding: HIGH on the measurement, MEDIUM on the recommendation** — the 3-vs-281
  split is measured and § 9's verdict is quoted verbatim; whether to hedge the verb is an operator
  judgement this research can only surface.
- **Pitfalls: HIGH** — every one was either observed in the live tree or hit during this session.

**Research date:** 2026-09-19
**Valid until:** 2026-10-19 (30 days). Earlier if `chip_database.json` is regenerated — every count
in §A and §H is a property of the current generated database and must be re-measured after any
regeneration.
