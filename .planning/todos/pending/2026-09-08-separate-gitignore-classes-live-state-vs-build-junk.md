---
created: 2026-09-08T00:00:00Z
title: Separate the .gitignore classes — live state and bench measurements must not sweep with build junk
area: meta
files:
  - .gitignore (lines 78-79 pin state.json and milestone.lock)
  - .planning/state.json, .planning/milestone.lock (live GSD state, ignored)
  - .planning/milestones/v1.34-artifacts/bench/cells/**/reads/*.bin (4.0M of hardware measurements, ignored)
  - .planning/notes/disposable-artifact-inventory.md (the evidence)
---

## Problem

`.gitignore` currently mixes three kinds of thing that happen to share one mechanism:

1. **Regenerable build junk** — `__pycache__`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`,
   `.cache-uv`, `graphify-out/`, the duplicate `.planning/graphs/graph.json`.
2. **Live state** — `.planning/state.json` and `.planning/milestone.lock`, ignored at
   `.gitignore:78-79`. Losing these loses session position, and `state.json` scrapes the STATE.md
   **body** rather than frontmatter, so it is not trivially reconstructible from the record.
3. **Irreproducible measurements** — `.planning/milestones/v1.34-artifacts/bench/cells/**/reads/*.bin` (4.0M:
   `run_NN.bin`, `written.bin`, per cell per arm). These came off physical hardware. No sha or
   rebuild recreates them.

Because all three are equally invisible to `git status`, the obvious cleanup gesture —
`git clean -Xdf` — silently destroys classes 2 and 3 while doing the intended job on class 1.
This is a live footgun, not a hypothetical: the whole point of the reclaim work is to run
exactly that kind of sweep.

## Approach

Options, in rough order of preference:

1. **Comment-segment `.gitignore`** into the three classes with explicit headers, so the file
   itself warns a reader that `-X` is unsafe here. Cheapest, zero behaviour change.
2. **Add a `tools/` clean script** that removes only class 1 by explicit path, so there is a
   correct gesture to reach for instead of `git clean -Xdf`. Note the existing precedent that
   `firestarter_app/tools/` sits outside every CI gate — anything added under a `tools/` dir gets
   no mypy, no ruff check, no ruff format. Keep it a shell script or accept that.
3. **Consider tracking the v1.34 bench reads** rather than ignoring them. They are 4.0M of
   evidence for a closed milestone whose `EVIDENCE.md` cites the paths. Ignoring measurement data
   that a record depends on is the actual root cause here. Weigh against `.planning/` already
   being 186M.

Option 3 is the real fix and the one worth deciding on; 1 and 2 are mitigations.

## Acceptance

- [ ] A reader of `.gitignore` can tell which entries are safe to `git clean` and which are not.
- [ ] Whatever the decision on option 3, it is recorded — including a plain "we accept the risk"
      if that is the call.
- [ ] If a clean script lands: running it leaves `.planning/state.json`,
      `.planning/milestone.lock`, and every `.planning/milestones/v1.34-artifacts/bench/**/*.bin` in place, verified by
      a before/after count.
