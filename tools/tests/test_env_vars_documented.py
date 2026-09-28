#!/usr/bin/env python3
"""Every environment variable the tools and the Makefile read is documented.

Configuration here is entirely env vars, so the only inventory that matters is
which ones exist and what an operator has to set. That list is spread over
`tools/tooling.py`, two Steam tools, the Makefile and the shell entry points, and
nothing kept it together: a new variable could be added with a default nobody
outside the diff knows, which is how a timeout or a scratch path ends up
impossible to change from outside the tool that reads it.

This gate collects the names the code actually reads (AST scan of the tools, plus
the Makefile's own variables) and requires each in the `tools/README.md`
"Environment variables" table, under a `VAR` backtick cell. A name in the table
that nothing reads is the other half of the drift and fails the same way.

Names the scan cannot attribute to configuration are listed in `NOT_CONFIG` with
the reason, so the exception stays a reviewed list rather than a growing regex
exemption. Stdlib only, no DLL, no network.

Usage: python3 tools/tests/test_env_vars_documented.py
"""

from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

README = _common.TOOLS / "README.md"
MAKEFILE = _common.REPO / "Makefile"
SECTION = "## Environment variables"

# Environment-shaped names the scan finds that are not operator configuration.
# Each is a real name, so the exemption is visible in review.
NOT_CONFIG = {
    "ASM_VARS": "make's own list of the ASM_VARS names, not a variable",
    "CURDIR": "make's own path variable",
    "HOME": "the operator's home directory, the fallback base for scratch paths",
    "ROOT": "make's own path variable",
    "SHELL": "make's own variable",
    "TOOLS": "make's own path variable",
}

# `VAR` in a backticked table cell of the section, e.g. `| `ASM` | ... |`.
CELL_RE = re.compile(r"^\|\s*`([A-Z][A-Z0-9_]*)`", re.M)
MAKE_ASSIGN_RE = re.compile(r"^([A-Z][A-Z0-9_]*)\s*[:?+]?=", re.M)
MAKE_USE_RE = re.compile(r"\$\{?\$\{?([A-Z][A-Z0-9_]*)\b")


def env_reads(path: Path) -> set[str]:
    """Names read out of the environment by one Python file.

    `os.environ.get("X")`, `os.environ["X"]` and `os.getenv("X")` for direct
    reads; module constants holding a variable name are followed, so the
    indirection every tool already uses (`MONO_TIMEOUT_ENV`) is covered without
    a second scan.
    """
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    consts: dict[str, str | tuple[str, ...]] = {}
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        value = node.value
        for target in targets:
            if not isinstance(target, ast.Name) or value is None:
                continue
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                consts[target.id] = value.value
            elif isinstance(value, (ast.Tuple, ast.List)):
                parts = tuple(
                    item.value
                    for item in value.elts
                    if isinstance(item, ast.Constant) and isinstance(item.value, str)
                )
                if parts:
                    consts[target.id] = parts

    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "getenv" and _is_os(node.func.value):
                found.update(_string_args(node))
            if node.func.attr == "get" and _is_environ(node.func.value):
                found.update(_string_args(node))
        if isinstance(node, ast.Subscript) and _is_environ(node.value):
            found.update(_string_args(node))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "getenv":
                found.update(_string_args(node))
    # Constants: a bare string (a timeout's variable) or a tuple of them (the
    # override names in one list), read from the `_ENV` / `_VARS` constants the
    # tools already use. Other uppercase tuples are path parts and verdict
    # words, not variables.
    for name, value in consts.items():
        if not name.isupper() or not name.endswith(("_ENV", "_VARS")):
            continue
        if isinstance(value, str) and re.fullmatch(r"[A-Z][A-Z0-9_]*", value):
            found.add(value)
        elif isinstance(value, tuple):
            found.update(v for v in value if re.fullmatch(r"[A-Z][A-Z0-9_]*", v))
    return found


def _is_os(node: ast.expr) -> bool:
    return isinstance(node, ast.Name) and node.id == "os"


def _is_environ(node: ast.expr) -> bool:
    return isinstance(node, ast.Attribute) and node.attr == "environ" and _is_os(node.value)


def _string_args(node: ast.Call) -> set[str]:
    """The name a call reads, its first argument; a default is not a variable."""
    if not node.args:
        return set()
    first = node.args[0]
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        return {first.value}
    return set()


def make_vars() -> set[str]:
    """Uppercase names the Makefile assigns or reads from its environment."""
    text = MAKEFILE.read_text(encoding="utf-8")
    found = set(MAKE_ASSIGN_RE.findall(text)) | set(MAKE_USE_RE.findall(text))
    return {name for name in found if not name.startswith("$$")}


def main() -> int:
    readme = README.read_text(encoding="utf-8")
    if SECTION not in readme:
        print(f"FAIL: {README.name} has no {SECTION!r} section", file=sys.stderr)
        return 1
    documented = set(CELL_RE.findall(readme.split(SECTION, 1)[1]))

    read: set[str] = set()
    for path in sorted(_common.TOOLS.rglob("*.py")):
        if "tests" in path.parts or "__pycache__" in path.parts:
            continue
        read |= env_reads(path)
    read |= make_vars()
    read -= set(NOT_CONFIG)

    bad = [
        f"{name}: read by the tools but not in the tools/README.md table"
        for name in sorted(read - documented)
    ]
    bad += [
        f"{name}: in the tools/README.md table but read by nothing"
        for name in sorted(documented - read)
    ]
    if bad:
        for line in bad:
            print("FAIL:", line)
        return 1
    print(f"OK: {len(read)} configuration variables documented in tools/README.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
