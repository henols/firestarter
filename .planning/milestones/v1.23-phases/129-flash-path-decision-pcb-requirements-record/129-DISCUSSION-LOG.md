# Phase 129: Flash-Path Decision & PCB Requirements Record - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-02
**Phase:** 129-Flash-Path Decision & PCB Requirements Record
**Areas discussed:** Where the record lives, VID/PID (record vs code), Bootloader budget number, PCB-02 list scope, Seed disposition

---

## Gray-area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Where the record lives | Meta vs firmware vs two-layered; decides whether sub-repos and gitlinks are touched | ✓ |
| VID/PID: record vs code | Edit `usb_cdc.c` (→ ARM CI) or record only; and which sourcing route | ✓ |
| Bootloader budget number | Name a figure as intent-with-cost, or refuse one; is the linker off-limits | ✓ |
| PCB-02 list scope | Exactly the four named items, or expanded with what the milestone surfaced | ✓ |
| PCB-05 placement | Where the socket-empty instruction lands; documentation vs installer prompt | — delegated |
| Sourcing discipline | Per-claim confidence tags vs one blanket caveat | — delegated |

**User's choice:** all four of the first set; both of the second set delegated to research/planner.

---

## Where the record lives

### Location

| Option | Description | Selected |
|--------|-------------|----------|
| Two-layered | Meta authoritative + firmware copy, lockstep (v1.7-SHIELD-REVS precedent) | ✓ |
| Firmware repo only | `platform/py32f071/PCB-REQUIREMENTS.md`, beside the linker script it cites | |
| Meta `.planning` only | Cheapest, zero sub-repo exposure — but invisible to a schematic author | |

### Document shape

| Option | Description | Selected |
|--------|-------------|----------|
| Milestone-prefixed decision doc | Matches v1.9-COBS-DECISION / v1.10-FRAMING-DECISION | ✓ |
| Numbered ADR | Formal ADR with a number; would start a new convention for one document | |
| Two documents | Split the flash-path decision from the PCB checklist | |

### Firmware layer contents

| Option | Description | Selected |
|--------|-------------|----------|
| Subset + fail-closed sync gate | Board-facing sections only; a checker asserts the shared sections match | ✓ |
| Subset, convention only | Same split, no gate — known failure mode is silent drift | |
| Full mirror | Byte-identical; a diff is the sync check, but ships planning rationale to the firmware repo | |

### App repo

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — PCB-05 lands there too | Third repo commit, second gitlink; but the installer's actual reader | |
| No — meta + firmware only | Smaller blast radius; app repo is mid-flight from Phases 127/128 | ✓ |
| Let the planner decide | Fold into the delegated PCB-05 placement question | |

### Gitlink timing

| Option | Description | Selected |
|--------|-------------|----------|
| In-phase | Matches Phase 125 (`4bb038e`) and Phase 128 | ✓ |
| Defer to Phase 130 close | One bump for the milestone; meta points at a tree without the record until close | |

**Notes:** The two-layered choice is the same shape the project already uses for
hardware-facing records. The sync gate was accepted specifically because cross-repo
source-scanning gates in this milestone have repeatedly failed OPEN.

---

## VID/PID: record vs code

### Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Record only | Placeholder stays; no ARM build, no operator-gated dispatch | ✓ |
| Edit the code too | Two-line change, but requires an ARM rebuild to stay honest | |
| Edit only if the route is free and immediate | Defers the scope question to research | |

### Sourcing route

| Option | Description | Selected |
|--------|-------------|----------|
| pid.codes — VID `0x1209` | Free open-source-hardware registry; legitimate rather than squatted | ✓ |
| Keep the squat, document the liability | Honest, but leaves PCB-04 an obligation rather than a decision | |
| USB-IF vendor ID | Unambiguous ownership; four-figure cost for a project with no board | |
| Let research pick | Comparison in the record, decision at plan or verify time | |

### Allocation

| Option | Description | Selected |
|--------|-------------|----------|
| Decide the route only | Allocation is a public PR filed by the operator; tracked as a follow-up | ✓ |
| Request it in-phase, operator-driven | Gets a real number, but blocks on a third party's turnaround | |
| Decide the route and pre-write the request | Draft the request content without filing it | |

### Interim placeholder

| Option | Description | Selected |
|--------|-------------|----------|
| Hard ship gate | No board ships, no release advertises a USB identity, until a PID exists | ✓ |
| Warning only | State the liability; leave enforcement to whoever ships | |
| Gate plus a tracked obligation | Ship gate plus a FUT-N requirement in REQUIREMENTS.md | |

**Notes:** Keeping `usb_cdc.c` untouched is what lets the whole phase stay free of an ARM
CI dispatch — the two decisions are linked, not independent.

