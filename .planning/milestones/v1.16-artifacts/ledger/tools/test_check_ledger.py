"""
pytest coverage for check_ledger.py — proves the 0/1/2 exit-code contract.

Drives the checker via subprocess.run() with env-overridable path constants
so each test controls exactly which fixture files are loaded.  All fixtures
live under tests/fixtures/; the failure-case tests mutate a copy of the valid
ledger in a tmp file rather than adding per-violation fixture files.

Tests:
  1. Exit 0 — a minimal valid ledger (all 12 buckets, PASS rows with full
     oracle/evidence/sha-match flags, UNVERIFIED no-silicon buckets,
     open_defects with status_changed=false, no raw SHAs).
  2. Exit 1 — a PASS row with the oracle field missing (D-09 violation).
  3. Exit 1 — a ledger containing a raw 64-hex SHA string (D-04 violation).
  4. Exit 1 — a ledger row with a matrix_family not present in the matrix
     fixture (LEDGER-01 join-key violation).
  5. Exit 2 — FIRESTARTER_LEDGER_FILE points at a missing path (load error).
  6. Exit 0 — a v1.18-native `0x08` graduation (self-consistent write/read-back
     SHA, no v1.15 write baseline) (Phase 99 / D-09 schema extension).
  7. Exit 1 — a `0x08` PASS row claiming graduation WITHOUT the
     v1_18_writeverify_sha_selfconsistent evidence (honesty guard).
  8. Exit 0 — the v1.18-native `0x08` graduation with the FUT-06 open_defect
     removed entirely (retirement-by-removal, not status_changed flip).
"""

import json
import os
import subprocess
import sys
import tempfile

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_CHECKER = os.path.join(_HERE, "check_ledger.py")
_FIXTURES = os.path.join(_HERE, "fixtures")
_LEDGER_VALID = os.path.join(_FIXTURES, "ledger_valid.json")
_EVIDENCE_MIN = os.path.join(_FIXTURES, "evidence_min.json")
_MATRIX_MIN = os.path.join(_FIXTURES, "matrix_min.json")


def _run_checker(ledger_path, evidence_path=None, matrix_path=None):
    """Invoke check_ledger.py with the given file paths via env vars."""
    env = os.environ.copy()
    env["FIRESTARTER_LEDGER_FILE"] = ledger_path
    env["FIRESTARTER_EVIDENCE_FILE"] = evidence_path or _EVIDENCE_MIN
    env["FIRESTARTER_MATRIX_FILE"] = matrix_path or _MATRIX_MIN
    result = subprocess.run(
        [sys.executable, _CHECKER],
        env=env,
        capture_output=True,
        text=True,
    )
    return result


def _write_tmp_ledger(data):
    """Write a ledger dict to a named temp file and return its path.

    The caller is responsible for deleting the file (use with try/finally or
    the tmp_ledger_file fixture).
    """
    fd, path = tempfile.mkstemp(suffix=".json", prefix="ledger_test_")
    try:
        os.write(fd, json.dumps(data).encode("utf-8"))
    finally:
        os.close(fd)
    return path


