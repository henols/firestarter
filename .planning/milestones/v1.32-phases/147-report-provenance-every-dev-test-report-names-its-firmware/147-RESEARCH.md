# Phase 147: Report Provenance — every `dev test` report names its firmware - Research

**Researched:** 2026-08-18
**Domain:** Python host-side instrumentation — identity capture off an existing serial handshake, report-model schema versioning, and three human-readable render surfaces
**Confidence:** HIGH (every load-bearing claim measured on disk this session; zero external dependencies)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Capture seam (PROV-01, PROV-02)**

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

- **D-04: The two values fail independently — return the identity even when the revision read
  fails.** The identity comes from the connect ack; the revision from the command ack. A board built
  without `HARDWARE_REVISION` answers `MSG_ERR_UNKNOWN_CMD` to `CMD_HW_VERSION`, and today's
  `if is_ok:` else-branch returns `None`. It must still return
  `ProgrammerIdentity(hw_revision=None, fw_board_identity="3.0.0b19:uno")` — those non-standard
  boards are exactly the ones a triager most needs to identify. Two independent failure paths, both
  tested.

**PROV-03 — the requirement's stated premise is false (PROV-03, PROV-04)**

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

- **D-06: Hand-correct `REQUIREMENTS.md` PROV-03 and `ROADMAP.md` Phase 147 criterion #2 BEFORE
  planning.** A criterion whose premise is false is how a verifier produces a false RED — or worse,
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

**Unknown rendering (PROV-05)**

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

**Triage attribution (PROV-06)**

- **D-14: Labelled line in the normal case; marker plus an explicit not-attributable clause when
  unknown.** PROV-06's purpose is not just showing a value — a triager needs to know whether any
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

### Deferred Ideas (OUT OF SCOPE)

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
- All 20 reviewed pending todos — **none folded** (CONTEXT.md §Reviewed Todos).

### Scope fences (binding)

- Phase 147 changes **NO firmware**. `firestarter/` is read-only reference.
- Do NOT touch `_probe_port` / `_validate_firmware_version` (D-05, GATE-1.8d ring-fenced).
- **Evidence Ceiling:** no criterion may require real AT28C silicon, assert the `0x0D` write path is
  proven, graduate `0x0D` out of `UNVERIFIED`, change any `support_status`, or be phrased as closing
  gh#21/#32/#11/#12.
