<!-- test fixture for 146-check-claims.py — NOT a closing artifact — never add to _DEFAULT_TARGETS -->
<!-- planted violation: trips the confirmed-working forbidden label; both required caveats ARE present, so
     this fixture fails for exactly one reason -->

This fixture is a copy of the first clean control's posture with a single overclaim added, so that a
failure here is attributable to that one sentence and to nothing else about the document.

The per-byte program loop and its parameter table are bench-validated on one part, one controller and one
shield revision; every other 27C family in the database is skipped-with-reason.

The program rail is held at the ~6.25 V program-VCC ceiling this shield can reach, so the silicon-margin
the datasheet method assumes is narrower here than that method presumes.

The planted sentence: the 27C per-byte program loop was confirmed working across the whole family.
