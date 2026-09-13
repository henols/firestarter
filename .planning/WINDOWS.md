---
schema_version: 1
open_count: 8
waived_count: 0
fixed_count: 0
total_count: 8
last_updated: 2026-09-13T00:38:49.742Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 172 | unrun-verify | .planning/phases/172-policy-one-tracker-protected-main/172-06-PLAN.md |  | Task 3's literal <automated> verify scripts (hardcoded Integration:15368:always bypass actor, three-fresh-creates assumption, 4998759-absence assertion) were never executed as written -- D-10's reversal to amend-in-place made their literal assertions false by design. Equivalent adapted checks were run manually and recorded in evidence/172-06-ruleset-readback.txt. | open |  | 2026-09-01T21:40:44.829Z |  |
| 2 | 172 | deviation | .planning/phases/172-policy-one-tracker-protected-main/172-06-PLAN.md |  | D-10 (delete-and-recreate henols/firestarter's ruleset 4998759) REVERSED at the Task 1 checkpoint:decision gate to Option B (amend 4998759 in place via PUT, create only firestarter_app fresh) after the incumbent was measured identical to the prom canary on every non-volatile field. No DELETE was issued anywhere in this plan. | open |  | 2026-09-01T21:40:45.364Z |  |
| 3 | 178 | deviation | .planning/REQUIREMENTS.md |  | Task 2's verify script cited a stale chip_test.py:2524-2541 (already stale by the time this plan ran); repaired to the re-derived chip_test.py:2567-2574 instead | open |  | 2026-09-06T12:58:56.445Z |  |
| 4 | 185 | deviation | .planning/phases/185-records-and-checks-that-are-current/185-03-PLAN.md |  | Task 1/2 verify gate 'grep -c def test_' assumes 1:1 test-def-to-collected mapping; 3 parametrize decorators break it (measured baseline 59/58, not plan's assumed 64/63) | open |  | 2026-09-11T18:00:32.014Z |  |
| 5 | 185 | deviation | .planning/phases/185-records-and-checks-that-are-current/185-03-PLAN.md |  | Task 1 verify gate 'grep -c _off_tty' (unfiltered) collides with pre-existing unrelated test name test_submit_off_tty_end_to_end_never_opens_browser_or_runs_gh; true zero-survivor gate is grep -c '_off_tty()' (parenthesized), which the plan's own Step 0 baseline used | open |  | 2026-09-11T18:00:32.619Z |  |
| 6 | 188 | deviation | firestarter_app/tests/test_blast_radius_invariance.py |  | WR-01 (snapshot-drift coverage over 19 shape ids, test_committed_snapshot_matches_a_fresh_regeneration) has no replacement; D-01/D-04 delete tools/snapshot_report_shapes.py in plan 188-05 and D-23 forbids a successor guard. Accepted loss, named for 188-09's verdict note. | open |  | 2026-09-13T00:38:49.490Z |  |
| 7 | 188 | deviation | firestarter_app/tests/test_blast_radius_invariance.py |  | Two prose mentions of tools/snapshot_report_shapes.py:render_shape (lines ~193, ~469 pre-edit) were left in place rather than edited, to preserve this file's added=0 (deletions-only) invariant and the plan's explicit leave-_to_dict_with_db_diff-exactly-as-is instruction. Plan 188-04's own zero-occurrence acceptance criterion for render_shape/snapshot_report_shapes is therefore not fully met (2 residual prose hits); render_shape itself is not deleted until plan 188-05, so these are not yet false. | open |  | 2026-09-13T00:38:49.622Z |  |
| 8 | 188 | deviation | firestarter_app/tests/test_lock_status_class_partition.py |  | test_silicon_only_tokens_never_appear_in_a_return_value_ast is now decorative: its planted-fixture pairing (test_planted_fixture_fails_the_gate_seam_naming_class1 + the protection-readability gate) was deleted with the retired gate family (D-01), so nothing left proves the AST rule can fail. Disclosed cost, named for 188-09's verdict note. | open |  | 2026-09-13T00:38:49.742Z |  |

````json
[
  {
    "id": 1,
    "kind": "unrun-verify",
    "phase": "172",
    "file": ".planning/phases/172-policy-one-tracker-protected-main/172-06-PLAN.md",
    "line": null,
    "description": "Task 3's literal <automated> verify scripts (hardcoded Integration:15368:always bypass actor, three-fresh-creates assumption, 4998759-absence assertion) were never executed as written -- D-10's reversal to amend-in-place made their literal assertions false by design. Equivalent adapted checks were run manually and recorded in evidence/172-06-ruleset-readback.txt.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-01T21:40:44.829Z",
    "resolved_at": null
  },
  {
    "id": 2,
    "kind": "deviation",
    "phase": "172",
    "file": ".planning/phases/172-policy-one-tracker-protected-main/172-06-PLAN.md",
    "line": null,
    "description": "D-10 (delete-and-recreate henols/firestarter's ruleset 4998759) REVERSED at the Task 1 checkpoint:decision gate to Option B (amend 4998759 in place via PUT, create only firestarter_app fresh) after the incumbent was measured identical to the prom canary on every non-volatile field. No DELETE was issued anywhere in this plan.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-01T21:40:45.364Z",
    "resolved_at": null
  },
  {
    "id": 3,
    "kind": "deviation",
    "phase": "178",
    "file": ".planning/REQUIREMENTS.md",
    "line": null,
    "description": "Task 2's verify script cited a stale chip_test.py:2524-2541 (already stale by the time this plan ran); repaired to the re-derived chip_test.py:2567-2574 instead",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-06T12:58:56.445Z",
    "resolved_at": null
  },
  {
    "id": 4,
    "kind": "deviation",
    "phase": "185",
    "file": ".planning/phases/185-records-and-checks-that-are-current/185-03-PLAN.md",
    "line": null,
    "description": "Task 1/2 verify gate 'grep -c def test_' assumes 1:1 test-def-to-collected mapping; 3 parametrize decorators break it (measured baseline 59/58, not plan's assumed 64/63)",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-11T18:00:32.014Z",
    "resolved_at": null
  },
  {
    "id": 5,
    "kind": "deviation",
    "phase": "185",
    "file": ".planning/phases/185-records-and-checks-that-are-current/185-03-PLAN.md",
    "line": null,
    "description": "Task 1 verify gate 'grep -c _off_tty' (unfiltered) collides with pre-existing unrelated test name test_submit_off_tty_end_to_end_never_opens_browser_or_runs_gh; true zero-survivor gate is grep -c '_off_tty()' (parenthesized), which the plan's own Step 0 baseline used",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-11T18:00:32.619Z",
    "resolved_at": null
  },
  {
    "id": 6,
    "kind": "deviation",
    "phase": "188",
    "file": "firestarter_app/tests/test_blast_radius_invariance.py",
    "line": null,
    "description": "WR-01 (snapshot-drift coverage over 19 shape ids, test_committed_snapshot_matches_a_fresh_regeneration) has no replacement; D-01/D-04 delete tools/snapshot_report_shapes.py in plan 188-05 and D-23 forbids a successor guard. Accepted loss, named for 188-09's verdict note.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-13T00:38:49.490Z",
    "resolved_at": null
  },
  {
    "id": 7,
    "kind": "deviation",
    "phase": "188",
    "file": "firestarter_app/tests/test_blast_radius_invariance.py",
    "line": null,
    "description": "Two prose mentions of tools/snapshot_report_shapes.py:render_shape (lines ~193, ~469 pre-edit) were left in place rather than edited, to preserve this file's added=0 (deletions-only) invariant and the plan's explicit leave-_to_dict_with_db_diff-exactly-as-is instruction. Plan 188-04's own zero-occurrence acceptance criterion for render_shape/snapshot_report_shapes is therefore not fully met (2 residual prose hits); render_shape itself is not deleted until plan 188-05, so these are not yet false.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-13T00:38:49.622Z",
    "resolved_at": null
  },
  {
    "id": 8,
    "kind": "deviation",
    "phase": "188",
    "file": "firestarter_app/tests/test_lock_status_class_partition.py",
    "line": null,
    "description": "test_silicon_only_tokens_never_appear_in_a_return_value_ast is now decorative: its planted-fixture pairing (test_planted_fixture_fails_the_gate_seam_naming_class1 + the protection-readability gate) was deleted with the retired gate family (D-01), so nothing left proves the AST rule can fail. Disclosed cost, named for 188-09's verdict note.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-13T00:38:49.742Z",
    "resolved_at": null
  }
]
````
