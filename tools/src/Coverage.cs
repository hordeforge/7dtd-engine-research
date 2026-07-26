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
    // '#'-named types are obfuscated/mangled compiler artifacts (no stable identity).
    return n.Contains("<") || n.Contains("$") || n.StartsWith("__") || n.StartsWith("<") ||
           n.StartsWith("#") || NsOf(t).StartsWith("#");
  }

  // Third-party / BCL namespaces: reachability picks these up (the game calls into
  // them) but they are not game code we reverse-engineer. Coverage is meaningless
  // over them, so they are reported separately and excluded from the game %.
  static readonly string[] LibNs = {
    "System", "UnityEngine", "Unity", "Newtonsoft", "Mono", "InControl", "Microsoft",
    "Google", "Noemax", "SpaceWizards", "Steamworks", "Epic", "TMPro", "Cinemachine",
    "Pathfinding", "UnityStandardAssets", "DG", "Rewired", "FMOD", "MS", "Facepunch",
    "SharpEXR", "ICSharpCode", "SteelSeries", "MemoryPack", "UniLinq",
    "KinematicCharacterController", "Internal",
    // Vendored libraries that ship inside Assembly-CSharp. They are reached (the
    // game calls them) but they are not game code to reverse engineer, exactly like
    // System/UnityEngine above. LiteNetLib is the UDP transport, Antlr/NCalc back the
    // expression parser. Leaving them in silently inflated the "game type" base.
    "LiteNetLib", "Antlr", "NCalc", "Mono", "MS"
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
  // Simple name without the generic-arity backtick suffix (List`1 -> List), which is
  // how a type is written in docs and tokenized from them.
  static string BaseName(TypeDefinition t) {
    string n = t.Name; int i = n.IndexOf('`');
    return i >= 0 ? n.Substring(0, i) : n;
  }

  static void Main(string[] a) {
    if (a.Length < 3) { Console.Error.WriteLine("usage: Coverage <asm> <docsDir> <out.md>"); Environment.Exit(2); }
    var r = new DefaultAssemblyResolver(); r.AddSearchDirectory(Path.GetDirectoryName(a[0]));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    var mod = asm.MainModule; var all = mod.GetTypes().ToList();

    // Devirtualization map for callvirt. Two edge kinds:
    //  (a) class overrides, by walking BaseType chains
    //  (b) INTERFACE implementations. Without (b) whole families that dispatch through
    //      an interface are invisible: the ~187 ConsoleCmdAbstract commands all run via
    //      IConsoleCommand.Execute, and only one of them was reached before this was added.
    foreach (var t in all) foreach (var m in t.Methods.Where(x => x.IsVirtual && x.HasBody)) {
      var bt = t.BaseType;
      while (bt != null) { var btd = bt.Resolve(); if (btd == null) break;
        var bm = btd.Methods.FirstOrDefault(x => x.Name == m.Name && x.Parameters.Count == m.Parameters.Count && x.IsVirtual);
        if (bm != null) { var k = btd.FullName + "::" + m.Name + "/" + m.Parameters.Count; List<MethodDefinition> l;
          if (!overrides.TryGetValue(k, out l)) { l = new List<MethodDefinition>(); overrides[k] = l; } l.Add(m); }
        bt = btd.BaseType; }
    }
    foreach (var t in all) {
      if (!t.HasInterfaces) continue;
      foreach (var ii in t.Interfaces) {
        TypeDefinition itd = null; try { itd = ii.InterfaceType.Resolve(); } catch { }
        if (itd == null) continue;
        foreach (var im in itd.Methods) {
          var impl = t.Methods.FirstOrDefault(x => x.HasBody && x.Name == im.Name && x.Parameters.Count == im.Parameters.Count);
          if (impl == null) continue;
          var k = itd.FullName + "::" + im.Name + "/" + im.Parameters.Count; List<MethodDefinition> l;
          if (!overrides.TryGetValue(k, out l)) { l = new List<MethodDefinition>(); overrides[k] = l; }
          if (!l.Contains(impl)) l.Add(impl);
        }
      }
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

    // Build two mention sets: "narrated" = named in any subsystem doc; "classified" =
    // named only in the out-of-scope classification doc. A type is "accounted for" if
    // it is narrated OR classified. This keeps the narrated % meaningful while letting
    // the accounted-for % reach 100 once the out-of-scope surface is enumerated.
    // Three DISTINCT signals, deliberately not merged:
    //   narrated   = backtick-quoted mention in a hand-written narrative doc (docs/*.md)
    //   catalogued = backtick-quoted mention only in a generated catalog (docs/inventories/)
    //   classified = listed in out-of-scope-surface.md
    // Backticks are required so prose words and markdown table headers ("| Field |",
    // "| Role |", "Entry points") cannot credit real types named Field/Entry/Data.
    var narrated = new HashSet<string>();
    var catalogued = new HashSet<string>();
    var classified = new HashSet<string>();
    foreach (var f in Directory.GetFiles(a[1], "*.md", SearchOption.AllDirectories)) {
      string fn = Path.GetFileName(f);
      if (fn == "coverage-report.md") continue;   // never let the tool read its own output
      bool isInventory = f.Replace('\\','/').Contains("/inventories/");
      var target = (fn == "out-of-scope-surface.md") ? classified : (isInventory ? catalogued : narrated);
      string text = File.ReadAllText(f);
      foreach (Match mt in Regex.Matches(text, "`([A-Za-z_][A-Za-z0-9_]*)`"))
        target.Add(mt.Groups[1].Value);
    }
    catalogued.ExceptWith(narrated);   // narrated wins over merely-catalogued

    // Bucket by namespace (top-level segment; <global> for no namespace).
    var byNs = new Dictionary<string, List<TypeDefinition>>();
    foreach (var t in gameReached) {
      string nsf = NsOf(t); string ns = string.IsNullOrEmpty(nsf) ? "<global>" : nsf.Split('.')[0];
      List<TypeDefinition> l; if (!byNs.TryGetValue(ns, out l)) { l = new List<TypeDefinition>(); byNs[ns] = l; } l.Add(t);
    }

    int docd  = gameReached.Count(t => narrated.Contains(BaseName(t)));
    int catd  = gameReached.Count(t => !narrated.Contains(BaseName(t)) && catalogued.Contains(BaseName(t)));
    int classd = gameReached.Count(t => !narrated.Contains(BaseName(t)) && !catalogued.Contains(BaseName(t)) && classified.Contains(BaseName(t)));
    int accounted = docd + catd + classd;
    int undoc = gameReached.Count - accounted;
    int uiInBase = gameReached.Count(t => BaseName(t).StartsWith("XUiC_") || BaseName(t).StartsWith("XUi"));
    int cmdInBase = gameReached.Count(t => BaseName(t).StartsWith("ConsoleCmd"));

    var sb = new StringBuilder();
    sb.AppendLine("# RE coverage report (V3.0.1, auto-generated)");
    sb.AppendLine();
    sb.AppendLine("**Tool:** `tools/src/Coverage`. **Lens:** call-graph reachability from the");
    sb.AppendLine("dedicated boot + tick drivers (devirtualized `callvirt`), cross-referenced");
    sb.AppendLine("against docs name-mentions. Regenerate:");
    sb.AppendLine("`mono tools/bin/Coverage.exe \"$ASM\" docs docs/inventories/coverage-report.md` (from the repo root, matching the other generated inventories).");
    sb.AppendLine();
    sb.AppendLine("## What this measures, and what it does not");
    sb.AppendLine();
    sb.AppendLine("**This is not a coverage metric.** It is *documentation-mention overlap on a static");
    sb.AppendLine("call graph*, and both sides of the ratio are approximations. Read the caveats before");
    sb.AppendLine("quoting any number here.");
    sb.AppendLine();
    sb.AppendLine("**The base (denominator) is wrong in both directions, by construction:**");
    sb.AppendLine();
    sb.AppendLine("- *Over-approximation:* `callvirt` is devirtualized to every override regardless of");
    sb.AppendLine("  whether the receiver is ever instantiated on a server, so client-only trees get");
    sb.AppendLine("  pulled in. This run has **" + uiInBase + " XUi/XUiC_ client-UI types** inside the base even");
    sb.AppendLine("  though a headless server renders nothing.");
    sb.AppendLine("- *Under-approximation:* code reached only by **reflection** (XML-instantiated");
    sb.AppendLine("  classes) is invisible. Interface dispatch IS devirtualized as of this version");
    sb.AppendLine("  (that fix brought the console-command family in: **" + cmdInBase + " `ConsoleCmd*` types**");
    sb.AppendLine("  are now in the base, against 1 before).");
    sb.AppendLine();
    sb.AppendLine("**The signal (numerator) is a mention, not an explanation.** A type counts as");
    sb.AppendLine("*narrated* only if its name appears **backtick-quoted** in a hand-written narrative");
    sb.AppendLine("doc. Backticks are required so prose and markdown table headers (`| Field |`,");
    sb.AppendLine("`| Role |`, \"Entry points\") cannot credit real types named `Field`/`Entry`/`Data`.");
    sb.AppendLine("Even so, one backticked cross-reference scores the same as a dedicated section.");
    sb.AppendLine();
    sb.AppendLine("The tiers are reported separately and deliberately **not summed into a headline**:");
    sb.AppendLine();
    sb.AppendLine("| Tier | Meaning |");
    sb.AppendLine("|---|---|");
    sb.AppendLine("| **narrated** | backticked in a narrative subsystem doc (the closest thing to real documentation) |");
    sb.AppendLine("| **catalogued only** | backticked only in a generated `inventories/` catalog: enumerated, not explained |");
    sb.AppendLine("| **classified** | listed in [out-of-scope-surface.md](../out-of-scope-surface.md) as not dedicated work |");
    sb.AppendLine("| **unaccounted** | appears nowhere: the honest gap list |");
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
    sb.AppendLine("| ...**narrated** (backticked in a narrative doc) | **" + docd + " (" + (100 * docd / Math.Max(1, gameReached.Count)) + "%)** |");
    sb.AppendLine("| ...**catalogued only** (generated inventory, not narrated) | " + catd + " |");
    sb.AppendLine("| ...**classified** out-of-scope | " + classd + " |");
    sb.AppendLine("| ...**unaccounted** (appears nowhere) | " + undoc + " |");
    sb.AppendLine("| of the base: XUi/XUiC_ client-UI types (over-approximation) | " + uiInBase + " |");
    sb.AppendLine("| of the base: `ConsoleCmd*` (recovered by interface devirt) | " + cmdInBase + " |");
    sb.AppendLine();
    sb.AppendLine("Third-party/BCL and obfuscated `#`-named types are excluded from the base.");
    sb.AppendLine("**Do not add these rows together and present the sum as coverage.** \"Narrated\"");
    sb.AppendLine("and \"classified\" are different epistemic states (reverse engineered vs judged");
    sb.AppendLine("out of scope), and the base itself is the approximation described above.");
    sb.AppendLine();

    sb.AppendLine("## Per-namespace coverage (reached game types)");
    sb.AppendLine();
    sb.AppendLine("| Namespace | reached | narrated+catalogued+classified | remaining | % |");
    sb.AppendLine("|---|---:|---:|---:|---:|");
    foreach (var kv in byNs.OrderByDescending(x => x.Value.Count)) {
      int d = kv.Value.Count(t => narrated.Contains(BaseName(t)) || catalogued.Contains(BaseName(t)) || classified.Contains(BaseName(t)));
      int u = kv.Value.Count - d;
      sb.AppendLine("| `" + kv.Key + "` | " + kv.Value.Count + " | " + d + " | " + u + " | " + (100 * d / kv.Value.Count) + "% |");
    }
    sb.AppendLine();

    sb.AppendLine("## Triage of the unaccounted set (2026-07-26)");
    sb.AppendLine();
    sb.AppendLine("A manual sample of the unaccounted list found it is **dominated by client, editor,");
    sb.AppendLine("and vendored code that happens to live in the `<global>` namespace**, where the");
    sb.AppendLine("namespace-based library filter cannot reach it: `PrefabEditModeManager` (editor),");
    sb.AppendLine("`CursorControllerAbs` (client input), `NCalcLexer` / `BindingNcalcFunctions`");
    sb.AppendLine("(vendored expression parser), `GameSenseManager` (SteelSeries peripherals),");
    sb.AppendLine("`DistantTerrain` (render), `SaveDataMergedPlatformSaveGameIOProvider` (console");
    sb.AppendLine("platform). These need per-type classification, not new reverse engineering.");
    sb.AppendLine();
    sb.AppendLine("So the honest reading of the number below is **not** \"N undocumented server");
    sb.AppendLine("systems\". It is a work queue whose largest bucket is classification debt.");
    sb.AppendLine();
    sb.AppendLine("## Top undocumented reached types (by method count) - the gap list");
    sb.AppendLine();
    sb.AppendLine("These execute on a dedicated server but no doc names them. High method counts =");
    sb.AppendLine("bigger unnarrated surface. (Many may be intentional residuals: support/utility");
    sb.AppendLine("code, client-shared helpers. Cross-check against `residuals.md` before acting.)");
    sb.AppendLine();
    sb.AppendLine("| Type | Namespace | methods (reached-set) |");
    sb.AppendLine("|---|---|---:|");
    foreach (var t in gameReached.Where(t => !narrated.Contains(BaseName(t)) && !catalogued.Contains(BaseName(t)) && !classified.Contains(BaseName(t)))
                                 .OrderByDescending(t => t.Methods.Count(x => x.HasBody)).Take(60)) {
      sb.AppendLine("| `" + t.Name + "` | " + (string.IsNullOrEmpty(t.Namespace) ? "<global>" : t.Namespace) + " | " + t.Methods.Count(x => x.HasBody) + " |");
    }
    sb.AppendLine();

    File.WriteAllText(a[2], sb.ToString());

    // Full undocumented-reached list (sidecar TSV): methods, namespace, type.
    var tsv = new StringBuilder();
    tsv.AppendLine("methods\tnamespace\ttype");
    foreach (var t in gameReached.Where(t => !narrated.Contains(BaseName(t)) && !catalogued.Contains(BaseName(t)) && !classified.Contains(BaseName(t)))
                                 .OrderByDescending(t => t.Methods.Count(x => x.HasBody)))
      tsv.AppendLine(t.Methods.Count(x => x.HasBody) + "\t" + (string.IsNullOrEmpty(NsOf(t)) ? "<global>" : NsOf(t)) + "\t" + t.Name);
    File.WriteAllText(a[2] + ".gaps.tsv", tsv.ToString());

    Console.Error.WriteLine("reached methods=" + visited.Count + " game types=" + gameReached.Count + " narrated=" + docd + " catalogued=" + catd + " classified=" + classd + " unaccounted=" + undoc);
    Console.WriteLine("wrote " + a[2] + " (+ " + a[2] + ".gaps.tsv, " + undoc + " undocumented)");
  }
}
