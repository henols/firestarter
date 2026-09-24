# Phase 205: The pre-flights leave the firmware - Pattern Map

**Mapped:** 2026-09-22
**Files analyzed:** 14 file groups (1 genuinely new file candidate, 13 modified surfaces)
**Analogs found:** 13 / 14 (one bench-artifact group has a template, not a code analog)

**Census authority:** RESEARCH.md § "Measured Site Census — 25 in-source sites, not 21" and
§ "Open Questions — RESOLVED at plan time" are the file list. Where CONTEXT.md and RESEARCH.md
disagree (spans at `memory.cpp:467-533`, `flash_nor_unlock.cpp:73-77`, `firestarter.h:62-63`,
`flash_5v_page.cpp:69-74`, `json_parser.c:117-122`, `_drive_region_compare`'s line), RESEARCH wins.

**Search method:** `git grep` from inside each submodule (the devcontainer `grep` is ugrep and
honours `.gitignore`). Every analog path below was confirmed git-TRACKED with `git ls-files` run
inside the owning repository — no gitignored mirror paths appear in this document.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `firestarter_app/firestarter/cli_handlers.py` — `erase` command (option, docstring, exit code) | controller (Click) | request-response | same file's `blank` handler (`:1153-1187`) and `verify` handler (`:1120-1131`) | exact |
| `firestarter_app/firestarter/eprom_operations.py` — `erase_eprom` widened `bool`→verdict; `-b` plumb | service | request-response / streaming compare | same file's `check_eprom_blank` (`:2971-3059`) + `write_eprom`'s keyword-only param (`:2248-2259`) | exact |
| `firestarter_app/firestarter/write_blank_guard.py` — `requires_blank_check` re-key off `0x08` | utility (pure predicate) | transform | itself (Phase 203); sibling gates `flash4_erase_gate.py`, `jp5_gate.py`, `page_size_gate.py` | exact |
| `firestarter_app/firestarter/constants.py` — retire `FLAG_SKIP_BLANK_CHECK`, reserved-gap note | config | — | same file's retired-ordinal COMMAND ladder note (Phase 204) + `firestarter.h:53-64` | exact |
| `firestarter_fw/include/firestarter.h` — retire `0x08`, reserved-gap note, fix stale `:61-64` | config/header | — | `firestarter.h:53-64` ordinal-4 reserved record (Phase 204, same file) | exact |
| `firestarter_fw/src/proms/memory.cpp`, `include/memory_utils.h` — the sweep | service (AVR core) | streaming | Phase 204 commits `29daf42`, `305b2f4` on the same two files | exact |
| `firestarter_fw/src/proms/{eprom,flash_intel,flash_nor_unlock}.cpp` — call-site deletions | protocol handler | request-response | Phase 204 commit `5f66595` (five `configure_*` arms) | exact |
| `firestarter_fw/src/{firestarter.cpp,json_parser.c}` — emit deletion + negative-address fix | dispatcher / parser | request-response | `test/native/avr/test_read_timing/test_read_timing_params.cpp` (parse-level native precedent) | role-match |
| `firestarter_fw/tests/test_verify_survival_source_contract.py` — gains absence legs + 3 migrated legs | test (source-contract gate) | transform | itself (Phase 204 plan 03 extended it the same way) | exact |
| `firestarter_fw/tests/test_blank_check_region_source_contract.py` — RETIRED, 3 legs migrated | test | transform | Phase 204's create-then-extend of the survival gate | exact |
| `firestarter_fw/tests/golden/protocol_branch_inventory.json` + its gate | test (golden) | transform | Phase 204 commit `cb6b434` / `305b2f4` re-derive (8th); this is the 9th | exact |
| `firestarter_fw/test/native/avr/**` (8 suites, 12 lines) | test (Unity) | — | Phase 204's native re-keys in `test_val_eprom.cpp`, `test_val_nor_unlock.cpp` | exact |
| `/workspaces/tools/catalog/messages.toml` — annotate 0xB0 + `DBG_FLAG_SKIP_BLANK` 0x2E | config (catalog) | — | meta commit `694acce3` (204-04) | exact |
| Bench + flash/RAM artifacts (`205-BENCH-MATRIX.md`, FWBLANK-05 table) | doc/evidence | — | `204-BENCH-MATRIX.md`; `.planning/milestones/v1.33-artifacts/sweep-outcome-record.md` | template, not code |

---

## Pattern Assignments

### `firestarter_app/firestarter/cli_handlers.py` — `erase` gains a 0/1/2 verdict (D-01/D-02/D-03, OQ-1)

**Analog:** the `blank` handler in the same file (`:1153-1187`) — it already ships the exact
contract D-02 asks for, including the docstring sentence that states it.

**Handler shape to copy** (`cli_handlers.py:1153-1187`):

```python
@cli.command(name="blank")
@click.argument("eprom", shell_complete=_complete_eprom)
@click.option("--full", is_flag=True, help="Report every non-blank range, not just the first.")
@click.pass_obj
@map_typed_errors
def blank(app: AppContext, eprom: str, address: str | None, size: str | None,
          force: bool, full: bool) -> None:
    """Checks if an EPROM is blank.

    Exits 0 when blank, 1 when at least one byte is not blank, 2 on a
    transport, hardware, setup, or region failure. The three are distinct:
    a transport failure is not reported as a not-blank verdict, ...
    """
    eprom_data = resolve_chip(eprom, db=app.db)
    refusal = _region_refusal_exit_code(eprom=eprom, eprom_data=eprom_data,
                                        address=address, size=size)
    if refusal is not None:
        sys.exit(refusal)
    verdict = app.eprom_operator.check_eprom_blank(
        eprom, eprom_data, operation_flags=_build_op_flags(force=force),
        address_str=address, size_str=size, full=full,
    )
    sys.exit(verdict)
```

Three things to copy literally:
1. **The exit-contract paragraph is in the Click docstring**, which IS the `--help` text — so it is
   user-facing and must carry no GSD/planning provenance.
2. **`sys.exit(verdict)`** — no `0 if ok else 1` mapping layer. `check_eprom_blank` already returns
   0/1/2, so D-02 needs no translation.
3. **A pre-connect refusal returns an exit code before the port opens** (`_region_refusal_exit_code`
   → `sys.exit(refusal)`). This is the shape OQ-1's `erase -s … -b` refusal should take: refuse
   *before* the erase runs, one stated line, non-zero exit.

**Current `erase` site to change** (`cli_handlers.py:1191-1262`) — keep the decorator order
(`@click.pass_obj`, `@map_typed_errors` last), keep `-b` as `is_flag=True, default=False,
"blank_check"`, and note the tail that D-02 replaces:

```python
    ok = app.eprom_operator.erase_eprom(
        eprom, eprom_data,
        operation_flags=_build_op_flags(blank_check=blank_check, force=force),
        address_str=sector_address, pin1_hazard_acknowledged=True,
    )
    sys.exit(0 if ok else 1)
```

**Docstring sentences that become FALSE and must be rewritten in the same edit** (RESEARCH confirms
both): *"On protocol ``0x0D`` the post-erase check is not wired, so ``-b`` has no effect there"* —
D-01 makes the host check protocol-agnostic, which is a behaviour **gain**; and the `-s`/`-b`
combination now needs its own refusal sentence per OQ-1.

**`firestarter.cli_handlers` is in the mypy strict island** (`disallow_untyped_defs = true`). The
annotation style to copy is exactly the `blank` signature above: every parameter annotated,
`-> None` on the command function, `str | None` for optional strings.
**`firestarter.eprom_operations` is deliberately excluded** from that island.

**Snapshot discipline:** `tests/__snapshots__/test_characterization.ambr::test_help_erase` carries
this whole docstring plus the `-b` help line. Hand-edit with the diff shown; **never
`--snapshot-update`**.

---

### `firestarter_app/firestarter/eprom_operations.py` — the `-b` plumb and the widened `erase_eprom`

**Analog A — the keyword-only insertion, Phase 203's own precedent in this same file** (`:2248-2259`):

```python
def write_eprom(
    self, eprom_name: str, eprom_data_dict: dict, input_file_path: str,
    operation_flags: int = 0, address_str: str | None = None, pulse_us: int = 0,
    pin1_hazard_acknowledged: bool = False,
    *,
    suppress_verdict_line: bool = False,   # keyword-only; every existing caller unchanged
) -> bool:
```

Copy this shape for the post-`0x08` blank signal. It neutralises both CONTEXT-named hazards by
construction: `build_flags`' four **positional** production callers (its docstring at `:305-311`
warns about this) and `chip_test.py:3221`'s positional flag argument cannot be shifted by a
keyword-only parameter, and the ~40 positional bool test call sites of `write_eprom` stay
byte-identical.

