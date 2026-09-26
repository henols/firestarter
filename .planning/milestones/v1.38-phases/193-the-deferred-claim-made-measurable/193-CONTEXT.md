# Phase 193: The Deferred Claim, Made Measurable - Context

**Gathered:** 2026-09-14
**Status:** Ready for planning

<domain>
## Phase Boundary

The seed that carries the destructive act gets a trigger someone can evaluate, and the two facts that make
the eventual failure survivable get written where the person doing it will meet them. Covers **GATE-01,
GATE-02, GATE-03**.

The phase writes to the **meta repository only**. No sub-repo code, no outward-facing act, no publish, no
bench. It depends on Phase 191 (the instrument has nothing to measure until a stable carrying the new URL
exists — that stable is **2.0.9**, live on PyPI since 2026-09-13).

**In scope:** one committed shell instrument under `tools/adoption/`; a rewrite of
`SEED-claim-firestarter-slug.md`'s `trigger_condition` frontmatter and its "Why the trigger is what it is"
section; two additions to `CLAUDE.md`; one new note for the `.gitmodules` trap carrying two executed
workaround transcripts.

**Out of scope (settled earlier, not re-litigated here):** claiming `henols/firestarter` (D-1 — this phase
makes the claim *measurable*, it does not perform or authorise it); mirroring firmware releases onto the
meta repository (D-2); repairing `.planning/milestones/` (D-5); solving the `.gitmodules` history trap
(D-6 — it is documented, not solved); any push or release (D-7).

**Measured at discussion time, not assumed.** All figures below are from the live ClickHouse public PyPI
dataset (`sql-clickhouse.clickhouse.com`, `user=play`, no credentials), current to 2026-09-13, and from
`gh api`, on 2026-09-14.

| Instrument | Per-version? | Per-installer? | Credentials | Verdict |
|---|---|---|---|---|
| `pypistats.org` API | **no** | no | none | cannot satisfy GATE-01 |
| ClickHouse public playground | **yes** | **yes** | **none** | the instrument |
| PyPI BigQuery | yes | yes | GCP account | recorded fallback |
| GitHub release-asset counts | n/a | n/a | `gh auth` | **answers research Q4 "no"** — cumulative only, no time series, no client-version dimension |

</domain>

<decisions>
## Implementation Decisions

### GATE-01 — the instrument's form

- **D-01:** **A committed, runnable shell script at `tools/adoption/`, not a recorded query recipe.**
  GATE-01 says the instrument *reports*; that reads as something runnable. Re-deriving a multi-table
  ClickHouse query from prose a year from now is exactly the "re-derive every call" failure Phase 192's
  D-01 rejected. It sits beside the existing `tools/catalog/`, which is `tools/`'s only other occupant.
  **Shell, not Python:** the whole instrument is one `curl -G` with a URL-encoded SQL query. No
  dependency on the devcontainer's Python, and the query stays legible as the artefact it actually is.
  **An elaborate self-check was offered and declined.** A third option — the script asserting the
  ClickHouse table exists and that `max(date)` is recent, refusing to print a verdict otherwise — was on
  the table and not chosen. Do not reintroduce it. A minimal "did the query return rows at all" guard is
  ordinary correctness and is permitted; a staleness gate is not.
  — **Reversibility:** reversible — one new directory holding one script, no consumer.

- **D-02:** **The honesty lives in the script's own output, every run.** GATE-01 requires the instrument to
  state what it does not measure. That caveat block prints beneath the numbers so the number cannot travel
  alone — not into an issue, not into a plan, not into a session a year from now where nobody opened the
  note. The record carries the reasoning; the output carries the limit.
  **The caveat must include the sharpest form of it, established during this discussion:** a download of a
  stranded version *today* is a **new acquisition** of an old version — a pin, a cache, a stale tutorial.
  A genuinely stranded user who installed 2.0.7 in March and never reinstalls generates **zero** downloads
  and is invisible to every instrument considered. So the threshold certifies *"new acquisition of stranded
  versions has effectively stopped"* — a necessary condition, never a sufficient one. Installed base is not
  observable; download share is a proxy; the never-upgrade residual survives any threshold.

- **D-03:** **One data source, with the fallbacks recorded rather than built.** The script targets
  ClickHouse only. The record names the two alternatives and what each costs — PyPI BigQuery (per-version,
  needs a GCP account) and the raw `pypi.pypi_raw` table — so whoever meets a dead endpoint has a route
  instead of a dead end. A second code path that is never exercised until the day it is needed is a path
  that fails on that day.

