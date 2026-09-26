# v1.23 Honesty Ledger — PY32F071 Integration

**Milestone:** v1.23 — PY32F071 Integration
**Firmware branch (`firestarter`):** `v1.23-py32f071-integration` · **HEAD at this writing:** `05c20bf59a4f0f73acf28d48d5dbbedab5724c5f`
**Host branch (`firestarter_app`):** `v1.23-py32f071-integration` · **HEAD at this writing:** `cc9452f4db9a814ffb221bab767c24db67288365`
**Meta branch:** `gsd/v1.23-py32f071-integration`
**Published cut tag:** **`3.0.0b15`** — observed, not predicted, quoted verbatim from `gh release list` in both `henols/firestarter` and `henols/firestarter_app` (`130-CHANNELS.md` §1: `3.0.0b15 Pre-release 3.0.0b15 2026-08-02T21:22:42Z` / `2026-08-02T21:21:19Z`). Both channels are public at this tag: the firmware GitHub prerelease carries four `.hex` assets including `firestarter_py32f071.hex` (first-ever publication of that asset), and PyPI carries the host app (`firestarter==3.0.0b15`, resolved from a clean venv). No stable release exists — PyPI `info.version` remains `2.0.7`. Filled by plan 130-16.
**Oracle:** software-only — native register trace (`pio test -e native` / `-e native_nodevtools`), host pytest (`firestarter_app`), source-scan gates (`tools/check_*.py`, this phase's `check_permitted_claims.py` / `check_record_corrections.py`), a local ARM configure+build (delta and byte-identity claims only), and two operator-authorised CI rehearsal dispatches of `beta-build.yml`. **No PY32F071 hardware exists**, so no board-level oracle contributed anything below.
**Generated:** 2026-08-02

**Composes with (cross-reference only — no data copied):**
- `.planning/REQUIREMENTS.md` §"Validation Ceiling" — the permitted-claim / forbidden-claim ceiling this ledger distils into evidence tiers
- `.planning/v1.23-FLASH-PATH-DECISION.md` — cross-reference only, no data copied, per that record's own line 28 ("this record's per-claim pairs are what CLOSE-02's honesty ledger consumes... by cross-reference")
- `.planning/research/SUMMARY.md` §"What Cannot Be Validated" — the raw material for the negative-space section below
- `.planning/phases/124-firmware-integration-merge/124-NONREGRESSION.md` §F4d — the A-5 discharge citation
- `.planning/phases/127-host-dfu-installer/127-NONREGRESSION.md` §7 — HOST-03's mock-only ceiling paragraph, cited rather than duplicated
- `.planning/phases/128-release-asset-fold/128-NONREGRESSION.md` §7 — REL-03/REL-04's stated seams
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-LEDGER.md` — the structural analog this document's shape follows

**Referenced and verified here, never edited.** `.planning/v1.23-FLASH-PATH-DECISION.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md` and `.planning/PROJECT.md` are all read by this document and none is written by it — this plan's own held-writes contract forbids it, and all five were independently brought green under `check_record_corrections.py` by plans 130-06 through 130-10 before this plan started.

---

## The ceiling, quoted verbatim

Attributed to `.planning/REQUIREMENTS.md` §"Validation Ceiling":

> **Permitted claims:** the target builds clean; the native and host suites pass at their recorded case *and* suite counts; the DFU sequence is exercised against device descriptors and mocks; host-side timing and sizes are measured where a tool exists to measure them.

**Forbidden claims:** cited by location rather than reproduced — `.planning/REQUIREMENTS.md:14`. This ledger does not repeat that line's five forbidden phrasings: doing so would trip this same document's own claim scanner (`check_permitted_claims.py`), which matches a phrase's shape regardless of quotation context, by design. That is the gate working as intended, not a defect to route around — the permitted-claims sentence quoted above is safe to reproduce because it contains no trigger shape.

**No PY32F071 hardware exists.** Every figure in this document has a software artifact as its subject — a golden register trace, a `pio run` size report, a pytest exit code, a source-scan result, a local or CI build log — never an observation made on a physical board.

---

## Status / claim key

- **`PERMITTED`** — a wording backed by a measured, re-runnable software artifact (a trace, a test, a source scan, a size report, a CI run).
- **`CONTEXT-ONLY`** — measured, cited for context, but explicitly not a gate.
- **`FORBIDDEN`** — the ceiling's forbidden claim. Appears in this ledger only as a citation of what is *not* claimed, never as prose asserting it.

## Sourcing key (Phase 129's vocabulary)

- **`[VERIFIED]`** / **`[VERIFIED: <evidence>]`** — a fact read from a file in this tree, or executed in this session.
- **`[CITED: <source>]`** — a fact from a published document or an external record (a CI run URL, a registry page).
- **`[ASSUMED — <reason>]`** — a reasoned inference, not directly sourced.
- **`[UNVERIFIED-UNTIL-SILICON]`** — anything whose truth depends on a PY32F071 part behaving as documented. No PY32F071 board exists, so every silicon-behaviour claim carries this tag regardless of documentation quality.

**These two axes answer orthogonal questions** — the status key says what may be *written*; the sourcing key says where the *fact* came from — and a row can legitimately be `PERMITTED` and `[ASSUMED]` at once: a permitted claim can rest on a reasoned inference, so long as the inference itself, not a silicon observation, is what is being claimed.

---

## Evidence tiers — weakest to strongest

This milestone's defining fact is that **all of it is software-only**: a green CMake configure and a published release asset are not comparable proof, so grouping claims by evidence tier — rather than one row per requirement category — is what keeps two adjacent rows from reading as equally strong. The six tiers below are ordered so the strength gradient is visible on the page; only the last two tiers touch anything published or decided about a physical board, and even there the permitted wording never extends past publication or decision, never to a board running.

### CI-compile-only

| Class | Permitted wording | Evidence (measured, with source) | Explicitly does NOT prove |
|---|---|---|---|
| **The ARM target configures and compiles** `PERMITTED` `[VERIFIED: CI run 30722352902]` | The PY32F071 target reaches a successful CMake configure and links a complete image inside CI, after the version bump, in the same job as the three AVR images. | MERGE-02 (Phase 124); the REL-01 step-order proof (`128-NONREGRESSION.md` §2.1: version/auto-commit/arm/Release step indices strictly increasing) plus a real dispatch, CI run `30722352902` — 22/22 steps `success`. | That the resulting image executes anything once written to a part — a successful compile says nothing about runtime behaviour. |
| **The version string is embedded correctly** `PERMITTED` `[VERIFIED: CI run 30722352902 step summary]` | The published image's version string matches the release version the host will compare against the tag (REL-01). | `128-NONREGRESSION.md` §3.5 — the run's own step-summary pass line, naming the dispatched version and board suffix. | Anything about the image beyond the string it embeds. |
| **A deliberately-broken ARM leg cannot silently take down the AVR release** `PERMITTED` `[VERIFIED: CI run 30722537152]` | A planted ARM-configure failure is contained: the three AVR `.hex` assets still publish, and the release step still succeeds, with a warning annotation naming the missing py32 asset. | `128-NONREGRESSION.md` §3.7–§3.9, a second real CI dispatch against a deliberately broken source-list entry (reproducing the historical C-1 defect on purpose). | That the failure-containment machinery has ever been exercised against a *real*, non-planted ARM regression — this is a planted-fault rehearsal, not an observed incident. |

### AVR-measured

| Class | Permitted wording | Evidence (measured, with source) | Explicitly does NOT prove |
|---|---|---|---|
| **AVR flash and RAM recorded for all three targets** `PERMITTED` `[VERIFIED: 124-NONREGRESSION.md §F4d]` | Leonardo flash **does not grow** (26072→26016, −56 B); Uno-class growth is **≤64 B, recorded** (Uno +22 B, uno328pb +28 B); RAM is unchanged on every target — measured against the BASE-01 baseline. | `check_size_baseline.py --policy merge05`, run and recorded in `124-NONREGRESSION.md` §F4d: `PASS: uno(flash=23954/32256[+22<=64],ram=1573/2048[=]), uno328pb(flash=24004/32384[+28<=64],ram=1579/2048[=]), leonardo(flash=26016/28672[-56<=0],ram=2014/2560[=])`. | Anything about behaviour — a size delta is not a behaviour proof; the golden register traces (below) carry that half. |
| **The native suite passes at its recorded count** `PERMITTED` `[VERIFIED]` | `pio test -e native` and `-e native_nodevtools` both report **141 test cases / 17 suites**, matching the BASE-01/Phase-123 baseline, unchanged by the merge or any later plan. | `124-NONREGRESSION.md`, re-confirmed by `128-NONREGRESSION.md` §2.8/§2.9. | That any of this exercises code compiled for the ARM target — `native` runs the AVR-family emulation host, never the ARM cross-compile. |
| **Golden register traces are byte-identical** `PERMITTED` `[VERIFIED]` | The merge's macro-to-`static inline` conversions and the portability shim are behaviour-identical to the pre-merge tree, proven per-array (not whole-file-hash) for `_shared/sdp_expected.h` and the other golden trace arrays. | `124-NONREGRESSION.md` §4/§5. | Anything about the ARM backend, which emits no register trace this harness records (see the ARM bus-trace oracle gap, below). |
| **The AVR flash-constraint decision — discharged at Phase 124** `PERMITTED` `[VERIFIED: 124-NONREGRESSION.md §F4d]` | The operator-visible flash constraint is restated as *"Leonardo flash must not grow; Uno-class growth ≤ 64 B, recorded"* — discharged, not merely satisfied on paper: `124-NONREGRESSION.md` §F4d's own pass line is the single citation naming all three deltas, closing the single-source gap research (A-5) had flagged for the ATmega328PB figure with an independently-built 328PB image. | `124-NONREGRESSION.md` §F4d, lines 100/505–510. | Any absolute figure for the ARM target — this row is entirely about the three AVR targets. |

### native-simulated

| Class | Permitted wording | Evidence (measured, with source) | Explicitly does NOT prove |
|---|---|---|---|
| **Dual-slot flash-config storage, covered against a fake backend** `PERMITTED` `[VERIFIED]` | CFG-05's dual-slot CRC32 storage design is covered on `native` against a fake backend across six named states: blank, newest-wins, CRC rejection, both-slots-corrupt, an interrupted write, and slot alternation. | Phase 126 plan SUMMARYs; `REQUIREMENTS.md` CFG-05. | That the target part's own flash-erase/write hardware behaves as the fake backend simulates — the fake backend is a native-host stand-in, never the part's own flash controller. |

### mock-only

| Class | Permitted wording | Evidence (measured, with source) | Explicitly does NOT prove |
|---|---|---|---|
| **`DFU_UPLOAD` readback, asserted against a mock** `PERMITTED` `[ASSUMED — the mock behaves exactly as instructed, per 127-NONREGRESSION.md §7]` | HOST-03's readback-and-verify sequence (the verify-result enum, the read-back step, the verify step, and all four of its outcomes) is exercised against a mock USB device that answers exactly as it is told, and fails soft when the device reports it cannot upload. | `127-NONREGRESSION.md` §7's self-contained paragraph: a matching backing image produces a verified outcome, an altered byte produces a mismatch outcome, a short slice produces a truncation failure. | That any of this sequence has ever exchanged a byte with a real bootloader. What is proven is that the flasher's own logic responds correctly to told answers, and nothing beyond that — this is one of CLOSE-02's four named minimum-coverage items. |
| **DFU opcode anchoring, independently sourced where possible** `PERMITTED` `[CITED: usb.org DFU 1.1 spec]` for the DFU-1.1 half; `CONTEXT-ONLY` `[UNVERIFIED-UNTIL-SILICON]` for the vendor-bootloader-specific half | The DFU 1.1 request codes, functional-descriptor type, and the upload-capability mask are anchored to literals fetched independently from `usb.org`, not imported from the module under test. | `127-NONREGRESSION.md` §Criterion 4 (`tests/test_dfu_opcode_anchors.py`, 7 tests). | That the vendor-bootloader-specific half of this anchor is independently confirmed — HOST-06's own residual states that source remains network-unreachable; see the residuals list below. |
| **The DFU sequence exercised against descriptors and mocks generally** `PERMITTED` `[VERIFIED]` | The whole py32 DFU client — discovery, class-based interface matching, the dialect fork, envelope refusal — is exercised against synthetic USB device descriptors and mock transports across the host test suite. | `127-NONREGRESSION.md` §2/§5. | Which of the two dialect branches a real bootloader would actually take — this fork has never been exercised against a real device by anyone, anywhere, per this project's own research. |

### real-published-artifact

| Class | Permitted wording | Evidence (measured, with source) | Explicitly does NOT prove |
|---|---|---|---|
| **A named, versioned release asset — pending observation** `PERMITTED`, pending `[ASSUMED — the publication mechanism is CI-proven via rehearsal; the real cut has not yet been observed, owed to plan 130-15]` | Once observed, the only permitted claim here is about **publication**: a file with a specific name, carrying a specific version string, became a downloadable release asset on the firmware repository's release page. Two operator-authorised rehearsal dispatches already demonstrated the mechanism at the CI level (see the CI-compile-only tier above), but no real, non-rehearsal cut has been observed by this plan. | `128-NONREGRESSION.md` §3 (the two rehearsal runs); the actual cut awaits `gh release list`, read by plan 130-15. | Anything about the published image running, booting, or installing — publication is the entire claim, and at the time this ledger is written it is not yet even a discharged claim. |

### decision-only-unverified

| Class | Permitted wording | Evidence (measured, with source) | Explicitly does NOT prove |
|---|---|---|---|
| **The provisional pin map** `PERMITTED` (as a decision) / **FORBIDDEN** to assert as fact — cited `.planning/REQUIREMENTS.md:16` `[ASSUMED — the VPP-sense pin follows the vendor's own ADC example; no schematic exists]` | A pin assignment exists so the target compiles before a schematic: the eight data lines, six control lines, and a VPP-sense channel. This is a placeholder that describes no existing PCB, chosen only to match the vendor's own reference example, nothing more. | `v1.23-FLASH-PATH-DECISION.md` §1.5/§3 R5; `include/boards/py32f071_rurp_shield.h`'s provisional-pin-map marker. | That any assignment is correct once a schematic exists. This is one of CLOSE-02's four named minimum-coverage items outright — see the negative-space section below for the mechanical enforcement this map still lacks. |
| **The USB identity decision** `PERMITTED` (as a decision) `[VERIFIED: firestarter@05c20bf]` / the ship-gate binding itself `[UNVERIFIED-UNTIL-SILICON]` because no board yet exists to ship | The descriptor now presents pid.codes' documented private-testing pair, replacing the silicon vendor's own registered pair the board previously presented; the value swap is confined to one source file, proven by a local ARM delta pass (one recompiled translation unit, numerically unchanged section sizes, a differing image hash). | `130-03-SUMMARY.md`; `.planning/v1.23-FLASH-PATH-DECISION.md` §5. | That an allocation under the community VID exists, or that the ship-gate binding — no board ships, no identity advertised, until a real allocation exists — has been satisfied. See the D-17 negative-space row below; this decision does not resolve that gate. |

---

## Mechanism corrections recorded here, not in `REQUIREMENTS.md`

`REQUIREMENTS.md`'s own wording is deliberately left alone for corrections where a requirement's stated *mechanism* turned out narrower or different — the same discipline this project applied at LOCK-04, LOCK-06, HOST-04, and Phase 121's D-06/D-17: satisfy the intent, record the correction in the phase artifact, leave the requirement text alone.

Plan 130-10 **did** amend two `REQUIREMENTS.md` clauses in place (PCB-03 and FUT-N04's stated VTOR-absence reason) rather than following that discipline, and the exception is exactly this project's own stated boundary: those two clauses asserted a **fact** that is simply false — that the target part lacks a vector table offset register — and a false fact does not survive being merely annotated elsewhere the way a narrower mechanism does. `REQUIREMENTS.md` itself now carries this fact-versus-mechanism boundary in a dedicated paragraph (added by plan 130-10, adjacent to FUT-N04), naming LOCK-04/LOCK-06/HOST-04/121 D-06/D-17 as the mechanism-class precedents the boundary does not disturb.

1. **PCB-04's Phase-129 clause, reversed as a reversal, not silently.** `.planning/v1.23-FLASH-PATH-DECISION.md` §5(d) previously stated the USB descriptor source stays unedited "this phase" — true as written for Phase 129, which declined the edit only because it was documentation-only with no cut planned. This phase's D-11 **reverses** that decision: publishing an image is a new fact Phase 129 did not have to weigh. Both flash-path-record copies now state the reversal explicitly, with the constraint named, per plan 130-03.
2. **The toolchain-absence premise, narrowed in `REQUIREMENTS.md` itself (plan 130-10), not merely recorded here.** The ARM cross-compiler and its build tools are present, install, and work in this devcontainer — the false "absent" premise is corrected in place because it was a fact, not a mechanism, and the surviving conclusion (an absolute ARM size claim still needs a CI run URL plus a commit SHA) is kept for the *better* reason research supplied: the local and CI compilers differ and produce different absolute sizes for the same source (measured `text=27260` local vs. `text=27344` CI).
3. **The claim-gate `_DEFAULT_TARGETS` repoint (RESEARCH C-2).** Plan 130-01 repointed the four contracted artifact paths from this checker's own Phase 123 directory (where they could never exist) to the sibling Phase 130 directory, per the module's own "Phase 130 coupling" docstring paragraph — the sanctioned same-commit amendment that paragraph requires, taken ahead of any artifact landing so the gate is armed *before* the first one, not after.

---

## What this milestone chose not to prove

A close that lists only wins reads as overclaiming even when every individual claim is true. This is the negative space.

### Deferred by decision or on research grounds — eight entries, `.planning/REQUIREMENTS.md` §"Future Requirements" lines 109–128

- **FUT-N02** — live progress reporting during firmware install. Deferred because avrdude's own progress is swallowed by process-pipe buffering on all three shipped AVR boards; adding it to the new target alone would give the least-proven path the project's only live feedback.
- **FUT-N04** — software reboot-into-bootloader (removing the strap-jumper dance). Its first stated reason (VTOR absence) is corrected false by this phase (see the mechanism-corrections section above); the deferral itself still stands on its three remaining reasons — the memory-remap mechanism is reported to have no effect on some sibling parts, it cannot be validated without a physical part, and FUT-N05 obsoletes it for the normal path.
- **FUT-N05** — the self-flash bootloader over the existing serial + framing transport. The seed's own primary route, its own milestone; landing the DFU path this milestone does not retire it.
- **FUT-N06** — publishing a raw binary release asset alongside the Intel-HEX image. Host acceptance already exists; publication waits until FUT-N05 needs it.
- **FUT-VPP** — closed-loop DAC-driven VPP control with independent overvoltage shutdown. Inseparable from the calibration model it shares an API with, and unvalidatable without a physical board.
- **FUT-CAL** — the cross-platform bandgap-reference + two-point calibration model. Owned by the queued White-Box Voltage-Reading Calibration milestone.
- **FUT-ORACLE** — a bus-trace oracle for the ARM target, so its emitted register sequences could be compared against the AVR goldens. Does not exist; see the negative-space row below naming the consequence.
- **FUT-ARMSIZE** — ARM flash/RAM as a checked-in baseline with a RAM ceiling. CI already runs a size-reporting step, but only into the job log — nobody would notice a regression there today.

### Trade-offs and residuals this milestone's phases recorded and owned

- **F-10, given top billing.** A contiguous 8-bit data bus is physically impossible on two of the seven candidate packages (two adjacent lines are not bonded on one package; six of eight lines are not bonded on the smallest package) — a **part-selection** constraint, unrecoverable once layout starts, decided before it. Five packages remain viable for this design. `.planning/v1.23-FLASH-PATH-DECISION.md` §1.5/§3 R3.
- **HOST-01** — the firmware-flasher dispatch router and the untouched avrdude installer path are recorded as an **accepted deviation** from the prescribed flasher-strategy extraction, not a defect: the constraint was to keep the bench-earned avrdude ladder verbatim, and the branch achieves it precisely by not touching that function at all.
- **HOST-04** — a CI leg installs the full test-plus-py32 dependency set and exercises the real USB-library import and API surface, confirmed green on a specific CI run; the primary CI job's separate, unrelated type-checking debt failure is **not** this requirement's claim and is stated as a distinct finding, per `127-NONREGRESSION.md` §3/§6.
- **HOST-06** — DFU opcode literals are anchored independently to the fetched USB DFU 1.1 spec; the vendor-bootloader-specific half of that anchor remains an unresolved residual, network-unreachable during this milestone.
- **REL-03** — the claim that a deliberately broken ARM build still publishes all three AVR assets has its assertion-fails-on-a-missing-asset half proven **locally only** (two planted-fixture exit-1 proofs), not exercised inside a CI job this phase — `128-NONREGRESSION.md` §7 Criterion 3 states this explicitly rather than folding it into the CI-proven half.
- **REL-04's F-8.** The cross-repo three-way filename binding between the two repos is proven **locally** (ten tests, zero skipped); it is enforced by **neither** app CI workflow, because neither checks out the firmware sibling. The binding holds by local runs and developer discipline, not by CI in either repo — say so rather than implying otherwise.

### One residual this phase itself owns — D-17

The USB-identity ship-gate tension is carried here as a **tension**, not a resolution. The gate reads: no board ships, and no release advertises a USB identity, until a PID allocated under the community vendor id exists. The interim pair now in the descriptor is the registry's own documented private-testing pair, not an allocation. This phase's D-11 publishes an image whose descriptor discloses that pair, caveated in-source (worded as an ask, per the registry's own "should," never as a requirement, per RESEARCH C-6) — and this ledger records why that disclosure is not read as advertising an identity, while stating plainly that a future reader may decide otherwise, which the gate's own wording deliberately permits by being a condition rather than a warning. The full reasoning lives in `130-DECISION.md`; this row is the pointer, not the argument. Also recorded here: RESEARCH's own assumption A3 — publishing an image that carries the interim pair is taken **not** to violate the registry's no-redistributed-device clause, because no device (no board) is being redistributed; this is a judgment call, named as one, not a settled reading of the registry's terms.

Two Phase 129 open hardware questions, both `[UNVERIFIED-UNTIL-SILICON]`:
- **The boot-selection option bit's factory default.** Unknown from either the datasheet or the vendor's bootloader manual; if the bit selects the wrong boot area, the DFU recovery path is gone.
- **Whether the USB PHY provides an internal D+ pull-up**, or whether a discrete pull-up resistor is required on the board. Answerable only from the reference manual's USB chapter or a real part; not guessed here.

---

## What no test, gate or review in this phase can close

Reproducing the three-way split this project's prior closes have used, in this document's own voice, because auditing exactly this split is the whole point of writing it.

**Mechanically checkable, cheap, re-runnable.** Every CLOSE-01 sub-claim; this ledger's own presence and its passing scan; the default-mode transition this phase's commit produces (recorded below).

**Requires the blocking operator wording review (D-02).** Whether the prose in this ledger and both release bodies is *honest*, not merely free of eight banned strings. A string scan cannot detect an implied overclaim, cannot judge whether a phrase's *absence* misleads a reader, and cannot weigh tone.

**Inherently unverifiable in-phase, at a sampling rate of zero, by design — CLOSE-02's four named minimum-coverage items, at minimum:**
- **The provisional pin map**, named above, has no schematic to confirm it against.
- **The absent ARM bus-trace oracle.** `HOST_STUBS_RECORD_BUS`, the register-write recording harness, runs on `native`, never on the ARM target — the ARM target's emitted register sequences could diverge from the AVR-family goldens with nothing able to notice. FUT-ORACLE names the deferred fix; nothing in this milestone builds it.
- **Unmeasured USB-interrupt-versus-PROM-pulse timing.** The USB write path spins with interrupts masked while the microsecond delay primitive busy-polls a hardware timer; a prior milestone's own measurement on a different board class found **572 µs against a 600 µs budget** (4.7 % headroom) — that measurement is a different board's number, cited for context, and **is not** a measurement of this milestone's target.
- **The mock-only ceiling on HOST-03's readback**, named in the mock-only tier above.

**The two-claims-never-conflated rule, restated in this document's own words:** a successful firmware install — one that transfers bytes and, where a readback exists, matches on comparison — says nothing about the *programmer* (the assembled device that will one day hold a PROM and drive its control signals) working. One is a transport-and-storage claim; the other is a hardware claim about a board that does not exist. This ledger, and both release bodies it governs, keep the two apart everywhere.

---

## The community inbox — not implied clear

No community thread receives a comment this milestone, and no CLOSE requirement depends on a reply. Per RESEARCH C-18, the inbox is **not empty**: gh#20 (an AT28C256 chip-validation failure reported 2026-07-30) and gh#18 both arrived **after** the 2026-07-27 backlog import that stopped at gh#17, and both are out of scope for this milestone. This paragraph exists so no reader of this ledger, or of either release body it governs, concludes the inbox is clear.

---

## Scanner status

This document is one of `check_permitted_claims.py`'s four contracted default targets for Phase 130. It is required to exit 0 when scanned by name, carrying the required silicon caveat above and zero forbidden-phrase matches within a target-token's proximity window, before it is committed. **A green result from that scanner is the mechanizable half of this milestone's honesty criterion only** — per the scanner's own module docstring, it cannot detect an implied overclaim, a misleading omission, or wrong tone, and a green run must never be reported, here or in any SUMMARY, as by itself satisfying the honesty criterion. The non-mechanizable half is **D-02's blocking operator wording review**, which precedes any release body reaching a public, outward-facing release — that review, not this scanner, is what actually closes the honesty question this ledger exists to organise evidence for.

Immediately after this document is committed, the claim gate's **default-mode** run transitions for the first time in this milestone: with exactly one of the four contracted artifacts now on disk, the gate's all-or-nothing arming (D-15) makes the run **FAIL** (exit 1), naming the three still-missing artifacts as a hard failure rather than a skip. This is **not a regression** — it is the positive, first-time evidence that plan 130-01's repoint of the default-target list (RESEARCH C-2) took effect in the real directory: before this commit, the default-mode run printed an `UNARMED:` notice and exited 0 because none of the four artifacts existed; the transition to a named, itemised failure is D-15's arming working as designed, observed for the first time. The exact transcript of this transition is recorded in `130-11-SUMMARY.md`.

---

*Phase: 130-close-honesty-ledger-claim-gate-release-decision*
*Written: 2026-08-02 (Plan 130-11)*
