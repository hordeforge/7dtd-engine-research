#!/usr/bin/env python3
"""Guard hand-maintained type tables against the DLL (types exist; bases match where the format is uniform).

dedicated-leaves.md (371 rows; heterogeneous section tables, generic names
listed without arity, honest "(not found)" markers) -> type-existence only.
netpackages.md (194 rows; uniform Type|Base table) -> existence + direct base.
A typo, a removed/renamed type, or a base change after a game patch fails here,
even though these inventories are hand-maintained.

Usage: python3 tools/tests/test_inventory_type_existence.py <asm>
"""
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(TOOLS)
INV = os.path.join(REPO, "docs", "inventories")

SRC = r"""
using System;
using System.Linq;
using Mono.Cecil;
class TypeBase {
  static void Main(string[] a) {
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(System.IO.Path.GetDirectoryName(System.IO.Path.GetFullPath(a[0])));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    foreach (var t in asm.MainModule.GetTypes())
      Console.WriteLine(t.Name + "\t" + (t.BaseType == null ? "" : t.BaseType.Name));
  }
}
"""
EXE = "/tmp/typebase_check.exe"


def norm(name: str) -> str:
    """Strip generic arity so `PList`1` matches the doc's `PList`."""
    return re.sub(r"`\d+$", "", name)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: test_inventory_type_existence.py <asm>", file=sys.stderr)
        return 2
    asm = sys.argv[1]
    src = "/tmp/typebase_check.cs"
    with open(src, "w") as f:
        f.write(SRC)
    subprocess.run(
        ["mcs", "-r:%s" % os.path.join(TOOLS, "bin", "Mono.Cecil.dll"), src, "-out:" + EXE],
        check=True,
    )
    env = dict(os.environ)
    env["MONO_PATH"] = os.path.join(TOOLS, "bin")
    out = subprocess.run(
        ["mono", EXE, asm], capture_output=True, text=True, env=env, check=True,
    ).stdout
    dll = {}
    for line in out.splitlines():
        name, _, base = line.partition("\t")
        dll[norm(name)] = base

    bad = []
    total = 0

    # dedicated-leaves.md: type existence (normalized), tolerate "(not found)" rows
    text = open(os.path.join(INV, "dedicated-leaves.md"), encoding="utf-8").read()
    for m in re.finditer(r"^\| `([^`]+)` \|", text, re.M):
        typ = m.group(1)
        total += 1
        row = text.splitlines()[text[: text.index(m.group(0))].count("\n")]
        if "(not found)" in row:
            if norm(typ) in dll:
                bad.append(f"dedicated-leaves.md: `{typ}` now resolves in the DLL (base {dll[norm(typ)]}); update the (not found) marker")
            continue  # documented unresolvable state
        if norm(typ) not in dll:
            bad.append(f"dedicated-leaves.md: type `{typ}` does not exist in the DLL")

    # netpackages.md: type existence + direct base (uniform Type|Base table)
    text = open(os.path.join(INV, "netpackages.md"), encoding="utf-8").read()
    for m in re.finditer(r"^\| `([^`]+)` \| ([^|]+) \|", text, re.M):
        typ, want_base = m.group(1), m.group(2).strip().strip("`")
        total += 1
        if norm(typ) not in dll:
            bad.append(f"netpackages.md: type `{typ}` does not exist in the DLL")
            continue
        if want_base and dll[norm(typ)] != want_base:
            bad.append(f"netpackages.md: `{typ}` base is {dll[norm(typ)]} in DLL, doc says {want_base}")

    if bad:
        for b in bad[:30]:
            print("FAIL:", b)
        if len(bad) > 30:
            print(f"...and {len(bad) - 30} more")
        return 1
    print(f"OK: {total} type rows exist (bases match for netpackages) in the DLL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
