---
last_mapped_commit: 55ca612f
last_mapped_at: 2026-09-14T05:19:26.128Z
mapped_paths: .claude,.devcontainer,.github,.gitignore,.gitmodules,.vscode,CLAUDE.md
---

# Codebase Concerns

**Analysis Date:** 2026-09-14 (scoped remap: meta-repo / dev-environment / CI layer)
**Prior full audit:** 2026-05-08 (submodule internals)

> **Scope note.** The 2026-08-26 and 2026-09-14 remaps each covered ONLY the meta-repo shell:
> `.claude/`, `.devcontainer/`, `.github/`, `.gitignore`, `.gitmodules`, `.vscode/`, `CLAUDE.md`.
> The two submodules (`firestarter_fw/` firmware, `firestarter_app/` host CLI) were NOT scanned by
> either. All findings in the "Submodule Findings (2026-05-08)" section below are preserved verbatim and
> individually marked `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`.
> Treat them as leads, not confirmed-current defects. The "Meta-Repo / Dev-Environment / CI
> Concerns" section is freshly re-verified as of 2026-09-14.

---

# Meta-Repo / Dev-Environment / CI Concerns

**Verified:** 2026-09-14 (previously 2026-08-26 · commit `e0dc0622`)

## Security Considerations

**Plaintext Discord bot token on disk in the workspace:** — **REMOVED 2026-08-26** (commit `3e2f7d89`), partially resolved
- **Status 2026-08-26:** the workspace copy `.claude/channels/discord/.env` and the whole `.claude/channels/` tree are **deleted**, and the tracked provisioning that recreated them is gone. What follows described the pre-removal state. **Residual:** one copy of the token still exists at `~/.claude/channels/discord/.env` (outside the repo, so never a commit risk) and the credential is **still valid** — revoking it requires a token reset in the Discord Developer Portal.
- Risk: A live Discord bot credential is stored as a plaintext file at `.claude/channels/discord/.env` (credential kind: Discord bot token; value not transcribed here). It lives on the **host bind mount**, not in a container-only volume, by deliberate design — see `.devcontainer/devcontainer.json:59-61` (`containerEnv.DISCORD_STATE_DIR=/workspaces/.claude/channels/discord`) and `.devcontainer/post-create.sh:18-35`.
- Files: `.claude/channels/discord/.env`, `.claude/channels/discord/access.json`
- Current mitigation: **Commit protection verified** — `git check-ignore -v .claude/channels/discord` resolves to `.gitignore:4` (`.claude/*`), and only 9 files are tracked under `.claude/` (all under `.claude/skills/`). File mode is `0600`, re-asserted by `post-create.sh:34` (`chmod 600`). So the token is genuinely not committable today.
- Residual risk: The protection rests entirely on the single broad `.gitignore:4` `.claude/*` line plus its `!.claude/skills/` negation (`.gitignore:5`). Any future negation added under `.claude/` (e.g. `!.claude/settings.json`, `!.claude/channels/`) would silently un-ignore sibling paths. There is no `.claude/**/.env`-specific belt-and-braces pattern and no pre-commit secret scan.
- Recommendations: Add an explicit, non-negatable guard (`.claude/channels/**` and `**/.env` as their own entries) so the token's protection does not depend on one broad glob; add a pre-commit secret scan; rotate the token if the workspace has ever been shared or imaged.

**`Read` deny-list does not cover the token's actual path:** — still open, reduced scope
- Risk: `.claude/settings.local.json` denies `Read(.env)`, `Read(.env.*)`, `Read(.secrets)` — repo-root-relative patterns. The token lives at `.claude/channels/discord/.env`, which those three patterns do not obviously match. An agent reading that path is not blocked by policy.
- Files: `.claude/settings.local.json` (`permissions.deny`)
- Recommendations: Add `Read(**/.env)` to the deny list. (`Read(.claude/channels/**)` is moot in-repo since 2026-08-26 — that tree is deleted — but the home-directory copy at `~/.claude/channels/discord/.env` is still readable.)

