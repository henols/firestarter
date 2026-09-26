# Phase 127: Host DFU Installer - Pattern Map

**Mapped:** 2026-08-01
**Files analyzed:** 14 (7 new test modules · 4 modified source/config · 1 CI workflow · 1 doc · 1 evidence artifact)
**Analogs found:** 13 / 14
**Repo:** all code lives in `firestarter_app/`. `firestarter/` (firmware) is a **read-only** analog source.

> **Read-only mechanic the planner must encode:** files arriving with the `4ee64a1` merge do
> **not exist on the current checkout**. Read them with
> `cd /workspaces/firestarter_app && git show 4ee64a1:<path>`. All excerpts below tagged
> `@4ee64a1` were extracted that way; line numbers correspond to the merged tree, matching
> `127-RESEARCH.md`'s anchors.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `tests/test_dfu_opcode_anchors.py` **(new)** | test (known-answer) | pure/transform | `firestarter/tests/test_config_storage_dualslot.py:107-111,573-588` (CRC32 KAT, 126 D-05) | exact (discipline) |
| `tests/test_py32_flash_map_host.py` **(new)** | test (cross-repo gate) | file-I/O + parse | `firestarter/tests/test_py32_flash_map.py:172-183,234-250` (parser) + `firestarter_app/tests/test_revision_constants_parity.py` (parity-gate shape) + `tests/test_sdp_bus_config_drift.py:19,38,41` (`fw_path`/`requires_fw` binding) | exact (3-way composite) |
| `tests/test_py32_pyusb_absent.py` **(new)** | test (subprocess) | process/event | `tests/test_skip_census.py:199-245` | exact |
| `tests/test_py32_channel_gating.py` **(new)** | test (subprocess) | process/event | `tests/test_skip_census.py:199-245` | exact |
| `tests/test_pyusb_api_surface.py` **(new)** | test (optional-dep integration) | request-response (USB) | **none** — see § No Analog Found | none |
| `tests/test_py32_packaging.py` **(new)** | test (textual/config) | file-I/O | **none for TOML parsing** — see § No Analog Found | partial |
| `tests/test_py32_dfu.py` **(modified)** | test fixture/fake | request-response | its own `_FakeUsbDevice.ctrl_transfer` `DFU_GETSTATUS` arm (`:57-69` @4ee64a1) | exact (self) |
| `firestarter/py32_dfu.py` **(modified)** | service/protocol client | request-response (USB control transfers) | its own `_get_status()` (`:678-683`) for the readback; `firmware.py:79-80` for the result-constant idiom | role-match |
| `firestarter/cli_handlers.py` **(modified)** | CLI controller | request-response | its own `--dfu-probe` refusal (`:941-946` @4ee64a1) | exact (self) |
| `firestarter/firmware.py` **(modified — comment only, D-17)** | service | request-response | its own `flash_method()` docstring (`:95-97`) | exact (self) |
| `pyproject.toml` **(modified)** | config | — | existing `[project.optional-dependencies]` block | exact |
| `.github/workflows/ci.yml` **(modified)** | config/CI | batch | the existing `ci:` job in the same file | exact |
| `doc/PY32F071-FIRMWARE-INSTALL.md` **(modified)** | doc | — | itself (scoped edit, D-15) | n/a |
| `.planning/phases/127-host-dfu-installer/127-NONREGRESSION.md` **(new)** | evidence artifact | — | `126-NONREGRESSION.md` / `125-NONREGRESSION.md` | exact |

---

## Pattern Assignments

### `tests/test_dfu_opcode_anchors.py` (new · known-answer test · D-18/HOST-06)

**Analog:** `/workspaces/firestarter/tests/test_config_storage_dualslot.py` — Phase 126 D-05's
independent CRC32 known-answer vector. This is the *discipline* precedent named in CONTEXT.

**Independent-constant block** (`test_config_storage_dualslot.py:107-111`):
```python
# The CRC32 known-answer vector (D-05) -- an INDEPENDENT vector, written
# ...
_CRC32_KAT_INPUT = b"123456789"
_CRC32_KAT_EXPECTED = 0xCBF43926
```

**The assertion shape** (`:573-588`):
```python
def test_crc32_matches_the_independent_known_answer_vector():
    """Coverage 1 -- D-05: the compiled core's rurp_config_crc32 over the
    ..."""
        observed = int(rows[0]["crc32"], 16)
        assert observed == _CRC32_KAT_EXPECTED, (
            f"expected CRC32({_CRC32_KAT_INPUT!r}) == "
            f"{_CRC32_KAT_EXPECTED:#010x}, got {observed:#010x}.\n"
```

