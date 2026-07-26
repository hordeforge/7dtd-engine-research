// StateMachines: index every mermaid stateDiagram in the docs tree, with the section
// that owns it and its state count. Emits a navigable catalog so "which lifecycles are
// modelled, and where" is answerable without grepping.
//   mono StateMachines.exe <docsDir> <out.md>
// Docs are the input here (not the assembly): this indexes the corpus, it does not
// re-derive the machines. Each entry's correctness is the owning doc's.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

static class StateMachines {
  class Entry { public string Doc, Section; public int States; public string Cluster; }

  static string ClusterOf(string doc) {
    string d = doc.Replace("inventories/", "");
    if (Regex.IsMatch(d, "^(loop|managers|architecture)")) return "Frame and lifecycle";
    if (Regex.IsMatch(d, "^(protocol|network|chat|platform-auth)")) return "Wire and session";
    if (Regex.IsMatch(d, "^(world|chunk|terrain|save|light|dynamic-mesh|weather)")) return "World, chunks, persistence";
    if (Regex.IsMatch(d, "^(entity|uai|aidirector|spawning|stealth|raycast|combat|buffs)")) return "Entities, AI, combat";
    if (Regex.IsMatch(d, "^(block|item|craft|loot|quest|progression|minevent|game-events|tile-entities|vehicles|npc)")) return "Gameplay systems";
    return "Ops, admin, integrations";
  }

  static void Main(string[] a) {
    if (a.Length < 2) { Console.Error.WriteLine("usage: StateMachines <docsDir> <out.md>"); Environment.Exit(2); }
    var entries = new List<Entry>();
    foreach (var f in Directory.GetFiles(a[0], "*.md", SearchOption.AllDirectories).OrderBy(x => x)) {
      string rel = f.Substring(a[0].Length).TrimStart('/', '\\').Replace('\\', '/');
      if (rel.EndsWith("state-machines.md")) continue;          // never index our own output
      var lines = File.ReadAllLines(f);
      string head = "(top of doc)";
      for (int i = 0; i < lines.Length; i++) {
        var hm = Regex.Match(lines[i], @"^#{2,3}\s+(.*)$");
        if (hm.Success) head = hm.Groups[1].Value.Trim();
        if (!lines[i].Contains("stateDiagram")) continue;
        var states = new HashSet<string>();
        for (int j = i + 1; j < lines.Length && lines[j].Trim() != "```"; j++)
          foreach (Match m in Regex.Matches(lines[j], @"([A-Za-z_][A-Za-z0-9_]*)\s*-->"))
            states.Add(m.Groups[1].Value);
        entries.Add(new Entry { Doc = rel, Section = head, States = states.Count, Cluster = ClusterOf(rel) });
      }
    }

    var sb = new StringBuilder();
    sb.AppendLine("# State machine index (V3.0.1)");
    sb.AppendLine();
    sb.AppendLine("**Kind:** generated catalog of every lifecycle modelled as a mermaid");
    sb.AppendLine("`stateDiagram` in this corpus, grouped by subsystem cluster, with the section");
    sb.AppendLine("that owns it. Use it to answer \"is this lifecycle modelled, and where\".  ");
    sb.AppendLine("**Regenerate:** `mono tools/bin/StateMachines.exe docs docs/inventories/state-machines.md`.  ");
    sb.AppendLine("**Scope note:** this indexes the docs, it does not re-derive the machines from IL.");
    sb.AppendLine("Each diagram's correctness is the owning doc's, and the state counts below are");
    sb.AppendLine("counted from the diagram source (nodes on the left of a transition), so a state");
    sb.AppendLine("that is only ever a target reads one lower.  ");
    sb.AppendLine("**Hub:** [`../INDEX.md`](../INDEX.md). **Visual overview:** [`../architecture-map.md`](../architecture-map.md).");
    sb.AppendLine();
    sb.AppendLine("**" + entries.Count + " state machines** across **" +
                  entries.Select(e => e.Doc).Distinct().Count() + " docs**.");
    sb.AppendLine();
    foreach (var g in entries.GroupBy(e => e.Cluster).OrderBy(g => g.Key)) {
      sb.AppendLine("## " + g.Key + " (" + g.Count() + ")");
      sb.AppendLine();
      sb.AppendLine("| Lifecycle | Doc | States |");
      sb.AppendLine("|---|---|---:|");
      foreach (var e in g.OrderBy(x => x.Doc).ThenBy(x => x.Section))
        sb.AppendLine("| " + e.Section.Replace("|", "\\|") + " | [" + e.Doc + "](../" + e.Doc + ") | " + e.States + " |");
      sb.AppendLine();
    }
    sb.AppendLine("## Changelog");
    sb.AppendLine();
    sb.AppendLine("- **2026-07-26:** Initial generated index of all modelled lifecycles.");
    File.WriteAllText(a[1], sb.ToString());
    Console.Error.WriteLine("indexed " + entries.Count + " state machines");
    Console.WriteLine("wrote " + a[1]);
  }
}
