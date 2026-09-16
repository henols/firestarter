# Cell A1 — write/read/judge narrative, one section per position

## Position 1 — `A1__control__w27c512`

- **Image:** `gen_addr_image.py --stamp-width 16 65536 16` -> `reads/A1__control__w27c512/written.bin`,
  65536 B, sha256 `8ee568689ae9ab14ac5e34179542fecbe44373c7ef8b4400a1b6f3e3f0d563a4`, matches
  `IMAGE-PLAN.json`'s row for this position by runtime lookup.
- **Write:** `control` arm, `firestarter -p /dev/ttyACM1 write w27c512 written.bin`, under
  `timeout --signal=INT 165` (the W27C512 ceiling — 4x the measured healthy 41.010 s from
  `BRINGUP-wrv`). Wrapper exit code **0** — the ceiling did **not** fire.
  - **Wall-clock (judged measure):** **41.305 s**
  - **App-reported (unjudged datum):** **37.48 s** (`Write to W27C512 successful (37.48s).`,
    grepped by string, not line number)
- **Read:** control arm, single read (normal case, no v133 disagreement to escalate against yet):
  `firestarter -p /dev/ttyACM1 read w27c512 run_01.bin`, exit code **0** (`--app-verdict`).
  App-reported read duration: 14.48 s (informational only; not the judged quantity).
- **Judge:** `judge_wrv.py --expect-size 65536 --app-verdict 0` ->
  `sha_verdict_judged=match`, `read_count=1`, `distinct_read_shas=1`, `size_violations=[]`,
  `app_verdict_unjudged=0`, `verdict_disagreement=false`.
- **Blank state:** not measured — the W27C512's pre-write blank check runs internally inside the
  write path (never skipped; no forbidden flag used); no standalone blank observation was taken
  for this position (the standalone `blank` command is reserved for the W29C020 smoke check,
  D-09, Task 7).
- **Outcome:** `validated`. Appended to `EVIDENCE.jsonl`, `render_evidence.py --check` green.
- No re-seat was needed.

## Position 2 — `A1__control__w29c020` — the milestone's first 262144 B write/read on silicon

- **D-09 smoke check** (outside the `P-01`..`P-11` step list; full detail in `SMOKE-W29C020.md`):
  `id w29c020` exit 0 (chip-id matched); standalone `blank w29c020` exit 1, `Not blank, at
  0x000000, v: 0x00` — a valid, expected addressability proof, **not** a failure. No forbidden
  flag used.
- **Image:** `gen_addr_image.py --stamp-width 32 262144 17` -> `reads/A1__control__w29c020/written.bin`,
  262144 B, sha256 `46e0fe13b11c46d3a86039c6812ddf6a809746ab33c945104e6753d0eb877dfb`, matches
  `IMAGE-PLAN.json`'s row by runtime lookup.
- **Write:** `control` arm, under `timeout --signal=INT 600` — **the 600 s absolute fallback,
  named as a fallback, not a derivation**, because this position is the one that creates the
  derived figure. Wrapper exit code **0** — did not fire.
  - **Wall-clock (judged measure):** **97.937 s**
  - **App-reported (unjudged datum):** **94.47 s** (`Write to W29C020 successful (94.47s).`)
  - **Derived D-08 W29C020 ceiling for every later W29C020 position: 4x97.937 = 391.748 s.**
    This number is carried into Task 11 (position 4, v133 x w29c020) and into plans 161-04
    (A2) and 161-05 (A3/B2) via this plan's SUMMARY.
- **First 262144 B read wall-clock:** **73.344 s** (app-reported 69.86 s). This is the read-set
  budget baseline A2/A3-B2 inherit — **a baseline to compare against, not a portable constant**:
  the Uno moves 512 B chunks per transfer where the Leonardo moves 1024 B.
- **Read:** control arm, single read: `firestarter -p /dev/ttyACM1 read w29c020 run_01.bin`,
  exit code **0** (`--app-verdict`).
- **Judge:** `judge_wrv.py --expect-size 262144 --app-verdict 0` -> `sha_verdict_judged=match`,
  `read_count=1`, `distinct_read_shas=1`, `size_violations=[]`, `app_verdict_unjudged=0`,
  `verdict_disagreement=false`.
