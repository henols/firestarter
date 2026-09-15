# Phase 190: Endpoints That Do Not Depend on a Redirect - Context

**Gathered:** 2026-09-13
**Status:** Ready for planning

<domain>
## Phase Boundary

On `beta`, nothing in the host application reaches the firmware repository through a redirect; the test
fixtures are structurally tied to the shipped constants so a future retarget cannot pass silently; and a
broken endpoint is distinguishable in `fw`'s output — and in its exit code — from "already up to date".
Covers **URL-01, URL-03, URL-04**.

The phase depends on Phase 189 only, and Phase 191 repeats the constant change on `main` as a separate
change against a branch 948 commits behind.

**In scope:** the three `FIRESTARTER_*_URL` constants in `firestarter_app/firestarter/constants.py` on the
milestone branch; the two hardcoded fixtures at `firestarter_app/tests/test_firmware_install.py:383,494`
plus the pin that makes a constant edit fail; the `fw` update path's dead-endpoint behaviour; the
`fw --list` path's failure/empty distinction; the firmware-slug references inside the `firestarter_app`
working tree (D-04); and the live end-to-end demonstration plus the local CI-equivalent transcript.

**Out of scope (settled at activation or in Phase 189, not re-litigated here):** `main` and the stable cut
(Phases 191, STABLE-01/02); claiming `henols/firestarter` (D-1); mirroring firmware releases (D-2); the
meta repository's `README.md` and its five `.planning/codebase/` documents (SWEEP-01, Phase 192); anything
under `.planning/milestones/` (D-5, and Phase 192 must prove a diff over that path is empty); the
repository-wide regression guard (D-10 from Phase 189, deferred to Phase 192); the `.gitmodules` history
trap (D-6, documented in Phase 193); `SUBMIT_REPO` itself, which correctly targets `firestarter_prom` and
whose redirect is permanent.

</domain>

<decisions>
## Implementation Decisions

### Fixture derivation and the pin (URL-03)

- **D-01:** URL-03 has **two halves that are different tests**. Derivation removes the duplicated literal:
  rewrite both `next_url` fixtures at `tests/test_firmware_install.py:383` and `:494` as f-strings off
  `FIRESTARTER_RELEASES_URL`. The **pin** is what satisfies criterion 2's "fails when the constant is
  edited alone": one **independently written** test asserting all three `FIRESTARTER_*_URL` constants carry
  `henols/firestarter_fw`.
  **Why derivation alone is insufficient — the planner must not treat this as belt-and-braces:** the two
  sites are mock pagination `next_url`s that are fed back into the mock and **never asserted**. An f-string
  off the constant therefore *tracks* any edit, and the test stays green on exactly the change criterion 2
  exists to catch. That is a tautology, not a guard.
- **D-02:** The pin is a **positive** assertion on `henols/firestarter_fw`. It does **not** carry a negative
  assertion against the bare slug: `henols/firestarter` is a **substring** of `henols/firestarter_fw`, so a
  naive negative check is either vacuous or wrong. The boundary-aware pattern that distinguishes the bare
  slug from `firestarter_fw` / `firestarter_app` / `firestarter_prom` belongs to SWEEP-01/02 in Phase 192
  (Phase 189 D-10).
- **D-03:** The pin asserts the **slug**, not each constant's full URL verbatim. A full-string pin would
  have to be edited for any legitimate path change, including the `{tag}` template.

### Scope boundary against Phase 192 (carried from Phase 189 D-09)