**Docstring framing to copy** (`test_config_storage_dualslot.py:27-28`) — states *why* the
independent vector exists:
> `D-05 adds a seventh, independent known-answer vector (CRC32("123456789") == 0xCBF43926) so the other six do not merely agree with` …

**What the new module pins** (values read from `py32_dfu.py` @4ee64a1 — the test must write
them **independently** with a UM1504 / DFU 1.1 §3 citing comment, never import-and-compare):

| Constant | Value | Anchor line @4ee64a1 |
|---|---|---|
| `DFU_DETACH … DFU_ABORT` | `0,1,2,3,4,5,6` | `py32_dfu.py:51-57` |
| `_DFU_FUNCTIONAL_DESCRIPTOR` | `0x21` | `:93` |
| `DFUSE_SET_ADDRESS` | `0x21` | `:96` |
| `DFUSE_ERASE_PAGE` | `0x41` | `:97` |
| `DFUSE_READ_UNPROTECT` | `0x92` | `:98` |
| `DFUSE_VERSION` | `0x011A` | `:100` |
| `FLASH_BASE` | `0x08000000` | `:107` |

**C-2 constraint (LOAD-BEARING):** purely additive. Do **not** delete or convert anything in
`tests/test_py32_dfu.py`; the "self-referential assertions" D-18 orders removed do not exist
(measured). Every `DFUSE_*`/`FLASH_BASE` use there is a *label inside a sequencing assertion*,
e.g. `tests/test_py32_dfu.py:242` `assert (DFUSE_ERASE_PAGE, FLASH_BASE) in commands`.

---

### `tests/test_py32_flash_map_host.py` (new · cross-repo gate · D-14)

Three analogs compose here. Copy all three.

**(1) The parser — copy verbatim with a citing comment.**
Source: `/workspaces/firestarter/tests/test_py32_flash_map.py:172-183`:
```python
_REGION_RE = re.compile(
    r"^\s*(\w+)\s*\([A-Za-z]+\)\s*:\s*ORIGIN\s*=\s*(0x[0-9A-Fa-f]+|\d+)\s*,"
    r"\s*LENGTH\s*=\s*(\d+)\s*([KkMm]?)\s*$",
    re.MULTILINE,
)
_PROVIDE_RE = re.compile(r"PROVIDE\(\s*(__\w+)\s*=\s*(.*?)\)\s*;")
```
and `_parse_regions` (`test_py32_flash_map.py:234-250`):
```python
def _parse_regions(text):
    """Returns a dict of region name -> (origin: int, length: int), parsed
    from the MEMORY { ... } block. K/M suffixes on LENGTH are normalised to
    bytes."""
    m = re.search(r"MEMORY\s*\{(.*?)\n\}", text, re.DOTALL)
    if not m:
        return {}
    block = m.group(1)
    regions = {}
    for name, origin_s, length_s, suffix in _REGION_RE.findall(block):
        origin = int(origin_s, 0)
        length = int(length_s)
        if suffix.lower() == "k":
            length *= 1024
        elif suffix.lower() == "m":
            length *= 1024 * 1024
        regions[name] = (origin, length)
```

**(2) The cross-repo binding — `fw_path` + `requires_fw`, module-scope constant.**
Source: `firestarter_app/tests/test_sdp_bus_config_drift.py:19,38,41-48`:
```python
from tests.fw_presence import fw_path, requires_fw

# The committed sdp_bus_config.h lives in the SIBLING firestarter repo, so
# resolve it through the shared `fw_path` helper -- repo presence is decided
# ONCE in tests/fw_presence.py, keyed on the sibling's `.git` marker. `requires_fw`
# is the ONLY skip marker this module uses ...
_COMMITTED_HEADER = fw_path("test", "native", "avr", "_shared", "sdp_bus_config.h")


@requires_fw
def test_committed_header_exists() -> None:
    """The committed header must exist in the firestarter submodule."""
    assert _COMMITTED_HEADER.exists(), (
        f"sdp_bus_config.h not found: {_COMMITTED_HEADER}\n"
        ...
    )
```
For this phase: `fw_path("platform", "py32f071", "linker", "PY32F071xB_FLASH.ld")`.
`fw_path` raises `MissingScanTargetError` when the repo is present but the file is not
(`tests/fw_presence.py:118-139`) — that is the fail-closed half; do **not** hand-build the path.

**No `ALLOWED_SKIP_REASONS` edit is needed.** `requires_fw` is `pytest.mark.skipif(not FW_REPO_PRESENT, reason=FW_ABSENT_REASON)` (`fw_presence.py:102`), and `FW_ABSENT_REASON` is
**imported** into `tests/test_skip_census.py:92` as allow-list entry 1 (`:117`) — imported,
never re-typed, "so the two constants can never drift".

