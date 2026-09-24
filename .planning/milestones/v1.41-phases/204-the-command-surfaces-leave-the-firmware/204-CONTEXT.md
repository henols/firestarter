# Phase 204: The command surfaces leave the firmware - Context

**Gathered:** 2026-09-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Command ordinals **4 (`CMD_BLANK_CHECK`)** and **6 (`CMD_VERIFY`)** leave the firmware entirely, on
both sides of the wire, with every in-algorithm verify provably intact. Both host↔firmware skew
directions are **observed on the bench**, not reasoned about.

**This phase is dual-repo** (`firestarter_fw` + `firestarter_app`) **and bench-gated.** It is the
first phase of v1.41 to touch firmware.

**What survives this phase and leaves in 205:** `mem_util_blank_check`,
`mem_util_blank_check_region`, `blank_check_saved_address`, `BLANK_CHECK_CHUNK_SIZE`,
`FLAG_SKIP_BLANK_CHECK`, and the write-init / erase-end pre-flight call sites that reach them. After
204 those functions are reachable **only** from write-init and erase-end — no command surface routes
to them any more.

**What survives permanently (D-7, milestone activation):** `memory_verify_execute`, the per-pulse
verify inside the EPROM program loop, `eeprom28c_verify_page_readback`, `flash_util_verify_operation`
and `MSG_ERR_VERIFY` (0xAF). **This phase removes a command surface. It does not remove
verification.**

**Not in this phase:** the version bump to `3.1.0b1` (REL-01, Phase 207); wiki documentation of the
breaking change (REL-04, Phase 207); the pre-flight removals and the `FLAG_SKIP_BLANK_CHECK` bit
(FWBLANK-01…05, Phase 205); `dev test`'s 3-way verdict migration and the serial session lease
(Phase 206); the `DONE`-based clean stop (**D-13** below, stays filed as CMP-F1).

</domain>

<decisions>
## Implementation Decisions

### How far the removal sweeps (the 204/205 seam)

- **D-01:** **Full sweep of both ordinals in 204.** FWCMD-01 names three sites; the tree carries
  **eleven firmware sites plus the host mirror**, measured during discussion. All of them go in this
  phase:

  | # | Site | What it is |
  |---|---|---|
  | 1 | `firestarter_fw/include/firestarter.h:52,54` | the two `#define`s |
  | 2 | `firestarter_fw/include/firestarter.h:117,119` | `is_memory_cmd` arms |
  | 3 | `firestarter_fw/src/firestarter.cpp:270-272,276-278` | dispatch switch arms |
  | 4 | `firestarter_fw/src/eprom_operations.cpp:30-33,53-56` | the two wrappers |
  | 5 | `firestarter_fw/include/eprom_operations.h:10,13` | their declarations |
  | 6 | `firestarter_fw/src/proms/memory.cpp:73-75` | `configure_memory`'s `CMD_VERIFY` arm |
  | 7 | `firestarter_fw/src/proms/eprom.cpp:56-58` | `configure_eprom`'s `CMD_BLANK_CHECK` arm |
  | 8 | `firestarter_fw/src/proms/flash_nor_unlock.cpp:43-45` | same, NOR unlock |
  | 9 | `firestarter_fw/src/proms/flash_intel.cpp:61` | same, Intel flash |
  | 10 | `firestarter_fw/src/proms/flash_5v_page.cpp:46` | same, flash4 |
  | 11 | `firestarter_fw/src/proms/eeprom_28c.cpp:150` | same, 28C parallel |
  | 12 | `firestarter_fw/src/operation_utils.cpp:231-…` | `_single_step_operation_callback`'s whole `CMD_BLANK_CHECK` emit-and-ack block |
  | 13 | `firestarter_fw/src/proms/memory.cpp:500,529` | the two `handle->cmd == CMD_BLANK_CHECK` branches **inside** `mem_util_blank_check_region` |

  Sites 12 and 13 exist **only** to serve the standalone command: they defer the `MSG_ERR_NOT_BLANK`
  and `MSG_DATA_PROGRESS` emits out of programmer mode, because the Uno's `rurp_log_id` is
  `com_mode`-gated and a direct emit there is silently dropped. With ordinal 4 gone, both branches
  collapse to their existing `else` arm — the direct emit — which is exactly what the surviving
  write-init and erase-end callers already take. **This is a behaviour-preserving collapse for every
  remaining caller**, and it must be proven so rather than assumed.

  Rejected alternatives and why: the *literal minimum* (sites 1-6 only) would leave eight unreachable
  references and **force `#define CMD_BLANK_CHECK 4` to survive**, which makes FWCMD-03's "reserved,
  never reused" record aspirational rather than real, and leaves a firmware between 204 and 205 that
  compiles a retired ordinal — a bisect landing there is misleading. The *middle* option (the five
  per-protocol arms but not the internals) re-anchors the same gate and the same golden as the full
  sweep, so it buys nothing.
  — **Reversibility:** costly — the sweep touches eleven firmware sites plus two test gates and a
  pinned golden; undoing it means re-deriving the golden a further time and restoring a census.

