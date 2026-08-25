#!/usr/bin/env python3
"""Require side-effect-free help from supported shell entry points."""

import subprocess
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
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
    print(f"OK: {len(SCRIPTS)} shell CLIs provide side-effect-free help")


if __name__ == "__main__":
    main()
