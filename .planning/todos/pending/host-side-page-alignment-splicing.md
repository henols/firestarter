---
created: 2026-09-16T00:00:00Z
title: "Restore unaligned protocol 0x05 writes by splicing the head and tail page host-side before an aligned write"
area: host
resolves_phase: unassigned
files:
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/firestarter/page_size_gate.py
  - firestarter_app/firestarter/cli_handlers.py
---

## Problem

Phase 195 shipped a two-layer refusal (host pre-flight predicate plus firmware per-chunk guard)
for protocol `0x05` writes whose start address or payload length is not a whole multiple of the
part's page size. This is correct and necessary -- the part's own datasheet states the page erase
is implicit, whole-page and unconditional, so any byte not loaded when the page commits is erased.
But it also means patching part of a ROM image with an unaligned start address -- a normal
operation an operator does routinely -- now refuses outright where it previously silently erased
neighbouring bytes. Phase 195 measured and accepted that regression rather than build a fix for it
(`.planning/v1.39/195-partial-write-refusal-record.md` §4); this todo is the deferred strand that
would restore the capability.

## The shape

Read the head page and the tail page of the target range through the existing region-read
primitive, splice the caller's payload over them in memory, and issue a single page-aligned write
covering the full spliced range. The firmware guard from Phase 195 stays in place unconditionally
as the backstop -- this strand only ever produces host-side inputs the guard already accepts.

## The three facts that make it tractable

1. It needs **no firmware RAM** -- the splice buffer lives in Python on the host, not in the
   firmware's constrained AVR memory. Phase 195's own measurement (a 512-byte firmware staging
   buffer leaves 142 bytes of RAM on `uno` and 213 bytes on `leonardo` for the whole call stack)
   is what ruled out doing this in firmware at all.
2. It works at **every page size the database carries, including 512** -- the two parts Phase 195
   found un-bench-tested at that geometry are exactly the case a host-side splice does not need to
   special-case, because the read-splice-write shape does not depend on the page fitting in any
   fixed-size buffer.
3. The region-read primitive this needs already exists and is already used this way by the
   chip-test engine (`chip_test._read_region`), so this strand extends an existing, tested
   capability rather than opening a new one.

## Two honest caveats

- **A read failure must abort rather than proceed.** If the host cannot read back the head or tail
  page before splicing, it must not fall back to writing an incomplete page -- that would silently
  reintroduce the exact defect Phase 195's refusal exists to prevent.
- **The region-read's accuracy should be verified explicitly before anything is built on it.** This
  strand's correctness depends entirely on the read primitive returning the true current contents
  of the page; that assumption should be tested directly, not assumed because the primitive is
  already used elsewhere.

## What would close it

A plan that implements the read-splice-write shape in `eprom_operations.py`, wired behind the same
call sites `require_page_alignment` uses today, with the firmware guard left untouched as the
backstop, and a native/host test matrix proving the splice is byte-correct at every page size the
database carries plus the two honest caveats above.

## Filed by

Phase 195 (partial writes stop destroying the page), D-01/D-03, Plan 04.

## Closed by
