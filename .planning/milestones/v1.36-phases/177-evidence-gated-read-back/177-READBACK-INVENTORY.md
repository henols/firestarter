# PRUNE-04 Read-Back Call-Site Inventory

Phase 177, plan 177-03. The evidence behind PRUNE-04's closure: every place in
`firestarter_app` that reads a device or a bus back to compare it against
something, named, and disposed with a reason. Coverage is judgeable, not
asserted — the search method that produced it is stated below, and the
`dev test` engine's own two `operator.read_eprom` call sites are additionally
pinned by a machine census in `firestarter_app/tests/test_readback_inventory.py`,
which is proven to redden against a planted third call site rather than merely
claimed to cover the module.

## Search method

1. `/usr/bin/grep -rn "read_eprom(" --include=*.py firestarter/` — every read
   entry point in the package.
2. `/usr/bin/grep -n "operator\.[a-z_]*(" firestarter/chip_test.py` piped
   through `sort | uniq` — the complete set of operator calls the engine
   makes.
3. `/usr/bin/grep -n "sha256\|!= source\|== source"` across
   `eprom_operations.py`, `cli_handlers.py`, `chip_test.py` — every host-side
   content comparison.
4. `/usr/bin/grep -rn "read.back\|read-back\|readback" --include=*.py firestarter/`
   — prose/name evidence of a read-back concept, to catch anything the first
   three passes missed by name alone.

(`/usr/bin/grep` deliberately, not the devcontainer's PATH `grep`, which is
ugrep and honors `.gitignore` and can silently under-scan.) The `dev test`
engine's own two sites are additionally pinned by an `ast` walk over
`firestarter/chip_test.py`'s parsed source — see
`firestarter_app/tests/test_readback_inventory.py` — rather than trusted to a
text search alone.

## The eight-row inventory

| # | Site | What it reads | What it compares against | Disposition |
|---|------|----------------|---------------------------|--------------|
| 1 | `chip_test.py:3108` (`_read_region`, called from `_dispatch_multi_run`) | the **write region**, not the whole device (region-scoped since quick task 260821-wna) | `expected` — the pattern buffer already in memory | **EXCLUDED by D-1.** This is the fingerprint diagnostic. Stays a read-back by design; Phase 177 gates *when* it runs, not *what* it is. A verify returns a bool and one mismatch address; `classify_fingerprint` needs the whole mismatch distribution (`ff_ratio` across the buffer, bit-clustering across every diff offset), so converting this site to a verify would delete the diagnostic R2 exists to preserve. |
| 2 | `chip_test.py:3338` (`_read_region`, called from `_dispatch_sdp_leg`) | the SDP leg's fixed region | `expected_readback` (pattern A) | **EXCLUDED — the SDP leg.** Its own docstring states the verdict comes from comparing the read-back bytes against what should be there, never from `write_eprom`'s own bool. The read-back IS the verdict, not decoration; converting it to a verify would delete the only evidence the leg exists to produce. |
| 3 | `chip_test.py:2843` (`_read_region`, called from `_resolve_write_target`) | a `_UV_PROBE_BLOCK_LENGTH` block, UV-slot policy only | nothing — the read IS the state lookup that computes the mask | **NOT APPLICABLE.** No held buffer exists to compare against. Also unreachable on a non-UV plan: `_resolve_write_target` returns an unmasked target before any read whenever `region_policy != REGION_POLICY_UV_SLOT`. |
| 4 | `chip_test.py:2642` (`_dispatch_read`) | the whole device, `runs` times | run *N* against run *N-1* — read-vs-read, no held buffer | **NOT APPLICABLE.** The metric is read repeatability, which a verify cannot measure — a verify proves the device matches a buffer, not that two reads of the device agree with each other. This is PRUNE-08 / seed R3's territory, Phase 180. |
| 5 | `eprom_operations.py:1079` (`consistency_check_eprom`) | whole device × N | read-vs-read SHA | **NOT APPLICABLE**, same reason as #4 — read repeatability, not a compare-to-held-buffer. |
| 6 | `eprom_operations.py:1195-1250` (`write_cycle_eprom`'s read block) | **the whole device** | `source_sha` — the SHA of the source image the method already holds (computed at `:1171`, compared at `:1246-1250`) | **EXCLUDED — the one genuine match in the package, outside the `dev test` engine.** This is the uno328pb read-repeatability oracle: its own docstring at `:1166-1168` forbids refactoring the read-back into a parallel read implementation, and D-1's reasoning forbids converting it to a verify for the same reason as row 4 — it exists to prove the device reads back the same bytes it was written, repeatedly, not merely that it matches once. It is not the `dev test` engine (`chip_test.py`); it is a separate `EpromOperator` method never called by `derive_plan`'s dispatch chain. |
| 7 | `cli_handlers.py:508` (the `read` command), `eprom_operations.py:1829` (`dev_read_eprom`, hexdump) | whole device / a window | nothing | **NOT APPLICABLE** — no comparison at all; nothing to replace with a verify. |
| 8 | `firmware.py:653-667`, `py32_dfu.py:_verify_readback` | DFU flash upload | the firmware payload | **OUT OF SCOPE** — the DFU bus, not the EPROM bus; not "the engine". |

## The two engine call sites, pinned

`firestarter/chip_test.py` contains exactly two `operator.read_eprom(...)`
call sites: rows 1 and 2 above, both routed through the shared
`_read_region` helper (`_read_region`'s own docstring: "the ONE place this
slice lives; every region read-back in this module goes through this
function"). `firestarter_app/tests/test_readback_inventory.py` censuses this
by `ast`, not by grep, and is proven to redden against a planted third call
site rather than merely asserted.

## The replacement primitive, named

`EpromOperator.verify_eprom(eprom_name, eprom_data_dict, input_file_path,
operation_flags=0, address_str=None) -> bool`
(`firestarter_app/firestarter/eprom_operations.py:2094-2101`). It issues
`COMMAND_VERIFY` and streams host→device; the firmware compares in place and
early-returns on the first mismatch. This is the primitive R1 names as
cheaper than a read-back everywhere a read-back is genuinely replaceable —
which, after this inventory, is nowhere left inside the engine.

## PRUNE-04's closure

Once D-1's exclusion (row 1) and the seed's own SDP carve-out (row 2) apply,
**the `dev test` engine's in-engine population of read-whole-device-to-
compare-a-held-buffer sites is measured EMPTY.** Row 6, the one genuine match
in the whole package, is outside the engine and is named-and-excluded with its
own reason: it is the uno328pb read-repeatability oracle, and converting it
would repeat, one layer down, the exact error D-1 corrects at the engine
layer. PRUNE-04 therefore closes as **measured-empty, with the named-and-
excluded reason recorded** — the same standing this milestone grants
PRUNE-08 for closing as *measured, not worth doing*. The census gate reddens
if a third `operator.read_eprom` site ever appears in `chip_test.py`.
