No external API integration: this phase touches the `dev test` host engine's
status/verdict vocabulary and the ATTR-06 rail-reading disclosure
(`firestarter_app/firestarter/chip_test.py`, `firestarter_app/firestarter/diagnostic_report.py`,
`firestarter_app/firestarter/submit.py`, `firestarter_app/firestarter/cli_handlers.py`), the
frozen-hash fixture registry (`firestarter_app/tests/fixtures/`), and two `.planning/`
documentation corrections (`REQUIREMENTS.md`, `research/FEATURES.md`) — no new
network call, no new external service, and no new runtime dependency.
