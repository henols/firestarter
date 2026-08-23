#pragma once

/*
 * The VPP control capability seam. This header declares VPP control as a
 * platform
 * property that a board either has (a DAC) or does not (a human adjusting a
 * potentiometer), and nothing else. It is a capability declaration, not an
 * implementation -- see src/rurp_vpp.cpp for the (refusal-shaped) bodies.
 *
 * WHY THIS IS DEPENDENCY-FREE:
 *   The only include below is <stdint.h>, which a plain host preprocessor
 *   resolves standalone -- no rurp_shield.h, no <Arduino.h>, no
 *   rurp_platform.h, no PY32 HAL. This is a standing constraint (D-02), not a
 *   local convenience: a later phase that wants configuration access or
 *   hardware register access must add that dependency deliberately, and pay
 *   for it explicitly, rather than inherit it here for free.
 *
 * WHAT THIS HEADER TESTS, NOT DEFINES:
 *   For every non-AVR target, the value of RURP_HAS_VPP_DAC is supplied ONLY
 *   by the board/platform build -- for py32f071 that means
 *   platform/py32f071/CMakeLists.txt's target_compile_definitions (D-07).
 *   This header never defines the macro for a non-AVR target; it only tests
 *   what the build supplies. A fifth non-AVR board that forgets to supply it
 *   fails at the preprocessor rather than silently inheriting manual control
 *   near an unregulated rail. This is Phase 124 D-14's lesson (a guard that
 *   defines what it tests is dead) applied before the fact.
 *
 * PERMANENCE:
 *   No Arduino/AVR-class RURP board carries a VPP DAC, and none ever will --
 *   the VPP rail on every AVR-class board is set by the operator's
 *   potentiometer. This is a PERMANENT property of the AVR-class boards, not
 *   a provisional placeholder pending hardware. Operator, 2026-07-31: "No
 *   arduino board will have the DAC so it must be set to disabled."
 *
 * WHY __AVR__ AND NOT THE TREE'S OWN PLATFORM-FAMILY MACRO:
 *   __AVR__ is compiler-supplied and unconditional on all three AVR targets,
 *   which is what keeps this header dependency-free. The tree's own
 *   RURP_PLATFORM_AVR (include/rurp_platform.h) looks like the more
 *   "in-house" choice but is a trap: it is defined inside an
 *   `#elif defined(__AVR__)` arm, so it is DERIVED from __AVR__, never
 *   independent of it; rurp_platform.h is reachable from no AVR build at all
 *   (its only includers are under platform/py32f071/ and
 *   include/boards/py32f071_rurp_shield.h), so RURP_PLATFORM_AVR is never
 *   actually defined during an AVR build; and rurp_platform.h carries its own
 *   terminal #error whose native escape arm names a macro
 *   (RURP_PLATFORM_NATIVE) that is defined nowhere in either repo. Including
 *   rurp_platform.h from this seam would break the native test environments
 *   harder than a bare capability-macro #error does. This reasoning is
 *   recorded here so a later phase does not "improve" the predicate below.
 *
 * FIRE-PROOF:
 *   tests/test_vpp_seam_manual_on_every_board.py compiles this header (and
 *   src/rurp_vpp.cpp) with a host compiler across every board macro-set plus
 *   a forced-DAC leg and an unset-and-non-AVR leg, and asserts the exact
 *   discriminating exit codes and error text for both guards below.
 */

#include <stdint.h>

#if !defined(RURP_HAS_VPP_DAC)
#  if defined(__AVR__)
/* Permanent, not provisional: no Arduino/AVR-class RURP board carries a
 * VPP DAC -- the rail is set by the operator's pot. Operator, 2026-07-31. */
#    define RURP_HAS_VPP_DAC 0
#  else
#    error "RURP_HAS_VPP_DAC must be supplied by the board/platform build (for py32f071: platform/py32f071/CMakeLists.txt's target_compile_definitions), not by this header."
#  endif
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    RURP_VPP_CONTROL_MANUAL = 0,
    RURP_VPP_CONTROL_DAC = 1,
} rurp_vpp_control_mode_t;

typedef enum {
    RURP_VPP_OK = 0,
    RURP_VPP_MANUAL_ADJUSTMENT_REQUIRED = 1,
} rurp_vpp_result_t;

rurp_vpp_control_mode_t rurp_vpp_control_mode(void);
rurp_vpp_result_t rurp_set_vpp_target_mv(uint16_t target_mv, uint16_t tolerance_mv, uint16_t timeout_ms);
void rurp_disable_vpp_control(void);

#ifdef __cplusplus
}
#endif
