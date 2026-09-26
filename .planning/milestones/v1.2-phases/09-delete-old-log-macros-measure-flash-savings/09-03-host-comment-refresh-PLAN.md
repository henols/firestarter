---
phase: 09-delete-old-log-macros-measure-flash-savings
plan: 03
type: execute
wave: 2
depends_on: []
files_modified:
  - firestarter_app/firestarter/serial_comm.py
autonomous: true
requirements:
  - LMIG-04
requirements_addressed:
  - LMIG-04
tags:
  - logging
  - host
  - comment-only
user_setup: []
must_haves:
  truths:
    - "The host-side comment block at serial_comm.py:752-755 no longer contains the phrase \"until then\" (the framing assumed Phase 9 had not yet shipped)"
    - "The mechanism is unchanged — FIRESTARTER_DEV_ALLOW_PRE_V12=1 still bypasses the major<3 refuse guard; only the rationale comment changes"
    - "pytest tests/test_fwguard.py reports 4 PASS unchanged (no test edit)"
    - "pytest tests/test_decoder.py reports 25 PASS unchanged"
  artifacts:
    - path: "firestarter_app/firestarter/serial_comm.py"
      provides: "Refreshed Phase 6 / LFW-05 comment for the FIRESTARTER_DEV_ALLOW_PRE_V12 escape hatch"
      contains: "FIRESTARTER_DEV_ALLOW_PRE_V12"
  key_links:
    - from: "firestarter_app/firestarter/serial_comm.py:752-755"
      to: "firestarter/include/version.h"
      via: "the comment describes the post-Phase-9 semantics of the env-var as a backwards-regression-test escape hatch"
      pattern: "bench-testing.*historical.*v2"
---

<objective>
Refresh the inline comment block at `firestarter_app/firestarter/serial_comm.py:752-755` to drop the "until then [Phase 9 firmware bump]" framing — after Phase 9 ships the firmware HAS bumped to major=3, and the env-var `FIRESTARTER_DEV_ALLOW_PRE_V12` becomes a forward-looking escape hatch for bench-testing a current host against historical (v2.x) firmware builds.

This plan is a 4-line comment-only edit. It runs in Wave 2 in parallel with Plan 02 (firmware atomic deletion) because the two changes touch disjoint sub-repos (`firestarter_app/` vs `firestarter/`). The mechanism — the `os.environ.get("FIRESTARTER_DEV_ALLOW_PRE_V12") != "1"` check and the `raise FirmwareOutdatedError(...)` body — is unchanged.

Purpose: keep the host code's inline rationale truthful after Phase 9 ships. The `until then` framing is wrong once the firmware HAS bumped. Implements the "KEEP, update comment" Claude's-Discretion item from `09-CONTEXT.md`.
Output: A single-file commit touching only lines 752-755 of `serial_comm.py`. The test_fwguard.py and test_decoder.py regression suites must stay green unchanged.
</objective>

<execution_context>
@/workspaces/firestarter_prom/.claude/get-shit-done/workflows/execute-plan.md
@/workspaces/firestarter_prom/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-CONTEXT.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-RESEARCH.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-PATTERNS.md
@firestarter_app/CLAUDE.md
@firestarter_app/firestarter/serial_comm.py

<interfaces>
<!-- Comment block to refresh. Source: 09-RESEARCH.md §"Host-side Surface" + 09-PATTERNS.md §"Pattern Assignment 7". -->

Current state (`serial_comm.py:752-755`):
```python
                                # Phase 6 (LFW-05 + LHOST-04): refuse pre-v1.2
                                # firmware. The firmware bumps to major=3 in
                                # Phase 9; until then, bench scripts use
                                # FIRESTARTER_DEV_ALLOW_PRE_V12=1 to bypass.
```

Target state after this plan (verbatim from 09-PATTERNS.md §"Pattern Assignment 7"):
```python
                                # Phase 6 (LFW-05 + LHOST-04): refuse pre-v1.2 firmware. The firmware bumped
                                # to major=3 in Phase 9. Set FIRESTARTER_DEV_ALLOW_PRE_V12=1 to bypass when
                                # bench-testing a current host against a historical (v2.x) firmware build.
```

