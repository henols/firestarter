#!/usr/bin/env python3
"""append_evidence.py -- the deriving evidence-row writer (D-05).

D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It is authored and lives
only under .planning/milestones/v1.34-artifacts/tools/ in the meta repo. It must NEVER be copied into
firestarter/ or firestarter_app/ -- this phase changes no firmware and no host source.
Nothing here is imported by, or imports from, either sub-repo.

WHAT THIS TOOL EXISTS TO PREVENT
---------------------------------
Twelve positions x ~40 fields is 480 opportunities to transcribe a field from the wrong
position. `gate_record.py` checks shape and domain, not correctness -- a field copied from
the neighbouring position's provenance passes every check it makes. This tool is D-05's
mechanism, not a transcriber's discipline: of the 40 `EVIDENCE.jsonl` columns, exactly FIVE
are supplied by a human at all (`blank_state`, `verdict`, `anomalies`, and the two write
durations, plus an optional `--shield-note`). Every other column is DERIVED from this
position's own three source artifacts -- `provenance_<position_id>.json`,
`WRV-VERDICT_<position_id>.json` and the cell's `READBACK-VERDICT.json` -- cross-checked
against each other, against `bench/IMAGE-PLAN.json`, and against `rig-pins.json`, and a
disagreement anywhere in that cross-check set is refused BY NAME, accumulated across every
check in one pass, never on the first failure only.

`outcome` is the one column this tool computes and NEVER accepts as an input: `validated`
iff `wrv.sha_verdict_judged == "match"` and `wrv.verdict_disagreement` is falsy and
`wrv.size_violations` is empty; otherwise `skipped-with-reason`. This is the only place the
judged truth reaches the row, because `gate_record.py`'s own `check_cross_oracle()` reads
three keys (`written_image_sha256`, `read_sha256`, `app_dev_consistency_verdict`) that do
not exist in this schema and is therefore structurally inert against every row this tool
writes.

DELEGATION, NEVER RE-IMPLEMENTATION
-------------------------------------
This tool imports, via the `importlib.util.spec_from_file_location` sibling idiom, rather
than re-deriving:
  - `gate_record.py`'s `_NOT_MEASURED_RE` / `_is_acceptable_not_measured` /
    `check_required_fields` (the "not measured -- <reason>" anti-fabrication idiom), and
    `check_commands` (the argv allow-list + forbidden-flag re-parse) -- applied to this
    row's `commands` field, including anything merged from `--commands-extra`, BEFORE the
    row is written.
  - `render_evidence.py`'s `append_row_to_file()` for the write itself -- the record-key
    presence/extra-key rejection, outcome-domain check, duplicate-`position_id` refusal,
    the byte-unchanged-prefix re-read and the atomic temp-file + `os.replace` all live
    there. This tool never hand-rolls a JSONL append.

Neither this tool's `EVIDENCE.md` re-render nor its rendering logic exists here at all --
`render_evidence.append_row_to_file()`'s own `--append` branch returns BEFORE the render
path, and the paired `render_evidence.py --jsonl ... --target ...` re-render is a separate
command the calling procedure step runs in the same step; coupling it into this tool would
hide the `--check` gate's meaning.

PER-POSITION ARTIFACT LAYOUT (PD-1)
-------------------------------------
`--wrv` defaults to `<cell-dir>/WRV-VERDICT_<position-id>.json` -- NOT a `positions/<id>/`
subdirectory. `bench/.gitignore` is exactly `cells/*/reads/` and `cells/*/written.bin`; a
`positions/<id>/` layout would NOT be ignored and would silently commit up to 12 large
binaries. `--readback` stays CELL-level (`<cell-dir>/READBACK-VERDICT.json`, one per flash
event, written by `judge_readback.py` at PROCEDURE.md P-04), not per-position.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_MILESTONE_DIR = _HERE.parent
_DEFAULT_PINS = _MILESTONE_DIR / "rig-pins.json"
_DEFAULT_IMAGE_PLAN = _MILESTONE_DIR / "bench" / "IMAGE-PLAN.json"
_DEFAULT_JSONL = _MILESTONE_DIR / "bench" / "EVIDENCE.jsonl"

# Field order matches bench/EVIDENCE.jsonl's own _schema.record_keys exactly (40 columns:
# the 9-column locked core + the 31-column v1.34 extension set). This tool is responsible
# for producing every one of them; render_evidence.append_row_to_file() re-validates this
# set independently against the JSONL's own header before writing, so a drift here is
# caught at write time, not silently accepted.
RECORD_KEYS = [
    "chip", "family", "board", "shield", "blank_state", "op", "sha256", "verdict",
    "anomalies", "position_id", "cell_id", "cell_slug", "arm", "target_env",
    "board_signature", "controller_string", "shield_rev_declared", "fw_sha",
    "fw_readback_sha_judged", "fw_readback_sha_whole_flash",
    "fw_readback_judged_span_bytes", "host_arm_sha", "host_arm_porcelain_clean",
    "host_arm_file", "config_dir_sha", "interpreter", "dep_freeze_sha",
    "eeprom_calibration", "image_mask", "image_stamp_width", "image_sha", "read_count",
    "read_shas", "app_verdict_unjudged", "sha_verdict_judged", "verdict_disagreement",
    "write_duration_wallclock_s", "write_duration_app_reported_s", "commands", "outcome",
]

# Small, stable tool constants (T in RESEARCH.md's derivation-map source column) -- never
# re-derived from a sub-repo, never hand-transcribed per-row.
_CHIP_LABEL = {"w27c512": "EPROM_STD", "w29c020": "FLASH_5V_PAGE"}
_BOARD_LABEL = {
    "uno": "Arduino Uno",
    "uno328pb": "Arduino Uno (328PB, MiniCore)",
    "leonardo": "Arduino Leonardo",
}
# probe_board.py's own _SIGNATURE_TO_MCU table, inverted (probe_board.py:11-14, "measured
# 2026-08-19, direct signature read"). Duplicated here as a small, stable 3-entry constant
# rather than imported, because it is data this tool cross-checks a provenance FIELD
# against, not a check owned by another tool.
_MCU_SIGNATURE = {
    "atmega328p": "0x1e950f",
    "atmega328pb": "0x1e9516",
    "atmega32u4": "0x1e9587",
}

_SYMPTOM_KEYWORDS = (
    "mismatch", "disagreement", "disagree", "incomplete", "fail", "timeout", "error",
    "violation", "corrupt", "wrong", "missing", "short read", "hardware", "serial",
    "refused", "crash", "hang", "guard", "high", "no board", "no chip",
)


# ---------------------------------------------------------------------------
# Sibling reuse -- the house importlib.util.spec_from_file_location idiom
# (gate_record.py's own _load_check_arms(), mirrored at capture_provenance.py).
# ---------------------------------------------------------------------------


def _load_sibling(name: str):
    spec = importlib.util.spec_from_file_location(name, _HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _gate_record():
    return _load_sibling("gate_record")


def _render_evidence():
    return _load_sibling("render_evidence")


# ---------------------------------------------------------------------------
# Pure deriving/validating logic -- no subprocess, no device, no app invocation.
# Reads only pre-existing artifacts earlier procedure steps already produced.
# Exercised directly by --selftest.
# ---------------------------------------------------------------------------


def validate_position(
    position_id: str,
    provenance: dict,
    wrv: dict,
    readback: dict,
    image_plan_row: dict | None,
    pins: dict,
) -> list[str]:
    """Accumulate-then-report cross-checks across the position's three source artifacts,
    bench/IMAGE-PLAN.json and rig-pins.json. This is D-05's own argument made mechanical:
    a field transcribed from the WRONG position's provenance is refused by name here, which
    is exactly the failure gate_record.py structurally cannot see (it validates shape and
    domain of a single already-assembled record, never cross-position identity)."""
    violations: list[str] = []

    def _check(label: str, a: object, b: object) -> None:
        if a != b:
            violations.append(f"{label}: {a!r} != {b!r}")

    _check("position_id vs provenance.position_id", position_id, provenance.get("position_id"))
    _check("position_id vs wrv.position_id", position_id, wrv.get("position_id"))

    _check("wrv.written_sha vs provenance.image_sha", wrv.get("written_sha"), provenance.get("image_sha"))

    if image_plan_row is not None:
        _check("wrv.written_sha vs image_plan.sha256", wrv.get("written_sha"), image_plan_row.get("sha256"))
        _check("provenance.image_mask vs image_plan.mask", provenance.get("image_mask"), image_plan_row.get("mask"))
        _check(
            "provenance.image_stamp_width vs image_plan.stamp_width",
            provenance.get("image_stamp_width"), image_plan_row.get("stamp_width"),
        )
        _check("provenance.image_sha vs image_plan.sha256", provenance.get("image_sha"), image_plan_row.get("sha256"))

    _check("provenance.arm vs readback.flashed_arm", provenance.get("arm"), readback.get("flashed_arm"))
    _check("provenance.target_env vs readback.target", provenance.get("target_env"), readback.get("target"))
    _check(
        "provenance.fw_readback_sha_judged vs readback.sha_actual_judged",
        provenance.get("fw_readback_sha_judged"), readback.get("sha_actual_judged"),
    )
    _check(
        "provenance.fw_readback_sha_whole_flash vs readback.sha_whole_flash_unjudged",
        provenance.get("fw_readback_sha_whole_flash"), readback.get("sha_whole_flash_unjudged"),
    )

    arm = provenance.get("arm")
    arm_cfg = pins.get("arms", {}).get(arm)
    if arm_cfg is None:
        violations.append(f"rig-pins.json has no arms entry for arm {arm!r}")
    else:
        _check("provenance.fw_sha vs pins.arms[arm].fw_sha", provenance.get("fw_sha"), arm_cfg.get("fw_sha"))
        _check(
            "provenance.host_arm_sha vs pins.arms[arm].app_sha",
            provenance.get("host_arm_sha"), arm_cfg.get("app_sha"),
        )

    target_env = provenance.get("target_env")
    target_cfg = pins.get("targets", {}).get(target_env)
    if target_cfg is None:
        violations.append(f"rig-pins.json has no targets entry for target_env {target_env!r}")
    else:
        known_sig = _MCU_SIGNATURE.get(target_cfg.get("mcu"))
        if known_sig is not None:
            _check(
                "provenance.board_signature vs known signature for pins.targets[env].mcu",
                provenance.get("board_signature"), known_sig,
            )

    chip = provenance.get("chip")
    if chip not in pins.get("chips", {}):
        violations.append(f"rig-pins.json has no chips entry for chip {chip!r}")

    return violations


def _derive_outcome(wrv: dict) -> str:
    """Never accepted as input -- always derived. Outside this function, no code path may
    ever assign 'validated' to a row's outcome."""
    if (
        wrv.get("sha_verdict_judged") == "match"
        and not wrv.get("verdict_disagreement")
        and not wrv.get("size_violations")
    ):
        return "validated"
    return "skipped-with-reason"


