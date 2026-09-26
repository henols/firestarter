---
phase: 85-datasheet-acquisition
reviewed: 2026-06-25T00:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - firestarter/datasheets/datasheets-check.sh
  - firestarter/datasheets/README.md
findings:
  critical: 0
  warning: 4
  info: 4
  total: 8
status: issues_found
---

# Phase 85: Code Review Report

**Reviewed:** 2026-06-25
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

Reviewed the only executable artifact in the phase, `datasheets-check.sh` (a `set -euo pipefail`
Wave-0 validation gate), plus the `README.md` datasheet index for factual consistency with the
committed tree. The script runs and returns PASS against the current tree, and the 12 bucket dirs
each hold at least one real `%PDF`-magic file as advertised.

No security findings (no network surface, no input parsing, no untrusted data — input is the repo's
own committed tree). No BLOCKER-class correctness defects: the gate fails closed on the cases it was
designed to catch.

However, the gate has several **false-PASS / false-FAIL robustness gaps** that undermine its value
as a phase gate. The most serious are: (1) the forbidden-bucket and exclusion checks use substring
`grep`/glob matching that will silently miss real violations or mis-trigger on superstrings; (2) the
`-size +1k` non-trivial-PDF threshold rejects legitimate small datasheets; and (3) the README→file
WARN loop runs in a pipe subshell, so even if it were ever upgraded to a hard check it could never
set `fail`. The soft README→source-URL-tail WARNs (`doc0006.pdf`, `m27c512.pdf`, etc.) are expected
behavior per the phase brief and are NOT flagged.

## Warnings

### WR-01: Forbidden/exclusion hex checks use unbounded substring matching (false-FAIL and false-PASS)

**File:** `firestarter/datasheets/datasheets-check.sh:62,66,72`
**Issue:** The forbidden-bucket loop matches with `compgen -G "$DS/${b}-*"` and `grep -q "$b"` on
the README. Both are unanchored substring matches over hex strings that are prefixes of one another
and of larger tokens:

- `grep -q "0x11"` matches any line containing `0x110`, `0x118`, `0x2A11`, etc. So the README could
  satisfy "mentions exclusion 0x11" via an *unrelated* token and never actually document the
  exclusion (false PASS of the DSHEET-03 exclusion requirement). Confirmed: `echo "0x110" | grep -q
  "0x11"` matches.
- Conversely, `compgen -G "$DS/0x2A-*"` only matches folders with a literal `-` after the hex; a
  stray forbidden folder named `0x2ABC` or `0x2A_GAL` (underscore) would slip past the forbidden
  check entirely (false PASS of the no-folder assertion).
- The forbidden set `0x05 0x06 ... 0x2C` shares prefixes (`0x2A`/`0x2B`/`0x2C`), so a malformed
  README mentioning only `0x2A` once could be miscredited.

This is the gate's weakest assertion: it is supposed to be a hard FAIL guard but its matching is too
loose in one direction and too strict in the other.
**Fix:** Anchor and word-bound the matches. For the README mention, match the documented row form,
e.g. `grep -qE "\`?${b}\`?[^0-9A-Fa-f]" "$DS/README.md"` (require a non-hex-digit boundary after the
hex). For the folder check, also catch suffix variants without a dash:

```bash
if compgen -G "$DS/${b}-*" >/dev/null 2>&1 \
   || compgen -G "$DS/${b}_*" >/dev/null 2>&1 \
   || compgen -G "$DS/${b}"   >/dev/null 2>&1; then
  echo "FAIL: forbidden bucket folder for $b exists under $DS/"
  fail=1
fi
```

### WR-02: `-size +1k` rejects legitimate small/valid PDFs (false-FAIL boundary bug)

**File:** `firestarter/datasheets/datasheets-check.sh:44,46`
**Issue:** The "non-trivial PDF" count uses `find ... -size +1k`, which is **strictly greater than
1024 bytes** (and rounds up by 1k blocks). A valid 1-page datasheet of exactly 1024 bytes — or any
small but genuine PDF — is counted as `n=0`, producing `FAIL: <dir> has no non-trivial PDF` even
though a real `%PDF` file is present. Confirmed: a 32-byte valid `%PDF-1.4` file yields `n=0`. The
intent (reject 0-byte / truncated stubs) does not require a 1KB floor; the separate `%PDF` magic
loop already rejects non-PDFs. The two checks are also redundant/inconsistent: `wc -l` counts by
size while the magic loop counts by content, so a directory containing only a >1k non-PDF passes the
count but fails magic — correct net result, but the count check adds no real coverage the magic
check lacks.
**Fix:** Drop the arbitrary 1KB floor; assert "at least one file passing the %PDF magic check"
instead. Reuse the magic loop's result, e.g. track a per-dir `pdf_ok` counter and FAIL the bucket
when it is 0. If a non-empty floor is desired, use `-size +0` (strictly non-empty) rather than `+1k`.

### WR-03: README→file consistency check is structurally incapable of failing (dead guard)

