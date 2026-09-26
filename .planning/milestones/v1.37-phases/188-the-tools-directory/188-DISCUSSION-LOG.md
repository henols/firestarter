# Phase 188: The Tools Directory - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-12
**Phase:** 188-the-tools-directory
**Areas discussed:** Consumer declaration form, Gate verdicts + retirement home, Placing the six process
tools, `audit_coverage_matrix.py` itself — then a second round on proof, ordering, `scan_paths.py`, and the
requirement ledger.

---

## Area selection

All four offered gray areas were selected. Areas offered:

| Option | Description | Selected |
|--------|-------------|----------|
| Consumer declaration form | TOOLS-02 — where "who runs this" lives | ✓ |
| Gate verdicts + retirement home | TOOLS-03 — per-gate verdict, and where a retirement condition is written given the no-comments rule | ✓ |
| Placing the six process tools | TOOLS-04 — meta repo, skill copy, retire, or stay | ✓ |
| `audit_coverage_matrix.py` itself | TOOLS-01 + TOOLS-07 — the stronger oracle and the silent `--check` red | ✓ |

---

## Consumer declaration form (first pass)

| Option | Description | Selected |
|--------|-------------|----------|
| In-file, dir-walked check | Each script declares its own consumer; check walks `tools/` on disk, fail-closed by construction | |
| `tests/` registry, `scan_paths.py` model | One committed table with a resolve test | |
| argparse `--help` text | User-facing carrier; measured to cover only about half the directory | |

**User's choice:** Free text — *"I believe that they aren't bringing any value at all to the projects."*

**Notes:** This reframed the entire phase from "document and decide" to "delete". Claude did not proceed on
the ambiguity; it asked in plain text which population was meant (the ten gates, the six process tools, or
`tools/` wholesale) and noted one caveat: the audit made this exact call once before on reference-count
evidence and was wrong about `ci_replica_venv.sh` and `derive_sdp_partition.py` — while stressing that an
operator judgment about *value* is a different and better class of evidence than that scan.

---

## Follow-up: which tools have real purpose

**User's reply:** *"build_db.py and catalog/codegen.py has a really purpose, if catalog/codegen_vectors.py
is needed must be investigated, but it's not something that shall be used in any ci."*

**Investigation run in response** (findings, not options): `codegen_vectors.py` generates frozen COBS/CRC8
golden vectors — `firestarter/include/frame_vectors.h` and `firestarter_app/firestarter/frame_vectors.py` —
consumed by exactly one test per repo and by no product module on either side. `pyproject.toml` has
`packages = ["firestarter"]`, so 18 KB of golden test vectors ship inside the pip wheel. CI runs it twice.
Also corrected the audit's record: CI invokes three `tools/` entry points, not one.

---

## Gate verdicts

| Option | Description | Selected |
|--------|-------------|----------|
| Retire unless load-bearing | Default DELETE; a gate survives only if reading its tests proves something breaks | |
| Retire the whole family, no exceptions | All ten go including `check_mypy_watermark.py` | ✓ |
| Decide each by name, no default | Ten independent verdicts | |

**User's choice:** Retire the whole family, no exceptions.
**Notes:** Chosen with the costs stated in the option text — that `check_mypy_watermark.py` is the only
CI-named gate and the type-error floor, and that `check_no_exists_proxy.py` had been extended eight days
earlier by quick-260912-mo6.

---

## The mypy floor

| Option | Description | Selected |
|--------|-------------|----------|
| Nothing — mypy leaves CI | Step deleted, type-error count no longer gated anywhere | ✓ |
| Plain mypy step, must exit 0 | Strongest floor; red on day one against ~33 existing errors | |
| Inline count in `ci.yml` | The script's job minus the script; must reproduce fail-closed on mypy rc=2 | |

**User's choice:** Nothing — mypy leaves CI.

---

## The six GSD-process tools

| Option | Description | Selected |
|--------|-------------|----------|
| Delete five, keep `diff_db.py` | `diff_db.py` stays with a product-facing rationale as the DB-regeneration review gate | |
| Delete all six | Nothing in `tools/` left doing GSD's work | ✓ |
| Move audit matrix to meta | Relocate rather than delete | |

**User's choice:** Delete all six.
**Notes:** Deletion cost was measured per tool before the question was asked —
`test_blast_radius_invariance.py` and `test_devtest_issue_corpus.py` read committed artifacts and survive;
`test_plan_shapes_drift.py` and `test_part_number_delta_drift.py` invoke their generator by subprocess and
die with it. Choosing this also dissolved TOOLS-01 and TOOLS-07, which was stated in the option text.

---

## The two CI mirrors

| Option | Description | Selected |
|--------|-------------|----------|
| Both go | `ci_parity.sh` and `ci_replica_venv.sh` deleted | ✓ |
| Keep `ci_parity.sh`, drop the replica | Three-leg local mirror survives, guarding the sibling-layout hazard | |
| Keep both, strip leg 4 | Smallest change | |

**User's choice:** Both go.

---

## The frame-vector apparatus

| Option | Description | Selected |
|--------|-------------|----------|
| Freeze the output, delete the generator | Keep both committed artifacts as fixtures; both tests keep passing; TOOLS-06 dissolves | |
| Keep it, out of CI, unship the fixture | Generator survives, CI steps go, `frame_vectors.py` moves out of the wheel | |
| Delete generator and both tests | Whole apparatus goes, both repos | ✓ |

