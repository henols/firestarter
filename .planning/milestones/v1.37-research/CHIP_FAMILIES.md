# Chip Families and Their Programming Requirements

**Research Date:** 2026-05-08
**Scope:** DIP 24/28/32 parallel memory devices supported by the Firestarter programmer

---

## Protocol ID Map (from `database.py`)

| Protocol ID | Algorithm Name   | Memory Family              |
|-------------|-----------------|----------------------------|
| `0x07`      | `EPROM_STD`     | UV-EPROM, standard 50ms pulse |
| `0x08`      | `EPROM_QUICK`   | UV-EPROM 27Cxxx, 100µs quick-pulse |
| `0x0B`      | `EPROM_LEGACY`  | Old UV-EPROM (2716/2732), 50ms, 18–25V VPP |
| `0x05`      | `FLASH_AMD_STD` | AMD/SST 29xx Flash, 5555/2AAA unlock |
| `0x06`      | `FLASH_AMD_ALT` | AMD 29Fxxx/SST39SFxxx Flash, 5555/2AAA unlock (wider family) |
| `0x10`      | `FLASH_INTEL`   | Intel/AMD 28Fxxx Flash, byte-command set |
| `0x0D`      | `EEPROM_POLL`   | Parallel EEPROM 28Cxxx, DQ7 DATA polling |
| `0x28`      | `SRAM_STD`      | SRAM (read/write, no programming) |

---

## 1. UV-EPROM — 27xx Family

UV-EPROMs are one-time-electrically-writable (erased by UV light). The host must raise VPP to program voltage and assert a PGM pulse per byte.

### 1.1 EPROM_LEGACY — 2716 / 2732 (24-pin)

**Chips:** 2716 (2 KB), 2732 (4 KB), and their B/A variants.

**Electrical:**
- VCC during programming: 6.5 V (older AMD), 5.5 V (Intel), or 5.0 V (SGS)
- VPP: 18 V (original 2716/2732), 13 V (B-suffix), 12 V (AT27xx)
- VDD: 5 V

**Pinout: `DIP24_2716`**
- Address bus: pins 8,7,6,5,4,3,2,1,23,22,19 (A0–A10)
- Data bus: pins 9,10,11,13,14,15,16,17 (D0–D7)
- CE: pin 18
- OE: pin 20
- VPP: pin 21

**2732 difference:** OE and VPP share pin 20. A12 is on pin 21. CE is pin 18. No separate VPP pin — VPP is applied via pin 20 (the OE/VPP mux pin). This means VPP must be applied _and_ OE deasserted at the same time for programming.

**Programming algorithm (EPROM_LEGACY):**
1. Apply VPP to VPP pin (18 V or 13 V depending on variant)
2. Set address bus
3. Set data bus with byte to write
4. Assert CE low (pin 18)
5. Assert PGM pulse: deassert OE (OE high = "program mode") or dedicated PGM pin
6. Pulse duration: 50 ms (50,000 µs) for standard; 1 ms for AT28C04
7. Deassert CE
8. Optionally read back and verify; retry if needed (up to 25× overprogram)
9. After all bytes: apply overprogram pulse = 3× total successful pulses, or single 25× pulse per site

**Verification:** Read back at VCC = 5 V, VPP = 5 V (disable mode). Compare byte-by-byte.

**Gotchas:**
- 2716 and 2732 have _different_ VPP pins and programming modes despite identical 24-pin DIP packages
- Early 2716 requires 25 V VCC during programming (some AMD datasheets specify VCC = 6.5 V but VCC_PROG can be as high as 6.5 V — not 25 V; the 25 V is a historical NiMH-era artifact for a different variant)
- No chip ID readable on most 2716/2732 variants (chip_id_value = 0x00000000 in DB)
- 2732A (Atmel AT2732A) reduced VPP to 12 V

**Database representation:**
```
algorithm: EPROM_LEGACY
pulse_duration: "50000 us"
pinout: DIP24_2716
```

---

### 1.2 EPROM_STD — 2764 / 27128 / 27256 / 27512 (28-pin)

**Chips:** 2764 (8 KB), 27128 (16 KB), 27256 (32 KB), 27512 (64 KB), and 27Cxxx CMOS variants of the same sizes.