---

## Bootloader budget number

### Budget figure

| Option | Description | Selected |
|--------|-------------|----------|
| Sector-quantised intent | Whole 8 KiB sectors, research-sized, always printed with its migration cost | ✓ |
| Ceiling, not a point value | A maximum rather than a size; honest about LOW-confidence sizing | |
| No number at all | Constraint and cost only; leaves the budget table with a hole | |

### Linker script

| Option | Description | Selected |
|--------|-------------|----------|
| Comment-only cross-reference | `LENGTH = 0` stands; add the record's filename to the existing comment | ✓ |
| Untouched | Zero edits; cross-reference lives only in the record | |
| Give BOOTLOADER a real length | Rejected — moves the application ORIGIN on a part with no VTOR | |

### Vector relocation

| Option | Description | Selected |
|--------|-------------|----------|
| State the cost, enumerate candidates | Consequence plus confidence-tagged candidate mitigations | ✓ |
| State the cost only | Enumerating unvalidatable mitigations risks one being read as a plan | |
| Defer entirely to FUT-N05 | PCB-03 explicitly requires the implication be stated here | |

### ARM CI

| Option | Description | Selected |
|--------|-------------|----------|
| No CI run — local proof only | No translation unit added; prove byte-identical output locally | ✓ |
| Yes — keep the milestone's habit | Structurally consistent, but costs a personal push and dispatch | |
| Only if the linker edit lands | Ties the decision to the actual diff at plan time | |

**Notes:** The linker script's own comment addresses Phase 129 by name and sets the standard
for how the figure may be presented. The comment-only edit closes that reference in both
directions without changing emitted output.

---

## PCB-02 list scope

### Breadth

| Option | Description | Selected |
|--------|-------------|----------|
| Four named + milestone-surfaced | Adds VPP on PA4/ADC ch4, data-bus test points, USB connector/D+ pullup | ✓ |
| Exactly the four named | Tightest scope control; goal sentence then over-promises | |
| Four named + explicit not-yet-decidable list | Adds the record's edges so silence is not read as "no constraint" | |

### Seed item 5 (reboot-into-bootloader)

| Option | Description | Selected |
|--------|-------------|----------|
| Recorded as an open question | Board cost stated both ways; FUT-N04 owns the software half | ✓ |
| Decided — strap-only for now | Makes BOOT0 reachability unconditional | |
| Out of scope — FUT-N04 owns it | Risk: a designer treats BOOT0 reachability as optional | |

### Row format

| Option | Description | Selected |
|--------|-------------|----------|
| Checkbox + rationale + failure mode | Workable straight off; CLOSE-02 can cite specific rows | ✓ |
| Checkbox + rationale | Shorter; the "why" usually implies the failure mode | |
| Table with a status column | Matches REQUIREMENTS.md and the protocol ledger | |

**Notes:** The "explicit not-yet-decidable list" idea from the rejected third option was
carried into CONTEXT.md `<specifics>` anyway — it is compatible with the chosen breadth.

---

## Seed disposition

### Seed status

| Option | Description | Selected |
|--------|-------------|----------|
| Status → partially-realised, seed stays | Frontmatter reflects reality; seed stays live for FUT-N05 | ✓ |
| Retire the seed into FUT-N05 | One carrier, but FUT-N05 is one line and the seed holds the rejected-route table | |
| Leave the seed untouched | Cost: a stale `dormant` status on a document the record cites | |

### Canonical carrier

| Option | Description | Selected |
|--------|-------------|----------|
| The new record | The only document citing Phase 126's actually-reserved addresses | ✓ |
| Seed stays canonical for the primary route | Two documents, clear division | |
| Let the planner decide | Both readings defensible | |

**Notes:** Surfaced during the wrap-up check — the seed's `trigger_condition` ("v1.28
activated OR first PCB specified") fired when v1.28 was activated as v1.23, while `status:`
still reads `dormant`.

---

## Claude's Discretion

- **PCB-05 placement and strength** — where the socket-empty instruction lands within the two
  in-scope repos; documentation only, since the app repo is out of scope.
- **Sourcing / confidence discipline** — per-claim tags vs one blanket caveat; resolve from
  existing honesty conventions, CLOSE-02 is the consumer.
- Exact filenames, section ordering, and the mechanism of the sync gate.

## Deferred Ideas

- Editing `usb_cdc.c` to the allocated VID/PID (needs an ARM build).
- Filing the pid.codes request — outward-facing operator action.
- Propagating PCB-05 into `firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md`.
- An installer-time socket-empty prompt — HOST scope.
- Giving BOOTLOADER a real length — FUT-N05.
- Software reboot-into-bootloader — FUT-N04.
- Introducing an ADR numbering scheme / `adr/` directory.
