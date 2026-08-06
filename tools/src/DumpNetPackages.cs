// Dump every NetPackage* type's wire surface: Setup/read/write/GetLength/
// ProcessPackage/ShouldProcess + the trivial channel/compress/direction getters.
// One <Type>_il.txt per package, plus INDEX.md (per-method IL sizes).
//
//   mono DumpNetPackages.exe <asm> <outDir>
using System;
using System.IO;
using System.Linq;
using System.Text;
using Mono.Cecil;
using Mono.Cecil.Cil;

class DumpNetPackages {
  static readonly string[] Methods = {
    "Setup", "read", "write", "GetLength", "ProcessPackage",
    "get_Channel", "get_Compress", "get_ReliableDelivery", "get_PackageDirection", "ShouldProcess"
  };
  static int IL(TypeDefinition t, string mn) {
    var m = t.Methods.FirstOrDefault(x => x.Name == mn && x.HasBody);
    return m == null ? 0 : m.Body.Instructions.Count;
  }
  static void Dump(StringBuilder sb, TypeDefinition t, string mname) {
    foreach (var m in t.Methods.Where(x => x.Name == mname && x.HasBody)) {
      sb.AppendLine("// " + t.Name + "::" + m.Name + "(" + IlFmt.Sig(m) + ") IL=" + m.Body.Instructions.Count);
      foreach (var i in m.Body.Instructions) sb.AppendLine(IlFmt.Op(i));
      sb.AppendLine();
    }
  }
  static void Main(string[] a) {
    if (a.Length < 2) { Console.Error.WriteLine("usage: DumpNetPackages <asm> <outDir>"); Environment.Exit(2); }
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(Path.GetDirectoryName(Path.GetFullPath(a[0])));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    Directory.CreateDirectory(a[1]);
    var pkgs = asm.MainModule.Types
      .Where(t => t.Name.StartsWith("NetPackage") && t.Name != "NetPackageManager")
      .OrderBy(t => t.Name).ToList();
    var idx = new StringBuilder();
    idx.AppendLine("# NetPackage body dump index");
    idx.AppendLine("// " + pkgs.Count + " NetPackage* types (excl NetPackageManager)");
    idx.AppendLine("| Type | fields | read | write | Setup | GetLength | Process |");
    idx.AppendLine("|---|--:|--:|--:|--:|--:|--:|");
    foreach (var t in pkgs) {
      var sb = new StringBuilder();
      sb.AppendLine("// ==== " + t.Name + " ====");
      sb.AppendLine("// base: " + (t.BaseType == null ? "" : t.BaseType.Name));
      sb.AppendLine("// fields: " + string.Join(", ", t.Fields.Select(f => f.FieldType.Name + " " + f.Name)));
      sb.AppendLine();
      foreach (var mn in Methods) Dump(sb, t, mn);
      File.WriteAllText(Path.Combine(a[1], t.Name + "_il.txt"), sb.ToString());
      idx.AppendLine("| " + t.Name + " | " + t.Fields.Count + " | " + IL(t, "read") + " | " + IL(t, "write") +
        " | " + IL(t, "Setup") + " | " + IL(t, "GetLength") + " | " + IL(t, "ProcessPackage") + " |");
    }
    File.WriteAllText(Path.Combine(a[1], "INDEX.md"), idx.ToString());
    Console.Error.WriteLine("Dumped " + pkgs.Count + " NetPackage types to " + a[1]);
  }
}