**Analog B — the engine D-01 calls into** (`:2971-3059`), already returning D-02's contract:

```python
def check_eprom_blank(
    self, eprom_name: str, eprom_data_dict: dict, operation_flags: int = 0,
    address_str: str | None = None, size_str: str | None = None, full: bool = False,
) -> int:
```

`full=False` is first-mismatch mode — **D-03's terse behaviour is this existing default parameter,
not new code.** `_drive_region_compare` is at `:2544` (not CONTEXT's `:2230-2334`).

**Analog C — widening a `bool` return to a verdict int:** the `verify_eprom` → `sys.exit(verdict)`
pair (`cli_handlers.py:1122-1131`) is the executed precedent for a handler consuming an int rather
than a bool. `erase_eprom` is at `:2832-2863` and currently returns `bool`.

---

### `firestarter_app/firestarter/write_blank_guard.py` — re-key `requires_blank_check` off the wire bit

**Analog:** the module itself. D-04 changes **what it keys on**, not what it decides. Site
(`:166-184`):

```python
def requires_blank_check(
    programmer_data: Mapping[str, Any] | None, operation_flags: int
) -> bool:
    """..."""
    flags = effective_flags(programmer_data, operation_flags)
    if flags & FLAG_SKIP_BLANK_CHECK:      # <- the line D-04 re-keys
        return False
    if is_erase_exempt(programmer_data, operation_flags):
        return False
    return is_guarded_protocol(programmer_data)
```

RESEARCH's recommended shape: thread the signal as a **third keyword argument with a `True`
default**, which keeps the signature stable for every existing caller.

**Refusal-string pattern to mirror for D-03's new one-line post-erase failure** (`:170-214`):

```python
_REFUSAL_FORMAT = (
    "Refusing write to {chip_name}: not blank at 0x{address:06X}, v: 0x{value:02X}."
)

def refusal_text(chip_name: str, address: int, value: int) -> str:
    """...Built from `_REFUSAL_FORMAT` rather than assembled at the raise site,
    following `flash4_erase_gate.refusal_text`'s shape, so a test can assert the
    exact sentence instead of a substring of a log line. ... it carries NO remedy
    clause ... An operator who reads the way out at the refusal site can route
    around a correct refusal."""
    return _REFUSAL_FORMAT.format(chip_name=chip_name.upper(), address=address, value=value)
```

Note the module's own **two-refusal-styles** precedent (`_NEGATIVE_ADDRESS_REFUSAL_FORMAT` at
`:216-263`): an *input-validation* refusal MAY carry a cause clause; a *safety* refusal may not.
OQ-1's `-s` + `-b` refusal is input-validation, so it follows the second style and names the reason.

