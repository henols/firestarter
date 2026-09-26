---
phase: 190-endpoints-that-do-not-depend-on-a-redirect
reviewed: 2026-09-13T00:00:00Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - firestarter_app/.planning/codebase/INTEGRATIONS.md
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/constants.py
  - firestarter_app/firestarter/firmware.py
  - firestarter_app/firestarter/submit.py
  - firestarter_app/tests/test_endpoint_constants.py
  - firestarter_app/tests/test_firmware_install.py
  - firestarter_app/tests/test_fw_list_failure_vs_empty.py
  - firestarter_app/tests/test_fw_update_dead_endpoint.py
  - firestarter_app/tests/test_py32_pyusb_absent.py
findings:
  critical: 0
  warning: 2
  info: 1
  total: 3
status: issues_found
---

# Phase 190: Code Review Report

**Reviewed:** 2026-09-13
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Reviewed the endpoint-rename and `None`-vs-`[]` split introduced by phase 190 across
`constants.py`, `firmware.py`, `cli_handlers.py`, `submit.py`, `INTEGRATIONS.md`, and the
five test modules covering them. The diff against `f926e36` (submodule pre-phase tip) is
small and surgical: three URL constants repointed to `henols/firestarter_fw`, `list_releases`
widened to `Optional[List[ReleaseInfo]]` with `None`/`[]` correctly discriminated by identity
(`is None`, never truthiness) at both the return site and the `fw --list` CLI handler, and a
new fall-through guard in `manage_firmware_update` that turns a previously-silent `return True`
into a named `return False` when no release could be resolved. No new comments were added to
product source (the one comment edit in `submit.py` is a slug fix inside an existing comment,
not a new one), and `SUBMIT_REPO` in `submit.py` was correctly left untouched. No stray
`henols/firestarter/` (non-`_fw`) references remain anywhere in the submodule.

The specific invariants the phase brief called out — `None`/`[]` discrimination, no
double-emit on `--force`/`--install`, no JSON document on stdout on a failed `--json --list`,
and a message naming both board and endpoint — all hold as claimed and are pinned by real
tests that were checked to actually exercise the guarded code path (not vacuously).

One real defect was found that the phase's own stated goal ("no double-emit") does not
actually hold for: the most central case of all — a genuinely dead/unreachable endpoint hit
through the default `fw` invocation (no `--install`/`--force`) — logs the error twice, and
every test asserting "exactly one ERROR record" for this guard stubs `fetch_release_info`
directly, which bypasses the exact internal logging this doubles up with. See CR-01 (kept out
of Critical because it does not affect exit codes or correctness, only diagnostic
duplication, but it directly contradicts a stated design invariant and the tests protecting
that invariant do not actually cover the path where it fires).

## Warnings

### WR-01: The new dead-endpoint guard double-logs on every real (unmocked) failure path

**File:** `firestarter_app/firestarter/firmware.py:955-962`
**Issue:** `manage_firmware_update`'s new guard fires whenever `fetch_release_info` returns
`(None, None)`:
```python
if not latest_version or not download_url:
    endpoint = _endpoint_for_channel(channel, pinned_version)
    logger.error(
        f"Could not resolve a firmware release for {board_to_use} from "
        f"{endpoint}. The installed firmware version was not compared "
        "against any release."
    )
    return False
```
But every real code path that can produce `(None, None)` from `fetch_release_info` already
calls `logger.error(...)` itself before returning:
- `fetch_latest_release_info` (stable channel): `firmware.py:268-272` (no asset/version) and
  `firmware.py:278-280` (`requests.RequestException`).
- `fetch_release_info(channel="pinned")`: `firmware.py:357-361` (fetch exception) and
  `firmware.py:365-369` (no matching asset).
- `fetch_release_info(channel="pre")`: `firmware.py:374-376` (fetch exception) and
  `firmware.py:401-406` (no matching asset on the picked pre-release); the no-candidates
  fallback path (`firmware.py:389-394`) delegates to `fetch_latest_release_info`, which
  logs its own error on failure too.

