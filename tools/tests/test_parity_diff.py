#!/usr/bin/env python3
"""Exercise the supported stock-snapshot parity CLI."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOL = _common.TOOLS / "parity" / "parity_diff.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(TOOL), *args], text=True, capture_output=True)


def main() -> None:
    base = {
        "packages": {
            "NetPackagePing": {"read": "A", "write": "B", "dir": 1},
            "NetPackageGone": {"read": "A", "write": "A", "dir": 0},
        },
        "enums": {"EnumChunkMode": "byte,short,int"},
    }
    changed = {
        "packages": {
            "NetPackagePing": {"read": "C", "write": "B", "dir": 2},
            "NetPackageNew": {"read": "A", "write": "A", "dir": 0},
        },
        "enums": {"EnumChunkMode": "byte,short,int,int"},
    }
    with tempfile.TemporaryDirectory(dir=_common.scratch_dir()) as td:
        old, new = Path(td) / "old.json", Path(td) / "new.json"
        old.write_text(json.dumps(base), encoding="utf-8")
        new.write_text(json.dumps(changed), encoding="utf-8")

        same = run(str(old), str(old))
        assert same.returncode == 0, same
        assert same.stdout.splitlines() == [
            "=== PACKAGE DIFF ===",
            "added (0): -",
            "removed (0): -",
            "changed wire (0):",
            "=== ENUM DIFF ===",
        ], same.stdout

        drift = run(str(old), str(new))
        assert drift.returncode == 1, drift
        lines = drift.stdout.splitlines()
        assert lines[0] == "=== PACKAGE DIFF ===", lines
        assert "added (1): NetPackageNew" in lines, lines
        assert "removed (1): NetPackageGone" in lines, lines
        assert "changed wire (1):" in lines, lines
        # every drifted field is named, in both directions
        for want in (
            "  NetPackagePing",
            "    dir 1 -> 2",
            "    read OLD A",
            "    read NEW C",
        ):
            assert want in lines, f"missing {want!r} in {lines}"
        # write did not drift, so no write pair may be printed
        assert not any(ln.startswith("    write ") for ln in lines), lines
        # enum drift is part of the changed count and of the report
        assert "  EnumChunkMode: byte,short,int -> byte,short,int,int" in lines, lines

        assert run("--coverage", str(new), td).returncode == 2
        assert run().returncode == 2
    print("OK: parity diff reports stock drift and rejects unsupported modes")


if __name__ == "__main__":
    main()