- Phase 150 also writes `cli_handlers.py` — 147 and 150 must never share a parallel wave.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PROV-01 | A `dev test` report records the firmware version and board identity of the programmer that produced it, in place of today's unconditional `null`. | §Verified Findings F-01/F-02/F-03 (`comm.firmware_identity` is populated and readable on the exact connection `read_hardware_revision_value` already opens); §Code Examples E-1/E-2 |
| PROV-02 | That capture happens without violating the SAFE-02 orchestrator-only contract — no extraneous connection, `EpromOperator.comm` stays transient. | §Verified Findings F-04 (`hardware.py` is outside every AST gate's scan scope); §Gate Verification G-1; §Validation Architecture PROV-02 row |
| PROV-03 | The recorded firmware string preserves the prerelease suffix (`3.0.0b19` distinguishable from `3.0.0b11`). | §Verified Findings F-05 (D-05 confirmed: raw untruncated identity; the `[\d.x]+` regex builds a separate local); D-08 differing-pair oracle |
| PROV-04 | Schema version bumped; earlier reports carrying `fw_board_identity: null` still parse. | §Verified Findings F-06/F-07 (`SCHEMA_VERSION = "1.3"` at `:55`; a `"1.4"` body **already** parses on BOTH parsers today — measured); §Validation Architecture Wave 0 gap W-3 |
| PROV-05 | Null identity renders as an explicit unknown in the human surfaces and in the issue parser — never blank, never bare `None`. | §Verified Findings F-08 (the two `str(None)` rows at `:518-519`); F-13 (skill prints `hw None`); §Pitfall P-4 (three surfaces, one string, no shared import) |
| PROV-06 | The `[dev test]` issue parser surfaces the firmware identity so a triager can attribute a report unasked. | §Verified Findings F-09 **(DRIFT: `render_diff` has ZERO tests)**, F-12/F-13/F-14; §Validation Architecture Wave 0 gaps W-2/W-4 |
</phase_requirements>

## Summary

This phase is unusually low-risk for its leverage. Every claim CONTEXT.md advances as measured
**holds on disk today**, at or within one line of the stated coordinates, with one substantive
exception and several additions the planner must act on. The mechanism is already there: the
CAP-02 `MSG_OK_READY` ack carries `"<version>:<board>"` untruncated onto `comm.firmware_identity`
**before** the dispatch switch runs, and `HardwareManager.read_hardware_revision_value()` already
holds a live reference to that communicator. The work is a return-type widening in `hardware.py`,
one call-site unpack, a schema-version bump with a rationale note, one new marker constant, and
three render edits — not a new capability.

The three findings the planner most needs are all about **oracles, not implementation**:
(1) `tools/parse_devtest_issue.py::render_diff` — PROV-06's named surface — has **zero tests
anywhere in the repo**, contradicting CONTEXT.md's "with committed CI-run tests"; (2) the
devtest-triage skill script has no test harness at all, and coupling the app suite to a meta-repo
path would create a fail-open gate, so it needs a `checkpoint:human-verify` with a committed fixture
body instead; (3) the D-11 "single-sourced constant" cannot literally be single-sourced —
`tools/parse_devtest_issue.py` is **stdlib-only by stated contract** and the skill script cannot
import from the app at all, so the same string must exist in three modules with a **value-parity
test** standing in for the import. Separately, D-04's mechanism is not merely plausible but
**verified in the firmware source**: `MSG_OK_READY` (identity-bearing) is emitted before the
`#ifdef HARDWARE_REVISION`-gated `case CMD_HW_VERSION`, and `_validate_hardware_revision` returns
early for a command with no `bus-config`, so a non-`HARDWARE_REVISION` board genuinely reaches the
`if is_ok:` else-branch with a good identity in hand.

Two mechanical traps deserve naming. The D-03 rename is **safe from silent false-greens** —
every `hardware_manager` mock in the suite is `Mock(spec=HardwareManager)`, which raises
`AttributeError` on an attribute the spec no longer has, so the rename fails loudly rather than
turning `assert_not_called()` vacuous (I verified spec strictness empirically). But if the plan adds
any new `_`-prefixed module-level helper in `cli_handlers.py` referenced from `dev_test`'s body, a
**hard-equality** assertion in `tests/test_check_devtest_orchestrator.py` goes RED until three
files change together. Keep every new line in `hardware.py` and `diagnostic_report.py` and that
trap never arms.

**Primary recommendation:** widen `read_hardware_revision_value` → `read_programmer_identity()`
returning a `NamedTuple` **inside `hardware.py`**, harvesting `comm.firmware_identity` (scrubbed for
non-printables, in that same module) alongside the existing revision ack, before the `finally:
comm.disconnect()`; add no new helper to `cli_handlers.py`; bump `SCHEMA_VERSION` to `"1.4"`; add one
marker constant in `diagnostic_report.py` plus a value-parity-tested twin in each of the two
parsers; and build the four missing oracles (`test_hardware.py` unit legs, `render_diff` tests, a
null-carrying frozen fixture, and a skill-script human-verify) as Wave 0 work.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Emit the firmware/board identity on the wire | Firmware (`firestarter/`) | — | Already shipped as the CAP-02 `MSG_OK_READY` tail. **Read-only this phase — no firmware change.** |
| Decode the identity off the ack | Host transport (`serial_comm.py`) | — | Already shipped at `:412`. GATE-1.8d ring-fenced — **do not edit** (D-05). |
| Harvest the identity from a live connection | Host hardware layer (`hardware.py`) | — | It is the only module that legitimately holds a `SerialCommunicator` for a one-shot energize/query read. Owning the harvest here keeps the transport import out of the orchestrator (SAFE-02) and out of every AST gate's scan scope. |
| Scrub the harvested string (D-07) | Host hardware layer (`hardware.py`) | — | Sanitise at the boundary where the untrusted bytes first become a Python `str`. Placing it in `cli_handlers.py` arms the `_HANDLER_FUNCTION_NAMES` equality trap (P-1); placing it in `diagnostic_report.py` breaks that module's no-transport-knowledge contract. |
| Thread the identity into the report model | Handler (`cli_handlers.py::dev_test`) | — | The existing `AutoCapture(...)` construction site. One keyword changes; no new helper. |
| Hold the identity as typed data | Report model (`diagnostic_report.py`) | — | `AutoCapture.fw_board_identity` already exists and is `str | None`; only its value population changes. |
| Render the explicit unknown, console | Report model (`diagnostic_report.py::render`) | — | The `rich` table is the only in-process human surface; it already sources from `to_dict()` (RPT-01). |
| Render the identity, app triage parser | Tooling (`tools/parse_devtest_issue.py`) | — | Stdlib-only by contract; owns its own marker literal. |
| Render the identity, skill triage parser | Skill (`.claude/skills/devtest-triage/scripts/`) | — | "Skills own their scripts" — no import from the app; owns its own marker literal. |
| Keep the three marker strings equal | Test suite (`tests/`) | — | A parity assertion replaces the import that architecture forbids. |

## Verified Findings — CONTEXT.md claim audit

Every coordinate below was opened this session on the live working tree
(`firestarter_app` @ `3cf429f`, `firestarter` @ current gitlink).

| # | CONTEXT.md claim | Status | Measured |
|---|------------------|--------|----------|
| F-01 | `cli_handlers.py:2491-2504` — `AutoCapture(...)` with hardcoded `fw_board_identity=None` and the honest comment | **HOLDS exactly** | Comment `:2494-2500`; `auto_capture = AutoCapture(` `:2501`; `fw_board_identity=None` `:2503`; `hw_revision=app.hardware_manager.read_hardware_revision_value(),` `:2504`; closing `)` `:2507` `[VERIFIED: sed -n 2493,2508p]` |
| F-02 | `hardware.py:115-148` — `read_hardware_revision_value` | **HOLDS exactly** | `def read_hardware_revision_value(self, flags: int = 0) -> Optional[str]:` at `:115`; body `find_and_connect` → `expect_ack` → `if is_ok: return msg` / else `return None`; `except (ProgrammerNotFoundError, SerialError, SerialTimeoutError)` → `return None`; `finally: if comm: comm.disconnect()` ending `:147` `[VERIFIED]` |
| F-03 | `find_and_connect` returns the probed communicator with `firmware_identity` set | **HOLDS** | `find_and_connect` `:922`, `return communicator` `:968`; `_probe_port` `:815`, sets nothing after `communicator.programmer_info = msg` `:890`. `firmware_identity` set at `:412` during the setup-ack decode, i.e. **before** the caller's second `expect_ack()`. `disconnect()` clears `programmer_info` (`:649`) but **not** `firmware_identity` `[VERIFIED]` |
| F-04 | `check_devtest_orchestrator.py` does not scan `hardware.py`; `cli_handlers.py` scanned only via `_HANDLER_FUNCTION_NAMES` | **HOLDS** | Targets are exactly `firestarter/chip_test.py` (full), `firestarter/cli_handlers.py` (scoped, `_HANDLER_FUNCTION_NAMES` at `:152-181`), `firestarter/submit.py` (full) — `main()` `:547-625`. Live run prints `PASS: scanned ../firestarter/chip_test.py, ../firestarter/cli_handlers.py, ../firestarter/submit.py` `[VERIFIED: gate executed, EXIT=0]` |
| F-05 | D-05: the `[\d.x]+` regex feeds only `_validate_firmware_version`; `firmware_identity` is raw | **HOLDS exactly** | `:865 identity = communicator.firmware_identity`; `:866 version_match = re.match(r"[\d.x]+", identity) if identity else None`; `:884 _validate_firmware_version(version_match.group(0), ...)`. The regex result is a **separate local**; `communicator.firmware_identity` is never reassigned `[VERIFIED]` |
| F-06 | `diagnostic_report.py:55-85` — `SCHEMA_VERSION` + per-bump block + `NOT_MEASURED` | **HOLDS exactly** | `SCHEMA_VERSION = "1.3"` at `:55`; 1.1/1.2/1.3 rationale comments `:56-84`; `NOT_MEASURED = "not measured"` at `:85` `[VERIFIED]` |
| F-07 | Both parsers accept `schema_version` by presence only | **HOLDS — and pre-verified for `"1.4"`** | `parse_devtest_issue.py:99 if "schema_version" not in obj:`; live fixture `"9.9-future"` at `tests/test_parse_devtest_issue.py:138`. I fed a synthesized `schema_version: "1.4"` body to **both** parsers offline; both parsed and rendered it without error `[VERIFIED: executed both CLIs]` |
| F-08 | `diagnostic_report.py:499-554` `render`, two `str(None)` rows | **HOLDS exactly** | `def render` `:505`; `table.add_row("fw_board_identity", str(ac["fw_board_identity"]))` `:518`; `table.add_row("hw_revision", str(ac["hw_revision"]))` `:519`. `host_version` `:517` is always populated so needs no marker `[VERIFIED]` |
| F-09 | `tools/parse_devtest_issue.py::render_diff()` "~line 192 … with committed CI-run tests" | **⚠ PARTIAL DRIFT** | `def render_diff(` is at **`:192`** exactly. But a repo-wide grep for `render_diff` returns **only two hits: its definition (`:192`) and its single call site (`:251`)**. `tests/test_parse_devtest_issue.py` (22 tests) imports `_MAX_BODY_BYTES, count_agreeing, extract_db_diff, parse_devtest_body` — **not `render_diff`**. PROV-06's named surface is **completely untested today** `[VERIFIED: grep -rn render_diff]` |
| F-10 | `dedup_fingerprint` excludes `fw_board_identity`; `is_submittable` ignores it | **HOLDS** | `is_submittable` `:195 return bool(ac.chip) and bool(ac.protocol) and bool(ac.host_version)`; `submit.py:585-595` names the same three fields. Populating the identity changes no submittability outcome and no dedup hash `[VERIFIED]` |
| F-11 | `tests/test_dev_test_cmd.py::test_absent_chip_still_hard_fails_before_hardware` carries the load-bearing `assert_not_called()` | **HOLDS** | `:845 app.hardware_manager.read_hardware_revision_value.assert_not_called()`; docstring `:831` names it load-bearing `[VERIFIED]` |
| F-12 | `.claude/skills/devtest-triage/scripts/devtest_issues.py` `show` render `~:325-340` | **HOLDS exactly** | `print(f"  host        {auto.get('host_version')}   "` `:332` / `f"hw {auto.get('hw_revision')}")` `:333`. `cmd_show` `:294` `[VERIFIED]` |
| F-13 | The skill prints `hw None` and no firmware identity | **HOLDS — reproduced** | Ran the skill offline against a synthesized null-identity body; output line: `  host        3.0.0b21   hw None`. No firmware-identity line anywhere in the render `[VERIFIED: executed]` |
| F-14 | `.claude/skills/` is un-ignored and committable, "but not yet committed" | **HOLDS, with a precondition CONTEXT.md omits** | `git ls-files .claude` → **empty** (nothing tracked). And the un-ignore itself is **uncommitted**: `git diff .gitignore` shows `-.claude/` → `+.claude/*` / `+!.claude/skills/` still in the working tree. A plan touching the skill script must land that `.gitignore` change (or `git add -f`) or the file cannot be committed at all |
| F-15 | Sub-repo branch base / squash caution | **HOLDS in intent; the squash caution does NOT apply to the app** | See §Sub-Repo Branch Precondition. App PR #51 landed as a **true merge** (`91c2add` has two parents, the second being `3cf429f`), so `--is-ancestor` returns **TRUE** here. Verify by content regardless |
| F-16 | D-04's mechanism ("a board without `HARDWARE_REVISION` answers `MSG_ERR_UNKNOWN_CMD` and the `if is_ok:` else-branch returns None") | **CONFIRMED IN FIRMWARE SOURCE** | `firestarter/src/firestarter.cpp` emits `LOG_OK_ID_BYTES(MSG_OK_READY, _ready, ...)` at `:227` — **before** the dispatch switch. `case CMD_HW_VERSION:` at `:338` sits inside `#ifdef HARDWARE_REVISION`, so a non-`HARDWARE_REVISION` build falls to `default:` → `LOG_ERROR_ID_U8(MSG_ERR_UNKNOWN_CMD, ...)`. On that build `_ready[2] = 0xFE` (REVISION_UNKNOWN), and `_validate_hardware_revision` (`serial_comm.py:772-793`) **returns immediately** because `{"state": COMMAND_HW_VERSION}` carries no `bus-config`. So the probe succeeds with a good identity and the second ack fails — D-04's leg is genuinely field-reachable `[VERIFIED: firmware + host source]` |
| F-17 | `FirmwareOutdatedError` reaching `read_hardware_revision_value` | **New — it is already caught** | `FirmwareOutdatedError`, `HardwareRevisionUnsupportedError` and `ProgrammerNotFoundError` are all `SerialError` subclasses (`exceptions.py:19-37`), so the existing `except (ProgrammerNotFoundError, SerialError, SerialTimeoutError)` clause swallows them → `return None` today. `ProtocolNotImplementedError` is **not** a `SerialError` (it derives from `EpromOperationError`, `:68`) but is raised only on `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` (`serial_comm.py:610`), unreachable for a bare `{"state": 15}` command. **The widened method must keep this clause and return `ProgrammerIdentity(None, None)`, not `None`** |

### Corrections the planner must carry forward

1. **`render_diff` is untested.** CONTEXT.md's "with committed CI-run tests" is wrong (F-09). PROV-06's
   automated oracle must be **created**, not extended. Treat as Wave 0.
2. **The `.gitignore` un-ignore is uncommitted** (F-14). It is a hard precondition for committing any
   skill-script change, and it lives in the **meta** repo working tree alongside two submodule
   gitlinks and untracked `.claude/` — stage the single file, never `git add -A`.
3. **D-11's "single-sourced" is architecturally impossible across all three surfaces** — see P-4.
4. `hardware.py:115` is the `def` line, so the method body runs `:115-147`; CONTEXT.md's `:115-148`
   is inclusive of the following blank line. Cosmetic only.

## Standard Stack

### Core

**No new dependency is required or permitted by this phase.** Every mechanism is already installed.

| Library / module | Version | Purpose | Why standard |
|------------------|---------|---------|--------------|
| `typing.NamedTuple` (stdlib) | py3.9+ | D-03's `ProgrammerIdentity` | In-repo precedent: `firestarter/frame_vectors.py:20 class FrameVector(NamedTuple)`. Named-field access is what makes a two-`Optional[str]` return swap-proof `[VERIFIED: grep]` |
| `pytest` | 9.1.1 local / `>=8.0` pinned | every automated oracle | The project's only test runner; `[tool.pytest.ini_options]` in `pyproject.toml` `[VERIFIED: pytest --version]` |
| `rich.table.Table` | 14.x | the console render surface | Already the render target; `diagnostic_report.render` imports it locally `[VERIFIED]` |
| `unittest.mock.Mock(spec=…)` (stdlib) | — | every `hardware_manager` double | Spec strictness is the mechanism that makes the D-03 rename fail loudly — see P-2 `[VERIFIED: executed]` |
| `ruff` | 0.16.3 | lint + format gate | CI scope is `firestarter/ tests/` **only** — `tools/` is not linted `[VERIFIED: ci.yml:215,218]` |
| `mypy` | 2.3.1 | watermark gate | argv is `[sys.executable, "-m", "mypy", "firestarter/", "tests/"]` — `tools/` is **not** type-checked `[VERIFIED: check_mypy_watermark.py:115]` |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `NamedTuple` | `@dataclass(frozen=True)` | Equivalent field safety, but `hardware.py` imports no `dataclasses` today and `frame_vectors.py` already sets the `NamedTuple` precedent. Prefer the precedent. |
| `NamedTuple` | a 2-tuple with a type alias | Rejected by D-03: positional unpacking of two `Optional[str]`s type-checks clean when swapped. |
| Marker constant imported into both parsers | three literals + a parity test | Forced by architecture (P-4), not chosen. |

**Installation:** none. Confirm the editable install only:

```bash
cd /workspaces/firestarter_app && pip install -e '.[test]' && python3 -c "import firestarter; print(firestarter.__version__)"
```

## Package Legitimacy Audit

**This phase installs zero external packages.** No `npm`/`pip`/`cargo` addition is proposed, and none
is needed — `typing.NamedTuple` is stdlib and every test/lint tool is already pinned in
`pyproject.toml`'s `[project.optional-dependencies] test` extra.

| Package | Registry | Verdict | Disposition |
|---------|----------|---------|-------------|
| *(none proposed)* | — | — | — |

**Packages removed due to `[SLOP]` verdict:** none.
**Packages flagged as suspicious `[SUS]`:** none.

If a plan proposes any new dependency, that is a scope escape — the phase is host-only instrumentation
over shipped mechanisms.

## Architecture Patterns

### System Architecture Diagram

```
                    ┌──────────────────────────────────────────────────────────┐
                    │  FIRMWARE (firestarter/) — READ-ONLY THIS PHASE           │
                    │                                                          │
   CMD_HW_VERSION ─▶│  firestarter.cpp: setup path                             │
   {"state": 15}    │    └─▶ LOG_OK_ID_BYTES(MSG_OK_READY, _ready)  ── ACK #1 ──┼──┐
                    │          [bufsz u16][hw_rev u8][ver_len u8][ver bytes]…   │  │
                    │                                                          │  │
                    │  firestarter.cpp:333  dispatch switch                    │  │
                    │    #ifdef HARDWARE_REVISION                              │  │
                    │      case CMD_HW_VERSION → MSG_OK_REV      ─── ACK #2 ────┼──┤
                    │    #else  default: → MSG_ERR_UNKNOWN_CMD   ─── ACK #2 ────┼──┤
                    └──────────────────────────────────────────────────────────┘  │
                                                                                  │
   ┌──────────────────────────────────────────────────────────────────────────────┘
   │  HOST TRANSPORT — serial_comm.py  ⚠ GATE-1.8d RING-FENCED, DO NOT EDIT (D-05)
   │
   ├─ ACK #1 → _decode_id_frame :412 → comm.firmware_identity = "3.0.0b19:leonardo"  (RAW, untruncated)
   │                                    comm.hw_revision      = 0xFE|rev byte  (u8, NOT the string)
   ├─ _probe_port :866  version_match = re.match(r"[\d.x]+", identity)   ── separate local ──▶ _validate_firmware_version
   │                    (never written back onto firmware_identity)
   └─ find_and_connect :968 → returns the live communicator
                    │
                    ▼
   ┌───────────────────────────────────────────────────────────────────────────────┐
   │  HOST HARDWARE LAYER — hardware.py  ← ★ THIS PHASE'S ONLY NEW LOGIC ★          │
   │  (scanned by NO AST gate; not in check_devtest_orchestrator's target list)     │
   │                                                                               │
   │  read_programmer_identity(flags=0) -> ProgrammerIdentity                       │
   │    comm = find_and_connect({"state": COMMAND_HW_VERSION})   ← ONE connection   │
   │    identity = _scrub(comm.firmware_identity)   ← D-07, non-printables only     │
   │    is_ok, msg = comm.expect_ack()              ← ACK #2                        │
   │    ┌── is_ok  → ProgrammerIdentity(hw_revision=msg,  fw_board_identity=identity)│
   │    ├── !is_ok → ProgrammerIdentity(hw_revision=None, fw_board_identity=identity)│  ← D-04
   │    └── SerialError-family → ProgrammerIdentity(None, None)                     │  ← F-17
   │    finally: comm.disconnect()                  ← SAFE-02 teardown unchanged    │
   └───────────────────────────────────────────────────────────────────────────────┘
                    │  (return value only — no object escapes)
                    ▼
   ┌───────────────────────────────────────────────────────────────────────────────┐
   │  ORCHESTRATOR / HANDLER — cli_handlers.py::dev_test  :2501-2507                │
   │  ident = app.hardware_manager.read_programmer_identity()                       │
   │  AutoCapture(host_version=…, fw_board_identity=ident.fw_board_identity,        │
   │              hw_revision=ident.hw_revision, chip=…, protocol=None)             │
   │  ⚠ ADD NO new `_`-prefixed helper here (arms the _HANDLER_FUNCTION_NAMES trap)  │
   └───────────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
   ┌───────────────────────────────────────────────────────────────────────────────┐
   │  REPORT MODEL — diagnostic_report.py   (imports NO transport class — SAFE-02)  │
   │  SCHEMA_VERSION "1.3" → "1.4"  :55        NOT_MEASURED :85 + NEW marker const  │
   │  to_dict() :408  fw_board_identity → typed value or null  (D-10: stays null)   │
   │  ├──▶ render() :505  rich table :518/:519  → marker instead of str(None)  D-12 │
   │  └──▶ to_json_block() :584  fenced JSON — UNCHANGED shape, populated value     │
   └───────────────────────────────────────────────────────────────────────────────┘
             │                                   │
             │ (console, operator)               │ (persisted + uploaded)
             ▼                                   ▼
      terminal render               ~/.firestarter/reports/dev-test-<chip>.{json,md}
                                               │
                                               ├──▶ submit.py: sanitize_dict → build_body → GitHub issue
                                               │
                          ┌────────────────────┴─────────────────────┐
                          ▼                                          ▼
   ┌──────────────────────────────────────┐   ┌──────────────────────────────────────────┐
   │ tools/parse_devtest_issue.py         │   │ .claude/skills/devtest-triage/scripts/   │
   │   render_diff() :192  ← 0 TESTS TODAY│   │   devtest_issues.py  cmd_show :294       │
   │   STDLIB-ONLY by contract:           │   │   prints `hw None` :333, no fw identity  │
   │   own marker literal, no import      │   │   SKILL-OWNED: own literal, no import    │
   └──────────────────────────────────────┘   └──────────────────────────────────────────┘
                          └──────────── value-parity test ────────────┘
                                    (replaces the forbidden import)
```

### Recommended change footprint

```
firestarter_app/
├── firestarter/
│   ├── hardware.py              # ★ ProgrammerIdentity + read_programmer_identity + _scrub
│   ├── cli_handlers.py          # one unpack at :2501-2507 + replace the :2494-2500 comment
│   └── diagnostic_report.py     # SCHEMA_VERSION 1.4 + rationale note + marker const + :518/:519
├── tools/
│   └── parse_devtest_issue.py   # render_diff: labelled identity line + not-attributable clause
└── tests/
    ├── test_hardware.py         # NEW: read_programmer_identity unit legs (D-04 ×2, D-07)
    ├── test_dev_test_cmd.py     # fixture returns the NamedTuple; 5 mock sites; D-13(b); D-08
    ├── test_diagnostic_report.py# D-13(a) render marker for BOTH identity rows
    └── test_parse_devtest_issue.py # NEW render_diff tests + null-carrying frozen fixture + parity

/workspaces/                      (meta repo)
├── .gitignore                   # ⚠ un-ignore of .claude/skills/ is UNCOMMITTED — land it
└── .claude/skills/devtest-triage/
    ├── scripts/devtest_issues.py# fw identity line + fix `hw None`
    └── SKILL.md                 # ⚠ :61-67 documents the `show` output verbatim — update it
```

### Pattern 1: Harvest-before-teardown on a borrowed connection

**What:** Read every derivable value off the communicator inside the same `try` that opened it, then
let the existing `finally: comm.disconnect()` run untouched.
**When to use:** any host value already present on a connection some other read already needs.
**Why it matters here:** it is the whole of PROV-02. No second `find_and_connect`, no cached
communicator, no attribute latched on a shared object.

**Ordering note (load-bearing):** read `comm.firmware_identity` **before** the second
`expect_ack()`, not after. It is populated by the setup ack (`:412`) and never cleared by
`disconnect()` (`:649` clears only `programmer_info`), so reading it late happens to work today —
but reading it early makes the D-04 else-branch return the identity without a second reference and
keeps the two values' provenance visually separate in the code.

### Pattern 2: Marker-instead-of-`str(None)` at the render boundary

**What:** never `str(x)` a nullable field into a human table; branch on `is None` and substitute a
named constant.
**Anti-shape it replaces:** `table.add_row("fw_board_identity", str(ac["fw_board_identity"]))`.
**Precedent:** `NOT_MEASURED` (`:85`) already does this for the transport counters; `_summarize` in
the skill script already does `auto.get("host_version") or "?"` (`:185`) — note the `or` idiom is
**wrong** for this field because it also swallows `""`; use `is None`.

### Pattern 3: Value-parity test in place of a forbidden import

**What:** when two modules must agree on a string but architecture forbids one importing the other,
assert equality in a test that legitimately imports both.
**Where:** `tests/test_parse_devtest_issue.py` already imports `firestarter.diagnostic_report`
(`:42`) **and** `tools.parse_devtest_issue` (`:50`). A one-line `assert` there is the cheapest
possible enforcement. (`tools/` is a PEP-420 namespace package — there is no `tools/__init__.py`, and
the existing tests import through it successfully.)

### Anti-Patterns to Avoid

- **Adding a `_`-prefixed helper to `cli_handlers.py`.** Arms a hard-equality assertion — see P-1.
- **Importing anything from `firestarter.*` into `tools/parse_devtest_issue.py`.** Breaks its stated
  stdlib-only contract (module docstring, "Stdlib-only CLI").
- **Importing from `firestarter_app/` into the skill script.** Violates "skills own their scripts".
- **Reusing `_sanitize_chip_token` for the identity.** It maps every non-`[alnum-_.]` character to
  `_`, which would mangle `"3.0.0b19:leonardo"` → `"3.0.0b19_leonardo"`. Follow its *shape*, not its
  character class (D-07 says "precedent", not "reuse").
- **Harvesting `comm.hw_revision`.** That is the CAP-02 **u8 byte** (`0xFE` on non-`HARDWARE_REVISION`
  builds), not the human revision string `read_hardware_revision_value` returns from ACK #2. Two
  different things with confusable names.
- **Using `or` as the null test.** `identity or MARKER` also fires on `""`, hiding an empty-string
  transport fault that D-07 exists to keep visible.
- **Mass-renaming `read_hardware_revision_value` across `/workspaces/.planning/`.** Eight hits there
  are **closed historical records** (`PROJECT.md:486`, `ROADMAP.md:1832`/`:3341`,
  `research/ARCHITECTURE.md:563`, `notes/sdp-surface-retirement…:106`,
  `todos/completed/dev-test-hard-fail-unknown-chip.md:41`, `STATE.md:1452`) describing what was true
  at the time. Rewriting them falsifies the record.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Get the firmware version | A `CMD_FW_VERSION` round trip / a new firmware command | `comm.firmware_identity` off the ack already exchanged | Already decoded at `serial_comm.py:412`; a second exchange is the SAFE-02 violation the current honest comment describes |
| Preserve the prerelease suffix | Widening `_validate_firmware_version` / a new version parser | Nothing — record `firmware_identity` verbatim | The suffix is already intact (F-05). D-05 ring-fences the gate |
| Split version and board | Two new schema keys | Keep the single `"<ver>:<board>"` string | `tests/test_diagnostic_report.py:128,525` and `test_parse_devtest_issue.py:374` already pin the combined shape; splitting turns a value change into a key addition and breaks PROV-04's one-case story |
| Decide whether a report is attributable | An `attributable` boolean in the JSON | A rendered clause in the human surfaces | D-14: no consumer exists; this is the `protect_on_after` dead-data shape the milestone is separately reconciling |
| Compare schema versions | `packaging.version` ordering in the parsers | Presence-only acceptance (unchanged) | D-17; the live `"9.9-future"` fixture would break any ordering comparison |
| Detect a "too old" report | Schema-version arithmetic | One clause true under both readings | D-17 |
| Scrub PII from the identity | A new scrubber in the parsers | `submit.py::sanitize_dict` (`:126`) already deep-scrubs every string leaf | Home-dir paths, `/dev/tty*`, `/tmp`, username — already recursive over `to_dict()`. D-07's job is only the U+FFFD class |
| Assert the render shows a value | An exit-code or "did not raise" check | `_rendered_text(table)` (`tests/test_diagnostic_report.py:965`) | The established, non-vacuous console-surface oracle in this repo |

**Key insight:** every capability this phase needs already exists somewhere in the codebase; the
phase is a *wiring and rendering* change. Any plan task that reaches for a new mechanism — a new
command, a new schema key, a new scrubber, a version comparator — is solving a problem the codebase
has already solved, and is a scope escape.

## Runtime State Inventory

This phase **renames a method** (D-03), so the inventory is mandatory.

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| **Stored data** | **No datastore stores the method name.** But `~/.firestarter/reports/dev-test-*.json` on every user's machine, and every `dev test` issue body already filed on GitHub, carry `fw_board_identity: null` **permanently**. Verified: `grep -rn read_hardware_revision_value` finds zero hits outside `.py` source and `.planning/` prose. | **Code edit only, no data migration.** The already-filed reports are *unfixable by design* — this is precisely why the Evidence Ceiling holds and why OUT-02 (Phase 152) asks reporters for a fresh run rather than re-attributing gh#21/#32. A plan must **not** attempt retro-attribution. |
| **Live service config** | None. No n8n workflow, Datadog service, Tailscale ACL or Cloudflare tunnel references this method or field. Verified by grepping the full meta + app + firmware trees. | None. |
| **OS-registered state** | None. No Task Scheduler entry, pm2 process, launchd plist or systemd unit names it. | None. |
| **Secrets / env vars** | None names the method. The relevant env seams are `FIRESTARTER_DEVTEST_SRC` / `FIRESTARTER_DEVTEST_HANDLER` / `FIRESTARTER_DEVTEST_SUBMIT` / `FIRESTARTER_DIAGREPORT_SRC` (gate target overrides) and `FIRESTARTER_CONFIG_DIR` (report output dir). All unaffected by the rename. `FIRESTARTER_DEV_ALLOW_PRE_V12` gates the ring-fenced version check — untouched. | None. |
| **Build artifacts / installed packages** | `firestarter` is installed **editable** at `/usr/local` (`3.0.0b20`), so a source rename is picked up with no reinstall — verified by importing the live module. Stale `tools/__pycache__/` and `tests/__pycache__/` exist but pytest invalidates by mtime. **`firestarter_app/.venv/ci-replica/` is a BROKEN artifact**: the directory exists but `bin/python` is missing, so `tools/ci_replica_venv.sh` must be run with `--refresh` if a mypy count is wanted. | Editable install: **none**. CI-replica venv: `--refresh` on demand only (not a phase blocker). |
| **Documentation / prose** | `.claude/skills/devtest-triage/SKILL.md:69-75` documents the `show` render **verbatim**, including the `host … hw Rev 2.0-class…` line. `/workspaces/.planning/` has 8 historical references to the old method name. | **SKILL.md:69-75 MUST be updated** in the same commit as the script (a documented example that no longer matches its script is how a triager stops trusting the tool). `.planning/` historical references: **leave alone** — see the anti-pattern above. |

## Test-Mock Churn Surface for the D-03 Rename

Complete enumeration. `grep -rn "read_hardware_revision_value"` over the entire `firestarter_app`
tree (`--include=*.py --include=*.md --include=*.toml`, excluding `.git/`) returns **exactly 8
hits**, in 3 files:

| # | Site | What it does | Action after rename |
|---|------|--------------|---------------------|
| 1 | `firestarter/hardware.py:115` | the `def` | **Rename**; widen return to `ProgrammerIdentity` |
| 2 | `firestarter/cli_handlers.py:2501` | the **only** production call site, inline inside `AutoCapture(...)` | **Unpack**: call once above the constructor, pass both fields as keywords |
| 3 | `tests/test_dev_test_cmd.py:378` | docstring prose in `make_hardware_manager` | Reword |
| 4 | `tests/test_dev_test_cmd.py:400` | `hw.read_hardware_revision_value.return_value = hw_revision` — the fixture wiring | **Rename + change the return value to the NamedTuple.** The fixture's `hw_revision: object = "Rev 2.0-class"` parameter should gain a sibling (e.g. `fw_board_identity: object = "3.0.0b19:leonardo"`) so the 41 `dev test` invocations keep working and D-08/D-13(b) can vary one field |
| 5 | `tests/test_dev_test_cmd.py:731` | docstring prose in `test_hw_revision_auto_captured_end_to_end` | Reword |
| 6 | `tests/test_dev_test_cmd.py:831` | docstring prose in `test_absent_chip_still_hard_fails_before_hardware` naming the load-bearing assertion | Reword — and keep it naming the assertion |
| 7 | `tests/test_dev_test_cmd.py:845` | **`app.hardware_manager.read_hardware_revision_value.assert_not_called()`** — the load-bearing negative assertion (F-11) | **Rename.** This is the absent-chip false-green guard |
| 8 | `tests/test_dev_test_cmd.py:863` | `hw.read_hardware_revision_value.assert_called()` in `test_dev_test_present_but_unsupported_still_sweeps` | **Rename** |

### Why a missed mock cannot go silently green

Every `hardware_manager` double in the suite is spec-bound. Enumerated:

- `tests/conftest.py:314` — `make_app_context`'s default: `Mock(spec=HardwareManager)`
- `tests/test_dev_test_cmd.py:391` — `make_hardware_manager`: `Mock(spec=HardwareManager)`
- `tests/test_cli_handlers.py:65,487,497,506,516` — `Mock(spec=HardwareManager)`
- `tests/test_validate_oracle.py:50,119,168,218,285,329,410,468,520,552` — `Mock(spec=HardwareManager)`
- `tests/test_protocol_not_implemented.py:62`, `tests/test_protocol_not_implemented_production_path.py:72`,
  `tests/test_matrix_artifact.py:36` — `Mock`/`MagicMock(spec=HardwareManager)`
- `tests/test_pulse_us_override.py:273`, `test_validate_family_cmd.py:36`, `test_write_skip_sdp_unlock.py:61` —
  typed `HardwareManager | Mock | None` parameters fed from the above

I verified empirically that `Mock(spec=HardwareManager).read_programmer_identity` raises
`AttributeError: Mock object has no attribute 'read_programmer_identity'`, while a bare `Mock()`
silently returns a truthy child. **There are no bare `Mock()` hardware managers in the suite.**
Therefore any of sites 4/7/8 left un-renamed produces a loud `AttributeError`, not a vacuous
`assert_not_called()` — the false-green trap does **not** reopen through this route.

Two residual routes the plan should still guard:

- **`tests/test_dev_test_cmd.py` is the only file that invokes `dev test`** (41 `runner.invoke(cli, ["dev", "test", …])`
  call sites, all in that one module — verified). So no other module can drift into calling the
  handler with an unconfigured spec mock whose auto-child `.hw_revision` would leak a `Mock` repr
  into a report.
- The NamedTuple's own **field names** are not spec-protected: `ident.fw_board_identity` on a mock
  whose `return_value` is a plain `MagicMock` yields a child mock, not `None`. Site 4 must return a
  **real `ProgrammerIdentity`**, never a bare `Mock`.

## Gate Verification

Both gates were executed this session against the live tree.

### G-1 — `tools/check_devtest_orchestrator.py` (SAFE-02/SAFE-03 AST gate)

```bash
cd /workspaces/firestarter_app && python3 tools/check_devtest_orchestrator.py; echo "EXIT=$?"
```

Live output:

```
PASS: scanned ../firestarter/chip_test.py, ../firestarter/cli_handlers.py, ../firestarter/submit.py; 0 VPP-set, 0 raw-wire-dict, 0 --force, 0 broad-except; firmware untouched (host-only, asserted)
EXIT=0
```

- **`hardware.py` is genuinely NOT in scan scope** — confirmed. The three targets are
  `FIRESTARTER_DEVTEST_SRC` (`firestarter/chip_test.py`, full scan), `FIRESTARTER_DEVTEST_HANDLER`
  (`firestarter/cli_handlers.py`, scoped), `FIRESTARTER_DEVTEST_SUBMIT` (`firestarter/submit.py`,
  full scan) — `main()` at `:547-625`, defaults at `:95/:106/:121`.
- **`_HANDLER_FUNCTION_NAMES` still gates `cli_handlers.py` coverage** — confirmed, frozenset at
  `:152-181` with 12 names (`dev_test`, `_verdict_code`, `_overall_exit_code`, `_dev_test_exit_code`,
  `_sanitize_chip_token`, `_is_uv_eprom`, `_resolve_write_scope`, `_default_uv_write_confirm`,
  `_chip_id_fields`, `_is_interactive`, `_make_sampler`, `_sdp_recovery_line`).
- **`_assert_host_only` is path-comparison only** (`:515-535`): it rejects a target resolving under
  `<meta_root>/firestarter`. It never requires the sibling to exist, so it behaves identically in
  standalone CI.
- **The denied wire-key vocabulary does not include `state`** — `{"state": COMMAND_HW_VERSION}` is
  outside it, and in any case lives in an unscanned file.
- **P-07's fail-open has been CLOSED since this pitfall was written.**
  `tests/test_check_devtest_orchestrator.py::test_every_helper_referenced_by_dev_test_is_listed`
  (`:561`) derives the referenced-helper set from the AST and asserts **hard equality** against
  `_EXPECTED_DEV_TEST_REFERENCED_HELPERS` (`:545-558`), plus a non-vacuity guard and a `>= 6`
  floor. `test_handler_function_names_all_resolve_to_real_callables` (`:493`) closes the reverse
  direction. See P-1 for the consequence.

### G-2 — `tools/check_diagnostic_report_claims.py` (14-pattern claim scanner)

```bash
cd /workspaces/firestarter_app && python3 tools/check_diagnostic_report_claims.py; echo "EXIT=$?"
```

Live output:

```
PASS: scanned /workspaces/firestarter_app/tools/../firestarter/diagnostic_report.py, 164 string literals checked, zero forbidden matches
EXIT=0
```

- **14 patterns confirmed** (`FORBIDDEN_PATTERNS`, `:106-150`): `verified-fixed`,
  `confirmed-working`, `silicon-verified`, `verified-on-silicon`, `works-on-silicon`, `now-works`,
  `should-now-work`, `proven-on-silicon`, `lock-inhibited-the-write`, `lock-held-unqualified`,
  `proven-behaviour`, `behaviourally-verified`, `now-proven`, `dev-test-proves-unqualified`.
  `REQUIRED_CAVEAT_PATTERN` (`:156`) is deliberately **unused** by `main()`.
- **`"not reported"` trips none of them.** I loaded the module and ran six candidate wordings through
  the live pattern table:

  | Candidate | Verdict |
  |---|---|
  | `not reported` | clean |
  | `not reported by the programmer` | clean |
  | `unknown (not reported)` | clean |
  | `firmware identity not reported -- this report is not attributable to a firmware version` | clean |
  | `not attributable -- ask for a fresh run on a current host` | clean |
  | `not attributable to a firmware version; request a fresh dev test run on a current host` | clean |

  All six are safe for both D-11 and D-14/D-17 phrasings. **Avoid** anything containing "now works",
  "should now work", "now proven", or "dev test proves".
- **Scope caveat (fails open elsewhere):** this gate scans **only** `diagnostic_report.py`
  (`_DEFAULT_DIAGREPORT_SRC`, `:88`). The not-attributable clause in `tools/parse_devtest_issue.py`
  and in the skill script is covered by **no claim gate at all**. See P-5.

## Common Pitfalls

### P-1 (HIGH): A new `_`-prefixed helper in `cli_handlers.py` turns three files RED at once

**What goes wrong:** the plan adds e.g. `_render_identity()` or `_scrub_identity()` beside `dev_test`
and calls it from `dev_test`'s body. `test_every_helper_referenced_by_dev_test_is_listed` derives the
referenced set from the AST and asserts **hard equality** with a literal expected set — so the test
goes RED even if the helper is harmless, and stays RED until `_HANDLER_FUNCTION_NAMES`
(`tools/check_devtest_orchestrator.py`) **and** `_EXPECTED_DEV_TEST_REFERENCED_HELPERS`
(`tests/test_check_devtest_orchestrator.py:545`) are both updated in the same commit.
**Why it happens:** the allow-list was fail-open against additions; Phase 131 closed it with a
bidirectional equality invariant. The invariant is correct — it is just strict.
**How to avoid:** put **zero** new callables in `cli_handlers.py`. D-01 already routes the capture to
`hardware.py` and D-11/D-12 route the rendering to `diagnostic_report.py`. The handler change is one
call plus two keywords.
**Warning signs:** a diff touching `cli_handlers.py` that adds a `def`; a plan task naming a helper.

### P-2 (MEDIUM, already mitigated — do not weaken the mitigation): the spec mock is what keeps the rename honest

**What goes wrong:** a future refactor swaps a `Mock(spec=HardwareManager)` for a bare `Mock()` "to
simplify", and every `assert_not_called()` / `assert_called()` on a renamed-away method becomes
vacuously true — reopening the absent-chip false-green trap for real.
**How to avoid:** the plan must not introduce any unspecced hardware-manager double, and site 4 must
return a real `ProgrammerIdentity`, not a `MagicMock`. Consider a one-line assertion in
`test_dev_test_cmd.py` that `make_hardware_manager()` returns a spec-bound mock — cheap, and it pins
the property the rename's safety rests on.

### P-3 (MEDIUM-HIGH): `render_diff` has no test, so PROV-06 can ship unproven

**What goes wrong:** an executor edits `render_diff`, the full suite stays green (because nothing
tests it), and PROV-06's criterion #5 gets ticked on an unexercised code path. This is the
volume-without-reachability shape.
**How to avoid:** treat `tests/test_parse_devtest_issue.py::render_diff` coverage as **Wave 0**, and
require the plan's verify block to show the new tests failing before the edit and passing after.
`render_diff` is a pure function of `(report_obj, diff, n_agreeing)` returning a string — it is
trivially testable, there is simply no test yet.
**Warning signs:** a plan whose PROV-06 verification is "ran the CLI and eyeballed the output".

### P-4 (HIGH): D-11's "single-sourced constant" cannot span all three surfaces — decide it, don't discover it

**What goes wrong:** the plan writes "import `NOT_REPORTED` from `diagnostic_report`" into all three
render tasks. `tools/parse_devtest_issue.py` is **stdlib-only by stated contract** (module docstring:
"Stdlib-only CLI"; imports are `argparse, json, re, sys, pathlib, typing` only) and the skill script
must not import from the app at all ("skills own their scripts"). Either the executor breaks a
contract, or it silently drifts three literals apart.
**How to avoid:** decide up front — **one constant per module, three modules, plus a value-parity
test**. `tests/test_parse_devtest_issue.py` already imports both `firestarter.diagnostic_report`
(`:42`) and `tools.parse_devtest_issue` (`:50`), so:

```python
def test_unknown_marker_string_matches_the_report_model():
    from firestarter.diagnostic_report import NOT_REPORTED as MODEL_MARKER
    from tools.parse_devtest_issue import NOT_REPORTED as PARSER_MARKER
    assert PARSER_MARKER == MODEL_MARKER
```

The skill script's copy cannot be covered this way without coupling the app suite to a meta-repo
path — cover it by the P-6 checkpoint instead, and say so in the plan.
**Warning signs:** any `from firestarter` line in `tools/parse_devtest_issue.py` or in the skill
script.

### P-5 (MEDIUM): the claim gate does not see the parsers

**What goes wrong:** the not-attributable clause is authored in `render_diff` and the skill script,
neither of which any claim gate scans. A future edit could put "the firmware now works" in a triage
render and no gate would fire.
**How to avoid:** keep the clause wording in the "clean" column of §G-2's table, and note the
coverage gap explicitly in the plan rather than implying the gate covers it. Widening
`FIRESTARTER_DIAGREPORT_SRC` to a second file is **not** this phase's job (its default is a single
path, and Phase 152 owns the outward-facing claim gate) — but a plan may legitimately add a small
`tests/` assertion that the two parser markers contain none of the 14 patterns, importing the table
from `tools.check_diagnostic_report_claims`.