- **Blank state:** not blank at `0x000000`, `v: 0x00` (D-09's standalone `blank` check) — the
  only blank observation the whole milestone will have for W29C020; since Phase 153,
  `-b`/`--no-blank-check` is unread on algorithm `0x05`, so the write itself performs no
  pre-write blank check on this part at all.
- **Outcome:** `validated`. Appended to `EVIDENCE.jsonl`, `render_evidence.py --check` green.
- No re-seat was needed.

## Position 3 — `A1__v133__w27c512` — v1.33 arm, three-read consistency set

- **Image:** `gen_addr_image.py --stamp-width 16 65536 18` -> `reads/A1__v133__w27c512/written.bin`,
  65536 B, sha256 `49476bbd2250ddb0b8d7ad5a44672151b5c7cf1571d4df9906722792ed9e123f`, mask **18**
  (distinct from position 1's mask 16 — D-12), matches `IMAGE-PLAN.json` by runtime lookup.
- **Write:** `v133` arm, under the 165 s W27C512 ceiling. Wrapper exit code **0** — did not fire.
  - **Wall-clock (judged measure):** **41.037 s**
  - **App-reported (unjudged datum):** **37.48 s**
- **Read set:** v1.33 arm, three independent reads via `dev consistency-check w27c512 --runs 3
  --output-dir ... --keep-files`, exit code **0**. Whole-invocation wall-clock **53.571 s**
  (app's own per-run elapsed 17.62 s x3), compared against `BRINGUP-wrv`'s 53.437 s baseline for
  the same chip/board class — consistent, not a regression.
- **Judge:** `judge_wrv.py --expect-size 65536 --app-verdict 0` -> `sha_verdict_judged=match`,
  `read_count=3`, `distinct_read_shas=1`, `size_violations=[]`, `app_verdict_unjudged=0`,
  `verdict_disagreement=false`. **No disagreement** — all three reads agreed with each other and
  with the written image on the first attempt. No retroactive three-run escalation is owed to
  the control arm's matching position (`A1__control__w27c512`).
- **Blank state:** not measured — same reasoning as position 1 (blank check runs internally
  inside the write path, no standalone observation taken here).
- **Outcome:** `validated`. Appended to `EVIDENCE.jsonl`, `render_evidence.py --check` green.
- No re-seat was needed.

## Position 4 — `A1__v133__w29c020` — v1.33 arm, three-read consistency set (cell's last)

- **Image:** `gen_addr_image.py --stamp-width 32 262144 19` -> `reads/A1__v133__w29c020/written.bin`,
  262144 B, sha256 `cc638893cf2760f79d5175e7ef4d93a00f5e75f803d7b0cc7e88b957ea88c452`, mask **19**,
  matches `IMAGE-PLAN.json` by runtime lookup.
- **Write:** `v133` arm, under the **DERIVED 391.748 s ceiling** (4x position 2's control-arm
  measured wall-clock, **not** the 600 s absolute fallback — that fallback was used only for
  position 2, the position that created this derivation). Wrapper exit code **0** — did not fire.
  - **Wall-clock (judged measure):** **97.916 s**
  - **App-reported (unjudged datum):** **94.48 s**
- **Read set:** v1.33 arm, three independent reads via `dev consistency-check w29c020 --runs 3
  --output-dir ... --keep-files`, exit code **0**. Whole-invocation wall-clock **219.390 s**
  (app's own per-run elapsed 73.01 s x3) — the v133-side half of the 262144 B read comparison
  against position 2's control-arm single-read baseline (73.344 s); each individual v133 read
  (73.01 s) closely matches the control single read (73.344 s).
- **Judge:** `judge_wrv.py --expect-size 262144 --app-verdict 0` -> `sha_verdict_judged=match`,
  `read_count=3`, `distinct_read_shas=1`, `size_violations=[]`, `app_verdict_unjudged=0`,
  `verdict_disagreement=false`. No disagreement.
- **Blank state:** not blank at `0x000000` per D-09's control-arm-only standalone check (not
  re-run here, per positional symmetry).
- **Outcome:** `validated`. Appended to `EVIDENCE.jsonl`, `render_evidence.py --check` green.
- No re-seat was needed.

## Summary: the two A/B pairs (all four measured, single write per position — a data point, not a
spread; NOT directly comparable to v1.31's 0.37 s figure, which is a three-cycle app-reported
spread, not a wall-clock duration — see `PROCEDURE.md`'s "Write-duration definition" section)

| Chip | Arm | Wall-clock write (s) | App-reported write (s) | Ceiling in force | Fired? |
|---|---|---|---|---|---|
| W27C512 | control | 41.305 | 37.48 | 165 s | No |
| W27C512 | v133 | 41.037 | 37.48 | 165 s | No |
| W29C020 | control | **97.937** | 94.47 | 600 s (absolute fallback) | No |
| W29C020 | v133 | 97.916 | 94.48 | **391.748 s (derived, 4x control)** | No |

W27C512 pair: control and v133 wall-clocks agree to within 0.3 s (41.305 vs 41.037), app-reported
figures identical (37.48 s both). W29C020 pair: control and v133 wall-clocks agree to within
0.02 s (97.937 vs 97.916), app-reported figures agree to within 0.01 s (94.47 vs 94.48). No A/B
divergence observed on A1 for either chip.

**262144 B read wall-clock comparison:** control single read 73.344 s; v133 per-run elapsed
73.01 s (x3, whole three-run invocation 219.390 s). The two arms' individual read durations agree
closely — this is a baseline for A2/A3-B2 to compare against, not a portable constant (the Uno
moves 512 B chunks per transfer where the Leonardo moves 1024 B).
