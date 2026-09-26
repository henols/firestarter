<!-- test fixture for check_permitted_claims.py -- NOT a closing artifact; never add to _DEFAULT_TARGETS -->
<!-- D-16's negative direction, the fixture with no v1.22 analogue: the two
     true AVR sentences below use forbidden phrases but must NOT fire the
     gate, because the ARM part's token is nowhere near them in the file. -->

# Clean AVR bench-validation control (D-16 negative direction)

The Leonardo target remains bench-validated from v1.15, and the Uno target
remains hardware-validated from the same earlier milestone -- both are true
statements about AVR silicon and have nothing to do with the ARM part.

<!-- WARNING: do not reflow this file. The required silicon caveat below
     must stay at least two blank lines away from the AVR sentences above
     -- the checker's 3-line proximity window means any line carrying the
     ARM part's token within one line of a forbidden phrase would make this
     fixture fire, which would defeat the entire point of this control. If
     you edit this file, preserve the blank-line gap below. -->


no PY32F071 hardware exists, so nothing in this fixture is a claim about
that part -- the sentences above are exclusively about AVR silicon
validated in earlier milestones.
