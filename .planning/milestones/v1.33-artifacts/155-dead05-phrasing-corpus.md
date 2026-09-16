---
title: DEAD-05 phrasing corpus -- three named exclusions and the non-vacuity floor
phase: 155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim
plan: "03"
status: AUTHORITATIVE -- the contract check_dead05_phrasing.py reads its scope from
requirements: [DEAD-05]
---

# DEAD-05 phrasing corpus -- v1.33 Phase 155

## 1. What DEAD-05 demands, and why prose needs a gate at all

DEAD-05 is a requirement about the honesty of wording, not about code: "the coverage
ceiling is stated, not implied" for `rurp_read_voltage_mv`. `src/boards/rurp_common.cpp`
compiles in no native environment (`[env:native]`'s `src_filter = +<proms/>`), so DEAD-04's
committed host-side numerical oracle is the *only* mechanical check on this arithmetic, and
no Phase 155 artefact may imply that native or bench coverage exists.

The single highest-risk event this gate exists to catch: the preserved reference
(`a6b46f8`) carries its own `rurp_common.cpp` comment claiming this arithmetic is covered by
a form of testing that does not exist. Copying that comment across unedited is the single
most likely way this phase fails DEAD-05 -- and would violate D-02 (no bench/hardware claim)
in the same stroke.

## 2. The two mandatory halves

**Negative half.** Scan every in-scope paragraph across the corpus for the forbidden
phrasings enumerated in `155-VALIDATION.md`, section "The Honest Coverage Ceiling", item 5.

**Positive half.** Assert that the mandated correct phrasing named in that same item 5 is
present, whitespace-normalised, in each of the four required-positive targets (section 8
below).

**Both are mandatory.** An absence-only gate is vacuous: an empty corpus, a renamed file, or
a typo'd glob would all report zero forbidden-phrasing hits and pass trivially, without ever
having looked at a single real paragraph. Requiring the positive assertion as well means the
gate can only pass when it has actually found, and approved, the correct sentence in the
places that matter -- it cannot pass by finding nothing.

## 3. The trigger: a paragraph naming `rurp_read_voltage_mv`

A paragraph is IN SCOPE for the negative scan if and only if it names the token
`rurp_read_voltage_mv`. Reason: DEAD-05 forbids implying coverage OF THAT FUNCTION, not
forbidding the words in the forbidden list (`155-VALIDATION.md` item 5) everywhere they
occur. Several entries in that list build on ordinary English verbs whose unrelated uses
elsewhere in this phase's own artefacts -- describing, say, the DEAD-01 symbol gate, or the
DEAD-06 native suites -- are not DEAD-05 violations. Scoping the trigger to the function name
is the honest reading of the requirement and is what keeps the gate discriminating instead of
noisy.

## 4. The paragraph unit

A paragraph is a blank-line-delimited block of the raw file text. This applies uniformly to
Markdown, C/C++ and Python source: a C comment block is one paragraph under this rule, and a
Python module docstring is one paragraph under this rule, provided neither is interrupted by
a genuinely blank line in the source.

This was chosen over a fixed line window (for example, "5 lines before and after the
trigger") because a line window is an arbitrary constant with no relationship to how prose or
comments are actually laid out -- it would either clip a real violation that spans a longer
comment block, or flag unrelated text pulled in by an oversized window. The blank-line rule
has no tunable constant and matches the natural unit a human author already writes in.

## 5. The corpus

Twelve globs, each named with the repository it is relative to. `.planning/` globs are
relative to the meta repo (`/workspaces`); `firestarter/...` paths are relative to the
`firestarter` submodule.

1. `.planning/phases/155-*/155-*-PLAN.md` (meta)
2. `.planning/phases/155-*/155-*-SUMMARY.md` (meta)
3. `.planning/phases/155-*/155-VERIFICATION.md` (meta, when it exists -- absent today)
4. `.planning/milestones/v1.33-artifacts/155-*.md` (meta)
5. `firestarter/src/boards/rurp_common.cpp` (fw)
6. `firestarter/src/proms/memory.cpp` (fw)
7. `firestarter/include/firestarter.h` (fw)
8. `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` (fw)
9. `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` (fw)
10. `firestarter/tests/test_voltage_reformulation_oracle.py` (fw -- created by plan 04, see
    section 4 of the "Corpus members that do not exist yet" note below)
11. `firestarter/scripts/check_no_heap_or_64bit_symbols.py` (fw)

`.planning/milestones/v1.33-artifacts/tools/` is never descended into by any of the above globs. The tool's own
source, its pytest, and its planted fixture live under that directory precisely so they
cannot enter the corpus they themselves judge -- this is stated explicitly, not left as an
accident of glob shape.

## 6. The three named exclusions -- exactly three, no more

- `155-RESEARCH.md` -- a researcher-authored input that enumerates the six forbidden
  phrasings in order to forbid them, and quotes the preserved reference's defective comment
  as evidence of the violation it warns against.
- `155-PATTERNS.md` -- same reason, plus it quotes the defective comment verbatim as the text
  to be rewritten, so a negative scan over it would flag the very passage that documents the
  fix.
- `155-VALIDATION.md` -- the file that DEFINES the forbidden list and carries the mandated
  correct phrasing this gate's positive half requires elsewhere. It is excluded from the
  negative half for that reason, and for no other: it is the document that enumerates the
  forbidden phrasings by name, so it necessarily contains their literal text.

These are the only three exclusions. No `PLAN.md`, no `SUMMARY.md`, no other `155-*` record,
and no source file -- including `firestarter/src/boards/rurp_common.cpp`, the oracle pytest,
or any `155-VALIDATION.md`-citing document -- is exempted. A fourth exclusion may not be
added to make a red run green; if a real artefact fails this gate, the artefact's wording is
fixed, not the gate's scope.

## 7. The non-vacuity floor

`PARAGRAPH_FLOOR = 6`. This is the minimum number of in-scope paragraphs (paragraphs naming
`rurp_read_voltage_mv`) the scan must find across the whole corpus before it may report
success. Below the floor, the gate cannot render a verdict and fails closed (exit 2), because
a shrunken or emptied corpus must never be indistinguishable from a genuinely clean one.

The floor is justified by construction -- six paragraphs that MUST exist once the phase's
artefacts are complete:

1. `rurp_common.cpp`'s own function comment above `rurp_read_voltage_mv`, which names the
   function it documents.
2. The oracle pytest's module docstring (`test_voltage_reformulation_oracle.py`), which must
   name the function it models.
3. The oracle's own coverage-ceiling test leg, which names the function under test.
4. Plan 04's ceiling paragraph (its PLAN.md / SUMMARY.md), which states the coverage ceiling
   for the function it changes.
5. Plan 06's ceiling paragraph (its PLAN.md / SUMMARY.md), which restates the ceiling once the
   real corpus is complete.
6. The phase record's (`155-after-figures.md`) ceiling section, which states the ceiling for
   the phase's readers.

A floor breach is reported as `ERROR:` and exit 2 -- "cannot render a verdict" -- never as
exit 0. A gate that silently shrank its own corpus to zero and then reported PASS would be
worthless; this floor is what prevents that failure mode.

## 8. The required-positive targets

The mandated correct phrasing (section 9 below) must appear, whitespace-normalised, in each
of these four files:

1. `155-VALIDATION.md` (meta)
2. `.planning/milestones/v1.33-artifacts/155-after-figures.md` (meta -- the phase record, produced by plan 06)
3. `firestarter/src/boards/rurp_common.cpp` (fw -- the corrected comment, produced by plan 04)
4. `firestarter/tests/test_voltage_reformulation_oracle.py` (fw -- produced by plan 04)

A required target missing from disk is `ERROR:` and exit 2, not a silent skip and not a
failure conflated with a real phrasing violation. This is why the real, complete-corpus run
belongs to plan 06: targets 2-4 do not exist until plans 04 and 06 have run. Plan 03 (this
plan) proves the tool discriminates correctly against a synthetic corpus; it does not, and
cannot, run cleanly against the real corpus yet.

### Corpus members that do not exist yet are expected, not an error

Two corpus members are deliberately absent from disk at the time this document and its tool
are committed: `firestarter/tests/test_voltage_reformulation_oracle.py` (created by plan 04)
and the corrected comment inside `firestarter/src/boards/rurp_common.cpp` (also plan 04). The
tool's glob-resolution step treats a corpus glob that currently matches nothing as an empty
match -- it is silently absent from the resolved file list, the same way an empty
`glob.glob()` result naturally behaves, and this is NOT the same code path as a
required-positive target that is missing (section 8's exit-2 path). The distinction is
deliberate: the corpus is scanned for violations only in files that exist ("nothing found to
scan" is not an error, because a corpus member that has not been authored yet cannot carry a
violation); a required-positive target, by contrast, is asserted BY PATH regardless of the
corpus glob match, so its absence is always exit 2. This choice cannot mask a later deletion
of an existing corpus member, because `PARAGRAPH_FLOOR` (section 7) requires the total
in-scope paragraph count across the whole corpus to clear 6 regardless of which individual
files those paragraphs came from -- deleting an already-existing, already-counted corpus file
would drop the total paragraph count and trip the floor, not silently pass. Plan 06, which
runs after plan 04, is the run where every corpus member and every required target is
expected to exist simultaneously.

## 9. The mandated correct phrasing

The negative half's forbidden phrasings are deliberately NOT reproduced in this document by
literal quotation of the same six words used as the tool's needles -- see `155-VALIDATION.md`
item 5 for the enumerated list. This document, like the tool's own source, lives inside the
corpus its own gate could in principle scan, and quoting the forbidden list verbatim would
either fail this document's own gate run or force a fourth exclusion -- exactly what section
6 forbids. Reference `155-VALIDATION.md` item 5 instead.

The mandated correct phrasing, which the positive half asserts is present verbatim (modulo
whitespace normalisation) in each of the four required targets in section 8:

> proven by a committed host-side numerical oracle over a stated input grid, bound to the
> shipped C by a source-contract scan; no native and no bench coverage exists.

## 10. The named residual risk -- stated as unmitigated

avr-gcc miscompiling the 32-bit multiply/divide in `rurp_read_voltage_mv` is a named residual
risk. It is unmitigated by any artefact of this phase. It is mitigated only by that being
AVR's most-exercised code-generation path, and by this phase's change reducing rather than
increasing codegen complexity (removing the 64-bit runtime helpers and their call sites). No
artefact in this phase's corpus may present this risk as covered or closed.

## 11. Not automated

`.planning/milestones/v1.33-artifacts/tools/check_dead05_phrasing.py` runs in NO CI workflow of either the meta
repo or the `firestarter` repo. It is a local-run obligation, exactly like
`firestarter/scripts/check_size_baseline.py` -- every run of it against the real corpus is
something a human or an agent must invoke by hand, and no artefact in this phase may imply
that CI enforces it.
