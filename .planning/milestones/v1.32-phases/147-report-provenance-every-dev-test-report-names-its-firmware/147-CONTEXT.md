# Phase 147: Report Provenance — every `dev test` report names its firmware - Context

**Gathered:** 2026-08-18
**Status:** Ready for planning

<domain>
## Phase Boundary

A `dev test` report identifies the firmware and board that produced it, so any community
report — this milestone's own included — can be attributed to a firmware version before any
write-path claim is made about it.

**In scope:** replacing `cli_handlers.py:2500`'s hardcoded `fw_board_identity=None` with a real,
prerelease-preserving identity captured inside the SAFE-02 orchestrator contract; an explicit
unknown rendering in the human-readable surfaces; a bumped-but-backward-compatible report schema
version; and the identity surfaced in the `[dev test]` issue parser(s). Host-only + the
devtest-triage skill script. PROV-01…PROV-06.

**Out of scope:** any firmware change (Phase 149 owns the only firmware-touching workstream);
`serial_comm.py`'s ring-fenced version-capture path (see D-05); the `write` handler in
`cli_handlers.py` (Phase 150 writes the same file — **never schedule 147 and 150 in the same
wave**); anything touching `0x0D`'s support status, the PROTOCOL-LEDGER, or gh#21/#32/#11/#12.

**Evidence Ceiling applies (binding, from `PROJECT.md` §Current Milestone: v1.32).** No AT28C part
exists in operator inventory. No criterion in this phase may require real silicon, assert the
`0x0D` write path is proven, graduate `0x0D` out of `UNVERIFIED`, change any `support_status`, or
be phrased as closing gh#21/#32/#11/#12.

</domain>

<decisions>
## Implementation Decisions

### Capture seam (PROV-01, PROV-02)

- **D-01: Piggyback the connection the hw-revision read already opens — no extra connection.**
  `HardwareManager.read_hardware_revision_value()` (`firestarter_app/firestarter/hardware.py:115`)
  already performs one SAFE-02-clean `find_and_connect` → `expect_ack` → `disconnect` cycle, and
  `_probe_port` sets `comm.firmware_identity` on that very connection **before** the revision ack
  is read (`serial_comm.py:412`, `:865`). Harvest both off that one connection. Zero extra serial
  connections, zero new firmware commands, `EpromOperator.comm` stays a transient per-operation
  connection torn down after every operator call (SAFE-02 intact).
  **Rejected:** a dedicated sibling `read_firmware_identity_value()` (opens a second connection to
  read a string the first already had); latching the identity on `EpromOperator` (zero extra
  connections and closest to PROV-01's literal intent, but adds mutable state to a class every
  command shares and touches `eprom_operations.py`).

- **D-02: Widen the existing method's return — do not add a near-duplicate sibling.** It has exactly
  **one** production call site (`cli_handlers.py:2501`); the churn is test mocks, not production
  code. One method, one handshake, no duplication.

- **D-03: Rename it and return a NamedTuple.** e.g.
  `read_programmer_identity() -> ProgrammerIdentity(hw_revision, fw_board_identity)`. Both values
  are `str | None`, so named fields — not positional unpacking — are what stop a silent swap from
  type-checking clean. `hardware.py` is scanned by **no** AST gate, so the rename breaks nothing
  structural; update the one call site plus the test mocks and docstrings that name it.

- **D-04: The two values fail independently — return the identity even if the revision read fails.**
  The identity comes from the connect ack; the revision from the command ack. A board built
  without `HARDWARE_REVISION` answers `MSG_ERR_UNKNOWN_CMD` to `CMD_HW_VERSION`, and today's
  `if is_ok:` else-branch returns `None`. It must still return
  `ProgrammerIdentity(hw_revision=None, fw_board_identity="3.0.0b19:uno")` — those non-standard
  boards are exactly the ones a triager most needs to identify. Two independent failure paths, both
  tested.

### PROV-03 — the requirement's stated premise is false (PROV-03, PROV-04)

