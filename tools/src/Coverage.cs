// Coverage: programmatic RE-coverage report. Runs call-graph reachability from the
// dedicated boot+tick drivers (same seeds as Reach), then cross-references the
// reached game types against which are name-mentioned in the docs tree. Emits a
// markdown report: reachability totals, per-namespace documented/undocumented split,
// and the top undocumented reached types (the actionable gaps).
//   mono Coverage.exe <asm> <docsDir> <out.md>
// The "documented" signal is a name mention in any docs/*.md (an upper bound: a type
// named in passing counts). Treat undocumented-reached as the honest gap list.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using Mono.Cecil;
using Mono.Cecil.Cil;

class Coverage {
  static Dictionary<string, List<MethodDefinition>> overrides = new Dictionary<string, List<MethodDefinition>>();

  static bool Generated(TypeDefinition t) {
    string n = t.Name;
    return n.Contains("<") || n.Contains("$") || n.StartsWith("__") || n.StartsWith("<");
  }

  // Third-party / BCL namespaces: reachability picks these up (the game calls into
  // them) but they are not game code we reverse-engineer. Coverage is meaningless
  // over them, so they are reported separately and excluded from the game %.
  static readonly string[] LibNs = {
    "System", "UnityEngine", "Unity", "Newtonsoft", "Mono", "InControl", "Microsoft",
    "Google", "Noemax", "SpaceWizards", "Steamworks", "Epic", "TMPro", "Cinemachine",
    "Pathfinding", "UnityStandardAssets", "DG", "Rewired", "FMOD", "MS", "Facepunch",
    "SharpEXR", "ICSharpCode", "SteelSeries", "MemoryPack", "UniLinq",
    "KinematicCharacterController", "Internal"
  };
  // Namespace of the outermost declaring type (nested types report an empty own ns).
  static string NsOf(TypeDefinition t) {
    var cur = t;
    while (cur.DeclaringType != null) cur = cur.DeclaringType;
    return cur.Namespace;
  }
  static bool IsLibrary(TypeDefinition t) {
    string ns = NsOf(t);
    if (string.IsNullOrEmpty(ns)) return false; // <global> is game code
    string top = ns.Split('.')[0];
    foreach (var p in LibNs) if (top == p) return true;
    return false;
  }

