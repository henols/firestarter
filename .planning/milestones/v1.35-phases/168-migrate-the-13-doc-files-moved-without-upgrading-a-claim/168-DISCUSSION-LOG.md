# Phase 168: MIGRATE — The 13 `doc/` Files, Moved Without Upgrading a Claim - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-30
**Phase:** 168-MIGRATE — The 13 `doc/` Files, Moved Without Upgrading a Claim
**Areas discussed:** Claim-diff unit & snapshot, The two clone-based gates, De-GSD-ification blast radius, Link-repair target & the generated DB

**Session note:** This is the **re-run** called for by `notes/v135-wiki-only-reversal.md` step 3.
The first attempt at `/gsd-discuss-phase 168` (2026-08-30, earlier the same day) halted before
CONTEXT.md was written when the operator reversed the milestone's wiki authoring model mid-session.
Four decisions taken in that halted session survive the reversal and were carried forward from the
note rather than re-asked (claim gates move to the meta repo; only the doc legs move;
`test_dispatch_mirror.py` relocates and finally runs; gates take the `tools/wiki/`
standalone-checker shape).

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Claim-diff unit & snapshot | Criterion 4 / HONEST-01 — what a "claim-bearing statement" is, where the pre-deletion snapshot lives, one-shot vs durable | |
| The two clone-based gates | Criteria 5 + 8 — HONEST-02 truth check and WIKI-05 navigation check, now the only automated guard on wiki content | |
| De-GSD-ification blast radius | Criterion 6 / LEGACY-06 — 2 named files vs the 6 files carrying `.planning/` pointers vs all 41 phase mentions | |
| Link-repair target & the generated DB | Criterion 2 / MIGRATE-04 — what a repaired reference points at, and the generated `chip_database.json` rows | |

**User's choice:** *No preference* — all four areas driven by Claude.
**Notes:** Read as a signal to drive rather than to skip. All four were worked through against the
measured tree; calls settled by precedent or by facts already on the ground were made directly and
recorded in CONTEXT.md with rationale, and only the three operator-shaped decisions below were put
back to the operator.

---

## Claim-diff unit & snapshot (HONEST-01, criterion 4)

**Decided without asking:** the unit is a **claim-token multiset** over a checked-in vocabulary
(D-01) — a text diff is unusable because the migration necessarily edits titles, links and framing.
The snapshot is a **git SHA per row in `MIGRATION-TABLE.md`** (D-02), not a committed copy, because
a committed 2,425-line copy of the documents would itself be the in-repo mirror WIKI-02 forbids.
The vacuous half is reported as vacuous in the checker's own output (D-04).

**Put to the operator — the gate's lifetime:**

| Option | Description | Selected |
|--------|-------------|----------|
| One-shot in-phase proof | Run during migration, demonstrate failing, commit output as evidence, retire. HONEST-02 is the standing truth gate. Cost: nothing stops a later wiki edit quietly softening a claim the 2026-08-30 docs made. | ✓ |
| Durable scheduled gate | Keeps asserting the wiki still says everything the frozen snapshot said. Cost: red on any legitimate restructure, and a check red for innocent reasons gets ignored — the `catalog-sync-check.yml` failure mode, 5 runs 5 fails. | |

**User's choice:** One-shot in-phase proof.
**Notes:** The accepted cost is stated explicitly in CONTEXT.md D-03 rather than left implicit. A
possible future middle path — a claim-token *floor* rather than multiset equality, which tolerates
restructuring while still catching a deleted hedge — was recorded as a deferred idea.

---

## The two clone-based gates (HONEST-02 criterion 5, WIKI-05 criterion 8)

**Decided without asking — not put to the operator.** These are design calls constrained by
measured facts and by the existing tooling's shape.

| Question | Options weighed | Call |
|---|---|---|
| One checker or two? | Fused (one red) vs split (distinguishable reds) | **Two checkers, one workflow, one shared clone** (D-05) |
| WIKI-05's mechanism | New checker vs repointing `wiki.py links` | **Repoint `links` at the clone, keep Home-only reachability, add a sidebar-completeness leg** (D-06) |
| HONEST-02's shape | New pytest harness vs `tools/wiki/` standalone script | **Standalone `python3`, 0/1/2 exit contract, `selftest.sh` driven** (D-07) |
| The stamp's version token | "DB vN" as the requirement words it | **Impossible — no version field exists in `chip_database.json`. Content hash + date instead** (D-08) |
| Scope of assertion | Check every claim on every page vs stamp-plus-resolve | **Stamp-plus-resolve, three legs incl. stale-vs-wrong distinction** (D-09) |
| Trigger and proof | Cron only, dispatch only, fixture only | **Weekly schedule + dispatch; demonstrated failing on a fixture clone AND run once live** (D-10) |

**Notes:** The D-08 finding is the significant one — `chip_database.json` is a 59-key vendor-keyed
object with no version field anywhere, so HONEST-02's requirement text is unsatisfiable as literally
written. Recorded as a stated substitution rather than papered over. Measured claim density across
the 12 files (11 of 12 carry per-chip or per-protocol claims; `PROTOCOLS.md` alone asserts 28 part
numbers and 34 algorithm values) is what rules out exhaustive verification and forces the stamp path.

---

## De-GSD-ification blast radius (LEGACY-06, criterion 6)

**Put to the operator** — it crosses activation decision 4 ("relocate and correct only"), which was
his call.

