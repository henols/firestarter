---
title: "dev test report field audit — the four values the report computes and throws away, the three dead keys, and why `duration_s` is not an operation cost"
date: 2026-08-23
context: "/gsd-explore: operator reported the report's timings are wrong and summed meaninglessly, that many JSON fields are permanently null, and that `chip_id_actual` is derivable on a pass. All three confirmed; the sweep found four more instances of the same class."
---

# What the `dev test` report knows and does not say

Audit of `DiagnosticReport.to_dict()` against the data its own inputs carry, run
2026-08-23 from a live read of `firestarter_app/firestarter/diagnostic_report.py`
(schema 1.7) and `chip_test.py`. Every row below was read from source, not inferred.

## The operator's two rules

Stated 2026-08-22/23, and they resolve every case in this note without further
adjudication:

1. **A field nothing populates gets deleted.** Not documented, not sentinel-filled
   — deleted.
2. **A field that can carry real data gets populated with real data.** No
   provenance decoration, no confidence qualifier, no `"firmware-confirmed-equal"`
   companion key. `chip_id_actual: 0xDA08` is the whole answer.

And the corollary the operator stated directly: the long comments explaining *why*
a value is withheld are themselves the defect — "that is totally pointless since
all the data is there for us to read." The truth is in the protocol and the chip
type, not in an essay above the `None`.

## Class A — computed, then discarded

Four values the report already holds and does not emit.

| field | what is actually known | source |
|---|---|---|
| `auto_capture.chip_id_actual` | On a **passing** id check it equals `chip_id_expected`. The firmware's OK reply carries no id back, so `check_eprom_id` returns the host's own echoed `cmd_data["chip-id"]` and `_chip_id_fields` discards it as "never measured". The id **was** verified — that is what OK means. | `diagnostic_report.py:961-975`, `cli_handlers.py:2330-2355` |
| `steps[].fingerprint` | Exports **only** `classification` — a four-bucket word. The `Fingerprint` object also carries `total`, `bad`, `bad_pct` and an `evidence` dict. `"indeterminate"` is printed where *3 of 65536 bytes bad, 0.005 %* was in hand. | `chip_test.py:170-177` vs `diagnostic_report.py:_step_dict` |
| `steps[].divergence` | **Not exported at all.** `StepResult.divergence` is the read-step byte-level divergence metric (D-06), computed every multi-run read and merged across cycles — then dropped at report time. `diagnostic_report.py` mentions the word exactly once, in a comment. This is the metric credited with the AM27C020 write#1/write#2 find. | set in `chip_test.py:1285`, merged at `:1624`, never read by the report |
| `plan.is_uv` | The UV decision, made **exactly once** by `derive_plan` from `electrical-type`, measured exact at 301/301. Not in the report — so a triage reader cannot tell a UV slot run from a full-device run except through `write_coverage` prose. | `chip_test.py:568`, `is_uv_eprom` |

`fingerprint` is the sharpest of the four: the classification string is a *lossy
summary of numbers the same object is carrying*.

## Class B — dead keys, nothing populates them

| key | evidence it is dead |
|---|---|
| `voltage.vpp_mv` | No assignment anywhere in the app — the only occurrences are the dataclass default, the `NOT_MEASURED` substitution, and a comment at `diagnostic_report.py:936` conceding the console render dropped "the `vpp_mv`/`vpe_mv` standalone slots that no code path assigns". |
| `voltage.vpe_mv` | Same. |
| `banner.locked_steps` | Derived from `Plan.locked_destructive`, which is populated only on a `write_scope="none"` plan. `_resolve_write_scope` (`cli_handlers.py:2453-2456`) returns **only** `"full"` or `"partial"` — `"none"` is unreachable from every CLI path. The `Plan` docstring says so itself and calls removal "an explicitly deferred cleanup, not this phase's work" (Phase 121 D-02). |

Note the shape of the `locked_steps` case: the code already knew it was dead, wrote
that down, and shipped it anyway. That is rule 1's whole justification.

## Class C — dead counters over live events

`transport_health`'s four counters (`cobs_errors`, `crc_failures`, `retries`,
`timeouts`) all emit `"not measured"` on every run, and the module comment says a
survey "verified NONE exist" (`RESEARCH §Transport Counter Survey`).

**The events exist. The counters do not.** `serial_comm.py:_read_and_parse_lines`
already detects and `logger.warning`s two distinct re-sync events —

- `serial_comm.py:520-526` — "Magic preamble seen but length bytes not received
  before timeout — re-syncing."
