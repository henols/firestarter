#!/usr/bin/env python3
"""gen_addr_image.py -- word-stamped, address-attributable bench write image generator.

D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It is authored and lives
only under .planning/phases/145-bench-validation/images/ in the meta repo. It must NEVER be
copied into firestarter/ or firestarter_app/ (in particular not into firestarter_app/tools/,
alongside the existing firestarter_app/tools/gen_test_image.py) -- this phase changes no
firmware and no host source (D-16). Nothing here is imported by, or imports from, either
sub-repo.

Recipe (RQ-2, D-05): the byte at offset N carries the LOW byte of N when N is even, and the
HIGH byte of N when N is odd, XORed with a per-image mask:

    stamp(N) = (N & 0xFF)         if N is even   (low address byte)
             = ((N >> 8) & 0xFF)  if N is odd     (high address byte)
    byte(N)  = stamp(N) ^ mask

Each aligned 2-byte word therefore literally stamps its own 16-bit address. That is what
makes a mismatched byte decodable back to a source address -- a property
firestarter_app/tools/gen_test_image.py's pseudo-random data does NOT have (a mismatch there
is detectable but not attributable to an address), which is exactly why D-05 rejects it and
requires this generator instead. The distinction is the one that root-caused Phase 97's
pin-31 (A18-aliasing) defect: an address-line fault must be traceable to which address line
aliased, not merely counted as "N bytes differ".
"""
import hashlib
import sys


def gen_image(size: int, mask: int) -> bytes:
    """Return `size` bytes of the word-stamped address pattern, XORed with `mask`."""
    b = bytearray(size)
    for n in range(size):
        stamp = (n >> 8) & 0xFF if (n & 1) else (n & 0xFF)
        b[n] = stamp ^ mask
    return bytes(b)


def decode_mismatch(offset: int, observed_byte: int, mask: int) -> str:
    """Un-mask an observed byte at `offset` and name which address byte it names.

    Worked example (RQ-2's simulated A8-stuck-low fault): first mismatch at offset
    0x0101, observed byte 0x00. Un-masking (mask=0x00 for img1) leaves 0x00. The
    offset is odd, so the stamp is the HIGH address byte -- the byte belongs to an
    address whose high byte is 0x00, i.e. address 0x0001, naming A8 (bit 8, the low
    bit of the high byte) as the aliased line.
    """
    unmasked = observed_byte ^ mask
    is_high_byte = bool(offset & 1)
    kind = "high" if is_high_byte else "low"
    return (
        f"offset=0x{offset:04X} observed=0x{observed_byte:02X} unmasked=0x{unmasked:02X} "
        f"-> {kind} address byte, source address high-byte-implied=0x{unmasked:02X}"
    )


def main(argv: list) -> int:
    if len(argv) != 4:
        sys.stderr.write(f"usage: {argv[0]} <size_bytes> <mask_hex_or_dec> <output_path>\n")
        return 2
    size = int(argv[1], 0)
    mask = int(argv[2], 0) & 0xFF
    out_path = argv[3]

    data = gen_image(size, mask)
    with open(out_path, "wb") as f:
        f.write(data)

    digest = hashlib.sha256(data).hexdigest()
    ff_count = data.count(0xFF)
    print(
        f"{out_path}: {size} bytes, mask=0x{mask:02X}, sha256={digest}, "
        f"0xFF_count={ff_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