**(3) The non-vacuity assertion — real in-tree example.**
Source: `/workspaces/firestarter/tests/test_py32_flash_map.py:771-782`:
```python
def test_manifest_names_the_flash_driver():
    """Coverage 15 -- C-3's edit-4 assertion: an implication with a PROVEN
    antecedent. Fails if the scan finds zero HAL_FLASH_ call sites; records
    the scanned-file count and the call-site count either way."""
    files_scanned, call_sites = _scan_hal_flash_calls(_PY32_SRC_DIR, _REPO_ROOT)
    assert call_sites, (
        f"antecedent unproven: scanned {files_scanned} file(s) under "
        f"{_PY32_SRC_DIR}, found 0 HAL_FLASH_ call sites -- the implication "
        f"this test checks would be vacuously true"
    )
```
And the violations-helper form of the same rule (`:678-684`):
```python
    if call_site_count == 0:
        return [
            "antecedent unproven: 0 HAL_FLASH_ call sites found -- refusing "
            "to evaluate a vacuous implication (an implication with an "
            "unproven antecedent is exactly the vacuous shape this project "
            "has had to unwind twice)"
        ]
```
→ For D-14: `assert "FLASH" in regions and "CONFIG" in regions, ...` **before** any value
comparison.

**(4) The parity-gate + fail-closed-RED shape** — `firestarter_app/tests/test_revision_constants_parity.py`
is the host repo's own cross-repo constant-parity gate, and it already carries the RED
demonstration D-14 needs (`:795-806`):
```python
def test_gate_fails_closed_on_an_unreadable_header_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unreadable/absent header path must be an ERROR, never a silent
    pass -- an empty define set would make every downstream assertion
    vacuously true. ..."""
    missing = tmp_path / "does_not_exist.h"
    monkeypatch.setattr(sys.modules[__name__], "FIRMWARE_HEADER", missing)
    with pytest.raises(AssertionError, match="firmware header not found"):
        _check_cmd_two_way()
```
Firmware-side equivalent (planted mutated copies + blob-SHA-unchanged proof):
`firestarter/tests/test_py32_flash_map.py:565` `test_helper_reports_violations_on_planted_copies`.

**Expected values** (measured, `127-RESEARCH.md` §Q2): `FLASH` ORIGIN `0x08000000` / LENGTH
`120K` = `122880`; `CONFIG` ORIGIN `0x0801E000` / LENGTH `8K`; `BOOTLOADER` ORIGIN
`0x08000000` / LENGTH `0`.

---

### `tests/test_py32_pyusb_absent.py` and `tests/test_py32_channel_gating.py` (new · subprocess · D-05, D-07, HOST-05, HOST-08)

**Analog:** `firestarter_app/tests/test_skip_census.py`.

**Module-scope constants** (`test_skip_census.py:85-97`):
```python
import functools
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from tests.fw_presence import FW_ABSENT_REASON, FW_REPO_PRESENT

_APP_DIR = Path(__file__).parent.parent
```

**The subprocess harness to copy** (`test_skip_census.py:199-245`):
```python
@functools.lru_cache(maxsize=1)
def _run_child_suite() -> _ChildRunResult:
    """Run the full host suite (minus this module) as a subprocess, exactly
    once per test session, and return the parsed result. ..."""
    collect = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "--collect-only",
            "-q",
            _IGNORE_ARG,
        ],
        cwd=str(_APP_DIR),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert _THIS_MODULE not in collect.stdout, (
        f"{_IGNORE_ARG} did not take effect -- ..."
    )
```
Copy: `@functools.lru_cache(maxsize=1)` (pay the child cost once), `[sys.executable, "-m", ...]`,
`cwd=str(_APP_DIR)`, `capture_output=True, text=True`, an **explicit `timeout=`**, and the
"prove the argument took effect" pre-assertion (its analog here: prove the blocker/version
patch actually applied, rather than trusting it).

**Cached-result dataclass** (`test_skip_census.py:193-196`) for parsed child output:
```python
    skip_entries: tuple[tuple[str, str], ...]
    total_collected: int
```

**The `-c` preamble for the pyusb blocker** (measured working, `127-RESEARCH.md` §Q4):
```python
class UsbBlocker(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "usb" or fullname.startswith("usb."):
            raise ModuleNotFoundError(f"blocked: {fullname}", name=fullname)
        return None

sys.meta_path.insert(0, UsbBlocker())
for m in [m for m in sys.modules if m == "usb" or m.startswith("usb.")]:
    del sys.modules[m]
```
`find_spec` must **raise** (returning `None` defers to the next finder).

