<!-- test fixture for 146-check-claims.py — NOT a closing artifact — never add to _DEFAULT_TARGETS -->

This second control exists so that a two-file run can demonstrate neither file was silently skipped. Its
prose is deliberately unlike the first control's, and the gate's PASS line must name both basenames.

gh#15's nine acceptance boxes are graded in this milestone's reconciliation with three tokens: met,
met-as-corrected naming the correction, and not-reachable-on-this-hardware naming the reason. The boxes
that were reachable in software are attested by the native suites and shown with their case counts; the
remainder were established only as far as one bench part allowed, and are reported as exactly that.

The two caveats this control carries are the ones the gate demands of a real closing artifact: the
~6.25 V program-VCC ceiling the RURP shield's program rail reaches, and the silicon margin that ceiling
narrows. Both are stated here as prose a reader would meet in a release body, not as a keyword stuffing.
