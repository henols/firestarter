# Standards for Voltage-Reading Accuracy

The following standards apply to this work. Each section gives why it applies, then the full text
of the standard as it stands at spec time.

---

## testing/no-source-introspection

**Why it applies here:** `firestarter_fw/tests/test_voltage_reformulation_oracle.py` is the ONLY thing proving the shipped conversion formula, and it is a source-text scan bound to the C by regex. Task 2 ports its cases into a native Unity suite and deletes it, which this standard requires when you touch one.

# No Source Introspection

A test exercises production code with data. It never reads source text and asserts on its contents, whether by regex, substring or `ast`. This applies in all repos.

| Allowed | Forbidden |
|---|---|
| Call production functions; assert on results | Read `.py` `.c` `.h` `.cpp` `.md` `.yml` `.toml` and assert on the text |
| Read shipped data (`firestarter/data/*.json`, `pinouts.json`) | `ast` walks of production modules |
| Native Unity tests that run firmware code | Tests that parse another repo's source |

Why: source scanners fail open. A rename makes them skip or match zero times, and nothing goes red.

- If a hazard cannot be observed by a test, make it true by construction: codegen from one source (like `tools/catalog/`), a single shared definition, `static_assert` / `#error`.
- Host/firmware parity comes from codegen, not from a parity test.
- The source contracts in `firestarter_fw/tests/` are legacy, pending removal. Add none, do not extend them, and remove one when you touch it.

---

## testing/native-firmware-tests

**Why it applies here:** `src/boards/rurp_common.cpp` is outside every `build_src_filter`, so the conversion math has no native and no bench coverage. Task 2 extracts the pure math into a testable TU and registers a new suite in BOTH `test_filter` and `shared_build_flags`.

# Native Firmware Tests

Unity suites live in `test/native/avr/<suite>/` and run on the host with `platform = native`.

To add a suite, update both lists in `[native_base]` in `platformio.ini`:

```ini
test_filter = ... native/avr/<suite>
shared_build_flags = ... -I test/native/avr/<suite>
```

A suite that is not in `test_filter` never runs.

```bash
pio test -e native && pio test -e native_nodevtools   # run both; CI runs `native` on PRs only
```

Harness blind spots:
- The recording stubs (`test/native/avr/_shared/host_stubs_common.inc`) log every register write. Real `rurp_write_to_register` skips unchanged values. Do not count register writes.
- Time is fake. Most suites mock `millis()` through ArduinoFake to always return 0, and `delay()` records nothing. Do not assert timing.

Golden traces run the happy path (matching chip ID, VPP in window). For every branch, add explicit tests: chip-ID mismatch, each WARNING/ERROR fork, VPP out of window, poll timeout.

---

## testing/non-vacuity

**Why it applies here:** The retuned VPP guard window (Task 6) and the conversion math (Task 2) each need a violating input, both boundaries, and a case proving the instrument is not inert. A guard that cannot fire is exactly the failure mode v1.40 RAIL-03 recorded.

# Prove a Check Can Fail

Every new check (gate, guard, refusal) ships with committed tests that feed it violating input and assert that it refuses.

```python
def test_is_affected_true_at_bit_19(): ...                   # refuses
def test_is_affected_false_at_bit_18(): ...                  # boundary: passes
def test_require_acknowledged_no_bus_key_raises_fail_closed(): ...  # absent evidence
```

- Test both sides of each threshold.
- For a fail-closed check, test `None` / empty / missing input.
- The violation is in the input data (synthetic pin map, bad page size). Never mutate source to plant it.
- A test written before the fix must fail on its own assertion. If it fails on setup or lookup, the test is broken, not the code. Read the failure message.
- Assertions on shipped data use exact counts (`== 746`), never floors (`>=`). A change updates the number on purpose.

---

## firmware/size-reporting

**Why it applies here:** Every task from 2 onward changes firmware. Leonardo is the tightest target with 4856 B of margin at last measure, and averaging plus a new dev command both cost flash.

# Flash and RAM Reporting

