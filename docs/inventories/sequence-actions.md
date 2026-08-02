# Sequence action catalog (V3.1.0)

**Kind:** per-action reference (name -> effect, derived from class name/base/fields/key-method IL; no bodies).
**Framework:** [`../game-events.md`](../game-events.md) owns the contract; this describes each `BaseAction` leaf.
**Regenerate:** hint extractor over transitive subclasses of `GameEvent.SequenceActions.BaseAction`.
**Hub:** [`../INDEX.md`](../INDEX.md).

Every concrete `BaseAction` subclass **in the `GameEvent.SequenceActions` namespace**, the effect side of the game-event sequence system (gates live in [sequence-requirements.md](sequence-requirements.md)). Actions are parsed from `gameevents.xml` properties (`ParseProperties`), cloned per running sequence (`CloneChildSettings`), and driven per phase by `GameEventActionSequence`.

**123 actions in the `GameEvent.SequenceActions` namespace** (132 types there: the root `BaseAction`, 8 shared intermediate bases, and 123 concrete leaves; `ActionBlockReplace`, `ActionRemoveEntities`, and `ActionSpawnEntity` are concrete leaves that also parent one subclass each).

**Scope caveat:** the full transitive closure of `BaseAction` is **137** types, not 132. The extra 5 live in sibling namespaces and are **not** listed below: `GameEvent.SequenceDecisions.BaseDecision` + `DecisionIf`, and `GameEvent.SequenceLoops.BaseLoop` + `LoopFor` + `LoopWhile`. Those three concrete leaves are real, XML-wired control-flow verbs (`GameEventsFromXml.ParseGameEventSequenceDecision` / `ParseGameEventSequenceLoop`) that wrap child actions with an if-condition or a for/while loop, so a sequence implementation needs them even though they are not `SequenceActions.*`.

## Dispatch contract

`BaseAction.PerformAction()` first walks the action-local `Requirements` list (each `BaseRequirement.CanPerform(Owner.Target)`), returning `RequirementsNotMet` on any failure, then tail-calls the virtual effect hook:

```
IL_005D: ldarg.0
IL_005E: callvirt BaseAction/ActionCompleteStates BaseAction::OnPerformAction()
```

Return enum `ActionCompleteStates`: `InComplete=0`, `InCompleteRefund=1`, `RequirementsNotMet=2`, `Complete=3` (`InComplete` keeps the action live across ticks; delays, waits, and staged block edits use it).

The intermediate bases specialize the hook:

| Base | Derives | Effect hook | What it adds |
|---|---|---|---|
| `BaseAction` | Object | `OnPerformAction` | phase fields (`Phase`, `PhaseOnComplete`, `PhaseOnDenied`), action keys, per-action requirements |
| `ActionBaseTargetAction` | BaseAction | `PerformTargetAction(Entity)` | iterates the sequence target or a named `targetGroup` entity list |
| `ActionBaseClientAction` | ActionBaseTargetAction | `OnServerPerform` / `OnClientPerform` | runs `OnServerPerform` server-side, then `OnClientPerform` locally or ships `NetPackageGameEventResponse` (response type 12) to the owning remote client |
| `ActionBaseBlockAction` | BaseAction | `UpdateBlock(World,Vector3i,BlockValue)` | scans a tag-filtered block box around the sequence position, batches changes via `ProcessChanges`/`UpdateBlocks` |
| `ActionBaseItemAction` | ActionBaseClientAction | `HandleItemStackChange` / `HandleItemValueChange` | walks bag/belt/equipment slots by item tag and count on the client |
| `ActionBaseContainersAction` | BaseAction | `HandleContainerAction(List)` | collects nearby lootable tile entities (`GetTileEntityList`, `CheckValidTileEntity`) |
| `ActionBaseSpawn` | BaseAction | `OnPerformAction` + `SpawnEntity` | entity-group selection, `FindValidPosition`, party-size scaling, group registration, repeat handling |
| `ActionBaseTeleport` | ActionBaseTargetAction | `TeleportEntity(Entity,Vector3)` | delayed teleport plumbing |
| `BaseWait` | BaseAction | `OnPerformAction` | condition-type polling for `WaitUntil` / `WaitWhile` |

