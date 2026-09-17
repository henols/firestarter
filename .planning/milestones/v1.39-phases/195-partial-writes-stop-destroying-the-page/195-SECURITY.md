---
phase: "195"
slug: "partial-writes-stop-destroying-the-page"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-16"
---

# Phase 195 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: `register_authored_at_plan_time: true` — all five plans
(`195-01` … `195-05`) carried a `<threat_model>` block. The auditor was not spawned:
ASVS level 1 with `threats_open: 0` short-circuits to the file write, and L1 grep-depth
verification is sufficient at that level.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| CLI arguments to the host predicate | The `-a` address string and the payload path are operator-supplied and reach the predicate as control inputs, not merely as data | address string, filesystem path |
| Resolved wire dict to the host predicate | The page size may originate in a user override file that never passed the database generator's validator | `page_size`, `algorithm` |
| Host to serial to the firmware JSON parser | `address` and `page_size` cross the wire; the firmware never receives the total payload length, so it cannot reason about the write as a whole | JSON command frame |
| Chunk N to chunk N+1 | The firmware advances its own address between chunks; an aligned chunk is not evidence that its successor is aligned | per-chunk `address`, `data_size` |
| Firmware guard to the silicon | A page load cannot be aborted once bytes are loaded; everything after the first byte load is unrecoverable | register writes to the bus |
| Typed exception to the operator's terminal | An arm placed below the generic family arm is unreachable, so the operator would see a generic prefix instead of the chip-naming refusal | refusal message |
| Native stub recorder to the assertion | A saturated recorder silently truncates, which would make a count assertion pass on missing data | recorded bus writes |
| Firmware source to the host gates that scan it | Two host test modules read firmware paths and fail open when a path moves | source paths |
| Generated artefact to a hand edit | The chip database, `messages.py`/`messages.h`, and `VALIDATED-EPROMS.md` are generated; only the ledger's Notes section survives regeneration | generated files |
| Meta repository to its submodules | A gitlink advanced from a dirty tree records a commit that does not contain the work | gitlink SHAs |
| Operator testimony / serial node to the bench transcript | The shield revision cannot be probed and node numbers shuffle across a replug, so neither is an identity | bench evidence |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-195-01 | Tampering | A page cycle driven over a partially loaded page | critical | mitigate | Firmware guard at `firestarter_fw/src/proms/flash_5v_page.cpp:87-95` refuses before the `for` loop; host guard `require_page_alignment` at `firestarter_app/firestarter/page_size_gate.py:136-183`. Refusal tests assert `RESPONSE_CODE_ERROR` **and** `bus_recording_count() == 0` | closed |
| T-195-02 | Repudiation | A write reporting success over bytes it erased | high | mitigate | The guard raises rather than returning a status. `test_page_alignment_error_renders_through_cli_write_command` asserts `exit_code != 0` and no generic prefix | closed |
| T-195-03 | Tampering | A guard that fails open on an unresolvable input | high | mitigate | `test_write_eprom_unparseable_address_refuses_before_operation_context` and `..._missing_payload_file_...` both require a raise | closed |
| T-195-04 | Elevation of privilege | A refusal wired into the CLI layer only | high | mitigate | Called at the operator layer in `eprom_operations.py:2010` and `cli_handlers.py:768`, both ahead of `_operation_context` / port open | closed |
| T-195-05 | Tampering | An unvalidated page size from a user override file | medium | mitigate | `_ACCEPTED_PAGE_SIZES` (`page_size_gate.py:60`) enforces the firmware's accepted set — see T-195-19 | closed |
| T-195-06 | Repudiation | An unreachable rendering arm | medium | mitigate | `test_page_alignment_error_renders_verbatim_with_no_generic_prefix` | closed |
| T-195-07 | Tampering | A hand edit to a generated artefact | medium | mitigate | `messages.py` / `messages.h` verified clean in `git status` in both sub-repos | closed |
| T-195-08 | Denial of service | A firmware page-staging buffer exhausting RAM | high | accept | See Accepted Risks R-01 | closed |
| T-195-09 | Information disclosure | New host against old firmware still corrupting silently | high | accept | See Accepted Risks R-02 | closed |
| T-195-10 | Tampering | npm / pip / cargo installs | high | accept | See Accepted Risks R-03 | closed |
| T-195-11 | Tampering | A chunk-boundary page destroyed inside the requested range | critical | mitigate | `test_5v_page_write_execute_refuses_unaligned_second_chunk` drives the handler twice with an advancing address, requiring error + zero recording on both | closed |
| T-195-12 | Repudiation | A boundary assertion passing vacuously on a truncated recording | high | mitigate | 13 `bus_recording_saturated` assertions in the native module | closed |
| T-195-13 | Tampering | A guard written with a conjunction instead of a disjunction | high | mitigate | Source uses `\|\|` (`flash_5v_page.cpp:87`); three separate refusal cases — start only, length only, both | closed |
| T-195-14 | Denial of service | A zero-length chunk refused, regressing the empty-input path | medium | mitigate | Explicit acceptance case asserting OK and zero recording for `data_size == 0` | closed |
| T-195-15 | Repudiation | A host gate that scans nothing but still reports a pass | medium | mitigate | Both firmware-source-scanning modules run explicitly with a required non-zero test count (`195-02-SUMMARY.md`) | closed |
| T-195-16 | Repudiation | A pre-existing red suite read as this phase's regression | medium | accept | See Accepted Risks R-04 | closed |
| T-195-17 | Denial of service | Firmware RAM consumed by a staging buffer | high | mitigate | No buffer allocated (D-01 chose refusal). Measured flash delta +64 B on both `uno` and `leonardo`, from builds that actually relinked | closed |
| T-195-18 | Tampering | npm / pip / cargo installs | high | accept | See Accepted Risks R-03 | closed |
| T-195-19 | Tampering | An unvalidated page size from a user override file | high | mitigate | `_ACCEPTED_PAGE_SIZES = {1,2,4,8,16,32,64,128,256,512}` — non-zero, power of two, ≤ 512, matching the firmware validator, one test leg per rejected class | closed |
| T-195-20 | Repudiation | A refusal message that misstates why it refused | medium | mitigate | Two separate format constants (`_REFUSAL_FORMAT`, `_INVALID_PAGE_SIZE_FORMAT`); the offending value is named | closed |
| T-195-21 | Tampering | A guard hardened into refusing a zero-length write | medium | mitigate | `test_write_eprom_zero_byte_payload_reaches_operation_context` pins the accepting direction | closed |
| T-195-22 | Spoofing | A test fixture absorbing a row from the user's own configuration | medium | mitigate | Every database built with `EpromDatabase(skip_local_override=True)`; `test_module_reads_the_database_with_the_no_local_override_convention` asserts it | closed |
| T-195-23 | Repudiation | Criterion 4 satisfied by a vacuous re-check | high | mitigate | `test_dev_test_region_matrix_over_all_27_protocol_0x05_rows` partitions and counts over rows selected by `FLASH4_PROTOCOL_ID`, not transcribed | closed |
| T-195-24 | Tampering | A hand edit to the generated chip database | medium | mitigate | `chip_database.json` verified clean in `git status` | closed |
| T-195-25 | Elevation of privilege | A predicate widened past protocol 0x05 | medium | mitigate | Both predicates key on `FLASH4_PROTOCOL_ID`; `test_require_page_alignment_another_algorithm_never_touches_filesystem` pins the no-op | closed |
| T-195-26 | Denial of service | `dev test` silently broken on parts nobody notices | medium | accept | See Accepted Risks R-05 | closed |
| T-195-27 | Tampering | npm / pip / cargo installs | high | accept | See Accepted Risks R-03 | closed |
| T-195-28 | Repudiation | The derived third loss direction presented as observed | high | mitigate | `195-partial-write-refusal-record.md:55` labels direction 3 "Derived from source and a datasheet quotation and never observed" | closed |
| T-195-29 | Repudiation | A record claiming the phase preserves untouched bytes | high | mitigate | Zero occurrences of the preserving claim in the record; it states the refusal shape chosen and the measurements that ruled out RMW | closed |
| T-195-30 | Tampering | A hand edit to the generated ledger silently discarded | medium | mitigate | Edit confined to `## Notes` in `VALIDATED-EPROMS.md`, the one section preserved verbatim; write-then-check round trip | closed |
| T-195-31 | Repudiation | A capability loss that disappears when the phase seals | high | mitigate | Three pending todos verified present with frontmatter: `host-side-page-alignment-splicing.md`, `protocol-0x05-write-override-flag-output-contract.md`, `dev-test-write-region-rounds-to-page-size.md` | closed |
| T-195-32 | Repudiation | A public claim that a defect is fixed when nothing has shipped | medium | mitigate | Comment scoped to the measured scope correction; claims no fix, no release, attaches no label, closes nothing | closed |
| T-195-33 | Tampering | A gitlink advanced from a dirty or wrong-branch tree | high | mitigate | Verified at audit: both gitlinks equal sub-repo HEAD (`fw b32d1adf`, `app 2acf5d33`), both on `v1.39-protocol-0x05-write-correctness`, both tracked-porcelain empty | closed |
| T-195-34 | Repudiation | A requirement marked Complete ahead of its evidence | high | mitigate | Plan 04 flipped nothing; plan 05 owns the flips after the bench transcript | closed |
| T-195-35 | Tampering | npm / pip / cargo installs | high | accept | See Accepted Risks R-03 | closed |
| T-195-36 | Spoofing | A part identified by its printed marking | high | mitigate | Chip id read and compared against the shipped database row before any write (5 transcript references) | closed |
| T-195-37 | Spoofing | A serial node assumed to be the same board | high | mitigate | Controller identity confirmed through sysfs on the named port before any operation and after each flash | closed |
| T-195-38 | Tampering | A bench run exercising a different checkout than the one reverted | high | mitigate | The installed package's resolved path printed and required to lie under the working tree before the revert | closed |
| T-195-39 | Tampering | A residual revert making the post-fix leg a second pre-fix leg | high | mitigate | Both trees restored and porcelain emptiness asserted at the end of task 2 and the start of task 3 | closed |
| T-195-40 | Repudiation | A post-fix refusal presented as proof the loss existed | high | mitigate | Loss proved only by the reproduction leg against a pre-fix build; two distinct build attribution lines recorded | closed |
| T-195-41 | Repudiation | A refusal that still touched the device | critical | mitigate | Full read-back hashed against the post-fix baseline after both refusals; `sha256` match is the sole basis for the device-unchanged claim | closed |
| T-195-42 | Repudiation | A derived direction recorded as observed | medium | mitigate | The interior direction's result recorded either way, with the reason | closed |
| T-195-43 | Repudiation | A requirement marked Complete beyond its evidence | high | mitigate | Verified at audit: `WRITE-01/02/03` checkboxes `[x]` and the traceability table rows `Complete` agree | closed |
| T-195-44 | Tampering | A write run with the blank-check-skip flag | high | mitigate | Zero `write … -b` invocations in the bench transcript | closed |
| T-195-45 | Denial of service | A recursive ignored-file clean destroying planning state | high | mitigate | Scratch removed by explicit path only; recursive clean prohibited outright | closed |
| T-195-46 | Tampering | npm / pip / cargo installs | high | accept | See Accepted Risks R-03 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above `workflow.security_block_on` (high) count toward `threats_open`*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-01 | T-195-08 | No staging buffer is allocated. A 512-byte buffer leaves 142 bytes of remaining RAM on `uno` for the entire call stack, which is why D-01 chose refusal over firmware read-modify-write | Phase 195 plan 01 (D-01) | 2026-09-16 |
| R-02 | T-195-09 | A new host against old firmware still corrupting silently is deliberately out of scope, already filed as a pending skew todo by Phase 194. The host cannot gate on firmware version because the version probe truncates the prerelease suffix | Phase 195 plan 01 | 2026-09-16 |
| R-03 | T-195-10, T-195-18, T-195-27, T-195-35, T-195-46 | No plan in this phase installs a package or changes a dependency manifest, so no package-legitimacy checkpoint is required | Phase 195 plans 01–05 | 2026-09-16 |
| R-04 | T-195-16 | The seventeen failures in the flash-path record-sync module are already dispositioned by Phase 194. Plan 02 pins the failing module list and the passed-count floor instead of requiring a fully green suite | Phase 195 plan 02 | 2026-09-16 |
| R-05 | T-195-26 | Per D-12 the `dev test` region is not changed here. The consequence is asserted and counted so it stays visible, and plan 04 filed the region-rounding proposal rather than folding a ledger-affecting change into a safety fix | Phase 195 plan 03 (D-12) | 2026-09-16 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-16 | 46 | 46 | 0 | /gsd-secure-phase (orchestrator, L1 short-circuit) |

---

## Related Findings Outside This Register

`WR-01` (code review `195-REVIEW.md`) — `require_page_alignment` accepts a negative
address string as falsely "aligned", and `simple_strtoul` drops the sign, so the write
silently lands at address 0. Dispositioned at the Phase 195 UAT checkpoint as accepted
debt and filed as
`.planning/todos/pending/2026-09-16-reject-negative-write-start-address.md`.

It is **not** entered in this register: it is a wrong-destination defect, not a
partial-page-destruction one. Address 0 is page-aligned for a length already proven to be
a whole number of pages, so it erases nothing outside the range it writes and crosses none
of the boundaries above in a way this phase's threat model covers. It remains a real gap
in write-address validation and is tracked as such.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-16