**Electrical:**
- VCC: 5.0–6.5 V (6.5 V for AMD/Motorola, 5.5 V for Intel, 5.0 V for CMOS variants)
- VPP: 13 V (standard), 18 V (original Intel 2764/27128), 12 V (Atmel AT27xxx)

**Pinout: `DIP28_2764`** (for 2764, 27128) and **`DIP28_27256`** (for 27256 — adds A14), **`DIP28_27512`** (A15 and VPP/OE pin swap)
- Address bus: A0–A12 (2764), A0–A13 (27128), A0–A14 (27256), A0–A15 (27512)
- Data bus: pins 11,12,13,15,16,17,18,19 (standard DIP28 JEDEC)
- CE: pin 20
- OE: pin 22 (2764/128/256); pin 22 on 27512 is VPP/OE mux (like 2732 vs 2716 situation)
- VPP: pin 1 (2764, 27128, 27256); pin 22 on 27512 (shared with OE)
- PGM: pin 27 (active during programming)

**Programming algorithm (EPROM_STD):**
1. Apply VPP (12–13 V) to pin 1 (or pin 22 for 27512)
2. Raise VCC to programming voltage (5.5–6.5 V)
3. Set address
4. Set data
5. Assert CE low
6. Assert PGM (pin 27) low for pulse duration
7. Pulse duration: 50 ms for 2764; 20 ms for 27128, 27256, 27512; 10 ms for CMOS 27Cxxx variants
8. Deassert PGM and CE
9. Verify byte immediately; if mismatch, retry up to 25×
10. Final over-program: 3× successful pulse count per byte

**Quick-Pulse Variant (for CMOS 27Cxxx at 28-pin):**
- Same as above but pulse durations 10 ms; many 27C256/27C512 chips accept this
- These are still `EPROM_STD` in the Firestarter DB, not `EPROM_QUICK`

**Verification:** Read with VPP = 5 V, OE low, CE low. Compare against source.

**Gotchas:**
- 27128 and 2764 use the same pinout (`DIP28_2764`) but different address bit counts — A13 on 27128 is pin 26 (NC on 2764)
- 27256 adds A14 on pin 27 (which was NC on 27128); uses `DIP28_27256` pinout
- 27512 moves VPP to pin 22 (was OE), adds A15 on pin 1 (was VPP) — uses `DIP28_27512` pinout
- This VPP/OE swap between 27256 and 27512 is the most common source of programming errors
- Some 27256 chips (e.g., Microchip 28C256) are actually EEPROMs reusing the same JEDEC 27256 pinout but need different algorithms

**Database representation:**
```
algorithm: EPROM_STD
pulse_duration: "50000 us" (2764) / "20000 us" (27128+) / "10000 us" (27Cxxx)
pinout: DIP28_2764 | DIP28_27256 | DIP28_27512
```

---

### 1.3 EPROM_QUICK — 27C010 / 27C020 / 27C040 (32-pin)

**Chips:** 27C010 (128 KB), 27C020 (256 KB), 27C040 (512 KB) and low-voltage variants (27LV010, 27LV040). Manufacturers: AMD, Atmel, Intel, Philips, Cypress, Fairchild, ISSI, EON, Holtek, ICE.

**Electrical:**
- VCC: 5.0–6.5 V (5.5 V most common)
- VPP: 13 V (AMD/Atmel), 12 V (Intel, Cypress), Unknown/5 V for 27LVxxx variants

**Pinout: `DIP32_STD`** — JEDEC standard 32-pin
- Address bus: A0–A16 (27C010), A0–A17 (27C020), A0–A18 (27C040)
- Data bus: pins 13,14,15,17,18,19,20,21
- CE: pin 22
- OE: pin 24
- VPP: pin 1
- VCC: pin 32, GND: pin 16

**Programming algorithm (EPROM_QUICK):**
This is the "Quick Pulse" (or "JEDEC Fast") algorithm, standardized for CMOS 27Cxxx:
1. Apply VPP (12–13 V) to pin 1
2. Set address
3. Set data
4. Assert CE low
5. Assert PGM (pin 31) low for **100 µs** pulse
6. Deassert PGM
7. Read back immediately; if verified, move to next byte
8. If mismatch: re-apply pulse up to 25× (with re-verify each time)
9. Final over-program: apply (N_successful × 3) additional 100 µs pulses per byte

