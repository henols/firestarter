---
created: 2026-09-21
source: 203-RESEARCH.md §4.2 (surfaced during Phase 203 planning; deliberately not folded)
resolves_phase:
severity: major
---

# `check_eprom_blank`'s SRAM/FRAM short-circuit is inert on the CLI path

`firestarter_app/firestarter/eprom_operations.py:2639-2648` short-circuits the blank check for
SRAM/FRAM parts by reading `electrical-type` and `protocol-id` from the programmer wire dict.
**The wire dict `resolve_chip` returns carries neither key.** It carries `algorithm`, `flags`,
`memory-size`, `pin-count`, `vpp_mv`, `pulse-delay` and three conditional keys — nothing else.
The short-circuit therefore never fires on the CLI path: both lookups miss, the branch evaluates
falsy, and an SRAM part gets the full blank read it was written to skip.

Probed during Phase 203 research; the probe **refuted** the assumption rather than confirming it.

**The repository already knows this failure class.** `firestarter_app/firestarter/sdp_capability.py:186-195`
hard-fails on a missing wire-dict key with a comment naming this exact bug as its reason. That
module chose `raise KeyError` over `.get(key, default)` precisely so a future key rename could not
silently reintroduce a vacuous predicate. The `check_eprom_blank` short-circuit predates that
lesson and never got it.

**Why it was not folded into Phase 203.** It is a `blank` defect; no WRITE requirement covers it,
and folding it would have widened an already-large phase. 203-RESEARCH.md recommended filing rather
than folding, and the planner agreed. Phase 203's own new predicate is protected against joining
this failure class by an AST test asserting it reads only `algorithm` and `flags` — so the fix here
is isolated, not a prerequisite for anything 203 builds.

**Blast radius.** The observable symptom is a slow `blank` on an SRAM/FRAM part, not a wrong answer:
the read returns whatever the part holds and the comparison is honest about it. The cost is time and
an unnecessary port session, not a false verdict. That is why this is major rather than critical.

Suggested fix: decide what the predicate should key on — `algorithm` against the four SRAM protocol
ids is the shape Phase 203's guard uses and the one the wire dict can actually answer — then make
the missing-key case `raise KeyError` in the `sdp_capability.py` style rather than defaulting. Add a
test that drives the short-circuit through a real `resolve_chip` wire dict, not a hand-built one; a
hand-built dict carrying `electrical-type` is exactly what let this survive.
