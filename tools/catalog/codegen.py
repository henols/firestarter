#!/usr/bin/env python3
"""
Firestarter v1.2 log-message catalog codegen.

Reads tools/catalog/messages.toml (or a vendored copy in a sub-repo's
tools/catalog/ directory) and emits one of two deterministic outputs:

  --language cpp        -> messages.h   (header guard, severity defines,
                                         MSG_* ID defines)
  --language python     -> messages.py  (severity codes, MSG_* ID constants,
                                         MessageDef dataclass, CATALOG dict)

An earlier revision emitted a third output
(`--language cpp-table` -> messages.c) holding a 256-byte PROGMEM table
backing a `MSG_PARAM_COUNT(id)` macro. The firmware never wired up a
caller for it (every emit-site already passes its param_count explicitly),
so the table cost ~256 B of Leonardo flash for no functional benefit.
Dropped to reclaim that space; the cpp-table emitter and
messages.c are gone from the codegen surface.

Determinism contract: two consecutive runs against the same catalog
file produce byte-identical output. Achieved by:
  - sorting messages by id ascending before emission
  - no timestamps, hostnames, or hashes in the banner
  - LF line endings via Path.write_text(..., newline='\n')
  - upper-case 2-digit hex literals ("0x%02X")
  - explicit dict iteration via sorted(...)

Validation: the --check flag runs the full 10-rule catalog
validator and exits 1 on any violation. Validation also runs unconditionally
before emission, so an invalid catalog never produces output.

Stdlib only (Python 3.11+ for tomllib).
"""

import argparse
import re
import sys
import tomllib
from pathlib import Path

# ===========================================================================
# 1. CONFIGURATION
# ===========================================================================

SEVERITY_CODES = {
    "OK":    0x01,
    "INIT":  0x02,
    "MAIN":  0x03,
    "END":   0x04,
    "INFO":  0x05,
    "WARN":  0x06,
    "ERROR": 0x07,
    "DATA":  0x08,
}
VALID_SEVERITIES = tuple(SEVERITY_CODES)

PARAM_TYPE_BYTES = {
    "u8":        1,
    "u16":       2,
    "u24":       3,
    "u32":       4,
    "i8":        1,
    "i16":       2,
    "i32":       4,
    # ascii_str is variable length on the wire (None = no fixed byte count;
    # the host catalog stores param_bytes=-1 for it).
    "ascii_str": None,
    # bytes is a raw payload; no fixed wire-byte count. Used for MSG_DATA_CHUNK
    # (chip-read streaming payload) and MSG_DEBUG sub-payload. No printf specifier
    # is emitted for bytes params — the host decoder handles them as raw bytes.
    "bytes":     None,
}
VALID_PARAM_TYPES = tuple(PARAM_TYPE_BYTES)

VALID_RENDERS = (
    "dec", "hex", "hex_byte", "hex_word", "hex_addr", "hex_dword",
    "signed_dec", "ascii_char", "ascii_str",
)

DEFAULT_RENDER_BY_TYPE = {
    "u8":        "dec",
    "i8":        "signed_dec",
    "u16":       "dec",
    "i16":       "signed_dec",
    "u24":       "hex_addr",
    "u32":       "hex",
    "i32":       "signed_dec",
    "ascii_str": "ascii_str",
    # bytes is a raw payload; rendered as a hex dump by the host if needed.
    "bytes":     "hex",
}

VALID_WIRE_FORMATS = ("id_frame", "text")
NAME_PATTERN = re.compile(r"^MSG_[A-Z][A-Z0-9_]*$")
# Pattern for debug sub-ID names in the [debug] section (B-03).
DBG_PATTERN = re.compile(r"^DBG_[A-Z][A-Z0-9_]*$")

# printf-style specifier matcher. Matches one specifier (excluding "%%").
# Specifier grammar (subset used in the catalog):
#   % [flags] [width] [length] type
# where:
#   flags   = '#' | '0'    (single optional)
#   width   = one or more digits
#   length  = 'l' | 'h'    (single optional)
#   type    = d | u | x | X | s | c
# Examples covered: %d %u %s %c %lu %lx %ld %02x %06x %#04x %02X %06lx %04x %lx
PRINTF_SPEC_RE = re.compile(r"%(?:%|[#0]?[0-9]*[lh]?[duxXsc])")

# 24-byte total wire-param budget for non-ascii_str messages (rule 10).
PARAM_BUDGET_BYTES = 24

