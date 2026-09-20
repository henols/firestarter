---
title: Phase 201 — the one-flag-deep latency, the narrowed uv-write-shortcut divergence, and backlog 999.44's retirement
date: 2026-09-20
context: Phase 201 Plan 05 (D-11, the folded 2026-09-08 todo, backlog 999.44) — read from the live source before writing any of the three findings below
---

# Phase 201 — three findings no test in this phase carries

Plan 201-05 closes BLANK-02's third leg with a source-contract gate, but a gate proves shape, not
judgement. Three findings this phase established are not the kind a test can carry, and are
recorded here so a later reader does not have to reconstruct them from a bench transcript, a
closed phase, or a stale-pointing todo.

## 1. The latency on the two out-of-scope sites is one flag deep, not safely latent (D-11)

D-10 changes exactly one write-init call site — `firestarter_fw/src/proms/eprom.cpp:145`. The other
two write-init sites that call the whole-device blank check are left byte-unchanged:
`firestarter_fw/src/proms/flash_intel.cpp:95` and `firestarter_fw/src/proms/flash_nor_unlock.cpp:105`.
Both are guarded by the same shape, read directly from the live source:

```
if (is_flag_set(FLAG_CAN_ERASE) && !is_flag_set(FLAG_SKIP_ERASE)) {
    <protocol-specific erase>
}
if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
    mem_util_blank_check(handle);
}
```

`FLAG_CAN_ERASE` marks the part as electrically erasable; when it is set and `FLAG_SKIP_ERASE` is
clear, the erase immediately above the check runs and leaves the device blank, so the whole-device
scan passes trivially. **That is the same mechanism that hid the whole-device defect on
`eprom.cpp`'s own site for its entire life before this phase.** It has not gone away on these two
sites — it has just never been asked to fail, because nothing on the CLI path sets `FLAG_SKIP_ERASE`
without also being willing to eat a whole-device refusal.

**Named non-claim: these two sites are not safely latent. They are one flag deep.**
`firestarter write --skip-erase` sets `FLAG_SKIP_ERASE` (Click option at
`firestarter_app/firestarter/cli_handlers.py:572-578`; the flag-mapping docstring at
`firestarter_app/firestarter/cli_handlers.py:341-345` states explicitly that `-b`/`--no-blank-check`
does **not** imply `--skip-erase`, so the two are independently settable). Passing `--skip-erase`
against an electrically-erasable part on either of these two protocols suppresses the erase and
makes the identical whole-device `mem_util_blank_check` refusal fire on a genuinely non-blank
part — the exact defect BLANK-01/BLANK-02 fix on `eprom.cpp`, unfixed here by design (D-10, deferred
because region-scoping these two sites needs its own bench budget this phase does not have).

**Which validated silicon this reaches today, verified against the live registry rather than
assumed.** `/workspaces/VALIDATED-EPROMS.md` lists four validated chips whose `electrical.type` is
`Flash/EEPROM`: `AE29F2008`, `W29C020`, `W29C040` (all `PROTO_FLASH_5V_PAGE`, algorithm 5) and
`SST39SF020` (`PROTO_FLASH_NOR_UNLOCK`, algorithm 6). Reading
`firestarter_fw/src/proms/flash_5v_page.cpp:66-73` directly shows that protocol's write-init
performs **no blank check at write-init at all** — the file's own comment states the part
auto-erases per page during the write loop, so the pre-write check was "a false precondition, not a
safety net," and `FLAG_SKIP_BLANK_CHECK` is consequently unread on that protocol. **`AE29F2008`,
`W29C020` and `W29C040` are therefore not reachable by this latency at all, regardless of
`--skip-erase`.** Of the four, only `SST39SF020` sits on one of D-11's two named sites
(`firestarter_fw/src/proms/flash_nor_unlock.cpp:105`) and is reachable by it today. `flash_intel.cpp`'s protocol
(`PROTO_FLASH_INTEL`, `0x10`) has zero validated chips in the registry as of this writing — the
latency is real on that site the moment a `0x10` part is validated, but nothing has exercised it
yet.

**This is also the mechanism plan 201-06's W27C512 rehearsal relies on.** W27C512
(`electrical.type: EEPROM`, algorithm 7, `PROTO_EPROM_28PIN` → `eprom.cpp`) carries `FLAG_CAN_ERASE`
and is driven with `--skip-erase` specifically so the bench rehearsal can force the whole-device
refusal RED, then confirm the region-scoped fix turns it GREEN, repeatably, without consuming a
non-erasable part. The rehearsal works only because `--skip-erase` reliably suppresses the erase and
lets the underlying blank-check shape decide the outcome — the identical one-flag-deep mechanism
this section documents on the two sites that are NOT fixed this phase.

## 2. The narrowed uv-write-shortcut divergence (folded todo, 2026-09-08) — answered: neither

