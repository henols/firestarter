# Phase 190: Endpoints That Do Not Depend on a Redirect - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-13
**Phase:** 190-endpoints-that-do-not-depend-on-a-redirect
**Areas discussed:** Fixture pin mechanism, Dead-endpoint exit code, `fw --list` scope, Criterion 4 evidence

**Area selection:** all four offered areas were selected. A fifth candidate — the Phase 190/192 boundary for
`submit.py:59` and the app repository's own `.planning/codebase/INTEGRATIONS.md` — was **not** offered as a
question because Phase 189's D-09 already settles it by precedent; it was presented as carried-forward and
recorded as D-04.

---

## Fixture pin mechanism

Research presented before the question: deriving a test's expected value from the thing under test is a
tautology — the comparison is true by construction and stays green on exactly the change it exists to catch.
The counter-pattern is an independently-written reference.

### Q1 — What is the pin?

| Option | Description | Selected |
|--------|-------------|----------|
| Slug pin on all three | Derive both fixtures off `FIRESTARTER_RELEASES_URL`, plus one new test asserting all three constants contain `henols/firestarter_fw` | ✓ |
| Exact full-URL pin on all three | Pin each constant to its full expected string verbatim; catches path changes too, but must be edited for any legitimate endpoint change including the `{tag}` template | |
| Slug pin + assert the requested URL | Both, plus capturing what `requests.get` is actually called with in `_fetch_all_releases` and `fetch_latest_release_info` | |

**User's choice:** Slug pin on all three (recommended option).
**Notes:** Recorded as D-01/D-02/D-03. The key finding driving the question: the two fixture sites are mock
pagination `next_url`s that are never asserted, so f-string derivation alone leaves the test green when a
constant is edited.

### Q2 — Where does the pin test live?

| Option | Description | Selected |
|--------|-------------|----------|
| New `tests/test_endpoint_constants.py` | Dedicated file, discoverable by name, portable to `main` for Phase 191 | |
| Inside `tests/test_firmware_install.py` | Alongside the fixtures it guards; no new file | |
| You decide | Claude picks at planning time based on what `main` actually looks like | ✓ |

**User's choice:** You decide.
**Notes:** Recorded under Claude's Discretion, with the dedicated-file leaning stated and its reason (Phase
191 ports the same change to a branch 948 commits behind).

---

## Dead-endpoint exit code

Research presented: Unix convention is to exit non-zero whenever the command could not accomplish its task;
silent `0` on network failure is filed as a bug in the tools that do it (`az acr login`,
`actions/runner --check`).

Two corrections made to the pre-question framing after measuring: **nothing scripted invokes `fw`** in
either sub-repository, and **no test covers the `(None, None)` fall-through** — so the blast radius is
operator habit, not tooling, and flipping the return turns nothing red.

### Q1 — What should the dead-endpoint path become?

| Option | Description | Selected |
|--------|-------------|----------|
| Fail loudly — exit 1 + named message | Return `False` so `fw` exits 1, message names the endpoint URL and the failure | ✓ |
| Distinguishable message, keep exit 0 | Literally satisfies criterion 3, which only demands a message; leaves a mistaken retarget invisible to anything reading the exit code | |
| Fail only when an action was requested | Exit 1 under `--install`/`--force`/`--firmware-version`; warn and exit 0 on a bare `fw` | |

**User's choice:** Fail loudly (recommended option).
**Notes:** Recorded as D-06, rated **costly** on reversibility — an exit-code change is a behavioural
contract, and Phase 191 carries the same change to the default install.

### Q2 — Should "unreachable" and "no asset for this board" be distinguishable from each other?

| Option | Description | Selected |
|--------|-------------|----------|
| Distinct messages at the point of failure | Promote the two existing `logger.error` lines to operator-visible output; caller returns `False` generically | |
| Widen the fetch contract to carry a reason | Typed exception or a reason alongside `(None, None)`; costs a signature change plus every 2-tuple stub in at least four test files | |
| One message covers both | `Could not resolve a firmware release for <board> from <URL>`, exit 1; the operator reads the preceding log line for the cause | ✓ |

**User's choice:** One message covers both.
**Notes:** Recorded as D-07 — least surface, and the `(None, None)` contract stays intact so no monkeypatched
stub needs touching.

**Stated as a constraint rather than asked:** `--force` already exits 1 on a dead endpoint via
`firmware.py:911-915`, so the new check must not double-emit on that path (D-08). Also noted that the
default log level is `INFO` and `logger.error` is already visible — the defect is the silent `return True`
after it, not invisibility.

---

## `fw --list` scope

Research presented: an empty list is exit 0 (the command worked, the answer is "none"); a fetch error is
non-zero, with detail on stderr. Exit codes cannot carry a readable reason, so the reason belongs in the
message.

A coupling was named before the question: criterion 4's evidence is most naturally `fw --list` against the
renamed repository, and an instrument that exits 0 when it fails cannot serve as proof.

### Q1 — Is `fw --list` in URL-04's scope, and how far?

| Option | Description | Selected |
|--------|-------------|----------|
| In scope — fetch failure exits 1, empty says so | Distinguish "fetch failed" from "nothing matched"; kills the header-row-with-nothing-under-it ambiguity | ✓ |
| In scope, minimal — fetch failure exits 1 only | Leave the genuine-empty case exactly as it is | |
| Out of scope | Criterion 3's "not mistakable for already up to date" cannot apply to `--list`, which never prints that | |