## Flow, variables, positions (11)

| Action | Role | base | key method |
|---|---|---|---|
| `ActionDelay` | Holds the phase for `delayTime` seconds before completing | BaseAction | OnPerformAction |
| `WaitUntil` | Blocks the phase until its requirement set passes | BaseWait | OnPerformAction |
| `WaitWhile` | Blocks the phase while its requirement set still passes | BaseWait | OnPerformAction |
| `ActionWaitForDead` | Polls a target group until all members are dead, with a despawn phase escape | BaseAction | OnPerformAction |
| `ActionCallGameEvent` | Fires another named game event (random pick from a list) via `GameEventManager.HandleAction`, optionally per group member | BaseAction | OnPerformAction |
| `ActionSetEventFlag` | Toggles a global `GameEventFlagTypes` flag (with duration) through `GameEventManager.SetGameEventFlag` | ActionBaseTargetAction | PerformTargetAction |
| `ActionModifyVarBool` | Sets a named per-sequence bool variable | ActionBaseClientAction | PerformTargetAction |
| `ActionModifyVarInt` | Applies an operation (set/add/...) to a named per-sequence int variable, clamped to min/max | ActionBaseClientAction | PerformTargetAction |
| `ActionModifyVarFloat` | Applies an operation to a named per-sequence float variable | ActionBaseClientAction | PerformTargetAction |
| `ActionGetNearbyPoint` | Resolves a valid nearby point (spawn-style raycast via `ActionBaseSpawn.FindValidPosition`) into the sequence position | BaseAction | OnPerformAction |
| `ActionGetLandClaimPosition` | Resolves the target player's primary land claim (`TEFeatureLandClaim`) into the sequence position | BaseAction | OnPerformAction |

## Entity groups (9)

Sequence-scoped named entity lists (`GameEventActionSequence.GetEntityGroup`) that later actions target.

| Action | Role | base | key method |
|---|---|---|---|
| `ActionAddAllPlayersToGroup` | Adds every online player to a named group | BaseAction | OnPerformAction |
| `ActionAddPlayerToGroup` | Adds one player (by name) to a group | BaseAction | OnPerformAction |
| `ActionAddPartyToGroup` | Adds the target's party members to a group | BaseAction | OnPerformAction |
| `ActionAddClosestEntityToGroup` | Adds the closest tag-matching entity within range | BaseAction | OnPerformAction |
| `ActionAddEntitiesToGroup` | Adds all tag/state-matching entities within range | BaseAction | OnPerformAction |
| `ActionAddSpawnedEntitiesToGroup` | Copies entities this event spawned into another group | BaseAction | OnPerformAction |
| `ActionClearGroup` | Empties a named group | BaseAction | OnPerformAction |
| `ActionSetupBossGroup` | Binds boss + minion groups with icons for the boss-bar UI | BaseAction | OnPerformAction |
| `ActionUpdateBossGroup` | Refreshes an existing boss group's state | BaseAction | OnPerformAction |

## Spawning and entity lifecycle (8)

