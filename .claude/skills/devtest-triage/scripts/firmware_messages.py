"""Resolve a firmware error code to its symbolic message name.

Self-contained: stdlib only. This skill OWNS a transcribed copy of `CATALOG`
from the app's generated `firestarter_app/firestarter/messages.py`, rather
than importing it, so `devtest_issues.py show` keeps working when
`firestarter_app` is not checked out. `messages.py` in turn defines a SECOND
id-to-name table, `DEBUG_CATALOG` (`DBG_*` names) -- a separate id space that
collides with `CATALOG` on nine ids (0x00-0x05, 0x10, 0x20, 0x30, each
meaning something different in each table). A step's `error_code` is always
a `CATALOG` id (the firmware `response.id` captured off
`EpromOperationError.error_code`), so `MESSAGE_NAMES` below mirrors `CATALOG`
only. `DEBUG_CATALOG` is deliberately excluded, never merged in.

The cost of owning a copy is that nothing stops the two tables drifting
apart. `tests/test_firmware_messages.py`'s `CatalogDriftTest` is the
detector: it `ast.parse`s the app's `messages.py` (never imports it) and
compares. Do not "correct" a value here from memory -- if this table and the
app's `CATALOG` ever disagree, that is what the drift test is for.
"""

from __future__ import annotations

import re

# --- Owned copy of firestarter_app/firestarter/messages.py:CATALOG -------
# Transcribed by an ast extraction over the app's module (id -> `name=`
# keyword of each `MessageDef(...)` call), pasted here as a literal. Not
# regenerated at import time -- see the drift test for what keeps this in
# step with the source of truth.
MESSAGE_NAMES: dict[int, str] = {
    0x00: "MSG_NONE",
    0x01: "MSG_OK_READY",
    0x02: "MSG_OK_REQ_DATA",
    0x03: "MSG_OK_FW_VERSION",
    0x04: "MSG_OK_REV",
    0x05: "MSG_OK_CFG",
    0x10: "MSG_INIT_DONE",
    0x20: "MSG_MAIN_DONE",
    0x30: "MSG_END_DONE",
    0x40: "MSG_INFO_MAIN_START",
    0x41: "MSG_INFO_MAIN_DONE",
    0x42: "MSG_INFO_INIT_START",
    0x43: "MSG_INFO_END_START",
    0x51: "MSG_INFO_RETRIES",
    0x52: "MSG_INFO_REG_HEADER",
    0x53: "MSG_INFO_BIT_HEADER",
    0x54: "MSG_INFO_BIT_STR",
    0x55: "MSG_INFO_CE_OE",
    0x56: "MSG_INFO_ADDR",
    0x57: "MSG_INFO_ADDR_REMAP",
    0x58: "MSG_INFO_SKIPPING_ERASE",
    0x59: "MSG_INFO_SKIPPING_ERASE_MEM",
    0x5A: "MSG_INFO_FW",
    0x5B: "MSG_INFO_HW",
    0x5C: "MSG_INFO_PHYSICAL_HW",
    0x5D: "MSG_INFO_CMD",
    0x5E: "MSG_INFO_SDP_UNLOCK",
    0x5F: "MSG_INFO_SDP_UNLOCK_DONE_US",
    0x60: "MSG_INFO_SDP_LOCK",
    0x61: "MSG_INFO_SDP_LOCK_DONE_US",
    0x62: "MSG_INFO_PAGE_LOAD_WORST_US",
    0x80: "MSG_WARN_REV0_VPP_UNSUPPORTED",
    0x81: "MSG_WARN_VPP_LOW",
    0x82: "MSG_WARN_VPP_HIGH",
    0x83: "MSG_WARN_CHIP_ID_MISMATCH",
    0x84: "MSG_WARN_MEM_SIZE_TOO_SMALL",
    0x85: "MSG_WARN_FL4_BOOT_BLOCK_LOCKED",
    0x86: "MSG_WARN_SDP_UNLOCK_SKIPPED",
    0x87: "MSG_WARN_SDP_TBLC_EXCEEDED",
    0xA0: "MSG_ERR_BAD_JSON",
    0xA1: "MSG_ERR_NO_CMD",
    0xA2: "MSG_ERR_SETUP",
    0xA3: "MSG_ERR_PARSE_CFG",
    0xA4: "MSG_ERR_EMPTY_INPUT",
    0xA5: "MSG_ERR_NOT_SUPPORTED",
    0xA6: "MSG_ERR_NO_CHIP_ID",
    0xA7: "MSG_ERR_OUT_OF_RANGE",
    0xA8: "MSG_ERR_TIMEOUT",
    0xA9: "MSG_ERR_DATA_ERR_N",
    0xAA: "MSG_ERR_CMD_TIMEOUT",
    0xAB: "MSG_ERR_UNKNOWN_CMD",
    0xAC: "MSG_ERR_REV0_VPP_RD",
    0xAD: "MSG_ERR_CMD",
    0xAE: "MSG_ERR_PULSE_TOO_WIDE",
    0xAF: "MSG_ERR_VERIFY",
    0xB0: "MSG_ERR_NOT_BLANK",
    0xB1: "MSG_ERR_WRITE_FAILED",
    0xB2: "MSG_ERR_EEPROM_TIMEOUT",
    0xB3: "MSG_ERR_FL4_VERIFY_TIMEOUT",
    0xB4: "MSG_ERR_INTEL_VPP",
    0xB5: "MSG_ERR_INTEL_PROGRAM",
    0xB6: "MSG_ERR_INTEL_SR_TIMEOUT",
    0xB7: "MSG_ERR_OP_TIMEOUT",
    0xB8: "MSG_ERR_VPP_HIGH",
    0xB9: "MSG_ERR_CHIP_ID_MISMATCH",
    0xBA: "MSG_ERR_MEM_SIZE_TOO_SMALL",
    0xBB: "MSG_ERR_PROTOCOL_NOT_IMPLEMENTED",
    0xBC: "MSG_ERR_FL4_BOOT_BLOCK_LOCKED",
    0xBD: "MSG_ERR_MAX_PULSES",
    0xBE: "MSG_ERR_ENERGY_CAP",
    0xBF: "MSG_ERR_FL4_PAGE_SIZE",
    0xC0: "MSG_ERR_FL4_PAGE_ALIGN",
    0xE0: "MSG_DATA_PROGRESS",
    0xE1: "MSG_DATA_PROTECTION_STATUS",
    0xE2: "MSG_DATA_SENDING",
    0xE4: "MSG_DATA_VPP_VOLTAGE",
    0xE5: "MSG_DATA_VPE_VOLTAGE",
    0xE6: "MSG_DATA_CHUNK",
    0xF0: "MSG_DEBUG",
}

