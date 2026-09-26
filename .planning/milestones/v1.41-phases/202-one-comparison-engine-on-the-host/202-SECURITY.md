---
phase: "202"
slug: "one-comparison-engine-on-the-host"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-24"
---

# Phase 202 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: **authored at plan time**. All five PLAN.md files (`202-01` to `202-05`) carry a
`<threat_model>` block. This audit therefore checked the mitigations named there and did not build a
register retroactively. No SUMMARY.md raised a `## Threat Flags` entry.

The audit ran retroactively on 2026-09-24, after phases 203 to 207.1 had also landed on the same
milestone branch. The evidence below was taken from the **current** tree (`firestarter_app` at
`5302f63`, branch `v1.41-verification-to-host`), not from the tree as it stood when 202 closed. The
202 mitigations are still present and green after the later phases.

This is a host-only phase. Its attack surface is a local single-user CLI. The only input that is
untrusted in practice is the serial byte stream from a device that may be faulty, mis-flashed or
mis-wired. The threats are mostly about **honesty of the verdict**: a fault must not read as a
match, a partial compare must not read as a whole one, and an abort must not read as a pass. There
are also denial-of-service bounds on memory, output and runtime.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| firmware to host (serial) | Chunk payloads, chunk lengths, frame ids and error frames come from a device the host does not control. A deliberate abort and a genuine timeout are identical on the wire. | Raw chip bytes and protocol frames. Not sensitive, but their size and content are adversarial-in-practice. |
| host to firmware (ack channel) | The host aborts a read by withholding an ack. The firmware's ack wait is the only thing that observes this. | Ack frames. |
| user to CLI | Chip name, file path, `--address` and `--size` come from the local operator's shell. | Local operator input. |
| host library to `dev test` | `Fingerprint` crosses from this phase's code into phase 206's contract. DEVTEST-03 forbids its meaning drifting. | An in-process classification object. |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-202-01 | Denial of Service | `compare.py` accumulator and `classify_streamed` finalisation | high | mitigate | Streaming `CompareAccumulator.feed` keeps no device-sized structure. Finalisation reads fixed-width counters only. Pinned by `tests/test_compare.py::TestCompareAccumulatorPeakAllocation`: a 1 MiB traced-peak ceiling across four fault patterns (`test_peak_allocation_under_ceiling`), plus flatness across two device sizes (`test_peak_allocation_flat_in_device_size`). | closed |
| T-202-02 | Denial of Service | `render_compare_lines` output volume | medium | mitigate | `MAX_RETAINED_RANGES = 64` (`firestarter/compare.py:33`), with exact `extra_ranges`/`extra_bytes` counters and a single tail line. Pinned by `TestCompareAccumulatorRangeCap`, `TestCompareAccumulatorRangeCapBoundary`, `TestCompareAccumulatorAlternatingPrecision` and `TestRenderCompareLines::test_extra_ranges_tail_line`. | closed |
| T-202-05 | Denial of Service | `verify_eprom` runtime on a 512 KiB part | medium | mitigate | An equality fast path per chunk, before the per-offset loop. Pinned by `TestCompareAccumulatorRuntime` (under 1 s all-matching, under 8 s all-differing) and by the structural check `TestCompareAccumulatorFastPathStructure::test_fast_path_precedes_per_offset_loop`. | closed |
| T-202-04 | Spoofing | Abort-vs-fault discrimination in `_drive_region_compare` | high | mitigate | A four-condition acceptance in `firestarter/eprom_operations.py` (`_drive_region_compare`, line 2724 onward). The intent flag `_read_abort_intended`, a recorded `_read_abort_stopped_at`, `last_firmware_error_code == MSG_ERR_TIMEOUT`, and elapsed time `<= READ_ABORT_ACCEPTANCE_WINDOW_S` (3.0, line 123) must all hold. Each condition is shown to be load-bearing by a negative test in `tests/test_eprom_operations.py::TestVerifyEpromReadAbort`: `test_non_timeout_error_after_intended_abort_returns_two`, `test_timeout_on_full_path_with_no_abort_requested_returns_two` and `test_timeout_outside_the_acceptance_window_returns_two`. Two further tests pin the window edges (`..._just_inside_...` and `..._exactly_at_...`). | closed |
| T-202-06 | Repudiation | `Fingerprint` meaning drifting across the refactor | high | mitigate | `tests/test_compare.py::TestClassifyFingerprintCorpus`: whole-object equality between the streamed path and an independently transcribed batch reference. It covers all five buckets (`test_corpus_covers_all_five_buckets`) and at least 12 rows (`test_corpus_has_at_least_twelve_rows`). | closed |
| T-202-07 | Spoofing | A prefix verdict presented as covering the whole region | medium | mitigate | `render_compare_lines` always appends the D-14 bucket line, carrying the compared count, the region total and the compared address span. `finalise()` always populates the fingerprint. Pinned by `TestRenderCompareLines::test_bucket_summary_line_exact_text` and `..._is_last_and_exactly_one`, and by `TestFinaliseAlwaysClassifies`. | closed |
| T-202-08 | Repudiation | An aborted compare reported as a clean pass | high | mitigate | Exit 0 only when `result.total > 0 and result.bad == 0 and result.compared == result.total` (`eprom_operations.py`, in `_drive_region_compare`). After a stop the read loop skips `progress.update()`, so the bar closes at the compared count. Pinned by `TestVerifyEpromReadAbort::test_zero_length_region_never_reports_a_clean_pass`, `test_first_byte_mismatch_aborts_after_one_chunk_and_reports_a_range` and `test_last_byte_mismatch_completes_normally_not_as_an_abort`. | closed |
| T-202-09 | Denial of Service | A wedged port after an aborted read | medium | mitigate | `_main_phase_read_data` drains after the stop (`continue`, never raise), so the terminating MAIN/ERROR frame is still read and teardown runs. Pinned by `TestVerifyEpromReadAbort::test_default_abort_stops_acking_after_the_mismatching_chunk`, which asserts that a second `verify_eprom` on the same operator returns 0 afterwards. | closed |
| T-202-10 | Spoofing | A transport or hardware fault presented as a chip mismatch, or the reverse | high | mitigate | A three-way int verdict (0/1/2) that bypasses the typed-error-to-exit-1 conversion. Pinned in `tests/test_cli_handlers.py` by the verify and blank happy, mismatch and setup-failure tests, by `test_map_typed_errors_never_exits_the_process_directly`, and by `test_service_setup_failure_route_to_exit_2_names_its_own_message` and `test_usage_error_also_exits_2_but_never_reaches_the_operator`, which tell an exit 2 apart from a Click usage error by its message. | closed |
| T-202-11 | Tampering | A region-scoped compare silently covering less than it claims | high | mitigate | `cli_handlers._region_refusal_exit_code` refuses (exit 2) before the port opens in two cases: an explicit `--size` larger than the input file, and a region running past the chip's end. Pinned by `test_verify_refuses_size_larger_than_input_file_before_opening_the_port`, `test_region_past_chip_end_is_refused_before_opening_the_port`, and the address-alone boundary tests (`..._past_chip_end_...`, `..._exactly_at_chip_end_...`, `test_blank_address_alone_at_last_valid_byte_is_not_refused`). | closed |
| T-202-12 | Information Disclosure | Region options widening a read beyond the declared region | low | mitigate | The existing `parse_address`/`parse_size` are reused, not re-implemented. Pinned by `test_region_scoped_verify_composes_a_command_dict_bounding_exact_region`, which asserts that the wire start and end bound exactly the requested region. | closed |
| T-202-03 | Tampering | `input_file` path passed to `verify` | low | accept | See R-01. | closed |
| T-202-SC | Tampering | Package-manager installs | low | accept | See R-02. | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-01 | T-202-03 | A surface that existed before this phase, unchanged by it. A local single-user CLI reads a path the invoking user supplied. The user can already read any file their own account can read, so no privilege boundary is crossed. | plan 202-01 and 202-05 threat models (disposition `accept`) | 2026-09-20 |
| R-02 | T-202-SC | No install task exists in this phase. RESEARCH.md § Package Legitimacy Audit records zero new package names. Every library used (`tracemalloc`, `time`, `ast`, `inspect`) is stdlib or already declared in `pyproject.toml`. | plan 202-01 to 202-05 threat models (disposition `accept`) | 2026-09-20 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-24 | 13 | 13 | 0 | `/gsd-secure-phase` orchestrator (L1, short-circuit: register authored at plan time, 0 open) |

Evidence run on 2026-09-24 against `firestarter_app` `5302f63`, using `pytest -o addopts="" -q`:

- `tests/test_compare.py`, `TestVerifyEpromReadAbort` and `TestOrdinalsNeverSentByVerifyOrBlank`: **84 passed**.
- `tests/test_cli_handlers.py` filtered to verify, blank, region, refusal, exit, usage and map_typed: **56 passed**.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-24
