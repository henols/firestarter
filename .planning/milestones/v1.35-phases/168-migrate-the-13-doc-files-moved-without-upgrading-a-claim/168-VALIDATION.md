---
phase: 168
slug: migrate-the-13-doc-files-moved-without-upgrading-a-claim
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-31
---

# Phase 168 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `168-RESEARCH.md` § "Validation Architecture" (lines 1169–1240).
> **This phase's gates are its product.** Criteria 4, 5 and 8 each demand *observed failure
> before a green result is believed*.

---

## Test Infrastructure

Three repositories, three different harnesses. There is no single "the suite".

| Property | Meta repo (`/workspaces`) | Host app (`firestarter_app/`) | Firmware (`firestarter/`) |
|----------|---------------------------|-------------------------------|---------------------------|
| **Framework** | none — bash driver + 0/1/2 checker exits (D-07) | pytest 9.1.1, pytest-cov 7.1.0, syrupy 6.0.0 | PlatformIO `pio test -e native` |
| **Config file** | none (no `pyproject.toml`, no `pytest.ini`, no `tests/`) | `pyproject.toml:99-101` (`testpaths=["tests"]`, `addopts="-ra -q"`) | `platformio.ini` |
| **Quick run command** | `bash tools/wiki/selftest.sh` | `python -m pytest tests/test_lockable_proms_doc_claims.py tests/test_protection_table_citations.py tests/test_protect_flags_doc_measurements.py tests/test_py32_packaging.py tests/test_dispatch_mirror.py tests/test_scan_paths_resolve.py -o addopts="" -q` | `pio test -e native` |
| **Full suite command** | `bash tools/wiki/selftest.sh` (12 cases today, all PASS) | `<venv311>/bin/python -m pytest tests/ -o addopts="" -q` | `pio test -e native` |
| **Estimated runtime** | ~3 s | ~5 s (doc subset) / **287 s** (full, 1976 tests) | ~60 s |

**Python floor.** The app suite counts for MIGRATE-03 **only** when run on **Python 3.11**.
The devcontainer runs 3.12 and has provably masked app CI breakage before. Route:
`uv venv --python 3.11` inside the devcontainer, then install and run from that venv —
and print `firestarter.__file__` to confirm the editable install actually resolved there.

**Doubled `-q` trap.** `addopts` is `-ra -q`; passing `-q` again suppresses the count line.
Every command above uses `-o addopts=""` so the pass/fail count is visible.

---

## Sampling Rate

- **After every task commit touching the app:** the 6-module doc subset + `test_scan_paths_resolve.py` — **< 5 s**
- **After every task commit touching the meta repo:** `bash tools/wiki/selftest.sh` — **~3 s**
- **After every plan wave:** full app suite on **py3.11** (expect `1976 passed`, 287 s) + `pio test -e native` if firmware source changed + `selftest.sh`
- **Before `/gsd-verify-work`:** full app suite green on 3.11 + `python -m build --sdist --no-isolation` + `pip install -e . && firestarter --help` + `selftest.sh` green + both new checkers **demonstrated RED then GREEN**, evidence committed
- **Max feedback latency:** 5 s per task; 300 s per wave

---

## Per-Task Verification Map

Task IDs are assigned by the planner; this map is keyed by requirement and behavior so the
planner can bind each row to the task that delivers it.