- **D-02:** **FWCMD-03's reserved record lives on BOTH ladders**, mirroring the shape FWBLANK-02
  already specifies for `0x08` in Phase 205. `#define CMD_BLANK_CHECK 4` / `#define CMD_VERIFY 6`
  leave `firestarter_fw/include/firestarter.h`, and `COMMAND_BLANK_CHECK` / `COMMAND_VERIFY` plus
  their `COMMAND_NAMES` rows leave `firestarter_app/firestarter/constants.py`. Each ladder gains a
  comment at the gap naming the version the ordinals were retired in and why they must never be
  reused. This honours `/workspaces/CLAUDE.md`'s rule that the two ladders move in the same commit
  pair.

  **Two consequences that must be handled in this phase, not discovered later:**
  - Phase 202 left inline comments in `eprom_operations.py` stating "COMMAND_VERIFY stays in
    constants.py" / "COMMAND_BLANK_CHECK stays in constants.py"
    (`eprom_operations.py:2705`, `:2978`). They go stale here and must be corrected in the same
    change.
  - `eprom_operations.py:628` is a **live use**, not a comment:
    `cmd in (COMMAND_WRITE, COMMAND_VERIFY)` gates the `region-end` wire key. Since nothing composes
    `COMMAND_VERIFY` any more, the tuple member is already dead; deleting the constant forces this
    expression to change. The surrounding comment cites BLANK-01 / D-05 and the firmware's
    region-scoped blank check — which Phase 205 removes — so re-read it rather than assuming it
    still describes live behaviour.
  — **Reversibility:** one-way — a retired wire ordinal is a published protocol contract, and
  REL-04 will document it in the wiki.

- **D-03:** **FWCMD-05 is factually wrong and must be amended before planning**, the same way
  Phase 203's D-02 amended WRITE-02 and Phase 202's discussion amended CMP-04. *(Operator answered
  "you decide"; decided by Claude with the reasoning recorded here.)*

  FWCMD-05 asserts that the per-pulse verify, `eeprom28c_verify_page_readback` and
  `flash_util_verify_operation` each still raise `MSG_ERR_VERIFY` (0xAF). Measured:

  | Named site | Error id it actually raises |
  |---|---|
  | per-pulse verify, `eprom.cpp:465-473` via `eprom_internal_report_budget_failure` | `MSG_ERR_MAX_PULSES` / `MSG_ERR_ENERGY_CAP` |
  | `eeprom28c_verify_page_readback`, `eeprom_28c.cpp:530` | `MSG_ERR_VERIFY` ✔ |
  | `flash_util_verify_operation`, `flash_utils.cpp:47` | `MSG_ERR_OP_TIMEOUT` — it is a DQ7 data-poll wait, not a compare; it can never raise 0xAF |

  The only other 0xAF raise in the tree is `memory_verify_execute` (`memory.cpp:391`), which
  FWCMD-04 covers separately.

  **The amendment is stronger, not weaker:** pin each site to the id it actually raises, so three
  distinct ids are proven instead of one wrong one. This also closes the recorded trap where a
  golden trace with a matching id misses the WARN/ERROR fork. Amend **both**
  `.planning/REQUIREMENTS.md` FWCMD-05 and `.planning/ROADMAP.md` Phase 204 success criterion 3,
  which carries the same wording. Record the before/after text in the phase record.