- **D-04:** **Phase 190 owns the `firestarter_app` working tree's firmware-slug references outright.**
  Phase 192 sweeps the meta repository and re-verifies the app repository as already-clean. Beyond the
  three constants and the two fixtures, that is two sites measured 2026-09-13:
  - `firestarter_app/firestarter/submit.py:59` — a comment naming `henols/firestarter` in the list of
    repositories where issue creation is disabled. `SUBMIT_REPO` on line 63 is correct and is **not**
    touched.
  - `firestarter_app/.planning/codebase/INTEGRATIONS.md:8` — names the endpoint and the constant that
    defines it. The app repository tracks its **own** `.planning/codebase/`.

  **Why this is decided here rather than deferred:** SWEEP-01 enumerates the *meta* repository's five
  `.planning/codebase/` documents and "both sub-repo READMEs". Neither of the two sites above is named by
  path in SWEEP-01, and neither is a "test, fixture or docstring" under this phase's criterion 1 — so
  without D-04 they fall through both phases, exactly the gap Phase 189's D-09 was written to close. Phase
  190 is already committing inside `firestarter_app`, so this costs nothing.
- **D-05:** **No new repository-wide regression guard is added here.** Cleanliness is proved with a
  `/usr/bin/grep` sweep at verification time. Phase 189's D-10 applies unchanged: a standing check needs the
  boundary-aware pattern that is Phase 192's to build, and source-scanning gates in this project have a
  history of failing **open** after renames.

### Dead-endpoint behaviour (URL-04, update path)

- **D-06:** When a firmware release cannot be resolved and a board **has** been identified,
  `manage_firmware_update` returns `False` so `fw` exits 1, and emits one operator-visible message naming
  the **endpoint URL** and the **board**.
  **Measured current behaviour:** `fetch_release_info` returns `(None, None)`, `is_up_to_date` stays
  `False`, every install branch requires `latest_version` and so none fires, and control reaches
  `return True` at `firestarter_app/firestarter/firmware.py:940` → `sys.exit(0 if ok else 1)` at
  `firestarter_app/firestarter/cli_handlers.py:1266`. The command exits **0**.
  **Why the blast radius is narrow:** no `.sh` script and no workflow in either sub-repository invokes
  `fw`, and no test asserts the current `True` — `TestManageFirmwareUpdate` covers no-port, up-to-date and
  no-current-no-intent, leaving this branch uncovered. With no board identified and no install intent the
  method already returns `False`.
  — **Reversibility:** costly — an exit-code change to a shipped CLI command is a behavioural contract for
  any operator or script that reads it, and Phase 191 carries the same change to the default install.
- **D-07:** **One message covers both** URL-04 conditions — unreachable, and reachable-but-no-asset-for-this-
  board. The `(None, None)` contract of `fetch_release_info` / `fetch_latest_release_info` is **not**
  widened: no typed exception, no third return value, no result object. The two pre-existing distinct
  `logger.error` lines inside the fetch functions remain for a reader who wants the cause.
  **Why:** widening the contract would touch every monkeypatched 2-tuple stub — at minimum
  `tests/test_py32_dfu.py`, `tests/test_fw_port_targeting_and_blind_install.py`,
  `tests/test_fw_update_path_gate.py` and `TestManageFirmwareUpdate` — for output detail the operator can
  already read one line up.
- **D-08:** **Constraint — `--force` already exits 1 on a dead endpoint.** `should_install_now` is `True`
  under force, so the guard at `firestarter_app/firestarter/firmware.py:911-915` fires first with
  *"Cannot install: latest firmware URL or version for {board} is not available."* The new check must
  **not** double-emit on the force path.

### `fw --list` (URL-04, list path)

- **D-09:** **`fw --list` is inside URL-04's scope.** A fetch failure emits a named error and exits 1; a
  genuinely empty result prints a "No releases found for board {board}" line and exits 0.
  **Measured current behaviour:** `list_releases` catches `requests.RequestException` (which covers the
  404, since `raise_for_status` raises `HTTPError`), logs, and returns `[]`; the handler then prints the
  header row, zero rows, and `sys.exit(0)`. A dead endpoint and a board with no releases are the same
  output but for one log line.
  **Why it is in scope despite criterion 3's wording:** criterion 3's "not mistakable for already up to
  date" cannot literally apply to `--list`, which never prints that — but URL-04's requirement text is
  "`fw` reports a clear, actionable error", and `--list` is `fw`. Decisive: **criterion 4's evidence is
  most naturally `fw --list` against the renamed repository**, and an instrument that exits 0 when it fails
  cannot serve as proof that the endpoint resolves.
