# References for 3.1.x Release Readiness

## Retired parents

Six documents from the deleted `.planning/` tree are the direct ancestors of this spec. GSD was
uninstalled and `.planning/` deleted on the `experiment/agent-os` branch.

**Read them at meta commit `5b9e41ab`** — the tip of `origin/beta` on 2026-09-25, the last published
commit that still carries the whole `.planning/` tree. Cite that SHA and not a branch name: once the
GSD-uninstall branch merges, `origin/beta:.planning/...` stops resolving, while `5b9e41ab` stays
reachable as an ancestor of the merge. All six were verified readable at that commit.

### The 3.0.x release-gate analysis
- **Location:** `.planning/notes/stable-3.0.0-release-gate.md` (140 lines), added `47eb542f`
  2026-09-20.
- **Read it with:** `git -C /workspaces show '5b9e41ab:.planning/notes/stable-3.0.0-release-gate.md'`
- **Relevance:** the origin of the `/releases/latest` trap analysis and of the feature-version rule
  this spec implements.
- **Key patterns:** each figure carries the command that produced it. Keep that discipline.
- **Obsolete in it:** every `3.0.0` version number; the divergence figures 1060 / 617 / 2055; the
  claim that a firmware push to `main` publishes with no dry run (inverted — see `shape.md`); and
  the `2.0.10` backport as the central mitigation (reversed by D-3).

### The promotion seed
- **Location:** `.planning/seeds/stable-3.0.0-promotion.md` (55 lines).
- **Read it with:** `git -C /workspaces show '5b9e41ab:.planning/seeds/stable-3.0.0-promotion.md'`
- **Relevance:** the scope list that becomes `RELEASING.md` — app before firmware, the
  Breaking-Changes preamble, the stable-install page, the CHANGELOG decision.
- **Obsolete in it:** the `trigger_condition` / `status: dormant` front matter is GSD seed
  machinery with no runtime. Those conditions become Phase 0 preconditions in the runbook.

### The pre-flash guard todo
- **Location:** `.planning/todos/pending/2026-09-20-preflight-firmware-version-compat-guard.md`
  (105 lines), added `9f9b4009`.
- **Read it with:** `git -C /workspaces show '5b9e41ab:.planning/todos/pending/2026-09-20-preflight-firmware-version-compat-guard.md'`
- **Relevance:** the rule and the truth table this spec implements, unchanged.
- **Obsolete in it:** "hand-roll the parser, do not add `packaging`" was scoped to the 2.0.x
  branch. The current app depends on `packaging` already and `_compare_versions` uses `Version`.

### The two CI defects the promotion trips over
- **Location:** `.planning/todos/pending/2026-09-13-release-yml-autocommit-vs-ruleset.md` (66
  lines) and `.planning/todos/pending/2026-09-13-publish-yml-release-published-never-fires.md`
  (103 lines).
- **Read them with:** `git -C /workspaces show '5b9e41ab:.planning/todos/pending/2026-09-13-release-yml-autocommit-vs-ruleset.md'`
- **Relevance:** these are the two blockers `RELEASING.md` documents. The first predicted the
  `GH013` failure that run `34784468070` then produced; the second explains why a bot-created
  release does not cascade to PyPI.
- **Key patterns:** the second document self-corrects a measurement taken with `gh run list
  --limit 10`, which truncated the one counterexample. Carry only the corrected diagnosis.

### The `--set-version` defect
- **Location:** `.planning/todos/pending/2026-09-24-update-version-set-version-ignores-beta-mode.md`
  (46 lines).
- **Read it with:** `git -C /workspaces show '5b9e41ab:.planning/todos/pending/2026-09-24-update-version-set-version-ignores-beta-mode.md'`
- **Relevance:** the same defect as "`3.1.0` is unreachable by the automation", from the other
  side. It is why the cleanest unblocking option needs a code change first.

## Similar implementations

### JP5 gate — the pure-gate shape to copy
- **Location:** `firestarter_app/firestarter/jp5_gate.py`
- **Relevance:** the canonical `is_*` / `require_*` / module-level refusal-constant module.
- **Key patterns:** the module docstring names the polarity, the worst case in each direction and
  the operator escape. `fw_release_gate.py` must do the same, including its one documented
  fail-open edge (D-9).

### Hardware-revision gate — a gate that runs after the ack
- **Location:** `firestarter_app/firestarter/hw_revision_gate.py`, and the spec at
  `agent-os/specs/2026-09-25-2040-hw-rev-gate-pin21/`.
- **Relevance:** the precedent for D-8. That gate also deviates from `host/pre-serial-gates` by
  running after a wire round-trip, because its evidence does not exist before one. It records the
  deviation rather than hiding it. Do the same.

### The three checks that are not this check
- **Location:** `firestarter_app/firestarter/firmware.py` `_compare_versions`;
  `firestarter_app/firestarter/serial_comm.py` `_validate_firmware_version` and
  `_is_version_sufficient`; `firestarter_app/firestarter/cli_handlers.py`
  `_maybe_auto_route_to_pre`.
- **Relevance:** all three look like a compatibility gate and none is one. `_compare_versions`
  asks whether the board's firmware is up to date. `_validate_firmware_version` is a hardcoded
  floor at connect time, waived during `fw`. `_maybe_auto_route_to_pre` flips a default and refuses
  nothing. None is modified by this spec.
- **Key patterns:** `_is_version_sufficient` does `int()` over a dot-split, so `"3.1.0b2"` is
  unparseable to it. Reusing it would invert the required `3.1.0b2` / `3.1.0b5` → allow row.

### Firmware tombstones
- **Location:** `firestarter_fw/include/firestarter.h` (ordinals 4 and 6, flag `0x08`) and the
  dispatch default arm in `firestarter_fw/src/firestarter.cpp`.
- **Relevance:** the evidence behind D-3. The default arm answers `MSG_ERR_UNKNOWN_CMD`, so a stale
  host's retired-ordinal frames fail loudly. Read, not changed.

### Tests
- **Location:** `firestarter_app/tests/test_firmware_install.py` (the
  `monkeypatch.setattr(fm, ...)` pattern and `TestManageFirmwareUpdate`).
- **Relevance:** where the service-layer refusal tests go.
- **Watch out:** `test_fw_version_guard.py`, `test_fwguard.py` and `test_fw_update_path_gate.py`
  are already taken by the connect-time floor and the update-deadlock regression. Do not reuse
  those names.

### The generated ledger
- **Location:** `VALIDATED-EPROMS.md`, generated by
  `.claude/skills/devtest-triage/scripts/eprom_ledger.py`.
- **Relevance:** `render()` emits the H1, the tables, then `## Notes`. There is no preamble slot,
  and prose above the tables is destroyed by the next `add`. `read_notes()` preserves the `## Notes`
  body verbatim — it is the only hand-editable surface in the file.
