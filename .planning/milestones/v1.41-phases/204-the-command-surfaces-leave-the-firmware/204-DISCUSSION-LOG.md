# Phase 204: The command surfaces leave the firmware - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-21
**Phase:** 204-the-command-surfaces-leave-the-firmware
**Areas discussed:** The 204/205 seam; What a retired ordinal answers; Bench method for REL-02/03; The DONE clean-stop fold-in

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| The 204/205 seam | How far the removal sweeps; which gates and goldens re-anchor here | ✓ |
| What a retired ordinal answers | Generic refusal vs a minted retired-command message | ✓ |
| Bench method for REL-02/03 | Which artifacts play the four version roles; how "no side effect" is observed | ✓ |
| The DONE clean-stop fold-in | Whether CMP-F1's cheaper route lands in this phase | ✓ |

**User's choice:** all four.

---

## The 204/205 seam

### Q1 — How far does 204's removal sweep go?

| Option | Description | Selected |
|--------|-------------|----------|
| Full sweep of ordinals 4 & 6 | All 11 firmware sites plus the host mirror; `mem_util_blank_check*` survives for 205; re-anchors the 201-05 gate and re-derives the eprom.cpp golden here; lets the `#define`s actually be retired | ✓ |
| Literal minimum | Only the three sites FWCMD-01 names plus the two wrappers; leaves 8 unreachable references and forces `#define CMD_BLANK_CHECK 4` to survive 204 | |
| Middle — dispatch arms now, internals in 205 | The five per-protocol arms but not `operation_utils.cpp`'s block or `memory.cpp`'s internal branches | |
| You decide | | |

**User's choice:** Full sweep.
**Notes:** Recorded as D-01. The rejection reasoning for the other two is preserved in CONTEXT.md:
the minimum makes FWCMD-03's "reserved" record aspirational and leaves a misleading bisect state;
the middle option re-anchors the same gate and golden, so it buys nothing over the full sweep.

### Q2 — Where does FWCMD-03's reserved-ordinal record live?

| Option | Description | Selected |
|--------|-------------|----------|
| Both sides, mirroring FWBLANK-02 | Delete from `firestarter.h` and `constants.py`; reserved comment at each ladder gap | ✓ |
| Firmware deletes, host keeps as reserved markers | Keeps Phase 202's inline comments true; departs from the ladders-move-together rule | |
| Keep named markers on both sides | Cheapest and most greppable; leaves a symbol that compiles | |
| You decide | | |

**User's choice:** Both sides.
**Notes:** Recorded as D-02, with two consequences surfaced during discussion — Phase 202's
"COMMAND_VERIFY stays in constants.py" comments go stale, and `eprom_operations.py:628` is a **live**
use of `COMMAND_VERIFY` in the `region-end` guard, not a comment.

### Q3 — FWCMD-05's `MSG_ERR_VERIFY` claim is false for two of its three named sites

| Option | Description | Selected |
|--------|-------------|----------|
| Amend to each site's own error id | Pin per-site ids; stronger than the current text, not weaker | |
| Narrow FWCMD-05 to the real 0xAF sites | Drops the proof obligation on two of three load-bearing verifies | |
| Leave the text, prove what is true | Records the discrepancy in VERIFICATION.md instead of fixing it | |
| You decide | | ✓ |

**User's choice:** You decide.
**Notes:** Claude chose to amend to per-site ids, recorded as D-03 with the measured table and the
reasoning. Follows the precedent set by Phase 203's D-02 (WRITE-02) and Phase 202's CMP-04
amendment. Requires edits to both `.planning/REQUIREMENTS.md` FWCMD-05 and `.planning/ROADMAP.md`
Phase 204 criterion 3 before planning.

### Q4 — What kind of test proves FWCMD-04 and the amended FWCMD-05?

| Option | Description | Selected |
|--------|-------------|----------|
| Split by property type | Source-contract gate for the call-site property; behavioural native tests for the emit property | ✓ |
| Behavioural only | Strongest reading of "not by inspection"; much more expensive, and hits the missing `millis` stub | |
| Source-contract gates only | Cheapest and consistent with repo precedent; proves shape, never behaviour | |
| You decide | | |

**User's choice:** Split by property type.
**Notes:** Recorded as D-04. Surfaced during discussion: `MSG_ERR_VERIFY` is asserted by **no test in
the tree today**, and the existing native tests assert `h.response_code`, never a message id — so
this is new machinery, not a copy.

### Continue check

