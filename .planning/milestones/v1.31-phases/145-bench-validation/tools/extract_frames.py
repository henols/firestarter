#!/usr/bin/env python3
"""extract_frames.py -- deterministic tqdm progress-frame extractor for D-10.

D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It lives only under
.planning/phases/145-bench-validation/tools/ and must NEVER be added into firestarter/ or
firestarter_app/ -- this phase changes no firmware and no host source. Pure standard-library
Python, no third-party imports. Hex parsing happens here in Python -- gawk's `strtonum` is a
gawk extension and is not portable, so it is deliberately not used anywhere in this pipeline.

Intended input: a raw tqdm stderr capture of a single `firestarter write` invocation, e.g.
`logs/write_cycleN.stderr.raw`, captured with plain shell redirection:

    firestarter -v write W27C512 imgN.bin > logs/write_cycleN.stdout.log \
                                  2> logs/write_cycleN.stderr.raw

Why two bars exist in one capture (RQ-4): the INIT-phase blank check also emits
MSG_DATA_PROGRESS frames (at a 2048-byte step), and `ClassProgressHandler.start()`
unconditionally closes and re-creates the tqdm bar for the MAIN-phase write -- leaving a
newline in the raw capture between the two bars. Counting frames from the wrong bar
(Pitfall 6) inflates the count and can manufacture a false intra-block-motion claim. This
script's segment selection exists specifically to avoid that: it keeps only the LAST segment
that contains at least one progress frame (the write bar), and discards every earlier segment
(INIT blank-check bars).

Usage:
    python3 extract_frames.py <path-to-raw-stderr-capture>
    python3 extract_frames.py --selftest
"""
import re
import sys

# tqdm's bar_format is "{l_bar}{bar}| {n:#06x}/{total:#06x} bytes " (eprom_operations.py:68,385).
# re.search (not re.match) so leading bar/percentage text never blocks a match.
FRAME_RE = re.compile(r"0x([0-9A-Fa-f]+)/0x[0-9A-Fa-f]+\s*bytes")
BLOCK_SIZE = 1024


def split_segments(content: str):
    """Split raw content on newlines into segments, one per tqdm bar instance.

    Each newline in a raw capture marks a bar close-and-recreate
    (`ClassProgressHandler.start()`). Empty strings produced by the split (in particular a
    trailing empty string from a capture whose final segment is itself newline-terminated)
    are not real segments and are dropped, so `segments=N` always counts actual bar
    instances, never a phantom empty tail.
    """
    parts = content.split("\n")
    segments = [p for p in parts if p != ""]
    return segments if segments else [""]


def frames_in_segment(segment: str):
    """Return every frame position found in `segment`, in encounter order (NOT
    de-duplicated), by splitting on carriage return (one potential frame per
    redraw) and matching each chunk against the tqdm frame shape."""
    positions = []
    for chunk in segment.split("\r"):
        m = FRAME_RE.search(chunk)
        if m:
            positions.append(int(m.group(1), 16))
    return positions


