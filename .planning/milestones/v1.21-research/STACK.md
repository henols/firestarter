# Stack Research

**Domain:** CLI diagnostic-report + GitHub-submission feature for an existing Click-based Python programmer app (`firestarter dev test <chip>`, Firestarter v1.21)
**Researched:** 2026-07-02
**Confidence:** HIGH

## Verdict (one line)

**Add zero new third-party dependencies.** Every capability `dev test` needs is already satisfied by the current dependency set (`click`, `rich`, `requests`) or the Python standard library (`json`, `subprocess`, `shutil.which`, `webbrowser`, `urllib.parse`). Reuse-first is not just honored — it is fully achievable with no `pyproject.toml` change.

## Recommended Stack

### Core Technologies (all already present — reuse)

| Technology | Version (pinned in `firestarter_app/pyproject.toml`) | Purpose for `dev test` | Why Recommended |
|------------|------|---------|-----------------|
| `click` | `>=8.1` (project on 8.x) | Register `dev test <chip>` as a subcommand under the existing `@cli.group(name="dev")` in `cli_handlers.py:941`; provide `--destructive`, `--submit`, `--json`/`--output` flags | Already the CLI framework for all 14 commands + the `dev` group (which already hosts `read`, `reg`, `addr`, `consistency-check`, `write-cycle`, `fault-inject`, `validate-family`). New command is a drop-in sibling of `validate-family`. |
| `rich` | `>=14.0` | Human-readable results table (`rich.table.Table`) + interactive provenance prompts (`rich.prompt.Prompt`/`Confirm`) | Already imported for prompts (`firmware.py:20` uses `rich.prompt.Confirm`) and for the `EpromConsolePresenter` display layer. The "prompt tester for shield rev / provenance / pot" step is exactly `rich.prompt`. No new dep. |
| Python stdlib `json` | 3.9+ (CI floor `requires-python = ">=3.9"`) | Build the machine-readable report dict and serialize the fenced ```` ```json ```` block; `json.dumps(report, indent=2)` | The report is emitted, not consumed/validated by this tool. A self-produced object serialized once needs no schema/validation library. |
| Python stdlib `subprocess` + `shutil.which` | 3.9+ | Tier-1 submission: detect `gh` (`shutil.which("gh")`) and shell out to `gh issue create` | Already the established pattern in-repo — `avr_tool.py` is a `subprocess` wrapper around `avrdude`. Same idiom. |
| Python stdlib `webbrowser` | 3.9+ | Tier-2 submission: open a prefilled `issues/new?...` URL cross-platform (`webbrowser.open(url)`) | Cross-platform out of the box (macOS `open`, Windows `os.startfile`/`start`, Linux `xdg-open`/`$BROWSER`). Zero dep, degrades gracefully (returns `False` if no browser) — print the URL as fallback. |
| Python stdlib `urllib.parse` | 3.9+ | Percent-encode the prefilled-URL `title=` and `body=` query params (`urllib.parse.urlencode` / `quote`) | Correct RFC-3986 encoding of a markdown+JSON body into a query string; hand-rolling encoding is the classic bug source. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `requests` | `>=2.20` (already a dep) | **Only** if a future gist-upload tier is built without `gh` | The gist/attachment tier (verbose failure log > URL limit) is *reserved, not in v1.21 scope* per the seed. If it is ever built and `gh gist create` is not usable, `requests.post` to the GitHub gists API is the fallback — but `gh gist create --filename` is strongly preferred (auth already solved). Do **not** add `PyGithub` for this. |

### Development Tools (no change)

| Tool | Purpose | Notes |
|------|---------|-------|
| `ruff` / `ruff format` | Lint + format gate | New `cli_handlers.py` code must pass the existing `select = ["E","F","I","UP"]` gate. Watch the **py3.12-masks-CI-py3.11** trap: validate `ruff check` + `ruff format --check` against py39/3.11 target before claiming green. |
| `mypy` (strict on 8 modules) | Type gate | `cli_handlers.py` is on the **strict list** (`disallow_untyped_defs = true`). All new handler functions and helpers in that module need full type annotations or the gate fails. |
| `pytest` + `pytest-cov` (`--cov-fail-under=70`) | Test + coverage floor | New report-builder / URL-builder / gh-detection logic must be unit-testable **without** serial hardware or network — factor them as pure functions (mirrors `frame_parser.py`, `codec.py`, `address_parser.py` pattern) so they contribute coverage. |

## Installation

```bash
# NO new packages. The feature is built entirely from existing deps + stdlib.
# Existing (already installed via `pip install -e .`):
#   click>=8.1, rich>=14.0, requests>=2.20, pyserial>=3.5, tqdm>=4.60, packaging>=21.0
# Stdlib (no install): json, subprocess, shutil, webbrowser, urllib.parse

