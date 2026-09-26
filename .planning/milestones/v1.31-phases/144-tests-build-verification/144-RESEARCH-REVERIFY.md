# Phase 144: Tests & Build Verification — Research Re-verification

> **Supplementary, not canonical.** `144-RESEARCH.md` is the canonical research the seven plans were
> authored from, and its `C-0N` / `F-NN` / `Pitfall N` IDs are the ones the plans cite. This document
> is a second pass run at the phase tip *after* `144-01` landed, under its own `R-NN` / `A-NN` ID
> space. **Its `C-01` and its `Pitfall N` numbering are NOT the ones the plans reference** — resolve
> every plan citation against `144-RESEARCH.md`.
>
> It confirms the canonical research and adds measured figures. Three items are new:
> **C-01** (`eprom_v131_expected.h` is `#include`d by `test_trace_eprom_v131.cpp:45` — already handled
> correctly by plan `144-03`), **A-01** (a third porcelain coupling at
> `test_py32_asset_name_host.py:323` — `144-06`'s porcelain-empty precondition already covers it), and
> **A-02** (firmware CI does run `pytest tests/ -v` at `build.yml:161`, so D-15's absence must stay
> scoped to the three `*_v131` envs — which is how `144-07` already words it).
>
> The one genuinely open item: the **cold native warning count** was not re-measured. The watermark is
> `<= 1166` with zero headroom, so this should be the first measurement of `144-05`'s consolidated run.

---

# Phase 144: Tests & Build Verification - Research (re-verification pass)

**Researched:** 2026-08-14
**Domain:** Gate authoring and build/size measurement across a dual-repo tree (PlatformIO C++ firmware + Python host CLI)
**Confidence:** HIGH — every load-bearing anchor was re-executed on disk this session, not recalled

## Summary

This is a **verification** phase. CONTEXT.md's 23 decisions are locked and unusually concrete: file
paths, line numbers, blob SHAs, byte counts, predicted capture totals. This research does not
re-litigate them. It re-runs the ground truth they rest on at the current tip and surfaces the
mechanics an executor would otherwise get wrong.

**Headline: every numeric prediction in CONTEXT.md was confirmed by live execution this session.**
The trace capture measures **91 / 115 / 59** exactly as D-06 predicts (`strobe_overflow=0`,
`timing_overflow=0` on all three), so D-07's `885 = 620 + 265` denominator is arithmetic, not
forecast. The AVR tip measures **24824 / 24874 / 26906** with RAM unmoved, exactly as D-09 states;
`leonardo` sits at 93.8% with 1766 B headroom. The host suite measures **1578 passed at 82.92%** on
the CI-parity interpreter, exactly as D-21 records. `native`/`native_nodevtools` report **141/141**,
`native_loop_v131` **79/79**, `native_params_v131` **9/9**. Both standing REDs reproduce verbatim.
F-138-05's uncaught `KeyError` reproduces live.

**One correction and two additions**, none of which reverses a decision:

- **C-01 (correction, D-05):** `eprom_v131_expected.h` **is** `#include`d today, by
  `test_trace_eprom_v131.cpp:45`. D-05's "included by nothing" is true only of the *post-rename*
  `_prechange.h`. A bare `git mv` therefore breaks the `native_trace_v131` build; the new fixture
  must land at the **old path, in the same commit**, and must keep the old **filename** because
  `test_golden_trace_identity_eprom_v131.py:212-219` hard-asserts the consumer still contains that
  literal include string.
- **A-01 (addition, D-20):** a **third** porcelain coupling exists —
  `firestarter_app/tests/test_py32_asset_name_host.py:323` asserts `_git_porcelain(FW_ROOT) == ""`
  with the same shape as `test_py32_flash_map_host.py:391`. Two host modules, not one, go RED on a
  dirty firmware tree.
- **A-02 (addition, D-15):** `pytest tests/ -v` **does** run in firmware CI (`build.yml:161`,
  `beta-build.yml:134`). D-15's "no CI" is precisely about the three `pio test -e *_v131` envs. The
  new pytest gates will be CI-covered once the branch reaches `main`/`beta`. Saying "CI covers none
  of this" would be an *under*claim about the gates and would mis-state the actual hole.

**Also: plan 144-01 has already executed.** Firmware `HEAD` is
`16e5bdc test(144-01): author the requirement->case mapping gate (D-01)`, which landed
`firestarter/tests/test_requirement_case_mapping_v131.py` (535 lines). D-01's deliverable exists and
is green. Research below reports its actual shape and independently re-verifies its map, rather than
proposing one.

**Primary recommendation:** author every new gate as a **pytest module under
`firestarter/tests/` or `firestarter_app/tests/`, never as `firestarter/scripts/check_*.py`** — the
latter triggers `test_checker_convention.py`'s seven-part convention (paired test module + planted
fixture + two floors raised in the same commit). Land D-05's rename, D-06's new fixture and D-08's
inventory rewrite in **one commit**, deriving the new blob SHA with `git hash-object` rather than a
second commit. Sequence every firmware file creation behind a `git commit` before running either
repo's suite (D-20, A-01).

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
  skipping — blocked on deciding which firmware ref the app's CI should pin (D-16).
- **An end-to-end synthetic-row overprogram oracle** — D-03's reversed option. Reachable only via a
  seventh env with a substituted params TU, or a seam in blob-pinned `src/`.
- **F-141-11 / F-143-02 / F-143-03: the unscoped whole-repo porcelain assertions** in
  `test_flash_path_record_sync.py` and `test_py32_flash_map_host.py`. Recorded-not-fixed; D-20 works
  around them rather than fixing them here.
- **Gate-asserting `eprom_v131_expected_prechange.h`** — D-08 leaves it un-gated by choice.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description (`.planning/REQUIREMENTS.md:226-243`) | Research Support |
|----|---------------------------------------------------|------------------|
| TEST-01 | Native tests prove `0x07`/`0x08`/`0x0B` each resolve to their own table row | §R-02: 3 mapped cases in `test_eprom_params_v131`, all verified to exist; gate already landed |
| TEST-02 | Fixed-width pulse/verify per byte, no escalation between attempts | §R-02: 4 mapped `test_loop01_*` cases, all verified to exist |
| TEST-03 | Overprogram duration derives from pulse count and honours `overprogram_cap_us` | §R-02: 5 `test_loop03_*` + the `test_loop04_no_live_row_emits_an_overprogram_pulse` non-claim witness |
| TEST-04 | Max-pulse failure aborts the block, reports the address, disables every HV route | §R-02: 3 `test_loop05_*` + 3 `test_vpp02_*`; the address clause is asserted *inside* `test_loop05_a_byte_that_misses_within_max_pulses_aborts_the_block` |
| TEST-05 | `0xFF`/already-matching skips plus the `pulse_delay == 0` fallback | §R-02: 4 `test_loop06_*` + two families of three `*_pulse_delay_*` cases (C-04 correction already frozen in the landed map) |
| TEST-06 | Pre-change traces frozen, new traces authored, diff attributable strobe by strobe | §R-05…R-11: rename mechanics, live 91/115/59 capture, 885 denominator, inventory field map |
| TEST-07 | All four envs build+pass, host suite passes, CI-scoped ruff/mypy clean, constants parity holds | §R-12…R-18, R-21, R-23: measured green state for every leg, CAP-03 offsets, absent-path command |
| TEST-08 | Per-target flash/RAM delta measured vs PREP-03, Leonardo ceiling watched | §R-19, R-20: measured tip, both RED verdicts verbatim, JSON schema, no-checker-edit confirmation |
</phase_requirements>

---

## Project Constraints (from CLAUDE.md)

Extracted from `/workspaces/CLAUDE.md`, `/workspaces/firestarter/CLAUDE.md`,
`/workspaces/firestarter_app/CLAUDE.md`. All are binding on plans in this phase.

| # | Directive | Source | Relevance here |
|---|-----------|--------|----------------|
| 1 | Meta-repo tracks only `.planning/` and `.claude/`; neither sub-repo is committed here | `/workspaces/CLAUDE.md` | D-19's `commits_land_in:` must name `firestarter` / `firestarter_app` / `meta` explicitly |
| 2 | `serial_comm.py` and `firestarter.cpp` protocol changes must stay in sync | `/workspaces/CLAUDE.md` | This is exactly what D-17's gate mechanises |
| 3 | `constants.py` ↔ `firestarter.h` / `rurp_pinout.h` / `rurp_shield.h` constant pairs change together | both sub-repo CLAUDE.md | D-16's parity sweep |
| 4 | `include/messages.h` is **codegen-generated and id-only** — never hand-edit; `MSG_OK_READY` is `param_bytes = -1` so CAP-01/02/03 needed zero codegen | firmware CLAUDE.md | D-17's gate must not assume a `messages.toml` entry describes the payload |
| 5 | `chip_database.json` is generated — never hand-edit | app CLAUDE.md | Not touched this phase; noted so no plan drifts into it |
| 6 | Tooling gate: `ruff check` + `ruff format --check` + `mypy` (strict on 8 modules) + `pytest --cov-fail-under=70`, enforced by `.github/workflows/ci.yml` | app CLAUDE.md | TEST-07's CI-scoped leg; commands verified in §R-21 |
| 7 | A new native suite must be added to **both** pinned envs' `test_filter` and `-I` lists — **overridden** for `*_v131` envs, which are added to neither | firmware CLAUDE.md | D-04 means no new suite is authored, so this rule is not exercised; it is the reason the `*_v131` envs exist |
| 8 | `test_flash_path_record_sync.py` runs in **no CI leg on this branch** — enforcement is a local-run obligation | firmware CLAUDE.md | Reinforces D-20's sequencing |

**Project skills:** `.claude/skills/` holds `devtest-rootcause`, `devtest-triage`, `find-skills`,
`skill-writer`. None carries `rules/*.md`, and none applies to this phase — the two `devtest-*`
skills are chip-datasheet triage workflows for `dev test` issues, which this phase does not touch.
No `.agents/skills/` directory exists. Confirmed by directory listing, not assumed.

---

## Architectural Responsibility Map

This phase adds no runtime capability. The tiers below are *evidence* tiers — which repo/mechanism
owns proving each claim.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| TEST-01…05 requirement→case mapping | Firmware repo, `firestarter/tests/` (pytest, source-scan) | — | Scans firmware suite sources; living in the firmware repo removes any cross-repo presence proxy that could fail open |
| TEST-01…05 behavioural proof | Firmware repo, `pio test -e native_loop_v131` / `-e native_params_v131` (Unity/native) | — | The 88 cases already exist; the mapping gate never re-proves them |
| TEST-06 trace capture | Firmware repo, `native_trace_v131` binary run directly | — | `pio test` swallows `printf`; the dump is a built-binary invocation |
| TEST-06 fixture identity | Firmware repo, `firestarter/tests/` (pytest + `git rev-parse`) | — | Blob identity is a git fact; two independent pins per golden |
| TEST-07 constants parity | Host repo, `firestarter_app/tests/` (reads firmware headers via `fw_path`) | Firmware repo (source-contract pins) | Every existing parity gate lives host-side; `fw_presence.py` is the sanctioned probe |
| TEST-07 CAP-03 byte layout | Host repo, `firestarter_app/tests/` (reads `firestarter/src/firestarter.cpp`) | Firmware `test_ack_layout_source_contract_v143.py` (in-repo half) | Neither existing half compares the two sides; D-17 is the comparison |
| TEST-07 lint/type/coverage | Host repo, `.venv/ci-replica` (py3.11) | — | Ambient 3.12 makes the mypy watermark fail-open |
| TEST-08 size measurement | Firmware repo, `pio run` + `scripts/check_size_baseline.py` | — | Baselines and the comparator both live in `firestarter/scripts/` |

---

## Standard Stack

No package is installed by this phase. Everything below is already present and was version-checked
this session.

### Core (measured this session)

