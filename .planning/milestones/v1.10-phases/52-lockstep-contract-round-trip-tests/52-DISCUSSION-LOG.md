# Phase 52: Lockstep Contract + Round-Trip Tests - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-02
**Phase:** 52-lockstep-contract-round-trip-tests
**Areas discussed:** Cross-repo proof mechanism, Golden-vector corpus + home, Constant-parity guard scope, CI green across both repos

---

## Cross-repo proof mechanism

### Q1 — How do we prove host-encode == firmware-decode byte-for-byte across the Python/C++ boundary?

| Option | Description | Selected |
|--------|-------------|----------|
| Shared frozen golden vectors | Canonical (payload → exact framed bytes) committed once; BOTH suites assert against the SAME bytes; transitive match; no cross-toolchain run. | ✓ |
| Independent round-trips + synced constant | Each repo self-round-trips against a manually-synced expected-bytes constant; drift-prone. | |
| Live cross-language harness | Python emits bytes piped into compiled native C++ decode (subprocess); needs both toolchains in one CI job; slow/flaky. | |

**User's choice:** Shared frozen golden vectors.
**Notes:** Constraint that shaped it — firmware tests are Unity native suites, host tests are pytest, executing in separate CI in separate repos; a live harness fights the submodule structure. → CONTEXT D-01.

### Q2 — How should the canonical golden-vector set be represented and consumed?

| Option | Description | Selected |
|--------|-------------|----------|
| Codegen into both repos (v1.2 pattern) | Canonical catalog → codegen emits C++ PROGMEM header + Python module; CI `<regen> && git diff --exit-code` drift gate. | ✓ |
| Flat hex file read at test time | Single vector file parsed at runtime by a Unity reader + a pytest loader. | |
| Hand-embedded literals, file is reference | Tests hard-code byte literals; canonical file is documentation only. | |

**User's choice:** Codegen into both repos (v1.2 pattern).
**Notes:** Investigation confirmed v1.2 uses a **vendored byte-identical** `messages.toml` + `codegen.py` in each sub-repo's `tools/catalog/`, each emitting its own artifact, each repo's CI running its own drift gate. This settles vector *home* too. → CONTEXT D-04.

### Q3 — How should each vector be exercised, and do failure cases belong in the golden set?

| Option | Description | Selected |
|--------|-------------|----------|
| Both directions + valid-only golden set | Each repo asserts encode==frame AND decode==payload per vector; negatives stay in existing per-repo suites. | ✓ |
| Both directions + negative vectors too | Golden set also carries corrupted/truncated vectors with expected outcomes. | |
| Decode-only against frozen frames | Pin only decode(frame)==payload; weaker on the encode→decode leg. | |

**User's choice:** Both directions + valid-only golden set.
**Notes:** One valid-payload set proves all four legs transitively; negative behavior already covered by `test_cobs_cmd_frame.cpp` + host `test_cobs.py`. → CONTEXT D-02, D-03.

---

## Golden-vector corpus + home

(Home settled by the codegen choice — vendored catalog per v1.2; see D-04.)

### Q4 — How broad should the corpus be beyond the ROADMAP-mandated cases?

| Option | Description | Selected |
|--------|-------------|----------|
| Mandated + COBS-boundary stress | 4 mandated cases + 253/254/255-run boundary (CR-01 class) + empty + lone-0x00 + data blocks at 512B & 1024B with all-0xFF/all-0x00. | ✓ |
| Mandated cases only | Just the 4 ROADMAP-mandated payloads at one size each. | |
| Exhaustive sweep | Boundary stress + randomized/fuzz sweep as frozen vectors. | |

**User's choice:** Mandated + COBS-boundary stress.
**Notes:** Targets the boundary class that produced the real Phase-50 CR-01 byte-drop. → CONTEXT D-05.

---

## Constant-parity guard scope

### Q5 — How to extend the parity guard, and how to handle CMD_FRAME_MAX board-variance?

| Option | Description | Selected |
|--------|-------------|----------|
| Extend existing test; pin CMD_FRAME_MAX to Uno floor | Add to skipif-guarded test_revision_constants_parity.py; assert host 512 == firmware Uno DATA_BUFFER_SIZE floor, documenting board-variance. | ✓ |
| Extend existing test; assert against both board sizes | Model 512 (Uno/uno328pb) and 1024 (Leonardo) explicitly. | |
| Flag the host 512-vs-DATA_BUFFER_SIZE mismatch first | Treat as a possible latent Leonardo bug; investigate before pinning. | |

**User's choice:** Extend existing test; pin CMD_FRAME_MAX to Uno floor.
**Notes:** `CMD_FRAME_MAX` is the only new named constant crossing the parity boundary; delimiter `0x00` and CRC8 poly `0x07` are pinned by golden vectors + KAT, not the parity test. → CONTEXT D-06, D-07.

---

## CI green across both repos

### Q6 — What does "CI green across both repos" concretely require?

| Option | Description | Selected |
|--------|-------------|----------|
| Each repo's own CI, independently | firestarter CI = Unity vectors + drift gate; firestarter_app CI = pytest vectors + parity + drift gate; no meta-level CI; lockstep by paired commits. | ✓ |
| Add a meta-level lockstep check | Meta-repo step diffs the two vendored catalogs for byte-identity. | |
| Defer CI wiring to the planner | Capture only the requirement; planner decides workflow invocation. | |

**User's choice:** Each repo's own CI, independently.
**Notes:** Mirrors the v1.2 catalog model. The declined meta-level diff is recorded as an accepted, paired-commit-mitigated risk. → CONTEXT D-08, D-09.

---

## Claude's Discretion

- Exact catalog filename/format and codegen emit shape (must match v1.2 determinism contract).
- Generated C++/Python symbol names.
- Where vector assertions live within each suite (extend `test_cobs_*` vs a new `test_lockstep_contract` suite).
- Exact representative JSON command payloads + data-block content patterns beyond the all-0xFF/all-0x00 extremes.
- Whether the CRC8 KAT reuses an existing fixture or adds a dedicated one.

## Deferred Ideas

- Meta-level cross-repo catalog-diff CI check (declined in favor of paired-commit discipline; D-09).
- Randomized/property-style fuzz sweep (separate per-repo test if ever wanted).
- WR-01 frame-level decoder deadline — behavior change, not a contract test; stays a pending todo.
- Host `CMD_FRAME_MAX` 512-vs-board-variance — judged acceptable for v1.10; revisit if a >512B Leonardo command frame becomes legitimate.
- Re-framing fw→host responses — out of v1.10 scope (ADR §4.2).
