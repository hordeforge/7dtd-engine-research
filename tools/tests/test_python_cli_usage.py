#!/usr/bin/env python3
"""Require dependency-free help from optional Python tools."""

import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
SCRIPTS = (
    "shader_blob_dump.py",
    "save_roundtrip_check.py",
    "facts.py",
    "mention_depth.py",
    "sandbox/extract_mesh_atlas.py",
    "sandbox/extract_sandbox_tables.py",
    "sandbox/extract_preset_codes.py",
    "sandbox/gen_atlas_zig.py",
    "sandbox/gen_zig_tables.py",
    "sandbox/try_extract_presets.py",
)


def main() -> None:
    bad = []
    for relative in SCRIPTS:
        path = TOOLS / relative
        result = subprocess.run([sys.executable, path, "--help"], text=True, capture_output=True)
        if result.returncode != 0 or "usage:" not in result.stdout.lower():
            bad.append(f"{relative}: rc={result.returncode}, stderr={result.stderr.strip()!r}")
    assert not bad, "\n".join(bad)
    print(f"OK: {len(SCRIPTS)} optional Python CLIs provide dependency-free help")


if __name__ == "__main__":
    main()
