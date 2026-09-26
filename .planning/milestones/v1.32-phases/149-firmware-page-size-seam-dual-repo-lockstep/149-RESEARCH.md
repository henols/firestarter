# Phase 149: Firmware Page-Size Seam (dual-repo lockstep) - Research

**Researched:** 2026-08-19
**Domain:** Arduino AVR C firmware (PlatformIO / Unity native tests) + Python host CLI, dual-repo lockstep
**Confidence:** HIGH (every mechanism claim below is a `file:line` citation or a pasted command transcript; the four LOW/ASSUMED items are named in the Assumptions Log)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Copied verbatim from `149-CONTEXT.md` `<decisions>`. **All 20 are BINDING. Do not re-litigate.**

- **D-01: Provenance-keyed — deliver only where the upstream `<ic>` record's own `protocol_id` is `0x0D`.** 18 rows qualify; **15 are movers**, every one growing 64 → 128. Rejected: grow-only ignoring provenance (17 movers — adds CYPRESS `FM28V020` and FUJITSU `MB85R256H`, both FRAM); all-real-values with sentinels falling back (28 movers).
- **D-02: The value is carried by `programming.page_size` — the existing key, reused.** Host needs ZERO code change. `infoic_page_size_raw` untouched. Rejected: a new distinct key (`page_size_28c`).
- **D-03: Emit for all 18 corroborated rows, including the 3 already at 64.** Field presence means "provenance-corroborated", not "differs from the firmware default".
- **D-04: The 66 promoted rows keep the 64 floor, and the comment that describes it is corrected.** Three deliverables: (1) a pending todo with the measured part lists; (2) a **separate** pending todo naming CYPRESS `FM28V020` / FUJITSU `MB85R256H`; (3) rewrite `eeprom_28c.cpp:19-32` — for the 11 rows at 16/32 the floor's safety is **unproven**, not disproven.
- **D-05: `page_size` resets to 0 in `json_parse`, exactly as `chip_id` does; the fallback to 64 is applied in the handler.**
- **D-06: Flush on a `page_mask = page_size - 1` bitwise AND against the ABSOLUTE address, never a runtime `%`.** Resolve and store the validated mask once at write-INIT.
- **D-07: Validation is a cheap silent firmware fallback; the invariant is proven on the host.** Firmware: anything not a power of two in `[1, DATA_BUFFER_SIZE]` falls back to 64, no log. Host carries the exhaustive proof across all 746 chips. Rejected: validate-and-warn in firmware; trust-and-mask with no check.
- **D-08: `0x0D` only — `flash_5v_page.cpp` is an explicit non-change.** FIX-04 frozen.
- **D-09: The 128 delivery is observed by a native test on flush cadence, and nothing else.** Runtime INFO log filed as a follow-up todo.
- **D-10: Rename the fallback constant** (e.g. `AT28C_PAGE_SIZE_FALLBACK`).
- **D-11: Pin the new-host / old-firmware direction with a native test** on the unknown-key skip at `json_parser.c:320`.
- **D-12: Fund the growth with a NEW, separately-named, SHA-attributed MERGE-05 exemption.** The existing defect-fix constant is **untouched and not widened**; `MERGE05_UNO_CLASS_FLASH_BAND` stays 64. Rejected: re-anchoring BASE-01; funding from in-phase savings; shipping a RED size gate.
- **D-13: The comparison point is a fresh COLD capture at the forked v1.32 tip, before the first edit.** `rm -rf .pio/build/<env>` then one `pio run -e <env>` per env. Any difference is recorded as **inherited from the v1.31 merge**, never attributed to this phase.
- **D-14: `scripts/baseline/size_baseline.json` is updated at phase end, with a superseding meta note.**
- **D-15: New test cases go into the EXISTING native suites — no new suite.**
- **D-16: `149-PAGE-SIZE.md` in the phase directory is the review artifact.** Precedent: `148-DB-DIFF.md`.
- **D-17: Phase 148's wire golden is preserved, with a committed expected-delta list.** Assert "golden **plus exactly these 18 named deltas**". Key union stays 9.
- **D-18: PGSZ-03 parity is a host test that scans firmware source, with an inventory entry.** Add `src/json_parser.c` to `tests/scan_paths.py`. Prove the skip leg by pointing `FIRESTARTER_FW_ROOT` at an empty directory.
- **D-19: A phase-local, fail-provable claim gate over an EXPLICIT target list.** Hard-code the paths. Plant a violation, watch RED, revert, watch GREEN, commit both transcripts.
- **D-20: One `firestarter_app` changelog line**, stated as **software-proven and unvalidated on silicon**.

### Claude's Discretion

