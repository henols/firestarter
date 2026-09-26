<!-- test fixture for check_permitted_claims.py — NOT a closing artifact — never add to _DEFAULT_TARGETS -->

This milestone derives, per chip, a plan from `sdp_capability()`: the 43 ALLOW-capability chips get
a six-step SDP leg, and the 41 REFUSE-capability chips get NA steps carrying their refusal reason.
The read-back comparison logic and every degenerate-input arm of it are proven in native test
environments. SDP command emission is provable only to the extent the host can observe a scripted
wire, never a real bus trace. Following this project's own evidence ceiling: no AT28C silicon was
tested.
