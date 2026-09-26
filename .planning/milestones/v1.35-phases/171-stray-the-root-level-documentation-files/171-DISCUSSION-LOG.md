# Phase 171: STRAY — The Root-Level Documentation Files - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-01
**Phase:** 171-STRAY — The Root-Level Documentation Files
**Areas discussed:** SECURITY.md disposition, autocompletion destination, things.md disposition, provenance recording

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| SECURITY.md — policy or nothing | Delete outright, or write a genuine disclosure policy | ✓ |
| Autocompletion's destination | Wiki page, README section, or a short README section pointing at a wiki page | ✓ |
| things.md — delete or salvage | Delete the whole thing, or keep the Windows avrdude fact | ✓ |
| Provenance in MIGRATION-TABLE.md | Whether the three files get rows, including rows for deletions | ✓ |

**User's choice:** all four areas.
**Notes:** Three findings were presented as settled rather than asked — that nothing links to any of
the three files (so no link sweep is owed), that the Phase 69 audit already has a canonical home in
the meta repo, and that `firestarter/PINOUTS.md` + `firestarter/PROTOCOLS.md` are deliberate Phase 168
implementation references rather than strays. None was contested.

---

## SECURITY.md disposition

### Q1 — What happens to `firestarter_app/SECURITY.md`?

| Option | Description | Selected |
|--------|-------------|----------|
| Delete it | The audit record is already preserved in the meta repo; GitHub then shows no security policy, which is honest. Costs nothing, commits to nothing, satisfies LEGACY-05's second branch | ✓ |
| Real policy, app repo only | A genuine disclosure policy at the same path; commits to a reporting channel and an implied response, and leaves the other two repos with nothing | |
| Real policy in prom, linked from both | One canonical policy in the same shape Phase 172 uses for the tracker; catch is that GitHub only surfaces a repo's own SECURITY.md | |

**User's choice:** Delete it.
**Notes:** Presented with the measurement that `/gsd-secure-phase` writes to `${PHASE_DIR}/${PADDED_PHASE}-SECURITY.md`
and never to a repository root, so the file will not regenerate at the deleted path.

### Q2 — Does anything replace it for someone looking for where to report a vulnerability?

| Option | Description | Selected |
|--------|-------------|----------|
| Nothing — silence is honest | No policy is claimed anywhere because none exists; the README already points at the prom tracker for problems generally | ✓ |
| One line in the app README | A sentence in Contributing saying security reports go to the prom tracker; touches an artifact Phase 170 closed and arguably belongs to POLICY-01 | |
| Hand it to Phase 172 | Delete here, note security reporting as an open question for POLICY-01 | |

**User's choice:** Nothing — silence is honest.
**Notes:** Area closed in two questions; nothing further remained to decide.

---

## Autocompletion destination

### Q1 — Where does `autocomplete.md`'s content end up?

| Option | Description | Selected |
|--------|-------------|----------|
| Wiki page, `Shell-Completion` | Move essentially as-is under the D-03 naming convention, add to `_Sidebar.md` and link from `Home.md`; keeps the 118-line README a get-started page | ✓ |
| Condensed section in the app README | ~10 lines under Installation or Configuration; app-specific and install-adjacent, but drops the pipx, fish, PowerShell and migration detail | |
| Wiki page + one-line README pointer | Nothing lost and README stays short, but states the same fact in two places, which REPO-02 and FRONT-03 push against | |

**User's choice:** Wiki page, `Shell-Completion`.
**Notes:** All nine live wiki pages open with the same logo block and `---`, and `autocomplete.md`
already does, so the move is close to byte-for-byte.

### Q2 — Where does the "Migrating from a previous Firestarter" note live?

| Option | Description | Selected |
|--------|-------------|----------|
| Stays on `Shell-Completion` | Where someone fixing a broken completion line is standing; `Breaking-Changes` is version-anchored and this change has no anchor in the source text | ✓ |
| Move it to `Breaking-Changes` | It is literally a change requiring action on upgrade, but would need a version heading that does not exist | |
| Both — note there, detail here | Discoverable from the upgrade page without duplicating detail, but still needs an invented version heading | |

**User's choice:** Stays on `Shell-Completion`.
**Notes:** The underlying swap landed in `firestarter_app` `3224f7e` (2026-05-28). Recorded as
provenance, explicitly not as a `Breaking-Changes` version anchor.

---

## things.md disposition

### Q1 — What happens to `things.md`?

| Option | Description | Selected |
|--------|-------------|----------|
| Delete outright | Its one fact is already on `Home` ("also ships inside the Arduino IDE and PlatformIO"); LEGACY-04 permits deletion and decision 4 argues against building a section around a third-party page | ✓ |
| Salvage the link onto `Home` | Alive today (HTTP 200), but becomes an external link the project implicitly vouches for, and 167's D-11 declined external link-liveness checking | |
| New `Installing-avrdude` wiki page | All three platforms with the hackaday link as further reading — authoring new content from a five-line source, which decision 4 rules out | |

**User's choice:** Delete outright.
**Notes:** The `hackaday.io` link was checked live before the question was put and returns HTTP 200,
so the choice was made knowing the link is not already dead.

---

## Provenance recording

### Q1 — Do these three files get rows in `.planning/v1.35/MIGRATION-TABLE.md`?

| Option | Description | Selected |
|--------|-------------|----------|
| All three, in the fitting section | `Shell-Completion` joins the main table as a Phase 171 row; `things.md` and `SECURITY.md` go in a "removed, never published" section beside the existing retired-pages section | ✓ |
| Only the wiki page | Reads the table strictly as "where every wiki page came from"; a future reader would have to find the right phase record to learn `things.md` was deleted deliberately | |
| No rows — it's Phase 168's record | Cheapest, keeps the table's scope tight, but the 999.9 rename sweep never sees `autocomplete.md`'s old path | |

**User's choice:** All three, in the fitting section.
**Notes:** Measured before the question: all three files are byte-identical at `d56424e`, the
branch-point SHA every existing Phase 168 row already cites, so the rows introduce no new SHA-column
semantics.

---

## Claude's Discretion

- Exact wording of the two new deletion rows in `MIGRATION-TABLE.md` and the heading of the new section.
- Placement of `Shell-Completion` within `Home.md`'s Reference list and within `_Sidebar.md`.
- Commit granularity for the deletions and the wiki page.

## Deferred Ideas

- `MIGRATION-TABLE.md` lists `Protocol-Flags` and `Protocol-ID` as current wiki pages; a fresh clone
  of the live wiki has neither. Table drift from the operator's post-168 reorganisation, raised as an
  out-of-scope observation and not acted on.
- A real security disclosure policy, if a reporting channel is ever chosen — and a `henols/.github`
  repository if it should cover all three repos.
- A security-reporting sentence in the app README, left to Phase 172 (POLICY-01).
- An `Installing-avrdude` wiki page, if Windows install support is ever asked for.
