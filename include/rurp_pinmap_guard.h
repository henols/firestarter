/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * The provisional-pin-map refusal, made concrete.
 *
 * WHY THIS HEADER EXISTS. `is_memory_cmd()` (include/firestarter.h) is the
 * ADMISSION gate: it decides which commands may reach configure_memory() at
 * all. This header adds a second, ORTHOGONAL gate that sits INSIDE
 * configure_memory() itself: even for an admitted command, a board whose
 * pin map is still provisional (no verified PCB assignment behind it) must
 * refuse to energise the PROM bus. Two different questions, two different
 * gates, deliberately not merged into one.
 *
 * WHY A PLATFORM-NEUTRAL FLAG, NOT `RURP_PY32F071_PINMAP_PROVISIONAL`
 * DIRECTLY. `configure_memory()` lives in src/proms/ and is compiled by
 * every target -- AVR (uno/uno328pb/leonardo), both native envs, and the
 * ARM py32f071 build. Naming the py32-specific macro here would hard-wire
 * one platform's name into shared code; a second provisional board arriving
 * later would need its own copy-pasted guard. The neutral flag lets any
 * board header opt in by defining it (see the bridging block in
 * include/boards/py32f071_rurp_shield.h), while shared code tests only the
 * neutral name.
 *
 * WHY THE DEFAULT IS 0, WRAPPED IN #ifndef. AVR boards never define this
 * flag at all, so the #ifndef/#define/#endif default (the same idiom as
 * DATA_BUFFER_SIZE and DEV_TOOLS in include/firestarter.h:16-42) resolves it
 * to 0 there -- the guard then compiles to nothing on every AVR target,
 * zero flash/RAM cost, unchanged from Plan 124-06's recorded figures. The
 * #ifndef wrapper is load-bearing, not decorative: without it, a build that
 * already defines the flag on the command line or via a board header (the
 * py32 case) would hit a macro-redefinition warning, which
 * check_build_warnings.py counts against the watermark.
 *
 * WHY THE PREDICATE DELEGATES TO is_memory_cmd() INSTEAD OF RE-LISTING THE
 * EIGHT COMMANDS (D-12). Re-listing CMD_READ/CMD_WRITE/CMD_ERASE/
 * CMD_BLANK_CHECK/CMD_CHECK_CHIP_ID/CMD_VERIFY/CMD_SDP_UNLOCK/CMD_SDP_LOCK
 * here would create a second hand-maintained copy of the exact set
 * is_memory_cmd() already enumerates -- two lists that can silently drift
 * apart the moment either one is edited. Delegating means the refused set
 * is ALWAYS is_memory_cmd()'s set, by construction, with no second list to
 * forget.
 *
 * WHICH COMMANDS STAY ALLOWED, AND WHY (D-12). The identity/config commands
 * -- CMD_FW_VERSION, CMD_CONFIG, CMD_HW_VERSION -- are NOT in
 * is_memory_cmd()'s set, so they are never refused here either: the board
 * must stay discoverable (fw version, hw revision, config read/write) even
 * while its pin map is provisional, or a host could never even identify
 * that it is talking to a py32f071 unit. CMD_READ_VPP/CMD_READ_VPE (the
 * VPP/VPE voltage monitor reads) are likewise outside is_memory_cmd()'s
 * set and stay allowed: they are read-only ADC monitor taps that do not
 * route voltage to the socket (see memory: reference_vpp_vpe_no_socket_
 * routing), so they carry none of the hazard this guard exists to prevent.
 *
 * WHY THE CONDITIONAL LIVES HERE, NEVER INSIDE is_memory_cmd()'S BODY.
 * firestarter_app/tools/check_is_memory_cmd_no_ifdef.py forbids ANY
 * preprocessor conditional inside is_memory_cmd() -- that predicate must
 * stay conditional-free so its two-env (native / native_nodevtools) truth
 * table proof stays meaningful (Phase 119 LOCK-03). The `#if
 * RURP_PINMAP_PROVISIONAL` test therefore lives in this SEPARATE function,
 * in this SEPARATE header, never inside is_memory_cmd() itself.
 *
 * WHY static inline, IN A HEADER (not a .cpp / new translation unit).
 * [env:native]'s build_src_filter compiles only src/proms/,
 * src/boards/rurp_serial_utils.cpp, src/json_parser.c and
 * src/operation_utils.cpp -- the exact same build_src_filter constraint
 * that makes is_memory_cmd() itself static inline in firestarter.h rather
 * than a .cpp function (see firestarter.h's own comment on that predicate).
 * A definition anywhere else would not link into the native test binary
 * that Plan 124-08's suite requires.
 *
 * The `#if` below is itself what makes THIS header a real CONSUMER of the
 * neutral flag for scripts/check_orphan_provisional.py's orphan-macro scan
 * -- a flag that is defined but never tested by anything enforces nothing,
 * which is exactly the defect class that gate exists to catch.
 */
#ifndef __RURP_PINMAP_GUARD_H__
#define __RURP_PINMAP_GUARD_H__

#include "firestarter.h"

#ifndef RURP_PINMAP_PROVISIONAL
#define RURP_PINMAP_PROVISIONAL 0
#endif

static inline bool rurp_pinmap_refuses(uint8_t cmd) {
#if RURP_PINMAP_PROVISIONAL
    return is_memory_cmd(cmd);
#else
    return false;
#endif
}

#endif /* __RURP_PINMAP_GUARD_H__ */
