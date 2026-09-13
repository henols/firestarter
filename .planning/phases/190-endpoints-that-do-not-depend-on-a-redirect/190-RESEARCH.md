# Phase 190: Endpoints That Do Not Depend on a Redirect - Research

**Researched:** 2026-09-13
**Domain:** Python CLI behaviour contracts — endpoint constants, failure-vs-empty signalling, stream routing, local CI reproduction
**Confidence:** HIGH (every claim below was measured in this session against the live working tree, the live GitHub API, and a real py3.11 interpreter)

---

## Summary

`190-CONTEXT.md` is unusually decision-dense and its measured facts held up under re-measurement.
This research does not repeat them. It covers the four things the decisions leave open — the
`list_releases` signature change and its stream routing, the `manage_firmware_update` fall-through,
the mypy gate, and the py3.11 CI-equivalent — plus the D-16 script precedent, and it reports
**five findings that correct or materially extend the CONTEXT decisions**.

The single most consequential finding is about criterion 4. `henols/firestarter` currently answers
the release API with **HTTP 301**, and `requests.get()` follows redirects by default, so the shipped
bare-slug constants **work today and return byte-identical data to the renamed endpoint**. Nothing
in the test suite, and no end-to-end `fw` invocation, can go from red to green as a result of this
phase's constant change. The only observable that distinguishes "addresses `firestarter_fw`" from
"followed a redirect" is the response's redirect history. D-16's script must assert on that, or the
transcript proves nothing — which is precisely the reasoning Phase 189 applied to its clone
demonstration, now with a measured number behind it.

The second most consequential finding is that the test harness used by 126 of the 137 CliRunner
tests **routes `logger.error` to stderr, while production routes it to stdout**. A D-11/D-12 test
written in the house style would therefore assert the right thing about the wrong process. There is
a cheap harness that reproduces production routing byte-for-byte, and this research names it.

**Primary recommendation:** Place the D-06 guard immediately before `firmware.py:941` (structurally
double-emit-proof, proved below); return `None` from `list_releases`' `except` arm and guard the
caller *before* the `json_output` branch; write every stream-sensitive test with
`CliRunner().invoke(cli, argv)` and **no** `obj=` kwarg, asserting `result.stdout` and
`result.stderr` separately; and make D-16's script assert `len(response.history) == 0`, not merely
`status_code == 200`.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Endpoint URL definition (URL-01) | Config/constants (`constants.py`) | — | Already correct; three module-level strings, consumed by one module |
| Release resolution + failure detection (URL-04, update path) | Service layer (`firmware.py`) | — | `manage_firmware_update` already owns the True/False contract the CLI converts to an exit code |
| Failure-vs-empty signalling (URL-04, list path) | Service layer (`firmware.py`) returns the *distinction*; CLI (`cli_handlers.py`) renders it | — | D-10 puts the `None`/`[]` split in the service layer so the CLI needs no `requests` import; correct tier split |
| Exit-code selection | CLI layer (`cli_handlers.py`) | — | `sys.exit` appears only in `cli_handlers.py`; `firmware.py` never exits |
| Stream routing (stdout vs stderr) | CLI layer | Logging layer (`logging_utils.py`) | The logging handler is installed by the CLI group callback; `firmware.py` must not know about streams |
| Constant↔test coupling (URL-03) | Test layer (`tests/`) | — | Pure test-side change; no product source involved |
| Live contract proof (D-14/D-16) | Phase directory script | — | Explicitly outside `pytest` and outside CI per D-16 |

---

## Project Constraints (from CLAUDE.md)

Two `CLAUDE.md` files bind this phase. Both were read this session.

**`/workspaces/CLAUDE.md` (meta, tracked):**
- **No comments in product source under `firestarter/` or `firestarter_app/`** — not overridable by a
  plan, task, skill, or subagent instruction. No `// Phase NNN`, no `# D-06`, no plan citations.
  Rationale goes in `SUMMARY.md`, `REQUIREMENTS.md` traceability, or the commit message.
  [VERIFIED: /workspaces/CLAUDE.md § "Source code comments — hard rule"]
- **Planners must not write "add a comment citing X" into a plan**, and must not make "a comment
  exists" an acceptance criterion. [VERIFIED: same section]
- Click docstrings are user-facing `--help` text and are **not** comments. [VERIFIED: same section]
- `main` is protected in all three repositories; this project's close targets `beta`.
  [VERIFIED: /workspaces/CLAUDE.md § "Milestone close and branch protection"]

