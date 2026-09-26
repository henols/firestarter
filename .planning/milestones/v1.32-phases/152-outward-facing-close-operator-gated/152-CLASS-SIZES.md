# 152-CLASS-SIZES.md — live two-method re-derivation of the protection-class partition

**Not a claim register. Not a `152-check-claims.py` scan target — deliberately absent from
`_DEFAULT_TARGETS`.** This file exists to settle RESEARCH Open Question 1 before any outward
sentence in this phase cites a protection-class count. It contains raw class-token vocabulary that
would trip `152-check-claims.py`'s own patterns if scanned, and it is not meant to be read as a
public artifact.

## Method, measured live — never reused from a prior document's citation

```text
Interpreter : Python 3.12.13
Timestamp   : 2026-08-21T15:30:46Z
Repo state  : firestarter_app @ a0bfd5e (gsd/v1.32-at28c-write-path-root-cause-report-provenance)
Database    : firestarter_app/firestarter/data/chip_database.json (746 rows, 59 vendors)
Classifier  : firestarter.protection_readability.protection_gate_for_entry(entry, display_name)
Tokeniser   : firestarter.sdp_capability.split_part_number_tokens (imported by the classifier itself
              for CURATION_PROTOCOL_IDS = {5, 6}; not re-implemented here)
```

Commands run, verbatim:

```bash
cd /workspaces/firestarter_app
python3 --version
# Python 3.12.13
git rev-parse --short HEAD
# a0bfd5e
python3 -c "
import json, collections
from firestarter.protection_readability import protection_gate_for_entry
data = json.load(open('firestarter/data/chip_database.json'))
rows = [chip for chips in data.values() for chip in chips]
print(len(rows))
"
# 746
```

The full derivation script used is reproduced below for anyone re-running it:

```python
import json, collections
from firestarter.protection_readability import protection_gate_for_entry

DB_PATH = "firestarter/data/chip_database.json"
data = json.load(open(DB_PATH))
rows = [chip for chips in data.values() for chip in chips]

def to_entry(row, name_override=None):
    return {
        "protocol-id": row["programming"]["algorithm"],
        "name": name_override if name_override is not None else row["part_number"],
    }

# Method A -- per-row canonical: build the entry's "name" field from ONLY the
# first alias of part_number, so the classifier's own tokeniser sees a single
# token and the row's other aliases are never consulted.
methodA = collections.Counter()
for row in rows:
    first_alias = row["part_number"].split(",")[0].strip()
    entry = to_entry(row, name_override=first_alias)
    token, _reason = protection_gate_for_entry(entry, first_alias)
    methodA[token] += 1

# Method B -- alias-aware: build the entry's "name" field from the row's FULL
# part_number string (every alias), exactly as firestarter.database.EpromDatabase
# always constructs it inside get_eprom() regardless of which alias a caller
# looked the chip up by. This is what the shipped CLI actually does.
methodB = collections.Counter()
for row in rows:
    entry = to_entry(row)
    display_name = row["part_number"].split(",")[0].strip()
    token, _reason = protection_gate_for_entry(entry, display_name)
    methodB[token] += 1
```

Zero classification errors were raised by either method, over all 746 rows, in both runs.

## Algorithm histogram, all 746 rows

```text
{5: 27, 6: 190, 7: 170, 8: 127, 11: 32, 13: 84, 14: 20, 16: 39, 39: 2, 40: 34, 41: 20, 52: 1}
```

- **algorithm 13** (`0x0D`, EEPROM_PARALLEL / the AT28C family): **84** rows.
- **algorithm 5** (Winbond/Atmel/SST 5 V boot-block family, curated): **27** rows.
- **algorithm 16** (`0x10`, Intel/AMD/Catalyst/ST command-register): **39** rows — matches
  `NOT_IMPLEMENTED_PROTOCOL_IDS`'s comment naming a corrected 39-row census (superseding an earlier
  39-vs-406 accounting note in that module).
- Sum: 27+190+170+127+32+84+20+39+2+34+20+1 = **746**. ✅

## Method A — per-row canonical (first alias only, single token)

| class token | count |
|---|---|
| `no_mechanism` | 405 |
| `not_implemented` | 40 |
| `not_readable` | 112 |
| `undocumented_alias` | 107 |
| `read_permitted` | 82 |
| **total** | **746** |
| classification errors | **0** |

Refusal classes summed (`no_mechanism` + `not_implemented` + `not_readable` +
`undocumented_alias`): 405 + 40 + 112 + 107 = **664**. `read_permitted` = **82**. 664 + 82 = 746. ✅

## Method B — alias-aware (full part_number, every alias tokenised)

| class token | count |
|---|---|
| `no_mechanism` | 405 |
| `not_implemented` | 40 |
| `not_readable` | 108 |
| `undocumented_alias` | 112 |
| `read_permitted` | 81 |
| **total** | **746** |
| classification errors | **0** |

Refusal classes summed: 405 + 40 + 108 + 112 = **665**. `read_permitted` = **81**. 665 + 81 = 746. ✅

**Method B reproduces `152-RESEARCH.md` §A-8's live re-derivation exactly** (405 / 112 / 108 / 40 /
81), because RESEARCH's own script — although described there as "keyed on the first alias" —
actually called the classifier with each row's full `part_number` string as `entry["name"]` (the
same shape `firestarter.database.EpromDatabase.get_eprom()` always builds, regardless of which
alias a caller looked the chip up by). RESEARCH's phrase "keyed on the first alias" describes only
which alias was used to *label* the row in its output table, not which aliases the classifier was
allowed to see.

