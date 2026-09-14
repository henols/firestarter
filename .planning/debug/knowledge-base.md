# GSD Debug Knowledge Base

Resolved debug sessions. Used by `gsd-debugger` to surface known-pattern hypotheses at the start
of new investigations.

---

## beta-probe-empty-input — Uno-class probe self-sustaining failure via spurious ack interleave
- **Date:** 2026-09-09
- **Error patterns:** Empty input, ERROR: Empty input, responded but not with OK, No compatible
  programmer found, Bad JSON, Buf val: 0x7b, self-sustaining probe failure, Uno DTR reset,
  MSG_ERR_EMPTY_INPUT
- **Root cause(s):** Firmware reuses `MSG_ERR_EMPTY_INPUT` ("Empty input") as a generic catch-all
  for every CMD_IDLE COBS-decode failure (empty read, CRC mismatch, COBS violation, or
  read/inter-byte underrun), so the host cannot distinguish a real command rejection from an
  unrelated, self-recovering framing glitch; `SerialCommunicator.expect_ack()`/`_probe_port`
  treat the FIRST post-send OK/ERROR response as final, with no check for whether the genuine ack
  is already queued immediately behind it. Both conditions were required (AND-gate): the ambiguous
  error text alone is cosmetic, and the host's read-first-response behavior alone would be
  harmless if firmware never emitted an unsolicited frame between a sent command and its ack.
  No firmware code regression was found or is implicated — a full source-diff bisect proved
  `firestarter_uno.hex` is compiled-byte-identical across 3.0.0b23/b24/b25 (one version-string
  line differs) and that the b22->b23 code delta never touches the CMD_IDLE decode path.
- **Fix:** `SerialCommunicator._probe_port` (`firestarter_app/firestarter/serial_comm.py`) keeps
  reading past the generic frame-decode-failure text within a bounded wall-clock deadline
  (`SETUP_ACK_RECOVERY_TIMEOUT_S`, 2.0s), discarding only responses whose text is exactly that
  generic string and returning the first response that is anything else — scoped to this one
  ambiguous error and to this one hazard-free call site (CMD_FW_VERSION never engages VPP/VPE),
  so a genuine rejection elsewhere still fails immediately. **Reworked once, live-hardware-driven:**
  the first version (a single fixed extra retry) was proven under-built by a live matrix on a
  real Arduino Uno R3 — `_probe_port`'s existing `fault_inject_outgoing` hook let the interleaved
  spurious-frame CONDITION be manufactured deterministically without needing the reporter's own
  noisy environment, separating "reproduce the failure" (needs their hardware) from "reproduce
  the cause" (doesn't). Two injected spurious frames broke the fixed-retry version exactly as the
  reporter's own log (which already showed two `Empty input` lines) implied was possible; the
  deadline-based rework survived two AND a bonus three-frame case, live, on the same board.
- **Files changed:** firestarter_app/firestarter/serial_comm.py,
  firestarter_app/tests/test_probe_spurious_setup_ack.py
