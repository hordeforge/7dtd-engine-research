// LeafInfo: for each type name in <namesFile> (one simple name per line), emit an
// IL-derived fingerprint: simple name, base type, declared-body-method count, and up
// to N behavioral methods (declared, non-ctor, non-accessor), tab-separated. Feeds a
// per-leaf catalog. Transformative metadata only (names + counts, no IL bodies).
//   mono LeafInfo.exe <asm> <namesFile> <out.tsv>
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Mono.Cecil;

static class LeafInfo {
  static bool Accessor(MethodDefinition m) {
    string n = m.Name;
    return m.IsConstructor || m.IsGetter || m.IsSetter || n == "GetHashCode" || n == "Equals" ||
           n == "ToString" || n.StartsWith("get_") || n.StartsWith("set_") || n.StartsWith("op_") ||
           n.StartsWith("add_") || n.StartsWith("remove_") || n.StartsWith("<");
  }

  static void CollectAll(IEnumerable<TypeDefinition> ts, Dictionary<string, TypeDefinition> map) {
    foreach (var t in ts) {
      if (!map.ContainsKey(t.Name)) map[t.Name] = t; // first wins; simple-name keyed
      if (t.HasNestedTypes) CollectAll(t.NestedTypes, map);
    }
  }

  static void Main(string[] a) {
    if (a.Length < 3) { Console.Error.WriteLine("usage: LeafInfo <asm> <namesFile> <out.tsv>"); Environment.Exit(2); }
    var asm = AssemblyDefinition.ReadAssembly(a[0]);
    var map = new Dictionary<string, TypeDefinition>();
    foreach (var mod in asm.Modules) CollectAll(mod.Types, map);

    var sb = new StringBuilder();
    sb.AppendLine("name\tbase\tbodyMethods\tfingerprint");
    foreach (var raw in File.ReadAllLines(a[1])) {
      string name = raw.Trim();
      if (name.Length == 0) continue;
      TypeDefinition t;
      if (!map.TryGetValue(name, out t)) { sb.AppendLine(name + "\t(not found)\t0\t"); continue; }
      string bt = t.BaseType == null ? "" : t.BaseType.Name;
      int bodies = t.Methods.Count(m => m.HasBody);
      var fp = t.Methods.Where(m => m.HasBody && !Accessor(m))
                        .OrderByDescending(m => m.Body.Instructions.Count)
                        .Take(4).Select(m => m.Name).ToList();
      sb.AppendLine(name + "\t" + bt + "\t" + bodies + "\t" + string.Join(", ", fp));
    }
    File.WriteAllText(a[2], sb.ToString());
    Console.WriteLine("wrote " + a[2]);
  }
}