- `serial_comm.py:536-541` — "Frame body truncated: expected N bytes, got M —
  re-syncing."

— plus `_decode_id_frame` returning `None`, plus the timeout path in
`get_response`. So this is rule 2, not rule 1: the increments are missing, not the
observations. These are worth having precisely because the failure they catch — a
chip "failing" because the link is dropping frames — is otherwise indistinguishable
from a real chip fault in the filed issue.

## Class D — the timings

Four separate defects, tangled.

1. **`duration_s` is not an operation cost.** `_run_step` stamps
   `time.monotonic()` around the whole step (`chip_test.py:2751-2782`), but
   `_merge_cycle_results` sets `duration_s=round(sum(durations), 3)` — the **sum
   across cycles** (`chip_test.py:1614-1625`). So `read x2` reports both reads
   added together. Its own comment says the sum is deliberate, "so `steps total`
   stays honest" — which is honest about the total at the cost of every per-step
   number meaning something different from what a reader assumes.
2. **It silently changes meaning under `--fast`.** `run_count=1` there, so the same
   key is a single-op cost on one run and a two-op sum on another, with nothing in
   the field itself to say which.
3. **`steps total` is a sum of sums.** It is neither wall-clock for the command nor
   any operation's cost. Its own comment concedes it "excludes the identity read,
   plan derivation, report write and the submit prompt" — which is the operator's
   complaint restated by the code that causes it.
4. **`steps total` is render-only.** Deliberately not in `to_dict()`
   (`diagnostic_report.py:1009-1021`), so no consumer can re-derive it and no filed
   issue carries it.

**Resolution (operator, 2026-08-23): operation cost.** The number exists to say
what the *firmware* costs to perform an operation — this is a firmware diagnostic,
not an IC characterisation. So `duration_s` becomes the per-operation cost, and the
render's sum-of-sums is replaced by a real `elapsed` that lives in `to_dict()`.

Per-byte throughput (µs/byte) was **considered and not taken**: it is the
size-comparable form, and the W27C512 root cause was expressed in exactly those
units (~1100 µs/byte → 72 s/64 KiB, see
`project_w27c512_write_slow_rca_per_byte_vpe_settle`), but the operator ruled the
report is about firmware operation cost, not chip performance. Recorded here so it
is not re-litigated as an oversight.

## The constraint that makes all of this cheap

`dedup_fingerprint` hashes exactly `chip | protocol | op=verdict:classification`
plus the `repeat_policy_tag` / `coverage_tag` discriminators
(`diagnostic_report.py:310-349`). **Not one field in Class A, B or D is in that
hash** — `duration_s` was deliberately excluded as volatile, and `chip_id_actual`,
`vpp_mv`, `vpe_mv` and `locked_steps` were never in it.

So, provided `classification` **stays in place as its own key** and the new byte
counts are added as additive siblings rather than replacing it:

- every already-filed report's `dedup_fingerprint` stays byte-identical,
- no historical `count_agreeing` group is re-keyed or reset,
- and Phase 114's GRAD-01 no-auto-graduate lock is untouched.

This is the same discipline quick tasks 260822-aq6 and 260821-wna used for their
own additive tags. Getting it wrong is the one way this work can do real damage.

## Consumer surface

- Both `[dev test]` parsers accept `schema_version` by **presence only**, never an
  exact match (a live fixture carries `"9.9-future"`,
  `tests/test_parse_devtest_issue.py:138`). A bump to 1.8 needs no parser change.
- Deletion must be **forward-only**. The frozen schema-1.2 fixtures in
  `.claude/skills/devtest-triage/fixtures/` carry `vpp_mv: 11800` and
  `"locked_steps": []`, and their headers forbid regeneration ("a current host
  build can no longer produce" that shape). Old bodies must keep parsing — the same
  PROV-04 obligation `fw_board_identity: null` already carries.
- Two skill consumers read `chip_id_actual` today and get `None` on every passing
  run: `devtest-triage/scripts/devtest_issues.py:393` and
  `devtest-rootcause/scripts/seed_debug_session.py:280`. Both improve for free when
  it is filled; neither breaks.

## Cross-references

- Backlog **999.36** — the phase this note scopes.
- `todos/pending/delete-banner-locked-steps-dead-field.md` — Class B's third row,
  split out because it is independent of the schema work.
- Backlog **999.34** / v1.33 Phase 154 — the provenance-comment sweep. Same
  underlying complaint, different surface: this note is about hedging prose in the
  *artifact*, 999.34 is about it in the *source*.
