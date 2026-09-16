# Cell A3/B2 — write/read/judge narrative, one section per position

## Position 1 — `A3-B2__control__w27c512`

- **Image:** `gen_addr_image.py --stamp-width 16 65536 24` -> `reads/A3-B2__control__w27c512/written.bin`,
  65536 B, sha256 `a094e902a30b4fa3369ee493338351e11a8b6667f7539460b63f78dce896ae43`, matches
  `IMAGE-PLAN.json`'s row for this position by runtime lookup (mask 24, stamp 16).
- **Write:** `control` arm, `firestarter -p /dev/ttyACM0 write w27c512 written.bin`, under
  `timeout --signal=INT 165` (the W27C512 ceiling). Wrapper exit code **0** — the ceiling did
  **not** fire (log `11_write_control_w27c512.std{out,err}.log`).
  - **Wall-clock (judged measure):** **37.172 s**
  - **App-reported (unjudged datum):** **33.37 s** (`Write to W27C512 successful (33.37s).`,
    grepped by string — `grep -o "Write to W27C512 successful ([0-9.]*s)"` — never by line
    number: the identical success string sits at `eprom_operations.py:2045` on the control arm
    and `:1934` on v133, an arm-dependent line offset).
  - **Cross-board reference:** A1's control-arm W27C512 figure (Uno, `161-03-SUMMARY.md`) was
    **41.305 s wall / 37.48 s app**. This cell's figures (37.172 s / 33.37 s) are close to but
    somewhat below A1's — consistent with, not proof of, the **Leonardo moving 1024-byte chunks
    where the Uno moves 512** (a comparison note, not a portable per-byte budget; the board
    identity, not the firmware, is the variable named here).
- **Read:** control arm, single read (normal case, no v133 disagreement to escalate against yet):
  `firestarter -p /dev/ttyACM0 read w27c512 run_01.bin`, exit code **0** (`--app-verdict`), log
  `12_read_control_w27c512.std{out,err}.log`. App-reported read duration: 7.40 s (informational
  only, not the judged quantity).
- **Judge:** `judge_wrv.py --expect-size 65536 --app-verdict 0` ->
  `sha_verdict_judged=match`, `read_count=1`, `distinct_read_shas=1`, `size_violations=[]`,
  `app_verdict_unjudged=0`, `verdict_disagreement=false`.
- **Blank state:** not measured — the W27C512's pre-write blank check runs internally inside the
  write path (never skipped; no forbidden flag used); no standalone blank observation was taken
  for this position.
- **Real VPP context for this write (P-06):** firmware-reported 12.3 V, operator meter 11.44 V —
  in band (guard window [11.4, 12.5] V, `eprom.cpp:713`/`:736`), the best achievable real rail on
  this shield. Full ratiometric-ADC finding in `POT.md`.
- **Chip-condition context:** this is the W27C512's ninth handling; the caveat carried from A1/A2
  was closed at `P-05` by operator inspection ("nothing looks of[f]") — not a measurement-based
  clearance. No `0x303`-class fault occurred on this write; no re-seat was needed.
- **Outcome:** `validated`. Appended to `EVIDENCE.jsonl` as position 9 of 12,
  `render_evidence.py --check` green.

## Position 2 — `A3-B2__control__w29c020`

- **No D-09 smoke check.** That was a one-time, A1-control-only addressability datum, outside the
  `P-01`..`P-11` step list; repeating it here would break positional symmetry across the twelve
  sweep positions (A2 correctly skipped it too).
- **Image:** `gen_addr_image.py --stamp-width 32 262144 25` -> `reads/A3-B2__control__w29c020/written.bin`,
  262144 B, sha256 `01bab1275e83430c4a33e77c04c369e086dc57857ed003d35a207023a1b60dd0`, matches
  `IMAGE-PLAN.json`'s row (mask 25, stamp 32).
