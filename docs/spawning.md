# Entity spawning subsystem (dedicated V3.0.1)

**Owns:** how entities are placed INTO the world: the spawn-manager family
(`SpawnManagerBiomes`, `SpawnManagerDynamic`, `SpawnManagerAbstract`), the
per-chunk-area biome budget (`ChunkAreaBiomeSpawnData`), the wave/static/sleeper
spawner (`EntitySpawner`), the chunk-heat scout and screamer hordes
(`AIDirectorChunkEventComponent`, `AIHordeSpawner`), player spawn points
(`SpawnPointList`), and prefab placement (`DynamicPrefabDecorator`). Also: how a
decided spawn becomes a live entity and reaches clients.
**Not:** the per-entity tick, AI decisions, or pathfinding once an entity exists
(those are [`entity-ai.md`](entity-ai.md)); the blood-moon and wandering-horde
director components themselves ([`aidirector.md`](aidirector.md)); the
`NetPackageEntitySpawn` wire layout ([`protocol-packages.md`](protocol-packages.md) §5.1);
XML spawn content (data, not loop IL).
**Evidence:** `SpawnManagerBiomes`, `SpawnManagerDynamic`, `EntitySpawner`,
`AIHordeSpawner`, `ChunkAreaBiomeSpawnData`, `AIDirectorChunkEventComponent`,
`SpawnPointList`, `DynamicPrefabDecorator` IL (global namespace; dump locally by
type name with `tools/bin/DumpMethod`, git-ignored).
**Hub:** [`INDEX.md`](INDEX.md). **Method:** [`re-methodology.md`](re-methodology.md).

This is authoritative server logic: every spawn decision below runs on the
dedicated host. Clients never decide spawns; they receive the resulting entity
through interest management (§7).

---

## 1. Architecture: five spawn sources, one placement path

Spawning is not a single system. Five independent drivers each decide "what,
where, when", then all funnel through the same two placement calls
(`World.SpawnEntityInWorld` or the async `Chunk.SpawnEntityAsync`) and tag the
new entity with an `EnumSpawnerSource` so the correct accounting owner can later
decrement its budget.

| Driver | Type | Trigger | Source tag | Budget owner |
|---|---|---|---|---|
| Biome wandering spawns | `SpawnManagerBiomes` | per active chunk-area, from `World.OnUpdateTick` | `Biome` (1) | `ChunkAreaBiomeSpawnData` |
| Dynamic night spawns | `SpawnManagerDynamic` | once per in-game day, night only | `Dynamic` (3) | `EntitySpawner` wave state |
| POI / static / sleeper spawners | `EntitySpawner` | per spawner class + day + time-of-day | `StaticSpawner` (2) or `Dynamic` (3) | `EntitySpawner` wave state |
| Chunk-heat scouts + follow-up hordes | `AIDirectorChunkEventComponent` -> `AIScoutHordeSpawner` | activity heat map, 5 s cadence | `Dynamic` (3) | scout/horde list |
| Screamer-summoned horde | `AIHordeSpawner` | screamer sense event | `Dynamic` (3) | `AIDirectorGameStagePartySpawner` |

```mermaid
flowchart TB
  subgraph tick[Server tick]
    OUT[World.OnUpdateTick per active chunk-area]
    DIR[AIDirector.ComponentsTick]
  end
  OUT --> SMB[SpawnManagerBiomes.SpawnUpdate]
  OUT --> SMD[SpawnManagerDynamic.Update night once/day]
  DIR --> CEC[AIDirectorChunkEventComponent.Tick heat map]
  CEC --> SCOUT[AIScoutHordeSpawner]
  SCR[Screamer sense] --> AHS[AIHordeSpawner.Tick]
  SMB --> PLACE
  SMD --> ES[EntitySpawner.SpawnManually]
  SCOUT --> ES
  ES --> PLACE
  AHS --> PLACE[World.SpawnEntityInWorld / Chunk.SpawnEntityAsync]
  PLACE --> ND[NetEntityDistribution.Add]
  ND --> NET[per-player NetPackageEntitySpawn on entry]
```