**Blanket `Bash(git *)` and `Bash(python3 *)` in the tracked-intent allow list:**
- Risk: `.claude/settings.json` `permissions.allow` (110 entries) includes `Bash(git *)` and `Bash(python3 *)`. `python3 *` is arbitrary code execution, and `git *` reaches `git -c core.pager=...`/`--exec-path` style escapes. Every narrower entry in the same list (`Bash(git add *)`, `Bash(git status *)`, the long per-PR `gh pr merge` literals) is thereby dead weight — the broad entries subsume them, so the file reads as far more restrictive than it behaves.
- Files: `.claude/settings.json`
- Recommendations: Delete the two blanket entries, or accept them and delete the ~30 narrower git/gh entries they subsume so the file stops implying least-privilege it does not enforce.

**`autoMode` grants unattended `git push`:**
- Risk: `.claude/settings.json` sets `autoMode.allow = ["$defaults", "Bash(git push *)", "Bash(git -C * push *)"]`, and `.claude/settings.local.json` additionally allows `Bash(git push:*)` plus per-submodule push. In auto mode an agent can publish to `origin` with no human confirmation, in all three repos.
- Files: `.claude/settings.json`, `.claude/settings.local.json`
- Current mitigation: Branch discipline is a documented convention only (milestone branches), not enforced by any hook.
- Recommendations: Restrict to `Bash(git push origin gsd/*)`-shaped patterns; add a `PreToolUse` guard rejecting pushes to `beta`/`main`.

**`--privileged` container with the whole host `/dev` bind-mounted:**
- Risk: `.devcontainer/devcontainer.json:13-15` runs `--privileged` and bind-mounts `/dev`. Any code executed in the container (including agent-run code and `pip install -e` of submodule packages) has effectively host-level device access.
- Files: `.devcontainer/devcontainer.json:11-15`
- Current mitigation: Required for Arduino serial/flash access; the comment says to remove both if not flashing hardware.
- Recommendations: Ship a second non-privileged devcontainer variant for docs/planning-only sessions, and narrow the mount to `/dev/ttyACM*`/`/dev/ttyUSB*` plus a `dialout` group where the platform allows it.

## Tech Debt

**No CI of any kind runs against this repository:**
- Issue: `.github/` holds `CONTRIBUTING.md` and a four-file `ISSUE_TEMPLATE/` directory — there is no `.github/workflows/` directory in this repository. Nothing tracked here is checked by CI: no test, no lint, no build, no publish job, and no cross-repo consistency check of any kind.
- Files: `.github/`
- Impact: A regression anywhere in the mapped scope — including the codegen/sync tooling that is meant to keep both submodules' catalogs in lockstep — is only discovered downstream, inside a submodule's own CI, if at all.
- Fix approach: Not attempted by this remap. Recorded as a deliberately unpaid debt for this milestone; see this phase's `SUMMARY.md` for the disposition.

**Devcontainer Python (3.12) is newer than the host app's CI Python (3.11):**
- Issue: `.devcontainer/Dockerfile:1` is `FROM mcr.microsoft.com/devcontainers/python:3.12`; the container reports `Python 3.12.14`. `firestarter_app`'s CI runs on Python **3.11 only** (its workflows live in the submodule and were out of scope this run, so the 3.11 figure is carried from prior findings and should be re-confirmed against `firestarter_app/.github/workflows/` before acting).
- Files: `.devcontainer/Dockerfile:1`, `.devcontainer/devcontainer.json` (no `postCreate` venv pin), `.devcontainer/post-create.sh:8`
- Impact: A **newer** local interpreter masks CI-only failures in exactly one direction: syntax/typing/stdlib behaviour that 3.12 accepts and 3.11 rejects passes locally and breaks CI. This has already been observed to break `beta` CI. It also hides breakage as *collection errors* rather than assertion failures, which reads as an unrelated problem.
- Fix approach: `post-create.sh` should create and install into a `uv venv --python 3.11` for `firestarter_app`, so the default local interpreter matches CI. Note `post-create.sh:8` installs the app with the bare system `pip` (3.12) — that is the specific line to change.