- **D-04:** **Proof instrument is split by property type.** FWCMD-04 ("`memory_verify_execute` is
  still called for `VERIFY_PER_PULSE_PLUS_FINAL`; a test fails if that call disappears") is a
  call-site-existence property — a **source-contract gate**, in the shape of the seven this
  repository already runs (`test_write_path_source_contract_v131.py` is the closest analogue). The
  amended FWCMD-05 ("each raises its own id on failure") is a behavioural property no grep can
  prove — **native behavioural tests** under `firestarter_fw/test/native/avr/`.

  **This is real work, not a copy.** The existing native tests assert `h.response_code ==
  RESPONSE_CODE_ERROR`, never the emitted message id, and `MSG_ERR_VERIFY` is asserted by **no test
  anywhere in the tree today** — the only tree-wide match outside source is prose inside the
  branch-inventory golden. Two recorded stub limits apply: the native stubs record no time
  (`delay()` is unstubbed, and `_shared/host_stubs_common.inc` has no `millis` seam), which bears
  directly on `flash_util_verify_operation`'s 150 ms `millis()` timeout path; and native trace stubs
  miss register-write elision.

### What a retired ordinal answers

- **D-05:** **The existing generic refusal is accepted; no new message is minted.** After the sweep,
  ordinals 4 and 6 still satisfy `handle->cmd < CMD_READ_VPP` (both are below 11), so
  `init_programmer_framed` admits them to `json_parse` and takes the `else` branch — which carries
  only `DEV_TOOLS`-gated debug lines. **`configure_memory` is gated on `is_memory_cmd` and is
  therefore never reached, so no hardware is touched.** The dispatch `default:` arm then emits
  `LOG_ERROR_ID_U8(MSG_ERR_UNKNOWN_CMD, handle.cmd)` → `Unknown command: 4` and calls
  `command_done()`, which returns the port to `CMD_IDLE`. FWCMD-06's three properties — explicit
  refusal, no hardware side effect, no hang — all hold by construction.

  Minting a dedicated retired-command id was rejected: it costs a `tools/catalog/messages.toml`
  change plus a codegen run in the meta repo and a sync into both sub-repos, a new catalog id, and a
  PROGMEM format string — in the phase whose stated premise is reclaiming AVR flash. It would also
  need a non-ordinal way to select itself, since criterion 1 forbids `CMD_VERIFY` or
  `CMD_BLANK_CHECK` appearing in that switch at all.

  **Accepted cost, recorded so nobody rediscovers it:** the operator sees `unknown`, which reads
  like a corrupt frame rather than a version boundary, and the pre-`3.1.0` host is shipped code that
  cannot soften it. Phase 207 owns REL-04's wiki breaking-change page, which is where the boundary
  gets named for a human.

- **D-06:** **The orphaned debug ids stay in the catalog.** `DBG_VERIFY_PROM` (0x08) and
  `DBG_BLANK_CHECK_PROM` (0x0B) exist only for the two `LOG_DEBUG_ID_SUB` lines inside the wrappers
  FWCMD-02 deletes; nothing else in either repository uses them. They keep their
  `tools/catalog/messages.toml` entries, each gaining a comment recording that its emit site was
  retired in `3.1.0` and that the id is not free for reuse.

  **This keeps 204 a two-repo phase, as the roadmap scopes it.** Retiring them would make it a
  three-repo lockstep commit set — meta codegen plus a sync into both sub-repos — to reclaim two
  debug ids that cost nothing on the AVR (`LOG_DEBUG_ID_SUB` is id-only; no format string reaches
  firmware flash).
  — **Reversibility:** reversible — a catalog comment, not a contract.

### The bench legs (REL-02, REL-03, criteria 4 and 5)

- **D-07:** **`3.1.0b1` is a substituted label at 204, and the phase record names the real shas.**
  REL-01's version bump is Phase 207, so neither side carries `3.1.0b1` during this phase.
  `3.1.0b1 host` / `3.1.0b1 firmware` mean the **post-204 working-tree builds**; `pre-3.1.0` means
  the **pre-204 artifacts**. This is honest rather than lossy: nothing in `verify` or `blank` gates
  on a version string — the refusal is `MSG_ERR_UNKNOWN_CMD` either way — so the label is
  documentation, not mechanism. Pulling REL-01 forward was rejected because it contradicts the
  roadmap's own reason for placing it in 207 (one commit pair, not burned twice) and because Phase
  205 changes firmware again afterwards.

  **The phase record must state the substitution explicitly and name the commit sha that played each
  of the four roles.**

- **D-08:** **The pre-`3.1.0` host is the published wheel, not a reconstruction.**
  `pip install firestarter==3.0.0b49` into a throwaway venv — the artifact a real user actually has,
  which is what REL-03's "a refusal the user can act on" is a claim about. A worktree at the pre-204
  app commit was rejected as a reconstruction, and the editable install does not follow a sibling
  worktree — a recorded trap that has already produced tests running against the wrong tree.

  **Two traps to design around, not discover:** the devcontainer's default interpreter is Python
  3.12 while app CI is 3.11-only, so the venv must be built on 3.11; and the app writes
  `~/.firestarter/config.json` regardless of `FIRESTARTER_CONFIG_DIR`, so a throwaway venv shares
  the real config unless that is handled.

- **D-09:** **"No hardware side effect" is proven by read-back equivalence on a socketed part**, not
  by argument from where the refusal fired. Socket a part with known non-blank content, checksum it,
  run the refused `verify` and `blank` from the `3.0.0b49` host against post-204 firmware, checksum
  again, and prove the content byte-identical. This observes the actual property — that nothing was
  written or erased — and it also proves the refusal did not silently erase, which is the failure a
  blank-check ordinal retiring badly would produce.

  An empty socket was rejected: with no part present there is no hardware to affect, so the
  "no side effect" half would be argued from code structure, which is exactly the inspection
  criterion 5 refuses. Rail observation was rejected outright: the vpp/vpe monitors do not route to
  the socket, so a reading proves nothing about what the part saw, and the held-rail tooling has a
  recorded history of reporting success while measuring nothing.

- **D-10:** **The rig is an Arduino Leonardo carrying a Rev 2.0 shield with a W27C512 seated, on
  `/dev/ttyACM0`, and the operator has given standing permission to drive and flash it without
  asking.** Confirmed by the operator mid-discussion and verified at the port: USB `2341:8036`,
  `cdc_acm`. (An earlier `/dev/ttyUSB0` reading during this discussion was a different device since
  unplugged; the Uno-class inference drawn from it was wrong.)

  **Consequences for the bench sequence, all of which make it easier rather than harder:**
  - **Leonardo is exempt from the chip-out-before-sideload rule**, so firmware swaps need no hands
    on the socket. The whole four-role matrix — post-204 host / pre-204 firmware, then pre-204 host
    / post-204 firmware — can run unattended in one sequence with the W27C512 seated throughout,
    which is exactly what D-09's read-back equivalence wants.
  - **Leonardo's buffer is 1024 bytes, not the Uno's 512**, which changes chunked transfer on the
    host side. Both 204 legs are read-only so this does not bite here, but it means a pass on this
    board does **not** demonstrate the Uno-class path.
  - **Progress emission is Leonardo-only** — `tests/test_progress_emission_is_leonardo_only.py`
    names `blank_check`, and D-01 site 12 deletes exactly the `CMD_BLANK_CHECK` progress-emit block
    that test is about. **The bench board is the one target where that behaviour is live**, so the
    test re-anchor and the bench run examine the same property from two directions.
  - Leonardo's real flash ceiling is **28672**, not 32768.

  Both 204 legs are read-only, so the W27C512's recorded write-path gotchas (plain `write` does
  erase; `-b` polarity is inverted) are not exercised — only its ability to hold content across a
  firmware swap matters.

  **Coverage gap to state, not hide:** this phase proves both skew directions on a Leonardo only. No
  Uno-class board is attached. If Uno-class coverage is wanted for FWCMD-06, it needs a board and is
  a separate leg.

