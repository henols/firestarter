---
phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end
plan: 01
subsystem: catalog
tags: [toml, codegen, messages, protocol, serial, firmware, arduino]

# Dependency graph
requires:
  - phase: 07-convert-error-warn-info-call-sites
    provides: codegen infrastructure (messages.toml schema, codegen.py emitters, sync_to_subrepos.sh, CI drift gates)
provides:
  - MSG_DATA_VPP_VOLTAGE (0xE4), MSG_DATA_VPE_VOLTAGE (0xE5), MSG_DATA_CHUNK (0xE6), MSG_DEBUG (0xF0) in catalog
  - Reshaped MSG_OK_REV (0x04), MSG_OK_CFG (0x05), MSG_OK_FW_HANDSHAKE (0x06) per P-02/P-03/P-04
  - [debug] section with 41 DBG_* sub-ID entries (0x00..0x28) for Phase 8 debug sweep (Plan 07)
  - codegen.py extended to emit DBG_* #defines + DEBUG_CATALOG dict
  - bytes param type support in catalog + codegen (MSG_DATA_CHUNK / MSG_DEBUG sub-payload)
  - Regenerated messages.h (firestarter) + messages.py (firestarter_app) committed
  - sync_to_subrepos.sh extended to also regenerate generated artifacts
  - /tmp/ph8-debug-audit.txt: debug string -> DBG_* name -> sub_id lookup table for Plan 07
affects:
  - 08-02 (wire-format len widening uses MSG_DATA_CHUNK)
  - 08-03 (host parser uses new catalog shapes for OK_REV/CFG/FW_HANDSHAKE)
  - 08-04..08-06 (call-site conversions use new MSG_* and LOG_*_ID_* macros)
  - 08-07 (debug sweep uses DBG_* from [debug] section)

# Tech tracking
tech-stack:
  added:
    - bytes param type in catalog (raw payload, no printf specifier, variable-length)
  patterns:
    - "bytes param type: raw payload params excluded from Rule 9 format-specifier count check"
    - "DBG_PATTERN = r'^DBG_[A-Z][A-Z0-9_]*$' for [debug] section name validation"
    - "[debug] section in messages.toml: same shape as [[messages]] but no severity/wire_format (both implicit)"
    - "DEBUG_CATALOG dict in messages.py mirrors CATALOG but uses severity=SEVERITY_DATA implicitly"
    - "sync_to_subrepos.sh now owns full generation cycle: copy TOML+codegen, then regen messages.h + messages.py"

key-files:
  created:
    - "/tmp/ph8-debug-audit.txt (debug string -> DBG_* mapping table for Plan 07; not committed)"
  modified:
    - "tools/catalog/messages.toml (4 new [[messages]] entries + 41 [[debug.messages]] entries + 3 reshaped OK entries)"
    - "tools/catalog/codegen.py (bytes type, DBG_PATTERN, [debug] validation, DBG_* emit, DEBUG_CATALOG emit)"
    - "tools/catalog/sync_to_subrepos.sh (extended to regenerate messages.h + messages.py)"
    - "firestarter/include/messages.h (regenerated: +4 MSG_* defines + 41 DBG_* defines)"
    - "firestarter_app/firestarter/messages.py (regenerated: +4 MSG_* constants + 41 DBG_* + DEBUG_CATALOG dict)"
    - "firestarter/tools/catalog/messages.toml (synced copy)"
    - "firestarter/tools/catalog/codegen.py (synced copy)"
    - "firestarter_app/tools/catalog/messages.toml (synced copy)"
    - "firestarter_app/tools/catalog/codegen.py (synced copy)"

key-decisions:
  - "Added 'bytes' to VALID_PARAM_TYPES (variable-length raw payload; excluded from Rule 9 format specifier count)"
  - "Rule 9 now counts only non-bytes params against printf specifier count (bytes are raw payload, not printf-rendered)"
  - "MSG_OK_REV format changed to 'Rev%u (eff: %u)' to satisfy Rule 9 spec-count == param-count (2 params, 2 specifiers)"
  - "MSG_OK_CFG format changed to 'R1: %lu, R2: %lu, Cfg: %u' (3 params, 3 specifiers; host renders override semantics)"
  - "MSG_OK_FW_HANDSHAKE format changed to 'HW: %u, Cmd: 0x%02x, FW: %s' (3 params: u8 hw, u8 cmd, ascii_str fw_version)"
  - "MSG_DATA_VPP/VPE_VOLTAGE use 4 u16 params (millivolts pre-split into integer and decimal parts) matching existing WARN_VPP_LOW/HIGH pattern"
  - "MSG_OK_FW_VERSION params kept as [] (Rule 8 enforces empty params for wire_format=text; LFW-05 bootstrap preserved)"
  - "41 unique debug strings found across 43 call-sites; CONTEXT.md B-01 count of 34 was stale"
  - "sync_to_subrepos.sh extended to also run codegen (previously only copied TOML + codegen.py)"

