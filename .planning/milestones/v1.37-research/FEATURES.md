# Feature Research

**Domain:** Community-facing hardware validation harness that files public defect reports against a device under test
**Milestone:** v1.36 `dev test` Fidelity — Only Run What Can Tell You Something, Report Only What You Know
**Researched:** 2026-09-02
**Confidence:** **HIGH** on every claim read verbatim out of a canonical artifact (OCP `ocp-diag-core` spec, flashrom `include/flash.h`, `smartctl.8.in`, and this repo's own `firestarter_app` tree at `0a93999`); **LOW** on the general-web claims. Per-claim tiers in §7. The `classify-confidence` seam returns `LOW` for `websearch`/`webfetch` unconditionally; where I depart from that floor I show the exact retrieval so the claim is re-checkable rather than asserted.

**Scope note.** This file answers the three questions in the research brief and then converts them into
table-stakes / differentiator / anti-feature rows. It deliberately does **not** re-research the six
already-built features (`dev test` itself, derived plan, independent non-fatal steps, fingerprint
classifier, dual-output report at schema 1.7, dedup fingerprint, no-auto-graduate lock). Every row
below names which of those it depends on.

---

## 0. The headline finding, up front

**There is an established, published, industry-body taxonomy for exactly the problem v1.36 exists to
solve, and it is a two-axis model, not a one-axis one.**

The **OCP Test & Validation Initiative** output specification (`opencomputeproject/ocp-diag-core`,
`json_spec/README.md`) separates:

| Axis | Enum | Meaning (verbatim from the spec) |
|---|---|---|
| **TestStatus** — *did the run execute validly?* | `COMPLETE` | "The diagnostic completed execution normally." |
| | `ERROR` | "The diagnostic did not complete execution normally due to an exception." |
| | `SKIP` | "The diagnostic was skipped or did not run to normal completion as part of its execution." |
| **TestResult** — *what is the verdict on the DUT?* | `PASS` | "Test has detected no non-conformances during execution." |
| | `FAIL` | "Test has detected non-conformances related to the hardware or software under test during execution." |
| | `NOT_APPLICABLE` | "The test status of a diagnostic was not complete so no final test result verdict can be successfully rendered." |

And it **locks the legal cross-product to four cells**:

| TestStatus | TestResult | Spec's example use-case |
|---|---|---|
| `SKIP` | `NOT_APPLICABLE` | "Diagnostic found no applicable hardware or received external abort request" |
| `ERROR` | `NOT_APPLICABLE` | "Diagnostic encountered error preventing normal execution" |
| `COMPLETE` | `PASS` | no non-conformances detected |
| `COMPLETE` | `FAIL` | non-conformances detected |

> "Any other combination of TestResult and TestStatus shall be considered invalid."

At artifact level the same split is enforced again:

- An **Error** artifact "reports a software, firmware, test or any other **hardware-unrelated** issue."
  Its required attribute is `symptom` — "a short string of the software issued verdict".
- A **Diagnosis** artifact "gives the verdict of the health status for **hardware components under
  test**", with `DiagnosisType` ∈ `PASS` / `FAIL` / `UNKNOWN`, where `UNKNOWN` is "could not determine
  whether it is functioning within specification."
- The spec explicitly distinguishes a `Log` message at ERROR severity (a non-critical software event)
  from an `Error` artifact (something that prevents test completion).

**Why this matters more than any other finding in this file.** v1.36's third target feature is "a tool
or rig fault is never filed as a chip verdict." The `dev test` harness today has **one** verdict axis
(`VERDICT_OK` / `VERDICT_BAD` / `VERDICT_NA` / `VERDICT_SKIPPED` / `marginal`, `chip_test.py:893-897`)
and it is the *result* axis. It has no *status* axis. That is precisely why
`chip_test.py:2567-2574`'s handler —

```python
except (SerialError, HardwareOperationError) as exc:
    return StepResult(op=step.op, verdict=VERDICT_BAD, reason=str(exc), run_count=1)
```

— has no honest place to put "a half-seated cable" and is forced to spend `VERDICT_BAD`, a chip
verdict, on a rig event. The comment above it already knows this is wrong ("a half-seated cable or
other transport-level fault"). The escape hatch immediately above it (`ProgrammerNotFoundError`,
`FirmwareOutdatedError`, `HardwareRevisionUnsupportedError` re-`raise`) shows the project already
invented half of the status axis by hand — but it only has two settings, *abort the whole run* or
*call the chip bad*, and gh#23's "the first one didn't have VPP correctly hooked up" lands in the gap
between them.

**Recommendation: adopt OCP's two-axis vocabulary rather than inventing one.** It is published by a
hyperscaler consortium, has reference implementations in Python (`ocptv` on PyPI), Rust, Go, C++, and
— decisively for the dedup-fingerprint constraint — it is *additive* to the existing verdict set
rather than a replacement for it.

---

## 1. Question 1 — how comparable tools decide which diagnostics to run

### 1.1 The three real strategies, and their names

| Strategy | Established name / vocabulary | Who actually does this | Fit for `dev test` |
|---|---|---|---|
| **Fixed sweep, every time** | "full pass", "extended self-test" | `memtest86` default all-tests pass; `badblocks` default 4-pattern write test | What `dev test` does today. Wrong for R1–R4. |
| **Named escalating tiers, operator picks depth** | **short / extended / conveyance / selective self-test** (ATA `SMART EXECUTE OFF-LINE IMMEDIATE`) | `smartctl -t short|long|conveyance|select` | **Best fit.** Real, decades-old, chip-adjacent vocabulary. |
| **Cheap oracle then escalate** | "screening test" → "fault isolation"; in JUnit-family terms "smoke then regression" | `smartctl` short test = small surface sample; `badblocks -n` non-destructive vs `-w` destructive | Fits R2/R3 (verify-instead-of-read, structured sample instead of second sweep). |

**The SMART tier vocabulary is worth stealing wholesale**, because each tier has a *stated purpose*,
not just a *duration*:

- **short** — a few minutes, checks only a small portion of the medium.
- **extended / long** — the entire surface, hours.
- **conveyance** — ATA-only, several minutes, and its *declared purpose is to detect damage that
  happened in transit, i.e. an environment fault rather than an intrinsic device fault*.
- **selective** — a caller-specified LBA range only.

`conveyance` is the closest published precedent for a diagnostic whose *whole job* is to arbitrate
"is this the part, or is this what happened around the part". A `dev test` analogue — a fast
rig-sanity leg run before the chip legs — has a name and a pedigree.

`selective` is the published precedent for v1.36's R3 ("the read step's second full sweep, replaceable
by a bit-structured sample that toggles every address line in both polarities"): a *declared,
caller-scoped subset* rather than a whole-device sweep, reported as such.

### 1.2 The per-operation coverage lattice — flashrom

flashrom is the closest living analogue to `dev test`: an open-source, community-reported,
chip-database-driven programmer whose support claims are *contributed by users running the tool on
real hardware*. Read verbatim from `flashrom/include/flash.h` (fetched 2026-09-02):

```c
enum test_state {
	OK = 0,
	NT = 1,	/* Not tested */
	BAD,	/* Known to not work */
	DEP,	/* Support depends on configuration (e.g. Intel flash descriptor) */
	NA,	/* Not applicable (e.g. write support on ROM chips) */
};

struct tested {
	enum test_state probe;
	enum test_state read;
	enum test_state erase;
	enum test_state write;
	enum test_state wp;
} tested;
```

Three things fall straight out of this:

1. **Support is tracked per operation, not per chip.** A chip is not "supported"; its *probe* is OK,
   its *read* is OK, its *erase* is NT. `dev test` already runs independent non-fatal steps, so it
   already produces this shape — but the report's ladder collapses it into one disposition.
2. **`NT` (not tested) is a first-class value distinct from `BAD`.** flashrom will not let silence be
   read as either success or failure. The `TEST_OK_PROBE` / `TEST_OK_PR` / `TEST_OK_PRE` /
   `TEST_OK_PREW` / `TEST_OK_PREWB` macro ladder makes *partial* coverage the normal, expressible case.
3. **`DEP` — "support depends on configuration" — is an explicit environment-conditional verdict.**
   That is a published precedent for "this failed, but under a rig/config condition that is not the
   chip's fault." There is no `DEP` in `dev test` today.

flashrom's contribution rule is also directly relevant to the submit path: *"Providing full logs which
indicate successful run is required to mark chip as tested."* Evidence is mandatory before a status
moves. This is the same instinct as the existing no-auto-graduate lock (GRAD-01) and confirms it.

### 1.3 Anti-pattern found in the wild: the always-on diagnostic whose output is empty

`smartctl` has a genuinely interesting honesty device here: the `-j u` flag emits
`smartctl_NNNN_u` keys for *"lines from the plaintext output which print info still **u**nimplemented
for JSON output"* — the tool machine-readably declares its own coverage gap rather than letting the
absence read as "nothing to report." That is the inverse of R1: `dev test` currently *runs* work whose
output is empty by construction, where smartctl *doesn't run it* but *says so*.

---

## 2. Question 2 — separating a DUT fault from a harness / rig / operator fault

### 2.1 Yes, there is an established taxonomy — several, converging

| Precedent | Vocabulary | Where the split lives |
|---|---|---|
| **OCP `ocp-diag-core`** | `TestStatus{COMPLETE,ERROR,SKIP}` × `TestResult{PASS,FAIL,NOT_APPLICABLE}`; `Error` artifact vs `Diagnosis` artifact; `DiagnosisType.UNKNOWN` | Two orthogonal enums, legal cross-product locked to 4 cells |
| **xUnit / JUnit XML / pytest** | **failure** vs **error** | A failed assertion inside the test body is a `failure`; an exception in setup/teardown/collection is an `error`. `<testsuite errors="">` is a separate counter from `failures=""`. Errors are "reserved for test abortions" |
| **Linux Test Project (LTP)** | `TPASS` / `TFAIL` / `TCONF` / `TBROK` / `TWARN` | `TCONF` = "test is not suitable for the current configuration" (optional functionality missing); `TBROK` = "something unexpected happened in the test setup and the test was aborted"; `TWARN` = "something unexpected happened but the test carried on" |
| **kselftest / KTAP** | `KSFT_PASS` / `KSFT_FAIL` / `KSFT_SKIP` (exit 4) / `KSFT_XFAIL` / `KSFT_XPASS` | Skip is a distinct exit code, not a pass |
| **`smartctl` exit status** | 8-bit **bitmask**, orthogonal channels | Bit 0 "command line did not parse", Bit 1 "device open failed", Bit 2 "SMART command … failed, or there was a checksum error" — *tool/transport* bits — versus Bit 3 "SMART status check returned DISK FAILING" — the *device verdict* bit |
| **SMART self-test log** | "Completed without error" / "Aborted by host" / "Interrupted (host reset)" / "Fatal or unknown error" / "read element of test failed" | Aborted / interrupted are *invalid runs*, structurally distinct from an element failing |
| **Maintenance & ATE literature** | **NFF / NTF / NDF / CND / RTOK / NFI** | "No Fault Found", "No Trouble Found", "Cannot Duplicate", "Re-Test OK" — the unit was pulled on a complaint and the lab could not reproduce it. There is an explicit academic push toward a *standardised* taxonomy (Cranfield, *"No Fault Found, Retest OK, Cannot Duplicate or Fault Not Found? — Towards a standardised taxonomy"*) |
| **Manufacturing test theory** | **test escape** (bad part passes, β/underkill) vs **false failure / overkill** (good part fails, α); **Gauge R&R / MSA** asks whether variance is in the part or the gauge | Names both directions of the error the harness itself can make |

**The single most citable name for v1.36's core defect is "false failure" / "overkill"** — a
conforming device failed because of the measurement system, not the part — and the discipline that
exists to prevent it is **measurement system analysis**: you must first show the gauge is capable
before you believe the gauge about the part. gh#23 (VPP not hooked up) is a textbook false failure.
gh#28 / gh#31 (chip isn't erased between writes) are textbook **test method defects**, not device
defects.

`smartctl`'s exit bitmask deserves special note: it does not model this as a single ordered severity
scale. Bits 0–2 (tool/transport) and bit 3 (device verdict) are **independently settable**. A run can
simultaneously be "the command failed to reach the device" and "no device verdict rendered." That is
the encoding `dev test` needs and cannot express with one `verdict` string per step.

### 2.2 How the automated reporters present it — the "don't file this" precedents

This is the part that maps onto `[dev test] <chip> — FAIL` being offered as a GitHub issue.

**Linux kernel taint flags.** The kernel marks itself tainted when something happened that "might be
relevant later when investigating problems," prints the taint string in every oops/BUG/panic, and the
documented consequence is blunt: *"Bug reports from tainted kernels will often be ignored by
developers, hence try to reproduce problems with an untainted kernel."* Two design details are
directly transferable:

- The taint is **carried into the report**, not just shown on screen. The report itself declares its
  own trustworthiness.
- **The taint is sticky.** "The kernel will remain tainted even after you undo what caused the taint
  … to indicate the kernel remains not trustworthy." A rig fault mid-run should not be erased by a
  later good step.

**ABRT / libreport `not-reportable`.** ABRT writes a `not-reportable` element into a problem
directory containing a **reason string**; when present, the reporting workflow refuses to submit and
shows the reason. ABRT's oops handler puts the list of tainted modules into that string, and by
default ABRT will not handle crashes from third-party (unpackaged) software at all. This is the exact
mechanism v1.36 needs: **a machine-readable, reason-carrying suppression of the submit path**, not a
softened title.

**avrdude**, in the same problem space as this project, illustrates the cost of *not* having this:
`avrdude: verification error, first mismatch at byte 0x….` is a device-shaped message that the
community overwhelmingly triages to *rig* causes — a USBasp supplying only 3.3 V, wiring, fuse
settings, back-to-back invocations racing. The tool reports a device symptom; the fault is the bench.
That is this milestone's problem, already a decade old, in the nearest neighbouring tool.

**minipro** takes the operator-override route instead of the classification route:
`-y, --no_id_error` ("Do NOT error on ID mismatch"), `-s, --no_size_error`, `-e, --skip_erase`,
`-x, --skip_id`, `-v, --skip_verify`, `-b, --blank_check`. Every gate is individually defeatable by
flag. **This is a warning, not a model to copy**: it moves the classification burden onto the
operator, and a defeated gate leaves no trace in any report. Note in particular that `-e/--skip_erase`
is precisely the shape of v1.36's `FLAG_SKIP_BLANK_CHECK` on `uv-slot` writes — the difference being
that v1.36 derives it from the plan rather than accepting it from the CLI, which is the strictly
better half of the pattern.

### 2.3 The vocabulary gap in `dev test` today, stated precisely

Measured against `firestarter_app` @ `0a93999`:

| What exists | Where | What it cannot express |
|---|---|---|
| `VERDICT_OK` / `BAD` / `NA` / `SKIPPED` / `marginal` | `chip_test.py:893-897` | Result axis only. No status axis. |
| Run-fatal escape for 3 host-setup exceptions | `chip_test.py:2441-2460` | Only two settings: kill the run, or blame the chip. |
| Transport fault → `VERDICT_BAD` | `chip_test.py:2567-2574` | **The defect.** Rig event spends a chip verdict. |
| `FP_INDETERMINATE` fingerprint class | `chip_test.py:141` | Classifies a *byte pattern*, not a *run*. |
| `_DISPOSITION_INCONCLUSIVE` + `_LADDER_NONE` | `diagnostic_report.py:~312` | Exists for the DB-diff ladder only; does not gate submit. |
| `is_submittable(ac)` | `diagnostic_report.py:150-162` | Gates on **identity completeness** (`chip`, `protocol`, `host_version`) only — never on run validity. |

The good news for scoping: **`is_submittable` is already the single choke point** and it is already
documented as "the auto-captured identity needed to act on a report." Adding a run-validity term to it
is a small, well-sited change — not a new subsystem.

---

## 3. Question 3 — what a good machine-readable diagnostic report contains, and how its schema evolves

### 3.1 Contents — the convergent minimum

Drawn from OCP `ocp-diag-core`, SARIF 2.1.0, `smartctl --json`, and Sentry's event envelope:

| Element | Precedent | Present in schema 1.7? |
|---|---|---|
| Schema/format version as the **first** thing emitted | OCP: "`schemaVersion` … shall be the first message emitted by the diagnostic". smartctl: `json_format_version: [1,0]` | Yes — `SCHEMA_VERSION` at `diagnostic_report.py:48`, `"schema_version"` first key in `to_dict()` at `:779` |
| Tool identity + **version** + exact invocation | OCP `TestRunStart` carries "diagnostic name, version, command line invocation" | Partly — `host_version`, `fw_board_identity`; no invocation |
| **DUT inventory** with stable IDs that later artifacts reference | OCP `DutInfo`, hardware/software components "assigned unique IDs for later reference" | Partly — chip, protocol, hw_revision. v1.36's `chip_id_actual` on a *passing* id check closes a real gap |
| Per-step start/end bracketing with its own status | OCP `TestStepStart` / `TestStepEnd` | Yes — `StepResult` per step |
| **Measurements** kept separate from verdicts | OCP `Measurement` vs `Diagnosis` — "a simple validation test may not output any measurements, opting to just have a final Diagnosis outcome" | Gap. v1.36's `total`/`bad`/`bad_pct`/`evidence`/`divergence` export is exactly this split, and OCP endorses making measurements *optional siblings* of the verdict |
| Software-fault channel distinct from device verdict | OCP `Error{symptom, message, softwareInfoIds, sourceLocation}` | **Missing entirely** |
| Grouping / dedup key | Sentry fingerprint; crash-stats signature | Yes — `dedup_fingerprint` |
| Timing | wall clock and per-operation | v1.36 adds `elapsed` + per-op `duration_s`. Note `_RAN_VERDICTS` already refuses `0.0` on a step that didn't run (`chip_test.py:2389-2391`) — that discipline is the model for every new field |
| Vendor extension point that older consumers can ignore | SARIF: every object may carry a `properties` property bag "allowing SARIF producers to include information … not explicitly specified" | Absent — and probably should stay absent (see anti-features) |

### 3.2 Schema evolution — the conventions, and the one that binds here

**OCP states the rule explicitly and it is exactly semver-for-schemas:**

- **Major** = "breaking changes that affect the parsing of the ensuing information" — *renaming or
  deletion of fields, removal of enumeration values, or cardinality changes*. Major resets minor to zero.
- **Minor** = "non-breaking changes such as the addition of a field or clarification of documentation"
  that "do not compromise existing diagnostic compliance."

**Applied to v1.36's stated plan, this produces a finding the milestone should hear.** v1.36 intends
schema **1.8** — a *minor* bump — while it (a) adds fields, (b) fills fields, and (c) **deletes
`voltage.vpp_mv`, `voltage.vpe_mv`, and `banner.locked_steps`**. Under the OCP rule, *field deletion
is a major change*. Three honest resolutions, in preference order:

1. **Deprecate rather than delete.** Keep the three keys emitted as `null`/`NOT_MEASURED` for one
   schema generation with a documented sunset, delete at 2.0. Costs three keys; keeps 1.8 truthful.
2. **Call it 2.0.** Honest, but re-keys nothing in `dedup_fingerprint` (the hash doesn't read
   `schema_version`) so it is cheap — the cost is purely that every downstream reference to "schema
   1.x" moves.
3. **Ship 1.8 with deletions and say so in the changelog.** Defensible *only* because the milestone
   can prove no code path assigns those three fields, i.e. they were never real data. Worth stating
   that proof in the requirement rather than leaving it implicit — "no code path assigns" is the whole
   justification and it should be a test, not a claim.

SARIF's **property bag** is the standard escape valve for additive extension without a version bump.
`smartctl` takes the looser route: `json_format_version` has sat at `[1,0]` across many releases while
fields were added, with the implicit must-ignore-unknown contract — a live demonstration that
consumers tolerate additive change but that a *stated* policy is better than an implied one.

**Sentry's grouping lesson is the sharpest constraint of all** and independently confirms v1.36's own
blast-radius gate: fingerprint rules "apply retroactively to new events, but existing issues are not
re-grouped." Changing a fingerprint does not migrate history — it **forks** it, silently, and the old
and new populations never rejoin. The project has already lived this: `diagnostic_report.py:170-181`
records that the SDP leg re-keyed 43 measured chips and orphaned gh#20's `00e121446ceb`. The
byte-identity gate on `dedup_fingerprint` is therefore not conservatism, it is the correct and
industry-standard posture, and the "add beside `classification`, never replace it" rule is exactly
right.

---

## 4. Feature landscape

### 4.1 Table stakes — a validation harness that files public issues must have these

| Feature | Why expected | Complexity | Depends on (existing) | Notes |
|---|---|---|---|---|
| **T1. A run-status axis orthogonal to the chip verdict** — every step carries *did this run validly* separately from *what did it say about the chip* | Universal across OCP, JUnit, LTP, kselftest, smartctl exit bits. Without it a rig fault has nowhere to go but the verdict field | **MEDIUM** | Independent non-fatal steps; `StepResult` | Additive field on `StepResult`; existing `verdict` values keep their meaning. Adopt OCP names (`COMPLETE`/`ERROR`/`SKIP`) rather than coining. Enforce the 4-cell legal cross-product in a test |
| **T2. Transport / rig faults classified as `ERROR`, never `BAD`** | This is the milestone's stated defect; `chip_test.py:2567-2574` is the exact site | **LOW** once T1 exists | T1; `chip_test.py:2498-2586` | Move `SerialError`/`HardwareOperationError` from `VERDICT_BAD` to status=`ERROR`, result=`NOT_APPLICABLE`. One handler. The comment already argues for it |
| **T3. A run containing an `ERROR` step is not submittable as a chip FAIL** | ABRT `not-reportable`; kernel taint; "bug reports from tainted kernels will often be ignored" | **LOW** | `is_submittable`; the submit prompt | Extend the *existing* choke point `is_submittable(ac)` with a run-validity term. Do not build a second gate |
| **T4. A machine-readable reason for non-submittability, carried in the JSON** | ABRT's `not-reportable` element is a **reason string**, not a boolean | **LOW** | Report `to_dict()` | Additive key. A human reading the JSON must be able to see *why* submit was withheld |
| **T5. Run-validity flags are sticky and reported even on a PASS** | Kernel taint survives unloading the module; SMART self-test log keeps "Aborted by host" | **LOW** | Report | A run that re-synced twice and then passed is still a run that re-synced twice. v1.36's `transport_health` wiring of `serial_comm.py:520-526` / `:536-541` is exactly this |
| **T6. `NOT_MEASURED` / not-run is a distinct value from both pass and fail, everywhere** | flashrom `NT`; LTP `TCONF`; kselftest exit 4; OCP `NOT_APPLICABLE` | **LOW** — largely already true | `VERDICT_NA`/`SKIPPED`; `_RAN_VERDICTS` | Already the project's instinct (`duration_s` stays `None` on a step that didn't run). Extend the same discipline to every new field |
| **T7. No operation runs whose result is empty by construction** | The R1–R4 core of the milestone; smartctl's `-j u` marks its own gaps rather than emitting empty work | **MEDIUM** | `derive_plan`; the fingerprint gate at `chip_test.py:3100` | The read-back gate must consult `outcomes`. Structural test over `derive_plan` output, same shape as `test_shipped_ops_never_reach_sdp_arm` |
| **T8. Canonical device naming in the report and issue title** | Every database-driven tool keys reports to a database identity, not a user token (flashrom `--flash-name`; smartctl drivedb) | **LOW** | Chip resolver; `build_title` | Report the matched `part_number`. Prerequisite for T3 being useful — an issue titled with a non-existent string can't be triaged |
| **T9. Per-operation coverage, not a per-chip verdict** | flashrom `struct tested {probe, read, erase, write, wp}` | **LOW** — already built | Independent non-fatal steps | Already have it. Named here so the roadmap doesn't regress it while adding T1 |
| **T10. Evidence required before any support-status movement** | flashrom: "Providing full logs which indicate successful run is required to mark chip as tested" | **NONE** — already built | GRAD-01 no-auto-graduate lock | Existing lock is correct and industry-standard. Do not weaken it |