**User's choice:** Delete generator and both tests.
**Notes:** The option text stated plainly that this is the only mechanism proving host and firmware agree on
the same wire bytes, and that unlike the ten gates it is a real byte-level contract test rather than a
zero-findings AST checker. Chosen with that cost visible. Claude then measured the knock-on rather than
reopening the decision: the suite is registered in both pinned native envs, so
`firestarter/scripts/baseline/size_baseline.json`'s `cases: 185` pin moves and the phase becomes
three-repo.

---

## TOOLS-02, second pass

| Option | Description | Selected |
|--------|-------------|----------|
| Drop the check, keep the declarations | Six survivors state who runs them; no new checker | |
| Keep it, as a test in `tests/` | Fail-closed, RED against a planted undeclared script, but not a `check_*.py` | |
| Drop declarations too | TOOLS-02 retired outright | ✓ |

**User's choice:** Drop declarations too.
**Notes:** The cost stated in the option text — that the audit's most confident finding goes unaddressed and
the next cleanup pass inherits the same blind spot — was accepted.

---

## The skill coupling, and `derive_sdp_partition.py`

| Option | Description | Selected |
|--------|-------------|----------|
| Skill takes its own copy of `diff_db` | Moves to `.claude/skills/devtest-rootcause/scripts/`; `check_dispatch.py` refs dropped | ✓ |
| Delete both, rewrite the procedure | Review step becomes a raw `git diff` on `chip_database.json` | |
| Keep `diff_db.py` in `tools/` after all | Reverses the earlier call for one tool | |

| Option | Description | Selected |
|--------|-------------|----------|
| Delete `derive_sdp_partition.py` | Its job shipped; nothing in code calls it | ✓ |
| Keep it | The one case where the audit's own correction applies directly | |

**User's choices:** Skill takes its own copy; delete `derive_sdp_partition.py`.

---

## Second round: proof, ordering, `scan_paths.py`, ledger

All four follow-up areas were selected for discussion.

### Proof the deletion was safe

| Option | Description | Selected |
|--------|-------------|----------|
| Suites green + native-only re-record | Executable gates only; AVR figures verified unmoved by one cold `uno` build | |
| Full cold three-target rebuild too | Phase 185's full transcription ritual for twelve figures | |
| Add a no-dangling-referent sweep | Committed evidence artifact proving zero remaining referents | |

**User's choice:** Free text — *"Do the simplest that aren't have complex things that isn't adding real
value of testing the code."*

**Notes:** Claude stated its reading back before writing it into CONTEXT.md and offered an explicit "my
proof reading is wrong" escape on the closing question: run the things that execute code (ruff, pytest,
smoke test, both native envs, `check_size_baseline.py`, one cold `uno` build); run the dangling-reference
grep as part of the work rather than staging it as a committed artifact; skip transcription ceremony for
figures that should not move. The reading was not corrected.

### Ordering across three repos

| Option | Description | Selected |
|--------|-------------|----------|
| Skill copy first, then host ∥ firmware | Meta wave 1, then two parallel disjoint waves | ✓ (by delegation) |
| Strictly sequential, firmware last | Simplest to bisect | |
| Firmware first | Baseline re-record leads | |

**User's choice:** "You decide." Claude selected the first option and recorded it as discretion at D-21.

### `tests/scan_paths.py`

| Option | Description | Selected |
|--------|-------------|----------|
| Keep the cross-repo half | 11 tool resolvers go; `CROSS_REPO_TEST_PATHS` and the resolve test survive | |
| Delete the module entirely | Both populations go | ✓ |

**User's choice:** Delete the module entirely.
**Notes:** The option text recorded that this removes the only named guard for a *measured* defect — seven
host test modules silently flipping PASS→SKIP at exit 0 on a firmware rename — repaired by Phase 184 eight
days earlier. Claude noted the cost once more when confirming, then carried the decision without
re-litigating it.

### The requirement ledger

| Option | Description | Selected |
|--------|-------------|----------|
| Amend in-phase, retired ≠ complete | Hand amendment as work lands; RETIRED recorded with cause | ✓ |
| Amend in-phase, mark complete | Milestone closes 7/7 on the grounds that the decision was the deliverable | |
| Defer the ledger to close | Reconcile in one pass at milestone close | |

**User's choice:** Amend in-phase, retired ≠ complete.

---

## Claude's Discretion

- Wave-to-plan decomposition and commit boundaries, subject to D-21's three named constraints.
- Ordering across the three repos (explicitly delegated — "you decide").
- Whether the ten gate deletions land as one commit or several, and how their tests batch with them.
- The verdict note's internal structure and prose.
- Which planted-violation fixtures under `tests/fixtures/` go with their gates and which are shared.
- Exact wording of the six survivors' docstrings after the citation sweep.

## Deferred Ideas

- A consumer-declaration convention for the six survivors — retired, not refuted.
- Re-guarding the firmware-rename masking defect that `scan_paths.py` covered.
- A replacement for the cross-repo wire-contract proof.
- The `firestarter_app/tests/` provenance sweep (~1,774 hits) — explicitly out of scope.
- A mypy floor in any form.

## Scope creep redirected

None. Every thread the operator opened was inside the phase boundary — in each case narrowing it by
deletion rather than widening it.
