FROM mcr.microsoft.com/devcontainers/python:3.12

# PlatformIO requires udev rules and the user in the dialout group for serial access
# unzip is needed by the Bun installer below (it unzips its download) and is declared
# here rather than assumed from the base image.
# cmake, ninja-build and the arm-none-eabi packages build the py32f071 firmware.
# CI installs the same packages in firestarter_fw/.github/actions/build-py32f071.
RUN apt-get update && apt-get install -y --no-install-recommends \
        udev \
        libusb-1.0-0 \
        avrdude \
        unzip \
        cmake \
        ninja-build \
        gcc-arm-none-eabi \
        binutils-arm-none-eabi \
        libnewlib-arm-none-eabi \
    && rm -rf /var/lib/apt/lists/*

# Add vscode user to dialout for serial port access
RUN usermod -aG dialout vscode

# Install PlatformIO CLI
RUN pip install --no-cache-dir platformio

# Install uv (used to install graphify and other tooling)
RUN pip install --no-cache-dir uv

# Install graphify (knowledge-graph tool used by GSD /gsd-graphify).
# Installed system-wide at image-build time (as root) so the entry point lands
# on PATH and there are no runtime cache/permission issues in named volumes.
RUN uv pip install --system graphifyy

# Install Bun (required by the official Claude Code Discord channel plugin, whose MCP
# server runs on Bun). Installed system-wide at image-build time (as root) with
# BUN_INSTALL=/usr/local so the binary lands at /usr/local/bin/bun, which is already on
# PATH for every shell -- including the non-interactive, non-login shell that Claude
# Code's MCP launcher uses, since the plugin's .mcp.json declares the bare command name
# "bun". Nothing is written to ~/.bun, which is not a named volume and would not survive
# a rebuild. The node devcontainer feature's package manager is not available yet at
# Dockerfile build time (it is applied after this image builds), so the official
# installer script is used instead.
RUN curl -fsSL https://bun.sh/install | BUN_INSTALL=/usr/local bash \
    && /usr/local/bin/bun --version

# Pre-create persistent volume mount points owned by vscode so Docker initialises
# the named volumes with the correct ownership on first run (not as root).
RUN mkdir -p /home/vscode/.platformio /home/vscode/.config /home/vscode/.cache/pip /home/vscode/.claude \
    && chown -R vscode:vscode /home/vscode/.platformio /home/vscode/.config /home/vscode/.cache/pip /home/vscode/.claude
