# Documentation Reorganization — wiki, meta and sub-repo docs

## Context

The Firestarter docs are spread over 15 wiki pages and about 20 repo `.md` files in 3 repos. Much of the content is repeated, and many facts are stale. Some pages contradict each other.

- **Wrong stable version:** some pages still say stable is 2.0.9. Stable **3.1.0** shipped 2026-09-26, and beta is now 3.1.0b5.
- **Three change-history sources:** app `CHANGELOG.md` (it stops at 3.1.0b2), wiki `Breaking-Changes` (its headings are internal milestone IDs), and GitHub release notes (empty).
- **Logos in three repos:** logo copies are in the meta, app and fw repos. The wiki hot-links the *old* pixel-art logo from `firestarter_app`.
- **Two Ko-fi IDs,** and no Ko-fi link on the meta README or the wiki.
- **Datasheet links:** the wiki's Lockable-PROMs page holds all 8.
- **Process content in technical docs:** they hold about 100 phase, plan and requirement IDs (PROTOCOLS.md, DECODE-NOTES.md, the py32f071 records). They also repeat each other (PINOUTS.md ≈ wiki Pin-Maps).
- **Gaps:** no wiki page explains how to *read* a chip.

**Intended outcome:**
- The wiki is the user manual: install, read, program, a short beta section, and the necessary technical reference.
- The meta README is the hub. It links the wiki and the two sub-repo READMEs, and it holds the **only** change log and `VALIDATED-EPROMS.md`.
- The sub-repo READMEs link back to the meta README and to their own short technical docs.
- Every document uses the same logo, hosted only in the meta repo.
- There are no datasheet links, and the Ko-fi link (`E1E21I2WWW`) is on every entry page.

## Decisions (from shaping)

| | Decision |
|---|---|
| D-1 | One change log: **`/workspaces/CHANGELOG.md`** in the meta repo, for the CLI and the firmware. The app `CHANGELOG.md` and the wiki `Breaking-Changes` page are removed. |
| D-2 | Delivery: one `docs/reorganize` branch and one PR to `main` in each of the 3 repos. I do not merge. The wiki is committed locally and pushed **only after the operator OKs it**. Nothing is pushed to `beta`, because every beta push publishes. Doc-only pushes to `main` are path-ignored. A push that changes `pyproject.toml`/`MANIFEST.in` runs `release.yml`, which finds the existing tag `3.1.0` and skips the release (`firestarter_app/.github/workflows/release.yml:71`). |
| D-3 | Logo: the horizontal wordmark `images/branding/firestarter_logo_horizontal.png`, at one absolute URL: `https://raw.githubusercontent.com/henols/firestarter/main/images/branding/firestarter_logo_horizontal.png` (it is already on meta `main`). All other logo files in the app and fw repos are deleted. |
| D-4 | Ko-fi: `https://ko-fi.com/E1E21I2WWW` only. It goes on the meta README, the app and fw READMEs, wiki Home and `_Sidebar`. The badge image is a shields.io URL, so no repo hosts `ko-fi.png`. |
| D-5 | Wiki `Lockable-PROMs` is deleted entirely. Nothing replaces it. |
| D-6 | Split: the **wiki is for users** and the **repo is for developers**. Wiki Pin-Maps keeps the socket tables and the adapter wiring. `PINOUTS.md` keeps only the shield internals and links the wiki for the socket tables. `PROTOCOLS.md` is rewritten as a short developer reference. |
| D-7 | In scope: delete app `val-results/`, clean `tools/DECODE-NOTES.md`, and clean the py32f071 records **together with the fw tests that pin them**. |
| D-8 | Truth source: the stable pages describe **3.1.0** (app `release/3.1.x`, fw `main`). Beta-only behaviour appears only on the Beta page and in the change log. Every command and flag is checked against `firestarter <cmd> --help` of that build. |
| D-10 | Every doc in scope is written with the `asd-ste100` skill: STE-flavored mode for READMEs, the change log and wiki prose; Strict mode for procedures and warnings. `.claude/skills/asd-ste100/scripts/ste-lint.py --disable synonym-rotation` reports 0 hard violations per file (synonym-rotation is a lexical rule, advisory in STE-flavored mode, and it collides with command names such as `verify` and `erase`). |
| D-9 | No internal process words (GSD, phase/plan/requirement IDs, milestone IDs, `.planning/`, claim-stamps, "relocated from…" footers) in any doc in scope. Excluded from scope: `CLAUDE.md` files, `agent-os/`, `.claude/`, test fixtures. |

