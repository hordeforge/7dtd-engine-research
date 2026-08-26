#!/usr/bin/env python3
"""Guard the console-command inventory against the DLL's command registry.

The inventory (docs/inventories/console-command-list.md) lists one primary row
per concrete ConsoleCmdAbstract subclass, plus short aliases as extra rows
marked "(alias)". The primary names are computed (first ldstr in getCommands,
or the static CommandName-style field value), so the check runs CmdMap.exe -
the same tool the inventory's Regenerate line documents - and compares its
output exactly against the inventory's primary rows. Alias rows must be real
names of the class they name (all ldstrs in getCommands + static-field string
values from the class .cctor). A game patch that adds/removes/renames a
command without updating the inventory fails here.

Usage: python3 tools/tests/test_console_cmd_inventory.py [<asm>] (defaults to ASM env / standard install discovery)
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

REPO = str(_common.REPO)
INV = os.path.join(REPO, "docs", "inventories", "console-command-list.md")
TSV = os.path.join(REPO, "docs", "inventories", "console-command-list.tsv")

# Number of primary commands (one per concrete ConsoleCmdAbstract subclass).
EXPECTED_PRIMARY = 188

SRC = r"""
using System;
using System.Linq;
using System.Collections.Generic;
using Mono.Cecil;
using Mono.Cecil.Cil;
class NameSet {
  static bool Derives(TypeDefinition t) {
    var b = t.BaseType; int g = 0;
    while (b != null && g++ < 24) {
      if (b.Name == "ConsoleCmdAbstract") return true;
      // Base outside the loaded assembly set: Resolve throws, null ends the walk.
      TypeDefinition r = null; try { r = b.Resolve(); } catch (AssemblyResolutionException) { }
      if (r == null) break; b = r.BaseType;
    }
    return false;
  }
  // value assigned to a static field in the class .cctor (ldstr; stsfld field)
  static string FieldValue(TypeDefinition t, string field) {
    var cctor = t.Methods.FirstOrDefault(x => x.Name == ".cctor" && x.HasBody);
    if (cctor == null) return null;
    var ins = cctor.Body.Instructions;
    for (int i = 0; i < ins.Count; i++) {
      if (ins[i].OpCode.Code == Code.Stsfld) {
        var fr = ins[i].Operand as FieldReference;
        if (fr != null && fr.Name == field && i > 0 && ins[i-1].OpCode.Code == Code.Ldstr)
          return (string)ins[i-1].Operand;
      }
    }
    return null;
  }
  static void Main(string[] a) {
    var asm = AssemblyDefinition.ReadAssembly(a[0]);
    foreach (var t in asm.MainModule.GetTypes().Where(Derives)) {
      if (t.IsAbstract) continue;
      var m = t.Methods.FirstOrDefault(x => x.HasBody && (x.Name == "getCommands" || x.Name == "GetCommands"));
      if (m == null) continue;
      var names = new List<string>();
      foreach (var i in m.Body.Instructions) {
        if (i.OpCode.Code == Code.Ldstr) names.Add((string)i.Operand);
        else if (i.OpCode.Code == Code.Ldsfld) {
          var fr = i.Operand as FieldReference; if (fr == null) continue;
          var v = FieldValue(t, fr.Name);
          if (v != null) names.Add(v);
        }
      }
      var seen = new HashSet<string>();
      var uniq = names.Where(x => seen.Add(x)).ToList();
      var dm = t.Methods.FirstOrDefault(x => x.HasBody && x.Name == "getDescription");
      string desc = "";
      if (dm != null) {
        var l = dm.Body.Instructions.FirstOrDefault(i => i.OpCode.Code == Code.Ldstr);
        if (l != null) desc = (string)l.Operand;
      }
      var pm = t.Methods.FirstOrDefault(x => x.HasBody && x.Name == "get_DefaultPermissionLevel");
      string perm = "INHERIT";
      if (pm != null) {
        var ldc = pm.Body.Instructions.FirstOrDefault(i =>
          i.OpCode.Code == Code.Ldc_I4 || i.OpCode.Code == Code.Ldc_I4_S);
        if (ldc != null) perm = ldc.Operand.ToString();
      }
      Console.WriteLine(t.Name + "\t" + string.Join("|", uniq) + "\t" + desc.Replace("\n", "\\n") + "\t" + perm);
    }
  }
}
"""


def parse_inventory(text: str) -> tuple[dict[str, str], list[tuple[str, str]]]:
    primaries: dict[str, str] = {}
    aliases: list[tuple[str, str]] = []
    for ln in text.splitlines():
        s = ln.strip()
        if not (s.startswith("| `") or s.startswith("|`")):
            continue
        parts = s.split("|")
        name = parts[1].strip().strip("`")
        typ = parts[2].strip()
        is_alias = typ.endswith(" (alias)")
        if is_alias:
            typ = typ[: -len(" (alias)")]
        typ = typ.strip("`")
        if is_alias:
            aliases.append((name, typ))
        else:
            primaries[name] = typ
    return primaries, aliases


def main() -> int:
    asm_path, asm_label = _common.resolve_asm(sys.argv[1] if len(sys.argv) > 1 else None)
    if asm_path is None:
        print(f"SKIP: assembly not found: {asm_label}")
        return 0
    asm = str(asm_path)
    rc, cmdmap, cerr = _common.run_tool("CmdMap.exe", asm)
    if rc != 0:
        print(f"FAIL: CmdMap.exe exited {rc}: {cerr[:300]}", file=sys.stderr)
        return 1
    dll_primary = {}
    for line in cmdmap.splitlines()[1:]:  # skip header
        name, _, typ = line.partition("\t")
        dll_primary[name] = typ

    probe = _common.run_probe(_common.compile_probe(SRC, "cmdnames_check"), asm)
    name_sets = {}
    descriptions = {}
    permissions = {}
    for line in probe.splitlines():
        parts = line.split("\t")
        if len(parts) != 4:
            continue
        typ, names, desc, perm = parts[0], parts[1], parts[2].replace("\\n", "\n"), parts[3]
        name_sets[typ] = set(names.split("|")) if names else set()
        descriptions[typ] = desc
        permissions[typ] = perm

    text_inv = open(
        INV, encoding="utf-8"
    ).read()  # read once; parse_inventory + self-state check reuse it
    primaries, aliases = parse_inventory(text_inv)
    bad = []
    # the committed CmdMap tsv (regen.sh artifact) must equal fresh output
    if os.path.exists(TSV) and open(TSV, encoding="utf-8").read() != cmdmap:
        bad.append("docs/inventories/console-command-list.tsv stale vs CmdMap.exe (rerun regen.sh)")
    if len(dll_primary) != EXPECTED_PRIMARY:
        bad.append(f"DLL primary commands = {len(dll_primary)} != expected {EXPECTED_PRIMARY}")
    if len(primaries) != EXPECTED_PRIMARY:
        bad.append(f"inventory primary rows = {len(primaries)} != expected {EXPECTED_PRIMARY}")
    if len(primaries) != len(dll_primary):
        bad.append(
            f"inventory primary rows {len(primaries)} != DLL primary commands {len(dll_primary)}"
        )
    # exact set equality of primary rows (name+type)
    only_inv = {k: v for k, v in primaries.items() if dll_primary.get(k) != v}
    only_dll = {k: v for k, v in dll_primary.items() if primaries.get(k) != v}
    for k, v in sorted(only_inv.items()):
        bad.append(f"inventory-only primary row: `{k}` -> {v}")
    for k, v in sorted(only_dll.items()):
        bad.append(f"missing primary row (DLL has it): `{k}` -> {v}")
    # alias rows must be real names of the class they name
    for name, typ in aliases:
        if typ not in name_sets:
            bad.append(f"alias `{name}` names unknown type {typ}")
        elif name not in name_sets[typ]:
            bad.append(
                f"alias `{name}` is not a registered name of {typ} (have {sorted(name_sets[typ])})"
            )

    # Does-column descriptions must equal getDescription (whitespace-normalized:
    # the doc renders embedded newlines as spaces; empty getDescription becomes
    # "(no description)")
    def norm_ws(s: str) -> str:
        return re.sub(r"\s+", " ", s).strip()

    for m in re.finditer(
        r"^\| `([^`]+)` \| `([^`]+)`(?: \(alias\))? \| ([^|]*) \| (.*?) \|$", text_inv, re.M
    ):
        name, typ, perm_col, does = m.group(1), m.group(2), m.group(3).strip(), m.group(4).strip()
        if typ not in descriptions:
            continue
        want = "" if does in ("(no description)", "") else does
        have = descriptions[typ].replace("\\n", "\n")
        if norm_ws(have) != norm_ws(want):
            bad.append(f"`{name}` description: doc `{want[:50]}` != getDescription `{have[:50]}`")
        # Perm column: blank = inherits the base default (no override);
        # a number = the class's get_DefaultPermissionLevel ldc
        want_perm = perm_col
        have_perm = "" if permissions.get(typ) == "INHERIT" else permissions.get(typ, "")
        if have_perm != want_perm:
            bad.append(f"`{name}` perm: doc `{want_perm}` != DLL `{have_perm or '(inherited)'}`")
    # the inventory must self-state the primary count
    if not re.search(rf"\b{EXPECTED_PRIMARY}\b", text_inv):
        bad.append(f"inventory does not self-state {EXPECTED_PRIMARY}")
    if bad:
        for b in bad:
            print("FAIL:", b)
        return 1
    print(
        f"OK: {len(dll_primary)} primary commands + {len(aliases)} aliases, descriptions consistent with the DLL"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