**Node runtime version is hardcoded into hook paths, at two different versions:**
- Issue: Every hook command in `.claude/settings.local.json` is an absolute path through an nvm directory: some entries use `/usr/local/share/nvm/versions/node/v24.15.0/bin/node`, others `v24.16.0` — within the same file. `.devcontainer/devcontainer.json:26-28` pins only the node *feature* major (`"version": "22"`), which does not match either hardcoded path.
- Files: `.claude/settings.local.json`, `.devcontainer/devcontainer.json:26-28`
- Impact: A node patch-version bump (or a container rebuild resolving a different node) makes those absolute paths vanish, and hooks fail. Hook failures are not surfaced as test failures — this is a **fail-open** guard: `gsd-workflow-guard.js`, `gsd-validate-commit.sh`, and `gsd-read-guard.js` simply stop enforcing.
- Fix approach: Invoke bare `node` (it is on PATH for the shells hooks run in) and normalise all entries to one form.

**`.vscode/` is committed but hardcodes one developer's host paths:**
- Issue: `.vscode/settings.json` points clang-tidy at `/home/henrik/dev/c64/llvm-mos/bin/clang-tidy`, and `.vscode/c_cpp_properties.json` is an auto-generated file (its own header says "DO NOT MODIFY") full of `/home/henrik/dev/henrik/git/firestarter_prom/...` and `/home/henrik/.platformio/...` include paths. Inside the devcontainer the repo is at `/workspaces` and PlatformIO at `/home/vscode/.platformio` — none of these paths exist.
- Files: `.vscode/settings.json`, `.vscode/c_cpp_properties.json`
- Impact: C/C++ IntelliSense and clang-tidy are silently broken for every user except that one host checkout; a fresh clone gets red squiggles unrelated to the code.
- Fix approach: Gitignore `c_cpp_properties.json` (it is regenerated by the PlatformIO extension) and replace the absolute clang-tidy path with a PATH lookup or `${workspaceFolder}`-relative one.

**`.gitignore`'s tracked-scope comment still carries a premise `CLAUDE.md` has since dropped:** — partially resolved
- Status: `CLAUDE.md` has been corrected. It now states the repo tracks `.planning/`, `.claude/`, `tools/` and `.github/` — the previous "tracks only `.planning/` and `.claude/`" sentence, which omitted `tools/` (the authoritative `messages.toml` catalog) and `.github/`, is gone.
- Issue: `.gitignore`'s `skills-lock.json` comment was not updated to match: it still reads "this repo tracks only `.planning/` and `.claude/`, so it stays local like package*.json" — the exact premise `CLAUDE.md` used to carry.
- Files: `.gitignore`
- Impact: A reader of `.gitignore` alone still gets the outdated premise, though the practical risk is lower now that `CLAUDE.md` itself names `tools/catalog/` correctly.
- Fix approach: Update the `.gitignore` comment to match `CLAUDE.md`'s corrected sentence.

## Fragile Areas

**Duplicated source of truth across the two submodules (documented, unenforced):**
- Files: `CLAUDE.md` ("Key Architecture Points"), pointing at `firestarter_app/firestarter/constants.py` ↔ `firestarter_fw/include/firestarter.h`, and `firestarter_app/firestarter/serial_comm.py` ↔ `firestarter_fw/src/firestarter.cpp`
- Why fragile: Protocol constants and flag bits are physically duplicated in two independently-versioned repos, and `CLAUDE.md` can only *ask* that they be changed together. No workflow in this repository enforces any of it — the repo has no CI at all (above) — and the codegen tooling that could enforce a slice of it (`messages.toml`) covers that file only, not `constants.py`/`firestarter.h`.
- Safe modification: Change both files in the same milestone branch triple; regenerate from `tools/catalog/` where the value is catalog-derived.
- Test coverage: Parity tests exist inside the submodules but at least one is known to be a tautology (a `@requires_fw` test asserting a `#define` that does not exist), so a green parity suite is not evidence.

**Any meta-repo gate that inspects submodule files under-detects in a worktree:**
- Files: `.gitmodules`
- Why fragile: `git worktree add` leaves submodule directories **empty**. A gate that globs `firestarter_fw/...` or `firestarter_app/...` from the meta-repo then finds nothing to scan and exits 0 — a textbook fail-open. This repository has no workflow of any kind today (above), so nothing currently walks into this trap, but any future gate that does the obvious thing — checking out submodules recursively and globbing their tracked files — would inherit it.
- Related: gates that grep *submodule source* from the meta-repo also fail open on a plain **rename** in the submodule.
- Safe modification: Every submodule-inspecting gate must assert a non-zero file count before asserting on content, and fail if the count is zero.
- Test coverage: None — no test proves any gate goes RED.

