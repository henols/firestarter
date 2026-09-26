# Phase 154: Provenance Comment Sweep + Remap Tool (dual-repo lockstep) — Research

**Researched:** 2026-08-23
**Domain:** Source-comment refactoring under content-pinned gates; line-number citation remapping; build-artifact byte-identity oracles
**Confidence:** HIGH (every load-bearing claim in this document was measured in this session against the clean `beta` trees; the commands are inline)

> **How to read this.** CONTEXT.md already settled D-01…D-12 against session
> measurements. This document does **not** re-derive them. It confirms the ones
> that were checkable, and it reports **five findings CONTEXT.md does not
> contain, three of which change the phase's shape**. Those are collected in
> §`Findings That Change The Phase's Shape` up front. Everything else is the
> mechanical detail the planner needs.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

*Copied verbatim from `154-CONTEXT.md` §`<decisions>`. Condensed to the decision
statements; each one's inline evidence remains in CONTEXT.md and is not restated
here.*

- **D-01: The triage is ONE mechanical decision procedure, not a three-way judgment call.** Per hit: (1) delete the provenance token(s) and their enclosing punctuation — `Phase N`, `Plan N`, `Plan N-NN`, `Task N`, `PNNN`, `<NNN>-CONTEXT.md`, and the requirement/decision IDs (`D-NN`, `LOCK-02`, `PGSZ-01`, `ERASE-04`, `LOOP-03`, `MERGE-04`, `TABLE-01`, `W-04`, `OD-3`, `BF-3`, `Q4`, `T-44-01`, `FIX-05`, `A-7`, `C-8`, `BASE-02`, `HOST-01`, `VPP-01`, `CFG-03`, `RCA-01`); (2) judge what remains — a sentence describing code that exists → **keep it, reflowed** (the majority case); nothing but connective punctuation → delete the whole comment; a sentence describing code that is NOT there (tombstone) → delete the whole comment; (3) **Guard:** step 2 may never delete the only statement of a non-obvious invariant, trap, or fail-closed rationale — if stripping leaves it too terse to stand alone, reword it to stand alone, do not delete it.
- **D-02: `CAP-0N` is EXEMPT** — it is live cross-repo wire-protocol vocabulary, not planning provenance. Generalised exemption test: a token that appears in **both** repos' shipped source is vocabulary, not provenance, and is exempt. **Consequence — `firestarter/src/firestarter.cpp:177-195` is a no-touch region**, pinned verbatim in raw un-stripped text by `test_cap03_ack_layout_parity.py`.
- **D-03: Requirement/decision IDs ARE provenance in shipped source and are stripped there — but are RETAINED in test files** where the ID is the test case's traceability key.
- **D-04: Test-file scope is NARROWED.** 331 of 636 hits (52%) are in test files. Test files get the **narrow** treatment: tombstone deletion and label-only-comment deletion only. No reflowing of substantive test commentary. Named keep-in-full case: `firestarter_app/tests/scan_paths.py`'s module docstring.
- **D-05: `firestarter_app/tests/scan_paths.py::ALL_CROSS_REPO_PATHS` is the authoritative inventory, and it is exactly 8 paths.** Use it; do not re-derive it by grep.
- **D-06: `test_sdp_table_parity.py` is the one genuinely dangerous gate, and a LIVE collision already exists** at `firestarter/src/proms/eeprom_28c.cpp:199-201`. Two comment-blind mechanisms: `_PAIR_RE` (:120) and the brace-depth slice (:141-158). **Requirement:** plant a violation and prove RED before and after. Same for `test_dispatch_mirror.py`'s C++ leg.
- **D-07: The manifest records all 10,054 citations that target a swept file**, not only the 6,939 predicted to shift. JSONL at `.planning/v1.33/sweep-citation-manifest.jsonl`, one record per citation: `{planning_file, planning_line, target_file, target_line, target_line_end, source_text, source_text_end, retarget}`. Range citations record **both** endpoints and both texts.
- **D-08: A citation pointing AT a comment line the sweep deletes is retargeted in the manifest, never silently dropped** — `retarget: true`, original cited text preserved, new target = the first surviving code line the comment described. **Its count is a deliverable of this phase.**
- **D-09: The remap tool lives at `.planning/v1.33/tools/remap_citations.py`** with a sibling `.planning/v1.33/tools/test_remap_citations.py`. **The tool takes the repo root as an explicit argument and never derives it from `_HERE`.** It must exit non-zero on an empty input set.
- **D-10: Keep the D-01 split; the roadmap's sweep-last fallback is DECLINED.**
- **D-11: Commit granularity — one commit per sub-repo plus one meta commit.** Both sub-repo commits must land **before** the host suite runs.
- **D-12: Two preconditions must be discharged before the sweep's first edit.** (1) The `firestarter` working tree is dirty — 11 modified files on branch `size-reduction-survey`, byte-for-byte equal to `.planning/notes/firmware-size-reduction-measured.patch`. **That reset is the operator's call at execution time, not the planner's to assume.** (2) No `gsd/v1.33-*` branch exists in either sub-repo; fork off `beta` in all three repos before any edit.

### Claude's Discretion

> "The operator delegated the whole gray-area set. Everything above was decided
> against a measurement or a precedent rather than a preference, so nothing here
> is open. The two items that remain genuinely unknown until the diff exists —
> and are therefore *deliverables*, not decisions — are D-08's retarget count and
> the per-file keep/delete ratio."

### Deferred Ideas (OUT OF SCOPE)

- **⚠ Cross-phase flag for Phase 157.** `test_json_key_parity.py:113`'s `_KEY_PARSERS_TABLE_RE` matches `key_parsers[]`, which **DECODE-01 deletes**. Phase 157 has no success criterion covering this gate. Worth adding as a DECODE-08 at `/gsd-discuss-phase 157`. Out of Phase 154's scope — it is a code change.
- **A global citation gate.** SWEEP-11's tool is close to one but is deliberately a *remapper*, not a *checker*. Promoting it is a real idea and its own phase; note it, do not build it here.
- **`reference_gsd_provenance_comments` as a lint.** A hook or gate rejecting new `Phase N`-stamped comments in shipped source. Out of scope: this phase removes the debt, it does not install the brake.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description (abbreviated) | Research Support |
|----|---------------------------|------------------|
| SWEEP-01 | D-01's single mechanical procedure applied per hit; five keep-examples land on "keep, reflowed" | §`Corpus Measurements` gives the per-group hit split the procedure runs over and the token frequency. **§F3 is a blocker on `eprom_params.cpp`, one of the five named keep-examples** — it is blob-sha-pinned |
| SWEEP-02 | `CAP-0N` exempt; both-repos exemption test; `firestarter.cpp:177-195` untouched | §`Corpus Measurements` measures the exemption at **exactly 20 hit-lines**; §`No-Touch Region` verifies the region is intact and locates the pinned string at `:192` |
| SWEEP-03 | IDs stripped in shipped source, retained in test files | §`Corpus Measurements` token frequency: `D-#` = 185 hit-lines, the second-largest class after `Phase` |
| SWEEP-04 | Test files get narrow treatment; 331-of-636 and "no oracle covers any of them" recorded | §`Corpus Measurements` reproduces 216 + 115 = **331 exactly**; §`Validation Architecture` states the coverage ceiling explicitly |
| SWEEP-05 | `uno` build byte-identical, stated as a measured pair of numbers | §`R5 — The Byte-Identity Oracle` — **fully solved and upgraded to a sha256 pair**, proven immune against a 1827-line comment strip |
| SWEEP-06 | All 8 `ALL_CROSS_REPO_PATHS` classified and disposed; the two generated headers fixed at their generators or shown to need no fix | §`The 8-Path Inventory` fills every hit count in D-05's table; **both generated headers measure 0 hits → provably need no fix**. **§F4: the inventory is incomplete — 22 further source-scanning firmware-repo gates have no comment stripping** |
| SWEEP-07 | Planted-violation controls for `test_sdp_table_parity.py` and `test_dispatch_mirror.py`'s C++ leg, RED before and after | §`R3 — Planted-Violation Controls` — **both controls built and run this session**; fixtures, exact wiring, and the silent-green proof are all specified. **§F10: this requires new test code, which the phase's "comment text only" framing does not cover** |
| SWEEP-08 | `eeprom_28c.cpp` swept as its own plan | §`R3` confirms 33 hits, the live `_PAIR_RE` collision at `:199-201`, and that the datasheet citation of record sits at `:176-202` inside the highest-risk block |
| SWEEP-09 | Pre-sweep manifest covering all 10,054 citations, both endpoints and both texts for ranges | §`R2 — Citation Extraction` — figures independently reproduced within 0.6%; four syntax variants enumerated with counts; **the sequencing problem is resolved** |
| SWEEP-10 | Retarget subset recorded with `retarget: true`, count reported | §`R2` and §`R1` — the `retarget` flag is produced by the same `map_point` clamp that handles a deleted line; the count is derivable only post-diff, as CONTEXT.md says |
| SWEEP-11 | `remap_citations.py` + test, idempotent, range-shrinking, explicit repo root, non-zero on empty input, not applied | §`R1 — The Remap Tool` — algorithm chosen and prototyped; shrink property demonstrated; **the idempotency failure mode and its fix both demonstrated concretely** |
| SWEEP-12 | Staleness marker planted, naming swept files, pointing at Phase 159 / REMAP-04 | §`R6` — `.planning/v1.33/` does not exist yet; this phase creates it |
| SWEEP-13 | One commit per sub-repo + one meta commit, sub-repo commits before the host suite; archived-`milestones/` gate collision recorded either way | §`R6` — **this phase edits nothing under `.planning/milestones/`**, so the hazard is Phase 159's. §F7 broadens D-11: **9 modules assert git porcelain, not 1** |
</phase_requirements>

---

## Summary

The phase's mechanically hardest problem — the remap tool — turns out to be
tractable with the Python standard library alone, and its two named hazards
(range shrinking, idempotency) both reduce to a single design decision: **map
each range endpoint independently against a `difflib` opcode map, and gate every
rewrite on the manifest's recorded `source_text` matching at the destination.**
The shrink property then falls out for free, and idempotency becomes a property
of the same code path that implements REMAP-02's oracle. Both were prototyped and
demonstrated in this session, including the exact non-idempotent drift
(`:15 → :10 → :8 → :6`) that a naive implementation produces.

The phase's strongest oracle is also better than the requirement asks for.
SWEEP-05 wants "a measured pair of numbers"; the correct artifact is
`.pio/build/uno/firestarter_uno.elf` (**not** `firmware.elf` — the `PROGNAME` is
rewritten by a pre-build hook), and it is bit-for-bit reproducible across cold
builds *and* provably immune to comment-only line shifts, because project sources
are compiled without `-g` and the ELF's `.debug_*` sections come entirely from the
prebuilt framework archive. Deleting 1827 whole-line comments across 31 firmware
files left both the `.elf` and the `.hex` sha256 unchanged. So the criterion should
be a **sha256 pair**, which is strictly stronger and equally free. A cold `uno`
build takes 1.5 s.

Against that, three findings make the phase larger than CONTEXT.md scopes it.
**Four committed golden sidecars pin the git blob SHAs of five in-scope source
files carrying 30 provenance hits** — including `eprom_params.cpp`, which is one of
SWEEP-01's five named keep-and-reflow examples, and `eprom.cpp`, the most-cited
file in `.planning/` at 627 citations. The sweep commit invalidates all four, and
no regeneration tool exists. **The firmware repo has 32 Python gates of its own,
30 of which scan `src/`/`include/` source text and 22 of which do no comment
stripping**; D-05's 8-path inventory covers only the *app* repo's cross-repo gates
and is silent on these. And **`test_sdp_table_parity.py` can be driven silently
green** — proven, with the real `EEPROM_SDP_ENABLE` terminal byte corrupted from
`0xA0` (lock) to `0x10` (chip erase) and the gate still reporting 5 passed — by a
single reflowed comment above the declaration.

**Primary recommendation:** plan the sweep as three sequenced groups gated on
D-12's tree reset — (1) harden and control the comment-blind gates *and*
regenerate the four blob-sha sidecars, (2) sweep, with `eeprom_28c.cpp` and the
five blob-sha-pinned files each as their own unit, (3) build the manifest and tool
— and adopt `sha256(firestarter_uno.elf)` as SWEEP-05's oracle rather than the
size figures.

---

## Findings That Change The Phase's Shape

