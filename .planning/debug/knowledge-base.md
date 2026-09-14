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

## planning-refs-in-src-comments — a sweep's own detector confirmed its own partial repair, so 1254 planning citations survived a sweep recorded as complete
- **Date:** 2026-09-14
- **Error patterns:** none — this class raises no error. Symptom keywords: `.planning` path in a
  comment, `Phase NNN`, `Plan NNN-NN`, `D-NN`, `REQ-`, `LOCK-NN`, `CAP-0N`, `SWEEP-NN` in product
  source; "sweep recorded as complete but instances remain"; "grep finds hits a gate reported zero
  for"; a comment that opens mid-sentence with its subject missing; a detector whose count fell to
  near zero across its own remediation.
- **Root cause(s):** THREE causes, AND-gated — no one of them alone produces the outcome.
  (1) LOAD-BEARING, code — a self-confirming detector. Phase 154's sweep oracle was
  `(//|/\*|^\s*\*|#)\s*(Task|Phase|Plan|P\d{3}|Req|REQ-|CAP-0|D-\d|WR-\d|LOOP-\d|\d{3}-CONTEXT)`.
  The `\s*` binds the token group TO THE COMMENT MARKER, so a citation anywhere further right is
  invisible; and `.planning` was never one of the tokens, so a bare path was always invisible. The
  prescribed repair — delete the marker-adjacent label — is precisely the operation that pushes the
  rest of the line out of marker-adjacency. The detector's visibility therefore FELL ACROSS ITS OWN
  REMEDIATION: 345 of 718 lines (48%) before, 94 of 357 (26%) after. It reported 73% removal against
  an actual 50%, and it reported that BECAUSE of its own partial fix. 535 of 620 survivors (86%)
  were structurally unreachable by it.
  NOTE, because it is the trap: `^\s*\*` IS one of the four alternations. Block-comment
  CONTINUATION lines were never invisible on account of the marker — the obvious hypothesis, and
  the wrong one. The anchor is the `\s*`, not the marker class.
  (2) LOAD-BEARING, config/process — no gate existed anywhere. None of the seven workflow files
  across the three repositories ran any comment or provenance check; the meta repository had no
  workflows at all. Nothing could go red, so neither the 612 survivors nor 8 later reintroductions
  were announced.
  (3) CONTRIBUTORY, process — the sweep discharged a NARROWER CONTRACT than the rule. SWEEP-03
  deliberately retains requirement/decision ids in test files, SWEEP-04 gives test files "narrow
  treatment only", and Ruling B leaves four blob-sha-pinned paths un-swept (editing them reddens a
  golden until it is re-derived, and the phase declined that cost). The sweep commit attributes 60
  of its 94 declared survivors to that retention. CLAUDE.md has no test-file carve-out. "Sweep
  complete" was true of SWEEP-01..13 and false of the rule it served.
  REFUTED as a cause: authoring-time reintroduction. `git blame` of all 620 marker-independent
  lines puts 612 BEFORE the sweeps and 8 after. Treating this as "someone keeps writing citations"
  would have produced a style reminder and fixed nothing.
- **Fix:** A replacement detector plus a standing gate plus the cleanup, because there are three
  causes. `tools/planning_citation_gate.py`, vendored into BOTH sub-repositories: scans comment
  TEXT, matches anywhere inside a comment and never binds a token to a marker (so the repair cannot
  shrink its input); consumes string and char literals before looking for comments; never reads a
  Python docstring, so Click `--help` text is safe by construction; five rules with a 17-entry
  `TECHNICAL_VOCABULARY` allow-list applied PER MATCHED TOKEN, not per line (`AA-55` — the SDP
  unlock pair — and `CRC-32` were real false positives); exits 2 rather than 0 on a vacuous scan.
  Wired as a CI step in each sub-repo's existing primary workflow. Cleanup 1254 → 0: firestarter_fw
  794 → 0 (187 files), firestarter_app 460 → 0 (140 files); comment paragraphs that were pure
  planning narration deleted whole, paragraphs carrying hardware/datasheet/protocol facts restated
  without the identifier; `# noqa`, `# type: ignore` and the MIT header never touched. Three
  source-text pins re-derived with their own documented protocols (they hash source INCLUDING
  comments, so a comment edit invalidates them by construction): `sdp_expected_inventory.json`
  dd1ba1cc→cb254374, `eprom_v131_trace_inventory.json` ae279eba→df780397 (both re-derived with each
  gate module's OWN `_parse_arrays()`, every array name and entry count unchanged, landed in the
  same commit per the one-commit property those goldens document), and `test_serial_comm.py`'s
  ring-fence 8b778000→4aa34549. 887 lines of GSD planning document moved out of the firmware test
  tree (`RED-BASELINE.md` → `.planning/milestones/v1.22-phases/117-.../117-RED-BASELINE.md`).
