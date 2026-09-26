# Phase 144: Tests & Build Verification - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-13
**Phase:** 144-tests-build-verification
**Areas discussed:** Native test posture (TEST-01…05), Trace freeze & diff (TEST-06), Size baseline & MERGE-05 (TEST-08), Gate reach (TEST-07)

---

## Area selection

All four offered gray areas were selected.

| Option | Description | Selected |
|--------|-------------|----------|
| Native test posture (01–05) | Author new cases vs. map the 88 existing v131 cases and fill proven gaps | ✓ |
| Trace freeze & diff (06) | How the pre-change fixture survives; attribution depth for 620→265 entries | ✓ |
| Size baseline & MERGE-05 (08) | Rebaseline vs. record-only; which of three disagreeing anchors | ✓ |
| Gate reach for TEST-07 | v131 envs in no CI leg; parity fail-open in app CI; CAP-03 layout gate | ✓ |

**Notes:** 18 pending todos matched on keyword score; none folded — all behavior/infrastructure work
in a phase that adds no behavior. Recorded as reviewed-not-folded in CONTEXT.md.

---

## Native test posture (TEST-01…05)

### Q1 — What is the native-test deliverable?

| Option | Description | Selected |
|--------|-------------|----------|
| Map + attest + fill gaps | Machine-checked requirement→case mapping gate; new cases only where a gap is proven. Matches H6's split. | ✓ |
| Author a fresh consolidated suite | New cases restating TEST-01…05 one-for-one, leaving the 88 existing cases as owning-phase evidence | |
| Prose mapping table only | A table in the phase record, no new gate and no new cases | |

**User's choice:** Map + attest + fill gaps.
**Notes:** Prose-only was framed as the same shape as the hollow parity legs Phase 120 had to rebuild.

### Q2 — How should TEST-03 flip, given Phase 141's disclosed narrowness?

| Option | Description | Selected |
|--------|-------------|----------|
| Synthetic-row end-to-end oracle | Drive the real loop against a synthetic row with `overprogram_factor=3` | ✓ (later reversed) |
| Flip as-is, record the non-claim | Flip on the pure-function cases with an explicit non-claim | |
| You decide | Resolve during planning | ✓ (initial answer) |

**User's choice:** "You decide" → Claude resolved to the synthetic-row oracle, on the exact
`native_params_v131` precedent (0 of 329 shipped chips reach `pulse_delay == 0`, making the native
suite the only possible oracle for TABLE-03; `overprogram_factor == 0` on every row is identical).
**Notes:** **Reversed later in the same session** — see the follow-up below. Investigation found no
injection seam at `eprom.cpp:303` and blob pins on both `eprom.cpp` and `eprom_params.cpp`, so the
oracle's true cost was a seventh env or a golden re-derivation. Re-presented to the operator.

### Q3 — Re-run the 88 cases, or cite the owning phases' records?

| Option | Description | Selected |
|--------|-------------|----------|
| One cold consolidated run, verbatim | Re-run every v131 env at the 144 tip; catches cross-phase regressions | ✓ |
| Cite the owning phases' records | Flip on runs already recorded in 141/142's records | |

**User's choice:** One cold consolidated run.
**Notes:** No single run has ever exercised all 88 cases against the final tree.

### Follow-up — the TEST-03 seam, re-presented with measured cost

| Option | Description | Selected |
|--------|-------------|----------|
| A 7th env with a substituted params TU | `-<proms/eprom_params.cpp>` + a suite-supplied synthetic row; no pinned source moves | |
| A test-only seam in `src/`, golden re-derived | Injection point plus `protocol_branch_inventory.json` re-derivation in the same commit | |
| Drop back to flip-with-non-claim | Flip on the pure-function cases; record the untested in-loop wiring | ✓ |

**User's choice:** Drop back to flip-with-non-claim.
**Notes:** Claude flagged that this overturned its own earlier "no 7th env, settled by precedent"
call. Net effect is stronger than the original plan: Phase 144 now edits **no** firmware `src/` file,
so the D-13/D-18 golden stays green for the entire phase — something Phases 141, 142 and 143 could
not say.

---

## Trace freeze & diff (TEST-06)

### Q1 — How does the pre-change fixture survive?

