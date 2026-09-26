# Phase 7: Convert ERROR + WARN + INFO Call-Sites - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-18
**Phase:** 7-Convert ERROR + WARN + INFO Call-Sites
**Areas discussed:** response_msg dispatcher removal depth, Macro ergonomics (LOG_ERROR_ID_* / LOG_WARN_ID_*), Catalog drift policy, Cleanup scope (dev_tools.cpp + commented-out logs)

---

## Gray-area selection

Operator selected three of four presented areas (multiSelect):

| Area | Selected |
|------|----------|
| response_msg dispatcher removal depth | ✓ |
| Macro ergonomics — add LOG_ERROR_ID_* / LOG_WARN_ID_*? | ✓ |
| Commit cadence / batching | (skipped — Claude's discretion) |
| Catalog drift + cleanup scope | ✓ |

---

## Area 1 — response_msg dispatcher removal depth

| Option | Description | Selected |
|--------|-------------|----------|
| Drop log_* in _check_response; keep response_code flow | Each populate site emits via LOG_ID_* AND sets response_code. _check_response keeps state-machine control flow but drops the four log_*(handle->response_msg) calls. response_msg becomes vestigial (Phase 9 deletes). | ✓ |
| Keep dispatcher intact; populate site emits then sets response_code | Populate site does both rurp_log_id() AND firestarter_*_response_format(). _check_response unchanged. Net effect: same line logged twice. | |
| Stronger: pull response_code into populate macros so call-sites are 1-line | Define LOG_ERROR_ID_* macro that emits + sets response_code in one call. | |

**User's choice:** Drop log_* in _check_response; keep response_code flow (recommended).
**Notes:** Phase 6 RESEARCH line 204 already locked this boundary — the gray area was the cleanup depth, not whether to refactor at all. Note that the OK + DATA branches of `_check_response` stay intact for Phase 8 (state-machine acks). Only ERROR + WARN log_* lines are removed in Phase 7.

---

## Area 2 — Macro ergonomics

| Option | Description | Selected |
|--------|-------------|----------|
| Add LOG_ERROR_ID_* AND LOG_WARN_ID_* mirroring LOG_INFO_ID_* | Symmetric surface: LOG_ERROR_ID, _U8/U16/U24/U32/BYTES + same for WARN. Unconditional (no FLAG_VERBOSE gate). Thin aliases over LOG_ID_*, zero runtime cost, ~25 lines added to logging_id.h. | ✓ |
| Only add LOG_WARN_ID_*; ERROR uses raw LOG_ID_* | Asymmetric; ERROR call-sites read as LOG_ID_U16(MSG_ERR_FOO, val). | |
| No new wrappers; ERROR + WARN use raw LOG_ID_* | Smallest surface; severity inferred from MSG_* prefix only. | |

**User's choice:** Add LOG_ERROR_ID_* AND LOG_WARN_ID_* mirroring LOG_INFO_ID_* (recommended).
**Notes:** Symmetric readability win is the goal — `LOG_ERROR_ID_U16(MSG_ERR_FOO, val)` next to `LOG_INFO_ID_U16(MSG_INFO_BAR, val)` makes severity obvious from the macro name. Implementation is one-line aliases; the win is exclusively at the call-site reading layer.

---

## Area 3 — Catalog drift policy

| Option | Description | Selected |
|--------|-------------|----------|
| Locked catalog — mismatch is a bug, fail-fast | Phase 6 RESEARCH claims 55 catalog entries cover every active call-site. Mismatch = stop conversion, fix catalog as separate commit (chore(catalog): add MSG_<NEW> — Phase 6 gap fix), re-sync, resume. | ✓ |
| Fluid catalog — add IDs as discovered | Phase 7 freely adds new catalog entries as call-sites are converted. | |
| Locked-with-exception — fail-fast except for format-string drift | Locked, but format-string drift (e.g. punctuation changes) makes the call-site adapt to the catalog. | (partial — see notes) |

**User's choice:** Locked catalog — mismatch is a bug, fail-fast (recommended).
**Notes:** The locked-with-exception sub-case (format-string drift) is folded INTO the locked policy as a sub-rule: when the current code's format string differs from the catalog (punctuation, casing, ordering), the call-site adapts to the catalog. The catalog is canonical. Don't fork the catalog to match historical code. This makes the policy "locked, with the catalog as source of truth — drift is fixed at the consumer, not the producer."

---

## Area 4 — Cleanup scope (multiSelect)

| Option | Description | Selected |
|--------|-------------|----------|
| Convert dev_tools.cpp's 6 INFO logs | dev_tools.cpp links into the firmware binary → same flash pressure, would fail SC#1 grep if skipped. | ✓ |
| Delete operation_utils.cpp's ~14 commented-out // log_* lines | Stale debug breadcrumbs referencing legacy macros; will become misleading after Phase 9 reorganizes logging.h. | ✓ |
| Leave dev_tools.cpp alone | Would require a documented exception in SC#1's grep. | |
| Leave commented-out lines alone | Diff stays strictly to conversions; cleanup deferred. | |

**User's choice:** Convert dev_tools.cpp + delete commented-out breadcrumbs.
**Notes:** Operator's mental model: anything in the binary counts toward flash and toward the SC#1 grep — no carve-outs. Commented-out lines are technical debt that decays into misinformation post-Phase-9; better deleted while the file is already being touched.

---

## Claude's Discretion

- **Commit cadence / batching strategy** — operator did not lock; planner picks. Recommended in CONTEXT.md §Claude's Discretion: macro-additions commit first (infrastructure), then per-PROM-module commits for populate-site conversions, then per-file commits for direct-log conversions (~12 commits total).
- **Multi-param composer macros** for catalog entries with 3+ params — planner picks between purpose-built composers and raw `LOG_ID_BYTES`.
- **`LOG_ERROR_RESPONSE(MSG, ...)` 1-call packaging** at populate sites — planner may revisit; recommended two-line form for now.
- **`log_error_format_buf(handle.response_msg, ...)` hybrid at firestarter.cpp:171** — planner converts to direct `LOG_ERROR_ID_U8` (no buffer, no response_code mutation).
- **`host_stubs.cpp` updates** for native test linkage post-conversion — researcher confirms.
- **Flash-savings target wording** — planner picks "measurable" threshold.
- **`_check_response` test coverage** — planner picks the gate (native dispatch suite vs Python integration).

## Deferred Ideas

None — discussion stayed strictly within Phase 7's locked scope. Operator did not surface any out-of-phase capabilities or new requirements. The "Deferred Ideas" section of CONTEXT.md contains only items deferred to LATER phases (response_msg buffer deletion → Phase 9, OK/INIT/MAIN/END conversion → Phase 8) — not scope-creep ideas from this discussion.
