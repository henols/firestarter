// clean_build_warnings_no_redef.cpp — Phase 123 Plan 03 (BASE-06, D-14).
//
// Fixture input, never project source. The paired control for
// planted_build_warnings_macro_redef.cpp: same shape, a single macro
// definition instead of two, so it compiles with zero warnings. Without
// this control, a parser that matched everything (rather than being
// genuinely discriminating) would still pass on the planted case.

#define FIRESTARTER_FIXTURE_MACRO_REDEF_123_03 1

int fixture_unused_symbol = FIRESTARTER_FIXTURE_MACRO_REDEF_123_03;