### P-6 (MEDIUM-HIGH): the skill script has no test harness, and inventing one couples the app CI to the meta repo

**What goes wrong:** the plan adds `tests/test_devtest_issues_skill.py` in the app repo that
subprocess-invokes `/workspaces/.claude/skills/.../devtest_issues.py`. In standalone CI that path
does not exist, so the test either errors (RED for the wrong reason) or skips (**fails open** — the
exact shape recorded as "App gates scan FIRMWARE source — renames break them ... they fail OPEN",
4× in Phase 117).
**How to avoid:** verify the skill render by a `checkpoint:human-verify` running the script offline
against two committed fixture bodies. Both commands are proven working — I ran them this session:

```bash
# populated identity
python3 /workspaces/.claude/skills/devtest-triage/scripts/devtest_issues.py \
  show --body-file <fixture-with-identity>.md --title '[dev test] at28c256 — FAIL'
# null identity
python3 /workspaces/.claude/skills/devtest-triage/scripts/devtest_issues.py \
  show --body-file <fixture-null>.md --title '[dev test] at28c256 — FAIL'
```

`cmd_show` (`:294`) takes the `--body-file` branch when no issue number is given, and **never shells
out to `gh`** on that branch — fully offline and hermetic. Today's null-identity output (measured):

```
#?  at28c256  —  FAIL
  schema      1.4   generated 2026-08-18T10:00:00Z
  host        3.0.0b21   hw None
  protocol    0x0D   chip at28c256
```

