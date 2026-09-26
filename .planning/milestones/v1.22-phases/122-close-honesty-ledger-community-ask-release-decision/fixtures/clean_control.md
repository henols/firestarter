<!-- test fixture for check_permitted_claims.py -- NOT a closing artifact; never add to _DEFAULT_TARGETS -->

# Clean control fixture

The SDP lock and unlock sequences are emitted exactly as specified, verified
byte-exact by golden register trace across all four `0x0D` pinouts, with a
documented and measured host-side timing assumption. The auto-unlock
sequence now reports one line before the six-write sequence and one line
after it, carrying a measured emit duration.

No AT28C silicon was tested; this record covers the software/register-trace
layer only.
