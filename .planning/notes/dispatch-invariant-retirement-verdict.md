---
title: Dispatch invariant retirement verdict — the three-way dispatch invariant is RETIRED OUTRIGHT, no successor
date: 2026-09-11
context: v1.37 Phase 184, CLAIM-03 — measured in this session against live source (all three repos)
  and git history, plus the two orphaned `planted_dispatch_*.cpp` fixtures, read in full before
  `184-04` deletes them.
---

# Dispatch invariant retirement verdict (CLAIM-03)

## THE VERDICT

**The three-way dispatch invariant — dispatch table (`PROTOCOLS.md`), host tool
(`KNOWN_PROTOCOLS`), and firmware (`kAllProtocolFamilies`) all agreeing — is RETIRED
OUTRIGHT. No successor guard. No backlog item. A future need re-opens the question from
scratch.** This was the operator's own call, taken against the orchestrator's
recommendation, which was to retire the three-way and backlog the narrower two-way
`KNOWN_PROTOCOLS` ↔ `kAllProtocolFamilies` successor instead.

**Two limits on this verdict, stated before any detail.** First, the verdict rests on
what the three legs were measured to do — not on a claim that the underlying protocol
lists actually agree; the divergence table below is on the record as measured and
explicitly unjudged. Second, retirement is reversible in principle, but nothing will be
watching after this note is committed — re-opening depends on someone noticing unaided,
which is precisely the condition this milestone exists to correct. That is the operator's
own caveat, stated in the operator's terms, and it is not softened here into a
reassurance: nothing currently planned will surface this question again.

## THE GROUNDS

Three grounds, checked against source in this session before being written. The first
ground below **corrects** the framing carried in `184-CONTEXT.md` (D-08 item 1) — the
correction and the evidence for it are given in place, because the original framing does
not survive verification and this document is not permitted to carry a citation that
does not.

**(a) Nothing machine-reads `firestarter/PROTOCOLS.md` today, in any of the three
repositories — but not because the file lacks a claims-region delimiter.** It has one.
`184-CONTEXT.md`'s D-08 item 1 states the document leg "carries no claims-region
delimiter at all"; that is false, and this session's own read of `PROTOCOLS.md` finds it
false on inspection:

```
$ cd /workspaces/firestarter && /usr/bin/grep -n 'firestarter-claims-begin\|firestarter-claims-end' PROTOCOLS.md
53:<!-- firestarter-claims-begin -->
82:<!-- firestarter-claims-end -->
```