**The `-c` preamble for channel gating (D-07)** — order is load-bearing:
```python
import firestarter
firestarter.__version__ = '3.0.0'          # or '3.0.0b1'
from firestarter import cli_handlers        # AFTER the assignment
```
Why a subprocess and not a monkeypatch — the asymmetry to cite in the docstring:
`channel.is_prerelease_build()` imports `firestarter` **inside the function**
(`channel.py:38-52` @4ee64a1) so it re-reads `__version__` per call, while
`cli_handlers.py:139-141` computes once at import:
```python
_ALL_BOARDS: tuple[str, ...] = ("uno", "uno328pb", "leonardo", "py32f071")
_BOARD_CHOICES: list[str] = available_boards(_ALL_BOARDS)
_PY32_ENABLED: bool = "py32f071" in _BOARD_CHOICES
```
with the in-source comment (`cli_handlers.py:137-138`) that D-07 deliberately departs from:
> *"Tests exercise channel.available_boards() / is_board_available() directly rather than reloading this module."*

**Neither module adds an `ALLOWED_SKIP_REASONS` entry** — both run identically in both CI legs
and carry no skip marker.

---

### `firestarter/cli_handlers.py` — `_reject_py32_only_option()` (D-08 / HOST-02)

**Analog: the existing refusal, verbatim** (`cli_handlers.py:939-944` @4ee64a1):
```python
    if dfu_probe:
        # `hidden` keeps the option out of --help; it does not reject it. On a
        # stable build the flag must fail as an unknown-usage error, not silently
        # run a py32-only diagnostic.
        if not _PY32_ENABLED:
            raise click.UsageError("no such option: --dfu-probe")
```
→ Preserve the **exact** message `f"no such option: {name}"`, the `click.UsageError` type, and
therefore exit code **2** (measured live: `--dfu-probe` → 2; `--usb-id` → **0**, the bug).

**Option declarations** (`cli_handlers.py:841-853` @4ee64a1) — `hidden` is the *only* current
gate on `--usb-id`:
```python
    "--usb-id",
    ...
    hidden=not _PY32_ENABLED,
...
    "--dfu-probe",
    "dfu_probe",
    ...
    hidden=not _PY32_ENABLED,
```

**Placement constraint:** the helper must be called **unconditionally for each option**, passing
givenness, and must run **before** `--usb-id` is consumed at `probe_dfu(usb_id=usb_id)`
(`cli_handlers.py:945`).

**Second enforcement layer to preserve** — the service choke point (`firmware.py:_install_with_dfu`
@4ee64a1):
```python
        # Channel gate enforced here, not only in the CLI: this is the single
        # choke point every DFU install passes through, including library callers
        # that never touch Click.
        if not is_board_available(board):
            raise FirmwareOperationError(beta_only_message(board))
```

---

### `firestarter/py32_dfu.py` — `verify_result` + readback (D-09…D-13 / HOST-03)

**Result-constant idiom in this codebase** (`firmware.py:79-85` @4ee64a1) — module-level string
constants + a dict router, **not** `enum`:
```python
FLASH_METHOD_AVRDUDE = "avrdude"
FLASH_METHOD_DFU = "dfu"

_BOARD_FLASH_METHODS = {
    "uno": FLASH_METHOD_AVRDUDE,
    ...
}
```
> ⚠ **There is no `enum` import anywhere in `firestarter/` or `tests/`** (measured). D-10 names an
> "enum"; the planner must pick one and say so: stdlib `enum.Enum` (py39-safe, no `StrEnum` —
> that is 3.11+) is the honest reading of D-10, but it introduces a construct with zero in-repo
> precedent. Module-level string constants match precedent exactly. **Either satisfies "tests
> assert the enum, not log text"; flag the choice explicitly in the plan.**

**Exception hierarchy to extend** (`py32_dfu.py:114-124`):
```python
class DfuError(Exception):
    """Base class for every failure in this module."""


class PyusbMissingError(DfuError):
    """pyusb (or its libusb backend) is not importable."""


class DfuDeviceNotFoundError(DfuError):
    """No USB device exposing a DFU interface was found."""
```
Error chain for D-11's `MISMATCH` (already wired, no new plumbing):
`DfuProtocolError` → caught as `DfuError` in `_install_with_dfu` → `FirmwareOperationError` →
`ClickException` → exit 1.

