#!/usr/bin/env python3
"""Regression test: IlFmt.Safe must never yield a fragment that escapes the dump out-dir.

Assembly-supplied namespace/type names flow into Path.Combine output paths
(DumpAll/DumpType/DumpNetPackages). Safe() keeps dots for namespaces, so a
crafted assembly naming a type or namespace "." or ".." used to produce a
parent-directory component (write outside il/<label>). Requires mcs + mono +
bin/Mono.Cecil.dll; SKIPs cleanly without them so CI stays green.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOLS = _common.TOOLS
CECIL = TOOLS / "bin" / "Mono.Cecil.dll"
ILFMT = TOOLS / "src" / "IlFmt.cs"
WORK = TOOLS.parent / ".scratch" / "ilfmt-safe"

# (assembly-supplied name, expected sanitized fragment)
CASES = [
    ("..", "_.."),
    (".", "_."),
    ("../x", ".._x"),
    ("System.Collections", "System.Collections"),  # namespaces keep their dots
    ("Foo/Bar\\Baz", "Foo_Bar_Baz"),
    ("", ""),
]


PROBE_CS = """\
using System;
using System.IO;
static class Probe {
  static int Main(string[] args) {
    var baseDir = Path.GetFullPath(args[0]);
    int bad = 0;
    for (int i = 1; i < args.Length; i++) {
      var name = args[i];
      var frag = IlFmt.Safe(name);
      var full = Path.GetFullPath(Path.Combine(baseDir, frag));
      var ok = full == baseDir || full.StartsWith(baseDir + Path.DirectorySeparatorChar);
      Console.WriteLine(name + "\\t" + frag + "\\t" + (ok ? "OK" : "ESCAPE"));
      if (!ok) bad++;
    }
    return bad == 0 ? 0 : 1;
  }
}
"""


def main() -> int:
    if shutil.which("mcs") is None or shutil.which("mono") is None:
        print("SKIP: mcs/mono not on PATH")
        return 0
    if not CECIL.is_file():
        print("SKIP: no built bin/Mono.Cecil.dll (run make tools)")
        return 0

    WORK.mkdir(parents=True, exist_ok=True)
    base = WORK / "out"
    base.mkdir(exist_ok=True)
    probe_cs = WORK / "probe.cs"
    probe_exe = WORK / "probe.exe"
    probe_cs.write_text(PROBE_CS, encoding="utf-8")

    compile_cmd = ["mcs", "-nologo", f"-r:{CECIL}", str(ILFMT), str(probe_cs), f"-out:{probe_exe}"]
    r = subprocess.run(compile_cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL: probe compile failed:", r.stderr.strip(), file=sys.stderr)
        return 1

    run = subprocess.run(
        ["mono", str(probe_exe), str(base)] + [c for c, _ in CASES],
        capture_output=True,
        text=True,
        env=dict(os.environ, MONO_PATH=str(CECIL.parent)),
    )
    if run.returncode != 0:
        print("FAIL: escaped fragments:\n" + run.stdout, file=sys.stderr)
        return 1

    rows = {}
    for line in run.stdout.splitlines():
        name, frag, verdict = line.split("\t")
        rows[name] = (frag, verdict)
        if verdict != "OK":
            print(f"FAIL: {name!r} -> {frag!r} escapes {base}", file=sys.stderr)
            return 1
    for name, want in CASES:
        got = rows[name][0]
        if got != want:
            print(f"FAIL: Safe({name!r}) = {got!r}, want {want!r}", file=sys.stderr)
            return 1
    print(
        f"OK: IlFmt.Safe contains all {len(CASES)} hostile fragments below the out dir; dots preserved"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
