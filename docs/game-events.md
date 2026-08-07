# GameEvent sequence framework (dedicated V3.1.0)

**Owns:** the `GameEvent.*` surface, the server-side scripted-event engine that
runs XML-defined action sequences against players and the world: the
`GameEventManager` driver, the `GameEventActionSequence` phase machine, the
action / requirement / decision / loop contracts, and the net plumbing that
requests, approves, and mirrors events to clients.
**Not:** the XML event definitions themselves (`gameevents.xml` is content, not
IL); the Twitch chat service that fires many of these events (external); the
quest and challenge systems that merely trigger events.
**Evidence:** `GameEvent.*` IL (179 types / 1014 method bodies across five
namespaces, plus the top-level `GameEventManager`, `GameEventActionSequence`,
`GameEventsFromXml`, `GameEventVariables` drivers, 127 more bodies; ~187
`GameEvent` rows in the type surface). Dump locally with
`tools/src/DumpAll GameEvent` + `DumpMethod GameEventManager ""` (git-ignored).
**Hub:** [`INDEX.md`](INDEX.md). **Method:** [`re-methodology.md`](re-methodology.md).

This is the most explicitly state-machine-shaped system in the assembly: a tree
of little interpreters (sequence -> phases -> actions, with decisions and loops
as actions that contain their own phase machines), ticked once per frame from
the main server loop ([`loop-gmupdate.md`](loop-gmupdate.md), manager chain).

---

## 1. Architecture

Five namespaces plus four top-level driver types:

| Namespace / type | Types | Role |
|---|---:|---|
| `GameEventManager` (top-level) | 1 (+nested) | Singleton driver: template registry, running-sequence list, spawn/block/flag/boss bookkeeping, net event fan-out |
| `GameEventActionSequence` (top-level) | 1 | One event: requirement list + action list run as a phase machine |
| `GameEventsFromXml`, `GameEventVariables` (top-level) | 2 | XML -> template parser; runtime variable store |
| `GameEvent.SequenceActions` | 132 | `BaseAction` + concrete verbs (spawn, teleport, items, blocks, UI, ...) |
| `GameEvent.SequenceRequirements` | 39 | `BaseRequirement` + 37 boolean gates |
| `GameEvent.SequenceDecisions` | 2 | `BaseDecision`, `DecisionIf` (conditional block) |
| `GameEvent.SequenceLoops` | 3 | `BaseLoop`, `LoopFor`, `LoopWhile` |
| `GameEvent.GameEventHelpers` | 3 | `HomerunManager` mini-game (boss "homerun" mode) |

`GameEventsFromXml` parses `<action|requirement|loop|wait|decision|variable|property>`
children of each event element, resolving the `class` attribute by reflection
against fixed prefixes (`GameEvent.SequenceActions.Action*`, `...Wait*`,
`GameEvent.SequenceRequirements.Requirement*`, `GameEvent.SequenceLoops.Loop*`,
`GameEvent.SequenceDecisions.Decision*`), supports a `template` attribute for
inheritance, and finishes each template with `HandleTemplateInit()` (variable
substitution into `DynamicProperties`, then `ParseProperties` + `Init` on every
node). Parsed templates land in the static
`Dictionary<string, GameEventActionSequence> GameEventManager.GameEventSequences`.

```mermaid
flowchart TB
  XML[gameevents.xml] --> P[GameEventsFromXml<br/>reflection: class attr -> Action*/Requirement*/Loop*/Decision*/Wait*]
  P --> T[(GameEventSequences<br/>template dictionary)]
  RQ[NetPackageGameEventRequest<br/>client / party] --> HA
  TW[Twitch integration] --> HA
  BLK[BlockGameEvent /<br/>MinEventActionCallGameEvent /<br/>QuestActionGameEvent] --> HA
  NEST[ActionCallGameEvent<br/>nested event] --> HA
  HA[GameEventManager.HandleAction] -->|CanPerform + SingleInstance gate| T
  T -->|Clone template| S[GameEventActionSequence instance]
  S --> RUN[(ActionSequenceUpdates<br/>running list)]
  GM[gmUpdate manager chain] -->|Update dt, server only| M[GameEventManager.Update]
  M --> AU[HandleActionUpdates<br/>tick + reap sequences]
  M --> SU[HandleSpawnUpdates<br/>tracked spawned entities]
  M --> BU[HandleBlockUpdates<br/>tracked spawned blocks]
  M --> FU[HandleEventFlagUpdates<br/>global flags]
  M --> BG[HandleBossGroupUpdates]
  M --> HR[HomerunManager.Update]
  AU --> RUN
```

`GameEventManager.Update(deltaTime)` is a hard no-op unless
`ConnectionManager.IsServer` and `GameManager.World` is non-null: the whole
engine runs server-side; clients only see mirrored effects.

---

## 2. Sequence lifecycle (state machine)

Creation is `GameEventManager.HandleAction(name, requester, target, ...)`.
The IL shows, in order: a comma-separated `name` fans out into one call per
event; on a client the call becomes a `NetPackageGameEventRequest` to the
server (`HandleActionClient`); on the server the template is looked up, any
passed `variables` are written into the template's `EventVariables` store,
`CanPerform(target)` is evaluated (all sequence requirements AND every action's
`CanPerform`, e.g. the spawn budget in §6), `SingleInstance` templates are
denied while a same-name sequence is running, and finally the template is
`Clone()`d, given `Target` / `TargetPosition` / requester context (inherited
from an `OwnerSequence` when a sequence-link or nested call created it), and
appended to `ActionSequenceUpdates`.

