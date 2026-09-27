# Rev 1 schematic — extracted facts

Source: `firestarter_fw/document/rurp_schematics_rev1.pdf` (KiCad 6.0.7,
`W27C512Programmer.kicad_sch`, titled "Relatively Universal ROM Programmer", Rev 0 in the title
block, Anders Nielsen / abnielsen.com). **This is the Rev 1 sheet. It is not evidence about Rev 2.x
boards**, whose divider and control-register assignments differ.

Extracted by decompressing the PDF content streams and collecting `(...) Tj` text operators — so
these are the sheet's *labels*, with **no net connectivity**. Reproduce with:

```bash
python3 -c "
import re,zlib
d=open('firestarter_fw/document/rurp_schematics_rev1.pdf','rb').read()
out=[]
for m in re.finditer(rb'stream\r?\n(.*?)endstream', d, re.S):
    try: out.append(zlib.decompress(m.group(1)))
    except Exception: pass
txt=b'\n'.join(out).decode('latin-1')
print(' | '.join(re.findall(r'\((.*?)\)\s*Tj', txt)))"
```

## 1. The boost converter and what it can actually generate

U1 is a **MIC2288**. The sheet carries its own design note, verbatim:

```
8.83V to 21.92V
Vout = vref * (R1/R2+1)
vref = 1.23
"R1" = R8 + RV1 + partial RN1 (2350+4700)
"R2" = partial RN1 (4700)

VPE-Max = 1.23 * ((22000+50000+2350+4700)/4700 + 1)   == 21.92V
VPE-Min = 1.23 * ((22000+0+2350+4700)/4700 + 1)       == 8.83V
```

Note these are the *feedback network's* R1/R2. **They are unrelated to the firmware's `VALUE_R1` /
`VALUE_R2`, which are the ADC sense divider.** The name collision is a live trap.

**Why this matters to the spec:** the sheet predicts a maximum VPE of **21.92 V**. Phase 199's meter
read **22.14 V** at max pot — agreement to +1.0 %. The firmware's ADC read **23900 mV** on the same
rail, which is **9 % above a voltage this feedback network cannot produce**. The meter agrees with
the hardware; the ADC is the outlier. This is the third independent line of evidence that the error
is in the measurement chain, not in the rail.

`RV1` is the 50 kΩ trimpot the operator sets by hand.

## 2. Resistor value census — the whole sheet

| Value | Count |
|---|---|
| 22k | 38 |
| 4k7 | 21 |
| 4k7 networks (RN1–RN9) | as above, in SIL packages |
| 1k | 4 |
| **270k** | **3** |
| 50k (RV1, the trimpot) | 1 |

**There is no 44k part anywhere on the sheet.** The firmware's `VALUE_R2 44000`
(`firestarter_fw/include/rurp_shield.h:48`) therefore does not name a single component. The
plausible construction is 22k + 22k in series, but that is an inference and has never been
verified — which is exactly what Task 4 Stage 3 measures.

`R16` is the one 270k explicitly visible next to the sense network, matching `VALUE_R1 270000`.

**The discriminator Task 4 Stage 3 is looking for**, since an in-circuit reading of one leg sees the
other in parallel:

| If R2 really is | Then A2→GND reads about |
|---|---|
| 44k (22k + 22k) | `44k ∥ 270k` = **37.83 kΩ** |
| 47k (a standard E12 value) | `47k ∥ 270k` = **40.05 kΩ** |

~2.2 kΩ apart, well inside meter resolution. An in-circuit reading is a **lower bound** on the true
value — parallel paths only lower it — so this corroborates, it does not prove.

## 3. Control nets named on the sheet

`VPE`, `VPE_TO_VPP`, `VPE_ENABLE`, `P1_VPP_ENABLE`, `A9_VPP_ENABLE`, `~{REG_DISABLE}`, `CTRL_LE`,
`RMSBLE`, `RLSBLE`, `~{RW}`, `~{ROM_CE}`, `~{ROM_OE}`.

Note `VPE_TO_VPP` is a **control** signal, consistent with the drop bit switching the regulator's
feedback network rather than inserting a passive series drop (spec decision D-B). Task 4 tests this.

## 4. Jumper legends, as printed on the sheet

- `JP1` — "24pin ROM VCC"
- `JP2` — ">=SST39SF020 & 28C512 need A17"
- `JP3` — "W27C010/AT27C010 needs p1 VPE/VPP (32 pin)"

## What is NOT in this extract

No net connectivity, so **the extract cannot say which node the ADC divider taps** — before or after
any drop element, or where a probe point is accessible. Task 4 must identify and record the probe
point physically. The Rev 2.x sense network is not covered at all; the only Rev 2 artifact in the
repo is `firestarter_fw/document/rurp_ctrl_reg_rev2.png` (control register, not the analog path).
