# PRE-PHASE.md — pre-sweep snapshots and budget (162-01 Task 3)

## Part A — the WRV `EVIDENCE.jsonl` snapshot

D-09's baseline that plan 162-10's phase gate re-runs and diffs, proving the sibling
`CHIP-EVIDENCE.jsonl` file never leaked into the WRV one.

```bash
python3 -c "
import json
lines=open('/workspaces/.planning/milestones/v1.34-artifacts/bench/EVIDENCE.jsonl').read().splitlines()
sch=json.loads(lines[0])['_schema']
rows=[json.loads(l) for l in lines[1:] if l.strip()]
nb=[r for r in rows if not str(r.get('cell_id','')).startswith(sch['bringup_cell_id_prefix'])]
print('position_count_expected =', sch['position_count_expected'])
print('non-bringup rows        =', len(nb))
assert sch['position_count_expected']==20
assert len(nb)==12, len(nb)
print('PASS: WRV file untouched at the pre-phase snapshot')
"
```

Verbatim output:
```
position_count_expected = 20
non-bringup rows        = 12
PASS: WRV file untouched at the pre-phase snapshot
```

Expected state confirmed: `position_count_expected: 20`, twelve non-bring-up rows. This is the
figure plan 162-10 re-derives and diffs against at close.

## Part B — the CLOSE-04 "before" issue count (pasted output, not an assertion)

Phase 166's CLOSE-04 explicitly refuses assertions — a code citation *is* an assertion — so this
is the pasted command output, run once at phase start:

```bash
gh issue list --repo henols/firestarter_prom --state all --limit 1000 --json number | \
  python3 -c "import sys,json;print('issue count:',len(json.load(sys.stdin)))"
```

Verbatim output:
```
issue count: 37
```

`gh` ran successfully (authenticated, `henols` account, `github.com`). This "before" figure (37)
is the value plan 162-10 must diff against at phase end. It will also be the expected
`dedup_query_outcome` context: `build_issue_url` produces a *prefilled new-issue URL*, not a
filed issue, so a `dev test --submit` run in this phase (if any position exercises the dedup path)
must never change this count on its own — a filed issue only exists if the operator follows the
prefilled URL, which is out of scope for this phase's automation.

## Part C — the anchors and the budget

**CONTEXT.md's `<specifics>` anchors are Uno figures and are NOT used in this phase.** This phase
runs on **Leonardo + Rev 2.0**; `A3-B2` measured that exact rig, on both arms, twice. All four
ceiling figures below (PD-14) derive from the A3/B2 **Leonardo** anchors, never the Uno ones.

### The four measured A3/B2 Leonardo anchors

| Chip | Op | Wall-clock | App-reported |
|---|---|---|---|
| W27C512 | write | 37.118 s (`A3-B2__v133__w27c512`) | 33.37 s |
| W29C020 | write | 66.674 s (`A3-B2__v133__w29c020`) | 62.99 s |
| W27C512 | read | — | 10.66 s/pass (`--runs 3` per-run figure) |
| W29C020 | read | — | 45.10 s/pass (`--runs 3` per-run figure) |

(Source: `.planning/milestones/v1.34-artifacts/bench/EVIDENCE.jsonl` rows `A3-B2__v133__w27c512` /
`A3-B2__v133__w29c020`, and `.planning/milestones/v1.34-artifacts/bench/cells/A3-B2/WRITE.md`'s three-run
consistency-check figures.)

### The budget: ~2 hours of machine time, not the ~65 min D-16 estimated

**Primary sweep ≈ 3320 s app ≈ 62 min wall** (RESEARCH R5's ten-part derived duration budget,
summed across `read×2 / write×2 / verify×2 / erase×2 / blank-check×1` per part). D-16's "~65 min"
estimate is coincidentally close to this figure — it was extrapolated from Uno figures for a bare
`write` command, and happens to land near the correct Leonardo estimate for a twelve-step,
two-cycle `dev test` invocation. It is not the same measurement arriving at the same number.