`CanPerform(player)` (IL=44) is the AND of every `Requirements[i].CanPerform`
and `Actions[i].CanPerform`. `SetupTarget()` (IL=97) resolves `POIInstance`/
`POIPosition` by `TargetType`: a POI/position type queries
`GetPrefabFromWorldPos` (falling back to the player's `prefab` bounding box
for entity targets); `HasTarget()` (IL=41) is `Target != null && !DeadCheck()`
for entity targets, `POIPosition != zero` for POI targets, and for position
targets "the block at `POIPosition` differs from the sequence's `blockValue`
(unless `AllowWhileDead`)".
`ParseProperties(properties)` (IL=70) stores the `Properties` and parses the
sequence knobs: `allow_user_trigger` (bool), `action_type` and `target_type`
(enums), `allow_while_dead`, `refund_inactivity`, `single_instance` (bools),
`category` (string), and the comma-split `category_names` array.

**`StartSequence(manager)` (IL=4):** only `StartTime = Time.time` (manager arg
unused in body).

`GameEventActionSequence.Update()` (IL=287) is the per-tick action dispatch:
for each incomplete action whose `Phase` matches `CurrentPhase`, it either
refunds (when `AllowRefunds && RefundInactivity` and
`Time.time - StartTime > 60`) or runs `PerformAction()`. A result of 3
(complete), or 1 combined with `action.IgnoreRefund`, marks `IsComplete` and
jumps to `PhaseOnComplete`; a result of 2 (denied) marks complete and jumps to
`PhaseOnDenied` (no jump when the target is -1).

Each tick, `HandleActionUpdates` runs `StartSequence` once (the `StartTime`
sentinel is `-1`; the first tick stamps `Time.time`), then `Update()`, inside a
try/catch that logs `Exception while updating action sequence <name>` and
rethrows. A reverse-order reap pass then aborts sequences whose target vanished
(`!HasTarget() && AllowRefunds`) and removes every `IsComplete` sequence,
returning its `ReservedSpawnCount` to the manager's `ReservedCount` budget.

`HasTarget()` is per `TargetTypes` (`Entity`=0, `POI`=1, `Block`=2): a live (or
`AllowWhileDead`) target entity, a nonzero `POIPosition`, or the recorded
`blockValue` still present in the world.

```mermaid
stateDiagram-v2
  [*] --> Template: GameEventsFromXml parse<br/>+ HandleTemplateInit
  Template --> Requested: HandleAction(name, ...)
  Requested --> Denied: CanPerform false /<br/>SingleInstance already running
  Denied --> [*]: NetPackageGameEventResponse Denied
  Requested --> Queued: Clone + SetupTarget<br/>-> ActionSequenceUpdates
  Queued --> Running: first tick StartSequence<br/>(StartTime -1 -> Time.time)
  Running --> Running: Update() = one pass over<br/>actions of CurrentPhase
  Running --> Running: no action left in phase<br/>-> CurrentPhase++
  Running --> Running: PhaseOnComplete/PhaseOnDenied jump<br/>-> Reset actions with Phase >= new phase
  Running --> Refunded: action returns InCompleteRefund<br/>(AllowRefunds, TwitchAction)
  Running --> Completed: CurrentPhase >= PhaseMax
  Running --> Aborted: target lost<br/>(!HasTarget && AllowRefunds)
  Completed --> [*]: notify requester (Completed)<br/>reap + release ReservedCount
  Refunded --> [*]: TwitchRefundNeeded to requester<br/>reap + release ReservedCount
  Aborted --> [*]: reap + release ReservedCount
```

The phase machine inside `Update()` (287 IL) works like this:

1. Scan all actions; only those with `Phase == CurrentPhase` and not
   `IsComplete` are touched. `PhaseMax` was computed in `Init()` as the highest
   declared phase + 1.
2. Each touched action gets `PerformAction()` (unless the 60-second
   inactivity-refund timer fired: `AllowRefunds && RefundInactivity &&
   Time.time - StartTime > 60` forces the `InCompleteRefund` outcome without
   running the action).
3. The returned `ActionCompleteStates` drives completion and phase jumps (§3).
4. If the pass touched nothing, `CurrentPhase++` (empty phases fall through).
   If an action requested a jump, `CurrentPhase = jump target` and every action
   with `Phase >= new phase` is `Reset()` so a backward jump re-runs them.
5. `CurrentPhase >= PhaseMax` marks the sequence `IsComplete` and notifies the
   requester: a local player via `HandleGameEventCompleted`, a remote one via
   `NetPackageGameEventResponse` `Completed` (13).

---

## 3. Action lifecycle (state machine)

`BaseAction` is the single node contract. Fields that matter: `Phase` (which
phase it belongs to), `PhaseOnComplete` / `PhaseOnDenied` (jump targets, `-1` =
none, XML `phase_on_complete` / `phase_on_denied`), `IgnoreRefund`
(`ignore_refund`), `IsComplete`, `Requirements` (per-action gate list), and an
`actionKey` built by `SetActionKeyData` (`<sequenceName><index>`, nested nodes
`<parentKey>:<index>`) registered in a static `sLookupByKey` dictionary so the
client can address one action inside one sequence (§6, client actions).

The template methods:

