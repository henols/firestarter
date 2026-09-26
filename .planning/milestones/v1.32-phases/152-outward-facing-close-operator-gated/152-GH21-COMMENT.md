Hi @AndersBNielsen — following up on your `dev test` report for at28c256.

**What your report already told us**

Your report's `auto_capture` block carries `"fw_board_identity": null`. A report that cannot say
which firmware produced it cannot be root-caused — there's no way to tell whether a failure belongs
to the host or to the board. That gap was the first thing fixed in v1.32, and it's the reason the ask
at the end of this comment is worth making at all. One more thing worth naming plainly: your report
ran host version `3.0.0b15`, not the latest pre-release, so everything below about what has changed is
measured against that version, not against whatever `pip install --pre` gives you today.

**The erase step's reason string is no longer true**

Your report's `erase` step reads `NA`, with the reason:

> protocol 0x0D (28C family) has no erase operation; each page write auto-erases internally

That line is no longer true of the tree. A standalone erase step now exists on this protocol,
implemented with the manufacturer's own software six-byte chip-erase sequence, not the datasheet's
12 V hardware path. The software path was the deliberate choice: the hardware path would put 12 V on
a pin of this part's pinout, and this project does not put 12 V on a pin of a 5 V part.

**The write and blank-check verdicts — two separate fixes, not one**

Your `blank-check` and `write` steps both read `BAD`. They were fixed in two different places, and it
matters which:

- The **blank-check step** is a host-side fix. On this protocol, a page write auto-erases internally,
  so no step in a test plan can ever leave the device blank. The step is now marked not-applicable,
  with that as its own reason, instead of run and failed.
- The **write step** is a firmware-side fix. The pre-write blank check on this protocol is gone: on
  this silicon a page write auto-erases and every page gets read back and verified anyway, so the
  check was never actually a safety net — it was a precondition that made a non-blank part unwritable
  unless you passed an override flag. Here's the consequence, stated plainly: the host's `dev test`
  write step sends no override flag, so this fix only takes effect on a board running v1.32 firmware.
  Against older firmware, the same failure would reproduce exactly as it did when you filed this
  report.

**gh#32**

gh#32 was closed on 2026-08-08 as a duplicate fold into gh#21, which stays open. Both reports carry
the same fingerprint (`00e121446ceb`), and the consolidated table in this thread preserves the folded
report. I'm not reopening #32, and this thread itself is not closed either.

**What's still unproven**

None of this has been checked against real AT28C hardware.

No AT28C part was tested at any point in v1.32 — not in writing the erase sequence, not in choosing
the unlock prefix, not in any test. The protocol's ledger status is unchanged, and no chip's support
field moved: the chip database is byte-for-byte the same as before. The erase timing constant used is
an Atmel-family maximum, and a part with a longer actual erase cycle than that maximum would read
non-blank right after a successful-looking erase, with nothing in the test suite able to catch it. And
no test can prove the wall-clock wait is actually honoured on real hardware — the native test stubs
this project runs record no elapsed time at all, so that particular assertion is structural, not
temporal.

**The ask**

If you still have this part, a fresh `dev test` run is worth doing now, because this run will be the
first one whose report can say which firmware it ran on. Two things to install first, and both
matter:

```
pip install --pre firestarter
firestarter fw --install
firestarter dev test at28c256
```

The write-path fix lives in the firmware, not the host, and the host's test step still sends no
override flag — so without the firmware update, the same failure would happen again for the same
underlying reason. Either outcome is useful: a pass would mean this write path has held up against a
real AT28C part for the first time; a failure this time comes with the firmware identity attached, so
it's something that can actually be root-caused instead of guessed at. I'm not promising which way it
goes.
