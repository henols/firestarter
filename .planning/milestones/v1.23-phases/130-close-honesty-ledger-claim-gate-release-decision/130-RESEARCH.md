# Phase 130: Close — Honesty Ledger, Claim Gate, Release Decision - Research

**Researched:** 2026-08-02
**Domain:** Milestone-close documentation integrity + outward-facing release publication mechanics
**Confidence:** HIGH (everything below was read or executed in the live trees this session; nothing is inherited from CONTEXT.md)

## Summary

CONTEXT.md's factual substrate holds up **unusually well**: every live-measured figure in
`<code_context>` re-verified AGREES, byte-for-byte — both branch tips, both ahead/behind counts, both
tag ceilings, all three b14 surfaces, the meta gitlinks, the `gh` scopes, the working-tree dirt, and
the absence of a `v1.23 PY32F071 Integration` entry in `ROADMAP.md`'s `## Milestones` list. Unlike
Phases 121, 127, 128 and 129, **no locked decision rests on a false premise about the world.**

What research *did* find is a different and equally load-bearing class of defect: **three broken
mechanisms in the tooling this phase is contractually bound to**, each currently invisible.
(1) 130-CONTEXT.md's own decision block is unparseable — the GSD decision extractor returns
`could-not-parse` and silently drops **9 of 16** decisions, including D-11, D-13, D-14 and D-15.
(2) `check_permitted_claims.py`'s `_DEFAULT_TARGETS` resolves into **Phase 123's** directory, not
Phase 130's, so writing all four contracted artifacts where CONTEXT says to write them yields
`UNARMED:` and **exit 0** — a green claim gate that scanned nothing. (3) That checker's own pytest
suite is **already RED** (1 failed / 9 passed), broken by the mere existence of `130-CONTEXT.md`,
and nothing in CI would ever notice because the meta repo runs no test workflow.

Beyond the tooling, two substantive scope findings: D-11's lockstep edit is **larger than CONTEXT
states** (§5(d) also becomes false, and the ship-gate sentence lives in a *third* place — a byte-exact
test constant), and §5(c)'s ship gate **as worded forbids exactly what D-11 does**. And CLOSE-03's
collapse of ROADMAP lines 33–34 silently discharges most of CLOSE-01's ROADMAP work, which makes an
ordering constraint CONTEXT's ten do not contain.

**Primary recommendation:** fix the three broken mechanisms in Wave 0 before any content is written
— rewrap CONTEXT's nine malformed D-NN labels, repoint `_DEFAULT_TARGETS` (in the same commit that
writes the artifacts, as its own docstring requires) and repair the RED arming test's locator with a
RED-preserving proof. Then order CLOSE-03 before CLOSE-01's ROADMAP sweep, resolve the §5(c)
ship-gate tension explicitly on the record, and treat the CLOSE-01 checker's self-reference and
history-block exemptions as first-class design (not an afterthought) because `ROADMAP.md:2468`
quotes its own needles.

---

## Corrections to CONTEXT.md

Ordered by severity. C-1 through C-3 are blocking.

### C-1 — CRITICAL: 130-CONTEXT.md's decision block is unparseable; 9 of 16 decisions are silently dropped

**CONTEXT.md claim:** `<code_context>` §Established Patterns warns *"`- **D-NN: text**` must close its
bold run on ONE line … otherwise plan-phase's §13a decision-coverage gate fails closed."*

**Evidence:** CONTEXT.md violates its own rule. Executed against the real parser
`/workspaces/.claude/gsd-core/bin/lib/decisions.cjs`:

```
outcome: could-not-parse
count: 7
ids: D-01, D-03, D-05, D-09, D-10, D-12, D-16
parseDecisions: ignored unparseable decision bullet: - **D-02: Both b15 release bodies …
parseDecisions: ignored unparseable decision bullet: - **D-04: Publish in-phase; …
parseDecisions: ignored unparseable decision bullet: - **D-06: CLOSE-01 amends …
parseDecisions: ignored unparseable decision bullet: - **D-07: The Validation Ceiling's …
parseDecisions: ignored unparseable decision bullet: - **D-08: CLOSE-01 is proven by …
parseDecisions: ignored unparseable decision bullet: - **D-11: The interim pid.codes …
parseDecisions: ignored unparseable decision bullet: - **D-13: The two py32 slots …
parseDecisions: ignored unparseable decision bullet: - **D-14: Binary Command Protocol …
parseDecisions: ignored unparseable decision bullet: - **D-15: Backlog stubs 999.23 …
```

Cause: all three accepted grammars (`bulletColonRe` line 35, `bulletEmDashRe` line 44,
`bulletTitledColonRe` line 56) require the closing `**` on the **same physical line** as
`- **D-NN`. For these nine, the bold run wraps. Example, CONTEXT.md:75–76:

```
- **D-02: Both b15 release bodies are hand-written and sit behind a blocking operator wording
  review.** `130-RELEASE-NOTES-fw.md` and `130-RELEASE-NOTES-app.md` are committed drafts carrying
```

Line 143's parse-miss guard fires, `parseMisses > 0`, and `extractDecisions` returns
`could-not-parse`. `[VERIFIED: executed against .claude/gsd-core/bin/lib/decisions.cjs]`

