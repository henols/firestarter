# Deferred Items

Out-of-scope discoveries logged during execution, per executor scope-boundary rules
(not fixed — pre-existing and unrelated to the executing plan's task).

## 121-08

- **Pre-existing untracked file in the firmware submodule**: `git -C /workspaces/firestarter status --porcelain` shows `?? firestarter/include/messages.h` (untracked). This plan's `<verification>` block calls for that command to be empty, but plan 121-08 makes no edits anywhere under `/workspaces/firestarter` (its objective states "No firmware source is edited by this plan") — the file predates this plan's execution. Left untouched; flagging for whichever plan/session owns firmware working-tree hygiene (likely a stale codegen artifact per `reference_firmware_messages_h_is_codegen_generated.md` — `messages.h` is codegen-generated from `messages.toml`).