- **D-11:** **Criterion 4 (REL-02) needs no refusal at all.** A post-204 host performing `verify`
  and `blank` against pre-`3.1.0` firmware only ever sends `CMD_READ`, which old firmware serves
  normally. The leg proves the *absence* of a compatibility problem, so its value is entirely in
  being run rather than assumed — which is what "Proven, not assumed" in REL-02 asks for.

### The deferred `DONE` clean stop

- **D-12:** **The `DONE`-based clean stop does NOT land in 204. It stays filed as CMP-F1.**
  `202-READ-ABORT-ANSWER.md` nominated this phase by name, on the grounds that 204 is already
  dual-repo and bench-gated and the firmware change is one line. Measured during discussion, those
  grounds are weaker than they looked:

  - The firmware half is genuinely one line: `op_wait_for_ack` (`operation_utils.cpp:94`) returns on
    `OP_MSG_ACK` and `OP_MSG_ERROR`; **`OP_MSG_DONE` falls through to `delay(10)`** and loops to the
    1000 ms timeout.
  - **The host half is not.** Today the host aborts by *withholding* acks — it sends nothing at all.
    Using `OP_MSG_DONE` means the host must start actively sending `"DONE"`, and
    `_drive_region_compare`'s four-condition discrimination keys on
    `last_firmware_error_code == MSG_ERR_TIMEOUT`, which a clean stop would no longer produce. Both
    sides move together, and the reworked surface is `verify` — the thing Phase 202 just built.
  - It is not in FWCMD-01…06, REL-02 or REL-03. Folding it in is scope addition to a phase that has
    already grown a full ordinal sweep, a gate re-anchor, a golden re-derive, an amended requirement
    and two bench legs.

  **Deferring costs nothing, and this is why:** old firmware's `op_get_message` **already** parses
  `"DONE"` into `OP_MSG_DONE` (`operation_utils.cpp:131-139`) and `op_wait_for_ack` already ignores
  it. A future host that sends `DONE` to pre-`3.1.0` firmware therefore degrades to exactly today's
  1 s timeout path. The change is **forward-compatible by construction** and can land in any later
  phase with the same properties. Record this finding on CMP-F1 so the next author does not re-derive
  it.

### Claude's Discretion

- The exact amendment wording for FWCMD-05 and ROADMAP criterion 3 (within D-03's per-site-id
  content), and whether the amendment lands as one commit or alongside the phase's first plan.
- The source-contract gate's module name, and whether FWCMD-04's gate is a new module or a leg added
  to an existing one — provided it fails when the `VERIFY_PER_PULSE_PLUS_FINAL` call disappears and
  that RED is **seen**, not pre-authored and assumed reachable.
- The mechanism for asserting an emitted message id in a native test (a log capture seam versus a
  trace diff), and whether `flash_util_verify_operation`'s timeout leg needs a `millis` stub or can
  be proven another way.
