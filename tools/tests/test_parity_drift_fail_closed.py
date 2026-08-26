#!/usr/bin/env python3
"""Ensure drift-check cannot bless an incomplete snapshot."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOLS = _common.TOOLS


def main() -> None:
    required = ("mono", "mcs")
    bins = ("Mono.Cecil.dll", "Census.exe", "FullSurface.exe", "EnumList.exe")
    if any(shutil.which(cmd) is None for cmd in required) or any(
        not (TOOLS / "bin" / name).is_file() for name in bins
    ):
        print("SKIP: drift fail-closed runtime probe needs built tools, mono, and mcs")
        return
    with tempfile.TemporaryDirectory(dir=_common.scratch_dir()) as td:
        root = Path(td)
        bad_asm = root / "not-an-assembly.dll"
        bad_asm.touch()
        env = os.environ | {"BASELINE_DIR": str(root / "baseline")}
        result = subprocess.run(
            [str(TOOLS / "parity" / "drift-check.sh"), str(bad_asm)],
            env=env,
            text=True,
            capture_output=True,
        )
        assert result.returncode == 2
        assert "drift: INCOMPLETE" in result.stderr
        assert not (root / "baseline" / "surface").exists()
    print("OK: drift check rejects incomplete snapshots without creating a baseline")


if __name__ == "__main__":
    main()
