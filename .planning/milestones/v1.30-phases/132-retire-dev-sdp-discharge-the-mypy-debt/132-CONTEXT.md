# Phase 132: Retire `dev sdp` & Discharge the mypy Debt - Context

**Gathered:** 2026-08-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Delete `firestarter dev sdp` from the host CLI, keep alive every piece two later phases depend on,
and drive `firestarter_app`'s primary `ci` job from RED to GREEN at the existing watermark of 35.

**In scope:** `cli_handlers.py`'s `dev_sdp` span and its four gates; a new
`firestarter/sdp_honesty.py` carrying the survivors; `git mv tests/test_dev_sdp_cmd.py` →
`tests/test_sdp_honesty.py` with `tools/check_no_exists_proxy.py`'s target list edited in the same
commit; a `COMMAND_NAMES[COMMAND_SDP_*]` dereference test; a typed `AppContext` factory + fixture in
`tests/conftest.py`; the ~30 mechanical mypy fixes that reach ≤35; the P-21 tripwire (comment at the
auto-unlock decision site + a test named for the dependency); the stale `301`/`377` comment
corrections; the scoped `test_help_dev` snapshot update; a committed numpy-free CI-replica venv
script; one operator-run certifying CI dispatch.

**Out of scope — and load-bearing:**
- **`eprom_operations.py`'s ring-fenced `[union-attr]` cluster is NOT opened.** Already an operator
  decision (`REQUIREMENTS.md` §Out-of-Scope, 2026-08-03) → `FUT-MYPY-02`. Research's
  operator-decision #2 asked for this to be decided at 132's scoping; it is decided, and this phase
  must not reopen it as a side effect of touching that file for `sdp_lock`/`sdp_unlock`.
- **No watermark edit.** The `35` in `pyproject.toml` is not touched (see D-09). Ratcheting to the
  true count belongs to a later phase, with the number this phase measures.
- **No honesty caveat added to the `write` auto-unlock path** (D-05).
- **No leg, no `--sdp-relock`, no channel gating.** Phases 133/134, 135, 136.
- **`firestarter` is not touched at all.** Host-only milestone; no firmware change, no dual-repo
  lockstep, no `.hex` re-cut.
- **The `.ambr` channel-split parametrisation is Phase 136's**, not this phase's (D-13).
- **Consolidating all eight `make_app_context` copies** — only the five typed ones carry errors, and
  only four survive the deletion. Consolidating the three untyped ones is scope creep.

</domain>

<decisions>
## Implementation Decisions

### Three live corrections measured this session — read before planning

These change what gets built. Each was measured in this session against the milestone branch, not
inherited from the record.

1. **Deleting `dev sdp` deletes the honesty caveat's only *production* carrier, not just its test.**
   All three honesty strings live in exactly one place: `cli_handlers.py:2215`, `:2267`, and
   `:2316-2318` — inside the span being deleted. `eprom_operations.py`'s `sdp_lock` (`:1784`) and
   `sdp_unlock` (`:1736`) carry no such wording, and the D-10 comment at `:2305-2314` explains why
   they cannot: `get_response()` filters the entire INFO band at `serial_comm.py:424`, so the
   operation layer never sees the firmware's `0x5F`/`0x61` frame. The D-14
   `EpromOperationError` → `MSG_ERR_UNKNOWN_CMD` → `FirmwareOutdatedError` arm is likewise
   `dev_sdp`-only, at `:2295-2302`. So RETIRE-03's "retargeted onto the new leg" is **not
   executable in Phase 132** — the leg is Phase 134. P-16's own prevention #2 says to do the leg and
   the deletion in one phase; the roadmap deliberately split them. D-01/D-02 resolve this.

2. **RETIRE-08's "three" stale references is five, across two files.** Measured:
   `firestarter/constants.py:69-70` (one reference), and
   `tests/test_revision_constants_parity.py:71-72`, `:527`, `:549`, `:585-586` (four). R-7's table
   named three. Note `:549` sits inside an assertion *message* string, so correcting it changes a
   test's failure text. Also confirmed: R-7's corrected coordinates are **right** —
   `_setup_operation` is at `:315` with its `COMMAND_NAMES[cmd]` deref at **`:329`**, and
   `_operation_context` at `:376` with its deref at **`:405`**.

