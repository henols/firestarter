<!-- test fixture for 146-check-claims.py — NOT a closing artifact — never add to _DEFAULT_TARGETS -->
<!-- planted violation: trips the bare-claim-word label (pattern 10, `\bproven\b`) after a hyphen; both
     required caveats ARE present, so this fixture fails for exactly one reason -->

This fixture pins the pattern most likely to bite a real closing artifact, because the word it forbids is
the word a bench record reaches for first. The word boundary holds after a hyphen, so the compound below
is a violation even though it reads as a narrowing rather than as an overclaim.

The program rail is held at the ~6.25 V program-VCC ceiling this shield can reach, so the silicon-margin
the datasheet method assumes is narrower here than that method presumes.

The planted sentence: 0x07 is bench-proven on one part, one controller, one shield revision.