**File:** `firestarter/datasheets/datasheets-check.sh:84-88`
**Issue:** The loop runs `grep ... | sort -u | while read -r ref; do ...`. Because it is the right
side of a pipe, the `while` body executes in a **subshell**; any variable assignment made there
(including `fail=1`) is discarded when the subshell exits. Today the body only emits `WARN`, so this
is latent — but it is a trap: a future maintainer who upgrades this to a hard check (`fail=1`) will
get a gate that prints FAIL lines yet still exits 0. The comment at line 80 ("This is a soft WARN")
documents intent but not the structural constraint. Additionally, `find "$DS" -name "$ref"` searches
the *entire* tree, so a README reference is satisfied by a file in **any** bucket, not the bucket the
README associates it with — a misfiled PDF would not be detected.
**Fix:** Convert to a process-substitution loop so the body shares the parent shell, making future
hardening safe:

```bash
while read -r ref; do
  if ! find "$DS" -name "$ref" -print -quit | grep -q .; then
    echo "WARN: README references $ref but no such file found under $DS/"
  fi
done < <(grep -oE '[A-Za-z0-9_.-]+\.pdf' "$DS/README.md" | sort -u)
```

For per-bucket fidelity (optional), validate the README's `filename | bucket` provenance rows
against the actual containing directory rather than a tree-wide `find`.

### WR-04: `%PDF` magic check is not anchored to the file start

**File:** `firestarter/datasheets/datasheets-check.sh:51`
**Issue:** `head -c4 "$f" | grep -q '%PDF'` is correct only because exactly 4 bytes are piped; but
the pattern is unanchored, so the check is conceptually "do the first 4 bytes contain `%PDF`
anywhere," which for a 4-byte window is fine but masks intent. More importantly, a real PDF that
begins with a UTF-8 BOM (`EF BB BF`) before `%PDF` — which some scanners/CDNs emit — fails this gate
even though it is a valid PDF: the first 4 bytes are `EF BB BF 25`, no `%PDF`. Confirmed by test. The
gate would then hard-FAIL a legitimate committed datasheet.
**Fix:** Anchor and widen the read to tolerate a BOM, e.g. check the first 8 bytes and anchor to a
`%PDF` occurrence within the header:

```bash
if ! head -c8 "$f" | grep -qa '%PDF'; then
  echo "FAIL: $f is not a real PDF (no %PDF header)"
  fail=1
fi
```

Use `grep -a` so a binary-content false "binary file matches" path cannot suppress the match on some
grep builds.

## Info

### IN-01: SAFE-05 requirement is documented but not actually checked

**File:** `firestarter/datasheets/datasheets-check.sh:10-11`
**Issue:** The header claims to "cover" SAFE-05 ("only `datasheets/` is modified"), but the script
performs no git-diff or scope assertion — the comment itself says it confirms "tree shape is
consistent, not re-running git-diff." No code in the script tests that nothing outside `datasheets/`
changed. The requirement is effectively unverified by this gate; a reader may over-trust the PASS.
**Fix:** Either remove the SAFE-05 claim from the covered-requirements list, or add an explicit
(opt-in) `git diff --name-only` scope assertion so the claim is backed by code.

### IN-02: `.gitkeep` present after all buckets are populated (stale placeholder)

**File:** `firestarter/datasheets/.gitkeep` (observed in tree; referenced by README §Folder Tree)
**Issue:** A 0-byte `datasheets/.gitkeep` remains although every bucket dir now holds committed PDFs,
so the placeholder no longer serves a purpose. It is harmless to the gate (not a `*.pdf`), but it is
dead scaffolding and is not listed in the README Folder Tree, creating a minor index/tree mismatch.
**Fix:** Remove `datasheets/.gitkeep`, or document it in the README Folder Tree if intentionally
retained.

### IN-03: README presents 0x34 as a "live protocol bucket" but firmware routes it to not_implemented

**File:** `firestarter/datasheets/README.md:3,37,163`
**Issue:** The README opens by mapping "each of the 12 live protocol bucket folders," and lists 0x34
EEPROM-X88C64 among them with handler `configure_not_implemented() → not_implemented.cpp`. Per
`firestarter/CLAUDE.md`, 0x34 is **not** in the documented dispatch chain or `KNOWN_PROTOCOLS`; it
would reach the generic fail-closed guard (step 6b), identical to the "infeasible" 0x11/0x2A/0x2B/0x2C
buckets that the README places under **Exclusions**. Calling 0x34 a "live" bucket while the firmware
treats it as not-implemented is an internally inconsistent framing for a Phase 86/89 consumer. (The
per-row handler annotation is itself honest — this is a "live vs excluded" categorization mismatch,
not a wrong handler.)
**Fix:** Clarify 0x34's status — e.g. note it has a DB chip (X88C64) and a folder but is currently
routed to `configure_not_implemented` (DB-present-but-unimplemented), distinguishing it from both
the dispatched buckets and the no-DB exclusions.

### IN-04: Magic numbers / hardcoded bucket and forbidden lists duplicated from firmware

**File:** `firestarter/datasheets/datasheets-check.sh:33-35,62`
**Issue:** `expected_buckets` and `forbidden` are hand-maintained literal lists that duplicate the
protocol taxonomy owned by `firestarter/CLAUDE.md` / `KNOWN_PROTOCOLS`. There is no cross-check that
these lists stay in sync with the firmware source of truth, so a future protocol added/removed in the
firmware will silently diverge from this gate. Acceptable for a one-shot Wave-0 gate, but worth a
note so a later phase does not assume the gate auto-tracks the firmware.
**Fix:** Add a comment pointing at the authoritative list location, or (future) derive the expected
set from a generated manifest rather than a literal.

---

_Reviewed: 2026-06-25_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
