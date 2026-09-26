# Phase 151: Protection Readability — `lock-status` - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-20
**Phase:** 151-protection-readability-lock-status
**Areas discussed:** Read source & firmware scope, Table shape & family key, Output/refusal/exit code, `protect_on_after`'s single home (all four offered areas selected)

---

## Read source & firmware scope

### Q1 — What "reports the protection state" means

| Option | Description | Selected |
|--------|-------------|----------|
| Host-only, curated answer | No firmware change; answer from the curated table, explicitly stating firestarter does not query silicon. Recommended by Claude on three grounds: v1.32 declared one firmware workstream (Phase 149, landed); leonardo at 1460 B free against a 0 B must-not-grow band; no bench phase, so a live read ships hardware-unvalidated. | |
| Host + firmware live read on 0x06/0x10 | The literal LOCK-02. New firmware command; `flash_util_get_chip_id` already does the neighbouring sequence. Costs a second firmware workstream, a third named MERGE-05 exemption, a cold triple-target re-measure, re-planted tripwires, dual-repo lockstep. | |
| Firmware read, but beta-only `dev lock-status` | Real silicon read registered only on a pre-release install via `_DevGroup` / `BETA_ONLY_DEV_COMMANDS`, so stable never sees it. Firmware bytes NOT avoided — channel gating is host-side only. | ✓ |

**User's choice:** Firmware read, beta-only `dev lock-status` — Claude's host-only recommendation overruled deliberately.
**Notes:** Claude verified before asking that `-D DEV_TOOLS` lives in `platformio.ini`'s shared `[env]` block (:26) and **is inherited by `uno`, `uno328pb` and `leonardo`** — correcting its own initial assumption that an `#ifdef` could make the firmware code free. Only `native_nodevtools` omits the flag. → CONTEXT D-01.

### Q2 — Which families the firmware read covers

| Option | Description | Selected |
|--------|-------------|----------|
| 0x06 + 0x05 boot-block | AMD Autoselect on 0x06 (190 rows) plus Winbond Product-ID boot-block on the 0x05 Winbond rows. Recommended because the operator owns a W29C040 whose locked 16K boot block is the still-open v1.17 RCA — the only option verifiable on real silicon today. | ✓ |
| 0x06 only | One sequence, smallest byte cost, largest readable class. Bench-validatable only if an Autoselect part is on hand. | |
| 0x06 + 0x10 | Both readable classes, 229 rows, so command coverage matches the table exactly with no unimplemented gap. Two sequences of firmware cost. | |
| All three | Full coverage of every documented-readable family; largest byte cost against a 0 B band, largest exemption to adjudicate. | |

**User's choice:** 0x06 + 0x05 boot-block.
**Notes:** Consequence surfaced immediately and carried forward: `0x10` (39 rows) becomes documented-readable-but-unimplemented, a **fourth** answer class distinct from both "not readable" and "unprotected". → CONTEXT D-02, D-09.

### Q3 — Bench leg

| Option | Description | Selected |
|--------|-------------|----------|
| W29C040 boot-block only | One operator-gated leg; operator seats the chip, Claude may drive the port. Recommended as a real oracle rather than a smoke test, on the grounds that v1.17 had established the expected answer. | ✓ |
| W29C040 + an Autoselect part | Adds a 0x06 part to exercise the path covering 190 of 229 readable rows on real silicon. | |
| No bench leg this phase | Native + host tests only; file bench validation as a todo. Both new sequences would reach beta unvalidated. | |

**User's choice:** W29C040 boot-block only.
**Notes:** ⚠ **Claude's stated grounds for this recommendation were subsequently found to be too strong, and the correction was surfaced before the next question.** `lockable-proms.md` §1 documents W29C040/W29C040P as *"Variant-dependent — Boot blocks or SDP — Must check the exact suffix and revision"* — **not** documented-readable. Only W29C020/W29C020C is `Yes—special` (Product ID mode, permanent). v1.17's locked-boot-block finding is **empirical** (write→verify failure), not a documented readable-status claim. The leg survives as an exploratory **probe**, not validation — see Q2 of the next area. → CONTEXT D-03.