| Method | Role |
|---|---|
| `ParseProperties` | XML -> fields (base parses `phase`, jumps, `ignore_refund`; subclasses append) |
| `Init` / `OnInit` | Post-parse setup, clears `IsComplete` |
| `CanPerform(target)` | Approval-time veto (default true), evaluated before the sequence is cloned |
| `PerformAction` | Per-tick entry: requirement gate, then `OnPerformAction` |
| `OnPerformAction` | The actual verb; returns `ActionCompleteStates` |
| `Reset` / `OnReset` | Re-arm after a phase jump or loop iteration |
| `Clone` / `CloneChildSettings` | Deep copy for instantiation from the template |
| `OnClientPerform` | Client-side half of a mirrored action |

`PerformAction()` (39 IL) is exactly: if `UseRequirements` and the list exists,
evaluate each `BaseRequirement.CanPerform(Owner.Target)` and return
`RequirementsNotMet` (2) on the first failure; otherwise return
`OnPerformAction()`. The four-value enum
`BaseAction.ActionCompleteStates` is the whole interpreter protocol:

| Value | Name | Sequence reaction |
|---:|---|---|
| 0 | `InComplete` | Keep the action live; run it again next tick |
| 1 | `InCompleteRefund` | With `IgnoreRefund`: treat as complete. Else, if `AllowRefunds` and the sequence is a `TwitchAction`: refund the requester (local: `HandleTwitchRefundNeeded`; remote: response `TwitchRefundNeeded`) and end the whole sequence. Other action types: just mark the action complete |
| 2 | `RequirementsNotMet` | Mark complete; jump to `PhaseOnDenied` if set |
| 3 | `Complete` | Mark complete; jump to `PhaseOnComplete` if set |

```mermaid
stateDiagram-v2
  [*] --> Armed: Init / Reset<br/>(IsComplete = false)
  Armed --> Gating: sequence tick,<br/>Phase == CurrentPhase
  Gating --> DeniedOut: any requirement false<br/>return RequirementsNotMet(2)
  Gating --> Executing: all requirements pass<br/>OnPerformAction()
  Executing --> Armed: InComplete(0)<br/>same phase next tick
  Executing --> CompleteOut: Complete(3)
  Executing --> RefundOut: InCompleteRefund(1)
  RefundOut --> CompleteOut: IgnoreRefund set
  RefundOut --> SequenceRefund: AllowRefunds &&<br/>ActionType == TwitchAction
  RefundOut --> Done: other ActionTypes<br/>(mark complete, no jump)
  CompleteOut --> Jump1: PhaseOnComplete != -1
  DeniedOut --> Jump2: PhaseOnDenied != -1
  CompleteOut --> Done
  DeniedOut --> Done
  Jump1 --> Done: sequence phase jump +<br/>Reset all actions with Phase >= target
  Jump2 --> Done
  Done --> Armed: Reset() on phase jump / loop repeat
  Done --> [*]: sequence ends
  SequenceRefund --> [*]: sequence IsComplete,<br/>requester refunded
```

The 60-second inactivity refund (§2, step 2) injects state 1 from the outside,
so a stalled Twitch event gives the viewer their points back instead of
spinning forever.

---

## 4. Requirement gating

`BaseRequirement` is a pure predicate: `Owner` (set to the owning sequence just
before evaluation), `CanPerform(Entity target)` (default true), an `invert`
property parsed at the base and applied by each leaf, plus the same
`ParseProperties` / `Init` / `Clone` template as actions. Requirements gate at
two levels with identical semantics (all must pass):

- **Sequence level** (`GameEventActionSequence.CanPerform`): checked once at
  `HandleAction` approval time, together with every action's `CanPerform`.
- **Action level** (`BaseAction.PerformAction`): checked every tick before
  `OnPerformAction`; failure returns `RequirementsNotMet`.

`BaseOperationRequirement` is the comparison workhorse: subclasses supply
`LeftSide(target)` / `RightSide(target)` objects; the base compares them as
strings or floats under an `operation` property. The `OperationTypes` enum
accepts three spellings per operator (`Equals`/`EQ`/`E`, `NotEquals`/`NEQ`/`NE`,
`Less`/`LessThan`/`LT`, `Greater`/`GreaterThan`/`GT`, `LessOrEqual`/...`/LTE`,
`GreaterOrEqual`/...`/GTE`); the right side resolves through
`GameEventManager.GetIntValue`/`GetFloatValue`, so `value` strings can name
cvars or event variables instead of literals.

The 37 leaves by category:

| Category | Requirements |
|---|---|
| Target entity state | `FullHealth`, `HasBuff`, `HasBuffByTag`, `HasEntityTag`, `HasHeld`, `InVehicle`, `IsIndoors`, `NearbyEntities` |
| Location | `InBiome`, `InPOI`, `InQuestZone`, `InSafeZone`, `InTraderArea`, `IsBlock` |
| Progression / quests | `Gamestage`, `Progression`, `OnQuest` |
| World / settings | `GameStatBool`, `GameStatFloat`, `GameStatInt`, `SandboxBool`, `SandboxFloat`, `SandboxInt`, `IsWeatherGracePeriod`, `EventActive` |
| Sequence state | `GroupLiveCount`, `HasSpawnedEntities`, `HasSequenceLink`, `VarBool`, `VarFloat`, `VarInt`, `VarString` |
| Misc | `CVar`, `RandomRoll`, `HasParty`, `IsTwitchActive`, `IsHomerunActive` |

`RequirementCVar` is representative: `LeftSide` reads the target's buff cvar,
`RightSide` resolves the `value` text, the base compares under `operation`.

---

## 5. Decisions and loops (nested control flow)