**Pulse timing detail:**
- 100 µs initial pulse (vs 50 ms for EPROM_STD) — this is the "quick" in EPROM_QUICK
- Some ALi/Acer M8720 variants use 20 µs pulses
- Total programming time is dramatically faster: ~100 µs × 25 retries max × byte count

**Chip ID reading:** Most 27Cxxx support electronic ID:
- Apply 12 V to A9 (pin 24 on 32-pin)
- CE low, OE low
- A0=0: reads manufacturer ID (e.g., 0x01 = AMD)
- A0=1: reads device ID (e.g., 0x0E = AMD 27C010)

**Verification:** Standard read at 5 V.

**Gotchas:**
- Some 27C010 chips need CE pulsed LOW → HIGH → LOW during the 100 µs window (CE-controlled pulse vs PGM-controlled)
- 27LV010/27LV020/27LV040 (3.3 V) use VPP = unknown/5 V — should not have 12/13 V VPP applied
- AM27C080 (1 MB, 32-pin) also uses EPROM_QUICK but requires A19 to be handled via extended address
- Chip ID reading requires A9 at 12 V — this is a different pin than VPP

**Database representation:**
```
algorithm: EPROM_QUICK
pulse_duration: "100 us"
pinout: DIP32_STD
```

---

## 2. Flash AMD/SST — 29xx / 39xx Family

These chips use a command/unlock sequence written to specific addresses to enter program/erase modes. No elevated VPP required during operation (some list VPP=12V for protection purposes, but programming uses standard 5 V VCC).

### 2.1 FLASH_AMD_STD — SST29EExx, AT29Cxx

**Chips:** SST29EE010/020/512, AT29BV010A, AT29LV010A, AT29BV020, AT29LV020, and AE29Fxxx variants.

**Electrical:**
- VCC: 5 V (2.7–5.5 V for BV/LV variants)
- VPP: 12 V (SST29EE, AT29C), or "Unknown" for low-voltage variants — VPP is listed as a write-protect input, not required for programming
- VDD: 5 V

**Pinout: `DIP32_STD`**

**Programming algorithm (FLASH_AMD_STD):**
Unlock sequence uses addresses 0x5555 and 0x2AAA:

1. **Chip Erase (before write):**
   ```
   Write 0xAA → 0x5555
   Write 0x55 → 0x2AAA
   Write 0x80 → 0x5555
   Write 0xAA → 0x5555
   Write 0x55 → 0x2AAA
   Write 0x10 → 0x5555   (chip erase command)
   ```
   Wait for completion: poll DQ7 (complement → data), or ~100 ms timeout

2. **Byte Program:**
   ```
   Write 0xAA → 0x5555
   Write 0x55 → 0x2AAA
   Write 0xA0 → 0x5555   (program command)
   Write <data> → <target address>
   ```
   Poll for completion: DQ7 goes HIGH when done (typically <20 µs per byte)

3. **Verify:** Read back and compare.

**The `flash_utils.h` command sequences used by Firestarter:**
```c
FLASH_ERASE:        {0x5555,0xAA}, {0x2AAA,0x55}, {0x5555,0x80}, {0x5555,0xAA}, {0x2AAA,0x55}, {0x5555,0x10}
FLASH_ENABLE_WRITE: {0x5555,0xAA}, {0x2AAA,0x55}, {0x5555,0xA0}
```

**DQ7 DATA Polling:**
- After write command issued: DQ7 outputs complement of written bit 7
- When write complete: DQ7 returns to written value
- Also: DQ6 toggles each read during write; stops toggling when complete

**Toggle Bit Verification:**
- Read address twice consecutively
- If DQ6 toggles between reads: operation in progress
- If DQ6 stable: operation complete

**Chip ID reading:**
```
Write 0xAA → 0x5555
Write 0x55 → 0x2AAA
Write 0x90 → 0x5555   (software ID entry)
Read 0x0000 → Manufacturer ID
Read 0x0001 → Device ID
Write 0xAA → 0x5555
Write 0x55 → 0x2AAA
Write 0xF0 → 0x5555   (exit ID mode)
```

**Gotchas:**
- SST29EE chips use page write (128 bytes at a time with the same unlock sequence)
- AT29Cxxx are sector-organized; smallest erase unit is a sector, not the entire chip
- VPP/WP pin on AT29Cxxx: pull HIGH to disable write protection; some tools apply 12 V here

---