# gh CLI is an OPTIONAL RUNTIME tool, not a Python dependency — never add it to
# pyproject.toml. Detect at runtime; degrade to the browser-URL tier if absent.
```

## GitHub Submission: `gh` shell-out vs prefilled URL (the core decision)

**Recommendation: tiered, `gh`-first, exactly as the seed specifies. Both tiers are stdlib/existing-dep.**

### Tier 1 — `gh issue create` (preferred when `gh` present + authed)

- Detect: `shutil.which("gh")` is present **and** `gh auth status` exits 0.
- Invoke: `subprocess.run(["gh", "issue", "create", "--title", t, "--label", "gsd-inbox,chip-validation", "--body-file", "-"], input=body, text=True, ...)`.
- **Critical: use `--body-file -` (stdin), NOT `--body`.** Passing the body as an argv string risks OS `ARG_MAX` / shell-quoting issues; stdin has **no length limit** and no shell-escaping hazard. `gh` 2.95.0 (verified installed in this env) supports `-F, --body-file file` with `-` = stdin. This makes the `gh` tier immune to the URL-length problem entirely.
- Bonus: `--label` lands the issue directly in `gsd-inbox` triage (seed requirement); `gh issue create` returns the created issue URL on stdout to echo back to the tester.

### Tier 2 — prefilled browser URL (fallback when `gh` absent/unauthed)

- Build `https://github.com/<owner>/<repo>/issues/new?title=<t>&body=<b>` with `urllib.parse.urlencode`.
- Open with `webbrowser.open(url)`; if it returns `False`, print the URL for manual copy.

### The URL length limit — quantified, with its consequence for the JSON payload