**Corrected statement:** The nine dropped decisions are exactly the highest-stakes ones — D-11 (the
`usb_cdc.c` edit), D-13/D-14/D-15 (the entire CLOSE-03 renumber), D-07/D-08 (CLOSE-01's mechanics),
D-02 (the blocking wording review), D-04 (the tag/gitlink boundary), D-06 (the REQUIREMENTS
amendment). A planner or plan-checker that consumes the parsed decision set plans **without** them.
Fix: rewrap each of the nine so the closing `**` lands on the bullet's first line — e.g.
`- **D-02: Both b15 release bodies are hand-written and sit behind a blocking wording review.**`
followed by the body. Verify by re-running the parser: expect `outcome` ≠ `could-not-parse` and
count 16. This must land before plan-phase's §13a gate runs.

### C-2 — CRITICAL: the claim gate's `_DEFAULT_TARGETS` points at Phase 123's directory, not Phase 130's

**CONTEXT.md claim:** `<domain>` — *"the four closing artifact names are a pre-existing contract …
`_DEFAULT_TARGETS` names `130-LEDGER.md`, `130-DECISION.md`, `130-RELEASE-NOTES-fw.md`,
`130-RELEASE-NOTES-app.md` with all-or-nothing arming."* `<integration_points>` places them at
`.planning/phases/130-…/130-LEDGER.md` etc.

**Evidence:** `check_permitted_claims.py:74` sets `_HERE = os.path.dirname(os.path.abspath(__file__))`
— the **Phase 123** directory — and lines 86–91 join the four names onto it. Resolved live:

```
/workspaces/.planning/phases/123-non-regression-baselines-gate-hardening/130-LEDGER.md         ABSENT
/workspaces/.planning/phases/123-non-regression-baselines-gate-hardening/130-DECISION.md       ABSENT
/workspaces/.planning/phases/123-non-regression-baselines-gate-hardening/130-RELEASE-NOTES-fw.md   ABSENT
/workspaces/.planning/phases/123-non-regression-baselines-gate-hardening/130-RELEASE-NOTES-app.md  ABSENT

$ python3 check_permitted_claims.py
UNARMED: none of the 4 named v1.23 closing artifacts for Phase 130 exist yet …
exit=0
```

Root cause confirmed: v1.22's original
(`.planning/phases/122-…/check_permitted_claims.py:39-56`) uses the same `_HERE` idiom, where it was
**correct** — `122-LEDGER.md` etc. live in the 122 directory. The v1.23 adaptation kept `_HERE` and
changed the filenames to `130-*` across a phase boundary. `[VERIFIED: read + executed]`

**Corrected statement:** If Phase 130 writes its four artifacts into its own directory and runs the
scanner in default mode, the gate prints `UNARMED:` and exits **0** — a green run that scanned
nothing, on the milestone's only outward-facing overclaim gate. Two resolutions:

- **(a) Recommended — repoint `_DEFAULT_TARGETS`** at
  `os.path.join(_HERE, "..", "130-close-honesty-ledger-claim-gate-release-decision", "<name>")`
  in the **same commit** that writes the artifacts. This is exactly the amendment the module
  docstring's *"Phase 130 coupling (load-bearing)"* paragraph anticipates, and it preserves D-15's
  all-or-nothing arming. Requires the paired test's expectations to move with it (see C-3).
- **(b) Rejected — always invoke with explicit `argv`/`FIRESTARTER_CLAIMSCAN_TARGETS`.** `main()`
  lines 254–291: arming applies **only** to the default set (`used_defaults`); named targets take the
  ordinary fail-closed branch. So the *"producing three of four is a hard failure by design"*
  guarantee CONTEXT relies on would not hold, and the guarantee is the reason the four names were
  contracted seven phases early.

### C-3 — CRITICAL: the claim gate's own test suite is already RED, and CI cannot see it

**CONTEXT.md claim:** `<code_context>` §Reusable Assets — *"`123/check_permitted_claims.py` +
`test_check_permitted_claims.py` + `fixtures/` — already written, already armed."*

**Evidence:**

```
$ python3 -m pytest test_check_permitted_claims.py -q
1 failed, 9 passed in 0.30s

FAILED test_check_permitted_claims.py::test_d15_arming_both_directions
  assert not real_phase_130_dir.exists() or not any(real_phase_130_dir.glob("130-*.md")),
    "test must not create a real 130-*.md artifact as a side effect"
```

`test_check_permitted_claims.py:301-304`'s side-effect guard globs `130-*.md` in the phase-130
directory. That directory now contains `130-CONTEXT.md` and `130-DISCUSSION-LOG.md`, committed by
`0005077 docs(130): capture phase context`. Nothing in CI runs this suite: the meta repo's only
workflow is `.github/workflows/catalog-sync-check.yml`, which never invokes pytest. Control: the
v1.22 analogue is green (`7 passed`). `[VERIFIED: executed]`

**Corrected statement:** "Already armed" is false in two independent ways — the arming target
resolves to the wrong directory (C-2), and the leg that proves arming both directions has been
failing since the discussion commit, before Phase 130 wrote anything. The guard's locator is too
broad. Phase 129's lesson applies verbatim (*"a pre-authored gate leg can be UNREACHABLE … fix
locators only, with a RED-preserving proof"*): narrow the glob from `130-*.md` to the four contracted
names, then prove the narrowed guard **still fires** if a `130-LEDGER.md` is planted in the real
directory. Do not delete the guard — it is the thing stopping a test from writing into the phase's
own deliverable set. Note this failure will get worse, not better, once the four artifacts land.

### C-4 — D-11's lockstep edit is larger than CONTEXT states: §5(d) also becomes false, and the ship-gate sentence is a third copy

**CONTEXT.md claim:** D-11 — *"§5 is `[SHARED:S4]` under the 41-leg body-only sync gate … so §5(a)'s
'what the descriptor currently presents' must be updated **identically in both copies** or the gate
goes red."* Only §5(a), only two copies.

**Evidence:**

1. `.planning/v1.23-FLASH-PATH-DECISION.md:206` — §5(d), **inside** `[SHARED:S4]`'s body — reads
   *"`usb_cdc.c` is **not edited** this phase (D-06) … Editing the descriptor follows the allocation,
   which follows an operator-filed public pull request, and it will need an ARM build to stay
   honest."* D-11 edits `usb_cdc.c` and **inverts** that ordering. §5(d) therefore needs substantive
   rework, in both copies, not merely a tweak.
2. `firestarter/tests/test_flash_path_record_sync.py:345-348` holds the ship-gate sentence as a
   **byte-exact module constant** `_L2_SHIP_GATE`, asserted by
   `test_vid_pid_decision_and_ship_gate[meta]/[fw]`. If §5(c) is touched, that is a **third** place.
3. §5(a) cites `usb_cdc.c` line numbers verbatim: *"defines `FIRESTARTER_USB_VID 0x36B7U` at line 20
   and `FIRESTARTER_USB_PID 0xFFFFU` at line 24."* Confirmed on disk at exactly those lines. A
   source-warning comment inserted **above** the defines invalidates both citations.
4. Compensating good news: `_S4_NEEDLES` (line 434) requires `"0x36B7"`, `"0xFFFF"`, `"0x1209"`,
   `"1209:0001"`, `"pid.codes"`, `"Puya Semiconductor"` to be **present**, so the provenance
   paragraph stays. `_extract_shared_section` compares bodies by **exact string equality** (only
   trailing blank lines stripped, no whitespace normalisation) — so both copies must match
   character-for-character within §5. Gate is currently **41/41 GREEN**
   (`FIRESTARTER_META_ROOT=/workspaces python3 -m pytest tests/test_flash_path_record_sync.py -q`
   → `41 passed`). Firmware CLAUDE.md states plainly that this module *"runs in no CI leg on this
   branch"* — re-running it is a local obligation. `[VERIFIED: read + executed]`

**Corrected statement:** D-11's lockstep footprint is **§5(a) + §5(d)** in two copies, plus
`_L2_SHIP_GATE` in the test module if §5(c) moves, plus the two line-number citations. Safest
mechanical choice: place the source warning **below** line 24 so `20`/`24` stay true; otherwise
update both citations in both copies in the same change.

### C-5 — §5(c)'s ship gate, as worded, forbids exactly what D-11 does

**CONTEXT.md claim:** D-11 — *"The record's own §5(b) calls the interim id 'strictly better than the
status quo' and notes it 'does not weaken the ship gate, because the test id's own terms forbid
shipping.'"*

**Evidence:** `.planning/v1.23-FLASH-PATH-DECISION.md:202`, verbatim:

> **Ship gate: no PY32F071 board ships, and no release advertises a USB identity, until a PID
> allocated under VID 0x1209 exists.**

Line 204: *"This is deliberately a condition rather than a warning, so a future reader can fail it."*
`1209:0001` is *"the registry's documented private-testing product id"* (§5(b), :198) — **not** an
allocated PID. D-11 both lands it and has the release body **state** it. `[VERIFIED: read]`

**Corrected statement:** D-11's cited rationale answers the *"no board ships"* clause only. The
*"no release advertises a USB identity"* clause is unaddressed, and by the record's own design a
future reader will fail it. A plan must resolve this **on the record**, choosing one:
(a) amend §5(c) in lockstep (three places, per C-4) to distinguish *advertising an identity* from
*disclosing a non-allocated interim id*; or (b) leave §5(c) verbatim and state in `130-DECISION.md`
and `130-LEDGER.md` why a caveated disclosure of an explicitly-non-allocated test id is not
"advertising". Leaving it silent is precisely the shape — *an outward-facing artifact omits a known
problem* — that D-11's own third rejected option was rejected for.

### C-6 — pid.codes' terms say the source warning SHOULD exist, not MUST

**CONTEXT.md claim:** D-11 and `<domain>` both say *"the source warning pid.codes' terms **require**"*
(twice).

**Evidence:** the terms quoted verbatim at `.planning/v1.23-FLASH-PATH-DECISION.md:198`: *"Source
code and configuration that references this VID/PID **should** warn users that the PID is not
universally unique and should not be used outside test environments."* `[CITED: pid.codes terms as
transcribed in the v1.23 flash-path record]`

**Corrected statement:** Land the warning — it is the right call and §5(b) already argues for it —
but do not write *"required by pid.codes' terms"* into an outward-facing artifact. In a phase whose
entire purpose is not overclaiming, upgrading a registry's SHOULD to a MUST is itself an overclaim.
Correct wording: *"pid.codes' terms for `1209:0001` ask that source referencing it warn the PID is
not universally unique; this firmware does."*

### C-7 — "the superseded figures are live" materially overstates R-10

**CONTEXT.md claim:** `<code_context>` — *"The superseded figures are live: `2992 B` in
ROADMAP/PROJECT/STATE."*

**Evidence:** all six occurrences enumerated with context:

| Site | Context | Verdict |
|---|---|---|
| `PROJECT.md:71` | inside the labeled `⚠ RESEARCH CORRECTIONS` block, as *"not 2992 B"* | legitimate correction |
| `STATE.md:302` | inside the labeled `⚠ RESEARCH CORRECTIONS` bullet, as *"not 2992 B"* | legitimate correction |
| `PROJECT.md:32` | v1.22 archive: *"(119, +392 B against 2992 B headroom)"* | historically **correct** |
| `PROJECT.md:163` | v1.22 decision register: *"the live Leonardo figure is 25680/28672, leaving 2992 B"* | historically **correct** |
| `STATE.md:699` | Phase 119 decision log | historically **correct** |
| `STATE.md:700` | Phase 119 decision log: *"measured against the live 2992 B phase-base headroom (28672-25680)"* | historically **correct** |
| `ROADMAP.md:2468` | **Phase 130's own success criterion**, quoting `"2992 B"` as a needle to grep for | self-reference (see C-8) |

2992 = 28672 − 25680 was the **pre-Phase-119** headroom, which is exactly what Phase 119's +392 B was
judged against; R-10's own text says the figure *"predates Phase 119's own +392 B."* Not one
occurrence asserts 2992 as the **current** v1.23 headroom. `[VERIFIED: grep + read of every hit]`

**Corrected statement:** R-10 needs **no substantive correction** in any of the five files. Criterion
1's own escape clause — *"outside a labeled correction/history block"* — is already satisfied for six
of seven hits. The CLOSE-01 work for R-10 is to **record that it is already discharged**, and to make
the D-08 checker's label-awareness recognise *history* blocks (the v1.22 archive, the decision logs)
as well as *correction* blocks. Planning a sweep that "removes stale 2992s" would delete
historically-accurate records.

### C-8 — `ROADMAP.md:2468` makes the D-08 checker unable to go green without an explicit self-reference exemption

**CONTEXT.md claim:** the self-reference trap is flagged only for `130-LEDGER.md` under
Claude's Discretion (*"the scanner matches phrase shape regardless of quotation context … this bit
all six `125-0N-SUMMARY.md` files"*).

**Evidence:** `ROADMAP.md:2468` is Phase 130's own criterion 1 and reads *"verified by grepping for
each specific superseded figure/claim (e.g. "2992 B", py32 buffer "1024", "27 commits behind")."* A
phrase-table checker over `ROADMAP.md` fires on **three** of its own needles in that one line.
`ROADMAP.md:2414` (Phase 129 criterion 3) similarly carries *"a part with no VTOR"* bare and
unlabeled. `[VERIFIED: grep]`

**Corrected statement:** The same trap CONTEXT flags for the LEDGER applies to CLOSE-01's **new**
checker, and there it is worse: the needle table and the document that defines the needle table live
in the same file. D-08's design must carry, explicitly and with a fixture each: (i) a self-reference
exemption for the success-criteria region (or a `<!-- claimscan:allow -->`-style inline marker);
(ii) label-awareness for **history** blocks as well as correction blocks (C-7); (iii) the
planted-violation and mislabeled-block fixtures D-08 already names. Without (i) and (ii) the checker
can never go green on an honest tree, and the likely reaction — weakening the phrase table — is
exactly the fail-open outcome BASE-08 exists to prevent.

### C-9 — the "no VTOR" prose has THREE live sites, not two

**CONTEXT.md claim:** D-06 — *"PCB-03's 'on a part with no VTOR' and FUT-N04's 'Cortex-M0+ has no
VTOR' are both corrected … This widens CLOSE-01's stated four-file list by one."*

**Evidence:** live `no VTOR` occurrences across the six target files:

| Site | Text | State |
|---|---|---|
| `REQUIREMENTS.md:96` | PCB-03, *"on a part with no VTOR"* | already carries an inline correction after it |
| `REQUIREMENTS.md:116` | FUT-N04, *"Cortex-M0+ has no VTOR"* | **bare falsehood**, first of four deferral reasons |
| `ROADMAP.md:2414` | Phase 129 criterion 3, *"a stated vector-relocation implication for a part with no VTOR"* | **bare, unlabeled** |
| `PROJECT.md:97` | names the prose as *"deliberately left OPEN for Phase 130's CLOSE-01"* | correct reference |
| `STATE.md:90` | C-1 row | correct reference |

`STATE.md:90`'s own C-1 row enumerates the sites: *"'A part with no VTOR' appears in D-12,
REQUIREMENTS PCB-03, **ROADMAP criterion 3**, FUT-N04 and the linker comment."* The linker comment
was fixed in Phase 129; ROADMAP criterion 3 was recorded **AMENDED** in `129-NONREGRESSION.md` but
the ROADMAP line itself was never touched. `[VERIFIED: grep + read]`

**Corrected statement:** Three prose sites need correction, not two. `ROADMAP.md:2414` is inside
CLOSE-01's stated ROADMAP.md scope, so no requirement is widened — but D-06's framing ("two VTOR
clauses", "widens the file list by one") will lead a planner to fix only the REQUIREMENTS pair and
leave the ROADMAP criterion asserting a disproven fact. Name `ROADMAP.md:2414` explicitly in the
plan.

### C-10 — `PROJECT.md:836`'s footer is a live R-11 + retired-slot site CONTEXT does not name

**Evidence:** `PROJECT.md:836`, the document footer: *"**Next milestone: v1.29 PY32F071 USB Firmware
Install (host-side)** — implementation already exists and is green on `firestarter_app` branch
`feature/py32f071-fw-install` @ `311eacf` … Start with `/gsd-new-milestone`."* It carries R-11's
superseded head SHA (correct value `4ee64a1`) and points a future reader at a slot D-13 retires. It
is a dated footer, not a labeled correction block. `[VERIFIED: read]`

**Corrected statement:** Add `PROJECT.md:836` to CLOSE-01's site list. It is the single highest-risk
stale site in the tree because it is a *"start here next"* instruction and `/gsd-new-milestone` reads
`PROJECT.md` to seed scope — the same propagation hazard D-08's forward payoff is argued from.

### C-11 — CLOSE-03 must precede CLOSE-01's ROADMAP sweep; CONTEXT's ten constraints do not say so

**Evidence:** `ROADMAP.md:33` (the `v1.28 PY32F071 Port` entry D-13 deletes) carries, verbatim and
live: R-1's full superseded description (*"`include/rurp_platform.h` normalized platform IDs,
`rurp_millis()`/`rurp_delay_ms()`/`rurp_delay_us()` so common code never calls Arduino timing APIs,
board-local physical pin maps behind platform-independent logical identifiers, capability macros only
for facilities small AVR builds lack"*), R-8 (*"a 195-line `platform/py32f071/PORTING.md`"*), R-9
(*"999.23 leads"*), R-14 (`2c2ed10`, *"603 additions across 8 files"*), and the whole stale prior-art
paragraph. `ROADMAP.md:34` (the `v1.29` entry) carries R-11 (`311eacf`), R-5 (*"44 new unit tests"*),
and the `.hex`-hardcoding claim R-7 closed. `[VERIFIED: grep with per-hit snippets]`

**Corrected statement:** A new hard sequencing constraint, **11**: *CLOSE-03's collapse of ROADMAP
lines 33–34 runs before CLOSE-01's ROADMAP sweep.* Run CLOSE-01 first and it writes `⚠ CORRECTION`
blocks into two lines CLOSE-03 then deletes; run CLOSE-03 first and the great majority of CLOSE-01's
ROADMAP work is discharged by deletion, with the historical text preserved in git as D-13 intends.
This also satisfies CONTEXT constraint 9 (*"CLOSE-01's checker runs against the tree that actually
gets merged"*) at zero extra cost.

### C-12 — the v1.28 Milestones entry carries no supersession marker while v1.29's does

**Evidence:** `ROADMAP.md:34` opens *"⬜ **v1.29 PY32F071 USB Firmware Install (host-side)** — Phases
TBD (**⚠ SUPERSEDED — this slot is RETIRED into v1.23** … Marker added 2026-07-31; content left
otherwise untouched for Phase 130 to retire."* `ROADMAP.md:33` opens *"⬜ **v1.28 PY32F071 Port (HAL
prep + native backend)** — Phases TBD (QUEUED at the 2026-07-27 backlog review — not yet
scoped/activated; version number provisional)"* — **no marker at all**. `[VERIFIED: read]`

**Corrected statement:** D-13 treats lines 33 and 34 symmetrically. They are not. Line 33's stale
prior-art paragraph — the exact thing
`todos/pending/correct-v128-py32-roadmap-prior-art.md` was filed about, and the thing
`/gsd-new-milestone` reads — is currently **unwarned**. Consequence for D-16's before/after proof:
the two lines' diffs will not look alike, and any assertion phrased as "both slots carried a
supersession marker" is false.

### C-13 — the app b15 cut is gated on a full green `pytest tests/` plus two codegen gates in CI

**CONTEXT.md claim:** `<code_context>` and the canonical refs describe `beta-release.yml` only as
*"same trigger shape and auto-increment."*

**Evidence:** `firestarter_app/.github/workflows/beta-release.yml` runs, in order and all **blocking,
before** the version bump and the release step: `pip install -e .[test]` → `codegen.py --check` →
the `messages.py` codegen drift gate (`git diff --exit-code firestarter/messages.py`) →
**`pytest tests/ -v`**. Measured on the milestone tip this session:

```
$ python3 -m pytest tests/            → 1303 passed in 115.66s   (py3.12, no /dev/ttyACM* attached)
$ python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check
  OK: catalog valid (73 messages, version 1).
