# Quest objective catalog (V3.1.0)

**Kind:** per-leaf behavioral catalog (name -> function, derived from class name/base/code signals; no bodies).  
**Framework:** [`../quests-challenges.md`](../quests-challenges.md) owns the contract; this describes each `BaseObjective` leaf.  
**Regenerate:** hint extractor over transitive subclasses.

Every `BaseObjective` subclass (quest objective leaf: fetch, clear, goto, activate, ...). Contract: [quests-challenges.md](../quests-challenges.md).

**38 leaves.**

| Leaf | Function | base | key methods |
|---|---|---|---|
| `ObjectiveAssemble` | Assemble | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveBaseFetchContainer` | Base Fetch Container | BaseObjective | RemoveFetchItems,SetupQuestTag,SetupObjective,SetupExpectedItem |
| `ObjectiveBlockActivate` | Block Activate | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveBlockPickup` | Block Pickup | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveBlockPlace` | Block Place | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveBlockUpgrade` | Block Upgrade | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveBuff` | Buff | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveClearSleepers` | Clear Sleepers | BaseObjective | SetupQuestTag,SetupObjective,SetupDisplay,AddHooks |
| `ObjectiveClosestPOIGoto` | Closest POIGoto (ObjectiveClosestPOIGoto: No POI found.) | ObjectiveGoto | SetupObjective,SetupDisplay,SetupIcon,SetupPosition |
| `ObjectiveCraft` | Craft | BaseObjective | SetupQuestTag,SetupObjective,SetupDisplay,AddHooks |
| `ObjectiveEntityKill` | Entity Kill | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveExchangeItemFrom` | Exchange Item From | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveFetch` | Fetch | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveFetchAnyContainer` | Fetch Any Container | ObjectiveBaseFetchContainer | SetupObjective,SetupDisplay,SetupQuestTag,HandleFailed |
| `ObjectiveFetchFromContainer` | Fetch From Container | ObjectiveBaseFetchContainer | SetupQuestTag,SetupObjective,SetupDisplay,HandleFailed |
| `ObjectiveFetchFromTreasure` | Fetch From Treasure | BaseObjective | RemoveFetchItems,SetupObjective,SetupExpectedItem,SetupDisplay |
| `ObjectiveFetchKeep` | Fetch Keep | ObjectiveFetch | Clone |
| `ObjectiveGameEvent` | Game Event | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveGoto` | Goto | BaseObjective | SetupObjective,SetupDisplay,SetupIcon,SetupPosition |
| `ObjectiveInteractWithNPC` | Interact With NPC | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveOpenWindow` | Open Window | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectivePOIBlockActivate` | POIBlock Activate | BaseObjective | SetupQuestTag,SetupObjective,SetupDisplay,AddHooks |
| `ObjectivePOIBlockUpgrade` | POIBlock Upgrade | BaseObjective | SetupQuestTag,SetupObjective,SetupDisplay,AddHooks |
| `ObjectivePOIStayWithin` | POIStay Within | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveRallyPoint` | Rally Point | BaseObjective | SetupObjective,AddHooks,SetupFlags,getBlockTransform |
| `ObjectiveRandomGoto` | Random Goto | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveRandomGotoNPC` | Random Goto NPC | ObjectiveRandomGoto | SetupPosition,GetPosition,Clone |
| `ObjectiveRandomPOIGoto` | Random POIGoto | ObjectiveGoto | SetupObjective,SetupIcon,SetupPosition,AddHooks |
| `ObjectiveRepair` | Repair | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveReturnToNPC` | Return To NPC | ObjectiveRandomGoto | SetupObjective,SetupIcon,GetPosition,OnStart |
| `ObjectiveScrap` | Scrap | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveSpendSkillPoints` | Spend Skill Points | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveStatAwarded` | Stat Awarded | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveStayWithin` | Stay Within | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveTime` | Time | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
| `ObjectiveTreasureChest` | Treasure Chest | BaseObjective | SetupQuestTag,SetupObjective,SetupDisplay,AddHooks |
| `ObjectiveTwitchVote` | Twitch Vote | BaseObjective | SetupObjective,SetupDisplay,Update,VoteStarted |
| `ObjectiveWear` | Wear | BaseObjective | SetupObjective,SetupDisplay,AddHooks,RemoveHooks |