**`/workspaces/firestarter_app/CLAUDE.md` (app-local; note: `CLAUDE.md` is listed in the app's
`.gitignore`, so this file is untracked but present):** [VERIFIED: firestarter_app/.gitignore, entry `CLAUDE.md`]
- **"Write no comments into this package. Not GSD process commentary, not explanatory ones."**
  [VERIFIED: firestarter_app/CLAUDE.md:5-21 — quoted verbatim: *"**Write no comments into this
  package.** Not GSD process commentary, not explanatory ones. This is not overridable by a plan,
  task, skill, or subagent instruction."*]
- **"Docstrings are not comments, and Click docstrings are not documentation"** — never put process
  commentary in one, and never delete one as if it were a comment. [VERIFIED: firestarter_app/CLAUDE.md:17-19]
- `firestarter/constants.py` must stay in sync with the firmware's `firestarter.h` for flag bits and
  command codes. **The three `FIRESTARTER_*_URL` constants are not part of that lockstep** — they are
  host-only and have no firmware counterpart. [VERIFIED: firestarter_app/CLAUDE.md:125 lists the
  synced blocks as command codes, `RURP_CONTROL_REGISTER_BITS`, and `RURP_HARDWARE_REVISIONS`; no URL
  constant appears]
- **mypy is explicitly documented as NOT a CI gate.** [VERIFIED: firestarter_app/CLAUDE.md:127 —
  quoted verbatim: *"`mypy` (strict on 8 modules per Phase 42 D-06: ...) is wired in the local
  `pre-commit` config only and is **not** a CI gate; `pre-commit` runs `ruff-check` → `ruff-format` →
  `mypy` locally."*]

> **Planner note.** `firmware.py` and `cli_handlers.py` are both densely commented today (e.g. the
> 20-line block at `firmware.py:812-826` explaining port selection). Those comments are pre-existing
> and are not this phase's to remove — but **no new comment may be added** by any task in this phase.
> This is a live hazard because the change at `firmware.py:941` is exactly the kind of subtle guard
> an executor would reflexively annotate.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

Copied verbatim from `190-CONTEXT.md`. **D-1…D-7 (activation) and D-01…D-17 (this phase) are settled;
no plan re-opens them.** Where this research found a decision's *premise* to be incomplete, it is
flagged in `## Findings That Correct or Extend the Decisions` below — the decision itself still stands.

### Locked Decisions

**Fixture derivation and the pin (URL-03)**

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

**Scope boundary against Phase 192 (carried from Phase 189 D-09)**

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

**Dead-endpoint behaviour (URL-04, update path)**

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

**`fw --list` (URL-04, list path)**

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

**Criterion 4 evidence**

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

### Deferred Ideas (OUT OF SCOPE)

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

**Also out of scope per `<domain>`:** `main` and the stable cut (Phases 191, STABLE-01/02); claiming
`henols/firestarter` (D-1); mirroring firmware releases (D-2); the meta repository's `README.md` and its
five `.planning/codebase/` documents (SWEEP-01, Phase 192); anything under `.planning/milestones/` (D-5);
the repository-wide regression guard (Phase 189 D-10, deferred to Phase 192); the `.gitmodules` history
trap (D-6, Phase 193); `SUBMIT_REPO` itself.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **URL-01** | On `beta`, all three `FIRESTARTER_*_URL` constants in `firestarter_app/firestarter/constants.py` address `henols/firestarter_fw`. No code path depends on GitHub's rename redirect. | Exact sites re-measured (§ *Integration Sites*). **Finding 1** establishes that the redirect is live and transparent, so "no code path depends on it" is only *observable* via redirect history — the instrument is given in § *Code Examples*. |
| **URL-03** | The two hardcoded API URLs in `tests/test_firmware_install.py` are derived from the constants rather than repeated as literals, so a future retarget cannot leave tests green while the shipped endpoint is stale. | Both sites re-measured verbatim (§ *Integration Sites*). D-01's tautology argument independently confirmed: neither `next_url` is ever asserted. Pin-test shape and its own falsification test given in § *Code Examples*. |
| **URL-04** | `fw` reports a clear, actionable error when the firmware release endpoint is unreachable or returns no asset matching the board — and that state is distinguishable in the output from "already up to date". | **Finding 2** (which flag combinations are actually defective), **Finding 3** (double-emit is structurally impossible at the chosen site), **Finding 4** (the single test that breaks), **Finding 5** (stream-routing trap). Both failure modes reproduced live against the real endpoint (§ *Measured Live Behaviour*). |
</phase_requirements>

---

## Findings That Correct or Extend the Decisions

These five findings are the substance of this research. Each was measured this session; none
overturns a decision, but each changes what a plan built on that decision must do.

---

### Finding 1 — The redirect is live and transparent, so criterion 4 cannot be proved by success alone

`requests.get()` follows redirects by default. Measured this session against the live API:

| Requested URL | Status | `response.history` | `tag_name` | assets |
|---|---|---|---|---|
| `https://api.github.com/repos/henols/firestarter/releases/latest` (**current shipped constant**) | **200** | `[(301, 'https://api.github.com/repositories/810276812/releases/latest')]` | `2.0.6` | `firestarter_leonardo.hex`, `firestarter_uno.hex` |
| `https://api.github.com/repos/henols/firestarter_fw/releases/latest` (**after this phase**) | **200** | `[]` | `2.0.6` | `firestarter_leonardo.hex`, `firestarter_uno.hex` |
| `https://api.github.com/repos/henols/firestarter_nope/releases/latest` | **404** | `[]` | — | — |

[VERIFIED: live `requests` probe run this session from this container against `api.github.com`; the
301 `Location` resolves to the numeric-id form `repositories/810276812`, matching the firmware repo
id recorded at Phase 189 close]

**Consequences the planner must act on:**

1. **The before/after data is identical.** A criterion-4 demonstration that only shows `fw --list`
   working, or `fetch_release_info` returning a version and an asset URL, would produce the **same
   transcript before and after the constant change**. It is not evidence for URL-01.
2. **The distinguishing observable is `response.history`** (equivalently `response.url ==
   requested_url`). This is the direct analogue of Phase 189's `<specifics>` point that "an exit code
   cannot distinguish 'resolved `firestarter_fw`' from 'followed a redirect'" — now with the measured
   mechanism behind it. D-16's script should assert `len(r.history) == 0` on the **API** call.
3. **Scope the assertion to the API call, not the asset download.** `_download_firmware_file` fetches
   a `browser_download_url` on `github.com`, which *legitimately* redirects to
   `objects.githubusercontent.com`. Asserting "no redirects anywhere" would fail D-14 check 3 for an
   unrelated and correct reason.
4. **No test can go red before the change.** There is no red-to-green signal available from the
   network. The pin test (D-01) is the only mechanism that can fail on a stale constant, which is
   exactly why D-01 insists on it — this finding raises that from "belt-and-braces avoidance" to
   "the sole guard".

---

### Finding 2 — Only **bare `fw`** is defective; `--install` already exits 1, not just `--force`

D-08 states that `--force` already exits 1 via the `firmware.py:911-915` guard. **`--install` does
too**, by the same route. Measured by driving the real `manage_firmware_update` with
`fetch_release_info` stubbed to `(None, None)` and a board identified:

| Invocation | returns | `fw` exit | log lines emitted by `manage_firmware_update` |
|---|---|---|---|
| bare `fw` (`install_flag=False`, `flags=0`) | `True` | **0** ← the defect | **none at all** |
| `fw --install` (`install_flag=True`, `flags=0`) | `False` | 1 | `INFO Proceeding with firmware update for uno (current: 3.0.0b29, latest: None).`<br>`ERROR Cannot install: latest firmware URL or version for uno is not available.` |
| `fw --force` (`flags=FLAG_FORCE`) | `False` | 1 | `INFO Forcing firmware installation for uno.`<br>`ERROR Cannot install: latest firmware URL or version for uno is not available.` |

[VERIFIED: live probe against `firestarter.firmware.FirmwareManager` in the py3.11 venv this session]

The mechanism: at `firmware.py:881` the `elif install_flag:` arm tests `if not is_up_to_date:` —
which is `True` when `latest_version` is `None` — and sets `should_install_now = True`, reaching the
same 911-915 guard as the force path.

**Consequences:**
- **The double-emit hazard D-08 names has two paths, not one.** Any guard that could fire when
  `should_install_now` is `True` would double-emit on *both* `--install` and `--force`.
- **The defective surface is narrower than "the update path"**: it is exactly *bare `fw` against a
  board that answered an identity query*. That is the plain version-check invocation — the most
  common one, and the one whose silent exit 0 reads as "all good".
- A secondary wart worth the planner's awareness: the `--install` path emits
  `"... (current: 3.0.0b29, latest: None)."` — it renders the Python literal `None` to the operator.
  Fixing that is **not** in URL-04's scope (it already exits 1 with a named error one line later) and
  should not be folded in without a decision.

---

### Finding 3 — A guard placed immediately before `firmware.py:941` is **structurally** double-emit-proof

This is a proof, not a measurement, and it is what lets the planner satisfy D-08 without a flag test.

`firmware.py:906` opens `if should_install_now:`. **Every path inside that block returns** — the
`not download_url or not latest_version` guard returns `False` (911-915), the download failure
returns `False`, and the tail returns `install_success`. [VERIFIED: firestarter_app/firestarter/firmware.py:906-940,
read this session; the block's three exits are `return False` (915), `return False` (919), and
`return install_success` (940)]

Therefore **line 941 is reachable only when `should_install_now` is `False`**. Since both `--force`
and `--install`-with-an-unresolvable-release set `should_install_now = True` (Finding 2), neither can
reach a guard placed at 941. A new check there **cannot** double-emit — no flag inspection, no
`force_install` test, and no ordering subtlety is required.

The other paths that legitimately reach 941 all have a **non-`None` `latest_version`**, so a guard
conditioned on `not latest_version or not download_url` stays silent on them:

| Path reaching line 941 | `latest_version` | guard fires? |
|---|---|---|
| `--install` when already up to date (`firmware.py:886-890`) | set | no — correct |
| No flags, update available, operator declines the `Confirm.ask` prompt (`firmware.py:891-902`) | set | no — correct |
| bare `fw`, release unresolvable | `None` | **yes — the D-06 case** |

> **Planner note.** CONTEXT cites the fall-through as `firmware.py:940`. The file is 941 lines and the
> `return True` is the **last line, 941**. [VERIFIED: `wc -l firestarter/firmware.py` → 941; `grep -n`
> → `941:        return True  # No installation performed, but process completed as expected`]
> Similarly CONTEXT's constants table cites lines 8/12/14 (the *assignment* lines) while the URL
> *values* sit at 9/12/15 — both readings are correct, they just refer to different lines of the same
> statements. Neither discrepancy is an error; plans should cite by content, not by line number.

---

### Finding 4 — Exactly **one** existing test breaks, and it is not one CONTEXT named

A throwaway patch implementing D-06 + D-10 + D-11 was applied, the full suite run, and the patch
reverted. Measured:

| Run | Result |
|---|---|
| Baseline (clean tree) | **2129 passed**, 0 failed, 306 s |
| With D-06 + D-10 + D-11 probe patch | **1 failed, 2128 passed**, 268 s |

[VERIFIED: two full `pytest tests/ -o addopts="" -q` runs in `.venv311` this session; tree confirmed
clean via `git status --porcelain` after revert]

**The single failure:** `tests/test_py32_pyusb_absent.py::test_fw_list_exits_zero_with_header_row`.

Why it breaks — and why it is the *right* test to break:

- The module stubs the HTTP seam by making `requests.get` **raise `requests.RequestException`**
  [VERIFIED: firestarter_app/tests/test_py32_pyusb_absent.py:187-190, `_raise_request_exception`],
  i.e. it drives exactly the **fetch-failure** path D-09 is about.
- Its comment encodes the *old* contract verbatim: *"list_releases() already catches
  requests.RequestException and returns an empty list (the real code path, not a bypass of it)."*
  [VERIFIED: firestarter_app/tests/test_py32_pyusb_absent.py:193-195]
- It then asserts `result.exit_code == 0` plus the four header-row column labels
  [VERIFIED: firestarter_app/tests/test_py32_pyusb_absent.py:274-283]. Under D-09 that path becomes
  exit 1 with no header row, so **both** assertion kinds fail.
- **Its purpose is not release listing.** The module proves `usb` is never imported; `fw --list` is
  merely a convenient offline CLI vehicle. The sibling
  `test_nothing_imported_usb[argv1]` — parametrized over `("fw","--list")` — **still passes**, because
  it asserts on the `usb*` module list, not the exit code.

**What this means for the plan:** the fix is to adapt the *vehicle*, not to weaken D-09. Making the
child stub return a successful empty release list (instead of raising) preserves the module's stated
intent — "`fw --list` exits 0 offline" and the header row — while leaving the failure path to the new
D-09 tests. Changing the assertion to `exit_code == 1` would silently re-purpose a pyusb-absence test
into an endpoint test.

**Also measured, contradicting nothing but correcting a count:** D-13 names one constraining test in
`test_cli_handlers.py`. There are **two**, and both stay green:

| Test | Line | Stub | Asserts | Status under D-09/D-10 |
|---|---|---|---|---|
| `test_fw_list_with_json` | `tests/test_cli_handlers.py:647` | `list_releases.return_value = []` | `exit_code == 0` | green — genuine empty |
| `test_fw_list_plain` | `tests/test_cli_handlers.py:656` | `list_releases.return_value = []` | `exit_code == 0` | green — genuine empty |

[VERIFIED: firestarter_app/tests/test_cli_handlers.py:647-663, read this session]

**And the D-07 suites are clear.** Every test that stubs `fetch_release_info` stubs a *successful*
2-tuple; none returns `(None, None)` through `manage_firmware_update`:

```
tests/test_fw_update_path_gate.py:289:  lambda **kw: ("3.0.0b19", "https://x.invalid/u")
tests/test_py32_dfu.py:862:             lambda **kw: ("3.0.0b12", "http://x/fw.bin")
tests/test_py32_dfu.py:928:             lambda **kw: ("3.0.0b11", "http://x/fw.hex")
```
[VERIFIED: `git grep -n "fetch_release_info" -- tests/` this session]

---

### Finding 5 — The house CliRunner harness routes `logger.error` to **stderr**; production routes it to **stdout**

D-12 is **correct about production** and this research confirms it. The trap is that the test harness
used by 126 of the 137 `runner.invoke(cli, ...)` call sites does **not** reproduce production routing.

**Root cause.** The Click group callback short-circuits before installing the log handler:

```python
    if ctx.obj is not None and isinstance(ctx.obj, AppContext):
        return

    _setup_logging(verbose)
```
[VERIFIED: firestarter_app/firestarter/cli_handlers.py:427-430, quoted verbatim; the preceding comment
at :425-426 states *"_setup_logging must run AFTER the test-mode short-circuit so it does not
destructively replace pytest's caplog handler on the root logger."*]

So any test invoking with `obj=app` **never installs `SingleLineStatusHandler`**. `logger.error` then
falls through to Python's `logging.lastResort` handler, which writes to **stderr** at WARNING and
above. With no `obj=`, `_setup_logging` runs, `SingleLineStatusHandler.__init__` binds
`stream or sys.stdout` at construction time [VERIFIED: firestarter_app/firestarter/logging_utils.py:25-27],
and the error lands on **stdout**.

**Measured, current code, dead endpoint (`requests.get` raising `RequestException`):**

| Harness | `fw --list --json` stdout | stderr | exit |
|---|---|---|---|
| `CliRunner().invoke(cli, argv, obj=app)` — the house style | `'[]\n'` | `'Failed to fetch releases for list: simulated dead endpoint\n'` | 0 |
| `CliRunner().invoke(cli, argv)` — **no `obj=`** | `'Failed to fetch releases for list: simulated dead endpoint\n[]\n'` | `''` | 0 |
| Real subprocess, real console entry point | `Failed to fetch releases for list: ...`<br>`[]` | *(empty)* | 0 |

[VERIFIED: three probes run this session in `.venv311`; the no-`obj=` CliRunner output is
byte-identical to the real subprocess]

**Consequences the planner must act on:**

1. **A D-11 test written in the house style is tautological.** `assert "..." in result.stderr` with
   `obj=app` passes because of `logging.lastResort`, and would keep passing even if production emitted
   to stdout. This is the same failure shape as D-01's `next_url` tautology, in a different disguise.
2. **The correct harness is `CliRunner().invoke(cli, argv)` with no `obj=` kwarg.** It reproduces
   production byte-for-byte, needs no subprocess, and 11 existing tests already use it
   [VERIFIED: `git grep -n "runner.invoke(cli" -- tests/` → 11 without `obj=`, 126 with].
3. **`result.stdout` and `result.stderr` are separate and `result.output` is their concatenation.**
   Click 8.5.0 is installed; a probe confirmed `output == 'ON-STDOUT\nON-STDERR\n'` while
   `stdout == 'ON-STDOUT\n'` and `stderr == 'ON-STDERR\n'`. **Asserting on `result.output` cannot
   distinguish the streams** and would not prove D-11.
   [VERIFIED: live Click probe this session; `click` version `8.5.0`]
4. **`result.stdout == ""` is not achievable by suppressing the `[]` alone.** The pre-existing
   `logger.error(f"Failed to fetch releases for list: {e}")` inside `list_releases`
   [VERIFIED: firestarter_app/firestarter/firmware.py:421] goes to **stdout** in production and D-07
   says it stays. So after D-11, production stdout still carries that line. A D-11 test must assert
   *"no JSON document on stdout"* (e.g. `json.loads(result.stdout)` raises, or `"[" not in
   result.stdout`), **not** `result.stdout == ""`.
5. **Pre-existing defect worth recording, not necessarily fixing:** because logs go to stdout,
   `fw --list --json 2>/dev/null` already emits `Failed to fetch...\n[]`, which is **not parseable
   JSON**. `--json`'s machine-readable contract is already broken whenever any log line fires. D-11
   improves this case but does not resolve the general one; that is a `SingleLineStatusHandler`
   routing question and is outside this phase.

---

## Measured Live Behaviour (D-14 / D-15 confirmation)

Run through the **real** `FirmwareManager` code path with the module constants repointed to
`firestarter_fw`, against the live API this session:

| Invocation | Result |
|---|---|
| stable, `board=uno` | `('2.0.6', 'https://github.com/henols/firestarter_fw/releases/download/2.0.6/firestarter_uno.hex')` |
| stable, `board=uno328pb` | `ERROR Could not find firmware version or URL for board 'uno328pb' in the latest release.` → `(None, None)` |
| stable, `board=py32f071` | `ERROR Could not find firmware version or URL for board 'py32f071' in the latest release.` → `(None, None)` |
| pre, `board=uno328pb` | `('3.0.0b29', 'https://github.com/henols/firestarter_fw/releases/download/3.0.0b29/firestarter_uno328pb.hex')` |

[VERIFIED: live probe this session]

**D-15 is confirmed exactly as written** — `--board uno328pb --stable` is a genuine asset-less case
against a reachable, correctly-named endpoint, needing no mock. (`py32f071` is a second such case.)

**One gap against `<specifics>`:** the existing asset-less error names the **board** but **not the
endpoint URL**. `<specifics>` requires the message to name the URL so a mistyped slug is visible. The
D-06/D-09 messages this phase adds must therefore carry the URL themselves — they cannot lean on the
pre-existing `logger.error` for it.

**D-14 check 3 — the real asset download, probed this session:**

| Property | Measured |
|---|---|
| URL | `https://github.com/henols/firestarter_fw/releases/download/2.0.6/firestarter_uno.hex` |
| Status | 200 |
| Size | 60 768 bytes |
| Final host after redirects | `release-assets.githubusercontent.com` — **a legitimate redirect**, see Finding 1 consequence 3 |
| First line | `:100000000C94C9020C94F1020C94F1020C94F10…` |
| Last line | `:00000001FF` (the Intel HEX EOF record) |
| Every non-empty line starts with `:` | yes |

[VERIFIED: live `requests.get` of the real release asset this session]

So D-14 check 3 is runnable from this container, and a line-prefix + EOF-record assertion is
sufficient to demonstrate "parses as Intel HEX" on the actual artefact.

Asset label resolution, for message wording:

```
uno       -> 'firestarter_uno.hex'
uno328pb  -> 'firestarter_uno328pb.hex'
py32f071  -> 'firestarter_py32f071.hex' or 'firestarter_py32f071.bin'
leonardo  -> 'firestarter_leonardo.hex'
```
[VERIFIED: live call to `firestarter.firmware._asset_label` this session]

---

## Integration Sites

Re-measured this session. All line numbers verified by `git grep -n` against the working tree on
`v1.38-repository-rename`.

### The three constants — `firestarter_app/firestarter/constants.py`

Quoted verbatim [VERIFIED: firestarter_app/firestarter/constants.py:8-16]:

```python
FIRESTARTER_RELEASE_URL = (
    "https://api.github.com/repos/henols/firestarter/releases/latest"
)

FIRESTARTER_RELEASES_URL = "https://api.github.com/repos/henols/firestarter/releases"

FIRESTARTER_RELEASE_BY_TAG_URL = (
    "https://api.github.com/repos/henols/firestarter/releases/tags/{tag}"
)
```

Consumed only by `firmware.py`, at three call sites [VERIFIED: firestarter_app/firestarter/firmware.py:251
(`fetch_latest_release_info`), :295 (`_fetch_all_releases`), :341 (`fetch_release_info` pinned arm);
`git grep` finds no other importer]. Note all three are imported by name at
`firmware.py:264-268`, so a test that monkeypatches the constant must patch
`firestarter.firmware.FIRESTARTER_*`, **not** `firestarter.constants.FIRESTARTER_*`.

### The two fixture sites — `firestarter_app/tests/test_firmware_install.py`

Quoted verbatim [VERIFIED: firestarter_app/tests/test_firmware_install.py:381-384 and :492-495]:

```python
        page1_mock = mock_releases_factory(
            releases_page1,
            next_url="https://api.github.com/repos/henols/firestarter/releases?page=2",
        )
```

```python
            mock_releases_factory(
                release_on_page(i),
                next_url=f"https://api.github.com/repos/henols/firestarter/releases?page={i + 1}",  # noqa: E501
            )
```

D-01's tautology claim independently confirmed: both values are consumed by `mock_releases_factory`
and fed back through the `Link: rel="next"` follow in `_fetch_all_releases`
[VERIFIED: firestarter_app/firestarter/firmware.py:289-317]; neither appears in any `assert`.

### The remaining D-04 sites

| Path | Line | Content | Note |
|---|---|---|---|
| `firestarter_app/firestarter/submit.py` | 59 | `` # `henols/firestarter` and `henols/firestarter_app`). A `dev test` report spans `` | Inside a comment block. `SUBMIT_REPO = "henols/firestarter_prom"` on **line 63** is correct and untouched. [VERIFIED: firestarter_app/firestarter/submit.py:55-63] |
| `firestarter_app/.planning/codebase/INTEGRATIONS.md` | 8 | `` - Endpoint: `https://api.github.com/repos/henols/firestarter/releases/latest` (defined in `firestarter/constants.py` as `FIRESTARTER_RELEASE_URL`) `` | [VERIFIED: firestarter_app/.planning/codebase/INTEGRATIONS.md:8] |

### Full boundary-aware sweep — 7 lines in 4 files

```
.planning/codebase/INTEGRATIONS.md:8
firestarter/constants.py:9
firestarter/constants.py:12
firestarter/constants.py:15
firestarter/submit.py:59
tests/test_firmware_install.py:383
tests/test_firmware_install.py:494
```
[VERIFIED: `git grep -nE 'henols/firestarter([^_a-zA-Z0-9]|$)' -- .` run in `/workspaces/firestarter_app`
this session; positive control `henols/firestarter_prom` → 8 files, proving non-vacuity]

This matches D-04's enumeration exactly. **No additional site was found.**

### The `--list` handler — `firestarter_app/firestarter/cli_handlers.py`

Quoted verbatim [VERIFIED: firestarter_app/firestarter/cli_handlers.py:1206-1228]:

```python
    if list_releases:
        channel_filter: Literal["all", "pre", "stable"]
        if pre:
            channel_filter = "pre"
        elif stable:
            channel_filter = "stable"
        else:
            channel_filter = "all"
        releases = app.firmware_manager.list_releases(
            channel_filter=channel_filter, board=board
        )
        if json_output:
            import json as _json

            print(_json.dumps(releases, indent=2))
        else:
            print(f"{'Version':<12} {'Channel':<14} {'Published':<22} Asset URL")
            for r in releases:
                print(
                    f"{r['version']:<12} {r['channel']:<14} {r['published']:<22} {r['asset_url']}"  # noqa: E501
                )
        sys.exit(0)
```

Exit wiring for the update path: `sys.exit(0 if ok else 1)` at `cli_handlers.py:1266`
[VERIFIED: `grep -n` this session].

---

## Standard Stack

This phase adds **no dependency**. Everything it needs is already installed and pinned.

### Core (already present)

| Library | Version in `.venv311` | Purpose | Why Standard |
|---------|------|---------|--------------|
| `requests` | (per `.[test]` resolution) | The HTTP seam already used by `firmware.py` | Incumbent; D-10 explicitly forbids introducing it into the CLI layer |
| `click` | **8.5.0** | CLI framework; `CliRunner` is the test harness | Incumbent [VERIFIED: `python -c "import click"` in `.venv311`] |
| `pytest` | **9.1.1** | Test runner | Incumbent [VERIFIED: `.venv311/bin/pytest --version`] |
| `ruff` | **0.16.5** | Lint + format, both CI gates | Incumbent [VERIFIED: `.venv311/bin/ruff --version`] |
| `mypy` | **2.3.1** | Type check — **local pre-commit only, not CI** | Incumbent [VERIFIED: `.venv311/bin/mypy --version`] |
| `packaging` | (transitive) | PEP 440 ordering in `_compare_versions` / `list_releases` | Incumbent |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|---|---|---|
| `print(..., file=sys.stderr)` for the D-11 error | `click.echo(..., err=True)` | Equivalent; `click.echo` is the Click-idiomatic form and handles encoding edge cases. **But the codebase has zero precedent for either** — `Console()` appears once (`cli_handlers.py:2496`) and no production module writes to `sys.stderr`. [VERIFIED: `grep -rn "stderr\|err=True" firestarter/*.py` → only `avr_tool.py` subprocess captures and `submit.py` `gh` stderr reads] Either choice is new surface; `click.echo(err=True)` is the smaller conceptual jump in a Click handler. |
| A dedicated stderr logging handler | Direct write | A handler change is global and would alter every other command's output. D-12 already anticipates this ("an explicit stderr write **or** a handler change scoped to that path"); the direct write is far lower-risk and cannot regress the 2129-test suite. |
| `Optional[List[ReleaseInfo]]` (typing import) | `List[ReleaseInfo] \| None` | The file already uses both idioms — `Tuple[str \| None, str \| None]  # noqa: UP006` at `firmware.py:241` mixes them. Match the file: keep `List[...]` with the `# noqa: UP006` and append `\| None`. The probe used exactly this form and ruff stayed green. |

**Installation:** none required.

---

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** No `pip install` of a new
distribution appears anywhere in scope. The only install commands are `pip install -e .[test]` and
`pip install -e .` (D-17's CI reproduction), both of which install the project itself from the local
working tree against an already-pinned dependency set in `pyproject.toml`.

| Package | Registry | Verdict | Disposition |
|---|---|---|---|
| *(none)* | — | — | — |

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none.

---

## Architecture Patterns

### Data flow through the two paths this phase changes

```
                    ┌──────────────────────────────────────────────┐
  `fw --list`  ───► │ cli_handlers.fw()  :1206  list_releases branch│
                    └───────────────────┬──────────────────────────┘
                                        │ calls
                                        ▼
                    ┌──────────────────────────────────────────────┐
                    │ firmware.list_releases()  :404               │
                    │   └─ _fetch_all_releases() :289 ─► requests  │──► api.github.com
                    │        except RequestException ──┐           │    /repos/{slug}/releases
                    └──────────────────────────────────┼───────────┘
                                                       │
              TODAY: returns []  ───────────────────────┘
              D-10 : returns None  ── failure   vs   [] ── genuine empty
                                        │                    │
                                        ▼                    ▼
                          ┌──────────────────────┐  ┌─────────────────────┐
                          │ named error → STDERR │  │ header row / "No    │
                          │ no JSON doc → stdout │  │ releases found" →   │
                          │ sys.exit(1)          │  │ stdout, sys.exit(0) │
                          └──────────────────────┘  └─────────────────────┘

                    ┌──────────────────────────────────────────────┐
  bare `fw`   ───►  │ cli_handlers.fw()  :1254  manage_firmware_… │
                    └───────────────────┬──────────────────────────┘
                                        ▼
                    ┌──────────────────────────────────────────────┐
                    │ firmware.manage_firmware_update()  :747      │
                    │  :823 fetch_release_info() ──► (None, None)  │──► api.github.com
                    │  :866 is_up_to_date = False                  │    /releases/latest
                    │  :877 should_install_now = False             │
                    │  :906 if should_install_now:  ── NOT TAKEN   │
                    │        (every branch inside RETURNS)         │
                    │  :941 return True   ◄── THE DEFECT           │
                    │        D-06 guard goes HERE, immediately     │
                    │        before it — unreachable when          │
                    │        should_install_now is True            │
                    └───────────────────┬──────────────────────────┘
                                        ▼
                            cli_handlers.py:1266
                            sys.exit(0 if ok else 1)
```

### Pattern 1: The D-16 evidence script — mirror `fresh-clone-fixture.sh`

D-16 names `fresh-clone-fixture.sh` as the shape. Read in full this session
[VERIFIED: /workspaces/.planning/phases/189-free-the-name/fresh-clone-fixture.sh, 220 lines].
Its measured conventions:

| Property | What 189 does |
|---|---|
| Shebang / strict mode | `#!/usr/bin/env bash` + `set -euo pipefail` (lines 55) |
| Header block | What it proves, `Usage:`, `Environment:`, `Dependencies:`, `Failure style:`, `Exit codes:`, `Re-runnable:` — lines 1-53 |
| `--help` | `sed -n '2,40p' "$0" \| sed 's/^# \{0,1\}//'; exit 0` (lines 62-65) — prints its own header |
| Unknown arg | `exit 2` with usage to stderr (lines 66-70) |
| Path resolution | `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` then derive roots relative to it (lines 79-80); **never hardcode `/workspaces`** |
| Env-var overrides | `META_REF`, `KEEP_CLONE`, `SCRATCH_DIR` with `${VAR:-default}` (lines 81-82, 107) |
| Scratch dir | `mktemp -d` **outside `/workspaces`** + `trap cleanup EXIT` (lines 103-118) — explicitly because `git clean -Xdf` destroys GSD state |
| Evidence emission | Titled header, then **each resolved value on its own labelled line** (`key: value`), *before* the verdict (lines 120-174) |
| Assertions | Bail on first failure; each names what was expected, the pre-state, and what to do next (lines 180-216) |
| Verdict | Literal `FRESH CLONE OK` token + `exit 0` |
| Exit codes | 0 = pass, 1 = failure, 2 = bad usage, **3 = one named, expected non-failure case** |
| Diagnostics | Failure detail to `>&2`, success values to stdout |

**Directly reusable:** the boundary-aware discriminator is already written and proven —
`BARE_SLUG_PATTERN='henols/firestarter([^_a-zA-Z0-9]|$)'`
[VERIFIED: /workspaces/.planning/phases/189-free-the-name/fresh-clone-fixture.sh:204, quoted verbatim].

### Pattern 2: Evidence transcript shape

`189-firmware-slug-sweep.txt` is the committed-transcript precedent
[VERIFIED: /workspaces/.planning/phases/189-free-the-name/evidence/189-firmware-slug-sweep.txt].
Its structure: a titled header, `capture_date:` (ISO-8601 Z) and `capture_commit:`, the exact command
in a code block, a PRE-STATE section, numbered POST-STATE READINGs each with `command:` /
`matching files:` / `result:`, **a non-vacuity positive control**, and a CONCLUSION paragraph. Five
such files live in `189-free-the-name/evidence/`.

### Anti-Patterns to Avoid

- **Asserting on `result.output` for a stream claim.** It is stdout+stderr concatenated (Finding 5).
  Use `result.stdout` / `result.stderr`.
- **Writing a stream-sensitive test with `obj=app`.** It bypasses `_setup_logging` and measures
  `logging.lastResort` (Finding 5).
- **Asserting `result.stdout == ""` for D-11.** The retained `logger.error` still writes there
  (Finding 5, consequence 4).
- **A negative assertion against `henols/firestarter` in the pin test.** D-02 forbids it, and it is a
  substring of `henols/firestarter_fw` — `assert "henols/firestarter" not in URL` would fail on the
  *correct* value. If a negative is ever wanted, only the boundary-aware regex is sound.
- **Sweeping with `grep 'henols/firestarter' | grep -v 'firestarter_fw'`.** Measured to be wrong —
  see Pitfall 1.
- **Asserting "no redirects" on the asset download.** `github.com/.../download/...` legitimately
  redirects to `objects.githubusercontent.com` (Finding 1, consequence 3).
- **Adding any comment to `constants.py`, `firmware.py`, `cli_handlers.py` or the test files.**
  Non-overridable (`## Project Constraints`).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Distinguishing the bare slug from `_fw`/`_app`/`_prom` | A new regex, or `grep -v` chaining | `henols/firestarter([^_a-zA-Z0-9]|$)` from `189-PATTERNS.md` | Already written, already proven against both sub-repos, already has a documented non-vacuity control. Re-deriving it is how the `grep -v` bug in Pitfall 1 gets reinvented. |
| Proving a URL was not reached via redirect | Parsing `Location` headers by hand, or `allow_redirects=False` plumbing | `response.history` / `response.url` from the existing `requests` response | `requests` already records the full redirect chain; `len(r.history) == 0` is the whole test (Finding 1). |
| Reproducing production stream routing in a test | A subprocess harness | `CliRunner().invoke(cli, argv)` with no `obj=` | Measured byte-identical to a real subprocess run, with none of the cost (Finding 5). A subprocess harness also cannot split streams in the existing `test_py32_pyusb_absent.py` shape, which reports only `result.output`. |
| Guaranteeing the D-06 guard does not double-emit | A `force_install` / `install_flag` condition on the new guard | Placement immediately before `firmware.py:941` | The placement is structurally sufficient (Finding 3). A flag condition adds a branch that can drift. |
| Parsing Intel HEX for D-14 check 3 | A hand-rolled record parser | `firestarter_app` has no HEX parser; the cheapest honest check is a format assertion (every line starts `:`, final record is `:00000001FF`) | Full HEX validation is not what D-14 asks for — it asks the file "parses as Intel HEX". Pulling in `intelhex` would be a new dependency for one evidence script. **[ASSUMED]** — no in-repo precedent was found either way. |
| A py3.11 environment | A fresh `uv venv` per run | The existing `/workspaces/firestarter_app/.venv311` | Already present, Python 3.11.16, editable-installed against the working tree, and self-ignoring via its own `.venv311/.gitignore` containing `*`. See § *Environment Availability*. |

**Key insight:** every instrument this phase needs already exists in the repository or in the
`requests`/`click` APIs. The failure mode here is not building the wrong thing — it is building a
*correct-looking* instrument that measures the wrong process (the CliRunner harness) or the wrong
string boundary (the `grep -v` sweep). Both produce green transcripts that prove nothing.

---

## Common Pitfalls

### Pitfall 1: The naive sweep silently misses `submit.py:59`

**What goes wrong:** The obvious D-05 verification sweep —
`grep -rn "henols/firestarter" | grep -v "firestarter_fw\|firestarter_app\|firestarter_prom"` —
under-reports.

**Measured:** that pipeline returns **6** of the **7** actual sites. It drops
`firestarter/submit.py:59`, because that line contains *both* the bare slug and `henols/firestarter_app`:

> `` # `henols/firestarter` and `henols/firestarter_app`). A `dev test` report spans ``

`grep -v` filters **lines**, not matches, so a line naming both slugs is discarded wholesale.
[VERIFIED: both pipelines run this session in `/workspaces/firestarter_app`; naive → 6 lines,
boundary-aware → 7 lines]

**Why it happens:** D-02 identifies the substring hazard in the *assertion* direction (a negative
assert is vacuous). This is the same hazard in the *sweep* direction, and it bites the opposite way —
the sweep is not vacuous, it is **falsely clean**.

**How to avoid:** use `git grep -nE 'henols/firestarter([^_a-zA-Z0-9]|$)'`. Always pair it with the
`henols/firestarter_prom` positive control (8 files in this repo) so a zero is provably not an empty
scan.

**Warning signs:** a sweep whose count is exactly one less than the enumeration in D-04.

### Pitfall 2: `grep` in this devcontainer is ugrep and honours `.gitignore`

**What goes wrong:** a bare `grep -rn` silently under-scans, and a gate built on it fails **open**.

**How to avoid:** `/usr/bin/grep` for filesystem sweeps, or `git grep` for tracked-file sweeps.
Phase 189 used `git grep` throughout and every `<automated>` block in its plans spells
`/usr/bin/grep` explicitly [VERIFIED: `189-02-PLAN.md:218,293`, `189-03-PLAN.md:230`,
`189-04-PLAN.md:143,252`]. Mirror that.

**Extra hazard carried from project memory:** `grep -qF` with a dash-leading pattern exits 2 and the
gate fails open; use `-qFe`. Not obviously triggered here, but the D-16 script does string matching.

### Pitfall 3: The devcontainer is py3.12 and has provably masked py3.11 CI breakage

**How to avoid:** run every gate inside `.venv311` (or a fresh `uv venv --python 3.11`). This is
D-17's whole substance. `python3 --version` at the devcontainer default is **not** what CI runs.

### Pitfall 4: mypy is not a CI gate, and its watermark is a comment

D-10 refers to "the mypy watermark gate". Measured:

- `pyproject.toml:140` reads `# mypy_error_watermark = 35   # Updated Phase 71-07: ...` — it is
  **commented out**, i.e. inert configuration, not an enforced threshold.
  [VERIFIED: firestarter_app/pyproject.toml:140, quoted verbatim]
- `ci.yml` has **no mypy step**. [VERIFIED: firestarter_app/.github/workflows/ci.yml read in full;
  the `ci` job's five `run:` steps are lines 56, 59, 62, 65, 71 — none invokes mypy]
- `CLAUDE.md:127` states it outright: *"`mypy` ... is wired in the local `pre-commit` config only and
  is **not** a CI gate"*.

**So the annotation change cannot fail CI.** It can only fail a local `pre-commit` run. That said, the
type error it produces is real and worth fixing — see § *Runnable Commands* for the measured failing
direction.

### Pitfall 5: mypy catches the table branch but **not** the `--json` branch

Measured with `list_releases -> List[ReleaseInfo] | None` and the caller left unguarded:

- mypy reports exactly one new error, at the `for r in releases:` loop:
  `firestarter/cli_handlers.py:1223: error: Item "None" of "list[ReleaseInfo] | None" has no
  attribute "__iter__" (not iterable)  [union-attr]`
- It reports **nothing** at `cli_handlers.py:1220`, `print(_json.dumps(releases, indent=2))`, because
  `json.dumps` accepts `Any`.

[VERIFIED: probe run this session; error count 33 → 34]

`json.dumps(None, indent=2)` returns the string `'null'`
[VERIFIED: `python -c "import json; print(repr(json.dumps(None, indent=2)))"` → `'null'`].

**So an executor who fixes only what mypy complains about will ship `fw --list --json` printing
`null` on stdout and exiting 0** — a *new* silent-success defect in exactly the machine-readable
surface D-11 exists to protect. **The `None` guard must sit before the `if json_output:` branch**, not
inside the `else`.

### Pitfall 6: `test_py32_pyusb_absent.py` encodes the old contract in a comment

The module comment at lines 193-195 asserts the current `RequestException → []` behaviour as settled
fact. An executor reading it may conclude D-09 is wrong. It is documentation of the defect, not a
constraint. See Finding 4 for the disposition.

### Pitfall 7: Constants are imported by name, so patching `constants` does not work

`firmware.py:264-268` does `from firestarter.constants import (..., FIRESTARTER_RELEASE_URL, ...)`.
A test or throwaway process producing D-15's unreachable case must set
`firestarter.firmware.FIRESTARTER_RELEASE_URL`, **not** `firestarter.constants.FIRESTARTER_RELEASE_URL`
— the latter has no effect on already-imported bindings.
[VERIFIED: firestarter_app/firestarter/firmware.py:264-272, read this session; confirmed empirically —
the live D-15 probe repointed `F.FIRESTARTER_RELEASE_URL` and the change took effect]

**This directly affects D-15's "unreachable case in a throwaway process"** and is the likeliest way
that leg silently demonstrates nothing.

### Pitfall 8: `test_flash_path_record_sync` asserts whole-repo porcelain

Project memory records that this test asserts repo cleanliness. Commit before running the full suite,
or it goes red for reasons unrelated to this phase. The baseline run in this session was green
**because the tree was clean**.

---

## Code Examples

### Verifying no redirect was followed (the D-16 instrument)

```python
# Source: measured against the live api.github.com this session
import requests
from firestarter.constants import FIRESTARTER_RELEASE_URL

r = requests.get(FIRESTARTER_RELEASE_URL, timeout=10)
print(f"requested: {FIRESTARTER_RELEASE_URL}")
print(f"resolved : {r.url}")
print(f"status   : {r.status_code}")
print(f"redirects: {len(r.history)}")
# Today (bare slug):   resolved -> https://api.github.com/repositories/810276812/releases/latest
#                      redirects -> 1        <-- the redirect this phase eliminates
# After URL-01:        resolved == requested
#                      redirects -> 0
assert len(r.history) == 0, f"followed {len(r.history)} redirect(s) -> {r.url}"
```

### The production-faithful CLI test harness (D-11 / D-12)

```python
# Source: measured byte-identical to a real subprocess run this session
from click.testing import CliRunner
from firestarter.cli_handlers import cli

# NOTE: no obj= kwarg. That is what makes _setup_logging run (cli_handlers.py:427-430)
# and routes logger.error to stdout exactly as production does.
result = CliRunner().invoke(cli, ["fw", "--list", "--json"])

assert result.exit_code == 1
assert "<the endpoint URL>" in result.stderr      # D-11: named error on stderr
# D-11: no JSON document on stdout. NOT `result.stdout == ""` -- the retained
# logger.error from firmware.py:421 still writes there (Finding 5).
assert "[" not in result.stdout and "null" not in result.stdout
```

### The URL-03 pin, and the test that proves the pin is not a tautology

```python
# Source: shape derived from D-01/D-02/D-03; no in-repo analog exists
# (git grep FIRESTARTER_RELEASE -- tests/ is empty today).
from firestarter.constants import (
    FIRESTARTER_RELEASE_BY_TAG_URL,
    FIRESTARTER_RELEASE_URL,
    FIRESTARTER_RELEASES_URL,
)

def test_release_endpoints_address_the_renamed_repository() -> None:
    for url in (
        FIRESTARTER_RELEASE_URL,
        FIRESTARTER_RELEASES_URL,
        FIRESTARTER_RELEASE_BY_TAG_URL,
    ):
        # D-02: POSITIVE assertion only. `henols/firestarter` is a substring of
        # `henols/firestarter_fw`, so a negative assertion is vacuous or wrong.
        # D-03: assert the slug, not the full URL, so a legitimate path change
        # (including the {tag} template) does not require editing this test.
        assert "henols/firestarter_fw/" in url
```

> The above is illustrative test code, not product source; the explanatory lines inside it are for
> the planner's benefit. **If any of it is carried into a plan, the comments must be dropped** — the
> app-local `CLAUDE.md` rule covers `tests/` as part of "this package".

**Criterion 2 demands the pin be *proved* to fail.** The cheapest honest proof, mirroring the
"plant a violation and see it go red" discipline the Deferred Ideas section calls for:

```bash
# Edit ONE constant back to the bare slug, run only the pin test, expect exit 1, revert.
cd /workspaces/firestarter_app
cp firestarter/constants.py /tmp/constants.py.bak
sed -i '12s|firestarter_fw|firestarter|' firestarter/constants.py
.venv311/bin/pytest tests/test_endpoint_constants.py -q ; echo "expect rc=1, got rc=$?"
cp /tmp/constants.py.bak firestarter/constants.py
git diff --quiet firestarter/constants.py && echo "reverted clean"
```

### Reproducing D-15's unreachable case (Pitfall 7 applies)

```python
# Source: measured this session -- patching firestarter.firmware, NOT firestarter.constants
import firestarter.firmware as F
F.FIRESTARTER_RELEASE_URL = (
    "https://api.github.com/repos/henols/firestarter_nope/releases/latest"
)
# That slug returns a real 404 (measured), so this is a genuine unreachable endpoint,
# not a mocked one.
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| `CliRunner(mix_stderr=False)` to split streams | `mix_stderr` removed; `result.stdout` / `result.stderr` / `result.output` always available, `output` = both concatenated | Click 8.2 | Installed Click is **8.5.0** [VERIFIED: probe this session]. `CliRunner.__init__` signature measured as `(self, charset='utf-8', env=None, echo_stdin=False, catch_exceptions=True, capture='sys')` — **no `mix_stderr`**. Code or advice using `mix_stderr=False` is stale and will `TypeError`. |
| `typing.List` / `typing.Optional` | PEP 604 `\| None`, builtin generics | py3.9/3.10 | The file deliberately retains `List`/`Tuple` with `# noqa: UP006`/`UP035` to keep ruff's pyupgrade rule quiet; **match the file's existing idiom** rather than "modernising" it, or ruff's `UP` rules will churn the diff. |
| `pip install` into the system interpreter | `uv venv --python 3.11` | — | `uv 0.12.6` is installed at `/usr/local/bin/uv` [VERIFIED: `uv --version` this session]. |

**Deprecated/outdated:**
- `click.__version__` — emits a `DeprecationWarning` on 8.5.0 and is removed in Click 9.1. Use
  `importlib.metadata.version("click")` if a version is ever needed.
  [VERIFIED: the deprecation warning was emitted during this session's probe]

---

## Runnable Commands, With Their Failing Direction

Every command below was executed this session in `/workspaces/firestarter_app`.

### The five `ci.yml` gate steps (D-17) — current state: **all green**

| # | Command (verbatim from `ci.yml`) | `ci.yml` line | Measured result |
|---|---|---|---|
| 1 | `pip install -e .[test]` | 56 | `.venv311` already satisfies this; `firestarter.__file__` resolves into the working tree |
| 2 | `ruff check firestarter/ tests/` | 59 | `All checks passed!` (rc 0) |
| 3 | `ruff format --check firestarter/ tests/` | 62 | `155 files already formatted` (rc 0) |
| 4 | `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` | 65 | **2129 passed**, `TOTAL 5871 896 85%`, `Required test coverage of 70% reached. Total coverage: 84.74%`, 372 s |
| 5 | `pip install -e . && firestarter --help` | 71 | rc 0 |

Run them prefixed with `.venv311/bin/` (e.g. `.venv311/bin/ruff check firestarter/ tests/`) or after
`source .venv311/bin/activate`.

**Coverage headroom: 14.74 points** above the 70% floor. The lines this phase adds are few and will be
directly tested, so the floor is not at risk.

**Failing direction for step 4:** any new untested branch lowers `TOTAL`; the gate fails only below
70%. With 84.74% today, a coverage failure would indicate something far larger went wrong.

> **D-17 completeness note.** D-17 names five steps, which is exactly the `ci` job. `ci.yml` also
> defines a **second job, `ci-py32`**, with two further gate steps
> [VERIFIED: firestarter_app/.github/workflows/ci.yml:79-103]:
> `pip install -e .[test,py32]` · `python3 -c "import usb.core, importlib.metadata; print('pyusb', importlib.metadata.version('pyusb'))"` ·
> `pytest tests/test_pyusb_api_surface.py -q`.
> This matters because **Finding 4's single breaking test lives in the pyusb-absence family**. The
> breaking test is in the primary `ci` job's scope (it is under `tests/` and not excluded), so step 4
> does catch it — but a planner reproducing "Host CI" should know `ci-py32` exists and that D-17's
> five steps are the `ci` job only. Reproducing `ci-py32` is optional; noting its existence is not.

> **Also note `paths-ignore`.** Both the `push` and `pull_request` triggers exclude `**.md`,
> `.gitignore`, `docs/**`, `.vscode/**`, `.editorconfig`
> [VERIFIED: firestarter_app/.github/workflows/ci.yml:20-32]. This phase changes `.py` files, so CI
> would fire — as CONTEXT's `<canonical_refs>` states.

### The mypy check (local only — **not** a CI gate)

```bash
cd /workspaces/firestarter_app && .venv311/bin/mypy firestarter/ tests/
```

| State | Result |
|---|---|
| Current (clean tree) | `Found 33 errors in 13 files (checked 157 source files)` |
| With `list_releases -> List[ReleaseInfo] \| None` and the caller **unguarded** | `Found 34 errors in 14 files` — the new one is `firestarter/cli_handlers.py:1223: error: Item "None" of "list[ReleaseInfo] \| None" has no attribute "__iter__" (not iterable)  [union-attr]` |
| With the `None` guard added before the `json_output` branch | expected back to 33 **[ASSUMED]** — not measured; the probe patch's guard was placed correctly but a separate 33-error confirmation run was not made |

**Failing direction:** the error appears in `cli_handlers.py`, which is in the **strict island**
(`disallow_untyped_defs = true`, `check_untyped_defs = true`)
[VERIFIED: firestarter_app/pyproject.toml:156-174, module list includes `firestarter.cli_handlers`].
`firestarter.firmware` is in the **non-strict** list with `follow_imports = "silent"`
[VERIFIED: firestarter_app/pyproject.toml:176-191]. So errors *inside* `firmware.py` are silenced, but
its **types still flow** to the strict caller — which is why the annotation change surfaces there and
only there.

**The watermark is inert** (Pitfall 4). If a plan wants a mypy assertion, the honest form is an exact
count comparison against the measured 33, not a reference to `mypy_error_watermark`.

### The boundary-aware sweep (D-05)

```bash
cd /workspaces/firestarter_app
git grep -nE 'henols/firestarter([^_a-zA-Z0-9]|$)' -- .          # expect 0 after this phase
git grep -lE 'henols/firestarter_prom' -- . | wc -l              # positive control: expect 8
```

| State | bare-slug matches | control |
|---|---|---|
| Today | **7 lines in 4 files** | **8 files** |
| After URL-01 + URL-03 + D-04 | 0 | 8 (unchanged) |

**Failing direction:** a non-zero bare-slug count means a site was missed. A **zero control** means the
scan itself is broken — treat a zero/zero result as a failed gate, not a pass.

### Full suite, quiet

```bash
cd /workspaces/firestarter_app && .venv311/bin/pytest tests/ -o addopts="" -q
```

`-o addopts=""` is required: `pyproject.toml` sets `addopts = "-ra -q"`, and doubling `-q` suppresses
the pass/fail count line. Baseline measured: **2129 passed, 1 warning, 306 s**.

---

## Runtime State Inventory

This phase changes a URL constant and CLI behaviour. It is adjacent to the v1.38 rename, so the five
categories are answered explicitly rather than omitted.

| Category | Items Found | Action Required |
|---|---|---|
| **Stored data** | **None.** No database, cache or datastore in either repository stores a firmware repository slug. `~/.firestarter/config.json` stores `port` and user settings only; the release URL is a module constant, never persisted. [VERIFIED: `git grep -nE 'henols/firestarter([^_a-zA-Z0-9]\|$)'` over `firestarter_app` finds 7 sites, all source/test/doc — none is a data file; `chip_database.json` contains no repository slug] | none |
| **Live service config** | **None for this phase.** GitHub repository settings, releases and assets were handled in Phase 189. No external service holds this app's release-endpoint URL — the constant is compiled into the wheel. | none |
| **OS-registered state** | **None.** No Task Scheduler entry, launchd plist, systemd unit or pm2 process references the release endpoint. Nothing scripted invokes `fw` — re-confirmed: no `.sh` and no workflow in either sub-repository calls it. [VERIFIED: `git grep` for `fw ` across `*.sh` and `.github/workflows/` in both sub-repos returns no invocation] | none |
| **Secrets / env vars** | **None.** The GitHub Releases API is used unauthenticated — `Auth: None — public API, no token required` [VERIFIED: firestarter_app/.planning/codebase/INTEGRATIONS.md:11]. `PYPI_API_TOKEN` exists but is publish-only and unrelated. No env var overrides the endpoint. | none |
| **Build artifacts / installed packages** | **Two.** (1) `firestarter_app/build/lib/` carries stale copies of `constants.py` and is **untracked** — CONTEXT says ignore it, and this research confirms `build/` is in `.gitignore` [VERIFIED: firestarter_app/.gitignore line 3, `build/`]. (2) `.venv311/` holds an **editable** install pointing at the working tree, so it picks the constant change up with no reinstall [VERIFIED: `firestarter.__file__` → `/workspaces/firestarter_app/firestarter/__init__.py`]. | none — but do **not** treat `build/lib/` as a site needing repair, and do **not** reinstall `.venv311` expecting it to matter |

**The one runtime state that does exist is outside this phase:** already-installed copies of the
`firestarter` wheel on users' machines carry the bare-slug constant. They keep working **only while
the 301 redirect lives** (Finding 1) — which is exactly the stranding risk the milestone bounds by
deferring the claim (D-1), and which Phases 191/193 own.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| Python 3.11 | D-17 (CI parity) | ✓ | 3.11.16 at `/workspaces/firestarter_app/.venv311/bin/python` | `uv venv --python 3.11` |
| `uv` | D-17 (`uv venv --python 3.11`) | ✓ | 0.12.6 at `/usr/local/bin/uv` | the existing `.venv311` |
| `pytest` | CI step 4 | ✓ | 9.1.1 (in `.venv311`) | — |
| `ruff` | CI steps 2–3 | ✓ | 0.16.5 (in `.venv311`) | — |
| `mypy` | D-10 type check (local only) | ✓ | 2.3.1 (in `.venv311`) | — |
| `click` | CLI + `CliRunner` | ✓ | 8.5.0 | — |
| Network to `api.github.com` | D-14 checks 1–2 and 4, D-16 | ✓ | HTTP 200 on `firestarter_fw`, 301 on bare slug, 404 on nonexistent | none — D-14 is inherently a live check |
| Network to `github.com` release assets | D-14 check 3 (`.hex` download) | ✓ | HTTP 200, **60 768 bytes** for `firestarter_uno.hex` @ `2.0.6`; final host `release-assets.githubusercontent.com` | none |
| `git` | D-05 sweep, D-16 script | ✓ | — | — |
| `/usr/bin/grep` (GNU) | evidence sweeps | ✓ | — | `git grep` |
| `avrdude` | **not needed** — D-14 explicitly stops before hardware | n/a | — | — |
| Bench hardware | **not needed** — ROADMAP states "Bench: none" | n/a | — | — |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none.

**Note on the `.venv311` tree:** it is untracked and self-ignoring — `.venv311/.gitignore` contains
`*`, which is why `git status --porcelain` stays empty despite `.gitignore` listing only `.venv/`
[VERIFIED: `git check-ignore -v .venv311/` → `.venv311/.gitignore:1:*	.venv311/`]. There is no risk
of committing it.

---

## Security Domain

`security_enforcement` is not set in `.planning/config.json`, so it is treated as enabled. This phase's
security surface is narrow but not empty.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | The Releases API is used unauthenticated against a public repository |
| V3 Session Management | no | No sessions |
| V4 Access Control | no | No authorization decisions |
| V5 Input Validation | **yes** | `FIRMWARE_VERSION_RE` already validates `--firmware-version` before it reaches the `{tag}` template [VERIFIED: firestarter_app/firestarter/firmware.py:283-288]. This phase must not weaken it. |
| V6 Cryptography | no | TLS is handled by `requests`; no crypto is written here |
| V12 Files & Resources | **yes** | `_download_firmware_file` writes a fetched `.hex` to a temp path and it is later flashed to hardware |

### Known Threat Patterns for this change

| Pattern | STRIDE | Standard Mitigation |
|---|---|---|
| **Endpoint retarget to an attacker-controlled repository** — the exact risk URL-01 and URL-04 exist to bound | Tampering / Spoofing | The D-01 pin makes a silent retarget impossible; the D-06/D-09 messages **name the URL**, so a mistyped or hostile slug is visible to the operator. This is the phase's primary security value. |
| **Silent fall-back to a redirect target** — a repository slug that later changes hands resolves somewhere new without any signal | Spoofing | Finding 1's `len(response.history) == 0` assertion. This is precisely the risk the deferred claim (`SEED-claim-firestarter-slug.md`) creates: after the claim, the bare slug resolves to the *meta* repository. D-4's "meta never publishes a Release" keeps the failure a loud 404 rather than a wrong-firmware download. |
| **Silent success on a failed fetch** — the current exit-0 defect | Repudiation / Tampering | D-06 and D-09. An operator who cannot tell "up to date" from "could not check" may ship a board on stale firmware believing it current. |
| Unvalidated tag interpolation into the URL template | Injection | Already mitigated by `FIRMWARE_VERSION_RE`, anchored with `\Z` not `$` specifically to stop a trailing newline corrupting the URL [VERIFIED: firestarter_app/firestarter/firmware.py:283-288 comment records this was fixed 2026-05-20 after code review]. **Do not touch this regex.** |
| Downloaded `.hex` is flashed without provenance verification | Tampering | **Pre-existing and out of scope.** No signature or checksum verification exists on the downloaded asset. Recorded here because D-14 check 3 downloads a real `.hex`; it is not this phase's to fix. |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | With the `None` guard correctly placed, mypy returns to exactly 33 errors | Runnable Commands | Low — the guarded form was not separately measured. A plan should measure it rather than assert it. |
| ~~A2~~ | ~~A full asset `.hex` download from `github.com` succeeds from this container~~ | — | **RESOLVED — probed and confirmed.** See § *Measured Live Behaviour*, D-14 check 3. |
| A3 | Checking "parses as Intel HEX" by line-prefix and EOF-record assertion is adequate for D-14 check 3 | Don't Hand-Roll | Low — D-14's wording is "confirm it parses as Intel HEX"; no in-repo HEX parser exists either way. The measured file satisfies exactly this check, so it is at minimum sufficient to pass. The planner may prefer a stricter check. |
| A4 | `click.echo(..., err=True)` is preferable to `print(..., file=sys.stderr)` for the D-11 write | Standard Stack | Low — both work; the codebase has precedent for neither. Style choice, explicitly within Claude's Discretion. |
| A5 | Adapting `test_py32_pyusb_absent.py`'s stub to a successful empty response (rather than re-pointing its assertion) is the right disposition | Finding 4 | Low–Medium — it preserves the module's stated intent, but the module's author may have wanted the `RequestException` specifically to avoid constructing a fake HTTP response. A plan should read `mock_releases_factory` before committing to the approach. |

---

## Open Questions

1. **Does `logger.error`'s stdout routing undermine D-11 in practice?**
   - What we know: after D-11, production stdout still carries `Failed to fetch releases for list: ...`
     from the retained `logger.error` (D-07), so `fw --list --json` stdout is still not clean JSON.
   - What's unclear: whether D-11's intent ("no document on stdout") is satisfied by "no JSON
     document" or requires a genuinely empty stdout.
   - Recommendation: implement "no JSON document" — it is the literal reading, it preserves D-07, and
     it needs no `SingleLineStatusHandler` change. **Record the residue explicitly in `SUMMARY.md`** so
     a future JSON-schema decision (a Deferred Idea) inherits the measurement rather than rediscovering
     it.

2. **Should the D-16 script assert redirect-freedom, given D-05 declines a standing guard?**
   - What we know: Finding 1 shows it is the only observable that distinguishes URL-01 done from
     URL-01 undone.
   - What's unclear: whether a redirect assertion inside the evidence script counts as the "standing
     check" D-05 defers to Phase 192.
   - Recommendation: it does not. D-05 defers a **repository-wide source-scanning regression guard**;
     a live network assertion inside an on-demand, non-CI evidence script is a different instrument
     with a different failure mode, and D-16 already establishes that such scripts live here. Include it.

3. **Is `test_endpoint_constants.py` portable to `main` (Phase 191)?**
   - What we know: the Discretion note prefers a standalone module precisely so Phase 191 can port it
     to a branch 948 commits behind.
   - What's unclear: whether `main` carries `FIRESTARTER_RELEASE_BY_TAG_URL` at all — the pinned-channel
     constant may post-date the `main` fork point. **Not measured this session** (`main` was not checked
     out; doing so is Phase 191's scope).
   - Recommendation: write the pin so it iterates over constants imported individually, and let
     Phase 191 drop any constant `main` lacks. Do not write it as a directory scan.

---

## Sources

### Primary (HIGH confidence — measured this session)

- `/workspaces/firestarter_app/firestarter/{constants,firmware,cli_handlers,logging_utils,submit}.py` — read directly
- `/workspaces/firestarter_app/tests/{test_firmware_install,test_cli_handlers,test_py32_pyusb_absent,test_fw_port_targeting_and_blind_install,test_fw_update_path_gate,test_py32_dfu}.py` — read / grepped
- `/workspaces/firestarter_app/{pyproject.toml,.pre-commit-config.yaml,.gitignore,CLAUDE.md}` — read
- `/workspaces/firestarter_app/.github/workflows/ci.yml` — read in full (103 lines)
- `/workspaces/CLAUDE.md`, `/workspaces/.planning/{REQUIREMENTS.md,config.json}` — read
- `/workspaces/.planning/STATE.md` lines 1–282, `/workspaces/.planning/ROADMAP.md` lines 300–340 — read per the budget
- `/workspaces/.planning/phases/189-free-the-name/{fresh-clone-fixture.sh,189-PATTERNS.md,189-VERIFICATION.md,evidence/189-firmware-slug-sweep.txt}` — read
- Live `api.github.com` probes: redirect history, status codes, release/asset resolution
- Live interpreter probes in `.venv311` (Python 3.11.16): `manage_firmware_update` flag matrix,
  `fetch_latest_release_info` per board, Click `CliRunner` stream split, `json.dumps(None)`
- Two full `pytest` runs (baseline and probe-patched) and one coverage run
- Two full `mypy` runs (baseline and probe-patched)
- `ruff check` and `ruff format --check` runs

### Secondary (MEDIUM confidence)

- `/workspaces/firestarter_app/.planning/codebase/INTEGRATIONS.md` — in-repo documentation dated
  2026-05-08; used for the auth claim, which is consistent with the code

### Tertiary (LOW confidence)

- None. No WebSearch or external documentation was consulted; every claim is grounded in this
  repository or a live API probe.

### Not used

- `.planning/graphs/graph.json` exists but is dated **2026-07-01** (~2.5 months stale) and this phase's
  surface is four files already enumerated by CONTEXT. No graph query was run; semantic relationships
  would have added nothing over direct reads.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| Standard stack | HIGH | No new dependencies; every version read from the live `.venv311` |
| Integration sites | HIGH | Every line number re-verified by `git grep -n` and the content quoted verbatim |
| `manage_firmware_update` behaviour | HIGH | Executed against the real method across all three flag combinations; the no-double-emit property is a structural proof over code read this session |
| `list_releases` / stream routing | HIGH | Three independent harnesses (CliRunner with `obj`, CliRunner without `obj`, real subprocess) agree, and the divergence's root cause was located in source |
| Blast radius on the test suite | HIGH | Measured by running the full 2129-test suite with and without a probe patch |
| mypy gate | HIGH | Both the "not a CI gate" claim and the exact new error were measured; the watermark's inertness read directly from `pyproject.toml` |
| CI equivalence (D-17) | HIGH | All five steps executed verbatim on py3.11 |
| Live endpoint state | HIGH | Probed directly; matches CONTEXT's independent 2026-09-13 measurement |
| D-16 script shape | HIGH | The precedent was read in full |
| Asset download reachability | LOW | Not probed (A2) |

**Research date:** 2026-09-13
**Valid until:** 2026-10-13 for the code and tooling findings (stable, in-repo). **The live endpoint
findings are volatile** — the 301 on `henols/firestarter` persists only until the deferred claim fires
(`SEED-claim-firestarter-slug.md`), at which point it becomes a 404 or, worse, a 200 from the meta
repository. Re-probe before relying on Finding 1 in any later milestone.

---

## Ready for Planning

The phase has no unresolved blockers. Every decision in `190-CONTEXT.md` stands; five of them need
their premise widened (Findings 1–5) and one environment probe (A2) is worth running before the D-16
script is planned.
