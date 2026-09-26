# Phase 129: Flash-Path Decision & PCB Requirements Record - Context

**Gathered:** 2026-08-02
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers a **written decision record**, not runtime behaviour. It captures the
three-tier flash path, the PCB requirements that are free today and unrecoverable after
layout, the flash budget **as Phase 126 actually reserved it**, a real USB VID/PID decision,
and a socket-empty safety instruction — all before the first schematic exists.

**Requirements:** PCB-01 … PCB-05. **Research flag: yes** (`/gsd-plan-phase --research-phase 129`).

**Repos touched:** meta (`.planning/`) + `firestarter` (firmware). `firestarter_app` is
**out of scope this phase** (D-04).

**Not in scope:** designing the bootloader, implementing anything, writing a schematic,
requesting the PID, or making any claim about PY32F071 silicon behaviour.

</domain>

<decisions>
## Implementation Decisions

### Where the record lives

- **D-01:** **Two-layered.** The authoritative record lives in the meta repo at
  `.planning/`; a **subset** lives in the firmware repo under `platform/py32f071/`.
  Precedent: `.planning/v1.7-SHIELD-REVS.md` + its sub-repo subset. Rejected: meta-only
  (a schematic author working in the firmware repo would never find it) and firmware-only
  (loses the meta decision trail).
- **D-02:** **Milestone-prefixed decision doc**, following this repo's actual precedent —
  `.planning/v1.9-COBS-DECISION.md`, `.planning/v1.10-FRAMING-DECISION.md`,
  `.planning/v1.13-PROTOCOL-ENUMERATION.md`. **Do not introduce an ADR numbering scheme** —
  none exists in this repo and the ROADMAP's phrase "ADR-style" means the shape, not a
  numbered series. Filename is the planner's call within that convention.
- **D-03:** The **firmware layer is a subset**, not a mirror: PCB checklist, flash budget,
  VID/PID decision, socket-empty warning. The meta layer additionally carries the full
  rationale and the rejected-route table. A **fail-closed sync gate** asserts the shared
  sections match between the two copies. That gate **must ship with a planted-violation
  fixture** — this milestone has repeatedly measured that source-scanning cross-repo gates
  fail OPEN (Phase 123 BASE-08; research finding A-7; the four gate breakages in Phase 117).
- **D-04:** **`firestarter_app` is not touched.** Two repos only. PCB-05 lands in the
  firmware layer and the meta record; propagating it to
  `firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md` is left to Phase 130 or a later
  host phase.
- **D-05:** **Meta gitlinks are bumped in-phase**, matching what Phase 125 actually did
  (`4bb038e`) and Phase 128 after execution — not deferred to milestone close.

### USB VID/PID (PCB-04)

- **D-06:** **Record only — `platform/py32f071/src/usb_cdc.c` is NOT edited.** Lines 20 and
  24 keep `FIRESTARTER_USB_VID 0x36B7U` / `FIRESTARTER_USB_PID 0xFFFFU`. PCB-04's wording
  ("replaces the placeholder") is satisfied by a recorded decision plus a tracked
  obligation, not by a code change. This is what keeps the phase free of an ARM rebuild.
- **D-07:** **The decision is pid.codes — VID `0x1209`**, the established free registry for
  open-source hardware. Research must confirm the current request process, its conditions,
  and whether anything about it has changed. Rejected: keeping the squat (leaves PCB-04 as
  an obligation rather than a decision), and a USB-IF vendor ID (four-figure cost for a
  project with no board).
- **D-08:** **The phase decides the route; it does not request the PID.** Allocation is a
  public pull request against `pidcodes.github.com` filed under the operator's name —
  outward-facing, and **no agent files it**. Tracked as an operator follow-up.
- **D-09:** The record states a **hard ship gate**: `0x36B7`/`0xFFFF` is unallocated and
  squatted; **no PY32F071 board ships and no release advertises a USB identity until a real
  PID is allocated.** PCB-04's "liability" clause becomes a checkable condition, not a
  warning.

### Flash budget & bootloader region (PCB-03)

- **D-10:** The record names a **sector-quantised bootloader figure** — whole 8 KiB sectors,
  research-sized against a CDC + COBS bootloader — and **every appearance of that figure
  carries its migration cost**. The linker comment forbids a number *that looks already paid
  for*; it does not forbid a number.