def _names_symptom(text: object) -> bool:
    if not isinstance(text, str):
        return False
    lowered = text.lower()
    return any(k in lowered for k in _SYMPTOM_KEYWORDS)


def build_row(
    provenance: dict,
    wrv: dict,
    readback: dict,
    image_plan_row: dict,
    pins: dict,
    human: dict,
    position_id: str,
    commands: list,
    outcome: str,
) -> dict:
    """Pure assembly -- assumes validate_position() has already accumulated and the caller
    has confirmed there are no violations. Returns the full 40-column row, keys in
    RECORD_KEYS order. (Signature note: RESEARCH.md's proposed shape was `build_row(prov,
    wrv, readback, image_plan_row, pins, human) -> (row, violations)`; this tool splits
    cross-check accumulation into validate_position() -- called separately, before this
    function -- and keeps build_row() a pure, violation-free assembler taking the
    already-derived position_id/commands/outcome explicitly, so the selftest can exercise
    assembly and cross-checking independently.)"""
    chip = provenance.get("chip")
    target_env = provenance.get("target_env")
    chip_cfg = pins.get("chips", {}).get(chip, {})
    target_cfg = pins.get("targets", {}).get(target_env, {})

    family = "0x%02x (%s)" % (chip_cfg.get("algorithm", 0), _CHIP_LABEL.get(chip, "UNKNOWN"))
    board = "%s (%s)" % (_BOARD_LABEL.get(target_env, target_env), str(target_cfg.get("mcu", "")).upper())
    shield = "mounted, %s, %s seated" % (provenance.get("shield_rev_declared"), str(chip).upper())
    if human.get("shield_note"):
        shield = f"{shield} -- {human['shield_note']}"
    op = "write-read-verify: %s B write, %sx independent read, judged by full-device SHA against the written image (D-10/D-11/D-12)" % (
        wrv.get("expect_size"), wrv.get("read_count"),
    )

    values = {
        "chip": chip,
        "family": family,
        "board": board,
        "shield": shield,
        "blank_state": human["blank_state"],
        "op": op,
        "sha256": wrv.get("written_sha"),
        "verdict": human["verdict"],
        "anomalies": human["anomalies"],
        "position_id": provenance.get("position_id"),
        "cell_id": provenance.get("cell_id"),
        "cell_slug": provenance.get("cell_slug"),
        "arm": provenance.get("arm"),
        "target_env": target_env,
        "board_signature": provenance.get("board_signature"),
        "controller_string": provenance.get("controller_string"),
        "shield_rev_declared": provenance.get("shield_rev_declared"),
        "fw_sha": provenance.get("fw_sha"),
        "fw_readback_sha_judged": provenance.get("fw_readback_sha_judged"),
        "fw_readback_sha_whole_flash": provenance.get("fw_readback_sha_whole_flash"),
        "fw_readback_judged_span_bytes": readback.get("judged_span_bytes"),
        "host_arm_sha": provenance.get("host_arm_sha"),
        "host_arm_porcelain_clean": provenance.get("host_arm_porcelain_clean"),
        "host_arm_file": provenance.get("host_arm_file"),
        "config_dir_sha": provenance.get("config_dir_sha"),
        "interpreter": provenance.get("interpreter"),
        "dep_freeze_sha": provenance.get("dep_freeze_sha"),
        "eeprom_calibration": provenance.get("eeprom_calibration"),
        "image_mask": provenance.get("image_mask"),
        "image_stamp_width": provenance.get("image_stamp_width"),
        "image_sha": provenance.get("image_sha"),
        "read_count": wrv.get("read_count"),
        "read_shas": wrv.get("read_shas"),
        "app_verdict_unjudged": wrv.get("app_verdict_unjudged"),
        "sha_verdict_judged": wrv.get("sha_verdict_judged"),
        "verdict_disagreement": wrv.get("verdict_disagreement"),
        "write_duration_wallclock_s": human["write_duration_wallclock_s"],
        "write_duration_app_reported_s": human["write_duration_app_reported_s"],
        "commands": commands,
        "outcome": outcome,
    }
    return {k: values[k] for k in RECORD_KEYS}


