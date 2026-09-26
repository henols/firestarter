# Phase 144: Tests & Build Verification - Context

**Gathered:** 2026-08-13
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase **proves** what Phases 140–143 built. It adds no algorithm behavior, changes no
programming path, and — see D-04 — edits **no file under `firestarter/src/`**.

What it delivers:

1. A machine-checked map from `TEST-01…05` onto the native cases that actually prove them, plus new
   cases only where a gap is named and proven (`TEST-01…05`).
2. The retirement of the milestone's first standing RED: the pre-change golden trace is frozen as a
   historical artifact, a new fixture is captured at this phase's tip, and the old→new diff is
   attributed decision by decision with machine-checked exhaustiveness (`TEST-06`).
3. Green builds and suites across `uno` / `uno328pb` / `leonardo` / `native` / `native_nodevtools`,
   the host suite, CI-scoped ruff and the mypy watermark, dual-repo constants parity, and a new
   cross-repo CAP-03 byte-layout parity gate (`TEST-07`).
4. The retirement of the milestone's second standing RED: per-target flash and RAM measured against
   the PREP-03 baseline, the baselines re-anchored to v1.31, and the re-anchor disclosed rather than
   presented as a pass (`TEST-08`).

**Not in this phase:** any bench run or claim about real silicon (Phase 145); the honesty ledger,
claim gate, gh#15 reconciliation and the ROADMAP prose correction D-01 of Phase 143 deferred
(Phase 146); wiring the `*_v131` envs into CI (D-15); any change to a chip's `support_status`.

</domain>

<decisions>
## Implementation Decisions

### Native tests — TEST-01…05

- **D-01:** **The deliverable is map + attest + fill gaps, not bulk re-authoring.** Phase 144 lands a machine-checked requirement→case mapping — a gate under `firestarter/tests/` that parses the v131 suite sources and asserts each `TEST-0N` names `RUN_TEST` cases which actually exist — and authors new cases only where a gap is named and proven. This follows H6 verbatim (`141-LOOP-RECORD.md` §12): TEST-01 owns "the requirement flip and the consolidated cross-phase accounting", not a second copy of behavior already proven. The risk this removes is specific: a requirement flipped against a case that was later renamed or deleted. A prose-only mapping table was rejected as the same shape as the hollow parity legs Phase 120 had to rebuild.

- **D-02:** **Evidence is ONE cold consolidated run, recorded verbatim.** Every v131 env is re-run at this phase's tip — `native_params_v131`, `native_loop_v131` (both its suites), `native_trace_v131` — alongside `native` and `native_nodevtools` at their pinned 141 cases / 17 suites. Citing the owning phases' recorded runs was rejected: no single run has ever exercised all 88 existing cases against the final tree, since Phase 141's cases have never run against 142's and 143's landed code together. A cross-phase interaction is exactly what this run exists to catch.

- **D-03:** **TEST-03 flips on the pure-function proof, with the in-loop wiring recorded as an explicit non-claim.** Reversed mid-discussion once the true cost was measured. `overprogram_factor` is `0` on every shipped row (`eprom_params.cpp:46-48`, asserted by `test_loop04_no_live_row_emits_an_overprogram_pulse`), so the overprogram path is structurally unreachable on live data; `eprom_overprogram_us` is proven directly by five cases from plan 141-08. An end-to-end synthetic-row oracle would need a params-table substitution, which needs either a seventh env or a seam in `src/` — and `eprom.cpp` **and** `eprom_params.cpp` are both blob-pinned by `firestarter/tests/golden/protocol_branch_inventory.json`, with `test_params_table_has_no_second_selector` separately asserting the table is switch-free. The operator chose the honest cheap option over paying that cost during a verification phase. **The non-claim must appear in the phase record:** the arithmetic is proven; the in-loop wiring on a live row is not, because no shipped row sets the factor.

