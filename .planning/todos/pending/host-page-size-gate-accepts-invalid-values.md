---
type: todo
created: 2026-09-15
source: 194-REVIEW.md (Phase 194 code review, Warning 1)
area: firestarter_app
resolves_phase:
---

# Host page-size gate accepts values the firmware rejects

`firestarter_app/firestarter/page_size_gate.py`'s `require_page_size` refuses only
on a falsy page size. The firmware's `flash_5v_page_mask`
(`firestarter_fw/src/proms/flash_5v_page.cpp`) additionally requires the value to be
a power of two no greater than `FLASH_5V_PAGE_SIZE_MAX` (512).

So the two refusal layers disagree about which page sizes are valid. A page size of
96, 1024 or 65535 passes the host gate and fails deep inside the firmware state
machine instead of at the named, pre-serial refusal the host layer exists to provide.

**Why the shipped database does not hit this:** `tools/build_db.py` carries a
whole-database validator that pins every emitted `page_size` to the same accepted set
the firmware enforces, and raises rather than writing a database if any value fails.

**Where it bites:** `~/.firestarter/database.json` user overrides never pass through
`build_db.py`, so nothing checks them before they reach the wire dict.

**Not a data-loss risk.** The firmware still refuses and performs zero register
writes — D-07's two-layer design working as intended. The cost is the quality of the
failure, not its safety.

**Suggested fix:** extend `require_page_size` to apply the same power-of-two and
range test, keeping it a pure predicate, and add a test module leg per rejected class
(non-power-of-two, above ceiling, transport-saturated). `page_size_gate.py`'s own
docstring already states the intended contract: "Only an exact, database-sourced page
size is safe, and there is no fallback value that is ever safe to guess."

Deliberately NOT fixed inside Phase 194: every plan was complete and green when the
review surfaced this, and the change is a behavior change to shipped host source
outside any plan's contract.
