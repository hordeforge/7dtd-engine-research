// Shared reachability-seed definitions for Reach.exe and Coverage.exe.
// Both tools must agree on what the "dedicated server call graph" starts from, or the
// two coverage lenses drift. Keep the seed DATA and the enqueue logic here and use
// Seeds.* from both tools; a test asserts the two tools' reached-method counts match.
using System;
using System.Collections.Generic;
using System.Linq;
using Mono.Cecil;

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
}