- The wording of the reserved-ordinal comments on both ladders and of the two catalog comments.
- Whether the Phase 201-05 nine-site source-contract gate is re-anchored to its four survivors in
  204 or retired here because 205 deletes the functions it guards. Not discussed — decide it in
  planning and state the reasoning.
- The bench sequence order, the number of chip swaps, and how the pre-204 firmware `.hex` is
  obtained (a released asset versus a local build of the pre-204 sha).
- Whether the `region-end` guard at `eprom_operations.py:628` becomes `cmd == COMMAND_WRITE` or
  keeps a one-member tuple.

### Folded Todos

- **`2026-08-30-remove-cmd-verify-from-firmware-compare-in-app.md`** (`area: both`,
  `resolves_phase: 204`) — the provenance todo for this entire milestone. Filed 2026-08-30, it
  scoped the verify half and named the constraint that governs v1.41: `memory_verify_execute` must
  survive because `eprom.cpp` calls it for `VERIFY_PER_PULSE_PLUS_FINAL`. **204 closes it.**
  **Scope note:** its `files:` list is partly stale and must not be used as a work list. It carries
  pre-rename `firestarter/` paths (the repository became `firestarter_fw` in Phase 189), and its
  host entries — `eprom_operations.py:1940-1973`, `cli_handlers.py:742-770`, `chip_test.py:162` —
  name code Phase 202 already rewrote. Read it for its reasoning, and take the site list from D-01.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

The ROADMAP.md Phase 204 entry carries no explicit `Canonical refs:` line; this list was accumulated
during analysis and discussion.

### Milestone scope and locked decisions
- `.planning/ROADMAP.md` lines 175-347 — the v1.41 milestone section and the Phase 204 detail block.
  Read **"Two removals, not one" (D-1)**, **"What must NOT be removed" (D-7)**, **"Ordering is a
  safety property, not a preference"**, and the **"204 and 205 are deliberately two phases"**
  paragraph. **D-03 above requires success criterion 3 to be amended here before planning.**
- `.planning/REQUIREMENTS.md` — FWCMD-01…06, REL-02, REL-03, activation decisions D-1…D-7, and the
  Scope paragraph. **D-03 above requires FWCMD-05 to be amended here before planning.**

### Phase 202's output — the engine that made this removal safe
- `.planning/phases/202-one-comparison-engine-on-the-host/202-CONTEXT.md` — the module boundary,
  the compare/render split, the exit-code scoping, and D-13's no-byte-values output rule.
- `.planning/phases/202-one-comparison-engine-on-the-host/202-READ-ABORT-ANSWER.md` — **read in full
  before acting on D-12.** The abort mechanism, its four-condition discrimination, the measured ≤1 s
  per-abort cost, and the "Implication for CMP-F1" section that nominated this phase.
- `.planning/phases/202-one-comparison-engine-on-the-host/202-VERIFICATION.md` and `202-REVIEW.md`.

### Phase 203's output — the host guard now standing in front of the firmware's
- `.planning/phases/203-the-write-guard-moves-up-a-layer/203-CONTEXT.md` — D-01's measured table of
  which firmware write-init paths blank-check today. **That table is the map of what Phase 205
  removes**, and it names the same five protocol files whose `CMD_BLANK_CHECK` arms D-01 above
  deletes. Also D-02's precedent for amending a requirement before planning, which D-03 follows.
- `.planning/phases/203-the-write-guard-moves-up-a-layer/203-SESSION-COST.md` — the measured
  three-port-open baseline, for anyone reasoning about bench wall-clock.

### Provenance
- `.planning/todos/pending/2026-08-30-remove-cmd-verify-from-firmware-compare-in-app.md` — **folded.**
  See Folded Todos. Its `files:` list is stale; read it for reasoning only.
- `.planning/todos/pending/2026-09-20-preflight-firmware-version-compat-guard.md` — **not folded.**
  Read it before writing the REL-03 leg: it is the general form of "an old CLI ends up driving
  firmware it cannot talk to", and it documents why the host's own version probe cannot resolve skew.
- `.planning/todos/pending/new-host-old-firmware-0x05-page-size-skew.md` — **not folded.** The other
  new-host/old-firmware skew in the tree, with a different mechanism. Its "caveat for whoever picks
  this up" explains the `_probe_port` prerelease-truncation limit that bears on D-07's labelling.

### Repository rules that bind this phase
- `/workspaces/CLAUDE.md` — § "Cross-repo obligations" (constants duplicated between `constants.py`
  and three firmware headers, changed in the same commit pair; messages generated **only** in the
  meta repo) and § "Milestone close and branch protection" (**a push to `beta` in either sub-repo
  PUBLISHES**; milestone work forks off `beta`; current branch is `v1.41-verification-to-host`).
- `firestarter_fw/CLAUDE.md` — build, test and CI commands. Owns them; do not copy them forward.
- `firestarter_app/CLAUDE.md` — § "What CI runs": `ruff` scope is `E,F,I,UP` (a `# noqa` for
  anything else is inert), the mypy strict module list in `pyproject.toml`, and the coverage floor.

