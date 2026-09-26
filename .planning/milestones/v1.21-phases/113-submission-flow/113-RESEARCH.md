# Phase 113: Submission Flow - Research

**Researched:** 2026-07-03
**Domain:** Host-only Python CLI — tiered GitHub issue submission (`gh` shell-out + prefilled browser URL), report sanitization, dedup fingerprint
**Confidence:** HIGH (codebase grounded; external `gh`/GitHub-URL facts verified with one MEDIUM caveat on the exact byte cap)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01 (LOCKED): Reports land in `henols/firestarter_app`, hardcoded module constant.** Both tiers point there (`gh issue create --repo henols/firestarter_app` and the browser `https://github.com/henols/firestarter_app/issues/new`). **No cwd git-remote inference** — a community tester's fork must never receive their own report.
- **D-02 (LOCKED): Fingerprint = deterministic short hash over `chip name + protocol + ordered per-step verdicts + byte-mismatch fingerprint classifications`.** Emitted as a field in the report JSON **and** surfaced in the issue **title**. Volatile fields EXCLUDED (`generated` timestamp, host version, measured VPP/VPE mV). Finer grain is deliberate (two different fault classes → distinct ids). Graceful degradation: a non-destructive run carries no verify `Fingerprint`, so its id collapses to `chip + protocol + verdicts`. Impl is stdlib `hashlib`; exact digest/length is planner's call.
- **D-03 (LOCKED): Refuse a non-submittable report.** If `is_submittable(auto_capture)` is `False` (post-112-04 = `chip`/`protocol`/`host_version` completeness, NOT provenance), `--submit` refuses and prints the failing field(s).
- **D-04 (LOCKED): Interactive-only — off-TTY does not auto-send.** On a real terminal: sanitize → preview → `Confirm.ask` → send (gh or browser). Off-TTY (piped / CI / mock seam): **print the sanitized body + the issue URL but do NOT auto-open the browser or run `gh issue create`.** No silent CI submissions.
- **D-05 (LOCKED): Oversize browser-URL body → drop JSON, then guide.** When the *encoded* URL body approaches the ~8 KB cap (escalate past ~7.5 KB encoded): drop the fenced JSON block, keep the human results table, append a note pointing to the always-saved `dev-test-<chip>.json` and/or suggesting the `gh` tier. Hard-stop before ~8 KB. `gh`'s stdin `--body-file -` path has no such cap.

### Claude's Discretion (grounded defaults)
- **Sanitization mechanism (SUB-02):** `to_dict()` is already a structural whitelist (no paths); scrub the free-text backstop vectors (`StepResult.reason`, `AutoCapture.chip_id_mismatch_reason`, `.md` Reason column) for home-dir paths, current username, serial device names. Hex/base64-encode raw byte dumps (none exist today — forward-looking). Exact regex set + sanitize-dict-vs-re-render is planner's call.
- **Issue title format:** surface dedup short-hash + chip + overall verdict, e.g. `[dev test] <chip> — <PASS/FAIL/INCONCLUSIVE> (<shorthash>)`.
- **`gh` auth detection:** `shutil.which("gh")` present AND `gh auth status` exit 0. Any non-zero / missing → browser tier. Injectable for tests.
- **Preview rendering:** reuse `rich`/`Confirm.ask` (precedent `firmware.py:20`, the `dev test --destructive` confirm). Show the exact bytes that will be sent.
- **`submit.py` internal decomposition + seam injection:** planner's call, constrained by SAFE-02 orchestrator-only and the mock-operator/injectable-subprocess test seam.

### Deferred Ideas (OUT OF SCOPE)
- **Fully-wired gist/attachment tier for verbose failure logs** → v2, SUB-F1. v1.21 only *reserves* it and escalates off the URL tier (D-05 drops JSON, never attaches).
- **Auto-merge/PR of community-confirmed DB entries** → v2, SUB-F2.
- **`gsd-inbox` triage-side auto-parse + DB-diff surfacing (INBOX-01)** and the no-auto-graduate `support_status` taxonomy lock (DISP-01/GRAD-01) → **Phase 114**. This phase *produces* the body; Phase 114 *consumes* it.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SUB-01 | `--submit` files the report via a tiered flow: `gh issue create --body-file -` (stdin, `gsd-inbox`) when gh present+authed, else a prefilled `issues/new` browser URL guarded under the ~8 KB server cap (escalate/omit JSON past ~7.5 KB encoded); gist tier reserved. | Tier detection (§Standard Stack, §gh CLI Facts); URL build + byte-measure (§Browser URL Facts); oversize escalation (§Oversize Handling). |
| SUB-02 | Report sanitized (field whitelist, local paths/PII scrubbed, byte dumps hex/base64) and shown for preview-before-submit; explicit/interactive only, never on a bare run. | to_dict() whitelist + regex scrub (§Sanitization); `Confirm.ask` preview + TTY gate (§Guardrails); `--submit` flag + `_is_interactive` (§Wiring). |
| SUB-03 | Submission carries a dedup fingerprint so repeat reports for the same chip are recognizable in triage. | `hashlib` over canonical field join, in report JSON + title (§Dedup Fingerprint). |
</phase_requirements>

## Summary

