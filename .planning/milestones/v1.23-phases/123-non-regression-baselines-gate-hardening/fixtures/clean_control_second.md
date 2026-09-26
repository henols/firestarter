<!-- test fixture for check_permitted_claims.py -- NOT a closing artifact; never add to _DEFAULT_TARGETS -->

# Second clean control fixture

This is a second, textually distinct clean control. Its only job is to let
the anti-skip test prove the scanner's PASS line names both scanned files
at once.

Host-side timing and sizes are measured wherever a tool exists to measure
them. The DFU install path is exercised against a mock USB stack and
recorded device descriptors only; no board of any kind was attached.

no PY32F071 hardware exists, and no claim in this note extends past what
the mock and the measured host-side numbers can support.