CPP_BANNER_TEMPLATE = (
    "/*\n"
    " * Project Name: Firestarter\n"
    " * Copyright (c) 2026 Henrik Olsson\n"
    " *\n"
    " * Permission is hereby granted under MIT license.\n"
    " *\n"
    " * Firestarter -- v1.2 log-message catalog ({side})\n"
    " *\n"
    " * DO NOT EDIT, and do not regenerate from this repository.\n"
    " * Generated in the henols/firestarter meta repo by its\n"
    " * tools/catalog/codegen.py from tools/catalog/messages.toml,\n"
    " * then synced here. Edit the catalog there and re-sync.\n"
    " *\n"
    " * Catalog version: {version}\n"
    " * Total messages: {count}\n"
    " */\n"
)

PY_BANNER_TEMPLATE = (
    '"""\n'
    "Project Name: Firestarter\n"
    "Copyright (c) 2026 Henrik Olsson\n"
    "\n"
    "Permission is hereby granted under MIT license.\n"
    "\n"
    "Firestarter -- v1.2 log-message catalog (host side)\n"
    "\n"
    "DO NOT EDIT, and do not regenerate from this repository.\n"
    "Generated in the henols/firestarter meta repo by its\n"
    "tools/catalog/codegen.py from tools/catalog/messages.toml,\n"
    "then synced here. Edit the catalog there and re-sync.\n"
    "\n"
    "Catalog version: {version}\n"
    "Total messages: {count}\n"
    '"""\n'
)


# ===========================================================================
# 2. CATALOG VALIDATION
# ===========================================================================

class CatalogError(Exception):
    """Raised by validate_catalog() on any rule violation."""


def _count_printf_specs(format_str):
    """Count printf specifiers in format_str, excluding literal '%%'."""
    n = 0
    for m in PRINTF_SPEC_RE.finditer(format_str):
        if m.group(0) != "%%":
            n += 1
    return n


def _validate_entry(entry, section, id_word, name_word, name_pattern,
                    seen_ids, seen_names, reserved_names=None):
    """Rules shared by [[messages]] and [[debug.messages]]: id (1/D1), name
    (2/D2), format (3/D3), params (4/D4), param types (5/D5) and renders
    (6/D6). `section`, `id_word` and `name_word` name the entry, its id and
    its name in error messages ("entry", "ID", "name" for the main catalog).
    Return (id, name, format, params)."""
    label = entry.get("name", "<no name>")
    mid = entry.get("id")
    if mid is None:
        raise CatalogError(f"Missing 'id' field in {section}: {entry!r}")
    if not isinstance(mid, int) or isinstance(mid, bool):
        raise CatalogError(
            f"Field 'id' must be an integer; got {type(mid).__name__} "
            f"({mid!r}) in {section} {label}"
        )
    if mid < 0 or mid > 255:
        raise CatalogError(
            f"{id_word} out of range [0, 255]: 0x{mid:X} in {section} {label}"
        )
    where = f"{id_word} 0x{mid:02X}"
    if mid in seen_ids:
        raise CatalogError(
            f"Duplicate {where}: '{label}' conflicts with prior "
            f"'{seen_ids[mid]}'"
        )

    name = entry.get("name")
    if name is None or not isinstance(name, str):
        raise CatalogError(f"Missing or non-string 'name' for {where}")
    if not name_pattern.match(name):
        raise CatalogError(
            f"Invalid name format for {where}: '{name}' "
            f"(must match {name_pattern.pattern})"
        )
    if name in seen_names:
        raise CatalogError(
            f"Duplicate {name_word} '{name}' at {where} "
            f"(prior 0x{seen_names[name]:02X})"
        )
    if reserved_names and name in reserved_names:
        raise CatalogError(
            f"{name_word.capitalize()} '{name}' at {where} collides with main-catalog name at "
            f"0x{reserved_names[name]:02X}"
        )
    where = f"{where} ({name})"

    fmt = entry.get("format")
    if not isinstance(fmt, str) or fmt == "":
        raise CatalogError(f"Missing or empty 'format' for {where}")

    params = entry.get("params")
    if not isinstance(params, list):
        raise CatalogError(f"Field 'params' must be a list for {where}")
    for i, p in enumerate(params):
        if not isinstance(p, dict):
            raise CatalogError(f"params[{i}] must be a table in {where}")
    for i, p in enumerate(params):
        ptype = p.get("type")
        if ptype not in VALID_PARAM_TYPES:
            raise CatalogError(
                f"Invalid param type '{ptype}' at params[{i}] in {where}. "
                f"Allowed: {sorted(VALID_PARAM_TYPES)}"
            )
    for i, p in enumerate(params):
        r = p.get("render")
        if r is not None and r not in VALID_RENDERS:
            raise CatalogError(
                f"Invalid render '{r}' at params[{i}] in {where}. "
                f"Allowed: {sorted(VALID_RENDERS)}"
            )
    return mid, name, fmt, params