**Readback core pattern — model on `_get_status()`** (`py32_dfu.py:678-683`), the only existing
IN control transfer:
```python
    def _get_status(self) -> Tuple[int, int, int]:  # noqa: UP006
        """Return ``(bStatus, poll_timeout_ms, bState)``."""
        raw = self._dev.ctrl_transfer(_IN, DFU_GETSTATUS, 0, self._index, 6)
        data = bytes(raw)
        if len(data) < 6:
            raise DfuProtocolError(f"Short DFU_GETSTATUS response: {len(data)} bytes")
```
An UPLOAD read is `self._dev.ctrl_transfer(_IN, DFU_UPLOAD, block, self._index, <length>)` —
5th arg is an **int length**, all five call-sites positional.

**`bitCanUpload`** — consumer only, no parsing: `bool(interface.attributes & 0x02)`.
`attributes` already lives on the dataclass (`py32_dfu.py:348` `attributes: int = 0`), set at
`:476`, and **has no consumer today**.

**Dialect predicate** (`py32_dfu.py:350-355`):
```python
    @property
    def is_dfuse(self) -> bool:
        """True when the device speaks the ST DfuSe dialect."""
        return self.dfu_version == DFUSE_VERSION or bool(
            self.name and self.name.startswith("@")
        )
```

**The C-5 hoist — the exact lines to move.** `flash()` (`py32_dfu.py:614-641`) ends:
```python
        if interface.is_dfuse:
            self._download_dfuse(interface, base, payload)
        else:
            logger.warning(
                "Device does not advertise DfuSe; using plain DFU 1.1 sequential "
                "download. The load address (0x%08X) is then decided by the "
                "bootloader, not by us.",
                base,
            )
            self._download_plain(interface, payload)

        logger.info("USB DFU download complete.")
        return True
```
The two `_finish()` calls to hoist are the **last statement of each downloader**:
```python
        self._finish(base, block, dfuse=True)     # py32_dfu.py:768, end of _download_dfuse
...
        self._finish(None, block, dfuse=False)    # py32_dfu.py:777, end of _download_plain
```
Signature to preserve (`py32_dfu.py:779`):
```python
    def _finish(self, base: Optional[int], next_block: int, dfuse: bool) -> None:  # noqa: UP045
        """End the download with a zero-length DNLOAD, then leave DFU mode.

        After a successful leave the device resets and disappears from the bus,
        so USB errors from this point on are expected and are *not* failures.
        """
```
→ Downloaders return `(base_or_None, next_block)`; `flash()` orders
**download → readback → `_finish()`**.

**D-13 envelope tightening — the existing guard** (`py32_dfu.py:644-653`):
```python
    def _check_envelope(self, base: int, length: int) -> None:
        """Refuse an image that cannot physically live in PY32F071xB flash."""
        if length == 0:
            raise ImageError("Refusing to flash an empty image.")
        if base < FLASH_BASE or base + length > FLASH_BASE + FLASH_SIZE:
            raise ImageError(
                f"Image spans 0x{base:08X}..0x{base + length:08X}, outside "
                f"PY32F071xB flash (0x{FLASH_BASE:08X}.."
                f"0x{FLASH_BASE + FLASH_SIZE:08X})."
            )
```
**Constraint:** `tests/test_py32_dfu.py:320` does `image.write_bytes(bytes(py32_dfu.FLASH_SIZE + 1))`
and expects `ImageError` matching `"outside"`. **Keep `FLASH_SIZE = 128 * 1024`** (`py32_dfu.py:108`)
as the *physical* constant and **add** `APP_REGION_END = 0x0801E000`; renaming/removing
`FLASH_SIZE` breaks that test.

**The pragma to remove (HOST-05, C-3)** — at `:375`, excluding statements `375` **and** `376`:
```python
    except ImportError as exc:  # pragma: no cover — environment-dependent
        raise PyusbMissingError(
            "USB firmware install needs pyusb. Install it with:\n"
            "    pip install 'firestarter[py32]'\n"
            "On Linux you also need libusb and permission to reach the device "
            "(a udev rule, or run as root); on Windows the DFU device needs a "
            "WinUSB driver."
        ) from exc
```
Assert on `pip install 'firestarter[py32]'`, `libusb`, `WinUSB`. **Never `Zadig`** (C-4 — the
word appears nowhere in the file). The two other pragmas at `:659-660` / `:665-666` (`_dev` /
`_index` guards) are **out of scope**.

---

### `tests/test_py32_dfu.py` — `_FakeUsbDevice` extension (HOST-03)

