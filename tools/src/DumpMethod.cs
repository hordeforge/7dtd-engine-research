// General workhorse: dump IL for every method whose Type::Name and method name
// match the given filters (substring, case-insensitive). Walks nested types.
//
//   mono DumpMethod.exe <Assembly-CSharp.dll> <typeFilter> <methodFilter> [outFile]
//
// Examples:
//   mono DumpMethod.exe "$ASM" GameManager gmUpdate
//   mono DumpMethod.exe "$ASM" NetPackageChunk read chunk-read.txt
// Empty methodFilter ("") dumps all methods of the matched types.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Mono.Cecil;

class DumpMethod {
  static void Main(string[] a) {
    if (a.Length < 3) { Console.Error.WriteLine("usage: DumpMethod <asm> <typeFilter> <methodFilter> [outFile]"); Environment.Exit(2); }
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(Path.GetDirectoryName(Path.GetFullPath(a[0])));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    string tf = a[1], mf = a[2];
    var all = new List<TypeDefinition>();
    AsmWalk.Collect(asm.MainModule.Types, all);

    var sb = new StringBuilder();
    int hits = 0;
    foreach (var t in all.Where(t => t.Name.IndexOf(tf, StringComparison.OrdinalIgnoreCase) >= 0)) {
      foreach (var m in t.Methods.Where(m => m.HasBody &&
               (mf.Length == 0 || m.Name.IndexOf(mf, StringComparison.OrdinalIgnoreCase) >= 0))) {
        sb.AppendLine("// " + t.FullName + "::" + m.Name + "(" + IlFmt.Sig(m) + ") IL=" + m.Body.Instructions.Count);
        foreach (var i in m.Body.Instructions) sb.AppendLine(IlFmt.Op(i));
        sb.AppendLine();
        hits++;
      }
    }
    if (a.Length >= 4) { File.WriteAllText(a[3], sb.ToString()); Console.Error.WriteLine("wrote " + hits + " method(s) to " + a[3]); }
    else Console.Write(sb.ToString());
  }
}