**Stale citations in this file that this phase must repair, not inherit** (RESEARCH measured them
already 3 lines stale after Phase 204, and this phase deletes the referents entirely): the
`GUARDED_PROTOCOL_IDS` docstring at `:58-65` cites `eprom.cpp:144-145`,
`flash_nor_unlock.cpp:104-105`, `flash_intel.cpp:94-95`. Rewrite to past tense. The module docstring
also states *"This guard is the whole safety net after Phase 205 removes the firmware's own
write-init pre-flight"* — that sentence becomes present-tense true here.

---

### `firestarter_fw/include/firestarter.h` + `firestarter_app/firestarter/constants.py` — the two ladders (D-05)

**Analog:** `firestarter.h:53-64`, Phase 204's executed reserved-ordinal record:

```c
// Ordinal 4 -- the standalone blank-check command -- retired in 3.1.0
// (Phase 204). The host side -- firestarter_app/firestarter/constants.py's
// COMMAND_BLANK_CHECK and its COMMAND_NAMES row -- was retired in the same
// commit pair. This ordinal must NEVER be reused for any new command, flag
// or reserved meaning: an already-shipped host still composes it, and
// reassigning the number would make that stale host silently drive a
// different operation.
// The region-scoped blank-check machinery itself (mem_util_blank_check,
// mem_util_blank_check_region) survives this retirement -- it is reached
// only from write-init and erase-end now, and leaves in Phase 205.   <-- :61-64, DELETE
```

