---
title: "CONFIG_VERSION is not bumped when a calibration default changes — stale EEPROM values are stranded forever"
date: 2026-08-09
status: resolved
resolved: 2026-09-26
resolved_by: "v1.43 per-board bandgap calibration; option 2 (range-validate)"
priority: medium
area: firmware
source: .planning/debug/resolved/firmware-vpp-misread.md (diagnosed 2026-06-04, root cause confirmed still live 2026-08-09)
files:
  - firestarter/src/rurp_config_utils.cpp
  - firestarter/include/rurp_shield.h
needs_decision: true
---

# RESOLVED 2026-09-26 — `CONFIG_VERSION` is not bumped on a default change — stale EEPROM calibration is stranded

Carried out of the `firmware-vpp-misread` debug session, which was diagnosed but never
fixed (`fix: ""`). The board-specific symptom is long gone; **the latent firmware defect
it uncovered is still present**, verified unchanged on 2026-08-09.

## The defect

`rurp_validate_config` re-applies compiled-in defaults **only** when the stored version
string differs from `CONFIG_VERSION`:

```c
// firestarter/src/rurp_config_utils.cpp:35-43
void rurp_validate_config(rurp_configuration_t* config) {
    if (strcmp(config->version, CONFIG_VERSION) != 0) {
        strcpy(config->version, CONFIG_VERSION);
        config->r1 = VALUE_R1;
        config->r2 = VALUE_R2;
        config->hardware_revision = 0xFF;
        rurp_save_config(config);
    }
}
```

`CONFIG_VERSION` is still `"VER06"` (`include/rurp_shield.h:46`) and `VALUE_R1` is
`270000` (`:49`). Phase 44 changed the `VALUE_R1` default from `1000` to `270000` **without
bumping `CONFIG_VERSION`**. Consequence: any board whose EEPROM was already written under
`VER06` keeps its stale `r1` forever — the code "fix" can never reach the EEPROM.

## Why it matters

`rurp_read_voltage_mv` computes `Vin = Vadc * 1100 * (r1 + r2) / (bandgap * r2)`. With a
stale `r1 ≈ 1000` the divider gain collapses from 7.14x to ~1.02x, so a true 12.2 V reads
as ~1.75 V — a 6.8x under-read. That trips the VPP-low threshold and stalls the program
path at the first chunk. The original session confirmed the arithmetic reproduces the
observed `1.8V` symptom exactly, and eliminated every other candidate (divider math
correct, no board-conditional R1/R2, ADC reference identical across Uno/328PB).

Relevant to v1.31: this milestone's whole subject is VPP/VPE-gated programming timing. A
board carrying stale calibration silently mis-measures the program rail.

## Why this is a decision, not a straightforward fix

Bumping `CONFIG_VERSION` is the obvious repair, **but it re-applies defaults on every
board on next boot — wiping genuinely-calibrated values.** The operator owns boards with
real per-board calibration (Rev 2.2, Rev 2.0, modified Rev 0), so a blind bump trades one
silent-wrong-value problem for another.

Options, none yet chosen:

1. **Bump `CONFIG_VERSION` to `VER07`.** Simple and correct-by-construction; destroys
   existing calibration. Needs an operator-facing "recalibrate after upgrade" note.
2. **Range-validate instead of version-gate.** Reject implausible `r1`/`r2` (e.g. `r1`
   below some floor) and fall back to defaults for those fields only. Fixes the stranding
   without discarding plausible calibration. More code, no flash budget measured yet.
3. **Surface it rather than fix it.** Have `firestarter config` / `hw` warn when stored
   `r1`/`r2` are implausible, leaving the correction manual. Cheapest; still allows a
   quiet mis-measurement if the warning is ignored.

Option 2 looks best on the merits (no data loss, fails safe) but needs a flash-cost check
against the AVR budget before committing.

## Verification when fixed

Non-destructive: `firestarter config` reports live EEPROM `r1`/`r2` (host renders
`MSG_OK_CFG` via `codec.py`). A board with stale calibration shows `r1` far below
`270000`. After the fix, either the value is corrected or the user is warned.


---

## Resolution, 2026-09-26 (v1.43)

**Option 2 was taken: range-validate instead of version-gate.**
`rurp_validate_config` now delegates to a pure `rurp_config_migrate`
(`src/rurp_config_migrate.cpp`) that checks each field against a band and keeps
whatever is still plausible:

- `r1` 202500–337500, `r2` 33000–55000 (±25 % of the defaults, the same
  tolerance the host already applied in `_R1_LO`/`_R1_HI`)
- `bandgap_mv` 1000–1200 mV (the ATmega datasheet window)
- `hardware_revision` is preserved **unconditionally**

This reaches the stale value the version gate never could: a board carrying
`r1 = 1000` under a matching version string is now corrected, because the band
check does not depend on the version string at all.

It also fixes a second defect the original note did not name: the old wipe reset
`hardware_revision` on every version bump, silently destroying an operator's
shield-revision override. Verified on hardware — the Leonardo still reports
`Rev 2.2 (override)` after migrating VER06 → VER07.

`CONFIG_VERSION` did move to `VER07`, because v1.43 appended `bandgap_mv` to the
struct. The bump is no longer destructive.

Covered by behaviour in `test/native/avr/test_config_migrate` (7 cases),
including the stranded `r1` reproduced with a **matching** version string and an
operator override surviving a bump.
