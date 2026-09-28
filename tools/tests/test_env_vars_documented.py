#!/usr/bin/env python3
"""Every environment variable the tools and the Makefile read is documented.

Configuration here is entirely env vars, so the only inventory that matters is
which ones exist and what an operator has to set. That list is spread over
`tools/tooling.py`, two Steam tools, the Makefile and the shell entry points, and
nothing kept it together: a new variable could be added with a default nobody
outside the diff knows, which is how a timeout or a scratch path ends up
impossible to change from outside the tool that reads it.

This gate collects the names the code actually reads (AST scan of the Python
tools, the Makefile's own variables, and the defaulting expansions in the shell
entry points) and requires each in the `tools/README.md` "Environment variables"
table, under a `VAR` backtick cell. A name in the table that nothing reads is
the other half of the drift and fails the same way.

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
    "ASM_RESOLVE": "make's own resolver command, not a variable an operator sets",
    "ASM_VARS": "make's own list of the ASM_VARS names, not a variable",
    "CURDIR": "make's own path variable",
    "GAME_ROOT_RESOLVE": "make's own resolver command, not a variable an operator sets",
    "HOME": "the operator's home directory, the fallback base for scratch paths",
    "ROOT": "make's own path variable",
    "SHELL": "make's own variable",
    "TOOLS": "make's own path variable",
}

# `VAR` in a backticked table cell of the section, e.g. `| `ASM` | ... |`.
CELL_RE = re.compile(r"^\|\s*`([A-Z][A-Z0-9_]*)`", re.M)
MAKE_ASSIGN_RE = re.compile(r"^([A-Z][A-Z0-9_]*)\s*[:?+]?=", re.M)
MAKE_USE_RE = re.compile(r"\$\{?\$\{?([A-Z][A-Z0-9_]*)\b")
ENV_NAME_RE = re.compile(r"[A-Z][A-Z0-9_]*")


def env_reads(path: Path) -> set[str]:
    """Names read out of the environment by one Python file.

    `os.environ.get("X")`, `os.environ["X"]` and `os.getenv("X")` for direct
    reads; module constants holding a variable name are followed, so the
    indirection every tool already uses (`MONO_TIMEOUT_ENV`) is covered without
    a second scan.
    """
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    consts: dict[str, str | tuple[str, ...]] = {}
    for stmt in tree.body:
        if not isinstance(stmt, (ast.Assign, ast.AnnAssign)):
            continue
        targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
        init = stmt.value
        for target in targets:
            if not isinstance(target, ast.Name) or init is None:
                continue
            if isinstance(init, ast.Constant) and isinstance(init.value, str):
                consts[target.id] = init.value
            elif isinstance(init, (ast.Tuple, ast.List)):
                parts = tuple(
                    item.value
                    for item in init.elts
                    if isinstance(item, ast.Constant) and isinstance(item.value, str)
                )
                if parts:
                    consts[target.id] = parts

    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "getenv" and _is_os(node.func.value):
                found.update(_call_arg_name(node))
            if node.func.attr == "get" and _is_environ(node.func.value):
                found.update(_call_arg_name(node))
        if isinstance(node, ast.Subscript) and _is_environ(node.value):
            found.update(_subscript_name(node))
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "getenv"
        ):
            found.update(_call_arg_name(node))
    # Constants: a bare string (a timeout's variable) or a tuple of them (the
    # override names in one list), read from the `_ENV` / `_VARS` constants the
    # tools already use. Other uppercase tuples are path parts and verdict
    # words, not variables.
    for name, constant in consts.items():
        if not name.isupper() or not name.endswith(("_ENV", "_VARS")):
            continue
        if isinstance(constant, str) and ENV_NAME_RE.fullmatch(constant):
            found.add(constant)
        elif isinstance(constant, tuple):
            found.update(v for v in constant if ENV_NAME_RE.fullmatch(v))
    return found


def _is_os(node: ast.expr) -> bool:
    return isinstance(node, ast.Name) and node.id == "os"


def _is_environ(node: ast.expr) -> bool:
    return isinstance(node, ast.Attribute) and node.attr == "environ" and _is_os(node.value)


def _constant_str(node: ast.expr) -> str | None:
    """A plain string literal expression, or None for anything computed."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _call_arg_name(node: ast.Call) -> set[str]:
    """The name a call reads, its first argument; a default is not a variable."""
    if not node.args:
        return set()
    name = _constant_str(node.args[0])
    return {name} if name is not None else set()


def _subscript_name(node: ast.Subscript) -> set[str]:
    """The name `os.environ["X"]` reads.

    A subscript carries its key in `slice`, not in `args`: routing it through
    the call reader raised AttributeError on the first tool that used the
    subscript form, which is why the scan documented a form it could not read.
    """
    name = _constant_str(node.slice)
    return {name} if name is not None else set()