`BaseDecision` and `BaseLoop` are themselves `BaseAction`s that contain a child
action list and replicate the sequence phase machine one level down
(`currentPhase` / `phaseMax`, same `ActionCompleteStates` dispatch, same
jump-and-reset rules; a child's `InCompleteRefund` with sequence `AllowRefunds`
propagates straight up). Both disable their own requirement gate
(`UseRequirements` = false) because their `Requirements` list is repurposed as
the **condition** under a `condition_type` property (`Any`=0 / `All`=1,
default `All`).

- **`DecisionIf`**: on first execution latches `runActions = CheckCondition()`.
  False: return `Complete` immediately (the block is skipped). True: run the
  child phase machine each tick until it returns `Complete`, then unlatch and
  return `Complete`.
- **`LoopWhile`**: same latch, but when the child machine completes it resets
  every child and re-evaluates the condition next tick; it only returns
  `Complete` when the condition check comes back false.
- **`LoopFor`**: resolves `loop_count` once at first execution (through
  `GetIntValue`, so it can be a cvar or variable), then runs the child machine;
  each child completion increments `currentLoop`, resets the children, and the
  loop returns `Complete` when `currentLoop >= loopCount`.
- **`BaseWait` / `WaitUntil` / `WaitWhile`** (in `SequenceActions`): degenerate
  loops with no children; they return `InComplete` each tick until their
  requirement condition flips, then `Complete`. `ActionDelay` is the timed
  equivalent.

```mermaid
stateDiagram-v2
  [*] --> Idle
  Idle --> Check: PerformAction (tick)
  Check --> Skipped: DecisionIf, condition false<br/>return Complete(3)
  Check --> ChildPhase: condition true (latched)
  state ChildPhase {
    [*] --> RunPhase
    RunPhase --> RunPhase: child actions of currentPhase<br/>same ActionCompleteStates dispatch
    RunPhase --> RunPhase: empty pass -> currentPhase++<br/>or PhaseOnComplete/Denied jump + Reset
    RunPhase --> [*]: currentPhase >= phaseMax
  }
  ChildPhase --> Refund: child InCompleteRefund &&<br/>Owner.AllowRefunds (propagate up)
  ChildPhase --> IterDone: child machine Complete
  IterDone --> Finished: DecisionIf (one shot)
  IterDone --> Recheck: LoopWhile: Reset children,<br/>re-evaluate condition
  IterDone --> Count: LoopFor: currentLoop++,<br/>Reset children
  Recheck --> ChildPhase: condition still true
  Recheck --> Finished: condition false
  Count --> ChildPhase: currentLoop < loopCount
  Count --> Finished: currentLoop >= loopCount
  Finished --> [*]: return Complete(3)
  Skipped --> [*]
  Refund --> [*]: return InCompleteRefund(1)
```

Because a decision or loop returns `InComplete` while its children run, the
parent sequence keeps re-entering it every tick; the nesting recurses (children
can themselves be decisions/loops), giving a full tree-walking interpreter with
per-node persistent state instead of a call stack.

---

## 6. The action zoo: bases and representative leaves

132 `SequenceActions` types resolve to nine abstract bases plus ~120 verbs. Do
not read them all; the bases carry the behavior:

| Base | Contract | Leaves (examples) |
|---|---|---|
| `BaseAction` | §3 | `ActionKill`, `ActionAddBuff`, `ActionSetDayTime`, `ActionSetWeather`, `ActionSetStorm`, `ActionSetHordeNight`, `ActionSetEventFlag`, `ActionCallGameEvent`, `ActionDelay`, `ActionModifyVarInt/Float/Bool`, group management (`ActionAddPlayerToGroup`, `ActionAddEntitiesToGroup`, `ActionClearGroup`, ...) |
| `ActionBaseSpawn` | Three-state spawn machine (below) | `ActionSpawnEntity`, `ActionSpawnEntitySpawner`, `ActionSpawnContainer` |
| `ActionBaseTargetAction` | Iterate an entity group, one entity per tick | `ActionPlaySound`, `ActionReplaceEntities`, `ActionTeleportToTarget` |
| `ActionBaseClientAction` | Server half + mirrored client half (below) | `ActionShowWindow`, `ActionCloseWindow`, `ActionShowMessageWindow`, `ActionBeltTooltip`, `ActionSetScreenEffect`, `ActionPauseBuff` |
| `ActionBaseItemAction` | Player inventory edits | `ActionAddItems`, `ActionRemoveItems`, `ActionReplaceItems`, `ActionDropItems`, `ActionAddItemDurability`, `ActionUnloadItems` |
| `ActionBaseBlockAction` | Block edits around the target | `ActionBlockUpgrade/Downgrade/Replace/Health/DoorState/AnimateBlock/TriggerFall/TriggerMines/GrowCrops`, `ActionFillArea`, `ActionFillSafeZone` |
| `ActionBaseContainersAction` | Loot container sweeps | `ActionEmptyContainers`, `ActionShuffleContainers`, `ActionReplaceItemsContainers` |
| `ActionBaseTeleport` | Position resolution + teleport | `ActionTeleport`, `ActionTeleportNearby`, `ActionRandomTeleport`, `ActionTeleportToSpecial` |
| `BaseWait` | Condition-holding wait (§5) | `WaitUntil`, `WaitWhile`, plus `ActionWaitForDead` |

