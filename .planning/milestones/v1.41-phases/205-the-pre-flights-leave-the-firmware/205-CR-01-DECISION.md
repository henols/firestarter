# 205-CR-01 Decision Record

**Gap:** `205-VERIFICATION.md`, `gaps[0]` — truth 9, `status: failed`. Delivers the gap's third
`missing` item: a recorded decision on whether the fix lands in Phase 205 or is deferred.

## 1. The decision

CR-01 is fixed inside Phase 205, before FWBLANK-01 is considered complete in substance. It is
**not** deferred with an accepted-risk window, and it is **not** filed to backlog. Plan 205-08,
tasks 1 and 2, close it: `write_blank_guard.is_erase_exempt` and `requires_blank_check` gain a
keyword-only `address` parameter, and protocol `0x06`'s exemption is withdrawn at any non-zero
write address.

## 2. The alternative that was displaced

The alternative considered was deferring CR-01 with a stated accepted-risk window — the shape
D-04's `write -b` skew was carried in, priced and stated in the phase record (`205-CONTEXT.md` §
"The `FLAG_SKIP_BLANK_CHECK` bit", D-04) rather than silently fixed or silently carried.

It was not taken here because the two regressions are not the same shape. D-04's regression is a
skew between two software versions the operator controls and can roll back (a post-205 host
against pre-205 firmware): `write -b` on a non-blank UV part is *refused* by the old firmware
where it works on the new one — a functionality regression with a safe failure mode, gated behind
an explicit `-b` flag, and reversible by reflashing. CR-01's is a silent, irreversible overwrite of
a non-blank flash region with no operator-visible signal at all, on 190 of 190 shipped
protocol-`0x06` rows, reachable through an ordinary `-a` with no flag required to opt in. A risk
window is a reasonable instrument for the first kind of regression and not for the second: there is
no safe interval during which an irreversible, silent data-integrity hazard is acceptable to carry
forward.

`205-VERIFICATION.md` also establishes that no later phase covers it: Phase 206 is `dev
test`/session-lease work and Phase 207 is a version bump plus a wiki page. Deferring here would
have meant deferring indefinitely, not deferring to a named future phase.

## 3. What changed, in behaviour terms

At address `0`, protocol `0x06`'s erase-capable exemption is unchanged — `firestarter erase`
followed by `write` at address `0` still pays no guard read, because
`flash_nor_unlock_erase_execute` erases the whole chip there and the exemption is genuinely sound.
At a non-zero address, the exemption is withdrawn: the write falls back to the ordinary
region-scoped host blank-check read `requires_blank_check` already performs for every
non-erase-exempt guarded part. A blank target region still writes; a non-blank one is refused with
the existing one-line host refusal.

| Protocol | Address `0` | Non-zero address |
|---|---|---|
| `0x06` (NOR unlock) | Exempt before, exempt after | Exempt before, region-scoped host check after |
| `0x07` / `0x08` / `0x0B` (UV-EPROM) | Unaffected — `eprom_erase_execute` delegates to `eprom_internal_erase`, which reads no address at all | Unaffected, same reason |
| `0x10` (Intel flash) | Unaffected — `flash_intel_erase_execute` writes its erase setup and confirm bytes to hard-coded address `0` regardless of `handle->address` | Unaffected, same reason |

## 4. The regression provenance

Plan 205-03's commit `1cf1b22` deleted the unconditional whole-device
`mem_util_blank_check(handle)` call from `flash_nor_unlock_write_init`. That call was the backstop
that made the host's address-blind exemption safe in practice before this phase: it scanned the
whole device on every write regardless of what the erase actually touched, so a sector erase
leaving the rest of the device untouched was still caught downstream. Phase 205 removed that
backstop as part of retiring the firmware's own pre-flight machinery (FWBLANK-01/02/03), and
nothing on the host replaced the address-scoping knowledge it implicitly carried until this plan.

## 5. The design decisions and their reversibility ratings

| Decision | Summary | Reversibility |
|---|---|---|
| D-G1 | The predicate lives in `is_erase_exempt`, with a keyword-only `address`, threaded through `requires_blank_check`. An additive parameter, default `0`, behaviour-preserving for every existing caller. | reversible |
| D-G2 | A non-zero-address `0x06` write falls back to the ordinary region-scoped blank check — it is checked, not refused. The **rejected** alternative — refusing the write outright — is the `one-way` route: a user-facing contract change on 190 shipped chip models that would become load-bearing in operator scripts within one release and could not be walked back without a second contract change. | reversible (route taken); the declined refusal route would have been `one-way` |
| D-G3 | No sector-size model is invented; any non-zero address withdraws the exemption conservatively, without attempting to narrow further to "inside the erased sector." The database carries no sector-size field, so inventing one would be guessing in the unsafe direction. | reversible |
| D-G4 | An absent or unparseable `-a` resolves to address `0`. A malformed address stays `_setup_operation`'s own `parse_address`/`ValueError` job — the write never reaches the wire at all — so there is no exemption hazard to guard against, and this module must not change that established error contract. | reversible |

## 6. The user-visible delta an operator could actually notice

A `write -a <non-zero>` on an erase-capable protocol-`0x06` part now performs one additional
region-scoped read before writing, and is refused with the existing one-line host refusal if that
region is not blank. `-b`/`--no-blank-check` remains the documented way past it, and
`--skip-erase` still re-arms the guard on every family regardless of address. A `dev test` partial
write on such a part likewise gains one read, because `chip_test.py`'s `write_eprom` call already
passes a non-zero `address_str` for a partial-write region.

## 7. Scope boundaries this decision did not cross

No firmware file was touched — the fix adds no wire bit and changes no wire field, so the
`constants.py`/firmware-header commit-pair rule does not apply. No wire field changed. The `write`
command's Click docstring was not edited — its claims about the host's blank-check coverage become
more true, not less, and stay accurate unedited. No bench or hardware leg was run — this gap is
host-side Python, provable in-process against a fake serial port. WR-01 and IN-01 are left open
exactly as `205-VERIFICATION.md` left them; they are prose-staleness warnings the verification did
not elevate to gaps, and this plan does not re-open that judgment.

---

*Phase: 205-the-pre-flights-leave-the-firmware*
*Plan: 08 (gap closure)*
*Recorded: 2026-09-22*