Four elements to copy: **version retired in**, **phase**, **the named host counterpart**, and **the
never-reuse reason stated as a mechanism** (a shipped peer still composes it). The last sentence
(`:61-64`) is the stale one this phase must delete rather than inherit.

The `0x08` note goes at the gap in the control-flag ladder (`firestarter.h:157-167`, define at
`:161`). The host counterpart goes in the flag block of `constants.py` (`:124-136`):

```python
# Control Flags — Firmware sync: firestarter.h
# flags bitmask values sent in JSON commands.
FLAG_FORCE = 0x01
FLAG_CAN_ERASE = 0x02
FLAG_SKIP_ERASE = 0x04
FLAG_SKIP_BLANK_CHECK = 0x08   # <- leaves; a reserved-gap comment replaces it
FLAG_VPE_AS_VPP = 0x10
```

**Both ladders move in the SAME COMMIT PAIR** (`/workspaces/CLAUDE.md` § Cross-repo obligations).
Note the marker phrase `"retired in 3.1.0"` is asserted by
`test_verify_survival_source_contract.py::test_both_reserved_ordinal_gaps_carry_a_recorded_reason`
by **count**; adding a third occurrence means that leg's expected count moves.

---

### `firestarter_fw/src/proms/memory.cpp` + `include/memory_utils.h` — the sweep

**Analog:** Phase 204's three-commit sweep on these same files — `29daf42` (behaviour-bearing
collapse, alone), `5f66595` (five protocol handler arms + gates + golden + native), `305b2f4` (the
`#define`s last, paired with the host ladder).

**The commit-ordering rule to copy, from `204-03-PLAN.md`'s objective:**

> The three commits are ordered by what each one reddens, not by file type. The collapses redden
> nothing, so they go first and alone — they are the only edits in this phase that change behaviour
> rather than delete a reference... The two `#define`s go last, because a define cannot be deleted
> before its references... the last of those in a paired commit.

**The must-have truths shape from `204-03-PLAN.md` that 205's plans should mirror**, notably the
survivor fence and the gate-integrity prohibition:

```
- "`mem_util_blank_check`, ... `BLANK_CHECK_CHUNK_SIZE` all still exist and are still reached
   from write-init and erase-end; only their command surface is gone. They leave in Phase 205."
- "The golden was re-derived by the gate module's own extractor, never hand-edited, and was
   diffed field by field against the previous golden keyed on the site line — the truthiness
   gate alone was not accepted as proof."
- "The sweep lands as three commits, each of which leaves all four firmware CI legs green, so no
   bisect between them can land on a RED tree."
prohibitions:
- "A gate re-anchor re-points a gate; it never weakens one. An equality stays an equality, no leg
   is deleted to make a count fit, no assertion becomes a floor..."
- "No push to `beta` in any of the three repositories during this phase."
```

**205-specific correction the analog does not carry:** the deletion in `memory.cpp` is **two
non-contiguous spans** (`:422-445` and `:460-537`) with the surviving `mem_util_operation_end` and
its doc comment at `:447-458` between them. A single-range cut takes a survivor.

---

### `firestarter_fw/tests/test_verify_survival_source_contract.py` — the source-contract family idiom