### Q4 — Behaviour against firmware predating the command

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse the sdp_honesty precedent | Send it; map `MSG_ERR_UNKNOWN_CMD` → `FirmwareOutdatedError` naming `firestarter fw --install`, keyed on message id never text, as `map_unknown_cmd_to_outdated` already does for CMD_SDP_LOCK/UNLOCK. Exploits the one real wire asymmetry: an unknown COMMAND errors and is detectable, an unknown flag BIT is silent. | ✓ |
| Probe the version first, refuse before sending | Never touches the chip on unsupported firmware — but `_probe_port`'s `[\d.x]+` truncates the pre-release suffix, so it cannot distinguish the beta that has the command from the one that does not, and would refuse both. | |
| Both | Version-gate where conclusive, map the error as backstop. Two code paths and two test sets for one condition. | |

**User's choice:** Reuse the sdp_honesty precedent.
**Notes:** The helper is worded for `"SDP {mode}"`; it gets generalised or gains a sibling. → CONTEXT D-04.

**Continue check:** "Next area."

---

## Table shape & family key

### Q1 — Form of the LOCK-01 curated table

| Option | Description | Selected |
|--------|-------------|----------|
| Python module, sdp_capability.py shape | Literal table of string literals with each row's citation in a comment above it, mirroring how `SDP_CAPABLE_TOKENS` carries its provenance. No loader; gateable like its neighbour. | ✓ |
| Committed JSON under firestarter/data/ | Clean data/code separation with a `citation` field. Costs a loader, schema test and packaging config — and puts a hand-curated file beside the **generated** `chip_database.json`, a footgun for the next reader. | |
| Markdown table under doc/ | Citations read naturally; but two sources of truth with nothing keeping them equal. | |

**User's choice:** Python module, sdp_capability.py shape. → CONTEXT D-05.

### Q2 — The 0x05 fork, after the W29C040 correction

| Option | Description | Selected |
|--------|-------------|----------|
| Keep it; W29C040 leg is an exploratory probe | Implement the Product-ID read, gate the readable verdict to W29C020C only, run W29C040 as a probe recorded either way. Both outcomes useful: a plausible reading corroborates v1.17 from the read side; garbage vindicates the variant-dependent refusal. Framing must say probe, never validation. | ✓ |
| Drop 0x05, spend the bytes on 0x06 only | The sequence can only be properly validated on a W29C020C, not confirmed in inventory — so the bytes buy an unvalidated path. | |
| Keep 0x05 — do you have a W29C020C? | If a W29C020/W29C020C is in the parts drawer the sequence gains a genuine documented oracle and the calculus changes. | |

**User's choice:** Keep it; W29C040 leg is an exploratory probe.
**Notes:** The operator did not report owning a W29C020C, so the readable verdict on 0x05 is gated to that part while the bench probe runs against the W29C040 that is on hand. → CONTEXT D-03.

### Q3 — The family key

| Option | Description | Selected |
|--------|-------------|----------|
| Three-state tokens, fail-closed, name the alias | documented-readable / documented-not-readable / undocumented. Entry answers only if every alias is documented-readable; refusal names the specific alias and its state, so curating it later flips the entry with no rule change. | ✓ |
| Per-entry curated verdict, curator adjudicates | Lets the curator mark `W29C020,W29C020C,W29C022` readable by adjudicating W29C022 as a W29C020 variant, giving 0x05 a live production path. Introduces a claim lockable-proms.md does not make — the edge DATA-04 polices. | |
| Strict token unanimity, sdp_capability's exact rule | Cheapest to gate, maximally consistent; but cannot tell the user whether an alias is documented-unreadable or simply never documented. | |

**User's choice:** Three-state tokens, fail-closed, name the alias.
**Notes:** Grounded in a measurement made during discussion: the DB entries are `W29C020,W29C020C,W29C022` and `W29C040,W29C042`, and **`W29C022` appears nowhere in `lockable-proms.md`**. Accepted consequence: no 0x05 row answers by default. → CONTEXT D-06.

### Q4 — The probe escape hatch

| Option | Description | Selected |
|--------|-------------|----------|
| `--force` opt-in, table unchanged | Table keeps refusing; `--force` runs the sequence and labels the output an unadjudicated probe. Explicit opt-in is the strongest guard against the output reading as a guarantee, and `--force` already means "proceed past a safety refusal" on `id`/`blank`/`erase`, with FLAG_FORCE downgrading chip-ID mismatch to a warning in firmware. | ✓ |
| Fourth table state: probe-permitted | Runs with no flag; keeps every decision inside the audited table with its citation. But the whole honesty burden lands on wording and the user never opts in. | |
| Both — probe-permitted state AND `--force` | Strictest: an unadjudicated read needs a curated citation *and* a user opt-in. Most machinery for one bench leg. | |

