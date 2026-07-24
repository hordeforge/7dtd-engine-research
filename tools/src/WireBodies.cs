// WireBodies: for every NetPackage* type with a write() body, walk the IL and
// emit an ordered wire-field catalog (source field/getter + wire type), plus a
// control-flow note when the body is not purely linear (loops/conditionals).
// Transformative metadata only (no raw IL beyond the ordered Write sequence).
// Usage: mono bin/WireBodies.exe <asm> <out.md>
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Mono.Cecil;
using Mono.Cecil.Cil;

static class WireBodies {
  static string WireType(MethodReference m) {
    // BinaryWriter.Write(T) overload -> compact wire type name.
    if (m.Parameters.Count == 0) return "?";
    string t = m.Parameters[0].ParameterType.Name;
    switch (t) {
      case "Boolean": return "bool";
      case "Byte": return "u8";
      case "SByte": return "i8";
      case "Int16": return "i16";
      case "UInt16": return "u16";
      case "Int32": return "i32";
      case "UInt32": return "u32";
      case "Int64": return "i64";
      case "UInt64": return "u64";
      case "Single": return "f32";
      case "Double": return "f64";
      case "String": return "string";
      case "Char": return "char";
      case "Byte[]": return "bytes[]";
      default: return t;
    }
  }

  static bool IsWriterWrite(MethodReference m) {
    // BinaryWriter / PooledBinaryWriter primitive Write(T)
    if (m.Name != "Write") return false;
    string dt = m.DeclaringType.Name;
    return dt == "BinaryWriter" || dt == "PooledBinaryWriter" || dt == "BinaryWriterExtensions";
  }

  static bool IsBaseChain(MethodReference m) {
    // super.write(writer): a NetPackage base-class handle emit, not a payload field.
    return (m.Name == "write" || m.Name == "Write") && m.DeclaringType.Name.StartsWith("NetPackage");
  }

  static bool IsNestedWrite(MethodReference m) {
    // Another type's serializer taking a writer (EntityCreationData.write, Bag.Write,
    // ItemStack.Write, PlayerDataFile.WriteNetwork, EntityNetworkStats.write, ...).
    string n = m.Name;
    if (n != "Write" && n != "write" && n != "WriteNetwork" && n != "WriteToStream" &&
        n != "ToStream" && n != "Serialize") return false;
    string dt = m.DeclaringType.Name;
    if (dt == "BinaryWriter" || dt == "PooledBinaryWriter" || dt == "BinaryWriterExtensions") return false;
    foreach (var p in m.Parameters) {
      string pt = p.ParameterType.Name;
      if (pt == "BinaryWriter" || pt == "PooledBinaryWriter" || pt == "Stream") return true;
    }
    return false;
  }

  // Extract the ordered wire fields of one write-method body. Records referenced
  // nested-serializer type names into `nested` for later expansion.
  static List<string> Extract(MethodDefinition m, HashSet<string> nested, out bool loop, out bool cond) {
    var rows = new List<string>();
    string lastSrc = "-";
    bool sawCount = false;
    loop = false; cond = false;
    foreach (var ins in m.Body.Instructions) {
      var code = ins.OpCode.Code;
      if (code == Code.Ldfld || code == Code.Ldflda) {
        var fr = ins.Operand as FieldReference;
        if (fr != null) lastSrc = fr.Name;
      } else if (code == Code.Call || code == Code.Callvirt) {
        var mr = ins.Operand as MethodReference;
        if (mr == null) continue;
        if (IsBaseChain(mr)) { lastSrc = "-"; continue; }
        if (mr.Name.StartsWith("get_Count") || mr.Name.StartsWith("get_Length") || mr.Name == "Count") { sawCount = true; continue; }
        if (mr.Name.StartsWith("get_")) { lastSrc = mr.Name.Substring(4); continue; }
        if (IsWriterWrite(mr)) {
          string note = sawCount ? " (list/array count)" : "";
          rows.Add("| " + (rows.Count + 1) + " | `" + lastSrc + "` | " + WireType(mr) + note + " |");
          lastSrc = "-"; sawCount = false;
        } else if (IsNestedWrite(mr)) {
          rows.Add("| " + (rows.Count + 1) + " | `" + lastSrc + "` | `" + mr.DeclaringType.Name + "." + mr.Name + "` |");
          if (nested != null) nested.Add(mr.DeclaringType.FullName);
          lastSrc = "-"; sawCount = false;
        }
      } else if (code == Code.Br || code == Code.Br_S || code == Code.Brtrue || code == Code.Brtrue_S ||
                 code == Code.Brfalse || code == Code.Brfalse_S || code == Code.Blt || code == Code.Blt_S ||
                 code == Code.Ble || code == Code.Ble_S || code == Code.Bge || code == Code.Bgt) {
        var tgt = ins.Operand as Instruction;
        if (tgt != null && tgt.Offset < ins.Offset) loop = true; else cond = true;
      }
    }
    return rows;
  }

  static void Emit(StringBuilder sb, string title, string mname, MethodDefinition m, HashSet<string> nested) {
    bool loop, cond;
    var rows = Extract(m, nested, out loop, out cond);
    sb.AppendLine("## " + title);
    sb.AppendLine("`" + mname + "` IL=" + m.Body.Instructions.Count + ", " + rows.Count + " wire field(s).");
    if (loop || cond) {
      sb.AppendLine();
      sb.AppendLine("> Control-flow: " + (loop ? "loop(s) present (count-prefixed list/array); " : "") +
                    (cond ? "conditional branch(es) present" : "").TrimEnd() + ". Flat sequence below is the backbone.");
    }
    sb.AppendLine();
    if (rows.Count == 0) sb.AppendLine("_No BinaryWriter/nested Write calls detected (empty body: only the base handle, or fully helper-delegated)._");
    else {
      sb.AppendLine("| # | Source (field/getter) | Wire |");
      sb.AppendLine("|---:|---|---|");
      foreach (var r in rows) sb.AppendLine(r);
    }
    sb.AppendLine();
  }