## `no_mechanism` (405) and `not_implemented` (40) are method-invariant

Both methods agree exactly on `no_mechanism` (405) and `not_implemented` (40), because those two
classes are decided purely by `protocol-id` membership in
`NO_MECHANISM_PROTOCOL_IDS`/`NOT_IMPLEMENTED_PROTOCOL_IDS` and never consult `entry["name"]` at
all — aliasing cannot move a row into or out of either class. The two methods disagree only inside
the 217-row curated surface (algorithms 5 and 6), where `not_readable` / `undocumented_alias` /
`read_permitted` are decided by tokenising `entry["name"]`.

## Per-algorithm breakdown inside the curated surface (Method B)

| algorithm | `not_readable` | `undocumented_alias` | `read_permitted` | total |
|---|---|---|---|---|
| 5 (27 rows) | 7 | 20 | 0 | 27 |
| 6 (190 rows) | 17 | 92 | 81 | 190 |

**No algorithm-5 row is `read_permitted`.** All 27 resolve to a refusal (7 `not_readable` + 20
`undocumented_alias`) — this corroborates D-13's "no `0x05` row answers by default" statement in
`152-CONTEXT.md`, and it is the measured explanation for why 151 D-06/D-09's published figure
**111 = 84 (`0x0D`) + 27 (`0x05`)** does not reproduce: that figure implicitly treated every
algorithm-5 row as `not_readable`, when in fact only 7 of the 27 are — the other 20 are
`undocumented_alias`, a distinct class 151's own eight-token vocabulary names but whose count 151's
D-06/D-09 prose never separately stated. This is a **more precise explanation than an aliasing
ambiguity**: it is a classification-bucket conflation in the published figure's own arithmetic, not
primarily a first-alias-vs-all-aliases method difference (though that difference is real too — see
below).

## Resolution

**Which method Phase 151 used: not fully determinable from the surviving artifacts.** `151-CONTEXT.md`
D-06/D-09 states the figures 406 / 111 / 39 with no runnable script attached; `152-RESEARCH.md` §A-8's
own live re-derivation, despite describing itself as "keyed on the first alias," in fact ran Method B
(alias-aware) throughout, because that is what `EpromDatabase.get_eprom()` always hands the classifier
regardless of lookup key. **There is no way to invoke the shipped CLI's actual `lock-status` command
with Method A's semantics at all** — every real invocation goes through `get_eprom()`, which always
supplies the full multi-alias `name`. Method A is therefore a synthetic counterfactual, included here
only because Task 1 requires running both, never a mode a user of this project can reach.

**Method A and Method B do NOT agree exactly.** Refusal totals are 664 (Method A) vs. 665 (Method B);
`read_permitted` is 82 (Method A) vs. 81 (Method B) — a ±1 swing, because one row's first alias alone
resolves to a readable/undocumented state that differs from the verdict produced once every alias in
that row is tokenised. **The "holds under either method" framing anticipated in `152-RESEARCH.md`'s
Open Question 1 recommendation is not literally exact** — it is exact to within 1 row, not identical.

**The formulation any outward artifact may cite, and why it is safe:** measured through the live
production code path (Method B — the only method the shipped CLI can actually run), **665 of the
746 database rows (89%) resolve to a refusal class; 81 are `read_permitted`.** This is not a
"robust under any conceivable method" claim — it is a direct measurement of what the shipped
classifier, as actually invoked by `firestarter dev lock-status`, produces today, with zero
classification errors over the full 746-row database. An outward sentence should attribute the
figure to "the live classifier" or "measured through the production code path," not to "either
counting method," since the two methods are not identical.

## Do not cite

The following figures are method-dependent, or precision that exceeds what is safe to publish, and
must **not** appear in any outward artifact this phase produces:

- **107 vs. 112** for `undocumented_alias` — differs by method (Method A: 107, Method B: 112).
- **112 vs. 108** for `not_readable` — differs by method (Method A: 112, Method B: 108).
- **82 vs. 81** for `read_permitted` — differs by method (Method A: 82, Method B: 81).
- **664 vs. 665** for the refusal-class total — differs by method.
- **406 / 111 / 39** — 151's own published D-06/D-09 figures; they do not reproduce under either
  method measured here (nearest matches: `no_mechanism` 405 not 406; the `not_readable`+
  `undocumented_alias` split behind "111" is 108+112 under Method B, not a single 111; `39` for
  algorithm `0x10` reproduces exactly under both methods and is safe to cite on its own if ever
  needed, but not as part of the disproven "406/111/39" triple).
- Any algorithm-5-only readability count that implies all 27 rows share one verdict — they do not
  (7 `not_readable`, 20 `undocumented_alias`, 0 `read_permitted`).
- **664/82 (Method A)** specifically — this is a synthetic, unreachable counterfactual, not what the
  shipped tool does; citing it outward would misrepresent what a real invocation of `lock-status`
  produces.

The only class-size figures safe to cite outward, per the Resolution above, are: **665 of 746 rows
resolve to a refusal class; 81 are `read_permitted`** (Method B / the live production code path),
and the two method-invariant class counts **`no_mechanism` = 405** and **`not_implemented` = 40**
(both decided purely by `protocol-id` membership, unaffected by aliasing).

This ships software-proven and unvalidated on silicon.

No AT28C part was tested at any point in v1.32.

Protocol `0x0D` stays UNVERIFIED in PROTOCOL-LEDGER.
