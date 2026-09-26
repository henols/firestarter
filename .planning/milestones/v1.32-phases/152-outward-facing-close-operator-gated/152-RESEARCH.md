# Phase 152: Outward-Facing Close (operator-gated) — Research

**Researched:** 2026-08-21
**Domain:** Outward-facing record correction + a fail-provable claim gate over public text; three-repo
beta merge/cut mechanics; GitHub issue-comment and release-body publication.
**Confidence:** HIGH on everything measured today (every number below carries its command and date).
LOW on nothing — but **six CONTEXT.md data have MOVED** and one CONTEXT claim is **disproven**. Read
§"Re-Verification Deltas" before anything else.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

`152-CONTEXT.md` (685 lines, gathered 2026-08-20) carries D-01…D-15 as **locked decisions**. They are
not re-litigated here. This section names them so the planner has them in one place; the reasoning
lives in CONTEXT.md and must be read there.

### Locked Decisions

- **D-01** — Comments are posted inside this phase; release notes are authored **version-agnostic**
  (the tag is filled in at cut time, never predicted). Superseded in *sequencing* by D-04.
- **D-02** — **Only the v1.32 cut gets bodies.** One app body, one firmware body. `b16`–`b22` stay
  bodiless, an accepted cost recorded not hidden. The `b14` notes are historical and published: they
  are **not** rewritten; the correction lands in the new notes.
- **D-03** — **Per-artifact blocking operator gate, agents post.** A separate blocking checkpoint
  immediately before each post, so approval for gh#12 cannot carry to gh#11.
- **D-04** — **Phase 152 owns the beta merges, then posts everything.** PRs to `beta` in all three
  repos (never direct merges), let CI cut, **read** both versions from `gh release list`, then post
  three comments and both release bodies. `git cherry`, not SHA ancestry. `gh workflow run` is blocked
  by the auto-mode classifier — any manual dispatch is operator-only.
- **D-05** — Criterion 2's OPEN list is amended to **gh#21, gh#11, gh#12** (gh#32 is CLOSED).
  `REQUIREMENTS.md`'s OUT-01 and OUT-04 bullets are stale and are corrected in the same class.
  **Hand-edit** ROADMAP.md and REQUIREMENTS.md — the `gsd-tools` verbs run `_normalizeMd` whole-file.
- **D-06** — The AT28C256 erase contradiction is stated outward, backlogged, and its premise corrected
  in the record. **No code change in 152.** *Do not re-derive; do not soften.*
- **D-07** — The write/erase policy became **Phase 153**. *(Shipped — see §"What Phase 153 Shipped".)*
- **D-08** — **Phase 153 runs BEFORE Phase 152.** By the time 152's notes are written, `0x0D` erase
  and the write-path policy **are shipped**, while `write --sdp-relock` still is not.
- **D-09** — Two invocation modes, one pattern table: **file mode** (default, hard-coded
  `_DEFAULT_TARGETS`, offline, CI-runnable) and **posted mode** (opt-in, network, re-fetch the live
  body and run the *same* patterns). A blob SHA proves intent, never storage; `updatedAt` is not a
  body-edit oracle. Env seam **`FIRESTARTER_CLAIMSCAN_TARGETS_152`**. The `"152-"` self-check literal
  in **both** the `startswith` call **and** its failure message.
- **D-10** — The Phase 153 capabilities are permitted with **NO per-claim caveat requirement**
  (operator decision, concern raised twice and resolved via D-11).
- **D-11** — Criterion 5's pairing clause is **narrowed, not deleted**: scoped to claims about `0x0D`
  **write-path correctness or validation status**, exempting statements of shipped, user-visible
  command behaviour. **The five FORBIDDEN classes are UNTOUCHED and the amendment cannot reach them.**
  Each release-note body carries the milestone-level non-claim **once**.
- **D-12** — `152-LEDGER.md` is produced **AND** is a hard-coded gate target. Given D-11's narrowing,
  **the ledger is where the per-claim pairing discipline now lives.**
- **The planted violation is already specified by criterion 5** and is not a discretion item: the
  pre-amendment criterion-1 wording naming `enable` as returning via `write --sdp-relock`. The gate
  must be **seen to reject it** before any pass is believed.
- **D-13** — `lock-status` is announced **with the refusal as the feature**. Beta-only,
  matched-firmware-required. The W29C040 run was an exploratory **probe**, never validation.
- **D-14** — OUT-01's reply **ADAPTS** `137-GH12-COMMENT.md`, with the diff committed. Keep its
  *"the two halves don't survive equally"* framing and its *"This isn't the 'enable/disable' you asked
  for"* paragraph. Add: the **second** withdrawal spanning two releases, Backlog **999.28** by name,
  `lock-status`, and Phase 153. **Omit** a process-failure narration.
- **D-15** — In-repo record corrections: PROJECT.md's *"one firmware-touching workstream"* → three;
  PROJECT.md's workstream table gains a row for 153; Phase 121 D-12's disproven premise corrected in
  `.planning` by 152. The **code comment** at `database.py:591` is left to Phase 153.

### Claude's Discretion

Still open to the planner, per CONTEXT.md §"Claude's Discretion":

1. The exact `_DEFAULT_TARGETS` list. *(Resolved below — §C-6.)*
2. The fixture-suite shape and the plant-and-revert transcript artifact name. *(Resolved — §C-7.)*
3. Plan/wave shape given three repo merges, five gated posts, one-writer-per-file. *(Resolved — §F.)*
4. What `/gsd-complete-milestone` is left holding, and how the handoff is recorded so nothing
   re-merges. *(Resolved — §E-5.)*
5. Whether the firmware release notes say anything about the `.hex` assets and the leonardo ceiling.
   *(Resolved — §G-2. **Measured: there are FOUR assets, not three.**)*
6. Whether `152-LEDGER.md` or a separate correction register carries the D-05/D-11/D-15 amendments.
   *(Resolved — §G-1.)*

### Deferred Ideas (OUT OF SCOPE — ignore completely)

- Split or trimmed AVR firmware builds to relieve the leonardo ceiling — **its own phase; do not fold
  into 152.**
- Backfilling `b16`–`b22` release bodies, including posting `146-RELEASE-NOTES-app.md`/`-fw.md` to
  `b21`. Declined by D-02.
- A `--json` output mode for `lock-status`; folding lock state into `dev test` reports.
- A live protection read for protocol `0x10` (ships as `not_implemented`).
- Curating `W29C022`.
- Obtaining the Atmel *Software Chip Erase* application note. **NOTE: Phase 153 obtained/used the
  AN 0544B sequence — see §B-3. This deferred item is DISCHARGED.**
- **`write --sdp-relock`** — Backlog 999.28. Not this phase, not Phase 153. A future promotion **must
  reverse OUT-05's fifth gate class in the same change that lands the feature.**
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description (from REQUIREMENTS.md, **as amended by ROADMAP.md**) | Research Support |
|----|------------------------------------------------------------------|------------------|
| **OUT-01** | The owed gh#12 reply is posted. Half-answered, **for a second release**: `disable` survives as `write`'s automatic auto-unlock (declinable via `--skip-sdp-unlock`); `enable` returns as **nothing** — Backlog 999.28. Must NOT name `write --sdp-relock` as shipped. | §D-1 (the exact 2026-07-30 claim to retract, at char-level); §D-2 (a **second, later** 2026-08-06 comment CONTEXT does not mention); §C-4 (why this file should never contain the literal command string); donor read in full (§Code Examples). |
| **OUT-02** | gh#21 (with #32 folded) carries a comment: what changed, what remains unproven, and a request for a fresh `dev test` run **answerable because the report now identifies its firmware**. OPEN list amended by D-05 to gh#21/#11/#12. | §D-3 — gh#21's own report body carries `"fw_board_identity": null` and `"host_version": "3.0.0b15"` **verbatim and citable**, plus the exact erase-NA reason string Phase 153 falsified. §A-1 confirms that defect is still live on `origin/beta`. |
| **OUT-03** | gh#11's 2024 report is answered in terms of the FIX-06 completion-vs-data-landed conflation. | §D-4 — **CONTEXT's "unanswered" is imprecise**: the 2026-08-03 `CMD_ERASE` question was answered *with a promise* ("I will soon get it pushed and I will keep you posted"). 153 discharges the promise. Reframes the reply. |
| **OUT-04** | Release notes announce **`lock-status`** as shipped in the version that contains it, correct the forward-looking wording v1.30 left behind, and state the `write --sdp-relock` withdrawal explicitly — naming Backlog 999.28. | §E — CI mechanics, both `body:`-less workflows, **PyPI is now automatic (a CONTEXT delta)**, and the **2.0.8 GitHub/PyPI divergence measured live today**. §G-2 — four `.hex` assets, re-measured leonardo ceiling. §A-6 — the exact `b14` sentence to correct. |
| **OUT-05** | A **fail-provable** claim gate rejects AT28C silicon validation, page-size-on-silicon validation, a `0x0D` graduation, a `support_status` change, **or `write --sdp-relock` as shipped/available**; every permitted `0x0D` claim paired with its explicit non-claim. | §C — the full gate design, **with the fifth-class regex derived and empirically proven 11/11 reject + 7/7 allow today**, and a **second, undocumented collision found** (`issue-closed` vs D-05). |
</phase_requirements>

---

## Summary

Phase 152 is a **records-and-publication** phase with no product code in it. Its technical content is
three things: (1) getting three repos merged to `beta` and reading what CI cuts, (2) authoring five
pieces of public text that are true at the moment they become public, and (3) building one machine
gate that can be *seen to reject* a specific planted overclaim before any of that text ships.

The research work the planner could not do from CONTEXT alone was measurement. **Six CONTEXT.md data
have moved and one CONTEXT.md claim is disproven.** The largest movers: the app milestone branch is
now **85 ahead / 7 BEHIND** `origin/beta` (CONTEXT said 67 ahead, silent on behind — the merge is not
a fast-forward and `git cherry` shows 5 commits already upstream by patch-id); the leonardo flash
figure moved from 27500 to **27630** with the Caterina headroom from 1172 to **1042 B** and the
MERGE-05 allowance from +594 to **+724** across **four** named exemptions; PyPI's stable is **2.0.7
while GitHub's is 2.0.8** — a live, un-noted channel divergence; and the app's PyPI upload is now
**automatic**, not manual dispatch.

The hardest single design problem — a forbidden string that is simultaneously mandatory — is
**solved and empirically proven** in §C-4: a *negative lookahead* (not a lookbehind, not a verb
allow-list) that forbids `write --sdp-relock` unless it is immediately followed by a withdrawal
predicate. It rejects all eleven overclaim phrasings tested, including the roadmap's own planted
violation and `REQUIREMENTS.md:279`'s live violation, and permits all seven withdrawal phrasings
tested. Direction of failure is **closed**: an un-anticipated phrasing rejects rather than passes.

Research also found a **second gate collision CONTEXT does not flag**: 149's inherited `issue-closed`
pattern fires on the natural phrasings of "gh#32 was closed", which **D-05 requires 152 to say**. Two
inherited rows therefore need adjudication, not one.

**Primary recommendation:** decompose into three sequential blocks — (1) record corrections + the gate
built and *seen RED then GREEN* on `.planning`-only files, (2) the three PRs to `beta` and the two
cuts, versions read after the fact, (3) five posts, each behind its own blocking gate, each preceded
by a green run of the gate in **both** file and posted mode. Put the gate GREEN before the first post
and re-run it in posted mode after each. Never under `--auto`/`--chain`.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Record corrections (ROADMAP / REQUIREMENTS / PROJECT amendments) | **Meta repo `.planning/`** | — | D-06/D-15: no sub-repo reach. Hand-edited (the `gsd-tools` verbs `_normalizeMd` whole-file). |
| The claim gate script + fixtures + suite | **Meta repo, phase-152 directory** | — | Phase-local by construction (`_HERE`), never a sibling-directory constant. Donor precedent 137/146/149. |
| `152-LEDGER.md` | **Meta repo, phase-152 directory** | Gate target (D-12) | The ledger is where D-11's narrowed pairing discipline now lives. |
| Merging code to `beta` | **Sub-repo git (`firestarter`, `firestarter_app`)** | Meta repo (gitlinks) | Executors commit *inside* each submodule; plan frontmatter needs `commits_land_in:`. |
| Cutting the released version | **GitHub Actions CI (both sub-repos)** | — | Fires on push to `beta`. Versions are **read**, never predicted. |
| Publishing to PyPI | **CI (`publish.yml` via `workflow_call`)** | — | **Measured automatic** now (`needs: github`), not a manual dispatch. See §E-3. |
| Release-note bodies | **GitHub Releases API (`gh release edit --notes-file`)** | — | Neither workflow passes `body:` — bodies are manual, always. |
| Issue comments | **GitHub Issues API (`gh issue comment`)** | — | Read-only `gh` is available; posting is a write and is per-artifact operator-gated (D-03). |
| Proving a post landed | **Re-read via `gh ... --json`** | — | `updatedAt` is not an oracle; the body text is. See §Validation Architecture. |

---

## A. Re-Verification Deltas — every "measured 2026-08-20" datum, re-measured 2026-08-21

Every row states the CONTEXT value, the value measured today, and the exact command.
**Rows marked ⚠ MOVED must not be inherited from CONTEXT.md.**

### A-1. `origin/beta` app state and the ahead/behind count — ⚠ MOVED (materially)

```bash
cd /workspaces/firestarter_app && git fetch origin
git rev-list --left-right --count origin/beta...HEAD    # → 7  85
git cherry origin/beta HEAD | awk '{print $1}' | sort | uniq -c   # → 80 '+', 5 '-'
git log --oneline HEAD..origin/beta
git show origin/beta:firestarter/cli_handlers.py | grep -n fw_board_identity
git show origin/beta:firestarter/database.py | grep -c vcc_mv        # → 0
git show origin/beta:firestarter/main.py | grep -c 'lock.status'      # → 0
```

| Datum | CONTEXT.md (2026-08-20) | Measured 2026-08-21 | Verdict |
|---|---|---|---|
| App commits ahead of `origin/beta` | **67** | **85** | ⚠ MOVED |
| App commits **behind** `origin/beta` | *not stated* | **7** | ⚠ **NEW — the merge is not a fast-forward** |
| `git cherry` already-upstream (`-`) | *not stated* | **5** | ⚠ NEW |
| `git cherry` genuinely new (`+`) | *not stated* | **80** | ⚠ NEW |
| `fw_board_identity=None` at `cli_handlers.py:2514` on beta | present | **present, exact line 2517** | ✅ HOLDS |
| `vcc_mv` on beta | absent | **absent (0 occurrences)** | ✅ HOLDS |
| `lock-status` on beta | absent | **absent (0 occurrences)** | ✅ HOLDS |

**The 7 behind-commits, named** (they are PR #52 plus its auto-commit — the fw-targeting fixes that
merged to `beta` on 2026-08-19 and cut `3.0.0b22`):

```
f505ae7 Apply automatic changes
eaca13e Merge pull request #52 from henols/fix/fw-update-path-and-port-targeting
16f5680 fix: flash the port the identity came from — defect A survived via the config path
04916e9 fix: the not-found hint blamed 2.x alone; pre-b8 3.0.0 fails identically
8610e93 fix: route the saved port through one writer — da6572b missed the flash path
cbebc05 fix: make --port authoritative, allow blind install, stop transient config leaking
a3163d7 fix: unblock the firmware-update path on pre-CAP-02 firmware
```

The five `-` (already-upstream-by-patch-id) commits on the milestone branch are
`ebbc299`, `da6572b`, `94d327d`, `a7e554d`, `c495e98`. **This is exactly the false-negative class D-04
warns about**: those five patches ARE on beta under different SHAs, so `git merge-base --is-ancestor`
would report them absent. `git cherry` is the correct oracle and it works.
`[VERIFIED: git, 2026-08-21]`

**Planning consequence:** the app PR to `beta` will show a merge (not a fast-forward) and may present
conflicts on the files PR #52 touched (`cli_handlers.py`, the fw-install path). The plan must fund a
conflict-resolution step, not assume a clean merge. `[VERIFIED: git rev-list, 2026-08-21]`

### A-2. Firmware repo vs `origin/beta` — ✅ clean

```bash
cd /workspaces/firestarter && git fetch origin
git rev-list --left-right --count origin/beta...HEAD    # → 0  39
git cherry origin/beta HEAD | awk '{print $1}' | sort | uniq -c   # → 39 '+', 0 '-'
git status --short                                       # → empty
```

**39 ahead, 0 behind, 0 already-upstream, working tree clean.** The firmware PR to `beta` is a clean
fast-forwardable merge. `[VERIFIED: git, 2026-08-21]`

`origin/beta`'s firmware still carries the pre-153 shape — `eeprom_28c.cpp:532-533` is the
`FLAG_SKIP_BLANK_CHECK`-gated `mem_util_blank_check`, and `:200` still comments that `CMD_ERASE` is
one of two commands "this protocol genuinely cannot do".
`[VERIFIED: git show origin/beta:src/proms/eeprom_28c.cpp, 2026-08-21]`

### A-3. Working-tree and gitlink state — ✅ current, with named untracked noise

```bash
git -C /workspaces submodule status
git -C /workspaces log --oneline -1
```

| Repo | Branch | HEAD | Tracked clean? |
|---|---|---|---|
| meta | `gsd/v1.32-at28c-write-path-root-cause-report-provenance` | `b23e7dd6` | yes (3 untracked: `.claude/skills/devtest-rootcause/`, `package.json`, `package-lock.json`) |
| `firestarter` | same branch name | `d990a4ce` | **yes, fully clean** |
| `firestarter_app` | same branch name | `a0bfd5e8` | yes (6 untracked, all predating this phase: `.planning/config.json`, `SECURITY.md`, 4 datasheets, `write_test_port.sh`) |

**Gitlinks are current** — `git ls-tree HEAD firestarter` = `d990a4ce…` = the firmware HEAD, verified
by 153's own verifier and re-confirmed by `submodule status` showing no `+` prefix on either entry.
`[VERIFIED: git submodule status, 2026-08-21]`

⚠ **`firestarter_app` shows a `?` prefix in the meta repo's `git status`** — untracked content inside
the submodule. That is the 6 files above and is benign, but the PR-creation step must not `git add -A`
inside the submodule.

### A-4. Release bodies and versions — ✅ HOLDS exactly

```bash
for t in 3.0.0b14 … 3.0.0b22 2.0.8; do gh release view "$t" --repo henols/firestarter_app \
  --json body -q '.body | length'; done
# firmware: same loop against henols/firestarter
gh release list --repo henols/firestarter_app --limit 15
gh release list --repo henols/firestarter --limit 15
```

