#!/usr/bin/env python3
"""gen_addr_image.py -- word-stamped, address-attributable bench write image generator.

D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It is authored and lives
only under .planning/milestones/v1.34-artifacts/tools/ in the meta repo. It must NEVER be copied into
firestarter/ or firestarter_app/ (in particular not into firestarter_app/tools/, alongside
the existing firestarter_app/tools/gen_test_image.py) -- this phase changes no firmware and
no host source (D-16). Nothing here is imported by, or imports from, either sub-repo.

Recipe (RQ-2, D-05), width 16 -- reproduces Phase 145's behaviour exactly, default for a
65536 B image where 16 bits covers the whole address space and attribution is complete:

    stamp(N) = (N & 0xFF)         if N is even   (low address byte)
             = ((N >> 8) & 0xFF)  if N is odd     (high address byte)
    byte(N)  = stamp(N) ^ mask

Each aligned 2-byte word therefore literally stamps its own 16-bit address. That is what
makes a mismatched byte decodable back to a source address -- a property
firestarter_app/tools/gen_test_image.py's pseudo-random data does NOT have (a mismatch there
is detectable but not attributable to an address), which is exactly why this generator is
required instead. The distinction is the one that root-caused Phase 97's pin-31 (A18-aliasing)
defect: an address-line fault must be traceable to which address line aliased, not merely
counted as "N bytes differ".

Recipe, width 32 -- required for the 262144 B W29C020 (Phase 160 D-12/T-160-15): the 16-bit
stamp above repeats every 65536 bytes, so an A16 or A17 aliasing fault on an 18-bit address
space would be invisible to address attribution. A 4-byte rotating word stamp fixes this: the
byte at offset N carries the address byte selected by `N & 3`, i.e. bits [8*(N & 3) ..
8*(N & 3)+7] of N, XORed with the mask:

    stamp(N) = (N >> (8 * (N & 3))) & 0xFF
    byte(N)  = stamp(N) ^ mask

That carries all 18 address bits of the 262144 B part: an A16 fault is visible at offsets
where N & 3 == 2 (byte 2 of the word carries bits [16:24)) and an A17 fault likewise (bit 17
is bit 1 of that same byte). A 262144 B image MUST use width 32 -- using width 16 there would
silently reproduce the exact unattributable-A16/A17 hazard this generator exists to close, so
this tool refuses that combination rather than producing a misleading image.
"""
import hashlib
import sys

WIDTH_16 = 16
WIDTH_32 = 32
VALID_WIDTHS = (WIDTH_16, WIDTH_32)


def gen_image(size: int, mask: int, stamp_width: int) -> bytes:
    """Return `size` bytes of the word-stamped address pattern, XORed with `mask`."""
    if stamp_width not in VALID_WIDTHS:
        raise ValueError(f"stamp_width must be one of {VALID_WIDTHS}, got {stamp_width}")
    if stamp_width == WIDTH_16 and size > 0x10000:
        raise ValueError(
            f"stamp_width=16 covers only 16 address bits (65536 B); refusing a "
            f"{size} B image, which would leave A16/A17 (and above) unattributable "
            f"on aliasing faults -- use --stamp-width 32"
        )
    b = bytearray(size)
    if stamp_width == WIDTH_16:
        for n in range(size):
            stamp = (n >> 8) & 0xFF if (n & 1) else (n & 0xFF)
            b[n] = stamp ^ mask
    else:
        for n in range(size):
            shift = 8 * (n & 3)
            stamp = (n >> shift) & 0xFF
            b[n] = stamp ^ mask
    return bytes(b)


def decode_mismatch(offset: int, observed_byte: int, mask: int, stamp_width: int) -> str:
    """Un-mask an observed byte at `offset` and name which address byte it names.

    Width 16 worked example (RQ-2's simulated A8-stuck-low fault): first mismatch at offset
    0x0101, observed byte 0x00. Un-masking (mask=0x00 for img1) leaves 0x00. The
    offset is odd, so the stamp is the HIGH address byte -- the byte belongs to an
    address whose high byte is 0x00, i.e. address 0x0001, naming A8 (bit 8, the low
    bit of the high byte) as the aliased line.

    Width 32: the unmasked stamp is bits [8*(offset & 3) .. 8*(offset & 3)+7] of the
    source address, so `offset & 3 == 2` names A16..A23 and `offset & 3 == 3` names
    A24..A31 -- on the 262144 B (18-bit) part only A16/A17 (within byte 2) are live.
    """
    unmasked = observed_byte ^ mask
    if stamp_width == WIDTH_16:
        is_high_byte = bool(offset & 1)
        kind = "high" if is_high_byte else "low"
        return (
            f"offset=0x{offset:05X} observed=0x{observed_byte:02X} unmasked=0x{unmasked:02X} "
            f"-> {kind} address byte (width=16), source address high-byte-implied=0x{unmasked:02X}"
        )
    byte_index = offset & 3
    bit_lo = 8 * byte_index
    bit_hi = bit_lo + 7
    return (
        f"offset=0x{offset:05X} observed=0x{observed_byte:02X} unmasked=0x{unmasked:02X} "
        f"-> address byte index {byte_index} (width=32), carries bits [{bit_lo}:{bit_hi}] "
        f"of the source address, value=0x{unmasked:02X}"
    )


