# Phase 120: HOST — CLI surface, wire emission, capability refusal - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-29
**Phase:** 120-HOST — CLI surface, wire emission, capability refusal
**Areas discussed:** Capability partition (HOST-04); `dev sdp` gating semantics (HOST-01); Outcome reporting + exit code (HOST-05); Parity test shape (HOST-03); HOST-06's proof artifact; `--skip-sdp-unlock` scope (HOST-02); plus an unplanned `dev test` redesign routing decision raised by the operator

---

## Capability partition (HOST-04)

### Q1 — The basis of the SDP capability partition

Surfaced before asking: on a part with no SDP command decoder the sequence is **not inert**. Post-117 the command writes reach silicon with `/WE` asserted, so `0xAA`/`0x55`/`0xA0` are stored as data at the bus-truncated magic addresses. `dev sdp 2816 enable` would report "sequence emitted" having corrupted three bytes. Reasoned inference from the emitter's shape, not a bench result.

| Option | Description | Selected |
|--------|-------------|----------|
| Fail-closed allow-list | Only parts on an explicit SDP-capable list may receive cmd 9/10; everything else, including unrecognised entries, is refused. ~79 of 84 tokens to enumerate. | ✓ |
| Literal 5-part deny-list | HOST-04 verbatim: `FM28V020`, `MB85R256H`, `2804`, `2816`, `2817`. Leaves XICOR `X2804A`/`X2816A`/`X2816B,C` and EXEL `XL2804A`/`XL2816A` permitted. | |
| Widened pre-SDP deny-list | HOST-04's five plus the same-generation XICOR/EXEL parts by part-number shape. Still default-permit for future additions. | |
| DB-derived structural rule | Refuse by pinout/size only. Over-refuses `DIP24_2816`, and cannot see the two FRAM parts at all. | |

**User's choice:** Fail-closed allow-list.
**Notes:** Verified during framing that both FRAM parts (`FM28V020`, `MB85R256H`) carry `electrical.type == "EEPROM"` in the DB, so no structural rule can find them and the existing `etype in ("SRAM","FRAM")` idiom is blind to them. The validation ceiling already concedes the partition is unprovable per family, which argues for refusal as the default rather than a curated exception list.

### Q2 — How the allow-list is keyed, and where fail-closed actually lives

| Option | Description | Selected |
|--------|-------------|----------|
| Allow-set in code + exhaustiveness gate | Production code holds the allow-set (runtime fail-closed); a pytest asserts allow ∪ refuse == exactly the 84 `algorithm==13` entries. | ✓ |
| Refuse-set in code + exhaustiveness gate | Far less code; fail-closed only at CI time. | |
| Structural allow rule + carved exceptions | Compact-looking; the curation hides inside the rule instead of disappearing. | |

**User's choice:** Allow-set in code + exhaustiveness gate.
**Notes:** Decided by a fact verified mid-question — `~/.firestarter/database.json` merges into the live DB at `database.py:187-199` and CI never sees it, so a CI-only gate leaves the one path where a wrong answer reaches real silicon unguarded.

### Q3 — Where the capability predicate lives

| Option | Description | Selected |
|--------|-------------|----------|
| New `firestarter/sdp_capability.py` | Pure `(bool, reason)` predicate; one stable file+symbol for Phase 121's GATE-01 AST gate. | ✓ |
| Beside `_SRAM_PROTO_IDS` in `eprom_operations.py` | Genuine in-tree precedent (`check_eprom_blank:1661-1676`), but buries a curated table in a 1733-line module. | |
| In `cli_handlers.py`'s `dev sdp` handler | Whole gate reads top-to-bottom, but couples a safety predicate to Click. | |

**User's choice:** New `firestarter/sdp_capability.py`.

### Q4 — Whether HOST-04 covers `write`'s automatic unlock

Surfaced before asking: firmware's auto-unlock is protocol-keyed, not part-keyed, so every `0x0D` write emits the 6-write sequence. On the non-SDP subset that leaves `0x2AAA←0x55` / `0x5555←0x20` before the payload — masked by a full-image write, persistent for a `-a`-ranged or short one.

| Option | Description | Selected |
|--------|-------------|----------|
| Auto-set the skip flag on write, and report it | Host sets `FLAG_SKIP_SDP_UNLOCK` for a refused part and prints one mandatory line saying so. | ✓ |
| `dev sdp` only; record the write exposure as a finding | Keeps the ROADMAP boundary exactly; ships a known corruption path for another milestone. | |
| Refuse `write` outright on those parts | Maximally fail-closed; breaks working functionality over a two-byte residue. | |

