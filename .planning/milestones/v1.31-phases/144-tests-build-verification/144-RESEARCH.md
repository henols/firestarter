# Phase 144: Tests & Build Verification - Research

**Researched:** 2026-08-13
**Domain:** Test/gate authoring and build measurement across a dual-repo (PlatformIO C++ firmware + Python host CLI) tree
**Confidence:** HIGH — every anchor fact CONTEXT.md asserts was re-verified on disk this session; five numbered corrections found

> **This file is the canonical research for Phase 144.** Plans `144-01` … `144-07` cite its
> `C-0N` / `F-NN` / `Pitfall N` IDs; that ID space is authoritative and must not be renumbered.
> A later re-verification pass at the phase tip (after `144-01` landed) is recorded separately in
> `144-RESEARCH-REVERIFY.md` under its own `R-NN` / `A-NN` IDs. It **confirms** this document and
> adds measured figures — it does not supersede it. Two items there are worth reading before
> executing `144-03` and `144-05`: the 91 / 115 / 59 capture is now *measured* rather than
> predicted, and the cold native warning count against the zero-headroom 1166 watermark is the one
> figure neither pass measured.

## Summary

This is a **verification phase**, not a build phase. CONTEXT.md's 23 decisions are locked and unusually
concrete — file paths, line numbers, blob SHAs, measured byte counts, predicted capture totals. This
research does **not** re-derive them. It re-verifies the ground truth they rest on at the current tip,
and surfaces the mechanics a planner would otherwise get wrong.

**Headline: every load-bearing anchor CONTEXT.md cites is intact at the current tip.** The D-05 blob
SHA `ca3e09f1…` resolves; both `protocol_branch_inventory.json` pins (`cedc88dc…` / `5dffe841…`) match
`git rev-parse HEAD:<path>` exactly, so D-04's "green throughout" invariant is **not** pre-broken;
`size_baseline.json` holds 23954 / 24004 / 26016; the three `*_v131` env blocks are at `platformio.ini`
:293 / :331 / :373 as cited; the warning watermarks are 1166-with-zero-headroom on native and `== 0` on
all three AVR envs; `overprogram_factor` is `0` on all three shipped rows at `eprom_params.cpp:46-48`;
`compare_avr_policy_merge05` is at :214, `NATIVE_ENVS` at :100, `MERGE05_UNO_CLASS_FLASH_BAND` at :107.
Case counts are exactly 47 / 32 / 9 = 88, and the 88-vs-79 apparent conflict reconciles cleanly
(§Finding F-01). The firmware pytest suite is **292 passed, 0 failed** right now, and D-07's `885`
denominator is arithmetically confirmed by an independent parse (620 measured + 265 predicted).

**Five corrections** (C-01…C-05) were found. None reverses a decision; each is a stated-fact refinement
that would cost an executor a wasted plan cycle or a false-green gate if left uncorrected. The largest
is **C-01**: `size_baseline_v131.json` currently records only `native_trace_v131` among the three v131
envs, so D-13's "refresh" must *add* two env records, not merely update counts.

**Primary recommendation:** Author D-01's mapping gate and D-07's exhaustiveness gate as **pytest
modules under `firestarter/tests/`, never as `firestarter/scripts/check_*.py`** — the latter triggers
`test_checker_convention.py`'s seven-part convention against `FLOOR = 6` / `FIXTURE_FLOOR = 15`, both of
which sit at **exactly** the current count with zero headroom (F-08). Sequence every firmware file
creation behind a commit before running either repo's suite (D-20, F-09). Land D-05's rename, D-06's
new fixture and D-08's inventory rewrite in **one commit** (F-05).

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Native tests — TEST-01…05**

- **D-01:** **The deliverable is map + attest + fill gaps, not bulk re-authoring.** Phase 144 lands a machine-checked requirement→case mapping — a gate under `firestarter/tests/` that parses the v131 suite sources and asserts each `TEST-0N` names `RUN_TEST` cases which actually exist — and authors new cases only where a gap is named and proven. This follows H6 verbatim (`141-LOOP-RECORD.md` §12): TEST-01 owns "the requirement flip and the consolidated cross-phase accounting", not a second copy of behavior already proven. The risk this removes is specific: a requirement flipped against a case that was later renamed or deleted. A prose-only mapping table was rejected as the same shape as the hollow parity legs Phase 120 had to rebuild.

- **D-02:** **Evidence is ONE cold consolidated run, recorded verbatim.** Every v131 env is re-run at this phase's tip — `native_params_v131`, `native_loop_v131` (both its suites), `native_trace_v131` — alongside `native` and `native_nodevtools` at their pinned 141 cases / 17 suites. Citing the owning phases' recorded runs was rejected: no single run has ever exercised all 88 existing cases against the final tree, since Phase 141's cases have never run against 142's and 143's landed code together. A cross-phase interaction is exactly what this run exists to catch.

- **D-03:** **TEST-03 flips on the pure-function proof, with the in-loop wiring recorded as an explicit non-claim.** Reversed mid-discussion once the true cost was measured. `overprogram_factor` is `0` on every shipped row (`eprom_params.cpp:46-48`, asserted by `test_loop04_no_live_row_emits_an_overprogram_pulse`), so the overprogram path is structurally unreachable on live data; `eprom_overprogram_us` is proven directly by five cases from plan 141-08. An end-to-end synthetic-row oracle would need a params-table substitution, which needs either a seventh env or a seam in `src/` — and `eprom.cpp` **and** `eprom_params.cpp` are both blob-pinned by `firestarter/tests/golden/protocol_branch_inventory.json`, with `test_params_table_has_no_second_selector` separately asserting the table is switch-free. The operator chose the honest cheap option over paying that cost during a verification phase. **The non-claim must appear in the phase record:** the arithmetic is proven; the in-loop wiring on a live row is not, because no shipped row sets the factor.

- **D-04:** **No new native env, and no edit to any file under `firestarter/src/`.** D-03's reversal removes the only reason this phase had to touch a pinned source. Consequence, and it is a strong one: `eprom.cpp` and `eprom_params.cpp` keep their recorded blob SHAs (`cedc88dc…` / `5dffe841…`) all phase, so `tests/test_protocol_branch_inventory.py` and the D-13/D-18 golden stay **green throughout** — unlike Phases 141, 142 and 143, none of which could say that. A plan that finds itself needing an `src/` edit must stop and report, not absorb it.

**Trace freeze and diff — TEST-06**

- **D-05:** **The pre-change fixture survives by a pure rename, and is included by nothing.** `git mv firestarter/test/native/avr/_shared/eprom_v131_expected.h → eprom_v131_expected_prechange.h`, content byte-untouched. Because a git blob SHA is content-only and path-independent, `ca3e09f164e6e1c541ecb63d15bbebf5bce41d70` still matches after the move — Phase 138's "this artifact is untouched" proof survives intact instead of being re-derived. No TU `#include`s it, so it never compiles and cannot trip the zero-headroom native warning watermark (D-23). Keeping both array sets in one header was rejected because the file's blob SHA would necessarily change, destroying that proof.

- **D-06:** **The new fixture is captured fresh at THIS phase's tip — `141-NEW-TRACE.md`'s arrays are stale and must not be pasted.** That document holds a ready-to-paste dump at 91 / 119 / 59, but Phase 142 moved `0x08` from 119 → **115** (`142-VPP-RECORD.md` §3, F-142-04). Phase 143 added **zero** frames because `native_trace_v131` pins `millis()` to `AlwaysReturn(0)` (`143-HOST-RECORD.md` §7.3), so TEST-06 will find **zero** D-02-attributable strobes — that is a prediction to confirm, not to assume. Expected totals at capture: **91 / 115 / 59**. A deviation is stop-and-report.

- **D-07:** **Attribution is per-segment, backed by a machine-checked exhaustiveness gate.** Partition both streams into named segments (init, route assert, address set, pulse, verify read, teardown); table the per-segment old→new counts; attribute each delta to a named decision from Phases 140–143. A script asserts every one of the 885 entries (620 old + 265 new) falls into exactly one attributed segment — so "every changed strobe attributable to a named decision" is **machine-proven**, and an unattributed entry fails the gate. A full 900-row positional table was rejected as unreadable and error-prone at that volume; counts-plus-narrative was rejected as a blanket snapshot update wearing a paragraph, which is what TEST-06 forbids.

- **D-08:** **The inventory is re-pointed at the NEW fixture only — and the pre-change file is deliberately left un-gated.** `firestarter/tests/golden/eprom_v131_trace_inventory.json` gets fresh entry counts and blob SHA for `eprom_v131_expected.h`, keeping the six-assertion identity gate armed for v1.32. Its `meta.how_to_update` is binding: re-derive by independent parse, never hand-edit a count. **Named non-claim:** with a single record, nothing gate-asserts `eprom_v131_expected_prechange.h`. Its preserved blob SHA `ca3e09f1…` is cited in the phase record and stays verifiable by hand via `git rev-parse HEAD:<path>`, but it is not machine-checked. Record that as a gap, do not imply otherwise.

**Size baseline and MERGE-05 — TEST-08**

- **D-09:** **PREP-03 and `size_baseline.json` are the SAME anchor, and it is the authoritative one.** `scripts/baseline/size_baseline.json` still holds 23954 / 24004 / 26016 — exactly Phase 138's measured figures, which `138-BASELINE.md` §5 confirmed byte-identical. So TEST-08's "measured against the PREP-03 baseline" and the script's default seam agree. F-142-09's "two anchors disagree" is about `size_baseline_base01.json` (a v1.24 artifact) versus that anchor — it is **not** an ambiguity about which anchor TEST-08 means. Decided mechanically; no discussion needed. Measured tip: **24824 / 24874 / 26906**, i.e. **+870 / +870 / +890 B**, RAM unmoved on all three, `leonardo` at 93.8% with 1766 B headroom.

- **D-10:** **`size_baseline.json` IS rewritten to the v1.31 tip.** A dedicated commit whose message states every delta and its attributing phase. The everyday strict-identity gate goes GREEN and v1.32 drift becomes detectable again. The reasoning that decided it: a gate that is RED for a known accepted reason can no longer report an **unknown** one — a surprise regression in Phase 145 or 146 would look identical to the noise already showing. Record-only-and-defer was rejected because it leaves the gate blind for two more phases and hands measurement work to a phase scoped for docs and claims.

- **D-11:** **`size_baseline_base01.json` is ALSO re-anchored, and the band is repurposed as a forward tripwire.** Operator decision, taken with the tradeoff stated: re-anchoring ends MERGE-05's ability to make its original v1.24 comparison. What replaces it is coherent and deliberate — the `0 B` / `64 B` band literals stay, but now measure growth from **24824 / 24874 / 26906**, arming against Phases 145/146 and v1.32 instead of against a milestone that already shipped. `leonardo`'s 1766 B of headroom gains an actual guard. **MERGE-05's v1.24 semantics are retired; its forward mechanism is kept.** `MERGE05_UNO_CLASS_FLASH_BAND` is not widened.

- **D-12:** **The v1.24 content is not preserved in-tree — git history is enough.** Overwrite `size_baseline_base01.json` in place. The figures stay recoverable at the pre-change blob, and `138-BASELINE.md` §5 already records them in prose alongside the verdicts they produced. Consistent with D-10's plain rewrite; no new frozen files this phase.

- **D-13:** **`size_baseline_v131.json` is refreshed from the same consolidated run.** It was created as a running record of the envs no gate covers, so leaving it stale removes its only purpose. `native_loop_v131` has grown to 79 cases and `native_trace_v131`'s counts move when TEST-06 re-freezes. No live gate reads this file — F-138-05 forbids feeding a `*_v131` env name to either checker — so refreshing it cannot turn anything RED.

- **D-14:** **The re-anchor disclosure is MANDATORY and its wording is constrained.** Claude's call, not discussed, because the milestone's ethos settles it. If `--policy merge05` reads green after D-11, the phase record must say **green because the anchor moved to v1.31**, never *green because growth stayed inside the band*. An undisclosed re-anchor is precisely the overclaim Phase 146's claim gate exists to catch, and it would be this milestone committing its own anti-pattern. F-141-01's operator acceptance and the +204 B parameter-table mechanism are cited alongside. The honesty-ledger entry itself belongs to Phase 146 / CLOSE-02; **stating the fact** belongs here.

**Gate reach — TEST-07**

- **D-15:** **The three `*_v131` envs stay a local run-by-name obligation, recorded loudly.** No CI wiring. TEST-07's text names only `native`; wiring `build.yml` / `beta-build.yml` is a v1.32 infrastructure change, not a v1.31 test obligation. The standing F-140-11 position holds, and the milestone's habit is to name a hole rather than quietly widen scope to fill it. **Never imply CI covers these envs** — restate the absence in the phase record.

- **D-16:** **Constants parity is proven in BOTH directions, and the absent-path run must be a subprocess.** Run the parity legs locally where the sibling firmware repo is present and record the verbatim PASS; then re-run with `FIRESTARTER_FW_ROOT` pointed at an empty directory to prove the absent path skips cleanly rather than erroring. `tests/fw_presence.py` binds `FW_ROOT` / `FW_REPO_PRESENT` / `requires_fw` **at import**, and `pytest.mark.skipif` binds at collection, so `monkeypatch.setenv` has no effect — the second run MUST be a child process with the env var set (RESEARCH Correction C-15). This is the sweep that catches devcontainer-masked CI defects before a beta push. Adding a firmware checkout to app CI was rejected: it forces an unanswered question about which firmware ref to pin, and `beta` and the v1.31 branch disagree today.

- **D-17:** **The CAP-03 byte-layout parity gate IS built, in `firestarter_app/tests/`, behind `requires_fw` / `fw_path`.** F-143-07 / H2 names TEST-07 as its owner. It asserts the firmware `MSG_OK_READY` pack order `[buffer u16][hw_rev u8][ver_len u8][ver bytes][budget u16]` against the host's `_decode_id_frame` offsets, **including the computed `ver_end`** the budget is read at — never a fixed index. Rationale is concrete, not theoretical: BF-1 was a two-repo protocol with nothing comparing the sides, it went unnoticed for three milestones, and it made the v1.31 app refuse every connection to a v1.31 build. The app repo is the right home because every existing parity gate lives there and `fw_presence.py` is the sanctioned cross-repo probe.

- **D-18:** **Every new gate leg is seen RED on a planted violation before its GREEN is believed.** Carried unchanged from Phases 140/141/142/143 (D-25). Applies to D-01's mapping gate, D-07's exhaustiveness gate and D-17's layout gate. Each transcript captured verbatim in its plan's SUMMARY. A pre-authored leg can be **unreachable** — RED proves nothing until the leg has also been seen to pass for the right reason.

**Cross-cutting mechanics**

- **D-19:** **This phase is DUAL-REPO, and every plan declares `commits_land_in:`.** Firmware work (fixtures, baselines, the mapping and exhaustiveness gates) and host work (D-17's layout gate, the suite/ruff/mypy sweep) both land. A worktree leaves submodules empty and `files_modified` alone under-detects a submodule target — a plan that only *reads* a submodule breaks the same way.

- **D-20:** **Commit before running either repo's suite.** `firestarter/tests/test_flash_path_record_sync.py` asserts the **whole firmware repo's** `git status --porcelain` (F-141-11 / F-143-02), and `firestarter_app/tests/test_py32_flash_map_host.py` asserts `_git_porcelain(FW_ROOT) == ""` for the *sibling* firmware repo (F-143-03) — so an untracked file in `firestarter` turns the **host** suite RED. Both are recorded-not-fixed and will bite this phase repeatedly; sequence around them rather than rediscovering them.

- **D-21:** **Host-suite measurement uses the CI-parity interpreter, with addopts cleared.** `.venv/ci-replica/bin/python` (3.11) from inside `/workspaces/firestarter_app`, never the ambient 3.12 (`138-04-HOST-BASELINE.md`). Pass `-o addopts=""` — the repo's `addopts` is `-ra -q`, and doubling `-q` suppresses the count line the record needs. Last recorded state: 1578 tests at 82.92% coverage (Phase 143).

- **D-22:** **Never feed a `*_v131` env name to `check_size_baseline.py` or `check_build_warnings.py`.** F-138-05, measured: `check_size_baseline.py` hardcodes `NATIVE_ENVS = ("native", "native_nodevtools")` and `compare_native` does a bare dict lookup, so an unknown env raises an **uncaught `KeyError`** — exit 1, a false regression signal, not the documented exit-2 tool failure. `check_build_warnings.py` handles it cleanly at exit 2 but has no baseline entry either way.

- **D-23:** **Warning watermarks are unchanged and unforgiving.** `native` / `native_nodevtools` sit at exactly **1166 with zero headroom** (`<= 1166`), so any new warning in a native TU turns `check_build_warnings.py` RED. All three AVR envs are `== 0`. D-05's include-nothing rename is what keeps the renamed fixture from becoming a warning source.

### Claude's Discretion

An **index** of discretionary items, not a second definition site — each is defined in full above. The
IDs are deliberately unbolded here: a `- **D-NN**` bullet without a `:` or ` — ` inside the bold makes
the decision-coverage gate fail closed with `reason: could-not-parse`.

- D-03's reversal was offered as an operator choice once the seam cost was measured; the operator took
  the flip-with-non-claim option. The **wording** of that non-claim is Claude's.
- D-09 (which anchor is authoritative) and D-14 (the disclosure is mandatory) were decided by Claude
  from the evidence and the milestone's own standards, not asked.
- D-04's "no `src/` edit" is a *consequence* of D-03, recorded as an invariant so a plan cannot drift
  into one silently.
- The segment taxonomy in D-07 — the exact names and boundaries of the six segments, and the form of
  the exhaustiveness script's output. The binding constraint is that no entry may be unattributed.
- The mapping gate's parse strategy in D-01 (source-scan of `RUN_TEST` names versus a declared
  manifest), and whether it lives in one file or beside the existing golden-identity gates.
