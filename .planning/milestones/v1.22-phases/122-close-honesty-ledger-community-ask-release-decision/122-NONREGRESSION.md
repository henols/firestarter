# Phase 122 Non-Regression Sweep — CLOSE-01, merged tree

**Written:** 2026-07-30 (Plan 122-04)
**Firmware phase base:** `0048b3d` · **Host phase base:** `96e0622` (the two meta-repo gitlink pointers, unchanged by this plan — D-07)
**Firmware HEAD at this sweep:** `953f74842ee0bcc89923a306d5bd79ef3ad19f92` (merge commit, parents `48c36e5` + `6611fba`)
**Host HEAD at this sweep:** `4001396bbd42d5ba36ce24f40e0315ee6de32d60` (merge commit, parents `c3c9424` + `1bb5599`)
**Post-merge version strings:** `firestarter_app/firestarter/__init__.py` → `3.0.0b13`; `firestarter/include/version.h` → `3.0.0b13`

This is the load-bearing gate result CONTEXT constraint 6 requires: every row below was
**re-executed in this session, against the tree produced by 122-03's inbound merge** — the tree that
will actually be pushed in wave 6, not an earlier commit. Nothing here is copied from a prior plan's
SUMMARY; where a prior artifact (`122-RESEARCH.md`, `122-VALIDATION.md`, `121-NONREGRESSION.md`) made
a claim, this document re-checks it against the live tree and says so, including one case where the
live tree disagrees with a stated pre-merge baseline (§4).

---

## 1. The claim, as precise statements

1. **`0x0D` is still `UNVERIFIED` in `PROTOCOL-LEDGER.md`, and the ledger was read, never written.**
   Checkable against §2 row 1 and the empty `git status --porcelain -- .planning/v1.16/ledger/`.
2. **Zero chips changed `support_status`, and the 84-chip `algorithm == 13` count is unchanged** —
   proven twice, independently: the DB-identity exit code (§2 row 3) and a from-scratch measurement
   over the raw JSON (§2 "Independent measurement"), not merely the test's own assertion.
3. **The eleven cross-repo non-regression commands are green on the merged tree**, including rows
   9a/9b which scan `firestarter/submit.py` and `cli_handlers.py` — the very file the merge
   conflicted (§3).
4. **`check_ledger.py` was never run as a CLOSE-01 gate.** Its pre-existing RED is recorded in §6
   with its v1.19 Phase 104 cause; it is excluded by explicit plan mandate (C-4), not by omission.

---

## 2. CLOSE-01's four mechanisms, on the merged tree