**User's choice:** Auto-set the skip flag on write, and report it.
**Notes:** Owned consequence — `write` behaviour for the refused subset diverges from `3.0.0b11` without the user asking, so the report line is mandatory per 118 D-01, and the divergence must be stated in the SUMMARY as deliberate.

---

## `dev sdp` gating semantics (HOST-01)

### Q1 — The form of the consent gate

| Option | Description | Selected |
|--------|-------------|----------|
| No mode flag; TTY confirm unless `-y` | The subcommand is the mode, so a `--destructive` flag would be mandatory on every invocation and carry no information. | (see below) |
| Mirror `dev test`'s `--destructive` exactly | Consistency with the one existing gated command. | |
| Typed chip-name confirmation | Stronger pre-hoc gate given the state is unreadable; new interaction pattern. | |

**User's choice:** Free-text — *"We must discuss if the destructive flag and other flags is not working as I want the to work."*
**Notes:** Answered with a full inventory of the current flag surface (all eight wire flags plus the two `dev test`-local host flags) and five specific defects: the flag surface advertises an erase capability `0x0D` does not have in three places (`FLAG_CAN_ERASE` set from the DB for all 84, `--skip-erase` accepted, `erase` now refused by firmware); `-b` is *mandatory* on `0x0D` for the wrong reason and is spelled `--no-blank-check`; `-b` has opposite polarity on `write` vs `erase`; `-y`/`--destructive` are `dev test`-local so no project-wide consent idiom exists; `-f/--force` covers two unrelated mismatches with one bit. Also corrected a stale saved note claiming `write -b` skips erase — Phase 92 decoupled them.

The operator then specified a `dev test` redesign (see the routing section below). Its first clause — *no flags* — settled this question: `dev sdp` gets no mode flag and an interactive confirm.

### Q2 — Whether `-y` survives, and off-TTY behaviour

| Option | Description | Selected |
|--------|-------------|----------|
| Keep `-y`; refuse off-TTY without it | With no mode flag, nothing could stand in as consent, so a bare invocation in a pipe must not mutate. Satisfies HOST-01's `-y` verbatim. | ✓ |
| Keep `-y`; proceed off-TTY | Mirrors `dev test`'s D-02, but here the consent stand-in would be the mere absence of a TTY. | |
| Drop `-y`; always ask | Cleanest expression of no-flags-always-ask; unusable from a script and needs a requirement-intent correction. | |

**User's choice:** Keep `-y`; refuse off-TTY without it.

### Q3 — Whether `enable` and `disable` share a gate

| Option | Description | Selected |
|--------|-------------|----------|
| Same gate, different confirm text | One code path, two strings — `enable` warns about refused writes and the unreadable result, `disable` about protection being removed. | ✓ |
| Gate `enable` only | Lock is the stranding direction; unlock only makes a chip more writable. Leaves `disable` as the one state-mutating command with no confirm. | |
| Gate both, require `-y` for `enable` even on a TTY | Strongest anti-accidental-lock; reintroduces the always-mandatory flag just removed. | |

**User's choice:** Same gate, different confirm text.

### Q4 — Pre-wire gate ordering

| Option | Description | Selected |
|--------|-------------|----------|
| absent → capability → support-status → confirm → serial | Capability outranks support-status so an `adapter-required` part with no SDP hears the useful answer; confirm last so nobody consents to something then refused. | ✓ |
| absent → support-status → capability → confirm → serial | Uniform CLI error precedence; the adapter message masks the capability answer for 9 parts. | |
| Skip `resolve_chip`; capability + confirm only | Follows `dev test`'s precedent literally; makes `dev sdp` a second bespoke resolution path. | |

**User's choice:** absent → capability → support-status → confirm → serial.

---

## Routing decision — the `dev test` redesign (raised mid-discussion, out of Phase 120 scope)

**Operator's specification, verbatim in intent:** `dev test` takes no flags; "destructive" applies only to UV-erasable EPROMs; the test stops and asks whether to do a destructive write, where yes means the full EPROM may be written and no means only a small part is written; every test always asks whether the result should create an issue, checking first whether the user has already reported an identical one and creating a new issue only if it differs; and `gh` is used instead of the URL path wherever it can be.

| Option | Description | Selected |
|--------|-------------|----------|
| Amend Phase 121's scope | Phase 121 already owns `dev test` for DEVTEST-01 and is already flagged as needing research for this exact ripple surface. One research pass, one golden regeneration. Grows Phase 121 on the critical path. | ✓ |
| New phase after 121, before close | Keeps Phase 121 tight; the Phase-112 reversal gets its own home. Two passes over the same op vocabulary and golden. | |
| Capture as a v1.23 seed | Keeps v1.22 on its stated arc; leaves b11's misfiling `--submit` bug shipped another milestone. | |

