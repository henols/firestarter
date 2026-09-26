# 3.1.x Release Readiness

## Context

Firestarter's stable channel has been frozen since 2025-11: firmware **2.0.6**, CLI **2.0.9**. All real work lives on `beta`, now at **3.1.0b2**, ahead of `main` by 1140 commits (app), 640 (fw) and 2316 (meta) — and `main` is also ahead by 20/6/18, so promotion is a real merge, not a fast-forward. No stable 3.x tag has ever existed.

The operator wants to be *able* to publish the first 3.x stable without committing to it yet. **This spec is readiness prep only. Nothing publishes** — no push to `beta` or `main`, no tag, no release. The deliverable is that the publish decision, when taken, is a runbook execution rather than a discovery exercise.

Three findings from the investigation shape the work:

**1. The stable release path is already broken, and has been since 2026-09-01.** Run `34784468070` (push to `main`, firestarter_app) shows *Create new patch release* succeed, ***Commit updated version* fail** with `GH013: Repository rule violations found for refs/heads/main — Changes must be made through a pull request`, and *Release* **skipped**. All three repos carry an identical active `Protect main` ruleset whose only bypass actor is `DeployKey`; `current_user_can_bypass` is `never`, so the owner cannot push directly either. **2.0.9 was hand-cut** — its release author is `henols`, created twelve minutes after the failed run. This inverts a standing hazard: a push to `main` in `firestarter_fw` today publishes *nothing*, because the auto-commit aborts the job before `pio run` and before the `Release` step. The old "any push to main cuts a stable release, there is no dry run" warning is false now — and re-arms the instant the bump is unblocked.

**2. `3.1.0` is unreachable by the automation.** `update_version.py` on `main` takes the stable path, discards the pre-release suffix and emits `major.minor.(patch+1)`. From `3.1.0b2` that is **`3.1.1`**. `--set-version` cannot rescue it: it forces beta mode and validates against a regex demanding a `b`/`rc` suffix. The first stable 3.x is either `3.1.1` or a hand-cut `3.1.0`.

**3. The 2.0.9 exposure cannot be fixed from the host side.** Publishing a `2.0.10` guard would protect almost nobody: `pip install --upgrade firestarter` resolves to the newest stable, so once 3.1.1 is on PyPI everyone upgrading lands there directly, and anyone who never upgrades never sees 2.0.10 either. The backport is dropped. What *does* protect the installed base is already in the firmware — retired ordinals 4 and 6 fall through `default: LOG_ERROR_ID_U8(MSG_ERR_UNKNOWN_CMD, handle.cmd)` at `firestarter_fw/src/firestarter.cpp:339`, so a 2.0.9 host's verify and standalone blank-check fail **loudly**. The residual quiet gap is narrow and specific, and is documented rather than fixed (see Task 5).

### Decisions taken

| | Decision |
|---|---|
| D-1 | Readiness prep only. Nothing publishes. |
| D-2 | Version guard: **forward half only**. It protects 3.1.x users from a future 3.2.x firmware. It does **not** protect 2.0.9 users from 3.1.1 — nothing on the host side can. |
| D-3 | No `2.0.10` backport. Unreachable by `pip install --upgrade` once 3.1.1 ships. |
| D-4 | No new bench validation. Release rests on 3.0.x evidence, annotated honestly. |
| D-5 | Open chip FAILs ship as documented known issues. |
| D-6 | First stable is **`3.1.1`** (recommended — matches the automation, costs nothing). Recorded as an open decision in the runbook; not acted on here. |

---

## Task 1: Save spec documentation

Create `agent-os/specs/2026-09-25-2218-3-1-x-release-readiness/` in the house four-file shape used by the three existing specs:

- **`shape.md`** — scope, decisions D-1…D-6 as bullets, context, standards applied
- **`plan.md`** — this plan
- **`standards.md`** — full text of the standards in Task 2 and Task 4
- **`references.md`** — the three 2026-09-20 documents that survive only on `origin/beta` under the deleted `.planning/` tree, each with its literal read command `git -C /workspaces show '1ea94a1e^:<path>'`, plus the two CI-defect todos the promotion trips over (`2026-09-13-release-yml-autocommit-vs-ruleset.md`, `2026-09-13-publish-yml-release-published-never-fires.md`)