**Analog:** itself. Phase 204 plan 02 created it; plan 03 extended it with absence legs — the exact
operation 205 performs (add `0x08`/blank-check absence legs, receive three migrated legs per OQ-2).

**Module header idiom** (`:1-118`) — every element is load-bearing and should be reproduced:
a phase/plan attribution line, a **`Requirements:` line**, a **`Defect class this closes:`**
paragraph explaining why a source scan and not a run, a numbered **`Coverage:`** list with one entry
per leg, an **`Environment seams:`** section naming every override and stating it binds at import
time, and the closing statement that the module is standalone stdlib-only pytest with **no
`conftest.py`** and no import of any other gate module.

**Path resolution — never the environment for the default** (`:114-147`):

```python
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_EPROM_REL = "src/proms/eprom.cpp"
_SCAN_EPROM = Path(os.environ.get("FIRESTARTER_VERIFY_SURVIVAL_SCAN_EPROM_SOURCE",
                                  str(_REPO_ROOT / _EPROM_REL)))
# The remaining targets have no override -- a stray environment value pointed at
# the eprom.cpp seam cannot make Coverage 2, 3, 9 or 10 vacuous.
_SCAN_MEMORY = _REPO_ROOT / _MEMORY_REL
```

**Concatenation-built needles, so the gate cannot match itself** (`:160-178`):

```python
_NEEDLE_CALL = "memory_verify_exec" + "ute"
_NEEDLE_RETIRED_BLANK = "CMD_BLANK" + "_CHECK"
_NEEDLE_RESERVED_MARKER = "retired in " + "3.1.0"
```
…paired with a `test_own_needles_do_not_appear_verbatim_in_this_module` leg. 205's new needles
(`FLAG_SKIP_BLANK` + `_CHECK`, `mem_util_blank` + `_check`) must be built the same way and added to
`_ALL_SELF_CHECK_NEEDLES`.

**Absence-leg shape to copy for FWBLANK-01/02/03/04** (`:400-420`):

```python
def test_no_protocol_handler_configures_a_retired_ordinal():
    """Coverage 9 (FWCMD-01) -- ... A whole-file scan, not a brace-matched one:
    this leg exists to catch a stray reference left in a comment exactly as
    loudly as one left in a case label."""
    hits = []
    for rel, path in _PROTOCOL_RELS:
        stripped = _read_stripped(path)
        for label, needle in ((... , _NEEDLE_RETIRED_VERIFY), (..., _NEEDLE_RETIRED_BLANK)):
            if needle in stripped:
                hits.append(f"{rel}: {label}")
    assert hits == [], ("found a retired ... identifier surviving ...\nGot:\n" + "\n".join(hits))
```

Note `assert hits == []` (not `len(hits) == 0`) and the failure message that **names the first
divergence** and prints it. Also note 204's own RED discipline, stated in this module's docstring:
*"These legs' RED was observed against the pre-deletion tree before plan 03's sweep landed — see
that plan's SUMMARY for the captured transcript."* 205 owes the same captured transcript.

**Anti-vacuity legs — the two that MUST migrate with the retired module (OQ-2)** (`:440-504`):

```python
def test_scan_targets_are_non_vacuous():
    """... every DEFAULT scan target (recomputed fresh from _REPO_ROOT -- the
    check_permitted_claims.py _HERE-resolves-to-the-wrong-directory landmine,
    closed here by construction) exists, is non-empty, resolves inside this
    repository, and its comment-stripped text is non-empty. A missing or empty
    scan target must FAIL, never silently pass ..."""
    for label, p in default_targets:
        assert p.is_file(), ...
        assert p.stat().st_size > 0, ...
        assert p.resolve().is_relative_to(_REPO_ROOT), ...

def test_this_module_cannot_be_silently_skipped():
    own_text = Path(__file__).read_text()
    skip_call = "pytest" + ".skip"
    skip_cond_marker = "mark" + "." + "ski" + "pif"
    dependency_skip_call = "importor" + "skip"
    assert skip_call not in own_text, ...
```