| Release | body length | Release | body length |
|---|---|---|---|
| app `3.0.0b14` (2026-07-30) | **4490** | fw `3.0.0b14` (2026-07-30) | **5257** |
| app `3.0.0b15` (2026-08-02) | **4856** | fw `3.0.0b15` (2026-08-02) | **8841** |
| app `3.0.0b16`…`b22` | **all 0** | fw `3.0.0b16`…`b19` | **all 0** |
| app `2.0.8` (stable, 2026-08-07) | **0** | — | — |

App latest pre-release **`3.0.0b22`** (2026-08-19T19:40:06Z); app stable GitHub release **`2.0.8`**;
firmware latest pre-release **`3.0.0b19`** (2026-08-18T10:00:08Z). Every CONTEXT figure reproduces
byte-exact. `[VERIFIED: gh release view --json body, 2026-08-21]`

⚠ **New, and CONTEXT does not carry it:** app `2.0.8`'s body length is **also 0**. So the *stable*
release is bodiless too. Anything OUT-04 says about the stable channel must not imply 2.0.8 was
announced.

### A-5. ⚠ **NEW FINDING — PyPI is BEHIND GitHub on the stable channel**

```bash
curl -s https://pypi.org/pypi/firestarter/json | python3 -c "…"
# info.version (stable): 2.0.7
# 2.0.6 PRESENT · 2.0.7 PRESENT · 2.0.8 ABSENT from PyPI
# 3.0.0b22 uploaded 2026-08-19T19:40:29   (GitHub release 19:40:06 -> 23 s later)
```

**CONTEXT says "stable 2.0.8". Measured: GitHub has a `2.0.8` release; PyPI does not have `2.0.8` at
all, and `info.version` is still `2.0.7`.** The beta channel *is* in sync (`3.0.0b22` landed on PyPI
23 seconds after the GitHub release), so the automatic `pypi` job works; the divergence is
stable-channel only. This is exactly the "GitHub carrying betas past PyPI" hazard class CONTEXT names,
measured live and on the channel CONTEXT did not check.
`[VERIFIED: pypi.org/pypi/firestarter/json, 2026-08-21]`

**Planning consequence for OUT-04:** the app release notes must state the install command for the
**beta** channel (`pip install --pre firestarter`) and must not assert that `2.0.8` is installable
from PyPI. If the notes mention a stable version at all, the version must be read from PyPI's
`info.version`, not from `gh release list`.

### A-6. The `b14` forward-looking sentence OUT-04 must correct — ✅ still live and public

The app `b14` body (4490 chars, published 2026-07-30, **not to be rewritten** per D-02) still contains
both the `dev sdp <chip> enable|disable` announcement and the sentence CONTEXT names:

> *"An opt-in re-lock after a write is deliberately not part of this release."*

That sentence is the "forward-looking wording v1.30 left behind" that criterion 4 names. It is
corrected **in the new notes**, never edited in place. `[CITED: 152-CONTEXT.md D-02; body length
re-verified 2026-08-21]` — the sentence itself is `[ASSUMED]` at char level (not re-grepped this
session; the body length matching CONTEXT byte-exact is strong corroboration that the body is
unchanged).

### A-7. AT28C256 DB row — ✅ HOLDS, plus three fields CONTEXT omits

```bash
cd /workspaces/firestarter_app && python3 -c "…json.load('firestarter/data/chip_database.json')…"
```

```json
{ "part_number": "AT28C256,AT28C256E,AT28C256F,AT28HC256,AT28HC256E,AT28HC256F,AT28HC256L",
  "pinout": "DIP28_28C256",
  "electrical": { "pin_count": 28, "size_bytes": 32768, "type": "EEPROM",
                  "vcc_mv": 5000, "vdd_mv": 5000, "vpp_mv": 12000 },
  "programming": { "algorithm": 13, "chip_id_check": false, "chip_id_value": "0x00000000",
                   "infoic_page_size_raw": 64, "protect_off_before": true,
                   "protect_on_after": true, "pulse_duration_us": 0 },
  "support_status": "supported" }
```

Every CONTEXT field reproduces. **Three fields CONTEXT does not mention and the planner should know:**

1. **`vpp_mv: 12000` on a 5 V EEPROM row.** This is the WARNING-5 protocol-override artefact
   (`firestarter_app/CLAUDE.md` §"Database Pipeline"), and 12 V on `DIP28_28C256`'s pin 1 is a damage
   path. **No outward artifact may cite `vpp_mv: 12000` as evidence that the datasheet's hardware
   12 V-on-OE erase path is available** — Phase 153 deliberately did not implement it.
2. **`part_number` is a comma-joined 7-alias list.** One database row covers AT28C256/E/F and
   AT28HC256/E/F/L. Any outward sentence saying "the AT28C256 row" is describing seven part numbers.
3. **`protect_on_after: true`** — the DATA-06 advisory field with **no runtime consumer in this
   release** because `write --sdp-relock` is deferred. It is `true` on 70/746 rows and is 27/27 on
   `algorithm: 5`, i.e. a constant there. The notes must not imply it is honoured.

`[VERIFIED: chip_database.json read live, 2026-08-21]`

### A-8. Live re-derivation of the DB class sizes — ⚠ CONTEXT's numbers do NOT reproduce exactly

Algorithm histogram over all **746** rows, re-derived through the production JSON:

```
{6: 190, 7: 170, 8: 127, 13: 84, 16: 39, 40: 34, 11: 32, 5: 27, 14: 20, 41: 20, 39: 2, 52: 1}
```

`algorithm 13` = **84**, `algorithm 5` = **27** (→ 111), `algorithm 16` (`0x10`) = **39**. Those three
reproduce CONTEXT exactly. `[VERIFIED: chip_database.json, 2026-08-21]`

The `lock-status` class partition, re-derived through the **real pipeline**
(`EpromDatabase().get_eprom(name)` → `protection_readability.protection_gate_for_entry`), keyed on the
first alias of each row's `part_number`:

| class token | measured 2026-08-21 | CONTEXT / 151 D-06 | delta |
|---|---|---|---|
| `no_mechanism` | **405** | 406 | −1 |
| `undocumented_alias` | **112** | *not stated* | — |
| `not_readable` | **108** | 111 (= 84 + 27) | −3 |
| `not_implemented` | **40** | 39 (the `0x10` rows) | +1 |
| `read_permitted` | **81** | *not stated* | — |
| **total** | **746**, zero errors | 746 | — |

⚠ **CONTEXT says 406 / 111 / 39; measured today by this method it is 405 / 108 / 40.** The likely
cause is aliasing: my derivation keys on the *first* alias per row, and 151's classifier is
alias-aware (`split_part_number_tokens`, hence the 112-row `undocumented_alias` bucket), so a row whose
first alias is uncurated lands in `undocumented_alias` and shifts the neighbours. **I did not resolve
which method 151 used, so neither set of numbers is safe to publish.**

**The planner must re-derive in-plan, with 151's own method, before any outward sentence cites a
count** — and should prefer the figure that is robust to the ambiguity:

> **665 of 746 database rows (89 %) resolve to a refusal class; only 81 are `read_permitted`.**

That statement holds under either method (405+112+108+40 = 665) and is the load-bearing fact behind
D-13's "the refusal IS the feature" framing. `[VERIFIED: live derivation, 2026-08-21]`

The eight class tokens are confirmed live in `firestarter/lock_status.py`:
`('protected', 'unprotected', 'not_readable', 'not_implemented', 'undocumented_alias',
'no_mechanism', 'firmware_outdated', 'unadjudicated_probe')`; exit codes
`{protected:0, unprotected:0, not_readable:2, not_implemented:2, undocumented_alias:2,
no_mechanism:2, firmware_outdated:3, unadjudicated_probe:4}`; and
`SILICON_ONLY_TOKENS = frozenset({'protected','unprotected'})`.
`[VERIFIED: python3 -c "from firestarter import lock_status", 2026-08-21]`

### A-9. ⚠ **The leonardo size figures HAVE MOVED — all three of them**

```bash
cd /workspaces/firestarter && python3 -c "json.load(open('scripts/baseline/size_baseline.json'))"
```

| Figure | CONTEXT.md (2026-08-20) | Measured 2026-08-21 | Verdict |
|---|---|---|---|
| leonardo `flash_used` | **27500** | **27630** | ⚠ MOVED +130 |
| leonardo `flash_free` | 5268 | **5138** | ⚠ MOVED |
| leonardo `flash_total` | 32768 | 32768 | ✅ |
| MERGE-05 delta vs `base01` | **+594 ≤ 594** | **+724 ≤ 724** | ⚠ MOVED |
| Named exemptions | **three**: 96 + 210 + 288 | **four**: 96 + 210 + 288 + **130** | ⚠ MOVED |
| Caterina cliff headroom (28672 − used) | **1172 B** | **1042 B** | ⚠ MOVED |
| leonardo `ram_used` / `ram_free` | 2016 / 544 *(not in CONTEXT)* | **2016 / 544** (`ram_total` 2560) | new |
| uno `flash_used` | *not in CONTEXT* | **25548** (free 7220) | new |
| uno328pb `flash_used` | *not in CONTEXT* | **25598** (free 7170) | new |

The +130 B is Phase 153's `erase-standalone` exemption (`D-153-01`). `size_baseline.json`'s `meta.phase`
names it: *"Phase 153 Plan 14 (ERASE-08): re-record the size baseline for the standalone CMD_ERASE
feature's measured cold footprint"*. `[VERIFIED: scripts/baseline/size_baseline.json, 2026-08-21]`

⚠ **The two figures must never be conflated** — `153-RECORD.md` states this as a standing rule:
*"MERGE-05 leonardo flash headroom is 0 B"* (delta = allowance, exactly) and *"the Caterina cliff
headroom is a separate, UNGUARDED figure: 28672 − 27630 = 1042 B"*. `board_upload.maximum_size` was
raised to the real 32768 B on all three AVR envs by quick task `260820-a7w`, **so the linker no longer
protects the USB bootloader boundary.** Nothing but the recorded 1042 B stands between a future
phase's growth and a bricked leonardo. `[CITED: 153-RECORD.md §"Two size figures, separately"]`

**These are the numbers any firmware-release-notes sentence about the ceiling must use** — see §G-2.

### A-10. `infoic.xml` AT28C256 record — ✅ inherited from CONTEXT, not re-measured

CONTEXT records `protocol_id 0x07`, `flags 0x0000C010` (bit `0x10` erasable **SET**),
`page_size 0x40`, `write_buffer_size 0x80`, `chip_id 0x00000000`. **Not re-measured this session** —
CONTEXT marks the erase findings (D-06) "established from primary sources, do not re-derive", and the
`0x40` page size is corroborated independently by the DB's `infoic_page_size_raw: 64` (§A-7).
`[CITED: 152-CONTEXT.md §code_context]` — treat as `[ASSUMED]` for the `write_buffer_size` and
`flags` values specifically.

### A-11. ⚠ **NEW — three stale record sites CONTEXT does not list**

Beyond D-05's OUT-01/OUT-04 and D-15's PROJECT.md items, the following are stale **today**:

1. **`ROADMAP.md:37`** (the v1.32 milestone bullet) still reads *"gh#21/#32/#11/#12 stay OPEN"*.
   gh#32 is CLOSED. Same defect class as D-05, one site further out.
   `[VERIFIED: grep, 2026-08-21]`
2. **`REQUIREMENTS.md` Coverage block (≈lines 431-435)** reads:
   *"v1 requirements: 33 total as authored; **25 in v1 scope**… Mapped to phases: 25 ✓ (Phases
   147–149, 151, 152)"*. Both numbers and the phase list predate Phase 153. **Measured actual:**
   `- [x]`/`- [ ]` checkboxes by family = DATA 6 + ERASE 9 + LOCK 4 + OUT 5 + PGSZ 5 + PROV 6 =
   **35 in scope** (30 complete, 5 pending); `⏸` deferred = RELOCK **7**; **42 defined**;
   traceability table = 42 requirement rows, 0 unmapped. The phase list must gain **153**.
   ⚠ **Arithmetic conflict:** the file's own footer says "25 → **34** in scope, 42 defined", but the
   checkboxes count **35**. Off by one. The planner must reconcile (likely DATA-06's re-homing being
   double-counted) — do not paper over it. `[VERIFIED: grep -c + per-family count, 2026-08-21]`
3. **`ROADMAP.md` and `REQUIREMENTS.md` both cite `database.py:621`** as the `FLAG_CAN_ERASE`
   exclusion-tuple edit site. Phase 153 measured the real site as **`:620`** and recorded it as the
   fourth corrected line number in its chain. Measured today, the exclusion tuple `if algo not in
   (5,):` sits at **`database.py:629`** (the file grew during 153). Both documents are wrong, and
   they are wrong differently from each other and from the tree.
   `[VERIFIED: sed -n '630,645p' firestarter/database.py, 2026-08-21]`

**All three are inside 152's write surface and are the same correction class as D-05.** They are
cheap to fix in the same edit and expensive to leave: an outward artifact drafted from a stale
requirements Coverage block would misstate the milestone's own size.

### A-12. `check_record_corrections.py` — ✅ GREEN today, and the line-shift risk is ZERO

CONTEXT calls this checker a tally of `{block, line-label, inline-history, inline-allow, superseded}`.
**Measured: those are its five *exemption verdicts*, and it is a Phase-130-hosted, twelve-needle
checker whose `_DEFAULT_TARGETS` are repo-root-relative — including three files 152 hand-edits.**

```bash
python3 .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/check_record_corrections.py
# PASS: scanned .planning/PROJECT.md, .planning/STATE.md, .planning/ROADMAP.md,
#   .planning/milestones/v1.23-REQUIREMENTS.md, .planning/notes/py32f071-port-branch-state.md;
#   exempt hits by verdict: {'block': 23, 'line-label': 4, 'inline-history': 6,
#   'inline-allow': 10, 'superseded': 12}
# rc=0    real 0m23.342s
```

Two load-bearing findings:

1. **It currently PASSES**, and it scans `PROJECT.md`, `STATE.md`, `ROADMAP.md`. `REQUIREMENTS.md` is
   **not** a target. Any 152 edit to the first three must re-run it. `[VERIFIED, 2026-08-21]`
2. ⚠ **The line-shift hazard is NOT present.** Every live `recordscan:supersedes needle=… lines=N`
   marker — the only line-number-keyed mechanism — lives in
   `.planning/notes/py32f071-port-branch-state.md` (7 markers, `lines=12`, `20,21,22,23,24,29`, `53`,
   `61`, `94`, `96`, `107`), a file 152 does not touch. `ROADMAP.md`'s single
   `recordscan:supersedes` grep hit at line 3581 is **narrative text inside another comment**
   describing the very orphaning hazard, not a live marker. `PROJECT.md` and `STATE.md` use only
   position-independent `recordscan:allow` / `recordscan:history`.
   **So 152 may hand-edit ROADMAP.md / PROJECT.md / STATE.md freely without orphaning any `lines=N`
   marker** — it must still re-run the gate to prove it. `[VERIFIED: grep -rno for live markers,
   2026-08-21]`

⚠ **Timing delta:** CONTEXT says the record gate needs a **300 s** timeout because of STATE.md's
~52k-char single line. Measured today this specific checker runs in **23.3 s**. Keep 300 s as the
plan's timeout ceiling (fail-open on a short timeout reads like a RED, and other record gates in this
project are slower), but do not budget 300 s of wall clock for it.

---

## B. What Phase 153 Actually Shipped — the single largest factual input to OUT-02/03/04

Sources: `153-VERIFICATION.md` (195 lines, `status: passed`, `score: 9/9`, re-verified 2026-08-21),
`153-RECORD.md` (438 lines), plus direct reads of the committed tree. Read the tree, not only the
record, for every claim below.

### B-1. Verified state: 9/9 truths, all nine ERASE-01…09 requirements `[x]` Complete

`153-VERIFICATION.md` frontmatter: `verified: 2026-08-21T12:30:00Z`, `status: passed`, `score: 9/9`,
`behavior_unverified: 0`, `overrides_applied: 0`, `gaps_remaining: []`, `regressions: []`. It is a
**re-verification** — the first pass scored 8/9 and found one live false doc claim, now closed.
`[VERIFIED: 153-VERIFICATION.md frontmatter, read 2026-08-21]`

### B-2. `write` performs **no blank check** on `0x0D` and `0x05` — and the flag is now UNREAD

The three-line conditional was **deleted outright, not re-gated**. `mem_util_blank_check` now appears
exactly once in `eeprom_28c.cpp` — the `CMD_BLANK_CHECK` dispatch arm at `:260`. The replacing comment
at `:647-657` reads, verbatim in the tree:

> *"152-CONTEXT.md D-07 / ERASE-01: no pre-write blank check on this protocol. On `0x0D` the silicon
> auto-erases per page during the write itself, and `eeprom28c_verify_page_readback` already
> read-back-verifies every page, so a pre-write blank check was never a safety net here — it was a
> false precondition that made a non-blank AT28C part un-writable without a flag.
> `FLAG_SKIP_BLANK_CHECK` is consequently **UNREAD** on this protocol; do not restore this conditional
> on the grounds that the bit looks orphaned."*

`0x05` (flash4): the sibling conditional was **located in code before being touched**, at
`flash_5v_page.cpp:88-90` (RESEARCH's original figure; PATTERNS' "correction" to `87-89` was itself
wrong). Deleted the same way. `flash_5v_page.cpp:90` now carries the same "consequently unread"
comment. `[VERIFIED: grep + sed over firestarter@d990a4c, 2026-08-21]`

### B-3. `erase` IS a standalone step on `0x0D` — via the **SOFTWARE** path, not the 12 V hardware path

- `case CMD_ERASE:` at `eeprom_28c.cpp:250-251` dispatches to `eeprom28c_erase_execute` (declared
  `:150`, defined `:545`).
- The implementation emits the **AN 0544B six-byte software chip-erase sequence**, cited in-tree at
  `:500-502` as *"Atmel Application Note 'Software Chip Erase', Rev. 0544B-10/98 (doc0544.pdf)"*.
  ⚠ **This discharges CONTEXT's deferred item "Obtaining the Atmel/Microchip Software Chip Erase
  application note"** — 153 had it. The 20 ms `t_EC` constant is documented at `:59-71`.
- Six inline `firestarter_set_data` calls, **0 B RAM** by construction (`D-153-01`).
- `D-153-02`: the erase emits an **SDP-disable prefix first**, on an asymmetry argument (an
  undetectable phantom erase is worse than six harmless extra bus writes).