Remaining families: progression rewards (`ActionAddXP`, `ActionAddSkillPoints`,
`ActionAddPlayerLevel`, `ActionAddQuest`, `ActionCompleteChallenge`), world
resets (`ActionPOIReset`, `ActionResetRegions`, `ActionResetSleepers`,
`ActionResetMap`, `ActionResetPlayerData`), boss/mini-game glue
(`ActionSetupBossGroup`, `ActionUpdateBossGroup`, `ActionStartHomerun`), and
eight `ActionTwitch*` types (points, cooldowns, votes, channel messages).

**`ActionBaseTargetAction`** shows the incremental style: on first tick it
snapshots `Owner.GetEntityGroup(targetGroup)` into `targetList`, then each tick
applies `PerformTargetAction` to one entity (skipping dead/despawned), returning
`InComplete` until the index runs off the end. Without a `targetGroup` it
applies once to the sequence `Target`.

The `EntityGroups` dict backing that snapshot: `AddEntityToGroup(name, e)`
(IL=35) skips TwitchAction sequences' players whose `TwitchActionsEnabled`
isn't 1, then get-or-creates the list and appends;
`GetEntityGroupLiveCount(name)` (IL=44) counts alive `EntityAlive` members;
`ClearEntityGroup(name)` (IL=15) clears the list (no-op when absent).

**`ActionBaseClientAction`** is the server/client split: `PerformTargetAction`
runs `OnServerPerform`, then either calls `OnClientPerform` directly (listen
host) or sends `NetPackageGameEventResponse` with `ClientSequenceAction` (12)
and the action key to the target player; the receiving client resolves the key
through `GameEventManager.HandleGameEventSequenceItemForClient` ->
`BaseAction.FindKey(key).OnClientPerform`. Fire-and-forget: it returns
`Complete` immediately.

**`ActionBaseSpawn`** (48 fields, 829-IL `OnPerformAction`) is the largest
action and carries its own explicit state field `SpawnUpdateTypes CurrentState`:

```mermaid
stateDiagram-v2
  [*] --> NeedSpawnEntries: OnPerformAction first tick
  NeedSpawnEntries --> NeedPosition: pick entities<br/>(entityNames / entity group, count,<br/>party addition, spawn multiplier)
  NeedPosition --> NeedPosition: FindValidPosition retry<br/>(min/max distance, raycast, air/safe)
  NeedPosition --> SpawnEntities: position accepted
  SpawnEntities --> SpawnEntities: spawn one entity per tick,<br/>RegisterSpawnedEntity, add to groups
  SpawnEntities --> [*]: currentCount == count<br/>return Complete
```

Its `CanPerform` is the approval-time budget gate: it resolves `count`, then
denies the whole event when `CurrentCount + count > MaxSpawnCount`
(`MaxSpawnCount` = 20 in the ctor; `CurrentCount` = live tracked spawns +
`ReservedCount` held by running sequences) or when the target is dead or the
spawn area cannot accept blocks (for non-safe spawns).

**`ActionBaseSpawn.SpawnEntity(entityId, target, startPoint, minDistance,
maxDistance, spawnInSafe, yOffset)` (IL=84)** is the per-entity commit the
SpawnEntities state runs once per tick. Position comes from
`FindValidPosition(ref pos, ...)` (8-arg overload, IL=150): a random
horizontal direction `dir = normalize(2r-1, 0, 2r-1)` and a random distance
`min + r*(max-min)` give `pos = startPoint + dir*dist`, then `y += 1.5` plus
`yOffset` when non-zero; a `Voxel.Raycast` from `startPoint + dir*raycastOffset`
toward `pos` (layer mask `-538750989`) rejects the spot on any terrain hit;
the block at `pos - rayDir*0.5` must not collide movement or arrows; when
`!spawnInSafe` the spot must pass `World.CanPlaceBlockAt(pos, null, false)`;
when `!spawnInAir` a `3 + yOffset` ray down must hit ground, snapping `pos`
to the hit point. The commit then builds
`EntityFactory.CreateEntity(entityId, pos + (0, 0.5, 0), rot, ownerId,
owner.ExtraData)` where `rot` faces the target (`target.transform.eulerAngles.y
+ 180`) or is zero, and `ownerId` is the target's entity id when
`owner.TwitchActivated` and the target exists, else `-1`; `SetSpawnerSource(3)`
(Dynamic); `World.SpawnEntityInWorld`; and
`BroadcastPlayByLocalPlayer(entity.position, spawnSound)` when a sound is set.
Position failure returns null and the machine stays in NeedPosition to retry.

**`ActionRespawnEntity` (IL=213) / `ActionRespawnEntities` (IL=254)** are the
respawn verbs (`respawnEntity` / `respawnEntities`). The single-entity
variant snapshots the old class/id/position/rotation of a non-player target
on its first tick, then waits out `delay` (counted down by `deltaTime`, while
still delaying it returns `InComplete`). On expiry it commits:
`EntityFactory.CreateEntity(oldClass, oldPos, oldRot, target.entityId,
extraData)` (null -> `Complete`, no respawn), `SetSpawnerSource(3)`
(Dynamic), `World.SpawnEntityInWorld`, `World.RemoveEntity(oldId, Killed)`,
and re-points the sequence `Target` at the new entity. When the old target
was an `EntityAlive`, it also `RegisterSpawnedEntity(new, old, requester,
owner, true)` and issues `SetAttackTarget(old, **12000**)` - a 12 s reaction
window on the replacement. The requester is then notified (in-process
`HandleGameEntitySpawned` locally, `NetPackageGameEventResponse(EntitySpawned
= 5)` on 192 remotely), each `AddToGroups` entry goes through
`AddEntityToGroup`, and `Audio.Manager.BroadcastPlayByLocalPlayer(oldPos,
respawnSound)` plays when a sound is set; success returns `Complete`. The
plural variant snapshots `Owner.GetEntityGroup(targetGroup)` into a private
`entityList` (missing group: `Debug.LogWarning` and `InCompleteRefund`), then
per `checkTime` expiry respawns **one** dead entity per tick with the same
commit and removes it from the list (`InComplete` while it keeps working).

