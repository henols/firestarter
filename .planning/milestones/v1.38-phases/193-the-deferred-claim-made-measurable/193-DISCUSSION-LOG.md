# Phase 193: The Deferred Claim, Made Measurable - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-14
**Phase:** 193-the-deferred-claim-made-measurable
**Areas discussed:** Instrument form, What the number measures, Trigger shape + window, Where the rules live

**Mode:** default (interactive), `workflow.research_before_questions: true`. Research was performed as
**live measurement** against the PyPI JSON API, the pypistats.org API, the ClickHouse public PyPI dataset
and `gh api`, rather than as a web search — the phase's subject is a number, and a measured number beats a
cited practice.

---

## Instrument form

### Q1 — What form does the instrument take?

| Option | Description | Selected |
|--------|-------------|----------|
| A committed runnable script | One curl to ClickHouse, prints the pip-only per-version table and the verdict. Cost: a maintenance surface with nothing watching it. | ✓ |
| A recorded query + one baseline measurement | SQL and curl written into a note plus today's numbers. Cost: whoever evaluates the trigger re-derives the run by hand. | |
| Script that prints its own staleness | Same script, asserting the table exists and `max(date)` is recent, refusing a verdict otherwise. | |

**User's choice:** A committed runnable script.
**Notes:** The third option was a real offer, not filler — declining it is recorded in CONTEXT.md D-01 so
a planner does not reintroduce a staleness gate as an "obvious" improvement.

### Q2 — Where does it live, and in what language?

| Option | Description | Selected |
|--------|-------------|----------|
| `tools/adoption/`, shell | Beside `tools/catalog/`. Shell because the instrument is one `curl -G` with a URL-encoded query. | ✓ |
| `tools/adoption/`, Python | Matches `tools/catalog/codegen.py`; buys arg parsing and formatting, costs a Python dependency. | |
| `.planning/` beside the seed | Put it where the trigger is evaluated. Cost: cuts against Phase 192 D-01's record/act-on split. | |

**User's choice:** `tools/adoption/`, shell.

### Q3 — Where does GATE-01's required honesty live?

| Option | Description | Selected |
|--------|-------------|----------|
| In the script's own output | Caveat block prints beneath the numbers every run. | ✓ |
| In the accompanying record only | Script prints numbers; note carries the caveats. Cost: the number travels alone once pasted. | |
| Both — short line in output, full reasoning in the record | Costs duplication and a path that must stay correct. | |

**User's choice:** In the script's own output.

---

## What the number measures

### Q4 — Which population does the share compute over?

| Option | Description | Selected |
|--------|-------------|----------|
| pip-only, stable channel only | Both sides `installer='pip'`, prereleases excluded. Measures exactly the at-risk population. | ✓ |
| pip-only, all versions in denominator | Conservative; blends two non-comparable populations across ~165 prerelease versions. | |
| No installer filter | What every public tool shows. Cost: pip is 3.2% of traffic — would measure mirror re-scan timing. | |

**User's choice:** pip-only, stable channel only.
**Notes:** Presented with the measured 90-day installer split — bandersnatch 11,672, unknown 6,739,
Browser 2,194, requests 1,718, pip 740, Nexus 52, uv 6.

### Q5 — What defines the numerator?

| Option | Description | Selected |
|--------|-------------|----------|
| Any stable `>= 2.0.9`, computed | First stable carrying the `firestarter_fw` URL; later stables count automatically. | ✓ |
| A named allowlist in the script | Unambiguous; costs a manual edit per stable, and a forgotten edit reads as un-fired forever. | |
| Everything except the known-stranded set | Same arithmetic inverted, but counts a 1.5.4 install as "fixed". | |

**User's choice:** Any stable `>= 2.0.9`, computed.

### Q6 — How much should the instrument hedge against its single free data source?

| Option | Description | Selected |
|--------|-------------|----------|
| Record the fallback, don't build it | Names BigQuery and `pypi.pypi_raw` in the record; no second code path. | ✓ |
| No hedge at all | Simplest artifact; a dead endpoint gives the evaluator no route. | |
| Build a second source | Genuinely resilient; an untested credentialed path fails on the day it is needed. | |

**User's choice:** Record the fallback, don't build it.

---

## Trigger shape + window

### Q7 — What shape is the trigger condition?

| Option | Description | Selected |
|--------|-------------|----------|
| Share AND an absolute floor | A ratio says nothing about how many people are behind it; the floor bounds harm. | ✓ |
| Share threshold alone | One number, one window, easy to state and check. | |
| Absolute decay only | Measures harm directly; noisy at 30–50 downloads/month and gives no adoption signal. | |

**User's choice:** Share AND an absolute floor.
**Notes:** Presented alongside the finding that a download of a stranded version *today* is a **new
acquisition** of an old version, and that a genuinely stranded user emits zero downloads — so any
threshold certifies a necessary, not sufficient, condition.

### Q8 — Pick the threshold and floor.

| Option | Description | Selected |
|--------|-------------|----------|
| `>= 90%` AND 2.0.7 `<= 10` per 90d | Would have fired ~3 months after the 2.0.7 cut. Today reads 12.8% / 116. | ✓ |
| `>= 95%` AND 2.0.7 `<= 5` per 90d | ~One further quarter of waiting; 5 sits inside the scraper noise floor. | |
| `>= 80%` AND 2.0.7 `<= 25` per 90d | Would have fired ~2 months after the cut; accepts ~a quarter still landing stranded. | |

