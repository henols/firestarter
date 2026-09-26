# 146-BENCH-RECHECK — W27C512 regression recheck run during Phase 146

> **Status of this document.** It is **not** the output of any `146-*-PLAN.md`. It records a bench
> run the orchestrator performed under standing operator authorization given on 2026-08-17
> ("if you have the need of bench testing you can do that without asking me"), while plan `146-12`
> was parked at its blocking operator wording review.
>
> It **ticks no requirement**, discharges no carry-forward, and amends no plan's record. Phase 145
> remains the milestone's bench-validation phase and its log remains the authority. Nothing here was
> written into `146-LEDGER.md`, `146-GH15-RECONCILIATION.md` or either release body — all three were
> frozen at the time of this run and are byte-unchanged by it.

## 0. Why this run happened

The three outward-facing artifacts awaiting the operator's wording verdict assert, among other
things, that the intermittent single-byte margin failure from Phase 145 session 1 is **mitigated and
not explained**, and that the firmware defect behind the byte-0 program failure was fixed. Those are
claims about to be published.

This run was a **falsification attempt** against them, chosen for its asymmetry:

- a **pass** changes nothing — the artifacts already say clean cycles are not a root cause;
- a **failure** would have been material, because it would mean the shipped mitigation is not
  holding and the release wording would be wrong to publish.

It failed to falsify. Details below.

## 1. Bench identity, measured at run time

| Item | Value | How |
|---|---|---|
| Controller | `leonardo` | `firestarter fw` |
| Port | `/dev/ttyACM0` | `firestarter fw` |
| Firmware on board | `3.0.0b17` | `firestarter fw` |
| Shield revision | `Rev 2.0-class, Override HW: Rev 2.0-class` | `firestarter hw` |
| Shield revision, operator-stated | Rev 2.0 | operator message, 2026-08-17 |
| Part | `W27C512` | `firestarter id w27c512` → chip-ID check passed (0.28 s) |

Port identity was re-verified in this session rather than carried forward, because `/dev/ttyACM*`
numbering shuffles across replug. The EEPROM revision byte cannot by itself distinguish the
operator's Rev 2.2 / Rev 2.0 / modified Rev 0 shields; the Rev 2.0 attribution here rests on the
operator's own statement, and the reading is recorded alongside it rather than in place of it.

`3.0.0b17` is the same build string that appears 14 times in `145-BENCH-LOG.md`. Per that log's own
caveat, a version string identifies neither the image nor the commit it was built from — so this is
recorded as a **consistent** reading, not as proof that the board carries a particular build.

## 2. Pre-state, before anything was written

Two consecutive full reads, no write between them:

| Read | SHA-256 | Bytes | Wall |
|---|---|---|---|
| 1 | `0549c4e673531cb0e23ded2fc56ce7527c4cb5e546dd0fcfca094a3dc323032d` | 65536 | 7.40 s |
| 2 | `0549c4e673531cb0e23ded2fc56ce7527c4cb5e546dd0fcfca094a3dc323032d` | 65536 | 7.40 s |

Read stability **PASS at N=2**, one distinct SHA. Content shape: 4096 bytes of pattern at the low
addresses, the remaining **61440 bytes blank (`0xFF`)**, 137 distinct byte values.

That SHA appears **zero** times in `145-BENCH-LOG.md`, so this is **not** the state Phase 145 left
the part in. Both pre-state reads were retained before the first write, so the prior contents are
recoverable.

## 3. Three cycles, three distinct images

Each cycle used a **different** deterministic 64 KiB image, so a no-op rewrite cannot present as a
success — the same precaution Phase 145 applied between its own cycles. Every cycle ran plain
`write`, which erases. **No** `--force`, **no** `write -b`, **no** `--no-blank-check`: `write -b`
skips the erase rather than merely the blank check, and silently corrupts a non-blank part while
still reporting success.