| # | Finding | Confidence | Effect |
|---|---------|-----------|--------|
| **F1** | The byte-identity oracle is `sha256(.pio/build/uno/firestarter_uno.elf)`, is reproducible across cold builds, and is **provably immune** to comment-only edits (no `-g` on project sources). Artifact name is `firestarter_uno.elf`, not `firmware.elf`. | `[VERIFIED: measured, 1827-line strip]` | Upgrades SWEEP-05 from a size-number pair to a hash pair. Removes the "is the artifact immune?" open question entirely. |
| **F2** | `test_sdp_table_parity.py` can be made **silently green** while the real table carries a `0xA0`→`0x10` (lock→chip-erase) corruption, via one reflowed comment. Also: CONTEXT.md D-06's "Negative control? **no**" is wrong — the module *has* a non-vacuity leg **and** a purpose-built `FIRESTARTER_SDP_SRC` env seam. | `[VERIFIED: gate run, 5 passed under corruption]` | Raises SWEEP-07's severity (fail-open, not RED-flip) but **lowers its cost** — the planting seam already exists. |
| **F3** | **NEW — not in CONTEXT.md.** Four committed golden sidecars blob-sha-pin **five in-scope source files carrying 30 provenance hits**, including `eprom_params.cpp` (a SWEEP-01 named keep-example) and `eprom.cpp` (627 citations). No regeneration tool exists. | `[VERIFIED: sidecar JSON + git rev-parse]` | **Blocking.** Adds a sixth disposition class to SWEEP-06 and a lockstep-regeneration task the plan does not currently have. |
| **F4** | **NEW — not in CONTEXT.md.** The **firmware** repo has 32 Python gates; **30 scan source text, 22 do no comment stripping**. D-05's inventory covers only the app repo. | `[VERIFIED: grep over firestarter/tests/]` | SWEEP-06's classification scope is incomplete. Needs a second inventory pass or an explicit out-of-scope ruling. |
| **F5** | **NEW.** 56% of `.planning/` citations are **bare basenames**, and **665 use an ambiguous basename** — `eeprom_28c.cpp` (286) and `firestarter.cpp` (204) collide with planted CMake fixtures; `firestarter.h` (99) collides with the app's own `tests/fixtures/fake_firestarter/include/firestarter.h`. | `[VERIFIED: extractor over .planning/]` | The manifest's `target_file` field needs a documented resolution rule, or 665 records resolve wrong. |
| **F6** | **NEW.** SWEEP-07's controls require writing **new test code and fixtures** into `firestarter_app/tests/`, which the phase's "comment text only, plus new files under `.planning/v1.33/`" framing does not cover. | `[VERIFIED: read requirement + gate source]` | Scope clarification the planner must make explicit, and a third sub-repo commit surface. |
| **F7** | D-11's commit-ordering rationale is broader than stated: **9 modules assert git porcelain**, not 1. Four are in the *app* repo asserting on the *firmware* repo's cleanliness. | `[VERIFIED: grep both repos]` | Strengthens D-11; the sweep's own uncommitted edits will redden 6 app-repo planted legs, not just `test_flash_path_record_sync`. |
| **F8** | D-12 precondition 1 (reset the firmware tree) is required for the **baseline**, not just the sweep. Measured against the dirty tree: host suite **1963 pass / 7 fail**; firmware gates **317 pass / 6 fail**. All failures attributable to the dirt. | `[VERIFIED: both suites run]` | No "before" measurement is meaningful until the reset lands. Makes the reset the plan's first gate, not a footnote. |

---

## Architectural Responsibility Map

This phase has no runtime tiers. The equivalent axis is **which repo owns which
artifact**, and it is the axis D-11's commit granularity runs on.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Firmware comment text (`src`, `include`, `test`) | `firestarter` sub-repo | — | D-11: one commit. Byte-identity oracle lives here. |
| Host comment text (`firestarter`, `tests`, `tools`) | `firestarter_app` sub-repo | — | D-11: one commit. **No size oracle exists on this side at all.** |
| Planted-violation controls + fixtures (SWEEP-07) | `firestarter_app` sub-repo | `firestarter` sub-repo (fixture *inputs* are firmware source copies) | F6: this is new **test code**, and it lands in the app repo where the gates live. |
| Blob-sha golden sidecars (F3) | `firestarter` sub-repo (`tests/golden/*.json`) | — | Must be regenerated in the **same commit** as the firmware sweep, or the gate is RED between commits. |
| Citation manifest, remap tool, staleness marker | meta repo (`.planning/v1.33/`) | — | D-09. Deliberately **not** `firestarter_app/tools/` — avoids coupling to the app's ruff/mypy watermark. |
| Applying the remap | **Phase 159** | — | D-01/D-10. Explicitly out of this phase. |

---

## R5 — The Byte-Identity Oracle (SWEEP-05)

### Which artifact

`pio` **is** available: PlatformIO Core 6.1.19 at `/usr/local/bin/pio`, with the
`toolchain-atmelavr` package installed under `~/.platformio/packages/`. (`avr-gcc`
is *not* on `PATH` — use `~/.platformio/packages/toolchain-atmelavr/bin/avr-size`
if you need the section table directly.) `[VERIFIED: pio --version, ls]`

The artifact is **`firestarter_uno.elf` / `firestarter_uno.hex`**, not
`firmware.elf`. `platformio.ini` wires `extra_scripts = pre:name_firmware.py` at
`[env]` scope, and that hook does `env.Replace(PROGNAME="firestarter_%s" %
board_name)`. Both pre-build hooks (`name_firmware.py`, `zero_bootloader_reserve.py`)
were read and are **fully deterministic** — no timestamps, no git SHA, no
environment reads. `[VERIFIED: read both scripts + build output]`

### The measurements

```bash
cd firestarter
rm -rf .pio/build/uno && pio run -e uno
sha256sum .pio/build/uno/firestarter_uno.elf .pio/build/uno/firestarter_uno.hex
```

| Run | `.elf` sha256 | `.hex` sha256 |
|-----|---------------|---------------|
| Cold build #1 | `64df1d2ff005077eb700479c09f60c7d4dc408ebc240075520b3b46d01456141` | `63fd625c78b69283f92e5860ec7db43883ce83dd1632985014208b8272f16e70` |
| Cold build #2 (after `rm -rf .pio/build/uno`) | **identical** | **identical** |
| Cold build in a **different absolute path** (`/tmp/.../fw`) | **identical** | **identical** |
| After deleting **1 comment line** in `eeprom_28c.cpp` + forced recompile | **identical** | **identical** |
| After deleting **1827 whole-line `//` comments across 31 files** + cold rebuild | **identical** | **identical** |

`RAM: 1562 / 2048` and `Flash: 23088 / 32768` in every case. Cold build: **1.5 s**.

### Why the `.elf` is immune (this was the open question)

The ELF *does* carry `.debug_info` (3747 B), `.debug_line` (2098 B),
`.debug_abbrev`, `.debug_str`, `.debug_aranges` — so the a-priori worry was
correct in principle. It does not bite here for two independently verified
reasons:

1. **Project sources are compiled without `-g`.** The verbatim compile line is
   `avr-g++ ... -Os -Wall -ffunction-sections -fdata-sections -flto ...` — no `-g`
   anywhere. The `.debug_*` sections come entirely from the prebuilt
   `libFrameworkArduino.a` and libgcc's `lib1funcs.S`, which the sweep never
   touches. Scanning the ELF for project source filenames returns **none** (only
   `lib1funcs.S` and LTO-mangled symbol names). `[VERIFIED: pio run -v, ELF string scan]`
2. **There is no `__LINE__` or `__FILE__` anywhere in `firestarter/src` or
   `firestarter/include`** — `grep -c` returns **0**. So no line number can reach
   `.text`/`.data` even indirectly. `[VERIFIED: grep]`

The ELF also embeds **no absolute paths** (`grep -c '/workspaces/firestarter'` on
the binary = 0), which is why the different-path cold build hashed identically.
That makes the oracle safe to run from a scratch copy.

### Recommendation

**Use `sha256sum` of the `.elf`.** It is a valid and strictly stronger form of
SWEEP-05's criterion, and it costs nothing. Report it as the required "measured
pair of numbers" — a pair of hashes plus the `RAM:`/`Flash:` figures, all four
recorded before and after.

- The `.hex` is *also* immune but is **weaker**: `avr-objcopy -O ihex` drops
  non-loadable sections, so a `.hex` match would mask a debug-section change. Since
  the `.elf` matches too, prefer the `.elf` and record the `.hex` as corroboration.
- The `pio run` size summary alone is the **weakest** form: `23088` is a
  4-significant-figure integer and would not detect a code change that happened to
  be size-neutral. Do not use it as the primary criterion.

**Cold-build convention** (this is what was run, and it worked):
`rm -rf .pio/build/uno && pio run -e uno`. Note that `touch`-ing a file does *not*
trigger a recompile (SCons uses a content decider), whereas a genuine content edit
does — verified both ways, so incremental builds are trustworthy, but use the cold
form for the recorded pair.

**Caveat the plan must honour:** every number above was measured against the
**dirty** `size-reduction-survey` working tree. They are the mechanics proof, not
the phase's baseline. The real "before" pair must be taken after D-12
precondition 1 lands (see F8).

---

## R1 — The Remap Tool: Line-Mapping Algorithm (SWEEP-11 → REMAP-01…03)

### Mechanism choice

| Candidate | Verdict |
|-----------|---------|
| **`difflib.SequenceMatcher.get_opcodes()`** | **CHOSEN.** Stdlib, no dependency, no subprocess, no git-revision plumbing. Yields exactly the `equal` / `delete` / `insert` / `replace` opcode stream the map needs, over line lists. Works on any two blobs regardless of git state, which matters because Phase 159 maps a **composite** pre-154 → post-158 diff that is not a single commit pair. |
| `git diff -U0` unified-hunk parsing | Rejected. Equivalent information but requires parsing `@@ -a,b +c,d @@` headers, a subprocess per file, and both endpoints resolvable as git revisions. Adds failure modes (submodule gitlinks, detached states) for no gain. Keep as a **cross-check** in the unit test: assert the difflib map agrees with `git diff -U0` on one real file. |
| `git blame --reverse` | Rejected. Designed for commit attribution, is per-line-expensive, and gives no clean "this line did not survive" signal. |
| `git diff --word-diff` | Rejected — wrong granularity entirely. Citations are line-keyed. |

**No third-party dependency.** `difflib` is stdlib and `.planning/v1.33/tools/`
has no package manifest — consistent with the `.planning/v1.16/ledger/tools/`
precedent (D-09), which is plain stdlib Python plus a sibling `pytest` file and a
`fixtures/` dir. `[VERIFIED: import difflib on py3.11; ls .planning/v1.16/ledger/tools/]`

### The map

```python
import difflib

def build_map(old_lines, new_lines):
    """old 1-based line -> new 1-based line, or None if the line did not survive."""
    sm = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    m = {}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                m[i1 + k + 1] = j1 + k + 1
        elif tag in ('delete', 'replace'):
            for k in range(i1, i2):
                m[k + 1] = None          # did not survive verbatim
    return m
```

Two deliberate choices:

- **`autojunk=False` is required.** `SequenceMatcher`'s default heuristic treats
  any element occurring in >1% of a sequence ≥200 items as junk. Over a
  900-line C++ file, ubiquitous lines like `` `}` `` or `` `` (blank) would be
  auto-junked and silently excluded from `equal` runs, corrupting the map. This is
  the single easiest way to get a subtly wrong map.
- **`replace` is treated as non-surviving, exactly like `delete`.** A reflowed
  comment is a `replace`: the text changed, so the manifest's `source_text` can no
  longer match at the destination. Such a citation **cannot round-trip** and must
  be flagged `retarget: true` (D-08) rather than assigned a number the oracle will
  then reject. Mapping `replace` positionally would manufacture false green.

### The three cases the requirement names

Demonstrated on a 20-line fixture with old lines 6–10 deleted:

```
map: {1:1, 2:2, 3:3, 4:4, 5:5, 6:None, 7:None, 8:None, 9:None, 10:None,
      11:6, 12:7, 13:8, 14:9, 15:10, ..., 20:15}
```

**(a) A single line that survives.** `map[15] = 10`. Direct lookup, `retarget=False`.

**(b) A range citation — both endpoints mapped independently.** Endpoint clamping
direction differs by role: a range **start** clamps *forward* to the next
surviving line, a range **end** clamps *backward* to the previous surviving line.

```python
def map_range(m, a, b, n_old):
    a2, ra = map_point(m, a, n_old, 'fwd')    # start: clamp forward
    b2, rb = map_point(m, b, n_old, 'back')   # end:   clamp backward
    return a2, b2, (ra or rb)
```

Measured: **old `3-18` (span 16) → new `3-13` (span 11), shrank by exactly the 5
deleted lines, `retarget=False`.** A constant-offset implementation would have
produced `-2-13`. The shrink property is **not** a special case that needs its own
code — it is the automatic consequence of mapping the two endpoints
independently, because the accumulated deletion offset at line 3 and at line 18
differ. This is precisely what REMAP-03 requires.

**(c) A citation targeting a deleted line.** `map_point(m, 8, 20, 'fwd')` →
`(6, True)`. The tool returns the next surviving line **and sets `retarget=True`**.
Note that it does *not* invent a mapping: the returned number is a documented
clamp, and `retarget=True` is the signal that Phase 159's oracle must **skip this
record by name** (D-08) rather than round-trip it. The plan must state that a
`retarget` record's new target is **hand-chosen** — the clamp is a starting
suggestion for the human, not the answer.

### Idempotency — the mechanism, and a test that catches its absence

The failure mode named in the phase scope is real and easy to hit. A map built
from two deletion blocks contains a **chain**: `map[15] = 10` *and* `map[10] = 8`.
Applying the map blind to whatever integer is found in the text drifts on every
run. Measured:

```
--- NAIVE: apply the offset map to whatever number is found ---
  run 1: see foo.c:10
  run 2: see foo.c:8
  run 3: see foo.c:6      <- drifts forever
```

**The mechanism that prevents it: make the REMAP-02 oracle the write predicate.**
Per record, in order:

1. **Fixed-point check first.** If the text at the citation's *current* line
   already equals the manifest's `source_text`, the record is already correct →
   **no-op**. This alone makes run 2 a no-op.
2. **Identity check.** Otherwise, only rewrite if the current line number equals
   the manifest's recorded **pre-sweep** `target_line`. Never key off "is this
   integer in the map's domain".
3. **Oracle assertion before writing.** Assert the text at the destination line
   equals `source_text`. If it does not, the map is wrong — fail loudly, do not
   write.

Measured with the same chained map:

```
--- FIXED-POINT (manifest-keyed, oracle-verified) ---
  run 1: see foo.c:10
  run 2: see foo.c:10
  run 3: see foo.c:10     <- runs 2 and 3 are exact no-ops
```