All five share the same global gate: `AIDirector.CanSpawn(1.0)`, which is simply
`GameStats.EnemyCount < GamePrefs.MaxSpawnedZombies * priority`. This is the
server-wide living-zombie cap; when it is hit, biome enemy spawns fall back to
animals-only and the horde/dynamic paths abort for the tick.

---

## 2. The biome spawn decision cycle (`SpawnManagerBiomes.SpawnUpdate`)

This is the main wandering-population loop. A "chunk-area" is a 5x5 block of
chunks: `ChunkAreaBiomeSpawnData` covers an 80 m by 80 m `Rect` anchored at the
master chunk origin. `World.OnUpdateTick` calls
`SpawnManagerBiomes.Update(name, spawnEnemies, chunkAreaSpawnData)` once per
active area, which forwards to `SpawnUpdate` unless the world is playtesting.

The single `SpawnUpdate` call decides at most ONE spawn. It is gated at every
step and returns early the instant any gate fails.

```mermaid
flowchart TB
  A[SpawnUpdate area] --> B{enemy request?}
  B -->|yes| C{AIDirector.CanSpawn<br/>and not blood moon?}
  C -->|no| D[demote to animals-only]
  C -->|yes| E
  B -->|no| F{AnimalCount<br/>&lt; MaxSpawnedAnimals?}
  F -->|no| STOP[return, no spawn]
  F -->|yes| E
  D --> F
  E[find nearby player] --> G{any player rect<br/>overlaps this area?}
  G -->|no| STOP
  G -->|yes| H[GetRandomSpawnPositionInAreaMinMaxToPlayers<br/>enemy 28..54 m, animal 48..70 m]
  H -->|no valid pos| STOP
  H --> I[resolve biome group list<br/>+ day/night]
  I --> J[first pass only: scan POIs in area,<br/>set poiTags + groupsEnabledFlags]
  J --> K[pick random start, scan up to min 5 groups]
  K --> L{group enabled,<br/>daytime match,<br/>enemy/animal match?}
  L -->|no| K
  L -->|yes| M[respawn-delay elapsed?<br/>ResetRespawn maxCount]
  M --> N{ChunkAreaBiomeSpawnData.CanSpawn<br/>count &lt; maxCount?}
  N -->|no| K
  N -->|yes| O{any entity within<br/>4 x 2.5 x 4 of pos?}
  O -->|yes| STOP
  O -->|no| P[GetRandomFromGroup -> classId]
  P -->|fail| Q[DecMaxCount, return]
  P --> R[IncCount, SetupEntityCreationData]
  R --> S[Chunk.SpawnEntityAsync -> OnEntitySpawned<br/>SetSpawnerSource Biome + chunkKey + biomeIdHash]
```

Key facts read from the IL:

- **Player gating.** For each spawned player, an 80 m by 80 m `Rect` centered on
  the player (position minus 40 on x and z) is tested against the area. If no
  player rect overlaps, the area does not spawn. Biome population therefore
  tracks players, not the whole map.
- **Blood-moon demotion.** If `AIDirectorBloodMoonComponent.BloodMoonActive`,
  the enemy request is demoted to animals-only; blood-moon enemies come from the
  director party, not the biome loop.
- **Placement ring.** Positions are drawn in a min/max distance band to the
  nearest players: 28..54 m for enemies, 48..70 m for animals, so wandering
  spawns appear off-camera but nearby.
- **Group selection.** The biome group list (`BiomeSpawnEntityGroupList`, keyed
  by biome name) is scanned from a random start for up to `min(5, count)` groups.
  A group must be enabled by POI tags, match the current `EDaytime`
  (`Any`, `Day`, `Night`), and match the enemy/animal request.
- **POI-tag enabling (once).** The first time an area is evaluated, overlapping
  prefab instances are unioned into `poiTags`, and each group's `POITags` /
  `noPOITags` set the `groupsEnabledFlags` bitmask. This is why POI-tagged
  spawn groups only fire inside the matching prefab footprints.