| Limit | Value | Source | Consequence |
|-------|-------|--------|-------------|
| **GitHub server-side URL cap** | **~8191 bytes** (8 KB) for the whole request line | GitHub serverside limit (community discussion #22946, github/docs #5136) | A prefilled URL whose total length exceeds ~8191 bytes returns **HTTP 414 Request-URI Too Large** — the issue page never loads. |
| **GitHub issue/PR body cap** | **65536 characters** | GitHub (renovatebot #14551, community #41331) | This is the *content* ceiling, only reachable via `gh --body-file` or the web editor — **not** via the prefilled URL, which hits 8 KB first. |

**Impact on the embedded JSON payload:** the ~8 KB URL budget is *shared* by the scheme+host+path (~60 bytes), the `title=` param, and the percent-encoded `body=`. **Percent-encoding roughly triples the size of the JSON-heavy body** (every `{`, `}`, `"`, newline, space becomes `%xx` — a `"` → `%22` is 3 bytes for 1). So the *effective* raw-markdown-plus-JSON budget for the Tier-2 URL is only **~2.5–3 KB of source text**, not 8 KB.

**Design consequence (confirms the seed's tiering):**
- A **single-chip** `dev test` report (results table + compact JSON of the two-tier diagnostic contract) is a few KB of source → **fits the URL** in the normal case, as the design note asserts. Keep the auto-captured JSON compact (no pretty-print / no raw byte dumps in the URL-bound body).
- The **verbose failure log** (byte-level mismatch dumps, raw serial traces) will blow past ~2.5 KB source → it **must not** go in a prefilled URL. This is precisely why the seed reserves the **gist/attachment tier** for that case, and why the `gh --body-file -` path (no limit) is the preferred Tier 1.
- Practical guard: **measure the encoded URL length; if it exceeds ~8000 bytes, do not open the browser** — instead tell the tester to install `gh` or paste the report manually (or route to the reserved gist tier). Silent truncation would corrupt the JSON block.

## Report Capture: `json` stdlib vs a schema/validation library

**Recommendation: stdlib `json` only. No schema/validation library (no `jsonschema`, no `pydantic`).**

- This command **produces** the report; it does not ingest untrusted JSON that needs validating. A tool validating its own output against a schema at emit time buys nothing at runtime.
- The two-tier diagnostic contract (auto-captured fields + prompted fields) is a fixed, small dict assembled in code. `json.dumps(report, indent=2)` for the human-visible fenced block; a compact `json.dumps(report, separators=(",",":"))` variant if it must ride in the Tier-2 URL.
- The dual output is **one dict, two renderings**: `rich.table.Table` for the human summary, `json.dumps` for the fenced block — built from the same source object so they can never disagree.
- **Version/schema hygiene without a library:** put a `"schema_version": 1` (or `"report_version"`) key in the JSON so the maintainer's `gsd-inbox` triage can evolve the contract later. This is a convention, not a dependency.
- **If** the *maintainer-side* triage tooling later wants to validate incoming community reports, that validation belongs in a separate tool/CI step, and even there `json.load` + explicit key checks suffice for a contract this small. Defer `jsonschema` until there is a real ingest-and-validate consumer — not in v1.21.

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| `gh issue create` (subprocess) | `PyGithub` | Never for this project. `PyGithub` adds a dependency, needs token management the project doesn't currently do, and duplicates what `gh` (already the maintainer's tool, already handles auth) does. Only reconsider if the app ever needed *unattended* API calls with no `gh` present — not the case here. |
| `gh issue create` (subprocess) | `requests.post` to the issues REST API | Only if `gh` is guaranteed absent *and* a token is available — but community testers won't have a maintainer token. The browser-URL tier is the correct auth-free fallback, not raw REST. |
| stdlib `json` | `pydantic` / `jsonschema` / `marshmallow` | Only if a maintainer-side ingest pipeline needs to *validate untrusted* community-submitted reports. Not in `dev test` (the producer). |
| stdlib `webbrowser` | `click.launch(url)` | `click.launch` is a thin, acceptable wrapper over the same OS handlers and is already a dependency — either is fine. Prefer `click.launch` only if you also want to open file paths; for a plain URL, stdlib `webbrowser.open` is the most explicit and equally cross-platform. |
| stdlib `urllib.parse.urlencode` | `new-github-issue-url` (JS) / hand-built strings | The JS lib is Node-only (irrelevant). Hand-building query strings mis-encodes markdown/JSON — always use `urlencode`. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `PyGithub` | New third-party dep; token/auth burden; duplicates `gh` which is already authed on maintainer machines and is the seed's chosen Tier-1 | `gh issue create` via `subprocess` + `shutil.which` detection |
| `jsonschema` / `pydantic` | New dep to validate JSON this command *authors* — no untrusted input at emit time | stdlib `json` + a `schema_version` key |
| `--body` argv string for `gh` | Risks `ARG_MAX` / shell-quoting corruption on large bodies; caps out where argv does | `gh ... --body-file -` reading the body from **stdin** (no length limit) |
| Prefilled URL for the *verbose failure log* | ~8 KB URL cap; percent-encoding ~3× inflation → ~2.5 KB source budget; overflow → HTTP 414, page fails to load | `gh --body-file -` (Tier 1), or the reserved gist tier for the rare oversized log |
| Embedding raw byte dumps / serial traces in the JSON block that rides the Tier-2 URL | Guarantees the ~8 KB URL overflow | Keep URL-bound JSON compact; route verbose payloads to `gh`/gist |
| Adding `gh` to `pyproject.toml` | `gh` is an external CLI binary, not a pip package; it is an *optional runtime* tool | Runtime `shutil.which("gh")` detection with graceful degradation |

## Stack Patterns by Variant

**If `gh` present AND `gh auth status` == 0 (and `--submit`):**
- Tier 1: `subprocess.run(["gh","issue","create","--title",t,"--label","gsd-inbox,...","--body-file","-"], input=body, text=True)`.
- No URL-length concern; body may use the full 65536-char GitHub body ceiling.

**If `gh` absent/unauthed AND report source ≲ ~2.5 KB (and `--submit`):**
- Tier 2: build URL via `urllib.parse.urlencode`, `webbrowser.open(url)`; print URL if `open` returns `False`.
- Guard: assert encoded URL length < ~8000 bytes before opening.

**If report source > URL budget AND no `gh`:**
- Do NOT open a truncated URL. Print the full report to a local file + instruct the tester to install `gh` or paste manually. (Reserved gist tier is the future home for this.)

**If run non-destructively (default):**
- Report must record "only N of M tests ran" as a first-class JSON field + a loud human-visible line (seed requirement) — a data/UX concern, no stack impact.

## Version Compatibility

| Component | Compatible With | Notes |
|-----------|-----------------|-------|
| `click>=8.1` | Existing `dev` group | New subcommand is a plain `@dev.command(name="test")`; no version bump needed. |
| `rich>=14.0` | `rich.table.Table`, `rich.prompt.Prompt`/`Confirm` | All present in 14.x; `Confirm` already used in-repo. |
| stdlib modules | Python 3.9–3.12 | `json`, `subprocess`, `shutil.which`, `webbrowser`, `urllib.parse` are stable and unchanged across the project's 3.9→3.12 support window. Nothing 3.10+-only. |
| `gh` CLI | 2.x (2.95.0 verified in this env) | `--body-file -`, `--label`, `--web` all present since well before 2.95. Runtime-detected, not pinned. |

## Integration Points in the Existing CLI (for the roadmap)

- **New command:** add `@dev.command(name="test")` in `firestarter/cli_handlers.py` (the `dev` group is defined at line 943; `validate-family` at line 1452 is the closest structural sibling to copy — same `@click.pass_obj` + `@map_typed_errors` + `AppContext` pattern, same `--output-dir` artifact-emit idiom).
- **Chip resolution:** reuse `resolve_chip(name, db=app.db)` (`chip_resolver.py`) exactly as `dev_read`/`validate-family` do — the test plan derives from the resolved entry + `classify()`.
- **Operations:** compose existing `eprom_operator` methods (read/write/verify/blank-check) as independent non-fatal steps; do NOT re-implement — mirror how `validate-family` "composes `write_cycle_eprom` / `consistency_check_eprom` (no re-implementation)".
- **VPP/VPE capture:** reuse the existing voltage monitor (the `vpp`/`vpe` monitor path) mid-sweep for the "measured rail" field.
- **Testability:** factor the report-builder, URL-builder, and `gh`-detection into pure helper functions (like `codec.py`/`frame_parser.py`) so they land under the 70% coverage floor without hardware.

## Sources

- GitHub prefilled-issue URL length limit (~8191 bytes → HTTP 414): [community Discussion #22946 — Passing long body to issues/new](https://github.com/orgs/community/discussions/22946), [github/docs #5136 — Document GitHub serverside limit on URL length](https://github.com/github/docs/issues/5136) — HIGH confidence (multiple corroborating community + docs-tracker sources).
- GitHub issue/PR body cap (65536 characters): [renovatebot/renovate #14551](https://github.com/renovatebot/renovate/issues/14551), [community Discussion #41331 — Comment is too long](https://github.com/orgs/community/discussions/41331) — HIGH confidence.
- Prefilled-URL builder reference (encoding approach, Node-only lib): [sindresorhus/new-github-issue-url](https://github.com/sindresorhus/new-github-issue-url) — MEDIUM confidence (illustrative, not adopted).
- `gh issue create` `--body-file -` / `--label` / `--web` flags: verified locally against `gh version 2.95.0 (2026-06-17)` in this environment — HIGH confidence.
- Python stdlib availability (`json`, `subprocess`, `shutil`, `webbrowser`, `urllib.parse`) on the project interpreter: verified locally via import — HIGH confidence.
- Existing project dependencies (`click>=8.1`, `rich>=14.0`, `requests>=2.20`) + `dev` Click group + `rich.prompt` usage: read directly from `firestarter_app/pyproject.toml` and `firestarter_app/firestarter/cli_handlers.py:941`/`firmware.py:20` — HIGH confidence.

---
*Stack research for: `firestarter dev test <chip>` community chip-validation command (v1.21)*
*Researched: 2026-07-02*