def make_vars() -> set[str]:
    """Uppercase names the Makefile assigns or reads from its environment."""
    text = MAKEFILE.read_text(encoding="utf-8")
    found = set(MAKE_ASSIGN_RE.findall(text)) | set(MAKE_USE_RE.findall(text))
    return {name for name in found if not name.startswith("$$")}


# `${NAME` followed by a default or required expansion: `:-`, `-`, `:=`, `=`,
# `:?`, `?`, `:+`, `+`. A name that only ever appears bare (`"$OUT"`) is a local
# the script assigned, which every shell entry point does, so counting it would
# drown the inventory; the defaulting form is what says an operator may set it.
# The character after an optional `:` has to be an expansion operator, not a
# digit, so a substring read (`${ASM_DIGEST:0:12}`) is not a config read.
SHELL_DEFAULT_RE = re.compile(r"\$\{([A-Z][A-Z0-9_]*)[:-=+?]?[-=+?]")


def shell_vars() -> set[str]:
    """Uppercase names the shell entry points read from the environment.

    Scanned over `*.sh` under `tools/`, source lines only: a name in a comment
    is a note about the variable, not a read of it, and quoting it in a gate
    that then fails on it sends the next maintainer looking for a knob nobody
    reads.
    """
    found: set[str] = set()
    for path in sorted(_common.TOOLS.rglob("*.sh")):
        for line in shell_code(path):
            found.update(SHELL_DEFAULT_RE.findall(line))
    return found


def shell_code(path: Path) -> list[str]:
    """Each line of one shell script with comments and single-quoted text cut.

    A `#` inside a string is text, not a comment, and quote state carries across
    lines because a multi-line string leaves the next line inside it. Double
    quotes are kept: bash expands `"${VAR}"` but not `'$VAR'`, so the read lives
    in the double-quoted span, which is where every defaulting read in this tree
    is written. Same rule the bounded-runs gate uses for spawns, so a `# VAR=`
    in a usage header never becomes a variable the code does not read.
    """
    return _ShellScanner().code(path.read_text(encoding="utf-8"))


class _ShellScanner:
    """Splits shell source into expandable code, line by line."""

    def __init__(self) -> None:
        self.quote: str | None = None

    def code(self, text: str) -> list[str]:
        lines: list[str] = []
        for line in text.splitlines():
            lines.append("".join(self._chars(line)))
        return lines

    def _chars(self, line: str) -> list[str]:
        """The expandable characters of one line, tracking quote state."""
        kept: list[str] = []
        for index, char in enumerate(line):
            if self.quote == "'":
                if char == "'":
                    self.quote = None
                continue
            if self.quote == '"':
                kept.append(char)
                if char == '"':
                    self.quote = None
                continue
            if char == "'":
                self.quote = "'"
                continue
            if char == '"':
                self.quote = '"'
                kept.append(char)
                continue
            if char == "#" and (index == 0 or line[index - 1].isspace()):
                break
            kept.append(char)
        return kept


def self_test() -> list[str]:
    """The shell scan against source whose answer is known, so the gate cannot
    pass by reading nothing.

    Each case is a line (or lines) of shell with the names the scan must find,
    and the ones it must not: a documented knob in a comment, a single-quoted
    literal, a substring read, and a local the script assigned itself.
    """
    cases: list[tuple[str, set[str], set[str]]] = [
        ('OUT="${OUT:-$SCRATCH}"', {"OUT"}, set()),
        ('if [[ -n "${STEAMCMD:-}" ]]; then', {"STEAMCMD"}, set()),
        ('V="${VAR?}"', {"VAR"}, set()),
        ('V="${VAR+x}"', {"VAR"}, set()),
        # A usage header naming the knob, a literal quoted string, a substring
        # read of a local, and a bare local: none of them is a read.
        ('# SCRATCH=/tmp/cache\n"$OUT"\necho "${ASM_DIGEST:0:12}"', set(), {"SCRATCH", "OUT"}),
        ("echo 'literal ${NOT_A_VAR}'", set(), {"NOT_A_VAR"}),
    ]
    bad = []
    for source, want, unwanted in cases:
        scanner = _ShellScanner()
        found: set[str] = set()
        for line in scanner.code(source):
            found.update(SHELL_DEFAULT_RE.findall(line))
        for name in sorted(want - found):
            bad.append(f"self-test: {name} not found in {source!r}")
        for name in sorted(found & unwanted):
            bad.append(f"self-test: {name} wrongly read from {source!r}")
    return bad


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
    read |= shell_vars()
    read -= set(NOT_CONFIG)

    bad = self_test()
    bad += [
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
