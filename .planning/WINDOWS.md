---
schema_version: 1
open_count: 0
waived_count: 0
fixed_count: 2
total_count: 2
last_updated: 2026-09-21T13:50:15.421Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 202 | deviation | firestarter_app/firestarter/eprom_operations.py |  | verify_eprom bounds its COMMAND_READ to the file's length by reusing _setup_operation's COMMAND_READ+size override (passing region_length as a string) ahead of --size landing for verify in 202-05. 202-05 should reconcile this with the real --size/-a option and D-17's explicit region-resolution rules. | fixed |  | 2026-09-20T16:22:24.576Z | 2026-09-20T19:21:05.488Z |
| 2 | 203 | deviation | firestarter_app/tests/test_characterization.py |  | test_help_write and test_no_blank_check_polarity (write --help snapshots) are known-red at 203-03 close by plan design -- write --verify/--full landed and changed the help text; hand-editing the two syrupy snapshot blocks is explicitly 203-04's job (203-03-PLAN.md verification block). Never run --snapshot-update. | fixed | Both write --help snapshot blocks hand-edited in 203-04 (never --snapshot-update) to match the rewritten host-side blank-check help text; both tests green, full suite 2304 passed / 0 failed, 36/36 snapshots passing. | 2026-09-21T13:34:28.036Z | 2026-09-21T13:50:15.421Z |

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
  }
]
````
