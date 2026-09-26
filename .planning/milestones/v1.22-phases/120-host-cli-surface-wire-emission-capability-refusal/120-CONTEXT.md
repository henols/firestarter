# Phase 120: HOST — CLI surface, wire emission, capability refusal - Context

**Gathered:** 2026-07-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Make Phase 119's SDP lock/unlock capability reachable from the CLI, correctly wired to the new
firmware commands — and ensure the host never emits a flag or command that current firmware would
silently ignore or misinterpret.

**In scope (HOST-01..06):**
- `firestarter dev sdp <chip> <enable|disable>` behind an interactive confirm + `-y` + the SAFE-04
  absent-chip hard-fail (HOST-01).
- `write --skip-sdp-unlock` emitting `FLAG_SKIP_SDP_UNLOCK 0x100` on the wire (HOST-02).
- `COMMAND_SDP_UNLOCK 9` / `COMMAND_SDP_LOCK 10` / `FLAG_SKIP_SDP_UNLOCK 0x100` in
  `constants.py`, with **mandatory `COMMAND_NAMES` entries**, and the constants-parity test
  rebuilt as a real header-parsing gate (HOST-03).
- A pre-wire capability refusal keeping SDP commands away from the non-SDP subset inside the
  `0x0D` bucket, **resolved in code with zero `chip_database.json` change** (HOST-04).
- The SDP outcome reported honestly, never as a fabricated state boolean (HOST-05).
- The host-never-before-firmware invariant upheld in practice, not just documented (HOST-06).
- **Newly pulled in by D-04:** the `write` path's automatic unlock is covered by the same
  capability refusal — a refused part gets `FLAG_SKIP_SDP_UNLOCK` auto-set, with a mandatory
  report line. This is an operator-approved reading of HOST-04's intent, not a leak.
- **Newly pulled in by D-09:** `_log_response`'s INFO-band severity mapping is corrected so
  Phase 118's OBS-01 report lines are actually visible at default verbosity.
- **Owned meta task (D-20):** the ROADMAP Phase 121 + `REQUIREMENTS.md` amendment for the
  operator's `dev test` redesign.
- The CORRECTION-4-item-4 cross-repo gate checklist, now **nine rows** (`119-NONREGRESSION.md` §
  CORRECTION-4 table) — mandatory in every phase from 118 on.

**Explicitly NOT in scope:**
- **Any firmware change.** No `firestarter/` edit of any kind, including `messages.toml` and the
  generated catalog artifacts. The `MSG_INFO_SDP_UNLOCK_DONE_US` caveat gap (F-120-03) is
  therefore answered host-side, not by editing the catalog.
- Any `chip_database.json` change, any `support_status` change, any `PROTOCOL-LEDGER` entry, any
  `build_db.py` change.
- The `dev test` redesign itself (no flags, interactive destructive ask, UV-only destructive
  scope, always-ask issue filing with `gh` dedup) — **routed to Phase 121**; only the ROADMAP /
  REQUIREMENTS amendment lands here (D-20).
- `OP_ERASE` marked `NA` for `0x0D` in the `dev test` sweep — DEVTEST-01's host half, Phase 121.
- GATE-01's AST capability gate over `sdp_capability.py` — Phase 121. This phase must leave that
  module in a shape the gate can assert against (D-03).
- Docs corrections (`doc/PROTOCOLS.md` §1.6, `doc/lockable-proms.md`, `doc/protocol-id.md`, both
  READMEs) — GATE-02, Phase 121.
- The wider CLI flag re-design (`-f` splitting, `-b` polarity reconciliation, a project-wide `-y`)
  and the `0x0D` no-erase flag-surface honesty problem — see `<deferred>`.
- `_probe_port`'s version-capture regex widening — see `<deferred>`; D-16 deliberately introduces
  no version floor.
- The `${sysenv.*}` DEV_TOOLS gating / release-channel split — stays with 999.15 / gh#8.

**Validation ceiling applies, unchanged.** No AT28C part is on the bench. `0x0D` stays
`UNVERIFIED`, **zero** chips change `support_status`, the **84**-chip count is unchanged. This
phase adds no bench work at all. Note the ceiling explicitly lists *"that the curated capability
partition is correct per family"* among the things **not** provable this milestone — D-01's
fail-closed direction is the response to that, not a claim against it. See
`.planning/REQUIREMENTS.md` §"Validation Ceiling" for the exact permitted and forbidden claims.

</domain>

<decisions>
## Implementation Decisions

### The capability partition — HOST-04

- **D-01: The partition is a fail-closed ALLOW-list, not a deny-list.**
  Only parts on an explicit SDP-capable list may receive `CMD_SDP_UNLOCK` / `CMD_SDP_LOCK`;
  everything else in the `0x0D` bucket is refused, **including anything unrecognised**. Driven by
  F-120-01: on a part with no SDP command decoder the sequence is not inert, it writes data. The
  two Out-of-Scope entries *"a `--force` path that widens which chips a lock can reach"* and
  *"for lock, prefer refuse-over-warn"* both point the same way, and the validation ceiling already
  concedes the partition cannot be proven correct per family — so the default must be refusal.
  Rejected: HOST-04's literal 5-part deny-list (`FM28V020`, `MB85R256H`, `2804`, `2816`, `2817`) —
  it leaves XICOR `X2804A` / `X2816A` / `X2816B,X2816C` and EXEL `XL2804A` / `XL2816A`, the same
  pre-SDP generation, permitted, and every future DB addition permitted by default. Rejected: a
  widened pre-SDP deny-list — same default-permit hole, and it needs a judgement HOST-04 does not
  authorise. Rejected: a DB-derived structural rule — wrong in both directions (over-refuses the
  19 `DIP24_2816` parts, several of which do have SDP; blind to the two 32 KB FRAM parts).

- **D-02: The allow-set is keyed on DB `part_number` tokens and its completeness is machine-checked.**
  Production code holds the allow-set, so the refusal is a **runtime** property — a `0x0D` chip a
  user adds to `~/.firestarter/database.json` (merged live at `database.py:192-194`, invisible to
  CI) is refused rather than silently permitted. A pytest then asserts
  `allow-set ∪ refuse-set == exactly the 84 `algorithm == 13` entries` in the shipped DB, so a
  regeneration that adds or renames a `0x0D` part goes RED instead of quietly widening reach.
  Follow `tests/test_sdp_db_invariant.py`'s shape verbatim — including its deliberate absence of a
  skip marker and its explicit non-vacuity case proving the invariant can fail. Note the keying
  cost: `part_number` values are alias-joined (`"AT28C64,AT28C64B(Non-Standard),AT28HC64,AT28HC64L"`),
  so token splitting is part of the work. Rejected: a refuse-set plus the same CI gate — cheaper,
  but its fail-closed property exists only at CI time, and the local-override path is exactly where
  a wrong answer reaches real silicon.

