<!-- test fixture for 152-check-claims.py -- NOT a phase artifact -- never add to _DEFAULT_TARGETS -->

This ships software-proven and unvalidated on silicon. No AT28C part was tested at any point in
v1.32. Protocol `0x0D` stays UNVERIFIED in PROTOCOL-LEDGER.

`write --sdp-relock` remains withdrawn, for a second release.

gh#32 (closed 2026-08-08, folded into gh#21).

Standalone erase is now available on this protocol, and write no longer performs a blank check on
it.