**Standard header** (the same on every doc in scope; wiki pages and repo docs alike):
```html
<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter/main/images/branding/firestarter_logo_horizontal.png" alt="Firestarter EPROM Programmer" width="400"></p>
```
**Ko-fi badge:** `[![Buy me a coffee](https://img.shields.io/badge/Ko--fi-Buy%20me%20a%20coffee-FF5E5B?logo=ko-fi&logoColor=white)](https://ko-fi.com/E1E21I2WWW)`

---

## Task 1: Save spec documentation

Create `agent-os/specs/2026-09-27-1140-documentation-reorganization/` in the house four-file shape (like `agent-os/specs/2026-09-25-2218-3-1-x-release-readiness/`):
- **plan.md** — this plan
- **shape.md** — scope, D-1…D-9, the inventory findings (the contradictions list, and the Ko-fi history that shows `E1E21I2WWW` has been there since 2025-07-18)
- **standards.md** — the full text of `host/help-docstrings`, `testing/non-vacuity`, `testing/standalone-checkout` and `testing/no-source-introspection`
- **references.md** — the prior spec's structure, the wiki at `firestarter.wiki` commit `6ef34f4`, and the ledger generator `.claude/skills/devtest-triage/scripts/eprom_ledger.py`

No `visuals/`.

## Task 2: Logos and Ko-fi (all 3 repos)

- `firestarter_app`: delete the whole `images/` folder: `images/firestarter_logo.png`, `images/ko-fi.png` and `images/branding/*`, which holds 4 files.
- `firestarter_fw`: delete `images/branding/`. **Keep** `document/rurp_ctrl_reg_rev2.png`, because it is a schematic and not a logo. Reference it from `PINOUTS.md`'s control-register section.
- Meta: keep `images/branding/firestarter_logo_horizontal.png` as the only logo.
- Update `RELEASING.md` (lines ~118/142/163) so that it no longer expects `images/` merge conflicts.
- **Order:** the meta URL already works. The wiki push and the app/fw PR merges can happen in any order, because nothing will reference app images afterwards.

## Task 3: The one change log — `/workspaces/CHANGELOG.md`

Keep a Changelog format. There is one entry for each published version, newest first: `3.1.0b5`, `3.1.0b4`, `3.1.0`, `3.1.0b3`, `3.1.0b2`, `3.1.0b1`, then one condensed `3.0.0 pre-releases` entry. That entry folds in the user-relevant items of the Breaking-Changes "v1.32 / v1.20 / v1.10" sections without their milestone labels. Last comes `2.0.x and older`, which is one line that links the GitHub releases.

- **Sub-sections:** Added/Changed/Fixed/Removed, and each line is tagged **CLI** or **Firmware**. One **Compatibility** line gives the CLI↔firmware pairing rule.
- **Source for each entry:** `git log <prev-tag>..<tag> --no-merges` in both sub-repos. Drop the "Apply automatic changes" and chore noise. Beta-only entries (after 3.1.0) are marked as pre-release.
- `3.1.0` has an **"Upgrading from 2.0.x"** block: upgrade the CLI first, then the firmware. This text comes from wiki Install §5 and Breaking-Changes.
- App repo: delete `CHANGELOG.md`. Remove it from `MANIFEST.in` and from `[tool.setuptools.package-data]` if it is listed there. In `pyproject.toml`, set `[project.urls] Changelog` → `https://github.com/henols/firestarter/blob/main/CHANGELOG.md`.

## Task 4: `VALIDATED-EPROMS.md` via its generator

The file is generated, so change `render()` in `.claude/skills/devtest-triage/scripts/eprom_ledger.py`. Do not edit the `.md`.
- Emit the standard header and a 3-line intro: what "validated" means (a real write→read→verify on silicon), that the evidence versions are shown, and how to add a chip (a link to wiki Testing-Chips).
- Make the columns precise. The `Families` "Parts" column counts alias names, not DB rows (229 vs 189). Either count DB entries or rename the column to say what it counts. Pick the one that is true, and state it in the heading.
- Regenerate with the script's `write` command, then run `check` and the skill's tests (`scripts/tests/`, `test_supersede.py`). Add a test that proves the header and intro are emitted.

## Task 5: Meta repo docs

- **`README.md`:** logo, pitch, **Documentation → wiki**, **Repositories** table that links each sub-repo **README** (`firestarter_app#readme`, `firestarter_fw#readme`), links to `CHANGELOG.md` and `VALIDATED-EPROMS.md`, reporting a problem, Ko-fi badge + short "Support" line.
- **`RELEASING.md`:** remove the stale facts. 3.1.0 shipped. The stable path is now tag-driven. The app `release.yml` has a `pypi` job. The "3.1.0 unreachable" and "frozen at 2.0.9" text goes. Also update the Phase-1 changelog step to point at the meta `CHANGELOG.md`. Add the header.
- **`CLAUDE.md` Release Hazards:** fix only the stale paragraph "A push to `main` currently publishes nothing…". It now publishes when the version on main has no tag yet. `agent-os/product/roadmap.md` also needs a one-line fix to its "Current version" line.
- **`.github/CONTRIBUTING.md`**, **`.devcontainer/README.md`:** header. Change `cd firestarter` to `cd firestarter_fw` at line 37. `ISSUE_TEMPLATE/bug-report.yml`: change the placeholders from 3.0.0b22 to 3.1.0.