**User's choice:** Amend Phase 121's scope.
**Notes:** Following 119-09's precedent, the amendment itself becomes an **owned task in Phase 120** (D-20) rather than a note. Three collisions recorded for the amendment to carry: it reverses three locked decisions (Phase 112 Plan 04's deliberate removal of all interactive prompts per `112-UAT.md`, SAFE-01's CLI-only `--destructive`, SAFE-03's only-remaining-input statement); "non-destructive means a partial write" is a contract change to `derive_plan`/`locked_destructive` that ripples through the closed six-string op vocabulary into the issue parser, report renderer, ladder taxonomy, `dedup_fingerprint` and the `audit_coverage_matrix` golden; and "destructive only for UV-erasable" needs an explicit axis pick, with `electrical.type == "UV-EPROM"` available but type-string keys historically fragile here. Carried facts: `--submit`'s "never on a bare run" contract contradicts always-ask; b11's `--submit` misfiles into `firestarter_app` rather than `henols/firestarter_prom`; `gh issue create --label` aborts unless the label pre-exists and the user has write access. Also noted that ~60% of the issue half already exists from Phase 113 (`submit.py`, sanitizer, `dedup_fingerprint`, gh-first tiering).

The wider flag re-design (`-f` splitting, `-b` polarity, project-wide `-y`) was **not** folded and is recorded as a deferred idea needing its own phase.

---

## Outcome reporting + exit code (HOST-05)

Two findings surfaced before asking. **F-120-02:** `_log_response` special-cases only `ERROR` and `WARN`, so the entire INFO band falls through to `logging.DEBUG` (`serial_comm.py:234-238`) while `_setup_logging` sets root to `INFO` unless `-v` — every Phase 118/119 SDP report line is invisible at default verbosity, so OBS-01 is satisfied in firmware and discarded by the host. **F-120-03:** `MSG_INFO_SDP_LOCK_DONE_US` (`0x61`) carries the "protection state is not readable" caveat but `MSG_INFO_SDP_UNLOCK_DONE_US` (`0x5F`), reused from 118 by 119 D-13, does not — so `dev sdp <chip> disable` has no firmware-supplied honesty line.

### Q1 — What `dev sdp` reports

| Option | Description | Selected |
|--------|-------------|----------|
| Host prints its own summary line | Independent of the severity bug, symmetric across both directions, satisfies HOST-05 in the host. Caveat wording then lives in two places. | |
| Fix the severity mapping instead | Makes OBS-01 true in practice with no new host text; still leaves the unlock direction with no caveat. | |
| Both: promote INFO and add the host line | Maximum visibility, OBS-01 genuinely true, unlock gap covered. Widest blast radius; duration risks appearing twice. | ✓ |

**User's choice:** Both: promote INFO and add the host line.
**Notes:** Verified after the choice that the blast radius is much smaller than stated — every other INFO id is emitted through the `FLAG_VERBOSE`-gated `LOG_INFO_ID*` family (`logging_id.h:44-46`), which firmware only sends when the host passed `-v`. Of 22 INFO-band entries, only five (`0x5E`, `0x5F`, `0x60`, `0x61`, `0x62`) are unconditional, so default-verbosity output changes for exactly those. One edge case recorded (F-120-07): `rurp_hw_rev_utils.h:96` emits the INFO-band id `MSG_INFO_HW` via `LOG_WARN_ID_U8`, and the host reads severity from the catalog entry rather than the frame, so an unknown-revision board will newly print one line.

### Q2 — How the duration is split between firmware and host lines

| Option | Description | Selected |
|--------|-------------|----------|
| Host line carries verdict + caveat only | Duration stays exclusively on the firmware's `0x5F`/`0x61` line; nothing printed twice, no second copy of a `micros()` figure to drift. | ✓ |
| Host line carries everything | One consolidated line; duplicates a measured number whose provenance is the firmware bracket. | |
| Accept the double print | Deliberate redundancy; the same figure in consecutive lines reads like a bug. | |

**User's choice:** Host line carries verdict + caveat only.

### Q3 — Exit code

| Option | Description | Selected |
|--------|-------------|----------|
| Plain `0/1`, WARN stays in the text | Matches every other command; applies 119 D-12's reasoning at the host end — no exit code can honestly say more than "the sequence was emitted". | ✓ |
| `0/1/2` like `dev test` | Gives scripts something actionable on a `t_BLC` WARN; edges toward encoding a silicon-state confidence the ceiling forbids. | |

**User's choice:** Plain `0/1`, WARN stays in the text.