- **Anti-stacking.** A `GetEntitiesInBounds` over a small 4 x 2.5 x 4 box around
  the chosen position aborts the spawn if anything is already there.
- **Difficulty scaling.** Enemy `maxCount` passes through
  `EntitySpawner.ModifySpawnCountByGameDifficulty` before the respawn reset.
- **Async placement.** The spawn is created off the main flow via
  `Chunk.SpawnEntityAsync` (through `EntityAsyncManager.StartCreateEntity`); the
  completion callback runs `OnEntitySpawned`, stamping
  `SetSpawnerSource(Biome, masterChunkKey, biomeIdHash)`.

---

## 3. Per-chunk-area caps, cooldown, and kill attrition (`ChunkAreaBiomeSpawnData`)

Each area owns a `Dictionary<idHash, CountsAndTime>` where a `CountsAndTime` is
`{ count, maxCount, delayWorldTime }` per spawn group. This is the biome budget,
and it persists: it is written into the chunk's `ChunkCustomData` blob
(`BeforeWrite` -> `write`), so a chunk remembers its spawn state across
save/load.

| Operation | Effect |
|---|---|
| `CanSpawn(idHash)` | true only if `count < maxCount` |
| `IncCount` | on spawn: `count++`, mark chunk modified |
| `DecCount(idHash, killed=false)` | despawn: `count--` (floored at 0) |
| `DecCount(idHash, killed=true)` | kill: `count--` AND `maxCount--` (attrition) |
| `DecMaxCount` | group produced no valid class: `maxCount--` |
| `ResetRespawn(idHash, world, maxCount)` | set `maxCount`, arm `delayWorldTime = now + respawnDelay * rand(0.9, 1.1)` |
| `DelayAllEnemySpawningUntil` | push all enemy groups' delay forward (used to suppress enemies) |

The despawn accounting lives in `OnEntityUnloaded`, registered as a world
delegate. It only touches `Biome`-sourced entities and reads the master chunk
back from the entity's stored spawner chunk key:

```mermaid
stateDiagram-v2
  [*] --> Reason
  Reason --> Ignore: Undef(0) or Unloaded(1)
  Reason --> DecOnly: Despawned(3) -> DecCount killed=false
  Reason --> Human: Killed(2) and EntityHuman
  Reason --> Attrition: Killed(2) non-human, or Captured(4)+ -> DecCount killed=true
  Human --> DecOnly: past timeToDie (old age)
  Human --> Attrition: before timeToDie (violent)
  Ignore --> [*]: budget untouched, slot reserved for respawn
  DecOnly --> [*]: count-- only, maxCount preserved
  Attrition --> [*]: count-- and maxCount-- (chunk thins out)
```

The consequence: an entity that simply leaves because its chunk **unloaded**
keeps its reserved slot (it will respawn), a **despawn** frees the slot, and a
**kill** both frees the slot and permanently lowers that group's `maxCount` for
this chunk until the respawn delay elapses and `ResetRespawn` restores it. That
is the "clear a chunk and it stays clearer for a while" behaviour, encoded as
`maxCount` attrition plus a randomized respawn timer.

Persisted wire form of `CountsAndTime` (per entry, version byte 2): `idHash:i32`,
then a packed `u16` = `(maxCount << 8) | count`, then `delayWorldTime:u64`. Both
`count` and `maxCount` are therefore clamped to a byte on disk.

---

## 4. Waves, static and sleeper spawners (`EntitySpawner`, `SpawnManagerDynamic`)

`EntitySpawner` is the general-purpose spawner behind POI/static spawners,
sleeper volumes, dynamic night spawns, and scout hordes. Its class definition
(`EntitySpawnerClass`, loaded per day from `spawning.xml`) carries the tuning:
`numberOfWaves`, `totalPerWaveMin/Max`, `totalAlive`, `delayBetweenSpawns`,
`delayToNextWave`, `spawnAtTimeOfDay`, `daysToRespawnIfPlayerLeft`,
`bAttackPlayerImmediately`, `bTerritorial` / `territorialRange`, and a
`startSound`.