**Gitlink re-pinning is easy to lose:**
- Files: `.gitmodules`, the `firestarter` / `firestarter_app` gitlinks
- Why fragile: `git commit -- <path>` with a pathspec silently discards a staged gitlink update, so a "re-pin the submodule" commit can land with no gitlink change and look successful.
- Safe modification: Stage the gitlink, then `git commit` with **no pathspec**; verify with `git diff HEAD~1 --submodule`.

**`post-create.sh` reaches into Claude Code's plugin cache and patches it:** — **RESOLVED 2026-08-26** (commit `3e2f7d89`)
- Status: this block was deleted along with the Discord bridge; `post-create.sh` no longer touches the plugin cache. Retained below as prior art, since the same anti-pattern would recur if any plugin is ever gated this way again.
- Files: `.devcontainer/post-create.sh:59-89` (as of `e0dc0622`; lines no longer exist)
- Why fragile: It globs `~/.claude/plugins/cache/claude-plugins-official/discord/*/`, takes the lexically-last directory, and rewrites that plugin's `.mcp.json` to redirect the MCP server through `.devcontainer/discord-singleton.sh`. This depends on an undocumented internal layout, picks the newest dir by *string sort* (not version sort), and wraps the whole thing in `except Exception` that prints and continues — a genuine failure is a log line, not an error, and `set -e` (line 2) never sees it.
- Safe modification: Fail loudly if the glob finds nothing when the plugin is expected, and re-run the patch on every session start rather than only at container create.
- Test coverage: None.

**`.gitignore` orphan-submodule class of failure (documented past incident):**
- Files: `.gitignore:31-36`
- Why fragile: The comment records that the **missing bare-path form** (`.planning/v1.7/upstream-rurp` without a trailing slash) let a nested clone get committed as an orphaned gitlink in `c502fc39`. A gitlink with no `.gitmodules` entry makes `actions/checkout` with `submodules: recursive` die with `fatal: No url found for submodule path` *before any assertion runs* — a failure mode any future submodule-checking-out workflow would need to guard against.
- Live risk: The same shape recurs for every local clone/worktree path the ignore file lists — `firestarter_app_py32/`, `firestarter_py32_ci/`, `chip-test/` (`.gitignore:56-60`) — all of which are given **only** the trailing-slash form, i.e. exactly the form that was insufficient last time.
- Safe modification: Add the bare-path twin for each of those three entries, matching the `upstream-rurp` fix.
- Test coverage: None. A `git ls-files --stage | awk '$1==160000'` check against `.gitmodules` would catch it in one line.

## Missing Critical Features

**The agent runtime is local-only and cannot be reproduced from a clone:**
- Problem: `.gitignore:4-5` ignores `.claude/*` and re-includes only `.claude/skills/` — 9 tracked files. Everything that defines *how the agent behaves* is untracked: `.claude/settings.json` (permissions, autoMode), `.claude/settings.local.json` (all 16 hook registrations), `.claude/hooks/` (20+ guard scripts including `gsd-validate-commit.sh`, `gsd-workflow-guard.js`, `gsd-read-guard.js`), `.claude/commands/`, `.claude/agents/`, `.claude/gsd-core/`, `.claude/gsd-file-manifest.json`.
- Blocks: Reproducibility and review. A fresh clone has no guards at all; two machines drift with nothing to diff; a permission or hook change is invisible to code review and unattributable in history. `post-create.sh:37-57` regenerates exactly two `settings.local.json` keys (`enabledPlugins`, `extraKnownMarketplaces`) as "config-as-code" — a good pattern applied to ~2% of the surface.
- Fix approach: Track a reviewed `.claude/settings.json` (secrets live in `.claude/channels/`, which stays ignored) and let `settings.local.json` hold only machine-specific overrides; or extend the `post-create.sh` regeneration pattern to hooks and permissions.