### Firmware source this phase changes
- `firestarter_fw/include/firestarter.h:45-60` (the CMD ladder) and `:108-130` (`is_memory_cmd`).
- `firestarter_fw/src/firestarter.cpp:74-95` — the admission gate. **Read the comment block:** the
  `is_memory_cmd(handle->cmd) || handle->cmd < CMD_READ_VPP` shape is deliberate and is why D-05's
  refusal path works without a `default`-arm change.
- `firestarter_fw/src/firestarter.cpp:262-345` — the dispatch switch and its `default:` arm.
- `firestarter_fw/src/eprom_operations.cpp:20-85` — both wrappers; note `eprom_verify` shares
  `_process_incoming_data` with `eprom_write`, and `eprom_blank_check`'s single-step shape is cited
  by `eprom_lock_status`'s own comment.
- `firestarter_fw/include/eprom_operations.h:10,13` — the declarations.
- `firestarter_fw/src/proms/memory.cpp:60-90` (`configure_memory`), `:377-397`
  (`memory_verify_execute`, **survives**), `:485-540` (`mem_util_blank_check_region` and its two
  command-keyed branches).
- `firestarter_fw/src/operation_utils.cpp:94-112` (`op_wait_for_ack`, D-12), `:112-150`
  (`op_get_message`'s `DONE` parse, D-12), `:224-250` (`_single_step_operation_callback`'s
  `CMD_BLANK_CHECK` block).
- `firestarter_fw/src/proms/eprom.cpp:45-63` (the configure arm), `:465-500` (the per-pulse verify's
  budget-failure exits and the `VERIFY_PER_PULSE_PLUS_FINAL` call FWCMD-04 pins).
- `firestarter_fw/src/proms/flash_nor_unlock.cpp:35-50`, `flash_intel.cpp:55-70`,
  `flash_5v_page.cpp:40-55`, `eeprom_28c.cpp:135-160` — the four other configure arms.
- `firestarter_fw/src/proms/flash_utils.cpp:30-52` — `flash_util_verify_operation`, whose real error
  id is `MSG_ERR_OP_TIMEOUT` (D-03).
- `firestarter_fw/src/proms/eeprom_28c.cpp:512-535` — `eeprom28c_verify_page_readback`, the one site
  whose `MSG_ERR_VERIFY` claim is true.

### Host source this phase changes
- `firestarter_app/firestarter/constants.py:45-60` (the COMMAND ladder) and `:85-100`
  (`COMMAND_NAMES`).
- `firestarter_app/firestarter/eprom_operations.py:45` (the import), `:612-632` (**the live
  `COMMAND_VERIFY` use** in the `region-end` guard — D-02), `:2695-2720` and `:2955-3010` (the
  Phase 202 comments that go stale).

### Test surfaces that move
- `firestarter_fw/tests/test_blank_check_region_source_contract.py` — Phase 201-05's **nine-site**
  census. D-01's sweep removes five of its nine sites. Its docstring enumerates them: three direct
  calls and six function-pointer assignments.
- `firestarter_fw/tests/test_protocol_branch_inventory.py` and
  `firestarter_fw/tests/golden/protocol_branch_inventory.json` — criterion 6. Scoped to
  `src/proms/eprom.cpp` + `eprom_params.cpp`, pins **blob SHAs**, and test 3 pins the three
  tier-`protocol` sites at **literal lines 71, 145 and 218**. Read the golden's `meta.recorded_by`
  field before re-deriving: it documents the one-commit property, the positional-matching rule, and
  seven prior re-derivations.
- `firestarter_fw/test/native/avr/test_dispatch/test_configure_memory.cpp`,
  `test_cmd_admission/test_cmd_admission.cpp` (the only `is_memory_cmd` test),
  `test_val_eprom/`, `test_val_eeprom28c/`, `test_val_5v_page/`, `test_val_nor_unlock/`,
  `test_eeprom28c_sdp/` — the native tests that name the retired ordinals.
- `firestarter_fw/tests/test_progress_emission_is_leonardo_only.py` — names `blank_check`, and is
  about exactly the emit block D-01 site 12 deletes. The bench board is a Leonardo, the one target
  where that behaviour is live (D-10).
- `firestarter_app/tests/test_eprom_operations.py` — the **only** app test referencing
  `COMMAND_VERIFY` / `COMMAND_BLANK_CHECK`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **The dispatch `default:` arm** (`firestarter.cpp:338-341`) — already emits
  `MSG_ERR_UNKNOWN_CMD` with the offending ordinal and sets `finished = true`, so `command_done()`
  runs. D-05's entire refusal is this existing path; no new code is written for FWCMD-06.
- **`command_done()`** (`firestarter.cpp:208-217`) — resets the control registers, disables the
  chip, sets `cmd = CMD_IDLE` and returns to communication mode. This is what makes "no hardware
  side effect" structurally true; D-09 observes it rather than trusting it.