| Action | Role | base | key method |
|---|---|---|---|
| `ActionSpawnEntity` | Spawns entities from names/groups with targeting, buffs on spawn, group registration | ActionBaseSpawn | AddPropertiesToSpawnedEntity, HandleTargeting |
| `ActionSpawnEntitySpawner` | Continuous spawner variant keeping a minimum alive count, optional spawn-on-hit | ActionSpawnEntity | HandleRepeat, HandleExtraAction |
| `ActionSpawnContainer` | Spawns a loot container entity with overridden loot list/name | ActionBaseSpawn | AddPropertiesToSpawnedEntity |
| `ActionRespawnEntities` | Recreates every dead member of a target group in place (`EntityFactory.CreateEntity` after `RemoveEntity`) | BaseAction | OnPerformAction |
| `ActionRespawnEntity` | Delayed single-entity respawn from recorded class/position | BaseAction | OnPerformAction |
| `ActionReplaceEntities` | Swaps group members for freshly spawned entities of new classes | ActionBaseTargetAction | PerformTargetAction |
| `ActionRemoveEntities` | Despawns a target group (deferred via `removeLater` coroutine, event bookkeeping in `HandleRemoveData`) | BaseAction | OnPerformAction |
| `ActionRemoveVehicles` | Vehicle-filtered removal that can refund the vehicle item and fuel | ActionRemoveEntities | HandleRemoveData |

## Entity combat and physics (15)

| Action | Role | base | key method |
|---|---|---|---|
| `ActionKill` | Kills the target outright via `Entity.DamageEntity` | ActionBaseTargetAction | PerformTargetAction |
| `ActionExplodeTarget` | Detonates a parameterized explosion (`GameManager.ExplosionServer`) at the target's block position | ActionBaseTargetAction | PerformTargetAction |
| `ActionExplodePosition` | Same explosion at the sequence position instead of an entity | BaseAction | OnPerformAction |
| `ActionRageZombies` | Forces `EntityHuman.StartRage` (speed % for a duration), wakes sleepers, sets attack target | ActionBaseTargetAction | PerformTargetAction |
| `ActionEnemyToCrawler` | Converts an enemy to a crawler via a synthetic dismember `DamageResponse` | ActionBaseTargetAction | PerformTargetAction |
| `ActionPrimeEntity` | Primes a demolisher-style target (`EntityZombieCop.HandlePrimingDetonator`) with override timer | ActionBaseTargetAction | PerformTargetAction |
| `ActionRagdoll` | Ragdolls/stuns the target for a duration | ActionBaseTargetAction | PerformTargetAction |
| `ActionPushEntity` | Applies a directional force to the target | ActionBaseTargetAction | PerformTargetAction |
| `ActionPullEntities` | Drags a target group toward the sequence position within a distance band | BaseAction | OnPerformAction |
| `ActionSetInvestigationPosition` | Points AI investigation (optionally alert) at the sequence position for a time | ActionBaseTargetAction | PerformTargetAction |
| `ActionEjectFromVehicle` | Detaches the target from its vehicle and closes open windows (local or via `NetPackageCloseAllWindows`) | ActionBaseTargetAction | PerformTargetAction |
| `ActionSetFuel` | Sets vehicle fuel to a preset level (`Vehicle.SetFuelLevel`) | ActionBaseTargetAction | PerformTargetAction |
| `ActionRemoveFuel` | Drains the target vehicle's fuel | ActionBaseTargetAction | PerformTargetAction |
| `ActionFlipRotation` | Flips the target/vehicle rotation client-side (`EntityVehicle.VelocityFlip`) | ActionBaseClientAction | OnClientPerform |
| `ActionRandomizeRotation` | Randomizes target/vehicle facing client-side | ActionBaseClientAction | OnClientPerform |

## Buffs, cvars, entity stats (9)

