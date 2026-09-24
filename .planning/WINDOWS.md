---
schema_version: 1
open_count: 0
waived_count: 0
fixed_count: 3
total_count: 3
last_updated: 2026-09-23T23:49:17.883Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 202 | deviation | firestarter_app/firestarter/eprom_operations.py |  | verify_eprom bounds its COMMAND_READ to the file's length by reusing _setup_operation's COMMAND_READ+size override (passing region_length as a string) ahead of --size landing for verify in 202-05. 202-05 should reconcile this with the real --size/-a option and D-17's explicit region-resolution rules. | fixed |  | 2026-09-20T16:22:24.576Z | 2026-09-20T19:21:05.488Z |
| 2 | 203 | deviation | firestarter_app/tests/test_characterization.py |  | test_help_write and test_no_blank_check_polarity (write --help snapshots) are known-red at 203-03 close by plan design -- write --verify/--full landed and changed the help text; hand-editing the two syrupy snapshot blocks is explicitly 203-04's job (203-03-PLAN.md verification block). Never run --snapshot-update. | fixed | Both write --help snapshot blocks hand-edited in 203-04 (never --snapshot-update) to match the rewritten host-side blank-check help text; both tests green, full suite 2304 passed / 0 failed, 36/36 snapshots passing. | 2026-09-21T13:34:28.036Z | 2026-09-21T13:50:15.421Z |
| 3 | 204 | unmet-truth | .planning/milestones/v1.41-phases/204-the-command-surfaces-leave-the-firmware/204-BENCH-TRACER.md |  | Task 3's <human-check> asked to confirm the seated part is a W27C512; the un-forced read reported Chip ID 0x1818 vs the database's expected 0xda08 for W27C512,W27E512. Most likely explained by the rig's known VPP-sensing unreliability, but not independently confirmed — needs operator/UAT sign-off. | fixed | Closed on evidence in 207.1 (D-01), no re-bench. Operator confirmation on 2026-09-23 (answer: Same chip): the 206-04 bench used the same physical W27C512 as the 204 and 205 benches. 206-SESSION-COST.md reads chip_id_actual 55816 (0xDA08, matching chip_id_expected) on all six runs, on the same rig: Leonardo, /dev/ttyACM0, Rev 2.0 shield. Probable cause of the 204 and 205 0x1818 reads, stated as probable and not measured: the VPP miscalibration that 206-04 found and the operator's pot trim corrected (13.0 V to 12.0 V, 206-04-SUMMARY.md); a wrong VPP puts the wrong voltage on A9 for the ID-sense read, and the 204-BENCH-TRACER.md and 205-BENCH-MATRIX.md transcripts both carry the VPP is high 13.0V warning. The returned 18 18 bytes match the chip's array data, not an ID encoding (204-BENCH-TRACER.md). | 2026-09-22T09:04:23.280Z | 2026-09-23T23:49:17.883Z |

````json
[
  {
    "id": 1,
    "kind": "deviation",
    "phase": "202",
    "file": "firestarter_app/firestarter/eprom_operations.py",
    "line": null,
    "description": "verify_eprom bounds its COMMAND_READ to the file's length by reusing _setup_operation's COMMAND_READ+size override (passing region_length as a string) ahead of --size landing for verify in 202-05. 202-05 should reconcile this with the real --size/-a option and D-17's explicit region-resolution rules.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-09-20T16:22:24.576Z",
    "resolved_at": "2026-09-20T19:21:05.488Z"
  },
  {
    "id": 2,
    "kind": "deviation",
    "phase": "203",
    "file": "firestarter_app/tests/test_characterization.py",
    "line": null,
    "description": "test_help_write and test_no_blank_check_polarity (write --help snapshots) are known-red at 203-03 close by plan design -- write --verify/--full landed and changed the help text; hand-editing the two syrupy snapshot blocks is explicitly 203-04's job (203-03-PLAN.md verification block). Never run --snapshot-update.",
    "status": "fixed",
    "reason": "Both write --help snapshot blocks hand-edited in 203-04 (never --snapshot-update) to match the rewritten host-side blank-check help text; both tests green, full suite 2304 passed / 0 failed, 36/36 snapshots passing.",
    "recorded_at": "2026-09-21T13:34:28.036Z",
    "resolved_at": "2026-09-21T13:50:15.421Z"
  },
  {
    "id": 3,
    "kind": "unmet-truth",
    "phase": "204",
    "file": ".planning/milestones/v1.41-phases/204-the-command-surfaces-leave-the-firmware/204-BENCH-TRACER.md",
    "line": null,
    "description": "Task 3's <human-check> asked to confirm the seated part is a W27C512; the un-forced read reported Chip ID 0x1818 vs the database's expected 0xda08 for W27C512,W27E512. Most likely explained by the rig's known VPP-sensing unreliability, but not independently confirmed — needs operator/UAT sign-off.",
    "status": "fixed",
    "reason": "Closed on evidence in 207.1 (D-01), no re-bench. Operator confirmation on 2026-09-23 (answer: Same chip): the 206-04 bench used the same physical W27C512 as the 204 and 205 benches. 206-SESSION-COST.md reads chip_id_actual 55816 (0xDA08, matching chip_id_expected) on all six runs, on the same rig: Leonardo, /dev/ttyACM0, Rev 2.0 shield. Probable cause of the 204 and 205 0x1818 reads, stated as probable and not measured: the VPP miscalibration that 206-04 found and the operator's pot trim corrected (13.0 V to 12.0 V, 206-04-SUMMARY.md); a wrong VPP puts the wrong voltage on A9 for the ID-sense read, and the 204-BENCH-TRACER.md and 205-BENCH-MATRIX.md transcripts both carry the VPP is high 13.0V warning. The returned 18 18 bytes match the chip's array data, not an ID encoding (204-BENCH-TRACER.md).",
    "recorded_at": "2026-09-22T09:04:23.280Z",
    "resolved_at": "2026-09-23T23:49:17.883Z"
  }
]
````