  static void Main(string[] a) {
    if (a.Length < 3) { Console.Error.WriteLine("usage: Coverage <asm> <docsDir> <out.md>"); Environment.Exit(2); }
    var r = new DefaultAssemblyResolver(); r.AddSearchDirectory(Path.GetDirectoryName(a[0]));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    var mod = asm.MainModule; var all = mod.GetTypes().ToList();

    // override map for callvirt devirtualization
    foreach (var t in all) foreach (var m in t.Methods.Where(x => x.IsVirtual && x.HasBody)) {
      var bt = t.BaseType;
      while (bt != null) { var btd = bt.Resolve(); if (btd == null) break;
        var bm = btd.Methods.FirstOrDefault(x => x.Name == m.Name && x.Parameters.Count == m.Parameters.Count && x.IsVirtual);
        if (bm != null) { var k = btd.FullName + "::" + m.Name + "/" + m.Parameters.Count; List<MethodDefinition> l;
          if (!overrides.TryGetValue(k, out l)) { l = new List<MethodDefinition>(); overrides[k] = l; } l.Add(m); }
        bt = btd.BaseType; }
    }

    var visited = new HashSet<MethodDefinition>(); var work = new Queue<MethodDefinition>();
    var gm = all.First(t => t.Name == "GameManager");
    string[] seeds = { "StartGame", "startGameCo", "StartAsServer", "gmUpdate", "UpdateTick", "SaveAndCleanupWorld", "PlayerLoginRPC", "PlayerSpawnedInWorld", "ChatMessageServer" };
    foreach (var s in seeds) foreach (var m in gm.Methods.Where(x => x.Name == s && x.HasBody)) if (visited.Add(m)) work.Enqueue(m);
    string[][] extra = { new[]{"ConnectionManager","Update"}, new[]{"DynamicMeshManager","Update"}, new[]{"World","TickEntities"}, new[]{"World","TickEntity"}, new[]{"World","OnUpdateTick"}, new[]{"EntityAlive","OnUpdateEntity"}, new[]{"EntityAlive","updateTasks"} };
    foreach (var e in extra) foreach (var m in all.Where(t => t.Name == e[0]).SelectMany(t => t.Methods).Where(x => x.Name == e[1] && x.HasBody)) if (visited.Add(m)) work.Enqueue(m);

    while (work.Count > 0) { var m = work.Dequeue();
      foreach (var i in m.Body.Instructions) {
        var mr = i.Operand as MethodReference; if (mr == null) continue;
        MethodDefinition md = null; try { md = mr.Resolve(); } catch { }
        if (md != null && md.HasBody && visited.Add(md)) work.Enqueue(md);
        if (i.OpCode.Code == Code.Callvirt) { var k = mr.DeclaringType.FullName + "::" + mr.Name + "/" + mr.Parameters.Count;
          List<MethodDefinition> ovs; if (overrides.TryGetValue(k, out ovs)) foreach (var ov in ovs) if (visited.Add(ov)) work.Enqueue(ov); }
      }
    }

    var reached = new HashSet<TypeDefinition>(visited.Select(m => m.DeclaringType));
    var nonGen = reached.Where(t => !Generated(t)).ToList();
    var libReached = nonGen.Where(IsLibrary).ToList();
    var gameReached = nonGen.Where(t => !IsLibrary(t)).ToList();

    // Build the doc-mention set: every whole-word token that looks like a type name
    // appearing in any docs/*.md. A reached type is "documented" if its simple name
    // appears as a whole word anywhere in the docs tree.
    var mentioned = new HashSet<string>();
    foreach (var f in Directory.GetFiles(a[1], "*.md", SearchOption.AllDirectories)) {
      string text = File.ReadAllText(f);
      foreach (Match mt in Regex.Matches(text, "[A-Za-z_][A-Za-z0-9_]+")) mentioned.Add(mt.Value);
    }

    // Bucket by namespace (top-level segment; <global> for no namespace).
    var byNs = new Dictionary<string, List<TypeDefinition>>();
    foreach (var t in gameReached) {
      string nsf = NsOf(t); string ns = string.IsNullOrEmpty(nsf) ? "<global>" : nsf.Split('.')[0];
      List<TypeDefinition> l; if (!byNs.TryGetValue(ns, out l)) { l = new List<TypeDefinition>(); byNs[ns] = l; } l.Add(t);
    }

    int docd = gameReached.Count(t => mentioned.Contains(t.Name));
    int undoc = gameReached.Count - docd;

    var sb = new StringBuilder();
    sb.AppendLine("# RE coverage report (V3.0.1, auto-generated)");
    sb.AppendLine();
    sb.AppendLine("**Tool:** `tools/src/Coverage`. **Lens:** call-graph reachability from the");
    sb.AppendLine("dedicated boot + tick drivers (devirtualized `callvirt`), cross-referenced");
    sb.AppendLine("against docs name-mentions. Regenerate:");
    sb.AppendLine("`mono bin/Coverage.exe \"$ASM\" ../docs coverage-report.md`.");
    sb.AppendLine();
    sb.AppendLine("**\"Documented\" = the type's simple name appears as a whole word in any");
    sb.AppendLine("`docs/*.md`.** This is an *upper bound* on narrative coverage (a type named in");
    sb.AppendLine("passing counts as documented), so treat the undocumented-reached list as the");
    sb.AppendLine("honest floor of what still needs attention. Reachability is the ground truth for");
    sb.AppendLine("\"executes on a dedicated server\".");
    sb.AppendLine();
    sb.AppendLine("## Totals");
    sb.AppendLine();
    sb.AppendLine("| Metric | Value |");
    sb.AppendLine("|---|---:|");
    sb.AppendLine("| Reached methods (with body) | " + visited.Count + " |");
    sb.AppendLine("| Reached types (incl. compiler-generated) | " + reached.Count + " |");
    sb.AppendLine("| Reached, non-generated | " + nonGen.Count + " |");
    sb.AppendLine("| ...third-party / BCL (System, Unity, Newtonsoft, ...) | " + libReached.Count + " (excluded from %) |");
    sb.AppendLine("| ...**game types** (the RE surface) | **" + gameReached.Count + "** |");
    sb.AppendLine("| ...game types name-mentioned in docs | **" + docd + " (" + (100 * docd / Math.Max(1, gameReached.Count)) + "%)** |");
    sb.AppendLine("| ...game types not mentioned (gap floor) | " + undoc + " |");
    sb.AppendLine();
    sb.AppendLine("The **game-type documented %** is the headline coverage number. Third-party/BCL");
    sb.AppendLine("code the game calls into is reached but out of scope (never reverse-engineered).");
    sb.AppendLine();

    sb.AppendLine("## Per-namespace coverage (reached game types)");
    sb.AppendLine();
    sb.AppendLine("| Namespace | reached | documented | undocumented | % |");
    sb.AppendLine("|---|---:|---:|---:|---:|");
    foreach (var kv in byNs.OrderByDescending(x => x.Value.Count)) {
      int d = kv.Value.Count(t => mentioned.Contains(t.Name));
      int u = kv.Value.Count - d;
      sb.AppendLine("| `" + kv.Key + "` | " + kv.Value.Count + " | " + d + " | " + u + " | " + (100 * d / kv.Value.Count) + "% |");
    }
    sb.AppendLine();

    sb.AppendLine("## Top undocumented reached types (by method count) - the gap list");
    sb.AppendLine();
    sb.AppendLine("These execute on a dedicated server but no doc names them. High method counts =");
    sb.AppendLine("bigger unnarrated surface. (Many may be intentional residuals: support/utility");
    sb.AppendLine("code, client-shared helpers. Cross-check against `residuals.md` before acting.)");
    sb.AppendLine();
    sb.AppendLine("| Type | Namespace | methods (reached-set) |");
    sb.AppendLine("|---|---|---:|");
    foreach (var t in gameReached.Where(t => !mentioned.Contains(t.Name))
                                 .OrderByDescending(t => t.Methods.Count(x => x.HasBody)).Take(60)) {
      sb.AppendLine("| `" + t.Name + "` | " + (string.IsNullOrEmpty(t.Namespace) ? "<global>" : t.Namespace) + " | " + t.Methods.Count(x => x.HasBody) + " |");
    }
    sb.AppendLine();

    File.WriteAllText(a[2], sb.ToString());
    Console.Error.WriteLine("reached methods=" + visited.Count + " game types=" + gameReached.Count + " documented=" + docd + " (" + (100 * docd / Math.Max(1, gameReached.Count)) + "%)");
    Console.WriteLine("wrote " + a[2]);
  }
}