- **D-03: The predicate lives in a new `firestarter/sdp_capability.py` as a pure function.**
  Signature shape `-> (allowed: bool, reason: str)`, no serial, no Click, no DB-loader coupling;
  answers both *"is this even `0x0D`"* and *"does this `0x0D` part have SDP"* in one call. Gives
  Phase 121's GATE-01 a single stable file and symbol to assert against and an obvious place to
  plant a violation fixture, and lets both the `dev sdp` handler and the `write` path import it.
  Rejected: beside `_SRAM_PROTO_IDS` in `eprom_operations.py` — genuine in-tree precedent
  (`check_eprom_blank`'s short-circuit at `:1661-1676` is the same shape) but it buries a curated
  ~79-token table in a 1733-line module and couples the predicate to `EpromOperator`. Rejected: in
  `cli_handlers.py` — couples a safety predicate to Click and makes the `write`-path reuse awkward.

- **D-04: HOST-04's refusal also covers the `write` path's automatic unlock, and the auto-set is reported.**
  For a part the allow-set refuses, the host sets `FLAG_SKIP_SDP_UNLOCK` on `write` itself and
  prints one line stating that it did and why. Reads HOST-04's *"keeps SDP commands away from
  non-SDP parts"* at its intent — the auto-unlock **is** an SDP command reaching those parts
  (firmware keys it on protocol, not part). The report line is **mandatory**, per 118 D-01's
  make-it-visible discipline: the host is changing wire behaviour the user did not ask for.
  Own the consequence: `write` behaviour for the refused subset diverges from `3.0.0b11`, and that
  divergence must be stated in the SUMMARY as a deliberate host-side change, never as a no-op.
  Rejected: scoping HOST-04 to `dev sdp` only and recording the write exposure as a finding.
  Rejected: refusing `write` outright on those parts — they are legitimately writable, so that
  trades a working operation for a two-byte residue.

### `dev sdp` gating semantics — HOST-01

- **D-05: No mode flag — the subcommand is the mode, and the gate is an interactive confirm.**
  Operator direction, given in freeform while redesigning `dev test`: no flags, always ask.
  `dev test`'s `--destructive` exists because that command has a genuine non-destructive mode and
  the flag *selects* between two; `dev sdp enable|disable` has no such mode, so the flag would be
  mandatory on every invocation and therefore carry no information. The reusable half of the v1.21
  pattern is the confirm gate at `cli_handlers.py:1833-1839`, not the mode flag. Rejected:
  mirroring `--destructive` for consistency — SDP-F4 (write-probe state inference) is explicitly
  deferred, so no second mode is coming. Rejected: a typed chip-name confirmation — stronger than
  the risk warrants, since `enable` is reversible via `disable`, and it invents a second confirm
  idiom in a CLI that has exactly one.

- **D-06: `-y` is kept, and off-TTY refuses without it.**
  TTY: always ask. Off-TTY: refuse with a message naming `-y`. With no mode flag there is nothing
  that could stand in as consent, so a bare `dev sdp at28c256 enable` in a pipe or CI must not
  mutate a part whose state cannot be read back. Satisfies HOST-01's `-y` verbatim and leaves `-y`
  as the single explicit scripting escape hatch. Rejected: proceeding off-TTY the way `dev test`'s
  D-02 does — there, `--destructive` is the consent; here the stand-in would be the mere absence of
  a TTY, which is strictly weaker than the gate it copies.

- **D-07: `enable` and `disable` share one gate with different confirm text.**
  Both mutate chip state through the same unobservable mechanism, so both get the confirm, the `-y`
  bypass, the off-TTY refusal and the capability refusal. One code path, two strings: `enable`
  warns that the part will refuse writes until explicitly unlocked and that the result cannot be
  read back; `disable` warns that write protection is being removed. Rejected: gating `enable` only
  — makes `disable` the one state-mutating command in the CLI with no confirm. Rejected: requiring
  a flag for `enable` even on a TTY — reintroduces the always-mandatory flag D-05 removed.

- **D-08: Gate order is absent → capability → support-status → confirm → serial.**
  SAFE-04's `get_eprom`-emptiness hard-fail first (keyed strictly off DB emptiness, never a
  `resolve_chip` refusal — the `cli_handlers.py:1841-1847` pattern), then one `sdp_capability()`
  call, then `resolve_chip`'s support-status refusal, then the confirm, then the port opens.
  Capability outranks support-status deliberately: an `adapter-required` `0x0D` part with no SDP
  hears *"this part has no SDP"* rather than *"get an adapter"*, and no adapter would have helped.
  The confirm sits last so a user is never asked to consent to something that is then refused.
  Rejected: `resolve_chip` first for CLI-wide error-precedence uniformity — the adapter message
  would mask the capability answer for the 9 `adapter-required` `0x0D` parts. Rejected: skipping
  `resolve_chip` the way `dev test` does — makes `dev sdp` a second bespoke resolution path.

### What the outcome says — HOST-05

- **D-09: INFO-band frames are promoted from DEBUG to INFO in `_log_response`.**
  `_log_response` special-cases only `ERROR` and `WARN`; the entire INFO band falls through to
  `logging.DEBUG` (`serial_comm.py:234-238`), and `_setup_logging` sets root to `INFO` unless `-v`
  (`cli_handlers.py:83`) — so Phase 118's OBS-01 lines were satisfied in firmware and discarded by
  the host (F-120-02). Blast radius is **verified small**: every other INFO id is emitted through
  the `FLAG_VERBOSE`-gated `LOG_INFO_ID*` family (`logging_id.h:44-46`), which firmware only sends
  when the host passed `-v`, so default-verbosity output changes for exactly the five unconditional
  ids `0x5E`, `0x5F`, `0x60`, `0x61`, `0x62` — plus the F-120-07 edge case. Rejected: leaving the
  mapping alone and relying only on a host line — leaves OBS-01 permanently invisible.

- **D-10: A host summary line carries the verdict and the unreadable-state caveat, never the duration.**
  `dev sdp` prints one INFO-level line of its own, stating which sequence was emitted and that the
  resulting protection state cannot be read back — symmetric across `enable` and `disable`, which
  matters because F-120-03 leaves the unlock direction with no firmware-supplied caveat. The
  measured microseconds stay **exclusively** on the firmware's `0x5F`/`0x61` line, which D-09 now
  surfaces: no figure is printed twice, no second copy of a `micros()`-derived number can drift,
  and the host never parses a duration out of a decoded frame. Rejected: a consolidated host line
  carrying the duration too. Rejected: deliberate double-printing for redundancy — on the lock path
  the same figure would appear in consecutive lines and read as a bug.

- **D-11: Exit code is plain `0/1`; WARNs stay in the text.**
  `sys.exit(0 if ok else 1)` off the state machine's result, matching every other command. A
  `MSG_WARN_SDP_TBLC_EXCEEDED` (`0x87`) prints at WARNING level and does **not** change the code.
  This is 119 D-12's own reasoning applied at the host end: put the nuance in the message, never in
  a status a caller could misread as a state claim — and since the protection state is unreadable
  either way, no exit code can honestly encode more than "the sequence was emitted". Rejected:
  `dev test`'s `0/1/2` tri-state — it would edge toward encoding a confidence level about silicon
  state, which the validation ceiling forbids.

### Constants parity — HOST-03