**The third migrating leg — the survivor fence** (`test_blank_check_region_source_contract.py:411`):

```python
def test_operation_end_is_defined_exactly_once_and_reads_both_members():
    """Coverage 6 -- plan 201-04's D-06 anchor: the operation-end resolution
    point ... is defined exactly once and its body reads both the region-end
    member and the device-size member, so the fail-closed clamp cannot be
    silently dropped while the function stays defined and apparently intact."""
    stripped = _read_stripped(_SCAN_MEMORY)
    def_matches = list(_OP_END_DEF_RE.finditer(stripped))
    assert len(def_matches) == 1, (...)
    body_span = _function_body_span(stripped, _OP_END_DEF_RE)   # brace-matched, never line proximity
    assert _OP_END_READS_REGION_END_RE.search(body_text), ...
    assert _OP_END_READS_MEM_SIZE_RE.search(body_text), ...
```

Carry `_strip_comments` (shape-preserving: a newline stays a newline, everything else becomes a
space, so line numbers survive), `_read_stripped`, `_function_body_span` and the three `_OP_END_*`
regexes across in the **same commit** that deletes the source module.

---

### `firestarter_fw/tests/golden/protocol_branch_inventory.json` — the 9th re-derive

**Analog:** the golden's own `meta.how_to_update`, executed by Phase 204 in `305b2f4`/`cb6b434`.
RESEARCH already executed this re-derive against the simulated sweep and verified positional
alignment: **0 mismatches across all 20 pairs**.

```bash
# Run from firestarter_fw/ with the SWEPT working tree in place, BEFORE staging.
python3 - <<'PY'
import json, pathlib, importlib.util
spec = importlib.util.spec_from_file_location("pbi", "tests/test_protocol_branch_inventory.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
g = json.load(open("tests/golden/protocol_branch_inventory.json"))
old  = [s for s in g["sites"] if s["line"] not in (52, 141)]
live = m._extract_predicates(pathlib.Path("src/proms/eprom.cpp").read_text())
assert len(old) == len(live)
for o, l in zip(old, live):
    assert (o["predicate"], tuple(o.get("keyed_on") or []), o["tier"]) == \
           (l["predicate"], tuple(l.get("keyed_on") or []), l["tier"]), (o, l)
PY
git hash-object src/proms/eprom.cpp   # -> meta.blob_shas["src/proms/eprom.cpp"]
```

Values: `total_sites` 22→20, `other_sites` 21→19, `protocol_keyed_sites` stays 1, pinned literal
`[67]`→`[64]`. **Positional matching is mandatory** — the two deleted sites share an identical
`(predicate, keyed_on, tier)` signature, exactly the dict collision `meta.recorded_by` warns about.
**The golden and `src/proms/eprom.cpp` must land in ONE commit** (204-03's stated key link: the gate
is legitimately RED between them, and the golden's own record names two prior breaches).

---

### `/workspaces/tools/catalog/messages.toml` — D-08's annotations

**Analog:** meta commit `694acce3` (204-04), verbatim shape — a `docs(...)` commit touching only the
catalog, **no codegen run, no sub-repo sync**:

```toml
[[debug.messages]]
# Orphaned as of 3.1.0: its only emit site was the eprom_verify() wrapper
# (LOG_DEBUG_ID_SUB(DBG_VERIFY_PROM)), retired along with the standalone
# CMD_VERIFY command surface in 3.1.0 (v1.41 phase 204). Nothing else in
# either repository emits this sub-id. KEPT, not retired (D-06) -- reusing
# the number would make a replayed capture or an older firmware's log
# stream silently misinterpreted, and retaining it costs nothing: this
# entry has no format-string bytes on the AVR side (LOG_DEBUG_ID_SUB is
# id-only). Not free for reuse.
id     = 0x08
name   = "DBG_VERIFY_PROM"
```

Copy: the comment sits **above** the `id =` line inside the `[[debug.messages]]` block; it names the
**retired emit site**, the **release**, the **decision id**, the **reuse hazard as a mechanism**, and
ends **"Not free for reuse."**

Also copy the commit body's proof paragraph: *"regenerating both the cpp header and the python
module from the amended catalog to a temporary path produces output byte-identical to what
firestarter_fw and firestarter_app already carry. The validator passes. Neither sub-repo was
touched, and `sync_to_subrepos.sh` was not run."*

**205's divergence, which the annotation must state:** `MSG_ERR_NOT_BLANK` (0xB0) is **not orphaned
on the host** — a post-205 host still *receives* it from pre-205 firmware (the D-07 skew). Its
comment records: firmware emit site retired in 3.1.0; host deliberately still renders it for
pre-3.1.0 firmware; id not free for reuse. `DBG_FLAG_SKIP_BLANK` (0x2E) takes the plain 204 shape.

---

### `firestarter_fw/test/native/avr/**` — 8 suites, 12 compile-breaking lines

**Analog:** Phase 204's native re-keys (`test_val_eprom.cpp`, `test_val_nor_unlock.cpp`,
`test_val_eeprom28c.cpp` in `5f66595`/`305b2f4`) — retired-surface tests were **migrated or
inverted**, not silently deleted, and each deletion removed its matching `RUN_TEST(...)` line.

