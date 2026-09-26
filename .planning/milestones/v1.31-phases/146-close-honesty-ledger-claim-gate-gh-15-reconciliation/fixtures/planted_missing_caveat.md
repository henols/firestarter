<!-- test fixture for 146-check-claims.py — NOT a closing artifact — never add to _DEFAULT_TARGETS -->
<!-- planted violation: the ceiling-narrowing caveat is ABSENT; the ceiling-voltage caveat is present and
     zero forbidden phrases appear, so this fixture fails for exactly one reason -->

This fixture carries the program-VCC figure and stops there. It names the ~6.25 V ceiling the shield's
program rail reaches, but it never states what that ceiling costs — the narrowing the second required
caveat exists to force an author to write down.

The per-byte program loop and its parameter table are bench-validated on one part, one controller and one
shield revision; every other 27C family in the database is skipped-with-reason, and each reason is
recorded rather than implied. No datasheet-conformance claim is made in either direction.