- **D-12: The parity test parses `firestarter.h` and asserts two-way correspondence.**
  Extract every `#define CMD_*` and `#define FLAG_*` and assert a real bidirectional mapping
  against `constants.py` — same value both ways, nothing missing on either side — shipped with a
  planted-violation fixture proving the gate fails (the anti-hollow discipline of v1.21 SAFE-03,
  118 D-06 and 119 D-04). Today's test asserts hardcoded literals with the firmware define named in
  a trailing comment and never reads the header, which is why `CMD_SDP_UNLOCK 9` / `CMD_SDP_LOCK 10`
  landed unnoticed. Two costs to own as task work: an exemption list is required (`CMD_IDLE 0` has
  no host constant; `CMD_DEV_ADDRESS` / `CMD_DEV_REGISTER` live inside `#ifdef DEV_TOOLS`), and this
  adds one more firmware-source-scanning gate to a set that broke 4× in Phase 117 and cost 4 pytest
  repairs in Phase 118 — so it joins the CORRECTION-4-item-4 checklist. Rejected: adding the three
  literals in the existing style — satisfies HOST-03's text and reproduces the same hollowness.
  Rejected: literals plus a standalone `COMMAND_NAMES` test — see D-13.

- **D-13: `COMMAND_NAMES` coverage rides in the same test, and the `FW_ABSENT` skipif is retained.**
  The gate asserts every parsed `CMD_*` has both a `constants.py` constant **and** a
  `COMMAND_NAMES` entry, closing the value-drift path and the crash path in one place —
  `_setup_operation` does `COMMAND_NAMES[cmd]` at `eprom_operations.py:301`, so a missing entry is
  a `KeyError`, not a cosmetic gap. `FW_ABSENT` is kept so host-only CI stays green, matching
  `test_sdp_bus_config_drift.py`. **Residual gap, recorded as known-and-explained:** in host-only
  CI the whole gate skips, so a host-only PR would not catch a missing `COMMAND_NAMES` entry.
  Rejected: splitting `COMMAND_NAMES` into its own always-on test (it needs no firmware and could
  therefore never skip) — considered and declined in favour of one gate.

### HOST-06's proof

- **D-14: `dev sdp` maps `MSG_ERR_UNKNOWN_CMD` to a firmware-too-old refusal.**
  An unknown **command** is detectable after the fact: `cmd 9` against `3.0.0b11` returns
  `MSG_ERR_UNKNOWN_CMD`, so the host maps that id to a clear *"firmware too old — run
  `firestarter fw --install`"* message instead of surfacing a bare protocol error. Zero firmware
  change, no version parsing, and it exploits the one asymmetry that actually exists between the
  two halves of the wire surface.

- **D-15: `--skip-sdp-unlock` requires the `0x86` ack and fails loudly when it is absent.**
  An unknown **flag bit** is undetectable by construction — `0x100` against b11 is silently ignored
  and the declined unlock runs anyway, which is precisely the harm HOST-06 names. But when the flag
  *is* honoured, firmware emits `MSG_WARN_SDP_UNLOCK_SKIPPED` (`0x86`, Phase 118). So when the flag
  was set and `0x86` never arrives, the host reports plainly that the opt-out was **not** honoured
  and the unlock ran, and fails the operation. Honest limitation to state in-source: this detects
  after the fact rather than preventing — on old firmware the unlock has already been emitted by the
  time the user is told. It nonetheless converts a silent failure into a loud one, using machinery
  that already ships. Rejected: a minimum-firmware version gate — blocked by F-120-04, and the
  regex fix it needs touches the ring-fenced transport version-capture path.

- **D-16: No version floor is introduced, and the landing-order fact is recorded with commit provenance.**
  D-14 and D-15 discharge HOST-06's substance at runtime; the sequencing invariant itself is
  recorded as a fact (firmware landed first, Phase 119 final commit `0048b3d`) in the SUMMARY and
  `VERIFICATION.md`. Rejected: requiring a numeric minor bump to `3.1.0` so the existing
  `[\d.x]+` capture would suffice — it would make HOST-06's correctness depend on a
  release-versioning decision that belongs to Phase 122's CLOSE-03, and constrain that decision
  from inside Phase 120.

### `--skip-sdp-unlock` scope — HOST-02

- **D-17: The flag is exposed on `write` only.**
  Settled by the code, not preference: firmware auto-unlocks in `eeprom28c_write_init` and nowhere
  else, so `write` is the only command with an unlock to decline. `read` / `verify` / `blank` have
  nothing to skip.

- **D-18: On a non-`0x0D` chip the host warns and proceeds.**
  One line saying the flag has no effect on this chip's protocol, then the write runs normally. The
  user learns their request was vacuous — the HOST-05 honesty point pointed at a flag rather than a
  state boolean — without losing a working operation, and a blanket-flag script still works across
  a mixed batch. Firmware never reads the bit on other protocols, so nothing unsafe happens either
  way. Rejected: refusing before the wire — it fails a write that would have succeeded, to prevent
  a no-op with no silicon risk. Rejected: silent pass-through — leaves the user believing they
  declined something.

- **D-19: The bit is mapped by a new keyword-only `build_flags()` parameter.**
  `build_flags` is genuinely in the production path (`_build_op_flags` calls it at
  `cli_handlers.py:275`), so adding `skip_sdp_unlock` there keeps every wire-flag bit mapped in one
  function, as `FLAG_SKIP_ERASE` and `FLAG_SKIP_BLANK_CHECK` already are. It must be **keyword-only
  with a `False` default** because `build_flags`' signature is pinned by
  `tests/test_bug_characterization.py`'s BUG-1 contract — re-check that test after the change.
  Rejected: OR-ing the bit in `_build_op_flags` after the call, as the OE/CE flags do — in-file
  precedent exists, but it splits wire-flag bit-mapping across two functions.

### Cross-phase amendment owned here