| Option | Description | Selected |
|--------|-------------|----------|
| All unopenable paths + full de-framing of the 2 | Every `.planning/` pointer in all 12 files removed or rewritten; the 2 named files lose titles, audit-trail lines, and sram-nvram's three `[CITED: …]` markers. "as of Phase 121" prose stays. | ✓ |
| Strictly the 2 named files | Narrowest reading, smallest claim diff. Cost: `PROTOCOLS.md` — 556 lines, the biggest page — ships publicly with 5 unopenable pointers and 22 phase mentions. | |
| Full de-GSD-ification of all 12 | All 41 phase mentions go. Cleanest public read. Cost: this is rewriting, not relocating — crosses activation decision 4, and every edit is noise in the criterion-4 claim diff. | |

**User's choice:** All unopenable paths + full de-framing of the 2.
**Notes:** The operating rule recorded in CONTEXT.md is **"can a public reader act on this?"** — an
unopenable `.planning/` path fails it and repairing it is *correcting*; a phase number inside a
sentence does not. Measured spread is 6 files / 15 references, three times what LEGACY-06 names.
Also decided without asking: **both named files ship, rewritten** rather than being dropped (D-12) —
each carries real operator-facing safety content (the `DIP24_2816` 5V-only / no-VPP guarantee; the
NVRAM blank-check limitation), and LEGACY-06 permits either outcome.

---

## Link-repair target & the generated DB (MIGRATE-04, criterion 2)

**Decided without asking, except the source comment.**

| Question | Call |
|---|---|
| What a repaired reference points at | **Page title, not URL**, everywhere except the two READMEs — Backlog 999.9 renames all three repos and invalidates every URL this milestone writes (D-13) |
| The 18 generated database references | **Fix `build_db.py:569` and regenerate + re-baseline**; the JSON is never hand-edited (D-14) |
| `firestarter/CLAUDE.md` ×5 | **The lockstep-maintenance rule against `SHIELD-REVISIONS.md` §4 must survive, repointed** — dropping it silently retires a real maintenance invariant (D-16) |
| The two READMEs | **Repaired in 168 anyway**, even though 169/170 rewrite them — criterion 2 demands it and 168 is where `doc/` dies (D-17) |
| Historical / archive records | **Excluded from repair, explicitly and by name** — repairing a historical record destroys the evidence it holds (D-18) |

**Put to the operator — the source comment:**

| Option | Description | Selected |
|--------|-------------|----------|
| Delete the comment | Consistent with the no-comments-in-source hard rule. Provenance moves to the wiki page, where the truth now lives. Cost: nothing in the header says where the constants came from. | ✓ |
| Repoint it to the wiki page by title | Keeps provenance next to the constants it justifies. Cost: keeps a comment in source, which the rule says goes — and Claude would be the one editing it. | |

**User's choice:** Delete the comment.
**Notes:** `firestarter/include/proto_constants.h:14` cites `firestarter/doc/PROTOCOLS.md` as truth
for an operator-approved constant set. The rule and the vanishing path point the same way.

---

## Claude's Discretion

The operator answered the three decisions that were genuinely his — HONEST-01's lifetime (D-03), the
de-GSD-ification boundary against his own activation decision 4 (D-11), and the source comment
against his no-comments rule (D-15). Everything else was decided from measured facts and recorded
precedent, and is marked in CONTEXT.md as **locked but revisable on evidence** rather than
operator-locked: D-01/D-02/D-04, D-05…D-10, D-12, D-13/D-14/D-16/D-17/D-18, D-19…D-22.

Two items were deliberately left open for research and planning:

- **Wiki push authentication** — whether `GITHUB_TOKEN` with `contents: write` can push to
  `.wiki.git` or a PAT secret is required. Only the clone (read) path is needed by CI.
- **Page-name resolution for the two hyphen hazards** — `AT28C04-ADAPTER.md` (part number already
  containing a hyphen) and `sram-nvram-behavior.md` (reads naturally with a slash).
  `MIGRATION-TABLE.md` already flags both and forbids the U+2010 look-alike workaround.

Also decided without asking, and worth flagging because it was not on the original gray-area list:
**two pages on the live public wiki are currently false.** `How-This-Wiki-Is-Published` states the
in-repo-is-authoritative rule and warns that wiki edits are overwritten on publish; `Home.md` links
to that claim, says the wiki is published from `beta`, and lists the twelve incoming pages by raw
source filename rather than by their eventual page names. Both are rewritten in this phase (D-21,
D-22) rather than deferred.

## Deferred Ideas

- **A durable anti-erosion gate for HONEST-01** — as a claim-token *floor* rather than multiset
  equality, if wiki-side claim erosion later proves real.
- **Exhaustive per-claim verification of all 11 claim-bearing pages** — out of reach here; the stamp
  path (D-09) exists because of it.
- **The compatibility matrix, family pages, algorithm pages and tutorials** — FUT-W-01…05, deferred
  at activation.
- **Re-sweeping every wiki URL after Backlog 999.9's repository rename** — the accepted sequencing
  hazard; D-13 minimises the blast radius but 169, 170 and 172 still need it.
- **External link liveness checking** — deferred at 167 and still deferred; the 6 dead issue links
  are Phase 172's work via a deterministic grep.
- **`sync_to_subrepos.sh` runs `diff -q $X $X` twice** — surfaced by `todo.match-phase 168`. The same
  defect class this phase's criteria are written against (a check that can only ever be green), but
  it lives in the catalog sync tooling, not the wiki tooling. Not folded — scope creep.
