# Challenge objective catalog (V3.0.1)

**Kind:** per-objective behavioral catalog (name -> role, derived from class name/base/hook fingerprint; no full bodies).
**Framework:** [`../quests-challenges.md`](../quests-challenges.md) owns the quest/challenge contract; this describes each `Challenges.BaseChallengeObjective` leaf.
**Regenerate:** `MethodList` + `DumpType`/`DumpMethod` over the transitive `BaseChallengeObjective` subclass family in the stable server DLL.
**Hub:** [`../INDEX.md`](../INDEX.md)

> **Dedicated relevance: challenge tracking is client-side.** The per-player
> `ChallengeJournal` is constructed in `EntityPlayerLocal.Awake` and ticked from
> `EntityPlayerLocal.OnUpdateLive`; every objective resolves its player through
> the journal's `EntityPlayerLocal` field, and the gather leaves even hook XUi
> inventory events. None of that exists on a dedicated server. The server's only
> roles are (a) persisting the serialized journal inside `PlayerDataFile`
> (`PlayerDataFile::Read/Write` call `ChallengeJournal::Read/Write`) and
> (b) executing the reward `GameEvent` sequence when a client redeems
> (`Challenge.Redeem` -> `GameEventManager.HandleAction(ChallengeClass.RewardEvent, player)`,
> which on a client ships `NetPackageGameEventRequest` to the server,
> [`../game-events.md`](../game-events.md)).

## Framework in brief

- **`ChallengeClass`** is the XML template (`challenges.xml` via
  `ChallengesFromXml`): name, objectives, `RewardEvent`, prerequisite chain
  (`GetNextChallengeName`), passive/MinEvent hooks (`FireEvent`, `ModifyValue`).
  `CreateChallenge(journal)` clones it into a runtime **`Challenge`**.
- **`ChallengeCategory` / `ChallengeGroup` / `ChallengeGroupEntry`** are the
  journal's display and rotation containers. `ChallengeJournal.Update` converts
  `World.worldTime` to days and calls `ChallengeGroupEntry.Update(day, player)`,
  which re-rolls daily group content (`AddAnyMissingChallenges`,
  `ResetChallenges`).
- **`Challenge`** owns `ObjectiveList` and a 3-state machine
  (`ChallengeStates`: `Active` 0, `Completed` 1, `Redeemed` 2).
  `HandleComplete` verifies every objective's `Complete`, then `EndChallenge`,
  fires `QuestEventManager.ChallengeCompleted(class, ...)` (so
  `ChallengeObjectiveChallengeComplete` leaves can count it) and shows the
  completion tooltip. `Redeem` fires the reward game event and notifies the
  journal (`HandleChallengeRedeemed` / `HandleChallengeGroupComplete`).
