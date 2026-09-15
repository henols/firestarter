#!/usr/bin/env python3
"""
Generates /workspaces/platformio.ini from <FIRMWARE_DIR>/platformio.ini.

Adds a [platformio] section that redirects all paths into the firmware submodule
so PlatformIO IDE can find the project from the repo root workspace.

Run manually after updating the firmware platformio.ini:
    python3 .devcontainer/gen-platformio-ini.py
"""
import re, pathlib

# ── Configuration ────────────────────────────────────────────────────────────
FIRMWARE_DIR = "firestarter_fw"   # name of the firmware submodule folder
# ─────────────────────────────────────────────────────────────────────────────

ROOT = pathlib.Path(__file__).parent.parent  # repo root (/workspaces)
SRC  = ROOT / FIRMWARE_DIR / "platformio.ini"
OUT  = ROOT / "platformio.ini"

HEADER = f"""\
; Auto-generated from {SRC.relative_to(ROOT)} — do not edit manually.
; Regenerate with:  python3 .devcontainer/gen-platformio-ini.py
;
; Maps PlatformIO IDE onto the {FIRMWARE_DIR}/ submodule from the repo root.
; To work on firmware outside the devcontainer, run pio from {FIRMWARE_DIR}/ directly.

"""

PATH_KEYS = f"""\
src_dir       = {FIRMWARE_DIR}/src
include_dir   = {FIRMWARE_DIR}/include
lib_dir       = {FIRMWARE_DIR}/lib
test_dir      = {FIRMWARE_DIR}/test
build_dir     = {FIRMWARE_DIR}/.pio/build
libdeps_dir   = {FIRMWARE_DIR}/.pio/libdeps
workspace_dir = {FIRMWARE_DIR}/.pio
"""

content = SRC.read_text()

# Prefix relative -I paths:  -I include  →  -I {FIRMWARE_DIR}/include
content = re.sub(r'(-I )(?!/|' + FIRMWARE_DIR + r'/)(\S+)', r'\1' + FIRMWARE_DIR + r'/\2', content)
# Prefix relative extra_scripts:  pre:script.py  →  pre:{FIRMWARE_DIR}/script.py
content = re.sub(r'((?:pre:|post:))(?!/|' + FIRMWARE_DIR + r'/)(\S+)', r'\1' + FIRMWARE_DIR + r'/\2', content)

# The source already declares [platformio] (it carries default_envs). Emitting a
# second one produces a file configparser rejects with "section 'platformio'
# already exists", so inject the path keys into the existing section instead.
if re.search(r'^\[platformio\]\s*$', content, flags=re.M):
    content = re.sub(r'^(\[platformio\]\s*)$', r'\1\n' + PATH_KEYS, content, count=1, flags=re.M)
else:
    content = "[platformio]\n" + PATH_KEYS + "\n" + content

OUT.write_text(HEADER + content)
print(f"Written {OUT}")
