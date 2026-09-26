---
phase: 154
slug: provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-23
---

# Phase 154 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from [`154-RESEARCH.md`](154-RESEARCH.md) §"Validation Architecture" — every
> number below was measured during the research session, not estimated.

---

## The coverage ceiling, stated first

This phase's validation ceiling is unusually low, and pretending otherwise is the main risk:

- The **strongest** oracle (`uno` byte-identity) covers **129 of 635 hit-lines (20%)** — only
  `firestarter/src` + `include`, and only files reaching the `uno` build. It covers **zero** of
  the 331 test-file hits (52% of the corpus, D-04) and **zero** of the 290 host-repo hits.
- The **host repo has no size or byte-identity oracle at all.** 290 hit-lines
  (`firestarter/` 132 + `tests/` 115 + `tools/` 43) have no mechanical
  did-this-change-behaviour check beyond the host suite itself.
- The gates that *do* scan firmware source **fail open**. Research finding F2 **proved** one of
  them (`test_sdp_table_parity.py`) can be driven silently green by exactly the operation D-01
  prescribes: the real `EEPROM_SDP_ENABLE` terminal byte was corrupted `0xA0` (SDP lock) → `0x10`
  (**chip erase**) with one reflowed comment above the declaration, and the gate reported
  **5 passed**.
- **Comment content itself is not mechanically checkable.** Whether D-01 step 3's guard was
  honoured — "never delete the only statement of a non-obvious invariant" — is irreducibly a
  review judgment.

So the architecture is: **strong mechanical proof that nothing *executable* changed; planted
controls proving the gates still work; and explicit, named human review for the comment-content
decisions**, with the review scope bounded by measurement rather than left open.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (firmware native)** | PlatformIO `pio test -e native` (Unity) — **172 cases** |
| **Framework (firmware gates)** | pytest, `firestarter/tests/` — **32 modules, 317 passing** |
| **Framework (host)** | pytest 8+ / syrupy 5+, `firestarter_app/tests/` — **1,970 tests** |
| **Config file** | `firestarter_app/pyproject.toml` (`addopts = "-ra -q"`, line 107) — double `-q` hides the count line; pass `-o addopts=""` |
| **Quick run command** | `rm -rf .pio/build/uno && pio run -e uno && sha256sum .pio/build/uno/firestarter_uno.elf` — **1.5 s** |
| **Quick run (host, targeted)** | `pytest tests/test_sdp_table_parity.py tests/test_dispatch_mirror.py -o addopts="" -q` — **< 1 s** |
| **Full suite command** | `FIRESTARTER_FW_ROOT=<fw> pytest tests/ -o addopts="" -q` (host) — **235 s**; `pio test -e native` — **22 s**; `pytest tests/` (firmware gates) — **12 s** |
| **Estimated runtime** | ~270 s for the whole phase gate; ~1.5 s for the per-file oracle |
| **Python** | **CPython 3.11 only** for host gates (`uv venv --python 3.11`) — the devcontainer's 3.12 masks app CI |
| **Byte-identity artifact** | `.pio/build/uno/firestarter_uno.elf` — **not** `firmware.elf`; `name_firmware.py` rewrites `PROGNAME` |

**Why `sha256` and not a size pair.** Measured: the artifact is bit-for-bit reproducible across
cold builds and across different absolute paths, and is **provably immune** to comment-only edits —
project sources compile with no `-g`, there are zero `__LINE__`/`__FILE__` uses, and the ELF's
`.debug_*` sections come entirely from the prebuilt framework archive. Deleting 1,827 comment lines
across 31 files left both `.elf` and `.hex` unchanged. **SWEEP-05 should be recorded as a hash
pair, which is strictly stronger than the size pair the requirement asks for.**

---

## Sampling Rate

- **Per file swept (firmware):** the byte-identity oracle — 1.5 s. At that cost run it **per file**,
  not per wave; it localises a regression to one file instead of to a batch.
- **Per task commit (host):** the two SWEEP-07 gates plus any gate naming the swept file — < 1 s.
- **Per wave merge (firmware):** `pio test -e native` (22 s) + `pytest tests/` (12 s).
- **Per wave merge (host):** the targeted subset. The 235 s full host suite is too slow for
  per-task and belongs at the phase gate.
- **Phase gate:** all three firmware CI legs (`native`, `native_nodevtools`, `pytest tests/`) plus
  the full host suite, run **after** both sub-repo commits land (D-11 — `test_flash_path_record_sync`
  asserts whole-repo porcelain), with the byte-identity pair recorded.
- **Max feedback latency:** **1.5 s** per swept file; 270 s at the phase gate.
- **Timeout guidance:** **600 s.** 300 s is not needed for anything this phase runs — the slowest
  measured leg is the host suite at 235 s. The known 300 s record-gate requirement (STATE.md's
  52k-char line) does not apply to any gate this phase runs.