- **D-04:** **No new native env, and no edit to any file under `firestarter/src/`.** D-03's reversal removes the only reason this phase had to touch a pinned source. Consequence, and it is a strong one: `eprom.cpp` and `eprom_params.cpp` keep their recorded blob SHAs (`cedc88dc…` / `5dffe841…`) all phase, so `tests/test_protocol_branch_inventory.py` and the D-13/D-18 golden stay **green throughout** — unlike Phases 141, 142 and 143, none of which could say that. A plan that finds itself needing an `src/` edit must stop and report, not absorb it.

### Trace freeze and diff — TEST-06

- **D-05:** **The pre-change fixture survives by a pure rename, and is included by nothing.** `git mv firestarter/test/native/avr/_shared/eprom_v131_expected.h → eprom_v131_expected_prechange.h`, content byte-untouched. Because a git blob SHA is content-only and path-independent, `ca3e09f164e6e1c541ecb63d15bbebf5bce41d70` still matches after the move — Phase 138's "this artifact is untouched" proof survives intact instead of being re-derived. No TU `#include`s it, so it never compiles and cannot trip the zero-headroom native warning watermark (D-23). Keeping both array sets in one header was rejected because the file's blob SHA would necessarily change, destroying that proof.

- **D-06:** **The new fixture is captured fresh at THIS phase's tip — `141-NEW-TRACE.md`'s arrays are stale and must not be pasted.** That document holds a ready-to-paste dump at 91 / 119 / 59, but Phase 142 moved `0x08` from 119 → **115** (`142-VPP-RECORD.md` §3, F-142-04). Phase 143 added **zero** frames because `native_trace_v131` pins `millis()` to `AlwaysReturn(0)` (`143-HOST-RECORD.md` §7.3), so TEST-06 will find **zero** D-02-attributable strobes — that is a prediction to confirm, not to assume. Expected totals at capture: **91 / 115 / 59**. A deviation is stop-and-report.

- **D-07:** **Attribution is per-segment, backed by a machine-checked exhaustiveness gate.** Partition both streams into named segments (init, route assert, address set, pulse, verify read, teardown); table the per-segment old→new counts; attribute each delta to a named decision from Phases 140–143. A script asserts every one of the 885 entries (620 old + 265 new) falls into exactly one attributed segment — so "every changed strobe attributable to a named decision" is **machine-proven**, and an unattributed entry fails the gate. A full 900-row positional table was rejected as unreadable and error-prone at that volume; counts-plus-narrative was rejected as a blanket snapshot update wearing a paragraph, which is what TEST-06 forbids.

- **D-08:** **The inventory is re-pointed at the NEW fixture only — and the pre-change file is deliberately left un-gated.** `firestarter/tests/golden/eprom_v131_trace_inventory.json` gets fresh entry counts and blob SHA for `eprom_v131_expected.h`, keeping the six-assertion identity gate armed for v1.32. Its `meta.how_to_update` is binding: re-derive by independent parse, never hand-edit a count. **Named non-claim:** with a single record, nothing gate-asserts `eprom_v131_expected_prechange.h`. Its preserved blob SHA `ca3e09f1…` is cited in the phase record and stays verifiable by hand via `git rev-parse HEAD:<path>`, but it is not machine-checked. Record that as a gap, do not imply otherwise.

### Size baseline and MERGE-05 — TEST-08

- **D-09:** **PREP-03 and `size_baseline.json` are the SAME anchor, and it is the authoritative one.** `scripts/baseline/size_baseline.json` still holds 23954 / 24004 / 26016 — exactly Phase 138's measured figures, which `138-BASELINE.md` §5 confirmed byte-identical. So TEST-08's "measured against the PREP-03 baseline" and the script's default seam agree. F-142-09's "two anchors disagree" is about `size_baseline_base01.json` (a v1.24 artifact) versus that anchor — it is **not** an ambiguity about which anchor TEST-08 means. Decided mechanically; no discussion needed. Measured tip: **24824 / 24874 / 26906**, i.e. **+870 / +870 / +890 B**, RAM unmoved on all three, `leonardo` at 93.8% with 1766 B headroom.