**User's choice:** `>= 90%` AND 2.0.7 `<= 10` per 90 days.
**Notes:** Grounded on the 2.0.6 → 2.0.7 natural experiment (70% / 94% / 100% across Jan–Mar 2026, with a
tail of 2 in May and 1 in July) and on the finding that the pre-2.0.7 tail is automation — 398 / 254 / 320
/ 265 / 52 by quarter, present even before 2.0.7 existed. The 90-day window was justified by the scraper
spikes at Jan 342 and May 312 against a 34–75 baseline.

### Q9 — Should the trigger carry a re-examination condition?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — a re-examine date, not an auto-fire | Forces a look at the premise; never fires the destructive act on a date. | ✓ |
| No — the trigger stands until met | Avoids reintroducing calendar gating; costs the accumulation pattern Phase 188 cleared by deletion. | |
| Yes — and name the fallback if it never fires | Most complete; designs a branch that may never be walked. | |

**User's choice:** Yes — a re-examine date, not an auto-fire.

---

## Where the rules live

### Q10 — Where is GATE-02's rule recorded?

| Option | Description | Selected |
|--------|-------------|----------|
| `CLAUDE.md` rule + note for the mechanism | Matches the existing close/branch-protection pattern; the only place guaranteed in front of an agent before it acts. | ✓ |
| The seed and the impact-analysis note only | Zero new surface; both reached only by someone already working on the rename. | |
| `CLAUDE.md` + the close-procedure note | Warning at the moment of the risky act; that note is v1.35-titled and already accreting. | |

**User's choice:** `CLAUDE.md` rule + note for the mechanism.

### Q11 — Where does GATE-03's `.gitmodules` trap live?

| Option | Description | Selected |
|--------|-------------|----------|
| `CLAUDE.md` pointer + a dedicated note | Archaeology sessions start from `CLAUDE.md`; the note carries both workarounds and transcripts. | ✓ |
| A note only, cited from the codebase docs | Keeps `CLAUDE.md` short; `STRUCTURE.md` is read when mapping, not when a clone has gone wrong. | |
| `CLAUDE.md` pointer + `.devcontainer/README.md` | Warns where fresh environments are built; two homes to keep true. | |

**User's choice:** `CLAUDE.md` pointer + a dedicated note.

### Q12 — Does `CLAUDE.md` point at the existing mechanism, or does a new note get written?

| Option | Description | Selected |
|--------|-------------|----------|
| Point at the existing note | One source of truth, no drift; the rule lives inside a dated analysis document. | ✓ |
| New standing-rules note, existing one cites it | Cleanest long-term home; edits a completed phase's document and adds a third file for one rule. | |
| Restate it in `CLAUDE.md` in full | No second hop; a 77-line brief absorbs version-parsing detail and a copy that can drift. | |

**User's choice:** Point at the existing note.

---

## Claude's Discretion

Settled mechanically during the discussion without consuming an operator question, each on a stated
precedent rather than preference:

- **PEP 440-shaped prerelease filter** over `NOT LIKE '%b%'` — the latter silently admits a future `rc`/`a`
  release into the stable denominator.
- **`uv` included alongside `pip`** in the installer set — excluding a pip-equivalent human installer
  under-counts real users and makes the gate fire late.
- **The at-risk denominator keys on 2.0.7 specifically**, not "everything `<= 2.0.7`" — the pre-2.0.7 tail
  is automation that predates 2.0.7's existence, and the record must say the population down there is
  outside the instrument's reach.
- **A single 90-day reading**, not two consecutive — the window already damps the spikes, D-7 puts a human
  in front of the act, and overlapping windows make "consecutive" ambiguous.
- **Re-examine date = 2027-09-13** — twelve months from 2.0.9's publish, four times the precedent's
  headroom. Offered for correction at the time and not corrected.
- **The seed's `trigger_condition:` frontmatter is rewritten verbatim with the numbers** — ROADMAP
  criterion 1 asks for exactly this.
- **GATE-03's "demonstrated" means executed with committed transcripts** — RENAME-03 required
  "demonstrated, not reasoned about" and STABLE-02 was proved with a RED/GREEN fixture pair.
- **Comments are permitted in the meta `tools/` script** but GSD process commentary is not — the
  operator's hard rule scopes to `firestarter/` and `firestarter_app/`; process citations are forbidden
  everywhere.

## Deferred Ideas

- Fixing `new-milestone.md`'s `SEED-*.md` glob mismatch (vendored file; `/gsd-update` would overwrite;
  this phase's seed matches anyway). Stays a todo.
- Running the instrument on a schedule (meta has no `.github/workflows/`).
- Building a second data source for the instrument (D-03 records fallbacks instead).
- Resolving the PyPI/GitHub name incoherence after the eventual claim (already out of scope at milestone
  level).

**Todos reviewed, none folded:** 37 matches, generic keyword collisions. Two checked properly — the
`publish.yml` bot-release item (app repository, not meta) and the seed-glob item (checked live; this
phase's seed does surface).
