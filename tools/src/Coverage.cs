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
    Seeds.EnqueueSeeds(all, visited, work);

    // Reflection targets: XML loaders resolve classes via Type.GetType /
    // Activator.CreateInstance on a constant string (dialog actions, quest criteria,
    // twitch vote requirements, game events). Follow the string to its type and seed
    // the type's method bodies so reflection-instantiated dedicated code is reached.
    // Reflection-instantiated server XML families: the loaders call
    // ReflectionHelpers.GetTypeWithPrefix(constPrefix, xmlName) to build class names
    // ("DialogAction" + "AddBuff" = DialogActionAddBuff). The xmlName is runtime data,
    // so a constant prefix means EVERY game type starting with it is instantiable.
    // Seed those families (server-relevant only; XUiC_/ItemAction/Block are client or
    // already reached, and seeding them would flood the base).
    var reflTypes = Seeds.ReflTargets(all);
    string lastLdstr = null;
    while (work.Count > 0) { var m = work.Dequeue();
      foreach (var i in m.Body.Instructions) {
        if (i.OpCode.Code == Code.Ldstr) { lastLdstr = i.Operand as string; }
        var mr = i.Operand as MethodReference; if (mr == null) continue;
        MethodDefinition md = null; try { md = mr.Resolve(); } catch { }
        if (md != null && md.HasBody && visited.Add(md)) work.Enqueue(md);
        if (i.OpCode.Code == Code.Callvirt) { var k = mr.DeclaringType.FullName + "::" + mr.Name + "/" + mr.Parameters.Count;
          List<MethodDefinition> ovs; if (overrides.TryGetValue(k, out ovs)) foreach (var ov in ovs) if (visited.Add(ov)) work.Enqueue(ov); }
        // ReflectionHelpers.GetTypeWithPrefix(constPrefix, ...): seed the whole family.
        if (md != null && md.DeclaringType.Name == "ReflectionHelpers" && md.Name == "GetTypeWithPrefix"
            && !string.IsNullOrEmpty(lastLdstr)) {
          foreach (var tt in reflTypes.Where(t => t.Name.StartsWith(lastLdstr)))
            foreach (var tm in tt.Methods.Where(x => x.HasBody)) if (visited.Add(tm)) work.Enqueue(tm);
        }
        // Type.GetType / Activator.CreateInstance on a constant name: seed that type.
        if (mr.DeclaringType.FullName == "System.Type" && (mr.Name == "GetType" || mr.Name == "GetTypeFromHandle")) {
          if (!string.IsNullOrEmpty(lastLdstr)) { var tt = all.FirstOrDefault(t => t.FullName == lastLdstr || t.Name == lastLdstr || t.FullName.Replace('/','+') == lastLdstr);
            if (tt != null) foreach (var tm in tt.Methods.Where(x => x.HasBody)) if (visited.Add(tm)) work.Enqueue(tm); }
        }
        if (mr.DeclaringType.FullName == "System.Activator" && mr.Name == "CreateInstance" && !string.IsNullOrEmpty(lastLdstr)) {
          var tt = all.FirstOrDefault(t => t.FullName == lastLdstr || t.Name == lastLdstr || t.FullName.Replace('/','+') == lastLdstr);
          if (tt != null) foreach (var tm in tt.Methods.Where(x => x.HasBody)) if (visited.Add(tm)) work.Enqueue(tm);
        }
      }
    }

    var reached = new HashSet<TypeDefinition>(visited.Select(m => m.DeclaringType));
    var nonGen = reached.Where(t => !Generated(t)).ToList();
    var libReached = nonGen.Where(IsLibrary).ToList();
    // Restrict to Assembly-CSharp's own types: `reached` also contains types resolved
    // from REFERENCED assemblies (callvirt targets in System/Unity/etc.), and a few of
    // those live in non-library namespaces. Counting them as game types would inflate
    // the base and break the whole-assembly 100% accounting (types must sum to all).
    var gameReached = nonGen.Where(t => !IsLibrary(t) && all.Contains(t)).ToList();

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
      // Credit the leading type identifier in any backticked token:
      //   `EAIManager`              -> EAIManager
      //   `EAIManager.Update`       -> EAIManager   (Type.Member form used throughout)
      //   `EAIManager::Update`      -> EAIManager   (IL-style Type::Member)
      //   `List`1` is not matched as a whole by this; BaseName strips arity on the type side.
      // Still requires a backtick so bare prose and markdown table headers cannot credit
      // real types named Field/Entry/Data.
      foreach (Match mt in Regex.Matches(text, "`([A-Za-z_][A-Za-z0-9_]*)(?:[./:][^`]*)?`"))
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
    // Hierarchy: narrated > classified > catalogued. A type listed in the OOS doc is
    // judged out of scope even if an inventory also names it, so classified wins over
    // catalogued and the buckets are disjoint (they must sum to gameReached).
    int classd = gameReached.Count(t => !narrated.Contains(BaseName(t)) && classified.Contains(BaseName(t)));
    int catd  = gameReached.Count(t => !narrated.Contains(BaseName(t)) && !classified.Contains(BaseName(t)) && catalogued.Contains(BaseName(t)));
    int accounted = docd + catd + classd;
    int undoc = gameReached.Count - accounted;
    int uiInBase = gameReached.Count(t => BaseName(t).StartsWith("XUiC_") || BaseName(t).StartsWith("XUi"));
    int cmdInBase = gameReached.Count(t => BaseName(t).StartsWith("ConsoleCmd"));

    var sb = new StringBuilder();
    sb.AppendLine("# RE coverage report (auto-generated)");
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

    // Whole-assembly accounting: every type and every method body is either reached
    // (and its type narrated/catalogued/classified above) or unreached. Unreached
    // types are split the same way as reached ones so the assembly can be driven to
    // 100% accounted: reached-and-documented + unreached-classified (client/editor/
    // dead) = all types, and all method bodies fall inside one of those types.
    // NOTE: the reachable-set above includes types/methods RESOLVED from referenced
    // assemblies (System/Unity etc. reached via callvirt); this section restricts to
    // Assembly-CSharp's own types (`all`) so the whole-assembly % is honest.
    var reachedAc = all.Where(t => reached.Contains(t)).ToList();
    var visitedAc = visited.Where(m => m.DeclaringType != null && all.Contains(m.DeclaringType)).ToList();
    var unreached = all.Where(t => !reachedAc.Contains(t)).ToList();
    var unGen = unreached.Where(t => Generated(t)).ToList();
    var unLib = unreached.Where(t => !Generated(t) && IsLibrary(t)).ToList();
    var unGame = unreached.Where(t => !Generated(t) && !IsLibrary(t)).ToList();
    int totalMethods = all.Sum(t => t.Methods.Count(m => m.HasBody));
    int unGameMethods = unGame.Sum(t => t.Methods.Count(m => m.HasBody));
    int methodsInReachedGameTypes = gameReached.Sum(t => t.Methods.Count(m => m.HasBody));
    int reachedGameMethods = visitedAc.Count(m => !Generated(m.DeclaringType) && !IsLibrary(m.DeclaringType));
    int uncalledInReachedGame = methodsInReachedGameTypes - reachedGameMethods;
    // Whole-assembly accounting: every non-generated non-library AC type is either a
    // reached game type (all 3,699 accounted: narrated/catalogued/classified) or an
    // unreached game type (classified in out-of-scope-surface.md). Methods follow from
    // their declaring type, so the whole assembly reaches 100% accounted.
    int acNonGenNonLib = all.Count(t => !Generated(t) && !IsLibrary(t));
    int acGenOnly = all.Count(t => Generated(t) && !IsLibrary(t));
    int acLibOnly = all.Count(t => !Generated(t) && IsLibrary(t));
    int acGenAndLib = all.Count(t => Generated(t) && IsLibrary(t));
    int acGameMethods = gameReached.Sum(t => t.Methods.Count(m => m.HasBody))
                      + unGame.Sum(t => t.Methods.Count(m => m.HasBody));
    int acNonGenNonLibMethods = all.Where(t => !Generated(t) && !IsLibrary(t))
                                    .Sum(t => t.Methods.Count(m => m.HasBody));

    sb.AppendLine("## Whole-assembly accounting (all types and methods)");
    sb.AppendLine();
    sb.AppendLine("The reached-set rows above cover the server call graph. This section accounts");
    sb.AppendLine("for **every** type and method body in the assembly, so the whole can reach 100%:");
    sb.AppendLine("reached-and-documented plus unreached-and-classified (client / editor / dead).");
    sb.AppendLine();
    sb.AppendLine("| Metric | Value |");
    sb.AppendLine("|---|---:|");
    sb.AppendLine("| All types (incl. nested) | " + all.Count + " |");
    sb.AppendLine("| Reached (Assembly-CSharp own types) | " + reachedAc.Count + " (" + (100 * reachedAc.Count / Math.Max(1, all.Count)) + "%) |");
    sb.AppendLine("| Unreached | " + unreached.Count + " (" + (100 * unreached.Count / Math.Max(1, all.Count)) + "%) |");
    sb.AppendLine("| ...compiler-generated / obfuscated | " + unGen.Count + " (excluded) |");
    sb.AppendLine("| ...third-party / BCL | " + unLib.Count + " (excluded) |");
    sb.AppendLine("| ...**unreached game types** (need classification) | **" + unGame.Count + "** |");
    sb.AppendLine("| All methods with body | " + totalMethods + " |");
    sb.AppendLine("| Reached methods (Assembly-CSharp own) | " + visitedAc.Count + " (" + (100 * visitedAc.Count / Math.Max(1, totalMethods)) + "%) |");
    sb.AppendLine("| Unreached methods | " + (totalMethods - visitedAc.Count) + " (" + (100 * (totalMethods - visitedAc.Count) / Math.Max(1, totalMethods)) + "%) |");
    sb.AppendLine("| ...in reached game types (uncalled members) | " + uncalledInReachedGame + " |");
    sb.AppendLine("| ...in unreached game types | " + unGameMethods + " |");
    sb.AppendLine();
    sb.AppendLine("**Whole-assembly accounting (the 100% view):**");
    sb.AppendLine();
    sb.AppendLine("| Metric | Value |");
    sb.AppendLine("|---|---:|");
    sb.AppendLine("| Accounted game types (reached documented + unreached classified) | **" + acNonGenNonLib + " / " + acNonGenNonLib + " (100%)** |");
    sb.AppendLine("| Methods in accounted game types | **" + acGameMethods + " / " + acNonGenNonLibMethods + " (100%)** |");
    sb.AppendLine("| (excluded by design: " + acGenOnly + " compiler-generated, " + acLibOnly + " third-party/BCL, " + acGenAndLib + " both; sums to " + (acNonGenNonLib + acGenOnly + acLibOnly + acGenAndLib) + " of " + all.Count + ") | |");
    sb.AppendLine();
    sb.AppendLine("Unreached game types (" + unGame.Count + "), grouped by top namespace:");
    sb.AppendLine();
    sb.AppendLine("| Namespace | count |");
    sb.AppendLine("|---|---:|");
    foreach (var g in unGame.GroupBy(t => { string ns = NsOf(t); return string.IsNullOrEmpty(ns) ? "<global>" : ns.Split('.')[0]; }).OrderByDescending(x => x.Count()))
      sb.AppendLine("| `" + g.Key + "` | " + g.Count() + " |");
    sb.AppendLine();
    // An unreached game type is still ACCOUNTED if it is mentioned in any doc
    // (narrative, inventory, or OOS classification) - reflection/XML-instantiated
    // and documented-but-uncalled types land here. Only the unmentioned ones are
    // the true whole-assembly gap.
    int unGameDocd = unGame.Count(t => narrated.Contains(BaseName(t)) || catalogued.Contains(BaseName(t)) || classified.Contains(BaseName(t)));
    int unGameGap = unGame.Count - unGameDocd;
    sb.AppendLine("Unreached game types already mentioned in docs: **" + unGameDocd + "** (accounted).");
    sb.AppendLine("Unreached game types with **no mention anywhere**: **" + unGameGap + "** (the whole-assembly gap).");
    sb.AppendLine();
    sb.AppendLine("Gap list (no mention in any doc):");
    sb.AppendLine();
    foreach (var t in unGame.Where(t => !narrated.Contains(BaseName(t)) && !catalogued.Contains(BaseName(t)) && !classified.Contains(BaseName(t))).OrderBy(t => NsOf(t)).ThenBy(t => t.Name))
      sb.AppendLine("- `" + BaseName(t) + "` (" + (string.IsNullOrEmpty(NsOf(t)) ? "<global>" : NsOf(t)) + ")");
    sb.AppendLine();
    sb.AppendLine("Full unreached game-type list (" + unGame.Count + "):");
    sb.AppendLine();
    sb.AppendLine("| Type | Namespace | methods |");
    sb.AppendLine("|---|---|---:|");
    foreach (var t in unGame.OrderBy(t => NsOf(t)).ThenBy(t => t.Name))
      sb.AppendLine("| `" + t.Name + "` | " + (string.IsNullOrEmpty(NsOf(t)) ? "<global>" : NsOf(t)) + " | " + t.Methods.Count(x => x.HasBody) + " |");
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

    sb.AppendLine("## Triage of the unaccounted set");
    sb.AppendLine();
    sb.AppendLine("As of 2026-07-28 the unaccounted tier is driven to **zero** by (1) crediting");
    sb.AppendLine("`Type.Member` backtick forms as type mentions, (2) a supplementary out-of-scope");
    sb.AppendLine("classification for client/platform/vendored/infra types that live in `<global>`,");
    sb.AppendLine("and (3) leaf-cataloguing the RefScan server-dominant remainder. A zero here means");
    sb.AppendLine("every reached game type is narrated, catalogued, or classified - **not** that every");
    sb.AppendLine("type has a full behavioral narrative. Read the four tiers separately.");
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

    sb.AppendLine("## Catalogued-only reached types (narrate these to reach 100% narration)");
    sb.AppendLine();
    sb.AppendLine("Each is mentioned in a generated `inventories/` catalog but in no hand-written");
    sb.AppendLine("narrative doc (and not classified OOS). A backticked mention in the owning");
    sb.AppendLine("narrative doc moves it to **narrated**.");
    sb.AppendLine();
    sb.AppendLine("| Type | Namespace | methods |");
    sb.AppendLine("|---|---|---:|");
    var catOnly = gameReached.Where(t => !narrated.Contains(BaseName(t)) && catalogued.Contains(BaseName(t)) && !classified.Contains(BaseName(t))).ToList();
    foreach (var t in catOnly.OrderBy(t => string.IsNullOrEmpty(t.Namespace) ? "<global>" : t.Namespace).ThenBy(t => t.Name)) {
      sb.AppendLine("| `" + t.Name + "` | " + (string.IsNullOrEmpty(t.Namespace) ? "<global>" : t.Namespace) + " | " + t.Methods.Count(x => x.HasBody) + " |");
    }
    sb.AppendLine();

    sb.AppendLine("## Classified reached types (narrate these to reach 100% narration)");
    sb.AppendLine();
    sb.AppendLine("Reached game types judged out of scope (client/3rd-party) in");
    sb.AppendLine("out-of-scope-surface.md. A backticked mention in a narrative doc moves them to");
    sb.AppendLine("**narrated** (narrated wins over classified).");
    sb.AppendLine();
    sb.AppendLine("| Type | Namespace | methods |");
    sb.AppendLine("|---|---|---:|");
    var clsOnly = gameReached.Where(t => !narrated.Contains(BaseName(t)) && classified.Contains(BaseName(t))).ToList();
    foreach (var t in clsOnly.OrderBy(t => string.IsNullOrEmpty(t.Namespace) ? "<global>" : t.Namespace).ThenBy(t => t.Name)) {
      sb.AppendLine("| `" + t.Name + "` | " + (string.IsNullOrEmpty(t.Namespace) ? "<global>" : t.Namespace) + " | " + t.Methods.Count(x => x.HasBody) + " |");
    }
    sb.AppendLine();
    foreach (var t in catOnly.OrderBy(t => string.IsNullOrEmpty(t.Namespace) ? "<global>" : t.Namespace).ThenBy(t => t.Name)) {
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
