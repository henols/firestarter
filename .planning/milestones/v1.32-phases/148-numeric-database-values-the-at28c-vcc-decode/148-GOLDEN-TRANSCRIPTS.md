# Phase 148 Plan 07 — Golden Field-Inventory Gate: Seen-to-Fail Transcripts (D-13)

Six legs proving `firestarter_app/tests/test_chip_database_field_inventory.py`
(the frozen schema inventory gate, TABLE-05/D-12, re-derived this plan for the
numeric mv/us migration under DATA-02/D-13) is still capable of failing before
being trusted green. Five planted violations (A-E), each driving the gate RED
for a named, correct reason, followed by one clean run on the real tree (F).

Precedent: Phase 140 Plan 03 shipped four RED / one GREEN for this same gate
(see `.planning/phases/140-parameter-table/140-03-SUMMARY.md` §"Planted
Violations"). This plan adds a fifth planted leg (Leg E) that Phase 140 did
not have — a key planted inside `tools/extra_chips.json`'s own record —
because RESEARCH F-1 made the supplement's contribution to the generator key
union load-bearing for the first time (the golden's `generator_scan_scope`
meta field documents this union).

**Seam mechanics.** `_DB_PATH` and `_GEN_PATH` (in
`tests/test_chip_database_field_inventory.py`) resolve from `os.environ` **at
import time**, so every planted violation below runs the pytest invocation as
a **child process** with the relevant environment variable set directly on
the command line — **never `monkeypatch`**, because `monkeypatch` only takes
effect inside the already-running test process, after the module-level
`_DB_PATH`/`_GEN_PATH` assignments have already executed; setting it via
`monkeypatch.setenv` inside a test body would be invisible to those
import-time-bound `Path` objects and would make the planted leg unreachable —
exactly the "gate that has only ever been seen to pass proves nothing" trap
this task exists to avoid.

`_EXTRA_CHIPS_PATH` is deliberately **not** environment-overridable by design
(see the module's "Generator scan scope" docstring section) — it always
resolves to the real `tools/extra_chips.json`, even while
`FIRESTARTER_BUILD_DB_SOURCE` redirects `_GEN_PATH` at a scratch copy of
`build_db.py` alone (Leg D has no sibling `extra_chips.json` next to the
scratch generator file, and still fails correctly on the planted key rather
than raising `FileNotFoundError`). This is why Leg E, which targets
`_EXTRA_CHIPS_PATH` specifically, has no env seam at all: it must mutate the
real `tools/extra_chips.json` in place, observe RED, then restore the file
byte-exact — done **last, immediately before Leg F**, so a failed restore
cannot contaminate any other leg's baseline.

Every leg besides E plants into a `mktemp -d` scratch directory **outside
both repositories**, and that directory is `rm -rf`'d immediately after the
run. `git diff --quiet` in `firestarter_app` was confirmed clean before,
between, and after every leg (Leg E's own restore step is verified
separately below).

Working directory for every command below: `/workspaces/firestarter_app`.

---

## Leg A — a new field on ONE chip (`FIRESTARTER_CHIP_DB_JSON`)

**Plant:** add a single new key (`programming.foo`) to exactly one chip in a
mutated copy of `chip_database.json`.

Command:
```
T=$(mktemp -d)
python3 -c "import json,sys; db=json.load(open('firestarter/data/chip_database.json')); db[sorted(db)[0]][0]['programming']['foo']=1; json.dump(db, open(sys.argv[1],'w'))" "$T/db.json"
FIRESTARTER_CHIP_DB_JSON="$T/db.json" python3 -m pytest tests/test_chip_database_field_inventory.py -o addopts="" -v
rm -rf "$T"
```

Verbatim output:
```
============================= test session starts ==============================
platform linux -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python3
cachedir: .pytest_cache
rootdir: /workspaces/firestarter_app
configfile: pyproject.toml
plugins: syrupy-5.5.3, cov-7.1.0, anyio-4.14.2
collecting ... collected 8 items

tests/test_chip_database_field_inventory.py::test_top_level_field_inventory_matches PASSED [ 12%]
tests/test_chip_database_field_inventory.py::test_programming_field_inventory_matches FAILED [ 25%]
tests/test_chip_database_field_inventory.py::test_electrical_field_inventory_matches PASSED [ 37%]
tests/test_chip_database_field_inventory.py::test_27c_protocol_chip_counts_match PASSED [ 50%]
tests/test_chip_database_field_inventory.py::test_inventory_is_non_vacuous PASSED [ 62%]
tests/test_chip_database_field_inventory.py::test_generator_emits_no_key_outside_the_frozen_inventory PASSED [ 75%]
tests/test_chip_database_field_inventory.py::test_default_targets_resolve_inside_this_repository PASSED [ 87%]
tests/test_chip_database_field_inventory.py::test_this_module_is_collected_and_never_skipped PASSED [100%]

=================================== FAILURES ===================================
___________________ test_programming_field_inventory_matches ___________________

    def test_programming_field_inventory_matches() -> None:
        golden = _load_golden()
        live = _walk(_load_db()).programming
        recorded = golden["levels"]["programming"]
>       assert dict(live) == recorded, (
            "chip_database.json programming-level field inventory diverged "
            f"from the frozen golden -- "
            f"{_describe_counter_diff(recorded, dict(live))}"
        )
E       AssertionError: chip_database.json programming-level field inventory diverged from the frozen golden -- added={'foo': 1}
E       assert {'algorithm':...aw': 744, ...} == {'algorithm':...us': 746, ...}
E
E         Omitting 8 identical items, use -vv to show
E         Left contains 1 more item:
E         {'foo': 1}
E
E         Full diff:
E           {...
E
E         ...Full output truncated (11 lines hidden), use '-vv' to show

tests/test_chip_database_field_inventory.py:308: AssertionError
=========================== short test summary info ============================
FAILED tests/test_chip_database_field_inventory.py::test_programming_field_inventory_matches
========================= 1 failed, 7 passed in 0.06s ==========================
```

**Exit code:** 1 (`RUN_A_EXIT=1`).

**Which test, and why:** `test_programming_field_inventory_matches` (test 2)
— the numbered test whose level (`programming`) the planted key was added
under. RED for the right reason: `added={'foo': 1}`, exactly naming the
planted key and its occurrence count.

---

## Leg B — a count change with NO new name (`FIRESTARTER_CHIP_DB_JSON`)

**Plant:** delete the first manufacturer's first chip entirely (a count
change, zero new field names) from a mutated copy of `chip_database.json`.

Command:
```
T=$(mktemp -d)
python3 -c "import json,sys; db=json.load(open('firestarter/data/chip_database.json')); k=sorted(db)[0]; db[k]=db[k][1:]; json.dump(db, open(sys.argv[1],'w'))" "$T/db.json"
FIRESTARTER_CHIP_DB_JSON="$T/db.json" python3 -m pytest tests/test_chip_database_field_inventory.py -o addopts="" -v
rm -rf "$T"
```

Verbatim output:
```
============================= test session starts ==============================
platform linux -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python3
cachedir: .pytest_cache
rootdir: /workspaces/firestarter_app
configfile: pyproject.toml
plugins: syrupy-5.5.3, cov-7.1.0, anyio-4.14.2
collecting ... collected 8 items

tests/test_chip_database_field_inventory.py::test_top_level_field_inventory_matches FAILED [ 12%]
tests/test_chip_database_field_inventory.py::test_programming_field_inventory_matches FAILED [ 25%]
tests/test_chip_database_field_inventory.py::test_electrical_field_inventory_matches FAILED [ 37%]
tests/test_chip_database_field_inventory.py::test_27c_protocol_chip_counts_match FAILED [ 50%]
tests/test_chip_database_field_inventory.py::test_inventory_is_non_vacuous FAILED [ 62%]
tests/test_chip_database_field_inventory.py::test_generator_emits_no_key_outside_the_frozen_inventory PASSED [ 75%]
tests/test_chip_database_field_inventory.py::test_default_targets_resolve_inside_this_repository PASSED [ 87%]
tests/test_chip_database_field_inventory.py::test_this_module_is_collected_and_never_skipped PASSED [100%]

=================================== FAILURES ===================================
____________________ test_top_level_field_inventory_matches ____________________
E       AssertionError: chip_database.json top-level field inventory diverged from the frozen golden -- count_changed={'electrical': {'recorded': 746, 'live': 745}, 'part_number': {'recorded': 746, 'live': 745}, 'pinout': {'recorded': 746, 'live': 745}, 'programming': {'recorded': 746, 'live': 745}, 'support_status': {'recorded': 746, 'live': 745}}

___________________ test_programming_field_inventory_matches ___________________
E       AssertionError: chip_database.json programming-level field inventory diverged from the frozen golden -- count_changed={'algorithm': {'recorded': 746, 'live': 745}, 'chip_id_check': {'recorded': 746, 'live': 745}, 'chip_id_value': {'recorded': 746, 'live': 745}, 'infoic_page_size_raw': {'recorded': 744, 'live': 743}, 'protect_off_before': {'recorded': 744, 'live': 743}, 'protect_on_after': {'recorded': 744, 'live': 743}, 'pulse_duration_us': {'recorded': 746, 'live': 745}}

___________________ test_electrical_field_inventory_matches ____________________
E       AssertionError: chip_database.json electrical-level field inventory diverged from the frozen golden -- count_changed={'pin_count': {'recorded': 746, 'live': 745}, 'size_bytes': {'recorded': 746, 'live': 745}, 'type': {'recorded': 746, 'live': 745}, 'vcc_mv': {'recorded': 746, 'live': 745}, 'vdd_mv': {'recorded': 746, 'live': 745}, 'vpp_mv': {'recorded': 746, 'live': 745}}

_____________________ test_27c_protocol_chip_counts_match ______________________
E       AssertionError: 27C protocol chip counts (programming.algorithm in {7, 8, 11}) diverged from the frozen golden -- recorded={7: 170, 8: 127, 11: 32} live={7: 170, 8: 126, 11: 32}. A count change invalidates every per-protocol figure this milestone cites, including F-140-04's pulse distribution and the D-09 citation scope clauses.

________________________ test_inventory_is_non_vacuous _________________________
E       AssertionError: non-vacuous guard: expected 746 chips (frozen) and > 0, scanned 745
E       assert (745 == 746)

=========================== short test summary info ============================
FAILED tests/test_chip_database_field_inventory.py::test_top_level_field_inventory_matches
FAILED tests/test_chip_database_field_inventory.py::test_programming_field_inventory_matches
FAILED tests/test_chip_database_field_inventory.py::test_electrical_field_inventory_matches
FAILED tests/test_chip_database_field_inventory.py::test_27c_protocol_chip_counts_match
FAILED tests/test_chip_database_field_inventory.py::test_inventory_is_non_vacuous
========================= 5 failed, 3 passed in 0.08s ==========================
```

**Exit code:** 1 (`RUN_B_EXIT=1`).

**Which tests, and why:** tests 1 (`test_top_level_field_inventory_matches`),
2 (`test_programming_field_inventory_matches`), 3
(`test_electrical_field_inventory_matches`), and 5
(`test_inventory_is_non_vacuous`) — the plan's stated minimum — plus test 4
(`test_27c_protocol_chip_counts_match`) as a bonus, since the deleted chip
happened to carry `algorithm: 8`, dropping that protocol's count 127→126.
**Every single failure is a `count_changed` entry — zero `added`/`removed`
key names appear anywhere in the output.** This is the explicit, verbatim
proof that a names-only gate would have passed this exact planted violation,
and that pinning per-key occurrence counts (not just names) is necessary.

---

## Leg C — a vacuous `{}` target (`FIRESTARTER_CHIP_DB_JSON`)

**Plant:** point `FIRESTARTER_CHIP_DB_JSON` at an empty JSON object.

Command:
```
T=$(mktemp -d)
printf '{}' > "$T/db.json"
FIRESTARTER_CHIP_DB_JSON="$T/db.json" python3 -m pytest tests/test_chip_database_field_inventory.py -o addopts="" -v
rm -rf "$T"
```

Verbatim output:
```
============================= test session starts ==============================
platform linux -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python3
cachedir: .pytest_cache
rootdir: /workspaces/firestarter_app
configfile: pyproject.toml
plugins: syrupy-5.5.3, cov-7.1.0, anyio-4.14.2
collecting ... collected 8 items

tests/test_chip_database_field_inventory.py::test_top_level_field_inventory_matches FAILED [ 12%]
tests/test_chip_database_field_inventory.py::test_programming_field_inventory_matches FAILED [ 25%]
tests/test_chip_database_field_inventory.py::test_electrical_field_inventory_matches FAILED [ 37%]
tests/test_chip_database_field_inventory.py::test_27c_protocol_chip_counts_match FAILED [ 50%]
tests/test_chip_database_field_inventory.py::test_inventory_is_non_vacuous FAILED [ 62%]
tests/test_chip_database_field_inventory.py::test_generator_emits_no_key_outside_the_frozen_inventory PASSED [ 75%]
tests/test_chip_database_field_inventory.py::test_default_targets_resolve_inside_this_repository PASSED [ 87%]
tests/test_chip_database_field_inventory.py::test_this_module_is_collected_and_never_skipped PASSED [100%]

=================================== FAILURES ===================================
____________________ test_top_level_field_inventory_matches ____________________
E       AssertionError: chip_database.json top-level field inventory diverged from the frozen golden -- removed={'datasheet': 2, 'electrical': 746, 'part_number': 746, 'pinout': 746, 'programming': 746, 'provenance': 2, 'source': 2, 'support_status': 746, 'unsupported_reason': 10, 'verification_note': 2, 'verification_status': 2}

___________________ test_programming_field_inventory_matches ___________________
E       AssertionError: chip_database.json programming-level field inventory diverged from the frozen golden -- removed={'algorithm': 746, 'chip_id_check': 746, 'chip_id_value': 746, 'infoic_page_size_raw': 744, 'page_size': 2, 'protect_off_before': 744, 'protect_on_after': 744, 'pulse_duration_us': 746}

___________________ test_electrical_field_inventory_matches ____________________
E       AssertionError: chip_database.json electrical-level field inventory diverged from the frozen golden -- removed={'pin_count': 746, 'size_bytes': 746, 'type': 746, 'vcc_mv': 746, 'vdd_mv': 746, 'vpp_mv': 746}

_____________________ test_27c_protocol_chip_counts_match ______________________
E       AssertionError: 27C protocol chip counts (programming.algorithm in {7, 8, 11}) diverged from the frozen golden -- recorded={7: 170, 8: 127, 11: 32} live={7: 0, 8: 0, 11: 0}. A count change invalidates every per-protocol figure this milestone cites, including F-140-04's pulse distribution and the D-09 citation scope clauses.

________________________ test_inventory_is_non_vacuous _________________________
    def test_inventory_is_non_vacuous() -> None:
        golden = _load_golden()
        db = _load_db()
>       assert isinstance(db, dict) and len(db) > 0, (
            f"non-vacuous guard: chip_database.json must load as a non-empty "
            f"dict, got {type(db).__name__!r}"
        )
E       AssertionError: non-vacuous guard: chip_database.json must load as a non-empty dict, got 'dict'
E       assert (True and 0 > 0)
E        +  where True = isinstance({}, dict)
E        +  and   0 = len({})

tests/test_chip_database_field_inventory.py:350: AssertionError
=========================== short test summary info ============================
FAILED tests/test_chip_database_field_inventory.py::test_top_level_field_inventory_matches
FAILED tests/test_chip_database_field_inventory.py::test_programming_field_inventory_matches
FAILED tests/test_chip_database_field_inventory.py::test_electrical_field_inventory_matches
FAILED tests/test_chip_database_field_inventory.py::test_27c_protocol_chip_counts_match
FAILED tests/test_chip_database_field_inventory.py::test_inventory_is_non_vacuous
========================= 5 failed, 3 passed in 0.06s ==========================
```

**Exit code:** 1 (`RUN_C_EXIT=1`).

**Which test, and why:** `test_inventory_is_non_vacuous` (test 5) is the
canonical failure for this leg — it fails explicitly on the empty-dict guard
(`got 0 chips`), never a silent pass; the other four DB-reading tests fail as
a direct, correctly-attributed consequence of the same empty target (every
key `removed`, matching the totality of an empty database), not an
import/path/decode error.

---

## Leg D — a new key in the GENERATOR only (`FIRESTARTER_BUILD_DB_SOURCE`)

**Plant:** insert a new `"foo": 1,` line into `tools/build_db.py`'s
`chip_entry = {...}` dict literal, immediately before the `"support_status"`
key, in a scratch copy. `tools/extra_chips.json` is **not** copied alongside
the scratch `build_db.py` — deliberately, to prove `_EXTRA_CHIPS_PATH`'s
real-tree-only resolution does not turn this into an unreachable-leg error.

Command:
```
T=$(mktemp -d)
sed 's/^\( *\)"support_status": _support_status,/\1"foo": 1,\n\1"support_status": _support_status,/' tools/build_db.py > "$T/build_db.py"
FIRESTARTER_BUILD_DB_SOURCE="$T/build_db.py" python3 -m pytest tests/test_chip_database_field_inventory.py -o addopts="" -v
rm -rf "$T"
```

`diff` confirmed exactly one line inserted:
```
724a725
>                     "foo": 1,
```

Verbatim output:
```
============================= test session starts ==============================
platform linux -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python3
cachedir: .pytest_cache
rootdir: /workspaces/firestarter_app
configfile: pyproject.toml
plugins: syrupy-5.5.3, cov-7.1.0, anyio-4.14.2
collecting ... collected 8 items

tests/test_chip_database_field_inventory.py::test_top_level_field_inventory_matches PASSED [ 12%]
tests/test_chip_database_field_inventory.py::test_programming_field_inventory_matches PASSED [ 25%]
tests/test_chip_database_field_inventory.py::test_electrical_field_inventory_matches PASSED [ 37%]
tests/test_chip_database_field_inventory.py::test_27c_protocol_chip_counts_match PASSED [ 50%]
tests/test_chip_database_field_inventory.py::test_inventory_is_non_vacuous PASSED [ 62%]
tests/test_chip_database_field_inventory.py::test_generator_emits_no_key_outside_the_frozen_inventory FAILED [ 75%]
tests/test_chip_database_field_inventory.py::test_default_targets_resolve_inside_this_repository PASSED [ 87%]
tests/test_chip_database_field_inventory.py::test_this_module_is_collected_and_never_skipped PASSED [100%]

=================================== FAILURES ===================================
___________ test_generator_emits_no_key_outside_the_frozen_inventory ___________

    def test_generator_emits_no_key_outside_the_frozen_inventory() -> None:
        golden = _load_golden()
        live = _generator_chip_entry_keys(_GEN_PATH.read_text(encoding="utf-8"))
        live |= _extra_chips_entry_keys(_EXTRA_CHIPS_PATH)
        recorded = set(golden["generator_emitted_chip_entry_keys"])
>       assert live == recorded, (
            "the generator's emitted chip-entry key set diverged from the "
            f"frozen golden -- added={sorted(live - recorded)} "
            f"removed={sorted(recorded - live)}. chip_database.json is "
            "generated, so a new key here becomes a new database field the "
            "moment anyone regenerates it."
        )
E       AssertionError: the generator's emitted chip-entry key set diverged from the frozen golden -- added=['foo'] removed=[]. chip_database.json is generated, so a new key here becomes a new database field the moment anyone regenerates it.
E       assert {'algorithm',...', 'foo', ...} == {'algorithm',...ize_raw', ...}
E
E         Extra items in the left set:
E         'foo'
E
E         Full diff:
E           {
E               'algorithm',...
E
E         ...Full output truncated (26 lines hidden), use '-vv' to show

tests/test_chip_database_field_inventory.py:388: AssertionError
=========================== short test summary info ============================
FAILED tests/test_chip_database_field_inventory.py::test_generator_emits_no_key_outside_the_frozen_inventory
========================= 1 failed, 7 passed in 0.07s ==========================
```

**Exit code:** 1 (`RUN_D_EXIT=1`).

**Which test, and why:** `test_generator_emits_no_key_outside_the_frozen_inventory`
(test 6) — the numbered test whose ast-walk over `build_db.py`'s `chip_entry`
construction reached the planted key. RED for the right reason:
`added=['foo']`, exactly naming the planted generator-only key. No other test
was disturbed, confirming the plant is isolated to the `chip_entry`
construction path and did not accidentally also perturb the DB-reading
tests.

---

## Leg E — a new key inside an `extra_chips.json` record (Phase-148-specific)

**Plant:** `_EXTRA_CHIPS_PATH` is deliberately not environment-overridable
(see "Seam mechanics" above), so this leg mutates the **real**
`tools/extra_chips.json` in place — adding `"foo": 1` to the first TI
record's `electrical` object — runs the gate, observes RED, then restores the
file byte-exact from a pre-plant backup. This is the plan's fifth,
Phase-148-specific leg: it exercises the union path (`_generator_chip_entry_keys`
unioned with `_extra_chips_entry_keys`) that RESEARCH F-1 made load-bearing —
Phase 140 Plan 03's four legs never planted into `extra_chips.json` itself.
Run **last, immediately before Leg F**, per the plan's explicit ordering
requirement, so a failed restore cannot contaminate any other leg.

Commands:
```
cp tools/extra_chips.json /tmp/extra_chips_backup.json
python3 -c "
import json
p = 'tools/extra_chips.json'
d = json.load(open(p))
d['TEXAS INSTRUMENTS'][0]['electrical']['foo'] = 1
json.dump(d, open(p, 'w'), indent=2)
"
python3 -m pytest tests/test_chip_database_field_inventory.py -o addopts="" -v
```

Verbatim output:
```
============================= test session starts ==============================
platform linux -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python3
cachedir: .pytest_cache
rootdir: /workspaces/firestarter_app
configfile: pyproject.toml
plugins: syrupy-5.5.3, cov-7.1.0, anyio-4.14.2
collecting ... collected 8 items

tests/test_chip_database_field_inventory.py::test_top_level_field_inventory_matches PASSED [ 12%]
tests/test_chip_database_field_inventory.py::test_programming_field_inventory_matches PASSED [ 25%]
tests/test_chip_database_field_inventory.py::test_electrical_field_inventory_matches PASSED [ 37%]
tests/test_chip_database_field_inventory.py::test_27c_protocol_chip_counts_match PASSED [ 50%]
tests/test_chip_database_field_inventory.py::test_inventory_is_non_vacuous PASSED [ 62%]
tests/test_chip_database_field_inventory.py::test_generator_emits_no_key_outside_the_frozen_inventory FAILED [ 75%]
tests/test_chip_database_field_inventory.py::test_default_targets_resolve_inside_this_repository PASSED [ 87%]
tests/test_chip_database_field_inventory.py::test_this_module_is_collected_and_never_skipped PASSED [100%]

=================================== FAILURES ===================================
___________ test_generator_emits_no_key_outside_the_frozen_inventory ___________

    def test_generator_emits_no_key_outside_the_frozen_inventory() -> None:
        golden = _load_golden()
        live = _generator_chip_entry_keys(_GEN_PATH.read_text(encoding="utf-8"))
        live |= _extra_chips_entry_keys(_EXTRA_CHIPS_PATH)
        recorded = set(golden["generator_emitted_chip_entry_keys"])
>       assert live == recorded, (
            "the generator's emitted chip-entry key set diverged from the "
            f"frozen golden -- added={sorted(live - recorded)} "
            f"removed={sorted(recorded - live)}. chip_database.json is "
            "generated, so a new key here becomes a new database field the "
            "moment anyone regenerates it."
        )
E       AssertionError: the generator's emitted chip-entry key set diverged from the frozen golden -- added=['foo'] removed=[]. chip_database.json is generated, so a new key here becomes a new database field the moment anyone regenerates it.
E       assert {'algorithm',...', 'foo', ...} == {'algorithm',...ize_raw', ...}
E
E         Extra items in the left set:
E         'foo'
E
E         Full diff:
E           {
E               'algorithm',...
E
E         ...Full output truncated (26 lines hidden), use '-vv' to show

tests/test_chip_database_field_inventory.py:388: AssertionError
=========================== short test summary info ============================
FAILED tests/test_chip_database_field_inventory.py::test_generator_emits_no_key_outside_the_frozen_inventory
========================= 1 failed, 7 passed in 0.07s ==========================
```

**Exit code:** 1 (`RUN_E_EXIT=1`).

**Which test, and why:** `test_generator_emits_no_key_outside_the_frozen_inventory`
(test 6) — same numbered test as Leg D, but reached via the **other** half of
the union (`_extra_chips_entry_keys`, not `_generator_chip_entry_keys`),
proving `tools/extra_chips.json`'s contribution to the generator key union is
independently load-bearing: a key planted only in the supplement (never in
`build_db.py`'s `chip_entry` construction) is still caught. RED for the
right reason: `added=['foo']`.

**Restore step (run immediately after the RED above, before Leg F):**
```
cp /tmp/extra_chips_backup.json tools/extra_chips.json
git diff --quiet tools/extra_chips.json && echo "extra_chips.json BYTE-RESTORED"
git status --porcelain tools/extra_chips.json
```
Output:
```
extra_chips.json BYTE-RESTORED
```
(`git status --porcelain tools/extra_chips.json` printed nothing — the file
is provably byte-identical to its pre-plant committed state.)

---

## Leg F — the real tree, no env seams set (expected: all 8 pass)

Command:
```
python3 -m pytest tests/test_chip_database_field_inventory.py -o addopts="" -v
git status --porcelain
```

Verbatim output:
```
============================= test session starts ==============================
platform linux -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python3
cachedir: .pytest_cache
rootdir: /workspaces/firestarter_app
configfile: pyproject.toml
plugins: syrupy-5.5.3, cov-7.1.0, anyio-4.14.2
collecting ... collected 8 items

tests/test_chip_database_field_inventory.py::test_top_level_field_inventory_matches PASSED [ 12%]
tests/test_chip_database_field_inventory.py::test_programming_field_inventory_matches PASSED [ 25%]
tests/test_chip_database_field_inventory.py::test_electrical_field_inventory_matches PASSED [ 37%]
tests/test_chip_database_field_inventory.py::test_27c_protocol_chip_counts_match PASSED [ 50%]
tests/test_chip_database_field_inventory.py::test_inventory_is_non_vacuous PASSED [ 62%]
tests/test_chip_database_field_inventory.py::test_generator_emits_no_key_outside_the_frozen_inventory PASSED [ 75%]
tests/test_chip_database_field_inventory.py::test_default_targets_resolve_inside_this_repository PASSED [ 87%]
tests/test_chip_database_field_inventory.py::test_this_module_is_collected_and_never_skipped PASSED [100%]

============================== 8 passed in 0.05s ===============================
```

`git status --porcelain` at this point showed only pre-existing,
plan-unrelated untracked files that were already present before this plan
started (`.planning/config.json`, `SECURITY.md`, four `datasheets/*.pdf`
files, `write_test_port.sh`) — none of this plan's own files appeared, since
Task 1's golden re-derivation was already committed before these legs ran.

`RUN_F_EXIT=0` — GREEN, **8 passed**.

---

## Post-run integrity check

```
git diff --quiet -- firestarter/data/chip_database.json tools/build_db.py tools/extra_chips.json && echo DB_AND_GENERATOR_AND_SUPPLEMENT_BYTE_UNCHANGED
git diff --quiet && echo TREE_CLEAN
git status --porcelain tools/extra_chips.json
```

All three passed: the database, the generator, and the supplement are all
byte-unchanged after all six legs; the working tree overall is clean; and
`tools/extra_chips.json`'s porcelain status is empty (no diff, no residue).

## Summary of the six legs

| Leg | Plant | Seam | Test(s) RED | Exit |
|---|---|---|---|---|
| A | new field on one chip | `FIRESTARTER_CHIP_DB_JSON` | 2 (`added={'foo': 1}`) | 1 |
| B | delete a chip (count change, no new name) | `FIRESTARTER_CHIP_DB_JSON` | 1, 2, 3, 4 (bonus), 5 — all `count_changed`, zero `added`/`removed` | 1 |
| C | vacuous `{}` target | `FIRESTARTER_CHIP_DB_JSON` | 1, 2, 3, 4, 5 — non-vacuity guard fires explicitly | 1 |
| D | new key in generator only | `FIRESTARTER_BUILD_DB_SOURCE` | 6 (`added=['foo']`) | 1 |
| E | new key inside `extra_chips.json` | none (real-tree mutate + restore) | 6 (`added=['foo']`, via the supplement half of the union) | 1 |
| F | clean tree | none | none — 8 passed | 0 |

Note on the word `monkeypatch`: it appears in this document only inside
sentences explaining why it must **not** be used to set
`FIRESTARTER_CHIP_DB_JSON` / `FIRESTARTER_BUILD_DB_SOURCE` for a planted leg
— those environment variables are read once, at module import time, so a
`monkeypatch.setenv` call made from inside a running test body would have no
effect on the already-resolved `_DB_PATH`/`_GEN_PATH` `Path` objects, making
the planted leg unreachable.