3. **Post-Phase-131 the devcontainer no longer false-greens — it fails loudly.** Run this session:
   `python3 tools/check_mypy_watermark.py` prints *"ERROR: mypy exited 2, which is neither the
   clean-run (0) nor errors-found (1) exit code. Treating as a tool/config failure, not a clean
   tree"* against `numpy 2.5.1`'s PEP-695 stub. `tools/ci_parity.sh`'s leg-4 header already
   documents this expected local exit 2. So the numpy-free venv is needed to obtain a **count**, not
   to unmask a lie. Any artifact describing the devcontainer as reporting false green is describing
   the pre-131 gate.

### Where the orphaned survivors land

- **D-01:** The D-10 honesty wording and the D-14 unknown-cmd mapping are **relocated into a shared production helper authored in this phase**, and the four honesty tests retarget onto *that*. Rejected: pre-staging them on Phase 135's `write --sdp-relock` path (ships production code no test can exercise end to end, and `ruff check` select `F` flags anything genuinely unused), and downgrading the four to a source-string-presence gate (converts four behavioral assertions into a scanning gate — the fail-open class this milestone exists to close). This gives the four tests a real SUT inside 132, with no coverage window, and makes the caveat a shared asset Phases 134 and 135 call rather than re-author.

- **D-02:** The helper is **`firestarter/sdp_honesty.py`**, added to `pyproject.toml`'s strict-island override list so the new carrier is type-checked from birth. Rejected: extending `firestarter/sdp_capability.py` (it is a fail-closed predicate whose narrowness is load-bearing for the 43/41/84 gate Phase 131 just built at `tests/test_sdp_db_invariant.py`, and mixing message text widens what that gate keys on), and placing it beside `sdp_lock`/`sdp_unlock` in `eprom_operations.py` (that module is deliberately outside the strict island per D-07's ring-fence, so a new honesty carrier there would be exempt from type checking — adding untyped code while discharging untyped debt).

- **D-03:** **`git mv tests/test_dev_sdp_cmd.py` → `tests/test_sdp_honesty.py`**, and `tools/check_no_exists_proxy.py:157` edited in the **same commit** (R-9: that gate exits 1 when any literal `_DEFAULT_TARGETS` entry is missing). Rejected research's `tests/test_dev_test_sdp_leg.py`: for two phases the filename would name a SUT that does not exist while its contents test a helper. `test_sdp_honesty.py` is accurate in 132 and stays accurate in 134/135, because the helper remains the carrier — one same-commit target-list edit, ever, instead of two.

- **D-04:** The gate-ordering cases whose gates die with the command (the TTY refusal at `:2277-2281`, `-y`, the `Confirm.ask` prompt at `:2267`) are **pruned, but counted and named in the phase record**. RETIRE-03 protects four tests out of 558 lines; a ~550-line deletion inside a `git mv` is exactly the diff shape that hides a real loss. "No net loss" must therefore be a measured claim about the four honesty assertions *plus* an accounted loss elsewhere. Rejected: silent pruning, and retargeting the chip-resolution / capability-refusal cases onto `sdp_capability()` (already covered by `tests/test_sdp_db_invariant.py` and `tests/test_check_sdp_capability.py` — duplicate coverage dressed as preservation).

- **D-05:** **No honesty caveat is added to the `write` auto-unlock path.** The caveat exists to qualify a *claim*, and `write`'s auto-unlock makes no claim about lock state — so there is no dishonest claim to caveat. Adding output would change the production write path's user-visible behavior inside a retirement phase, with `.ambr` churn beyond the one `test_help_dev` line. Recorded for Phases 134/135, whose leg and relock **do** make claims. Honest residual to state plainly: between this phase and Phase 134, the caveat has no user-reachable carrier.

### How GREEN is proven

- **D-06:** **Iterate against a committed numpy-free CI-replica venv; certify with exactly one operator push + dispatch.** Measured constraint that drove this: the milestone branch `gsd/v1.30-sdp-surface-retirement` does **not exist on origin** (`git ls-remote --heads origin` → no match; local is 9 ahead of `origin/beta`), and `ci.yml`'s `push` trigger is `branches: [main]` only — so certification needs **two** privileged operator actions, a branch push *and* a `workflow_dispatch`. Dispatch-driven iteration would cost an operator turn per batch while chasing ~30 errors, and `gh workflow run` is blocked by Claude Code's auto-mode classifier independent of the project allowlist. Local-venv-only was rejected because ROADMAP criterion 4 ("the `ci` job passes end to end") would become unachievable as worded, and any artifact then saying "ci is GREEN" would be the v1.22 C-5 overclaim class. This also discharges Phase 131 D-11's promise that 132's own dispatch is the hardened-gate-in-CI proof.

