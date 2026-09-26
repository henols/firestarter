No external API integration: this phase changes the `dev test` host engine's UV slot-write path
(`firestarter_app/firestarter/chip_test.py` — the monotonicity witness, the inline positional
`FLAG_SKIP_BLANK_CHECK` at the write call site, and the execution-time UV blank-check verdict
adjudication), the shared test double (`firestarter_app/tests/fake_chip.py`), the frozen-hash
fixture registry and re-key ledger (`firestarter_app/tests/fixtures/`), one new test module, and
`.planning/` records — no new network call, no new external service, no new SDK and no new runtime
dependency. The only wire it touches is the existing 250000-baud USB serial link to the Arduino,
using an existing flag bit (`0x08`) that already exists identically on both sides.

The deterministic detector agrees: `node gsd-core/bin/lib/api-coverage.cjs --json` over this phase's
ROADMAP section plus the four PLAN bodies returned `{"detected":false,"signals":[]}` — no `skipped`
key, so it examined real input and reached a real negative.