patterns-established:
  - "bytes type pattern: declare as params entry, excluded from format specifier count, rendered as raw buffer host-side"
  - "[debug] section validation: mirrors main-catalog rules D1-D8 with DBG_PATTERN prefix check"
  - "DBG_* sub_id namespace: 0x00..0xFF u8, separate from main MSG_* namespace, dense allocation from 0x00"

requirements-completed: [LMIG-03]

# Metrics
duration: 25min
completed: 2026-05-18
---

# Phase 8 Plan 01: Catalog Additions Summary

**Extended messages.toml with 4 new DATA-band IDs (VPP/VPE voltages, DATA_CHUNK streaming wrapper, MSG_DEBUG channel), reshaped 3 OK entries per P-02..P-04, added [debug] section with 41 DBG_* sub-IDs, and extended codegen.py to emit DBG_* + DEBUG_CATALOG**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-05-18T18:50:27Z
- **Completed:** 2026-05-18T18:59:47Z
- **Tasks:** 3
- **Files modified:** 9 (meta-repo: 3, firestarter sub-repo: 3, firestarter_app sub-repo: 3)

## Accomplishments

- messages.toml now declares all Phase 8 protocol IDs: VPP_VOLTAGE (0xE4), VPE_VOLTAGE (0xE5), DATA_CHUNK (0xE6), MSG_DEBUG (0xF0), plus reshaped OK_REV/OK_CFG/FW_HANDSHAKE shapes per P-02..P-04
- codegen.py extended with `bytes` param type, [debug] section validation (Rules D1-D8), DBG_* #define emission, and DEBUG_CATALOG dict emission
- Both sub-repos carry regenerated artifacts: messages.h has 41 DBG_* defines + 4 new MSG_* defines; messages.py has DEBUG_CATALOG dict with 41 entries
- sync_to_subrepos.sh now runs the full generation cycle (copy + regen + verify)
- LCAT-05 idempotence preserved: second run of sync_to_subrepos.sh produces zero git diff in both sub-repos
- /tmp/ph8-debug-audit.txt contains the full debug string -> DBG_* name -> sub_id mapping table for Plan 07

## Debug Audit Summary

- **Total call-sites:** 43 (firestarter/src/, excluding logging infrastructure)
- **Unique strings:** 41 (allocated sub_id 0x00..0x28)
- **CONTEXT.md cited count:** 34 (stale — actual count is 41 unique strings across 43 sites)
- **Shared strings:** "Check chip ID" (eprom.cpp:84 + :305), "Checking VPP voltage %u mV" (eprom.cpp:230 + flash_intel.cpp:39)

## Task Commits

1. **Task 1: Audit + extend messages.toml** - `b87f034` (feat)
2. **Task 2: Extend codegen.py** - `e92bad2` (feat)
3. **Task 3: Sync sub-repos + extend sync_to_subrepos.sh** - `0a0d59d` (chore)

**Sub-repo commits:**
- firestarter: `606eeda` (chore — messages.h + catalog sync)
- firestarter_app: `b3f0b1b` (chore — messages.py + catalog sync)

## Files Created/Modified

- `/workspaces/firestarter_prom/tools/catalog/messages.toml` — 4 new [[messages]] entries + [debug] section with 41 [[debug.messages]] + reshaped 0x04/0x05/0x06 + format update for 0x03
- `/workspaces/firestarter_prom/tools/catalog/codegen.py` — bytes type, DBG_PATTERN, [debug] validation (Rules D1-D8), DBG_* emit in emit_cpp_header, DEBUG_CATALOG emit in emit_python
- `/workspaces/firestarter_prom/tools/catalog/sync_to_subrepos.sh` — extended to regenerate messages.h + messages.py after copying TOML/codegen
- `/workspaces/firestarter_prom/firestarter/include/messages.h` — regenerated with 41 DBG_* defines + 4 new MSG_* defines (75 total messages)
- `/workspaces/firestarter_prom/firestarter_app/firestarter/messages.py` — regenerated with 41 DBG_* constants + DEBUG_CATALOG dict (75 total messages)
- `/tmp/ph8-debug-audit.txt` — debug string -> DBG_* name -> sub_id lookup map for Plan 07 (not committed)

## Decisions Made

1. **bytes param type added to VALID_PARAM_TYPES** — MSG_DATA_CHUNK needs a raw payload param that has no printf specifier equivalent. Added as variable-length (PARAM_TYPE_BYTES = None) and excluded from Rule 9 format-spec count check.