So on a genuinely dead/unreachable endpoint reached via the plain `fw` command (the exact
scenario this phase is named for), the operator sees **two** `ERROR` lines: the original
fetch failure, then the new guard's "Could not resolve a firmware release ... from
{endpoint}" line. This directly contradicts the "no double-emit" design goal the phase
brief calls out (it only explicitly checked the `--force`/`--install` variant, which is
indeed clean — those paths return earlier, inside the `if should_install_now:` block, and
never reach this guard).

This is masked by the test suite: every test in `tests/test_fw_update_dead_endpoint.py`
and every `manage_firmware_update` test in `tests/test_firmware_install.py`
(`TestManageFirmwareUpdate`) that reaches this guard **monkeypatches
`FirmwareManager.fetch_release_info` itself** to return `(None, None)` directly:
```python
monkeypatch.setattr(
    fm,
    "fetch_release_info",
    lambda channel="stable", version=None, board="uno": (
        latest_version,
        download_url,
    ),
)
```
(`tests/test_fw_update_dead_endpoint.py:52-59`). This bypasses the internal `logger.error`
calls entirely, so the "exactly one ERROR record" assertions in
`test_bare_check_with_unresolvable_release_returns_false_and_names_endpoint` and its
siblings never actually exercise the code that would produce the second line. The invariant
they claim to pin does not hold once the real `fetch_release_info` is used.

**Fix:** Either suppress the internal error logging in `fetch_latest_release_info`/
`fetch_release_info` when called from `manage_firmware_update` (e.g. have those methods
return the failure reason instead of logging directly, and let the single call site in
`manage_firmware_update` own all diagnostic output), or drop the new guard's own
`logger.error` and instead upgrade the *existing* internal message to include the board name
(most of them already do) so there is exactly one line either way. Add a test that calls
`manage_firmware_update` with the real `fetch_release_info` (only `requests.get` and
`check_current_firmware` stubbed) to prove the "exactly one ERROR" claim end-to-end.

### WR-02: `_endpoint_for_channel` can name the wrong endpoint for the `pre` channel's stable fallback

**File:** `firestarter_app/firestarter/firmware.py:155-163`, call site `firmware.py:955-956`
**Issue:**
```python
def _endpoint_for_channel(channel, version):
    if channel == "pre":
        return FIRESTARTER_RELEASES_URL
    if channel == "pinned" and version:
        return FIRESTARTER_RELEASE_BY_TAG_URL.format(tag=version)
    return FIRESTARTER_RELEASE_URL
```
`fetch_release_info(channel="pre", ...)` (`firmware.py:371-407`) paginates `/releases`
(`FIRESTARTER_RELEASES_URL`); when pagination succeeds but no prerelease candidate is found,
it silently falls back to `fetch_latest_release_info(board=board)` (`firmware.py:389-394`),
which fetches `FIRESTARTER_RELEASE_URL` (the singular `/releases/latest` endpoint) instead.
If *that* fallback fetch is what actually fails, `_endpoint_for_channel("pre", ...)` still
reports `FIRESTARTER_RELEASES_URL` (plural) in the guard's error message — naming an
endpoint that was never the one that failed. No test exercises `channel="pre"` through this
guard at all (`tests/test_fw_update_dead_endpoint.py` only covers the default/bare,
`--install`, `--force`, up-to-date, and `pinned` cases), so this inaccuracy is currently
unobserved.
**Fix:** Either have `fetch_release_info`/`fetch_latest_release_info` return which endpoint
they actually contacted (or the failure reason) so the caller reports the true source, or
have `_endpoint_for_channel("pre", ...)` acknowledge the stable-fallback case explicitly
(e.g. by threading through whether the pre-release list was empty vs. genuinely
unreachable). At minimum, add a `channel="pre"` case to
`tests/test_fw_update_dead_endpoint.py` covering both the direct-pagination-failure and
the fallback-then-fail scenarios.

## Info

### IN-01: `list_releases`'s internal error log and the CLI's own failure message overlap by design, but are visually redundant