Every firmware change reports flash and RAM, before and after, for `leonardo` and `uno`.

```bash
pio run -e leonardo                                       # stable image
PLATFORMIO_BUILD_FLAGS="-D DEV_TOOLS=1" pio run -e leonardo   # beta image (larger)
pio run -e uno
```

- Take the numbers from the `RAM:` / `Flash:` lines of the build output.
- Leonardo is the tightest target: 28672 B Caterina ceiling, not 32768.
- Report the beta (`DEV_TOOLS=1`) image too. It ships and it is larger.
- Always report RAM next to flash. A PROGMEM move trades one for the other.

---

## firmware/fail-closed-refusals

**Why it applies here:** `rurp_read_voltage_mv` returns 0 on an implausible calibration. 0 reads as LOW, which is only a WARNING, so a write proceeds against an unknown rail. That is a silent clamp on a high-voltage path.

# Fail-Closed Refusals

Unknown or out-of-range input is refused with an error ID. Never clamp, never pick a default row.

```cpp
const eprom_params_t* row = eprom_params_for(handle->protocol);
if (row == NULL) {                       // never &EPROM_PARAMS[0]
    LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, (uint8_t)handle->protocol);
    handle->response_code = RESPONSE_CODE_ERROR;
    return;
}
if (energy_cap_us > 0 && handle->pulse_delay > energy_cap_us) {  // 0 = uncapped
    LOG_ERROR_ID_U32(MSG_ERR_PULSE_TOO_WIDE, handle->pulse_delay);
    handle->response_code = RESPONSE_CODE_ERROR;
    return;
}
```

Why: a fallback can put HV on a part that cannot take it. A silent clamp gives a verify failure that looks like bad silicon. The host needs an explicit error ID as evidence.

- Refuse pre-flight, before any HV bit is set.
- Every refusal = `LOG_ERROR_ID_*` + `RESPONSE_CODE_ERROR` + `return`. Change no hardware state.
- Lookups return NULL on no match; callers check it.
- Unknown protocol values end in `configure_not_implemented()` (`0xBB`). No other path.
- Only exception: a `0` on the wire means "use the handler default" (`pulse_delay`, AT28C `page_size`). Resolve the default first, then run the refusal checks.
- Guard sentinels: `0` in a cap field means "uncapped", not "cap at zero".

---

## firmware/timing

**Why it applies here:** The post-mux settling delay added in Task 2 must carry a cited AVR datasheet figure, not a guessed number.

# Timing, Polls and Delays

Bound new chip-poll loops by an iteration count, not a `millis()` deadline.

```cpp
// An ITERATION COUNT, not a millis() deadline: native suites mock millis() == 0.
#define AT28C_PAGE_POLL_MAX_READS 2000

for (uint16_t n = 0; n < AT28C_PAGE_POLL_MAX_READS; n++) {
    if ((read(addr) & AT28C_DQ7_MASK) == (expected & AT28C_DQ7_MASK)) return true;
}
return false;
```

- Native suites mock `millis()` to 0, so a deadline loop never ends under test.
- The `millis() < deadline` loops in `flash_intel.cpp` and `flash_utils.cpp` are legacy. Do not copy them.
- Every timing value is a named `#define` with a unit suffix (`_US`, `_MS`) and a citation: `[doc number, rev, section, page]`.
- Say in the comment whether the value is a delay to insert or a maximum to stay under (e.g. `t_BLC`).
- Delays above 16383 µs go through `mem_util_delay_us()`. AVR `delayMicroseconds()` is inaccurate above that.
- An erase pulse has its own constant (`EPROM_ERASE_PULSE_US`). Never reuse `handle->pulse_delay` for it; that is the per-byte program width.

---

## protocol/message-catalog

**Why it applies here:** Task 3 adds a message ID for the raw-count readout. `messages.toml` in the meta repo is the only source; `messages.h` and `messages.py` are generated and never hand-edited.

# Message Catalog

Message IDs have one source: `tools/catalog/messages.toml` in the meta repo. Generate the artifacts only there.