def _load_valid_ledger():
    with open(_LEDGER_VALID, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Test 1: valid ledger → exit 0
# ---------------------------------------------------------------------------
def test_valid_ledger_exits_0():
    """A minimal well-formed ledger satisfies all LEDGER-01/02/03 assertions → exit 0."""
    result = _run_checker(_LEDGER_VALID)
    assert result.returncode == 0, (
        f"Expected exit 0 but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# Test 2: PASS row missing oracle → exit 1  (LEDGER-02 / D-09 violation)
# ---------------------------------------------------------------------------
def test_pass_row_missing_oracle_exits_1():
    """A PASS row without oracle='leonardo+Rev2.0' is a D-09 structural violation → exit 1."""
    ledger = _load_valid_ledger()
    # Find the first PASS row and remove its oracle field
    for row in ledger["rows"]:
        if row.get("verification_status") == "PASS":
            row.pop("oracle", None)
            break

    path = _write_tmp_ledger(ledger)
    try:
        result = _run_checker(path)
    finally:
        os.unlink(path)

    assert result.returncode == 1, (
        f"Expected exit 1 but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# Test 3: raw 64-hex SHA copied into a row → exit 1  (D-04 no-copy guard)
# ---------------------------------------------------------------------------
def test_raw_sha_in_ledger_exits_1():
    """A 64-char hex string in the ledger body triggers the D-04 no-copy guard → exit 1."""
    # This is a fake SHA (safe to include in test source — it is 64 chars of hex but is
    # NOT a real hash of anything, and it lives in test code, not in the ledger fixture).
    FAKE_SHA = "a" * 64  # 64 'a' chars — matches [0-9a-f]{64}
    ledger = _load_valid_ledger()
    # Inject the fake SHA into a note field on the first row
    ledger["rows"][0]["_test_injected_sha"] = FAKE_SHA

    path = _write_tmp_ledger(ledger)
    try:
        result = _run_checker(path)
    finally:
        os.unlink(path)

    assert result.returncode == 1, (
        f"Expected exit 1 (D-04 no-copy guard) but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# Test 4: matrix_family not in matrix fixture → exit 1  (LEDGER-01 join key)
# ---------------------------------------------------------------------------
def test_bad_matrix_family_exits_1():
    """A matrix_family value absent from the matrix fixture is a LEDGER-01 violation → exit 1."""
    ledger = _load_valid_ledger()
    # Mutate the first non-null matrix_family to an unknown value
    for row in ledger["rows"]:
        if row.get("matrix_family") is not None:
            row["matrix_family"] = "nonexistent_family_xyz"
            break

    path = _write_tmp_ledger(ledger)
    try:
        result = _run_checker(path)
    finally:
        os.unlink(path)

    assert result.returncode == 1, (
        f"Expected exit 1 (LEDGER-01 bad matrix_family) but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# Test 5: missing ledger path → exit 2  (load error)
# ---------------------------------------------------------------------------
def test_missing_ledger_file_exits_2():
    """When FIRESTARTER_LEDGER_FILE points at a non-existent path, the checker exits 2."""
    result = _run_checker("/nonexistent/path/no_such_ledger.json")
    assert result.returncode == 2, (
        f"Expected exit 2 (load error) but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# Helpers for the Phase-99 0x08 v1.18-native graduation tests
# ---------------------------------------------------------------------------
def _find_0x08_row(ledger):
    for row in ledger["rows"]:
        if row.get("bucket") == "0x08":
            return row
    raise AssertionError("fixture has no bucket=0x08 row")


def _graduate_0x08_row(row):
    """Mutate a 0x08 row in-place into a v1.18-native graduation (Test A shape).

    No v1.15 write baseline exists for AM27C020 (its v1.15 write was the
    0-bits failure) — self-consistency (written-image SHA == read-back SHA
    on the Phase-98 fixed firmware) is the graduation oracle instead of
    "matches v1.15". SHAs are referenced by artifact path only (D-04).
    """
    row["verification_status"] = "PASS"
    row["oracle"] = "leonardo+Rev2.0"
    row["on_hand_chip"] = "AM27C020"
    row["evidence"] = {
        "v1_18_writeverify_sha_selfconsistent": True,
        "p90_read_sha_matches_v115": True,
        "p90_artifacts": [".planning/milestones/v1.18-artifacts/bench/AM27C020-graduation/"],
    }


# ---------------------------------------------------------------------------
# Test 6: v1.18-native 0x08 graduation (self-consistent, no v1.15 write
# baseline) → exit 0  (Phase 99 / D-09 schema extension)
# ---------------------------------------------------------------------------
def test_0x08_v1_18_native_graduation_exits_0():
    """A v1.18-native 0x08 graduation (written-image SHA == read-back SHA on
    the fixed firmware, no v1.15 write baseline) passes the gate at exit 0."""
    ledger = _load_valid_ledger()
    row = _find_0x08_row(ledger)
    _graduate_0x08_row(row)

    path = _write_tmp_ledger(ledger)
    try:
        result = _run_checker(path)
    finally:
        os.unlink(path)

    assert result.returncode == 0, (
        f"Expected exit 0 (v1.18-native 0x08 graduation) but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# Test 7: 0x08 PASS row WITHOUT the self-consistency evidence → exit 1
# (honesty guard — the extension must not admit a bare PASS claim)
# ---------------------------------------------------------------------------
def test_0x08_pass_without_selfconsistency_exits_1():
    """A 0x08 PASS row missing v1_18_writeverify_sha_selfconsistent must still
    fail the gate — the honesty guard holds (no dishonest v1.15-write-baseline
    fabrication, and no free pass either)."""
    ledger = _load_valid_ledger()
    row = _find_0x08_row(ledger)
    _graduate_0x08_row(row)
    # Omit the self-consistency marker entirely (Test B).
    del row["evidence"]["v1_18_writeverify_sha_selfconsistent"]

    path = _write_tmp_ledger(ledger)
    try:
        result = _run_checker(path)
    finally:
        os.unlink(path)

    assert result.returncode == 1, (
        f"Expected exit 1 (0x08 PASS without self-consistency evidence) but got "
        f"{result.returncode}.\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# Test 8: 0x08 graduation + FUT-06 removed from open_defects[] → exit 0
# (retirement-by-removal, not by flipping status_changed)
# ---------------------------------------------------------------------------
def test_0x08_graduation_with_fut06_removed_exits_0():
    """Retiring FUT-06 by removing its block from open_defects[] (not by
    flipping status_changed) still satisfies the gate at exit 0."""
    ledger = _load_valid_ledger()
    row = _find_0x08_row(ledger)
    _graduate_0x08_row(row)
    ledger["open_defects"] = [
        d for d in ledger.get("open_defects", []) if d.get("id") != "FUT-06"
    ]

    path = _write_tmp_ledger(ledger)
    try:
        result = _run_checker(path)
    finally:
        os.unlink(path)

    assert result.returncode == 0, (
        f"Expected exit 0 (0x08 graduation + FUT-06 retired by removal) but got "
        f"{result.returncode}.\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