No `visuals/` — this is process work.

---

## Task 2: The pre-flash version guard (3.1.x line)

**New file `firestarter_app/firestarter/fw_release_gate.py`** — a pure gate per `host/pre-serial-gates.md`: no I/O, no environment reads, no serial, importing only `packaging.version` and `firestarter.exceptions`. Named for the *release tag about to be flashed*, distinct from the three similarly-named checks that already exist.

```python
def feature_version(raw: str | None) -> tuple[int, int] | None
def is_refused(app_version: str | None, release_version: str | None) -> bool
def require_installable_release(app, release, *, allow_newer: bool = False) -> None
```

The rule: **refuse when `(fw.major, fw.minor) > (cli.major, cli.minor)`.** Patch and pre-release suffix ignored, so `3.1.0b2` and `3.1.0b5` are one feature version. Use `packaging.version.Version` — already a hard dependency (`pyproject.toml:50`) and already used by `_compare_versions`. It handles the `v` prefix (real in the fw tag history), pre-release suffixes, and one-segment versions natively, and raises `InvalidVersion` as the fail-closed hook.

**Do not reuse `serial_comm._is_version_sufficient`** — it does `int()` over a dot-split, so `_is_version_sufficient("3.1.0b2", "3.1.0")` returns `False` with a parse warning, which gets the required "allow" row exactly wrong. It also maps `x` → `999` and is a private method on the serial layer.

**Fail closed**: unparseable on either side refuses. **One deliberate exception**: a `None` release version returns without raising — there is no release, so nothing flashes, and `manage_firmware_update` already reports the failed fetch. Turning a GitHub outage into a version-mismatch refusal would be a lie. Document this in the module docstring; it is the one place the gate looks fail-open and is not.

**New exception** in `firestarter/exceptions.py`, after `FirmwareOperationError`:

```python
class FirmwareReleaseRefusedError(FirmwareOperationError): ...
```

Subclassing gets verbatim, prefix-free rendering through the existing `FirmwareOperationError` arm at `cli_handlers.py:220`. **Add no new arm** — `host/typed-refusals.md` says existing verbatim arms are the exception, do not add more.

**Refusal text** — module-level `_REFUSAL_FORMAT` and `_UNREADABLE_FORMAT` per `host/refusal-text.md`: hazard first, ASD-STE100, escape hatch named, and `pip install --upgrade firestarter` spelled out **with** the `--pre` variant, because a beta CLI upgraded without `--pre` silently drops to stable.

**Two call sites**, both calling the same `require_*`:

- **Authoritative** — `firmware.py::manage_firmware_update`, immediately after `fetch_release_info(...)` (~line 856) and before `force_install = flags & FLAG_FORCE`. This is the single funnel: one caller, no `try`/`except` in the function, and it guards where `latest_version` is *born* rather than on four separate downstream branches. It fires before `Confirm.ask`, so the operator is never prompted "Update now?" and then refused.
- **Early** — `cli_handlers.py::fw`, after the `--list` exit (~1714), before `_maybe_auto_route_to_pre_click` (~1737), guarded by `if firmware_version:`. The pinned target is knowable with no port open and no HTTP request. Safe ordering: the auto-route helper returns early on `firmware_version`, so the pinned path never reaches it.

`--list` and `--dfu-probe` stay ungated — enumeration is the operator's discovery path and must keep working during a refusal.

**Override flag: `--allow-newer-firmware`** (new, long-only, no short letter). **Do not reuse `--force`**: it is a *wire* flag (`FLAG_FORCE` → `command_dict["flags"]`), so overloading it would send the host's compatibility decision to a board whose protocol the host just declared it cannot speak; it also already waives the hw-revision gate, and one flag waiving two unrelated hazards is what `host/gate-polarity.md` warns against. No collision — no `--allow-*` option exists anywhere in the CLI. Plumbed as a keyword-only `allow_newer_firmware: bool = False` on `manage_firmware_update`, defaulting fail-closed for library callers.

**Behaviour change to call out in review**: the guard sits *before* the `is_up_to_date` short-circuit, so `fw` against a board already on 3.2.0 with a 3.1.0 CLI now refuses instead of printing "already up to date". That is correct, and the refusal names the fix — but a reviewer will read it as a regression unless the commit message says so.