```bash
# edit tools/catalog/messages.toml, then:
tools/catalog/sync_to_subrepos.sh   # writes firestarter_fw/include/messages.h
                                    #    and firestarter_app/firestarter/messages.py
```

- Never hand-edit `messages.h` or `messages.py`. The next sync overwrites them without warning.
- Never regenerate in a sub-repo. The sub-repos hold generated artifacts only.
- Commit in all three repos on the same milestone branch: catalog (meta), `messages.h` (fw), `messages.py` (app).
- A new ID needs host rendering in the same change (format string, render hints, decoder handling).
- Never reorder entries.
- The ERROR band `0xA0–0xBF` is full. New ERROR IDs start at `0xC0`. Severity comes from the `severity` field, never from the ID range.
- Params: at most 24 wire bytes. `wire_format = "text"` entries have `params = []`.

---

## protocol/duplicated-constants

**Why it applies here:** Task 3's new command ordinal exists in both `firestarter_fw/include/firestarter.h` and `firestarter_app/firestarter/constants.py`.

# Duplicated Host/Firmware Constants

Some wire values exist on both sides. Change both sides in one change pair.

| Host (`firestarter_app/firestarter/`) | Firmware (`firestarter_fw/`) |
|---|---|
| `constants.py` `COMMAND_*` | `include/firestarter.h` `CMD_*` |
| `constants.py` `FLAG_*` | `include/firestarter.h` `FLAG_*` |
| `constants.py` `CTRL_*` | `include/rurp_pinout.h` `CTRL_*` |
| `constants.py` `JSON_KEY_*` | `src/json_parser.c` key strings |
| `constants.py` `BUFFER_SIZE`, `CMD_FRAME_MAX` | `firestarter.h` `DATA_BUFFER_SIZE`, `CMD_FRAME_MAX` |

- Edit both files and commit both on the same milestone branch.
- A change to one side only is incomplete, even if all tests pass.

---

## protocol/rollout-compatibility

**Why it applies here:** Firmware ships before the host command that depends on it. `MSG_DATA_VPP_VOLTAGE` is a FIXED-length 4-u16 frame, so it is NOT widened — the raw counts go in a new message.

# Rollout and Compatibility

Firmware ships first. The host may require the latest firmware.

- Release the firmware before the host that depends on it.
- If the firmware is too old, the host raises `FirmwareOutdatedError`, and the message tells the user to run `firestarter fw --install`. The host has no fallback paths for old firmware.
- New ack and blob fields go at the end. The host finds them by frame length, never by version string. Compute offsets from the length bytes (`ver_len`), never from a literal index.
- A numeric field has a plausibility range, and `0` means "not sent" (e.g. `write_budget_s` accepts `[1, 14400]`). Never read `0` as a real value.

---

## host/help-docstrings

**Why it applies here:** The new host diagnostic command's docstring is user-facing `--help` text.

# Click Docstrings Are --help

A command docstring and every `help=` string are user documentation. Click prints them as `--help`.

- No internal references: no phase or plan IDs, requirement tags (`WRITE-01`), `file:line`, or maintainer notes.
- Put implementation reasoning in a `#` comment in the function body, not in the docstring.
- Write in ASD-STE100 (same as refusal text).
- Do not add tests that pin `--help` text.

---

## host/echo-vs-logger

**Why it applies here:** `click.echo` for the operator-facing raw-count output at default verbosity; `logger` for -v diagnostics.

# click.echo vs logger

`logger.*` is for diagnostics that show only with `-v`. A fact the operator needs uses `click.echo`, so it shows at default verbosity.

```python
# operator must see this without -v
click.echo(f"{eprom.upper()}: pulse override {pulse_us} us (database: {db_pulse} us)")

# diagnostic detail
logger.debug("resolved bus config: %s", bus_config)
```

- Use `click.echo` for: refusals that exit without an exception, verdict lines, and notices that change what the operation does.
- Use `logger` for: trace detail, timings, raw frames.