- `D-153-04`: **device-global by construction** — `erase -b` is a documented no-op and
  `erase --sector-address` is ignored.
- `D-153-05`: `erase` stays **standalone** — no `FLAG_CAN_ERASE`-gated erase-on-write block was added,
  and no `--skip-sdp-unlock` option was added to `erase`.

`[VERIFIED: firestarter/src/proms/eeprom_28c.cpp read at HEAD d990a4c, 2026-08-21]`

### B-4. `FLAG_CAN_ERASE` is RESTORED for algorithm 13 — measured at `database.py:629`

```python
# firestarter_app/firestarter/database.py  (measured 2026-08-21)
if full_eprom_data.get("electrical-type", "") in ("EEPROM", "Flash/EEPROM"):
    if algo not in (5,):                 # ← exclusion tuple, was (5, 13)
        simple_flags |= FLAG_CAN_ERASE   # FLAG_CAN_ERASE is 0x02
```

The exclusion tuple is now `(5,)` — algorithm 5 stays excluded **for its own, unrelated
hardware-hazard reason**, never conflated with algorithm 13's retired one. All **84** algorithm-13
rows now advertise `FLAG_CAN_ERASE` on the wire; `153-12` proved exhaustively that exactly 84 of 746
rows changed and 0 non-algorithm-13 rows moved. The in-tree comment records the plan-shape
consequence: *"erase becomes a supported destructive step, and blank-check moves to sit after it,
where it doubles as the erase's oracle."* `[VERIFIED: sed -n '630,645p' database.py, 2026-08-21]`

### B-5. GATE-03 — the roadmap's stated mechanism **did not hold**, and 153 says so

`153-RECORD.md` §"Mechanism corrections", verbatim finding:

> *"ROADMAP criterion 3 implies `tools/check_dispatch.py` is what prevents the hardware 12 V-on-OE
> erase path from reaching `0x0D`. **It structurally cannot** — that checker is
> database-and-dispatch-table scoped and never looks inside a C++ handler body."*

What actually guards the hazard is a **new** control: `firestarter/scripts/check_erase_no_vpp.py`, a
brace-matched negative source scan, proven **reachable** (fails on a committed planted violation) and
**discriminating** (fails on `eeprom28c_check_chip_id`'s legitimate A9-12 V writes).
`tools/check_dispatch.py` was **not weakened, exempted or re-baselined** — `git diff --quiet` holds.

Both gates re-run live in this session's verification and both exit 0, as does
`check_no_community_support_status_write.py`. `[CITED: 153-RECORD.md; 153-VERIFICATION.md re-run
transcript, 2026-08-21]`

⚠ **Consequence for 152:** any outward sentence about the hazard must name
`scripts/check_erase_no_vpp.py`, not `check_dispatch.py`. **GATE-03's criterion was corrected, not
satisfied** — saying "GATE-03 prevented it" would repeat a mechanism claim 153 disproved.

### B-6. `ic_layout.py:578-586` was **NOT** edited — ERASE-06 was satisfied from the other side

CONTEXT D-07 lists `ic_layout.py:579` as a surface needing correction. **Measured: `ic_layout.py` has
zero commits from Phase 153.** ERASE-06 was read as *"the two axes must not contradict"*, not
*"`info` must derive from the wire bit"* — and under that reading the block needed **zero edits**: it
already keys on `electrical.type` alone, and it already **agrees** once ERASE-03 restored the wire
flag. The block is at `:578-586` (PATTERNS' corrected figure, which held; RESEARCH's original
`:581-585` was wrong). `[VERIFIED: sed -n '578,586p' ic_layout.py + 153-VERIFICATION truth 5,
2026-08-21]`

### B-7. The `database.py:591` code comment WAS corrected — D-15's carve-out is discharged

ERASE-07 landed it; `153-RECORD.md` records it as *"the fourth recorded reversal in its chain"*
(Phases 119 → 120 → 121 → 153), now at `database.py:585-616`. **152 therefore has no code comment to
reach for** — D-15's *"the code comment is left to Phase 153"* is satisfied, and 152's own D-15 work is
the `.planning`-side premise correction only. `[CITED: 153-RECORD.md ERASE-07 + Mechanism corrections]`

### B-8. ⚠ `dev test`'s write step — the fix is in the FIRMWARE, so it needs **matched firmware**

This is the subtlest fact in the phase and OUT-02 turns on it.

```bash
cd /workspaces/firestarter_app && grep -n "write_eprom" firestarter/chip_test.py
# :1918   outcomes.append(operator.write_eprom(name, eprom_data, tmp_source_path))   ← STILL FLAGLESS
# :2150   wrote_ok = operator.write_eprom(name, eprom_data, tmp_source_path, flags)  ← the SDP leg
grep -n "def write_eprom" firestarter/eprom_operations.py   # :1872, operation_flags: int = 0
```

**The main `dev test` write step at `chip_test.py:1918` is still flagless, and `write_eprom` still
defaults `operation_flags: int = 0`.** CONTEXT cites this at `:1893` — the line **moved to `:1918`**.
Phase 153 did **not** change the host call; it removed the firmware-side conditional. So:

> **`dev test`'s write step passes on a non-blank `0x0D` part only when the board is running v1.32
> firmware.** Against older firmware the host still sends no `FLAG_SKIP_BLANK_CHECK` and the firmware
> still blank-checks at write INIT — i.e. the gh#20 `Not blank, at 0x000000, v: 0x40` failure
> reproduces exactly as before.

**OUT-02's request for a fresh run must therefore state BOTH halves of the install**:
`pip install --pre firestarter` **and** `firestarter fw --install`. That is the same dual dependency
D-13 already requires for `lock-status` (a new `CMD_*` mapping `MSG_ERR_UNKNOWN_CMD` →
`FirmwareOutdatedError`, per 151 D-04), so the two paragraphs share one install instruction.
`[VERIFIED: grep over firestarter_app@a0bfd5e, 2026-08-21]`

### B-9. `blank` remains its own step — non-regression, unchanged

`cli_handlers.py:854` → `CMD_BLANK_CHECK` → `mem_util_blank_check` (firmware `eeprom_28c.cpp:248`).
Already worked before 153; proven still to work across CLI, host-call and firmware-dispatch layers.
`[CITED: 153-RECORD.md ERASE-05]`

### B-10. What Phase 153 did **NOT** do — transcribe this list, do not paraphrase it

`153-RECORD.md` §"What was NOT proven", verbatim substance:

- **This change ships software-proven and unvalidated on silicon.** No AT28C part was involved at any
  point — not in writing the erase sequence, not in choosing the SDP-disable prefix, not in any test.
- **`0x0D` stays `UNVERIFIED`** in `PROTOCOL-LEDGER`. Nothing graduates it.
- **No `support_status` field moved.** `chip_database.json` is **byte-unchanged** (`git diff --stat`
  empty); `check_no_community_support_status_write.py` and `check_diagnostic_report_claims.py` both
  exit 0.
- **gh#21, gh#11 and gh#12 stay OPEN.** A code fix is not a validation. *(gh#32 was already CLOSED
  2026-08-08 — corrected in-record 2026-08-21, and **"Phase 152 must not 'reply' to a closed issue on
  the strength of this line"**.)*
- **The 20 ms `t_EC` figure is an Atmel-family maximum** from AN 0544B Rev. 0544B-10/98. The 84-row
  algorithm-13 bucket spans other vendors. **A part with a longer actual cycle time would read
  non-blank after a successful-looking erase, and nothing in the test suite could catch that.**
- **No native test can prove the wall-clock wait is honoured.** The native trace stubs do not stub
  `delay()` and record no time — the `AT28C_TEC_MAX_MS` assertion is **structural, not temporal**.

`153-RECORD.md` §"What Phase 152 must not repeat" — the three now-false claims:

1. That the `0x0D` / AT28C family has **no erase operation at all**.
2. That `-b` / `--no-blank-check` is **required** to write a non-blank AT28C part.
3. That v1.32 has **fewer than three** firmware-touching workstreams.

`[CITED: 153-RECORD.md, read in full 2026-08-21]`

### B-11. ⚠ D-15's PROJECT.md / ROADMAP.md workstream correction is **ALREADY DONE**

Phase 153 landed it. `PROJECT.md:45-47` now reads *"**three** firmware-touching workstreams — Phase
149 (the page-size seam), Phase 151 (the protection read) and…"* with an explicit
`152-CONTEXT.md D-15` attribution note at `:47`. `ROADMAP.md:37` and `:163` carry the corrected count
with dated amendment notes. `[VERIFIED: grep -n "firmware-touching" PROJECT.md ROADMAP.md,
2026-08-21]`

**So of D-15's three bullets, one is discharged (the count), one is discharged by 153 (the code
comment, §B-7), and what remains for 152 is:** the PROJECT.md workstream-table row for 153 + the
workstream-4 description update, and the Phase 121 D-12 premise correction in `.planning`.
**The planner must verify the table row's absence before funding it** — 153 may have landed that too.

---

## C. The Claim Gate (OUT-05, D-09 / D-11 / D-12) — mechanism, derived and proven

### C-1. The donor, read in full

`.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-check-claims.py`, **531 lines**.
Measured live today: **17 forbidden rows**, **1 required-caveat row**, and it is **GREEN**:

```bash
python3 .planning/phases/149-*/149-check-claims.py     # rc=0, PASS over 9 targets
python3 -m pytest test_check_claims_v132.py -q -o addopts=""   # 20 passed in 0.82s
```

`[VERIFIED: both run live, 2026-08-21]`

### C-2. The four mandatory renames a `152-check-claims.py` must make

Transcribed from the donor's own docstring (`:24-56`), retargeted:

| # | What renames | 149's value | 152's value |
|---|---|---|---|
| 1 | `_DEFAULT_TARGETS` | 9 entries, enumerated | see §C-6 — **enumerated one by one, never a wildcard** |
| 2 | The self-check prefix literal, in **both** the `startswith` call **and** its failure message | `"149-"` | `"152-"` |
| 3 | The env-override seam | `FIRESTARTER_CLAIMSCAN_TARGETS_149` | **`FIRESTARTER_CLAIMSCAN_TARGETS_152`** |
| 4 | The docstring + its explicit non-claim, retargeted at this phase's requirement id and its own blocking operator review | PGSZ-05 | **OUT-05**, and D-03's per-artifact gates |

Plus the mechanics that transcribe **unchanged** (do not re-invent): the `__file__`-derived `_HERE`
constant; `resolve_targets`'s argv/env/defaults precedence with the load-bearing
`os.environ.get(...)`-with-no-default so `is not None` distinguishes *absent* from *present-but-empty*;
the hoisted **never-vacuous** guard; the fail-closed missing-target branch; `_print_bucket`'s 20-entry
display cap; `_required_caveats_for()`'s **fail-CLOSED** default (an unknown basename gets the FULL
caveat set, never the empty set); and **no window, no exclusion, no inline allow-marker** — every
match anywhere in a scanned file's text is a violation.

The env seam name is confirmed correct as `FIRESTARTER_CLAIMSCAN_TARGETS_152`: the phase-number suffix
(not a bare or milestone-suffixed name) is what stops one phase's seam retargeting another's live
gate. `[VERIFIED: 149-check-claims.py:159-171, 2026-08-21]`

### C-3. The `_HERE` fail-open trap, concretely

`.planning/phases/137-*/check_permitted_claims.py` (360 lines) documents the trap it avoided, at
`:51-74`: v1.23's copy named its targets against a **sibling** phase directory via a hardcoded string
constant `_PHASE_130_DIRNAME`, so a naive copy into another phase directory *"silently resolves its
targets somewhere else entirely — scanning nothing and exiting 0, a green that proves absolutely
nothing."*

But 137 carries a **second, distinct** fail-open path 149 deliberately did not port —
`check_permitted_claims.py:302-312`:

```python
if used_defaults and len(missing) == len(targets):
    print("UNARMED: none of Phase 137's 4 named closing artifacts exist yet …")
    return 0            # ← exit 0 with nothing scanned
```

**152 must not port this branch.** 149's docstring states why: *"an exit-0-on-nothing-scanned path is
a green that proves nothing."* Copy 149's shape (never-vacuous → `return 1`; any missing target →
`return 1`), not 137's. `[VERIFIED: check_permitted_claims.py read, 2026-08-21]`

### C-4. ⭐ The fifth forbidden class — the hardest problem, SOLVED and empirically proven

**The problem.** Criterion 4 *requires* the two release-note bodies to name `write --sdp-relock`
explicitly (as withdrawn). Criterion 5 *forbids* naming it as shipped. The same literal string is
mandatory in one framing and forbidden in another, and the inherited gate has **no window and no
exclusion mechanism**, so a bare pattern on the string would reject the sentence criterion 4 demands.

**Approaches considered, with their failure modes:**

| Approach | Mechanism | Failure mode |
|---|---|---|
| Bare pattern on `write --sdp-relock` | one row | Rejects criterion 4's own mandated sentence. Unusable. |
| **Verb allow-list** (forbid only near `ships`/`available`/`use`…) | positive enumeration | **Fails OPEN by construction.** Any unlisted phrasing (*"Protecting a part: `write --sdp-relock`"*) passes. Wrong direction of failure. |
| Per-file rule (forbid in the comment files, permit in the notes) | `_CAVEAT_RULES`-style basename map | Permits *any* framing inside the notes, including "ships". Defeats the class where it matters most. |
| Proximity window | new mechanism | Explicitly refused by the donor's D-14 precedent — Phase 139 measured a windowed scanner passing four planted overclaims. |
| **⭐ Negative LOOKAHEAD requiring an adjacent withdrawal predicate** | one row, same table shape | **Fails CLOSED.** Mandates one canonical word order. Direct structural analogue of 149's `(?<!software-)` narrowing. **Recommended.** |

**A lookbehind cannot be used** — Python `re` requires fixed-width lookbehinds, and the natural prose
order puts the withdrawal predicate *after* the command name. **Lookahead is variable-width-capable**,
so it is the right operator.

**The derived pattern** (tested on Python 3.12.13, the devcontainer interpreter):

```python
(
    "sdp-relock-as-shipped",
    re.compile(
        r"write\s+--sdp-relock"
        r"(?!`?\s*(?:(?:is|stays|remains|was)\s+)?(?:still\s+)?"
        r"(?:withdrawn|deferred|not\s+shipped|not\s+shipping|unavailable|absent))",
        re.IGNORECASE,
    ),
),
```

⚠ **The optional backtick MUST live inside the lookahead, never in the consumed part.** My first
derivation wrote `r"write\s+--sdp-relock`?(?!…)"` and it permitted **nothing**: the engine backtracks
off the consumed backtick, the lookahead then inspects the backtick itself, the alternation fails, and
every withdrawal sentence matches. That bug produced 7/7 false HITs. Record it — it is not obvious and
a re-derivation will hit it again.

**Empirical proof, run 2026-08-21, zero failures:**

| MUST REJECT (11/11 HIT ✓) |
|---|
| `` `enable` returns as `write --sdp-relock`. `` ← **the roadmap's own planted violation** |
| `` `enable` returns as `write --sdp-relock`, and it must not describe `` ← **`REQUIREMENTS.md:270` live text** |
| ``The release notes announce `write --sdp-relock` and `lock-status` as shipped in the`` ← **`REQUIREMENTS.md:279` live text** |
| ``You can now protect a part with `write --sdp-relock`.`` |
| ``Protecting a part: `write --sdp-relock` `` ← the phrasing a verb allow-list would miss |
| `write --sdp-relock ships in this release` |
| ``Use `write --sdp-relock` to re-protect the chip.`` |
| ``` `write --sdp-relock` will return in a future release. ``` |
| ``` `write --sdp-relock` is available. ``` |
| ``` `write --sdp-relock` is shipped. ``` |
| `firestarter write --sdp-relock AT28C256 image.bin` |

| MUST ALLOW (7/7 MISS ✓) |
|---|
| ``` `write --sdp-relock` is withdrawn — tracked as Backlog 999.28. ``` |
| ``` `write --sdp-relock` remains withdrawn, for a second release. ``` |
| ``` `write --sdp-relock` stays deferred (Backlog 999.28). ``` |
| ``` `write --sdp-relock` is still withdrawn. ``` |
| ``` `write --sdp-relock` is not shipped in this release. ``` |
| `write --sdp-relock withdrawn` |
| ``` `write --sdp-relock` was withdrawn in v1.30 and stays withdrawn in v1.32. ``` |

`[VERIFIED: python3 re, 18 assertions, 0 failures, 2026-08-21]`

**The mandated word order this creates, stated for the wording review:** the command name comes
**first**, the withdrawal predicate **immediately after**. Any other order rejects. That is a real
constraint on the prose and it is the intended cost — the same cost 149 accepted when it mandated
*"software-proven and unvalidated on silicon"* as the only permitted spelling of *proven*.

**Belt-and-braces (recommended, and 149's own two-sided precedent):** pair the forbidden row with a
`REQUIRED_CAVEAT_PATTERNS` row that forces the withdrawal sentence to be **present** in the two
release-note bodies — otherwise the class can be satisfied by silently dropping the sentence, which
criterion 4 forbids independently.

**Add a companion row for the bare flag** (`--sdp-relock` without `write `), same shape — otherwise
*"the `--sdp-relock` option is available"* passes. `[ASSUMED]` — designed but not tested this session;
the planner should test it alongside.

**Scoping insight that reduces the surface:** `137-GH12-COMMENT.md` **never names
`write --sdp-relock`** (read in full — it says *"the design for one is settled and the work is
queued"*). D-14's adaptation adds only *Backlog 999.28 by name*, which is not the command string. So
the cleanest plan is: **only the two release-note bodies carry the literal command string**, in the
mandated withdrawal shape. The three comment drafts and the ledger never contain it, and the fifth
class never fires on them. `[VERIFIED: 137-GH12-COMMENT.md read in full, 46 lines, 2026-08-21]`

### C-5. ⚠ **A SECOND collision CONTEXT does not flag — `issue-closed` vs D-05**

149's inherited row:

```python
("issue-closed", re.compile(r"gh#(?:21|32|11|12)\b(?:\s+\w+){0,3}\s+(?:closed|resolved|fixed)",
                            re.IGNORECASE)),
```

**D-05 requires 152 to state that gh#32 is closed.** Measured against the live table today:

| sentence | verdict |
|---|---|
| `gh#32 was closed on 2026-08-08 as a duplicate fold into gh#21.` | **BLOCKED** `[issue-closed]` |
| `gh#32 is CLOSED (folded into gh#21).` | **BLOCKED** `[issue-closed]` |
| `gh#32 (CLOSED 2026-08-08, folded into gh#21)` | CLEAN — parenthetical form only |
| `gh#21, gh#11 and gh#12 stay OPEN.` | CLEAN |