- **D-07:** The venv recipe is a **separate committed script in `firestarter_app/tools/`**, deliberately **not** folded into `tools/ci_parity.sh`. That script's contract is *faithful CI mirror* (Phase 131 D-08: "exactly CI's path set, neither wider nor narrower") and a local venv substitute is not a CI step; folding it in would also rewrite a script shipped 9 commits ago whose leg-4 header documents the local exit 2 as correct behaviour. Committed rather than prose because Phases 133–136 hit the same wall, and Phase 131 D-07's own reasoning is that a doc-only recipe is what every later phase silently skips.

- **D-08:** The certifying run's evidence is **both summary lines plus Phase 131 D-12's metadata shape**: the gate's `mypy errors: N (watermark: M)` line, mypy's verbatim `Found N errors in M files (checked K source files)` line, run id + URL, `gh run view <id>` step statuses, resolved mypy version, Python version. **Read, never computed.** The `checked K` clause is load-bearing: Phase 131's F-07 found it **structurally absent** from an aborted run's log, so its presence is itself the proof the run completed — and it cannot be assumed.

### The watermark and the typed fixture

- **D-09:** **Certify GREEN at the existing watermark of 35 and record the run's true count; do not ratchet in this phase.** This matches RETIRE-06 and ROADMAP criterion 4 word for word, costs one operator turn, and carries zero divergence risk. Rejected: setting the watermark to the locally-measured count before the single dispatch (a ±1 local/CI divergence reddens the gate and costs a second turn to recover — and A-1 is this project's own record of local and CI disagreeing on exactly this number), and green-at-35-then-ratchet-plus-second-dispatch (two operator push/dispatch turns in one phase; Phase 131 spent a full turn on one). Honest cost to state: **+2 of silent headroom persists** in what Phase 131 D-04 called the milestone's central honesty artifact. The actual defence against new errors is D-10's typed fixture, not a tight watermark. The measured true count becomes a named input to a later phase's ratchet — the same "measure, don't set" split Phase 131 used.

- **D-10:** RETIRE-05's fixture is a **typed `make_app_context(...) -> AppContext` factory with explicit typed keyword parameters (no `**overrides: object`), plus a thin `app_context` fixture wrapping it**, both in `tests/conftest.py`. The factory does the type work; the fixture satisfies RETIRE-05's literal word and serves the common case. Per-test variation stays possible, which is *why* the surviving modules rolled their own. Measured, and wider than A-2 states: `make_app_context` is defined in **eight** test modules, in two shapes — five with `**overrides: object` (`test_dev_test_cmd.py:84`, `test_write_skip_sdp_unlock.py:55`, `test_write_skip_erase_0x0d.py:68`, `test_validate_family_cmd.py:28`, `test_dev_sdp_cmd.py:80`) which are the 30-error set, and three with an unannotated `**manager_overrides` (`test_cli_handlers.py:40`, `test_protocol_not_implemented.py:43`, `test_protocol_not_implemented_production_path.py:53`) which are untyped and contribute **zero** errors under `check_untyped_defs = false`. Only four of the five survive the deletion. Consolidating the three untyped copies is out of scope.

### The stale-anchor corrections

- **D-11:** Corrections name **`_setup_operation` / `_operation_context` first, with `:329` / `:405` alongside** as a reader convenience. Function names are the durable anchor; R-7's own table is the receipt that line numbers re-stale — v1.23's ~+98-line insertion staled 11 of its 12 anchors. Rejected: corrected numbers only (guaranteed to re-stale, and this milestone already holds the evidence), and function names with the numbers dropped (the two derefs are 76 lines apart in a 1700-line module; the numbers earn their place).

- **D-12:** **RETIRE-08's count is corrected in-phase**, in the same commit as the fixes, with the measured evidence clause (five references, two files, enumerated in correction 2 above). Fixing five satisfies "three" a fortiori, but RETIRE-08 is this phase's own requirement — ticking it while knowing its text is wrong is the shape that closes as "three corrected" with two left behind. Rejected: deferring the text to Phase 137's CLOSE-01, which would leave a wrong number in `REQUIREMENTS.md` for five phases.