- **D-10:** `list_releases` returns `Optional[List[ReleaseInfo]]` — **`None` = could not fetch, `[]` =
  nothing matched**. No new exception class, and no `requests` import in the CLI layer. One annotation
  change for the mypy watermark gate (scope `firestarter/ tests/`, py3.11). `list_releases` has exactly one
  production caller, the `fw` handler at `firestarter_app/firestarter/cli_handlers.py:1214`; every other
  reference is a test calling it directly.
- **D-11:** `fw --list --json` on a fetch failure prints **no document on stdout**, the named error on
  **stderr**, and exits 1. It must never emit a well-formed `[]` describing a state that was not observed —
  `--json` is the machine-readable surface, so that is the silent-success defect in the place most likely
  to be parsed.
- **D-12:** **Constraint — stderr needs an explicit route.** `SingleLineStatusHandler` writes to
  `sys.stdout` (`firestarter_app/firestarter/logging_utils.py:27`), and the default log level is `INFO`
  (`firestarter_app/firestarter/cli_handlers.py:103`), so `logger.error` is already visible **on stdout**.
  D-11's "error to stderr" therefore cannot be a plain `logger.error` call — it needs an explicit stderr
  write or a handler change scoped to that path.
- **D-13:** **Constraint — an existing test must stay green.**
  `firestarter_app/tests/test_cli_handlers.py:657` asserts *"`firestarter fw --list` exits 0 with mocked
  `list_releases` returning `[]`"*. Under D-09/D-10 a genuine empty is still exit 0, which is precisely
  what preserves it. If that test goes red, the failure/empty split has been implemented wrongly.

### Criterion 4 evidence

- **D-14:** The end-to-end demonstration is **four live checks against `henols/firestarter_fw`**:
  1. resolve the **stable** channel and print the version and asset URL;
  2. resolve the **pre** channel and print the version and asset URL;
  3. download one real `.hex` through `_download_firmware_file` and confirm it parses as Intel HEX;
  4. demonstrate **both** URL-04 failures for real — the asset-less case and the unreachable case — showing
     exit 1 and the named message for each.

  No bench, no `avrdude`; the download is the last network step before hardware.
- **D-15:** The **asset-less case needs no mock.** Measured live 2026-09-13: stable `2.0.6` ships only
  `firestarter_leonardo.hex` and `firestarter_uno.hex`, while pre `3.0.0b29` ships all four. So
  `fw --board uno328pb --stable` is a genuine "returns no asset matching the board" against a reachable,
  correctly-named endpoint. The unreachable case is produced by pointing the constant at a non-existent
  slug in a throwaway process.
- **D-16:** The demonstration is a **re-runnable script committed under the phase directory**, plus its
  captured transcript. **Nothing live enters `pytest` and nothing enters CI** — live contract checks run on
  demand, not on every PR, so the suite stays deterministic and offline. Phase 191 re-runs it against the
  stable it cuts; a post-claim milestone re-runs it to watch the 404 arrive. This follows Phase 189's D-06
  precedent, and `189-fresh-clone-fixture.sh` is the shape to mirror.
- **D-17:** Criterion 4's **"Host CI is green"** half is satisfied by running the five `ci.yml` gate steps
  **verbatim** inside a `uv venv --python 3.11` and committing the transcript:
  `pip install -e .[test]` · `ruff check firestarter/ tests/` · `ruff format --check firestarter/ tests/` ·
  `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` ·
  `pip install -e . && firestarter --help`.
  **The py3.11 venv is the substance of this decision, not a detail:** the devcontainer is py3.12 and has
  previously been proven to mask real py3.11 CI breakage on `beta`.
  **Why not a real Actions run:** the milestone branch is **not on origin**, and Host CI triggers on
  `push: branches: ['**']`. A milestone-branch push would fire `ci.yml` only — `beta-release.yml` is
  `beta`-only and `publish.yml` is release-only, so nothing would be published — but a push is
  outward-facing, gated by D-7 and by the standing push-at-ship-time policy. **The phase record must state
  plainly that this is the local equivalent and that the real Actions run happens when the operator pushes
  at ship.**