**User's choice:** Next area. Declined an offered fifth question on the fate of the Phase 201-05
nine-site gate; it is recorded in CONTEXT.md under Claude's Discretion instead.

---

## What a retired ordinal answers

*Practice research was run for this area only (`workflow.research_before_questions` is enabled). It
returned nothing specific to retired opcodes in serial protocols; the one transferable point — make
a skew boundary explicit and easy for a human to reason about — is noted in CONTEXT.md as the
argument the chosen option trades away.*

### Q1 — What should post-204 firmware say when a pre-3.1.0 host sends ordinal 4 or 6?

| Option | Description | Selected |
|--------|-------------|----------|
| Accept the generic default arm | Existing `MSG_ERR_UNKNOWN_CMD` path; zero new code, zero new PROGMEM | ✓ |
| Mint a retired-command message | Names the version boundary; costs meta-repo codegen, a catalog id and a format string | |
| Generic arm now, message in 207 | Defers the wording decision to the phase that owns the wiki breaking-change page | |
| You decide | | |

**User's choice:** Accept the generic default arm.
**Notes:** Recorded as D-05, including the traced path — with 4 and 6 out of `is_memory_cmd` they
still satisfy `handle->cmd < CMD_READ_VPP`, so they parse but never reach `configure_memory`, then
hit the dispatch `default:` arm. The accepted cost (the operator sees "unknown", which reads like a
corrupt frame rather than a version boundary) is recorded rather than glossed.

### Q2 — What happens to the orphaned debug ids?

| Option | Description | Selected |
|--------|-------------|----------|
| Leave them in the catalog | Reserved note in `messages.toml`; keeps 204 a two-repo phase | ✓ |
| Retire them with the wrappers | Consistent with D-02's delete-don't-mark stance; makes 204 three-repo | |
| Defer to 207 | | |
| You decide | | |

**User's choice:** Leave them in the catalog.
**Notes:** Recorded as D-06. `DBG_VERIFY_PROM` (0x08) and `DBG_BLANK_CHECK_PROM` (0x0B) have no other
user in either repository.

### Continue check

**User's choice:** Next area.

---

## Bench method for REL-02/03

### Q1 — What carries the `3.1.0b1` label at 204, given REL-01 is Phase 207?

| Option | Description | Selected |
|--------|-------------|----------|
| Substitute build identity, record it | Labels mean post-204 / pre-204 builds; the phase record names the real shas | ✓ |
| Pull REL-01 forward into 204 | Makes criteria 4 and 5 literally true; contradicts the roadmap's reason for 207 | |
| Bump firmware only | Splits REL-01 across two phases | |
| You decide | | |

**User's choice:** Substitute build identity.
**Notes:** Recorded as D-07, with the supporting observation that nothing in `verify` or `blank`
gates on a version string, so the label is documentation rather than mechanism.

### Q2 — What plays the pre-3.1.0 host?

| Option | Description | Selected |
|--------|-------------|----------|
| PyPI 3.0.0b49 in its own venv | The artifact a real user actually has | ✓ |
| Git worktree at the pre-204 app commit | A reconstruction; the editable install does not follow a worktree | |
| Both, as separate legs | Strongest evidence; doubles the bench sequence | |
| You decide | | |

**User's choice:** PyPI 3.0.0b49.
**Notes:** Recorded as D-08 with two traps to design around — the 3.12-vs-3.11 interpreter split and
the app writing `~/.firestarter/config.json` regardless of `FIRESTARTER_CONFIG_DIR`.

### Q3 — How is "no hardware side effect" proven?

| Option | Description | Selected |
|--------|-------------|----------|
| Read-back equivalence on a socketed part | Checksum before, refusal, checksum after, byte-identical | ✓ |
| Empty socket, refusal observation only | No hardware present, so the property is argued from code structure | |
| Rail observation during the refusal | The vpp/vpe monitors do not route to the socket | |
| You decide | | |

**User's choice:** Read-back equivalence.
**Notes:** Recorded as D-09.

### Q4 — Which rig?

| Option | Description | Selected |
|--------|-------------|----------|
| Rev 2.2 + W27C512 | | |
| Rev 2.2 + AT28C256 | | |
| Rev 2.0 or modified Rev 0 | | ✓ |
| You decide / tell me at execution | | |

**User's choice:** Rev 2.0 or modified Rev 0 — disambiguated by follow-up to **Rev 2.0**.
**Notes:** The follow-up was asked because `hw_revision` cannot distinguish the operator's three
shields, and because the modified Rev 0's electricals have never been physically verified.

