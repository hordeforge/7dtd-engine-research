#!/usr/bin/env python3
"""Every text boundary in the Python tooling names its encoding.

Two failure modes this pins, both real on a UTF-8 host:

- A subprocess runner with `text=True` and no `encoding=` decodes with
  locale.getpreferredencoding(). Under LC_ALL=C (which tools/build.sh and
  tools/parity/drift-check.sh export) that is ANSI_X3.4-1968, and one non-ASCII
  byte in a tool's output (a type or asset name, a localized error string)
  raises UnicodeDecodeError instead of reporting the tool's result.
- open()/read_text()/write_text() without `encoding=` binds the process locale
  to a file read, so a save dump or an inventory written as UTF-8 is decoded as
  whatever the shell's locale happens to be.

The static half scans the tree (AST, so a string in a comment never matches and
a keyword can never hide); the runtime half runs the shared runner under a C
locale and a child that writes raw UTF-8 bytes, which is the exact input that
raised before.

Usage: python3 tools/tests/test_text_encoding.py
"""

import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOLS = _common.TOOLS
REPO = _common.REPO
SKIP_DIRS = {".git", "il", "__pycache__", ".scratch", ".mypy_cache", ".ruff_cache"}
# Callables that decode a child's bytes, and Path methods that decode a file's.
SUBPROCESS_CALLS = {"run", "Popen", "call", "check_call", "check_output"}
TEXT_MODE = {"text", "universal_newlines"}
# Writes raw UTF-8 regardless of the inherited locale, so the decode is the
# only thing under test.
CHILD = "import sys; sys.stdout.buffer.write('caf\\u00e9\\n'.encode('utf-8'))"


def _python_files() -> list[str]:
    out: list[str] = []
    for sub, dirs, names in os.walk(str(TOOLS)):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        out.extend(os.path.join(sub, n) for n in sorted(names) if n.endswith(".py"))
    return out


def _kwargs(call: ast.Call) -> dict[str, ast.expr]:
    return {kw.arg: kw.value for kw in call.keywords if kw.arg}


def _is_const_true(node: ast.expr) -> bool:
    return isinstance(node, ast.Constant) and node.value is True


def _encoding_missing(path: str, tree: ast.AST) -> list[str]:
    bad: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        kw = _kwargs(node)
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr in TEXT_MODE:
            if "encoding" not in kw:
                bad.append(f"{path}:{node.lineno}: {func.attr}() without encoding=")
        elif isinstance(func, ast.Name) and func.id == "open":
            # mode is the second positional argument, and defaults to text.
            mode = (
                kw.get("mode") if "mode" in kw else (node.args[1] if len(node.args) > 1 else None)
            )
            binary = isinstance(mode, ast.Constant) and "b" in str(mode.value)
            if not binary and "encoding" not in kw:
                bad.append(f"{path}:{node.lineno}: open() without encoding=")
        elif isinstance(func, ast.Attribute) and func.attr in ("read_text", "write_text"):
            if "encoding" not in kw:
                bad.append(f"{path}:{node.lineno}: {func.attr}() without encoding=")
        elif isinstance(func, ast.Attribute) and func.attr in SUBPROCESS_CALLS:
            owner = func.value
            is_subprocess = (isinstance(owner, ast.Name) and owner.id == "subprocess") or (
                isinstance(owner, ast.Attribute) and owner.attr == "subprocess"
            )
            if not is_subprocess:
                continue
            text_mode = any(
                key in TEXT_MODE and _is_const_true(kw[key]) for key in kw if key in TEXT_MODE
            )
            if text_mode and "encoding" not in kw:
                bad.append(
                    f"{path}:{node.lineno}: subprocess.{func.attr}() in text mode without encoding="
                )
    return bad


def static_scan() -> list[str]:
    bad: list[str] = []
    for path in _python_files():
        with open(path, encoding="utf-8") as fh:
            bad.extend(
                _encoding_missing(os.path.relpath(path, str(REPO)), ast.parse(fh.read(), path))
            )
    return bad


def c_locale_child() -> tuple[int, str, str]:
    """Run the shared runner under a C locale against a child emitting UTF-8."""
    sys.path.insert(0, str(TOOLS))
    import tooling

    env = dict(os.environ) | {"LC_ALL": "C", "LANG": "C"}
    # PEP 538/540 auto-enable UTF-8 in a C locale, which would hide the defect
    # this pins; turn both off so the runner is decoded exactly as written.
    env["PYTHONCOERCECLOCALE"] = "0"
    env["PYTHONUTF8"] = "0"
    return tooling.run_bounded([sys.executable, "-c", CHILD], env=env, timeout=60.0)


def main() -> int:
    bad = static_scan()
    rc, out, err = c_locale_child()
    if rc != 0 or out != "café\n":
        bad.append(f"C-locale child: rc={rc} stdout={out!r} stderr={err.strip()!r}")
    if bad:
        for b in bad:
            print("FAIL:", b)
        return 1
    print("OK: text boundaries name their encoding; C-locale subprocess decode is UTF-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
