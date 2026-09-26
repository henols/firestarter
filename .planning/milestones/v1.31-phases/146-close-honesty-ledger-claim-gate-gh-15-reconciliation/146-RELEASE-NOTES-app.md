# Host app prerelease — 27C pulse override + long-write timeout fix

**Version:** `3.0.0b21` — read from `gh release list --repo henols/firestarter_app` at 2026-08-18T09:58:57Z, never predicted. Cut by `beta-release.yml` from merge commit `91c2add0` (PR #51). PyPI upload verified **independently of GitHub**, because this project has had GitHub carrying betas through `b17` while PyPI stopped at `b15`: `firestarter-3.0.0b21-py3-none-any.whl` and `firestarter-3.0.0b21.tar.gz` are both present on PyPI. Stable is **unchanged** — PyPI `info.version` is still `2.0.7`. The matching firmware release is **`3.0.0b19`**; the two repositories version independently, so the numbers do not agree and are not expected to.

`pip install --pre --upgrade firestarter`

This GitHub release page carries no attached files — it is a tag-and-marker page only. PyPI is the
distribution channel for the host app; the command above pulls it. The matching firmware for this
release is published separately, and its `.hex` files are what `firestarter fw --install` pulls
when you update your board — a reader upgrading one half without the other should know which half
does what before doing so.

## What changed

### Long writes no longer time out, and you can see them progressing

A write whose block takes tens of seconds used to hit the previous 10-second transport timeout and
appear to hang. It now reports its position from inside the block while it runs, and the write
completes without that timeout firing.

The boundary: intra-block progress arrives on the `leonardo` controller class only. On
`uno`/`uno328pb`-class controllers the emission is compiled out of the firmware structurally —
not merely absent by chance — so the display falls back to today's block-granularity progress on
those boards.

A cosmetic artefact you will see: the write progress bar does not reach a full 100%. This is a
display artefact, and every write is verified byte-exact regardless of where the bar stops — it is
filed as backlog **999.30**. Do not read a partial bar as a partial write.

### A max-pulse failure now names the address and the pulse count

Previously, a byte that failed to verify within its pulse budget could surface as an opaque
transport error with nothing pointing at what actually went wrong. It now reports the failing
address and how many pulses the firmware attempted before giving up — that is the diagnostic
difference this release makes.

### A per-run pulse override

`firestarter write --pulse-us N` (1–65535 microseconds) overrides the database's pulse width for
that one run. The bound is parity with another programmer's own integer pulse-width field — it is
**not** a wire-type or hardware limit. Use it to try a wider pulse on a marginal part for a single
run without editing the chip database; the database value itself lives in
`chip_database.json` (or your `~/.firestarter/database.json` override), and changing it there is
the persistent, per-chip way to make the change stick. The override rides the existing wire field
and introduces no new one.

## Also in this release

The write option surface this project documents now matches what actually ships. Two entries were
corrected: the blank-check option's documented long name and its own behaviour were both wrong
before this release — it is `-b` / `--no-blank-check`, and skipping the pre-write erase is now its
own separate option, `--skip-erase`. **Skipping erase on a non-blank electrically-erasable chip
leaves un-erased bits that cannot be reprogrammed afterward — treat that warning at full strength,
not as a milder caution than it sounds.**

## What is established, and what is not

**Established:**

- One 27C protocol, `0x07`, validated end to end on one part, one controller and one shield
  revision — the Winbond W27C512 (chip id `0xda08`) on a `leonardo`-class controller, shield
  Rev 2.0.
- The `--pulse-us` override exercised on that same part, on the wire, end to end.
- The corrected write-option documentation (the blank-check rename and the separate erase-skip
  option) matches the shipped CLI help text.
- Both this project's test suites pass locally at measured counts.

**Not established:**

- **The other two 27C protocols, `0x08` and `0x0B`, remain unvalidated on real silicon** —
  skipped-with-reason, because neither an AM27C020 nor an M2716/M2732 was on the bench this
  milestone, and neither disposition is inferred from the `0x07` result.
- **No comparative claim.** This release is not faster or more reliable than what preceded it — no
  control run was made, and a historical pre-milestone write-time figure recorded elsewhere in
  this project's history is a recorded number, not a control measurement.
- **No CI run has exercised any of this milestone's code**, on either the host or the firmware
  side, on any target.
- **The residual timeout gap is board-specific, not universal.** With no write-time budget
  advertised by the firmware (an older firmware build, for instance), `0x07`/`0x08` can still time
  out above roughly 4687 microseconds per pulse on a `leonardo`-class board and roughly 9375
  microseconds per pulse on an `uno`-class board — two different numbers for two different boards,
  not one project-wide figure.
- **The raised program-VCC ceiling.** The program-VCC the vendor write algorithms assume for
  threshold margin — around **6.25 V** above nominal — is unreachable on this shield, which has no
  VCC-raise path. This release delivers timing, pulse-count and verify fidelity, and **not**
  silicon-margin fidelity.

## The ask

If you have an AM27C020 or an M2716/M2732, running a write against it with this release and
reporting the result back — either outcome — is the most useful thing you could send for either of
the two unvalidated 27C protocols.