**`ActionReplaceEntities.PerformTargetAction` (IL=163)** swaps a live,
non-player target for a new instance of a class picked from the configured
`entityIDs` list (`Random.Range(0, count)` unless `selectedEntityIndex >= 0`
pins one). The commit is the respawn pipeline again: `CreateEntity(classId,
target.position, target.rotation, owner.Target?.entityId ?? -1,
owner.ExtraData)`, `SetSpawnerSource(3)` (Dynamic), spawn, and the new entity
goes onto the action's `newList`. With `attackTarget` set and both sides
`EntityAlive` it registers the replacement
(`RegisterSpawnedEntity(new, old, requester, owner, true)`),
`SetAttackTarget(old, 12000)` (the same 12 s window), and also
`new.aiManager.SetTargetOnlyPlayers(100)` - a player-only targeting override
at 100 m on the spawned AI. Requester notification follows the same pattern
(remote: `NetPackageGameEventResponse(EntitySpawned = 5, ...)` on 192), then
`HandleRemoveData(target)` and a `removeLater(target)` coroutine retires the
old entity; returns `Complete`.

---

## 7. Server driver, tracking, and net plumbing

`GameEventManager.Update` runs in the `gmUpdate` manager chain
([`loop-gmupdate.md`](loop-gmupdate.md), step 5;
[`managers.md`](managers.md)) and fans into five bookkeeping passes plus the
sequence tick of §2:

| Pass | Tracks | Behavior (IL-observed) |
|---|---|---|
| `HandleSpawnUpdates` | `spawnEntries` (spawned entity, requester, owning sequence) | 2 s cadence while the list is non-empty; reaps despawned entries (flags `HasDespawn` on the owning sequence) and dead or model-less entries, notifying the requester (`EntityDespawned` / `EntityKilled`) in-process or via `NetPackageGameEventResponse` on 192; the per-entry re-aggro pass exists but is inert on b14 (§7.1) |
| `HandleBlockUpdates` | `blockEntries` (`SpawnedBlocksEntry`) | Counts down `TimeAlive` (`-1` = permanent) and bulk-removes expired event blocks (`TryRemoveBlocks`); periodic block-damage sync |
| `HandleEventFlagUpdates` | `GameEventFlags` (`GameEventFlagTypes`: BigHead, Dancing, BucketHead, TinyZombies, ...) | 1 s cadence; timed global flags with buff application on flag change |

`HandleFlagBuffUpdates(flag, deltaTime)` (IL=69) is the buff side of that 1 s
cadence: it counts `gameFlagCheckTime` down and, on expiry, maps the flag
(1 = BigHead, 2 = Dance, 3 = BucketHead, 4 = TinyZombies) to its
`twitch_buff*` name and `AddBuff(name, -1, true, false, -1)` on every player
that does not already have it, then resets the timer to 1.
| `HandleBossGroupUpdates` | `BossGroups` | 1 s cadence; boss + minion HP groups, client HUD sync (`SetupClientBossGroup` / `SendBossGroups`) |
| `HomerunManager.Update` | mini-game | `GameEvent.GameEventHelpers` |

`Cleanup`/`ClearActions` (game shutdown / XML reload) clear the running list,
the template dictionary, and all tracked entries.

### 7.1 Spawn-entry tracking: reap vs re-aggro

`GameEventManager.Update` (IL=25) is gated on `IsServer` **and** a live world;
with no world the whole fan-out is skipped. `HandleSpawnUpdates` (IL=148)
only counts its `attackTimerUpdate` down while `spawnEntries` is non-empty,
resetting it to **2** s on expiry (that reset value is what gates the
re-aggro pass, `loc.0`). Every entry is then processed backwards:

- **Despawned** (`Entity.IsDespawned`): sets `GameEvent.HasDespawn = true` on
  the owning sequence, removes the entry, and notifies the requester. A local
  requester gets the in-process `HandleGameEntityDespawned(entityId)`; a
  remote one gets `NetPackageGameEventResponse(EntityDespawned = 6,
  entityId, -1, "", false)` on channel 192.
- **Dead or model-less** (`!IsAlive()` or `emodel == null`): removes the
  entry, then `HandleGameEntityKilled(entityId)` locally or
  `NetPackageGameEventResponse(EntityKilled = 7, ...)` remotely on 192.
- Otherwise, when the 2 s timer fired: `SpawnEntry.HandleUpdate()`.

**`RegisterSpawnedEntity(spawned, target, requester, gameEvent, isAggressive)`
(IL=19)** appends a `SpawnEntry{SpawnedEntity, Target, Requester, GameEvent}`
to the list and **drops the `isAggressive` argument**: the body stores only
four fields (IL is 19 instructions end to end) and nothing else in the
assembly ever writes `SpawnEntry.IsAggressive`. RefScan finds zero references
to the nested `GameEventManager/SpawnEntry` type outside `GameEventManager`
itself, and inside it the field is only ever read. All five callers do pass a
value (the four spawn/respawn/replace/twitch actions pass `true`;
`ActionBaseSpawn.OnPerformAction` passes its XML-parsed `isAggressive` field,
`PropIsAggressive`), so the flag is dropped at the boundary on purpose or by
regression. Consequence: the re-aggro branch of `SpawnEntry.HandleUpdate`
(IL=32: when `IsAggressive`, `SetAttackTarget(World.GetClosestPlayer(entity,
500, false), 1000)`; with an existing player target it re-issues
`SetAttackTarget(player, 1000)`) is **structurally dead on V3.1.0 b14** - the
500 m search and 1000 ms reaction time are the intended behavior, not what a
stock server runs. The spawn-entry machinery's real work on b14 is the
despawn/death reap and the requester notification above.

