# Phase 203: The write guard moves up a layer - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-21
**Phase:** 203-the-write-guard-moves-up-a-layer
**Areas discussed:** Todo folding, Who pays the read, The refusal line, `write --verify`'s contract, Three port opens

---

## Todo folding

`todo.match-phase 203` returned 45 of 48 pending todos, almost all on broad keyword overlap.
Four were presented as having real scope overlap.

| Option | Description | Selected |
|--------|-------------|----------|
| Negative write address | `2026-09-16` — `write -a -256` passes the host page-alignment guard and the firmware reads it as 0. This phase rewires the write path's region arithmetic. | ✓ |
| dev test UV write divergence | `2026-09-08` — `dev test` writes a non-blank UV part via `FLAG_SKIP_BLANK_CHECK` while `write` is refused, undisclosed. | |
| Dead branch in compare.py | `2026-09-20` (202-REVIEW IN-01) — `CompareAccumulator.feed()`'s `if not offs:` branch is unreachable. | |
| Read-abort window untested | `2026-09-20` (202-REVIEW WR-01) — the 3.0 s acceptance window is untested at its true failure boundary. | |

**User's choice:** Negative write address only.
**Notes:** The other three are recorded in CONTEXT.md § Reviewed Todos with the reason each was not
folded. The negative-address todo is folded **host half only** — its firmware half needs a
`firestarter_fw` change and this phase is app-only, bench-no.

---

## Who pays the read

Presented with a measured table of all six firmware write-init paths, showing that only
`0x07`/`0x08`/`0x0B`, `0x06` and `0x10` pre-flight a blank check today, and that `FLAG_CAN_ERASE` is
deliberately cleared for protocol `0x05` for a 12 V-on-a-5 V-part safety reason.

### Q1 — the exemption predicate

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve today's coverage | Guard exactly the families the firmware pre-flights today; SRAM/FRAM and `0x05` become named exemptions; WRITE-02 amended so the test pins the exact guarded set and fails on narrowing **or** widening. | ✓ |
| Flag, plus named exceptions | Keep `FLAG_CAN_ERASE` as primary, add two explicitly-reasoned carve-outs pinned by name. | |
| Literal `FLAG_CAN_ERASE` only | Hold the requirement verbatim; SRAM/FRAM and `0x05` writes to a non-blank part start being refused and need `-b`. | |

**Notes:** The literal option would have introduced a behaviour regression on three protocol families
the firmware has never checked. This is the same class of requirement/reality conflict that produced
Phase 202's D-15 (CMP-04 amendment).

### Q2 — region or whole device

| Option | Description | Selected |
|--------|-------------|----------|
| Region always | Read `address` → `address+len` on every guarded family; diverges deliberately from `flash_nor_unlock`/`flash_intel`'s whole-device check and lands the host half of the 2026-08-30 whole-device todo. | ✓ |
| Region, but per family | Mirror the firmware byte-for-byte — region for UV, whole-device for `0x06`/`0x10`. | |
| Whole device always | One rule, widest net — but breaks WRITE-06 outright. | |

### Q3 — unclassifiable protocol

| Option | Description | Selected |
|--------|-------------|----------|
| Fail closed — guard it | Follows `jp5_gate` / `sdp_capability`. Worst case is an unnecessary read plus a refusal `-b` clears. | ✓ |
| Fail open — exempt it | Follows `flash4_erase_gate`, whose docstring argues refusing an unclassifiable part is an availability regression. | |
| Cannot happen — refuse earlier | Treat it as a `resolve_chip` failure so neither polarity applies. | |

**Notes:** The two polarities coexist in the repo on purpose. CONTEXT.md D-05 requires the reason
this guard departs from `flash4_erase_gate` to be stated at the site.

### Q4 — where the policy lives

| Option | Description | Selected |
|--------|-------------|----------|
| New pure-predicate module | Fifth sibling to `jp5_gate.py`, `flash4_erase_gate.py`, `sdp_capability.py`, `page_size_gate.py`. Testable without a board. | ✓ |
| Inline in `write_eprom` | Reasoning physically at the call site, but policy becomes untestable without mocking an operator. | |
| Predicate module + CLI refusal text | As the module, with the refusal string in it too. | |

**Notes:** The third option's refusal-text idea was adopted anyway as CONTEXT.md D-12 — the choice
between options 1 and 3 turned out not to be exclusive.

**Decided without asking (mechanical, settled by "preserve today's coverage"):** `--skip-erase`
re-arms the guard on an erase-capable part, because the exemption's premise is that the erase ran.
`-f`/`--force` does not bypass the guard, matching today.

---

## The refusal line

Grounded in the exact current firmware wording, `Not blank, at 0x%06x, v: 0x%02x`
(`tools/catalog/messages.toml:556-565`).

### Q1 — wording

| Option | Description | Selected |
|--------|-------------|----------|
| Keep the firmware wording | Character-for-character, so bench records and gh issue reports stay greppable across the transition. | |
| Host-voiced, with remedy | Names the chip and the way out (`Use -b to write anyway`). | |
| Host-voiced, no remedy | Makes it unmistakable the **host** refused; keeps address and value; silent about `-b` per `flash4_erase_gate`'s stated reasoning. | ✓ |

