# Sequence requirement catalog (V3.1.0)

**Kind:** per-leaf behavioral catalog (name -> function, derived from class name/base/code signals; no bodies).  
**Framework:** [`../game-events.md`](../game-events.md) owns the contract; this describes each `BaseRequirement` leaf.  
**Regenerate:** hint extractor over transitive subclasses.
**Hub:** [`INDEX.md`](../INDEX.md).  

Every `GameEvent.SequenceRequirements.BaseRequirement` subclass (game-event gate: cvar, event-active, operation compare, ...). Contract: [game-events.md](../game-events.md).

**37 concrete leaves** (38 requirement types transitively, including the abstract `BaseOperationRequirement` base of the 12 operation-compare leaves). Note: the same-named `Quests.Requirements.*` types (`RequirementBuff`/`Group`/`Holding`/`Level`/`Wearing`, contract `SetupRequirement`/`CheckRequirement`/`Clone`) are a **different** base and belong to the quest system, not here.

| Leaf | Function | base | key methods |
|---|---|---|---|
| `BaseOperationRequirement` | Operation Requirement | BaseRequirement | OnInit,compare,CanPerform,LeftSide |
| `RequirementCVar` | CVar | BaseOperationRequirement | OnInit,LeftSide,RightSide,ParseProperties |
| `RequirementEventActive` | Event Active | BaseRequirement | OnInit,CanPerform,ParseProperties,CloneChildSettings |
| `RequirementFullHealth` | Full Health | BaseRequirement | OnInit,CanPerform,CloneChildSettings |
| `RequirementGameStatBool` | Game Stat Bool | BaseRequirement | OnInit,CanPerform,ParseProperties,CloneChildSettings |
| `RequirementGameStatFloat` | Game Stat Float | BaseOperationRequirement | LeftSide,RightSide,ParseProperties,CloneChildSettings |
| `RequirementGameStatInt` | Game Stat Int | BaseOperationRequirement | OnInit,LeftSide,RightSide,ParseProperties |
| `RequirementGamestage` | Gamestage | BaseOperationRequirement | OnInit,LeftSide,RightSide,ParseProperties |
| `RequirementGroupLiveCount` | Group Live Count | BaseOperationRequirement | OnInit,LeftSide,RightSide,ParseProperties |
| `RequirementHasBuff` | Has Buff | BaseRequirement | OnInit,CanPerform,CheckBuff,ParseProperties |
| `RequirementHasBuffByTag` | Has Buff By Tag | BaseRequirement | CanPerform,ParseProperties,CloneChildSettings |
| `RequirementHasEntityTag` | Has Entity Tag | BaseRequirement | CanPerform,ParseProperties,CloneChildSettings |
| `RequirementHasHeld` | Has Held | BaseRequirement | OnInit,CanPerform,ParseProperties,CloneChildSettings |
| `RequirementHasParty` | Has Party | BaseRequirement | OnInit,CanPerform,CloneChildSettings |
| `RequirementHasSequenceLink` | Has Sequence Link | BaseRequirement | CanPerform,CloneChildSettings |
| `RequirementHasSpawnedEntities` | Has Spawned Entities | BaseRequirement | OnInit,CanPerform,ParseProperties,CloneChildSettings |
| `RequirementInBiome` | In Biome | BaseRequirement | CanPerform,ParseProperties,CloneChildSettings |
| `RequirementInPOI` | In POI | BaseRequirement | CanPerform,ParseProperties,CloneChildSettings |
| `RequirementInQuestZone` | In Quest Zone | BaseRequirement | CanPerform,CloneChildSettings |
| `RequirementInSafeZone` | In Safe Zone | BaseRequirement | CanPerform,CloneChildSettings |
| `RequirementInTraderArea` | In Trader Area | BaseRequirement | CanPerform,CloneChildSettings |
| `RequirementInVehicle` | In Vehicle | BaseRequirement | OnInit,CanPerform,CloneChildSettings |
| `RequirementIsBlock` | Is Block | BaseRequirement | OnInit,CanPerform,CheckBlock,ParseProperties |
| `RequirementIsHomerunActive` | Is Homerun Active | BaseRequirement | CanPerform,CloneChildSettings |
| `RequirementIsIndoors` | Is Indoors | BaseRequirement | CanPerform,CloneChildSettings |
| `RequirementIsTwitchActive` | Is Twitch Active | BaseRequirement | CanPerform,CloneChildSettings |
| `RequirementIsWeatherGracePeriod` | Is Weather Grace Period | BaseRequirement | CanPerform,CloneChildSettings |
| `RequirementNearbyEntities` | Nearby Entities | BaseRequirement | OnInit,CanPerform,ParseProperties,CloneChildSettings |
| `RequirementOnQuest` | On Quest | BaseRequirement | CanPerform,ParseProperties,CloneChildSettings |
| `RequirementProgression` | Progression | BaseOperationRequirement | OnInit,LeftSide,RightSide,ParseProperties |
| `RequirementRandomRoll` | Random Roll | BaseOperationRequirement | OnInit,LeftSide,RightSide,ParseProperties |
| `RequirementSandboxBool` | Sandbox Bool | BaseRequirement | OnInit,CanPerform,ParseProperties,CloneChildSettings |
| `RequirementSandboxFloat` | Sandbox Float | BaseOperationRequirement | LeftSide,RightSide,ParseProperties,CloneChildSettings |
| `RequirementSandboxInt` | Sandbox Int | BaseOperationRequirement | OnInit,LeftSide,RightSide,ParseProperties |
| `RequirementVarBool` | Var Bool | BaseRequirement | CanPerform,ParseProperties,CloneChildSettings |
| `RequirementVarFloat` | Var Float | BaseOperationRequirement | OnInit,LeftSide,RightSide,ParseProperties |
| `RequirementVarInt` | Var Int | BaseOperationRequirement | OnInit,LeftSide,RightSide,ParseProperties |
| `RequirementVarString` | Var String | BaseOperationRequirement | OnInit,LeftSide,RightSide,ParseProperties |