def analyze(content: str) -> dict:
    """Core parsing shared by real-capture mode and both self-test fixtures."""
    segments = split_segments(content)

    # The selected segment is the LAST one containing at least one frame -- the write
    # bar. Every earlier segment (with or without frames) is an INIT-phase blank-check
    # bar and is discarded.
    selected_index = None  # 0-based index into `segments`
    selected_frames = []
    for i, seg in enumerate(segments):
        f = frames_in_segment(seg)
        if f:
            selected_index = i
            selected_frames = f

    if selected_index is None:
        selected_index = len(segments) - 1
        selected_frames = []

    distinct_positions = sorted(set(selected_frames))

    blocks: dict = {}
    for p in distinct_positions:
        blocks.setdefault(p // BLOCK_SIZE, []).append(p)

    intra_block_positions = [p for p in distinct_positions if p % BLOCK_SIZE != 0]
    multi_blocks = {b: ps for b, ps in blocks.items() if len(ps) > 1}

    deltas: dict = {}
    for a, b in zip(distinct_positions, distinct_positions[1:]):
        d = b - a
        deltas[d] = deltas.get(d, 0) + 1

    return {
        "segments": len(segments),
        "selected_segment": selected_index + 1,  # 1-based, per spec
        "frames": len(selected_frames),
        "positions": distinct_positions,
        "blocks": blocks,
        "intra_block_frames": len(intra_block_positions),
        "blocks_with_multiple_updates": len(multi_blocks),
        "multi_blocks": multi_blocks,
        "step_histogram": deltas,
    }


def print_report(result: dict) -> None:
    """Print the greppable report, in the mandated field order."""
    print(f"segments={result['segments']}")
    print(f"selected_segment={result['selected_segment']}")
    print(f"frames={result['frames']}")
    for p in result["positions"]:
        block = p // BLOCK_SIZE
        kind = "boundary" if p % BLOCK_SIZE == 0 else "INTRA-BLOCK"
        print(f"{p}\t{block}\t{kind}")
    print(f"intra_block_frames={result['intra_block_frames']}")
    print(f"blocks_with_multiple_updates={result['blocks_with_multiple_updates']}")
    for b in sorted(result["multi_blocks"]):
        print(f"block {b} has {len(result['multi_blocks'][b])} updates")
    hist = ",".join(f"{d}:{c}" for d, c in sorted(result["step_histogram"].items()))
    print(f"step_histogram={hist}")


# --------------------------------------------------------------------------------------
# --selftest: both outcomes of the instrument must be OBSERVED before it is trusted.
# --------------------------------------------------------------------------------------


def _frame(pos_hex: str) -> str:
    return f"0x{pos_hex}/0x10000 bytes"


def _build_positive_fixture() -> str:
    """Two segments. Segment 1: INIT-style bar (2048-byte step). Segment 2: write-style
    bar with one genuinely intra-block frame at 0x0500 (1280, inside block 1)."""
    seg1 = "\r".join([_frame("0000"), _frame("0800"), _frame("1000")])
    seg2 = "\r".join([_frame("0000"), _frame("0400"), _frame("0500"), _frame("0800")])
    return seg1 + "\n" + seg2 + "\n"


def _build_negative_fixture() -> str:
    """Same two-segment shape; segment 2 carries only boundary (multiple-of-1024)
    frames, so no intra-block motion exists to find."""
    seg1 = "\r".join([_frame("0000"), _frame("0800"), _frame("1000")])
    seg2 = "\r".join([_frame("0000"), _frame("0400"), _frame("0800"), _frame("0C00")])
    return seg1 + "\n" + seg2 + "\n"


def _assert_field(name, expected, observed, diffs):
    if expected != observed:
        diffs.append(f"  {name}: expected={expected!r} observed={observed!r}")


def _run_selftest_leg(name: str, content: str, expected: dict) -> bool:
    result = analyze(content)
    diffs = []
    _assert_field("segments", expected["segments"], result["segments"], diffs)
    _assert_field(
        "selected_segment", expected["selected_segment"], result["selected_segment"], diffs
    )
    _assert_field("positions", expected["positions"], result["positions"], diffs)
    _assert_field(
        "intra_block_frames",
        expected["intra_block_frames"],
        result["intra_block_frames"],
        diffs,
    )
    _assert_field(
        "blocks_with_multiple_updates",
        expected["blocks_with_multiple_updates"],
        result["blocks_with_multiple_updates"],
        diffs,
    )
    observed_block_updates = {b: len(ps) for b, ps in result["multi_blocks"].items()}
    _assert_field("block_updates", expected["block_updates"], observed_block_updates, diffs)
    if "absent_position" in expected:
        absent_ok = expected["absent_position"] not in result["positions"]
        _assert_field(
            f"absent_position({expected['absent_position']})", True, absent_ok, diffs
        )

    if diffs:
        print(f"SELFTEST: {name} FAIL")
        for d in diffs:
            print(d)
        return False
    print(f"SELFTEST: {name} PASS")
    return True


def run_selftest() -> int:
    positive_ok = _run_selftest_leg(
        "POSITIVE",
        _build_positive_fixture(),
        {
            "segments": 2,
            "selected_segment": 2,
            "positions": [0, 1024, 1280, 2048],
            "intra_block_frames": 1,
            "blocks_with_multiple_updates": 1,
            "block_updates": {1: 2},
            "absent_position": 4096,  # proves segment 1's INIT frames did not leak in (Pitfall 6)
        },
    )
    negative_ok = _run_selftest_leg(
        "NEGATIVE",
        _build_negative_fixture(),
        {
            "segments": 2,
            "selected_segment": 2,
            "positions": [0, 1024, 2048, 3072],
            "intra_block_frames": 0,
            "blocks_with_multiple_updates": 0,
            "block_updates": {},
        },
    )
    return 0 if (positive_ok and negative_ok) else 1


def main(argv) -> int:
    if len(argv) >= 2 and argv[1] == "--selftest":
        return run_selftest()

    if len(argv) != 2:
        sys.stderr.write(f"usage: {argv[0]} <raw-stderr-capture-path>\n")
        sys.stderr.write(f"       {argv[0]} --selftest\n")
        return 2

    with open(argv[1], "rb") as f:
        raw = f.read()
    # Decoded permissively: tqdm's default bar glyphs are multi-byte UTF-8; a raw
    # capture that happens to be truncated mid-glyph must not crash the extractor.
    content = raw.decode("utf-8", errors="replace")

    print_report(analyze(content))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