# ---------------------------------------------------------------------------
# Artifact loading -- hard refusal, named path, distinct absent/unparseable branches
# (capture_provenance.py:300-328's read_readback_verdict() shape, generalised).
# ---------------------------------------------------------------------------


def _load_json(path: Path, label: str) -> tuple[bool, dict | None, str]:
    if not path.exists():
        return False, None, f"{label} not found at {path}"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, None, f"{label} at {path} could not be read: {exc}"
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return False, None, f"{label} at {path} is not valid JSON: {exc}"
    if not isinstance(data, dict):
        return False, None, f"{label} at {path} is not a JSON object"
    return True, data, ""


def _load_image_plan_row(path: Path, position_id: str) -> tuple[bool, dict | None, str]:
    ok, plan, detail = _load_json(path, "image plan")
    if not ok:
        return False, None, detail
    positions = plan.get("positions")
    if not isinstance(positions, list):
        return False, None, f"image plan at {path} has no top-level 'positions' list"
    for row in positions:
        if isinstance(row, dict) and row.get("position_id") == position_id:
            return True, row, ""
    return False, None, f"no image plan row found for position_id {position_id!r} in {path}"


def _read_text_or_dash(path_or_dash: str) -> tuple[bool, str | None, str]:
    if path_or_dash == "-":
        return True, sys.stdin.read(), ""
    p = Path(path_or_dash)
    if not p.exists():
        return False, None, f"file not found: {p}"
    try:
        return True, p.read_text(encoding="utf-8"), ""
    except OSError as exc:
        return False, None, f"could not read {p}: {exc}"