### 2.2 FLASH_AMD_ALT — AM29Fxxx, SST39SFxxx, SST29SFxxx (32-pin)

**Chips:** AM29F010, AM29F040, SST39SF010/020/040, SST29SF010/020/040, SST29VF010/020/040, SST39LH/VF series, AS29F002, various compatibles.

This is the _most common_ algorithm for 29xx/39xx DIP-32 flash. `FLASH_AMD_ALT` differs from `FLASH_AMD_STD` primarily in which chips use it (wider, more common family) and some timing/sector details, but the _command sequences are identical_.

**Electrical:**
- VCC: 5 V (SST39SF requires 5 V; SST39VF works at 2.7–5.5 V)
- VPP: 12 V for SST39SF (write protect function, not required for normal programming); "Unknown" for VF variants
- All programming at 5 V VCC — no elevated VPP required

**Pinout: `DIP32_STD`**

**Programming algorithm (FLASH_AMD_ALT):**
Same command sequences as FLASH_AMD_STD:

1. **Chip Erase:**
   ```
   0xAA → 0x5555
   0x55 → 0x2AAA
   0x80 → 0x5555
   0xAA → 0x5555
   0x55 → 0x2AAA
   0x10 → 0x5555
   ```
   Erase time: ~100 ms (SST39SF), up to 10 seconds (some AM29Fxxx). Poll DQ7.

2. **Sector Erase (where supported):**
   ```
   0xAA → 0x5555
   0x55 → 0x2AAA
   0x80 → 0x5555
   0xAA → 0x5555
   0x55 → 0x2AAA
   0x30 → <sector address>
   ```

3. **Byte Program:**
   ```
   0xAA → 0x5555
   0x55 → 0x2AAA
   0xA0 → 0x5555
   <data> → <target address>
   ```
   Byte program time: ~20 µs typical.

4. **DQ7 polling / Toggle bit** — same as FLASH_AMD_STD above.

**SST39SF specific notes:**
- Sector size: 4 KB (SST39SF010/020/040)
- Chip must be erased (sector or chip) before programming — cannot overwrite 0→1 at byte level
- SST39SF040 chip ID: 0xBFB7 (manufacturer 0xBF = SST, device 0xB7)
- SST39VF040 chip ID: 0xBFD7 (same as SST39LH040)

**AM29F specific notes:**
- AM29F010: 128 KB, 8 sectors of 16 KB each
- AM29F040: 512 KB, 8 sectors of 64 KB each
- Chip ID AM29F010: 0x0120 (mfr 0x01 = AMD, device 0x20)
- Chip ID AM29F040: 0x01A4

**Difference between STD and ALT in practice:**
In the Firestarter database, `FLASH_AMD_STD` covers older-generation SST29EE and AT29Cxxx page-write devices, while `FLASH_AMD_ALT` covers the AM29Fxxx and SST39SFxxx sector-erase devices. The underlying command sequences written to 0x5555/0x2AAA are identical; what differs is:
- Page write vs sector/chip erase granularity
- Timing characteristics
- Which chips historically tested against which algorithm ID in the minipro reference

**Gotchas:**
- Cannot write a '1' bit to an already-programmed '0' bit without erasing — blank check before write
- Sector erase is faster than chip erase for partial updates; chip erase is simpler
- SST39VF/LH variants are 3.3 V parts — do not apply 5 V VCC
- Some SST29SF/SF chips have VPP pin that gates write: must pull HIGH or apply 12 V; "Unknown" in DB means not needed or pulled internally

---

## 3. Flash Intel — 28F Series (FLASH_INTEL)

Uses Intel's proprietary byte-command set. All commands written to the target address (not a fixed unlock address). Status register polling instead of DQ7/toggle bit.

**Chips:** AM28F256, AM28F512, AM28F010, AM28F010A, AM28F020, Intel 28F001, 28F002, CAT28F010/020, SST28SF040, SST28LF040. Also Intel-compatible clones including some NEC and Fujitsu parts.

Note: AMD AM28Fxxx uses the Intel command set (not AMD command set). AM29Fxxx uses AMD command set. This naming confusion is common.

**Electrical:**
- VCC: 5 V
- VPP: 12 V (required for erase and program — this is a real elevated VPP, unlike AMD-family flash)
- VPP must be applied to the VPP pin (pin 1 on DIP32_STD) during erase and program operations