**User's choice:** `--force` opt-in, table unchanged. → CONTEXT D-07.

**Continue check:** "Next area."

---

## Output, refusal & exit code

*(The command surface itself was already settled as beta-only `dev lock-status` in area 1, so this area covered the remaining four decisions. Claude had by this point derived eight distinct outcomes from the locked decisions and presented that count with the questions.)*

### Q1 — How the outcomes render

| Option | Description | Selected |
|--------|-------------|----------|
| Named class token + prose | Every answer leads with a machine-stable class name, then prose. The class name IS the honesty contract: tests assert the token rather than grepping wording, so a prose edit cannot silently collapse two classes and `unprotected` can never come from a path that did not read silicon. | ✓ |
| Prose only | Simplest surface; but LOCK-04's distinction then lives entirely in wording, testable only by full-text assertions — the syrupy-snapshot pattern this codebase already carries two of. | |
| Named class token + prose + `--json` | Adds structured output for `dev test` reports or a future diagnostic. Report-layer folding is itself out of phase scope. | |

**User's choice:** Named class token + prose.
**Notes:** `--json` and report folding captured as a deferred idea. → CONTEXT D-08, D-09.

### Q2 — Exit codes

| Option | Description | Selected |
|--------|-------------|----------|
| 0 only for a real silicon read | 0 when the chip was queried and a state came back; distinct non-zero for "cannot answer"; separate non-zero for operational failure. `$? == 0` then means exactly "I hold a real state". Class token still carries detail, so tests assert both together. | ✓ |
| 0 for every honest answer, including refusals | A refusal is the correct answer, so it succeeds; makes the class token the single source of truth. Cost: a script cannot distinguish answered from correctly-declined without parsing. | |
| Per-class distinct codes throughout | Maximally script-friendly with no parsing; but makes a correct `protected` read a non-zero failure, and this codebase already has exit-code precedence defects where `max()` picked the wrong verdict. | |

**User's choice:** 0 only for a real silicon read. → CONTEXT D-10.

### Q3 — Where the refusal prose lives

| Option | Description | Selected |
|--------|-------------|----------|
| Extend sdp_honesty.py | The designated honesty carrier; its existing caveat is already the right sentence for `not_readable`; no `click` dependency by design. Both its declared forward callers (Phase 134 report rows, Phase 135/150 relock) were deferred, so lock-status is the first to land. Cost: the module's name says SDP while carrying Autoselect and boot-block wording too. | ✓ |
| The curated table module owns its own prose | Verdict and explanation physically cannot drift apart; costs a second copy of the unreadable-state sentence. | |
| A new dedicated honesty module | Cleanest blast radius against the four existing honesty tests; most duplication, and two modules obliged to agree about one physical fact. | |

**User's choice:** Extend sdp_honesty.py. → CONTEXT D-11.

### Q4 — What enforces LOCK-04 mechanically

| Option | Description | Selected |
|--------|-------------|----------|
| DB-wide class invariant test | Walk all 746 entries, resolve each class, assert the partition exhaustively; assert `protected`/`unprotected` unreachable without a real read; assert every readable row carries a citation. Tests the mechanism not the prose — unsatisfiable by rewording, red when a new row lands in no class, does not rot on a sentence edit. | ✓ |
| Phase-local claim-gate script | A `151-check-claims.py` scanning output strings, per the `149-check-claims.py` / OUT-05 precedent. Flagged risk: the `check_permitted_claims.py` family has already failed OPEN once, its `_HERE` resolving to the checking phase's own directory. | |
| Both | Invariant test for misclassification, claim gate for wording. Two mechanisms for two distinct failure modes. | |

**User's choice:** DB-wide class invariant test. → CONTEXT D-12.

---

## `protect_on_after`'s single home (DATA-06)

### Q1 — Where the authoritative statement lives

