#!/usr/bin/env python3
"""Print the dedicated server's assembly path, or the install root around it.

One resolution for every entry point that needs the live dedicated build. The
Python tools already resolved `ASM` / `SEVENDTD_ASM` / `SEVENDTD_DS_DIR` and
every Steam library root of the host OS, while the Makefile and the shell entry
points each carried the Linux path as a literal: on Windows or macOS the
documented variables were honoured by the tools and ignored by `make`, and the
`Data/Config` pins had no way to find the install at all. This prints the same
answer the tools get, so a Makefile `$(shell ...)` and a shell `$(...)` cannot
drift apart.

Usage:
  python3 tools/asm_path.py              # the Assembly-CSharp.dll in use
  python3 tools/asm_path.py --game-dir   # the install root holding Data/Config

Nothing found prints no path, says which variables to set, and exits 0: the
value lands in a variable that a later `-f "$ASM"` guard reports with its own
context, and a nonzero exit would instead kill a `set -e` caller whose run does
not need the DLL (a `--check-only` pin check, for one). An override that points
at nothing is the opposite case and exits 2: discovery would otherwise fall
through to a probed root and quietly study a different install than the one
named.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tooling

VARS = "/".join(tooling.ASM_VARS)
MISSING = 2


def resolve(game_dir: bool) -> tuple[str, int]:
    """`(path, rc)`. The path is "" with the reason on stderr when it is unusable."""
    for name, path in tooling.env_candidates(os.environ):
        if not path.is_file():
            print(f"asm_path: {name}={path} is not a file", file=sys.stderr)
            return "", MISSING
    asm = tooling.find_asm()
    if asm is None:
        print(f"asm_path: no dedicated server found; set {VARS}", file=sys.stderr)
        return "", 0
    if not game_dir:
        return str(asm), 0
    root = tooling.game_dir(asm)
    if root is None:
        print(
            f"asm_path: {asm} is not under an install root; pass --game-dir "
            "(the directory holding Data/Config)",
            file=sys.stderr,
        )
        return "", MISSING
    return str(root), 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Print the dedicated server's assembly path or its install root."
    )
    ap.add_argument(
        "--game-dir",
        action="store_true",
        help="print the install root holding Data/Config instead of the assembly",
    )
    args = ap.parse_args()
    path, rc = resolve(args.game_dir)
    if path:
        print(path)
    return rc


if __name__ == "__main__":
    sys.exit(main())
