---
status: resolved
trigger: "firestarter info command crashes with a TypeError in ic_layout.py (vpp-pin comparison bug) — e.g. `firestarter info W27C512` exits 1 with a traceback instead of displaying chip info. This blocks the DEC-03 user-visible verification in Phase 57 (the regenerated chip_database.json has W27C512 pulse_duration=100 us, but the info command can't display it). Pinned by tests/test_characterization.py::test_info_known_chip in firestarter_app. Find root cause and fix."
created: 2026-06-08T13:53:08Z
updated: 2026-06-08T14:10:00Z
related_phase: 57-decode-bug-fixes-protocol-map-check-dispatch-extension
sub_repo: firestarter_app
---

# Debug Session: firestarter-info-vpp-pin-crash

## Symptoms

DATA_START

**Expected behavior:** `firestarter info W27C512` (and any chip) displays the chip's
detailed specification — including the corrected `programming.pulse_duration` of 100 us
from the Phase-57-regenerated `chip_database.json` — and exits 0.

**Actual behavior:** The command exits 1 with a Python traceback and displays no chip
info. Per the `test_info_known_chip` docstring, this crash affects **all chips**, not
just W27C512.

**Error message (reproduced 2026-06-08 via the `firestarter` console script at
`~/.local/bin/firestarter`, system python 3.12):**

```
  File "/workspaces/firestarter_app/firestarter/cli_handlers.py", line 338, in info
    structured_details = app.eprom_presenter.prepare_detailed_eprom_data(...)
  File "/workspaces/firestarter_app/firestarter/eprom_info.py", line 122, in prepare_detailed_eprom_data
    eprom_specifications = self.spec_builder.build_specifications(eprom_details)
  File "/workspaces/firestarter_app/firestarter/ic_layout.py", line 506, in build_specifications
    display_pin_names = self._generate_pin_names_for_display(eprom_data)
  File "/workspaces/firestarter_app/firestarter/ic_layout.py", line 396, in _generate_pin_names_for_display
    if "vpp-pin" in pin_map_details and pin_map_details["vpp-pin"] <= pin_count:
TypeError: '<=' not supported between instances of 'list' and 'int'
```

**Timeline:** Pre-existing. `tests/test_characterization.py::test_info_known_chip`
explicitly pins this as "the CURRENT broken behavior" (rc==1 + traceback on stderr), so
it predates Phase 57. Phase 57 declared it out of scope but it now blocks the DEC-03
user-visible surface (`firestarter info W27C512` should show 100 us).

**Reproduction:** `cd firestarter_app && firestarter info W27C512` (or any chip).
Note: `python -m firestarter` fails differently (no `__main__`); use the console script.

DATA_END

## Initial Evidence

- Crash site: `ic_layout.py:394` in `_generate_pin_names_for_display`:
  `pin_map_details["vpp-pin"] <= pin_count` — LHS is a `list`, RHS is an `int`.
- The Phase 57 `check_dispatch.py` GATE-03 guard (plan 57-02) treats `vpp-pin` as a
  pinout field and loads `pinouts.json`; that work touched the *dispatch* reader, not
  this *display* reader. Worth comparing how each consumes the `vpp-pin` field shape.
- `chip_database.json` was regenerated in Phase 57 (plan 57-03) but the algorithm/pinout
  fields were proven unchanged vs the Phase-56 baseline (0 diffs), so the crash is NOT a
  Phase-57 data regression — it is the pre-existing display-path bug.

## Current Focus

hypothesis: CONFIRMED — `_generate_pin_names_for_display` assumes `pin_map_details["vpp-pin"]`
is a scalar pin index, but pinouts.json stores all single-pin fields (vpp-pin, oe-pin,
rw-pin) as single-element lists (e.g. `[22]`). The `<= pin_count` comparison raises TypeError.
Secondary: `database._map_data()` hardcoded `pulse-delay: 0` despite chip_database.json
carrying `programming.pulse_duration: "100 us"`.

## Evidence

- `pinouts.json` DIP28_27512 entry: `"vpp-pin": [22]` — a list, not a scalar.
- All single-pin fields (vpp-pin, oe-pin, rw-pin, ce-pin) across all 12 pin maps
  are single-element lists; none are scalars.
- `database.py:425`: `"pulse-delay": 0,  # Not directly available in new format`
  — the `programming.pulse_duration` field was never parsed; hardcoded to 0.

## Eliminated

- Phase-57 data regression: chip_database.json pinout fields are unchanged vs Phase-56
  baseline (0 diffs). The bug predates Phase 57.

## Resolution

root_cause: Two bugs in the `firestarter info` display path. (1) `ic_layout._generate_pin_names_for_display` compared pin map fields (vpp-pin, oe-pin, rw-pin) as integers but `pinouts.json` stores them as single-element lists — `[22] <= 28` raises `TypeError: '<=' not supported between instances of 'list' and 'int'`. (2) `database._map_data()` hardcoded `pulse-delay: 0` rather than parsing `programming.pulse_duration` ("100 us" → 100).

fix: (1) Added `EpromSpecBuilder._first_pin(pin_field)` static helper to extract the integer from a single-element list field; replaced all three scalar usages in `_generate_pin_names_for_display` with extracted locals. (2) Added `_parse_pulse_duration(pulse_str) -> int` module-level helper to `database.py` that parses "N us" strings; wired it into `_map_data()`. Updated `test_info_known_chip` and `test_info_chip_resolution_happy_path` to assert exit 0; refreshed characterization snapshot showing `Pulse delay: 100µS`.

verification: `firestarter info W27C512` exits 0 and displays full chip info including `Pulse delay: 100µS`. 480 tests pass. ruff check + format --check clean on all changed files. Committed as `8088141` on branch `v1.11-infoic-decode-correctness` in `firestarter_app`.

files_changed:
  - firestarter/ic_layout.py (add _first_pin helper; fix _generate_pin_names_for_display)
  - firestarter/database.py (add _parse_pulse_duration; wire into _map_data)
  - tests/test_characterization.py (update test_info_known_chip to assert exit 0)
  - tests/test_cli_handlers.py (update test_info_chip_resolution_happy_path to assert exit 0)
  - tests/__snapshots__/test_characterization.ambr (refresh snapshot with correct output)