| Option | Description | Selected |
|--------|-------------|----------|
| `doc/infoic-field-dictionary.md` | Add a `protect_on_after` / `protect_off_before` section beside the existing per-field entries, which already carry CONFIRMED/UNKNOWN status lines and feed the file's "build_db.py Known Bugs vs Correct Semantics" summary. The artifact whose declared job this is. Other two tables get a one-line pointer, so "documented once" means one statement not one mention. | ✓ |
| The LOCK-01 module's docstring | Co-locates with the protection subject matter in the module 151 creates, and 151 is the only phase permitted to write about the field. But a Python module is a surprising home for field provenance. | |
| A new dedicated advisory-fields doc | Unmissable, with an obvious home for future advisory fields. A fourth place discussing these bits, and a one-entry doc goes stale unread. | |

**User's choice:** `doc/infoic-field-dictionary.md`.
**Notes:** Claude established before asking that the upstream *bit* is already tabled in three places (`package-details.md:43`, `infoic-field-dictionary.md:120`, `protocol-flags.md:24`) but that all three document minipro's bit semantics — a different fact from the emitted field's runtime status, which is what DATA-06 is about. → CONTEXT D-13.

### Q2 — The sibling field

| Option | Description | Selected |
|--------|-------------|----------|
| Cover both siblings | One section, both bits, each with its own measurement. Documenting one and leaving its sibling silently dead reproduces the exact condition DATA-06 exists to end, and a reader finding one field explained will reasonably assume the neighbour IS consumed. | ✓ |
| `protect_on_after` only — DATA-06's literal scope | Provably scoped closure, which matters for Phase 152's claim gate; sibling gets a pending todo. | |
| Both, plus a todo for the undecoded bits | Also chases bit 22 (`0x00400000`, AT29C/W29C/W29EE group) and bit 9 (`0x200`, MX29F040 only) from the research note's loose ends. | |

**User's choice:** Cover both siblings.
**Notes:** Claude measured both fields against `chip_database.json` before asking: `protect_on_after` 70/746 (alg 5 → 27 of 27, alg 13 → 43); `protect_off_before` 148/746 (alg 5 → 27, alg 6 → 77, alg 13 → 43, alg 52 → 1). Neither has any runtime consumer — the only references in `firestarter/` are a comment at `sdp_capability.py:74` and two test files. → CONTEXT D-14, D-15.

---

## Claude's Discretion

The operator did not elect to discuss these; they are the planner's to decide, consistent with the locked decisions. Full statements in CONTEXT.md §Claude's Discretion.

- Wire protocol shape for the new firmware command (command number, response framing, single status byte vs per-region structure).
- Device-global vs per-sector/per-region reporting, and how a multi-region answer renders under a single leading class token.
- Which named MERGE-05 exemption funds the new firmware bytes, and its framing.
- How `permanence` is represented separately from `readability` in the table.
- Whether `protect_off_before`'s algorithm-6 correlation (77 rows, the Autoselect family) earns a sentence in the DATA-06 section.

## Deferred Ideas

- Fold lock state into `dev test` reports and/or add `--json` — own phase.
- A live protection read for `0x10` (39 rows) — ships as the `not_implemented` class.
- Curating `W29C022` to unblock the `W29C020,W29C020C,W29C022` entry — needs a datasheet, not an inference.
- Decoding `infoic.xml` bits 22 and 9 — declined here.
- `write --sdp-relock` — Backlog 999.28, deferred twice; Phase 152 must describe a withdrawal, never a migration.
- A compensating bootloader-safe flash guard — raised and declined during the concurrent quick task `260820-a7w` that removed the linker's protection over the bootloader region.

Twenty-four `todo.match-phase 151` matches were reviewed, all at a flat 0.6 (keyword noise). One was **folded** — `decode-infoic-flags-bits-14-15-protect-metadata.md`, whose emit half already landed and whose remaining interpretation guardrail is exactly what DATA-06 now writes. The rest are itemised in CONTEXT.md §Reviewed Todos.

---

## Process note

The discussion was interrupted mid-area-3 by an unrelated `/gsd-quick` request (firmware flash-limit guards, task `260820-a7w`). Progress was checkpointed to `151-DISCUSS-CHECKPOINT.json` before switching, and resumed from there. Two of Claude's own claims were corrected mid-discussion rather than left standing: the `#ifdef DEV_TOOLS` cost assumption (Q1 of area 1) and the W29C040 bench oracle (Q3 of area 1 → Q2 of area 2). Both corrections are recorded above at the point they occurred.
