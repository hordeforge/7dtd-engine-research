// Whole-assembly STRUCTURAL census (metadata only, no instruction bodies): the
// committable "100% surface map". Emits, for every type, its namespace/kind/base/
// interfaces/field types/method signatures + IL sizes. Signatures and sizes are
// facts about the API surface, not the copyrighted implementation, so they are
// safe to commit; instruction bodies go to the git-ignored il/ full dump instead.
//
//   mono FullSurface.exe <asm> <outDir>
// Writes:
//   <outDir>/surface-namespaces.md   namespace -> type/method/IL/field counts
//   <outDir>/surface-types.md        one row per type (fullname, kind, base, #f, #m, IL)
using System;
using System.IO;
using System.Linq;
using System.Text;
using Mono.Cecil;

class FullSurface {
  static string Kind(TypeDefinition t) =>
    t.IsInterface ? "interface" : t.IsEnum ? "enum" : t.IsValueType ? "struct" :
    (t.BaseType != null && t.BaseType.Name == "MulticastDelegate") ? "delegate" : "class";

  static void Main(string[] a) {
    if (a.Length < 2) { Console.Error.WriteLine("usage: FullSurface <asm> <outDir>"); Environment.Exit(2); }
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(Path.GetDirectoryName(Path.GetFullPath(a[0])));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    Directory.CreateDirectory(a[1]);
    var all = asm.MainModule.GetTypes().OrderBy(t => t.FullName).ToList();

    // Per-type inventory (one row each).
    var types = new StringBuilder();
    types.AppendLine("# Full type surface (metadata only)");
    types.AppendLine("// " + all.Count + " types (incl nested). Signatures/sizes only; no IL bodies (policy).");
    types.AppendLine("| Type | ns | kind | base | fields | methods | IL |");
    types.AppendLine("|---|---|---|---|--:|--:|--:|");
    foreach (var t in all) {
      int il = t.Methods.Where(m => m.HasBody).Sum(m => m.Body.Instructions.Count);
      types.AppendLine("| " + t.Name + " | " + (t.Namespace == "" ? "-" : t.Namespace) + " | " + Kind(t) +
        " | " + (t.BaseType == null ? "-" : t.BaseType.Name) + " | " + t.Fields.Count + " | " +
        t.Methods.Count(m => m.HasBody) + " | " + il + " |");
    }
    File.WriteAllText(Path.Combine(a[1], "surface-types.md"), types.ToString());

    // Per-namespace summary.
    var ns = new StringBuilder();
    ns.AppendLine("# Namespace surface summary");
    ns.AppendLine("| Namespace | types | methods(body) | IL total | fields |");
    ns.AppendLine("|---|--:|--:|--:|--:|");
    foreach (var g in all.GroupBy(t => t.Namespace == "" ? "<global>" : t.Namespace)
                         .OrderByDescending(g => g.SelectMany(t => t.Methods).Count(m => m.HasBody))) {
      int m = g.SelectMany(t => t.Methods).Count(x => x.HasBody);
      long il = g.SelectMany(t => t.Methods).Where(x => x.HasBody).Sum(x => (long)x.Body.Instructions.Count);
      int f = g.Sum(t => t.Fields.Count);
      ns.AppendLine("| " + g.Key + " | " + g.Count() + " | " + m + " | " + il + " | " + f + " |");
    }
    File.WriteAllText(Path.Combine(a[1], "surface-namespaces.md"), ns.ToString());
    Console.Error.WriteLine("wrote surface-types.md (" + all.Count + " types) + surface-namespaces.md to " + a[1]);
  }
}
