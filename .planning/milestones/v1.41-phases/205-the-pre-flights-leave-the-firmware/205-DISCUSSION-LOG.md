# Phase 205: The pre-flights leave the firmware - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-22
**Phase:** 205-the-pre-flights-leave-the-firmware
**Areas discussed:** Todo folding, `erase -b` disposition, the `0x08` bit, the bench legs, the orphans and the reserved records

---

## Todo folding

| Option | Description | Selected |
|--------|-------------|----------|
| Negative write address — firmware half | `2026-09-16-reject-negative-write-start-address.md`. 203 folded the host half; both 203 and 204 deferred the firmware half here by name. `json_parser.c`'s `simple_strtoul` consumes only `[0-9]`, so a leading `-` silently becomes 0 | |
| `region-end` has no json_parse coverage | `2026-09-20-region-end-wire-key-has-no-json-parse-coverage.md` (201-REVIEW WR-01). Tests set `handle->region_end` directly on the C struct, so a PROGMEM-key typo reddens nothing | |
| Neither — keep 205 to FWBLANK-01…05 | Both stay open; 205 is already a dual-repo removal with two bench legs, a golden re-derive and a gate retirement | |

**User's choice:** "you decide"
**Notes:** Decided by Claude — fold the negative-address firmware half as its own plan/commit
(205 is its last dual-repo home in v1.41; a bisect lands on a commit, not a phase, so 204's
bisect objection is satisfied by commit separation). Do **not** fold the `region-end` coverage
todo: never routed here, adds coverage rather than fixing a defect this removal touches, and
`region_end` demonstrably survives the phase. Noted as near-free if the folded fix stands up
json_parse native coverage anyway. Two further todos fold by construction —
`2026-08-30-write-init-blank-check-is-whole-device.md` (FWBLANK-01 *is* its firmware half) and
`2026-09-20-blank-check-region-fails-open-on-start-greater-than-end.md` (closed by deletion, not
by the local clamp it proposes).

---

## `erase -b` disposition