---

## Parity test shape (HOST-03)

### Q1 — How the constants-parity test is extended

| Option | Description | Selected |
|--------|-------------|----------|
| Parse the header, assert two-way correspondence | Real bidirectional `CMD_*`/`FLAG_*` mapping plus a planted-violation fixture. Needs an exemption list (`CMD_IDLE`, the `#ifdef DEV_TOOLS` pair) and adds a firmware-scanning gate to a fragile set. | ✓ |
| Add the three literals | Satisfies HOST-03's text verbatim at almost no cost; reproduces the hollowness that let cmd 9/10 through. | |
| Literals plus a `COMMAND_NAMES` completeness test | Closes the actual `KeyError` crash path without taking on header parsing. | |

**User's choice:** Parse the header, assert two-way correspondence.
**Notes:** Framing established that the existing test asserts hardcoded literals with the firmware define named only in a trailing comment, under a `FW_ABSENT` skipif keyed on the header merely existing — 119's own CONTEXT had already flagged that firmware-only additions do not trip it.

### Q2 — `COMMAND_NAMES` coverage and absent-firmware behaviour

| Option | Description | Selected |
|--------|-------------|----------|
| Cover `COMMAND_NAMES`; keep `FW_ABSENT` skip | One gate closes both value drift and the `KeyError` path; host-only CI stays green. Residual gap: the gate skips entirely in host-only CI. | ✓ |
| Cover `COMMAND_NAMES` in a separate always-on test | Needs no firmware so it could never skip — `test_sdp_db_invariant.py`'s no-skip-marker reasoning. Two functions instead of one. | |
| Header parsing only | Smallest change; leaves the one failure mode HOST-03 calls mandatory unguarded. | |

**User's choice:** Cover `COMMAND_NAMES`; keep `FW_ABSENT` skip.
**Notes:** Residual host-only-CI gap recorded in CONTEXT.md as a known-and-explained condition rather than silently accepted.

---

## HOST-06's proof artifact

### Q1 — Landing order, or a runtime guard

Surfaced before asking: the two halves of the wire surface have different detectability. An unknown command returns `MSG_ERR_UNKNOWN_CMD`; an unknown flag bit is silently ignored, which is exactly the harm HOST-06 names.

| Option | Description | Selected |
|--------|-------------|----------|
| Version-gate the flag; error-map the command | Cheapest correct mechanism per half. Needs a version floor for a beta not yet cut. | ✓ |
| Version-gate both halves | Uniform, one mechanism; a version string is a weak capability proxy and the free error mapping goes unused. | |
| Landing order plus a recorded statement | Zero cost, requirement text satisfied; protects nothing at runtime, and `pip install -U` without `fw --install` is the default outcome. | |

**User's choice:** Version-gate the flag; error-map the command.

### Q2 — How the flag avoids silent ignoring, given the host cannot see a `b`-suffix

Surfaced before asking: firmware is at `VERSION "3.0.0b11"` and `_probe_port` captures with `re.search(r"FW:\s*([\d.x]+)", …)`, so `"3.0.0b11"` reaches the comparator as `"3.0.0"`. A b11-vs-b12 floor is not implementable as-is (F-120-04). But `MSG_WARN_SDP_UNLOCK_SKIPPED` (`0x86`) is emitted whenever the flag *is* honoured.

| Option | Description | Selected |
|--------|-------------|----------|
| Detect via the `0x86` ack | Zero transport change, no version floor, uses Phase 118 machinery; converts the silent failure into a loud one. Detects after the fact rather than preventing. | ✓ |
| Widen the probe regex, floor at the next beta | Genuine pre-emptive refusal via `packaging.version.Version`; edits the ring-fenced transport version-capture path and needs a guessed floor. | |
| Require a numeric minor bump to `3.1.0` | Pre-emptive with the smallest host diff; makes HOST-06 depend on a release-versioning decision belonging to Phase 122's CLOSE-03. | |

**User's choice:** Detect via the `0x86` ack.
**Notes:** The honest limitation — on old firmware the unlock has already been emitted by the time the user is told — is to be stated in-source, not glossed.

---

## `--skip-sdp-unlock` scope (HOST-02)

Command surface settled by the code rather than preference: firmware auto-unlocks only in `eeprom28c_write_init`, so `write` is the only command with an unlock to decline.

### Q1 — Behaviour on a non-`0x0D` chip

| Option | Description | Selected |
|--------|-------------|----------|
| Warn and proceed | User learns the request was vacuous without losing a working operation; a blanket-flag script still works across a mixed batch. | ✓ |
| Refuse before the wire | Consistent with the phase's refuse-over-warn posture; fails a write that would have succeeded, to prevent a no-op with no silicon risk. | |
| Pass it through silently | Smallest code; leaves the user believing they declined something. | |

