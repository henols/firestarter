# `planted_release_assets_zero_byte_leonardo/`

A planted violation proving `check_release_assets.py`'s (Phase 128 Plan 01, D-11/D-12,
REL-03/REL-02) non-empty check. This case is load-bearing, not belt-and-braces:
`softprops/action-gh-release`'s own `paths()` filter accepts any path where
`statSync(p).isFile()` is true, so a zero-byte hex would be uploaded to the release as a
real asset if the checker only tested existence.

## What is planted

`= clean_release_assets_all_three/` with **one edit**:
`leonardo/firestarter_leonardo.hex` is truncated to **zero bytes**. All three directories
(`uno/`, `uno328pb/`, `leonardo/`) exist; `uno/` and `uno328pb/` carry their normal
non-empty `.hex` files, byte-identical to the clean tree.

## Expected gate behaviour

`FIRESTARTER_PIO_BUILD_ROOT=<this dir>/pio_build python3 scripts/check_release_assets.py`
(or `--build-root <this dir>/pio_build`):

- Exit **non-zero** (1)
- stdout contains `FAIL:` and names `leonardo` and the observed size `0`
- stdout never contains `PASS:`

## Why `pio_build/`, not `.pio/`

Same reason as the clean control: `firestarter/.gitignore` line 1 (`.pio`) matches at any
depth and would silently swallow a `.pio`-named fixture directory via `git add`'s silent
no-op on ignored paths. `pio_build/` has no leading dot, so nothing here is ignored.