- **D-20: The Phase 121 scope amendment for the operator's `dev test` redesign is an owned task in this phase.**
  Operator decision, 2026-07-29: fold the redesign into Phase 121 rather than inserting a new phase
  or deferring to a v1.23 seed. Following 119-09's precedent exactly, the amendment is an explicit
  **task in Phase 120**, not a note: `ROADMAP.md`'s Phase 121 entry and Phase Details, plus new
  `REQUIREMENTS.md` requirement ids and traceability rows, plus a `PROJECT.md` correction block.
  The redesign, verbatim: `dev test` takes **no flags**; "destructive" applies only to UV-erasable
  EPROMs; the sweep **stops and asks** whether to do a destructive write, where yes means the full
  device may be written and no means only a small part of it is written; **every** run asks whether
  to file an issue, checking first whether the user has already reported an identical one and
  creating a new issue only when it differs; and the `gh` path is used wherever it can replace the
  URL/browser path. Do **not** implement any of it in Phase 120 — only the amendment.
  Three collisions the amendment must record, because the researcher and planner will hit them:
  (a) it **reverses three locked decisions** — Phase 112 Plan 04 deliberately removed every
  interactive prompt from `dev test` (operator-approved, `112-UAT.md`), SAFE-01 locks
  `--destructive` as CLI-only and never inferred, and SAFE-03 states the confirm is the only
  interactive input left; record it *as* a reversal, the way 119 D-18 recorded reversing 118's
  D-12. (b) "non-destructive means a partial write" is a **contract change, not a flag change** —
  today `derive_plan(destructive=False)` omits write/verify from `steps` and records them on the
  advisory-only `locked_destructive` list with no code path to reach them (`chip_test.py:295-396`,
  SAFE-01/D-01); a partial write is a third mode, and it ripples through the closed six-string op
  vocabulary into the issue parser, report renderer, ladder-state taxonomy, `dedup_fingerprint` and
  the `audit_coverage_matrix` golden. (c) "destructive only for UV-erasable" needs an explicit axis
  pick — `electrical.type == "UV-EPROM"` is available in the DB, but this project has been bitten
  by type-string keys before (`protocol_id` is the algorithm axis, **not** the UV-vs-EEPROM axis)
  and prefers structural guards. Also carry: `--submit`'s contract is *"explicit +
  interactive-only; never on a bare run"* (SUB-01/02), which always-ask contradicts;
  `dev test --submit` in `3.0.0b11` **misfiles into `firestarter_app`** instead of
  `henols/firestarter_prom` and must be fixed wherever this lands; and `gh issue create --label`
  aborts before creating unless the label pre-exists **and** the user has write access, which
  community testers have neither of.

### Claude's Discretion

- **Exact confirm wording, refusal reason strings, and the host summary line's phrasing.** Must
  satisfy D-10's honesty requirement in the text itself, and D-01's refusal reasons should name
  *why* a part is refused (pre-SDP generation / FRAM / not `0x0D` / unrecognised).
- **Whether `dev sdp` is a Click sub-group or a `<chip>` argument plus an `enable|disable`
  `click.Choice`** — the locked CLI surface is `firestarter dev sdp <chip> <enable|disable>`, chip
  first, so a Choice argument is the natural reading, but the group form is acceptable if the help
  output reads better.
- **The allow-set's concrete data shape** — a `frozenset` of tokens, or a mapping from token to a
  reason/provenance string. D-01 and D-02 constrain the semantics, not the container.
- **How the header parser extracts the defines** — a new regex, or reuse of
  `tools/check_is_memory_cmd_no_ifdef.py`'s brace-matched extraction, which already handles
  `firestarter.h` and already carries the fail-closed `FIRESTARTER_*_SRC` seam.
- **The exemption-list mechanics** for `CMD_IDLE` and the `#ifdef DEV_TOOLS` pair (D-12) —
  provided the exemptions are enumerated explicitly rather than pattern-skipped.
- **Severity of the D-15 missing-ack failure** (ERROR vs WARNING) and its exact wording — that it
  fails the operation is decided; how loudly is not.
- **Whether the D-04 auto-set report line is one line or two** (what was suppressed / why),
  provided it is unconditional and visible at default verbosity.
- **Plan ordering**, subject to two hard constraints: `constants.py` + `COMMAND_NAMES` (HOST-03)
  must precede any plan that emits `cmd 9`/`cmd 10`, since `_setup_operation` `KeyError`s without
  the name entry; and `sdp_capability.py` (D-03) must precede both the `dev sdp` handler and the
  `write`-path auto-set that import it.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone framing and constraints (read first)
- `.planning/REQUIREMENTS.md` — HOST-01..06 verbatim; the **Locked decisions** table (the
  `dev sdp` CLI surface and auto-unlock policy **(d)** are locked there, not re-openable); the
  **Out of Scope** table (note *"a `--force` path that widens which chips a lock can reach"*,
  *"`firestarter lock-status` + hand-curated protection table"*, and *"a generic `locked` DB
  boolean"*); §"Future Requirements" SDP-F1/F2 (deferred `--sdp-relock` and the three-field report
  shape — HOST-05 is the retained honesty floor); and §"Validation Ceiling", which explicitly lists
  the capability partition among the things **not** provable this milestone.
- `.planning/ROADMAP.md` §v1.22 → "Phase Details" → **Phase 120** — the five success criteria this
  phase is verified against. ⚠ Criterion in *Depends on* and ROADMAP:136 both say
  "flags `0x100`/`0x200`" — **there is no `0x200` flag** (F-120-05); record the correction, do not
  edit `REQUIREMENTS.md`. Also read **Phase 121** and **Phase 122** — D-20 amends Phase 121.
