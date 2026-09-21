#!/usr/bin/env python3
"""Tools live in documented folders, and the tools do not reach into tests.

Two structural rules that a move or a new script can silently break:

  1. No maintained module under `tools/` (outside `tools/tests/`) imports the
     test package (`tests/_common`) or any `tests.*` module. Tools importing
     test helpers was the state before `tools/tooling.py` existed: it made the
     tools depend on the gate suite's package and hid the shared helpers in the
     wrong place.
  2. Every `.py` under `tools/` is named in `tools/README.md`, so moving or
     splitting a file without documenting it fails here rather than drifting.

Usage: python3 tools/tests/test_tools_layout.py
"""

from __future__ import annotations

import ast
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

README = _common.TOOLS / "README.md"
FORBIDDEN = ("_common", "tests")


def imports_test_package(tree: ast.AST) -> list[str]:
    """Import statements that pull in a name from the forbidden set."""
    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN:
                    offenders.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".")[0]
            if root in FORBIDDEN:
                offenders.append(f"from {node.module} import ...")
    return offenders


def main() -> None:
    readme = README.read_text(encoding="utf-8")
    bad: list[str] = []
    checked = 0
    for path in sorted(_common.TOOLS.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        relative = path.relative_to(_common.TOOLS)
        if "tests" not in relative.parts:
            checked += 1
            offenders = imports_test_package(ast.parse(path.read_text(encoding="utf-8")))
            for offender in offenders:
                bad.append(f"{relative}: {offender} (tools must import tools/tooling.py)")
        # Whole-token match on the basename: a path prefix (`tests/`, `sandbox/`)
        # is fine, but "tooling.py" must not pass merely because
        # `bench_version_update_tooling.py` contains it.
        if re.search(rf"(?<![\w.]){re.escape(relative.name)}(?![\w])", readme) is None:
            bad.append(f"{relative}: not named in tools/README.md")
    if bad:
        for line in bad:
            print(f"FAIL: {line}", file=sys.stderr)
        raise SystemExit(1)
    print(
        f"OK: {checked} maintained modules import no test helpers, and every tools/*.py "
        "is documented"
    )


if __name__ == "__main__":
    main()
