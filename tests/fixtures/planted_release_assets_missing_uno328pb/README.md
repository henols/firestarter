# `planted_release_assets_missing_uno328pb/`

A planted violation proving `check_release_assets.py`'s (Phase 128 Plan 01, D-11/D-12,
REL-03/REL-02) required-set assertion: every key in `scripts/baseline/size_baseline.json`'s
`avr_targets` must have a present, non-empty `firestarter_<key>.hex` under the build root,
or the checker fails closed.

## What is planted

`= clean_release_assets_all_three/` with **one edit**: `uno328pb/firestarter_uno328pb.hex`
is absent. Because git cannot track an empty directory, the `uno328pb/` directory itself is
absent with it. `uno/` and `leonardo/` are byte-identical to the clean tree.

## Expected gate behaviour

`FIRESTARTER_PIO_BUILD_ROOT=<this dir>/pio_build python3 scripts/check_release_assets.py`
(or `--build-root <this dir>/pio_build`):

- Exit **non-zero** (1)
- stdout contains `FAIL:` and names `uno328pb` and the expected absolute path
- stdout never contains `PASS:`

## Why `pio_build/`, not `.pio/`

Same reason as the clean control: `firestarter/.gitignore` line 1 (`.pio`) matches at any
depth and would silently swallow a `.pio`-named fixture directory via `git add`'s silent
no-op on ignored paths. `pio_build/` has no leading dot, so nothing here is ignored.