### P-7 (MEDIUM): `comm.hw_revision` is not the hardware revision string

**What goes wrong:** the harvest reads `comm.hw_revision` (an `Optional[int]`, the CAP-02 `u8` at
`params_bytes[2]`, declared at `serial_comm.py:127` and `:168`) instead of / alongside the ACK #2
message string, and the report gains a bare integer where a `"Rev 2.0-class, Override HW: Rev 2.3"`
string belongs. On a non-`HARDWARE_REVISION` build that byte is `0xFE`.
**How to avoid:** `hw_revision` in the report comes **only** from `expect_ack()`'s `msg`; the identity
comes **only** from `comm.firmware_identity`. Nothing else on the communicator is harvested.

### P-8 (MEDIUM): `or`-based null tests swallow the empty-string fault D-07 exists to expose

**What goes wrong:** `auto.get("fw_board_identity") or MARKER` renders the marker for `""` as well as
for `None`. A firmware that emits a zero-length identity tail (`ver_len == 0`) yields exactly `""` —
`serial_comm.py:410-413` computes `ver_end = 4 + params_bytes[3]` and slices, so a zero length gives
an empty string, not `None`. That is a transport/firmware fault D-07 wants visible, and `or` hides it
as "not reported".
**How to avoid:** branch on `is None` in all three renders. If the plan wants `""` treated as a fault
rather than as unknown, say so explicitly and test it.