`[VERIFIED: live import of 149's FORBIDDEN_PATTERNS, 2026-08-21]`

**So two inherited rows need adjudication, not one.** Recommended resolution: **drop `32` from the
alternation** → `gh#(?:21|11|12)\b…`. This is principled and is a *narrowing to the true claim class*,
not a loosening: the forbidden class is "claiming an issue this milestone did not close is closed", and
gh#32's closure is a **measured fact from 2026-08-08**, not a claim. Rejected alternative: mandating
the parenthetical spelling — brittle, and it would force awkward prose in three artifacts.

The narrowing needs the same discipline 149 applied to `proven-unqualified`: record the measurement,
name the reason in the row's own comment, and add fixture legs proving `gh#21 … closed`,
`gh#11 … resolved` and `gh#12 … fixed` **all still fire**.

**Two other inherited rows were checked and are FINE:** `now-works` and `at28c256-fixed` correctly
block `"erase now works on AT28C256"` and `"AT28C256 is fixed in this release"` — the exact D-10
concern — while leaving D-11's exempted phrasings (`"erase is now available"`, `"write no longer
blank-checks"`) clean. `[VERIFIED, 2026-08-21]`

**And the planted violation is CLEAN against the inherited 17-row table** — confirming the fifth class
is genuinely new work and that 149's gate, copied unchanged, would have **passed** the very text
criterion 5 names. `[VERIFIED, 2026-08-21]`

### C-6. `proven-unqualified` — the lookbehind, re-derived for 152

**Recommendation: keep 149's `(?<!software-)\bproven\b` verbatim, and add a second required-caveat
row for D-11's own content.** Reasoning:

1. The phrase **"software-proven and unvalidated on silicon"** is now this milestone's established
   vocabulary in **three** places, all measured today: 149's `REQUIRED_CAVEAT_PATTERNS`;
   `153-RECORD.md` §"What was NOT proven" (*"This change ships software-proven and unvalidated on
   silicon."*); and `firestarter/README.md`'s Protocol Notes, which 153's verifier confirmed carries
   *"**This ships software-proven and unvalidated on silicon**"* verbatim. The release notes and the
   ledger will use it because it is the honest description of 153's erase.
2. Re-deriving a *different* spelling means re-deriving the lookbehind, and CONTEXT itself flags the
   failure mode: widening past exactly one prefix silently permits `bench-proven`,
   `datasheet-proven`, `silicon-proven`.
3. D-11's stated caveat content — *no AT28C silicon tested, `0x0D` stays `UNVERIFIED`* — contains **no
   instance of the word "proven"**, so it needs no lookbehind of its own and can be a plain required
   row.

**Verified today:** the two candidate caveat sentences below are **CLEAN** against 149's full 17-row
table, i.e. requiring both creates no self-collision:

```
This ships software-proven and unvalidated on silicon.
No AT28C part was tested at any point in v1.32, and protocol `0x0D` stays UNVERIFIED in
PROTOCOL-LEDGER.
```

`[VERIFIED: live table scan, 2026-08-21]`

**Two required-caveat rows, therefore:**

| label | pattern (proposed) | required on |
|---|---|---|
| `software-proven-unvalidated` | `software[-\s]proven\s+and\s+unvalidated\s+on\s+silicon` *(149's, verbatim)* | ledger + both release-note bodies |
| `at28c-unverified-nonclaim` | *(D-11's content — must match "no AT28C … tested" **and** "`0x0D` … UNVERIFIED"; two patterns or one, planner's call)* | both release-note bodies, **once each** (D-11) |

⚠ **The "once" in D-11 is a cardinality constraint the donor's mechanism cannot express** — 149's
required-caveat check is presence-only. Either accept presence-only (recommended; "once" is a wording
convention for the human review, not a machine rule) or add a count assertion. **Do not silently
convert a wording convention into an unenforced machine claim.**

⚠ **`\bproven\b` is case-insensitive and fires on the word inside a filename or an id.** Check every
candidate `_DEFAULT_TARGETS` member for incidental hits before committing the list.

### C-7. `_DEFAULT_TARGETS` — concrete list, and who owns each addition

**Hard-coded, one path per line, no wildcard, all built from `_HERE`.** A `152-`-prefixed glob would
sweep in `152-CONTEXT.md`, `152-RESEARCH.md`, `152-DISCUSSION-LOG.md` (all carrying forbidden
vocabulary as discussion prose — **this very file does**), `fixtures/` (planted violations by design),
and the transcript (whose RED blocks necessarily quote forbidden text).

| # | Target | Owning plan | Note |
|---|---|---|---|
| 1 | `152-GH12-COMMENT.md` | the plan that authors it | OUT-01 draft |
| 2 | `152-GH21-COMMENT.md` | the plan that authors it | OUT-02 draft |
| 3 | `152-GH11-COMMENT.md` | the plan that authors it | OUT-03 draft |
| 4 | `152-RELEASE-NOTES-app.md` | the plan that authors it | OUT-04 draft — **carries the literal `write --sdp-relock`** |
| 5 | `152-RELEASE-NOTES-fw.md` | the plan that authors it | OUT-04 draft — same |
| 6 | `152-LEDGER.md` | the ledger plan | **D-12: mandatory** |
| 7…N | every `152-NN-SUMMARY.md` | ⚠ **the LAST plan only** | see the ordering trap below |

**Explicitly and permanently OUT** (state this in the module docstring, as 149 does):
`152-CONTEXT.md`, `152-RESEARCH.md`, `152-DISCUSSION-LOG.md`, `152-VALIDATION.md`,
`152-CLAIM-GATE-TRANSCRIPTS.md`, `fixtures/*`, every `152-NN-PLAN.md`.

⚠ **The 149 ordering trap, restated for this list.** The never-vacuous + fail-closed-on-missing
branches have **no** exit-0-on-nothing-scanned escape hatch, so **any `_DEFAULT_TARGETS` entry that
does not exist on disk makes the gate return rc=1.** 149 hit this exactly: it extended its list in
plan 08 and *still* had to leave `149-08-SUMMARY.md` out until it was written, scanning it via argv
instead. Consequences:

- Entries 1-6 may only be added **after** the artifacts exist. Practically: one plan builds the gate
  armed at a minimal existing set, and a **later** plan extends `_DEFAULT_TARGETS`.
- **The final `152-NN-SUMMARY.md` cannot be a default-list member at the time the extending plan
  runs.** Scan it via positional argv, and record the argv run in the transcript. 149's transcript has
  a §"Final target list (plan 08 close-out)" section that does exactly this — copy that shape.
- Every basename added to `_DEFAULT_TARGETS` must simultaneously gain a `_CAVEAT_RULES` entry, or the
  fail-closed default demands the *full* caveat set from it. 149 has a dedicated test for this
  (`test_every_default_targets_basename_has_a_caveat_rule_entry`).

### C-8. Fixture suite + transcript — the shapes to copy

**Fixtures** (`149-*/fixtures/`, 11 files, measured today): two clean controls
(`clean_control.md`, `clean_control_second.md`) and nine planted files, one per added/modified label
(`planted_at28c256_fixed.md`, `planted_graduation.md`, `planted_issue_closed.md`,
`planted_missing_caveat.md`, `planted_page_size_proven.md`, `planted_proven_unqualified.md`,
`planted_support_status_change.md`, `planted_forbidden_claim.md`,
`planted_extended_overclaim_08.md`). All small (383-708 B).

**Suite** (`test_check_claims_v132.py`, 721 lines, **20 tests, 0.82 s**, green today). Its legs:

| Leg class | Tests |
|---|---|
| Behaviour | clean-control exits 0; planted overclaim → non-zero; planted missing caveat → non-zero; planted bare claim word → non-zero |
| Fail-closed | non-existent target → non-zero; explicitly empty target list → non-zero (never-vacuous) |
| Contract | `PASS:` line names every scanned file; positional argv beats the env seam |
| Arming | armed against the **real** phase artifacts; defaults resolve inside this phase dir; default basenames carry this phase's prefix |
| Caveat map | every default basename has a `_CAVEAT_RULES` entry; unknown basename → **full** set; exempt basename passes without caveats **but still fails on a forbidden phrase** |
| Narrowing | the required phrase alone does **not** trip the narrowed `proven` pattern; an unqualified `proven` **still does** |
| Non-target | the transcript is not a gate target; CONTEXT/RESEARCH/DISCUSSION-LOG are not gate targets |
| **Meta** | **`test_every_forbidden_pattern_has_a_planted_fixture`** — for every ADDED/MODIFIED label, a committed fixture that trips **exactly that label and no other** (leg isolation), fails for the forbidden phrase and **not** a missing caveat, and asserts the fixture set is non-empty first |

**152 must therefore ship fixtures for at least three labels**: the new `sdp-relock-as-shipped`, the
new bare-flag companion, and the modified `issue-closed`. Plus `proven-unqualified` if its lookbehind
changes (§C-6 recommends it does not — then no new fixture is owed for it, but the two narrowing
tests still transcribe).

⚠ **Behavioural legs must be `subprocess`-driven, never an in-process import** — 149's docstring:
*"so a passing suite proves the **gate**"*, and the gate's own filename (`152-check-claims.py`) is not
a valid Python identifier anyway.

⚠ **Filename discipline (measured, load-bearing).** 149's docstring `:57-64`: *"`test_check_claims_v132.py`,
deliberately distinct from every sibling phase's same-shaped suite — pytest's default `prepend` import
mode **collides on a repeated basename** run from `/workspaces`."* **152's suite must be
`test_check_claims_152.py`** (or similar), never a second `test_check_claims_v132.py`.
`[VERIFIED: 149 docstring + 20-test green run, 2026-08-21]`

⚠ **Fixture-authoring hazard, measured by 149:** *"several candidate fixture wordings tripped an
UNINTENDED second label (writing out a forbidden label's own name in a fixture's HTML comment, for
instance, can itself contain a forbidden substring) and were rewritten before being committed."* Run
each candidate fixture through the scanner before committing it.

**Transcript** (`149-CLAIM-GATE-TRANSCRIPTS.md`, 274 lines). Section shape:

```text
  # 152-CLAIM-GATE-TRANSCRIPTS.md — RED/GREEN evidence for `152-check-claims.py`
  ## RED — one block per forbidden-pattern label this phase added or modified
  ### 1. `sdp-relock-as-shipped` — ADDED  (plant = the roadmap's pre-amendment criterion-1 wording)
  ### 2. bare `--sdp-relock` companion — ADDED
  ### 3. `issue-closed` — MODIFIED (32 dropped), with the three still-fires controls
  ## RED — donor-carried rows, for completeness
  ### N. Missing required caveat
  ## GREEN — the real default targets, no argv, no seam
  ## Paired suite — `python3 -m pytest test_check_claims_152.py -q -o addopts=""`
  ## What this transcript does and does not prove
  ## Extended target list (plan NN)   ← RED w/ the real extended list + one plant, GREEN, ARGV
  ## Final target list (close-out — the last SUMMARY added via argv)
```

⚠ **Standing trap: a pre-authored gate leg can be structurally UNREACHABLE.** RED proves nothing until
the leg is **seen to pass**, and the fix must be **locator-only** — never a change to what the
assertion asserts.

### C-9. Posted mode (D-09) — the network half

Same `FORBIDDEN_PATTERNS` and `REQUIRED_CAVEAT_PATTERNS` tables, different source of text:

```bash
gh issue view 12 --repo henols/firestarter_prom --json comments \
  --jq '.comments[-1].body'          > /tmp/posted-gh12.md
gh release view "$TAG" --repo henols/firestarter_app --json body --jq '.body' > /tmp/posted-app.md
FIRESTARTER_CLAIMSCAN_TARGETS_152="/tmp/posted-gh12.md:/tmp/posted-app.md" \
  python3 152-check-claims.py
```

Two design points measured today:

1. **The env seam is the right vehicle** — it accepts absolute paths and `_required_caveats_for()` is
   keyed on **basename**, so a temp-file name outside `_CAVEAT_RULES` **fails closed to the full
   caveat set**. For posted comment bodies (which carry no caveat requirement) that would be a false
   RED. **The planner must either name the temp files to match the draft basenames, or add explicit
   `_CAVEAT_RULES` entries for the posted-mode filenames.** This is a real, easy-to-miss failure mode.
2. **A separate `--posted` argv mode is the cleaner alternative** to the env seam, keeping one code
   path for pattern evaluation and one for text acquisition. `[ASSUMED]` — a design recommendation,
   not measured.

---

## D. The Issue Threads — LIVE state, measured 2026-08-21

```bash
gh issue view <N> --repo henols/firestarter_prom \
  --json number,title,state,stateReason,createdAt,updatedAt,closedAt,comments
```

| # | Title | State | stateReason | Comments | Created | Verdict vs CONTEXT |
|---|---|---|---|---|---|---|
| **12** | AT28Cxxx Write Protection Enable/Disable missing | **OPEN** | — | **10** | 2024-09-15 | ✅ HOLDS |
| **21** | [dev test] at28c256 — FAIL (`00e121446ceb`) | **OPEN** | — | **2** | **2026-08-06** | ✅ HOLDS |
| **32** | [dev test] at28c256 — FAIL (`00e121446ceb`) | **CLOSED** | **COMPLETED** | 1 | 2026-08-07 | ✅ HOLDS — `closedAt: 2026-08-08T09:31:09Z` |
| **11** | Issues with AT28C256 Reading / Writing | **OPEN** | — | **18** | 2024-09-26 | ✅ HOLDS |
| **20** | [dev test] at28c256 — FAIL (`00e121446ceb`) | CLOSED | COMPLETED | 5 | 2026-07-30 | ✅ HOLDS |

`[VERIFIED: gh issue view --json, 2026-08-21]`

### D-1. gh#12 — the exact claim to retract

The 2026-07-30 comment (`henols`, id `IC_kwDOSX4ER88AAAABMfdMMg`, 5093 chars,
`…/issues/12#issuecomment-5133257778`) contains, at its line 15, verbatim:

> `- `firestarter dev sdp <chip> enable|disable` gives standalone control in both directions — chip name`

**That is the sentence to retract.** `[VERIFIED: gh issue view 12 --json comments | grep, 2026-08-21]`

### D-2. ⚠ **NEW — gh#12's LAST comment is 2026-08-06, not 2026-07-30**

CONTEXT names only the 2026-07-30 comment. Measured, there is a **later** one
(`henols`, 2026-08-06T08:08:38Z, 665 chars, `#issuecomment-5202072813`), quoted in full:

> *"Now is there is a new version of the pre release of firestarter. Install firestarter with the
> --pre flag and update the firmware. Hopefully it will work much better so you are free to test all
> your available eproms. Instead of reporting a manual issue about EPROMs that don't work at
> firestarter_prom, run firestarter dev test and when you are asked to create an issue do that, I
> also want you to test and report issues for working EPROMs so I keep track of what is working. …"*

**An identical 665-char comment was posted the same minute on gh#11** (2026-08-06T08:08:19Z,
`#issuecomment-5202069494`). Two things follow:

1. **This is the comment that generated gh#21.** AndersBNielsen filed gh#21 at 2026-08-06T08:21:06Z —
   **13 minutes later** — and gh#32 the next day. The call to action worked, and it pointed at a
   version that had no release notes and still had `fw_board_identity=None`.
2. **OUT-01's reply is the third `henols` comment in a row on gh#12, and the second "try the new
   pre-release" message.** That materially affects tone: a reply that says "install the pre-release
   and test" without acknowledging that the last one already said that, and that the run then failed
   for a reason we have since fixed, reads as a repeat. `137-GH12-COMMENT.md`'s *"name the shortfall
   before naming the gain"* discipline applies to this too.

`[VERIFIED: gh issue view --json comments, 2026-08-21]`

### D-3. ⭐ gh#21 — the report body is a **directly citable oracle** for OUT-02

**Author: `AndersBNielsen`** (not datapaganism — CONTEXT does not say). Both existing comments are
`henols`: the consolidated-reports table folding #32 (2026-08-08T09:31:07Z, 577 chars) and the
`devtest-triage` datasheet cross-check (2026-08-08T09:46:28Z, 3121 chars). **There is no community
comment on gh#21.**

The issue body carries, verbatim:

```json
"auto_capture": {
  "host_version": "3.0.0b15",
  "fw_board_identity": null,
  "hw_revision": "Rev 2.0-class, Override HW: Rev 2.3",
  "chip": "at28c256",
  "protocol": "13",
  "chip_id_expected": null, "chip_id_actual": null, "chip_id_mismatch_reason": null
},
"transport_health": { "cobs_errors": "not measured", … "transport_suspect": false },
```

and its step table:

| Step | Verdict | Reason |
|---|---|---|
| id | NA | no chip-id in DB entry |
| read | OK | - |
| **blank-check** | **BAD** | - |
| **write** | **BAD** | - (fingerprint `"indeterminate"`) |
| **verify** | **BAD** | - (fingerprint `"indeterminate"`) |
| erase | NA | **`protocol 0x0D (28C family) has no erase operation; each page write auto-erases internally`** |

`schema_version: "1.2"`, `generated: 2026-08-06T08:20:45Z`, `banner: {n_ran: 4, m_applicable: 4}`.
`[VERIFIED: gh issue view 21 --json body, 2026-08-21]`

**Three OUT-02 hooks this hands over, each citable to the reporter's own paste:**

1. **`"fw_board_identity": null`** — the PROV-01 defect, in the public record, and (§A-1) **still live
   on `origin/beta` today**, so the criterion-2 phrasing *"answerable because the report now
   identifies its firmware"* is true **only after** the merge D-04 puts in this phase. Posting it
   before the merge would be false in every published version. **This is the load-bearing measurement
   of the whole phase and it re-verifies.**
2. **The erase NA reason string is exactly the claim Phase 153 falsified** (§B-10's first
   "must not repeat"). The comment can quote the reporter's own line and say the reason text is now
   false and has been corrected in the tree.
3. **The report ran `3.0.0b15`**, not `b16` — filed 12 minutes after being told to install `--pre`.
   Any statement about what has changed since must be measured against `b15`, not against the latest
   pre-release.

### D-4. ⚠ gh#11 — CONTEXT's "unanswered" is imprecise, and the correction changes the reply

CONTEXT: *"Unanswered: datapaganism's 2026-08-03 question about `erase not supported` and hacking a
`CMD_ERASE` into `configure_eeprom28c`."* **Measured: it was answered — with a promise.**

Comment timeline (all measured):

| Date | Author | Substance |
|---|---|---|
| 2025-09-28 | `AndersBNielsen` | The page-write analysis (705 chars): *"When programming more than a single byte the 28C256 goes into page write mode. In page write mode it accepts up to 64 bytes - if more than 64 bytes ar…"* |
| 2026-07-30 | `henols` | 4863 chars — the FIX-06 conflation answer CONTEXT cites. |
| 2026-07-30 | `datapaganism` | *"Could not erase — https://…/issues/20"* |
| **2026-08-03T09:33** | `datapaganism` | *"I tried hacking in an erase sequence in the firmware (added a CMD_ERASE to configure_eeprom28c) but I am not sure how I can enable firestarter to trig…"* |
| **2026-08-03T09:36** | `henols` | **"It's not probably implemented yet, I will soon get it pushed and I will keep you posted."** ← **an answer, and a commitment** |
| 2026-08-03T09:47 | `datapaganism` | *"Yes but I am not using discord"* — confirms the reply-on-the-issue preference |
| 2026-08-06T08:08 | `henols` | the 665-char `--pre` call to action (§D-2) |

`[VERIFIED: gh issue view 11 --json comments, 2026-08-21]`

**Planning consequence for OUT-03.** The obligation is **stronger** than CONTEXT implies and different
in kind: it is a **kept promise, 18 days late**, not a broken silence. The reply should discharge
*"I will soon get it pushed and I will keep you posted"* — Phase 153 pushed exactly the thing
datapaganism hand-hacked, by the software path, and they are the only person who has ever run this
code on real AT28C silicon. Apologising for silence would be inaccurate. **CONTEXT's "unanswered"
framing must not be carried into the reply text.**

### D-5. ⭐ The post-verification oracle — what is sound, and what is not

**Not sound:** `updatedAt`. Measured at issue level, gh#12's `updatedAt` is `2026-08-06T08:08:39Z` —
i.e. it tracks the last comment's **creation**, so it bumps whether or not anything was edited.

**Measured refinement CONTEXT does not have:** at the **comment** level, `updatedAt` is
**`null` on all 30 comments across gh#12/#21/#11**. So a non-null comment-level `updatedAt` *is* an
edit signal — but it is useless as a *landed* oracle, because a freshly created comment has
`updatedAt: null` too. `[VERIFIED: gh issue view --json comments --jq '.comments[].updatedAt',
2026-08-21]`

**Sound oracles, in order of strength:**

| Oracle | Command | Proves |
|---|---|---|
| **Body-content re-read (strongest)** | `gh issue view N --json comments --jq '.comments[-1].body'` → diff against the frozen draft | The exact text we authored is what GitHub stored. **This is D-09's posted mode and is the only sound proof.** |
| Comment id + URL capture | same query, `--jq '.comments[-1] \| {id, url, createdAt}'` | A durable, quotable handle for the ledger (e.g. `#issuecomment-NNNN`). |
| Comment-count delta | count before, count after | Cheap non-vacuity: 10 → 11 on gh#12, 2 → 3 on gh#21, 18 → 19 on gh#11. Cannot prove *which* text. |
| Release body length + content | `gh release view TAG --json body -q '.body \| length'` then diff | 0 → N proves a body landed; the diff proves it is ours. |
| Issue still OPEN | `--json state` | Criterion 2 / 146 D-07: comment posted, **issue stays OPEN**, body **not** edited. |

**Use body-content re-read as the primary; use count delta as the non-vacuity guard; record the
comment id/URL in `152-LEDGER.md`.** Never `updatedAt`.

---

## E. Merge / Cut Mechanics (D-04)

### E-1. App: `firestarter_app/.github/workflows/beta-release.yml` — 134 lines

| Property | Measured value |
|---|---|
| Trigger | `push: branches: [beta]` **plus** `workflow_dispatch` with an optional `beta_version` (PEP 440) input |
| `paths-ignore` | **none** — deliberately removed. The header comment records PR #46 hitting exactly that trap: a `.github/**`-only merge cut nothing while the firmware repo cut from the same class of change, so *"the two repos disagreed about what beta means."* |
| Release action | `softprops/action-gh-release@v2`, `prerelease: true`, `make_latest: false`, `tag_name: ${{ steps.version.outputs.version }}` |
| **`body:`** | **ABSENT** — bodies are only ever added manually via `gh release edit --notes-file` |
| Target commit | `target_commitish: ${{ steps.release_target.outputs.sha }}` — the **post-auto-commit** SHA, so the tag lands on the commit containing the bumped `__version__`, not the trigger SHA (Phase 20 E2E-02 fix) |
| Token | `secrets.PERSONAL_ACCESS_TOKEN` for the release step |
| Publish loop | none — `git-auto-commit-action` pushes with the default `GITHUB_TOKEN`, which does not trigger workflow runs (confirmed empirically in the firmware repo) |

`[VERIFIED: read .github/workflows/beta-release.yml, 2026-08-21]`

### E-2. Firmware: the file is **`beta-build.yml`**, not `beta-release.yml`

CONTEXT says "the firmware equivalent" without naming it. Measured: `firestarter/.github/workflows/`
contains `beta-build.yml`, `build.yml`, `py32f071.yml` — **there is no `beta-release.yml`.**

| Property | Measured value |
|---|---|
| Name | `Firestarter beta pre-release build` |
| Trigger | `push: branches: [beta]` **plus** `workflow_dispatch` (with the rehearsal inputs from Plan 128-07) |
| Release action | `softprops/action-gh-release@v2` at `:330`, `prerelease: true` |
| **`body:`** | **ABSENT** — bodies manual |
| `files:` | `.pio/build/**/firestarter_*.hex` and `build/py32f071/firestarter_*.hex` (two entries, required because PlatformIO and the ARM build write to different roots) |
| Rehearsal safety | `tag_name` is overridden to `format('rehearsal-{0}', github.run_id)` when `rehearsal == 'true'`, so a rehearsal makes no real tag |

`[VERIFIED: read .github/workflows/beta-build.yml, 2026-08-21]`

### E-3. ⚠ **PyPI is AUTOMATIC now — a CONTEXT delta**

CONTEXT (and project memory) list *"PyPI needs manual dispatch"* as a standing CI gotcha at a
milestone cut. **Measured: it does not.**

```yaml
  pypi:
    needs: github
    uses: ./.github/workflows/publish.yml
    with:
      tag: ${{ needs.github.outputs.version }}
    secrets: inherit
```

The workflow's own header comment records why this exists and what it fixed:

> *"the `release.published` event does NOT reach `publish.yml` for betas: the Release step creates the
> release with `secrets.PERSONAL_ACCESS_TOKEN`, and that PAT lacks `workflow` scope, so GitHub
> suppresses the downstream event. The failure was silent — **GitHub reached b17 while PyPI stopped at
> b15**, and nothing reported an error. Calling `publish.yml` directly removes the dependency on event
> delivery and on any credential's scope."*

`publish.yml` accepts both a `release:` trigger (stable path) and a `workflow_call` with a `tag` input
(beta path). **Empirical confirmation it works:** app `3.0.0b22`'s GitHub release is
2026-08-19T19:40:06Z and its PyPI upload is 2026-08-19T19:40:29Z — **23 seconds later.**

**So no manual PyPI dispatch is expected for the beta cut**, which also removes the `gh workflow run`
blocker from the critical path. `[VERIFIED: beta-release.yml + publish.yml + PyPI JSON, 2026-08-21]`

⚠ **But the stable channel is still divergent** (§A-5): `2.0.8` is on GitHub and absent from PyPI.
The plan must verify PyPI **independently of GitHub** after the cut — `curl -s
https://pypi.org/pypi/firestarter/json` — and must not infer PyPI state from `gh release list`.

### E-4. Known CI gotchas at a milestone cut

| Gotcha | Status |
|---|---|
| **Codegen drift vs ruff** | `codegen.py` emits ruff-clean, format-stable `messages.py` — do **not** hand-normalize. Firmware `messages.h` is codegen-generated and ID-only; wording-only changes produce a **zero** diff. `[CITED: project memory]` |
| **`.[dev]` vs `.[test]`** | Distinct extras; the wrong one fails the CI leg. `[CITED: project memory]` |
| **Devcontainer py3.12 masks app CI (py3.11)** | Local greens can be fail-open. `[CITED: project memory]` |
| **Sibling-layout masking** | ⚠ **CONTEXT Hard Precondition 3: point the sibling root at an empty dir before any beta push** — the devcontainer's sibling layout masks CI-only test defects. |
| **`test_flash_path_record_sync.py` asserts WHOLE-repo porcelain** | **Commit before running the suite.** `[CITED: project memory]` |
| **Every merge to `beta` cuts a pre-release, by design** | Two merges (app + fw) = two cuts. Meta has no release CI and cuts nothing. |
| **Local `beta` lags `origin/beta`** | Re-read `origin/beta`'s version before acting on it; ff-only to `origin/beta` before any tag. `[CITED: project memory]` |
| **`gsd-tools query commit` can switch branches** | Its unanchored `##…vX.Y` regex scrapes ROADMAP prose. **Check `HEAD` after every commit call.** `[CITED: project memory]` |

### E-5. What `/gsd-complete-milestone` is left holding — and the no-re-merge handoff

Once 152 has merged and cut, `/gsd-complete-milestone` still owns: archiving `ROADMAP.md` and
`REQUIREMENTS.md` to `.planning/milestones/v1.32-*`, the `MILESTONES.md` §v1.32 entry, the meta `v1.32`
tag, gitlink re-pinning to the published commits, and the stable-promotion decision (**operator-gated
— "nothing is stable until I say so"**).

**It must be told the merges are already done.** CONTEXT Hard Precondition 2 and v1.30's measured
failure mode: v1.30 closed via a **squashed** PR to `beta` (PR #44 → `568e58b`), which made
`git merge-base --is-ancestor` a **false negative** — the close then looked un-merged.

**Recommended handoff record — a dedicated `152-MERGE-RECORD.md`, gate-scanned, containing:**

1. The three PR numbers and URLs, and each PR's **merge method** (squash / merge-commit / rebase),
   because that is what determines whether SHA ancestry works at all.
2. For each sub-repo, the **`git cherry origin/beta HEAD` output captured after the merge** — expected
   all-`-`. This is the oracle that survives a squash; `--is-ancestor` is not.
3. The two **observed** cut tags, read from `gh release list` with the command and timestamp, never
   predicted.
4. The **PyPI-side** confirmation, read from `pypi.org/pypi/firestarter/json`, separately.
5. The post-merge `origin/beta` SHA for each sub-repo, and the gitlink each should be pinned to.
6. A one-line, unambiguous instruction: **"the beta merges for v1.32 are COMPLETE; do not re-merge;
   verify with `git cherry`, never `--is-ancestor`."**

⚠ Also note for the close: **`/gsd-new-milestone` step 6 `phases.clear` is DESTRUCTIVE — skip it**
(it hard-deletes 50+ phase dirs), **milestone close breaks its own record gates** (archived sections
orphan `lines=N`; `git rm REQUIREMENTS.md` trips target lists), and **`.planning/research/` is not
archived at close** — `git mv` it before the next milestone's researchers run. `[CITED: project
memory]`

---

## F. Plan / Wave Shape — recommendation

**Constraints the shape must satisfy:** one-writer-per-file across plans; the gate GREEN before the
first post (D-03/OUT-05); every public post behind its own blocking operator gate (D-03); the
`_DEFAULT_TARGETS` ordering trap (§C-7); `commits_land_in:` for sub-repo work; and D-08's ordering
already discharged (153 complete).

### The one-writer collisions, named

| File | Writers wanted | Resolution |
|---|---|---|
| **`ROADMAP.md`** | D-05 criterion-2 amendment · D-11 criterion-5 amendment · the `**Plans**: TBD` → real line · §A-11(1) the `gh#21/#32/#11/#12` bullet at `:37` · §A-11(3) the `database.py:621` citation | **ONE plan owns all five.** Do them in a single hand-edit task. |
| **`REQUIREMENTS.md`** | OUT-01 + OUT-04 pre-amendment text · OUT-02's gh#32 phrasing · §A-11(2) the Coverage block · §A-11(3) the `:621` citation · the OUT-01…05 checkbox flips | **ONE plan.** ⚠ Executors are measured to skip `update_requirements` when told "no state writes" — say explicitly that the OUT checkboxes must flip. |
| **`PROJECT.md`** | D-15 workstream-table row for 153 · workstream 4's description · the Phase 121 D-12 premise correction | **ONE plan.** Verify first — 153 may have landed part of it (§B-11). |
| `152-check-claims.py` | the building plan · the `_DEFAULT_TARGETS`-extending plan | **Two plans, sequenced** — unavoidable per §C-7 and matching 149's precedent. |
| `152-LEDGER.md` | one plan | Must be written **after** the versions are read (it captures live HEADs and observed tags). |

### Recommended decomposition — 11 plans, 6 waves

**Wave 0 — the gate, armed and proven, before anything public** *(no network, no merges)*
1. `152-check-claims.py` + `fixtures/` + `test_check_claims_152.py` + the RED half of
   `152-CLAIM-GATE-TRANSCRIPTS.md`. Armed initially at a **minimal existing set**. Must contain the
   **plant-and-revert seen RED** for `sdp-relock-as-shipped`, the bare-flag companion, and the
   modified `issue-closed` with its three still-fires controls. **No pass is believed until a RED is
   seen and the fix is locator-only.**

**Wave 1 — record corrections** *(parallel; one writer per file)*
2. `ROADMAP.md` — all five edits above, as labelled correction blocks + register entries. Re-run
   `check_record_corrections.py` (300 s timeout, measured 23 s).
3. `REQUIREMENTS.md` — all five edits above. **Not** a `check_record_corrections.py` target.
4. `PROJECT.md` — D-15 remainder. Re-run the record gate.

**Wave 2 — the drafts** *(parallel; each its own file; each ends with a gate run)*
5. `152-GH12-COMMENT.md` — adapt `137-GH12-COMMENT.md`, **commit the diff against the 137 original**
   (D-14). Must not contain the literal `write --sdp-relock`.
6. `152-GH21-COMMENT.md` — built on §D-3's citable oracles; states the matched-firmware requirement
   (§B-8).
7. `152-GH11-COMMENT.md` — discharges the 2026-08-03 promise (§D-4), FIX-06 framing, AndersBNielsen's
   2025-09-28 page-write analysis acknowledged.
8. `152-RELEASE-NOTES-app.md` + `-fw.md` — version-agnostic; `146-RELEASE-NOTES-app.md`'s opening
   paragraph reused verbatim for the version-read discipline; the withdrawal sentence in the
   **mandated shape** (§C-4); the D-11 non-claim **once** per body.

**Wave 3 — the merges and the cuts** *(sequential, `commits_land_in:` set, operator-gated)*
9. Point the sibling root at an empty dir. Commit everything. Three PRs to `beta` (fw, app, meta).
   ⚠ **The app merge is not a fast-forward — 7 commits behind, conflicts possible on the PR #52
   files** (§A-1). Then: read both cut tags from `gh release list`; verify PyPI independently; write
   `152-MERGE-RECORD.md` (§E-5).

**Wave 4 — extend the gate to the real target list, then post** *(operator-gated per artifact)*
10. Extend `_DEFAULT_TARGETS` to the six named artifacts + the SUMMARYs that exist; add the matching
    `_CAVEAT_RULES` entries; fill the tags into the two bodies; **GREEN in file mode**; then five
    posts, **each behind its own blocking checkpoint (D-03)**, each followed by a **posted-mode**
    gate run and a body-content re-read (§D-5). Mark
    `todos/pending/gh12-followup-after-dev-sdp-retirement.md` resolved when OUT-01 posts.

**Wave 5 — ledger and close-out**
11. `152-LEDGER.md` (live-captured HEADs, observed tags, per-gate counts, every claim paired with its
    explicit non-claim — D-12); the transcript's final-target-list section (last SUMMARY via argv);
    OUT-01…05 checkbox flips.

### Frontmatter requirements, per plan

- **Every posting plan** must restate: **⚠ this phase must NOT be run under `--auto`/`--chain`** —
  and note that `autonomous: false` alone is **not** self-protecting.
- **Wave 3's plan** needs `commits_land_in:` naming both sub-repos. ⚠ **Worktrees leave submodules
  EMPTY and the gate under-detects** — READ-only plans break too.
- Any plan touching `PROJECT.md`/`STATE.md`/`ROADMAP.md` must budget a **300 s** timeout for the
  record gate (measured 23 s, but a short timeout returns rc=124 and reads like a RED).

---

## G. The Remaining Discretion Items

### G-1. Where the D-05 / D-11 / D-15 amendments are recorded

**Recommendation: labelled correction blocks in place, plus a register entry in `152-LEDGER.md` —
not a separate correction register.**

Reasoning, measured:

- `check_record_corrections.py` exempts by **five mechanisms** — `block`, `line-label`,
  `inline-history`, `inline-allow`, `superseded` — and today tallies
  `{block: 23, line-label: 4, inline-history: 6, inline-allow: 10, superseded: 12}` with rc=0. It
  needs the marker to be **in the edited file**, not in a sibling register. So the in-place labelled
  block is not optional. `[VERIFIED, 2026-08-21]`
- 146 used **both** (`146-CORRECTIONS.md` + `146-CLAIM-FACTCHECK.md` + `146-DOC-CHECK-RECORD.md`), but
  that phase had 18 research corrections across two repos. 152 has ~8 in three `.planning` files.
- **D-12 makes `152-LEDGER.md` a hard gate target** and states *"the ledger is where the per-claim
  pairing discipline now lives."* A separate register would be a second document that must also be a
  gate target (146's own reason for including its ledger), for no gain.
- ⚠ **`check_record_corrections.py`'s `superseded` mechanism is line-keyed and must be avoided.**
  Use `⚠ CORRECTION` blocks / line labels / `recordscan:history` / `recordscan:allow` — all
  position-independent. §A-12 confirms no live `lines=N` marker sits in any file 152 edits, and 152
  must not introduce the first one.

### G-2. Whether the firmware release notes mention the `.hex` assets and the leonardo ceiling

**The `.hex` assets — YES, and ⚠ there are FOUR, not three.**

```bash
gh release view 3.0.0b19 --repo henols/firestarter --json assets --jq '.assets[].name'
# firestarter_leonardo.hex
# firestarter_py32f071.hex
# firestarter_uno.hex
# firestarter_uno328pb.hex
```

`[VERIFIED, 2026-08-21]` — CONTEXT's discretion item says "three `.hex` assets". Measured: **four**.
`firestarter_py32f071.hex` has been published since v1.23 Phase 128. **A note saying "three assets"
would be a factual error in the most public artifact.**

Say: which board each asset targets, and that `firestarter fw --install` picks the attached board.
⚠ **Do not promise `--board` targeting** — measured project behaviour is that `fw --install` **flashes
the ATTACHED board and ignores `--board`**. `[CITED: project memory]`
⚠ **`firestarter_py32f071.hex` must carry its standing non-claim** — no PY32F071 PCB exists and
nothing in that port has ever run on the silicon.

**The leonardo ceiling — YES, but only as a maintainer-facing note, and only with §A-9's re-measured
numbers.** Recommendation: one short paragraph, because it is genuinely user-relevant (a leonardo user
should know the image is 1042 B from bricking its own USB bootloader if a future build grows), and
because the deferred split-firmware phase needs the figure on the public record. **State exactly two
numbers and never conflate them:**

> `leonardo` flash used **27630 B** of 32768 B. The Caterina USB-bootloader boundary sits at
> **28672 B**, leaving **1042 B**, and it is **UNGUARDED** — `board_upload.maximum_size` was raised to
> the real 32768 B, so the linker no longer refuses a build that would overwrite the bootloader.
> (Separately, and *not the same number*: the MERGE-05 size band's leonardo headroom is **0 B** — the
> measured delta against `size_baseline_base01.json` is **+724 B**, exactly equal to the four-term
> allowance `96 + 210 + 288 + 130`.)

⚠ **Do not present the split-firmware relief as planned or queued** — CONTEXT defers it explicitly and
says *"do not fold into 152 or 153."* Name it as an unaddressed constraint, not a roadmap item.

---

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md` (meta) and `firestarter_app/CLAUDE.md`:

| Directive | Bearing on Phase 152 |
|---|---|
| Meta repo tracks **only** `.planning/` and `.claude/`; neither sub-repo is committed here | 152's own artifacts all live in `.planning/`. Sub-repo work is submodule-internal — `commits_land_in:`. |
| **Serial protocol changes must be kept in sync** between `serial_comm.py` and `firestarter.cpp` | Not applicable — 152 makes no code change (D-06). |
| **Constants/flag bits are duplicated** between `constants.py` and `firestarter.h` — change both together | Not applicable to 152; relevant only as background to 153's `FLAG_CAN_ERASE` work. |
| **`chip_database.json` is GENERATED** — never hand-edited; fix the decode function | 152 makes no DB change. Any outward sentence about a DB value must name it as generated from `infoic.xml` + the override rules. |
| `firestarter_app/CLAUDE.md` §"Database Pipeline" — the **WARNING-5 protocol override** promotes AT28C256 from upstream `0x07` to `0x0D`, and 12 V on that pinout's pin 1 is a damage path | Directly load-bearing: §A-7's `vpp_mv: 12000` must never be cited as evidence the hardware erase path is available. |
| Board buffer sizes differ (Uno 512 B, Leonardo 1024 B) | Background only. |
| **Firmware `messages.h` is codegen-generated and ID-only** | 152 writes no messages. Relevant only as a CI gotcha (§E-4). |
| Project skills present: `devtest-triage`, `devtest-rootcause` | **Relevant background to gh#21/#11.** `devtest-triage` is what closed gh#32 as a fold into gh#21 (D-05), and **only `devtest-triage` closes a `dev test` issue** — 152 does not close any. `devtest-rootcause` knows `chip_database.json` is generated. |

---

## Standard Stack

No new libraries. Everything this phase needs is already in the tree or the environment.

### Core

| Tool | Version | Purpose | Why standard |
|---|---|---|---|
| `gh` CLI | installed, authenticated | Read + post issue comments; read + edit release bodies; read release lists | Used live throughout this session. `gh issue view/comment`, `gh release view/edit/list`. |
| `git` | installed | Three PRs to `beta`; `git cherry` as the merge oracle | `git cherry` is the *only* correct oracle after a squashed merge (§A-1 proves 5 false negatives waiting). |
| Python 3 | **3.12.13** (devcontainer) | The claim gate, its suite, DB re-derivations | ⚠ CI runs **3.11** — a local green can be fail-open. The gate itself uses only `os`/`re`/`sys` so version risk is nil. |
| `pytest` | installed | The paired gate suite | `-q -o addopts=""` — ⚠ the project's `addopts` is `-ra -q`, and doubling `-q` **suppresses the count line**. |
| `curl` + `python3 -m json.tool` | installed | Independent PyPI verification | GitHub state is not PyPI state (§A-5). |

### Supporting

| Asset | Purpose | When |
|---|---|---|
| `149-check-claims.py` (531 lines) | The gate's direct donor | Sibling it with the four renames (§C-2). |
| `test_check_claims_v132.py` (721 lines, 20 tests) | The suite's donor | Copy legs; **rename the file** (§C-8). |
| `149-CLAIM-GATE-TRANSCRIPTS.md` (274 lines) | Transcript shape | §C-8. |
| `149-*/fixtures/` (11 files) | Fixture shape | §C-8. |
| `137-GH12-COMMENT.md` (46 lines) | OUT-01's base (D-14) | Adapt; commit the diff. |
| `137-LEDGER.md`, `146-LEDGER.md` | Ledger shape, live-HEAD-capture discipline | `152-LEDGER.md`. |
| `146-RELEASE-NOTES-app.md` opening paragraph | Version-read discipline, **verbatim reusable** | Both bodies. |
| `137-RELEASE-NOTES-app.md` "Removed" section | The correct `dev sdp` mapping | OUT-04's Removed section. |
| `check_record_corrections.py` (Phase 130) | Record-correction gate over PROJECT/STATE/ROADMAP | Re-run after every hand-edit. |

### Alternatives Considered

| Instead of | Could use | Tradeoff |
|---|---|---|
| `git cherry` | `git merge-base --is-ancestor` | **Measured false negative** — v1.30's squash, plus 5 live patch-id matches today (§A-1). Never use it. |
| Body-content re-read | `updatedAt`, or a blob SHA of the draft | `updatedAt` bumps on creation; a blob SHA proves intent, not storage (D-09). |
| Negative lookahead (§C-4) | verb allow-list / per-file rule / proximity window | All three fail OPEN or are refused by donor precedent. |
| Hand-editing ROADMAP/REQUIREMENTS | `gsd-tools` roadmap/requirements verbs | The verbs run `_normalizeMd` over the **whole file** — blast radius. Hand-edit (D-05). |

**Installation:** none. **Version verification:** not applicable — no packages are added.

## Package Legitimacy Audit

**Not applicable.** Phase 152 installs **zero** external packages in either ecosystem. It writes
Markdown into `.planning/`, one stdlib-only Python script (`os`, `re`, `sys`), one pytest suite, and
makes git/`gh` calls. No `npm install`, no `pip install`, no `cargo add`.

| Package | Registry | Verdict | Disposition |
|---|---|---|---|
| *(none)* | — | — | — |

**Packages removed due to `[SLOP]` verdict:** none.
**Packages flagged as suspicious `[SUS]`:** none.

⚠ One conditional exception, from CONTEXT §canonical_refs: reading `AT28C256.pdf` requires
`pip install pypdf 'cryptography>=3.1'` (the file is AES-encrypted; `pdftotext` is absent here).
**This research did NOT install them** — D-06 says the datasheet findings are established from primary
sources and must not be re-derived. If a plan needs one page reference confirmed, `pypdf` and
`cryptography` are both long-established, high-download PyPI packages `[ASSUMED — not verified against
the registry this session]`, and the install should be gated behind a `checkpoint:human-verify`.

---

## Architecture Patterns

### System Architecture Diagram

```
                      ┌───────────────────────────────────────────────┐
   .planning/         │  RECORD CORRECTIONS (hand-edited, in place)   │
   (meta repo)        │  ROADMAP.md · REQUIREMENTS.md · PROJECT.md    │
                      │  labelled ⚠ CORRECTION blocks + register      │
                      └───────────────┬───────────────────────────────┘
                                      │ re-run
                                      ▼
                      ┌───────────────────────────────────────────────┐
                      │  check_record_corrections.py  (Phase 130)     │
                      │  targets PROJECT/STATE/ROADMAP · rc must be 0 │
                      └───────────────────────────────────────────────┘

   ┌──────────────────────────────────────────────────────────────────────────┐
   │ 152-check-claims.py   ── ONE pattern table, TWO text sources (D-09) ──   │
   │                                                                          │
   │  FORBIDDEN_PATTERNS (17 inherited + 2 new + 1 modified)                  │
   │  REQUIRED_CAVEAT_PATTERNS (2)   _CAVEAT_RULES (fail-CLOSED by basename)  │
   │                                                                          │
   │   FILE MODE (default, offline)          POSTED MODE (opt-in, network)    │
   │   _DEFAULT_TARGETS, hard-coded          gh issue view --json comments    │
   │   from _HERE, no wildcard               gh release view --json body      │
   └────────┬───────────────────────────────────────────────┬─────────────────┘
            │ must be GREEN before                          │ must be GREEN after
            ▼                                               ▼
   ┌──────────────────────┐   proven by   ┌──────────────────────────────────┐
   │ 5 DRAFTS + LEDGER    │◄──────────────│ fixtures/ (per-label, isolated)  │
   │ gh12 · gh21 · gh11   │               │ test_check_claims_152.py (~20)   │
   │ notes-app · notes-fw │               │ 152-CLAIM-GATE-TRANSCRIPTS.md    │
   │ 152-LEDGER.md        │               │   RED seen, then GREEN           │
   └──────────┬───────────┘               └──────────────────────────────────┘
              │
              │  ══ D-04: the merges must happen BEFORE any post ══
              ▼
   ┌───────────────────────────────────────────────────────────────────────────┐
   │ PR → beta (firestarter)   PR → beta (firestarter_app)   PR → beta (meta)  │
   │  39 ahead / 0 behind       85 ahead / 7 BEHIND ⚠         no release CI    │
   │  clean merge               conflicts possible            cuts nothing     │
   └──────────┬────────────────────────┬───────────────────────────────────────┘
              │ push to beta           │ push to beta
              ▼                        ▼
   ┌────────────────────────┐  ┌────────────────────────────────────────────┐
   │ beta-build.yml (fw)    │  │ beta-release.yml (app)                     │
   │ action-gh-release@v2   │  │ action-gh-release@v2, NO body:             │
   │ NO body:               │  │        │                                   │
   │ files: 4 × .hex        │  │        └──► pypi (needs: github)  AUTO ⚠   │
   └──────────┬─────────────┘  └────────────────────┬───────────────────────┘
              │                                     │
              ▼                                     ▼
   ┌─────────────────────────┐          ┌────────────────────────────────────┐
   │ gh release list  → TAG  │          │ pypi.org/pypi/firestarter/json     │
   │ (READ, never predicted) │          │ (verified INDEPENDENTLY of GitHub) │
   └──────────┬──────────────┘          └────────────────────────────────────┘
              │ tag filled into both bodies at cut time
              ▼
   ┌───────────────────────────────────────────────────────────────────────────┐
   │  FIVE PUBLIC ACTS — each behind its OWN blocking operator gate (D-03)     │
   │  gh issue comment 12 · 21 · 11    gh release edit --notes-file × 2        │
   │  ⚠ NEVER under --auto / --chain                                           │
   └──────────┬────────────────────────────────────────────────────────────────┘
              │ for each: re-read the stored body, diff vs the frozen draft
              ▼
   ┌───────────────────────────────────────────────────────────────────────────┐
   │ 152-LEDGER.md · 152-MERGE-RECORD.md   live HEADs, observed tags,          │
   │ comment ids/URLs, per-gate counts, every claim ⇄ its explicit non-claim   │
   └───────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| File / artifact | Responsibility |
|---|---|
| `152-check-claims.py` | The scanning half of the gate. Two text sources, one pattern table, no window, no exclusion. |
| `test_check_claims_152.py` | Proves the **gate** (subprocess-driven), including leg isolation per label. |
| `fixtures/` | Planted violations, one per added/modified label. **Permanently out of `_DEFAULT_TARGETS`.** |
| `152-CLAIM-GATE-TRANSCRIPTS.md` | Committed RED/GREEN evidence. **Permanently out of `_DEFAULT_TARGETS`** (its RED blocks quote forbidden text). |
| `152-GH12/21/11-COMMENT.md` | The three drafts. Frozen before posting; gate targets. |
| `152-RELEASE-NOTES-app.md` / `-fw.md` | The two bodies. Version-agnostic until cut time. **The only files carrying the literal `write --sdp-relock`.** |
| `152-LEDGER.md` | Every claim ⇄ its explicit non-claim; live HEADs; per-gate counts. **Gate target (D-12).** |
| `152-MERGE-RECORD.md` | The `/gsd-complete-milestone` handoff (§E-5). |

### Pattern 1 — Narrow one pattern, mandate one spelling (the project's own precedent)

**What:** when a required phrase collides with a forbidden pattern, do not add a window or an
exclusion. Narrow the *forbidden* pattern with a lookaround naming **exactly** the required spelling,
and simultaneously add a **required-caveat** row forcing that spelling to be present.

**When to use:** any time a literal string must be mandatory in one framing and forbidden in another.

**Two live instances:** 149's `(?<!software-)\bproven\b` (lookbehind, fixed-width, prefix); 152's
`sdp-relock-as-shipped` (lookahead, variable-width, suffix — §C-4).

**Failure mode to avoid:** widening the lookaround past exactly the required spelling. 149's own
comment: *"a bare-hyphen form would silently also permit 'bench-proven' and 'silicon-proven'."*

### Pattern 2 — Read the version, never predict it

**What:** every release-notes artifact opens by naming **where** the version was read from and
**when**. `146-RELEASE-NOTES-app.md`'s opening paragraph is verbatim reusable.

**Why:** measured — Phase 146 authored bodies for `3.0.0b21` and **they were never posted** (`b21`'s
body length is 0 today, §A-4). Predicting a tag both risks being wrong and makes the artifact stale
the moment CI cuts something else.

### Pattern 3 — Fail closed, at every layer

`_required_caveats_for()` returns the **full** caveat set for an unknown basename. Never-vacuous
returns 1. Any missing target returns 1. **No exit-0-on-nothing-scanned branch** (§C-3). The
`sdp-relock` lookahead rejects un-anticipated phrasings rather than permitting them (§C-4).

### Anti-Patterns to Avoid

- **A `152-`-prefixed glob for `_DEFAULT_TARGETS`.** Sweeps in CONTEXT / RESEARCH / DISCUSSION-LOG /
  fixtures / transcript — all of which legitimately carry forbidden vocabulary. **This RESEARCH.md
  does.**
- **A sibling-directory string constant in the gate.** The `_HERE` trap; has already failed open once.
- **Porting 137's `UNARMED: … return 0` branch.** A green that proves nothing.
- **`git merge-base --is-ancestor` as a merge oracle.** Measured false negative; 5 live patch-id
  matches today.
- **`updatedAt` as a landed-comment oracle.** Bumps on creation.
- **Inferring PyPI state from `gh release list`.** `2.0.8` is on GitHub and absent from PyPI *today*.
- **Reusing `test_check_claims_v132.py` as a filename.** pytest `prepend` basename collision.
- **Consuming the optional backtick before the lookahead** (§C-4). Silently permits nothing.
- **Citing `check_dispatch.py` as the erase hazard control.** 153 disproved that mechanism (§B-5).
- **Saying "three `.hex` assets" or "three firmware-touching workstreams" without checking.** Both
  numbers moved.
- **`gsd-tools` requirements/roadmap verbs on ROADMAP.md / REQUIREMENTS.md.** Whole-file
  `_normalizeMd`.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Scanning outward text for overclaims | A fresh scanner | **Sibling `149-check-claims.py`** with the four renames | 531 lines of measured mechanics: argv/env precedence, never-vacuous, fail-closed missing target, fail-closed caveat default, 20-entry display cap. Three prior phases' bug fixes are baked in. |
| Proving the gate is not vacuous | An ad-hoc manual run | **Fixture suite + committed plant-and-revert transcript** (146 D-12, followed by 149) | 146 D-12 required *both*. One without the other has been insufficient in this project's own history. |
| Deciding what beta already has | SHA ancestry | **`git cherry`** | §A-1: 5 commits are on beta under different SHAs *today*. |
| Proving a comment landed | Blob SHA / `updatedAt` / exit code of `gh` | **Re-read the stored body and diff it** | A blob SHA proves intent; `updatedAt` bumps on creation; a zero exit code proves the API accepted the call, not what it stored. |
| Release-note bodies | A `body:` key in the workflow | **`gh release edit --notes-file`** | Neither workflow passes `body:`. Adding one is out of scope and would retro-affect nothing. |
| Amending a record file | The `gsd-tools` roadmap/requirements verbs | **Hand-edit + labelled correction block + register entry** | The verbs `_normalizeMd` the whole file; and `check_record_corrections.py` needs the marker in the edited file. |
| Re-deriving the AT28C256 erase datasheet findings | A fresh datasheet read | **Cite D-06** | Established from primary sources; *"do not re-derive, do not soften."* |
| Re-deriving the write/erase decomposition | A fresh code survey | **Cite D-07 + `153-RECORD.md`** | 153 shipped it and its record is the authoritative account. |

**Key insight:** in this phase, a custom solution's failure mode is a *public overclaim*. Every
mechanism above exists because a previous phase in this project got the same thing wrong once and
recorded the fix — the gate that failed open, the ancestry check that returned a false negative, the
release notes that were authored and never posted, the windowed scanner that passed four plants.

---

## Runtime State Inventory

Phase 152 is not a rename or a refactor, but D-04 makes it a **publication** phase, and published
state is exactly the class a grep audit cannot see. Adapted accordingly.

| Category | Items found | Action required |
|---|---|---|
| **Stored data** | **None** — no database, collection, key or user_id is touched. `chip_database.json` is byte-unchanged by 153 and untouched by 152. *(Verified: `git diff --stat` empty per `153-VERIFICATION.md` truth 8.)* | none |
| **Live service config (state that lives outside git)** | ⚠ **FOUR live public surfaces.** (1) app `3.0.0b14` body, 4490 chars, **still publicly announces `dev sdp enable\|disable`, deleted 2026-08-05** — not rewritten (D-02). (2) fw `3.0.0b14` body, 5257 chars, same class. (3) gh#12's 2026-07-30 comment, line 15, *"gives standalone control in both directions"* — never retracted. (4) gh#12 + gh#11's 2026-08-06 comments pointing readers at a `--pre` install that still has `fw_board_identity=None`. | Correct in the **new** notes + the three comments. **Never edit the published `b14` bodies.** |
| **OS-registered state** | **None** — no Task Scheduler entry, pm2 process, launchd plist or systemd unit is involved. | none |
| **Secrets / env vars** | ⚠ Two CI secrets are load-bearing and **must not be touched**: `secrets.PERSONAL_ACCESS_TOKEN` (the release step; **lacks `workflow` scope by design**, which is why `publish.yml` is invoked via `workflow_call`) and `PYPI_API_TOKEN` (satisfied by `secrets: inherit`). **New:** the gate's own env seam `FIRESTARTER_CLAIMSCAN_TARGETS_152` — it must be phase-suffixed so it cannot retarget 146's or 149's live gate. | none / add the new seam name |
| **Build artifacts / installed packages** | ⚠ **CI-generated, not in git:** four `.hex` assets per firmware release (§G-2), and the PyPI sdist/wheel. Both are produced by the cut and **read after the fact**, never predicted. ⚠ **`size_baseline.json` moved during 153** (§A-9) — any inherited leonardo figure is stale. | read after the cut; use §A-9's figures |
| **Git state that a grep cannot see** | ⚠ `origin/beta` app is **7 commits ahead** of the milestone branch, and **5 milestone commits are already upstream under different SHAs**. Neither is visible in any file. | `git cherry`, both directions (§A-1) |

**The canonical question, answered:** *after every file in `.planning/` is corrected, what public
surfaces still carry the old claims?* → the two `b14` release bodies (left alone by design), gh#12's
2026-07-30 comment (retracted in the new comment, not edited), and the two 2026-08-06 `--pre` comments
(superseded by the new comments). Nothing else.

---

## Common Pitfalls

### Pitfall 1 — Posting before the merge

**What goes wrong:** criterion 2's *"answerable **because** the report now identifies its firmware"* is
**false in every published version** — `fw_board_identity=None` is still hardcoded at
`origin/beta:cli_handlers.py:2514` today (§A-1).
**Why it happens:** the fix exists on the milestone branch, so it *feels* shipped.
**How to avoid:** D-04's ordering is load-bearing. Merge, cut, read the tags, *then* post.
**Warning sign:** a draft naming a version that `gh release list` does not yet show.

### Pitfall 2 — A gate that has never been seen to fail

**What goes wrong:** the gate passes and the pass is believed, but the leg was structurally
unreachable and asserted nothing.
**Why it happens:** a pre-authored gate leg can be unreachable; a green is indistinguishable from a
vacuous green from the outside.
**How to avoid:** plant the **specified** violation (the pre-amendment criterion-1 wording), see RED,
then revert. If a leg is unreachable, **fix the locator only** — never the assertion. Commit the
transcript.
**Warning sign:** the RED block in the transcript is described rather than pasted.

### Pitfall 3 — `_DEFAULT_TARGETS` naming a file that does not exist yet

**What goes wrong:** the fail-closed missing-target branch returns rc=1 and the gate looks broken.
**Why it happens:** the natural instinct is to write the final target list once.
**How to avoid:** build the gate at a minimal existing set; extend in a later plan; scan the final
SUMMARY via **argv**, and record that argv run in the transcript. 149 did exactly this.
**Warning sign:** a `152-NN-SUMMARY.md` in `_DEFAULT_TARGETS` in the plan that writes it.

### Pitfall 4 — Inheriting a moved number

**What goes wrong:** an outward artifact states 27500 B, +594, three exemptions, 1172 B headroom,
three `.hex` assets, 67 commits ahead, or "PyPI has 2.0.8". **All six are wrong today** (§A-4, §A-5,
§A-9, §G-2).
**Why it happens:** CONTEXT.md is unusually complete, which makes it feel authoritative on numbers it
explicitly marks *"re-verify at plan time, do NOT inherit."*
**How to avoid:** every number in an outward artifact carries the command that produced it and the
date. **Re-measure in-plan.**
**Warning sign:** a figure with no adjacent command.

### Pitfall 5 — Overclaiming Phase 153 under pressure to answer gh#21 optimistically

**What goes wrong:** *"erase now works on AT28C256"* / *"the write path is fixed"*.
**Why it happens:** 153 shipped real capability, datapaganism is waiting, and the honest sentence is
less satisfying.
**How to avoid:** `153-RECORD.md` §"What Phase 152 must not repeat" exists for precisely this and names
the temptation explicitly. The gate blocks the two worst spellings today (`now-works`,
`at28c256-fixed` — §C-5), but it cannot catch an implied overclaim. **The blocking wording review is
not discharged by a green gate.**
**Warning sign:** any sentence about `0x0D` correctness without its non-claim within sight.

### Pitfall 6 — Conflating the two leonardo size numbers

**What goes wrong:** *"leonardo has 0 B of headroom"* stated where a reader will read it as *"the next
build bricks the bootloader"*, or *"1042 B free"* stated where it reads as MERGE-05 slack.
**Why it happens:** both are "leonardo headroom" in English.
**How to avoid:** `153-RECORD.md`: *"These two numbers are never the same number and must never be
conflated in any later plan or outward-facing text."* Use §G-2's paragraph shape.
**Warning sign:** one paragraph containing exactly one of the two numbers.

### Pitfall 7 — The `issue-closed` collision silently blocking D-05

**What goes wrong:** the gate returns rc=1 on the drafts, the cause is misread as a wording problem,
and the D-05 amendment gets softened into vagueness to make the gate green.
**Why it happens:** CONTEXT flags the `proven-unqualified` collision and not this one (§C-5).
**How to avoid:** adjudicate the row **before** authoring — drop `32` from the alternation, with the
three still-fires controls.
**Warning sign:** a draft that says "gh#32 (see gh#21)" and never says it is closed.

### Pitfall 8 — `gsd-tools query commit` switching branches mid-phase

**What goes wrong:** an unanchored `##…vX.Y` regex scrapes ROADMAP prose and the commit lands on
another branch — catastrophic in a phase that merges three repos.
**How to avoid:** `git branch --show-current` **after every** `gsd-tools query commit` call, in all
three repos. Also: `commit` stages **all** changes — the untracked files in §A-3 must not be swept in.

---

## Code Examples

### Re-verify the merge picture (both sub-repos, both directions)

```bash
# Source: measured live 2026-08-21
for R in firestarter firestarter_app; do
  cd "/workspaces/$R" && git fetch origin --quiet
  echo "== $R =="
  git rev-list --left-right --count origin/beta...HEAD   # "<behind>  <ahead>"
  git cherry origin/beta HEAD | awk '{print $1}' | sort | uniq -c
  git status --short
done
# firestarter      -> 0  39   | 39 '+'   | clean
# firestarter_app  -> 7  85   | 80 '+', 5 '-'
```

### The fifth forbidden class, with its two proofs

```python
# Source: derived and tested 2026-08-21 on Python 3.12.13. 18 assertions, 0 failures.
# The optional backtick lives INSIDE the lookahead -- never in the consumed part,
# or the engine backtracks off it, inspects it, and the class permits nothing.
(
    "sdp-relock-as-shipped",
    re.compile(
        r"write\s+--sdp-relock"
        r"(?!`?\s*(?:(?:is|stays|remains|was)\s+)?(?:still\s+)?"
        r"(?:withdrawn|deferred|not\s+shipped|not\s+shipping|unavailable|absent))",
        re.IGNORECASE,
    ),
),
```

### Prove a comment landed — the only sound oracle

```bash
# Source: D-09 posted mode; oracle choice measured 2026-08-21
BEFORE=$(gh issue view 12 --repo henols/firestarter_prom --json comments --jq '.comments | length')
gh issue comment 12 --repo henols/firestarter_prom \
  --body-file .planning/phases/152-*/152-GH12-COMMENT.md
