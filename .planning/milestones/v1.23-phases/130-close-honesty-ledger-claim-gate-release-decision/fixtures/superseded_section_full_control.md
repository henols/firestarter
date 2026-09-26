<!-- fixture for check_record_corrections.py test suite: never scanned as a real planning record -->
<!-- plants the branches-27-behind needle TWICE in an "original body", then retroactively supersedes BOTH occurrences via a single recordscan:supersedes marker naming both line numbers -- the positive-direction sibling of superseded_section_control.md (which deliberately leaves one occurrence uncovered and FAILs). Must PASS. NOTE: this comment deliberately avoids repeating the planted figure itself. -->

<!-- DO NOT REFLOW: tests below locate the two needle lines and the marker
     line by exact content -- keep the body lines, the SUPERSEDED opener,
     and the marker line each on their own single physical line exactly as
     below, and do not renumber them without updating the marker's lines=
     value and the test module together. -->

# Fixture: superseded-section full control (original body)

Every branch in this fixture's imaginary inventory is 27 commits behind its imaginary base, as measured on this capture's own date.

A second, unrelated line also says every branch is 27 commits behind, and this time the marker below names both line numbers, so both are covered.

# Appended section

**⚠ SUPERSEDED (fixture) — the two body lines above are preserved verbatim; this section retroactively corrects both of them by line number, without editing either.**

Both claims above are corrected: the imaginary branches are now 0 behind. <!-- recordscan:supersedes needle=branches-27-behind lines=12,14 reason: fixture proves mechanism 3 retroactively exempts every named line in one marker, not just the first -->
