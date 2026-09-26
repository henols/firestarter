# gh#15 Reconciliation — Acceptance Criteria, Item by Item

**Requirement:** CLOSE-04 — gh#15's acceptance criteria are reconciled item by item, each marked
`met`, `met-as-corrected` (naming the correction), or `not-reachable-on-this-hardware` (naming the
reason).

This grades the nine boxes **as originally filed** in gh#15, not the amended set our own later
comment proposed. `met-as-corrected` only parses against the text a reader actually sees at the top
of the issue — a reconciliation that graded the amended criteria instead would leave a stranger
looking at nine unticked boxes with a grading that answers a document they never opened. A reader
who never saw our earlier comment
(GitHub id `#5233463320`, filed against this same issue) gets the whole story here: the nine boxes,
what changed and why, and the one factual correction that comment itself needs.

CLOSE-04 offers exactly three literal dispositions: `met`, `met-as-corrected`, and
`not-reachable-on-this-hardware`. None of the nine boxes below draws the third. The ~6.25 V
program-VCC ceiling this milestone cannot reach bounds what any implementation of this issue can
buy — timing, pulse-count and verify fidelity, not silicon-margin fidelity — but that ceiling is a
property of the *hardware*, not of any one box's literal wording, so it travels as a named
narrowing on the boxes it touches (5, 7, 9 below) rather than standing in as a fourth box's whole
disposition. `not-reachable-on-this-hardware` remains available for a future reconciliation that
needs it; this one does not.

## The nine boxes as filed

Reproduced verbatim, in filed order, from
`.planning/phases/139-gh-15-correction-outward/139-GH15-ORIGINAL-CRITERIA.md` — itself already
verified byte-identical to the live issue body's tail, so nothing below is re-scraped from GitHub:

1. `0x07`, `0x08`, and `0x0B` use separate write handlers.
2. No new database algorithm flags are introduced.
3. `EPROM_STD` uses per-byte fixed 1 ms pulse/verify cycles and a final overprogram pulse.
4. `EPROM_QUICK` uses its own fixed short-pulse handler.
5. `EPROM_LEGACY` uses a long fixed programming pulse rather than the current adaptive loop.
6. The current block mismatch/adaptive pulse-growth algorithm is removed from EPROM writing.
7. VPP routing remains protocol-correct and is disabled on all exits.
8. Native tests cover dispatch, pulse behavior, verification, failure, and cleanup.
9. All firmware targets build successfully.

## Disposition table