- Exact names for the fallback constant (D-10), the handle field, the mask local, and the new MERGE-05 exemption constant (D-12) — keep each single-sourced.
- Field width of the handle member (`uint16_t` covers 1…512 and costs 2 B RAM against leonardo's 546 B free — the obvious choice, but not locked).
- Whether the `build_db.py` emit rule and the firmware seam land in one plan or two, provided `149-PAGE-SIZE.md` can still show the DB-side and firmware-side evidence separately.
- Fixture shape and location for D-17's expected-delta list.
- Exact wording of the corrected `eeprom_28c.cpp` comment, provided it says **unproven** rather than overrun for the 11 promoted 16/32 rows.

### Deferred Ideas (OUT OF SCOPE)

- **The 66 promoted `0x0D` rows (D-04).** 31 at raw `1`, 8 at 32, 3 at 16, 1 at 256, 1 at 128. They keep the 64 floor. File as a pending todo.
- **CYPRESS `FM28V020` and FUJITSU `MB85R256H` ride the `0x0D` handler by pinout promotion** — both FRAM. A **separate** pending todo: a classification question, not a page-size one.
- **A runtime INFO log naming the effective page size** — declined here on flash cost (D-09), filed as a follow-up.
- **Unifying `flash_5v_page.cpp` onto the wire field** — D-08 records it as a deliberate non-change.
- **Folding `response_code` into the handler log macro** — considered as D-12 funding and **not** folded.
- Reviewed-but-not-folded todos: VPP check skip, CONFIG_VERSION bump, FM1608 byte 0, PlatformIO dev-tools flag, `vcc == 5500` group, AT28C256 gh#20 (Backlog **999.29**, **not retired**), `DATA_BUFFER_SIZE` speed spike.
- **Folded todo (IN scope):** `remove-dead-json-init-sizeof-pointer-bug` — delete `json_init()` and its `json_parser.h:19` declaration. Any flash saving is a bonus; **do not** count it toward D-12's budget.

### Evidence Ceiling (binding, `PROJECT.md` §Current Milestone: v1.32)

No criterion here may require silicon, assert the `0x0D` write path is proven, graduate `0x0D`, change any `support_status`, or be phrased as closing gh#21/#32/#11/#12. **AT28C256 — the gh#21 part — carries `page_size 64`, exactly today's floor**, so this phase cannot change its behaviour at all. *(Independently re-measured this session — see §Measured Non-Claims.)*
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description (from REQUIREMENTS.md §PGSZ) | Research Support |
|----|------------------------------------------|------------------|
| **PGSZ-01** | The per-chip page size travels from `chip_database.json` over the wire to the firmware handler, through the existing JSON command path. | §R5 (emit site `build_db.py:786-795`, `proto_id`/`raw_page_size` in scope at `:478`/`:490`); §R5b (host emit is already built — `database.py:417-419`, `:552-553`); §R2 (the 5-part firmware key skeleton); D-01 arithmetic verified byte-for-byte (§D-01 Verification) |
| **PGSZ-02** | The `0x0D` handler uses the delivered page size, falling back to the conservative 64-byte floor when the field is absent. | §R3 (the single flush site `eeprom_28c.cpp:599`; `handle->address` is `uint32_t` at `firestarter.h:195`); §R3b (mask ≡ mod proven on 7 geometries); §R4 (`test_read_timing` + `test_val_eeprom28c` both in CI, both green here); D-05 reset precedent at `json_parser.c:271-278` |
| **PGSZ-03** | Constants and flag bits stay in lockstep between `firestarter/include/firestarter.h` and `firestarter_app/firestarter/constants.py`. | §R7 (`fw_presence.py` `fw_path`/`requires_fw`; `scan_paths.py` `CROSS_REPO_TEST_PATHS` has 7 entries, `_FLOOR = 6`, `src/json_parser.c` absent); `constants.py:144-148` sync note measured FALSE; `test_cap03_ack_layout_parity.py` is the newest cpp-scan precedent; `tools/ci_parity.sh:86-88` already runs the empty-`FW_ROOT` leg |
| **PGSZ-04** | The flash and RAM delta is measured against a pre-change baseline for all three AVR targets; leonardo has near-zero headroom and MERGE-05's band breach is open. | §R8 (live = BASE-01 + 96 on all three; leonardo MERGE-05 headroom = **0 B**, uno-class = 64 B; leonardo `flash_free` 1670 / 28672 = 5.8%); `_merge05_flash_allowance()` diff shape + the 4 test legs and 2 fixtures it breaks; toolchain installed and `pio` works |
| **PGSZ-05** | The change is stated as **software-proven and unvalidated on silicon**, in those terms. No page-size claim about any physical AT28C part. | §R9 (`146-check-claims.py` pattern, `_assert_default_targets_are_local()` already solves the `_HERE` trap); **the `\bproven\b` forbidden pattern collides with PGSZ-05's own required phrase** — a blocking finding; changelog surface is `README.md:61` |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

Extracted from `/workspaces/CLAUDE.md`, `firestarter/CLAUDE.md`, `firestarter_app/CLAUDE.md`, and `.claude/skills/devtest-rootcause/SKILL.md`. The planner must verify compliance for each.

| # | Directive | Source | Bearing on this phase |
|---|-----------|--------|-----------------------|
| C-1 | **`chip_database.json` is GENERATED and must NEVER be hand-edited.** Every value change lands in `build_db.py`'s decode/emit path. | `devtest-rootcause` SKILL.md; CONTEXT.md §Established Patterns | The 18 rows' `page_size` comes from an emitter change at `build_db.py:786-795`, never a JSON edit |
| C-2 | **Serial protocol changes must be kept in sync** between `firestarter_app/firestarter/serial_comm.py` and `firestarter/src/firestarter.cpp`. | `/workspaces/CLAUDE.md` §Key Architecture Points | The new key rides the existing JSON command path; **no** `serial_comm.py` change is needed (verified — the wire dict is built in `database.py`, framed unchanged) |
| C-3 | **Constants/flag bits are duplicated between `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h`. Change both together.** | `/workspaces/CLAUDE.md` | This IS PGSZ-03. `JSON_KEY_PAGE_SIZE` already exists host-side; the firmware half does not |
| C-4 | **Board differences:** Uno 512-byte data buffer, Leonardo 1024. Buffer size affects chunked transfer in `eprom_operations.py`. | `/workspaces/CLAUDE.md` | Bounds D-07's validation range `[1, DATA_BUFFER_SIZE]` — and makes that range **board-dependent** (§R10c) |
| C-5 | **`messages.h` is codegen-generated and ID-only** — edit `tools/catalog/messages.toml` + regen; there is a CI drift gate. | CONTEXT.md §Established Patterns; `.github/workflows/build.yml:114` | D-07/D-09 add **no** message, so **no codegen run is needed**. If that changes, the catalog is the edit point |
| C-6 | **Firmware build commands** run from `firestarter/`: `pio run -e uno\|uno328pb\|leonardo`, `pio test` for unit tests. | `/workspaces/CLAUDE.md` §Development Commands | D-13's cold capture; §R8c confirms both work here |
| C-7 | **Every `# noqa: BLE001` in `firestarter_app` is inert** (ruff `select = ["E","F","I","UP"]`, `pyproject.toml:131`) — keep `except` clauses narrow by hand. | CONTEXT.md §Established Patterns; measured at `pyproject.toml:131` | Any host-side except added by the emit rule or the parity test |
| C-8 | **`.planning/` and `.claude/` only** are tracked in the meta repo; neither sub-repo is committed there. | `/workspaces/CLAUDE.md` §Repository Structure | `commits_land_in:` per plan (§R11) |

---

## Summary

This phase has an unusually short technical distance to travel and an unusually long *evidence* distance. Every hop in the data path from `infoic.xml` to `eeprom28c_write_execute` already exists except two: the provenance-keyed emit condition in `build_db.py`, and the firmware side of the wire key. The host requires **literally zero code change** — `database.py:417-419` already lifts `programming.page_size` into `_map_data` and `:552-553` already emits wire `page-size`, both truthiness-guarded, and `page-size` is already the 6th of the wire golden's 9 keys. The firmware side is a five-point edit with an exact in-repo template (`read-settling-delay`, Phase 44) and a single flush site to change (`eeprom_28c.cpp:599`).

What is hard is proving it honestly inside a zero-headroom flash budget and an Evidence Ceiling that forbids silicon. Three measurements this session changed what the plan must say. **First**, D-01's arithmetic is exactly right — 84 `algorithm: 13` rows, all 84 joined to the pinned XML with zero unmatched, 18 upstream-native `0x0D` splitting 15 movers @ 128 and 3 no-change @ 64, the four-way provenance table reproducing CONTEXT.md's counts digit for digit, and zero `infoic_page_size_raw` fidelity mismatches. The 15-mover and 3-no-change part lists are byte-identical to CONTEXT.md's. The two curated `_PAGE_SIZE_BY_PART` rows are upstream `0x05`, so they **cannot** collide with the provenance rule. **Second**, R1's named research item resolves against CONTEXT.md: the 18 rows do **not** classify under `PROV01_PROTECT_METADATA` today — they classify under `RULE_VCC_MARGIN_RAIL`, Phase 148's own bucket, and they **stay** there after Phase 149, with `programming.page_size` merely joining each row's compound-secondary list. The bucket census is unchanged at 686/56/2, total changed stays 744, and exit stays 0. A plan criterion of the form "the 18 rows report in the `PGSZ_PAGE_SIZE` bucket" would be **unreachable**. **Third**, PGSZ-05's own required phrase — "software-**proven** and unvalidated on silicon" — is matched by the `proven-unqualified` forbidden pattern `\bproven\b` that every prior claim gate in this project carries, because `\b` fires after a hyphen. The repo already documents this property at `146-check-claims.py:63-65`. Copied verbatim, D-19's gate would be unsatisfiable by the very artifact it exists to protect.

The budget picture is stark and precise. Live flash is BASE-01 + 96 B on all three targets; the leonardo band is 0 B and `MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96` is **fully consumed**, so leonardo's remaining MERGE-05 headroom is **exactly 0 bytes** and uno-class has 64 B. The warm ELFs already on disk measure 24920 / 24970 / 27002 flash and 1573 / 1579 / 2014 RAM — byte-identical to `size_baseline.json` — and `origin/beta` differs from the current firmware tip only by an equal-length version string, so D-13's cold capture should show an inherited delta of 0. That must still be measured, not asserted. The new exemption constant is not a one-line addition: `_merge05_flash_allowance()` is a 4-tuple with two call sites and a decomposition the docstring makes load-bearing, and four legs of `tests/test_check_size_baseline.py` plus two planted fixtures key on the literals `allowance of 96 B` / `allowance of 160 B` / `delta=+97`. Those tests **do** run in firmware CI (`build.yml:161` `pytest tests/ -v`), even though the size script itself runs in no workflow.

**Primary recommendation:** Fork the v1.32 firmware branch off `origin/beta` and take D-13's cold baseline as Wave 0 task 1, before any edit. Then land the DB-side emit rule and the firmware seam as separate plans (both are independently provable), extend `test_read_timing` for D-05/D-11 and `test_val_eeprom28c` for D-09, and treat three things as first-class plan tasks rather than incidental: the `\bproven\b` regex resolution, the `_merge05_flash_allowance()` blast radius including its four broken test legs, and a `diff_db` acceptance criterion phrased around *census invariance plus 18 new compound-secondary tokens* rather than a bucket move that will never happen.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Decide *which* chips get a delivered page size (provenance rule) | Host build tool (`build_db.py`) | — | Only the generator sees the upstream `<ic>`'s own `protocol_id`; the firmware never sees provenance |
| Emit the value into the generated DB | Host build tool (`build_db.py:786-795`) | — | C-1: `chip_database.json` is generated |
| Carry DB value → internal dict → wire | Host runtime (`database.py:417-419`, `:552-553`) | — | **Already built.** Zero change (D-02) |
| Exhaustive power-of-two / range invariant | Host test suite | — | D-07: the only producer is our own in-repo host, so the assertion can be total and free |
| Parse the wire key, reset it per command | Firmware parser (`json_parser.c`) | — | D-05: keeps `json_parse` algorithm-agnostic |
| Validate + resolve the mask (silent fallback) | Firmware handler (`eeprom28c_write_init`) | — | D-06/D-07: the floor stays a named firmware constant |
| Consume the mask at the flush boundary | Firmware handler (`eeprom_28c.cpp:599`) | — | Single site; absolute-address semantics must be preserved |
| Prove the 128 delivery | Firmware native tests (`[env:native]`) | Host wire golden (`test_wire_dict_equivalence.py`) | D-09 proves the *consumption*; D-17 proves the *emission*. Neither alone spans the seam |
| Prove cross-repo constant lockstep | Host test suite (`tests/`, scanning firmware source) | — | D-18: the fail-closed scan infrastructure already exists |
| Flash/RAM budget adjudication | Firmware scripts (`scripts/check_size_baseline.py`) | — | Phase-level gate; runs in no workflow (its *tests* do) |
| Honesty enforcement | Meta repo (phase-local claim gate) | — | D-19: `.planning/phases/149-*/` |

**Tier misassignment this map prevents:** putting the provenance decision in the firmware (it cannot see `protocol_id` provenance — only the resolved `algorithm`), or putting the power-of-two proof in the firmware (D-07 correctly locates it host-side, where it can be exhaustive over all 746 rows for zero AVR bytes).

---

## Preconditions

Everything here must be true before plan task 1 runs. Items 1–3 are **execution-ordering** preconditions the plan itself owns.

| # | Precondition | Status | Verification command |
|---|--------------|--------|----------------------|
| P-1 | A v1.32 firmware branch exists, forked off `origin/beta` | **NOT MET** — `firestarter/` is on `gsd/v1.31-27c-programming-algorithm-fidelity` @ `6992271` | see §R10a |
| P-2 | D-13's cold baseline captured at that fork point, **before the first firmware edit** | **NOT MET** — cannot exist; the fork point does not exist yet | see §R10a / §R8c |
| P-3 | `firestarter_app/` is on the v1.32 milestone branch | **MET** — `gsd/v1.32-at28c-write-path-root-cause-report-provenance` @ `b142c0e` | `git -C firestarter_app rev-parse --abbrev-ref HEAD` |
| P-4 | AVR toolchain present and `pio run` works for all three envs | **MET** (see §R8c) | `pio run -e uno --target size` from `firestarter/` |
| P-5 | `[env:native]` runs green here | **MET** — 10/10 cases in 5.8 s for the two target suites | see §R4d |
| P-6 | Host suite green | **MET** — 1641 passed, 0 failed, 218 s | see §R6c |
| P-7 | Firmware pytest suite green | **MET** — 314 passed, 10.7 s | see §R8f |
| P-8 | Pinned `infoic.xml` copy present and byte-verified | **MET** — 17,861,009 B, md5 `b4548e57c4f6c6c8c4f7387add03fa77` | see §D-01 Verification |
| P-9 | Firmware working tree clean (so the porcelain-asserting suite and any cold build are honest) | **MET at research time** — `git -C firestarter status --porcelain` empty | — |
| P-10 | Meta working tree is dirty (both submodule gitlinks, untracked `.claude/`, `package*.json`); app tree has 7 untracked files | **KNOWN** — stage specific files only | `git status --porcelain` |

**P-1/P-2 ordering is not negotiable.** The plan's Wave 0 must be: fork → cold capture → commit the capture → only then edit firmware. A cold capture taken after any edit cannot serve criterion 4.

---

## Contradictions with CONTEXT.md

Five measured contradictions. None invalidates a decision; all four of the first change what a plan task or acceptance criterion may say. **Surfaced, not silently resolved.**

### X-1 — The 18 rows do NOT classify under `PROV01_PROTECT_METADATA` (R1, highest impact)

**CONTEXT.md `<code_context>` §Integration Points says:** "the 18 rows already classify under `PROV01_PROTECT_METADATA` in today's 744-changed-chip report".

**Measured:** all 18 classify under **`RULE_VCC_MARGIN_RAIL`** — Phase 148's own bucket — because every one of the 18 is also among Phase 148's 56 `vcc_mv 4000 → 5000` movers, and `RULE_VCC_MARGIN_RAIL` sits at priority 4 in `_classify_diff`'s `elif` chain (`diff_db.py:443-446`), far above `PGSZ_PAGE_SIZE` and `PROV01_PROTECT_METADATA`, which are last (`:595`, `:609`).

```
$ python3 tools/diff_db.py 2>&1 | grep -E '^\[[A-Z0-9_]+\] \([0-9]+ chips\)'
[RULE_VCC_MARGIN_RAIL] (56 chips)
[PGSZ_PAGE_SIZE] (2 chips)
[PROV01_PROTECT_METADATA] (686 chips)
```

Per-row census, TODAY vs an injected AFTER-149 state (read-only harness over the real baseline and the real current DB, both passed through `diff_db._canonicalize_db`):

```
row                                            TODAY bucket             AFTER-149 bucket         page_size in secondary?
ATMEL/AT28C010,AT28C010E                       RULE_VCC_MARGIN_RAIL     RULE_VCC_MARGIN_RAIL     True
ATMEL/AT28C040,AT28C040E                       RULE_VCC_MARGIN_RAIL     RULE_VCC_MARGIN_RAIL     True
ATMEL/AT28LV010                                RULE_VCC_MARGIN_RAIL     RULE_VCC_MARGIN_RAIL     True
ATMEL/AT28MC020                                RULE_VCC_MARGIN_RAIL     RULE_VCC_MARGIN_RAIL     True
ATMEL/AT28MC040                                RULE_VCC_MARGIN_RAIL     RULE_VCC_MARGIN_RAIL     True
CATALYST(CSI)/CAT28C010                        RULE_VCC_MARGIN_RAIL     RULE_VCC_MARGIN_RAIL     True
CATALYST(CSI)/CAT28C020                        RULE_VCC_MARGIN_RAIL     RULE_VCC_MARGIN_RAIL     True
CATALYST(CSI)/CAT28C040                        RULE_VCC_MARGIN_RAIL     RULE_VCC_MARGIN_RAIL     True
CATALYST(CSI)/CAT28C512                        RULE_VCC_MARGIN_RAIL     RULE_VCC_MARGIN_RAIL     True
MAXWELL/28C010,28C010T,28C011,28C011T          RULE_VCC_MARGIN_RAIL     RULE_VCC_MARGIN_RAIL     True
SGS-THOMSON/M28010                             RULE_VCC_MARGIN_RAIL     RULE_VCC_MARGIN_RAIL     True
ST/M28010                                      RULE_VCC_MARGIN_RAIL     RULE_VCC_MARGIN_RAIL     True
WED/WE512K8                                    RULE_VCC_MARGIN_RAIL     RULE_VCC_MARGIN_RAIL     True
WED/WME128K8                                   RULE_VCC_MARGIN_RAIL     RULE_VCC_MARGIN_RAIL     True
XICOR/X28C010                                  RULE_VCC_MARGIN_RAIL     RULE_VCC_MARGIN_RAIL     True
ATMEL/AT28MC010                                RULE_VCC_MARGIN_RAIL     RULE_VCC_MARGIN_RAIL     True
WED/WE128K8                                    RULE_VCC_MARGIN_RAIL     RULE_VCC_MARGIN_RAIL     True
WED/WE256K8                                    RULE_VCC_MARGIN_RAIL     RULE_VCC_MARGIN_RAIL     True

TODAY  : {'RULE_VCC_MARGIN_RAIL': 18}
AFTER  : {'RULE_VCC_MARGIN_RAIL': 18}

injected page_size into 18 rows
AFTER-149 whole-DB bucket census: {'PROV01_PROTECT_METADATA': 686, 'RULE_VCC_MARGIN_RAIL': 56, 'PGSZ_PAGE_SIZE': 2}
total changed: 744  unexplained: 0  []
=> diff_db.py exit code would be: 0
```

**Planner consequence.** `diff_db.py` is **not** a bucket-move oracle for this change. The reachable criterion is *census invariance plus token appearance*:
- `python3 tools/diff_db.py` exits **0**
- prints `PASS: all 744 changed chips explained (0 new chips confirmed; 0 chips removed from baseline)`
- bucket census stays **exactly** `686 PROV01_PROTECT_METADATA / 56 RULE_VCC_MARGIN_RAIL / 2 PGSZ_PAGE_SIZE` — in particular `PGSZ_PAGE_SIZE` stays **2**, it does not become 20
- the `--- COMPOUND changes (58) ---` section gains `programming.page_size` in the secondary list of exactly the 18 named rows and no others

**Do NOT write** "the 18 rows report under `PGSZ_PAGE_SIZE`" — measured unreachable. **Do NOT write** "the 18 rows move out of `PROV01_PROTECT_METADATA`" — they were never in it.

**Also measured, for the isolated arms** (synthetic controls on the same real record):

```
CONTROL: page_size ONLY delta          -> bucket=PGSZ_PAGE_SIZE  (clean)
CONTROL: PROV01 keys ONLY delta        -> bucket=PROV01_PROTECT_METADATA  (clean)
CONTROL: PROV01 keys + page_size       -> bucket=PGSZ_PAGE_SIZE  +compound secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
```

So in the *hypothetical* where `vcc_mv` had not moved, `PGSZ_PAGE_SIZE` would win over `PROV01_PROTECT_METADATA` — one silently wins, never both, because `PROV01`'s arm carries an explicit `bl_prog.get("page_size") == cu_prog.get("page_size")` guard at `diff_db.py:622` that makes it unreachable once `page_size` differs. No escalation to unexplained occurs in any case, because `("programming","page_size")` is in `_all_rule_paths` (`diff_db.py:768-770`, verified `True`).

### X-2 — PGSZ-05's required phrase is caught by the standard `\bproven\b` forbidden pattern (D-19)

**CONTEXT.md D-19 says:** the gate "requires PGSZ-05's exact phrase" and cites the prior checkers as the pattern to mirror.

**Measured:** every prior claim gate in this project carries `("proven-unqualified", re.compile(r"\bproven\b", re.IGNORECASE))` — `146-check-claims.py:169`, transcribed from `139-check-claims.py:98-128`, which D-14 of that phase "forbids loosening, narrowing or re-deriving". And:

```
$ python3 -c "import re; p=re.compile(r'\bproven\b', re.IGNORECASE); ..."
'software-proven and unvalidated on silicon' -> True
'This is software-proven.' -> True
'proven on silicon' -> True
'unproven' -> False

proven-on-silicon vs required phrase: False
```

`\b` matches after a hyphen, so **"software-proven" is a `proven-unqualified` violation.** The repo already states this property explicitly at `146-check-claims.py:63-65`:

> "the pattern table is a **writing constraint**: `\bproven\b` is forbidden unqualified and matches after a hyphen, so the closing artifacts are written around the word rather than the pattern loosened."

Phase 146 could write *around* the word. **Phase 149 cannot** — PGSZ-05 mandates the literal phrase "software-proven and unvalidated on silicon", and D-19 requires the gate to demand it. Copied verbatim, the gate is unsatisfiable: `149-PAGE-SIZE.md` would simultaneously be required to contain the phrase and forbidden to contain `proven`.

**Planner consequence — this is a plan decision, not an implementation detail.** Three viable resolutions, in descending preference:
1. **Narrow with a negative lookbehind:** `(?<!software-)\bproven\b`. Keeps the tripwire armed against `proven`, `proven on silicon`, `write path is proven`; permits only the exact PGSZ-05 compound. Cheapest, and provable with a two-line fixture pair (`software-proven` → PASS; `the write path is proven` → FAIL).
2. **Drop `proven-unqualified` from the 149 table** and rely on the narrower `proven-on-silicon` / `verified-on-silicon` / `silicon-verified` patterns plus the required-caveat leg. Loses coverage of a bare "proven".
3. Add a proximity exemption. Rejected by precedent — `146-check-claims.py:59-62` records that Phase 139 *measured* a windowed scanner passing four planted overclaims.

Whichever is chosen, the plan must carry a **negative control** showing the surviving pattern still fires on an unqualified `proven`, or D-19's "fail-provable" property is hollow for the one word that matters most here.

### X-3 — `size_baseline.json`'s `firmware_tree_sha` is stale relative to its own AVR figures (D-13)

**CONTEXT.md D-13 says:** "`size_baseline.json`'s figures were measured at firmware tree `3d8ec49` (Phase 145 debug session)".

**Measured:** `scripts/baseline/size_baseline.json` `meta.firmware_tree_sha` is `3d8ec4913913f5db4e636d88d5180172f83776f9`, which is the root tree of commit **`6cc4795`** ("test(144-04): prove the exhaustiveness gate under D-18 with two planted violations", 2026-08-14) — a **Phase 144** commit. That tree **does not contain the Phase 145 fix**:

```
$ git cat-file -t 3d8ec49
tree
$ git grep -c 'eprom_internal_program_pulse' 6cc4795 -- src/proms/eprom.cpp
(no output — zero hits)
$ git grep -c 'eprom_internal_program_pulse' origin/beta -- src/proms/eprom.cpp
origin/beta:src/proms/eprom.cpp:4
$ git log --oneline 6cc4795..origin/beta -- src include
7f6afc6 Apply automatic changes
6992271 docs(firestarter.cpp): preserve PR #49's two CAP-02 facts the merge resolved away
034363c Merge origin/beta into gsd/v1.31-27c-programming-algorithm-fidelity
ebe9cb3 fix(eprom): raise the VPP settles to 1000us/100us on bench evidence
eb563d2 fix(eprom): assert the program-voltage route around every program pulse
6fab4ea Apply automatic changes
b1737b2 feat(protocol): carry HW revision + FW identity in the MSG_OK_READY ack (#49)
```

`meta.generated_by` correctly describes the Phase-145 re-measure ("SUPERSEDES Phase 144 Plan 05's measurement for the three avr_targets flash_used/flash_free figures ONLY"), but `firmware_tree_sha` was **not** updated alongside it. So the file's own recorded tree SHA predates the +96 B it records.

**Planner consequence.** The plan must **not** reason about the fork-point delta by comparing against `firmware_tree_sha`. Reason by content instead (§R8b), and D-14's phase-end update to this file must **correct `firmware_tree_sha`** to the tree actually measured — otherwise the same defect is re-shipped.

### X-4 — D-10's `PAGE_SIZE` reference count is wrong (4 refs / 3 test files)

**CONTEXT.md D-10 says:** "4 references: `eeprom_28c.cpp:33`, `:634`, plus `PAGE_SIZE` mentions in 3 native test files (`test_val_eeprom28c.cpp:204,256`, `test_eeprom28c_sdp.cpp:1532,1543,1603`)".

**Measured — 8 occurrences across 3 files (2 of them test files):**

```
$ grep -rn '\bPAGE_SIZE\b' --include='*.c' --include='*.cpp' --include='*.h' src include test lib
src/proms/eeprom_28c.cpp:19:/* PAGE_SIZE 64 is a deliberate CONSERVATIVE FLOOR (D-13), not an unexamined
src/proms/eeprom_28c.cpp:33:#define PAGE_SIZE 64
src/proms/eeprom_28c.cpp:599:        bool page_end = ((address + 1) % PAGE_SIZE) == 0;
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:204: * base address 0, data_size 8 (PAGE_SIZE 64, so this is one flush on
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:256: * with PAGE_SIZE 64 the write flushes twice -- once at address 63 on
test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp:1532: * worst value. Two pages (data_size 72, PAGE_SIZE 64: one flush at the
test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp:1543:    const size_t   data_size = 72; /* > PAGE_SIZE (64): two flush windows */
test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp:1603:    const size_t   loaded_before_abort = 64; /* PAGE_SIZE -- the first page, in full */
```

Two firmware files → it is **2** test files, not 3. D-10's *line list* is complete and correct; only the count and file count are wrong, and it misses `:19` (which D-04 rewrites anyway). Exactly **one** occurrence is a code reference (`:634`); `:33` is the definition; the other 6 are comments plus one comment-annotated literal at `test_eeprom28c_sdp.cpp:1603`.

Add a **9th** touch point the rename implies but D-10 does not name: `test/native/avr/test_read_timing/test_read_timing_params.cpp:70-72`'s comment about `json_init()`'s `sizeof` bug, which the folded todo's deletion makes stale (§R10b).

### X-5 — `flash4_page_size()` does not exist (three stale host comments)

**CONTEXT.md** does not raise this, but three host comments cite a firmware function that was renamed away in v1.19 Phase 104:

```
$ git -C firestarter grep -rn 'flash4_page_size' src/ include/
(no output)
$ git -C firestarter grep -rn 'flash_5v_page_page_size' src/
src/proms/flash_5v_page.cpp:27:static uint32_t flash_5v_page_page_size(uint32_t mem_size) {
src/proms/flash_5v_page.cpp:80:    uint32_t page_size = flash_5v_page_page_size(handle->mem_size);
```

Stale references: `tools/build_db.py:125`, `firestarter/database.py:416`, `firestarter/constants.py:147`. All three say absent chips "ride the firmware `flash4_page_size(mem_size)` heuristic" — which after this phase is **doubly** wrong for `0x0D` (the fallback becomes the named AT28C floor constant, and `flash_5v_page`'s heuristic never governed `0x0D` at all). These are one-line corrections that belong in this phase's diff because the phase edits all three files' neighbourhoods.

*(Bonus, same class: `platformio.ini:64-67`'s comment claims the host "sizes host->fw chunks to 1022 (1024-2: CRC8 + decoder NUL slot)". Measured: CAP-01 relocated the advertisement to the `MSG_OK_READY` ack, which carries `DATA_BUFFER_SIZE` **verbatim** — `firestarter.cpp:209-210` — and `_calculate_buffer_size()` returns it unmodified (`eprom_operations.py:436-442`). The chunk is 512 or 1024, not 1022. See §R10c.)*

---

## D-01 Verification (independent re-measurement)

Read-only replication of `build_db.py:450-474`'s INFOIC2PLUS filter plus `:718-724`'s `part_number` normalisation, joined against the live `chip_database.json`. **Nothing was written; `build_db.py` was never invoked.**

**Pinned source verified first:**
```
$ ls -la /tmp/.../scratchpad/infoic_fresh.xml && md5sum ...
-rw-r--r-- 1 vscode vscode 17861009 Aug 19 13:40 infoic_fresh.xml
b4548e57c4f6c6c8c4f7387add03fa77  infoic_fresh.xml
```
Both the byte count (17,861,009) and md5 match CONTEXT.md's pinned values. `[VERIFIED: local md5sum + stat]`

**Join integrity:**
```
INFOIC2PLUS <database> sections matched: 1
upstream filter-passing unique (mfg, normalized-name) keys: 766
keys with >1 upstream <ic>: 1
chip_database.json rows: 746
algorithm==13 rows: 84
  matched: 84   unmatched: 0
```

> **Join-key gotcha for the planner.** A naive `(mfg, ic.get("name"))` join misses 53 of the 84, because the upstream name carries `@PACKAGE` aliases (`AT28C256,AT28C256@SOIC28,AT28C256E,...`) that `build_db.py:718-724` strips, dedupes and rejoins. Any future re-measurement must replicate that normalisation verbatim or it will silently under-count. This is a live instance of the same class of trap as the `firestarter` name collision.

### The four-way provenance table — reproduces CONTEXT.md digit for digit

```
=== D-01's four-way provenance table (MEASURED) ===
  0x07: 1->14 · 16->1 · 32->8 · 64->22 · 128->1 · 256->1   (total 47)
  0x0B: 1->17 · 16->2                                      (total 19)
  0x0D: 64->3 · 128->15                                    (total 18)
```

47 + 19 + 18 = 84. ✓  66 promoted + 18 native = 84. ✓  D-04's "11 rows at 16/32" = 3 at 16 (1 × `0x07` + 2 × `0x0B`) + 8 at 32 = **11**. ✓  D-04's "31 at raw 1 (14 upstream `0x07`, 17 upstream `0x0B`)" = **31**. ✓

### The 15 movers and 3 no-change rows — byte-identical to CONTEXT.md's lists

```
=== upstream-native 0x0D: 18  movers: 15  no-change@64: 3 ===
--- MOVERS (page -> 128) ---
  ATMEL            AT28C010,AT28C010E              upstream_page=128 db_raw=128 size=131072
  ATMEL            AT28C040,AT28C040E              upstream_page=128 db_raw=128 size=524288
  ATMEL            AT28LV010                       upstream_page=128 db_raw=128 size=131072
  ATMEL            AT28MC020                       upstream_page=128 db_raw=128 size=262144
  ATMEL            AT28MC040                       upstream_page=128 db_raw=128 size=524288
  CATALYST(CSI)    CAT28C010                       upstream_page=128 db_raw=128 size=131072
  CATALYST(CSI)    CAT28C020                       upstream_page=128 db_raw=128 size=262144
  CATALYST(CSI)    CAT28C040                       upstream_page=128 db_raw=128 size=524288
  CATALYST(CSI)    CAT28C512                       upstream_page=128 db_raw=128 size=65536
  MAXWELL          28C010,28C010T,28C011,28C011T   upstream_page=128 db_raw=128 size=131072
  SGS-THOMSON      M28010                          upstream_page=128 db_raw=128 size=131072
  ST               M28010                          upstream_page=128 db_raw=128 size=131072
  WED              WE512K8                         upstream_page=128 db_raw=128 size=524288
  WED              WME128K8                        upstream_page=128 db_raw=128 size=131072
  XICOR            X28C010                         upstream_page=128 db_raw=128 size=131072
--- NO-CHANGE (page == 64) ---
  ATMEL            AT28MC010                       upstream_page= 64 db_raw= 64 size=131072
  WED              WE128K8                         upstream_page= 64 db_raw= 64 size=131072
  WED              WE256K8                         upstream_page= 64 db_raw= 64 size=262144
```

**`infoic_page_size_raw` fidelity: 0 mismatches across all 84.** ✓ D-01's "faithful copy" claim confirmed — there is no decode bug here.

**D-01's same-density-different-page argument survives:** `AT28MC010` (131072 B, page 64) and `AT28C010` (131072 B, page 128) are **both** upstream-native `0x0D` and both in the delivered set. So the reasoning `eeprom_28c.cpp:22-25` rests on is fully preserved by the provenance rule, and the corrected comment can keep citing that pair.

### The two FRAM rows (D-04 deliverable 2) — confirmed, with the 3.3 V detail

```
  CYPRESS      FM28V020     upstream_proto=0x07 upstream_page=128 type=EEPROM vcc_mv=5000 vpp_mv=12000
  FUJITSU      MB85R256H    upstream_proto=0x07 upstream_page=256 type=EEPROM vcc_mv=3300 vpp_mv=12000
```
`MB85R256H` is the 3.3 V part carrying `vpp_mv 12000`. Both are upstream `0x07`, so the provenance rule excludes both — exactly the outcome D-01 was chosen for.

### Measured Non-Claims (Evidence Ceiling, load-bearing)

**AT28C256 — the gh#21 part — is a PROMOTED row and this phase cannot touch it.**
```
=== AT28C256 (gh#21 part) provenance ===
  ATMEL AT28C256,AT28C256E,AT28C256F,AT28HC256,AT28HC256E,AT28HC256F,AT28HC256L
    upstream_proto=0x07  upstream_page=64  db_raw=64  db_algorithm=13  support_status=supported
```
Its upstream `<ic>` carries `protocol_id="0x07"` and `page_size="0x0040"`. Under D-01 it receives **no** emitted `page_size`, keeps the 64-byte floor, and its wire dict is byte-unchanged. `[VERIFIED: pinned infoic.xml join + live chip_database.json]`

**No attribute in `infoic.xml` corroborates `page_size`** — the traps, re-measured:
```
  write_buffer_size: {128: 46, 32: 33, 64: 4, 256: 1}
  read_buffer_size : {512: 58, 2048: 18, 128: 8}
  pages_per_block  : {0: 84}
  AT28C256 write_buffer_size=128 (datasheet page is 64)
```
`write_buffer_size` matches CONTEXT.md's `{128×46, 32×33, 64×4, 256×1}` exactly. `pages_per_block` is 0 on all 84. *Minor correction:* CONTEXT.md says `read_buffer_size` "is the same shape" — measured, it takes a **different** value set (`{512, 2048, 128}`); it is the same *kind* of field (a programmer buffer), not the same distribution. Say "same kind", not "same shape".

**Candidate delivered values and the D-07 invariant:**
```
  candidate delivered values (native 0x0D): [64, 128]  all powers of two in [1,512]: True
  page_size values emitted TODAY across all 746: [128, 256]  n= 2
```

### The `_PAGE_SIZE_BY_PART` collision question (R5) — answered: NO collision possible

```
=== curated _PAGE_SIZE_BY_PART rows ===
  WINBOND  W29C020,W29C020C,W29C022  db_algorithm=5  emitted_page_size=128  raw=128  upstream_proto=0x05
  WINBOND  W29C040,W29C042           db_algorithm=5  emitted_page_size=256  raw=256  upstream_proto=0x05
```
Both curated rows are upstream `protocol_id = 0x05`. The provenance rule keys on `proto_id == 0x0D`. **The two sets are disjoint by construction** — no row can satisfy both conditions, so the emitter needs no precedence rule between them (though writing the curated arm first, as it is today, keeps the diff minimal and the intent legible).

Both curated values also agree with `flash_5v_page_page_size()`'s band table (`flash_5v_page.cpp:27-31`: `≤65536→64`, `≤262144→128`, `else→256`): `W29C020` is 262144 → 128 ✓, `W29C040` is 524288 → 256 ✓. This is the measurement behind D-08 — the wire field and the frozen heuristic already agree for both rows, so leaving `flash_5v_page.cpp` alone changes nothing observable.

### `tools/extra_chips.json` — the second emission path (Phase 148 finding)

Measured contents: **exactly 2 rows**, both under `"TEXAS INSTRUMENTS"` — part numbers `2516` and `2532`, `"source": "non-upstream-supplement"`, `programming.algorithm: 11` (`0x0B`), `pulse_duration_us: 500`, `verification_status: "UNVERIFIED"`.

- Neither carries `page_size` **or** `infoic_page_size_raw`. ✓ Confirms D-02's "the two `tools/extra_chips.json` rows that lack page keys" and explains why `.get`-guarded access host-side is load-bearing.
- Both are **authored** rows: they bypass `classify()`, the XML decode loop, and the emitter entirely. So `extra_chips.json` **can** technically inject a `page_size` (nothing schema-validates against it), and doing so would **bypass the provenance rule completely**.
- **Planner action:** D-01's provenance rule is unenforced against this path. A cheap host test asserting no `extra_chips.json` row carries `page_size` (or, more usefully, that every emitted `page_size` in the built DB is either a `_PAGE_SIZE_BY_PART` row or an upstream-native `0x0D` row) closes the hole for zero AVR bytes and folds naturally into D-07's exhaustive host proof.

---

## R2 — The Phase 44 optional-key precedent, line for line

The five-part shape, all citations from the live firmware tree (`firestarter/` @ `6992271`, byte-identical to `origin/beta` apart from `version.h`).

### (a) PROGMEM key string + `key_parsers[]` row

```c
// firestarter/src/json_parser.c:75-77
/* Phase 44 — host-tunable read-timing knobs (D-04 sweep params) */
const char key_read_settling[] PROGMEM = "read-settling-delay";
const char key_read_strobe[]   PROGMEM = "read-strobe-us";

// firestarter/src/json_parser.c:91
typedef struct {
    PGM_P key;
    bool (*parser_func)(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);
} key_parser_t;

static const key_parser_t key_parsers[] PROGMEM = {
    {key_mem_size, get_memory_size}, {key_address, get_address},         {key_flags, get_flags},
    {key_chip_id, get_chip_id},      {key_pin_count, get_pin_count},     {key_pulse_delay, get_delay},
    {key_vpp_mv, get_vpp_mv},        {key_algorithm, get_algorithm},
    /* Phase 44 — read-timing sweep knobs (RCA-01 causal proof, D-04) */
    {key_read_settling, get_read_settling},                              {key_read_strobe, get_read_strobe},
};
```

**The table is self-sizing.** The dispatch loop is `for (size_t j = 0; j < sizeof(key_parsers) / sizeof(key_parsers[0]); j++)` at `json_parser.c:301` — adding a row needs **no** count constant update anywhere. `[VERIFIED: json_parser.c:301]`

**Where the PROGMEM string table lives:** the key strings are file-scope `const char[] PROGMEM` globals at `json_parser.c:67-77` (8 pre-existing + 2 Phase 44 = 10 today). `key_parsers[]` itself is `static const ... PROGMEM` and is read through `pgm_read_ptr` at `:114` and `:116`.

### (b) The `get_*` function + forward declaration

```c
// firestarter/src/json_parser.c:20-19  (forward declarations, alongside 8 siblings)
bool get_read_settling(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);
bool get_read_strobe(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);

// firestarter/src/json_parser.c:348-357
#define READ_TIMING_MAX_US 1000UL   /* T-44-01 sane max (~1ms); caps both knobs */

bool get_read_settling(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    if (jsoneq(json, &tokens[pos], "read-settling-delay") == 0) {
        unsigned long v = simple_strtoul(json + tokens[pos + 1].start);
        handle->read_settling_us = (uint32_t)(v > READ_TIMING_MAX_US ? READ_TIMING_MAX_US : v);
        return 1;
    }
    return 0;
}
```

Note the **two idioms** available:
- **Plain store** — the `extract_long` / `extract_int` macro (`json_parser.c:459-469`), used by 11 of the 13 getters, e.g. `get_chip_id` at `:296-298`: `extract_int("chip-id", handle->chip_id);` — a **one-line** function body.
- **Store-with-clamp** — the hand-written form above, used by exactly the two Phase 44 knobs, because they need a cap at parse time.

**Recommendation for the planner:** use the **plain `extract_int` form** for `page-size` and do the validation in the handler, because D-07 locates validation in `eeprom28c_write_init`, not at parse time. `extract_int` is `#define extract_int(element, register) extract_long(element, register)` (`:282`), and `extract_long` uses `simple_strtoul` (`:37-45`), which handles positive decimals only — fine for a page size. This keeps `json_parse` algorithm-agnostic exactly as D-05 requires, and costs the fewest bytes.

### (c) The `firestarter_handle_t` field

```c
// firestarter/include/firestarter.h:188-224 (excerpt :192-204)
    uint32_t protocol;
    uint8_t pins;
    uint32_t mem_size;
    uint32_t address;              // <- uint32_t; the flush test's operand
    uint16_t vpp_mv;
    uint32_t pulse_delay;
    uint32_t read_settling_us;   /* address-settling delay before /CE assert (µs; 0 = no settling delay) */
    uint32_t read_strobe_us;     /* /CE read-strobe pulse width (µs; 0 = use default 3µs) */
    uint32_t ctrl_flags;
    uint16_t chip_id;
    char data_buffer[DATA_BUFFER_SIZE];
```
The struct closes at `firestarter.h:224`. `chip_id` at `:201` is the `uint16_t` precedent for the discretionary field width; `vpp_mv` at `:196` is a second.

### (d) The optional-key reset in `json_parse` (D-05's precedent)

```c
// firestarter/src/json_parser.c:164-278
int json_parse(const char* json, jsmntok_t* tokens, int token_count, firestarter_handle_t* handle) {
    handle->address = 0;
    handle->ctrl_flags = 0;
    handle->bus_config.rw_line = 0xFF;
    handle->bus_config.vpp_line = 0xFF;
    handle->bus_config.address_lines[0] = 0xFF;
    handle->bus_config.address_mask = 0;
    handle->bus_config.static_high_mask = 0;
    handle->chip_id = 0;                      // <- :89, D-05's exact precedent
```
*(CONTEXT.md cites `:85-95`; the precise reset block is `:82-89`, and `chip_id`'s reset is line **89**.)*

**Why the reset is load-bearing — confirmed by measurement.** `firestarter_handle_t handle;` is a single file-scope global at `firestarter.cpp:33` with **no** per-command `memset`, and `json_parse` is called exactly once per command from `parse_json` (`firestarter.cpp:75`), which `init_programmer_framed` calls at `:131` from the `CMD_IDLE` branch (`:332`). So without a reset, a `page_size` parsed for AT28C010 (128) persists into the next command for a floor chip — making "absent ⇒ 64" false in practice. ✓ D-05 confirmed.

**Note the Phase 44 knobs are NOT reset** — `read_settling_us` / `read_strobe_us` do not appear in the `:82-89` block. They get away with it because both treat 0 as "use the default", so a stale non-zero value is a *behaviour* bug the same way `page_size` would be. This is a latent instance of the same defect one field over; not this phase's business, but worth a one-line note in `149-PAGE-SIZE.md` since the phase touches this exact block. `[MEASURED: json_parser.c:271-278 vs :198-199]`

### (e) The paired `constants.py` key + sync note — and it is currently FALSE

```python
# firestarter_app/firestarter/constants.py:137-148  (verbatim)

# Dev sweep knobs — Firmware sync: json_parser.c (key_read_settling, key_read_strobe)
# JSON key name strings for host-tunable read-timing parameters.
# MUST stay in sync with the PROGMEM key strings in firmware json_parser.c.
# Used by consistency_check_eprom() to emit knob values in per-read JSON commands.
JSON_KEY_READ_SETTLING_DELAY = "read-settling-delay"
JSON_KEY_READ_STROBE_US = "read-strobe-us"
# Per-chip page size wire field (PGSZ-03 / CR-01) — Firmware sync: json_parser.c (key_page_size)
# Emitted by eprom_operations.py only when the DB supplies a datasheet-sourced page_size
# (emit-when-present, mirrors read-strobe-us pattern). When absent, firmware falls back
# to flash4_page_size(mem_size) heuristic. 0 = use firmware default.
JSON_KEY_PAGE_SIZE = "page-size"
```

**Confirmed FALSE, twice over:**
1. `key_page_size` does not exist in the firmware. `grep -n 'key_page_' firestarter/src/json_parser.c` → zero hits (the only `key_*` PROGMEM names are `key_mem_size`, `key_address`, `key_flags`, `key_chip_id`, `key_pin_count`, `key_pulse_delay`, `key_vpp_mv`, `key_algorithm`, `key_read_settling`, `key_read_strobe`). ✓ D-18's premise.
2. `flash4_page_size` does not exist either (§X-5).

Also worth the planner's attention: the comment says "Emitted by `eprom_operations.py`". Measured, the emit is in **`database.py:552-553`** (`convert_to_programmer`); `eprom_operations.py` never mentions `page_size`. A third false clause in the same five-line comment. All three are one-line corrections in a block this phase must edit anyway.

**Only 3 `JSON_KEY_*` constants exist** (`constants.py:142`, `:144`, `:149`) — so the parity test's surface is small and enumerable.

### Byte cost of a comparable key

**UNVERIFIED — planner must confirm by measurement.** Phase 44 added *two* keys plus two `uint32_t` handle fields plus a clamp plus read-loop instrumentation in `memory_get_data()` in one commit, so git history does not isolate a single key's cost. No isolated `git show --stat` gives a per-key flash figure.

Structural estimate for guidance only (`[ASSUMED]`): one PROGMEM key string (`"page-size"` = 10 B incl. NUL), one `key_parsers[]` row (2 × 2 B = 4 B in PROGMEM on AVR), one `extract_int`-shaped getter (a handful of instructions), one handle field (2 B RAM if `uint16_t`), one reset line, and the mask resolve + AND in the handler. **The plan must measure, not estimate** — D-13's cold before/after is the only acceptable source, and D-12's exemption size cannot be chosen until that measurement exists. This is the single largest scheduling constraint in the phase: **the exemption constant's value is unknown until after the firmware edit is built.**

---

## R3 — The flush loop and the mask (D-06)

### (a) The floor, its comment, and the single flush site

```c
// firestarter/src/proms/eeprom_28c.cpp:19-33
/* PAGE_SIZE 64 is a deliberate CONSERVATIVE FLOOR (D-13), not an unexamined
 * default. A mem_size-derived band table (the shape flash_5v_page.cpp's
 * flash_5v_page_page_size() uses -- READ-ONLY ANALOG, FIX-04 frozen -- NOT
 * adopted here) would be WRONG for 0x0D: the pinned infoic.xml (commit
 * a8efaedc, <database type='INFOIC2PLUS'>) records AT28MC010 at 128 KB with
 * page_size = 0x0040 (64) while AT28C010 at the SAME 128 KB density carries
 * 0x0080 (128) -- same density, different page size, so density alone
 * cannot select the right value. 64 errs SAFE: a smaller flush granularity
 * issues two legal write cycles into one physical page and can never
 * overrun a page. It is self-checking once FIX-06's read-back lands (plan
 * 117-03), which verifies whatever granularity is actually used. The real
 * per-chip value is delivered by a separate, DEFERRED phase (infoic.xml ->
 * build_db.py -> chip_database.json -> wire -> json_parser.c -> handler;
 * 117-CONTEXT.md <deferred>; not yet inserted into ROADMAP.md). */
#define PAGE_SIZE 64
```

D-04 rewrites the `:26-28` clause ("64 errs SAFE … can never overrun a page") to say **unproven** for the 11 promoted 16/32 rows. The `:22-25` density argument stays true and is independently re-verified in §D-01 Verification. The `:30-32` sentence ("delivered by a separate, DEFERRED phase … not yet inserted into ROADMAP.md") is what **this phase closes** and must be rewritten to a statement of fact, with the software-proven/unvalidated qualifier.

### (b) The load loop and `eeprom28c_write_execute`

```c
// firestarter/src/proms/eeprom_28c.cpp:622-657  (loop body verbatim)
    bool page_load_aborted = false;
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint32_t address = handle->address + i;          // :623  ABSOLUTE address
        uint8_t data = handle->data_buffer[i];
        handle->firestarter_set_data(handle, address, data);

        uint32_t page_load_now_us = micros();
        uint32_t page_load_interval_us = (uint32_t)(page_load_now_us - page_load_previous_us);
        if (page_load_interval_us > page_load_worst_us) {
            page_load_worst_us = page_load_interval_us;
        }
        page_load_previous_us = page_load_now_us;

        bool page_end = ((address + 1) % PAGE_SIZE) == 0;   // :634  THE ONLY code use
        bool last_byte = (i == handle->data_size - 1);
        if (page_end || last_byte) {
            if (!eeprom28c_wait_for_page_write(handle, address, data)) {   // :644
                page_load_aborted = true;
                break;
            }
            if (!eeprom28c_verify_page_readback(handle, window_start, i)) { // :648
                page_load_aborted = true;
                break;
            }
            window_start = i + 1;                                          // :652
        }
    }
    (void)page_load_aborted;
    LOG_ID_U32(MSG_INFO_PAGE_LOAD_WORST_US, page_load_worst_us);           // :656
}
```

| Fact | Value | Citation |
|---|---|---|
| Current flush expression | `((address + 1) % PAGE_SIZE) == 0` | `eeprom_28c.cpp:599` |
| Type of `handle->address` | `uint32_t` | `firestarter.h:195` |
| Type of the loop's `address` local | `uint32_t` | `eeprom_28c.cpp:623` |
| Other sites reading `PAGE_SIZE` in `src/` | **none** — `:634` is the only one | §X-4 grep |
| Other sites reading `PAGE_SIZE` in `src/proms/` | **none** | §X-4 grep |
| Function called once per flush | `eeprom28c_wait_for_page_write` (`:644`) + `eeprom28c_verify_page_readback` (`:648`) | `eeprom_28c.cpp:606,648` |

### (c) Where write-INIT lives, and the early-return trap

```
$ grep -n '^[a-zA-Z_].*(\|^static .*(' src/proms/eeprom_28c.cpp | grep -v ';$'
109:static void eeprom28c_emit_sdp_sequence_timed(...)
189:void configure_eeprom28c(firestarter_handle_t* handle) {
229:static void eeprom28c_check_chip_id(...)
298:static void eeprom28c_emit_command_sequence(...)
348:static void eeprom28c_wait_for_sdp_completion(...)
401:static void eeprom28c_emit_sdp_sequence_timed(...)
422:static void eeprom28c_sdp_unlock_execute(...)
441:static void eeprom28c_sdp_lock_execute(...)
448:void eeprom28c_write_init(firestarter_handle_t* handle) {
537:void eeprom28c_write_execute(firestarter_handle_t* handle) {
676:static bool eeprom28c_wait_for_page_write(...)
722:static bool eeprom28c_verify_page_readback(...)
```

`eeprom28c_write_init` is `:448-535`. **It has an early `return` at `:454`:**

```c
// firestarter/src/proms/eeprom_28c.cpp:420-428
void eeprom28c_write_init(firestarter_handle_t* handle) {
    if (handle->chip_id > 0) {
        eeprom28c_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;                                     // :454  EARLY RETURN
        }
    }
```

**Planner precision point.** D-06 says "resolve and store the validated mask once at write-INIT". If the resolution is placed **after** `:456`, it is skipped on a chip-ID mismatch. That path also aborts the write (`response_code == RESPONSE_CODE_ERROR`), so it is not exploitable today — but it makes the mask's initialisation *conditional*, which a future refactor can turn into a live defect, and it makes a native test harder to write. **Place the mask resolution as the first statement of `eeprom28c_write_init`, above the `chip_id` block**, so it is unconditional by construction.

**Second option worth naming:** `configure_eeprom28c` (`:189-221`) also runs exactly once per command, immediately after `json_parse` (via `configure_memory` at `firestarter.cpp:93`), and is where `handle->pulse_delay = 0` is already set (`:192`). Resolving the mask there is equally unconditional and arguably better-placed (it is the "resolve this protocol's parameters" function), but it runs for **every** `0x0D` command including `CMD_BLANK_CHECK` / `CMD_SDP_UNLOCK` / `CMD_SDP_LOCK`, which do not use the mask. Either site satisfies D-06; `write_init`-top is the narrower blast radius, `configure_eeprom28c` is the more idiomatic home. **Claude's discretion; the plan should name which and why.**

**Storage lifetime constraint (measured):** `eeprom28c_write_execute` is `firestarter_operation_main` (`:209`) and runs **once per data block**, while `write_init` is `firestarter_operation_init` (`:208`) and runs **once per operation**. So a mask resolved in `write_init` must survive across repeated `write_execute` calls. Both viable stores cost 2 B: a handle field (visible to native tests, which construct handles directly — see §R4) or a file-scope `static` in `eeprom_28c.cpp` (invisible to native tests, which would then have to observe the mask only through flush cadence). **A handle field is strongly preferable** because it keeps D-09's assertion direct and keeps `test_val_eeprom28c`'s existing `firestarter_handle_t h = {}` construction sufficient.

### (d) Mask ≡ mod, measured on seven geometries (D-06)

Exact replica of `:623`/`:634`/`:635`/`:636`, run both ways:

```
== MOD form (today's production, PAGE_SIZE literal) ==
today  page64      base=0    size=128  page=64   -> [0..63@a63] [64..127@a127]  flushes=2
mover  page128     base=0    size=128  page=128  -> [0..127@a127]  flushes=1
today  page64      base=0    size=512  page=64   -> 8 windows  flushes=8
mover  page128     base=0    size=512  page=128  -> [0..127@a127] [128..255@a255] [256..383@a383] [384..511@a511]  flushes=4
unaligned page64   base=56   size=16   page=64   -> [0..7@a63] [8..15@a71]  flushes=2
unaligned page128  base=56   size=16   page=128  -> [0..15@a71]  flushes=1
unaligned page128  base=100  size=200  page=128  -> [0..27@a127] [28..155@a255] [156..199@a299]  flushes=3
== MASK form (D-06) -- byte-identical to MOD above on all seven ==
   (identical output, line for line)
== degenerate page_size=1 -> mask 0 ==
page1 mask0        base=0    size=8    page=1    -> 8 single-byte windows  flushes=8
```

**Confirmed:**
- `((address + 1) & (page_size - 1)) == 0` is behaviour-identical to `((address + 1) % page_size) == 0` for every power-of-two `page_size`, **including unaligned bases** — the `base=100, size=200, page=128` case flushes at absolute addresses 127, 255, 299, i.e. on true chip page boundaries with a short first window (28 bytes) and a short last window (44 bytes). ✓ D-06's "flushes align to true chip page boundaries even when `handle->address` is unaligned" is verified, not assumed.
- The degenerate mask `0` (from `page_size == 1`) flushes **every byte** and cannot overrun. ✓ D-06's degenerate claim verified.
- `__udivmodsi4` avoidance: `%` on a `uint32_t` by a **runtime** value pulls the AVR division helper in; `%` by a compile-time constant 64 does not (gcc strength-reduces it to a mask). So the mask form is not merely equal-cost — it is what **keeps** the cost equal once the divisor becomes a variable. `[ASSUMED — standard avr-gcc strength reduction; the cold before/after measurement is the proof, and D-13 already requires it]`

**Concrete D-09 test geometry (recommended):** base 0, `data_size` 128 → **2 flushes at page 64 vs 1 flush at page 128**. 128 fits `DATA_BUFFER_SIZE = 512` on native (§R10c). The 64-case number is what the *absent-field* leg must reproduce.

---

## R4 — The native test surface (D-09, D-11, D-15)

### (a) A JSON-parser native suite EXISTS and is in `test_filter` — D-11 and D-15 do not conflict

**`native/avr/test_read_timing` is the suite.** `platformio.ini:107` lists it in `[env:native]`'s `test_filter` (17 entries, `:102-119`). It is a full `json_parse` harness:

```cpp
// firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp:61-81
/* Build a zero-initialized handle suitable for JSON parse tests. */
static firestarter_handle_t make_handle(uint8_t cmd) {
    firestarter_handle_t h = {};   /* zero-init: ensures new fields default 0 */
    h.cmd = cmd;
    h.response_code = RESPONSE_CODE_OK;
    return h;
}

/* Helper: parse a JSON string into a handle, return the json_parse result.
 * Note: json_init() uses sizeof(tokens)/sizeof(tokens[0]) which is wrong when
 * tokens is a pointer arg (evaluates to pointer-size/element-size on host).
 * Call jsmn_parse directly with NUMBER_JSNM_TOKENS to avoid the off-by-many. */
static int parse_json(const char* json_str, firestarter_handle_t* handle) {
    jsmntok_t tokens[NUMBER_JSNM_TOKENS];
    jsmn_parser parser;
    jsmn_init(&parser);
    int token_count = jsmn_parse(&parser, json_str, strlen(json_str),
                                 tokens, NUMBER_JSNM_TOKENS);
    if (token_count < 0) return token_count;
    return json_parse(json_str, tokens, token_count, handle);
}
```

Its 4 existing cases (`:116-124`) are exactly the shape D-05/D-11 need:
| Case | Line | What it proves | Page-size analogue |
|---|---|---|---|
| `test_read_settling_us_parsed_from_json` | `:76-82` | key → field stored | `{"cmd":2,"page-size":128}` → field == 128 |
| `test_read_strobe_us_parsed_from_json` | `:85-91` | second key stored | — |
| `test_read_timing_fields_default_zero_when_absent` | `:94-101` | **absent key → 0** | D-05's reset leg |
| `test_read_settling_us_capped_at_max` | `:105-114` | parse-time clamp | *(not used — D-07 validates in the handler)* |

**So D-15 ("extend existing suites, no new suite") and D-11 are fully compatible.** No new translation unit, no new watermark measurement, no new `-I` entry in `platformio.ini`. Each new case is ~6 lines plus one `RUN_TEST` line.

**D-11's sharp form** (the unknown-key skip at `json_parser.c:320`): the existing absent-key case does **not** exercise it. The skip is about **token-walk desynchronisation** — `token_idx += 2` on an unrecognised key. So the test must place an unknown key *before* a known one and assert the known one still lands:

```cpp
/* D-11: a new host's unknown key must not desync the token walk. */
const char* json = "{\"cmd\":2,\"totally-unknown-key\":7,\"read-strobe-us\":25}";
/* assert rc == 0 AND h.read_strobe_us == 25 */
```
A version asserting only "no crash" would pass with a broken `token_idx` and is under-sampled. See §Validation Architecture.

### (b) Is flush/poll COUNT observable? — YES, but NOT via the bus recorder

This is the load-bearing question for D-09, and the answer requires care.

`test_val_eeprom28c/host_stubs.cpp:28` defines **only** `HOST_STUBS_RECORD_BUS`, exposing:
```cpp
// firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:44-48
extern "C" void clear_bus_recording();
extern "C" int  bus_recording_count();
extern "C" uint8_t recorded_reg(int i);
extern "C" uint8_t recorded_data(int i);
```
That recorder captures `(reg, data)` pairs from `rurp_write_to_register` — **register writes**, capped at 256 entries (`:208`). It does **not** see reads.

But every write-path case in the suite **replaces the read seam with a mock**:
```cpp
// test_val_eeprom28c.cpp:98-103, 217
static uint8_t mock_get_data_planted(firestarter_handle_t*, uint32_t address) { ... }
...
h.firestarter_get_data = mock_get_data_planted;
```
And `eeprom28c_wait_for_page_write` reads exclusively through that seam:
```c
// firestarter/src/proms/eeprom_28c.cpp:676-681
static bool eeprom28c_wait_for_page_write(firestarter_handle_t* handle, uint32_t address, uint8_t expected) {
    uint8_t observed = 0;
    for (uint16_t j = 0; j < AT28C_PAGE_POLL_MAX_READS; j++) {
        delayMicroseconds(10);
        observed = handle->firestarter_get_data(handle, address);
```
`eeprom_28c.cpp:672-675` states this explicitly: *"Every read goes through `handle->firestarter_get_data` (`memory_get_data`) -- never a direct `rurp_*` read, never `fu_flash_data_poll()`"*.

**Therefore flush count IS observable — via a test-local counter inside the mock `get_data`**, keyed on address. Concretely: record every queried address in a suite-local array (or just count calls, and separately record the set of addresses at which a *first* call occurred), and the flush points are recoverable exactly, because `wait_for_page_write` is called once per flush at the flush address and does a double-read there (`eeprom_28c.cpp:629-632`, the double-read idiom).

**Two known traps, and how each lands here:**
- *Native trace stubs record NO time* — `host_stubs_common.inc:137-144` states `delay()` / `delayMicroseconds()` are **not stubbed anywhere** in the shared include (they are ArduinoFake free functions, `.AlwaysReturn()`-mocked in each suite's `setUp()`). ✓ **Does not weaken D-09**, which counts flushes and never times them. `test_val_eeprom28c.cpp:69-79` already mocks `delayMicroseconds`, `delay`, `millis`, and `micros` (all `AlwaysReturn(0)`) precisely so the write path is reachable without timing.
- *Native stubs can MISS register-write elision unless `rurp_register_utils.h` is included* — `test_val_eeprom28c` does **not** define `HOST_STUBS_REAL_REGISTER_UTILS` (only `HOST_STUBS_RECORD_BUS`), so its `rurp_write_to_register` is the stub recorder with **no** cache-compare elision (`host_stubs_common.inc:59-84`). ✓ **Does not weaken D-09** either, because D-09's observable is the *read* seam (the mock `get_data`), not the register recorder. It **would** weaken any attempt to count flushes from `bus_recording_count()` — so the plan must not take that route.

**Recommendation:** D-09's assertion should be a **flush-count** assertion derived from the mock `get_data` call log, not a `bus_recording_count()` delta and not a timing assertion. Assert three numbers on one geometry: `page 64 → 2 flushes`, `page 128 → 1 flush`, `field absent → 2 flushes` (identical to the 64 case). The third is PGSZ-02's fallback leg and the second is criterion 1's "observed to deliver 128".

### (c) Handle construction in these suites

```cpp
// firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:111-125
static firestarter_handle_t make_write_handle(uint32_t address, uint32_t data_size) {
    firestarter_handle_t h = {};
    h.protocol = 0x0D;
    h.cmd = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id = 0;
    h.mem_size = SDP_BUS_CONFIGS[0].mem_size;        // AT28C256 / DIP28_28C256, 32768
    h.bus_config = SDP_BUS_CONFIGS[0].bus_config;
    h.address = address;
    h.data_size = data_size;
    for (uint32_t k = 0; k < data_size; k++) {
        h.data_buffer[k] = (char)(0x10 + k);
    }
    return h;
}
```
`firestarter_handle_t h = {}` zero-inits, so a **new handle field defaults to 0** with no factory change — which is exactly the "field absent" state D-05/PGSZ-02 need. Setting `h.<page_field> = 128` before `configure_memory(&h)` gives the delivered case. `h.chip_id = 0` also means `write_init`'s `:451` branch is skipped, so a mask resolved at the **top** of `write_init` is reached and a mask resolved **after** `:456` is also reached here — the early-return trap is invisible to this suite, which is another reason to place the resolution at the top by construction rather than by test.

The existing cases drive `h.firestarter_operation_main(&h)` directly (`:218`, `:249`, `:269`) after `configure_memory(&h)`. **They never call `firestarter_operation_init`** — so if the mask is resolved in `write_init`, every existing case would run with an unresolved (zero) mask. **This is a real hazard:** mask 0 flushes every byte, so `test_fix06_page_boundary_window_readback` (`:260-302`, which asserts two-window behaviour at base 56 / size 16) would change behaviour and could go RED or, worse, GREEN for the wrong reason.

**Two ways out; the plan must pick one explicitly:**
1. Resolve the mask in **`configure_eeprom28c`** (which every existing case *does* call, via `configure_memory`). Existing cases then get the 64 default with no edit.
2. Resolve in `write_init` **and** make the consumer fall back at point of use (`mask == 0 ⇒ use the fallback constant`), so an un-initialised mask is indistinguishable from the absent-field case. This is one extra `if` in the hot loop's setup — not per byte, if hoisted above the loop.

Option 1 is cheaper and touches no existing test. **Recommend option 1**, with D-06's "at write-INIT" read as "once per operation, before the loop" rather than literally inside `eeprom28c_write_init`. Flag it in `149-PAGE-SIZE.md` as a mechanism-corrected/intent-satisfied note, per this project's established practice.

### (d) Both suites are in `test_filter`, both run in CI, both green here

`platformio.ini:102-119` `test_filter` (17 entries) includes `native/avr/test_read_timing` (`:107`), `native/avr/test_val_eeprom28c` (`:112`), and `native/avr/test_eeprom28c_sdp` (`:118`). ✓ CONTEXT.md confirmed.

**CI legs — measured, and this CORRECTS project memory:**
```
$ grep -n 'pio test\|pio run' .github/workflows/build.yml
142:        run: pio test -e native
155:        run: pio test -e native_nodevtools
193:        run: pio run
```
`[env:native]` **does** run in CI (`build.yml:142`), and so does `native_nodevtools` (`:155`). So D-15's "both are already in `[env:native]`'s `test_filter`, so they run in CI" is **correct**. Project memory's note that `native_params_v131` / `native_trace_v131` run in no CI leg remains true — those are separate envs and appear in zero workflow files, along with `native_loop_v131` and `native_pinmap_provisional`:
```
$ grep -rn 'native_pinmap_provisional\|native_params_v131\|native_trace_v131\|native_loop_v131' .github/workflows/
(no output)
```

**Live run in this devcontainer:**
```
$ pio test -e native -f native/avr/test_val_eeprom28c -f native/avr/test_read_timing
test_val_eeprom28c.cpp:309: test_eeprom28c_read_configure_no_vpp                                    [PASSED]
test_val_eeprom28c.cpp:310: test_eeprom28c_write_configure_no_vpp                                   [PASSED]
test_val_eeprom28c.cpp:311: test_eeprom28c_blank_check_configure_no_vpp                             [PASSED]
test_val_eeprom28c.cpp:314: test_fix06_planted_partial_write_fails_fixed_path_and_passes_legacy_poll [PASSED]
test_val_eeprom28c.cpp:315: test_fix06_clean_page_write_succeeds_isolation_control                  [PASSED]
test_val_eeprom28c.cpp:316: test_fix06_page_boundary_window_readback                                [PASSED]
------- native:native/avr/test_val_eeprom28c [PASSED] Took 1.94 seconds -------
================= 10 test cases: 10 succeeded in 00:00:05.777 =================
RC=0
```
4 cases in `test_read_timing` + 6 in `test_val_eeprom28c` = 10, ~6 s. Writes only into gitignored `.pio/` (`.gitignore:1`); firmware porcelain confirmed empty afterwards.

**Full-env baseline for D-14 (from `size_baseline.json`):** `native` and `native_nodevtools` each `{cases: 141, succeeded: 141, suites: 17, all_passed: true}`; `native_pinmap_provisional` `{cases: 10, suites: 1}`. Adding N cases to existing suites moves `cases` from 141 to 141+N on **both** pinned envs while `suites` stays **17** — `envs_agree` must stay `true`. `check_size_baseline.py` reads these, so D-14's phase-end update must bump both `cases` and `succeeded` on both envs by the same N. **A common miss: updating one env and not the other, which trips `envs_agree`.**

---

## R5 — The host emit rule (D-01 / D-02 / D-03)

### (a) `_PAGE_SIZE_BY_PART` — not to be extended

```python
# firestarter_app/tools/build_db.py:121-140
# PGSZ-01 / CR-01: datasheet-sourced per-chip page size map.
# Keyed on the canonical part number (first alias in the comma-separated list).
# Each entry carries a [CITED:] datasheet reference — DO NOT author [ASSUMED] values.
# Chips absent from this map omit the page_size field → firmware falls back to
# flash4_page_size(mem_size) heuristic (safe, proven-correct for these chips).   <- STALE (§X-5)
# Only in-repo datasheet PDFs are authoritative sources.
_PAGE_SIZE_BY_PART: dict[str, int] = {
    # [CITED: firestarter/datasheets/0x05-FLASH-AMD-STD/W29C040.pdf §6.2 ...]
    "W29C040": 256,
    # [CITED: firestarter/datasheets/0x05-FLASH-AMD-STD/W29C020.pdf §6.2 ...]
    "W29C020": 128,
}
```
2 entries, both algorithm `0x05`, both upstream `protocol_id 0x05`. **Not extended by this phase** (REQUIREMENTS.md §Out of Scope, DATA-04).

*Note the `:125` comment also contains the words "proven-correct" — if D-19's claim gate is ever pointed at `tools/`, that string is a `proven-unqualified` hit. It is not in D-19's target list, so this is informational only.*

### (b) `classify()` arm 2 — the promotion that makes 66 of 84 non-native

```python
# firestarter_app/tools/build_db.py:371-386
    # 2. 5V-EEPROM pinout clusters (was Rule 1 + Rule 2 / WARNING-5).
    #    These pinouts have no programming VPP; route to configure_eeprom28c (0x0D).
    if pinout_key == "DIP24_2816":
        return "EEPROM", 0x0D, pinout_key
    if proto_id in {0x07, 0x08, 0x0B} and (
        pinout_key in {"DIP28_28C64", "DIP28_28C256"}
        or (pinout_key == "DIP28_2764" and (flags & 0x10))
    ):
        return "EEPROM", 0x0D, pinout_key
```
`classify()` spans `:317-402`; arm 2 is `:371-386` (CONTEXT.md cites `:374-382` — the *condition* block; the `DIP24_2816` arm at `:380-381` is part of the same promotion). Arm 4 (`:393-394`) is where a **genuinely** upstream-`0x0D` row lands: `if proto_id in {0x05, 0x06, 0x0D, 0x10}: return "Flash/EEPROM", proto_id, pinout_key`.

**Key structural fact for the emitter:** `classify()` **returns the resolved algorithm but discards provenance**. The emitter cannot ask `classify()` "was this upstream-native?" — it must read `proto_id` directly. Which it can, because:

### (c) `proto_id` and `raw_page_size` are read off the same `<ic>` and ARE in scope at the emitter

```python
# firestarter_app/tools/build_db.py:477-490
                variant = int(ic.get("variant"), 16)
                proto_id = int(ic.get("protocol_id"), 16)              # :478
                flags = int(ic.get("flags"), 16)
                # PROV-01 (136.1-01): raw, un-curated upstream page_size attribute
                # off this SAME <ic> element. Deliberately NOT the same key as the
                # existing datasheet-curated _PAGE_SIZE_BY_PART / programming.page_size
                # mechanism a few dozen lines below -- same English word, two
                # different sources, never to be confused. This raw value is needed
                # downstream only as PROV-06's corroborating axis (b15 vs
                # infoic_page_size_raw > 1); it is not consulted by any ALLOW/REFUSE
                # decision anywhere in this codebase.
                raw_page_size = int(ic.get("page_size", "0x0"), 16)     # :490
```

Both are plain locals inside the `for ic in mfg.findall(".//ic")` body (`:455`), and the emitter at `:786-795` is inside the **same** loop body. **Verified in scope — no plumbing needed.** ✓

*(The `:485-486` comment "not consulted by any ALLOW/REFUSE decision anywhere in this codebase" becomes **false** the moment D-01's rule lands, because the rule consults `proto_id` and — depending on shape — `raw_page_size` as the value source. That comment must be updated in the same diff, or the file self-contradicts.)*

### (d) The emit site — exactly where D-01/D-02/D-03 land

```python
# firestarter_app/tools/build_db.py:779-796
                        "protect_off_before": True if (flags & 0x4000) else False,
                        "protect_on_after": True if (flags & 0x8000) else False,
                        "infoic_page_size_raw": raw_page_size,
                        # PGSZ-01 / CR-01: datasheet-sourced per-chip page size.
                        # Looked up by the FIRST alias of the comma-separated part
                        # name (canonical key). Absent chips omit the field entirely
                        # so they ride the firmware flash4_page_size() heuristic.   <- STALE (§X-5)
                        **(
                            {
                                "page_size": _PAGE_SIZE_BY_PART[
                                    name.split(",")[0].split("@")[0].strip()
                                ]
                            }
                            if name.split(",")[0].split("@")[0].strip()
                            in _PAGE_SIZE_BY_PART
                            else {}
                        ),
                    },
                    "pinout": pinout_key,
                }
```

A conditional dict-splat. The provenance arm is a second condition on the same splat (or a second splat immediately after). Because the two populations are **disjoint** (§D-01 Verification), ordering is a legibility choice, not a correctness one. Sketch:

```python
                        **(
                            {"page_size": _PAGE_SIZE_BY_PART[_canon]}
                            if _canon in _PAGE_SIZE_BY_PART
                            # D-01/D-03: provenance-keyed — the page_size attribute is
                            # meaningful for the algorithm that consumes it; a record
                            # filed under 0x07/0x0B is not evidence about a 28C page
                            # buffer. 18 upstream-native rows qualify (15 at 128, 3 at
                            # 64); the 66 promoted rows keep the firmware floor (D-04).
                            else {"page_size": raw_page_size}
                            if proto_id == 0x0D
                            else {}
                        ),
```
with `_canon = name.split(",")[0].split("@")[0].strip()` hoisted (it is currently computed **twice**, `:789` and `:792` — hoisting is a free readability win in a line the phase edits anyway).

**Guard-rail the plan should require:** the provenance arm must **not** filter on `raw_page_size != 64` (that is D-03's explicitly rejected direction). It also should not filter on `raw_page_size in (64, 128)` — even though that is measurably the only observed pair (§D-01 Verification) — because a future upstream bump would then silently drop a row. If a bound is wanted, the honest one is the D-07 invariant (power of two in `[1, 512]`), asserted **host-side as a test** rather than baked into the emitter as a silent filter. Otherwise the emitter and the test would encode the same rule twice.

### (e) D-02's "host needs ZERO code change" — CONFIRMED, with two precision corrections

```python
# firestarter_app/firestarter/database.py:414-419  (_map_data)
        # PGSZ-01 / CR-01: carry datasheet-sourced per-chip page_size when present.
        # Set by build_db.py only for chips with a [CITED:] datasheet entry; absent
        # for all other chips so they ride the firmware flash4_page_size() heuristic.  <- STALE
        page_size_val = programming.get("page_size")
        if page_size_val:                                   # :418  TRUTHINESS, not presence
            data["page_size"] = int(page_size_val)          # :419  internal key: page_size (underscore)
```
```python
# firestarter_app/firestarter/database.py:549-553  (convert_to_programmer)
        # PGSZ-03 / CR-01: emit page-size wire field only when the DB supplies a
        # datasheet-sourced per-chip page_size (emit-when-present, mirrors chip-id).
        # Absent chips send nothing → firmware uses flash4_page_size(mem_size) heuristic.  <- STALE
        if full_eprom_data.get("page_size"):                # :552
            programmer_data["page-size"] = full_eprom_data["page_size"]   # :553  WIRE key: page-size (hyphen)
```

**Confirmed:** no `KeyError` risk on the `extra_chips.json` rows; the wire key already exists; no `serial_comm.py` change (C-2 satisfied by inspection — the framing layer is agnostic to dict contents).

Two corrections to CONTEXT.md's citations, both minor but worth carrying into plan tasks:
1. CONTEXT.md says "`database.py:417` already carries `programming.page_size` into `_map_data` and `:552` already emits wire `page-size`, both via `.get`". Measured: the guards are **truthiness** (`if page_size_val:`, `if full_eprom_data.get("page_size"):`), not presence. Both delivered values (64, 128) are truthy so behaviour is identical — but a `page_size` of **0** would be silently dropped. This makes 0 an unreachable wire value host-side, which is a *convenient* accident (it means the firmware never has to distinguish "absent" from "0"), and it is worth stating as a measured property rather than leaving it as luck. The actual emit statement is `:553`, not `:552`.
2. **Two different key spellings in the same flow:** internal `page_size` (underscore, `:419`/`:552`) vs wire `page-size` (hyphen, `:553`). The firmware's PROGMEM string must match the **hyphen** form, and so must `constants.py`'s `JSON_KEY_PAGE_SIZE` (it does — `constants.py:148` is `"page-size"`). D-18's parity assertion must compare the hyphen form.

### (f) `extra_chips.json` and the provenance rule

See §D-01 Verification, final subsection. Summary for the planner: 2 authored rows, no page keys, bypasses the emitter and `classify()` entirely, **can** inject a `page_size` that bypasses D-01, and a one-assertion host test closes the hole.

---

## R6 — The wire golden delta fixture (D-17)

### (a) Golden shape and the exact comparison

```python
# firestarter_app/tests/test_wire_dict_equivalence.py:54-55
_HERE = Path(__file__).resolve().parent
_GOLDEN = _HERE / "golden" / "wire_dict_baseline.json"

# :153-165
def test_live_capture_matches_golden() -> None:
    doc = json.loads(_GOLDEN.read_text(encoding="utf-8"))
    recorded = doc["records"]
    live = _capture_wire_dicts(_REAL_DB)
    assert recorded == live, (
        "live 746-chip wire-dict capture drifted from "
        "tests/golden/wire_dict_baseline.json; "
        "if this is a legitimate wire-value change, Phase 148 is "
        "specifically forbidden to make it (D-14) -- a legitimate future "
        "wire change must re-capture the golden deliberately and say in the "
        "commit message which chips and which keys moved. "
        f"Diff: {_describe_record_diff(recorded, live)}"
    )
```

- File shape: `{"meta": {...}, "records": {"<mfg>|<part_number>|<i>": {<wire dict>}}}`, **746 records**. `[VERIFIED: json.load]`
- Comparison: a **single whole-dict equality** on `records`. Goes RED the moment 18 rows gain `page-size`. ✓ D-17's premise.
- The RED message is self-documenting: `_describe_record_diff` (`:101-131`) reports `changed={<record key>: [<differing wire keys>]}`, so the transcript names each of the 18 keys with `['page-size']`. Excellent for the seen-to-fail record.
- `test_wire_key_union_is_exactly_nine_keys` (`:173-183`) asserts the union equals `_EXPECTED_WIRE_KEYS` (`:62-72`), which **already contains `page-size`**. ✓ Stays GREEN with no edit. Key union stays 9. ✓ D-17 confirmed.
- Capture helper `_capture_wire_dicts` (`:82-98`) keys records `f"{mfg}|{pn}|{i}"` — never `pn` alone, because 65-69 records share a `part_number`.
- `_REAL_DB = EpromDatabase(skip_local_override=True)` at `:79` — module-level, `skip_local_override=True` is **mandatory**.

### (b) The 2 records carrying `page-size` today — exact keys

```
records carrying page-size TODAY:
  [('WINBOND|W29C020,W29C020C,W29C022|7', 128), ('WINBOND|W29C040,W29C042|8', 256)]
```
✓ CONTEXT.md's "2 rows carrying it today" confirmed, with the record keys resolved.

### (c) The 18 expected deltas — resolved golden record keys, ready to paste

All 18 resolved against the committed golden; **none carries `page-size` today** (verified per key):

```json
{
  "ATMEL|AT28C010,AT28C010E|22":              {"page-size": 128},
  "ATMEL|AT28C040,AT28C040E|25":              {"page-size": 128},
  "ATMEL|AT28LV010|34":                       {"page-size": 128},
  "ATMEL|AT28MC010|35":                       {"page-size": 64},
  "ATMEL|AT28MC020|36":                       {"page-size": 128},
  "ATMEL|AT28MC040|37":                       {"page-size": 128},
  "CATALYST(CSI)|CAT28C010|13":               {"page-size": 128},
  "CATALYST(CSI)|CAT28C020|14":               {"page-size": 128},
  "CATALYST(CSI)|CAT28C040|15":               {"page-size": 128},
  "CATALYST(CSI)|CAT28C512|12":               {"page-size": 128},
  "MAXWELL|28C010,28C010T,28C011,28C011T|0":  {"page-size": 128},
  "SGS-THOMSON|M28010|18":                    {"page-size": 128},
  "ST|M28010|15":                             {"page-size": 128},
  "WED|WE128K8|0":                            {"page-size": 64},
  "WED|WE256K8|1":                            {"page-size": 64},
  "WED|WE512K8|2":                            {"page-size": 128},
  "WED|WME128K8|3":                           {"page-size": 128},
  "XICOR|X28C010|5":                          {"page-size": 128}
}
```
`matched golden record keys: 18 / 18`. **Warning:** the `|<i>` suffix is a positional index within the manufacturer's list. If any future emitter change reorders or adds a row for these manufacturers, these keys shift. That is a *feature* for a golden (it forces a deliberate re-derivation) but the plan must generate this fixture from the golden programmatically, not transcribe it by hand.

### (d) Recommended fixture shape and location (Claude's discretion — a recommendation, not a mandate)

**Path:** `firestarter_app/tests/golden/wire_dict_expected_deltas_149.json`
Sibling of the golden it modifies, inside `tests/golden/` so it inherits the "no legitimate skip path" property `test_wire_dict_equivalence.py:38-42` relies on.

**Shape:**
```json
{
  "meta": {
    "phase": "149",
    "decision": "D-17 — the pre-149 golden is PRESERVED; this file is the committed expected-delta list",
    "provenance": "The 18 upstream-native protocol-0x0D rows (D-01). 15 gain page-size 128, 3 gain page-size 64. Generated from tests/golden/wire_dict_baseline.json, never transcribed.",
    "honesty": "software-proven and unvalidated on silicon",
    "how_to_update": "A new delta here must name the chips and the reason in the commit message. Growing this list without a provenance justification is the re-baselining D-17 exists to prevent."
  },
  "deltas": {
    "<record key>": {"page-size": 128}
  }
}
```

**Test change — minimum violence, four assertions instead of one:**
```python
def test_live_capture_matches_golden_plus_the_149_deltas() -> None:
    doc = json.loads(_GOLDEN.read_text(encoding="utf-8"))
    recorded = doc["records"]
    deltas = json.loads(_DELTAS_149.read_text(encoding="utf-8"))["deltas"]

    # 1. Anti-laundering: the golden itself is STILL the pre-149 capture.
    carriers = {k for k, w in recorded.items() if "page-size" in w}
    assert carriers == {"WINBOND|W29C020,W29C020C,W29C022|7",
                        "WINBOND|W29C040,W29C042|8"}, ...

    # 2. Every delta key exists in the golden and does NOT already carry the key.
    for key, patch in deltas.items():
        assert key in recorded, ...
        assert "page-size" not in recorded[key], ...

    # 3. Exact count — 18, not "at least".
    assert len(deltas) == 18, ...

    # 4. Golden PLUS exactly these deltas equals live.
    expected = copy.deepcopy(recorded)
    for key, patch in deltas.items():
        expected[key].update(patch)
    assert expected == live, f"Diff: {_describe_record_diff(expected, live)}"
```

Assertion 1 is the one that makes the fixture un-launderable: a future phase that re-captures the golden to make a failure disappear breaks it. Assertion 2 makes the fixture non-vacuous (a delta naming a key that already carries the value would prove nothing). Assertion 3 pins the blast radius to D-01's measured set. `_describe_record_diff` is reused unchanged, so `test_describe_record_diff_is_non_vacuous` (`:211-231`) needs no edit.

**Renaming the test** (rather than editing `test_live_capture_matches_golden` in place) makes the change visible in any test-name diff and in CI output — worth it here, since the whole point of D-17 is that this change be legible.

### (e) Host suite baseline

```
$ python3 -m pytest tests/ -o addopts="" -q
1641 passed, 1 warning in 218.65s (0:03:38)
--------------------------- snapshot report summary ----------------------------
32 snapshots passed.
```
1641 passed / 0 failed, ~3m39s. Matches Phase 148's recorded 1641. `addopts` is `-ra -q` (project memory) so `-o addopts=""` is required to see the count line — confirmed necessary. `[VERIFIED: live run]`

*`tests/test_flash_path_record_sync.py` does **not** exist in `firestarter_app` — it is a **firmware**-repo test (`firestarter/tests/test_flash_path_record_sync.py`). See §R8f.*

---

## R7 — The cross-repo parity gate (D-18)

### (a) `fw_presence.py` — the mechanism, verbatim where it matters

```python
# firestarter_app/tests/fw_presence.py:77-102
_APP_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_FW_ROOT = _APP_REPO_ROOT.parent / "firestarter"

FW_ROOT: Path = Path(os.environ.get("FIRESTARTER_FW_ROOT", str(_DEFAULT_FW_ROOT)))
FW_REPO_MARKER: Path = FW_ROOT / ".git"
FW_REPO_PRESENT: bool = FW_REPO_MARKER.exists()
FW_ABSENT_REASON: str = (
    f"firestarter firmware checkout absent (no {FW_REPO_MARKER} marker)"
)
requires_fw = pytest.mark.skipif(not FW_REPO_PRESENT, reason=FW_ABSENT_REASON)

# :117-140
def fw_path(*parts: str) -> Path:
    resolved = FW_ROOT.joinpath(*parts)
    if FW_REPO_PRESENT and not resolved.exists():
        raise MissingScanTargetError(...)     # HARD FAILURE, never a skip
    return resolved
```

Measured locally:
```
FW_ROOT: /workspaces/firestarter
MARKER:  /workspaces/firestarter/.git
PRESENT: True
```
So the parity tests **run** in this devcontainer (they do not skip), and **skip** in app CI, which has no sibling checkout. ✓ D-18's "state that" requirement is satisfiable as a measured fact.

Import-time binding confirmed at `:80` (module-scope `os.environ.get`) and `:102` (`pytest.mark.skipif` binds at collection). `monkeypatch.setenv` has no effect. ✓

### (b) Adding `src/json_parser.c` to the inventory

```python
# firestarter_app/tests/scan_paths.py:94-129  (CROSS_REPO_TEST_PATHS — 7 entries today)
CROSS_REPO_TEST_PATHS: tuple[ScanPathEntry, ...] = (
    ScanPathEntry("include/firestarter.h",
                  ("test_revision_constants_parity.py", "test_check_is_memory_cmd_no_ifdef.py")),
    ScanPathEntry("src/proms/eeprom_28c.cpp",
                  ("test_check_no_log_in_sdp_window.py", "test_sdp_table_parity.py")),
    ScanPathEntry("doc/PROTOCOLS.md", ("test_dispatch_mirror.py",)),
    ScanPathEntry("test/native/avr/test_dispatch/test_configure_memory.cpp", ("test_dispatch_mirror.py",)),
    ScanPathEntry("test/native/avr/_shared/sdp_bus_config.h", ("test_sdp_bus_config_drift.py",)),
    ScanPathEntry("test/native/avr/_shared/validation_matrix.h", ("test_gen_validation_header.py",)),
    ScanPathEntry("src/firestarter.cpp", ("test_cap03_ack_layout_parity.py",)),
)
```

**Confirmed:** `include/firestarter.h` is listed; **`src/json_parser.c` is not**. ✓ D-18's premise. The addition is one `ScanPathEntry`:
```python
    ScanPathEntry("src/json_parser.c", ("test_json_key_parity.py",)),   # or whatever the test is named
```

**No count assertion breaks.** `ALL_CROSS_REPO_PATHS` is *derived* (`scan_paths.py:265-274`) so it picks the new entry up automatically, and the guards are **floors**:
```python
# firestarter_app/tests/test_scan_paths_resolve.py:47, :98, :103
_FLOOR = 6
assert len(ALL_CROSS_REPO_PATHS) >= _FLOOR, ...
assert len(CROSS_REPO_TEST_PATHS) >= _FLOOR, ...
```
The only exact-count assertion is on the **tool** population: `assert len(CROSS_REPO_TOOL_RESOLVERS) == 11` (`scan_paths.py:247`), untouched by this change. ✓

`test_scan_paths_resolve.py:127` also asserts `not resolved.is_relative_to(_APP_REPO_ROOT)` for every inventory path — the `firestarter` name-collision guard. `FW_ROOT / "src/json_parser.c"` = `/workspaces/firestarter/src/json_parser.c`, which is **outside** `/workspaces/firestarter_app`. ✓ Safe.

**Two stale docstring counts to fix while there** (`scan_paths.py:30` says "6 paths resolved from the 7 proxy-carrying modules"; `:259` says "this union is the same 6 paths as population A"). Both were true before Phase 147 added `src/firestarter.cpp`; there are now **7**. The phase adds an 8th, so both numbers need updating regardless. A file whose entire purpose is "deliberately explicit, never derived" should not carry a wrong count.

### (c) How an existing test asserts a Python constant equals a firmware source string

Two precedents. **`test_cap03_ack_layout_parity.py` (Phase 147) is the closest** — it scans a `.cpp` with regexes and is the newest:

```python
# firestarter_app/tests/test_cap03_ack_layout_parity.py:78, :89
from tests.fw_presence import FW_REPO_PRESENT, FW_ROOT, fw_path, requires_fw
_HERE = Path(__file__).resolve().parent
FIRMWARE_ACK_SOURCE = fw_path("src", "firestarter.cpp")     # module scope
...
_READY_DECL_RE = re.compile(r"uint8_t\s+_ready\s*\[\s*4\s*\+\s*32\s*\+\s*2\s*\]\s*;")
_BYTE3_RE      = re.compile(r"_ready\[3\]\s*=\s*_vlen\s*;")
```

Its module docstring states the pattern D-18 should copy exactly (`:34-47`):
> "`requires_fw` … is the ONLY skip marker this module uses… `FIRMWARE_ACK_SOURCE` (resolved via `fw_path`) doubles as the fixture-injection seam the two planted-violation legs below `monkeypatch.setattr`. Those two legs deliberately carry NO `requires_fw` decorator: they read committed fixtures under `tests/fixtures/`, which are always present regardless of whether the sibling firmware checkout exists, so they stay live and exercise the gate's failure modes even in an absent-firmware run."

**This is the single most valuable structural finding for D-18.** It means the parity gate can be **fail-provable in app CI even though the firmware-reading leg skips there** — by putting the planted-violation legs on committed fixtures under `tests/fixtures/` with no `requires_fw`. Without that split, D-18's gate would be entirely unexercised in CI and its RED leg unprovable in the only environment that runs on every push.

`test_revision_constants_parity.py:128,148` is the header-scanning sibling (`FIRMWARE_HEADER = fw_path("include", "firestarter.h")`), and its `:37-40` docstring records the *anti*-pattern to avoid: two legs that "were 100% hollow with respect to firmware drift: they asserted hardcoded Python literals with the corresponding `firestarter.h` define named only in a trailing comment, and never actually read the header."

**Recommended D-18 assertion shape.** Both directions, from the same read of `json_parser.c`:
1. `constants.py`'s `JSON_KEY_PAGE_SIZE` (`"page-size"`) appears as a PROGMEM key string literal in `src/json_parser.c` — i.e. `re.search(r'const\s+char\s+key_page_size\s*\[\s*\]\s+PROGMEM\s*=\s*"page-size"\s*;', src)`.
2. That same PROGMEM identifier appears in the `key_parsers[]` table body — otherwise the string exists but is never dispatched (the "declared but unwired" hole, which is exactly what a naive string-presence assertion would miss).
3. Two-way: every `JSON_KEY_*` constant in `constants.py` (there are exactly 3 — `:143`, `:144`, `:149`) maps to a PROGMEM key string in `json_parser.c`, and every PROGMEM `key_*` string maps back. This turns the whole `JSON_KEY_*` block into an enforced claim, not just the new one, and is cheap because the surface is 3 vs 10.

Direction 3 will initially FAIL on the two Phase 44 knobs' direction if the firmware carries keys with no Python constant (`memory-size`, `address`, `flags`, `chip-id`, `pin-count`, `pulse-delay`, `vpp_mv`, `algorithm` have no `JSON_KEY_*` constants). So the **firmware→Python** direction needs an explicit exemption list, exactly as `test_revision_constants_parity.py`'s CMD two-way leg does (`:446`, `:520`, `:563-575` show the errors-list-then-assert-empty shape with exemptions). **Recommend: assert Python→firmware totally, and firmware→Python with a named exemption tuple** — and make the exemption tuple's completeness itself an assertion, so a new firmware key must be deliberately classified.

### (d) Proving the SKIP leg — the mechanism ALREADY EXISTS

Because of import-time binding, `FIRESTARTER_FW_ROOT` must be set **before** import — so a subprocess is required. Both mechanisms are already in the repo:

```python
# firestarter_app/tests/test_fw_presence.py:80, :100
    """... runs `fw_presence`'s constants in a **subprocess**, with FIRESTARTER_FW_ROOT
    set to `fw_root`, then attempts fw_path() on each of ..."""
    env = {**os.environ, "FIRESTARTER_FW_ROOT": str(fw_root)}
```

```bash
# firestarter_app/tools/ci_parity.sh:69, :86-88
TMPROOT="$(mktemp -d)"
...
banner 1 "FIRESTARTER_FW_ROOT=<empty dir> python3 -m pytest tests/ -q" \
       ...
FIRESTARTER_FW_ROOT="${TMPROOT}" python3 -m pytest tests/ -q
```

**`tools/ci_parity.sh` leg 1 is exactly D-18's requested skip-leg proof, already scripted.** The plan does not build this — it *runs* it and captures the transcript, asserting the new parity test appears as SKIPPED with `FW_ABSENT_REASON` (use `-rs` to make skips visible; the script's bare `-q` will not show them, so the plan should run the leg with `-rs` added for the transcript). `ci_parity.sh`'s four legs are: (1) empty-`FW_ROOT` pytest, (2) plain pytest, (3) ruff lint + format at ci.yml's exact path set, (4) mypy watermark.

### (e) `constants.py:144-148` quoted, and the sync note confirmed FALSE

Quoted in full in §R2(e). **Three false clauses measured** in that five-line comment: `key_page_size` does not exist in firmware; `flash4_page_size` does not exist; the emit is in `database.py`, not `eprom_operations.py`. D-18 turns clause 1 into a true, enforced claim; clauses 2 and 3 are one-line corrections in the same block.

---

## R8 — The size and warning gates (D-12, D-13, D-14, PGSZ-04)

### (a) The MERGE-05 mechanism, exactly

```python
# firestarter/scripts/check_size_baseline.py:123, :167
MERGE05_UNO_CLASS_FLASH_BAND = 64
MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96
```
```python
# firestarter/scripts/check_size_baseline.py:274-296
def _merge05_flash_allowance(env):
    """Resolve `env`'s MERGE-05 flash-growth figures. Returns
    (band, exemption, allowance, band_label).

    Sole consumer of BOTH MERGE05_UNO_CLASS_FLASH_BAND and
    MERGE05_DEFECT_FIX_EXEMPTION_BYTES -- compare_avr_policy_merge05 (the FAIL
    arm) and main()'s PASS-line builder both call this rather than each
    recomputing the band, so neither literal is ever read in two places...

    `allowance` is the effective ceiling actually enforced: base band plus the
    named defect-fix exemption. `band` and `exemption` are returned separately
    so every message can show the decomposition instead of only the sum -- the
    +96 B stays visible in the output rather than being absorbed into one
    widened number.
    """
    band = 0 if env == "leonardo" else MERGE05_UNO_CLASS_FLASH_BAND
    band_label = "leonardo" if env == "leonardo" else "uno-class"
    exemption = MERGE05_DEFECT_FIX_EXEMPTION_BYTES
    return band, exemption, band + exemption, band_label
```
```python
# firestarter/scripts/check_size_baseline.py:334-341  (the FAIL arm)
    band, exemption, allowance, band_label = _merge05_flash_allowance(env)
    flash_delta = flash_used - rec["flash_used"]
    if flash_delta > allowance:
        failures.append(
            f"{env}: flash_used baseline={rec['flash_used']} observed={flash_used} "
            f"delta={flash_delta:+d} exceeds MERGE-05 {band_label} allowance of "
            f"{allowance} B (band {band} B + defect-fix exemption {exemption} B)"
```

**How the constant enters the comparison:** exactly one function (`_merge05_flash_allowance`) reads both literals; the FAIL arm (`:334`) and `main()`'s PASS-line builder (`:536`) are its **only two** call sites. RAM keeps zero tolerance and is **deliberately not** widened by the exemption (`:316-320`).

**How the SHA attribution is recorded:** as prose in the constant's own comment block (`:132-138`) naming `eb563d2` and `ebe9cb3` and what the 96 bytes *are*, plus a parallel `merge05_clause` paragraph in `size_baseline.json`'s `meta.deltas_vs_base01.{leonardo,uno,uno328pb}`. There is no machine-readable SHA field — attribution is documentary, enforced only by review.

### (b) The measured position, and leonardo's headroom AS A NUMBER

| Target | BASE-01 flash | Live flash | Δ | band | exemption | allowance | **MERGE-05 headroom** | flash_total | flash_free | RAM (BASE-01 = live) |
|---|---|---|---|---|---|---|---|---|---|---|
| `uno` | 24824 | **24920** | **+96** | 64 | 96 | 160 | **64 B** | 32256 | 7336 | 1573 |
| `uno328pb` | 24874 | **24970** | **+96** | 64 | 96 | 160 | **64 B** | 32384 | 7414 | 1579 |
| `leonardo` | 26906 | **27002** | **+96** | **0** | 96 | **96** | **0 B** | 28672 | **1670 (5.8%)** | 2014 |

`[VERIFIED: scripts/baseline/size_baseline.json + size_baseline_base01.json, read verbatim]`

**Criterion 4's "leonardo warning watermark's remaining headroom stated as a number" — two distinct numbers, and the plan must state both, because they are different quantities:**
- **MERGE-05 flash headroom: 0 bytes.** Allowance 96, current delta +96. `+96 <= 96` passes by exactly zero margin. One byte of growth fails the gate.
- **Physical flash headroom: 1670 B** of 28672 (5.8% free). BASE-01's was 1766 B.
- **Native warning watermark headroom: 0.** `native` and `native_nodevtools` are both at `total_watermark: 1166` with `macro_redefinition: 1166` — the policy is `<= watermark`, and the recorded figure IS the current cold count, so **any** new warning fails. `native_pinmap_provisional` is at 138.
- **AVR warning headroom: 0 by construction** — the rule is `== 0`, not `<= 0`.

*(Project memory records "leonardo 93.8%/1766 B" from Phase 144 — that is the pre-Phase-145 figure, i.e. BASE-01's. The live figure is 1670 B / 94.2%. The `93.8%` in memory matches the **planted +97 fixture** at 27003 B, not the live tree. Use 1670 B / 27002.)*

### (c) The cold-capture picture — and why the inherited delta should be 0

`origin/beta` vs the current firmware tip:
```
$ git diff --stat HEAD origin/beta
 include/version.h | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
$ git diff HEAD origin/beta -- include/version.h
-#define VERSION "3.0.0b18"
+#define VERSION "3.0.0b19"
$ echo -n 3.0.0b18 | wc -c ; echo -n 3.0.0b19 | wc -c
8
8
```
**Equal-length version string, no other difference.** And from the Phase-145 fix commit to the current tip, the only `src`/`include` deltas are that version bump plus 19 **comment** lines:
```
$ git diff --stat ebe9cb3 HEAD -- src include
 include/version.h   |  2 +-
 src/firestarter.cpp | 19 +++++++++++++++++++
 2 files changed, 20 insertions(+), 1 deletion(-)
$ git show --stat 6992271
docs(firestarter.cpp): preserve PR #49's two CAP-02 facts the merge resolved away
```

**Independent size measurement of the tree as it stands** — from the warm build artifacts already on disk (built 2026-08-18 09:26, i.e. at the merged v1.31 tip), measured with the toolchain's own `avr-size`:
```
$ ~/.platformio/packages/toolchain-atmelavr/bin/avr-size -C --mcu=atmega328p .pio/build/uno/firestarter_uno.elf
Program:   24920 bytes (76.0% Full)      Data:  1573 bytes (76.8% Full)
$ ... uno328pb
Program:   24970 bytes (76.2% Full)      Data:  1579 bytes (77.1% Full)
$ ... --mcu=atmega32u4 .pio/build/leonardo/firestarter_leonardo.elf
Program:   27002 bytes (82.4% Full)      Data:  2014 bytes (78.7% Full)
```
**Byte-identical to `size_baseline.json`'s live figures on all six numbers.** `[VERIFIED: avr-size against on-disk ELFs]`

**Conclusion for D-13:** the fork point's cold capture should reproduce 24920 / 24970 / 27002 and 1573 / 1579 / 2014, i.e. an inherited delta of **0**. This is a *prediction with a mechanism*, not a substitute for the measurement — these are warm/incremental artifacts and D-13 requires the `rm -rf` + single-invocation procedure. **If the cold capture differs, D-13's "inherited from the v1.31 merge" clause applies and the difference must be recorded as inherited, in either direction.** The plan should state the predicted figures in the task so a mismatch is caught rather than absorbed.

**Toolchain availability — MET:**
```
$ which pio ; pio --version
/usr/local/bin/pio
PlatformIO Core, version 6.1.19
$ ls ~/.platformio/packages/
contrib-piohome  framework-arduino-avr  framework-arduino-avr-minicore
tool-avrdude  tool-avrdude@1.60300.200527  tool-scons  toolchain-atmelavr
$ ls .pio/build/
leonardo  native  native_loop_v131  native_nodevtools  native_params_v131
native_trace_v131  uno  uno328pb
```
`toolchain-atmelavr`, `framework-arduino-avr` **and** `framework-arduino-avr-minicore` (required by `uno328pb`, whose board is `ATmega328PB` with `build.core = "MiniCore"`) are all installed, and warm builds exist for all three AVR envs. Versions in `size_baseline.json`'s meta (`platformio_core 6.1.19`, `platform_atmelavr 5.2.0`, `toolchain_atmelavr 1.70300.191015`, `avr_gcc 7.3.0`, `framework_arduino_avr 5.3.0`, `framework_arduino_avr_minicore 3.1.2`) must be re-confirmed at capture time — D-14's update should carry them.

**Cold build duration: UNVERIFIED — planner must measure.** No cold build was run this session (the hard safety rules forbid capturing the D-13 baseline, and a cold build is exactly that capture). The warm `pio test -e native` run of 2 suites took 5.8 s; a cold AVR build compiles the full Arduino core (~40 `FrameworkArduino/*.o` present in `.pio/build/uno/`) plus ~25 firmware TUs. **Budget generously and do not put a short timeout on the task.** `[ASSUMED: single-digit minutes per env; three envs sequentially]`

**`platformio.ini` generation — no impact on a cold build, but one gotcha.** `/workspaces/platformio.ini` is auto-generated from `firestarter/platformio.ini` by `/workspaces/.devcontainer/gen-platformio-ini.py` and is **untracked** in the meta repo (`git ls-files platformio.ini` → empty). Its header says *"To work on firmware outside the devcontainer, run pio from `firestarter/` directly."* Crucially it redirects `build_dir = firestarter/.pio/build` — **the same directory** either invocation uses. So:
- `rm -rf firestarter/.pio/build/<env>` is correct regardless of which `platformio.ini` is in play.
- **Run `pio` from `firestarter/`** for D-13 (matching `size_baseline.json`'s own recorded procedure and CLAUDE.md's C-6), not from `/workspaces`.
- **If the plan edits `firestarter/platformio.ini`** (it should not need to — the table is self-sizing and no new `-I` is required, §R4a), the generated root copy goes stale and must be regenerated. Since no edit is expected, this is a negative check worth asserting: `git -C firestarter diff --quiet -- platformio.ini`.

### (d) The diff shape for a NEW exemption constant — bigger than it looks

D-12 says "mirror the existing exemption's *mechanism* with a distinct constant carrying its own justification and its own commit SHAs; the existing defect-fix constant is untouched and not widened". Measured blast radius:

**`scripts/check_size_baseline.py`:**
1. New constant beside `:167`, e.g. `MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES = <N>`, with its own comment block in the shape of `:125-166` — what the bytes ARE, which alternatives were rejected, the commit SHAs.
2. `_merge05_flash_allowance()` (`:274-296`) must return the **new** exemption separately. Its docstring makes decomposition load-bearing (`:287-291`: *"`band` and `exemption` are returned separately so every message can show the decomposition instead of only the sum — the +96 B stays visible"*). **Summing the two exemptions into one `exemption` value destroys exactly that property** and would launder the new growth into the old constant's number. So the honest shape is a **5-tuple** `(band, defect_exemption, seam_exemption, allowance, band_label)`.
3. Both call sites unpack the tuple: `:334` (FAIL arm) and `:536` (PASS-line builder). A 5-tuple breaks both unless updated.
4. The FAIL message at `:338-341` and the PASS line both need the third term: `(band N B + defect-fix exemption 96 B + page-size-seam exemption M B)`.
5. The module docstring's own worked examples at `:50`, `:55-58`, `:115`, `:130-133` all quote the current allowances (96 / 160) and the +97 plant. All need re-deriving.

**`tests/test_check_size_baseline.py` — four legs break on string literals and one on an exit code:**
| Leg | Line | What breaks |
|---|---|---|
| `test_policy_merge05_admits_the_documented_defect_fix` | `:374-459` | Asserts `"allowance of 96 B" in over.stdout` (`:458`) → literal changes. Asserts `over.returncode == 1` (`:449`) on a `delta=+97` leonardo plant → **+97 becomes INSIDE the new allowance (96+N for N≥1), so this goes GREEN and the assertion goes RED.** Also asserts `"delta=+97"` (`:455`). |
| PASS-decomposition assertion | `:433` | Asserts the PASS text shows the allowance "DECOMPOSED into the unchanged …" — the decomposition string changes |
| `test_policy_merge05_fires_on_uno_class_over_band` | `:463-490` | Asserts `"allowance of 160 B" in result.stdout` (`:490`) → becomes 160+N |
| `test_policy_merge05_permits_the_measured_landing_deltas` | `:316` | Depends on the allowance arithmetic |

**Two planted fixtures must be re-planted:**
```
$ grep -n 'Flash:\|RAM:' tests/fixtures/planted_size_baseline_policy_leonardo_growth.log
78:RAM:   [========  ]  78.7% (used 2014 bytes from 2560 bytes)
79:Flash: [========= ]  93.8% (used 27003 bytes from 28672 bytes)
```
`27003 = 26906 + 97`. To stay one byte past the new allowance it must become `26906 + 96 + N + 1`. Same for `planted_size_baseline_policy_uno_over_band.log`.

**AND THIS MATTERS: those tests DO run in firmware CI.** `check_size_baseline.py` itself appears in **zero** workflow files:
```
$ grep -rn 'check_size_baseline\|check_build_warnings' .github/workflows/
(no output)
```
✓ CONTEXT.md is right that neither *script* runs in CI, so the plan must invoke both as phase-level gates. **But** `build.yml:161` runs `pytest tests/ -v` in the firmware repo, and `tests/test_check_size_baseline.py` is in `tests/`. So breaking any of those four legs is a **CI-visible RED**, not a local-only one. This is a correction to the natural reading of CONTEXT.md's "neither size script runs in CI" — the script is not a gate, but its test suite is.

**Sequencing consequence, and it is the phase's tightest constraint.** `N` (the new exemption's value) is unknown until the firmware edit is built and cold-measured. So the plan cannot author the constant, the message format, the four test legs and the two fixtures until after the firmware seam lands. **The size-gate plan must be strictly downstream of the firmware-seam plan** — it cannot be parallelised with it, and it cannot be pre-authored with a placeholder, because a placeholder `N` would make the planted fixtures wrong and the RED/GREEN transcripts meaningless.

### (e) `check_build_warnings.py` policy

```
# firestarter/scripts/check_build_warnings.py:10-15, :121-178
AVR:    macro_redefinition "== 0", not "<= 0"     (policy.avr_rule)
native: total <= total_watermark                  (policy.native_rule)
        > watermark -> FAIL
        < watermark -> INFO  ("re-measure and lower total_watermark")
        == watermark -> OK
```
`check_env` returns `("OK"|"INFO"|"FAIL", message)`. INFO is **not** a failure. Watermarks from `size_baseline.json`: `native` 1166, `native_nodevtools` 1166, `native_pinmap_provisional` 138; AVR all `{macro_redefinition: 0, total: 0}`.

Counting command, recorded in the baseline itself:
```
pio test -e <env> 2>&1 | grep -cE 'warning: *"[^"]+" +redefined'   # macro-redefinition count
pio test -e <env> 2>&1 | grep -cE 'warning:'                        # total
```

**Why D-15 is a warning-budget decision — confirmed.** `size_baseline.json`'s `meta.warm_vs_cold_correction` records that the 1166 figure comes from `include/rurp_platform_compat.h` defining program-memory macros that ArduinoFake's `pgmspace.h` redefines "across roughly 27 more translation units". I observed this live during the native run (`pgm_read_word`, `pgm_read_dword`, `pgm_read_ptr`, `F` all reported redefined against `include/rurp_platform_compat.h:40,44,48,81`). A **new suite** adds TUs and therefore warnings, forcing a cold re-measure and a raised watermark. **Extending existing suites adds zero TUs and leaves all three watermarks untouched.** ✓ D-15 verified by mechanism, and §R4a shows extension is sufficient for every case this phase needs.

**Cold-vs-warm trap, restated because it will bite:** the recorded 1166 is the **COLD** figure; warm is 998. `check_build_warnings.py`'s below-watermark arm returns INFO (not FAIL), so a watermark set to the cold figure stays green in both states — but a *re-measurement* taken warm would read 998 and, if written into the baseline, would go RED on the next cold CI run. **Any warning re-measure must be cold, in the `rm -rf` + single-invocation sequence.**

### (f) Firmware pytest baseline, and the porcelain question

```
$ python3 -m pytest tests/ -q      # from firestarter/
314 passed in 10.71s
```
`[VERIFIED: live run, clean tree]`

`firestarter/tests/test_flash_path_record_sync.py` exists (it is a **firmware**-repo test, not an app one). Its porcelain machinery is `_git_porcelain(path)` at `:252-262` (`git -C <path> status --porcelain`). The leg that exercises it, `test_dirty_tree_is_detected` (`:838-848`), operates on a `tmp_path` repo it dirties itself, and its docstring at `:841` states that *"calling `_git_porcelain` against the real firmware repo must not raise"* — i.e. it asserts non-raising, not emptiness, against the real repo.

**So the "whole-repo porcelain" warning is softer than project memory implies** — the suite passed here with a clean tree, and its own docstring suggests it tolerates a dirty real repo. **UNVERIFIED — not probed against a dirty tree** (doing so would have required dirtying the firmware working tree, which the safety rules forbid). **Planner guidance: commit before running the firmware suite anyway.** The cost of following the rule is one commit; the cost of being wrong is a RED that reads like a real failure mid-plan.

---

## R9 — The claim gate (D-19)

### (a) Where the prior gates live

```
$ find /workspaces/.planning -name 'check_permitted_claims*.py' -o -name '*-check-claims.py'
.planning/phases/122-.../check_permitted_claims.py
.planning/phases/123-.../check_permitted_claims.py
.planning/phases/137-.../check_permitted_claims.py
.planning/phases/139-gh-15-correction-outward/139-check-claims.py
.planning/phases/146-close-honesty-ledger-.../146-check-claims.py
```
**Use `146-check-claims.py` (451 lines) as the donor** — it is the most recent, it names `139-check-claims.py` as *its* donor with verbatim line citations, and it already carries the `_HERE`-trap defence. Its paired suite is `146-.../test_check_claims_v131.py` (30,928 B) with fixtures under `146-.../fixtures/`.

### (b) The `_HERE` trap — already solved in the donor

```python
# .planning/phases/146-.../146-check-claims.py:102-120
# Module-top path constant. This is the ONLY directory `_DEFAULT_TARGETS`
# below is ever built from -- never a sibling-directory string constant.
# This construction is what stops the cross-phase-copy defect where a
# checker's defaults silently resolved to a stale sibling phase directory
# and passed vacuously with nothing actually scanned.
# Source: `139-check-claims.py:73`, copied verbatim.
_HERE = os.path.dirname(os.path.abspath(__file__))

_DEFAULT_TARGETS = [
    os.path.join(_HERE, "146-LEDGER.md"),
    os.path.join(_HERE, "146-CORRECTIONS.md"),
    os.path.join(_HERE, "146-GH15-RECONCILIATION.md"),
    os.path.join(_HERE, "146-RELEASE-NOTES-fw.md"),
    os.path.join(_HERE, "146-RELEASE-NOTES-app.md"),
]
```
```python
# .planning/phases/146-.../146-check-claims.py:235-269
def _assert_default_targets_are_local():
    """Startup self-check -- called first thing in main(), before target
    resolution or any scanning. ...
    This is the run-time equivalent of a paired-test suite's mandatory
    cross-phase-copy legs, moved inside the script itself so a future copy
    of this file into another phase's directory fails loudly the first
    time it is run, rather than silently scanning nothing and reporting
    success. Source: `139-check-claims.py:148-181`..."""
    all_local = True
    for entry in _DEFAULT_TARGETS:
        if os.path.dirname(entry) != _HERE:
            print(f"FAIL: _DEFAULT_TARGETS entry {entry!r} does not resolve "
                  "inside this phase's own directory -- this is the exact "
                  "cross-phase-copy defect this self-check exists to catch")
            all_local = False
        if not os.path.basename(entry).startswith("146-"):
            print(f"FAIL: _DEFAULT_TARGETS entry {entry!r} does not carry "
                  "this phase's own 146- prefix -- ...")
            all_local = False
    return all_local
```

**The named `_HERE` trap is already defended, twice over:** by building every default from `_HERE` (so a copy re-points at its new home rather than a stale sibling), and by a runtime self-check that additionally requires the phase-number prefix. So a copy of `146-check-claims.py` into `149-*/` with the targets renamed to `149-*` is correct by construction; a copy with the targets **left** as `146-*` fails loudly on the prefix check rather than scanning nothing. **The plan must carry both mechanisms and must change the prefix literal to `149-` in three places: `_DEFAULT_TARGETS`, the prefix comparison at `:262`, and its printed message.**

### (c) Env seam and exit codes

```python
# :132-134
FIRESTARTER_CLAIMSCAN_TARGETS_146 = os.environ.get("FIRESTARTER_CLAIMSCAN_TARGETS_146")
```
The suffix is the **phase number**, deliberately (`:122-127`): four prior checkers use bare / `_V130` / `_V131`-suffixed names and a collision "would let one phase's seam silently retarget another phase's gate". So Phase 149's must be `FIRESTARTER_CLAIMSCAN_TARGETS_149`. `os.environ.get` with **no default** is deliberate so `resolve_targets` can distinguish absent (→ defaults) from present-but-empty (→ zero targets, never a silent fall-back).

```
# :67-85  Exit codes
0 -- every resolved target exists, zero forbidden matches, every required caveat present
1 -- self-check fails OR zero targets resolved OR a target missing from disk
     OR any forbidden match OR a missing required caveat
There is deliberately no branch that exits 0 when nothing was scanned.
(Phase 137's checker carried one; it is NOT ported.)
```

### (d) Pattern tables — and the `\bproven\b` collision (see §X-2)

Twelve forbidden patterns at `:142-172`, all `re.IGNORECASE`, no proximity window: `datasheet-conformant`, `datasheet-correct`, `algorithm-accurate`, `datasheet-compound-unqualified`, `verified-on-silicon`, `silicon-verified`, `confirmed-working`, `works-on-silicon`, `proven-on-silicon`, **`proven-unqualified` (`\bproven\b`)**, `now-works`, `should-now-work`.

Two required-caveat patterns at `:178-189`, consumed through a per-file `_CAVEAT_RULES` map (`:209-217`) keyed on **basename**, with `_required_caveats_for()` (`:220-232`) **failing CLOSED** on an unknown basename (an unmapped target gets the FULL caveat set, never the empty set).

**Phase 149's tables must add**, beyond the milestone-vocabulary carry-over:
| Kind | Label | Suggested pattern | Why |
|---|---|---|---|
| REQUIRED | `software-proven-unvalidated` | `r"software[-\s]proven\s+and\s+unvalidated\s+on\s+silicon"` (IGNORECASE) | PGSZ-05's literal phrase, in those words |
| FORBIDDEN | `page-size-proven` | `r"page[-\s]size\s+(?:is\s+)?(?:proven\|verified\|validated)"` | criterion 5's "no page-size claim about any physical AT28C part" |
| FORBIDDEN | `graduation` | `r"(?:graduat\w+\|promot\w+)\s+(?:\w+\s+){0,3}(?:0x0[Dd]\|protocol\s+13)"` | `0x0D` stays `UNVERIFIED` |
| FORBIDDEN | `support-status-change` | `r"support_status\s*(?:[:=]\|changed\|updated\|now)"` | no `support_status` changes |
| FORBIDDEN | `issue-closed` | `r"gh#(?:21\|32\|11\|12)\b(?:\s+\w+){0,3}\s+(?:closed\|resolved\|fixed)"` | REQUIREMENTS.md §Out of Scope |
| FORBIDDEN | `at28c256-fixed` | `r"AT28C256\b(?:\s+\w+){0,4}\s+(?:fixed\|works\|now)"` | the measured non-claim |
| MODIFIED | `proven-unqualified` | `r"(?<!software-)\bproven\b"` | **§X-2 — otherwise unsatisfiable** |

**Anti-vacuity requirement.** `146-check-claims.py:59-62` records that Phase 139 *measured* a windowed scanner passing four planted overclaims — so every windowed pattern above (the `{0,3}` / `{0,4}` forms) is weaker than an unwindowed one and each needs its own planted-fixture leg. Prefer unwindowed forms where the vocabulary allows.

### (e) D-19's target list, hard-coded

```python
_DEFAULT_TARGETS = [
    os.path.join(_HERE, "149-PAGE-SIZE.md"),
    os.path.join(_HERE, "149-01-SUMMARY.md"),
    ...   # every 149-NN-SUMMARY.md, enumerated, NOT globbed
]
```
**Never a glob.** `:110-113` records why: a `146-*.md` default set "would sweep in `146-CONTEXT.md` (six `proven-unqualified` hits) and the fixtures directory". `149-CONTEXT.md` and this `149-RESEARCH.md` both contain `proven` in ways the gate would flag, so both **must be excluded** — and that means the SUMMARY list has to be enumerated once the plan count is known.

**Ordering hazard — the reason this needs its own plan task, and possibly two.** D-19 requires the gate to exist "before the artifacts it scans are final", but a hard-coded target list fails closed on a **missing** target (`:74-75`, exit 1), and Phase 137's exit-0-on-nothing-scanned escape hatch is deliberately **not** ported. So the gate cannot be authored with the full SUMMARY list before those SUMMARYs exist. Two workable shapes:
1. **Author the gate early with only `149-PAGE-SIZE.md`** in `_DEFAULT_TARGETS`, prove RED/GREEN against it, then extend the list in the final plan and re-run. Two transcripts, both real.
2. **Author the gate in the final plan**, with the full list, and prove RED/GREEN there. One transcript, but 149's earlier artifacts go unscanned until the end.

**Recommend (1)** — it matches D-19's "before the artifacts it scans are final" and yields a gate that is armed while the artifacts are being written, which is when overclaims get authored.

**The changelog entry is a target too (D-19 names it).** It lives in `firestarter_app/README.md` (§(f)), which is **outside** `_HERE` — so `_assert_default_targets_are_local()` would **FAIL on it** (`os.path.dirname(entry) != _HERE`). Three options: (a) pass the README via `argv` (which `resolve_targets` supports and which bypasses the locality self-check by design, since the self-check only validates `_DEFAULT_TARGETS`); (b) scan only the extracted changelog *text* mirrored into `149-PAGE-SIZE.md`; (c) relax the self-check with a named exemption. **Recommend (a)** — `resolve_targets`'s argv precedence exists for exactly this, the self-check stays untouched, and the plan's verify block names the README path explicitly so the scan is visible in the transcript.

### (f) Where the changelog line goes (D-20)

**There is no `CHANGELOG.md` in `firestarter_app`:**
```
$ find . -iname '*changelog*' -o -iname '*CHANGES*' -o -iname '*RELEASE*' | grep -v '.git/'
./.github/workflows/beta-release.yml
./.github/workflows/release.yml
```

**The changelog surface is `firestarter_app/README.md`, `## Breaking Changes (v1.32)` at line 61.** Structure measured:
```
$ grep -n '^#\{1,3\} ' README.md | head
 61:## Breaking Changes (v1.32)
 63:### Chip database now stores numeric values (breaking change)
 76:### AT28C-family VCC now reports 5.0v (correction, not a write-path fix)
 92:## Breaking Changes (v1.20)
119:## Breaking Changes (v1.10)
```

Phase 148's own record confirms this is the established pattern and that it was a deliberate choice, not an omission (`148-08-SUMMARY.md`):
> "README.md's new `Breaking Changes (v1.32)` section, inserted immediately above `Breaking Changes (v1.20)`, states both the breaking numeric schema … and the AT28C VCC correction … **No CHANGELOG.md created.**"
> verify: "…**no CHANGELOG.md file exists**"

**So D-20 lands as a new `###` subsection under the existing `## Breaking Changes (v1.32)`**, following the shape of `:76-88`. Two precision points:

1. **Insertion point.** `README.md:90` is the closing sentence of the *whole* v1.32 section — *"This change is beta-only (v1.32). Nothing is promoted to stable without operator authorization."* A new `###` must go **before** line 90, or line 90's singular "This change" becomes wrong. Cleanest: insert the new `###` block between `:88` and `:90`, and if the sentence is touched at all, pluralise it deliberately.
2. **Do not create `CHANGELOG.md`.** Phase 148 asserted its absence in a plan verify block. That assertion is **not** a live test — `grep -rn 'CHANGELOG' tests/ tools/` returns nothing in the app repo — so creating one would not go RED. But it would silently contradict a closed phase's recorded decision. Follow the precedent.

3. **Framing, per D-20.** Phase 148's AT28C subsection is the model for an honest heading: `### AT28C-family VCC now reports 5.0v (correction, not a write-path fix)`. The 149 analogue should carry its own disqualifier in the heading, e.g. `### 15 AT28C010-class parts now write with a 128-byte page (software-proven, unvalidated on silicon)`. And unlike 148's, this change **does** alter write behaviour, so the body must say so plainly — while stating that no physical AT28C part was tested, that AT28C256 is unaffected, and that `0x0D` remains `UNVERIFIED`.

---

## R10 — Preconditions the plan must sequence first

### (a) `origin/beta` carries v1.31 — verified BY CONTENT, not by ancestry

```
$ git -C firestarter rev-parse --abbrev-ref HEAD ; git rev-parse HEAD
gsd/v1.31-27c-programming-algorithm-fidelity
6992271306a2cd344f7c7cd1f703142dd66b8400
$ git rev-parse origin/beta ; git log -1 --format='%H %ci %s' origin/beta
7f6afc65be2022575989772cc0a5945611741831
7f6afc65be2022575989772cc0a5945611741831 2026-08-18 09:59:10 +0000 Apply automatic changes
$ stat -c '%y' .git/FETCH_HEAD
2026-08-19 14:44:16 +0000        # fetched today
```
✓ CONTEXT.md's `6992271` / `7f6afc6` both confirmed.

**Four content checks, all positive** — use these exact commands in the plan (ancestry checks return false negatives because the v1.31 PRs were squashed):
```
$ git -C firestarter show origin/beta:scripts/check_size_baseline.py | grep -n 'MERGE05'
21:    defect-fix exemption of MERGE05_DEFECT_FIX_EXEMPTION_BYTES (96 B, commits
123:MERGE05_UNO_CLASS_FLASH_BAND = 64
167:MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96
293:    band = 0 if env == "leonardo" else MERGE05_UNO_CLASS_FLASH_BAND
...
$ git cat-file -e origin/beta:scripts/baseline/size_baseline_base01.json && echo EXISTS
EXISTS
$ git grep -c 'eprom_internal_program_pulse' origin/beta -- src/proms/eprom.cpp
origin/beta:src/proms/eprom.cpp:4          # Phase 145's fix IS present
$ git grep -n 'CAP-02' origin/beta -- src include | head -3
origin/beta:src/firestarter.cpp:158:    // CAP-02 is being PORTED here, not invented: ...
origin/beta:src/firestarter.cpp:164:    //      CAP-01              CAP-02                                CAP-03
origin/beta:src/firestarter.cpp:192:    //    misparses. Hosts predating CAP-02 test `len(params) == 2`, ...
```

**fw#52's CAP-02 conflict is RESOLVED on `origin/beta`, and it does not touch this phase's files.** The full content diff between the v1.31 branch tip and `origin/beta` is a single equal-length version string:
```
$ git diff --stat HEAD origin/beta
 include/version.h | 2 +-
$ git diff --stat HEAD origin/beta -- src/json_parser.c include/firestarter.h src/proms/eeprom_28c.cpp scripts/ platformio.ini test/native
(empty — zero differences in every file this phase touches)
```
✓ `json_parser.c`, `firestarter.h`, `eeprom_28c.cpp`, `scripts/`, `platformio.ini` and `test/native` are **byte-identical** on both. The CAP-02 resolution landed in `src/firestarter.cpp` comments only (`6992271`, docs-only, 19 comment lines).

**The fork command shape (NOT RUN — execution owns this):**
```bash
git -C firestarter fetch origin
git -C firestarter checkout -b gsd/v1.32-at28c-write-path-root-cause-report-provenance origin/beta
git -C firestarter rev-parse HEAD          # expect 7f6afc6…  (or later if origin/beta moved)
# then, and only then, D-13's cold capture:
for e in uno uno328pb leonardo; do
  rm -rf firestarter/.pio/build/$e
  ( cd firestarter && pio run -e $e )      # one uninterrupted invocation per env
done
```
**Re-verify `origin/beta`'s tip at fork time.** It was fetched 2026-08-19 14:44; `beta` has fired spurious CI-driven bumps before (project memory: "beta merge+push at close auto-fires CI → spurious beta", "local `beta` lags origin"). A `git fetch` immediately before the fork, plus recording the actual forked SHA in `149-PAGE-SIZE.md`, is the cheap defence.

### (b) The folded todo: dead `json_init()`

```c
// firestarter/src/json_parser.c:42-65
int json_init(const char* json, int len, jsmntok_t* tokens) {
    jsmn_parser parser;
    jsmn_init(&parser);
    return jsmn_parse(&parser, json, len, tokens, sizeof(tokens) / sizeof(tokens[0]));
}
```
`sizeof(tokens)` on a **pointer** parameter → `num_tokens` is `8/8 = 1` on a 64-bit host and `2/8 = 0` on AVR; either way `jsmn_parse` cannot succeed for a real command.

```c
// firestarter/include/json_parser.h:19
    int json_init(const char* json, int len, jsmntok_t* tokens);
```

**Called from nowhere:**
```
$ grep -rn 'json_init' src/ include/
src/json_parser.c:42:int json_init(const char* json, int len, jsmntok_t* tokens) {
include/json_parser.h:19:    int json_init(const char* json, int len, jsmntok_t* tokens);
$ grep -rn 'json_init' test/
test/native/avr/test_read_timing/test_read_timing_params.cpp:70: * Note: json_init() uses sizeof(tokens)/sizeof(tokens[0]) which is wrong when
```
✓ Zero call sites in `src/`; one **comment** mention in the very suite this phase extends. ✓ CONTEXT.md confirmed.

**`--gc-sections` IS on** — measured from the platform builder, not assumed:
```
$ grep -rn 'gc-sections\|ffunction-sections' ~/.platformio/platforms/atmelavr/builder/frameworks/arduino.py
98:        "-ffunction-sections",  # place each function in its own section
111:        "-Wl,--gc-sections",
```
So the linker almost certainly already discards `json_init`. And the flash saving is bounded even further than the todo assumes:
```
$ grep -rn 'jsmn_parse\|jsmn_init' src/ include/
src/json_parser.c:62,63,64          (inside json_init)
src/firestarter.cpp:53,56,57        (the LIVE parser, parse_json)
```
`jsmn_parse` / `jsmn_init` are **also** called from `firestarter.cpp:53-57`, so deleting `json_init` cannot free the jsmn library either. **Expected flash saving: 0 bytes.** ✓ The folded todo's "any flash saving is a bonus, not the justification" is exactly right, and the plan must **not** count it toward D-12's budget — measured, there is nothing to count.

**Three edit points, not two:** `src/json_parser.c:42-65` (definition), `include/json_parser.h:19` (declaration), and `test/native/avr/test_read_timing/test_read_timing_params.cpp:70-72` (the now-stale explanatory comment — the local `parse_json` helper it justifies should stay, since it is the right harness, but its rationale sentence must change from "json_init is broken" to "json_init was deleted in Phase 149").

### (c) `DATA_BUFFER_SIZE` and the board-dependent validation range

```c
// firestarter/include/firestarter.h:16-18
#ifndef DATA_BUFFER_SIZE
#define DATA_BUFFER_SIZE 512
#endif
```
```ini
# firestarter/platformio.ini:61-67  ([env:leonardo] only)
	; Leonardo (ATmega32u4, 2.5KB SRAM) uses the full 1K data buffer. The host reads
	; DATA_BUFFER_SIZE from the FW identity string and sizes host->fw chunks to 1022
	; (1024-2: CRC8 + decoder NUL slot). Phase 53 / #transport-protocol-verify.
	-D DATA_BUFFER_SIZE=1024
```

| Env | `DATA_BUFFER_SIZE` | Source |
|---|---|---|
| `uno` | **512** | default, `firestarter.h:17` (no override in `[env:uno]`, `platformio.ini:35-38`) |
| `uno328pb` | **512** | default (no override, `:52-55`) |
| `leonardo` | **1024** | `platformio.ini:67` |
| `native` / `native_nodevtools` | **512** | inherits `${env.build_flags}` (`:120-121`), which carries no override |

**Answer to R10's question: YES, the validation range `[1, DATA_BUFFER_SIZE]` is board-dependent** — `[1, 512]` on uno/uno328pb/native, `[1, 1024]` on leonardo. Consequences the plan must handle:

1. **Both delivered values (64, 128) are inside both ranges**, so for the delivered set the divergence is unobservable. The range choice is safe for this phase's data.
2. **A native test compiled for neither board.** `[env:native]` gets 512, so a native test cannot observe leonardo's 1024 bound at all. A case asserting "1024 is accepted" would pass on leonardo and **fall back to 64** on native/uno — a per-board behaviour divergence that no native test can see. **Do not write such a case.** Probe values that are unambiguous on every target: inside → 64, 128, 256; outside on all → 2048 (or 0, or 96 as a non-power-of-two).
3. **Consider whether `DATA_BUFFER_SIZE` is even the right bound.** It is convenient (a page larger than the transfer buffer is physically meaningless for this programmer) but it makes the *validation contract* board-dependent for no benefit at the delivered values. A board-invariant literal ceiling — 512, or 256 (the largest page any of the 746 rows carries) — would make the contract identical on all four envs and make the native test's coverage total rather than partial. **Claude's discretion-adjacent; the plan should state which bound it chose and why**, because "in `[1, DATA_BUFFER_SIZE]`" reads as one rule and is in fact two.
4. **Write-block sizes are multiples of 128 — confirmed, and `platformio.ini`'s comment is stale.** The advertised chunk is `DATA_BUFFER_SIZE` **verbatim**:
   ```c
   // firestarter/src/firestarter.cpp:209-210
   _ready[0] = (uint8_t)(((uint16_t)DATA_BUFFER_SIZE >> 8) & 0xFF);
   _ready[1] = (uint8_t)((uint16_t)DATA_BUFFER_SIZE & 0xFF);
   ```
   ```python
   # firestarter_app/firestarter/eprom_operations.py:436-442
   max_chunk = getattr(self.comm, "firmware_max_chunk", None) if self.comm else None
   if max_chunk is not None and max_chunk >= 1:
       return max_chunk
   # CAP-01 safe Uno-floor default: absent advertisement -> 512.
   return 512
   ```
   and `serial_comm.py:394-401` decodes it with a plausibility clamp to `[1, 4096]`. So the chunk is **512 or 1024**, both exact multiples of 128 — ✓ CONTEXT.md confirmed — and `platformio.ini:65-66`'s "1022 (1024-2)" is superseded by CAP-01 (§X-5 bonus). Since the flush test is on the **absolute** address anyway (`eeprom_28c.cpp:623`, `:634`), correctness does not depend on the multiple: §R3d's `base=100, size=200` case proves an arbitrary base and size still flush on true page boundaries.

### (d) App CI gate scope — measured, and `tools/` is NOT covered

```
# firestarter_app/.github/workflows/ci.yml:53, :78-90
python-version: '3.11'
run: pip install -e .[test]
run: ruff check firestarter/ tests/
run: ruff format --check firestarter/ tests/
run: python tools/check_mypy_watermark.py
run: pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70
```
```python
# firestarter_app/tools/check_mypy_watermark.py:106-115
    return [sys.executable, "-m", "mypy", "firestarter/", "tests/"]
```
```
# firestarter_app/pyproject.toml:131, :155, :174
select = ["E", "F", "I", "UP"]
python_version = "3.10"
# mypy_error_watermark = 35
```

| Gate | Path set | Bearing |
|---|---|---|
| `ruff check` / `ruff format --check` | `firestarter/ tests/` — **not `tools/`** | `build_db.py` and `diff_db.py` edits are **ungated** by ruff. Format them by hand to match. |
| mypy watermark (35) | `firestarter/ tests/` — **not `tools/`** | Same. A new host test in `tests/` **is** typed-checked; the emitter change is not. |
| coverage | `--cov=firestarter --cov-fail-under=70` | `tools/` is excluded from the numerator too, so the emit rule cannot move coverage; new `tests/` files only help |
| `select = ["E","F","I","UP"]` | — | C-7: every `# noqa: BLE001` is inert; keep excepts narrow by hand |
| Python version | CI **3.11**, mypy config **3.10**, devcontainer **3.12** | A local pass is **not** a CI pass. Run `tools/ci_parity.sh` (§R7d) for the closest local approximation, and say "green locally on 3.12" rather than "green in CI" in any SUMMARY. |

---

## Architecture Patterns

### System Architecture Diagram

```
 UPSTREAM DATA                     HOST BUILD                        GENERATED DB
 ┌──────────────────┐    ┌──────────────────────────────┐    ┌──────────────────────┐
 │ infoic.xml       │    │ build_db.py                  │    │ chip_database.json   │
 │ <database        │───▶│  :450-474  DIP-parallel filt.│───▶│  746 rows            │
 │  type=INFOIC2PLUS│    │  :478 proto_id ──────┐       │    │  programming:        │
 │ per <ic>:        │    │  :490 raw_page_size ─┤       │    │   algorithm          │
 │  protocol_id     │    │  :317-402 classify() │       │    │   infoic_page_size_  │
 │  page_size       │    │    arm2 :371-386     │       │    │     raw   (all)      │
 │  flags, pin_map  │    │    PROMOTES 66→0x0D  │       │    │   page_size          │
 └──────────────────┘    │    arm4 :393 native  │       │    │     ┌ 2 curated 0x05 │
   (2 curated rows       │  :718-724 part_number│       │    │     └ 18 native 0x0D ◀── NEW (D-01/D-03)
    via _PAGE_SIZE_      │  :786-795 EMIT ◀─────┘       │    └──────────┬───────────┘
    BY_PART :127-140)    │      ▲ NEW provenance arm    │               │
                         └──────┼──────────────────────-┘               │
 tools/extra_chips.json ────────┘  (2 authored TI rows,                 │
   BYPASSES classify() + emitter    no page keys — D-02)                │
                                                                        ▼
 HOST RUNTIME                                              ┌────────────────────────┐
                                                           │ database.py            │
   ┌───────────────────────────────────────────────────────│  :417-419 _map_data    │
   │                                                       │    → data["page_size"] │
   │                        ALREADY BUILT — ZERO CHANGE    │  :552-553 convert_to_  │
   │                                    (D-02)             │    programmer          │
   │                                                       │    → "page-size"  WIRE │
   │  constants.py:148 JSON_KEY_PAGE_SIZE = "page-size" ◀──┤                        │
   │        ▲ PGSZ-03 parity scan (D-18)                   └───────────┬────────────┘
   │        │                                                          │
   │        │                                       COBS/CRC8 @250000  │ {"cmd":2,...,
   │        │                                       (serial_comm.py,   │  "page-size":128}
   │        │                                        UNCHANGED)        │
 ══╪════════╪══════════════════ REPO BOUNDARY ═══════════════════════╪═══════════════
   │        │                                                          ▼
 FIRMWARE   │                                          ┌───────────────────────────┐
            │                                          │ firestarter.cpp           │
            │                                          │  :33  global handle       │
            │                                          │       (NO memset!)        │
            │                                          │  :131 init_programmer_    │
            │                                          │       framed              │
            │                                          │  :78  json_parse ─────┐   │
            └── scan src/json_parser.c ────┐           │  :93  configure_memory│   │
                (scan_paths.py entry, NEW) │           └───────────────────────┼───┘
                                           ▼                                   │
                         ┌──────────────────────────────────────┐              │
                         │ json_parser.c                        │◀─────────────┘
                         │  :56-66  PROGMEM key strings         │
                         │          + key_page_size      ◀ NEW  │
                         │  :73-79  key_parsers[] (self-sizing) │
                         │          + one row            ◀ NEW  │
                         │  :82-89  optional-key RESETS         │
                         │          + page_size = 0      ◀ NEW  │ D-05
                         │  :113    dispatch loop               │
                         │  :133    unknown-key SKIP     ◀ D-11 │
                         │  :296-298 extract_int precedent      │
                         └──────────────┬───────────────────────┘
                                        │  handle-><page field>   (firestarter.h:188-224, NEW)
                                        ▼
   ┌─────────────────────────────────────────────────────────────────────┐
   │ eeprom_28c.cpp                                                      │
   │  :189-221 configure_eeprom28c  ── RESOLVE + VALIDATE mask (D-06/07) │
   │     │        power of two in range? ── no ──▶ fall back to          │
   │     │                                        AT28C_PAGE_SIZE_       │
   │     │                                        FALLBACK (64) SILENTLY │
   │     │        (D-10 renames PAGE_SIZE :33)                           │
   │     ├──▶ :448 write_init  (early return :454 — do NOT resolve here) │
   │     └──▶ :537 write_execute        ONCE PER BLOCK                   │
   │            :622 for each byte i                                     │
   │            :623   address = handle->address + i     ABSOLUTE        │
   │            :634   page_end = ((address+1) & mask) == 0   ◀ D-06     │
   │            :636   if (page_end || last_byte)                        │
   │            :644     wait_for_page_write   ── DQ7 poll, 2 reads      │
   │            :648     verify_page_readback  ── window bytes           │
   │            :652     window_start = i + 1                            │
   └─────────────────────────────────────────────────────────────────────┘
                        │                              │
                        │ read seam: handle->           │ register writes:
                        │ firestarter_get_data          │ rurp_write_to_register
                        ▼                               ▼
             ┌──────────────────────────┐   ┌──────────────────────────┐
             │ NATIVE TEST OBSERVABLE   │   │ HOST_STUBS_RECORD_BUS    │
             │ mock get_data + counter  │   │ (reg,data) pairs, cap256 │
             │ ⇒ FLUSH COUNT  ◀── D-09  │   │ ⇒ CANNOT see flushes     │
             └──────────────────────────┘   └──────────────────────────┘

 NON-CHANGE (D-08): flash_5v_page.cpp:27-31 mem_size band table stays frozen.
   W29C020/W29C040 already receive wire page-size and IGNORE it — the heuristic
   and the wire value agree numerically (128 / 256), so nothing is observable.
```

### Recommended edit map (not a new project structure — this phase adds no files to either sub-repo's source tree)

```
firestarter/                                 (v1.32 branch, forked off origin/beta)
├── include/
│   ├── firestarter.h              :188-219  + one handle field
│   └── json_parser.h              :19       − json_init declaration
├── src/
│   ├── json_parser.c              :50-54    − json_init definition
│   │                              :56-66    + PROGMEM key string
│   │                              :73-79    + key_parsers[] row
│   │                              :82-89    + optional-key reset
│   │                              :296-298  + extract_int getter (near siblings)
│   └── proms/eeprom_28c.cpp       :19-33    ~ comment (D-04) + constant rename (D-10)
│                                  :189-221  + resolve/validate mask
│                                  :634      ~ mod → mask
├── test/native/avr/
│   ├── test_read_timing/…params.cpp         + parse case, + absent case, + unknown-key case
│   │                              :62-64    ~ stale json_init comment
│   ├── test_val_eeprom28c/….cpp   :204,:256 ~ PAGE_SIZE comment refs
│   │                                        + flush-cadence cases (D-09)
│   └── test_eeprom28c_sdp/….cpp   :1475,:1486,:1540  ~ PAGE_SIZE comment refs
├── scripts/
│   ├── check_size_baseline.py     :167      + new exemption constant
│   │                              :274-296  ~ 5-tuple
│   │                              :334,:536 ~ both call sites + messages
│   └── baseline/size_baseline.json          ~ D-14 phase-end update (+ fix firmware_tree_sha, §X-3)
└── tests/
    ├── test_check_size_baseline.py          ~ 4 legs
    └── fixtures/planted_size_baseline_policy_{leonardo_growth,uno_over_band}.log  ~ re-plant

firestarter_app/                             (already on the v1.32 branch)
├── tools/build_db.py              :121-140  ~ stale flash4_page_size comment
│                                  :485-486  ~ "not consulted by any decision" now false
│                                  :786-795  + provenance-keyed emit arm
├── firestarter/
│   ├── database.py                :414-419  ~ stale comment
│   │                              :549-553  ~ stale comment
│   └── constants.py               :145-148  ~ three false clauses → true
├── tests/
│   ├── scan_paths.py              :30,:94-129,:259  + entry, ~ two stale counts
│   ├── test_wire_dict_equivalence.py        ~ golden-plus-deltas
│   ├── golden/wire_dict_expected_deltas_149.json    + NEW fixture (18 deltas)
│   ├── test_json_key_parity.py              + NEW (D-18)
│   ├── test_page_size_invariants.py         + NEW (D-07 exhaustive host proof)
│   └── fixtures/                            + planted json_parser.c fixtures (D-18 RED legs)
└── README.md                      :61-90    + one ### subsection (D-20)

.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/
├── 149-check-claims.py                      + NEW (D-19, from 146-check-claims.py)
├── test_check_claims_v132.py                + NEW paired suite
├── fixtures/                                + planted overclaim fixtures
└── 149-PAGE-SIZE.md                         + NEW review artifact (D-16)

.planning/todos/pending/                     + 2 new todos (D-04.1, D-04.2), + 1 (D-09 INFO log)
                                             − remove-dead-json-init-sizeof-pointer-bug (folded)
```

### Pattern 1: Optional wire key, five points, self-sizing table

**What:** an optional host→firmware JSON key that degrades to a firmware default when absent.
**When to use:** any per-chip parameter the DB knows and the firmware currently hardcodes.
**Example — the live Phase 44 template, all five points in one view:**
```c
// (1) firestarter/src/json_parser.c:76 — PROGMEM key string
const char key_read_settling[] PROGMEM = "read-settling-delay";
// (2) firestarter/src/json_parser.c:164 — key_parsers[] row (table is self-sizing at :113)
    {key_read_settling, get_read_settling},
// (3) firestarter/src/json_parser.c:20 fwd decl + :350-357 definition
bool get_read_settling(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) { ... }
// (4) firestarter/include/firestarter.h:198 — handle field
    uint32_t read_settling_us;   /* ... 0 = no settling delay */
// (5) firestarter_app/firestarter/constants.py:142 — paired constant + sync note
JSON_KEY_READ_SETTLING_DELAY = "read-settling-delay"
```
**What Phase 149 adds that Phase 44 lacks:** point (6), the reset in `json_parse:82-89` (D-05 — Phase 44 skipped it, §R2d), and point (7), the enforced parity scan (D-18 — Phase 44's sync note is a comment nobody checks).

### Pattern 2: Golden-plus-committed-deltas instead of re-baselining

**What:** when a change legitimately perturbs a golden, keep the golden and commit an explicit delta list.
**When to use:** any change that would otherwise be "re-capture the golden and say so in the commit message".
**Why here:** Phase 148's central claim — its migration changed nothing on the wire — stays legible in the same file, and a later phase cannot quietly re-baseline the diff away. See §R6d for the concrete shape, including the anti-laundering assertion that pins the golden's own `page-size` carriers at exactly 2.

### Pattern 3: Named, SHA-attributed exemption instead of a moved anchor

**What:** when growth genuinely must be admitted, add a distinct named constant with its own justification rather than widening a band or re-anchoring the reference.
**Source:** `check_size_baseline.py:125-166` is a complete worked example including the three rejected alternatives.
**Why it matters here:** `size_baseline_base01.json:re_anchor_note` records the lesson directly — *"a green `--policy merge05` run after this commit means the anchor moved, not that flash growth stayed inside the original v1.24 band (D-14)."* PGSZ-04 exists to stop that happening a third time.

### Anti-Patterns to Avoid

- **Counting flushes from `bus_recording_count()`.** The recorder sees register writes, not reads; the poll reads go through the mocked `get_data` seam. It also caps at 256 entries (`test_val_eeprom28c.cpp:208`), which a 512-byte geometry would overflow. Count in the mock.
- **Asserting a `diff_db` bucket move.** Measured unreachable (§X-1). Assert census invariance plus 18 compound-secondary tokens.
- **Copying the claim-gate pattern table verbatim.** `\bproven\b` makes PGSZ-05's own phrase a violation (§X-2).
- **A `raw != 64` filter in the emitter.** D-03's explicitly rejected direction; it would also couple the host's emit condition to a firmware constant.
- **A runtime `%` by a variable divisor in the per-byte loop.** Pulls `__udivmodsi4` into a build with 0 bytes of MERGE-05 headroom (D-06).
- **Resolving the mask after `write_init:456`.** Skipped on chip-ID mismatch, and invisible to the existing native suite, which never calls `firestarter_operation_init` (§R4c).
- **A native case asserting page 1024 is accepted.** Passes on leonardo, falls back to 64 on native/uno — a divergence no native test can observe (§R10c).
- **`glob`-ing the claim gate's target list.** `149-CONTEXT.md` and `149-RESEARCH.md` both contain `proven` (§R9e).
- **Extending `_PAGE_SIZE_BY_PART`, or adding any per-chip guess table under a new name.** REQUIREMENTS.md §Out of Scope / DATA-04; three such tables were deleted in Phase 70.
- **Hand-editing `chip_database.json`.** C-1.
- **Creating `CHANGELOG.md`.** Contradicts Phase 148's recorded decision; the surface is `README.md:61` (§R9f).
- **Counting the `json_init` deletion toward D-12's budget.** Measured 0 bytes (§R10b).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| "Is the firmware checkout present?" | A `not <some file>.exists()` proxy | `tests/fw_presence.py`'s `requires_fw` / `fw_path` | `fw_presence.py:10-17` records the measured defect: seven modules each had their own proxy, and a firmware **rename** flipped their gate legs PASS→SKIP at exit 0 |
| Cross-repo scan-path tracking | A per-test path constant, or a `grep`-derived list | `tests/scan_paths.py`'s committed inventory | `:21-27` — a derived list re-creates the `firestarter` name-collision trap; `:36-53` measured 7 of 11 grep hits resolving into the app's own package |
| Proving `FW_ROOT`-absent behaviour | `monkeypatch.setenv` | A subprocess with `FIRESTARTER_FW_ROOT` in `env`, or `tools/ci_parity.sh` leg 1 | Import-time binding (`fw_presence.py:35-45`) — `monkeypatch` has literally no effect |
| Flush-boundary arithmetic | A per-block byte counter | The mask AND against the **absolute** address | A per-block counter breaks on an unaligned `--address` write; §R3d measures the difference |
| Page-size validation | A firmware log + a new message ID | Silent firmware fallback + an exhaustive host test | D-07; a new message ID needs `messages.toml` + a PROGMEM string + a codegen run against a 0-byte budget, to report a condition only our own host could cause |
| A claim-gate target list | A glob or a directory walk | An enumerated list built from `_HERE` + the locality self-check | `146-check-claims.py:110-113` (a glob sweeps in CONTEXT.md) and `:235-269` (the cross-phase-copy defect) |
| Admitting flash growth | Re-anchoring BASE-01, or widening a band | A new named SHA-attributed exemption constant | `size_baseline_base01.json:re_anchor_note` — a green after an anchor move means the anchor moved, not that growth shrank |
| A wire-golden conflict | Re-capturing the golden | Golden + committed expected-delta fixture | D-17; a re-capture erases Phase 148's own central claim from the same file |
| Firmware message strings | Editing `include/messages.h` | `tools/catalog/messages.toml` + `codegen.py` | C-5; `messages.h` is codegen-generated and there is a CI drift gate (`build.yml:114`). This phase should need **neither** |
| JSON tokenising | Anything | `jsmn` via `firestarter.cpp:53-57`'s live path | And note `json_init` is the dead wrapper this phase deletes (§R10b) |

**Key insight:** almost every mechanism this phase needs already exists and was built *because* a hand-rolled version failed in a measured, documented way. The phase's real work is wiring, measuring, and writing honestly — not building.

---

## Common Pitfalls

### Pitfall 1: The stale `page_size` across two commands in one session
**What goes wrong:** writing AT28C010 (128), then a floor chip in the same session, leaves the second chip flushing on 128-byte boundaries — the exact page overrun PGSZ-02 exists to prevent.
**Why it happens:** `firestarter_handle_t handle;` is a single file-scope global (`firestarter.cpp:33`) with **no** per-command `memset`; `json_parse` resets only the keys listed at `:82-89`.
**How to avoid:** D-05's reset. Add `handle-><page field> = 0;` in that block.
**Warning signs:** a native test that only ever parses one JSON string per handle cannot detect this. The detecting test parses **two** strings into the **same** handle — the delivered one first, then one without the key — and asserts the field is 0 the second time. (The existing `test_read_timing` cases all use a fresh `make_handle()` per case, so none of them would catch it. This is a new case shape, not a copy.)

### Pitfall 2: The mask is never resolved because the existing suite skips `operation_init`
**What goes wrong:** `test_val_eeprom28c`'s cases call `configure_memory(&h)` then `h.firestarter_operation_main(&h)` directly (`:216-218`, `:246-249`, `:266-269`) — they **never** call `firestarter_operation_init`. A mask resolved in `eeprom28c_write_init` stays 0, mask 0 flushes every byte, and `test_fix06_page_boundary_window_readback` (`:260-302`) changes behaviour.
**Why it happens:** the suite tests the configure + main phases, by design.
**How to avoid:** resolve in `configure_eeprom28c` (§R4c option 1), or fall back at point of use on `mask == 0`.
**Warning signs:** the three `test_fix06_*` cases going RED, **or** going GREEN for a changed reason. If they change at all, the resolution site is wrong.

### Pitfall 3: The claim gate cannot be satisfied by its own required phrase
**What goes wrong:** `\bproven\b` matches "software-proven"; the gate demands the phrase and forbids the word.
**Why it happens:** `\b` fires after a hyphen. Documented at `146-check-claims.py:63-65`.
**How to avoid:** §X-2 — narrow to `(?<!software-)\bproven\b` and keep a negative control proving a bare `proven` still fails.
**Warning signs:** the gate goes RED on `149-PAGE-SIZE.md` immediately after the required phrase is added. If the first response is to delete the phrase, PGSZ-05 is lost.

### Pitfall 4: The new exemption silently disarms the MERGE-05 tripwire
**What goes wrong:** adding exemption `N` makes the planted +97 B leonardo fixture fall **inside** the allowance, so `test_policy_merge05_admits_the_documented_defect_fix` (`:374-459`) stops being a negative control while still claiming to be one.
**Why it happens:** the fixture's 27003 B was chosen as `26906 + 96 + 1`.
**How to avoid:** re-plant both fixtures at `BASE-01 + band + 96 + N + 1` and update the four asserted literals.
**Warning signs:** that test going **GREEN** without an edit is the failure. Firmware CI runs it (`build.yml:161`), so it will surface — but as a passing test, which is the worst kind of signal.

### Pitfall 5: D-13's cold baseline taken after the first edit
**What goes wrong:** criterion 4's "captured before the first firmware edit" is unsatisfiable retroactively, and the phase's flash delta becomes unattributable — exactly the MERGE-05 failure mode PGSZ-04 exists to stop.
**Why it happens:** the branch does not exist yet, so the natural first instinct is to fork, start editing, and measure later.
**How to avoid:** fork → cold capture → **commit the capture** → then edit. Make the committed capture a Wave 0 deliverable with its own SHA.
**Warning signs:** no committed pre-edit measurement artifact at the point the first `src/` change is staged.

### Pitfall 6: Measuring the fork-point delta against `firmware_tree_sha`
**What goes wrong:** `size_baseline.json`'s recorded tree SHA (`3d8ec49` = `6cc4795`, Phase 144) **predates** the +96 B its own AVR figures record (§X-3).
**How to avoid:** reason by content (`git diff --stat <tree> origin/beta`), and fix the field in D-14's update.
**Warning signs:** a plan sentence of the form "the baseline was measured at `3d8ec49`, and `3d8ec49..origin/beta` contains N commits, therefore…". That reasoning is unsound.

### Pitfall 7: A warm warning re-measure written into the baseline
**What goes wrong:** warm native reads 998, cold reads 1166. Writing 998 makes the next **cold** CI run RED.
**Why it happens:** local re-runs are warm by default; `pio` reuses `.pio/build/`.
**How to avoid:** `rm -rf .pio/build/<env>` then one invocation. `size_baseline.json:meta.warm_vs_cold_correction` documents the whole derivation.
**Warning signs:** any watermark figure that went **down** without a `rm -rf` in the transcript.

### Pitfall 8: A native test that passes with the mask hardcoded
**What goes wrong:** if the test asserts only "a 128-byte-page handle completes without error", it passes whether or not the 128 was used. Criterion 1 says *observed to deliver 128*.
**How to avoid:** assert the flush **count** (2 vs 1 on a 128-byte geometry), and include the absent-field leg reproducing the 64 count. Three numbers, one geometry.
**Warning signs:** a test whose assertion does not contain a number that differs between the 64 and 128 cases.

### Pitfall 9: The `extra_chips.json` back door
**What goes wrong:** an authored row can carry a `page_size` that never passed D-01's provenance rule, because that path bypasses `classify()` and the emitter entirely.
**How to avoid:** fold the check into D-07's exhaustive host test — every emitted `page_size` in the built DB must be either a `_PAGE_SIZE_BY_PART` row or an upstream-native `0x0D` row.
**Warning signs:** a D-07 test that only checks power-of-two-ness. That is necessary but not sufficient; 256 is a power of two and would be wrong for a promoted row.

### Pitfall 10: Two key spellings, one flow
**What goes wrong:** the internal dict key is `page_size` (underscore, `database.py:419`, `:552`); the **wire** key is `page-size` (hyphen, `:553`). A firmware PROGMEM string or a parity assertion written against the underscore form silently never matches.
**How to avoid:** the firmware key and `JSON_KEY_PAGE_SIZE` are both the **hyphen** form. D-18's assertion compares the hyphen form.
**Warning signs:** a parity test that passes trivially, or a firmware key that never dispatches. §R7c assertion 2 (the key string must appear in `key_parsers[]`, not merely exist) is the guard.

### Pitfall 11: Worktrees leave submodules empty
**What goes wrong:** a plan that only **reads** a submodule breaks too, and the `commits_land_in:` gate under-detects when `files_modified` is used instead.
**How to avoid:** every plan in this phase declares `commits_land_in:` explicitly — `firestarter`, `firestarter_app`, or the meta repo. Do not execute this phase from a git worktree.
**Warning signs:** an empty `firestarter/` or `firestarter_app/` directory at executor start.

---

## Code Examples

### Enumerating flush points from production's own predicate (verified equivalence)
```c
/* Exact replica of eeprom_28c.cpp:623 / :634 / :635 / :636.
   Source: firestarter/src/proms/eeprom_28c.cpp @ 6992271 */
for (uint32_t i = 0; i < data_size; i++) {
    uint32_t address = base + i;                              /* :623 absolute */
    int page_end = ((address + 1) & (page_size - 1)) == 0;    /* :634 D-06 mask form */
    int last     = (i == data_size - 1);                      /* :635 */
    if (page_end || last) { /* flush: wait_for_page_write + verify_page_readback */ }
}
```
Measured equivalent to the `%` form on `{base, size, page}` ∈ `{(0,128,64), (0,128,128), (0,512,64), (0,512,128), (56,16,64), (56,16,128), (100,200,128)}`, and mask 0 flushes every byte. §R3d.

### The parity-scan module skeleton (D-18)
```python
# Source pattern: firestarter_app/tests/test_cap03_ack_layout_parity.py:68-89
import re
from pathlib import Path
import pytest
from firestarter.constants import JSON_KEY_PAGE_SIZE
from tests.fw_presence import FW_REPO_PRESENT, fw_path, requires_fw

_HERE = Path(__file__).resolve().parent
FIRMWARE_PARSER_SOURCE = fw_path("src", "json_parser.c")   # module scope; hard-fails on rename

_PROGMEM_KEY_RE = re.compile(
    r'const\s+char\s+(?P<ident>key_\w+)\s*\[\s*\]\s+PROGMEM\s*=\s*"(?P<key>[^"]+)"\s*;'
)
_PARSERS_TABLE_RE = re.compile(
    r'key_parser_t\s+key_parsers\s*\[\s*\]\s+PROGMEM\s*=\s*\{(?P<body>.*?)\};', re.DOTALL
)

@requires_fw
def test_page_size_key_string_matches_constants_py() -> None:
    src = FIRMWARE_PARSER_SOURCE.read_text(encoding="utf-8")
    keys = {m.group("ident"): m.group("key") for m in _PROGMEM_KEY_RE.finditer(src)}
    assert keys, "extraction found ZERO PROGMEM keys -- the regex drifted, not the source"   # non-vacuity
    assert JSON_KEY_PAGE_SIZE in keys.values(), ...
    # and the identifier must be DISPATCHED, not merely declared:
    ident = next(i for i, k in keys.items() if k == JSON_KEY_PAGE_SIZE)
    body = _PARSERS_TABLE_RE.search(src).group("body")
    assert ident in body, f"{ident} declared but absent from key_parsers[] -- never dispatched"

# The planted-violation legs carry NO @requires_fw: they read committed fixtures,
# so they stay live in app CI where the sibling checkout is absent.
def test_gate_fires_on_a_key_declared_but_not_dispatched(monkeypatch) -> None:
    monkeypatch.setattr(<module>, "FIRMWARE_PARSER_SOURCE",
                        _HERE / "fixtures" / "planted_json_parser_undispatched_key.c")
    ...
```
The `assert keys` line is the non-vacuity guard: without it, a regex that matches nothing makes every downstream assertion trivially satisfiable — the `test_revision_constants_parity.py:90` shape ("an empty define set would make every downstream assertion...").

### The provenance-keyed emit arm (D-01/D-03)
```python
# firestarter_app/tools/build_db.py, replacing :786-795
                        # D-01/D-03 (149): provenance-keyed. The page_size attribute
                        # is meaningful for the algorithm that CONSUMES it; a record
                        # filed under 0x07/0x0B is not evidence about a 28C page
                        # buffer. 18 upstream-native 0x0D rows qualify (15 at 128,
                        # 3 at 64); the 66 rows classify() PROMOTES into 0x0D keep the
                        # firmware floor (D-04). Disjoint from _PAGE_SIZE_BY_PART: both
                        # curated rows are upstream 0x05, so no row satisfies both arms.
                        # software-proven and unvalidated on silicon.
                        **(
                            {"page_size": _PAGE_SIZE_BY_PART[_canon]}
                            if _canon in _PAGE_SIZE_BY_PART
                            else {"page_size": raw_page_size}
                            if proto_id == 0x0D
                            else {}
                        ),
```

---

## Validation Architecture

*(`.planning/config.json` has no `workflow.nyquist_validation` key → treated as ENABLED.)*

### Test Framework

| Property | Value |
|----------|-------|
| Firmware unit framework | Unity via PlatformIO, `test_framework = unity` (`firestarter/platformio.ini:71`) |
| Firmware script framework | pytest (`firestarter/tests/`) — 314 tests |
| Host framework | pytest 9.1.1 + syrupy snapshots (`firestarter_app/tests/`) — 1641 tests, 32 snapshots |
| Firmware native config | `firestarter/platformio.ini` `[env:native]` `:69-119`, `test_filter` 17 entries |
| Host config | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]`, `addopts = "-ra -q"` |
| Quick run (native, this phase's suites) | `cd firestarter && pio test -e native -f native/avr/test_val_eeprom28c -f native/avr/test_read_timing` — **5.8 s** |
| Quick run (firmware scripts) | `cd firestarter && python3 -m pytest tests/ -q` — **10.7 s** |
| Quick run (host, targeted) | `cd firestarter_app && python3 -m pytest tests/test_wire_dict_equivalence.py tests/test_scan_paths_resolve.py -o addopts="" -q` |
| Full suite (native) | `cd firestarter && pio test -e native` and `pio test -e native_nodevtools` (141 cases / 17 suites each, both must agree) |
| Full suite (host) | `cd firestarter_app && python3 -m pytest tests/ -o addopts="" -q` — **218 s** |
| CI-parity local run | `cd firestarter_app && tools/ci_parity.sh` — 4 legs incl. the empty-`FW_ROOT` skip leg |

### Phase Requirements → Test Map

| Req | Behavior | Test type | Automated command | File exists? |
|---|---|---|---|---|
| PGSZ-01 | 18 upstream-native `0x0D` rows gain `programming.page_size`; the 66 promoted rows and AT28C256 do not | unit (host) | `python3 -m pytest tests/test_page_size_invariants.py -o addopts="" -q` | ❌ Wave 0 |
| PGSZ-01 | Every emitted `page_size` across all 746 is a power of two in range **and** comes from a curated or upstream-native row (D-07 + §Pitfall 9) | unit (host) | same file | ❌ Wave 0 |
| PGSZ-01 | Wire capture equals golden **plus exactly the 18 named deltas**; golden still carries exactly 2 `page-size` records | unit (host) | `python3 -m pytest tests/test_wire_dict_equivalence.py -o addopts="" -q` | ✅ exists — modified + new fixture |
| PGSZ-01 | Wire key union stays exactly 9 | unit (host) | same file, `test_wire_key_union_is_exactly_nine_keys` | ✅ passes unchanged |
| PGSZ-01 | `diff_db` census invariant: exit 0, 744 changed, 0 unexplained, 0 new, 0 missing, buckets `686/56/2`, +18 `programming.page_size` secondaries | integration (host) | `python3 tools/diff_db.py; echo $?` | ✅ exists (§X-1 gives the reachable assertion) |
| PGSZ-01 | `"page-size":128` parsed off the wire into the handle field | unit (native) | `pio test -e native -f native/avr/test_read_timing` | ✅ suite exists — new case |
| PGSZ-02 | Absent field ⇒ handle field 0 ⇒ handler uses the 64 floor: **flush count 2** on a 128-byte geometry | unit (native) | `pio test -e native -f native/avr/test_val_eeprom28c` | ✅ suite exists — new case |
| PGSZ-02 | Delivered 128 ⇒ **flush count 1** on the same geometry | unit (native) | same | ✅ suite exists — new case |
| PGSZ-02 | Field resets to 0 between two commands on the **same** handle (D-05) | unit (native) | `pio test -e native -f native/avr/test_read_timing` | ✅ suite exists — new case (novel shape, §Pitfall 1) |
| PGSZ-02 | An unknown key before a known one does not desync the token walk (D-11) | unit (native) | same | ✅ suite exists — new case |
| PGSZ-02 | A non-power-of-two / out-of-range value falls back to 64 silently (flush count 2, no log) | unit (native) | `pio test -e native -f native/avr/test_val_eeprom28c` | ✅ suite exists — new case |
| PGSZ-02 | The three pre-existing `test_fix06_*` cases are **byte-unchanged in behaviour** | regression (native) | same | ✅ passes unchanged (this is the §Pitfall 2 control) |
| PGSZ-03 | `JSON_KEY_PAGE_SIZE` equals the PROGMEM key string in `src/json_parser.c` **and** that identifier appears in `key_parsers[]` | unit (host, scans fw) | `python3 -m pytest tests/test_json_key_parity.py -o addopts="" -q` | ❌ Wave 0 |
| PGSZ-03 | All 3 `JSON_KEY_*` constants map two-way, with a named firmware-side exemption tuple | unit (host, scans fw) | same file | ❌ Wave 0 |
| PGSZ-03 | `src/json_parser.c` is in the committed inventory and resolves | unit (host) | `python3 -m pytest tests/test_scan_paths_resolve.py -o addopts="" -q` | ✅ exists — one entry added |
| PGSZ-03 | The gate SKIPS (not fails) with no firmware checkout, and its planted legs stay LIVE | integration (host) | `FIRESTARTER_FW_ROOT=$(mktemp -d) python3 -m pytest tests/ -rs -o addopts="" -q` (= `tools/ci_parity.sh` leg 1 + `-rs`) | ✅ mechanism exists |
| PGSZ-03 | The gate goes RED on a planted undispatched / mismatched key | negative control (host) | `python3 -m pytest tests/test_json_key_parity.py -o addopts="" -q` (fixture legs) | ❌ Wave 0 + fixtures |
| PGSZ-04 | Cold baseline captured at the v1.32 fork, **before** the first edit, for all three envs | manual-then-recorded | `rm -rf .pio/build/<env> && pio run -e <env>` × 3, output committed | ❌ Wave 0 (P-2) |
| PGSZ-04 | Post-change flash + RAM measured cold for all three envs; deltas stated | manual-then-recorded | same procedure, post-edit | ❌ (end of phase) |
| PGSZ-04 | Default-mode byte-identity gate + `--policy merge05` both exit 0 against BASE-01 | integration (fw script) | `python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --log uno=… --log uno328pb=… --log leonardo=…` | ✅ script exists |
| PGSZ-04 | The tripwire is still ARMED one byte past the **new** allowance | negative control (fw) | `python3 -m pytest tests/test_check_size_baseline.py -q` with re-planted fixtures | ✅ exists — 4 legs + 2 fixtures modified |
| PGSZ-04 | AVR warnings `== 0`; native `<= 1166` on both pinned envs | integration (fw script) | `python3 scripts/check_build_warnings.py --rebuild …` (cold) | ✅ script exists |
| PGSZ-04 | `native` / `native_nodevtools` still agree on `{cases, suites, all_passed}`; suites stays 17 | integration (fw) | `pio test -e native` + `pio test -e native_nodevtools`, compared | ✅ mechanism exists (`envs_agree`) |
| PGSZ-05 | Every 149 artifact contains the literal phrase and zero forbidden claims | integration (meta) | `python3 .planning/phases/149-*/149-check-claims.py` | ❌ Wave 0 |
| PGSZ-05 | The gate goes RED on a planted overclaim, GREEN after revert; both transcripts committed | negative control (meta) | same + `python3 -m pytest .planning/phases/149-*/test_check_claims_v132.py -q` | ❌ Wave 0 + fixtures |
| PGSZ-05 | The surviving `proven` pattern still fires on an unqualified "proven" (§X-2) | negative control (meta) | same fixture suite | ❌ Wave 0 |
| PGSZ-05 | `0x0D` rows' `support_status` byte-unchanged; AT28C256's wire dict byte-unchanged | unit (host) | `python3 -m pytest tests/test_page_size_invariants.py -o addopts="" -q` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit (firmware):** `pio test -e native -f native/avr/test_val_eeprom28c -f native/avr/test_read_timing` (5.8 s) + `python3 -m pytest tests/ -q` (10.7 s)
- **Per task commit (host):** targeted module run, e.g. `python3 -m pytest tests/test_wire_dict_equivalence.py tests/test_json_key_parity.py tests/test_page_size_invariants.py -o addopts="" -q`
- **Per task commit (meta):** `python3 .planning/phases/149-*/149-check-claims.py` — under a second
- **Per wave merge (firmware):** `pio test -e native` **and** `pio test -e native_nodevtools` (both, compared) + `python3 -m pytest tests/ -q` + `pio run` (all three AVR envs link)
- **Per wave merge (host):** `python3 -m pytest tests/ -o addopts="" -q` (218 s) + `ruff check firestarter/ tests/` + `ruff format --check firestarter/ tests/` + `python tools/check_mypy_watermark.py`
- **Phase gate:** cold `pio run` × 3 + `check_size_baseline.py` default **and** `--policy merge05` + cold `check_build_warnings.py` + `tools/ci_parity.sh` (all 4 legs) + `python3 tools/diff_db.py` + the claim gate — all green before `/gsd-verify-work`
- **Record gate:** allow **300 s** — `STATE.md` carries a ~52k-char single line; a short timeout returns rc=124 and reads like a RED

### Under-sampling risks — what each proof does NOT cover

| Proof | Under-samples if… | Honest ceiling |
|---|---|---|
| Native flush-count test (D-09) | it asserts only completion, or only that no error occurred | Proves the **firmware consumes** the value on the host compiler at `DATA_BUFFER_SIZE=512`. Proves **nothing** about an AVR build, about timing (`delay()` unstubbed — `host_stubs_common.inc:137-144`), or about any physical die accepting a 128-byte page load |
| Native absent-field test | it uses a fresh handle, missing the D-05 stale-value path | Proves the fallback for a *zero-initialised* handle. The stale-value case needs the two-parse-one-handle shape |
| Host wire golden (D-17) | the golden is re-captured, or the delta list is `>= 18` instead of `== 18` | Proves the **host emits** exactly 18 new `page-size` values. Says nothing about the firmware |
| `diff_db` census | phrased as a bucket move (§X-1) | Proves no chip became unexplained and the blast radius is 18 rows. It does **not** highlight the change — the label does not move |
| D-07 host invariant | it checks only power-of-two-ness | 256 is a power of two and would be wrong for a promoted row. Must also check provenance (and cover the `extra_chips.json` path) |
| PGSZ-03 parity | the regex matches nothing (vacuous), or the key is declared but not dispatched | Proves LAYOUT agreement on a key **string**. Does not prove the getter stores into the right field, nor that the handler reads that field |
| PGSZ-03 skip-leg | run without `-rs` (skips invisible under `-q`) | Proves the gate degrades to SKIP rather than ERROR. Does not prove it would have caught anything |
| Size gate | the script is never run (it runs in **no** workflow), or run warm, or run after the first edit | Proves the delta is inside the admitted allowance. Does not prove the growth was necessary |
| MERGE-05 tripwire | the planted fixtures are not re-planted for the new allowance (§Pitfall 4) | The negative control silently becomes a positive |
| Warning gate | re-measured warm (998 vs cold 1166) | Cold-only |
| Claim gate | its RED leg is never seen; or `\bproven\b` is dropped without a replacement negative control | Proves compliance with a **pattern table** only. `146-check-claims.py:87-95`: "It cannot detect an implied overclaim, a misleading omission, a wrong tone, or a true statement placed where it misleads" |
| Whole phase | any artifact reads the green as write-path validation | **The entire phase is software-only by construction.** No AT28C part exists in operator inventory (`PROJECT.md` §Current Milestone: v1.32); REQUIREMENTS.md §Out of Scope explicitly excludes bench validation of the page-size change |

### Criteria that are software-only by construction (Evidence Ceiling)

All five ROADMAP criteria are software-only. Explicitly:

1. **Criterion 1** ("observed to deliver 128") is satisfied by a **native flush-count** assertion (D-09) on a host compiler. It is not, and must not be described as, an observation on hardware.
2. **Criterion 2** (fallback) is satisfied by native tests. Its ceiling is the same.
3. **Criterion 3** (parity) is a source-text scan. It proves two files agree on a string, not that the round trip works on a board.
4. **Criterion 4** (flash/RAM) is a real measurement of real AVR binaries — the **only** criterion here whose evidence is about actual target code. It still says nothing about runtime behaviour.
5. **Criterion 5** (honesty) is satisfied by a pattern gate plus a human wording review. The gate alone is insufficient by its own donor's explicit non-claim.

**No criterion in this phase can be satisfied by, or should be phrased as requiring, silicon.** Adding one would create a hardware-gated criterion nothing can satisfy — which is precisely why REQUIREMENTS.md §Out of Scope names "Bench validation of the page-size change" as excluded.

### Wave 0 Gaps

- [ ] `firestarter_app/tests/test_page_size_invariants.py` — PGSZ-01 selection + D-07 exhaustive invariant + provenance + AT28C256 non-change + `extra_chips.json` back door
- [ ] `firestarter_app/tests/test_json_key_parity.py` — PGSZ-03 two-way parity (D-18)
- [ ] `firestarter_app/tests/fixtures/planted_json_parser_*.c` — the parity gate's RED legs (no `requires_fw`, so live in app CI)
- [ ] `firestarter_app/tests/golden/wire_dict_expected_deltas_149.json` — D-17's 18 deltas, generated from the golden
- [ ] `.planning/phases/149-*/149-check-claims.py` + `test_check_claims_v132.py` + `fixtures/` — D-19
- [ ] Cold pre-edit baseline capture at the v1.32 fork — P-1/P-2, blocking everything
- [ ] Re-planted `firestarter/tests/fixtures/planted_size_baseline_policy_{leonardo_growth,uno_over_band}.log` — after `N` is known
- [ ] New cases in `test_read_timing_params.cpp` and `test_val_eeprom28c.cpp` — extensions, not new files (D-15)

*No framework install is needed: Unity, PlatformIO, pytest and syrupy are all present and green (§P-4…P-7).*

---

## R11 — Sequencing and wave shape (recommendation)

Two hard serialisations dominate the shape:
- **S-1: fork + cold baseline before every firmware edit** (D-13, criterion 4). Nothing firmware-side can start first.
- **S-2: the exemption constant's value `N` is unknown until the firmware edit is built and cold-measured** (§R2 byte cost, §R8d). So the size-gate work is strictly downstream of the firmware seam and cannot be pre-authored.

Everything else is parallelisable. The DB side and the firmware side are genuinely independent (CONTEXT.md grants this as discretion) — they share no file, and `149-PAGE-SIZE.md` can carry their evidence in separate sections.

### Recommended wave shape

| Wave | Plans | `commits_land_in:` | Parallel? | Rationale |
|---|---|---|---|---|
| **0** | **A.** Fork `firestarter` off `origin/beta`; verify by content (§R10a's four checks); cold-capture all three envs; commit the capture + a `149-PAGE-SIZE.md` skeleton with the pre-edit figures | `firestarter` (fork + capture), meta (`149-PAGE-SIZE.md`) | **No — strictly first** | S-1. Blocks every firmware plan. Also the natural place to record the predicted 24920/24970/27002 so a mismatch is caught |
| **0** | **B.** D-19 claim gate: `149-check-claims.py` with `_DEFAULT_TARGETS = [149-PAGE-SIZE.md]` only, its paired suite, its fixtures; resolve the `\bproven\b` collision (§X-2) with a negative control; RED→GREEN transcripts | meta | **Yes — with A** | Touches no sub-repo. Arms the gate while artifacts are being written (§R9e option 1) |
| **1** | **C.** DB-side: the provenance emit arm (`build_db.py:786-795`), the three stale-comment fixes (§X-5), `test_page_size_invariants.py`, the D-17 delta fixture + reworked golden assertion, the `diff_db` census criterion | `firestarter_app` | **Yes — with D** | Independent of the firmware seam. **Requires** a `build_db.py` run by the executor (network fetch) — see the note below |
| **1** | **D.** Firmware seam: the 5-point key + D-05 reset, the `json_init` deletion (3 edit points), the mask resolve/validate, `:634` mod→mask, D-10 rename (8 occurrences / 3 files, §X-4), D-04 comment rewrite, new native cases in both suites | `firestarter` | **Yes — with C** | Depends only on Wave 0A |
| **2** | **E.** PGSZ-03 parity: `test_json_key_parity.py`, the `scan_paths.py` entry + two stale counts, planted fixtures, the `ci_parity.sh` leg-1 skip transcript | `firestarter_app` | **No** | Scans the firmware source D delivers |
| **2** | **F.** Post-change cold measurement (all three envs) + the new MERGE-05 exemption constant, `_merge05_flash_allowance` 5-tuple, both call sites + messages, the 4 broken test legs, both re-planted fixtures, cold warning re-measure | `firestarter` | **No** | S-2 — needs D's built binary to know `N` |
| **3** | **G.** D-14 `size_baseline.json` update (incl. the §X-3 `firmware_tree_sha` fix and the `native_envs` case-count bump on **both** pinned envs); D-16 `149-PAGE-SIZE.md` completed; D-20 README subsection; the 3 pending todos (D-04.1, D-04.2, D-09 INFO log); extend D-19's target list to every `149-*-SUMMARY.md` and re-run RED→GREEN | `firestarter` + `firestarter_app` + meta | **No — strictly last** | Closes the record. The claim gate must scan the final artifacts |

**Why 7 plans, not 4:** the four items that most often get folded into a neighbour and then skipped are (i) the `\bproven\b` resolution, (ii) the four broken size-gate test legs plus two fixtures, (iii) the parity gate's planted RED legs, and (iv) the `firmware_tree_sha` correction. Each is small; each is load-bearing; each is invisible if it rides along in someone else's plan.

### Cross-cutting notes for the planner

- **`commits_land_in:` per plan, never `files_modified`.** A worktree leaves submodules EMPTY, and a plan that only **reads** a submodule (plan E reads `firestarter/src/json_parser.c`) breaks too. Plan E must declare it reads `firestarter` even though it commits to `firestarter_app`.
- **Plan C must run `build_db.py`, which fetches `infoic.xml` over the network and has no CLI flags** — it writes straight to `firestarter_app/firestarter/data/chip_database.json` (`build_db.py:22`, `:436-440`). That is correct and necessary for an *execution* plan (C-1: the DB is generated). But it means (a) plan C needs network, (b) the regenerated DB will reflect whatever upstream is live at execution time, not the pinned copy, and (c) `diff_db.py`'s 744/0/0/0 result is the gate that catches any unrelated upstream drift. **The plan should assert the four `diff_db` numbers explicitly**, so an upstream change that arrives with this diff is caught rather than absorbed.
- **`149-PAGE-SIZE.md` needs both evidences separately** (CONTEXT.md's condition for splitting C and D): a DB-side section (provenance table, 15/3 lists, `diff_db` census, wire delta list) and a firmware-side section (the seam, flush-count transcripts, cold flash/RAM figures, leonardo headroom as a number, the MERGE-05 breach named). Wave 0A creates the skeleton; wave 3G completes it.
- **Record gate: 300 s timeout.** `STATE.md`'s single ~52k-char line.
- **Snapshot-and-diff `ROADMAP.md` before and after any `phase.complete`** — it has clobbered an unrelated phase's `**Plans:**` line before.
- **Re-check COMMITS after any interrupt.** A killed executor leaves commits, not just a dirty tree.
- **`gsd-tools query commit` can switch branches** on a stale milestone heading — check `HEAD` after each commit call, in **all three** repos.
- **Do not use `--auto` / `--chain` for plan B or G** — both carry human-verify-shaped gates (the wording review D-19 explicitly cannot discharge; the D-20 user-facing line), and auto mode auto-approves outward-facing gates.

---

## Security Domain

`security_enforcement` is not set to `false` anywhere in `.planning/config.json`, so it is treated as enabled. This is an embedded firmware + local CLI phase with no network surface, no auth, and no session — most ASVS categories are structurally inapplicable, and saying so explicitly is the point.

### Applicable ASVS categories

| ASVS category | Applies | Standard control |
|---|---|---|
| V2 Authentication | **no** | No user identity anywhere in this system; the serial link is a physical trust boundary |
| V3 Session Management | **no** | The three-phase INIT→MAIN→END state machine is a protocol, not a session; no credentials |
| V4 Access Control | **no** | Single local operator with physical access to the board |
| V5 Input Validation | **YES** | The new wire field is untrusted input crossing a repo and process boundary into a memory-unsafe C parser. Controls: `simple_strtoul` (`json_parser.c:29-37`, positive-decimal only, no overflow path into a pointer); the D-07 power-of-two + range check in the handler; the reset at `json_parse:82-89` so a stale value cannot leak across commands; the `token_idx += 2` unknown-key skip (`:133`) that D-11 pins |
| V6 Cryptography | **no** | No crypto. CRC8-CCITT (`eprom_operations.py:847`) is integrity, not authenticity, and is unchanged |
| V7 Error Handling / Logging | partial | D-07 chooses a **silent** fallback deliberately (a new message ID costs PROGMEM against a 0-byte budget to report a condition only our own host could cause). The compensating control is the exhaustive host-side proof. Recorded as a deliberate trade, not an omission |
| V12 Files / Resources | partial | `build_db.py` fetches over the network (`requests.get`, `:438`) and writes the generated DB. Pre-existing; unchanged by this phase |
| V13 API / Web Service | **no** | No API surface |
| V14 Configuration | partial | `~/.firestarter/database.json` overrides can supply a `page_size`. **See the finding below.** |

### Known threat patterns for this stack

| Pattern | STRIDE | Standard mitigation | Status in this phase |
|---|---|---|---|
| Out-of-bounds page write / page overrun on the die | **Tampering** | Flush granularity ≤ the physical page | The whole point of PGSZ-02. A too-**large** delivered value is the dangerous direction; D-07's fallback + D-01's provenance rule are the two controls, and D-04 correctly downgrades the floor's safety claim to *unproven* for the 11 promoted 16/32 rows |
| Unbounded value from the wire reaching a loop bound | **DoS** | Range clamp at the trust boundary | D-07's `[1, DATA_BUFFER_SIZE]` check. Note the mask is only ever ANDed with an address — it cannot index memory — so the failure mode is wrong granularity, never a buffer overrun. Worth stating explicitly in `149-PAGE-SIZE.md` |
| Integer overflow in `page_size - 1` | Tampering | Reject 0 before subtracting | `page_size == 0` → mask `0xFFFF…` if computed on an unsigned type, which would flush **almost never** — the dangerous direction. D-07's `>= 1` lower bound must be enforced **before** the subtraction. Measured mitigating factor: the host cannot send 0 because both emit guards are truthiness tests (§R5e), so 0 is unreachable from our own host — but the firmware must not rely on that |
| Token-walk desynchronisation on an unknown key | Tampering | Fixed `key + value` advance | `json_parser.c:320-321`; D-11 pins it |
| Stale global state across commands | Tampering | Explicit per-command reset | D-05. `firestarter.cpp:33` has no `memset`; the reset block is the only defence |
| Cross-algorithm value reinterpretation | Tampering (data-integrity) | Provenance-keyed selection | D-01. This is the phase's central security-flavoured control: a `page_size` read out of an `0x07`/`0x0B` record is not evidence about a 28C page buffer, and delivering one to a FRAM part is the concrete harm the rule prevents |
| A local override supplying an unvalidated `page_size` | Tampering | Firmware-side validation | **Finding:** the D-07 host test iterates the *generated* DB, so a `~/.firestarter/database.json` override could supply a non-power-of-two or out-of-range `page_size` that the host emits (it is truthy) and the host test never sees. The **firmware** check is therefore load-bearing, not belt-and-braces. `[VERIFIED: database.py:417-419 is override-agnostic; test_wire_dict_equivalence.py:79 uses skip_local_override=True]` The plan should state this as the reason D-07's firmware half exists at all |
| A slopsquatted or malicious dependency | Tampering | Package audit | **N/A — this phase installs no packages.** See §Package Legitimacy Audit |

### Package Legitimacy Audit

**Not applicable — this phase installs no external packages in either repo.**

Every mechanism this phase needs already exists in-tree: Unity + PlatformIO + ArduinoFake (firmware, already installed, §R8c), pytest + syrupy + ruff + mypy (host, already installed and green, §R6e / §R10d). `jsmn` is a vendored in-repo library (`firestarter/.pio/build/uno/lib5fe/libjsmn.a`, built from the repo's own `lib/`). No `pip install`, no `npm install`, no new `platformio.ini` `lib_deps` entry.

| Package | Registry | Verdict | Disposition |
|---|---|---|---|
| *(none)* | — | — | — |

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none.
**Planner action:** if any plan adds a dependency, the Package Legitimacy Gate must be run at that point — but nothing in the researched design requires one, and adding one would need its own justification against a phase whose budget is 0 bytes of AVR flash.

---

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|---|---|---|---|
| `mem_type` / `type` wire field as a second dispatch axis | `algorithm` is the sole dispatch key | v1.20, phases 105-107 | The wire dict has one dispatch axis; the new key is a parameter, not a selector |
| `flash_type_3` / `flash_type_4` | `flash_nor_unlock` / `flash_5v_page` | v1.19 Phase 104 | Makes `flash4_page_size` a dead name in three host comments (§X-5) |
| Buffer size parsed out of the FW identity **string** | `MSG_OK_READY` ack carries `DATA_BUFFER_SIZE` as a length-discriminated blob (CAP-01/CAP-02/CAP-03) | v1.16 Phase 55 → v1.31 | Makes `platformio.ini:65-66`'s "1022" comment stale; the chunk is 512/1024 (§R10c) |
| Voltage/timing as unit-suffixed strings (`"5V"`, `"100 us"`) | `vcc_mv` / `vdd_mv` / `vpp_mv` / `pulse_duration_us` integers | v1.32 Phase 148 | The DB schema this phase's emitter writes into. `page_size` was **already** an integer, so no schema question arises |
| Seven independent "firmware absent" proxies | `tests/fw_presence.py` + `tests/scan_paths.py` | v1.22 Phase 123 | D-18 adds one inventory entry, not a mechanism |
| A whole-byte equality poll conflating completion and data-landed | `eeprom28c_wait_for_page_write` (DQ7-complement) + `eeprom28c_verify_page_readback` | v1.22 Phase 117, FIX-06 | The two functions called once per flush — the flush count D-09 observes |
| BASE-01 as an immutable v1.24 reference | BASE-01 re-anchored **once** to the v1.31 tip, with the mechanism unchanged | v1.31 Phase 144 | D-12 forbids a second move; the exemption mechanism is the sanctioned route |
| Un-adjudicated MERGE-05 band breach | `MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96`, named and SHA-attributed | v1.31 Phase 145 | Fully consumed; leonardo headroom **0 B** |

**Deprecated / outdated — do not reintroduce:**
- Per-chip lookup tables keyed on part number (three deleted in Phase 70; `_PAGE_SIZE_BY_PART` is the surviving datasheet-cited exception and is frozen at 2 entries).
- `json_init()` — dead by inspection, deleted by this phase's folded todo.
- Editing `include/messages.h` directly — codegen-generated, CI-drift-gated.
- `check_uno_ram.sh` — superseded by `size_baseline.json` (`size_baseline_base01.json:meta.supersedes`).

---

## Assumptions Log

Claims tagged `[ASSUMED]` above. Each needs planner confirmation (or explicit acceptance as non-load-bearing) before it becomes a locked plan criterion.

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| **A1** | Adding one PROGMEM key + one table row + one getter + one `uint16_t` handle field + the mask logic costs a **small, single-digit-to-low-double-digit** number of AVR flash bytes | §R2 (byte cost) | **HIGH.** `N` drives D-12's exemption size, the four broken test legs and both re-planted fixtures. If the real cost is large (e.g. >200 B on leonardo), the phase may need to fund it differently — and D-12 explicitly rejected in-phase savings as a funding source. **Mitigation: D-13's cold before/after measurement resolves this before the size-gate plan is authored. Do not author the exemption before that number exists.** |
| **A2** | A cold AVR build takes single-digit minutes per env; three envs sequentially is a tractable single task | §R8c | LOW-MEDIUM. A wrong estimate produces a task timeout that reads like a build failure. **Mitigation: no timeout, or a generous one; the transcript is the deliverable.** |
| **A3** | `%` by a **runtime** `uint32_t` divisor pulls `__udivmodsi4` into the AVR build, whereas `%` by the compile-time constant 64 does not — so the mask form is what *keeps* the cost flat | §R3d | LOW. D-06 mandates the mask regardless, on the independent ground that it preserves absolute-address semantics (§R3d, measured). The `__udivmodsi4` argument is a *reason*, not a *requirement*, and A1's measurement settles it either way |
| **A4** | `firestarter/tests/test_flash_path_record_sync.py` goes RED on a dirty **real** firmware tree | §R8f | LOW. Its own docstring (`:841`) suggests it tolerates one, and it passed here with a clean tree. Not probed (dirtying the firmware tree is forbidden by this research's safety rules). **Mitigation: commit before running the firmware suite anyway — cost is one commit.** |
| **A5** | `origin/beta` is still at `7f6afc6` at fork time | §R10a | MEDIUM. `beta` has moved from spurious CI-fired bumps before. **Mitigation: `git fetch` immediately before the fork, verify by content with §R10a's four checks, and record the actual forked SHA in `149-PAGE-SIZE.md`.** |
| **A6** | The suggested forbidden-pattern regexes (`page-size-proven`, `graduation`, `support-status-change`, `issue-closed`, `at28c256-fixed`) are the right vocabulary for this phase's artifacts | §R9d | MEDIUM. Windowed patterns (`{0,3}` / `{0,4}`) are measurably weaker than unwindowed ones (`146-check-claims.py:59-62`). **Mitigation: each pattern needs its own planted-fixture leg; prefer unwindowed forms.** |
| **A7** | No plan in this phase needs a new dependency | §Package Legitimacy Audit | LOW. Every needed framework is present and green. If one is added, run the gate then |

**Not assumed — measured this session:** D-01's full arithmetic and both part lists; the `diff_db` bucket behaviour before and after; the `\bproven\b` collision; all size and RAM figures; the mask ≡ mod equivalence; the toolchain's presence; both test-suite counts; the golden's 2 current carriers and all 18 delta keys; `json_init`'s zero call sites; `--gc-sections`; `DATA_BUFFER_SIZE` per env; every CI gate's path set; and `origin/beta`'s content parity with the v1.31 tip.

---

## Open Questions

1. **What is the actual flash cost, and can leonardo afford it at all?**
   - *What we know:* leonardo's MERGE-05 headroom is exactly **0 B** and its physical free flash is 1670 B (5.8%). The edit is small. `--gc-sections` is on.
   - *What's unclear:* the number. A1.
   - *Recommendation:* make D-13's cold before/after a **gate**, not a report. If the leonardo delta is larger than the phase can justify as a named exemption, the honest options are (a) a smaller field width, (b) `uint8_t` storing `log2(page_size)` — 2 B → 1 B RAM and a shift instead of a subtract, (c) escalate. Do **not** silently absorb it, and do **not** re-anchor BASE-01 (D-12).

2. **Where should the mask be resolved — `configure_eeprom28c` or `write_init`?**
   - *What we know:* `write_init` has an early return at `:454`, and the existing native suite never calls `firestarter_operation_init` (§R4c). `configure_eeprom28c` runs once per command for every `0x0D` command, including three that never use the mask.
   - *What's unclear:* nothing factual — this is a design choice with a measured hazard on one side.
   - *Recommendation:* `configure_eeprom28c`, recorded in `149-PAGE-SIZE.md` as mechanism-corrected / intent-satisfied against D-06's literal "at write-INIT". It touches no existing test and is unconditional by construction.

3. **Should the validation upper bound be `DATA_BUFFER_SIZE` (board-dependent) or a literal?**
   - *What we know:* `[1, 512]` on uno/uno328pb/native, `[1, 1024]` on leonardo (§R10c). Both delivered values are inside both.
   - *What's unclear:* whether anyone will ever care about a value in `(512, 1024]`.
   - *Recommendation:* a board-invariant literal (512, or 256 = the largest page any of the 746 rows carries) makes the contract identical on all four envs and makes the native test's coverage total. State the choice and the reason.

4. **How is the `\bproven\b` collision resolved?**
   - *Recommendation:* negative lookbehind `(?<!software-)\bproven\b`, with a planted-fixture pair proving both directions. Blocking for plan B.

5. **Do the Phase 44 knobs' missing resets get fixed here?**
   - *What we know:* `read_settling_us` / `read_strobe_us` are **not** in `json_parse`'s reset block (§R2d), so they carry the same stale-value defect one field over. Both treat 0 as "use the default", so the symptom is a stale non-zero knob.
   - *Recommendation:* **no** — out of scope, and it would perturb `test_read_timing`'s existing `test_read_timing_fields_default_zero_when_absent`. File as a pending todo (a 4th one) and note it in `149-PAGE-SIZE.md`, since the phase edits exactly that block and a reader will ask.

6. **Should `infoic_page_size_raw` stay, now that `page_size` carries it for 18 rows?**
   - *What we know:* D-02 says `infoic_page_size_raw` is untouched and stays the raw provenance axis. For the 18 rows the two fields will hold identical values; for the other 728 they diverge or only one exists.
   - *Recommendation:* keep both, exactly as D-02 says — the raw field is what makes the provenance rule auditable after the fact, and `diff_db`'s `PROV01_PROTECT_METADATA` rule keys on it. Worth one sentence in `149-PAGE-SIZE.md` explaining why an apparent duplicate is not one.

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| PlatformIO Core | firmware build + native tests | ✓ | 6.1.19 (matches baseline meta) | — |
| `toolchain-atmelavr` | `pio run -e uno\|uno328pb\|leonardo` | ✓ | installed (`avr-size` verified working) | — |
| `framework-arduino-avr` | uno / leonardo | ✓ | installed | — |
| `framework-arduino-avr-minicore` | **uno328pb** (`board = ATmega328PB`, `build.core = MiniCore`) | ✓ | installed | — |
| ArduinoFake (native mocks) | `[env:native]` | ✓ | `.pio/libdeps/native/ArduinoFake` present | — |
| Unity | native test framework | ✓ | via `test_framework = unity` | — |
| Python (devcontainer) | host tests, tools, gates | ✓ | 3.12 | **⚠ app CI runs 3.11; mypy config says 3.10.** A local pass is not a CI pass |
| pytest | both repos | ✓ | 9.1.1 | — |
| syrupy (snapshots) | host suite | ✓ | 32 snapshots pass | — |
| ruff | app CI gate legs 3 | ✓ | present (`.ruff_cache/`) | — |
| mypy | app CI gate leg 4 | ✓ | present (`.mypy_cache/`); watermark 35 | — |
| `git` | all | ✓ | submodule checkouts intact, `origin` fetched today | — |
| Network access | **plan C only** — `build_db.py` fetches `infoic.xml` (`build_db.py:438`) | ✓ (assumed; the pinned local copy exists but `build_db.py` has no flag to use it) | — | **None.** `build_db.py` has no CLI flags and no offline path. If the fetch fails it `sys.exit(1)` (`:441-443`) |
| Pinned `infoic.xml` copy | research verification only | ✓ | 17,861,009 B, md5 `b4548e57c4f6c6c8c4f7387add03fa77` | — |
| `node` | `gsd-tools` | ✓ | not on `PATH`; use `.claude/gsd-core/bin/gsd-tools.cjs` | — |
| AT28C silicon | **nothing** — by design | ✗ | — | **N/A.** REQUIREMENTS.md §Out of Scope excludes bench validation; PGSZ-05 ships software-proven |

**Missing dependencies with no fallback:** none that block execution.
**Missing dependencies with fallback:** none.
**Notable:** the knowledge graph at `.planning/graphs/graph.json` is **stale** — `age_hours: 1176`, `commits_behind: 1418`, `stale: true`, `commit_stale: true`. It was not queried for this research; treat any semantic relationship it reports as unreliable for v1.32 work.

---

## Sources

### Primary (HIGH confidence) — read directly this session

**Firmware (`firestarter/` @ `6992271`, content-identical to `origin/beta` @ `7f6afc6`):**
- `src/json_parser.c` — full read; `:25-26`, `:37-45`, `:47-48`, `:50-54`, `:56-79`, `:81-141`, `:272-366`
- `src/firestarter.cpp:28-116`, `:131`, `:214-215`, `:262-270`, `:332`
- `src/proms/eeprom_28c.cpp:1-56`, `:189-228`, `:448-545`, `:575-681`, function inventory
- `src/proms/flash_5v_page.cpp:19-31`
- `include/firestarter.h:1-40`, `:180-221`; `include/json_parser.h` (full)
- `platformio.ini:1-130`
- `scripts/check_size_baseline.py:118-175`, `:270-341`, `:536`
- `scripts/check_build_warnings.py:10-15`, `:115-178`
- `scripts/baseline/size_baseline.json` (full), `scripts/baseline/size_baseline_base01.json` (full)
- `tests/test_check_size_baseline.py` (grep survey), `tests/test_flash_path_record_sync.py` (grep survey)
- `tests/fixtures/planted_size_baseline_policy_leonardo_growth.log:78-79`
- `test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` (full, 319 lines) + its `host_stubs.cpp` (full)
- `test/native/avr/test_read_timing/test_read_timing_params.cpp` (full, 125 lines) + its `host_stubs.cpp` (full)
- `test/native/avr/_shared/host_stubs_common.inc:51-153`
- `.github/workflows/build.yml`, `beta-build.yml` (grep survey)
- `~/.platformio/platforms/atmelavr/builder/frameworks/arduino.py:98,111`

**Host (`firestarter_app/` @ `b142c0e`):**
- `tools/build_db.py:112-145`, `:317-402`, `:435-500`, `:705-796`, `:860`
- `tools/diff_db.py:1-30`, `:300-320`, `:370-400`, `:420-470`, `:595-660`, `:660-730`, `:733-810`, `:908-931`
- `tools/extra_chips.json` (full), `tools/baseline/chip_database.baseline.json` (programmatic)
- `tools/check_mypy_watermark.py:1-125`; `tools/ci_parity.sh:60-160`
- `firestarter/database.py:405-425`, `:530-562`; `firestarter/constants.py:137-154`
- `firestarter/eprom_operations.py:425-450`, `:840-870`; `firestarter/serial_comm.py:147-200`, `:349-411`
- `firestarter/data/chip_database.json` (programmatic; 746 rows / 59 vendors)
- `tests/fw_presence.py` (full, 140 lines); `tests/scan_paths.py` (full, 355 lines)
- `tests/test_wire_dict_equivalence.py` (full, 231 lines); `tests/golden/wire_dict_baseline.json` (programmatic)
- `tests/test_scan_paths_resolve.py` (grep survey); `tests/test_revision_constants_parity.py:1-130`, `:440-580`
- `tests/test_cap03_ack_layout_parity.py:30-90`, `:160-212`
- `pyproject.toml:128-175`; `.github/workflows/ci.yml`; `README.md:61-92`

**Meta (`/workspaces`):**
- `.planning/phases/149-*/149-CONTEXT.md` (full, 493 lines)
- `.planning/REQUIREMENTS.md` §PGSZ, §Out of Scope; `.planning/ROADMAP.md` §Phase 149; `.planning/PROJECT.md` §Current Milestone: v1.32
- `.planning/phases/146-*/146-check-claims.py:60-275`; `.planning/phases/148-*/148-08-SUMMARY.md`
- `CLAUDE.md`; `.devcontainer/gen-platformio-ini.py`; `.planning/config.json`

**Upstream data:** `infoic.xml` @ minipro `a8efaedc236c1d9718bd28299dfbb99536b010ff`, `<database type='INFOIC2PLUS'>` only — pinned local copy, byte- and md5-verified.

### Command transcripts executed this session (all read-only)
`git rev-parse` / `log` / `diff` / `show` / `cat-file` / `grep` / `ls-tree` (both submodules) · `md5sum` + `stat` on the pinned XML · `avr-size -C` on three pre-existing ELFs · `pio --version`, `pio test -e native -f …` (2 suites, 10 cases, PASSED) · `python3 -m pytest tests/ -q` in `firestarter` (314 passed) · `python3 -m pytest tests/ -o addopts="" -q` in `firestarter_app` (1641 passed) · `python3 tools/diff_db.py` (PASS, 744, exit 0) · `gcc` + run of a 40-line flush-predicate enumerator · three read-only Python harnesses over the pinned XML, the live DB, the pinned baseline and `diff_db._classify_diff` · `gsd-tools graphify status`

### Secondary (MEDIUM confidence)
- Project memory entries on branching, worktrees, `phase.complete`, the record-gate timeout, `pytest -q` doubling, `--auto` gate auto-approval, and `gsd-tools query commit` branch switching — used for process guidance, cross-checked against the repo where a file could confirm them.
- `146-check-claims.py`'s citations of `139-check-claims.py` line numbers — transitively trusted; `139-check-claims.py` was located but not read line by line.

### Tertiary (LOW confidence)
- The `__udivmodsi4` / strength-reduction reasoning (A3) — standard avr-gcc behaviour, not measured here.
- Cold-build duration (A2) — not measured; forbidden by this research's safety rules.
- Byte cost of a comparable optional key (A1) — not isolable from git history.

**No web search or external documentation lookup was performed or needed.** Every question in scope was answerable from the two sub-repos, the meta repo, the pinned upstream XML, and the installed toolchain. No package was recommended, so no registry or Context7 lookup applies.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| D-01 arithmetic and both part lists | **HIGH** | Independently re-joined against the byte-verified pinned XML; 84/84 matched, 0 unmatched, 0 fidelity mismatches; every count and both lists reproduce CONTEXT.md exactly |
| Firmware seam mechanics (R2, R3) | **HIGH** | Full reads of all four files with exact line numbers; the flush-predicate equivalence was executed, not reasoned |
| `diff_db` behaviour (R1) | **HIGH** | Demonstrated on the real baseline and the real DB, plus four synthetic controls, plus a whole-DB after-149 census; exit code predicted and mechanism cited |
| Native test surface (R4) | **HIGH** | Both suites read in full and **run** green here; the flush-count observability question traced through the actual read seam and both stub layers |
| Host emit path (R5) | **HIGH** | Every line read; the two guard-shape corrections and the two-spelling gotcha are measured |
| Wire golden (R6) | **HIGH** | Shape, comparison, current carriers and all 18 delta keys extracted programmatically |
| Parity infrastructure (R7) | **HIGH** | Both modules read in full; `_FLOOR`, the exact-count assertion's scope, and the pre-existing skip-leg script all located |
| Size / warning gates (R8) | **HIGH** for mechanism and current figures; **MEDIUM** for the new exemption's blast radius | Constants, allowance function, both call sites, four test legs and both fixtures located and read. The blast radius is enumerated from those reads but the actual edit was not attempted; `N` is unknown by construction (A1) |
| Claim gate (R9) | **HIGH** | Donor read; the `\bproven\b` collision executed against the real regex; the changelog surface located and its precedent quoted |
| Preconditions (R10) | **HIGH** | Content-verified fork target; `json_init` and `--gc-sections` both measured; `DATA_BUFFER_SIZE` per env enumerated from source |
| Flash cost of the change | **LOW** | Not measurable without building. This is A1, the phase's single biggest open number, and D-13 is designed to resolve it |
| Cold build duration | **LOW** | Not measured (forbidden). A2 |

**Files written by this research:** exactly one — this document. No source, test, database, or other planning file was modified. Throwaway harnesses live in `/tmp/claude-1000/-workspaces/a207c722-3cd9-4367-b626-a4a5c12beed6/scratchpad/` (`d01.py`, `d01b.py`, `r1.py`, `r1b.py`, `flush.c`). No git branch was created, renamed, switched or checked out in any repo. `build_db.py` was never invoked.

**Research date:** 2026-08-19
**Valid until:** 2026-09-02 (14 days) for the in-repo mechanism claims — this is a fast-moving milestone with three repos in flight, and `origin/beta` in particular can move under the phase (A5). The D-01 provenance measurement is valid as long as the pinned `infoic.xml` commit (`a8efaedc`) remains the source; a `build_db.py` run against a moved upstream invalidates the 15/3 lists, which is exactly why `diff_db.py`'s 744/0/0/0 is a gate rather than a report.