### Claude's Discretion

Two smaller areas the operator delegated. Both are grounded in measured research, and each records why.

- **D-13:** The `.ambr` update is **scoped to the `test_help_dev` node id**, followed by a review of `git diff tests/__snapshots__/test_characterization.ambr` against a **named expected shape** — "the only change is the removal of line 141's `sdp` line from `test_help_dev`" — with `git diff --stat` recorded. Never a broad `--snapshot-update`, which regenerates every snapshot in the selection and would silently bless drift in `test_help`, `test_info_known_chip` or `test_list`. **Narrowing worth stating: P-15's second failure mode does not fire in this phase.** syrupy 5.5.3 fails the whole session on *unused* snapshots and `addopts` is `-ra -q` with no `--snapshot-warn-unused` — but deleting line 141 leaves the `test_help_dev` entry still used. The unused-snapshot trap arrives when the entry is renamed or parametrised, which is **Phase 136's** channel split. A 132 plan that engineers around it is engineering around the wrong phase's hazard.

- **D-14:** The P-21 tripwire goes at the **decision** site, not the audit site. R-7 measured that the record's `eprom_operations.py:1637` is a comment inside the D-15/HOST-06 block with live statements at `:1653`/`:1654`, and is the **audit** site — mis-attributed. The host's auto-unlock decision lives in `cli_handlers.py`: the `skip_sdp_unlock: bool = False` defaults (`:302`, `:579`) and the D-04 auto-set / flag-independence block (`:626-640`, measured this session). The comment lands there and at `FLAG_SKIP_SDP_UNLOCK`'s definition (`constants.py:121`, verified). The named test — whose name and docstring *are* the record — extends the existing `tests/test_write_skip_sdp_unlock.py`, which already covers `--skip-sdp-unlock` and is itself one of the four surviving 30-error modules, so the phase is already open in that file. **Criterion, not coordinates:** a developer changing the auto-unlock default must read the tripwire by construction. Re-measure every anchor at plan time (R-7's discipline).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

`ROADMAP.md` carries no `Canonical refs:` line for this phase; this list is accumulated from the
ROADMAP entry body, `REQUIREMENTS.md`, the research spine, and this session's codebase scout.

### Milestone contract (read first)
- `.planning/REQUIREMENTS.md` §"Retire `dev sdp`…(RETIRE)" (lines 126–140) — RETIRE-01…RETIRE-08
  verbatim, plus the **Evidence Ceiling** at the top of the file, which must not be smoothed over in
  any artifact. **⚠ RETIRE-08's "three" is corrected by D-12 — five, measured.**
- `.planning/REQUIREMENTS.md` §Out-of-Scope, the `eprom_operations.py` D-07 ring-fence row
  (line 280) — the **operator decision of 2026-08-03** that closes research's operator-decision #2.
  → `FUT-MYPY-02`. Do not reopen.
- `.planning/ROADMAP.md` §"Phase 132: Retire `dev sdp` & Discharge the mypy Debt" — the goal, the 5
  success criteria, and the cross-cutting rule to **name the exact requirement IDs each plan may
  mark Complete, at dispatch** (executors did this prematurely 4× in Phase 116).
- `.planning/ROADMAP.md` §"v1.30 — SDP Surface Retirement…" (line 151) — the dependency spine, the
  serial-execution resolution, and the two narrowings that must survive into every phase's
  artifacts.

### The immediate predecessor (its outputs are this phase's inputs)
- `.planning/phases/131-gate-hardening-ci-parity/131-CI-BASELINE.md` — the fork-base count **69**
  (watermark 35), read verbatim from CI run `30822281624` (`workflow_dispatch` on `beta` @
  `16a313a`, mypy 2.3.0, Python 3.11.15). States explicitly that it is **an input to Phase 132's
  watermark, not a Phase 131 claim**. **⚠ F-07:** the verbatim `Found N errors in M files (checked K
  source files)` line is structurally **absent** from that log — the run aborted. D-08 requires its
  presence in *this* phase's certifying run as the completion proof.
