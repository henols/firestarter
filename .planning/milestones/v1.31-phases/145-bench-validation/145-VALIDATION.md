---
phase: 145
slug: bench-validation
status: approved
nyquist_compliant: true
wave_0_complete: false
created: 2026-08-15
---

# Phase 145 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `145-RESEARCH.md` § Validation Architecture.

**Phase shape note:** this phase adds **no automated tests**. D-16 forbids source changes, and
BENCH-01/BENCH-02 are irreducibly hardware- and operator-gated. The existing suites are run as
**regression tripwires**, not as requirement evidence. Requirement evidence is the bench record and
its artifacts.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (both sub-repos); PlatformIO Unity for the firmware native suites |
| **Config file** | none in `/workspaces/firestarter` (house rule — no `conftest.py`/`pytest.ini`/`pyproject.toml`/`setup.cfg`/`tox.ini`); `firestarter_app/pyproject.toml` sets `addopts = -ra -q` |
| **Quick run command** | `cd /workspaces/firestarter && python3 -m pytest tests/ -q -o addopts=""` |
| **Full suite command** | `python3 -m pytest tests/ -q -o addopts=""` in each sub-repo |
| **Estimated runtime** | ~17.3 s firmware (312 passed) · ~0.5 s host tripwire subset (38 passed) |

**Hard precondition (proven, RQ-9):** `git -C /workspaces/firestarter status --porcelain` must be
**empty** before any pytest run. One untracked file in the firmware checkout turns **9 tests RED**
(5 firmware + 4 host). `-o addopts=""` is required or the doubled `-q` hides the count line.

---

## Sampling Rate

- **After every task commit:** Run `cd /workspaces/firestarter && python3 -m pytest tests/ -q -o addopts=""` (~17 s)
- **After every plan wave:** Run the full suite in **both** sub-repos
- **Per gate:** the gate's own commands **plus** `git -C /workspaces/firestarter status --porcelain` empty
- **Before `/gsd-verify-work`:** both full suites green **and** firmware porcelain empty
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

Rows are gate-level. `Test Type` `hardware` and `human-verify` rows are **not** automatable — they
carry `autonomous: false` (D-19, D-20).

