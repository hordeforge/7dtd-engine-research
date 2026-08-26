#!/usr/bin/env python3
"""Verify the sandbox preset decoder and its path-independent CLI."""

import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOL = _common.TOOLS / "sandbox" / "extract_preset_codes.py"


def main() -> None:
    with tempfile.TemporaryDirectory(dir=_common.scratch_dir()) as td:
        result = subprocess.run([sys.executable, str(TOOL)], cwd=td, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    rows = result.stdout.splitlines()
    assert len(rows) == 7
    assert "Scavenger" in rows[1]
    assert rows[1].endswith("0.5 | 1 | 2 | 2")
    assert "Nomad" in rows[3]
    assert rows[3].endswith("1 | 1 | 1 | 1")

    probe = (
        f"import sys; sys.path.insert(0, {str(TOOL.parent)!r}); "
        "from extract_preset_codes import decode; decode('bad', {}, {})"
    )
    bad = subprocess.run(
        [sys.executable, "-c", probe],
        text=True,
        capture_output=True,
    )
    assert bad.returncode != 0
    assert "invalid sandbox code shape" in bad.stderr
    print("OK: sandbox preset decoder is strict and independent of the working directory")


if __name__ == "__main__":
    main()
