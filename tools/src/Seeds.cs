// Shared reachability-seed definitions for Reach.exe and Coverage.exe.
// Both tools must agree on what the "dedicated server call graph" starts from, or the
// two coverage lenses drift. Keep the seed DATA and the enqueue logic here and use
// Seeds.* from both tools; a test asserts the two tools' reached-method counts match.
using System;
using System.Collections.Generic;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

static class Seeds {
  // GameManager boot + tick drivers (the dedicated entry points).
  public static readonly string[] GameManagerSeeds = {
    "StartGame", "startGameCo", "StartAsServer", "gmUpdate", "UpdateTick",
    "SaveAndCleanupWorld", "PlayerLoginRPC", "PlayerSpawnedInWorld", "ChatMessageServer",
  };

  // Peer Updates / entity tick that run on the dedicated loop outside GameManager.
  public static readonly string[][] Extra = {
    new[]{"ConnectionManager","Update"}, new[]{"DynamicMeshManager","Update"},
    new[]{"World","TickEntities"}, new[]{"World","TickEntity"}, new[]{"World","OnUpdateTick"},
    new[]{"EntityAlive","OnUpdateEntity"}, new[]{"EntityAlive","updateTasks"},
    // Dedicated HTTP API: GameManager.Awake -> Webserver.WebServer.Init registers the
    // GameStartDone/WorldShuttingDown ModEvent handlers; the IsServer-gated
    // GameStartDone creates Webserver.Web (the REST host). Both are verifiably
    // dedicated-server code, so they are seeded directly (a blanket GameManager.Awake
    // seed would flood the base with client UI).
    new[]{"WebServer","Init"}, new[]{"WebServer","GameStartDone"},
    new[]{"WebServer","WorldShuttingDown"},
  };

  // Reflection-instantiated server XML families: the loaders call
  // ReflectionHelpers.GetTypeWithPrefix(constPrefix, xmlName) to build class names
  // ("DialogAction" + "AddBuff" = DialogActionAddBuff). The xmlName is runtime data,
  // so a constant prefix means EVERY game type starting with it is instantiable.
  // Server-relevant only; XUiC_/ItemAction/Block are client or already reached, and
  // seeding them would flood the base.
  public static readonly string[] ReflPrefixes = {
    "QuestAction", "Requirement", "Objective", "ObjectiveModifier",
    "Reward", "QuestCriteria", "LootEntryRequirement", "DialogAction", "DialogRequirement",
  };

  // Enqueue the static seeds (GameManager methods + extra (type,method) pairs).
  public static void EnqueueSeeds(List<TypeDefinition> all,
      HashSet<MethodDefinition> visited, Queue<MethodDefinition> work) {
    var gm = all.First(t => t.Name == "GameManager");
    foreach (var s in GameManagerSeeds)
      foreach (var m in gm.Methods.Where(x => x.Name == s && x.HasBody))
        if (visited.Add(m)) work.Enqueue(m);
    foreach (var e in Extra)
      foreach (var m in all.Where(t => t.Name == e[0]).SelectMany(t => t.Methods)
                           .Where(x => x.Name == e[1] && x.HasBody))
        if (visited.Add(m)) work.Enqueue(m);
  }

  // The reflection-instantiable types (all AC types matching a server XML prefix).
  public static List<TypeDefinition> ReflTargets(List<TypeDefinition> all) {
    return all.Where(t => ReflPrefixes.Any(p => t.Name.StartsWith(p))).ToList();
  }

  // Constant-string -> type lookup for the Type.GetType / Activator.CreateInstance
  // reflection seeds. Built once per run: the BFS hits those call sites for every
  // visited method body, and rescanning `all` per hit (with FullName formatting plus
  // a Replace allocation for every type on every scan) dominated tool runtime.
  // Accepts exactly the three forms the linear scan matched before: FullName, simple
  // Name, and the nested '+' form of FullName. First match in `all` order wins: each
  // key maps to the earliest type that produces it under any accepted form, which is
  // what FirstOrDefault returned.
  static Dictionary<string, TypeDefinition> byConstantName;

  public static void IndexTypes(List<TypeDefinition> all) {
    var idx = new Dictionary<string, TypeDefinition>(all.Count * 3);
    foreach (var t in all) {
      AddKey(idx, t.FullName, t);
      AddKey(idx, t.Name, t);
      AddKey(idx, t.FullName.Replace('/', '+'), t);
    }
    byConstantName = idx;
  }

  static void AddKey(Dictionary<string, TypeDefinition> idx, string k, TypeDefinition t) {
    if (!idx.ContainsKey(k)) idx[k] = t;
  }

  // Resolve a ldstr constant to its type (null when no type matches the string).
  public static TypeDefinition FindByConstantName(string constant) {
    if (string.IsNullOrEmpty(constant) || byConstantName == null) return null;
    TypeDefinition t;
    return byConstantName.TryGetValue(constant, out t) ? t : null;
  }

