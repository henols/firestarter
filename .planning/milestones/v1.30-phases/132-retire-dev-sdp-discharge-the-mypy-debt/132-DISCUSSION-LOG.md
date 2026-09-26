# Phase 132: Retire `dev sdp` & Discharge the mypy Debt - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-03
**Phase:** 132-Retire `dev sdp` & Discharge the mypy Debt
**Areas discussed:** Orphaned survivors' destination, How GREEN gets proven, Watermark policy and the
typed fixture, Stale-anchor correction shape

**Areas offered and declined:** none — the operator selected all four. Two smaller areas (the `.ambr`
snapshot-update mechanics, the tripwire's exact placement) were offered as Claude's discretion and
left there. One area was **not offered**, deliberately: the `eprom_operations.py` D-07 ring-fence,
which research asked to be decided at this phase's scoping but which `REQUIREMENTS.md`'s Out-of-Scope
table already records as an operator decision of 2026-08-03 → `FUT-MYPY-02`.

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Orphaned survivors' destination | The four honesty assertions, the D-14 mapping, the D-10 wording have no SUT in 132 — their destinations are Phases 134/135 | ✓ |
| How GREEN gets proven | The devcontainer cannot produce a count; `gh workflow run` needs an operator turn | ✓ |
| Watermark policy once green | RETIRE-06 says "at 35"; the research spine says "re-baselined to the true count" | ✓ |
| Stale-anchor correction shape | Five references measured, not three; line numbers re-stale | ✓ |

**User's choice:** all four.

---

## Orphaned survivors' destination

### Where the D-10 wording and D-14 mapping land

| Option | Description | Selected |
|--------|-------------|----------|
| Shared helper now | A production module both future consumers call; the four honesty tests get a real SUT inside 132 | ✓ |
| Pre-stage on the write path | Put them where Phase 135's `--sdp-relock` will use them; unreachable until 135, and ruff `F` flags anything unused | |
| Source-presence gate only | Assert the four assertion strings are grep-findable; converts behavioral assertions into a scanning gate | |

**User's choice:** Shared helper now → **D-01**.
**Notes:** Framed by a live measurement — all three honesty strings exist in exactly one production
location (`cli_handlers.py:2215`, `:2267`, `:2316-2318`), inside the deleted span, so the deletion
removes the *carrier*, not just its test.

### Where the helper lives

| Option | Description | Selected |
|--------|-------------|----------|
| New `firestarter/sdp_honesty.py` | Single-purpose, added to the strict island so it is type-checked from birth | ✓ |
| Extend `firestarter/sdp_capability.py` | No new file, but mixes message text into a fail-closed predicate whose narrowness the 43/41/84 gate keys on | |
| Beside `sdp_lock`/`sdp_unlock` in `eprom_operations.py` | Closest to the ops, but that module is outside the strict island — untyped by construction | |

**User's choice:** New `firestarter/sdp_honesty.py` → **D-02**.

### The moved test file's name

| Option | Description | Selected |
|--------|-------------|----------|
| `tests/test_sdp_honesty.py` | Accurate in 132 and still accurate in 134/135; one same-commit target-list edit ever | ✓ |
| `tests/test_dev_test_sdp_leg.py` | Research's forward-looking name; for two phases it names a SUT that does not exist | |
| You decide | | |

**User's choice:** `tests/test_sdp_honesty.py` → **D-03**.
**Notes:** Either way `tools/check_no_exists_proxy.py:157` must change in the same commit or that
fail-closed gate goes RED (R-9).

### The other ~554 lines

| Option | Description | Selected |
|--------|-------------|----------|
| Prune, but account for it | Delete the dead gate-cases; count and name them so "no net loss" is a measured claim about four plus an accounted loss elsewhere | ✓ |
| Prune silently | Cheapest; a 550-line deletion inside a `git mv` is the diff shape that hides a real loss | |
| Keep what maps onto a survivor | Retarget onto `sdp_capability()`; risks duplicate coverage dressed as preservation | |

**User's choice:** Prune, but account for it → **D-04**.

### The `write` auto-unlock path's caveat

| Option | Description | Selected |
|--------|-------------|----------|
| Out of scope — record it | The caveat qualifies a *claim*, and `write`'s auto-unlock makes none; adding output is scope creep in a retirement phase | ✓ |
| In scope — add the caveat | Otherwise the caveat has no user-reachable carrier until Phase 134 | |
| You decide | | |

**User's choice:** Out of scope — record it → **D-05**.
**Notes:** The interim gap is recorded honestly in CONTEXT.md rather than closed early.

---

## How GREEN gets proven

| Option | Description | Selected |
|--------|-------------|----------|
| Local CI-replica venv, then one dispatch | Iterate against a numpy-free `.[test]` venv; ONE operator push + dispatch to certify | ✓ |
| Dispatch-driven throughout | Maximum fidelity; an operator turn per iteration, none of it automatable | |
| Local venv only; defer the CI claim | No operator turn; makes ROADMAP criterion 4 unachievable as worded | |

**User's choice:** Local CI-replica venv, then one dispatch → **D-06**.
**Notes:** Driven by a live measurement presented mid-question — the milestone branch does **not**
exist on origin (local 9 ahead of `origin/beta`) and `ci.yml`'s push trigger is `branches: [main]`
only, so certification needs *two* privileged operator actions, not one.

### Is the venv recipe committed?

| Option | Description | Selected |
|--------|-------------|----------|
| Separate committed script | Companion to `ci_parity.sh`, deliberately not folded in — that script's contract is faithful CI mirror | ✓ |
| Fold into `ci_parity.sh` leg 4 | One entry point; breaks the mirror contract and rewrites a script shipped 9 commits ago | |
| Prose in the phase record only | Zero new surface; 133–136 re-derive or skip it | |

**User's choice:** Separate committed script → **D-07**.

### Evidence form from the certifying run

| Option | Description | Selected |
|--------|-------------|----------|
| Both lines + 131 D-12's metadata | Gate line AND mypy's verbatim `Found N … (checked K source files)`, plus run id/URL, step statuses, versions | ✓ |
| Gate line only | Simpler; drops the clause that distinguishes a complete run from a truncated one | |
| You decide | | |

**User's choice:** Both lines + 131 D-12's metadata → **D-08**.
**Notes:** Phase 131's F-07 found the `checked K` clause structurally absent from an aborted run's
log, which is what makes its presence a completion proof rather than decoration.

### Correction issued during this area

Claude's own framing of the devcontainer as "false-greening" was corrected in-session against a live
run: post-Phase-131 the gate exits 2 with an explicit tool/config-failure message, and
`ci_parity.sh`'s leg-4 header already documents that. The venv is needed to obtain a count, not to
unmask a lie. Recorded as correction 3 in CONTEXT.md.

---

## Watermark policy and the typed fixture

| Option | Description | Selected |
|--------|-------------|----------|
| Green at 35, record the true count | Matches RETIRE-06 and criterion 4 verbatim; one operator turn; zero divergence risk; +2 headroom persists | ✓ |
| Ratchet to the local count, then dispatch once | Zero headroom, one turn IF the numbers agree; a ±1 divergence reddens the gate | |
| Green at 35, then ratchet + a second dispatch | Both states proven in CI; two operator turns in one phase | |

**User's choice:** Green at 35, record the true count → **D-09**.
**Notes:** Presented with the sequencing constraint that the watermark can only be lowered honestly
against a **CI** number, and the phase buys exactly one dispatch. The ratchet is filed as a deferred
item needing a named owner.

### The typed `AppContext` fixture's shape

| Option | Description | Selected |
|--------|-------------|----------|
| Typed factory + thin fixture | `make_app_context(...) -> AppContext` with explicit typed kwargs, plus an `app_context` fixture wrapping it | ✓ |
| Factory only | Least new surface; RETIRE-05 says "fixture", so the wording would need reconciling | |
| Fixture only | Idiomatic; callers needing variation re-invent a factory — how the 30-error pattern arose | |

**User's choice:** Typed factory + thin fixture → **D-10**.
**Notes:** Measured after the answer and recorded in CONTEXT.md: `make_app_context` is defined in
**eight** modules, not the five A-2 names — three use an unannotated `**manager_overrides` and
contribute zero errors under `check_untyped_defs = false`. Consolidating those three is out of scope.

---

## Stale-anchor correction shape

| Option | Description | Selected |
|--------|-------------|----------|
| Function names + corrected numbers | `_setup_operation`/`_operation_context` named first, `:329`/`:405` alongside | ✓ |
| Corrected numbers only | Exactly RETIRE-08's ask; guaranteed to re-stale | |
| Function names only, drop the numbers | Cannot go stale; loses a genuinely useful pointer across 76 lines | |

**User's choice:** Function names + corrected numbers → **D-11**.
**Notes:** R-7's own table is the receipt — v1.23's ~+98-line insertion staled 11 of its 12 anchors.

### RETIRE-08's own count

| Option | Description | Selected |
|--------|-------------|----------|
| Correct RETIRE-08 in-phase | Fix all five and correct the count in the same commit with a measured evidence clause | ✓ |
| Fix five, defer the text to Phase 137 | Satisfy it over-completely and hand the discrepancy to CLOSE-01; leaves a wrong number in place for five phases | |
| You decide | | |

**User's choice:** Correct RETIRE-08 in-phase → **D-12**.
**Notes:** The measurement that prompted it — five references across two files
(`constants.py:69-70`; `test_revision_constants_parity.py:71-72`, `:527`, `:549`, `:585-586`), where
the requirement and R-7 both say three.

---

## Claude's Discretion

Two areas offered as discretion and left there. Both are recorded in CONTEXT.md with reasoning, so a
later reader can overturn either on new facts rather than on taste.

- **D-13 — the `.ambr` snapshot update.** Scoped to the `test_help_dev` node id, reviewed against a
  named expected-diff shape, `git diff --stat` recorded; never a broad `--snapshot-update`. Carries a
  narrowing found during the scout: **P-15's second failure mode (syrupy failing the session on
  unused snapshots) does not fire in this phase** — removing line 141 leaves the `test_help_dev`
  entry still used. That trap belongs to Phase 136's channel split.