- **D-10:** **`size_baseline.json` IS rewritten to the v1.31 tip.** A dedicated commit whose message states every delta and its attributing phase. The everyday strict-identity gate goes GREEN and v1.32 drift becomes detectable again. The reasoning that decided it: a gate that is RED for a known accepted reason can no longer report an **unknown** one — a surprise regression in Phase 145 or 146 would look identical to the noise already showing. Record-only-and-defer was rejected because it leaves the gate blind for two more phases and hands measurement work to a phase scoped for docs and claims.

- **D-11:** **`size_baseline_base01.json` is ALSO re-anchored, and the band is repurposed as a forward tripwire.** Operator decision, taken with the tradeoff stated: re-anchoring ends MERGE-05's ability to make its original v1.24 comparison. What replaces it is coherent and deliberate — the `0 B` / `64 B` band literals stay, but now measure growth from **24824 / 24874 / 26906**, arming against Phases 145/146 and v1.32 instead of against a milestone that already shipped. `leonardo`'s 1766 B of headroom gains an actual guard. **MERGE-05's v1.24 semantics are retired; its forward mechanism is kept.** `MERGE05_UNO_CLASS_FLASH_BAND` is not widened.

- **D-12:** **The v1.24 content is not preserved in-tree — git history is enough.** Overwrite `size_baseline_base01.json` in place. The figures stay recoverable at the pre-change blob, and `138-BASELINE.md` §5 already records them in prose alongside the verdicts they produced. Consistent with D-10's plain rewrite; no new frozen files this phase.

- **D-13:** **`size_baseline_v131.json` is refreshed from the same consolidated run.** It was created as a running record of the envs no gate covers, so leaving it stale removes its only purpose. `native_loop_v131` has grown to 79 cases and `native_trace_v131`'s counts move when TEST-06 re-freezes. No live gate reads this file — F-138-05 forbids feeding a `*_v131` env name to either checker — so refreshing it cannot turn anything RED.

- **D-14:** **The re-anchor disclosure is MANDATORY and its wording is constrained.** Claude's call, not discussed, because the milestone's ethos settles it. If `--policy merge05` reads green after D-11, the phase record must say **green because the anchor moved to v1.31**, never *green because growth stayed inside the band*. An undisclosed re-anchor is precisely the overclaim Phase 146's claim gate exists to catch, and it would be this milestone committing its own anti-pattern. F-141-01's operator acceptance and the +204 B parameter-table mechanism are cited alongside. The honesty-ledger entry itself belongs to Phase 146 / CLOSE-02; **stating the fact** belongs here.

### Gate reach — TEST-07

- **D-15:** **The three `*_v131` envs stay a local run-by-name obligation, recorded loudly.** No CI wiring. TEST-07's text names only `native`; wiring `build.yml` / `beta-build.yml` is a v1.32 infrastructure change, not a v1.31 test obligation. The standing F-140-11 position holds, and the milestone's habit is to name a hole rather than quietly widen scope to fill it. **Never imply CI covers these envs** — restate the absence in the phase record.

- **D-16:** **Constants parity is proven in BOTH directions, and the absent-path run must be a subprocess.** Run the parity legs locally where the sibling firmware repo is present and record the verbatim PASS; then re-run with `FIRESTARTER_FW_ROOT` pointed at an empty directory to prove the absent path skips cleanly rather than erroring. `tests/fw_presence.py` binds `FW_ROOT` / `FW_REPO_PRESENT` / `requires_fw` **at import**, and `pytest.mark.skipif` binds at collection, so `monkeypatch.setenv` has no effect — the second run MUST be a child process with the env var set (RESEARCH Correction C-15). This is the sweep that catches devcontainer-masked CI defects before a beta push. Adding a firmware checkout to app CI was rejected: it forces an unanswered question about which firmware ref to pin, and `beta` and the v1.31 branch disagree today.