### GATE-01 — what the number measures

- **D-04:** **Numerator and denominator are both `installer IN ('pip','uv')`, stable channel only.**
  The at-risk population is default installs; `3.0.0bNN` users already carry the `firestarter_fw` URL from
  `beta` and are not what the gate protects.
  **Unfiltered share measures mirrors, not users.** Last 90 days for `firestarter`: bandersnatch
  **11,672**, unknown **6,739**, Browser **2,194**, requests **1,718**, **pip 740**, Nexus 52, uv 6 — pip
  is **3.2%** of traffic. An unfiltered gate would fire when mirrors finished re-scanning.
  **`uv` joins `pip` by decision, not oversight** (6 downloads in 90 days today). Excluding a
  pip-equivalent human installer would under-count real users and make the gate fire late.

- **D-05:** **The prerelease filter is a PEP 440-shaped regex, not `NOT LIKE '%b%'`.** Exclude
  `match(version, '(a|b|rc)[0-9]|dev')`. `NOT LIKE '%b%'` happens to work on this package's history and
  would silently admit a future `3.0.0rc1` or `2.1.0a1` into the stable denominator.

- **D-06:** **The numerator is any stable `>= 2.0.9`, computed — not an allowlist.** 2.0.9 is the first
  stable carrying the `firestarter_fw` URL (verified live on `main` by Phase 191; **2.0.8 never reached
  PyPI**). Later stables inherit it and count automatically with no edit. A named allowlist was declined
  because a forgotten edit makes the gate read permanently un-fired.

- **D-07:** **The at-risk denominator is 2.0.7 specifically, not "everything `<= 2.0.7`".**
  The ancient-version tail is **automation, not stranded humans**, and it dwarfs the signal. By quarter,
  pip+uv stable-channel downloads of pre-2.0.7 versions run **398 / 254 / 320 / 265 / 52** (2025-Q3 →
  2026-Q3) — holding at 250–400 even in quarters *before 2.0.7 existed*, spread 1–4 downloads each across
  ~30 ancient 1.x versions.
  So the gate keys on **2.0.7** — the version `pip install firestarter` actually served from 2026-01-13 to
  2026-09-13. **The record must state that the pre-2.0.7 population is outside the instrument's reach
  entirely**, because the instrument cannot separate a stranded human from a scanner down there. That is
  a real limit, not a rounding choice.

### GATE-01 — the trigger

- **D-08:** **Share AND an absolute floor. Share alone is not a harm bound.**
  A ratio says nothing about how many people are behind it, and the thing that breaks is a count of humans.

- **D-09:** **The number, stated once so no downstream agent re-derives it:**

  > Fixed share of `(>= 2.0.9) / ((>= 2.0.9) + 2.0.7)` is **>= 90%**, **AND** 2.0.7 draws **<= 10**
  > `pip`+`uv` downloads, **both measured over a rolling 90-day window** on the stable channel.

  **Why 90 days and not 30:** monthly stable-channel totals show scraper spikes — **Jan 342** and
  **May 312** against a 34–75 baseline. A 30-day window is swamped by one scraper pass.
  **Why these values:** the 2.0.6 → 2.0.7 transition is the natural experiment. 2.0.7 published
  2026-01-13; pip stable-channel by month — Jan `2.0.6=14 / 2.0.7=33` (70%), Feb `2 / 32` (**94%**),
  Mar `0 / 36` (100%), then 2.0.6 reappears with **2** in May and **1** in July. Share crosses 90% in about
  six weeks and plateaus against a thin tail that never reaches zero. This threshold would have fired
  **~3 months** after that cut. A stricter `>= 95% / <= 5` was declined: at a 30–50/month baseline, 5
  downloads sits inside the scraper noise floor, so the floor leg could stay unsatisfied for reasons
  unrelated to any human. A looser `>= 80% / <= 25` was declined as accepting ~a quarter of new stable
  acquisitions still landing stranded at the moment `fw` breaks.
  **Baseline at authoring time (2026-09-14, 90-day window, pip+uv, stable channel):** FIXED (>= 2.0.9)
  **17** · 2.0.7 **116** · older-stable tail **52**. Fixed share of the at-risk pair = **12.8%**. Nowhere
  near firing, and the record should say so plainly.

- **D-10:** **A single 90-day reading suffices — not two consecutive ones.** The window already damps the
  spikes D-09 names, and D-7 puts a human in front of the destructive act regardless. A second automated
  confirmation adds delay without adding judgement. (Overlapping 90-day windows also make "consecutive"
  ambiguous.)

