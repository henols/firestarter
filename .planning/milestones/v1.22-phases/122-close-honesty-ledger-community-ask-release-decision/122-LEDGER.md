# v1.22 Honesty Ledger — AT28C Software Data Protection Lifecycle

**Milestone:** v1.22 — AT28C Software Data Protection Lifecycle
**Firmware inbound-merge commit:** `953f74842ee0bcc89923a306d5bd79ef3ad19f92` (merge; parents `48c36e569c8ddfd3daa8aea7e55c5bbc79b48b08` branch HEAD + `6611fbae18e94abd58f1eea7a96deed533efdb38` `origin/beta`)
**Host inbound-merge commit:** `4001396bbd42d5ba36ce24f40e0315ee6de32d60` (merge; parents `c3c9424f7a299c6ff3498a15620e5235cf72a782` branch HEAD + `1bb55999965a30103f30c506b57032291421dda1` `origin/beta`)
**Published cut tag:** **`3.0.0b14`** — **observed, not predicted.** Read from the actual published releases, not from the auto-increment arithmetic that happened to predict the same value. Evidence: `gh release list --repo henols/firestarter` and `--repo henols/firestarter_app` both list `3.0.0b14` as a prerelease (firmware cut by `beta-build.yml` run `30551682616`, carrying `firestarter_leonardo.hex` / `firestarter_uno.hex` / `firestarter_uno328pb.hex`; app cut by `beta-release.yml` run `30554308461`, carrying zero assets — correct, PyPI is the app's sole channel); PyPI's JSON API lists `3.0.0b14` with both a wheel and an sdist, uploaded `2026-07-30T15:12:52Z` after one explicit manual `gh workflow run publish.yml -f tag=3.0.0b14` dispatch. Full record: `122-CUT.md` (the cut) and `122-CHANNELS.md` (the both-channels-public verification). *Backfilled 2026-07-30 during phase verification — Plan 122-08 was assigned this field but never carried `122-LEDGER.md` in its `files_modified`, so the backfill was structurally impossible from that plan. No claim in this ledger changed; this field records a verified fact that was already independently correct in every public-facing artifact.*
**Version-string caveat:** both merged trees currently report `3.0.0b13` in `firestarter/include/version.h` and `firestarter_app/firestarter/__init__.py`. That string is **not** the identity of what gets published — the two inbound-merge commit SHAs above, plus the observed cut tag once filled in, are the identity. The same discipline `.planning/v1.16/ledger/PROTOCOL-LEDGER.md`'s own caveat line applies: "firmware reports `3.0.0b10`; the actual build is the v1.16 recompose — record the submodule commit, not the version string."
**Oracle:** software-only — native register trace (`pio test -e native`), host pytest (`firestarter_app`), source-scan gates (`tools/check_*.py`), plus three-board host-side timing measurements (Leonardo, Uno, uno328pb). No AT28C silicon was tested during this milestone.
**Generated:** 2026-07-30

**Composes with (cross-reference only — no data copied):**
- `.planning/REQUIREMENTS.md` §"Validation Ceiling" — the permitted claim and forbidden claim this ledger distils into claim classes
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-NONREGRESSION.md` — the merged-tree gate results every CLOSE-01 figure below cross-references
- `.planning/phases/119-lock-sdp-enable-command-surface-fw-half/119-MEASUREMENT.md` — the flash-vs-timing budget distinction and the two named kinds of page-load number
- `.planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-SDP-PARTITION.md` — the derived-partition provenance and its ground-truth probes
- `.planning/v1.16/ledger/PROTOCOL-LEDGER.md` — the `0x0D` row's status, structural analog for this document's shape

**`PROTOCOL-LEDGER.{md,json}` is referenced and verified here, never edited (D-09).** CLOSE-01 asks that the `0x0D` row *stays* `UNVERIFIED` — a check, not a write; `git -C /workspaces status --porcelain -- .planning/v1.16/ledger/` is asserted empty at every task boundary in this plan. Its own header pins firmware commit `a296195`, which is an ancestor of **neither** `origin/beta` nor this milestone's live line — a stale pin that is precisely why editing that file, rather than writing this new one, was refused.

---

## The ceiling, quoted verbatim

Attributed to `.planning/REQUIREMENTS.md` §"Validation Ceiling", reproduced here so no downstream artifact (the two prerelease bodies, the two community-comment drafts) has to re-derive it:

> **Permitted claim at close:** *"The SDP lock and unlock sequences are emitted exactly as specified, verified byte-exact by golden register trace across all four `0x0D` pinouts, with a documented and measured host-side timing assumption."*

> **Forbidden claim:** cited by location rather than reproduced — `.planning/REQUIREMENTS.md:152`. This ledger does not repeat that sentence's exact wording: doing so would trip this same document's own claim scanner (`check_permitted_claims.py`), which matches a phrase's shape regardless of quotation context, by design. That is the gate working as intended, not a defect to route around. The permitted claim above is safe to reproduce because it contains no trigger shape.

**No AT28C silicon was tested during this milestone.** Every figure below has a software artifact as its subject — a golden register trace, a `pio run` size report, a pytest exit code, a source-scan result, a derived-partition computation — never a silicon observation.

---

## Status / claim key

- **`PERMITTED`** — a wording backed by a measured, re-runnable software artifact (a trace, a test, a source scan, a size report).
- **`CONTEXT-ONLY`** — measured, and cited for context, but explicitly not a gate — Phase 119 D-16 declined to make it one.
- **`COMMUNITY-CORROBORATED`** — a real-silicon datapoint supplied by a third party, provenance stated plainly, not independently reproducible on this bench.
- **`FORBIDDEN`** — the ceiling's forbidden claim. It appears in this ledger only as a citation of what is *not* claimed, never as prose asserting it.

---

## The nine claim classes

Nine rows, not the "roughly eight" D-11 named. D-11's eight classes split the single "measured host-side timing" class into two distinct measurements with different sources and different dispositions — the SDP unlock **emitter's** duration (a gating, budgeted figure) and the **page-load** per-byte interval (context only, never a gate, per Phase 119 D-16). Recording the split here rather than silently: `119-MEASUREMENT.md` §1/§4 is the source that separates these two kinds of number, and conflating them was a documentation error PROJECT.md itself once made and later corrected.

| Class | Permitted wording | Evidence (measured, with source) | Explicitly does NOT prove |
|---|---|---|---|
| **1. Per-pinout emission byte-exactness** `PERMITTED` | The SDP lock and unlock sequences are emitted exactly as specified, verified byte-exact by golden register trace across all four `0x0D` pinouts. | Phase 116 trace harness + Phase 119 golden traces (`test_eeprom28c_sdp.cpp`); re-confirmed green on the merged tree by `122-NONREGRESSION.md` §3 rows 1–4. Coverage figure: **66 of 84** chips individually trace-covered — not the full 84-chip bucket, and never rounded up. | That any silicon accepted the sequence, entered or left the protected state, or that the magic addresses are correct for every family member — **SDP-F7** leaves them `UNVERIFIED` for AT28C040 / AT28C16 / AT28C04. |
| **2. Measured host-side timing — the SDP unlock emitter** `PERMITTED` | The emitted sequence's host-side duration is measured, per board, against a documented budget of 600 µs (`6 × AT28C_TBLC_MAX_US`) — Leonardo **568 µs**, Uno **412 µs**, uno328pb **424 µs**. | `OBS-04` (Phase 118); `119-MEASUREMENT.md`. F-118-01 separately measured **572 µs** on a Leonardo as a second observation of the same emitter and board class — cited here, never averaged with the 568 µs figure. | That `t_BLC` is met **as accepted by the die** — no AT28C part measured this on real hardware. |
| **3. Page-load per-byte interval — context, not a gate** `CONTEXT-ONLY` | The worst per-byte page-load interval is measured — Uno **84 µs**, Leonardo **88 µs** — against the 100 µs datasheet maximum. | `119-MEASUREMENT.md` §1/§4. Phase 119 D-16 explicitly declined a runtime budget check on this path; these numbers are recorded for context, never enforced. | Any silicon-side timing conformance. The Leonardo figure is **not** directly comparable to the Uno-class figures — its measurement folds in a page-boundary crossing the Uno-class figures do not carry, per `119-MEASUREMENT.md`'s naming of the two kinds of number. Never compare them as if they measured the same thing. |
| **4. `0x0D`-scoped fail-closed refusal** `PERMITTED` | Lock and unlock are fail-closed for any `protocol != 0x0D`, machine-checked. | `test_configure_memory.cpp` case groups 1/2 (Phase 119). Mechanism correction (LOCK-04): shipped as **one generic op-layer NULL-`main` refusal** in `operation_utils.cpp`, **not** the requirement's literal `default:` arm in `configure_eeprom28c` — that arm would have refused read and verify on every one of the 84 `0x0D` chips. | Anything about behaviour on a real `0x0D` part. |
| **5. `DEV_TOOLS` invariance of the admission guard** `PERMITTED` | The explicit `is_memory_cmd()` predicate is proven identical with and without `-D DEV_TOOLS`, by a two-env truth table over all 256 `cmd` values plus a brace-matched source-scan gate with a planted-violation fixture. | Plan 119-02/119-03 (`LOCK-03`). | Anything about SDP itself — this is a prerequisite invariant, not an SDP claim. |
| **6. Other protocol families byte-identical** `PERMITTED` | The `0x05`/`0x06`/`0x07`/`0x10`/SRAM golden traces are byte-identical, and `flash_utils.{h,cpp}`, `flash_5v_page.cpp` and `flash_nor_unlock.cpp` are byte-untouched. | `FIX-04` (Phase 117); re-confirmed on the merged tree, `122-NONREGRESSION.md` §5's clean codegen-drift and native-suite rows. | That the `0x0D` change itself is correct — only that it is contained and did not disturb the settled families. |
| **7. The host refuses before the wire** `PERMITTED` | A pre-wire capability refusal keeps SDP commands away from `0x0D` parts with no SDP command decoder, as a **fail-closed allow-list** derived from minipro `infoic.xml` `INFOIC2PLUS` `flags` bit 15 — **43 ALLOW / 41 REFUSE** across the 84 chips, with zero `chip_database.json` change. | `HOST-04` (Phase 120); `120-SDP-PARTITION.md`; re-derived on the merged tree, `122-NONREGRESSION.md` §2. | That the partition is correct per family — the ceiling names this explicitly as not provable without parts — nor that any refused part is actually SDP-incapable in silicon. `120-WATCHLIST.md` names **nine** residual-risk entries where a wrong bit-15 value would cost a real regression; none has been bench-contradicted. **SDP-F8** additionally flags `DIP24_2816`'s missing `static-high-pins` as a separate open question the partition does not resolve. |
| **8. The defect is community-corroborated; the fix is not** `COMMUNITY-CORROBORATED` | On 2026-07-27 a community reporter (`datapaganism`) running `3.0.0b11` on a real AT28C256 reproduced the exact inverted-check INIT abort this milestone predicted in software — raising Phase 116's `TRACE-06` from software-predicted to community-corroborated. | `116-PREMISE.md` (the software prediction); gh#11 comment thread, 2026-07-27 (`ERROR: EEPROM timeout at 0x005555: wrote 0x20 got 0xff`). Provenance stated plainly: an issue-comment paste, no captured logs beyond the text, board revision and firmware build unconfirmed. | That the **fix** is silicon-effective. `0x0D` stays `UNVERIFIED`; zero chips changed `support_status`. This asymmetry — premise corroborated, fix unproven — is the sharpest honesty statement in this close and is stated in exactly those terms, never softened into "confirmed" or any wording implying the fix has been checked the same way. |
| **9. Flash budget (a separate row from timing, deliberately)** `PERMITTED` | The Leonardo flash delta is reported and fits — final Leonardo `26072/28672` = **2600 B free**, judged against the live phase-base headroom of **2992 B**, with `-D DEV_TOOLS` (the tighter, binding configuration) costing **1292 B**. Uno `23932/32256`, uno328pb `23976/32384`, compared by **delta only** because their capacities differ by bootloader reservation. | `LOCK-06` (Phase 119); re-confirmed on the merged tree, `122-NONREGRESSION.md` §5. `LOCK-06`'s originally-cited `3348 B` headroom figure is **superseded** — it predates Phase 117's `+204 B` and Phase 118's `+152 B`, already spent by the time this milestone closed. | Any timing property. `119-MEASUREMENT.md:33-34` records that `LOCK-06` is a **flash** budget and F-118-01 is a **timing** budget — two different budgets that a prior `PROJECT.md` directive once conflated. Rows 2/3 and this row are never merged into one claim. |

---

## The four `0x0D` pinouts — composition, and why "all four pinouts" needs a qualifier

Measured composition, re-derived on the merged tree by `122-NONREGRESSION.md` §2:

| Pinout | Chips | SDP ALLOW | SDP REFUSE |
|---|---:|---:|---:|
| `DIP28_28C64` | 35 | 15 | 20 |
| `DIP24_2816` | 19 | **0** | **19** |
| `DIP32_28C512_EEPROM` | 18 | 18 | 0 |
| `DIP28_28C256` | 12 | 10 | 2 |
| **Total** | **84** | **43** | **41** |

**Emission traced byte-exact for a pinout** and **the operation permitted on parts with that pinout** are **different claims**. Class 1 above proves the first for all four pinouts; the ALLOW/REFUSE column proves the second is false for every single chip on `DIP24_2816`. A ledger row — or a release body, or a public comment — that says "all four `0x0D` pinouts" without carrying this qualifier reads as broader capability than shipped, even though the trace-coverage sentence alone is true.

`DIP24_2816`'s full refusal is *correct*, not a gap, for two reasons. First, on a part with no SDP command decoder the sequence is not inert: after Phase 117's emitter fix, the command writes reach silicon, so `0xAA`/`0x55`/`0xA0` would land **as data** at bus-truncated magic addresses rather than doing nothing. Second, **SDP-F7** (magic addresses unverified for AT28C16 / AT28C04) and **SDP-F8** (`DIP24_2816` carries no `static-high-pins`) both name this exact family. The honest nuance SDP-F8 needs stated plainly: the 28- and 32-pin `0x0D` pinouts also carry no `static-high-pins` — the asymmetry is specific to **24-pin** pinouts sharing that socket position, which is why SDP-F8 says to confirm against the shield schematic before acting on it.

Derived provenance, precisely: minipro `infoic.xml`, `<database type="INFOIC2PLUS">`, `flags` bit 15 (`0x8000`, `MP_PROTECT_AFTER`), at minipro commit `a8efaedc236c1d9718bd28299dfbb99536b010ff`, the full 84-entry `0x0D` set matched (84 of 84), zero unmatched, zero `MIXED`. This supersedes Phase 120 RESEARCH's earlier curated `37/47` and the interim `~74/10` placeholder. That derivation makes the partition **reproducible** — anyone can re-run the join and get the same 43/41 split — not **bench-verified**; no AT28C silicon was tested to confirm any individual entry's placement.

---

## Mechanism corrections recorded here, not in `REQUIREMENTS.md`

`REQUIREMENTS.md`'s wording is deliberately not edited for any of the five corrections below — the same discipline already applied at `LOCK-04`, `LOCK-06`, `HOST-04`, and Phase 121's D-06/D-17: when a requirement's stated mechanism turns out narrower or different, the intent is satisfied, the correction is recorded in the phase record, and the requirement text is left alone.

1. **`check_ledger.py`'s pre-existing RED (C-4).** That tool exits 1 today with two `LEDGER-01` violations, because `PROTOCOL-LEDGER.json` rows `0x05`/`0x06` carry `matrix_family` values `flash4`/`flash3`, and v1.19 Phase 104 renamed those families to `5v_page`/`nor_unlock`. `tools/validation_matrix_spec.json` is not in the `beta...HEAD` diff, so this is pre-existing and not v1.22's damage. `CLOSE-01`'s text does not mention this tool; it was **not** run as a gate and was **not** fixed, because fixing it would edit a closed milestone's artifact (D-09). The `0x0D` row's own join key (`eeprom28c`, `protocols: [13]`) is present and valid — only `0x05`/`0x06` are stale. A backlog seed is the recommended disposition.

2. **D-06's stated conflict set (C-1/C-2).** The firmware inbound merge had **zero** conflicts, not the three-file conflict CONTEXT.md's D-06 implied. The app conflicted in exactly two files, `firestarter/submit.py` and `tests/test_submit.py`. `firestarter/include/version.h` (firmware) and `firestarter/__init__.py` (app) both **auto-merged** and were never conflicts. The resolution used was whole-file `--ours`, justified by a mechanical superset proof (all 60 of `beta`'s test functions exist among branch HEAD's 77, `comm -23` empty) and proven by an empty diff — hunk-level resolution was forbidden because hunks 3 and 4 sandwich a shared region branch HEAD needs twice, and a textual "ours" there produces code that compiles and passes while silently rebinding an `elif` to the wrong `if` (C-11/C-12).

3. **D-14's `No-Hazmats` answer — a flagged, locked-decision divergence (C-5).** CONTEXT.md's D-14 (`122-CONTEXT.md:185`, not reproduced verbatim here because its exact wording trips this ledger's own claim scanner — the pattern doing its job, not a defect) prescribed telling that reporter their AT28C parts had become able to do what they wanted. Measured over the full 84-entry `0x0D` set: every 2K×8 part sits on pinout `DIP24_2816`, and all 19 of 19 `DIP24_2816` chips are `REFUSE`d by the SDP allow-set (7 as `pre-SDP generation`, 12 as `unrecognised`). The corrected answer, owned by Plan 122-10, is phrased **by size class, not by an assumed part number**. **This is flagged as an explicit divergence from a locked decision, not a silent fix.** Plan 122-11's operator wording review is the place this divergence is put to the operator as an explicit accept-or-overturn; if overturned, the overturn must propagate back to this row — this ledger, not the comment draft, is the traceable record of what the locked decision said versus what research measured.

4. **Release mechanics (C-6/C-7).** Both prior release bodies (`3.0.0b13`, both repos) are **empty strings**, not auto-generated commit lists — so writing a body is an *add* via `gh release edit --notes-file`, never a careful overwrite. Only the **firmware** release carries assets (three `.hex` files, one per board); the app GitHub release carries zero assets, and PyPI is the app's sole distribution channel.

5. **`diff_db.py`'s self-interpreted result (C-13).** The tool interprets its own result and exits 0 on the two explained changes. "Identity" here means *still exactly 2 explained `PGSZ_PAGE_SIZE` changes, 0 new, 0 removed* — not a literal zero diff. Reading a two-change result as a failure would itself be a documentation error.

---

## What this milestone chose not to prove

A close that lists only wins reads as overclaiming even when every individual claim is true. This section is the negative space.

### Deferred by decision or on research grounds — SDP-F1 through SDP-F8

- **SDP-F1** — `--sdp-relock`, deselected for v1.22. If it returns, it needs a stated constraint: an unconditional step in a conditional pipeline is the Phase-112 `if destructive:` lesson repeating, and a re-lock after a failed verify would strand the user with a locked chip they cannot retry on.
- **SDP-F2** — the full three-field SDP report shape. Deselected; `HOST-05`'s minimal honesty floor is retained instead.
- **SDP-F3** — a `dev test` SDP step. Perturbs `dedup_fingerprint` across the full 84-chip `0x0D` bucket and triples the blast radius of a milestone with no silicon on the bench.
- **SDP-F4** — write-probe SDP inference. The only real state observation available, but destructive, and an honest-labelling design problem.
- **SDP-F5** — the datasheet 6-byte software chip-erase. A real gap, but an *erase* feature riding an *SDP* milestone, and it needs `OE = V_H = 12 V` — the T-93-CANERASE hazard class.
- **SDP-F6** — SDP handling for the AT29C / SST39SF / W29EE families. Multiplies the no-silicon problem across otherwise-settled bench evidence.
- **SDP-F7** — datasheet verification of the SDP magic addresses for AT28C040 / AT28C16 / AT28C04. Recorded `UNVERIFIED` rather than assumed correct.
- **SDP-F8** — `DIP24_2816`'s missing `static-high-pins` (19 chips with `static_high_mask == 0`). The remap fix does not address it; confirm against the shield schematic before acting.

### Two trade-offs Phase 121 recorded and owned

- An off-TTY `dev test` writes silicon with nobody consenting — stated plainly as an accepted consequence of the zero-option redesign (`DEVTEST-02`), not as a defect discovered here.
- `doc/lockable-proms.md` ships roughly 300 datasheet-compiled rows with **no provenance header**, deliberately, as an owned trade-off (`GATE-02`) that is explicitly not to be re-opened.

### One trade-off this phase itself owns

- **D-01 declined a bench smoke-test of the b14 install/flash path.** The `pip install --pre` → `fw -i` → one-live-op chain that Phase 115 existed to prove is trusted rather than re-verified before either community reporter is pointed at b14. Named here as a known, accepted gap — if a b14 install problem surfaces, this record shows it was known and accepted, not an oversight.

---

## What no test, gate or review in this phase can close

Reproducing `122-VALIDATION.md`'s three-way split in this ledger's own voice, because auditability of exactly this split is the whole point of writing this document.

- **Mechanically checkable.** Every `CLOSE-01` sub-claim, every `CLOSE-03` sub-claim, and `CLOSE-02`'s *delivery* facts (posted, still open, byte-equal to the reviewed draft). Cheap, deterministic, re-runnable — the eleven-row cross-repo gate, the four `CLOSE-01` mechanisms, both full suites, the claim scanner below.
- **Requires the blocking operator review (D-16).** Whether the prose is *honest*, not merely free of banned strings. A string scan cannot detect an implied overclaim, cannot judge whether omitting the `DIP24_2816` refusal misleads a reader, and cannot weigh tone. **A green claim-scan does NOT satisfy ROADMAP criterion 4** — criterion 4 closes only with this gate **plus** the D-16 review in Plan 122-11.
- **Inherently unverifiable in-phase, at a sampling rate of zero, by design.** That silicon enters or leaves the protected state; that `tBLC` is met as accepted by the die; that gh#11's symptom is gone on real hardware; that the capability partition is correct per family. `0x0D` stays `UNVERIFIED` precisely because these are open, permanently, until an AT28C part is on the bench. The one asymmetry stated precisely (class 8 above): the **defect** is community-corroborated on real AT28C256 silicon; the **fix** is not. That is the most easily-overclaimed sentence in this phase, and it is deliberately narrow.

---

## Scanner status

This document is one of `check_permitted_claims.py`'s five default outward-facing targets. It is required to exit 0 against this file, carrying the required silicon caveat above and containing zero forbidden-phrase matches, before this file is committed. **A green result from that scanner is the mechanizable half of ROADMAP criterion 4 only** — per the scanner's own module docstring and the split stated in the section immediately above. It does not by itself close `CLOSE-02`'s honesty requirement; the D-16 blocking operator wording review in Plan 122-11 does that.

---

*Phase: 122-close-honesty-ledger-community-ask-release-decision*
*Written: 2026-07-30 (Plan 122-05)*