- `.planning/PROJECT.md` §"Current Milestone: v1.22" — **all six** ⚠ correction blocks. Load-bearing
  here: FOURTH CORRECTION item 4 (*"every phase from 118 on must include an explicit task checking
  firmware renames/deletions against `firestarter_app`'s source-scanning gates"*) and item 5's
  `flash_utils.{h,cpp}` vacuous-path warning; SIXTH CORRECTION (the DEVTEST-01 split, LOCK-04's
  mechanism correction, and the `_SRAM_PROTO_IDS` keep-disposition **for this phase**).
- `.planning/research/SUMMARY.md` — the 4-stream adjudicated synthesis; §"Critical Pitfalls" 1–2
  (the false-success trap).

### Phase 116–119 output — this phase's substrate
- `.planning/phases/119-lock-sdp-enable-command-surface-fw-half/119-CONTEXT.md` — **D-05 (LOCK-04's
  corrected mechanism), D-06/D-07 (the generic op-layer NULL-`main` refusal → `MSG_ERR_NOT_SUPPORTED`
  with `RESPONSE_CODE_ERROR`), D-12 (OK means "the sequence was emitted", said in words —
  `response_code` untouched on the SDP path), D-13 (the standalone unlock reuses 118's ids; the lock
  got new ones) and D-17 (the lock's hardware duration explicitly waits for this phase's CLI) all
  bind here.** Its `<deferred>` records the `_SRAM_PROTO_IDS` identify-here/act-there hook, now
  closed as **keep**.
- `.planning/phases/119-.../119-NONREGRESSION.md` — the **nine-row** CORRECTION-4 gate table,
  explicitly handed to Phases 120-122; §4's per-board flash/RAM figures.
- `.planning/phases/119-.../119-MEASUREMENT.md` — SDP unlock 568/412/424 µs and the page-load
  figures with provenance; §1/§4 explain why the Leonardo and Uno-class numbers measure different
  things.
- `.planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-CONTEXT.md` — **D-01
  (unconditional `LOG_ID` on INFO-band ids — the decision F-120-02 shows the host undoes), D-02
  (WARN without touching `response_code`) and D-04 (separate literal ids) bind here.**
- `.planning/phases/117-fix-remap-aware-0x0d-emitter-honest-completion-signal/117-CONTEXT.md` —
  **D-05 (the SDP path never writes `response_code`)** is why D-11's exit code cannot carry nuance.
- `.planning/notes/dev-tools-gating-channel-split.md` — 999.15 / gh#8. Relevant open disposition:
  the stable channel currently keeps only `dev read` + `dev test`, which would strip a user-facing
  SDP command from stable. Recorded, **not acted on** in this phase.

### Host — the code this phase changes
- `firestarter_app/firestarter/cli_handlers.py` — **`dev` group at `:962-969`** (its docstring
  currently reads *"Debug command for development purposes"*); `dev test` at `:1753-1935` for the
  **v1.21 gate pattern to copy**: `_is_interactive()` at `:1718-1726` (monkeypatchable precisely
  because `CliRunner` replaces `sys.stdin`), the `Confirm.ask` gate at `:1836-1842`, and **SAFE-04's
  `if not app.db.get_eprom(chip)` hard-fail at `:1844-1850`** with its comment explaining why it is
  keyed off `get_eprom` emptiness and never a `resolve_chip` refusal. Also `write` at `:463-530`,
  `_build_op_flags` at `:242-280`, `build_arg_flags` at `:165-197`, and `_setup_logging` at
  `:75-95` (root level `INFO` unless `-v` — half of F-120-02).
- `firestarter_app/firestarter/constants.py` — `COMMAND_*` at `:56-70`, **`COMMAND_NAMES` at
  `:72-86`**, `FLAG_*` at `:90-99`. Note `CTRL_VPP_VPE_DROP_ENABLE = 0x100` at `:117` is a
  *control-register* bit in a different namespace — no conflict with `FLAG_SKIP_SDP_UNLOCK 0x100`,
  but do not let a reader confuse them.
- `firestarter_app/firestarter/eprom_operations.py` — **`build_flags` at `:168-183`** (D-19's
  target); `_setup_operation` at `:287-345`, whose **`COMMAND_NAMES[cmd]` at `:301`** is why
  HOST-03's name entries are load-bearing; `_operation_context` at `:347-383`;
  `_run_state_machine` at `:392+`; **`erase_eprom` at `:1628-1651` — the exact payload-free
  precedent** (`_operation_context(...)` plus a bare `_run_state_machine(op_name)`, no main-phase
  handler); `_SRAM_PROTO_IDS` at `:1656` and `check_eprom_blank`'s pre-wire short-circuit at
  `:1658-1676` — the in-tree shape D-03 declined to follow but should still be read.
- `firestarter_app/firestarter/serial_comm.py` — **`_log_response`'s severity mapping at
  `:232-247`** (D-09's target; only `ERROR` and `WARN` are special-cased);
  `NON_RESPONSE_PREFIXES` at `:89`; `_is_version_sufficient` at `:536-554`;
  `_validate_firmware_version` at `:556-591`; **`_probe_port`'s `re.search(r"FW:\s*([\d.x]+)", …)`
  at `:643`** — F-120-04's cause. The `_read_and_parse_lines` body is GATE-1.8d ring-fenced; do not
  touch it.
- `firestarter_app/firestarter/database.py` — **`:187-199` merges `~/.firestarter/database.json`
  live** (D-02's decisive fact) and `skip_local_override` is the test seam; **`:570-595` sets
  `FLAG_CAN_ERASE` from `electrical.type` for every `EEPROM`/`Flash/EEPROM` part with
  `algorithm != 5`** — including all 84 `0x0D` chips, where the flag is firmware-inert (see the
  `<deferred>` honesty item); `convert_to_programmer` at `:535+` produces the `algorithm` /
  `protocol-id` / `electrical-type` keys the predicate needs.
- `firestarter_app/firestarter/chip_resolver.py` — `resolve_chip` at `:16+`; it raises
  `ChipNotFoundError` for an absent chip and `ChipNotImplementedError` when
  `support_status != "supported"`. **9 of the 84 `0x0D` parts are `adapter-required`** and are
  refused there today — D-08 places this gate third, after capability.
- `firestarter_app/firestarter/codec.py` — `decode_id_frame`; **`:206-209` logs
  `"Unknown message ID 0x.. — catalog out of date?"` and drops the frame**, so new firmware ids
  degrade gracefully against a released host. `SEVERITY_LABEL` comes from the generated
  `messages.py`, so the host's severity view is the **catalog's**, not the frame's (F-120-07).
- `firestarter_app/firestarter/messages.py` — the generated host mirror; already carries `0x60`,
  `0x61`, `0x62`, `0x86`, `0x87` from Phase 119. **Never hand-normalise** its raw codegen output
  (`.planning` memory `reference_codegen_ruff_clean_emitter.md`).

### Firmware — read-only reference; this phase edits nothing here
- `firestarter/include/firestarter.h` — **`CMD_SDP_UNLOCK 9` / `CMD_SDP_LOCK 10` at `:61-62`, both
  unconditional (never `DEV_TOOLS`-gated), with an in-source comment naming Phase 120 HOST-01/03 as
  the host half**; `is_memory_cmd()` at `:109-137`; `FLAG_*` at `:131-148` ending at
  **`FLAG_SKIP_SDP_UNLOCK 0x100` — the only new flag (F-120-05)**; `ctrl_flags` as `uint32_t`.
- `firestarter/include/version.h:11` — **`#define VERSION "3.0.0b11"`**, not yet bumped.
- `firestarter/include/logging_id.h:28` (`LOG_ID`, unconditional) vs **`:42-92` the
  `FLAG_VERBOSE`-gated `LOG_INFO_ID*` family** — the fact that bounds D-09's blast radius.
- `firestarter/src/proms/eeprom_28c.cpp` — `eeprom28c_write_init`'s unconditional auto-unlock and
  its `FLAG_SKIP_SDP_UNLOCK` opt-out; `eeprom28c_write_execute`'s page-load loop and its
  `MSG_INFO_PAGE_LOAD_WORST_US` report. Protocol-keyed, not part-keyed — D-04's cause.
- `firestarter/src/operation_utils.cpp` — `op_execute_stateful_operation`'s NULL-`main` refusal
  (119 D-06/D-07), the source of `MSG_ERR_NOT_SUPPORTED` on a structurally-excluded command.
- `firestarter/src/firestarter.cpp` — `loop()`'s command `switch` and its
  `default: MSG_ERR_UNKNOWN_CMD`, which D-14 keys off.
- `tools/catalog/messages.toml` — canonical catalog (**edit ONLY this one, and not in this phase**).
  Relevant ids: `0x5E` `MSG_INFO_SDP_UNLOCK`, **`0x5F` `MSG_INFO_SDP_UNLOCK_DONE_US` — "SDP unlock
  emitted in %lu us", no caveat (F-120-03)**, `0x60` `MSG_INFO_SDP_LOCK`, **`0x61`
  `MSG_INFO_SDP_LOCK_DONE_US` — "…; protection state is not readable"**, `0x62`
  `MSG_INFO_PAGE_LOAD_WORST_US`, **`0x86` `MSG_WARN_SDP_UNLOCK_SKIPPED` — D-15's ack**, `0x87`
  `MSG_WARN_SDP_TBLC_EXCEEDED`, and `MSG_ERR_NOT_SUPPORTED` / `MSG_ERR_UNKNOWN_CMD`.

### Host test surfaces
- `firestarter_app/tests/test_revision_constants_parity.py` — **D-12/D-13's target.** `FW_ABSENT`
  at `:50-58`; `test_command_values_match_firmware` at `:77-119`;
  `test_flag_values_match_firmware` at `:122-145`. All hardcoded literals; the header is never read.
- `firestarter_app/tests/test_sdp_db_invariant.py` — **D-02's template.** Reads the shipped DB
  directly, pins the 84-count (also CLOSE-01's fact), and carries an explicit non-vacuity case. Its
  module docstring explains why it deliberately carries **no** skip marker.
- `firestarter_app/tests/test_bug_characterization.py` — pins `build_flags`/`build_arg_flags`'
  BUG-1 contract; **re-check after D-19.**
- `firestarter_app/tests/test_cli_handlers.py`, `tests/test_dev_test_cmd.py` — the `CliRunner`
  patterns for a gated `dev` subcommand, including how `_is_interactive` is monkeypatched.
- `firestarter_app/tests/test_eprom_operations.py`, `tests/test_serial_comm.py` — the seams for
  D-09's mapping change and D-15's ack observation.
- `firestarter_app/tools/check_is_memory_cmd_no_ifdef.py` + `tests/test_check_is_memory_cmd_no_ifdef.py`
  — Phase 119's new gate: brace-matched extraction from `firestarter.h` with a fail-closed
  `FIRESTARTER_*_SRC` seam and a planted-violation fixture. **The reusable extraction for D-12.**
- `firestarter_app/tools/check_no_log_in_sdp_window.py`, `tests/test_sdp_table_parity.py`,
  `tools/gen_sdp_bus_config.py` + `tests/test_sdp_bus_config_drift.py`, `tools/check_dispatch.py`,
  `tools/build_db.py`, `tools/check_devtest_orchestrator.py` — the rest of the nine-row CORRECTION-4
  checklist. This phase edits no firmware, so none should break — **confirm rather than assume.**
- `firestarter_app/tests/test_audit_coverage_matrix.py` — **pre-existing RED**, not this phase's
  regression (`.planning` memory `reference_audit_coverage_matrix_golden_stale.md`).
- `firestarter_app/tests/test_no_programmer_found_*` — go RED with a live board attached; env
  artifact (`.planning` memory
  `reference_characterization_no_programmer_tests_fail_with_live_board.md`).

### Project conventions
- `firestarter_app/CLAUDE.md` — the `constants.py` ↔ `firestarter.h` sync rule, and the **tooling
  gate**: `ruff check` + `ruff format --check` + `mypy` (strict on 8 modules, `cli_handlers.py` and
  `serial_comm.py` among them — both are edited here) + `pytest --cov-fail-under=70`.
- `CLAUDE.md` (meta) — the constants/flag-bit duplication rule. **This phase closes the pair that
  firmware-before-host deliberately left open.**
- Ruff/format must be validated against the **py3.9/3.11 CI targets**, not the devcontainer's 3.12
  (`.planning` memory `reference_devcontainer_py312_masks_ci_py39.md`).

### Todos consulted
- `.planning/todos/decode-infoic-flags-bits-14-15-protect-metadata.md` — reviewed, **not folded**;
  see `<deferred>`.
- `.planning/todos/fold-response-code-into-log-macro.md` — reviewed, **not folded**; see
  `<deferred>`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Verified facts established during this discussion (do NOT re-derive)
- **`CMD_SDP_UNLOCK 9` / `CMD_SDP_LOCK 10` are unconditional in firmware** and their in-source
  comment already names Phase 120 HOST-01/HOST-03 as the host half (`firestarter.h:61-62`).
- **`FLAG_SKIP_SDP_UNLOCK 0x100` is the only new flag.** Firmware's flag block ends there
  (`firestarter.h:148`); 118 added one flag and 119 added none. The ROADMAP's "`0x100`/`0x200`"
  is wrong (F-120-05).
- **`COMMAND_NAMES` is load-bearing, not cosmetic** — `_setup_operation` does `COMMAND_NAMES[cmd]`
  at `eprom_operations.py:301`, so a missing entry is a `KeyError` at operation setup.
- **The 84 `0x0D` chips split 66 `EEPROM` / 18 `Flash/EEPROM`**, across pinouts `DIP28_28C64` (35),
  `DIP24_2816` (19), `DIP32_28C512_EEPROM` (18), `DIP28_28C256` (12). **9 are
  `adapter-required`**; the rest are `supported`.
- **Both FRAM parts carry `electrical.type == "EEPROM"` in the DB.** They are `FM28V020` (CYPRESS)
  and `MB85R256H` (FUJITSU), both 32 KB on `DIP28_28C256` — structurally indistinguishable from an
  `AT28C256`. Nothing in the DB says "FRAM", so the existing `etype in ("SRAM","FRAM")` idiom is
  blind to them and no structural rule can find them. This is why HOST-04 says "resolved in code".
- **HOST-04's named pre-SDP trio is three MICROCHIP entries** (`2804`, `2816`, `2817`), but XICOR
  `X2804A,X2804AI` / `X2816A` / `X2816B,X2816C` and EXEL `XL2804A` / `XL2816A,XLE28C16A,XLS28C16A`
  are the same generation and are **not** named — the gap D-01's allow-list direction closes.
- **`~/.firestarter/database.json` merges into the live DB at runtime** (`database.py:187-199`), and
  CI never sees it. This is the fact that forced D-02's runtime allow-set over a CI-only gate.
- **All 84 `0x0D` chips get `FLAG_CAN_ERASE` from the DB** (`database.py:584-594`, `electrical.type`
  ∈ {`EEPROM`, `Flash/EEPROM`} and `algorithm != 5`), yet `configure_eeprom28c` never reads it —
  documented as firmware-inert in that comment block. See the `<deferred>` honesty item.
- **INFO-band frames log at `logging.DEBUG`.** `_log_response` special-cases only `ERROR` and
  `WARN` (`serial_comm.py:234-238`); `_setup_logging` sets root to `INFO` unless `-v`
  (`cli_handlers.py:83`). So every Phase 118/119 SDP report line is invisible without `-v`
  (F-120-02).
- **Every other INFO id is `FLAG_VERBOSE`-gated in firmware** via the `LOG_INFO_ID*` family
  (`logging_id.h:44-46`), so firmware only sends them when the host passed `-v`. The INFO band has
  **22** entries; only five (`0x5E`, `0x5F`, `0x60`, `0x61`, `0x62`) are emitted unconditionally.
  That bounds D-09's blast radius.
- **`_probe_port` captures the firmware version with `re.search(r"FW:\s*([\d.x]+)", …)`**
  (`serial_comm.py:643`), so `"3.0.0b11"` arrives at the comparator as `"3.0.0"`, and
  `_is_version_sufficient` int-splits on `.`. **The host structurally cannot distinguish b11 from
  b12** (F-120-04). Firmware is still at `VERSION "3.0.0b11"` (`version.h:11`).
- **`erase_eprom` is the payload-free command precedent** (`eprom_operations.py:1628-1651`):
  `_operation_context(...)` plus a bare `_run_state_machine(op_name)` with no main-phase handler.
  `CMD_SDP_*` need exactly this shape — no data frames, no `DONE` round-trip.
- **`build_flags` is in the production path**, called by `_build_op_flags` at
  `cli_handlers.py:275` — it is not merely the argparse-era shim.

### Reusable Assets
- **`dev test`'s gate trio** (`cli_handlers.py:1716-1847`) — `_is_interactive()`, the `Confirm.ask`
  gate, and SAFE-04's `get_eprom`-emptiness hard-fail, in that order. Copy the shape, drop the
  mode flag (D-05).
- **`erase_eprom`** — the payload-free operation wrapper both SDP commands need.
- **`check_eprom_blank`'s pre-wire short-circuit** (`eprom_operations.py:1658-1676`) — a working
  in-tree example of "refuse with a spoken reason before any firmware command", including the
  wording register to match.
- **`tests/test_sdp_db_invariant.py`** — D-02's exhaustiveness gate template, including the
  non-vacuity case and the deliberate absence of a skip marker.
- **`tools/check_is_memory_cmd_no_ifdef.py`** — brace-matched extraction from `firestarter.h` with
  a fail-closed `FIRESTARTER_*_SRC` seam and a planted-violation fixture; the closest analog for
  D-12's parser.
- **`MSG_WARN_SDP_UNLOCK_SKIPPED` (`0x86`)** — shipped in Phase 118 for a different purpose; D-15
  repurposes it as the host's honoured/ignored ack with zero firmware change.
- **`packaging.version.Version`** — already a dependency, already used in
  `_maybe_auto_route_to_pre` (`cli_handlers.py:225-236`); relevant only if the deferred
  probe-regex widening is ever taken.

### Established Patterns
- **Every gate ships a planted-violation fixture proving it actually fails.** Structural/AST scans
  over substring greps (v1.21 SAFE-03, 118 D-06, 119 D-04).
- **Refuse before the wire, with a spoken reason** — never a silent no-op, never a fabricated
  success.
- **Put honesty in the message text, not in a status code** (117 D-05, 118 D-02, 119 D-12) — D-10
  and D-11 are the host-side application of the same rule.
- **`-b` has opposite polarity on `write` and `erase`**, preserved verbatim from argparse under a
  rationale lock. Do not "fix" it in this phase.
- **Firmware renames/deletions break host source-scanning gates** — 4× in Phase 117, 4 pytest
  repairs in Phase 118. This phase edits no firmware, so the risk runs the other way: confirm the
  nine-row checklist is untouched rather than assuming it
  (`.planning` memory `reference_firmware_renames_break_host_source_scanning_gates.md`).
- **Executors prematurely mark multi-plan requirements Complete** — 4× in Phase 116. **Name the
  allowed HOST-NN ids in every dispatch prompt** and re-check `REQUIREMENTS.md` after each plan
  (`.planning` memory `reference_executors_prematurely_mark_requirements_complete.md`).
- **Exit-code-only tests lie about an absent chip.** In `dev test`'s absent-chip work the
  load-bearing assertion was `read_hardware_revision_value.assert_not_called()`, not the exit code
  (`.planning` memory `reference_dev_test_absent_chip_false_green_trap.md`). D-08's ordering needs
  the same treatment: assert **no port was opened**, not merely that the command failed.
- **STATE.md tooling under-writes and re-clobbers fields.** Call `state.record-session` FIRST, then
  progress/metric/decision calls, then hand-verify `current_phase_name` (em-dash/parenthetical
  splitting) and `progress.percent` regardless of order. Never trust the returned `updated` array.
- **`- **D-NN: text**` must close its bold run on ONE line**, contain at most one colon before the
  closing `**`, and never open with a glyph — otherwise plan-phase's §13a decision-coverage gate
  fails closed (STATE.md's Phase 119 planning note).

### Integration Points
- `firestarter_app/firestarter/sdp_capability.py` — **new**; the allow-set and the pure predicate.
- `firestarter_app/firestarter/cli_handlers.py` — the `dev sdp` handler under the existing `dev`
  group; `write`'s new `--skip-sdp-unlock` option; `_build_op_flags`' new kwarg.
- `firestarter_app/firestarter/eprom_operations.py` — `build_flags`' new keyword-only param; two
  new payload-free operator methods for `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK`; the `write` path's D-04
  auto-set and its report line; D-15's `0x86` ack observation.
- `firestarter_app/firestarter/constants.py` — `COMMAND_SDP_UNLOCK`, `COMMAND_SDP_LOCK`, their
  `COMMAND_NAMES` entries, `FLAG_SKIP_SDP_UNLOCK`.
- `firestarter_app/firestarter/serial_comm.py` — `_log_response`'s severity mapping (D-09).
- `firestarter_app/tests/` — the rebuilt parity gate plus its planted-violation fixture, the
  allow-set exhaustiveness gate, `dev sdp` CliRunner tests (gate ordering, off-TTY refusal, no port
  opened on refusal), the D-09 mapping test, and the D-15 missing-ack test.
- `.planning/ROADMAP.md` Phase 121 + `.planning/REQUIREMENTS.md` + `.planning/PROJECT.md` — D-20's
  owned amendment.

### Setup precondition (verify at plan time, do not assume)
`firestarter_app` must be on `v1.22-at28c-software-data-protection-lifecycle` before any sub-repo
write — confirmed on that branch at discussion time. The **firmware** sub-repo is on the same
branch at `0048b3d` and must stay **byte-untouched** by this phase. The milestone-branch check has
been a real trap twice (`.planning` memory `project_v121_submodule_branch_base.md`).

</code_context>

<specifics>
## Specific Ideas

- **The sharpest finding in this discussion is that the SDP sequence is not inert on a part that
  lacks SDP.** Phase 117 made the command writes reach silicon; on a part with no command decoder
  those writes are simply stored as data at the bus-truncated magic addresses. So `dev sdp 2816
  enable` would report "sequence emitted" having corrupted three bytes, and today's `write` on a
  pre-SDP `0x0D` part already leaves `0x2AAA←0x55` / `0x5555←0x20` behind before the payload lands.
  A full-image write overwrites both; a `-a`-ranged or short write does not. This is a reasoned
  inference from the emitter's post-117 shape, **not** a bench result — it stays inside the
  validation ceiling, and it is what turns HOST-04 from tidiness into a safety requirement and
  justifies D-04 widening the refusal to the `write` path.
- **HOST-04 is the third requirement this milestone whose stated mechanism was narrower than its
  intent.** LOCK-04's `default:` arm was harmful; LOCK-06's headroom figure was superseded; HOST-04
  names five parts when the same reasoning covers a whole generation plus every future DB addition.
  The established response holds: satisfy the intent, record the correction in phase artifacts, and
  do not edit `REQUIREMENTS.md`.
- **Phase 118's OBS-01 work was invisible in practice and nobody noticed for a whole phase.** 118
  D-01 deliberately chose unconditional `LOG_ID` over the `FLAG_VERBOSE`-gated family so the report
  lines would always be *sent* — and the host's severity mapping dropped them all to DEBUG. The
  firmware half of an observability requirement was verified; the host half was never checked. Worth
  remembering as a class: a two-repo requirement can pass its own phase's verification and still be
  false end to end.
- **The two halves of the wire surface have different detectability, and that asymmetry is the whole
  answer to HOST-06.** An unknown command produces an error; an unknown flag bit produces silence.
  So the command half gets an error mapping and the flag half gets an ack requirement — and no
  version comparison is needed for either, which is fortunate, because F-120-04 shows the host
  cannot see a `b`-suffix at all.
- **Exit codes must not learn to lie.** 119 D-12 put the lock's honesty in the message text
  precisely so the status code could not be misread as a state claim. D-11 keeps that at the host:
  a `t_BLC` WARN is loud in the text and invisible in `$?`, because no exit code can honestly say
  more than "the sequence was emitted".
- **The operator's `dev test` redesign is a genuine reversal of Phase 112's Plan-04 decision, and it
  should be recorded as one.** 112 removed every interactive prompt on purpose and documented that
  in `112-UAT.md`; SAFE-01 and SAFE-03 locked the consequences. Re-introducing the asking is a
  legitimate change of mind, and 119 D-18's *"record the reversal as a reversal, with its
  constraints named, so the next phase does not read it as the new default"* is the pattern to
  follow.

</specifics>

<deferred>
## Deferred Ideas

### Raised during this discussion, routed elsewhere
- **The `dev test` redesign** — no flags; destructive scoped to UV-erasable EPROMs; an interactive
  destructive-write ask where yes means the full device and no means a small part of it; always
  asking whether to file an issue, with a `gh`-first dedup against the user's own prior identical
  report; `gh` preferred over the URL/browser path wherever possible. **Routed to Phase 121**
  (operator decision, 2026-07-29). D-20 makes the ROADMAP/REQUIREMENTS amendment an owned task in
  *this* phase; none of the implementation happens here.
- **The wider CLI flag re-design** — splitting `-f/--force`'s two unrelated meanings (VPP mismatch
  vs chip-ID mismatch) into separate flags, reconciling `-b`'s opposite polarity between `write`
  and `erase`, and establishing a project-wide `-y` idiom instead of a `dev test`-local one. Raised
  by the operator; not folded, because each one changes behaviour on commands this phase does not
  otherwise touch. Needs its own phase.
- **The `0x0D` flag-surface honesty problem.** All 84 `0x0D` chips carry `FLAG_CAN_ERASE` from the
  DB and `write --skip-erase` is accepted for them, yet `configure_eeprom28c` has no erase op at
  all — so the CLI advertises a capability the family does not have in three places, while
  `firestarter erase at28c256` now hits Phase 119's NULL-`main` refusal. GATE-02 is currently
  scheduled only to **document** this. Consider fixing it rather than documenting it, in Phase 121
  or its own phase.
- **`MSG_INFO_SDP_UNLOCK_DONE_US` (`0x5F`) has no honesty caveat** where `0x61` does — 119 D-13
  reused 118's unlock ids, which were written for the inside-a-write context. Fixing the text is a
  catalog change requiring both sub-repos to regenerate, which is out of scope for a host-only
  phase. D-10 covers the gap host-side. Natural home: Phase 121 or 122, alongside the other catalog
  work.
- **Widening `_probe_port`'s `[\d.x]+` version capture** so the host can see pre-release suffixes
  and order `3.0.0b11 < 3.0.0b12` (via `packaging.version.Version`, already a dependency). Would
  enable a genuine pre-emptive minimum-firmware gate, but touches the ring-fenced transport
  version-capture path guarded by `test_fwguard.py` and `test_fw_version_guard.py`. Declined here in
  favour of D-15's ack detection.
- **`dev sdp`'s release-channel disposition.** 999.15 / gh#8's channel split currently keeps only
  `dev read` + `dev test` in stable, which would strip a user-facing SDP command from stable builds
  — while firmware deliberately defines `CMD_SDP_*` unconditionally as *"real user-facing operations
  in every build"*. Recorded as an open disposition for 999.15; **not acted on** in this phase, and
  the locked `dev sdp` CLI surface is not re-opened.
- **A separate always-on `COMMAND_NAMES` completeness test** that reads only `constants.py` and can
  therefore never skip (`test_sdp_db_invariant.py`'s no-skip-marker reasoning). Considered at D-13
  and declined in favour of one gate; the residual host-only-CI gap is recorded there as
  known-and-explained.

### Carried forward from Phase 119, still not taken
- **Widening the trace recorder to a third strobe kind (data-bus direction)** — declined by 118 and
  119; nothing in HOST-01..06 requires it. Still deferred, recorded so the next owner finds it.
- **The end-to-end `infoic.xml` `page_size` decode phase** — still operator-approved, still **not
  inserted into ROADMAP.md**. Insert with `/gsd-phase`; heed `.planning` memory
  `reference_new_milestone_phases_clear_destructive.md`.
- Unity-teardown SIGABRT root cause (`test_flash_intel_vpp`); recording every side-effecting
  `rurp_*` call; all-84-chips table-driven trace coverage; `DIP24_2816`'s missing `static-high-pins`
  (**SDP-F8**); datasheet verification of SDP magic addresses (**SDP-F7** — directly relevant to
  D-01's allow-set membership, and still UNVERIFIED).
- **`prove-pio-dev-flag-fails-closed.md` items 1–3** — the `${sysenv.*}` fail-open/fail-closed
  matrix and the gating-mechanism choice. Belongs to 999.15 / gh#8; item 4 was answered in Phase 119.

### Reviewed Todos (not folded)
`todo.match-phase 120` returned **13** matches, 12 scored. Ten carry the same disposition as Phases
116–119 — generic keyword overlap (VPP-on-reads, avrdude fallback, COBS frame deadline, JP4/JP5
renderer, Rev-0 photography and MODIFICATIONS trace, dead `json_init()`, v1.28 PY32 roadmap
prior-art, `DATA_BUFFER_SIZE` spike). Two were considered on their merits:

- **`decode-infoic-flags-bits-14-15-protect-metadata.md`** (0.6) — decode `infoic.xml` flags bits
  14/15 (protect-before / protect-after) in `build_db.py`. Phase 119's `<deferred>` named "Phase 120
  or the deferred `page_size` phase" as its natural home, and it *is* real SDP-protection metadata
  that would bear directly on D-01's allow-set. **Not folded:** HOST-04 explicitly requires **zero
  DB change**, and `build_db.py` output is guarded by `diff_db.py` identity under GATE-03 and by
  CLOSE-01's unchanged-84 count. Revisit in the `page_size` phase, where a DB regeneration is
  already in scope — and note it could later replace part of D-01's curated allow-set with decoded
  metadata.
- **`fold-response-code-into-log-macro.md`** (0.2) — derive `response_code` from the log id's
  severity band. Declined at 118, at 119, and again here: it conflicts with 117 D-05 / 118 D-02 /
  119 D-12, and D-11 above deepens the conflict — the host's plain `0/1` exit code depends on the
  SDP path leaving `response_code` untouched. Needs its own phase.

</deferred>

---

*Phase: 120-HOST — CLI surface, wire emission, capability refusal*
*Context gathered: 2026-07-29*