AFTER=$(gh issue view 12 --repo henols/firestarter_prom --json comments --jq '.comments | length')
[ "$AFTER" -eq "$((BEFORE + 1))" ] || { echo "FAIL: count did not advance"; exit 1; }

# The proof: the stored body IS the frozen draft.
gh issue view 12 --repo henols/firestarter_prom --json comments \
  --jq '.comments[-1].body' > /tmp/posted-gh12.md
diff -u .planning/phases/152-*/152-GH12-COMMENT.md /tmp/posted-gh12.md

# The durable handle, for 152-LEDGER.md.
gh issue view 12 --repo henols/firestarter_prom --json comments \
  --jq '.comments[-1] | {id, url, createdAt}'

# The state assertion (146 D-07): comment posted, issue stays OPEN, body untouched.
gh issue view 12 --repo henols/firestarter_prom --json state --jq '.state'   # must be OPEN
```

### Read the cut version — never predict it

```bash
# Source: 146-RELEASE-NOTES-app.md's opening-paragraph discipline
gh release list --repo henols/firestarter_app --limit 5
gh release list --repo henols/firestarter     --limit 5
TAG_APP=$(gh release list --repo henols/firestarter_app --limit 20 \
  --json tagName,isPrerelease,publishedAt \
  --jq '[.[] | select(.isPrerelease)] | sort_by(.publishedAt) | last | .tagName')