| Option | Description | Selected |
|--------|-------------|----------|
| Pure rename, included by nothing | `git mv` to `_prechange.h`, content untouched; blob SHA survives the move since git blobs are path-independent | ✓ |
| Two array sets in one header | `_PRECHANGE` arrays beside the new ones; breaks the file's blob SHA | |
| Git history + the 138 record only | Overwrite in place | |

**User's choice:** Pure rename, included by nothing.
**Notes:** Include-nothing also avoids an unused-const warning, which matters because
`check_build_warnings.py`'s native watermark sits at 1166 with zero headroom.

### Q2 — Attribution granularity for 620 old vs. 265 new entries?

| Option | Description | Selected |
|--------|-------------|----------|
| Segment attribution + exhaustiveness gate | Named segments, per-segment deltas attributed to decisions, script proving all 885 entries are attributed | ✓ |
| Full positional per-entry diff | ~900-row side-by-side table | |
| Counts and narrative | Three totals plus prose | |

**User's choice:** Segment attribution + exhaustiveness gate.
**Notes:** Counts-and-narrative was framed as a blanket snapshot update wearing a paragraph — what
TEST-06 forbids.

### Q3 — Does the new fixture get the same dual-pin treatment?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, pin it the same way | Re-point the inventory at the new fixture with fresh counts and blob SHA | ✓ |
| Pin both files | Two inventory records — historical artifact plus new cadence | |
| Leave the new one unpinned | Defer to v1.32 | |

**User's choice:** Yes, pin it the same way.
**Notes:** Claude recorded the consequence rather than smoothing it — with one record, nothing
gate-asserts the renamed pre-change file; its preserved SHA is cited and hand-verifiable only. Logged
in CONTEXT.md as a named non-claim (D-08) and as a deferred idea.

---

## Size baseline & MERGE-05 (TEST-08)

**Decided by Claude before asking:** PREP-03 and `size_baseline.json` hold the *same* figures
(23954/24004/26016, byte-identity confirmed by `138-BASELINE.md` §5), so TEST-08's anchor is
unambiguous. F-142-09's "two anchors disagree" is BASE-01 (a v1.24 artifact) versus that anchor — not
an ambiguity about TEST-08's own anchor.

### Q1 — Rewrite `size_baseline.json` to the v1.31 tip?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — rewrite to the v1.31 tip | Record 24824/24874/26906; the everyday gate goes GREEN and v1.32 drift becomes detectable again | ✓ |
| No — record only, leave RED for Phase 146 | Preserve the read-only discipline through the milestone | |
| Rewrite, and freeze the old anchor beside it | Rewrite plus a named frozen pre-v1.31 file | |

**User's choice:** Yes — rewrite to the v1.31 tip.
**Notes:** A gate RED for a known accepted reason can no longer report an unknown one.

### Q2 — What happens to MERGE-05 and `size_baseline_base01.json`?

| Option | Description | Selected |
|--------|-------------|----------|
| Leave BASE-01 untouched, record unreachability | Keep v1.24's frozen evidence; record the RED and cite F-141-01 | |
| Re-anchor BASE-01 to v1.31 too | Both baselines rewritten; `--policy merge05` goes green | ✓ |
| Widen the band literal | Raise `MERGE05_UNO_CLASS_FLASH_BAND` with a recorded rationale | |

**User's choice:** Re-anchor BASE-01 to v1.31 too.
**Notes:** Claude had stated the tradeoff in the option text — that re-anchoring ends MERGE-05's
ability to make its original v1.24 comparison — and the operator selected it with that visible. Taken
as decided, not re-litigated. Two follow-ups were needed to pin down what the re-anchor *means*.

### Q3 — Refresh `size_baseline_v131.json`?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — refresh with the consolidated run | Update from the run TEST-01…05 already produces | ✓ |
| No — leave it as the Phase 138 snapshot | Treat as frozen pre-change evidence | |

**User's choice:** Yes — refresh.
**Notes:** No live gate reads this file, so refreshing it cannot turn anything RED.

### Follow-up Q1 — What is the re-anchored band measuring?

| Option | Description | Selected |
|--------|-------------|----------|
| Forward tripwire from v1.31 | Band literals kept, now measuring growth from 24824/24874/26906; v1.24 semantics retired | ✓ |
| Re-anchor only, semantics left as-is | Move the numbers, change nothing else | |
| Retire MERGE-05 outright | Delete the policy mode and BASE-01 | |