- **D-11:** **The trigger carries a re-examination date, not an auto-fire.**
  **2027-09-13** — twelve months from 2.0.9's publish, four times the headroom the 2.0.6 → 2.0.7 precedent
  needed. If the trigger has not fired by then, the **premise** is re-examined: maybe the threshold was
  wrong, maybe the front-door problem was solved another way, maybe 2.0.7 acquisition is structural. It
  **never** fires the destructive act on a date — that would reintroduce exactly the calendar gating the
  seed rejects ("gate on that stable having shipped and having displaced 2.0.7 — not on a calendar date").
  This answers `.planning/seeds/phase-gate-expiry-discipline.md` for this gate: a dormant seed with no
  review point is the accumulation pattern Phase 188 had to clear by deletion.
  A third option — also naming a fallback if the trigger proves unreachable — was declined as designing a
  branch that may never be walked, inside a phase scoped to measurement.

- **D-12:** **The seed's `trigger_condition:` frontmatter is rewritten to carry D-09's numbers verbatim.**
  ROADMAP criterion 1 requires precisely this: a threshold and an observation window rather than "once
  adoption has moved". The seed's prose sections are updated to match, and **2.0.7 → 2.0.9 corrections are
  applied throughout** — the seed was planted 2026-09-13 before the stable shipped and still says a stable
  "has shipped" in the future tense. Its "Do not fire this while any of these is untrue" checklist is now
  satisfied on all three legs (URL-01/02, STABLE-01, RENAME-02) and should say so.
  — **Reversibility:** reversible — frontmatter and prose in one dormant seed file.

### GATE-02 and GATE-03 — where the rules live

- **D-13:** **`CLAUDE.md` carries both rules; the mechanisms live in notes it cites.**
  `CLAUDE.md` already runs exactly this pattern — its "Milestone close and branch protection" section
  states rules in-line and points at `.planning/notes/v135-close-procedure-under-protection.md` for the
  mechanics. It is also the only location guaranteed to be in front of an agent *before* it acts.
  **Why not the seed and the impact-analysis note alone:** both already carry the Release rule, but both
  are reached only by someone already working on the rename. A milestone close that publishes a Release
  for unrelated reasons meets neither.
  **Why not `REQUIREMENTS.md` or `ROADMAP.md`:** both are archived into `.planning/milestones/` at close,
  where D-5 makes them historical-by-intent. Anything recorded only there is gone.

- **D-14:** **GATE-02's mechanism is cited, not restated.**
  `.planning/notes/999.9-repo-rename-impact-analysis.md` § "Standing rule this must produce" already
  carries the full `_compare_versions` walkthrough — a `v1.36` tag parses as PEP 440 `1.36`, so
  `Version("3.0.0b29") >= Version("1.36")` reads **true** and `fw` reports firmware current forever.
  `CLAUDE.md` states the rule and why it is not cosmetic, and cites that section. **One source of truth,
  no drift.** Writing a new standing-rules note was declined (a third file for one rule, and it edits a
  completed phase's analysis); restating the mechanism in full inside `CLAUDE.md` was declined (a 77-line
  onboarding brief absorbing a paragraph of version-parsing detail, plus a second copy that can drift).

- **D-15:** **GATE-03 gets a pointer in `CLAUDE.md`'s repo-structure area plus a dedicated note.**
  Its reader is different from GATE-02's — someone checking out `v1.35` or bisecting firmware history, not
  someone closing a milestone — and archaeology sessions start from `CLAUDE.md`. The note carries both
  workarounds **and their transcripts**. `.planning/codebase/STRUCTURE.md` was declined as the sole home:
  it is read when mapping the repo, not when a clone has already gone wrong. `.devcontainer/README.md` was
  declined as a second home: it addresses container setup, not historical checkouts.

### Claude's Discretion

Settled mechanically during discussion, without consuming an operator question. Recorded as locked, not as
open latitude:

- **D-16:** **GATE-03's "demonstrated" means executed, with transcripts committed.** Both cases are run for
  real — an existing clone (`git config submodule.firestarter.url` in `.git/config` overriding
  `.gitmodules`) and a fresh clone at a pre-rename ref (`--no-recurse-submodules` plus a manual URL set) —
  and the transcripts land under `${phase_dir}/evidence/`. Settled by precedent, not preference: RENAME-03
  required *"demonstrated, not reasoned about"*, and Phase 191 proved STABLE-02 with a RED/GREEN fixture
  pair rather than an argument. A reasoned-only GATE-03 would be the one weaker leg in the milestone.
  **The pre-rename ref must be chosen to actually reproduce the trap** — a commit whose `.gitmodules`
  still reads `url = git@github.com:henols/firestarter.git`, i.e. before Phase 189 landed RENAME-02.
  **Today the trap does not yet bite** (the old slug still redirects, D-1 holds), so the demonstration
  shows the *mechanism* and its fix, and must say plainly that the failure it prevents arms only when the
  claim fires. Do not write a transcript that claims a breakage that has not happened.

- **D-17:** **No comments in the shell script beyond what a reader of `tools/` needs.** The operator's hard
  rule — no comments in source, ever, not overridable by a plan — is scoped in `CLAUDE.md` to
  `firestarter/` and `firestarter_app/`. Meta `tools/` is outside it, so the SQL query may be explained.
  **GSD process commentary is still forbidden everywhere:** no `# Phase 193`, no `# GATE-01`, no plan or
  milestone citations. Rationale belongs in `SUMMARY.md`.

- **D-18:** The todo cross-reference is **not** folded — see `<deferred>`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and scope
- `.planning/REQUIREMENTS.md` §GATE — GATE-01, GATE-02, GATE-03, verbatim.
- `.planning/REQUIREMENTS.md` §"Decisions taken at activation" — D-1 (stops before the claim), D-4 (never
  publish a Release), D-6 (the trap is documented, not solved), D-7 (operator-gated).
- `.planning/ROADMAP.md` §"Phase 193: The Deferred Claim, Made Measurable" — goal and the four success
  criteria. Criterion 1 is what D-09 and D-12 satisfy; criterion 2 is what D-02 and D-07 satisfy.

### The subject matter — read all three before writing anything
- `.planning/seeds/SEED-claim-firestarter-slug.md` — **the file this phase rewrites.** Its
  `trigger_condition:` frontmatter is the artefact criterion 1 names. Planted 2026-09-13, before 2.0.9
  shipped; its tense and its `2.0.7` references need D-12's correction pass.
- `.planning/notes/999.9-repo-rename-impact-analysis.md` §"Standing rule this must produce" — the
  `_compare_versions` walkthrough GATE-02 cites (D-14). **Do not duplicate it.**
- `.planning/notes/999.9-repo-rename-impact-analysis.md` §"The `.gitmodules` archaeology trap" — the
  two workarounds GATE-03 must demonstrate (D-16), already written out.
- `.planning/research/questions.md` — the four questions this phase answers. **Q1 answered:** pypistats has
  no per-version endpoint; ClickHouse does, without credentials. **Q2 answered:** D-09's natural
  experiment. **Q3 answered:** D-09. **Q4 answered "no":** GitHub release-asset counts are cumulative
  only, with no time series and no client-version dimension — verified against
  `repos/henols/firestarter_fw/releases` (assets read 0–2 downloads each).

### Files the phase edits or creates
- `tools/adoption/` — **new.** The instrument (D-01).
- `CLAUDE.md` — two additions: GATE-02's rule in the close/branch-protection section (D-13, D-14), and
  GATE-03's pointer near the repository-structure material (D-15).
- `.planning/notes/` — **one new note** for the `.gitmodules` trap (D-15), carrying the transcripts of
  D-16.
- `.planning/seeds/SEED-claim-firestarter-slug.md` — frontmatter and prose (D-12).

### Prior-phase decisions this phase inherits
- `.planning/phases/191-.../191-VERIFICATION.md` — establishes that the published stable is **2.0.9**,
  that it carries the `firestarter_fw` URL on `main`, and that **2.0.8 never reached PyPI**. D-06's cut
  point comes from here.
- `.planning/phases/192-live-references-only/192-CONTEXT.md` — D-01's record/act-on test (the reason the
  instrument goes in `tools/` and not `.planning/`), and D-08's precedent for **declaring** an unbuilt
  guard rather than shipping one that fails open.
- `.planning/seeds/phase-gate-expiry-discipline.md` — answered for this gate by D-11.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **The ClickHouse query itself, already validated during this discussion.** Table
  `pypi.pypi_downloads_per_day_by_version_by_installer_by_type`, endpoint
  `https://sql-clickhouse.clickhouse.com/` with `--data-urlencode "user=play"`, `FORMAT TSV`. Every figure
  in `<decisions>` came from it. **Do not re-derive the schema** — sibling tables exist for country,
  python version, system and file type, and the installer table is the one that matters.