The folded todo (`.planning/todos/pending/2026-09-08-uv-write-shortcut-disclosure-key.md`) recorded
that `dev test m27c512` passed on a non-blank UV part by passing `FLAG_SKIP_BLANK_CHECK` on a proven
monotonic masked write, while `firestarter write -a` was refused by the identical firmware
write-init pre-flight on the same part, with nothing disclosing the divergence. Its own cited
source, `.planning/research/PITFALLS.md` Pitfall 7, gave the verdict "both, or neither" — either
export a key naming the divergence and make the harness mirror the product path, or accept and
disclose the divergence explicitly.

**This phase removes the premise the todo was filed against.** After BLANK-01/BLANK-02, a write into
a blank region of a non-blank part succeeds through the product's own `firestarter write -a` path,
with no flag needed — the two paths (the `dev test` harness's `FLAG_SKIP_BLANK_CHECK` shortcut and
the product's own write command) now converge on the case the todo's bench evidence exercised: a
blank target region on a non-blank part.

**What remains, stated plainly.** `firestarter_app/firestarter/chip_test.py:3310` still passes
`FLAG_SKIP_BLANK_CHECK` for a MASKED write into a partially-programmed slot, where the target
region itself is genuinely not blank (a proven-monotonic bit-clear, not a blank-region write). That
is a narrower and differently-shaped divergence than the one the todo described — the todo's own
bench transcript was about a blank target region behind a non-blank device, which BLANK-01/BLANK-02
now handles identically on both paths.

**Recommendation: neither.** No new report key is warranted. Both of the todo's own stated reasons
for "neither" hold with RPT-A4 landed rather than pending, verified against the live source rather
than quoted from a quotation:

- `plan.is_uv` now reaches the report as a top-level boolean —
  `firestarter_app/firestarter/diagnostic_report.py:1022`: `"is_uv": self.plan.is_uv,`.
- `write_current_source` is exported per write step —
  `firestarter_app/firestarter/diagnostic_report.py:946`:
  `"write_current_source": target.current_source if target else None,`.

A triager reading a UV report already has both facts available: whether the plan is UV at all, and
whether a given write step's source was a probe-masked shortcut. Adding a dedicated
divergence-naming key on top of those two, for a divergence now narrowed to the masked-slot-write
case alone, is not warranted. **Phase 181 closed under v1.36**
(`.planning/milestones/v1.36-phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-CLOSURE.md`),
so the todo's own pointer at "deferred to Phase 181" is stale; this section is the todo's answer,
not another re-pointing.

## 3. Backlog 999.44 is retired; flash headroom measured

Backlog 999.44 (`.planning/todos/pending/2026-08-30-write-init-blank-check-is-whole-device.md`)
prescribed two halves. **Half (b) — passing `FLAG_SKIP_BLANK_CHECK` on `uv-slot` writes in
`chip_test.py` — shipped in v1.36 Phase 179 and quick `260821-wna`**, and is live today at
`firestarter_app/firestarter/chip_test.py:3310`
(`FLAG_SKIP_BLANK_CHECK if _is_monotonic_masked_target(resolved_target) else 0`). **This phase closes
half (a)** — region-scoping the firmware write-init check on `eprom.cpp`. With both halves landed,
backlog 999.44 is retired.

The todo's third consequence — "the report blames the chip" when a tool defect produces a BAD
verdict against the wrong target — is addressed by construction: the region-scoped refusal now
names a byte that is genuinely inside the operation's own target region, rather than an arbitrary
byte up to 262 KB away from a 256-byte slot write. A future BAD verdict from this check is a real
finding about the targeted region, not a tool artifact misattributed to the chip.

**Flash headroom, measured because nothing automated checks it.** `scripts/baseline/` does not
exist in this repository, and no CI leg gates firmware image size —
`firestarter_fw/platformio.ini:78-82` overrides `board_upload.maximum_size` to `32768` against the
real ATmega32U4-on-Caterina ceiling of `28672` B, with the file's own comment stating "the linker no
longer protects the top 4096 B." This phase's final `pio run` (plan 201-05, adding a test-only file
with zero production-source bytes changed) reports the identical figure plan 201-04 left:
**leonardo Flash 24134/32768 B (73.7%)**, or **24134/28672 B (84.2%) of the real ceiling, 4538 B
margin** against it. The running trail across this phase: 23816 B (pre-phase baseline,
`201-RESEARCH.md`) → 23850 B (201-02) → 23932 B (201-03) → 23970 B (201-04 Task 1) → 24134 B
(201-04 Task 2, unchanged through 201-05). `uno` and `uno328pb` remain `SUCCESS` throughout,
unaffected by any change in this phase (`SERIAL_ON_IO` compiles the progress-emission block out on
those targets). This is a measurement recorded for trend visibility across the phase, not an
enforced pass — no gate exists to make it one.