- **Write:** `control` arm, `firestarter -p /dev/ttyACM0 write w29c020 written.bin`, under
  `timeout --signal=INT 391.748` — the **DERIVED** ceiling (4x A1's measured control-arm W29C020
  wall-clock, 97.937 s, from `161-03-SUMMARY.md`; the 600 s absolute fallback was **not** used).
  Wrapper exit code **0** — the ceiling did not fire, not approached (log
  `13_write_control_w29c020.std{out,err}.log`).
  - **Wall-clock (judged measure):** **66.671 s**
  - **App-reported (unjudged datum):** **62.99 s** (`Write to W29C020 successful (62.99s).`,
    grepped by string).
- **Read:** control arm, single read, `firestarter -p /dev/ttyACM0 read w29c020 run_01.bin`, exit
  code **0** (`--app-verdict`), log `14_read_control_w29c020.std{out,err}.log`.
  - **Read wall-clock (this task's own cross-board datum):** **45.756 s** (app-reported: 41.87 s).
  - **Cross-board comparison, buffer difference named:** A1's control-arm 262144 B read baseline
    (`161-03-SUMMARY.md`) was **73.344 s**. This cell's read (45.756 s) is markedly faster —
    **consistent with, not proof beyond**, the Leonardo moving 1024-byte chunks per transfer where
    the Uno-class boards move 512; this is a comparison point, not a portable per-byte budget for
    this board (the board's own buffer size is the named variable, per `/workspaces/CLAUDE.md`'s
    board-buffer note).
- **Judge:** `judge_wrv.py --expect-size 262144 --app-verdict 0` ->
  `sha_verdict_judged=match`, `read_count=1`, `distinct_read_shas=1`, `size_violations=[]`,
  `app_verdict_unjudged=0` agreeing.
- **Real VPP context:** unchanged from position 1 — firmware 12.3 V / operator meter 11.44 V, pot
  untouched at `P-08` per instruction.
- **Chip-condition context:** this is a **different, physical W29C020**, unlike the shared
  W27C512 — its condition is **unassessed** (no inspection was sought or given for this chip).
- **Outcome:** `validated`. Appended to `EVIDENCE.jsonl` as position 10 of 12,
  `render_evidence.py --check` green. No re-seat was needed; no `0x303`-class fault occurred.

## Position 3 — `A3-B2__v133__w27c512`

- **Image:** `gen_addr_image.py --stamp-width 16 65536 26` -> `reads/A3-B2__v133__w27c512/written.bin`,
  65536 B, sha256 `558decd0795b5d534aece2d94be4c52d62d42aa67a03f72a37f984d0eeadb807`, matches
  `IMAGE-PLAN.json`'s row (mask 26, stamp 16 — differs by design from position 1's mask 24).
- **Write:** `v133` arm, `firestarter -p /dev/ttyACM0 write w27c512 written.bin`, under
  `timeout --signal=INT 165`. Wrapper exit code **0** (log
  `18_write_v133_w27c512.std{out,err}.log`).
  - **Wall-clock (judged measure):** **37.118 s**
  - **App-reported (unjudged datum):** **33.37 s** (`Write to W27C512 successful (33.37s).`,
    grepped by string — this arm's identical success string sits at `eprom_operations.py:1934`,
    a different source line than the control arm's `:2045`).
- **Read set — N=3 read-stability gate (v1.33 arm only, a real gate, not a formality):**
  `dev consistency-check w27c512 --runs 3 --output-dir reads/A3-B2__v133__w27c512 --keep-files`,
  whole-invocation wall-clock **32.607 s** (log
  `19_consistency_check_v133_w27c512.std{out,err}.log`). Per-run app-reported elapsed: run 1
  10.69 s, run 2 10.57 s, run 3 10.66 s. **All three SHAs agree with each other AND with the
  written image** (`558decd0...`) — `distinct_read_shas=1`, `n3_disagreement=false`. Command exit
  code **0** (`--app-verdict`).
- **Judge:** `judge_wrv.py --expect-size 65536 --app-verdict 0` ->
  `sha_verdict_judged=match`, `read_count=3`, `distinct_read_shas=1`, `size_violations=[]`,
  `app_verdict_unjudged=0` agreeing with the judged match.
- **Relevance to cell A2's open N=3 instability question (position 3,
  `A2__v133__w27c512`), stated explicitly:** A2 recorded three DISTINCT SHAs on the identical
  arm (v133) and identical chip (this same physical W27C512, its eighth handling there) on the
  **uno328pb**, and A2's own control-arm escalation meant to disambiguate it was **blocked**
  (VPP finding) and left **UNDETERMINED**. This position runs the **same v133 arm, the same
  physical chip** (its tenth handling overall, ninth-plus-one since the caveat closed), on a
  **different board** (Leonardo, not uno328pb) — and the three reads here are **perfectly
  stable**. This is informative in both directions, stated with its limits: it does **not**
  resolve A2's own instability (a different board, a different real VPP rail — 11.44 V here vs
  A2's inferred ~11.05 V — and different EEPROM calibration are all simultaneously different
  between the two cells, so this single stable result cannot isolate which variable mattered
  there). It **does** show that the same v133-arm / same-chip combination is **not
  unconditionally unstable** — instability is not an inherent property of this exact chip under
  the v1.33 arm regardless of rig. Handed to Phase 165 alongside A2's own unresolved record, not
  as a resolution of it.