- **D-14 — the tripwire's placement.** At the auto-unlock **decision** site in `cli_handlers.py`
  (defaults `:302`/`:579`, D-04 auto-set block `:626-640`) plus `FLAG_SKIP_SDP_UNLOCK`'s definition
  (`constants.py:121`), with the named test extending `tests/test_write_skip_sdp_unlock.py`. R-7
  measured that the record's `eprom_operations.py:1637` is the **audit** site and mis-attributed.

## Deferred Ideas

- Ratchet the watermark to the measured true count — needs a named owner; file as a backlog item
  alongside Phase 131's 999.26 and 999.27.
- The `eprom_operations.py` `[union-attr]` ring-fence — already dispositioned → `FUT-MYPY-02`.
  Recorded so it is not re-opened as an unhandled carry.
- Consolidating the three untyped `make_app_context` copies — tidiness, not debt; zero mypy errors.
- The honesty caveat on the `write` auto-unlock path — Phases 134/135 own the claiming surfaces.
- The `.ambr` channel-split parametrisation and syrupy's unused-snapshot failure — Phase 136.
- `gh#20` (AT28C256 `dev test` FAIL) — triage before or with Phase 134's leg.
- P-17 traces 7–11 (gh#12 reply, b14 release notes, `.planning/` record sweep, the stale
  `--sdp-relock` deferral label) — Phase 137's CLOSE-05/06, behind a blocking operator wording review.

## Scope creep

None raised. The discussion stayed inside the phase boundary; every deferral above originates in the
research record or in a measurement made this session, not in a new capability the operator proposed.