### Claude's Discretion

- **Placement of the slug-pin test.** Leaning toward a dedicated
  `firestarter_app/tests/test_endpoint_constants.py` rather than burying an endpoint invariant inside
  `test_firmware_install.py` — Phase 191 must port the same change to `main`, which is 948 commits behind
  and may not carry that file in its current shape. Either satisfies D-01.
- The exact wording of the D-06 and D-09 messages, beyond naming the endpoint URL and the board.
- The shape, name and argument handling of the D-16 script, and how its transcript is captured, so long as
  all four checks of D-14 are covered and it is genuinely re-runnable.
- The mechanism for producing D-15's unreachable case in a throwaway process.
- Commit granularity across the constants, the tests, the `fw` behaviour change and the evidence.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope and the decisions that bound this phase
- `.planning/REQUIREMENTS.md` — URL-01, URL-03, URL-04 verbatim; the D-1…D-7 activation decisions table;
  the Out of Scope table. **D-1…D-7 are settled; no plan re-opens them.**
- `.planning/ROADMAP.md` § "Phase 190: Endpoints That Do Not Depend on a Redirect" (≈ lines 308–330) — the
  goal and the four success criteria. § v1.38 milestone header (≈ lines 172–270) — the ordering constraint,
  the branch model, the measured blast radius, and the **"Bench: none"** statement that bounds D-14.
- `.planning/PROJECT.md` § "Current Milestone: v1.38 Repository Rename" (lines 41–112) — the five strands
  and the full D-1…D-7 rationale.

### The immediately prior phase — its decisions are inherited, not re-derived
- `.planning/phases/189-free-the-name/189-CONTEXT.md` — **D-09** (the phase already committing inside a
  repository owns its slug references outright) is the direct parent of this phase's D-04; **D-10** (no
  regression guard; the boundary-aware pattern is Phase 192's) is the parent of D-05; **D-06** (a
  re-runnable script under the phase directory, not a one-off transcript) is the parent of D-16.
- `.planning/phases/189-free-the-name/189-SUMMARY.md` and `189-VERIFICATION.md` — what the rename actually
  landed, and the evidence shape this phase should mirror.
- `.planning/phases/189-free-the-name/fresh-clone-fixture.sh` — the concrete precedent for D-16's script.

### The rename's measured impact
- `.planning/notes/999.9-repo-rename-impact-analysis.md` — the whole note. § "Blast radius" establishes
  that the three constants are consumed **only** by `firmware.py`, so only the `fw` command is at risk;
  that is what bounds this phase.

### The deferred destructive half — this phase must not advance it
- `.planning/seeds/SEED-claim-firestarter-slug.md` — the dormant seed. D-4's no-Releases-on-the-meta-repo
  rule is what keeps the post-claim failure a loud 404 rather than a silent "firmware is current", which is
  the same failure class D-06 addresses on the update path.

### Standing repository rules — binding on every plan in this phase
- `CLAUDE.md` § "Source code comments — hard rule" — **no comments in product source, not overridable by a
  plan, a task, a skill, or a subagent instruction.** This phase edits `constants.py`, `firmware.py`,
  `cli_handlers.py` and test files; rationale goes in `SUMMARY.md` or the commit message, never in source.
  Click docstrings are user-facing `--help` text and are **not** comments.
- `CLAUDE.md` § "Milestone close and branch protection" — `main` is protected in all three repositories;
  this project's close targets `beta`, not `main`.
- `.planning/notes/v135-close-procedure-under-protection.md` — how changes land on protected branches, for
  anyone tempted to short-circuit D-17.

### The CI contract this phase must satisfy
- `firestarter_app/.github/workflows/ci.yml` — the five gate steps and the py3.11 pin that D-17 reproduces.
  Note `paths-ignore` excludes `**.md`; this phase changes `.py`, so CI would fire.