**Notes:** Keeping the address and value is a deliberate, recorded exception to Phase 202's D-13
("no expected or actual byte values are printed"), which governs compare output. WRITE-01 requires
the value and the firmware has always carried it.

### Q2 — do the compare engine's extra lines print

| Option | Description | Selected |
|--------|-------------|----------|
| Refusal line only | The guard aborts at the first non-blank byte, so the range is one byte and the bucket would be classified from a one-byte sample — 202's D-09 trap at its worst. | ✓ |
| Refusal plus bucket | Gives `dev test` and issue reporters a classification for free. | |
| All three lines | Identical rendering to `verify`; one code path, one output shape. | |

---

## `write --verify`'s contract

### Q1 — exit codes

| Option | Description | Selected |
|--------|-------------|----------|
| 0/1/2 when `--verify` is given | `write` keeps 0/1; `--verify` opts the invocation into 202's contract. | (Claude) |
| 0/1/2 always | One contract per command, but changes plain `write`'s exit code on a dead board — what 202's D-11 explicitly declined. | |
| Keep 0/1 everywhere | Honours D-11 literally; a failed verify and a dead board both exit 1. | |

**User's choice:** "You decide."
**Notes:** Decided by Claude as **0/1/2 gated on `--verify`**. Reasoning recorded in CONTEXT.md D-13:
202's D-11 objected to changing exit codes with no requirement covering them; WRITE-05 covers the
`--verify` path and nothing covers plain `write`. The cost — one command with two contracts — is
accepted and must be stated in the `--verify` help text.

### Q2 — terminal wording under `--verify` (WRITE-05)

| Option | Description | Selected |
|--------|-------------|----------|
| One combined verdict | `--verify` suppresses the plain success line; one terminal line, and the word "successful" never appears on a `--verify` run. | ✓ |
| Success line, then verdict | Preserves the existing line for log-scrapers, but "successful" still prints on a failed run. | |
| Verdict replaces, keep the timing split | One line carrying both write and verify timings. | |

**Notes:** Chosen for the structural property — the forbidden word is absent from the path, so a
later edit to a failure line cannot reintroduce a WRITE-05 violation.

### Q3 — `--full`

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — same flag, same meaning | Scans the whole written region; a half-landed write is exactly the case that needs it. | ✓ |
| No — first mismatch only | Keeps the option surface small; run `verify --full` afterwards instead. | |
| Yes, and `--verify` implies it | No separate flag; always drain the read. | |

---

## Three port opens

### Q1 — which layer the guard runs at

| Option | Description | Selected |
|--------|-------------|----------|
| In `write_eprom` | Every caller inherits it, as the firmware guard always did. `dev write-cycle` erases first (exempt); `dev test` already passes `FLAG_SKIP_BLANK_CHECK` for its monotonic-masked UV targets, so its shortcut keeps working. | ✓ |
| In `cli_handlers.write` | CLI-only; simpler for the harness but drops coverage the firmware has today and widens the `dev test`-vs-`write` divergence. | |
| In `write_eprom`, CLI decides | Guard in the operator, opted into by an explicit parameter. | |

### Q2 — the session cost

| Option | Description | Selected |
|--------|-------------|----------|
| Accept and measure | Three cycles stand for one phase; record the added wall-clock so Phase 206's SESS-02 has a real before-figure rather than inventing its own baseline. | ✓ |
| Accept, don't measure | Strictly WRITE-01…06; 206 establishes its own baseline. | |
| Lease the session here | Collapse the three cycles now — pre-empts SESS-01 in an app-only, bench-no phase. | |

---

## Final check

Offered one further area before writing CONTEXT.md: `tests/fake_chip.py`'s `WriteInitPreflightChip`
overrides `EpromOperator.write_eprom` wholesale, which is exactly the method the guard now lives
inside — so every test using that double passes regardless of what the real guard does, and WRITE-06
and criterion 5 have no working harness yet.

**User's choice:** "I'm ready for context" — record it as a named trap and real work for the
researcher and planner, rather than designing the harness during discussion. Recorded in CONTEXT.md
§ Known traps.

## Claude's Discretion

- `write`'s exit-code contract under `--verify` (answered "you decide"; decided as 0/1/2 gated on
  the flag, reasoning recorded in CONTEXT.md D-13).
- Exact wording and capitalisation of the refusal line and the three `--verify` verdict lines.
- The predicate module's name, and allowlist-vs-predicate expression of the guarded set.
- Whether the guard read shows a progress bar.
- How the D-17 session cost is measured (bench run vs `tests/test_connect_cost_harness.py`).
- Refusal mechanism — typed exception through `map_typed_errors` versus a `False` return.

## Deferred Ideas

- Collapsing the three port opens into one leased session — Phase 206, SESS-01.
- The firmware half of the negative-address todo (`json_parser.c`'s `simple_strtoul`) — Phase 205.
- CLI-wide exit-code consistency for the other ~20 commands — backlog, carried from Phase 202.