def _validate_params_fit(where, fmt, params, check_specs):
    """Rule 9/D7: the printf-specifier count matches the non-bytes param count
    ('bytes' params are raw payload with no printf representation). Rule
    10/D8: fixed-width params fit the 24-byte budget, so the largest
    fixed-shape frame fits the AVR's 64-byte UART TX buffer (4 magic + 1 len
    + 1 id + 24 params + 1 crc + 1 nl = 32 bytes)."""
    if check_specs:
        spec_count = _count_printf_specs(fmt)
        non_bytes_count = sum(1 for p in params if p.get("type") != "bytes")
        if spec_count != non_bytes_count:
            raise CatalogError(
                f"Format-vs-param-count mismatch for {where}: format has "
                f"{spec_count} printf specifier(s), params has "
                f"{non_bytes_count} non-bytes params (total params: "
                f"{len(params)}). format={fmt!r}"
            )
    fixed_bytes = sum(PARAM_TYPE_BYTES[p["type"]] or 0 for p in params)
    if fixed_bytes > PARAM_BUDGET_BYTES:
        raise CatalogError(
            f"Param byte budget exceeded for {where}: "
            f"{fixed_bytes} > {PARAM_BUDGET_BYTES}"
        )


def validate_catalog(catalog):
    """Run all 10 validation rules. Raise CatalogError on first failure."""
    if not isinstance(catalog, dict):
        raise CatalogError("Top-level catalog must be a TOML table.")

    meta = catalog.get("catalog")
    if not isinstance(meta, dict) or "version" not in meta:
        raise CatalogError("Missing [catalog] table or [catalog].version key.")
    if not isinstance(meta["version"], int):
        raise CatalogError("[catalog].version must be an integer.")

    messages = catalog.get("messages")
    if not isinstance(messages, list) or not messages:
        raise CatalogError("Missing or empty [[messages]] array of tables.")

    seen_ids = {}
    seen_names = {}
    for msg in messages:
        if not isinstance(msg, dict):
            raise CatalogError("Every [[messages]] entry must be a TOML table.")
        mid, name, fmt, params = _validate_entry(
            msg, "entry", "ID", "name", NAME_PATTERN, seen_ids, seen_names)
        where = f"ID 0x{mid:02X} ({name})"

        # Rule 7: severity valid
        sev = msg.get("severity")
        if sev not in VALID_SEVERITIES:
            raise CatalogError(
                f"Invalid severity '{sev}' for {where}. "
                f"Allowed: {list(VALID_SEVERITIES)}"
            )

        # Rule 8: wire_format valid; text entries must have empty params
        wf = msg.get("wire_format", "id_frame")
        if wf not in VALID_WIRE_FORMATS:
            raise CatalogError(
                f"Invalid wire_format '{wf}' for {where}. "
                f"Allowed: {list(VALID_WIRE_FORMATS)}"
            )
        if wf == "text" and len(params) != 0:
            raise CatalogError(
                f"wire_format=text entries must have params=[] "
                f"({where} has {len(params)} params)"
            )

        _validate_params_fit(where, fmt, params, check_specs=wf == "id_frame")
        seen_ids[mid] = name
        seen_names[name] = mid

    # [debug] section: the same rules in the DBG_* namespace (D1-D8). Debug
    # entries are always id_frame and carry no severity of their own.
    seen_dbg_ids = {}
    seen_dbg_names = {}
    for dbg in catalog.get("debug", {}).get("messages", []):
        if not isinstance(dbg, dict):
            raise CatalogError("Every [[debug.messages]] entry must be a TOML table.")
        did, dname, dfmt, dparams = _validate_entry(
            dbg, "[[debug.messages]] entry", "debug sub_id", "debug name", DBG_PATTERN,
            seen_dbg_ids, seen_dbg_names, reserved_names=seen_names)
        _validate_params_fit(f"[[debug.messages]] id 0x{did:02X} ({dname})",
                             dfmt, dparams, check_specs=True)
        seen_dbg_ids[did] = dname
        seen_dbg_names[dname] = did

    return True


# ===========================================================================
# 3. HELPERS
# ===========================================================================

def _param_wire_bytes(params):
    """Return integer wire-byte count for fixed-shape params, or None when any
    param is variable-length (ascii_str, bytes)."""
    total = 0
    for p in params:
        w = PARAM_TYPE_BYTES.get(p["type"])
        if w is None:
            return None  # variable-length present
        total += w
    return total