- **Files changed:** `firestarter_fw/tools/planning_citation_gate.py` (new),
  `firestarter_fw/.github/workflows/{build,beta-build}.yml`, 95 firestarter_fw source files,
  `firestarter_fw/tests/golden/{sdp_expected_inventory,eprom_v131_trace_inventory}.json`;
  `firestarter_app/tools/planning_citation_gate.py` (new),
  `firestarter_app/.github/workflows/ci.yml`, 86 firestarter_app source files,
  `firestarter_app/tests/test_serial_comm.py`; `tools/citations/code_digest.py` (new, meta);
  `.planning/milestones/v1.22-phases/117-fix-remap-aware-0x0d-emitter-honest-completion-signal/117-RED-BASELINE.md`
  (relocated). Commits: meta `d90e1730`, firestarter_fw `876a223`, firestarter_app `c77ff2e`
  (residual closed by the operator's `088d2b7`, gitlinked by meta `735ecb89`).
- **Why not caught:** No gate existed for this class, in any of the three repositories. The nearest
  thing was Phase 154's one-shot corpus survey — an instrument for a single remediation, never wired
  to run again, and (per cause 1) incapable of catching this even if it had been. Code review could
  not catch it because a survivor reads as ordinary prose once its leading label is gone; the tell
  is a dangling sentence, not a keyword. Neither test suite catches it because comment content is
  not something either asserts on. Build, typecheck and lint are blind to comments by construction.
- **Recurrence guard:** (a) the two vendored `planning_citation_gate.py` detectors, which do NOT
  share the old detector's failure mode — proven non-vacuous against six planted controls including
  the two exact classes that produced the 612 survivors, and proven silent on a C string literal and
  on a Click docstring carrying the same words; (b) the CI steps that run them —
  `firestarter_fw/.github/workflows/build.yml` + `beta-build.yml` ahead of the build,
  `firestarter_app/.github/workflows/ci.yml` ahead of ruff. Both workflows already trigger on every
  branch and every pull request, and `main` is protected with pull-request-required in all three
  repositories, so a red check blocks the merge. BOTH sub-repository tips are gate-green
  (firestarter_fw `876a223`, firestarter_app `088d2b7`), so the step is a live gate, not one that
  lands red and gets ignored; (c) `tools/citations/code_digest.py` with its `--self-test`, which
  makes a future sweep's "no code changed" claim checkable rather than asserted; (d) this entry.
  Deliberately NOT a pytest module in either suite — the operator has ruled that tests must not scan
  source text, and the host suite's 24 source-scanning modules were removed for that reason in
  firestarter_app `088d2b7`.
- **Known uncovered surfaces (recorded so the next reader does not rediscover them):**
  **firestarter_fw has TWO test trees, and a one-tree check reports the wrong thing.**
  `test/native/avr/` (23 C++ Unity suites) was swept and is clean. `firestarter_fw/tests/` —
  30 `test_*.py` modules, 316 tests, 29 of which read a source file at runtime — had only its
  COMMENTS scanned, and those are clean; its DOCSTRINGS carry **530 planning-citation lines across
  31 modules**, and unlike the host suite's `@requires_fw` legs these DO execute in CI (`pytest
  tests/` is a firmware CI leg), so the narration is live and reachable. Deliberately not swept:
  the operator has not ruled on that suite, and it is a separate decision with its own risk profile
  (29 of those modules are the source-text contract scanners whose whole technique the operator has
  already retired on the host side). Also uncovered by design: Python docstrings generally,
  `.github/workflows/*.yml` comments in both sub-repos, and Markdown. Separately,
  `firestarter_fw/tests/test_checker_convention.py::test_scope_is_firmware_only` is RED and was red
  before this session — it asserts the repository directory is named `firestarter`, which the v1.38
  rename made `firestarter_fw`.
- **Transferable pattern (the reason to read this entry):** a detector whose own prescribed repair
  shrinks its input is SELF-CONFIRMING — it reports success as a consequence of a partial fix.
  Whenever a sweep, codemod or migration reports "N → ~0", check whether the repair operation could
  have moved instances out of the detector's view rather than out of the tree, and re-measure with
  an independent oracle that does not share the detector's anchor. Corollary: never let the
  remediation and the measurement key on the same structural feature.
---