These markers have been in the file since it was first committed (`bbcdc39`, "docs: add
the firmware protocol and pinout references") — they did not arrive or leave with any
edit this phase makes. The now-deleted meta-repo checker
(`tools/wiki/dispatch_mirror.py`, deleted 2026-09-02 by `5426d7ef`) parsed exactly this
delimiter pair structurally, recoverable from git history even though no live checkout
carries the file:

```
$ git show 5426d7ef^:tools/wiki/dispatch_mirror.py | head -35
...
CLAIMS_BEGIN = "<!-- firestarter-claims-begin -->"
CLAIMS_END = "<!-- firestarter-claims-end -->"
...
def parse_claims_region(text: str) -> str | None:
    begin = text.find(CLAIMS_BEGIN)
    if begin == -1:
        return None
    ...
```

So the document leg was not unparseable, and the "keep its table shape intact"
instruction the old `PROTOCOLS.md` paragraph carried was real advice for a real (if
never-exercised) parser, not a warning about an empty gesture. What actually makes the
document leg bound nothing is narrower and more damning than "no marker exists": every
consumer of that marker is gone — the app repo's original `tests/test_dispatch_mirror.py`
(module-scope `fw_path("doc", "PROTOCOLS.md")`, deleted 2026-08-31 by `39ea3e8`) and its
meta-repo successor `tools/wiki/dispatch_mirror.py` (deleted 2026-09-02 by `5426d7ef`) —
and, per `5426d7ef`'s own commit message (quoted in full under Leg B below), the CI
workflow that would have run the meta-repo checker, `wiki-check.yml`, **had run ZERO
times** before its own retirement. A parser that exists in source but is wired to a
workflow that never once executed bounds nothing in practice, whether or not it carries a
delimiter. Confirmed today, across all three repositories:

```
$ /usr/bin/grep -rn 'firestarter-claims-begin\|firestarter-claims-end\|PROTOCOLS.md' \
    --include='*.py' --include='*.sh' --include='*.yml' /workspaces 2>/dev/null | /usr/bin/grep -v '/.planning/'
(no output — no live script in any of the three repositories references PROTOCOLS.md or its delimiter)
```

(The only hits inside `.planning/` are frozen `.v1.34-arms/` bench-rig control snapshots
from the closed v1.34 milestone — archived comparison artefacts, not live scripts, and
excluded from the count above.)

**(b) The firmware leg was fail-open by construction.** The deleted checker's firmware-leg
check extracted every `0x[0-9A-Fa-f]+` token from the whole file text of
`test/native/avr/test_dispatch/test_configure_memory.cpp` via a bare regex with no
comment-awareness:

```
$ git show 5426d7ef^:tools/wiki/dispatch_mirror.py | /usr/bin/grep -n '_FW_HEX_TOKEN_RE\|fw_hex_tokens ='
41:_FW_HEX_TOKEN_RE = re.compile(r"0x([0-9A-Fa-f]+)")
132:    fw_hex_tokens = {int(tok, 16) for tok in _FW_HEX_TOKEN_RE.findall(fw_text)}
```

So a comment-only mention of a protocol's hex identifier satisfied this leg exactly as
well as a real dispatch case would. The two orphaned `planted_dispatch_*.cpp` fixtures
prove this directly and are the subject of their own section below (D-08 item 3), because
that finding must survive their deletion in `184-04`.

**(c) Of the three legs, only the host leg — `KNOWN_PROTOCOLS`, a plain Python set
literal in `firestarter_app/tools/build_db.py` — was checked by native language semantics
rather than by regex-scraping raw file text.** The document leg required a markdown-table
regex parse (`_BUCKET_ROW_RE`/`_FAMILY_ROW_RE`, shown in Leg A below) and the firmware leg
required the comment-blind hex-token regex in ground (b); only the host leg was `import`ed
and read as an actual Python object (`set(dispatch_module.KNOWN_PROTOCOLS)`). That
asymmetry does not by itself retire the invariant — the document leg's structural parse
was real, when it ran — but combined with (a)'s "ran zero times" fact and (b)'s fail-open
firmware leg, the practical result is the same: nothing in this project's actual history
exercised a three-way check that would have caught a real divergence before it happened.

## THE EVIDENCE CHAIN

Two lettered legs, the two-deletion history that nobody intended.

**Leg A — `39ea3e8`, 2026-08-31, app repo, `fix(168-04): sever the module-scope fw_path
collection hazard`.** It deleted `tests/test_dispatch_mirror.py` because that module's
module-scope `fw_path("doc", "PROTOCOLS.md")` raised `MissingScanTargetError` and aborted
the WHOLE app suite at collection once `firestarter/doc/` was deleted — a collection-time
abort, not a test failure. In the same commit it deliberately re-pointed the surviving
`ScanPathEntry` at `tools/wiki/dispatch_mirror.py (meta repo; relocated by 168-10)`,
naming where the mirror-check logic had already moved by that point (Phase 168 Plan 10).

```
$ cd /workspaces/firestarter_app && git log -1 --format='%H %ad %s' --date=short 39ea3e8
39ea3e8f9819603a999f13027deaaddc1f459492 2026-08-31 fix(168-04): sever the module-scope fw_path collection hazard

$ git show 39ea3e8 --stat
 tests/scan_paths.py            |   6 +-
 tests/test_dispatch_mirror.py  | 366 -----------------------------------------
 tools/check_no_exists_proxy.py |   1 -
 3 files changed, 1 insertion(+), 372 deletions(-)

$ git show 39ea3e8 -- tests/scan_paths.py
--- a/tests/scan_paths.py
+++ b/tests/scan_paths.py
@@ -109,13 +109,9 @@ CROSS_REPO_TEST_PATHS: tuple[ScanPathEntry, ...] = (
             "test_sdp_table_parity.py",
         ),
     ),
-    ScanPathEntry(
-        "doc/PROTOCOLS.md",
-        ("test_dispatch_mirror.py",),
-    ),
     ScanPathEntry(
         "test/native/avr/test_dispatch/test_configure_memory.cpp",
-        ("test_dispatch_mirror.py",),
+        ("tools/wiki/dispatch_mirror.py (meta repo; relocated by 168-10)",),
     ),
```

**Leg B — `5426d7ef`, 2026-09-02, meta repo, `chore: retire wiki-check.yml and the
tools/wiki checkers`.** Two days later it retired every `tools/wiki/` checker,
demolishing the receiving end of a handoff that had just been written.

```
$ git log -1 --format='%H %ad %s' --date=short 5426d7ef
5426d7ef6b32cf83680ae056baa4e65d591a2ab6 2026-09-02 chore: retire wiki-check.yml and the tools/wiki checkers

$ git show 5426d7ef --stat | head -12
 .planning/CLOSE-RECORD.md               | ...
 .planning/REQUIREMENTS.md                | ...
 .planning/ROADMAP.md                     | ...
 .github/workflows/wiki-check.yml         | deleted
 tools/wiki/wiki.py                       | deleted
 tools/wiki/honest01_claims.py            | deleted
 tools/wiki/honest02_truth.py             | deleted
 tools/wiki/dispatch_mirror.py            | deleted
 tools/wiki/provenance_footers.py         | deleted
 tools/wiki/selftest.sh                   | deleted
 tools/wiki/claim-allowlist.json          | deleted
 tools/wiki/claim-vocabulary.json         | deleted
```

The commit's own message states the measured reason, quoted in full because it is the
strongest evidence in this whole record for "bounded nothing":

```
Measured 2026-09-02, and the reason:
  2,558 lines of checkers (selftest.sh alone 653)
  guarding 12 wiki pages, 28 commits old, one human author
  the Wiki check workflow had run ZERO times
  HONEST-02's leg 2 resolved claims on exactly 1 page of 12
  honest01_claims.py, 308 lines, was invoked by nothing
  dispatch_mirror.py never read the wiki, despite its leg's message
```

**Neither commit intended to retire the invariant.** Each was a correct local fix — sever
a collection-time abort, retire disproportionate machinery that had never run — and the
invariant died in the eleven-day gap between them, unnoticed until this phase's own CLAIM-01/CLAIM-02 sweep found it.

## WHAT THE DELETED FIXTURES PROVED

This is D-08 item 3, and it is the reason `184-04` may delete the two orphaned fixtures at
all — the knowledge they encode is captured here first.

`firestarter_app/tests/fixtures/planted_dispatch_comment_only_hex.cpp`'s own header states
the fail-open finding directly, quoted verbatim:

```
 * THIS FIXTURE'S PAIRED TEST LEG asserts GREEN, not RED. Do NOT "fix" this file by
 * removing the comment or by wrapping the paired leg
 * (test_planted_comment_only_hex_is_NOT_detected) in `pytest.raises`. The
 * GREEN result IS the finding: `test_dispatch_mirror_firmware_leg_enumerates_all_protocols`
 * extracts every `0x[0-9A-Fa-f]+` token from the WHOLE file text via a bare
 * regex with no comment-awareness, so a comment-only mention of `0x10`
 * satisfies the gate exactly as well as a real dispatch case would. A
 * reader who "corrects" this fixture or its leg to expect RED destroys the
 * one committed proof that the gate cannot distinguish "a native dispatch
 * test exists for this protocol" from "a comment mentions this protocol".
```

Its paired leg, `test_planted_comment_only_hex_is_NOT_detected`, asserted GREEN — and the
GREEN was the finding, not a bug to fix. `firestarter_app/tests/fixtures/planted_dispatch_missing_hex.cpp`'s header names the
same `0x[0-9A-Fa-f]+` regex from the RED side, and explains why that sibling fixture never
spells the real identifier as a contiguous `0x`-prefixed token anywhere, not even in its
own header:

```
 * never spells the real identifier as one contiguous `0x`-prefixed token
 * anywhere in this file (not even here in the header) -- because
 * `test_dispatch_mirror_firmware_leg_enumerates_all_protocols` extracts
 * every `0x[0-9A-Fa-f]+` token from the WHOLE file text via a bare regex
 * with no comment-awareness, and a stray mention in this very docstring
 * would silently satisfy that regex and invalidate this fixture's entire
 * purpose.
```

Two further facts, recorded here because they corroborate the rest of this document and
because both fixtures are about to be deleted:

- **Both fixture bodies carry a byte-faithful copy of `kAllProtocolFamilies`**, with
  `flash_intel`'s row rewritten from `{0x10, "flash_intel (0x10)"}` to `{0xFF, "flash_intel
  (0xFF)"}`. Counted in this session, in both files:

  ```
  $ cd /workspaces/firestarter_app && /usr/bin/grep -c '^    {0x' tests/fixtures/planted_dispatch_comment_only_hex.cpp tests/fixtures/planted_dispatch_missing_hex.cpp
  tests/fixtures/planted_dispatch_comment_only_hex.cpp:13
  tests/fixtures/planted_dispatch_missing_hex.cpp:13
  ```

  13 rows in each — independently corroborating the 13-row figure the drift table below
  states for `kAllProtocolFamilies`, without relying on `test_configure_memory.cpp` as the
  only source for that count.

- **Both headers instruct future readers NOT to delete the fixtures.** That instruction is
  **superseded by D-05 and D-07**: their consumer, `tests/test_dispatch_mirror.py`, was
  deleted 2026-08-31 by `39ea3e8` (Leg A above), and under D-05's retire-outright verdict
  no consumer will ever exist again. This note is where the knowledge the do-not-delete
  instruction was protecting now lives — a later reader who finds the fixtures' deletion
  in git history, and wonders why a header saying "do not delete" was overridden, should
  land here.

## THE DRIFT, MEASURED AND NOT ADJUDICATED

Three protocols disagree between the host's `KNOWN_PROTOCOLS`
(`firestarter_app/tools/build_db.py:137`) and the firmware's `kAllProtocolFamilies`
(`firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp:203`), each
carrying its own side's stated reason in its own source:

| Protocol | `KNOWN_PROTOCOLS` (host) | `kAllProtocolFamilies` (firmware) | Reason each side carries |
|---|---|---|---|
| `0x34` | **present** | absent | "XICOR X88C64P — DIP-parallel NovRAM; unimplemented protocol but confirmed DIP-parallel memory... included as protocol-not-implemented" (`build_db.py:130-137`) |
| `0x35` | absent | **present** | "NOT 0x35 or 0x39 — removed by v1.11 DEC-05" (`build_db.py:149`, host-side comment) |
| `0x39` | absent | **present** | same — removed by v1.11 DEC-05 |

Totals, re-measured in this session rather than carried forward from `184-CONTEXT.md`:

```
$ cd /workspaces/firestarter_app && python3 -c "
known = {0x05,0x06,0x07,0x08,0x0B,0x0D,0x0E,0x10,0x27,0x28,0x29,0x34}
print(len(known))
"
12

$ cd /workspaces/firestarter && /usr/bin/grep -c '^    {0x' test/native/avr/test_dispatch/test_configure_memory.cpp
13
```

12 host-side, 13 firmware-side.

**This phase MEASURED the divergence and did NOT verify the reason either side carries.**
Neither figure — the host's inclusion of `0x34`, or the firmware's inclusion of `0x35` and
`0x39` — is verified by anything in this session or, as far as this record establishes, by
anything before it. Adjudicating which side is correct would mean reopening v1.11's DEC-05
(the decision that removed `0x35`/`0x39` from the host) and the X88C64P
not-implemented decision (why `0x34` is host-included but firmware-absent) — protocol-domain
work the milestone's Out of Scope bars, and a defect surfaced there would have no room to
be fixed in this milestone. No reader should mistake this table for a clean bill of
health on either side.

## WHAT THIS PHASE DELIBERATELY DID NOT DO

The negative record. A later reader of this note should not mistake the absence of a
successor guard or a backlog filing for the question having gone unasked — it was asked,
and answered: file nothing.

- **ZERO backlog items were filed on this axis.** No `KNOWN_PROTOCOLS` ↔
  `kAllProtocolFamilies` successor-guard item. No "unverified drift" item. No todo, no
  GitHub issue.
- **The two-way successor WAS considered, and the operator explicitly declined to file
  it.** Both `KNOWN_PROTOCOLS` (a Python set literal) and `kAllProtocolFamilies` (a C
  array) are structured and machine-readable, so a successor could be checked properly —
  "every difference is accounted for" — rather than through the comment-blind regex that
  made the deleted three-way leg fail open. It is recorded here as a **rejected option**,
  so a later reader knows it was considered, not as a backlog candidate: do not file it on
  the strength of this paragraph.
- **Phase 182's 999.55–999.59 and Phase 183's 999.63–999.66 set a filing pattern that does
  not apply here.** An "obviously warranted" filing on this axis would quietly reinstate
  what the operator closed.
- **The same one-row-per-`KNOWN_PROTOCOLS`-entry false claim recurs at three further sites
  inside `test/native/avr/test_dispatch/test_configure_memory.cpp`, beyond the single
  clause `184-02` already excised** (the comment above `kAllProtocolFamilies`, corrected
  in commit `ec7c1bb`, "docs(184-02): delete false one-row-per-KNOWN_PROTOCOLS clause from
  dispatch comment"):

  ```
  $ cd /workspaces/firestarter && /usr/bin/grep -n 'KNOWN_PROTOCOLS' test/native/avr/test_dispatch/test_configure_memory.cpp
  9:One test per protocol in KNOWN_PROTOCOLS (build_db.py:89). Each test
  65:Positive dispatch tests — one per protocol in KNOWN_PROTOCOLS.
  425:13 protocol-positive tests (one per KNOWN_PROTOCOLS entry)
  ```

  All three repeat the same false clause the excised one carried: `KNOWN_PROTOCOLS` has
  **12** entries, not 13, so "one per `KNOWN_PROTOCOLS` entry" undercounts by exactly the
  `0x35`/`0x39` divergence this table already carries. Line 9 additionally cites
  `build_db.py:89` for the `KNOWN_PROTOCOLS` symbol, which actually lives at line 137 —
  line 89 sits inside an unrelated dict (`NMOS_TRUE_VPP_MV`), confirmed in this session:

  ```
  $ cd /workspaces/firestarter_app && sed -n '85,92p' tools/build_db.py
  # (NMOS_TRUE_VPP_MV block — unrelated to KNOWN_PROTOCOLS)
  $ /usr/bin/grep -n '^KNOWN_PROTOCOLS = {' tools/build_db.py
  137:KNOWN_PROTOCOLS = {
  ```

  These three sites were **seen and deliberately left**: `184-CONTEXT.md`'s D-10 names one
  clause only, its § Deferred Ideas flags the line-number citation as explicitly not filed,
  and D-06 bars a filing on this axis. Recording them here is a record, not a filing — that
  distinction is the whole point of this section, and the whole point of this phase.

## Backlog items this verdict generates

None. Zero, deliberately, per D-06 — see the negative record above.