| # | Disposition | Correction or reason |
|---|---|---|
| 1 | **met-as-corrected** | Our own comment replaced this premise, in its own words: "Protocol owns *shape*; the database owns the *pulse*. One shared per-byte loop, driven by a `const` table keyed by `protocol_id`, replaces three handlers that would otherwise duplicate most of their own body — on a device with a hard AVR flash budget." The issue asked for three separate write handlers, one per protocol; what shipped is one shared per-byte pulse-then-verify loop plus a single `const`, PROGMEM, `protocol_id`-keyed table (`eprom_params_t`, `firestarter/include/eprom_params.h:38-58`, `firestarter/src/proms/eprom_params.cpp`) carrying `max_pulses`, `overprogram_factor`, `overprogram_cap_us`, `verify_mode` and `vpp_path` — no pulse-width column, because pulse width stays `handle->pulse_delay`. |
| 2 | **met** | Unchanged, as filed. No new `chip_database.json` algorithm field was added; `protocol_id` remains the single dispatch key end to end (`firestarter/CLAUDE.md` §"Protocol Dispatch"; `.planning/REQUIREMENTS.md` §"Out of Scope" row 1). |
| 3 | **met-as-corrected** | Our own comment's correction, in its own words: "The per-byte loop and the final overprogram pulse are this issue's central, correct insight, and both are kept. The `1 ms` is wrong: `0x07`'s most common value is `100 us`, and it spans `50` to `1000 us` across the shipped database." What shipped: `configure_eprom`'s `pulse_delay == 0` fallback for `0x07` is `1000` us (`firestarter/src/proms/eprom.cpp:69-73`), used only when the database supplies no value; the database-supplied pulse is the modal value in 113 of 170 `0x07` chips at `100` us. The per-byte pulse-then-verify loop and its final over-array verify pass (`verify_mode == VERIFY_PER_PULSE_PLUS_FINAL`) are exactly as the issue asked. |
| 4 | **met-as-corrected** | Our own comment's correction, in its own words: "\"Its own handler\" falls with the row above. \"Fixed\" falls with the pulse-width evidence above: `0x08` spans `10` to `1000 us` across 6 distinct values, and 23 of 127 chips are not `100 us`." What shipped: `0x08` shares the same loop as every other row in the table (no dedicated handler), and its `pulse_delay == 0` fallback is `100` us (`firestarter/src/proms/eprom.cpp:71`), matching 104 of 127 chips but not the other 23. |
| 5 | **met-as-corrected** | Our own comment's correction, in its own words: "Dropping the adaptive loop is kept. \"Long\" is wrong — that is the `50000 us` ×100 bug above; the true value is `500 us`." What shipped: `0x0B`'s `pulse_delay == 0` fallback is `500` us (`firestarter/src/proms/eprom.cpp:72`), not `50000` us, and the current adaptive loop this box's own phrase names is gone (see box 6). This box's separate `energy_cap_us = 50000UL` (50 ms) is a per-byte accumulated cap, not a pulse width — see "The public correction" below, which corrects our own earlier justification for that number. |
| 6 | **met** | Unchanged, as filed. `configure_eprom`'s per-byte loop (`firestarter/src/proms/eprom.cpp:341-494`) pulses at a fixed width, verifies, and either advances or retries up to `max_pulses`; no attempt widens the pulse between retries, and a byte that exhausts `max_pulses` hard-fails the block via `MSG_ERR_MAX_PULSES` with the failing address and pulse count, not a silent partial success (`eprom.cpp:467-468`). The block-level mismatch mask and adaptive pulse-growth formula the issue names are removed, not retained under another name. |
| 7 | **met-as-corrected** | Two narrowings, named rather than left implied by a bare "kept, unchanged." (a) Every **error** exit from the write path — verify failure, max-pulse failure, any other error return — disables every active control-register high-voltage route through a single-exit wrapper (`firestarter/src/proms/eprom.cpp:209`, `:525-527`; quoted from `firestarter/CLAUDE.md` §"Algorithm Handlers": "Every **error** exit from the write path disables every control-register high-voltage route through a single-exit wrapper"). (b) The **operation**-level disable — `command_done()` — is a **source contract**, not a behavioural result: it is asserted by native tests against production code but never observed as a voltage on any rail, because the file that owns the Uno-class UART teardown (`firestarter/src/boards/uno_rurp_shield.cpp`) compiles in no native environment. And a **successful** block deliberately leaves the route energised rather than disabling it, so the once-per-block VPP settle is not re-paid on every byte (D-09, D-10 as amended, `142-VPP-RECORD.md`). VPP routing itself is unchanged in shape: one shared `eprom_hv_route_mask()` resolves the route for both `eprom_check_vpp()` and the write path from the table's `vpp_path` column (VPP-01, VPP-03), so no protocol crosses into another's route. |
| 8 | **met** | Kept, with two narrowings named rather than left implied. "Dispatch" now means **table-row selection** — `eprom_params_for()` resolving a `protocol_id` to its row — rather than handler selection, because there is only one handler left (box 1). And one coverage claim — that the write path disables every high-voltage route on the exits box 7 names — is established **only in the emitted control-register stream**, never behaviourally and never on real hardware (`144-TEST-RECORD.md`:438-439). Within those two narrowings, native suites do cover dispatch (`native`/`native_nodevtools`, 141 cases / 17 suites each), pulse behavior and verification (`native_params_v131`, 9 cases; `native_loop_v131`'s `test_loop_eprom_v131`, 47 cases), failure (`MSG_ERR_MAX_PULSES` asserted by TEST-04), and cleanup (the single-exit wrapper asserted by native tests against production code, per (a) above) — none of `native_params_v131`, `native_loop_v131` or `native_trace_v131` runs in any CI leg of either repository, a fact this box's grading does not paper over. |
| 9 | **met-as-corrected** | All four firmware build targets build against this milestone's code: the three AVR targets are measured at this tip — `uno` 24920 B, `uno328pb` 24970 B, `leonardo` 27002 B, RAM 1573/1579/2014 — each carrying MERGE-05's admitted, SHA-attributed +96 B defect-fix exemption (cited from `.planning/STATE.md:2043`, not re-measured here), and the ARM `py32f071` CMake target — which did not exist when this issue was filed — was compiled against this milestone's code for the first time in Phase 146 plan 146-03, emitting exactly one `firestarter_py32f071.hex` (78769 B, sha256 `5b0b55a2d71282a1899d3a931c673357912e1993a942934c26e67f61a4bebf8e`) under the firmware repository's own composite-action oracle; that ARM result is a local **delta** against a target no CI run has ever compiled against any v1.31 code — it is **not CI parity**, and no PY32F071 circuit board exists anywhere in this project, so it establishes nothing about hardware (`146-ARM-BUILD-RECORD.md` §3). Neither repository's CI has run against any v1.31 code beyond Phase 138 (`146-ARM-BUILD-RECORD.md` §1) — stated once here because it bounds every AVR reading in this row too, not only the ARM one. |

## The public correction

Our own earlier comment (`139-GH15-COMMENT.md`) said, verbatim:

> "`0x0B` loops pulse-then-verify with a 50 ms accumulated-energy cap per byte (`100 × 500 us`,
> which is the classic 2716 total programming time) and no overpulse row at all."