Phase 113 adds a new `firestarter/submit.py` module plus a `--submit` Click flag on the
existing `dev_test` handler (`cli_handlers.py:1751`). On `--submit` after a completed run,
`submit.py` consumes **this run's in-memory `DiagnosticReport`** — it never re-runs the sweep —
sanitizes it, previews the exact bytes to the tester, and (on an interactive confirm) files it
to the maintainer's tracker via one of two tiers: `gh issue create --repo henols/firestarter_app
--body-file - --label gsd-inbox --title "…"` (body piped over stdin, no length cap) when `gh` is
present and authenticated, else a prefilled `issues/new` browser URL whose encoded byte length is
measured and whose fenced JSON block is dropped once the encoded URL approaches GitHub's ~8 KB
server cap. Every submitted report carries a deterministic dedup short-hash (stdlib `hashlib`)
over chip identity + verdicts + fingerprint classes, surfaced in both the report JSON and the
issue title. The whole module is stdlib-only (`shutil`, `subprocess`, `webbrowser`,
`urllib.parse`, `hashlib`, `getpass`, `sys`, `re`, `base64`) plus the already-present `rich` —
**zero new third-party dependency** — and is orchestrator-only (SAFE-02): it sets no VPP, builds
no wire dict, adds no firmware dispatch entry.

**Primary recommendation:** Build `submit.py` as a set of small pure/seam-injected functions
(`which_fn=shutil.which`, `run_fn=subprocess.run`, `browser_open=webbrowser.open`,
`isatty_fn=_is_interactive`, `confirm_fn=Confirm.ask` — all keyword-injectable with real
defaults, mirroring the `prompt_provenance(ask=, confirm=)` and `_is_interactive` seams). Compute
the dedup fingerprint as a helper in `diagnostic_report.py` and add it to `to_dict()` so it lands
in the JSON automatically (preserving that module's single-source invariant); `submit.py` reads
it back for the title. Sanitize the **dict** (a recursive string-scrub over `to_dict()` output),
not a re-render, so both the fenced JSON and the human table derive from the same scrubbed source.

**One HIGH-confidence external gotcha the planner must reconcile (see §Common Pitfalls #1):**
the browser-URL `labels=gsd-inbox` param only applies for a user with label-add permission on the
target repo; a community stranger (no write access) gets the label dropped or a 404 page. And the
`gh --label gsd-inbox` path *fails the whole create* if the label does not already exist in
`henols/firestarter_app`. The `gsd-inbox` label existing in the repo is a maintainer prerequisite;
the browser tier should treat the label as best-effort (recommend an issue-template carrying the
label, or omit the param and rely on the title marker + fenced-JSON `schema_version` for triage).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Detect `gh` presence + auth | Host CLI (`submit.py`) | — | `shutil.which` + `subprocess` probe; no network/hardware |
| File issue via `gh` | Host CLI → external `gh` process | GitHub API (via gh) | Shell-out is a submission concern, not a hardware path (SAFE-02) |
| File issue via browser | Host CLI → OS default browser | GitHub web form | `webbrowser.open` hands off to the OS; server enforces the URL cap |
| Sanitize report body | Host CLI (`submit.py`) | `diagnostic_report.to_dict()` whitelist | Whitelist is the guarantee; regex scrub is the backstop |
| Dedup fingerprint | `diagnostic_report.py` helper | consumed by `submit.py` (title) | Belongs in the report JSON (single source); Phase 114 also parses it |
| TTY / interactive gate | Host CLI (`_is_interactive`) | injected `isatty_fn` for tests | SUB-02 explicit-only; D-04 off-TTY no-send |
| Preview + confirm | Host CLI (`rich.Confirm`) | injected `confirm_fn` for tests | Same shape as the `--destructive` confirm |

## Standard Stack

### Core (all stdlib — zero new dependency, satisfies the milestone anti-feature)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `shutil.which` | stdlib (3.11) | Detect `gh` on PATH | Already used at `firestarter/avr_tool.py:14` (`from shutil import which`) [VERIFIED: codebase] |
| `subprocess` (`run`/`Popen`/`PIPE`) | stdlib | `gh auth status` probe + `gh issue create` shell-out with stdin body | Precedent at `avr_tool.py:15` (`from subprocess import PIPE, CalledProcessError, Popen, TimeoutExpired`) [VERIFIED: codebase] |
| `webbrowser.open` | stdlib | Open the prefilled `issues/new` URL | Standard stdlib browser hand-off; returns `bool`, may return `False`/raise on headless [CITED: docs.python.org/3/library/webbrowser] |
| `urllib.parse.urlencode` / `quote` | stdlib | Build + percent-encode the query string; measure encoded length | Standard; `urlencode` with `quote_via=quote` encodes spaces as `%20` |
| `hashlib` (`sha256`) | stdlib | Dedup fingerprint short-hash | Already imported in `chip_test.py:29` and `cli_handlers.py:20` [VERIFIED: codebase] |
| `getpass.getuser()` | stdlib | Portable current-username lookup for the PII scrub | Checks `LOGNAME`/`USER`/`LNAME`/`USERNAME` env, falls back to `pwd` [CITED: docs.python.org/3/library/getpass] |
| `re` | stdlib | Path / serial-device / username scrub regexes | — |
| `base64` | stdlib | Forward-looking raw-byte-dump encoder (no byte fields exist today) | — |
| `sys.stdin.isatty` | stdlib | TTY detection (via existing `_is_interactive`) | Precedent `cli_handlers.py:1717-1724` [VERIFIED: codebase] |

### Supporting (already project dependencies — not new)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `rich.prompt.Confirm` | present | Interactive confirm before send | Precedent `firmware.py:20`, `cli_handlers.py:32`, the `--destructive` confirm at `cli_handlers.py:1817` [VERIFIED: codebase] |
| `rich.console.Console` | present | Preview rendering | `cli_handlers.py:31` [VERIFIED: codebase] |
| `click` | present | The `--submit` flag on `dev_test` | `cli_handlers.py:29` [VERIFIED: codebase] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `gh` shell-out | `requests` + PAT to REST API | Rejected: needs a stored token, more auth surface; `gh` is an optional runtime tool per Out-of-Scope row, `requests` submission is not the design |
| `subprocess.run(input=…)` | `Popen`+`communicate()` | `run(..., input=body, capture_output=True, text=True)` is simpler and equally injectable; use it unless a streaming edge case demands `Popen` |
| Fingerprint in `submit.py` | Fingerprint helper in `diagnostic_report.py` | Recommend `diagnostic_report.py`: it lands in `to_dict()` JSON automatically (single-source) and Phase-114 triage parses it there |

**Installation:** No install step. All submission primitives are Python stdlib; `rich`/`click`
are already declared. `gh` is an optional runtime tool the tester may or may not have — detected,
never required, never a pip dependency.

## Package Legitimacy Audit

**Not applicable — this phase installs zero external packages.** Every submission primitive is
Python standard library (`shutil`, `subprocess`, `webbrowser`, `urllib.parse`, `hashlib`,
`getpass`, `re`, `base64`, `sys`), and `rich`/`click` are pre-existing project dependencies. The
milestone Out-of-Scope table explicitly forbids new third-party Python dependencies; `gh` is an
optional runtime CLI tool detected via `shutil.which`, not a pip package.

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none.

## Architecture Patterns

### System Architecture Diagram

```
firestarter dev test <chip> --submit
        │
        ▼
 dev_test handler (cli_handlers.py:1751)
   builds DiagnosticReport ──► render() to stdout ──► ALWAYS persist dev-test-<chip>.{json,md}
        │                                                    │ (json_file path)
        │ report (in-memory) + json_file path                │
        ▼                                                     ▼
 submit.submit_report(report, chip, saved_json_path, *seams)
        │
        ├─► [D-03] is_submittable(report.auto_capture)? ──NO──► print failing field(s), return (no send)
        │            YES
        ▼
   sanitize_dict(report.to_dict())          # recursive string scrub: home paths, serial, username
        │
        ├─► build body (human table markdown + fenced JSON block from sanitized dict)
        ├─► build title  "[dev test] <chip> — <PASS/FAIL/INCONCLUSIVE> (<shorthash>)"
        ▼
   [D-04] isatty_fn()?
        │
   ┌────┴───────────────────────────┐
   NO (off-TTY / CI / mock)          YES (real terminal)
   │                                 │
   print sanitized body + issue URL  preview (rich) ──► confirm_fn("Submit this report?")
   DO NOT open browser / run gh                          │           │
                                                        NO           YES
                                                     abort           │
                                              ┌──────────────────────┴──────────┐
                                              ▼                                  ▼
                                    which_fn("gh") AND                  (no gh / not authed)
                                    gh auth status == 0                        │
                                              │                                ▼
                                   run_fn(["gh","issue","create",     build issues/new URL,
                                     "--repo","henols/firestarter_app", urlencode(title,body,labels)
                                     "--label","gsd-inbox",                    │
                                     "--title",title,                  measure len(url.utf-8)
                                     "--body-file","-"], input=body)          │
                                              │                     >7.5KB? drop JSON block, re-encode
                                     capture stdout → issue URL      >~8KB? hard-stop (print, no open)
                                     echo URL to tester                       │
                                                                     browser_open(url)
