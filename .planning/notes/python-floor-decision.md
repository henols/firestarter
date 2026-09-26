---
title: The Python floor raised to 3.11 — why, what it breaks, and the rule for the next move
date: 2026-09-12
context: v1.37 Phase 186, FLOOR-01/02/03 (D-01…D-12) — measured in the py3.11 CI-replica venv, mypy 2.3.1 and ruff 0.16.4
---

# The Python floor raised to 3.11 (FLOOR-01)

## VERDICT

**The floor is 3.11, and all four statements that assert it now name that value together:**
`requires-python = ">=3.11"` in `firestarter_app/pyproject.toml`, `[tool.ruff] target-version =
"py311"`, `[tool.mypy] python_version = "3.11"`, and the `python-version:` pin in every
`firestarter_app` CI workflow that carries one (`ci.yml` twice, `beta-release.yml` once). This
resolves the gap Phase 131 D-13 found and explicitly declined to close itself — `python_version`
had silently drifted to `"3.10"` under mypy 2.0+'s own minimum-supported-target clamp while
`requires-python` and the ruff target kept advertising `3.9`, since 2026-05-27, with nothing
catching the divergence in CI or locally.

3.11 was chosen over three measured alternatives (§1) because it is the version this project's own
CI already runs — the floor becomes proven rather than advertised — and because it buys roughly
thirteen months against its own end-of-life rather than seven weeks.

This note is required to carry, and does carry: the decision and its three rejected alternatives
with their measured grounds (§1); the evidence backing the decision, transcribed rather than
re-measured (§2); a standing rule usable without re-deriving it (§3); a successor backlog item
carrying the next deadline (§4); and the residual gap this phase leaves open, named rather than
implied (§5).

## 1. The decision, and the three rejected alternatives

**3.10 (the minimum move) — rejected.** Python 3.10 EOLs 2026-10-31. Moving the floor there would
make it end-of-life on the day it landed, would not let CI test at it (CI already runs 3.11), and
would re-fire backlog 999.27 within weeks of this phase closing rather than years from now.

**Hold 3.9 — rejected, and unreachable, not merely undesirable.** Measured this phase:
`mypy.defaults.PYTHON3_VERSION_MIN == (3, 10)` in the installed **mypy 2.3.1** — mypy cannot target
3.9 at all under the project's standing `mypy>=2.1.0,<3` pin (set by Phase 131 D-14 for the
watermark regexes). Holding 3.9 would mean abandoning that pin or adopting a second type checker,
for a runtime that itself EOL'd 2025-10-31 — the advertised floor was already a dead interpreter
before this phase touched anything.

**3.12 — rejected.** CI runs 3.11, not 3.12. Moving the floor to 3.12 would force a CI change in
the same breath as the metadata change, and would drop 3.11 users who are on a still-supported
runtime for no gain this phase needed.

**Why 3.11, specifically.** It is the version CI already executes, so raising the floor to it makes
the floor *proven*, not merely asserted in three files nobody checks against each other. It is also
what `tools/catalog/`'s codegen already needs (`tomllib`, stdlib from 3.11). And it EOLs
2027-10-31 — about thirteen months from this phase's close, against the seven weeks 3.10 would have
bought.

## 2. The evidence

All figures below are transcribed verbatim from `186-RESEARCH.md`, measured once during this
phase's research pass and never re-measured here. They are pinned to **mypy 2.3.1** and
**ruff 0.16.4** — a version bump in either tool can change them, and a reader relying on this note
after such a bump should re-measure rather than trust these numbers unchanged.

The mypy count is byte-identical at the old and new target, so raising the floor changed nothing
mypy reports:

```
# current config (python_version = "3.10"):
Found 35 errors in 15 files (checked 181 source files)

# at the new floor (python_version = "3.11"), same source tree:
Found 35 errors in 15 files (checked 181 source files)
```

`diff` of the two runs' output was `IDENTICAL`. Neither branch of this phase's own watermark policy
(ratchet down / fix a rise) fired — the `# mypy_error_watermark = 35` line in
`firestarter_app/pyproject.toml` did not move.

The reason 3.9 was unreachable, quoted from the runtime introspection this phase performed:

```
mypy.defaults.PYTHON3_VERSION_MIN == (3, 10)
```

— confirmed live in the installed mypy 2.3.1's own `defaults.py`, not merely asserted from
documentation.

