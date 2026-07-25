// Xref: exact cross-reference finder. Reports every site that CALLS a given
// Type::Method or READS/WRITES a given Type::Field, and attributes each site to its
// enclosing method AND its outermost declaring type (so hits inside lambda closures
// and iterator state machines are credited to the real owner, not to '<>c__DisplayClass').
//
//   mono Xref.exe <asm> <Type> <Member> [--field]
//
// Why this exists: the older FindCallers.exe ignored its method argument and only
// substring-matched the type name against callee signatures, so it reported calls
// where the type merely appeared as a parameter or return type, and it was blind to
// field access entirely. Caller-based "client-only vs server" claims need the exact
// form, so use this tool for them.
using System;
using System.Collections.Generic;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

static class Xref {
  static TypeDefinition Outermost(TypeDefinition t) {
    while (t.DeclaringType != null) t = t.DeclaringType;
    return t;
  }

  static void Walk(IEnumerable<TypeDefinition> ts, List<TypeDefinition> into) {
    foreach (var t in ts) { into.Add(t); if (t.HasNestedTypes) Walk(t.NestedTypes, into); }
  }

  static void Main(string[] a) {
    if (a.Length < 3) {
      Console.Error.WriteLine("usage: Xref <asm> <Type> <Member> [--field]");
      Console.Error.WriteLine("  default: find calls to Type::Member");
      Console.Error.WriteLine("  --field: find reads/writes of the field Type::Member");
      Environment.Exit(2);
    }
    string wantType = a[1], wantMember = a[2];
    bool fieldMode = a.Length > 3 && a[3] == "--field";

    var asm = AssemblyDefinition.ReadAssembly(a[0]);
    var all = new List<TypeDefinition>();
    foreach (var mod in asm.Modules) Walk(mod.Types, all);

    int hits = 0;
    foreach (var t in all) {
      foreach (var m in t.Methods) {
        if (!m.HasBody) continue;
        foreach (var ins in m.Body.Instructions) {
          string kind = null;
          string declName = null, memberName = null;

          if (!fieldMode) {
            var mr = ins.Operand as MethodReference;
            if (mr == null) continue;
            var c = ins.OpCode.Code;
            if (c != Code.Call && c != Code.Callvirt && c != Code.Newobj && c != Code.Ldftn && c != Code.Ldvirtftn) continue;
            declName = mr.DeclaringType.Name;
            memberName = mr.Name;
            kind = ins.OpCode.Name;
          } else {
            var fr = ins.Operand as FieldReference;
            if (fr == null) continue;
            var c = ins.OpCode.Code;
            if (c != Code.Ldfld && c != Code.Ldflda && c != Code.Ldsfld && c != Code.Ldsflda &&
                c != Code.Stfld && c != Code.Stsfld) continue;
            declName = fr.DeclaringType.Name;
            memberName = fr.Name;
            kind = ins.OpCode.Name;
          }

          // exact member name; declaring type matched on simple name (handles nesting/generics)
          if (memberName != wantMember) continue;
          string dn = declName; int tick = dn.IndexOf('`');
          if (tick >= 0) dn = dn.Substring(0, tick);
          if (dn != wantType) continue;

          var owner = Outermost(t);
          string site = t.FullName + "::" + m.Name;
          string ownerNote = ReferenceEquals(owner, t) ? "" : "   [owner: " + owner.FullName + "]";
          Console.WriteLine(kind + "  " + site + "  IL_" + ins.Offset.ToString("X4") + ownerNote);
          hits++;
        }
      }
    }
    Console.Error.WriteLine((fieldMode ? "field" : "call") + " sites for " + wantType + "::" + wantMember + " = " + hits);
  }
}
