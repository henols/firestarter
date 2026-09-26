# W27C512 (0x07) Bench Re-Validation — Operator Checklist (Phase 91)

> **✅ EXECUTED 2026-06-26 — RESULT: PASS.** The operator returned and seated the W27C512; this
> checklist was run end-to-end. chip-ID PASSED (0xDA08); erase-enabled plain `firestarter write`
> (writeA→verifyA→writeB→verifyB→consistency-check N=3) byte-identical to v1.15 `e16b2a5b…`; no
> VPP-high guard. **0x07 graduated to PASS** (evidence `bench/W27C512-fix/`); LEDGER-02 fully
> satisfied (all 4 on-hand protocols PASS). The procedure below is retained for reference/re-runs.
>
> **Why this was deferred originally:** the prior session ran with the **SST39SF040** seated;
> W27C512 needed a chip swap (operator-only). The RCA + fix were done autonomously; this was the
> turnkey for return.
>
> **RCA verdict (Phase 91 — PROVEN on the SST39SF040, same axis applies to W27C512):**
> The Phase-90 `bad bytes:921 @0x000000` on a clean 12.0 V rail was **NOT a VPP regression** and
> **NOT a firmware/host code regression**. It was a **TEST-METHOD error**: Phase 90 used
> `firestarter write -b`, and `-b` (`--no-blank-check`) ALSO sets `FLAG_SKIP_ERASE` (its help reads
> "…and skip erase"). W27C512 is an electrically-erasable EEPROM-class part that **requires an erase
> before write**; with the erase skipped, the first block keeps bits that can't be re-set (program
> only clears 1→0). On the SST39SF040 this was proven exactly (3 stuck bytes `== imgA & imgB`) and
> **fixed by switching to the erase-enabled plain `firestarter write`** (write+verify byte-identical
> to v1.15). The b10 baseline fw failed identically with `-b`, so the recompose is innocent. Full
> detail: `rca/91-RCA.md`.
>
> **Expected outcome here:** plain `firestarter write W27C512 …` (which erases) should write+verify
> clean to the v1.15 baseline. `write -b` is contraindicated for W27C512 (it skips the required erase).

## Preconditions
1. Controller identity: `firestarter fw` → must report **leonardo on /dev/ttyACM*** (the port may be
   ACM0 or ACM1 — the CLI auto-detects; after any reflash, wait ~10 s for the Leonardo to
   re-enumerate before the first op, or you'll hit a spurious "Operation timed out").
2. Shield: confirm **Rev 2.0** silkscreen.
3. Seat **W27C512 ONLY** (remove the SST39SF040 first). Verify pins seated.
4. Board on milestone firmware (stock recompose a296195). `firestarter fw` says `3.0.0b10` for any
   v1.16 build; the reliable discriminator is the flash byte count at last upload (recompose ≈
   25136 B). If unsure, reflash from `/workspaces/firestarter`:
   `pio run -e leonardo && pio run -t upload -e leonardo` (Leonardo is EXEMPT from chip-out).

## Stage the v1.15 images (deterministic generator, seed 1 = A, seed 2 = B)
```
python3 /workspaces/firestarter_app/tools/gen_test_image.py 65536 1 /tmp/W27C512_img_A.bin
python3 /workspaces/firestarter_app/tools/gen_test_image.py 65536 2 /tmp/W27C512_img_B.bin
```

## Write-cycle — use PLAIN `write` (erase-enabled), NOT `write -b`
```
firestarter write   W27C512 /tmp/W27C512_img_A.bin     # erase + blank-check + program; expect RC=0
firestarter verify  W27C512 /tmp/W27C512_img_A.bin     # expect RC=0
firestarter write   W27C512 /tmp/W27C512_img_B.bin     # expect RC=0
firestarter verify  W27C512 /tmp/W27C512_img_B.bin     # expect RC=0
firestarter dev consistency-check W27C512 --runs 3 --output-dir firestarter-runs/W27C512-fix/
```
Each W27C512 write is ~slow (erase + program); allow a few minutes per op. (CLI runs may exceed a
2-minute shell timeout — run unattended or background them.)

## PASS gate (silicon truth)
Final write-cycle / consistency-check SHA-256 ==
`e16b2a5b26d99440a8e596963faa0f2d64fff4e1dd9682b93b2f8f1ddc326ab5` (v1.15 W27C512 image-B baseline).
Negative control: `firestarter verify W27C512 /tmp/W27C512_img_A.bin` → RC=1 (verify non-vacuous).

## Diagnostics (only if it still fails)
- A clean rail + bad-bytes-@0x0 confirms the erase axis, not VPP. Loaded-rail capture (optional):
  `timeout -s INT 20 stdbuf -oL firestarter vpp` during a write (measure-only; safe with a chip
  seated). Erase-rail hold for a DMM: `firestarter dev reg 0 0 0x86 -f` (reset clears).
- If plain `write` still fails at 0x0 after a clean retry: the erase is genuinely not clearing this
  individual chip (chip-specific). Record as a carried defect — do NOT auto-pass (D-03).
- Do NOT "fix" by adding `-b` — that re-introduces the skipped-erase bug.

## Disposition step (after the bench result)
- **PASS (SHA == e16b2a5b…):** graduate the **0x07** row in
  `.planning/milestones/v1.16-artifacts/ledger/PROTOCOL-LEDGER.{json,md}` from `bench-pending` to **PASS** with
  `oracle: leonardo+Rev2.0` and evidence refs → `bench/W27C512-fix/`. Closes the last LEDGER-02
  on-hand row.
- **FAIL:** record the residual mechanism (carried defect).
- Either way: `python3 .planning/milestones/v1.16-artifacts/ledger/tools/check_ledger.py` must exit **RC=0**; append the
  result to `BENCH-LOG.md` (do not rewrite Phase-90/91 history). Honor D-04 (no raw SHA in the
  ledger JSON/MD — reference by evidence path).