- **D-17:** **The CAP-03 byte-layout parity gate IS built, in `firestarter_app/tests/`, behind `requires_fw` / `fw_path`.** F-143-07 / H2 names TEST-07 as its owner. It asserts the firmware `MSG_OK_READY` pack order `[buffer u16][hw_rev u8][ver_len u8][ver bytes][budget u16]` against the host's `_decode_id_frame` offsets, **including the computed `ver_end`** the budget is read at — never a fixed index. Rationale is concrete, not theoretical: BF-1 was a two-repo protocol with nothing comparing the sides, it went unnoticed for three milestones, and it made the v1.31 app refuse every connection to a v1.31 build. The app repo is the right home because every existing parity gate lives there and `fw_presence.py` is the sanctioned cross-repo probe.

- **D-18:** **Every new gate leg is seen RED on a planted violation before its GREEN is believed.** Carried unchanged from Phases 140/141/142/143 (D-25). Applies to D-01's mapping gate, D-07's exhaustiveness gate and D-17's layout gate. Each transcript captured verbatim in its plan's SUMMARY. A pre-authored leg can be **unreachable** — RED proves nothing until the leg has also been seen to pass for the right reason.

### Cross-cutting mechanics

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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase requirements and milestone framing
- `.planning/REQUIREMENTS.md` §"Tests & Build" — TEST-01…08, the exact requirement text (lines 226–243).
- `.planning/ROADMAP.md` §"Phase 144: Tests & Build Verification" — goal, dependencies, and the four
  success criteria (lines 431–443).
- `.planning/PROJECT.md` §"Current Milestone: v1.31" — the 6.25 V evidence ceiling and the
  out-of-scope list; the Phase 143 close footer (line 1177) carries the current gate state.

### Prior-phase records — the hand-offs this phase consumes
- `.planning/phases/138-preconditions-baseline/138-BASELINE.md` — **§4** the frozen trace (fixture
  path, blob `ca3e09f1…`, arrays 198/221/201 and the two pinning mechanisms); **§5** the size and
  suite-count baseline this phase measures against (23954/24004/26016, the 141/17 pins, the 1166 and
  138 warning watermarks, the verbatim gate verdicts); **§7** the findings register incl. F-138-05.
- `.planning/phases/138-preconditions-baseline/138-03-TRACE-CAPTURE.md` — **§2** the measured entry
  counts; **§8** the freeze record and its three planted break classes.
- `.planning/phases/138-preconditions-baseline/138-04-HOST-BASELINE.md` — **§3** the host-suite
  baseline and the CI-parity interpreter constraint D-21 restates.
- `.planning/phases/141-per-byte-program-loop/141-LOOP-RECORD.md` — **§12 hand-offs H5** (dispositions
  this phase must NOT re-litigate: `verify_mode` is consumed; `cap_us=0` yields 0 µs) and **H6** (the
  TEST-01 seam D-01 implements); **§10** (the three `*_v131` envs run in no CI leg); **§15** findings
  incl. F-141-01 (MERGE-05 operator-accepted) and F-141-02 (the ~14× prediction miss).
- `.planning/phases/141-per-byte-program-loop/141-NEW-TRACE.md` — the post-change dump and §5 arrays.
  **Read D-06 first: these are STALE at 91/119/59 and must not be pasted.**
- `.planning/phases/142-high-voltage-routing/142-VPP-RECORD.md` — **§3** every `Was` value this
  milestone produced (the `0x08` 119→115 movement dated to plan 142-04); **§1.5** the cold figures and
  both MERGE-05 anchors verbatim; **§15** F-142-03, F-142-04, F-142-09.
- `.planning/phases/143-host-timeout-progress-pulse-override/143-HOST-RECORD.md` — **§7.1** the cold
  flash/RAM table D-09 cites; **§7.3/§5.4** the zero-added-frames confirmation D-06 depends on;
  **§7.4** the verbatim `check_size_baseline.py` output; **F-143-07** and **H1/H2/H3**, the three
  hand-offs this phase discharges; **F-143-02/F-143-03**, the porcelain coupling D-20 names.