This single design gives three requirements at once: **SWEEP-11 idempotency**,
**REMAP-02's oracle**, and **REMAP-05's resumability** (a partially-applied remap
resumes correctly because already-correct records are recognised as fixed points,
not re-shifted).

**The unit test that catches a non-idempotent implementation** (this is the test
to write, and it is more specific than "run it twice"):

> Build a synthetic fixture whose map contains a **chain** — i.e. some line `a`
> with `map[a] = b` where `b` is itself a key with `map[b] = c`, `c ≠ b`. Requires
> at least **two** separated deletion blocks; a single deletion block cannot
> produce a chain, so a one-block fixture will pass even against a blind
> implementation. Assert: after run 1 the citation reads `b`; after run 2 it still
> reads `b`; and the run-2 diff is empty.

Add a second idempotency leg for the range case: a range whose *both* endpoints
chain, asserting the span is stable across runs (a blind implementation shrinks
the span again on every run).

### Round-trip oracle → manifest schema requirements

Phase 159's oracle is: *for every non-`retarget` record, the text at
`target_file:target_line` after the remap equals the manifest's `source_text`.*
For that to be executable, D-07's schema needs three things the field list already
implies but that the plan must state explicitly:

1. **`source_text` must be stored exactly as read, including trailing newline
   handling** — pick one convention (recommend: store the line *without* its line
   terminator, and compare against `splitlines()` output) and state it in the
   manifest header, because a mismatch here fails every record.
2. **`source_text_end` is what makes the range half of the oracle possible.**
   Without both texts, a range's end endpoint is unverifiable. D-07 already
   requires it — this confirms why.
3. **A `target_file` resolution field.** See F5 / §R2: `target_file` as *cited*
   is often a bare basename. The manifest must record the **resolved
   repo-relative path** (e.g. `firestarter/src/proms/eeprom_28c.cpp`) alongside
   the **as-cited string**, or Phase 159 cannot open the file. Recommend adding
   `target_file_cited` (verbatim, needed to find the text to rewrite) and
   `target_file_resolved` (needed to read the source). This is a **schema
   addition to D-07** and the planner should treat it as such.

**Anti-pattern to avoid:** a tool that derives the map from the *current* working
tree instead of from the recorded pre-sweep blob. The pre-sweep side must come
from git (`git show <pre-sweep-sha>:<path>`), because by the time the remap runs in
Phase 159 the "old" content exists nowhere on disk.

### Fail-closed requirements (D-09)

- Repo root is an **explicit argument**, never `_HERE`-derived — per
  `reference_check_permitted_claims_here_resolves_wrong_phase_dir`, a mis-sited
  `_HERE` checker scans nothing and exits 0.
- **Exit non-zero on an empty input set.** Also recommend: exit non-zero if the
  manifest parses to 0 records, if any record's `target_file_resolved` does not
  exist, and if any oracle assertion fails. Silence must never be success.
- The tool is **not applied** in this phase. Its unit test must therefore be the
  only thing that exercises it, which is why the synthetic fixtures carry the whole
  proof burden.

---

## R2 — Citation Extraction (SWEEP-09)

### Syntax variants actually present

Measured over `.planning/` (2,975 files scanned, including `.md`, `.py`, `.json`,
`.txt`, `.sh`, `.csv`), restricted to source extensions `cpp|c|h|ino|py`:

| Variant | Example | Count (all) | Count (targeting a swept file) |
|---------|---------|-------------|--------------------------------|
| `colon_single` — `path:N` | `eeprom_28c.cpp:199` | 6,253 | 4,949 |
| `colon_range` — `path:N-M` | `database.py:580-630` | 6,068 | 4,771 |
| `anchor_L` — markdown `path#LN` / `#LN-LM` | `[x](notes/f.py#L42-L51)` | 407 | 75 |
| `colon_list` — `path:N,M[,…]` | `hardware.py:39,153` | 274 | 194 |
| **TOTAL** | | **13,002** | **9,989** |

All four variants are live. Backticked forms (`` `path:42` ``) are a *wrapper*, not
a distinct variant — the inner text matches `colon_single`, so no separate
handling is needed.

**`colon_range` is 48% of the swept-targeting corpus (4,771 of 9,989).** Range
handling is not an edge case in this phase; it is roughly half the work, which is
why REMAP-03's both-endpoints requirement carries the weight it does.

`colon_list` (194) is a variant the requirements do not mention and the tool must
handle: `hardware.py:39,153` is **two independent point citations sharing one
path**, not a range. Each element maps independently with `direction='fwd'`.

### Verification of the recorded figures

Measured against the clean `beta` exports of both sub-repos
(`git archive beta | tar -x`; both repos verified at `HEAD == beta`, 0 ahead / 0
behind — `firestarter` at `8695ee5`, `firestarter_app` at `6bfa645`):

| Metric | Recorded | **Measured this session** | Δ |
|--------|----------|---------------------------|---|
| `file:LINE` citations anywhere in `.planning/` | 12,753 | **13,002** | +249 (+2.0%) |
| …targeting one of the touched source files | 10,054 | **9,989** | −65 (−0.6%) |
| …at or below that file's first GSD comment | 6,939 | **6,928** | −11 (−0.16%) |
| …above the first GSD comment | 3,115 | **3,061** | −54 |

Shifting citations by subtree:

| Subtree | Recorded | Measured |
|---------|----------|----------|
| `phases/` | 4,918 | 4,869 |
| `milestones/` | 1,309 | 1,302 |
| `research/` | 180 | **180 (exact)** |
| `graphs/` | 108 | 107 |
| `debug/` | 99 | 94 |
| `quick/` | 55 | **55 (exact)** |
| `notes/` | 54 | 72 |
| `PROJECT.md` | 42 | **42 (exact)** |

**Verdict: the recorded figures are sound.** Three subtree figures reproduce
exactly and the headline totals agree within 0.6%. The residual deltas are
explained by extractor-definition differences (my scan includes non-`.md` files;
`notes/` has grown since the survey). **Do not silently adopt either number** —
the plan should regenerate the manifest and report the count it actually produces,
citing 10,054 as the pre-registered expectation and explaining any delta.

Commands used are reproduced in §`Reproduction Commands`.

### The swept-file-set ordering problem — resolved

D-07 requires "all 10,054 citations that target a swept file" in a **pre-sweep**
deliverable, but the set of files the sweep actually edits is not known until the
sweep runs. Both are satisfiable because they are answered by two different sets:

- **Candidate set (knowable pre-sweep, and what the manifest must use):** every
  file under the sweep's globs carrying ≥1 provenance hit. **Measured: 160 files.**
  This is a strict superset of the files the sweep will edit, because D-02's
  `CAP-0N` exemption and D-01's "delete the whole comment" outcomes can leave a
  candidate file untouched.
- **Actual swept set (post-sweep):** the files with a non-empty diff.

**Concrete sequencing:**

1. Build the candidate set from the clean pre-sweep tree (160 files). This is a
   pure function of the tree and the survey regex — fully deterministic, and
   reproducible by Phase 159.
2. Generate the manifest over the **candidate** set. Recording a citation into a
   file that turns out untouched is harmless: at Phase 159 its `source_text` still
   matches at its recorded line, so the fixed-point check makes it a no-op. This is
   the same mechanism that gives idempotency, reused.
3. **Commit the manifest before the first sweep edit** — this is what makes it a
   pre-sweep deliverable, and D-07 is explicit that it cannot be reconstructed
   later.
4. Post-sweep, record the **actual** swept set in the staleness marker (SWEEP-12
   requires the marker to name the swept files). The difference between candidate
   and actual is itself a reportable number.

The manifest is therefore generated from the candidate set, and "targets a swept
file" is interpreted as "targets a **candidate** swept file" — a slight
over-approximation that is provably safe and strictly better for Phase 159's
oracle, exactly parallel to D-07's own reasoning for recording 10,054 rather
than 6,939.

### Path resolution — the trap, and the rule (F5)

**56% of citations are bare basenames.** Distribution of the 13,002 target
strings:

| Shape | Count |
|-------|-------|
| bare basename, resolves uniquely | 7,314 |
| exact repo-relative path | 2,429 |
| path suffix match (partial path) | 1,639 |
| **bare basename, AMBIGUOUS** | **665** |
| bare basename, unresolved | 553 |
| path, unresolved | 402 |

Indexing both clean `beta` trees yields 401 source files and **15 ambiguous
basenames**. The ones that are actually cited, and by how much:

| Basename | Citations | Collides with |
|----------|-----------|---------------|
| `eeprom_28c.cpp` | **286** | `firestarter/tests/fixtures/planted_cmake_manifest_missing_source/src/proms/eeprom_28c.cpp` |
| `firestarter.cpp` | **204** | 3 × `firestarter/tests/fixtures/planted_cmake_manifest_*/src/firestarter.cpp` |
| `firestarter.h` | **99** | **`firestarter_app/tests/fixtures/fake_firestarter/include/firestarter.h`** |
| `uno_rurp_shield.cpp` | 50 | 2 × `firestarter/tests/fixtures/…` |
| `host_stubs.cpp` | 9 | **23 real copies** under `firestarter/test/native/avr/*/` |
| `codegen.py` | 7 | `firestarter/tools/catalog/` vs `firestarter_app/tools/catalog/` |
| `test_update_version.py` | 4 | both repos |
| `__init__.py`, `main.cpp`, `serial_read_mock.h`, `update_version.py`, `codegen_vectors.py` | 1 each | various |

The three highest-cited ambiguities are exactly the phase's hottest files.
`firestarter.h` is **the `firestarter` name-collision trap in citation form** —
the app's own fixture tree contains an `include/firestarter.h`, which is the same
one-`..`-versus-two-`..` confusion `scan_paths.py`'s docstring documents at the
path-construction level.

**Recommended resolution rule for the extractor**, applied in order, with the
outcome recorded per record so nothing resolves silently:

1. If the cited string is an **exact** repo-relative path in the candidate set →
   use it.
2. If it is a **path suffix** of exactly one candidate → use that.
3. If it is a **bare basename**, resolve against an index built from the candidate
   set with `**/fixtures/**` and `**/fixture/**` **excluded**. This alone
   disambiguates `eeprom_28c.cpp`, `firestarter.cpp`, `firestarter.h`,
   `uno_rurp_shield.cpp` — **639 of the 665** ambiguous citations, because every
   colliding alternate is a planted or fake fixture.
4. Anything still ambiguous → **`resolution: ambiguous`, no `target_file_resolved`,
   excluded from the oracle, count reported.** Measured residue after step 3:
   **11 citations** (9 × `host_stubs.cpp`, 1 × `__init__.py`,
   1 × `serial_read_mock.h`). Small enough to resolve by hand if worth it.
5. Unresolvable → `resolution: unresolved`, count reported. **Measured: 1,351.**

**Never resolve a fixture path as if it were the real file.** A citation remapped
onto `tests/fixtures/planted_cmake_manifest_missing_source/src/proms/eeprom_28c.cpp`
would round-trip green against the wrong file — a silent-correctness failure of the
same family as F2.

### The 1,351 unresolved citations are mostly legitimate

Sampling the top targets shows these are **not** extractor bugs and must not be
force-resolved:

| Target | Count | What it is |
|--------|-------|------------|
| `database.c` | 117 | **infoic's external decompiled source**, not a repo file (`database.c:611` → `device->pin_map = (uint8_t)opts;`). Out-of-repo by design. |
| `flash_type_3.cpp`, `flash_type_4.cpp` | 57 + 50 | Renamed/removed firmware files |
| `primitives.cpp` | 53 | **The v1.16 primitives layer that was never merged** — citations into a file that never existed on `beta`. Corroborates `reference_v116_primitives_layer_never_merged`. |
| `check_size_baseline.py`, `139-check-claims.py`, `146-check-claims.py`, `check_permitted_claims.py` | 46 + 31 + 29 + 25 | Phase-scoped checkers under `.planning/phases/…`, i.e. citations *within* `.planning/`, not into swept source |
| `../firestarter/include/rurp_shield.h` | 29 | A `../`-relative citation — resolvable only relative to the citing document |

**The tool must record these, not crash on them and not drop them.** They are
outside the swept set, so they need no remapping — but a manifest generator that
silently discards 1,351 rows is indistinguishable from one that is broken.

---

## R3 — Planted-Violation Controls (SWEEP-07)

All results in this section were produced by **running the real gates** in this
session. Environment used (see §`Environment Availability`):

```bash
export UV_CACHE_DIR=<writable>            # ~/.cache/uv is NOT writable here
uv venv --python 3.11 <venv>              # uv fetches CPython 3.11.16
uv pip install --python <venv>/bin/python -e '.[test]'
cd firestarter_app
FIRESTARTER_FW_ROOT=/workspaces/firestarter \
  <venv>/bin/python -m pytest tests/test_sdp_table_parity.py -o addopts="" -q
```

Two mechanics notes: `-o addopts=""` is required because the project's
`addopts = "-ra -q"` plus a command-line `-q` suppresses the count line
(`reference_pytest_addopts_q_suppresses_count_line`). And **the sibling layout is
required** — `fw_presence.py` resolves `FW_ROOT` as `<app repo>/../firestarter` and
keys presence on `FW_ROOT/.git`; `/workspaces/firestarter` and
`/workspaces/firestarter_app` already satisfy this. `FIRESTARTER_FW_ROOT` overrides
the root but is **read at import time**, so it must be set in the process
environment, never via `monkeypatch`.

### Correction to D-06: the fixture mechanism already exists

CONTEXT.md's D-06 table records `test_sdp_table_parity.py` as
"Negative control? **no**". That is **not accurate**, and the correction makes
SWEEP-07 substantially cheaper:

- The module's docstring documents **Test 3: "Non-vacuous proof: an altered temp
  copy of eeprom_28c.cpp (one pair's byte flipped) makes the parity assertion
  fail"** — `test_altered_temp_copy_fails_parity_non_vacuous`.
- It ships a purpose-built planting seam: **`FIRESTARTER_SDP_SRC`**, with a
  `_sdp_src_path()` resolver that raises `FileNotFoundError` on a bad path
  (fail-closed) and an `_env_override` context manager. Its own comment says it
  "exists only so the non-vacuity test below can plant an altered fixture without
  touching the real, clean eeprom_28c.cpp".

**What D-06's underlying concern gets right:** the existing control proves the gate
detects a **byte-value drift**. It does **not** exercise either comment-blind
mechanism. So SWEEP-07's requirement stands — but the work is *two new test bodies
reusing an existing seam*, not a new fixture-wiring pattern.

### `test_sdp_table_parity.py` — both comment-blind mechanisms, proven RED

Baseline: **5 passed** on the unmodified source.

Three fixtures were built from the clean `beta` copy of `eeprom_28c.cpp` and run
through `FIRESTARTER_SDP_SRC`:

| Fixture | Plant | Result |
|---------|-------|--------|
| `planted_sdp_comment_misanchor.cpp` | Two comment lines inserted *above* the real declaration, spelling `EEPROM_SDP_ENABLE[3] = {` followed by `{0x1111,0x11}, {0x2222,0x22}, {0x3333,0x33} }` | **RED.** The gate read `[(4369,17),(8738,34),(13107,51)]` — **entirely from inside the comment.** It never saw the real table. |
| `planted_sdp_comment_brace.cpp` | One comment line inserted *inside* the initializer body: `// note: the terminating brace } of this table is load-bearing` | **RED.** `"EEPROM_SDP_ENABLE must have exactly 3 pairs, found 1"` — the brace-depth walk terminated early on the comment's `}`. |
| `planted_sdp_byte_drift.cpp` | Terminal byte `0xA0` → `0xA1` (the existing control's mechanism) | **RED.** Baseline sanity. |

**Why the mis-anchor works** (sharper than D-06 states): `_extract_byte_flip_pairs`
does `decl_pattern.search(source_text)` where
`decl_pattern = rf"\b{decl_name}\s*\[\s*\d*\s*\]\s*=\s*"` — it takes the **first**
match in the file, then `source_text.index("{", match.end())`, then a raw
`{`/`}` depth walk. A comment containing the initializer *form* anywhere above the
real declaration wins the race. This is reachable by exactly the operation D-01
prescribes: reflowing the `D-10 … SAFETY property` block at `:199-201`, which
already contains three `_PAIR_RE`-shaped pairs
(`{0x5555,0xAA}, {0x2AAA,0x55}, {0x5555,0xA0}`) and already names the arrays.

**The live collision is confirmed present and currently harmless.** In clean
`beta`, `eeprom_28c.cpp` has `extern const byte_flip_t EEPROM_SDP_ENABLE[3];` at
line 220 and the initializer at 221–225; the comment pairs sit at 199–201, i.e.
*above* the anchor, so they are outside the slice today.

#### The finding that raises SWEEP-07's severity: this gate can go SILENTLY GREEN

A fourth fixture, `planted_sdp_silent_green.cpp`:

- Two comment lines above the declaration spelling the initializer form with the
  **correct** bytes: `EEPROM_SDP_ENABLE[3] = {` / `{0x5555, 0xAA}, {0x2AAA, 0x55}, {0x5555, 0xA0} }`.
- The **real** table's terminal byte corrupted `{0x5555, 0xA0}` → `{0x5555, 0x10}`.

Result: **`5 passed`.**

`0xA0` is SDP lock; `0x10` is **chip erase**. That is precisely the "one-nibble
chip-erase hazard" the module's own `_HAZARD_CONTEXT` says it exists to catch, and
all five legs — including `test_unlock_table_terminal_byte_differs_from_erase_terminal_byte`
— were disarmed by two comment lines.

**Consequences for the plan:**

1. A green run from this gate after the sweep is **worthless as evidence**. This is
   `reference_firmware_renames_break_host_source_scanning_gates` realised on a
   comment-only edit, and it is a fail-**open** path, not the RED-flip that D-06
   emphasises.
2. The RED-before / RED-after controls SWEEP-07 requires are necessary but **not
   sufficient** — they prove the gate *can* fail, not that it is anchored on the
   real table. Recommend adding a leg that asserts the extracted slice's
   **byte offset** lies within the real declaration's span, or (better) that
   `_extract_byte_flip_pairs` is fed **comment-stripped** text.
3. The stripper already exists twice in-repo and is offset-preserving:
   `firestarter_app/tests/test_cap03_ack_layout_parity.py::_strip_comments`
   ("replacing each stripped span with whitespace of the SAME SHAPE … so any
   position offset computed against the result still lines up with the original
   file"), itself "copied structurally from
   `firestarter/tests/test_ack_layout_source_contract_v143.py`". Reusing it is a
   ~2-line change at each of the four `_extract_byte_flip_pairs` call sites.
   **But note this is a behaviour change to a gate**, which collides with the
   phase's "no code changes" constraint — see F6. Flag it for the planner; do not
   assume it.

### `test_dispatch_mirror.py` — the C++ leg

The leg is `test_dispatch_mirror_firmware_leg_enumerates_all_protocols`. Its
mechanism is a **set-membership scrape with no comment stripping**:

```python
fw_text = _FW_DISPATCH_TEST.read_text(encoding="utf-8")
fw_hex_tokens = {int(tok, 16) for tok in re.findall(r"0x([0-9A-Fa-f]+)", fw_text)}
missing = real_handler_protocols - fw_hex_tokens
assert not missing
```

Because it is a *superset* test, **any** `0x05` anywhere in the file — including
inside a comment — satisfies the requirement. The gate structurally cannot
distinguish "a native dispatch test exists for this protocol" from "a comment
mentions this protocol".

**Measured on clean `beta`** (using the repo's own `parse_protocols_md()` and
`_strip_comments`):

| Metric | Value |
|--------|-------|
| §0 protocols needing a positive routing test | 11 — `0x05 0x06 0x07 0x08 0x0B 0x0D 0x0E 0x10 0x27 0x28 0x29` |
| hex tokens in `test_configure_memory.cpp`, raw | 14 |
| hex tokens after comment stripping | **14 (unchanged)** |
| hex tokens existing **only** inside comments | **[] (none)** |
| §0 protocols whose only occurrence is a comment | **NONE** |

**Good news, and a real de-risking:** no §0 protocol currently depends on a
comment-only hex occurrence. So sweeping this file's 4 provenance hits **cannot
flip this gate RED today**, and the gate is not currently vacuous for any
protocol. Unlike `eeprom_28c.cpp`, there is **no live collision here** — the
SWEEP-07 control must be a purely synthetic plant.

**The two planted fixtures, both run this session.** `_FW_DISPATCH_TEST` is a
module-level constant read *inside* the test body, so
`monkeypatch.setattr(test_dispatch_mirror, "_FW_DISPATCH_TEST", fixture)` works —
the same shape `test_json_key_parity.py` uses.

| Fixture | Plant | Result |
|---------|-------|--------|
| `planted_dispatch_comment_only_hex.cpp` | every real `0x10` usage rewritten to `0xFF`; a **comment** added mentioning `0x10` | **GREEN — fail-open control.** This is the leg SWEEP-07 needs: it proves a comment alone satisfies the gate. |
| `planted_dispatch_missing_hex.cpp` | every real `0x10` usage rewritten to `0xFF`; **no** comment mention | **RED** — `"firmware leg test_configure_memory.cpp does not enumerate §0 protocol(s): 0x10"`. Proves the gate can fail. |

The real `0x10` occurrences are
`make_handle(0x10, 0, CMD_READ)` and two `{0x10, "flash_intel (0x10)"}` table rows —
so `0x10` is a clean choice for the plant.

**Both fixtures are needed**, and they prove different things: the RED one
satisfies SWEEP-07's literal wording; the GREEN one documents the fail-open
mechanism, which is the actual hazard. Recommend the plan require both.

### The model to copy: `test_json_key_parity.py`

Confirmed as the right template. It ships **16 planted fixtures** under
`firestarter_app/tests/fixtures/` (`planted_json_parser_key_string_drift.c`,
`planted_json_parser_undispatched_key.c`, and 14 others for sibling gates), wired
by `monkeypatch.setattr` on a module constant, with committed fixture files that
are "always present regardless of whether the sibling firmware" repo is checked
out — so the planted legs carry **no** `requires_fw` decorator and run in
standalone app CI.

**The "V12 ceremony" every planted leg performs** (read from
`test_cap03_ack_layout_parity.py::test_planted_literal_index_is_detected`) — copy
it, it is the house pattern:

1. Capture the **real** file's `git hash-object` sha *before* any monkeypatch.
2. `monkeypatch.setattr` the source constant to the fixture.
3. `with pytest.raises(AssertionError)` around the **same helper the live leg
   calls** — never a parallel reimplementation.
4. Assert a distinguishing phrase is in the message, and that the *other* plant's
   distinguishing phrase is **absent** (leg isolation).
5. Assert the real file's sha is **unchanged**, and assert
   `_git_porcelain(FW_ROOT) == ""` — the plant must never write into the real
   firmware checkout.

Step 5 is the origin of F7/F8: these legs require the firmware working tree to be
**porcelain-clean**, and they are RED right now for exactly that reason.

### Can the RED-before / RED-after proof run in this devcontainer?

**Yes, verified.** `test_sdp_table_parity.py` (5 tests) and the `test_dispatch_mirror.py`
C++ leg both ran, and all six planted fixtures produced the results tabulated
above, under `uv`-provisioned **CPython 3.11.16** with the sibling layout at
`/workspaces/firestarter` + `/workspaces/firestarter_app`.

- **Python must be 3.11, not the devcontainer's 3.12** — app CI runs 3.11 only
  (`reference_devcontainer_py312_masks_ci_py39`). `python3.11` is **not** on
  `PATH`; `uv venv --python 3.11` fetches it.
- `UV_CACHE_DIR` must be redirected — `~/.cache/uv` is not writable (`os error 13`).
- `pip` is absent from the uv venv; use `uv pip install`.
- For `test_sdp_table_parity.py` alone the package need not be installed (rootdir
  is on `sys.path`). For the full suite, `uv pip install -e '.[test]'` is needed;
  `firestarter.egg-info/` **is** in `.gitignore` (line 6), so this does not dirty
  the tree.
- The **planted legs of `test_cap03_ack_layout_parity.py`, `test_json_key_parity.py`,
  `test_py32_asset_name_host.py` and `test_py32_flash_map_host.py` require a
  porcelain-clean firmware tree** and cannot be proven green until D-12
  precondition 1 lands.

---

## Corpus Measurements

Reproducing the survey against clean `beta` exports, with the writeup's regex
(`(//|/\*|^\s*\*|#)\s*(Task|Phase|Plan|P\d{3}|Req|REQ-|CAP-0|D-\d|WR-\d|LOOP-\d|\d{3}-CONTEXT)`):

| Group | CONTEXT.md (D-04) | **Measured** | Files |
|-------|-------------------|--------------|-------|
| `firestarter/src` + `include` | 130 | **129** | 34 |
| `firestarter/test` | 216 | **216 (exact)** | 60 |
| `firestarter/lib` | — | **0** | 0 |
| `firestarter_app/firestarter` | 132 | **132 (exact)** | 20 |
| `firestarter_app/tests` | 115 | **115 (exact)** | 37 |
| `firestarter_app/tools` | 43 | **43 (exact)** | 9 |
| **TOTAL** | 636 | **635** | **160** |

Four of five groups reproduce **exactly**; `src`+`include` differs by 1 (regex
reconstruction ambiguity). D-04's headline **331 test-file hits (216 + 115)
reproduces exactly**, as does the 52% share. The writeup's "~646 hits / 167 files"
is the wider earlier survey; **160 files** is the figure to plan against.

**Token frequency** (a line can match more than one token):

| Token | Hit-lines |
|-------|-----------|
| `Phase` | 308 |
| `D-#` | 185 |
| `Plan` | 56 |
| `Task` | 25 |
| `CAP-0` | 20 |
| `WR-#` | 18 |
| `LOOP-#` | 16 |
| `Req` | 4 |
| `###-CONTEXT` | 3 |
| `P###` | **0** |
| `REQ-` | **0** |

Two of the survey regex's eleven alternations (`P\d{3}`, `REQ-`) match **nothing**
on `beta`. Harmless, but the plan should not budget triage effort for them.

**D-02's `CAP-0N` exemption, measured:** exactly **20 hit-lines** match `CAP-0`
and **no other** token — 13 in `firestarter_app/firestarter`, 4 in
`firestarter_app/tests`, 3 in `firestarter/src`. So the exemption removes 20 of
635, leaving a **net actionable corpus of 615 hit-lines**. `[VERIFIED: measured]`

### The 8-Path Inventory (SWEEP-06 / D-05) — hit counts filled in

D-05's table left several hit counts as "yes" or "—". Measured on clean `beta`:

| Path | D-05 says | **Measured hits** | Disposition |
|------|-----------|-------------------|-------------|
| `test/native/avr/_shared/sdp_bus_config.h` | — (generated) | **0** | Generated by `tools/gen_sdp_bus_config.py`. **0 hits → provably needs no generator fix.** Output untouched. |
| `test/native/avr/_shared/validation_matrix.h` | — (generated) | **0** | Generated by `tools/gen_validation_header.py`. **0 hits → provably needs no generator fix.** Output untouched. |
| `doc/PROTOCOLS.md` | — (outside globs) | **2** | Outside the sweep's globs, but it **does** carry 2 hits, and `test_dispatch_mirror.py` reads it. Confirm the out-of-scope ruling explicitly rather than by silence. |
| `include/firestarter.h` | yes | **2** | In sweep |
| `src/proms/eeprom_28c.cpp` | **33** | **33 (exact)** | In sweep, own plan (SWEEP-08) |
| `src/firestarter.cpp` | 8 | **8 (exact)** | In sweep, **minus** the D-02 no-touch region |
| `src/json_parser.c` | 8 | **7** | In sweep |
| `test/native/avr/test_dispatch/test_configure_memory.cpp` | yes | **4** | In sweep, narrow treatment (D-04) |

**SWEEP-06's "fixed at their generators or shown to need no fix" is discharged by
measurement:** both generated headers carry **zero** provenance hits, so no
generator change is required and their output is never edited. Record the zero.

### No-Touch Region (D-02 / SWEEP-02) — verified intact

`firestarter/src/firestarter.cpp:177-195` is present on clean `beta` and contains
the CAP-01/CAP-02/CAP-03 wire-layout block. The string
`test_cap03_ack_layout_parity.py` pins verbatim
(`_WIRE_LAYOUT_COMMENT = "[buffer_size u16 BE][hw_revision u8][ver_len u8][ver bytes][write_budget_s u16 BE]"`)
sits at **line 192**. `[VERIFIED: sed + grep]`

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Old→new line map from a diff | A hunk-header parser for `git diff -U0` | `difflib.SequenceMatcher(..., autojunk=False).get_opcodes()` | Stdlib, no subprocess, no git-revision plumbing; works on the composite non-commit-pair diff Phase 159 needs |
| Offset-preserving comment stripping | A new C/C++ comment stripper | `firestarter_app/tests/test_cap03_ack_layout_parity.py::_strip_comments` | Already exists **twice** in-repo (also `firestarter/tests/test_ack_layout_source_contract_v143.py`), handles `//` and `/* */`, and preserves byte offsets |
| Proving a source-scanning gate still works | A green run of the gate | A committed planted fixture + the 5-step "V12 ceremony" | These gates **fail open**; F2 proves one can be silently disarmed |
| Planting a fixture into `test_sdp_table_parity.py` | A new temp-file/env mechanism | The existing `FIRESTARTER_SDP_SRC` seam + `_env_override` | Purpose-built for exactly this, fail-closed on a bad path |
| Planting into `test_dispatch_mirror.py` | A new seam | `monkeypatch.setattr(module, "_FW_DISPATCH_TEST", fixture)` | Constant is read inside the test body; matches the `test_json_key_parity.py` house pattern |
| The cross-repo scan-path inventory | A `grep`-derived file list | `scan_paths.py::ALL_CROSS_REPO_PATHS` | D-05; the module's own docstring explains that a mechanical derivation **re-creates** the name-collision trap |
| Resolving a cited basename to a file | `find`-first-match | The 5-step rule in §R2, with fixtures excluded and residue reported | 665 citations are ambiguous; a first-match resolver silently binds 639 of them to planted fixtures |
| Byte-identity comparison | Parsing the `pio run` size summary | `sha256sum .pio/build/uno/firestarter_uno.elf` | Strictly stronger, free, and proven immune |
| Idempotency | "Run it twice and eyeball it" | The fixed-point/oracle write predicate + a **chained-map** fixture | A single-deletion-block fixture passes even against a blind implementation |

**Key insight:** in this phase almost every "custom solution" temptation is a
temptation to build a *second, weaker* oracle beside one that already exists. The
repo is unusually rich in fail-closed seams, planted fixtures and offset-preserving
helpers; the phase's job is to *use* them, and its main risk is trusting a green
run from a gate that was never anchored on what it claims to check.

---

## Common Pitfalls

### Pitfall 1: Trusting a green run from a comment-blind gate
**What goes wrong:** the sweep lands, all gates are green, and a real defect ships.
**Why:** `test_sdp_table_parity.py` extracts by first-regex-match plus a raw brace
walk. A reflowed comment above the declaration wins the anchor race. Proven: 5/5
green with `0xA0`→`0x10` corruption in the real table.
**How to avoid:** plant the fail-open fixture (comment says the right thing, code
says the wrong thing) and require it to be **RED**. If it is green, the gate is
not anchored and the sweep of that file is unverified.
**Warning signs:** the gate passes but the extracted pair list, if printed, has
values that appear only in comment text.

### Pitfall 2: `difflib`'s `autojunk` silently corrupting the map
**What goes wrong:** the map looks right on small fixtures and is wrong on real files.
**Why:** default `autojunk=True` treats elements occurring in >1% of a sequence of
≥200 items as junk. Over a 900-line C++ file, `}` and blank lines get auto-junked
and excluded from `equal` runs.
**How to avoid:** `SequenceMatcher(None, old, new, autojunk=False)`, always.
**Warning signs:** the map has `None` for lines that visibly did not change; the
map's surviving-line count is lower than `len(new_lines)`.

### Pitfall 3: A single-deletion-block idempotency fixture
**What goes wrong:** the idempotency test passes; the tool is not idempotent.
**Why:** a chain (`map[a]=b`, `map[b]=c`) requires **two separated** deletion
blocks. With one block, no surviving line is also a key mapping elsewhere, so a
blind implementation is accidentally idempotent.
**How to avoid:** fixture with ≥2 deletion blocks; assert the chain exists before
asserting idempotency.
**Warning signs:** the fixture's map has no key `a` with `map[a]` itself a key.

### Pitfall 4: Measuring the "before" against the dirty firmware tree
**What goes wrong:** the byte-identity pair, the 172/172 native run and the host
suite baseline are all taken against the size-reduction patch, not `beta`.
**Why:** `firestarter` is on `size-reduction-survey` with 11 modified files (D-12).
**How to avoid:** discharge D-12 precondition 1 **first**; re-take every baseline.
**Warning signs:** `git -C firestarter status --porcelain` is non-empty; 6 firmware
gates and 7 host gates are RED (see F8 for the exact counts).

### Pitfall 5: Resolving a cited basename to a planted fixture
**What goes wrong:** a citation remaps onto
`tests/fixtures/planted_cmake_manifest_missing_source/src/proms/eeprom_28c.cpp`
and round-trips green against the wrong file.
**Why:** 286 citations say `eeprom_28c.cpp` with no path; two files match.
**How to avoid:** exclude `**/fixtures/**` from the resolution index; report the
11-citation residue rather than guessing.
**Warning signs:** `target_file_resolved` contains `fixtures/` or `fake_`.

### Pitfall 6: Editing a blob-sha-pinned file without regenerating its sidecar
**What goes wrong:** the sweep commit turns four firmware gates RED, and the cause
looks like a comment-sweep defect rather than a stale sidecar.
**Why:** F3 — four `tests/golden/*.json` sidecars pin `git rev-parse HEAD:<path>`.
**How to avoid:** treat the five pinned files as a distinct disposition class;
regenerate all four sidecars **in the same commit** as the firmware sweep.
**Warning signs:** `test_eprom_params_citations.py::test_blob_shas_match_the_recorded_sources`,
`test_protocol_branch_inventory.py`, `test_golden_trace_identity*.py` RED.

### Pitfall 7: Running the host suite before the sub-repo commits land
**What goes wrong:** 7+ gates RED on the sweep's own uncommitted edits.
**Why:** F7 — **9** modules assert git porcelain, 4 of them in the app repo
asserting on the *firmware* repo.
**How to avoid:** D-11's ordering, enforced: firmware commit → app commit → host
suite. Not "commit eventually".

### Pitfall 8: `pytest -q` hiding the count line
**What goes wrong:** you cannot tell 1963-passed from 1963-collected.
**Why:** project `addopts = "-ra -q"`; adding `-q` doubles it.
**How to avoid:** `-o addopts=""`.

---

## Code Examples

### The line map (stdlib, prototyped and run this session)

```python
import difflib

def build_map(old_lines, new_lines):
    """old 1-based line -> new 1-based line, or None if the line did not survive."""
    sm = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    m = {}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                m[i1 + k + 1] = j1 + k + 1
        elif tag in ('delete', 'replace'):
            for k in range(i1, i2):
                m[k + 1] = None
    return m


def _surviving(m, n_old):
    return sorted(l for l in range(1, n_old + 1) if m.get(l) is not None)


def map_point(m, line, n_old, direction):
    """direction='fwd' for a range START (clamp to next survivor),
       'back' for a range END (clamp to previous survivor)."""
    if m.get(line) is not None:
        return m[line], False                    # survived; retarget=False
    surv = _surviving(m, n_old)
    if direction == 'fwd':
        c = [l for l in surv if l > line]
        return (m[c[0]], True) if c else (None, True)
    c = [l for l in surv if l < line]
    return (m[c[-1]], True) if c else (None, True)


def map_range(m, a, b, n_old):
    a2, ra = map_point(m, a, n_old, 'fwd')
    b2, rb = map_point(m, b, n_old, 'back')
    return a2, b2, (ra or rb)                    # third value -> `retarget`
```

Measured on a 20-line fixture with old lines 6–10 deleted: `map_range(m,3,18,20)`
→ `(3, 13, False)`. Old span 16 → new span 11: **shrank by exactly 5**, the
deleted-block size. A constant-offset implementation returns `(-2, 13)`.

### The idempotent write predicate (the REMAP-02 oracle, reused)

```python
def apply_record(doc_text, rec, new_lines, line_map, path_re):
    """rec: {target_line, source_text, ...} captured PRE-sweep."""
    def sub(mo):
        cur = int(mo.group(1))
        # 1. fixed point? -> no-op. THIS is what makes the tool idempotent.
        if 1 <= cur <= len(new_lines) and new_lines[cur - 1] == rec["source_text"]:
            return mo.group(0)
        # 2. only rewrite the recorded PRE-sweep line; never "any key of the map"
        if cur != rec["target_line"]:
            return mo.group(0)
        tgt = line_map.get(cur)
        if tgt is None:
            return mo.group(0)              # deleted -> retarget by hand (D-08)
        # 3. oracle BEFORE writing; a mismatch means the map is wrong
        assert new_lines[tgt - 1] == rec["source_text"], "oracle violated"
        return f'{mo.group("path")}:{tgt}'
    return path_re.sub(sub, doc_text)
```

Measured: run 1 rewrites `:15`→`:10`; runs 2 and 3 are **exact no-ops**. The same
map applied blind gives `:15`→`:10`→`:8`→`:6`.

### Planting into `test_sdp_table_parity.py` (existing seam)

```python
_FIXTURE_MISANCHOR = _FIXTURES_DIR / "planted_sdp_comment_misanchor.cpp"

@requires_fw
def test_planted_comment_misanchor_is_detected() -> None:
    assert _FIXTURE_MISANCHOR.is_file()
    real = _EEPROM_28C_CPP
    before = _git_hash_object(real)
    with _env_override("FIRESTARTER_SDP_SRC", str(_FIXTURE_MISANCHOR)):
        with pytest.raises(AssertionError) as ei:
            test_eeprom_sdp_enable_matches_flash_enable_write_and_write_protection()
    assert "Diverging pair" in str(ei.value)
    assert _git_hash_object(real) == before          # V12 ceremony step 5
    assert _git_porcelain(FW_ROOT) == ""
```

### Planting into `test_dispatch_mirror.py` (module-constant monkeypatch)

```python
def test_planted_comment_only_hex_is_NOT_detected(monkeypatch) -> None:
    """Fail-open control: a comment mentioning 0x10 satisfies the gate even
    though every real 0x10 usage is gone. Documents the hazard; must stay green
    until the gate strips comments."""
    monkeypatch.setattr(
        sys.modules[__name__], "_FW_DISPATCH_TEST", _FIXTURE_COMMENT_ONLY_HEX
    )
    test_dispatch_mirror_firmware_leg_enumerates_all_protocols()   # passes

def test_planted_missing_hex_is_detected(monkeypatch) -> None:
    monkeypatch.setattr(
        sys.modules[__name__], "_FW_DISPATCH_TEST", _FIXTURE_MISSING_HEX
    )
    with pytest.raises(AssertionError) as ei:
        test_dispatch_mirror_firmware_leg_enumerates_all_protocols()
    assert "0x10" in str(ei.value)
```

---

## F3 in detail — Blob-SHA-Pinned Source Files (NEW, blocking)

Four committed golden sidecars in the **firmware** repo pin `git rev-parse HEAD:<path>`
blob SHAs of source files. All four pinned SHAs were verified to match `beta`
today, and all five pinned files carry provenance hits, so the sweep breaks all
four.

| Sidecar | Pinned path(s) | Pinned SHA (verified vs `beta`) | Provenance hits | Gate |
|---------|----------------|--------------------------------|-----------------|------|
| `tests/golden/eprom_params_citations.json` | `include/eprom_params.h` | `b04c788b…` ✓ | **1** | `test_eprom_params_citations.py::test_blob_shas_match_the_recorded_sources` |
| " | `src/proms/eprom_params.cpp` | `5dffe841…` ✓ | **2** | " |
| `tests/golden/protocol_branch_inventory.json` | `src/proms/eprom.cpp` | `838aca47…` ✓ | **20** | `test_protocol_branch_inventory.py` |
| " | `src/proms/eprom_params.cpp` | `5dffe841…` ✓ | **2** | " |
| `tests/golden/eprom_v131_trace_inventory.json` | `test/native/avr/_shared/eprom_v131_expected.h` | `ae279eba…` ✓ | **4** | `test_golden_trace_identity_eprom_v131.py::test_blob_sha_matches_the_recorded_inventory` |
| `tests/golden/sdp_expected_inventory.json` | `test/native/avr/_shared/sdp_expected.h` | `dd1ba1cc…` ✓ | **3** | `test_golden_trace_identity.py` |

**Five distinct files, 30 provenance hits, `eprom_params.cpp` pinned twice.**

Why this is phase-shaping:

1. **`src/proms/eprom_params.cpp` is one of SWEEP-01's five named keep-and-reflow
   examples** (`eprom_params.cpp:61` — `D-05: fail closed, zero hardware side
   effects`). The requirement explicitly asks for that comment to be reflowed. Doing
   so changes the blob SHA. Verified: removing that one line changes
   `5dffe841aeb7013f9f53e9991a6248b203ae22da` →
   `d0b5183e53047e5a6b9db87eac948ba7f6311a3a`.
2. **`src/proms/eprom.cpp` is the most-cited file in `.planning/`** — 627 citations
   — and carries 20 hits.
3. **No regeneration tool exists.** `tools/` has no citation/inventory generator;
   `test_eprom_params_citations.py`'s own failure message says to "re-derive
   `tests/golden/eprom_params_citations.json`". This is hand work, and it must land
   in the **same commit** as the firmware sweep (D-11), or the intermediate tree is
   RED.
4. **These four gates are content-pinned, not comment-blind.** They fail *closed*,
   which is the good direction — but they will fail, and the plan must expect it
   rather than diagnose it.

Two related modules were checked and are **safe**: `test_config_schema_pinned.py`
and `test_config_storage_seam_shape.py` both state explicitly that "No blob SHA
literal appears anywhere in this module" — they compute SHAs at runtime for a
planted-copy demonstration. The app repo's `test_consistency_check.py` hashes
`run_NN.bin` outputs, not source. `[VERIFIED: read all three]`

**Recommended disposition:** add a **sixth class** to SWEEP-06 —
*blob-SHA-pinned* — listing these five files, and add a task that regenerates the
four sidecars in the firmware sweep commit. Alternatively, exempt the five files
from the sweep entirely (costs 30 of 615 hits, ~5%) and record the exemption. The
planner should choose; both are defensible, and the second is markedly cheaper.

---

## F4 in detail — The Firmware Repo's Own Gates (NEW)

D-05's inventory is `firestarter_app/tests/scan_paths.py::ALL_CROSS_REPO_PATHS` —
the paths the **app** repo resolves into the firmware repo. The **firmware repo
has its own Python gate suite**, and it is larger:

| Metric | Count |
|--------|-------|
| `firestarter/tests/*.py` modules | **32** |
| …that read `src/` or `include/` source text | **30** |
| …that carry a `_strip_comments` | **8** |
| **…that scan source text with NO comment stripping** | **22** |

The 8 with stripping: `test_eprom_params_citations.py`,
`test_requirement_case_mapping_v131.py`, `test_ack_layout_source_contract_v143.py`,
`test_protocol_branch_inventory.py`, `test_progress_emission_is_leonardo_only.py`,
`test_hv_routing_source_contract_v142.py`,
`test_trace_segment_exhaustiveness_v131.py`,
`test_write_path_source_contract_v131.py`.

The 22 without: `test_check_erase_no_vpp.py`, `test_check_landing_range.py`,
`test_check_orphan_provisional.py`, `test_check_cmake_manifest.py`,
`test_checker_convention.py`, `test_config_schema_pinned.py`,
`test_vpp_seam_manual_on_every_board.py`,
`test_flash_geometry_recorded_before_linker.py`,
`test_config_storage_seam_shape.py`, `test_check_size_baseline.py`,
`test_check_build_warnings.py`, `test_config_storage_design_vendored.py`,
`test_config_storage_eeprom_regression.py`, `test_py32_flash_map.py`,
`test_check_release_assets.py`, `test_flash_path_record_sync.py`,
`test_pr45_non_ancestry.py`, `test_golden_trace_identity_eprom_v131.py`,
`test_config_storage_dualslot.py`, `test_golden_trace_identity.py`,
`test_update_version.py`, `test_pinmap_guard_fires.py`.

Not all 22 are at risk — several read source only to check for a *presence* of a
construct, and some (`test_config_schema_pinned.py`,
`test_config_storage_seam_shape.py`) were verified safe above. But the phase
currently has **no** requirement covering them, and per
`reference_firmware_renames_break_host_source_scanning_gates` a green run from any
of them is not evidence.

**Recommendation:** the plan should either (a) extend SWEEP-06's classification to
these 22 with a one-line disposition each — cheap, since the question is only
"does it pattern-match text that a comment could contain?" — or (b) record an
explicit, reasoned out-of-scope ruling. Silence would leave 22 fail-open gates
un-assessed across a 615-hit comment sweep. **Measured baseline to work from:
`pytest tests/` in the firmware repo is 317 passed / 6 failed in 12 s.**

---

## Validation Architecture

`workflow.nyquist_validation` is **absent** from `.planning/config.json` → treated
as **enabled**. This section is required.

### The coverage problem, stated plainly

This phase's validation ceiling is unusually low, and pretending otherwise is the
main risk:

- The **strongest** oracle (`uno` byte-identity) covers **129 of 635 hit-lines
  (20%)** — only `firestarter/src` + `include`, and only files that reach the
  `uno` build. It covers **zero** of the 331 test-file hits (52% of the corpus,
  D-04) and **zero** of the 290 host-repo hits.
- The **host repo has no size or byte-identity oracle at all.** 290 hit-lines
  (`firestarter` 132 + `tests` 115 + `tools` 43) have no mechanical
  "did-this-change-behaviour" check beyond the host test suite itself.
- The gates that *do* scan firmware source **fail open**, and F2 proves one of
  them can be driven silently green by exactly the operation D-01 prescribes.
- **Comment content itself is not mechanically checkable.** Whether D-01 step 3's
  guard was honoured — "never delete the only statement of a non-obvious
  invariant" — is irreducibly a review judgment.

So the honest architecture is: **strong mechanical proof that nothing *executable*
changed; planted-violation controls that the gates still work; and explicit,
named human review for the comment-content decisions**, with the review scope
bounded by measurement rather than left open.

### Test Framework

| Property | Value |
|----------|-------|
| Firmware unit/native | PlatformIO `pio test -e native` (Unity), **172 test cases** |
| Firmware CI legs | `native` + `native_nodevtools` + `pytest tests/` (per `reference_v131_firmware_native_gate_gotchas` — these three **only**) |
| Firmware Python gates | pytest, `firestarter/tests/` — **32 modules, 317 passing** |
| Host | pytest 8+ / syrupy 5+, `firestarter_app/tests/` — **1,970 tests** |
| Host config file | `firestarter_app/pyproject.toml` (`addopts = "-ra -q"`, line 107) |
| Firmware build | `pio run -e uno` (also `uno328pb`, `leonardo`) |
| Quick run (firmware) | `pio test -e native` — **22 s** |
| Quick run (host, targeted) | `pytest tests/test_sdp_table_parity.py tests/test_dispatch_mirror.py -o addopts="" -q` — **< 1 s** |
| Full suite (host) | `FIRESTARTER_FW_ROOT=<fw> pytest tests/ -o addopts="" -q` — **235 s (3 m 55 s)** |
| Full suite (firmware gates) | `pytest tests/` — **12 s** |
| Byte-identity oracle | `rm -rf .pio/build/uno && pio run -e uno && sha256sum .pio/build/uno/firestarter_uno.elf` — **1.5 s** |
| Python for host gates | **CPython 3.11 only** (`uv venv --python 3.11`); the devcontainer's 3.12 masks app CI |

### Phase Requirements → Test Map

| Req | Behavior | Test Type | Automated Command | Exists? |
|-----|----------|-----------|-------------------|---------|
| SWEEP-01 | Triage procedure applied per hit; 5 keep-examples reflowed | **manual-only** | — (comment *content* is not machine-checkable) | ❌ review |
| SWEEP-01 | The sweep changed no code | automated | `sha256sum .pio/build/uno/firestarter_uno.elf` (pair) | ✅ |
| SWEEP-02 | `CAP-0N` exempt; no-touch region untouched | automated | `git diff beta -- src/firestarter.cpp \| grep -c '^[-+].*buffer_size u16 BE'` → must be **0**; plus `pytest tests/test_cap03_ack_layout_parity.py` | ✅ |
| SWEEP-02 | cap03 gate still able to fail | automated | `pytest tests/test_cap03_ack_layout_parity.py -k planted` (2 existing planted legs) | ✅ (needs clean FW tree) |
| SWEEP-03 | IDs stripped in src, retained in tests | automated | Re-run the survey regex per group; assert `src`+`include` ID hits → 0 and test-file ID hits unchanged | ❌ **Wave 0** |
| SWEEP-04 | Narrow treatment on test files | automated (weak) | `pio test -e native` = 172/172 — proves tests still **compile and pass**, not that comments were treated narrowly | ✅ |
| SWEEP-05 | `uno` byte-identical | **automated, strongest** | cold build + `sha256sum` on `.elf`, `.hex`, plus `RAM:`/`Flash:` | ✅ |
| SWEEP-05 | other two AVR targets unchanged | automated | same for `-e uno328pb`, `-e leonardo` (free; recommend adding) | ✅ |
| SWEEP-06 | 8 paths classified; generated headers need no fix | automated | hit-count assertion per path; the two generated headers must measure **0** | ❌ **Wave 0** |
| SWEEP-06 (F4) | 22 non-stripping firmware gates dispositioned | **manual-only** | `pytest tests/` (317 pass) is necessary, not sufficient — fail-open | ❌ review |
| SWEEP-07 | sdp gate RED on comment mis-anchor | automated | `pytest tests/test_sdp_table_parity.py -k planted_comment` | ❌ **Wave 0** (proven feasible) |
| SWEEP-07 | sdp gate RED on comment brace break | automated | same | ❌ **Wave 0** (proven feasible) |
| SWEEP-07 | sdp gate not silently green (F2) | automated | a leg asserting the extracted slice lies inside the real declaration span | ❌ **Wave 0**, **recommended addition** |
| SWEEP-07 | dispatch C++ leg RED on missing hex | automated | `pytest tests/test_dispatch_mirror.py -k planted_missing` | ❌ **Wave 0** (proven feasible) |
| SWEEP-07 | dispatch C++ leg fail-open documented | automated | `pytest tests/test_dispatch_mirror.py -k planted_comment_only` (asserts **green**) | ❌ **Wave 0** (proven feasible) |
| SWEEP-08 | `eeprom_28c.cpp` its own plan | process | plan-structure check; not a test | n/a |
| SWEEP-09 | manifest covers all candidate-swept citations, both endpoints | automated | manifest generator's own self-check: row count, 0 unhandled variants, every range has `target_line_end` + `source_text_end` | ❌ **Wave 0** |
| SWEEP-09 | manifest schema is valid JSONL | automated | `python -c` line-by-line `json.loads` + required-key assertion | ❌ **Wave 0** |
| SWEEP-10 | retarget subset flagged, count reported | automated | count rows with `retarget: true`; assert none has a null `target_line` without a recorded reason | ❌ **Wave 0** |
| SWEEP-11 | tool idempotent | automated | `test_remap_citations.py::test_idempotent_on_chained_map` (**chain required**) | ❌ **Wave 0** |
| SWEEP-11 | range shrinks, not translates | automated | `test_remap_citations.py::test_range_spanning_deleted_block_shrinks` | ❌ **Wave 0** |
| SWEEP-11 | explicit repo root, non-zero on empty input | automated | `test_remap_citations.py::test_exits_nonzero_on_empty_input` + assert `_HERE` absent from the module | ❌ **Wave 0** |
| SWEEP-11 | tool **not applied** | automated | `git diff beta --stat -- .planning/` shows no citation-bearing file modified except the new `v1.33/` tree | ❌ **Wave 0** |
| SWEEP-12 | marker planted, names swept files, points at REMAP-04 | automated (weak) | file exists + contains the literal `REMAP-04` and ≥1 swept path | ❌ **Wave 0** |
| SWEEP-13 | commit granularity + ordering | automated | `git -C firestarter rev-list --count <pre>..HEAD` == 1; same for app; both porcelain before the host suite | ❌ **Wave 0** |
| SWEEP-13 | archived-`milestones/` collision recorded | **manual-only** | n/a — **this phase edits nothing under `milestones/`** (§R6) | ❌ record |
| F3 | four golden sidecars regenerated in lockstep | automated | `pytest tests/test_eprom_params_citations.py tests/test_protocol_branch_inventory.py tests/test_golden_trace_identity.py tests/test_golden_trace_identity_eprom_v131.py` | ✅ (gates exist; the **fix** is Wave 0) |

### Sampling Rate

- **Per task commit (firmware):** `rm -rf .pio/build/uno && pio run -e uno && sha256sum .pio/build/uno/firestarter_uno.elf` — 1.5 s. At this cost, run it **per file swept**, not per wave; it localises a regression to one file.
- **Per task commit (host):** the two SWEEP-07 gates + any gate naming the swept file — < 1 s.
- **Per wave merge (firmware):** `pio test -e native` (22 s) + `pytest tests/` (12 s).
- **Per wave merge (host):** targeted subset. The **235 s** full host suite is too slow for per-task and belongs at the phase gate.
- **Phase gate:** all three firmware CI legs (`native`, `native_nodevtools`,
  `pytest tests/`) + the full host suite, **after** both sub-repo commits land
  (D-11 / F7), with the byte-identity pair recorded.
- **Timeout guidance:** 300 s is **not** needed for anything this phase runs. The
  slowest leg measured is the host suite at 235 s — allow **600 s**. See §R6 on
  the record-gate note.

### Wave 0 Gaps

- [ ] `firestarter_app/tests/fixtures/planted_sdp_comment_misanchor.cpp` — SWEEP-07 (content specified in §R3)
- [ ] `firestarter_app/tests/fixtures/planted_sdp_comment_brace.cpp` — SWEEP-07
- [ ] `firestarter_app/tests/fixtures/planted_dispatch_comment_only_hex.cpp` — SWEEP-07 fail-open control
- [ ] `firestarter_app/tests/fixtures/planted_dispatch_missing_hex.cpp` — SWEEP-07 RED control
- [ ] New test legs in `firestarter_app/tests/test_sdp_table_parity.py` (3) and `test_dispatch_mirror.py` (2) — SWEEP-07. **F6: this is new test code; confirm scope.**
- [ ] `.planning/v1.33/tools/remap_citations.py` — SWEEP-11
- [ ] `.planning/v1.33/tools/test_remap_citations.py` — SWEEP-11 (must include a **chained-map** idempotency fixture)
- [ ] `.planning/v1.33/tools/fixtures/` — synthetic diff fixtures (≥2 deletion blocks)
- [ ] A manifest **generator** (SWEEP-09 does not name one, but 10k rows cannot be hand-authored). Recommend `.planning/v1.33/tools/build_citation_manifest.py`, sharing the resolution rule with the remapper.
- [ ] A survey-regex re-runner for the SWEEP-03 / SWEEP-06 hit-count assertions
- [ ] Regenerated `firestarter/tests/golden/{eprom_params_citations,protocol_branch_inventory,eprom_v131_trace_inventory,sdp_expected_inventory}.json` — F3
- [ ] **Framework install:** none needed in CI. Locally: `uv venv --python 3.11` + `uv pip install -e '.[test]'` with `UV_CACHE_DIR` redirected.

---

## R6 — Two Known-Hazard Confirmations

### SWEEP-13 / archived `milestones/` records

**This phase does not edit anything under `.planning/milestones/`.** The remap is
deferred to Phase 159 (D-01 / D-10), and this phase's only `.planning/` writes are
**new** files under `.planning/v1.33/` (which does not yet exist — verified) plus
the staleness marker. The manifest *records* 1,302 shifting citations that live in
`milestones/`, but recording is a read.

Therefore `reference_milestone_close_breaks_record_gates` (archived sections
orphan `lines=N` counters) **cannot** be tripped by Phase 154. SWEEP-13's clause
"whether editing archived `milestones/` records tripped [it] is recorded either
way" is discharged by recording: **"No archived record was edited — the citation
repair is deferred to Phase 159 per D-01, so the archived-record hazard belongs to
REMAP-01, not to this phase."** That is the collision's *absence, with cause*,
which is exactly what the requirement asks for.

The hazard is real for **Phase 159**, where 1,302 `milestones/` citations do get
rewritten. Worth carrying forward as a note on REMAP-01.

The only `lines=` counters found outside archives are in `.planning/ROADMAP.md`,
which this phase does not rewrite. `[VERIFIED: grep]`

### The record gate's runtime

`reference_record_gate_slow_on_state_md_long_line` attributes a ~300 s record-gate
runtime to a very long single line in `STATE.md`. **Two measured updates:**

1. **`STATE.md`'s longest line is now 2,965 characters** (file: 2,660 lines). The
   remembered "52k-char line" is no longer present. So the original cause has
   largely resolved itself, and the 300 s figure is probably stale.
2. **No `.planning`-level record-gate script exists** — `gsd-tools` has no `record`
   verb, and the `check-claims.py` / `check_record_corrections.py` scripts are
   **phase-scoped**, living under `.planning/phases/130|146|149|152/`. Phase 154
   authors no phase record that an existing gate would scan.

**Conclusion: the 300 s guidance does not apply to any gate this phase must run.**
Use **600 s** as a general timeout, sized by the actual slowest leg (the 235 s host
suite), not by the record-gate folklore. If a record gate is authored for this
phase, re-measure rather than inheriting 300 s. `[VERIFIED: awk on STATE.md; gsd-tools --help; find]`

---

## Runtime State Inventory

This is a comment-refactor phase, so the rename/refactor inventory applies. "State"
here means anything that survives a source edit and still references the old text.

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| **Stored data** | **None** — the sweep changes only comment text; no database, collection name, key or user_id is involved. Verified: the phase touches no `chip_database.json`, no ChromaDB/Mem0 keys, no EEPROM `rurp_configuration_t` field. | none |
| **Live service config** | **None.** No n8n workflow, Datadog service name, Tailscale ACL or Cloudflare tunnel references a source comment. | none |
| **OS-registered state** | **None.** No Task Scheduler / pm2 / systemd registration embeds comment text. | none |
| **Secrets / env vars** | **None changed.** Two env-var *names* are load-bearing for the SWEEP-07 controls and must be used, not renamed: `FIRESTARTER_SDP_SRC` (the sdp planting seam) and `FIRESTARTER_FW_ROOT` (`fw_presence.py`'s only seam, **read at import time** — must be set in the process environment, never monkeypatched). | none (use, do not rename) |
| **Build artifacts / installed packages** | **Four committed golden sidecars go stale** — see **F3**. `firestarter/tests/golden/{eprom_params_citations, protocol_branch_inventory, eprom_v131_trace_inventory, sdp_expected_inventory}.json` pin blob SHAs of 5 in-scope files. **This is a data migration, not a code edit, and it is the phase's one genuine stale-state item.** Also: `.pio/build/*` is gitignored and rebuilt; `firestarter.egg-info/` is gitignored (`.gitignore:6`) — neither needs action. | **regenerate all four sidecars in the firmware sweep commit** |
| **Line-number references (the phase's own subject)** | **9,989 citations** in `.planning/` target a candidate swept file; **6,928** shift. Deliberately left stale by D-01, closed by Phase 159 / REMAP-04. | manifest + marker (SWEEP-09/12); repair deferred |

**The canonical question — after every file is updated, what still holds the old
text?** Answer for this phase: the four golden sidecars (by content hash) and the
9,989 `.planning/` citations (by line number). Nothing else. The sidecars are
**not** covered by any current requirement; the citations are covered by
SWEEP-09/10/12 and REMAP-01…05.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO Core | SWEEP-05 byte-identity oracle | ✓ | 6.1.19 (`/usr/local/bin/pio`) | — |
| `toolchain-atmelavr` | `uno` build | ✓ | installed under `~/.platformio/packages/` | — |
| `avr-size` | ELF section table (optional) | ✓ | `~/.platformio/packages/toolchain-atmelavr/bin/avr-size` — **not on `PATH`** | use `python`-side ELF parse |
| `avr-gcc` on `PATH` | — | ✗ | — | not needed; pio invokes its own |
| CPython 3.11 | host gates (app CI is 3.11 only) | ✓ **via `uv`** | 3.11.16 | none — 3.12 masks CI defects |
| `python3.11` binary on `PATH` | — | ✗ | — | `uv venv --python 3.11` fetches it |
| `uv` | py3.11 provisioning + installs | ✓ | 0.12.5 | — |
| Writable `~/.cache/uv` | `uv` default | ✗ **`os error 13`** | — | **`export UV_CACHE_DIR=<writable>`** — required |
| `pip` inside the uv venv | — | ✗ | — | `uv pip install` |
| pytest / syrupy | both suites | ✓ (installed via `uv pip install -e '.[test]'`) | pytest 9.1.1, syrupy 6.0.0 | — |
| `pyserial`, `tqdm`, `requests` | host package imports | ✓ | via `.[test]` | — |
| `difflib` (stdlib) | remap tool | ✓ | stdlib | — |
| git | blob SHAs, diffs, porcelain assertions | ✓ | 2.55.0 | — |
| node | `gsd-tools.cjs` | ✓ | v22.23.2 (not on default `PATH`; `nvm` shim) | — |
| Sibling repo layout | every cross-repo gate | ✓ | `/workspaces/firestarter` + `/workspaces/firestarter_app` | `FIRESTARTER_FW_ROOT` env (import-time) |
| Knowledge graph | context | ⚠ **unusable** | 1,257 h old, **1,700 commits behind** | direct measurement (used throughout) |

**Missing dependencies with no fallback:** none. Everything the phase needs is
available.

**Missing dependencies with fallback:** `~/.cache/uv` is unwritable — redirect
`UV_CACHE_DIR`. `python3.11` is absent as a binary — `uv` fetches it. Neither
blocks.

**Not a dependency but a blocking precondition:** D-12's dirty `firestarter`
working tree. See F8 — no baseline measurement is meaningful until it is reset.

---

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md`:

- **Meta repo tracks only `.planning/` and `.claude/`.** Neither sub-repo is
  committed here. → D-11's three commits go to three different repos; the meta
  commit carries only `.planning/v1.33/`.
- **`firestarter/` is Arduino C++ (PlatformIO); `firestarter_app/` is the Python
  host CLI.** Read each sub-repo's own `CLAUDE.md`.
- **Serial protocol changes must be kept in sync** between
  `firestarter_app/firestarter/serial_comm.py` and `firestarter/src/firestarter.cpp`.
  → reinforces D-02: `CAP-0N` is shared wire vocabulary, and
  `firestarter.cpp:177-195` is the wire-layout record. No-touch.
- **Constants/flag bits are duplicated** between
  `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h`
  — "change both together". → `include/firestarter.h` has 2 hits and is
  gate-scanned by two modules; comment-only edits do not break parity, but the
  file is in the 8-path inventory.
- **Board differences:** Uno 512 B buffer, Leonardo 1024 B. → the byte-identity
  oracle is specified on `uno`; `uno328pb` and `leonardo` are free additional
  checks (§Validation Architecture).
- **Hardware calibration lives in Arduino EEPROM** (`rurp_configuration_t`). → not
  touched; no data migration (§Runtime State Inventory).
- Commands: `pio run -e uno`, `pio test`, `pip install -e .`, monitor at 250000
  baud.

No CLAUDE.md directive conflicts with any locked decision. The relevant `.claude/skills/`
entries are the GSD workflow skills plus `devtest-triage` / `devtest-rootcause`,
neither of which applies to a comment sweep.

---

## Security Domain

`security_enforcement` is not set in `.planning/config.json` → treated as enabled.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | no auth surface; comment text only |
| V3 Session Management | no | none |
| V4 Access Control | no | none |
| V5 Input Validation | **yes (tooling)** | `remap_citations.py` and the manifest generator parse untrusted-shaped text (10k citations, arbitrary paths). Validate: resolved paths must stay **inside** the repo root passed as the explicit argument; reject `..` traversal and absolute paths; never `open()` a path that escapes. Note 29 citations are literally `../firestarter/include/rurp_shield.h`. |
| V6 Cryptography | **yes (read-only)** | SHA-256 for artifact identity and SHA-1 for git blob identity are both **used as recorded identifiers, not as security primitives**. Do not hand-roll: `hashlib`, `sha256sum`, `git hash-object`. |
| V12 File Handling | **yes** | The tools write into `.planning/` across ~2,700 files. Write atomically (temp + rename) and never follow symlinks out of the tree. |
| V14 Configuration | no | none |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal via a cited path (`../firestarter/...`, absolute paths) | Tampering | Resolve, then assert the result is under the explicit repo-root argument; reject otherwise. Report, do not open. |
| **Gate silently disarmed by a comment** (F2 — proven, `0xA0`→`0x10` chip erase) | Tampering / Repudiation | Planted-violation controls (SWEEP-07); comment-stripped extraction |
| A checker that scans nothing and exits 0 (`_HERE` fail-open) | Repudiation | D-09: explicit repo root; exit non-zero on empty input |
| Remap silently corrupting 10k citations with no gate to catch it | Tampering | REMAP-02's round-trip oracle, made the write predicate (§R1) |
| Safety-relevant comment deleted (the AT28C no-payload invariant) | Denial of Service (of future correctness) | D-01 step 3's guard; `eeprom_28c.cpp` as its own plan (SWEEP-08) |

**The one genuine safety-adjacent concern in this phase** is not a classic
vulnerability: `eeprom_28c.cpp:176-202` holds the AT28C datasheet citation of
record and the D-10 statement that "the ONLY thing separating 'lock the chip' from
'prefix a byte write' is that NO DATA WRITE FOLLOWS this sequence". F2 shows the
gate protecting the adjacent table can be disarmed by editing exactly this block.
Highest comment value and highest gate risk coincide, as CONTEXT.md D-06 says —
and the measurement confirms the coincidence is worse than stated.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `firmware.elf` / `firmware.hex` as PlatformIO artifact names | `firestarter_<board>.elf/.hex` via `name_firmware.py`'s `env.Replace(PROGNAME=…)` | Phase 21 Plan 21-02 | Any oracle hard-coding `firmware.elf` silently measures nothing |
| "`~20` files under `firestarter_app/tests/` scan firmware source" | **8 paths**, `scan_paths.py::ALL_CROSS_REPO_PATHS` | Phase 123 Plan 08 | D-05. But see **F4** — the *firmware* repo has 30 more, uninventoried |
| `STATE.md` carries a ~52 k-char line (record gate needs 300 s) | Longest line is now **2,965** chars | since that note | The 300 s guidance is stale; size timeouts by measurement |
| `git rev-parse HEAD:` blob pins as an anti-drift device | still current, **4 sidecars, 5 files** | Phases 140/131 era | **F3** — makes comment edits gate-visible |

**Deprecated / outdated for this phase:**

- The writeup's "~646 hits / 167 files" → **635 hits / 160 files** on `beta`.
- The survey regex's `P\d{3}` and `REQ-` alternations → **0 matches**; dead.
- CONTEXT.md D-06's "`test_sdp_table_parity.py` … Negative control? **no**" → it
  **has** one, plus a purpose-built planting seam (§R3).
- `firestarter/src/primitives.cpp` → never merged; 53 citations point at a file
  that never existed (corroborates `reference_v116_primitives_layer_never_merged`).

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The survey regex I reconstructed is the same one that produced the recorded figures | Corpus Measurements | Low — 4 of 5 groups reproduce exactly; the 1-hit delta in `src`+`include` is the whole exposure |
| A2 | The `-g`-absent compile line holds for every env, not just `uno` | R5 | Low, and scoped — SWEEP-05 only names `uno`, which was measured directly. Re-check before extending the hash oracle to `leonardo`/`uno328pb` |
| A3 | Not all 22 non-stripping firmware gates are actually comment-sensitive | F4 | Medium — I classified by presence/absence of a stripper, not by reading each gate's patterns. The disposition pass is real work |
| A4 | Excluding `**/fixtures/**` is the right disambiguation rule | R2 | Low — verified to resolve 639 of 665, and every colliding alternate inspected was a planted/fake fixture |
| A5 | The 7 host + 6 firmware baseline failures are **all** caused by the dirty tree | F8 | Medium — established by mechanism (porcelain assertions, live-content re-parse) and by one direct check (`test_page_size_key_string_matches_constants_py` passes against clean `beta`), but not by a full clean-tree run. **A full clean-tree baseline is the first thing to measure after D-12.** |
| A6 | No regeneration tool exists for the four golden sidecars | F3 | Low — searched `tools/` and the gate sources; the gate's own message says "re-derive" |
| A7 | `firestarter_app/tools/*.py` files carry no blob-sha pin on firmware source | F3 | Low — grepped; only `test_consistency_check.py` matched, and it hashes `.bin` outputs |

Nothing in this document rests on training knowledge about the project. Every
project-specific claim was measured or read this session.

---

## Open Questions (RESOLVED)

> **All five were closed at plan time (2026-08-23) by orchestrator rulings A-H, recorded in
> `154-{01..12}-PLAN.md`.** Each question keeps its original text so the reasoning stays legible;
> the `**RESOLVED:**` line under each records what was actually decided and where it landed.

1. **Does SWEEP-07 authorise writing new test code?**
   - What we know: SWEEP-07 requires planted-violation controls; the house pattern
     is committed fixtures plus new test functions; there is no way to satisfy it
     without adding both.
   - What's unclear: the phase's stated boundary is "comment text only, plus new
     files under `.planning/v1.33/`".
   - Recommendation: the planner should state explicitly that SWEEP-07's controls
     are new files in `firestarter_app/tests/{,fixtures/}` and fold them into the
     app-repo commit (D-11). This is F6, and it is a wording gap, not a conflict.
   - **RESOLVED — Ruling A (plan 03).** Yes. SWEEP-07 is a settled requirement that mandates the
     controls, and a control is test infrastructure, not a behaviour change; CONTEXT.md's
     "comment text only" describes edits to *existing* source. Plan 03 carries the four fixtures
     and the five new legs, states the scope clarification explicitly so it does not read as
     creep, and the files fold into the single app-repo commit (D-11) made by plan 12.

2. **Regenerate the four golden sidecars, or exempt the five pinned files?**
   - What we know: 5 files, 30 of 615 hits (~5%). Regeneration is hand work with no
     tool; exemption is one line each.
   - What's unclear: whether `eprom_params.cpp:61` (a **named** SWEEP-01
     keep-example) may be exempted without weakening SWEEP-01.
   - Recommendation: **exempt the four `test/`- and `eprom.cpp`-side files;
     regenerate only `eprom_params_citations.json`** so the named keep-example is
     still delivered. Cheapest path that keeps SWEEP-01 intact. Operator-visible
     trade — worth surfacing.
   - **RESOLVED — Ruling B (plans 02 and 07).** Take the recommendation: regenerate only
     `eprom_params_citations.json`; exempt the other four pinned paths, each named with the
     sidecar pinning it. The planner then found the recommendation incomplete —
     `eprom_params.cpp` is pinned by **two** sidecars, since
     `firestarter/tests/golden/protocol_branch_inventory.json` also carries that path in
     `meta.blob_shas`. Plan 07 task 2 updates both; updating only the first would have left
     `test_protocol_branch_inventory.py::test_blob_shas_match_the_recorded_inventory` RED.

3. **Should `test_sdp_table_parity.py` be hardened, or only controlled?**
   - What we know: F2 proves it can be silently disarmed; the offset-preserving
     stripper already exists in-repo; the fix is ~2 lines at 4 call sites.
   - What's unclear: hardening is a behaviour change to a gate, which the phase
     excludes.
   - Recommendation: **plant the controls in this phase** (SWEEP-07 as written)
     and file the hardening as a follow-on, unless the planner judges a 2-line
     comment-strip a comment-adjacent change. Do not leave the finding unrecorded
     either way.
   - **RESOLVED — controlled, not hardened.** SWEEP-07 as written: plant the controls in this
     phase (plan 03 proves them RED before the sweep, plan 12 re-proves them RED after) and
     record the hardening as a follow-on. Hardening is a behaviour change to a gate, which the
     phase excludes; F2 is recorded rather than fixed here.

4. **F4's 22 gates — disposition or explicit deferral?**
   - What we know: 22 firmware-repo gates scan source with no comment stripping;
     none is in D-05's inventory.
   - What's unclear: how many are genuinely comment-sensitive (A3).
   - Recommendation: a one-line disposition each inside SWEEP-06, or a reasoned
     out-of-scope ruling. Silence is the one bad option.
   - **RESOLVED — Ruling D (plans 02 and 12).** SWEEP-06's text is **not** expanded; it stands as
     the 8 app-repo paths. The 22 firmware-repo gates are dispositioned one line each and
     recorded as a named exposure in `sweep-gate-dispositions.md`, not controlled — building 22
     planted controls is its own phase, filed as a follow-on. Silence was avoided.

5. **Does `doc/PROTOCOLS.md` stay out of scope?**
   - What we know: 2 provenance hits, outside the sweep's globs per D-05, read by
     `test_dispatch_mirror.py`.
   - Recommendation: keep it out (D-05), but record the 2 hits so the exclusion is
     visible rather than accidental.
   - **RESOLVED — stays out, recorded (plan 02).** `doc/PROTOCOLS.md` keeps its 2 hits and is
     listed as a named exclusion alongside `firestarter/lib` (0 hits) and
     `firestarter/tests/*.py` (20 hits across 7 files — outside CONTEXT.md's
     `firestarter/{src,include,test}` globs, a third exclusion the planner found).

---

## Reproduction Commands

```bash
# --- clean beta exports (both sub-repos verified HEAD == beta) --------------
git -C firestarter     rev-list --left-right --count HEAD...beta   # 0  0
git -C firestarter_app rev-list --left-right --count HEAD...beta   # 0  0
git -C firestarter     archive beta | tar -x -C <scratch>/firestarter
git -C firestarter_app archive beta | tar -x -C <scratch>/firestarter_app

# --- SWEEP-05 byte-identity oracle ----------------------------------------
cd firestarter
rm -rf .pio/build/uno && pio run -e uno
sha256sum .pio/build/uno/firestarter_uno.elf .pio/build/uno/firestarter_uno.hex
~/.platformio/packages/toolchain-atmelavr/bin/avr-size -A \
  .pio/build/uno/firestarter_uno.elf
pio run -e uno -v 2>&1 | grep 'eeprom_28c'      # confirm no -g
grep -rc '__LINE__\|__FILE__' src include        # 0

# --- corpus survey (regex per the writeup) --------------------------------
#   (//|/\*|^\s*\*|#)\s*(Task|Phase|Plan|P\d{3}|Req|REQ-|CAP-0|D-\d|WR-\d|LOOP-\d|\d{3}-CONTEXT)
#   per group: firestarter/{src,include,test,lib}; firestarter_app/{firestarter,tests,tools}

# --- citation census ------------------------------------------------------
grep -roE '#L[0-9]+(-L?[0-9]+)?' .planning --include=*.md | wc -l          # 427
grep -roE '[A-Za-z0-9_./-]+\.(cpp|c|h|py|ino)+:[0-9]+-[0-9]+' .planning \
     --include=*.md | wc -l                                                # 6030
grep -roE '[A-Za-z0-9_./-]+\.(cpp|c|h|py|ino)+:[0-9]+,[0-9]+' .planning \
     --include=*.md | wc -l                                                # 273

# --- blob-sha pins (F3) ---------------------------------------------------
git -C firestarter rev-parse beta:src/proms/eprom_params.cpp   # 5dffe841...
git -C firestarter show beta:src/proms/eprom_params.cpp \
  | grep -v 'D-05: fail closed' | git hash-object --stdin      # d0b5183e...
python3 -c "import json;print(json.load(open('firestarter/tests/golden/eprom_params_citations.json'))['meta']['blob_shas'])"

# --- host gates at py3.11 (F2 / SWEEP-07) --------------------------------
export UV_CACHE_DIR=<writable>
uv venv --python 3.11 <venv>
uv pip install --python <venv>/bin/python -e '.[test]'
cd firestarter_app
FIRESTARTER_FW_ROOT=/workspaces/firestarter FIRESTARTER_SDP_SRC=<fixture> \
  <venv>/bin/python -m pytest tests/test_sdp_table_parity.py -o addopts="" -q

# --- suite baselines (against the DIRTY tree; re-take after D-12) ---------
cd firestarter && pio test -e native                # 172/172 in 21.9 s
cd firestarter && pytest tests/ -q --no-header      # 317 passed, 6 failed, 12.2 s
cd firestarter_app && FIRESTARTER_FW_ROOT=../firestarter \
  pytest tests/ -o addopts="" -q                   # 1963 passed, 7 failed, 235 s
```

---

## Sources

### Primary (HIGH confidence — measured or read in this session)

- `pio run -e uno` × 5 build configurations; `pio run -e uno -v`; `avr-size -A`;
  `sha256sum` on `.elf`/`.hex` — the SWEEP-05 oracle
- `pio test -e native` — 172/172
- `pytest firestarter/tests/` — 317 passed / 6 failed
- `pytest firestarter_app/tests/` at CPython 3.11.16 — 1963 passed / 7 failed
- `pytest tests/test_sdp_table_parity.py` against 4 purpose-built fixtures,
  including the **silent-green** proof
- `test_dispatch_mirror.py` firmware leg against 2 purpose-built fixtures
- Source read in full: `firestarter_app/tests/scan_paths.py`,
  `tests/fw_presence.py`, `tests/test_sdp_table_parity.py`,
  `tests/test_dispatch_mirror.py`; partial: `tests/test_cap03_ack_layout_parity.py`,
  `tests/test_json_key_parity.py`, `firestarter/tests/test_eprom_params_citations.py`
- `firestarter/platformio.ini`, `name_firmware.py`, `zero_bootloader_reserve.py`
- `firestarter/tests/golden/*.json` + `git rev-parse beta:<path>` verification
- Citation extractor over 2,975 `.planning/` files; corpus survey over both clean
  `beta` exports
- `difflib` prototype: line map, range shrink, chained-map idempotency
- `.planning/`: `154-CONTEXT.md`, `REQUIREMENTS.md` §1 and §6, `ROADMAP.md`,
  the phase writeup todo, `/workspaces/CLAUDE.md`

### Secondary (MEDIUM confidence)

- Project memory references used as hypotheses and then **verified independently**:
  `reference_devcontainer_py312_masks_ci_py39` (confirmed — 3.11 needed),
  `reference_pytest_addopts_q_suppresses_count_line` (confirmed — `-o addopts=""`),
  `reference_firmware_renames_break_host_source_scanning_gates` (confirmed, and
  strengthened by F2), `reference_flash_path_record_sync_asserts_whole_repo_porcelain`
  (confirmed, and broadened to 9 modules by F7),
  `reference_v116_primitives_layer_never_merged` (corroborated by 53 dangling
  citations), `reference_record_gate_slow_on_state_md_long_line` (**contradicted** —
  longest line is now 2,965 chars)

### Tertiary (LOW confidence)

- None. No web search or Context7 lookup was needed or performed: every question
  in this phase is answerable against this repository, and was.
- The knowledge graph (`.planning/graphs/graph.json`) was checked and **rejected as
  input**: 1,257 h old, 1,700 commits behind, `stale: true`.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|------|-------|--------|
| Byte-identity oracle (R5) | **HIGH** | Directly measured across 5 build configurations; the immunity has a verified mechanism (`-g` absent, 0 `__LINE__`), not just an observation |
| Remap algorithm (R1) | **HIGH** | Prototyped and run; shrink and idempotency both demonstrated, including the failure mode |
| Citation extraction (R2) | **HIGH** | Independently reproduced the recorded figures within 0.6%; 3 subtree figures exact |
| Planted controls (R3) | **HIGH** | Both gates run against 6 fixtures; the silent-green result is direct evidence |
| Blob-sha pins (F3) | **HIGH** | Sidecar JSON read, SHAs verified against `beta`, hit counts measured, SHA-change demonstrated |
| Firmware-repo gate inventory (F4) | **MEDIUM** | Counts are exact; per-gate comment-sensitivity was **not** individually assessed (A3) |
| Suite baselines (F8) | **MEDIUM** | Numbers exact, but taken against the dirty tree; the clean-tree attribution rests on mechanism plus one direct check (A5) |
| Corpus measurements | **HIGH** | 4 of 5 groups reproduce exactly; D-04's 331 exact |
| R6 hazard confirmations | **HIGH** | `.planning/v1.33/` absence, `milestones/` non-involvement, and `STATE.md` line length all directly verified |

**Research date:** 2026-08-23
**Valid until:** 2026-09-22 (30 days — the corpus is a `beta`-tip snapshot; re-run
the survey and the citation census before execution if `beta` has moved). Note the
figures shift the moment D-12 precondition 1 is discharged, so **re-take every
baseline after the tree reset**, not before.