def _verdict_line(out_path: str, size: int, mask: int, stamp_width: int, data: bytes) -> str:
    digest = hashlib.sha256(data).hexdigest()
    ff_count = data.count(0xFF)
    return (
        f"{out_path}: {size} bytes, mask=0x{mask:02X}, stamp_width={stamp_width}, "
        f"sha256={digest}, 0xFF_count={ff_count}"
    )


def _run_selftest() -> int:
    """Positive and negative fixtures, all in-memory. Returns 0 iff every leg behaves."""
    ok = True

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal ok
        status = "PASS" if cond else "FAIL"
        if not cond:
            ok = False
        suffix = f" -- {detail}" if detail else ""
        print(f"{status}: {name}{suffix}")

    # Positive leg 1: 65536 B image at width 16 decodes back to source address at probes.
    mask_a = 0x11
    img16 = gen_image(0x10000, mask_a, WIDTH_16)
    check("width16 image is 65536 bytes", len(img16) == 0x10000)
    probes = [0x00000, 0x0FFFF, 0x10000 - 1]
    all_decode_ok = True
    for off in probes:
        if off >= len(img16):
            continue
        observed = img16[off]
        decode_mismatch(off, observed, mask_a, WIDTH_16)  # exercised for crash-freedom
        # A byte that matches the image at its own offset must decode to itself.
        expected_stamp = (off >> 8) & 0xFF if (off & 1) else (off & 0xFF)
        if (observed ^ mask_a) != expected_stamp:
            all_decode_ok = False
    check("width16 positive: probe offsets decode to their own stamp", all_decode_ok)

    # Positive leg 2: 262144 B image at width 32 decodes at a spread including 0x10000/0x20000/0x3FFFF.
    mask_b = 0x22
    img32 = gen_image(0x40000, mask_b, WIDTH_32)
    check("width32 image is 262144 bytes", len(img32) == 0x40000)
    probes32 = [0x00000, 0x0FFFF, 0x10000, 0x20000, 0x3FFFF]
    all_decode_ok32 = True
    for off in probes32:
        observed = img32[off]
        shift = 8 * (off & 3)
        expected_stamp = (off >> shift) & 0xFF
        if (observed ^ mask_b) != expected_stamp:
            all_decode_ok32 = False
    check(
        "width32 positive: probe offsets 0x00000/0x0FFFF/0x10000/0x20000/0x3FFFF decode correctly",
        all_decode_ok32,
    )

    # Positive leg 3: two images with different masks have different SHA-256.
    img_mask_c = gen_image(0x10000, 0x33, WIDTH_16)
    sha_a = hashlib.sha256(img16).hexdigest()
    sha_c = hashlib.sha256(img_mask_c).hexdigest()
    check("positive: differing masks produce differing sha256", sha_a != sha_c)

    # Negative leg 1: a 262144 B size with stamp_width=16 is refused.
    refused = False
    detail = ""
    try:
        gen_image(0x40000, 0x44, WIDTH_16)
    except ValueError as exc:
        refused = True
        detail = str(exc)
    check("negative: 262144 B @ stamp_width=16 is refused", refused, detail)

    # Negative leg 2: A17 alias asymmetry. Inject byte from N to N^0x20000 in both widths;
    # width32 must both DETECT and ATTRIBUTE it to the aliased address line; width16 must
    # DETECT it (bytes differ) but NOT be able to attribute it to A17 specifically (the low
    # 16-bit stamp at N and at N^0x20000 are IDENTICAL, since 0x20000 only touches bits above
    # the low 16 -- so a width16 image cannot even show a detectable difference at this
    # offset pair, which is itself the asymmetry: width16 cannot see this fault class at all).
    src_off = 0x00002
    alias_off = src_off ^ 0x20000  # 0x20002

    img32_faulty = bytearray(img32)
    img32_faulty[alias_off] = img32[src_off]
    detected32 = img32_faulty[alias_off] != img32[alias_off]
    # Attribution: decode_mismatch at width 32 names byte_index 2 -> bits [16:24), which
    # covers A16/A17 -- i.e. the decode function itself resolves the address-byte identity.
    decoded32 = decode_mismatch(alias_off, img32_faulty[alias_off], mask_b, WIDTH_32)
    attributed32 = "index 2" in decoded32 and "[16:23]" in decoded32
    check(
        "negative: width32 A17-alias injection is DETECTED",
        detected32,
        f"byte at 0x{alias_off:05X} changed from 0x{img32[alias_off]:02X} to 0x{img32_faulty[alias_off]:02X}",
    )
    check(
        "negative: width32 A17-alias injection is ATTRIBUTED to address bits [16:23]",
        attributed32,
        decoded32,
    )

    # Now the width16 asymmetry: at the SAME offset pair, the width-16 stamp is identical
    # for src_off and alias_off (both low-16-bit-derived, and 0x20000 doesn't change the low
    # 16 bits), so injecting the byte from src_off into alias_off in a width-16 image produces
    # NO CHANGE AT ALL -- the fault is invisible, not merely unattributable. That is the
    # measured asymmetry: width16 cannot even detect this fault class, let alone attribute it.
    stamp16_src = (src_off >> 8) & 0xFF if (src_off & 1) else (src_off & 0xFF)
    stamp16_alias = (alias_off >> 8) & 0xFF if (alias_off & 1) else (alias_off & 0xFF)
    width16_would_be_invisible = stamp16_src == stamp16_alias
    check(
        "negative: width16 A17-alias injection is UNDETECTABLE (not merely unattributable) "
        "-- the asymmetry that justifies stamp_width=32",
        width16_would_be_invisible,
        f"width16 stamp at src=0x{src_off:05X} is 0x{stamp16_src:02X}, "
        f"at alias=0x{alias_off:05X} is 0x{stamp16_alias:02X}",
    )

    return 0 if ok else 1