- **D-05: The version gate is NOT touched.** PROV-03 and ROADMAP criterion #2 both assert
  `_probe_port`'s `[\d.x]+` truncation is what makes suffix-preservation impossible. **It is not.**
  That regex (`serial_comm.py:866`) feeds **only** `_validate_firmware_version`;
  `comm.firmware_identity` (`serial_comm.py:412`) holds the raw, untruncated
  `"<version>:<board>"` string decoded from the CAP-02 ack tail. Firmware side confirms:
  `FW_VERSION = VERSION ":" RURP_BOARD_NAME` with `VERSION "3.0.0b18"`
  (`firestarter/include/version.h:11`, `firestarter/src/firestarter.cpp:204-222`, 32-char cap).
  So the recorded string preserves `b19` **for free**. The version-capture path is GATE-1.8d
  ring-fenced and pinned by `test_fwguard.py` + `test_fw_version_guard.py`; editing it buys this
  phase nothing and risks refusing boards.
  **Note:** this supersedes the standing note that "the host cannot see the firmware prerelease
  suffix" — that observation was written against the retired `re.search(r"FW:\s*([\d.x]+)", fw_msg)`
  text-line probe, which CAP-02 replaced.

- **D-06: Hand-correct `REQUIREMENTS.md` PROV-03 and `ROADMAP.md` criterion #2 BEFORE planning.**
  A criterion whose premise is false is how a verifier produces a false RED — or worse,
  how an executor "fixes" a ring-fenced file to satisfy it. Restate both to the measured finding.
  Precedent: this milestone's own HEAD commit (`ae82391c`) corrects a charter claim.
  **Mechanic:** use **hand edits**. The GSD requirements/roadmap verbs reformat the whole file
  (`_normalizeMd` blast radius) — snapshot and diff.

- **D-07: Record verbatim, but scrub non-printables.** `serial_comm.py:412` decodes with
  `errors="replace"`, so a corrupt ack can yield U+FFFD — and the value reaches a public GitHub
  issue body via `submit.py`. Follow the existing `_sanitize_chip_token` precedent. A mangled
  identity stays **visible as evidence of a transport fault**, never silently converted to unknown.
  **Rejected:** a plausibility-clamp to unknown (mirrors CAP-01/CAP-03's "implausible → absent"
  convention but discards fault evidence and would reject a legitimate future format).

- **D-08: PROV-03's oracle is a differing-pair discrimination test.** Two identities differing
  **only** in prerelease suffix — `"3.0.0b11:leonardo"` vs `"3.0.0b19:leonardo"` — must land as two
  **different** values in the report JSON. That is literally the b11-vs-b12 discrimination the
  requirement exists to enable, and it is the shape that survives a later refactor; a single
  round-trip assertion passes vacuously if something later normalises suffixes away.
  Format precedent already exists in `tests/test_diagnostic_report.py:128,525` and
  `tests/test_parse_devtest_issue.py:374`.

- **D-09 (decided mechanically, precedent-settled): `SCHEMA_VERSION` 1.3 → 1.4**, with a rationale
  note in the existing per-bump comment block (`diagnostic_report.py:55-84`) stating that the bump
  marks a **value-population** change (a key that was unconditionally `null` now carries data), not
  a key addition. The 1.3 note explicitly **rejected** "a field-plus-JSON change with no version
  bump". Low friction: tests import `SCHEMA_VERSION` rather than hardcoding it, and both parsers
  accept `schema_version` by presence only. The frozen 1.1-era fixture in
  `tests/test_parse_devtest_issue.py` is already PROV-04's backward-compat oracle in shape.

### Unknown rendering (PROV-05)

- **D-10: The fenced JSON keeps `null`; the marker lives in the human surfaces.** Typed absence lets
  machine consumers test `is None`, and PROV-04's "old reports carry `null` and still parse" story
  stays **one** case instead of two. The explicit marker appears in the `rich` table
  (`diagnostic_report.py:512`) and the triage render. **PROV-05's "both report outputs" wording is
  tightened in the same hand-edit pass as D-06** — as written it reads as requiring a sentinel in
  the JSON.