</canonical_refs>

<code_context>
## Existing Code Insights

### Measured facts — do not re-measure, cite these

Captured 2026-09-13 against the live GitHub API and the `firestarter_app` working tree on
`v1.38-repository-rename`.

**The three constants** (`firestarter_app/firestarter/constants.py`), all still bare-slug:

| line | constant | value |
|---|---|---|
| 8 | `FIRESTARTER_RELEASE_URL` | `.../repos/henols/firestarter/releases/latest` |
| 12 | `FIRESTARTER_RELEASES_URL` | `.../repos/henols/firestarter/releases` |
| 14 | `FIRESTARTER_RELEASE_BY_TAG_URL` | `.../repos/henols/firestarter/releases/tags/{tag}` |

**Consumed only by `firmware.py`** — lines 251, 295 and 341 respectively. No other module imports them.
`firestarter_app/build/lib/` carries stale copies and is **untracked**; ignore it.

**No test references any of the three constants today** — `git grep FIRESTARTER_RELEASE -- tests/` is
empty. D-01's pin is therefore new surface, not a modification.

**The two fixture sites are mock pagination `next_url`s**, not assertions:
`tests/test_firmware_install.py:383` (a literal) and `:494` (an f-string over `i`). Both are handed to
`mock_releases_factory` and fed back through the `Link: rel="next"` follow in `_fetch_all_releases`.

**Live release state on `henols/firestarter_fw`:**

| channel | resolves to | assets |
|---|---|---|
| stable (`/releases/latest`) | `2.0.6` | `firestarter_leonardo.hex`, `firestarter_uno.hex` |
| pre | `3.0.0b29` | `leonardo`, `py32f071`, `uno`, `uno328pb` |

The stable release's missing `uno328pb` and `py32f071` assets are what make D-15's asset-less
demonstration real rather than mocked.

**`fw` exit wiring:** `cli_handlers.py:1266` is `sys.exit(0 if ok else 1)`; the `--list` and `--dfu-probe`
paths exit earlier and independently.

**Nothing scripted invokes `fw`** — no `.sh` and no workflow in either sub-repository.

**Logging:** default level `INFO` (`cli_handlers.py:103`), and `SingleLineStatusHandler` writes to
`sys.stdout` (`logging_utils.py:27`). `logger.error` is visible today; it is the silent `return True`
after it that is the defect.

**The milestone branch is not on origin** in `firestarter_app`. All three repositories are on
`v1.38-repository-rename`.

### Established patterns this phase inherits

- **Executors commit inside the submodule**, on the milestone branch; the meta repository re-pins the
  gitlink. The gitlink is advanced **per phase** (the norm since v1.36).
- **Pushes happen at ship time, never ad hoc**, and D-7 makes every outward-facing step operator-gated.
  D-16 and D-17 are both chosen so this phase needs no push.
- **Evidence lives under the phase directory** and is re-runnable where it reasonably can be (Phase 189
  D-06).
- **Host CI is py3.11 only**; the devcontainer is py3.12 and has been proven to mask real CI breakage.
  D-17's `uv venv --python 3.11` exists for that reason.

### Integration points

- `firestarter_app/firestarter/constants.py:8,12,14` — URL-01.
- `firestarter_app/tests/test_firmware_install.py:383,494` — URL-03 derivation.
- A new (or existing) test module — URL-03's pin, per Claude's Discretion.
- `firestarter_app/firestarter/firmware.py` — the `manage_firmware_update` fall-through at line 940
  (D-06/D-07/D-08) and `list_releases` (D-09/D-10).
- `firestarter_app/firestarter/cli_handlers.py:1206-1226` — the `--list` / `--json` output and exit paths
  (D-09/D-11/D-12).
- `firestarter_app/firestarter/submit.py:59` and `firestarter_app/.planning/codebase/INTEGRATIONS.md:8` —
  D-04.
- The phase directory — D-16's script and transcript, and D-17's CI-equivalent transcript.

