---
phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur
plan: 05
subsystem: bench-tooling
tags: [bench, avrdude, objcopy, readback, sha, oracle, serial, judge]

requires:
  - phase: 160-01
    provides: "rig-pins.json (avrdude binary/conf/forbidden_binaries, per-target mcu/programmer/baud/flash_size/hex_span_expected/judged_span_policy/vector_exclusions, objcopy path, image_naming pattern, chips.*.size_bytes, forbidden_flags)"
  - phase: 160-03
    provides: "tools/gen_addr_image.py's mask/stamp_width convention and bench/IMAGE-PLAN.json's per-position sha/mask this plan's judge_wrv.py pairs against"
  - phase: 160-04
    provides: "tools/gate_record.py — the record gate these two judges' verdict shape must satisfy; tools/probe_board.py — the sibling avrdude-invoking tool whose CLI conventions (pinned-binary resolution, --selftest style, atomic write) this plan mirrors"
provides:
  - "tools/judge_readback.py — the independent on-device flash judge (D-01/D-02): a separate avrdude read-back, normalized against the pinned avr-objcopy, judged over the pinned per-target judged_span_policy, with the whole-flash SHA recorded but explicitly unjudged"
  - "tools/judge_wrv.py — the full-device write→read→verify judge (D-10/D-11/RIG-04): SHA-256 over the full chip size against the written image, never the app's own dev consistency-check exit code, with the app's 0/1/2 recorded beside it and any disagreement between the two oracles surfaced rather than resolved"
  - "tools/touch_1200.py — the Leonardo Caterina bootloader-entry helper, with both post-touch port behaviours available behind --wait-new-port and its own device leg declared unproven until bring-up"
affects: ["160-08", "160-09", "160-10", "160-11", "160-12", "160-13"]

tech-stack:
  added: ["pyserial (touch_1200.py only, system-wide 3.5, the one permitted non-stdlib rig-tool import)"]
  patterns:
    - "Pure decision functions (judge_span_bytes, resolve_judged_policy, judge_position, decide_new_port, wait_for_new_port with injected clock/sleep/enumerate_fn) kept separate from subprocess/serial-invoking wrappers, so --selftest and the hand-built bring-up fixtures exercise the real decision logic with zero wall-clock cost and no device"
    - "--readback/--no-read is a paired, mutually-required flag idiom (each requires the other) so a re-judge of a committed artifact can never be silently mistaken for a live device read"
    - "A judge's 'incomplete-read-set' state is derived from the producing tool's own semantic signal (app_verdict==2, or zero files present) rather than from a tracked expected-N — because RIG-04 forbids assuming N anywhere in the judging path and neither this plan's frozen verdict-key list nor its flag list carries an expected-count field"
    - "verdict_disagreement is a single XOR of two independently-computed booleans (app_says_ok = app_verdict==0; judged_ok = sha_verdict_judged=='match') rather than a hand-enumerated table of app-code/sha-verdict pairs — this generalizes cleanly to every one of the plan's worked examples without extra branches"

key-files:
  created:
    - .planning/v1.34/tools/judge_readback.py
    - .planning/v1.34/tools/judge_wrv.py
    - .planning/v1.34/tools/touch_1200.py
  modified: []