**Analog: the fake's own request-dispatch arm** (`tests/test_py32_dfu.py:47-69` @4ee64a1):
```python
class _FakeUsbDevice:
    """Records ctrl_transfer calls; answers DFU_GETSTATUS with a canned state."""

    def __init__(self, status=0, state=STATE_DFU_IDLE, poll_ms=0):
        self.calls = []
        self.status = status
        self.state = state
        self.poll_ms = poll_ms

    def ctrl_transfer(self, bmRequestType, bRequest, wValue=0, wIndex=0, data=None):  # noqa: N803
        self.calls.append((bmRequestType, bRequest, wValue, wIndex, data))
        if bRequest == DFU_GETSTATUS:
            poll = self.poll_ms
            return bytes(
                [
                    self.status,
                    poll & 0xFF,
                    (poll >> 8) & 0xFF,
                    (poll >> 16) & 0xFF,
                    self.state,
                    0,
                ]
            )
        return len(data) if data else 0
```
Add a `DFU_UPLOAD` arm in the same shape, returning `bytes` sliced from a settable backing
image and honouring the requested int length. (Today an UPLOAD falls through to
`return len(data) if data else 0` → **`0`**, because UPLOAD passes an int, not bytes.)

**Assertion-helper idiom to extend** (`:74-97`):
```python
    def dnloads(self):
        """Every DFU_DNLOAD as ``(wBlockNum, payload_bytes)``."""
        return [
            (value, bytes(data) if data else b"")
            for _, request, value, _, data in self.calls
            if request == DFU_DNLOAD
        ]
```
→ Add an `uploads()` helper in the same shape; the ordering assertion (readback strictly before
`_finish()`) is expressed over `self.calls` indices.

**`_interface()` factory to extend** (`:100-113`) — add `attributes=0` as a **defaulted**
parameter so all 58 existing tests keep passing:
```python
def _interface(device, name="@Internal Flash /0x08000000/64*002Kg", dfuse=True):
    return DfuInterface(
        device=device,
        vendor_id=0x1A86,
        product_id=0x8012,
        configuration=1,
        interface=0,
        alt_setting=0,
        protocol=py32_dfu.DFU_PROTOCOL_DFU_MODE,
        name=name if dfuse else "PY32 bootloader",
        transfer_size=64,
        dfu_version=DFUSE_VERSION if dfuse else 0x0110,
    )
```
> Consequence to record: with `attributes` defaulting to `0`, all 58 existing tests take the
> `SKIPPED_NO_UPLOAD` path. Because `flash()` keeps returning `bool` (D-10), every existing
> `assert flash(...) is True` still passes.

**C-6 signature drift:** the fake's 5th param is `data`, the real pyusb 1.3.1 names it
`data_or_wLength` and adds `timeout=None`. Consider aligning while extending.

---

### `.github/workflows/ci.yml` — `workflow_dispatch:` + `ci-py32` (D-01, D-02)

**Analog: the existing `ci` job in the same file.** Trigger block to extend:
```yaml
name: Host CI
on:
  push:
    branches:
    - main
    paths-ignore:
    - '**.md'
    ...
  pull_request:
    paths-ignore:
    ...
```
→ D-01 adds `workflow_dispatch:` **only**. Do **not** add the milestone branch to `push:`.

**Job shape to copy:**
```yaml
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      ...
      - name: Install package + test deps
        run: pip install -e .[test]
      ...
      - name: Run pytest with coverage
        run: pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70
```
`ci-py32` = checkout → setup-python `'3.11'` (match the primary job) → `pip install -e .[test,py32]`
→ `pytest tests/test_pyusb_api_surface.py -q`. Per the discretion default: **no** ruff / mypy /
coverage steps, and **no** codegen-drift steps.

**Existing comment-header convention at the top of the file** (phase-and-decision citations) —
follow it for the new job:
```yaml
# Phase 37 (D-07): install uses .[test] extra; gate steps: ruff check, ruff format --check, mypy watermark, pytest --cov.
```

---

### `pyproject.toml` — `[py32]` floor (D-19 / HOST-07)

Merged form (`pyproject.toml` @4ee64a1):
```toml
py32 = [
    "pyusb>=1.2.1",
]
```
→ `"pyusb>=1.3.1,<2"`. Sits under the existing `[project.optional-dependencies]` block
alongside `dev = ["pytest>=7.0"]`. `requires-python = ">=3.9"` is unchanged and pyusb 1.3.1
declares `Requires-Python: >=3.9.0`.

---

### `firestarter/firmware.py` — D-17 deviation comment

**Analog: the adjacent docstring style in the same file** (`firmware.py:95-97`):
```python
def flash_method(board: Optional[str]) -> str:
    """Return the install method for a board name (case-insensitive)."""
    return _BOARD_FLASH_METHODS.get((board or "").lower(), FLASH_METHOD_AVRDUDE)
```
Longer decision-recording docstring in the same file to imitate for tone
(`firmware.py:100-115`, `asset_candidates`) — it explains *why* the shape is what it is.