### BOARD-04 comparison paragraph — the only valid v1.31 timing comparison in this milestone

**A/B pair, same board same chip same shield same pot, only the arm differs:** this cell's
control-arm W27C512 write (position 1, `A3-B2__control__w27c512`) was **37.172 s wall / 33.37 s
app**; this position's v1.33-arm write was **37.118 s wall / 33.37 s app**. **Wall-clock
difference: 0.054 s; app-reported figures are identical to two decimals (33.37 s both).** This
tiny difference is the A/B signal this milestone exists to produce for this chip on this rig —
essentially no behavioural difference between the two arms' write paths for the W27C512 on this
board, at this real VPP rail.

**v1.31 comparison, on the only rig where it is valid at all, stated with its method difference
named:** v1.31's **0.37 s** figure is the **spread** (max minus min) across **three** full 64 KiB
write cycles' app-reported, success-only durations — 106.06 / 105.69 / 106.06 s — measured on
this exact **Leonardo + Rev 2.0** rig, firmware `ebe9cb3`. It is a spread, not a duration, and
Phase 145 drew no comparative claim from it. **v1.34 takes one write per position on each arm, so
there is no v1.34 spread to set against v1.31's** — the honest comparison is the two app-reported
figures above (control 33.37 s, v133 33.37 s) and their difference (**0.00 s**, to two decimals),
presented beside v1.31's three-cycle spread of 0.37 s, never as a single v1.34 figure "compared
to 0.37 s".

**Both v1.34 figures land far below v1.31's ~106 s baseline. This is PR #55's per-byte VPE-settle
amortisation** (105.9 s to 33.35 s, merged as firmware `3.0.0b22`), which is in **both** the
control arm's merge base and v1.33's — `rig-pins.json` records the same PR as the reason the
control hex is the *larger* of the two arms' binaries. **Both arms carry the fix.** Stating these
figures next to 0.37 s without this sentence would read as a spectacular v1.33 improvement that
is nothing of the kind; it is not one.

- **Outcome:** `validated`. Appended to `EVIDENCE.jsonl` as position 11 of 12,
  `render_evidence.py --check` green. No re-seat needed; no `0x303`-class fault occurred; the
  chip-condition caveat closed at `P-05` held through this position too.

## Position 4 — `A3-B2__v133__w29c020` — the last position of the phase's twelve

- **Image:** `gen_addr_image.py --stamp-width 32 262144 27` -> `reads/A3-B2__v133__w29c020/written.bin`,
  262144 B, sha256 `5da571d8407b97c754858bb63524b4adc80c8078d90d8a39f478cb248edfbfb8`, matches
  `IMAGE-PLAN.json`'s row (mask 27, stamp 32 — differs by design from position 2's mask 25).
