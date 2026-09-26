# Phase 56: Snapshot + Field Dictionary + Corrected Docs - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-08
**Phase:** 56-snapshot-field-dictionary-corrected-docs
**Areas discussed:** Snapshot vehicle, Citation grounding, Dictionary home, Doc correction style

---

## Snapshot vehicle (GATE-01)

### Q1 — Store/consume the pinned snapshot?

| Option | Description | Selected |
|--------|-------------|----------|
| Vendor file, local-default | Commit full infoic.xml; build_db.py reads local by default, --refresh re-pulls | |
| Vendor + pin SHA in code | Same vendored file + recorded upstream commit SHA constant | |
| Commit-pinned URL | Fetch from a fixed commit SHA URL instead of master | |

**User's choice:** *Other (free text)* — "I dont want the infoic.xml file to be in the repo, it shall be downloaded in rebuild of the database"
**Notes:** Operator rejected all vendoring options. Flagged GATE-01 ("pin commit, commit in-repo") and GATE-04 ("no runtime fetch / byte-identical") tension before continuing.

### Q2 — What is the pin, and how does build_db.py fetch?

| Option | Description | Selected |
|--------|-------------|----------|
| Pin commit SHA, fetch by SHA | INFOIC_PINNED_COMMIT constant; fetch /-/raw/<sha>/; --refresh bumps it | |
| Fetch master, no pin | Keep fetching /master/ live each rebuild | ✓ |
| Pin SHA + cache locally | Pin SHA, fetch-and-cache to gitignored path, offline after first pull | |

**User's choice:** Fetch master, no pin
**Notes:** Live-master fetch confirmed. Surfaced the consequence: milestone loses its upstream-drift guard; GATE-01 literal wording overridden.

### Q3 — Where does the regression baseline come from?

| Option | Description | Selected |
|--------|-------------|----------|
| Snapshot the generated DB | Commit current chip_database.json as pre-milestone baseline; GATE-02 diffs against it | ✓ |
| No baseline — drop the gate | Accept live master, descope GATE-01/02/04 | |
| Capture both, decide at gate | Snapshot DB + record provenance SHA (not used to fetch) | |

**User's choice:** Snapshot the generated DB
**Notes:** Immutable anchor moves from input (XML) to output (DB). GATE-04 weakened to "deterministic given stable upstream" — flagged for Phase 59.

---

## Citation grounding (DEC-01)

### Q1 — How should dictionary citations reference minipro source?

| Option | Description | Selected |
|--------|-------------|----------|
| Commit-permalink URLs | GitLab permalinks pinned to a specific minipro commit SHA; no vendored source | ✓ |
| Path + line vs master | Plain file:line against master; drifts/rots over time | |
| Vendor pinned source | Commit a pinned snapshot of relevant minipro source files | |

**User's choice:** Commit-permalink URLs
**Notes:** Consistent with no-vendor stance. Claude added (no objection sought, low-value default): single recorded citation-commit SHA at the top of the dictionary, shared by all permalinks.

---

## Dictionary home (DEC-01)

### Q1 — Where should the authoritative field dictionary live?

| Option | Description | Selected |
|--------|-------------|----------|
| Companion markdown in doc/ | New firestarter_app/doc/infoic-field-dictionary.md; reviewable prose; code stays code | ✓ |
| Annotated build_db.py constants | Encode dictionary as commented Python constants/docstrings | |
| Both: doc canonical + code stubs | Markdown canonical + short pointer comments in build_db.py | |

**User's choice:** Companion markdown in doc/
**Notes:** Canonical authority Phase 57 cites; fits the DOC-01/02/03 doc family.

---

## Doc correction style (DOC-01/02/03)

### Q1 — How should the 3 docs be corrected relative to the dictionary?

| Option | Description | Selected |
|--------|-------------|----------|
| Surgical fix + cross-link | Correct in place, preserve structure, cross-link to dictionary | |
| Rewrite from dictionary | Rewrite all 3 fresh, derived from the dictionary | ✓ |
| Thin pointers to dictionary | Reduce docs to short intros deferring to the dictionary | |

**User's choice:** Rewrite from dictionary
**Notes:** Implies intra-phase ordering — dictionary first, then docs regenerated from it. Preserve the logo-header convention. Largest doc diffs but cleanest internal consistency.

---

## Claude's Discretion

- Exact path/filename of the baseline DB snapshot.
- Per-attribute table layout of the field dictionary.
- Whether the citation-commit SHA is mirrored as a comment in build_db.py.

## Deferred Ideas

- v1.11 input pinning / true offline-reproducible rebuilds (the original GATE-01/04 design) — intentionally not pursued; recorded for a future maintainer.
- `w27c512-eeprom-misclassification` todo — v1.11-relevant but a Phase 57/58 classification fix, not a Phase 56 snapshot/docs item. Dictionary should document correct erasability semantics so the later phase can fix it.