### P-9 (LOW-MEDIUM, pre-existing — do not propagate): `diagnostic_report.py` is not importable on the advertised Python floor

**What goes wrong:** `pyproject.toml` declares `requires-python = ">=3.9"` and ruff targets `py39`,
but `diagnostic_report.py` has **no** `from __future__ import annotations` and uses `str | None` at
dataclass **class-body** scope (`:120-127`). A dataclass evaluates its annotations at class creation,
and PEP 604 `X | Y` on builtins requires 3.10. CI runs 3.11 only, so this is untested and invisible.
**How to avoid:** the new `ProgrammerIdentity` lives in `hardware.py`, which uses
`from typing import Optional, Tuple  # noqa: UP035` and is currently 3.9-import-safe. **Use
`Optional[str]` there**, matching that module's existing convention, rather than importing the
3.10-only syntax into a module that does not have it. Do not attempt to fix
`diagnostic_report.py` — out of scope, and ruff's `UP` rules will not force the change at
`target-version = "py39"`.

### P-10 (LOW): the `.md` artifact — the actual GitHub issue body — has no human-readable identity line

**What goes wrong:** a reviewer reads criterion #4 ("the human-readable report surfaces") as covering
the `dev-test-<chip>.md` artifact and marks it unmet. It is not covered, deliberately: the `.md`
body is `# dev test -- <chip>` + a `| Step | Verdict | Reason |` table + `to_json_block()`
(`cli_handlers.py:2550-2561`), and `submit.py::build_body` (`:179-198`) is the same shape. The
identity appears there **only inside the fenced JSON** — which D-10 keeps as typed `null`.
**How to avoid:** state in the plan that PROV-05's "human-readable report surfaces" = the `rich`
console table (`render`), and PROV-06's parser surfaces = the two triage renders. Do not silently
extend the `.md` table; if a plan wants an identity row there, that is a new decision, not a
criterion reading.

### P-11 (LOW): `test_flash_path_record_sync`-class whole-repo porcelain assertions

The app suite is green on a **clean** tree (measured: 1590 passed). Commit before running the suite
as a verification leg — a mid-change dirty tree can turn a porcelain-asserting test RED for reasons
unrelated to the change.

## Code Examples

### E-1 — the widened harvest (`hardware.py`)

```python
# Source: measured shape of firestarter/hardware.py:115-147 (this session);
# NamedTuple precedent from firestarter/frame_vectors.py:20
class ProgrammerIdentity(NamedTuple):
    """Both values from ONE connection, failing independently (D-04)."""
    hw_revision: Optional[str]        # from the CMD_HW_VERSION ack (ACK #2)
    fw_board_identity: Optional[str]  # from the CAP-02 MSG_OK_READY tail (ACK #1)


def read_programmer_identity(self, flags: int = 0) -> ProgrammerIdentity:
    command = {"state": COMMAND_HW_VERSION}
    if flags:
        command["flags"] = flags

    comm = None
    identity: Optional[str] = None
    try:
        comm = SerialCommunicator.find_and_connect(command, self.config)
        # Harvest FIRST: _probe_port set this off ACK #1, before the dispatch
        # switch ran, so it is available even when ACK #2 errors (D-01/D-04).
        identity = _scrub_identity(comm.firmware_identity)
        is_ok, msg = comm.expect_ack()
        if is_ok:
            return ProgrammerIdentity(hw_revision=msg, fw_board_identity=identity)
        logger.error(f"Failed to read hardware revision: {msg}")
        return ProgrammerIdentity(hw_revision=None, fw_board_identity=identity)
    except (ProgrammerNotFoundError, SerialError, SerialTimeoutError) as e:
        # F-17: FirmwareOutdatedError / HardwareRevisionUnsupportedError /
        # ProgrammerNotFoundError are ALL SerialError subclasses and land here.
        logger.error(f"Failed to read hardware revision: {e}")
        return ProgrammerIdentity(hw_revision=None, fw_board_identity=identity)
    finally:
        if comm:
            comm.disconnect()   # SAFE-02 teardown, unchanged
```

Note the `except` branch returns `identity` too — it is `None` unless the failure happened after the
harvest, which keeps the two failure paths genuinely independent.

### E-2 — the handler unpack (`cli_handlers.py:2498-2504`)

```python
# Source: current construction at firestarter/cli_handlers.py:2498-2504
# Replaces (never deletes) the :2494-2500 comment: say why THIS connection can
# serve, where the old comment said why EpromOperator.comm cannot.
identity = app.hardware_manager.read_programmer_identity()
auto_capture = AutoCapture(
    host_version=version,
    fw_board_identity=identity.fw_board_identity,
    hw_revision=identity.hw_revision,
    chip=chip,
    protocol=None,
)
```

Field access by name (`identity.fw_board_identity`), never `a, b = ...` — a positional swap of two
`Optional[str]`s type-checks clean (D-03).

### E-3 — the marker render (`diagnostic_report.py:511-513`)

```python
# Source: current rows at firestarter/diagnostic_report.py:511-513
NOT_REPORTED = "not reported"  # beside NOT_MEASURED at :85 (D-11)

def _identity_cell(value: object) -> str:
    """`is None`, never `or` — an empty string is a transport fault, not
    an absent value (D-07 / Pitfall P-8)."""
    return NOT_REPORTED if value is None else str(value)

table.add_row("host_version", str(ac["host_version"]))
table.add_row("fw_board_identity", _identity_cell(ac["fw_board_identity"]))  # D-12
table.add_row("hw_revision", _identity_cell(ac["hw_revision"]))              # D-12
```

### E-4 — the render-level oracle (`tests/test_diagnostic_report.py`)

```python
# Source: the established pattern at tests/test_diagnostic_report.py:965-983
def _rendered_text(table) -> str:
    cells = [str(cell) for column in table.columns for cell in column.cells]
    return " ".join(cells)

def test_null_identity_renders_the_explicit_marker_in_both_rows():
    report = _minimal_report()                     # AutoCapture(fw_board_identity=None,
    rendered = _rendered_text(report.render())     #             hw_revision=None)
    assert rendered.count(NOT_REPORTED) >= 2       # D-12: both rows
    assert " None " not in f" {rendered} "         # never the bare str(None)
    assert report.to_dict()["auto_capture"]["fw_board_identity"] is None   # D-10
```

### E-5 — the D-08 differing-pair oracle

```python
# Source: format precedent tests/test_diagnostic_report.py:128,525 and
# tests/test_parse_devtest_issue.py:374
@pytest.mark.parametrize("identity", ["3.0.0b11:leonardo", "3.0.0b19:leonardo"])
def test_prerelease_suffix_survives_into_the_report(runner, identity):
    ...  # one run each, collect data["auto_capture"]["fw_board_identity"]

def test_two_identities_differing_only_in_suffix_land_as_different_values():
    """gh#21/#32's exact undiagnosable case: host 3.0.0b15 against an unknown
    firmware cannot be distinguished from a board lacking the whole
    Phase-117-120 0x0D fix stack."""
    assert captured["3.0.0b11:leonardo"] != captured["3.0.0b19:leonardo"]
```

The inequality assertion is the point — a single round-trip assertion passes vacuously if a later
refactor normalises suffixes away (D-08).

### E-6 — the parser render (`tools/parse_devtest_issue.py::render_diff`)

```python
# Source: current lines at tools/parse_devtest_issue.py:200-214.
# Stdlib-only module: local constant, NO import from firestarter (Pitfall P-4).
NOT_REPORTED = "not reported"

fw = auto_capture.get("fw_board_identity")
lines.append(f"  host_version:            {auto_capture.get('host_version') or NOT_REPORTED}")
if fw is None:
    lines.append(
        f"  fw_board_identity:       {NOT_REPORTED} -- this report is NOT attributable "
        "to a firmware version; ask the reporter for a fresh `dev test` run on a "
        "current host build"          # D-14/D-17: one clause, no schema-version ordering
    )
else:
    lines.append(f"  fw_board_identity:       {fw}")
```