def _usage(prog: str) -> str:
    return (
        f"usage: {prog} <size_bytes> <mask_hex_or_dec> <output_path> "
        f"[--stamp-width {{16,32}}]\n"
        f"       {prog} --decode <offset_hex_or_dec> <observed_byte_hex_or_dec> "
        f"<mask_hex_or_dec> --stamp-width {{16,32}}\n"
        f"       {prog} --selftest\n"
    )


def _extract_stamp_width(args: list) -> tuple[list, int | None]:
    """Pull `--stamp-width N` (space-separated, matching this tool's CLI contract) out of
    `args`, returning the remaining positional args and the parsed width, or None if absent.
    """
    remaining = []
    width = None
    i = 0
    while i < len(args):
        if args[i] == "--stamp-width":
            if i + 1 >= len(args):
                raise ValueError("--stamp-width requires a value")
            width = int(args[i + 1], 0)
            i += 2
            continue
        remaining.append(args[i])
        i += 1
    return remaining, width


def main(argv: list) -> int:
    prog = argv[0]
    rest = argv[1:]

    if rest[:1] == ["--selftest"]:
        return _run_selftest()

    if rest[:1] == ["--decode"]:
        try:
            positional, stamp_width = _extract_stamp_width(rest[1:])
        except ValueError as exc:
            sys.stderr.write(f"usage: {exc}\n")
            return 2
        if len(positional) != 3 or stamp_width is None:
            sys.stderr.write(_usage(prog))
            return 2
        offset = int(positional[0], 0)
        observed_byte = int(positional[1], 0) & 0xFF
        mask = int(positional[2], 0) & 0xFF
        if stamp_width not in VALID_WIDTHS:
            sys.stderr.write(f"usage: --stamp-width must be one of {VALID_WIDTHS}\n")
            return 2
        print(decode_mismatch(offset, observed_byte, mask, stamp_width))
        return 0

    try:
        positional, stamp_width = _extract_stamp_width(rest)
    except ValueError as exc:
        sys.stderr.write(f"usage: {exc}\n")
        return 2

    if len(positional) != 3:
        sys.stderr.write(_usage(prog))
        return 2

    size = int(positional[0], 0)
    mask = int(positional[1], 0) & 0xFF
    out_path = positional[2]

    if stamp_width is None:
        stamp_width = WIDTH_16 if size <= 0x10000 else WIDTH_32
    if stamp_width not in VALID_WIDTHS:
        sys.stderr.write(f"usage: --stamp-width must be one of {VALID_WIDTHS}\n")
        return 2

    try:
        data = gen_image(size, mask, stamp_width)
    except ValueError as exc:
        sys.stderr.write(f"usage: {exc}\n")
        return 2

    with open(out_path, "wb") as f:
        f.write(data)

    print(_verdict_line(out_path, size, mask, stamp_width, data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