**Add the control re-runs: ~19–21 min.** N ≥ 4 flips are budgeted before any genuine divergence
verdict (W29C040, FM1608, ST M27C512, AM27C020 — PD-5), each costing its part's own `dev test`
runtime plus two flashes with their own read-back proofs (~90 s/flash-pair including the judge,
measured `touch_to_read_complete_s = 3.878` plus a `pio run -t upload`). N=4 realistic: W29C040
580 s + FM1608 20 s + M27C512 34 s + AM27C020 137 s = ~771 s + 4 flash pairs (~360 s) ≈ 19 min.
N=6 pessimistic (adds W27E040 980 s + W27E512 120 s + 2 more flash pairs) ≈ +21 min more.

**Total budget: ~2 hours of machine time** (primary sweep ~62 min + control re-runs ~19–21 min),
on top of nine operator chip-swap handovers, one pot move, two JP4 changes, and the per-wave gate
runs. This is materially more than D-16's "~65 min" and this record states so explicitly.

### PD-14's four stall ceilings, each with its arithmetic

Per 161 D-08's pattern: a stalled write is killed at a ceiling derived from a measured healthy
figure (4×), and the kill is logged. `dev test` is a **single invocation covering all twelve
steps**, so the ceiling is a whole-invocation timeout, not a per-write one.

| Size class | First part (supplies the class figure) | Ceiling for later parts of the class | Fallback absolute for the first part, with its arithmetic |
|---|---|---|---|
| 8 KiB | FM1608 (part 4) | 4 × its own measured total | **120 s** = 4 × 25 s, floored generously because 8 KiB cannot legitimately take minutes (write rate unmeasured — flagged) |
| 64 KiB | **W27C512 (part 1)** | 4 × its measured total | **500 s** = 4 × 123 s, where 123 s = read 21 s (2×10.66) + write 67 s (2×33.37÷~1) + verify 21 s + erase ~2 s + blank-check 11 s, every component measured on this rig |
| 256 KiB | **W29C020 (part 8)** | 4 × its measured total | **1120 s (18.7 min)** = 4 × 280 s, from the same-rig 62.99 s app-write and 45.10 s/read pass |
| 512 KiB | **SST39SF040 (part 5, after PD-1's swap)** | 4 × its measured total | **3920 s (65 min)** = 4 × 980 s. 980 s is the **larger** of the two 512 KiB estimates (W27E040's proto-8 at an assumed 1964 B/s vs SST39SF040's proto-6 at v1.15's ~2185 B/s); the larger is used deliberately because **neither proto-6 nor proto-8 write rate is measured on current firmware**, and 161 D-08 requires a widening to be stated rather than silently exceeded |

Every ceiling above is derived from measured components at a stated rate, ×4 — never a bare
number, per 161 D-08's discipline.

## `write`/`write-partial` dual-key rule and the SDP-floor-unreachable finding

Any per-step lookup keyed on the literal `"write"` alone will **silently miss** AM27C020 and
M27C512, whose write op is `write-partial` (see `DERIVE-PLAN.json`). Every bench plan's per-step
lookup in this phase must key on **both** `write` and `write-partial`.

All six SDP legs (`write-baseline-a`, `write-baseline-b`, `sdp-lock`, `write-inhibited`,
`sdp-unlock`, `write-restored`) are `supported=False` on all eleven tokens in `DERIVE-PLAN.json`,
every reason string reading "SDP lock/unlock applies only to protocol 0x0D parallel EEPROMs" (or
the UV-specific "no electrical erase" reason on the two UV parts) — confirming CONTEXT.md's claim
that **the SDP exit floor can never fire in this phase**.

## `run_gates.sh` — full suite, exit code read directly

```bash
bash /workspaces/.planning/milestones/v1.34-artifacts/tools/run_gates.sh
RC=$?
```

Result: **12/12 tool selftests, 5/5 live gates, exit 0.** (This plan adds no new tool, so the
count stays at 12 — `run_gates.sh` itself is not modified by this plan; the two-tool/two-live-gate
expansion for `append_chip_evidence.py`/`render_chip_evidence.py` is a later plan's work.)

Verbatim tail of `run_gates.sh`'s own summary:
```
live gate PASS: gate_record.py

===== run_gates.sh SUMMARY =====
  tool self-tests run: 12 / 12
  mode: full
ALL GATES PASSED
```
`RC=$?` read directly (never through a pipe): **0**. Independently counted: `grep -c "selftest
PASS:"` → 12; `grep -c "live gate PASS:"` → 5; `ls .planning/milestones/v1.34-artifacts/tools/*.py | wc -l` → 12 (no
scratch `.py` file was left under `tools/`).