- **Write:** `v133` arm, `firestarter -p /dev/ttyACM0 write w29c020 written.bin`, under
  `timeout --signal=INT 391.748` — the **DERIVED** ceiling (4x A1's measured control-arm W29C020
  wall-clock, 97.937 s; the 600 s absolute fallback was **not** used). Wrapper exit code **0**
  (log `20_write_v133_w29c020.std{out,err}.log`).
  - **Wall-clock (judged measure):** **66.674 s**
  - **App-reported (unjudged datum):** **62.99 s** (`Write to W29C020 successful (62.99s).`,
    grepped by string).
- **Read set — N=3 read-stability gate:** `dev consistency-check w29c020 --runs 3
  --output-dir reads/A3-B2__v133__w29c020 --keep-files`, whole-invocation wall-clock **135.763 s**
  (log `21_consistency_check_v133_w29c020.std{out,err}.log`; the first attempt at this command
  was killed by the calling shell's own outer timeout mid-run-3 at ~120 s — an artifact of the
  tool harness, not a device behaviour; the partial `run_03.bin` (163840/262144 B) from that
  attempt was discarded and every file re-generated cleanly on the immediate re-run with a longer
  outer timeout, recorded here per the same discipline as a discarded touch/probe attempt).
  Per-run app-reported elapsed: run 1 45.16 s, run 2 45.11 s, run 3 45.04 s. **All three SHAs
  agree with each other AND with the written image** (`5da571d8...`) — `distinct_read_shas=1`,
  `n3_disagreement=false`. Command exit code **0** (`--app-verdict`).
- **Judge:** `judge_wrv.py --expect-size 262144 --app-verdict 0` ->
  `sha_verdict_judged=match`, `read_count=3`, `distinct_read_shas=1`, `size_violations=[]`,
  `app_verdict_unjudged=0` agreeing.
- **A/B pair vs this cell's own control W29C020 (position 2), same board same chip same shield
  same pot, only the arm differs:** control was **66.671 s wall / 62.99 s app**; this v133-arm
  write is **66.674 s wall / 62.99 s app**. Wall-clock difference 0.003 s; app-reported figures
  identical to two decimals. As with the W27C512 pair, essentially no behavioural difference
  between the two arms for this chip on this rig at this real VPP rail.
- **Cross-board context (a board characteristic, not a v1.33 signal — both this cell's control
  and v133 figures are compared to A1's control-arm figure, never v133-to-v133 across boards):**
  A1's control-arm W29C020 write (Uno) was 97.937 s; this rig's **control** W29C020 write
  (position 2) was 66.671 s — **~32% faster**, consistent with the Leonardo's 1024-byte chunks
  vs the Uno's 512.
- **Outcome:** `validated`. Appended to `EVIDENCE.jsonl` as position 12 of 12 — **the last
  position of the phase's twelve sweep positions.** No re-seat needed; no `0x303`-class fault
  occurred.

### Cell A3/B2 four-position A/B summary (Phase 163 cites these rows, never re-runs them)

| Position | Arm | Chip | Judged verdict | Wall-clock | App-reported |
|---|---|---|---|---|---|
| 9 (`control__w27c512`) | control | W27C512 | match | 37.172 s | 33.37 s |
| 10 (`control__w29c020`) | control | W29C020 | match | 66.671 s | 62.99 s |
| 11 (`v133__w27c512`) | v133 | W27C512 | match (N=3 stable) | 37.118 s | 33.37 s |
| 12 (`v133__w29c020`) | v133 | W29C020 | match (N=3 stable) | 66.674 s | 62.99 s |

All four positions on this cell are clean matches — the control and v1.33 arms are
**behaviourally indistinguishable** on both chips on this rig, at this real VPP rail (~11.44 V).
The only two arm-attributable data points in this cell that carry any signal are the two
independent read-back proofs' judged spans (28170 B control vs 25098 B v133, by construction —
the arms' own binary sizes) — not a write/read timing difference.
