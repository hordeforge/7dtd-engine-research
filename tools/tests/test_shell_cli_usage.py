#!/usr/bin/env python3
"""Require side-effect-free help from supported shell entry points."""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOLS = _common.TOOLS
SCRIPTS = (
    "build.sh",
    "cecil-pin.sh",
    "post-update.sh",
    "regen.sh",
    "stock-sync.sh",
    "parity/drift-check.sh",
    "parity/fetch_version.sh",
)


def main() -> None:
    bad = []
    for relative in SCRIPTS:
        path = TOOLS / relative
        result = subprocess.run([path, "--help"], text=True, capture_output=True)
        if result.returncode != 0 or not result.stdout.strip():
            bad.append(f"{relative}: rc={result.returncode}, stderr={result.stderr.strip()!r}")
    assert not bad, "\n".join(bad)
    assert subprocess.run([TOOLS / "build.sh", "--bad"], capture_output=True).returncode == 2
    assert subprocess.run([TOOLS / "regen.sh", "--bad"], capture_output=True).returncode == 2
    assert subprocess.run([TOOLS / "post-update.sh", "--bad"], capture_output=True).returncode == 2

    # The opt-in Steam side of the post-update path must stay documented: the
    # default run is offline, so a reader only discovers --steam from the help.
    help_text = subprocess.run(
        [TOOLS / "post-update.sh", "--help"], text=True, capture_output=True
    ).stdout
    assert "--steam" in help_text, help_text
    assert "offline" in help_text, help_text
    print(f"OK: {len(SCRIPTS)} shell CLIs provide side-effect-free help")


if __name__ == "__main__":
    main()