**Phase-128 contract — DO NOT TOUCH:**
```python
    if flash_method(board) == FLASH_METHOD_DFU:
        return [f"firestarter_{board}.hex", f"firestarter_{board}.bin"]
    return [f"firestarter_{board}.hex"]
```

---

### `127-NONREGRESSION.md` (new · evidence artifact)

**Analog:** `.planning/phases/126-…/126-NONREGRESSION.md`, whose section structure is:
```
# Phase 126 Non-Regression Sweep — closing plan (126-12)
## 1. The claim, as precise statements
## 2. The baseline, as recorded and as re-verified
## 3. The gate table — command, expected, observed
###   Firmware repo (`/workspaces/firestarter`)
###   Host repo (`/workspaces/firestarter_app`) — the … gate set
###   Host repo — hygiene and full-suite rows, plus the skip census
###   Meta repo
###   ARM row (re-queried read-only in this session)
## 4. Success criteria — one subsection each, quoting the ROADMAP verbatim
###   Criterion 1 … Criterion 5
## 5. Decision coverage — all nineteen, D-01…D-19
## 6. Informational findings carried forward
## 7. Claim ceiling
## Sweep Summary
```
`125-NONREGRESSION.md` uses the same 1/2 opening and then `## Criterion N` at top level, plus
`## Non-regression rows`, `## The claim gate, run for real, target named explicitly`,
`## Sweep Summary`. **Use 126's shape** (nearest neighbour, same nineteen-decision count —
Phase 127 also has D-01…D-19).

Phase-127-specific rows the artifact must carry (from CONTEXT/RESEARCH):
- D-04's recorded-not-gated collected count (`1216` merged; re-measured at evidence time), with
  the verbatim `pytest --collect-only` trailer.
- C-8's measurement: full suite under **pyusb-present** = 1213 passed / 3 skipped / 0 failed,
  identical to pyusb-absent → D-02's "accepted cost" measures as **zero today**.
- C-1's zero-fixup merge measurement with its reproduction command.
- D-17's accepted deviation (`flash_method()` router; `_install_with_avrdude` untouched;
  `avrdude-mcu-detection-fallback` todo reviewed and **not** folded).
- The mock-only ceiling on HOST-03, in a form Phase 130's CLOSE-02 honesty ledger can cite.
- The operator-dispatched `ci-py32` workflow-run URL (D-01, `autonomous: false` plan).
- The sibling-layout requirement (`/workspaces/firestarter_app` + `firestarter` sibling), because
  a wrongly-named directory produces 6 spurious failures.

---

## Shared Patterns

### Cross-repo binding (apply to: `test_py32_flash_map_host.py`)
**Source:** `firestarter_app/tests/fw_presence.py:102,118-139`
```python
requires_fw = pytest.mark.skipif(not FW_REPO_PRESENT, reason=FW_ABSENT_REASON)


class MissingScanTargetError(Exception):
    """Raised when the firmware repo IS present but a named path under it
    is not. ..."""


def fw_path(*parts: str) -> Path:
    resolved = FW_ROOT.joinpath(*parts)
    if FW_REPO_PRESENT and not resolved.exists():
        raise MissingScanTargetError(
            f"{resolved} does not exist, but the firmware repo IS present "
            f"(marker found at {FW_REPO_MARKER}). This scan target was "
            "renamed or moved -- update this path (or the cross-repo "
            "scan-path inventory) rather than removing or bypassing this "
            "gate."
        )
    return resolved
```
Never hand-build `Path(__file__).parent.parent.parent / "firestarter" / ...`.

### Skip-reason discipline (apply to: every new test module)
**Source:** `firestarter_app/tests/test_skip_census.py:110-141`
Allow-list is exactly four entries, matched by **prefix** (`str.startswith`), with
`FW_ABSENT_REASON` imported rather than re-typed:
```python
ALLOWED_SKIP_REASONS: frozenset[str] = frozenset(
    {
        FW_ABSENT_REASON,
        "firestarter entry point not found on PATH",
        "meta-repo ledger not available at",
        "EVIDENCE.json not found at",
    }
)
```
**No plan in this phase adds a fifth entry.** D-05, D-07 and D-14 each need none (measured).
`test_skip_census.py::test_no_pinned_skip_count` also enforces D-04's no-pinned-count rule.

### Independent-oracle assertion (apply to: `test_dfu_opcode_anchors.py`, `test_py32_flash_map_host.py`)
Write the expected value as a module-level constant with a **citing comment naming the external
source**, then assert the module's constant equals it — never import-and-compare, never derive
the expectation from the thing under test. Precedent: `_CRC32_KAT_EXPECTED = 0xCBF43926`
(126 D-05).