| Requirement | Wave | Behavior verified | Test Type | Automated Command | File Exists | Status |
|-------------|------|-------------------|-----------|-------------------|-------------|--------|
| MIGRATE-01 | late | 12 pages present and reachable on the live wiki | integration | `git clone <wiki.git> wiki-clone && python3 tools/wiki/wiki.py links --source-dir wiki-clone` (asserts 14 pages, all reachable) | ✅ `wiki.py links` | ⬜ pending |
| MIGRATE-01 | early | Move is auditable per file — no `TBD` left | data | `! grep -q TBD .planning/v1.35/MIGRATION-TABLE.md` | ❌ W0 (one-line gate) | ⬜ pending |
| MIGRATE-02 | mid | Both `doc/` dirs gone | smoke | `! test -d firestarter/doc && ! test -d firestarter_app/doc` | ❌ W0 | ⬜ pending |
| MIGRATE-03 | late | Suite green on the CI floor | full suite | `<venv311>/bin/python -m pytest tests/ -o addopts="" -q` → expect `1976 passed` | ✅ exists | ⬜ pending |
| MIGRATE-03 | late | Build + install + entry point | integration | `python -m build --sdist --no-isolation && pip install -e . && firestarter --help` | ✅ mirrors `ci.yml:96` | ⬜ pending |
| MIGRATE-03 | late | sdist doc-delta **reported**, not assumed | evidence | `tar tzf dist/*.tar.gz \| grep -c 'doc/'` before and after → **0 and 0** | ❌ W0 (report-only) | ⬜ pending |
| MIGRATE-04 | mid | No dead `doc/` link in either sub-repo | source scan | the three `git grep` sweeps in RESEARCH § Repair Surface, minus the D-18 exclusion list, return only excluded paths | ❌ W0 | ⬜ pending |
| HONEST-01 | mid | Claim multiset preserved per page | one-shot checker | `python3 tools/wiki/<honest1>.py --table .planning/v1.35/MIGRATION-TABLE.md --wiki-dir wiki-clone --vocab tools/wiki/claim-vocabulary.json` | ❌ W0 | ⬜ pending |
| HONEST-01 | mid | **Demonstrated RED** on a weakened claim | negative | same checker against a wiki fixture with one `adapter-required` softened → exit 1, DROPPED bucket non-empty | ❌ W0 | ⬜ pending |
| HONEST-01 | mid | Vacuous half reported **as vacuous** | output assertion | checker stdout contains the literal zero-counts for `vpp-exceeds-max`, `UNVERIFIED`, `PROTOCOL-LEDGER` | ❌ W0 | ⬜ pending |
| HONEST-02 | late | Stamp present on every claim-bearing page | checker leg 1 | `python3 tools/wiki/<honest2>.py --wiki-dir wiki-clone --db firestarter_app/firestarter/data/chip_database.json` | ❌ W0 | ⬜ pending |
| HONEST-02 | late | Delimited claims resolve in the DB | checker leg 2 | same | ❌ W0 | ⬜ pending |
| HONEST-02 | late | Stamp hash matches DB → distinct `stale` outcome | checker leg 3 | same | ❌ W0 | ⬜ pending |
| HONEST-02 | late | **Demonstrated RED — fixture** | negative | fixture clone via `new_bare_wiki` with a page claiming an absent part number → exit 1 | ❌ W0 | ⬜ pending |
| HONEST-02 | late | **Demonstrated run — live** | integration | run once against the real clone; record the outcome whatever it is | ❌ W0 | ⬜ pending |
| LEGACY-06 | mid | No unopenable `.planning/` path on any page | source scan | `! grep -rn '\.planning/' wiki-clone/` | ❌ W0 (one-liner) | ⬜ pending |
| LEGACY-06 | mid | Two named pages de-framed | assertion | no `Phase 58` / `Phase 59` in title, no `Full audit trail:`, no `[CITED: .planning` | ❌ W0 | ⬜ pending |
| WIKI-02 | late | No in-repo mirror anywhere | smoke | `! test -d wiki && ! test -f .github/workflows/wiki-publish.yml && ! grep -qE 'def cmd_(publish\|sidebar\|check)' tools/wiki/wiki.py` | ❌ W0 | ⬜ pending |
| WIKI-05 | late | Every page reachable from Home | checker | `python3 tools/wiki/wiki.py links --source-dir wiki-clone` | ✅ exists | ⬜ pending |
| WIKI-05 | late | `_Sidebar.md` lists every page | new leg | new containment leg in `wiki.py links` | ❌ W0 | ⬜ pending |
| WIKI-05 | late | **Demonstrated RED** | negative | **live**: run `links` against the clone after pushing the 12 pages, *before* rewriting `Home.md` → 12 orphans. Plus a fixture case in `selftest.sh`. | ✅ live case already proven during research | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tools/wiki/claim-vocabulary.json` — the D-01 checked-in vocabulary data (not embedded in the checker)
- [ ] `tools/wiki/<honest1-checker>.py` — one-shot HONEST-01 multiset comparison, 0/1/2 exit contract
- [ ] `tools/wiki/<honest2-checker>.py` — standing HONEST-02 stamp + resolve + hash checker, 0/1/2 exit contract
- [ ] `tools/wiki/selftest.sh` — delete the 7 publish/sidebar cases (D-20); add ≥3 new cases (HONEST-01 weakened claim, HONEST-02 absent part number, WIKI-05 unreferenced page)
- [ ] `tools/wiki/wiki.py` — `links` gains a `_Sidebar.md` containment leg; `DEFAULT_SOURCE_DIR` (`:45`) must move or `--source-dir` becomes required, because `wiki/` is deleted this phase
- [ ] `.github/workflows/wiki-check.yml` — rewritten as a clone-driven `schedule` + `workflow_dispatch` workflow
- [ ] Shell one-liner gates for MIGRATE-02, MIGRATE-04, LEGACY-06, WIKI-02 (no framework needed)
- [ ] **`test_dispatch_mirror.py` relocation target** — where the relocated doc leg lives and what it reads (wiki clone? recorded SHA?) is the largest unresolved design question the planner must settle

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The 12 pages are pushed to the live public wiki | MIGRATE-01 | D-19: push is a local operator-run action against a public repository; no CI job publishes | Clone `https://github.com/henols/firestarter_prom.wiki.git`, commit the 12 pages, push. Record the resulting SHA in the phase summary. |
| The two currently-false public pages are corrected | (D-21, D-22) | Same — a live public page edit | Rewrite `How-This-Wiki-Is-Published` and `Home`, push, confirm the rendered pages. |
| Wiki page rendering / hyphen-hazard page names read correctly | MIGRATE-01 | Only observable in GitHub's rendered wiki | Open each of the 14 pages; confirm the two hyphen-hazard names resolve and their inbound links work. |