# A reported `error_name` must look like an identifier and stay short, or it
# is discarded outright -- this is what stops an unbounded or hostile string
# in a community-authored issue body from ever reaching stdout.
_NAME_RE = re.compile(r"^[A-Za-z0-9_]{1,40}$")


def _usable_name(reported_name: object) -> str | None:
    if not isinstance(reported_name, str):
        return None
    return reported_name if _NAME_RE.match(reported_name) else None


def resolve_error(code: object, reported_name: object = None) -> str:
    """Render one step's error cell per the DD-3 contract.

    Pure and total: no I/O, no subprocess, nothing raises. Every rejected
    input falls through to `-`, `?`, or the table's own answer -- never the
    untrusted value itself.

    | Input                                            | Cell                          |
    |---------------------------------------------------|-------------------------------|
    | `code` absent or `None`                            | `-`                           |
    | not an `int`, or a `bool`, or outside `0..255`     | `?`                           |
    | in the table, no usable `reported_name`            | `183 MSG_ERR_OP_TIMEOUT`      |
    | not in the table, no usable `reported_name`        | `183 unknown`                 |
    | usable `reported_name`, code not in the table      | `183 MSG_SOMETHING_NEW`       |
    | usable `reported_name` agrees with the table       | `183 MSG_ERR_OP_TIMEOUT`      |
    | usable `reported_name` disagrees with the table    | `183 MSG_SOMETHING (table: MSG_ERR_OP_TIMEOUT)` |
    """
    if code is None:
        return "-"
    # `bool` is a subclass of `int` in Python -- exclude it explicitly, or
    # `True` would silently resolve to id 1.
    if isinstance(code, bool) or not isinstance(code, int):
        return "?"
    if not 0 <= code <= 255:
        return "?"

    table_name = MESSAGE_NAMES.get(code)
    name = _usable_name(reported_name)

    if name is None:
        return f"{code} {table_name if table_name is not None else 'unknown'}"
    if table_name is None or name == table_name:
        return f"{code} {name}"
    return f"{code} {name} (table: {table_name})"
