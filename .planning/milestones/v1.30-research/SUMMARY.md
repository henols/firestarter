# Project Research Summary

**Project:** Firestarter — v1.30 SDP Surface Retirement & Behavioral Lock Proof
**Domain:** Host-only Python CLI change (`firestarter_app`) — surface retirement + an *inverted-assertion* behavioural test leg + two fail-open gate repairs
**Researched:** 2026-08-03
**Tree measured:** `firestarter_app` @ `beta` `16a313a` · `firestarter` @ `0933bd7` (untouched) · meta @ `d1b9ce9e`
**Confidence:** HIGH

## Executive Summary

This is a debt-and-proof milestone on a mature single-repo host CLI. Six scope items: delete
`firestarter dev sdp`, add a plan-derived SDP lifecycle leg to `dev test`, add `write --sdp-relock`,
harden the fail-open mypy gate, land the 999.15/gh#8 `dev`-group channel split, and answer gh#12
outward. **Zero new dependencies, zero new frameworks, zero version bumps** — every item is served by
tooling already pinned in `pyproject.toml` and harnesses already committed under `tests/`. The only
stack-shaped decisions the milestone owes are a one-line `[tool.mypy] python_version` correction and a
rewrite of `check_mypy_watermark.py`'s result interpretation.

The research's central finding is that **the milestone's only deliverable — the oracle — is vacuous as
the planning record specifies it.** `generate_pattern(start, length)` is a pure function of
`(start, length)`, so patterns A and B are byte-identical if both are built the idiomatic way, making
"read-back equals A" unconditionally TRUE. Three further mechanisms compound it: `_diff_offsets`
reports zero differences for an empty read-back; `_dispatch_multi_run` makes the write's boolean the
verdict and runs it twice; and `SKIPPED`/`NA` both map to exit 0 by six enumerated routes. The leg
therefore cannot be built by reusing the module's blessed primitives — every one of them has the right
polarity for its original job and the wrong polarity for an equality oracle. Nine numbered corrections
below carry these; the Corrections section is not optional reading.

The recommended approach is gate-first, then delete, then build. Harden the checker *mechanism* before
any count is trusted (a number measured with a fail-open gate is meaningless); delete `dev sdp` next
because it drops the honest mypy count 69 → 63 for free and removes one row from 999.15's
classification table; establish a typed `AppContext` fixture and re-baseline the watermark before any
new test module is authored, or the new work either reddens the honest gate or hides behind a raised
one. The dominant risk is not implementation difficulty — it is **overclaiming at close**. The causal
claim *"the lock inhibited the write"* is unreachable this milestone, and the two existing
`check_permitted_claims.py` copies are both unsafe to copy verbatim (the v1.23 copy would print a
confident `PASS:` while scanning v1.23's own artifacts). The evidence ceiling below is reproduced
verbatim and must land in REQUIREMENTS before planning.

## Corrections to the Planning Record

The planning record for v1.30 = `.planning/notes/sdp-surface-retirement-and-behavioral-proof.md`,
`.planning/PROJECT.md` § Current Milestone v1.30, `.planning/ROADMAP.md` Phase 999.25, and
`.planning/research/questions.md` §999.25. **In 4 of the last 5 milestones a locked decision rested on
a false premise.** Each correction states the claim as the record has it, the measured truth, the
evidence, and the consequence for scope.

### R-1 (CRITICAL) — The oracle is VACUOUS as designed

- **The record says:** design note §4, step table: step 1 "write pattern A + verify"; step 3 "write
  pattern **B** with `FLAG_SKIP_SDP_UNLOCK`, then read back — the oracle: bytes must still equal
  pattern A." PROJECT.md repeats it.
- **Measured truth:** `chip_test.py:59 generate_pattern(start, length)` returns
  `bytes(address_fold_byte(start + i) for i in range(length))`, and `address_fold_byte` (`:48`) is
  `(addr ^ (addr>>8) ^ (addr>>16) ^ (addr>>24)) & 0xFF` — a pure function of the absolute address.
  There is exactly **one pattern per region** in this engine, and `_write_region_for(step, ...)`
  returns the region `derive_plan` fixed once for the whole plan. If step 1 and step 3 are both built
  the way every other write step in the module is built, **A and B are byte-identical** and
  "read-back equals A" evaluates TRUE unconditionally — whether the lock inhibited the write, whether
  the lock did nothing, whether the write silently no-op'd, or whether the part is a brick still
  holding A. It looks completely idiomatic in review because it reuses the module's blessed generator.
- **Evidence:** PITFALLS P-01 (first-party read, HIGH); FEATURES §1.1 measured `generate_pattern` for
  `AT28C256` region `(0, 256)` = `00 01 02 03 …`; ARCHITECTURE §2.4 independently confirms purity.
- **Consequence for scope:** the design note §4 step table **as written is invalid** and must not be
  transcribed into requirements. The two research proposals are reconciled in **A-3**. This also
  invalidates the implicit assumption that the leg is a small append to `derive_plan`: it needs a
  second named pattern generator, its own dispatch arm, and a transition-proving baseline.

### R-2 (CRITICAL) — `_diff_offsets` reports ZERO differences for an empty read-back

- **The record says:** nothing — the record treats read-back comparison as a solved primitive, and
  `chip_test.py:86-88` **mandates** `_diff_offsets` as the single divergence implementation (D-04).
- **Measured truth:** `chip_test.py:93-104` — `cmp_len = min(len(expected), len(actual))`;
  `diff_offsets = [o for o in range(cmp_len) if expected[o] != actual[o]]`; `pct = … if cmp_len else
  0.0`. Its own docstring: *"unequal-length inputs are compared only over their common prefix and never
  raise."* With `actual = b""`: `cmp_len == 0`, `diff_offsets == []`, `pct == 0.0`. **A total read
  failure is indistinguishable from a byte-perfect match.** Same for a short read-back whose prefix
  happens to match.
- **Evidence:** PITFALLS P-02 (first-party read, HIGH).
- **Consequence for scope:** the mandated divergence primitive reads a total read failure as perfect
  equality. The leg needs an explicit **length gate before any comparison**, returning `VERDICT_BAD`
  (never `SKIPPED`), plus four planted-fixture cases (`b""`, short prefix, all-`0xFF`, all-`0x00`) each
  asserting BAD. A named requirement, not an implementation detail.

### R-3 (HIGH) — `write` never verifies, so `--sdp-relock`'s decided polarity has no hook

- **The record says:** PROJECT.md — *"Polarity decided (operator, 2026-08-03): on verify failure the
  relock is SKIPPED and the skip is reported loudly."* The design note §8 carries the v1.22 assumption
  that the relock is *"gated on verify success."*
- **Measured truth:** there is **no `verify_eprom` call anywhere in the `write` handler**
  (`cli_handlers.py:529-691`, read end to end; grep-confirmed negative). Verification is a separate
  command (`@cli.command(name="verify")` at `:694`). `write_eprom`'s `ok` (`eprom_operations.py:1583`
  → `:1676`) is firmware's own write/data-poll result plus the `0x86`-ack audit at `:1655-1666` —
  **not** a read-back comparison of contents.
- **Evidence:** ARCHITECTURE §5.2 (HIGH, grep-confirmed negative).
- **Consequence for scope:** **this is a scope addition, not a wiring detail.** The decided polarity
  requires a verify pass to *exist*. Recommended (ARCHITECTURE design B): when `--sdp-relock` is
  passed, run an explicit `verify_eprom(eprom, eprom_data, input_file, address_str=address)` after a
  successful write and gate the relock on **both** results — costing an extra pass only on runs that
  asked for the flag, leaving the default `write` path byte-identical. The polarity is decided; the
  mechanism it gates on is new work.

### R-4 (CRITICAL, safety) — `sdp_unlock` must be EXEMPT from `_DESTRUCTIVE_OPS`

- **The record says:** design note §7 / PROJECT.md — extend `chip_test.py:636 _DESTRUCTIVE_OPS` with
  "new ops for the lock / inhibited-write / unlock steps", i.e. all four.
- **Measured truth:** `run_plan:784` — `if step.op in _DESTRUCTIVE_OPS and destructive_gate_closed:
  results.append(_skip_result(...))`. `destructive_gate_closed` is computed once from the `OP_ID` step
  and is constant for the rest of the loop. **If `sdp_unlock` is in `_DESTRUCTIVE_OPS`, a gate that
  closes after the lock has run SKIPS the unlock** — the protection gate becomes the mechanism that
  ships a locked part.
- **Evidence:** PITFALLS P-20 (HIGH, first-party read of `run_plan`); ARCHITECTURE §2.1 confirms the
  gate's all-or-nothing property but recommends all four in the frozenset — **PITFALLS wins on the
  safety asymmetry, and this is the one place the two disagree on a safety-bearing detail.**
- **Consequence for scope:** encode the asymmetry explicitly, with a comment and two tests: *gate
  closed from the start ⇒ `sdp_lock` SKIPPED and `sdp_unlock` not attempted (nothing was locked); lock
  ran, then the gate closed ⇒ `sdp_unlock` STILL attempted.* A cleanup unlock on a possibly-
  misidentified part is the lesser harm than a possibly-locked part, and if the lock never ran the
  unlock is a no-op emission.

### R-5 (HIGH) — The chip-ID destructive gate is structurally VACUOUS for all 43 SDP-capable chips

- **The record says:** `_DESTRUCTIVE_OPS` membership is the leg's chip-ID protection.
- **Measured truth:** **all 43 capability-ALLOWED `0x0D` chips have `chip-id == 0`** (measured live).
  `derive_plan` therefore always emits `Step(op=OP_ID, supported=False, reason="no chip-id in DB
  entry")`, and `_id_step_closes_gate`'s documented behaviour is that an **`NA` id step does not close
  the gate** (`chip_test.py:804-806`). The gate never closes for any chip the leg reaches.
- **Evidence:** FEATURES §2.6 (live measurement, HIGH).
- **Consequence for scope:** **requirements must not claim "the leg is chip-ID gated."** That is an
  overclaim of exactly the v1.22 C-5 class. The branch must still be specified and tested (correct
  behaviour if a chip-id is ever added; frozenset membership is correct defence-in-depth) but must be
  **labelled unreachable-today**. The leg's only real pre-flight protections are `sdp_capability()`
  and `_ALWAYS_WRITES_NOTICE` — which makes the recovery line and the baseline gate *more*
  load-bearing, not less.