**User's choice:** In scope, full (recommended option).
**Notes:** Recorded as D-09. Noted that `test_cli_handlers.py:657` asserts exit 0 on an empty list, and the
failure/empty split is precisely what keeps that test valid.

### Q2 — How does `list_releases` signal the difference?

| Option | Description | Selected |
|--------|-------------|----------|
| Return `None` on failure, `[]` on empty | `Optional[List[ReleaseInfo]]`; no new class, no `requests` import in the CLI layer | ✓ |
| Raise a typed exception from `exceptions.py` | Most explicit; costs a new exception family alongside `SerialError` / `EpromOperationError` | |
| Let `requests.RequestException` propagate | Fewest moving parts in `firmware.py`, but leaks the transport library into the CLI layer | |

**User's choice:** Return `None` on failure, `[]` on empty (recommended option).
**Notes:** Recorded as D-10. `list_releases` has exactly one production caller, so the contract change is
contained.

### Q3 — What does `fw --list --json` do on a fetch failure?

| Option | Description | Selected |
|--------|-------------|----------|
| No stdout JSON; error to stderr, exit 1 | A parser gets empty input and a non-zero status, never a well-formed `[]` describing an unobserved state | ✓ |
| JSON error object on stdout, exit 1 | Parsers always get valid JSON; costs a second output schema for `--list` | |
| Keep printing `[]` but exit 1 | Smallest change; a parser ignoring exit codes still reads `[]` as "no releases" | |

**User's choice:** No stdout JSON; error to stderr, exit 1 (recommended option).
**Notes:** Recorded as D-11. Constraint D-12 follows from it and was stated rather than asked:
`SingleLineStatusHandler` writes to stdout, so "error to stderr" cannot be a plain `logger.error` call.

---

## Criterion 4 evidence

Live measurement presented before the questions: stable `2.0.6` on `firestarter_fw` ships only `leonardo`
and `uno` assets while pre `3.0.0b29` ships all four — so `--board uno328pb --stable` is a genuine,
unmocked asset-less case.

Research presented: live smoke tests belong outside CI, run on demand, and should skip-not-fail when the
dependency is unavailable; the standard split is mocked tests in CI plus a separate live contract check.

### Q1 — What does "resolves a real firmware release end-to-end" cover?

| Option | Description | Selected |
|--------|-------------|----------|
| Resolve + download + both live failures | Both channels, a real `.hex` download, and both URL-04 failures demonstrated live | ✓ |
| Resolve + download the asset | Stops before the failure demonstrations, leaving those to mocked unit tests | |
| Resolution only | `--list` plus a version+asset-URL resolution; never fetches bytes | |

**User's choice:** Resolve + download + both live failures (recommended option).
**Notes:** Recorded as D-14/D-15. Bounded by the milestone's "Bench: none" statement — no `avrdude`.

### Q2 — What form does the demonstration take, and does any of it enter the test suite?

| Option | Description | Selected |
|--------|-------------|----------|
| Re-runnable script + transcript, not in CI | Phase 189 D-06 shape; CI stays deterministic and offline | ✓ |
| Script + transcript, plus an opt-in pytest marker | Gives the check a name for Phases 191/193 to invoke; fails confusingly on a full-suite run | |
| Transcript only | Least work now; nothing for a post-claim milestone to re-run | |

**User's choice:** Re-runnable script + transcript, not in CI (recommended option).
**Notes:** Recorded as D-16, mirroring `189-fresh-clone-fixture.sh`. The opt-in-marker option is preserved
as a deferred idea.

### Q3 — How is "Host CI is green on the milestone branch" satisfied?

| Option | Description | Selected |
|--------|-------------|----------|
| Local CI-equivalent under py3.11, recorded | Run the five `ci.yml` gate steps verbatim in a `uv venv --python 3.11`, commit the transcript | ✓ |
| Operator pushes the milestone branch | A milestone-branch push fires `ci.yml` only and publishes nothing, but is an ad-hoc outward-facing push against D-7 | |
| Local equivalent now, real CI deferred to ship | Same local run, recorded as close-carried in the Phase 189 D-08 shape | |

**User's choice:** Local CI-equivalent under py3.11, recorded (recommended option).
**Notes:** Recorded as D-17. Measured facts that framed the question: the milestone branch is not on origin;
Host CI triggers on `push: branches: ['**']`; `beta-release.yml` is `beta`-only and `publish.yml` is
release-only, so a milestone-branch push would publish nothing. The py3.11 venv is the substance — the
devcontainer is py3.12 and has previously masked real CI breakage.

---

## Claude's Discretion

- Placement of the slug-pin test (Q2 of the fixture-pin area answered "You decide"). Leaning: a dedicated
  `tests/test_endpoint_constants.py`, for portability to `main` in Phase 191.
- Exact wording of the D-06 and D-09 messages beyond naming the endpoint URL and the board.
- Shape, name, argument handling and transcript capture of the D-16 script.
- Mechanism for producing D-15's unreachable case in a throwaway process.
- Commit granularity across the constants, tests, `fw` behaviour change and evidence.

## Deferred Ideas

- A repository-wide bare-slug regression guard for `firestarter_app` — Phase 192 (SWEEP-01/02).
- Granular exit codes for `fw` (1 runtime / 2 user error) rather than the binary 0/1 split.
- A JSON error schema for `fw --list --json`, reconsidered only if a machine consumer appears.
- Stripping GSD provenance from `submit.py:59` and `meta_presence.py` — tracked as todo
  `2026-08-27-strip-gsd-provenance-comments-from-source.md`; this phase changes the slug only.
- Adding the live end-to-end check to `pytest` behind an opt-in marker.