  // --- Shared call graph -------------------------------------------------------
  // Reach.exe and Coverage.exe must walk the SAME graph or their "reached methods"
  // counts drift (test_reach_consistency.py fails). The devirtualization map and the
  // BFS below therefore live here, next to the seeds, not in either tool.

  // Devirtualization map for callvirt. Two edge kinds:
  //  (a) class overrides, by walking BaseType chains
  //  (b) INTERFACE implementations. Without (b) whole families that dispatch through
  //      an interface are invisible: the ~187 ConsoleCmdAbstract commands all run via
  //      IConsoleCommand.Execute, and only one of them was reached before this was added.
  public static Dictionary<string, List<MethodDefinition>> BuildOverrideMap(List<TypeDefinition> all) {
    var overrides = new Dictionary<string, List<MethodDefinition>>();
    foreach (var t in all) foreach (var m in t.Methods.Where(x => x.IsVirtual && x.HasBody)) {
      var bt = t.BaseType;
      while (bt != null) { var btd = bt.Resolve(); if (btd == null) break;
        var bm = btd.Methods.FirstOrDefault(x => x.Name == m.Name && x.Parameters.Count == m.Parameters.Count && x.IsVirtual);
        if (bm != null) AddEdge(overrides, btd.FullName + "::" + m.Name + "/" + m.Parameters.Count, m);
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
          AddEdge(overrides, itd.FullName + "::" + im.Name + "/" + im.Parameters.Count, impl);
        }
      }
    }
    return overrides;
  }

  static void AddEdge(Dictionary<string, List<MethodDefinition>> map, string k, MethodDefinition m) {
    List<MethodDefinition> l; if (!map.TryGetValue(k, out l)) { l = new List<MethodDefinition>(); map[k] = l; }
    if (!l.Contains(m)) l.Add(m);
  }

  // The reachability BFS: call/callvirt/newobj edges, callvirt devirtualized through
  // `overrides`, plus reflection-following on constant strings:
  //   - ReflectionHelpers.GetTypeWithPrefix(constPrefix, ...): seed every type whose
  //     name starts with the constant prefix (the xmlName half is runtime data).
  //   - Type.GetType / Activator.CreateInstance on a constant name: seed that type.
  public static void WalkCallGraph(List<TypeDefinition> all, HashSet<MethodDefinition> visited,
      Queue<MethodDefinition> work, Dictionary<string, List<MethodDefinition>> overrides,
      List<TypeDefinition> reflTargets) {
    IndexTypes(all);
    // Resolve memo: the BFS revisits each MethodReference operand once per
    // referencing instruction (~304k visits over ~82k distinct instances on
    // V3.1.0), and Resolve() re-walks metadata every call. Resolving each
    // instance once (including null-on-error results) cut the walk from
    // ~1.6s to ~0.7s; nothing mutates during the walk, so caching is safe.
    var resolved = new Dictionary<MethodReference, MethodDefinition>();
    string lastLdstr = null;
    while (work.Count > 0) { var m = work.Dequeue();
      foreach (var i in m.Body.Instructions) {
        if (i.OpCode.Code == Code.Ldstr) { lastLdstr = i.Operand as string; }
        var mr = i.Operand as MethodReference; if (mr == null) continue;
        MethodDefinition md;
        if (!resolved.TryGetValue(mr, out md)) {
          md = mr as MethodDefinition;
          if (md == null) { try { md = mr.Resolve(); } catch { } }
          resolved[mr] = md;
        }
        if (md != null && md.HasBody && visited.Add(md)) work.Enqueue(md);
        if (i.OpCode.Code == Code.Callvirt) { var k = mr.DeclaringType.FullName + "::" + mr.Name + "/" + mr.Parameters.Count;
          List<MethodDefinition> ovs; if (overrides.TryGetValue(k, out ovs)) foreach (var ov in ovs) if (visited.Add(ov)) work.Enqueue(ov); }
        if (!string.IsNullOrEmpty(lastLdstr)) {
          if (md != null && md.DeclaringType.Name == "ReflectionHelpers" && md.Name == "GetTypeWithPrefix") {
            foreach (var tt in reflTargets.Where(t => t.Name.StartsWith(lastLdstr)))
              foreach (var tm in tt.Methods.Where(x => x.HasBody)) if (visited.Add(tm)) work.Enqueue(tm);
          }
          if (mr.DeclaringType.FullName == "System.Type" &&
              (mr.Name == "GetType" || mr.Name == "GetTypeFromHandle"))
            SeedByConstantName(lastLdstr, visited, work);
          if (mr.DeclaringType.FullName == "System.Activator" && mr.Name == "CreateInstance")
            SeedByConstantName(lastLdstr, visited, work);
        }
      }
    }
  }

  static void SeedByConstantName(string constant, HashSet<MethodDefinition> visited,
      Queue<MethodDefinition> work) {
    var tt = FindByConstantName(constant);
    if (tt != null) foreach (var tm in tt.Methods.Where(x => x.HasBody)) if (visited.Add(tm)) work.Enqueue(tm);
  }
}