`SpawnManually` is the engine. Its callbacks let each caller supply its own
precondition, spawn-position, and count-modifier, so biome, dynamic, and scout
spawners all reuse it. Per invocation it:

1. Resolves the per-day `EntitySpawnerClass`; resets runtime state if the day
   rolled over and the class is flagged to reset.
2. Enforces `numberOfWaves`, `spawnAtTimeOfDay`, `timeDelayToNextWave`, and
   `timeDelayBetweenSpawns` gates (returns early if not yet due).
3. Prunes its `entityIdSpawned` list of dead or removed entities so `totalAlive`
   reflects reality.
4. Rolls `numberToSpawnThisWave` from `totalPerWaveMin/Max` (difficulty-scaled),
   then loops spawning up to `totalAlive` currently-alive entities, one every
   `delayBetweenSpawns`.
5. Tags each new entity `StaticSpawner` (2) or `Dynamic` (3), tracks its id,
   optionally sets a revenge target and a territorial home area.
6. Starts the next wave only once alive count falls to 20 % of the wave target
   (`0.2` factor, floored at 1), arming `delayToNextWave`.

`daysToRespawnIfPlayerLeft` uses `worldTimeNextWave = now + days * 24000` ticks
(24000 ticks per in-game day) so a POI that a player abandoned repopulates on a
schedule.

`SpawnManagerDynamic` is the thin night-only wrapper: it returns immediately in
daytime or with no players, builds one fresh `EntitySpawner` per in-game day
(`lastDaySpawned`), and calls `SpawnManually` with a position callback that
picks 64..96 m from a random player. Its own `currentSpawner` is serialized, so
a day's dynamic spawn progress survives a restart.

---

## 5. Chunk-heat scouts and screamer hordes (state machine)

Sustained activity (noise, digging, combat) raises a per-region heat value.
`AIDirectorChunkEventComponent` keeps an `activeChunks` map of
`AIDirectorChunkData` keyed by the same 5x5-chunk region key, decays it, and
every 5 s (`spawnDelay`) runs `CheckToSpawn`. When a region's `ActivityLevel`
crosses 25 (and the `ZombieHordeMeter` and `IsSpawnEnemies` game stats are set),
it spawns a scout party toward the hot spot; scouts that reach the player can in
turn create a follow-up horde. `AIHordeSpawner` is the closely related
screamer-triggered variant: it logs `Screamer spawned ...` and pulls a
gamestage-scaled group toward a target position.

```mermaid
stateDiagram-v2
  [*] --> Cooling
  Cooling --> Cooling: Tick every 5 s, activity decays
  Cooling --> Check: activity >= 25 and horde stats enabled
  Check --> Cooling: no chunk event found
  Check --> Cooldown: FindBestEventAndReset, StartCooldownOnNeighbors
  Cooldown --> Scouts: SpawnScouts, pick Scouts1/2/Feral/Radiated by gamestage
  Scouts --> Spawning: AIScoutHordeSpawner / AIHordeSpawner gathers player party
  Spawning --> Spawning: spawn one per tick until numToSpawn, IncSpawnCount
  Spawning --> Hunting: each mob SetInvestigatePosition(target, 2400 ticks)
  Hunting --> Horde: scouts reach target -> CreateHorde (optional)
  Horde --> Done: all mobs spawned
  Spawning --> Done: canSpawn false or count reached
  Done --> Cleanup: Cleanup clears IsHordeZombie + bIsChunkObserver
  Cleanup --> [*]
```

Facts from the IL:

- **Gamestage selection.** `SpawnScouts` reads `CalcGameStageAround` for the
  closest player within 120 m and picks the group by thresholds:
  `Scouts1` (&lt; 45), `Scouts2` (&lt; 85), `ScoutsFeral` (&lt; 125),
  `ScoutsRadiated` (otherwise). A 20 % roll upgrades to the feral/long-cooldown
  variant and applies a longer neighbor cooldown.