```

### Recommended Module Structure (`firestarter/submit.py`)

```
firestarter/submit.py
├── SUBMIT_REPO = "henols/firestarter_app"      # D-01 hardcoded constant
├── GSD_INBOX_LABEL = "gsd-inbox"
├── _URL_ESCALATE_BYTES = 7500   # drop JSON past this (D-05)
├── _URL_HARD_CAP_BYTES = 8000   # hard-stop before GitHub's ~8191 server cap
├── PII/path scrub regexes (module constants)
├── sanitize_dict(d) -> dict                    # SUB-02 recursive string scrub
├── overall_verdict(results) -> str             # PASS/FAIL/INCONCLUSIVE for the title
├── build_body(sanitized_dict, results, *, include_json=True) -> str
├── build_issue_url(title, body) -> str         # urlencode; caller measures + escalates
├── gh_available(*, which_fn, run_fn) -> bool    # shutil.which + gh auth status exit 0
├── submit_via_gh(title, body, *, run_fn) -> str|None    # returns created URL (stdout)
├── submit_via_browser(title, body, saved_json_path, *, browser_open) -> str  # w/ D-05 escalation
└── submit_report(report, chip, saved_json_path, *, which_fn=shutil.which,
        run_fn=subprocess.run, browser_open=webbrowser.open,
        isatty_fn=_is_interactive-equivalent, confirm_fn=Confirm.ask, console=None) -> None
```

### Pattern 1: Seam-injected callables with real defaults
**What:** Every side-effecting boundary (`which`, `subprocess.run`, `webbrowser.open`, TTY check,
confirm) is a keyword argument with a real default, so unit tests monkeypatch by passing a mock —
never touching PATH, network, browser, or a real terminal.
**When to use:** All of `submit.py`.
**Example:**
```python
# Mirrors the prompt_provenance(ask=, confirm=) injection style + cli_handlers.py _is_interactive
def submit_report(report, chip, saved_json_path, *,
                  which_fn=shutil.which, run_fn=subprocess.run,
                  browser_open=webbrowser.open, isatty_fn=None,
                  confirm_fn=Confirm.ask, console=None):
    ...
```
Test seam mirrors `tests/test_dev_test_cmd.py` `make_app_context` + `Mock(spec=…)` and the
`patch("firestarter.cli_handlers._is_interactive", …)` idiom (patch the function, NOT
`sys.stdin.isatty`, because `CliRunner.invoke` swaps `sys.stdin`) [VERIFIED: codebase,
`cli_handlers.py:1717-1724` docstring + `test_dev_test_cmd.py:1-20`].

### Pattern 2: gh shell-out with stdin body (no cap)
**What:** Pipe the full (uncapped) body over stdin via `--body-file -`; capture stdout for the URL.
**Example:**
```python
proc = run_fn(
    ["gh", "issue", "create",
     "--repo", "henols/firestarter_app",
     "--label", "gsd-inbox",
     "--title", title,
     "--body-file", "-"],
    input=body, text=True, capture_output=True, check=False,
)
if proc.returncode == 0:
    created_url = proc.stdout.strip()   # gh prints the issue URL to stdout on success