def _load_catalog(catalog_path):
    text = catalog_path.read_text(encoding="utf-8")
    return tomllib.loads(text)


def _sorted_messages(catalog):
    return sorted(catalog["messages"], key=lambda m: m["id"])


def _message_def(entry, severity_expr, wire_format):
    """Render one `0xNN: MessageDef(...)` entry of a Python catalog dict."""
    params = tuple(
        f'("{p["type"]}", "{p.get("render") or DEFAULT_RENDER_BY_TYPE[p["type"]]}")'
        for p in entry["params"]
    )
    if len(params) == 1:
        params_repr = f"({params[0]},)"
    else:
        params_repr = "(" + ", ".join(params) + ")"
    # -1 marks variable length on the host side, so callers can tell
    # "0 fixed bytes" from "variable".
    wb = _param_wire_bytes(entry["params"])
    param_bytes = -1 if wb is None else wb
    # Escape for a Python string literal. Format strings are ASCII printf
    # strings.
    fmt_escaped = entry["format"].replace("\\", "\\\\").replace('"', '\\"')
    return (
        f"    0x{entry['id']:02X}: MessageDef(\n"
        f"        id=0x{entry['id']:02X},\n"
        f'        name="{entry["name"]}",\n'
        f"        severity={severity_expr},\n"
        f'        format="{fmt_escaped}",\n'
        f"        params={params_repr},\n"
        f"        param_bytes={param_bytes},\n"
        f'        wire_format="{wire_format}",\n'
        f"    ),\n"
    )


# ===========================================================================
# 4. EMITTERS
# ===========================================================================

def emit_cpp_header(catalog):
    """Render messages.h source text."""
    version = catalog["catalog"]["version"]
    messages = _sorted_messages(catalog)
    count = len(messages)
    debug_messages = sorted(
        catalog.get("debug", {}).get("messages", []),
        key=lambda m: m["id"],
    )

    parts = []
    parts.append(CPP_BANNER_TEMPLATE.format(
        side="C++ firmware side",
        version=version,
        count=count,
    ))
    parts.append("\n")
    parts.append("#ifndef __MESSAGES_H__\n")
    parts.append("#define __MESSAGES_H__\n")
    parts.append("\n")
    parts.append("#ifdef __cplusplus\n")
    parts.append('extern "C" {\n')
    parts.append("#endif\n")
    parts.append("\n")
    parts.append("#include <stdint.h>\n")
    parts.append("#include <avr/pgmspace.h>\n")
    parts.append("\n")
    parts.append("// --- Severity codes (mirrors host catalog) ---\n")
    for sev in VALID_SEVERITIES:
        parts.append(
            f"#define MSG_SEVERITY_{sev:<6}0x{SEVERITY_CODES[sev]:02X}\n"
        )
    parts.append("\n")
    parts.append("// --- Message IDs (sorted ascending) ---\n")
    # Width: longest name + 2 chars for alignment.
    max_name_len = max(len(m["name"]) for m in messages)
    name_col = max_name_len + 2
    for m in messages:
        parts.append(
            f"#define {m['name']:<{name_col}}0x{m['id']:02X}\n"
        )
    # --- Debug sub-IDs (sorted ascending) ---
    if debug_messages:
        parts.append("\n")
        parts.append("// --- Debug sub-IDs (sorted ascending) ---\n")
        # Use a separate alignment column computed over DBG_* names only, so
        # a long DBG_* name does not shift the MSG_* block above.
        max_dbg_name_len = max(len(d["name"]) for d in debug_messages)
        dbg_name_col = max_dbg_name_len + 2
        for d in debug_messages:
            parts.append(
                f"#define {d['name']:<{dbg_name_col}}0x{d['id']:02X}\n"
            )
    parts.append("\n")
    parts.append("#ifdef __cplusplus\n")
    parts.append("}\n")
    parts.append("#endif\n")
    parts.append("\n")
    parts.append("#endif  // __MESSAGES_H__\n")
    return "".join(parts)