| Tool | Version | Purpose | Where verified |
|------|---------|---------|----------------|
| PlatformIO Core | 6.1.19 (per baselines) | native + AVR builds/tests | `/usr/local/bin/pio` |
| Unity | via `test_framework = unity` | native test harness | `platformio.ini` |
| ArduinoFake | `fabiobatsilva/ArduinoFake@^0.4.0` | native `rurp_*` stubs | `platformio.ini` native envs |
| Python (CI parity) | **3.11.15** | host suite / lint / types | `.venv/ci-replica/bin/python --version` |
| pytest | **9.1.1** | both repos' gate suites | `.venv/ci-replica/bin/python -m pytest --version` |
| ruff | **0.16.1** | lint + format check | `-m ruff --version` |
| mypy | **2.3.0** | watermark gate | `-m mypy --version` |
| Python (ambient) | 3.12 | firmware `pytest tests/` | `python3` in `/workspaces/firestarter` |

`ruff`'s configured `select` is `[E, F, I, UP]` — narrower than default. A `# noqa: BLE001` in this
repo is inert (recorded project fact); do not add one expecting it to do anything.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pytest module under `tests/` | `scripts/check_*.py` checker | Triggers `test_checker_convention.py`'s 7 legs: paired `tests/test_check_<X>.py`, a `planted_<X>*` fixture, a `returncode != 0` assertion, and **both** `FLOOR = 6` / `FIXTURE_FLOOR = 15` raised in the same commit (`tests/test_checker_convention.py:129-130`). Both floors sit at exactly the current counts. Use only if the gate genuinely needs a CLI. |
| `git hash-object` to derive the new blob SHA in one commit | Two commits (land fixture, then read `HEAD:` and land JSON) | `test_blob_sha_matches_the_recorded_inventory` reads `git rev-parse HEAD:<path>`, so the JSON cannot be authored from `HEAD` before the fixture is committed. `git hash-object <path>` yields the identical content-addressed SHA and permits a single atomic commit. |
| `--rebuild` on both checkers | Capture logs with `pio run`/`pio test`, then pass `--*-log ENV=PATH` | `--rebuild` invokes `pio` itself (the only mode that *guarantees* a clean build per the script's own non-claim) but gives no reusable artifact for the phase record. Log capture is what every prior phase recorded. |

**Installation:** none. This phase installs nothing.

## Package Legitimacy Audit

**Not applicable — this phase installs no external package in either repo.** No `npm install`, no
`pip install <newpkg>`, no `lib_deps` addition. The only dependency changes possible would be a new
`lib_deps` entry in `platformio.ini` (D-04 forbids the env work that would motivate one) or a new
`[test]` extra in `firestarter_app/pyproject.toml` (nothing in the decision set requires one).

**Packages removed due to [SLOP] verdict:** none — no packages were evaluated.
**Packages flagged as suspicious [SUS]:** none.

If a plan finds itself needing a new dependency, that is a signal it has drifted out of this phase's
boundary — stop and report, per D-04's precedent.

---

## Findings — the six prioritised unknowns

Every claim below carries the command or the file:line it came from.

### R-01 — The 88 / 79 reconciliation is arithmetic, not a conflict `[VERIFIED: measured]`

```
$ cd /workspaces/firestarter && for d in test_loop_eprom_v131 test_vpp_eprom_v131 test_eprom_params_v131; do
    grep -rho 'RUN_TEST *( *[A-Za-z0-9_]*' test/native/avr/$d/ | wc -l; done
47
32
9
```

`platformio.ini`'s `[env:native_loop_v131]` names **two** suites in its `test_filter`
(`native/avr/test_loop_eprom_v131` and `native/avr/test_vpp_eprom_v131`, added by Phase 142's
addendum block). So:

| Env | Suites | Cases | Measured this session |
|-----|--------|-------|-----------------------|
| `native_loop_v131` | `test_loop_eprom_v131` + `test_vpp_eprom_v131` | 47 + 32 = **79** | `79 test cases: 79 succeeded in 00:00:19.326` |
| `native_params_v131` | `test_eprom_params_v131` | **9** | `9 test cases: 9 succeeded in 00:00:12.191` |
| **Total across the three mapped suites** | 3 | **88** | — |
| `native` | 17 | 141 | `141 test cases: 141 succeeded` |
| `native_nodevtools` | 17 | 141 | `141 test cases: 141 succeeded` |
| `native_trace_v131` | `test_trace_eprom_v131` | 5 registered (6 reported, see R-09) | **RED** — `6 test cases: 3 failed, 2 succeeded` |

CONTEXT.md's "88 existing cases" (§Reusable Assets) and D-13's "`native_loop_v131` has grown to 79
cases" are both correct and describe different denominators: 88 is the **suite** total across all
three mapped suites; 79 is one **env's** total. No reconciliation work is owed.

`firestarter/CLAUDE.md`'s "Phase 142 addition" paragraph still says `test_loop_eprom_v131` has **39**
cases and the env totals **71** — stale by 8 cases. Not this phase's requirement to fix, but a plan
touching that file should not copy the number.

### R-02 — D-01's mapping gate has already landed; its map is independently confirmed `[VERIFIED: measured]`

Firmware `HEAD` is `16e5bdc test(144-01): author the requirement->case mapping gate (D-01)`, dated
2026-08-14 06:19Z, adding `firestarter/tests/test_requirement_case_mapping_v131.py` (+535 lines,
one file, nothing under `src/` — D-04 preserved).

I re-derived the map from that file and cross-checked every name against a fresh, independent parse
of the three suite sources:

```
total unique cases: 88
mapped unique:      29
MISSING:            (none)
unmapped:           59
```

The frozen `_REQUIREMENT_CASES` map, verbatim:

| Req | Cases (all verified present) |
|-----|------------------------------|
| **TEST-01** (3) | `test_each_protocol_resolves_to_its_own_distinct_row`, `test_unknown_protocol_returns_null`, `test_row_values_match_the_frozen_table` |
| **TEST-02** (4) | `test_loop01_pulse_width_never_grows_between_attempts`, `test_loop01_each_byte_gets_exactly_the_seeded_number_of_fixed_width_pulses`, `test_loop01_verify_read_follows_every_pulse`, `test_loop01_a_byte_that_converges_on_its_last_permitted_pulse_succeeds` |
| **TEST-03** (6) | `test_loop03_overprogram_duration_is_three_times_the_pulse_count_times_the_width`, `test_loop03_overprogram_is_zero_when_the_factor_is_zero`, `test_loop03_overprogram_clamps_at_the_cap_rather_than_refusing`, `test_loop03_overprogram_is_32_bit_safe_at_the_uint16_ceiling`, `test_loop03_a_zero_cap_yields_no_overprogram_pulse`, `test_loop04_no_live_row_emits_an_overprogram_pulse` |
| **TEST-04** (6) | `test_loop05_a_byte_that_misses_within_max_pulses_aborts_the_block`, `test_loop05_the_loops_own_strobes_disable_the_high_voltage_route`, `test_loop05_a_successful_block_does_not_disable_the_route`, `test_vpp02_x3_the_energy_cap_exit_disables_the_route`, `test_vpp02_x4_the_final_pass_verify_failure_disables_the_route`, `test_vpp02_e1_write_init_error_exit_leaves_no_route_asserted` |
| **TEST-05** (10) | `test_loop06_an_ff_target_byte_is_never_read_and_never_pulsed`, `test_loop06_an_already_matching_byte_is_read_once_and_never_pulsed`, `test_loop06_a_block_of_only_skipped_bytes_emits_no_pulse_at_all`, `test_loop06_the_ff_rule_does_not_suppress_the_final_verify_pass`, `test_0x0{7,8,B}_zero_pulse_delay_takes_the_{1000,100,500}us_fallback` (3), `test_0x0{7,8,B}_nonzero_pulse_delay_is_left_alone` (3) |

**There is no genuine TEST-01…05 gap.** The 59 unmapped cases are harness/setup cases
(`test_setup_*`, `test_readback_model_*`, `test_timing_hook_*`, `test_logged_id_capture_*`) and cases
owned by *other* requirements from earlier phases — `test_budget_*` (HOST-01), `test_progress_*`
(HOST-02), `test_loop04_energy_cap_*` / `test_loop07_*` (LOOP-04/LOOP-07), `test_loop08_*` /
`test_vpp01_*` / `test_vpp03_*` / `test_vpp04_*` (VPP-01…04). None of them belongs under
TEST-01…05, so "authors new cases only where a gap is named and proven" resolves to **zero new
cases** — the honest outcome, and worth stating explicitly in the record rather than leaving as an
absence.

The gate's docstring carries a correction (**C-04**) that a planner should carry forward: CONTEXT.md
§Reusable Assets nominates "the two fallback cases" for TEST-05, a pair that names no existing case.
The real shape is **two families of three** — the three `zero_pulse_delay` cases plus their three
`nonzero_pulse_delay` negative controls, the latter being the non-vacuity half (a fallback that fired
unconditionally would pass the first three and fail the second three). The landed map freezes the
corrected six-case shape.

### R-03 — `RUN_TEST` parse strategy `[VERIFIED: measured]`

**Source form.** Every `RUN_TEST` in all four v131 suites is written on its own line, inside `main()`
between `UNITY_BEGIN()` and `return UNITY_END()`, in the exact form `RUN_TEST(name);` — no space
between the macro name and `(`, no multi-line continuation, no macro indirection. Verified across
`test_eprom_params_v131.cpp:207-217`, `test_loop_eprom_v131.cpp:1978+`,
`test_trace_eprom_v131.cpp:383-392`.

**Landed regex** (`tests/test_requirement_case_mapping_v131.py:251`):

```python
_RUN_TEST_RE = re.compile(r"RUN_TEST\(\s*([A-Za-z0-9_]+)\s*\)")
```

applied to comment-stripped text (`:275`). Deliberately literal on `RUN_TEST(` — a `RUN_TEST (name)`
form would be missed, but no such form exists in the tree and Unity's own idiom never emits one.

**Conditional-compilation trap.** `test_trace_eprom_v131.cpp:391-393` wraps its sixth
`RUN_TEST(test_dump_v131_traces)` in `#ifdef EPROM_V131_TRACE_DUMP`, which **no env defines**. A
naive source-scan would count 6 cases where a default build registers 5. The landed gate excludes
that suite from `_MAPPED_SUITES` entirely and asserts the exclusion's *reason* stays true
(`test_trace_suite_is_deliberately_out_of_scope` re-checks the `#ifdef` is still present) — so the
exclusion is machine-checked, not folklore. **Any future source-scanning gate over `test/native/avr/`
must handle `#ifdef`-guarded `RUN_TEST` lines**; this is the only instance in the tree today.

### R-04 — How this gate avoids the "app gates scanning firmware source fail OPEN" trap `[VERIFIED: measured]`

The recorded project failure mode is: an app-repo gate keys "firmware absent" on a *scan-target*
proxy, a firmware rename flips the leg PASS → SKIP at exit 0, and nobody notices. Four structural
properties keep this gate out of that class:

1. **It lives inside the firmware repo.** There is no cross-repo presence probe at all, so there is
   no proxy to flip. `_REPO_ROOT` is derived from `Path(__file__).resolve().parent.parent`.
2. **A missing suite file raises, it does not skip.** No `pytest.mark.skipif` anywhere in the module;
   `test_this_module_cannot_be_silently_skipped` asserts the module's own source contains no
   skip-bypass call, no skip decorator and no import-or-skip call, each needle
   **concatenation-built** so the assertion cannot self-match its own prose — and
   `test_own_needles_do_not_appear_verbatim_in_this_module` proves the needles are absent verbatim.
3. **Two non-vacuity floors fail closed.** Per-suite floors `{47, 32, 9}` and a union floor
   `_TOTAL_FLOOR = 88` (`:182-187`). An emptied or misdirected scan root produces 0 names and turns
   the floor leg RED rather than making every membership check pass over an empty set.
4. **The seam cannot silently redirect the self-check.** `FIRESTARTER_CASE_MAP_SCAN_ROOT` overrides
   the scanned root only, binds at import, and Coverage 5's *first* half recomputes the default
   target from `_REPO_ROOT` **without reading `os.environ` at all** — closing the recorded
   `check_permitted_claims.py` landmine where `_HERE` resolved to the wrong phase dir and the scan
   silently covered nothing while exiting 0.

D-18's two plants are already in the module (`test_planted_renamed_case_is_detected` — Plant A, a
renamed case in a scratch tree run through a child process; `test_planted_emptied_scan_root_fails_the_non_vacuity_leg`
— Plant B). Both use `_run_gate_in_subprocess` with `FIRESTARTER_CASE_MAP_SCAN_ROOT` set in the
child env, never `monkeypatch.setenv`, because the value binds at import.