### Q5 — Which part?

| Option | Description | Selected |
|--------|-------------|----------|
| W27C512 | Erasable, so known content can be re-established without a UV eraser | ✓ |
| AT28C256 | A different protocol family from the UV path 205 stresses | |
| Whatever is already socketed | | |

**User's choice:** W27C512.

### Mid-discussion correction from the operator

The operator corrected the board identity during the write-up: **an Arduino Leonardo carrying the
Rev 2.0 shield with the W27C512 already seated, and standing permission to drive and flash it
without asking.** Verified at the port — `/dev/ttyACM0`, USB `2341:8036`, `cdc_acm`. An earlier
`/dev/ttyUSB0` reading taken during this discussion belonged to a different device since unplugged,
and the Uno-class inference drawn from it was wrong. D-10 was rewritten: Leonardo is exempt from the
chip-out-before-sideload rule, so the whole four-role matrix runs unattended; its buffer is 1024
bytes rather than 512; progress emission is Leonardo-only, which puts the bench board on the exact
behaviour D-01 site 12 deletes; and the phase proves both skew directions on a Leonardo only, with
no Uno-class coverage.

### Continue check

**User's choice:** Next area.

---

## The DONE clean-stop fold-in

### Q1 — Does the DONE-based clean stop land in Phase 204?

| Option | Description | Selected |
|--------|-------------|----------|
| Leave it filed as CMP-F1 | Not in this phase's requirement set; the host half is not one line; deferring costs nothing | ✓ |
| Fold it in here | Removes the ~1 s per-abort cost and the wire-identical-error ambiguity | |
| Firmware half now, host half in 206 | The firmware half is inert until the host sends DONE | |
| You decide | | |

**User's choice:** Leave it filed as CMP-F1.
**Notes:** Recorded as D-12. Two findings from reading the code during this area are carried into
CONTEXT.md so they are not re-derived: the host currently aborts by *withholding* acks and sends
nothing, so using `OP_MSG_DONE` means teaching it to send `"DONE"` and reworking
`_drive_region_compare`'s four-condition discrimination; and old firmware **already** parses `"DONE"`
into `OP_MSG_DONE` and ignores it, so a future host sending it degrades to exactly today's timeout
path — the change is forward-compatible by construction.

---

## Todo folding

| Todo | Decision |
|---|---|
| `2026-08-30-remove-cmd-verify-from-firmware-compare-in-app.md` (`resolves_phase: 204`) | **Folded.** The milestone's provenance todo; 204 closes it. Its `files:` list is stale and must not be used as a work list. |
| `2026-09-20-preflight-firmware-version-compat-guard.md` | Not folded — host-only, stable-channel, gated on the stable-3.0.0 seed. Read before writing the REL-03 leg. |
| `new-host-old-firmware-0x05-page-size-skew.md` | Not folded — different mechanism; its `_probe_port` caveat bears on D-07. |

`todo.match-phase 204` returned 50 of 50 pending todos, almost all on broad keyword overlap.

---

## Claude's Discretion

- The amendment wording for FWCMD-05 and ROADMAP criterion 3 (user answered "you decide" on Q3 of
  the seam area).
- The source-contract gate's module name and whether it is new or an added leg.
- The mechanism for asserting an emitted message id in a native test, and whether
  `flash_util_verify_operation`'s 150 ms timeout leg needs a `millis` stub.
- The reserved-ordinal comment wording on both ladders and the two catalog comments.
- Whether the Phase 201-05 nine-site gate is re-anchored to its four survivors or retired in 204
  (offered as a fifth question in the seam area; the user chose to move on).
- The bench sequence order and how the pre-204 firmware `.hex` is obtained.
- Whether `eprom_operations.py:628`'s guard becomes `cmd == COMMAND_WRITE` or keeps a one-member
  tuple.

## Deferred Ideas

- The `DONE`-based clean stop in `op_wait_for_ack` — best home is wherever the host's abort path is
  next opened; Phase 206 already owns the serial-session rework.
- A dedicated retired-command message naming the version boundary — best home Phase 207, which owns
  REL-04's wiki breaking-change page.
- Retiring the orphaned `DBG_VERIFY_PROM` / `DBG_BLANK_CHECK_PROM` catalog entries — best home any
  later phase already paying for a `messages.toml` codegen run.
- The firmware half of the negative-address todo — still Phase 205, carried forward from Phase 203's
  deferred list.
- Uno-class coverage of FWCMD-06's refusal — no Uno-class board is attached; a separate leg if wanted.