**Pinout: `DIP32_STD`**

**Programming algorithm (FLASH_INTEL):**

All commands are written to the _target address_ (not a fixed 0x5555 unlock sequence):

1. **Chip Erase:**
   ```
   Write 0x20 → <any address>   (erase setup command)
   Write 0xD0 → <any address>   (erase confirm command)
   ```
   Poll status register: read from chip; bit 7 (WSMS = Write State Machine Status) goes HIGH when done.

2. **Byte Program:**
   ```
   Write 0x40 → <target address>   (byte program command)
   Write <data> → <target address> (data)
   ```
   Poll status register: bit 7 HIGH = complete.
   Typical program time: ~9 µs per byte.

3. **Read Status Register:**
   ```
   Write 0x70 → <any address>   (read status command)
   Read <any address>           (returns status byte)
   ```
   Status byte bits:
   - Bit 7 (WSMS): 1 = ready, 0 = busy
   - Bit 4 (VPP status): 1 = VPP out of range error
   - Bit 5 (Program status): 1 = program error
   - Bit 3 (VPP low detect): 1 = VPP low during operation

4. **Reset / Read Array:**
   ```
   Write 0xFF → <any address>   (return to read mode)
   ```

5. **Read Electronic ID:**
   ```
   Write 0x90 → <any address>
   Read 0x0000 → Manufacturer ID
   Read 0x0001 → Device ID
   Write 0xFF → <any address>   (exit ID mode)
   ```

**Chip IDs:**
- AM28F010: 0x01A7
- AM28F010A: 0x01A2
- AM28F020: 0x012A
- CAT28F010: 0x31B4
- CAT28F020: 0x31BD

**Key differences from AMD command set:**
| Feature | Intel (FLASH_INTEL) | AMD (FLASH_AMD_ALT) |
|---------|--------------------|--------------------|
| Command target | Target address | Fixed 0x5555/0x2AAA |
| Erase command | 0x20+0xD0 | 6-byte unlock sequence |
| Program command | 0x40 | 3-byte unlock + data |
| Completion check | Status register bit 7 | DQ7 data polling / DQ6 toggle |
| VPP | Required 12V for write/erase | Not required (or WP-only) |
| Reset to read | 0xFF command | Automatic after operation |

**Gotchas:**
- VPP must be stable at 12 V _before_ issuing erase/program commands and held until complete
- Status register must be cleared with 0x50 (clear status) after any error before retrying
- Erase verify: after erase, each byte should read 0xFF; program verify: read back and compare
- SST28SF040 and SST28LF040 use Intel command set but note: SST28LF040 requires VPP=5 V (low-voltage variant)
- Some Intel-set chips require a "suspend" command for interrupting operations — not needed for Firestarter's sequential programming

---

## 4. Parallel EEPROM — 28Cxx Family (EEPROM_POLL)

Electrically erasable and writable byte-by-byte (or by page). No UV erase required. Uses a polling mechanism (DQ7 or READY/BUSY) to detect write completion.

### 4.1 EEPROM_POLL — AT28C010, CAT28C010, AT28C040

**Chips:** AT28C010/010E (128 KB, 32-pin), AT28C040/040E (512 KB, 32-pin), AT28LV010 (3.3V), CAT28C010.

**Electrical:**
- VCC: 5 V (2.7–5.5 V for LV variants)
- VPP: 12 V listed for AT28C010 (write protection pin) — can be pulled HIGH to enable write, or tied to VCC; not required for programming itself
- Write cycle time: ~1 ms (internal timer controls write, not the programmer)

**Pinout: `DIP32_STD`**

**Programming algorithm (EEPROM_POLL):**
1. Set address
2. Set data
3. Assert WE (write enable) low for minimum pulse (typically 100–500 ns setup, 500 ns WE pulse)
4. Deassert WE — internal write cycle begins automatically
5. **Poll DQ7** (DATA polling):
   - During write: DQ7 outputs complement of written data bit 7
   - When write complete: DQ7 returns to the written value
6. After DQ7 confirms completion, advance to next byte
7. Total write cycle: 200 µs–5 ms depending on variant

**Page Write Mode (AT28C010 supports 128-byte pages):**
- Within a page (128-byte aligned), bytes can be written in rapid succession without waiting for completion between bytes
- After all bytes in the page are written, poll DQ7 of the last written byte for completion
- Write must complete within 150 µs (tBLC) or page write is aborted

