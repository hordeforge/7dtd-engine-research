#!/usr/bin/env python3
"""Guard the leaf-count inventories against the DLL's concrete subclass counts.

Each per-leaf inventory (item-actions 38, sequence-requirements 37, ...)
counts concrete subclasses of a base class, minus the *Data payload classes,
plus any listed abstract base leaves. A game patch that adds/removes a leaf
without updating the inventory fails here.

Usage: python3 tools/tests/test_subclass_counts.py <asm>
"""
import os
import re
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(TOOLS)
INV = os.path.join(REPO, "docs", "inventories")

# base -> (inventory, expected total, exclude-DATA, extra base leaves)
CHECKS = [
    ("BaseRequirement", "sequence-requirements.md", 37, False, []),
    ("ItemAction", "item-actions.md", 38, True, ["ItemActionAttack"]),
]


SRC = r"""
using System;
using System.Linq;
using Mono.Cecil;
class SubCount {
  static void Main(string[] a) {
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(System.IO.Path.GetDirectoryName(System.IO.Path.GetFullPath(a[0])));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    foreach (var b in a[1].Split(',')) {
      bool nodata = b.EndsWith("_nodata");
      string prefix = nodata ? b.Substring(0, b.Length - 7) : b;
      int n = asm.MainModule.GetTypes().Count(t =>
        t.IsClass && !t.IsAbstract && t.BaseType != null && t.BaseType.Name.StartsWith(prefix) &&
        (!nodata || !t.Name.Contains("Data")));
      Console.WriteLine(b + "=" + n);
    }
  }
}
"""
EXE = "/tmp/subcount_check.exe"


def count_rows(inventory: str) -> int:
    n = 0
    for l in open(os.path.join(INV, inventory), encoding="utf-8").read().splitlines():
        s = l.strip()
        if s.startswith("| `") or s.startswith("|`"):
            n += 1
    return n


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: test_subclass_counts.py <asm>", file=sys.stderr)
        return 2
    asm = sys.argv[1]
    with open("/tmp/subcount_check.cs", "w") as f:
        f.write(SRC)
    subprocess.run(["mcs", "-r:%s" % os.path.join(TOOLS, "bin", "Mono.Cecil.dll"), "/tmp/subcount_check.cs", "-out:" + EXE], check=True)
    exe = EXE
    env = dict(os.environ)
    env["MONO_PATH"] = os.path.join(TOOLS, "bin")
    out = subprocess.run(
        ["mono", exe, asm, ",".join(c[0] for c in CHECKS)],
        capture_output=True, text=True, env=env, check=True,
    ).stdout
    counts = {}
    for line in out.splitlines():
        k, _, v = line.partition("=")
        counts[k] = int(v)
    bad = []
    for base, inventory, expected, drop_data, extra in CHECKS:
        concrete = counts[base]
        # drop *Data payload classes: re-derive by excluding names containing
        # "Data" (ItemActionData*/InventoryData* are payloads, not leaves)
        if drop_data:
            env2 = dict(os.environ)
            env2["MONO_PATH"] = os.path.join(TOOLS, "bin")
            out2 = subprocess.run(
                ["mono", exe, asm, base + "_nodata"],
                capture_output=True, text=True, env=env2, check=True,
            ).stdout
            concrete = int(out2.split("=")[-1])
        # concrete + listed base leaves must cover the self-stated count
        if concrete + len(extra) != expected:
            bad.append(
                f"{inventory}: concrete {base}={concrete} + bases {len(extra)} != stated {expected}"
            )
        # and the inventory must self-state the expected number
        text = open(os.path.join(INV, inventory), encoding="utf-8").read()
        if not re.search(rf"\b{expected}\b", text):
            bad.append(f"{inventory}: does not self-state {expected}")
    if bad:
        for b in bad:
            print("FAIL:", b)
        return 1
    print(f"OK: {len(CHECKS)} leaf inventories consistent with the DLL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
