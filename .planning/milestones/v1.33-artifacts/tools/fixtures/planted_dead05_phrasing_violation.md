<!-- Deliberate planted DEAD-05 violation, used only by
     test_check_dead05_phrasing.py. This file lives under
     .planning/milestones/v1.33-artifacts/tools/, so it is outside the real corpus by
     construction (see 155-dead05-phrasing-corpus.md section 5 -- corpus
     globs never descend into this directory). Its third paragraph carries
     a forbidden phrasing but does NOT name the function, which exists to
     prove the trigger scoping is real rather than incidental. -->

Paragraph one names `rurp_read_voltage_mv` directly and claims the
arithmetic was tested on real hardware before this change shipped, which is
exactly the forbidden coverage claim this gate exists to catch.

Paragraph two also names `rurp_read_voltage_mv`, and is clean: it is
proven by a committed host-side numerical oracle over a stated input grid,
bound to the shipped C by a source-contract scan; no native and no bench
coverage exists. This paragraph must not be flagged.

Paragraph three never names the function at all, but still claims the
firmware build was tested this session -- proving that a forbidden word
alone, without the trigger token present in the same paragraph, is not
enough to flag anything.