```
[VERIFIED: cli.github.com/manual/gh_issue_create — "Read body text from file (use \"-\" to read
from standard input)"; the manual's examples show the created issue URL printed to stdout.]

### Anti-Patterns to Avoid
- **Re-running the sweep on `--submit`.** The report is in memory and already persisted; consume
  it. (CONTEXT §Phase Boundary, §Reusable Assets.)
- **cwd git-remote inference for the target repo.** D-01 forbids it — hardcode
  `henols/firestarter_app`.
- **Measuring the *unencoded* body length.** GitHub's cap is on the *encoded* URL bytes; encode
  first, then measure `len(url.encode("utf-8"))`.
- **Opening the browser / running `gh` off-TTY.** D-04 — print and stop.
- **Constructing a wire-shaped dict or a `--force` literal in `submit.py`.** Would trip SAFE-03
  (see §Common Pitfalls #4).
- **Blocking on `gh` interactive prompts.** Always pass `--title`, `--body-file`, `--repo`,
  `--label` so `gh` never prompts; `capture_output=True` + explicit stdin body prevents a hang.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Percent-encoding the query | Manual `%`-escaping | `urllib.parse.urlencode(..., quote_via=quote)` | Handles spaces, unicode, reserved chars correctly |
| Current username | Parse `$HOME`/`/etc/passwd` | `getpass.getuser()` | Portable across Linux/macOS/Windows env vars |
| Finding `gh` | Scan PATH dirs | `shutil.which("gh")` | Handles PATHEXT on Windows, exec-bit on POSIX |
| Detecting auth | Parse `~/.config/gh/hosts.yml` | `gh auth status` exit code | Robust to token env vars, enterprise hosts, expiry |
| Report → dict | New serializer | `report.to_dict()` (already the single source) | `diagnostic_report.py:346` already whitelists fields |
| Byte-diff / verdict logic | Recompute | Read `StepResult.verdict` / `.fingerprint.classification` | Phase 108 froze these |

**Key insight:** The report model was deliberately built so `to_dict()` is the ONE canonical
mapping both renders consume (`diagnostic_report.py:346-363` docstring). Sanitizing and
fingerprinting must respect that — scrub/hash the dict, do not fork a second field list.

## Sanitization (SUB-02) — grounded field & regex set

**The whitelist is the guarantee; the scrub is the backstop.** `to_dict()`
(`diagnostic_report.py:346`) emits only a fixed field set — no filesystem paths, no arbitrary
data. The only *free-text* leak vectors are exception/reason strings that may embed a path or
device name:

| Leak vector | Exact source | Risk |
|-------------|--------------|------|
| `StepResult.reason` | `chip_test.py:481` field; populated from `str(exc)` of `EpromOperationError`/`resolve_chip` refusals (`chip_test.py:698-708`, `_run_step`), and template strings (`_dispatch_multi_run:926`, `_dispatch_read:810`, `_dispatch_id:764-768`) | An operator/serial exception can embed a device name (`/dev/ttyACM0`) or a temp path (`C:\Users\<user>\AppData\Local\Temp\...` on Windows, which leaks the username) |
| `AutoCapture.chip_id_mismatch_reason` | `diagnostic_report.py:93`, filled from the id-step reason via `_chip_id_fields` (`cli_handlers.py:1705-1714`) | Hex ids only today — low risk, scrub anyway for uniformity |
| `.md` Reason column | `cli_handlers.py:1890-1891` (`r.reason`) | Same content as `StepResult.reason` — covered by scrubbing the dict, since the md body is rebuilt from the sanitized dict |
| `hw_revision` / `fw_board_identity` | `diagnostic_report.py:87-88` | Coarse bucket string / `None` today — no PII |
| Raw byte dumps | none exist in `to_dict()` today | Forward-looking guard: base64-encode any `bytes` leaf |

**Recommended approach — sanitize the DICT (not re-render):** `submit.py` calls
`report.to_dict()`, deep-copies it, and runs a recursive string-scrubber over every string leaf,
then builds BOTH the human table text and the fenced JSON block from the scrubbed dict. This
covers the JSON block and the derived `.md`/preview table in one pass and is future-proof if a new
free-text field is added.

**Concrete regex set (module constants):**
```python
import re, getpass
_USER = re.escape(getpass.getuser())
_SCRUBS = [
    (re.compile(r"/home/[^/\s:]+"), "/home/<user>"),
    (re.compile(r"/Users/[^/\s:]+"), "/Users/<user>"),
    (re.compile(r"C:\\Users\\[^\\\s:]+", re.IGNORECASE), r"C:\\Users\\<user>"),
    (re.compile(r"/dev/tty(ACM|USB)\d+"), "/dev/tty<redacted>"),
    (re.compile(r"/dev/tty\.[\w-]+"), "/dev/tty<redacted>"),   # macOS
    (re.compile(r"\bCOM\d+\b"), "COM<redacted>"),               # Windows serial
    (re.compile(r"/tmp/[^\s:]+"), "/tmp/<redacted>"),
]
# Username scrub is applied only if getuser() is non-trivial (len >= 3) to avoid
# over-scrubbing a short/common token; the home-dir rules already catch it in path context.
if len(getpass.getuser()) >= 3:
    _SCRUBS.append((re.compile(rf"\b{_USER}\b"), "<user>"))
```
Byte-dump guard: in the recursive scrubber, `if isinstance(v, bytes): v = base64.b64encode(v).decode()`.

[VERIFIED: codebase for all cited file:line leak vectors. Regex set is [ASSUMED] — sound but must
be reviewed against the actual reason strings the operator produces on the target platforms; a
missed vector fails open (leaks), so the planner should add a test asserting each vector is
scrubbed.]

## Dedup Fingerprint (SUB-03, D-02)

**Where it lives:** add a helper in `diagnostic_report.py` and include its output in `to_dict()`
so it lands in the JSON automatically (single-source invariant) and Phase-114 triage can parse it;
`submit.py` reads `report.to_dict()["dedup_fingerprint"]` for the title.

**Inputs (deterministic, volatile fields EXCLUDED):**
- `auto_capture.chip` (`diagnostic_report.py:89`)
- `auto_capture.protocol` (`diagnostic_report.py:93`; set to `str(prog.get("algorithm"))` at
  `cli_handlers.py:1862`)
- ordered per-step `(op, verdict)` — `StepResult.op` / `.verdict` (`chip_test.py:479-480`),
  vocabulary `OK`/`BAD`/`NA`/`SKIPPED`/`marginal` (`chip_test.py:445-449`)
- per-step `fingerprint.classification` when present — `Fingerprint.classification`
  (`chip_test.py:135`), one of `blank/contact`/`address-line`/`transport`/`indeterminate`
  (`chip_test.py:114-117`). Absent on non-destructive runs (fingerprint attached only to
  write/verify, `chip_test.py:483`) → the id naturally collapses to `chip+protocol+verdicts`
  (D-02 graceful degradation, verified against the code path).

**EXCLUDE** (volatile): `generated` timestamp (`diagnostic_report.py:355`), `host_version`,
measured `vpp_*_mv`/`vpe_*_mv` (`diagnostic_report.py:254-259`), `error_code`, and free-text
`reason` (which carries the scrubbable PII — must not enter the hash anyway).

**Impl:**
```python
def dedup_fingerprint(report) -> str:
    ac = report.auto_capture
    parts = [ac.chip or "", str(ac.protocol or "")]
    for r in report.results:
        cls = r.fingerprint.classification if r.fingerprint else ""
        parts.append(f"{r.op}={r.verdict}:{cls}")
    canonical = "|".join(parts)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]  # length is planner's call