### 4.2 Differentiators — real advantage, not required

| Feature | Value proposition | Complexity | Depends on (existing) | Notes |
|---|---|---|---|---|
| **D1. A named rig-sanity leg run before the chip legs** (the "conveyance test" analogue) | Turns gh#23's "VPP wasn't hooked up" from a post-hoc triage argument into a pre-run refusal. The one feature that would have prevented the specific rebuttal that motivated this milestone | **HIGH** | `derive_plan`; firmware VPP/VPE monitors | **Scope hazard.** Project memory records that vpp/vpe monitors *don't route to the socket*, so a rig leg can prove the rail exists but not that it reaches the chip — a blank/`0x303` read is the only contact-fault signal. A leg that over-claims here is worse than none. Consider deferring; at minimum, scope it to what the monitors can actually arbitrate |
| **D2. Escalating tiers with declared purpose** — `--tier short|full`, each tier stating what it can and cannot conclude | SMART's short/extended/conveyance/selective, verbatim precedent. Lets a reporter run something cheap first | **MEDIUM** | `derive_plan`; `coverage_tag` | `coverage_tag` already exists and is already in the dedup hash — a tier axis must either reuse it or stay out of the hash. Check before designing |
| **D3. A `DEP`-equivalent verdict: "failed under a configuration this rig cannot satisfy"** | flashrom's `DEP` is the published name. Distinguishes "your board can't do this" from "the chip can't do this" — e.g. the 999.44 firmware-half blank-check case that this milestone knowingly leaves broken | **MEDIUM** | T1; `derive_plan` | Directly serves the out-of-scope 999.44 firmware half: the host can *label* the known-bad case honestly this milestone even though it can't *fix* it |
| **D4. Measurements exported as optional siblings of the verdict** | OCP's `Measurement` vs `Diagnosis` split. Makes a report re-analysable without re-running the chip | **LOW** | Fingerprint classifier; report | This is RPT-A1…E3 almost exactly. OCP endorses the shape. Keep them siblings — never let a measurement become the verdict |
| **D5. Prior-report linkage on re-report** | Sentry issue grouping; `find_prior_report` already exists in `submit.py:362` | **NONE** — already built | dedup fingerprint; `submit.py` | Named so it isn't rebuilt |
| **D6. Deprecation window on deleted schema keys** | OCP's major/minor rule makes deletion a breaking change; deprecate-then-delete is the standard mitigation | **LOW** | Report `to_dict()` | Resolves the 1.8-vs-2.0 tension in §3.2 at the cost of three `null` keys |

