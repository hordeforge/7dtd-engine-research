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
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
    foreach (var t in asm.MainModule.GetTypes()) {
      var bodies = t.Methods.Where(m => m.HasBody).ToList();
      int maxIl = bodies.Count == 0 ? 0 : bodies.Max(m => m.Body.Instructions.Count);
      Console.WriteLine(t.Name + "\t" + (t.BaseType == null ? "" : t.BaseType.Name)
        + "\t" + bodies.Count + "\t" + maxIl + "\t" + (t.FullName.Contains("/") ? "N" : "T"));
    }
  }
}
"""


def norm(name: str) -> str:
    """Strip generic arity so `PList`1` matches the doc's `PList`."""
    return re.sub(r"`\d+$", "", name)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: test_inventory_type_existence.py <asm>", file=sys.stderr)
        return 2
    asm = sys.argv[1]
    out = _common.run_probe(_common.compile_probe(SRC, "typebase_check"), asm)
    dll = {}
    top_level_netpkg = set()
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 5:
            continue
        name, base, nb, mx, lvl = parts[0], parts[1], int(parts[2]), int(parts[3]), parts[4]
        dll[norm(name)] = (base, nb, mx)
        if lvl == "T" and name.startswith("NetPackage") and name != "NetPackageManager":
            top_level_netpkg.add(norm(name))

    bad = []
    total = 0

    # dedicated-leaves.md: type existence (normalized), tolerate "(not found)" rows
    text = open(os.path.join(INV, "dedicated-leaves.md"), encoding="utf-8").read()
    for row in text.splitlines():
        m = re.match(r"^\| `([^`]+)` \|", row)
        if not m:
            continue
        typ = m.group(1)
        total += 1
        if "(not found)" in row:
            if norm(typ) in dll:
                bad.append(
                    f"dedicated-leaves.md: `{typ}` now resolves in the DLL (base {dll[norm(typ)]}); update the (not found) marker"
                )
            continue  # documented unresolvable state
        if norm(typ) not in dll:
            bad.append(f"dedicated-leaves.md: type `{typ}` does not exist in the DLL")

    # netpackages.md: type existence + direct base + method count + max method
    # IL + completeness (the table must list every top-level NetPackage* type,
    # excluding NetPackageManager; nested types like DroneWeapons/
    # NetPackageDroneParticleEffect live in dedicated-leaves.md instead)
    text = open(os.path.join(INV, "netpackages.md"), encoding="utf-8").read()
    doc_np_rows = {
        norm(m.group(1)) for m in re.finditer(r"^\| `(NetPackage[A-Za-z0-9]*)` \|", text, re.M)
    }
    for missing in sorted(top_level_netpkg - doc_np_rows):
        bad.append(f"netpackages.md: top-level `{missing}` missing from the table")
    for m in re.finditer(r"^\| `([^`]+)` \| ([^|]+) \| (\d+) \| (\d+) \|", text, re.M):
        typ, want_base, want_n, want_max = (
            m.group(1),
            m.group(2).strip().strip("`"),
            int(m.group(3)),
            int(m.group(4)),
        )
        total += 1
        info = dll.get(norm(typ))
        if info is None:
            bad.append(f"netpackages.md: type `{typ}` does not exist in the DLL")
            continue
        base, nb, mx = info
        if want_base and base != want_base:
            bad.append(f"netpackages.md: `{typ}` base is {base} in DLL, doc says {want_base}")
        if nb != want_n:
            bad.append(f"netpackages.md: `{typ}` has {nb} method bodies in DLL, doc says {want_n}")
        if mx != want_max:
            bad.append(f"netpackages.md: `{typ}` max method IL is {mx} in DLL, doc says {want_max}")

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
