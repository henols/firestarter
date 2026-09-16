---
last_mapped_commit: 55ca612f
last_mapped_at: 2026-09-14T05:19:26.128Z
mapped_paths: .claude,.devcontainer,.github,.gitignore,.gitmodules,.vscode,CLAUDE.md
---
# Testing

**Analysis Date:** 2026-09-14

**Source (this pass):** meta-repo tracked paths only — `.github/`, `.devcontainer/`, `.vscode/`, `.claude/skills/`, `.gitignore`, `.gitmodules`, `CLAUDE.md`. The firmware (`firestarter_fw/`) and host app (`firestarter_app/`) are git submodules and were **not** scanned in this pass; their internal test layout is marked below.

## Summary — corrects the 2026-05-08 claim

The previous revision of this document asserted that the project "has no Python unit
tests" and that "no pytest, unittest, or other Python testing framework is configured."
**That claim is obsolete and must not be repeated.** The host app has a real Python test
suite with a pytest + mypy + ruff gate, and the firmware has PlatformIO native unit tests.
Both live inside the submodules.

What is true of the layer this pass can see:

| Layer | Test/gate surface | Verified in scope |
|-------|-------------------|-------------------|
| Meta repo (this repo) | No `.github/workflows/` directory at all. No automated check of any kind. | Yes |
| Host app `firestarter_app/` | pytest suite, mypy watermark gate, ruff (`select = [E,F,I,UP]`), run on Python 3.11 | No — submodule out of scope |
| Firmware `firestarter_fw/` | `pio test` (PlatformIO), native + native_nodevtools environments | Partly — `CLAUDE.md` documents `pio test` |
| `.claude/skills/*/scripts/*.py` | **Nothing.** No tests, no type checking, no lint in any CI. | Yes |

## Meta-repo CI — none exists

`.github/` holds `CONTRIBUTING.md` and a four-file `ISSUE_TEMPLATE/` directory, and
nothing else — there is no `.github/workflows/` directory in this repository. No CI
workflow of any kind runs against this repo: no test, no lint, no build, no publish job,
and no cross-repo consistency check. The only executable artefacts in the mapped scope
are the devcontainer provisioning scripts (`.devcontainer/post-create.sh`,
`.devcontainer/gen-platformio-ini.py`), which run at container build/create time, not as
a gate on any push or pull request.

Releases are cut from the sub-repos' own workflows; this repo enforces nothing about
them.

## Test tooling installed by the devcontainer

`.devcontainer/Dockerfile` and `.devcontainer/post-create.sh` define the local test
environment:

- Base image `mcr.microsoft.com/devcontainers/python:3.12` — the container reports
  **Python 3.12.14**.
- `pip install platformio` — provides `pio run`, `pio test`.
- `pip install uv` — used for creating pinned virtualenvs and installing tooling.
- `apt`: `udev`, `libusb-1.0-0`, `avrdude`, `unzip`; user `vscode` added to `dialout` so
  serial hardware tests can reach `/dev/ttyACM*`.
- `devcontainer.json` sets `--privileged` and bind-mounts `/dev`, which is what makes
  **hardware-in-the-loop testing possible from inside the container**.
- `post-create.sh` runs `pip install -e /workspaces/firestarter_app` and
  `cd /workspaces/firestarter && pio pkg install`.

**Python version mismatch (quality-relevant):** the devcontainer's default interpreter is
3.12 (`python.defaultInterpreterPath: /usr/local/bin/python`), which is **not** the
version the host-app CI pins (3.11) `[unverified in 2026-08-26 and 2026-09-14 scoped remaps]`. Running
the app suite with the container default can pass locally while the CI job fails, and
py3.12 has been observed to surface Click/snapshot breakage as collection errors instead.
Create a pinned venv before trusting a local green run:

```bash
uv venv --python 3.11 && . .venv/bin/activate
pip install -e '/workspaces/firestarter_app[test]'
```

There is **no** `pytest`, `mypy`, `ruff`, or `clang-format` installed at image level and
no configuration for them in the meta repo — those come from the sub-repos' own
dependency groups.

## Agent-tooling scripts are untested

`.claude/skills/*/scripts/` contains ~2100 lines of tracked Python across four files:

| File | Lines |
|------|-------|
| `.claude/skills/devtest-rootcause/scripts/diff_db.py` | 996 |
| `.claude/skills/devtest-triage/scripts/devtest_issues.py` | 693 |
| `.claude/skills/devtest-triage/scripts/eprom_families.py` | 219 |
| `.claude/skills/devtest-rootcause/scripts/infoic_lookup.py` | 210 |

None of it is covered by a test file, a `conftest.py`, mypy, or ruff — this repo has no
workflow of any kind (above), so nothing touches these files. This matters because
`devtest_issues.py` parses **untrusted, community-authored GitHub issue bodies** (its
docstring says so explicitly and it bounds input at `MAX_BODY = 1_000_000`). That
hardening is asserted by comment only.

The substitutes that exist:

- **Golden fixtures without a runner:** `.claude/skills/devtest-triage/fixtures/dev-test-at28c256-null-identity.md`
  and `dev-test-at28c256-populated-identity.md` are checked-in parser inputs, exercised
  manually via `devtest_issues.py show --body-file <fixture> --title "$T"`.

Recommended additions are a `tests/` directory beside the skills plus a ruff/mypy leg
added to a new workflow path filter for `.claude/skills/**`.

## Manual / hardware verification

Hardware validation is operator-driven and not scripted in this repo. `CLAUDE.md` records
the entry points:

```bash
# host app (run from firestarter_app/)
./firestarter_test.sh [EPROM]     # full hardware integration test
./write_test.sh [EPROM]           # write/verify test

# firmware (run from firestarter_fw/)
pio run -e uno                    # build for Arduino Uno
pio run -e leonardo               # build for Arduino Leonardo
pio run -t upload -e uno          # flash
pio run -t monitor -e uno         # serial monitor at 250000 baud
pio test                          # unit tests
```

Run output is gitignored, which tells you where it lands: `firestarter-runs/`,
`consistency-check-*/`, `write-cycle-*/`, `chip-test/`, and root-level `/*.bin`.

## Host-app integration scripts (submodule — preserved from 2026-05-08)

*`[unverified in 2026-08-26 and 2026-09-14 scoped remaps]` — `firestarter_app/` was out
of scope. Paths below have been rewritten from the stale `/home/henrik/dev/...` prefix to
repo-relative form; the descriptions are otherwise preserved.*

### `firestarter_app/firestarter_test.sh`

An end-to-end suite requiring a physical EPROM programmer.

```bash
./firestarter_test.sh [EPROM_NAME]   # defaults to W27C512
```

Covers, in order: firmware version (`firestarter fw`), hardware version (`firestarter hw`),
hardware config, VPP (`firestarter vpp -t 5`), VPE (`firestarter vpe -t 5`), chip ID
(if supported), write random data, verify, read back, binary diff of written vs read-back
via `xxd` + `colordiff`, erase (if supported), blank check (if supported), list EPROMs,
search by name, info.

**Data approach:** generates random binary data with `dd if=/dev/urandom`, splits into
low/high halves and concatenates into a full image, compares byte-level with
`xxd` + `colordiff`, and cleans `./test_data/` on exit via `trap`. EPROM metadata is read
with `jq`. *Note: the old doc named `./firestarter/data/database_generated.json`;
`CLAUDE.md` now names `firestarter_app/firestarter/data/chip_database.json` as the
database — assume the latter.*

### `firestarter_app/write_test.sh`

A focused write/verify/read script, also hardware-dependent.

### Modules testable without hardware `[unverified in 2026-08-26 and 2026-09-14 scoped remaps]`

| Module | Testable without hardware |
|--------|--------------------------|
| `utils.py` | Yes — pure functions (`extract_hex_to_decimal`, `format_size`, `time_formatter`) |
| `constants.py` | Yes — static values |
| `database.py` | Yes — JSON loading/parsing/searching with mock files |
| `eprom_info.py` | Yes — data formatting and display logic |
| `config.py` | Yes — file I/O with temp dirs |
| `serial_comm.py` | Partially — parsing/validation logic; hardware interaction needs mocking |
| `eprom_operations.py` | Partially — flag building, state logic; serial layer needs mocking |

---

*Testing analysis: 2026-09-14 (meta-repo layer); 2026-05-08 (submodule layer, preserved above)*