**Marketplace-installed skills are unversioned by design and unpinned:**
- Problem: `.gitignore:7-17` deliberately excludes `.claude/skills/find-skills/`, `.claude/skills/skill-creator`, `.agents/`, and the `skills-lock.json` manifest, with instructions to reinstall via `npx skills add anthropics/skills@skill-creator` rather than vendor.
- Blocks: Reproducibility — ignoring the **lock manifest** in particular means there is no record of which skill versions a given session ran, so a behaviour change from a skill update cannot be distinguished from a repo change. The two hand-authored skills (`devtest-triage`, `devtest-rootcause`) are tracked and unaffected.
- Fix approach: Track `skills-lock.json` (it is a manifest, not an artifact) even while the skill bodies stay ignored.

**`platformio.ini` is generated, ignored, and only regenerated at container create:**
- Problem: `.gitignore:19-20` ignores the root `platformio.ini`, which `.devcontainer/gen-platformio-ini.py` derives from `firestarter_fw/platformio.ini`. `post-create.sh:4-5` runs the generator once, at create time only.
- Blocks: After the firmware's `platformio.ini` changes (a new env, changed build flags), the root wrapper is stale until someone manually re-runs the generator — the script's own docstring says "Run manually after updating the firmware platformio.ini". PlatformIO IDE then builds against stale config from the repo root while `pio run -e ...` inside `firestarter_fw/` is correct, producing divergent results from the two invocation paths.
- Fix approach: Regenerate on session start (a `SessionStart` hook) or check freshness and warn.

## Test Coverage Gaps

**Zero tests for the meta-repo's own dev-environment tooling:**
- What's not tested: `.devcontainer/gen-platformio-ini.py` and the ~20 hook scripts in `.claude/hooks/`. (`.devcontainer/discord-singleton.sh` was also on this list — an flock singleton gate whose whole value was a race that was never exercised — but it was deleted 2026-08-26, commit `3e2f7d89`.)
- Files: `.devcontainer/`, `.claude/hooks/`
- Risk: These are the components that enforce agent guardrails. A silent failure in any of them is indistinguishable from correct operation. There is no CI at all in this repository (above) to catch one.
- Priority: High

---

# Submodule Findings (2026-05-08)

**Not re-verified in the 2026-08-26 or 2026-09-14 scoped remaps.** Every entry below is marked
`[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`. Re-confirm against the submodule
working tree before acting on any of them.

## Tech Debt

**Database override system is disabled:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Issue: `override_proms = None` is hardcoded on line 170 of `database.py`, disabling the `database_overrides.json` file entirely. A comment shows it was replaced with the new `minipro_complete_db.json` format but the override mechanism was never re-enabled or ported to the new format.
- Files: `firestarter_app/firestarter/database.py`
- Impact: Users cannot override EPROM definitions via the documented `~/.firestarter/database.json` override file path; the code path to merge overrides calls `_merge_databases`, which has a known comment noting "This might not merge correctly if format differs."
- Fix approach: Port the override merge logic to the new `minipro_complete_db.json` format and re-enable loading from `database_overrides.json`.

**Commented-out `get_eprom` pruning logic:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Issue: Lines 406–425 of `database.py` contain a large block of commented-out code that was responsible for trimming fields on non-full data fetches. The `get_eprom` function now always returns full data, and the comment explains nothing about whether this is intentional or a regression.
- Files: `firestarter_app/firestarter/database.py`
- Impact: Callers always receive the full dict; `convert_to_programmer` re-filters, so there is no runtime breakage, but the code is confusing and misleading.
- Fix approach: Remove the dead commented-out code block once it is confirmed the current behavior is correct.

**`globals()` introspection to derive command names:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Issue: Two places in `eprom_operations.py` (lines 163 and 217) resolve command names by scanning `globals()` for constants matching a numeric command code. This is fragile, slow, and hard to reason about.
- Files: `firestarter_app/firestarter/eprom_operations.py`
- Impact: If a constant is renamed, or two constants share the same value, the lookup silently returns the wrong name or raises `IndexError`.
- Fix approach: Use a reverse-lookup dict keyed by command integer, e.g. `COMMAND_NAMES = {COMMAND_READ: "READ", ...}`.