**Relationship to `_maybe_auto_route_to_pre`** — complementary, neither subsumes the other. It catches firmware *older* than the CLI (a beta host downgrading itself); this gate catches firmware *newer*. It also feeds the gate: auto-route steers a beta CLI to the newest pre-release, which is the channel most likely to be ahead. Add a comment at `cli_handlers.py:320` noting the deliberate polarity split — auto-route fails *open* on `InvalidVersion`, this gate fails *closed*, and that asymmetry should be explicit rather than discovered.

**Out of scope, do not silently close**: `fw --stable` on a beta CLI remains an unguarded downgrade. That is the reverse mismatch, deferred by operator decision.

---

## Task 3: Tests for the guard

Land the module skeleton **before** the tests — `testing/non-vacuity.md` requires a test to fail on its own assertion, and pure-policy tests written first fail at collection with `ImportError`, which is a setup failure.

**New `firestarter_app/tests/test_fw_release_gate.py`.** Names `test_fw_version_guard.py`, `test_fwguard.py` and `test_fw_update_path_gate.py` are already taken by the connect-time floor and the deadlock regression — do not reuse them.

- **Parsing**: `3.1.0`→(3,1); `3.1.0b2`→(3,1); `v3.2.0`→(3,2); `3`→(3,0); `not-a-version`/`None`/`""`→`None`
- **The rule, both sides of the threshold**: 3.1.0/3.2.0 refuse; 3.1.0/3.1.5 allow; 3.1.0b2/3.1.0b5 allow; 3.2.0/3.1.0 allow; 3.1.0/3.1.0 allow (equality passes); 3.9.0/4.0.0 refuse; 4.0.0/3.9.0 allow
- **Absent evidence**: unparseable CLI, unparseable release, `None` CLI, `""` CLI → all raise. `None` release and `""` release → return, deliberately, with the reason in the test docstring
- **Override**: waives both the refusal and the unreadable case; omitting the kwarg still raises
- **Refusal text**: import the constants, never copy them; assert `pip install --upgrade firestarter` and `--allow-newer-firmware` appear in both; assert the subclass relationship
- **CLI wiring** (`CliRunner`, `obj=AppContext(...)` per `host/command-skeleton.md`): pinned refusal exits 1 **and `check_current_firmware` / `manage_firmware_update` were never called** — those mock assertions are the non-vacuity core, proving no port opened and no HTTP request happened. Plus: pinned pass reaches the manager; `--allow-newer-firmware` passes through; `--list` with a too-new release still exits 0 and prints the row

**Added to `tests/test_firmware_install.py`** as `TestNewerFirmwareRefusal`, reusing the existing `monkeypatch.setattr(fm, ...)` pattern: too-new release raises with **zero** calls to `_download_firmware_file`/`_install_firmware`; override installs; **`flags=FLAG_FORCE` without the override still raises** (the single most likely future regression); matching version unchanged; `(None, None)` fetch unchanged; the "already up to date on a too-new board" case now raises; and the headline end-to-end — bare `fw` on a pre-release CLI auto-routes to `pre`, resolves a too-new pre-release, refuses.

**Do not pin the literal `"3.1.0b1"`** — monkeypatch `firestarter.__version__` or pass it explicitly, or the suite breaks on the next release. No `--help` text test; `host/help-docstrings.md` forbids it.

Verify from a fresh clone per `testing/standalone-checkout.md` — the devcontainer's editable install points at `/workspaces` and masks CI-only defects. CI is Python **3.11**.

---

## Task 4: The promotion runbook — `/workspaces/RELEASING.md`

Meta repo root, beside `README.md` and `VALIDATED-EPROMS.md`. An operator runbook, not an agent-os doc. **Describes; performs nothing.**

