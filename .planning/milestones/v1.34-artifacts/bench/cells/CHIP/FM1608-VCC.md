# FM1608-VCC.md — resolving CONTEXT.md's open `vcc_mv: 3300` item (162-01 Task 3, R2)

**Conclusion: the field is decorative — display-only. It is never transmitted to the firmware,
no VCC *control* path exists on any shield revision, and the socket runs at the board's fixed
5 V rail regardless of what the DB says.** All three commands below were run against the v1.33
arm / this rig's firmware source, and none needs a device.

## Command 1 — the wire-dict key set (vcc_mv/vdd_mv are absent from what's transmitted)

```bash
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
/workspaces/.v1.34-arms/v133/.venv/bin/python -P -c '
from firestarter.database import EpromDatabase
db = EpromDatabase(); full = db.get_eprom("FM1608")
wire = db.convert_to_programmer(full)
assert "vcc_mv" not in wire, wire
assert "vdd_mv" not in wire, wire
print("PASS: vcc_mv/vdd_mv absent from wire dict; keys =", sorted(wire))
'
```

Verbatim output:
```
PASS: vcc_mv/vdd_mv absent from wire dict; keys = ['algorithm', 'bus-config', 'chip-id', 'flags', 'memory-size', 'pin-count', 'pulse-delay', 'vpp_mv']
```

`convert_to_programmer()` (`firestarter/database.py`) is the one function that builds what goes
to the programmer. Neither `vcc_mv` nor `vdd_mv` is in its output. **Strongest citation.**

## Command 2 — negative grep: no VCC setter exists anywhere in firmware source or headers

```bash
grep -rn "rurp_set_vcc\|set_vcc\|write_vcc\|VCC_SET" /workspaces/firestarter/src /workspaces/firestarter/include
```

Verbatim output: **zero matches** (grep exit 1 / negated-grep exit 0). The only VCC-named symbol
in the firmware is `rurp_read_vcc_mv()` (`src/boards/rurp_common.cpp:42`) — a **read**, computed
from the internal 1.1 V bandgap (`VCC_mV = 1126400 / ADC_reading`), used only to format the
`hw`/`info` reply (`src/hardware_operations.cpp:69-76`). `include/eprom_params.h:31-33` states the
constraint explicitly: *"`verify_mode`: WHEN to verify, never at what VCC. The datasheets'
raised-VCC verify margin is unreachable on this shield's ~6.25 V ceiling, so no value in this
column may ever encode a verify VCC."* There is no setter, no wire field, no register. **No
shield revision can honour a 3300 mV VCC because nothing in the firmware can ask for one.**

## Command 3 — byte-diff: the field is pre-existing on both arms, never a v1.33 finding

```bash
diff <(python3 -c 'import json;d=json.load(open("/workspaces/.v1.34-arms/control/firestarter/data/chip_database.json"));print(json.dumps([r for r in d["RAMTRON"] if r["part_number"]=="FM1608"],sort_keys=True))') \
     <(python3 -c 'import json;d=json.load(open("/workspaces/.v1.34-arms/v133/firestarter/data/chip_database.json"));print(json.dumps([r for r in d["RAMTRON"] if r["part_number"]=="FM1608"],sort_keys=True))')
```

Verbatim output: **empty diff, exit 0.** The two arms' FM1608 rows are byte-identical:

```json
[
  {
    "electrical": {
      "pin_count": 28, "size_bytes": 8192, "type": "FRAM",
      "vcc_mv": 3300, "vdd_mv": 5000, "vpp_mv": 12000
    },
    "part_number": "FM1608",
    "pinout": "DIP28_JEDEC_SRAM_8K",
    "programming": {
      "algorithm": 40, "chip_id_check": false, "chip_id_value": "0x00000000",
      "infoic_page_size_raw": 256, "protect_off_before": false,
      "protect_on_after": false, "pulse_duration_us": 0
    },
    "support_status": "supported"
  }
]
```

So `vcc_mv: 3300` **cannot be a v1.33-caused finding** — it is identical, generated data on both
arms.

## Root cause — the `build_db.py` ordering interaction (`_PHASE84_RELABEL`)

The 3300 is **genuine upstream data, correctly decoded**, not invented. Upstream `infoic.xml`
carries `FM1608`'s `voltages="0x0100"`; `build_db.py`'s `VCC_VOLTAGES = {0x01: 3300, …}` maps
`(0x0100 >> 8) & 0x0F == 0x01` to 3300 correctly.

The SRAM-class correction that *should* override it for FM1608 (upstream types it `type="4"` /
MP_SRAM) does not fire, because of an ordering interaction between two blocks in the same
generator function, live-verified in this session at their exact current line numbers:

- **`tools/build_db.py:613`** — `_PHASE84_RELABEL = {"FM1608": "FRAM"}` sets `_etype = "FRAM"`
  for this one part (comment at `:607-612` states it "must NOT touch proto_id / pinout / vpp /
  algorithm" — it does not touch those, but it silently disables an unrelated correction instead).
- **`tools/build_db.py:745`** — `if _etype == "SRAM":  chip_entry["electrical"]["vcc_mv"] = \
  chip_entry["electrical"]["vdd_mv"]` — the correction that maps SRAM-class parts onto the
  shield's real fixed 5 V rail. Because line 613 runs before line 745 and re-labels `_etype` to
  `"FRAM"` (not `"SRAM"`), this `if` evaluates **False** for FM1608 alone, and the 3300 mV
  test-rail value from upstream survives uncorrected into the generated DB.

The generator's own correction-block comment (`:738-744`) is the authoritative statement of
shield behaviour: *"Static-memory parts have ONE supply rail, so minipro's vcc (read) vs vdd
(program) split is meaningless for them and upstream's lower test-rail vcc misreports the real
supply. The shield feeds SRAM-class parts a fixed 5V, which is vdd. … SRAM only. On UV-EPROM and
Flash/EEPROM, vdd is the ELEVATED program rail (~6.5V) and must never be surfaced as operating
Vcc."*

**Classification: a pre-existing `build_db.py` decode gap** — the SRAM-class vcc→vdd
substitution should key on the SRAM *family* (including FRAM), not the post-relabel string. It
is:
- **not Phase 162 work** — this phase changes no product code, and `chip_database.json` is
  GENERATED, never hand-edited, per `/workspaces/CLAUDE.md`;
- **not Phase 165 work either** — Phase 165 owns v1.33-*caused* regressions, and this gap is
  byte-identical on both arms (Command 3, above);
- **filed as a backlog item in plan 162-10**, not fixed here. Its only live consequence is that
  `firestarter info FM1608` prints a wrong, user-facing `Vcc: 3.3V`.

## Interaction with the byte-0 write defect: none, in either direction

`.planning/todos/pending/fm1608-byte0-write-never-lands-register-cache-elision.md` hypothesises a
digital strobe-sequencing defect (`rurp_write_to_register`'s cache-skip eliding all three
shift-register strobes on the first `memory_set_data(0, byte0)` call), independent of supply
voltage. A value that is never transmitted (Command 1) and never actuated (Command 2, no setter
exists) cannot participate in a strobe-sequencing bug: the socket is at the board's fixed 5 V rail
on every run regardless of what `vcc_mv` says, so there is no under-voltage condition to blame a
missing byte-0 write on, and equally no way for the field to excuse one. The todo's own falsified
list already rules out voltage-adjacent explanations independently (three uniform writes at
different patterns all left byte 0 at `0xFF`; a triple-read after one write was byte-identical; a
single-byte `write -a 0` reproduced it).

**Prediction for FM1608's `dev test` position, recorded here so it cannot be mistaken for a
discovery:** `derive_plan` gives FM1608 two full-device 8192 B writes with different patterns
(`write` supported, policy full-device, region `(0, 8192)`, payload `alternate`) each followed by
a verify over the same region. If the byte-0 defect manifests, the expected shape is `write`
reporting success and `verify` going BAD with a single-byte mismatch at offset `0x0000` and every
other byte correct. That row must cite the todo inline as **known-carried, pre-existing** — it
must not enter Phase 165's failure set or Phase 166's findings as a v1.34 discovery.

## Structural NAs on FM1608 (not an omission)

`id` is structurally NA (`chip_id_check: false`, `chip_id_value: 0x00000000`); `blank-check` is
structurally NA ("blank-check not applicable to FRAM (volatile/byte-rewritable)"); `erase` is
structurally NA (`FLAG_CAN_ERASE` not set for this chip). Three of the six D-02 comparison cells
are NA on this part by construction. See `DERIVE-PLAN.json` for the machine-measured confirmation.

## Socket VCC — not measured

**Socket VCC not measured** — no VCC control path exists in firmware (`eprom_params.h:31-33`,
`rurp_read_vcc_mv()` is read-only) and the shield's rail is fixed; v1.34 makes no electrical
claim. The only way to obtain an actual figure would be a multimeter on FM1608's pin 28 with the
part seated, which is outside every requirement in this phase and outside CONTEXT.md's deferred
list (no program-window electrical claims). Not requested here.