> **The `Task ID` / `Plan` columns below are a pre-planning guess and are SUPERSEDED.** The
> authoritative row→task bindings live in `145-BENCH-LOG.md`'s own "Verification map bindings"
> table, authored by `145-01` Task 1 (17 distinct `145-0N Task M` bindings). Read that table, not
> this column. Deliberately not duplicated here — two copies would drift.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD (Gate 0) | 01 | 1 | BENCH-03 | — | no `support_status` mutation across v1.31 | automated | `git -C firestarter_app diff 4d18b645..HEAD -- firestarter/data/chip_database.json` → empty | ✅ | ⬜ pending |
| TBD (Gate 0) | 01 | 1 | BENCH-03 | — | generator inputs unchanged | automated | diff over `tools/build_db.py`, `extra_chips.json`, `infoic.xml` → empty | ✅ | ⬜ pending |
| TBD (Gate 0) | 01 | 1 | BENCH-03 | — | write-locus lock still holds | automated | `python3 tools/check_no_community_support_status_write.py` → exit 0 | ✅ | ⬜ pending |
| TBD (Gate 0) | 01 | 1 | BENCH-03 | — | histogram unchanged (736 supported / 9 adapter-required / 1 protocol-not-implemented / 746 total) | automated | histogram recount over `chip_database.json` | ✅ | ⬜ pending |
| TBD (Gate 0) | 01 | 1 | BENCH-02 | — | `0x08` skip names part + 60/64 → 0/64 + FUT-08 + "NOT inferred" sentence | source assertion | grep the record for each literal | ✅ | ⬜ pending |
| TBD (Gate 0) | 01 | 1 | BENCH-02 | — | `0x0B` skip names part + 22.4 V DMM / 23.9 V firmware + parked graduation + "NOT inferred" sentence | source assertion | grep the record for each literal | ✅ | ⬜ pending |
| TBD (Gate 0) | 01 | 1 | BENCH-01 | — | three distinct address-attributable 64 KiB images + one 4 KiB pulse image | automated | generate → `sha256sum` → `SHA256SUMS.txt`; assert 4 distinct digests, each file exactly 65536/4096 B | ✅ | ⬜ pending |
| TBD (Gate 1) | 02 | 2 | BENCH-01 | T-HW-flash | image under test identified by **commit**, not version string | hardware | `pio run -t upload -e leonardo` + captured avrdude log (expect 26906 B) | ✅ | ⬜ pending |
| TBD (Gate 1) | 02 | 2 | BENCH-01 | T-HW-size | zero flash growth vs `size_baseline.json` (26906 / 2014) | automated | `pio run -e leonardo --target size` | ✅ | ⬜ pending |
| TBD (Gate 1) | 02 | 2 | BENCH-01 | T-HW-ident | controller/port identity verified this session, not assumed | hardware | `firestarter hw` / `--list` with `-p` and reported port recorded | ✅ | ⬜ pending |
| TBD (Gate 1) | 02 | 2 | BENCH-01 | T-HW-chipid | seated part is Winbond `0xda08`, not ST `0x203d` | hardware | chip-id read; plain `write` aborts on mismatch (fails safe) | ✅ | ⬜ pending |
| TBD (Gate 1) | 02 | 2 | BENCH-01 | T-HW-vpp | VPP in band; **`--force used? No`** | human-verify + hardware | operator adjusts pot; **one** confirming `timeout -s INT N firestarter vpp` | ✅ | ⬜ pending |
| TBD (Gate 1) | 02 | 2 | BENCH-01 | — | pre-write content preserved before first erase | hardware | `firestarter read W27C512 prewrite.bin` + digest into `SHA256SUMS.txt` | ✅ | ⬜ pending |
| TBD (Gate 1) | 02 | 2 | BENCH-01 | — | D-03 settled on the bench, not assumed | hardware | `firestarter erase W27C512 -b` → exit 0 (note: `-b` polarity is **inverted** vs `write`) | ✅ | ⬜ pending |
| TBD (Gate 2 ×3) | 03 | 3 | BENCH-01 | T-HW-write | 64 KiB write completes, firmware verify passes | hardware | `firestarter -v write W27C512 imgN.bin` → exit 0 + `Write to W27C512 successful (…s).` | ✅ | ⬜ pending |
| TBD (Gate 2 ×3) | 03 | 3 | BENCH-01 | — | oracle 1 — second firmware-side compare | hardware | `firestarter verify W27C512 imgN.bin` → exit 0 | ✅ | ⬜ pending |
| TBD (Gate 2 ×3) | 03 | 3 | BENCH-01 | — | oracle 2 — **independent** SHA compare (D-06, recorded on its own line) | automated | `firestarter read W27C512 readbackN.bin` then `sha256sum` equality vs `imgN.bin` | ✅ | ⬜ pending |
| TBD (Gate 2 ×3) | 03 | 3 | BENCH-01 | — | read stability **per cycle** (D-07) | hardware | `dev consistency-check W27C512 --runs 3 --output-dir …` → exit 0, `Distinct SHAs: 1` | ✅ | ⬜ pending |
| TBD (Gate 2) | 03 | 3 | BENCH-01 | — | erase actually fired (D-03 corroboration) | derived | cycles 2 and 3 PASS while 99.8 % / 90.6 % of bytes need a `0→1` transition | ✅ | ⬜ pending |
| TBD (Gate 2) | 03 | 3 | BENCH-01 | — | 3/3 byte-exact on **both** oracles (D-09); any re-seat recorded **twice** | derived | all three cycles PASS on both oracle lines | — | ⬜ pending |
| TBD (Gate 2) | 03 | 3 | BENCH-01 | T-HW-force | **no `--force`, anywhere** (D-17) | source assertion | every recorded command line quoted verbatim as its own subsection heading | ✅ | ⬜ pending |
| TBD (Gate 2) | 03 | 3 | D-11 / 143 H4 | — | long write survives the advertised budget (free evidence) | derived | the 64 KiB write completed at all | — | ⬜ pending |
| TBD (Gate 2) | 03 | 3 | D-10 Claim A | — | ≥1 bar frame at a **non-multiple-of-1024** position | automated | frame extraction over `write_cycleN.stderr.raw`, counting only frames after the **last** bar restart | ✅ | ⬜ pending |
| TBD (Gate 3) | 04 | 4 | D-10 Claim B | T-HW-wear | ≥2 distinct positions inside the same `n // 1024` bucket | automated | frame extraction over the `--pulse-us 4688` run's stderr | ✅ | ⬜ pending |
| TBD (Gate 3) | 04 | 4 | D-12 | — | `--pulse-us` exercised on silicon **above** the 4687 µs residual-gap threshold | hardware | `firestarter write W27C512 img_4k_pulse.bin --pulse-us 4688` → exit 0 | ✅ | ⬜ pending |
| TBD (Gate 3) | 04 | 4 | D-12 | — | A1 per-pulse overhead measured | derived | `(t₂ − t₁)/N` vs `P₂ − P₁` across two pulses over the same byte count; error bars recorded honestly | ✅ | ⬜ pending |
| TBD (Gate 3) | 04 | 4 | D-10 eyes-on | — | operator confirms a smoothly moving bar, not an end-burst | human-verify | operator statement recorded verbatim | — | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `.planning/phases/145-bench-validation/images/*.bin` + `SHA256SUMS.txt` — generated in Gate 0, **before any hardware**
- [ ] `.planning/phases/145-bench-validation/145-BENCH-LOG.md` skeleton (the `99-03-BENCH-LOG.md` gate structure) — authored in Gate 0 so a D-13 halt still lands a usable record
- [ ] `runs/`, `logs/`, `readbacks/` directories with explicit non-`consistency-check-*` naming (Pitfall 5)