D-15: `host_version` **and** `fw_board_identity`; **no** `hw_revision` row.

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|--------------|------------------|--------------|----------------------|
| `CMD_FW_VERSION` probe reading an `"OK: FW: <ver>"` text line, host-side `re.search(r"FW:\s*([\d.x]+)", fw_msg)` | CAP-02 identity tail on the `MSG_OK_READY` ack; `comm.firmware_identity` holds the raw string | v1.16-era CAP-01/02, CAP-03 added in v1.31 | **This is the whole reason PROV-03's premise was false.** The "host cannot see the prerelease suffix" note describes the retired probe |
| `_HANDLER_FUNCTION_NAMES` as documentation (fail-open against additions) | Bidirectional AST-derived equality invariant in `tests/test_check_devtest_orchestrator.py` | Phase 131 (`test_every_helper_referenced_by_dev_test_is_listed`) | P-07 in `.planning/research/PITFALLS.md` is now **closed**; the consequence is P-1's strictness |
| `mypy` target `py39` | target `python_version = "3.10"` (mypy clamps below that) | Phase 131 D-13/GATE-05 | Nothing type-checks against the advertised 3.9 floor — hence P-9 |
| ad-hoc local lint invocations | `tools/ci_parity.sh` (4 legs) + `tools/ci_replica_venv.sh` (5 legs) | Phase 131 / 132 | Use these rather than hand-rolling CI-scoped commands |

**Deprecated / outdated in this area:**
- `comm.programmer_info` as an identity source — it is the ACK message text, and `disconnect()`
  nulls it (`serial_comm.py:649`). `firmware_identity` survives teardown.