| Action | Role | base | key method |
|---|---|---|---|
| `ActionAddBuff` | Adds a named buff (duration, removes-buff list, alt-vision variant, sequence link) | ActionBaseTargetAction | PerformTargetAction |
| `ActionAddRandomBuff` | Adds one random buff from a list, removing its paired buff | ActionBaseTargetAction | PerformTargetAction |
| `ActionRemoveBuff` | Removes named buff(s) | ActionBaseTargetAction | PerformTargetAction |
| `ActionRemoveBuffsByTag` | Removes all buffs matching a tag set | ActionBaseTargetAction | PerformTargetAction |
| `ActionRemoveDeathBuffs` | Strips death-related buffs except excluded tags | ActionBaseTargetAction | PerformTargetAction |
| `ActionReplaceBuff` | Swaps one buff for another | ActionBaseTargetAction | PerformTargetAction |
| `ActionPauseBuff` | Pauses/resumes buffs matching tags (server + client sides) | ActionBaseClientAction | OnServerPerform, OnClientPerform |
| `ActionModifyEntityStat` | Applies an operation to a `StatTypes` stat (health/stamina/..., absolute or percent) on the client entity | ActionBaseClientAction | OnClientPerform |
| `ActionModifyCVar` | Applies an operation to a named cvar via `EntityBuffs.SetCustomVar` | ActionBaseClientAction | OnClientPerform |

## Progression, quests, player data (10)

| Action | Role | base | key method |
|---|---|---|---|
| `ActionAddXP` | Grants a fixed XP amount | ActionBaseClientAction | OnClientPerform |
| `ActionAddXPDeficit` | Grants XP toward the next-level deficit | ActionBaseClientAction | OnClientPerform |
| `ActionAddPlayerLevel` | Adds player levels directly | ActionBaseClientAction | OnClientPerform |
| `ActionAddSkillPoints` | Grants skill points | ActionBaseClientAction | OnClientPerform |
| `ActionModifyProgression` | Adds/removes named progression entries (perks/skills) with values | ActionBaseClientAction | OnClientPerform |
| `ActionResetPlayerData` | Selectively wipes persistent player data: levels, skills, land claims, sleeping bag, books, crafting, quests, challenges, backpack, stats | ActionBaseClientAction | OnServerPerform, OnClientPerform |
| `ActionResetMap` | Clears the client map database, optionally waypoints and discovery | ActionBaseClientAction | OnClientPerform |
| `ActionAddQuest` | Gives the player a quest by ID | ActionBaseClientAction | OnClientPerform |
| `ActionFailQuest` | Fails (optionally removes) a quest by ID | ActionBaseClientAction | OnClientPerform |
| `ActionCompleteChallenge` | Completes (optionally force-redeems) a challenge by ID | ActionBaseClientAction | OnClientPerform |

## Items and inventory (10)

| Action | Role | base | key method |
|---|---|---|---|
| `ActionAddItems` | Grants item lists with counts | ActionBaseClientAction | OnClientPerform |
| `ActionAddStartingItems` | Re-runs `EntityPlayerLocal.SetupStartingItems` | ActionBaseClientAction | OnClientPerform |
| `ActionAddItemDurability` | Adds/removes durability (flat or percent) on tag-matched items | ActionBaseItemAction | HandleItemStackChange, HandleItemValueChange |
| `ActionDropHeldItem` | Forces the held item to drop with a sound | ActionBaseItemAction | OnClientPerform |
| `ActionDropItems` | Drops tag-matched items, optionally replacing them with another item | ActionBaseItemAction | HandleItemStackChange |
| `ActionRemoveItems` | Deletes tag-matched items | ActionBaseItemAction | HandleItemStackChange, HandleItemValueChange |
| `ActionReplaceItems` | Replaces tag-matched items (equipment-aware) with a named item | ActionBaseItemAction | HandleItemStackChange, CheckEquipmentReplace |
| `ActionUnloadItems` | Ejects ammo/contents from tag-matched items | ActionBaseItemAction | HandleItemStackChange |
| `ActionSetItemSlots` | Writes specific items into specific slot numbers of a location | ActionBaseClientAction | OnClientPerform |
| `ActionShuffleItems` | Shuffles items across the chosen inventory locations | ActionBaseClientAction | OnClientPerform |

## Containers and signs (4)

