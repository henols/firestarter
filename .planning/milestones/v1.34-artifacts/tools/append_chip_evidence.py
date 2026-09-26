#!/usr/bin/env python3
"""append_chip_evidence.py -- the chip sweep's deriving evidence-row writer (D-05 sibling).

D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It is authored and lives
only under .planning/milestones/v1.34-artifacts/tools/ in the meta repo. It must NEVER be copied into
firestarter/ or firestarter_app/ -- this phase changes no firmware and no host source.
Nothing here is imported by, or imports from, either sub-repo.

WHAT THIS TOOL EXISTS TO PREVENT
---------------------------------
Ten parts plus up to six control re-runs, at ~70 fields each, is over a thousand
opportunities to transcribe a field from the wrong position. Every machine field of a row
is DERIVED from this position's own `dev test` report JSON, its provenance artifact
(tools/capture_provenance.py's output) and its READBACK-VERDICT artifact -- never
transcribed by a human. The human supplies exactly four values (vpp_real_mv,
prior_disposition, known_carried, reseat_count) plus two domain-checked judgements
(divergence_verdict, jp4_position); `verdict`/`anomalies` are the two inherited
locked-column human fields the WRV sibling (append_evidence.py) already carries.

`outcome` is the one column this tool computes and NEVER accepts as an input: `validated`
iff `fw_board_identity` is non-null, the report copy-out's two SHAs both matched their
sources, and the frozen config-dir invariant held before and after; otherwise
`skipped-with-reason`. This is deliberately NOT keyed on the chip's own step verdicts -- a
`dev test` BAD is a result carried forward as P-H2, never a skip (outcome_semantics_note,
CHIP-EVIDENCE.jsonl's own schema).

DELEGATION, NEVER RE-IMPLEMENTATION
-------------------------------------
This tool imports, via the `importlib.util.spec_from_file_location` sibling idiom, rather
than re-deriving:
  - `gate_record.py`'s `_is_acceptable_not_measured` / `check_required_fields` (the "not
    measured -- <reason>" anti-fabrication idiom) and `check_commands` (the argv
    allow-list + forbidden-flag re-parse), applied to this row's `commands` field BEFORE
    the row is written.
  - `render_evidence.py`'s `append_row_to_file()` for the write itself -- the record-key
    presence/extra-key rejection, outcome-domain check, duplicate-`position_id` refusal,
    the byte-unchanged-prefix re-read and the atomic temp-file + `os.replace` all live
    there. This tool never hand-rolls a JSONL append.
  - `check_arms.py`'s `compute_config_dir_sha()` for every config-dir digest this tool
    computes -- never a fresh hashlib walk, because a different walk order silently
    produces a different digest.
  - `capture_provenance.py`'s `resolve_out_path()` (the milestone-containment check) for
    the copy-out destination, and its `_cell_id_type` pattern is mirrored (not imported,
    since this tool's cell is always the fixed "CHIP" slug).

`RECORD_KEYS` is never a module-level constant here (unlike append_evidence.py's own
`RECORD_KEYS` list): it is read fresh from the TARGET JSONL's own `_schema.record_keys` on
every call, so this tool and CHIP-EVIDENCE.jsonl can never drift silently.

THE COPY-OUT ORDERING (PD-3) -- AND THE "ASSERT PRISTINE" RESOLUTION
-----------------------------------------------------------------------
`dev test <chip>` ALWAYS persists its report unconditionally into
`<config_dir>/reports/dev-test-<TOKEN>.{json,md}` before this tool is ever invoked --
so at invocation time the frozen config dir already differs from the milestone's
one-time pristine pin (arms-provenance.json's `config_dir_sha`) by exactly the report this
position produced. A literal "the whole-dir digest equals the pristine pin" check would
therefore always fail on every real invocation. This tool resolves that by computing the
"assert pristine" check with this position's own two expected report files temporarily
moved aside (renamed, not copied, not deleted) for the DURATION of one
`check_arms.compute_config_dir_sha()` call, then immediately restored -- so the digest
computed is "what the frozen config dir looks like once this position's own report is set
aside", compared against the milestone pin. A STRAY file left by an earlier, incomplete run
(anything beyond the expected report pair) still makes this check fail, named by path
(Negative 8). This never re-derives the SHA walk itself -- the same canonical
`compute_config_dir_sha()` is called throughout; only the directory's transient state
around the call is orchestrated. The SECOND assertion, after the two source files are
permanently removed, is a plain unmodified call to the same function with no files moved
aside at all (nothing to exclude -- the sources are already gone).

PER-POSITION ARTIFACT LAYOUT
-------------------------------
`--cell-dir` defaults to `bench/cells/CHIP` (this phase runs one cell for its whole sweep).
`--provenance` defaults to `<cell-dir>/provenance_<position-id>.json`, `--readback` to
`<cell-dir>/READBACK-VERDICT.json` -- the same PD-1 shape append_evidence.py already
established for the WRV sibling. The copied-out report destination is
`<cell-dir>/reports/<position_id>.{json,md}` -- POSITION_ID-keyed, which is what makes
D-17's interleaved control re-run safe: `dev test` writes a FIXED path per chip token, so
without this keying a control re-run of the same chip would destroy the v1.33 report before
it was ever read.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_MILESTONE_DIR = _HERE.parent
_DEFAULT_PINS = _MILESTONE_DIR / "rig-pins.json"
_DEFAULT_ARMS_PROVENANCE = _MILESTONE_DIR / "arms-provenance.json"
_DEFAULT_JSONL = _MILESTONE_DIR / "bench" / "CHIP-EVIDENCE.jsonl"
_DEFAULT_CELL_DIR = _MILESTONE_DIR / "bench" / "cells" / "CHIP"

# diagnostic_report.py's SCHEMA_VERSION at the time this tool was authored (162-02).
# Read-only reference value -- never re-derived from the sub-repo, per D-16.
_REPORT_SCHEMA_VERSION_PINNED = "1.7"

_OUTCOME_VALIDATED = "validated"
_OUTCOME_SKIPPED = "skipped-with-reason"

# Both write op strings this appender's per-step lookups must accept (Positive 6): a UV
# part's write step is "write-partial", never merely "write".
_WRITE_OPS = ("write", "write-partial")

# The multi-run destructive/verify + read op set (mirrors chip_test.py's own
# _REPEAT_POLICY_OPS grouping) -- a small, stable rig-side constant, never imported from
# the sub-repo, used only to classify an already-derived step_run_counts map.
_MULTI_RUN_POLICY_OPS = ("read", "write", "write-partial", "verify", "erase")
_REPEAT_POLICY_DEGRADED_TAG = "runs=1"

# submit.py's own off-TTY console strings (D-04/D-10), scraped verbatim -- never
# re-implemented as a duplicate dedup check.
_DEDUP_PRIOR_MARKER = "you appear to have already reported this"
_DEDUP_UNAVAILABLE_MARKER = "the duplicate check could not run"
_DEDUP_ISSUE_URL_RE = re.compile(r"https://github\.com/henols/firestarter_prom/issues/new\?")

_DEDUP_PRIOR_FOUND = "prior report found"
_DEDUP_CHECK_UNAVAILABLE = "duplicate check could not run (gh absent, unauthenticated, or offline)"
_DEDUP_NO_PRIOR = "duplicate check ran, no prior report found"

# hardware.py's own "%u.%uV" wire-frame format (_VOLTAGE_RE), scraped from the standalone
# `firestarter vpp` command's console output -- the SAME regex shape, cited not imported.
_VPP_LINE_RE = re.compile(r"VPP:\s*(\d+)\.(\d+)\s*V")

# diagnostic_report.py's own write-coverage UV-slot line shape (_write_coverage_line),
# parsed here to recover the two numeric fields uv_slot needs as separate values.
_UV_SLOT_ADDR_RE = re.compile(r"slot (0x[0-9A-Fa-f]+) \((\d+) bytes\)")
_UV_SLOTS_LEFT_RE = re.compile(r"(\d+) of (\d+) slots left")

_JP4_CHOICES = ("28-pin", "32-pin")
_ARM_CHOICES = ("control", "v133")

# The permanent, project-wide sha256 named absence for THIS file only (sha256_absence_note,
# CHIP-EVIDENCE.jsonl's own schema) -- `dev test` retains no read image at all.
_SHA256_ABSENCE_VALUE = (
    "not measured — dev test retains no read image; the read runs are destroyed with the "
    "step. The report artifact SHAs are recorded in report_json_sha256/report_md_sha256."
)

# Small, stable rig-side constant (T in RESEARCH.md's derivation-map source column) --
# never re-derived from a sub-repo, mirrors append_evidence.py's own _BOARD_LABEL.
_BOARD_LABEL = {
    "uno": "Arduino Uno",
    "uno328pb": "Arduino Uno (328PB, MiniCore)",
    "leonardo": "Arduino Leonardo",
}


def _na(reason: str) -> str:
    """The named not-applicable shape -- distinct from gate_record's "not measured"
    idiom: this column is not merely unmeasured, it structurally does not apply to this
    row (e.g. control_rerun_for on a primary v133 row)."""
    return f"not applicable — {reason}"


def _nm(reason: str) -> str:
    return f"not measured — {reason}"


# ---------------------------------------------------------------------------
# Sibling reuse -- the house importlib.util.spec_from_file_location idiom.
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


def _check_arms():
    return _load_sibling("check_arms")


def _capture_provenance():
    return _load_sibling("capture_provenance")


# ---------------------------------------------------------------------------
# Artifact loading -- hard refusal, named path, distinct absent/unparseable branches
# (append_evidence.py's own _load_json(), mirrored).
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


def _load_record_keys_from_jsonl(jsonl_path: Path) -> tuple[bool, list | None, str]:
    """RECORD_KEYS is read from the TARGET jsonl's own _schema line 1 -- never a
    module-level constant duplicating CHIP-EVIDENCE.jsonl's column list, so the tool and
    the file cannot drift (mirrors capture_provenance.py's own pins-derivation idiom, PD-4
    applied to a schema instead of a chips map)."""
    if not jsonl_path.exists():
        return False, None, f"--jsonl file does not exist: {jsonl_path}"
    try:
        text = jsonl_path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, None, f"--jsonl file at {jsonl_path} could not be read: {exc}"
    lines = text.splitlines()
    if not lines:
        return False, None, f"--jsonl file is empty: {jsonl_path}"
    try:
        header = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        return False, None, f"--jsonl file {jsonl_path} line 1 is not valid JSON: {exc}"
    schema = header.get("_schema") if isinstance(header, dict) else None
    if not isinstance(schema, dict) or not isinstance(schema.get("record_keys"), list):
        return False, None, f"--jsonl file {jsonl_path} line 1 has no _schema.record_keys list"
    return True, schema["record_keys"], ""


# ---------------------------------------------------------------------------
# Config-dir invariant (PD-3) -- compute_config_dir_sha reused, never re-derived.
# ---------------------------------------------------------------------------


def _find_stray_report_files(config_dir: Path, exclude: set | None = None) -> list:
    exclude = exclude or set()
    reports_dir = config_dir / "reports"
    if not reports_dir.is_dir():
        return []
    excluded_resolved = {p.resolve() for p in exclude}
    return sorted(
        p for p in reports_dir.iterdir() if p.is_file() and p.resolve() not in excluded_resolved
    )


def _assert_pristine_ignoring_expected(
    config_dir: Path, expected: list, pristine_sha: str, ca_mod
) -> tuple[bool, str, str]:
    """compute_config_dir_sha(), called with `expected` (this position's own two report
    files) temporarily moved OUTSIDE config_dir for the DURATION of the call, then
    restored -- never a re-derived walk. Moved OUT of the tree entirely, not merely
    renamed in place: compute_config_dir_sha's rglob(...).is_file() walk would still find
    a same-directory rename. A stray file beyond the expected pair (an earlier,
    incomplete run's leftover) still makes this fail, named by path (Negative 8)."""
    import shutil
    import tempfile

    moved = []
    holding_dir = Path(tempfile.mkdtemp(prefix="chipev-pristine-check-"))
    try:
        for i, p in enumerate(expected):
            if p.is_file():
                tmp = holding_dir / f"{i}-{p.name}"
                shutil.move(str(p), str(tmp))
                moved.append((p, tmp))
        actual = ca_mod.compute_config_dir_sha(str(config_dir))
    finally:
        for original, tmp in moved:
            shutil.move(str(tmp), str(original))
        shutil.rmtree(holding_dir, ignore_errors=True)
    if actual != pristine_sha:
        stray = _find_stray_report_files(config_dir, exclude=set(expected))
        stray_txt = (
            f"; un-copied report file(s) present: {[str(p) for p in stray]}" if stray else ""
        )
        return False, actual, (
            f"config dir sha {actual} != pristine pin {pristine_sha} (checked with this "
            f"position's own report temporarily set aside) -- the frozen config dir is not "
            f"pristine before this run{stray_txt}"
        )
    return True, actual, ""


def _assert_pristine_plain(config_dir: Path, pristine_sha: str, ca_mod) -> tuple[bool, str, str]:
    actual = ca_mod.compute_config_dir_sha(str(config_dir))
    if actual != pristine_sha:
        return False, actual, (
            f"config dir sha {actual} != pristine pin {pristine_sha} after copy-out+removal "
            "-- the frozen config dir was not restored"
        )
    return True, actual, ""


def _sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_out_report(
    src_json: Path, src_md: Path, dest_json: Path, dest_md: Path, dry_run: bool
) -> tuple[bool, str, str | None, str | None]:
    if not src_json.is_file():
        return False, f"report json not found at {src_json}", None, None
    if not src_md.is_file():
        return False, f"report md not found at {src_md}", None, None
    src_json_sha = _sha256_of(src_json)
    src_md_sha = _sha256_of(src_md)
    if dry_run:
        return True, "", src_json_sha, src_md_sha

    dest_json.parent.mkdir(parents=True, exist_ok=True)
    dest_json.write_bytes(src_json.read_bytes())
    dest_md.write_bytes(src_md.read_bytes())
    dest_json_sha = _sha256_of(dest_json)
    dest_md_sha = _sha256_of(dest_md)
    if dest_json_sha != src_json_sha:
        return False, f"copied json sha {dest_json_sha} != source sha {src_json_sha}", None, None
    if dest_md_sha != src_md_sha:
        return False, f"copied md sha {dest_md_sha} != source sha {src_md_sha}", None, None

    # Remove the two source files ONLY -- never the reports/ directory, because an empty
    # directory is invisible to compute_config_dir_sha's rglob(...).is_file() walk.
    src_json.unlink()
    src_md.unlink()
    return True, "", dest_json_sha, dest_md_sha


# ---------------------------------------------------------------------------
# Report / provenance / readback validation -- accumulate-then-report.
# ---------------------------------------------------------------------------


def validate_report(report: dict, chip_token: str) -> list:
    violations = []
    schema_version = report.get("schema_version")
    if schema_version != _REPORT_SCHEMA_VERSION_PINNED:
        violations.append(
            f"report schema_version {schema_version!r} is not the pinned "
            f"{_REPORT_SCHEMA_VERSION_PINNED!r}"
        )
    ac = report.get("auto_capture") or {}
    report_chip = ac.get("chip")
    if report_chip != chip_token:
        violations.append(
            f"report auto_capture.chip {report_chip!r} != --chip-token {chip_token!r}"
        )
    if ac.get("fw_board_identity") is None:
        violations.append(
            "report auto_capture.fw_board_identity is null -- CHIP-02 is a hard "
            "requirement and this position's board identity cannot be attributed "
            "(route to P-H1)"
        )
    return violations


def validate_provenance(position_id: str, arm: str, chip: str, provenance: dict, pins: dict) -> list:
    violations = []
    mismatches = []
    if provenance.get("position_id") != position_id:
        mismatches.append(f"position_id: {provenance.get('position_id')!r} != {position_id!r}")
    if provenance.get("arm") != arm:
        mismatches.append(f"arm: {provenance.get('arm')!r} != {arm!r}")
    if provenance.get("chip") != chip:
        mismatches.append(f"chip: {provenance.get('chip')!r} != {chip!r}")
    if mismatches:
        violations.append("provenance disagrees with CLI arguments: " + "; ".join(mismatches))

    arm_cfg = pins.get("arms", {}).get(arm) or {}
    expected_fw_sha = arm_cfg.get("fw_sha")
    if expected_fw_sha and provenance.get("fw_sha") != expected_fw_sha:
        violations.append(
            f"provenance.fw_sha {provenance.get('fw_sha')!r} != "
            f"pins.arms[{arm!r}].fw_sha {expected_fw_sha!r}"
        )
    return violations


def validate_readback(provenance: dict, readback: dict) -> list:
    violations = []
    if readback.get("sha_actual_judged") is None and readback.get("sha_whole_flash_unjudged") is None:
        violations.append(
            "readback verdict carries no judged result (sha_actual_judged and "
            "sha_whole_flash_unjudged are both absent)"
        )

    def _check(label: str, a, b) -> None:
        if a != b:
            violations.append(f"{label}: {a!r} != {b!r}")

    _check("provenance.arm vs readback.flashed_arm", provenance.get("arm"), readback.get("flashed_arm"))
    _check("provenance.target_env vs readback.target", provenance.get("target_env"), readback.get("target"))
    return violations


def _check_divergence_verdict(value: str) -> str | None:
    if value == "same":
        return None
    if value.startswith("diverges: ") and value[len("diverges: "):].strip():
        return None
    return (
        f"--divergence-verdict {value!r} is neither 'same' nor 'diverges: <non-empty>' -- "
        "SC#3's column holds exactly two shapes"
    )


def _check_control_rerun_for(arm: str, control_rerun_for: str | None) -> str | None:
    if arm == "v133" and control_rerun_for:
        return (
            f"--control-rerun-for {control_rerun_for!r} is set on an arm=v133 row -- only "
            "an arm=control row may arbitrate another row (SC#4)"
        )
    if arm == "control" and not control_rerun_for:
        return (
            "--control-rerun-for must be set on an arm=control row -- every control row "
            "names the v133 row it arbitrates (SC#4)"
        )
    return None


def _validate_vpp_real(value: str, gr_mod) -> tuple[bool, object, str]:
    if gr_mod._is_acceptable_not_measured(value):
        return True, value, ""
    try:
        return True, float(value), ""
    except (TypeError, ValueError):
        return False, None, (
            f"--vpp-real-mv value {value!r} is neither a float nor the "
            "'not measured — <reason>' shape"
        )


# ---------------------------------------------------------------------------
# Pure derivation helpers -- report/provenance -> row fields.
# ---------------------------------------------------------------------------


def derive_dedup_query_outcome(console_log_text: str) -> str:
    if _DEDUP_PRIOR_MARKER in console_log_text:
        return _DEDUP_PRIOR_FOUND
    if _DEDUP_UNAVAILABLE_MARKER in console_log_text:
        return _DEDUP_CHECK_UNAVAILABLE
    if _DEDUP_ISSUE_URL_RE.search(console_log_text):
        return _DEDUP_NO_PRIOR
    return _nm("console log names none of the three known dedup_query_outcome markers")


def derive_vpp_firmware_mv(report: dict | None, console_log_text: str):
    """Prefer the report's own voltage.vpp_before_mv (an exact mV int, native to a real
    `dev test` report -- see its rendered 'vpp (before/after)' table row) over a console-log
    text scrape. Found live, 162-06 Task 2 (position 3, SST27SF512): a real `dev test`
    invocation's console output never contains a literal 'VPP: <N.N>V' line -- that string
    shape belongs only to the standalone `vpp` CLI subcommand's own continuous-print loop
    (C-03's separate invocation), never to `dev test`'s own rich-rendered summary table. The
    console-log regex therefore silently produced 'not measured' on every real chip-sweep
    position (positions 1 and 2 carry this same gap, undetected because neither plan's own
    `<verify>` block asserted vpp_shortfall_mv numerically). Fixed at the correct layer: read
    the authoritative machine field the report already carries; fall back to the console-log
    scrape only when that field is absent or non-numeric (preserves this function's original,
    already-selftested behaviour for a report that genuinely lacks voltage data)."""
    if report is not None:
        voltage = report.get("voltage") or {}
        v = voltage.get("vpp_before_mv")
        if isinstance(v, (int, float)):
            return v
    match = _VPP_LINE_RE.search(console_log_text)
    if not match:
        return _nm(
            "no 'VPP: <N.N>V' line found in --console-log, and report.voltage.vpp_before_mv "
            "is absent or non-numeric"
        )
    v_int, v_dec = int(match.group(1)), int(match.group(2))
    return v_int * 1000 + v_dec * 100


def derive_vpp_shortfall_mv(vpp_target_mv, vpp_firmware_mv):
    if not isinstance(vpp_target_mv, (int, float)) or not isinstance(vpp_firmware_mv, (int, float)):
        return _nm("vpp_target_mv and/or vpp_firmware_mv is not a number -- see those columns")
    return vpp_target_mv - vpp_firmware_mv


def _steps_by_op(steps: list) -> dict:
    result = {}
    for s in steps:
        op = s.get("op") if isinstance(s, dict) else None
        if op is not None:
            result[op] = s
    return result


def derive_step_maps(steps: list) -> tuple:
    verdicts, run_counts, durations, error_codes, fingerprints = {}, {}, {}, {}, {}
    for s in steps:
        if not isinstance(s, dict):
            continue
        op = s.get("op")
        if op is None:
            continue
        verdicts[op] = s.get("verdict")
        run_counts[op] = s.get("run_count")
        durations[op] = s.get("duration_s")
        error_codes[op] = s.get("error_code")
        fingerprints[op] = s.get("fingerprint")
    return verdicts, run_counts, durations, error_codes, fingerprints


_REPEAT_POLICY_DEFAULT_TAG = "default (every multi-run step at run_count>=2, no --fast)"


def derive_repeat_policy(steps: list) -> str:
    """Rule 1 fix (found live, 162-05 Task 3): the healthy/non-degraded case used to return
    a bare "" -- a real, deliberate design choice mirroring chip_test.py's own
    repeat_policy_tag() sentinel, but gate_record.check_required_fields treats EVERY
    record_key as required-non-blank unless it carries the 'not measured — <reason>' shape,
    and an empty string is blank by that rule. "" silently failed CHIP-EVIDENCE.jsonl's own
    record-shape gate on every row this position type produces. Now returns an honest,
    non-blank, descriptive value for both cases -- never weakens what the value MEANS, only
    how the healthy case is spelled, and 162-07's own acceptance check ("empty string OR a
    non-empty string that does not contain 'runs=1'") already anticipated exactly this."""
    for s in steps:
        if not isinstance(s, dict):
            continue
        if s.get("op") in _MULTI_RUN_POLICY_OPS and s.get("run_count") == 1:
            return _REPEAT_POLICY_DEGRADED_TAG
    return _REPEAT_POLICY_DEFAULT_TAG


def _find_write_step(steps: list):
    return next((s for s in steps if isinstance(s, dict) and s.get("op") in _WRITE_OPS), None)


def _find_read_step(steps: list):
    return next((s for s in steps if isinstance(s, dict) and s.get("op") == "read"), None)


def derive_write_target(write_step) -> object:
    if write_step is None:
        return _na("no write/write-partial step in this report")
    return {
        "region_start": write_step.get("write_region_start"),
        "region_length": write_step.get("write_region_length"),
        "bits_cleared": write_step.get("write_bits_cleared"),
        "bits_retained": write_step.get("write_bits_retained"),
        "current_source": write_step.get("write_current_source"),
    }


def derive_write_coverage(write_step) -> object:
    if write_step is None:
        return _na("no write/write-partial step in this report")
    coverage = write_step.get("write_coverage")
    if coverage is None:
        return _na("this write disclosed no coverage line (plain, unexcluded full-device write)")
    return coverage


def derive_uv_slot(write_coverage, write_target) -> object:
    if not isinstance(write_coverage, str) or "slot " not in write_coverage:
        return _na(
            "write coverage line does not describe a UV slot -- non-UV write, or no write "
            "step ran"
        )
    m_addr = _UV_SLOT_ADDR_RE.search(write_coverage)
    m_left = _UV_SLOTS_LEFT_RE.search(write_coverage)
    slot_written = m_addr.group(1) if m_addr else (
        write_target.get("region_start") if isinstance(write_target, dict) else None
    )
    slots_remaining = int(m_left.group(1)) if m_left else None
    slots_total = int(m_left.group(2)) if m_left else None
    return {
        "slot_written": slot_written,
        "slots_remaining": slots_remaining,
        "slots_total": slots_total,
    }


def derive_chip_id(auto_capture: dict) -> dict:
    return {
        "expected": auto_capture.get("chip_id_expected"),
        "actual": auto_capture.get("chip_id_actual"),
        "mismatch_reason": auto_capture.get("chip_id_mismatch_reason"),
    }


def derive_blank_state(steps: list) -> str:
    by_op = _steps_by_op(steps)
    bc = by_op.get("blank-check")
    if bc is None:
        return _nm("no blank-check step present in this report")
    verdict = bc.get("verdict")
    if verdict == "NA":
        reason = bc.get("reason") or "blank-check is NA for this part"
        return _nm(f"blank-check is NA for this part ({reason})")
    return f"blank-check verdict: {verdict}"


def derive_op(chip_token: str, write_step, exit_code: int, named_absence: str | None) -> str:
    if named_absence is not None:
        return "not run — named absence"
    if write_step is None:
        return f"dev test {chip_token}: no write/write-partial step in this report, exit {exit_code}"
    region_start = write_step.get("write_region_start")
    region_length = write_step.get("write_region_length")
    run_count = write_step.get("run_count")
    region = (
        f"(0x{region_start:X}, {region_length})"
        if isinstance(region_start, int) and isinstance(region_length, int)
        else f"({region_start!r}, {region_length!r})"
    )
    return (
        f"dev test {chip_token}: {write_step.get('op')} over {region}, {run_count} cycles, "
        f"exit {exit_code}"
    )


def derive_family(chip_cfg: dict) -> str:
    algorithm = chip_cfg["algorithm"]
    label = chip_cfg["family_label"]
    return "0x%02x (%s)" % (algorithm, label)


def derive_board(target_env: str, target_cfg: dict) -> str:
    mcu = str(target_cfg.get("mcu", "")).upper()
    return "%s (%s)" % (_BOARD_LABEL.get(target_env, target_env), mcu)


def derive_shield(shield_rev_declared, chip_token: str) -> str:
    return "mounted, %s, %s seated" % (shield_rev_declared, str(chip_token).upper())


def derive_outcome(fw_board_identity, copy_ok: bool, config_dir_invariant_held: bool) -> str:
    """Never accepted as input -- always derived. Deliberately excludes the chip's own
    step verdicts (outcome_semantics_note): a BAD dev test still books 'validated' here as
    long as the report was captured and the frozen config dir stayed sound."""
    if fw_board_identity and copy_ok and config_dir_invariant_held:
        return _OUTCOME_VALIDATED
    return _OUTCOME_SKIPPED


def _parse_prior_disposition(text: str) -> tuple:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return "", []
    return lines[0], lines


_PRIOR_SOURCE_RE = re.compile(r"(v\d+\.\d+[A-Za-z0-9.-]*).{0,40}?((?:[Pp]hase\s*)?\d{2,3}\b)")


def derive_prior_disposition_source(newest_line: str) -> str:
    m = _PRIOR_SOURCE_RE.search(newest_line)
    if not m:
        return _nm(
            "could not derive a milestone+phase citation from --prior-disposition-file's "
            "newest line -- the operator's prose did not carry a recognizable 'vX.Y ... "
            "NNN' citation"
        )
    return f"{m.group(1)}, phase {m.group(2).lstrip('Pp').lstrip('hase').strip()}"


_READ_DIVERGENCE_NOT_EXPORTED_REASON = (
    "chip_test.py computes a per-read divergence metric internally (StepResult.divergence, "
    "surfaced only via the fingerprint/marginal classifier) but diagnostic_report.py's own "
    "_step_dict() never serializes a 'divergence' key into the exported report -- confirmed "
    "live, 162-05 Task 3: no read step in any dev-test-<CHIP> report this project can produce "
    "carries this key at all. Host-app limitation (firestarter_app/firestarter/"
    "diagnostic_report.py), out of scope for this phase (D-16: no product-code changes); filed "
    "as a Phase 165/166 backlog item -- C-06's own read-divergence follow-up trigger "
    "(`read_divergence.repeat_divergent == true`) can never fire from the report alone until "
    "this is fixed upstream."
)


def derive_read_divergence(read_step) -> object:
    """Real value if the report ever carries one (future-proofing, never assumed away);
    otherwise the schema's own gate-legible not-measured shape, naming the exact gap rather
    than a silent null -- gate_record.check_required_fields requires every record_key to be
    either real data or 'not measured — <reason>', never a bare None (Rule 1 fix, found live
    162-05 Task 3: the prior unconditional `read_step.get("divergence")` produced a bare
    `None`, which fails that check on every single row)."""
    if isinstance(read_step, dict) and read_step.get("divergence") is not None:
        return read_step["divergence"]
    return _nm(_READ_DIVERGENCE_NOT_EXPORTED_REASON)


def _is_not_measured_str(value: object) -> bool:
    return isinstance(value, str) and value.startswith("not measured — ")


def derive_read_consistency_followup(read_divergence) -> object:
    if _is_not_measured_str(read_divergence):
        return _na(
            "read_divergence itself is not measured (the report never exports this metric) -- "
            "whether a follow-up read was needed cannot be determined from the report alone"
        )
    if read_divergence is None:
        return _na("the read step's two runs agreed -- no follow-up read was required (PD-7)")
    if isinstance(read_divergence, dict) and not read_divergence.get("repeat_divergent"):
        return _na("the read step's two runs agreed -- no follow-up read was required (PD-7)")
    return _nm(
        "the read step's two runs diverged; this appender has no dedicated CLI input for a "
        "follow-up read's per-run SHAs -- see read_divergence for the reported metric"
    )


# ---------------------------------------------------------------------------
# build_row -- pure assembly, assumes every prior check already passed.
# ---------------------------------------------------------------------------


def build_row(*, record_keys: list, inputs: dict, chip_cfg: dict, target_cfg: dict,
              provenance: dict, report: dict | None, report_json_sha, report_md_sha,
              report_json_dest, report_md_dest, outcome: str) -> dict:
    named_absence = inputs["named_absence"]
    chip = inputs["chip"]
    chip_token = inputs["chip_token"]
    arm = inputs["arm"]
    target_env = provenance.get("target_env")

    newest_disposition, all_dispositions = _parse_prior_disposition(inputs["prior_disposition_text"])

    if named_absence is not None:
        steps = []
        auto_capture = {}
        write_step = None
        read_step = None
        report_derived = {
            "report_schema_version": _nm(named_absence),
            "host_version": _nm(named_absence),
            "fw_board_identity": _nm(named_absence),
            "hw_revision": _nm(named_absence),
            "protocol": _nm(named_absence),
            "chip_id": _nm(named_absence),
            "step_verdicts": _nm(named_absence),
            "step_run_counts": _nm(named_absence),
            "step_durations_s": _nm(named_absence),
            "step_error_codes": _nm(named_absence),
            "step_fingerprints": _nm(named_absence),
            "read_divergence": _nm(named_absence),
            "write_target": _nm(named_absence),
            "write_coverage": _nm(named_absence),
            "banner": _nm(named_absence),
            "sdp_hold_state": _nm(named_absence),
            "db_diff": _nm(named_absence),
            "transport_health": _nm(named_absence),
            "dedup_fingerprint": _nm(named_absence),
            "repeat_policy": _nm(named_absence),
            "exit_code": _nm(named_absence),
            "report_json_path": _nm(named_absence),
            "report_json_sha256": _nm(named_absence),
            "report_md_path": _nm(named_absence),
            "report_md_sha256": _nm(named_absence),
            "vpp_firmware_mv": _nm(named_absence),
            "vpp_shortfall_mv": _nm(named_absence),
            "uv_slot": _nm(named_absence),
            "dedup_query_outcome": _nm(named_absence),
            "read_consistency_followup": _nm(named_absence),
        }
        blank_state = _nm(named_absence)
        op_value = derive_op(chip_token, None, inputs["exit_code"], named_absence)
    else:
        steps = report.get("steps") or []
        auto_capture = report.get("auto_capture") or {}
        write_step = _find_write_step(steps)
        read_step = _find_read_step(steps)
        verdicts, run_counts, durations, error_codes, fingerprints = derive_step_maps(steps)
        write_target = derive_write_target(write_step)
        write_coverage = derive_write_coverage(write_step)
        read_divergence = derive_read_divergence(read_step)
        vpp_firmware_mv = derive_vpp_firmware_mv(report, inputs["console_log_text"])
        report_derived = {
            "report_schema_version": report.get("schema_version"),
            "host_version": auto_capture.get("host_version"),
            "fw_board_identity": auto_capture.get("fw_board_identity"),
            "hw_revision": auto_capture.get("hw_revision"),
            "protocol": auto_capture.get("protocol"),
            "chip_id": derive_chip_id(auto_capture),
            "step_verdicts": verdicts,
            "step_run_counts": run_counts,
            "step_durations_s": durations,
            "step_error_codes": error_codes,
            "step_fingerprints": fingerprints,
            "read_divergence": read_divergence,
            "write_target": write_target,
            "write_coverage": write_coverage,
            "banner": report.get("banner") or {"n_ran": None, "m_applicable": None, "locked_steps": []},
            "sdp_hold_state": report.get("sdp_hold_state", ""),
            "db_diff": report.get("db_diff"),
            "transport_health": report.get("transport_health"),
            "dedup_fingerprint": report.get("dedup_fingerprint"),
            "repeat_policy": derive_repeat_policy(steps),
            "exit_code": inputs["exit_code"],
            "report_json_path": str(report_json_dest),
            "report_json_sha256": report_json_sha,
            "report_md_path": str(report_md_dest),
            "report_md_sha256": report_md_sha,
            "vpp_firmware_mv": vpp_firmware_mv,
            "vpp_shortfall_mv": derive_vpp_shortfall_mv(chip_cfg.get("vpp_mv"), vpp_firmware_mv),
            "uv_slot": derive_uv_slot(write_coverage, write_target),
            "dedup_query_outcome": derive_dedup_query_outcome(inputs["console_log_text"]),
            "read_consistency_followup": derive_read_consistency_followup(read_divergence),
        }
        blank_state = derive_blank_state(steps)
        op_value = derive_op(chip_token, write_step, inputs["exit_code"], None)

    if arm == "v133":
        control_rerun_for_value = _na("arm is v133, not a control re-run")
    else:
        control_rerun_for_value = inputs["control_rerun_for"]

    values = {
        "chip": chip,
        "family": derive_family(chip_cfg),
        "board": derive_board(target_env, target_cfg),
        "shield": derive_shield(provenance.get("shield_rev_declared"), chip_token),
        "blank_state": blank_state,
        "op": op_value,
        "sha256": _SHA256_ABSENCE_VALUE,
        "verdict": inputs["verdict_text"],
        "anomalies": inputs["anomalies_text"],
        "position_id": inputs["position_id"],
        "cell_id": provenance.get("cell_id"),
        "cell_slug": provenance.get("cell_slug"),
        "arm": arm,
        "target_env": target_env,
        "board_signature": provenance.get("board_signature"),
        "controller_string": provenance.get("controller_string"),
        "shield_rev_declared": provenance.get("shield_rev_declared"),
        "fw_sha": provenance.get("fw_sha"),
        "fw_readback_sha_judged": provenance.get("fw_readback_sha_judged"),
        "fw_readback_sha_whole_flash": provenance.get("fw_readback_sha_whole_flash"),
        "fw_readback_judged_span_bytes": target_cfg.get("hex_span_expected_by_arm", {}).get(arm),
        "host_arm_sha": provenance.get("host_arm_sha"),
        "host_arm_porcelain_clean": provenance.get("host_arm_porcelain_clean"),
        "host_arm_file": provenance.get("host_arm_file"),
        "config_dir_sha": provenance.get("config_dir_sha"),
        "interpreter": provenance.get("interpreter"),
        "dep_freeze_sha": provenance.get("dep_freeze_sha"),
        "eeprom_calibration": provenance.get("eeprom_calibration"),
        "vpp_target_mv": chip_cfg.get("vpp_mv"),
        "vpp_real_mv": inputs["vpp_real_mv_val"],
        "prior_disposition": newest_disposition,
        "prior_disposition_source": derive_prior_disposition_source(newest_disposition),
        "prior_dispositions_all": all_dispositions,
        "divergence_verdict": inputs["divergence_verdict"],
        "known_carried": inputs["known_carried"],
        "control_rerun_for": control_rerun_for_value,
        "jp4_position": inputs["jp4"],
        "reseat_count": inputs["reseat_count"],
        "commands": inputs["combined_commands"],
        "named_absence": named_absence if named_absence is not None else _na("this position was seated and run — see the report artifacts"),
        "outcome": outcome,
    }
    values.update(report_derived)
    return {k: values[k] for k in record_keys}


# ---------------------------------------------------------------------------
# process_position -- the whole load -> validate -> derive -> copy-out -> (write) pipeline.
# ---------------------------------------------------------------------------


def process_position(inputs: dict, jsonl_path: Path, dry_run: bool = False) -> tuple:
    violations = []

    ok, record_keys, detail = _load_record_keys_from_jsonl(jsonl_path)
    if not ok:
        violations.append(detail)
    ok, pins, detail = _load_json(inputs["pins_path"], "pins file")
    if not ok:
        violations.append(detail)
    ok, arms_prov, detail = _load_json(inputs["arms_provenance_path"], "arms-provenance file")
    if not ok:
        violations.append(detail)
    if violations:
        return 1, violations, None

    gr = _gate_record()
    ca = _check_arms()

    chip = inputs["chip"]
    chip_token = inputs["chip_token"]
    arm = inputs["arm"]
    position_id = inputs["position_id"]
    named_absence = inputs["named_absence"]

    chip_cfg = pins.get("chips", {}).get(chip)
    if chip_cfg is None:
        violations.append(f"rig-pins.json has no chips entry for chip {chip!r}")
    elif "algorithm" not in chip_cfg or "family_label" not in chip_cfg:
        violations.append(
            f"rig-pins.json chips[{chip!r}] is missing 'algorithm' or 'family_label'"
        )

    arm_cfg = pins.get("arms", {}).get(arm)
    if arm_cfg is None:
        violations.append(f"rig-pins.json has no arms entry for arm {arm!r}")

    if named_absence is not None and (
        inputs["report_json_path"] is not None or inputs["report_md_path"] is not None
    ):
        violations.append(
            "--named-absence is mutually exclusive with --report-json/--report-md"
        )
    if named_absence is not None and not named_absence.strip():
        violations.append("--named-absence value must be non-blank")

    report = None
    config_dir = pins.get("config_dir") if pins else None
    pristine_sha = arms_prov.get("config_dir_sha") if arms_prov else None

    if named_absence is None:
        report_json_path = inputs["report_json_path"]
        report_md_path = inputs["report_md_path"]

        if not dry_run:
            if not config_dir:
                violations.append("rig-pins.json has no config_dir to recompute against")
            elif not Path(config_dir).is_dir():
                violations.append(f"config_dir {config_dir!r} does not exist")
            elif not pristine_sha:
                violations.append(
                    "arms-provenance file has no config_dir_sha to compare against"
                )
            else:
                ok, _actual, detail = _assert_pristine_ignoring_expected(
                    Path(config_dir), [report_json_path, report_md_path], pristine_sha, ca
                )
                if not ok:
                    violations.append(detail)

        ok, report, detail = _load_json(report_json_path, "report json")
        if not ok:
            violations.append(detail)
        elif chip_cfg is not None:
            violations.extend(validate_report(report, chip_token))
        if not report_md_path.is_file():
            violations.append(f"report md not found at {report_md_path}")

    ok, provenance, detail = _load_json(inputs["provenance_path"], "provenance artifact")
    if not ok:
        violations.append(detail)
    readback = None
    if inputs.get("pending_readback"):
        # Seam added 162-05 Task 3 (Rule 1 fix, found live): a chip-sweep position
        # never flashes on its own -- the arm's flash-and-readback proof (if any)
        # belongs to a different, earlier cell/plan, or (on a divergence) to this
        # SAME position's own C-08 interleave, which passes --pending-readback=False
        # (the default) and supplies a real READBACK-VERDICT.json. Skip the load and
        # the arm/target cross-check entirely; fw_readback_sha_* come from --provenance
        # as-is (already a "not measured -- pending" placeholder, or a real judged
        # value for a control-rerun row).
        pass
    else:
        ok, readback, detail = _load_json(inputs["readback_path"], "READBACK-VERDICT artifact")
        if not ok:
            violations.append(detail)

    if provenance is not None and pins is not None:
        violations.extend(validate_provenance(position_id, arm, chip, provenance, pins))
    if provenance is not None and readback is not None:
        violations.extend(validate_readback(provenance, readback))

    violations.extend(
        gr.check_required_fields(
            {
                "verdict": inputs["verdict_text"],
                "anomalies": inputs["anomalies_text"],
                "known_carried": inputs["known_carried"],
                "prior_disposition_text": inputs["prior_disposition_text"],
            },
            ["verdict", "anomalies", "known_carried", "prior_disposition_text"],
        )
    )

    vpp_ok, vpp_real_mv_val, detail = _validate_vpp_real(inputs["vpp_real_mv_raw"], gr)
    if not vpp_ok:
        violations.append(detail)

    dv_detail = _check_divergence_verdict(inputs["divergence_verdict"])
    if dv_detail:
        violations.append(dv_detail)

    cr_detail = _check_control_rerun_for(arm, inputs["control_rerun_for"])
    if cr_detail:
        violations.append(cr_detail)

    combined_commands = list((provenance or {}).get("commands") or [])
    if inputs.get("commands_extra"):
        combined_commands = combined_commands + list(inputs["commands_extra"])
    if pins is not None:
        violations.extend(gr.check_commands({"commands": combined_commands}, pins))

    if violations:
        return 1, violations, None

    inputs = dict(inputs)
    inputs["vpp_real_mv_val"] = vpp_real_mv_val
    inputs["combined_commands"] = combined_commands

    report_json_sha = report_md_sha = None
    report_json_dest = report_md_dest = _na("this position was never seated — no report exists")

    if named_absence is None:
        cp = _capture_provenance()
        cell_dir = inputs["cell_dir"]
        containment_root = inputs.get("containment_root", _MILESTONE_DIR)
        report_json_dest = cell_dir / "reports" / f"{position_id}.json"
        report_md_dest = cell_dir / "reports" / f"{position_id}.md"
        ok, resolved_json, detail = cp.resolve_out_path(str(report_json_dest), containment_root)
        if not ok:
            return 1, [detail], None
        ok, resolved_md, detail = cp.resolve_out_path(str(report_md_dest), containment_root)
        if not ok:
            return 1, [detail], None
        report_json_dest, report_md_dest = resolved_json, resolved_md

        ok, detail, report_json_sha, report_md_sha = copy_out_report(
            inputs["report_json_path"], inputs["report_md_path"],
            report_json_dest, report_md_dest, dry_run,
        )
        if not ok:
            return 1, [detail], None

        if not dry_run:
            ok, _actual, detail = _assert_pristine_plain(Path(config_dir), pristine_sha, ca)
            if not ok:
                return 1, [detail], None

    fw_board_identity = (report or {}).get("auto_capture", {}).get("fw_board_identity")
    outcome = derive_outcome(fw_board_identity, True, True)

    target_cfg = pins.get("targets", {}).get((provenance or {}).get("target_env"), {})
    row = build_row(
        record_keys=record_keys, inputs=inputs, chip_cfg=chip_cfg or {}, target_cfg=target_cfg,
        provenance=provenance or {}, report=report, report_json_sha=report_json_sha,
        report_md_sha=report_md_sha, report_json_dest=report_json_dest,
        report_md_dest=report_md_dest, outcome=outcome,
    )

    # Rule 1 fix (found live, 162-05 Task 3): the ONLY required-field check this tool ran
    # before writing was scoped to the four human-supplied fields (verdict/anomalies/
    # known_carried/prior_disposition_text) -- every one of the ~60 MACHINE-derived fields
    # in `row` reached disk with zero validation against the same rule
    # gate_record.check_required_fields enforces on every record_key, later, in a SEPARATE
    # full-file scan (run_gates.sh's own live gate). A derivation bug (e.g. an empty string
    # or a bare None on a required column) was therefore only ever caught after the fact, by
    # a different tool, against an already-written row. Self-check the WHOLE constructed row
    # against the SAME record_keys list before it is ever written (or returned under
    # --dry-run) -- this is the exact check `run_gates.sh` will run again later; catching it
    # here means a bad row is refused at append time, never merely detected afterward.
    row_field_violations = gr.check_required_fields(row, record_keys)
    if row_field_violations:
        return 1, row_field_violations, None

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
    ap.add_argument("--position-id", required=True, help="CHIP__{v133|control}__<slug>")
    ap.add_argument("--arm", required=True, choices=list(_ARM_CHOICES))
    ap.add_argument("--chip", required=True, help="rig-pins.json chips map key (lowercase slug)")
    ap.add_argument("--chip-token", required=True, help="exact `dev test <TOKEN>` CLI token, as typed")
    ap.add_argument("--cell-dir", default=str(_DEFAULT_CELL_DIR))
    ap.add_argument("--report-json", default=None)
    ap.add_argument("--report-md", default=None)
    ap.add_argument("--provenance", default=None)
    ap.add_argument("--readback", default=None)
    ap.add_argument("--exit-code", required=True, type=int)
    ap.add_argument("--console-log", required=True, help="path or '-' for stdin")
    ap.add_argument("--commands-extra", default=None, help="path to a JSON list merged after provenance.commands")
    ap.add_argument("--pins", default=str(_DEFAULT_PINS))
    ap.add_argument(
        "--arms-provenance", default=str(_DEFAULT_ARMS_PROVENANCE),
        help="milestone-level provenance file carrying the pristine config_dir_sha pin",
    )
    ap.add_argument("--jsonl", default=str(_DEFAULT_JSONL))
    ap.add_argument("--verdict-file", required=True, help="path or '-' for stdin")
    ap.add_argument("--anomalies-file", required=True, help="path or '-' for stdin")
    ap.add_argument("--vpp-real-mv", required=True, help="FLOAT or 'not measured — <reason>'")
    ap.add_argument("--prior-disposition-file", required=True, help="path or '-' for stdin")
    ap.add_argument("--divergence-verdict", required=True, help="'same' or 'diverges: <reason>'")
    ap.add_argument("--known-carried", required=True)
    ap.add_argument("--control-rerun-for", default=None)
    ap.add_argument("--named-absence", default=None)
    ap.add_argument(
        "--pending-readback", action="store_true",
        help=(
            'this position never flashes -- the currently-seated arm flash-and-readback proof (if any) belongs to a DIFFERENT, earlier cell/plan (e.g. Phase 161 A3/B2 for the v133 arm on this rig), not to this chip-sweep position. Skip loading/validating --readback (READBACK-VERDICT.json) entirely for this position; fw_readback_sha_judged/fw_readback_sha_whole_flash are taken verbatim from --provenance instead (capture_provenance.py own --pending-readback placeholder text, or a real judged value if this position IS the control-rerun/re-flash pair a divergence C-08 performs). Found live, 162-05 Task 3: append_chip_evidence.py readback load was unconditional, inherited unmodified from the WRV sibling (append_evidence.py) where every position DOES flash-and-readback -- but a chip-sweep position only does that on a divergence (C-08), so every non-diverging position hard-refused with no artifact ever able to exist for it. Default (omitted): unchanged, hard refusal on a missing READBACK-VERDICT.json as before -- a control-rerun row (arm=control) keeps requiring and validating a real judged read-back.'
        ),
    )
    ap.add_argument("--jp4", required=True, choices=list(_JP4_CHOICES))
    ap.add_argument("--reseat-count", default="0")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    return ap


def main() -> int:
    # --selftest pre-parse, exactly per capture_provenance.py/append_evidence.py's own
    # variant: several arguments here are required=True with no default, so a normal
    # ap.parse_args() would refuse "--selftest" alone before this function ever routed to
    # the selftest. The token is double-quoted in source deliberately -- run_gates.sh
    # greps for that exact byte sequence.
    if "--selftest" in sys.argv[1:]:
        return _run_selftest()

    ap = build_argparser()
    args = ap.parse_args()

    cell_dir = Path(args.cell_dir)
    pins_path = Path(args.pins)
    arms_provenance_path = Path(args.arms_provenance)
    jsonl_path = Path(args.jsonl)
    provenance_path = Path(args.provenance) if args.provenance else (
        cell_dir / f"provenance_{args.position_id}.json"
    )
    readback_path = Path(args.readback) if args.readback else (cell_dir / "READBACK-VERDICT.json")

    report_json_path = report_md_path = None
    if args.named_absence is None:
        config_dir_for_default = None
        ok, pins_doc, _detail = _load_json(pins_path, "pins file")
        if ok:
            config_dir_for_default = pins_doc.get("config_dir")
        default_json = (
            Path(config_dir_for_default) / "reports" / f"dev-test-{args.chip_token}.json"
            if config_dir_for_default else None
        )
        default_md = (
            Path(config_dir_for_default) / "reports" / f"dev-test-{args.chip_token}.md"
            if config_dir_for_default else None
        )
        report_json_path = Path(args.report_json) if args.report_json else default_json
        report_md_path = Path(args.report_md) if args.report_md else default_md

    pre_violations = []
    ok, verdict_text, detail = _read_text_or_dash(args.verdict_file)
    if not ok:
        pre_violations.append(f"--verdict-file: {detail}")
        verdict_text = ""
    ok, anomalies_text, detail = _read_text_or_dash(args.anomalies_file)
    if not ok:
        pre_violations.append(f"--anomalies-file: {detail}")
        anomalies_text = ""
    ok, prior_disposition_text, detail = _read_text_or_dash(args.prior_disposition_file)
    if not ok:
        pre_violations.append(f"--prior-disposition-file: {detail}")
        prior_disposition_text = ""
    ok, console_log_text, detail = _read_text_or_dash(args.console_log)
    if not ok:
        pre_violations.append(f"--console-log: {detail}")
        console_log_text = ""

    commands_extra = None
    if args.commands_extra:
        ok, commands_extra, detail = _load_json_list(Path(args.commands_extra))
        if not ok:
            pre_violations.append(detail)

    if pre_violations:
        for v in pre_violations:
            print(f"FAIL: {v}", file=sys.stderr)
        return 1

    inputs = {
        "position_id": args.position_id,
        "arm": args.arm,
        "chip": args.chip,
        "chip_token": args.chip_token,
        "cell_dir": cell_dir,
        "report_json_path": report_json_path,
        "report_md_path": report_md_path,
        "provenance_path": provenance_path,
        "readback_path": readback_path,
        "pins_path": pins_path,
        "arms_provenance_path": arms_provenance_path,
        "exit_code": args.exit_code,
        "console_log_text": console_log_text,
        "verdict_text": verdict_text,
        "anomalies_text": anomalies_text,
        "vpp_real_mv_raw": args.vpp_real_mv,
        "prior_disposition_text": prior_disposition_text,
        "divergence_verdict": args.divergence_verdict,
        "known_carried": args.known_carried,
        "control_rerun_for": args.control_rerun_for,
        "named_absence": args.named_absence,
        "pending_readback": args.pending_readback,
        "jp4": args.jp4,
        "reseat_count": args.reseat_count,
        "commands_extra": commands_extra,
    }

    rc, violations, row = process_position(inputs, jsonl_path, dry_run=args.dry_run)

    if rc != 0:
        for v in violations:
            print(f"FAIL: {v}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(json.dumps(row, indent=2, ensure_ascii=False))
        return 0

    print(
        f"OK: appended position_id={args.position_id!r} outcome={row['outcome']!r} "
        f"divergence_verdict={row['divergence_verdict']!r} to {jsonl_path}"
    )
    return 0


# ---------------------------------------------------------------------------
# --selftest: on-disk fixtures under one mkdtemp, per-leg subdirectories,
# accumulate-then-report, finally: shutil.rmtree. Seven positive + eleven named
# negative legs (<behavior>), each asserting on a NAMED reason substring.
# ---------------------------------------------------------------------------

_SELFTEST_POSITION_ID = "CHIP__v133__w27c512"

_SELFTEST_RECORD_KEYS = [
    "chip", "family", "board", "shield", "blank_state", "op", "sha256", "verdict", "anomalies",
    "position_id", "cell_id", "cell_slug", "arm", "target_env", "board_signature",
    "controller_string", "shield_rev_declared", "fw_sha", "fw_readback_sha_judged",
    "fw_readback_sha_whole_flash", "fw_readback_judged_span_bytes", "host_arm_sha",
    "host_arm_porcelain_clean", "host_arm_file", "config_dir_sha", "interpreter",
    "dep_freeze_sha", "eeprom_calibration", "report_schema_version", "host_version",
    "fw_board_identity", "hw_revision", "protocol", "chip_id", "step_verdicts",
    "step_run_counts", "step_durations_s", "step_error_codes", "step_fingerprints",
    "read_divergence", "write_target", "write_coverage", "banner", "sdp_hold_state",
    "db_diff", "transport_health", "dedup_fingerprint", "repeat_policy", "exit_code",
    "report_json_path", "report_json_sha256", "report_md_path", "report_md_sha256",
    "vpp_target_mv", "vpp_real_mv", "vpp_firmware_mv", "vpp_shortfall_mv",
    "prior_disposition", "prior_disposition_source", "prior_dispositions_all",
    "divergence_verdict", "known_carried", "control_rerun_for", "jp4_position", "uv_slot",
    "reseat_count", "commands", "dedup_query_outcome", "read_consistency_followup",
    "named_absence", "outcome",
]

_SELFTEST_PINS = {
    "arms": {
        "control": {"fw_sha": "fw_control_sha", "app_sha": "app_control_sha",
                     "venv_bin": "/opt/arms/control/bin/firestarter",
                     "venv_python": "/opt/arms/control/bin/python"},
        "v133": {"fw_sha": "fw_v133_sha", "app_sha": "app_v133_sha",
                  "venv_bin": "/opt/arms/v133/bin/firestarter",
                  "venv_python": "/opt/arms/v133/bin/python"},
    },
    "targets": {
        "leonardo": {"mcu": "atmega32u4", "hex_span_expected_by_arm": {"control": 28170, "v133": 25098}},
    },
    "chips": {
        "w27c512": {"algorithm": 7, "family_label": "EPROM-STD", "vpp_mv": 12000, "size_bytes": 65536, "chip_token": "W27C512"},
        "2516": {"algorithm": 11, "family_label": "EPROM-LEGACY", "vpp_mv": 25000, "size_bytes": 2048, "chip_token": "2516"},
        "am27c020": {"algorithm": 8, "family_label": "EPROM-QUICK", "vpp_mv": 13000, "size_bytes": 262144, "chip_token": "AM27C020"},
    },
    "config_dir": None,  # set per-leg
    "forbidden_flags": ["--force", "-f", "-b", "--no-blank-check", "--skip-erase"],
    "avrdude": {"binary": "/opt/avrdude/avrdude"},
    "pio_binary": "/opt/pio/pio",
    "pio_project_dir": "/opt/firestarter",
    "git_binary": "/usr/bin/git",
}

_SELFTEST_PROVENANCE = {
    "position_id": _SELFTEST_POSITION_ID,
    "cell_id": "CHIP",
    "cell_slug": "CHIP",
    "arm": "v133",
    "target_env": "leonardo",
    "chip": "w27c512",
    "board_signature": "0x1e9587",
    "controller_string": "not measured — selftest fixture, no board attached",
    "shield_rev_declared": "Rev 2.0",
    "fw_sha": "fw_v133_sha",
    "fw_readback_sha_judged": "readback_judged_sha",
    "fw_readback_sha_whole_flash": "readback_whole_sha",
    "host_arm_sha": "app_v133_sha",
    "host_arm_porcelain_clean": True,
    "host_arm_file": "/opt/arms/v133/firestarter/__init__.py",
    "config_dir_sha": "config_sha_at_capture_time",
    "interpreter": "Python 3.12.14",
    "dep_freeze_sha": "dep_sha",
    "eeprom_calibration": {"hw_revision_bucket": "not measured — selftest fixture"},
    "commands": [
        {"argv": ["/opt/arms/v133/bin/firestarter", "dev", "test", "W27C512"], "cwd": "/workspaces"},
    ],
}

_SELFTEST_READBACK = {
    "flashed_arm": "v133",
    "target": "leonardo",
    "sha_actual_judged": "readback_judged_sha",
    "sha_whole_flash_unjudged": "readback_whole_sha",
    "judged_span_bytes": 25098,
}

_SELFTEST_REPORT = {
    "schema_version": _REPORT_SCHEMA_VERSION_PINNED,
    "generated": "2026-08-28T00:00:00Z",
    "auto_capture": {
        "host_version": "3.0.0b32",
        "fw_board_identity": "leonardo-rev2.0",
        "hw_revision": "Rev 2.0-class",
        "chip": "W27C512",
        "protocol": "7",
        "chip_id_expected": 55816,
        "chip_id_actual": None,
        "chip_id_mismatch_reason": None,
    },
    "transport_health": {
        "cobs_errors": "not measured", "crc_failures": "not measured",
        "retries": "not measured", "timeouts": "not measured", "transport_suspect": False,
    },
    "steps": [
        {"op": "id", "verdict": "OK", "run_count": 1, "reason": "", "error_code": None,
         "fingerprint": None, "duration_s": 0.5, "write_region_start": None,
         "write_region_length": None, "write_bits_cleared": None, "write_bits_retained": None,
         "write_current_source": None, "write_coverage": None},
        {"op": "read", "verdict": "OK", "run_count": 2, "reason": "", "error_code": None,
         "fingerprint": "clean", "duration_s": 3.2, "write_region_start": None,
         "write_region_length": None, "write_bits_cleared": None, "write_bits_retained": None,
         "write_current_source": None, "write_coverage": None, "divergence": None},
        {"op": "blank-check", "verdict": "OK", "run_count": 1, "reason": "", "error_code": None,
         "fingerprint": None, "duration_s": 0.4, "write_region_start": None,
         "write_region_length": None, "write_bits_cleared": None, "write_bits_retained": None,
         "write_current_source": None, "write_coverage": None},
        {"op": "write", "verdict": "OK", "run_count": 2, "reason": "", "error_code": None,
         "fingerprint": "clean", "duration_s": 12.0, "write_region_start": 0,
         "write_region_length": 65536, "write_bits_cleared": 65536, "write_bits_retained": 0,
         "write_current_source": "onboard", "write_coverage": None},
        {"op": "verify", "verdict": "OK", "run_count": 2, "reason": "", "error_code": None,
         "fingerprint": "clean", "duration_s": 3.0, "write_region_start": 0,
         "write_region_length": 65536, "write_bits_cleared": None, "write_bits_retained": None,
         "write_current_source": None, "write_coverage": None},
        {"op": "erase", "verdict": "NA", "run_count": 0, "reason": "no electrical erase", "error_code": None,
         "fingerprint": None, "duration_s": None, "write_region_start": None,
         "write_region_length": None, "write_bits_cleared": None, "write_bits_retained": None,
         "write_current_source": None, "write_coverage": None},
    ],
    "banner": {"n_ran": 5, "m_applicable": 5, "locked_steps": []},
    "voltage": {"vpp_before_mv": "not measured", "vpp_after_mv": "not measured",
                "vpe_before_mv": "not measured", "vpe_after_mv": "not measured",
                "vpp_mv": "not measured", "vpe_mv": "not measured"},
    "is_submittable": True,
    "dedup_fingerprint": "abc123def456",
    "db_diff": {"current_support_status": "supported", "proposed_disposition": "no change suggested (advisory)", "ladder_state": ""},
    "sdp_hold_state": "NOT-RUN",
}

_SELFTEST_REPORT_MD = "# dev test -- W27C512\n\n(selftest fixture markdown body)\n"

_SELFTEST_HUMAN = {
    "verdict_text": "Clean write-read-verify on the selftest fixture; no anomalies.",
    "anomalies_text": "None observed in this selftest fixture.",
    "vpp_real_mv_raw": "12.1",
    "prior_disposition_text": "v1.16 Phase 91: PASS — read+write-cycle byte-identical to v1.15",
    "divergence_verdict": "same",
    "known_carried": "no",
    "control_rerun_for": None,
    "named_absence": None,
    "jp4": "28-pin",
    "reseat_count": "1",
    "exit_code": 0,
    "console_log_text": (
        "https://github.com/henols/firestarter_prom/issues/new?title=...\n"
        "VPP: 12.1V, Internal VCC: 5.0V\n"
    ),
}


def _write_config_dir(base: Path, chip_token: str, report_json: dict, report_md: str, ca_mod,
                       extra_stray: bool = False):
    """Returns (config_dir, pristine_sha, report_json_path, report_md_path). pristine_sha
    is computed on the config dir BEFORE this position's own report exists -- matching the
    milestone's own one-time arms-provenance.json pin."""
    config_dir = base / "config"
    config_dir.mkdir()
    (config_dir / "seed.txt").write_text("frozen config seed\n", encoding="utf-8")
    # The pristine pin is captured BEFORE any stray/report content exists -- exactly the
    # milestone's own one-time arms-provenance.json pin, taken before any dev test ever ran.
    pristine_sha = ca_mod.compute_config_dir_sha(str(config_dir))
    if extra_stray:
        stray_dir = config_dir / "reports"
        stray_dir.mkdir()
        (stray_dir / "leftover-from-a-prior-run.json").write_text("{}", encoding="utf-8")
    reports_dir = config_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    json_path = reports_dir / f"dev-test-{chip_token}.json"
    md_path = reports_dir / f"dev-test-{chip_token}.md"
    json_path.write_text(json.dumps(report_json), encoding="utf-8")
    md_path.write_text(report_md, encoding="utf-8")
    return config_dir, pristine_sha, json_path, md_path


def _make_inputs(leg: Path, config_dir, report_json_path, report_md_path, pins_path,
                  arms_provenance_path, provenance_path, readback_path, cell_dir, **overrides):
    inputs = {
        "position_id": _SELFTEST_POSITION_ID,
        "arm": "v133",
        "chip": "w27c512",
        "chip_token": "W27C512",
        "cell_dir": cell_dir,
        "containment_root": leg,
        "report_json_path": report_json_path,
        "report_md_path": report_md_path,
        "provenance_path": provenance_path,
        "readback_path": readback_path,
        "pins_path": pins_path,
        "arms_provenance_path": arms_provenance_path,
        "exit_code": _SELFTEST_HUMAN["exit_code"],
        "console_log_text": _SELFTEST_HUMAN["console_log_text"],
        "verdict_text": _SELFTEST_HUMAN["verdict_text"],
        "anomalies_text": _SELFTEST_HUMAN["anomalies_text"],
        "vpp_real_mv_raw": _SELFTEST_HUMAN["vpp_real_mv_raw"],
        "prior_disposition_text": _SELFTEST_HUMAN["prior_disposition_text"],
        "divergence_verdict": _SELFTEST_HUMAN["divergence_verdict"],
        "known_carried": _SELFTEST_HUMAN["known_carried"],
        "control_rerun_for": _SELFTEST_HUMAN["control_rerun_for"],
        "named_absence": _SELFTEST_HUMAN["named_absence"],
        "jp4": _SELFTEST_HUMAN["jp4"],
        "reseat_count": _SELFTEST_HUMAN["reseat_count"],
        "commands_extra": None,
    }
    inputs.update(overrides)
    return inputs


def _write_jsonl(base: Path) -> Path:
    path = base / "CHIP-EVIDENCE.jsonl"
    schema = {"record_keys": _SELFTEST_RECORD_KEYS, "outcome_values": ["validated", "skipped-with-reason"],
              "outcome_domain": ["validated", "skipped-with-reason"]}
    path.write_text(json.dumps({"_schema": schema}, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _write_fixture_json(path: Path, data) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def _run_selftest() -> int:
    import copy
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

    ca_mod = _check_arms()
    tmp = Path(tempfile.mkdtemp(prefix="append_chip_evidence_selftest_"))
    try:
        def _leg(name: str, extra_stray: bool = False):
            leg = tmp / name
            leg.mkdir()
            cell_dir = leg / "cell"
            cell_dir.mkdir()
            config_dir, pristine_sha, rj, rm = _write_config_dir(
                leg, "W27C512", _SELFTEST_REPORT, _SELFTEST_REPORT_MD, ca_mod, extra_stray=extra_stray,
            )
            pins = copy.deepcopy(_SELFTEST_PINS)
            pins["config_dir"] = str(config_dir)
            pins_path = leg / "rig-pins.json"
            _write_fixture_json(pins_path, pins)
            arms_prov_path = leg / "arms-provenance.json"
            _write_fixture_json(arms_prov_path, {"config_dir_sha": pristine_sha})
            provenance_path = leg / "provenance.json"
            _write_fixture_json(provenance_path, copy.deepcopy(_SELFTEST_PROVENANCE))
            readback_path = leg / "readback.json"
            _write_fixture_json(readback_path, copy.deepcopy(_SELFTEST_READBACK))
            jsonl_path = _write_jsonl(leg)
            return leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path, readback_path, jsonl_path

        # --- positive 1 ---
        (leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path,
         readback_path, jsonl_path) = _leg("pos1")
        inputs = _make_inputs(leg, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path, readback_path, cell_dir)
        rc, violations, row = process_position(inputs, jsonl_path)
        round_trip_ok = row is not None and len(jsonl_path.read_text().splitlines()) == 2
        report(
            "positive 1: complete fixture triple derives all declared record_keys in "
            "schema order and round-trips through render_evidence.append_row_to_file",
            rc == 0 and not violations and row is not None and list(row.keys()) == _SELFTEST_RECORD_KEYS
            and round_trip_ok,
            f"rc={rc} violations={violations}",
        )
        report(
            "positive 4: the copy-out leaves the fixture config dir's tree digest "
            "byte-identical to its pre-run value, and both copies' SHAs equal their sources'",
            rc == 0 and ca_mod.compute_config_dir_sha(str(config_dir)) == json.loads(arms_prov_path.read_text())["config_dir_sha"]
            and not rj.exists() and not rm.exists()
            and (cell_dir / "reports" / f"{_SELFTEST_POSITION_ID}.json").is_file()
            and (cell_dir / "reports" / f"{_SELFTEST_POSITION_ID}.md").is_file(),
            f"rc={rc}",
        )

        # --- positive 2: --named-absence ---
        leg = tmp / "pos2"; leg.mkdir()
        cell_dir2 = leg / "cell"; cell_dir2.mkdir()
        pins2 = copy.deepcopy(_SELFTEST_PINS); pins2["config_dir"] = str(tmp / "unused-config")
        pins_path2 = leg / "rig-pins.json"; _write_fixture_json(pins_path2, pins2)
        arms_prov_path2 = leg / "arms-provenance.json"; _write_fixture_json(arms_prov_path2, {"config_dir_sha": "unused"})
        provenance2 = copy.deepcopy(_SELFTEST_PROVENANCE)
        provenance2.update({"position_id": "CHIP__v133__2516", "chip": "2516"})
        provenance_path2 = leg / "provenance.json"; _write_fixture_json(provenance_path2, provenance2)
        readback_path2 = leg / "readback.json"; _write_fixture_json(readback_path2, copy.deepcopy(_SELFTEST_READBACK))
        jsonl_path2 = _write_jsonl(leg)
        inputs2 = _make_inputs(
            leg, None, None, None, pins_path2, arms_prov_path2, provenance_path2, readback_path2, cell_dir2,
            position_id="CHIP__v133__2516", chip="2516", chip_token="2516",
            named_absence="2516 is never seated in this phase (D-14)",
        )
        rc2, violations2, row2 = process_position(inputs2, jsonl_path2)
        gr_mod = _gate_record()
        req_violations = gr_mod.check_required_fields(row2 or {}, _SELFTEST_RECORD_KEYS) if row2 else ["no row"]
        report(
            "positive 2: --named-absence produces a complete row with every "
            "machine-derived field in the 'not measured — <reason>' shape and passes "
            "check_required_fields",
            rc2 == 0 and not violations2 and row2 is not None and not req_violations,
            f"rc={rc2} violations={violations2} req_violations={req_violations}",
        )

        # --- positive 3: vpp_shortfall_mv is computed, not constant ---
        leg = tmp / "pos3a"; leg.mkdir()
        cell_dir3a = leg / "cell"; cell_dir3a.mkdir()
        config_dir3a, pristine3a, rj3a, rm3a = _write_config_dir(leg, "W27C512", _SELFTEST_REPORT, _SELFTEST_REPORT_MD, ca_mod)
        pins3a = copy.deepcopy(_SELFTEST_PINS); pins3a["config_dir"] = str(config_dir3a)
        pins_path3a = leg / "rig-pins.json"; _write_fixture_json(pins_path3a, pins3a)
        arms_prov_path3a = leg / "arms-provenance.json"; _write_fixture_json(arms_prov_path3a, {"config_dir_sha": pristine3a})
        provenance_path3a = leg / "provenance.json"; _write_fixture_json(provenance_path3a, copy.deepcopy(_SELFTEST_PROVENANCE))
        readback_path3a = leg / "readback.json"; _write_fixture_json(readback_path3a, copy.deepcopy(_SELFTEST_READBACK))
        jsonl_path3a = _write_jsonl(leg)
        inputs3a = _make_inputs(leg, config_dir3a, rj3a, rm3a, pins_path3a, arms_prov_path3a, provenance_path3a, readback_path3a, cell_dir3a)
        inputs3a["console_log_text"] = "VPP: 11.9V, Internal VCC: 5.0V\n"
        rc3a, v3a, row3a = process_position(inputs3a, jsonl_path3a)

        leg = tmp / "pos3b"; leg.mkdir()
        cell_dir3b = leg / "cell"; cell_dir3b.mkdir()
        config_dir3b, pristine3b, rj3b, rm3b = _write_config_dir(leg, "W27C512", _SELFTEST_REPORT, _SELFTEST_REPORT_MD, ca_mod)
        pins3b = copy.deepcopy(_SELFTEST_PINS); pins3b["config_dir"] = str(config_dir3b)
        pins_path3b = leg / "rig-pins.json"; _write_fixture_json(pins_path3b, pins3b)
        arms_prov_path3b = leg / "arms-provenance.json"; _write_fixture_json(arms_prov_path3b, {"config_dir_sha": pristine3b})
        provenance_path3b = leg / "provenance.json"; _write_fixture_json(provenance_path3b, copy.deepcopy(_SELFTEST_PROVENANCE))
        readback_path3b = leg / "readback.json"; _write_fixture_json(readback_path3b, copy.deepcopy(_SELFTEST_READBACK))
        jsonl_path3b = _write_jsonl(leg)
        inputs3b = _make_inputs(leg, config_dir3b, rj3b, rm3b, pins_path3b, arms_prov_path3b, provenance_path3b, readback_path3b, cell_dir3b)
        inputs3b["console_log_text"] = "VPP: 12.4V, Internal VCC: 5.0V\n"
        rc3b, v3b, row3b = process_position(inputs3b, jsonl_path3b)
        report(
            "positive 3: vpp_shortfall_mv is COMPUTED (target - firmware) -- two "
            "different firmware readings against the same target yield two different "
            "shortfalls with the documented sign",
            rc3a == 0 and rc3b == 0 and row3a is not None and row3b is not None
            and row3a["vpp_shortfall_mv"] != row3b["vpp_shortfall_mv"]
            and row3a["vpp_shortfall_mv"] == 12000 - 11900
            and row3b["vpp_shortfall_mv"] == 12000 - 12400,
            f"rc3a={rc3a} rc3b={rc3b} v3a={v3a} v3b={v3b} "
            f"shortfall_a={row3a.get('vpp_shortfall_mv') if row3a else None} "
            f"shortfall_b={row3b.get('vpp_shortfall_mv') if row3b else None}",
        )

        # --- positive 4: derive_vpp_firmware_mv PREFERS report.voltage.vpp_before_mv over a
        #     console-log text scrape -- 162-06 Task 2 finding: a real `dev test` console log
        #     never contains a literal 'VPP: <N.N>V' line at all, so the report's own machine
        #     field must be read directly rather than relied on as a fallback-only source. ---
        leg = tmp / "pos3c"; leg.mkdir()
        cell_dir3c = leg / "cell"; cell_dir3c.mkdir()
        report3c = copy.deepcopy(_SELFTEST_REPORT)
        report3c["voltage"]["vpp_before_mv"] = 12400
        config_dir3c, pristine3c, rj3c, rm3c = _write_config_dir(leg, "W27C512", report3c, _SELFTEST_REPORT_MD, ca_mod)
        pins3c = copy.deepcopy(_SELFTEST_PINS); pins3c["config_dir"] = str(config_dir3c)
        pins_path3c = leg / "rig-pins.json"; _write_fixture_json(pins_path3c, pins3c)
        arms_prov_path3c = leg / "arms-provenance.json"; _write_fixture_json(arms_prov_path3c, {"config_dir_sha": pristine3c})
        provenance_path3c = leg / "provenance.json"; _write_fixture_json(provenance_path3c, copy.deepcopy(_SELFTEST_PROVENANCE))
        readback_path3c = leg / "readback.json"; _write_fixture_json(readback_path3c, copy.deepcopy(_SELFTEST_READBACK))
        jsonl_path3c = _write_jsonl(leg)
        inputs3c = _make_inputs(leg, config_dir3c, rj3c, rm3c, pins_path3c, arms_prov_path3c, provenance_path3c, readback_path3c, cell_dir3c)
        # No 'VPP: <N.N>V' line anywhere in this console log -- matching a REAL `dev test`
        # invocation's actual output shape (only a rich-rendered table, never that literal
        # string). If the fix regressed to console-log-only, this would fall through to
        # not-measured; asserting a real numeric value here proves the report field wins.
        inputs3c["console_log_text"] = (
            "https://github.com/henols/firestarter_prom/issues/new?title=...\n"
        )
        rc3c, v3c, row3c = process_position(inputs3c, jsonl_path3c)
        report(
            "positive 4: vpp_firmware_mv reads report.voltage.vpp_before_mv directly when "
            "present and numeric, even though the console log carries no 'VPP: <N.N>V' line "
            "at all (the real dev-test console shape, per 162-06 Task 2)",
            rc3c == 0 and row3c is not None
            and row3c["vpp_firmware_mv"] == 12400
            and row3c["vpp_shortfall_mv"] == 12000 - 12400,
            f"rc3c={rc3c} v3c={v3c} "
            f"vpp_firmware_mv={row3c.get('vpp_firmware_mv') if row3c else None} "
            f"shortfall={row3c.get('vpp_shortfall_mv') if row3c else None}",
        )

        # --- positive 5 + 6: UV fixture (write-partial) ---
        uv_report = copy.deepcopy(_SELFTEST_REPORT)
        uv_report["auto_capture"]["chip"] = "AM27C020"
        for s in uv_report["steps"]:
            if s["op"] == "write":
                s["op"] = "write-partial"
                s["write_region_start"] = 0x3FF00
                s["write_region_length"] = 256
                s["write_bits_cleared"] = 128
                s["write_bits_retained"] = 128
                s["write_coverage"] = "slot 0x3FF00 (256 bytes), 128 bits cleared this cycle; 5 of 21 slots left on this part"
        leg = tmp / "pos5"; leg.mkdir()
        cell_dir5 = leg / "cell"; cell_dir5.mkdir()
        config_dir5, pristine5, rj5, rm5 = _write_config_dir(leg, "AM27C020", uv_report, _SELFTEST_REPORT_MD, ca_mod)
        pins5 = copy.deepcopy(_SELFTEST_PINS); pins5["config_dir"] = str(config_dir5)
        pins_path5 = leg / "rig-pins.json"; _write_fixture_json(pins_path5, pins5)
        arms_prov_path5 = leg / "arms-provenance.json"; _write_fixture_json(arms_prov_path5, {"config_dir_sha": pristine5})
        provenance5 = copy.deepcopy(_SELFTEST_PROVENANCE)
        provenance5.update({"position_id": "CHIP__v133__am27c020", "chip": "am27c020"})
        provenance_path5 = leg / "provenance.json"; _write_fixture_json(provenance_path5, provenance5)
        readback_path5 = leg / "readback.json"; _write_fixture_json(readback_path5, copy.deepcopy(_SELFTEST_READBACK))
        jsonl_path5 = _write_jsonl(leg)
        inputs5 = _make_inputs(
            leg, config_dir5, rj5, rm5, pins_path5, arms_prov_path5, provenance_path5, readback_path5, cell_dir5,
            position_id="CHIP__v133__am27c020", chip="am27c020", chip_token="AM27C020",
        )
        rc5, v5, row5 = process_position(inputs5, jsonl_path5)
        report(
            "positive 5: a UV fixture's write-coverage slot line and slots-remaining "
            "figure reach the row verbatim, and uv_slot carries "
            "slot_written/slots_remaining/slots_total",
            rc5 == 0 and not v5 and row5 is not None
            and row5["write_coverage"] == "slot 0x3FF00 (256 bytes), 128 bits cleared this cycle; 5 of 21 slots left on this part"
            and row5["uv_slot"] == {"slot_written": "0x3FF00", "slots_remaining": 5, "slots_total": 21},
            f"rc={rc5} violations={v5} row5={row5.get('uv_slot') if row5 else None}",
        )
        report(
            "positive 6: a fixture whose write step's op is 'write-partial' populates "
            "the same write columns as one whose op is 'write'",
            rc5 == 0 and row5 is not None
            and isinstance(row5["write_target"], dict)
            and row5["write_target"]["region_start"] == 0x3FF00
            and row5["write_target"]["region_length"] == 256,
            f"write_target={row5.get('write_target') if row5 else None}",
        )

        # --- positive 7: --dry-run writes nothing ---
        (leg, cell_dir7, config_dir7, rj7, rm7, pins_path7, arms_prov_path7, provenance_path7,
         readback_path7, jsonl_path7) = _leg("pos7")
        before_mtime = jsonl_path7.stat().st_mtime_ns
        before_bytes = jsonl_path7.stat().st_size
        inputs7 = _make_inputs(leg, config_dir7, rj7, rm7, pins_path7, arms_prov_path7, provenance_path7, readback_path7, cell_dir7)
        rc7, v7, row7 = process_position(inputs7, jsonl_path7, dry_run=True)
        after_mtime = jsonl_path7.stat().st_mtime_ns
        after_bytes = jsonl_path7.stat().st_size
        report(
            "positive 7: --dry-run writes nothing -- unchanged jsonl mtime AND byte count, "
            "and the source report files are left untouched",
            rc7 == 0 and not v7 and row7 is not None
            and before_mtime == after_mtime and before_bytes == after_bytes
            and rj7.exists() and rm7.exists(),
            f"rc={rc7} violations={v7}",
        )

        # --- positive 8: --pending-readback skips the READBACK-VERDICT load/validate ---
        # entirely -- a chip-sweep position that never flashes on its own (162-05 Task 3
        # Rule 1 fix). Delete readback.json outright so any un-gated code path would hard
        # fail on a missing file; the row must still succeed and carry provenance's own
        # (placeholder) fw_readback_sha_* verbatim.
        (leg, cell_dir8, config_dir8, rj8, rm8, pins_path8, arms_prov_path8, provenance_path8,
         readback_path8, jsonl_path8) = _leg("pos8")
        pending_provenance = copy.deepcopy(_SELFTEST_PROVENANCE)
        pending_provenance["fw_readback_sha_judged"] = "not measured — pending flash and read-back for this cell"
        pending_provenance["fw_readback_sha_whole_flash"] = "not measured — pending flash and read-back for this cell"
        _write_fixture_json(provenance_path8, pending_provenance)
        readback_path8.unlink()
        inputs8 = _make_inputs(
            leg, config_dir8, rj8, rm8, pins_path8, arms_prov_path8, provenance_path8, readback_path8, cell_dir8,
            pending_readback=True,
        )
        rc8, v8, row8 = process_position(inputs8, jsonl_path8)
        report(
            "positive 8: --pending-readback skips the READBACK-VERDICT load/validate "
            "entirely (no readback.json exists on disk) and the row carries provenance's "
            "own not-measured fw_readback_sha_* verbatim",
            rc8 == 0 and not v8 and row8 is not None
            and not readback_path8.exists()
            and row8["fw_readback_sha_judged"] == "not measured — pending flash and read-back for this cell"
            and row8["fw_readback_sha_whole_flash"] == "not measured — pending flash and read-back for this cell",
            f"rc={rc8} violations={v8} judged={row8.get('fw_readback_sha_judged') if row8 else None}",
        )

        # --- negative 1: fw_board_identity: null ---
        (leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path,
         readback_path, jsonl_path) = _leg("neg1", )
        bad_report = copy.deepcopy(_SELFTEST_REPORT)
        bad_report["auto_capture"]["fw_board_identity"] = None
        rj.write_text(json.dumps(bad_report), encoding="utf-8")
        inputs = _make_inputs(leg, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path, readback_path, cell_dir)
        rc, v, row = process_position(inputs, jsonl_path)
        report(
            "negative 1: fw_board_identity: null is refused, naming the field and CHIP-02",
            rc == 1 and any("fw_board_identity" in x and "CHIP-02" in x for x in v),
            str(v),
        )

        # --- negative 2: auto_capture.chip mismatches --chip-token ---
        (leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path,
         readback_path, jsonl_path) = _leg("neg2")
        bad_report = copy.deepcopy(_SELFTEST_REPORT)
        bad_report["auto_capture"]["chip"] = "WRONGTOKEN"
        rj.write_text(json.dumps(bad_report), encoding="utf-8")
        inputs = _make_inputs(leg, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path, readback_path, cell_dir)
        rc, v, row = process_position(inputs, jsonl_path)
        report(
            "negative 2: report auto_capture.chip disagreeing with --chip-token is "
            "refused, naming both values",
            rc == 1 and any("WRONGTOKEN" in x and "W27C512" in x for x in v),
            str(v),
        )

        # --- negative 3: schema_version mismatch ---
        (leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path,
         readback_path, jsonl_path) = _leg("neg3")
        bad_report = copy.deepcopy(_SELFTEST_REPORT)
        bad_report["schema_version"] = "0.1"
        rj.write_text(json.dumps(bad_report), encoding="utf-8")
        inputs = _make_inputs(leg, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path, readback_path, cell_dir)
        rc, v, row = process_position(inputs, jsonl_path)
        report(
            "negative 3: a report schema_version other than the pinned value is "
            "refused by name",
            rc == 1 and any("schema_version" in x for x in v),
            str(v),
        )

        # --- negative 4: divergence_verdict domain ---
        (leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path,
         readback_path, jsonl_path) = _leg("neg4a")
        inputs = _make_inputs(leg, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path, readback_path, cell_dir,
                               divergence_verdict="inconclusive")
        rc_a, v_a, _ = process_position(inputs, jsonl_path)
        (leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path,
         readback_path, jsonl_path) = _leg("neg4b")
        inputs = _make_inputs(leg, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path, readback_path, cell_dir,
                               divergence_verdict="diverges: ")
        rc_b, v_b, _ = process_position(inputs, jsonl_path)
        report(
            "negative 4: --divergence-verdict 'inconclusive' is refused, and separately "
            "'diverges: ' with an empty tail is refused, both naming the two-value domain",
            rc_a == 1 and any("divergence-verdict" in x for x in v_a)
            and rc_b == 1 and any("divergence-verdict" in x for x in v_b),
            f"a={v_a} b={v_b}",
        )

        # --- negative 5: forbidden flags -b and --force, delegated to check_commands ---
        (leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path,
         readback_path, jsonl_path) = _leg("neg5a")
        prov_b = copy.deepcopy(_SELFTEST_PROVENANCE)
        prov_b["commands"] = [{"argv": ["/opt/arms/v133/bin/firestarter", "write", "w27c512", "-b"], "cwd": "/tmp"}]
        provenance_path.write_text(json.dumps(prov_b), encoding="utf-8")
        inputs = _make_inputs(leg, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path, readback_path, cell_dir)
        rc_a, v_a, _ = process_position(inputs, jsonl_path)
        (leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path,
         readback_path, jsonl_path) = _leg("neg5b")
        prov_f = copy.deepcopy(_SELFTEST_PROVENANCE)
        prov_f["commands"] = [{"argv": ["/opt/arms/v133/bin/firestarter", "write", "w27c512", "--force"], "cwd": "/tmp"}]
        provenance_path.write_text(json.dumps(prov_f), encoding="utf-8")
        inputs = _make_inputs(leg, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path, readback_path, cell_dir)
        rc_b, v_b, _ = process_position(inputs, jsonl_path)
        report(
            "negative 5: a commands entry containing '-b' is refused, and separately one "
            "containing '--force' is refused, both through delegated gate_record.check_commands",
            rc_a == 1 and any("forbidden flag" in x for x in v_a)
            and rc_b == 1 and any("forbidden flag" in x for x in v_b),
            f"a={v_a} b={v_b}",
        )

        # --- negative 6: duplicate position_id ---
        (leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path,
         readback_path, jsonl_path) = _leg("neg6")
        inputs = _make_inputs(leg, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path, readback_path, cell_dir)
        rc1, v1, _ = process_position(inputs, jsonl_path)
        (leg2, cell_dir2, config_dir2, rj2, rm2, pins_path2, arms_prov_path2, provenance_path2,
         readback_path2, _unused_jsonl) = _leg("neg6-dup-source")
        inputs2 = _make_inputs(leg2, config_dir2, rj2, rm2, pins_path2, arms_prov_path2, provenance_path2, readback_path2, cell_dir2)
        rc2, v2, _ = process_position(inputs2, jsonl_path)
        report(
            "negative 6: a duplicate position_id is refused, surfacing render_evidence's "
            "own message",
            rc1 == 0 and rc2 == 1 and any("already exists" in x for x in v2),
            f"rc1={rc1} v1={v1} rc2={rc2} v2={v2}",
        )

        # --- negative 7: extra key rejected by render_evidence, not gate_record ---
        (leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path,
         readback_path, jsonl_path) = _leg("neg7")
        re_mod = _render_evidence()
        bad_row = {k: "x" for k in _SELFTEST_RECORD_KEYS}
        bad_row["outcome"] = "validated"
        bad_row["position_id"] = "EXTRA-KEY-LEG"
        bad_row["an_extra_key_not_in_record_keys"] = "boom"
        try:
            re_mod.append_row_to_file(jsonl_path, bad_row)
            extra_key_caught = False
            extra_detail = "did not raise"
        except re_mod.RenderError as exc:
            extra_key_caught = "not declared in record_keys" in str(exc)
            extra_detail = str(exc)
        report(
            "negative 7: a row carrying an extra key is refused by render_evidence, "
            "proving the extra-key guarantee lives there, not in gate_record",
            extra_key_caught,
            extra_detail,
        )

        # --- negative 8: dirty fixture config dir (stray leftover file) ---
        (leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path,
         readback_path, jsonl_path) = _leg("neg8", extra_stray=True)
        inputs = _make_inputs(leg, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path, readback_path, cell_dir)
        rc, v, _ = process_position(inputs, jsonl_path)
        report(
            "negative 8: a dirty fixture config dir at step 1 is refused, naming the "
            "un-copied report file",
            rc == 1 and any("leftover-from-a-prior-run.json" in x for x in v),
            str(v),
        )

        # --- negative 9: control_rerun_for vs arm, both halves ---
        (leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path,
         readback_path, jsonl_path) = _leg("neg9a")
        inputs = _make_inputs(leg, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path, readback_path, cell_dir,
                               control_rerun_for="CHIP__v133__w27c512")
        rc_a, v_a, _ = process_position(inputs, jsonl_path)
        (leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path,
         readback_path, jsonl_path) = _leg("neg9b")
        prov_c = copy.deepcopy(_SELFTEST_PROVENANCE); prov_c["arm"] = "control"
        provenance_path.write_text(json.dumps(prov_c), encoding="utf-8")
        inputs = _make_inputs(leg, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path, readback_path, cell_dir,
                               arm="control", control_rerun_for=None)
        rc_b, v_b, _ = process_position(inputs, jsonl_path)
        report(
            "negative 9: --control-rerun-for set on an arm=v133 row is refused, and "
            "separately an arm=control row with it unset is refused",
            rc_a == 1 and any("control-rerun-for" in x for x in v_a)
            and rc_b == 1 and any("control-rerun-for" in x for x in v_b),
            f"a={v_a} b={v_b}",
        )

        # --- negative 10: provenance disagreement, both halves ---
        (leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path,
         readback_path, jsonl_path) = _leg("neg10a")
        prov_bad = copy.deepcopy(_SELFTEST_PROVENANCE)
        prov_bad.update({"position_id": "WRONG-POS", "arm": "control", "chip": "w29c020"})
        provenance_path.write_text(json.dumps(prov_bad), encoding="utf-8")
        inputs = _make_inputs(leg, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path, readback_path, cell_dir)
        rc_a, v_a, _ = process_position(inputs, jsonl_path)
        (leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path,
         readback_path, jsonl_path) = _leg("neg10b")
        prov_sha = copy.deepcopy(_SELFTEST_PROVENANCE); prov_sha["fw_sha"] = "totally-different-sha"
        provenance_path.write_text(json.dumps(prov_sha), encoding="utf-8")
        inputs = _make_inputs(leg, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path, readback_path, cell_dir)
        rc_b, v_b, _ = process_position(inputs, jsonl_path)
        report(
            "negative 10: provenance whose arm/position_id/chip disagree with the CLI "
            "arguments is refused with every disagreement named in one pass, and "
            "separately provenance whose fw_sha disagrees with pins.arms[arm].fw_sha "
            "is refused",
            rc_a == 1
            and any("WRONG-POS" in x and "control" in x and "w29c020" in x for x in v_a)
            and rc_b == 1 and any("fw_sha" in x and "totally-different-sha" in x for x in v_b),
            f"a={v_a} b={v_b}",
        )

        # --- negative 11: no judged readback result, blank human field, bare "not measured" ---
        (leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path,
         readback_path, jsonl_path) = _leg("neg11a")
        bad_readback = {"flashed_arm": "v133", "target": "leonardo",
                         "sha_actual_judged": None, "sha_whole_flash_unjudged": None,
                         "judged_span_bytes": 25098}
        readback_path.write_text(json.dumps(bad_readback), encoding="utf-8")
        inputs = _make_inputs(leg, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path, readback_path, cell_dir)
        rc_a, v_a, _ = process_position(inputs, jsonl_path)

        (leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path,
         readback_path, jsonl_path) = _leg("neg11b")
        inputs = _make_inputs(leg, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path, readback_path, cell_dir)
        inputs["verdict_text"] = ""
        rc_b, v_b, _ = process_position(inputs, jsonl_path)

        (leg, cell_dir, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path,
         readback_path, jsonl_path) = _leg("neg11c")
        inputs = _make_inputs(leg, config_dir, rj, rm, pins_path, arms_prov_path, provenance_path, readback_path, cell_dir)
        inputs["vpp_real_mv_raw"] = "not measured"
        rc_c, v_c, _ = process_position(inputs, jsonl_path)
        report(
            "negative 11: a read-back verdict with no judged result, a blank human "
            "field, and a bare 'not measured' with no reason are each refused by name",
            rc_a == 1 and any("judged result" in x for x in v_a)
            and rc_b == 1 and any("verdict" in x for x in v_b)
            and rc_c == 1 and any("neither a float" in x for x in v_c),
            f"a={v_a} b={v_b} c={v_c}",
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"append_chip_evidence.py --selftest overall: {'ok' if ok_overall else 'FAILED'}")
    return 0 if ok_overall else 1


if __name__ == "__main__":
    sys.exit(main())
