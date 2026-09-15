"""
Ledger self-consistency gate for PROTOCOL-LEDGER.json.

Loads three JSON inputs (env-overridable paths), runs the LEDGER-01/02/03 +
D-09 assertion set, and exits with one of three contract codes:

Exit codes:
  0 — all assertions pass; the ledger is structurally consistent.
  1 — at least one structural violation (join key unresolved, D-09 PASS
      constraint broken, D-04 no-copy SHA guard triggered, missing bucket,
      defect status_changed != false, invalid verification_status enum).
      This is the real BLOCK — investigate and fix the ledger before merge.
  2 — infrastructure error: a required input JSON (ledger, EVIDENCE.json, or
      validation_matrix_spec.json) could not be loaded or parsed. Distinct
      from 1 so a CI consumer does not confuse a missing input with a real
      structural BLOCK (WR-04).
"""

import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Env-overridable path constants
# ---------------------------------------------------------------------------
_LEDGER_DIR = os.path.join(os.path.dirname(__file__), "..")
_EVIDENCE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".planning", "v1.15", "bench")
_MATRIX_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "firestarter_app", "tools")

LEDGER_FILE = os.environ.get(
    "FIRESTARTER_LEDGER_FILE",
    os.path.join(_LEDGER_DIR, "PROTOCOL-LEDGER.json"),
)
EVIDENCE_FILE = os.environ.get(
    "FIRESTARTER_EVIDENCE_FILE",
    os.path.join(_EVIDENCE_DIR, "EVIDENCE.json"),
)
MATRIX_FILE = os.environ.get(
    "FIRESTARTER_MATRIX_FILE",
    os.path.join(_MATRIX_DIR, "validation_matrix_spec.json"),
)

# ---------------------------------------------------------------------------
# The 12 canonical buckets (LEDGER-03 / D-07)
# ---------------------------------------------------------------------------
_REQUIRED_BUCKETS = {
    "0x05", "0x06", "0x07", "0x08",
    "0x0B", "0x0D", "0x0E", "0x10",
    "0x27", "0x28", "0x29", "0x34",
}

# Buckets that must carry verification_status == "UNVERIFIED" (no on-hand silicon)
_UNVERIFIED_BUCKETS = {"0x0D", "0x0E", "0x10", "0x27", "0x29", "0x34"}

# Valid verification_status enum values
_VALID_STATUSES = {"PASS", "UNVERIFIED", "FAIL-INVESTIGATE", "open-defect-carried", "bench-pending"}

# Regex for a raw 64-hex SHA string (D-04 no-copy guard)
_RAW_SHA_RE = re.compile(r"\b[0-9a-f]{64}\b")


# ---------------------------------------------------------------------------
# Load helper (WR-04: exits 2 on load/parse failure, not 1)
# ---------------------------------------------------------------------------
def _load_db(path, label):
    """Load a JSON file, exiting 2 (infra error) on any load failure.

    WR-04: a missing/malformed input is an infrastructure problem, NOT a
    structural BLOCK -- it must use a distinct exit code (2) so a CI consumer
    keying on the exit status does not misreport it as a real gate failure.
    """
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: cannot load {label} {path}: {e}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Assertion helpers
# ---------------------------------------------------------------------------

def _assert_ledger01(ledger, evidence_chip_names, matrix_family_ids, violations):
    """LEDGER-01: join keys resolve + D-04 no-copy guard + all 12 buckets present."""

    # (a) All 12 buckets must be present exactly once
    row_buckets = [row.get("bucket") for row in ledger.get("rows", [])]
    bucket_set = set(row_buckets)
    missing = _REQUIRED_BUCKETS - bucket_set
    if missing:
        violations.append(
            f"LEDGER-01: missing buckets: {sorted(missing)}"
        )
    duplicates = [b for b in _REQUIRED_BUCKETS if row_buckets.count(b) > 1]
    if duplicates:
        violations.append(
            f"LEDGER-01: duplicate bucket rows: {sorted(duplicates)}"
        )

    # (b) matrix_family join key resolves (or is null for 0x34)
    for row in ledger.get("rows", []):
        fam = row.get("matrix_family")
        bucket = row.get("bucket", "<unknown>")
        if fam is not None and fam not in matrix_family_ids:
            violations.append(
                f"LEDGER-01: row bucket={bucket} matrix_family={fam!r} not in "
                f"validation_matrix_spec families: {sorted(matrix_family_ids)}"
            )

    # (c) evidence_chip join keys resolve
    for row in ledger.get("rows", []):
        bucket = row.get("bucket", "<unknown>")
        evidence = row.get("evidence")
        if not isinstance(evidence, dict):
            continue
        for cell_key in ("v1_15_read_cell", "v1_15_writecycle_cell"):
            cell = evidence.get(cell_key)
            if not isinstance(cell, dict):
                continue
            chip = cell.get("evidence_chip")
            if chip is not None and chip not in evidence_chip_names:
                violations.append(
                    f"LEDGER-01: row bucket={bucket} {cell_key}.evidence_chip={chip!r} "
                    f"not in EVIDENCE.json cells"
                )

    # (d) D-04 no-copy guard: no raw 64-hex SHA anywhere in the serialized ledger
    serialized = json.dumps(ledger)
    sha_matches = _RAW_SHA_RE.findall(serialized)
    if sha_matches:
        violations.append(
            f"LEDGER-01 (D-04): raw 64-hex SHA string(s) found in ledger "
            f"(no-copy guard violation): {sha_matches[:3]!r}"
            + (" ..." if len(sha_matches) > 3 else "")
        )