### Explicitly NOT integration points for this phase

- `firestarter_app/firestarter/submit.py:63` (`SUBMIT_REPO`) — targets `firestarter_prom`, whose redirect
  is permanent. Correct as written.
- Anything on `main` in any repository — Phase 191.
- The meta repository's `README.md` and its five `.planning/codebase/` documents — SWEEP-01, Phase 192.
- Anything under `.planning/milestones/` — D-5; Phase 192 must prove a diff over that path is empty.
- Any `.github/workflows/` file — no workflow hardcodes a repository slug. 999.9's "CI/release workflows"
  clause is a **no-op**. `ci.yml` is *read* for D-17, never edited.

</code_context>

<specifics>
## Specific Ideas

- **The failure message must name the URL, not just the failure.** URL-04's second stated purpose is making
  a mistaken retarget visible rather than silent, and an operator who mistyped a slug learns that only from
  seeing the endpoint that was actually addressed.
- **D-16's script must print what it resolved**, not merely exit 0 — the same reasoning Phase 189 applied
  to its clone demonstration. An exit code cannot distinguish "resolved `firestarter_fw`" from "followed a
  redirect", and this whole phase exists to eliminate the redirect.
- **The D-14 failure demonstrations belong in the same script as the success checks.** A transcript showing
  the endpoint answering *and* both failure modes producing exit 1 with distinct messages is one coherent
  piece of evidence for criteria 3 and 4 together.

</specifics>

<deferred>
## Deferred Ideas

- **A repository-wide bare-slug regression guard for `firestarter_app`.** Declined here under D-05; the
  boundary-aware pattern is Phase 192's to build (SWEEP-01/02). Worth noting that source-scanning gates in
  this project fail **open** after renames, so the guard's own test must plant a violation and see it go
  red.
- **Granular exit codes for `fw`** (e.g. 1 for runtime failure, 2 for user error) rather than the binary
  0/1 split. Some CLIs do this, but the binary split is the safe default and nothing in URL-04 asks for
  more. Would be a separate behavioural decision affecting every `firestarter` subcommand, not just `fw`.
- **A JSON error schema for `fw --list --json`.** D-11 chose "no document on stdout" over emitting
  `{"error": ...}`, which would give parsers a reason without reading stderr. Reconsider only if a machine
  consumer appears.
- **`firestarter/tests/meta_presence.py` and `submit.py:59` carry GSD provenance in their comments and
  docstrings** — exactly what `CLAUDE.md`'s hard rule targets, already tracked as todo
  `2026-08-27-strip-gsd-provenance-comments-from-source.md`. **This phase changes the slug inside
  `submit.py:59` and nothing else**; stripping the provenance is that todo's job.
- **Adding the live end-to-end check to `pytest` behind an opt-in marker.** Declined under D-16 — it would
  fail confusingly for anyone running the full suite without deselecting it. Revisit if Phase 191 or 193
  wants to invoke the check by test name.

### Reviewed Todos (not folded)

`todo.match-phase 190` returned 34 matches out of 35 pending todos. **All 34 are keyword noise** — the
top 14 score 0.9 on the bare word `firestarter` (plus generic terms like `test`, `firmware`, `phase`),
and none touches a repository slug, a release endpoint, or the `fw` command. Representative:

- *Skip VPP error/warning checks when VPP is unused* — firmware behaviour; v1.38 changes no firmware source.
- *Drive outputs/pins to a safe state on power-up and on ANY fault* — firmware behaviour; same reason.
- *Add a `dev test` flag that files the issue automatically* — host app, but the `submit.py` surface, and
  unrelated to firmware release endpoints.
- *Strip residual GSD provenance comments from product source* — adjacent (this phase edits a line inside
  such a comment), but a repo-wide hygiene sweep; folding it would widen a three-requirement infrastructure
  phase. See the Deferred Ideas entry above.

None folded.

</deferred>

---

*Phase: 190-Endpoints That Do Not Depend on a Redirect*
*Context gathered: 2026-09-13*
