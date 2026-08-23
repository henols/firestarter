#pragma once

/*
 * Dependency-free fragment header carrying the PY32F071 pin-map
 * "configured for a real build" guard.
 *
 * WHY THIS IS A SEPARATE, DEPENDENCY-FREE FILE:
 *   include/boards/py32f071_rurp_shield.h includes py32f0xx_hal.h, which
 *   pulls in PY32 HAL headers that no local toolchain in this devcontainer
 *   can resolve (arm-none-eabi-gcc is absent; the PY32 SDK is
 *   FetchContent-only and only materializes during a networked CMake
 *   configure). This file includes NOTHING AT ALL, so a plain host
 *   preprocessor (`g++ -E`) can evaluate it standalone. Hoisting the guard
 *   out of the board header and into this fragment is what makes it
 *   provable at all -- that is mandatory, not a style preference.
 *
 * WHAT THIS HEADER TESTS, NOT DEFINES:
 *   RURP_PY32F071_PINMAP_CONFIGURED is supplied ONLY by the ARM build's
 *   compile definitions (platform/py32f071/CMakeLists.txt's
 *   target_compile_definitions). This header never defines it -- it only
 *   TESTS what the build supplies. A build that forgets to supply it now
 *   fails at the preprocessor with a named error instead of silently
 *   compiling an unconfigured, provisional pin map that could energise a
 *   PROM.
 *
 * THE CONDITION BELOW FIRES ON BOTH THE UNSET AND THE EXPLICITLY-ZERO ARM:
 *   `!defined(X) || !X` states the defined()-ness explicitly rather than
 *   relying on an undefined identifier evaluating to 0 in `#if`. A bare
 *   `#if !X` would fire on "unset" only incidentally (because `#if`
 *   silently treats an undefined identifier as 0) -- stating `!defined(X)`
 *   explicitly makes the "unset must fail" intent visible to a reader and
 *   also survives a later `-Wundef` build flag, which would otherwise warn
 *   on the undefined-identifier read.
 *
 * FIRE-PROOF:
 *   tests/test_pinmap_guard_fires.py preprocesses THIS file standalone with
 *   a host compiler across three arms -- macro unset, =1, =0 -- and asserts
 *   the exact discriminating exit codes and error text recorded below.
 */

#if !defined(RURP_PY32F071_PINMAP_CONFIGURED) || !RURP_PY32F071_PINMAP_CONFIGURED
#error "RURP_PY32F071_PINMAP_CONFIGURED is not set: the PY32F071 Firestarter wiring is not configured for this build. This macro must be supplied by the build system (platform/py32f071/CMakeLists.txt's target_compile_definitions), not by this header."
#endif