def _assert_ledger02_d09(ledger, violations):
    """LEDGER-02 / D-09: PASS rows must have oracle + non-empty evidence + both sha-match flags."""
    for row in ledger.get("rows", []):
        bucket = row.get("bucket", "<unknown>")
        status = row.get("verification_status")
        if status != "PASS":
            continue

        oracle = row.get("oracle")
        if oracle != "leonardo+Rev2.0":
            violations.append(
                f"LEDGER-02/D-09: PASS row bucket={bucket} missing or wrong oracle "
                f"(got {oracle!r}, expected 'leonardo+Rev2.0')"
            )

        evidence = row.get("evidence")
        if not isinstance(evidence, dict):
            violations.append(
                f"LEDGER-02/D-09: PASS row bucket={bucket} missing evidence block"
            )
            continue

        artifacts = evidence.get("p90_artifacts")
        if not artifacts:
            violations.append(
                f"LEDGER-02/D-09: PASS row bucket={bucket} evidence.p90_artifacts "
                f"is empty or absent"
            )

        # Phase 99 (v1.18-native graduation, 99-RESEARCH.md Pitfall 2): a chip
        # may have a v1.15 *read* baseline but no v1.15 *write* baseline (its
        # v1.15 write was a documented failure). In that case the graduation
        # oracle is self-consistency -- written-image SHA == read-back SHA on
        # THIS milestone's fixed firmware -- not "matches v1.15". Recognize
        # that shape via evidence.v1_18_writeverify_sha_selfconsistent and do
        # NOT demand a fabricated p90_writecycle_sha_matches_v115 claim.
        if evidence.get("v1_18_writeverify_sha_selfconsistent") is True:
            if evidence.get("p90_read_sha_matches_v115") is not True:
                violations.append(
                    f"LEDGER-02/D-09: PASS row bucket={bucket} "
                    f"evidence.p90_read_sha_matches_v115 is not true"
                )
        else:
            if evidence.get("p90_read_sha_matches_v115") is not True:
                violations.append(
                    f"LEDGER-02/D-09: PASS row bucket={bucket} "
                    f"evidence.p90_read_sha_matches_v115 is not true"
                )

            if evidence.get("p90_writecycle_sha_matches_v115") is not True:
                violations.append(
                    f"LEDGER-02/D-09: PASS row bucket={bucket} "
                    f"evidence.p90_writecycle_sha_matches_v115 is not true"
                )


def _assert_ledger03(ledger, violations):
    """LEDGER-03: UNVERIFIED set, defect status_changed=false, valid status enum."""

    rows = ledger.get("rows", [])

    # (a) Exactly the no-silicon buckets carry UNVERIFIED
    for row in rows:
        bucket = row.get("bucket", "<unknown>")
        status = row.get("verification_status")
        if bucket in _UNVERIFIED_BUCKETS and status != "UNVERIFIED":
            violations.append(
                f"LEDGER-03: bucket={bucket} expected verification_status='UNVERIFIED' "
                f"(no on-hand silicon), got {status!r}"
            )

    # (b) verification_status enum
    for row in rows:
        bucket = row.get("bucket", "<unknown>")
        status = row.get("verification_status")
        if status not in _VALID_STATUSES:
            violations.append(
                f"LEDGER-03: row bucket={bucket} invalid verification_status={status!r}; "
                f"must be one of {sorted(_VALID_STATUSES)}"
            )

    # (c) open_defects[].status_changed must be false
    for defect in ledger.get("open_defects", []):
        did = defect.get("id", "<unknown>")
        if defect.get("status_changed") is not False:
            violations.append(
                f"LEDGER-03: open_defect id={did!r} status_changed is not false "
                f"(defect rows must not silently change status)"
            )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Load inputs, run all three assertion groups, report, exit with contract code."""
    ledger = _load_db(LEDGER_FILE, "ledger")
    evidence = _load_db(EVIDENCE_FILE, "EVIDENCE")
    matrix = _load_db(MATRIX_FILE, "validation_matrix_spec")

    # Build join-key sets from the upstream sources
    evidence_chip_names = {cell["chip"] for cell in evidence.get("cells", []) if "chip" in cell}
    matrix_family_ids = {fam["id"] for fam in matrix.get("families", []) if "id" in fam}

    # Collect violations grouped by requirement
    ledger01_violations = []
    ledger02_violations = []
    ledger03_violations = []

    _assert_ledger01(ledger, evidence_chip_names, matrix_family_ids, ledger01_violations)
    _assert_ledger02_d09(ledger, ledger02_violations)
    _assert_ledger03(ledger, ledger03_violations)

    all_violations = ledger01_violations + ledger02_violations + ledger03_violations

    if all_violations:
        print("FAIL: ledger self-consistency check found violations:\n")
        if ledger01_violations:
            print("-- LEDGER-01 (join keys / bucket presence / D-04 no-copy guard) --")
            for v in ledger01_violations:
                print(f"  {v}")
            print()
        if ledger02_violations:
            print("-- LEDGER-02 / D-09 (PASS structural constraint) --")
            for v in ledger02_violations:
                print(f"  {v}")
            print()
        if ledger03_violations:
            print("-- LEDGER-03 (UNVERIFIED set / defect status_changed / status enum) --")
            for v in ledger03_violations:
                print(f"  {v}")
            print()
        print(f"Total: {len(all_violations)} violation(s). Exit 1 (BLOCK).")
        sys.exit(1)

    row_count = len(ledger.get("rows", []))
    defect_count = len(ledger.get("open_defects", []))
    print(
        f"PASS: ledger self-consistency check OK — "
        f"{row_count} rows, {defect_count} open_defects, "
        f"all LEDGER-01/02/03 + D-09 assertions satisfied."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