- **Party sizing.** `AIHordeSpawner` gathers players inside its search bounds as
  members of an `AIDirectorGameStagePartySpawner`, which sets the group name and
  the `numToSpawn` budget from party gamestage.
- **Placement.** For the **screamer path** (`AIHordeSpawner.Tick`), mobs spawn at
  45/55/45 m (day) or 55/70/55 m (night) via `GetMobRandomSpawnPosWithWater`
  (`IsDaytime()`-branched). The **chunk-heat scout spawner** uses different
  constants (`0/8/10`, no day/night branch) in its `SpawnUpdate` position callback.
  Spawned mobs are tagged `Dynamic`, flagged
  `IsHordeZombie` and `bIsChunkObserver` (so they keep their own chunk loaded),
  and are pointed at the target with `SetInvestigatePosition(target, 2400)`.
- **Teardown.** When a spawner reports finished, `TickActiveSpawns` calls
  `Cleanup`, which clears `IsHordeZombie` and `bIsChunkObserver` on every mob so
  they revert to normal despawn rules, then removes the spawner from its list.

Blood-moon and wandering hordes proper are separate director components
(`AIDirectorBloodMoonComponent`, `AIDirectorWanderingHordeComponent`); their
lifecycle is owned by [`aidirector.md`](aidirector.md). This subsystem owns only
the chunk-heat and screamer spawners above.

---

## 6. Player spawn points (`SpawnPointList`)

`SpawnPointList` holds the world's fixed player start positions.
`GetRandomSpawnPosition(world, refPos, minDistance, maxDistance)`:

- With no reference position, returns a uniformly random point.
- With a reference (respawn near bedroll or death), it makes up to 100 tries for
  a point in the `[minDistance, maxDistance]` ring; if none qualifies it falls
  back to the nearest point by squared distance, or `SpawnPosition.Undef` if the
  list is empty.

The list is built at world load (`GameManager.setSpawnPointListCo`) and is the
player-only counterpart to the entity spawners above.

---

## 7. From decision to entity to client

A decided spawn becomes a networked entity through one path, and interest
management (not the spawner) decides who sees it.

```mermaid
stateDiagram-v2
  [*] --> Created: EntityFactory.CreateEntity / SetupEntityCreationData
  Created --> Registered: World.SpawnEntityInWorld
  Registered --> Registered: AddEntityToMap, alive/manager lists,<br/>AIDirector.AddEntity, NetEntityDistribution.Add
  Registered --> Tracked: player enters interest range
  Tracked --> Replicated: NetPackageEntitySpawn -> client (EntityCreationData)
  Replicated --> Live: client-side entity, server keeps authority
  Live --> Untracked: player leaves range -> despawn package to that client only
  Untracked --> Tracked: player returns
  Live --> Removed: killed / despawn / chunk unload
  Removed --> Accounting: OnEntityUnloaded adjusts budget (biome only, see §3)
  Accounting --> [*]
```

Client place requests arrive as `NetPackageRequestToSpawnEntity` →
`GameManager.RequestToSpawnEntityServer` (falling-tree dedupe, backpack
persistent record, then `EntityFactory.CreateEntity` +
`World.SpawnEntityInWorld`). See [protocol-packages.md](protocol-packages.md)
section 5.0.

`World.SpawnEntityInWorld` registers the entity (world map, alive list, per-type
trackers, `AIDirector.AddEntity`) and calls `NetEntityDistribution.Add`. It does
**not** broadcast a spawn. The replication layer (`NetEntityDistribution`,
[`entity-ai.md`](entity-ai.md) §9) walks players against tracked entities by
distance and view angle and emits `NetPackageEntitySpawn` (an
`EntityCreationData` payload, [`protocol-packages.md`](protocol-packages.md) §5.1)
to each player only when the entity enters that player's set, and a delete when
it leaves. This is the observer/player-gating for spawned entities: spawns are
decided near players (§2, §5) and replicated per player on demand, so cost
scales with players by tracked entities, not with total world population.