  static MethodDefinition FindWriter(TypeDefinition t) {
    string[] names = { "write", "Write", "WriteNetwork", "WriteToStream", "ToStream", "Serialize" };
    foreach (var n in names) {
      var m = t.Methods.FirstOrDefault(x => x.Name == n && x.HasBody &&
        x.Parameters.Any(p => p.ParameterType.Name == "BinaryWriter" || p.ParameterType.Name == "PooledBinaryWriter" || p.ParameterType.Name == "Stream"));
      if (m != null) return m;
    }
    return null;
  }

  static void Main(string[] a) {
    if (a.Length < 2) { Console.Error.WriteLine("usage: WireBodies <asm> <out.md>"); Environment.Exit(2); }
    var asm = AssemblyDefinition.ReadAssembly(a[0]);
    var all = new Dictionary<string, TypeDefinition>();
    foreach (var mod in asm.Modules) CollectTypes(mod.Types, all);
    var types = all.Values.Where(t => t.Name.StartsWith("NetPackage") && t.Methods.Any(x => x.Name == "write" && x.HasBody))
                          .OrderBy(t => t.Name).ToList();

    var sb = new StringBuilder();
    sb.AppendLine("# NetPackage wire-body catalog (V3.0.1)");
    sb.AppendLine();
    sb.AppendLine("**Kind:** auto-extracted per-package wire-body reference (ordered `write()` field");
    sb.AppendLine("sequence). Not a hand-narrative; complements the annotated bodies in");
    sb.AppendLine("[`../protocol-packages.md`](../protocol-packages.md) and the census in");
    sb.AppendLine("[`netpackages.md`](netpackages.md).  ");
    sb.AppendLine("**Regenerate:** `mono tools/bin/WireBodies.exe \"$ASM\" docs/inventories/netpackage-bodies.md`.  ");
    sb.AppendLine("**Method:** [`../re-methodology.md`](../re-methodology.md).");
    sb.AppendLine();
    sb.AppendLine("Each row is one `BinaryWriter.Write(T)` or nested `.Write(writer)` in emit order.");
    sb.AppendLine("**Source** is the nearest preceding field/getter (best-effort; inside a loop it");
    sb.AppendLine("shows the element accessor, e.g. `Item`/`Current`). **Wire** is the on-the-wire");
    sb.AppendLine("type. A **control-flow** note flags loops (a `(list/array count)` row is followed");
    sb.AppendLine("by its per-element row(s)) and conditionals; for those, the flat sequence is the");
    sb.AppendLine("backbone and the exact framing is in the per-package narrative where one exists.");
    sb.AppendLine("The leading package handle (`base.write` -> `NetPackage.write`) is not repeated.");
    sb.AppendLine();
    sb.AppendLine("**Extractor limits (honest):** read-side-only fields (rare), values built by");
    sb.AppendLine("arithmetic before a `Write`, and helper-delegated bodies may show `-` as the");
    sb.AppendLine("source; nested `.Write` rows name the serializer type, whose own layout is in its");
    sb.AppendLine("own doc/dump. Verify a load-bearing body against its `write`/`read` IL before");
    sb.AppendLine("cloning.");
    sb.AppendLine();
    sb.AppendLine("Total packages with an extractable `write()` body: **" + types.Count + "**.");
    sb.AppendLine();

    var nested = new HashSet<string>();
    foreach (var t in types) {
      var m = t.Methods.First(x => x.Name == "write" && x.HasBody);
      Emit(sb, t.Name, "write", m, nested);
    }

    // Expand the nested serializers packages delegate to (EntityCreationData,
    // EntityNetworkStats, Bag, ItemStack, ...), transitively, so the catalog is
    // self-contained. Skip NetPackage bases (already covered) and BinaryWriter.
    sb.AppendLine("---");
    sb.AppendLine();
    sb.AppendLine("# Nested serializers referenced by the packages above");
    sb.AppendLine();
    var done = new HashSet<string>();
    var queue = new List<string>(nested.OrderBy(x => x));
    for (int qi = 0; qi < queue.Count && done.Count < 200; qi++) {
      string fn = queue[qi];
      if (done.Contains(fn)) continue;
      done.Add(fn);
      TypeDefinition td;
      if (!all.TryGetValue(fn, out td) || td == null) continue;
      if (td.Name.StartsWith("NetPackage") || td.Name == "BinaryWriter" || td.Name == "PooledBinaryWriter") continue;
      var wm = FindWriter(td);
      if (wm == null) continue;
      var more = new HashSet<string>();
      Emit(sb, td.Name, wm.Name, wm, more);
      foreach (var x in more) if (!done.Contains(x)) queue.Add(x);
    }

    File.WriteAllText(a[1], sb.ToString());
    Console.WriteLine("wrote " + a[1] + " (" + types.Count + " packages, " + done.Count + " nested serializers)");
  }

  static void CollectTypes(IEnumerable<TypeDefinition> ts, Dictionary<string, TypeDefinition> into) {
    foreach (var t in ts) {
      if (!into.ContainsKey(t.FullName)) into[t.FullName] = t;
      if (t.HasNestedTypes) CollectTypes(t.NestedTypes, into);
    }
  }
}
