# GATE-1.5 Baseline Capture Procedure

**Plan:** 21-01 (Phase 21 — Firmware Target `uno328pb`)
**Anchor:** `firestarter/beta @ 5fd751e` (version-unbumped)
**Purpose:** Document the reproducible recipe used to produce `firestarter_uno.hex` and `firestarter_leonardo.hex` baselines under this directory so Phase 21 Plan 21-02's `cmp -s` byte-identity gate can re-verify on any dev box. Cites CONTEXT D-04 (GATE-1.5 verification = `cmp -s` against checked-in baseline hex files).

This file is the meta-repo record. The hex files alongside it MUST stay byte-identical to a fresh `pio run` from the same anchor commit — that is the GATE-1.5 obligation.

## Captured-from anchor

| Field | Value |
|---|---|
| Firmware sub-repo | `/workspaces/firestarter/` (git submodule of meta-repo) |
| Branch | `beta` |
| Commit | `5fd751e8e2e638e9bec401c5bb5df4809503e226` (short: `5fd751e`) |
| Commit subject | `chore: ignore __pycache__/*.pyc + untrack accidentally-committed bytecode` |
| `include/version.h` | `#define VERSION "3.0.0b2"` (verbatim, **unmodified** — see "Why pre-bump" below) |
| `name_firmware.py` | Original 3-line form using `env.GetProjectOption("board")` (pre-rework — Plan 21-02 owns the rework) |
| Captured | 2026-05-20 |
| PlatformIO Core | 6.1.19 |
| `platformio/atmelavr` platform | 5.2.0 (published 2026-04-28) |

## Captured baselines

`sha256sum` output (use this to detect any post-capture drift; `sha256sum -c` against these lines will pass on the committed files):

```
0dd5c01a870de38e868bdc71cebd547cb65ed1d7573dc90678c99f7dc3a854d2  firestarter_uno.hex
f49e2a57a2ab8dad7224733d3e5f08f36df2d6aee4c4f924217a4d0c921fdc90  firestarter_leonardo.hex
```

| File | Size (bytes) | First Intel-HEX record (`head -1`) |
|---|---|---|
| `firestarter_uno.hex`      | 62617 | `:100000000C946F010C9497010C9497010C94970138` |
| `firestarter_leonardo.hex` | 68876 | `:100000000C94E8010C9410020C9410020C94100251` |

## Reproducible recipe

Run from the meta-repo root (`/workspaces`). The firmware sub-repo is a git submodule at `firestarter/`.

```bash
# 1. Confirm sub-repo clean and on the recorded anchor (no version-h drift,
#    no unintended edits leaking into the build).
git -C firestarter status                  # MUST be clean
git -C firestarter rev-parse HEAD
# expected: 5fd751e8e2e638e9bec401c5bb5df4809503e226

# 2. If HEAD has drifted off the anchor, restore it BEFORE building.
#    Do NOT invoke firestarter/.github/scripts/update_version.py — see
#    "Why pre-bump" callout below; it perturbs include/version.h's
#    .rodata region and defeats the GATE-1.5 cmp.
# git -C firestarter checkout 5fd751e8e2e638e9bec401c5bb5df4809503e226

# 3. Note the current branch so we can return to it after the detached
#    HEAD checkout (5fd751e on beta tip means git switch - is a no-op).
ORIGINAL_BRANCH=$(git -C firestarter rev-parse --abbrev-ref HEAD)

# 4. Drop any stale .pio/build outputs from a possibly post-rework state.
( cd firestarter && pio run -t clean -e uno -e leonardo )

# 5. Build both envs from a clean state. No update_version.py invocation.
( cd firestarter && pio run -e uno -e leonardo )

# 6. Copy the freshly built hex files into the meta-repo baseline dir.
cp firestarter/.pio/build/uno/firestarter_uno.hex            .planning/milestones/v1.5-artifacts/baselines/firestarter_uno.hex
cp firestarter/.pio/build/leonardo/firestarter_leonardo.hex  .planning/milestones/v1.5-artifacts/baselines/firestarter_leonardo.hex

# 7. Verify checksums against the table above.
( cd .planning/milestones/v1.5-artifacts/baselines && sha256sum -c <<'EOF'
0dd5c01a870de38e868bdc71cebd547cb65ed1d7573dc90678c99f7dc3a854d2  firestarter_uno.hex
f49e2a57a2ab8dad7224733d3e5f08f36df2d6aee4c4f924217a4d0c921fdc90  firestarter_leonardo.hex
EOF
)

# 8. Restore original branch (a no-op if we were already on it).
git -C firestarter switch "$ORIGINAL_BRANCH" 2>/dev/null || true
```