### R-05 — CORRECTION C-01: `eprom_v131_expected.h` IS included today `[VERIFIED: measured]`

```
$ grep -rn "eprom_v131_expected" --include=*.cpp --include=*.h --include=*.py --include=*.json .
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:45:#include "../_shared/eprom_v131_expected.h"
tests/golden/eprom_v131_trace_inventory.json:3:    "source": "test/native/avr/_shared/eprom_v131_expected.h"
tests/test_golden_trace_identity_eprom_v131.py:78,215  (path constant + include-literal assertion)
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:70  (comment reference only)
```

D-05's sentence "No TU `#include`s it, so it never compiles" is true of the file **after** it is
renamed to `_prechange.h`, and false of the file at its current path. Three consequences the planner
must build around:

1. **A bare `git mv` breaks the `native_trace_v131` build.** The rename and the creation of the new
   fixture at the old path must land in the **same commit**.
2. **The new fixture must keep the exact filename `eprom_v131_expected.h`.**
   `test_golden_trace_identity_eprom_v131.py:212-219` (Coverage 5) asserts the consumer TU still
   contains the literal string `_shared/eprom_v131_expected.h`. Renaming the *new* file too would
   turn that leg RED.
3. **D-05's warning-watermark reasoning holds.** `_shared/` appears in **no** `-I` `build_flags`
   entry and **no** `test_filter` in `platformio.ini` — the directory is reached only by relative
   `#include` from a consuming TU. A `_prechange.h` with no includer therefore compiles in no env
   and cannot contribute to the zero-headroom 1166 watermark (D-23). Verified by
   `grep -n "_shared" platformio.ini` → one hit, a comment at `:189`.

**The blob-SHA claim is intact.** `git rev-parse HEAD:test/native/avr/_shared/eprom_v131_expected.h`
→ `ca3e09f164e6e1c541ecb63d15bbebf5bce41d70`, matching `138-BASELINE.md` §4 and the inventory's
`meta.blob_sha`. A `git mv` is content-preserving, so the same SHA resolves at the new path — the
single check D-05's §Specifics names.

### R-06 — The fixture header is far more than three arrays `[VERIFIED: measured]`

`test/native/avr/_shared/eprom_v131_expected.h` is **649 lines**. Structure:

| Lines | Content | Must the NEW fixture reproduce it? |
|-------|---------|------------------------------------|
| 38-42 | Include guard `__EPROM_V131_EXPECTED_H__`, `<stdint.h>`, `<unity.h>`, `"firestarter.h"` | Yes |
| ~44-59 | `extern "C"` declarations of the recorder API (`strobe_count`, `timing_kind`, `timing_after_strobe`, …) | Yes |
| 78-83 | `typedef struct { uint8_t kind; uint8_t pin; uint8_t value; uint32_t us; } v131_trace_entry_t;` | Yes |
| 88-91 | `STROBE_KIND_DATA 1` / `STROBE_KIND_PIN 2` / `TIMING_KIND_DELAY_US 3` / `TIMING_KIND_DELAY_MS 4` | Yes |
| 94 | `v131_merged_length()` | Yes |
| 111 | `v131_merged_at(int k, v131_trace_entry_t* out)` — **the splice rule** | Yes |
| 147 | `v131_first_divergence()` | Yes |
| 173 | `v131_assert_stream_equals()` — what the consumer's failing assertion calls | Yes |
| 204 | `v131_snapshot()` | Yes |
| 274-366 | `EPROM_V131_TRACE_PROTO_07[]` (198 entries) + `_LEN` macro | **Replaced** — 91 entries |
| 411-508 | `EPROM_V131_TRACE_PROTO_08[]` (221 entries) + `_LEN` macro | **Replaced** — 115 entries |
| 555-647 | `EPROM_V131_TRACE_PROTO_0B[]` (201 entries) + `_LEN` macro | **Replaced** — 59 entries |

**The new fixture is not "three arrays in a file" — it is the whole header with three arrays
swapped.** Dropping the helpers would break `test_trace_eprom_v131.cpp`'s link. The cheapest correct
authoring path is: copy the header, replace the three array bodies and their provenance comments,
leave everything else byte-identical.

**Splice rule** (`:111`, verbatim from the source comment): every timing whose
`timing_after_strobe()` equals `i` is emitted immediately **before** strobe `i` (in push order among
ties); timings whose key equals `strobe_count()` are emitted after the last strobe. A two-pointer
merge of two already-sorted sequences.

`_parse_arrays` in the identity gate (`test_golden_trace_identity_eprom_v131.py:84-88`) requires the
declaration form literally `static const v131_trace_entry_t <NAME>[] = {` … `};` and counts
`\{[^{}]*\}` occurrences **after** stripping `/* */` and `//` comments. The dump's one-entry-per-line
output satisfies this; hand-added segment banners are stripped before counting and cannot inflate a
count.

### R-07 — D-06's prediction CONFIRMED by live capture `[VERIFIED: measured this session]`

Commands, verbatim (from `141-NEW-TRACE.md` §1, re-executed 2026-08-14; cwd must be
`/workspaces/firestarter` — the gitignored root `platformio.ini` carries two `[platformio]` sections
and `pio -d <dir>` does not work around it):

```bash
cd /workspaces/firestarter && \
  PLATFORMIO_BUILD_FLAGS="-D EPROM_V131_TRACE_DUMP" pio test -e native_trace_v131 --without-testing
cd /workspaces/firestarter && .pio/build/native_trace_v131/firestarter_native
```

Output banners, verbatim:

```
##### EPROM_V131_TRACE_PROTO_07 total=91 strobe_overflow=0 timing_overflow=0
##### EPROM_V131_TRACE_PROTO_08 total=115 strobe_overflow=0 timing_overflow=0
##### EPROM_V131_TRACE_PROTO_0B total=59 strobe_overflow=0 timing_overflow=0
```

**91 / 115 / 59 — exactly D-06's prediction.** No deviation; no stop-and-report condition. The
0x08 figure is 115, confirming Phase 142's 119 → 115 movement (F-142-04) and confirming Phase 143
added zero frames.

**Arithmetic for D-07:**

| | 0x07 | 0x08 | 0x0B | Total |
|---|---|---|---|---|
| Pre-change (`arrays[].entries`) | 198 | 221 | 201 | **620** |
| New (measured) | 91 | 115 | 59 | **265** |
| | | | | **885** ✓ |

Independently re-derived the pre-change side by parsing the live header (198/221/201), and counted
`265` entry lines in the dump. D-07's `885` denominator is confirmed by two independent counts.

**Per-kind split of the new capture** (computed from the dump; feeds `meta.measured_entry_counts`):

| Protocol | DATA (kind 1) | PIN (kind 2) | strobes | `delay_us` (3) | `delay_ms` (4) | timings | merged |
|----------|---------------|--------------|---------|----------------|----------------|---------|--------|
| 0x07 | 11 | 55 | **66** | 24 | 1 | **25** | **91** |
| 0x08 | 17 | 67 | **84** | 30 | 1 | **31** | **115** |
| 0x0B | 7 | 35 | **42** | 16 | 1 | **17** | **59** |

Pre-change, for the same field (`meta.measured_entry_counts` as committed): 0x07 142/56/198,
0x08 157/64/221, 0x0B 142/59/201.

### R-08 — The dump gives entries, not segments `[VERIFIED: measured]`

`dump_v131_merged_ready_to_paste` (`test_trace_eprom_v131.cpp:350-361`, permanently behind
`#ifdef EPROM_V131_TRACE_DUMP`) prints:

```
    {%d, 0x%02X, 0x%02X, %luUL}, /* %d */
```

— kind, pin, value, microseconds, and **an index comment only**. It emits no segment banners.

The *pre-change* fixture, by contrast, carries hand-authored segment comments that already name a
usable taxonomy (`:274-366`, verbatim samples):

```
/* one-time VPP-regulator enable (ctrl -> 0x81) + ms=500 */
/* pass 1: VPE/route assert (ctrl -> 0x85) + ms=10 */
/* pass 1: program byte@lsb=0x00 payload=0x3C pulse=100us */
/* pass 1: VPE/route release (ctrl -> 0x91) */
/* pass 1: verify byte@lsb=0x00 */
```

So D-07's per-segment partition is **authorship on top of a raw dump for the new side**, and **a read
of existing comments for the old side**. The pre-change cadence is a three-pass whole-block rewrite
(`pass 1/2/3` × {route assert, N × program byte, route release, N × verify byte}); the new cadence is
per-byte pulse→verify. That structural difference *is* the diff TEST-06 must attribute.

The entry vocabulary that makes segmentation mechanical (read off the new 0x07 stream):

- `{1, 0x00, V, 0}` — a control-register byte write (`V` = `0x81` regulator on, `0x85` route
  asserted, `0x91` released, `0x95` route + data-latch, and payload/address bytes elsewhere)
- `{2, 0x08, 1/0, 0}` — control-register latch strobe pair
- `{2, 0x01, 1/0, 0}` — LSB address latch strobe pair
- `{2, 0x04, 1/0, 0}` — chip-enable / write-enable line
- `{2, 0x20, 0/1, 0}` — the program-pulse pin, bracketing a `{3, .., .., <pulse_us>}` timing
- `{3, …, N}` / `{4, …, N}` — `delayMicroseconds(N)` / `delay(N)`

A segment boundary is therefore identifiable from `(kind, pin, value)` triples without any positional
guessing. Six segments (init, route assert, address set, pulse, verify read, teardown) map onto this
vocabulary cleanly; the exact names and boundaries are Claude's discretion per CONTEXT.md.

### R-09 — The standing RED's exact shape, and the "5 vs 6 cases" subtlety `[VERIFIED: measured]`

`pio test -e native_trace_v131` at a clean build directory, no dump flag, verbatim:

```
test_trace_eprom_v131.cpp:383: test_smoke_setup_leaves_both_recorders_clean	[PASSED]
test_trace_eprom_v131.cpp:384: test_smoke_timing_hook_fires_for_delay_and_delaymicroseconds	[PASSED]
test_trace_eprom_v131.cpp:176: test_protocol_0x07_am27c512_capture_is_sound_and_deterministic: Expected 198 Was 91. 0x07 AM27C512 DIP28_27512	[FAILED]
test_trace_eprom_v131.cpp:176: test_protocol_0x08_am27c020_capture_is_sound_and_deterministic: Expected 221 Was 115. 0x08 AM27C020 DIP32_27C020	[FAILED]
test_trace_eprom_v131.cpp:176: test_protocol_0x0B_am2716_capture_is_sound_and_deterministic: Expected 201 Was 59. 0x0B AM2716 DIP24_2716	[FAILED]
 native_trace_v131:native/avr/test_trace_eprom_v131 [ERRORED] Took 1.25 seconds
============= 6 test cases: 3 failed, 2 succeeded in 00:00:01.248 =============
```

**The `6` is PlatformIO's arithmetic, not a sixth registered case:** 2 passed + 3 failed + 1 ERRORED
suite entry. The non-dump binary registers **5** cases. `size_baseline_v131.json` records
`native_trace_v131: {cases: 5, succeeded: 5, all_passed: true}` — that is the *green-state* figure
from Phase 138, and it is the figure the env should return to after TEST-06 re-freezes the fixture.
D-13's refresh should expect `5 / 5 / 1 suite / all_passed: true`, not 6.

### R-10 — Build-cache contamination trap `[VERIFIED: measured this session]`

`PLATFORMIO_BUILD_FLAGS="-D EPROM_V131_TRACE_DUMP"` bakes the flag into
`.pio/build/native_trace_v131`. A subsequent bare `pio test -e native_trace_v131` in the same tree is
not guaranteed to reflect the un-flagged build. The dump invocation also uses `--without-testing`, so
its own summary line reads `0 test cases: 0 succeeded` — **that line is not evidence of anything**
and must not be recorded as a run result.

**Required sequence** for any recorded measurement after a dump:

```bash
rm -rf .pio/build/native_trace_v131
pio test -e native_trace_v131
```

Confirmed working this session. This matters doubly for D-23: a warning count read from a
dump-flagged or warm build directory is not the COLD figure the watermark policy is anchored to.

### R-11 — D-08's six assertions and the exact fields to update `[VERIFIED: measured]`

`firestarter/tests/test_golden_trace_identity_eprom_v131.py` — six assertions, one function each:

| # | Function | Line | What it asserts | Reads which JSON field |
|---|----------|------|-----------------|------------------------|
| 1 | `test_blob_sha_matches_the_recorded_inventory` | 155 | `git rev-parse HEAD:test/native/avr/_shared/eprom_v131_expected.h` == recorded | `meta.blob_sha` |
| 2 | `test_array_names_match_the_recorded_inventory` | 168 | ordered array-name list from a live re-parse == recorded | `arrays[].name` |
| 3 | `test_array_entry_counts_match_the_recorded_inventory` | 177 | per-array counts match **positionally**; message names the FIRST divergence | `arrays[].entries` |
| 4 | `test_inventory_is_non_vacuous` | 198 | `len(arrays) >= 3` and every `entries >= 1` | `arrays` |
| 5 | `test_consuming_suites_still_include_the_fixture` | 212 | `test_trace_eprom_v131.cpp` still contains the literal `_shared/eprom_v131_expected.h` | — (source scan) |
| 6 | `test_git_is_required_not_optional` | 222 | this module's own source contains no `pytest.skip` / `@pytest.mark.skipif` line | — (self-scan) |

**Fields D-08 must change** (`tests/golden/eprom_v131_trace_inventory.json`):

| Field | Gate-asserted? | Current | New |
|-------|----------------|---------|-----|
| `meta.blob_sha` | **Yes (#1)** | `ca3e09f164e6e1c541ecb63d15bbebf5bce41d70` | blob of the new fixture |
| `arrays[0].entries` | **Yes (#3)** | 198 | **91** |
| `arrays[1].entries` | **Yes (#3)** | 221 | **115** |
| `arrays[2].entries` | **Yes (#3)** | 201 | **59** |
| `arrays[*].name` | **Yes (#2)** | `EPROM_V131_TRACE_PROTO_07/_08/_0B` | **unchanged, same order** |
| `meta.source` | No | `test/native/avr/_shared/eprom_v131_expected.h` | **unchanged** |
| `meta.recorded_at_head` | No | `3dad6450e…` | new head |
| `meta.recorded_by` / `meta.requirement` | No | `Phase 138 Plan 05` / `PREP-03` | `Phase 144 Plan NN` / `TEST-06` |
| `meta.measured_entry_counts` | No | 142/56/198, 157/64/221, 142/59/201 | 66/25/91, 84/31/115, 42/17/59 (see R-07) |
| `meta.overflow_observed` | No | prose | re-state from this capture (all four overflow flags 0) |
| `meta.frozen_for` | No | "Phase 144 / TEST-06 …" | re-point at v1.32 |

`meta.how_to_update` is **binding**: re-derive by independent parse, never hand-edit a count, and
state in the commit message which array changed and why.

**One-commit sequencing insight.** Assertion #1 reads `HEAD:`, so the JSON cannot be authored from
`HEAD` before the fixture is committed. Rather than split into two commits, derive the blob directly:

```bash
git hash-object test/native/avr/_shared/eprom_v131_expected.h
```

`git hash-object` produces the identical content-addressed SHA that `git rev-parse HEAD:<path>` will
report once committed, so the rename, the new fixture and the inventory rewrite can land atomically.

**D-08's named non-claim is real and verified:** nothing in the repo references
`eprom_v131_expected_prechange.h` (the name does not exist yet, and no gate file lists it). After the
rename, `ca3e09f1…` stays verifiable by hand via
`git rev-parse HEAD:test/native/avr/_shared/eprom_v131_expected_prechange.h` but is asserted by no
gate. Record it as a gap.

### R-12 — CAP-03 byte layout, both sides, with line numbers `[VERIFIED: measured]`

**Firmware pack site** — `firestarter/src/firestarter.cpp:185-204`, inside `init_programmer_framed`,
a single `LOG_OK_ID_BYTES(MSG_OK_READY, ...)` emit:

```c
const char* _ver = FW_VERSION;
uint8_t _vlen = (uint8_t)strlen(_ver);
if (_vlen > 32) _vlen = 32;                             // :193  ver_len clamped to 32
uint8_t _ready[4 + 32 + 2];                             // :194  buffer sized for the max tail + budget
_ready[0] = (uint8_t)(((uint16_t)DATA_BUFFER_SIZE >> 8) & 0xFF);  // :195
_ready[1] = (uint8_t)((uint16_t)DATA_BUFFER_SIZE & 0xFF);         // :196
#ifdef HARDWARE_REVISION
_ready[2] = (uint8_t)rurp_get_hardware_revision();      // :198
#else
_ready[2] = 0xFE;  // REVISION_UNKNOWN                  // :200
#endif
_ready[3] = _vlen;                                      // :202
memcpy(_ready + 4, _ver, _vlen);                        // :203
uint16_t _budget = eprom_block_budget_s(handle->protocol, handle->pulse_delay,
                                        (uint32_t)DATA_BUFFER_SIZE);   // :204-205
_ready[4 + _vlen]     = (uint8_t)((_budget >> 8) & 0xFF);   // :206  COMPUTED offset
_ready[4 + _vlen + 1] = (uint8_t)(_budget & 0xFF);          // :207  COMPUTED offset
LOG_OK_ID_BYTES(MSG_OK_READY, _ready, (uint8_t)(4 + _vlen + 2));  // :208  length includes the budget
```

**Host decode site** — `firestarter_app/firestarter/serial_comm.py:344-442`, `_decode_id_frame`:

```python
params_bytes = body[1:-1]                    # :388  strip the id byte and the trailing CRC
if len(params_bytes) >= 2:                   # :394
    value = struct.unpack(">H", params_bytes[:2])[0]      # :395   CAP-01
    if 1 <= value <= 4096: self.firmware_max_chunk = value # :400-401
if len(params_bytes) >= 4:                   # :408
    self.hw_revision = params_bytes[2]       # :409   CAP-02
    ver_end = 4 + params_bytes[3]            # :410   COMPUTED
    if ver_end <= len(params_bytes):         # :411
        self.firmware_identity = params_bytes[4:ver_end].decode("ascii", errors="replace")  # :412
        if len(params_bytes) >= ver_end + 2: # :430   CAP-03
            value = struct.unpack(">H", params_bytes[ver_end : ver_end + 2])[0]  # :431-433
            if 1 <= value <= WRITE_BUDGET_MAX_S: self.write_block_budget_s = value  # :440-441
```

`WRITE_BUDGET_MAX_S = 14400` at `serial_comm.py:77`.

**The parity table D-17's gate must assert:**

| Field | Firmware index | Host index into `params_bytes` | Width | Endianness |
|-------|----------------|-------------------------------|-------|------------|
| CAP-01 buffer size | `_ready[0..1]` | `[:2]` | u16 | BE (`>>8` first / `">H"`) |
| CAP-02 hw revision | `_ready[2]` | `[2]` | u8 | — |
| CAP-02 ver_len | `_ready[3]` | `[3]` | u8 | — |
| CAP-02 ver bytes | `_ready[4 .. 4+_vlen-1]` | `[4:ver_end]` | `ver_len` | ascii |
| **CAP-03 budget** | `_ready[4+_vlen]`, `[4+_vlen+1]` | `[ver_end : ver_end+2]`, `ver_end = 4 + params_bytes[3]` | u16 | BE |
| Total length | `4 + _vlen + 2` | implied by `len(params_bytes) >= ver_end + 2` | — | — |

Two facts a gate should carry as named non-claims rather than assert:

- **Frame framing differs by one byte on each end.** The firmware packs a bare params blob; the host
  reads `body[1:-1]`, stripping an id byte and a CRC that `LOG_OK_ID_BYTES` adds at the transport
  layer. A gate that compares "firmware index N" to "host index N" must compare against
  `params_bytes` indices, not `body` indices.
- **`ver_len` is clamped to 32 firmware-side (`:193`) but is unbounded host-side** beyond the
  `ver_end <= len(params_bytes)` guard. That is a benign asymmetry — the host degrades to
  `firmware_identity = None`, never a partial value — but it is an asymmetry, and asserting a
  symmetric clamp would fail.

### R-13 — What D-17's gate is actually closing `[VERIFIED: measured]`

Two half-gates exist; **no live cross-repo comparison exists**.

| Existing | Repo | What it proves | What it does not |
|----------|------|----------------|-------------------|
| `firestarter/tests/test_ack_layout_source_contract_v143.py` | firmware | 7 legs pinning the pack layout in `src/firestarter.cpp`: the retired 2-byte emit is gone, exactly one blob emit exists, the buffer has room for the budget, the budget is written at a **computed** offset with no bare index > 3, the emitted length accounts for the budget, the budget comes from the shipped function, the revision byte is emitted on both `#ifdef` arms | Reads nothing from the host repo. Its own docstring hands "the standing gate" to Phase 144 / TEST-07. |
| `firestarter_app/tests/test_hw_revision_gate.py::_cap03_params` (`:175-188`) | host | `_decode_id_frame` decodes a **hand-written** fixture reproducing the documented layout, at two identity lengths (proving `ver_end` is computed) | The fixture *restates* the firmware layout; it never reads firmware source. Its own docstring: "nothing else in either repo compares the two sides (RESEARCH Open Question 4 hands the standing gate to Phase 144 / TEST-07)." |

So D-17's gate is precisely: **read `firestarter/src/firestarter.cpp` from the host repo via
`fw_path`, extract the pack indices, and assert they agree with the host decoder's offsets** —
including that the budget index is `4 + <the ver_len variable>` and not a literal.

**`src/firestarter.cpp` is NOT in the cross-repo scan-path inventory.**
`firestarter_app/tests/scan_paths.py`'s `CROSS_REPO_TEST_PATHS` currently holds 6 entries:

```
include/firestarter.h                                       (test_revision_constants_parity, test_check_is_memory_cmd_no_ifdef)
src/proms/eeprom_28c.cpp                                    (test_check_no_log_in_sdp_window, test_sdp_table_parity)
doc/PROTOCOLS.md                                            (test_dispatch_mirror)
test/native/avr/test_dispatch/test_configure_memory.cpp     (test_dispatch_mirror)
test/native/avr/_shared/sdp_bus_config.h                    (test_sdp_bus_config_drift)
test/native/avr/_shared/validation_matrix.h                 (test_gen_validation_header)
```

Enforcement in `test_scan_paths_resolve.py` is a `>=` **floor**, not an exhaustive coverage check —
`test_py32_flash_map_host.py` and `test_py32_asset_name_host.py` already resolve firmware paths
without inventory entries. So adding `src/firestarter.cpp` is **house convention, recommended, not
mechanically required**. Stated honestly rather than as a hard obligation.

### R-14 — The planted-fixture pattern D-18 requires `[VERIFIED: measured]`

Committed fixtures live in `firestarter_app/tests/fixtures/`:
`planted_constants_value_drift.h`, `planted_constants_host_missing.h`, `planted_constants_fw_missing.h`.
The working pattern (`test_revision_constants_parity.py:733-790`):

```python
_FIXTURES_DIR    = Path(__file__).parent / "fixtures"
_FIXTURE_DRIFT   = _FIXTURES_DIR / "planted_constants_value_drift.h"

def test_planted_value_drift_is_detected(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _FIXTURE_DRIFT.is_file(), f"committed fixture missing: {_FIXTURE_DRIFT}"
    monkeypatch.setattr(sys.modules[__name__], "FIRMWARE_HEADER", _FIXTURE_DRIFT)  # module-level path const
    with pytest.raises(AssertionError) as excinfo:
        _check_cmd_two_way()                     # the SAME helper the real leg calls
    message = str(excinfo.value)
    assert "CMD_VERIFY = 106" in message         # names the drift
    assert "COMMAND_VERIFY = 6" in message
    assert "has no host constant" not in message # LEG ISOLATION: only this check fired
```

Four properties to reproduce for D-17:

1. The path constant is **module-level** (`FIRMWARE_HEADER = fw_path("include", "firestarter.h")` at
   `:148`) and resolved via `fw_path`, so a present-repo rename is a named `MissingScanTargetError`,
   never a silent skip.
2. The planted leg calls the **same private helper** the real leg calls, never a reimplementation.
3. Every planted leg asserts **leg isolation** — the message must contain the expected report *and
   must not* contain the neighbouring report.
4. Fixture-driven planted legs deliberately carry **no** `@requires_fw`: the fixture is always
   present in the app repo, so a host-only CI run still exercises the checker's failure modes even
   though it cannot exercise them against the real header (`:722-728`).

`monkeypatch.setattr` works here because `FIRMWARE_HEADER` is a module **attribute**, not an
import-time environment read — this is the opposite case from `fw_presence.FW_ROOT` (see R-15).

### R-15 — D-16's absent-path subprocess run, verified working `[VERIFIED: measured this session]`

**Env var name, read from source, not assumed:** `fw_presence.py:80` —

```python
FW_ROOT: Path = Path(os.environ.get("FIRESTARTER_FW_ROOT", str(_DEFAULT_FW_ROOT)))
```

`FW_REPO_MARKER = FW_ROOT / ".git"` (`:86`), `FW_REPO_PRESENT = FW_REPO_MARKER.exists()` (`:88`),
`requires_fw = pytest.mark.skipif(not FW_REPO_PRESENT, reason=FW_ABSENT_REASON)` (`:102`),
`fw_path()` (`:117`). All bind at import; `skipif` binds at collection. `monkeypatch.setenv` cannot
reach any of them.

**Working command shape** (executed this session):

```bash
mkdir -p /tmp/empty_fw
cd /workspaces/firestarter_app && FIRESTARTER_FW_ROOT=/tmp/empty_fw \
  .venv/ci-replica/bin/python -m pytest tests/test_revision_constants_parity.py -o addopts="" -q -rs
```

Result, verbatim:

```
6 passed, 8 skipped in 0.10s
SKIPPED [1] tests/test_revision_constants_parity.py:563: firestarter firmware checkout absent (no /tmp/empty_fw/.git marker)
   (… 7 more, same canonical reason, at :575 :585 :598 :617 :658 :686 :786)
```

The **present**-path run for the same module: `14 passed in 0.05s`.

Both directions therefore hold: 14 pass with the sibling repo present; 8 skip cleanly and 6 still
pass with it absent. `-rs` is what makes the skip reasons appear in the transcript D-16 wants
recorded — without it the record shows only a count.

Two notes for the record:

- The empty directory must contain **no `.git`**. A `/tmp` scratch dir is fine; do not point the seam
  at a real repo.
- For the full sweep, the same env-var-in-a-child-process shape applies to the **whole** host suite,
  not just this one module — that is the run that surfaces devcontainer-masked CI defects (the
  recorded sibling-layout finding). Twelve app modules import `fw_path`
  (`test_check_no_log_in_sdp_window`, `test_fw_presence`, `test_sdp_table_parity`, `scan_paths`,
  `test_check_is_memory_cmd_no_ifdef`, `test_gen_validation_header`, `test_revision_constants_parity`,
  `test_py32_flash_map_host`, `test_dispatch_mirror`, `test_sdp_bus_config_drift`,
  `test_py32_asset_name_host`, plus `fw_presence` itself).

### R-16 — Size baselines: schema, invocations, current verdicts `[VERIFIED: measured this session]`

**Line numbers in `firestarter/scripts/check_size_baseline.py`, all confirmed:**
`FIRESTARTER_SIZE_BASELINE` seam `:95`, `AVR_ENVS` `:99`, `NATIVE_ENVS` `:100`,
`MERGE05_UNO_CLASS_FLASH_BAND = 64` `:107`, `compare_avr` `:183`,
`compare_avr_policy_merge05` `:214`, `compare_native` `:269`.

**Schema each rewrite must produce.** The comparators read exactly these keys:

```jsonc
{
  "meta": { /* free-form provenance; read by nothing */ },
  "avr_targets": {
    "<uno|uno328pb|leonardo>": {
      "flash_used": <int>,   // compare_avr (==) / compare_avr_policy_merge05 (band)
      "flash_total": <int>,  // both: must be unchanged
      "flash_free": <int>,   // recorded, not read
      "ram_used": <int>,     // both: must be exactly unchanged
      "ram_total": <int>,    // both: must be unchanged
      "ram_free": <int>      // recorded, not read
    }
  },
  "native_envs": {
    "<env>": { "cases": <int>, "succeeded": <int>, "suites": <int>, "all_passed": <bool> }
  },
  "envs_agree": <bool>,
  "warnings": {
    "avr":  { "<env>": { "macro_redefinition": <int>, "total": <int> } },
    "native": { "<env>": { "macro_redefinition": <int>, "total_watermark": <int> } },
    "policy": { "avr_rule": "== 0", "native_rule": "<= total_watermark" }
  }
}
```

`check_build_warnings.py` reads the `warnings` block via the same `FIRESTARTER_SIZE_BASELINE` seam
(`:82`) and its own `AVR_ENVS`/`NATIVE_ENVS` at `:86-87`.

**Which invocation produces the measurement.** Two routes:

```bash
# Route A — capture logs, then compare (what every prior phase recorded)
pio run -t clean -e uno && pio run -e uno > /tmp/uno.log 2>&1        # repeat for uno328pb, leonardo
rm -rf .pio/build/native && pio test -e native > /tmp/native.log 2>&1  # repeat for native_nodevtools
python3 scripts/check_size_baseline.py \
  --avr-log uno=/tmp/uno.log --avr-log uno328pb=/tmp/uno328pb.log --avr-log leonardo=/tmp/leonardo.log \
  --native-log native=/tmp/native.log --native-log native_nodevtools=/tmp/nnd.log

# Route B — let the script rebuild (guarantees a clean build; no reusable artifact)
python3 scripts/check_size_baseline.py --rebuild
```

`--rebuild` iterates `AVR_ENVS` then `NATIVE_ENVS` (`:420-424`), i.e. the same five envs.
`--baseline PATH` overrides the seam. Argv is parsed by a hand-rolled parser (`_parse_argv`, `:330`);
an unrecognised `--policy` value is exit **2**, a tool failure, not a regression.

**`--policy` flags that exist:** exactly one value, `merge05` (`:368-380`). Absence of `--policy`
selects strict byte-identity.

**Current verdicts at this tip, verbatim:**

```
$ python3 scripts/check_size_baseline.py --avr-log uno=… --avr-log uno328pb=… --avr-log leonardo=…
FAIL:
  uno: flash_used baseline=23954 observed=24824
  uno328pb: flash_used baseline=24004 observed=24874
  leonardo: flash_used baseline=26016 observed=26906
exit=1

$ python3 scripts/check_size_baseline.py --policy merge05 \
    --baseline scripts/baseline/size_baseline_base01.json --avr-log …
FAIL:
  uno: flash_used baseline=23932 observed=24824 delta=+892 exceeds MERGE-05 uno-class band of 64 B
  uno328pb: flash_used baseline=23976 observed=24874 delta=+898 exceeds MERGE-05 uno-class band of 64 B
  leonardo: flash_used baseline=26072 observed=26906 delta=+834 exceeds MERGE-05 leonardo band of 0 B
exit=1
```

**D-11's claim CONFIRMED: re-anchoring needs no edit to `check_size_baseline.py`.**
`compare_avr_policy_merge05` (`:214-266`) reads `baseline["avr_targets"][env]` for every figure and
takes the band from the module constant `MERGE05_UNO_CLASS_FLASH_BAND` (`:107`) / a hardcoded `0` for
`leonardo` (`:249`). Nothing about the anchor is in the script. Re-anchoring is a pure JSON rewrite.
After D-10 + D-11 both gates read green, and the merge05 line will print
`uno(flash=24824/32256[+0<=64],ram=1573/2048[=])` — a green whose *reason* is D-14's mandatory
disclosure.

**AVR warnings gate is already green at this tip:**

```
$ python3 scripts/check_build_warnings.py --log uno=… --log uno328pb=… --log leonardo=…
PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0), leonardo: macro_redefinition=0 (== 0)
exit=0
```

### R-17 — CLI asymmetry between the two checkers `[VERIFIED: measured this session]`

The two scripts take **different log flags**. This is an easy executor trap:

| Script | Log flag(s) | Verified failure on the wrong flag |
|--------|-------------|-------------------------------------|
| `check_size_baseline.py` | `--avr-log ENV=PATH`, `--native-log ENV=PATH` | — |
| `check_build_warnings.py` | `--log ENV=PATH` (one flag for both kinds) | `ERROR: unrecognized argument: --avr-log` → exit **2** |

Both accept `--baseline PATH` and `--rebuild`.

### R-18 — D-22 / F-138-05 reproduced live `[VERIFIED: measured this session]`

```
$ pio test -e native_loop_v131 > /tmp/loopfull.log 2>&1
$ python3 scripts/check_size_baseline.py --native-log native_loop_v131=/tmp/loopfull.log
Traceback (most recent call last):
  File "scripts/check_size_baseline.py", line 457, in main
    failures = compare_native(env, parsed, baseline)
  File "scripts/check_size_baseline.py", line 278, in compare_native
    rec = baseline["native_envs"][env]
KeyError: 'native_loop_v131'
exit=1
```

Uncaught `KeyError`, exit 1 — a **false regression signal**, not the documented exit-2 tool failure.
Exactly as D-22 states. The mechanism survives even though `size_baseline.json` *does* contain a
`native_envs` block, because that block has no `native_loop_v131` key.

### R-19 — `size_baseline_v131.json` is missing TWO env records, not merely stale `[VERIFIED: measured]`

Current `native_envs` keys in `scripts/baseline/size_baseline_v131.json`:
`native`, `native_nodevtools`, `native_pinmap_provisional`, `native_trace_v131`.
**Absent: `native_params_v131`, `native_loop_v131`.**

So D-13's "refresh" is an **add-two-and-update-one** operation, not a numeric touch-up. Measured
values for the refresh, from this session's runs:

| Env | cases | succeeded | suites | all_passed | Note |
|-----|-------|-----------|--------|------------|------|
| `native` | 141 | 141 | 17 | true | unchanged |
| `native_nodevtools` | 141 | 141 | 17 | true | unchanged |
| `native_pinmap_provisional` | 10 | 10 | 1 | true | not re-run this session; unchanged since Phase 138 |
| `native_trace_v131` | 5 | 5 | 1 | true | **currently RED**; returns to this after TEST-06 re-freezes |
| `native_params_v131` | **9** | **9** | **1** | true | **NEW record** |
| `native_loop_v131` | **79** | **79** | **2** | true | **NEW record** |

The corresponding `warnings.native` block needs the same two new env keys with COLD
`macro_redefinition` / `total_watermark` figures — which must come from
`rm -rf .pio/build/<env>` + a single `pio test -e <env>` invocation, never a warm re-run
(the file's own `meta.warm_vs_cold_correction` is explicit that a warm figure is not a valid
watermark).

D-13's "cannot turn anything RED" is confirmed structurally: no live gate reads this file — it is
never the `FIRESTARTER_SIZE_BASELINE` default (that is `size_baseline.json`, `:95`) and D-22 forbids
passing a `*_v131` env name to either checker even with `--baseline` pointed here.

### R-20 — AVR tip measured; D-09 confirmed exactly `[VERIFIED: measured this session]`

```
=== uno ===       RAM: 76.8% (used 1573 from 2048)   Flash: 77.0% (used 24824 from 32256)
=== uno328pb ===  RAM: 77.1% (used 1579 from 2048)   Flash: 76.8% (used 24874 from 32384)
=== leonardo ===  RAM: 78.7% (used 2014 from 2560)   Flash: 93.8% (used 26906 from 28672)
```

| Env | flash baseline (`size_baseline.json`) | flash observed | Δ | RAM baseline | RAM observed | Δ | headroom |
|-----|---------------------------------------|----------------|---|--------------|--------------|---|----------|
| uno | 23954 | 24824 | **+870** | 1573 | 1573 | 0 | 7432 B (23.0%) |
| uno328pb | 24004 | 24874 | **+870** | 1579 | 1579 | 0 | 7510 B (23.2%) |
| leonardo | 26016 | 26906 | **+890** | 2014 | 2014 | 0 | **1766 B (6.2%)** |

D-09's figures are exact. **Caveat on my measurement:** these were **warm** `pio run` invocations
(the build dirs already existed). Flash/RAM figures are deterministic from source so warm/cold does
not affect them — but the *recorded* measurement for the phase record must follow the baselines' own
documented procedure (`pio run -t clean -e <env>` then one uninterrupted `pio run -e <env>` at a
540000 ms timeout), because the same logs are the warning-count source and warnings **are**
warm/cold-sensitive. A default 2-minute Bash timeout truncates the toolchain build mid-compile and
the partial log still parses — the live trap `size_baseline.json`'s own `meta.note` records.

### R-21 — Host-side green state on the CI-parity interpreter `[VERIFIED: measured this session]`

Interpreter: `/workspaces/firestarter_app/.venv/ci-replica/bin/python` → **Python 3.11.15**
(pytest 9.1.1, ruff 0.16.1, mypy 2.3.0).

```bash
cd /workspaces/firestarter_app
.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q \
    --cov=firestarter --cov-report=term-missing --cov-fail-under=70
```

```
TOTAL                               5035    860    83%
Required test coverage of 70% reached. Total coverage: 82.92%
30 snapshots passed.
1578 passed, 1 warning in 233.52s (0:03:53)
```

**1578 passed at 82.92% — byte-for-byte D-21's recorded Phase 143 state.**

CI-scoped gates, from `.github/workflows/ci.yml:80-87`, all run this session:

| CI step | Exact command | Result |
|---------|---------------|--------|
| ruff lint | `ruff check firestarter/ tests/` | `All checks passed!` |
| ruff format check | `ruff format --check firestarter/ tests/` | `134 files already formatted` |
| mypy watermark | `python tools/check_mypy_watermark.py` | `checked 136 source files` / `mypy errors: 33 (watermark: 35)` → **INFO, 2 below** |
| pytest + coverage | `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` | as above |

Two honesty notes:

- The mypy gate's own message says the watermark "may be lowered to 33". **Do not lower it in this
  phase** — the gate's own rule is "lower it in the same commit as the fixes that reduced the count,
  never to make a failing gate pass," and this phase lands no type fixes. Lowering it here would be a
  cosmetic tightening dressed as progress.
- The watermark gate is **fail-open under the ambient 3.12** (a recorded project finding). Running it
  on `.venv/ci-replica` is what makes the `33 / 35` figure meaningful; a 3.12 run is not evidence.

**Also measured: the app repo's own working tree is currently dirty** (untracked `.coverage`,
`.planning/config.json`, `SECURITY.md`, `datasheets/*.pdf`, `write_test_port.sh`) and the full suite
still passed. So **no gate asserts the app repo's own porcelain** — only the firmware repo's. That is
an empirical result, not an inference from reading the sources.

### R-22 — ADDITION A-01: D-20 has THREE porcelain couplings, not two `[VERIFIED: measured]`

| # | Module | Line | Asserts | Repo whose porcelain |
|---|--------|------|---------|----------------------|
| 1 | `firestarter/tests/test_flash_path_record_sync.py` | 1247 | `_git_porcelain(_FW_REPO_ROOT) == ""` | the firmware repo (its own) |
| 2 | `firestarter_app/tests/test_py32_flash_map_host.py` | 391 | `_git_porcelain(FW_ROOT) == ""` | the **sibling** firmware repo |
| 3 | **`firestarter_app/tests/test_py32_asset_name_host.py`** | **323** | `_git_porcelain(FW_ROOT) == ""` | the **sibling** firmware repo |

CONTEXT.md's D-20 names #1 and #2. **#3 is the same coupling with the same failure message shape**
("the firmware repo's working tree is no longer clean after the planted-copy test -- it is a
read-only input to this phase") and is not mentioned anywhere in CONTEXT.md. A plan that sequences
around only `test_py32_flash_map_host.py` will still hit #3.

Additionally, `firestarter/tests/test_flash_path_record_sync.py` reaches into the **meta repo** via
`tests/meta_presence.py` and the `FIRESTARTER_META_ROOT` seam (`:134`, `:626-647`, `:733-743`), to
compare `.planning/v1.23-FLASH-PATH-DECISION.md`'s `[SHARED:S1..S5]` sections against
`platform/py32f071/FLASH-PATH-AND-PCB.md`. It does **not** assert meta-repo porcelain — I grepped;
the only `_git_porcelain` calls are against `_FW_REPO_ROOT`. So writing new `.planning/phases/144-*`
files is safe. Editing `.planning/v1.23-FLASH-PATH-DECISION.md` would not be; nothing in this phase
requires that.

### R-23 — ADDITION A-02: precise CI reach `[VERIFIED: measured]`

```
firestarter/.github/workflows/build.yml:142   pio test -e native
firestarter/.github/workflows/build.yml:155   pio test -e native_nodevtools
firestarter/.github/workflows/build.yml:158   pip install pytest
firestarter/.github/workflows/build.yml:161   pytest tests/ -v
firestarter/.github/workflows/build.yml:193   pio run                      # = default_envs: uno, uno328pb, leonardo
firestarter/.github/workflows/beta-build.yml:122/128/131/134/145  — identical set
```

Two distinct statements, both true, and they must not be collapsed:

- **`pio test -e native_trace_v131` / `-e native_params_v131` / `-e native_loop_v131` run in NO CI
  leg.** D-15's hole is real and must be restated in the phase record.
- **`pytest tests/ -v` DOES run in CI** on `main` and `beta`. So D-01's mapping gate, D-07's
  exhaustiveness gate, the trace-identity gate and every other `firestarter/tests/` module *will* be
  CI-covered once this branch merges. It does **not** run in any CI leg on the milestone branch
  itself.

Saying "none of this phase's gates are CI-covered" would be an *under*claim. Saying "CI covers the
v131 envs" would be an overclaim. The honest sentence names both halves.

### R-24 — Sequencing: the only ordering that survives D-20 + A-01 `[VERIFIED: derived from R-22]`

The constraint is asymmetric and easy to get backwards: **an untracked file in `firestarter` turns
the HOST suite red**, not just the firmware suite.

```
1. Firmware work, one plan at a time, each ending in a `git commit` inside `firestarter/`.
   Firmware plans must be SERIALISED even where files_modified sets are disjoint —
   plan B's uncommitted file turns plan A's own suite run RED (#1 above).
   Between plans: `git -C /workspaces/firestarter status --porcelain` must be EMPTY.

2. After ALL firmware commits land: run the firmware suites.
      python3 -m pytest tests/ -q -o addopts=""       # currently 301 passed
      pio test -e native ; pio test -e native_nodevtools
      pio test -e native_params_v131 ; pio test -e native_loop_v131 ; pio test -e native_trace_v131
      pio run -t clean -e {uno,uno328pb,leonardo} ; pio run -e <each>

3. ONLY THEN the host half. The firmware tree must be clean at this moment (#2 and #3 above).
      cd /workspaces/firestarter_app
      .venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q --cov=firestarter \
          --cov-report=term-missing --cov-fail-under=70
      .venv/ci-replica/bin/python -m ruff check firestarter/ tests/
      .venv/ci-replica/bin/python -m ruff format --check firestarter/ tests/
      .venv/ci-replica/bin/python tools/check_mypy_watermark.py

4. D-16's absent-path child-process sweep (R-15), recorded with `-rs`.

5. Meta-repo record files last (they touch no gate; see R-22's meta-root note).
```

Host-half plans (D-17's gate) are separable in **content** — they depend on no firmware change this
phase — but not in **scheduling**: their own suite run needs the firmware tree clean.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---------|-------------|-------------|-----|
| Capturing the new trace arrays | Hand-transcribe from a `pio test` failure message | `dump_v131_merged_ready_to_paste` via `PLATFORMIO_BUILD_FLAGS="-D EPROM_V131_TRACE_DUMP" … --without-testing` then run the binary | `pio test` swallows `printf`; the failure message gives only totals, never entries |
| "Is the firmware repo present?" | A `some_header.exists()` proxy | `tests/fw_presence.py`'s `FW_REPO_PRESENT` / `requires_fw` / `fw_path` | Scan-target proxies flip PASS→SKIP at exit 0 on a rename — the recorded fail-open class this module exists to remove |
| Re-deriving the inventory JSON | Copy `arrays[].entries` from this document | An independent parse of the committed fixture | `meta.how_to_update` is binding: two independent readings compared, never one parser trusting its own prior output |
| The new blob SHA | A second commit to read `HEAD:<path>` | `git hash-object <path>` | Content-addressed and identical to what `HEAD:` will report; permits one atomic commit (R-11) |
| A CLI checker for the new gates | `scripts/check_<x>.py` | A pytest module under `tests/` | Triggers `test_checker_convention.py`'s 7 legs and obligates raising `FLOOR`/`FIXTURE_FLOOR` in the same commit |
| Changing an env's `test_filter` to run a new case | Fold a suite into `native`/`native_nodevtools` | Nothing — D-04 authors no new case | Both pinned envs are asserted at exactly 141 cases / 17 suites by `compare_native` |
| Overriding `FW_ROOT` in-process | `monkeypatch.setenv("FIRESTARTER_FW_ROOT", …)` | A child process with the env var set | `FW_ROOT` binds at import; `skipif` binds at collection |
| Segment attribution by eye | A 900-row positional table | A machine-checked partition over `(kind, pin, value)` triples, denominator 885 | D-07's own rejection; the vocabulary in R-08 makes it mechanical |

**Key insight:** every "don't" above is a *recorded* prior failure in this repository, not a general
principle. The milestone's standing ethos — a named hole beats a quiet claim — is enforced
mechanically by these gates, so working around one is always more expensive than working with it.

---

## Runtime State Inventory

This phase performs a `git mv` (D-05) and rewrites three JSON records (D-10/D-11/D-13), so the
rename checklist applies.

| Category | Items found | Action required |
|----------|-------------|-----------------|
| **Stored data** | **None** — no database, no ChromaDB/Mem0 collection, no persisted key references `eprom_v131_expected`. Verified by repo-wide grep (R-05: 5 hits, all source/JSON/py in-tree). | none |
| **Live service config** | **None** — no external service (n8n, Datadog, Cloudflare, Tailscale) references any artifact this phase renames. | none |
| **OS-registered state** | **None** — no scheduled task, pm2 process or systemd unit references these paths. | none |
| **Secrets / env vars** | Six env seams touch this phase's work, none of them a secret: `FIRESTARTER_FW_ROOT` (`fw_presence.py:80`, import-bound), `FIRESTARTER_SIZE_BASELINE` (`check_size_baseline.py:95`, `check_build_warnings.py:82`), `FIRESTARTER_META_ROOT` (`meta_presence.py`, import-bound), `FIRESTARTER_CASE_MAP_SCAN_ROOT` + `FIRESTARTER_144_GATE_CHILD` (`test_requirement_case_mapping_v131.py`, import-bound), and the build-time `EPROM_V131_TRACE_DUMP` / `PLATFORMIO_BUILD_FLAGS` pair. **None is renamed by this phase.** All the import-bound ones require a child process to vary. | none — but every one of them must be set in a child process, never monkeypatched |
| **Build artifacts** | `.pio/build/native_trace_v131` is **contaminated** after a dump build (R-10); `.pio/build/*` warm caches invalidate cold warning measurements; `firestarter_app/.coverage` is an untracked artifact of the host run. | `rm -rf .pio/build/<env>` before any recorded cold measurement; leave `.coverage` untracked (it trips nothing — R-21) |

**Two path-string references that a rename would break, both already accounted for:**
`tests/golden/eprom_v131_trace_inventory.json:3` (`meta.source`) and
`tests/test_golden_trace_identity_eprom_v131.py:78` (`_FIXTURE_PATH`). Both name
`test/native/avr/_shared/eprom_v131_expected.h` — the path the **new** fixture occupies, so neither
needs editing. Confirmed by grep, not assumed.

---

## Common Pitfalls

### Pitfall 1: `git mv` without creating the replacement in the same commit
**What goes wrong:** `test_trace_eprom_v131.cpp:45` `#include`s the old path; the env fails to
compile, and the failure looks like a fixture bug rather than a missing file.
**Why:** D-05's "included by nothing" describes the post-rename `_prechange.h`, not the pre-rename
file (C-01).
**How to avoid:** one commit containing the `git mv`, the new fixture at the old path, and the
inventory rewrite.
**Warning signs:** any `pio test -e native_trace_v131` output mentioning `No such file or directory`.

### Pitfall 2: Authoring the new fixture as "three arrays"
**What goes wrong:** link errors on `v131_assert_stream_equals`, `v131_merged_at`, `v131_snapshot`.
**Why:** the header carries the typedef, four kind macros, five helper functions and the recorder
`extern "C"` declarations alongside the arrays (R-06).
**How to avoid:** copy the header, swap only the three array bodies.
**Warning signs:** the new file is materially shorter than ~350 lines.

### Pitfall 3: Recording the dump build's `0 test cases: 0 succeeded` as a run result
**What goes wrong:** a meaningless line enters the phase record as evidence.
**Why:** the dump invocation passes `--without-testing`.
**How to avoid:** the dump build is a *build*; the run is the binary; the test result is a separate,
clean-directory `pio test -e native_trace_v131`.

### Pitfall 4: Feeding a `*_v131` env name to either checker
**What goes wrong:** uncaught `KeyError`, exit 1 — indistinguishable from a real size regression
(R-18).
**How to avoid:** D-22. Record `*_v131` counts only in `size_baseline_v131.json`, by hand.

### Pitfall 5: `--avr-log` on `check_build_warnings.py`
**What goes wrong:** exit 2, `ERROR: unrecognized argument: --avr-log` (R-17).
**How to avoid:** `check_build_warnings.py` takes `--log ENV=PATH` for both kinds.

### Pitfall 6: Running the host suite with the firmware tree dirty
**What goes wrong:** two host modules go RED (R-22), and the failure message blames a "planted-copy
test" that has nothing to do with the change in flight.
**How to avoid:** R-24's sequence; `git -C /workspaces/firestarter status --porcelain` empty first.

### Pitfall 7: Measuring warnings from a warm or dump-flagged build
**What goes wrong:** native watermarks read ~998 warm vs 1166 cold; a watermark lowered from a warm
figure turns the next cold CI run RED.
**How to avoid:** `rm -rf .pio/build/<env>` then a single `pio test -e <env>` at a 540000 ms timeout.
**Warning signs:** a build that completes in seconds rather than minutes.

### Pitfall 8: Lowering the mypy watermark because the gate says you may
**What goes wrong:** a cosmetic tightening is recorded as phase progress; the gate's own rule is
violated.
**How to avoid:** leave `35` alone; this phase lands no type fixes (R-21).

### Pitfall 9: A pre-authored gate leg that is unreachable
**What goes wrong:** RED is observed for the wrong reason (e.g. an import error), the leg is believed
proven, and it never fires on the real defect.
**How to avoid:** D-18 in full — see the RED *and* see the same leg pass for the right reason.

### Pitfall 10: Assuming `pio -d <dir>` works
**What goes wrong:** the gitignored root `platformio.ini` carries two `[platformio]` sections and
the wrong project is selected.
**How to avoid:** every `pio` invocation runs with cwd `/workspaces/firestarter`.

---

## Code Examples

### Capture the new trace (verified this session)
```bash
cd /workspaces/firestarter
PLATFORMIO_BUILD_FLAGS="-D EPROM_V131_TRACE_DUMP" pio test -e native_trace_v131 --without-testing
./.pio/build/native_trace_v131/firestarter_native > /tmp/dump144.txt
grep '^#####' /tmp/dump144.txt
#   ##### EPROM_V131_TRACE_PROTO_07 total=91  strobe_overflow=0 timing_overflow=0
#   ##### EPROM_V131_TRACE_PROTO_08 total=115 strobe_overflow=0 timing_overflow=0
#   ##### EPROM_V131_TRACE_PROTO_0B total=59  strobe_overflow=0 timing_overflow=0
rm -rf .pio/build/native_trace_v131          # MANDATORY before any recorded run
```

### Re-derive the inventory by independent parse (mirrors the gate's own `_parse_arrays`)
```python
# Source: firestarter/tests/test_golden_trace_identity_eprom_v131.py:84-144
import re, subprocess
ARRAY = re.compile(r"static const v131_trace_entry_t\s+(\w+)\[\]\s*=\s*\{(.*?)\};", re.DOTALL)
ENTRY = re.compile(r"\{[^{}]*\}")
p = "test/native/avr/_shared/eprom_v131_expected.h"
text = open(p).read()
for m in ARRAY.finditer(text):
    body = re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", m.group(2), flags=re.DOTALL))
    print(m.group(1), len(ENTRY.findall(body)))
print("blob", subprocess.run(["git", "hash-object", p], capture_output=True, text=True).stdout.strip())
```

### D-16's absent-path child-process run (verified this session)
```bash
mkdir -p /tmp/empty_fw
cd /workspaces/firestarter_app
FIRESTARTER_FW_ROOT=/tmp/empty_fw .venv/ci-replica/bin/python -m pytest \
    tests/test_revision_constants_parity.py -o addopts="" -q -rs
# 6 passed, 8 skipped
# SKIPPED [1] …:563: firestarter firmware checkout absent (no /tmp/empty_fw/.git marker)
```

### D-18 planted-violation shape for D-17's new gate
```python
# Source: firestarter_app/tests/test_revision_constants_parity.py:733-750
_FIXTURES_DIR = Path(__file__).parent / "fixtures"
_FIXTURE_BAD  = _FIXTURES_DIR / "planted_ack_layout_fixed_index.cpp"   # new, this phase

def test_planted_fixed_index_budget_is_detected(monkeypatch):
    assert _FIXTURE_BAD.is_file(), f"committed fixture missing: {_FIXTURE_BAD}"
    monkeypatch.setattr(sys.modules[__name__], "FIRMWARE_ACK_SOURCE", _FIXTURE_BAD)
    with pytest.raises(AssertionError) as excinfo:
        _check_cap03_offset_parity()          # the SAME helper the real leg calls
    msg = str(excinfo.value)
    assert "budget" in msg and "computed" in msg   # names the defect
    assert "ver_len" not in msg                    # LEG ISOLATION
```

### The two current REDs this phase retires (verbatim)
```
uno: flash_used baseline=23954 observed=24824
uno: flash_used baseline=23932 observed=24824 delta=+892 exceeds MERGE-05 uno-class band of 64 B
test_protocol_0x07_am27c512_capture_is_sound_and_deterministic: Expected 198 Was 91.
```

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `pio` (PlatformIO Core) | every native/AVR build and test | ✓ | 6.1.19 (`/usr/local/bin/pio`) | — |
| AVR toolchain (`avr-gcc`) | uno/uno328pb/leonardo builds | ✓ | 7.3.0 (built successfully this session) | — |
| ArduinoFake | native envs | ✓ | `^0.4.0`, present under `.pio/libdeps/` | — |
| `git` | blob-identity + porcelain gates | ✓ | on PATH (`_resolve_git` fail-closed) | none — a missing `git` must FAIL, never skip |
| `.venv/ci-replica` (py3.11) | host suite / ruff / mypy | ✓ | 3.11.15 | ambient 3.12 — **NOT acceptable**, makes the mypy gate fail-open |
| `python3` (ambient) | `firestarter/tests/` pytest | ✓ | 3.12 | — |
| pytest / ruff / mypy | CI-scoped gates | ✓ | 9.1.1 / 0.16.1 / 2.3.0 | — |
| Sibling `../firestarter/.git` | host cross-repo parity legs | ✓ | present as a directory | absent → `requires_fw` skips cleanly (that is D-16's second run, deliberately) |
| Warm `.pio/build/*` caches | speed only | ✓ (all 6 native + 3 AVR) | — | must be **deleted** for cold warning measurements |
| Physical EPROM hardware | — | ✗ | — | **not needed** — Phase 145 owns every bench claim |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none.

---

## Validation Architecture

Nyquist validation is enabled (`workflow.nyquist_validation` absent from `.planning/config.json` ⇒
enabled). For a **verification** phase the validation question is not "does the new behaviour work"
— no behaviour is added — but **"is each new gate genuinely capable of failing?"** That is D-18's
planted-RED discipline, and it is the validation architecture.

### Test Framework

| Property | Firmware repo | Host repo |
|----------|---------------|-----------|
| Framework | pytest (gates) + Unity via PlatformIO (native suites) | pytest 9.1.1 |
| Config file | `platformio.ini` (envs); **no `conftest.py` anywhere under `firestarter/tests/`** — a recorded house rule, so every module resolves its own paths | `pyproject.toml` (`addopts = "-ra -q"`), `tests/conftest.py` |
| Quick run command | `python3 -m pytest tests/ -q -o addopts=""` (15.5 s, **301 passed** today) | `.venv/ci-replica/bin/python -m pytest tests/<module> -o addopts="" -q` |
| Full suite command | the above **plus** `pio test -e {native,native_nodevtools,native_params_v131,native_loop_v131,native_trace_v131}` and `pio run -e {uno,uno328pb,leonardo}` | `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q --cov=firestarter --cov-report=term-missing --cov-fail-under=70` (234 s, **1578 passed / 82.92%**) |

### Phase Requirements → Test Map

| Req | Behaviour being *proven* | Type | Automated command | Exists? |
|-----|--------------------------|------|-------------------|---------|
| TEST-01…05 | the map names only cases that exist; floors non-vacuous | gate (pytest) | `python3 -m pytest tests/test_requirement_case_mapping_v131.py -q -o addopts=""` | ✅ landed at `16e5bdc` |
| TEST-01…05 | the cases themselves pass at this tip | suite (Unity) | `pio test -e native_loop_v131` (79/79) ; `pio test -e native_params_v131` (9/9) | ✅ green today |
| TEST-06 | new fixture identity (blob + per-array counts) | gate (pytest) | `python3 -m pytest tests/test_golden_trace_identity_eprom_v131.py -q -o addopts=""` | ✅ exists; **must be re-pointed** (D-08) |
| TEST-06 | the re-frozen fixture actually matches the live capture | suite (Unity) | `pio test -e native_trace_v131` → must read `5 test cases: 5 succeeded` | ⚠️ **RED today by design** |
| TEST-06 | every one of 885 entries falls in exactly one attributed segment | gate (pytest) | `python3 -m pytest tests/test_<exhaustiveness>.py -q -o addopts=""` | ❌ **Wave 0 — new** |
| TEST-07 | four targets build and pass | build/suite | `pio run -e {uno,uno328pb,leonardo}` ; `pio test -e native` | ✅ green today |
| TEST-07 | host suite + CI-scoped ruff/mypy | suite | R-21's four commands | ✅ green today |
| TEST-07 | constants parity, both directions | gate (pytest) | present: `-m pytest tests/test_revision_constants_parity.py` (14 passed) ; absent: same with `FIRESTARTER_FW_ROOT=/tmp/empty_fw` (6 passed, 8 skipped) | ✅ green today |
| TEST-07 | CAP-03 byte-layout parity across repos | gate (pytest) | `.venv/ci-replica/bin/python -m pytest tests/test_<cap03_layout>.py -o addopts="" -q` | ❌ **Wave 0 — new** |
| TEST-08 | strict size identity | gate (script) | `python3 scripts/check_size_baseline.py --avr-log …` → exit 0 | ⚠️ **RED today** (D-10 retires it) |
| TEST-08 | MERGE-05 band | gate (script) | `python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log …` → exit 0 | ⚠️ **RED today** (D-11 retires it) |
| TEST-08 | warning watermarks | gate (script) | `python3 scripts/check_build_warnings.py --log <env>=<log>` | ✅ AVR green today (0/0/0) |

### Sampling Rate

- **Per task commit:** the single pytest module the task touched, `-q -o addopts=""`.
- **Per firmware plan (before the next plan starts):** `git status --porcelain` empty, then
  `python3 -m pytest tests/ -q -o addopts=""` (301+ passed). This is the D-20 checkpoint.
- **Per wave merge:** the owning repo's full suite.
- **Phase gate:** R-24's full sequence, all five native envs + three AVR targets + both repos'
  suites + the D-16 absent-path sweep, before `/gsd-verify-work`.

### Wave 0 Gaps

- [ ] `firestarter/tests/test_<exhaustiveness>.py` — D-07's 885-entry partition gate, **plus two
      planted fixtures**: (a) an entry deliberately outside every segment → must RED naming the
      entry's index and both stream totals; (b) a segment table whose counts sum to something other
      than 885 → must RED naming the denominator and the observed sum.
- [ ] `firestarter_app/tests/test_<cap03_layout>.py` — D-17's cross-repo gate, behind `requires_fw` /
      `fw_path("src", "firestarter.cpp")`.
- [ ] `firestarter_app/tests/fixtures/planted_ack_layout_*.cpp` — at least two: a **fixed-index**
      budget write (`_ready[20]` instead of `_ready[4 + _vlen]`) and a **truncated emitted length**
      (`4 + _vlen` instead of `4 + _vlen + 2`). Each must RED on its own leg and **not** on the
      other's — leg isolation, per R-14.
- [ ] Optional, house convention: a `ScanPathEntry` for `src/firestarter.cpp` in
      `firestarter_app/tests/scan_paths.py` (R-13 — recommended, not mechanically required).

**No framework install is needed.** Both repos' harnesses exist and are green.

**What "proven" means for each new gate (the D-18 contract, restated so a plan cannot dilute it):**
a gate is proven when its transcript shows (1) RED on a planted violation, with the failure message
naming the specific defect and its location — never a bare "assert False"; (2) GREEN on the real
tree; and (3) evidence that the RED and the GREEN exercised **the same leg**. A leg that REDs because
of an import error or a missing fixture has proven nothing.

---

## Security Domain

`security_enforcement` is absent from `.planning/config.json`, so it is treated as enabled. This
phase adds no runtime code path, no network surface, no parser and no new dependency, so most
categories genuinely do not apply — stated as "no", not omitted.

### Applicable ASVS Categories

| ASVS category | Applies | Standard control |
|---------------|---------|------------------|
| V2 Authentication | no | No authentication surface exists anywhere in this system |
| V3 Session Management | no | No sessions; the serial link is a local point-to-point transport |
| V4 Access Control | no | Single-user local CLI |
| V5 Input Validation | **partially** | The gates this phase authors *parse untrusted-shaped input* only in the sense of reading in-repo source files. The one live validation surface it **asserts about** is `_decode_id_frame`'s plausibility clamps: CAP-01 `[1, 4096]` (`serial_comm.py:400`) and CAP-03 `[1, WRITE_BUDGET_MAX_S=14400]` (`:440`). D-17's gate must not weaken either clamp; both are documented as defenses against a *malfunctioning or mismatched* board, explicitly **not** against an adversarial one (`serial_comm.py:67-77`). |
| V6 Cryptography | no | The only hash used is git's content addressing (`git hash-object` / `rev-parse`), which is an identity mechanism, not a security control here |
| V12 File Handling | **yes, weakly** | Planted-violation fixtures write only under `tmp_path` and every planted leg asserts the real file's blob is unchanged afterwards (`test_py32_flash_map_host.py:388-393` pattern). Reproduce that assertion in any new planted leg. |
| V14 Configuration | **yes** | Six env seams (see Runtime State Inventory). None is a secret; all bind at import. A seam left set from a planted run could redirect a later leg — mitigated by the "first half never reads `os.environ`" pattern (R-04.4). |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard mitigation | Status here |
|---------|--------|---------------------|-------------|
| A gate that silently skips instead of failing | Repudiation | Fail-closed skip audits (`test_git_is_required_not_optional`, `test_this_module_cannot_be_silently_skipped`) | Already enforced; reproduce in every new gate |
| A planted-violation test that mutates the real tree | Tampering | `tmp_path`-only writes + a post-hoc blob-identity assertion + a porcelain assertion | Enforced by all three existing planted-copy modules |
| `shell=True` in a gate's subprocess call | Tampering / Elevation | List-form `argv`, invoked directly | House rule; every existing gate follows it — `subprocess.run([git_bin, *args], …)` |
| A malfunctioning board wedging the host with an absurd budget | DoS | The `[1, 14400]` clamp, which leaves the attribute `None` rather than raising | Already shipped; D-17's gate must assert the clamp survives |
| An env seam set wrong in a real run | Tampering | Only the *root* is overridable, never the marker name or a floor literal | `fw_presence.py:66-76` states this explicitly |

**Non-claim:** nothing in this phase hardens the serial protocol against an adversarial device. The
existing clamps are correctness guards against mismatched firmware, and the phase record should not
describe them otherwise.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|-------|---------|---------------|
| A1 | The new fixture will be authored by copying the existing header and swapping three array bodies (rather than by some other mechanism) | R-06 | Low — any other approach still has to satisfy the same link surface; the risk is wasted effort, not a wrong gate |
| A2 | A six-segment taxonomy over `(kind, pin, value)` triples can partition both streams without residue | R-08 | Medium — if some entry resists classification, D-07's "no entry unattributed" forces either a seventh segment or an explicit named residue. Either is acceptable; discovering it late is the cost. |
| A3 | `native_pinmap_provisional` still reports 10 cases / 1 suite (not re-run this session) | R-19 | Low — nothing in Phases 140–144 touches that suite; verify in the consolidated run rather than trusting this |
| A4 | Cold native warning counts are still 1166 (not re-measured cold this session; AVR was measured and is 0/0/0) | R-20, Pitfall 7 | **Medium — this is the one number I did not re-derive.** A cold native run is expensive and D-23 says the headroom is zero, so if a Phase 140–143 change added a native warning the gate is already RED and nobody has seen it. The consolidated run must measure this cold, early. |
| A5 | Adding `src/firestarter.cpp` to `scan_paths.py` is optional | R-13 | Low — the enforcing test is a `>=` floor and two existing modules already omit their targets |

**Everything else in this document was executed, not assumed.**

---

## Open Questions

1. **Is the cold native warning count still ≤ 1166?**
   - What we know: the watermark is `<= 1166` with **zero** headroom on both `native` and
     `native_nodevtools`; all three AVR envs measured `0` this session and PASS.
   - What's unclear: I ran the native envs (`141/141` both) but did not capture and count a **cold**
     warning figure — that requires `rm -rf .pio/build/<env>` plus a full uninterrupted rebuild per
     env.
   - Recommendation: make this the **first** measurement of the consolidated D-02 run, not the last.
     If it exceeds 1166, that is a Phase 140–143 regression surfacing in Phase 144, and it needs
     naming before any baseline is rewritten.

2. **Does D-07's exhaustiveness gate read the fixtures, or a committed segment table?**
   - What we know: D-07 requires that all 885 entries fall into exactly one attributed segment, and
     that an unattributed entry fails the gate.
   - What's unclear: whether the segment boundaries live in the gate's own frozen table (like
     `_REQUIREMENT_CASES`) or are derived from the fixtures' comment banners.
   - Recommendation: **frozen table**, matching the landed mapping gate's precedent — a derived
     partition would be a parser trusting its own output, which is exactly what
     `meta.how_to_update` forbids for the sibling inventory. A frozen table also makes the planted
     "unattributed entry" violation trivially constructible.

3. **Does the pre-change side of the 885 come from the renamed `_prechange.h` or from the git blob?**
   - What we know: after the rename the file still exists in the tree at the new path, and its
     content is byte-identical.
   - What's unclear: whether the gate should parse `_prechange.h` (making it load-bearing, which
     D-08 explicitly declined to gate) or read `git show ca3e09f1…`.
   - Recommendation: parse `_prechange.h` **for the partition** while leaving D-08's identity
     non-claim intact. Parsing it does not gate-assert its blob; the two are different claims, and
     conflating them would either overclaim (implying it is pinned) or force a scope expansion D-08
     rejected.

4. **A prior 144-RESEARCH.md and seven plans already exist, and plan 144-01 has landed.**
   - What we know: `.planning/phases/144-tests-build-verification/` contains `144-01..07-PLAN.md`,
     `144-PATTERNS.md`, `144-VALIDATION.md` and a prior `144-RESEARCH.md` (committed at `fcd23a5e`);
     firmware `HEAD` is the 144-01 commit; `STATE.md` says `status: executing`.
   - What's unclear: whether this research pass is meant to supersede those plans or to re-verify
     them mid-execution.
   - Recommendation: treat this document as **re-verification at the current tip**. Its corrections
     (C-01, A-01, A-02) and its live measurements are additive; nothing here invalidates a landed
     plan. The prior RESEARCH.md is recoverable at `fcd23a5e` if a side-by-side is wanted.

---

## Sources

### Primary — HIGH confidence (executed this session)

- `pio test -e {native, native_nodevtools, native_loop_v131, native_params_v131, native_trace_v131}` — case/suite counts
- `pio run -e {uno, uno328pb, leonardo}` — flash/RAM figures
- `PLATFORMIO_BUILD_FLAGS="-D EPROM_V131_TRACE_DUMP" pio test … --without-testing` + direct binary run — the 91/115/59 capture
- `python3 scripts/check_size_baseline.py` (default and `--policy merge05`) — both RED verdicts verbatim
- `python3 scripts/check_build_warnings.py --log …` — AVR PASS
- `.venv/ci-replica/bin/python -m pytest tests/ …` — 1578 passed / 82.92%
- `.venv/ci-replica/bin/python -m {ruff check, ruff format --check}`, `tools/check_mypy_watermark.py`
- `FIRESTARTER_FW_ROOT=/tmp/empty_fw … pytest tests/test_revision_constants_parity.py -rs`
- `git rev-parse HEAD:test/native/avr/_shared/eprom_v131_expected.h` → `ca3e09f1…`
- Independent Python re-parse of the three suites' `RUN_TEST` names and the fixture's three arrays

### Primary — HIGH confidence (source read this session)

- `firestarter/platformio.ini` (env blocks at :293 / :331 / :373, all confirmed)
- `firestarter/src/firestarter.cpp:160-212` — the `MSG_OK_READY` pack
- `firestarter/test/native/avr/_shared/eprom_v131_expected.h` (649 lines)
- `firestarter/test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp`
- `firestarter/tests/test_golden_trace_identity_eprom_v131.py`, `tests/golden/eprom_v131_trace_inventory.json`
- `firestarter/tests/test_requirement_case_mapping_v131.py` (landed by 144-01)
- `firestarter/tests/test_checker_convention.py`, `tests/test_ack_layout_source_contract_v143.py`, `tests/test_flash_path_record_sync.py`
- `firestarter/scripts/check_size_baseline.py`, `check_build_warnings.py`, `scripts/baseline/*.json`
- `firestarter/.github/workflows/{build,beta-build}.yml`
- `firestarter_app/firestarter/serial_comm.py:344-442`
- `firestarter_app/tests/{fw_presence,scan_paths,test_revision_constants_parity,test_hw_revision_gate,test_py32_flash_map_host,test_py32_asset_name_host}.py`
- `firestarter_app/.github/workflows/ci.yml:80-87`

### Secondary — MEDIUM confidence (project records, cross-checked against the above)

- `.planning/phases/144-tests-build-verification/144-CONTEXT.md` — the 23 locked decisions
- `.planning/phases/141-per-byte-program-loop/141-NEW-TRACE.md` §1 — the dump commands (re-executed)
- `.planning/REQUIREMENTS.md:226-243`, `.planning/ROADMAP.md:431-443`, `.planning/STATE.md`
- `/workspaces/CLAUDE.md`, `firestarter/CLAUDE.md`, `firestarter_app/CLAUDE.md`

### Tertiary — LOW confidence

None. No claim in this document rests on training data or on an unverified web source.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|------|-------|--------|
| Requirement→case mapping (R-01…R-04) | **HIGH** | 88 counted three ways; 29 mapped names each verified present by an independent parse; the gate itself read line by line |
| Trace freeze mechanics (R-05…R-11) | **HIGH** | Capture executed live and matched the prediction exactly; the include-graph correction found by grep, not inference |
| CAP-03 layout (R-12…R-14) | **HIGH** | Both sides read with line numbers; the byte table is a direct transcription, not a reconstruction |
| Absent-path run (R-15) | **HIGH** | Executed; env var read from source |
| Size baselines (R-16…R-20) | **HIGH** | Every figure measured; both REDs reproduced verbatim; the `KeyError` reproduced |
| Host green state (R-21) | **HIGH** | Full suite + three CI gates executed on the CI-parity interpreter |
| Sequencing / porcelain (R-22…R-24) | **HIGH** for the three coupling sites (grepped and read); **MEDIUM** for the recommended ordering, which is derived rather than executed end to end |
| Cold native warning counts | **MEDIUM** | Not re-measured cold — see Assumption A4 and Open Question 1 |

**Research date:** 2026-08-14
**Valid until:** ~2026-09-13 for the tooling facts; **invalid the moment any commit lands in
`firestarter/`** for the measured size/count/blob figures — every one of them is tip-specific.