- `.planning/phases/143-host-timeout-progress-pulse-override/143-CONTEXT.md` — **D-25** (the planted-RED
  discipline D-18 carries) and **D-08** (CAP-03's pack layout D-17 asserts).

### Firmware artifacts this phase moves or reads
- `firestarter/test/native/avr/_shared/eprom_v131_expected.h` — the fixture D-05 renames (649 lines,
  three arrays plus `v131_merged_at`'s splice rule).
- `firestarter/tests/golden/eprom_v131_trace_inventory.json` — D-08's target; `meta.how_to_update` is
  binding.
- `firestarter/tests/test_golden_trace_identity_eprom_v131.py` — the six-assertion parallel gate.
- `firestarter/tests/golden/protocol_branch_inventory.json` — pins **both** `src/proms/eprom.cpp`
  (`cedc88dc…`) and `src/proms/eprom_params.cpp` (`5dffe841…`); D-04's read-only invariant protects it.
- `firestarter/tests/test_protocol_branch_inventory.py` — incl. `test_params_table_has_no_second_selector`.
- `firestarter/platformio.ini` — the six native envs; `[env:native_trace_v131]` at :293,
  `[env:native_params_v131]` at :331, `[env:native_loop_v131]` at :373. Their caveat blocks are the
  authoritative statement of D-15 and D-22.
- `firestarter/scripts/check_size_baseline.py` — `NATIVE_ENVS` at :100, `MERGE05_UNO_CLASS_FLASH_BAND`
  at :107, `compare_avr_policy_merge05` at :214.
- `firestarter/scripts/baseline/size_baseline.json`, `size_baseline_base01.json`,
  `size_baseline_v131.json` — D-10, D-11 and D-13's three targets.
- `firestarter/test/native/avr/test_loop_eprom_v131/` (47 cases), `test_vpp_eprom_v131/` (32),
  `test_eprom_params_v131/` (9) — the existing coverage D-01 maps.

### Host artifacts
- `firestarter_app/tests/fw_presence.py` — `FW_ROOT` / `FW_REPO_PRESENT` / `requires_fw` /
  `fw_path` / `MissingScanTargetError`. **Read its import-time-binding warning before writing D-16's
  absent-path run.** `fw_path` at :117.
- `firestarter_app/tests/test_revision_constants_parity.py` — the bidirectional CMD_/FLAG_ gate,
  `FIRMWARE_HEADER` at :148, planted-violation fixtures at :728+.
- `firestarter_app/tests/fixtures/planted_constants_{value_drift,fw_missing,host_missing}.h` — the
  planted-violation pattern D-18 requires of D-17's new gate.
- `firestarter_app/firestarter/serial_comm.py` — `_decode_id_frame` and CAP-02's variable-length tail;
  the computed `ver_end` D-17 asserts against.
- `firestarter_app/.github/workflows/ci.yml` — ruff check / ruff format --check / mypy watermark /
  pytest --cov (:80–:87); the CI-scoped commands TEST-07 means.
- `firestarter/.github/workflows/build.yml` (:142, :155, :193) and `beta-build.yml` (:122, :128, :145)
  — the only `pio test` / `pio run` legs that exist. Evidence for D-15.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **88 existing v131 native cases** across three suites: `test_loop_eprom_v131` (47),
  `test_vpp_eprom_v131` (32), `test_eprom_params_v131` (9). TEST-01…05 are far better covered than
  the roadmap implies — `test_each_protocol_resolves_to_its_own_distinct_row` (TEST-01),
  `test_loop01_pulse_width_never_grows_between_attempts` (TEST-02), the five `test_loop03_*`
  (TEST-03), `test_loop05_a_byte_that_misses_within_max_pulses_aborts_the_block` plus the asserted
  `u24 address + u8 pulse count` payload and `test_vpp02_x3/x4/e1` (TEST-04), the four
  `test_loop06_*` and the two fallback cases (TEST-05).
- **`tests/fw_presence.py`** — the sanctioned cross-repo probe. Repo presence keys on
  `../firestarter/.git`, a marker no in-repo rename can move; a missing scan target under a *present*
  repo is a hard `MissingScanTargetError`, never a silent skip. D-17's new gate uses it rather than
  authoring its own proxy.
- **The planted-violation fixture pattern** in `firestarter_app/tests/fixtures/planted_constants_*.h`
  — a working template for D-18's proof of D-17.
- **`dump_v131_merged_ready_to_paste`** — the recorder helper that produced `141-NEW-TRACE.md` §5;
  D-06 re-runs it rather than hand-authoring arrays.

### Established Patterns
- **A pinned env may never absorb a new suite.** `native` and `native_nodevtools` are asserted at
  exactly 141 cases / 17 suites by `compare_native`, which is why envs 4, 5 and 6 exist. Phase 142
  reused `native_loop_v131` for a second suite rather than creating a seventh — the standing pattern,
  and D-03's reversal means this phase needs neither.
- **Two independent pins per golden.** Every frozen artifact carries a blob-SHA check *and* a
  structural check, because a whole-file match cannot distinguish "unchanged" from "an array deleted
  with its consumer". D-08 preserves that shape.
- **Goldens are re-derived by independent parse, never hand-edited.** Both inventories carry a binding
  `meta.how_to_update`; the commit message must state which site changed and why.
- **Gates fail OPEN across the repo boundary by design** — `requires_fw` skips when the sibling repo
  is absent, which is honest but means CI proves nothing about parity. D-16 measures both directions
  instead of pretending otherwise.

### Integration Points
- `firestarter/tests/` — D-01's mapping gate and D-07's exhaustiveness script land beside the existing
  golden-identity gates.
- `firestarter_app/tests/` — D-17's CAP-03 layout gate lands beside the existing parity gates.
- `firestarter/scripts/baseline/` — D-10, D-11, D-13 rewrite three JSONs; `check_size_baseline.py`
  itself is **not** modified (D-11 keeps the band literals).
- `firestarter/test/native/avr/_shared/` — D-05's rename and D-06's new fixture.

</code_context>

<specifics>
## Specific Ideas

- **Expected capture totals are 91 / 115 / 59** (D-06). Anything else is stop-and-report, not
  absorb — the 0x08 value in particular is the one that already moved once this milestone.
- **885 is the exhaustiveness gate's denominator** (620 pre-change entries + 265 new).
- **`ca3e09f164e6e1c541ecb63d15bbebf5bce41d70` must still resolve after the rename.** That is the
  single check proving D-05 preserved the artifact rather than re-created it.
- **The re-anchor sentence is load-bearing.** "MERGE-05 reads green because its anchor moved to
  v1.31, not because growth stayed inside v1.24's band" — D-14. Say it in those terms.

</specifics>

<deferred>
## Deferred Ideas

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

### Reviewed Todos (not folded)

18 pending todos matched Phase 144 on keyword score; **none folded** — all are behavior or
infrastructure work in a phase that adds no behavior. Highest-scoring, all rejected as scope creep:
"Skip VPP error/warning checks when VPP is unused (reads/blank-checks)" (0.9, firmware behavior),
"FM1608 byte 0 write never lands — register cache-skip elides all three shift-register strobes"
(0.9, a different write path), "Prove the PlatformIO dev-tools build flag fails CLOSED" (0.9, a
gate this phase does not own), "CONFIG_VERSION is not bumped when a calibration default changes"
(0.7). The matches are keyword artifacts — "phase", "build", "baseline", "address" — not scope
overlap.

</deferred>

---

*Phase: 144-Tests & Build Verification*
*Context gathered: 2026-08-13*
