# Phase 127: Host DFU Installer - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `127-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-08-01
**Phase:** 127-Host DFU Installer
**Areas discussed:** CI evidence route for HOST-04 · pyusb present-vs-absent (HOST-04 ∥ HOST-05) · HOST-03 DFU_UPLOAD readback shape · Flash-map reconciliation — 127 or 129?

All four offered gray areas were selected. Sixteen decisions locked (D-01…D-16); three further
requirements (HOST-01's deviation record, HOST-06's opcode anchoring, HOST-07's floor bump) were
left as Claude's-discretion defaults, D-17…D-19.

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| CI evidence route for HOST-04 | `ci.yml` has no `workflow_dispatch` and its `push` trigger is `main`-only — a new leg would exist but never run | ✓ |
| pyusb present-vs-absent (HOST-04 ∥ HOST-05) | The two requirements demand opposite environments in the same suite | ✓ |
| HOST-03 DFU_UPLOAD readback shape | Soft-fail semantics, dialect scope, compare extent, where the state lives | ✓ |
| Flash-map reconciliation — 127 or 129? | Phase 126 reserved Sector 15; the host guard still permits the full 128 KiB, and no HOST id covers it | ✓ |

**Notes:** Presented alongside seven live-measured facts (clean `merge-tree`, 87-commit drift,
1158+58 test counts, pyusb absent / libusb present, no serial devices, `ci.yml` triggers, the
confirmed `--usb-id` gap). Four pending todos matched on keywords only, all firmware-area; the
recommendation to review-not-fold was not contested.

---

## CI evidence route for HOST-04

### Q1 — How does the `.[test,py32]` leg actually get RUN?

| Option | Description | Selected |
|--------|-------------|----------|
| Add `workflow_dispatch`, operator dispatches | Mirrors 124 D-08 / 125 D-13 / 126; `autonomous: false` plan, operator runs push + dispatch; evidence = run URL + head SHA | ✓ |
| Draft PR against `beta` | `pull_request:` already fires with no branch filter — zero workflow edits, but attaches a public artifact mid-milestone and stays open across 128–130 | |
| Add the milestone branch to `push:` | Automatic, no operator step — but a branch literal that rots, and it makes agent pushes CI-triggering | |
| Local-only, recorded as CI-uncovered | The 126 D-01 shape; libusb is present locally — but HOST-04's text says "A CI leg installs…", so it is a partial discharge | |

**User's choice:** Add `workflow_dispatch`, operator dispatches.
**Notes:** Verified after the answer and folded into D-01: pushing the app milestone branch fires
nothing — `beta-release.yml` is `beta`-only, `release.yml` and `ci.yml`'s `push` are `main`-only,
`publish.yml` is release/dispatch-only. Zero release hazard, same as the firmware side.

### Q2 — What shape should the leg take inside `ci.yml`?

| Option | Description | Selected |
|--------|-------------|----------|
| Second job, py32-only tests | Separate `ci-py32` job, ~1 min, isolated so a pyusb/libusb break cannot take down the main gate | ✓ |
| Second job, full suite under `[test,py32]` | Catches tests whose behaviour changes when `usb` becomes importable — but doubles wall-clock and forces a coverage-gate decision | |
| Matrix dimension on the existing job | Least YAML — but doubles the four codegen-drift gates and the smoke test for no reason | |

**User's choice:** Second job, py32-only tests.
**Notes:** Accepted cost recorded in D-02 — the full suite is not re-run under pyusb-present.
D-05's subprocess design is what keeps that gap low-risk.

### Q3 — What can the "real pyusb API surface" test exercise with no device?

| Option | Description | Selected |
|--------|-------------|----------|
| Real `find` + signature-anchored `ctrl_transfer` | `usb.core.find(find_all=True)` for real; `inspect.signature` on the installed pyusb pins argument order — catches the real break in ~3s | ✓ |
| Real `find` + a real `Device` against a fake backend | Highest fidelity, exercises pyusb's own marshalling — but ~100+ lines of untested shim that can drift from libusb | |
| Real `find` only | Smallest — but leaves `ctrl_transfer`, named in Criterion 2, unverified | |

**User's choice:** Real `find` + signature-anchored `ctrl_transfer`.

### Q4 — How is Criterion 1's "exact collected-test count" discharged?

| Option | Description | Selected |
|--------|-------------|----------|
| Recorded in the evidence artifact, not gated | Verbatim `--collect-only` trailer + baseline + per-file delta; consistent with 126 D-01 and 123 D-10's rationale | ✓ |
| A test asserts the count | Literal "exact count" as an exit code — but exactly the shape D-10 rejected, and red on every legitimate addition | |
| Gated floor, recorded exact | `>=` floor catches loss without going red on additions — but two mechanisms for one criterion | |

**User's choice:** Recorded in the evidence artifact, not gated.
**Notes:** A deliberate, reasoned exception to the standing "exit code, not a human read"
preference — D-04 says so explicitly so it does not read as a lapse.

---

## pyusb present-vs-absent (HOST-04 ∥ HOST-05)

### Q1 — How is "pyusb genuinely uninstalled" produced?

| Option | Description | Selected |
|--------|-------------|----------|
| Subprocess with a `sys.meta_path` import blocker | Runs identically in both legs — no skip marker, no `ALLOWED_SKIP_REASONS` entry; same discipline `test_skip_census.py` uses | ✓ |
| `monkeypatch` on `sys.modules` in-process | Simplest — but fakes absence; an eager top-level import would already have succeeded | |
| A `pip uninstall pyusb` step | Literal machine state — but `.[test]` never installs it, so the step asserts CI config, not code | |

**User's choice:** Subprocess with a `sys.meta_path` import blocker.

### Q2 — How does the de-pragma'd `PyusbMissingError` line get covered?

| Option | Description | Selected |
|--------|-------------|----------|
| Two tests: in-process for coverage, subprocess for the CLI | Each mechanism does the job it is good at | ✓ |
| One subprocess test + coverage subprocess support | One test covers both — but the plumbing degrades silently to "no data" | |
| In-process only, drop the subprocess | All coverage lands — but reverses D-05 and lets an eager-import regression through | |

**User's choice:** Two tests: in-process for coverage, subprocess for the CLI.
**Notes:** The pragma sits on `except ImportError` in `_require_usb()` (`py32_dfu.py:374`), and a
subprocess contributes nothing to the parent's `--cov-fail-under=70` run — the coupling that
forced the split.

### Q3 — How is HOST-08's import-time `_BOARD_CHOICES` behaviour proven?

| Option | Description | Selected |
|--------|-------------|----------|
| Subprocess per version, reusing D-05's harness | Import-time computation proven by construction; module imported once, after the version is set | ✓ |
| `importlib.reload(cli_handlers)` in-process | Fast, contributes coverage — but contradicts the branch's documented strategy and carries a stale-command-object trap | |
| Both — subprocess for truth, reload for coverage | Belt and braces — but two mechanisms for one requirement, and the reload half keeps the trap | |

**User's choice:** Subprocess per version, reusing D-05's harness.

### Q4 — HOST-02: which mechanism rejects `--usb-id` on stable?

| Option | Description | Selected |
|--------|-------------|----------|
| One shared helper for both options | `_reject_py32_only_option()` — the two refusals cannot drift, a third option gets it free | ✓ |
| Mirror the existing check inline | Most literal "exactly as" — but two copies of one rule, the shape that produced this bug | |
| Don't register the options at all on stable | Click emits its own genuine error — but needs signature defaults, and *changes* `--dfu-probe` rather than matching it | |

**User's choice:** One shared helper for both options.

---

## HOST-03 DFU_UPLOAD readback shape

### Q1 — Does readback run in plain DFU 1.1?

| Option | Description | Selected |
|--------|-------------|----------|
| DfuSe only; plain DFU records "not verifiable" | Never claims a comparison it cannot ground; converts the existing warning into a recorded fact | ✓ |
| Both dialects, sequential upload from block 2 | Well-defined *if* the bootloader mirrors DNLOAD block semantics on UPLOAD — unverifiable with no silicon | |
| Both dialects, best-effort compare | Max coverage if plain works — but a soft-fail that absorbs real mismatches cannot fail | |

**User's choice:** DfuSe only; plain DFU records "not verifiable".

### Q2 — Where does the soft-fail state live?

| Option | Description | Selected |
|--------|-------------|----------|
| Enum attribute on the flasher + WARNING log | `verify_result` enum; `flash()` keeps its `bool`; tests assert the enum, not log text; zero signature churn | ✓ |
| `flash()` returns a result dataclass | Most expressive, callers cannot ignore it — but churn inside the merge's blast radius | |
| Log lines only | Smallest — but "state" becomes a string, asserted via brittle `caplog` text | |

**User's choice:** Enum attribute on the flasher + WARNING log.
**Notes:** Ordering constraint surfaced here and recorded in D-12 — `_finish()` leaves DFU mode and
the device resets off the bus, so readback must precede it.

### Q3 — What happens on a genuine MISMATCH?

| Option | Description | Selected |
|--------|-------------|----------|
| Hard failure — raise, exit 1 | Matches avrdude's verify-by-default parity that motivated HOST-03; soft stays reserved for "could not verify" | ✓ |
| Soft for everything | Uniform — but a verification step that cannot fail the build is decoration | |
| Hard, with an explicit opt-out flag | Useful if the bootloader returns garbage on UPLOAD — but research names a safety-overriding `--force` as an anti-feature | |

**User's choice:** Hard failure — raise, exit 1.

### Q4 — How much is read back and compared?

| Option | Description | Selected |
|--------|-------------|----------|
| Full payload, byte-for-byte | The only compare that means "the flash holds what we sent"; matches avrdude; cheapest to assert against a mock | ✓ |
| Full payload, chunked with a progress line | Avoids looking like a hang — but the download path prints nothing either, so it would be inconsistent | |
| First and last block only | Two round trips — but "verified" would mean "the ends match" | |

**User's choice:** Full payload, byte-for-byte.

---

## Flash-map reconciliation — 127 or 129?

### Q1 — Does the host envelope guard learn about Phase 126's reservation here?

| Option | Description | Selected |
|--------|-------------|----------|
| Tighten the guard to the app region, in 127 | Closes a divergence Phase 126 created, in the only repo that can close it, while the fact is fresh | ✓ |
| Warn, don't refuse | Preserves full-flash recovery writes — but a warning is not a guard, and the envelope refusal is deliberately non-overridable | |
| Doc only in 127, code deferred to 129 | Avoids editing the same constants twice | |
| Defer all of it to 129 | Strictly inside HOST-01…08 — but leaves the doc contradicting the linker script through 127–128 | |

**User's choice:** Tighten the guard to the app region, in 127.
**Notes:** Presented with the honest risk assessment — DfuSe erase is payload-scoped, so a ≤120K
app image never touches Sector 15; the defect is that the *guard* is looser than the map. Live map
read first: `FLASH 0x08000000/120K`, `CONFIG 0x0801E000/8K`, `BOOTLOADER 0x08000000/LENGTH 0`.

### Q2 — How does the host constant stay honest against the linker script?

| Option | Description | Selected |
|--------|-------------|----------|
| Cross-repo gate parsing the linker script, fail-CLOSED | `@requires_fw` binding + an explicit non-vacuity assertion, or it is research finding A-7 verbatim | ✓ |
| Hardcoded constant + citing comment | No new gate, no fail-open surface — but nothing detects it when Phase 129 moves the map | |
| Hardcoded + a todo owned by Phase 129 | Honest about the coupling without a gate needing its own fixture to trust | |

**User's choice:** Cross-repo gate parsing the linker script, fail-CLOSED.
**Notes:** A-7 measured a firmware rename flipping five gate legs PASS→SKIP at exit 0 with a false
reason, and moving firmware files is this milestone's premise — hence the two non-negotiable
properties written into D-14.

### Q3 — What does `doc/PY32F071-FIRMWARE-INSTALL.md` get here?

| Option | Description | Selected |
|--------|-------------|----------|
| Facts this phase changed, only | 127 documents what it built, 129 documents what it decides | ✓ |
| Full reconciliation pass now | One coherent document — but writes down flash-path positions 129 has not decided | |
| A "current as of Phase 127" header | Minimal and honest about staleness — but a doc that contradicts the linker script *and admits it* is worse than either fixing it or not shipping it | |

**User's choice:** Facts this phase changed, only.

### Q4 — How should post-merge semantic breakage land?

| Option | Description | Selected |
|--------|-------------|----------|
| Merge commit, then fixups in separate commits | History honestly shows what the 87-commit drift cost; each repair reviewable alone; red intermediate accepted | ✓ |
| Merge with `--no-commit`, fix, then one green commit | No red state — but the drift repairs become invisible inside a merge commit nobody can diff | |
| Rebase `4ee64a1` onto the branch first | Cleanest linear result — but rewrites the SHAs, so Criterion 1 fails literally | |

**User's choice:** Merge commit, then fixups in separate commits.
**Notes:** Criterion 1 forces a real merge commit, the opposite of Phase 124 D-05's squash. Not an
inconsistency — 124's squash was forced by *its own* Criterion 1 (an ancestor-branch constraint)
that has no analogue here. D-16 records both halves so a reader does not read it as drift.

---

## Claude's Discretion

Three requirements were not put to the user, on the grounds that they are mechanical once the
discipline above is fixed. Recorded in CONTEXT.md as D-17…D-19 with their rationale:

- **HOST-01** — where the accepted-deviation record lives (evidence artifact + a comment at
  `flash_method()`), and what it must say about `_install_with_avrdude` being untouched.
- **HOST-06** — which opcode literals get independently written from UM1504 / DFU 1.1, and the
  ruling that the existing self-referential assertions are *removed or converted*, not merely
  supplemented.
- **HOST-07** — `pyusb>=1.3.1,<2`, measured as zero-cost against the project's py39 floor.

Plus three lower-stakes defaults: `ci-py32` runs pytest only (no duplicate lint/mypy/coverage);
the evidence artifact is `127-NONREGRESSION.md`; one operator-gated CI dispatch at the end of the
phase rather than one per wave.

## Deferred Ideas

- Full reconciliation of `doc/PY32F071-FIRMWARE-INSTALL.md` (flash path, `BOOTLOADER` sizing,
  VID/PID, strapping, SWD pads, socket-empty line, seed-not-retired statement) → Phase 129.
- Re-checking D-13's application-region constant once `BOOTLOADER` gets a non-zero length → Phase 129.
- `--sdp-relock` → unscheduled (pre-existing v1.22 deferral, unrelated).
- The self-flash bootloader over CDC + COBS — the seed's *primary* route; landing DFU does not
  retire it, and Phase 129 must say so explicitly.

**Reviewed todos, not folded:** `avrdude-mcu-detection-fallback` (would contradict HOST-01's
freeze on `_install_with_avrdude`), `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads`,
`prove-pio-dev-flag-fails-closed`, `cobs-decoder-framelevel-deadline-wr01` — all firmware-area
keyword matches with no host surface.

**No scope creep occurred.** D-13 is a deliberate in-scope addition with no HOST id, adjudicated
by the user rather than assumed, and recorded as such.
