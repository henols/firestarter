# v1.38 — Close Record: Repository Rename

**Closed 2026-09-15. 5 phases (189–193) · 23 plans · 15/15 requirements · merged to
`beta` in all three repositories. Not tagged — stable release stays operator-gated.**

App `3.0.0b42`, firmware `3.0.0b29` on `beta`.

---

## 1. What the milestone set out to do, and what it did

The firmware repository was `henols/firestarter`. The meta repository had no name of
its own. This milestone gave the meta repository that name and moved the firmware to
`henols/firestarter_fw`, on the rule that **nothing may depend on GitHub's redirect**
— a redirect is a courtesy that survives only until someone claims the freed slug.

All 15 requirements are complete. The rename is done, the three firmware release
endpoints address the new slug on both `beta` and `main`, every live tracked
reference across the three repositories is correct, and the one trap that cannot be
fixed — history — is documented rather than papered over.

## 2. The phases

| phase | plans | what it delivered |
|---|---|---|
| 189 Free the Name | 4 | Repository renamed. Old slug left deliberately unclaimed. Submodule resolves the new URL directly. |
| 190 Endpoints That Do Not Depend on a Redirect | 4 | Three release endpoints repointed on `beta`; fixtures **derived from** the endpoint constants so a future retarget cannot pass silently; `fw --list` separates failure from empty. |
| 191 The Branch That Reaches Users | 5 | Same endpoints on `main`, a stable cut carrying them, validated against that stable rather than a prerelease. |
| 192 Live References Only | 5 | Every live tracked reference corrected across three repositories, with the archived ones proven untouched. |
| 193 The Deferred Claim, Made Measurable | 5 | The deferred adoption claim turned into a number with a stated threshold, and the `.gitmodules` archaeology trap written down. |

## 3. The trap that history cannot be fixed out of

`.gitmodules` records a submodule URL **per commit**. Checking out a pre-rename ref,
or bisecting firmware history, resurrects the old URL from that commit. Fixing the
live branches does not fix history, and no amount of sweeping can.

This is recorded in `.planning/notes/gitmodules-archaeology-trap.md` with both
workarounds, their executed transcripts, and the `git submodule sync` hazard that
silently undoes one of them. **It does not bite today**, because the old slug still
redirects. It arms the moment that freed slug is claimed by anyone.

## 4. Work that rode along, and is not in the requirement count

A substantial amount of unplanned work landed on this milestone branch. It is
recorded here because the requirement count does not describe it.

**Source-introspecting tests removed from the host suite.** Operator ruling:
source-text scanning is not a legitimate testing technique, and the ruling covers
`ast`-based introspection as well as literal substring matching. Keep criterion: only
data-driven tests that exercise production code.

The removal set was **measured, not guessed**. Regex classification of the test
sources gave answers between 80 and 205 depending on the heuristic — the same
brittleness the ruling rejects. A pytest plugin instead patched `open`, `Path.open`,
`Path.read_text` and `Path.read_bytes` and recorded the resolved path of every read
per test nodeid across a full run: **129 tests read source or docs at runtime, 377
read `.json`/`.xml` data.** The 129 defined the set. 24 modules went, plus
`fw_presence.py`, a fixture repo and 11 `planted_*` fixtures that existed only to be
scanned. Suite 2145 → 1886, zero skips, coverage 84.91% against a 70% floor.

Why it surfaced now: the rename moved the sibling checkout out from under
`fw_presence.py`'s hardcoded `FW_ROOT`, so all 71 `@requires_fw` legs began skipping.
No workflow in either repository sets `FIRESTARTER_FW_ROOT` or checks out the
firmware, so **those legs had never run in CI at all**. That is the failure mode of
the technique: host-side source-scanning gates fail open, and nothing goes red when
coverage stops.

**The planning-citation leak, root-caused and gated.** 1254 comment lines across both
sub-repositories, of which the previous detector could see 141. Full record in
`.planning/debug/resolved/planning-refs-in-src-comments.md`.

**Four silent build defects found by reading `platformio.ini`.** A bootloader guard
now refuses an image that would overwrite the bootloader; a suite quarantined four
months ago under a misdiagnosed cause was repaired; nine build targets became five;
and dev tools became a per-channel decision.

## 5. What the close cost, recorded rather than absorbed

**A requirement nearly lost its only coverage.** Removing the unused
`native_params_v131` env would have deleted `test_eprom_params_v131`, three of whose
nine cases were TEST-01's **only** mapped coverage. The env went; the suite was folded
into CI instead, where it had never run.

**Real coverage was lost, and is named.**
`test_loop05_a_successful_block_does_not_disable_the_route` went with
`test_loop_eprom_v131`. `tests/golden/protocol_branch_inventory.json` still cites it
as the reason the HV route is cleared conditionally rather than unconditionally. The
firmware behaviour is unchanged and correct. Nothing tests it now.

**A four-month-old diagnosis was wrong.** `test_flash_intel_vpp` was excluded from CI
on 2026-05-20 as a "pre-existing parallel-build filesystem race" producing an
"intermittent SIGABRT". It fails **5 runs out of 5**, deterministically, because
`setUp` mocks `delay` but not `Serial`. Three lines fixed it. The written explanation
is why nobody looked again.

**The same mistake was made again during this close, and caught.** Concurrent `pio
test` processes against one build directory produced 194/194, then 173/171, then
144/140 — inconsistent counts that would have read as a real regression. A serialized
run showed 194/194 both ways. *Intermittent* is the easiest claim to make wrongly,
because its evidence is the absence of a stable result.

## 6. Not claimed

- **No hardware was involved.** Nothing here is validated against a board.
- **The stable firmware configuration has never been flashed to a device.** `-D
  DEV_TOOLS` left the shared `[env]` block this milestone, so `main` now builds
  without it. It compiles and its native suite passes; no board has run it.
- **`PLATFORMIO_BUILD_FLAGS` reaching the compiler on `beta` is unproven in CI.** The
  first beta build after this close is the first test of it. It fails in the safe
  direction — a lost variable ships stable-configured firmware to beta, not dev
  tooling to stable — but it fails silently.
- **`milestone.complete` was not run.** This close is hand-archived, as v1.35, v1.36
  and v1.37 were, because the CLI regenerates a ROADMAP that is hand-authored.

## 7. What is open, and named

- **`firestarter_fw/tests/` is 286 tests across 31 modules, 30 of them source-text
  scanners** using the technique retired on the host side this milestone. Unlike the
  host's, these execute in CI. No ruling has been made.
- **`DEV_TOOLS` docstring residue.** The gate added this milestone deliberately does
  not scan Python docstrings, and `firestarter_fw/tests/*.py` module docstrings carry
  heavy planning narration.
- **Three orphan envs were removed; the decision that kept them out of CI was
  circular** — `CLAUDE.md` attributed it to a gate retired on 2026-09-13, then kept
  the separation because the no-CI-leg property still held.
- **`.github/workflows/*.yml` comments** in both sub-repositories carry planning
  citations. A workflow file is not product source, so the gate does not scan them.
