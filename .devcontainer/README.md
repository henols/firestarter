<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter/main/images/branding/firestarter_logo_horizontal.png" alt="Firestarter EPROM Programmer" width="400"></p>

# Development container

Everything needed to build the firmware, run the CLI and talk to a board over
USB, without installing anything on your own machine.

Open the repository in VS Code and choose **Reopen in Container**. The first build
takes a few minutes. After that, the container starts in seconds.

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
3.12, CI runs 3.11, and that difference hid real breakage in the past:

```bash
uv venv --python 3.11 /tmp/py311
/tmp/py311/bin/python -m pip install -e 'firestarter_app[test]'
/tmp/py311/bin/python -m pytest firestarter_app/tests -o addopts="" -q
```

## Working on the firmware

```bash
cd firestarter_fw
pio run -e uno              # build
pio test -e native          # unit tests
pio run -t upload -e uno    # flash a connected board
pio run -t monitor -e uno   # serial monitor, 250000 baud
```

Swap `uno` for `leonardo` or `uno328pb` for the other boards.

Build the py32f071 firmware with CMake. Set `RURP_BOARD` to `py32f071` or `micropetal_uno`:

```bash
cd firestarter_fw
cmake -S platform/py32f071 -B /tmp/py32f071 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DRURP_BOARD=py32f071
cmake --build /tmp/py32f071
FIRESTARTER_PY32_COMPILE_COMMANDS=/tmp/py32f071/compile_commands.json \
  python3 -m pytest tests -q
```

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

**PlatformIO cannot find the project** — regenerate the wrapper that it reads.
Do this after each change to the firmware's own `platformio.ini`:

```bash
python3 .devcontainer/gen-platformio-ini.py
```