- **D-11:** **The linker script gets a comment-only cross-reference.**
  `BOOTLOADER (rx) : ORIGIN = 0x08000000, LENGTH = 0` stands unchanged. The existing comment
  already says "for Phase 129 (PCB-03/FUT-N05) to cite" — add the record's actual filename so
  the reference closes in both directions. **Giving BOOTLOADER a real length is explicitly
  rejected** (it moves the application ORIGIN — Phase 126 D-13).
- **D-12:** **Vector relocation: state the cost, then enumerate candidates.** The cost is
  that with no VTOR, every previously flashed unit's vector-table address changes. The
  record lists the candidate mitigations research surfaces (SYSCFG `MEM_MODE` remap, RAM
  vector copy, linker-relocated app with a trampoline) **each tagged with its confidence** —
  none is a plan; FUT-N04 already deferred the software half as unvalidatable without silicon.
- **D-13:** **No operator-gated ARM CI run this phase.** The only firmware edits are a new
  `.md` and a linker comment; neither can change emitted output. Prove it locally instead —
  a byte-identical-artifact or comment-stripped-diff argument recorded in the non-regression
  doc. Phases 125/126/128 each needed CI because they added translation units; this one adds
  none. **The standing rule still holds: no task may run `git push` or `gh workflow run`.**

### PCB requirements list (PCB-02)

- **D-14:** **The four named items plus what this milestone surfaced.** Named by PCB-02:
  BOOT0/nBOOT1 strap reachability, exposed SWD pads, a contiguous 8-bit GPIO port for the
  data bus, a depopulated HSE footprint. Additionally in scope because they are equally
  unrecoverable after layout: VPP sense on PA4 / ADC ch4, data-bus test points, USB
  connector and D+ pullup. The phase goal is "every PCB decision free today and
  unrecoverable after layout" — broader than the four, and the record should match the goal.
- **D-15:** **Seed item 5 — reboot-into-bootloader as a protocol command vs strap-only — is
  recorded as an open question with its board cost stated on both sides**, not decided.
  Strap-only means the BOOT0 jumper must stay reachable forever; a protocol command could
  relax that. FUT-N04 owns the software half.
- **D-16:** **Each checklist row is: checkbox + one line of rationale + one line of what
  breaks if the board ships without it.** A schematic author can work straight off it, and
  Phase 130's honesty ledger (CLOSE-02) can cite specific rows.

### Seed disposition (PCB-01)

- **D-17:** `.planning/seeds/py32f071-no-external-tool-fw-install.md` has its
  `trigger_condition` **already fired** (v1.28 was activated as v1.23) while `status:` still
  reads `dormant`. Update the frontmatter to reflect reality — the DFU runner-up landed in
  v1.23, the primary self-flash route did not — and record that **the seed remains live for
  FUT-N05**. This is what PCB-01's "does not retire the seed" points at concretely.
- **D-18:** **The new record is canonical** for the flash-path decision. The seed and
  FUT-N05 both point at it. It is the only document that cites Phase 126's
  actually-reserved addresses, which is the entire reason the phase exists.

### Claude's Discretion

Two areas the operator explicitly delegated:

- **PCB-05 placement and strength.** Where the socket-empty-before-install instruction lands
  within the two in-scope repos, and whether it stays documentation or becomes an
  installer-time prompt. Note the constraint from D-04: `firestarter_app` is out of scope,
  so an installer-time prompt is **not** available this phase. Also note
  `firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md` currently says **nothing** about the
  socket (measured 2026-08-02), and `platform/py32f071/README.md` §"Hardware validation
  still required" is the nearest existing text.
- **Sourcing / confidence discipline.** Whether every claim carries a per-claim sourcing tag
  and an "unverified until silicon" marker, or one blanket caveat suffices. Resolve from the
  project's existing honesty conventions; CLOSE-02's honesty ledger is the downstream
  consumer.

Also at planner discretion: exact filenames, section ordering, and the mechanism of the
D-03 sync gate.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope & requirements
- `.planning/ROADMAP.md` §"Phase 129: Flash-Path Decision & PCB Requirements Record" — goal,
  five success criteria, research flag