- There is **no `ChallengeStage` type**. Multi-step challenges ("gather, then
  craft, then place") are modeled by **`BaseRequirementObjectiveGroup`** plus
  indexed **`RequirementGroupPhase`** lists; six concrete groups exist
  (`RequirementObjectiveGroup{BlockUpgrade,Craft,GatherIngredients,Hold,Place,WindowOpen}`).
  Leaves with a `CreateRequirements()` override install their own group, e.g.
  `ChallengeObjectiveCraft.CreateRequirements` news up a
  `RequirementObjectiveGroupGatherIngredients` and calls
  `Challenge.SetRequirementGroup`.
- **`BaseChallengeObjective`** is a counter: `current` vs `MaxCount`, with
  `Complete` flipped by `CheckObjectiveComplete` / `CompleteObjective`.
  `HandleAddHooks` / `HandleRemoveHooks` subscribe the leaf's `Current_*`
  handler to a `QuestEventManager` event (the same client event hub quest
  objectives use). `CheckBaseRequirements` gates counting on the owning group
  being active and on an optional `Biome` filter checked against
  `Player.biomeStandingOn`. Save format is minimal: `Read`/`Write` persist only
  the `current` int (plus extra state in overrides such as
  `ChallengeObjectiveTime`).
- **`ChallengeBaseTrackedItemObjective`** (abstract, 5 subclasses) adds item
  resolution (`SetupItem`) and world tracking: on tracking start it registers a
  `TrackingEntry` with the challenge's `ChallengeTrackingHandler`, which scans
  chunks (`HandleTrack(Chunk)`, `Current_BlockChange`) to push nav markers for
  harvestable blocks.
- Client residency is visible in three IL lines of
  `BaseChallengeObjective::get_Player`:

  ```
  IL_0001: ldfld Challenge BaseChallengeObjective::Owner
  IL_0006: ldfld ChallengeJournal Challenge::Owner
  IL_000B: ldfld EntityPlayerLocal ChallengeJournal::Player
  ```

## Leaves

**28 leaves** (plus the abstract intermediate `ChallengeBaseTrackedItemObjective`).
`ChallengeObjectiveType` enumerates 27 concrete verbs (`HarvestByTag` reuses the
`Harvest` id).

| Objective | Role | base | key methods |
|---|---|---|---|
| `ChallengeObjectiveBlockPlace` | Place N matching blocks | BaseChallengeObjective | HandleAddHooks,Current_BlockPlace,CreateRequirements |
| `ChallengeObjectiveBlockUpgrade` | Upgrade N blocks | BaseChallengeObjective | HandleAddHooks,Current_BlockUpgrade,CreateRequirements |
| `ChallengeObjectiveBloodmoon` | Survive a blood moon night (`BloodMoonSurvive` event) | BaseChallengeObjective | HandleAddHooks,Current_BloodMoonSurvive |
| `ChallengeObjectiveChallengeComplete` | Complete N other challenges (recount via `UpdateMax`) | BaseChallengeObjective | HandleAddHooks,Current_ChallengeComplete,UpdateMax |
| `ChallengeObjectiveChallengeStatAwarded` | Accumulate a named challenge stat credit | BaseChallengeObjective | HandleAddHooks,Current_ChallengeAwardCredit |
| `ChallengeObjectiveCraft` | Craft item(s)/recipe; installs gather-ingredients stage | BaseChallengeObjective | Current_CraftItem,HandleRecipeListUpdate,CreateRequirements,CheckForNeededItem |
| `ChallengeObjectiveCureDebuff` | Use a listed cure item while the debuff is active | BaseChallengeObjective | HandleAddHooks,Current_UseItem,PlayerHasBuff |
| `ChallengeObjectiveEnterBiome` | Enter a target biome | BaseChallengeObjective | HandleAddHooks,Current_BiomeEnter |
| `ChallengeObjectiveGather` | Hold N of an item across backpack + toolbelt | ChallengeBaseTrackedItemObjective | ItemsChangedInternal,CheckForNeededItem,HandleUpdatingCurrent |
| `ChallengeObjectiveGatherByTag` | Hold N of any item matching a tag | ChallengeBaseTrackedItemObjective | ItemsChangedInternal,CheckForNeededItem,ParseElement |
| `ChallengeObjectiveGatherIngredient` | Hold recipe ingredients (feeder phase for craft stages) | ChallengeBaseTrackedItemObjective | ItemsChangedInternal,CheckForNeededItem,HandleUpdatingCurrent |
| `ChallengeObjectiveHarvest` | Harvest N of an item (optional required held tool) | ChallengeBaseTrackedItemObjective | HandleAddHooks,Current_HarvestItem,CreateRequirements |
| `ChallengeObjectiveHarvestByTag` | Harvest by block/harvest tag (optional held-item filter) | ChallengeBaseTrackedItemObjective | HandleAddHooks,Current_HarvestItem,CreateRequirements |
| `ChallengeObjectiveHold` | Have a specific item in hand | BaseChallengeObjective | HandleAddHooks,Current_HoldItem,HandleCheckStatus |
| `ChallengeObjectiveKill` | Kill N entities of a class (auto-completes when `EntityFactory.EnemySpawnMode` is off and target is an enemy) | BaseChallengeObjective | HandleAddHooks,Current_EntityKill |
| `ChallengeObjectiveKillByTag` | Kill N entities matching tags (same auto-complete guard) | BaseChallengeObjective | HandleAddHooks,Current_EntityKill |
| `ChallengeObjectiveLootContainer` | Open lootable container(s) | BaseChallengeObjective | HandleAddHooks,Current_ContainerOpened |
| `ChallengeObjectiveMeetTrader` | Meet/talk to a trader NPC | BaseChallengeObjective | HandleAddHooks,Current_NPCMeet |
| `ChallengeObjectiveQuestComplete` | Complete quest(s) matching tags/class | BaseChallengeObjective | HandleAddHooks,Current_QuestComplete |
| `ChallengeObjectiveScrap` | Scrap N items | BaseChallengeObjective | HandleAddHooks,Current_ScrapItem |
| `ChallengeObjectiveSpendSkillPoint` | Spend skill point(s) (attribute filter) | BaseChallengeObjective | HandleAddHooks,Current_SkillPointSpent,CreateRequirements |
| `ChallengeObjectiveSurvive` | Survive for an amount of time (`TimeSurvive` float event) | BaseChallengeObjective | HandleAddHooks,Current_TimeSurvive |
| `ChallengeObjectiveTime` | Elapsed-time counter on the update loop (pauses while dead/invalid; persists extra state) | BaseChallengeObjective | HandleAddHooks(AddObjectiveToBeUpdated),Update,Read,Write |
| `ChallengeObjectiveTrader` | Buy or sell N items at a trader | BaseChallengeObjective | HandleAddHooks,Current_BuyItems,Current_SellItems |
| `ChallengeObjectiveTwitch` | Twitch integration milestones (`TwitchObjectiveTypes`: VoteComplete, PimpPot, DefeatBossHorde, ...) | BaseChallengeObjective | HandleAddHooks,Current_TwitchEventReceive |
| `ChallengeObjectiveUseItem` | Use/consume a listed item | BaseChallengeObjective | HandleAddHooks,Current_UseItem |
| `ChallengeObjectiveWear` | Wear listed equipment (also hooks XUi equipment changes) | BaseChallengeObjective | HandleAddHooks,Current_WearItem |
| `ChallengeObjectiveWindowOpen` | Open a named UI window | BaseChallengeObjective | HandleAddHooks,Current_WindowChanged,HandleUpdatingCurrent |

Hook wiring is uniform: `HandleAddHooks` subscribes the `Current_*` handler to
the matching `QuestEventManager` event (`add_EntityKill`, `add_CraftItem`,
`add_HarvestItem`, `add_BlockPlace`, `add_ContainerOpened`, `add_WindowChanged`,
...), verified per leaf against the IL. Exceptions: the three gather leaves poll
inventory through `Bag.OnBackpackItemsChangedInternal` /
`Inventory.OnToolbeltItemsChangedInternal` on the local player's XUi, and
`ChallengeObjectiveTime` registers with
`QuestEventManager.AddObjectiveToBeUpdated` and ticks in `Update(dt)`.

## Requirement groups (challenge "stages")

| Group | Built by / purpose |
|---|---|
| `RequirementObjectiveGroupGatherIngredients` | `ChallengeObjectiveCraft.CreateRequirements`; gather-then-craft |
| `RequirementObjectiveGroupCraft` | craft phase inside a larger chain |
| `RequirementObjectiveGroupBlockUpgrade` | gather/craft-then-upgrade chains |
| `RequirementObjectiveGroupPlace` | craft-then-place chains |
| `RequirementObjectiveGroupHold` | hold-item requirement phase |
| `RequirementObjectiveGroupWindowOpen` | open-window requirement phase |

Each group advances an indexed `RequirementGroupPhase` list
(`CheckPhaseStatus(int)`), re-using the same objective leaves as phase members
(`RequirementGroupPhase.AddChallengeObjective`).

## Changelog

- 2026-07-24: initial catalog from stable V3.0.1 server DLL (28 leaves + 1 abstract item base, hook wiring and client-side residency verified from IL).