- **Why not caught:** no gate existed for this class. The existing test suite exercised
  `_probe_port`/`expect_ack()` only with clean, well-ordered response streams (see
  `test_fwguard.py`, `test_hw_revision_gate.py`); nothing modeled an interleaved unsolicited
  response between a sent command and its ack, so a host-side "return on first response" gap had
  no test surface to fail against. The bug is also structurally invisible to this project's CI:
  every native/host test runs against a Leonardo-shaped or hardware-free fixture; the Uno-specific
  PORTD/UART pin-sharing hazard class this bug's spurious frame most plausibly originates from
  (already documented twice elsewhere in this codebase — `PREFIX_REGEX`'s rightmost-match design
  and `rurp_set_communication_mode()`'s boot-transition drain) has no native/CI equivalent at all.
  A raw-byte capture on real Uno hardware caught a reproducible stray boot byte (8/8 trials,
  same value) independent of any injection, corroborating that this hazard class is real and not
  merely theoretical — but a first pass at "verify on real hardware" that only ran the NATURAL,
  non-adversarial probe (41/41 clean) would have reported false confidence had the coordinator
  not pushed for deliberate fault injection to separate the failure from its cause.
- **Recurrence guard:** regression tests
  `firestarter_app/tests/test_probe_spurious_setup_ack.py::test_probe_port_recovers_from_spurious_empty_input_ahead_of_real_ack`
  and `::test_probe_port_recovers_from_two_spurious_empty_input_frames_ahead_of_real_ack` (the
  second one RED against the original fixed-retry fix, GREEN after the deadline rework — it is
  the one that actually pins the bound-vs-count distinction), plus the negative-control sibling
  `test_probe_port_still_fails_on_a_genuine_unrecoverable_error`, which confirms the fix does not
  broaden `_probe_port`'s tolerance beyond the one ambiguous error text and stays bounded rather
  than hanging. If a future firmware change ever splits `MSG_ERR_EMPTY_INPUT` into distinct
  message IDs per failure cause (a reasonable future enhancement, not done this session), this KB
  entry and the retry's text-match scoping should be revisited together. **Process lesson worth
  reusing on a future "verify a host-side fix against a flaky hardware interaction" session:**
  if the target device already exposes an outgoing/incoming fault-injection seam (as
  `fault_inject_outgoing` did here), prefer manufacturing the CONDITION deterministically over
  waiting for or asking for the reporter's exact noisy environment — the two are often separable,
  and a live A/B/C(/D) matrix through the seam is strictly better evidence than either a
  `_FakeSerial`-only test or a natural-conditions non-reproduction.
---

## auto-mode-permission-blocks — blanket Bash wildcards pre-empt the classifier, and a bare `cd` segment always defers to it
- **Date:** 2026-09-14
- **Error patterns:** Permission for this action was denied by the Claude Code auto mode
  classifier, [Self-Modification], [Auto-Mode Bypass], denied in this session (external system
  write), cd in a compound command can trigger a permission prompt, gh release create, git push
  denial, wiki push denial
- **Root cause(s):** Claude Code resolves a Bash action deterministically only when every
  shell-control-operator-separated segment of the command matches a `permissions.allow` entry. A
  bare `cd` segment matched no entry in either settings file, so any `cd X && verb args` command
  always deferred to the auto-mode classifier, no matter how well the trailing verb was covered.
  This caused the reported friction. Separately, `permissions.allow` in settings.json carried
  blanket single-verb wildcards (`Bash(git *)`, `Bash(gh *)`, `Bash(gh pr *)`, `Bash(gh api *)`),
  and settings.local.json separately carried `Bash(gh release:*)`, `Bash(gh release edit:*)`, and
  `Bash(gh pr merge:*)`. These wildcards deterministically pre-approved bare invocations of the
  exact dangerous sub-verbs the classifier's own `hard_deny`/`soft_deny` arrays exist to gate,
  before those arrays were ever consulted. This was the more serious, safety-relevant half of the
  root cause. Both causes needed a fix together, one in the config-scope category and one in the
  usage-pattern category (AND-gate: the missing `cd` rule alone only explains friction, the
  blanket wildcards alone only explain the safety gap).
- **Fix:** In `/workspaces/.claude/settings.json`, removed the four blanket wildcards, added
  scoped read-only sub-verb entries (`gh issue list/view`, `gh pr list/view/diff/checks`, `gh run
  list/view`, `gh release list/view`, `gh label list`, `gh search`, `gh repo view`, `gh api -X
  GET`), and merged a full `autoMode` block (environment 9, allow 13, soft_deny 7, hard_deny 6
  entries) naming the project's actual safety boundary, including a rule that lets a `cd` into a
  known project directory followed by an already-permitted command clear the classifier instead
  of tripping on the bare `cd` segment. In `/workspaces/.claude/settings.local.json`, removed the
  three dangerous entries named above. `git push` was kept allowed, on the operator's call, because
  GitHub branch protection with `current_user_can_bypass: never` already rejects the catastrophic
  case server-side.
- **Files changed:** `/workspaces/.claude/settings.json`, `/workspaces/.claude/settings.local.json`.
  Both are gitignored and not tracked by git. No source files changed.
- **Why not caught:** No gate existed for this class. This is a Claude Code harness
  permission-configuration gap, not a defect in project source or tests. Nothing in CI, code
  review, or any existing GSD gate audits `.claude/settings*.json` for allow-rule scope or for
  compound-command segment coverage.
- **Recurrence guard:** The narrowed `permissions.allow` lists and the populated `autoMode`
  `hard_deny`/`soft_deny` arrays are now the durable artifact. This knowledge base entry is the
  detection guard for a future session that reports the same friction or the same self-modification
  denial. There is no automated test for this class. A future audit of either settings file should
  check for a reintroduced single-verb blanket wildcard (`Bash(git *)`, `Bash(gh *)`, or similar)
  before assuming a new allow entry is safe.
---