def _load_json_list(path: Path) -> tuple[bool, list | None, str]:
    if not path.exists():
        return False, None, f"--commands-extra file not found: {path}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, None, f"--commands-extra file unreadable/invalid JSON: {exc}"
    if not isinstance(data, list):
        return False, None, f"--commands-extra file {path} is not a JSON list"
    return True, data, ""


def _validate_duration(value: object, flag_name: str) -> tuple[bool, object, str]:
    gr = _gate_record()
    if gr._is_acceptable_not_measured(value):
        return True, value, ""
    try:
        return True, float(value), ""  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False, None, (
            f"{flag_name} value {value!r} is neither a float nor the "
            "'not measured — <reason>' shape"
        )


# ---------------------------------------------------------------------------
# process_position -- the whole load -> validate -> derive -> (write) pipeline, driven
# identically by main() and by --selftest so every negative leg exercises the real path.
# ---------------------------------------------------------------------------


def process_position(
    position_id: str,
    provenance_path: Path,
    wrv_path: Path,
    readback_path: Path,
    image_plan_path: Path,
    pins_path: Path,
    human: dict,
    jsonl_path: Path,
    commands_extra: list | None = None,
    dry_run: bool = False,
) -> tuple[int, list[str], dict | None]:
    violations: list[str] = []

    ok, pins, detail = _load_json(pins_path, "pins file")
    if not ok:
        violations.append(detail)
    ok, provenance, detail = _load_json(provenance_path, "provenance artifact")
    if not ok:
        violations.append(detail)
    ok, wrv, detail = _load_json(wrv_path, "WRV-VERDICT artifact")
    if not ok:
        violations.append(detail)
    ok, readback, detail = _load_json(readback_path, "READBACK-VERDICT artifact")
    if not ok:
        violations.append(detail)
    ok, image_plan_row, detail = _load_image_plan_row(image_plan_path, position_id)
    if not ok:
        violations.append(detail)

    if violations:
        return 1, violations, None

    gr = _gate_record()

    violations.extend(validate_position(position_id, provenance, wrv, readback, image_plan_row, pins))

    violations.extend(
        gr.check_required_fields(
            {
                "blank_state": human["blank_state"],
                "verdict": human["verdict"],
                "anomalies": human["anomalies"],
            },
            ["blank_state", "verdict", "anomalies"],
        )
    )

    wc_ok, wallclock_val, wc_detail = _validate_duration(human["write_duration_wallclock_s"], "--write-wallclock-s")
    if not wc_ok:
        violations.append(wc_detail)
    ar_ok, app_val, ar_detail = _validate_duration(human["write_duration_app_reported_s"], "--write-app-reported-s")
    if not ar_ok:
        violations.append(ar_detail)

    combined_commands = list(provenance.get("commands") or [])
    if commands_extra:
        combined_commands = combined_commands + list(commands_extra)
    violations.extend(gr.check_commands({"commands": combined_commands}, pins))

    outcome = _derive_outcome(wrv)
    if outcome == "skipped-with-reason" and not _names_symptom(human["verdict"]):
        violations.append(
            "outcome derives as 'skipped-with-reason' but --verdict-file names no observed "
            "symptom (P-H2 record contract)"
        )

    if violations:
        return 1, violations, None

    human_resolved = dict(human)
    human_resolved["write_duration_wallclock_s"] = wallclock_val
    human_resolved["write_duration_app_reported_s"] = app_val

    row = build_row(
        provenance, wrv, readback, image_plan_row, pins, human_resolved,
        position_id, combined_commands, outcome,
    )

    if dry_run:
        return 0, [], row

    re_mod = _render_evidence()
    try:
        re_mod.append_row_to_file(jsonl_path, row)
    except re_mod.RenderError as exc:
        return 1, [str(exc)], None

    return 0, [], row


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_argparser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--position-id", required=True, help="<cell_slug>__<arm>__<chip>, IMAGE-PLAN.json's primary key")
    ap.add_argument("--cell-dir", default=None, help="default: bench/cells/<cell_slug>")
    ap.add_argument("--provenance", default=None, help="default: <cell-dir>/provenance_<position-id>.json")
    ap.add_argument("--wrv", default=None, help="default: <cell-dir>/WRV-VERDICT_<position-id>.json (PD-1)")
    ap.add_argument("--readback", default=None, help="default: <cell-dir>/READBACK-VERDICT.json (cell-level)")
    ap.add_argument("--image-plan", default=str(_DEFAULT_IMAGE_PLAN))
    ap.add_argument("--pins", default=str(_DEFAULT_PINS))
    ap.add_argument("--jsonl", default=str(_DEFAULT_JSONL))
    ap.add_argument("--verdict-file", required=True, help="path or '-' for stdin")
    ap.add_argument("--anomalies-file", required=True, help="path or '-' for stdin")
    ap.add_argument("--blank-state", required=True, help="a real reading, or 'not measured — <reason>'")
    ap.add_argument("--shield-note", default=None, help="optional, appended to the derived shield column")
    ap.add_argument("--write-wallclock-s", required=True, help="FLOAT or 'not measured — <reason>'")
    ap.add_argument("--write-app-reported-s", required=True, help="FLOAT or 'not measured — <reason>'")
    ap.add_argument("--commands-extra", default=None, help="path to a JSON list merged after provenance.commands")
    ap.add_argument("--dry-run", action="store_true", help="print the assembled row, write nothing")
    ap.add_argument("--selftest", action="store_true")
    return ap