def emit_python(catalog):
    """Render messages.py source text."""
    version = catalog["catalog"]["version"]
    messages = _sorted_messages(catalog)
    count = len(messages)
    debug_messages = sorted(
        catalog.get("debug", {}).get("messages", []),
        key=lambda m: m["id"],
    )

    parts = []
    parts.append(PY_BANNER_TEMPLATE.format(version=version, count=count))
    parts.append("\n")
    parts.append("from dataclasses import dataclass\n")
    parts.append("\n")
    parts.append("# --- Severity codes (mirrors firmware) ---\n")
    for sev in VALID_SEVERITIES:
        parts.append(f"SEVERITY_{sev} = 0x{SEVERITY_CODES[sev]:02X}\n")
    parts.append("\n")
    parts.append("SEVERITY_LABEL = {\n")
    for sev in VALID_SEVERITIES:
        parts.append(f'    SEVERITY_{sev}: "{sev}",\n')
    parts.append("}\n")
    parts.append("\n")
    parts.append("\n")
    parts.append("@dataclass(frozen=True)\n")
    parts.append("class MessageDef:\n")
    parts.append("    id: int\n")
    parts.append("    name: str\n")
    parts.append("    severity: int\n")
    parts.append("    format: str\n")
    parts.append("    params: tuple[tuple[str, str], ...]\n")
    parts.append("    param_bytes: int\n")
    parts.append("    wire_format: str\n")
    parts.append("\n")
    parts.append("\n")
    parts.append("# --- ID constants (sorted ascending) ---\n")
    for m in messages:
        parts.append(f"{m['name']} = 0x{m['id']:02X}\n")
    parts.append("\n")
    parts.append("\n")
    parts.append("# --- Catalog lookup ---\n")
    parts.append("CATALOG: dict[int, MessageDef] = {\n")
    for m in messages:
        parts.append(_message_def(
            m, f"SEVERITY_{m['severity']}", m.get("wire_format", "id_frame")))
    parts.append("}\n")

    # --- Debug sub-ID constants and DEBUG_CATALOG (B-03) ---
    if debug_messages:
        parts.append("\n\n")
        parts.append("# --- Debug sub-ID constants (sorted ascending) ---\n")
        for d in debug_messages:
            parts.append(f"{d['name']} = 0x{d['id']:02X}\n")

        parts.append("\n\n")
        parts.append("# --- Debug sub-ID catalog lookup ---\n")
        parts.append("DEBUG_CATALOG: dict[int, MessageDef] = {\n")
        # Debug entries use severity=SEVERITY_DATA (the MSG_DEBUG band) and
        # are always id_frame.
        for d in debug_messages:
            parts.append(_message_def(d, "SEVERITY_DATA", "id_frame"))
        parts.append("}\n")

    return "".join(parts)


# ===========================================================================
# 5. CLI
# ===========================================================================

LANGUAGE_EMITTERS = {
    "cpp":       emit_cpp_header,
    "python":    emit_python,
}


def _build_argparser():
    p = argparse.ArgumentParser(
        prog="codegen.py",
        description="Generate firmware/host catalog artifacts from the "
                    "canonical messages.toml.",
    )
    p.add_argument("--catalog", required=True, type=Path,
                   help="Path to messages.toml (canonical or vendored copy).")
    p.add_argument("--target", type=Path, default=None,
                   help="Output path (required unless --check). "
                        "Suggested suffix: .h for cpp, .py for python.")
    p.add_argument("--language", choices=sorted(LANGUAGE_EMITTERS.keys()),
                   default=None,
                   help="Output language (required unless --check).")
    p.add_argument("--check", action="store_true",
                   help="Validate the catalog and exit 0/1. No files written.")
    return p


def main():
    args = _build_argparser().parse_args()

    if not args.catalog.is_file():
        print(f"ERROR: catalog file not found: {args.catalog}",
              file=sys.stderr)
        return 2

    try:
        catalog = _load_catalog(args.catalog)
    except tomllib.TOMLDecodeError as e:
        print(f"ERROR: failed to parse TOML in {args.catalog}: {e}",
              file=sys.stderr)
        return 1

    try:
        validate_catalog(catalog)
    except CatalogError as e:
        print(f"ERROR: catalog validation failed: {e}", file=sys.stderr)
        return 1

    if args.check:
        n = len(catalog["messages"])
        print(f"OK: catalog valid ({n} messages, version "
              f"{catalog['catalog']['version']}).")
        return 0

    if args.target is None or args.language is None:
        print("ERROR: --target and --language are required unless --check.",
              file=sys.stderr)
        return 2

    emitter = LANGUAGE_EMITTERS[args.language]
    output = emitter(catalog)

    args.target.parent.mkdir(parents=True, exist_ok=True)
    # newline='' + writing '\n' explicitly: LF endings guaranteed regardless
    # of platform (per Python docs for write_text + newline kwarg).
    args.target.write_text(output, encoding="utf-8", newline="\n")
    print(f"OK: wrote {args.target} ({args.language}, "
          f"{len(catalog['messages'])} messages).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
