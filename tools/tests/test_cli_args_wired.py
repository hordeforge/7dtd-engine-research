#!/usr/bin/env python3
"""CLI flags must be wired both ways: declared then read, read then declared.

Removing a CLI flag leaves `args.oldflag` behind, and nothing else catches it:
the tool still passes every test that exercises the other flags, and the broken
path only fires when that flag's branch runs (this happened with
`steam_builds --url`, whose live PICS path kept reading `args.url`).

Static, DLL-free, network-free. Two failures are caught: an `args.<name>` read
that no `add_argument` declares (the stale flag left after removing one, which
happened with `steam_builds --url`), and a declared flag that nothing reads (a
dead CLI surface, which the same removal should not leave behind either).
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


def declared_dests(tree: ast.AST) -> set[str]:
    dests: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr != "add_argument":
            continue
        explicit = next(
            (
                keyword.value.value
                for keyword in node.keywords
                if keyword.arg == "dest"
                and isinstance(keyword.value, ast.Constant)
                and isinstance(keyword.value.value, str)
            ),
            None,
        )
        if explicit is not None:
            dests.add(explicit)
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                name = arg.value
                dests.add(name.lstrip("-").replace("-", "_") if name.startswith("-") else name)
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


def unread(source: str) -> list[str]:
    """Declared destinations that no `args.<name>` read ever touches."""
    tree = ast.parse(source)
    declared = declared_dests(tree)
    if rebinds_args(tree) or not declared:
        return []
    read = read_dests(tree)
    return sorted(dest for dest in declared if dest not in read and dest != "help")


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
    assert unread(stale) == [], unread(stale)
    dead = """
import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--url", default="x")
ap.add_argument("--from", dest="from_path")
args = ap.parse_args()
print(args.from_path)
"""
    assert unread(dead) == ["url"], unread(dead)
    assert undeclared(dead) == [], undeclared(dead)
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
    for path in _common.argparse_clis():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        if not declared_dests(tree):
            continue  # help-only CLI, nothing to wire
        checked += 1
        if rebinds_args(tree):
            skipped += 1
            continue
        relative = path.relative_to(_common.TOOLS)
        missing = sorted(read_dests(tree) - declared_dests(tree))
        if missing:
            bad.append(f"{relative}: undeclared {', '.join(missing)}")
        unused = sorted(dest for dest in declared_dests(tree) if dest not in read_dests(tree))
        if unused:
            bad.append(f"{relative}: declared but never read {', '.join(unused)}")
    if bad:
        for line in bad:
            print(f"FAIL: {line}", file=sys.stderr)
        raise SystemExit(1)
    print(
        f"OK: {checked} argparse tools wire every read to a declaration and every "
        f"declaration to a read ({skipped} skipped: rebind args)"
    )


if __name__ == "__main__":
    main()
