// CmdMap: emit the console-command registry as `primaryName -> TypeName`, by reading
// each ConsoleCmdAbstract subclass's getCommands(). Handles both the common
// `ldstr "name"` form and the static-field form (`ConsoleCmdExportPrefab` holds its
// name in a static `CommandName` field, invisible to an ldstr-only scan).
//   mono CmdMap.exe <asm> [out.tsv]
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Mono.Cecil;
using Mono.Cecil.Cil;

static class CmdMap {
  static bool DerivesFromConsoleCmd(TypeDefinition t) {
    var b = t.BaseType;
    int guard = 0;
    while (b != null && guard++ < 24) {
      if (b.Name == "ConsoleCmdAbstract") return true;
      TypeDefinition r = null; try { r = b.Resolve(); } catch { }
      if (r == null) break;
      b = r.BaseType;
    }
    return false;
  }

  // First string literal reachable from getCommands, following a static-field read
  // into the declaring type's .cctor when the method returns a field rather than a literal.
  static string PrimaryName(TypeDefinition t) {
    var m = t.Methods.FirstOrDefault(x => x.HasBody &&
             (x.Name == "getCommands" || x.Name == "GetCommands"));
    if (m == null) return null;
    foreach (var i in m.Body.Instructions) {
      if (i.OpCode.Code == Code.Ldstr) return (string)i.Operand;
      if (i.OpCode.Code == Code.Ldsfld) {
        var fr = i.Operand as FieldReference; if (fr == null) continue;
        var cctor = t.Methods.FirstOrDefault(x => x.Name == ".cctor" && x.HasBody);
        if (cctor == null) continue;
        foreach (var ci in cctor.Body.Instructions)
          if (ci.OpCode.Code == Code.Ldstr) return (string)ci.Operand;
      }
    }
    return null;
  }

  static void Main(string[] a) {
    if (a.Length < 1) { Console.Error.WriteLine("usage: CmdMap <asm> [out.tsv]"); Environment.Exit(2); }
    var asm = AssemblyDefinition.ReadAssembly(a[0]);
    var sb = new StringBuilder(); sb.AppendLine("command\ttype");
    int n = 0;
    foreach (var t in asm.MainModule.GetTypes().Where(DerivesFromConsoleCmd).OrderBy(x => x.Name)) {
      if (t.IsAbstract) continue;
      var name = PrimaryName(t);
      if (name == null) continue;
      sb.AppendLine(name + "\t" + t.Name); n++;
    }
    if (a.Length > 1) { File.WriteAllText(a[1], sb.ToString()); Console.Error.WriteLine("wrote " + a[1]); }
    else Console.Write(sb.ToString());
    Console.Error.WriteLine("commands mapped: " + n);
  }
}