- `.planning/REQUIREMENTS.md` lines 94–98 — PCB-01…PCB-05 verbatim
- `.planning/REQUIREMENTS.md` §"Future Requirements" → **FUT-N04** (software
  reboot-into-bootloader, deferred: no VTOR, `SYSCFG MEM_MODE` unreliable on sibling F0
  parts), **FUT-N05** (self-flash bootloader — the seed's primary route, its own milestone),
  **FUT-N06** (`.bin` release asset)
- `.planning/REQUIREMENTS.md` §"Out of Scope" — in particular "Hardcoding `--usb-id 0448` as
  a default" (`0x0448` is a bootloader-table device ID, **not** a confirmed USB PID) and
  "Any claim about PY32F071 silicon behaviour"

### The flash-path decision being recorded
- `.planning/seeds/py32f071-no-external-tool-fw-install.md` — the three-tier decision's
  origin, the rejected-route table (PY32DfuTool / dfu-util / vendored-pyusb / puyaisp), the
  reliability argument, and the five PCB requirements. **Status update owed — see D-17.**
- `.planning/notes/py32f071-port-branch-state.md` — branch-state evidence the seed cites
- `firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md` — the DFU path as shipped
  (§2a/§2b/§2c bootloader-entry table). **Read-only this phase (D-04).**

### The flash map that must be cited (PCB-03)
- `firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld` — **the authoritative
  addresses.** `BOOTLOADER (rx) ORIGIN 0x08000000 LENGTH 0` (named seam) ·
  `FLASH (rx) ORIGIN 0x08000000 LENGTH 120K` · `CONFIG (r) ORIGIN 0x0801E000 LENGTH 8K`
  (sector 15, 7680 B deliberate slack) · `RAM (xrw) ORIGIN 0x20000000 LENGTH 16K`. Its
  BOOTLOADER comment is a **direct instruction to this phase** — read it before writing the
  budget section.
- `firestarter/platform/py32f071/CONFIG-STORAGE.md` §"Flash geometry" — page 256 B,
  sector 8192 B, main flash `0x08000000..0x0801FFFF`, sourced to Puya PY32F07X RM V0.2
  §4.1/§4.2.1/Table 4-1
- `.planning/phases/126-flash-persistent-config-via-a-storage-backend-seam-highest-r/126-CONTEXT.md`
  — D-10/D-13/D-18: why CONFIG is a whole sector, why BOOTLOADER is zero-length, and the
  ORIGIN-migration cost in the author's own words

### VID/PID (PCB-04)
- `firestarter/platform/py32f071/src/usb_cdc.c:19-36` — the placeholder defines
  (`0x36B7U` / `0xFFFF`) and their use in the descriptor. **Not edited this phase (D-06).**
- `firestarter_app/firestarter/py32_dfu.py:441` — discovery is by **interface class
  0xFE/0x01, not VID/PID**, so the host side is unaffected by the placeholder. State this
  in the record so nobody reads PCB-04 as a host bug.

### Pin map & safety (PCB-05)
- `firestarter/platform/py32f071/README.md` §"Provisional example pin map" (PB0–PB7 data,
  PA0–PA5 control, VPP on PA4/ADC ch4) and §"Hardware validation still required" — the
  provisional map is **why** the socket-empty warning is stronger here than the comparable
  warning elsewhere
- `.planning/PROJECT.md` §"Current Milestone: v1.23" — the no-PCB ceiling and the forbidden
  claims

### Document-shape precedent
- `.planning/v1.7-SHIELD-REVS.md` — the two-layered meta + sub-repo-subset pattern (D-01)
- `.planning/v1.9-COBS-DECISION.md`, `.planning/v1.10-FRAMING-DECISION.md`,
  `.planning/v1.13-PROTOCOL-ENUMERATION.md` — the milestone-prefixed decision-doc shape (D-02)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets
- **`platform/py32f071/CONFIG-STORAGE.md`** — Phase 126 landed a design record in exactly
  the location D-01 puts the firmware layer, as a single-file commit. Same shape, same
  directory, established one phase ago.
- **The linker script's BOOTLOADER comment** already anticipates this phase by name. It is
  the closest thing to a pre-written brief; D-11 completes the round trip.
- **Cross-repo gate precedent** — Phase 128's `128-09` cross-repo binding gate for the
  py32f071 asset filename (`firestarter_app` commit `cc9452f`) is the nearest analogue for
  D-03's sync gate, including the direction of the check.

### Established patterns that constrain this phase
- **Fail-closed with a planted-violation fixture.** BASE-08 (Phase 123) required every
  checker to ship one. Research finding A-7 measured cross-repo gates flipping five legs
  PASS→SKIP at exit 0 with a false reason. Any gate written here without a RED
  demonstration is presumed broken.
- **Only the closing plan may tick requirements.** The Phase 116 4× premature-tick guard —
  restated in Phases 125 and 126 — means only the final plan ticks PCB-01…PCB-05, and every
  other plan is told so explicitly.
- **A `NONREGRESSION.md` per phase**, with the claim-ceiling gate applied to it. Note the
  Phase 125 self-reference trap: summaries that quote forbidden phrases inside their own
  compliance paragraphs trip the gate when scanned directly.
- **No agent runs `git push` or `gh workflow run`** — structural, not a checkpoint type.
  `--auto`/`--chain` auto-approve human-verify gates, so separation is the only real gate.

### Integration points
- Meta `.planning/` (new record) → firmware `platform/py32f071/` (subset) → the sync gate
  binding them.
- `platform/py32f071/linker/PY32F071xB_FLASH.ld` — one comment line.
- `.planning/seeds/py32f071-no-external-tool-fw-install.md` — frontmatter status (D-17).
- Meta gitlink for `firestarter` — bumped in-phase (D-05).

</code_context>

<specifics>
## Specific Ideas

- **"Never as a number that looks already paid for."** The linker comment's own phrasing is
  the standard for D-10. A bootloader figure appears only with its migration cost attached.
- **The ship gate is a condition, not an adjective.** PCB-04 says squatting "becomes a
  liability the moment a board ships"; D-09 turns that into something a future reader can
  fail: no board ships, no release advertises a USB identity, until a real PID exists.
- **The record should state its own edges.** Where the answer is not yet decidable
  (connector choice, socket/ZIF, power budget), say so — silence must not read as "no
  constraint".
- **The three-tier framing is fixed:** self-flash bootloader over CDC + COBS = intended
  primary; factory USB DFU = maintainer/manufacturing recovery; SWD = last resort. Landing
  the DFU path in v1.23 does **not** retire the self-flash seed.

</specifics>

<deferred>
## Deferred Ideas

- **Editing `usb_cdc.c` to the allocated VID/PID** — follows the pid.codes allocation, which
  follows an operator-filed public PR. A later phase or milestone; it will need an ARM build
  to stay honest.
- **Filing the pid.codes request** — outward-facing operator action, tracked as a follow-up
  from this record (D-08).
- **Propagating PCB-05 into `firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md`** — Phase 130
  or a later host phase (D-04).
- **An installer-time socket-empty prompt** — HOST scope, and unavailable this phase since
  the app repo is untouched.
- **Giving BOOTLOADER a real length** — a flash-map migration on a part with no VTOR;
  FUT-N05 owns it (D-11).
- **Software reboot-into-bootloader** — already deferred as FUT-N04; this phase only records
  its PCB consequence (D-15).
- **Introducing an ADR numbering scheme / `adr/` directory** — a repo-wide convention change
  that should not ride on a single document (D-02).

### Reviewed Todos (not folded)

The `todo.match-phase 129` matcher returned keyword-noise against a documentation phase.
None folded:

- **`correct-v128-py32-roadmap-prior-art`** — the only substantive hit, and it is already
  owned by **CLOSE-03 / Phase 130**. Folding it here would duplicate a requirement.
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads` — AVR runtime
  behaviour; unrelated.
- `prove-pio-dev-flag-fails-closed` — PlatformIO build-flag proof; unrelated (matched on
  "flag").
- `avrdude-mcu-detection-fallback` — AVR install path; unrelated.
- `cobs-decoder-framelevel-deadline-wr01` — firmware COBS decoder timing; unrelated.
- `decode-infoic-flags-bits-14-15-protect-metadata` — chip-database decode; unrelated.

</deferred>

---

*Phase: 129-Flash-Path Decision & PCB Requirements Record*
*Context gathered: 2026-08-02*
