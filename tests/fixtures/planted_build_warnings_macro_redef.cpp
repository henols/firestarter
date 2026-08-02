// planted_build_warnings_macro_redef.cpp — Phase 123 Plan 03 (BASE-06, D-14).
//
// Fixture input, never project source. Compiled at test time by
// tests/test_check_build_warnings.py using a real host g++ (never avr-g++ --
// see that module's docstring and 123-RESEARCH.md's pinned compiler choice).
// Defines one macro twice with different replacement lists, so any
// conforming preprocessor emits a redefinition diagnostic. The macro name is
// deliberately distinctive and fixture-scoped -- unlikely to collide with
// any real project or system macro -- because the paired test asserts that
// this EXACT name appears in the parsed diagnostic, proving the parser
// extracted the macro name rather than merely matching the word "redefined".

#define FIRESTARTER_FIXTURE_MACRO_REDEF_123_03 1
#define FIRESTARTER_FIXTURE_MACRO_REDEF_123_03 2

int fixture_unused_symbol = FIRESTARTER_FIXTURE_MACRO_REDEF_123_03;