RESEARCH's measured dispositions (use these, not a re-derivation): DELETE
`test_blank_check_resumes_across_chunks_and_restores_the_cursor` (`:484-525`) and
`test_erase_end_blank_check_scans_from_zero` (`:544-564`); **RE-KEY**
`test_write_init_accepts_blank_region_on_non_blank_part` (`:655-685`) to FWBLANK-01's positive proof;
**INVERT** `test_write_init_still_refuses_when_target_region_is_non_blank`. Remove `RUN_TEST` at
`:736`, `:737`, `:745`, `:746`. `test_read_timing_params.cpp:245` must be **re-keyed onto a
surviving flag, not dropped** — the leg proves `FIELD_MASK` does not saturate.

**Negative-address firmware fix (folded todo, own plan, own commit):** the ready-made home is
`test/native/avr/test_read_timing/test_read_timing_params.cpp`, which already drives
`parse_json("{\"cmd\":2,\"flags\":65536}", &h)` and asserts on the resulting handle. Per OQ-3, scope
the refusal to the **address field only** and assert the other six numeric fields are untouched.
That plan's `<verify>` must run `pio test -e native` **and** `pio test -e native_nodevtools`.

---

## Shared Patterns

### Commit shape for a dual-repo removal
**Source:** `204-03-PLAN.md` frontmatter + objective; firmware `29daf42`, `5f66595`, `305b2f4`,
`fa7603c`, `24e3fdf`.
**Apply to:** every removal plan in 205.
Order commits by **what each reddens**, not by file type. Behaviour-bearing edits go first and
alone. `#define`s go last. The two constant ladders land as a **commit pair**. Every commit leaves
all four firmware CI legs green so no bisect lands RED. Gate re-anchors and their goldens land in
the **same** commit as the source change that moves them.

### Gate-integrity prohibition
**Source:** `204-03-PLAN.md` prohibitions block.
**Apply to:** every plan that touches a gate or golden.
"A gate re-anchor re-points a gate; it never weakens one. An equality stays an equality, no leg is
deleted to make a count fit, no assertion becomes a floor, and the golden is re-derived by the gate's
own extractor rather than hand-edited."

### RED-seen-first discipline
**Source:** `tests/test_verify_survival_source_contract.py:21-24`.
**Apply to:** every new absence leg in 205.
"These legs' RED was observed against the pre-deletion tree before plan 03's sweep landed — see that
plan's SUMMARY for the captured transcript." A pre-authored gate leg can be unreachable; RED proves
nothing until it is *seen* to fail for the intended reason, and the transcript goes in the SUMMARY.