That sentence is wrong about *why* the number is 50 ms. The TI TMS 2516 datasheet's own recommended
timing table states its total programming time for **all bits** is **100 seconds**, not 50 ms; the
50 ms figure is the *per-location* typical pulse width, `t_w(PR)` TYP (45/**50**/55 ms) — a different
quantity than the one our sentence named (`140-PARAM-TABLE-RECORD.md:259`). The shipped **value**
(`energy_cap_us = 50000UL`, 50 ms) has a genuine primary-datasheet basis; the published **reason**
for it did not.

One more nuance the firmware's own protocol reference already carries, load-bearing for box 5's
grading above: the datasheet specifies a single 50 ms pulse per location, permits verification
immediately after that one pulse, and specifies **neither** a final full-array pass **nor** an
over-program step — while the firmware ships a looped pulse-verify under a 50 ms **accumulated**
per-byte cap instead of a single unconditional pulse. Both readings are satisfied by the same 50 ms
figure read two different ways (`firestarter/doc/PROTOCOLS.md:250-254`).

This is a correction to the **public** record, not to the firmware: `firestarter/doc/PROTOCOLS.md`
§1.5 already carries the identical correction, landed in place by Phase 140 before this phase ran
(`firestarter/doc/PROTOCOLS.md:255-259`). What was still uncorrected was our own earlier comment on
gh#15 itself — the copy a stranger reading the issue thread actually sees — which this section
corrects.

## Bench boundary

The one protocol this issue's acceptance criteria require, `0x07`, completed a full
write-read-verify cycle on one part with its chip identifier — the Winbond **W27C512**, chip-id
`0xda08` — on one controller, `leonardo`, with one shield revision read off the silkscreen by the
operator because the stored `hw_revision` byte cannot distinguish Rev 2.0 from Rev 2.2 from a
modified Rev 0. The other two protocols this issue names, `0x08` (needs an AM27C020) and `0x0B`
(needs an M2716/M2732), are **skipped-with-reason** — no part of either kind was on the bench this
milestone, and neither disposition is inferred from the `0x07` result: the three protocols share a
write path but not a part, a VPP path, or a bench outcome. The ceiling restated: the raised
program-VCC all four vendor algorithms assume for threshold margin, roughly **6.25 V**, is
unreachable on this shield, so what this milestone buys is timing, pulse-count and verify fidelity
and not **silicon-margin** fidelity. This record makes no comparative claim — fidelity, not
improvement, with no pre-milestone control run by design, and the **22.84 s** pre-v1.31 write figure
appearing in the bench log's own cycle-1 record is a recorded historical number, not a control
measurement (`145-BENCH-LOG.md:2700-2706`). And this record takes no position, either way, on how
closely the shipped algorithm follows any datasheet — a limit stated in the bench log's own
"Boundaries" section, cited here by line range rather than quoted because that section's own wording
there carries a phrase this phase's claim gate forbids unqualified (`145-BENCH-LOG.md:2707-2709`).

---

Full evidence tiers, the four-column claim table, and the twelve carry-forwards: `146-LEDGER.md`.
Mechanism corrections in full, including the ones this reconciliation cites above: `146-CORRECTIONS.md`.
