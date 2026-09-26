# Phase 160: RIG — Dual-Arm Build, Flash Provenance & the Shared Cell Procedure - Pattern Map

**Mapped:** 2026-08-26
**Files analyzed:** 17 new (12 tools/scripts, 2 evidence-substrate, 1 procedure doc, 7 committed binary artifact classes) + 1 modified
**Analogs found:** 13 / 17 with a same-role analog · **4 have NO analog in the tree** (every path that shells out to `avrdude`, plus the JSONL→Markdown renderer's diff-vs-committed leg)

**Boundary confirmed.** Every file below lands under `.planning/v1.34/`. The one file touched outside it is
`.planning/todos/pending/avrdude-mcu-detection-fallback.md` — a front-matter/annotation edit, still inside
`.planning/`. **No file in `firestarter/` or `firestarter_app/` is created or modified.** Both sub-repos appear
below only as *read-only reference analogs*; if a plan maps an analog into a sub-repo as a modification target,
that is a boundary breach to report, not a mapping to make (CONTEXT §Phase Boundary, REQUIREMENTS Out of Scope).

---

## Findings that change the mapping

Report these to the planner before it assigns analogs:

1. **The gate-script analog set splits in two, and RESEARCH.md names only the older half.**
   `.planning/v1.18/bench/check_*.py` (5 files, 282 lines total) is the *shape* precedent — `def main() -> int`,
   judged by exit code — but **none of the five takes an argument at all**: each hardcodes a repo-relative
   `EV = ".planning/v1.18/bench/EVIDENCE.json"` and is therefore cwd-dependent on `/workspaces`.
   `.planning/v1.33/tools/` is the *closer* analog for every Phase 160 tool that takes arguments: 8 argparse
   tools, milestone-level, JSONL-substrate, atomic writes, a `_schema` header record, and a serialize-then-scan
   self-check. **Use v1.18 for the verdict/exit-code idiom and v1.33 for argument handling and JSONL.**

2. **`.planning/v1.33/tools/` ships 7 `test_*.py` pytest files and a `.pytest_cache/`, yet `pytest` is NOT
   importable from `python3` in this container** (`ModuleNotFoundError`, verified). RESEARCH.md's "the meta repo
   has no test framework" is true of the *interpreter*, false of the *tree*. Those tests were run in some other
   environment and are currently unrunnable. **Do not copy the `test_*.py` pattern for Phase 160 tools** — it
   would produce dead tests. Use `extract_frames.py`'s in-file `--selftest` mode instead (analog below), which
   runs under plain `python3` and is asserted by exit code.

3. **CONTEXT.md's `gen_test_image.py` citation is wrong** and RESEARCH.md already corrected it. The generator to
   copy is `.planning/phases/145-bench-validation/images/gen_addr_image.py`. This pattern map assigns that file.

4. **`sys.exit(main())` is the actual majority convention, not `raise SystemExit(main())`.**
   `raise SystemExit(main(sys.argv))` appears in the two Phase 145 tools; `sys.exit(main())` appears in all five
   v1.18 gates, in v1.33's `strip_provenance.py`/`check_dead05_phrasing.py`, and in `tools/catalog/codegen.py`.
   Either is in-repo precedent; the planner should pin one and say so, because a `160-PLAN` verify leg that greps
   for the wrong one will fail on correct code.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `tools/gen_addr_image.py` | utility (generator) | transform → file-I/O | `.planning/phases/145-bench-validation/images/gen_addr_image.py` | **verbatim copy** (exact) |
| `tools/gate_record.py` | test/gate | batch validate | `.planning/v1.18/bench/check_graduation.py` + `build_citation_manifest.py:self_check` | exact |
| `tools/judge_wrv.py` | service (judge) | file-I/O → verdict | `.planning/v1.18/bench/check_signature.py` (SHA-consistency judging) | role-match |
| `tools/check_rebuild.py` | test/gate | batch compare | `.planning/v1.7/phase-33-baseline-hex/check-migration.sh` Assertion 3 (`cmp` per env) | exact (in bash) |
| `tools/render_evidence.py` | utility (renderer) | transform, JSONL → MD | `tools/catalog/codegen.py` (determinism contract + `--check`) | role-match; **`--check`-diffs-committed leg has no analog** |
| `bench/EVIDENCE.jsonl` | model (record substrate) | append-only log | `.planning/v1.33/sweep-citation-manifest.jsonl` (shape) + `.planning/v1.15/bench/EVIDENCE.json` (columns) | split analog, both exact |
| `bench/EVIDENCE.md` | doc (rendered) | transform output | `.planning/v1.18/bench/EVIDENCE.md` | exact |
| `tools/capture_provenance.py` | service (collector) | request-response (subprocess fan-out) | `.planning/v1.33/tools/build_citation_manifest.py` (`_git_head`, header record, atomic write) | role-match; **avrdude leg unanalogged** |
| `tools/probe_board.py` | service (probe) | request-response | **NO ANALOG** — closest is `firestarter_app/firestarter/avr_tool.py` (product code, read-only) + the pending todo's sketch | partial |
| `tools/judge_readback.py` | service (judge) | file-I/O → verdict | **NO ANALOG for the avrdude read**; the compare half maps to `check-migration.sh` Assertion 3 | partial |
| `tools/touch_1200.py` | utility | event (serial side-effect) | `firestarter_app/firestarter/avr_tool.py:114-121` `_trigger_reset` (read-only reference) | partial |
| `tools/run_gates.sh` | config (runner) | batch | `.planning/v1.4-e2e-verify.sh` (header/usage/exit-code contract) | role-match |
| `PROCEDURE.md` | doc (procedure) | — | `.planning/phases/145-bench-validation/145-BENCH-LOG.md` (discipline prose); **no arm-agnostic procedure doc exists** | partial |
| `images/*.hex` (6) | artifact | file-I/O | `.planning/v1.7/phase-33-baseline-hex/{uno,uno328pb,leonardo}.hex` | exact — **but those were gitignored; these are committed** |
| `images/SHA256SUMS.txt` | artifact manifest | — | `.planning/phases/145-bench-validation/SHA256SUMS.txt` | exact |
| `bench/cells/<cell-id>/…` | artifact layout | file-I/O | `.planning/phases/145-bench-validation/{images,readbacks,runs,logs}/` | role-match (flattened → per-cell) |
| `.planning/todos/pending/avrdude-mcu-detection-fallback.md` **(modified)** | doc (todo) | — | its own front matter | n/a |

---

## Pattern Assignments

### `tools/gen_addr_image.py` (utility, transform) — **copy verbatim**

**Analog:** `.planning/phases/145-bench-validation/images/gen_addr_image.py` (79 lines, read in full)

This is a copy, not a rewrite. Two things must survive the copy and one decision must be made.

**The D-16 boundary comment — this is the pattern for how a copied rig tool declares its boundary** (lines 4-9):

```python
"""gen_addr_image.py -- word-stamped, address-attributable bench write image generator.

D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It is authored and lives
only under .planning/phases/145-bench-validation/images/ in the meta repo. It must NEVER be
copied into firestarter/ or firestarter_app/ (in particular not into firestarter_app/tools/,
alongside the existing firestarter_app/tools/gen_test_image.py) -- this phase changes no
firmware and no host source (D-16). Nothing here is imported by, or imports from, either
sub-repo.
```

The copy must re-path the "lives only under" clause to `.planning/v1.34/tools/` — leaving the Phase 145 path in
place would make the comment false, and a false boundary comment is worse than none. **Every other new tool in
this phase should carry an adapted version of this paragraph**; it is the phase's only in-source enforcement of
the no-product-code rule.

**Core pattern** (lines 30-36) and the decode helper (39-54), unchanged:

```python
def gen_image(size: int, mask: int) -> bytes:
    """Return `size` bytes of the word-stamped address pattern, XORed with `mask`."""
    b = bytearray(size)
    for n in range(size):
        stamp = (n >> 8) & 0xFF if (n & 1) else (n & 0xFF)
        b[n] = stamp ^ mask
    return bytes(b)
```

**CLI + verdict line** (lines 57-79) — positional argv, no argparse, exit 2 on usage:

```python
def main(argv: list) -> int:
    if len(argv) != 4:
        sys.stderr.write(f"usage: {argv[0]} <size_bytes> <mask_hex_or_dec> <output_path>\n")
        return 2
    size = int(argv[1], 0)
    mask = int(argv[2], 0) & 0xFF
    ...
    print(f"{out_path}: {size} bytes, mask=0x{mask:02X}, sha256={digest}, 0xFF_count={ff_count}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

**Open decision the copy forces** (RESEARCH.md §Correction): the stamp encodes only 16 address bits, so on the
262144 B W29C020 the pattern repeats every 64 KiB and an A16/A17 alias is invisible to attribution. Extend the
stamp to carry all 18 bits, or record the limitation as a stated non-claim. `mask` is 8 bits → 256 distinct
images, which covers D-12's 20.

---

### `tools/gate_record.py` (test/gate, batch validate)

**Analog A — the verdict idiom:** `.planning/v1.18/bench/check_graduation.py` (112 lines, read in full)

**Required-field + placeholder pattern** (lines 27-47, 63-68) — note the field lists as module constants, and
that "missing" and "still a placeholder" are deliberately the *same* failure:

```python
REQ_COMMON = ["controller", "port", "r1_readback", "r2_readback", "fw_commit", "vpp_adc_mv", "verdict"]
REQ_PASS   = ["write_image_sha256", "readback_sha256"]
REQ_DEFER  = ["bits_flipped", "post_read_sha256"]

def _is_tbd(value: object) -> bool:
    """True if the field is missing or still carries a TBD placeholder."""
    return "TBD" in str(value if value is not None else "TBD")

    missing_common = [k for k in REQ_COMMON if _is_tbd(cell.get(k))]
    if missing_common:
        print(f"FAIL: bench-discipline fields unfilled: {missing_common}", file=sys.stderr)
        return 1
```

**Branch-dependent required sets + a self-consistency assertion** (lines 70-108) — this is the exact shape
D-18's `outcome ∈ {validated, skipped-with-reason}` domain check and D-15's judged/unjudged verdict pairing need:

```python
    if verdict.startswith("PASS"):
        ...
        if write_sha != readback_sha:
            print("FAIL: PASS verdict but write_image_sha256 != readback_sha256 "
                  f"({write_sha!r} != {readback_sha!r}) -- graduation oracle contradicted", file=sys.stderr)
            return 1
    ...
    print(f"FAIL: verdict does not start with PASS or DEFER: {verdict!r}", file=sys.stderr)
    return 1
```

**Fail-closed-on-absence** (lines 17-19 docstring + 57-59) — the precedent for a gate that is **red before the
bench runs**, which is what "observed red, not authored" needs:

```python
Exits 1 (not 0) when no phase99* AM27C020 cell exists yet -- this is the expected
pre-bench state; the gate only turns green after plan 99-04 fills the cell in.
No raw SHA is ever hardcoded here -- all SHAs are read from the cell fields.
```

**Two things to fix rather than copy.** (a) All five v1.18 gates hardcode
`EV = ".planning/v1.18/bench/EVIDENCE.json"` — a repo-relative literal, so the gate silently depends on
`cwd=/workspaces`. `gate_record.py` takes a cell path per RESEARCH's test map, so take it via argparse and
resolve it; see the `_HERE = Path(__file__).resolve().parent` idiom in
`.planning/v1.33/tools/strip_provenance.py:53` (and standing memory
`reference_check_permitted_claims_here_resolves_wrong_phase_dir` on why `_HERE` alone is not enough).
(b) None of the five validates a **command line**; RIG-05's `argv[0] ∈ {two absolute arm binaries}` /
reject-bare-`firestarter` leg has no analog and must be written fresh.

**Analog B — the JSONL row validator:** `.planning/v1.33/tools/build_citation_manifest.py:611-658`
`self_check()`. This is the closest thing in the tree to what `gate_record.py` must do across all 20 rows:

```python
REQUIRED_KEYS = frozenset(RECORD_KEYS)

def self_check(out_path: Path) -> tuple[list[str], list[dict]]:
    violations: list[str] = []
    with open(out_path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            if not line.strip():
                violations.append(f"line {lineno}: blank line in a JSONL file")
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                violations.append(f"line {lineno}: not valid JSON: {exc}")
                continue
            if lineno == 1:
                if "_schema" not in obj:
                    violations.append("line 1: missing the '_schema' header record")
                continue
            missing = REQUIRED_KEYS - set(obj)
            if missing:
                violations.append(f"line {lineno}: missing keys {sorted(missing)}")
                continue
            if obj["variant"] not in VARIANTS:
                violations.append(f"line {lineno}: unhandled variant {obj['variant']!r}")
```

Note the **accumulate-all-violations-then-report** style (vs v1.18's return-on-first-failure). For a 20-row
`EVIDENCE.jsonl` the accumulating style is the right one — a single run names every gap.

---

### `bench/EVIDENCE.jsonl` (model, append-only log)

**Analog A — the columns:** `.planning/v1.15/bench/EVIDENCE.json` and `.planning/v1.18/bench/EVIDENCE.json`
(both parsed). `locked_columns` is **byte-identical** across the two:

```json
"locked_columns": ["chip","family","board","shield","blank_state","op","sha256","verdict","anomalies"],
"evid_extension_columns": ["read_count","blank_check_result","write_image_seed_A","sha256_image_A",
                           "write_image_seed_B","sha256_image_B","cr01_risk"],
"locked_columns_note": "read_count/blank_check_result are EVID extension columns per EVID-01."
```

That two-tier shape (stable locked core + named per-milestone extension list + a note explaining which observed
keys are extensions) is what D-15 pins at Phase 160. A v1.15 cell, for the row shape:

```json
{"chip": "W27C512", "family": "0x07 (EPROM_STD / EEPROM)", "board": "leonardo", "shield": "Rev 2.0",
 "blank_state": "n/a — not factory-blank, current contents recorded", "op": "read+blank_check",
 "sha256": "9376dcd8…", "verdict": "PASS",
 "anomalies": "VPP-high read refusal (~18.8V) cleared by board reset before this read; negative-control verify exited RC=1",
 "read_count": 3, "blank_check_result": "not-blank (data present, e.g. 0x94 at 0x2000)"}
```

**The `not measured` convention, verbatim from `.planning/v1.18/bench/EVIDENCE.json` cell 0** — copy this
discipline exactly; it is how the Leonardo-read-window and VPP-under-load non-claims will read:

```json
"dmm_pin1_v": "not measured — held-rail proxy blocked by DTR-reset-on-close tooling bug (debug: held-rail-dev-reg-timeout, H1 confirmed; fix deferred to Phase 98). VPP→pin-1 routing CONFIRMED by code RCA: -f 0x188 → physical CTRL 0x89, P1 asserted (H2 disproven)."
```

Blocking reason on the **same line**, never blank. And a negative control recorded as **FIRED**, from v1.15's
top-level `note`: `"Negative control (EVID-03) FIR…"`.

**What carries over vs what changes, going JSON → JSONL:**

| Carries over | Changes |
|---|---|
| The nine `locked_columns`, verbatim | Whole-file object → line-per-row; the top-level metadata object becomes a **line-1 `_schema` header record** |
| `evid_extension_columns` + `locked_columns_note` two-tier idiom | They move *into* the `_schema` header |
| Per-cell preconditions block; negative-control-as-FIRED; `not measured — <reason>` inline | `cells: [...]` array disappears; rows are appended, never rewritten |
| Prose `verdict` / `anomalies` carrying their own inline citation | Requires a fixed `RECORD_KEYS` order (JSONL has no schema elsewhere to lean on) and a byte-stability contract |

**Analog B — the JSONL mechanics:** `.planning/v1.33/tools/build_citation_manifest.py`. It is the **only** JSONL
producer in the tree and its `_schema` header states the convention explicitly (lines 412-434) — the phrase
"no JSONL file existed anywhere in the three repos before this one" makes it the sole precedent:

```python
        "_schema": {
            "schema_version": SCHEMA_VERSION,
            "purpose": ("Pre-sweep citation manifest for milestone v1.33 Phase 154 …"),
            "record_keys": list(RECORD_KEYS),
            "jsonl_convention": (
                "One JSON object per line; LF line terminators; UTF-8 with "
                "ensure_ascii=False; keys emitted in the fixed RECORD_KEYS "
                "order and never sorted; this header object is line 1 and is "
                "the only line carrying the key '_schema'. No timestamp is "
                "recorded anywhere, so regeneration over an unchanged tree is "
                "byte-identical."
            ),
```

**Atomic write** (`build_citation_manifest.py:594-602`) — use this for any rewrite of `EVIDENCE.jsonl`; a
torn write mid-sweep would be unrecoverable:

```python
def write_manifest(out_path: Path, header: dict, records: list[dict]) -> None:
    """Atomic write: temp file plus os.replace (ASVS V12)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_name(out_path.name + ".tmp")
    with open(tmp_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(_dump(header) + "\n")
        for record in records:
            fh.write(_dump(_ordered(record)) + "\n")
    os.replace(tmp_path, out_path)

def _ordered(record: dict) -> dict:
    return {key: record[key] for key in RECORD_KEYS}

def _dump(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
```

One caution: `EVIDENCE.jsonl` is **append-only** per D-15, while this analog rewrites the whole file. Appending
a row with a plain `open(..., "a")` is not atomic; the analog's rewrite-and-replace is the safer pattern and
loses nothing, provided the tool refuses to change any pre-existing row (assert the prefix is unchanged before
`os.replace`).

---

### `bench/EVIDENCE.md` (doc, rendered) + `tools/render_evidence.py` (utility, transform)

**Analog for the output:** `.planning/v1.18/bench/EVIDENCE.md` (read, lines 1-40). Header block to mirror:

```markdown
# v1.18 Bench EVIDENCE — AM27C020 0x08 Write-Path RCA

**Generated:** 2026-06-29T15:43:35Z
**Milestone:** v1.18 — AM27C020 0x08 Write-Path RCA & Fix
**Phase:** 97 — pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program
**Board / Shield (LOCKED):** Leonardo + RURP Rev 2.0
**Branch base:** firmware `bccd995` (v1.17 tip) · host `e0bdea4`

> **STATUS: COMPLETE (Plans 97-02/03, 2026-06-30).** **NEVER-fabricated** cells,
> mirroring `EVIDENCE.json`. …
```

…and the per-plan discipline table (line 38 onward), which is the row shape a v1.34 render should follow:

```markdown
| Plan | Timestamp | Controller identity | Port | R1 | R2 | Board | Shield | … | fw commit | Notes |
|------|-----------|---------------------|------|----|----|-------|--------|---|-----------|-------|
| 97-02 | 2026-06-30 ~07:29Z | leonardo | /dev/ttyACM0 | 270000 | 44000 | Leonardo | Rev 2.0 | … | bccd995 (3.0.0b10) | … |
```

**Two divergences the renderer must introduce.** The v1.18 file says "mirroring `EVIDENCE.json`" — a *hand-kept*
mirror, exactly the drift D-15 rejects. And it carries `**Generated:** <timestamp>`, which **breaks
`--check`**: a timestamp makes the render non-reproducible and the diff-vs-committed gate can never be green.
Drop the timestamp (or source it from the `_schema`, never from `datetime.now()`).

**Analog for `--check`:** `tools/catalog/codegen.py`. Its determinism contract (docstring lines 22-35) is exactly
what `render_evidence.py` needs, and is stated as a contract rather than left implicit:

```python
Determinism contract (LCAT-05): two consecutive runs against the same catalog
file produce byte-identical output. Achieved by:
  - sorting messages by id ascending before emission
  - no timestamps, hostnames, or hashes in the banner
  - LF line endings via Path.write_text(..., newline='\n')
  - upper-case 2-digit hex literals ("0x%02X")
  - explicit dict iteration via sorted(...)
```

```python
    p.add_argument("--check", action="store_true",
                   help="Validate the catalog and exit 0/1. No files written.")
    ...
    args.target.parent.mkdir(parents=True, exist_ok=True)
    # newline='' + writing '\n' explicitly: LF endings guaranteed regardless
    # of platform (per Python docs for write_text + newline kwarg).
    args.target.write_text(output, encoding="utf-8", newline="\n")
```

**Where the analog stops — state this plainly.** `codegen.py --check` validates the **source** and exits 0/1;
it does **not** render and diff against the committed target. D-15's `--check` must do the harder thing:
re-render from `EVIDENCE.jsonl` and byte-compare against the committed `EVIDENCE.md`. The nearest in-repo
precedent for that comparison is not Python at all — it is `check-migration.sh`'s `cmp -s` (below).

---

### `tools/check_rebuild.py` (test/gate, batch compare)

**Analog:** `.planning/v1.7/phase-33-baseline-hex/check-migration.sh` Assertion 3 (lines 59-87). This is the
tree's existing "rebuilt `.hex` must be byte-identical to a captured baseline, per AVR env" gate — precisely
SC#1's reproduce-or-record-the-divergence clause, already written once for these same three envs:

```bash
BASELINE_DIR="/workspaces/.planning/v1.7/phase-33-baseline-hex"
for env in uno uno328pb leonardo; do
    BASELINE_HEX="${BASELINE_DIR}/${env}.hex"
    BUILT_HEX="${FIRMWARE_DIR}/.pio/build/${env}/firestarter_${env}.hex"
    ...
    if ! cmp -s "${BASELINE_HEX}" "${BUILT_HEX}"; then
        echo "FAIL: ${env}.hex diverged from baseline"
        echo "      diff (first 20 byte positions): $(cmp -l "${BASELINE_HEX}" "${BUILT_HEX}" 2>/dev/null | head -20)"
```

**Header pattern worth copying** (lines 16-18) — a gate that documents which wave it is *expected* to be red in:

```bash
# Pre-Wave-1: Assertion 1 will FAIL (the old names still exist — that's the
# load-bearing proof that the gate is wired correctly).
# Post-Wave-3: all 3 assertions PASS — prints "PASS: alias migration verified clean"
```

**Two deltas.** Those Phase 33 baseline `.hex` files were **gitignored** (comment at line 27: "gitignored per
Phase 31 D-11"); D-04 commits the six v1.34 images instead, so the baseline is `SHA256SUMS.txt` rather than a
sibling file — prefer `sha256sum -c` over per-file `cmp`, and keep `cmp -l | head -20` as the divergence
*detail* when a check fails. And this analog compares one arm's rebuild; v1.34 has six (2 arms × 3 targets), so
the loop is over `(arm, env)` pairs, and Pattern 1's arm-tagged filenames are what make that loop expressible
at all.

---

### `tools/capture_provenance.py` (service, subprocess fan-out)

**Analog:** `.planning/v1.33/tools/build_citation_manifest.py` — for the git-subprocess leg, the header record,
and the atomic write (all excerpted above). The git probe (lines 373-385) is the pattern for D-08's SHA leg:

```python
def _git_head(root: Path) -> str | None:
    try:
        done = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=False,
        )
    except OSError:
        return None
    if done.returncode != 0:
        return None
    return done.stdout.strip() or None
```

**Note the failure mode to reject.** This analog returns `None` on failure — appropriate for an optional
manifest field, **wrong** for D-13/RIG-05, where a `None` is exactly the silent-null RESEARCH's Pitfall 1
warns about. `capture_provenance.py` must treat any probe failure as a hard non-zero exit, never as a null field.
Same for the `git status --porcelain` leg: empty output is the *pass* condition, and "command failed" must not
be indistinguishable from "clean tree".

**Argparse shape** — `.planning/v1.33/tools/rehearse_citation_remap.py:423-435` is the closest in-repo
`required=True`-heavy parser, matching RESEARCH's Pattern 5 sketch almost one-for-one:

```python
def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(...)
    ap.add_argument("repo_root", help="the LIVE meta-repo root to rehearse from (read-only)")
    ap.add_argument("--manifest", action="append", required=True)
    ap.add_argument("--exceptions", required=True)
    ap.add_argument("--planning-base-sha", required=True)
    ap.add_argument("--firmware-head", required=True)
    ap.add_argument("--app-head", required=True)
    ap.add_argument("--output", required=True)
    ...
    sys.exit(0 if record["status"] == "COMPLETE" else 1)
```

**Closed-set argument validation** — `.planning/v1.33/tools/survey_provenance.py:73, 90` states the security
rationale for `choices` as the mechanism, which is what D-13's `--shield-rev` needs:

```python
# closed set: --group's argparse `choices` is drawn from this dict's keys,
```
> "…(argparse `choices`), so no filesystem path, `..` segment, or absolute path…" — `survey_provenance.py:73`

**The in-repo precedent for validating an operator-supplied string that reaches a path** —
`firestarter/name_firmware.py:46-52` (read-only reference; do **not** modify):

```python
                # Defensive validation per RESEARCH Security Domain V5: PROGNAME
                # flows into a filename, so the value must be a safe identifier.
                if not re.match(r"^[a-zA-Z0-9_-]+$", v):
                    print("ERROR: name_firmware.py — RURP_BOARD_NAME value '%s' "
                          "is not a valid identifier (must match [a-zA-Z0-9_-]+)" % v)
                    env.Exit(1)
```

Apply this to `--cell-id` (which becomes `bench/cells/<cell-id>/`) — `choices` covers `--shield-rev` and
`--arm`, but `--cell-id` is free-form and lands in a path, so it needs the regex, not a choices list.

---

### `tools/probe_board.py` (service, request-response) — **NO ANALOG**

**No `.planning` script in the tree invokes `avrdude`** (verified: `grep -rn subprocess`/`avrdude` across
`.planning/**/*.py` and `*.sh` — zero hits). There is no rig-side avrdude analog to copy.

**Closest neighbour, and what it does not cover:** `firestarter_app/firestarter/avr_tool.py` — **product code,
read-only reference only** (D-14 forbids extending it; modifying it would breach the Out-of-Scope table).
Useful for the invocation shape:

```python
    def build_options(self, extra_flags=None):
        options = ["-v", "-p", self.partno, "-c", self.programmer_id,
                   "-b", str(self.baud_rate), "-P", self.port]
        if self.config:
            options += ["-C", str(self.config.absolute())]
```
```python
    def _get_avrdude_version(self):
        stderr, _ = self._execute_command([])
        match = re.search(r"avrdude\s+version\s+(\d+\.\d+(\.\d+)?)", stderr, re.IGNORECASE)
```

**What it does not cover:** (a) it never reads flash — no `flash:r`, no `-A`; (b) it resolves avrdude via
`which()` and supplies `-C` **only below version 7.0** (`avr_tool.py:50`), so on this container's 7.1 it passes
no conf at all — RESEARCH's "pin one avrdude binary *and* its conf explicitly" is therefore a *departure* from
this analog, not a copy of it; (c) it omits `-xnometadata`, which is why RESEARCH forbids `fw -i` as the flash
path on `uno328pb`; (d) it has no signature-probe route.

**The signature-probe mechanism comes from the todo, not from code.**
`.planning/todos/pending/avrdude-mcu-detection-fallback.md` (bench-verified 2026-05-21, both parse routes):

```
$ avrdude -c urclock -P /dev/ttyUSB0 -b 115200 -p m328p -n
avrdude error: connected part ATmega328PB differs in signature from -p ATmega328P
                              ^^^^^^^^^^^^^ ← regex anchor

$ avrdude -c urclock -P /dev/ttyUSB0 -b 115200 -p m328pb -n -v
avrdude: device signature = 0x1e9516 (probably m328pb)
```

```python
    # Route 1: "connected part ATmega328PB differs in signature"
    m = re.search(r"connected part (\w+)", stderr)
    if m:
        return m.group(1).lower()
    # Route 2: "device signature = 0xNNNNNN (probably mXXX)"
    m = re.search(r"\(probably (m\w+)\)", stderr)
    if m:
        return m.group(1)
    return None
```

Reuse the **regexes and the `-n` invocation**; reject the `return None` — RIG-02 needs a hard failure when
neither route parses, not a null identity. The todo's own note that `-c arduino` against the 328PB fails
"unable to open programmer" (RESEARCH Code Example 6) is itself a signal worth recording.

---

### `tools/judge_readback.py` (service, judge) — **partial: the compare half has an analog, the read half does not**

**No analog for the avrdude read.** RESEARCH.md is explicit that `flash:r` has never been invoked in this
project's history, and this pattern sweep independently confirms no `.planning` script calls avrdude at all.
Both the `-A` flag behaviour and the three per-target read chains (arduino / urclock / avr109) are unproven on
this bench. **The planner must treat this file as new construction with a bring-up proof, not as a port.**

**Analog for the compare half:** `check-migration.sh` Assertion 3, excerpted above (`cmp -s` + `cmp -l | head -20`).
`.planning/phases/145-bench-validation/SHA256SUMS.txt` supplies the recording convention:

```
f72489604bfe917db7ee505e4d674576b2905a418e8dc55372b78dcab3e34e3a  images/img1.bin
9376dcd81713e7edc4f8df8e98b7c834eefcd880c2f9fef04ee1602397ad23c8  readbacks/prewrite.bin
f72489604bfe917db7ee505e4d674576b2905a418e8dc55372b78dcab3e34e3a  readbacks/readback1.bin
```

Note `readback1.bin`'s SHA equals `img1.bin`'s — the read-back-equals-written-image oracle, recorded as
plain `sha256sum` output so it is re-checkable with `sha256sum -c`. Same for D-02's two data: the judged span
SHA and the unjudged whole-flash 32768 B SHA both belong in a `SHA256SUMS.txt`-shaped file, not only in prose.
The `avr-objcopy -I ihex -O binary` normalization step (RESEARCH Pattern 2) has **no** in-repo precedent —
`objcopy` appears nowhere in `.planning` tooling.

---

### `tools/judge_wrv.py` (service, judge)

**Analog:** `.planning/v1.18/bench/check_signature.py` (48 lines, read in full) — the tree's existing
"SHAs must be consistent with the recorded observation" judge:

```python
REQ = ["bad_bytes", "retries", "bits_flipped", "vpp_adc_mv", "dmm_pin1_v", "dmm_pin31_v", "post_read_sha256"]

def main() -> int:
    d = json.load(open(EV))
    cells = [c for c in d["cells"] if c["chip"] == "AM27C020"]
    if not cells:
        print("FAIL: no AM27C020 cell", file=sys.stderr)
        return 1
    a = cells[0]
    missing = [k for k in REQ if "TBD" in str(a.get(k, "TBD"))]
    ...
    bits = a.get("bits_flipped")
    pristine_ok = a.get("pre_read_sha256") == a.get("post_read_sha256")
    if str(bits) in ("0", "0.0") and not pristine_ok:
        print("FAIL: 0 bits flipped but pre/post read SHA differ (chip not pristine)", file=sys.stderr)
        return 1
    print(f"RCA-01 signature complete; bits_flipped={bits}")
    return 0
```

The `bits_flipped==0 XOR pre!=post` cross-check is structurally the same assertion `judge_wrv.py` needs between
the app's unjudged 0/1/2 verdict and the SHA verdict — a **contradiction between two oracles is itself the
finding**, printed and non-zero rather than resolved.

**Three things this analog does not have, all from RESEARCH Pattern 3.** It reads a curated JSON, not a
directory of binaries — `judge_wrv.py` must `glob` `run_*.bin` and **count the files** (a hardware error makes
`dev consistency-check` return 2 early, leaving fewer than N). It must assert each file's size equals
65536 / 262144 exactly. And it must emit `disagreement` as a recorded outcome rather than retrying (RIG-04's
own wording). None of those legs exists anywhere in the tree.

---

### `tools/touch_1200.py` (utility, serial side-effect) — **partial**

**Closest neighbour:** `firestarter_app/firestarter/avr_tool.py:114-121` — **read-only reference**:

```python
    def _trigger_reset(self):
        """Trigger a reset for certain microcontrollers."""
        try:
            serial.Serial(port=self.port, baudrate=1200).close()
            time.sleep(2)
            return True
        except Exception as e:  # noqa: F841
            logger.warning(f"Failed to trigger reset: {self.port}")
            return False
```

Copy the three-line mechanism (`Serial(port, 1200).close()` then a settle sleep); **reject** the
swallow-and-warn error handling — a rig tool must exit non-zero so the recorded cell shows the failure. Note
also that the product path fires this only for `partno == "atmega32u4"` and the Leonardo may re-enumerate on a
*different* port after the touch (RESEARCH Pitfall 5 / the wait-for-new-port flag PIO supplies). No
`.planning` tool has ever done this; it is new construction.

---

### `tools/run_gates.sh` (config, runner)

**Analog:** `.planning/v1.4-e2e-verify.sh` — the tree's only "run every check and report" runner. Its header
is the contract to copy, in particular the explicit exit-code table and the honest naming of what it *cannot*
automate:

```bash
#!/usr/bin/env bash
# Post-cut automated verifier for v1.4 E2E-01 sub-criteria.
# Mechanically verifies (a) …, (c) …, and (d) …. Optionally probes (e) …
#
# Sub-criteria (b), (e), (f) are HUMAN-UAT items in '20-HUMAN-UAT.md' (D-06) -- they
# require operator interaction with live installs and/or flash hardware and cannot be
# automated by a script.
#
# Exit codes:
#   0  All checks passed (or skipped via --quick).
#   1  One or more checks failed; failure summary printed to stderr.
#   2  Bad usage (missing BETA_VERSION or unrecognized flag).

set -euo pipefail
```

That "cannot be automated by a script" paragraph is exactly where D-17's fresh-context reconstruction and D-03's
cross-flash belong: named in the runner, explicitly out of its scope. `set -euo pipefail` on every rig shell
script. `check-migration.sh` supplies the alternative style (accumulate failures, print `PASS: …` once at the
end) — pick one and apply it to both scripts.

---

### `PROCEDURE.md` (doc) — **partial**

**No arm-agnostic procedure document exists in the tree** (searched: no `PROCEDURE*` file under `.planning`,
and `.planning/v1.34/` does not yet exist). The nearest analogs are partial and complementary:

- `.planning/phases/145-bench-validation/145-BENCH-LOG.md` (216 KB) — the **discipline prose**: "nothing here is
  fabricated; a tooling-blocked reading is `not measured` with its blocking reason on the same line", and the
  gate/verification-map binding. This is a *log*, not a procedure — it records what happened, whereas
  PROCEDURE.md prescribes what will. Take the discipline sentences, not the structure.
- `.planning/v1.18/bench/EVIDENCE.md`'s "Bench-Discipline Columns (D-08) — filled per task at the bench" table
  — the per-step field list a procedure step must produce.
- RESEARCH Pattern 6 already **derives** the 11-step order from standing rules (chip-out window covering flash
  *and* read-back on Uno-class; pot set once per cell because both chips declare `vpp_mv 12000`). Prefer that
  derivation over inventing an order.

The `$ARM_BIN`-substitution requirement (SC#3, one step vocabulary, two arms) has no precedent at all. RESEARCH
Pattern 4 measured the two arms' Click surfaces as set-identical (25 commands, zero difference), which is what
makes the empty step-list diff achievable — but the `render_steps.py --arm control|v133` tool the test map names
is not in the recommended-layout file list. **Flag to the planner:** either add it to the tool set or state how
the diff-empty criterion is produced without it.

---

### `images/` and `bench/cells/` (artifacts)

**Analog:** `.planning/phases/145-bench-validation/` — the committed per-cycle layout `images/ readbacks/
runs/ logs/` with a single top-level `SHA256SUMS.txt` covering all four (excerpted above; 4552 bytes, paths
relative to the phase dir). v1.34 nests this per cell (`bench/cells/<cell-id>/`) instead of flattening it,
because the sweep has 20 positions rather than Phase 145's handful.

**Two deltas to decide before the first cell, not after the twentieth.** Phase 145 committed ~0.5 MB;
RESEARCH computes v1.34 at ~10.5 MB. And `.planning/v1.7`'s baseline `.hex` files were **gitignored** whereas
D-04 commits these six — `/workspaces/.gitignore` was verified to contain no rule blocking
`.planning/v1.34/**` binaries, so committing works as-is.

**Pattern 1 (arm in the filename) is load-bearing here** — `name_firmware.py:60` makes both arms build to the
identical artifact name:

```python
board_name = _extract_board_name()
env.Replace(PROGNAME="firestarter_%s" % board_name)
```

So `.pio/build/uno/firestarter_uno.hex` is the control arm's *and* the v1.33 arm's output path. Disambiguate at
copy time (`firestarter_uno.control.hex` / `firestarter_uno.v133.hex`), and `rm -rf .pio/build/<env>` between
arms so a failed build cannot leave the previous arm's artifact looking fresh.

---

### `.planning/todos/pending/avrdude-mcu-detection-fallback.md` (modified)

D-14 requires a front-matter/body annotation only: "mechanism reused by v1.34 Phase 160; product-side
`--detect-mcu` still pending", with `status: pending` **unchanged**. The file's existing front matter is the
pattern:

```yaml
id: avrdude-mcu-detection-fallback
status: pending
resolves_phase: null
```

`resolves_phase` stays `null` — Phase 160 reuses the mechanism, it does not resolve the todo. Standing memory
`reference_gsd_requirements_roadmap_verbs_reformat_whole_file` applies: prefer a hand edit over a GSD verb that
would reformat the file.

---

## Shared Patterns

### Gate-script skeleton
**Source:** `.planning/v1.18/bench/check_diff07.py` (29 lines — the smallest complete instance)
**Apply to:** `gate_record.py`, `judge_readback.py`, `judge_wrv.py`, `check_rebuild.py`, `render_evidence.py --check`

```python
#!/usr/bin/env python3
"""Phase-97 RCA-02 differential-control gate.

Verifies the W27C512 (0x07) differential-control cell in
.planning/v1.18/bench/EVIDENCE.json is filled with a recorded verdict (no "TBD").
Exits non-zero if unfilled.
"""
import json
import sys

EV = ".planning/v1.18/bench/EVIDENCE.json"

def main() -> int:
    ...
    if "TBD" in verdict or not verdict:
        print("FAIL: W27C512 differential verdict not recorded", file=sys.stderr)
        return 1
    print(f"RCA-02 differential control recorded; W27C512 verdict={verdict}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

Invariants across all five precedents: module docstring naming the requirement it gates and the exact condition;
stdlib only; `FAIL: <reason>` to **stderr**; a single positive verdict line to **stdout** carrying the measured
value; `return 1` for a violation, `return 2` for bad usage; judged by exit code. Do **not** copy the hardcoded
`EV` path (see `gate_record.py` above).

### Self-test in-file, instead of pytest
**Source:** `.planning/phases/145-bench-validation/tools/extract_frames.py` (tail)
**Apply to:** every new tool — this is how "observed red" gets discharged under plain `python3`

```python
def main(argv) -> int:
    if len(argv) >= 2 and argv[1] == "--selftest":
        return run_selftest()

    if len(argv) != 2:
        sys.stderr.write(f"usage: {argv[0]} <raw-stderr-capture-path>\n")
        sys.stderr.write(f"       {argv[0]} --selftest\n")
        return 2
    ...

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

`run_selftest()` runs a **positive and a negative** fixture and returns
`0 if (positive_ok and negative_ok) else 1` — the negative fixture is the in-file equivalent of the deliberately
broken input RESEARCH's Wave 0 note demands (a truncated read-back, a null provenance field, a hand-edited
`EVIDENCE.md`, an `outcome: inconclusive`). `.planning/v1.33/tools/fixtures/` shows the alternative: on-disk
fixtures, including `planted_dead05_phrasing_violation.md` — a committed, deliberately-broken input. Either is
in-repo precedent; the on-disk form is better when the fixture is a binary.

### D-16 boundary comment
**Source:** `gen_addr_image.py:4-9` and `extract_frames.py:3-8` (both quoted above)
**Apply to:** every file under `.planning/v1.34/tools/`

`extract_frames.py`'s wording is the shorter template:

```python
D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It lives only under
.planning/phases/145-bench-validation/tools/ and must NEVER be added into firestarter/ or
firestarter_app/ -- this phase changes no firmware and no host source. Pure standard-library
Python, no third-party imports.
```

Re-path the "lives only under" clause per file. The "no third-party imports" clause matters: rig tools run from
system `python3`, **not** from an arm venv, so they cannot import `firestarter` — and `pyserial` (system-wide,
3.5) is the only non-stdlib import any of them may take (`touch_1200.py`).

### Anti-fabrication recording
**Source:** `.planning/v1.18/bench/EVIDENCE.json` (`dmm_pin1_v`), `check_graduation.py` docstring line 19
**Apply to:** `EVIDENCE.jsonl`, `EVIDENCE.md`, every cell record

Three rules, all with precedent: a blocked reading is `not measured — <blocking reason>` on the **same line**,
never blank; **no raw SHA is ever hardcoded in a gate** ("all SHAs are read from the cell fields"); a negative
control is recorded as **FIRED**, not as configured.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `tools/judge_readback.py` (the avrdude read + objcopy normalize legs) | service | request-response → file-I/O | `flash:r` has never been invoked in this project's history; no `.planning` script calls `avrdude` at all; `avr-objcopy` appears in no rig tool. Closest neighbour `firestarter_app/firestarter/avr_tool.py` never reads flash, resolves avrdude by `which()`, and passes `-C` only below v7.0 — it is a reference for invocation shape only, and is read-only product code. |
| `tools/probe_board.py` | service | request-response | Same — no avrdude analog. The mechanism comes from the pending todo's bench-verified stderr regexes, not from any executing code. `-xshowvector` on `uno328pb` has no precedent whatsoever. |
| `tools/touch_1200.py` | utility | event | No `.planning` tool has ever driven a serial port. `avr_tool.py:114-121` supplies the three-line mechanism but swallows the failure, which a rig tool must not. |
| `render_evidence.py --check` (the render-and-diff-vs-committed leg) | test/gate | transform → compare | `codegen.py --check` validates the source and never diffs against the committed target; the only diff-vs-committed precedent is `check-migration.sh`'s `cmp -s`, in bash, over `.hex` files. |
| `PROCEDURE.md`'s arm-agnostic step vocabulary + `render_steps.py` | doc / utility | — | No procedure document and no step renderer exists. RESEARCH Pattern 6 derives the order; the `$ARM_BIN` substitution and the diff-empty gate are new. |

For these five, the planner should lean on RESEARCH.md's Code Examples 3-8 and Patterns 2-3 (which carry
*measured* command shapes and *verified-from-source* artifact contracts) rather than on any codebase analog —
and should keep RESEARCH's own honesty marker attached: Code Examples 3, 5 and 8 are marked **NOT RUN — no board
attached**, so every one of these five files needs a bring-up proof before it is trusted, cheapest target first
(`uno`, where `-A` is already the default).

---

## Metadata

**Analog search scope:** `.planning/v1.15/bench/`, `.planning/v1.18/bench/`, `.planning/v1.33/tools/`,
`.planning/v1.7/phase-33-baseline-hex/`, `.planning/phases/145-bench-validation/{tools,images}/`,
`.planning/todos/pending/`, `.planning/*.sh`, `tools/catalog/`, `firestarter/name_firmware.py`,
`firestarter_app/firestarter/avr_tool.py` (read-only)
**Files read in full:** 8 (5 × `check_*.py`, `gen_addr_image.py`, plus targeted ranges of 6 more)
**Negative searches performed:** `avrdude` in `.planning/**/*.{py,sh}` → 0 hits · `import pytest` →
`ModuleNotFoundError` · `PROCEDURE*` under `.planning` → 0 hits · `.planning/v1.34/` → does not exist
**Pattern extraction date:** 2026-08-26
