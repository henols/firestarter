# Phase 174: Blast-Radius Invariance Harness - Research

**Researched:** 2026-09-03
**Domain:** Test-only invariance harness (frozen-hash oracle) over `firestarter_app`'s `dedup_fingerprint` / `build_db_diff`
**Confidence:** HIGH on everything measured this session; **LOW on three inherited hashes that FAILED TO REPRODUCE** (see Measured Facts)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Sixteen decisions, D-01…D-16, are locked. Reproduced in full because every one of them constrains a task:

- **D-01:** A frozen shape is a **Python builder plus a committed `to_dict()` JSON snapshot** — the hash is taken off the object exactly as production does. **No deserializer is written.** There is no `from_dict` anywhere in the tree; `DiagnosticReport` is constructed at exactly one production site (`cli_handlers.py:2388`) and `dedup_fingerprint` takes the object, not a dict. A loader would be new machinery between fixture and hash that production never exercises — if it drifted, the oracle would lie while staying green. The committed JSON is an *output* snapshot, and is already Phase 181's RPT-E2/E3 parse oracle.
- **D-02:** Frozen shapes come from **two separate tables** — a hand-specified table pinning the hash *function* (immune to DB regeneration), and a smaller table from real `derive_plan` output for named chips (m27c512/full, the SST27SF512 six-step) pinning the shapes research measured. `chip_database.json` is GENERATED, so a generator fix reddens only the second table — a signal worth having. A hand-specified-only table could not catch re-key path #2.
- **D-03:** Builders live in a **new module under `firestarter_app/tests/fixtures/`**, beside the committed JSON — not inside `tests/test_diagnostic_report.py`, which carries 68 `dedup_fingerprint` call sites. **Reversibility: costly** — every later phase's imports and every ledger `shape_id` reference points at this path.
- **D-04:** Every frozen shape carries a **stable string `shape_id`** (e.g. `uv-slot-write-pass`, `sst27sf512-six-step`). Ledger, ladder table and JSON filenames all key off it. Positional indices rejected. **Reversibility: one-way once ledger rows exist.**
- **D-05:** The synthetic row set derives from **this milestone's own change list**: the four measured re-key paths, plus ATTR-01's status-axis shape and PRUNE-03's synthesized-fingerprint shape. Every row exists because a *named later phase* is measured against it.
- **D-06:** All **27** filed `[dev test]` issues committed as `(issue number, chip, embedded 12-hex)` rows. Builder shapes must **reproduce the filed hash** for **m27c512, sst27sf512, at28c256, w27e257**. Real dedup groups must survive: `00e121446ceb` spans gh#20/#21/#32 (at28c256, N=3), `334c3fa198bf` spans gh#39/#40 (at28c256, N=2). *(See Correction C1: the count is 26.)*
- **D-07:** The **sorted `to_dict()` key-list pin lands in this phase**, not 181. Phase 181's three deletions (`voltage.vpp_mv`, `voltage.vpe_mv`, `banner.locked_steps`) are then measured against a gate that predates them. A deliberate addition to the roadmap's five criteria.
- **D-08:** The ladder pin covers **all four `build_db_diff` disposition branches** — `BAD`, marginal-or-indeterminate, all-OK, fallback — each with its `(proposed_disposition, ladder_state)` pair. **It must include a non-SDP all-OK shape**, because AT28C256's SDP leg attaches fingerprints in every arm.
- **D-09:** **Append, never edit.** Rows are `(shape_id, before_hash, after_hash, ledger_id)`; `after_hash` is `None` until declared; assertion is `current == after_hash if declared else before_hash`. **Reversibility: costly** — consumed by seven later phases and the meta-side checker.
- **D-10:** The harness asserts the **complete `shape_id` set**, element-wise, against a committed sorted list. Deleting an inconvenient row, or adding one that quietly widens the oracle, is a RED.
- **D-11:** A declared re-key lands in **its own commit**, separate from the behaviour change. **This constrains Phases 175–181, not just 174** — each of those planners must carry it.
- **D-12:** The ledger is **pre-seeded in this phase** with all four measured re-keys: before-hashes filled, `after_hash` empty, each row naming its owning phase. Rows 2 and 3 are re-keys the milestone declines, seeded anyway because the ledger records the blast radius that *exists*.

  | # | Change | Owner | before → after |
  |---|---|---|---|
  | 1 | Gate the fingerprint read-back on failure | Phase 177 | `4dc282a5d596` → `60a031573aab` (SST27SF512 six-step) |
  | 2 | Prune unsupported SDP steps from `Plan.steps` | out of scope (rejected) | `a00791f1c2b4` → `7d1cd4157cfa` (m27c512/full) |
  | 3 | Canonical `part_number` naming | Phase 181, avoided by D-2 | `a00791f1c2b4` → `a6f6c6354047` |
  | 4 | UV blank-check abort → `run_count` collapse | Phase 179 | shape-level, via `repeat_policy_tag` |

  *(CONTEXT.md itself instructs these be re-measured at the actual branch base before freezing. See Corrections C2 and C3.)*
- **D-13:** The **app-side table is the authoritative machine-readable ledger**, checked by the app suite. A checker in the **meta repo** — which can see both trees — asserts every filled `after_hash` has a matching `MILESTONES.md` row. The direction that can see both files holds the check, so it cannot fail open.
- **D-14:** GATE-04's delta is a **whole-database aggregate over all 746 rows PLUS explicit per-chip rows for each of the 27 filed issues**. Both readings satisfied, not one chosen.
- **D-15:** The raw CLI token is resolved through **`chip_resolver.resolve_chip`** (`firestarter/chip_resolver.py:16`) and the returned `part_number` recorded. The lowercase-form proxy (732/746) may be reported alongside as the published number, but **it is not the measurement**.
- **D-16:** The delta artifact is **script-generated, committed, and drift-tested**. Per standing policy the script must be **owned by this repo**, not imported from elsewhere.

### Claude's Discretion

Decided without asking, on standing precedent — the planner treats these as locked:

- **Anti-vacuity is mandatory.** The frozen table gets a planted-mutation leg that must make it go RED. A gate authored before the content it guards can be unreachable and prove nothing; RED is not proven until it has been *seen*. Copy the discipline from `tests/test_erase_flag_invariants.py` and the closure idiom from `tests/test_chip_test_sdp_leg.py:827` (`test_shipped_ops_never_reach_sdp_arm`).
- **All measurement in the py3.11 CI-replica venv**, never the devcontainer's default 3.12. `uv venv --python 3.11`.
- **No new library.** HYG-02 is milestone-wide; stdlib + pytest only. `syrupy>=5.0,<7` bounding is Phase 181's.
- **Branch:** fork `gsd/v1.36-dev-test-fidelity` off `beta` **in the app submodule too**. *(Already done — see Correction C5.)*
- **Grep in this devcontainer is ugrep and honors `.gitignore`** — use `/usr/bin/grep` or a `bash` script for any gate evidence.

### Deferred Ideas (OUT OF SCOPE)

- **Reproducing all 27 filed hashes from builders** — scoped down to four (D-06). The `(issue, chip, hash)` artifact this phase commits is the input for any later extension.
- **A general report deserializer (`from_dict`)** — deliberately not built (D-01). If Phase 181's RPT-E2 needs one it is introduced there with its own drift gate, not smuggled in here.
- **Whether the 4.22 s whole-DB sweep runs on every push** against a 737 s suite, or is marked slow — a planner call. *(Measured input supplied below.)*
- **`--fast` / `repeat_policy_tag` shape interaction** with the pre-seeded UV `run_count` row — Phase 179 owns the UV shape.
- **The stray uncommitted `tools/build_db.py` rename** — not this phase's business. *(No longer present.)*

**Folded todos:** none. Three todos carry `resolves_phase` for 177/181/181 and are correctly homed there.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description (verbatim, REQUIREMENTS.md §Blast-Radius Oracle) | Research Support |
|---|---|---|
| **GATE-01** | A frozen `(report shape → 12-hex dedup_fingerprint)` table exists, computed against HEAD **before** any behaviour change lands, covering at minimum the four measured re-key shapes (read-back gating, SDP-step pruning, canonical naming, UV `run_count` collapse). | Branch base verified `49bac1a` ≡ `origin/beta`, tree clean. Canonical-string model validated against the one shipped literal. SST pair reproduced with pre-image; m27c512 shapes re-measured (`6d3afbc52315`, `776846bf2dc8`, `37ad34d39a19`, `e4838f7bb1d3`, `077a32d1a5c4`, `71869ccc23b4`, `00064b8f2ab3`); UV collapse mechanism corrected. Builder precedents named. |
| **GATE-02** | The suite fails when `dedup_fingerprint` output changes for any frozen shape. The assertion is against an absolute expected value, never `fp(a) == fp(b)`. | Measured baseline: 68 call sites, 11 relational comparisons, only 2 absolute sites (both `a0a50436ae3d`). Pattern 1 + planted-mutation leg (Pattern 4) supplied. |
| **GATE-03** | `build_db_diff`'s ladder output is pinned for the same shapes, so a promotion-ladder change cannot land silently. | All four arms measured with exact `(proposed_disposition, ladder_state)` strings and a concrete reaching shape each. Non-SDP all-OK chips identified (`sst27sf512`, `w27e257`). AT28C256 blind spot reproduced. Existing partial coverage at `:715` flagged (C8). |
| **GATE-04** | The raw-CLI-token → `part_number` delta across the shipped database is measured and recorded as an artifact, not assumed. | Full aggregate measured through `resolve_chip`: 746 rows / 677 distinct `part_number` / 953 aliases / **942 differ** / **514 resolve to a comma-joined list** / 16 `NotImplemented` / 0 `NotFound`. All 26 per-issue rows tabulated. `part_number` read-site mechanics corrected. |
| **GATE-05** | A report corpus lives in `firestarter_app/tests/fixtures/`. There is none today. | Confirmed absent: 23 entries, all `planted_*`/`synthetic_*`/`fake_firestarter`, zero report JSON. `to_dict()` structure captured for the snapshots. |
| **GATE-06** | Every deliberate re-key in this milestone is recorded in `MILESTONES.md` as a declared, dated, one-time decision with its before/after hashes. | House format read (v1.35 section); closest precedent for a falsifying measurement is v1.33 §"Post-Close Correction: The Sweep's Oracle Was Blind". Meta-side runner situation measured (D-13). |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