The ruff consequence of moving `target-version` to `py311`, measured before any fix was applied:
**182 findings** (177 `UP045` `Optional[X]` → `X | None`, 2 `UP017` `datetime.timezone.utc` →
`datetime.UTC`, 2 `UP035` deprecated-import, 1 `I001` unsorted-imports); **190 fixes applied**
across two `--fix` passes (a second-order `F401` unused-import finding was unmasked once the first
pass rewrote a signature), with **3 sites hand-fixed** individually rather than swept, at
`firestarter/eprom_info.py:97,100,103` — plan 186-02's `SUMMARY.md` records the exact hand-fix and
its verification.

The ordering constraint, the single most reusable fact in this evidence set: the sweep is not
floor-neutral. Its `UP017` rewrite (`datetime.timezone.utc` → `datetime.UTC`) emits `datetime.UTC`,
which is itself a Python 3.11 addition. Applying the sweep before raising `python_version` produces
two new mypy errors (`Module has no attribute "UTC"`) and a false "new type errors introduced"
signal at the watermark gate — 37 against a watermark of 35. The config change must land before, or
in the same commit as, the sweep; the reverse order is the one whose intermediate-commit redness
is a false type-error signal rather than an honest, cosmetic lint backlog.

**What a 3.9/3.10 consumer actually experiences — measured, not assumed.** An unpinned
`pip install firestarter` on a 3.9 or 3.10 interpreter produces **no error and exits 0**: pip's
resolver silently walks past the newer releases whose `Requires-Python` now excludes that
interpreter and installs the newest release that still advertises a compatible floor. The quoted
refusal wording (`ERROR: Package 'firestarter' requires a different Python: 3.10.x not in
'>=3.11'`) fires only on a **pinned or exact** version request (for example
`pip install firestarter==<new-version>`), never on a bare `pip install firestarter`. The honest
statement of consumer impact is therefore: **3.9/3.10 users are pinned to the last release that
advertised the old floor, and their installs will quietly stop receiving updates — not that pip
will refuse their install.** This was measured against a local `--find-links` wheel index built
for the purpose of this research, not against PyPI directly; the underlying mechanism (candidate
filtering by `Requires-Python`) is index-agnostic, but the observation is one step removed from the
thing it describes and is recorded as such rather than as a direct PyPI measurement.

## 3. The standing rule

**The floor tracks the version CI runs; when mypy's minimum supported target rises above it, move
all four statements together.**

What enforces it: `firestarter_app/tests/test_python_floor_agreement.py`, a seven-leg, zero-comment,
dependency-free gate that fails closed the instant any one of the four statements —
`requires-python`, ruff's `target-version`, mypy's `python_version`, or any CI `python-version:`
pin — disagrees with the others, including a CI pin silently moving off the floor on its own. That
last clause is deliberate, not incidental: CI drifting to a newer interpreter while the metadata
stayed put, untested and unnoticed, is exactly the mechanism that let the divergence this note
describes survive from 2026-05-27 until this phase.

## 4. The successor: 3.11 EOLs 2027-10-31

Backlog **999.67** carries this date forward. This phase exists on schedule, ahead of its own
deadline rather than as a surprise discovered after the fact, for exactly one reason: Phase 131's
D-13 filed backlog items 999.26 and 999.27 carrying their own deadline the same way, so the
2026-10-31 EOL of Python 3.10 arrived as a tracked backlog item rather than an unannounced break.
999.67 repeats that mechanism for **2027-10-31**, Python 3.11's end of life.

The 2027-10-31 date itself is carried forward from this phase's own `186-CONTEXT.md` D-08 and was
**not independently re-verified against python.org** during this phase's research — it is recorded
as the lowest-confidence figure in `186-RESEARCH.md`'s own assumptions log. If it is wrong, 999.67
carries a wrong deadline, which is a smaller failure than carrying none, but not a nil one; whoever
next relies on it should confirm it against python.org before acting on the date alone.

## 5. The residual gap, named explicitly

`firestarter/py32_dfu.py` keeps **14** `Optional[...]` annotations, every one of them individually
suppressed with a `# noqa: UP045` (several also carrying `# noqa: UP006` for their accompanying
`Dict`/`Tuple` spellings). Ruff's autofix does not reach a suppressed site by design, and these
sites pre-date this phase — they were not introduced by it and were deliberately left untouched by
the sweep rather than swept along with everything else.

That means the new lint target's principal consequence — the union-spelling migration — is
switched off in one whole file. This is precisely the shape this phase's own D-09 rejected in the
abstract when it declined to add `UP045` to `extend-ignore` project-wide rather than absorb the
177-line sweep: a nominal rule whose consequence is silenced is a claim-shaped defect, and leaving
one file's worth of that shape standing is worth naming plainly rather than leaving implicit. It is
recorded here, not tasked — closing it would mean touching `py32_dfu.py`'s working, already-tested
DFU protocol code for a lint-only reason this phase was not chartered to take on.
