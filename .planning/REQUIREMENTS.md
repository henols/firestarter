# Requirements: Firestarter — v1.39 Protocol 0x05 Write Correctness

**Defined:** 2026-09-15
**Milestone:** v1.39 — "Never report success over bytes you erased"
**Core Value (this milestone):** A write to a 5V page-write flash part either preserves the bytes it was
not asked to change, or refuses — and never reports success while destroying data.

**Scope:** Firmware and host, dual-repo lockstep, plus one meta-repository tidy. The firmware's
protocol `0x05` write path changes. The host changes only where it must carry the part's real page size
or surface a refusal. The meta repository disposes of an instrument whose question has been answered.
No other protocol is touched.

**Provenance:** Both defects were filed by the operator on 2026-09-11 with bench evidence
([gh#67](https://github.com/henols/firestarter/issues/67),
[gh#68](https://github.com/henols/firestarter/issues/68)) and were tracked by no milestone until this
one. Both were reproduced on a **W29C020** — Leonardo, Rev 2.0-class shield, firmware `3.0.0b22`,
host `3.0.0b38`. That part's derived page size is *correct*, which is what isolates WRITE from PAGE.

## Decisions taken at activation (operator, 2026-09-15)

| | Decision |
|---|---|
| **D-1** | **Silent corruption is the milestone.** Both defects report `successful` while destroying data. Whatever the fix shape, the non-negotiable outcome is that a write never claims success over bytes it erased. |
| **D-2** | **Refusing is an acceptable fix.** Read-modify-write is not assumed. A firmware that declines an unsafe partial write with a clear error resolves WRITE-01 — losing the operation is strictly better than losing the chip. |
| **D-3** | **The page size comes from the database, not a second derivation.** The real page is already generated as `programming.infoic_page_size_raw`. Replacing one wrong derivation with another is not a fix. |
| **D-4** | **Bench validation on real silicon is required.** Both issues carry hardware evidence; the fixes must too. A green native test is not sufficient for a defect that was found on a bench. |
| **D-5** | **The stable firmware channel is out of scope.** `/releases/latest` serves 2.0.6 while current firmware is `3.0.0b30`. That is an operator-gated release decision, not phase work. |

## v1 Requirements

### WRITE — a write never destroys what it was not asked to change (gh#68)

- [ ] **WRITE-01**: A partial or unaligned write to a protocol `0x05` part either preserves every byte
      of the touched physical page that was not part of the write, or refuses the operation with a
      named error and leaves the device unchanged. Which of the two is a design decision, not a
      requirement — D-2 permits either.
- [ ] **WRITE-02**: No protocol `0x05` write reports `successful` when bytes outside the requested
      address range were erased. If the operation cannot guarantee that, it must not claim success.
- [ ] **WRITE-03**: The behaviour is demonstrated on real silicon in **both** loss directions — bytes
      before the start address and bytes after the end — on a part whose derived page size is already
      correct, so the result isolates this defect from PAGE-01.

### PAGE — the firmware uses the part's real page size (gh#67)

- [x] **PAGE-01**: The page size used by the protocol `0x05` write path is the part's recorded page
      size from the chip database, not a value derived from the device's total size.
- [x] **PAGE-02**: For **all 27** protocol `0x05` parts, the page size the firmware uses equals the
      part's recorded real page. This is measured across the whole set, not asserted for the 9 known
      to be wrong — a fix that corrects those 9 while breaking one of the other 18 is not a fix.
- [ ] **PAGE-03**: A contiguous multi-page write to one of the 9 previously under-sized parts reads
      back byte-identical on real silicon. **Status (2026-09-15):** the software half is landed and
      measured — see `.planning/v1.39/194-page-size-27-row-record.md` for the evidence-class split.
      A no-regression bench write on `W29C020` (one of the 18 already-correct parts, chosen because
      both gh#67 and gh#68 were originally reproduced on it) is now recorded in
      `.planning/v1.39/194-w29c020-bench-transcript.md`: chip-ID-confirmed, this phase's firmware
      and host, a 2048-byte / 16-page pattern, byte-identical read-back. That run proves the fix did
      not regress an already-correct part. It does not and cannot prove any of the 9 were fixed,
      because `W29C020` was never wrong. The hardware leg for the 9 stays OPEN per D-11: 0 of 9 on
      hardware, 9 of 9 on the database comparison, until the ordered `W29C512` arrives and a bench
      write on one of the 9 is read back.

### INSTR — the adoption instrument answers a live question, or is retired (v1.38 carry-over)

- [ ] **INSTR-01**: `tools/adoption/pypi_version_share.sh` either measures a question with a named
      consumer, or is removed. Either way the disposition is recorded with its reason.
- [ ] **INSTR-02**: No document describes the instrument as gating a claim that has already fired. The
      seed, `CLAUDE.md` and any note pointing at it agree with the chosen disposition.

## Out of Scope

| Item | Reason |
|---|---|
| Cutting a stable firmware release | D-5. Whether stable users move off 2.0.6 is an operator-gated release decision. |
| Read-modify-write specifically | D-2. RMW is one possible shape for WRITE-01; refusing is another. The requirement fixes the outcome, not the mechanism. |
| The other 12 protocols | Scope is `0x05`. If the same defect class exists elsewhere it is filed, not fixed here. |
| The 999.x backlog | 17 backlog phase directories stay untouched. |
| Re-auditing the slug claim | Done, recorded, and its consequences are documented in `.planning/notes/gitmodules-archaeology-trap.md`. |

## Traceability

| Requirement | Phase | Status |
|---|---|---|
| WRITE-01 | Phase 195 | Pending |
| WRITE-02 | Phase 195 | Pending |
| WRITE-03 | Phase 195 | Pending |
| PAGE-01 | Phase 194 | Complete |
| PAGE-02 | Phase 194 | Complete |
| PAGE-03 | Phase 194 | Pending (hardware leg OPEN per D-11) |
| INSTR-01 | Phase 196 | Pending |
| INSTR-02 | Phase 196 | Pending |

**Coverage:**

- v1 requirements: 8 total
- Mapped to phases: 8
- Unmapped: 0 ✓

---
*Requirements defined: 2026-09-15*
*v1.38's requirements are recoverable at `git show 77a60b53:.planning/REQUIREMENTS.md` — this file is
replaced per milestone, the convention since v1.9.*