### Non-vacuity before comparison (apply to: any scanning/parsing test)
Prove the antecedent is non-empty and fail with a message that says *"would be vacuously true"*
**before** evaluating the real assertion. Precedent excerpts above from
`firestarter/tests/test_py32_flash_map.py:678-684, 771-782`.

### Two-layer channel gating (apply to: `cli_handlers.py`, `py32_dfu.py` if any new surface)
CLI layer (`_PY32_ENABLED`, import-time) **and** service choke point
(`firmware.py:_install_with_dfu` → `is_board_available` / `beta_only_message`). The gate reads
**no environment** and fails **closed** (`channel.py:37-58`) — do not add an env override "for
testing".

### Error-to-exit-code chain (apply to: D-11 `MISMATCH`)
`DfuProtocolError` (subclass of `DfuError`) → `_install_with_dfu`'s
`except DfuError as e: raise FirmwareOperationError(str(e)) from e` → `map_typed_errors`
decorator (`cli_handlers.py:144+`) → `ClickException` → exit 1. No new plumbing required.

### Test-module docstring convention (apply to: all new test modules)
Every analog opens with the MIT header block, then a paragraph naming the **phase, plan and
decision ID** the module discharges, and *why* the mechanism was chosen over the rejected one.
See `tests/test_skip_census.py:1-90`, `tests/fw_presence.py:1-63`,
`tests/test_revision_constants_parity.py:1-80`.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `tests/test_pyusb_api_surface.py` | test (optional-dep integration) | request-response | **No test in this repo is gated on an optional dependency.** All existing conditional tests gate on *cross-repo file presence* (`requires_fw`) or *CLI-on-PATH*, never on an importable extra. The planner must invent the declaration; the honest options are (a) a module-level `pytest.importorskip("usb")` — but that emits a skip reason **not** in `ALLOWED_SKIP_REASONS`, which `test_skip_census.py` would flag, or (b) **run the module only in the `ci-py32` job** with no marker at all, and keep it out of the primary leg via an explicit path argument or `--ignore`. **(b) is the shape D-02 already describes** (`ci-py32` runs *only* the pyusb-API-surface tests) and adds no skip reason. Flag this explicitly — it is the one genuinely undecided mechanism in the phase. |
| `tests/test_py32_packaging.py` (TOML parsing half) | test (config) | file-I/O | **No test in `tests/` parses `pyproject.toml`; there is no `tomllib`/`tomli` import anywhere in the repo** (measured). `tomllib` is stdlib only from py3.11 and the project floor is py3.9, so a stdlib parse is not portable and `tomli` is not a dependency. Recommend a **regex/substring scan** of `pyproject.toml` text for `pyusb>=1.3.1,<2` inside the `py32 = [` block — consistent with the repo's existing source-scanning gates (`test_revision_constants_parity.py`'s `#define` extractor is the nearest idiom) and adds no dependency. |
| `firestarter/py32_dfu.py` — `verify_result` **enum** | service | — | **`enum` is imported nowhere in `firestarter/` or `tests/`.** The only in-repo result-constant precedent is module-level strings + a dict router (`firmware.py:79-85`). Not a blocker — stdlib `enum.Enum` is py39-safe — but the planner must state the choice, since it introduces a construct with zero precedent. `StrEnum` is **py3.11+** and must not be used. |

---

## Metadata

**Analog search scope:**
`/workspaces/firestarter_app/{firestarter,tests,.github/workflows}` (working tree + `git show 4ee64a1:`),
`/workspaces/firestarter/tests/`, `/workspaces/.planning/phases/{125,126}-*/`.

**Files read (analog sources):**
- `/workspaces/firestarter/tests/test_py32_flash_map.py`
- `/workspaces/firestarter/tests/test_config_storage_dualslot.py`
- `/workspaces/firestarter_app/tests/fw_presence.py`
- `/workspaces/firestarter_app/tests/test_skip_census.py`
- `/workspaces/firestarter_app/tests/test_sdp_bus_config_drift.py`
- `/workspaces/firestarter_app/tests/test_revision_constants_parity.py`
- `/workspaces/firestarter_app/.github/workflows/ci.yml`
- `/workspaces/firestarter_app/pyproject.toml`
- `@4ee64a1`: `firestarter/py32_dfu.py`, `firestarter/cli_handlers.py`, `firestarter/channel.py`, `firestarter/firmware.py`, `tests/test_py32_dfu.py`
- `/workspaces/.planning/phases/126-…/126-NONREGRESSION.md`, `/workspaces/.planning/phases/125-…/125-NONREGRESSION.md`

**Read-only compliance:** no source file modified; no branch checked out; no merge performed;
no package installed. `4ee64a1` content accessed via `git show` only.

**Pattern extraction date:** 2026-08-01
