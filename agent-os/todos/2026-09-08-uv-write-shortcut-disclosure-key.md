---
title: dev test m27c512 now passes on a non-blank UV part via FLAG_SKIP_BLANK_CHECK while firestarter write is still refused by the identical firmware, and no exported key discloses the divergence
date: 2026-09-08
priority: low
blocked_by: deferred to Phase 181 by design — RPT-A4 (plan.is_uv reaching the report as a top-level boolean, read off the single derive_plan decision) is explicitly Phase 181's, and Phase 179 judged an unrequested new exported key would grow the frozen-key surface this milestone is holding still mid-milestone.
resolves_phase: none
---

# Q5 / RESEARCH assumption A5 — the UV write-shortcut disclosure key

## What is true after Phase 179

`firestarter dev test m27c512` now passes (`overall_verdict == "PASS"`, `run_count == 2`) on a
non-blank UV part, by passing `FLAG_SKIP_BLANK_CHECK` on a proven monotonic masked write. On the
IDENTICAL part, `firestarter write -a 0x…` is still refused by the identical firmware write-init
pre-flight — the user-facing write command does not set `FLAG_SKIP_BLANK_CHECK`, and nothing in the
current report discloses that the `dev test` harness took a path the product's own write command
does not take.

`.planning/research/PITFALLS.md:236-247` (Pitfall 7) argued this divergence needs disclosure, and its
own verdict was "Both, or neither" — either export a key naming the divergence AND fix the harness to
mirror the product path, or accept the divergence explicitly and disclose it. Phase 179 took
"neither" as its working answer for THIS phase, for two reasons:

1. `write_current_source` (the per-step field Phase 179 already exports, reading
   `"probe read (tranche N/2)"` on the write step that used the flag) already discloses that the
   write was probe-masked — a triager reading a UV `PASS` report can see the write step's
   `write_current_source` field and infer the shortcut was taken, even without a dedicated key.
2. `RPT-A4` (`plan.is_uv` reaching the report as a top-level boolean, read off the single
   `derive_plan` decision, never re-derived) is EXPLICITLY Phase 181's requirement
   (`.planning/REQUIREMENTS.md`'s Report Fidelity section). A UV-shortcut disclosure key is a natural
   sibling of `plan.is_uv` — it belongs in the same phase that adds the boolean it would key off of,
   not bolted on ahead of it in Phase 179.

An unrequested exported key added in Phase 179 would also grow the frozen-key surface this milestone
is deliberately holding still mid-milestone (the blast-radius invariance harness treats every new
top-level report key as a re-key event across the frozen corpus) — a cost Phase 179's own scope
(UV-01/UV-02/UV-03) does not require paying.

## Disposition

**Deferred to Phase 181**, alongside `RPT-A4`. When Phase 181 lands `plan.is_uv`, revisit whether a
dedicated `write_flags_diverge_from_product` (or similarly-named) key is warranted, or whether
`write_current_source`'s existing probe-masked disclosure plus `plan.is_uv` together already satisfy
Pitfall 7's "Both, or neither" bar without a new key. Not resolved by this todo — filed as the
decision point Phase 181 should reach, not a specific implementation this todo prescribes.