`/workspaces/CLAUDE.md` (meta) plus user-global instructions. Actionable directives bearing on this phase:

| Directive | Source | Bearing on this phase |
|---|---|---|
| **`.planning/` is the only tracked content in meta**; neither sub-repo is committed here | meta CLAUDE.md §Repository Structure | The app-side work commits **inside** `firestarter_app/`, on the milestone branch; the meta-side checker and `MILESTONES.md` commit in meta |
| **`main` is protected in all three repos** — PR required, no direct push, `current_user_can_bypass: never` | meta CLAUDE.md §Milestone close | The D-13 workflow cannot be validated by pushing to `main`; and `main`-scoped triggers will not fire during this milestone |
| **This project's close targets `beta`, not `main`** (`git.base_branch: beta`) | meta CLAUDE.md; verified in `.planning/config.json` | The meta-side checker's triggers must include `beta` and `gsd/**` |
| **Serial protocol / constants stay in sync across the two repos** | meta CLAUDE.md §Key Architecture | Not touched — this phase is test-only, host-only |
| **`chip_database.json` is GENERATED; never hand-edit** | meta CLAUDE.md + project memory | GATE-04's artifact must be script-generated and drift-tested (D-16); a drift RED is signal |
| **HARD RULE: no comments in source, ever — a plan cannot override it** | user-global memory (broadened 2026-08-29) | Docstrings are fine and are the house style for these gates; **no explanatory `#` comments** in the new fixtures/tests/scripts |
| **Skills must own their scripts** — no importing `firestarter_app/tools` from elsewhere | user-global memory | Reinforces D-16: the meta-side checker must not import the app's script |
| Python app dev flow is `pip install -e .` from `firestarter_app/` | meta CLAUDE.md §Development Commands | Use the py3.11 replica venv variant (see Environment Availability) |

**No directive in CLAUDE.md contradicts any locked decision in CONTEXT.md.**

## Measured Facts

Every row was produced this session. Environment for all of them:

```bash
cd /workspaces/firestarter_app
export UV_CACHE_DIR=<writable>          # /home/vscode/.cache/uv is NOT writable in this devcontainer
uv venv --python 3.11 .venv311
uv pip install --python .venv311/bin/python -e '.[test]'   # `pip` alone leaks to system py3.12: uv venv ships no pip
.venv311/bin/python -c "import sys,firestarter,pytest;print(sys.version.split()[0],firestarter.__file__,pytest.__version__)"
# -> 3.11.16  /workspaces/firestarter_app/firestarter/__init__.py  9.1.1
```

### Branch base

| Fact | Value | Marker | Command |
|---|---|---|---|
| `firestarter_app` HEAD | `49bac1a3a97126f29fb14e795a6569a8e5e09ddd` | MEASURED | `git -C firestarter_app rev-parse HEAD` |
| Branch | `gsd/v1.36-dev-test-fidelity` | MEASURED | `git -C firestarter_app rev-parse --abbrev-ref HEAD` |
| Parity with `origin/beta` | 0 ahead / 0 behind | MEASURED | `git rev-list --left-right --count origin/beta...HEAD` |
| Working tree | clean (0 entries) | MEASURED | `git status --porcelain \| wc -l` |
| `0a93999` -> HEAD content delta | **1 file, 1 line** (`firestarter/__init__.py`) | MEASURED | `git diff --stat 0a93999 HEAD` |

The last row **verifies** CONTEXT.md's claim that research's measurement tree is functionally identical
to the branch base. That verification is what makes the three non-reproducing hashes below a real
discrepancy rather than a tree-drift artifact.

### The canonical-string model (validated before any hash was trusted)

`dedup_fingerprint` is `sha256("|".join(parts))[:12]` where
`parts = [ac.chip, str(ac.protocol or "")] + [f"{op}={verdict}:{cls}" per result] + [repeat_policy_tag] + [coverage_tag]`,
the two tags appended **only when non-empty**
(`firestarter/diagnostic_report.py:186-241` — read this session).

Model validated against the one shipped frozen literal:

| Canonical string | Hash | Expected | Marker |
|---|---|---|---|
| `M8720\|0x08\|write=OK:clean` | `a0a50436ae3d` | `a0a50436ae3d` (`tests/test_diagnostic_report.py:1377`) | **MEASURED — model confirmed** |

Every hash below was produced by the real `dedup_fingerprint` on a real `DiagnosticReport`, with the
canonical string printed alongside for auditability.

### Re-key pair 1 — read-back gating (SST27SF512 six-step): REPRODUCED

| # | Hash | Canonical pre-image | Marker |
|---|---|---|---|
| before | `4dc282a5d596` | `SST27SF512\|7\|id=OK:\|read=OK:\|write=OK:indeterminate\|verify=OK:indeterminate\|erase=OK:\|blank-check=OK:` | **MEASURED — reproduces research exactly** |
| after | `60a031573aab` | same, with `write=OK:` and `verify=OK:` (classification emptied) | **MEASURED — reproduces research exactly** |

Recovered by pre-image search over the real `derive_plan` op orders. **Note the shape is synthetic:** it
is the six *supported* steps of `sst27sf512/full` only, with the chip name spelled **uppercase**
`SST27SF512`, not the raw lowercase CLI token. It is not any real `run_plan` output. The planner should
freeze it as a **hand-specified** row (D-02 table 1), not as a `derive_plan`-derived row.

### Re-key pairs 2 and 3 — m27c512/full: FAILED TO REPRODUCE

`.planning/research/STACK.md:268-299` states these were measured on `m27c512`, `write_scope="full"`,
12 steps. I confirmed that plan shape is still exactly 12 steps in that order:

```
id read blank-check write verify   erase(unsupported)
write-baseline-b write-baseline-a sdp-lock write-inhibited sdp-unlock write-restored   (all unsupported)
```

| Hash | Research's claim | Marker |
|---|---|---|
| `a00791f1c2b4` | m27c512/full before (paths 2 and 3) | **FAILED TO REPRODUCE** |
| `7d1cd4157cfa` | after pruning the 6 SDP steps | **FAILED TO REPRODUCE** |
| `a6f6c6354047` | after canonical `part_number` naming | **FAILED TO REPRODUCE** |

Search space exhausted (all via the validated canonical model):
- the 5 supported steps over **all 5^5 verdict assignments x all 5^5 classification assignments**
  (`""`, `indeterminate`, `blank/contact`, `address-line`, `transport`), unsupported tail pinned `NA:`;
- both layouts (12-step, and 6-step with the SDP tail pruned);
- protocol spellings `"7"`, `""`, `"0x07"`, `"0x08"`;
- chip spellings `m27c512`, `M27C512`, `M27C512,M27V512`, `M27V512`, `m27v512`;
- tag suffixes `""`, `"|runs=1"`, `"|cov=full-device"`, `"|runs=1|cov=full-device"`;
- additionally, uniform-verdict variants with classification `clean` / `match` on ten different step
  subsets, and `write-partial` in place of `write`.

A final exhaustive pre-image sweep over the documented 12-step layout — the 5 supported steps across
**all 5^5 verdict assignments x all 7^5 classification assignments** (adding `clean` and `match` to the
five real values), x 2 protocol spellings, x both step layouts — ran to completion:

```
exhausted 105043750 candidates x2 layouts     # ~2.1e8 canonical strings, 0 hits
```

**None matched, across roughly 210 million canonical strings.** Since the tree is proven
content-identical to research's tree, these three values are **not reproducible from any m27c512 report
shape expressible in the hash's own input grammar**, and must be treated as **unverified priors**. The
most likely explanation is a transcription or bookkeeping error in the original measurement session;
what matters for planning is that no builder this phase writes can be made to emit them.

**What I measured instead**, for the same chip and scope, end to end through the real
`derive_plan` -> `run_plan` -> `DiagnosticReport` path:

| Shape | Hash | Marker |
|---|---|---|
| m27c512/full, all-OK (correct chip id), runs=2 | `6d3afbc52315` | MEASURED |
| m27c512/full, same shape with `ac.chip="M27C512"` (D-2's canonical-naming alternative) | `776846bf2dc8` | MEASURED |
| m27c512/full, same shape with `ac.chip="M27C512,M27V512"` (the full comma-joined `part_number`) | `37ad34d39a19` | MEASURED |
| m27c512/full, all-OK, runs=1 (`\|runs=1` tag present) | `e4838f7bb1d3` | MEASURED |
| m27c512/full, blank-check BAD | `077a32d1a5c4` | MEASURED |
| m27c512/partial, all-OK, runs=2 | `71869ccc23b4` | MEASURED |
| m27c512/none, all-OK, runs=2 | `00064b8f2ab3` | MEASURED |

Canonical string for the first row (all others printed in the same run):
`m27c512|7|id=OK:|read=OK:|blank-check=OK:|write=SKIPPED:|verify=SKIPPED:|erase=NA:|write-baseline-b=NA:|write-baseline-a=NA:|sdp-lock=NA:|write-inhibited=NA:|sdp-unlock=NA:|write-restored=NA:`

**The `m27c512` -> `M27C512` pair `6d3afbc52315` -> `776846bf2dc8` is a genuine, this-session-measured
substitute for research's path-3 pair** and is what the ledger should seed.

### Re-key path 4 — UV `run_count` collapse: DID NOT OCCUR

CONTEXT.md D-12 row 4 and research assert that a BAD standalone blank-check on a UV part aborts cycle 2,
collapsing `run_count` to 1 and making `repeat_policy_tag` emit the degraded `runs=1` discriminator.
**Measured: it does not.**

| Shape | `repeat_policy_tag` | Hash | Marker |
|---|---|---|---|
| m27c512/full, blank-check OK, runs=2 | `''` | `6d3afbc52315` | MEASURED |
| m27c512/full, blank-check **BAD**, runs=2 (the collapse) | **`''` — still empty** | `077a32d1a5c4` | MEASURED |
| m27c512/full, blank-check OK, **runs=1** (`--fast`) | `'runs=1'` | `e4838f7bb1d3` | MEASURED |

Root cause, read this session: `repeat_policy_tag` (`firestarter/chip_test.py:1081-1097`) fires only on
`result.op in _REPEAT_POLICY_OPS and result.run_count == 1`. In the collapse the write and verify steps
are **`SKIPPED` with `run_count == 0`**, not `1`, so the predicate never fires. Measured `run_count` map
for the collapsed run: `{'id':1,'read':2,'blank-check':1,'write':0,'verify':0, ...all others 0}`.

So the collapse **does** move the hash (`6d3afbc52315` -> `077a32d1a5c4`), but via the
`blank-check=OK:` -> `blank-check=BAD:` triple, **not** via `repeat_policy_tag`. The ledger row must say
so, or Phase 179 will be measured against a mechanism that is not the one operating.

**A second, blocking measurement note for this row:** with the shipped `_mock_operator` the m27c512 write
step is never reachable at all — it reports `SKIPPED` with reason *"every UV slot exhausted without
clearing >= 64 bits and retaining >= 64 bits under this pattern"*, because the double's `read_eprom`
returns `True` while writing no file, so no UV slot can satisfy the monotonicity witness. **Producing a
realistic UV write shape requires a stateful operator double that returns a real chip image**, in the
manner of `tests/test_chip_test.py:_sdp_leg_readback_operator`. The planner must budget a task for that
double; the UV row cannot be frozen from `_mock_operator` output.

### GATE-03 — the four `build_db_diff` disposition branches, pinned

Source read this session: `firestarter/diagnostic_report.py:287-322`. The four arms and the concrete
shapes that reach them, each measured:

| Arm | Condition | `proposed_disposition` | `ladder_state` | Concrete shape measured | Marker |
|---|---|---|---|---|---|
| 1 | `"BAD" in verdicts` | `suggests: community-fail signal (advisory -- human triage required)` | `community-fail` | any step BAD (e.g. m27c512/full blank-check BAD) | MEASURED |
| 2 | `"marginal" in verdicts or has_indeterminate_fingerprint` | `inconclusive -- needs N>=2 agreement (advisory)` | `''` | **at28c256/full, SDP-aware double, genuinely all-OK** | MEASURED |
| 3 | `"OK" in verdicts and verdicts <= {"OK","NA","SKIPPED"}` | `suggests: candidate for community-reported (advisory)` | `community-reported` | **`sst27sf512/full` and `w27e257/full`, all-OK, non-SDP** | MEASURED |
| 4 | fallback | `no change suggested (advisory)` | `''` | verdicts `{NA, SKIPPED}` with **no** OK; also empty `results` | MEASURED |

**D-08's blind spot is confirmed by direct measurement.** A genuinely all-OK AT28C256 run through the
SDP-aware double lands in **arm 2**, not arm 3:

```
at28c256|13|id=NA:|read=OK:|write=OK:indeterminate|verify=OK:indeterminate|erase=OK:|blank-check=NA:
|write-baseline-b=OK:indeterminate|write-baseline-a=OK:indeterminate|sdp-lock=OK:
|write-inhibited=OK:indeterminate|sdp-unlock=OK:|write-restored=OK:indeterminate|cov=full-device
  -> 52fb759dc48c   ladder=('inconclusive -- needs N>=2 agreement (advisory)', '')
```

This independently reproduces `.planning/todos/pending/build-db-diff-ladder-state-community-reported-regression.md`.
**`sst27sf512` and `w27e257` are the concrete non-SDP chips that do reach arm 3** — either one satisfies
D-08's "must include a non-SDP all-OK shape" requirement:

| Non-SDP all-OK shape | Hash | Ladder | Marker |
|---|---|---|---|
| `sst27sf512\|7\|id=OK:\|read=OK:\|write=OK:\|verify=OK:\|erase=OK:\|blank-check=OK:\|...NA...\|cov=full-device` | `4b3e52cab987` | `community-reported` | MEASURED |
| `w27e257` same shape | `22908e2954c3` | `community-reported` | MEASURED |

**Partial pre-existing coverage the planner must not duplicate:** `tests/test_diagnostic_report.py:715`
(`test_ladder_state_verdict_mapping`) already asserts all four `ladder_state` values absolutely against
the module constants. It does **not** pin `proposed_disposition` strings and is not keyed to any
`shape_id`. GATE-03's new work is the disposition text plus the `shape_id` binding, not the ladder tag.

### GATE-04 — raw-CLI-token -> `part_number` delta, measured through `resolve_chip`

Measured via `chip_resolver.resolve_chip` (`firestarter/chip_resolver.py:16`) with
`EpromDatabase(skip_local_override=True)`, per D-15 — not the lowercase-form proxy.

**Whole-database aggregate:**

| Quantity | Value | Marker |
|---|---|---|
| rows in `firestarter/data/chip_database.json` | **746** (59 vendors) | MEASURED |
| distinct `part_number` values | **677** | MEASURED |
| `part_number` values containing a comma (alias lists) | **234** | MEASURED |
| distinct single aliases after splitting on `,` | **953** | MEASURED |
| `part_number != part_number.lower()` | **732 / 746** | MEASURED (matches research) |
| **aliases whose lowercase token != resolved `part_number`** | **942 / 953** | MEASURED |
| aliases whose lowercase token == resolved `part_number` | **11 / 953** | MEASURED |
| **aliases resolving to a COMMA-JOINED `part_number`** | **514 / 953** | MEASURED |
| aliases raising `ChipNotImplementedError` | **16 / 953** | MEASURED |
| aliases raising `ChipNotFoundError` | **0** | MEASURED |

**514 of 953 aliases resolve to a comma-joined `part_number`** — the majority. That is the real size of
RPT-F1's "which alias does a title show" problem, and it is far larger than the 732/746 lowercase-form
proxy suggests. Worked examples: `2732` and `2732a` both resolve to `2732,2732A,M2732,M2732A`;
`27128a` resolves to `27128A,D27128A,D27128B`; `27lv256` resolves to `27C256,27LV256`.

**Per-issue rows (D-14's second half), all 26 filed issues:**

| gh# | raw token | verdict | 12-hex | resolved `part_number` | token != pn | state |
|---|---|---|---|---|---|---|
| 18 | fm1608 | PASS | `a6915f4437ee` | `FM1608` | yes | CLOSED |
| 20 | at28c256 | FAIL | `00e121446ceb` | `AT28C256,AT28C256E,AT28C256F,AT28HC256,AT28HC256E,AT28HC256F,AT28HC256L` | yes | CLOSED |
| 21 | at28c256 | FAIL | `00e121446ceb` | (same 7-alias list) | yes | **OPEN** |
| 22 | w27c512 | FAIL | `0eec03f6821b` | `W27C512,W27E512` | yes | CLOSED |
| 23 | w27e257 | FAIL | `7a89fcea856a` | `W27E257` | yes | **OPEN** |
| 24 | w27e257 | FAIL | `3870f9b5f6ca` | `W27E257` | yes | CLOSED |
| 25 | sst39sf020 | PASS | `ed1b5dc79022` | `SST39SF020,SST39SF020A` | yes | CLOSED |
| 26 | w27c020 | FAIL | `f8cb30c62aac` | `W27C02,W27C020,W27E02,W27E020,W27L02` | yes | CLOSED |
| 27 | w27c020 | PASS | `ea556a61c3db` | (same 5-alias list) | yes | CLOSED |
| 28 | m27c512 | FAIL | `31547956e56b` | `M27C512,M27V512` | yes | **OPEN** |
| 29 | m27c512 | INCONCLUSIVE | `7c6997788e25` | `M27C512,M27V512` | yes | CLOSED |
| 30 | m27c1001 | FAIL | `317d6b1e6e18` | `M27C1001,M27V101` | yes | CLOSED |
| 31 | m27c1001 | INCONCLUSIVE | `d8771536cb43` | `M27C1001,M27V101` | yes | **OPEN** |
| 32 | at28c256 | FAIL | `00e121446ceb` | (same 7-alias list) | yes | CLOSED |
| 39 | at28c256 | INCONCLUSIVE | `334c3fa198bf` | (same 7-alias list) | yes | CLOSED |
| 40 | at28c256 | INCONCLUSIVE | `334c3fa198bf` | (same 7-alias list) | yes | CLOSED |
| 41 | w27c512 | FAIL | `137e93501512` | `W27C512,W27E512` | yes | CLOSED |
| 42 | w27c512 | PASS | `8236361b75a5` | `W27C512,W27E512` | yes | CLOSED |
| 45 | **W27E040** | FAIL | `957307f7b750` | `W27C04,W27C040,W27E040` | yes | **OPEN** |
| 46 | W27E512 | PASS | `2f4fb4f62ff3` | `W27C512,W27E512` | yes | CLOSED |
| 47 | sst27sf512 | PASS | `f9dbc31dcd27` | `SST27SF512` | yes | CLOSED |
| 48 | W29c040 | PASS | `969aa43f48c3` | `W29C040,W29C042` | yes | CLOSED |
| 49 | fm1608 | PASS | `0e86f636df87` | `FM1608` | yes | CLOSED |
| 50 | sst39sf040 | FAIL | `52af74c52f2c` | `SST39SF040` | yes | **OPEN** |
| 51 | W27E020 | PASS | `e62e68e1c93a` | `W27C02,W27C020,W27E02,W27E020,W27L02` | yes | CLOSED |
| 52 | W29c020 | PASS | `e09213a69a71` | `W29C020,W29C020C,W29C022` | yes | CLOSED |

- **26 issues, not 27.** MEASURED. `gh issue list --state all --limit 300` returns 45 issues total; 26
  match `[dev test]` in the title and **all 26** carry a 12-hex in the title, with no 12-hex-bearing
  title outside that set. **D-06 and D-14's "27" is wrong by one.** (The `dev-test` *label* covers only
  15 of them, so the label is not a usable enumerator — use the title.)
- **15 distinct chips.** 26/26 rows have `token != part_number`, so the per-chip delta is 100%.
- **Research's "every open issue title is lowercase" is FALSIFIED.** gh#45's raw token is `W27E040`.
  Five of the 26 (gh#45, #46, #48, #51, #52) are not lowercase. RPT-F1's rule cannot assume a lowercase
  input token.
- `resolve_chip` succeeded for **all 26** tokens; none of the filed chips is refused.

**Both named dedup groups VERIFIED exactly:**

| 12-hex | N | issues | chip | Marker |
|---|---|---|---|---|
| `00e121446ceb` | **3** | gh#20, gh#21, gh#32 | at28c256 | **MEASURED — matches D-06** |
| `334c3fa198bf` | **2** | gh#39, gh#40 | at28c256 | **MEASURED — matches D-06** |

These are the only two N>=2 groups in the corpus. `count_agreeing`
(`tools/parse_devtest_issue.py:164-184`, read this session) groups on the **embedded**
`dedup_fingerprint` and never re-hashes — confirming a re-key is permanent for these groups.

### D-06's four reproduction targets — feasibility measured

D-06 requires builder shapes that reproduce the **filed** hash for m27c512, sst27sf512, at28c256, w27e257.

| Chip | Filed hash to reproduce | Feasibility | Marker |
|---|---|---|---|
| sst27sf512 | `f9dbc31dcd27` (gh#47 PASS) | not reproduced this session | UNMEASURED |
| m27c512 | `31547956e56b` (gh#28 FAIL) | not reproduced this session | UNMEASURED |
| at28c256 | `00e121446ceb` (gh#20/21/32 FAIL) | not reproduced this session | UNMEASURED |
| w27e257 | `7a89fcea856a` (gh#23 FAIL) | not reproduced this session | UNMEASURED |

**This is a scope warning, not a blocker.** None of the four filed hashes matched any of the ~40 real
report shapes I generated, and the three m27c512 research hashes did not reproduce either. Reproducing a
*filed* hash requires reconstructing the exact verdict/classification vector of a real community run —
which is recoverable from each issue's fenced JSON `steps[]`, but that means **parsing issue bodies**,
which D-01 explicitly declines to build a loader for. The planner must either (a) budget a task to
hand-transcribe the four step vectors from the four issue bodies into hand-specified builders, or
(b) reduce D-06's reproduction requirement and record why. Recommend (a) for exactly the four named
chips — it is bounded, and hand-transcription is not a loader.

### Cost measurements (the deferred "slow marker" question)

| Measurement | Value | Marker | Command |
|---|---|---|---|
| `derive_plan` sweep: 677 distinct `part_number` x 3 scopes = **2031 plans** | **4.26 s** | MEASURED | timed `derive_plan` loop |
| distinct `(op, supported)` plan shape classes over that sweep | **21** | MEASURED | same run |
| plans where every step is unsupported | **0** | MEASURED | same run |
| the three shipped whole-DB sweep files (`test_erase_flag_invariants`, `test_sdp_db_invariant`, `test_page_size_invariants`) | **0.47 s / 26 tests** | MEASURED | `pytest ... -o addopts="" -q` |
| tests collected in `tests/` | **1955** | MEASURED | `pytest tests/ -o addopts="" -q --collect-only` |
| **full suite wall clock** | **740.92 s (12m20s)** — 1952 passed, **3 failed** (all `test_skip_census.py`, all `subprocess.TimeoutExpired` at its own 180 s child cap) | MEASURED | `pytest tests/ -o addopts="" -q -p no:randomly` |
| the sweep as a share of the suite | **4.26 / 740.92 = 0.58 %** | MEASURED (derived) | — |
| snapshot tests | 32 passed | MEASURED | same run |

**4.26 s independently confirms research's 4.22 s, and 740.92 s independently confirms research's 737 s.**

**PRE-EXISTING RED BASELINE, with a measured root cause — the planner must know this before the phase
starts.** The suite is **not green at the branch base** in this devcontainer. Three tests in
`tests/test_skip_census.py` fail, and **all three fail for the same single reason**, captured verbatim:

```
subprocess.TimeoutExpired: Command '[... '-m', 'pytest', 'tests/', '-rs', '-q',
  '--ignore=tests/test_skip_census.py']' timed out after 180 seconds
```

`test_skip_census.py` spawns a **child pytest run over the whole of `tests/`** and caps it at **180 s**.
The suite actually takes **740.92 s** — **4.1x the child timeout** — so all three census tests
(`test_no_skip_claims_firmware_absent_while_marker_present`, `test_every_skip_reason_is_allow_listed`,
`test_census_child_run_is_live`) time out before asserting anything. This is **not** the sibling-layout
or firmware-absent trap it superficially resembles; it is a **suite-duration** failure, and the census
gate is currently **incapable of passing in this environment regardless of skip hygiene**.

Three consequences for the planner:
1. **A plan must not use "whole suite green" as an acceptance criterion.** It cannot be met at the
   branch base. Carve these three out by name and state the measured reason.
2. **An executor must not "fix" them as collateral** — none of the three touches `dedup_fingerprint`,
   `build_db_diff`, `derive_plan` or `tests/fixtures/`.
3. **This is the real argument for keeping the new sweep cheap.** Every second this phase adds to the
   suite pushes the census child further past its 180 s cap. 4.26 s is negligible against a 561 s
   existing overrun, so it does not change the verdict in Open Question 3 — but a plan that added a
   minutes-long sweep would deepen an already-broken gate. Worth filing as a backlog todo
   (census child timeout vs. real suite duration); it is **not** this phase's to fix.

Confirm the phase's own baseline with a scoped run
(`pytest tests/test_diagnostic_report.py tests/test_chip_test.py -o addopts=""`), not the whole suite. Note the important distinction the planner needs:
the three *existing* whole-DB sweeps cost only 0.47 s in total because they sweep the raw
`chip_database.json`, **not** `derive_plan`. A `derive_plan` sweep is roughly **9x the cost of all three
existing sweeps combined**. Recommendation below.

### Schema pins available for D-07

Captured from a real `report.to_dict()` this session. `SCHEMA_VERSION == "1.7"`.

Top-level sorted keys (11):
`auto_capture, banner, db_diff, dedup_fingerprint, generated, is_submittable, schema_version, sdp_hold_state, steps, transport_health, voltage`

| Sub-object | Sorted keys | Marker |
|---|---|---|
| `voltage` | `vpe_after_mv, vpe_before_mv, vpe_mv, vpp_after_mv, vpp_before_mv, vpp_mv` | MEASURED |
| `banner` | `locked_steps, m_applicable, n_ran` | MEASURED |
| `auto_capture` | `chip, chip_id_actual, chip_id_expected, chip_id_mismatch_reason, fw_board_identity, host_version, hw_revision, protocol` | MEASURED |
| `transport_health` | `cobs_errors, crc_failures, retries, timeouts, transport_suspect` | MEASURED |
| `steps[0]` | `duration_s, error_code, fingerprint, op, reason, run_count, verdict, write_bits_cleared, write_bits_retained, write_coverage, write_current_source, write_region_length, write_region_start` | MEASURED |

**All three of Phase 181's planned deletions are present today** and are therefore pinnable now:
`voltage.vpp_mv`, `voltage.vpe_mv`, `banner.locked_steps`. Note `auto_capture` has **no**
`canonical_part_number` key yet — D-2/RPT-F1 will add it, so the top-level and `auto_capture` key lists
must both be part of the D-07 pin for that addition to be visible.

### The gate's own absence, re-verified

| Claim | Measured | Marker |
|---|---|---|
| `dedup_fingerprint` call sites in `tests/test_diagnostic_report.py` | **68** | MEASURED |
| absolute-hash assertion sites in the whole suite | **2**, both `"a0a50436ae3d"` (lines 1377, 1381) | MEASURED |
| relational `dedup_fingerprint(a) == / != dedup_fingerprint(b)` comparisons | **11** | MEASURED |
| report corpus in `firestarter_app/tests/fixtures/` | **none** — 23 entries, all `planted_*` / `synthetic_*` / `fake_firestarter`, zero report JSON | MEASURED |

GATE-05's premise is confirmed: there is no report corpus today.

### D-13 — where a meta-side checker can actually run

| Fact | Value | Marker |
|---|---|---|
| workflows registered in meta `.github/workflows/` | **exactly one**: `catalog-sync-check.yml` | MEASURED (`ls`) |
| `/workspaces/tools/` contents | `catalog/`, `wiki/` only | MEASURED |
| `tools/wiki/` checkers | retired 2026-09-02; `wiki-check.yml` not registered | CITED (project memory + the `ls` above) |
| `catalog-sync-check.yml` triggers | `push` and `pull_request` on branch **`main`** only, paths `tools/catalog/**` + its own file | MEASURED (read lines 1-17) |
| its last run | **2026-08-31, push to `main`, conclusion `failure`** | MEASURED (`gh run list`) |
| total runs ever | 8 (2 push/main, 6 pull_request) | MEASURED |
| app submodule workflows | `beta-release.yml`, `ci.yml`, `publish.yml`, `release.yml` | MEASURED |

**This is the phase's biggest unresolved planning risk and it needs an explicit decision.**

1. There is exactly **one** live meta-side workflow and it is **currently RED**. Adding a job to it, or
   modelling a new one on it, inherits a red baseline — the planner must not treat a red run as evidence
   its own new leg fired.
2. `catalog-sync-check.yml` is scoped to **`main`**. This project's `git.base_branch` is **`beta`**
   (`.planning/config.json`, measured), `main` is protected and lags, and milestone work happens on
   `gsd/v1.36-*`. A new checker copying those triggers **would not run once during this milestone** —
   precisely the fail-open shape D-13 exists to avoid. The six historical `pull_request` runs fired only
   because those PRs *targeted* `main`.
3. `catalog-sync-check.yml` *is* nonetheless the right structural model for the cross-tree read: it
   checks out meta to a subdirectory and then checks out the sub-repo explicitly at a resolved ref,
   rather than relying on `submodules: recursive` (its own comments record that submodule fetching
   re-armed a `No url found for submodule path` failure class). Copy that shape.

**Recommendation:** the meta-side ledger checker should be a **plain script in meta invoked by a local
gate** (the phase's own verification command, run against the checked-out submodule at
`/workspaces/firestarter_app`), and *additionally* registered in a new workflow triggered on
`push`/`pull_request` to **`beta` and `gsd/**`** with paths covering `.planning/MILESTONES.md` and the app
submodule gitlink. Do not put it in `catalog-sync-check.yml`. Have the planner require the checker be
**seen RED** against a hand-broken ledger row before it is accepted — the workflow-not-registered failure
mode is exactly this project's documented `wiki-check.yml` history.

## Summary

CONTEXT.md already settles this phase's design across sixteen locked decisions. This research therefore
does not survey alternatives — it **measures**, at the actual branch base, the exact literals the planner
cannot write without them. Every number below was computed this session in a py3.11 CI-replica venv
against `firestarter_app @ 49bac1a`, which is at exact parity with `origin/beta` (0 ahead / 0 behind) on
a clean working tree. CONTEXT.md's "Branch-base facts" block is stale on both of its points and the
orchestrator's corrections are confirmed: both submodules are already on `gsd/v1.36-dev-test-fidelity`,
and the stray `tools/build_db.py` rename is gone.

**The single most important finding is a correction, not a confirmation.** The SST27SF512 six-step re-key
pair reproduces *byte-exactly* and I recovered its full canonical pre-image. The two real dedup groups
(`00e121446ceb` across gh#20/21/32 and `334c3fa198bf` across gh#39/40) reproduce exactly. But **three of
the four inherited before/after hashes — `a00791f1c2b4`, `7d1cd4157cfa`, `a6f6c6354047` — could not be
reproduced from any m27c512 report shape**. An exhaustive pre-image sweep over the documented 12-step
layout — every verdict x classification assignment, both step layouts, four protocol spellings,
~2.1e8 candidate canonical strings — returned **zero hits**. And the fourth
measured re-key path (the UV `run_count` collapse) **did not occur**: the collapse leaves
`repeat_policy_tag` empty, because the collapsed write/verify steps carry `run_count == 0`, not `1`.
The ledger (D-12) must therefore be seeded with **re-measured** values, not inherited ones.

Two further corrections the planner must carry: there are **26** filed `[dev test]` issues, not 27
(D-06/D-14 both say 27); and the claim that "every open issue title is lowercase" is false — gh#45 is
titled `W27E040`.

**Primary recommendation:** Freeze only hashes this phase *computes itself* from a committed builder, and
treat every inherited hash in CONTEXT.md D-12 and PROJECT.md as an unverified prior. Seed the ledger's
`before_hash` column from this phase's own measurement run, and record in `MILESTONES.md` that three
inherited values did not reproduce — that discrepancy is itself the blast-radius finding this gate exists
to surface.

## Corrections to Upstream Documents

The planner must carry these; they contradict CONTEXT.md, REQUIREMENTS.md, PROJECT.md or research.

| # | Document says | Measured truth | Impact |
|---|---|---|---|
| C1 | D-06/D-14: "**27** filed `[dev test]` issues" | **26** | The committed artifact has 26 rows; a test asserting 27 fails |
| C2 | D-12 rows 2/3: `a00791f1c2b4` -> `7d1cd4157cfa` / `a6f6c6354047` | **not reproducible** | Ledger must seed re-measured values (`6d3afbc52315` -> `776846bf2dc8` for naming) |
| C3 | D-12 row 4 / research: UV collapse re-keys "via `repeat_policy_tag`" | tag stays `''`; re-key is via the `blank-check` verdict triple | Phase 179's row names the wrong mechanism |
| C4 | Research: "every open issue title is lowercase" | gh#45 is `W27E040`; 5 of 26 are not lowercase | RPT-F1 cannot assume a lowercase token |
| C5 | CONTEXT.md: app submodule on `gsd/v1.35-...` at `0a93999`, stray `build_db.py` rename | on `gsd/v1.36-dev-test-fidelity` at `49bac1a`, tree clean | Branch/fork tasks are already done; no stray to avoid |
| C6 | Research: 732/746 is "the" naming delta | true, but the load-bearing number is **514/953 aliases resolve to a comma-joined `part_number`** | RPT-F1's rule domain is the majority case, not an edge case |
| C7 | Implicit: the three shipped whole-DB sweeps cost ~4.2 s | they cost **0.47 s**; the 4.26 s is specific to a `derive_plan` sweep | Changes the slow-marker tradeoff |
| C8 | GATE-03 as wholly new | `test_ladder_state_verdict_mapping` (`:715`) already pins all four `ladder_state` values | New work is disposition text + `shape_id` binding |

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|---|---|---|---|
| Frozen shape builders + `shape_id` registry | app test fixtures (`firestarter_app/tests/fixtures/`) | — | D-03; imported by Phases 175-181, so it is a published contract |
| Absolute-hash assertions (GATE-01/02) | app test suite | — | Hash is taken off the real object by the real function |
| Committed `to_dict()` JSON snapshots + key-list pin (D-07, GATE-05) | app test fixtures | — | Output snapshots, no loader (D-01) |
| Ladder/disposition pin (GATE-03) | app test suite | — | `build_db_diff` is pure and app-local |
| Raw-token -> `part_number` delta artifact (GATE-04) | app script + committed output + drift test (D-16) | — | DB is generated; drift is signal |
| Machine-readable re-key ledger | app test data (authoritative, D-13) | — | Checked by the suite that can see the hashes |
| Narrated re-key ledger (GATE-06) | meta `.planning/MILESTONES.md` | — | Human record, house format |
| Cross-tree ledger consistency check (D-13) | **meta repo** script + CI | local phase gate | Only meta can see both trees; app-side would fail open |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---|---|---|---|
| CPython | **3.11.16** | CI-replica interpreter | MEASURED in this session's venv. App CI is 3.11-only; devcontainer default 3.12 is proven in this project to mask beta-CI breakage |
| pytest | **9.1.1** | test runner, `parametrize` for the frozen table | MEASURED as installed by `.[test]` |
| stdlib `hashlib` / `json` / `dataclasses` | stdlib | hashing, JSON snapshots, report construction | `dedup_fingerprint` already uses `hashlib.sha256` |

### Supporting

| Library | Version | Purpose | When to Use |
|---|---|---|---|
| `uv` | installed | create the 3.11 venv | Setup only; **must set `UV_CACHE_DIR`** and **must use `uv pip install --python .venv311/bin/python`** |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|---|---|---|
| stdlib + pytest | `syrupy` snapshots for the frozen table | Rejected: HYG-02 is milestone-wide; and `syrupy` bounding is Phase 181's work, not this phase's. An absolute-literal assertion is also *more* legible than a snapshot for a gate whose whole point is that the value is declared |
| stdlib + pytest | `hypothesis`, `jsonschema`, `pydantic` | Rejected at milestone level (REQUIREMENTS.md §Out of Scope, measured unnecessary) |

**Installation:** none. **No new library is added** (Claude's Discretion, locked; HYG-02).

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** The Standard Stack above is entirely
already-installed interpreter, already-pinned test dependencies, and the Python standard library. No
`package-legitimacy check` was required and none was run.

**Packages removed due to `[SLOP]` verdict:** none.
**Packages flagged as suspicious `[SUS]`:** none.

## Architecture Patterns

### System Architecture Diagram

```
                        ┌──────────────────────────────────────────┐
                        │  PRODUCTION (read-only for this phase)   │
                        │                                          │
  raw CLI token ──────► │  chip_resolver.resolve_chip ──► part_num  │
                        │                                          │
                        │  derive_plan ──► Plan.steps               │
                        │        │                                  │
                        │        ▼                                  │
                        │  run_plan ──► [StepResult]                │
                        │        │                                  │
                        │        ▼                                  │
                        │  DiagnosticReport ──┬─► dedup_fingerprint │
                        │                     ├─► build_db_diff     │
                        │                     └─► to_dict()         │
                        └─────────┬─────────┬─────────┬─────────────┘
                                  │         │         │
        ┌─────────────────────────┘         │         └──────────────┐
        ▼                                   ▼                        ▼
┌───────────────────┐          ┌────────────────────────┐  ┌──────────────────┐
│ shape builders    │          │ ladder/disposition pin │  │ to_dict() JSON   │
│ + shape_id        │──┐       │ 4 arms, absolute       │  │ snapshot         │
│ (tests/fixtures/) │  │       └────────────────────────┘  │ + sorted key pin │
└───────────────────┘  │                                   └──────────────────┘
        │              │
        ▼              ▼
┌───────────────────┐  ┌─────────────────────────────┐
│ frozen hash table │  │ re-key LEDGER (authoritative)│
│ absolute 12-hex   │◄─┤ (shape_id, before, after,    │
│ per shape_id      │  │  ledger_id) — append only    │
└───────────────────┘  └───────────┬─────────────────┘
        ▲                          │
        │                          ▼
┌───────────────────┐   ┌──────────────────────────────────┐
│ PLANTED MUTATION  │   │  META repo checker (D-13)        │
│ must be SEEN RED  │   │  reads BOTH trees:               │
└───────────────────┘   │  app ledger  ⟷  MILESTONES.md    │
                        └──────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ GATE-04: script ──► committed delta artifact ──► drift test │
│ (953 aliases → part_number, + 26 per-issue rows)            │
└────────────────────────────────────────────────────────────┘
```

The load-bearing property: **the hash is always taken off a real `DiagnosticReport` by the real
`dedup_fingerprint`**. No deserializer sits between fixture and hash (D-01). The committed JSON is a
downstream *output* snapshot, never an input.

### Recommended Project Structure

```
firestarter_app/tests/fixtures/
├── report_shapes.py                  # builders + SHAPE_IDS registry (D-03, D-04)
├── rekey_ledger.py                   # (shape_id, before_hash, after_hash, ledger_id) rows (D-09, D-12)
├── reports/                          # committed to_dict() snapshots, one per shape_id (D-01, GATE-05)
│   ├── sst27sf512-six-step.json
│   ├── m27c512-full-all-ok.json
│   └── ...
├── devtest_issue_corpus.json         # 26 (issue, chip, 12-hex, part_number) rows (D-06, D-14)
├── part_number_delta.json            # GATE-04 committed artifact (D-16)
└── planted_rekey_mutation.py         # anti-vacuity counter-example (Discretion)

firestarter_app/tests/
├── test_blast_radius_invariance.py   # GATE-01/02/05 + D-07 + D-10
├── test_rekey_ledger.py              # D-09/D-11/D-12 mechanics
└── test_part_number_delta_drift.py   # GATE-04 drift (D-16)

firestarter_app/tools/
└── measure_part_number_delta.py      # generator for the GATE-04 artifact (D-16, repo-owned)

/workspaces/tools/rekey/              # meta-side (D-13)
└── check_rekey_ledger.py             # app ledger ⟷ MILESTONES.md
```

### Pattern 1: Frozen absolute-hash parametrize table

**What:** one `parametrize` row per `shape_id`, asserting an absolute 12-hex literal.
**When to use:** GATE-01/GATE-02.
**Example** — generalize the shipped precedent at `tests/test_diagnostic_report.py:1377`:

```python
# Source: firestarter_app/tests/test_diagnostic_report.py:1362-1382 (shipped idiom)
@pytest.mark.parametrize("shape_id,expected", sorted(FROZEN_HASHES.items()))
def test_dedup_fingerprint_is_frozen(shape_id, expected):
    """A GATE, not a claim. Pinning the literal -- rather than asserting two
    shapes agree with each other -- is what makes a re-key visible instead of
    silently forking every historical count_agreeing group."""
    report = build_shape(shape_id)
    assert dedup_fingerprint(report) == expected, (
        f"{shape_id} re-keyed: expected {expected}, got "
        f"{dedup_fingerprint(report)}. If deliberate, declare it in the ledger "
        f"in a SEPARATE commit (D-11)."
    )
```

### Pattern 2: Element-wise committed list pin (D-07 and D-10)

**What:** assert a sorted list equality, not a membership check.
**When to use:** the `to_dict()` key list, and the complete `shape_id` set.
**Example** — the shipped idiom is list equality with a drift-naming message:

```python
# Source: firestarter_app/tests/test_erase_flag_invariants.py:280-296 (shipped idiom)
assert ops == _AT28C256_FULL_EXPECTED_OP_ORDER, (
    f"AT28C256 write_scope='full' op order drifted from the pinned shape; "
    f"expected {_AT28C256_FULL_EXPECTED_OP_ORDER}, got {ops}"
)
```

Apply the same shape to `sorted(report.to_dict())` and to `sorted(SHAPE_IDS)`. A membership check would
let D-10's "add a row that quietly widens the oracle" through.

### Pattern 3: Append-only ledger assertion (D-09)

```python
for row in LEDGER:
    expected = row.after_hash if row.after_hash is not None else row.before_hash
    assert dedup_fingerprint(build_shape(row.shape_id)) == expected
```

`before_hash` never leaves the tree, so RPT-E3's "exactly the change it declared and nothing more" is a
machine check. Pair it with an assertion that every row's `shape_id` is in `SHAPE_IDS` and that every
filled `after_hash` carries a non-empty `ledger_id`.

### Pattern 4: Anti-vacuity via planted mutation, SEEN red

**What:** a counter-example that must make the gate fail.
**When to use:** mandatory (Claude's Discretion).
**Precedent:** `tests/fixtures/planted_diagnostic_report_claim.py` is the house shape — a standalone,
never-imported module fed to the checker through an env-override seam, *not* a copy of the real module.
For an in-process hash gate the analogue is a builder-level mutation:

```python
def test_frozen_table_is_not_vacuous():
    """The gate must be SEEN to go RED. A gate authored before the content it
    guards can be unreachable and prove nothing."""
    report = build_shape("sst27sf512-six-step")
    report.results[2].fingerprint = None          # the exact re-key Phase 177 will take
    assert dedup_fingerprint(report) != FROZEN_HASHES["sst27sf512-six-step"]
```

### Pattern 5: Closure sentinel over the shape registry (D-10)

Copy `test_shipped_ops_never_reach_sdp_arm` (`tests/test_chip_test_sdp_leg.py:827`): derive the expected
set from the *module's own* declarations so a future added shape cannot escape by omission. Assert
`set(FROZEN_HASHES) == set(SHAPE_IDS) == set(committed_json_filenames)` three ways.

### Anti-Patterns to Avoid

- **Relational assertions.** `fp(a) == fp(b)` passes through any hash change. 11 such comparisons ship
  today and are exactly why this phase exists. GATE-02 forbids them for frozen shapes.
- **Writing a `from_dict` loader.** D-01 forbids it. A loader would drift silently and the oracle would
  lie while staying green.
- **Freezing an inherited hash.** Three of the four inherited pairs do not reproduce. Freeze only what
  this phase computes.
- **Freezing a hash off `_mock_operator` for a UV shape.** The write step is unreachable with that
  double (measured); the frozen value would encode a mock artifact.
- **Fixing a RED gate inside a behaviour-change commit.** D-11 requires a separate commit.
- **Positional indices instead of `shape_id`.** D-04 rejects them; this milestone inserts shapes.
- **Copying `catalog-sync-check.yml`'s `branches: [main]` triggers.** Measured: the milestone never
  targets `main`, so the checker would never run.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Constructing a report for hashing | a new report factory | generalize `_minimal_report` / `_coverage_report` (`tests/test_diagnostic_report.py:151`, `:1311`) | Working, blessed builders taking `(op, verdict, cls, reason)` tuples |
| Reading a report shape from JSON | a `from_dict` deserializer | build the object, snapshot `to_dict()` as output | D-01; there is no `from_dict` anywhere in the tree |
| Whole-DB sweep scaffolding | a new sweep harness | copy `test_erase_flag_invariants.py` / `test_sdp_db_invariant.py` / `test_page_size_invariants.py` | Three shipped precedents; measured 0.47 s total |
| Pinning a list | membership/subset checks | element-wise list equality with a drift message | Shipped idiom; catches deletion *and* addition |
| Proving a gate is not vacuous | reasoning about it | a planted counter-example, seen RED | `MAX_27C020_SIZE` is a live example of a tautological gate in this repo |
| Cross-repo consistency | an app-side gate reading meta | a **meta-side** checker reading the submodule | Every app-side gate scanning the other repo in this project has failed open |
| Grouping filed reports by hash | re-hashing issue bodies | `tools/parse_devtest_issue.py:count_agreeing` | It reads the embedded hash — which is *why* a re-key is permanent |
| Enumerating filed issues | the `dev-test` label | the `[dev test]` title prefix | Measured: the label covers only 15 of 26 |

**Key insight:** every mechanism this phase needs already ships in this repo. The phase's difficulty is
not construction — it is **measurement discipline**: refusing to freeze a number it did not compute.

## Common Pitfalls

### Pitfall 1: Freezing a number that was inherited rather than computed
**What goes wrong:** the ledger seeds `a00791f1c2b4` as a before-hash; no shape in the tree produces it;
the ledger row can never go green, or worse, an executor "fixes" it by editing the builder until it does.
**Why it happens:** CONTEXT.md D-12 presents the four pairs as measured facts, and they are cited in
PROJECT.md and REQUIREMENTS.md too, so they read as settled.
**How to avoid:** every ledger `before_hash` must be produced by a committed builder in the same commit.
Add a test that every ledger row's `shape_id` resolves to a builder and that the builder's current hash
equals the row's expected value.
**Warning signs:** a hash literal in the tree with no builder that produces it.

### Pitfall 2: The AT28C256 ladder blind spot (D-08)
**What goes wrong:** the harness exercises AT28C256 for the "all-OK" arm; AT28C256's SDP leg attaches
`indeterminate` fingerprints in every arm, so an all-OK run lands in arm 2 (`ladder_state == ''`); the
D-4/D-6 flip to `community-reported` is invisible.
**Why it happens:** AT28C256 is the natural choice — it is the chip with the most filed issues.
**How to avoid:** MEASURED — use **`sst27sf512`** or **`w27e257`** for the non-SDP all-OK shape. Both
reach `community-reported` (`4b3e52cab987` / `22908e2954c3`).
**Warning signs:** every ladder row in the pin has `ladder_state == ''` or `'community-fail'`.

### Pitfall 3: A gate that is unreachable and therefore proves nothing
**What goes wrong:** the frozen table is authored, all rows pass, and nobody checks that a change would
fail it. `MAX_27C020_SIZE`'s parity test in this repo guards a firmware `#define` that does not exist.
**How to avoid:** the planted-mutation leg is **mandatory** and must be *seen* RED before the phase
closes. Record the observed RED output in the plan's summary, not just the assertion's existence.

### Pitfall 4: The UV shape cannot be built from `_mock_operator`
**What goes wrong:** a UV `run_count` row is frozen from `_mock_operator` output; the write step is
actually `SKIPPED` with reason *"every UV slot exhausted..."*; the frozen hash encodes a mock artifact,
not a UV write.
**How to avoid:** MEASURED — build a stateful double returning a real chip image, modelled on
`_sdp_leg_readback_operator`. Budget a task for it.

### Pitfall 5: `repeat_policy_tag` does not fire on the collapse
**What goes wrong:** Phase 179 is measured against `repeat_policy_tag` changing; it does not change,
because collapsed steps carry `run_count == 0`, not `1`. The re-key rides the `blank-check` verdict.
**How to avoid:** state the mechanism in the ledger row. MEASURED: `6d3afbc52315` -> `077a32d1a5c4`.

### Pitfall 6: The meta-side checker never runs
**What goes wrong:** a workflow is added copying `catalog-sync-check.yml`'s `branches: [main]`; the
milestone works on `beta`/`gsd/v1.36-*`; the checker fires zero times and the gate fails open — the exact
shape of this project's retired `wiki-check.yml`.
**How to avoid:** MEASURED triggers above. Also make the checker runnable locally as the phase's own
verification command so it does not depend on CI registration at all.

### Pitfall 7: The devcontainer environment silently lies
Three separate traps, all hit this session:
- `grep` is **ugrep** and honors `.gitignore` — it silently under-scans. Use `/usr/bin/grep`.
- `uv venv` ships **no pip**, so a bare `pip install -e '.[test]'` inside the activated venv installs into
  **system python 3.12**. Symptom: `import firestarter` works, `import pytest` fails. Use
  `uv pip install --python .venv311/bin/python`.
- `/home/vscode/.cache/uv` is **not writable**; `uv` fails with `Permission denied (os error 13)` unless
  `UV_CACHE_DIR` points somewhere writable.
- `pytest` `addopts` is `-ra -q`; doubling `-q` hides the count line. Use `-o addopts=""`.

### Pitfall 8: Deleting a row to make a gate green
**What goes wrong:** seven of eight phases in this milestone re-key something; the cheapest route past a
RED is to delete the row.
**How to avoid:** D-10's complete-`shape_id`-set pin, asserted element-wise against a committed sorted
list, plus the three-way closure check in Pattern 5.

### Pitfall 9: Counting 27 issues
MEASURED: there are **26**. A gate asserting 27 fails on day one. Also do not enumerate by the `dev-test`
label (15 of 26).

## Code Examples

### Reproducing the SST27SF512 six-step pair (verified this session)

```python
# Source: measured this session against firestarter_app @ 49bac1a
import hashlib
def dedup(canonical): return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]

BEFORE = ("SST27SF512|7|id=OK:|read=OK:|write=OK:indeterminate"
          "|verify=OK:indeterminate|erase=OK:|blank-check=OK:")
AFTER  = ("SST27SF512|7|id=OK:|read=OK:|write=OK:"
          "|verify=OK:|erase=OK:|blank-check=OK:")
assert dedup(BEFORE) == "4dc282a5d596"
assert dedup(AFTER)  == "60a031573aab"
```

The builder must construct this through `_minimal_report`-style `step_specs`, **not** by hashing a string
— the string above is documentation of the pre-image, not the implementation.

### Building a shape end to end (the path production uses)

```python
# Source: derived from firestarter/cli_handlers.py:2374-2431 (the sole construction site)
from firestarter.chip_test import derive_plan, run_plan
from firestarter.diagnostic_report import (AutoCapture, DiagnosticReport,
                                           TransportHealth, dedup_fingerprint, build_db_diff)

plan = derive_plan(chip, db, write_scope=scope)
results = run_plan(plan, operator_double, db, runs=2)
ac = AutoCapture(host_version=version, chip=chip,                  # raw CLI token (D-2)
                 protocol=str(db.convert_to_programmer(db.get_eprom(chip))["algorithm"]))
report = DiagnosticReport(auto_capture=ac, transport=TransportHealth(),
                          plan=plan, results=results)
fp = dedup_fingerprint(report)
diff = build_db_diff(chip, db, results)     # -> (proposed_disposition, ladder_state)
```

`ac.protocol` is `str(prog["algorithm"])` — MEASURED `"7"` for m27c512/sst27sf512/w27e257, `"13"` for
at28c256.

### The GATE-04 measurement path (D-15)

```python
# Source: measured this session; chip_resolver.resolve_chip is firestarter/chip_resolver.py:16
from firestarter.database import EpromDatabase
from firestarter.chip_resolver import resolve_chip
from firestarter.exceptions import ChipNotFoundError, ChipNotImplementedError

db = EpromDatabase(skip_local_override=True)       # no ~/.firestarter override
for alias in aliases:                              # 953 distinct, from part_number.split(",")
    token = alias.lower()                          # the raw CLI token shape
    cfg, _ = db.get_eprom_config(token)            # carries part_number; convert_to_programmer does NOT
    resolved = cfg.get("part_number")
    try:    resolve_chip(token, db)                # the path the CLI actually takes
    except (ChipNotFoundError, ChipNotImplementedError): pass
```

**Important mechanical detail:** `resolve_chip` returns `convert_to_programmer(...)`, whose keys are
hyphenated (`protocol-id`, `memory-size`) and which **does not contain `part_number`**. The
`part_number` must be read from `db.get_eprom_config(token)`'s raw config. A planner task that expects
`resolve_chip`'s return value to carry `part_number` will fail.

### The four ladder arms (measured)

```python
# Source: measured this session; firestarter/diagnostic_report.py:287-322
# arm 1  any BAD                          -> ('suggests: community-fail signal (advisory -- human triage required)', 'community-fail')
# arm 2  marginal OR indeterminate fp     -> ('inconclusive -- needs N>=2 agreement (advisory)', '')
# arm 3  OK and verdicts <= {OK,NA,SKIPPED} -> ('suggests: candidate for community-reported (advisory)', 'community-reported')
# arm 4  fallback (no OK at all)          -> ('no change suggested (advisory)', '')
```

Arm 4 is reachable with `verdicts == {"NA","SKIPPED"}` or with an empty `results` list. MEASURED: **no
real `derive_plan` output has every step unsupported (0 of 2031 plans)**, so arm 4 needs a synthetic
shape — which is legitimate, and should be labelled as such in the `shape_id`.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| Relational dedup assertions (`fp(a) == fp(b)`) | absolute frozen literals | this phase | 11 relational comparisons ship; only 2 absolute sites exist |
| Hash continuity asserted in prose | machine-checked ledger | this phase | RPT-E3 becomes a check |
| `coverage_tag` / `repeat_policy_tag` empty-default discipline | unchanged, and now **pinned** | shipped (260821-wna / 260822-aq6) | Any new discriminator must follow the empty-default rule or it re-keys history |

**Deprecated/outdated:**
- `tools/wiki/` checkers and `wiki-check.yml` — retired 2026-09-02; not a model for D-13.
- The frozen schema-1.2 fixtures' placeholder tokens (`deadnu11id00`, `aaaa11112222`, `shared0000ab`) —
  they prove parsing and grouping and **cannot** prove hash continuity.


## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| CPython 3.11 | every measurement + all gates (Discretion, locked) | ✓ | **3.11.16** via `uv venv --python 3.11` | none needed |
| `uv` | building the replica venv | ✓ | present | `python3.11 -m venv` + `pip` |
| pytest | the harness itself | ✓ | **9.1.1** (from `.[test]`) | none needed |
| `firestarter` (editable) | importing production modules | ✓ | editable from working tree | none needed |
| `gh` CLI | enumerating the 26 filed issues (D-06/D-14) | ✓ | authenticated; `gh issue list` and `gh run list` both worked | commit the artifact and drift-test it offline |
| `git` submodule access to `firestarter_app` | the D-13 cross-tree checker | ✓ | submodule populated at `49bac1a` | none needed |
| meta CI runner for a new workflow | D-13's CI leg | **✗ (effectively)** | only `catalog-sync-check.yml` registered, `main`-scoped, last run RED | **run the checker as a local phase gate**; register CI additionally |
| EPROM hardware / serial port | nothing in this phase | n/a | — | phase is test-only; no hardware needed |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:**
- **A meta-side CI runner that fires on this milestone's branches.** Measured: the only registered meta
  workflow triggers on `main` only. Fallback (recommended): make the D-13 checker a plain script invoked
  by the phase's own `<automated>` verification against the populated submodule, and register CI as an
  additional, non-load-bearing leg.

**Devcontainer gotchas that must be encoded in every plan's commands** (all four hit this session):

| Gotcha | Symptom | Correct form |
|---|---|---|
| `uv` cache dir unwritable | `failed to create directory /home/vscode/.cache/uv: Permission denied (os error 13)` | `export UV_CACHE_DIR=<writable>` |
| `uv venv` ships no `pip` | `import firestarter` OK but `import pytest` → `ModuleNotFoundError`; install silently went to system 3.12 | `uv pip install --python .venv311/bin/python -e '.[test]'` |
| `grep` is ugrep, honors `.gitignore` | silent under-scan; also matches `__pycache__/*.pyc` as "binary file matches" | `/usr/bin/grep` or a `bash` script |
| `addopts = -ra -q` | a second `-q` hides the pass/fail count line | `-o addopts=""` |

**Working-tree hygiene note:** `uv venv` writes a `.gitignore` containing `*` inside the venv directory,
so `.venv311/` does **not** dirty the submodule — verified `git status --porcelain | wc -l` → `0` after
creating and populating it. `.gitignore` itself only lists `.venv/`, so a hand-made `.venv311` **would**
show up; keep using `uv venv`.

## Security Domain

`security_enforcement` is **absent** from `.planning/config.json` and therefore enabled by default. This
phase is **test-only**: it adds no production code path, no input parser, no network call, no
authentication surface, and no cryptographic decision. The relevant analysis is therefore short and
mostly negative.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | no auth surface added |
| V3 Session Management | no | no sessions |
| V4 Access Control | no | no access decisions; `resolve_chip`'s support-status guard is only *read*, never changed |
| V5 Input Validation | **partially** | the GATE-04 script and the issue-corpus artifact ingest `gh` output. Treat issue titles/bodies as **untrusted input**: parse with a strict anchored regex, never `eval`, and never let a title influence a filesystem path. The measured parse used `^\[dev test\]\s+(\S+)\s+—\s+(\w+)\s+\(([0-9a-f]{12})\)` |
| V6 Cryptography | **no (do not hand-roll)** | `dedup_fingerprint` is `hashlib.sha256[:12]` and is **explicitly a non-secret dedup id, not a security control** (its own docstring). This phase must not restate it as a security property, and must not reimplement the hash — call `dedup_fingerprint` |
| V14 Configuration | **yes** | the D-13 workflow is CI configuration; a checker that never runs is the security-relevant failure (fail-open) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---|---|---|
| Untrusted issue title/body drives a test fixture or path | Tampering | Anchored regex parse; commit the *derived* artifact, not raw bodies; never interpolate a title into a path |
| A gate that cannot fail (vacuous oracle) | Repudiation | Mandatory planted-mutation leg, **seen** RED (Discretion, locked) |
| A cross-repo gate that fails open because it never runs | Repudiation | D-13 direction rule + a local runner, not CI-only |
| Treating a 12-hex dedup id as a security/integrity token | Spoofing | Keep the docstring's framing: non-secret dedup id, truncated for distribution only |
| Local `~/.firestarter/database.json` override changing a frozen hash | Tampering | Use `EpromDatabase(skip_local_override=True)` in every fixture and in the GATE-04 script — measured to work, and it is what the shipped sweeps do |

**One concrete finding worth carrying:** the app is documented to write `~/.firestarter/config.json`
despite `FIRESTARTER_CONFIG_DIR` (project memory). Nothing in this phase should touch the config dir, but
any task that *runs* the CLI must not assume the env var isolates it.

## Sections Deliberately Omitted

- **Runtime State Inventory** — omitted by the template's own rule. This is a **greenfield, test-only,
  additive** phase: it renames nothing, migrates nothing, and replaces no string. No datastore key, live
  service config, OS registration, secret name or build artifact carries a value this phase changes.
  Verified negatively: the phase writes only new files under `firestarter_app/tests/fixtures/`,
  `firestarter_app/tests/`, `firestarter_app/tools/`, meta `tools/`, and `.planning/MILESTONES.md`.
  *(The later phases 177/179/181 DO re-key stored values — the embedded hashes in 26 filed GitHub issues
  — and each of those phases needs its own Runtime State Inventory. That is what the ledger records.)*
- **Validation Architecture** — `workflow.nyquist_validation` is explicitly **`false`** in
  `.planning/config.json` (measured), so no VALIDATION.md will be created.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | The three non-reproducing hashes arose from a transcription/bookkeeping error rather than from a step vector outside the hash's input grammar | Measured Facts | The search is now exhaustive over the documented layout (~2.1e8 strings, 0 hits) and the model is VERIFIED against the shipped literal, so this is a weak residual. The remedy is unchanged either way: re-measure and seed measured values |
| A2 | `sst27sf512` and `w27e257` remain non-SDP all-OK chips after the D-4/D-6 `match` bucket lands in Phase 177 | GATE-03 | If the `match` bucket changes their classification, the frozen row re-keys — which is exactly what the ledger is for. Low risk, self-detecting |
| A3 | A meta-side workflow triggered on `beta` + `gsd/**` would actually run (never exercised in this repo) | D-13 | The checker fails open. Mitigated by the recommended local-gate primary |
| A4 | Hand-transcribing four filed step vectors from issue bodies satisfies D-06 without being "a loader" D-01 forbids | D-06 feasibility | If the planner reads it as a loader, D-06's reproduction requirement needs an explicit operator reduction instead |
| A5 | *Resolved — no longer an assumption.* Full suite MEASURED at **740.92 s**; sweep share **0.58 %** | Cost | — |
| A6 | 26 is the complete filed corpus (no issue was deleted, and none is in another repo) | GATE-04 / D-06 | Measured against all 45 issues in `henols/firestarter_prom`; project memory confirms tracking is centralized there. Low risk |

## Open Questions

1. **The three non-reproducing hashes — what does the ledger seed?**
   - What we know: the tree is proven content-identical to research's tree; the SST pair reproduces
     exactly; the m27c512 trio does not, across an exhausted search space.
   - What's unclear: whether research's m27c512 shape can be recovered at all.
   - **Recommendation:** seed the ledger with this phase's own measured pairs (naming:
     `6d3afbc52315` → `776846bf2dc8`) and record the non-reproduction in `MILESTONES.md` as a
     falsified prior — the v1.33 §"The Sweep's Oracle Was Blind" precedent is exactly this shape.
     Do **not** silently substitute; do **not** freeze the inherited values.

2. **D-06's four filed-hash reproductions.**
   - What we know: none of the four reproduces from generated shapes; each issue's fenced JSON carries
     the step vector that would.
   - What's unclear: whether hand-transcription is in scope for a first phase.
   - **Recommendation:** budget one task to hand-transcribe the four step vectors into hand-specified
     builders. If the planner judges it out of scope, D-06 must be explicitly reduced with the reason
     recorded — not left as an assertion that cannot pass.

3. **Does the `derive_plan` whole-DB sweep run on every push?** (CONTEXT.md defers this to the planner.)
   - What we know: MEASURED 4.26 s for 2031 plans; the three existing whole-DB sweeps total 0.47 s;
     1955 tests collected; full suite MEASURED at **740.92 s**, so the sweep is **0.58 %** of it.
   - **Recommendation:** **run it on every push, unmarked.** 0.58 % of the measured suite is noise, and
     this phase's whole purpose is a gate that actually fires. Marking it
     slow re-creates the "gate that never runs" failure mode. Use a **module-scoped fixture** so the
     sweep is paid once, as research recommends for Phase 175.

4. **Where does the D-13 checker run?**
   - What we know: one meta workflow, `main`-scoped, currently RED.
   - **Recommendation:** local gate primary, CI additional, triggers on `beta` + `gsd/**`; require the
     checker be seen RED against a hand-broken ledger row.

5. **`shape_id` naming, since D-04 makes it a one-way contract.**
   - **Recommendation:** settle the full `shape_id` list in the plan, not during execution, and include
     the shapes Phases 175–181 will need (ATTR-01 status axis, PRUNE-03 synthesized fingerprint) even
     though they cannot be frozen yet — reserve the names now.

## Sources

### Primary (HIGH confidence)

All measured or read this session, in the py3.11 replica venv against `firestarter_app @ 49bac1a`:

- `firestarter/diagnostic_report.py:150-162` (`is_submittable`), `:186-241` (`dedup_fingerprint`),
  `:247-322` (`_DISPOSITION_*`, `_LADDER_*`, `build_db_diff`), `to_dict()` output
- `firestarter/chip_test.py:138-141` (`FP_*`), `:162-215` (`classify_fingerprint`), `:486-520`
  (`derive_plan`), `:893-897` (`VERDICT_*`), `:1073-1128` (`repeat_policy_tag`, `coverage_tag`),
  `:1503-1512` and `:1725-1735` (unsupported → `VERDICT_NA`)
- `firestarter/chip_resolver.py:1-80` (`resolve_chip`)
- `firestarter/cli_handlers.py:2344-2431` (the sole `DiagnosticReport` construction site; `chip=chip`,
  `protocol=str(prog["algorithm"])`)
- `tools/parse_devtest_issue.py:155-184` (`count_agreeing`)
- `tests/test_diagnostic_report.py:140-198` (`_minimal_report`), `:1311-1382` (`_coverage_report`, the
  frozen literal), `:715-780` (`test_ladder_state_verdict_mapping`)
- `tests/test_erase_flag_invariants.py:154-340` (whole-DB sweep + pinned plan shape idiom)
- `tests/test_chip_test_sdp_leg.py:827-860` (closure sentinel)
- `tests/test_chip_test.py:1009-1054` (`_mock_operator`, `_sdp_leg_readback_operator`)
- `tests/fixtures/planted_diagnostic_report_claim.py` (planted-fixture house style)
- `firestarter/data/chip_database.json` (746 rows, 59 vendors, keyed by `part_number`)
- `pyproject.toml` (`[project.optional-dependencies] test`)
- `gh issue list --repo henols/firestarter_prom --state all --limit 300` (45 issues; 26 `[dev test]`)
- `gh run list --repo henols/firestarter_prom` (8 runs, one workflow, last RED)
- `/workspaces/.github/workflows/catalog-sync-check.yml`, `/workspaces/tools/`
- `/workspaces/.planning/config.json` (`nyquist_validation: false`, `parallelization: false`,
  `git.base_branch: beta`)

### Secondary (MEDIUM confidence)

- `.planning/REQUIREMENTS.md` §Blast-Radius Oracle (GATE-01…06 verbatim), §"Decisions taken at
  definition" (D-1…D-8), §Out of Scope
- `.planning/phases/174-.../174-CONTEXT.md` (D-01…D-16 + Discretion)
- `.planning/MILESTONES.md` (house format; v1.33 §"Post-Close Correction" precedent)
- `.planning/todos/pending/build-db-diff-ladder-state-community-reported-regression.md` — its finding
  was **independently reproduced** by measurement, upgrading it to HIGH
- `/workspaces/CLAUDE.md`, user-global memory (project conventions, devcontainer traps)

### Tertiary (LOW confidence — do not treat as authoritative)

- `.planning/research/SUMMARY.md`, `STACK.md:268-299`, `PITFALLS.md:36-37` — the four re-key pairs.
  **One pair reproduced, three did not, one mechanism was wrong.** Treat every hash in these documents
  as an unverified prior.
- `.planning/PROJECT.md:109-111` — restates the same three unreproduced hashes.

**No external/web source was consulted or needed:** this phase is entirely an in-repo measurement
exercise, no new library is permitted, and every pattern it needs has a named in-tree precedent.
Accordingly no `research-plan` provider fetch was performed and no digests were cached.

## Metadata

**Confidence breakdown:**
- **Measured facts (branch base, GATE-03 arms, GATE-04 aggregate + 26 issue rows, dedup groups, sweep
  cost, `to_dict()` keys, gate-absence baseline):** **HIGH** — computed this session in the py3.11
  replica, canonical-string model validated against a shipped literal, both named dedup groups exact.
- **Standard stack:** **HIGH** — no new library; versions read from the live venv.
- **Architecture / patterns:** **HIGH** — every pattern is a shipped in-tree idiom cited by file and line.
- **Pitfalls:** **HIGH** for the measured ones (including four devcontainer traps hit directly and a
  pre-existing 3-test RED baseline observed in a full 740.92 s suite run).
- **The three inherited m27c512 hashes:** **FAILED TO REPRODUCE, and now HIGH confidence in that
  negative** — an exhaustive ~2.1e8-candidate pre-image sweep over the documented layout returned zero
  hits. The phase must re-measure and must not freeze the inherited values.
- **UV `run_count` re-key mechanism:** **HIGH that the documented mechanism is wrong**; MEDIUM on what
  the realistic UV shape's hash will be, since it needs an operator double that does not exist yet.
- **D-13 runner:** **MEDIUM** — the constraint is measured; the proposed remedy is untried in this repo.

**Research date:** 2026-09-03
**Valid until:** ~2026-10-03 for the patterns and stack. **The frozen hashes are valid only at
`firestarter_app @ 49bac1a`** — any commit touching `dedup_fingerprint`, `derive_plan`, `run_plan`,
`build_db_diff` or `chip_database.json` invalidates them, which is precisely the property GATE-01 exists
to exploit.