- **Seven existing source-contract gate modules** in `firestarter_fw/tests/` —
  `test_write_path_source_contract_v131.py`, `test_hv_routing_source_contract_v142.py`,
  `test_ack_layout_source_contract_v143.py`, `test_boolean_convention_source_contract_v133.py`,
  `test_jsmn_token_layout_source_contract_v158.py`, `test_blank_check_region_source_contract.py`.
  D-04's FWCMD-04 gate is the eighth; copy the closest analogue's shape rather than inventing one.
- **`firestarter_fw/test/native/avr/_shared/host_stubs_common.inc`** (302 lines) — the shared native
  stub set. **It carries no `millis` or `delay` seam**, which is the constraint on D-04's
  `flash_util_verify_operation` leg.

### Established Patterns
- **A source-contract gate pins a reasoned census and names the first divergence**, never a bare
  count. `test_blank_check_region_source_contract.py` and `test_protocol_branch_inventory.py` both
  do this, and both resolve their scan targets from `_REPO_ROOT` rather than the environment —
  closing the `check_permitted_claims.py` `_HERE`-resolves-wrong landmine by construction.
- **A golden is re-derived by the gate module's own extractor, never hand-edited**, and old sites are
  matched to live sites **positionally**, never through a `(predicate, keyed_on, tier)` dict — that
  key collides for at least two site pairs in `eprom.cpp` and a dict comprehension silently keeps
  only the last. This is recorded in the golden's own `meta.recorded_by` and has bitten twice.
- **The constants ladders move in the same commit pair** (`/workspaces/CLAUDE.md`), and messages are
  generated **only** in the meta repo — never regenerate or hand-edit `messages.h` / `messages.py`
  inside a sub-repo.
- **Reasoning lives at the site.** The no-comments-in-source rule was removed on 2026-09-19;
  D-01's collapse, D-02's reserved notes and D-05's refusal path each describe reasoning that
  belongs in the code.

### Integration Points
- **`dev test` needs no change in this phase.** Its `OP_VERIFY` and `OP_BLANK_CHECK` arms
  (`chip_test.py:2591`, `:3237`) already route through `check_eprom_blank` and `verify_eprom`, which
  Phase 202 rewired to `COMMAND_READ`. **Nothing in the app composes ordinal 4 or 6 today** — this
  was measured, and it is why removing the firmware surface breaks no host path. The 3-way verdict
  migration stays Phase 206's.
- **`mem_util_blank_check_region` keeps both remaining callers** — `eprom.cpp`'s write-init and
  `eprom.cpp`'s erase-end — and after D-01's collapse they take the direct-emit path they already
  take today. Phase 205 removes them.
- **`is_memory_cmd` feeds `rurp_pinmap_refuses`** (`rurp_pinmap_guard.h:52`), the JP5 pin-1 hazard
  gate. Removing 4 and 6 from the predicate means `rurp_pinmap_refuses(4)` becomes false — harmless,
  because a retired ordinal never reaches `configure_memory` where that guard runs, but state it
  rather than leave it to be noticed.

### Known traps that apply here
- **The branch-inventory golden's test 3 pins literal line numbers 71, 145 and 218.** D-01 deletes
  three lines from `configure_eprom` near the top of `eprom.cpp`, so **every one of those shifts**.
  Re-deriving the golden is not enough; the test's own pinned constants move too.
- **A pre-authored gate leg can be unreachable.** RED proves nothing until it is *seen* to fail for
  the intended reason. Both D-04 instruments need a planted-violation run.
- **`grep` in this devcontainer is ugrep and honours `.gitignore`**, so a census sweep can silently
  under-scan. And `grep -qF` with a dash-leading pattern exits 2, which makes a gate fail open.
- **Gate idioms that fail open** — BRE `\+\+\+`, `;`-chains, OR-grep, `grep -c`, `--stat`, unset-var
  `rev-list`. A new gate must not use them.
- **Run the app suite on Python 3.11**, not the devcontainer's 3.12 default — a green local run on a
  later interpreter has broken app CI before. Doubling pytest `-q` hides the count line; `addopts` is
  `-ra -q`, so use `-o addopts=""` when a count is needed.
- **`test_no_programmer_found_*` go RED with a live board attached.** `/dev/ttyACM0` (the Leonardo)
  is attached now, so those tests fail locally for a reason that is not a defect.
- **Firmware CI is `native` + `native_nodevtools` + `pytest tests/`**, and `firestarter_fw` has **two**
  test trees — `test/native/avr/` (Unity/PlatformIO) and `tests/*.py` (pytest). Both move here.
- **Worktrees leave submodules empty**, and a sibling worktree does not carry the editable install.
  Relevant to D-08 if any leg is tempted toward a worktree after all.
