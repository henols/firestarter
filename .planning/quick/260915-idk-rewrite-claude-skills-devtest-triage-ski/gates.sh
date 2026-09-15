#!/usr/bin/env bash
# Invariance harness for the devtest-triage/SKILL.md STE rewrite (quick item 260915-idk).
# Runs every gate leg and prints one PASS/FAIL line per leg. Exits non-zero if any leg fails.
# Usage: bash gates.sh [--final]
#   --final : legs 9 and 10 are required to run (a SKIP counts as a FAIL). Task 3 uses this.
set -u

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/../../.." && pwd)"

SKILL="$ROOT/.claude/skills/devtest-triage/SKILL.md"
SELFTEST="$ROOT/.claude/skills/devtest-triage/scripts/test_supersede.py"
LINT="/home/vscode/.claude/skills/asd-ste100/scripts/ste-lint.py"

BEFORE="$DIR/skill-before.txt"
FENCE_BASE="$DIR/fences-baseline.txt"
TOKEN_TXT="$DIR/token-census.txt"
TOKEN_MD="$DIR/token-census.md"
CITE_DERIVED="$DIR/citations-derived.txt"
CITE_REMAP="$DIR/citation-remap.md"

FINAL=0
[ "${1:-}" = "--final" ] && FINAL=1

OVERALL_RC=0
fail() { OVERALL_RC=1; }

# Reserved-word list kept here, not hard-coded elsewhere in the plan.
BANNED_STRINGS=(
  "henols/firestarter_prom"
)
REQUIRED_STRINGS=(
  "henols/firestarter"
)

# ---------------------------------------------------------------------------
extract_fences() {
  awk '
  { stripped = $0; gsub(/^[ \t]+|[ \t]+$/, "", stripped) }
  stripped ~ /^(```|~~~)/ { print $0; infence = !infence; next }
  infence { print $0 }
  ' "$1"
}

# ---------------------------------------------------------------------------
leg1_lint() {
  local out rc
  out=$(python3 "$LINT" "$SKILL" 2>&1)
  rc=$?
  if [ $rc -eq 0 ] && printf '%s\n' "$out" | grep -qE '\(0 hard, baseline 0\)'; then
    echo "PASS leg1-ste-lint"
  else
    echo "FAIL leg1-ste-lint (exit=$rc)"
    printf '%s\n' "$out" | tail -8
    fail
  fi
}

# ---------------------------------------------------------------------------
leg2_fence() {
  if [ ! -f "$FENCE_BASE" ]; then
    echo "FAIL leg2-fence-sha ($FENCE_BASE missing)"
    fail
    return
  fi
  local live_sha base_sha
  live_sha=$(extract_fences "$SKILL" | sha256sum | awk '{print $1}')
  base_sha=$(sha256sum "$FENCE_BASE" | awk '{print $1}')
  if [ "$live_sha" = "$base_sha" ]; then
    echo "PASS leg2-fence-sha ($live_sha)"
  else
    echo "FAIL leg2-fence-sha live=$live_sha base=$base_sha"
    fail
  fi
}

# ---------------------------------------------------------------------------
leg3_selftest() {
  local tmp rc
  tmp=$(mktemp)
  python3 "$SELFTEST" >"$tmp" 2>&1
  rc=$?
  if [ $rc -eq 0 ] && grep -qF '6/6 cases behaved as specified' "$tmp"; then
    echo "PASS leg3-supersede-selftest"
  else
    echo "FAIL leg3-supersede-selftest (exit=$rc)"
    cat "$tmp"
    fail
  fi
  rm -f "$tmp"
}

# ---------------------------------------------------------------------------
leg4_tables() {
  local out rc
  out=$(python3 - "$SKILL" <<'PY'
import re, sys

CODE_FENCE = re.compile(r"^(```|~~~)")
TABLE_SEPARATOR_CELL = re.compile(r"^:?-{3,}:?$")

def split_table_row(line):
    left = len(line) - len(line.lstrip())
    right = len(line.rstrip())
    content = line[left:right]
    if "|" not in content:
        return None
    if content.startswith("|"):
        content = content[1:]
    if content.endswith("|"):
        content = content[:-1]
    raw_cells = re.split(r"(?<!\\)\|", content)
    if len(raw_cells) < 2:
        return None
    return [c.strip() for c in raw_cells]

path = sys.argv[1]
lines = open(path, encoding="utf-8").read().splitlines()
masked = []
in_fence = False
for line in lines:
    stripped = line.strip()
    if CODE_FENCE.match(stripped):
        in_fence = not in_fence
        masked.append("")
        continue
    masked.append("" if in_fence else line)

tables = []
i = 1
while i < len(masked):
    sep = split_table_row(masked[i])
    header = split_table_row(masked[i - 1])
    if (not sep or not header or len(sep) != len(header)
            or not all(TABLE_SEPARATOR_CELL.fullmatch(c) for c in sep)):
        i += 1
        continue
    cols = len(header)
    j = i + 1
    rows = 0
    while j < len(masked):
        row = split_table_row(masked[j])
        if not row or len(row) != cols:
            break
        rows += 1
        j += 1
    tables.append((i, cols, rows))
    i = j

expected = [(3, 5), (2, 6), (3, 3), (3, 11), (4, 10), (2, 13)]
got = [(c, r) for (_, c, r) in tables]
for t in tables:
    print("TABLE line=%d cols=%d rows=%d" % t)
if got == expected:
    print("OK")
    sys.exit(0)
else:
    print("MISMATCH expected=%r got=%r" % (expected, got))
    sys.exit(1)
PY
)
  rc=$?
  if [ $rc -eq 0 ]; then
    echo "PASS leg4-prose-tables"
  else
    echo "FAIL leg4-prose-tables"
    printf '%s\n' "$out"
    fail
  fi
}

