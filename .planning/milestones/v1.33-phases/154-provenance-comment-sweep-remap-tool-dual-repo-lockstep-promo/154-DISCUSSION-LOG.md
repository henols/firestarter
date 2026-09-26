# Phase 154: Provenance Comment Sweep + Remap Tool (dual-repo lockstep) — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `154-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-08-23
**Phase:** 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep
**Areas discussed:** all four presented areas, decided by Claude at the operator's direction

---

## How this session ran

Four gray areas were presented for selection. The operator declined the selection
and delegated:

> *"if you what to discuss something that you can decide you can ask othervice i
> have full confidence that you know the right path forward"*

Consistent with the standing preference *decide mechanical gray areas, do not
ask* — if a precedent or a measurement settles it, decide it. All four areas were
then decided from evidence gathered this session, and **no question was put back
to the operator**, because none of the four turned out to need a preference: each
resolved against a measurement or an existing project precedent.

The areas as presented, and where each landed:

| Area presented | Resolved as |
|---|---|
| Triage rule — what "load-bearing" means | D-01, D-02, D-03 |
| Test-file scope — 331 of 636 hits | D-04 |
| Remap tool — where it lives, how it's proven | D-09 |
| Manifest scope + un-round-trippable subset | D-07, D-08 |

Three further decisions were required that were **not** in the presented set,
because the evidence for them only appeared while resolving the four:

| Additional area | Resolved as |
|---|---|
| Gate classification — the real inventory | D-05, D-06 |
| Split vs the roadmap's sweep-last fallback | D-10 (split kept) |
| Commit granularity and preconditions | D-11, D-12 |

---

## Triage rule

| Option | Description | Selected |
|---|---|---|
| Apply the writeup's three-way classification per hit | Bookkeeping → delete, tombstone → delete, rationale → condense | |
| Keep-list first | Enumerate the keep-set up front, delete everything else by default | |
| Delete-by-default with an operator-reviewed exception list | Operator signs off the exception list before the sweep runs | |
| **One mechanical procedure: strip the token, then judge the remainder** | Three outcomes fall out of one rule; no up-front classification needed | ✓ |

**Basis:** reading all 130 shipped-firmware hits showed the dominant operation is
not "delete vs keep" but "strip the label, keep the sentence that follows". The
three-way classification is an *output* of that, not an input. The procedure was
checked against all five keep-examples the writeup names and reproduces "keep,
reflowed" on all five, so it needs no exception list.

**Rejected — keep-list first:** would require reading all 636 hits before the
first edit, and produces a list that is itself unreviewable.
**Rejected — operator-reviewed exception list:** the operator explicitly delegated
this; a rule that routes back to them for 636 decisions defeats the delegation.

---

## Requirement/decision IDs — provenance or traceability?

| Option | Description | Selected |
|---|---|---|
| Strip everywhere | IDs resolve only against `.planning/`, which is the coupling being removed | |
| Keep everywhere | IDs are GSD traceability, not provenance | |
| **Strip in shipped source, retain in test files** | The ID is dead weight in shipped source and a traceability key in a test | ✓ |

**Basis:** in shipped source an ID like `LOCK-02` resolves only against
`.planning/`. In a test file `Case 30 / ERASE-01` *is* the link REQUIREMENTS.md
traceability runs on, and no gate would notice it being severed.

**Notes:** the asymmetry has to be stated in the plan (SWEEP-03) so a later reader
does not read it as an inconsistency and "fix" it.

---

## `CAP-0N`

| Option | Description | Selected |
|---|---|---|
| Strip as provenance | It is on the survey regex's alternation list | |
| **Exempt as live cross-repo protocol vocabulary** | It names a wire capability generation in both repos' shipped source | ✓ |

**Basis:** `CAP-0N` appears in shipped *host* source (`serial_comm.py:67-156`,
`hardware.py:39,153`, `firmware.py:180`) and in 13 host test modules. Separately,
`test_cap03_ack_layout_parity.py:100-102` pins a comment from
`firestarter/src/firestarter.cpp` **verbatim in raw text**. Two independent lines
of evidence for the same conclusion.

**Notes:** generalised into an exemption test — a token present in *both* repos'
shipped source is vocabulary, not provenance. This also produced the phase's one
no-touch region (`src/firestarter.cpp:177-195`).

---

## Test-file scope

| Option | Description | Selected |
|---|---|---|
| Out of scope entirely | Defer all 331 test-file hits to a later phase | |
| Same treatment as shipped source | One rule, uniformly applied | |
| **Narrow treatment: tombstones and label-only comments only** | Delete the worthless, leave substantive test commentary alone | ✓ |

**Basis:** the measured split — 331 of 636 hits (52%) are in test files, against
the writeup's framing of the corpus as "shipped source". Decisive factor: **no
oracle covers any of the 331.** The byte-identical `uno` build does not include
native tests, and the host repo has no size oracle at all. Reflowing substantive
test commentary would be unverified work.

**Rejected — out of scope entirely:** tombstones and label-only comments in tests
are pure noise and free to remove; excluding them leaves the debt half-paid for no
gain.
**Rejected — uniform treatment:** would apply the highest-risk operation
(reflowing) exactly where there is no safety net.

---

## Remap tool location

| Option | Description | Selected |
|---|---|---|
| `firestarter_app/tools/` | Has pytest, mypy, ruff already wired | |
| Inside the phase directory | Matches the `check-claims.py` phase-gate precedent | |
| **`.planning/v1.33/tools/` with a sibling unit test** | Matches `.planning/v1.16/ledger/tools/` — milestone-scoped tool + its own test | ✓ |

**Basis:** the tool is consumed by Phase 159, so a phase-scoped home is wrong. 36
Python scripts already live under `.planning/`, and `v1.16/ledger/tools/` is the
exact precedent for a milestone-scoped tool with a sibling `test_*.py`.