```
[VERIFIED: codebase for every field/vocabulary reference. Digest length (8–12 hex chars) is
Claude's discretion per D-02.]

**Overall verdict for the title** (submit.py-local; cosmetic, not the process exit code): FAIL if
any step verdict is `BAD`, else INCONCLUSIVE if any `marginal`, else PASS. Note: this is *not* the
same as the handler's exit-code `max()` at `cli_handlers.py:1901` (where `marginal=2 > BAD=1`,
`cli_handlers.py:1657-1660`) — the title verdict should read FAIL-dominant for human legibility;
do not reuse `_verdict_code` for the title.

## gh CLI Facts (verified)

- **Auth detection:** `gh auth status` exits `0` when authenticated, `1` on any auth issue, and
  writes its human output to **stderr** (stdout stays empty). [VERIFIED: cli.github.com/manual/
  gh_auth_status; cli/cli PR #9240 "Exit with 1 on authentication issues"; cli/cli #7447 "writes
  to stderr instead of stdout on success"]. **Caveat [ASSUMED→verify]:** very old `gh` (≈2.42.x,
  before PR #9240 landed ~2.44) had a bug returning `0` even when unauthenticated (cli/cli #8845).
  Mitigation: this is safe — if a stale `gh` falsely reports authed, `gh issue create` surfaces
  its own error and the tester sees it in the preview/echo; the browser tier remains the safe
  default. Detect via `run_fn(["gh","auth","status"], capture_output=True, check=False).returncode == 0`.
- **`gh issue create`:** `--body-file -` reads the body from stdin; `--label` adds labels by name;
  `--title`, `--repo [HOST/]OWNER/REPO`. On success it prints the created issue URL to **stdout**
  (capture it for the confirmation echo). [VERIFIED: cli.github.com/manual/gh_issue_create]
- **`--label` requires the label to already EXIST in the repo** — otherwise `gh` errors with
  `could not add label: 'gsd-inbox' not found` and **creates no issue** (non-zero exit).
  [VERIFIED: cli/cli #3284; community discussion #35377]. → Maintainer prerequisite: create the
  `gsd-inbox` label in `henols/firestarter_app` once. Defensive option: on a create failure whose
  stderr matches `not found`, retry once without `--label` and surface a note. (Planner's call;
  simplest is to document the prerequisite — Phase 114 triage needs the label to exist anyway.)

## Browser URL Facts (verified)

- **Endpoint + params:** `https://github.com/OWNER/REPO/issues/new?title=…&body=…&labels=…`.
  Supported query params: `title`, `body`, `labels`, `milestone`, `assignees`, `projects`,
  `template`. Multiple labels: repeat `labels[]=`. [VERIFIED: docs.github.com "Using query
  parameters to create an issue"]
- **Server URL cap:** GitHub enforces a serverside limit of **~8191 bytes** on the full issues/new
  URL; exceeding it returns a `414`/error page. [CITED: github/docs issue #5136 "Document GitHub
  serverside limit on URL length"]. **This is community-documented, not in GitHub's official docs —
  treat 8191 as MEDIUM-confidence.** The CONTEXT figures (~8 KB cap, escalate past ~7.5 KB) are
  consistent with it; the 7.5 KB escalate + ~8 KB hard-stop leave a safe margin. Measure
  `len(url.encode("utf-8"))` on the fully-encoded URL (bytes, not characters).
- **`webbrowser.open(url)`** launches the OS default browser, returns `bool` ("not necessarily
  meaningful"), and on a headless machine may return `False` or raise `webbrowser.Error`. Only
  called on a real TTY (D-04). [CITED: docs.python.org/3/library/webbrowser]

## Oversize Handling (D-05)

1. Build the full body = human results table (markdown) + fenced JSON block (from the sanitized
   dict).
2. Build the URL with all params encoded; measure `n = len(url.encode("utf-8"))`.
3. If `n > _URL_ESCALATE_BYTES (7500)`: rebuild the body **without** the fenced JSON block, keep
   the table, append a note: *"Full machine-readable report saved locally at
   `dev-test-<chip>.json` — attach it to this issue, or re-run with the `gh` CLI installed to file
   the complete report automatically."* Re-encode.
4. If still `n > _URL_HARD_CAP_BYTES (~8000)`: **hard-stop** — do not open the browser; print the
   URL (or an abbreviated instruction) and the local JSON path, and tell the tester to use the
   `gh` tier. (A single-chip sweep is normally a few KB and fits — this is the safety valve.)
5. The **`gh` tier has no cap** (stdin `--body-file -`) and always carries the full body incl. the
   fenced JSON. [VERIFIED: gh manual — file/stdin body]
6. The gist/attachment tier is **RESERVED, not wired** (SUB-F1 → v2). Do not implement it.

**The `dev-test-<chip>.json` the note points to** is written unconditionally at
`cli_handlers.py:1881-1882` (`json_file = out_path / f"dev-test-{safe_chip}.json"`), default
`<config dir>/reports`. Pass that resolved path into `submit_report` so the note prints the real,
already-scrubbed-for-filename location (use just the filename in the public body, not the full
`out_path`, to avoid leaking the tester's home dir — the full path is a local hint printed to
their own console, not embedded in the issue body).

## Guardrails (D-03, D-04)

- **D-03 refuse-gate:** call `is_submittable(report.auto_capture)` (`diagnostic_report.py:150`,
  auto-capture-only: `chip` ∧ `protocol` ∧ `host_version`). If `False`, print which of the three
  is empty and return without sending. `submit.py` should re-derive the failing field names
  (`is_submittable` returns only a bool):
  ```python
  missing = [n for n, v in (("chip", ac.chip), ("protocol", ac.protocol),
                            ("host_version", ac.host_version)) if not v]
  ```
- **D-04 TTY gate:** reuse the `_is_interactive()` pattern (`cli_handlers.py:1717-1724`,
  `sys.stdin.isatty()`), injectable so tests patch it. On a TTY: preview the exact body (rich
  Console) → `Confirm.ask("Submit this report to henols/firestarter_app?", default=False)` → send.
  Off-TTY: print the sanitized body + the issue URL, and **return without** opening the browser or
  running `gh`. (Do NOT reuse the `-y/--yes` destructive-bypass for submission — SUB-02 wants an
  explicit submit confirm regardless; `--yes` is scoped to the `--destructive` chip-sacrifice
  prompt at `cli_handlers.py:1816`.)

## Wiring Point + Test Seams

- **Flag:** add `@click.option("--submit", is_flag=True, default=False, help=…)` to the `dev_test`
  decorator stack (`cli_handlers.py:1751-1781`) and a `submit: bool` parameter to `def dev_test(…)`
  (`cli_handlers.py:1783-1789`).
- **Call site:** after the report is rendered and persisted — i.e. after `cli_handlers.py:1897`
  (`console.print("Report written to …")`) and **before** the `sys.exit(code)` at
  `cli_handlers.py:1899-1902`. Pass the in-memory `report`, `chip`, and the `json_file` path:
  ```python
  if submit:
      from firestarter import submit as submit_mod
      submit_mod.submit_report(report, chip, json_file, console=console)
  ```
  Import lazily (or at top) — lazy keeps `submit.py` off the import path of every other command.
- **Test seam:** mirror `tests/test_dev_test_cmd.py` — `CliRunner`, `make_app_context()` with
  `EpromDatabase(skip_local_override=True)` + `Mock(spec=…)` managers, and patch
  `firestarter.cli_handlers._is_interactive`. For `submit.py` unit tests, call `submit_report`
  directly with mock `which_fn`/`run_fn`/`browser_open`/`isatty_fn`/`confirm_fn` — never touch
  PATH, network, or a browser. Assert: tier selection (gh present+authed vs not), the exact `gh`
  argv, stdin body content (sanitized), the encoded-URL byte measurement + JSON-drop at the
  threshold, off-TTY no-send, D-03 refusal messaging, and that each PII vector is scrubbed.

## SAFE-03 Orchestrator Checker (`tools/check_devtest_orchestrator.py`)

The checker today scans `chip_test.py` **in full** (`_scan_file`) and `cli_handlers.py` **scoped**
to `_HANDLER_FUNCTION_NAMES` (`dev_test` + its private helpers), via `main()`
(`check_devtest_orchestrator.py:320+`). It denies: VPP-set call names (`_VPP_SET_NAMES`), raw
wire-dict literals (≥2 keys from `_WIRE_DICT_KEYS`), and `force=True`/`"--force"`.

**Findings for `submit.py`:**
- `submit.py` is **not currently in the scan set.** The `gh` shell-out lives in `submit.py`, not
  in `dev_test`, so it will **not** false-positive the scoped `cli_handlers.py` scan.
- `submit.py` is **clean against all three deny buckets** by construction: it sets no VPP (no
  `set_vpp`/`enable_vpp`/…); the `gh` argv is a **list**, not a dict, so `visit_Dict` never fires;
  and it contains no `--force` literal (gh args are `--repo`/`--label`/`--title`/`--body-file`).
- **Recommendation:** ADD `submit.py` as a THIRD full-scan target (a new `FIRESTARTER_DEVTEST_SUBMIT`
  env-overridable path constant + a `_scan_file` call appended to `main()`'s `scanned`/violation
  aggregation, and included in `_assert_host_only`). It is a fresh orchestrator module with zero
  pre-existing `--force` usage (like `chip_test.py`), so a full scan is safe and tightens the
  contract. Confirm the paired negative-fixture pytest (`tests/test_check_devtest_orchestrator.py`)
  still passes and, ideally, add a fixture proving the new target leg flips red on a planted
  violation (D-03 anti-hollow contract). This is the SAFE-03 non-regression obligation for the
  new module. [VERIFIED: codebase — checker structure at check_devtest_orchestrator.py:320-405]

## Common Pitfalls

### Pitfall 1: Browser `labels=gsd-inbox` silently drops (or 404s) for community testers
**What goes wrong:** The design says the browser tier auto-labels `gsd-inbox`. But the GitHub
issues/new `labels` param **requires the user to have permission to add labels** — a stranger
with no write access to `henols/firestarter_app` either has the label dropped or gets a `404 Not
Found` page. [VERIFIED: docs.github.com — "you must have permission to add a label … or the URL
will return a 404 Not Found error page"; community discussion #22510 "Labels not applying for
non-write users"]
**Why it happens:** Labeling is a triage-permission action; outside contributors don't have it.
**How to avoid:** For the browser tier, treat the label as best-effort. Two robust options for the
planner: (a) **omit** `labels` from the browser URL and rely on the title marker `[dev test]` +
the fenced-JSON `schema_version` for Phase-114 triage discovery; or (b) ship an issue-form/template
in `henols/firestarter_app` (`.github/ISSUE_TEMPLATE/dev-test-report.*`) whose front-matter carries
`labels: [gsd-inbox]` — a template applies its labels **server-side on submission regardless of the
submitter's permission** — and point the browser URL at `?template=dev-test-report.md`. The `gh`
tier (authenticated maintainer/contributor) can pass `--label gsd-inbox` directly.
**Warning signs:** Community-submitted issues arrive unlabeled; testers report a 404 page.

### Pitfall 2: `gh --label gsd-inbox` fails the whole create if the label doesn't exist
**What goes wrong:** `could not add label: 'gsd-inbox' not found` → non-zero exit, **no issue
created**, tester's report lost.
**How to avoid:** Maintainer prerequisite — create the `gsd-inbox` label in the repo once (Phase
114 needs it anyway). Optionally, `submit.py` catches a `not found` stderr and retries without
`--label`, surfacing a note. [VERIFIED: cli/cli #3284]

### Pitfall 3: Measuring the unencoded body against the cap
**What goes wrong:** The body fits by char count but the percent-encoded URL blows past 8 KB
(each unsafe byte becomes 3 chars `%XX`; a JSON block full of `"`, `{`, spaces, newlines expands
~1.5–3×). The browser then shows a 414/blank page.
**How to avoid:** Build the full encoded URL first, then measure `len(url.encode("utf-8"))`.
Escalate/drop JSON at 7.5 KB encoded, hard-stop before ~8 KB.

### Pitfall 4: Tripping SAFE-03 from `submit.py`
**What goes wrong:** Adding a dict literal that happens to carry ≥2 wire-protocol keys, a
`force=True` kwarg, or the string `"--force"` anywhere in `submit.py` (or in the scanned `dev_test`
helpers) turns the SAFE-03 gate red.
**How to avoid:** Keep `gh` args as a **list**, never a dict; never write `force=`/`"--force"`.
The only user-facing "force"-like concept here is submission consent (handled by `Confirm.ask`),
which uses no such token.

### Pitfall 5: `gh` hangs waiting for interactive input
**What goes wrong:** Omitting `--title` or `--body-file` makes `gh issue create` prompt
interactively; under `subprocess` with a captured stdin/stdout it can hang or error.
**How to avoid:** Always supply `--title` + `--body-file -` + `--repo` + `--label`; pass the body
via `input=`; `capture_output=True`; `check=False` and inspect `returncode` yourself.

## Runtime State Inventory

Not applicable — Phase 113 is greenfield host-only code (a new `submit.py` + one `--submit` flag).
It stores no data, registers no OS-level state, defines no new secret/env var, and produces no
build artifact beyond the normal pip package. No rename/refactor/migration is involved.

## Code Examples

### Building + measuring the prefilled URL (D-05)
```python
from urllib.parse import urlencode, quote

def build_issue_url(title: str, body: str, *, include_label: bool) -> str:
    params = {"title": title, "body": body}
    if include_label:
        params["labels"] = "gsd-inbox"   # best-effort; see Pitfall 1
    query = urlencode(params, quote_via=quote)
    return f"https://github.com/henols/firestarter_app/issues/new?{query}"

url = build_issue_url(title, full_body, include_label=True)
if len(url.encode("utf-8")) > 7500:                 # escalate: drop JSON
    url = build_issue_url(title, table_only_body_with_note, include_label=True)
if len(url.encode("utf-8")) > 8000:                 # hard-stop
    print("Report too large for a browser URL — use `gh` or attach dev-test-<chip>.json")
    return
browser_open(url)                                    # only on a TTY (D-04)
```
[Pattern verified against urllib/webbrowser stdlib semantics; thresholds per D-05.]

### gh tier with captured URL echo
```python
proc = run_fn(["gh", "issue", "create", "--repo", "henols/firestarter_app",
               "--label", "gsd-inbox", "--title", title, "--body-file", "-"],
              input=body, text=True, capture_output=True, check=False)
if proc.returncode == 0:
    console.print(f"[green]Filed:[/green] {proc.stdout.strip()}")
else:
    console.print(f"[yellow]gh failed:[/yellow] {proc.stderr.strip()}")
    # fall back to browser tier or surface the error
```
[VERIFIED: gh manual — stdin body + stdout URL.]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `gh auth status` always exit 0 | Exits 1 on auth failure | cli/cli PR #9240 (~gh 2.44) | Exit-code auth detection is reliable on modern gh; guard for stale gh |
| Fixed `--body` string | `--body-file -` stdin | long-standing | Uncapped body over stdin; the gh tier carries the full JSON |
| Manual issue labeling | issue-form template `labels:` front-matter | GitHub issue forms GA | Server-side labels regardless of submitter permission (Pitfall 1 fix) |

**Deprecated/outdated:** none relevant. All chosen primitives are current stdlib / current gh.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | GitHub issues/new server URL cap is ~8191 bytes | Browser URL Facts / Oversize | Community-documented (github/docs #5136), not official. If lower, some large reports 414; the 7.5 KB escalate + ~8 KB hard-stop already leave margin. Planner: keep conservative thresholds. |
| A2 | Very old `gh` (<~2.44) may return exit 0 when unauthenticated | gh CLI Facts | A stale gh could pick the gh tier while unauthed → `gh issue create` fails; tester sees the stderr echo. Safe (browser is the default fallback), but note in help text. |
| A3 | The proposed PII regex set covers the real leak vectors | Sanitization | A missed vector fails **open** (leaks a path/username). Planner MUST add a test asserting each vector is scrubbed and review actual operator/serial exception strings on Linux/macOS/Windows. |
| A4 | Browser `labels` param drops/404s for non-write users | Pitfall 1 | HIGH-confidence (GitHub docs), but exact behavior (silent drop vs 404) varies by report. Recommend template-based labeling or omit the param. |
| A5 | `gh --label` fails create if label absent | Pitfall 2 | HIGH-confidence. Mitigated by the maintainer prerequisite; optional retry-without-label. |

**If this table is empty:** it is not — A1–A5 need the planner's attention (esp. A3, which fails
open, and A4/A5, which affect whether the `gsd-inbox` label actually lands).

## Open Questions

1. **Should the `gsd-inbox` issue-template ship in this phase or Phase 114?**
   - Known: an issue-form template with `labels: [gsd-inbox]` is the robust way to get the label
     on community-submitted (browser-tier) issues (Pitfall 1). It lives in
     `henols/firestarter_app/.github/ISSUE_TEMPLATE/`.
   - Unclear: whether authoring that template is in scope for Phase 113 (submission producer) or
     Phase 114 (`gsd-inbox` triage consumer).
   - Recommendation: Phase 113 should at minimum add `?template=dev-test-report.*` to the browser
     URL and flag the template as a dependency; the planner decides which phase authors the file.
     Fallback that needs no repo change: omit `labels`, rely on the title marker + fenced JSON.

2. **Retry-without-label on a `gh not found` failure, or document the prerequisite?**
   - Recommendation: document the one-time `gsd-inbox` label creation as a maintainer prerequisite
     (Phase 114 needs it regardless); a defensive retry-without-label is a nice-to-have, not
     required.

3. **Digest length for the dedup short-hash (D-02 leaves it to the planner).**
   - Recommendation: first 12 hex chars of sha256 — collision-safe at this scale, short enough for
     a title.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `gh` CLI | Preferred submit tier (SUB-01) | optional (detected at runtime via `shutil.which`) | — | Prefilled browser URL tier (always available) |
| Default web browser | Browser submit tier | optional (OS-dependent) | — | Off-TTY / headless: print the URL, tester opens manually (D-04) |
| Python stdlib | All submission primitives | ✓ (3.11 target) | 3.11 | — |
| `rich` / `click` | Preview + flag | ✓ (declared deps) | present | — |

**Missing dependencies with no fallback:** none — the browser-URL tier needs no external tool;
if no browser can be opened, the URL is printed for manual use.
**Missing dependencies with fallback:** `gh` (→ browser tier); interactive browser (→ printed URL).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest` + `click.testing.CliRunner` + `unittest.mock` [VERIFIED: tests/test_dev_test_cmd.py] |
| Config file | `pyproject.toml` (`.[test]` extra); CI at `.github/workflows/ci.yml` |
| Quick run command | `pytest tests/test_submit.py -x` (new file) |
| Full suite command | `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SUB-01 | gh tier chosen when `which_fn` finds gh AND auth exit 0; correct argv + stdin body | unit | `pytest tests/test_submit.py -k gh_tier -x` | ❌ Wave 0 |
| SUB-01 | browser tier when no gh / not authed; URL params correct | unit | `pytest tests/test_submit.py -k browser_tier -x` | ❌ Wave 0 |
| SUB-01 | encoded-URL byte measure + JSON drop past 7.5 KB, hard-stop past ~8 KB | unit | `pytest tests/test_submit.py -k oversize -x` | ❌ Wave 0 |
| SUB-02 | each PII vector (home path, /dev/tty*, COM*, username, temp) scrubbed | unit | `pytest tests/test_submit.py -k sanitize -x` | ❌ Wave 0 |
| SUB-02 | off-TTY prints, does NOT open browser / run gh; TTY confirm gate | unit | `pytest tests/test_submit.py -k tty -x` | ❌ Wave 0 |
| SUB-02 | D-03 refusal prints missing field(s) when `is_submittable` False | unit | `pytest tests/test_submit.py -k refuse -x` | ❌ Wave 0 |
| SUB-03 | dedup hash deterministic; identical outcome → same id; excludes volatile fields | unit | `pytest tests/test_diagnostic_report.py -k dedup -x` | ❌ Wave 0 |
| SUB-03 | fingerprint appears in to_dict() JSON AND is used in the title | unit | `pytest tests/test_submit.py -k title -x` | ❌ Wave 0 |
| SAFE-03 | `submit.py` passes the orchestrator checker (if added to scan set) | unit | `python tools/check_devtest_orchestrator.py` | ✅ (extend) |
| SUB-01/02 | `--submit` flag wired end-to-end via CliRunner | integration | `pytest tests/test_dev_test_cmd.py -k submit -x` | ✅ (extend) |

### Sampling Rate
- **Per task commit:** `pytest tests/test_submit.py -x` + `ruff check firestarter/ tests/`
- **Per wave merge:** full suite + `ruff format --check` + `python tools/check_devtest_orchestrator.py`
- **Phase gate:** full suite green + orchestrator gate green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_submit.py` — new file covering SUB-01/02/03 (tier selection, sanitize, oversize,
  TTY gate, refusal, title)
- [ ] Extend `tests/test_dev_test_cmd.py` — `--submit` flag end-to-end (mock seams)
- [ ] Extend `tests/test_diagnostic_report.py` — dedup fingerprint determinism + volatile-field
  exclusion
- [ ] Extend `tests/test_check_devtest_orchestrator.py` — prove the new `submit.py` scan leg flips
  red on a planted violation (if `submit.py` is added to the scan set)
- [ ] No framework install needed — `pytest`/`CliRunner`/`mock` already in `.[test]`

## Security Domain

Host-only CLI; `security_enforcement` treated as enabled (absent = enabled).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No credentials handled; `gh` owns its own auth token |
| V3 Session Management | no | Stateless CLI |
| V4 Access Control | no | Local tool; GitHub enforces repo perms server-side |
| V5 Input Validation / Output Encoding | **yes** | `urllib.parse.quote` for URL encoding; `subprocess` **argv list** (never `shell=True`) prevents command injection from a chip name / reason text |
| V6 Cryptography | no | `hashlib.sha256` here is a non-secret dedup id, not a security control — do not treat it as one |
| V7 Data Protection / Privacy | **yes** | The SUB-02 PII/path scrub IS the privacy control; whitelist + regex backstop (see §Sanitization) |

### Known Threat Patterns for a shell-out + URL-builder CLI

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Command injection via chip name / reason in the `gh` call | Tampering / EoP | Pass argv as a **list** to `subprocess.run` (no `shell=True`); the chip name and body never reach a shell [VERIFIED: matches avr_tool.py subprocess pattern] |
| PII/path leak into a public GitHub issue | Information Disclosure | Whitelisted `to_dict()` + regex scrub of free-text reasons; fails open, so tests must assert each vector (A3) |
| URL-injection / param smuggling via unescaped body | Tampering | `urllib.parse.quote`/`urlencode` percent-encodes all body/title content |
| Sending a report the tester didn't intend | Repudiation | D-04 explicit `Confirm.ask` preview + off-TTY no-send; no silent submission |
| Report routed to attacker's fork | Tampering | D-01 hardcoded `henols/firestarter_app`; no cwd/remote inference |

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md` and `firestarter_app/CLAUDE.md`:
- **Host-only phase** — the "constants duplicated Python↔C++" and "serial protocol sync" rules do
  **not** apply (no firmware/wire change). Note the parity rules exist but are out of scope here.
- **Tooling gate (v1.8):** `ruff check` + `ruff format --check` + `mypy` (strict on 8 modules) +
  `pytest --cov-fail-under=70`, all enforced by `.github/workflows/ci.yml`. New `submit.py` must be
  ruff-clean and format-stable. Consider adding `submit.py` to the mypy-strict watermark set
  (`tools/check_mypy_watermark.py`) — it is a fresh, easily-typed module. [Planner: confirm the
  watermark tool's module list.]
- **Dev install:** `pip install -e .[test]`; verify `firestarter --help`.
- **CI Python target is 3.11** — the devcontainer runs 3.12, which **masks** py3.11 ruff/codegen
  differences (see MEMORY `reference_devcontainer_py312_masks_ci_py39`). Validate `ruff check
  firestarter/ tests/` and `ruff format --check firestarter/ tests/` against the 3.11 target
  before claiming CI green. No new third-party dependency (Out-of-Scope row).

## Sources

### Primary (HIGH confidence)
- Codebase: `firestarter_app/firestarter/diagnostic_report.py` (to_dict:352, render:371,
  to_json_block:441, is_submittable:153, AutoCapture:68, _step_dict:323, build_db_diff:196)
- Codebase: `firestarter_app/firestarter/chip_test.py` (StepResult:464, verdict vocab:445-449,
  Fingerprint:127, classification labels:114-117, derive_plan:318, run_plan:512)
- Codebase: `firestarter_app/firestarter/cli_handlers.py` (dev_test:1753, helpers 1665-1750,
  _is_interactive:1719, _sanitize_chip_token:1670, persist:1877-1900, imports:18-58)
- Codebase: `firestarter_app/firestarter/avr_tool.py:14-15` (shutil.which + subprocess precedent)
- Codebase: `firestarter_app/firestarter/firmware.py:20` (`from rich.prompt import Confirm`)
- Codebase: `firestarter_app/tools/check_devtest_orchestrator.py` (SAFE-03 checker, full)
- Codebase: `firestarter_app/tests/test_dev_test_cmd.py` (test seam pattern)
- Codebase: `firestarter_app/.github/workflows/ci.yml` (py3.11, ruff/mypy/pytest gate)
- cli.github.com/manual/gh_issue_create (`--body-file -`, `--label`, `--title`, `--repo`, stdout URL)
- cli.github.com/manual/gh_auth_status (exit code + stderr)
- docs.github.com — "Using query parameters to create an issue" (params, label permission → 404)

### Secondary (MEDIUM confidence)
- github/docs issue #5136 — ~8191-byte serverside URL cap (community-documented, not official)
- cli/cli PR #9240 / #8845 / #7447 — gh auth status exit-code + stderr behavior + stale-version bug
- cli/cli #3284, community #35377 — `gh --label` requires the label to pre-exist
- community discussion #22510 — browser template/labels not applying for non-write users

### Tertiary (LOW confidence)
- docs.python.org/3/library/webbrowser, /getpass — stdlib semantics (standard, treated as known)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all stdlib + existing deps, every primitive has a codebase precedent
- Architecture / wiring: HIGH — grounded in real file:line of the exact handler and report model
- gh CLI facts: HIGH (behavior) / MEDIUM (stale-version exit-code edge, A2)
- Browser URL cap: MEDIUM — the 8191-byte figure is community-documented (A1)
- Label behavior (Pitfall 1/2): HIGH — GitHub docs + multiple corroborating issues
- Sanitization regex completeness: MEDIUM — sound but fails open; must be test-asserted (A3)

**Research date:** 2026-07-03
**Valid until:** 2026-08-02 (stable domain; re-check the gh manual + the 8 KB URL cap if GitHub
changes the issues/new form or gh's create output format)