- **D-11: A new identity-specific single-sourced constant** (e.g. `NOT_REPORTED = "not reported"`)
  beside the existing `NOT_MEASURED`, reused by both human surfaces. You don't *measure* a version
  string, and "not measured" conflates "asked and got nothing" with "never asked" — the exact
  ambiguity PROV-05 exists to remove. **Rejected:** reusing `NOT_MEASURED`; a reason-bearing
  `NOT-RUN: <reason>`-style marker (precedented by `sdp_hold_state`, but the realistic reason space
  is nearly empty — see D-13 — and it would need a reason threaded through the NamedTuple).
  Wording is unaffected by `check_diagnostic_report_claims.py`'s 14 forbidden patterns (all
  silicon-claim phrases), but re-run that gate.

- **D-12: Fix both identity fields in the rich table — `fw_board_identity` AND `hw_revision`.**
  `hw_revision` has the identical `str(None)` → `"None"` defect one row below. Shipping
  `"not reported"` above `"None"` invites a triager to read the difference as meaningful. They share
  an origin (the same connection) and the same honest-best-effort semantics. **`protocol` and the
  `chip_id` expected/actual pair are left alone** — `chip_id`'s `None` is genuinely informative (the
  part has no factory signature) and `protocol` can't be `None` on a submittable report.

- **D-13: The unknown leg is a defensive path, and is proven at two levels that actually run.**
  `_probe_port` **refuses** firmware reporting no identity (`FirmwareOutdatedError`), so in the field
  a successful `dev test` run essentially always has one. Prove it with (a) a render-level unit test
  building `AutoCapture(fw_board_identity=None)` directly and asserting the marker in **both** the
  rich table and `render_diff`, and (b) a `dev_test` handler test setting the existing
  `HardwareManager` mock to return `(None, None)` and asserting the marker reaches the rendered
  report **and** the saved JSON. Both legs reachable and seen to pass — not pre-authored RED that
  proves nothing.

### Triage attribution (PROV-06)

- **D-14: Labelled line in the normal case; marker plus a not-attributable clause when unknown.**
  PROV-06's purpose is not just showing a value — a triager needs to know whether any
  firmware claim can rest on this report. Mirror the existing "maintainer decision input — NEVER an
  auto-promotion trigger" labelling style in `render_diff`. **Rejected:** a machine-readable
  `attributable` boolean — a derived field nothing consumes, i.e. the same dead-data shape as
  `protect_on_after` that this milestone is separately having to reconcile (D-03 at milestone level).

- **D-15: The triage render carries `fw_board_identity` + `host_version`. `hw_revision` stays out.**
  A write-path finding is attributable only when host **and** firmware are both known, and
  "host `3.0.0b15` against unknown firmware" is precisely the half-answer that made gh#21
  undiagnosable. `hw_revision` is a coarse silkscreen bucket that cannot discriminate the operator's
  Rev 2.2 / Rev 2.0 / modified Rev 0 boards — it would add a line that looks authoritative while
  answering nothing.

- **D-16: BOTH `[dev test]` parsers get the field.** PROV-06 names one parser; there are two:
  - `firestarter_app/tools/parse_devtest_issue.py` — `render_diff()` (~line 192), the named surface,
    with committed CI-run tests.
  - `.claude/skills/devtest-triage/scripts/devtest_issues.py` — the `show` render (~lines 330-336),
    which is what triage actually reaches for. It prints `host` and `hw` but no firmware identity,
    and prints `hw None` today.

  **Skills own their scripts** — no importing from `firestarter_app/tools`. Two deliberate edits,
  not a shared import. Fix the skill's own `hw None` rendering in the same pass (consistent with
  D-12).

- **D-17: One action-oriented clause; NO schema-version ordering logic.** A `null` identity means
  two things for triage (old report: the host build never captured it, a fresh run fixes it;
  post-bump report: capture *failed*). Emit a single clause true under either reading and pointing
  at the action — not attributable, ask for a fresh run on a current host. Both parsers deliberately
  accept `schema_version` **by presence only, never by value**, and a live fixture carries
  `schema_version: "9.9-future"` (`tests/test_parse_devtest_issue.py:138`) that any ordering
  comparison would have to survive.

### Claude's Discretion

- Exact constant name and marker wording for D-11 (`NOT_REPORTED` / `"not reported"` is a
  suggestion, not a lock) — keep it single-sourced and outside the claim-gate vocabulary.
