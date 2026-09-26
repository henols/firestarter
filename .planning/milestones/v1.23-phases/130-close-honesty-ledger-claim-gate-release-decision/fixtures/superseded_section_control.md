<!-- fixture for check_record_corrections.py test suite: never scanned as a real planning record -->
<!-- plants the branches-27-behind needle TWICE in an "original body", then retroactively supersedes only ONE of the two occurrences (line 12) via a recordscan:supersedes marker inside a trailing SUPERSEDED block -- exercises exemption mechanism 3 (Plan 130-09) in BOTH directions: the covered line PASSes, the uncovered line 14 stays FAIL, proving the marker is line-scoped, not file- or heading-scoped. Must FAIL as shipped (line 14 is deliberately left uncovered); see the test module for the covered-only variant. NOTE: this comment deliberately avoids repeating the planted figure itself. -->

<!-- DO NOT REFLOW: tests below locate the two needle lines and the marker
     line by exact content -- keep the body lines, the SUPERSEDED opener,
     and the marker line each on their own single physical line exactly as
     below, and do not renumber them without updating the marker's lines=
     value and the test module together. -->

# Fixture: superseded-section control (original body)

Every branch in this fixture's imaginary inventory is 27 commits behind its imaginary base, as measured on this capture's own date.

A second, unrelated line also says every branch is 27 commits behind, so the marker below must name line 12 by number, not merely "the branches-27-behind needle", to prove the exemption is scoped to a specific line rather than to every occurrence of the label in the file.

# Appended section

**⚠ SUPERSEDED (fixture) — the two body lines above are preserved verbatim; this section retroactively corrects one of them by line number, without editing either.**

The claim on line 12 is corrected: the imaginary branches are now 0 behind. <!-- recordscan:supersedes needle=branches-27-behind lines=12 reason: fixture proves mechanism 3 retroactively exempts a named line without touching it -->
