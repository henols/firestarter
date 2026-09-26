# Phase 175 — API Coverage Declaration

**Phase:** 175-structural-sentinel-over-derive-plan
**Declared:** 2026-09-04
**Declared by:** gsd-planner, at plan time

No external API integration: test-only sentinel over an in-repo Python module.

## Reasoning

The deterministic external-API detector was not run by the orchestrator, and the planner's own
review of the phase scope finds nothing for it to detect. This phase adds Python test modules,
one committed JSON data artifact and one generator script, all inside `firestarter_app`, all
reading `firestarter.chip_test.derive_plan`, `firestarter.chip_test.run_plan` and
`firestarter.cli_handlers._resolve_write_scope` — in-repo Python functions.

Measured properties of the work this phase adds, all verified in the py3.11 CI-replica venv
during research and re-confirmed at plan time:

| Surface | Present in this phase | Evidence |
|---|---|---|
| External HTTP / network call | none | `run_plan`'s only outbound calls go to an injected `unittest.mock.Mock(spec=[...])`; the engine never imports `hardware.py` (`chip_test.py:1615-1616` docstring) |
| Third-party SDK or client library | none | HYG-02 is milestone-wide: stdlib + pytest only. `## Standard Stack` in `175-RESEARCH.md` names `pytest`, `dataclasses`, `unittest.mock`, `json`, `copy`, `collections`, `argparse`, `subprocess` |
| Package-manager install | none | Package Legitimacy Audit in `175-RESEARCH.md` records zero packages, zero `[ASSUMED]`, zero `[SUS]`, zero `[SLOP]` |
| Serial port / hardware | none | Nothing in this phase opens a port; the operator is a `Mock` |
| Filesystem writes outside the repo | none | `run_plan`'s `tempfile` use is audited clean: 0 new entries in `$HOME`, `~/.firestarter`, the CWD and the system temp dir after a full 1,354-plan sweep |
| Credentials, secrets, auth surface | none | No auth surface exists anywhere in `firestarter_app` |

A coverage matrix would have no rows. This reasoned declaration stands in its place for the
`verify:pre` seal-time gate.
