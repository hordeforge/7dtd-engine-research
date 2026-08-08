// Dump EVERY method body of EVERY type to per-type IL files: the full local
// reversal of the whole assembly (~1.7M instructions). Output goes to a local
// directory that MUST stay git-ignored (game IL; never redistribute). Use this to
// reverse 100% of the code on your own machine; commit only structural metadata
// (FullSurface) and human narrative, never this output.
//
//   mono DumpAll.exe <asm> <outDir> [namespaceFilter]
// One file per type: <outDir>/<Namespace>/<Type>.il.txt
using System;
using System.IO;
using System.Linq;
using System.Text;
using Mono.Cecil;

class DumpAll {
  static string Safe(string s) => string.Concat(s.Select(c => char.IsLetterOrDigit(c) || c == '_' || c == '.' ? c : '_'));
  static void Main(string[] a) {
    if (a.Length < 2) { Console.Error.WriteLine("usage: DumpAll <asm> <outDir> [nsFilter]"); Environment.Exit(2); }
    string nsFilter = a.Length >= 3 ? a[2] : null;
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(Path.GetDirectoryName(Path.GetFullPath(a[0])));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    var all = asm.MainModule.GetTypes()
      .Where(t => nsFilter == null || (t.Namespace ?? "").StartsWith(nsFilter)).ToList();
    int nt = 0, nm = 0;
    foreach (var t in all) {
      var sb = new StringBuilder();
      sb.AppendLine("// ==== " + t.FullName + " ====");
      sb.AppendLine("// kind base=" + (t.BaseType == null ? "-" : t.BaseType.FullName) +
        " interfaces=" + string.Join(",", t.Interfaces.Select(i => i.InterfaceType.Name)));
      sb.AppendLine("// fields: " + string.Join(", ", t.Fields.Select(f => f.FieldType.Name + " " + f.Name)));
      sb.AppendLine();
      foreach (var m in t.Methods.Where(m => m.HasBody)) {
        sb.AppendLine("// " + t.Name + "::" + m.Name + "(" + IlFmt.Sig(m) + ") IL=" + m.Body.Instructions.Count);
        foreach (var i in m.Body.Instructions) sb.AppendLine(IlFmt.Op(i));
        sb.AppendLine();
        nm++;
      }
      // Scope the file by the full declaring chain and place it under the
      // OUTERMOST declaring type's namespace. Cecil reports an empty Namespace
      // for nested types even when the owning type is namespaced, so two
      // different namespaced parents (e.g. Platform.EOS.User and
      // Platform.MultiPlatform.User) used to collide in _global on a single
      // declaring-name scope and clobber each other's files; the whole chain
      // plus the real namespace keeps one file per type (observed: 7432 -> 6675
      // before the fix).
      string scope = "";
      var root = t;
      for (var p = t.DeclaringType; p != null; p = p.DeclaringType) { scope = Safe(p.Name) + "_" + scope; root = p; }
      string ns = root.Namespace;
      string dir = Path.Combine(a[1], Safe(ns == "" ? "_global" : ns));
      Directory.CreateDirectory(dir);
      File.WriteAllText(Path.Combine(dir, scope + Safe(t.Name) + ".il.txt"), sb.ToString());
      nt++;
    }
    Console.Error.WriteLine("dumped " + nt + " types / " + nm + " method bodies to " + a[1]);
  }
}
