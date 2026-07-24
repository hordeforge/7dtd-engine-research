// Dump the (de)serialization surface of named types: fields, plus every
// read/write/Read/Write method body. Used for wire payload structs that are
// not NetPackages (EntityCreationData, BlockChangeInfo, ItemValue, ...).
//
//   mono DumpType.exe <asm> <outDir> <TypeName> [TypeName ...]
using System;
using System.IO;
using System.Linq;
using System.Text;
using Mono.Cecil;

class DumpType {
  static readonly string[] Wanted = { "read", "write", "Read", "Write" };
  static void Main(string[] a) {
    if (a.Length < 3) { Console.Error.WriteLine("usage: DumpType <asm> <outDir> <Type> [Type ...]"); Environment.Exit(2); }
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(Path.GetDirectoryName(Path.GetFullPath(a[0])));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    var mod = asm.MainModule;
    Directory.CreateDirectory(a[1]);
    for (int k = 2; k < a.Length; k++) {
      var t = mod.GetTypes().FirstOrDefault(x => x.Name == a[k]);
      if (t == null) { Console.Error.WriteLine(a[k] + " NOT FOUND"); continue; }
      var sb = new StringBuilder();
      sb.AppendLine("// ==== " + t.Name + " (base " + (t.BaseType == null ? "" : t.BaseType.Name) + ") ====");
      sb.AppendLine("// fields: " + string.Join(", ", t.Fields.Select(f => f.FieldType.Name + " " + f.Name)));
      sb.AppendLine();
      foreach (var m in t.Methods.Where(m => m.HasBody && Wanted.Contains(m.Name))) {
        sb.AppendLine("// " + t.Name + "::" + m.Name + "(" + IlFmt.Sig(m) + ") IL=" + m.Body.Instructions.Count);
        foreach (var i in m.Body.Instructions) sb.AppendLine(IlFmt.Op(i));
        sb.AppendLine();
      }
      File.WriteAllText(Path.Combine(a[1], t.Name + "_il.txt"), sb.ToString());
      Console.Error.WriteLine("dumped " + t.Name);
    }
  }
}
