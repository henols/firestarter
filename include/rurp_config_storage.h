/*
 * Project Name: Firestarter
 * Copyright (c) 2026 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __RURP_CONFIG_STORAGE_H__
#define __RURP_CONFIG_STORAGE_H__

/*
 * The configuration-persistence storage seam. This header declares byte-blob
 * persistence as a platform property: EACH platform (AVR EEPROM,
 * py32f071 dual-slot CRC-protected flash) implements the same two
 * functions, and the common policy layer above the seam never knows which
 * one it is talking to.
 *
 * WHY EXACTLY TWO FUNCTIONS (D-06):
 *   The seam is two bool-returning functions over a byte blob --
 *   rurp_config_storage_load(void*, size_t) / rurp_config_storage_save(const
 *   void*, size_t) -- so a backend can report "no valid record" HONESTLY
 *   instead of returning zeroed bytes and relying on a version-string
 *   accident to distinguish blank from loaded. Two alternatives were
 *   considered and rejected:
 *     - a void/void seam: makes py32's "both slots blank" indistinguishable
 *       from "loaded zeros", handled only by the version-string accident --
 *       the same inference style as v1.22's inverted 0x5555 check;
 *     - a richer status enum (OK / BLANK / CRC_FAIL / IO_ERROR): invents
 *       vocabulary with no consumer today (D-15 explicitly declines to
 *       distinguish blank from both-slots-corrupt on the wire). A
 *       declaration with no implementation and no consumer does not land
 *       (Phase 124 D-01, Phase 125 D-09) -- add it only if a consumer
 *       arrives.
 *
 * WHAT STAYS ABOVE THE SEAM (D-07):
 *   All four public config functions -- rurp_get_config, rurp_load_config,
 *   rurp_save_config, rurp_validate_config -- and the rurp_config global
 *   stay in the common policy layer, src/rurp_config_utils.cpp. Their
 *   declarations stay exactly where they already are, in rurp_shield.h
 *   (:61, :150-152). Only the two byte-blob calls below cross this seam.
 *   `CONFIG_START` (the EEPROM offset 48) is an EEPROM ADDRESS -- it is
 *   meaningless on py32 -- so it lives BELOW the seam, in the AVR backend
 *   translation unit, not here and not in the policy layer.
 *
 * WHY rurp_shield.h IS NOT TOUCHED (D-09):
 *   This header is included by exactly THREE translation units: the common
 *   policy layer (src/rurp_config_utils.cpp) and the two per-platform
 *   backends (src/boards/rurp_config_storage_eeprom.cpp for AVR;
 *   platform/py32f071/src/config_storage_flash.cpp for ARM, landed by Plan
 *   126-08). rurp_shield.h is reachable from 46 translation units, 14 of
 *   them native host_stubs.cpp files -- Phase 125's C-1 measured that ONE
 *   #include line added to rurp_shield.h took `pio test -e native` from
 *   141 cases / 141 succeeded to 17 suites / 0 succeeded. This header is
 *   therefore never included from rurp_shield.h, and never will be.
 *
 * AVR BEHAVIOUR IS UNCHANGED (CFG-04):
 *   The AVR implementation of rurp_config_storage_load returns `true`
 *   UNCONDITIONALLY after the typed EEPROM.get() read, and the common
 *   policy layer calls rurp_validate_config() either way -- exactly as it
 *   did before this seam existed. The signature is new; the behaviour is
 *   byte-identical, which is what CFG-04 requires.
 *
 * FIRE-PROOF:
 *   tests/test_config_storage_seam_shape.py (Plan 126-05) gates this
 *   header's shape (exactly two declarations, the include-guard form, the
 *   include-before-extern-C ordering, the includer census of exactly three
 *   translation units). tests/test_config_storage_eeprom_regression.py
 *   (Plan 126-02) pins the AVR access this seam's load/save calls must
 *   still produce: EEPROM.get/put at offset 48, length sizeof(rurp_configuration_t).
 */

#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Load the persisted configuration byte blob from this platform's
 * backing store into `blob`.
 *
 * @param blob Destination buffer, at least `len` bytes.
 * @param len  Number of bytes to read -- callers pass
 *             sizeof(rurp_configuration_t).
 * @return true if the read was performed (AVR: always true -- EEPROM always
 *         yields bytes, and rurp_validate_config() decides whether they are
 *         usable); false if this platform can positively determine no valid
 *         record exists (py32: both slots blank or CRC-rejected, D-15).
 */
bool rurp_config_storage_load(void* blob, size_t len);

/**
 * @brief Persist `len` bytes from `blob` to this platform's backing store.
 *
 * @param blob Source buffer, at least `len` bytes.
 * @param len  Number of bytes to write -- callers pass
 *             sizeof(rurp_configuration_t).
 * @return true if the write was performed (AVR: always true). py32's
 *         dual-slot backend (Plan 126-08) also returns true unconditionally
 *         here -- a write failure mode has no consumer today.
 */
bool rurp_config_storage_save(const void* blob, size_t len);

#ifdef __cplusplus
}
#endif

#endif // __RURP_CONFIG_STORAGE_H__