### Citation repair, never inheritance
**Source:** `/workspaces/CLAUDE.md`; firmware commits `fa7603c` and `24e3fdf` (204's two dedicated
citation-repair commits).
**Apply to:** RESEARCH sites 11, 12, 14, 16, 17, 18, 19, 20, 22, 23, 24, 25 and
`write_blank_guard.py:58-65`.
A `docs(...)` commit that repairs every `file:LINE` and symbol reference the sweep staled is an
**expected deliverable**, not optional cleanup — 204 shipped two of them.

### Reasoning lives at the site
**Source:** `/workspaces/CLAUDE.md` (the no-comments-in-source rule was **REMOVED** 2026-09-19);
`write_blank_guard.py`'s module docstring.
**Apply to:** D-05's two reserved-gap notes, D-01's host-check justification, and the rewritten
comments at RESEARCH sites 12, 17, 18. Per OQ-4 the rewrites must state honestly that
`OPERATION_IN_PROGRESS` is never set post-205 — a vestigial-but-harmless guard — rather than restate
a live-mechanism claim that has stopped being true.
**Exception:** never write GSD/planning provenance into Click docstrings — they are user-facing
`--help` text.

### Collection-cliff-driven commit grouping (host only)
**Source:** RESEARCH § Host app tree, measured.
**Apply to:** the `constants.py` sweep plan.
Deleting `constants.py:129` alone produces **65 collection errors** — four modules import the
constant at module level. The constant, its five production sites and `tests/fake_chip.py`'s import
must move **in one commit** or the suite cannot collect at all. Separately, the frozen
`dedup_fingerprint` re-key in `test_blast_radius_invariance.py` wants **its own commit**, per the
gate's own failure message.

### Measurement record template (FWBLANK-05)
**Source:** `.planning/milestones/v1.33-artifacts/sweep-outcome-record.md` and `156-after-figures.md`.
**Apply to:** the flash/RAM table.
`pio run -t clean` per env, then `pio run -e uno -e uno328pb -e leonardo`, grep `^Processing|^RAM:|^Flash:`,
and sha256 both `.elf` and `.hex` per target. Quote **both** Leonardo denominators (x/32768 reported,
x/28672 real). RESEARCH already measured baseline and delta (−518 B flash, −4 B RAM, identical on all
three targets) — the record must still quote a `pio run` on the **actual** post-phase tree.

### Bench evidence format
**Source:** `204-BENCH-MATRIX.md` and `204-BENCH-TRACER.md`.
**Apply to:** the D-06/D-07 bench plan. D-07's rider **extends** 204's matrix rather than replacing
it. 204's D-07 label discipline applies unchanged: "pre-205"/"post-205" are documented label
substitutions and the record must name the **commit sha** that played each role — the host cannot
read a firmware prerelease suffix, so the sha is the only witness. Each UV leg must record that it
ran on an **erasable proxy**, not UV silicon.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `firestarter_fw/PROTOCOLS.md:321` rewrite | doc | — | No prior phase rewrote a PROTOCOLS.md protocol-behaviour assertion; three clauses on one very long line change at once, and D-01 makes the third ("`erase --blank-check` is a documented no-op on this protocol") false. Follow the citation-repair pattern above and RESEARCH's § Firmware documentation table. |
| `205-SESSION-COST` figure for Phase 206 | doc/evidence | — | Partial analog only: `203-SESSION-COST.md` supplies the cited per-open medians (Uno-class 2.518 s, Leonardo-class 2.607 s). D-01 adds exactly one open, so 205's number is a **derivation over a cited measurement** — label it as such, and never blend the two board classes. |

---

## Metadata

**Analog search scope:** `/workspaces/.planning/phases/20{3,4}-*/`, `/workspaces/tools/catalog/`,
`firestarter_fw/{tests,test/native/avr,src,include}/`, `firestarter_app/{firestarter,tests}/`.
**Search tool:** `git grep` / `git log` / `git show` run inside each repository (the devcontainer
`grep` is ugrep and honours `.gitignore`).
**Tracked-source gate:** `git ls-files` confirmed every analog path inside its owning repository.
**Files scanned:** ~30 read (5 in full, the rest targeted, non-overlapping ranges).
**Pattern extraction date:** 2026-09-22