**User's choice:** Warn and proceed.

### Q2 — Where the `0x100` bit is mapped

| Option | Description | Selected |
|--------|-------------|----------|
| New `build_flags()` param, threaded from `_build_op_flags` | Keeps every wire-flag bit mapped in one function, as `FLAG_SKIP_ERASE` and `FLAG_SKIP_BLANK_CHECK` already are. Must be keyword-only with a `False` default because the signature is BUG-1-characterization-pinned. | ✓ |
| OR the bit in `_build_op_flags` after the call | In-file precedent exists (the OE/CE flags); splits bit-mapping across two functions. | |

**User's choice:** New `build_flags()` param, threaded from `_build_op_flags`.

---

## Claude's Discretion

- Exact confirm wording, refusal reason strings, and the host summary line's phrasing (must satisfy the honesty requirement in the text itself; refusal reasons should name *why* — pre-SDP generation / FRAM / not `0x0D` / unrecognised).
- Whether `dev sdp` is a Click sub-group or a `<chip>` argument plus an `enable|disable` `click.Choice`.
- The allow-set's concrete data shape — `frozenset` of tokens, or a token→reason mapping.
- How the header parser extracts the defines — a new regex, or reuse of `tools/check_is_memory_cmd_no_ifdef.py`'s brace-matched extraction and its fail-closed `FIRESTARTER_*_SRC` seam.
- The exemption-list mechanics for `CMD_IDLE` and the `#ifdef DEV_TOOLS` pair, provided exemptions are enumerated explicitly rather than pattern-skipped.
- Severity of the missing-`0x86` failure (ERROR vs WARNING) and its wording — that it fails the operation is decided.
- Whether the auto-set report line is one line or two, provided it is unconditional and visible at default verbosity.
- Plan ordering, subject to two hard constraints: `constants.py` + `COMMAND_NAMES` must precede any plan emitting cmd 9/10 (`_setup_operation` `KeyError`s without the name entry), and `sdp_capability.py` must precede both importers.

## Deferred Ideas

- The `dev test` redesign — routed to Phase 121; only the ROADMAP/REQUIREMENTS amendment lands in Phase 120 (D-20).
- The wider CLI flag re-design — splitting `-f/--force`'s two meanings, reconciling `-b`'s opposite polarity between `write` and `erase`, a project-wide `-y` idiom. Needs its own phase.
- The `0x0D` flag-surface honesty problem — `FLAG_CAN_ERASE` set and `--skip-erase` accepted on a family with no erase op; GATE-02 currently only documents it.
- `MSG_INFO_SDP_UNLOCK_DONE_US` (`0x5F`) missing the honesty caveat `0x61` carries — a catalog change, so out of scope for a host-only phase. Phase 121 or 122.
- Widening `_probe_port`'s `[\d.x]+` version capture so pre-release suffixes are comparable.
- `dev sdp`'s release-channel disposition against 999.15/gh#8, which currently keeps only `dev read` + `dev test` in stable.
- A separate always-on `COMMAND_NAMES` completeness test — considered at Q2 and declined in favour of one gate.
- Carried forward from Phase 119: the third-strobe trace-recorder widening; the `infoic.xml` `page_size` decode phase (approved, still not in ROADMAP.md); SDP-F7 (datasheet verification of SDP magic addresses — directly relevant to the allow-set's membership) and SDP-F8; `prove-pio-dev-flag-fails-closed.md` items 1–3.

### Reviewed Todos (not folded)

- `decode-infoic-flags-bits-14-15-protect-metadata.md` (0.6) — real SDP-protection metadata that would bear on the allow-set, and Phase 119 named Phase 120 as a candidate home. Not folded: HOST-04 requires zero DB change, and `build_db.py` output is guarded by `diff_db.py` identity (GATE-03) and CLOSE-01's unchanged-84 count. Revisit in the `page_size` phase.
- `fold-response-code-into-log-macro.md` (0.2) — declined at 118, at 119, and again here; conflicts with 117 D-05 / 118 D-02 / 119 D-12, and the plain `0/1` exit code decided above depends on the SDP path leaving `response_code` untouched.
- Ten further matches carry the same disposition as Phases 116–119 (generic keyword overlap): VPP-on-reads, avrdude fallback, COBS frame deadline, JP4/JP5 renderer, Rev-0 photography, MODIFICATIONS trace, dead `json_init()`, v1.28 PY32 roadmap prior-art, `DATA_BUFFER_SIZE` spike.