- Exact `ProgrammerIdentity` NamedTuple name and field order (fields must be named — D-03).
- Exact phrasing of the not-attributable clause (D-14/D-17), subject to the claim gate.
- Where the capture sits relative to `run_plan`: **keep it where it is today** (before the plan
  runs, `cli_handlers.py:2501`) unless research finds a reason to move it.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone charter & requirements (binding)
- `.planning/PROJECT.md` §"Current Milestone: v1.32" — D-01…D-04, the Evidence Ceiling, the
  finding that opens the milestone (`cli_handlers.py:2500`), workstream table.
- `.planning/REQUIREMENTS.md` §"Report Provenance (PROV)" — PROV-01…PROV-06. **PROV-03 and PROV-05
  are hand-corrected by this phase per D-06/D-10.**
- `.planning/ROADMAP.md` §"v1.32 — AT28C Write-Path Root Cause & Report Provenance" — sequencing
  spine, locked decisions, must-not-do list; §"Phase 147" success criteria (**criterion #2
  hand-corrected per D-06**).
- `.planning/ROADMAP.md` §"Phase 999.29" — the AT28C256 write-path backlog item this phase
  *unblocks diagnosis of* but does **not** retire.

### The defect and its call site
- `firestarter_app/firestarter/cli_handlers.py:2491-2504` — the `AutoCapture(...)` construction with
  the hardcoded `fw_board_identity=None` and its honest explanatory comment (which D-01 supersedes).
- `firestarter_app/firestarter/hardware.py:115-148` — `read_hardware_revision_value()`, the
  SAFE-02-clean single-read precedent this phase widens (D-02/D-03).

### The identity's transport path
- `firestarter_app/firestarter/serial_comm.py:370-440` — the `MSG_OK_READY` / CAP-01/02/03
  length-discriminated decode; `:412` sets `firmware_identity` untruncated.
- `firestarter_app/firestarter/serial_comm.py:815-890` — `_probe_port`; `:866` is the `[\d.x]+`
  version-gate extraction that D-05 leaves alone; the identity-absent refusal that makes D-13's leg
  defensive.
- `firestarter/include/version.h:11` and `firestarter/include/firestarter.h:54` — `VERSION
  "3.0.0b18"`, `FW_VERSION = VERSION ":" RURP_BOARD_NAME`.
- `firestarter/src/firestarter.cpp:161-225` — the CAP-02 identity-tail emit and its 32-char cap.
  **Read-only for this phase — Phase 147 changes no firmware.**

### Report model & rendering
- `firestarter_app/firestarter/diagnostic_report.py` — `SCHEMA_VERSION` + per-bump rationale block
  (`:55-84`), `NOT_MEASURED` (`:85`), `AutoCapture` (`:98-131`), `is_submittable` (`:183`),
  `dedup_fingerprint` (`:222`), `to_dict` (`:408`, `:492`), `render` (`:505-560`).
- `firestarter_app/tools/parse_devtest_issue.py` — `render_diff()` (~`:192`), PROV-06's named
  surface.
- `.claude/skills/devtest-triage/scripts/devtest_issues.py` — the second parser surface (`show`
  render ~`:325-340`). `.claude/skills/` is un-ignored in `.gitignore` and therefore committable,
  but is **not yet committed** — a plan touching it starts from an untracked baseline.
- `.claude/skills/devtest-triage/SKILL.md` — the triage procedure that consumes that output.

### Gates that must stay green (and one that fails OPEN)
- `firestarter_app/tools/check_devtest_orchestrator.py` — the SAFE-02/SAFE-03 AST gate. Scans
  `chip_test.py` and `submit.py` in full, and `cli_handlers.py` **only** through the
  `_HANDLER_FUNCTION_NAMES` frozenset (`:152-165`). Denies VPP-set calls, dict literals carrying
  wire keys (`cmd`, `algorithm`, `vpp_mv`, `bus-config`, `pin-count`, `chip-id`, `flags`,
  `pulse-delay`), `force=True` / `"--force"`, and broad excepts.
  **⚠ Trap:** a new private helper added beside `dev_test` is **not scanned** unless its name joins
  `_HANDLER_FUNCTION_NAMES` — the gate fails **OPEN** on it. D-01 keeps the new code in
  `hardware.py`, which this gate does not scan at all; `{"state": COMMAND_HW_VERSION}` is also
  outside the denied wire-key vocabulary.
