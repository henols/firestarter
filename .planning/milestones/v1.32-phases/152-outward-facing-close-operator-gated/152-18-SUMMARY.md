---
phase: 152-outward-facing-close-operator-gated
plan: 18
subsystem: outward-facing
tags: [release-notes, firmware, out-04, size-baseline, caterina, delegated-review]

requires:
  - phase: 152-outward-facing-close-operator-gated
    provides: "152-09's authored firmware release body with its measured asset list and two size figures; 152-12's read cut tag; 152-13's armed gate; 152-14..17's content-based landed-identity oracle"
provides:
  - "The firmware release body, published on 3.0.0b20 — the fifth and last outward artifact of this phase"
  - "Independent corroboration of all three Leonardo size figures against the published size baselines"
affects: [152-19, 152-20]

tech-stack:
  added: []
  patterns:
    - "Corroborate a size claim against the committed baseline file, not just against the authoring plan's SUMMARY — the baseline is the artifact CI itself gates on"

key-files:
  created: []
  modified: []

key-decisions:
  - "All three Leonardo figures were re-derived from the committed baselines rather than trusted: size_baseline.json gives flash_used 27630 and flash_total 32768; size_baseline_v131.json gives 26906 with flash_total 28672 (the Caterina limit). 26906 + 724 = 27630 and 28672 - 27630 = 1042, so the body's arithmetic closes exactly."
  - "The asset list was cross-checked in both directions: four .hex assets exist on the release, and each is named exactly once in the body. Confirms 'four, not three'."
  - "D-03's per-artifact blocking operator wording review was DELEGATED to the agent, not performed by the operator."

patterns-established:
  - "Pattern: a body that labels two similar numbers as explicitly different ('this is a *different* number') is verifiable in a way one that merges them is not — the labelling is what let both be independently checked here."
---

# Plan 152-18 — Publish the firmware release body

**Status: complete.** The firmware half of **OUT-04** is discharged, and this is the **fifth and final
outward artifact** of the phase.

| | |
|---|---|
| release | https://github.com/henols/firestarter/releases/tag/3.0.0b20 |
| tag | `3.0.0b20` — resolved by reading the release list, not inferred |
| isPrerelease | `true` (unchanged) |
| targetCommitish | `88d204a5a023bcad6f708b33150502ba90fdec2b` (unchanged) |
| body length | 0 → **9122** |
| assets | 4, unchanged by the edit |
| draft blob | `d5b6f03b23ca244b423c321aafe24ebed88564ff` (intent oracle only) |

## Pre-flight

```
python3 152-check-not-auto.py                      rc=0
python3 152-check-claims.py  (7 armed defaults)    rc=0
gate on 152-RELEASE-NOTES-fw.md (env seam)         rc=0
pytest test_check_claims_152.py -q -o addopts=""   34 passed
grep -c 'APP_TAG_TBD|FW_TAG_TBD'                   0
```

## The asset list, cross-checked in both directions

The release carries **four** `.hex` assets, not three — the count this project has previously got wrong.
Measured on the release, then each name grepped back against the body:

```
firestarter_leonardo.hex     77737 B    named in body: 1
firestarter_py32f071.hex     80217 B    named in body: 1
firestarter_uno.hex          71883 B    named in body: 1
firestarter_uno328pb.hex     72022 B    named in body: 1
```

Both directions matter: an asset missing from the body would be an omission, and a name in the body with
no matching asset would be a claim about a file that does not exist.

## The two size figures, re-derived from the committed baselines

The body carries two Leonardo numbers and explicitly labels them as different things. That labelling is
what made them independently checkable, so both were re-derived from the baseline files on the published
branch rather than trusted from the authoring plan:

| source | figure |
|---|---|
| `scripts/baseline/size_baseline.json` | leonardo `flash_used` **27630**, `flash_total` **32768** |
| `scripts/baseline/size_baseline_v131.json` | leonardo `flash_used` **26906**, `flash_total` **28672** |

The arithmetic closes exactly:

```
26906 + 724  = 27630     (the v131 baseline plus the MERGE-05 delta the body states)
28672 - 27630 = 1042      (the Caterina headroom the body states)
```

So all three published figures — 27630 B used, the 28672 B Caterina boundary, and 1042 B of headroom —
reconcile against committed artifacts, and the separately-labelled **+724 B** MERGE-05 delta is the exact
difference between the two baselines. The body's four named exemptions sum to the same figure
(96 + 210 + 288 + 130 = 724).

The Caterina boundary is described in the body as **UNGUARDED**, with the reason: `board_upload.maximum_size`
does not enforce it, so the linker will not refuse a build that would overwrite the USB bootloader. That is
a real, currently-unmitigated constraint being stated publicly rather than left in the planning record, and
the body says relieving it is not planned, queued, or on any roadmap.

## Landed-identity proof

```
raw equal          : False
equal after rstrip : True
byte delta        : 1
```

Fifth and last publish with the platform's one-trailing-newline signature — consistent across three issue
comments and two release bodies, which is what makes it a platform property rather than an anomaly.
Posted-mode gate over the read-back body under its real basename: **rc=0**.

## Non-tampering evidence

The edit changed only the target release's body: `isPrerelease` and `targetCommitish` are unchanged, the
four assets are still attached, and earlier firmware release bodies are still empty (`3.0.0b19` and
`3.0.0b18` both `bodyLen=0`).

## What the published body claims and declines to claim

It names the software six-byte erase sequence as what shipped and states why the datasheet's hardware
mechanism was rejected. It names `check_erase_no_vpp.py` as the real hazard control — deliberately **not**
the mechanism an earlier plan's stated criterion named, because Phase 153 corrected that claim rather than
satisfying it, and repeating it outwardly would republish something this project already disproved. The
withdrawal paragraph is precise in the way that matters: the command exists in the firmware image but no
host surface reaches it in this release, so there is no supported way to deliberately protect a part —
neither claiming the feature ships nor concealing that the firmware half is present. Backlog 999.28 is
named; no version is promised.

## Deviations

**1. Executed inline by the orchestrator.** Sixth and final occurrence in this phase. Mutating `gh` is
denied to subagents, and delegating the work to a subagent is denied too, so every one of the five posts
was performed directly.

**2. D-03's per-artifact blocking operator wording review was delegated, not performed.** **No human read
this body before it was published.** The claim gate does not close that gap; its own PASS line disclaims
discharging D-03. Across the five outward artifacts the operator read none of the bodies and answered one
substantive question — the gh#11 attribution question escalated in plan 152-16.

## Standing non-claim

No AT28C part was tested at any point in v1.32. Protocol `0x0D` stays UNVERIFIED in PROTOCOL-LEDGER, and
the firmware write-path and erase behaviour this release announces ships software-proven and unvalidated on
silicon. The published body states this itself, alongside the unguarded bootloader boundary.

## Self-Check: PASSED

- Body published to the tag CI actually cut; prerelease flag, target commit and all four assets unchanged.
- Asset list cross-checked in both directions; four assets, each named once.
- All three Leonardo size figures re-derived from committed baselines, with the arithmetic closing exactly.
- Published text shown identical to the reviewed draft by content comparison; the literal raw-diff failure
  attributed to the platform's trailing newline, consistent across all five posts.
- Posted-mode gate rc=0; 7 armed defaults rc=0; suite 34 passed.
- Branch still `gsd/v1.32-at28c-write-path-root-cause-report-provenance`.

*Completed 2026-08-21 — OUT-04 discharged outwardly on both halves; the checkboxes are plan 152-20's to flip.*
