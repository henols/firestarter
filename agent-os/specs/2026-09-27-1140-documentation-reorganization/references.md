# References for Documentation Reorganization

## Prior spec shape

- **Location:** `agent-os/specs/2026-09-25-2218-3-1-x-release-readiness/`
- **Relevance:** the house four-file spec shape. It also wrote the CHANGELOG and the three wiki
  pages that this spec now reorganizes.

## The wiki before the change

- **Location:** `firestarter.wiki` (remote `henols/firestarter.wiki`, branch `master`), commit
  `6ef34f4`.
- **Relevance:** the 15 pages that are merged, rewritten or deleted.
- **Read a page as it was:** `git -C /workspaces/firestarter.wiki show 6ef34f4:<Page>.md`

## The validated-chip ledger generator

- **Location:** `.claude/skills/devtest-triage/scripts/eprom_ledger.py`
- **Relevance:** `VALIDATED-EPROMS.md` is generated. Change `render()`, never the `.md` file.
- **Key patterns:** `write` regenerates, `check` compares the file with a fresh render.

## Release workflow guards

- `firestarter_app/.github/workflows/release.yml` — `paths-ignore: '**.md', 'images/**'`, and a
  tag-exists check that skips the release when the version on `main` is already tagged.
- `firestarter_fw/.github/workflows/build.yml` — the same `paths-ignore` and tag check.
- `beta-release.yml` / `beta-build.yml` — no path filter. Each push to `beta` publishes.
