#!/usr/bin/env python3
"""Guard entityclass-props.md against the EntityClass..cctor.

The doc tables every `ldstr` + `stsfld EntityClass::PropX` pair in the cctor
(167 rows) plus the non-string statics (20) and pins IL=394. A game patch that
adds/renames/removes a prop name constant without updating the doc fails here.

Usage: python3 tools/tests/test_entityclass_props_current.py <asm>
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

REPO = str(_common.REPO)
DOC = os.path.join(REPO, "docs", "inventories", "entityclass-props.md")
EXPECTED_IL = 394
EXPECTED_PAIRS = 167
EXPECTED_TOTAL = 187

SRC = r"""
using System;
using System.Linq;
using System.Collections.Generic;
using Mono.Cecil;
using Mono.Cecil.Cil;
class EcProps {
  static void Main(string[] a) {
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(System.IO.Path.GetDirectoryName(System.IO.Path.GetFullPath(a[0])));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    var t = asm.MainModule.GetTypes().First(x => x.Name == "EntityClass");
    var cctor = t.Methods.First(x => x.Name == ".cctor" && x.HasBody);
    var ins = cctor.Body.Instructions;
    Console.WriteLine("IL=" + ins.Count);
    var pairs = new List<string>();
    for (int i = 0; i < ins.Count - 1; i++) {
      if (ins[i].OpCode.Code == Code.Ldstr && ins[i + 1].OpCode.Code == Code.Stsfld) {
        var fr = ins[i + 1].Operand as FieldReference;
        if (fr != null && fr.DeclaringType.Name == "EntityClass")
          pairs.Add(fr.Name + "=" + ins[i].Operand);
      }
    }
    Console.WriteLine("PAIRS=" + pairs.Count);
    foreach (var p in pairs) Console.WriteLine(p);
  }
}
"""


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: test_entityclass_props_current.py <asm>", file=sys.stderr)
        return 2
    asm = sys.argv[1]
    out = _common.run_probe(_common.compile_probe(SRC, "ecprops_check"), asm)
    lines = out.splitlines()
    il = int(next(ln for ln in lines if ln.startswith("IL=")).split("=")[1])
    npairs = int(next(ln for ln in lines if ln.startswith("PAIRS=")).split("=")[1])
    dll = {ln for ln in lines if "=" in ln and not ln.startswith(("IL=", "PAIRS="))}

    doc = open(DOC, encoding="utf-8").read()
    doc_rows = {
        m.group(1) + "=" + m.group(2)
        for m in re.finditer(r"^\| `(Prop[A-Za-z0-9_]+)` \| `([^`]+)` \|", doc, re.M)
    }
    bad = []
    if il != EXPECTED_IL:
        bad.append(f"cctor IL = {il}, doc pins {EXPECTED_IL}")
    if npairs != EXPECTED_PAIRS:
        bad.append(f"cctor ldstr+stsfld pairs = {npairs}, doc has {EXPECTED_PAIRS}")
    if len(doc_rows) != EXPECTED_PAIRS:
        bad.append(f"doc PropX rows = {len(doc_rows)}, expected {EXPECTED_PAIRS}")
    for p in sorted(dll - doc_rows):
        bad.append(f"missing doc row: `{p}` (regenerate from DumpMethod)")
    for p in sorted(doc_rows - dll):
        bad.append(f"doc row not in cctor: `{p}`")
    if not re.search(rf"\b{EXPECTED_TOTAL}\b", doc):
        bad.append(f"doc does not self-state {EXPECTED_TOTAL}")
    if bad:
        for b in bad[:25]:
            print("FAIL:", b)
        if len(bad) > 25:
            print(f"...and {len(bad) - 25} more")
        return 1
    print(f"OK: {npairs} EntityClass prop pairs + IL={il} pin consistent with the DLL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