echo "app tag read from gh release list on $(date -u +%FT%TZ): $TAG_APP"
```

### Verify PyPI independently of GitHub

```bash
# Source: measured 2026-08-21 -- GitHub has 2.0.8, PyPI does not.
curl -s https://pypi.org/pypi/firestarter/json | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('stable info.version:', d['info']['version'])          # 2.0.7
print('tag present?', '$TAG_APP' in d['releases'])
"
```

### Post a release body (the only way — no workflow passes `body:`)

```bash
gh release edit "$TAG_APP" --repo henols/firestarter_app \
  --notes-file .planning/phases/152-*/152-RELEASE-NOTES-app.md
gh release view "$TAG_APP" --repo henols/firestarter_app --json body --jq '.body | length'  # 0 -> N
gh release view "$TAG_APP" --repo henols/firestarter_app --json body --jq '.body' \
  | diff -u .planning/phases/152-*/152-RELEASE-NOTES-app.md -
```

---

## State of the Art

| Old approach (as of CONTEXT, 2026-08-20) | Current (measured 2026-08-21) | When changed | Impact |
|---|---|---|---|
| App 67 commits ahead of `origin/beta`, nothing behind | **85 ahead, 7 behind, 5 already-upstream by patch-id** | PR #52 merged 2026-08-19 → `b22` | The app merge is not a fast-forward; fund conflict resolution. |
| leonardo `flash_used` 27500; +594 over 3 exemptions; 1172 B cliff headroom | **27630; +724 over 4 exemptions; 1042 B** | Phase 153 Plan 14 | Any inherited figure is wrong. |
| `0x0D` has no erase operation; `-b` required to write a non-blank part | **`CMD_ERASE` dispatches (software AN 0544B); no pre-write blank check on `0x0D` or `0x05`** | Phase 153, 2026-08-21 | The primary subject of OUT-02/03/04. |
| `FLAG_CAN_ERASE` cleared for `algo ∈ {5,13}` at `database.py:621` | **Exclusion tuple `(5,)`, measured at `:638`** | Phase 153 ERASE-03 | All 84 algo-13 rows advertise the flag. |
| GATE-03 / `check_dispatch.py` guards the 12 V-on-OE erase path | **It structurally cannot** — the real control is `scripts/check_erase_no_vpp.py` | Phase 153 `D-153-03` | Naming `check_dispatch.py` outward repeats a disproven mechanism claim. |
| PyPI needs manual dispatch at a cut | **Automatic** — `pypi: needs: github` via `workflow_call` | after the b15/b17 divergence | Removes `gh workflow run` from the critical path. |
| PyPI stable == GitHub stable | **GitHub `2.0.8`; PyPI `2.0.7`, and `2.0.8` absent entirely** | 2026-08-07 → today | OUT-04 must not claim 2.0.8 is installable. |
| Three `.hex` release assets | **Four** (incl. `firestarter_py32f071.hex`) | v1.23 Phase 128 | A "three assets" sentence would be a public factual error. |
| `152-CONTEXT.md`: gh#11's `CMD_ERASE` question is unanswered | **Answered 2026-08-03 with a commitment** — "I will soon get it pushed and I will keep you posted" | 2026-08-03 | OUT-03 discharges a promise, not a silence. |
| Criterion 2: "gh#21, #32, #11 and #12 are all still OPEN" | **gh#32 CLOSED 2026-08-08, `COMPLETED`** | 2026-08-08 | D-05's amendment. Also stale at `ROADMAP.md:37`. |

**Deprecated / outdated:**
- `git merge-base --is-ancestor` as a merge oracle — measured false negative, twice over.
- `updatedAt` as a body-edit or landed oracle — bumps on creation.
- `firestarter dev sdp <chip> enable|disable` — deleted 2026-08-05, **still announced in two live
  `b14` bodies and one gh#12 comment.**
- `write --sdp-relock` — deferred **twice** (v1.30 Phase 135, v1.32 Phase 150) → Backlog 999.28.
- The claim *"`0x0D` has no erase operation"* — false since Phase 153; corrected at **seven** sites
  including `firestarter/README.md`.
- `write -b` as the recommended path for a non-blank AT28C part — **must never appear in the notes.**

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | `infoic.xml`'s AT28C256 `flags 0x0000C010` / `write_buffer_size 0x80` / `chip_id 0x00000000` are current | §A-10 | Low. Inherited from CONTEXT (D-06, "do not re-derive"); the `page_size 0x40` half is independently corroborated by the DB's `infoic_page_size_raw: 64`. Only matters if an outward artifact cites the raw flags word. |
| A2 | The `b14` app body still contains the exact sentence *"An opt-in re-lock after a write is deliberately not part of this release."* | §A-6 | Low. Body length reproduces CONTEXT byte-exact (4490), so the body is unchanged — but the sentence was not re-grepped this session. **Re-grep before quoting it in OUT-04.** |
| A3 | A bare-flag companion pattern (`--sdp-relock` without `write `) is needed and works in the same shape | §C-4 | Medium. **Designed, not tested.** Without it, *"the `--sdp-relock` option is available"* passes. The planner must test it alongside the primary. |
| A4 | A separate `--posted` argv mode is cleaner than the env seam for posted mode | §C-9 | Low — a design preference. Either works; the env seam's **basename→caveat fail-closed** trap is the real finding and applies to both. |
| A5 | `pypdf` + `cryptography>=3.1` are legitimate, established PyPI packages | Package Legitimacy Audit | Low, but **not verified against the registry this session** and not installed. Gate any install behind `checkpoint:human-verify`. |
| A6 | 151's D-06 class-size figures (406/111/39) used an alias-aware method that explains the ±1..3 delta from my derivation | §A-8 | **Medium — this is the one number the planner MUST resolve.** Publishing either set without re-deriving risks a wrong count in the release notes. The robust alternative (**665 of 746 refuse; 81 `read_permitted`**) holds under either method. |
| A7 | D-11's "once per body" is a wording convention, not a machine rule the donor's mechanism can express | §C-6 | Low. If the operator reads it as a machine rule, a count assertion must be added. **Do not silently leave it unenforced while implying it is enforced.** |
| A8 | The PROJECT.md workstream-table row for Phase 153 does not yet exist | §B-11, §F | Low. The *count* correction is confirmed landed; the table row was not separately grepped. **Verify before funding the task.** |

---

## Open Questions

1. **Which method produced 151's 406 / 111 / 39?**
   - *Known:* my pipeline derivation gives 405 / 112 / 108 / 40 / 81 = 746, zero errors, and the eight
     class tokens are confirmed. The alias-aware `undocumented_alias` bucket (112) is almost certainly
     the source of the delta.
   - *Unclear:* whether 151 counted per-row-canonical, per-alias-token, or excluded the alias bucket.
   - *Recommendation:* re-derive in-plan with 151's own code path. **Meanwhile prefer "665 of 746
     rows resolve to a refusal class; 81 are `read_permitted`"** — robust under either method and it is
     the fact D-13's argument actually needs.

2. **Will the app PR to `beta` conflict?**
   - *Known:* 85 ahead / 7 behind; the 7 are PR #52 plus its auto-commit, all touching the
     firmware-install/port-targeting path; 5 milestone commits are the same patches under other SHAs.
   - *Unclear:* whether git resolves the patch-id duplicates cleanly or presents them as conflicts.
   - *Recommendation:* fund a conflict-resolution task in the merge plan. **Do not `git cherry-pick`
     or drop the 5 duplicated commits** — let the merge resolve them and verify with `git cherry`
     afterwards (expect all-`-`).

3. **Does REQUIREMENTS.md's in-scope count reconcile to 34 or 35?**
   - *Known:* per-family checkboxes = 35 (DATA 6, ERASE 9, LOCK 4, OUT 5, PGSZ 5, PROV 6); the file's
     footer says 34; the Coverage block still says 25.
   - *Unclear:* the off-by-one — most likely DATA-06's re-homing counted as an addition.
   - *Recommendation:* resolve it while correcting the Coverage block (§A-11(2)). Do not restate an
     unreconciled number.

4. **Does the PROJECT.md workstream table already have its 153 row?**
   - *Recommendation:* grep before funding; 153 landed the adjacent count correction.

5. **Is the `--auto`/`--chain` prohibition mechanically enforceable at all?**
   - *Known:* `config.json` has `workflow._auto_chain_active: false` today; `--auto`/`--chain`
     **auto-approve** human-verify checkpoints; `autonomous: false` is measured **not**
     self-protecting; and CONTEXT D-03 states plainly that per-artifact gates reduce blast radius but
     do not remove this dependence.
   - *Unclear:* whether any in-plan assertion can fail closed on it.
   - *Recommendation:* if a plan can read `_auto_chain_active` and hard-fail before the first post,
     that is worth one task. Otherwise, restate the prohibition in every posting plan's frontmatter
     and accept it as the stated residual risk — **do not present a restatement as a control.**

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| `git` | three PRs, `git cherry` | ✓ | system | — |
| `gh` CLI (authenticated, read) | issue + release reads | ✓ | verified live all session | — |
| `gh` CLI (write: `issue comment`, `release edit`) | the five posts | ✓ *(assumed — same auth)* | — | ⚠ **If a write is refused, D-03's rejected `152-POST-COMMANDS.md` alternative becomes the fallback** (agent authors, operator runs). |
| `gh workflow run` | any manual CI dispatch | ✗ | — | **Blocked by the auto-mode classifier; settings edits cannot fix it.** Not on the critical path (§E-3). Read-only `gh run` works. |
| Python 3 | the gate + derivations | ✓ | **3.12.13** | ⚠ CI runs **3.11** — a local green can be fail-open. Gate is stdlib-only, so low risk. |
| `pytest` | the paired suite | ✓ | 149's suite ran 20 passed / 0.82 s | ⚠ `addopts` is `-ra -q`; use `-o addopts=""`. |
| `curl` + network to pypi.org | independent PyPI check | ✓ | verified live | — |
| GitHub Actions (both sub-repos) | the two cuts | ✓ | `beta-release.yml` / `beta-build.yml` read | — |
| `pypdf` + `cryptography>=3.1` | reading `AT28C256.pdf` | ✗ | not installed | **Not needed** — D-06 forbids re-deriving. Only if one page reference must be confirmed. |
| `pdftotext` | same | ✗ | absent from devcontainer | as above |
| AT28C silicon | validating anything | ✗ | **none in inventory** | **No fallback and none is needed** — the Evidence Ceiling is the phase's subject, not its blocker. |

**Missing with no fallback:** `gh workflow run` (not on the critical path). AT28C silicon (by design).
**Missing with fallback:** `gh` write access (→ operator-run command file); PDF tooling (→ cite D-06).

---

## Validation Architecture

### Test Framework

| Property | Value |
|---|---|
| Framework | **pytest** (devcontainer install; 149's suite verified green today) |
| Config file | `firestarter_app/pyproject.toml` supplies `addopts = "-ra -q"` for app-scoped runs; the `.planning`-hosted gate suites take **no** project config and run from their own phase directory |
| Quick run command | `cd .planning/phases/152-*/ && python3 -m pytest test_check_claims_152.py -q -o addopts=""` |
| Full suite command | the quick run **plus** `python3 152-check-claims.py` (file mode) **plus** `python3 ../130-*/check_record_corrections.py` |
| Measured baselines today | 149's suite **20 passed in 0.82 s**; 149's gate **rc=0**; `check_record_corrections.py` **rc=0 in 23.3 s** |

⚠ `test_check_claims_152.py` must have a **distinct basename** — pytest's default `prepend` import
mode collides on a repeated basename when run from `/workspaces` (§C-8).
⚠ Doubling `-q` suppresses the count line; always `-o addopts=""`.

### Phase Requirements → Test Map

| Req | Behavior | Test type | Automated command | File exists? |
|---|---|---|---|---|
| OUT-05 | The gate rejects the **specified planted violation** | integration (subprocess) | `python3 -m pytest test_check_claims_152.py -q -o addopts="" -k planted_sdp_relock` | ❌ Wave 0 |
| OUT-05 | The gate rejects the bare-flag form | integration | same, `-k planted_sdp_relock_bare_flag` | ❌ Wave 0 |
| OUT-05 | The modified `issue-closed` row **still fires** on gh#21/#11/#12 | integration | same, `-k issue_closed_still_fires` | ❌ Wave 0 |
| OUT-05 | The permitted withdrawal sentence does **not** trip the class | integration | same, `-k withdrawal_sentence_is_permitted` | ❌ Wave 0 |
| OUT-05 | Never-vacuous: empty target list → non-zero | unit | same, `-k never_vacuous` | ❌ Wave 0 (donor leg) |
| OUT-05 | Fail-closed: missing target → non-zero | unit | same, `-k nonexistent_scan_target` | ❌ Wave 0 (donor leg) |
| OUT-05 | Unknown basename → **full** caveat set | unit | same, `-k unrecognised_basename` | ❌ Wave 0 (donor leg) |
| OUT-05 | Armed against the **real** 152 artifacts | integration | same, `-k armed_against_the_real` | ❌ Wave 4 (after the extension) |
| OUT-05 | CONTEXT/RESEARCH/DISCUSSION-LOG/transcript are **not** gate targets | unit | same, `-k are_not_gate_targets` | ❌ Wave 0 (donor leg) |
| OUT-05 | Every added/modified label has an isolated fixture | meta | same, `-k every_forbidden_pattern_has_a_planted_fixture` | ❌ Wave 0 (donor leg) |
| OUT-05, OUT-01…04 | All six drafts + ledger are clean in **file** mode | integration | `python3 152-check-claims.py` → rc 0 | ❌ Wave 4 |
| OUT-01/02/03 | The **posted** comment body equals the frozen draft | integration | `gh issue view N --json comments --jq '.comments[-1].body' \| diff -u <draft> -` | ❌ Wave 4 |
| OUT-01/02/03 | The comment count advanced by exactly 1 (non-vacuity) | integration | `gh issue view N --json comments --jq '.comments \| length'` before/after | ❌ Wave 4 |
| OUT-02 | gh#21 is **still OPEN** after commenting (146 D-07) | integration | `gh issue view 21 --json state --jq '.state'` → `OPEN` | ❌ Wave 4 |
| OUT-04 | The release body **is** the one we authored | integration | `gh release view "$TAG" --json body --jq '.body' \| diff -u <draft> -` | ❌ Wave 4 |
| OUT-04 | The body length moved 0 → N (non-vacuity) | integration | `gh release view "$TAG" --json body -q '.body \| length'` | ❌ Wave 4 |
| OUT-04 | PyPI carries the cut tag, verified **independently** of GitHub | integration | `curl -s https://pypi.org/pypi/firestarter/json \| python3 -c "…'$TAG' in d['releases']"` | ❌ Wave 3 |
| D-05/D-11/D-15 | The hand-edited amendments are **present**, without a whole-file normalise | unit | `grep -c` for each amendment's dated marker, **plus** `git diff --stat` showing a bounded line count on ROADMAP.md / REQUIREMENTS.md / PROJECT.md | ❌ Wave 1 |
| D-05/D-15 | The record-corrections gate still passes after the hand-edits | integration | `timeout 300 python3 ../130-*/check_record_corrections.py` → rc 0 | ✅ exists (green today, 23.3 s) |
| D-04 | Beta merges are complete and **not re-mergeable-by-mistake** | integration | `git -C <repo> cherry origin/beta HEAD` → **all `-`** | ✅ mechanism exists |

