# Development container

Everything needed to build the firmware, run the CLI and talk to a board over
USB, without installing anything on your own machine.

Open the repository in VS Code and choose **Reopen in Container**. First build
takes a few minutes; after that it starts in seconds.

## Working on the CLI

The `firestarter` command is already installed and points at `firestarter_app/`
in your working tree, so edits take effect immediately — no reinstall.

```bash
firestarter --help
firestarter search 27C256
```

Run its tests:

```bash
cd firestarter_app && python -m pytest tests -o addopts="" -q
```

**Before trusting a green run, repeat it on Python 3.11.** The container runs
3.12, CI runs 3.11, and that difference has hidden real breakage before:

```bash
uv venv --python 3.11 /tmp/py311
/tmp/py311/bin/python -m pip install -e 'firestarter_app[test]'
/tmp/py311/bin/python -m pytest firestarter_app/tests -o addopts="" -q
```

## Working on the firmware

```bash
cd firestarter
pio run -e uno              # build
pio test -e native          # unit tests
pio run -t upload -e uno    # flash a connected board
pio run -t monitor -e uno   # serial monitor, 250000 baud
```

Swap `uno` for `leonardo` or `uno328pb` for the other boards.

## Talking to a board

Plug it in over USB and it appears as `/dev/ttyACM*` or `/dev/ttyUSB*` inside
the container — no extra setup.

```bash
firestarter hw              # which shield revision answered
firestarter fw              # which firmware is on the board
```

## If something is missing

**The `firestarter_fw/` or `firestarter_app/` folder is empty** — the submodules
did not check out:

```bash
git submodule update --init --recursive
```

**PlatformIO cannot find the project** — regenerate the wrapper it reads, which
is needed after the firmware's own `platformio.ini` changes:

```bash
python3 .devcontainer/gen-platformio-ini.py
```