- Plan decomposition and wave structure, including which plan owns the firmware half and which owns
  the host half. The two are separable: D-17's host gate depends on no firmware change in this phase.
- Whether the phase record is `144-TEST-RECORD.md` or another name, and its section ordering.

### Deferred Ideas (OUT OF SCOPE)

- **Wiring the three `*_v131` envs into `build.yml` / `beta-build.yml`** — a real hole (F-140-11),
  deliberately left open by D-15. v1.32 infrastructure, not a v1.31 test obligation.
- **A firmware checkout in `firestarter_app`'s CI** so constants parity runs for real rather than
  skipping — blocked on deciding which firmware ref the app's CI should pin (D-16). Belongs with the
  above.
- **An end-to-end synthetic-row overprogram oracle** — D-03's reversed option. Reachable only via a
  seventh env with a substituted params TU, or a seam in blob-pinned `src/`. Revisit if a future row
  ever ships a non-zero `overprogram_factor`, which would make the path live rather than theoretical.
- **F-141-11 / F-143-02 / F-143-03: the unscoped whole-repo porcelain assertions** in
  `test_flash_path_record_sync.py` and `test_py32_flash_map_host.py`. Still unassigned and still
  recorded-not-fixed; D-20 works around them rather than fixing them here.
- **Gate-asserting `eprom_v131_expected_prechange.h`** — D-08 leaves it un-gated by choice. A second
  inventory record would close it.

</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description (verbatim, `REQUIREMENTS.md:228-243`) | Research Support |
|----|-------------|------------------|
| TEST-01 | Native tests prove `0x07`, `0x08` and `0x0B` each resolve to their own table row. | F-02 candidate map: `test_each_protocol_resolves_to_its_own_distinct_row` + `test_unknown_protocol_returns_null` + `test_row_values_match_the_frozen_table` — all three exist and pass |
| TEST-02 | Native tests prove fixed-width pulse/verify per byte and that the width does not escalate between attempts. | F-02: `test_loop01_pulse_width_never_grows_between_attempts` + 3 sibling `test_loop01_*` cases exist |
| TEST-03 | Native tests prove the overprogram duration derives from the successful byte's pulse count and honours `overprogram_cap_us`. | F-02: five `test_loop03_*` cases exist (exact count verified); D-03's structural-unreachability premise confirmed at `eprom_params.cpp:46-48` (F-04) |
| TEST-04 | Native tests prove max-pulse failure aborts the block, reports the address, and disables every high-voltage route. | F-02: `test_loop05_a_byte_that_misses_within_max_pulses_aborts_the_block`, `test_loop05_the_loops_own_strobes_disable_the_high_voltage_route`, `test_vpp02_x3/x4/e1` — all exist |
| TEST-05 | Native tests prove the `0xFF`/already-matching skips and the `pulse_delay == 0` fallback. | F-02: four `test_loop06_*` exist; **C-04** — "the two fallback cases" names no existing pair; there are three `*_zero_pulse_delay_takes_the_*us_fallback` + three `*_nonzero_pulse_delay_is_left_alone` |
| TEST-06 | Pre-change golden traces frozen, new traces authored, diff reviewed with every changed strobe attributable to a named decision — no blanket snapshot update. | F-05 (one-commit sequencing), F-06 (capture recipe verified), F-07 (segmentation design, 620+265=885 confirmed by independent parse) |
| TEST-07 | `uno`, `uno328pb`, `leonardo` and `native` all build and pass; host suite and CI-scoped ruff/mypy clean; dual-repo constants parity holds. | F-10 (CAP-03 byte offsets, both sides), F-11 (D-16 absent-path mechanic verified working), F-12 (exact CI commands + interpreter), C-02 |
| TEST-08 | Per-target flash and RAM delta measured against the PREP-03 baseline and recorded — Leonardo ceiling watched, not discovered at the end. | F-13 (all three baselines read; anchors confirmed), C-01, C-03, F-14 (checker CLI surface + how KeyError is actually reachable) |
</phase_requirements>

---

## Corrections

> Numbered so plans can cite them. **None reverses a locked decision.** Each is a stated-fact
> refinement that would cost an executor a wasted cycle or produce a false-green gate if left
> uncorrected. Adjudication is the planner's / operator's.

### C-01 — `size_baseline_v131.json` records only ONE of the three v131 envs; D-13's "refresh" must ADD two records

**CONTEXT.md D-13 implies** the file already carries `native_loop_v131` and `native_params_v131` counts
that have gone stale ("`native_loop_v131` has **grown** to 79 cases").

**Measured** `[VERIFIED: firestarter/scripts/baseline/size_baseline_v131.json]`:

```
native_envs keys:        ['native', 'native_nodevtools', 'native_pinmap_provisional', 'native_trace_v131']
warnings.native keys:    ['native', 'native_nodevtools', 'native_pinmap_provisional', 'native_trace_v131']
```

`native_loop_v131` and `native_params_v131` are **absent from both blocks**. `native_trace_v131` is
recorded at `{cases: 5, succeeded: 5, suites: 1, all_passed: true}`.

**Consequence for the plan:** D-13's task is *add two new env records + update one*, not *update three*.
It must also decide whether to add `warnings.native` entries for the two new envs (the file's own
convention, followed for `native_trace_v131`, is to record both blocks) — and if it does, it must
measure those two envs' cold warning counts, which no record currently holds.

**Cross-check** `[CITED: .planning/phases/141-per-byte-program-loop/141-NEW-TRACE.md §6]` — that
document records the two missing envs' counts **in prose only**, explicitly "never in a baseline JSON",
which is why they are absent. D-13 changes that policy; the plan should say so.

### C-02 — the four CI-scoped commands are at `ci.yml` :81 / :84 / :87 / :90, not ":80–:87"

**CONTEXT.md** cites `firestarter_app/.github/workflows/ci.yml` "(:80–:87)" for "ruff check / ruff
format --check / mypy watermark / pytest --cov".

**Measured** `[VERIFIED: firestarter_app/.github/workflows/ci.yml]`:

| Line | Command |
|---|---|
| :81 | `ruff check firestarter/ tests/` |
| :84 | `ruff format --check firestarter/ tests/` |
| :87 | `python tools/check_mypy_watermark.py` |
| :90 | `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` |

The `pytest --cov` leg is at **:90**, outside the cited range. Low impact, but a plan that quotes
":80–:87" as its scan target would omit the coverage floor from its own verification.

### C-03 — D-22's uncaught `KeyError` is *baseline-dependent*, not env-name-absolute; the rule needs restating to survive D-13

**CONTEXT.md D-22** states the mechanism as "an unknown env raises an uncaught `KeyError`".

**Measured** `[VERIFIED: firestarter/scripts/check_size_baseline.py]`. The mechanism is precisely:
`compare_native` does `rec = baseline["native_envs"][env]` — a bare subscript, no `.get()`, no
`try`/`except`. `KeyError` is not `ParseError`, and `main()` converts only `ParseError` to exit 2, so
the `KeyError` escapes as a traceback → **exit 1**. Confirmed exactly as D-22 says.

But the lookup is against **the selected baseline**, and the env name arrives via
`--native-log <env>=<path>`:

| Env fed as `--native-log` | vs default `size_baseline.json` | vs `size_baseline_base01.json` | vs `size_baseline_v131.json` |
|---|---|---|---|
| `native_trace_v131` | KeyError → exit 1 | KeyError → exit 1 | **present — compares cleanly** |
| `native_loop_v131` | KeyError | KeyError | KeyError |
| `native_params_v131` | KeyError | KeyError | KeyError |

Two consequences:

1. `--rebuild` iterates only `AVR_ENVS` and `NATIVE_ENVS`, so `--rebuild` can **never** reach a `*_v131`
   env. The hazard exists only via explicit `--native-log`.