### 4.3 Anti-features — plausible, requested, and wrong for this project

| Feature | Why it gets requested | Why problematic | Do instead |
|---|---|---|---|
| **A1. A softer FAIL — "POSSIBLE FAIL", "LIKELY CHIP ISSUE", confidence percentages on the chip verdict** | Feels kinder than a bare FAIL on a chip the reporter owns | Hedging is not honesty. OCP models this as `DiagnosisType.UNKNOWN` — *"could not determine whether it is functioning within specification"* — a **flat statement of ignorance**, not a graded belief. A percentage claims a calibration the harness does not have | `UNKNOWN` / `NOT_APPLICABLE`. One word, no number |
| **A2. A per-flag CLI override for every gate** (`--no-blank-check`, `--no-id-error`, `--force`) | minipro does exactly this (`-y`, `-s`, `-e`, `-x`, `-v`) and it is popular | Moves classification onto the operator, and a defeated gate leaves **no trace in the report** — so a forced run and a clean run are indistinguishable downstream. This directly manufactures the false-PASS the project has spent milestones eliminating | Derive the skip from the plan (v1.36's `FLAG_SKIP_BLANK_CHECK` on `uv-slot` writes is the right shape) and record the derivation in the report |
| **A3. Auto-filing issues, or auto-retrying a failed step until it passes** | "The tool already knows; why make me click" | Auto-retry-until-pass is the mechanism that manufactures **NTF/RTOK**: an intermittent fault that a retry loop launders into a PASS. The maintenance literature names this failure mode and it is expensive | Keep the human submit gate. Report `run_count` and divergence, which the project already does (`repeat_policy_tag`, run1-vs-run2 `_diff_offsets`) |
| **A4. A generic `properties` property bag / free-form extension point** | SARIF has one; it makes schema evolution painless | For *this* report it is a hole in the honesty model: anything can be written there, nothing is specified, and the `dedup_fingerprint` cannot safely be defined over it. SARIF can afford it because SARIF consumers are aggregators, not triagers | Named additive fields with a stated version policy. Accept the version bumps |
| **A5. Collapsing status and result into one enriched verdict enum** (adding `RIG_FAULT` as a sixth `verdict` value) | Looks cheaper than a second axis. One field, one place to change | It is a **cardinality change to an existing enum inside the dedup input**. `dedup_fingerprint` hashes `op=verdict:cls` triples (`diagnostic_report.py:~213`) — a new `verdict` value re-keys every group that hits it, exactly the Sentry fork, exactly the gh#20 orphan. And it makes the illegal states representable again | Second, additive, orthogonal field, kept **out** of the dedup hash. This is why T1 is MEDIUM and not HIGH |
| **A6. Re-keying `dedup_fingerprint` to include the new byte counts / classification split** | The new data is better data; the hash should reflect it | Re-keys every `count_agreeing` group in project history and disturbs GRAD-01. Sentry's documented behaviour: existing issues are **not** re-grouped, so history forks silently | The milestone's own blast-radius gate already says this. Assert byte-identity against the frozen schema-1.2 fixtures |
| **A7. Suppressing or downgrading a report because it *might* be a rig fault** | Natural over-correction after three community rebuttals | Turns a false-failure problem into a **test-escape** problem — the other, worse direction of the same error. A real chip fault silently withheld is undetectable | Suppress only on *evidence* of an invalid run (an `ERROR`-status step actually occurred). Never on suspicion or heuristic |
| **A8. A "score" or grade for a chip** | Compact, shareable | The report is evidence for triage, not a rating. Compresses away exactly the per-operation detail (flashrom's `struct tested`) that makes a report actionable | Per-operation verdicts, already built |
| **A9. Fixing the 999.44 firmware half opportunistically** | It's the actual root cause of gh#28/gh#31 | Explicitly out of scope at activation; drags in dual-repo lockstep, golden traces, size baseline. The milestone took this knowingly | Ship D3 (`DEP`-equivalent) so the known-bad case is *labelled* honestly, and leave the fix in backlog |

---

## 5. Feature dependencies

```
T1. run-status axis (OCP TestStatus)
     ├──enables──> T2. transport fault => ERROR, not BAD
     │                  └──enables──> T3. ERROR run is not submittable
     │                                    └──requires──> T4. machine-readable reason
     │                                    └──requires──> T8. canonical part_number in title
     ├──enables──> D3. DEP-equivalent ("rig/config cannot satisfy")
     └──conflicts──> A5. sixth value on the existing `verdict` enum

T5. sticky run-validity flags  ──requires──> T1
                               ──feeds────> transport_health (RPT, existing)

T7. no empty-by-construction operations
     ├──requires──> derive_plan (existing)
     ├──requires──> the load-bearing invariant: every write has a verify behind it
     │                └──enforced by──> structural test over derive_plan output
     └──enables──> D2. escalating tiers

D2. escalating tiers ──conflicts──> coverage_tag's presence in dedup_fingerprint
                                     (resolve before designing, not after)

D4. measurements as siblings ──requires──> fingerprint classifier (existing)
                             ──constrained by──> A6 / blast-radius gate

D6. deprecation window ──resolves──> the schema 1.8-vs-2.0 tension (field deletion is major)

GRAD-01 no-auto-graduate (existing) ──unaffected by──> everything above,
                                       PROVIDED dedup_fingerprint stays byte-identical
```

### Dependency notes

- **T2 requires T1, and nothing else does the job.** Without a status axis the only two available
  behaviours are the ones that exist today: re-`raise` (kills the run) or `VERDICT_BAD` (blames the
  chip). Adding a third `verdict` value is A5 and is rejected on dedup grounds.
- **T3 must reuse `is_submittable`, not add a parallel gate.** It is already the single documented
  choke point (`diagnostic_report.py:150-162`) and already carries the "objective, machine-captured
  identity" doctrine. A second gate would let the two disagree.
- **T7's one load-bearing dependency is already correctly identified in PROJECT.md**: dropping the
  unconditional read-back is safe *only* because a verify follows every write in the same cycle. The
  structural test must fail on a plan that emits a write with no verify. This is the single highest-risk
  item in the milestone because the safety argument lives outside the code that benefits from it.
- **D2 has a hidden collision with the blast-radius gate.** `coverage_tag` is already an input to
  `dedup_fingerprint`. Any tier mechanism that changes `coverage_tag`'s value for an existing chip
  re-keys its group. Check this before scoping D2, not during execution.
- **D1 is gated by a physical fact, not an engineering one.** Per project record, the VPP/VPE monitors
  do not route to the socket; a rig leg can confirm the rail and still miss a contact fault. Any
  requirement for D1 must state what it can and cannot conclude, or it becomes A1 in disguise.

---

## 6. MVP definition for v1.36

### Ship in this milestone (P1)

- [ ] **T1** run-status axis, OCP names, 4-cell legality asserted by test — *the enabling change*
- [ ] **T2** transport/rig faults become `ERROR`, not `BAD` — *the milestone's stated third target feature*
- [ ] **T3** `ERROR`-bearing run is not offered as `[dev test] <chip> — FAIL` — *what the community asked for*
- [ ] **T4** machine-readable non-submittable reason in the JSON
- [ ] **T5** sticky transport-health, reported on PASS runs too — *already scoped as the `serial_comm.py:520-526`/`:536-541` wiring*
- [ ] **T7** no empty-by-construction operations + the structural `derive_plan` test — *R1–R4*
- [ ] **T8** canonical `part_number` in report and title
- [ ] **D4** measurements as additive siblings — *RPT-A1…E3, already drafted*
- [ ] **UV blank-check skip** (999.44 host half) + the regression test that does not exist today
- [ ] **Blast-radius gate**: `dedup_fingerprint` byte-identical against frozen schema-1.2 fixtures

### Decide during requirements, don't assume

- [ ] **D6 / schema version number.** Field deletion is a *major* change under the OCP rule. Either
      deprecate the three dead keys for one generation (keeps 1.8 honest) or call it 2.0. Pick
      deliberately; do not let 1.8-with-deletions pass unexamined.
- [ ] **D3 `DEP`-equivalent.** Cheap, and it is the only way this milestone can be honest about the
      999.44 firmware half it is not fixing.

### Defer

- [ ] **D1 rig-sanity leg** — highest value against gh#23, but blocked on what the VPP/VPE monitors can
      actually arbitrate. Deferring is honest; shipping an over-claiming version is not.
- [ ] **D2 escalating tiers** — real precedent, real value, but collides with `coverage_tag` in the
      dedup hash. Speed is explicitly "the consequence, not the goal" this milestone; T7 already
      delivers the measured 31.5%.

---

## 7. Prioritisation matrix

| Feature | User value | Impl. cost | Dedup-hash risk | Priority |
|---|---|---|---|---|
| T1 run-status axis | HIGH | MEDIUM | **LOW if additive & excluded from hash; HIGH if it touches `verdict`** | P1 |
| T2 rig fault ⇒ ERROR | HIGH | LOW | LOW | P1 |
| T3 ERROR ⇒ not submittable | HIGH | LOW | NONE | P1 |
| T4 reason string | MEDIUM | LOW | NONE | P1 |
| T5 sticky transport health | MEDIUM | LOW | NONE (additive) | P1 |
| T6 not-measured distinctness | MEDIUM | LOW | NONE | P1 (mostly built) |
| T7 no-information ops removed | HIGH | MEDIUM | **MEDIUM — changes which steps run, which changes `coverage_tag`** | P1 |
| T8 canonical part_number | MEDIUM | LOW | **MEDIUM — verify `chip` is not hashed as a raw token** | P1 |
| D4 measurements as siblings | MEDIUM | LOW | LOW (additive beside `classification`) | P1 |
| D6 deprecation window | LOW | LOW | NONE | P2 |
| D3 DEP-equivalent | MEDIUM | MEDIUM | LOW | P2 |
| D2 escalating tiers | MEDIUM | MEDIUM | HIGH | P3 |
| D1 rig-sanity leg | HIGH | HIGH | LOW | P3 (blocked on physics) |

**Two rows carry a dedup risk the milestone brief does not currently flag.** T7 changes which steps
run, and T8 changes the chip token — both are plausibly upstream of `dedup_fingerprint` inputs
(`coverage_tag`, and the `op=verdict:cls` triple set). The brief's gate says "not one field being
added, filled or deleted is in that hash today." That is a statement about *fields*, not about *which
steps exist* or *what the chip is called*. **Verify both against the frozen schema-1.2 fixtures before
scoping, not after implementing.**

---

## 8. Competitor feature analysis

| Concern | flashrom | smartctl / SMART | OCP ocp-diag | minipro | `dev test` today | v1.36 recommendation |
|---|---|---|---|---|---|---|
| Per-operation verdicts | `struct tested {probe,read,erase,write,wp}` | per self-test-element | per `TestStep` | none | **has it** | keep |
| Not-tested distinct from failed | `NT` vs `BAD` | self-test log "aborted" vs "failed" | `SKIP`+`NOT_APPLICABLE` | none | `NA`/`SKIPPED` | keep, extend to new fields |
| Environment-conditional verdict | **`DEP`** | `conveyance` test | `Error` artifact | none | **none** | adopt (D3) |
| Tool fault vs device fault | log-based, manual | **exit bitmask, orthogonal bits** | **two-axis enum, 4 legal cells** | `-y` override | **collapsed into `BAD`** | adopt OCP two-axis (T1/T2) |
| Suppress reporting on invalid run | n/a | n/a | n/a | n/a | none | ABRT `not-reportable` pattern (T3/T4) |
| Report trustworthiness carried in the artifact | n/a | self-test log status | `Error` + `softwareInfoIds` | n/a | partial | kernel-taint pattern, sticky (T5) |
| Evidence required to change support status | **yes, full logs** | n/a | n/a | n/a | **yes, GRAD-01** | keep; already best-in-class |
| Schema versioning policy | n/a | `json_format_version` `[1,0]`, implicit must-ignore | **explicit major/minor rule** | n/a | `SCHEMA_VERSION` string, no policy | state the policy; resolve deletion-vs-1.8 |
| Grouping/dedup | n/a | n/a | n/a | n/a | `dedup_fingerprint` | keep byte-identical (Sentry precedent) |
| Operator overrides | build-time | n/a | n/a | **every gate** | none | **do not adopt** (A2) |

**The single most useful comparison for the roadmap:** `dev test` is already ahead of flashrom on
evidence discipline (GRAD-01 vs "mail us your logs") and ahead of minipro on everything, but it is
behind `smartctl` — a tool from 2002 — on the one axis this milestone is about. smartctl has kept
"the command didn't reach the device" (bit 1/2) structurally separate from "the device is failing"
(bit 3) for its entire life. That is the whole of T1/T2.

---

## 9. Confidence assessment

| Claim | Retrieval | Seam verdict | My tier | Basis for departing |
|---|---|---|---|---|
| OCP `TestStatus`/`TestResult` enums, 4-cell table, `Error` vs `Diagnosis`, `DiagnosisType`, major/minor rule | `WebFetch` of `raw.githubusercontent.com/opencomputeproject/ocp-diag-core/main/json_spec/README.md`, quoted verbatim | LOW (`webfetch`) | **HIGH** | Canonical spec file, quoted, re-checkable at a stable raw URL |
| flashrom `enum test_state {OK,NT,BAD,DEP,NA}` + `struct tested` + `TEST_OK_*` macros | `curl` of `raw.githubusercontent.com/flashrom/flashrom/main/include/flash.h`, lines 188–208, 481–487 | LOW | **HIGH** | Source file read verbatim, line numbers cited |
| smartctl exit-status bitmask, `-j` sub-flags incl. `smartctl_NNNN_u` | `curl` of `smartmontools/smartctl.8.in`, `.SH EXIT STATUS` section quoted | LOW | **HIGH** | Manpage source read verbatim |
| minipro flag semantics (`-y`, `-e`, `-x`, `-v`, `-s`, `-b`) | `WebFetch` of mankier manpage rendering | LOW | **MEDIUM** | Third-party rendering of an upstream manpage; flag names consistent with upstream issue threads |
| LTP `TCONF`/`TBROK`/`TWARN`, kselftest `KSFT_SKIP`=4 | `WebSearch` over LTP docs + kselftest patch series | LOW | **MEDIUM** | Multiple independent sources agreeing; not read from source |
| pytest/JUnit failure-vs-error split, `<testsuite errors>` | `WebSearch` | LOW | **MEDIUM** | Well-established, corroborated by pytest issue tracker |
| Kernel taint semantics + "reports from tainted kernels will often be ignored" | `WebSearch` returning `tainted-kernels.rst` | LOW | **MEDIUM** | Quoted from the kernel doc via search snippet, not fetched raw |
| ABRT `not-reportable` element carries a reason; taint list written into it; 3rd-party crashes not handled by default | `WebSearch` over ABRT docs/wiki | LOW | **LOW–MEDIUM** | Mechanism corroborated across sources; exact file semantics **not** read from libreport source. **Verify before writing a requirement that mimics it precisely** |
| SMART short/extended/conveyance/selective purposes | `WebSearch` | LOW | **MEDIUM** | Consistent across ArchWiki, Thomas-Krenn, pfSense docs |
| NFF/NTF/CND/RTOK taxonomy + Cranfield standardisation paper | `WebSearch` | LOW | **MEDIUM** | Peer-reviewed paper exists; the *terms* are certain, a single ratified standard is **not** |
| Sentry: rules apply to new events, existing issues not re-grouped | `WebSearch` over Sentry docs | LOW | **MEDIUM** | Corroborated; and independently confirmed by this project's own gh#20 orphan record |
| SARIF property bags / forward compat | `WebSearch` over OASIS spec | LOW | **MEDIUM** | Spec is authoritative; read via search summary not raw |
| Every `firestarter_app` file:line citation in this file | `sed`/`grep` against the working tree @ `0a93999` | n/a | **HIGH** | Read directly |

**Named gaps.** (1) I did not read libreport's source, so the exact `not-reportable` file format is
MEDIUM at best — T4's *concept* is safe, its *mechanics* should not be copied on this evidence.
(2) There is no single ratified ISO/SAE standard for NFF terminology; the Cranfield paper is an
argument *for* one, which is itself the honest citation. (3) I did not verify whether `coverage_tag`
or the chip token are byte-inputs to `dedup_fingerprint` under every path — flagged twice above as
something requirements must confirm against the frozen fixtures rather than inherit from this file.

---

## Sources

**Primary artifacts read verbatim**
- OCP Test & Validation output specification — [json_spec/README.md](https://github.com/opencomputeproject/ocp-diag-core/blob/main/json_spec/README.md), [repo](https://github.com/opencomputeproject/ocp-diag-core), [initiative](https://www.opencompute.org/projects/test-and-validation-enablement-initiative), [`ocptv` on PyPI](https://pypi.org/project/ocptv), [ocp-diag-core-rust](https://github.com/opencomputeproject/ocp-diag-core-rust)
- flashrom `include/flash.h` — `enum test_state`, `struct tested`, `TEST_*` macros (`raw.githubusercontent.com/flashrom/flashrom/main/include/flash.h`)
- smartmontools `smartctl.8.in` — `EXIT STATUS` bitmask, `-j` sub-flags (`raw.githubusercontent.com/smartmontools/smartmontools/master/smartmontools/smartctl.8.in`), rendered [manpage](https://manpages.debian.org/unstable/smartmontools/smartctl.8.en.html)
- `firestarter_app` working tree @ `0a93999` — `chip_test.py`, `diagnostic_report.py`, `submit.py`, `serial_comm.py`

**Secondary**
- flashrom — [How to mark chip as tested](https://www.flashrom.org/contrib_howtos/how_to_mark_chip_tested.html), [Supported flash chips](https://www.flashrom.org/supported_hw/supported_flashchips.html), [Board Testing HOWTO](https://www.flashrom.org/Board_Testing_HOWTO)
- Linux kernel — [tainted-kernels.rst](https://www.kernel.org/doc/Documentation/admin-guide/tainted-kernels.rst)
- Linux Test Project — [C Test API](https://linux-test-project.readthedocs.io/en/latest/developers/api_c_tests.html), [tst_res(3)](https://github.com/linux-test-project/ltp/blob/master/doc/man3/tst_res.3); kselftest [KTAP/exit-code series](https://www.mail-archive.com/linux-kselftest@vger.kernel.org/msg08014.html)
- ABRT — [D-Bus API / problem elements](https://github.com/abrt/abrt/wiki/ABRT-D-Bus-API), [FAQ](https://github.com/abrt/doc/blob/master/faq.rst)
- pytest / JUnit XML — [error-vs-failure discussion #7950](https://github.com/pytest-dev/pytest/discussions/7950), [issue #5044](https://github.com/pytest-dev/pytest/issues/5044)
- SMART self-tests — [ArchWiki S.M.A.R.T.](https://wiki.archlinux.org/title/S.M.A.R.T.), [Thomas-Krenn SMART tests](https://www.thomas-krenn.com/en/wiki/SMART_tests_with_smartctl)
- minipro — [manpage](https://www.mankier.com/1/minipro)
- No-Fault-Found taxonomy — [Cranfield: *No Fault Found, Retest OK, Cannot Duplicate or Fault Not Found? — Towards a standardised taxonomy*](https://dspace.lib.cranfield.ac.uk/server/api/core/bitstreams/4ae14941-17c5-4771-8acc-4387b50a3cad/content), [No fault found (Wikipedia)](https://en.wikipedia.org/wiki/No_fault_found), [Ungar, *Causes and Costs of No Fault Found Events*](https://www.electronics.org/system/files/technical_resource/E38&S18-02%20-%20Louis%20Ungar.pdf)
- Sentry — [Event grouping](https://docs.sentry.io/concepts/data-management/event-grouping/), [SDK fingerprinting](https://docs.sentry.io/platforms/python/usage/sdk-fingerprinting/)
- SARIF — [OASIS SARIF 2.1.0 + Errata 01](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- Community rebuttals motivating the milestone — henols/firestarter_prom [#23](https://github.com/henols/firestarter_prom/issues/23), [#28](https://github.com/henols/firestarter_prom/issues/28), [#31](https://github.com/henols/firestarter_prom/issues/31)

---
*Feature research for: v1.36 `dev test` Fidelity*
*Researched: 2026-09-02*
