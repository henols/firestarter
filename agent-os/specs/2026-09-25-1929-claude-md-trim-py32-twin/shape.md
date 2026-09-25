# CLAUDE.md Trim and PY32 Twin Retirement — Shaping Notes

## Scope

Trim `firestarter_fw/CLAUDE.md` and `firestarter_app/CLAUDE.md` in place. Keep only what the code
and CI config do not show and what is costly to get wrong. Replace text that a standard in
`agent-os/standards/` already holds with a one-line pointer to that standard.

Retire the PY32 flash-path twin. `platform/py32f071/FLASH-PATH-AND-PCB.md` copied five sections of
`.planning/milestones/v1.23-FLASH-PATH-DECISION.md` in the meta repo. Meta commit `1ea94a1e`
deleted that file, so the firmware copy becomes the only record. Its sync test goes.

Add a Standards section to the root `CLAUDE.md`.

## Decisions

- **D-1. Scope.** Trim in place. Do not merge the submodule files into the root. Claude Code loads a
  subdirectory CLAUDE.md only when it works in that subtree, and each submodule can be checked out
  on its own.
- **D-2. Branches.** Use the current branches: `v1.42-jumper-display` in fw and app,
  `experiment/agent-os` in meta. Advance the gitlinks in meta. Do not push.
- **D-3. PY32 doc.** `FLASH-PATH-AND-PCB.md` is authoritative. Delete
  `tests/test_flash_path_record_sync.py` and `tests/meta_presence.py`. Do not recover the
  parent-only sections (§1, §7–9). They are in meta history at `1ea94a1e^`.
- **D-4. Standards.** `testing/no-source-introspection`, `testing/standalone-checkout`,
  `protocol/duplicated-constants`, `protocol/retired-ordinals`, `protocol/message-catalog`.
- **D-5. Keep/drop rule.** Keep a line only if the code or CI config does not show it, and getting it
  wrong is costly: it publishes a release, damages a part, gives a false green, or edits a generated
  file. If a standard covers it, point to the standard.

## Context

- **Visuals:** None.
- **References:** `agent-os/standards/index.yml` (the target of the pointers);
  `agent-os/specs/2026-09-25-1503-info-jumper-table/` (the spec format).
- **Product alignment:** the mission's "fail closed" and "honest claims" rules. The kept safety
  invariants (12V hazards, fail-closed dispatch, UNVERIFIED status) are the ones that serve them.

## Standards Applied

- testing/no-source-introspection — the twin test scans text. The fw CLAUDE.md points here for the
  legacy `tests/` tree.
- testing/standalone-checkout — the twin test reads the meta repo, and it skips in CI.
- protocol/duplicated-constants — replaces the constants tables in both CLAUDE.md files.
- protocol/retired-ordinals — replaces the reserved-ordinal and flag-`0x08` notes.
- protocol/message-catalog — replaces the `messages.h` codegen note.