### R-6 (MEDIUM, user-visible) — `dedup_fingerprint` continuity breaks for all 43 ALLOW chips

- **The record says:** design note §7 — every consumer that reads `StepResult.op` *"picks them up
  without learning a new field."*
- **Measured truth:** true of the *schema*, but `dedup_fingerprint` (`diagnostic_report.py:183`, hash
  input at `:224`) hashes `f"{op}={verdict}:{cls}"` **per step, in order**. Adding four steps
  **changes the fingerprint value for all 43 ALLOW chips.**
  `tools/parse_devtest_issue.py::count_agreeing` groups *saved* report bodies by the already-embedded
  fingerprint and never re-hashes, so every pre-v1.30 community report for an ALLOW chip lands in a
  different dedup group and **its N≥2 promotion count resets to zero.**
- **Evidence:** STACK §3d and FEATURES §1.3 (independent, both HIGH).
- **Consequence for scope:** arguably correct (a different test was run), and it is also a free win —
  an SDP-leg run can never dedup into a non-SDP run's group, so GRAD-01's no-auto-graduate lock holds
  through the fingerprint unchanged. But it is **a stated decision, not a discovery**, and it belongs
  in the release notes. `SCHEMA_VERSION` bumps `1.2 → 1.3`;
  `tests/test_parse_devtest_issue.py:102` asserts `== "1.2"` and must be updated; the frozen legacy
  `"1.1"` fixture stays untouched by design.

### R-7 (HIGH, pervasive) — The stale-anchor set: ~11 of 12 design-note anchors moved

All three code researchers independently re-measured the design note's line references. **This is the
authoritative corrected table. Any anchor not in it must be re-measured, not trusted.** Drift cause:
v1.23 inserted ~98 lines above the `cli_handlers.py` tail region (`py32f071` board plumbing,
`_BOARD_CHOICES`, the `fw` option block) — expect the same +98 offset on any other `cli_handlers.py`
anchor the record carries.