Measured first: the erase-end blank check is wired on exactly one protocol family
(`eprom.cpp`'s `CMD_ERASE` arm). `flash_nor_unlock.cpp:41` has it commented out; `flash_intel.cpp`
and `eeprom_28c.cpp` never had one.

### Q1 — What replaces `erase -b`'s implementation?

| Option | Description | Selected |
|--------|-------------|----------|
| Host post-erase blank check | `erase -b` keeps its meaning via `check_eprom_blank`; mirrors 203's host-gains-before-firmware-loses shape and gains a better report. Cost: one extra port open, and work not named in FWBLANK-01…05 | ✓ |
| Remove `erase -b` entirely | Flag leaves the CLI; `firestarter blank` is the replacement. Smallest change. Cost: a documented flag disappears, REL-04 must name it | |
| Keep the flag, make it a no-op | Cheapest diff. Cost: help text claims a check that no longer runs | |
| You decide | | |

**User's choice:** Host post-erase blank check
**Notes:** Two sub-decisions taken by precedent without asking — whole-device (the firmware's was
`0 → mem_size`; erase on this family is device-global, so there is no region to scope to) and
opt-in behind `-b` (preserves today's inverted polarity, matches D-3's opt-in stance for
post-write verify).

### Q2 — Which exit-code contract?

| Option | Description | Selected |
|--------|-------------|----------|
| Adopt 0/1/2, like `write --verify` | Follows 203 D-13; refuses to reproduce the defect filed against `dev test`'s blank step where a transport failure reads as a chip verdict. Cost: a third command with two contracts | ✓ |
| Keep 0/1 unchanged | Follows 202 D-11 (no requirement covers `erase`'s exit codes). Cost: a transport failure exits 1 and reads as "the chip did not erase" | |
| You decide | | |

**User's choice:** Adopt 0/1/2, like `write --verify`

### Q3 — What does a failed check print?

| Option | Description | Selected |
|--------|-------------|----------|
| Full 202 output, and `erase` gains `--full` | Same switch `_drive_region_compare` takes and the surface `write --verify` gained in 203 D-15 | |
| Full 202 output, no `--full` flag | Always full-scan; an erase failure is rare and diagnosis is the point | |
| One terse line, like the write guard | Mirrors 203 D-10/D-11 and the standing terse-output preference (v1.40 Phase 200 UAT, `b3a777e`) | ✓ |
| You decide | | |

**User's choice:** One terse line, like the write guard
**Notes:** Recorded in CONTEXT.md that — unlike 203's guard, whose one-byte abort makes a bucket a
verdict from a short prefix — a whole-device post-erase scan *would* support a well-founded
diagnosis. Terseness was chosen over it deliberately, with `firestarter blank --full` documented
as the composition for an operator who wants the full picture.

---

## The `0x08` bit

Measured first: five host sites read or set `0x08`, including the Phase 203 guard's own bypass
test (`write_blank_guard.py:180`) and `dev test`'s masked UV slot write (`chip_test.py:3221`).

| Option | Description | Selected |
|--------|-------------|----------|
| Full retirement — requirement stands | Constant leaves `constants.py`, host stops composing `0x08`, `-b` reaches the guard as a host-side signal. Cost: `write -b` and `dev test`'s masked UV writes regress against pre-205 firmware; REL-04 documents it | ✓ |
| Keep composing the bit, amend FWBLANK-04 | Wire bit still sent so pre-205 firmware honours `-b`; follows the 203 D-02 / 204 D-03 amendment precedent. Cost: the ladders visibly diverge for a milestone | |
| Full retirement + a host firmware-version gate | Names the regression where it bites. Cost: the host cannot read a firmware prerelease suffix, and activation D-4 rules a version gate out of scope | |
| You decide | | |

**User's choice:** Full retirement — requirement stands
**Notes:** The first v1.41 requirement that measurement *confirms* rather than contradicts — worth
stating, since 203 D-02 and 204 D-03 both amended theirs. The internal plumbing mechanism was left
to the planner (explicitly, per the workflow's rule that implementation approach is not the user's
question), with two recorded hazards flagged: `build_flags`' first four parameters are passed
positionally by both production callers, and `chip_test.py:3221` passes its flag positionally too.

---

## The bench legs

### Q1 — How is criterion 3's "non-blank UV part" met?

| Option | Description | Selected |
|--------|-------------|----------|
| W27C512 proxy via `--skip-erase` | Phase 201-06's established rehearsal; exercises the exact deleted path, repeatably, without consuming a true UV part. Coverage limit stated | ✓ |
| Socket a genuinely non-erasable UV part | Highest fidelity. Cost: hand-socketed and consumed — no reset without a UV eraser | |
| Both | Proxy for repeatable legs, one real UV part for the criterion-3 observation | |
| You decide | | |

**User's choice:** W27C512 proxy via `--skip-erase`

### Q2 — What covers the erasable half and the other two files?

| Option | Description | Selected |
|--------|-------------|----------|
| Same W27C512, erase path on — 0x06/0x10 test-only | One part, two roles; both exercise `eprom.cpp`. `0x10` has zero validated chips so cannot be benched regardless | ✓ |
| Add an SST39SF020 for the 0x06 leg | Covers a second protocol family and the site the 201 note calls "one flag deep". Cost: a socket swap and a second sequence | |
| You decide | | |

**User's choice:** Same W27C512, erase path on — 0x06/0x10 test-only

### Q3 — Is the D-04 skew regression observed on silicon?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — observe it | Post-205 host + pre-205 firmware, `write -b` on the non-blank part; captures the refusal verbatim for REL-04 | ✓ (Claude) |
| No — record it as reasoned | Keeps the bench to criteria 3 and 5. Cost: REL-04 documents a behaviour nobody watched | |
| You decide | | ✓ (user) |

**User's choice:** "you decide"
**Notes:** Decided by Claude — observe it, as a rider on the criterion-3 sequence rather than a
second matrix. The part is already seated and already non-blank, the Leonardo is exempt from the
chip-out-before-sideload rule so a firmware swap needs no hands, and unlike 204's D-08 the old
artifact is a build of the current branch HEAD, not a published wheel. 204's D-08/D-09 precedent
is explicit that a claim about what a real user sees is observed, not argued — and REL-04 will
make exactly that claim.

---

## The orphans and the reserved records

### Q1 — `MSG_ERR_NOT_BLANK` (0xB0)

| Option | Description | Selected |
|--------|-------------|----------|
| Keep it, annotate it — 204's D-06 shape | Meta-only docs commit, as `694acce3` did. Keeps 205 a two-repo phase; the id costs no AVR flash | ✓ (Claude) |
| Retire it from the catalog | Three-repo lockstep; a post-205 host would print an unknown id where pre-205 firmware sends `Not blank` | |
| You decide | | ✓ (user) |

**User's choice:** "you decide"
**Notes:** Decided by Claude — keep and annotate. The measurement that settles it: 0xB0 is **not**
orphaned on the host. Its only firmware raise site dies with `mem_util_blank_check_region`, but a
post-205 host still receives it from pre-205 firmware — the exact skew the bench leg above
captures. Discussion also turned up a third orphaned debug id not previously named anywhere,
`DBG_FLAG_SKIP_BLANK` (0x2E) at `firestarter.cpp:89`, which takes the same annotation.

### Q2 — Sweep width

| Option | Description | Selected |
|--------|-------------|----------|
| Full sweep — 204's D-01 precedent | Everything reachable only from the deleted machinery, plus stale docstrings. No dead code for a bisect to land on; every byte counts toward FWBLANK-05 | ✓ (Claude) |
| Literal five symbols only | Smallest diff. Cost: `uint32_to_bytes` survives with zero callers and the flash figure understates the removal | |
| You decide | | ✓ (user) |

**User's choice:** "you decide"
**Notes:** Decided by Claude — full sweep, with a 21-row measured site list written into
CONTEXT.md. Two sites are rewrites rather than deletions and are called out as such: the
anti-regression comments at `eeprom_28c.cpp:378-383` and `flash_5v_page.cpp:69-74` both read "do
not restore the conditional because the bit looks orphaned", which becomes *wrong* once the bit
genuinely does not exist.

---

## Claude's Discretion

- Which todos to fold (user: "you decide") — see Todo folding above.
- Whether the D-04 skew regression gets a bench leg (user: "you decide") — decided yes.
- `MSG_ERR_NOT_BLANK`'s catalog disposition (user: "you decide") — decided keep and annotate.
- Sweep width (user: "you decide") — decided full sweep.
- The internal mechanism for plumbing `-b` to the Phase 203 guard once `0x08` is gone, with the
  positional-signature hazard flagged for the researcher.
- Exact wording of the two reserved-gap comments, the three catalog annotations, and the rewritten
  comments at the three stale-comment sites.
- FWBLANK-05's measurement method — not asked, settled by the v1.33 precedent, with the DEV_TOOLS
  build-config question flagged as something the figures must state.
- The bench sequence order and how the pre-205 firmware `.hex` is produced.

## Deferred Ideas

- Collapsing `erase -b`'s second port open into the erase's own session → Phase 206, SESS-01.
- A dedicated retired-command/retired-flag message instead of a bare refusal → Phase 207 (REL-04).
- The `DONE`-based clean stop → still CMP-F1; Phase 206 owns the surface.
- Retiring the four orphaned catalog ids → any later phase already paying for a codegen run;
  `MSG_ERR_NOT_BLANK` specifically cannot go until pre-`3.1.0` firmware support is dropped.
- Region-scoping the `0x06`/`0x10` write-init checks → moot, this phase deletes them; the Phase 201
  "one flag deep" finding is what makes deletion safe.