| Action | Role | base | key method |
|---|---|---|---|
| `ActionEmptyContainers` | Empties nearby containers (inputs/outputs/fuel/tools toggles) | ActionBaseContainersAction | HandleContainerAction |
| `ActionReplaceItemsContainers` | Replaces tag-matched items inside nearby containers | ActionBaseContainersAction | HandleContainerAction |
| `ActionShuffleContainers` | Shuffles contents of nearby containers | ActionBaseContainersAction | HandleContainerAction |
| `ActionRenameSigns` | Rewrites nearby sign text | ActionBaseContainersAction | HandleContainerAction |

## Blocks, POI, claim areas (19)

| Action | Role | base | key method |
|---|---|---|---|
| `ActionBlockReplace` | Replaces tag-matched blocks with random picks from a list (optionally only air) | ActionBaseBlockAction | UpdateBlock |
| `ActionBlockReplaceAttack` | Timed hostile block-replace that tracks added blocks and removes/refunds them after `timeAlive` | ActionBlockReplace | UpdateBlock, ChangesComplete |
| `ActionBlockUpgrade` | Upgrades matched blocks one stage | ActionBaseBlockAction | UpdateBlock |
| `ActionBlockDowngrade` | Downgrades matched blocks one stage | ActionBaseBlockAction | UpdateBlock |
| `ActionBlockHealth` | Sets/damages matched block health by state and amount | ActionBaseBlockAction | UpdateBlock |
| `ActionBlockDoorState` | Opens/closes and locks/unlocks matched doors | ActionBaseBlockAction | UpdateBlock |
| `ActionBlockAnimateBlock` | Drives Animator bool/int/trigger parameters on matched block entities | ActionBaseBlockAction | UpdateBlock, AnimateBlock |
| `ActionBlockGrowCrops` | Advances matched crops to grown | ActionBaseBlockAction | UpdateBlock |
| `ActionBlockPickup` | Pops matched blocks into pickup items | ActionBaseBlockAction | UpdateBlock |
| `ActionBlockTriggerFall` | Triggers falling on matched unsupported blocks | ActionBaseBlockAction | UpdateBlock |
| `ActionBlockTriggerMines` | Detonates (or arms) matched mines | ActionBaseBlockAction | UpdateBlock |
| `ActionBlockGameEvent` | Fires named game events at matched block positions | ActionBaseBlockAction | UpdateBlock |
| `ActionPOIReset` | Resets the containing POI prefab via a staged coroutine | BaseAction | OnPerformAction (coroutine `onPerformAction`) |
| `ActionPOISetLightState` | Toggles POI light blocks (by index block names) on/off | BaseAction | OnPerformAction, UpdateBlocks |
| `ActionResetSleepers` | Resets all sleeper volumes (`World.ResetSleeperVolumes`) | BaseAction | OnPerformAction |
| `ActionRemoveSpawnedBlocks` | Removes blocks previously spawned by this event (tracked in `GameEventManager`), optional despawn effect | BaseAction | OnPerformAction |
| `ActionFillArea` | Staged chunk-by-chunk block fill of an area with tag filters and player teleport-out | BaseAction | OnPerformAction |
| `ActionFillSafeZone` | Same staged fill scoped to the target's land-claim safe zone | BaseAction | OnPerformAction |
| `ActionDestroySafeZone` | Staged destruction of a land-claim safe zone by destruction type, buffing/flagging affected players | BaseAction | OnPerformAction |

## Teleportation (5)

| Action | Role | base | key method |
|---|---|---|---|
| `ActionTeleport` | Teleports the target to a fixed/offset position | ActionBaseTeleport | PerformTargetAction |
| `ActionTeleportNearby` | Short-range random displacement of the target | ActionBaseTeleport | PerformTargetAction |
| `ActionRandomTeleport` | Random long-range teleport within a distance band (bounded tries) | ActionBaseTeleport | PerformTargetAction |
| `ActionTeleportToTarget` | Teleports group members to a resolved point near another group | ActionBaseTeleport | OnPerformAction, HandleTeleportToTarget |
| `ActionTeleportToSpecial` | Client-side teleport to a `SpecialPointTypes` location (e.g. trader) after a delay | ActionBaseClientAction | OnClientPerform, handleTeleport |

