<!-- fixture for check_record_corrections.py test suite: never scanned as a real planning record -->
<!-- plants R-10's flash-headroom needle inside a properly opened warning-block, with the needle on a numbered body line below the opener (mirroring PROJECT.md:67's real shape) -- exercises the block-label exemption path, not just the line-label path. Must PASS. NOTE: this comment deliberately avoids repeating the planted figure itself. -->

<!-- DO NOT REFLOW: the block-suppression-is-real test (test 5) rewrites this
     file with the numbered needle line moved ABOVE the opener paragraph and
     asserts the mutation FAILS -- keep the opener paragraph and the numbered
     body line as separate, ordered lines exactly as below. -->

# Fixture: labeled correction control

**⚠ CORRECTION (fixture) — this paragraph opens a labeled block whose body
carries the stale figure below, corrected elsewhere in the same record.**

1. The Leonardo target has 2992 B of flash headroom remaining, a figure
   superseded by a later measurement; this numbered item stays inside the
   block opened immediately above because it is a numbered list item, not a
   top-level dash bullet, and is not itself a new label opener.