**File:** `firestarter_app/firestarter/cli_handlers.py:1221-1227`, `firestarter_app/firestarter/firmware.py:436-439`
**Issue:** On a fetch failure, `fw --list` prints two things: `list_releases`'s own
`logger.error(f"Failed to fetch releases for list: {e}")` (routed to stdout via
`SingleLineStatusHandler`, as `tests/test_fw_list_failure_vs_empty.py`'s module docstring
confirms is intentional/D-07), and then the CLI handler's separate `click.echo(..., err=True)`
to stderr. This is deliberately covered by the test suite (see the docstring at
`tests/test_fw_list_failure_vs_empty.py:30-34`) and is not a defect, but it means an operator
piping only stderr for troubleshooting gets a generic message while the more specific
underlying `requests` exception text only ever reaches stdout. Worth a naming/wording pass
so both lines aren't needed to diagnose a failure from stderr alone.
**Fix:** Consider having `list_releases` surface the underlying exception text back to the
caller (e.g. via a second return value or a raised/caught reason string) so the CLI's
stderr-only message can include it, rather than requiring the stdout log line for detail.

---

_Reviewed: 2026-09-13_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

---

## Orchestrator assessment (execute-phase, 2026-09-13)

The code-review gate is advisory and does not block phase completion. Both warnings were
checked against the source and against this phase's locked decisions before being carried
forward. One does not survive that check.

### WR-01 — DISPUTED, and not carried as a defect

WR-01 reports that the new fall-through guard in `manage_firmware_update` double-logs on a
genuine unmocked endpoint failure, because `fetch_release_info` / `fetch_latest_release_info`
already call `logger.error` themselves, and concludes this "directly contradicts the phase's
own no-double-emit goal."

That conflates two different things, and `190-CONTEXT.md` distinguishes them explicitly:

- **D-07 decides that the fetch-internal lines stay.** Verbatim: *"The two pre-existing
  distinct `logger.error` lines inside the fetch functions **remain** for a reader who wants
  the cause."* The intended shape is a **cause** line from the fetch plus a **consequence**
  line from the guard — the latter being the only one that names the endpoint URL and the
  board, which is what URL-04 actually asks for.
- **D-08's prohibition is about two *consequence* messages** — the pre-existing force-path
  guard at `firmware.py:911-915` ("Cannot install: latest firmware URL or version for {board}
  is not available.") firing *alongside* the new guard. The review itself confirms that path
  is clean, and RESEARCH Finding 3 explains why it is structurally impossible: every branch
  inside `if should_install_now:` returns, so the fall-through is reachable only when that
  flag is false, which neither `--force` nor `--install` permits.

The behaviour WR-01 describes is therefore the decided design, not a regression, and
`evidence/190-url-04-endpoint-contract.txt` records it as such — case 4a shows the cause line
and the consequence line together.

The review's *secondary* observation is fair and worth keeping: the tests in
`test_fw_update_dead_endpoint.py` monkeypatch `fetch_release_info`, so they never exercise the
fetch-internal logging. That is true. It is not a coverage gap in the invariant being pinned,
because the fetch-internal line is by-design output rather than part of the no-double-emit
contract — but a future reader comparing the test's "exactly one ERROR record" assertion
against real-world output should know why the two differ.

### WR-02 — CONFIRMED, narrow

`_endpoint_for_channel("pre", ...)` unconditionally returns `FIRESTARTER_RELEASES_URL`, but
the `pre` channel falls back to stable when no prerelease candidate parses (see the
`fetch_release_info` docstring, *"falls back to stable if none"*). If that fallback is what
fails, the guard names `FIRESTARTER_RELEASES_URL` while the request that actually failed went
to `FIRESTARTER_RELEASE_URL`.

Real, and it does blunt URL-04's stated purpose — the phase's own specifics note says an
operator who mistyped a slug learns that *only* from seeing the endpoint actually addressed.
Narrow in practice: both constants address the same, correct repository slug, so the message
can misreport *which endpoint* was last tried but never *which repository*. Left unfixed here
rather than patched after the plans' verify legs have run; it is a candidate for the phase
verifier, or for a follow-up alongside Phase 191's port of the same constants to `main`.

### IN-01

Accepted as described — a by-design redundancy, no action.