## World and environment (6)

| Action | Role | base | key method |
|---|---|---|---|
| `ActionSetDayTime` | Jumps world time to an absolute day/hour/minute (`World.SetTimeJump`) | BaseAction | OnPerformAction |
| `ActionTimeChange` | Jumps time by preset (dawn/dusk/...) or offset, dawn/dusk from `SkyManager` | BaseAction | OnPerformAction |
| `ActionSetHordeNight` | Forces blood moon for today (`AIDirectorBloodMoonComponent.SetForToday`), optional keep-day flag | BaseAction | OnPerformAction |
| `ActionSetWeather` | Forces a named weather group for a duration (`WeatherManager.ForceWeather`) | BaseAction | OnPerformAction |
| `ActionSetStorm` | Starts/sets a storm (`WeatherManager.SetStorm` + `TriggerUpdate`) | BaseAction | OnPerformAction |
| `ActionResetRegions` | Coroutine-staged region reset by `ResetTypes` | BaseAction | OnPerformAction (coroutine `HandleReset`) |

## Client UI and feedback (7)

| Action | Role | base | key method |
|---|---|---|---|
| `ActionAddChatMessage` | Sends localized chat text to the target player | ActionBaseClientAction | OnClientPerform |
| `ActionBeltTooltip` | Shows a toolbelt tooltip with optional sound | ActionBaseClientAction | OnClientPerform |
| `ActionShowMessageWindow` | Opens a titled message window | ActionBaseClientAction | OnClientPerform |
| `ActionShowWindow` | Opens a named GUI window | ActionBaseClientAction | OnClientPerform |
| `ActionCloseWindow` | Closes a named GUI window | ActionBaseClientAction | OnClientPerform |
| `ActionPlaySound` | Plays (optionally looping/in-head/behind-player) sounds, with stop handling | ActionBaseTargetAction | PerformTargetAction, OnClientPerform |
| `ActionSetScreenEffect` | Applies a named screen effect with intensity/fade | ActionBaseClientAction | OnClientPerform |

## Twitch integration (10)

| Action | Role | base | key method |
|---|---|---|---|
| `ActionTwitchAddPoints` | Awards Twitch points (type/recipient/requester filters) | ActionBaseClientAction | OnClientPerform |
| `ActionTwitchAddActionCooldown` | Puts matched Twitch actions on cooldown | ActionBaseClientAction | OnClientPerform |
| `ActionTwitchStartCooldown` | Starts the global Twitch action cooldown | ActionBaseClientAction | OnClientPerform |
| `ActionTwitchEndCooldown` | Ends the global Twitch cooldown, optional sound | ActionBaseClientAction | OnClientPerform |
| `ActionTwitchStartVote` | Queues a Twitch vote type (`TwitchVotingManager.QueueVote`) | BaseAction | OnPerformAction |
| `ActionTwitchVoteDelay` | Delays the next Twitch vote | BaseAction | OnPerformAction |
| `ActionTwitchSendChannelMessage` | Posts localized text to the Twitch channel chat | ActionBaseClientAction | OnClientPerform |
| `ActionTwitchChallengeAction` | Reports progress to a Twitch objective type | ActionBaseClientAction | OnClientPerform |
| `ActionTwitchAddEntitiesToSpawned` | Registers target entities as Twitch-spawned for kill tracking | ActionBaseTargetAction | PerformTargetAction |
| `ActionStartHomerun` | Starts the Twitch "homerun" minigame with reward levels/events for a game-time window | ActionBaseTargetAction | PerformTargetAction |

## Changelog

- 2026-07-24: initial catalog from V3.0.1 dedicated-server IL (132 `GameEvent.SequenceActions` types, 123 concrete actions; dispatch contract, base specializations, and key-method roles verified against `MethodList`/`DumpType`/`DumpMethod` output).