2. **Rule 9 updated to exclude bytes params** — Format specifier count is compared against non-bytes param count only. This allows MSG_DATA_CHUNK (format: `"<data chunk>"`, params: [bytes]) and MSG_DEBUG (format: `"[debug:%u]"`, params: [u8, bytes]) to pass validation.

3. **MSG_OK_REV format: "Rev%u (eff: %u)"** — 2 params (physical, effective) need 2 format specifiers. Plan suggested single-branch format; validator requires specifier count match. Chose inclusive format; host renders override semantics on top.

4. **MSG_OK_CFG format: "R1: %lu, R2: %lu, Cfg: %u"** — 3 params (r1, r2, override) need 3 specifiers. Override rendered as override byte value; host decodes 0xFF=no-override sentinel.

5. **MSG_OK_FW_VERSION params kept as []** — Rule 8 enforces empty params for wire_format=text entries. The plan's "ascii_str for documentation" intent cannot be expressed without breaking the validator. LFW-05 bootstrap exemption preserved.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added 'bytes' param type to codegen.py**
- **Found during:** Task 2 (extending codegen.py)
- **Issue:** messages.toml uses `bytes` type for MSG_DATA_CHUNK and MSG_DEBUG, but codegen.py's VALID_PARAM_TYPES did not include 'bytes', causing CatalogError on validate_catalog
- **Fix:** Added `"bytes"` to VALID_PARAM_TYPES with None wire-byte count (variable-length), added to DEFAULT_RENDER_BY_TYPE as "hex", updated Rule 9 to exclude bytes from format specifier count
- **Files modified:** tools/catalog/codegen.py
- **Verification:** `python tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` exits 0
- **Committed in:** e92bad2

**2. [Rule 1 - Bug] MSG_OK_REV and MSG_OK_CFG format strings adjusted for Rule 9 compliance**
- **Found during:** Task 1 (writing messages.toml entries)
- **Issue:** Plan specified single-branch format strings ("Rev{0}", "R1: {0}, R2: {1}" in Python syntax) with fewer specifiers than params. The validator's Rule 9 enforces specifier count == param count.
- **Fix:** Added specifiers for all params: "Rev%u (eff: %u)" for MSG_OK_REV, "R1: %lu, R2: %lu, Cfg: %u" for MSG_OK_CFG. Host renders override semantics independently.
- **Files modified:** tools/catalog/messages.toml
- **Committed in:** b87f034

**3. [Rule 2 - Missing] sync_to_subrepos.sh did not regenerate messages.h/messages.py**
- **Found during:** Task 3 (examining sync script)
- **Issue:** The script only copied messages.toml + codegen.py but did not run codegen to regenerate the generated artifacts. The plan's Task 3 action requires regeneration as part of the sync.
- **Fix:** Extended sync_to_subrepos.sh to run codegen for both sub-repos after copying the TOML/codegen files
- **Files modified:** tools/catalog/sync_to_subrepos.sh
- **Committed in:** 0a0d59d

---

**Total deviations:** 3 auto-fixed (1 Rule 2 missing critical, 1 Rule 1 bug, 1 Rule 2 missing)
**Impact on plan:** All auto-fixes required for validator correctness and sync completeness. No scope creep.

## Issues Encountered

None — all blockers resolved inline as deviations.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 02 (wire-format len u8→u16 widening) can begin: catalog declares MSG_DATA_CHUNK with bytes payload
- Plan 03 (host parser reshape for OK_REV/CFG/FW_HANDSHAKE) can begin: catalog shapes are locked
- Plan 04-05 (call-site conversions) can begin: all MSG_* and existing IDs are in catalog
- Plan 07 (debug sweep) has its DBG_* lookup table in /tmp/ph8-debug-audit.txt and in messages.h/messages.py
- No firmware call-sites changed — Wave 1 is infrastructure-only per Phase 7 D-03 pattern

---
*Phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end*
*Completed: 2026-05-18*

## Self-Check: PASSED

### Files verified:
- [x] tools/catalog/messages.toml exists and has [debug] section
- [x] tools/catalog/codegen.py has DBG_PATTERN and DEBUG_CATALOG
- [x] tools/catalog/sync_to_subrepos.sh regenerates artifacts
- [x] firestarter/include/messages.h has DBG_* defines
- [x] firestarter_app/firestarter/messages.py has DEBUG_CATALOG
- [x] /tmp/ph8-debug-audit.txt exists

### Commits verified:
- [x] b87f034 — feat(catalog): add Phase 8 IDs
- [x] e92bad2 — feat(codegen): emit DBG_* defines + DEBUG_CATALOG
- [x] 0a0d59d — chore(catalog): extend sync_to_subrepos.sh
- [x] 606eeda — chore(catalog) in firestarter sub-repo
- [x] b3f0b1b — chore(catalog) in firestarter_app sub-repo
