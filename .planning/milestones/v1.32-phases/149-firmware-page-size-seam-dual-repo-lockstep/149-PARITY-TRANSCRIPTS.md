# 149-PARITY-TRANSCRIPTS.md — Phase 149 Plan 05 (PGSZ-03, D-18) transcripts

Transcripts for `tests/test_json_key_parity.py`'s two undecorated planted-fixture legs, and (below,
added by this plan's Task 3) the empty-`FIRESTARTER_FW_ROOT` skip-leg transcript. All commands run
from `/workspaces/firestarter_app`.

## Plant 1 — key-string drift (`planted_json_parser_key_string_drift.c`)

The page-size PROGMEM string is spelled with an underscore (`page_size`) instead of the wire's
hyphen (`page-size`) — Pitfall 10's exact shape.

### pytest invocation (the wrapper test, which asserts the helper raises — expected exit 0)

```
$ python3 -m pytest tests/test_json_key_parity.py::test_planted_key_string_drift_is_detected -o addopts="" -q ; echo EXIT=$?
.                                                                        [100%]
1 passed in 0.04s
EXIT=0
```

### Direct helper invocation — the seen-to-fail evidence (outside pytest, no wrapper)

```
$ python3 -c "
import tests.test_json_key_parity as m
m.FIRMWARE_PARSER_SOURCE = m._FIXTURE_KEY_STRING_DRIFT
try:
    m._check_page_size_key_present_and_dispatched()
    print('UNEXPECTED: did not raise')
except AssertionError as e:
    print('RAISED:', e)
"
RAISED: no PROGMEM key string equal to JSON_KEY_PAGE_SIZE ('page-size') was found in /workspaces/firestarter_app/tests/fixtures/planted_json_parser_key_string_drift.c -- extracted key strings: ['address', 'algorithm', 'chip-id', 'flags', 'memory-size', 'page_size', 'pin-count', 'pulse-delay', 'read-settling-delay', 'read-strobe-us', 'vpp_mv']
```

The raised message names `page_size` (the fixture's mis-spelling) among the extracted keys and
never `page-size` — the gate's own shared helper (`_check_page_size_key_present_and_dispatched`,
the same one `test_page_size_key_string_matches_constants_py` calls) is what fired, not a
parallel reimplementation.

## Plant 2 — undispatched key (`planted_json_parser_undispatched_key.c`)

The page-size PROGMEM string is spelled correctly (`page-size`), but its `key_parsers[]` row is
absent — the declared-but-unwired hole.

### pytest invocation (expected exit 0)

```
$ python3 -m pytest tests/test_json_key_parity.py::test_planted_undispatched_key_is_detected -o addopts="" -q ; echo EXIT=$?
.                                                                        [100%]
1 passed in 0.03s
EXIT=0
```

### Direct helper invocation — the seen-to-fail evidence

```
$ python3 -c "
import tests.test_json_key_parity as m
m.FIRMWARE_PARSER_SOURCE = m._FIXTURE_UNDISPATCHED_KEY
try:
    m._check_page_size_key_present_and_dispatched()
    print('UNEXPECTED: did not raise')
except AssertionError as e:
    print('RAISED:', e)
"
RAISED: the page-size key string 'page-size' is declared as 'key_page_size' but that identifier does not appear inside the key_parsers[] dispatch body -- a PROGMEM string that is declared but never dispatched exists on the wire and never matches anything a host sends.
```

Leg isolation, confirmed by the test module's own assertions and visible above: plant 1's message
never contains the phrase "does not appear inside the key_parsers"; plant 2's message never contains
"no PROGMEM key string equal to JSON_KEY_PAGE_SIZE" — the two failure modes are distinguishable from
their raised text alone.

### Real firmware source untouched

Both plants inject via `monkeypatch.setattr` on the module-scope `FIRMWARE_PARSER_SOURCE` constant,
never an edit to the real file. Confirmed after both runs above:

```
$ git -C /workspaces/firestarter status --porcelain
(empty)
$ test "$(git -C /workspaces/firestarter hash-object src/json_parser.c)" = "$(git -C /workspaces/firestarter rev-parse HEAD:src/json_parser.c)" && echo MATCH
MATCH
```

Both planted legs also assert this same before/after blob-hash equality and the empty-porcelain
condition internally, every time they run (the V12 ceremony), not just in this manual transcript.

## The empty-FW_ROOT skip leg (D-18)

`tests/fw_presence.py` binds `FW_ROOT` / `FW_REPO_PRESENT` / `requires_fw` at **import time**, so
`monkeypatch.setenv` has no effect — the skip condition must be proved in a subprocess, pointing
`FIRESTARTER_FW_ROOT` at a directory with no `.git` marker (a fresh `mktemp -d`). This is exactly the
state `firestarter_app`'s own CI runs in: it has no sibling `firestarter` checkout at all, so every
`@requires_fw` leg in this module skips on every push, and the two planted legs — which read a
committed fixture, never the sibling checkout — are the ONLY part of this gate app CI exercises.

### Module-scoped run

