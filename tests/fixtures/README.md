# `tests/fixtures/` — naming discipline

This directory holds committed evidence used by Phase 123's baseline JSON and its downstream
checkers/tests (123-02 … 123-06). Every fixture in this phase — in this directory and in the
sibling `firestarter_app/tests/fixtures/` and `.planning/phases/123-…/fixtures/` directories —
follows the same three-prefix naming discipline:

- **`captured_*`** — verbatim tool output, committed **unedited**. No trimming beyond an explicitly
  recorded contiguous window, no reflow, no ANSI stripping, no hand-edited number. If a capture is
  truncated (for example, a `pio test` tail block rather than the full run), the truncation point is
  a stated fact in the producing plan's SUMMARY, never an invisible edit.
- **`planted_*`** — a deliberate violation, each derived from a named `captured_` (or otherwise real)
  file by a single stated edit, used to prove a checker fails closed rather than passing vacuously.
- **`clean_*`** — a control that must pass a checker cleanly, proving the checker does not fire on
  legitimate input.

## Why `firestarter/tests/` cannot reach a real build

`firestarter/tests/` is invisible to PlatformIO. PlatformIO's unit-test discovery globs `test/`
(the real native suites live at `test/native/avr/…`), and the default `[env]` source filter for the
two native environments is explicitly
`+<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>` — no path under
`tests/` is named anywhere in `platformio.ini`. A `.cpp` fixture placed here therefore cannot reach
any build, `pio run` or `pio test` alike, and `platformio.ini` stays completely untouched by this
phase.

## Verifying fixture presence

Fixture presence in this directory is verified with `git ls-files`, **never** with `git add`'s exit
code. Git refuses to stage any path containing a `.git` path component (file or directory) and does
so **silently at exit 0** — `git add` reports success while staging nothing. `git ls-files` is the
only check that reflects what is actually tracked in the index. Every capture in this directory is
independently checked with `git ls-files tests/fixtures/` rather than trusted from a shell's own exit
code.

## Per-file inventory is mechanical, not prose

The per-file inventory (which `captured_/planted_/clean_` file exists, and which checker/pytest each
one backs) is enforced mechanically by `tests/test_checker_convention.py` (Phase 123 Plan 06), not
duplicated here as a hand-maintained list. Prose here would drift the moment a new checker or fixture
is added; the convention test cannot.

## Files in this directory (as of Plan 01)

| File | Prefix | Backs |
|------|--------|-------|
| `captured_build_uno.log` | `captured_` | BASE-01 comparator (`check_size_baseline.py`), BASE-06 warning gate (AVR zero rule) |
| `captured_build_uno328pb.log` | `captured_` | same |
| `captured_build_leonardo.log` | `captured_` | same |
| `captured_test_native_summary.log` | `captured_` | BASE-01 comparator native-env parsing |
| `captured_test_native_nodevtools_summary.log` | `captured_` | same, `native_nodevtools` env |
| `captured_native_warnings_excerpt.log` | `captured_` | BASE-06 warning gate — proves the parser survives real `pio test` framing around a genuine macro-redefinition diagnostic, not just a bare compiler invocation |

**Known, recorded gap (D-14):** `pio test` output never contains a literal `Compiling .pio/build/...`
progress line — that framing is specific to `pio run` (see `captured_build_uno.log` for an example).
`captured_native_warnings_excerpt.log` instead carries `pio test`'s own real framing for that command
(`Processing <suite> in native environment`, `Building...`, and the compiler's own `In file included
from ...` chain) immediately surrounding the warning — this is pio's genuine wrapping for this
command, verified across default, `-v` and `-vvv`-on-a-clean-rebuild invocations, none of which ever
emit the word `Compiling` during `pio test`. Recorded here, and in `123-01-SUMMARY.md`, so a later
reader does not mistake the absence for an incomplete capture.
