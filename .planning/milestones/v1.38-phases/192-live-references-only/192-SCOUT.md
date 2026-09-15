# Phase 192 — pre-discussion scouting

**Produced:** 2026-09-13, by `/gsd-plan-phase 192` before it exited at the CONTEXT gate.
**Status:** evidence only. Not a CONTEXT.md, not a plan. `/gsd-discuss-phase 192` should treat
this as an inventory it does not need to re-derive, and settle the open fork at the bottom.

All counts below come from `/usr/bin/grep` (NOT PATH `grep`, which is ugrep here and honours
`.gitignore`) over `git ls-files` output, using the boundary pattern
`henols/firestarter($|[^_A-Za-z0-9])` so that `firestarter_app`, `firestarter_fw` and
`firestarter_prom` do not false-match.

---

## 1. SWEEP-01 — live tracked references to the bare slug

| File | Hits | Line(s) |
|---|---|---|
| `README.md` (meta) | 1 | 27 |
| `.planning/codebase/STACK.md` | 2 | 19, 145 |
| `.planning/codebase/INTEGRATIONS.md` | 3 | 18, 31, 154 |
| `.planning/codebase/ARCHITECTURE.md` | 2 | 344, 404 |
| `.planning/codebase/STRUCTURE.md` | 1 | 22 |
| `.planning/codebase/TESTING.md` | 1 | 56 |
| `firestarter/` (firmware sub-repo) | **0** | — |
| `firestarter_app/` (host sub-repo) | **0** | — |

**Both sub-repos are already clean.** Every `henols/` reference in them resolves to
`firestarter_fw`, `firestarter_app` or `firestarter_prom`. SWEEP-01's "both sub-repo READMEs"
clause was already satisfied by phases 189/190 — it needs proving, not fixing.

Branches checked: `firestarter` and `firestarter_app` both on `v1.38-repository-rename`.

## 2. SWEEP-02 — the D-5 protected set

173 tracked files under `.planning/milestones/` match the boundary pattern. None may be
modified. The acceptance test is `git diff --stat -- .planning/milestones/` over the
milestone range returning empty.

**Adjacent, and NOT covered by either SWEEP-01 or SWEEP-02:** roughly 60 further live tracked
meta files match — `.planning/phases/189..191/` plans, summaries and evidence,
`.planning/notes/`, `.planning/seeds/`, `.planning/todos/`, `.planning/debug/`,
`.planning/v1.3x/`, plus `ROADMAP.md` / `STATE.md` / `PROJECT.md` / `REQUIREMENTS.md`
themselves. Most of these quote the old slug **deliberately** — they are records of the rename,
or live planning documents whose subject is the rename. SWEEP-01 names a closed list and does
not reach them. Worth stating explicitly in CONTEXT.md so the sweep's blast radius is a
recorded decision rather than an executor's guess.

## 3. SWEEP-03 — the phantom workflow, and how far it actually spreads

`.github/workflows/` **does not exist in the meta repository.** `catalog-sync-check.yml` was
retired in `7d7179ec` ("fix(185-06): retire catalog-sync-check.yml (D-01, CLAIM-08)").
`wiki-check.yml` and `wiki-publish.yml` were retired in `5426d7ef`. `tools/` now contains
`catalog/` alone — `tools/wiki/` was removed 2026-09-08.

SWEEP-03 names `STACK.md` only. Success criterion 4 names four more. **Seven** documents
actually describe the retired workflow as live:

| Document | In SWEEP-03 / criterion 4? | Stale lines |
|---|---|---|
| `STACK.md` | yes (SWEEP-03) | 139, 145–146 |
| `ARCHITECTURE.md` | yes (criterion 4) | 251, 341, 396, 437, 438, 444 |
| `INTEGRATIONS.md` | yes (criterion 4) | 22, 27, 30, 130 |
| `STRUCTURE.md` | yes (criterion 4) | 63, 127, 171 |
| `TESTING.md` | yes (criterion 4) | 31, 33, 36 |
| `CONCERNS.md` | **no** | 61, 62, 100, 105, 117–119, 131, 162 |
| `CONVENTIONS.md` | **no** | 83 |

`STRUCTURE.md` carries two further retired-CI citations beyond the slug: lines 64–65 and 127
list `wiki-check.yml` and `wiki-publish.yml` as tracked, and line 73 lists `tools/wiki/` as a
tracked directory. All three are gone.

---

## Operator answers already given (2026-09-13, at the plan-phase gate)

Recorded here so they are not lost to a `/clear`. They are **inputs to discussion**, not
locked decisions — `/gsd-discuss-phase 192` owns turning them into `D-NN` rows.

1. **Sweep scope — extend to all seven `.planning/codebase/` documents.** Add `CONCERNS.md`
   and `CONVENTIONS.md` to the phantom-workflow correction, and strip the two retired wiki
   workflows (and `tools/wiki/`) from `STRUCTURE.md`. Rationale given: leave
   `.planning/codebase/` internally consistent in one pass rather than shipping a known-stale
   remainder.
2. **Research — skipped.** The reference surface is fully enumerated by the tables above; a
   researcher would mostly re-derive them. Re-run `/gsd-plan-phase 192 --research` if
   discussion turns up a question this note does not answer.

## Open fork for discussion

Extending to seven documents makes the plan **wider than SWEEP-03 as written**. Either
`SWEEP-03` in `REQUIREMENTS.md` is amended to match the real scope (keeping the traceability
table honest), or the extension rides as an unrequirement'd extra. The operator was offered
"extend, and add a requirement" and chose plain "extend" — confirm during discussion which of
the two is intended, because the requirements-coverage gate at plan time reads the written
requirement, not this note.
