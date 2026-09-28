#!/usr/bin/env python3
"""The body-diff lens survives a failing walk on either side.

`asm_body_diff.py` hashes two assemblies concurrently, one walk per thread. A
walk that throws (an unreadable path, a file that is not an assembly) escaped
the thread, and Mono turns an unhandled exception on any thread into a process
abort: the run died with a runtime stack trace naming neither side, the other
walk's work was thrown away, and the two maps the main thread reads had no
guarantee behind them. Each walk now owns its result slot and reports its own
failure, so the run exits 1 naming the side instead.

The shipped `AsmBodyDiff` class is compiled and run here against a stand-in
`BodyHasher` (the real one needs Mono.Cecil.dll from `make tools`), so the
behaviour is pinned on the text that ships rather than on a copy of it.

Usage: python3 tools/tests/test_asm_body_diff_threads.py
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOL = _common.TOOLS / "asm_body_diff.py"

# Stand-in for the Cecil-backed hasher: one map entry per line of the input, and
# a throw on the first line reading "bad" so a failing walk can be provoked
# without a game assembly.
STUB_HASHER = """
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;

class BodyHasher {
  public Dictionary<string,string> Map(string path) {
    var lines = File.ReadAllLines(path);
    if (lines.Length > 0 && lines[0] == "bad") throw new BadImageFormatException(path);
    var d = new Dictionary<string,string>();
    foreach (var l in lines) d[l] = "hash\\t1";
    return d;
  }
}
"""


def shipped_class() -> str:
    """The `AsmBodyDiff` class text, out of the tool's embedded C# source."""
    text = TOOL.read_text(encoding="utf-8")
    embedded = re.search(r'HASH_CS = r"""(.*?)"""', text, re.S)
    assert embedded is not None, f"{TOOL}: no embedded C# source (HASH_CS)"
    body = re.search(r"static class AsmBodyDiff \{.*?\n\}\n", embedded.group(1), re.S)
    assert body is not None, f"{TOOL}: no AsmBodyDiff class in the embedded source"
    return body.group(0)


def build(directory: Path) -> Path:
    source = directory / "Probe.cs"
    source.write_text(STUB_HASHER + shipped_class(), encoding="utf-8")
    exe = directory / "Probe.exe"
    proc = _common.run_cmd(["mcs", f"-out:{exe}", str(source)])
    assert proc.returncode == 0, f"mcs failed on the shipped AsmBodyDiff:\n{proc.stderr}"
    return exe


def fixture(directory: Path, name: str, *lines: str) -> Path:
    path = directory / name
    path.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
    return path


def main() -> int:
    for tool in ("mcs", "mono"):
        if shutil.which(tool) is None:
            print(f"SKIP: {tool} not on PATH")
            return 0
    with tempfile.TemporaryDirectory(prefix="body-diff-threads-", dir=_common.scratch_dir()) as td:
        directory = Path(td)
        exe = build(directory)
        old = fixture(directory, "old.txt", "a::M", "b::M")
        new = fixture(directory, "new.txt", "a::M", "c::M")
        bad = fixture(directory, "bad.txt", "bad")

        ok = _common.run_cmd(["mono", str(exe), str(old), str(new)])
        assert ok.returncode == 0, f"the happy path failed:\n{ok.stdout}{ok.stderr}"
        assert "methods bak=2 live=2 added=1 removed=1" in ok.stdout, ok.stdout
        assert "FATAL UNHANDLED EXCEPTION" not in ok.stderr, ok.stderr

        for side, first, second in (("old", bad, new), ("new", old, bad)):
            proc = _common.run_cmd(["mono", str(exe), str(first), str(second)])
            assert proc.returncode == 1, f"{side} walk failure: rc={proc.returncode}\n{proc.stderr}"
            assert "FATAL UNHANDLED EXCEPTION" not in proc.stderr, proc.stderr
            assert f"{side} assembly walk failed" in proc.stderr, proc.stderr

        usage = _common.run_cmd(["mono", str(exe), str(old)])
        assert usage.returncode == 2, f"a one-argument run: rc={usage.returncode}\n{usage.stderr}"
        assert "usage:" in usage.stderr, usage.stderr
    print("OK: a failing walk names its side and exits 1; the happy path is unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