**Software Data Protection (SDP):**
Many 28Cxxx chips have SDP. To enable write, send the SDP unlock sequence before each write (or page write):
```
Write 0xAA → 0x5555
Write 0x55 → 0x2AAA
Write 0xA0 → 0x5555
<then proceed with byte write>
```
SDP is enabled by default on some chips (AT28C256, AT28C64B). Older chips (AT28C64, CAT28C64A) may not have SDP.

**To disable SDP permanently:**
```
Write 0xAA → 0x5555
Write 0x55 → 0x2AAA
Write 0x80 → 0x5555
Write 0xAA → 0x5555
Write 0x55 → 0x2AAA
Write 0x20 → 0x5555
```

**Verification:** Read back at VCC = 5 V, WE high (read mode). DQ7 polling confirms the write cycle completed before reading.

**Gotchas:**
- AT28C010 write cycle time in DB: "Algorithm Controlled" — the 1 ms internal timer is self-timed; host only needs to poll, not time the pulse
- AT28C040 uses same algorithm but 512 KB capacity
- AT28LV010: 2.7–5.5 V, VPP = "Unknown" — do not apply 12 V
- Microchip 28C256 in the DB has `EPROM_STD` algorithm and `pulse_duration: "1000000 us"` — this is NOT the same as AT28C256; Microchip 28C256 appears to be treated as a slow OTP EPROM

---

### 4.2 28Cxx at 28-pin — AT28C64, AT28C256 (JEDEC 28-pin)

**Chips:** AT28C64 (8 KB), AT28C256 (32 KB) — 28-pin DIP, Atmel and compatible.

**Electrical:**
- VCC: 5 V
- VPP: 12 V (WP function pin); for Atmel AT28C64/256, pin 1 (VPP) can be left floating or connected to VCC for normal write operation
- Write cycle time: ~1 ms internal

**Pinout: `DIP28_2764`** — same physical pinout as 2764/27128

**Algorithm:** In the Firestarter database, AT28C64 and AT28C256 (Atmel) use `EPROM_STD` algorithm, while Microchip 28C64A/28C256 also use `EPROM_STD`. This is because these chips are compatible with the standard JEDEC programming timing, though they use internal self-timed write cycles.

The canonical AT28C010 (32-pin) uses `EEPROM_POLL` — which is the proper byte-polling algorithm for these devices.

**True 28C write algorithm (for `EEPROM_POLL`-flagged chips):**
1. Assert OE high (disable read)
2. Set address
3. Set data
4. Assert WE low for tWP (minimum 100 ns)
5. Deassert WE — internal write timer starts
6. Poll: read DQ7 at target address; if complement of written bit 7, still busy; if matching, done
7. Typical tWC: 1 ms (AT28C010), 200 µs–1 ms (AT28C64/256)

**SDP on AT28C256:**
- Atmel AT28C256 has SDP enabled from factory
- Requires unlock sequence before each byte or page write
- Page size: 64 bytes for AT28C256

**VPP/WP pin behaviour:**
- AT28C64/256 pin 1: if VPP = 12 V applied during read, chip enters ID mode (reads manufacturer/device ID at 0x00/0x01)
- At VCC = 5 V: pin 1 = WP input (active LOW = write protect); leave at VCC or float for normal operation
- For ID reading: raise pin 1 to 12 V, CE low, OE low → read mfr/device byte

---

## 5. Cross-Family Programming Comparison Table

| Algorithm        | VPP     | Pulse Control     | Completion Check      | Unlock Seq | Notes                          |
|-----------------|---------|-------------------|-----------------------|------------|-------------------------------|
| `EPROM_LEGACY`  | 18/13V  | 50 ms, PGM pin    | Readback verify       | None       | 2716/2732 only                |
| `EPROM_STD`     | 12-13V  | 50/20 ms, PGM pin | Readback verify       | None       | 2764–27512                    |
| `EPROM_QUICK`   | 12-13V  | 100 µs, PGM pin   | Readback verify       | None       | 27Cxxx CMOS                   |
| `FLASH_AMD_STD` | None*   | Self-timed        | DQ7 poll / toggle bit | 5555/2AAA  | SST29EE, AT29Cxx              |
| `FLASH_AMD_ALT` | None*   | Self-timed        | DQ7 poll / toggle bit | 5555/2AAA  | AM29Fxxx, SST39SFxxx          |
| `FLASH_INTEL`   | 12V     | Self-timed        | Status register bit 7 | None       | AM28Fxxx, Intel 28Fxxx        |
| `EEPROM_POLL`   | None*   | Self-timed        | DQ7 poll              | SDP unlock | AT28C010, AT28C040            |

