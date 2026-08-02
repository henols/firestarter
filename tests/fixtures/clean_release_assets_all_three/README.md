# `clean_release_assets_all_three/`

The control fixture for `check_release_assets.py` (Phase 128 Plan 01, D-11/D-12,
REL-03/REL-02). One `pio_build/<env>/firestarter_<env>.hex` per `avr_targets` key in
`scripts/baseline/size_baseline.json` — `uno`, `uno328pb`, `leonardo` — every one present
and non-empty. This is the tree the checker must exit **0** against.

## What is planted

Nothing — this is the clean control, not a planted violation. Each `.hex` file is a
minimal but syntactically real Intel-HEX stub: one data record (`:0400000000010203F6`)
followed by the EOF record (`:00000001FF`). The checker reads only `Path.exists()` and
`stat().st_size`, never file content, so a truncated stub is faithful to everything the
checker actually inspects.

Deliberately **no py32 image anywhere in this tree** — the checker must exit 0 without
one. This is REL-03's tolerance: the AVR-assets-present gate does not require (and must
never require) the py32f071 asset, whose absence on a soft-contained ARM failure is
exactly what REL-03 permits.

## Why `pio_build/`, not `.pio/`

`firestarter/.gitignore` line 1 is the bare pattern `.pio`, which matches at **any
depth** — a fixture tree using a real `.pio/build/...` layout would be silently ignored by
`git add` (exit 0, nothing staged). `check_release_assets.py` reads its build root through
the `FIRESTARTER_PIO_BUILD_ROOT` env seam (or `--build-root`), defaulting to
`<repo>/.pio/build` for a real build but pointed at this fixture's `pio_build/` directory
in tests — a directory name with no leading dot, so nothing here is ignored.

## The two planted siblings

- `planted_release_assets_missing_uno328pb/` = this tree with `uno328pb/` (and its `.hex`)
  removed entirely.
- `planted_release_assets_zero_byte_leonardo/` = this tree with
  `leonardo/firestarter_leonardo.hex` truncated to zero bytes.