### The four validation questions this phase actually poses

1. **What proves a comment landed?** Not `updatedAt` (bumps on creation; and comment-level `updatedAt`
   is `null` on all 30 existing comments, so it cannot distinguish "new" from "unedited"). **The
   stored body, re-read and diffed against the frozen draft**, with the comment count delta as the
   non-vacuity guard and the comment id/URL recorded in the ledger. See §D-5.
2. **What proves a release body is ours?** `gh release view --json body --jq '.body'` diffed against
   the draft. Length 0 → N is the non-vacuity guard; the diff is the identity proof. A blob SHA of the
   draft proves only intent.
3. **How is the claim gate proven fail-provable rather than vacuous?** Three independent legs, all
   required: (a) a **committed** plant-and-revert transcript with the RED **pasted, not described**;
   (b) a fixture suite with **per-label leg isolation** (a plant trips exactly its own label and no
   neighbour, and fails for the forbidden phrase rather than a missing caveat); (c) the arming legs —
   defaults resolve inside this phase's dir, carry the `152-` prefix, are non-empty, and every
   basename has a `_CAVEAT_RULES` entry. ⚠ **A pre-authored leg can be structurally unreachable — RED
   proves nothing until the leg is seen to pass, and the fix must be locator-only.**
4. **How is a hand-edited amendment proven present without a whole-file normalise?** Two paired
   assertions: a **positive** `grep -c` on the amendment's own dated marker text (e.g. `AMENDED
   2026-08-21 (D-05)`) **and** a **bounded-diff** assertion — `git diff --numstat` showing the
   changed-line count is within the expected range for that file. The bounded diff is what catches an
   accidental `_normalizeMd` blast: a whole-file reformat shows hundreds of changed lines where an
   amendment shows a handful. ⚠ Do **not** use "the file is byte-unchanged except…" as a criterion —
   that criterion class has broken before in this project.

### Sampling Rate

- **Per task commit:** `python3 -m pytest test_check_claims_152.py -q -o addopts=""` (sub-second) plus
  `python3 152-check-claims.py` once targets exist.
- **Per wave merge:** the above **plus** `timeout 300 python3 ../130-*/check_record_corrections.py`,
  **plus** (Wave 3 onward) `git cherry origin/beta HEAD` in both sub-repos.
- **Per public post:** file-mode gate GREEN **before** the blocking checkpoint; posted-mode gate plus
  the body diff **after**.
- **Phase gate:** every gate above green, all six drafts + the ledger in `_DEFAULT_TARGETS`, all five
  posts verified by body diff, both PyPI checks done, `152-MERGE-RECORD.md` written, before
  `/gsd-verify-work`.

### Wave 0 Gaps

- [ ] `152-check-claims.py` — sibling of `149-check-claims.py`, four renames (§C-2), two new forbidden
      rows, one modified row, two required-caveat rows. Covers OUT-05.
- [ ] `fixtures/planted_sdp_relock_as_shipped.md` — **the specified planted violation** (the
      pre-amendment criterion-1 wording). Covers OUT-05.
- [ ] `fixtures/planted_sdp_relock_bare_flag.md` — covers OUT-05.
- [ ] `fixtures/planted_issue_closed_still_fires.md` (×3 controls: gh#21/#11/#12) — covers OUT-05.
- [ ] `fixtures/clean_control.md` + `clean_control_second.md` — the permitted withdrawal sentence and
      both required caveats, proven clean.
- [ ] `test_check_claims_152.py` — ~20 legs (§C-8), **subprocess-driven**, distinct basename.
- [ ] `152-CLAIM-GATE-TRANSCRIPTS.md` — RED per added/modified label, then GREEN, then the extension
      and final-target-list sections.
- [ ] Framework install: **none needed** — pytest is present and 149's suite is green today.

---

## Security Domain

`security_enforcement` is absent from `.planning/config.json` → treated as **enabled**. This is a
records-and-publication phase with no product code, so most ASVS categories do not apply; the ones
that do apply to the *publication* act and the *CI credentials*.

### Applicable ASVS Categories

| ASVS category | Applies | Standard control |
|---|---|---|
| V2 Authentication | **no** | No auth code. `gh` uses the existing operator credential. |
| V3 Session Management | **no** | No sessions. |
| V4 Access Control | **yes** | **The publication capability itself.** D-03's per-artifact blocking checkpoint is the access control on five irreversible public acts, and it is *documented as insufficient* under `--auto`/`--chain`. The rejected-but-safer alternative (agents never post; a `152-POST-COMMANDS.md` the operator runs) removes the capability rather than gating it. |
| V5 Input Validation | **yes** | The gate's `resolve_targets` argv/env handling: `os.environ.get()` with **no default**, so `is not None` distinguishes absent from empty; a present-but-empty seam yields **zero** targets and the never-vacuous guard returns 1 — it must never silently fall back to defaults. |
| V6 Cryptography | **no** | Nothing is signed or encrypted by this phase. `secrets.PERSONAL_ACCESS_TOKEN` and `PYPI_API_TOKEN` are consumed by CI, never handled here. |
| V7 Error Handling / Logging | **yes** | The gate fails **closed** at every layer and prints a bucketed `FAIL:` naming the offending file, label and line — never a bare non-zero exit. |
| V14 Configuration | **yes** | Two CI credentials are load-bearing and must not be touched (§Runtime State Inventory). The `PERSONAL_ACCESS_TOKEN` **deliberately lacks `workflow` scope** — that is why `publish.yml` is invoked via `workflow_call`, and widening the scope was explicitly rejected. |

### Known Threat Patterns for this phase

| Pattern | STRIDE | Standard mitigation |
|---|---|---|
| An overclaim published to an irreversible public surface | **Repudiation / Information disclosure** | The fail-provable claim gate (OUT-05) in **both** modes, plus the blocking human wording review — which a green gate explicitly does **not** discharge. |
| `--auto`/`--chain` auto-approving an outward-facing checkpoint | **Elevation of privilege** | The prohibition restated in every posting plan's frontmatter. ⚠ **This is a stated residual risk, not a control** — `autonomous: false` is measured not self-protecting. |
| A gate that passes vacuously (scanned nothing) | **Tampering** (integrity of the control) | Never-vacuous guard + fail-closed missing target + no exit-0-on-nothing-scanned branch + the arming legs. 137's checker failed open exactly here. |
| One phase's env seam retargeting another phase's live gate | **Tampering** | Phase-number-suffixed seam `FIRESTARTER_CLAIMSCAN_TARGETS_152`, plus the `startswith("152-")` self-check in both the call and its message. |
| Announcing a version that does not exist, or that PyPI does not have | **Spoofing** (of release state) | Versions **read** from `gh release list`, never predicted; PyPI verified **independently** (§A-5 shows this is not hypothetical). |
| Re-merging an already-merged branch on a false-negative ancestry check | **Tampering** (repo integrity) | `git cherry`, recorded in `152-MERGE-RECORD.md`; `--is-ancestor` explicitly forbidden. |
| A record edit silently reformatting a whole file | **Tampering** (integrity of the record) | Hand-edit + bounded-diff assertion; never the `gsd-tools` roadmap/requirements verbs. |
| Publishing a firmware `.hex` whose build could brick a leonardo bootloader | **Denial of service** (on the user's hardware) | ⚠ **The linker guard was REMOVED** — `board_upload.maximum_size` is the real 32768 B. The only remaining control is the **recorded** 1042 B figure (§A-9), which is why §G-2 recommends stating it publicly. |

---

## Sources

### Primary (HIGH confidence — measured live in this session, 2026-08-21)

- `git rev-list --left-right --count origin/beta...HEAD`, `git cherry origin/beta HEAD`,
  `git log --oneline HEAD..origin/beta`, `git status --short`, `git submodule status`,
  `git show origin/beta:<path>` — both sub-repos.
- `gh release list --repo henols/firestarter{,_app}`; `gh release view <tag> --json body,assets`.
- `gh issue view {11,12,20,21,32} --repo henols/firestarter_prom --json
  number,title,state,stateReason,createdAt,updatedAt,closedAt,comments,body,author`.
- `curl -s https://pypi.org/pypi/firestarter/json`.
- `firestarter/scripts/baseline/size_baseline.json`, `size_baseline_base01.json`,
  `size_baseline_v131.json` (meta blocks).
- `firestarter/src/proms/eeprom_28c.cpp`, `flash_5v_page.cpp` at HEAD `d990a4c`.
- `firestarter_app/firestarter/{database.py, ic_layout.py, chip_test.py, eprom_operations.py,
  lock_status.py, protection_readability.py}`; `firestarter/data/chip_database.json`.
- `firestarter_app/.github/workflows/{beta-release.yml, publish.yml}`;
  `firestarter/.github/workflows/beta-build.yml`.
- `python3 149-check-claims.py` (rc 0); `python3 -m pytest test_check_claims_v132.py -q -o addopts=""`
  (20 passed / 0.82 s); `python3 130-*/check_record_corrections.py` (rc 0 / 23.3 s).
- Live derivation: algorithm histogram over 746 rows; `protection_gate_for_entry` over all 746 rows
  via `EpromDatabase().get_eprom()`.
- Live regex testing: 18 assertions on the fifth-class lookahead (0 failures); the 149 table run
  against 17 candidate 152 sentences.

### Primary (HIGH confidence — project documents read in full)

- `.planning/phases/152-*/152-CONTEXT.md` (685 lines, all of D-01…D-15).
- `.planning/phases/153-*/153-VERIFICATION.md` (195 lines); `153-RECORD.md` (438 lines).
- `.planning/phases/149-*/149-check-claims.py` (531 lines, incl. the full module docstring);
  `test_check_claims_v132.py` (721 lines); `149-CLAIM-GATE-TRANSCRIPTS.md` (274 lines);
  `fixtures/` (11 files).
- `.planning/phases/137-*/check_permitted_claims.py` (360 lines); `137-GH12-COMMENT.md` (46 lines).
- `.planning/phases/130-*/check_record_corrections.py`.
- `.planning/ROADMAP.md` §"Phase 152", §"Phase 153", §"Phase 150", `:37`, `:163`;
  `.planning/REQUIREMENTS.md` §"Outward-Facing Close (OUT)", §"Write-Path Erase Policy (ERASE)",
  traceability + Coverage; `.planning/PROJECT.md` `:45-47`; `.planning/config.json`.
- `/workspaces/CLAUDE.md`; `firestarter_app/CLAUDE.md` (§"Database Pipeline", via CONTEXT citation).

### Secondary (MEDIUM confidence)

- `.planning/phases/146-*/146-LEDGER.md` (section headings surveyed, not read in full).
- Project memory notes on CI gotchas, `gsd-tools query commit` branch switching, `fw --install`
  ignoring `--board`, pytest `addopts` doubling, worktree/submodule under-detection,
  `--auto` auto-approval. Each is a prior measured finding, cited not re-measured.

### Tertiary (LOW confidence — flagged in the Assumptions Log)

- `infoic.xml` AT28C256 `flags` / `write_buffer_size` / `chip_id` (A1).
- The exact `b14` "opt-in re-lock" sentence at char level (A2).
- The bare-flag companion pattern (A3); the `--posted` argv-mode preference (A4).
- `pypdf` / `cryptography` registry status (A5).
- 151's class-size derivation method (A6) — **the one item that must be resolved in-plan.**
- The PROJECT.md 153 table-row state (A8).

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| Merge / branch state | **HIGH** | `git cherry` + `rev-list` both directions, run live in both sub-repos today. |
| Release / PyPI state | **HIGH** | Every body length re-measured; PyPI JSON fetched directly; the 2.0.8 divergence confirmed by explicit presence checks. |
| What Phase 153 shipped | **HIGH** | `153-VERIFICATION.md` (9/9, re-verified) plus **direct reads of the committed tree**, never the record alone. |
| The claim gate design | **HIGH** | Donor read in full; the fifth class **derived and empirically proven** (18 assertions, 0 failures); the `issue-closed` collision **measured**, not inferred. |
| Issue-thread state | **HIGH** | All five issues and all 30 comments enumerated via `gh --json` today. |
| CI / cut mechanics | **HIGH** | Both workflow files read; the automatic-PyPI change confirmed by the `b22` 23-second upload delta. |
| Size figures | **HIGH** | `size_baseline.json` read live; the `meta.phase` string names Phase 153 Plan 14 as its origin. |
| DB class sizes | **MEDIUM** | Re-derived through the real pipeline with zero errors, but ±1..3 from 151's published figures. **Method ambiguity unresolved — see Q1.** |
| `infoic.xml` fields | **LOW** | Inherited from CONTEXT per D-06's "do not re-derive"; only `page_size` independently corroborated. |

**Research date:** 2026-08-21
**Valid until:** ⚠ **~3 days for the merge/version/issue data.** Every measurement in §A, §D and §E is
against moving targets: `origin/beta` moved 7 commits and cut a release in the 2 days between CONTEXT
and this file, and the phase's own merges will move them again. **Re-measure §A-1, §A-2, §A-4 and §D
at the start of the merge plan, and re-read the cut tags after CI.** The gate design (§C), the 153
findings (§B) and the pattern/pitfall material are stable for ~30 days.
