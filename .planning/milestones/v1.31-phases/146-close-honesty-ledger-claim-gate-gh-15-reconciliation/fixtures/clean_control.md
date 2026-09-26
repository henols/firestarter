<!-- test fixture for 146-check-claims.py — NOT a closing artifact — never add to _DEFAULT_TARGETS -->

Phase 146's honesty ledger states, class by class, what this milestone's 27C write path has established
and what it has not. The per-byte program loop and its parameter table are bench-validated on one part,
one controller and one shield revision; every other 27C family in the database is skipped-with-reason,
and each reason is recorded rather than implied.

The evidence ceiling this cycle is a hardware one. The program rail is held at the ~6.25 V program-VCC
ceiling this shield can reach, so the silicon-margin the datasheet method assumes is narrower here than
that method presumes. No datasheet-conformance claim is made in either direction: the claim this
milestone is permitted is fidelity of shape, attested by the native suites and measured once on a bench.
