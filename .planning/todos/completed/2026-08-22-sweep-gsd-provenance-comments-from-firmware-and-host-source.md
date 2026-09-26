---
created: 2026-08-22T21:57:53Z
title: "Sweep GSD provenance comments from firmware and host source — delete the bookkeeping, condense the rationale (tracked as Backlog 999.34, ⭐ promote first into the next milestone)"
area: general
resolves_phase: 154
files:
  - firestarter/src/**, firestarter/include/**  (~345 hits / 94 files)
  - firestarter_app/firestarter/**, firestarter_app/tests/**  (~301 hits / 73 files)
  - firestarter/src/proms/eprom_params.cpp:61
  - firestarter/src/boards/uno_rurp_shield.cpp:109
  - firestarter_app/firestarter/database.py:580-630
  - firestarter_app/tests/test_dispatch_mirror.py
---

## Problem

> **Roadmap handle: Backlog Phase 999.34** (filed 2026-08-22), flagged ⭐ PROMOTE FIRST
> into the next milestone. Phase dir: `.planning/phases/999.34-sweep-gsd-provenance-comments/`.
> This todo is the full writeup — the ROADMAP entry deliberately defers to it.
> Sizing rationale (phase, not quick; big-bang beats incremental) lives in the ROADMAP entry.

GSD executors have been stamping planning provenance into the shipped source for
~150 phases. A survey on 2026-08-22 (branch `beta`) counted:

| Repo | Hits | Files |
|---|---|---|
| `firestarter/` (`*.cpp *.h *.c *.ino` under `src include lib test`) | ~345 | 94 |
| `firestarter_app/` (`*.py` under `firestarter tests tools`) | ~301 | 73 |
| **total** | **~646** | **167** |

Survey regex: a comment marker (`//`, `/*`, `*`, `#`) followed by
`(Task|Phase|Plan|P<NNN>|Req|REQ-|CAP-0|D-<N>|WR-<N>|LOOP-<N>|<NNN>-CONTEXT)`.
Re-run it before starting — these counts are a `beta`-tip snapshot, and the
regex is deliberately wide, so triage every hit rather than trusting the class
split below to be exhaustive.

The comments split into three kinds, and they must NOT be treated alike:

1. **Pure bookkeeping — delete.** Provenance with no reader value:
   `// Phase 151 (LOCK-02): CMD_LOCK_STATUS operation for the 0x06 AMD ...`,
   `/* Phase 44 — host-tunable read-timing knobs (D-04 sweep params) */`,
   `// D-01 / D-02` trailing a mask OR. The phase number tells a future reader
   nothing the code doesn't; git blame already carries it.

2. **Tombstones — delete.** `// Phase 9: deleted the legacy SERIAL_DEBUG
   infrastructure`, `// Phase 9: deleted the two legacy text-prefix log helper
   declarations`. These describe code that is not there. There are several in
   `boards/uno_rurp_shield.cpp` and `include/rurp_serial_utils.h` alone.

3. **Real rationale wearing a phase label — CONDENSE, never delete.** The
   decision ID is noise but the sentence after it is load-bearing:
   - `eprom_params.cpp:61` — `return NULL; /* D-05: fail closed, zero hardware
     side effects -- never &EPROM_PARAMS[0] */` → keep "fail closed; never fall
     back to entry 0 — it would drive the wrong chip's rails."
   - `uno_rurp_shield.cpp:109` — "the com_mode gate is critical" (explains why
     the override cannot emit unconditionally).
   - `database.py:580-630` — the Phase 121 D-12 / Phase 153 REVERSAL RECORD.
     ~50 lines explaining that D-12's *policy* was right and its *premise* was
     wrong. This is the single highest-value comment block in the repo; it must
     survive in condensed form or the reversal gets re-reversed.
   - `flash_5v_page.cpp:101` — `D-153-05: an erase-on-write block gated this way,
     inside a ...` (a trap description, not provenance).
   - `json_parser.c:92` — `D-05: page_size resets to 0 exactly like chip_id`
     (an invariant a future editor will otherwise break; cf. the open todo
     `phase-44-read-timing-knobs-missing-json-parse-reset.md`, which is exactly
     this class of bug).

## Solution

Mechanically cheap, but three real hazards make it a phase and not a `/gsd-fast`:

**Hazard 1 — host gates scan firmware source.** ~20 files under
`firestarter_app/tests/` read `firestarter/src` and `firestarter/include`
directly (`test_dispatch_mirror.py`, `test_json_key_parity.py`,
`test_check_no_log_in_sdp_window.py`, `test_sdp_bus_config_drift.py`,
`test_cap03_ack_layout_parity.py`, `test_revision_constants_parity.py`, …).
Some strip comments and *prove* they do — `test_check_no_log_in_sdp_window.py`
carries a dedicated "comment-not-a-call control" test. Others show no stripping
at all (`test_dispatch_mirror.py` has zero comment handling). A comment-only
sweep can therefore flip a gate in either direction: RED because a token
vanished from a comment the gate was matching, or **silently green** because a
gate that was only ever matching comment text now matches nothing. Before the
sweep, classify every firmware-source-scanning gate as
comment-stripping / comment-sensitive, and for each comment-sensitive one assert
it still fails on a planted violation afterwards. Per
`reference_firmware_renames_break_host_source_scanning_gates`, these gates
**fail open** — a green run is not evidence.

**Hazard 2 — `file:LINE` citations in `.planning/` go stale. DECIDED
2026-08-22 (operator): repair them. Not "accept staleness for archives" — the
whole set gets rewritten.** Phase records, CONTEXT docs and claim gates cite
source by line number, and deleting comment lines shifts nearly every line
number in the 167 touched files.

Measured size of the repair (survey 2026-08-22, branch `beta`):

| Metric | Count |
|---|---|
| `file:LINE` citations anywhere in `.planning/` | 12,753 |
| …that target one of the 167 touched source files | 10,054 |
| …**at or below** that file's first GSD comment (i.e. actually shift) | **6,939** |

Shifted citations by subtree: `phases/` 4,918 · `milestones/` 1,309 ·
`research/` 180 · `graphs/` 108 · `debug/` 99 · `quick/` 55 · `notes/` 54 ·
`PROJECT.md` 42.

Because the operator's call includes the archives, `milestones/`' 1,309
citations are in scope. That collides with
`reference_milestone_close_breaks_record_gates` (archived sections orphan
`lines=N`) — editing archived records can trip record gates that were green
only because nobody had touched those files since close. Budget for that.

**How the repair must run — one atomic transform, not a second pass.**
The remap is fully derivable, so it should be scripted, never hand-edited:

1. Do the comment sweep on a scratch copy and diff it to build, per file, an
   old-line → new-line map (deleted lines map to the surviving line that
   replaced them; condensed blocks map to their new first line).
2. Rewrite every `file:LINE` and `file:LINE-LINE` citation in `.planning/`
   through that map. **Ranges need both endpoints mapped**, and a range that
   spans a deleted block shrinks — the map must handle that, not just add a
   constant offset.
3. Commit source edit + citation rewrite **together**. If they land as separate
   commits, the intermediate tree carries 6,939 wrong citations, and any claim
   gate running in between either goes red or — worse — passes while pointing at
   the wrong lines.

**Oracle (there is no existing gate for this).** Nothing in the repo verifies
citation accuracy today: the `check-claims.py` / `check_record_corrections.py`
scripts under `phases/130`, `146`, `149`, `152` are phase-scoped claim gates,
not a global citation checker. So the repair must bring its own, and the
round-trip form is exact and needs zero judgment:

> for every citation, the source text at the cited line **before** the sweep
> must equal the source text at the remapped line **after** it.

Run it over all 6,939. Any mismatch is a map bug. This also catches the
citations that point *at a comment line being deleted* — those cannot round-trip
and must be retargeted by hand to the code the comment described (not silently
dropped). Expect that subset to be the only manual work in the repair, and
treat its size as an unknown until the diff exists.

Neighbours: `reference_record_gate_slow_on_state_md_long_line` (the record gate
needs 300s; `rc=124` reads like a RED) and
`reference_check_permitted_claims_here_resolves_wrong_phase_dir` (`_HERE`
resolves to the checker's own dir, so a mis-sited checker scans nothing and
exits 0 — do not let the citation checker fail open the same way).

**Hazard 3 — the firmware size watermark.** Comments cost zero bytes, so the
`uno` build must come out **byte-identical**. That is the sweep's strongest
oracle: diff the `.elf`/size output before and after. Any delta means a comment
edit changed code (a stray `#if` boundary, a swallowed line continuation in
`json_parser.c`) and must be reverted. Per
`reference_v131_firmware_native_gate_gotchas` there is 0 headroom at watermark
1166, so a silent regrowth here would be caught late and blamed elsewhere.

Sequencing: firmware and host are separate sub-repo commits on one milestone
branch (see `project_v18_phase_execution_mechanics`), and
`test_flash_path_record_sync` asserts whole-repo porcelain — commit before
running the suite.

Scope note: `messages.h` is codegen-generated
(`reference_firmware_messages_h_is_codegen_generated`) and
`chip_database.json` is generated — comments in generated artifacts must be
fixed at the generator/`messages.toml` and never in the output.
