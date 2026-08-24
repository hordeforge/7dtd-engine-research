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
using System.IO;
using Mono.Cecil;
using Mono.Cecil.Cil;

static class Xref {
  // The member one candidate site instruction references: the called method for
  // call-family opcodes, or the accessed field for field opcodes. kind stays
  // null when the instruction is not a site in the requested mode.
  static void SiteTarget(Instruction ins, bool fieldMode, out string kind,
      out string declName, out string memberName) {
    kind = null; declName = null; memberName = null;
    if (!fieldMode) {
      var mr = ins.Operand as MethodReference;
      if (mr == null) return;
      var c = ins.OpCode.Code;
      if (c != Code.Call && c != Code.Callvirt && c != Code.Newobj && c != Code.Ldftn && c != Code.Ldvirtftn) return;
      declName = mr.DeclaringType.Name;
      memberName = mr.Name;
    } else {
      var fr = ins.Operand as FieldReference;
      if (fr == null) return;
      var c = ins.OpCode.Code;
      if (c != Code.Ldfld && c != Code.Ldflda && c != Code.Ldsfld && c != Code.Ldsflda &&
          c != Code.Stfld && c != Code.Stsfld) return;
      declName = fr.DeclaringType.Name;
      memberName = fr.Name;
    }
    kind = ins.OpCode.Name;
  }

  // Batch mode: count call sites for every requested Type::Member pair in ONE
  // assembly pass. Matching is identical to single-target mode (exact member
  // name; declaring type on simple name with the generic-arity suffix stripped;
  // call/callvirt/newobj/ldftn/ldvirtftn opcodes, via SiteTarget). test_xref_claims.py drives
  // this so N doc claims cost one assembly load, not N.
  static void RunBatch(string asmPath, string claimsPath) {
    var order = new List<string>();
    var counts = new Dictionary<string, int>();
    foreach (var raw in File.ReadAllLines(claimsPath)) {
      var line = raw.Trim();
      if (line.Length == 0 || line.StartsWith("#")) continue;
      var parts = line.Split('\t');
      if (parts.Length != 2 || parts[0].Length == 0 || parts[1].Length == 0) {
        Console.Error.WriteLine("bad claim line (want '<Type><TAB><Member>'): " + raw);
        Environment.Exit(2);
      }
      string key = parts[0] + "::" + parts[1];
      if (!counts.ContainsKey(key)) { counts[key] = 0; order.Add(key); }
    }

    var asm = AssemblyDefinition.ReadAssembly(asmPath);
    var all = AsmWalk.AllTypes(asm);

    // Member-name prefilter (same order as single-target mode): a site can only
    // count when its callee NAME is claimed, so test that before building any
    // "Type::Member" key. Keying every operand of ~1.7M instructions dominated
    // batch mode otherwise.
    var claimedNames = new HashSet<string>();
    foreach (var k in counts.Keys) {
      int sep = k.IndexOf("::");
      if (sep > 0) claimedNames.Add(k.Substring(sep + 2));
    }

    foreach (var t in all) {
      foreach (var m in t.Methods) {
        if (!m.HasBody) continue;
        foreach (var ins in m.Body.Instructions) {
          SiteTarget(ins, false, out string kind, out string declName, out string memberName);
          if (kind == null || !claimedNames.Contains(memberName)) continue;
          string key = AsmWalk.SimpleName(declName) + "::" + memberName;
          if (counts.ContainsKey(key)) counts[key]++;
        }
      }
    }
    foreach (var k in order) Console.WriteLine(k + " = " + counts[k]);
  }

  static void Main(string[] a) {
    if (a.Length >= 3 && a[1] == "--batch") { RunBatch(a[0], a[2]); return; }
    if (a.Length < 3) {
      Console.Error.WriteLine("usage: Xref <asm> <Type> <Member> [--field]");
      Console.Error.WriteLine("       Xref <asm> --batch <claims.tsv>   (one '<Type><TAB><Member>' pair per line)");
      Console.Error.WriteLine("  default: find calls to Type::Member");
      Console.Error.WriteLine("  --field: find reads/writes of the field Type::Member");
      Console.Error.WriteLine("  --batch: one assembly pass for every claim; prints '<Type>::<Member> = <count>' per input line");
      Environment.Exit(2);
    }
    string wantType = a[1], wantMember = a[2];
    bool fieldMode = a.Length > 3 && a[3] == "--field";

    var asm = AssemblyDefinition.ReadAssembly(a[0]);
    var all = AsmWalk.AllTypes(asm);

    int hits = 0;
    foreach (var t in all) {
      foreach (var m in t.Methods) {
        if (!m.HasBody) continue;
        foreach (var ins in m.Body.Instructions) {
          SiteTarget(ins, fieldMode, out string kind, out string declName, out string memberName);
          if (kind == null) continue;

          // exact member name; declaring type matched on simple name (handles nesting/generics)
          if (memberName != wantMember) continue;
          if (AsmWalk.SimpleName(declName) != wantType) continue;

          var owner = AsmWalk.Outermost(t);
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