Everything else on this phase has automated verification.

---

## Non-Vacuity Discipline

Project standard, precedent at `firestarter_app/tests/test_py32_packaging.py:33-42`:

- Every new checker **must assert its scan target was found** before comparing anything.
- Every negative case **must be seen to fail** before its green is believed.
- A "0 of 0 checked, PASS" reported as a plain PASS is precisely the false-PASS this milestone
  exists to prevent — `catalog-sync-check.yml` is the in-repo cautionary record (5 runs, 5
  failures, zero assertions).

---

## Ordering Constraint That Destroys an Oracle If Missed

**D-02: the 12 pre-deletion SHAs must be recorded in `MIGRATION-TABLE.md` before the `doc/`
delete commits.** After deletion the source side is only reachable via
`git -C <subrepo> show <sha>:doc/<file>`. If the SHAs are not captured first, HONEST-01 has no
oracle and criterion 4 becomes unverifiable — irrecoverably.

**Research-confirmed hard blocker (H-1):** deleting `firestarter/doc/PROTOCOLS.md` while the
firmware sibling is present aborts the **entire** app suite at collection — 0 tests run —
because `tests/test_dispatch_mirror.py:38` calls `fw_path("doc","PROTOCOLS.md")` at module
scope and `fw_path` raises (`tests/fw_presence.py:130-140`). The relocation of that leg must
land **before** the firmware `doc/` delete, or MIGRATE-03 cannot be observed at all.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 300 s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