```
$ TMPROOT="$(mktemp -d)" && FIRESTARTER_FW_ROOT="$TMPROOT" python3 -m pytest tests/test_json_key_parity.py -rs -o addopts="" -q ; echo EXIT=$?
ssssssss..                                                               [100%]
=========================== short test summary info ============================
SKIPPED [1] tests/test_json_key_parity.py:230: firestarter firmware checkout absent (no /tmp/tmp.jcgJ57AfEz/.git marker)
SKIPPED [1] tests/test_json_key_parity.py:245: firestarter firmware checkout absent (no /tmp/tmp.jcgJ57AfEz/.git marker)
SKIPPED [1] tests/test_json_key_parity.py:255: firestarter firmware checkout absent (no /tmp/tmp.jcgJ57AfEz/.git marker)
SKIPPED [1] tests/test_json_key_parity.py:278: firestarter firmware checkout absent (no /tmp/tmp.jcgJ57AfEz/.git marker)
SKIPPED [1] tests/test_json_key_parity.py:299: firestarter firmware checkout absent (no /tmp/tmp.jcgJ57AfEz/.git marker)
SKIPPED [1] tests/test_json_key_parity.py:323: firestarter firmware checkout absent (no /tmp/tmp.jcgJ57AfEz/.git marker)
SKIPPED [1] tests/test_json_key_parity.py:331: firestarter firmware checkout absent (no /tmp/tmp.jcgJ57AfEz/.git marker)
SKIPPED [1] tests/test_json_key_parity.py:351: firestarter firmware checkout absent (no /tmp/tmp.jcgJ57AfEz/.git marker)
2 passed, 8 skipped in 0.03s
EXIT=0
```

The 8 `@requires_fw` legs are SKIPPED with `fw_presence.py`'s absent-firmware reason text — not
ERROR, not FAILED. `test_planted_key_string_drift_is_detected` and
`test_planted_undispatched_key_is_detected` are the 2 "passed" — neither appears in the skipped set.
Exit code is 0.

### Whole-suite run (the shape `tools/ci_parity.sh`'s leg 1 actually runs)

```
$ TMPROOT="$(mktemp -d)" && FIRESTARTER_FW_ROOT="$TMPROOT" python3 -m pytest tests/ -rs -o addopts="" -q ; echo EXIT=$?
...
SKIPPED [1] tests/test_json_key_parity.py:230: firestarter firmware checkout absent (no /tmp/tmp.SEPdSMbQ2W/.git marker)
SKIPPED [1] tests/test_json_key_parity.py:245: firestarter firmware checkout absent (no /tmp/tmp.SEPdSMbQ2W/.git marker)
SKIPPED [1] tests/test_json_key_parity.py:255: firestarter firmware checkout absent (no /tmp/tmp.SEPdSMbQ2W/.git marker)
SKIPPED [1] tests/test_json_key_parity.py:278: firestarter firmware checkout absent (no /tmp/tmp.SEPdSMbQ2W/.git marker)
SKIPPED [1] tests/test_json_key_parity.py:299: firestarter firmware checkout absent (no /tmp/tmp.SEPdSMbQ2W/.git marker)
SKIPPED [1] tests/test_json_key_parity.py:323: firestarter firmware checkout absent (no /tmp/tmp.SEPdSMbQ2W/.git marker)
SKIPPED [1] tests/test_json_key_parity.py:331: firestarter firmware checkout absent (no /tmp/tmp.SEPdSMbQ2W/.git marker)
SKIPPED [1] tests/test_json_key_parity.py:351: firestarter firmware checkout absent (no /tmp/tmp.SEPdSMbQ2W/.git marker)
...
1639 passed, 58 skipped, 1 warning in 209.57s (0:03:29)
EXIT=0
```

No `ERROR` line and no `failed` anywhere in the run's output. `test_planted_key_string_drift_is_detected`
and `test_planted_undispatched_key_is_detected` do not appear in the `-rs` skip summary — they are
part of the 1639 passed.

**State that:** `firestarter_app`'s own standalone CI has no sibling firmware checkout, so the state
captured above — every `@requires_fw` leg SKIPPED, both planted legs PASSED, exit 0 — is exactly the
state this module runs in on every push to that repository. The two planted legs are the only part of
`test_json_key_parity.py` that app CI exercises; the eight `@requires_fw` legs run only in an
environment (this devcontainer, or a future CI leg with the firmware checked out) where the sibling
`firestarter` repo is present.

## `bash tools/ci_parity.sh` — all four legs

```
Leg 1 (pytest, empty sibling root):  exit 0
Leg 2 (pytest, sibling present):     exit 0
Leg 3 (ruff check + format --check): exit 0
Leg 4 (mypy watermark gate):         exit 2
CI-PARITY: FAIL (legs:4)
```

Leg 4's exit 2 is the devcontainer's documented, pre-existing local condition (ambient numpy
PEP-695 stub truncating mypy's run on Python 3.12; `tools/ci_parity.sh`'s own header names this
exact exit code as "the gate working correctly, not a script defect"). It is unrelated to this
plan's changes and was not introduced by them — legs 1-3, which this plan's changes bear on, all
exit 0.