- `firestarter/primitives.{h,cpp}` and a wire `page_size` — the Phase 89 recompose was never merged
  (relevant to Phase 149, not 147).

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `python3` (`/usr/local/bin/python3`) | everything | ✓ | 3.12.13 | — |
| `firestarter` editable install | handler-level tests | ✓ | 3.0.0b20 (branch `gsd/v1.31-…`) | `pip install -e '.[test]'` |
| `pytest` | every automated oracle | ✓ | 9.1.1 (`~/.local/bin`) | — |
| `syrupy` | snapshot leg (30 snapshots pass; none touch this phase) | ✓ | installed | — |
| `ruff` | CI-scoped lint/format gate | ✓ | 0.16.3 | — |
| `mypy` | watermark gate | ✓ | 2.3.1 | see below |
| `rich`, `click`, `packaging`, `pyserial` | runtime imports | ✓ | installed | — |
| `gh` CLI | skill `list`/`show <number>` modes only | ✓ | 2.97.0 | `--body-file` mode needs no `gh` — use it for verification |
| `python3.11` (CI's interpreter) | exact mypy-count parity | **✗** | — | `tools/ci_replica_venv.sh` falls back to `python3` (3.12); the count is numpy-free and usable, but not literally CI's interpreter |
| `.venv/ci-replica` | numpy-free mypy count | **✗ broken** | dir exists, `bin/python` missing | `bash tools/ci_replica_venv.sh --refresh` |
| Real AT28C silicon | nothing in this phase | **✗** | — | **N/A by design** — Evidence Ceiling; no criterion may require it |
| `/dev/ttyACM0` (a live board) | nothing in this phase | ✓ (attached) | — | Full suite measured **green with the board attached** (1590 passed), so the `comports=[]`-vs-live-board hazard is not currently firing |

**Missing dependencies with no fallback:** none that block this phase.

**Missing dependencies with fallback:**
- `python3.11` → `ci_replica_venv.sh` builds on `python3`. Sufficient for a mypy count; note the
  interpreter delta in any record.
- Broken `.venv/ci-replica` → `--refresh`. Not a phase blocker: `python3 tools/check_mypy_watermark.py`
  **exits 2 locally by documented design** (ambient numpy's PEP-695 stub truncates mypy's run), which
  `tools/ci_parity.sh`'s own leg-4 header calls expected, correct behaviour. Reproduced this session:
  `numpy/__init__.pyi:737: error: Type statement is only supported in Python 3.12 and greater`,
  `EXIT=2`. **Do not "fix" this with `|| true`.**

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` 9.1.1 local (pinned `>=8.0`), `syrupy>=5.0` for snapshots |
| Config file | `firestarter_app/pyproject.toml` → `[tool.pytest.ini_options]`: `testpaths = ["tests"]`, `addopts = "-ra -q"` |
| Quick run command | `cd /workspaces/firestarter_app && python3 -m pytest tests/test_dev_test_cmd.py tests/test_diagnostic_report.py tests/test_parse_devtest_issue.py tests/test_hardware.py tests/test_provenance.py tests/test_submit.py tests/test_check_devtest_orchestrator.py tests/test_check_diagnostic_report_claims.py -o addopts="" -q` |
| Quick run measured baseline | 239 passed in **43.7 s** (the 7-file subset without `test_hardware.py`) |
| Full suite command | `cd /workspaces/firestarter_app && python3 -m pytest tests/ -o addopts="" -q` |
| Full suite measured baseline | **1590 passed, 1 warning in 228.9 s** (30 snapshots passed), clean tree, board attached |

**`addopts` note (load-bearing):** the project sets `addopts = "-ra -q"`. Adding another `-q` reaches
`-qq` and **suppresses the `N passed` count line** — a verification leg that needs the count must
pass `-o addopts=""`. Every command in this section already does.

**mypy note:** `python3 tools/check_mypy_watermark.py` prints a legible summary but **exits 2** in this
devcontainer (ambient numpy). Its argv is `[sys.executable, "-m", "mypy", "firestarter/", "tests/"]`
and the watermark is **35** (`pyproject.toml:174`). `tools/` is outside mypy's scope, so any new code
in `tools/parse_devtest_issue.py` is **not type-checked** — assert on behaviour, not on types, there.

**ruff note:** CI scope is exactly `ruff check firestarter/ tests/` and
`ruff format --check firestarter/ tests/` (`ci.yml:215,218`). Running ruff wider than that is not CI
parity and can produce findings CI will never see; running it narrower hides real ones.
`tools/` and `.claude/skills/` are **not** linted by CI.

### Phase Requirements → Test Map

| Req ID | Behavior (observable oracle) | Test type | Automated command | File exists? |
|--------|------------------------------|-----------|-------------------|--------------|
| PROV-01 | `read_programmer_identity()` returns the harvested `comm.firmware_identity` verbatim off a **single** `find_and_connect` | unit (hardware) | `python3 -m pytest tests/test_hardware.py -o addopts="" -q -k programmer_identity` | ❌ **Wave 0 (W-1)** — `test_hardware.py` exists (13 tests) but tests **only** `get_hardware_revision`; no coverage of the value-returning sibling at all |
| PROV-01 | The identity reaches `to_dict()["auto_capture"]["fw_board_identity"]` in the **saved JSON artifact** and the **rendered output**, end-to-end | handler | `python3 -m pytest tests/test_dev_test_cmd.py -o addopts="" -q -k fw_board_identity` | ⚠ extend — mirror `test_hw_revision_auto_captured_end_to_end` (`:730-743`) exactly; it already asserts both `result.output` and `_load_report(...)` |
| PROV-02 | Exactly **one** `SerialCommunicator.find_and_connect` call and exactly **one** `disconnect()` per `read_programmer_identity()`; no `EpromOperator` attribute is written | unit (hardware) | same as W-1, with `patch("firestarter.serial_comm.SerialCommunicator.find_and_connect")` asserting `call_count == 1` and `comm.disconnect.assert_called_once()` | ❌ **Wave 0 (W-1)** — the `make_comm` / `fake_serial` conftest fixtures and the `patch(find_and_connect)` idiom are the established pattern (`test_hardware.py:58,72,89,…`) |
| PROV-02 | The SAFE-02/SAFE-03 AST gate stays green and still names all three targets in its PASS line | gate | `python3 tools/check_devtest_orchestrator.py` → `EXIT=0`, output contains `chip_test.py`, `cli_handlers.py`, `submit.py` | ✅ measured PASS today |
| PROV-02 | No new `dev_test` helper slipped past the allow-list | gate (test) | `python3 -m pytest tests/test_check_devtest_orchestrator.py -o addopts="" -q` | ✅ exists (`test_every_helper_referenced_by_dev_test_is_listed`) — must stay green **without** editing its expected set |
| PROV-03 | **Differing-pair discrimination (D-08):** `"3.0.0b11:leonardo"` and `"3.0.0b19:leonardo"` land as two **different** JSON values | handler | `python3 -m pytest tests/test_dev_test_cmd.py -o addopts="" -q -k suffix` | ❌ **Wave 0** — new test; format precedent at `test_diagnostic_report.py:128,525` |
| PROV-03 | `comm.firmware_identity` is never truncated by the version gate — the `[\d.x]+` match is a separate local | unit (transport, read-only) | `python3 -m pytest tests/test_fwguard.py tests/test_fw_version_guard.py -o addopts="" -q` | ✅ exists — these **pin the ring fence**. Run them as a non-regression leg; **do not add to them and do not edit the fenced path** (D-05) |
| PROV-04 | `SCHEMA_VERSION == "1.4"` and the fenced block carries it | unit | `python3 -m pytest tests/test_diagnostic_report.py -o addopts="" -q -k schema` | ✅ exists (`:516 assert parsed["schema_version"] == SCHEMA_VERSION`) — **imports the constant, so it auto-follows the bump** |
| PROV-04 | A frozen report body carrying `fw_board_identity: null` **still parses** against the bumped version, on **both** parsers | parser | `python3 -m pytest tests/test_parse_devtest_issue.py -o addopts="" -q -k legacy` | ❌ **Wave 0 (W-3)** — `test_legacy_vocabulary_b11_body_still_parses` (`:456`) exists but `_B11_BODY` (`:361-374`) carries a **populated** `"3.0.0b11:leonardo"`. A null-carrying frozen fixture does not exist |
| PROV-04 | Forward-compat: presence-only acceptance survives the bump | parser | same file, `-k presence` | ✅ exists (`test_detect_schema_version_matched_by_presence_not_exact_value`, `"9.9-future"` at `:138`). **Pre-verified:** I fed a `"1.4"` body to both parsers today; both accepted it |
| PROV-04 | Blast radius: dedup + submittability unchanged | unit | `python3 -m pytest tests/test_provenance.py -o addopts="" -q` | ✅ exists — pins `dedup_fingerprint` excluding the field and `is_submittable` gating on three others |
| PROV-05 | **D-13(a)** render-level: `AutoCapture(fw_board_identity=None, hw_revision=None)` → marker present in the `rich` table for **both** rows; no bare `"None"`; JSON still `null` | unit (render) | `python3 -m pytest tests/test_diagnostic_report.py -o addopts="" -q -k marker` | ❌ **Wave 0** — new test; use the existing `_rendered_text(table)` helper (`:965`) and `_minimal_report()` |
| PROV-05 | **D-13(b)** handler-level: `HardwareManager` mock returns `ProgrammerIdentity(None, None)` → marker in the rendered report **and** `null` in the saved JSON | handler | `python3 -m pytest tests/test_dev_test_cmd.py -o addopts="" -q -k unknown` | ❌ **Wave 0** — new test; drive it through `make_hardware_manager(...)` |
| PROV-05 | **D-04 leg 1:** revision ack fails, identity survives → `ProgrammerIdentity(None, "<identity>")` | unit (hardware) | W-1 command, `-k revision_fails` | ❌ **Wave 0 (W-1)** — patch `expect_ack` to `(False, "err")` with `comm.firmware_identity` set |
| PROV-05 | **D-04 leg 2:** transport raises → `ProgrammerIdentity(None, None)`, never a bare `None` return | unit (hardware) | W-1 command, `-k transport_error` | ❌ **Wave 0 (W-1)** — F-17: `FirmwareOutdatedError` is a `SerialError`, so it lands in the existing clause |
| PROV-05 | **D-07:** a U+FFFD-bearing identity is scrubbed but stays visibly faulty (not converted to the unknown marker) | unit (hardware) | W-1 command, `-k scrub` | ❌ **Wave 0 (W-1)** |
| PROV-05 | The marker string trips none of the 14 forbidden claim patterns | gate | `python3 tools/check_diagnostic_report_claims.py` → `EXIT=0` | ✅ measured PASS; six candidate wordings pre-checked clean (§G-2) |
| PROV-06 | `render_diff` emits a **labelled** `fw_board_identity` line when populated, and marker + not-attributable clause when `null`; `hw_revision` is **absent** (D-15) | parser | `python3 -m pytest tests/test_parse_devtest_issue.py -o addopts="" -q -k render_diff` | ❌ **Wave 0 (W-2)** — **`render_diff` has ZERO tests today** (F-09). The whole oracle must be created |
| PROV-06 | The three marker literals are equal | parity | `python3 -m pytest tests/test_parse_devtest_issue.py -o addopts="" -q -k marker_string` | ❌ **Wave 0** — one assert; the file already imports both worlds (§P-4) |
| PROV-06 | The skill's `show` render carries the identity, fixes `hw None`, and matches `SKILL.md`'s documented example | manual (checkpoint) | the two `show --body-file` commands in §P-6, plus a diff of `SKILL.md:61-67` against the new output | ❌ **Wave 0 (W-4)** — no harness exists, and building one in the app repo would fail open (§P-6) |
| PROV-06 | Criterion #5 (a triager can attribute without asking) | manual (checkpoint) | Same fixtures; operator reads both renders and confirms attribution is answerable for the populated case and explicitly refused for the null case | ❌ judgement criterion — pair it with W-4, do not claim it as automated |

### Sampling Rate

- **Per task commit:** the quick-run command above (measured 43.7 s for 239 tests) **plus** both
  gates (`check_devtest_orchestrator.py`, `check_diagnostic_report_claims.py`, each < 1 s).
- **Per wave merge:** `python3 -m pytest tests/ -o addopts="" -q` (measured 228.9 s / 1590 tests) —
  and commit first (P-11). Plus `ruff check firestarter/ tests/` and
  `ruff format --check firestarter/ tests/`.
- **Phase gate:** `bash tools/ci_parity.sh` (4 legs: pytest with an empty firmware-sibling root,
  pytest with the sibling present, CI-scoped ruff, the mypy watermark gate). **Leg 4 exits 2 in this
  devcontainer by documented design** — that is the hardened gate refusing to report a count for a
  truncated run, not a defect. Record it as expected; do not add `|| true`. Full suite green before
  `/gsd-verify-work`.

### Wave 0 Gaps

- [ ] **W-1** `tests/test_hardware.py` — no coverage exists for the value-returning revision read at
      all. Add unit legs for: one-connection/one-disconnect (PROV-02), happy path (PROV-01),
      **D-04 leg 1** (revision ack fails, identity survives), **D-04 leg 2** (transport raises →
      `(None, None)`), **D-07** scrub. Use the existing `hw_config` / `make_comm` / `fake_serial`
      fixtures and `patch("firestarter.serial_comm.SerialCommunicator.find_and_connect")`.
      **`make_comm()` sets `firmware_identity = None` by default** (`conftest.py:225`) — a test
      wanting a populated identity must set it explicitly, and the default gives the absent case free.
- [ ] **W-2** `tests/test_parse_devtest_issue.py` — create the first-ever tests for `render_diff`
      (PROV-06). Import it alongside the four names already imported at `:50`.
- [ ] **W-3** `tests/test_parse_devtest_issue.py` — a **new** frozen fixture carrying
      `fw_board_identity: null` (the existing `_B11_BODY` carries a populated value), asserted to
      parse and group unchanged. PROV-04's real-world population is null-bearing reports.
- [ ] **W-4** Skill-render verification harness — **none exists**. Commit two fixture bodies (one
      populated, one null) and a `checkpoint:human-verify` running the two offline
      `show --body-file` commands from §P-6. Do **not** add an app-repo test that reaches into
      `/workspaces/.claude/` (fails open in standalone CI).
- [ ] **W-5** `tests/test_dev_test_cmd.py::make_hardware_manager` — must return a real
      `ProgrammerIdentity`, and gain a second parameter so D-08 and D-13(b) can vary one field. This
      is a fixture change 41 `dev test` invocations depend on; land it before the render/oracle tasks.
- [ ] Framework install: **none needed** — `pytest`, `syrupy`, `ruff`, `mypy` all present.

## Sub-Repo Branch Precondition

`firestarter_app` is on `gsd/v1.31-27c-programming-algorithm-fidelity` (HEAD `3cf429f`). It **must**
be moved to a v1.32 branch off `origin/beta` before any executor is dispatched.

**Verified by content, not ancestry:**

```bash
cd /workspaces/firestarter_app
git fetch origin
git diff --stat gsd/v1.31-27c-programming-algorithm-fidelity origin/beta
#   measured today →  firestarter/__init__.py | 2 +-   (1 file changed, 1 insertion, 1 deletion)
git show origin/beta:firestarter/__init__.py | grep __version__
#   measured today →  __version__ = "3.0.0b21"
```

The **only** content delta between the v1.31 branch tip and `origin/beta` is the version bump
`3.0.0b20` → `3.0.0b21`. `origin/beta` therefore carries v1.31's content in full.

**Ancestry note (F-15):** app PR #51 landed as a **true merge**, not a squash —
`git cat-file -p 91c2add` shows two parents, the second being `3cf429f`. So
`git merge-base --is-ancestor HEAD origin/beta` **succeeds** here. CONTEXT.md's squash caution is a
correct general rule (v1.30's meta PR #44 *was* squashed) but does not apply to this repo's v1.31
merge. Verify by content anyway — it is one command and immune to either shape.

**Create the branch:**

```bash
cd /workspaces/firestarter_app
git checkout -b gsd/v1.32-at28c-write-path-root-cause-report-provenance origin/beta
python3 -c "import firestarter; print(firestarter.__version__)"   # expect 3.0.0b21 (editable install)
```

- Meta repo is already on `gsd/v1.32-at28c-write-path-root-cause-report-provenance` ✓.
- `firestarter/` (firmware) needs **no** branch — Phase 147 changes no firmware. Phase 149 owns that.
- Meta working tree is dirty (`.gitignore`, both submodule gitlinks, untracked `.claude/`,
  `package*.json`). **Stage specific files only** — never `git add -A`.
- **`.gitignore` precondition (F-14):** the `.claude/*` + `!.claude/skills/` un-ignore is
  **uncommitted**. Land it (or `git add -f`) before attempting to commit the skill-script change,
  or the file silently will not be added.
- Editable install: switching branches needs **no** reinstall.

## Project Constraints (from CLAUDE.md)

`/workspaces/CLAUDE.md` (meta repo). Actionable directives and how they bear on Phase 147:

| Directive | Bearing on this phase |
|-----------|----------------------|
| Meta repo tracks only `.planning/` and `.claude/`; neither sub-repo is committed here | Code commits land **inside** `firestarter_app` on its own v1.32 branch; the skill-script edit commits in the **meta** repo |
| **Serial protocol changes must be kept in sync** between `serial_comm.py` and `firestarter.cpp` | **No protocol change here** — the CAP-02 tail already exists on both sides. Any plan task that edits either is out of scope |
| **Constants/flag bits duplicated** between `constants.py` and `firestarter.h` — change both together | **No constant crosses the wire here.** `COMMAND_HW_VERSION` is already paired |
| EPROM database is generated; user overrides in `~/.firestarter/database.json` | Untouched by this phase (Phase 148 owns the generator) |
| Board differences: Uno 512-byte buffer, Leonardo 1024 | Irrelevant to identity capture; the board **name** is the identity's suffix, which is why the combined single string must not be split |
| Python app dev commands run **from `firestarter_app/`** | Every command in this document is `cd`-anchored absolutely |

`firestarter_app/CLAUDE.md` and `firestarter/CLAUDE.md` exist per the meta CLAUDE.md's pointer; the
planner should have executors read the app one before editing. No directive found in this session's
reading contradicts any locked decision.

**Project skills:** `.claude/skills/devtest-triage/SKILL.md` is a **binding edit target** (D-16) and
its documented example output (`:61-67`) must be updated in lockstep with `scripts/devtest_issues.py`.
`.claude/skills/devtest-rootcause/` is the consumer of the triage output but is not edited here. The
"skills must own their scripts" rule forbids importing from `firestarter_app/tools` — see P-4.

## Security Domain

`security_enforcement` is not disabled in `.planning/config.json` (the key is absent → enabled).

### Applicable ASVS Categories

| ASVS category | Applies | Standard control |
|---------------|---------|------------------|
| V2 Authentication | no | No auth surface. `gh` handles GitHub credentials; this phase adds no auth path |
| V3 Session Management | no | No sessions |
| V4 Access Control | no | Local CLI; no privilege boundary crossed |
| V5 Input Validation | **yes** | Two untrusted inputs. **(a)** `comm.firmware_identity` is decoded from firmware bytes with `errors="replace"` and is length-bounded to 32 by the firmware (`firestarter.cpp:214`) — D-07's scrub is the control, and it must be applied at the `hardware.py` boundary before the value can reach a GitHub issue body. **(b)** Every issue body reaching either parser is community-authored and hostile; both parsers already bound size before parsing (`_MAX_BODY_BYTES`, `MAX_BODY`), never `eval`/`exec`, never shell out, and never interpolate body text into a command. **Preserve all four properties** — the skill's `SKILL.md:88-92` states them as a contract |
| V6 Cryptography | no | `dedup_fingerprint` is a non-security dedup hash and is **not** changed (F-10) |
| V7 Error Handling / Logging | **yes** | `logger.error(f"Failed to read hardware revision: {e}")` already exists and stays. The scrubbed identity may be logged; it carries no secret. Do **not** log the raw pre-scrub bytes |
| V8 Data Protection / Privacy | **yes** | The identity travels to a **public** GitHub issue. `submit.py::sanitize_dict` (`:126-143`) already deep-scrubs home-dir paths, `/dev/tty*`, `/tmp` paths and the username from every string leaf of `to_dict()` — the new value inherits that automatically. Verify it does, rather than assuming |
| V12 Files / Resources | marginal | Report artifacts are written under `get_config_dir()/reports` with `_sanitize_chip_token`-derived filenames; unchanged |
| V14 Configuration | no | No new env var, no new flag |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard mitigation |
|---------|--------|---------------------|
| Malicious/garbled firmware identity injected into a public issue body (markdown or fence-breaking payload) | Tampering / Spoofing | D-07 scrub at the `hardware.py` boundary + `json.dumps` escaping inside the fenced block + `sanitize_dict`'s recursive pass. **A `` ``` `` sequence inside the identity is escaped by `json.dumps`, so it cannot break out of the fence** — but the *rendered* triage line is plain text, so a scrub that keeps only printable ASCII closes the render path too |
| A spoofed identity making a broken board look patched | Spoofing / Repudiation | Out of scope to prevent, and explicitly so: the report says what the *board claimed*. The Evidence Ceiling already forbids treating any report as proof; D-14's clause states attributability rather than authenticity |
| Hostile issue body driving the parsers to arbitrary code / resource exhaustion | Tampering / DoS | Existing controls: size bound before parse, `JSONDecodeError`-guarded `json.loads`, fixed argv to `gh`, fail-soft extraction. **Do not add a code path that formats body content into a shell command** |
| Log injection via a newline-bearing identity | Tampering | The scrub removes non-printables including `\n`/`\r` |
| An extra serial connection energizing a socketed part | (hardware safety, not STRIDE) | PROV-02 / SAFE-02 — and the firmware's own note at `firestarter.cpp:200-205`: the identity ack is emitted before `firestarter_operation_init`, so the VPP regulator is not engaged. Zero new connections means zero new energize events |

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|-------|---------|---------------|
| A1 | `typing.NamedTuple` with class syntax and `Optional[str]` fields is importable on Python 3.9 | Standard Stack, E-1 | Low. No 3.9 interpreter is available here to run. `NamedTuple` class syntax has been available since 3.6.1 and `Optional[str]` is 3.9-safe; CI runs 3.11 so the practical risk is nil. `[ASSUMED]` |
| A2 | `diagnostic_report.py`'s class-body `str \| None` makes it un-importable on 3.9 (P-9) | Pitfall P-9 | Low. Reasoned from PEP 604 semantics (`type.__or__` added in 3.10) plus the absence of `from __future__ import annotations` — **not** executed on 3.9. If wrong, P-9's advice ("use `Optional[str]` in `hardware.py`") is still correct by module convention. `[ASSUMED]` |
| A3 | A zero-length CAP-02 identity tail (`ver_len == 0`) yields `""` rather than `None` (P-8) | Pitfall P-8 | Low-medium. Read from `serial_comm.py:410-413`'s slice arithmetic, not exercised. If wrong, the `is None`-not-`or` advice is harmless. `[ASSUMED]` |
| A4 | The full app CI suite is green on `origin/beta` | Environment Availability | Low. Measured green on the **v1.31 branch tip** (1590 passed), which differs from `origin/beta` by one version-string line only. `[ASSUMED]` for beta specifically |
| A5 | `ci_replica_venv.sh` falling back to `python3` (3.12) yields a mypy count comparable to CI's 3.11 | Environment Availability | Low. `mypy` targets `python_version = "3.10"` regardless of the running interpreter, so the population should match; not executed this session. `[ASSUMED]` |
| A6 | No `.claude/skills/devtest-triage` consumer other than `SKILL.md` reads the `show` output format | Runtime State Inventory | Low. `grep` found no programmatic consumer; `devtest-rootcause` reads it as prose. `[ASSUMED]` |

Everything else in this document is `[VERIFIED]` by direct execution or file read this session, or
`[CITED]` to a specific file:line.

## Open Questions

1. **Should the identity capture move, or stay where it is?**
   - What we know: CONTEXT.md leaves this to discretion with a default of "keep it where it is
     today" (before `run_plan`, `cli_handlers.py:2501`).
   - What research found: **no reason to move it.** Moving it after `run_plan` would open a *second*
     connection (the whole SAFE-02 problem the current comment describes) and would put an energize
     event after the write. Capturing before the plan also means a report exists even if `run_plan`
     is interrupted.
   - Recommendation: **keep it at `:2501-2507`.** Treat this discretion item as resolved.

2. **How much of `SKILL.md` must change?**
   - What we know: `:61-67` reproduces the `show` output verbatim, including `hw Rev 2.0-class…`.
   - What's unclear: whether the plan also wants the example to show the null case.
   - Recommendation: update `:61-67` to the new populated-case output (mandatory — a stale example is
     a trust defect), and add the null-case render only if it fits without bloating §2 of the skill.

3. **Should `""` be treated as unknown or as a visible fault?**
   - What we know: D-07 says a mangled identity stays visible as evidence of a transport fault.
   - What's unclear: an empty string is arguably "no identity" rather than "mangled".
   - Recommendation: treat `""` as a **fault**, rendering it distinguishably from `None` (e.g. the
     marker only for `None`). If the planner prefers to collapse them, say so explicitly and test it
     — the failure mode to avoid is deciding it implicitly via `or`.

4. **Does the plan want a claim-pattern assertion over the two parser markers?**
   - What we know: neither parser is claim-gated (P-5).
   - Recommendation: a small test importing `FORBIDDEN_PATTERNS` from
     `tools.check_diagnostic_report_claims` and asserting the two parser marker strings match none
     of them. Cheap; closes a fail-open. Optional, not required by any PROV requirement.

## Sources

### Primary (HIGH confidence — measured on disk / executed this session)

- `firestarter_app/firestarter/cli_handlers.py` — `:2162-2177` (`_sanitize_chip_token`),
  `:2180-2192` (`_chip_id_fields`), `:2494-2507` (the defect), `:2520-2592` (artifact + submit path)
- `firestarter_app/firestarter/hardware.py` — `:1-30` (imports/convention), `:105-147`
  (`get_hardware_revision` tail + `read_hardware_revision_value`)
- `firestarter_app/firestarter/serial_comm.py` — `:110-175` (CAP-02/03 attribute declarations),
  `:395-425` (identity decode), `:600-615` (`expect_ack`), `:640-650` (`disconnect`),
  `:772-813` (`_validate_hardware_revision`), `:850-895` (`_probe_port`), `:922-988`
  (`find_and_connect`)
- `firestarter_app/firestarter/diagnostic_report.py` — `:1-20` (module contract), `:45-131`
  (`SCHEMA_VERSION`, `NOT_MEASURED`, `AutoCapture`), `:183-196` (`is_submittable`), `:400-412`
  (`to_dict` identity keys), `:500-565` (`render`), `:584-586` (`to_json_block`)
- `firestarter_app/firestarter/submit.py` — `:126-143` (`sanitize_dict`), `:166-198`
  (`build_title`/`build_body`), `:575-620` (`submit_report` gating)
- `firestarter_app/firestarter/exceptions.py` — `:13-104` (the `SerialError` hierarchy)
- `firestarter_app/tools/parse_devtest_issue.py` — `:1-52` (stdlib-only contract), `:77-106`
  (presence-only detection), `:192-214` (`render_diff`), `:251` (its only call site)
- `firestarter_app/tools/check_devtest_orchestrator.py` — `:86-130` (targets), `:140-181`
  (`_HANDLER_FUNCTION_NAMES`), `:500-546` (`_scan_target_functions`, `_assert_host_only`),
  `:547-625` (`main`) — **executed, PASS, EXIT=0**
- `firestarter_app/tools/check_diagnostic_report_claims.py` — `:86-160`
  (`FORBIDDEN_PATTERNS`, `REQUIRED_CAVEAT_PATTERN`) — **executed, PASS, EXIT=0**; pattern table
  loaded and six candidate markers probed
- `firestarter_app/tools/check_mypy_watermark.py` — `:92-140` (`get_watermark`, `mypy_argv`,
  `run_mypy`) — **executed, EXIT=2 as documented**
- `firestarter_app/tools/ci_parity.sh`, `tools/ci_replica_venv.sh` — leg structure and their
  explicit non-mirror boundaries
- `firestarter_app/tests/conftest.py` — `:201-236` (`make_comm`), `:239-330` (`make_app_context`)
- `firestarter_app/tests/test_dev_test_cmd.py` — `:365-401` (`make_hardware_manager`), `:703-743`
  (artifact + `hw_revision` end-to-end), `:820-866` (`TestAbsentChipHardFail`)
- `firestarter_app/tests/test_diagnostic_report.py` — `:120-140` (`_build_report`), `:505-540`
  (schema + auto-capture assertions), `:965-1020` (`_rendered_text` + the both-surfaces pattern)
- `firestarter_app/tests/test_parse_devtest_issue.py` — `:36-56` (imports), `:110-148`
  (detection/presence), `:355-400` (`_B11_TITLE`/`_B11_BODY`), `:456-505` (legacy legs)
- `firestarter_app/tests/test_check_devtest_orchestrator.py` — `:87-105` (subprocess harness),
  `:493-530` (name-resolution invariant), `:545-625` (the AST-derived equality invariant)
- `firestarter_app/tests/test_fwguard.py` — `:30-70` (`_probe_with_identity`, the ring-fence harness)
- `firestarter_app/tests/test_hardware.py` — 13 tests, all `patch(find_and_connect)`; **no coverage
  of the value-returning read**
- `firestarter_app/pyproject.toml` — `:105-137` (pytest/ruff config), `:138-175` (mypy config +
  watermark `35`)
- `firestarter_app/.github/workflows/ci.yml` — `:184-230` (the exact CI gate steps and their scopes)
- `firestarter/src/firestarter.cpp` — `:150-230` (the CAP-01/02/03 `MSG_OK_READY` emit, before
  dispatch), `:325-358` (the `#ifdef HARDWARE_REVISION`-gated `case CMD_HW_VERSION` + `default:`)
- `firestarter/src/hardware_operations.cpp` — `:95-115` (`fw_get_version`, `hw_get_version`)
- `/workspaces/.claude/skills/devtest-triage/scripts/devtest_issues.py` — `:170-190` (`_summarize`),
  `:240-275` (`cmd_fold` renders), `:294-345` (`cmd_show`) — **executed offline against synthesized
  populated and null bodies**
- `/workspaces/.claude/skills/devtest-triage/SKILL.md` — `:55-95` (the documented `show` example)
- `/workspaces/.gitignore` (+ `git diff`) — the **uncommitted** `.claude/skills/` un-ignore
- `git` history: `firestarter_app` `git cat-file -p 91c2add` (two parents), `git diff --stat`
  v1.31-branch↔`origin/beta`, `git show origin/beta:firestarter/__init__.py`
- **Executed test runs:** 7-file subset (239 passed / 43.7 s); full suite (1590 passed, 30 snapshots,
  228.9 s); `ruff check` + `ruff format --check` at CI scope (clean, 135 files formatted)

### Secondary (MEDIUM confidence)

- `/workspaces/.planning/research/PITFALLS.md` §P-07 — the fail-open allow-list, **re-verified as
  now closed** by the Phase 131 equality invariant
- `/workspaces/.planning/PROJECT.md` §Current Milestone: v1.32 — the Evidence Ceiling and kickoff
  decisions
- `/workspaces/.planning/REQUIREMENTS.md` §Report Provenance (PROV) — read in its hand-corrected
  form (PROV-03 and PROV-05 both carry the 2026-08-18 correction notes; D-06/D-10 are **already
  landed**, so no plan task should re-do them)
- `/workspaces/.planning/ROADMAP.md` §v1.32 spine + §Phase 147 — criteria #2 and #4 both carry the
  correction notes; confirmed landed

### Tertiary (LOW confidence — not relied on)

- `.planning/graphs/graph.json` — **NOT USED.** `gsd-tools graphify status` reports
  `stale: true`, `age_hours: 1149`, `commits_behind: 1366`, `built_at_commit: f4150b8` vs current
  `82f11fd`. Querying it would risk injecting stale file:line coordinates into a document whose
  entire value is measured coordinates. Every relationship in this research was derived by direct
  `grep`/read instead. A rebuild is advisable before any phase relies on it.
- **No external documentation provider was consulted.** The `research-plan` seam was not exercised
  because this phase has **zero external dependencies**: no package is added, no third-party API is
  called, and every claim is answerable from the three local repositories. Consulting a web or docs
  provider would have added unverifiable material to a fully measurable question.

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|------|-------|--------|
| Standard stack | HIGH | No new dependency; every tool version read from the live environment |
| Capture seam / architecture | HIGH | Traced end to end through host **and** firmware source; D-04's mechanism confirmed in `firestarter.cpp`, not inferred |
| Gate behaviour | HIGH | Both gates executed; candidate marker wordings run through the live pattern table |
| Test-mock churn surface | HIGH | Exhaustive `grep` (8 hits, 3 files) plus an empirical check of `Mock(spec=)` strictness |
| Validation architecture | HIGH for what exists, HIGH for the gaps | Baselines measured (239 / 43.7 s; 1590 / 228.9 s); the four Wave 0 gaps proven absent by grep, not assumed |
| Pitfalls | HIGH | P-1, P-3, P-4, P-6, P-7, P-9, P-10 each traced to a specific file:line; P-9 reasoned from PEP 604 (see A2) |
| Python-3.9-floor claims | MEDIUM | No 3.9 interpreter available (A1, A2) |
| Branch precondition | HIGH | Verified by content diff and by inspecting the merge commit's parents |

**Research date:** 2026-08-18
**Valid until:** 2026-09-17 (30 days — the codebase is stable in this area; but re-verify
`origin/beta`'s tip and the `.gitignore` state if any beta cut fires in between, and re-run
`gsd-tools graphify` before any phase intends to trust the knowledge graph)