Biome spawns additionally run through the async creator
(`Chunk.SpawnEntityAsync` -> `EntityAsyncManager`), which safely refuses to
spawn onto a chunk that is unloading.

---

## 8. Prefab placement context (`DynamicPrefabDecorator`)

`DynamicPrefabDecorator` is the world's prefab (POI) registry, not an entity
spawner, but it is what makes POI-gated spawning and sleeper volumes possible.
`DecorateChunk` looks up the prefab instances overlapping a chunk
(`GetPrefabsAtXZ`, sorted by size) and stamps each into the chunk
(`PrefabInstance.CopyIntoChunk`), which is what brings a POI's sleeper volumes
and block data into the world. The same `GetPOIsAtXZ` / prefab-tag surface is
what `SpawnManagerBiomes` reads to compute an area's `poiTags` (§2). Trader
areas, quest-POI selection, and volume ownership all hang off this registry.

Sleeper volumes themselves tick in `SleeperVolume.Tick`
([`entity-ai.md`](entity-ai.md) §10, D8); this doc's role is to note that the
sleeper population enters the world through prefab placement here, then through
`EntitySpawner` (§4) when a player trips the volume.

---

## 9. Dedicated relevance and residuals

- **Runs on dedicated.** Every spawn decision in §2 to §7 executes on the server
  from `World.OnUpdateTick` and `AIDirector.ComponentsTick`. Clients only apply
  the resulting `NetPackageEntitySpawn`.
- **Caps are server prefs.** `MaxSpawnedZombies` (GamePref 99) and
  `MaxSpawnedAnimals` (GamePref 129) are the two global living-population caps;
  per-chunk-area `maxCount` and per-spawner `totalAlive` are the local caps.
- **Residual (content, not loop IL):** `spawning.xml` (spawner classes, waves,
  times), `biomes.xml` spawn groups (`BiomeSpawnEntityGroupList`), and
  `entitygroups.xml` (`EntityGroups.GetRandomFromGroup` tables) are data. The IL
  proves the decision structure; the numbers per biome/POI live in XML.
- **Residual (persisted state):** per-chunk `ChunkAreaBiomeSpawnData` and
  `SpawnManagerDynamic.currentSpawner` are serialized into the save
  ([`save-region.md`](save-region.md)); their contents are runtime data.
- **Residual (external):** Unity entity GameObject instantiation and the async
  creation thread pool internals sit below the managed spawn logic.

---

## Spawn config leaves

Small config/state types that orbit the spawners above (inventoried in
[`inventories/dedicated-leaves.md`](inventories/dedicated-leaves.md)); all five
run or fire on the dedicated server.

- **`EntitySpawnerClassForDay`** (base `Object`) is the day-indexed schedule of
  wave classes parsed from `spawning.xml`: a sparse `List<EntitySpawnerClass>`
  (`days`, null-padded by `AddForDay`) that `Day(int)` resolves for the current
  game day, with `bWrapDays` cycling past the end via modulo over `Count - 1`
  and `bClampDays` holding the last entry. `EntitySpawner` (§4) calls `Day` in
  its constructor, `Spawn`, and `SpawnManually` to pick the active wave class.
- **`SpawnEntry`** (nested `GameEventManager/SpawnEntry`, base `Object`) tracks
  one entity spawned by a game-event action sequence (`SpawnedEntity`, `Target`,
  `Requester`, owning `GameEvent`, `IsAggressive`). Its only method,
  `HandleUpdate`, enforces aggression: when `IsAggressive` and the entity has no
  player attack target, it calls `World.GetClosestPlayer(entity, 500f, false)`
  and `SetAttackTarget(target, 1000)`. Server-side game-event bookkeeping
  ([`game-events.md`](game-events.md)).