### 7.2 Block-entry tracking (event-placed blocks)

`HandleBlockUpdates` (IL=53) reaps `blockEntries` backwards: an entry with
`TimeAlive > 0` counts down by `deltaTime`; `TimeAlive == -1` is permanent
and skipped; on expiry (`<= 0`) it tries `TryRemoveBlocks()` - success
removes the entry, failure resets `TimeAlive = 5` for a retry in 5 s. Entries
flagged `IsRefunded` are dropped regardless.

`SpawnedBlocksEntry` (ctor IL=16) defaults `TimeAlive = -1` (permanent) and
assigns a monotone `BlockGroupID` from a static counter (`++newID`).
`TryRemoveBlocks()` (IL=111) walks the block list backwards and, for every
position whose chunk is loaded (`GetChunkFromWorldPos`), appends
`BlockChangeInfo(pos, BlockValue.Air, true)` to a batch and removes the entry
from the list; any pending changes go out through `World.SetBlocksRPC` (the
ChangeBlocks machine, [`blocks.md`](blocks.md) §4.1). Once the list empties,
it plays `RemoveSound` at `Center` (`BroadcastPlayByLocalPlayer`), calls
`GameEvent.SetRefundNeeded()` when `RefundOnRemove`, and notifies the
requester: local `HandleGameBlocksRemoved(BlockGroupID, IsDespawn)`, remote
`NetPackageGameEventResponse(BlocksRemoved = 9, -1, BlockGroupID, "",
IsDespawn)` on 192. Its return value is `BlockList.Count == 0`, the signal
`HandleBlockUpdates` uses to reap the entry or retry.
`RegisterSpawnedBlocks` (IL=32) stores all eight fields
(`BlockList, Target, Requester, GameEvent, TimeAlive, RemoveSound, Center,
RefundOnRemove`) and returns the new entry.

**Early-destruction refunds:** `RefundSpawnedBlock(pos)` (IL=32) is the hook
for a player destroying a tracked event block before its timer: it finds the
first entry whose `BlockList` contains `pos`, calls
`GameEvent.SetRefundNeeded()` and marks `IsRefunded = true` (reaped by the
next `HandleBlockUpdates`). `RemoveSpawnedEntry(entity)` (IL=73) is the
entity-side equivalent: matching `SpawnedEntity` -> `GameEvent.HasDespawn =
true`, entry removed, and the requester notified with `EntityDespawned` (6)
on 192, exactly like the despawn branch of `HandleSpawnUpdates`.

**Flag store:** `SetGameEventFlag(flag, value, duration, isPermanent)` (IL=94)
adds a `GameEventFlag` to `GameEventFlags` when setting (updating the duration
of an existing non-permanent entry, otherwise appending a new one and calling
`HandleFlagChanged(flag, true, true)`), and `RemoveAt`s the entry when clearing
(`HandleFlagChanged(flag, true, false)`). `CheckGameEventFlag(flag)` (IL=23)
is a linear presence scan of the list.

Request/response wire flow (packages annotated in
[`protocol.md`](protocol.md)):

```mermaid
sequenceDiagram
  participant C as Client (or Twitch via server)
  participant S as GameEventManager (server)
  participant T as Target player's client
  C->>S: NetPackageGameEventRequest(eventName, entityID, target, variables, ...)
  S->>S: gate: target is sender or in sender's party
  S->>S: HandleAction: template lookup, CanPerform, SingleInstance, Clone
  alt approved
    S->>C: NetPackageGameEventResponse Approved (1)
    loop per tick while running
      S->>T: ClientSequenceAction (12) for ActionBaseClientAction leaves
      S->>C: EntitySpawned/Killed/Despawned, Blocks* (5..11) tracking events
    end
    S->>C: Completed (13) or TwitchRefundNeeded (3)
  else denied
    S->>C: NetPackageGameEventResponse Denied (0)
  end
```

`NetPackageGameEventResponse.ResponseTypes` doubles as the event vocabulary the
manager also raises in-process (C# events `GameEventApproved`, `GameEventDenied`,
`GameEventCompleted`, `TwitchRefundNeeded`, `GameEntitySpawned/Despawned/Killed`,
`GameBlocksAdded/Removed`), which is how the Twitch integration, quest
objectives (`ObjectiveGameEvent`), and the event UI observe outcomes without
polling. Sequence links (`RegisterLink` / `GetSequenceLink`) let a later
`HandleAction` attach a new sequence to a still-running owner sequence by
player + tag, inheriting its requester/refund context.
`GetSequenceLink(player, tag)` (IL=38) linear-scans `SequenceLinks` for a
`CheckLink(player, tag)` match and returns the owner sequence (null for a null
player/empty tag or no match); `GetTargetType(name)` (IL=11) reads
`GameEventSequences[name].TargetType`, defaulting to enum 0 on a missing key.
`RegisterLink(player, seq, tag)` (IL=35) keeps an existing matching link
(first link wins) and otherwise appends `SequenceLink{Owner, OwnerSeq, Tag}`;
`UnRegisterLink(player, tag)` (IL=25) removes the first matching link.

