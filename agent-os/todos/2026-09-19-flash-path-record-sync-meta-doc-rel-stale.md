---
created: 2026-09-19T00:00:00Z
title: test_flash_path_record_sync.py's _META_DOC_REL points at a path the .planning layout reorganisation moved — 17 local failures, invisible to CI
area: firmware test suite
files:
  - firestarter_fw/tests/test_flash_path_record_sync.py (:77 _META_DOC_REL)
  - firestarter_fw/tests/meta_presence.py (:95 requires_meta, :84 META_PRESENT)
  - firestarter_fw/include/firestarter.h (:181-184, stale citation to a deleted host test)
  - firestarter_fw/tests/meta_presence.py (:19, :70, stale citation to a deleted host test)
---

## Problem

`firestarter_fw/tests/test_flash_path_record_sync.py:77` defines

```python
_META_DOC_REL = "v1.23-FLASH-PATH-DECISION.md"
```

resolved under `META_ROOT/.planning/` by the module's own `meta_path()` helper. The file now lives
at `/workspaces/.planning/milestones/v1.23-FLASH-PATH-DECISION.md` — the `.planning` layout
reorganisation moved it into `milestones/` and this scan path was never updated to match. Every leg
that reads the meta copy of the flash-path decision record fails with a `MissingScanTargetError` in
any checkout where the meta repository is present.

## Reproduction

```bash
cd /workspaces/firestarter_fw
python3 -m pytest tests/ -o addopts="" -q
# -> 17 failed, 284 passed (or higher, depending on suite growth since) in this devcontainer
```

## Why CI never sees this

`tests/meta_presence.py:84` computes `META_PRESENT: bool = META_MARKER.exists()`, and every affected
leg in `test_flash_path_record_sync.py` carries the `requires_meta` marker
(`tests/meta_presence.py:95`: `requires_meta = pytest.mark.skipif(not META_PRESENT, reason=...)`).
CI checks out `firestarter_fw` standalone — no parent `.git` — so `META_PRESENT` is `False` and all
17 legs **skip** rather than fail. In `/workspaces`, the meta repository's `.git` is present, so
`META_PRESENT` is `True` and the same legs run for real, hit the stale path, and fail closed by
design (the module's own docstring calls this the "hard-failure half of the split" — a present meta
repo with a broken scan target must FAIL, never silently skip).

## Workaround, confirmed working, used throughout Phase 201's own verify blocks

```bash
cd /workspaces/firestarter_fw
mkdir -p /tmp/no-meta
FIRESTARTER_META_ROOT=/tmp/no-meta python3 -m pytest tests/ -o addopts="" -q
# -> 269 passed, 32 skipped in ~13-15s (pre-Phase-201 baseline; higher after Phase 201's own new legs)
```

`FIRESTARTER_META_ROOT` must be set in the **child process** environment — it binds at import time
(`tests/meta_presence.py:79`), so a post-import monkeypatch does not work. Setting it to a directory
with no `.git` reproduces CI's meta-absent condition exactly, and `META_PRESENT` resolves `False`
identically to a standalone-checkout CI run.

## Disposition

**Not repaired here.** The repair belongs with the `.planning` layout change that moved the file
(a meta-repository change), not with a bench-gated dual-repo lockstep phase whose commit pairing
between `firestarter_fw` and the meta repository is already load-bearing (Phase 201 threat model
T-201-05-03 and sibling plans' verify legs both depend on precise, minimal per-commit diffs). Fixing
`_META_DOC_REL` here would add an unrelated firmware commit into that lockstep.

**Fix, when picked up:** update `_META_DOC_REL` in
`firestarter_fw/tests/test_flash_path_record_sync.py:77` to
`"milestones/v1.23-FLASH-PATH-DECISION.md"` (or wherever the file lives by the time this is picked
up — re-verify the live path first), then confirm
`FIRESTARTER_META_ROOT=/workspaces python3 -m pytest tests/test_flash_path_record_sync.py -o addopts="" -q`
goes from failing to passing with the meta repository genuinely present.

## Two more stale in-repo citations found while checking this (same root cause class: a deleted or
moved target, never updated)

Neither of the following affects test behaviour — both are prose citations in comments, not scan
targets — but both are wrong today and are recorded here so they are fixed in the same pass as the
`_META_DOC_REL` repair rather than rediscovered separately:

1. `firestarter_fw/include/firestarter.h:181-184` cites
   `firestarter_app/tests/test_revision_constants_parity.py` as the gate that bidirectionally pins
   the largest `ctrl_flags` value at `0x100`. That file does not exist —
   `ls firestarter_app/tests/test_revision_constants_parity.py` reports "No such file or directory".
   It was deleted by operator ruling `088d2b7` (the host-side source-scanning gate ban).
2. `firestarter_fw/tests/meta_presence.py:19` and `:70` both cite
   `firestarter_app/tests/fw_presence.py` as the sibling module whose "two parents up" arithmetic
   this module's docstring contrasts itself against. That file also does not exist —
   `ls firestarter_app/tests/fw_presence.py` reports "No such file or directory" — deleted by the
   same operator ruling.

Both citations describe real, still-correct reasoning (the parity invariant firestarter.h's comment
describes, and the parent-vs-sibling arithmetic meta_presence.py's docstring describes); only the
named file each points at is gone. Whoever repairs `_META_DOC_REL` should either point these two
citations at whatever gate now carries the same invariant (if one exists post-088d2b7) or rephrase
them to state the invariant without naming a file that no longer resolves.