The mechanism following the comment (lines 756-770 approx) is unchanged:
```python
try:
    major = int(current_version.split(".")[0])
except (ValueError, IndexError):
    major = 0
if (
    major < 3
    and os.environ.get("FIRESTARTER_DEV_ALLOW_PRE_V12") != "1"
):
    raise FirmwareOutdatedError(
        f"Firmware version {current_version} is pre-v1.2 (text-format logging). "
        ...
    )
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Refresh the FIRESTARTER_DEV_ALLOW_PRE_V12 inline comment</name>
  <read_first>
    - firestarter_app/firestarter/serial_comm.py (read lines 740-790 to see the comment + the surrounding refuse-guard mechanism)
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-RESEARCH.md §"Host-side Surface" → "FIRESTARTER_DEV_ALLOW_PRE_V12 — KEEP, update comment wording"
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-PATTERNS.md §"Pattern Assignment 7" (exact diff)
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-CONTEXT.md §"Claude's Discretion" → "Host `FIRESTARTER_DEV_ALLOW_PRE_V12` env-var fate"
    - firestarter_app/tests/test_fwguard.py (the 4 SC#3 cases — must stay green unchanged)
  </read_first>
  <files>firestarter_app/firestarter/serial_comm.py</files>
  <behavior>
    - Before: lines 752-755 contain the 4-line "Phase 6 ... until then ... FIRESTARTER_DEV_ALLOW_PRE_V12=1 to bypass." block
    - After: lines 752-754 contain the new 3-line "Phase 6 (LFW-05 + LHOST-04): refuse pre-v1.2 firmware. The firmware bumped to major=3 in Phase 9. Set FIRESTARTER_DEV_ALLOW_PRE_V12=1 to bypass when bench-testing a current host against a historical (v2.x) firmware build." block
    - No code below line 755 changes (the `try: major = int(...)` and the `if major < 3 and os.environ.get(...): raise FirmwareOutdatedError(...)` mechanism stays exactly as-is)
    - No imports are added or removed
    - The comment preserves the `# Phase N (LXXX-NN): ...` voice per 09-PATTERNS.md §"Shared Patterns" — phase-tagged inline comment voice
  </behavior>
  <action>
    At `firestarter_app/firestarter/serial_comm.py:752-755`, replace the 4-line comment block (lines starting `# Phase 6 (LFW-05 + LHOST-04): refuse pre-v1.2`, `# firmware. The firmware bumps to major=3 in`, `# Phase 9; until then, bench scripts use`, `# FIRESTARTER_DEV_ALLOW_PRE_V12=1 to bypass.`) with the new 3-line comment block from 09-PATTERNS.md §"Pattern Assignment 7":

    ```
    # Phase 6 (LFW-05 + LHOST-04): refuse pre-v1.2 firmware. The firmware bumped
    # to major=3 in Phase 9. Set FIRESTARTER_DEV_ALLOW_PRE_V12=1 to bypass when
    # bench-testing a current host against a historical (v2.x) firmware build.
    ```

    Preserve the exact leading whitespace / indentation of the original block (32 spaces by the `# ` prefix shown in 09-PATTERNS.md). Do NOT touch any line below 755 — the `try: major = int(current_version.split(".")[0])` and the `if major < 3 and os.environ.get(...): raise FirmwareOutdatedError(...)` mechanism stays exactly as-is. Do NOT touch any line above 752.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_prom &amp;&amp; [ "$(grep -c 'until then' firestarter_app/firestarter/serial_comm.py)" = "0" ] &amp;&amp; grep -c 'bench-testing a current host against a historical (v2.x) firmware build' firestarter_app/firestarter/serial_comm.py &amp;&amp; cd firestarter_app &amp;&amp; pytest tests/test_fwguard.py tests/test_decoder.py -q 2>&amp;1 | tail -3 | grep -E 'passed'</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c 'until then' firestarter_app/firestarter/serial_comm.py` returns exactly 0 (the stale framing is gone)
    - `grep -c 'bench-testing a current host against a historical (v2.x) firmware build' firestarter_app/firestarter/serial_comm.py` returns exactly 1 (the new wording is present)
    - `grep -c 'FIRESTARTER_DEV_ALLOW_PRE_V12' firestarter_app/firestarter/serial_comm.py` returns 2 (one in the comment, one in the `os.environ.get(...)` mechanism check — unchanged from pre-Phase-9 count)
    - `cd firestarter_app && pytest tests/test_fwguard.py -v` reports 4 PASS
    - `cd firestarter_app && pytest tests/test_decoder.py -q` reports 25 PASS
  </acceptance_criteria>
  <done>
    - The 4-line comment block is replaced by the new 3-line comment block per 09-PATTERNS.md §"Pattern Assignment 7"
    - The mechanism is byte-identical to pre-Phase-9 (the `if major < 3 and os.environ.get(...)` check is untouched)
    - Both host pytest suites (`test_fwguard.py` + `test_decoder.py`) stay green unchanged
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| comment ↔ mechanism | Inline comment is documentation only; no functional behavior on the host. If the comment becomes stale (e.g., references a state that has changed), it misleads a future developer; the mechanism is unaffected. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-09-03-01 | Information Disclosure | Inline comment misleads developer about post-Phase-9 semantics | mitigate | This plan IS the mitigation — the comment is refreshed to describe the post-Phase-9 reality. Future plans should re-audit if Phase 10+ changes the env-var's role. |
| T-09-03-02 | Tampering | Accidental edit to the surrounding `if major < 3 and os.environ.get(...)` mechanism during comment refresh | mitigate | Task 1 acceptance criterion explicitly verifies (a) `FIRESTARTER_DEV_ALLOW_PRE_V12` appears exactly 2× (one in the comment, one in the mechanism) and (b) the 4 fwguard tests stay green. The pytest gate would catch any mechanism break. |
</threat_model>

<verification>
### Plan-level acceptance gate

```bash
# 1. Stale framing removed
[ "$(grep -c 'until then' firestarter_app/firestarter/serial_comm.py)" = "0" ] || { echo "FAIL: stale framing"; exit 1; }
# 2. New wording present
grep -q 'bench-testing a current host against a historical (v2.x) firmware build' firestarter_app/firestarter/serial_comm.py || { echo "FAIL: new wording"; exit 1; }
# 3. Mechanism intact (env-var still referenced exactly 2x)
[ "$(grep -c 'FIRESTARTER_DEV_ALLOW_PRE_V12' firestarter_app/firestarter/serial_comm.py)" = "2" ] || { echo "FAIL: mechanism altered"; exit 1; }
# 4. Host regression suites green
cd firestarter_app && pytest tests/test_fwguard.py tests/test_decoder.py -q 2>&1 | tail -3 | grep -q 'passed' || { echo "FAIL: pytest"; exit 1; }
echo "PLAN 03 GREEN"
```
</verification>

<success_criteria>
- The comment block at `serial_comm.py:752-755` is replaced by the new 3-line block per 09-PATTERNS.md §"Pattern Assignment 7"
- The phrase "until then" no longer appears anywhere in `serial_comm.py`
- The `if major < 3 and os.environ.get("FIRESTARTER_DEV_ALLOW_PRE_V12") != "1"` mechanism is untouched
- `pytest tests/test_fwguard.py` reports 4 PASS; `pytest tests/test_decoder.py` reports 25 PASS
</success_criteria>

<output>
After completion, create `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-03-SUMMARY.md` recording:
- The 4-line → 3-line diff at `serial_comm.py:752-755`
- Confirmation that `grep -c 'until then'` returns 0
- pytest output (4 PASS for test_fwguard, 25 PASS for test_decoder)
</output>
