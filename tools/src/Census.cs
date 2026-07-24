// Whole-assembly census: the coverage.md ground-truth numbers, regenerated
// against the live DLL so docs can be re-checked after a game patch.
//
//   mono Census.exe <asm>
using System;
using System.IO;
using System.Linq;
using Mono.Cecil;

class Census {
  static void Main(string[] a) {
    if (a.Length < 1) { Console.Error.WriteLine("usage: Census <asm>"); Environment.Exit(2); }
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(Path.GetDirectoryName(Path.GetFullPath(a[0])));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    var mod = asm.MainModule;
    var top = mod.Types.ToList();
    var all = mod.GetTypes().ToList();
    Console.WriteLine("TopLevelTypes                = " + top.Count);
    Console.WriteLine("MethodsWithBody (top-level)  = " + top.SelectMany(t => t.Methods).Count(m => m.HasBody));
    Console.WriteLine("AllTypes (incl nested)       = " + all.Count);
    Console.WriteLine("AllMethodsWithBody           = " + all.SelectMany(t => t.Methods).Count(m => m.HasBody));
    Console.WriteLine("NetPackage* (top-level)      = " + top.Count(t => t.Name.StartsWith("NetPackage") && t.Name != "NetPackageManager"));
    Console.WriteLine("NetPackage* (incl nested)    = " + all.Count(t => t.Name.StartsWith("NetPackage") && t.Name != "NetPackageManager"));
    foreach (var t in all) {
      foreach (var m in t.Methods.Where(m => m.HasBody)) {
        if (t.Name == "GameManager" && m.Name == "gmUpdate")
          Console.WriteLine("GameManager.gmUpdate IL      = " + m.Body.Instructions.Count);
        if (t.Name == "WorldState" && m.Name == "SaveLoad" && m.Parameters.Count >= 1 && m.Parameters[0].ParameterType.Name.Contains("Stream"))
          Console.WriteLine("WorldState.SaveLoad(Stream)  = " + m.Body.Instructions.Count);
      }
    }
  }
}