---

## Per-Requirement Verification Map

Task IDs are assigned by `gsd-planner`; this map is keyed by requirement so the planner can attach
each row to the task that discharges it.

| Requirement | Behavior | Test Type | Automated Command | Exists |
|-------------|----------|-----------|-------------------|--------|
| SWEEP-01 | Triage procedure applied per hit; 5 keep-examples reflowed | **manual-only** | — comment *content* is not machine-checkable | ❌ review |
| SWEEP-01 | The sweep changed no code | automated | `sha256sum .pio/build/uno/firestarter_uno.elf` (pair) | ✅ |
| SWEEP-02 | No-touch region untouched | automated | `git diff <pre> -- src/firestarter.cpp \| grep -c '^[-+].*buffer_size u16 BE'` → **0** | ✅ |
| SWEEP-02 | cap03 gate still able to fail | automated | `pytest tests/test_cap03_ack_layout_parity.py -k planted` (2 existing planted legs) | ✅ needs clean FW tree |
| SWEEP-03 | IDs stripped in src, retained in tests | automated | survey-regex re-runner: `src`+`include` ID hits → 0; test-file ID hits unchanged | ❌ **W0** |
| SWEEP-04 | Narrow treatment on test files | automated (weak) | `pio test -e native` = 172/172 — proves tests compile and pass, **not** that treatment was narrow | ✅ |
| SWEEP-05 | `uno` byte-identical | **automated, strongest** | cold build + `sha256sum` on `.elf` and `.hex`, plus the `RAM:`/`Flash:` pair | ✅ |
| SWEEP-05 | other two AVR targets unchanged | automated | same for `-e uno328pb`, `-e leonardo` — free, recommended | ✅ |
| SWEEP-06 | 8 app-repo paths classified; generated headers need no fix | automated | per-path hit-count assertion; both generated headers measure **0** (research-measured) | ❌ **W0** |
| SWEEP-06 (F4) | 22 non-stripping **firmware-repo** gates dispositioned | **manual-only** | `pytest tests/` (317 pass) is necessary, not sufficient — fail-open | ❌ review |
| SWEEP-07 | sdp gate RED on comment mis-anchor | automated | `pytest tests/test_sdp_table_parity.py -k planted_comment` | ❌ **W0** proven feasible |
| SWEEP-07 | sdp gate RED on comment brace break | automated | same | ❌ **W0** proven feasible |
| SWEEP-07 | sdp gate not silently green (F2) | automated | leg asserting the extracted slice lies inside the real declaration span | ❌ **W0** recommended addition |
| SWEEP-07 | dispatch C++ leg RED on missing hex | automated | `pytest tests/test_dispatch_mirror.py -k planted_missing` | ❌ **W0** proven feasible |
| SWEEP-07 | dispatch C++ leg fail-open documented | automated | `pytest tests/test_dispatch_mirror.py -k planted_comment_only` (asserts **green**) | ❌ **W0** proven feasible |
| SWEEP-08 | `eeprom_28c.cpp` swept as its own plan | process | plan-structure check, not a test | n/a |
| SWEEP-09 | manifest covers all candidate-swept citations, both endpoints | automated | generator self-check: row count, 0 unhandled variants, every range has `target_line_end` + `source_text_end` | ❌ **W0** |
| SWEEP-09 | manifest is valid JSONL | automated | line-by-line `json.loads` + required-key assertion | ❌ **W0** |
| SWEEP-10 | retarget subset flagged, count reported | automated | count `retarget: true` rows; assert none has a null `target_line` without a recorded reason | ❌ **W0** |
| SWEEP-11 | tool idempotent | automated | `test_remap_citations.py::test_idempotent_on_chained_map` — **chained map required** | ❌ **W0** |
| SWEEP-11 | range shrinks, not translates | automated | `test_remap_citations.py::test_range_spanning_deleted_block_shrinks` | ❌ **W0** |
| SWEEP-11 | explicit repo root; non-zero on empty input | automated | `test_exits_nonzero_on_empty_input` + assert `_HERE` absent from the module | ❌ **W0** |
| SWEEP-11 | tool **not applied** | automated | `git diff <pre> --stat -- .planning/` shows no citation-bearing file modified except the new `v1.33/` tree | ❌ **W0** |
| SWEEP-12 | marker planted, names swept files, points at REMAP-04 | automated (weak) | file exists and contains the literal `REMAP-04` plus ≥1 swept path | ❌ **W0** |
| SWEEP-13 | commit granularity + ordering | automated | `git -C firestarter rev-list --count <pre>..HEAD` == 1; same for app; both porcelain before the host suite | ❌ **W0** |
| SWEEP-13 | archived-`milestones/` collision recorded | **manual-only** | n/a — research §R6 established this phase edits **nothing** under `milestones/` | ❌ record |
| F3 | four golden sidecars handled in lockstep | automated | `pytest tests/test_eprom_params_citations.py tests/test_protocol_branch_inventory.py tests/test_golden_trace_identity.py tests/test_golden_trace_identity_eprom_v131.py` | ✅ gates exist; the **fix** is W0 |