**User's choice:** Forward tripwire from v1.31.
**Notes:** Converts a permanently-dead backward gate into a live one and gives Leonardo's 1766 B of
headroom an actual guard.

### Follow-up Q2 — Preserve BASE-01's v1.24 content in-tree first?

| Option | Description | Selected |
|--------|-------------|----------|
| Git history is enough | Overwrite in place; figures recoverable at the pre-change blob and in `138-BASELINE.md` §5 | ✓ |
| Copy to a named v1.24 frozen file first | Self-documenting in-tree diff between the two eras | |

**User's choice:** Git history is enough.

---

## Gate reach (TEST-07)

### Q1 — Wire the three `*_v131` envs into CI?

| Option | Description | Selected |
|--------|-------------|----------|
| Keep local, record loudly | Run by name in the consolidated run; restate that no CI leg covers them | ✓ |
| Add to `build.yml` and `beta-build.yml` | Three new steps in both firmware workflows | |
| Add to `build.yml` only | Cover the PR gate, leave the release workflow alone | |

**User's choice:** Keep local, record loudly.
**Notes:** TEST-07's text names only `native`; CI wiring is v1.32 infrastructure. Deferred, not lost.

### Q2 — What satisfies "dual-repo constants parity holds" when app CI skips it?

| Option | Description | Selected |
|--------|-------------|----------|
| Local run both directions, recorded | Present-sibling PASS plus a subprocess run with `FIRESTARTER_FW_ROOT` at an empty dir | ✓ |
| Check out the firmware repo in app CI | Genuinely closes the fail-open | |
| Make the CI skip fail closed | Hard-fail on an absent checkout | |

**User's choice:** Local run both directions, recorded.
**Notes:** Both rejected options collide with an unanswered question — which firmware ref app CI
should pin, given `beta` and the v1.31 branch disagree today. Deferred with that blocker named.

### Q3 — Build H2's CAP-03 byte-layout parity gate here?

| Option | Description | Selected |
|--------|-------------|----------|
| Build it | Assert the firmware pack order against the host decode offsets, incl. the computed `ver_end` | ✓ |
| Defer to backlog | Record F-143-07 and let v1.32 build it | |
| You decide | Resolve during planning | |

**User's choice:** Build it.
**Notes:** F-143-07 names TEST-07 as its owner, and BF-1 — a two-repo protocol with nothing comparing
the sides — went unnoticed for three milestones and refused every connection this milestone.

---

## Claude's Discretion

Items resolved by Claude rather than asked, each recorded inline in CONTEXT.md:

- **D-03's non-claim wording** — the operator chose flip-with-non-claim; how it is phrased is Claude's.
- **D-09, the authoritative anchor** — decided from byte-identity evidence, not asked.
- **D-14, the mandatory re-anchor disclosure** — decided from the milestone's own standards: a green
  `--policy merge05` must be reported as *green because the anchor moved*, never as *green because
  growth stayed inside the band*.
- **D-04's "no `src/` edit" invariant** — a consequence of D-03, recorded so no plan drifts into one.
- **No 7th env** — originally offered as settled by the Phase 142 precedent; the TEST-03 investigation
  overturned the reasoning, and D-03's reversal made the question moot.
- **Gate homes** — D-01's mapping gate in `firestarter/tests/` (it scans firmware test sources);
  D-17's layout gate in `firestarter_app/tests/` behind `requires_fw`/`fw_path` (where every existing
  parity gate lives).
- **D-19/D-20 mechanics** — dual-repo `commits_land_in:` declarations, and committing before running
  either suite because of the whole-repo porcelain coupling (F-141-11 / F-143-02 / F-143-03).
- **D-07's segment taxonomy**, **D-01's parse strategy**, plan decomposition and the phase record's
  name — left open for research and planning.

## Deferred Ideas

- Wiring the three `*_v131` envs into `build.yml` / `beta-build.yml` (F-140-11) — v1.32.
- A firmware checkout in `firestarter_app`'s CI so parity runs for real — blocked on deciding which
  firmware ref to pin.
- An end-to-end synthetic-row overprogram oracle — revisit only if a row ever ships a non-zero
  `overprogram_factor`.
- Fixing the unscoped whole-repo porcelain assertions (F-141-11 / F-143-02 / F-143-03) — still
  unassigned; D-20 works around them.
- Gate-asserting `eprom_v131_expected_prechange.h` via a second inventory record.