| Cycle | Image SHA-256 | `write` | wall | `verify` | read-back ×2 | Verdict |
|---|---|---|---|---|---|---|
| 1 | `195b82be5e39bc88e6d2ee170ca296bbaee8ae8dcf37a29aed5e9b431fac3e75` | rc=0 | 105.83 s | rc=0 (5.68 s) | both SHA-identical to source | byte-exact, stable |
| 2 | `9b2654ab3fccddc97c0e079eb72a6fea908f41cee3e8f316df143c3e767e7b67` | rc=0 | 109 s | rc=0 | both SHA-identical to source | byte-exact, stable |
| 3 | `84896d964d10f819d6bfc33145d671e9ee1328a4cad3bfd528b1cf1bbecf5c0f` | rc=0 | 110 s | rc=0 | both SHA-identical to source | byte-exact, stable |

All three image SHAs are distinct (`sort -u` over the three returns 3). In every cycle the read-back
SHA equals the source image SHA on both reads, so each cycle is byte-exact over all 65536 bytes with
read stability at N=2.

## 4. What this establishes

1. **Byte `0x000000` programs.** The Phase 145 session-1 failure mode — `Byte at 0x000000 failed to
   program within 25 pulses`, exit 1, on the first byte of the first block — did **not** recur, in
   three consecutive cycles on this board. The debug session
   `.planning/debug/w27c512-program-fail-byte0.md` attributed that failure to a firmware defect
   (Phase 141 removed the EPROM write path's only `CTRL_VPE_ENABLE` assert). This run is consistent
   with that fix being present and effective on the attached board.
2. **Full-array fidelity on this part, this controller, this shield revision** — three erase-and-
   reprogram cycles, byte-exact each time, each verified by an independent read-back pair rather than
   by the write command's own return value alone.
3. **Three more clean cycles**, on top of the roughly seventeen `145-BENCH-LOG.md` already records.

## 5. What this does NOT establish — read this before citing the section above

1. **It does not root-cause the intermittent single-byte margin failure.** Carry-forward items 12 and
   5 in `145-BENCH-LOG.md` (`:2516`, `:2535`) state the discriminator plainly: separating an
   under-settled route from a marginal cell from program-window VPP droop needs either the
   instrument noted there as blocked, or a second W27C512 sample. Clean cycles are not a root cause,
   and three more clean cycles are not either. **That carry-forward stays open and unowned.**
2. **It does not supply the second sample.** Whether the part seated for this run is the same
   physical sample Phase 145 used, or a different one, is operator knowledge that cannot be read over
   this interface — no serial number is exposed. The pre-state SHA not matching Phase 145's end state
   is consistent with either a different sample *or* an intervening write to the same one, and does
   not discriminate between them. So this run cannot be counted as the second-sample evidence the
   carry-forward asks for.
3. **It is not CI parity and it is not coverage of anything else.** One part, one controller class,
   one shield revision. No AVR target other than this Leonardo was exercised, no other protocol was
   exercised, and the two protocols Phase 145 skipped-with-reason remain skipped.
4. **It does not revisit the program-VCC ceiling.** The roughly 6.25 V accepted debt and the
   silicon-margin narrowing it implies are untouched by this run; nothing here was measured with a
   meter, and no rail was instrumented under load.
5. **It changes no published wording.** The release bodies' framing of this failure as mitigated
   rather than explained remains accurate, which is the one conclusion this run does support.

## 6. Boundary compliance

- **D-01** — no push, no merge, no tag, no release, no workflow dispatch, nothing posted. The two
  sub-repository ahead-counts were unchanged by this run (`firestarter` 63, `firestarter_app` 18).
- **D-06** — no firmware or host source byte was touched. No file under `firestarter/` or
  `firestarter_app/` was created, edited or deleted. Both inner working trees were at their expected
  state throughout (`firestarter` porcelain 0 lines; `firestarter_app` porcelain 7 lines of
  pre-existing untracked dirt).
- **Frozen artifacts** — `146-GH15-RECONCILIATION.md`, `146-RELEASE-NOTES-fw.md` and
  `146-RELEASE-NOTES-app.md` were byte-unchanged by this run and remain at the blob SHAs `146-12`
  recorded at its freeze.
- **No requirement ticked.** `CLOSE-01` through `CLOSE-05` remain unticked; `146-13` owns all five.
- All working files for this run were written under the session scratch directory, not into either
  repository.
