# Phase 110: Diagnostic Report Model + Dual Output + Provenance Prompts - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-02
**Phase:** 110-Diagnostic Report Model + Dual Output + Provenance Prompts
**Mode:** `--auto` — all gray areas auto-selected; each question resolved to the recommended default (no interactive prompts).
**Areas discussed:** Dual-render mechanism, Transport-health capture, Provenance component/ownership, DB-diff proposed-change

---

## Dual-render mechanism (RPT-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Composed `@dataclass` → JSON canonical, table = derived view | One `to_dict()` for the fenced JSON + one `render()` for the rich table, both reading the same dataclass fields; `schema_version` single-sourced constant in the dict | ✓ |
| Independent JSON dict + separate table row list | Assemble the machine dict and the human rows separately | |

**Auto choice:** Composed dataclass, single field source (D-01/D-02).
**Notes:** "No duplicated logic" is the RPT-01 contract — two parallel field lists silently drift. Table is never parsed back out of the JSON string. `rich>=14.0` already a dep; `_write_validation_matrix_artifact` is the json+md shape precedent.

---

## Transport-health capture (XPORT-01)

| Option | Description | Selected |
|--------|-------------|----------|
| No new instrumentation; best-effort + `"not measured"` sentinel | Capture only counters the serial/COBS layer already exposes; `transport-suspect` trips only on present+elevated counters; unavailable ⇒ explicit `"not measured"` | ✓ |
| Instrument `serial_comm.py` with new COBS/CRC/timeout counters | Add first-class transport counters this phase | |

**Auto choice:** No new instrumentation (D-03).
**Notes:** Instrumenting the serial hot path is scope creep and risks the milestone's zero-firmware-touch / SAFE-02 posture. App has no reliable first-class counters today (only a mostly-`0` per-cell `retry_count` in the validate-family harness). Honest `"not measured"` mirrors Phase 108's `indeterminate` bucket; a legitimately-empty transport section is an ACCEPTED outcome.

---

## Provenance component ownership + prompt set (RPT-04)

| Option | Description | Selected |
|--------|-------------|----------|
| Build model + prompt fn + `is_submittable` here; Phase 112 invokes | `Provenance` dataclass, prompt-collecting function, submittable predicate live in Phase 110; the handler calls them before the sweep | ✓ |
| Defer the whole provenance concern to Phase 112 | Only the report scaffold here | |

**Auto choice:** Model/component/predicate here (D-04/D-05/D-06).
**Notes:** Mirrors Phase 109's data-here/rendering-downstream split. Shield revision offers explicit **"not sure"** (never auto-derived from `hw_revision` — Bug A lesson); "not sure" is a *submittable* answer, only an unanswered/blank field blocks submission. Prompts use `rich.prompt` behind the mock-operator seam.

---

## DB-diff proposed-change (RPT-05)

| Option | Description | Selected |
|--------|-------------|----------|
| Advisory read-only proposed-disposition string | Show current `support_status` + a plain-language proposal derived from verdicts; never writes DB; taxonomy/transitions deferred to Phase 113/114 | ✓ |
| Emit a concrete target `support_status` value | Compute the actual next state | |

**Auto choice:** Advisory read-only proposal (D-07).
**Notes:** The report *surfaces* the diff; it never *is* the decision. A concrete target value reads as a decision and invites a future auto-write, blurring the Phase-114 human gate — rejected. Grounded in the milestone's founding no-auto-graduate constraint.

## Claude's Discretion

- Exact sub-dataclass names/decomposition (`AutoCapture`/`TransportHealth`/`DbDiff`/`Provenance`), constrained by D-01.
- `schema_version` starting value (recommend `"1.0"`), single-sourced + present in JSON.
- JSON representation of absent/NA fields (recommend `null` for scalars, `"not measured"` string for the transport-unavailable case).
- `transport-suspect` threshold numbers + which counters are actually reachable (research task under D-03).
- DB-diff proposed-disposition exact wording/branching within D-07's advisory/read-only bound.

## Deferred Ideas

None from discussion — stayed within phase scope. Adjacent concerns owned elsewhere: Phase 111 (VPP/VPE mV sampler), Phase 112 (`dev test` CLI surface + prompt invocation + render), Phase 113 (`--submit`), Phase 113/114 (`support_status` taxonomy + N≥2 promotion + no-auto-write lock).

Reviewed-not-folded todos (8, same off-axis set Phase 109 rejected) are recorded in CONTEXT.md `<deferred>`.
