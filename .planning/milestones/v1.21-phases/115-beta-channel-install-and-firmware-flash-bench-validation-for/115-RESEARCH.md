# Phase 115: Beta Install & Firmware-Flash Bench Validation — Community Onboarding (close) - Research

**Researched:** 2026-07-10
**Domain:** Release engineering (dual-repo GitHub Actions + PyPI + GitHub prerelease `.hex` assets) + hardware-gated install/flash/smoke validation + community onboarding doc
**Confidence:** HIGH on all CI/source mechanics (read directly from workflow + source files); MEDIUM on the D-01↔D-02 "how code reaches a buildable state without the deferred beta merge" reconciliation (needs an operator decision — see BLOCKERS)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01 (LOCKED):** This phase DRIVES the `3.0.0b11` release cut (not verify-only). It authors + runs the full release-engineering: land v1.20 + v1.21 onto `beta` (lockstep, all 3 repos), bump `firestarter_app/firestarter/__init__.py` `3.0.0b10 → 3.0.0b11`, gitlink bump from PINNED b10, changelog/prerelease notes, trigger the PyPI publish (`beta-release.yml` via manual `gh` dispatch), ensure the GitHub prerelease carries a `firestarter_<board>.hex` asset per board (built by firmware `beta-build.yml`).
- **D-02 (LOCKED):** Release cut scoped to the BETA PUBLISH only. In scope: everything to make both channels (PyPI `--pre` + GitHub prerelease with `.hex`) publicly reachable. **Out of scope (deferred to a separate operator-gated close step):** the `v1.21` git tag, any final `--no-ff` merge to `beta`, and the `/gsd-ship` / `/gsd-complete-milestone` ceremony.
- **D-03 (LOCKED):** Irreversible/outward-facing publish steps get an explicit operator-authorization checkpoint at execution time. The PyPI `gh` dispatch and the GitHub-prerelease publish pause for explicit operator go-ahead — never fired autonomously.
- **D-04 (LOCKED):** Doc is draft-first (write ONBOARD-04 doc from known facts BEFORE the cut so b11 ships with it), then finalized from bench findings as a repo update on `beta`/v1.21.
- **D-05 (LOCKED):** Uno + Leonardo are HARD pass/fail gates; uno328pb is best-effort (flaky/failed run recorded + FUT item, does NOT block close). `.hex` choice: flash `firestarter_uno328pb.hex`; if the third board proves to be a plain Uno, note it explicitly and use `firestarter_uno.hex` — never silently substitute.
- **D-06 (LOCKED):** Close ceremony is a SEPARATE operator-gated step after verification. Order: (1) draft doc → (2) release cut + publish b11 → (3) per-board bench validation → (4) finalize doc → (5) phase verification → (6) THEN operator-gated `v1.21` tag + final merge + ship (NOT this phase's plan).
- **D-07 (LOCKED):** Fresh-venv + `FIRESTARTER_CONFIG_DIR` isolation. Each per-board run uses a throwaway virtualenv (`pip install --pre firestarter`, NOT the operator's `-e` install) and points `FIRESTARTER_CONFIG_DIR` at a clean temp dir.
- **D-08 (LOCKED):** One evidence record per board (e.g. `chip-test/onboard-<board>.md`, mirroring `chip-test/dev-test-w27c512.md`): the `firestarter --version` string (must be `3.0.0b11`), the `fw -i` resolved channel + downloaded asset name, avrdude flash+verify output, smoke-op result. Blank/failed fields recorded honestly.
- **D-09 (LOCKED):** New standalone doc in `firestarter_app/doc/` (suggested `beta-testing-install.md`). Contents: per-board commands, avrdude prerequisite, the `/dev/ttyACM*` controller-identity gotcha, correct `.hex` per board, hand-off into `dev test <chip>` (link `community-validation.md`). README gets a pointer link only, NOT a duplicate.

### Claude's Discretion
- Exact venv/`FIRESTARTER_CONFIG_DIR` scaffolding mechanics (temp-dir layout, teardown) — within D-07.
- Evidence-record filename/template details — within D-08.
- Doc filename + section ordering — within D-09.
- Smoke-test op: default is `firestarter fw` (version+board) then `firestarter hw` (hardware revision read/identify) as the one minimal live op. Planner may pick `id`/identify if research shows a more universal minimal op.
- **Whether the firmware repo needs its own version tag alongside the app b11 cut, and how `beta-build.yml` `.hex` assets attach to the GitHub prerelease — flagged as the `--research-phase 115` item.** → **ANSWERED below (Q1).**

### Deferred Ideas (OUT OF SCOPE)
- Milestone close ceremony (`v1.21` tag, final `--no-ff` merge to beta, `/gsd-ship`, `/gsd-complete-milestone`).
- uno328pb as a hard gate (deferred; FUT item if a future session stabilizes/identifies the third board).
- avrdude MCU-detection fallback (`avrdude-mcu-detection-fallback.md`) — feature-add to the avrdude recovery path; this phase validates the EXISTING path only.
- All Reviewed Todos (firmware/DB-decode/hardware/bench axis) — none folded; scope guardrail overrides auto-fold.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ONBOARD-01 | Fresh venv `pip install --pre firestarter` installs `3.0.0b11`; `firestarter --version` reports it — per board. Step 0 confirms PyPI publish or halts. | Q1 (PyPI publish runbook), Q4 (fresh-venv recipe), Q5 (version-report command) |
| ONBOARD-02 | Bare `fw -i` auto-routes to `--pre`, downloads board-matching `firestarter_<board>.hex` from the GitHub prerelease, avrdude flashes+verifies — per board. Step 0 confirms the prerelease exposes a `.hex` per board. | Q1 (firmware `.hex` prerelease runbook), Q2 (`fetch_release_info` acceptance shape), Q3 (board→`.hex` + detection), Q6 (avrdude) |
| ONBOARD-03 | Post-flash smoke test: `firestarter fw` reports expected beta version+board + one minimal live op (`hw`/identify). NOT a chip write/verify. | Q5 (smoke commands, `hw` op) |
| ONBOARD-04 | Community doc in `firestarter_app` sub-repo, stranger-oriented: per-board commands, avrdude prereq, `/dev/ttyACM*` gotcha, correct `.hex`, hand-off into `dev test`. | Q6 (avrdude prereq), Q3 (board→`.hex`), D-09 (doc home) |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- **Dual-repo + lockstep discipline:** meta tracks only `.planning/`+`.claude/`; code in `firestarter/` (firmware) and `firestarter_app/` (host CLI). Constants/flags duplicated between `constants.py` ↔ `firestarter.h`/`rurp_pinout.h` — change together. `messages.py`/`messages.h` are codegen-generated from `messages.toml`; CI drift-gate enforced.
- **App tooling gate (CI `ci.yml`):** `ruff check` + `ruff format --check` + `mypy` (8 strict modules) + `pytest --cov-fail-under=70` on every PR. `pre-commit` mirrors hook order.
- **This phase changes ZERO firmware behavior, ZERO dispatch, ZERO `chip_database.json`.** It is orchestration/validation/docs only. The doc lands in `firestarter_app/doc/` (operator-canonical, two-layer doc pattern).

## Summary

This is the v1.21 close capstone: a VALIDATION + DOCS phase. The install/flash/channel-select feature already exists and is not rebuilt (`firmware.py` channel select + GitHub-prerelease pagination; `cli_handlers.py` `fw` 3-way mutex + bare-`fw -i` auto-route; `avr_tool.py` avrdude wrapper). The phase does three things: (1) drives the `3.0.0b11` beta publish so the community path is publicly reachable on BOTH channels, (2) runs the full install→flash→smoke chain per bench board on real hardware, and (3) ships a stranger-oriented onboarding doc.

The single most important mechanical finding is an **asymmetry in where the two channels live**: the Python package publishes to **PyPI** (from the `firestarter_app` repo), while the board `.hex` assets that `fw -i` downloads come from a **GitHub prerelease on the `henols/firestarter` firmware repo** — the app's release-fetch URLs are hardcoded to `https://api.github.com/repos/henols/firestarter/releases`. The app and firmware version lines are **independent** (both happen to sit at `3.0.0b10` now, both auto-increment to `b11`, but nothing couples them — the "skipped-version fw tag" history confirms they can diverge). So Step 0 must verify TWO separately-published artifacts on TWO different repos.

The second load-bearing finding is a **version-mode trap in `update_version.py`**: the CI version bump only takes the beta path when `GITHUB_REF == refs/heads/beta` OR the `beta_version`/`BETA_VERSION` input is set. If the operator triggers the cut from any non-`beta` branch (e.g. the current `v1.21` branch) via `workflow_dispatch` **without** supplying the explicit `beta_version=3.0.0b11` input, the script silently takes the STABLE path and produces `3.0.1` instead of `3.0.0b11`. Every dispatch in the runbook must pass the explicit version input.

**Primary recommendation:** Do NOT push to `beta` to trigger the cut (a push auto-fires both workflows, performs the D-02/D-06-deferred beta merge, and removes the D-03 human gate). Instead resolve the D-01↔D-02 tension with the operator (see BLOCKERS), most likely by `workflow_dispatch`-ing both `beta-release.yml` (app) and `beta-build.yml` (firmware) against the `v1.21` branch ref with an explicit `beta_version=3.0.0b11`, then a manual `gh workflow run publish.yml -f tag=3.0.0b11` for PyPI — each dispatch behind an explicit operator checkpoint (D-03). avrdude 7.1 and three USB serial devices are present in the devcontainer, so per-board flashing is drivable here.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| PyPI package publish (`3.0.0b11`) | `firestarter_app` GitHub Actions (`publish.yml`) | operator (`gh` dispatch) | Package lives on PyPI; publish is a manual `gh workflow run` because the PAT-created release suppresses `release.published`. |
| Firmware `.hex` per-board build + prerelease | `firestarter` GitHub Actions (`beta-build.yml`) | operator (push/dispatch) | `pio run` builds uno/uno328pb/leonardo; `action-gh-release` attaches `firestarter_*.hex` to a prerelease on `henols/firestarter`. |
| Channel select + `.hex` asset resolution | Host CLI (`firmware.py` `fetch_release_info`) | GitHub Releases API | App resolves highest prerelease + board asset; reads from firmware repo. |
| Bare `fw -i` → `--pre` auto-route | Host CLI (`cli_handlers.py` `_maybe_auto_route_to_pre`) | — | Installed-app prerelease version flips the channel to `pre`. |
| Board detection (which `.hex`) | Host CLI (`check_current_firmware` identity parse) | operator (`-b/--board` override) | Board read from the currently-flashed FW identity string; overridable. |
| avrdude flash + verify | Host (`avr_tool.py` → `/usr/bin/avrdude`) | devcontainer USB passthrough | Per-board partno/programmer/baud; `-D -U flash:w:<hex>:i`. |
| Config/DB isolation | `config.py` `FIRESTARTER_CONFIG_DIR` seam | fresh venv | Isolates `~/.firestarter` config + DB override so the fresh-machine claim holds. |
| Onboarding doc | `firestarter_app/doc/` (operator-canonical) | README pointer | Two-layer doc pattern; hand-off into `community-validation.md`. |

---

## Q1 — Dual-repo release-engineering mechanics (the flagged item)

### Current state (verified 2026-07-10)
- Both submodules are on branch `v1.21-community-chip-validation-command`.
- App `firestarter_app/firestarter/__init__.py:1` = `__version__ = "3.0.0b10"`. Firmware `firestarter/include/version.h` = `#define VERSION "3.0.0b10"`.
- App tags: `3.0.0b6..b10`. Firmware tags: `3.0.0b3..b10`. [VERIFIED: `git tag`]
- Both sub-repo `beta` branches are **strictly behind** the v1.21 branch and contain nothing HEAD lacks: `git rev-list --left-right --count origin/beta...HEAD` → app `0  129`, firmware `0  23`. So the v1.21 branch carries all of v1.20 + v1.21; a merge to beta would be a clean fast-forward. [VERIFIED: git]
- avrdude `7.1` present at `/usr/bin/avrdude`; USB `/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0` attached. [VERIFIED: shell]

### The two channels live in DIFFERENT repos
`firmware.py` fetches `.hex` from hardcoded constants pointing at the **firmware** repo [VERIFIED: `constants.py:8-15`]:
```
FIRESTARTER_RELEASE_URL        = https://api.github.com/repos/henols/firestarter/releases/latest
FIRESTARTER_RELEASES_URL       = https://api.github.com/repos/henols/firestarter/releases
FIRESTARTER_RELEASE_BY_TAG_URL = https://api.github.com/repos/henols/firestarter/releases/tags/{tag}
```
So: PyPI publish comes from the **app** repo; the `.hex` prerelease `fw -i` reads comes from the **firmware** repo (`henols/firestarter`). They are independent version lines. **The firmware repo DOES need its own prerelease** carrying the `.hex` assets (answering the D-09 flag: yes, a firmware prerelease is required alongside the app b11 cut; its tag need not equal the app's, though both auto-compute to `b11` here).

### App PyPI path — two workflows, PyPI needs a manual dispatch
`firestarter_app/.github/workflows/beta-release.yml` [VERIFIED]:
- Trigger: `push` to `beta` (with `paths-ignore` for `**.md`,`**.sh`,`tools/**`,`.github/**`, …) OR `workflow_dispatch` with an optional `beta_version` input.
- Steps: setup py3.11 → `pip install -e .[test]` → catalog validity check → **codegen drift gate** (`codegen.py --target firestarter/messages.py` → `ruff format` → `ruff check --add-noqa` → `git diff --exit-code firestarter/messages.py`) → `pytest tests/ -v` → `update_version.py` (bump) → `git-auto-commit-action` → `action-gh-release` (`prerelease: true`, `make_latest: false`, token = `PERSONAL_ACCESS_TOKEN`).
- **This workflow does NOT publish to PyPI** — it only bumps the version and creates a GitHub Release on the app repo.

`firestarter_app/.github/workflows/publish.yml` [VERIFIED]:
- Trigger: `release: published` OR `workflow_dispatch` with a **required** `tag` input.
- Steps: checkout the tag → `python -m build` → `pypa/gh-action-pypi-publish` (token = `PYPI_API_TOKEN`).
- **Header comment documents the gotcha:** a release created by another workflow using a PAT that lacks `workflow` scope suppresses the `release.published` event, so `publish.yml` does NOT auto-fire. **PyPI publish must be a manual `gh workflow run publish.yml -f tag=3.0.0b11`.** [VERIFIED: `publish.yml:5-16`] — this confirms the `reference_betarelease_ci_gotchas_v18` "PyPI needs a manual gh dispatch" note is still current.

### Firmware `.hex` path — one workflow, attaches assets automatically
`firestarter/.github/workflows/beta-build.yml` [VERIFIED]:
- Trigger: `push` to `beta` OR `workflow_dispatch` with optional `beta_version`.
- Steps: py3.11 → catalog check → **messages.h codegen drift gate** (`codegen.py --target include/messages.h --language cpp` → `git diff --exit-code`) → `pip install platformio` → `pio test -e native` → `pytest tests/` → `update_version.py` (edits `include/version.h`, tag-scan increment) → `git-auto-commit-action` → **`pio run`** → `action-gh-release` with `files: .pio/build/**/firestarter_*.hex`, `prerelease: true`, `make_latest: false`, token = `GITHUB_TOKEN`.
- `platformio.ini` `default_envs = uno, uno328pb, leonardo` [VERIFIED:31-16], so `pio run` builds all three. `name_firmware.py` sets `PROGNAME = firestarter_<RURP_BOARD_NAME>` [VERIFIED:60-61], producing `firestarter_uno.hex`, `firestarter_uno328pb.hex`, `firestarter_leonardo.hex` → all three attach to the prerelease automatically (no manual asset upload). [VERIFIED]

### The version-mode trap (LOAD-BEARING)
`update_version.py` `is_beta_mode()` returns True only if `--beta` OR `GITHUB_REF == refs/heads/beta` OR `BETA_VERSION` env is set [VERIFIED: app `update_version.py:50-58`; fw script identical shape]. Both workflows wire `env: BETA_VERSION: ${{ github.event.inputs.beta_version }}` on the bump step [VERIFIED: app:65-66, fw:70-71].
- **Push to `beta`** → `GITHUB_REF == refs/heads/beta` → beta mode; git-tag scan `b10 → b11` automatically.
- **`workflow_dispatch` from a non-`beta` branch (e.g. v1.21) WITHOUT the `beta_version` input** → `BETA_VERSION=""` → `is_beta_mode` False → **STABLE path → bumps to `3.0.1`** (wrong). Every dispatch MUST pass `-f beta_version=3.0.0b11`.

### CI traps that gate the cut (still apply — verify before triggering)
From `reference_betarelease_ci_gotchas_v18`, cross-checked against the live workflows:
- **Codegen drift vs ruff baseline** — both workflows fail if regenerated `messages.py`/`messages.h` differs from committed after ruff-normalization. Pre-validate locally. [CONFIRMED still present]
- **`.[dev]` vs `.[test]`** — app workflow installs `-e .[test]` (not `[dev]`); `pyproject.toml` defines both `dev` and `test` optional-dependency groups [VERIFIED:57-61]. Validate against `[test]`.
- **Version/traceback snapshot tests** — `pytest tests/ -v` runs the full suite; syrupy snapshot + version-string tests can trip on the bump. Run the suite on the exact tree that will be cut.
- **py3.12-masks-CI-py3.11** (`reference_devcontainer_py312_masks_ci_py39`) — devcontainer python is 3.12; CI is 3.11. Validate `ruff check` + `ruff format --check` against the 3.11 target; a green local run under 3.12 is not proof.
- **Secrets are operator-side** — `PERSONAL_ACCESS_TOKEN`, `PYPI_API_TOKEN`, `GITHUB_TOKEN` live on the `henols/*` GitHub repos. `gh workflow run` must be authenticated to those repos (operator's `gh` auth). Claude cannot dispatch these without operator credentials → the dispatch steps are inherently operator-gated (aligns with D-03).

### PUBLIC (this phase) vs milestone-close (out of scope)
- **PUBLIC (D-01/D-02, this phase):** app version `b11` published to PyPI; firmware prerelease with the three `.hex` assets live on `henols/firestarter`. Both channels reachable by `pip install --pre firestarter` and `fw -i`.
- **OUT (D-02/D-06, close ceremony):** the `v1.21` git *milestone* tag, the final `--no-ff` merge to `beta`, `/gsd-ship`, `/gsd-complete-milestone`. Note: the release *version tags* `3.0.0b11` created by the workflows are release-engineering artifacts, distinct from the `v1.21` milestone tag.

---

## Q2 — How `firmware.py` resolves the prerelease + board `.hex`

`fetch_release_info(channel='pre', board=<b>)` [VERIFIED: `firmware.py:224-311`]:
1. `_fetch_all_releases()` GETs `FIRESTARTER_RELEASES_URL`, following `Link: rel="next"` pagination, capped at `max_pages=5` (~150 releases) [firmware.py:194-222].
2. Filters each release: **skip unless `prerelease == True` AND `draft` is falsy** [firmware.py:280-282].
3. Parses `tag_name` with `packaging.version.Version`; **skips tags that raise `InvalidVersion`** (logs a warning) [firmware.py:283-287].
4. If no candidates → **falls back to stable** (`fetch_latest_release_info`) — matches `pip --pre` semantics [firmware.py:289-294]. (Relevant to Step 0: if the prerelease is missing/mis-shaped, `fw -i` silently downloads STABLE firmware, not an error — so Step 0 must positively confirm the prerelease exists, not just that `fw -i` "works".)
5. Sorts candidates descending by PEP 440, picks the highest [firmware.py:296-298].
6. Matches `asset.name == f"firestarter_{board}.hex"` exactly; returns `(tag_name, browser_download_url)`; if the asset is absent → logs error, returns `(None, None)` [firmware.py:300-311].

### EXACT prerelease shape required for `fw -i` to find it (Step 0 acceptance bar)
On `henols/firestarter` there must exist a GitHub release with:
- `prerelease: true`, `draft: false`
- `tag_name` PEP 440-parseable (e.g. `3.0.0b11`)
- `assets[]` including `firestarter_uno.hex`, `firestarter_uno328pb.hex`, `firestarter_leonardo.hex` (exact names) with valid `browser_download_url`
- It must be the **highest** PEP 440 prerelease (else a newer prerelease wins).

### Programmatic Step-0 checks (no hardware needed)
- PyPI channel: `pip index versions firestarter --pre` shows `3.0.0b11` (or `python -m pip download --pre --no-deps firestarter==3.0.0b11`).
- `.hex` channel, per board, using the app's own resolver (authoritative — same code path `fw -i` uses):
  `firestarter fw --list --pre -b uno` (and `-b uno328pb`, `-b leonardo`) → each must list the `3.0.0b11` prerelease row with an `asset_url`. `--json` gives a machine-checkable array. [VERIFIED: `list_releases` firmware.py:319-385 + `fw --list` cli_handlers.py:901-922]
- Raw API cross-check: `GET https://api.github.com/repos/henols/firestarter/releases` → confirm the prerelease + 3 assets.

---

## Q3 — Board → `.hex` mapping + the `fw -i` board-detection path

### Board → artifact table

| Bench board | PIO env | `RURP_BOARD_NAME` | Artifact | avrdude partno / programmer / baud | Gate (D-05) |
|-------------|---------|-------------------|----------|-----------------------------------|-------------|
| Arduino Uno | `[env:uno]` | `uno` | `firestarter_uno.hex` | `atmega328p` / `arduino` / `115200` | HARD |
| Arduino Leonardo | `[env:leonardo]` | `leonardo` | `firestarter_leonardo.hex` | `atmega32u4` / `avr109` / `57600` | HARD |
| uno328pb (Uno-shaped, ATmega328PB) | `[env:uno328pb]` | `uno328pb` | `firestarter_uno328pb.hex` | `atmega328pb` / `urclock` / `115200` | best-effort |

[VERIFIED: `platformio.ini:31-67`, `name_firmware.py:60-61`, `firmware.py:431-446`]. uno328pb DOES emit a **distinct** `firestarter_uno328pb.hex` — it does not share the uno build (its own env + `RURP_BOARD_NAME="uno328pb"` literal, ATmega328PB signature `0x1E9516` differs from 328P `0x1E950F`, so a shared uno build would fail avrdude's signature check).

### Board detection (which `.hex` gets pulled)
`manage_firmware_update` [VERIFIED: `firmware.py:539-575`]:
1. Calls `check_current_firmware()` → parses the FW identity line `"<version>:<board>[:buf[:maxchunk]]"`, returns `(port, current_version, current_board)` — reads `board` from the **currently-flashed firmware**. [firmware.py:82-138]
2. `board_to_use = current_board or board_override` (override default = `"uno"`). [firmware.py:571]
3. `fetch_release_info(channel, board=board_to_use)` selects the asset.

**Implication for D-05:** a board already running FW that reports `uno328pb` auto-selects `firestarter_uno328pb.hex`. If the third board reports `uno` (the `project_uno328pb_correction` mis-ID case, or a bricked/blank board where `check_current_firmware` returns `None` → falls back to override `uno`), it selects `firestarter_uno.hex`. To force the intended board, pass `-b/--board` (a `click.Choice(["uno","uno328pb","leonardo"])`, cli_handlers.py:816-822): `firestarter fw -i -b uno328pb`. Per D-05, flash `firestarter_uno328pb.hex` (use `-b uno328pb`) unless the board proves to be a plain Uno — then record it explicitly and use `-b uno`.

### `fw -i` channel routing end-to-end
- `fw()` enforces the 3-way `--pre`/`--firmware-version`/`--stable` mutex (UsageError/exit-2 if >1) [cli_handlers.py:882-895].
- `_maybe_auto_route_to_pre_click` → `_maybe_auto_route_to_pre`: when `install` is set AND none of `--pre`/`--firmware-version`/`--stable` given, it checks the **installed app** version; if `Version(firestarter.__version__).is_prerelease` is True it sets `pre=True` [cli_handlers.py:200-239, 767-787]. So a `3.0.0b11`-installed app makes bare `fw -i` route to `pre` (D-23/D-24). A stable-installed app is unaffected.
- Channel resolution: `firmware_version → "pinned"`, `pre → "pre"`, else `"stable"` [cli_handlers.py:928-934], then `manage_firmware_update(..., channel=channel, board_override=board)` [cli_handlers.py:942-951].

---

## Q4 — Fresh-venv + `FIRESTARTER_CONFIG_DIR` isolation (D-07)

### The seam exists and what it isolates
`config.py` `get_config_dir()` returns `os.environ.get("FIRESTARTER_CONFIG_DIR") or ~/.firestarter` [VERIFIED: config.py:22-32]. It governs `config.json`, `database.json` (local DB override), and `pin-maps.json` [config.py:35-39]. So the seam isolates the operator's persisted config (saved port, avrdude paths) and any local chip-DB/pin-map override — exactly the contamination D-07 targets.

### Two isolation GOTCHAS (flag in the recipe + the doc)
1. **`HOME_PATH` is import-time in `config.py`** (`HOME_PATH = get_config_dir()` at line 35) and `ConfigManager.__new__/__init__` use that module-level constant, not `get_config_dir()` at call time [VERIFIED: config.py:35, 89, 97]. Therefore `FIRESTARTER_CONFIG_DIR` MUST be set in the environment **before** the CLI process starts (i.e. exported before invoking `firestarter`). Setting it mid-process has no effect. For a subprocess run in a fresh venv this is naturally satisfied — but the recipe must `export FIRESTARTER_CONFIG_DIR=...` before every `firestarter` call.
2. **`firmware.py` has its OWN `HOME_PATH = ~/.firestarter`** (line 67) that does **NOT** honor `FIRESTARTER_CONFIG_DIR` — the downloaded `.hex` is written there by `_download_firmware_file` then deleted [VERIFIED: firmware.py:67, 387-418, 648-655]. This is a minor, transient leak (a temp `.hex` touches the real `~/.firestarter`, then is removed) and does not affect config/DB isolation, but note it: a truly pristine run cannot rely on the config-dir seam to keep `~/.firestarter` untouched during a flash. Acceptable for D-07's purpose (the fresh-machine claim is about config/DB/`-e`-install contamination, which the venv + config-dir cover).

### Concrete fresh-venv recipe (per board)
```bash
# One throwaway venv + clean config dir per board run
BOARD=uno   # or leonardo / uno328pb
WORK=$(mktemp -d /tmp/onboard-$BOARD.XXXX)
python3 -m venv "$WORK/venv"
"$WORK/venv/bin/pip" install --upgrade pip
"$WORK/venv/bin/pip" install --pre firestarter        # pulls 3.0.0b11 from PyPI (ONBOARD-01)

export FIRESTARTER_CONFIG_DIR="$WORK/config"           # clean, isolated (export BEFORE any firestarter call)
FS="$WORK/venv/bin/firestarter"

"$FS" --version                                        # MUST print 3.0.0b11 (record in evidence)
# ... fw -i / fw / hw per Q5 ...
# teardown: rm -rf "$WORK"  (venv + config dir; nothing leaks into ~/.firestarter except transient .hex)
```
Notes: use the venv's own `firestarter` shim path (not the operator's `-e` install on PATH). `reference_firestarter_app_python_test_env` — use the `/usr/local` python; ignore any foreign `.venv/` on the bench. The devcontainer python is 3.12, which is fine for *running* the published wheel (the py3.11 concern is a CI-lint concern, not a runtime concern).

---

## Q5 — Smoke-test op (ONBOARD-03)

**Default (per CONTEXT):** `firestarter fw` for version+board, then `firestarter hw` as the one minimal live protocol op. Both need NO chip seated.

### Commands (per board, in the isolated venv from Q4)
```bash
"$FS" fw -i -b "$BOARD"     # ONBOARD-02: auto-route→pre, download firestarter_<board>.hex, avrdude flash+verify
"$FS" fw                    # ONBOARD-03 part 1: reports "Current firmware version: 3.0.0b11, for controller: <board> ..."
"$FS" hw                    # ONBOARD-03 part 2: live protocol op — reads hardware revision / identifies
```
- `firestarter fw` (no `-i`): `manage_firmware_update(install_flag=False)` → `check_current_firmware` opens serial, reads the identity line, logs `Current firmware version: <v>, for controller: <board> on port <p>` [VERIFIED: firmware.py:122-125]. That log line is the version+board evidence. (It also then compares against the release and may print "up to date"/prompt — for the smoke test only the identity read matters; capture stdout/log.)
- `firestarter hw`: `hw()` → `hardware_manager.get_hardware_revision(...)` — a live energize/query op requiring only a powered board, no chip [VERIFIED: cli_handlers.py:707-712]. This is the minimal "stack is alive and speaks the protocol" proof. `id`/identify was considered as an alternative but `hw` is the more universal bare-board op (identify targets a chip). Recommend `hw`.
- **uno328pb caveat (D-05):** expect possible instability on the live op (timeouts, `0xff` drift, VPP misread per `project_uno328pb_bench_instability_27_04`). Record the outcome verbatim; do NOT retry into a false green. Also verify `controller:` identity per run — `/dev/ttyACM*` numbers shuffle across replug (`feedback_verify_port_identity_each_task`).

---

## Q6 — avrdude prerequisite

`avr_tool.Avrdude` [VERIFIED: avr_tool.py]:
- `_find_avrdude_path`: uses `--avrdude-path` override → configured path → `shutil.which("avrdude")` [avr_tool.py:57-68]. So a bare `avrdude` on PATH suffices.
- `_get_avrdude_version`: parses `avrdude version X.Y`. If `< 7.0`, an `avrdude.conf` path is required (`_configure_avrconf`, `-C`); if `>= 7.0`, no config needed (`self.config = None`) [avr_tool.py:50-55, 70-95, 138-139].
- Flash command: `avrdude -v -p <partno> -c <programmer> -b <baud> -P <port> [-C <conf>] -D -U flash:w:<hex>:i` [avr_tool.py:125-151].
- Leonardo (`atmega32u4`) needs a 1200-baud touch reset before flashing (`_trigger_reset`) [avr_tool.py:101-123].
- Per-board partno/programmer/baud table: see Q3.

**Devcontainer status:** `avrdude 7.1` at `/usr/bin/avrdude` [VERIFIED] → `>= 7.0`, so **no `avrdude.conf` needed** for the bench runs here. USB `/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0` present → flashing is drivable over the devcontainer USB passthrough (chip handling not needed for the smoke test).

**What the doc must tell a stranger (ONBOARD-04):** install avrdude (`apt install avrdude` / `brew install avrdude` / it also ships inside PlatformIO's toolchain); avrdude `>= 7.0` needs no `-c/--avrdude-config-path`, `6.3` does (use `-c`); the app auto-detects avrdude on PATH else pass `--avrdude-path`; the per-board `-b` selects the correct `.hex`; the `/dev/ttyACM*` port shuffles across replug so re-check which port is which board before each flash.

---

## Release-Cut Runbook (Step 0 — make BOTH channels public)

> Ordered per D-06 step (2). Every ⚠️ IRREVERSIBLE step is non-autonomous and MUST pause for explicit operator go-ahead (D-03). Secrets/`gh` auth are operator-side.

**Pre-flight (local, reversible, do first):**
0a. Resolve the D-01↔D-02 branch question with the operator (see BLOCKERS) — decide push-to-beta vs `workflow_dispatch`-from-v1.21. Runbook below assumes the recommended `workflow_dispatch`-from-v1.21 path (defers the beta merge per D-02/D-06).
0b. On the exact tree to be cut, in **both** sub-repos, pre-validate the CI gates locally so the dispatched run does not fail after a partial publish:
   - App: `pip install -e .[test]`; `python tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check`; regen `messages.py` → `ruff format` → `ruff check --add-noqa` → `git diff --exit-code firestarter/messages.py`; `ruff check .`; `ruff format --check .`; `pytest tests/ -v`. Validate against the py3.11 target where possible (py3.12-masks-CI).
   - Firmware: `codegen.py --check`; regen `include/messages.h` → `git diff --exit-code`; `pio test -e native`; `pio run` (confirm all three `firestarter_*.hex` build).
0c. Draft the ONBOARD-04 doc now (D-04 draft-first) so b11 ships with it.

**Firmware `.hex` channel (`henols/firestarter`):**
1. ⚠️ IRREVERSIBLE — operator dispatches `beta-build.yml` with the explicit version input:
   `gh workflow run beta-build.yml --ref v1.21-community-chip-validation-command -f beta_version=3.0.0b11`
   (or push-to-beta if 0a chose that). Produces a prerelease on `henols/firestarter` tagged `3.0.0b11`, `prerelease:true`, with `firestarter_uno.hex` / `firestarter_uno328pb.hex` / `firestarter_leonardo.hex` attached. **Without `-f beta_version=…` from a non-beta ref, the bump takes the STABLE path → wrong version.**
2. Verify per board: `firestarter fw --list --pre -b uno` / `-b uno328pb` / `-b leonardo` each show the `3.0.0b11` row with an asset URL (or raw GitHub API).

**App PyPI channel (`firestarter_app`):**
3. ⚠️ IRREVERSIBLE — operator dispatches `beta-release.yml`:
   `gh workflow run beta-release.yml --ref v1.21-community-chip-validation-command -f beta_version=3.0.0b11`
   → bumps `__init__.py` to `3.0.0b11`, commits, creates a GitHub Release tagged `3.0.0b11` on the app repo. (Does NOT publish to PyPI.)
4. ⚠️ IRREVERSIBLE (PyPI versions can never be reused) — operator dispatches PyPI publish (auto-trigger is suppressed):
   `gh workflow run publish.yml -f tag=3.0.0b11`
   → `python -m build` + `gh-action-pypi-publish`. Verify: `pip index versions firestarter --pre` shows `3.0.0b11`.

**Meta gitlink bump (D-01; not required for public reachability):**
5. After the b11 commits exist in both sub-repos, bump the meta-repo submodule gitlinks from PINNED b10 to the b11 commits and commit in the meta repo. (This is a dev-workspace consistency step; the community installs via PyPI/GitHub, not via meta gitlinks.)

**Then (D-06 continues):** per-board bench validation (Q4/Q5) → finalize doc → phase verification → operator-gated close ceremony (OUT of this phase).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Version bump b10→b11 | Manual edit of `__init__.py`/`version.h` | `update_version.py` via workflow `beta_version` input | CI is the canonical bumper; a hand-edit that disagrees with the tag-scan desyncs the release tag from the committed version. Pass the explicit input to control it deterministically. |
| Prerelease + asset upload | `gh release create` + manual `.hex` upload | `beta-build.yml` `action-gh-release files:` | Workflow builds all three envs and attaches assets in one step; hand-upload risks a missing/renamed asset that `fetch_release_info` silently skips. |
| Channel/asset resolution in the smoke test | re-querying GitHub API by hand | `firestarter fw --list --pre -b <board>` | Uses the exact `list_releases`/`fetch_release_info` code path `fw -i` uses — the authoritative acceptance check. |
| avrdude args per board | Hand-rolled `avrdude` invocation | `firestarter fw -i -b <board>` | `avr_tool.py` already encodes partno/programmer/baud + Leonardo reset + version-gated config path. |
| Config/DB isolation | Deleting/moving `~/.firestarter` | `FIRESTARTER_CONFIG_DIR` + fresh venv | Non-destructive, established v1.15/v1.21 seam; no risk to the operator's real config. |

**Key insight:** every mechanical primitive this phase needs already exists and is tested. The phase's real work is *sequencing irreversible publishes behind operator gates* and *recording honest bench evidence* — not writing code.

## Common Pitfalls

### Pitfall 1: Dispatching the cut from a non-beta branch without the version input
**What goes wrong:** `update_version.py` takes the STABLE path and produces `3.0.1` instead of `3.0.0b11`; a stable version gets published to PyPI irreversibly.
**Why:** `is_beta_mode` is False unless `GITHUB_REF==refs/heads/beta` or `BETA_VERSION` is set.
**How to avoid:** always pass `-f beta_version=3.0.0b11` on every `workflow_dispatch`; verify the dispatched run's version output before the PyPI step.
**Warning signs:** a `3.0.1` tag/release appears; `pip index versions` shows no `b11`.

### Pitfall 2: Assuming `fw -i` "working" proves the prerelease exists
**What goes wrong:** `fetch_release_info(channel='pre')` **falls back to stable** when no prerelease is found (firmware.py:289-294). A green `fw -i` may have flashed STABLE firmware.
**How to avoid:** Step 0 must positively confirm the `3.0.0b11` prerelease + assets via `fw --list --pre` per board; the per-board evidence must record the *resolved tag* and *downloaded asset name*, not just "success".

### Pitfall 3: Board mis-detection selecting the wrong `.hex`
**What goes wrong:** a uno328pb reporting `uno` (mis-ID) or a blank board (falls back to override `uno`) downloads `firestarter_uno.hex`.
**How to avoid:** always pass `-b uno328pb`; if the board proves to be a plain Uno, record it explicitly and switch to `-b uno` (D-05) — never silently accept the auto-detected board for the third board.

### Pitfall 4: Pushing to `beta` to trigger the cut
**What goes wrong:** a push auto-fires BOTH workflows (removing the D-03 human gate) and performs the D-02/D-06-deferred final beta merge as a side effect.
**How to avoid:** prefer `workflow_dispatch` from the v1.21 branch; keep beta merge for the close ceremony. Confirm with the operator (BLOCKER-1).

### Pitfall 5: CI gate failing after a partial publish
**What goes wrong:** codegen/ruff/pytest drift fails the app workflow AFTER the firmware prerelease already published → channels half-public.
**How to avoid:** run the full pre-flight (0b) locally on the exact tree first; publish firmware and app only once both pre-validate.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `release.published` auto-triggers PyPI | Manual `gh workflow run publish.yml -f tag=…` | Phase 20 E2E-01 (PAT lacks `workflow` scope) | PyPI publish is a deliberate operator step, not automatic. |
| avrdude 6.3 needs `-C avrdude.conf` | avrdude ≥7.0 auto-resolves config | avr_tool version gate | Devcontainer's 7.1 needs no config path. |
| `type`/`mem_type` fallback dispatch axis | protocol-only dispatch | v1.20 | Not this phase's concern, but the b11 cut is the first beta carrying it. |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The operator's `gh` is authenticated to `henols/firestarter` + `henols/firestarter_app` with rights to run the workflows and the workflows' secrets (`PERSONAL_ACCESS_TOKEN`, `PYPI_API_TOKEN`) are configured. | Q1, Runbook | If not, the cut cannot be triggered → publish-first blocker; planner must add an operator-precondition checkpoint. |
| A2 | The current `v1.21` branch tree passes all CI gates (codegen/ruff/pytest for app; codegen/native/pio for fw) as-is, or with only the version bump. | Runbook 0b | A failing gate blocks the cut; pre-flight 0b surfaces it before any publish. |
| A3 | `workflow_dispatch` from the `v1.21` branch ref (with `beta_version`) is an acceptable way to publish without merging to beta, honoring D-02/D-06. | Runbook, BLOCKER-1 | If the operator requires the code on beta first, the runbook's trigger mechanism changes (push-to-beta) and the deferred-merge framing is affected. |
| A4 | The firmware prerelease tag `3.0.0b11` (independent of the app) is acceptable; app and firmware version lines need not be coupled. | Q1 | If a specific firmware tag is required, the `beta_version` input for `beta-build.yml` changes. |
| A5 | `firestarter hw` is a sufficient minimal live op on a bare board for all three boards. | Q5 | If `hw` is unreliable on a board, planner falls back to `id`/identify (still no chip write). Recorded honestly per D-05/D-08. |

## Open Questions

1. **Publish without merging to beta — mechanism (see BLOCKER-1).** Recommendation: `workflow_dispatch` from v1.21 with `-f beta_version=3.0.0b11`; confirm with operator.
2. **Does the operator want the firmware prerelease on `henols/firestarter` specifically, or a fork?** The app URL is hardcoded to `henols/firestarter` — the prerelease must land there for `fw -i` to see it. If bench testing must target a fork, the app constant would have to change (out of this phase's zero-code-change scope) → flag as a blocker if raised.
3. **Changelog / prerelease notes content (D-01).** Minor; planner drafts from the v1.20+v1.21 requirement set.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| avrdude | ONBOARD-02 flash | ✓ | 7.1 (`/usr/bin/avrdude`) | ≥7.0 → no config path needed |
| USB serial passthrough | flash + smoke op | ✓ | ttyACM0/ttyACM1/ttyUSB0 attached | — (operator seats/replugs boards) |
| Python venv | ONBOARD-01 fresh install | ✓ | 3.12 (runtime OK; CI lint target is 3.11) | — |
| `pip install --pre firestarter` (3.0.0b11) | ONBOARD-01 | ✗ (not yet published) | — | **Publish-first blocker** — resolved by the Step-0 runbook |
| GitHub prerelease w/ `.hex` on henols/firestarter | ONBOARD-02 | ✗ (not yet published) | — | **Publish-first blocker** — resolved by the Step-0 runbook |
| `gh` CLI auth to henols repos | Runbook dispatch | operator-side (unverified) | — | operator credentials (A1) |
| PlatformIO (`pio`) | fw pre-flight build (local) | check at plan time | — | CI builds it if absent locally |

**Missing dependencies with no fallback:** none blocking within the phase's control — the two "not yet published" items ARE the phase's Step-0 work.
**Missing dependencies with fallback:** avrdude config (n/a at 7.1); py3.11 lint (validate carefully, py3.12 masks it).

## Package Legitimacy Audit

**N/A — this phase installs no NEW packages.** It installs the project's own already-published `firestarter` package (`pip install --pre firestarter`) into throwaway venvs for validation. Runtime deps `requests>=2.20` and `packaging>=21.0` are pre-existing, declared in `firestarter_app/pyproject.toml:48,52` [VERIFIED]. No third-party package is added (consistent with the v1.21 "no new third-party deps" lock).

## Validation Architecture

> `.planning/config.json` not read for an explicit `nyquist_validation:false`; treat as enabled. This is a hardware-gated VALIDATION phase — the "tests" are the per-board bench evidence records, not automated unit tests (the feature under test already has unit coverage from prior phases).

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual bench validation + evidence artifacts (no new pytest suites; the install/flash/channel code is already unit-tested in `firestarter_app/tests/`) |
| Config file | `firestarter_app/pyproject.toml` (`[tool.pytest] testpaths=["tests"]`) — used only for the release-cut CI gate, not for this phase's acceptance |
| Quick run command | `firestarter fw --list --pre -b <board>` (Step-0 acceptance, no hardware) |
| Full suite command | per-board `pip install --pre` → `fw -i -b <board>` → `fw` → `hw`, recorded to `chip-test/onboard-<board>.md` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ONBOARD-01 | fresh venv installs b11; `--version` reports it | install + smoke | `pip install --pre firestarter && firestarter --version` (in isolated venv) | evidence record (Wave: per-board) |
| ONBOARD-02 | bare `fw -i` → pre → board `.hex` → avrdude flash+verify | hardware | `firestarter fw -i -b <board>` (avrdude return 0) | evidence record |
| ONBOARD-03 | post-flash `fw` version+board + `hw` live op | hardware (bare board) | `firestarter fw` + `firestarter hw` | evidence record |
| ONBOARD-04 | community doc exists in `firestarter_app/doc/` | docs | file review + link check into `community-validation.md` | `firestarter_app/doc/beta-testing-install.md` (Wave 0: create) |
| Step 0 (ONBOARD-01/02) | both channels public | pre-hardware gate | `pip index versions firestarter --pre` + `fw --list --pre -b <board>` ×3 | halt-on-blocker |

### Sampling Rate
- **Per board (unit of work):** the full install→flash→smoke chain, one evidence record (D-08).
- **Phase gate:** Uno + Leonardo evidence records both PASS (HARD gates, D-05); uno328pb recorded (best-effort, advisory). Step-0 acceptance green on both channels before any board run.

### Wave 0 Gaps
- [ ] `firestarter_app/doc/beta-testing-install.md` — the ONBOARD-04 doc (draft-first per D-04, before the cut).
- [ ] Per-board evidence template `chip-test/onboard-<board>.md` (mirror `chip-test/dev-test-w27c512.md`).
- [ ] Step-0 acceptance script/checklist (PyPI `--pre` + `fw --list --pre` ×3 boards).

## Security Domain

> `security_enforcement` not disabled in config — included. This phase writes no product code, but it performs irreversible outward-facing publishes.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V1 Architecture / SDLC | yes | Operator-gated release (D-03) — irreversible publishes require explicit human authorization; not autonomous. |
| V6 Cryptography / secrets | yes | PyPI token + GitHub PAT are repo secrets on `henols/*`, never in the plan/repo; `gh` auth is operator-side. |
| V10 Malicious code / supply chain | yes | `name_firmware.py` validates `RURP_BOARD_NAME` against `[a-zA-Z0-9_-]+` before it flows into a filename (avr_tool builds `-U flash:w:<hex>`). Only the project's own published package/firmware is installed. |
| V5 Input validation | n/a | No new input surface (validation-only phase). |

### Known Threat Patterns for this phase
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Publishing the wrong version (stable instead of beta) to PyPI | Tampering / irreversibility | Explicit `beta_version` input + verify the dispatched run's version before the PyPI step (Pitfall 1). |
| Flashing the wrong `.hex` to a board | Tampering (hardware) | Explicit `-b <board>`; record resolved tag + asset name (Pitfall 3). |
| Autonomous irreversible publish | Elevation / loss of control | D-03 operator-authorization checkpoint immediately before each ⚠️ step. |

## BLOCKERS

- **BLOCKER-1 (needs operator decision before planning the runbook trigger): D-01 says "land v1.20 + v1.21 onto `beta`" but D-02/D-06 defer "any final `--no-ff` merge to `beta`" to the close ceremony.** These are in tension: the workflows trigger on push-to-beta, and landing code on beta *is* a merge to beta. The reconciliation that best honors all three decisions is to publish via `workflow_dispatch` against the `v1.21` branch ref (with `-f beta_version=3.0.0b11`), which makes both channels public WITHOUT merging to beta — deferring the beta merge to the close ceremony. The planner must confirm this interpretation with the operator, because the alternative (push-to-beta now) performs the deferred merge and auto-fires the workflows (removing the D-03 gate). This is the exact "release-mechanics / dual-repo lockstep" item CONTEXT D-09 flagged for research; it is resolvable but is a decision, not a fact.
- **BLOCKER-2 (verify, not necessarily blocking): operator `gh`/secrets access (A1).** The cut cannot be triggered unless the operator's `gh` is authenticated to `henols/firestarter` + `henols/firestarter_app` and `PERSONAL_ACCESS_TOKEN`/`PYPI_API_TOKEN` are configured on those repos. If not, Step 0 surfaces a publish-first blocker (as STATE.md's "Operator Next Steps" already anticipates). Planner should add an operator-precondition checkpoint before the runbook.

## Sources

### Primary (HIGH confidence — read directly this session)
- `firestarter_app/.github/workflows/beta-release.yml`, `publish.yml`, `release.yml`, `ci.yml` (listing)
- `firestarter/.github/workflows/beta-build.yml`, `firestarter/platformio.ini`, `firestarter/name_firmware.py`
- `firestarter_app/.github/scripts/update_version.py`; `firestarter/.github/scripts/update_version.py` (grep)
- `firestarter_app/firestarter/firmware.py`, `constants.py` (grep), `avr_tool.py`, `config.py`, `cli_handlers.py` (fw handler + auto-route + hw)
- `firestarter/include/version.h`; `firestarter_app/firestarter/__init__.py`
- git state (branch/tags/`rev-list --left-right`), `which avrdude` + version, `/dev/tty*`, `firestarter_app/doc/` + `chip-test/` listings
- `.planning/ROADMAP.md` (Phase 115), `.planning/REQUIREMENTS.md` (ONBOARD-01..04), `.planning/STATE.md`

### Secondary (MEDIUM — cross-referenced project memory)
- `reference_betarelease_ci_gotchas_v18`, `reference_devcontainer_py312_masks_ci_py39`, `reference_firestarter_app_python_test_env`, `project_uno328pb_correction`, `project_uno328pb_bench_instability_27_04`, `feedback_verify_port_identity_each_task`, `project_v121_submodule_branch_base`, `project_v120_milestone_seed`

## Metadata

**Confidence breakdown:**
- Release mechanics (workflows, version trap, channel repos): HIGH — read from the actual workflow + script files.
- Feature-under-test behavior (`fetch_release_info`, board detection, avrdude, config seam): HIGH — read from source.
- D-01↔D-02 reconciliation / trigger mechanism: MEDIUM — a decision requiring operator confirmation (BLOCKER-1).
- Operator `gh`/secrets availability: LOW — not verifiable from the workspace (A1/BLOCKER-2).

**Research date:** 2026-07-10
**Valid until:** 2026-08-09 (30 days) — or until the workflows / `firmware.py` release-fetch code change.