key-decisions:
  - "judge_readback.py's 'incomplete manifest' path is tolerant-by-design: BUILD-MANIFEST.json does not exist yet in this session (plan 02, the images build plan, has not run), so _load_json() treats a missing manifest as {} rather than a hard failure — the hex_span_expected cross-check against rig-pins.json still fires unconditionally; the BUILD-MANIFEST.json cross-check fires only when that file (and a matching image entry) exists. This keeps the tool authorable and fully selftestable now while remaining correct once plan 02 lands the real manifest."
  - "judge_wrv.py's 'incomplete-read-set' verdict is triggered by app_verdict==2 OR read_count==0, never by comparing the observed count against a tracked expected N — the plan's own frozen flag list (--written/--reads/--expect-size/--app-verdict/--position-id/--pins/--out/--selftest) and verdict-key list (no 'expected_count' key) both omit an N slot, and RIG-04's own text ties incompleteness to the app's documented early-return-2 contract, not to a number this tool would otherwise have to assume. The selftest's 'two read files where three were expected' negative leg supplies app_verdict=2 to signal exactly this app-side contract, which is the same signal a live hardware/serial error produces."
  - "verdict_disagreement is computed uniformly as (app_verdict==0) XOR (sha_verdict_judged=='match') across every sha_verdict_judged state (match/mismatch/disagreement/incomplete-read-set), not only for match/mismatch — this was checked against both of the plan's own worked examples (app=0 vs mismatch; app=1 vs match) and against the incomplete-read-set states, where it also correctly flags a contradiction (e.g. app claims PASS but zero read files exist) without needing a separate branch."
  - "judge_readback.py's --readback and --no-read are made MUTUALLY required (each errors without the other) rather than --readback alone implying --no-read, per the plan's own framing of --no-read as --readback's 'explicit companion' — this makes a re-judge invocation self-documenting in its own argv rather than relying on one flag's presence to silently imply the other's behaviour."
  - "touch_1200.py's --wait-new-port timeout/enumeration logic takes clock/sleep/enumerate_fn as injectable parameters specifically so --selftest can exercise the --timeout-s 0 timeout leg and a genuinely-new-port leg with a fake monotonic clock — zero wall-clock cost, no real device, and no reliance on a live poll loop actually elapsing during a test run."
  - "touch_1200.py's --timeout-s default (10.0s) is a new value this plan introduces (not stated in rig-pins.json or CONTEXT) chosen to exceed RESEARCH Pitfall 5's measured ~8s Caterina inactivity window with margin; it is a tool default only, overridable per invocation, and plan 10's Leonardo bring-up is the authority on whether it needs revision."

requirements-completed: []

coverage:
  - id: D1
    description: "judge_readback.py authored — independent avrdude read-back (-A on every target, fixed flash_size length asserted), avr-objcopy hex-extent normalization, per-target judged_span_policy with placeholder refusal and vector-exclusion support, whole-flash SHA recorded but explicitly unjudged, --flashed-arm/--expect-arm as distinct closed-choice arguments expressing the D-03 cross-flash as one invocation — Task 1"
    requirement: "RIG-01"
    verification:
      - kind: unit
        ref: "python3 .planning/v1.34/tools/judge_readback.py --selftest (rc=0, 2 positive + 6 negative legs PASS, including a real avr-objcopy subprocess invocation against a synthetic Intel-hex fixture)"
        status: pass
      - kind: other
        ref: "live invocation against hand-built fixtures outside --selftest via --readback/--no-read: short-read-back, prefix-mismatch, cross-arm-expectation and placeholder-judged_span_policy legs all observed red (rc=1, FAIL:... quoted in this SUMMARY); a matching-arm positive control observed green (rc=0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "judge_wrv.py authored — SHA-256 over the full device size against the written image, never the app's dev consistency-check exit code; globs and counts run_*.bin rather than assuming N; incomplete-read-set / disagreement / size_violations all recorded as outcomes, never retried; verdict_disagreement flags a contradiction between the app's unjudged verdict and the judged SHA verdict — Task 2"
    requirement: "RIG-04"
    verification:
      - kind: unit
        ref: "python3 .planning/v1.34/tools/judge_wrv.py --selftest (rc=0, 1 positive + 7 negative legs PASS)"
        status: pass
      - kind: other
        ref: "the Pitfall 6 false-green leg (three self-consistent but wrong reads, app_verdict=0) observed red live against hand-built fixture files outside --selftest: rc=1, sha_verdict_judged=mismatch, verdict_disagreement=true (quoted in this SUMMARY)"
        status: pass
    human_judgment: false
  - id: D3
    description: "touch_1200.py authored — 1200-baud touch mechanism copied from avr_tool.py with the swallow-and-warn handling rejected (every failure path exits non-zero), both same-port and wait-for-new-port behaviours implemented behind --wait-new-port, its own device leg declared unproven until Leonardo bring-up — Task 3"
    requirement: "RIG-01"
    verification:
      - kind: unit
        ref: "python3 .planning/v1.34/tools/touch_1200.py --selftest (rc=0, 5 legs PASS, including a dependency-injected fake-clock timeout leg and a stubbed-directory enumeration leg)"
        status: pass
      - kind: other
        ref: "live invocation against a non-existent port path observed red outside --selftest: rc=1, FAIL: port does not exist (quoted in this SUMMARY)"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-08-26
status: complete
---

# Phase 160 Plan 05: The Flash Read-Back Judge, the Write-Verify Judge, and the Caterina Touch Summary