\* VPP pin present as write-protect, not required for normal programming at 5 V VCC.

---

## 6. Chip ID Reading Methods by Family

| Family        | Method                        | Address for mfr | Address for device |
|--------------|-------------------------------|-----------------|-------------------|
| 27Cxxx (UV)  | A9 = 12 V, CE/OE low         | A0=0            | A0=1              |
| Flash AMD    | SW command: 0x5555←0xAA, 0x2AAA←0x55, 0x5555←0x90 | 0x0000 | 0x0001 |
| Flash Intel  | Write 0x90 to any addr        | 0x0000          | 0x0001            |
| 28Cxxx EEPROM| VPP=12V on pin 1, CE/OE low  | A0=0            | A0=1              |

---

## 7. Key Gotchas and Decisions for Firestarter

1. **2716 vs 2732 pinout reuse:** Both use `DIP24_2716` pinout in Firestarter, but the 2732 has VPP and OE sharing pin 20. The firmware must handle this difference within `EPROM_LEGACY` dispatch.

2. **27256 vs 27512 VPP location:** 27256 uses VPP on pin 1; 27512 uses VPP on pin 22 (the OE pin slot). These are different pinout entries (`DIP28_27256` vs `DIP28_27512`).

3. **FLASH_AMD_STD vs FLASH_AMD_ALT:** Both use identical 0x5555/0x2AAA command sequences. The distinction maps to minipro's 0x05 vs 0x06 protocol IDs and covers different chip generations, but the Firestarter firmware can share the command sequence implementation between both.

4. **AM28Fxxx is Intel command set, not AMD:** "AM28F" = Intel-compatible. "AM29F" = AMD command set. This is a major naming trap.

5. **SST39SF vs SST39VF:** SF variants (SST39SF010/020/040) require VCC=5V and list VPP=12V for WP. VF variants operate at 2.7–5.5V. Do not assume they are interchangeable.

6. **EEPROM_POLL vs EPROM_STD for 28Cxx:** The Firestarter DB currently assigns `EPROM_STD` to some 28C devices (AT28C64, AT28C256) and `EEPROM_POLL` to others (AT28C010, CAT28C010). The correct algorithm for all 28Cxxx is EEPROM_POLL; `EPROM_STD` in the DB for these chips is likely a gap in the pipeline that this project needs to address.

7. **VPP calibration:** The firmware communicates VPP in millivolts (`vpp * 1000`). The RURP shield has a hardware DAC/regulator for VPP. The correct millivolt value must match the chip's datasheet requirement exactly.

8. **Blank state:** UV-EPROMs erase to 0xFF. Flash and EEPROM also erase to 0xFF. Blank check = verify all bytes are 0xFF.

---

## 8. Database Cross-Reference: Protocol ID → Algorithm → Chip Count

From `minipro_complete_db.json` (767 total chips):

| Protocol | Algorithm      | Chip Count | Notes                          |
|----------|---------------|------------|-------------------------------|
| 0x07     | EPROM_STD     | 237        | Largest family                 |
| 0x06     | FLASH_AMD_ALT | 190        | Second largest                 |
| 0x08     | EPROM_QUICK   | 127        | 27Cxxx CMOS                   |
| 0x0B     | EPROM_LEGACY  | 53         | Oldest devices                 |
| 0x10     | FLASH_INTEL   | 39         | Intel/AMD 28Fxxx               |
| 0x0D     | EEPROM_POLL   | 18         | 28Cxxx parallel EEPROM         |
| 0x05     | FLASH_AMD_STD | 27         | SST29EE, AT29Cxx               |
| 0x28     | SRAM_STD      | 10         | SRAM (no programming)          |

---

*Research complete. Sources: Firestarter codebase analysis (`minipro_complete_db.json`, `database.py`, `flash_utils.h`, `pinouts.json`), datasheet knowledge for AMD 27/29 series, Intel 28F series, Atmel AT28C series, and SST 29/39 series.*