## Task 6: `firestarter_app` docs

- **`README.md`** (it is also the PyPI page, so **every link must be absolute**):
  - The header, then the PyPI and MIT badges and the Ko-fi badge.
  - A short intro that has no duplicate RURP paragraph, plus a link **up to the meta README**.
  - Install is shortened to `pip install firestarter` + `fw -i -b <board>` + a wiki Install link.
  - The command table (it is correct today).
  - "Developer docs" links to `tools/DECODE-NOTES.md`.
  - Contributing → wiki, and Changelog → the meta `CHANGELOG.md` (absolute).
  - Delete the second Ko-fi button (`M4M2Z7VNE`) and the stale "From 3.1.0b1" pre-release framing.
- **`SUPPORT.md`:** header, and merge it with the Contributing pointer.
- **`tools/DECODE-NOTES.md`:** header. Remove all phase/plan/requirement/decision IDs and the `.planning` references, and keep every decode fact. `tests/test_build_db_inclusion.py:75,141` cite "§4/§5", so **keep the section numbering**, or update those two docstrings in the same commit.
- **Delete** `val-results/` (6 files).

## Task 7: `firestarter_fw` docs

- **`README.md`:**
  - The header, the Ko-fi badge and a link up to the meta README.
  - The boards table: add py32f071 as beta-only, "no PCB exists", with a link to `platform/py32f071/README.md`.
  - Build, and install via the CLI.
  - Links to `PROTOCOLS.md` and `PINOUTS.md`.
  - Remove the false "machine-read claims region" sentence (lines 69-70) and the duplicated 0x0D paragraph.
  - Change the history link → the meta `CHANGELOG.md`.
- **`PROTOCOLS.md`:** rewrite it as a developer reference of about 200 lines.
  - One overview table: protocol → handler → chip count → VPP.
  - One section per protocol with the write, erase and verify algorithm, the key timing, and the VPP/pin roles. Each datasheet is cited **by name and page only, with no link**.
  - The pulse-override and VCC-ceiling text appears once, not three times.
  - Remove the claims markers, the stamps, all phase and ID references, the fragment at line 16 and the broken `[Pin Maps](Pin-Maps)` link (it becomes an absolute wiki link).
  - Chip counts come from `firestarter_app/firestarter/data/chip_database.json`.
- **`PINOUTS.md`:**
  - Keep the Arduino↔shield pins, the A2/A3 analog inputs and the control-register table (show both the `0x01` and the `HARDWARE_REVISION` `0x100` bit positions), with a link to the schematic PNG.
  - Delete the 17 socket tables and the adapter text. The wiki Pin-Maps page holds them.
  - Settle the adapter pin-21 conflict against the code before the adapter text moves to the wiki.
- **`platform/py32f071/`:** merge the five records into the `README.md` plus **one** design record for config storage and flash path. Rename `v1.23-FLASH-PATH-DECISION.md` to a name with no milestone ID.
  - Remove the GSD, phase and ID references, the broken `../notes/`, `../ROADMAP.md` and `../milestones/` links, and the stale `firestarter/platform/...` path prefixes.
  - Remove the reference to the missing `scripts/check_release_assets.py`.
  - Update the linker-script comment that cites `CONFIG-STORAGE.md`.
  - **Update the tests that pin these files in the same commit:** `tests/test_flash_path_record_sync.py`, `tests/test_config_storage_design_vendored.py`, `tests/test_py32_flash_map.py:146,410`, `tests/test_flash_geometry_recorded_before_linker.py:90`.
  - Some of those tests check a git history property (for example the "adding commit" in `test_flash_geometry_recorded_before_linker`). A rename breaks that property. Where it breaks, change the assertion to the content fact that the test protects. Do not delete the check. Follow `testing/non-vacuity`: each changed check still has a violating-input test.
- **`.github/ISSUE_TEMPLATE/config.yml:4`:** change `firestarter_prom` → `firestarter`. This closes todo `2026-09-27-fw-issue-template-still-names-firestarter-prom.md`.

## Task 8: Wiki restructure (`/workspaces/firestarter.wiki`, branch `master`)

Target pages, grouped in `_Sidebar.md` as **Getting started / Using Firestarter / Reference / Project**:

| Page | Content |
|---|---|
| Home | What it is, a 3-step quick start that links Install, a page index, links to the meta README, CHANGELOG and VALIDATED-EPROMS, and Ko-fi |
| Install | Stable 3.1.0: board table, pip/pipx, `fw -i -b`, check with `fw`/`hw`, **upgrading from 2.0.x**, and when something goes wrong |
| Beta-Channel (renamed from Install-Beta; short) | What the pre-release channel is and its risk, `pip install --pre` in a venv, firmware on beta, the list of beta-only features (from the change log), how to go back to stable, and reporting |
| Shield-Revisions | The revision table, **jumper settings per revision**, the VPP pot adjustment (`vpp`/`vpe`), detection and `rev` override. Settle the Rev 2.2 R41/band contradiction against `firestarter_fw/include/rurp_shield.h` |
| **Reading-Chips (new)** | `search`, `info` (the pin layout and jumpers), `id`, `read` (the output file, the region), `blank` |
| Writing-and-Verifying | `write` (blank check, erase, `--verify`, SDP flags), `verify`, `blank`, `erase` and the exit codes. Remove all "(from 3.1.0b1)" tags |
| Known-Issues | Refreshed from `gh issue list -R henols/firestarter --state open` |
| Testing-Chips | `dev test` as it is today; it links VALIDATED-EPROMS |
| Pin-Maps | The socket tables and the adapter wiring (the canonical copy). The link to PINOUTS.md now says "shield internals" and uses `blob/main` |
| Programming-Protocols | A user summary: which protocol a chip uses and what works. The flag-bit table moves to Chip-Database-Fields |
| Chip-Database-Fields | The user override file and the fields. Settle the 18-vs-20 page_size count against the DB |
| Shell-Completion | Fix the PowerShell line (use `$env:` syntax) and the "save to completions directory" step |
| Contributing | Issues and PRs, plus links to the sub-repo READMEs for dev setup |
| **Deleted** | Breaking-Changes (→ CHANGELOG) and Lockable-PROMs (D-5) |

On every page: the standard header; no claim-stamps, HTML markers or "relocated" footers; no datasheet links; no internal IDs; repo links use `blob/main`. Commit locally. **Do not push until the operator OKs it.**

## Task 9: Final sweep and PRs

- Run the verification below. Commit on `docs/reorganize` in each repo. Open PRs to `main` in app, fw and meta. The meta PR does not bump gitlinks. Show the wiki diff for approval, then push the wiki.
- Follow-up note for the operator (not done here): at the next beta cut, carry these doc changes to `beta`, because that cut publishes. The 3.1.0 GitHub release bodies are empty. They could link the new CHANGELOG.

---

## Verification

1. **Doc sweep across the four trees** (scope files only):
   - `grep -rniE 'phase [0-9]|plan 0|\.planning|gsd|\b[A-Z]{2,6}-[0-9]{2}\b|claim-stamp|firestarter_prom|v1\.[0-9]{2}'` → 0 hits.
   - `grep -rniE '\.pdf|datasheet[^s ]*\]\(http'` → 0 hits.
   - `grep -rn 'ko-fi.com/' | grep -v E1E21I2WWW` → 0 hits.
   - Each doc in scope starts with the standard header line.
   - `git ls-files '*.png'` in app and fw → only `document/rurp_ctrl_reg_rev2.png`.
2. **STE:** `python3 .claude/skills/asd-ste100/scripts/ste-lint.py --disable synonym-rotation <file>` exits 0 (0 hard violations) on every doc in scope and every wiki page.
3. **Links:** run a markdown link check (e.g. `lychee --offline` for relative links, and online for the absolute github.com and raw.githubusercontent.com links) over all changed docs and the wiki. For wiki pages, check that every `[x](Page)` target exists as `Page.md`.
4. **Facts:** for each command or flag that the wiki and the READMEs name, run `firestarter <cmd> --help` in a 3.1.0 install (the app checkout at `release/3.1.x`, `pip install -e .`) and confirm it. Also compare the chip counts against `chip_database.json`.
5. **Tests:**
   - fw: `pytest tests/` on a clean tree (commit first, because the `test_planted_*` tests need a clean tree).
   - app: `pytest tests/` on Python 3.11.
   - skill: `.claude/skills/devtest-triage/scripts/tests` and `eprom_ledger.py check`.
6. **PyPI render:** in the app, `python -m build --sdist` plus `twine check dist/*`. The long description renders, has no relative image or link, and the sdist no longer has CHANGELOG.md.
7. **Nothing publishes:**
   - Each PR targets `main`. `gh release list` in both sub-repos still shows `3.1.0b5` as the newest after the PRs are opened.
   - No push goes to `beta`.