def main() -> int:
    # --selftest is scanned for BEFORE the full parse, deliberately: several arguments here
    # are required=True with no default (D-05's "exactly five human inputs, all required"),
    # so a normal ap.parse_args() would itself refuse `--selftest` alone with a
    # missing-required-argument error before this function got a chance to route to the
    # selftest, which carries no artifact/device arguments at all (capture_provenance.py's
    # own pre-parse variant, main():513-520).
    if "--selftest" in sys.argv[1:]:
        return _run_selftest()

    ap = build_argparser()
    args = ap.parse_args()

    cell_slug = args.position_id.split("__", 1)[0]
    cell_dir = Path(args.cell_dir) if args.cell_dir else (_MILESTONE_DIR / "bench" / "cells" / cell_slug)
    provenance_path = Path(args.provenance) if args.provenance else (cell_dir / f"provenance_{args.position_id}.json")
    wrv_path = Path(args.wrv) if args.wrv else (cell_dir / f"WRV-VERDICT_{args.position_id}.json")
    readback_path = Path(args.readback) if args.readback else (cell_dir / "READBACK-VERDICT.json")
    image_plan_path = Path(args.image_plan)
    pins_path = Path(args.pins)
    jsonl_path = Path(args.jsonl)

    pre_violations: list[str] = []
    ok, verdict_text, detail = _read_text_or_dash(args.verdict_file)
    if not ok:
        pre_violations.append(f"--verdict-file: {detail}")
        verdict_text = ""
    ok, anomalies_text, detail = _read_text_or_dash(args.anomalies_file)
    if not ok:
        pre_violations.append(f"--anomalies-file: {detail}")
        anomalies_text = ""

    commands_extra: list | None = None
    if args.commands_extra:
        ok, commands_extra, detail = _load_json_list(Path(args.commands_extra))
        if not ok:
            pre_violations.append(detail)

    if pre_violations:
        for v in pre_violations:
            print(f"FAIL: {v}", file=sys.stderr)
        return 1

    human = {
        "blank_state": args.blank_state,
        "verdict": verdict_text,
        "anomalies": anomalies_text,
        "write_duration_wallclock_s": args.write_wallclock_s,
        "write_duration_app_reported_s": args.write_app_reported_s,
        "shield_note": args.shield_note,
    }

    rc, violations, row = process_position(
        args.position_id, provenance_path, wrv_path, readback_path, image_plan_path,
        pins_path, human, jsonl_path, commands_extra=commands_extra, dry_run=args.dry_run,
    )

    if rc != 0:
        for v in violations:
            print(f"FAIL: {v}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(json.dumps(row, indent=2, ensure_ascii=False))
        return 0

    print(f"OK: appended position_id={args.position_id!r} outcome={row['outcome']!r} to {jsonl_path}")
    return 0


# ---------------------------------------------------------------------------
# --selftest: on-disk fixtures in a tempfile directory, accumulate-then-report. Every
# negative leg asserts on the NAMED reason, not merely a non-zero return (per <behavior>).
# ---------------------------------------------------------------------------


_SELFTEST_POSITION_ID = "SELFTEST__control__w27c512"

_BASE_PINS = {
    "arms": {
        "control": {
            "fw_sha": "fw_control_sha", "app_sha": "app_control_sha",
            "venv_bin": "/opt/arms/control/bin/firestarter",
            "venv_python": "/opt/arms/control/bin/python",
        },
        "v133": {
            "fw_sha": "fw_v133_sha", "app_sha": "app_v133_sha",
            "venv_bin": "/opt/arms/v133/bin/firestarter",
            "venv_python": "/opt/arms/v133/bin/python",
        },
    },
    "targets": {"uno": {"mcu": "atmega328p"}, "leonardo": {"mcu": "atmega32u4"}},
    "chips": {
        "w27c512": {"algorithm": 7, "size_bytes": 65536},
        "w29c020": {"algorithm": 5, "size_bytes": 262144},
    },
    "avrdude": {"binary": "/opt/avrdude/avrdude"},
    "pio_binary": "/opt/pio/pio",
    "pio_project_dir": "/opt/firestarter",
    "git_binary": "/usr/bin/git",
    "forbidden_flags": ["--force", "-f", "-b", "--no-blank-check", "--skip-erase"],
}

_BASE_PROVENANCE = {
    "position_id": _SELFTEST_POSITION_ID,
    "cell_id": "SELFTEST",
    "cell_slug": "SELFTEST",
    "arm": "control",
    "target_env": "uno",
    "chip": "w27c512",
    "board_signature": "0x1e950f",
    "controller_string": "not measured — selftest fixture, no board attached",
    "shield_rev_declared": "Rev 2.0",
    "fw_sha": "fw_control_sha",
    "fw_readback_sha_judged": "readback_judged_sha",
    "fw_readback_sha_whole_flash": "readback_whole_sha",
    "host_arm_sha": "app_control_sha",
    "host_arm_porcelain_clean": True,
    "host_arm_file": "/opt/arms/control/firestarter/__init__.py",
    "config_dir_sha": "config_sha",
    "interpreter": "Python 3.12.14",
    "dep_freeze_sha": "dep_sha",
    "eeprom_calibration": {"hw_revision_bucket": "not measured — selftest fixture"},
    "image_mask": 1,
    "image_stamp_width": 16,
    "image_sha": "image_sha_value",
    "commands": [
        {"argv": ["/opt/arms/control/bin/python", "-P", "-c", "print(1)"], "cwd": "/workspaces"},
    ],
}

_BASE_WRV = {
    "position_id": _SELFTEST_POSITION_ID,
    "written_sha": "image_sha_value",
    "expect_size": 65536,
    "read_count": 3,
    "read_shas": ["image_sha_value", "image_sha_value", "image_sha_value"],
    "app_verdict_unjudged": 0,
    "sha_verdict_judged": "match",
    "verdict_disagreement": False,
    "size_violations": [],
}

_BASE_READBACK = {
    "flashed_arm": "control",
    "target": "uno",
    "sha_actual_judged": "readback_judged_sha",
    "sha_whole_flash_unjudged": "readback_whole_sha",
    "judged_span_bytes": 26026,
}

_BASE_IMAGE_PLAN = {
    "positions": [
        {"position_id": _SELFTEST_POSITION_ID, "mask": 1, "stamp_width": 16, "sha256": "image_sha_value"},
    ]
}

_BASE_HUMAN = {
    "blank_state": "not measured — selftest fixture, no chip attached",
    "verdict": "Clean write-read-verify match on the selftest fixture.",
    "anomalies": "None observed in this selftest fixture.",
    "write_duration_wallclock_s": "12.34",
    "write_duration_app_reported_s": "11.0",
    "shield_note": None,
}


def _write_leg_fixtures(
    base_dir: Path,
    provenance: dict | None = None,
    wrv: dict | None = None,
    readback: dict | None = None,
    image_plan: dict | None = None,
    pins: dict | None = None,
) -> dict[str, Path]:
    import copy

    prov = copy.deepcopy(_BASE_PROVENANCE)
    if provenance:
        prov.update(provenance)
    w = copy.deepcopy(_BASE_WRV)
    if wrv:
        w.update(wrv)
    rb = copy.deepcopy(_BASE_READBACK)
    if readback:
        rb.update(readback)
    ip = copy.deepcopy(_BASE_IMAGE_PLAN) if image_plan is None else image_plan
    pn = copy.deepcopy(_BASE_PINS)
    if pins:
        pn.update(pins)

    paths = {
        "provenance": base_dir / "provenance.json",
        "wrv": base_dir / "WRV-VERDICT.json",
        "readback": base_dir / "READBACK-VERDICT.json",
        "image_plan": base_dir / "IMAGE-PLAN.json",
        "pins": base_dir / "rig-pins.json",
    }
    paths["provenance"].write_text(json.dumps(prov), encoding="utf-8")
    paths["wrv"].write_text(json.dumps(w), encoding="utf-8")
    paths["readback"].write_text(json.dumps(rb), encoding="utf-8")
    paths["image_plan"].write_text(json.dumps(ip), encoding="utf-8")
    paths["pins"].write_text(json.dumps(pn), encoding="utf-8")
    return paths


def _write_jsonl(base_dir: Path, existing_rows: tuple = ()) -> Path:
    path = base_dir / "EVIDENCE.jsonl"
    schema = {
        "record_keys": RECORD_KEYS,
        "outcome_values": ["validated", "skipped-with-reason"],
        "outcome_domain": ["validated", "skipped-with-reason"],
    }
    lines = [json.dumps({"_schema": schema}, ensure_ascii=False, separators=(",", ":"))]
    for row in existing_rows:
        lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _run_selftest() -> int:
    import shutil
    import tempfile

    ok_overall = True

    def report(name: str, passed: bool, detail: str = "") -> None:
        nonlocal ok_overall
        status = "PASS" if passed else "FAIL"
        if not passed:
            ok_overall = False
        suffix = f" -- {detail}" if detail else ""
        print(f"{status}: {name}{suffix}")

    tmp = Path(tempfile.mkdtemp(prefix="append_evidence_selftest_"))
    try:
        # --- positive 1: complete fixture derives all 40 record_keys and round-trips ---
        leg = tmp / "pos1"; leg.mkdir()
        paths = _write_leg_fixtures(leg)
        jsonl_path = _write_jsonl(leg)
        rc, violations, row = process_position(
            _SELFTEST_POSITION_ID, paths["provenance"], paths["wrv"], paths["readback"],
            paths["image_plan"], paths["pins"], dict(_BASE_HUMAN), jsonl_path,
        )
        round_trip_ok = len(jsonl_path.read_text().splitlines()) == 2 and _SELFTEST_POSITION_ID in jsonl_path.read_text()
        report(
            "positive 1: complete fixture triple derives all 40 record_keys in schema "
            "order and round-trips through render_evidence.append_row_to_file",
            rc == 0 and not violations and row is not None and list(row.keys()) == RECORD_KEYS
            and len(row) == 40 and round_trip_ok,
            f"rc={rc} violations={violations}",
        )

        # --- positive 2: blank_state of the 'not measured -- reason' shape is accepted ---
        leg = tmp / "pos2"; leg.mkdir()
        paths = _write_leg_fixtures(leg)
        jsonl_path = _write_jsonl(leg)
        human = dict(_BASE_HUMAN)
        human["blank_state"] = "not measured — pot not yet set for this selftest fixture"
        rc, violations, row = process_position(
            _SELFTEST_POSITION_ID, paths["provenance"], paths["wrv"], paths["readback"],
            paths["image_plan"], paths["pins"], human, jsonl_path,
        )
        report(
            "positive 2: blank_state='not measured — <reason>' is accepted",
            rc == 0 and not violations,
            f"rc={rc} violations={violations}",
        )

        # --- positive 3: sha_verdict_judged != match -> skipped-with-reason, written,
        #     provided the verdict prose names a symptom ---
        leg = tmp / "pos3"; leg.mkdir()
        paths = _write_leg_fixtures(leg, wrv={"sha_verdict_judged": "mismatch"})
        jsonl_path = _write_jsonl(leg)
        human = dict(_BASE_HUMAN)
        human["verdict"] = "Read-back MISMATCH observed: the third read disagreed with the written image."
        rc, violations, row = process_position(
            _SELFTEST_POSITION_ID, paths["provenance"], paths["wrv"], paths["readback"],
            paths["image_plan"], paths["pins"], human, jsonl_path,
        )
        report(
            "positive 3: sha_verdict_judged != match derives outcome=skipped-with-reason "
            "and is written when verdict prose names a symptom",
            rc == 0 and not violations and row is not None and row["outcome"] == "skipped-with-reason",
            f"rc={rc} violations={violations} outcome={row.get('outcome') if row else None}",
        )

        # --- negative 1: position_id disagreeing with provenance AND wrv, both named ---
        leg = tmp / "neg1"; leg.mkdir()
        paths = _write_leg_fixtures(
            leg, provenance={"position_id": "WRONG-PROV"}, wrv={"position_id": "WRONG-WRV"},
        )
        jsonl_path = _write_jsonl(leg)
        rc, violations, row = process_position(
            _SELFTEST_POSITION_ID, paths["provenance"], paths["wrv"], paths["readback"],
            paths["image_plan"], paths["pins"], dict(_BASE_HUMAN), jsonl_path,
        )
        report(
            "negative 1 (D-05's own argument): --position-id disagreeing with provenance "
            "AND wrv is refused, both disagreements named in one pass",
            rc == 1
            and any("position_id vs provenance.position_id" in v for v in violations)
            and any("position_id vs wrv.position_id" in v for v in violations),
            str(violations),
        )

        # --- negative 2: wrv.written_sha != provenance.image_sha ---
        leg = tmp / "neg2"; leg.mkdir()
        paths = _write_leg_fixtures(leg, wrv={"written_sha": "different_sha_value"})
        jsonl_path = _write_jsonl(leg)
        rc, violations, row = process_position(
            _SELFTEST_POSITION_ID, paths["provenance"], paths["wrv"], paths["readback"],
            paths["image_plan"], paths["pins"], dict(_BASE_HUMAN), jsonl_path,
        )
        report(
            "negative 2: wrv.written_sha != provenance.image_sha is refused",
            rc == 1 and any("wrv.written_sha vs provenance.image_sha" in v for v in violations),
            str(violations),
        )

        # --- negative 3: provenance.arm != readback.flashed_arm ---
        leg = tmp / "neg3"; leg.mkdir()
        paths = _write_leg_fixtures(leg, readback={"flashed_arm": "v133"})
        jsonl_path = _write_jsonl(leg)
        rc, violations, row = process_position(
            _SELFTEST_POSITION_ID, paths["provenance"], paths["wrv"], paths["readback"],
            paths["image_plan"], paths["pins"], dict(_BASE_HUMAN), jsonl_path,
        )
        report(
            "negative 3: provenance.arm != readback.flashed_arm is refused",
            rc == 1 and any("provenance.arm vs readback.flashed_arm" in v for v in violations),
            str(violations),
        )

        # --- negative 4: provenance.target_env != readback.target ---
        leg = tmp / "neg4"; leg.mkdir()
        paths = _write_leg_fixtures(leg, readback={"target": "leonardo"})
        jsonl_path = _write_jsonl(leg)
        rc, violations, row = process_position(
            _SELFTEST_POSITION_ID, paths["provenance"], paths["wrv"], paths["readback"],
            paths["image_plan"], paths["pins"], dict(_BASE_HUMAN), jsonl_path,
        )
        report(
            "negative 4: provenance.target_env != readback.target is refused",
            rc == 1 and any("provenance.target_env vs readback.target" in v for v in violations),
            str(violations),
        )

        # --- negative 5: a bare 'not measured' with no reason is refused (imported regex) ---
        leg = tmp / "neg5"; leg.mkdir()
        paths = _write_leg_fixtures(leg)
        jsonl_path = _write_jsonl(leg)
        human = dict(_BASE_HUMAN)
        human["blank_state"] = "not measured"
        rc, violations, row = process_position(
            _SELFTEST_POSITION_ID, paths["provenance"], paths["wrv"], paths["readback"],
            paths["image_plan"], paths["pins"], human, jsonl_path,
        )
        report(
            "negative 5: bare 'not measured' (no reason) in --blank-state is refused via "
            "the imported gate_record._NOT_MEASURED_RE, never a re-derived regex",
            rc == 1 and any("blank_state" in v for v in violations),
            str(violations),
        )

        # --- negative 6: an empty verdict AND an empty anomalies are each refused ---
        leg = tmp / "neg6a"; leg.mkdir()
        paths = _write_leg_fixtures(leg)
        jsonl_path = _write_jsonl(leg)
        human = dict(_BASE_HUMAN)
        human["verdict"] = ""
        rc_v, violations_v, _ = process_position(
            _SELFTEST_POSITION_ID, paths["provenance"], paths["wrv"], paths["readback"],
            paths["image_plan"], paths["pins"], human, jsonl_path,
        )
        leg2 = tmp / "neg6b"; leg2.mkdir()
        paths2 = _write_leg_fixtures(leg2)
        jsonl_path2 = _write_jsonl(leg2)
        human2 = dict(_BASE_HUMAN)
        human2["anomalies"] = ""
        rc_a, violations_a, _ = process_position(
            _SELFTEST_POSITION_ID, paths2["provenance"], paths2["wrv"], paths2["readback"],
            paths2["image_plan"], paths2["pins"], human2, jsonl_path2,
        )
        report(
            "negative 6: an empty --verdict-file and an empty --anomalies-file are each refused",
            rc_v == 1 and any("verdict" in v for v in violations_v)
            and rc_a == 1 and any("anomalies" in v for v in violations_a),
            f"verdict-empty={violations_v} anomalies-empty={violations_a}",
        )

        # --- negative 7 (Pitfall 5): outcome is never 'validated' when sha_verdict_judged
        #     != match, or verdict_disagreement is true, or size_violations is non-empty ---
        variants = [
            dict(_BASE_WRV, sha_verdict_judged="mismatch"),
            dict(_BASE_WRV, verdict_disagreement=True),
            dict(_BASE_WRV, size_violations=[{"file": "x", "size_bytes": 1}]),
        ]
        outcomes = [_derive_outcome(v) for v in variants]
        report(
            "negative 7 (the leg gate_record.check_cross_oracle() cannot perform): outcome "
            "is never 'validated' when sha_verdict_judged != match, verdict_disagreement is "
            "true, or size_violations is non-empty",
            all(o == "skipped-with-reason" for o in outcomes),
            str(outcomes),
        )

        # --- negative 8: a missing AND an unparseable WRV-VERDICT.json are each refused,
        #     the path named in both cases ---
        leg = tmp / "neg8"; leg.mkdir()
        paths = _write_leg_fixtures(leg)
        jsonl_path = _write_jsonl(leg)
        missing_wrv = leg / "WRV-VERDICT-MISSING.json"
        rc_m, violations_m, _ = process_position(
            _SELFTEST_POSITION_ID, paths["provenance"], missing_wrv, paths["readback"],
            paths["image_plan"], paths["pins"], dict(_BASE_HUMAN), jsonl_path,
        )
        bad_wrv = leg / "WRV-VERDICT-BAD.json"
        bad_wrv.write_text("{not valid json", encoding="utf-8")
        rc_b, violations_b, _ = process_position(
            _SELFTEST_POSITION_ID, paths["provenance"], bad_wrv, paths["readback"],
            paths["image_plan"], paths["pins"], dict(_BASE_HUMAN), jsonl_path,
        )
        report(
            "negative 8: a missing WRV-VERDICT.json and an unparseable one are each refused "
            "with the path named",
            rc_m == 1 and any(str(missing_wrv) in v for v in violations_m)
            and rc_b == 1 and any(str(bad_wrv) in v for v in violations_b),
            f"missing={violations_m} unparseable={violations_b}",
        )

        # --- negative 9: a duplicate position_id already in EVIDENCE.jsonl is refused,
        #     surfacing render_evidence's own message ---
        leg = tmp / "neg9"; leg.mkdir()
        paths = _write_leg_fixtures(leg)
        existing_row = build_row(
            _BASE_PROVENANCE, _BASE_WRV, _BASE_READBACK, _BASE_IMAGE_PLAN["positions"][0],
            _BASE_PINS, _BASE_HUMAN, _SELFTEST_POSITION_ID, _BASE_PROVENANCE["commands"], "validated",
        )
        jsonl_path = _write_jsonl(leg, existing_rows=(existing_row,))
        rc, violations, row = process_position(
            _SELFTEST_POSITION_ID, paths["provenance"], paths["wrv"], paths["readback"],
            paths["image_plan"], paths["pins"], dict(_BASE_HUMAN), jsonl_path,
        )
        report(
            "negative 9: a duplicate position_id already present in EVIDENCE.jsonl is "
            "refused, surfacing render_evidence.append_row_to_file's own message",
            rc == 1 and any("already exists" in v for v in violations),
            str(violations),
        )

        # --- negative 10 (P-H2): outcome=skipped-with-reason but the verdict prose names
        #     no observed symptom is refused ---
        leg = tmp / "neg10"; leg.mkdir()
        paths = _write_leg_fixtures(leg, wrv={"sha_verdict_judged": "mismatch"})
        jsonl_path = _write_jsonl(leg)
        human = dict(_BASE_HUMAN)
        human["verdict"] = "Nothing notable to report about this position."
        rc, violations, row = process_position(
            _SELFTEST_POSITION_ID, paths["provenance"], paths["wrv"], paths["readback"],
            paths["image_plan"], paths["pins"], human, jsonl_path,
        )
        report(
            "negative 10 (the P-H2 record contract): outcome derived as "
            "skipped-with-reason whose verdict prose names no observed symptom is refused",
            rc == 1 and any("symptom" in v for v in violations),
            str(violations),
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"append_evidence.py --selftest overall: {'ok' if ok_overall else 'FAILED'}")
    return 0 if ok_overall else 1


if __name__ == "__main__":
    sys.exit(main())
