// Protocol-wide metadata census. For every NetPackage*, resolve the constant
// returned by the trivial getters (channel, compress, direction, delivery,
// allowed-before-auth). Emits META.md (full table) and a stdout summary of the
// non-default rows (channel != 0, compress == 1, before-auth == 1).
//
//   mono NetProtocolCensus.exe <asm> <outFile>
using System;
using System.IO;
using System.Linq;
using System.Text;
using Mono.Cecil;
using Mono.Cecil.Cil;

class NetProtocolCensus {
  // Returns the int a trivial `ldc.i4.X; ret` getter yields; null if missing,
  // -999 if the getter is non-trivial (computed).
  static int? ConstOf(TypeDefinition t, string name) {
    var m = t.Methods.FirstOrDefault(x => x.Name == name && x.HasBody);
    if (m == null) return null;
    var ins = m.Body.Instructions.Where(i => i.OpCode != OpCodes.Nop && i.OpCode != OpCodes.Ret).ToList();
    if (ins.Count != 1) return -999;
    var ii = ins[0]; var c = ii.OpCode.Code;
    switch (c) {
      case Code.Ldc_I4_0: return 0; case Code.Ldc_I4_1: return 1; case Code.Ldc_I4_2: return 2;
      case Code.Ldc_I4_3: return 3; case Code.Ldc_I4_4: return 4; case Code.Ldc_I4_5: return 5;
      case Code.Ldc_I4_6: return 6; case Code.Ldc_I4_7: return 7; case Code.Ldc_I4_8: return 8;
      case Code.Ldc_I4_M1: return -1;
      case Code.Ldc_I4_S: return (sbyte)ii.Operand;
      case Code.Ldc_I4: return (int)ii.Operand;
      default: return -999;
    }
  }
  static string S(int? v) => v == null ? "inherit" : v == -999 ? "expr" : v.ToString();
  static void Main(string[] a) {
    if (a.Length < 2) { Console.Error.WriteLine("usage: NetProtocolCensus <asm> <outFile>"); Environment.Exit(2); }
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(Path.GetDirectoryName(Path.GetFullPath(a[0])));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    var pkgs = asm.MainModule.Types
      .Where(t => t.Name.StartsWith("NetPackage") && t.Name != "NetPackageManager")
      .OrderBy(t => t.Name).ToList();
    var sb = new StringBuilder();
    sb.AppendLine("# NetPackage protocol metadata census");
    sb.AppendLine("// channel/compress/direction/delivery/before-auth from trivial getters; `expr` = computed at runtime.");
    sb.AppendLine("| Package | Chan | Compress | Dir | Delivery | BeforeAuth |");
    sb.AppendLine("|---|--:|--:|--:|--:|--:|");
    foreach (var t in pkgs)
      sb.AppendLine("| " + t.Name + " | " + S(ConstOf(t, "get_Channel")) + " | " + S(ConstOf(t, "get_Compress")) +
        " | " + S(ConstOf(t, "get_PackageDirection")) + " | " + S(ConstOf(t, "get_ReliableDelivery")) +
        " | " + S(ConstOf(t, "get_AllowedBeforeAuth")) + " |");
    File.WriteAllText(a[1], sb.ToString());
    Console.WriteLine("channel != 0 (non-default band):");
    foreach (var t in pkgs) { var c = ConstOf(t, "get_Channel"); if (c != null && c != 0 && c != -999) Console.WriteLine("  chan " + c + "  " + t.Name); }
    Console.WriteLine("compress == 1:");
    foreach (var t in pkgs) if (ConstOf(t, "get_Compress") == 1) Console.WriteLine("  " + t.Name);
    Console.WriteLine("AllowedBeforeAuth == 1:");
    foreach (var t in pkgs) if (ConstOf(t, "get_AllowedBeforeAuth") == 1) Console.WriteLine("  " + t.Name);
  }
}