2. **Once C-01's refresh lands, `native_loop_v131` and `native_params_v131` become feedable against
   `size_baseline_v131.json` too.** D-22's rule must therefore be restated as an *unconditional*
   operational prohibition ("never feed a `*_v131` env name to either checker, regardless of
   `--baseline`") or it will read as permission the moment D-13 completes. Recommend the
   unconditional form; it is what the `platformio.ini` caveat blocks already say.

`check_build_warnings.py` confirmed clean: `check_env` raises `ParseError` when the env is in neither
`warnings.avr` nor `warnings.native` → exit 2, documented tool failure. ✓ as D-22 states.

### C-04 — TEST-05's "the two fallback cases" names no existing pair

**CONTEXT.md `<code_context>`** nominates, for TEST-05: "the four `test_loop06_*` and **the two
fallback cases**".

**Measured** `[VERIFIED: firestarter/test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp]`
— there are **six** fallback-adjacent cases, in two families of three:

```
test_0x07_zero_pulse_delay_takes_the_1000us_fallback
test_0x08_zero_pulse_delay_takes_the_100us_fallback
test_0x0B_zero_pulse_delay_takes_the_500us_fallback
test_0x07_nonzero_pulse_delay_is_left_alone
test_0x08_nonzero_pulse_delay_is_left_alone
test_0x0B_nonzero_pulse_delay_is_left_alone
```

No pair of two. **This is exactly the defect class D-01's mapping gate exists to catch**, arriving in
CONTEXT.md's own prose — which is a point worth making in the phase record rather than quietly fixing.
The plan must name TEST-05's cases explicitly. Recommended (all six, plus the four skips):
`test_loop06_*` ×4 + `test_0x{07,08,0B}_zero_pulse_delay_takes_the_*us_fallback` ×3 +
`test_0x{07,08,0B}_nonzero_pulse_delay_is_left_alone` ×3 — the second family is the non-vacuity half
(a fallback that fired unconditionally would pass the first three and fail these).

### C-05 — `test_trace_eprom_v131` has SIX `RUN_TEST` invocations, of which one is `#ifdef`-guarded

**Measured** `[VERIFIED: test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:383-393]` — six
`RUN_TEST(` sites; the sixth, `RUN_TEST(test_dump_v131_traces)`, sits inside
`#ifdef EPROM_V131_TRACE_DUMP`, which **no env defines**. The default-build count is therefore 5, which
is what `size_baseline_v131.json` records and what `141-NEW-TRACE.md` §6 states.

**Consequence:** a naive `grep -c 'RUN_TEST('` mapping gate would report 6 for this suite. The three
suites D-01 actually maps (`test_loop_eprom_v131` 47, `test_vpp_eprom_v131` 32,
`test_eprom_params_v131` 9) contain **zero** guarded or commented-out `RUN_TEST` sites (verified), so
the parse is safe for them — but the gate must either exclude `test_trace_eprom_v131` or strip
preprocessor-guarded regions. State which. See F-03 for the full parse-tolerance spec.

---

## Anchor Verification Ledger

> Every fact CONTEXT.md's decisions rest on, re-checked on disk this session. Cite these as `F-00`.

| CONTEXT.md claim | Verified value | Verdict |
|---|---|---|
| D-05: `test/native/avr/_shared/eprom_v131_expected.h` exists, blob `ca3e09f164e6e1c541ecb63d15bbebf5bce41d70` | `git rev-parse HEAD:<path>` → `ca3e09f164e6e1c541ecb63d15bbebf5bce41d70` (649 lines, 38528 B) | ✅ EXACT |
| D-04: `protocol_branch_inventory.json` pins `src/proms/eprom.cpp` = `cedc88dc…` | `HEAD:` blob = `cedc88dc20936d0749f03572551b0621063ae930`; working tree `hash-object` identical | ✅ **not pre-broken** |
| D-04: pins `src/proms/eprom_params.cpp` = `5dffe841…` | `HEAD:` blob = `5dffe841aeb7013f9f53e9991a6248b203ae22da`; working tree identical | ✅ **not pre-broken** |
| D-09: `size_baseline.json` holds 23954 / 24004 / 26016 | `avr_targets.{uno,uno328pb,leonardo}.flash_used` = 23954 / 24004 / 26016 | ✅ EXACT |
| D-09: measured tip 24824 / 24874 / 26906, +870/+870/+890, leonardo 93.8%, 1766 B headroom | `143-HOST-RECORD.md` :227-248 reproduces all six figures | ✅ EXACT |
| D-22: `NATIVE_ENVS` at :100 | `check_size_baseline.py:100` — `NATIVE_ENVS = ("native", "native_nodevtools")` | ✅ EXACT |
| D-11: `MERGE05_UNO_CLASS_FLASH_BAND` at :107 | `check_size_baseline.py:107` — `= 64` | ✅ EXACT |
| D-11: `compare_avr_policy_merge05` at :214 | `check_size_baseline.py:214` — `def compare_avr_policy_merge05` | ✅ EXACT |
| D-22: `compare_native` bare dict lookup → uncaught `KeyError` | `rec = baseline["native_envs"][env]`; `main()` catches only `ParseError` | ✅ CONFIRMED (see C-03 for the qualifier) |
| D-15/D-22: three `*_v131` env blocks at `platformio.ini` :293 / :331 / :373 | `[env:native_trace_v131]`=293, `[env:native_params_v131]`=331, `[env:native_loop_v131]`=373 | ✅ EXACT |
| D-23: `native`/`native_nodevtools` watermark 1166, zero headroom | `warnings.native.{native,native_nodevtools}.total_watermark` = 1166; `policy.native_rule` = `"<= total_watermark"` | ✅ EXACT |
| D-23: all three AVR envs `== 0` | `warnings.avr.*` = `{macro_redefinition: 0, total: 0}`; `policy.avr_rule` = `"== 0"` | ✅ EXACT |
| D-03: `overprogram_factor` is `0` on every shipped row, `eprom_params.cpp:46-48` | Rows at :50/:51/:52; 4th struct field = `0` on all three | ✅ EXACT |
| D-03: `test_loop04_no_live_row_emits_an_overprogram_pulse` exists | present in `test_loop_eprom_v131.cpp` | ✅ |
| D-03/D-04: `test_params_table_has_no_second_selector` exists | `tests/test_protocol_branch_inventory.py:495` | ✅ |
| D-06: `native_trace_v131` pins `millis()` to `AlwaysReturn(0)` | `test_trace_eprom_v131.cpp:92` — `When(Method(ArduinoFake(), millis)).AlwaysReturn(0)` | ✅ EXACT (see F-06 for a *second* independent reason) |
| D-06: `141-NEW-TRACE.md` is stale at 91/119/59 | banners at :47-49 read `total=91` / `total=119` / `total=59` | ✅ stale confirmed |
| D-06: 0x08 moved 119 → 115 | `142-VPP-RECORD.md:210` — `0x08 \| 119 \| 119 \| **115** (−4 …)` | ✅ EXACT |
| D-01: suites at 47 / 32 / 9 = 88 | `RUN_TEST(` counts: 47 / 32 / 9 (all unique, all unguarded) | ✅ EXACT |
| D-13: `native_loop_v131` "has grown to 79 cases" | its `test_filter` names 2 suites → 47 + 32 = **79** | ✅ EXACT (see F-01) |
| D-02: `native`/`native_nodevtools` pinned at 141 cases / 17 suites | both `test_filter` blocks = 17 entries; baseline `native_envs` = 141/17 | ✅ EXACT |
| D-08: `eprom_v131_trace_inventory.json` records 198 / 221 / 201 | `arrays` = `[{07,198},{08,221},{0B,201}]`; `meta.blob_sha` = `ca3e09f1…` | ✅ EXACT |
| D-08: inventory `meta.how_to_update` is binding | verbatim in F-05 below | ✅ |
| D-21: `.venv/ci-replica/bin/python` is 3.11 | symlink → `python3.11`; `--version` → **Python 3.11.15** | ✅ EXACT |
| D-21: repo `addopts` is `-ra -q` | `pyproject.toml:107` — `addopts = "-ra -q"` | ✅ EXACT |
| D-21: host baseline 1578 tests / 82.92% | `143-HOST-RECORD.md:405-406` | ✅ EXACT |
| D-20: firmware whole-repo porcelain assertion | `test_flash_path_record_sync.py:1247` | ✅ (see F-09) |
| D-20: host asserts `_git_porcelain(FW_ROOT) == ""` | `test_py32_flash_map_host.py:391` | ✅ (see F-09) |
| D-16: `fw_path` at :117 | `fw_presence.py:117` — `def fw_path(*parts: str) -> Path` | ✅ EXACT |
| D-17 template: `FIRMWARE_HEADER` at :148 | `test_revision_constants_parity.py:148` | ✅ EXACT |
| D-18 template: planted fixtures at :728+ | `_FIXTURES_DIR` at :727, three `_FIXTURE_*` at :728-730, three planted legs from :733 | ✅ EXACT |
| D-07: 885 = 620 old + 265 new | independent parse of the fixture → **620** (198+221+201); 91+115+59 = **265**; 620+265 = **885** | ✅ ARITHMETIC CONFIRMED |

**Additional baseline datum (not in CONTEXT.md, useful to the plan):** the firmware pytest suite is
**292 passed, 0 failed** at the current tip (`python3 -m pytest tests/ -q`, 13.7 s). That is the number
D-04's "green throughout" invariant must preserve, and the number a plan's own verification should
compare against.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Requirement→case mapping (D-01) | Firmware repo `tests/` (pytest, host-side static analysis) | — | Parses `test/native/avr/**/*.cpp` text. No compilation, no firmware behavior. Lives with the other source-scanning gates. |
| Trace fixture rename (D-05) | Firmware repo `test/native/avr/_shared/` (git plumbing) | — | Pure `git mv`; no tier consumes the renamed file. |
| Trace capture (D-06) | Firmware repo native build (PlatformIO `native_trace_v131` + direct binary invocation) | — | Requires a compiled host binary; `pio test` cannot deliver it (swallows `printf`). |
| Segment exhaustiveness (D-07) | Firmware repo `tests/` (pytest, static parse of two C headers) | — | Both streams are literal C arrays; a Python parse is the right tool. Never needs a build. |
| Golden inventory re-point (D-08) | Firmware repo `tests/golden/` (JSON data) | Firmware `tests/` (the gate that reads it) | Data + its gate must move together (one-commit property, F-05). |
| Size/RAM measurement + re-anchor (D-09…D-14) | Firmware repo AVR builds (`pio run -e uno/uno328pb/leonardo`) | Firmware `scripts/baseline/` (JSON) | Measurement is a build-tier activity; the record is data. `check_size_baseline.py` itself is **not** modified. |
| Constants parity sweep (D-16) | Host repo `tests/` (pytest, cross-repo read via `fw_presence`) | Firmware repo (read-only scan target) | Every existing parity gate lives host-side; `fw_presence.py` is the sanctioned probe. |
| CAP-03 byte-layout parity (D-17) | Host repo `tests/` (pytest) | Firmware `src/firestarter.cpp` (read-only scan target) | Compares a firmware source-text pack order against the host decoder's live offsets. Host repo is the only place both sides are reachable. |
| CI-scoped lint/type/coverage (TEST-07) | Host repo tooling (`ruff`, `mypy` watermark, `pytest --cov`) | — | Commands are fixed by `ci.yml`; parity requires the 3.11 replica interpreter. |

---

## Standard Stack

No new dependency is introduced by this phase. Everything below is already installed and in use.

### Core

| Tool | Version | Purpose | Why Standard |
|---|---|---|---|
| pytest | (repo-pinned, both repos) | Every gate in this phase is a pytest module | 292 firmware + 1578 host tests already run on it |
| PlatformIO Core | 6.1.19 `[CITED: size_baseline.json meta.platformio_core]` | Builds/runs the AVR + native envs | Sole build system for firmware |
| Unity (via PlatformIO `test_framework`) | bundled | The native `RUN_TEST` suites D-01 maps | All 88 v131 cases already use it |
| ArduinoFake | `^0.4.0` `[VERIFIED: platformio.ini lib_deps]` | Host-side mocking of `millis()`/`Serial` in native envs | The `AlwaysReturn(0)` pin D-06 depends on |
| `.venv/ci-replica/bin/python` | **3.11.15** `[VERIFIED: --version]` | CI-parity host-suite interpreter (D-21) | Ambient 3.12 masks CI defects (py39/3.11 target) |
| ruff | (repo-pinned) | `ruff check` + `ruff format --check`, scoped `firestarter/ tests/` | Exact CI commands, C-02 |
| mypy (via `tools/check_mypy_watermark.py`) | watermark **35** `[VERIFIED: pyproject.toml:174]` | Type-error watermark gate | `# mypy_error_watermark = 35` parsed by regex from a comment line |

### Supporting

| Tool | Purpose | When to Use |
|---|---|---|
| `git rev-parse HEAD:<path>` | Committed blob identity (D-05, D-08) | Reads the **committed** blob, never the worktree — this is why F-05's one-commit rule binds |
| `git hash-object <path>` | Worktree blob identity | Pre-staging prediction of a blob SHA (the pattern `protocol_branch_inventory.json` documents) |
| `scripts/check_size_baseline.py` | TEST-08's measurement gate | `--avr-log env=path` / `--native-log env=path` / `--rebuild` / `--baseline` / `--policy merge05` |
| `scripts/check_build_warnings.py` | Warning watermark gate (D-23) | Same env-name discipline; exits 2 cleanly on unknown env |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|---|---|---|
| pytest module under `firestarter/tests/` for D-01/D-07 | `firestarter/scripts/check_*.py` | **Strongly disrecommended** — triggers `test_checker_convention.py`'s seven requirements at zero-headroom floors. See F-08. |
| Source-scanning `RUN_TEST` names (D-01) | A committed manifest JSON the suites must match | A manifest is a second hand-maintained site — the exact drift class D-01 exists to catch. Source-scan is correct; see F-03 for the parse spec. |
| Per-entry field classification (D-07) | Positional state machine over the merged stream | Per-entry alone **cannot** separate "pulse" from "verify read" (both are CE strobes). A state machine keyed on the `OUTPUT_ENABLE` toggle is required. See F-07. |

**Installation:** none. No `npm install`, `pip install` or `lib_deps` addition is required by this phase.

## Package Legitimacy Audit

**Not applicable — this phase installs zero external packages.** Every tool it uses is already present
in both repos and already exercised by 292 + 1578 existing tests. No registry lookup, no slopcheck run,
and no `checkpoint:human-verify` install gate is needed. If a plan proposes adding a dependency, that is
a scope deviation to report, not to absorb.

---

## Findings

### F-01 — The 88-vs-79 apparent conflict reconciles exactly; no correction needed

CONTEXT.md says "**88** existing v131 native cases" (`<code_context>`) and "`native_loop_v131` has grown
to **79** cases" (D-13). Both are right, and they are counting different things:

| Env | Suites in its `test_filter` | Cases |
|---|---|---|
| `native_loop_v131` | `test_loop_eprom_v131` + `test_vpp_eprom_v131` | 47 + 32 = **79** |
| `native_params_v131` | `test_eprom_params_v131` | **9** |
| **Total across the two envs D-01 maps** | 3 suites | **88** |
| `native_trace_v131` | `test_trace_eprom_v131` | 5 (6 with `-D EPROM_V131_TRACE_DUMP` — C-05) |

All verified `[VERIFIED: platformio.ini test_filter blocks; RUN_TEST counts]`. **88 is the mapping
denominator; 79 is a per-env run figure.** A plan should use both, labelled, and never add them.

Provenance note: `firestarter/CLAUDE.md` still documents `native_loop_v131` as "**71 cases total**"
(39 + 32, "plan 142-05's tip"). That is stale by 8 cases against the measured 79. It is documentation,
not a gate, and Phase 146 owns doc reconciliation — but a plan that quotes CLAUDE.md rather than
measuring will be wrong. `[VERIFIED: firestarter/CLAUDE.md "Phase 142 addition" block vs measured 47+32]`

### F-02 — Candidate TEST-01…05 → case-name map; every nominated case exists except C-04's phantom pair

All names below were extracted programmatically from the three suites and cross-checked against
CONTEXT.md's `<code_context>` nominations. **Every nominated case exists under its stated name except
TEST-05's "two fallback cases" (C-04).**

| Req | Suite | Cases (verified to exist) | Count |
|---|---|---|---|
| TEST-01 | `test_eprom_params_v131` | `test_each_protocol_resolves_to_its_own_distinct_row`, `test_unknown_protocol_returns_null`, `test_row_values_match_the_frozen_table` | 3 |
| TEST-02 | `test_loop_eprom_v131` | `test_loop01_pulse_width_never_grows_between_attempts`, `test_loop01_each_byte_gets_exactly_the_seeded_number_of_fixed_width_pulses`, `test_loop01_verify_read_follows_every_pulse`, `test_loop01_a_byte_that_converges_on_its_last_permitted_pulse_succeeds` | 4 |
| TEST-03 | `test_loop_eprom_v131` | `test_loop03_overprogram_duration_is_three_times_the_pulse_count_times_the_width`, `test_loop03_overprogram_is_zero_when_the_factor_is_zero`, `test_loop03_overprogram_clamps_at_the_cap_rather_than_refusing`, `test_loop03_overprogram_is_32_bit_safe_at_the_uint16_ceiling`, `test_loop03_a_zero_cap_yields_no_overprogram_pulse` — **exactly the "five cases from plan 141-08"** D-03 cites; plus `test_loop04_no_live_row_emits_an_overprogram_pulse` as the structural-unreachability witness | 5 (+1) |
| TEST-04 | `test_loop_eprom_v131` + `test_vpp_eprom_v131` | `test_loop05_a_byte_that_misses_within_max_pulses_aborts_the_block`, `test_loop05_the_loops_own_strobes_disable_the_high_voltage_route`, `test_loop05_a_successful_block_does_not_disable_the_route` (the non-vacuity half), `test_vpp02_x3_the_energy_cap_exit_disables_the_route`, `test_vpp02_x4_the_final_pass_verify_failure_disables_the_route`, `test_vpp02_e1_write_init_error_exit_leaves_no_route_asserted` | 6 |
| TEST-05 | `test_loop_eprom_v131` + `test_eprom_params_v131` | `test_loop06_an_ff_target_byte_is_never_read_and_never_pulsed`, `test_loop06_an_already_matching_byte_is_read_once_and_never_pulsed`, `test_loop06_a_block_of_only_skipped_bytes_emits_no_pulse_at_all`, `test_loop06_the_ff_rule_does_not_suppress_the_final_verify_pass` + the **six** params cases named in C-04 | 4 + 6 |

**Gap analysis (D-01's "authors new cases only where a gap is named and proven"):** no TEST-01…05
requirement is left without a named, existing, currently-passing case. On the evidence, **the honest
finding is that no new native case is required**. If a plan authors one anyway it must first name the
gap and prove it — which per D-01 is the bar, not a formality.

One reachability note for the record: TEST-04's "reports the address" clause is satisfied by the
asserted `u24 address + u8 pulse count` payload inside
`test_loop05_a_byte_that_misses_within_max_pulses_aborts_the_block` (CONTEXT.md's own framing). The
plan should cite the assertion, not just the case name, or the mapping gate proves only that a name
exists.

### F-03 — Parse specification for D-01's mapping gate

**Files a source-scanning parse must read** (exactly three; `host_stubs.cpp` in each directory contains
zero `RUN_TEST` — verified):

```
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp      (47 RUN_TEST)
test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp        (32 RUN_TEST)
test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp  ( 9 RUN_TEST)
```

**What the parse must tolerate — measured, not assumed:**

| Hazard | Present in the three mapped suites? | Required handling |
|---|---|---|
| `#if` / `#ifdef`-guarded `RUN_TEST` | **No** (0 occurrences) — but **yes** in `test_trace_eprom_v131` (C-05) | Either scope the gate to the three suites, or strip guarded regions. Do not silently include the trace suite. |
| Commented-out `RUN_TEST` | **No** (`anchored == any == total` for all three) | Strip `/*…*/` and `//…` before matching anyway — the precedent `_parse_arrays` in `test_golden_trace_identity_eprom_v131.py:140-141` does exactly this |
| Macro line-wrapping (`RUN_TEST(\n  name)`) | **No** — all 88 match `^\s*RUN_TEST\([A-Za-z0-9_]+\)` on one line | Use `RUN_TEST\(\s*([A-Za-z0-9_]+)\s*\)` with `re.S` tolerance so a future wrap does not silently drop a case |
| `RUN_TEST` inside a helper function | **No** — all 88 are in `main()` | Do not assume; a name found anywhere still proves the name exists, which is the assertion |
| Duplicate names | **No** — unique counts equal total counts in all three | Assert uniqueness; a duplicate would inflate a count |
| `RUN_TEST` appearing in a comment or docstring | 2 comment mentions of `RUN_TEST` exist in the repo, both in JSON prose (`size_baseline*.json`), none in the three `.cpp` files | Comment-stripping covers it |

**Non-vacuity is mandatory** (house pattern, every existing source-scan gate has it): assert the
extracted set is non-empty **and** that its size is `>= 88`, with the floor as a hardcoded literal, so a
mis-globbed or emptied parse fails loudly instead of making every `TEST-0N in extracted_names` check
pass over an empty set. This is the same shape as `test_checker_convention.py`'s `FLOOR` and
`test_golden_trace_identity_eprom_v131.py::test_inventory_is_non_vacuous`.

**Planted-violation seam (D-18):** follow the established convention exactly — a module-level
`Path(os.environ.get("FIRESTARTER_<NAME>_SCAN_<TARGET>", str(_REPO_ROOT / _REL)))` that **binds at
import**, so the planted run must be a child process with the env var set. Precedents, all verified:

```
tests/test_write_path_source_contract_v131.py:150    FIRESTARTER_WRITE_PATH_SCAN_SOURCE
tests/test_hv_routing_source_contract_v142.py:200    FIRESTARTER_HV_SCAN_DISPATCH_SOURCE
tests/test_progress_emission_is_leonardo_only.py:206 FIRESTARTER_PROGRESS_SCAN_EPROM_SOURCE
tests/test_ack_layout_source_contract_v143.py        FIRESTARTER_ACK_SCAN_DISPATCH_SOURCE
```

**No in-repo precedent parses `RUN_TEST` names.** D-01 introduces a new pattern; the four modules above
are the structural template (seam, non-vacuity, concatenation-built needles, no-skip self-check), not a
functional one.

### F-04 — D-03's structural-unreachability premise is exactly true, and the struct field is unambiguous

`[VERIFIED: firestarter/src/proms/eprom_params.cpp:45-49]`

```
static const eprom_params_t EPROM_PARAMS[] PROGMEM = {
    /* 0x07 */ { 75000UL, 0UL,     25,  0, VERIFY_PER_PULSE_PLUS_FINAL, VPP_PATH_DROP_RESISTOR },
    /* 0x08 */ { 75000UL, 0UL,     25,  0, VERIFY_PER_PULSE_PLUS_FINAL, VPP_PATH_DROP_RESISTOR },
    /* 0x0B */ { 75000UL, 50000UL, 255, 0, VERIFY_PER_PULSE,            VPP_PATH_DIRECT_VPE    },
};
```

The 4th positional field is `0` on all three rows. `eprom_params_for()` returns `NULL` for an
unrecognised protocol (fail-closed, D-05 of Phase 140) — not `&EPROM_PARAMS[0]`. So no shipped row can
reach the overprogram path, and there is no fallback row that could. D-03's non-claim wording is
therefore accurate as written: **the arithmetic is proven; the in-loop wiring on a live row is not,
because no shipped row sets the factor.**

### F-05 — D-05 + D-06 + D-08 MUST land in ONE commit or the identity gate is transiently RED

This is the single highest-risk sequencing hazard in the phase.

`tests/test_golden_trace_identity_eprom_v131.py` hardcodes:

```
_FIXTURE_PATH = "test/native/avr/_shared/eprom_v131_expected.h"
_CONSUMERS    = (… / "test_trace_eprom_v131" / "test_trace_eprom_v131.cpp",)
```

and `test_blob_sha_matches_the_recorded_inventory` compares
`git rev-parse HEAD:test/native/avr/_shared/eprom_v131_expected.h` against `meta.blob_sha`. Because it
reads **`HEAD:`, not the worktree**, the gate's state is a function of what is *committed*:

| Commit state | `git rev-parse HEAD:<path>` | Gate verdict |
|---|---|---|
| Now | `ca3e09f1…` = recorded | GREEN |
| After D-05's `git mv` alone | path absent → `git rev-parse` exits non-zero → `_git`'s `assert result.returncode == 0` fires | **FAIL (not skip)** |
| After D-05 + D-06 but not D-08 | new fixture's SHA ≠ `ca3e09f1…` | **FAIL** |
| After D-05 + D-06 + D-08 in one commit | new SHA = newly recorded SHA | GREEN |

Two further couplings, both verified:

- The new fixture **must take the old name**, because `_FIXTURE_PATH` and
  `test_consuming_suites_still_include_the_fixture` both hardcode
  `_shared/eprom_v131_expected.h`, and `test_trace_eprom_v131.cpp:45` is
  `#include "../_shared/eprom_v131_expected.h"`. D-05/D-06 already do this; the plan must not "helpfully"
  rename the new one.
- D-08's inventory rewrite carries the **chicken-and-egg** the repo already has a documented pattern
  for: the recorded `blob_sha` must be the SHA the new fixture *will have once committed*. Use
  `git hash-object <path>` on the worktree file **before staging**, exactly as
  `protocol_branch_inventory.json`'s own `recorded_by` note documents for Phases 142/143. Then
  `recorded_at_head` names the commit's **parent** — the deliberate one-commit offset, not a mistake.

`meta.how_to_update` is binding and reads, verbatim:

> "If this file legitimately changes, re-derive this inventory from the file with an independent parse
> (never hand-edit the numbers) AND state in the commit message which array changed and why -- never
> edit this JSON merely to make a surprise disappear."

**D-05's include-nothing claim is confirmed.** Exactly one `#include` of the fixture exists repo-wide
(`test_trace_eprom_v131.cpp:45`). The two other textual references —
`test/native/avr/_shared/host_stubs_common.inc:162` and
`test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:70` — are **comments**, and both remain
factually correct after the rename because the new fixture keeps the old name. The renamed
`eprom_v131_expected_prechange.h` sits in `_shared/`, which is reached only by relative `../_shared/…`
includes, so an unincluded header there compiles in no TU and cannot contribute a warning (D-23). ✅

### F-06 — D-06's capture mechanics, exact and verified

**Where the helper is:** `dump_v131_merged_ready_to_paste` at
`test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:351`, called by
`test_dump_v131_traces` (:363) which is registered at :392 behind `#ifdef EPROM_V131_TRACE_DUMP`.
**No env defines that macro** — it must come from the environment.

**Output form** (`:358`) — one entry per line, already paste-shaped, with a positional index comment:

```
    {%d, 0x%02X, 0x%02X, %luUL}, /* %d */
```

preceded per array by a banner (`:353`):

```
##### <TAG> total=<n> strobe_overflow=<0|1> timing_overflow=<0|1>
```

**Exact command sequence** `[CITED: 141-NEW-TRACE.md §1, re-verified against the source]`:

```bash
# 1. Build WITH the dump macro. --without-testing so pio does not run+swallow it.
cd /workspaces/firestarter && PLATFORMIO_BUILD_FLAGS="-D EPROM_V131_TRACE_DUMP" \
  pio test -e native_trace_v131 --without-testing

# 2. Run the built binary DIRECTLY — `pio test` swallows printf (comment at :346)
cd /workspaces/firestarter && .pio/build/native_trace_v131/firestarter_native

# 3. Confirm the RED's shape via the normal (no-dump) invocation
cd /workspaces/firestarter && pio test -e native_trace_v131
```

**Three mechanics a plan must specify or an executor will get a stale/wrong capture:**

1. **cwd is load-bearing.** Every `pio` invocation must run with cwd `/workspaces/firestarter`. A
   gitignored root `platformio.ini` exists at `/workspaces/platformio.ini` carrying two `[platformio]`
   sections, and `pio -d <dir>` does **not** work around it. `[VERIFIED: /workspaces/platformio.ini exists, 11776 B; CITED: 141-NEW-TRACE.md §1]`
2. **Stale-binary hazard.** `.pio/build/native_trace_v131/` may hold a binary built *without* the dump
   macro (or from an older tree). Step 1 changes `build_flags` via `PLATFORMIO_BUILD_FLAGS`, which
   PlatformIO treats as a rebuild trigger — but the safe, self-evidencing form is
   `rm -rf .pio/build/native_trace_v131` first, which also makes the run a **cold** build (the same
   discipline `size_baseline.json`'s `meta.warm_vs_cold_correction` mandates for every watermark
   figure). Recommend the plan require it.
3. **Real-capture vs stale-paste discriminator.** Three independent tells, all cheap:
   - the dump build's Unity summary reads **`6 test cases: 3 failed, 2 succeeded`** (the 6th being the
     dump case, C-05) whereas the no-dump run reads `5 test cases: 3 failed, 2 succeeded`;
   - the banner totals must be **91 / 115 / 59** — and `141-NEW-TRACE.md`'s pasteable arrays are
     **91 / 119 / 59**, so a `0x08` total of 119 is *positive proof of a stale paste*;
   - `strobe_overflow=0 timing_overflow=0` on all three (caps are 512 each —
     `HOST_STUBS_MAX_STROBES`/`HOST_STUBS_MAX_TIMINGS` at `host_stubs_common.inc:102`/`:168`; 115 is
     22% of cap, ample headroom).

**D-06's zero-added-frames prediction has a SECOND independent basis, which strengthens it.** D-06
cites `millis()` pinned to `AlwaysReturn(0)` (`test_trace_eprom_v131.cpp:92`) — verified, and the guard
at `eprom.cpp:399` is `if ((uint32_t)(millis() - last_emit_ms) >= EPROM_PROGRESS_EMIT_INTERVAL_MS)` with
`last_emit_ms = millis()` at `:327`, so `0 - 0 = 0 >= 1000` is false forever. But independently: the
progress emit is a **serial frame** (`LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, …)` at `:401`), and the
recorders capture only register strobes (`STROBE_KIND_DATA`/`STROBE_KIND_PIN`) and `delay`/
`delayMicroseconds` timings — **never `Serial` writes**. So even an advancing clock could not add a
trace entry. Report both reasons; the prediction is robust, and saying why is more honest than "as
predicted."

### F-07 — D-07's exhaustiveness gate: the arithmetic is confirmed, and the segmentation needs a state machine, not a field lookup

**Arithmetic — independently re-derived, confirmed:**

| Array | Recorded (inventory) | My independent parse | ✓ |
|---|---|---|---|
| `EPROM_V131_TRACE_PROTO_07` | 198 | 198 | ✓ |
| `EPROM_V131_TRACE_PROTO_08` | 221 | 221 | ✓ |
| `EPROM_V131_TRACE_PROTO_0B` | 201 | 201 | ✓ |
| **pre-change total** | **620** | **620** | ✓ |
| new predicted (D-06) | 91 + 115 + 59 = 265 | — | ✓ |
| **D-07 denominator** | **885** | 620 + 265 = **885** | ✓ |

**Entry shape** (`eprom_v131_expected.h:77-91`) — a flat 4-tuple, no nesting:

```c
typedef struct { uint8_t kind; uint8_t pin; uint8_t value; uint32_t us; } v131_trace_entry_t;
#define STROBE_KIND_DATA 1  /* pin=0, value = byte written to the data buffer, us=0 */
#define STROBE_KIND_PIN  2  /* pin = latch/strobe pin, value = 0|1,           us=0 */
#define TIMING_KIND_DELAY_US 3  /* pin=value=0, us = delayMicroseconds arg */
#define TIMING_KIND_DELAY_MS 4  /* pin=value=0, us = delay arg              */
```

`_ENTRY_RE = re.compile(r"\{[^{}]*\}")` (the existing gate's counter,
`test_golden_trace_identity_eprom_v131.py:88`) is safe because entries never nest. A stricter parse
that captures the four fields is what D-07 needs:
`\{\s*(\d+)\s*,\s*(0x[0-9A-Fa-f]+)\s*,\s*(0x[0-9A-Fa-f]+)\s*,\s*(\d+)UL\s*\}` — verified to match all
620 entries with zero misses.

**Register/pin identity IS fully recoverable from an entry** `[VERIFIED: include/rurp_shield.h:53-57]`:

| `pin` | Constant | Role in the stream |
|---|---|---|
| `0x01` | `LEAST_SIGNIFICANT_BYTE` | LSB address latch |
| `0x02` | `MOST_SIGNIFICANT_BYTE` | MSB address latch |
| `0x04` | `OUTPUT_ENABLE` | **the program-vs-verify discriminator** |
| `0x08` | `CONTROL_REGISTER` | HV route / A16-A17 latch; its `value` carries the route bits |
| `0x20` | `CHIP_ENABLE` | the pulse strobe and the verify-read strobe |

The idiom is a 4-entry latch group: `{1,0x00,V,0}` (data) → `{2,PIN,1,0}` (LE high) → `{3,0,0,1}`
(the 1 µs post-latch settle from `rurp_internal_write_to_register`) → `{2,PIN,0,0}` (LE low). Elided
latches (register-cache hit, `rurp_register_utils.h:24-38` early `return`) contribute **nothing** — the
stream is the physical truth, which is why a raw call-log golden would be wrong.

One nuance for the segmentation author: the recorded control `value` is **post-mapping and 8-bit**.
`rurp_write_to_register` applies `rurp_map_ctrl_reg_for_hardware_revision(data)` before the strobe
(`:47`), and `native` compiles with `-D HARDWARE_REVISION`, so the 9-bit
`CTRL_VPP_VPE_DROP_ENABLE == 0x100` never appears as `0x100` in the fixture — it appears as whatever
physical bit the mapper assigns. Do not write a segmentation rule against `0x100`.

**A per-entry classifier is necessary but NOT sufficient.** My primitive classification partitions all
620 entries into disjoint buckets with zero unclassified — proving mechanical partitionability:

```
PROTO_07 (198): pin_CE 38, pin_LSB 36, data_write 33, latch_settle_1us 26, pin_OE 19,
                oe_access_3us 19, pin_CTRL 16, settle_ms 4, pulse_100us 4, pulse_105us 2, pulse_110us 1
PROTO_08 (221): data_write 38, pin_CE 38, pin_LSB 36, latch_settle_1us 31, pin_CTRL 26, pin_OE 19,
                oe_access_3us 19, settle_ms 4, pulse_100us 4, settle_4us 3, pulse_105us 2, pulse_110us 1
PROTO_0B (201): pin_CE 38, pin_LSB 36, data_write 33, latch_settle_1us 26, pin_OE 19, oe_access_3us 19,
                pin_CTRL 14, settle_ms 4, pulse_500us 4, settle_4us 3, pin_MSB 2, pulse_525us 2, pulse_550us 1
```

But `pin_CE` (38) spans **both** the pulse segment and the verify-read segment — the same primitive in
two phases. D-07's six phase segments therefore require a small **state machine** walking the stream.
The discriminator is verified exact: `OUTPUT_ENABLE` value. On `0x07`, `{2,0x04,0x01}` precedes each
program pulse and `{2,0x04,0x00}` precedes each verify read; the counts are `7 + 12 = 19`, matching the
19 `pin_OE` entries exactly (7 pulses across 3 passes = 4+2+1; 12 verify reads = 4+4+4). Recommended
state machine:

| Segment | Entry condition |
|---|---|
| `init` | before the first `CONTROL_REGISTER` write whose value asserts a route bit; includes the 500 ms regulator settle (`kind=4, us=500`) |
| `route_assert` | a `CONTROL_REGISTER` latch group whose value changes HV route bits, plus its trailing `kind=4` settle (10 ms) |
| `address_set` | LSB/MSB latch groups (`pin ∈ {0x01,0x02}`) and their 1 µs settles |
| `pulse` | while `OUTPUT_ENABLE == 1`: the data write, the CE-low → `delayMicroseconds(width)` → CE-high window |
| `verify_read` | while `OUTPUT_ENABLE == 0`: the CE-low → 3 µs access → CE-high window |
| `teardown` | the route-release `CONTROL_REGISTER` group(s) after the last data or verify strobe |

**Binding constraint from D-07:** no entry may be unattributed. Implement that as an assertion that the
per-segment counts **sum to exactly the array length** for each of the six arrays, and that the union of
the segment index sets equals `range(len(array))` with no overlap — set equality, not a count match. A
count match alone can hide a double-counted entry paired with a dropped one.

### F-08 — Author D-01/D-07 as pytest modules, NOT as `scripts/check_*.py`; both convention floors are at zero headroom

`tests/test_checker_convention.py` (BASE-08) globs `check_*.py` in `firestarter/scripts/`
**non-recursively** and enforces seven requirements. Measured against the current tree:

| Literal | Value | Current count | Headroom |
|---|---|---|---|
| `FLOOR` (`:132`) | **6** | `ls scripts/check_*.py` → **6** | **0** |
| `FIXTURE_FLOOR` (`:133`) | **15** | `ls -d tests/fixtures/planted_*` → **15** | **0** |

Adding one `firestarter/scripts/check_<X>.py` therefore obliges, **in the same commit**:

1. `firestarter/tests/test_check_<X>.py` must exist (Test 2);
2. at least one `firestarter/tests/fixtures/planted_<X>*` entry — file *or* directory (Test 3);
3. that paired module's source must contain the checker's **exact filename** (Test 5);
4. that paired module's source must contain a `returncode != 0` assertion (Test 6);
5. `FLOOR` raised to 7 **and** `FIXTURE_FLOOR` raised — the module's own docstring says "A later phase
   that adds a firmware checker under `firestarter/scripts/` raises both floors deliberately in the SAME
   commit that adds the checker; lowering a floor is never the correct response to a red gate."

That is five coordinated edits and an edit to a convention gate, in a phase whose whole premise is that
it changes no behavior. **A pytest module under `firestarter/tests/` triggers none of it** — the glob
never reaches `tests/`. CONTEXT.md already places D-01's gate "under `firestarter/tests/`"; this finding
extends the same conclusion to D-07's "script" and resolves the D-01 discretion item ("one file or
beside the existing golden-identity gates") mechanically in favour of `tests/`.

Recommended homes, beside the existing golden-identity gates:

```
firestarter/tests/test_requirement_case_mapping_v131.py   # D-01
firestarter/tests/test_trace_segment_exhaustiveness_v131.py  # D-07
```

If a plan nonetheless wants a runnable CLI for D-07, put the module under `tests/` and give it an
`if __name__ == "__main__":` block — that is not matched by `CHECKER_GLOB` and costs nothing.

### F-09 — The two whole-repo porcelain assertions, and the exact ordering they impose

Both verified by reading the assertion sites in full.

| Assertion | Location | Asserts | Fires when |
|---|---|---|---|
| `assert _git_porcelain(_FW_REPO_ROOT) == ""` | `firestarter/tests/test_flash_path_record_sync.py:1247`, inside `test_planted_mutation_of_the_real_subset_is_detected` (from :1203) | the **whole firmware repo** is clean | any modified/untracked file anywhere in `firestarter/` → **firmware** suite RED |
| `assert _git_porcelain(FW_ROOT) == ""` | `firestarter_app/tests/test_py32_flash_map_host.py:391`, inside `test_planted_mutated_config_origin_is_detected` (from :351) | the **sibling firmware repo** is clean | any modified/untracked file anywhere in `firestarter/` → **host** suite RED |

Both are the trailing assertion of a planted-mutation test whose purpose is "the plant never touched the
real file." Neither is scoped to the file under test. So:

**Ordering rule for every plan in this phase:** *every* new or modified file in `firestarter/` — the
renamed fixture, the new fixture, the two new gates, the three rewritten baseline JSONs, the inventory —
must be **committed before either repo's suite is run**. Not staged: committed. A plan that creates the
fixture and then runs `pytest tests/` in the same task will see two unrelated RED tests and mis-diagnose
them.

Corollary that is easy to miss: the **host** half (D-17's gate, the D-16 sweep, the D-21 measurement)
depends on the **firmware** repo being clean. So the host-suite measurement cannot be interleaved with
uncommitted firmware work even though the two halves are otherwise independent (CONTEXT.md's discretion
note that "the two are separable" is true about *content*, not about *scheduling*).

**Current tree state, measured this session:**

| Repo | Branch | Porcelain |
|---|---|---|
| `firestarter` | `gsd/v1.31-27c-programming-algorithm-fidelity` @ `59a8a42` | **clean** ✅ |
| `firestarter_app` | `gsd/v1.31-27c-programming-algorithm-fidelity` @ `f77b0ea` | **8 untracked** ⚠️ |
| meta (`/workspaces`) | `gsd/v1.31-…` @ `e503f07` | 8 untracked + 2 modified submodule pointers |

The firmware repo is clean **right now**, so both porcelain assertions pass at phase start. The host
repo's 8 untracked entries (`.coverage`, `.planning/config.json`, `SECURITY.md`, four
`datasheets/*.pdf`, `write_test_port.sh`) do **not** trip either assertion — neither asserts the *host*
repo's porcelain. But they are noise a plan should either commit or `.gitignore` before measuring, and
`.coverage` in particular will be rewritten by the D-21 run.

The meta repo's two modified submodule pointers mean the meta commit does not yet record the sub-repo
tips. Whether that matters is a `commits_land_in:` question for D-19, not a gate.

### F-10 — CAP-03 byte layout: both sides read, offsets are index-identical, and the gate's scan targets

**Firmware side — authoritative pack order** `[VERIFIED: firestarter/src/firestarter.cpp:185-204, inside init_programmer_framed]`:

| Line | Statement | Byte(s) of `_ready` |
|---|---|---|
| :194 | `uint8_t _ready[4 + 32 + 2];` | buffer sized 38 |
| :195 | `_ready[0] = (DATA_BUFFER_SIZE >> 8) & 0xFF` | 0 (buffer hi) |
| :196 | `_ready[1] = DATA_BUFFER_SIZE & 0xFF` | 1 (buffer lo) |
| :198 / :200 | `_ready[2] = rurp_get_hardware_revision()` / `= 0xFE` (`#ifdef HARDWARE_REVISION` / `#else`) | 2 (hw_rev) |
| :202 | `_ready[3] = _vlen;` (`_vlen = strlen(FW_VERSION)`, clamped `> 32 → 32` at :193) | 3 (ver_len) |
| :203 | `memcpy(_ready + 4, _ver, _vlen);` | 4 … 4+_vlen−1 (ver bytes) |
| :206 | `_ready[4 + _vlen]     = (_budget >> 8) & 0xFF` | 4+_vlen (budget hi) |
| :207 | `_ready[4 + _vlen + 1] = _budget & 0xFF` | 4+_vlen+1 (budget lo) |
| :208 | `LOG_OK_ID_BYTES(MSG_OK_READY, _ready, (uint8_t)(4 + _vlen + 2));` | emitted length |

The wire-layout comment at `:168` states it in one line, and this is the string a scanning gate can
anchor on:

```
[buffer_size u16 BE][hw_revision u8][ver_len u8][ver bytes][write_budget_s u16 BE]
```

**Host side — the decoder's offsets** `[VERIFIED: firestarter_app/firestarter/serial_comm.py:344-442]`.
`params_bytes = body[1:-1]` (`:388`) strips the id byte and the trailing CRC, so **`params_bytes[i]`
corresponds 1:1 to firmware `_ready[i]`**:

| Host expression | Line | Firmware counterpart |
|---|---|---|
| `struct.unpack(">H", params_bytes[:2])[0]`, guarded `len >= 2`, clamped `1 <= v <= 4096` | :394-401 | `_ready[0..1]` |
| `self.hw_revision = params_bytes[2]`, guarded `len >= 4` | :408-409 | `_ready[2]` |
| `ver_end = 4 + params_bytes[3]` | **:410** | `_ready[3]` = `_vlen` |
| `params_bytes[4:ver_end]`, guarded `ver_end <= len` | :411-414 | `memcpy(_ready+4, …, _vlen)` |
| `struct.unpack(">H", params_bytes[ver_end : ver_end + 2])[0]`, guarded `len >= ver_end + 2`, clamped `1 <= v <= WRITE_BUDGET_MAX_S` | **:430-441** | `_ready[4+_vlen]`, `_ready[4+_vlen+1]` |

`WRITE_BUDGET_MAX_S = 14400` `[VERIFIED: serial_comm.py:77]`.

**What D-17's gate must assert, concretely:**
1. the firmware pack order string / index expressions at the five sites above, read from
   `fw_path("src", "firestarter.cpp")`;
2. that the budget is read by the host at the **computed** `ver_end`, not a literal — the load-bearing
   assertion. `ver_end = 4 + params_bytes[3]` must appear, and no bare integer index `> 3` may be used
   to reach the budget;
3. index-identity: firmware `_ready[k]` ↔ host `params_bytes[k]` for `k ∈ {0,1,2,3}` and the two
   computed budget bytes;
4. big-endian on both sides for both u16 fields (`>> 8` / `& 0xFF` pairs vs `struct.unpack(">H", …)`).

**Existing coverage the gate must NOT duplicate** — this is the seam, and it is explicit:

- `firestarter/tests/test_ack_layout_source_contract_v143.py` pins the **firmware** side as a source
  contract (10 coverage items) and states in its own docstring: *"It does NOT perform a live cross-repo
  comparison against `firestarter_app/firestarter/serial_comm.py`'s decoder — that standing gate is
  handed to Phase 144 / TEST-07 (143-RESEARCH.md Open Question 4)."* `[VERIFIED]`
- `firestarter_app/tests/test_hw_revision_gate.py` pins the **host** side behaviourally via a
  `_cap03_params` fixture at two identity lengths (`3.0.0:uno` / `3.0.0:leonardo`), plus the truncation,
  zero, 65535 and 14400 boundary cases. **27 passed** on the 3.11 replica this session. `[VERIFIED]`

So D-17's contribution is precisely **the cross-repo comparison neither side performs** — not a third
copy of either. Say that in the plan, or a reviewer will reasonably read it as duplication.

**Asymmetry worth recording as a non-claim:** the firmware clamps `_vlen` to `≤ 32` (`:193`) and sizes
`_ready` at exactly `4 + 32 + 2`; the host applies **no** upper bound on `params_bytes[3]`, relying only
on `ver_end <= len(params_bytes)`. That is safe (a longer declared length simply fails the guard and
leaves the fields `None`) and is not a defect — but "the two sides agree on the layout" should not be
stated as "the two sides agree on the bounds."

**Home and plumbing for the new gate** (all verified):
- `firestarter_app/tests/`, behind `@requires_fw`, resolving its scan target via
  `fw_path("src", "firestarter.cpp")` so a firmware rename is a named `MissingScanTargetError`
  (`fw_presence.py:117-140`) and never a silent skip.
- `tests/scan_paths.py` holds `CROSS_REPO_TEST_PATHS` (6 entries) and `test_scan_paths_resolve.py`
  asserts every entry resolves, with `_FLOOR = 6`. **There is no completeness check** forcing a new
  cross-repo consumer to be listed — so adding `src/firestarter.cpp` to that inventory is the house
  convention, not a gate requirement. If the plan adds it, the entry must resolve (it does) and must not
  be a same-repo lookalike (`test_no_entry_is_a_same_repo_lookalike`); adding it also raises the
  effective floor, so do not lower `_FLOOR`.
- `tests/test_skip_census.py` pins **no** counts — adding a `requires_fw`-gated module cannot break it.
  `[VERIFIED: no FLOOR/CEILING/EXPECTED literal in the module]`
- `tools/check_no_exists_proxy.py` scans an **explicit `_DEFAULT_TARGETS` list, never a glob**, so a new
  test module is not auto-scanned. It also matters that the new gate uses `requires_fw` rather than a
  module-level `not path.exists()` idiom — which it will, by construction.

### F-11 — D-16's absent-path subprocess mechanic: verified working, with a verbatim transcript

`fw_presence.py:35-45` documents the import-time binding hazard, and `:80`/`:86`/`:88`/`:102` implement
it (`FW_ROOT` from `os.environ.get` at module scope; `requires_fw = pytest.mark.skipif(not
FW_REPO_PRESENT, …)`). `monkeypatch.setenv` cannot reach any of them.

**I ran both directions this session on the CI-parity interpreter.** Present path:

```
$ cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest \
    tests/test_revision_constants_parity.py -o addopts="" -q
14 passed in 0.15s
```

Absent path (child process, env var set in the child's environment):

```
$ FIRESTARTER_FW_ROOT=<empty dir> .venv/ci-replica/bin/python -m pytest \
    tests/test_revision_constants_parity.py -o addopts="" -rs -q
.sssssss...s..
SKIPPED [1] tests/test_revision_constants_parity.py:563: firestarter firmware checkout absent (no <empty dir>/.git marker)
… (8 skips, one canonical reason string, each naming the probed marker path)
6 passed, 8 skipped in 0.06s
```

**The mechanic works exactly as D-16 describes: clean skips, no errors, one canonical reason string
naming the probed marker.** Note the 6 that still pass in the absent run — those are the
fixture-driven planted-violation legs (`_FIXTURE_*` at `:728-730`), which read committed fixtures under
`tests/fixtures/` rather than the real header and therefore carry no `requires_fw`. That is deliberate
(the module's comment at `:720-724` calls it "partially offsets the residual host-only-CI skip gap") and
is a *good* property to record: even with no firmware checkout, the checker's failure modes are still
exercised.

**Scope of the D-16 sweep — 13 host modules use `requires_fw`** (occurrence counts):
`test_revision_constants_parity.py` 16, `test_py32_asset_name_host.py` 13, `test_py32_flash_map_host.py`
11, `test_sdp_table_parity.py` 9, `test_gen_validation_header.py` 8, `test_sdp_bus_config_drift.py` 5,
`test_dispatch_mirror.py` 4, plus `test_check_is_memory_cmd_no_ifdef.py`,
`test_check_no_log_in_sdp_window.py`, `test_fw_presence.py`, `test_scan_paths_resolve.py` (3 each),
`test_skip_census.py` and `conftest.py` (1 each). A plan can run the whole suite twice, or name this
subset for the absent-path leg — either satisfies D-16, but the record should say which and why.

**Empty-dir caveat:** an "empty directory" is enough — `FW_REPO_PRESENT` probes
`FW_ROOT / ".git"` existence only (`:86-88`, `.exists()` not `.is_dir()`, deliberately, so a submodule
or worktree `.git` *file* also counts). Do **not** point `FIRESTARTER_FW_ROOT` at a path that happens to
contain a `.git` entry, or the run silently tests the present path instead. Assert the skip count in the
plan's verification, not just exit 0.

### F-12 — TEST-07's exact command set, and the interpreter that makes it CI-parity

| Leg | Command | Notes |
|---|---|---|
| ruff lint | `ruff check firestarter/ tests/` | `ci.yml:81`; the scope is those two dirs, not the repo |
| ruff format | `ruff format --check firestarter/ tests/` | `ci.yml:84` |
| mypy watermark | `python tools/check_mypy_watermark.py` | `ci.yml:87`; watermark **35**, read by regex from the `# mypy_error_watermark = 35` comment at `pyproject.toml:174`. Exits 0 at-or-below, 1 above, and prints an `INFO:` (still 0) when *below* — a below-watermark result is a lowering **invitation**, not a pass to celebrate |
| host suite + coverage | `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` | `ci.yml:90`. For D-21's record add `-o addopts=""`, since `addopts = "-ra -q"` and doubling `-q` suppresses the count line |
| firmware pytest | `python3 -m pytest tests/ -q` in `firestarter/` | Not in the CI legs for this branch's workflows the way the host's are; **292 passed** at tip |
| AVR builds | `pio run -t clean -e <env>` then `pio run -e <env>`, one env per uninterrupted invocation | The measurement procedure `size_baseline.json:meta.note` mandates. A default 2-minute Bash timeout **truncates the toolchain build mid-compile and silently contaminates the measurement** — the trap that record explicitly names. Use a long explicit timeout. |
| native suites | `pio test -e native`, `-e native_nodevtools` | Pinned at 141 cases / 17 suites; asserted by `compare_native` |
| v131 envs (D-02, D-15) | `pio test -e native_params_v131`, `-e native_loop_v131`, `-e native_trace_v131` | Run **by name**, never fed to either checker (C-03). In **no** CI leg — restate that. |

Interpreter: `.venv/ci-replica/bin/python` → `python3.11` → **Python 3.11.15**, run from inside
`/workspaces/firestarter_app`. Ambient is 3.12 and masks CI defects (the `mypy` watermark gate is
**fail-open** under the wrong interpreter — a recorded hazard).

`ruff` target is `py39` (`pyproject.toml:110`) and `line-length = 88` — a new host test module must be
written to those, or `ruff format --check` goes RED on arrival.

### F-13 — The three baselines, their contents, and which one each decision targets

| File | Current AVR flash (uno/uno328pb/leonardo) | `native_envs` recorded | Targeted by | Read by default? |
|---|---|---|---|---|
| `scripts/baseline/size_baseline.json` | **23954 / 24004 / 26016** | native, native_nodevtools, native_pinmap_provisional | **D-10** (rewrite to tip) | **Yes** — `FIRESTARTER_SIZE_BASELINE` default at `check_size_baseline.py:95-97`; also read by `check_build_warnings.py` |
| `scripts/baseline/size_baseline_base01.json` | 23932 / 23976 / 26072 (v1.23-era, BASE-01) | native, native_nodevtools | **D-11** (re-anchor; band literals unchanged) | No — named explicitly via `--baseline …base01.json` for `--policy merge05` |
| `scripts/baseline/size_baseline_v131.json` | 23954 / 24004 / 26016 (same as the live anchor; `deltas_vs_size_baseline` all zero) | native, native_nodevtools, native_pinmap_provisional, **native_trace_v131 only** | **D-13** (refresh — see **C-01**) | No |

D-09's identification of `size_baseline.json` as the PREP-03 anchor is confirmed byte-for-byte.

Two mechanics from the files' own metadata that a plan should honour:

- `size_baseline_v131.json:meta.frozen_for` states: *"TEST-08 must pass
  `--baseline scripts/baseline/size_baseline_v131.json` explicitly … relying on the default seam here
  would silently compare against a moving target."* That is a direct instruction to TEST-08 from the
  artifact it inherits. It does not conflict with D-09 (which names the *comparison anchor*); it
  constrains *how* the v131 record is re-derived.
- `size_baseline.json:meta.supersedes` states the canonical `--policy merge05` invocation "always names
  [BASE-01] explicitly via `--baseline scripts/baseline/size_baseline_base01.json`." D-11's re-anchor
  changes that file's *contents*, not the invocation. `MERGE05_UNO_CLASS_FLASH_BAND` stays 64 and
  `check_size_baseline.py` is not modified — verified consistent with D-11.

**Leonardo ceiling arithmetic, for TEST-08's explicit check (D-09 / success criterion 4):**
`flash_total = 28672`; tip `flash_used = 26906` → **93.8%**, **1766 B** remaining. After D-11's
re-anchor, the leonardo band becomes `<= 0` growth from 26906 — so leonardo's 1766 B gains a real guard
for the first time, which is exactly D-11's stated intent.

### F-14 — `check_size_baseline.py`'s CLI surface, and its never-vacuous guard

`[VERIFIED: scripts/check_size_baseline.py main()]`

```
--baseline <path>            # overrides FIRESTARTER_SIZE_BASELINE
--avr-log <env>=<path>       # repeatable
--native-log <env>=<path>    # repeatable
--rebuild                    # iterates AVR_ENVS then NATIVE_ENVS, building each
--policy merge05             # band policy instead of strict identity (AVR only)
```

Two behaviours a plan must design around:

1. **Never-vacuous guard.** With no `--avr-log`, no `--native-log` and no `--rebuild`, `main()` prints
   `FAIL: no envs compared …` and returns **1**. A comparator that compares nothing cannot print PASS.
   So an invocation must always name its inputs; a "just check the baseline" call is a red.
2. **`--rebuild` cannot reach a `*_v131` env** (it iterates the two hardcoded tuples). The only route to
   a `*_v131` env is an explicit `--native-log`, which is exactly the route C-03 says to never take.

`compare_avr_policy_merge05` (`:214-…`) rules, verified: leonardo `flash_delta <= 0`; uno/uno328pb
`flash_delta <= 64`; **all three** require `ram_used` *exactly* unchanged and `flash_total`/`ram_total`
unchanged (a moved total is "board or framework moved" — a finding, not a pass). Note the RAM equality
on `uno328pb` is deliberately **stronger** than MERGE-05's text, per the function's own docstring.

### F-15 — Where D-01's gate and D-07's gate should live, and the module conventions they inherit

`firestarter/tests/` has **no `conftest.py` anywhere in the repo** — a recorded house-rule, restated in
at least three modules' docstrings, not an omission. Every module resolves its own paths at module scope:

```python
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
```

Inherited conventions, each verified present in the four source-scan precedents:

1. **Env seam per scan target**, `os.environ.get(...)` at module scope, documented as import-binding.
2. **Non-vacuity self-protection**, in two halves: one that recomputes the default target from the repo
   root *without* reading the environment (closing the
   `check_permitted_claims.py`-`_HERE`-resolves-wrong landmine), and one that runs the extractor against
   whatever the seam currently resolves to and requires a non-empty result.
3. **Concatenation-built needles** for every negative assertion, plus a self-test that no needle appears
   verbatim in the module's own source.
4. **A no-skip self-check**: the module's own source must contain no `pytest.skip` call and no
   `@pytest.mark.skipif` decorator, asserted with `stripped.startswith(...)` so the assertion's own
   prose cannot self-match (`test_golden_trace_identity_eprom_v131.py:222-244` is the shortest example).
5. **Fail-closed `git` resolution**: `shutil.which(os.environ.get("GIT", "git"))` followed by a plain
   `assert`, never a skip (`:91-109`).
6. **An honest CI-framing paragraph** in the docstring, because `pytest tests/ -v` appears at
   `firestarter/.github/workflows/build.yml:161` and `beta-build.yml:134` — so these modules *will* run
   in CI once the branch reaches `main`/`beta`, but do **not** run in any CI leg on the milestone branch
   itself. State it that way; do not imply current coverage.

---

## Architecture Patterns

### Gate authoring flow for this phase

```
                    ┌─────────────────────────────────────────────┐
                    │ PHASE START: firestarter clean @ 59a8a42     │
                    │ 292 firmware pytest / 141+141 native pinned  │
                    │ trace identity gate GREEN (ca3e09f1…)        │
                    └────────────────────┬────────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        │ FIRMWARE HALF (commits_land_in: firestarter)                    │
        │                                                                 │
        │  D-01 mapping gate ──► parse 3 .cpp ──► assert 88 names exist   │
        │       │  planted RED: rename a case in a scratch copy via seam  │
        │       ▼                                                         │
        │  D-05 git mv ──┐                                                │
        │  D-06 capture ─┼──► ONE COMMIT (F-05) ──► identity gate GREEN   │
        │  D-08 inventory┘        ▲                                       │
        │                         │ blob SHA via `git hash-object`        │
        │                         │ BEFORE staging; recorded_at_head =    │
        │                         │ this commit's PARENT                  │
        │  D-07 exhaustiveness gate ──► parse BOTH headers ──► 885 attributed
        │       │  planted RED: an entry outside every segment            │
        │       ▼                                                         │
        │  D-10/D-11/D-12/D-13 baseline rewrites (after measurement)      │
        │                                                                 │
        │  ══► COMMIT EVERYTHING before any suite run (F-09) ◄══          │
        └────────────────────────────────┬────────────────────────────────┘
                                         │ firmware repo must be CLEAN
        ┌────────────────────────────────▼────────────────────────────────┐
        │ HOST HALF (commits_land_in: firestarter_app)                    │
        │                                                                 │
        │  D-17 CAP-03 parity gate ──► fw_path("src","firestarter.cpp")   │
        │       │                  ──► serial_comm._decode_id_frame       │
        │       │  planted RED: fixture .cpp with budget at literal idx   │
        │       ▼                                                         │
        │  D-16 sweep: PRESENT run ──► verbatim PASS                      │
        │              ABSENT run  ──► child proc, FIRESTARTER_FW_ROOT=∅   │
        │                          ──► assert skip COUNT, not just exit 0 │
        │  D-21 measurement: .venv/ci-replica/bin/python, -o addopts=""    │
        │  F-12 legs: ruff check / ruff format / mypy 35 / pytest --cov 70 │
        └────────────────────────────────┬────────────────────────────────┘
                                         │
        ┌────────────────────────────────▼────────────────────────────────┐
        │ MEASUREMENT (build tier, long timeouts)                          │
        │  pio run -t clean -e {uno,uno328pb,leonardo} then pio run        │
        │  pio test -e {native, native_nodevtools}      → 141/17 each      │
        │  pio test -e {native_params,native_loop,native_trace}_v131       │
        │    ── run BY NAME; never as a checker env arg (C-03) ──          │
        └─────────────────────────────────────────────────────────────────┘
```

### Recommended file layout

```
firestarter/
├── test/native/avr/_shared/
│   ├── eprom_v131_expected_prechange.h    # D-05: git mv, byte-untouched, included by NOTHING
│   └── eprom_v131_expected.h              # D-06: NEW capture, keeps the old NAME (F-05)
├── tests/
│   ├── golden/eprom_v131_trace_inventory.json      # D-08: new counts + new blob_sha
│   ├── test_requirement_case_mapping_v131.py       # D-01  (pytest, NOT scripts/ — F-08)
│   └── test_trace_segment_exhaustiveness_v131.py   # D-07  (pytest, NOT scripts/ — F-08)
└── scripts/baseline/
    ├── size_baseline.json          # D-10: rewrite to tip
    ├── size_baseline_base01.json   # D-11: re-anchor in place (D-12: no in-tree copy of v1.24)
    └── size_baseline_v131.json     # D-13: refresh + ADD two env records (C-01)

firestarter_app/
└── tests/
    ├── test_cap03_ack_layout_parity.py             # D-17, behind @requires_fw
    └── fixtures/planted_cap03_*.cpp                # D-18's planted violation(s)
```

### Pattern: two independent pins per golden

Every frozen artifact in this repo carries a **blob-SHA check AND a structural check**, because a
whole-file match cannot distinguish "unchanged" from "an array deleted together with its consumer."
`eprom_v131_trace_inventory.json` implements it as six assertions (blob SHA / array names / entry counts
positionally / non-vacuity / consumer-still-includes / git-is-required-not-optional). D-08 preserves
that shape. **A new golden authored this phase must carry both pins too** — a bare count is the hollow
shape this project has had to rebuild before.

### Pattern: the one-commit property

When a data file and the gate that reads it must agree, they land in the **same commit**, and the
recorded `recorded_at_head` therefore names that commit's **parent**. Both
`protocol_branch_inventory.json` (Phases 142 and 143) document this explicitly so a later reader does
not mistake the offset for an error. F-05 applies it to D-05/D-06/D-08.

### Anti-Patterns to Avoid

- **Pasting `141-NEW-TRACE.md` §5's arrays.** Stale at 91/**119**/59. `0x08` is 115. D-06 forbids it and
  F-06 gives three independent tells that catch it.
- **Hand-editing a count or a blob SHA in either inventory JSON.** Both carry a binding
  `meta.how_to_update` requiring an independent re-parse and a commit message naming what changed.
- **Authoring D-07's gate as `scripts/check_*.py`.** F-08 — five coordinated edits and two zero-headroom
  floors, for zero benefit.
- **Feeding a `*_v131` env name to either checker.** Uncaught `KeyError` → exit 1 → a *false regression
  signal*, which is worse than a tool failure because it looks like real damage (C-03).
- **Running either suite with uncommitted firmware files.** Two unrelated RED tests, both mis-diagnosable
  (F-09).
- **`monkeypatch.setenv("FIRESTARTER_FW_ROOT", …)`.** No effect; binds at import (F-11).
- **A default Bash timeout on an AVR build.** Truncates the toolchain mid-compile and silently
  contaminates the size measurement — named in `size_baseline.json:meta.note` (F-12).
- **Asserting only exit 0 on the absent-path run.** A `.git` entry inside the "empty" dir silently tests
  the present path. Assert the skip count (F-11).
- **Claiming CI covers the `*_v131` envs.** It does not, in either repo (D-15, F-15 item 6).
- **A count-sum-only exhaustiveness check.** Use set equality over index ranges; a count match hides a
  double-count paired with a drop (F-07).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Firmware repo presence / cross-repo path resolution | A `not path.exists()` proxy | `tests/fw_presence.py` — `requires_fw`, `fw_path`, `MissingScanTargetError` | A firmware rename flips a bespoke proxy PASS→SKIP at exit 0. That defect class (A-7, 7 modules) is precisely what this module was built to remove, and `tools/check_no_exists_proxy.py` lints for it. |
| Re-parsing the trace fixture's arrays | A new regex from scratch | `test_golden_trace_identity_eprom_v131.py::_parse_arrays` as the **template** (comment-strip then `\{[^{}]*\}`) — reimplemented, not imported | The gate's own docstring explains why: inventory and file must be compared by two **independent** readings, not one parser trusting its prior output. Copy the technique; do not import it. |
| Capturing the new trace | Hand-deriving entries from the loop's logic | `dump_v131_merged_ready_to_paste` + direct binary invocation (F-06) | Every array in the repo is empirical. A hand-derived array asserts what you believe, not what the code emits — and the pre-change fixture's own banner says exactly that. |
| Planted-violation fixtures | An inline temp file written by the test | Committed `tests/fixtures/planted_*` + the import-time env seam | The committed-fixture form is what makes the planted leg reproducible on a machine with no firmware checkout, which is how `test_revision_constants_parity.py` keeps 6 of 14 legs live in the absent-path run (F-11). |
| Predicting a not-yet-committed blob SHA | Committing, reading, amending | `git hash-object <path>` before staging, `recorded_at_head` = parent | The documented one-commit pattern; avoids an amend dance that breaks the "one commit, one reason" property the D-18 goldens rely on. |
| A budget/pack-order restatement in the new gate | Re-deriving the pack arithmetic in Python | Assert against `eprom_block_budget_s(...)` being *called* and the `_ready[…]` index expressions | `test_ack_layout_source_contract_v143.py`'s Coverage 6 already forbids hand-rolled restatement at the emit site; the parity gate must not reintroduce one on the test side. |

**Key insight:** in this repo the expensive part of a gate is never the assertion — it is the
self-protection (non-vacuity, seam, no-skip, needle-hygiene) that keeps the gate from passing over an
empty set. Four modules already implement that scaffolding correctly. Copy their *structure* verbatim
and spend the thinking budget on the assertion.

## Runtime State Inventory

> D-05 is a rename, so this section applies — scoped to it and to the capture.

| Category | Items Found | Action Required |
|---|---|---|
| Stored data | **None** — no database, datastore or persisted record references `eprom_v131_expected.h`. Verified: the only non-source references are `tests/golden/eprom_v131_trace_inventory.json` (`meta.source`, in-tree, D-08 rewrites it) and `tests/test_golden_trace_identity_eprom_v131.py` (`_FIXTURE_PATH`, in-tree). | D-08's inventory rewrite; nothing else |
| Live service config | **None** — verified by grep across both repos; no CI workflow, no external service references the fixture path. The three `*_v131` envs appear in no `build.yml` / `beta-build.yml` leg (D-15). | none |
| OS-registered state | **None** — verified: no scheduler task, systemd unit or pm2 process references any Phase 144 artifact. | none |
| Secrets/env vars | **None renamed.** Five env seams are *read* by this phase's targets and none changes name: `FIRESTARTER_SIZE_BASELINE`, `FIRESTARTER_FW_ROOT`, `FIRESTARTER_META_ROOT`, `FIRESTARTER_ACK_SCAN_DISPATCH_SOURCE`, `PLATFORMIO_BUILD_FLAGS`. A new gate adds a **new** seam name (F-03), it renames none. | none; document the new seam in the module docstring (house rule — the repo has no central env inventory) |
| Build artifacts | **Two, both real.** (a) `.pio/build/native_trace_v131/firestarter_native` may be a stale binary built without `-D EPROM_V131_TRACE_DUMP` or from an older tree — a stale run would produce a *plausible-looking wrong capture*. (b) `.pio/build/<avr env>/` warm caches make a size or warning measurement non-comparable to the recorded COLD figures. | `rm -rf .pio/build/native_trace_v131` before the capture; `pio run -t clean -e <env>` before each AVR measurement (F-06, F-12) |

**The canonical question, answered:** after every file in `firestarter/` is updated, the only runtime
state still holding the old content is the PlatformIO build cache under `.pio/build/`. Nothing else
caches, stores or registers the fixture. That is a narrow blast radius — but the stale-capture failure
mode is silent, which makes it the one worth a plan step.

## Common Pitfalls

### Pitfall 1: The identity gate reads `HEAD:`, not the worktree
**What goes wrong:** the new fixture is written, `pytest tests/` is run, and
`test_blob_sha_matches_the_recorded_inventory` still reports the OLD SHA — or, after a bare `git mv`,
the test **fails inside `_git`'s `returncode == 0` assert** rather than reporting a SHA mismatch, so the
message names git's exit code instead of the real problem.
**Why it happens:** `_git("rev-parse", f"HEAD:{_FIXTURE_PATH}")` at `:158`.
**How to avoid:** land D-05 + D-06 + D-08 in one commit (F-05); predict the SHA with `git hash-object`.
**Warning signs:** a test failure whose message is about git's exit code, not about a SHA.

### Pitfall 2: `native_loop_v131` is two suites, and a "case count" is ambiguous
**What goes wrong:** a plan records "79" as the suite count or "88" as an env's case count, and the
number is unfalsifiable afterwards.
**Why it happens:** `native_loop_v131`'s `test_filter` names two suites (47 + 32); `native_params_v131`
names one (9). 88 is the three-suite mapping denominator; 79 is one env's run figure.
**How to avoid:** always label a count with **which env** or **which suite** produced it (F-01).
**Warning signs:** any bare "79" or "88" without an env or suite name attached.

### Pitfall 3: A pre-authored gate leg can be unreachable, so RED proves nothing on its own
**What goes wrong:** a planted violation turns a leg RED, the transcript is captured, D-18 is declared
satisfied — but the leg was RED because its *locator* never matched anything, and it will never go GREEN
for the right reason either.
**Why it happens:** a source-scan gate whose extraction silently returns empty passes every negative
assertion vacuously and fails every positive one, and both look like correct behaviour.
**How to avoid:** every gate needs a non-vacuity leg (F-03, F-15 item 2), and D-18's evidence must be a
**RED-then-GREEN pair with the GREEN attributed to the right cause** — not a RED alone. This is
CONTEXT.md's own D-18 sentence; it is repeated here because it is the pitfall most likely to be
under-executed.
**Warning signs:** a planted-RED transcript whose failure message names zero specific items.

### Pitfall 4: `--policy merge05` reading green after D-11 means the anchor moved
**What goes wrong:** the phase record says "MERGE-05 green" and a reader concludes growth stayed inside
v1.24's band. It did not — growth was +870/+870/+890 against a 64 B band.
**Why it happens:** D-11 rewrites the file the band measures *from*, leaving the band literals untouched.
**How to avoid:** D-14's constrained sentence, verbatim: *"MERGE-05 reads green because its anchor moved
to v1.31, not because growth stayed inside v1.24's band."*
**Warning signs:** any sentence pairing "MERGE-05" and "green" without the word "anchor" nearby.

### Pitfall 5: A `*_v131` env name in a checker invocation looks like a size regression
**What goes wrong:** `check_size_baseline.py --native-log native_loop_v131=…` exits 1 with a `KeyError`
traceback. Exit 1 is the *regression* code; the reader believes the tree regressed.
**Why it happens:** `compare_native`'s bare subscript; `KeyError` is not `ParseError` so it never
reaches the exit-2 arm (C-03).
**How to avoid:** never pass a `*_v131` env to either checker, under any `--baseline`. Record the three
envs' counts in prose and in `size_baseline_v131.json` only.
**Warning signs:** a `Traceback` in a gate's output — a working gate never prints one.

### Pitfall 6: Warm-cache measurement, silently
**What goes wrong:** a native warning count comes in at 998 instead of 1166, or an AVR flash figure
differs from a prior record for no code reason.
**Why it happens:** PlatformIO reuses `.pio/build/<env>`; the recorded watermarks are **cold** figures
(998 is the warm figure for both native envs — `size_baseline.json:meta.warm_vs_cold_correction`).
Below-watermark returns `INFO`, not `FAIL`, so a warm run stays green and looks fine.
**How to avoid:** `rm -rf .pio/build/<env>` / `pio run -t clean -e <env>`, one uninterrupted invocation
per env, with a long explicit timeout. Never lower a watermark from a warm figure.
**Warning signs:** an `INFO:` line inviting you to lower a watermark.

### Pitfall 7: The host suite depends on the *firmware* repo being clean
**What goes wrong:** the firmware half is mid-flight, the host half is run in parallel to save time, and
`test_py32_flash_map_host.py::test_planted_mutated_config_origin_is_detected` goes RED for reasons that
have nothing to do with the host.
**Why it happens:** `assert _git_porcelain(FW_ROOT) == ""` at `:391` (F-09).
**How to avoid:** the two halves are separable in *content* but serialised in *scheduling*: firmware
files committed, then host suite.
**Warning signs:** a py32 flash-map test failing during a phase that touches no py32 code.

## Code Examples

### Reading the committed blob (D-05's single proof, D-08's assertion)

```bash
# Source: firestarter/tests/test_golden_trace_identity_eprom_v131.py:158
cd /workspaces/firestarter
git rev-parse HEAD:test/native/avr/_shared/eprom_v131_expected_prechange.h
# must print ca3e09f164e6e1c541ecb63d15bbebf5bce41d70 after D-05's git mv

# Predicting the NEW fixture's SHA before staging (D-08):
git hash-object test/native/avr/_shared/eprom_v131_expected.h
```

### Independent array re-parse (the technique D-08's `how_to_update` mandates)

```python
# Source: firestarter/tests/test_golden_trace_identity_eprom_v131.py:131-144
_ARRAY_DECL_RE = re.compile(r"static const v131_trace_entry_t\s+(\w+)\[\]\s*=\s*\{(.*?)\};", re.DOTALL)
_ENTRY_RE = re.compile(r"\{[^{}]*\}")

def _parse_arrays(text):
    arrays = []
    for m in _ARRAY_DECL_RE.finditer(text):
        body_nc = re.sub(r"/\*.*?\*/", "", m.group(2), flags=re.DOTALL)
        body_nc = re.sub(r"//[^\n]*", "", body_nc)
        arrays.append((m.group(1), len(_ENTRY_RE.findall(body_nc))))
    return arrays
```

### Field-capturing parse for D-07 (verified to match all 620 entries)

```python
# Derived this session against test/native/avr/_shared/eprom_v131_expected.h
_ENTRY_FIELDS_RE = re.compile(
    r"\{\s*(\d+)\s*,\s*(0x[0-9A-Fa-f]+)\s*,\s*(0x[0-9A-Fa-f]+)\s*,\s*(\d+)UL\s*\}"
)
# kind: 1=STROBE_DATA 2=STROBE_PIN 3=DELAY_US 4=DELAY_MS   (eprom_v131_expected.h:88-91)
# pin:  0x01 LSB  0x02 MSB  0x04 OUTPUT_ENABLE  0x08 CONTROL_REGISTER  0x20 CHIP_ENABLE
#       (include/rurp_shield.h:53-57)
```

### The import-time env seam every new source-scan gate needs

```python
# Source: firestarter/tests/test_hv_routing_source_contract_v142.py:200-206 (pattern)
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_MAPPING_REL = "test/native/avr"
# Binds at IMPORT -- a planted run must set this in a CHILD process, never monkeypatch it.
_SCAN_SUITES = Path(
    os.environ.get("FIRESTARTER_CASE_MAP_SCAN_ROOT", str(_REPO_ROOT / _MAPPING_REL))
)
```

### The no-skip self-check (fail-closed, self-matching-safe)

```python
# Source: firestarter/tests/test_golden_trace_identity_eprom_v131.py:222-244
def test_this_module_cannot_be_silently_skipped():
    for line in Path(__file__).read_text().splitlines():
        stripped = line.strip()
        assert not stripped.startswith("pytest.skip"), f"skip-bypass call at: {line!r}"
        assert not stripped.startswith("@pytest.mark.skipif"), f"skip-marker at: {line!r}"
```

### D-16's absent-path run (verified working this session)

```bash
# Source: firestarter_app/tests/fw_presence.py:35-45 (the binding warning), executed and confirmed
cd /workspaces/firestarter_app
EMPTY=$(mktemp -d)                                   # must contain NO .git entry
FIRESTARTER_FW_ROOT="$EMPTY" .venv/ci-replica/bin/python -m pytest \
    tests/ -o addopts="" -rs -q
# assert the SKIP COUNT, not just exit 0 -- a stray .git in $EMPTY silently
# tests the PRESENT path instead (fw_presence.py:86-88 probes .exists()).
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact on this phase |
|---|---|---|---|
| Each host module derives "firmware absent" from its own `not <file>.exists()` proxy | One `fw_presence.py` keyed on `../firestarter/.git`; a missing scan target under a present repo is a hard `MissingScanTargetError` | Phase 123 / v1.23 | D-17 must use `requires_fw` + `fw_path`, never a bespoke proxy; `tools/check_no_exists_proxy.py` lints for the old shape |
| A golden pinned by blob SHA alone | Two independent pins per golden (blob + structural re-parse) | Phase 124 (SDP), extended Phase 138 (v131 trace) | D-08 must preserve both; a new golden needs both |
| Checkers added ad hoc | `test_checker_convention.py` enforces checker ↔ test ↔ planted-fixture triples with hardcoded floors | Phase 123 / BASE-08 | F-08: keep the new gates out of `scripts/` |
| New native suite folded into `[env:native]` | Dedicated env per suite, because both pinned envs are asserted at exactly 141/17 | Phase 124 (pinmap), 138 (trace), 140 (params), 141 (loop) | D-04's "no new env" holds *because* D-03 reversed; the pattern is why 6 native envs exist |
| CAP-01 ack read at a fixed 2-byte index | Length-discriminated blob, CAP-02/CAP-03 read at **computed** offsets | Phase 143 (CAP-03), CAP-02 ported from `origin/beta` `13eb350` | D-17's central assertion is that `ver_end` is computed, not literal |
| Warning watermark measured warm | Watermarks are COLD figures; below-watermark returns `INFO` not `FAIL` | Phase 124 (`warm_vs_cold_correction`) | F-12/Pitfall 6: clean before measuring |

**Deprecated/outdated in this phase's inputs:**
- `141-NEW-TRACE.md` §5's arrays — stale on `0x08` (119, now 115). Reference for *method*, never for
  *values* (D-06).
- `firestarter/CLAUDE.md`'s "`native_loop_v131` … **71 cases total**" — stale by 8; measured 79 (F-01).
  Doc reconciliation is Phase 146's; do not quote it as a count here.
- `size_baseline_base01.json`'s v1.24 semantics — retired by D-11; its forward mechanism (the 0/64 B
  band) is kept and re-pointed.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | The new capture will total exactly 91 / 115 / 59. | F-06 | D-06 already labels this "a prediction to confirm, not to assume," and any deviation is stop-and-report. Verified only as far as the *current tip's* `Was` values recorded in `142-VPP-RECORD.md` §3 and `143-HOST-RECORD.md` §7.3 — **I did not run the capture** (it needs a native build, which belongs to the executor). If the total differs, D-07's 885 denominator moves with it. |
| A2 | D-07's six phase segments can be derived by the state machine in F-07 without further seams. | F-07 | I proved *primitive* partitionability on all 620 pre-change entries and verified the `OUTPUT_ENABLE` discriminator arithmetic exactly (7 + 12 = 19 on `0x07`). I did **not** validate the state machine against the *new* 265-entry stream, which does not exist yet. A new cadence could introduce a phase boundary the OE toggle does not mark. |
| A3 | No new native case is required for TEST-01…05. | F-02 | Based on name-level and docstring-level reading of all 88 cases, not on reading every assertion body. A case could be named for a behaviour it does not actually assert. D-01's gate proves names exist, not that they prove the requirement — that judgement stays human. |
| A4 | The two `*_v131` envs missing from `size_baseline_v131.json` should be added with both `native_envs` and `warnings.native` records. | C-01 | This is the file's own convention (followed for `native_trace_v131` and `native_pinmap_provisional`) but D-13 does not say so explicitly. Adding `warnings.native` records requires measuring two envs' cold warning counts, which no record holds — a real cost the planner should price or explicitly decline. |
| A5 | `PLATFORMIO_BUILD_FLAGS="-D EPROM_V131_TRACE_DUMP"` still triggers a rebuild on the current PlatformIO version. | F-06 | Cited from `141-NEW-TRACE.md` §1 where it demonstrably worked; not re-executed this session. Mitigated by recommending an explicit `rm -rf .pio/build/native_trace_v131` regardless, which makes the question moot. |

## Open Questions

1. **Does D-13's refresh add `warnings.native` records for the two missing envs, or only `native_envs`?**
   - What we know: the file records both blocks for all four envs it currently names; `native_loop_v131`
     and `native_params_v131` appear in neither (C-01).
   - What's unclear: D-13 says "refreshed from the same consolidated run" — a `pio test` run yields case
     counts naturally, but warning counts require the cold-build discipline and a separate `grep -cE`.
   - Recommendation: add `native_envs` for both (cheap, directly from the D-02 run) and add
     `warnings.native` **only if** the consolidated run is cold; otherwise record the gap explicitly in
     the phase record rather than writing a warm figure. Never write a warm figure into a watermark
     field.

2. **Should D-17's gate add `src/firestarter.cpp` to `firestarter_app/tests/scan_paths.py`?**
   - What we know: `test_scan_paths_resolve.py` asserts every listed entry resolves (`_FLOOR = 6`) but
     imposes **no completeness requirement** on new consumers (F-10).
   - What's unclear: whether the operator wants the inventory to stay a complete census (its docstring's
     stated intent: "a rename anywhere in that repo becomes ONE named failure instead of N anonymous
     skips") or only the 6 rekeyed Phase-123 modules.
   - Recommendation: add it. The inventory's own rationale argues for completeness, the cost is one
     dict entry, and it makes a future `firestarter.cpp` rename one named failure instead of a
     `MissingScanTargetError` surfacing from an unexpected module.

3. **Is `test_dump_v131_traces` in or out of D-01's mapping-gate scope?**
   - What we know: it is the 6th `RUN_TEST` in `test_trace_eprom_v131`, guarded by
     `#ifdef EPROM_V131_TRACE_DUMP` which no env defines (C-05).
   - What's unclear: whether the gate scopes to the three TEST-mapped suites or to all four v131 suites.
   - Recommendation: scope to the three (`test_loop_eprom_v131`, `test_vpp_eprom_v131`,
     `test_eprom_params_v131`) and say so in the module docstring, with the reason — the trace suite
     proves TEST-06, not TEST-01…05, and its case set is build-flag dependent.

4. **Does `size_baseline_v131.json:meta.frozen_for`'s instruction ("TEST-08 must pass `--baseline …_v131.json` explicitly") create a third measurement leg?**
   - What we know: D-09 names `size_baseline.json` as *the comparison anchor*; the v131 file's own note
     says TEST-08 must name it explicitly rather than relying on the default seam.
   - What's unclear: whether that means an *additional* `check_size_baseline.py` invocation against the
     v131 baseline, or merely that D-13's refresh must not be derived from the default seam.
   - Recommendation: read it as the latter (it is a re-derivation instruction, not a gate leg) and state
     the reading in the phase record so a v1.32 reader is not left guessing. The two are consistent: the
     v131 file is a *record*, not a gate — D-13 says so, and no code reads it.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| `git` | D-05, D-08 blob identity; both porcelain assertions | ✓ | on PATH | none — every gate resolves it fail-closed (a missing `git` is a FAILURE, never a skip) |
| `python3` (ambient) | firmware pytest suite | ✓ | 3.12 | — (firmware tests are version-tolerant; 292 pass) |
| `.venv/ci-replica/bin/python` | D-21 host measurement, F-12 CI parity | ✓ | **3.11.15** | none — ambient 3.12 makes the mypy gate **fail-open** |
| `ruff` | TEST-07 lint/format legs | ✓ (in the app repo's `[test]` extra) | repo-pinned | none |
| `mypy` (via `tools/check_mypy_watermark.py`) | TEST-07 type leg | ✓ | watermark 35 | none |
| PlatformIO Core (`pio`) | D-02 native runs, D-06 capture, TEST-07/08 AVR builds | assumed ✓ (six envs configured; prior phases measured with it) | 6.1.19 per baseline meta | **none** — every native and AVR leg is blocked without it |
| `avr-gcc` toolchain | AVR builds for TEST-08 | assumed ✓ (managed by PlatformIO) | 7.3.0 per baseline meta | none |
| Physical programmer board | — | ✗ (`/dev/ttyACM*` and `/dev/ttyUSB*` both absent) | — | **Not needed.** Phase 144 makes no bench claim (Phase 145 owns that). This is also *good* for the host suite: the `test_no_programmer_found_*` characterization tests go RED with a live board attached, so an empty bench is the correct measurement condition. |

**Missing dependencies with no fallback:** none identified that block this phase. PlatformIO and the AVR
toolchain were not invoked this session (deliberately — builds belong to executors), so their presence
is inferred from six configured envs and four prior phases of recorded measurements rather than
directly probed. An executor's first plan should confirm `pio --version` before scheduling long builds.

**Missing dependencies with fallback:** none.

## Validation Architecture

### The inverted question: how do you validate a validator?

Phase 144's deliverables are **gates**. A gate that passes proves nothing until you have seen it fail
for the right reason *and* pass for the right reason. D-18 states the first half; the known trap —
*a pre-authored leg can be unreachable, and RED proves nothing until the leg is also seen to pass for
the right reason* — states the second. Both halves are required evidence.

### Test Framework

| Property | Value |
|---|---|
| Framework (firmware gates) | pytest — `firestarter/tests/`, stdlib + pytest only, **no `conftest.py` anywhere in the repo** (recorded house rule) |
| Framework (firmware native suites) | Unity via PlatformIO `test_framework = unity` |
| Framework (host gates) | pytest — `firestarter_app/tests/`, run on `.venv/ci-replica/bin/python` (3.11.15) |
| Config file (firmware) | none for pytest; `platformio.ini` for the native envs |
| Config file (host) | `pyproject.toml` (`addopts = "-ra -q"` at :107; `# mypy_error_watermark = 35` at :174; ruff `py39`/88 at :110-111) |
| Quick run (firmware) | `cd /workspaces/firestarter && python3 -m pytest tests/ -q` → **292 passed in ~14 s** |
| Quick run (host, single module) | `cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/<module> -o addopts="" -q` → ~0.1–0.2 s |
| Full suite (firmware native, pinned) | `pio test -e native` and `-e native_nodevtools` → 141 cases / 17 suites each |
| Full suite (firmware native, v131) | `pio test -e native_params_v131` (9), `-e native_loop_v131` (79), `-e native_trace_v131` (5, 3 RED by design until D-06/D-08 land) |
| Full suite (host) | `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" --cov=firestarter --cov-report=term-missing --cov-fail-under=70` → baseline **1578 passed, 82.92%**, ~230 s |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| TEST-01 | 3 params cases exist and pass | unit (Unity) | `pio test -e native_params_v131` | ✅ 9 cases |
| TEST-01…05 | each requirement names cases that **actually exist** | gate (pytest, static) | `python3 -m pytest tests/test_requirement_case_mapping_v131.py -q` | ❌ **Wave 0** (D-01) |
| TEST-02 | 4 `test_loop01_*` pass | unit (Unity) | `pio test -e native_loop_v131 -f "*test_loop_eprom_v131*"` | ✅ within 47 |
| TEST-03 | 5 `test_loop03_*` + `test_loop04_no_live_row_emits_an_overprogram_pulse` pass | unit (Unity) | same | ✅ within 47 |
| TEST-04 | 3 `test_loop05_*` + `test_vpp02_{x3,x4,e1}` pass | unit (Unity) | `pio test -e native_loop_v131` (both suites) | ✅ 47 + 32 |
| TEST-05 | 4 `test_loop06_*` + 6 params fallback cases pass | unit (Unity) | `pio test -e native_loop_v131` + `-e native_params_v131` | ✅ (C-04 fixes the naming) |
| TEST-06 | 3 arrays re-frozen; identity gate GREEN on the new fixture | gate (pytest) | `python3 -m pytest tests/test_golden_trace_identity_eprom_v131.py -q` | ✅ module exists; currently GREEN on the OLD fixture |
| TEST-06 | new stream equals the new fixture positionally | integration (Unity) | `pio test -e native_trace_v131` → 5 cases, 0 failed | ✅ suite exists; **3 RED by design** until D-06/D-08 land |
| TEST-06 | all 885 entries attributed to exactly one segment | gate (pytest, static) | `python3 -m pytest tests/test_trace_segment_exhaustiveness_v131.py -q` | ❌ **Wave 0** (D-07) |
| TEST-07 | firmware pytest green | gate | `python3 -m pytest tests/ -q` → 292 | ✅ |
| TEST-07 | AVR builds green | build | `pio run -t clean -e <env>` then `pio run -e <env>` ×3 | ✅ envs exist |
| TEST-07 | pinned native envs at 141/17 | gate | `pio test -e native`, `-e native_nodevtools` | ✅ |
| TEST-07 | constants parity, present path | gate (pytest) | `.venv/ci-replica/bin/python -m pytest tests/test_revision_constants_parity.py -o addopts="" -q` → **14 passed (verified)** | ✅ |
| TEST-07 | constants parity, absent path skips cleanly | gate (pytest, subprocess) | `FIRESTARTER_FW_ROOT=<empty> … -rs -q` → **6 passed, 8 skipped (verified)** | ✅ |
| TEST-07 | CAP-03 byte layout agrees across repos | gate (pytest, cross-repo static) | `.venv/ci-replica/bin/python -m pytest tests/test_cap03_ack_layout_parity.py -o addopts="" -q` | ❌ **Wave 0** (D-17) |
| TEST-07 | CI-scoped ruff / mypy / coverage clean | gate | F-12's four commands verbatim | ✅ tooling present |
| TEST-08 | per-target flash/RAM measured vs PREP-03 | gate | `python3 scripts/check_size_baseline.py --avr-log uno=… --avr-log uno328pb=… --avr-log leonardo=…` (default baseline) | ✅ |
| TEST-08 | MERGE-05 band policy, disclosed per D-14 | gate | `… --policy merge05 --baseline scripts/baseline/size_baseline_base01.json` | ✅ |
| TEST-08 | warning watermarks hold | gate | `python3 scripts/check_build_warnings.py` per env | ✅ |

### Sampling Rate

- **Per task commit:** the owning repo's pytest suite — `python3 -m pytest tests/ -q` (firmware, ~14 s)
  or the touched module on the 3.11 replica (host, sub-second). **Commit first** (F-09).
- **Per wave merge:** firmware pytest (292) + both pinned native envs (141/17) + all three v131 envs by
  name; host full suite on the replica with `-o addopts=""`.
- **Phase gate:** the whole of F-12's command set, cold, with every verdict captured verbatim — this is
  D-02's "ONE cold consolidated run."

### Wave 0 Gaps

- [ ] `firestarter/tests/test_requirement_case_mapping_v131.py` — covers TEST-01…05 (D-01)
- [ ] `firestarter/tests/test_trace_segment_exhaustiveness_v131.py` — covers TEST-06 (D-07)
- [ ] `firestarter_app/tests/test_cap03_ack_layout_parity.py` — covers TEST-07 (D-17)
- [ ] `firestarter_app/tests/fixtures/planted_cap03_*.cpp` — D-18's planted violation for the above
- [ ] planted-violation inputs for the two firmware gates (scratch copies reached via the import-time
      env seam; a committed fixture is preferable where the input is small — F-15 item 1)
- [ ] Framework install: **none required.** Both suites already run.

### Per-gate planted-violation specification (D-18)

For each new gate: the concrete planted violation, and what the GREEN must be attributed to. **Both
transcripts, verbatim, in the plan's SUMMARY.**

| Gate | Planted violation (turns it RED) | RED evidence must show | GREEN evidence must show |
|---|---|---|---|
| **D-01 mapping** | A scratch copy of `test_loop_eprom_v131.cpp` with `test_loop01_pulse_width_never_grows_between_attempts` **renamed** to `..._never_grows`, reached via `FIRESTARTER_CASE_MAP_SCAN_ROOT` in a **child process**. This is the exact defect D-01 names: "a requirement flipped against a case that was later renamed or deleted." | the failure message **names the missing case and the requirement (TEST-02)** — not a bare "lists differ" | the non-vacuity leg reports `>= 88` extracted names, and the per-requirement legs each name a non-zero count. A GREEN with an empty extraction set is the unreachable-leg trap. |
| **D-01 mapping, second plant** | The same scratch root but **emptied** (a directory with no `.cpp`). | the **non-vacuity** leg fails, not the mapping legs — proving an empty parse cannot pass vacuously | (as above) |
| **D-07 exhaustiveness** | A scratch copy of the new fixture with **one entry mutated to an unclassifiable shape** — e.g. `{2, 0x40, 0x01, 0UL}` (pin `0x40` is not one of the five known pins). | the message **names the entry's array, its positional index, and its (kind,pin,value,us)** — an unattributed entry must be locatable, not just counted | the segment index sets **partition `range(len(array))` exactly** for all six arrays, and the totals sum to **885**. A GREEN that only compares counts is the trap (Pitfall 3). |
| **D-07 exhaustiveness, second plant** | A scratch copy with **one entry deleted and one duplicated** (length unchanged). | the **set-equality/overlap** leg fails while a count-only check would pass — proving the count check is not the load-bearing one | (as above) |
| **D-17 CAP-03 layout** | A committed fixture `.cpp` in `firestarter_app/tests/fixtures/` that is `src/firestarter.cpp` with `_ready[4 + _vlen]` replaced by a **literal `_ready[13]`**, reached by `monkeypatch.setattr` on the module's path constant (the `FIRMWARE_HEADER` pattern at `test_revision_constants_parity.py:148` / `:733`). This is BF-1's shape: a wire layout changed on one side with nothing comparing them. | the message **names the literal index and the computed offset it should have been** | the gate resolves the **real** `src/firestarter.cpp` via `fw_path`, finds the five real index expressions, and matches them against `serial_comm.py`'s five real offsets — with a non-vacuity leg proving the extraction was non-empty. |
| **D-17, second plant** | A fixture with the budget bytes **omitted from the emitted length** (`(uint8_t)(4 + _vlen)` instead of `+ 2`). | a **silent capability loss** is caught loudly — this is the failure mode that would leave the host's attribute `None` forever | (as above) |

**Committed-fixture preference:** where the planted input is small enough to commit (D-17's two `.cpp`
fixtures), commit it. That is what keeps 6 of `test_revision_constants_parity.py`'s 14 legs live even
with **no firmware checkout present** (F-11) — the same property is worth having for a CAP-03 gate whose
real scan target lives in the other repo.

## Security Domain

> `security_enforcement` is absent from `.planning/config.json`, so it is treated as enabled. Scoped
> honestly: this phase authors test gates and rewrites JSON records. It ships no user-facing surface, no
> network path, no authentication, no session, no data persistence and no cryptography.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | No auth surface in scope. |
| V3 Session Management | no | No sessions. |
| V4 Access Control | no | No access-control surface. |
| V5 Input Validation | **yes, narrowly** | Every new gate parses untrusted-in-principle file content (C source, JSON). Controls, all already house convention: bounded regex (no catastrophic backtracking — the existing `_ENTRY_RE = \{[^{}]*\}` is linear and non-nesting by construction), `json.loads` on committed data only, non-vacuity floors so an empty/malformed parse **fails closed**, and `subprocess.run` with **list-form argv, never `shell=True`** (`test_golden_trace_identity_eprom_v131.py:112-128` is the reference implementation). |
| V6 Cryptography | no | Blob SHAs are computed by `git` (`rev-parse` / `hash-object`) — content addressing, not a security control. No hand-rolled hashing; none needed. |
| V12 Files & Resources | **yes, narrowly** | Every planted-violation write goes under `tmp_path` (or a committed `tests/fixtures/` path), and each planted test asserts the **real** file's blob SHA is unchanged before and after — the "the plant never touched the source of truth" ceremony at `test_flash_path_record_sync.py:1242-1250` and `test_py32_flash_map_host.py:384-395`. Reuse that ceremony verbatim for every new plant. |
| V14 Configuration | **yes, narrowly** | Five env seams are read at import. Each must be documented in its module's docstring (the repo has **no central env-variable inventory**, so the docstring is the only discoverable site) and must override a **path only**, never a marker name or a policy literal — `fw_presence.py:66-76` states the rationale: "making the marker name overridable too would be one more knob that can be set wrong in a real run." |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---|---|---|
| A gate that silently skips (missing `git`, absent repo, empty parse) and reports exit 0 | **Repudiation** — the record claims verification that never happened | Fail-closed `git` resolution via a plain `assert`; non-vacuity floors as hardcoded literals; a self-check that the module contains no `pytest.skip` / `@pytest.mark.skipif`. All three already exist as house patterns (F-15). |
| A planted-violation test that writes to the real tree | **Tampering** | `tmp_path` only + before/after blob-SHA assertion + the porcelain assertion (F-09). Already the ceremony. |
| `subprocess` with a shell string built from a path | **Elevation of privilege / Tampering** | List-form argv, `shell=False` (the default), binary resolved via `shutil.which`. Never string-interpolate a path into a command. |
| An env seam that redirects a gate to an attacker-chosen (or merely stale) target, making it pass vacuously | **Tampering / Repudiation** | The two-half non-vacuity pattern: one leg recomputes the default target from the repo root **without reading `os.environ` at all**, so a stray seam value cannot make it pass. This is the `check_permitted_claims.py`-`_HERE` landmine, closed by construction in `test_hv_routing_source_contract_v142.py`'s Coverage 14 and `test_ack_layout_source_contract_v143.py`'s Coverage 8. |
| An overclaim in the phase record (e.g. "MERGE-05 green" without the anchor disclosure) | **Repudiation** | D-14's constrained sentence; Phase 146's claim gate is the backstop, but stating the fact is this phase's job (Pitfall 4). |
| Catastrophic regex backtracking on a 38 KB / 649-line header | **Denial of service** (self-inflicted, in CI) | The existing patterns are linear: `\{[^{}]*\}` cannot nest, and `_ARRAY_DECL_RE`'s `(.*?)` is bounded by a literal `};`. Do not introduce nested quantifiers. |

**Honest non-claim:** nothing in this phase changes the firmware's high-voltage behaviour, so nothing
here is a *safety* control. The `disables every high-voltage route` clause of TEST-04 is proven by
existing native cases in the emitted control-register stream only — never on a part. That boundary is
Phase 145's, and this phase must not be recorded as narrowing it.

## Sources

### Primary (HIGH confidence — read on disk this session)

**Firmware repo (`/workspaces/firestarter` @ `59a8a42`, branch `gsd/v1.31-27c-programming-algorithm-fidelity`)**
- `test/native/avr/_shared/eprom_v131_expected.h` — 649 lines; typedef (:77-82), kind constants (:88-91), `v131_merged_length` (:94), `v131_merged_at` splice rule (:111-140), the three arrays (:274/:411/:555) and their `_LEN` macros; independently parsed to 198/221/201
- `test/native/avr/_shared/host_stubs_common.inc` — recorder internals (:87-131, :161-191), caps `HOST_STUBS_MAX_STROBES` :102 / `HOST_STUBS_MAX_TIMINGS` :168
- `test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp` — fixture include :45, `millis()` pin :92, dump machinery :341-376, `main()` :378-396
- `test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` — 47 `RUN_TEST`; advancing-clock harness :113-179
- `test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp` — 32 `RUN_TEST`
- `test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp` — 9 `RUN_TEST`
- `tests/test_golden_trace_identity_eprom_v131.py` — the six-assertion gate; `_FIXTURE_PATH` :78, `_CONSUMERS` :80-82, `_parse_arrays` :131-144, blob leg :155-165, no-skip self-check :222-244
- `tests/golden/eprom_v131_trace_inventory.json` — blob `f102a5ed…`; `meta.blob_sha` = `ca3e09f1…`; arrays 198/221/201; `how_to_update` and `frozen_for` quoted verbatim in F-05
- `tests/golden/protocol_branch_inventory.json` — both pins verified against `HEAD:`
- `tests/test_protocol_branch_inventory.py` — `test_params_table_has_no_second_selector` :495
- `tests/test_checker_convention.py` — `CHECKER_GLOB` :129, `FLOOR = 6` :132, `FIXTURE_FLOOR = 15` :133, seven tests documented :108-146
- `tests/test_flash_path_record_sync.py` — `_git_porcelain` :252, whole-repo assertion :1247
- `tests/test_ack_layout_source_contract_v143.py` — 10 coverage items; the explicit hand-off of the cross-repo comparison to Phase 144 / TEST-07
- `tests/test_write_path_source_contract_v131.py` :150, `tests/test_hv_routing_source_contract_v142.py` :200-208, `tests/test_progress_emission_is_leonardo_only.py` :206-210 — the env-seam pattern
- `src/firestarter.cpp` :160-212 — the `MSG_OK_READY` pack, wire-layout comment :168
- `src/proms/eprom_params.cpp` :28-62 — the three rows and `eprom_params_for`
- `src/proms/eprom.cpp` — progress emit :322-327, :398-401
- `include/rurp_shield.h` :53-57 — the five pin constants
- `include/rurp_pinout.h` :19-21, :75-76, :96 — the legacy/rev2 drop-bit split
- `include/rurp_register_utils.h` :24-90 — cache elision, revision mapping, the 1 µs post-latch settle
- `scripts/check_size_baseline.py` — :91-127 seams/regexes, `AVR_ENVS` :99, `NATIVE_ENVS` :100, band :107, `ParseError` :130, `compare_avr` :183, `compare_avr_policy_merge05` :214, `compare_native`, `main()`
- `scripts/check_build_warnings.py` — `AVR_ENVS` :86, `NATIVE_ENVS` :87, `check_env` :121-165
- `scripts/baseline/size_baseline.json`, `…_base01.json`, `…_v131.json` — all three read in full
- `platformio.ini` — nine env blocks; :293/:331/:373 and their caveat comments; `test_filter` counts
- `CLAUDE.md` — the three-row algorithm table, CAP-01/02/03 section, native-env exception blocks

**Host repo (`/workspaces/firestarter_app` @ `f77b0ea`, same branch)**
- `tests/fw_presence.py` — read in full (141 lines); binding warning :35-45, seam :77-80, marker :86-88, `requires_fw` :102, `MissingScanTargetError` :105, `fw_path` :117-140
- `tests/test_revision_constants_parity.py` — `FIRMWARE_HEADER` :148, fixture constants :727-730, three planted legs :733-786
- `tests/test_py32_flash_map_host.py` — `_git_porcelain` :232, sibling-repo assertion :391
- `tests/scan_paths.py` — `CROSS_REPO_TEST_PATHS` (6) / `CROSS_REPO_TOOL_RESOLVERS` (11)
- `tests/test_scan_paths_resolve.py` — `_FLOOR = 6` :47; four tests
- `tests/test_skip_census.py` — verified to pin no counts
- `tools/check_no_exists_proxy.py` — `_DEFAULT_TARGETS` :125 (explicit list, not a glob)
- `tools/check_mypy_watermark.py` — `get_watermark()` regex :91-104, `enforce_watermark` :211-227
- `firestarter/serial_comm.py` — `_decode_id_frame` :344-442, `WRITE_BUDGET_MAX_S` :77
- `tests/test_hw_revision_gate.py` — `_cap03_params` :175, CAP-03 legs :246-341
- `.github/workflows/ci.yml` :81/:84/:87/:90; `pyproject.toml` :107 addopts, :110-111 ruff, :174 watermark

**Commands executed this session (all read-only or sandboxed)**
- `git rev-parse HEAD:<path>` ×3, `git hash-object` ×2, `git status --porcelain` ×3 (both repos + meta)
- `grep -c 'RUN_TEST('` per suite + uniqueness cross-check
- an independent field-capturing parse of all 620 fixture entries with a candidate segment classifier
- `python3 -m pytest tests/ -q` (firmware) → **292 passed in 13.73 s**
- `.venv/ci-replica/bin/python -m pytest tests/test_revision_constants_parity.py -o addopts="" -q` → **14 passed**
- `FIRESTARTER_FW_ROOT=<empty> .venv/ci-replica/bin/python -m pytest … -rs -q` → **6 passed, 8 skipped**
- `.venv/ci-replica/bin/python -m pytest tests/test_hw_revision_gate.py -o addopts="" -q` → **27 passed**
- `.venv/ci-replica/bin/python --version` → **Python 3.11.15**
- `ls /dev/ttyACM* /dev/ttyUSB*` → both absent (no board attached)

### Secondary (HIGH-MEDIUM — prior-phase records, cross-checked against the tree where possible)

- `.planning/phases/138-preconditions-baseline/138-BASELINE.md` §4 (:180-205) — the frozen trace, the two pinning mechanisms; §5 the size/suite/watermark baseline
- `.planning/phases/141-per-byte-program-loop/141-NEW-TRACE.md` §1 (capture commands, cwd constraint), §2 (banners 91/119/59 — **stale**), §5 (arrays), §6 (env counts in prose)
- `.planning/phases/142-high-voltage-routing/142-VPP-RECORD.md` §3 (:200-215) — the `Was` table, `0x08` 119→115; §15 F-142-04
- `.planning/phases/143-host-timeout-progress-pulse-override/143-HOST-RECORD.md` §7.1 (:227-248) cold flash/RAM; §7.3/non-claim 4 (:158-162) zero added frames; §7.6 (:405-427) host-suite 1578/82.92%
- `.planning/REQUIREMENTS.md` :226-243 — TEST-01…08 verbatim
- `.planning/ROADMAP.md` :431-443 — goal, dependencies, four success criteria
- `.planning/STATE.md` — `current_phase: 144`, `status: verifying`, 45/45 plans complete through Phase 143

### Tertiary (LOW — noted, not relied on)

- `.planning/graphs/graph.json` — **stale: 1037 h old, 1188 commits behind** (`built_at_commit f4150b8` vs `current_commit e503f07`). Deliberately **not queried**; at that drift any semantic relationship it reports would be about a tree that no longer exists. No finding in this document derives from it.
- `firestarter/CLAUDE.md`'s "71 cases total" for `native_loop_v131` — stale by 8; superseded by the measured 79 (F-01).

## Metadata

**Confidence breakdown:**
- Anchor verification (the 32-row ledger): **HIGH** — every row read on disk this session with the exact file:line or command that produced it.
- Corrections C-01…C-05: **HIGH** — each is a direct on-disk contradiction of a stated figure, reproducible with one command.
- Case counts and the TEST-01…05 map: **HIGH** for existence and counts (programmatic extraction, uniqueness cross-checked); **MEDIUM** for sufficiency, since I read names and docstrings rather than every assertion body (see Assumption A3).
- D-07 arithmetic (885): **HIGH** — 620 re-derived independently; 265 is D-06's prediction, so the sum inherits A1's status.
- D-07 segmentation design: **MEDIUM-HIGH** — primitive partitionability proven on all 620 pre-change entries and the `OUTPUT_ENABLE` discriminator verified exactly (7+12=19); the new 265-entry stream does not exist yet (A2).
- D-06 capture mechanics: **HIGH** for the source facts (helper location, `#ifdef`, `printf` comment, `millis()` pin, output format); **MEDIUM** for the command line, cited from `141-NEW-TRACE.md` §1 and not re-executed (A5) — mitigated by recommending an explicit clean.
- D-16/D-17 host mechanics: **HIGH** — the absent-path mechanic was *executed* this session, both directions, with transcripts; both sides of the CAP-03 layout were read line by line.
- Convention/floor hazards (F-08, F-09, F-10): **HIGH** — floors and assertion sites read directly, counts measured against them.
- PlatformIO / avr-gcc availability: **MEDIUM** — inferred from six configured envs and four phases of recorded measurements; not probed this session.

**Research date:** 2026-08-13
**Valid until:** ~7 days, or until the next commit lands in either sub-repo — whichever comes first. Six of the anchor facts are blob SHAs and porcelain states, which any commit can move. Re-run the anchor ledger's commands if planning slips past the next commit; the 32 rows are cheap to re-verify and expensive to be wrong about.
