---
phase: 152-outward-facing-close-operator-gated
plan: 09
subsystem: release-engineering
tags: [release-notes, claim-gate, firmware, platformio, gh-cli]

# Dependency graph
requires:
  - phase: 152-01
    provides: 152-CLAIM-CLASSES.md, the claim gate's contract
  - phase: 152-02
    provides: 152-check-claims.py, the gate script
  - phase: 152-03
    provides: gate fixtures / plant-and-revert proof
  - phase: 152-04
    provides: prior wave-3 artifacts (152-RELEASE-NOTES-app.md, 152-CLASS-SIZES.md)
provides:
  - 152-RELEASE-NOTES-fw.md, a frozen, gate-clean, version-agnostic firmware release draft
affects: [152-12 (version substitution), 152-18 (posting under operator checkpoint)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Version-read opening paragraph with bracketed placeholder-fill notes (FW_TAG_TBD/APP_TAG_TBD)"
    - "Two-separately-labelled-size-figures pattern for a shared linker ceiling vs a MERGE-05 growth band"
    - "Withdrawal-word-order phrasing for a deferred command name (gate class (e))"

key-files:
  created:
    - .planning/phases/152-outward-facing-close-operator-gated/152-RELEASE-NOTES-fw.md
  modified: []

key-decisions:
  - "Used the b19 measured asset byte sizes as the live figures (the only ones available pre-cut); tag is placeholdered per D-01, byte sizes are not."
  - "Named firestarter/scripts/check_erase_no_vpp.py as the hazard control per RESEARCH §B-5's mechanism correction; the roadmap-named checker is never mentioned by name in the draft."
  - "Avoided the literal string 'AT28C256' throughout, using 'this chip family'/'the 28C protocol' instead, matching the app body's register and reducing at28c256-fixed gate-pattern surface."

patterns-established:
  - "Firmware release draft asset list as one bullet per image (not one packed sentence) so the gate's '.hex count == measured asset count' acceptance criterion is checkable by grep -c (which counts matching lines, not occurrences)."

requirements-completed: [OUT-04]

coverage:
  - id: D1
    description: "152-RELEASE-NOTES-fw.md lists all four measured firmware assets with board mapping, no --board-targeting promise, and the ARM standing non-claim"
    requirement: "OUT-04"
    verification:
      - kind: other
        ref: "gh release view 3.0.0b19 --repo henols/firestarter --json assets; grep -c '\\.hex' 152-RELEASE-NOTES-fw.md == 4"
        status: pass
    human_judgment: false
  - id: D2
    description: "The two Leonardo size figures (Caterina-boundary headroom vs MERGE-05 band headroom) are measured live and kept under separate labels"
    requirement: "OUT-04"
    verification:
      - kind: other
        ref: "python3 -c over firestarter/scripts/baseline/size_baseline.json and size_baseline_base01.json; grep -n '28672\\|1042\\|+724' 152-RELEASE-NOTES-fw.md"
        status: pass
    human_judgment: false
  - id: D3
    description: "The deferred command `write --sdp-relock` is withdrawn (Backlog 999.28), named only in that order in the draft, and the draft passes the claim gate"
    requirement: "OUT-04"
    verification:
      - kind: other
        ref: "FIRESTARTER_CLAIMSCAN_TARGETS_152=<abs>/152-RELEASE-NOTES-fw.md python3 152-check-claims.py"
        status: pass
    human_judgment: false
  - id: D4
    description: "Wording review items and posting/verification invocation contract handed to Plan 152-18"
    human_judgment: true
    rationale: "The gate's own docstring states a green run is not a substitute for D-03's per-artifact blocking operator wording review; that review happens in Plan 152-18, not here."

duration: 10min
completed: 2026-08-21
status: complete
---

# Phase 152 Plan 09: Firmware Release Body (OUT-04) Summary

**Authored and froze `152-RELEASE-NOTES-fw.md`, the version-agnostic firmware release draft: four
measured `.hex` assets mapped to their boards, the two Leonardo size figures kept under separate
labels with the Caterina boundary named UNGUARDED. `write --sdp-relock` is withdrawn (Backlog
999.28), named in the draft only in that order, and all three required non-claim caveats are
present. The gate exits 0.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-08-21T15:42:06Z
- **Completed:** 2026-08-21T15:52:00Z
- **Tasks:** 3
- **Files modified:** 1 (created)

## Accomplishments

- Measured every figure the firmware body cites, live, rather than inheriting any of them from
  CONTEXT/RESEARCH/a prior record (all three had moved between 2026-08-20 and 2026-08-21).
- Authored `152-RELEASE-NOTES-fw.md` following the 146 donor's shape, with 152-specific corrections
  (workflow filename, four assets not three, the real hazard-control name, the re-measured Leonardo
  figures).
- Ran the claim gate against the draft via the env seam and iterated to a green result, catching and
  fixing four forbidden-pattern hits and one required-caveat gap along the way.
- Confirmed the firmware draft's placeholder tokens are byte-identical to the app draft's, and that
  the working tree is clean on the milestone branch after committing.

## Task Commits

1. **Task 1: Measure the published assets and both Leonardo size figures live** — no file changes
   (pure measurement; results below and folded into Task 2's commit).
2. **Task 2: Author `152-RELEASE-NOTES-fw.md` from the measured figures** — `332552fe` (docs)
3. **Task 3: Freeze the draft and hand the placeholder contract to Plan 152-12 and Plan 152-18** —
   verification-only; no further file change was needed since Task 2's commit already produced the
   frozen, gate-clean file. Confirmed via `git status --porcelain` (empty) and
   `git rev-parse --abbrev-ref HEAD` (still the milestone branch).

**Plan metadata:** (this SUMMARY's own commit, made immediately after this file is written)

## Files Created/Modified

- `.planning/phases/152-outward-facing-close-operator-gated/152-RELEASE-NOTES-fw.md` — the frozen
  OUT-04 firmware release draft.

## Task 1 — Measurements (verbatim)

**Command timestamp:** `2026-08-21T15:42:06Z`

**`gh release list --repo henols/firestarter --limit 5`:**

```
3.0.0b19	Pre-release	3.0.0b19	2026-08-18T10:00:08Z
3.0.0b18	Pre-release	3.0.0b18	2026-08-07T14:18:19Z
3.0.0b17	Pre-release	3.0.0b17	2026-08-07T11:31:22Z
3.0.0b16	Pre-release	3.0.0b16	2026-08-07T09:12:26Z
3.0.0b15	Pre-release	3.0.0b15	2026-08-02T21:22:42Z
```

Latest pre-release tag: `3.0.0b19`.

**`gh release view 3.0.0b19 --repo henols/firestarter --json assets --jq '.assets[] | {name, size}'`
— the measured asset list, count = 4 (not three, per RESEARCH §G-2):**

| Asset | Bytes |
|---|---|
| `firestarter_leonardo.hex` | 75961 |
| `firestarter_py32f071.hex` | 79047 |
| `firestarter_uno.hex` | 70120 |
| `firestarter_uno328pb.hex` | 70246 |

**AVR size figures, all three environments, from `firestarter/scripts/baseline/size_baseline.json`
(live, current tree, HEAD `d990a4c`):**

| Env | flash_used | flash_total | flash_free | ram_used | ram_total |
|---|---|---|---|---|---|
| `uno` | 25548 | 32768 | 7220 | 1575 | 2048 |
| `uno328pb` | 25598 | 32768 | 7170 | 1581 | 2048 |
| `leonardo` | **27630** | 32768 | 5138 | 2016 | 2560 |

**Same, from `firestarter/scripts/baseline/size_baseline_base01.json`:**

| Env | flash_used | flash_total |
|---|---|---|
| `uno` | 24824 | 32768 |
| `uno328pb` | 24874 | 32768 |
| `leonardo` | **26906** | 32768 |

**Leonardo delta vs `base01` (Label A — the MERGE-05 size-band headroom, NOT the boundary
headroom):** `27630 − 26906 = 724`. Exemption terms named in `size_baseline.json`'s
`meta.deltas_vs_base01.leonardo.merge05_clause` and summed: `96 (defect-fix) + 210 (page-size seam) +
288 (lock-status read) + 130 (standalone erase) = 724`. **The delta equals the allowance exactly — the
MERGE-05 size-band headroom is 0 B.**

**Bootloader-boundary arithmetic (Label B — the Caterina headroom, a DIFFERENT, UNGUARDED number,
never the same as Label A):** boundary `28672` minus measured `leonardo flash_used` `27630` =
**`1042` B**.

**`grep -n 'maximum_size' firestarter/platformio.ini`:**

```
46:board_upload.maximum_size = 32768
75:board_upload.maximum_size = 32768
95:board_upload.maximum_size = 32768
```

All three AVR envs (`uno`, `uno328pb`, `leonardo`) carry `maximum_size = 32768` — the real device
flash size, **not** a bootloader-protecting figure (Leonardo's own Caterina boundary sits at `28672`,
well below `32768`). This is what makes the boundary unguarded: the linker's upload-size ceiling no
longer refuses a build that would overwrite the bootloader region.

**Sentence stating what each Label means, kept separate as the plan requires:** Label A (0 B) is
whether this milestone's growth stayed inside the recorded band-plus-exemptions comparison; Label B
(1042 B) is the physically remaining flash before a future build would overwrite the USB bootloader
itself. Conflating them is the specific mistake `153-RECORD.md` and RESEARCH §Pitfall 6 name.

## Task 2 — Authoring and gate iteration

Authored `152-RELEASE-NOTES-fw.md` in the shape of the 146 donor with the required 152-specific
corrections (workflow file `beta-build.yml` not `beta-release.yml`; four assets not three; the real
hazard control named per RESEARCH §B-5's mechanism correction).

**Gate iterations before green:** the first draft failed on two `FORBIDDEN_PATTERNS` rows — one
matching an unqualified appearance of the completion-claim word this milestone reserves exclusively
for its own software-prefixed compound (in a sentence describing the erase hazard-control source
scan), and one matching a mention of the deferred command's name with no adjacent withdrawal
predicate (in a "What is established" bullet) — plus a required-caveat miss: the mandated AT28C
non-claim sentence had been split across a line wrap. The `.hex` count also read 3 instead of 4
because `grep -c` counts matching **lines**, not occurrences, and the asset list had been packed onto
two lines with the ARM image's filename repeated in a following sentence. Fixed by: rewording the
erase-control sentence so the source scan is described as failing on a planted violation, dropping
the reserved word entirely; rewording the "What is established" bullet to refer to "the deferred
protection command named above" instead of repeating the bare command name without its withdrawal
predicate; putting the mandated caveat sentence on its own single unwrapped line; and restructuring
the asset list into one bullet per image (one `.hex` occurrence per line, four lines total) with no
`.hex`-suffixed repeat elsewhere in the file.

**Final gate run** (`cd .planning/phases/152-outward-facing-close-operator-gated &&
FIRESTARTER_CLAIMSCAN_TARGETS_152="$(pwd)/152-RELEASE-NOTES-fw.md" python3 152-check-claims.py`):

```
PASS: scanned 152-RELEASE-NOTES-fw.md; 1 of 1 caveat-required file(s) carry every caveat their own
rule demands; 0 file(s) carry no caveat requirement (this PASS is compliance with the
forbidden-phrase table and the per-file caveat rule only ...)
```

`GATE rc=0`

**All ten acceptance-criteria greps, final values:**

| Check | Result |
|---|---|
| `sdp-relock` | 2 |
| `999.28` | 2 |
| `.hex` (lines) | 4 |
| `28672` | 1 |
| `check_erase_no_vpp` | 1 |
| `FW_TAG_TBD` | 1 |
| `APP_TAG_TBD` | 1 |
| `No AT28C part was tested at any point in v1.32` | 1 |
| `software-proven and unvalidated on silicon` | 1 |
| `unguarded` (case-insensitive) | 1 |
| `check_dispatch` | 0 |

**Every size figure in the file traced to a Task 1 reading:** `27630` (leonardo flash_used, measured),
`32768` (device flash size, measured), `28672` (Caterina boundary, cited from RESEARCH §A-9/§G-2, not
re-derived since it is a fixed hardware constant not a live-build figure), `1042` (28672−27630,
computed in-file), `724` (27630−26906, computed in-file), `96+210+288+130=724` (exemption sum,
transcribed from `size_baseline.json`'s own `meta` block), `75961`/`79047`/`70120`/`70246` (asset
sizes, measured). No figure in the draft is inherited from CONTEXT or RESEARCH prose alone.

## Task 3 — Freeze and handoff contract

**Placeholder tokens, with line and read command:**

| Token | Line | Read command (Plan 152-12) |
|---|---|---|
| `FW_TAG_TBD` | 3 | `gh release list --repo henols/firestarter --json tagName,isPrerelease --jq '[.[] \| select(.isPrerelease)][0].tagName'` |
| `APP_TAG_TBD` | 7 | `gh release list --repo henols/firestarter_app --json tagName,isPrerelease --jq '[.[] \| select(.isPrerelease)][0].tagName'` |

**Token-set identity, confirmed:** `grep -o 'APP_TAG_TBD\|FW_TAG_TBD' 152-RELEASE-NOTES-fw.md | sort -u`
and the same over `152-RELEASE-NOTES-app.md` both produce the identical two-line set
(`APP_TAG_TBD`, `FW_TAG_TBD`) — one substitution pass covers both files.

**The exact posting invocation Plan 152-18 will use:**

```
gh release edit FW_TAG_TBD --repo henols/firestarter --notes-file .planning/phases/152-outward-facing-close-operator-gated/152-RELEASE-NOTES-fw.md
```

**The exact verification invocation:**

```
gh release view FW_TAG_TBD --repo henols/firestarter --json body --jq '.body' | diff -u - .planning/phases/152-outward-facing-close-operator-gated/152-RELEASE-NOTES-fw.md
```

plus the body-length read as the 0-to-N non-vacuity guard:
`gh release view FW_TAG_TBD --repo henols/firestarter --json body --jq '.body | length'`.

**Measured current body length of the candidate release (b19, the latest pre-release as of this
plan):** `gh release view 3.0.0b19 --repo henols/firestarter --json body --jq '.body | length'` → `0`.
This matches D-02's measured fact that every firmware pre-release from b16 through b19 is bodiless, and
gives Plan 152-18's non-vacuity guard a measured starting value of `0`, not an assumed one.

**Five wording-review items for the Plan 152-18 operator checkpoint:**

1. The two size figures' separation — confirm the Caterina-boundary sentence (1042 B, UNGUARDED) and
   the MERGE-05 band sentence (0 B headroom, +724 = 96+210+288+130) read as two distinct numbers with
   two distinct meanings, not one restated.
2. The unguarded statement — confirm the reader understands *why* it is unguarded (the linker's
   `maximum_size` is now the real device flash size, not a bootloader-protecting figure) and what
   happens if a future build crosses it.
3. The asset-to-board mapping and the no-board-selection caveat — confirm each of the four assets
   names its board plainly and that `firestarter fw --install` flashing the attached board (not a
   chosen one) is stated, not implied.
4. The ARM image's standing non-claim — confirm "no PY32F071 circuit board exists… nothing in that
   port has run on any silicon" reads as a caveat on the fourth asset, not buried after it.
5. The withdrawal wording — confirm the deferred command's name is used only in the mandated order
   (name, immediately followed by its withdrawal predicate — `write --sdp-relock` is withdrawn),
   naming Backlog 999.28, and that the firmware-side consequence (no host surface reaches it; the
   protection bit cannot be read back on this family either) is stated plainly.

**Post-commit checks:**

```
git -C /workspaces status --porcelain -- .planning/phases/152-outward-facing-close-operator-gated/152-RELEASE-NOTES-fw.md
PORCELAIN-END
```
→ empty (clean).

`git -C /workspaces rev-parse --abbrev-ref HEAD` → `gsd/v1.32-at28c-write-path-root-cause-report-provenance`.

## Decisions Made

- Used the measured `3.0.0b19` asset byte sizes as the draft's live figures, since no v1.32 cut exists
  yet; only the tag itself is placeholdered, per D-01. Plan 152-12 substitutes tags after the real cut;
  if the cut's asset sizes differ, that is a fact for 152-12/152-18 to reconcile, not a defect in this
  draft's measurement discipline.
- Restructured the asset list as one bullet per image (rather than the 146 donor's single packed
  sentence) so the `.hex`-count acceptance criterion, which relies on `grep -c` counting matching
  **lines**, resolves to the correct value of 4.
- Never wrote the literal string `AT28C256` anywhere in the draft, using "this chip family" / "the 28C
  protocol" throughout — reduces exposure to the `at28c256-fixed` forbidden-pattern class and matches
  the sibling app body's register.
- Did not name `tools/check_dispatch.py` at all (not even in a "not X" contrastive clause), per the
  explicit prohibition; the real hazard control, `firestarter/scripts/check_erase_no_vpp.py`, is named
  plainly instead.

## Deviations from Plan

None — plan executed exactly as written. The four gate-iteration fixes documented above (an
unqualified appearance of the reserved completion-claim word, a mention of the deferred command's
name lacking an adjacent withdrawal predicate, a line-wrapped mandated sentence, and the
`.hex`-count miscount) were all caught and corrected within Task 2's own acceptance loop before any
commit was made; they are iteration on a single task's required verification, not after-the-fact
deviations from the plan's instructions.

## Issues Encountered

None beyond the gate-iteration items above, which were resolved before committing.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

`152-RELEASE-NOTES-fw.md` is frozen, gate-clean, and committed on the milestone branch. Plan 152-12 can
substitute both placeholder tokens in one pass once the real cut exists; Plan 152-18 has the exact
posting and verification invocations, the measured non-vacuity starting value (body length 0), and the
five wording-review items for its own operator checkpoint. No network write occurred in this plan;
nothing has been posted.

This ships software-proven and unvalidated on silicon.

## Self-Check: PASSED

- `FOUND: .planning/phases/152-outward-facing-close-operator-gated/152-RELEASE-NOTES-fw.md`
- `FOUND: 332552fe` (Task 2's commit hash, verified present in `git log --oneline --all`)

---
*Phase: 152-outward-facing-close-operator-gated*
*Completed: 2026-08-21*