**`LEONARDO_BUFFER_SIZE` constant is unused:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Issue: `constants.py` defines `LEONARDO_BUFFER_SIZE = 1024`, but `_calculate_buffer_size()` in `eprom_operations.py` always returns `BUFFER_SIZE = 512` and ignores the Leonardo variant. The comment says it "matches the firmware's internal buffer size" without board-specific branching.
- Files: `firestarter_app/firestarter/constants.py`, `firestarter_app/firestarter/eprom_operations.py`
- Impact: Leonardo boards may be sending sub-optimal (half-sized) chunks, but more importantly, a defined constant that is never used signals unfinished work.
- Fix approach: Either wire up board detection (the board name is returned from `check_current_firmware`) to select the correct buffer size, or remove the unused constant.

**Duplicate/stale `build/` directory in repo:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Issue: `firestarter_app/build/lib/firestarter/` contains a copy of most source files. The `ic_layout.py` build copy is 301 lines (vs 626 in source), indicating it is significantly outdated.
- Files: `firestarter_app/build/`
- Impact: The stale build artifacts can cause confusion about which files are authoritative and may accidentally be imported.
- Fix approach: Add `build/` to `.gitignore` and remove the checked-in build artefacts.

**Inconsistent command dict key (`"cmd"` vs `"state"`):** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Issue: EPROM operations send `{"cmd": ...}` while hardware/firmware commands send `{"state": ...}`. The serial communicator works around this in `_probe_port` with `command_to_send.get("state") or command_to_send.get("cmd")`.
- Files: `firestarter_app/firestarter/eprom_operations.py`, `firestarter_app/firestarter/hardware.py`, `firestarter_app/firestarter/firmware.py`, `firestarter_app/firestarter/serial_comm.py`
- Impact: Adding new command types requires remembering which key to use, and the dual-lookup is error-prone.
- Fix approach: Standardize on a single key (e.g., `"cmd"`) across all command dicts and update the firmware protocol documentation accordingly.

**`pulse-delay` is always zero:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Issue: `_map_data` in `database.py` (line 346) sets `"pulse-delay": 0` with a comment "Not directly available in new format, may need parsing from string." It is never populated with a real value.
- Files: `firestarter_app/firestarter/database.py`
- Impact: EPROMs that require a specific programming pulse delay will use the wrong (zero) value, potentially causing write failures or data errors.
- Fix approach: Parse the pulse delay from the new database format string field, or add the field explicitly to the EPROM database entries.

**`_verbose` global in `utils.py` is set but never read:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Issue: `utils.py` declares a module-level `_verbose = False` but nothing in the module reads it; verbosity is handled via the standard `logging` framework everywhere else.
- Files: `firestarter_app/firestarter/utils.py`
- Impact: Dead code, minor confusion.
- Fix approach: Remove the unused global.

## Known Bugs

**`can_erase_str` uses wrong flag key:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Symptoms: The "Can be erased" field in `info` output is always `false` for Flash/EEPROM chips even when they support electrical erase.
- Files: `firestarter_app/firestarter/ic_layout.py` (line 510)
- Trigger: Run `firestarter info <flash-eprom>`.
- Workaround: None.
- Root cause: Line 510 reads `eprom_data.get("flags", 0) & 0x00000010` but the erasability bit is stored in `"info-flags"`, not `"flags"`. The `"flags"` key holds the simple programmer-facing flags (e.g., `FLAG_CAN_ERASE = 0x02`), not the detailed info-flags. The correct read would be `eprom_data.get("info-flags", 0) & 0x00000010`.

**`get_eproms(verified=False)` returns all EPROMs instead of unverified only:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Symptoms: Calling `get_eproms(verified=False)` returns all chips, not just unverified ones.
- Files: `firestarter_app/firestarter/database.py` (lines 380–383)
- Trigger: Call `db.get_eproms(verified=False)`.
- Workaround: None.
- Root cause: The condition `or (not verified)` is True whenever `verified=False`, so the filter never restricts results when `verified` is `False`.

