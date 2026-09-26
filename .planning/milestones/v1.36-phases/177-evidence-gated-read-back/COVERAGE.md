No external API integration: this phase touches the `dev test` host engine's
fingerprint read-back gate (`firestarter_app/firestarter/chip_test.py`), the
frozen-hash fixture registry (`firestarter_app/tests/fixtures/`), and one
planning seed (`.planning/seeds/dev-test-adaptive-sequencing.md`) — no new
network call, no new external service, and no new runtime dependency (HYG-02).