- **`SupplyCrateSpawn`** (nested `AIAirDrop/SupplyCrateSpawn`, base `Object`,
  fields only: `Delay`, `SpawnPos`, `ChunkRef`) is one pending air-drop crate:
  `AIAirDrop.CreateFlightPaths` queues it per flight path and `AIAirDrop.Tick`
  counts down `Delay` then spawns the crate and removes the entry; `ChunkRef` is
  the `ChunkObserver` that keeps the drop chunk loaded until then. Part of the
  air-drop director component ([`aidirector.md`](aidirector.md)).
- **`RequestToSpawnPlayer` join path (IL=496):** server creates the remote
  `EntityPlayer` and sends `NetPackagePlayerId` before `SpawnEntityInWorld`.
  Spawn position order: team-near (GameStats 25) -> friend-near (`nearEntityId`,
  40..150) -> `SpawnPointList`. New vs returning file chooses
  `RespawnType.EnterMultiplayer` (4) vs `JoinMultiplayer` (5). Full sequence and
  wire bodies: [protocol.md](protocol.md) section 5. `PlayerSpawnedInWorld` is a
  **later** client-driven package, not part of this method.
- **`SPlayerSpawningData`** (nested `ModEvents/SPlayerSpawningData`, a
  `ValueType`) is the payload struct for the `ModEvents.PlayerSpawning` hook:
  `ClientInfo`, `ChunkViewDim`, `PlayerProfile`. `GameManager.RequestToSpawnPlayer`
  constructs it and invokes the event by ref at the end of the spawn method.
  This is an in-process mod-hook data struct ([`managers.md`](managers.md)
  section 2), not a wire format; nothing serializes it.
- **`SPlayerSpawnedInWorldData`** (nested `ModEvents/SPlayerSpawnedInWorldData`,
  a `ValueType`) is the matching payload for `ModEvents.PlayerSpawnedInWorld`:
  `ClientInfo`, `IsLocalPlayer`, `EntityId`, `RespawnType`, `Position`
  (`Vector3i`). Fired by `GameManager.PlayerSpawnedInWorld` when
  `NetPackagePlayerSpawnedInWorld` is processed (after the entity is already
  world-spawned); consumed in-assembly by `DiscordManager`. Also in-process only,
  not a wire struct.

---

## Related docs

| Doc | Role |
|---|---|
| [entity-ai.md](entity-ai.md) | What a spawned entity does next: tick, AI, path, and `NetEntityDistribution` replication |
| [aidirector.md](aidirector.md) | Blood-moon and wandering-horde director components (separate from this doc's spawners) |
| [protocol-packages.md](protocol-packages.md) | `NetPackageEntitySpawn` / `EntityCreationData` wire layout (§5.1) |
| [loop.md](loop.md) | `OnUpdateTick` frame context that drives the biome loop |
| [world-chunks.md](world-chunks.md) | Chunk-area grid and chunk custom data |
| [network.md](network.md) | Entity replication cost |
| [managers.md](managers.md) | Other in-process managers |
| [save-region.md](save-region.md) | Where per-chunk spawn budgets persist |
| [full-surface.md](full-surface.md) | Where this sits in the whole-assembly map |
| [re-methodology.md](re-methodology.md) | How this was reversed |
| [residuals.md](residuals.md) | Content and native residuals |

## Changelog

- **2026-07-28:** RequestToSpawnEntityServer place path.

- **2026-07-28:** Documented RequestToSpawnPlayer join path vs PlayerSpawnedInWorld timing.

- **2026-07-23:** Initial entity-spawning reversal: five spawn sources, the biome
  decision cycle, per-chunk-area caps/cooldown/kill-attrition, wave/static/sleeper
  spawner, chunk-heat scout and screamer horde lifecycles, spawn-to-client
  replication path, and prefab-placement context, with state machines.
- **2026-07-24:** Added spawn config leaves: `EntitySpawnerClassForDay`,
  `GameEventManager/SpawnEntry`, `AIAirDrop/SupplyCrateSpawn`, and the two
  `ModEvents` player-spawn payload structs.