- **Phase 0 — preconditions**: the `3.1.0` vs `3.1.1` decision written down; Known-Issues page live; CHANGELOG seeded; stable-install page live; ledger Notes annotated; milestone closed on `beta` and the latest `3.1.0bN` green.
- **Phase 1 — app first.** Disable `release.yml`; branch `release/3.1.x` from `main`; merge `origin/beta` (expect conflicts in `README.md`, `images/`, `__init__.py`); set the version by hand; **merge commit, never squash** — a squash collapses 1140 commits and destroys history that `git tag` scanning and `git log` both read. Tag and push (**not blocked** — the ruleset scopes to `~DEFAULT_BRANCH`, not tags). **Create the release as yourself, not via a bot** — that is what makes the `release: published` cascade deliver. Record the blocking point: `require_extra_approval_for_unattributed_changes: true` with `required_approving_review_count: 0` means a PR carrying commits not attributable to a GitHub account needs one approval; over 1140 commits that is a live risk — check `gh pr view <n> --json mergeStateStatus,reviewDecision` before you need it.
- **Phase 2 — firmware second.** Open the PR with `build.yml` **still enabled** — `pull_request` carries no branch filter, so it runs in full and yields the green compile plus the no-dev-tools assertion, with no publish step. Disable only after that run is green, then merge. **Blocking point: nothing builds the release assets** — `build.yml` has no `workflow_dispatch` and no `upload-artifact`, so the `.hex` files exist only as release assets. Build locally from the exact merge SHA without `DEV_TOOLS` and re-run the assertion by hand. **This is the moment `/releases/latest` flips from 2.0.6** and every un-upgraded 2.0.x CLI starts resolving it.
- **Phase 3 — meta last.** Advance both gitlinks. **Bare tag only, never a GitHub Release from the meta repo** — `v1.42` parses as PEP 440 `1.42`, and `Version("3.1.1") >= Version("1.42")` is true, so any CLI pointed at the meta repo reports firmware up to date forever.
- **Phase 4 — re-enable**, noting that from then on every merge to `main` re-fires the blocked auto-commit and leaves a red run until the bump path is fixed.
- **Phase 5 — post-release checks.**

Record the unblocking options without choosing one: hand-cut with workflows disabled (the only approach with evidence behind it — it is how 2.0.9 was cut); deploy-key bypass (the `DeployKey` slot is already in `bypass_actors`, but a deploy-key push re-triggers workflows → bump loop, needs `[skip ci]`); Actions as a bypass actor (unproven); bump by PR; or stop bumping on `main` (cleanest, needs the `--set-version` gate fixed first).

Also record the **second, independent blocker**: `release.yml` has no `pypi:` job while `beta-release.yml` does, so the stable PyPI upload depends on a `release: published` cascade that does not fire for bot-created releases. `2.0.8` exists on GitHub and **never reached PyPI**.

---

## Task 5: User-facing documentation

**`firestarter_app/CHANGELOG.md`** (new) — Keep-a-Changelog shape, `## [Unreleased]` on top, seeded with `3.1.0b2`. The app repo only, **not** the firmware: PyPI renders `README.md` and has no path to the wiki, so this is the one surface where the wiki is structurally unreachable; the firmware has no independent audience since users get it through `firestarter fw -i`. Add `Changelog` to `[project.urls]` and a link line in `README.md`.

**Wiki edits** in `/workspaces/firestarter.wiki/`:

- **`Breaking-Changes.md`** — replace the preamble. Current line 16 reads *"All of these are beta-only. Nothing is promoted to stable without operator authorization."* Apply the **pre-publication** version now (states that the stable channel is still 2.0.9/2.0.6 and that a plain `pip install` keeps you there, making no promise about promotion). Draft the **post-publication** version in the spec for Phase 4 of the runbook, but do not apply it.
- **`Install.md`** (new) — named `Install`, not `Install-Stable`; that is what a new user looks for. Mirrors `Install-Beta.md` minus every `--pre`, and gains the section with no counterpart there: **upgrading from 2.0.x, CLI first**. This is the page that carries the exposure in D-2/D-3.
- **`Known-Issues.md`** (new) — #21/#11/#12 (AT28C family), #86/#90 (SST39SF040, two independent reports), #62 (AE29F2008 erase). **State the #62 contradiction explicitly**: AE29F2008 has a PASS row in the ledger *and* an open firmware-caused erase failure. A row records one sweep, not a chip on which every command works. Plus a standing section that protocol `0x0D` is unverified by design. No chip counts — those are database-derived claims needing a claim-stamp footer.
- **`_Sidebar.md`, `Home.md`, `Install-Beta.md`, `Testing-Chips.md`, `Contributing.md`** — add the two new pages and cross-links.