- `.planning/phases/131-gate-hardening-ci-parity/131-CONTEXT.md` — D-01…D-18. Load-bearing here:
  **D-04** (why there is no canary and why the watermark's meaning must not be corrupted), **D-05**
  (`MIN_CHECKED_SOURCE_FILES = 120`, and its note that a `git mv` holds the count at 120 —
  **verify**), **D-11/D-12** (dispatch discipline, evidence shape), **D-17** (the research-record
  correction — do **not** go hunting in `firestarter_app` for
  `test_present_root_with_missing_target_raises_not_skips`; it is in the firmware repo, out of
  scope).
- `.planning/phases/131-gate-hardening-ci-parity/131-RECORD.md` §4a and §6a — the CI-dispatch
  mechanics: `gh workflow run` needs an operator turn; read-only `gh run view`/`gh run list` work;
  export `XDG_CACHE_HOME` to a writable path first or `--log` returns silently empty.
- `.planning/phases/131-gate-hardening-ci-parity/131-CI-PARITY.md` and
  `firestarter_app/tools/ci_parity.sh` — the four-leg recipe this phase runs before and after the
  deletion, and the leg-4 header explaining the expected local exit 2.

### The research spine (why this phase is research-SKIP)
- `.planning/research/SUMMARY.md` §"Phase 132" (line 704) — the delivery list.
  §**R-7** (line 154) — the authoritative corrected anchor table; **any anchor not in it must be
  re-measured, not trusted**. §**R-8** (line 183) — the mypy root cause (already fixed by 131).
  §**R-9** (line 219) — the `check_no_exists_proxy.py` same-commit trap and the four honesty
  assertions. §**A-1** (line 244) — why the devcontainer and CI disagree. §**A-2** (line 272) — the
  69-error arithmetic, the measured 63 → 39 → **33** path, and the confirmation that green at
  watermark 35 needs **no** ring-fence work.
- `.planning/research/PITFALLS.md` §**P-15** (line 570) — the two snapshot failure modes; **⚠ its
  second mode is Phase 136's, not this phase's — see D-13.** §**P-16** (line 597) — the four honesty
  assertions, with the exact docstring quotations and the four-grep acceptance criterion.
  §**P-17** (line 622) — the full trace table; traces 1–6 and 12 are this phase's, and trace 12's
  zero-`.md`-hits grep is a cheap acceptance leg. §**P-21** (line 740) — the tripwire's four layers;
  D-14 takes layers 1 and 2. §**P-14** (line 545) — which fail-open idioms to copy. §**P-18**
  (line 647) — the three defect classes this devcontainer cannot see; **⚠ its item 4 is corrected by
  Phase 131 D-17.**
- `.planning/research/STACK.md` §1 — the mypy mechanism end to end, including the numpy stub chain
  as a devcontainer-only artefact and **"do NOT switch the gate to `mypy --output json`"** (JSON mode
  emits no summary line, discarding the `checked K` signal D-08 depends on).

### Milestone design intent
- `.planning/notes/sdp-surface-retirement-and-behavioral-proof.md` — §2 (why `dev sdp` does not earn
  its place), §6 (**why deleting the command is safe** — the auto-unlock dependency D-14's tripwire
  records), §7 (insertion points; **⚠ its line numbers are superseded by R-7**), §9 (costs accepted
  knowingly, incl. the stranded gh#12 reply). Background, not a spec.

### Live code this phase edits, moves, or must not break
- `firestarter_app/firestarter/cli_handlers.py` — 2321 lines. `@dev.command(name="sdp")` **:2196**,
  `def dev_sdp` **:2213**, body to **:2321 = EOF**; span **2196–2321**, the last function in the
  file. Inside it: the capability refusal at `:2244`, the `Confirm.ask` prompt at `:2267`, the TTY
  refusal at `:2277-2281`, the **D-14 mapping at `:2295-2302`**, the **D-10 summary at
  `:2315-2319`**. The auto-unlock decision site is elsewhere: defaults at `:302`/`:579`, D-04
  auto-set block at `:626-640`.
- `firestarter_app/firestarter/constants.py` — `COMMAND_SDP_UNLOCK = 9` **:72**,
  `COMMAND_SDP_LOCK = 10` **:73**, their `COMMAND_NAMES` entries **:90-91**,
  `FLAG_SKIP_SDP_UNLOCK = 0x100` **:121**, and the stale-anchor comment **:69-70**. RETIRE-04's
  dereference test protects `:90-91`.
- `firestarter_app/firestarter/eprom_operations.py` — `_setup_operation` **:315** with
  `COMMAND_NAMES[cmd]` **:329**; `_operation_context` **:376** with the deref **:405**;
  `sdp_unlock` **:1736**; `sdp_lock` **:1784**. **Ring-fenced** — read and reference, do not
  type-fix.
- `firestarter_app/firestarter/sdp_capability.py` — `sdp_capability` **:266** (R-7's 2-of-3
  concurrence confirmed; STACK's 272 is wrong — `sdp_capability_for_entry` is at `:201`).
  Untouched by this phase.
- `firestarter_app/firestarter/serial_comm.py:424` — the INFO-band filter that makes a duration
  figure structurally impossible at the operation layer. The mechanical basis of the
  no-fabricated-duration assertion.
- `firestarter_app/tools/check_no_exists_proxy.py:157` — `"tests/test_dev_sdp_cmd.py"` in the
  literal, non-glob `_DEFAULT_TARGETS`. **Same-commit edit or the gate goes RED.**
- `firestarter_app/tests/test_dev_sdp_cmd.py` — 558 lines. The four protected tests:
  `test_summary_line_carries_the_unreadable_state_caveat_on_both_directions` **:395**,
  `test_summary_line_carries_no_duration_figure` **:423**,
  `test_no_fabricated_lock_state_boolean_in_the_report` **:453**,
  `test_firmware_too_old_is_reported_when_unknown_cmd_comes_back` **:513**. Local
  `make_app_context` at **:80**.
- `firestarter_app/tests/test_revision_constants_parity.py` — stale anchors at **:71-72**, **:527**,
  **:549** (inside an assertion *message*), **:585-586**.
- `firestarter_app/tests/__snapshots__/test_characterization.ambr:141` — the `sdp` line inside
  `test_help_dev` (`# name: test_help_dev`, **:124**).
- `firestarter_app/tests/conftest.py` — where D-10's factory + fixture land. Already provides
  `build_frame`, `_FakeSerial`, `make_comm`.
- `firestarter_app/pyproject.toml` — `[tool.mypy] python_version = "3.10"` and the watermark comment
  `# mypy_error_watermark = 35` at **:159** (read by regex from a *comment*, so a change is a
  one-token visible edit); the Phase 42 D-06 strict-island module list D-02 extends; the
  `follow_imports = "silent"` ring-fence block naming `firestarter.eprom_operations`.
- `firestarter_app/.github/workflows/ci.yml` — `push: branches: [main]` only (**:9-11**),
  `workflow_dispatch:` (**:25**), Python **3.11** (**:33-36**), the ruff path set (**:63-67**), the
  watermark gate step (**:69-70**).

### Pattern precedents to copy
- `firestarter_app/tools/ci_parity.sh` — the banner / per-leg-status / non-swallowing-aggregate-exit
  shape D-07's new script mirrors, and the `BOARD-ATTACHED:` stamping convention.
- `firestarter_app/tests/test_check_no_exists_proxy.py`, `test_check_sdp_capability.py`,
  `test_check_devtest_orchestrator.py`, `test_check_mypy_watermark.py` — the house `test_check_*`
  shape including the `*_fails_closed_on_missing_target` legs.
- `firestarter_app/tests/test_skip_census.py` — `ALLOWED_SKIP_REASONS` fails **closed** on any new
  skip reason. This phase should need **no** new skip reason; if a fix wants one, that is a signal to
  re-examine the fix, not to add an entry.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets
- **`tools/ci_parity.sh` (Phase 131, 9 commits old)** — four legs, aggregate exit, board stamping.
  D-07's venv script is its sibling, not its replacement. Run the recipe **before and after** the
  deletion per the ROADMAP's cross-cutting rule.
- **The hardened `tools/check_mypy_watermark.py`** — now split into a pure
  `classify_mypy_result(returncode, output) -> int` plus a thin runner, with
  `enforce_watermark(count, watermark)` separate. The pure functions are directly callable, so the
  venv script and any new test can use them without a subprocess.
- **`tests/conftest.py`** already carries `build_frame`, `_FakeSerial`, `make_comm` — the scripted-wire
  seam the milestone's "emission proof" is limited to (ROADMAP narrowing 1: the Phase 116 bus-trace
  harness is **unreachable from the host**).
- **`tests/test_write_skip_sdp_unlock.py`** already covers `--skip-sdp-unlock` and is one of the four
  surviving 30-error modules — so D-14's named test and D-10's fixture migration touch the same file
  the phase is already fixing.
- **`tests/fixtures/` is `extend-exclude`d from ruff** (`pyproject.toml`), which is what makes canned
  fixture content viable there.

### Established patterns
- **Explicit non-glob target lists** in every `tools/check_*.py` (never a tree-walk). This is exactly
  why `check_no_exists_proxy.py:157` must move in the same commit — the property that makes the gate
  honest is the property that makes it brittle to a `git mv`.
- **Import-time binding is pervasive and treacherous** — `FW_ROOT`, `FW_REPO_PRESENT`, `requires_fw`,
  `_BOARD_CHOICES` and `channel.is_prerelease_build()`'s effect on option construction are frozen at
  import/collection. `monkeypatch.setenv` runs **after** and has no effect. Anything simulating a
  different environment needs a **subprocess**.
- **`_HERE`-style path resolution is a live trap** — `check_permitted_claims.py`'s `_DEFAULT_TARGETS`
  resolving against the wrong phase dir scanned nothing and exited 0 on v1.23's only outward-facing
  gate. Any new default target list must resolve **locally** and be proven to.
- **`CliRunner` is wrong for help-text snapshots** — `CliRunner.isolation()` forces
  `click.formatting.FORCED_WIDTH = 80`, which wraps differently from a real subprocess's unforced 78.
  `tests/test_characterization.py`'s `_run_fw_help_at_version` (~`:242-286`) already solves this;
  copy it rather than reinventing.

### Integration points
- `ci.yml`'s `ci` job is the only consumer of the watermark gate. It is **RED at the fork base by
  design** — Phase 131 hardened the mechanism and fixed zero of the 69. This phase is the one that
  turns it green, and its dispatch is simultaneously the hardened-gate-in-CI proof Phase 131 D-11
  deferred here.
- `firestarter/sdp_honesty.py` (new, D-02) becomes a shared dependency of Phase 134's leg report rows
  and Phase 135's `write --sdp-relock`. Its API shape is therefore a **forward contract**, not an
  internal detail — name it for what it carries, not for `dev sdp`.
- `MIN_CHECKED_SOURCE_FILES = 120` (Phase 131 D-05) — a `git mv` holds the count, but this phase also
  **adds** `firestarter/sdp_honesty.py` and `tests/test_sdp_honesty.py` while removing nothing net,
  so the floor rises rather than falls. **Verify, do not assume**; D-05's comment says the floor is
  lowered only in the same commit as a legitimate deletion, with the new measured number.

### Measured live this session (re-verify at plan time; do not inherit)
- `firestarter_app` is on **`gsd/v1.30-sdp-surface-retirement`** @ `8caf77f`, **9 commits ahead of
  `origin/beta`**, and the branch **does not exist on origin**.
- `python3 tools/check_mypy_watermark.py` → *"ERROR: mypy exited 2 … Treating as a tool/config
  failure, not a clean tree"* against `numpy 2.5.1`. The gate is honest here; it is simply unable to
  produce a count.
- `grep -rn "cannot be read back" --include=*.py firestarter/` → **three hits, all in
  `cli_handlers.py`'s `dev_sdp` span**. `"not a claim about"` → one hit, `:2318`. `"was emitted"` →
  one hit, `:2316`.
- `make_app_context` is defined in **eight** test modules (five typed `**overrides: object`, three
  untyped `**manager_overrides`).
- `grep -rn "dev sdp" --include=*.md firestarter_app/` — P-17 trace 12 claims zero hits. **Re-run as
  an acceptance leg**, do not inherit.

</code_context>

<specifics>
## Specific Ideas

- **The phase's durable value, stated for the record:** this is the phase that makes
  `firestarter_app`'s primary `ci` job green for the first time in two months. A-1 established the
  gate was red on PRs and manual dispatch and **invisible otherwise** (`push` is `main`-only), which
  is why it went unnoticed. Green here is not cosmetic — it is what makes every later phase's "green
  suite" claim checkable at all.
- **Ordering comes from P-13 and is non-negotiable:** harden (Phase 131, done) → delete (−6, free) →
  typed fixture → the ~24 remaining fixes of the single mock-typing pattern → the six
  `[var-annotated]` annotations (`database.py:174,175,325`, `ic_layout.py`) → measure in a
  CI-equivalent env → certify. The fixture comes **before** the bulk fixes, not after, because it is
  what the fixes migrate onto.
- **The four honesty assertions are the phase's real deliverable, not the deletion.** The deletion is
  ~126 lines and a snapshot line. What can actually be lost here is four assertions that exist
  nowhere else in the tree, and the production wording they assert against. Plan the phase around
  protecting those, not around the `git rm`.
- **Say the split out loud in the phase record:** this phase proves the command is *gone* and the
  gate is *green*. It proves nothing about SDP behaviour on silicon — `0x0D` stays `UNVERIFIED`, no
  AT28C part has ever been in operator inventory, and the causal claim "the lock inhibited the write"
  is reachable only from a community `dev test` report that by design does not gate this milestone's
  close.

</specifics>

<deferred>
## Deferred Ideas

- **Ratchet the watermark to the measured true count** — D-09 records the number but does not set it.
  Needs a named owner or it becomes a seventh consecutive acknowledgement. **File as its own backlog
  item**, alongside 999.26 (`requires-python` / py3.9 floor) and 999.27 (the mypy-target treadmill)
  that Phase 131 filed for the same reason.
- **The `eprom_operations.py` `[union-attr]` ring-fence** — 10 errors, one root cause, one fix,
  outside the strict island since the v1.8-era GATE-1.8d read-path ring-fence. Already dispositioned
  by operator decision → **`FUT-MYPY-02`**. Recorded here only so a later reader does not re-open it
  as an unhandled carry.
- **Consolidating the three untyped `make_app_context` copies** (`test_cli_handlers.py:40`,
  `test_protocol_not_implemented.py:43`, `test_protocol_not_implemented_production_path.py:53`) onto
  D-10's factory — they contribute zero mypy errors today, so this is tidiness, not debt. Cheap for
  whichever later phase opens those files.
- **The honesty caveat on the `write` auto-unlock path** (D-05) — out of scope here; Phases 134/135
  own the surfaces that make claims. State the interim gap honestly rather than closing it early.
- **The `.ambr` `test_help_dev` channel-split parametrisation** and syrupy's unused-snapshot session
  failure — **Phase 136's**, per D-13. Do not pre-solve it here.
- **`gh#20`** (AT28C256 `dev test` FAIL, open since 2026-07-30) — the live instance of the "lock a
  part whose baseline write never worked" hazard. Triage before or with Phase 134's leg.
- **Traces 7–11 of P-17** (the gh#12 reply, the b14 release notes, the `.planning/` record sweep, the
  stale `--sdp-relock` deferral label) — Phase 137's CLOSE-05/06, behind a blocking operator
  wording-review gate.

### Reviewed todos (not folded)

`todo.match-phase 132` returned **13 pending, 10 matches; none folded.** Nine are keyword noise
against a host-only retirement-and-typing phase — six are firmware-area or firmware-subject items
(`skip-vpp-error-and-warning-checks…`, `prove-pio-dev-flag-fails-closed`,
`avrdude-mcu-detection-fallback`, `cobs-decoder-framelevel-deadline-wr01`,
`fold-response-code-into-log-macro`), plus three bench/hardware items
(`photograph-modified-rev-0`, `write-modifications-md-rework-trace`,
`fix-jp4-labels-and-rev2-revision-block`), matching on generic tokens like "check", "gate", "dev",
"tools", "phase".

The one substantive hit is **`gh12-followup-after-dev-sdp-retirement`** — owned by **Phase 137**
(CLOSE-05/06) by requirement, behind a blocking operator wording-review gate. Not foldable here: it
describes a substitution that must already be true, and it is an outward-facing publication this
phase has no mandate to make. `decode-infoic-flags-bits-14-15-protect-metadata` is adjacent to the
`flags` bit-15 decode Phase 131's 43/41/84 gate keys on, but concerns bits **14/15** in
`build_db.py`'s emitter — a database-pipeline change, not a host-surface one.

</deferred>

---

*Phase: 132-Retire `dev sdp` & Discharge the mypy Debt*
*Context gathered: 2026-08-03*
