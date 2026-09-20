#!/usr/bin/env python3
"""Every `args.<name>` a tool reads must come from one of its `add_argument` calls.

Removing a CLI flag leaves `args.oldflag` behind, and nothing else catches it:
the tool still passes every test that exercises the other flags, and the broken
path only fires when that flag's branch runs (this happened with
`steam_builds --url`, whose live PICS path kept reading `args.url`).

Static, DLL-free, network-free: parse each maintained Python tool, collect the
destinations its parsers declare, and fail on any read that no parser declares.
Parsers built elsewhere (subparsers) are covered because every `add_argument`
call in the file counts. A file that rebinds the name `args` (a local list named
`args`, for example) is skipped: the checker cannot tell the two apart, and a
false FAIL would train people to ignore the gate. The detector is self-tested.

Usage: python3 tools/tests/test_cli_args_wired.py
"""

from __future__ import annotations

import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

SCAN_DIRS = ("", "parity", "sandbox")


def declared_dests(tree: ast.AST) -> set[str]:
    dests: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr != "add_argument":
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                name = arg.value
                dests.add(name.lstrip("-").replace("-", "_") if name.startswith("-") else name)
        for keyword in node.keywords:
            if (
                keyword.arg == "dest"
                and isinstance(keyword.value, ast.Constant)
                and isinstance(keyword.value.value, str)
            ):
                dests.add(keyword.value.value)
    return dests


def _from_parse_args(value: ast.AST | None) -> bool:
    return (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Attribute)
        and value.func.attr == "parse_args"
    )


def rebinds_args(tree: ast.AST) -> bool:
    """True when `args` is also assigned from something other than parse_args()."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            named = any(
                isinstance(target, ast.Name) and target.id == "args" for target in node.targets
            )
            if named and not _from_parse_args(node.value):
                return True
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == "args" and not _from_parse_args(node.value):
                return True
    return False


def read_dests(tree: ast.AST) -> set[str]:
    used: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "args"
        ):
            used.add(node.attr)
    return used


def undeclared(source: str) -> list[str]:
    tree = ast.parse(source)
    declared = declared_dests(tree)
    if rebinds_args(tree) or not declared:
        return []
    return sorted(read_dests(tree) - declared)


def self_test() -> None:
    assert undeclared("import argparse\nargs = argparse.Namespace()\nprint(args.url)\n") == []
    stale = """
import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--from", dest="from_path")
args = ap.parse_args()
print(args.from_path, args.url)
"""
    assert undeclared(stale) == ["url"], undeclared(stale)
    rebinding = """
import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--out")
args = ap.parse_args()
args = []
args.append("x")
"""
    assert undeclared(rebinding) == [], undeclared(rebinding)


def main() -> None:
    self_test()
    bad: list[str] = []
    checked = skipped = 0
    paths = sorted(_common.TOOLS.glob("*.py"))
    for sub in SCAN_DIRS[1:]:
        paths.extend(sorted((_common.TOOLS / sub).glob("*.py")))
    for path in paths:
        if path.name == "__init__.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        if not declared_dests(tree):
            continue  # not a CLI
        checked += 1
        if rebinds_args(tree):
            skipped += 1
            continue
        missing = sorted(read_dests(tree) - declared_dests(tree))
        if missing:
            bad.append(f"{path.relative_to(_common.TOOLS)}: undeclared {', '.join(missing)}")
    if bad:
        for line in bad:
            print(f"FAIL: {line}", file=sys.stderr)
        raise SystemExit(1)
    print(
        f"OK: {checked} argparse tools read only declared arguments ({skipped} skipped: rebind args)"
    )


if __name__ == "__main__":
    main()