**Typo in SIGINT handler message:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Symptoms: When the user presses Ctrl+C, the message "Prosess interrupted." is printed instead of "Process interrupted."
- Files: `firestarter_app/firestarter/main.py` (line 698)
- Trigger: Press Ctrl+C during any operation.
- Workaround: Cosmetic only.

## Security Considerations

**Firmware downloaded over HTTPS but not verified:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Risk: The firmware `.hex` file is downloaded from GitHub Releases over HTTPS, but there is no checksum or signature verification before flashing it to the Arduino.
- Files: `firestarter_app/firestarter/firmware.py`
- Current mitigation: HTTPS provides transport-level protection, and the URL is the official GitHub API endpoint.
- Recommendations: Verify a SHA-256 checksum published alongside the release asset, or verify a GPG signature, before passing the file to avrdude.

**Config file written without directory permission check:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Risk: If `~/.firestarter/` is world-writable (e.g., misconfigured system), a local attacker could pre-populate the config with a malicious `avrdude-path`, causing arbitrary code execution the next time `firestarter fw --install` is run.
- Files: `firestarter_app/firestarter/config.py`, `firestarter_app/firestarter/firmware.py`
- Current mitigation: Default `~` directory permissions restrict this on standard systems.
- Recommendations: Validate `avrdude-path` from config is a real executable in a trusted location before invoking it.

## Performance Bottlenecks

**Serial port probing adds 2-second stabilization delay per port:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Problem: Each candidate serial port connection adds a `time.sleep(2.0)` (`CONNECTION_STABILIZE_DELAY`) to allow the Arduino to reset. If multiple ports are tried, this multiplies linearly.
- Files: `firestarter_app/firestarter/serial_comm.py` (line 106)
- Cause: Arduino boards with auto-reset on DTR/RTS require time to leave the bootloader and enter application mode.
- Improvement path: Cache the last successful port in config (already done) so the preferred port is tried first and the delay is only paid once on first connection. Consider reducing delay or using a readiness handshake to detect when the board is ready earlier.

**O(n) linear scan of entire EPROM database on every lookup:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Problem: `get_eprom`, `get_eprom_config`, and `search_eprom` iterate over all manufacturers and all ICs on every call. With thousands of entries in `minipro_complete_db.json`, this is noticeable.
- Files: `firestarter_app/firestarter/database.py`
- Cause: The database is stored as a nested dict of lists (`{manufacturer: [ic, ic, ...]}`), not indexed by part number.
- Improvement path: Build an inverted index `{part_number.lower(): ic_data}` during `_initialize_database_core` for O(1) name lookups.

## Fragile Areas

**`expect_ack` loops forever on unexpected response types:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Files: `firestarter_app/firestarter/serial_comm.py` (lines 234–246)
- Why fragile: The `expect_ack` loop only breaks on `"OK"` or `"ERROR"` responses. Any other response type (e.g., `"WARN"`, `"DATA"`) causes the loop to call `get_response` again. A firmware bug that sends only `"WARN"` responses will spin until `get_response` itself times out, which takes `DEFAULT_RESPONSE_TIMEOUT = 10` seconds per call, potentially looping for a very long time.
- Safe modification: Add a counter or dedicate a maximum retry limit; log and raise on unexpected types after N attempts.
- Test coverage: No unit tests; only tested via physical hardware integration tests in `.sh` scripts.

**State machine in `_run_state_machine` assumes INIT always succeeds:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Files: `firestarter_app/firestarter/eprom_operations.py` (line 242)
- Why fragile: `_ = self._execute_phase("INIT", progress)` discards the return value. If INIT fails with a programmer error, `_execute_phase` raises `EpromOperationError`, which is caught by the outer try/except — but the MAIN ACK (`self.comm.send_ack()`) on line 245 is sent unconditionally before checking anything, potentially desynchronizing the protocol.
- Safe modification: Validate the INIT return value before sending the MAIN start ACK.
- Test coverage: No unit tests.

**Database merge (`_merge_databases`) uses shallow `.update()`:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Files: `firestarter_app/firestarter/database.py` (line 208)
- Why fragile: When merging user overrides, `existing_names[manual_item["name"]].update(manual_item)` performs a shallow dict update. Nested dicts (e.g., `programming`, `electrical`) in the override will replace, not merge, the base entry's nested fields.
- Safe modification: Use a deep-merge utility instead of `.update()`.
- Test coverage: No automated tests.