The `firestarter/` submodule MUST be left with a clean working tree at the end of this procedure. Verify with `git -C firestarter status -s` returning empty.

## How to verify a fresh build matches (used by Plan 21-02)

After Plan 21-02 lands the macro-guard widening (CONTEXT D-01), the `[env:uno328pb]` block (CONTEXT D-07), and the reworked `name_firmware.py` (CONTEXT D-06), the phase's GATE-1.5 step re-runs `pio run -e uno -e leonardo` (still version-unbumped — `include/version.h` MUST stay at `3.0.0b2`) and runs:

```bash
cmp -s firestarter/.pio/build/uno/firestarter_uno.hex            .planning/milestones/v1.5-artifacts/baselines/firestarter_uno.hex
cmp -s firestarter/.pio/build/leonardo/firestarter_leonardo.hex  .planning/milestones/v1.5-artifacts/baselines/firestarter_leonardo.hex
```

Both `cmp -s` invocations MUST exit 0 (silent success) for GATE-1.5 to pass. A non-zero exit indicates that one of the changes in Plan 21-02 perturbed the existing `uno` or `leonardo` output — that's a phase-level fail and the change must be re-examined.

The `RURP_BOARD_NAME` single-source-of-truth invariant (CONTEXT D-05 + D-09) requires that the reworked `name_firmware.py` produce `firestarter_uno.hex` and `firestarter_leonardo.hex` BYTE-IDENTICAL to these baselines — both the artifact filename and content. The `[env:uno]` and `[env:leonardo]` build_flags already declare `-D RURP_BOARD_NAME=\"${this.board}\"`, so the reworked extractor MUST resolve those to `uno` and `leonardo` respectively, preserving the triple end-to-end.

## Why pre-bump

> **DO NOT invoke `firestarter/.github/scripts/update_version.py` between baseline capture and Plan 21-02's verification step.**

Per RESEARCH.md Pitfall 3, `update_version.py` rewrites `firestarter/include/version.h`, and the `VERSION` macro lands in `.rodata` via `FW_VERSION VERSION ":" RURP_BOARD_NAME` at `firestarter/include/firestarter.h:16`. The version string region of the `.hex` file is the ASCII bytes of the literal (here, `3.0.0b2`), embedded directly in `.rodata` and visible in `firestarter_*.hex` Intel-HEX records. Any version bump rewrites both the version bytes AND every affected Intel-HEX line's trailing checksum byte. A naive `cmp -s` against a version-bumped baseline tears on every drifted byte — false-positive GATE-1.5 failure with no real regression.

The defense is to capture the baseline at `5fd751e` with `include/version.h` left untouched (current literal `VERSION "3.0.0b2"`) and re-build Plan 21-02's verification from the SAME version-unbumped working tree. Phase 22 (REL) owns the next version bump on the actual release cut.

If the operator accidentally bumps `version.h` before Plan 21-02 verifies, the recovery is:

```bash
git -C firestarter checkout 5fd751e8e2e638e9bec401c5bb5df4809503e226 -- include/version.h
```

…and then re-build. (Do **not** revert the entire working tree — that would also discard the Plan 21-02 changes.)

## References

- CONTEXT D-04 — `.planning/phases/21-firmware-target-uno328pb/21-CONTEXT.md` (GATE-1.5 verification = `cmp -s` against checked-in baseline hex files).
- CONTEXT D-05 / D-07 / D-09 — `boards/uno328pb.json` dropped; `RURP_BOARD_NAME` is the single source of truth for the board-id = artifact-name = handshake-string triple.
- RESEARCH Pitfall 3 — `.planning/phases/21-firmware-target-uno328pb/21-RESEARCH.md` ("GATE-1.5 cmp against a version-bumped baseline").
- v1.4 precedent — `.planning/phases/15-versioning-locked-step-coordination-foundation/lockstep-dryrun-fixture.sh` (the byte-identity-gate pattern this baseline reuses).
- Plan 21-01 — `.planning/phases/21-firmware-target-uno328pb/21-01-PLAN.md` (this plan).
- Plan 21-02 — consumes these baselines via the GATE-1.5 `cmp -s` step described above.

---

*Captured: 2026-05-20 — version.h = `3.0.0b2` (verbatim, unmodified) — pio 6.1.19 + atmelavr 5.2.0.*