| Record claim | Live | Status |
|---|---|---|
| `dev_sdp` at `cli_handlers.py:2095-2227` | `@dev.command(name="sdp")` **2196**, `def dev_sdp` **2213**, body to **2321 = EOF**; span **2196-2321**, 126 lines, last function in the file | **STALE** |
| `dev_test(app, chip)` at `cli_handlers.py:1958` | `@dev.command(name="test")` **2055**, `def dev_test` **2059**; two params, zero options | **STALE** |
| `COMMAND_NAMES[cmd]` deref at `eprom_operations.py:301` and `:377` | **`:329`** (`_setup_operation`) and **`:405`** (`_operation_context`) | **STALE** — the `KeyError` risk is real, the coordinates are wrong |
| host-side auto-unlock at `eprom_operations.py:1637` | `1637` is a comment inside the D-15/HOST-06 block; live statements **`:1653`/`:1654`**. And it is the **audit** site, not the decision site — the host's auto-unlock *decision* is `cli_handlers.py:622-636` | **STALE + MIS-ATTRIBUTED** |
| `sdp_capability` at `sdp_capability.py:266` | FEATURES and ARCHITECTURE both read **266**; STACK reads `def sdp_capability` at **272** | **266 — 2 of 3 concur; re-verify at execution** |
| `--sdp-relock` deferral at `STATE.md:154` / `PROJECT.md:671` | note says so itself | **STALE** |
| `--sdp-relock` deferral at `STATE.md:532` / `PROJECT.md:705` (PROJECT.md's **own correction**) | live **`STATE.md:538`** / **`PROJECT.md:823`** | **ALSO STALE** — the correction is itself stale |
| `dev` group at `cli_handlers.py:960`, docstring `:965` | `def dev()` **1173**, docstring **1174-1177** | **STALE** |
| "eight `dev` subcommands" (gating note) | **nine** — `sdp` landed after the note; back to eight after v1.30 | **STALE** |
| `fw --pre` `:797` / `--stable` `:810` | **956** / **969** | **STALE** |
| `firmware.py:47` version regex | `FIRMWARE_VERSION_RE` **52** (47 is its comment) | **STALE** |
| "test suite ~1293" | **1303** collected | **STALE** |
| `eprom_operations.py:1736 sdp_unlock` · `:1784 sdp_lock` · `constants.py:72-73` + `COMMAND_NAMES` `:90-91` + `FLAG_SKIP_SDP_UNLOCK` `:121` · `chip_test.py:289-295` op vocabulary · `:636 _DESTRUCTIVE_OPS` · `diagnostic_report.py:183` · `channel.py` `BETA_ONLY_BOARDS` (33/34) | all as claimed | **VERIFIED** |

The stale `301`/`377` pair is **baked into three places in the shipped tree** and should be corrected
while the milestone is here (comment-only, zero behaviour): `firestarter/constants.py:69-70` (the
source comment that *is* the KeyError warning), and `tests/test_revision_constants_parity.py:71` and
`:526` (quoted in the gate's own rationale prose).

### R-8 (HIGH) — The mypy gate's root cause is regex-before-returncode, and `python_version = "3.9"` has NEVER taken effect

- **The record says:** PROJECT.md — the gate *"shells to a bare `mypy` from `PATH`; under Python 3.12
  the configured `python_version = "3.9"` is rejected and a numpy stub aborts the run."*
- **Measured truth, two distinct corrections:**
  1. **The bare-`PATH` invocation is a real but secondary defect.** The *load-bearing* bug is one line
     of ordering in `count_mypy_errors` (`tools/check_mypy_watermark.py`): the regex
     `re.search(r"Found (\d+) errors?", output)` is consulted **before** `result.returncode`, and mypy
     emits `Found N errors …` on the truncated path too. So a run that checked **1 of 120 files** and
     exited **2** is indistinguishable from a clean-ish tree. The documented `sys.exit(2)` arm is real
     and simply **unreachable on the failure that actually happens**. Reordering
     returncode-before-regex is *the* fix and flips the devcontainer GREEN → exit 2, measured.
  2. **`python_version = "3.9"` has never once taken effect, in CI either.** The `test` extra pins
     `mypy>=2.1.0` — the **original** pin, added `7acdcf3` on 2026-05-27 (Phase 37/v1.8), never
     raised. mypy **2.0** removed `--python-version 3.9` (mypy **1.20** was the last release
     supporting it), so the declared target has been dead for the whole life of the pin. In the
     *config file* the value is a **non-fatal note, silently discarded** (on the CLI it is a fatal
     argparse usage error) — moving it into the config converted a loud refusal into a silent no-op.
     Measured by revealed-type branch probe: mypy clamps to its **minimum supported target, 3.10** —
     *not* to the running interpreter. The watermark of 35 was set (Phase 71-07) against a checker
     already ignoring the declared target.
- **Evidence:** STACK §1b/§1e (reproduced with three purpose-built probe configs, HIGH; the mypy
  changelog fact cross-checked against the reproduced message, MEDIUM-verified); PITFALLS P-13
  (reproduced locally, exact output quoted); ARCHITECTURE §7.0 (independently reproduced).
- **Consequence for scope:** the fix is three changes in two files, not a rewrite: `python_version =
  "3.10"` (**zero error-count change** — 3.10 is already what mypy has been using, so it can neither
  mask nor manufacture an error), returncode-before-regex + require the `(checked N source files)`
  completion clause + a `MIN_CHECKED_SOURCE_FILES` coverage floor (commit the measured **120**), and
  `[sys.executable, "-m", "mypy", …]`. **Do NOT switch to `mypy --output json`** — measured: JSON mode
  emits no summary line at all, discarding the very `checked N` signal the fix depends on. Also record
  the honest cost: after the target moves, **nothing type-checks against the py3.9 floor the package
  still advertises**; `[tool.ruff] target-version = "py39"` becomes the only remaining py39
  enforcement (syntax/idiom only, not stdlib APIs). And note the treadmill: **Python 3.10 EOLs
  2026-10-31**, ~3 months out — a future mypy clamping to ≥3.11 re-fires this exact failure, and the
  hardened gate is what makes that arrive as a red gate instead of a silent green.

### R-9 (HIGH) — Deleting `tests/test_dev_sdp_cmd.py` turns a FAIL-CLOSED gate RED

- **The record says:** design note §7 — delete `firestarter_app/tests/test_dev_sdp_cmd.py`.
- **Measured truth:** `tools/check_no_exists_proxy.py:156` names `"tests/test_dev_sdp_cmd.py"` in its
  literal, deliberately non-glob `_DEFAULT_TARGETS` enumeration, and the gate **exits 1 when any
  listed target is missing** (~`:328-332`, *"…vacuously pass with a target silently skipped"*).
  `git rm` that file and the gate goes RED unless the list moves in the **same commit**.
- **Evidence:** FEATURES §5.3, ARCHITECTURE §1.1, both first-party HIGH. Identical shape to the
  recorded `git rm REQUIREMENTS.md` trap at milestone close.
- **Consequence for scope:** a named requirement, not a discovery during execution. It compounds with
  **P-16**: the file carries **four honesty assertions that exist nowhere else** — the both-directions
  unreadable-state caveat (`:395`, whose docstring records that the host summary line is the **only**
  carrier of the caveat on the unlock direction, because firmware's `0x5F` frame lacks it), the
  no-fabricated-duration test (`:423`), the three positive-framing no-fabricated-lock-state assertions
  (`:453`), and the old-firmware `MSG_ERR_UNKNOWN_CMD` reporting test (`:513`). **`git mv`, not
  `git rm`**, retargeting each onto the new leg, with a grep-based acceptance criterion that all four
  assertion strings remain findable in `tests/`. `dev_sdp` is also the sole in-tree consumer of the
  `MSG_ERR_UNKNOWN_CMD` → `FirmwareOutdatedError` D-14 mapping (`:2283-2306`) and of the D-10 honesty
  wording (`:2313-2318`) — both must **move to the `write --sdp-relock` path**, not be dropped
  (`ruff check` select `F` flags them as unused if merely orphaned).

## Adjudicated Conflicts

Where two researchers disagree, one wins. The evidence tier that decided it is named.

### A-1 — Is `firestarter_app`'s primary `ci` job genuinely RED, or only vacuously green locally?

- **STACK:** genuinely RED. Confirmed via `gh run view 30708836339` (Host CI, `workflow_dispatch`,
  2026-08-01): every step before it green, `X mypy type check (watermark gate)` — *"Process completed
  with exit code 1"* — and **`pytest` and the entry-point smoke test never ran.** Adds that `ci.yml`'s
  `push` trigger is `branches: [main]` only, so pushes to `beta` fire `beta-release.yml` and never
  `ci.yml` — the gate is red on PRs and manual dispatch and invisible otherwise, which is why a RED
  primary gate went unnoticed for two months.
- **ARCHITECTURE:** rates it MEDIUM and calls for one `workflow_dispatch` to settle, on the grounds
  that the *local* tree is vacuously **green** (measured: ruff clean, `ruff format --check` clean, full
  pytest suite green with 30 snapshots, `check_mypy_watermark.py` exit 0 reporting "1 errors — 34 below
  watermark").
- **VERDICT — both are true and they are not the same claim. STACK wins on the CI fact**, on the
  strongest available tier: a real CI run log, not an inference. ARCHITECTURE's measurement is correct
  about the *devcontainer*, where an ambient numpy truncates the run to 1 error and the gate reports
  green. This is the **third recorded instance of this devcontainer masking a CI-only defect**, so the
  two observations are the expected pair, not a contradiction.
- **Pre-planning action (explicit, do this before the roadmap commits to a watermark number):**

  ```
  gh workflow run ci.yml --repo henols/firestarter_app --ref beta
  gh run list --workflow=ci.yml --limit 1     # then: gh run view <id> --log-failed
  ```

  Purpose is not to re-establish that it is red — run 30708836339 already did — but to obtain a
  **current** post-fork number on the exact fork base, since the count is the thing the watermark is
  set from. Same discipline as v1.23 Phase 128's two real dispatches.

### A-2 — The true mypy error count and the path to green

- **STACK:** **69** at py3.11 in a numpy-free venv reproducing `ci.yml`'s `.[test]` closure exactly;
  watermark 35 ⇒ gap +34; and a *measured* path to **33**: delete `tests/test_dev_sdp_cmd.py` (−6, free,
  scope item 1) → 63; one `make_app_context` factory fix (`tests/test_dev_test_cmd.py:84`, `overrides:
  object` forwarded into a typed dataclass) retires the remaining 24 of a 30-error single pattern → 39;
  six `[var-annotated]` annotations (`database.py:174,175,325`, `ic_layout.py`) → **33 ≤ 35, GREEN.**
- **ARCHITECTURE:** **69** at py3.12 (`mypy --python-version 3.12 firestarter/ tests/` — v1.23's number
  reproduced exactly), of which 6 live in the file item 1 deletes → "delete first, then harden at 63".
- **VERDICT — compatible arithmetic told two ways; no conflict of fact.** Reconciled:
  **69 is the honest count today** and it is environment-independent in the ways that matter — STACK
  measured it at a **3.11** interpreter in a numpy-free CI-replica venv (mypy's *effective target* being
  3.10 by the clamp, per R-8), ARCHITECTURE measured it at **3.12** with an explicit
  `--python-version 3.12`, and they agree on the number and on the 17-file/120-checked shape. STACK
  additionally ruled out a tooling artefact: re-running with `--no-local-partial-types
  --no-strict-bytes` also yields exactly 69, so **none** of the drift 35 → 69 is a mypy-2.x default
  change; it is all accreted code. Split: 25 in `firestarter/`, 44 in `tests/`.
- **Ordering consequence (the load-bearing half):** **63, not 69, is the number any phase should
  target**, and the watermark must be re-baselined *after* the deletion or it will be wrong within the
  same milestone. Critically, the 30-error `AppContext(..., <object>, ...)` mock-typing pattern spans
  `test_dev_test_cmd.py` (9), `test_write_skip_sdp_unlock.py` (7), `test_write_skip_erase_0x0d.py` (6),
  `test_validate_family_cmd.py` (6), `test_dev_sdp_cmd.py` (6) — so **new test modules for the leg, the
  relock and the channel split, written in the same idiom, will add errors of exactly that class.** A
  **typed `AppContext` fixture must exist in `tests/conftest.py` before those modules are authored**,
  or the honest gate reddens on brand-new work. And the good news for the roadmap: **the primary `ci`
  job can be made GREEN at the existing watermark of 35 without touching the ring-fenced
  `eprom_operations.py` `[union-attr]` cluster at all** (10 errors at `:467,471,514,526,564,590,593,620,638,1655`,
  one `Optional` connection attribute never narrowed). That cluster becomes optional extra credit —
  the difference between a scoped phase and an open-ended one.

### A-3 — Pattern B's construction

- **FEATURES:** pattern B = **bitwise complement of A**. Measured: complement of A`[:8]` =
  `ff fe fd fc fb fa f9 f8`, differing from A in **every** byte, so a change at any offset is
  detectable. Explicitly rejects `prepass_images`' all-`0xFF`, which would coincide with A wherever
  `address_fold_byte == 0xFF`, creating blind offsets in the oracle. ARCHITECTURE §2.4 independently
  arrives at the same construction (`sdp_probe_pattern(start, length)` = `bytes(b ^ 0xFF for b in
  generate_pattern(start, length))`) and adds that it is neither all-`0x00` nor all-`0xFF`, so a blank
  read and a stuck-bus read stay distinguishable from a successful inhibited write.
- **PITFALLS (P-05):** prove a **transition, not a state.** Because `generate_pattern` is
  deterministic, the *second* `dev test` run on the same chip finds A already on the die — so a chip
  whose write path is dead but which carries A from a previous run passes step 1, passes step 3, and
  passes step 4. **A completely dead write path produces a perfect SDP leg result, with no bug, just by
  running `dev test` twice.**
- **VERDICT — these are not competing answers to one question; they answer two different questions,
  and BOTH are required.** ONE recommendation:

  1. **B is the bitwise complement of A**, from its own named generator (`sdp_probe_pattern`), never
     from `generate_pattern`. Committed test: `len(a) == len(b) == region_length`; `all(x != y for
     x, y in zip(a, b))` — differ **everywhere**, not somewhere; neither equals `bytes(n)` nor
     `b"\xff" * n`. Plus a lint-style test asserting the inhibited-write step's payload is **not**
     `generate_pattern(...)`'s output for the plan's region.
  2. **The baseline step proves a transition:** write **B**, verify B, then write **A**, verify A —
     two proven transitions in opposite directions before any lock is applied. On a `0x0D` EEPROM both
     bit directions are writable, so this is physically sound. Cost: one extra write pass on a bounded
     region. Benefit: it is the **only** evidence that the write path is live, which is the entire
     premise of step 3's inference. Record the pre-write read hash in the JSON artifact so a community
     report carries the evidence even when the leg passes.
  3. A committed fixture whose "chip" starts holding pattern A and whose write is a **no-op** must make
     the baseline step report **BAD**. Without that fixture the P-05 defect is unobservable in a suite
     whose mocks always start blank.

  Rejected: a nonce or timestamp for B (non-reproducible report, breaks the `dedup_fingerprint` hash).

### A-4 — Is a new "inconclusive" status needed?

- **FEATURES:** **NO.** `marginal` already means exactly that, wired end to end: exit **2**
  (`cli_handlers.py:1862-1868`), `build_db_diff` disposition *"inconclusive — needs N≥2 agreement"*
  (`diagnostic_report.py:290-301`), **no** ladder tag, and it **counts as "ran"** (`_RAN_VERDICTS`
  includes `MARGINAL`, `chip_test.py:1209`). A sixth status is an **anti-feature** and a false-green
  path: `_verdict_code` is `_VERDICT_EXIT_CODES.get(verdict, 0)` (`:1876`), so an **unrecognised verdict
  string exits 0**, and it would miss every arm of `build_db_diff`, landing in the final `else` → *no
  change suggested* / no ladder tag, silently discarding the finding.
- **PITFALLS (P-04):** raises an adjacent-but-different concern — `SKIPPED` and `NA` both map to exit 0
  by six enumerated routes (R1 chip-ID gate, R2 any id uncertainty, R3 `resolve_chip` refusal, R4
  `step.supported is False`, R5 `write_scope="none"` structural omission, R6 empty `results`), plus R7:
  `count_applicable` computes `M = sum(1 for s in plan.steps if s.supported) + len(plan.locked_destructive)`,
  so an `NA` SDP step is excluded from **M as well as N** and the headline `N of M` coverage ratio
  **stays perfect while the oracle never ran.**
- **VERDICT — FEATURES is CONFIRMED on the status question; PITFALLS' concern is real but is not a
  status question.** Keep the five statuses. Use `marginal` for genuine inconclusiveness (its
  documented scope, *"destructive/verify-only, never forced onto read-step disagreement"*, is in-family
  for an inhibited-write step). Address P-04 with **two mechanisms that are not a new verdict**:
  1. A **named, always-present `DiagnosticReport` field** rendered on every ALLOW-chip run as one of
     `HELD / NOT-HELD / NOT-RUN(reason)` — so `NOT-RUN` is visible in the JSON artifact and the filed
     issue even at exit 0. This also makes P-02's failure recoverable after the fact, which it is not
     otherwise.
  2. **Extend `count_applicable`'s `M` to include the SDP oracle for ALLOW chips regardless of
     outcome**, so an `NA`/`SKIPPED` oracle *drops* the N/M ratio and fires the banner. Pin with a test.
  Whether an ALLOW-chip `SKIPPED` oracle should additionally map to exit **2** is an **operator
  decision** — it changes `dev test`'s published exit-code contract (`cli_handlers.py:2091`). See
  Operator Decisions.

## ⚠ Evidence Ceiling — preserved verbatim, restate in REQUIREMENTS before planning

> **Provable this milestone:** the *emission* (correct sequence, pinout remap, `/WE` asserted) via the
> Phase 116 trace harness; the *plan derivation* (43 ALLOW get four steps, 41 REFUSE get four NA steps
> carrying reasons — measurable today with zero hardware); the *read-back comparison logic* and every
> branch of the outcome matrix in the native envs with a stubbed operator.
>
> **NOT provable this milestone:** the causal claim *"the lock inhibited the write."* Reachable only on
> silicon, i.e. only from a community `dev test` report, which **by design does not gate the close.**
>
> **Additionally not provable, and newly discovered:** there is no identity gate behind the leg for any
> chip that reaches it, so *"the leg is chip-ID gated"* must not appear in any requirement.
>
> Writing requirements that conflate the first bullet with the second reproduces v1.22's C-5 overclaim.

**Two research findings NARROW what "emission" proof can mean, and must not be smoothed over:**

1. **The firmware-side trace harness is UNREACHABLE from the host.**
   `firestarter/test/native/avr/test_sdp_harness/` (Phase 116 Plan 05) and
   `test_eeprom28c_sdp/` (Plan 06) are PlatformIO `[env:native]` Unity/C++ binaries **in the firmware
   repo**, one statically linked executable per directory, run by `pio test -e native`. The host `ci`
   job installs Python deps only — no `pio`, no C++ toolchain — and **`firestarter` is declared
   untouched this milestone.** Consequence: the harness can be **cited** as the source of the emission
   proof (it shipped that proof in v1.22) but it **cannot be run as part of this milestone's evidence**,
   and it is out of scope as an executable gate for v1.30.
2. **A locked die is unrepresentable in either repo's stubs.** Firmware side: the recorder hooks
   `rurp_write_data_buffer` + `rurp_set_control_pin` and records an ordered *bus stream* — it models the
   **bus**, never the **die**; there is no state machine anywhere in it that would begin refusing writes
   after observing the lock sequence. Representing a locked part means authoring a new **stateful 28C
   die model**, i.e. new firmware test code, out of scope. Host side: there is no bus stub at all —
   `tests/test_dev_test_cmd.py` builds its world from `Mock(spec=EpromOperator)` (`make_app_context`
   `:84`, `make_clean_operator` `:110`), where a "locked part" is a **scripted return-value sequence**:
   trivially representable and trivially worthless as silicon evidence.

**State this split in the phase's own words, or the milestone closes claiming a proof it does not
hold.** What the host *can* honestly carry is the fake-serial seam, not the operator mock:
`tests/conftest.py` ships `build_frame(msg_id, params)` (`:96`), an independent `_ref_crc8_ccitt`
(`:80`), `class _FakeSerial` (`:109`), the `fake_serial` fixture (`:165`) and `make_comm` (`:172`) — a
real `SerialCommunicator` over a scripted wire. `tests/test_dev_sdp_cmd.py` **already** imports
`build_frame` for what its own docstring calls *"the one dedicated real-operator leg"*, so the
precedent for driving a genuine `EpromOperator` over a scripted wire exists **inside the very file
being deleted**. The design note's "repurpose the gate-ordering cases" should be read to include *this*
mechanism, which is the more valuable half.

## Key Findings

### Recommended Stack

**Nothing is added.** The runtime closure stays at six packages (`pyserial>=3.5`, `requests>=2.20`,
`tqdm>=4.60`, `click>=8.1`, `rich>=14.0`, `packaging>=21.0`) plus the optional `[py32] pyusb>=1.3.1,<2`;
the `test` extra stays at pytest 9.x · syrupy 5.x · ruff · mypy · pytest-cov · types-pyserial. A CLI that
ships to PyPI pays for a new dependency on every user's install, forever — and every one of the six
scope items is host-side logic, Click wiring, or test code. The complete version decision set is: move
`[tool.mypy] python_version` `"3.9"` → `"3.10"` (zero error-count change, measured); keep the watermark
at 35 and re-baseline **downward** after the deletion; keep `requires-python = ">=3.9"` in v1.30 and
backlog the 3.9 drop (3.9 EOL'd 2025-10-31, but breaking published metadata is its own decision);
everything else unchanged.

**Core tooling, and what each carries for this milestone:**

- **pytest 9.1.1 + `unittest.mock` + `_FakeSerial`/`build_frame`** — covers all four of the leg's
  assertions (plan derivation, the read-back oracle end to end through the frame codec, Trap-2
  sensitivity, Trap-1 partial change). No property-based framework, no fake-hardware DSL.
- **syrupy 5.5.3** (already used by six modules) — the natural home for the new report rows and the
  Trap-3 recoverability line. ⚠ It **fails the whole pytest session on UNUSED snapshots** unless
  `--snapshot-warn-unused` is passed, and `addopts` is only `"-ra -q"` — see Pitfall 5.
- **ruff 0.15.14+ with `target-version = "py39"`** — becomes **load-bearing** once mypy targets 3.10: it
  is then the only remaining py39 floor enforcement (syntax/idiom, via `UP`), and it cannot catch a
  py3.10+ *stdlib API* used on 3.9. That residual gap is real, is not new (it has existed since
  2026-05-27), and its correct closure is a py3.9 CI matrix leg or dropping 3.9 — not the mypy config.
- **`firestarter/channel.py`** (81 lines) — the channel gate already exists, **fails closed** on an
  unparseable version, and its docstring forbids an env seam in the project's own words. Reuse it;
  add `STABLE_DEV_COMMANDS` beside `BETA_ONLY_BOARDS`. Do not invent an env-var gate.
- **Six committed `tools/check_*.py` gates with paired fail-provable pytests** — `check_devtest_orchestrator`,
  `check_no_exists_proxy`, `check_sdp_capability_invariants`, `check_no_community_support_status_write`,
  `check_no_log_in_sdp_window`, `check_dispatch`. **`check_mypy_watermark.py` is the one with no paired
  test** — it is also the one that was fail-open for two months. It earns the project's own anti-hollow
  contract.

**Explicitly do NOT add:** any runtime dependency · a new test framework · `hidden=True` as a gating
mechanism (documented `--help` cosmetic; the HOST-02 bug class) · any env-var override in `channel.py` ·
`mypy --output json` as the gate's input · a dedicated venv or a second mypy pin for the gate · pinning
mypy back to `<2` · **any option on `dev test`** (zero options since Phase 121 D-05) · a new `StepResult`
field (`StepResult.op` is the extension axis) · raising the watermark to 69.

### Expected Features

**Must have (table stakes):**

- **Delete `dev sdp`** — a command whose own success line admits it proves nothing is surface debt, and
  999.15 removes it from stable anyway. Clean tail truncation (`cli_handlers.py:2193-2318`, the last
  function in the file). **LOW–MEDIUM.** Depends on: auto-unlock staying default-on (record it),
  `sdp_capability.py` surviving in full, the `COMMAND_NAMES` entries surviving (`KeyError` at
  `:329`/`:405` otherwise), and `check_no_exists_proxy.py:156` moving in the same commit (R-9).
- **`write --sdp-relock`** — the only legitimate need `dev sdp` served (an AT28C destined for a live
  machine); gh#12 asked for it; minipro's `-P` is the class norm. **MEDIUM**, plus the new verify pass
  (R-3). Must ship **with** the deletion: landing the deletion alone removes the only legitimate
  capability the command served, in a released pre-release.
- **The recoverability report line** — an aborted run ships a locked chip to a stranger, and R-5 shows
  there is no identity gate behind it. **LOW** (wording only, no new report field). Must say **"rewrite"**,
  never "erase" — protocol `0x0D` has **no erase operation at all**, so "erase" is not imprecise, it is
  actively unfollowable advice. Prints on both paths: the loud form when the run did not confirm the part
  was unlocked again, a **neutral** one-line confirmation on the happy path (silence is not a statement;
  an unconditional *warning* trains dismissal).
- **mypy gate-hardening → primary `ci` GREEN** — a fail-open gate is worse than no gate. **MEDIUM–HIGH**,
  fully independent of every SDP item.
- **gh#12 outward follow-up** — a published instruction (2026-07-30) stranded one day later. **LOW** +
  operator wording review.

**Should have (differentiators):**

- **The plan-derived SDP leg in `dev test`** — the **only oracle in existence** for this feature. No
  comparable programmer offers *any* verification of protection state. **HIGH complexity**; it is the
  milestone's reason to exist.
- **Verify-gated relock** — stricter than minipro's unconditional `-P`; never locks a known-bad image
  behind an unreadable state clearable only by another write.
- **Evidence returns to the repo** — the leg files through `submit_report` (already built), so a
  stranger's silicon result reaches the maintainer instead of dying in their terminal.
- **999.15 / gh#8 channel gating** — stable users get a surface that cannot hurt them; beta keeps the
  sharp tools. **MEDIUM.**

**Recommended op vocabulary** (kebab-case, matching `blank-check`/`write-partial`), appended at
`chip_test.py:295` — four new strings, all in `_DESTRUCTIVE_OPS` **except** `sdp-unlock` per R-4, none in
`_MULTI_RUN_OPS`, all in a **new `_SDP_OPS`** single-run dispatch allow-list checked **before** the
`_MULTI_RUN_OPS` branch: `sdp-baseline` (transition-proving write, A-3) · `sdp-lock` (CMD 10, emission
only) · `sdp-inhibited-write` (**the oracle**) · `sdp-unlock` (CMD 9 + write + verify, the must-run
cleanup). `SCHEMA_VERSION` `1.2 → 1.3`.

**Anti-features, explicitly do not build:** any option on `dev test` · a sixth verdict/status (A-4) ·
downgrading an unexpected write success to `SKIPPED`/`NA` · using `write_eprom()`'s bool as the oracle ·
reporting a partial change as `OK` · a "is it locked?" query or a `lock_state: bool` in the report
(physically impossible on `0x0D`; already forbidden by a committed test) · making `--sdp-relock` and
`--skip-sdp-unlock` mutually exclusive (they act at opposite ends of one write and their combination is
coherent) · a confirmation prompt or `-y` on `--sdp-relock` (`write` has no prompts, scripts depend on
that, and the optional flag **is** consent) · wording recovery as "erase" · a permanent transitional
`dev sdp` stub (stays registered for 999.15 to classify, no removal date, `--help`-invisible anyway) ·
re-adding the capability as `dev sdp-lock`/`dev sdp-unlock` · raising the watermark to 69.

**External corroboration (LOW tier, upstream fetched directly):** minipro exposes protection control
**only** as flags on the write operation (`-u/--unprotect`, `-P/--protect`) — **no standalone
protect/unprotect subcommand exists**, and **no read-back/status query exists either**, consistent with
the AT28C datasheets documenting a 3-byte enable/disable sequence and **no status bit**. That is
independent support for retiring `dev sdp` and re-homing the lock on `write`. minipro's `-P` is *not*
verify-gated, so Firestarter's verify-gated skip is stricter than the reference implementation.

### Architecture Approach

The change is entirely within the existing four-layer host shape and — deliberately — **`eprom_operations.py`
is not modified at all.** That is a checkable property, not a preference: `sdp_lock`/`sdp_unlock`/
`write_eprom`/`verify_eprom` already accept everything both survivors need, and the one thing that would
have forced a change (`sdp_capability` needing the chip **name** and `db`, where `resolve_chip`'s
programmer dict carries neither) is answered by keeping the relock decision **in the CLI handler**, per
that file's own recorded reasoning at `cli_handlers.py:610-612`. `sdp_capability_for_entry` *raises
`KeyError` with a diagnostic message* if handed a programmer dict, so the placement is structural.

**Major components:**

1. **`cli_handlers.py`** — CLI surface. Deletes `2196-2321`; extends `_ALWAYS_WRITES_NOTICE`
   (`2045-2052`) with the Trap-3 sentence; adds `--sdp-relock` + its refusal matrix + the new verify pass
   + the exit-code rework + the relocated D-14 mapping in the `write` handler (`529-691`, insertion
   between `:690` and `:691`); adds `cls=_DevGroup` to `@cli.group(name="dev")` (`:1171`).
2. **`chip_test.py`** — orchestration/pure compute, and **scanned in FULL** by
   `check_devtest_orchestrator.py`. Owns the leg: 4 ops, `Step.group`/`role`, `_SDP_OPS`,
   `_SDP_REGION` + `sdp_probe_pattern`, `derive_plan` capability derivation, a `run_plan` cleanup
   registry drained by `try/finally`, and a widened `_run_step` except set. **Put the leg's logic here,
   not in the handler** — the handler is scanned only through a hardcoded 9-name allow-list (Pitfall 4).
3. **`diagnostic_report.py`** — `SCHEMA_VERSION` 1.2→1.3, the new rows, the recoverability line, and the
   `HELD/NOT-HELD/NOT-RUN` field from A-4. `dedup_fingerprint` needs **no** change (it hashes
   `result.op`), but see R-6 for the consequence.
4. **`channel.py` + a `_DevGroup(click.Group)` subclass** — `STABLE_DEV_COMMANDS = {"read", "test"}` and
   `is_dev_command_available(name)` as pure policy; the mechanism overrides `list_commands` (so
   `dev --help` hides) and `get_command` (informative refusal on a stable build). **Zero change to any of
   the nine `@dev.command` decorators.** Recommended over an import-time `del dev.commands[name]` because
   group *lookup* has later hooks where `click.Choice` (the board gate) has none — so the `dev` gate can
   be invocation-time and in-process testable, where the board gate needs a subprocess per version.

**Two structural holes the design note does not mention, both of which the leg needs closed:**

- **`_run_step`'s except set is too narrow, and the missing classes are the likely ones.** It catches
  `EpromOperationError` and `(ChipNotImplementedError, ChipNotFoundError)`. It does **not** catch
  `SerialError` (`exceptions.py:13`) or its subclasses `SerialTimeoutError`, `ProgrammerNotFoundError`,
  `FirmwareOutdatedError`, nor `HardwareOperationError` — all siblings of `EpromOperationError`, not
  descendants, raised at twelve sites in `serial_comm.py` including the read-timeout path. Today such an
  exception propagates out of `run_plan`, out of `dev_test`, into `map_typed_errors` and becomes a
  `ClickException` — so `report.results` is never assigned, no JSON/MD artifact is written,
  `submit_report` never runs, and **a locked chip goes back in the envelope with no report line telling
  anyone.** A cable that half-seats mid-leg is the single most likely field failure and it currently
  takes out the entire report. Fix: add a **named** `(SerialError, HardwareOperationError)` arm →
  `VERDICT_BAD`. Never a bare `except Exception` (it would swallow the deliberate `AssertionError` at
  `:1130-1132` whose whole purpose is to be loud); never `BaseException` (Ctrl-C must stay Ctrl-C). This
  is ~3 lines and the single highest-value safety change in the milestone — but it **is** a behaviour
  change for every `dev test` run and needs its own recorded decision and test.
- **There is no cleanup path of any kind.** `chip_test.py` has exactly two `finally:` blocks (`:1106`,
  `:1161`), both scoped to unlinking a temp file; **no** `try/finally` around `run_plan`'s loop, **no**
  `atexit`, **no** `KeyboardInterrupt` handling anywhere in `chip_test.py`, `cli_handlers.py` or
  `main.py`. Fix: a `pending_cleanup: dict[str, Step]` registry armed by `role == "lock"`, disarmed by
  `role == "cleanup"`, drained in a `finally` — which runs on `KeyboardInterrupt` and `SystemExit` too,
  swallows nothing, and needs no re-raise. `atexit` was considered and rejected (runs at interpreter
  teardown with the operator possibly already garbage; fires on the success path; untestable without
  process isolation).

What the model already gives the leg **for free**: strict step ordering (`Plan.steps` is an ordered list
and nothing reorders it), continuation after a BAD step, and cross-step state derived from a prior
step's verdict — `destructive_gate_closed` is a plain local `bool` in `run_plan`, and it is **the
precedent to copy** for "did the lock emit OK?". **Nothing flows between steps for the patterns**: step 3
re-derives from `step.write_region`, which `derive_plan` stamps once. Rejected: a nested `Plan` (four
consumers all take a flat list), a `must_run` bool without `group`, a single composite step (kills the
report's ability to show *which* of baseline/lock/oracle/restore failed), and a payload-carrying
`StepResult.data` field (the report body is a **public GitHub issue body**, and a new field is a live
risk of leaking into the deliberately volatile-field-free dedup id).

**Region recommendation:** give the leg its own `_SDP_REGION = (256, 256)` stamped on all four steps,
rather than sharing the existing `(0, 256)` window. Every `0x0D` part is ≥2 KiB (smallest is `2816`), so
it always fits. Reason: on the shared window a sceptical reader cannot tell whether step 3's read-back
matched because the leg's baseline wrote A or because the *earlier* `OP_WRITE` step did. Width stays a
module constant, never a DB field (the SC4 rule).

### Critical Pitfalls

PITFALLS enumerates 25 (P-01…P-25). The five that decide whether the milestone delivers anything:

1. **The vacuous oracle (P-01) + the empty-read-back equality (P-02)** — carried as **R-1** and **R-2**.
   Avoid by: a second named generator for B, a "differ at every byte" test, a lint test forbidding
   `generate_pattern` as B's source, a length gate before every comparison, and four degenerate-input
   fixtures each asserting BAD. *The oracle is the milestone's only deliverable; a hollow one is not a
   quality gap, it is the milestone failing.*
2. **`_MULTI_RUN_OPS` is a trap that the fail-closed instruction leads you into (P-03).** The module's
   own comment says *"any future op added to the vocabulary MUST be added to both frozensets or it fails
   closed by construction"* — and registering the inhibited write in `_MULTI_RUN_OPS` routes it into
   `_dispatch_multi_run`, which (a) sets `verdict = VERDICT_OK if outcomes and outcomes[0] else BAD`,
   i.e. **the write's boolean IS the verdict**; (b) runs it **twice** (`runs: int = 2`, and `runs < 2` is
   *rejected*), so a partially-leaky lock's read-back state depends on how many passes ran; and (c)
   swallows a failed read-back to `actual = b""` leaving the boolean verdict standing with no fingerprint
   and nothing in the report saying the oracle did not run. Avoid by: a dedicated `_SDP_OPS` dispatch arm
   **above** the `_MULTI_RUN_OPS` branch, `runs == 1` enforced structurally (the new arm takes no `runs`),
   a test asserting the op is **not** in `_MULTI_RUN_OPS` with a comment pointing at this pitfall, and a
   **both-directions** deliberate-break test: `write_eprom → True` + read-back == **B** ⇒ **BAD**;
   `write_eprom → False` + read-back == **A** ⇒ **OK**. Without both directions the test passes on a
   boolean-driven implementation.
3. **Inverted sensitivity — eight named routes by which an unexpected SUCCESS gets downgraded (P-09).**
   *"The write succeeded, so the lock must not be supported — mark NA"* is the finding being deleted.
   Avoid by: an explicit four-arm truth table with **no default arm** (== A ⇒ OK; == B ⇒ BAD *"the lock
   did not inhibit the write"*; something else ⇒ BAD partial change; length/blank bad ⇒ BAD inconclusive),
   a final `raise AssertionError` for anything unclassified, a **polarity-pin** test asserting the BAD
   arm's reason contains the causal statement and the OK arm's does not (so a diff that inverts the
   comparison turns **two** tests red), and a grep-style gate forbidding `VERDICT_NA`/`VERDICT_SKIPPED`/
   `VERDICT_MARGINAL` inside the oracle function. **The "write succeeded ⇒ BAD + exit 1" test is the
   single most important test in the milestone and must be a named, listed acceptance criterion.**
4. **`check_devtest_orchestrator.py` silently does not scan the leg's new helper (P-07).**
   `_HANDLER_FUNCTION_NAMES` (`:138-150`) hardcodes 9 names and `_scan_target_functions` fails closed
   **only when NONE match** — a partial match scans successfully and **silently omits** a new
   `_sdp_leg_*` helper. Its fail-closed guarantee is documented about *renames and removals*, not
   *additions*, and RESEARCH C-4 proved the fail-open empirically. Avoid by: keeping the logic in
   `chip_test.py` (scanned in full), a test that derives the required set from the AST (every
   module-level `_`-prefixed function referenced from `dev_test`'s body must be a subset of the
   frozenset), and re-running the checker with a planted violation inside a **new** helper name as a
   phase acceptance criterion.
5. **The claim gate: neither existing `check_permitted_claims.py` copy is safe to copy verbatim, and the
   v1.23 copy is the more dangerous (P-11).** Its `_PHASE_130_DIR` is `_HERE/../130-close-honesty-ledger-…`
   by string literal; `_HERE` becomes the *new* phase dir, `os.pardir` is still `.planning/phases/`, and
   **`130-…/` still exists on disk with all four artifacts**. So a copied checker resolves four real
   files, finds all four carry `"no PY32F071 hardware exists"`, finds zero py32-proximate forbidden
   phrases, and prints a confident **`PASS:` naming four real files on a milestone whose artifacts it has
   never opened.** That is strictly worse than the C-2 defect it was built to fix (C-2 at least printed
   `UNARMED:`). Avoid by: **fork the VOCABULARY from the v1.22 copy** (its eight AT28C/SDP/silicon
   patterns; `REQUIRED_CAVEAT_PROSE = "no AT28C silicon was tested"` is already the milestone's ceiling
   sentence) and the **MECHANICS from the v1.23 copy** (D-16 ±1-line proximity window on
   `at28c|sdp|0x0d`, D-15 all-or-nothing arming, hoisted never-vacuous guard); add this milestone's own
   forbidden claims (`lock inhibited the write`, unqualified `the lock held`, `proven behaviour`,
   `behaviourally/behaviorally verified`, `now proven`, `self-verifying` without "emission" or the caveat
   in the window, unqualified `dev test proves`); **suffix the env seam**
   (`FIRESTARTER_CLAIMSCAN_TARGETS_V130` — it would otherwise be shared by three checkers) and **rename
   the test module** (`test_check_permitted_claims_v130.py` — three same-named files in three non-package
   dirs is an "import file mismatch" collection error for anyone running pytest from `/workspaces`); and
   add **two new test legs**: `test_default_targets_resolve_inside_this_phase_directory` and
   `test_default_target_basenames_are_this_milestones`. Because the **meta repo runs no pytest workflow
   at all**, the checker's own suite must be run as an explicit recorded acceptance criterion — v1.23's
   C-3 found this checker's suite *already RED* (1 failed, 9 passed) with nothing able to notice.

**Also load-bearing, at MEDIUM–HIGH:** the baseline is non-discriminating because the pattern is
idempotent (**P-05**, carried in A-3) · the lock step's OK is an *emission* claim that will be read as a
*state* claim in a column headed **Verdict** (**P-06** — non-empty emission-only `reason` on success,
rendered, asserted by **positive framing** not a forbidden-word list, and **no boolean named `locked`
anywhere in `to_dict()`**) · `_ALWAYS_WRITES_NOTICE` currently promises "TWICE per invocation" and its
committed test asserts only that it is *first* and *unconditional*, **not what it says** (**P-08** — the
notice can silently become false while its test stays green, and it is the first thing a community
member reads before consenting to sacrifice a chip) · **syrupy fails the whole session on UNUSED
snapshots** (**P-15**: `.ambr:141` carries the `sdp` help line; the 999.15 split *requires* renaming
`test_help_dev` into two named entries, which orphans the old one; and a broad `--snapshot-update`
regenerates every snapshot in the selection, silently blessing unrelated drift — so scope the update, and
make *"the only changes are X and Y"* an explicit diff-shape acceptance criterion) · the devcontainer
cannot see three whole classes of defect this milestone can ship (**P-18**: py3.12 local vs 3.11 CI vs a
3.9 floor; the **sibling-repo layout** standalone CI lacks — three CI-only failures fired simultaneously
on the real b15 push; and a live board on `/dev/ttyACM*` beating a `comports=[]` patch) · the stable
channel surface is **unreachable in any local run** (**P-19**: `is_prerelease_build()` returns True for
`3.0.0b15` and for a `_dev` checkout, so an in-process stable-behaviour test passes **vacuously**;
simulate the channel in a **subprocess**, and assert positive **and** negative membership on
`dev.commands`, never an exit code) · and "removal is safe because auto-unlock is default-on" decaying
into an unfindable sentence (**P-21**: put the tripwire where the change will happen — a comment at
`eprom_operations.py`'s auto-unlock site and at `FLAG_SKIP_SDP_UNLOCK`'s definition, plus a test *named
for the dependency* whose failure message explains the coupled decision; a sentence in a note is not a
mechanism).

## Implications for Roadmap

Three orderings were proposed. **PITFALLS:** 131 gate-hardening · 132 retire + re-home · 133 the leg ·
134 relock · 135 channel · 136 close, with "131 before everything" and "the leg before or with the
deletion". **ARCHITECTURE:** A delete → B mypy → C leg ∥ D relock → E channel → F outward, arguing mypy
belongs at B because its target number *depends* on the deletion (−6 free) and because items 2/3/5 all add
test modules in the idiom that generates the errors. **STACK:** the same delete-then-harden ordering
consequence, plus "land the deletion before re-baselining the watermark or the new number will be wrong
within the same milestone."

**The conflict is only apparent, and it dissolves by splitting the mypy work in two:** hardening the
checker *mechanism* is count-independent and must come first (a number measured with a fail-open gate is
meaningless); *fixing the errors and setting the watermark* is count-dependent and must come after the
deletion. One recommended spine:

### Phase 131 — Gate hardening, CI parity, and the fail-open sweep

**Rationale:** every later phase's "green suite" is unverified until the mypy gate can actually fail. This
is this project's own established gate-first pattern (v1.12's baseline-and-gate-before-touching-firmware;
v1.23 Phase 123's six fail-provable gates authored *before any firmware moved*). Deliberately
**count-independent** — it hardens the mechanism and does not set a watermark.
**Delivers:** `check_mypy_watermark.py` fail-closed (returncode-before-regex; require the
`(checked N source files)` completion clause; `MIN_CHECKED_SOURCE_FILES = 120`; `sys.executable -m mypy`);
`python_version = "3.10"` with an honest comment; **the first paired pytest this checker has ever had**
(fake-mypy stub via an env seam + planted fixtures: truncated shape ⇒ exit 2, config-rejection ⇒ exit 2,
`Found 200 … (checked 120)` ⇒ exit 1, `Found 3 … (checked 4)` ⇒ exit 2 on the coverage floor, canary
floor missing ⇒ red); one real `gh workflow run ci.yml` dispatch recorded (A-1); the derived
`_HANDLER_FUNCTION_NAMES` subset test; a `check_no_exists_proxy.py` re-run; the `sdp_capability`
**43/41/84 count gate, derived not literal** (the missing gate is against **narrowing for convenience** —
the cheapest way to green a field BAD is to move a chip to REFUSE); and the reusable **CI-parity recipe**
as an acceptance leg.
**Addresses:** mypy gate-hardening (table stakes).
**Avoids:** P-13, P-14, P-07, P-10, P-18, and pre-authors P-11's vocabulary + the two target-resolution
test legs (targets must resolve locally).
**Research flag:** **SKIP** — STACK §1 and PITFALLS P-13 give the fix line by line, both reproduced.

### Phase 132 — Retire `dev sdp`, re-home its honesty tests, discharge the mypy debt

**Rationale:** smallest diff, largest unblocking effect: it removes one row from 999.15's classification
table, dissolves the host/firmware contradiction instead of arbitrating it, and drops the honest mypy
count 69 → 63 **for free**. Landing it before the watermark is re-baselined is the only way the number
stays put. Combining the deletion with the mypy discharge in one phase is what resolves the three-way
ordering conflict.
**Delivers:** `cli_handlers.py:2193-2318` deleted; `tools/check_no_exists_proxy.py:156` edited **in the
same commit** (R-9); `git mv tests/test_dev_sdp_cmd.py → tests/test_dev_test_sdp_leg.py` with the four
honesty assertions retargeted and a grep acceptance criterion proving no net loss; the D-14
`MSG_ERR_UNKNOWN_CMD` mapping and the D-10 honesty wording **relocated, not dropped**; the `.ambr`
snapshot update scoped to `test_help_dev` with a named expected diff shape; the `COMMAND_NAMES[COMMAND_SDP_*]`
dereference test; the P-21 tripwire (comment at the auto-unlock site + a test named for the dependency);
the three in-tree `301`/`377` comment corrections; **then** the typed `AppContext` fixture in
`tests/conftest.py`, the ~30 remaining mechanical fixes, and the watermark re-baselined to the true count
(measured path: 63 → 39 → **33 ≤ 35 GREEN** without touching the ring-fenced `eprom_operations.py`
cluster).
**Addresses:** delete `dev sdp`; the mypy debt.
**Avoids:** R-9, P-15, P-16, P-17, P-21, P-08 (notice update lands with the leg), and the A-2 trap where
new test modules add errors of exactly the class being fixed.
**Research flag:** **SKIP** — three researchers independently mapped every trace.

### Phase 133 — The plan-derived SDP leg in `dev test` (the oracle)

**Rationale:** the milestone's reason to exist, and it depends on 132 for the typed fixture, the re-homed
honesty assertions and a gate that can fail. **Likely worth splitting into two phases** (133 *mechanism*:
`Step.group`/`role`, the `finally` cleanup registry, the widened `_run_step` except set, `_SDP_OPS` +
the extended deliberate-break test, the `group=None` byte-identical no-op proof; 133b *leg*: the four
ops, `derive_plan` derivation, `_SDP_REGION` + `sdp_probe_pattern`, the oracle truth table, the report
rows).
**Delivers:** the four ops with `sdp-unlock` **exempt** from `_DESTRUCTIVE_OPS` (R-4); the transition-
proving baseline and complement-B (A-3); the four-arm no-default truth table with the length gate; the
`HELD/NOT-HELD/NOT-RUN` report field and the extended `count_applicable` M (A-4); `SCHEMA_VERSION` 1.2→1.3;
the recoverability line in the word **"rewrite"**; the extended `_ALWAYS_WRITES_NOTICE` with a **content**
assertion; the op-registration parity test (P-23 — one test, ten assertions, converting eight fail-open
registries into one fail-closed gate).
**Named acceptance criteria that must be listed, not incidental:** the write-succeeded ⇒ **BAD + exit 1**
test · the both-directions oracle test · four degenerate-read-back fixtures · a test per exit-code
laundering route R1–R6 each asserting `sdp_lock.assert_not_called()` **and** a visible `NOT-RUN` reason ·
the `try/finally` drain and the baseline gate · the "erase"-forbidding grep.
**Avoids:** P-01, P-02, P-03, P-04, P-05, P-06, P-09, P-12 (report strings), P-20, P-23.
**Research flag:** **NEEDS `--research-phase`** if split further — specifically on whether `_dispatch_sdp`
is one function or four (style call, no correctness content, but it must be reflected in the `_SDP_OPS`
deliberate-break test) and on the exact `run_plan` `finally` shape. Everything else is specified.

### Phase 134 — `write --sdp-relock`

**Rationale:** must ship **with** the deletion (they are a pair — deleting the lock before re-homing it
strands the only legitimate use case), inherits 132's repurposed gate-ordering tests and the relocated
D-14/D-10 material, and is much the smaller of the two build phases. **Can parallelise with 133** —
disjoint file regions (133 writes `chip_test.py`, `diagnostic_report.py` and `cli_handlers.py` only at
`_ALWAYS_WRITES_NOTICE` + the `dev_test` body; 134 writes `cli_handlers.py` only in the `write` handler at
`529-691`, ~1,400 lines apart, no overlap; neither touches `eprom_operations.py`, `constants.py`,
`sdp_capability.py` or `channel.py`). **If the executor model enforces one-writer-per-file, serialise 134
after 133** — 134 is the smaller diff and reordering costs little.
**Delivers:** the option and help text; **the new post-write verify pass** (R-3); the refusal matrix
reusing the already-computed `allowed, sdp_reason` at `:626` (non-`0x0D` ⇒ **refuse loudly**, deliberately
*unlike* the D-18 warn-and-proceed arm, because CMD 10's magic-address bytes would land as **data**;
capability-REFUSED ⇒ refuse **before any hardware is energized** — this is where the deleted command's
Gate 2 gets repurposed rather than discarded); the exit-code table; the loud skip on verify failure.
**Avoids:** P-22 — the hazard is the word *"loudly"*: a skip that appears only at `INFO` is not loud, and
because protection state cannot be read back **the user has no way to ever discover the part is
unprotected**. Requires a non-zero exit or a mandatory final `WARNING:` line, asserted by test, plus
`operator.sdp_lock.assert_not_called()` on the verify-fail path.
**Also fixes:** the stale `--sdp-relock` deferral label at `STATE.md:538` / `PROJECT.md:823` (R-7).
**Research flag:** **SKIP** — the chain is traced end to end and the refusal matrix is fully specified.

### Phase 135 — 999.15 / gh#8 dev-tools channel gating

**Rationale:** after 132 (one fewer subcommand to classify, contradiction gone) and best after 133/134 so
`dev test`'s and `write`'s final shapes are what gets asserted. Weakly parallelisable at best — the
classification keys on command *names*, not bodies, but pinning `dev --help` against final content is
worth the wait.
**Delivers:** `STABLE_DEV_COMMANDS` + `is_dev_command_available` + `dev_beta_only_message` in
`channel.py`; a `_DevGroup(click.Group)` filtering `list_commands` and refusing informatively in
`get_command`; a reworded `dev` group docstring (it currently reads *"Debug command for development
purposes. USR button will break command and return."*, which actively warns off the stable users
`dev read` + `dev test` are being kept for); `dev --help` pinned on **both** channels via subprocess.
**Avoids:** P-19, P-15's second failure, and the **`hidden=` fail-open** — `hidden=` is a `--help`
cosmetic documented as such in `_reject_py32_only_option`'s own docstring (the HOST-02 bug: on a stable
build `--usb-id` was accepted at exit 0 while `--dfu-probe` was refused at exit 2, both being py32-only
surface). `@dev.command(hidden=True)` behaves identically for a command: `firestarter dev reg …` stays
fully invokable, just undocumented. **999.15 must gate by not registering the command.** Anything less is
security-by-help-text. And **do not build the gate by scanning firmware source** — four host gates broke
that way in Phase 117 and they failed **OPEN**.
**Research flag:** **NEEDS `--research-phase`** — one open design choice (invocation-time `_DevGroup` vs
import-time deletion + a subprocess harness; both satisfy 999.15) plus a live carry-forward: `dev reg 0 0
0x86 -f` is the held-erase-rail DMM proxy and load-bearing bench tooling, so a source-checkout override
must be designed **up front**.

### Phase 136 — Close: honesty ledger, armed claim gate, gh#12 follow-up

**Rationale:** the claim gate must be authored **and hosted** by the phase that authors the artifacts —
that was v1.22's shape and it was correct *for v1.22* precisely because author and host were the same
phase. Do not repeat v1.23's cross-phase pre-authoring unless the arming + sibling-dirname coupling is
re-derived from scratch, with a test.
**Delivers:** the v1.30 claim gate (vocabulary from v1.22, mechanics from v1.23, suffixed env seam,
renamed test module, two new target-resolution legs), armed and green with a `PASS:` naming **this**
milestone's four artifacts, **its own suite run and its output recorded in the SUMMARY**; a **host-side**
claim scan in `firestarter_app/tools/` over `diagnostic_report.py`'s string literals (surface 4 — the
`dev test` report text goes to strangers on every run and **no gate scans it today**, and a host-side
gate lives where CI actually runs); the honesty ledger pairing every permitted claim with its explicit
non-claim, including the P-21 coupled-decision row; the release-notes "Removed" section mapping
`dev sdp disable` → `write` (automatic) and `dev sdp enable` → `write --sdp-relock`; the gh#12 reply
**behind a blocking operator wording review as an explicit non-`<automated>` step**.
**Avoids:** P-11, P-12, P-25.
**Research flag:** **SKIP** — P-11 specifies the gate design completely.

### Phase Ordering Rationale

- **131 first, and count-independent.** Any green suite reported by 132–136 is unverified until the mypy
  gate can actually fail. Splitting "harden the mechanism" from "fix the errors" is what lets 131 come
  first without waiting on the deletion's −6.
- **132 before 133** resolved deliberately: PITFALLS warns that deleting first opens a window in which
  the SDP capability has zero test coverage and the four honesty assertions exist nowhere — the
  mitigation is `git mv` plus the grep criterion **inside 132**, not deferring the deletion. With those,
  132-then-133 is safe and gives 133 a typed fixture and a settled watermark.
- **132 before 135, either way.** Whichever of the deletion and the channel split lands first shrinks the
  other's diff, and v1.30 **deletes** a subcommand 999.15 would otherwise have to classify — including
  the awkward case where `constants.py:66-67` documents the *firmware* commands as deliberately **not**
  DEV_TOOLS-gated *"because they are real user-facing operations in every build"* while the *host*
  surface was about to be classified beta-only.
- **133 ∥ 134 is genuinely available** on disjoint regions; 134 is also the phase that inherits 132's
  gate-ordering cases, which apply to `write --sdp-relock` **more** than to the `dev test` leg.
- **136 last and serial** — the gh#12 follow-up describes a substitution; written earlier it would
  describe a plan, not a fact.
- **Cross-cutting, every phase:** run P-18's CI-parity recipe (suite twice — once with
  `FIRESTARTER_FW_ROOT` at an empty dir, once with the sibling present; CI-scoped ruff; no board attached
  for one run) and **name the exact requirement IDs each plan may mark Complete** at dispatch (P-24 —
  executors prematurely marked multi-plan requirements Complete 4× in P116).
- **Do not run the close under `--auto`/`--chain`** — this milestone has an operator-wording-review gate
  and a bench-free evidence ceiling, and `--auto` auto-approves human-verify gates.

### Research Flags

Phases likely needing `/gsd-plan-phase --research-phase`:

- **Phase 133 (and 133b if split)** — the `_dispatch_sdp` shape (one function or four) and the exact
  `run_plan` `finally` shape are open; everything else is specified to the line.
- **Phase 135** — the invocation-time vs import-time gate choice is a live operator/roadmapper decision,
  and the `dev reg` bench-tooling override must be designed up front.

Phases with standard patterns (skip research-phase):

- **Phase 131** — STACK §1 and PITFALLS P-13 give the fix line by line, both reproduced locally.
- **Phase 132** — every trace independently enumerated by three researchers; the only judgement call
  (clean removal vs a transitional stub) is already argued and decided in favour of clean removal.
- **Phase 134** — the call chain is traced end to end and the refusal matrix is fully specified.
- **Phase 136** — P-11 specifies the gate design completely, including its two new test legs.

## Operator Decisions Needed

Surfaced, not guessed. Each changes something the implementer must not decide alone.

1. **`count_applicable` / exit-code policy for a non-running oracle.** Should an ALLOW-chip oracle that
   lands `SKIPPED`/`NA` map to exit **2** (`marginal`) rather than 0? *"We tried and could not tell"* is
   genuinely marginal — but this **changes `dev test`'s published exit-code contract** at
   `cli_handlers.py:2091` (*"0 if every step is OK/NA/SKIPPED, 2 if any step is marginal, 1 if any BAD"*)
   for community reporters already running b14/b15. The `HELD/NOT-HELD/NOT-RUN` report field and the
   `count_applicable` M extension are recommended **regardless**; only the exit-code remap needs a
   decision.
2. **The `eprom_operations.py` D-07 ring-fence.** `firestarter.eprom_operations` is *deliberately*
   outside the strict island per D-07's *"GATE-1.8d read-path ring-fence, deferred to v1.9 post-RCA"*
   (verified in `pyproject.toml`'s `follow_imports = "silent"` override block). Its 10 `[union-attr]`
   errors are one root cause with one fix. **This milestone opens that exact file anyway** (`sdp_lock`/
   `sdp_unlock` are declared load-bearing survivors, and R-7's comment corrections touch it). Decide the
   ring-fence question **deliberately at scoping**; do not let it be answered as a side effect. Note the
   good news: `ci` can be green at watermark 35 **without** touching it (A-2), so this is genuinely
   optional extra credit rather than a blocker.
3. **Does the py3.9 floor keep type-level enforcement once mypy targets 3.10?** After R-8's fix, nothing
   type-checks against the `>=3.9` floor the package still advertises in two places
   (`requires-python`, and a `Programming Language :: Python :: 3.9` classifier). `[tool.ruff]
   target-version = "py39"` carries the syntax/idiom floor but **cannot** catch a py3.10+ *stdlib API*
   used on 3.9. The residual gap is real and not new (it has existed since 2026-05-27). Its correct
   closure is either **a py3.9 CI matrix leg** or **dropping 3.9** (EOL 2025-10-31) — both are decisions
   orthogonal to these six items. Research recommends: keep `>=3.9` in v1.30 and backlog the drop.
4. **`--sdp-relock`'s verify gate now requires a verify pass to exist.** The **polarity is already
   decided** (operator, 2026-08-03: *verify failure ⇒ skip the relock and report it loudly*) — this is
   **not** an open choice. What is open is the mechanism: R-3 measured that `write` has **no verify pass
   at all**, so honouring the decided polarity means adding an explicit `verify_eprom` call on the
   `--sdp-relock` path (recommended design B: extra pass only when the flag is passed; default `write`
   path byte-identical) rather than silently degrading the gate to `write_eprom`'s boolean (design A,
   which would make "verify" a misnomer and relock a chip whose contents were never compared). Approve
   the added scope, or approve design A explicitly with the misnomer recorded.
5. **Shared or distinct SDP region?** `_SDP_REGION = (256, 256)` is recommended for evidence hygiene
   (ARCHITECTURE §2.4). A phase could legitimately choose the shared `(0, 256)` window for simplicity —
   but must then explain in the report why step 3's read-back is not confounded by the earlier `OP_WRITE`
   step.
6. **`gh#20` (AT28C256 `dev test` FAIL, open since 2026-07-30) should be triaged before or with the
   leg.** The first community `dev test` report on an SDP-capable `0x0D` part is a **failure**, and v1.30
   is about to add a lock to that same run. This is the live instance of the "lock a part whose baseline
   write never worked" hazard, and it is the reason the baseline gate is a safety criterion rather than a
   nicety.
7. **Two latent carries worth a decision at scoping, not a discovery at close:** (a)
   `test_present_root_with_missing_target_raises_not_skips` — a Phase-129-authored **hard assert that was
   softened to a skip** during the b15 hand-off (a defect-class change), and that commit is the current
   fork base; restore it with a correct standalone-checkout guard, or record the downgrade deliberately.
   (b) The still-owed `81fa53c` carry — an app CI fix that exists on `beta` **only** and must be
   reintroduced at the next merge toward `main`; `main` has still never been merged in any of the three
   repos, so it stays latent, but v1.30 touches `check_no_log_in_sdp_window.py`'s neighbourhood and
   should not make it worse.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | **HIGH** | Everything measured on this tree: the mypy mechanism reproduced with three purpose-built probe configs, the 69-error count and its full file/class distribution measured in a numpy-free venv reproducing `ci.yml`'s closure exactly, every file:line read from the live tree, the channel-gating mechanism read in full. MEDIUM-verified only on two external version facts (mypy's minimum-target policy history, Python EOL dates) — both cross-checked against a live source *and* reproduced locally. |
| Features | **HIGH** on host-surface mechanics | All measured against the live tree, including a live DB measurement (84 `0x0D` chips / 43 ALLOW / 41 REFUSE; all 43 with `chip-id == 0`) and an executed Click 8.3.3 unknown-subcommand probe. **LOW** on the external competitor comparison (minipro man page, web-sourced, though fetched from the upstream repo directly; one third-party doc describes an inverted `-u` polarity that no changelog corroborates — noted, not relied on). |
| Architecture | **HIGH** on every integration point | All read from the live tree at `16a313a`, most re-measured by execution; `chip_test.py` read in full across four passes, `diagnostic_report.py`/`sdp_capability.py`/`channel.py` read in full; the "`write` never verifies" finding is a grep-confirmed negative. **MEDIUM-HIGH** on build order — its single soft spot (the CI-redness premise) is settled by A-1. |
| Pitfalls | **HIGH** for the 13 grounded in first-party reads + P-13 (reproduced locally, exact output quoted) + P-11 (both checker copies read in full) | **MEDIUM→HIGH** on syrupy's unused-snapshot default (cross-checked against syrupy 5.5.3's own `session.py`/`__init__.py` source, not docs alone). **MEDIUM** on P-24/P-25 (this project's recorded incident history, not re-verified this session) and on *which* specific downgrade an implementer will reach for (the routes are enumerated from code; the likelihood ordering is judgement). |

**Overall confidence:** **HIGH.** All four researchers worked the same live tree, independently
re-measured the same anchors, and agree on every load-bearing number. The only substantive disagreements
are the four adjudicated above, and three of them dissolve on inspection.

### Gaps to Address

- **The current post-fork mypy count on `16a313a`.** 69 is well established, but the watermark should be
  set from a **current** CI run. Handle in Phase 131 with the A-1 dispatch, before any number is
  committed to `pyproject.toml`.
- **`sdp_capability`'s exact line (266 vs 272).** Two of three researchers read 266. Cosmetic; re-measure
  at execution rather than trusting either.
- **`_dispatch_sdp` shape and the exact `run_plan` `finally` structure.** No correctness content, but it
  must be reflected in the `_SDP_OPS` deliberate-break test. Handle in Phase 133's plan.
- **Whether `_ALWAYS_WRITES_NOTICE`'s true write-pass count is 5, 6, 7 or 8** for a representative ALLOW
  chip. Do not hardcode the sentence twice — **derive** the count from the plan the engine actually
  emits, and assert the notice against that derivation.
- **The `dev reg` source-checkout override for 999.15.** Load-bearing bench tooling that a naive channel
  gate would remove from a source checkout. Needs designing in Phase 135, not discovering.
- **`0x0D` remains `UNVERIFIED` and will remain so at close.** Not a research gap — the evidence ceiling.
  The gap that *must* be closed is that the report **carries the evidence** when the one settling
  community report finally arrives: the pre-write read hash, the read-back hash and length, and the
  `HELD/NOT-HELD/NOT-RUN` state must be in `report.to_dict()`, or that report will arrive unable to settle
  anything.

## Sources

### Primary (HIGH confidence)

- **Live tree `firestarter_app` @ `beta` `16a313a`** — `chip_test.py` (1,253 lines, read in full),
  `cli_handlers.py` (2,321 lines), `diagnostic_report.py` (532), `sdp_capability.py` (281),
  `channel.py` (81), `eprom_operations.py`, `constants.py`, `exceptions.py`, `serial_comm.py`,
  `firmware.py`, `submit.py`; `pyproject.toml`, `.github/workflows/{ci,beta-release}.yml`
- **`tools/`** — `check_mypy_watermark.py`, `check_devtest_orchestrator.py`, `check_no_exists_proxy.py`,
  `check_sdp_capability_invariants.py`, `check_no_log_in_sdp_window.py`, `parse_devtest_issue.py`
- **`tests/`** — `conftest.py`, `fw_presence.py`, `scan_paths.py`, `test_dev_sdp_cmd.py` (558 lines),
  `test_dev_test_cmd.py`, `test_characterization.py`, `test_py32_channel_gating.py`, `test_skip_census.py`,
  `test_parse_devtest_issue.py`, `test_revision_constants_parity.py`, `__snapshots__/test_characterization.ambr`
- **Live tree `firestarter` @ `0933bd7`** (untouched this milestone) —
  `test/native/avr/test_sdp_harness/`, `test_eeprom28c_sdp/`, `platformio.ini` `[env:native]`
- **Executed measurements (2026-08-03):** `mypy 2.3.0` at three targets incl. a numpy-free CI-replica
  venv (`Found 69 errors in 17 files (checked 120 source files)`, EXIT=1) · `mypy firestarter/` alone
  (25 in 6) · `--no-local-partial-types --no-strict-bytes` (also 69) · `python3 tools/check_mypy_watermark.py`
  (exit **0**, "1 errors — 34 below watermark") · `pytest --collect-only` (**1303** tests) · full
  `pytest tests/ -q` green · CI-scoped `ruff check`/`ruff format --check` clean · live DB partition
  (84/43/41, all 43 `chip-id == 0`) · `derive_plan("AT28C256", write_scope="full")` step list and region
  `(0, 256)` · Click 8.3.3 unknown-subcommand error + exit 2 · syrupy 5.5.3 `pytest_sessionfinish` source
- **`gh run view 30708836339`** (Host CI, `workflow_dispatch`, 2026-08-01) — RED at exactly
  `mypy type check (watermark gate)`; `pytest` and the smoke test never ran
- **Meta repo** — `.planning/notes/sdp-surface-retirement-and-behavioral-proof.md` (157 lines),
  `PROJECT.md` § Current Milestone v1.30, `STATE.md`, `RETROSPECTIVE.md`, `research/questions.md` §999.25,
  both `check_permitted_claims.py` copies + their tests and fixtures (122-close, 123-non-regression)

### Secondary (MEDIUM confidence)

- [python/mypy `CHANGELOG.md` (master)](https://raw.githubusercontent.com/python/mypy/master/CHANGELOG.md) —
  mypy 2.0 removed `--python-version 3.9`; 1.20 was the last supporting release; 2.0 defaulted
  `--local-partial-types`/`--strict-bytes` on. Cross-checked against the reproduced error message and
  against the 2.1.0/2.3.0 pair present on this box.
- [Python | endoflife.date](https://endoflife.date/python) and
  [Python 3.10 EOL discussion](https://discuss.python.org/t/python-3-10-eol-is-there-an-official-end-of-support-date-within-october-2026/108064) —
  3.9 EOL **2025-10-31**, 3.10 EOL **2026-10-31**
- [syrupy README / releases](https://github.com/syrupy-project/syrupy/blob/main/README.md),
  [syrupy on PyPI](https://pypi.org/project/syrupy/),
  [syrupy issue #138](https://github.com/tophat/syrupy/issues/138) — unused-snapshot handling and
  `--snapshot-warn-unused`; cross-checked against the installed 5.5.3 source

### Tertiary (LOW confidence — needs validation)

- [minipro man page, `man/minipro.1`](https://gitlab.com/DavidGriffith/minipro) and its
  [ManKier rendering](https://www.mankier.com/1/minipro) — `-u/--unprotect` / `-P/--protect` quoted
  verbatim; no standalone protect subcommand, no status query. Some third-party/older docs describe an
  inverted `-u` polarity; **no changelog corroborates it** — noted, not relied on.
- [AT28C256](https://ww1.microchip.com/downloads/en/DeviceDoc/doc0006.pdf) /
  [AT28C64B](https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/AT28C64B-64-Kbit-8Kx8-Parallel-EEPROM-with-Page-Write-and-Software-Data-Protection-DS20006432.pdf)
  datasheets and [Microchip Device Operation docs](https://onlinedocs.microchip.com/pr/GUID-BF812ABD-A95E-4E56-B54E-14AA4CC3999A-en-US-1/GUID-D6DBCF7C-05FF-418D-8F92-F6EC72BB55D4.html) —
  3-byte SDP enable/disable sequences, ships SDP-disabled, survives power cycling, **no status bit
  documented**. Primary-source corroboration of Phase 117 D-05 / Phase 119 D-12.

### Detailed research documents

- `.planning/research/STACK.md` · `FEATURES.md` · `ARCHITECTURE.md` · `PITFALLS.md`

---
*Research completed: 2026-08-03*
*Ready for roadmap: yes*
