// RefScan: batch reverse-reference scan. Given a list of type names (one per line),
// reports every site in the assembly that references each type (call/newobj/ldftn,
// field access, or a typed operand), attributed to the OUTERMOST declaring type of
// the referencing method. One assembly load for the whole batch.
//
//   mono RefScan.exe <asm> <typeNamesFile> [out.tsv]
//
// Output columns: target, referencingOuterType, referencingMethod, opcode
// Use it to audit "client-only" / "dead code" claims in bulk: if every referencing
// outer type is UI/render/editor, the claim holds; a GameManager/World/NetPackage
// referrer falsifies it. Complements tools/src/Xref (single-member, exact).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Mono.Cecil;
using Mono.Cecil.Cil;

static class RefScan {
  static TypeDefinition Outermost(TypeDefinition t) {
    while (t.DeclaringType != null) t = t.DeclaringType;
    return t;
  }
  static void Walk(IEnumerable<TypeDefinition> ts, List<TypeDefinition> into) {
    foreach (var t in ts) { into.Add(t); if (t.HasNestedTypes) Walk(t.NestedTypes, into); }
  }
  static string Simple(string n) {
    int i = n.IndexOf('`'); if (i >= 0) n = n.Substring(0, i);
    return n;
  }

  static void Main(string[] a) {
    if (a.Length < 2) { Console.Error.WriteLine("usage: RefScan <asm> <typeNamesFile> [out.tsv]"); Environment.Exit(2); }
    var targets = new HashSet<string>(File.ReadAllLines(a[1]).Select(x => x.Trim()).Where(x => x.Length > 0));
    var asm = AssemblyDefinition.ReadAssembly(a[0]);
    var all = new List<TypeDefinition>();
    foreach (var mod in asm.Modules) Walk(mod.Types, all);

    var sb = new StringBuilder();
    sb.AppendLine("target\treferencingOuterType\treferencingMethod\topcode");
    var counts = new Dictionary<string, int>();
    foreach (var t in targets) counts[t] = 0;

    foreach (var t in all) {
      var owner = Outermost(t);
      string ownerName = owner.FullName;
      foreach (var m in t.Methods) {
        if (!m.HasBody) continue;
        foreach (var ins in m.Body.Instructions) {
          string hit = null;
          var mr = ins.Operand as MethodReference;
          var fr = ins.Operand as FieldReference;
          var tr = ins.Operand as TypeReference;
          if (mr != null) hit = Simple(mr.DeclaringType.Name);
          else if (fr != null) hit = Simple(fr.DeclaringType.Name);
          else if (tr != null) hit = Simple(tr.Name);
          if (hit == null || !targets.Contains(hit)) continue;
          // do not count a type's own internal references
          if (Simple(owner.Name) == hit) continue;
          counts[hit]++;
          sb.AppendLine(hit + "\t" + ownerName + "\t" + t.Name + "::" + m.Name + "\t" + ins.OpCode.Name);
        }
      }
    }

    string outp = a.Length > 2 ? a[2] : null;
    if (outp != null) { File.WriteAllText(outp, sb.ToString()); Console.Error.WriteLine("wrote " + outp); }
    else Console.Write(sb.ToString());
    foreach (var kv in counts.OrderBy(k => k.Value))
      Console.Error.WriteLine(string.Format("{0,-40} external refs: {1}", kv.Key, kv.Value));
  }
}