**Unresolved before `Install.md` links to `Testing-Chips`**: `roadmap.md:40` says stable exposes `dev test` and `channel.py`'s `BETA_ONLY_DEV_COMMANDS` agrees, but `Testing-Chips.md` opens with *"You need the beta."* Stable firmware is built without `DEV_TOOLS`. Until settled, route chip testing through `Install-Beta`.

---

## Task 6: Honest ledger annotation

`/workspaces/VALIDATED-EPROMS.md` is **generated** by `.claude/skills/devtest-triage/scripts/eprom_ledger.py`. `render()` emits the H1, the tables, then `## Notes` — **there is no preamble slot**, and prose placed above the tables is destroyed by the next `add`/`write`. `read_notes()` preserves the `## Notes` body verbatim; it is the only hand-editable surface.

**Append two bullets to `## Notes`. Change nothing else.** First: every row is 3.0.0bNN evidence, no row has been re-run on 3.1.x, and since 3.1.0b1 moved verify and blank-check to the host those two steps are unproven on 3.1.x for every row. Second: a row records one passing sweep, not a chip on which every command works — AE29F2008 passed and `erase` still fails (gh#62).

Both are verifiable from the file's own Host and Firmware columns. No phase numbers, no `.planning/` paths, no `D-` ids. Governance is `agent-os/product/mission.md` §"Honest claims"; no standard covers prose honesty, and writing one (`standards/docs/evidence-claims.md`) is **deferred, not in this spec**.

---

## Task 7: Staleness sweep

- **`agent-os/product/tech-stack.md`** — delete the `.planning/` clause (deleted in `1ea94a1e`); name the ruleset precisely; **correct the factually wrong line 54-55** *"A push to `main` publishes the stable release"* — it does not, and has not since 2026-09-01; add the missing `pypi:` job finding.
- **`agent-os/product/roadmap.md`** — current version `3.1.0b2` not `3.1.0b1`; add firmware 2.0.6 to the stable-channel line; note all 11 ledger rows are 3.0.x evidence; mark in-progress item 5 done; rewrite the "path for the stable-release version bump" bullet — **all three** repos, **observed** not predicted, and the hazard is now a silent no-publish that re-arms when unblocked.
- **`/workspaces/CLAUDE.md`** — the trim dropped **"the meta repository must never publish a GitHub Release — bare milestone tags only"**, present at `41a34c6a:CLAUDE.md:88` and now nowhere in the working tree. Restore it, and restore a *corrected* form of the firmware `main`-push hazard. Both are the "costly to get wrong — it publishes a release" class the trim's own keep/drop rule says to keep.

---

## Verification

**Guard (Tasks 2-3)** — the real gate, run from a fresh clone because the devcontainer's editable install masks CI-only defects:

```bash
git clone /workspaces/firestarter_app "$SCRATCH/app" && cd "$SCRATCH/app"
export UV_CACHE_DIR="$SCRATCH/uv-cache"
uv venv --python 3.11 .venv
VIRTUAL_ENV=.venv uv pip install -e '.[test]'
.venv/bin/ruff check firestarter/ tests/ && .venv/bin/ruff format --check firestarter/ tests/
.venv/bin/pytest tests/ -o addopts="" --cov=firestarter --cov-fail-under=70
```

Then exercise the refusal by hand, with no board attached — it must refuse before any port opens:

```bash
firestarter fw --firmware-version 99.9.0        # refuses, names pip install --upgrade
firestarter fw --firmware-version 99.9.0 --allow-newer-firmware   # proceeds to fetch
firestarter fw --list                            # still enumerates, including too-new releases
```

**Docs (Tasks 4-7)** — `eprom_ledger.py check` must still report `ok: VALIDATED-EPROMS.md matches a fresh render` after the Notes edit. Confirm every wiki cross-link resolves against the 14 pages in `_Sidebar.md`. Confirm no file under `firestarter_app/` or `firestarter_fw/` was pushed and no tag created: `git -C <repo> status` clean on the milestone branch, `git log origin/beta..HEAD` shows only local commits.

**Scope guard** — `gh release list` for all three repos must be unchanged from its pre-task state, and `gh api repos/henols/firestarter_fw/releases/latest --jq .tag_name` must still return `2.0.6`.