**`_read_voltage_loop` uses tuple unpacking on `get_response` return:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Files: `firestarter_app/firestarter/hardware.py` (line 204)
- Why fragile: Line 204 calls `response_type, message = comm.get_response()`, but `get_response` returns a `Response` namedtuple, not a plain tuple. While namedtuple unpacking works, if `get_response`'s return type changes this will break silently.
- Safe modification: Use `response.type` and `response.message` directly (as done everywhere else).
- Test coverage: None.

## Dependencies at Risk

**`requests` used for GitHub API without retry or rate-limit handling:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Risk: GitHub API rate-limits unauthenticated requests to 60/hour. If the rate limit is hit, `fetch_latest_release_info` fails silently and returns `(None, None)`, which prevents firmware installation even when `--install` is passed.
- Impact: Firmware update check fails; user gets a confusing error about "latest firmware URL not available."
- Migration plan: Add `Retry` adapter to the `requests.Session`, or cache the latest-release response locally with a TTL.

**`argcomplete>=3.6.2` is a recent pinned minimum:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Risk: `argcomplete` 3.6.2 was released recently; older system Python environments may not satisfy this constraint, breaking installation.
- Impact: `pip install firestarter` fails on systems with older package caches.
- Migration plan: Evaluate whether any 3.6.2-specific features are actually used; if not, relax to `>=2.0`.

## Missing Critical Features

**No partial-write recovery:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Problem: If a write operation is interrupted mid-way (power loss, USB disconnect), there is no way to resume from the last written address. The user must restart the write from the beginning.
- Blocks: Reliable operation on large (1 MB+) Flash chips where write time is significant.

**No automated unit tests:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Problem: The test suite consists entirely of bash integration scripts (`firestarter_test.sh`, `write_test.sh`) that require physical hardware. There are no Python unit tests, no mocks for serial communication, and no CI configuration.
- Blocks: Confident refactoring, contributor onboarding, CI/CD pipelines.

**Board type not persisted after firmware check:** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- Problem: `check_current_firmware` returns the board name from the programmer, but this is never stored in config. On the next run, `_install_with_avrdude` falls back to the CLI `--board` argument default (`"uno"`), which may be wrong for Leonardo users.
- Blocks: Correct firmware installation on Leonardo boards without always passing `--board leonardo`.

## Test Coverage Gaps

**Serial communication layer (`serial_comm.py`):** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- What's not tested: Response parsing, timeout handling, checksum verification in `read_data_block`, port probing logic, firmware version comparison.
- Files: `firestarter_app/firestarter/serial_comm.py`
- Risk: Protocol bugs or regressions in checksum, timeout, or version-check logic will only be caught at hardware integration time.
- Priority: High

**Database loading and lookup (`database.py`):** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- What's not tested: Singleton initialization, JSON loading failure paths, `_merge_databases` correctness, `get_bus_config` pin conversion, `search_chip_id`.
- Files: `firestarter_app/firestarter/database.py`
- Risk: Silent data corruption in pin mappings or incorrect EPROM definitions sent to hardware.
- Priority: High

**EPROM operations state machine (`eprom_operations.py`):** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- What's not tested: State machine phase transitions, write chunking protocol, progress reporting, error recovery, checksum generation.
- Files: `firestarter_app/firestarter/eprom_operations.py`
- Risk: Protocol desynchronization bugs are hard to diagnose without hardware.
- Priority: High

**Firmware manager (`firmware.py`):** `[unverified in 2026-08-26 and 2026-09-14 scoped remaps — may since be fixed]`
- What's not tested: Version comparison edge cases (e.g., `x` wildcard replacement), download failure paths, avrdude subprocess invocation, port selection logic.
- Files: `firestarter_app/firestarter/firmware.py`
- Risk: Incorrect version comparison could prevent update or force unnecessary re-flash.
- Priority: Medium

---

*Concerns audit: submodule layer 2026-05-08 (unverified) · meta-repo / dev-env / CI layer 2026-08-26, re-verified 2026-09-14*
