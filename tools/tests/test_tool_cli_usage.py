#!/usr/bin/env python3
"""Require a consistent missing-argument contract from maintained C# tools."""

import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOLS = _common.TOOLS
SHARED = {"AsmWalk", "IlFmt", "Seeds"}


def main() -> None:
    if shutil.which("mono") is None:
        print("SKIP: maintained-tool CLI probe needs mono")
        return
    names = {p.stem for p in (TOOLS / "src").glob("*.cs")} - SHARED
    names.add("ParitySurface")
    missing = sorted(name for name in names if not (TOOLS / "bin" / f"{name}.exe").is_file())
    if missing:
        print("SKIP: build maintained tools first: " + ", ".join(missing))
        return
    bad = []
    for name in sorted(names):
        result = subprocess.run(
            ["mono", str(TOOLS / "bin" / f"{name}.exe")], text=True, capture_output=True
        )
        if result.returncode != 2 or "usage:" not in result.stderr.lower():
            bad.append(f"{name}: rc={result.returncode}, stderr={result.stderr.strip()!r}")
    assert not bad, "\n".join(bad)
    print(f"OK: {len(names)} maintained C# CLIs reject missing arguments with usage + exit 2")


if __name__ == "__main__":
    main()