# ---------------------------------------------------------------------------
gen_token_census() {
  python3 - "$SKILL" <<'PY'
import re, sys
CODE_FENCE = re.compile(r"^(```|~~~)")
TOK_RE = re.compile(r"\b(id|read|blank-check|write|verify|erase)(s|ing|ed|d)?\b", re.I)
path = sys.argv[1]
lines = open(path, encoding="utf-8").read().splitlines()
in_fence = False
for lineno, line in enumerate(lines, 1):
    stripped = line.strip()
    if CODE_FENCE.match(stripped):
        in_fence = not in_fence
        continue
    if in_fence:
        continue
    for m in TOK_RE.finditer(line):
        print(f"{lineno}\t{m.group(0)}\t{line.strip()}")
PY
}

leg5_token_census() {
  gen_token_census > "$TOKEN_TXT"
  local census_count=0
  census_count=$(wc -l < "$TOKEN_TXT" | tr -d ' ')

  if [ ! -f "$TOKEN_MD" ]; then
    echo "FAIL leg5-token-census ($TOKEN_MD missing)"
    fail
    return
  fi

  local out rc
  out=$(python3 - "$TOKEN_TXT" "$TOKEN_MD" <<'PY'
import re, sys

census_path, md_path = sys.argv[1], sys.argv[2]
census = []
with open(census_path, encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line:
            continue
        lineno, token, _src = line.split("\t", 2)
        census.append((lineno, token.lower()))

rows = []
with open(md_path, encoding="utf-8") as f:
    for raw in f:
        raw = raw.rstrip("\n")
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not cells or cells[0].lower() in ("#", ""):
            pass
        # skip separator rows like |---|---|
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            continue
        # skip header row (first data-shaped row whose 2nd cell is literally "Line")
        if len(cells) >= 2 and cells[1].strip().lower() == "line":
            continue
        rows.append(cells)

if len(rows) != len(census):
    print(f"MISMATCH row_count census={len(census)} md={len(rows)}")
    sys.exit(1)

forbidden_hits = []
for idx, ((c_line, c_token), cells) in enumerate(zip(census, rows), 1):
    if len(cells) < 4:
        print(f"MISMATCH row {idx} has fewer than 4 columns: {cells}")
        sys.exit(1)
    _, m_line, m_token, m_class = cells[0], cells[1], cells[2], cells[3]
    if m_line.strip() != c_line:
        print(f"MISMATCH row {idx} line: census={c_line} md={m_line}")
        sys.exit(1)
    if m_token.strip("` ").lower() != c_token:
        print(f"MISMATCH row {idx} token: census={c_token} md={m_token}")
        sys.exit(1)
    if m_class.strip().upper() == "VERB":
        forbidden_hits.append((m_line, m_token))

if forbidden_hits:
    print(f"FORBIDDEN class VERB present: {forbidden_hits}")
    sys.exit(1)

print(f"OK {len(rows)} occurrences classified, 0 forbidden")
sys.exit(0)
PY
)
  rc=$?
  if [ $rc -eq 0 ]; then
    echo "PASS leg5-token-census ($out)"
  else
    echo "FAIL leg5-token-census"
    printf '%s\n' "$out"
    fail
  fi
}

# ---------------------------------------------------------------------------
leg6_triggers() {
  local desc
  desc=$(sed -n '3p' "$SKILL")
  local objs=(
    "dev test issues"
    "the chip test reports"
    "an EPROM against its datasheet"
    "the pin map or VPP for a chip"
    "passing validation issues"
    "failures that later passed"
    "[dev test] at28c256"
  )
  local missing=()
  for obj in "${objs[@]}"; do
    if ! printf '%s' "$desc" | grep -qF "$obj"; then
      missing+=("$obj")
    fi
  done
  if [ ${#missing[@]} -eq 0 ]; then
    echo "PASS leg6-trigger-phrases"
  else
    echo "FAIL leg6-trigger-phrases missing: ${missing[*]}"
    fail
  fi
}

# ---------------------------------------------------------------------------
leg7_frontmatter_structural() {
  local line1 line3 line4 ok=1
  line1=$(sed -n '1p' "$SKILL")
  line3=$(sed -n '3p' "$SKILL")
  line4=$(sed -n '4p' "$SKILL")
  local total_frontmatter_lines
  total_frontmatter_lines=$(awk '/^---$/{c++; if(c==2){print NR; exit}}' "$SKILL")

  [ "$line1" = "---" ] || ok=0
  [ "$line4" = "---" ] || ok=0
  [ "$total_frontmatter_lines" = "4" ] || ok=0
  case "$line3" in
    "description:"*) ;;
    *) ok=0 ;;
  esac
  local value="${line3#description:}"
  value="${value# }"
  if printf '%s' "$value" | grep -qF ': '; then
    ok=0
  fi
  if [ "$ok" = "1" ]; then
    echo "PASS leg7-frontmatter-structural"
  else
    echo "FAIL leg7-frontmatter-structural line1='$line1' line4='$line4' frontmatter_close_at=$total_frontmatter_lines line3='$line3'"
    fail
  fi
}

# ---------------------------------------------------------------------------
leg8_rename() {
  local ok=1
  for req in "${REQUIRED_STRINGS[@]}"; do
    grep -qF -- "$req" "$SKILL" || ok=0
  done
  for banned in "${BANNED_STRINGS[@]}"; do
    grep -qF -- "$banned" "$SKILL" && ok=0
  done
  if [ "$ok" = "1" ]; then
    echo "PASS leg8-repo-slug"
  else
    echo "FAIL leg8-repo-slug"
    fail
  fi
}

# ---------------------------------------------------------------------------
derive_citations() {
  python3 - "$ROOT" "$DIR" <<'PY'
import glob, os, re, sys

root, own_dir = sys.argv[1], sys.argv[2]
own_rel = os.path.relpath(own_dir, root)

FULL_RE = re.compile(r'devtest-triage/SKILL\.md:(\d+(?:-\d+)?)')
SHORT_RE = re.compile(r'`:(\d+(?:-\d+)?)`')

exclude_prefixes = ('.planning/graphs/', own_rel + '/')

records = []
for path in sorted(glob.glob(os.path.join(root, '.planning', '**', '*.md'), recursive=True)):
    rel = os.path.relpath(path, root)
    if any(rel.startswith(p) for p in exclude_prefixes):
        continue
    with open(path, encoding='utf-8', errors='replace') as f:
        lines = f.read().splitlines()
    for lineno, line in enumerate(lines, 1):
        fulls = FULL_RE.findall(line)
        if not fulls:
            continue
        shorts = SHORT_RE.findall(line)
        for tgt in fulls:
            records.append((rel, lineno, tgt, 'full'))
        for tgt in shorts:
            records.append((rel, lineno, tgt, 'shorthand'))

for r in records:
    print('\t'.join(str(x) for x in r))
PY
}

leg9_citation_enum() {
  derive_citations | sort > "$CITE_DERIVED"
  local derived_count
  derived_count=$(wc -l < "$CITE_DERIVED" | tr -d ' ')

  if [ ! -f "$CITE_REMAP" ]; then
    if [ "$FINAL" = "1" ]; then
      echo "FAIL leg9-citation-enum ($CITE_REMAP missing, --final requires it)"
      fail
    else
      echo "SKIP leg9-citation-enum ($CITE_REMAP absent — task 3 not yet run)"
    fi
    return
  fi

  local out rc
  out=$(python3 - "$CITE_DERIVED" "$CITE_REMAP" <<'PY'
import re, sys

derived_path, remap_path = sys.argv[1], sys.argv[2]
derived = set()
derived_list = []
with open(derived_path, encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line:
            continue
        parts = tuple(line.split("\t"))
        derived.add(parts)
        derived_list.append(parts)

VALID_DISPOSITIONS = {"unmoved", "retargeted", "anchor", "pre-existing-stale"}

rows = []
with open(remap_path, encoding="utf-8") as f:
    for raw in f:
        stripped = raw.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            continue
        if len(cells) >= 2 and cells[0].lower() in ("citing file", "citing_file"):
            continue
        if len(cells) < 7:
            continue
        rows.append(cells)

remap_keys = set()
bad_disposition = []
for cells in rows:
    citing_file, citing_line, old_target, shape = cells[0], cells[1], cells[2], cells[3]
    disposition = cells[5]
    key = (citing_file, citing_line, old_target, shape)
    remap_keys.add(key)
    if disposition not in VALID_DISPOSITIONS:
        bad_disposition.append((key, disposition))

missing = derived - remap_keys
extra = remap_keys - derived

if bad_disposition:
    print(f"BAD DISPOSITION: {bad_disposition}")
    sys.exit(1)
if missing:
    print(f"MISSING rows for derived targets: {sorted(missing)}")
    sys.exit(1)
if extra:
    print(f"EXTRA rows not in derivation: {sorted(extra)}")
    sys.exit(1)

print(f"OK {len(derived_list)} derived targets, {len(rows)} remap rows, 1:1")
sys.exit(0)
PY
)
  rc=$?
  if [ $rc -eq 0 ]; then
    echo "PASS leg9-citation-enum ($derived_count derived targets) ($out)"
  else
    echo "FAIL leg9-citation-enum"
    printf '%s\n' "$out"
    fail
  fi
}

# ---------------------------------------------------------------------------
leg10_roundtrip() {
  if [ ! -f "$CITE_REMAP" ]; then
    if [ "$FINAL" = "1" ]; then
      echo "FAIL leg10-roundtrip ($CITE_REMAP missing, --final requires it)"
      fail
    else
      echo "SKIP leg10-roundtrip ($CITE_REMAP absent — task 3 not yet run)"
    fi
    return
  fi

  local out rc
  out=$(python3 - "$BEFORE" "$SKILL" "$CITE_REMAP" "$ROOT" <<'PY'
import re, subprocess, sys

before_path, live_path, remap_path, root = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
before_lines = open(before_path, encoding="utf-8").read().splitlines()
live_lines = open(live_path, encoding="utf-8").read().splitlines()

def get_line(lines, n):
    if n < 1 or n > len(lines):
        return None
    return lines[n - 1]

def parse_range(target):
    if "-" in target:
        a, b = target.split("-", 1)
        return int(a), int(b)
    n = int(target)
    return n, n

def nearest_heading(lines, n):
    for i in range(min(n, len(lines)) - 1, -1, -1):
        line = lines[i]
        if line.lstrip().startswith("#"):
            return line.strip()
    return None

rows = []
with open(remap_path, encoding="utf-8") as f:
    for raw in f:
        stripped = raw.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            continue
        if len(cells) >= 2 and cells[0].lower() in ("citing file", "citing_file"):
            continue
        if len(cells) < 7:
            continue
        rows.append(cells)

failures = []
checked = 0
for cells in rows:
    citing_file, citing_line, old_target, shape, new_target, disposition, evidence = cells[:7]
    checked += 1
    if disposition in ("unmoved", "retargeted"):
        old_a, old_b = parse_range(old_target)
        new_a, new_b = parse_range(new_target)
        old_text_a = get_line(before_lines, old_a)
        new_text_a = get_line(live_lines, new_a)
        old_text_b = get_line(before_lines, old_b)
        new_text_b = get_line(live_lines, new_b)
        if old_text_a != new_text_a:
            failures.append((citing_file, citing_line, "start-endpoint", old_a, new_a, old_text_a, new_text_a))
        if old_text_b != new_text_b:
            failures.append((citing_file, citing_line, "end-endpoint", old_b, new_b, old_text_b, new_text_b))
        if disposition == "unmoved" and (old_a, old_b) != (new_a, new_b):
            failures.append((citing_file, citing_line, "unmoved-claim-but-numbers-differ", old_target, new_target, None, None))
    elif disposition == "anchor":
        if not evidence.strip():
            failures.append((citing_file, citing_line, "anchor-missing-reason", old_target, new_target, None, None))
            continue
        new_a, _ = parse_range(new_target)
        old_a, _ = parse_range(old_target)
        if get_line(live_lines, new_a) is None:
            failures.append((citing_file, citing_line, "anchor-new-line-missing", old_target, new_target, None, None))
            continue
        old_heading = nearest_heading(before_lines, old_a)
        new_heading = nearest_heading(live_lines, new_a)
        if old_heading != new_heading:
            failures.append((citing_file, citing_line, "anchor-heading-mismatch", old_target, new_target, old_heading, new_heading))
    elif disposition == "pre-existing-stale":
        if old_target != new_target:
            failures.append((citing_file, citing_line, "pre-existing-stale-target-changed", old_target, new_target, None, None))
            continue
        rc = subprocess.run(
            ["git", "-C", root, "diff", "--quiet", "--", citing_file],
            capture_output=True,
        )
        if rc.returncode != 0:
            failures.append((citing_file, citing_line, "pre-existing-stale-file-modified", old_target, new_target, None, None))
    else:
        failures.append((citing_file, citing_line, "bad-disposition", old_target, new_target, disposition, None))

if failures:
    for f in failures:
        print("ROUNDTRIP FAIL:", f)
    sys.exit(1)

print(f"OK {checked} rows round-tripped")
sys.exit(0)
PY
)
  rc=$?
  if [ $rc -eq 0 ]; then
    echo "PASS leg10-roundtrip ($out)"
  else
    echo "FAIL leg10-roundtrip"
    printf '%s\n' "$out"
    fail
  fi
}

# ---------------------------------------------------------------------------
echo "=== gates.sh $( [ "$FINAL" = 1 ] && echo '--final' ) ==="
leg1_lint
leg2_fence
leg3_selftest
leg4_tables
leg5_token_census
leg6_triggers
leg7_frontmatter_structural
leg8_rename
leg9_citation_enum
leg10_roundtrip
echo "=== overall: $( [ $OVERALL_RC -eq 0 ] && echo PASS || echo FAIL ) ==="
exit $OVERALL_RC
