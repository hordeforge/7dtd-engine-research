#!/usr/bin/env python3
"""Exercise the supported stock-snapshot parity CLI."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "parity" / "parity_diff.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(TOOL), *args], text=True, capture_output=True)


def main() -> None:
    base = {"packages": {"NetPackagePing": {"read": "A", "write": "B", "dir": 1}}, "enums": {}}
    changed = {"packages": {"NetPackagePing": {"read": "C", "write": "B", "dir": 1}}, "enums": {}}
    with tempfile.TemporaryDirectory() as td:
        old, new = Path(td) / "old.json", Path(td) / "new.json"
        old.write_text(json.dumps(base), encoding="utf-8")
        new.write_text(json.dumps(changed), encoding="utf-8")
        assert run(str(old), str(old)).returncode == 0
        assert run(str(old), str(new)).returncode == 1
        assert run("--coverage", str(new), td).returncode == 2
        assert run().returncode == 2
    print("OK: parity diff reports stock drift and rejects unsupported modes")


if __name__ == "__main__":
    main()