$ git diff --exit-code firestarter/messages.py            → clean
```

CI pins Python **3.11**. The known live-board REDs (`test_no_programmer_found_*`) cannot fire on a
runner. The HOST-04 mypy-debt RED (69 errors) lives in a **different** workflow (`ci.yml`) and does
not gate the cut. `[VERIFIED: executed + read]`

**Corrected statement:** Any RED in the app suite means **no app b15 at all**, which breaks D-01's
lockstep pairing (*"a firmware asset with no published host that can install it is inert, and vice
versa"*) after the firmware half has already published. Record the pre-flight suite state in
`130-DECISION.md` as a measured gate, not an assumption — the pattern `122-DECISION.md` already uses
for branch tips. The firmware side's equivalent blocking steps are `pio test -e native` and
`pytest tests/`; the firmware suite measures **221 passed** locally
(matching PROJECT.md's recorded 180 → 221).

### C-14 — `paths-ignore` could suppress a cut entirely; verified it will not this time

**Evidence:** firmware `beta-build.yml` ignores `**.md`, `**.sh`, `.gitignore`, `docs/**`,
`documents/**`, `images/**`, `.vscode/**`, `.editorconfig/**`. App `beta-release.yml` additionally
ignores `.github/**` and `tools/**`. Measured non-ignored changed files vs `origin/beta`:
**112** (firmware) and **32** (app). `firestarter/.github/workflows/py32f071.yml` has
`push: branches: [beta]` with **no** paths filter, so the loud ARM gate always fires.
`[VERIFIED: git diff --name-only + read]`

**Corrected statement:** Both pushes will trigger. Worth recording because a documentation-only close
would silently cut **nothing** while looking successful — and D-11's `usb_cdc.c` edit is not what
saves it here; 112 code files already do.

### C-15 — b15 is deterministically derivable, and the "blank beta_version writes a stable version" trap does not apply to this push

**Evidence:** `.github/scripts/update_version.py:53-61` — `is_beta_mode()` returns True when
`GITHUB_REF == "refs/heads/beta"`, so a **push** to `beta` takes the beta path with `BETA_VERSION`
empty. Then `compute_beta_version` → `_git_tag_scan_fallback("3.0.0")` → `git tag --list "3.0.0b*"`,
`max(nums)+1`. Tag ceiling verified `3.0.0b14` in both repos (`git tag --list | sort -V`), and
`actions/checkout` uses `fetch-depth: 0`, so all tags are present. `[VERIFIED: read + git tag]`

**Corrected statement:** The auto-increment target is **b15** in both repos, deterministically.
CONTEXT constraint 5 nonetheless stands and should not be relaxed — the *observed* tag is read from
`gh release list` because a concurrent cut, a tag pushed out of band, or a rehearsal-tag collision
would change it. Separately, the *"blank `beta_version` writes a STABLE version"* trap applies only
to a `workflow_dispatch` on a **non-`beta`** ref (where `GITHUB_REF` is not `refs/heads/beta`); it is
irrelevant to this phase's push and relevant only if a rehearsal is ever re-run.

### C-16 — two citation ranges in the canonical refs are wrong, one of them dropping deferrals D-10 needs

**Evidence:** verified against `REQUIREMENTS.md`: §Validation Ceiling `:8-22` ✓; CLOSE-01…04
`:102-105` ✓; PCB-03 `:96` ✓; FUT-N04 `:116` ✓. But §"Future Requirements" is `:109-128`, **not
`:108-123`** — the cited range stops at FUT-CAL (:123) and excludes **FUT-ORACLE (:127)** and
**FUT-ARMSIZE (:128)**, two of the eight deferrals D-10 must carry. And the REL-01…04 parentheticals
are `:85-88`, not `:86-89`. All eight named deferrals (FUT-N02, FUT-N04, FUT-N05, FUT-N06, FUT-VPP,
FUT-CAL, FUT-ORACLE, FUT-ARMSIZE) do exist and are exactly eight. `[VERIFIED: read]`

### C-17 — A-5's "operator-visible flash-constraint decision" is a spine deliverable with no home in D-01…D-16, and is already discharged

**Evidence:** `.planning/research/SUMMARY.md:301` assigns Phase 130 *"the **A-5 flash-constraint
decision, operator-visible**."* CONTEXT's canonical refs cite A-5, but none of D-01…D-16 addresses
it. It is already satisfied: `REQUIREMENTS.md` Operator Decision #4 restates the constraint as
*"Leonardo flash must not grow; Uno-class growth ≤ 64 B, recorded"*, MERGE-05 encodes it, and Phase
124 closed SUMMARY:345's single-source gap with an independent 328PB build —
`124-NONREGRESSION.md` §F4d: `PASS: uno(23954[+22<=64]), uno328pb(24004[+28<=64]),
leonardo(26016[-56<=0])`. `[VERIFIED: read]`

**Corrected statement:** Record A-5 in `130-LEDGER.md` / `130-NONREGRESSION.md` as **discharged at
Phase 124, with the operator restatement cited**, rather than planning fresh work or leaving a spine
deliverable silently unaddressed.

### C-18 — two new community `[dev test]` reports arrived after the import; neither is this phase's work

**Evidence:** `gh issue list --repo henols/firestarter_prom --state open` returns gh#20
(*"[dev test] at28c256 — FAIL"*, 2026-07-30) and gh#18 (*"[dev test] fm1608 — PASS"*, 2026-07-28) —
both **after** the 2026-07-27 import that stopped at gh#17. `[VERIFIED: gh issue list]`

**Corrected statement:** CONTEXT's *"v1.23 has no outstanding reporter and no requirement depends on
a reply"* is true **as to requirements** — no CLOSE id needs a comment. But the inbox is not empty,
and gh#20 is an AT28C256 FAIL arriving via v1.21's submission flow the day v1.22 shipped its SDP fix.
Out of scope for Phase 130; do not silently imply the inbox is clear in any closing artifact.

---

## Live State Re-Verification (2026-08-02, this session)

CONTEXT.md instructs *"re-verify at plan time, do NOT inherit."* Every item re-measured.

| CONTEXT.md claim | Verdict | Measured value |
|---|---|---|
| Both sub-repos on `v1.23-py32f071-integration` | **AGREES** | both `git rev-parse --abbrev-ref HEAD` = `v1.23-py32f071-integration` |
| `firestarter` at `5a89ee7` | **AGREES** | `5a89ee7` |
| `firestarter` 83 ahead / 0 behind `origin/beta` (`5c9160a`) | **AGREES** | `rev-list --left-right --count origin/beta...HEAD` → `0  83`; origin/beta `5c9160a` |
| `firestarter_app` at `cc9452f` | **AGREES** | `cc9452f` |
| `firestarter_app` 37 ahead / 0 behind `origin/beta` (`e7d3ee8`) | **AGREES** | `0  37`; origin/beta `e7d3ee8` |
| Zero behind in both → no inbound catch-up merge | **AGREES** | confirmed; outbound merge is clean in both |
| Tag ceiling `3.0.0b14` in both repos | **AGREES** | `git tag --list \| sort -V`: …b12, b13, **b14**, v1.21, v1.22 in both |
| b14 live on GitHub in both repos, 2026-07-30 | **AGREES** | fw `3.0.0b14` 2026-07-30T14:28:19Z; app `3.0.0b14` 2026-07-30T14:58:35Z, both `Pre-release`, neither draft |
| PyPI carries `3.0.0b14`; latest stable `2.0.7` | **AGREES** | `info.version` = `2.0.7`; `3.0.0b14` uploaded 2026-07-30T15:12:52; `3.0.0b15` absent |
| Meta gitlinks match working tips | **AGREES** | `git ls-tree HEAD` → `5a89ee76…` / `cc9452f4…` |
| `gh` authenticated as `henols`, scopes `gist, read:org, repo, workflow` | **AGREES** | exact match |
| `ROADMAP.md` `## Milestones` has no v1.23 PY32F071 Integration entry | **AGREES** | line 27 `✅ v1.22` → line 28 `⬜ v1.23 Binary Command Protocol`; only `PY32F071 Integration` hit in the list region is inside line 34's marker |
| The superseded figures are live | **PARTIALLY DRIFTED** | see **C-7** — every `2992` hit is a labeled correction, a historically-correct archive statement, or criterion 1's own needle |
| Working-tree dirt: app modified `.gitignore` + untracked `.coverage`, `.planning/config.json`, `SECURITY.md`, `write_test_port.sh`; meta shows `m firestarter_app` | **AGREES** | exact match; **`firestarter` tree is fully clean** (relevant: `test_dirty_tree_is_detected` exists in the sync gate) |
| `config.json` `planning.sub_repos` lists four repos | **AGREES** | `firestarter`, `firestarter_app`, `firestarter_app_py32`, `firestarter_py32_ci` — and **all four directories exist on disk**, so a naive iteration really does reach the two scratch worktrees |
| *(new)* local `beta` vs `origin/beta` | **0 / 0 in both repos** | fw `beta` = `5c9160a` = origin/beta; app `beta` = `e7d3ee8` = origin/beta. The lag CONTEXT warns about is **post-CI only** |
| *(new)* b14 published assets | fw: `firestarter_leonardo.hex`, `firestarter_uno.hex`, `firestarter_uno328pb.hex` — **no py32 asset**. app: **zero assets**. | Confirms D-03's premise: b15 would be the first py32 asset ever published |
| *(new)* `3.0.0b12` on PyPI | **ABSENT** | corroborates the "6 of 13 app betas never reached PyPI" pattern behind constraint 6 |
| *(new)* run `30722352902` | readable, `conclusion: success`, SHA `7a0a375`, `event: workflow_dispatch` | D-01's cited rehearsal evidence survives |
| *(new)* run `30722537152` | readable, `conclusion: success`, SHA `6c1c31f` | REL-03's contained-ARM evidence survives |

---

## The R-1…R-18 Work List (raw material for CLOSE-01 and D-08's phrase table)

Enumerated verbatim from `.planning/research/SUMMARY.md` §"Corrections to the Planning Record"
(`:183-202`), then grepped across the six target files: `PROJECT.md`, `STATE.md`, `ROADMAP.md`,
`.planning/notes/py32f071-port-branch-state.md`, `REQUIREMENTS.md`. `[VERIFIED: grep with
per-hit snippets]`

**Note on scope drift:** SUMMARY.md's own header says the list *"is to be applied to both PROJECT.md
and STATE.md"* — two files. CLOSE-01 widened it to four; D-06/D-07 widen it to five (REQUIREMENTS);
C-10 argues the `PROJECT.md` footer belongs too. The six-file set below is what the checker should
scan.

| # | Superseded claim (needle) | Live sites | Already labeled? | Action |
|---|---|---|---|---|
| **R-1** | `portability-macros` provides normalized platform IDs / timing abstraction / pin maps / capability macros | `ROADMAP.md:33`; partial at `:1725`, `:1732` | ✗ (line 33 unmarked, C-12) | **Discharged by CLOSE-03's line-33 deletion** (C-11). `PROJECT.md:42` already states the corrected "compat-shim layer" wording |
| **R-2** | py32 `DATA_BUFFER_SIZE = 1024` | `PROJECT.md:59`; `notes:53` | ✗ both | `PROJECT.md:59` is a **false current-fact inside a `⚠`-labeled block about a different subject** — label-awareness would skip it; must be corrected in prose. `notes:53` → SUPERSEDED section. `PROJECT.md:75` already carries the corrected 512 |
| **R-3** | branches are 27 commits behind `beta` | `notes:20-24` (table, 5×), `notes:29`, `notes:132`; `ROADMAP.md:2468` (needle quote) | ✗ | append-only SUPERSEDED section per D-05; ROADMAP:2468 is self-reference (C-8) |
| **R-4** | the 72 commits "include the whole v1.22 milestone" | **NONE** | — | already-corrected phrasing everywhere; record as no-op. **Hollow phrase-table entry risk** — nothing to detect |
| **R-5** | host branch has 44 unit tests | `ROADMAP.md:34` (*"44 new unit tests"*) | ✓ (line 34 carries `⚠ SUPERSEDED`) | discharged by CLOSE-03's line-34 collapse |
| **R-6** | `cli_handlers.py:819` holds the board list | `notes:96` | ✗ | SUPERSEDED section (correct: `:932`) |
| **R-7** | `.hex` extension hardcoded / needs work | `notes:94` | ✗ | SUPERSEDED section (`asset_candidates()`/`_pick_asset()` closed it) |
| **R-8** | *"CRC-validated dual-slot flash per `PORTING.md`"* | `ROADMAP.md:33`, `:1732`, `:1747`, `:1883`, `:2233`; `PROJECT.md:45`; `notes:61`; `REQUIREMENTS.md:139` | mixed | `ROADMAP:33` → CLOSE-03 deletion; `:1732` → D-15's 999.23 retirement; `:1747`/`:1883` are dated review-history paragraphs; `:2233` is a Phase-126 research-flag (historical); `PROJECT.md:45` already carries the `⚠ DESIGN work` correction inline; `notes:61` → SUPERSEDED |
| **R-9** | build order: portability-macros first | `ROADMAP.md:33`, `:1732`, `:1883`; `PROJECT.md:69` | `PROJECT.md:69` ✓ (inside `⚠ RESEARCH CORRECTIONS`) | ROADMAP:33 → CLOSE-03; `:1732` → D-15; `:1883` history |
| **R-10** | Leonardo headroom ≈ 2992 B | 6 sites + criterion quote | 2 ✓ correction, 4 ✓ history | **no substantive correction needed — see C-7** |
| **R-11** | host branch head `311eacf` | `PROJECT.md:836`; `ROADMAP.md:34`; `notes:107` | `ROADMAP:34` ✓ only | `PROJECT.md:836` is the **unnamed high-risk footer (C-10)**; `notes:107` → SUPERSEDED |
| **R-12** | *(new)* Leonardo RAM never recorded | **NONE** (now recorded: BASE-01, `size_baseline_base01.json`) | — | record as discharged |
| **R-13** | *(new)* PY32 SRAM assumed 20 K | **NONE** — no `20 K…SRAM` collocation in any target file | — | record as discharged; `PROJECT.md:38` states 16 KiB correctly |
| **R-14** | *(new)* `feature/py32f071-release-assets` a third stack; `2c2ed10` / 603 additions / 8 files | `ROADMAP.md:33`, `:1732`, `:1747`, `:1883`; `PROJECT.md:55`, `:58`; `STATE.md:309`; `notes:12` | `PROJECT.md:55/58` ✓, `STATE.md:309` ✓, `notes:12` ✓ (all quote it **to refute it**) | ROADMAP:33 → CLOSE-03; `:1732` → D-15; `:1747`/`:1883` history |
| **R-15** | *(new)* `py32f071.yml` has no `push` trigger; ARM unbuildable in this devcontainer | `PROJECT.md:70` ✓, `STATE.md:302` ✓ (no-push half, now **fixed** by MERGE-03); `REQUIREMENTS.md:18` ✗ (toolchain-absent half) | half/half | **R-15 has two halves and both moved.** The no-push half is fixed in code (`py32f071.yml` now carries `push: branches: [beta]`, verified). The toolchain-absent half is **itself false** — this is D-07's target at `REQUIREMENTS.md:18` |
| **R-16** | *(new)* README advises a glob then supplies a literal; `beta-build.yml:92` glob excludes `build/py32f071/` | **NONE** in the six planning files | — | subject is firmware-repo files, both fixed by REL-02 (`files:` now has two entries, second is `build/py32f071/firestarter_*.hex`, verified). Record as discharged |
| **R-17** | *(new)* `write_checksums.cmake` orphaned | `REQUIREMENTS.md:50` ✓, `ROADMAP.md:2101`/`:2118` ✓, `STATE.md:794` ✓ — all record it as **deleted** | ✓ all | discharged by MERGE-08; no stale assertion anywhere |
| **R-18** | *(new)* `DEV_TOOLS` absent on ARM reads as a decision | `REQUIREMENTS.md:50` ✓ (records it made explicit) | ✓ | discharged by MERGE-08 |

**Summary of the actual CLOSE-01 work list**, after label- and history-awareness and after C-11's
ordering:

- **`ROADMAP.md`** — CLOSE-03's collapse of lines 33–34 discharges R-1, R-5, R-8(partial), R-9(partial),
  R-11(partial), R-14(partial) in one edit. Remaining: **`:2414`** (C-9, no-VTOR), and a decision on
  whether `:1732`/`:1749` (D-15's stubs) and the dated review-history paragraphs `:1747`/`:1883` are
  history-exempt.
- **`PROJECT.md`** — `:59` (R-2, a false current fact inside a `⚠` block about something else),
  **`:836`** (C-10, R-11 + retired-slot pointer). `:45`, `:69`, `:70`, `:71`, `:75`, `:97` already
  correct or correctly labeled.
- **`STATE.md`** — no stale assertion found. `:90`, `:302`, `:309`, `:794` all correct or correctly
  labeled. In-place edits per D-05 are additive, not corrective.
- **`.planning/notes/py32f071-port-branch-state.md`** — append-only SUPERSEDED section covering
  `:12`(context), `:20-24`, `:29`, `:53`, `:61`, `:94`, `:96`, `:107`, `:132`. Frontmatter
  `date: 2026-07-28` confirmed, which is D-05's stated justification.
- **`REQUIREMENTS.md`** — `:18` (D-07), `:96` + `:116` (D-06).

**Six R-Ns have zero live stale occurrences** (R-4, R-12, R-13, R-16, plus R-17/R-18 already recorded
as fixed) and one (R-10) has no *substantive* one. A phrase-table entry for a needle that appears
nowhere is unfalsifiable — an unprovable leg, the shape Phase 129's F-item warns about. Record them
as **discharged with evidence** in `130-NONREGRESSION.md` instead of manufacturing checker legs for
them.

---

## The Four-Artifact Contract — validated

`.planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py`, read in
full and executed. `[VERIFIED: read + executed]`

| Property | Finding |
|---|---|
| `_DEFAULT_TARGETS` names the four `130-*` files | **Yes**, lines 86–91 — but joined to `_HERE` = **Phase 123's** directory. **See C-2.** |
| All-or-nothing arming (D-15) | **Confirmed by code**, `main()` lines 254–280: `used_defaults = not argv and env is None`; zero-of-four → `UNARMED:` + exit **0**; one-to-three-of-four → hard fail naming the missing. Arming applies **only** to the default set — argv/env targets take the ordinary fail-closed branch (lines 281–291) |
| Never-vacuous guard hoisted above missing-target | Confirmed, lines 242–252 — deliberate hardening over v1.22's ordering |
| Self-reference trap semantics | `scan_text()` lines 168–199 matches phrase **shape** on a raw line with **no quotation, citation or code-fence awareness**. A ledger that quotes a forbidden phrase to disclaim it **will** trip its own gate |
| Proximity window | `PROXIMITY_WINDOW = 1` → a **3-line** window (`lineno-1 … lineno+1`). A forbidden match reports only if a `/py32/i` token appears on that line or either neighbour |
| Required caveat | `"no PY32F071 hardware exists"` (whitespace-tolerant regex), checked **document-level**, not proximity-scoped. **All four artifacts must carry it** |
| Known interaction, documented in-file | Lines 144–153: an honest negation such as *"nothing about the PY32F071 is silicon-verified"* trips `silicon-verified`. The sanctioned response is the canonical caveat sentence, **never** narrowing `FORBIDDEN_PATTERNS` or `PY32_TOKEN_RE` |
| Eight forbidden patterns | `runs-on-py32`, `works-end-to-end`, `silicon-verified`, `bench-validated`, `hardware-validated`, `flashed-a-py32`, `closed-loop-vpp`, `pin-map-correct`. First and sixth are narrowed to an explicit py32 object; the rest are broad and rely entirely on proximity |
| Env seam | `FIRESTARTER_CLAIMSCAN_TARGETS`, read at **module import** (line 104) — must be set in a child process, not monkeypatched |
| Paired test suite | **1 failed / 9 passed** — see **C-3** |
| v1.22 precedent | `.planning/phases/122-…/check_permitted_claims.py:50-56` — five targets, same `_HERE` idiom, correct there. v1.22 also shipped `122-CUT.md`, `122-CHANNELS.md`, `122-DELIVERY.md` **outside** its scanned set, so the precedent for adding an unscanned artifact exists |

**Implication for Claude's Discretion:** if Phase 130 adds a fifth artifact (e.g. a channels
transcript) and it is *not* meant to be scanned, v1.22's precedent covers it — `_DEFAULT_TARGETS`
need not grow. Only a **rename of, or an addition to, the scanned set** requires the same-commit
amendment. Either way, C-2's directory fix is required regardless.

---

## D-11's Firmware Change — verified on disk

`[VERIFIED: read]`

| Question | Answer |
|---|---|
| Does `usb_cdc.c` define `0x36B7`/`0xFFFF`? | **Yes.** `firestarter/platform/py32f071/src/usb_cdc.c:20` `#define FIRESTARTER_USB_VID 0x36B7U`; `:24` `#define FIRESTARTER_USB_PID 0xFFFFU` |
| Guarded? | Both wrapped in `#ifndef` (`:19`, `:23`) — a `-D` could override, but the default descriptor presents `36B7:FFFF` |
| Consumed where? | `:35-36`, inside the `USB_DEVICE_DESCRIPTOR_INIT` call building `firestarter_cdc_descriptor` |
| Any other VID/PID site in the py32 tree? | **No** — only `usb_cdc.c:20` and the record's own prose |
| What does the meta record's §5(a) say? | `.planning/v1.23-FLASH-PATH-DECISION.md:196` — cites *"line 20"* and *"line 24"* verbatim (see C-4 item 3) |
| Is the firmware subset byte-identical there? | **Yes** — `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md:106` is the same paragraph; `test_shared_sections_match[S4]` passes |
| How does the sync gate compare? | `_extract_shared_section` (lines 167–213): span-scoped between the `## ` heading carrying `[SHARED:S4]` and the next `## ` heading; heading excluded; **trailing blank lines stripped**; otherwise **exact string equality**. No whitespace normalisation. Duplicate marker → `refusing to guess`; missing marker → `None` → non-vacuity `AssertionError` |
| Leg count | **41**, all currently **passing** (`FIRESTARTER_META_ROOT=/workspaces python3 -m pytest tests/test_flash_path_record_sync.py -q` → `41 passed`) |
| Runs in CI? | **No.** `firestarter/CLAUDE.md` states it plainly: *"that test module runs in no CI leg on this branch, so the enforcement is a local-run obligation."* |
| `_S4_NEEDLES` constraints on the edit | Must keep `0x1209`, `1209:0001`, `pid.codes`, `0x36B7`, `0xFFFF`, `Puya Semiconductor`, `usbd_cdc_if.c`, `pycdc.inf`, `0ed2f4b…`, `0x0448`, `py32_dfu.py`, `0xFE/0x01` all present in §5 |
| `_L2_SHIP_GATE` | Byte-exact literal at `test_flash_path_record_sync.py:345-348`. Touching §5(c) is a **third** edit site (C-4) |
| pid.codes `1209:0001` semantics | The registry's documented **private-testing** product id; terms permit in-house testing, forbid use on redistributed/sold/manufactured devices, and say source referencing it **should** warn it is not universally unique (C-6). Not an allocated PID — which is what makes §5(c) bite (C-5) |

---

## CLOSE-03's Subject Matter — exact current lines

`.planning/ROADMAP.md` `## Milestones` list. `[VERIFIED: read]`

| Line | Entry | Role in CLOSE-03 |
|---|---|---|
| 27 | `✅ **v1.22 AT28C Software Data Protection Lifecycle**` | boundary; unchanged |
| **28** | `⬜ **v1.23 Binary Command Protocol**` | renumbered → **v1.28** and **moved** after line 32 (D-14); line 28 becomes `✅ v1.23 PY32F071 Integration — Phases 123–130` (D-13) |
| **29** | `⬜ **v1.24 Bus-Config Mask-Model Redesign**` | **byte-unchanged** (D-16) |
| **30** | `⬜ **v1.25 Jumper-Display Correctness & 2516-Family Support**` | **byte-unchanged** |
| **31** | `⬜ **v1.26 White-Box Voltage-Reading Calibration**` | **byte-unchanged** |
| **32** | `⬜ **v1.27 Per-Protocol EPROM Programming Algorithms**` | **byte-unchanged** |
| **33** | `⬜ **v1.28 PY32F071 Port (HAL prep + native backend)**` | collapses into the retirement line. **Carries no supersession marker (C-12)** and holds the stale prior-art paragraph plus R-1/R-8/R-9/R-14 |
| **34** | `⬜ **v1.29 PY32F071 USB Firmware Install (host-side)**` | collapses. Already carries `⚠ SUPERSEDED — this slot is RETIRED into v1.23 … Marker added 2026-07-31; content left otherwise untouched for Phase 130 to retire` |
| 35 | `⬜ **v1.30 SDP Surface Retirement & Behavioral Lock Proof**` | untouched per D-14, **except** its back-reference *"the v1.29 slot immediately above is still occupied by the py32 USB-install entry until v1.23's Phase 130 retires it"* — the **only** occurrence of that phrase in the file |

**No `v1.23 PY32F071 Integration` entry exists in the list — CONFIRMED.** The only
`PY32F071 Integration` hit in the list region is inside line 34's supersession marker.

**The stale prior-art paragraph**, verbatim from line 33:

> **Prior art — verified 2026-07-27:** [`henols/firestarter` PR #46] ("Add native PY32F071 HAL,
> backend plan, and firmware toolchain") was **CLOSED unmerged as a draft on 2026-07-21**, so this
> work is *not* in flight — but the branch `feature/py32f071-toolchain` survives at `2c2ed10` with
> 603 additions across 8 files, including a 195-line `platform/py32f071/PORTING.md` stating the
> combined HAL + native-backend contract, plus an ARM GCC CMake toolchain, PY32F071xB linker script,
> Puya-derived vector table and a CI workflow emitting ELF/BIN/HEX + SHA256SUMS. **Start scoping
> from that branch, not from scratch.**

**Backlog stubs and back-references (D-15):** `[VERIFIED: grep + read]`

| Site | Text | D-15 action |
|---|---|---|
| `:1723` | `### Phase 999.23: Prepare firmware HAL for PY32F071 (⏫ QUEUED 2026-07-27 → v1.28, leads — gh#16)` | retire as shipped-into-v1.23; the `→ v1.28` pointer breaks on the renumber |
| `:1732` | 999.23 disposition — carries `provisional v1.28 PY32F071 Port`, *"999.23 leads"*, PR #46 closed-unmerged, `2c2ed10`, `PORTING.md` (195 lines) | retire + correct |
| `:1738` | `### Phase 999.24: Native PY32F071 firmware backend … (⏫ QUEUED 2026-07-27 → v1.28, follows — gh#17)` | retire |
| `:1749` | 999.24 disposition — *"follows 999.23 inside the provisional `v1.28 PY32F071 Port` milestone slot"* | retire + correct |
| `:1755` | `### Phase 999.25: Retire dev sdp … (⏫ QUEUED 2026-07-31 → v1.30, NEXT after v1.23)` | **untouched** per D-15 |
| `:35` | v1.30 entry, *"the v1.29 slot immediately above"* | correct to name the retirement |
| `:1883` | Third-review-pass history paragraph — carries *"999.23 + 999.24 → `v1.28 PY32F071 Port`"* **and** the stale prior-art (*"scope v1.28 from that document"*) | **not named by D-15.** A dated review-history paragraph; decide history-exempt vs corrected, and record the choice |
| `:1877`, `:1879`, `:1887` | earlier dated review-pass paragraphs referencing 999.23/999.24 counts | history; record as exempt |

**D-15 nuance:** the phrase *"the v1.29 slot immediately above"* occurs **only once** (line 35).
D-15 says *"The `v1.30` entry's **and 999.25's** … back-references are corrected"* — 999.25's stub
(`:1755+`) does **not** contain that phrase. Its heading does carry `→ v1.30, NEXT after v1.23`,
which stays true. So the 999.25 half of D-15 may be a no-op; verify before planning an edit.

**The owning todo:** `.planning/todos/pending/correct-v128-py32-roadmap-prior-art.md` — five numbered
corrections plus a header note recording that v1.23 research re-verified all five and found a sixth
(A-6/R-8, `PORTING.md` absent from the live branch). `resolves_phase: 130`. Its closing note is the
propagation argument D-08 reuses: *"Do this before v1.28 is activated, not after —
`/gsd-new-milestone` reads this entry to seed scope."* Move to `.planning/todos/completed/` when
CLOSE-03 lands.

---

## Release Mechanics — verified from the workflow files

`[VERIFIED: read + gh + git]`

### `firestarter/.github/workflows/beta-build.yml`

| Property | Value |
|---|---|
| Trigger | `push: branches: [beta]` with `paths-ignore` = `**.md`, `**.sh`, `.gitignore`, `docs/**`, `documents/**`, `images/**`, `.vscode/**`, `.editorconfig/**` |
| Dispatch inputs | `beta_version` (optional string) **and** `rehearsal` (typed boolean, permanent by design) |
| Rehearsal resolution | `steps.mode` resolves once and echoes to `$GITHUB_STEP_SUMMARY`; `draft:` and `tag_name:` read only `steps.mode.outputs.rehearsal`, never `inputs.rehearsal` |
| Version step | `env: BETA_VERSION: ${{ github.event.inputs.beta_version }}` → `update_version.py`, then `stefanzweifel/git-auto-commit-action@v5` |
| Auto-increment | `is_beta_mode()` True via `GITHUB_REF == refs/heads/beta` on a push; `_git_tag_scan_fallback` scans `3.0.0b*` → `max+1` → **b15** |
| ARM step | `id: arm`, **`continue-on-error: true`** at the call site (never inside the composite action) |
| Missing-image report | `if: steps.arm.outcome == 'failure'` — keyed on `outcome`, not `conclusion` (the P128 run-B finding) |
| `files:` | two entries: `.pio/build/**/firestarter_*.hex` and **`build/py32f071/firestarter_*.hex`** — a **glob**, matches `firestarter_py32f071.hex` |
| `fail_on_unmatched_files` | **not set** → default `false` → an unmatched glob **warns**, does not fail |
| Release | `prerelease: true`; `draft:`/`tag_name:` rehearsal-gated |

### `firestarter/.github/workflows/py32f071.yml`

`push: branches: [beta]` with **no** paths filter (MERGE-03, implemented literally), plus
`pull_request` on py32/include/src/lib paths, plus `workflow_dispatch`. **No `continue-on-error`** —
the LOUD gate. Its header comment records the loud/soft split and states the removal trigger for
`beta-build.yml`'s containment is silicon validation, which is unreachable this milestone.

### `firestarter_app/.github/workflows/beta-release.yml`

`push: branches: [beta]` with `paths-ignore` additionally covering `.github/**` and `tools/**`.
Blocking pre-release steps: `pip install -e .[test]` → catalog validity check → `messages.py` codegen
drift gate → **`pytest tests/ -v`** (see **C-13**). Then version bump → auto-commit → resolve
post-bump SHA → `softprops/action-gh-release@v2` with `tag_name`, `target_commitish`,
`prerelease: true`, `make_latest: false`, and `GITHUB_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}`.
**No `files:`** — app betas publish zero assets (confirmed: b14 has none).

### `firestarter_app/.github/workflows/publish.yml`

`on: release: types: [published]` **plus** `workflow_dispatch` with a **required** `tag` string.
In-file comment records the cause: *"when a release is created by another workflow … using a PAT that
lacks `workflow` scope, GitHub suppresses the release.published event."* Checkout uses
`ref: ${{ github.event.inputs.tag || github.ref }}`. This is why constraint 6's manual dispatch is
the norm — and `3.0.0b12`'s absence from PyPI corroborates it.

### Prior-run evidence

`30722352902` (SHA `7a0a375`, `workflow_dispatch`, `conclusion: success`) and `30722537152`
(SHA `6c1c31f`, `conclusion: success`) are both still readable via `gh run view`. D-01's rejection of
a fresh rehearsal rests on real, still-available evidence.

---

## Things That Would Break a Plan

1. **A green claim-gate run that scanned nothing** (C-2) — the highest-value fail-open in the phase.
2. **A RED checker suite mistaken for the phase's own damage** (C-3) — it predates the phase.
3. **Nine decisions invisible to the planner and plan-checker** (C-1).
4. **A phrase-table checker that can never go green** (C-8) — because criterion 1 quotes its own
   needles, and four legitimate v1.22-archive hits need history-exemption.
5. **`config.json`'s four-entry `sub_repos`** — all four directories exist (`firestarter`,
   `firestarter_app`, `firestarter_app_py32`, `firestarter_py32_ci`). Any close step that iterates the
   list reaches into two scratch worktrees that are not deliverables. Iterate the two named repos
   explicitly, as CONTEXT says.
6. **A CLOSE-01 sweep that runs before CLOSE-03** (C-11) — wasted edits or vanished corrections.
7. **A `[SHARED:S4]` edit that lands in only two of three places** (C-4) — `_L2_SHIP_GATE` is a
   byte-exact test constant, and §5's body comparison is exact string equality.
8. **A source-warning comment inserted above `usb_cdc.c:20`** (C-4) — silently falsifies §5(a)'s
   line citations in both copies.
9. **An app suite RED after the firmware half has published** (C-13) — the lockstep pair breaks
   asymmetrically, with the firmware asset already public.
10. **The sync gate's dirty-tree leg** — `test_dirty_tree_is_detected` exists; the firmware tree is
    clean now, and `firestarter_app`'s pre-existing dirt (untracked `.planning/config.json`,
    `SECURITY.md`, `write_test_port.sh`, `.coverage`; modified `.gitignore`) must not be read as this
    phase's damage.
11. **Constraint 5 vs a literal `3.0.0b15`** — no command intended to be run verbatim may contain the
    literal. b15 is derivable (C-15) but must still be **read** from `gh release list`.
12. **`--auto`/`--chain` auto-approving the outward-facing gates** — D-02's wording review and the
    push must be gated **structurally**, by which plan owns which command, never by a checkpoint type
    or an `autonomous:` flag.
13. **Premature requirement ticking** — 4× in Phase 116. Only the closing plan may tick
    CLOSE-01…CLOSE-04; name the allowed ids in every dispatch prompt and re-read `REQUIREMENTS.md`
    after each plan.

---

## Project Constraints (from CLAUDE.md)

`/workspaces/CLAUDE.md`, `firestarter/CLAUDE.md`, `firestarter_app/CLAUDE.md` — all read.

- **Meta repo tracks only `.planning/` and `.claude/`.** Its claim *"Neither sub-repo is committed
  here"* is imprecise: `.gitmodules` exists and gitlinks are tracked — D-04's subject. Verified:
  `git ls-tree HEAD` returns `160000 commit` entries for both.
- **Serial-protocol and constant changes must stay in lockstep** between
  `firestarter_app/firestarter/serial_comm.py` / `constants.py` and `firestarter/src/firestarter.cpp`
  / `include/firestarter.h`. **Not touched by this phase** — D-11 changes only two USB descriptor
  `#define`s in a py32-only TU.
- **`firestarter/CLAUDE.md` names the five `[SHARED:S*]` keys** and the three-places convention, and
  states explicitly that `test_flash_path_record_sync.py` **runs in no CI leg**, making a local
  re-run a stated obligation for anyone editing either copy. It also warns *"do not imply CI
  coverage."*
- **`firestarter_app/CLAUDE.md`'s tooling gate is validated against py3.9/3.11 CI targets, not the
  devcontainer's 3.12.** All local suite runs in this document were on 3.12; CI runs 3.11.
- **`messages.h`/`messages.py` are codegen-generated.** Not touched by this phase; the app's codegen
  drift gate is nonetheless a blocking pre-cut step (C-13) and is currently clean.
- **Firmware `pytest tests/` and `pio test -e native`** are blocking pre-cut steps. Local:
  221 passed. A CMakeLists source-path rename trips Phase 123's manifest gate **before** ARM builds
  (the P128 run-B lesson) — D-11 does not touch CMakeLists.

---

## Validation Architecture

`workflow.nyquist_validation` is **absent** from `.planning/config.json` → treat as **enabled**.

### Test Framework

| Property | Value |
|---|---|
| Framework | pytest (both sub-repos + the meta `.planning/` checkers); PlatformIO Unity for `pio test -e native` |
| Config files | `firestarter_app/pyproject.toml`; `firestarter/platformio.ini` (`[env:native]`, `[env:native_nodevtools]`); **none** for `.planning/phases/**` checkers (no `conftest.py`, no `pytest.ini` — verified) |
| Quick run — claim gate | `cd .planning/phases/123-non-regression-baselines-gate-hardening && python3 -m pytest test_check_permitted_claims.py -q` (~0.3 s) |
| Quick run — sync gate | `cd firestarter && FIRESTARTER_META_ROOT=/workspaces python3 -m pytest tests/test_flash_path_record_sync.py -q` (~0.6 s, 41 legs) |
| Quick run — decision parse | `node -e '…require(".claude/gsd-core/bin/lib/decisions.cjs").extractDecisions(<130-CONTEXT.md>)'` — assert `outcome !== "could-not-parse"` and 16 ids |
| Full suite — firmware | `cd firestarter && python3 -m pytest tests/ -q` (221 passed, ~7 s) + `pio test -e native` |
| Full suite — app | `cd firestarter_app && python3 -m pytest tests/ -q` (1303 passed, ~116 s) |
| Phase gate | all of the above green **before** the `130-DECISION.md` commit, and re-run on the exact tree that gets merged (constraint 9) |

### Phase Requirements → Test Map

| Req | Behavior | Test type | Automated command | Exists? |
|---|---|---|---|---|
| CLOSE-01 | Every R-N superseded figure is corrected or provably inside a labeled correction/history block | unit (new checker) | `python3 .planning/phases/130-…/check_record_corrections.py` | ❌ Wave 0 (D-08) |
| CLOSE-01 | The checker fails on a planted stale figure **and** on a mislabeled block | unit (new fixtures) | `python3 -m pytest .planning/phases/130-…/test_check_record_corrections.py -q` | ❌ Wave 0 (D-08, BASE-08) |
| CLOSE-01 | The checker is not defeated by criterion 1's own needle quote or by v1.22-archive history | unit | same suite, two dedicated legs | ❌ Wave 0 (**C-7, C-8**) |
| CLOSE-02 | All four contracted artifacts exist and carry the required caveat with zero forbidden matches | unit (existing, **broken**) | `cd .planning/phases/123-… && python3 check_permitted_claims.py` | ⚠️ exists but points at the wrong directory — **C-2** |
| CLOSE-02 | D-15 arming fails on three-of-four | unit (existing, **RED**) | `python3 -m pytest test_check_permitted_claims.py -q` | ⚠️ **1 failed / 9 passed — C-3** |
| CLOSE-02 | `[SHARED:S4]` stays identical across both copies after D-11's body edit | integration (existing) | `FIRESTARTER_META_ROOT=/workspaces python3 -m pytest tests/test_flash_path_record_sync.py -q` | ✅ 41/41 green |
| CLOSE-03 | v1.24–v1.27 byte-unchanged | one-shot, deliberately **not** a checker (D-16) | `sha256sum` of each of lines 29–32 before/after + `git diff -U0 -- .planning/ROADMAP.md`, recorded in `130-NONREGRESSION.md` | ❌ Wave N (procedure, not code) |
| CLOSE-03 | The renumber landed and no `v1.23 Binary Command Protocol` remains in the list | grep assertion in a plan | `grep -n 'v1.2[3-8]' .planning/ROADMAP.md \| sed -n '1,12p'` | ❌ Wave N |
| CLOSE-04 | `130-DECISION.md` committed **before** any push | structural (plan ownership) | `git log --oneline -- .planning/phases/130-…/130-DECISION.md` predates both `origin/beta` moves | ❌ Wave N |
| CLOSE-04 | Observed cut tag read, never computed | procedure | `gh release list --repo henols/firestarter --limit 3` and `… firestarter_app …` | ✅ command verified read-only this session |
| CLOSE-04 | `firestarter_py32f071.hex` present in the **real** b15 assets (D-03) | procedure | `gh release view <observed> --repo henols/firestarter --json assets` | ✅ command verified (b14 → 3 AVR hexes, no py32) |
| CLOSE-04 | PyPI resolution verified directly from a clean temp env | procedure | `python3 -m venv /tmp/v && /tmp/v/bin/pip download --no-deps --pre firestarter==<observed> -d /tmp/d` | ❌ Wave N |
| CLOSE-04 | Both AVR + py32 asset sets and PyPI verified before claiming completion | procedure | committed transcript (`115-VALIDATION.md` / `122-CHANNELS.md` shape) | ❌ Wave N |

### Sampling Rate

- **Per task commit:** the relevant quick run — claim-gate suite for CLOSE-02 tasks, sync gate for
  D-11 tasks, decision parse for the C-1 fix, the new CLOSE-01 checker for R-N tasks.
- **Per wave merge:** `firestarter` `pytest tests/` + `pio test -e native`; `firestarter_app`
  `pytest tests/`; both `.planning/` checker suites.
- **Phase gate:** every suite green **on the exact tree that gets merged**, captured in
  `130-NONREGRESSION.md`, **before** `130-DECISION.md` is committed and therefore before any push.

### Wave 0 Gaps

- [ ] **Rewrap the nine malformed `D-NN` labels in `130-CONTEXT.md`** and re-run the parser — covers
      C-1. Blocks plan-phase's §13a gate.
- [ ] **Repoint `_DEFAULT_TARGETS`** in `.planning/phases/123-…/check_permitted_claims.py` at the
      Phase 130 directory, in the same commit that writes the artifacts — covers C-2. Update the
      docstring's four resolved paths.
- [ ] **Narrow `test_check_permitted_claims.py:301-304`'s side-effect glob** from `130-*.md` to the
      four contracted names, with a RED-preserving proof — covers C-3.
- [ ] **New `check_record_corrections.py` + `test_…` + `fixtures/`** with the phrase table, the
      label-awareness (correction **and** history blocks), the self-reference exemption, and both
      planted-violation fixtures — D-08 / BASE-08.
- [ ] Framework install: **none needed** — pytest, node and `gh` are all present and working.

---

## Security Domain

`security_enforcement` is absent from `.planning/config.json` → enabled.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard control |
|---|---|---|
| V2 Authentication | no | no auth surface; `gh` uses an existing OAuth token (scopes `gist, read:org, repo, workflow`) |
| V3 Session Management | no | — |
| V4 Access Control | **yes** | The push, the CI dispatch and the release-body post are the privileged acts. They are gated **structurally** — by which plan owns which command — not by a checkpoint type, because `--auto`/`--chain` auto-approves human-verify gates and `autonomous: false` does not protect an outward-facing gate |
| V5 Input Validation | **yes** | `beta-build.yml`'s `rehearsal` is a **typed boolean** specifically so a string could not reach `draft:`/`tag_name:` (recorded in-file, Security V5). `BETA_VERSION_RE` validates any explicit version. `publish.yml`'s `tag` input flows into `ref:` — an untrusted value there is a checkout-of-arbitrary-ref vector, so the dispatch must carry the **observed** tag read from `gh release list` |
| V6 Cryptography | no | nothing hand-rolled; `PYPI_API_TOKEN` and `PERSONAL_ACCESS_TOKEN` are repo secrets |
| V14 Configuration | **yes** | `paths-ignore` (C-14) and `continue-on-error` (D-03) are both configuration that can silently reduce what gets published or verified |

### Known Threat Patterns for this phase

| Pattern | STRIDE | Mitigation |
|---|---|---|
| Publishing a firmware image presenting another company's registered USB vendor identity | **Spoofing** | D-11 replaces `36B7:FFFF` with pid.codes `1209:0001` before the cut; the release body states it; the ship gate stands (see **C-5** for the wording tension) |
| A green CI tick read as evidence the py32 asset shipped | Repudiation / false assurance | D-03 asserts asset presence from `gh release view` on the **real** b15, never from the run's conclusion — `continue-on-error: true` makes green and shipped independent |
| A green claim-gate run that scanned nothing | false assurance | **C-2** — the primary security-relevant finding of this research |
| PyPI resolution inferred from a green tick | false assurance | Constraint 7: `pip download` from a clean temp env; corroborated by `3.0.0b12`'s absence from PyPI |
| An unvalidated `tag` reaching `publish.yml`'s `ref:` | Tampering | Dispatch only with the tag read from `gh release list`; never a computed literal |
| A stray or premature prerelease from an accidental push | Tampering / availability | `130-DECISION.md` before any push (constraint 1); v1.21's close skipped it and auto-cut a stray b12 which is still public |

---

## Sources

### Primary (HIGH confidence — read or executed in the live trees, 2026-08-02)

- `.planning/phases/130-…/130-CONTEXT.md` — full read; decision block executed against the parser
- `.planning/phases/123-…/check_permitted_claims.py` (332 lines, full read + executed) and
  `test_check_permitted_claims.py` (349 lines, full read + executed)
- `.planning/phases/122-…/check_permitted_claims.py` (`_DEFAULT_TARGETS` idiom), `122-LEDGER.md` +
  `122-DECISION.md` heading structures, full 122 artifact inventory
- `.claude/gsd-core/bin/lib/decisions.cjs` — the three bullet grammars + parse-miss guard, executed
- `.planning/research/SUMMARY.md` §"Corrections to the Planning Record" (`:183-202`), §A-5
  (`:146-160`), §"What Cannot Be Validated" (`:223-243`), phase-130 spine entry (`:300-302`),
  Research Flags (`:316-330`)
- `.planning/REQUIREMENTS.md` (full), `.planning/ROADMAP.md` (Milestones `:5-35`, backlog
  `:1723-1890`, Phase 130 detail `:2461-2480`), `.planning/PROJECT.md`, `.planning/STATE.md`,
  `.planning/notes/py32f071-port-branch-state.md` (full),
  `.planning/todos/pending/correct-v128-py32-roadmap-prior-art.md` (full)
- `.planning/v1.23-FLASH-PATH-DECISION.md` §2, §5(a)–(e), line 28
- `firestarter/platform/py32f071/src/usb_cdc.c`,
  `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md:106`,
  `firestarter/tests/test_flash_path_record_sync.py` (helpers, needles, all 41 legs; executed)
- `firestarter/.github/workflows/beta-build.yml`, `py32f071.yml`, `.github/scripts/update_version.py`
- `firestarter_app/.github/workflows/beta-release.yml`, `publish.yml`
- `.planning/phases/124-…/124-NONREGRESSION.md` (A-5 second-source), `128-NONREGRESSION.md` (cited)
- `CLAUDE.md` (meta), `firestarter/CLAUDE.md`, `firestarter_app/CLAUDE.md`
- Live commands: `git rev-parse` / `rev-list` / `ls-tree` / `status` / `tag --list` / `diff
  --name-only` in all three repos; `gh auth status`; `gh release list` + `gh release view` in both
  repos; `gh run view` ×2; `gh issue list`; PyPI JSON API for `firestarter`; `pytest` ×5

### Secondary (MEDIUM confidence)

- pid.codes' `1209:0001` terms — quoted verbatim inside `.planning/v1.23-FLASH-PATH-DECISION.md:198`
  rather than fetched from the registry this session. The SHOULD/MUST distinction in **C-6** rests on
  that transcription; if the exact wording becomes load-bearing in an outward-facing body, re-fetch
  it. `[CITED: v1.23-FLASH-PATH-DECISION.md:198]`
- Puya vendor-id attribution for `0x36B7` — `[CITED: the-sz.com USB ID database, single-source, per
  the record's own tag]`

### Tertiary (LOW confidence)

- None relied upon.

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | The b15 auto-increment target is `3.0.0b15` in both repos | C-15 | Low — derived from read code plus verified tag lists, and constraint 5 makes the observed tag authoritative regardless |
| A2 | The app CI suite will be green on py3.11 as it is on py3.12 | C-13 | **Medium** — a py-version-specific RED would block the app cut *after* the firmware half published. Mitigate by recording the pre-flight run in `130-DECISION.md` and, if cheap, running the suite under 3.11 |
| A3 | Publishing a `.hex` release asset carrying `1209:0001` does not violate pid.codes' *"MUST NOT be used on any device that will be redistributed"* clause, because no device is redistributed | C-5 | **Medium** — a judgment call on registry terms. Operator-resolvable; record the reasoning in `130-DECISION.md` rather than leaving it implicit |
| A4 | `.planning/` checker suites are not run by any CI in any of the three repos | C-3 | Low — meta has only `catalog-sync-check.yml`; the sub-repo workflows were read and reference no `.planning/` path |
| A5 | Option (a) in C-2 (repointing `_DEFAULT_TARGETS`) is within the docstring's sanctioned amendment | C-2 | Low — the docstring says *"amend this list in the same commit that renames or adds one"*; a relocation is a rename of the path. Worth one line in `130-NONREGRESSION.md` recording the reading |

## Open Questions

1. **Does the operator accept §5(c)'s ship gate being amended, or must the release body's phrasing
   thread it instead?** (C-5)
   - Known: `1209:0001` is not an allocated PID; §5(c) forbids a release advertising a USB identity
     until one exists; §5(c) says explicitly it is a condition a future reader can fail.
   - Unclear: whether the operator reads a caveated disclosure as "advertising".
   - Recommendation: **escalate during planning**, as C-1/C-2 were in Phase 129. If amended, budget
     three edit sites (both record copies + `_L2_SHIP_GATE`). If not, the release body must disclose
     the interim id **as a non-claim** and `130-DECISION.md` must record why that is not advertising.

2. **Are the dated review-history paragraphs (`ROADMAP.md:1747`, `:1877`, `:1879`, `:1883`,
   `:1887`) history-exempt?**
   - Known: criterion 1's own escape clause says *"outside a labeled correction/**history** block"*;
     these are dated, signed review notes and `:1883` carries the stale prior-art plus the
     `→ v1.28` pointers.
   - Recommendation: treat them as history-exempt and record that ruling in `130-NONREGRESSION.md`,
     because rewriting a dated review record is the same error D-05 avoids for the branch-state note.
     But `:1883`'s *"scope v1.28 from that document"* is an **instruction**, not a record — consider
     one inline supersession note there specifically.

3. **Does D-15's 999.25 half have any subject?** (CLOSE-03 section)
   - Known: the phrase *"the v1.29 slot immediately above"* occurs exactly once, at `:35`. 999.25's
     stub carries only `→ v1.30, NEXT after v1.23`, which stays true.
   - Recommendation: verify before planning an edit; if it is a no-op, record it as such rather than
     inventing one.

4. **Where does A-5's operator-visible flash-constraint decision get recorded?** (C-17)
   - Known: assigned to Phase 130 by the research spine; already discharged at Phase 124 with an
     independent 328PB build.
   - Recommendation: one row in `130-LEDGER.md` (evidence tier: AVR-measured) plus one line in
     `130-NONREGRESSION.md` citing `124-NONREGRESSION.md` §F4d. No fresh work.

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| `git` | every phase step | ✓ | — | none needed |
| `gh` | observed tag, asset assertion, run evidence | ✓ | authed as `henols`, scopes `gist, read:org, repo, workflow` | none |
| `python3` + `pytest` | all checker and suite runs | ✓ | 3.12.13 (CI: 3.9/3.11) | run under 3.11 if a version-specific RED appears |
| `node` | the decision-parser check (C-1) | ✓ | via `.claude/gsd-core/bin/` | manual regex inspection |
| `pio` | `pio test -e native` (firmware pre-cut gate) | ✓ | `/usr/local/bin/pio` | CI runs it regardless |
| `pip` + `venv` | clean-env PyPI resolution check (constraint 7) | ✓ | — | none |
| `arm-none-eabi-gcc` / `cmake` / `ninja` | a local ARM pass for D-11 | **✗ not installed** | — | **Installable** (Phase 129 C-3 built 41/41 objects with it, needing two newlib packages CI omits). Per D-07, a local build supports **delta/byte-identity claims only** — never an absolute size, which needs a CI run URL + SHA. The ARM pass before the merge can also be satisfied by `py32f071.yml`'s loud gate on a pushed branch, but **no task may run `gh workflow run` or `git push`** |
| PY32F071 PCB | nothing | **✗ does not exist** | — | none, by design — this is the milestone's ceiling |

**Missing with no fallback:** none blocking.
**Missing with fallback:** the ARM toolchain — install locally for a delta/byte-identity proof of
D-11's edit, or rely on the loud CI gate after the (operator-run) push. Note the ordering constraint:
constraint 2 wants an ARM pass **before** the outbound merge, which means the local install is the
only agent-reachable route.

## Metadata

**Confidence breakdown:**

- Live state re-verification: **HIGH** — every figure measured this session with the command shown.
- Tooling defects (C-1, C-2, C-3): **HIGH** — all three reproduced by execution, not by reading.
- `[SHARED:S4]` / D-11 footprint (C-4): **HIGH** — read from source and the 41-leg gate executed.
- Ship-gate tension (C-5): **HIGH** on the facts, **judgment** on the resolution — operator-gated.
- R-N work list: **HIGH** — per-hit greps with snippets and label context for every needle.
- Release mechanics: **HIGH** — read from the workflow files and `update_version.py`, corroborated by
  two still-readable runs and the live release/PyPI surfaces.
- pid.codes terms wording (C-6): **MEDIUM** — transcribed from the record, not re-fetched.

**Research date:** 2026-08-02
**Valid until:** ~7 days for the live-state table (branch tips and tag ceilings move the moment
anyone pushes); ~30 days for the tooling and mechanics findings. **Re-verify the live-state table
immediately before the merge**, per CONTEXT's setup precondition.