**Authored the two judges that make this milestone's oracles independent of the things they judge — `judge_readback.py` proves a flash by a separate avrdude read-back normalized against the pinned `avr-objcopy` and judged under a per-target policy that refuses an unresolved bootloader interrogation; `judge_wrv.py` proves a write by full-device SHA-256 against the written image, never the app's own exit code, and surfaces any disagreement between the two oracles as a finding — plus `touch_1200.py`, the Leonardo Caterina bootloader-entry helper that reports its own failure instead of swallowing it.**

## Performance

- **Duration:** ~50 min
- **Started:** 2026-08-26T22:07Z (context load)
- **Completed:** 2026-08-26T22:17Z
- **Tasks:** 3/3, all `type="auto"`
- **Files modified:** 3 created, 0 modified

## Accomplishments

- `tools/judge_readback.py` reads the pinned avrdude with `-A` explicit on every invocation (Pitfall 2), asserts the read-back file is exactly the target's `flash_size` before doing anything else, normalizes the reference `.hex` with the pinned `avr-objcopy -I ihex -O binary`, cross-checks the resulting span against both `rig-pins.json`'s `hex_span_expected` and (when present) `BUILD-MANIFEST.json`'s per-image `hex_span`, and judges the `[0, span)` prefix under the target's `judged_span_policy` — refusing outright, with a named `FAIL:` line, any target whose policy is still the `PENDING-*` placeholder (Pitfall 3). `--flashed-arm` and `--expect-arm` are distinct closed-choice arguments, both recorded in the verdict, so the D-03 deliberate cross-flash is a single invocation (flash arm X, judge against arm Y's hex). The whole 32768 B read-back's SHA is recorded as `sha_whole_flash_unjudged` and no code path in the file ever consumes it in a match decision. `--readback PATH` + the mutually-required `--no-read` judge an existing file without touching a device.
- `tools/judge_wrv.py` judges a position (never a command): it globs `run_*.bin` in `--reads` and derives `read_count` from the glob, asserts every file's size equals `--expect-size` (rejecting any value other than 65536/262144) and records violations in `size_violations`, computes SHA-256 over the full device size for every read file and the written image, and sets `sha_verdict_judged` to `match` only when every read equals the written image's SHA. `app_verdict_unjudged` records the app's own 0/1/2 without ever being treated as the verdict; `verdict_disagreement` is a single XOR between the app's claimed direction and the judged direction, catching both of the plan's worked contradictions (app=0 vs SHA-mismatch; app=1 vs SHA-match) plus the app-claims-PASS-but-zero-files-exist case. `distinct_read_shas > 1` produces `disagreement` with `n3_disagreement=True` and every individual read SHA listed — never retried. `app_verdict==2` or zero files present produces `incomplete-read-set`.
- `tools/touch_1200.py` copies `avr_tool.py`'s three-line 1200-baud-touch-then-settle mechanism and explicitly rejects its swallow-and-warn exception handling — every failure path (nonexistent port, serial exception, `--wait-new-port` timeout) exits non-zero with a `FAIL:` line. Both PlatformIO's wait-for-a-new-port behaviour and the app's reuse-the-same-port behaviour are implemented, selected by `--wait-new-port`, because which one holds for the read-back direction is a plan-10 Leonardo bring-up measurement rather than an assumption. `--settle-s` defaults to 2. `serial` is the file's only non-stdlib import.
- All three tools' `--selftest` modes pass (0 exit) with every documented positive and negative leg individually named: `judge_readback.py` (2 positive + 6 negative, including a real `avr-objcopy` subprocess call against a synthetic Intel-hex fixture), `judge_wrv.py` (1 positive + 7 negative), `touch_1200.py` (5 legs, including a dependency-injected fake-clock timeout leg with zero wall-clock cost).
- An AST scan across all three files confirms zero `subprocess` calls with `shell=True`. `judge_wrv.py` and `touch_1200.py` import only the standard library plus, in `touch_1200.py` alone, `pyserial` (the one permitted non-stdlib rig-tool import, per `rig-pins.json`'s `tool_conventions.import_policy`).
- The plan's four highest-value negative legs for `judge_readback.py` were all **observed red live**, outside `--selftest`, against hand-built fixtures (synthetic Intel-hex images + synthetic read-back `.bin` files, real pinned `avrdude`/`avr-objcopy` binaries) — quoted below. `judge_wrv.py`'s Pitfall 6 false-green leg and `touch_1200.py`'s missing-port leg were likewise observed red live outside `--selftest` — also quoted below.
- Both sub-repos (`firestarter`, `firestarter_app`) confirmed porcelain-clean throughout.

## Task Commits

1. **Task 1: Author `tools/judge_readback.py`** — `8435b5b2` (feat)
2. **Task 2: Author `tools/judge_wrv.py`** — `9388cd39` (feat)
3. **Task 3: Author `tools/touch_1200.py`** — `b12c6c11` (feat)

**Plan metadata:** committed below (this SUMMARY + STATE.md/ROADMAP.md)

## Files Created/Modified

- `.planning/v1.34/tools/judge_readback.py` — independent flash read-back judge (Task 1)
- `.planning/v1.34/tools/judge_wrv.py` — full-device write→read→verify judge (Task 2)
- `.planning/v1.34/tools/touch_1200.py` — Caterina bootloader-entry helper (Task 3)

## Decisions Made

See `key-decisions` in the frontmatter above for the full list with rationale. Summary:

- `judge_readback.py` tolerates a missing `BUILD-MANIFEST.json` (it doesn't exist yet — plan 02 hasn't run) by treating it as `{}`; the `rig-pins.json` `hex_span_expected` cross-check still fires unconditionally, so the tool is neither silently permissive nor blocked on an artifact this plan doesn't own.
- `judge_wrv.py`'s `incomplete-read-set` is derived from `app_verdict==2` or `read_count==0`, never from a tracked "expected N" — the plan's own frozen flag and verdict-key lists have no slot for one, and RIG-04's early-return-2 contract is itself the signal.
- `verdict_disagreement` is one XOR (`app_verdict==0` vs `sha_verdict_judged=='match'`) applied uniformly across all four `sha_verdict_judged` states, rather than a hand-enumerated per-state table — verified against every worked example the plan itself gives.
- `judge_readback.py`'s `--readback` and `--no-read` are mutually required (neither works without the other), making a re-judge invocation self-documenting in its own argv.
- `touch_1200.py`'s wait-for-new-port polling takes an injectable clock/sleep/enumerate_fn specifically so the timeout and new-port-detection legs are testable in `--selftest` with zero wall-clock cost.
- `touch_1200.py`'s `--timeout-s` default of 10.0s is a new tool default (not previously pinned anywhere), chosen with margin over RESEARCH's measured ~8s Caterina window; plan 10's bring-up is the authority on whether it needs adjustment.

## Deviations from Plan

None — plan executed as written. The items above are documented design decisions within genuinely open implementation choices (the plan describes behavior and constraints — e.g. "reported with the actual count and the expected count" for `incomplete-read-set`, "explicit companion" for `--no-read` — not exact algorithms or an expected-N mechanism), not deviations from anything the plan specified.

## Issues Encountered

**Observed-red evidence, per the plan's acceptance criteria.**

`judge_readback.py` — all four legs run against hand-built fixtures (a synthetic Intel-hex pair for `control`/`v133`, synthetic read-back `.bin` files, the real pinned `avrdude`/`avr-objcopy` binaries via `--readback`/`--no-read` so no device is touched):

```
$ python3 .planning/v1.34/tools/judge_readback.py --target uno --flashed-arm control --expect-arm control \
    --out-dir <tmp>/out1 --pins <fixture-pins.json> --readback <tmp>/readback_short.bin --no-read
FAIL: read-back file is 199 B, expected exactly 200 B -- this is the truncation symptom -A exists to prevent (Pitfall 2)
(exit 1)

$ python3 .planning/v1.34/tools/judge_readback.py --target uno --flashed-arm control --expect-arm control \
    --out-dir <tmp>/out2 --pins <fixture-pins.json> --readback <tmp>/readback_corrupt.bin --no-read
FAIL: judged span mismatch -- 1 differing byte(s), first 1 shown: offset=0x00005 expected=0x05 actual=0x06
(exit 1)

$ python3 .planning/v1.34/tools/judge_readback.py --target uno --flashed-arm control --expect-arm v133 \
    --out-dir <tmp>/out3 --pins <fixture-pins.json> --readback <tmp>/readback_ok.bin --no-read
FAIL: judged span mismatch -- 100 differing byte(s), first 20 shown: offset=0x00000 expected=0x03 actual=0x00; ... (20 offsets total)
(exit 1)

$ python3 .planning/v1.34/tools/judge_readback.py --target uno328pb --flashed-arm control --expect-arm control \
    --out-dir <tmp>/out4 --pins <fixture-pins.json> --readback <tmp>/readback_ok.bin --no-read
FAIL: judged_span_policy is still the placeholder value 'PENDING-xshowvector' -- the bootloader interrogation (-xshowvector) has not yet been recorded for this target; judging now would risk a false mismatch at 0x0000 on every correctly-flashed board
(exit 1)
```

Positive control (matching arm, same fixture set) observed green immediately after, confirming the negative legs above are not simply a broken tool:

```
$ python3 .planning/v1.34/tools/judge_readback.py --target uno --flashed-arm control --expect-arm control \
    --out-dir <tmp>/out5 --pins <fixture-pins.json> --readback <tmp>/readback_ok.bin --no-read
OK: judged_match=True target=uno flashed_arm=control expect_arm=control judged_span_bytes=100 sha_whole_flash_unjudged=9b60b816bcde...
(exit 0)
```

`judge_wrv.py` — the Pitfall 6 false-green leg, live against hand-built fixture files (three self-consistent, mutually identical reads that differ from the written image, `--app-verdict 0`):

```
$ python3 .planning/v1.34/tools/judge_wrv.py --written <tmp>/written.bin --reads <tmp>/reads \
    --expect-size 65536 --app-verdict 0 --position-id BRINGUP-pitfall6 --out <tmp>/verdict.json
FAIL: position BRINGUP-pitfall6 judged sha_verdict_judged='mismatch' read_count=3 distinct_read_shas=1 verdict_disagreement=True size_violations=[]
(exit 1)
```

`touch_1200.py` — missing-port leg, live (no board attached, no fixture needed — the port simply does not exist as a filesystem path):

```
$ python3 .planning/v1.34/tools/touch_1200.py --port /dev/definitely-not-a-port
FAIL: port does not exist: /dev/definitely-not-a-port
(exit 1)
```

No blocking issues.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `judge_readback.py` is ready for plans 08 (uno), 09 (uno328pb) and 10 (leonardo): the avrdude read direction remains genuinely unproven on a real device until those plans put it on the bench — everything in this plan's own risk framing holds. Plan 02 (or whichever plan builds the six images) must populate `.planning/v1.34/images/BUILD-MANIFEST.json` with a `hex_span` per image and `firestarter_<env>.<arm>.hex` files under `.planning/v1.34/images/` for the live path to run; the tool tolerates the manifest's current absence but will need it once real judging starts.
- `judge_wrv.py` is ready for plan 12's live full-device verdict and pairs directly with `bench/IMAGE-PLAN.json`'s per-position `sha256`/`mask`/`stamp_width` (160-03) as the `--written` image's expected SHA.
- `touch_1200.py` is ready for plan 10's Leonardo bring-up, which is the authority on whether `--wait-new-port` or the same-port behaviour holds for the read-back direction specifically, and on whether the 10.0s default `--timeout-s` needs adjustment.
- RIG-01 and RIG-04 are intentionally **not** marked complete, per this plan's own "Requirement completion" section: this plan closes the *judge* mechanism only. RIG-01's "proven able to fail" clause and RIG-04's live full-device verdict both land on a device in plans 08–10 and 12. `REQUIREMENTS.md` stays `Pending` for both.
- No blockers.

## Self-Check: PASSED

- `FOUND: .planning/v1.34/tools/judge_readback.py`
- `FOUND: .planning/v1.34/tools/judge_wrv.py`
- `FOUND: .planning/v1.34/tools/touch_1200.py`
- `FOUND: commit 8435b5b2` (Task 1)
- `FOUND: commit 9388cd39` (Task 2)
- `FOUND: commit b12c6c11` (Task 3)
- `python3 .planning/v1.34/tools/judge_readback.py --selftest` → rc=0
- `python3 .planning/v1.34/tools/judge_wrv.py --selftest` → rc=0
- `python3 .planning/v1.34/tools/touch_1200.py --selftest` → rc=0
- `git -C /workspaces/firestarter status --porcelain` → empty
- `git -C /workspaces/firestarter_app status --porcelain` → empty

---
*Phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur*
*Completed: 2026-08-26*
