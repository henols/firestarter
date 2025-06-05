#!/usr/bin/env python3
import re
import os
from datetime import timezone


def get_header_version():
    header_file = "include/version.h"

    # rxs = "^#define VERSION (\w+)"
    rxs = "^#define VERSION(.\")([0-9\.]+)"

    txt = [line for line in open(header_file)]

    for line in txt:
        m = re.match(rxs, line)
        if m:
            major, minor, patch = str(m.group(2)).split(".")
            return (major, minor, patch)

def update_version(major, minor, patch):
    """Update the version number in the header file."""
    header_file = "include/version.h"

    rxs = "^(#define VERSION )"
    
    txt = [line for line in open(header_file)]

    fout = open(header_file, "w")

    for line in txt:
        m = re.match(rxs, line)
        if m:
            line = m.groups(0)[0] + f"\"{major}.{minor}.{patch}\"\n"
            fout.write(line)
        else:
            fout.write(line)

    fout.close()
    print(f"Version file updated: {major}.{minor}.{patch}")


def calculate_version():

    major, minor, patch = get_header_version()

    pattern = re.compile("[0-9]+")
    if pattern.match(patch):
        patch = int(patch) + 1
    else:
        patch = 0
    update_version(major, minor, patch)

    print(f"New versin created: {major}.{minor}.{patch}")
    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        print(f"version={major}.{minor}.{patch}", file=fh)
        print(f"major={major}", file=fh)
        print(f"minor={minor}", file=fh)
        print(f"patch={patch}", file=fh)


if __name__ == "__main__":
    calculate_version()
