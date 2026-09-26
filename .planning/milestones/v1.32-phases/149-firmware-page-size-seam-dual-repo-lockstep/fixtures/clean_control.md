<!-- test fixture for 149-check-claims.py -- NOT a phase artifact -- never add to _DEFAULT_TARGETS -->

Phase 149 carries the per-chip page size from chip_database.json over the existing wire path to the
firmware's protocol-0x0D write handler. Fifteen AT28C010-class parts move from the 64-byte floor to a
128-byte page; three upstream-native rows stay at 64. This change is software-proven and unvalidated on silicon. No physical AT28C part has been
exercised on a bench during this phase, and none of the fifteen movers changes AT28C256's own value.
