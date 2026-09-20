---
schema_version: 1
open_count: 0
waived_count: 0
fixed_count: 1
total_count: 1
last_updated: 2026-09-20T19:21:05.488Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 202 | deviation | firestarter_app/firestarter/eprom_operations.py |  | verify_eprom bounds its COMMAND_READ to the file's length by reusing _setup_operation's COMMAND_READ+size override (passing region_length as a string) ahead of --size landing for verify in 202-05. 202-05 should reconcile this with the real --size/-a option and D-17's explicit region-resolution rules. | fixed |  | 2026-09-20T16:22:24.576Z | 2026-09-20T19:21:05.488Z |

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
  }
]
````
