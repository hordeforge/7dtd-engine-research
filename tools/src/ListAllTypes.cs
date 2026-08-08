// One-off: enumerate every type FullName in the assembly, sorted, to a file.
// Not part of the toolchain; used to audit DumpAll completeness.
using System;
using System.IO;
using System.Linq;
using Mono.Cecil;

class ListAllTypes {
  static void Main(string[] a) {
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(Path.GetDirectoryName(Path.GetFullPath(a[0])));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    var names = asm.MainModule.GetTypes()
      .Select(t => t.Namespace + "\t" + t.FullName).OrderBy(x => x).ToList();
    File.WriteAllLines(a[1], names);
    Console.Error.WriteLine("wrote " + names.Count + " type names");
  }
}
