"""Cost + connect model for `firestarter dev test`, as measured 2026-08-30.

Companion to .planning/notes/dev-test-sequence-cost-model.md.

PROVENANCE, stated so nobody mistakes this for a benchmark harness: every rate
below is derived from ONE operator log -- a single `dev test sst27sf512 --fast`
run on a Leonardo (1024 B buffer) against a 65536 B part. An Uno's 512 B buffer
will produce different rates. Re-measure before trusting these numbers on
another board class. `erase` is treated as flat because one data point cannot
establish whether it scales with size.

The CONNECT model is a different kind of claim: it is derived structurally from
the code, not fitted, and it reproduces the observed count exactly (13/13). Its
per-connect COST is unmeasured -- the port was busy during the session that
wrote this -- so it reports counts only.
"""

N = 65536.0
R_RATE = N / 7.51    # read   device->host + host file write
V_RATE = N / 5.71    # verify host->device, firmware compares (memory.cpp:377)
B_RATE = N / 4.86    # blank-check, device-side scan, no payload
W_RATE = N / 30.04   # write, programming-limited
ERASE = 5.15
ID = 0.28

SAMPLE = 4096        # bit-structured preflight sample, bytes


def R(n):
    return n / R_RATE


def V(n):
    return n / V_RATE


def B(n):
    return n / B_RATE


def W(n):
    return n / W_RATE


def current(mem, wr, cycles=2, has_erase=True, has_blank=True, uv=False):
    t = ID + 2 * R(mem)
    for c in range(cycles):
        final = c == cycles - 1
        if uv and has_blank:
            t += B(mem)
        t += W(wr)
        if final:
            t += R(wr)
        t += V(wr)
        if final:
            t += R(wr)
        if has_erase:
            t += ERASE
        if not uv and has_blank:
            t += B(mem)
    return t


def proposed(mem, wr, cycles=2, has_erase=True, has_blank=True, uv=False):
    t = ID + 2 * R(SAMPLE)
    for c in range(cycles):
        if uv and has_blank:
            t += B(mem)
        t += W(wr)
        t += V(wr)
        if has_erase:
            t += ERASE
        if not uv and has_blank:
            t += B(mem)
    return t


def connects_now(cycles, has_erase, has_blank, uv, sdp_ops=0, uv_probe_blocks=0):
    c = 1                                    # read_programmer_identity
    c += 1                                   # id step
    c += cycles                              # read step, runs=cycles
    for i in range(cycles):
        final = i == cycles - 1
        if uv and has_blank:
            c += 1
        if uv:
            c += uv_probe_blocks             # _resolve_write_target slot probe
        c += 2                               # sampler("before"): vpp + vpe
        c += 1                               # write
        c += 2                               # sampler("after"): vpp + vpe
        if final:
            c += 1                           # fingerprint readback (write)
        c += 1                               # verify
        if final:
            c += 1                           # fingerprint readback (verify)
        if has_erase:
            c += 1
        if not uv and has_blank:
            c += 1
    c += 2 * sdp_ops                         # each SDP-leg op: write + read_region
    return c


CHIPS = [
    # name, mem, write_region, has_erase, has_blank, uv, sdp_ops, uv_probe_blocks
    ("sst27sf512  EEPROM  full-dev", 65536, 65536, True, True, False, 0, 0),
    ("w27c512     EEPROM  full-dev", 65536, 65536, True, True, False, 0, 0),
    ("at28c256    EEPROM  + SDP leg", 32768, 32768, True, False, False, 6, 0),
    ("m27c512     UV      uv-slot ", 65536, 256, False, True, True, 0, 1),
    ("am27c020    UV      uv-slot ", 262144, 256, False, True, True, 0, 1),
    ("w29c040     flash4  full-dev", 524288, 491520, False, False, False, 0, 0),
]

if __name__ == "__main__":
    got = connects_now(1, True, True, False)
    status = "MATCH" if got == 13 else "MISMATCH"
    print(f"connect model, --fast sst27sf512: {got} vs 13 observed -> {status}\n")

    print(f"{'chip':32} {'now':>9} {'proposed':>9} {'saved':>9} {'%':>6} {'conn':>6}")
    tot_a = tot_b = 0
    for name, mem, wr, he, hb, uv, sdp, pb in CHIPS:
        a = current(mem, wr, has_erase=he, has_blank=hb, uv=uv)
        b = proposed(mem, wr, has_erase=he, has_blank=hb, uv=uv)
        c = connects_now(2, he, hb, uv, sdp, pb)
        tot_a += a
        tot_b += b
        print(f"{name:32} {a:8.1f}s {b:8.1f}s {a - b:8.1f}s {100 * (a - b) / a:5.1f}% {c:6}")
    print(f"{'TOTAL':32} {tot_a:8.1f}s {tot_b:8.1f}s {tot_a - tot_b:8.1f}s "
          f"{100 * (tot_a - tot_b) / tot_a:5.1f}%")
