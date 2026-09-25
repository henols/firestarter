#!/usr/bin/env bash
set -e

echo "=== Generating platformio.ini wrapper ==="
python3 /workspaces/.devcontainer/gen-platformio-ini.py

echo "=== Installing Python CLI (dev mode) ==="
pip install -e /workspaces/firestarter_app

echo "=== Initialising PlatformIO project dependencies ==="
cd /workspaces/firestarter_fw && pio pkg install

echo "=== Installing graphify skill (writes into ~/.claude volume) ==="
# graphify itself is installed in the image (Dockerfile); this step installs the
# skill/references into the ~/.claude named volume, which is only mounted at runtime.
graphify install

echo "=== Done ==="