Variable plumbing has one observed quirk: `HandleAction` writes incoming
`variables` into the **template's** `EventVariables` store before cloning, and
`Clone()` does not copy the `eventVariables` reference, so per-request values
live on the shared template object while `RequirementVar*` / `ActionModifyVar*`
leaves read `Owner.EventVariables` (the clone's lazily created store). Runtime
numeric properties (`loop_count`, spawn counts, comparison values) instead
resolve lazily through `GetIntValue`/`GetFloatValue`, which accept literals,
cvars, or variables at evaluation time.

---

## 8. Dedicated relevance and residuals

- **Runs on dedicated, server-authoritative.** `Update` is gated on
  `IsServer`; clients only send requests and execute mirrored
  `ClientSequenceAction` halves plus HUD/boss-bar sync.
- **Idle cost is near zero:** with no running sequences the five passes iterate
  empty lists ([`entity-ai.md`](entity-ai.md) records the 25-IL `Update` shell
  in the manager-chain cost table). The engine only becomes hot while events
  run, and spawns are capped by the `MaxSpawnCount` budget.
- **Content, not IL:** which sequences exist, their phases, actions, and
  properties are `gameevents.xml` data; this doc covers the interpreter only.
- **External (residuals):** the Twitch chat/PubSub service that triggers
  `TwitchAction` events; XUi widgets rendering event UI client-side. See
  [`residuals.md`](residuals.md).

---


## Boss / request packages (verified)

### `NetPackageBossEvent` (write IL=53)

```text
bossGroupID : i32
eventType : u8
bossGroupType : u8
entityID : i32
bossIcon1 : string
// if eventType == SetupClient (1):
  minionCount : i32
  minionIDs : i32 x count
```

Process switch: SendBossGroups, SetupClientBossGroup, UpdateBossGroupType, remove/add nav, etc.

### `NetPackageGameEventRequest` / `Response`

Request write IL=83, Process IL=211 (server approve/start sequences).
Response write IL=102, Process IL=135 (client sequence/entity spawn feedback).
Full field lists in inventories/netpackage-bodies.md; tick pipeline above.

## Related docs

| Doc | Role |
|---|---|
| [`full-surface.md`](full-surface.md) | Where `GameEvent.*` sits in the whole-assembly map |
| [`loop-gmupdate.md`](loop-gmupdate.md) | The manager chain that ticks `GameEventManager.Update` |
| [`managers.md`](managers.md) | Sibling in-process managers |
| [`protocol.md`](protocol.md) | Wire framing; `NetPackageGameEventRequest`/`Response` context |
| [`entity-ai.md`](entity-ai.md) | Spawned-entity behavior once an event spawns something |
| [`re-methodology.md`](re-methodology.md) | How this was reversed |
| [`residuals.md`](residuals.md) | External/native residuals |

**Leaf catalog:** every instance in [`inventories/sequence-requirements.md`](inventories/sequence-requirements.md) (all 37 concrete requirement leaves).

## Changelog

- **2026-08-08:** Spawn-entry tracking (7.1) + respawn verbs: HandleSpawnUpdates
  (IL=148) 2 s reap cadence, HasDespawn flag, EntityDespawned (6) / EntityKilled
  (7) requester notify on 192; RegisterSpawnedEntity (IL=19) drops its
  isAggressive argument (all 5 callers pass a value, ActionBaseSpawn from
  PropIsAggressive XML) and nothing writes SpawnEntry.IsAggressive, so
  HandleUpdate's 500 m / 1000 ms re-aggro is structurally dead on b14;
  ActionRespawnEntity (IL=213) / ActionRespawnEntities (IL=254) snapshot,
  delay/checkTime gates, CreateEntity + SetSpawnerSource 3 + RemoveEntity
  (Killed), 12000 ms retarget, Spawned (4) notify, AddToGroups, respawnSound;
  Update (IL=25) IsServer + world gate.
- **2026-08-08:** SpawnEntity (IL=84) commit + FindValidPosition (IL=150):
  random dir/dist, y+1.5, mask -538750989 raycast, ground snap, facing rot,
  TwitchActivated ownerId; block-entry tracking (7.2): HandleBlockUpdates
  (IL=53) reap/retry-5s, SpawnedBlocksEntry TryRemoveBlocks (IL=111) Air batch
  via SetBlocksRPC + BlocksRemoved (9) notify + refund on remove,
  RefundSpawnedBlock (IL=32) SetRefundNeeded + IsRefunded, RemoveSpawnedEntry
  (IL=73) entity-side despawn reap.
- **2026-08-08:** ActionReplaceEntities (IL=163): entityIDs pick (selected
  index or Random.Range), SetTargetOnlyPlayers(100), 12000 ms retarget,
  EntitySpawned (5) notify, removeLater coroutine; response enum values pinned
  (Denied 0 .. Completed 13, EntitySpawned = 5).
- **2026-08-07:** StartSequence IL=4 stamps Time.time only.

- **2026-07-28:** BossEvent wire; GameEventRequest/Response pointers.

- **2026-07-23:** Initial `GameEvent.*` reversal: manager driver + template
  registry, sequence phase machine, `ActionCompleteStates` action protocol,
  requirement gating, decision/loop nested interpreters, spawn state machine,
  and request/approval net flow, with state diagrams for each machine.