*Status legend: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky · **W0** = Wave 0 dependency*

---

## Wave 0 Requirements

Nothing in this list is optional — every `❌ W0` row above depends on one of these existing first.

- [ ] `firestarter_app/tests/fixtures/planted_sdp_comment_misanchor.cpp` — SWEEP-07 (content specified in RESEARCH §R3)
- [ ] `firestarter_app/tests/fixtures/planted_sdp_comment_brace.cpp` — SWEEP-07
- [ ] `firestarter_app/tests/fixtures/planted_dispatch_comment_only_hex.cpp` — SWEEP-07 fail-open control
- [ ] `firestarter_app/tests/fixtures/planted_dispatch_missing_hex.cpp` — SWEEP-07 RED control
- [ ] New legs in `firestarter_app/tests/test_sdp_table_parity.py` (3) and `test_dispatch_mirror.py` (2) — SWEEP-07. **This is new test code; the phase's "comment text only" framing does not cover it (research F6). Scope clarification, not a conflict — SWEEP-07 requires the controls, and a control is test infrastructure, not a behaviour change.**
- [ ] `.planning/v1.33/tools/remap_citations.py` — SWEEP-11
- [ ] `.planning/v1.33/tools/test_remap_citations.py` — SWEEP-11, **must** include a chained-map idempotency fixture with **two separated deletion blocks** (a one-block fixture passes even against a blind implementation)
- [ ] `.planning/v1.33/tools/fixtures/` — synthetic diff fixtures (≥2 deletion blocks)
- [ ] `.planning/v1.33/tools/build_citation_manifest.py` — SWEEP-09 names no generator, but ~10k rows cannot be hand-authored. Shares the path-resolution rule with the remapper.
- [ ] A survey-regex re-runner for the SWEEP-03 / SWEEP-06 hit-count assertions
- [ ] Disposition of `firestarter/tests/golden/{eprom_params_citations,protocol_branch_inventory,eprom_v131_trace_inventory,sdp_expected_inventory}.json` — research F3
- [ ] **Framework install:** none needed in CI. Locally `uv venv --python 3.11` + `uv pip install -e '.[test]'` with `UV_CACHE_DIR` redirected.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| D-01 step 3's guard was honoured — no non-obvious invariant, trap, or fail-closed rationale lost its only statement | SWEEP-01 | Comment *content* is not machine-checkable. No oracle can distinguish "condensed well" from "condensed away". | Review the full comment diff file-by-file. Bound the scope by measurement: the 129 `uno`-covered hit-lines get the oracle *and* review; the 331 test-file hits and 290 host hits get review only, so they are where review effort belongs. |
| The five named keep-examples land on "keep, reflowed" | SWEEP-01 | Same. | Diff each of `eprom_params.cpp:61`, `uno_rurp_shield.cpp:109`, `database.py:580-630`, `flash_5v_page.cpp:101`, `json_parser.c:92` and show the surviving sentence. |
| `database.py:580-630` still says D-12's *policy* was right and its *premise* was wrong | SWEEP-01 / CONTEXT `<specifics>` | Semantic. Condensing this wrong re-reverses a recorded reversal. | Read the condensed block; confirm both halves of the reversal survive. |
| The 22 non-comment-stripping **firmware-repo** gates are dispositioned | SWEEP-06 / research F4 | They fail open — a green run is not evidence. Building 22 planted controls is out of scope for this phase. | For each, state whether the sweep touches a file it scans; where it does, either add a control or record the exposure. |
| `eeprom_28c.cpp`'s datasheet citation of record survives verbatim | SWEEP-08 | A citation is not provenance; only a reader can tell. | Confirm Atmel doc0270 rev 0270L-PEEPR-2/09 §19 note 2 and Microchip DS20006432B §6.18 note 2 are present, unaltered. |
| The D-08 retarget targets are correct | SWEEP-10 | Choosing "the first surviving code line the comment described" is a judgment per citation. | Review each `retarget: true` row against the pre-sweep text. This is the phase's only manual repair work; its count is a deliverable. |

---

## Validation Sign-Off

- [ ] All tasks have an `<automated>` verify or a named Wave 0 dependency
- [ ] Sampling continuity: no 3 consecutive tasks without an automated verify
- [ ] Wave 0 covers all `❌ W0` references above
- [ ] No watch-mode flags
- [ ] Feedback latency < 600 s (measured worst leg: 235 s)
- [ ] Every `manual-only` row above is attached to a named reviewable artifact, not left implicit
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
