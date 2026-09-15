# Arm CLI Surface Comparison

Compared: `control` vs `v133` (Phase 160 D-06/RIG-03).

- `control` command/group entry count: 25
- `v133` command/group entry count: 25

## Option/argument name set difference (THE GATE)

- Entries present in `control` but not `v133`: **none**
- Entries present in `v133` but not `control`: **none**

This set comparison is the gate that makes one arm-agnostic step vocabulary valid for PROCEDURE.md: it must be empty in both directions.

## `--help` text differences (recorded datum, NOT a gate failure)

None. Both arms render identical `--help` text for every command.

A help-text difference is a recorded datum, not a gate failure -- the v1.33 app range contains a commit titled "restore Click command docstrings", so help text is known to have moved independently of the option/argument surface. No PROCEDURE.md step depends on help text, so a difference here does not invalidate the shared step vocabulary.