**Rejected — `firestarter_app/tools/`:** couples a meta-repo tool to the app's
mypy watermark and to `test_flash_path_record_sync`'s porcelain assertion. Note
the packaging objection is *not* the reason — `pyproject.toml:94` is
`packages = ["firestarter"]`, so `tools/` does not ship either way.

**Notes:** carried a constraint in from precedent — the tool takes the repo root
as an explicit argument and never derives it from `_HERE`, because
`check_permitted_claims.py` fails open exactly that way.

---

## Manifest scope

| Option | Description | Selected |
|---|---|---|
| The 6,939 predicted to shift | Smallest sufficient set | |
| All 12,753 `.planning/` citations | Maximal | |
| **The 10,054 that target a swept file** | Lets Phase 159 prove the non-shifting 3,115 did not move | ✓ |

**Basis:** 6,939 is a *pre-sweep prediction* ("at or below the file's first GSD
comment"). Recording 10,054 turns Phase 159's oracle from "assume the rest didn't
move" into "prove it", for ~45% more rows in a generated file.

**Notes:** JSONL, both range endpoints and both source texts per record, at
`.planning/v1.33/sweep-citation-manifest.jsonl`.

---

## Citations pointing at a deleted comment line

| Option | Description | Selected |
|---|---|---|
| Drop them | They cannot round-trip by construction | |
| Leave them stale | Phase 159 handles it | |
| **Record as `retarget: true`, hand-pick the new target, preserve the original text** | Phase 159's oracle skips them by name instead of failing open | ✓ |

**Basis:** the writeup already calls this the only manual work in the repair. The
addition here is the mechanism — a named record type, so the oracle skips a known
set explicitly rather than silently tolerating mismatches.

**Notes:** the subset's size is unknown until the diff exists. Recorded as a
deliverable (SWEEP-10 reports the count), not as an estimate.

---

## Split (D-01) vs the roadmap's sweep-last fallback

| Option | Description | Selected |
|---|---|---|
| Take the fallback — run 155–158 first, sweep last | One sweep, one remap, atomic, no staleness window, no ruling bend | |
| **Keep the split** | Sweep first, build the tool, Phase 159 applies it once over the composite diff | ✓ |

**Basis:** the roadmap explicitly parks this decision at this discuss step, so it
was live. Kept the split: the measured justification stands (723 citations
remapped twice, 41% of that from four added `#include` lines), REMAP-04's
close-blocking marker makes the staleness window structural rather than a
promise, and one composite mapping avoids the range-shrinking hazard that
composing four successive mappings creates.

---

## Findings that changed the phase's shape

Two things surfaced during scouting that were not in the writeup and are not
preferences — they are facts that reshape the work:

1. **The gate surface is 8 paths, not "~20 files".**
   `firestarter_app/tests/scan_paths.py::ALL_CROSS_REPO_PATHS` is a committed,
   self-asserting inventory. 21 test modules import it, but they resolve the same
   8 firmware paths. Two of the 8 are generated headers, one is markdown outside
   the sweep's globs, so **five** paths are actually in scope.

2. **`test_sdp_table_parity.py` is the one dangerous gate, and a live collision
   already exists.** It does no comment stripping and ships no planted-violation
   fixture. `firestarter/src/proms/eeprom_28c.cpp:199-201` already contains three
   `_PAIR_RE`-shaped `{0x…, 0x…}` pairs *inside a comment* — currently outside the
   sliced initializer, so invisible today. And the slice itself
   (`source_text.index("{", match.end())` then a raw brace depth count) is
   comment-blind, so a `{` or `}` in a reflowed comment between a declaration and
   its initializer mis-anchors it silently. This is the writeup's Hazard 1
   predicted in the abstract, found concretely.

Both were verified by reading the gate source, not inferred.

---

## Preconditions surfaced (not decisions)

- **The `firestarter` working tree is dirty** — 11 modified files on
  `size-reduction-survey`, byte-for-byte equal to
  `.planning/notes/firmware-size-reduction-measured.patch` (verified via
  `git apply --stat`: 229 insertions / 231 deletions both ways). They are the same
  files Phase 154 sweeps. The byte-identical `uno` oracle needs a clean tree. The
  patch is the committed recovery record, so resetting is safe — **but that is an
  operator action at execution time, not an assumption the planner may make.**
- **No `gsd/v1.33-*` branch exists in either sub-repo.** `firestarter` is on
  `size-reduction-survey` (0 ahead / 0 behind `beta`); `firestarter_app` is on
  `beta`.

---

## Claude's Discretion

The whole gray-area set, by explicit delegation. Every decision was made against
a measurement taken this session or an existing project precedent rather than a
preference, and each carries that evidence inline in CONTEXT.md. Two items remain
genuinely unknown until the diff exists and are recorded as **deliverables**
rather than decisions: D-08's retarget count, and the per-file keep/delete ratio.

## Deferred Ideas

- **Phase 157 flag (real, and currently uncovered):**
  `test_json_key_parity.py:113`'s `_KEY_PARSERS_TABLE_RE` matches
  `key_parsers[] PROGMEM = {…}` — and **DECODE-01 deletes that table.** Phase 157
  has no success criterion covering this gate. Suggest a DECODE-08 at
  `/gsd-discuss-phase 157`. Out of scope here: it is a code change, not a comment
  change.
- **A global citation gate.** None exists today. SWEEP-11's tool is close to one
  but is deliberately a remapper, not a checker. Promoting it is its own phase.
- **A lint against recurrence.** A hook rejecting new `Phase N`-stamped comments
  in shipped source is the obvious follow-on. This phase removes the debt; it does
  not install the brake.