- `firestarter_app/tools/check_diagnostic_report_claims.py` — string-literal claim scanner over
  `diagnostic_report.py` (14 silicon-claim patterns). Re-run after adding the D-11 marker.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`HardwareManager.read_hardware_revision_value()`** (`hardware.py:115`) — the orchestrator-safe
  read pattern: `find_and_connect` → `expect_ack` → `disconnect` in `finally`, returning data or an
  honest `None`. Already the auto-capture source for `AutoCapture.hw_revision`. **This is the method
  D-02/D-03 widen and rename.**
- **`SerialCommunicator.firmware_identity`** — the raw `"<version>:<board>"` string, set on **every**
  successful connect. Requires no new command, no new flag, and no firmware change.
- **`NOT_MEASURED`** (`diagnostic_report.py:85`) — the existing honest-fallback constant convention
  D-11's new constant sits beside.
- **The `SCHEMA_VERSION` per-bump rationale block** (`:55-84`) — the documented format D-09's note
  extends; it also contains 1.2's and 1.3's own reasoning about presence-only parsing.
- **Format precedent for the field** — `tests/test_diagnostic_report.py:128,525` and
  `tests/test_parse_devtest_issue.py:374` already use `"3.0.0b10:leonardo"` /
  `"3.0.0b11:leonardo"`, so the combined single-string shape is settled; do **not** split it into
  separate version and board keys (that would be a schema key *addition*, changing PROV-04's story).
- **The frozen 1.1-era fixture** in `tests/test_parse_devtest_issue.py` — PROV-04's backward-compat
  oracle already exists in shape.
- **`_sanitize_chip_token`** (in `_HANDLER_FUNCTION_NAMES`) — the sanitising precedent D-07 follows.

### Established Patterns
- **Populating this field has zero blast radius on the two things that looked risky.**
  `dedup_fingerprint` deliberately **excludes** `fw_board_identity` (it hashes only chip, protocol,
  and per-step op/verdict/classification), so filling it breaks neither dedup continuity nor the
  N-agreeing promotion ladder. `is_submittable` gates on `chip` + `protocol` + `host_version` only,
  so no submittability outcome changes. Both are pinned by `tests/test_provenance.py`.
- **`diagnostic_report.py` is orchestrator-only by contract** — it imports no serial/hardware class
  and never fetches identity. The identity must stay **threaded in** from the handler; do not let
  the fix leak a transport import into this module (RESEARCH Pitfall 1).
- **Absent-chip hard-fail negative assertion.**
  `tests/test_dev_test_cmd.py::test_absent_chip_still_hard_fails_before_hardware` asserts
  `read_hardware_revision_value.assert_not_called()` as its load-bearing check. After the D-03
  rename, that assertion must follow the new name — otherwise the absent-chip false-green trap
  reopens (an exit-code-only test proves nothing here).
- **`str(None)` → `"None"`** is the whole of the PROV-05 defect in the rich table; the same shape
  exists in the skill's `show` render.
- **No render snapshot pins the report.** `tests/__snapshots__/` holds only
  `test_characterization.ambr`; nothing in `tests/golden/` references `fw_board_identity`. No
  re-baselining needed.

### Integration Points
- `cli_handlers.py:2501` — the single production call site; becomes the NamedTuple unpack.
- `diagnostic_report.py:402` (`to_dict`) — key already present, value becomes populated (D-09).
- `diagnostic_report.py:512-513` — the two rich-table rows D-12 fixes.
- `tools/parse_devtest_issue.py::render_diff` and
  `.claude/skills/devtest-triage/scripts/devtest_issues.py::show` — D-14/D-15/D-16/D-17.

### Execution mechanics (not a decision — a precondition)
- **Sub-repo branch base.** `firestarter_app` is currently checked out on
  `gsd/v1.31-27c-programming-algorithm-fidelity`. Per the v1.32 charter, sub-repo branches fork off
  their **`beta` tips**, which now carry v1.31 (app PR #51, firmware PR #52, both merged 2026-08-18)
  and the beta cut those merges fired — app **3.0.0b21**, firmware **3.0.0b19**. Create/check out
  the v1.32 app branch off `origin/beta` before dispatching any executor. Those PRs were squashed,
  so `git merge-base --is-ancestor` against the v1.31 branch is a **false negative** — verify by
  content, not ancestry.
- **One-writer-per-file.** Phase 150 (`write --sdp-relock`) also writes `cli_handlers.py`. 147 and
  150 must never be scheduled in the same parallel wave.
- **Meta-repo working tree** is dirty (`.gitignore`, both submodule gitlinks, untracked
  `.claude/`, `package*.json`). Stage specific files only.

</code_context>

<specifics>
## Specific Ideas

- The b11-vs-b19 pair is not an arbitrary test value — it is the exact discrimination gh#21/#32
  need. Both reports state host `3.0.0b15` against an **unknown** firmware, and so cannot be
  distinguished from a board lacking the entire Phase-117–120 `0x0D` fix stack (FIX-01 `/WE`-inhibit
  routing, FIX-03 A16–A18 staleness, FIX-06 the completion-vs-data-landed conflation that is gh#11's
  actual shape). Keep that framing in the test names and the not-attributable wording.
- The honest comment currently at `cli_handlers.py:2491-2496` should be **replaced, not deleted** —
  it correctly states why `EpromOperator.comm` cannot serve, and the replacement should say why the
  hw-revision connection can.

</specifics>

<deferred>
## Deferred Ideas

- **Suffix-aware firmware version gating.** Widening `_validate_firmware_version` to compare
  prerelease suffixes (via `packaging.version`, already a dependency through
  `_maybe_auto_route_to_pre`) would make a future "requires firmware ≥ 3.0.0bN" gate possible. D-05
  explicitly leaves the ring-fenced path alone; no v1.32 requirement asks for it. Revisit when a
  phase actually needs per-beta gating — and prefer detect-over-gate (require an observable ack) as
  v1.22 Phase 120 D-15 did.
- **A reason-bearing unknown marker** (`sdp_hold_state`'s `NOT-RUN: <reason>` shape) for the identity
  field — richer triage signal, but the reason space is near-empty while `_probe_port` refuses
  identity-less firmware. Revisit if that refusal is ever relaxed.
- **A machine-readable `attributable` flag** in the report — rejected as dead data today (D-14);
  worth revisiting only when a consumer exists that would filter on it.
- **Extending the explicit-unknown treatment to `protocol` / `chip_id` renderings** — deliberately
  out (D-12), since `chip_id`'s `None` is informative.

### Reviewed Todos (not folded)

20 pending todos were cross-referenced against Phase 147. **None folded** — every match scored on
keyword noise (`firmware`, `phase`, `version`, `blank`, `null`), and folding any of them would be
scope creep into a report-provenance phase:

- *Skip VPP error/warning checks when VPP is unused* (0.9) — firmware, unrelated.
- *CONFIG_VERSION is not bumped when a calibration default changes* (0.9) — firmware EEPROM
  calibration versioning, unrelated to the report schema version.
- *Prove the PlatformIO dev-tools build flag fails CLOSED* (0.9) — firmware build gating.
- *FM1608 byte 0 write never lands* (0.7) — firmware register cache elision.
- *AT28C256 write-path failure (gh#20)* (0.6) — Backlog 999.29, explicitly **not** retired by v1.32
  and blocked by the Evidence Ceiling.
- *avrdude MCU-detection fallback*, *`build_db_diff`'s `ladder_state`*, *COBS decoder frame
  deadline*, *GSD plan-scan loose regex*, *board photography / MODIFICATIONS.md*, *Phase 130 record
  gate*, *infoic flags bits 14/15*, *JP4 labels*, *`response_code` log macro*, *dead `json_init()`*,
  *JP5 dead renderer*, *DATA_BUFFER_SIZE spike* (0.2–0.6) — all outside this phase.
- *Reply on gh#12 / correct the b14 release notes* (0.6) → already mapped to **Phase 152** (OUT-01).
- *Land `write --sdp-relock`* (0.6) → already mapped to **Phase 150** (Backlog 999.28, promoted).

</deferred>

---

*Phase: 147-Report Provenance — every `dev test` report names its firmware*
*Context gathered: 2026-08-18*