- **`tools/catalog/`** — the only existing occupant of meta `tools/`. `codegen.py` plus
  `sync_to_subrepos.sh` set the precedent that a tracked, runnable, CI-less tool lives here.
- **Per-phase `evidence/` directories** — 189, 190, 191 and 192 each committed their transcripts under
  `${phase_dir}/evidence/`. D-16's two workaround transcripts follow that shape.

### Established Patterns
- **`CLAUDE.md` states a rule in-line and cites a note for its mechanism.** The existing "Milestone close
  and branch protection" section is the template D-13 and D-14 follow.
- **Demonstrated, not reasoned about.** RENAME-03 and STABLE-02 both required execution over argument.
  D-16 applies it to GATE-03.
- **`/usr/bin/grep`, never PATH `grep`.** The devcontainer's `grep` is ugrep and honours `.gitignore`,
  silently under-scanning. Load-bearing in 189–192 and in any sweep this phase runs.

### Integration Points
- **`new-milestone.md:79` globs `ls .planning/seeds/SEED-*.md`.** Verified 2026-09-14:
  `SEED-claim-firestarter-slug.md` is the **only** seed in the directory that matches. The other 13 use
  the bare-slug form `/gsd-explore` writes and have never surfaced at a milestone start (filed as
  `.planning/todos/pending/explore-seeds-invisible-to-new-milestone-glob-mismatch.md`, 2026-08-20). So
  the seed genuinely does reach a future milestone — which is what makes D-12's rewrite load-bearing
  rather than decorative. **This phase does not fix the glob defect** — see `<deferred>`.
- **The meta repository has no `.github/workflows/` at all.** Nothing will run the instrument on a
  schedule, and nothing will notice if it rots. That is accepted, not overlooked (D-01, D-03).

</code_context>

<specifics>
## Specific Ideas

- The operator selected the recommended option on every question in this discussion, including where the
  recommendation carried a cost the alternative avoided. Read that as endorsement of the stated rationale,
  not as indifference — each recommendation named what it was buying and what it was paying.
- **An elaborate self-check was explicitly offered and declined** (D-01). A planner adding staleness gates,
  scheduled runs, CI scaffolding or a second data path is working against a choice already made.
- The framing the operator accepted for the caveat is the strong one: the instrument certifies that **new
  acquisition** of stranded versions has stopped, which is necessary and not sufficient, because a truly
  stranded user emits no downloads at all. Any weaker phrasing in the delivered artefacts is a regression
  against criterion 2.

</specifics>

<deferred>
## Deferred Ideas

- **Fixing `new-milestone.md`'s seed glob.** The consumer globs `SEED-*.md` while `explore.md` writes
  `{slug}.md`, and the miss is silent — 13 seeds have never surfaced. It does not block this phase
  (`SEED-claim-firestarter-slug.md` matches), `.claude/gsd-core/` is vendored and `/gsd-update` would
  overwrite a local fix, and no GATE requirement asks for it. It stays filed as a todo.
- **Running the instrument on a schedule.** Would need a `.github/workflows/` the meta repository does not
  have, and would put a recurring job behind a gate that will be evaluated a handful of times at most.
- **A second data source for the instrument.** D-03 records the fallbacks rather than building them.
- **Resolving the PyPI/GitHub name incoherence** — after the eventual claim, PyPI `firestarter` is the app
  while GitHub `firestarter` is the meta repo. Already out of scope at milestone level; noted, not
  resolved.

### Reviewed Todos (not folded)

`gsd-tools query todo.match-phase 193` returned **37** matches. **None folded** — the same generic
keyword collision Phase 192 recorded (`firestarter`, `phase`, `rule`, `version`, `gate`), dominated by
firmware defects and host database questions with no relation to the gate surface.

Two were checked properly rather than dismissed on score:

- *"publish.yml's release published trigger is suppressed for bot-created releases"* — concerns the
  **app** repository's publish workflow, filed by Phase 191. GATE-02 is about Releases on the **meta**
  repository. Different repository, different failure, not this phase.
- *"All 13 seeds are invisible to /gsd-new-milestone"* — genuinely adjacent, and checked live rather than
  assumed: this phase's seed **does** match the consumer glob, so the surfacing path GATE-01 depends on
  works. Deferred above.

</deferred>

---

*Phase: 193-the-deferred-claim-made-measurable*
*Context gathered: 2026-09-14*