| # | Mechanism | Command | Expected | Observed |
|---|-----------|---------|----------|----------|
| 1 | `0x0D` still `UNVERIFIED` | `grep -c '^\| \`0x0D\` .*\*\*UNVERIFIED\*\*' .planning/v1.16/ledger/PROTOCOL-LEDGER.md` | 1 | **1** — line 27, `\| \`0x0D\` \| EEPROM-POLL \| ... \| **UNVERIFIED** \| No on-hand silicon. Rep chip: AT28C256 ...` |
| 2 | 84-count + `chip_id_check` invariant | `cd firestarter_app && python3 -m pytest tests/test_sdp_db_invariant.py -q` | 4 passed | **4 passed** |
| 3 | DB identity | `cd firestarter_app && python3 tools/diff_db.py` | exit 0 | **exit 0** — `PASS: all 2 changed chips explained (0 new chips confirmed; 0 chips removed from baseline)`. Identity here means still exactly 2 explained `PGSZ_PAGE_SIZE` changes, not zero diff (GATE-03's recorded reading, C-13) |
| 4 | No code path writes `support_status` | `cd firestarter_app && python3 tools/check_no_community_support_status_write.py` | exit 0 | **exit 0** — `PASS: scanned ../firestarter/diagnostic_report.py, parse_devtest_issue.py; 0 support_status writes (sole write locus stays tools/build_db.py)` |

`git -C /workspaces status --porcelain -- .planning/v1.16/ledger/` → **empty** both before and after row 1 — the ledger pair was read, never written.

**Independent second measurement path** (a non-test route to the same facts, loading
`firestarter/data/chip_database.json` directly and computing from scratch — never trusting the
test's own assertion):

```
total chips in chip_database.json : 746
algorithm == 13                   :  84
chip_id_check among those 84      : {False}
support_status among those 84     : supported 75, adapter-required 9
pinout among those 84             : DIP28_28C64 35, DIP24_2816 19, DIP32_28C512_EEPROM 18, DIP28_28C256 12
```

Every figure reproduces `122-RESEARCH.md`'s recorded live measurement exactly.

**Per-pinout SDP ALLOW/REFUSE split** — measured by invoking
`sdp_capability.sdp_capability_for_entry` over each of the 84 `algorithm == 13` entries, built in
the `db.get_eprom()` shape (`protocol-id: 13`, `name` = `part_number`) as the predicate's hard-fail
guard requires:

| Pinout | Chips | SDP ALLOW | SDP REFUSE |
|--------|------:|----------:|-----------:|
| `DIP28_28C64` | 35 | 15 | 20 |
| `DIP24_2816` | 19 | **0** | **19** |
| `DIP32_28C512_EEPROM` | 18 | 18 | 0 |
| `DIP28_28C256` | 12 | 10 | 2 |
| **Total** | **84** | **43** | **41** |

This reproduces STATE.md's derived partition exactly.

> **Named finding:** *emission-traced byte-exact for a pinout* and *the operation permitted on parts
> with that pinout* are **different claims**. For `DIP24_2816` the first is true (all four `0x0D`
> pinouts are byte-exact golden-traced) and the second is false for all 19 chips on that pinout (0
> ALLOW). Every downstream artifact that says "all four `0x0D` pinouts" must carry this distinction,
> or it reads as broader capability than shipped.

**`check_ledger.py` was NOT run.** It is pre-existing RED (v1.19 Phase 104 renamed
`flash_type_3`/`flash_type_4` → `flash_nor_unlock`/`flash_5v_page`; the v1.16 ledger's
`matrix_family` join keys for rows `0x05`/`0x06` never followed, and `tools/validation_matrix_spec.json`
is not in the `beta...HEAD` diff — not v1.22's damage). Fixing it would edit a closed milestone's
artifact (D-09). The `0x0D` row's own join key (`eeprom28c`, `protocols: [13]`, `rep_chip: AT28C256`)
is present and valid — only `0x05`/`0x06` are stale. See §6 for the full record.

---

## 3. The eleven-row cross-repo gate table

Run from `/workspaces/firestarter_app` against the merged tree, in order. Every command re-executed
in this session; none accepted from a prior plan's SUMMARY.

| # | Command | Result |
|---|---------|--------|
| 1 | `python3 tools/check_no_log_in_sdp_window.py` | **PASS** — resolved `../../firestarter/src/proms/eeprom_28c.cpp`, emitter lines 298-314, poll lines 348-361 |
| 2 | `pytest tests/test_check_no_log_in_sdp_window.py -q` | **PASS** (7 of the 18-test combined run, §below) |
| 3 | `pytest tests/test_sdp_table_parity.py -q` | **PASS** (5 of 18) |
| 4a | `python3 tools/check_is_memory_cmd_no_ifdef.py` | **PASS** — resolved `../../firestarter/include/firestarter.h`, predicate body lines 109-123, exactly 8 commands |
| 4b | `pytest tests/test_check_is_memory_cmd_no_ifdef.py -q` | **PASS** (6 of 18) |
| 5 | `python3 tools/gen_sdp_bus_config.py` | **PASS** — `OK: wrote /workspaces/firestarter/test/native/avr/_shared/sdp_bus_config.h`; idempotence assertion below |
| 6 | `pytest tests/test_sdp_bus_config_drift.py -q` | **PASS** (4 of a 19-test combined run, §below) |
| 7 | `pytest tests/test_revision_constants_parity.py -q` | **PASS** (13 of 19) |
| 8 | `pytest tests/test_dispatch_mirror.py -q` | **PASS** (2 of 19) |
| 9a | `python3 tools/check_dispatch.py` | **PASS** — `all 746 chips scanned; 736 supported; 10 chips confirmed non-dispatchable; 0 non_supported_dispatchable; 0 dispatch regressions; 0 consistency violations` |
| 9b | `python3 tools/check_devtest_orchestrator.py` | **PASS** — `scanned ../firestarter/chip_test.py, ../firestarter/cli_handlers.py, ../firestarter/submit.py; 0 VPP-set, 0 raw-wire-dict, 0 --force; firmware untouched (host-only, asserted)` |

Rows 1-4 combined (`pytest tests/test_check_no_log_in_sdp_window.py tests/test_sdp_table_parity.py
tests/test_check_is_memory_cmd_no_ifdef.py -v`): **18 passed in 0.49s**.
Rows 6-8 combined (`pytest tests/test_sdp_bus_config_drift.py tests/test_revision_constants_parity.py
tests/test_dispatch_mirror.py -v`): **19 passed in 0.16s**.

**Row 5's idempotence assertion.** Pre-generator `git -C /workspaces/firestarter status --porcelain`
→ `?? firestarter/` (the named pre-existing dirt — an untracked nested directory, unrelated to the
generator). After running `gen_sdp_bus_config.py`, the same command returns the identical
`?? firestarter/` string — not empty, but unchanged from baseline. The generator wrote no new diff.

**Row 9b's named file list.** `PASS: scanned ../firestarter/chip_test.py, ../firestarter/cli_handlers.py,
../firestarter/submit.py; ...` — `submit.py` is named explicitly, and this list is unchanged from
`121-NONREGRESSION.md`'s own record (`scanned chip_test.py, cli_handlers.py, submit.py`). This is the
row at real risk (Pitfall 5): `submit.py` is one of the two files the inbound merge conflicted, and
the whole-file `--ours` resolution (122-03) is re-proved against this gate rather than trusted from
that plan's own SUMMARY. It passes non-vacuously — `0 VPP-set, 0 raw-wire-dict, 0 --force` — exactly
as before the merge.

**All eleven rows PASS.** No row was accepted on the strength of an earlier plan's claim alone.

---

## 4. Full-suite results

| Suite | Command | Baseline | Observed |
|---|---|---|---|
| App pytest | `cd firestarter_app && python3 -m pytest -v` | 1150 passed (stated in `122-RESEARCH.md`/`122-VALIDATION.md`/this plan's own text) | **1134 passed**, 29 snapshots passed, in 52.12s — **see delta note below** |
| Firmware native | `cd firestarter && pio test -e native` | 141/141 succeeded, 17 suites | **141/141 succeeded**, 17 suites, 19.9s — matches exactly |
| Firmware script tests | `cd firestarter && python3 -m pytest tests/ -v` | 8 passed | **8 passed** in 0.03s — matches exactly |

**Delta note on the app pytest count (1134 observed vs 1150 stated baseline) — investigated, not
rounded or paraphrased.** `git -C firestarter_app log --oneline` shows the app repo's branch HEAD
immediately before the merge (`c3c9424`) is the **same commit** as Phase 121's own final commit —
zero 122-01/122-02 commits touched `firestarter_app` before 122-03's merge (both of those plans'
artifacts are meta-repo-only: `check_permitted_claims.py`, its test, and its four fixtures live at
`.planning/phases/122-.../`, not inside the `firestarter_app` submodule). `121-NONREGRESSION.md`'s
own final sweep — an independently-committed, already-verified prior figure — recorded **1134
passed** at that exact commit. Since the true pre-merge branch HEAD is `c3c9424` and its test count
is independently on record as 1134, the actually-correct pre-merge baseline is **1134, not 1150**;
this sweep's observed 1134 on the merged tree therefore shows **zero regression** from the real
pre-merge state — the merge added no net test-count change to the app suite. The "1150" figure
appearing in `122-RESEARCH.md`, `122-VALIDATION.md`, and this plan's own text is not reproducible
against the git history and is recorded here as a documentation inconsistency in those artifacts,
not a defect in the merged tree. (A dry-run investigation confirmed the mechanism that could explain
a *different* number: five `origin/beta`-side "quick-260728-ahy" hotfix commits each touched both
`firestarter/submit.py` and `tests/test_submit.py`, adding roughly 10 new test functions on the
`beta` side — but the merge's mandated whole-file `--ours` resolution (C-12) keeps the `v1.22`
branch's own version of both files intact and discards none of the branch's own tests; `origin/beta`'s
own `test_submit.py` in isolation carries only 60 `def test_` matches against the branch's 77, so
`--ours` is not a test-count reduction relative to beta either — the two versions are simply
divergent content from Phase 121's rework, not a superset/subset pair.)

---

## 5. Both beta workflows' local gate sets, pre-validated

**`firestarter/beta-build.yml`'s set** (all run from `/workspaces/firestarter`):

| Gate | Command | Result |
|---|---|---|
| Catalog validity | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` | `OK: catalog valid (73 messages, version 1)` |
| Codegen drift (`include/messages.h`) | regenerate, then `git diff --exit-code include/messages.h` | **NO DRIFT** (exit 0) |
| `pio test -e native` | — | **141/141 succeeded** (§4) |
| `pytest tests/ -v` | — | **8 passed** (§4) |
| `pio run` (uno, uno328pb, leonardo) | — | **3/3 SUCCESS** — flash/RAM figures below |

Three flash/RAM figures, all matching the recorded Phase 121 baseline exactly:

| Env | Flash | RAM |
|---|---|---|
| Leonardo | 26072/28672 (90.9%) | 2014/2560 (78.7%) |
| Uno | 23932/32256 (74.2%) | 1573/2048 (76.8%) |
| uno328pb | 23976/32384 (74.0%) | 1579/2048 (77.1%) |

**`firestarter_app/beta-release.yml`'s set** (all run from `/workspaces/firestarter_app`):

| Gate | Command | Result |
|---|---|---|
| `pip install -e .[test]` | not re-run — already satisfied in this devcontainer (RESEARCH's Package Legitimacy Audit records zero installs in phase scope) | N/A by design |
| Catalog validity | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` | `OK: catalog valid (73 messages, version 1)` |
| Codegen drift (`firestarter/messages.py`) | regenerate → `ruff format` → `ruff check --add-noqa` → `git diff --exit-code firestarter/messages.py` | **NO DRIFT** (exit 0; `1 file left unchanged`) |
| `pytest tests/ -v` | — | **1134 passed** (§4, with the delta note recorded there) |

**What these two workflows do NOT run**, so their green tick is not over-read: no ruff, no mypy, no
coverage floor, no vector-catalog gate, no CLI smoke test on either workflow — those live only in
`ci.yml` (main/PR), which **never triggers on a `beta` push** (C-8). Recorded anyway, out of an
abundance of honesty, not as a gate requirement:

| Check | Result | Note |
|---|---|---|
| `ruff check .` (0.16.0, CI-resolved version) | **4 errors, 3 files** — `tools/audit_coverage_matrix.py`, `tools/catalog/codegen.py`, `tools/catalog/codegen_vectors.py` | Pre-existing; `git diff --stat 96e0622..HEAD` on these 4 files (+`.github/scripts/update_version.py`) is **empty** — none touched by v1.22 |
| `ruff format --check .` (0.16.0) | **4 files would be reformatted** — same 3 plus `tools/check_mypy_watermark.py` | Same empty-diff proof; pre-existing |
| mypy watermark | `mypy errors: 1 (watermark: 35)` | 34 below; unchanged |

**Also recorded as by-design, never chased:** `catalog-sync-check.yml` remains **red until the
`main` merge** — it checks out both sub-repos at `ref: main` (lines 33/40 of the workflow), and
v1.22 has not merged to `main` in either repo; that merge is `/gsd-complete-milestone`'s job. The
in-phase proof is the three-way catalog `cmp` (below) plus `codegen --check`, both clean on the
merged trees. Same by-design-red applies to firmware `build.yml`'s `pio test -e native_nodevtools`
step, which also first executes for real at that same `main` merge.

**Three-way catalog identity, re-confirmed on the merged trees:**

```
$ diff /workspaces/tools/catalog/messages.toml /workspaces/firestarter/tools/catalog/messages.toml
(empty) → MATCH firmware
$ diff /workspaces/tools/catalog/messages.toml /workspaces/firestarter_app/tools/catalog/messages.toml
(empty) → MATCH app
```

**Both sub-repo trees still show only the named pre-existing dirt after every gate above ran:**

```
$ git -C /workspaces/firestarter_app status --porcelain
 M .gitignore
?? .coverage
?? .planning/config.json
?? SECURITY.md
?? write_test_port.sh

$ git -C /workspaces/firestarter status --porcelain
?? firestarter/
```

No gate run changed any tracked file in either sub-repo.

---

## 6. Known-and-explained conditions — never silent

1. **`check_ledger.py` is pre-existing RED, never run as a CLOSE-01 gate (C-4).** Cause: v1.19 Phase
   104 renamed `flash_type_3`/`flash_type_4` → `flash_nor_unlock`/`flash_5v_page`; the v1.16 ledger's
   `matrix_family` join keys for rows `0x05`/`0x06` never followed, and `validation_matrix_spec.json`
   is not in the `beta...HEAD` diff — not this milestone's damage. Fixing it would edit a closed
   milestone's artifact (D-09); RESEARCH's Open Question 4 recommends a backlog seed instead. The
   `0x0D` row's own join key is present and valid — only `0x05`/`0x06` are stale.
2. **`catalog-sync-check.yml` red-until-`main`-merge, by design.** `ref: main` in both checkout steps;
   the in-phase proof is the three-way `cmp` + `codegen --check` (§5), both clean.
3. **Firmware `build.yml`'s `pio test -e native_nodevtools` step** first executes for real at that
   same `main` merge — same cause, same non-chase.
4. **Four pre-existing `ruff check` findings and four `ruff format` drift files**, all in `tools/` +
   `.github/scripts/`, structurally outside `ci.yml`'s `firestarter/ tests/` scope and confirmed
   untouched by v1.22's own diff (§5).
5. **mypy watermark at 1 error against a 35 watermark** — 34 below, unchanged from Phase 121.
6. **The app pytest delta (§4)** — 1134 observed vs a stated-but-unreproducible 1150 baseline in
   `122-RESEARCH.md`/`122-VALIDATION.md`; recorded as a documentation inconsistency in those
   artifacts, not a regression in the merged tree.
7. **Named pre-existing working-tree dirt in all three repos** (§5's final block; meta repo:
   ` M .planning/config.json`, ` M firestarter`, ` M firestarter_app` — the last two are the expected
   unstaged submodule-pointer drift D-07/A5 documents, not a staged gitlink change).

---

## 7. Validation-ceiling statement

**Permitted claim, quoted verbatim (`.planning/REQUIREMENTS.md`):** *"The SDP lock and unlock
sequences are emitted exactly as specified, verified byte-exact by golden register trace across all
four `0x0D` pinouts, with a documented and measured host-side timing assumption."*

**Forbidden claim — cited by location, not reproduced verbatim (`.planning/REQUIREMENTS.md:152`):**
the forbidden sentence asserts unqualified operational success, naming the ledger's representative
`0x0D` part, with no software-artifact qualifier at all. **Deliberate note on why this document does
not reproduce that sentence's exact wording:** doing so would itself trip §7's own claim-scanner
below — the scanner matches the phrase's shape regardless of quotation context, by design, per its
own module docstring's "an honest negated phrasing... WILL trip the forbidden pattern" warning. That
is a demonstration of the gate working as intended, not a defect to route around by weakening the
pattern set; the permitted claim above is reproduced verbatim because it contains no trigger shape,
and REQUIREMENTS.md:152 remains the citable source of the forbidden sentence's literal text.

**Required silicon caveat, stated plainly: no AT28C silicon was tested during this plan.**

**Line-by-line confirmation that nothing in this document asserts the forbidden claim:** every
result above has a software artifact as its subject — a git blob identity, a `pio run` size report,
a pytest exit code, a source-read confirmation, a byte-for-byte `diff`/`cmp` — never a silicon
observation. No AT28C part was on the bench during this plan; the three attached devices were used
only for `pio run`'s build step (no upload, no serial I/O). Measured figures cited, never rounded:
**66 of 84** emission-traced — not the full 84-chip `0x0D` bucket; the honest Phase 116
trace-coverage figure — **43 ALLOW / 41 REFUSE** (§2), **301/301** UV via `electrical-type`
(Phase 121's structural axis, superseding the old `algorithm == 0x0B` proxy's 32/301). The flash
budget (LOCK-06, **2600 B free** on the Leonardo) and the timing budget (F-118-01, **572 µs** vs the
**600 µs** `AT28C_TBLC_MAX_US` datasheet maximum) are kept as **two separate statements** here, never
combined into one figure — `119-MEASUREMENT.md` records the correction that PROJECT.md once
conflated them.

**A green claim-scan does not satisfy ROADMAP criterion 4, stated plainly.** Criterion 4 is closed by
this gate **plus** the D-16 blocking operator wording review (plan 122-11), not by this document
alone. One whole claim class — silicon-level confirmation of the SDP sequence on a real `0x0D` part —
has a sampling rate of **zero, permanently, by design**, because no AT28C part has ever been on the
bench for this milestone.

**Courtesy claim-scan run over this artifact itself**, as an early smoke test of both the gate and
the prose (this file is not one of the scanner's five default outward-facing targets, so this is a
courtesy check, not a contract):

```
$ FIRESTARTER_CLAIMSCAN_TARGETS=/workspaces/.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-NONREGRESSION.md \
  python3 /workspaces/.planning/phases/122-close-honesty-ledger-community-ask-release-decision/check_permitted_claims.py
```

---

## 8. Deliberately not taken

- **No `PROTOCOL-LEDGER.{md,json}` edit.** D-09 makes it read-only for the whole phase; CLOSE-01 asks
  that `0x0D` *stays* `UNVERIFIED`, which is a check, not a write.
- **No `check_ledger.py` fix.** Would edit a closed milestone's artifact for a defect this milestone
  did not cause (§6.1).
- **No ruff finding fixed, no generated file hand-edited, no formatter run with a write flag** beyond
  the two mandated codegen-drift regenerations (`messages.h`, `messages.py`), both of which produced
  zero diff and were not committed as new content (the regenerated bytes are byte-identical to what
  is already on disk).
- **No gitlink bump.** D-07 assigns that to `/gsd-complete-milestone`; the meta gitlinks remain
  pinned at `0048b3d`/`96e0622` throughout this plan.
- **No push, no `gh release`, no tag.** Nothing in this plan leaves the machine.

---

## Sweep Summary

| Gate | Result |
|---|---|
| `0x0D` `UNVERIFIED` grep | count 1; ledger provably unmodified |
| `test_sdp_db_invariant.py` | 4 passed |
| `diff_db.py` | PASS, exit 0, identity = 2 explained/0 new/0 removed |
| `check_no_community_support_status_write.py` | PASS, exit 0 |
| Independent measurement | 746 / 84 / `{False}` / 75+9 / 35-19-18-12 — all reproduced |
| SDP ALLOW/REFUSE split | 43/41 total, `DIP24_2816` 0/19 — all reproduced |
| Eleven-row cross-repo gate | all 11 PASS; row 5 idempotent; row 9b file list unchanged |
| App pytest | 1134 passed (see §4 delta note — no regression vs the true pre-merge count) |
| Firmware native | 141/141, 17 suites |
| Firmware script tests | 8 passed |
| `pio run` (3 envs) | 3/3 SUCCESS, figures unchanged from Phase 121 |
| Both codegen drift gates | clean |
| Catalog three-way identity | clean |
| `check_ledger.py` | NOT run; RED recorded with cause (§6.1) |
| Both sub-repo trees | clean except named pre-existing dirt |

**CLOSE-01's entire verification surface is green on the tree that will actually be published.**
This plan ticks no requirement — CLOSE-01 closes only in plan 122-13, after `122-LEDGER.md` and the
PROJECT.md EIGHTH CORRECTION exist and after the phase's other requirements have landed.