*No test-framework install is needed; no test file is added. `tools/gen_test_image.py` does **not**
satisfy D-05's address-attributability constraint — the image generator is bench tooling authored in
the **meta** repo, never in either sub-repo (D-16).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Board silkscreen reads Rev 2.0 | BENCH-01 (D-01) | The EEPROM `hw_revision` byte cannot distinguish Rev 2.0 / 2.2 / modified Rev 0 | Operator reads the silkscreen by eye and states the revision; recorded in the identity table |
| Chip seated / re-seated | BENCH-01 (D-09, D-19) | Physical handling is operator-only | Operator seats the part and confirms; a discarded failure **and** its re-run are both recorded |
| VPP in band, no `--force` | BENCH-01 (D-17) | The operator adjusts the pot himself — no live monitor loop | State the target, wait, take **one** confirming `timeout -s INT N firestarter vpp` read; restart the run clean |
| DMM readings | BENCH-01 (D-19) | Requires physical instrument access | Operator reads and states the value; recorded verbatim, or "not measured" with the reason |
| Bar motion, eyes-on half | D-10 / 143 H4 | The machine half proves frames exist; only a human can confirm the terminal *looked* smooth rather than end-bursting | Operator watches a live write and states what the terminal did |
| Gate authorization per spend | BENCH-01 (D-09, 99-03 precedent) | Silicon spend is the operator's to authorize | Operator signs the authorization line before each gate that touches the chip |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify, a `human-verify` gate with `autonomous: false`, or a Wave 0 dependency
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (images, record skeleton, artifact directories)
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] Firmware porcelain empty before every pytest invocation (RQ-9 tripwire)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-08-15 — `gsd-plan-checker` Dimension 8 PASS (8a–8d individually
verified) across two verification passes over the 9-plan set. `wave_0_complete` stays `false`:
Wave 0's artifacts (images, `SHA256SUMS.txt`, the `145-BENCH-LOG.md` skeleton, the run/log/readback
directories) are produced by `145-01` and `145-02` at execution time, not at plan time.