- **`test_flash_path_record_sync` asserts whole-repo porcelain** — commit before running it.
- **`fw --install` flashes the attached board and ignores `--board`.** One board is attached, so
  this is unambiguous here — but it means a `--board` argument in a bench script is inert and must
  not be read as targeting.
- **The host cannot see a firmware prerelease suffix.** `_probe_port`'s `[\d.x]+` regex truncates it,
  so the host cannot tell `b33` from `b34` from a post-204 build. D-07's substituted labels are
  therefore the only record of which firmware was on the board — the host will not tell you.

</code_context>

<specifics>
## Specific Ideas

- The operator chose the **full sweep over the literal requirement text**, accepting a gate
  re-anchor and a golden re-derive inside this phase rather than leaving a firmware that compiles a
  retired ordinal for one phase. The instruction behind it: a bisect between 204 and 205 should not
  land on a misleading state, and FWCMD-03's "reserved" record should be real rather than
  aspirational.
- The operator chose to **mirror FWBLANK-02's both-sides shape** for the reserved record rather than
  let the host keep markers — consistent with the standing rule that the two constant ladders move
  together.
- The operator chose the **free generic refusal over a minted message**, in a milestone whose premise
  is reclaiming flash, and chose to **keep 204 a two-repo phase** rather than pull meta-repo codegen
  into a bench-gated removal.
- The operator chose the **published `3.0.0b49` wheel** over a reconstruction for the old-host leg —
  REL-03 is a claim about what a real user sees.
- The operator chose **read-back equivalence on a socketed part**: the "no side effect" claim is to
  be observed on silicon, not argued from where the refusal fired.
- The operator **declined to fold in the `DONE` clean stop**, keeping the phase to its requirement
  set. CMP-F1 stays filed.
- The operator named **Rev 2.0** specifically when asked to disambiguate, then corrected the board
  itself mid-discussion: **a Leonardo, not an Uno-class board**, with the W27C512 already seated —
  and gave **standing permission to drive and flash it without asking**. The bench legs are
  therefore designed as an unattended sequence, not as an operator-assisted one.

</specifics>

<deferred>
## Deferred Ideas

- **The `DONE`-based clean stop in `op_wait_for_ack`.** Offered and declined (D-12). **Best home:**
  wherever the host's abort path is next opened — Phase 206 already owns the serial-session rework
  and would design "send DONE" alongside the leased session. Carry forward the finding that old
  firmware already ignores `DONE` gracefully, so the change is forward-compatible by construction.
- **A dedicated retired-command message** naming the version boundary instead of `Unknown command: 4`
  (D-05). **Best home:** Phase 207, which owns REL-04's wiki breaking-change page and would decide
  whether the wording deserves a catalog id once the version strings exist.
- **Retiring the orphaned `DBG_VERIFY_PROM` / `DBG_BLANK_CHECK_PROM` catalog entries** (D-06). Best
  home: any later phase already touching `tools/catalog/messages.toml`, where the codegen run and
  the two sub-repo syncs are already being paid for.
- **The firmware half of the negative-address todo** (`json_parser.c`'s `simple_strtoul` dropping the
  sign), carried forward from Phase 203's deferred list. Still **Phase 205**, which is dual-repo and
  bench-gated. 204 is dual-repo too, but its firmware change is a pure removal and this is a parser
  fix; folding it would blur what a bisect across 204 means.

### Reviewed Todos (not folded)

- `2026-09-20-preflight-firmware-version-compat-guard.md` — refuse a firmware whose feature version
  exceeds the CLI's. Adjacent to REL-03 and the general form of the same hazard, but host-only, its
  stated home is a `2.0.10` cut from `main` on the **stable** channel, and it is gated on the
  stable-3.0.0 promotion seed. Folding it would pull stable-channel release work into a beta-line
  firmware phase. **Read it before writing the REL-03 leg.**
- `new-host-old-firmware-0x05-page-size-skew.md` (`resolves_phase: unassigned`) — the other
  new-host/old-firmware skew, with a different mechanism (silent page-size corruption, not a refused
  ordinal). Not folded, but its caveat about `_probe_port`'s prerelease truncation bears on D-07's
  labelling and should be read.
- `2026-09-21-blank-check-sram-fram-shortcircuit-is-inert.md` and
  `2026-09-20-devtest-blank-check-folds-transport-failure-into-verdict-bad.md` — both are host-side
  `dev test` verdict issues. **Phase 206's** territory.
- `2026-08-30-write-init-blank-check-is-whole-device.md` (`resolves_phase: 205`) — unchanged by this
  phase; its firmware half stays with Phase 205.

`todo.match-phase 204` returned **50 of 50** pending todos, almost all on broad keyword overlap
(`cmd`, `command`, `phase`, `check`, `cpp`). Only the entries above had real scope overlap.

</deferred>

---

*Phase: 204-The command surfaces leave the firmware*
*Context gathered: 2026-09-21*
