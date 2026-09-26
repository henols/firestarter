<!-- fixture for check_record_corrections.py test suite: never scanned as a real planning record -->
<!-- plants three needles (R-10, R-11, R-3) quoted AS needles on one line, mirroring ROADMAP.md:2468's self-reference (RESEARCH C-8: that line is Phase 130's own success criterion 1 and quotes the checker's own needles verbatim because it DEFINES them) -- exercises the recordscan:allow exemption path. Must PASS. NOTE: this comment deliberately avoids repeating any of the three planted figures/strings themselves, so the descriptive comment cannot accidentally re-trigger the needles it is describing. -->

<!-- DO NOT REFLOW: the self-reference-suppression-is-real test (test 9)
     rewrites this file's single needle-quoting line -- keep the three
     quoted needles and the recordscan:allow marker on ONE line. -->

# Fixture: self-reference control

This criterion is verified by grepping for each specific superseded figure/claim (e.g. "2992 B", "311eacf", "27 commits behind") and confirming zero remaining occurrences outside a labeled block, mirroring ROADMAP.md:2468. <!-- recordscan:allow this line defines three of the needle table's own entries, exactly as ROADMAP.md:2468 does (RESEARCH C-8) -->
