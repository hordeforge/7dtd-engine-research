# AIDirector component types (V3.1.0)

**Owns:** AIDirector type inventory + player-state/horde targeting/chunk-event heat pipeline.  
**Tick path:** [`entity-ai.md`](entity-ai.md), [`loop.md`](loop.md) §5.  
**Install order detail:** [`closed-gaps.md`](closed-gaps.md).  
**Hub:** [`INDEX.md`](INDEX.md).

Registered components are ticked via `AIDirector.ComponentsTick` → each `AIDirectorComponent.Tick`.  
Constructed always from `CreateComponents` (fixed order) when `WorldState.SetFrom` builds `new AIDirector()`.

```mermaid
flowchart TB
  WS[WorldState.SetFrom] --> NEW[new AIDirector]
  NEW --> CC[CreateComponents fixed order]
  CC --> M1[MarkerManagement]
  CC --> M2[PlayerManagement]
  CC --> M3[WanderingHorde]
  CC --> M4[AirDrop]
  CC --> M5[ChunkEvent]
  CC --> M6[BloodMoon]
  OUT[World.OnUpdateTick server] --> T[AIDirector.Tick]
  T --> CT[ComponentsTick]
  CT --> M1
  CT --> M2
  CT --> M3
  CT --> M4
  CT --> M5
  CT --> M6
```

## AIDirector : Object

- `Tick(Double)` IL=6 → `ComponentsTick` IL=21 (plus `DebugTick` IL=7)
- `CreateComponents()` IL=31 (fixed install order, verified)
- `CanSpawn(Single)` IL=10
- `UpdatePlayerInventory(EntityPlayerLocal)` IL=5
- `UpdatePlayerInventory(Int32,AIDirectorPlayerInventory)` IL=6
- `GetActivityWorldTimeDelay()` IL=16: `clamp(GameStats[11]
  TimeOfDayIncPerSec / 6, 0.2, 5) * 1000` world-time ticks between activity
  passes (scales with the day-speed stat)
- `ComponentsInitNewGame()` IL=20: `InitNewGame()` on every registered
  component; `NotifyIntentToAttack(zombie, player)` IL=1 is an empty residual
  (its only caller, `EntityEnemy.OnEntityTargeted` IL=21, fires it for
  non-remote, non-`Dynamic`-spawned enemies targeting a player)

**Caller:** `World.OnUpdateTick` → `AIDirector.Tick` (Xref=1, server path).

**Director leaves:** `AddEntity` (IL=10) routes `EntityPlayer` to `AddPlayer`
(IL=9) = `playerManagementComponent.AddPlayer` + `bloodMoonComponent.AddPlayer`;
`RemovePlayer` (IL=9) mirrors both removals. `GetComponent<T>()` (IL=19) looks
up the `components` dict by `Type.FullName` (default(T) when absent).
Persistence: `Save(stream)` (IL=7) writes version **10** then
`ComponentsSave` (IL=21), which runs `component.Write(writer)` over the install
order; `Load(stream)` (IL=14) reads the version, `ComponentsLoad` (IL=22) runs
`component.Read(reader, version)` per component, and a zero `world.worldTime`
triggers `Init()` (fresh world).

**Noise + activity:** `NotifyNoise` (IL=84) / `NotifyActivity` (IL=31) - the
AI-aware sound and heat-map entries (reached from `OnSoundPlayedAtPosition`
IL=17); full bodies in the chunk-event section below.

### CreateComponents order (IL=31, verified)

1. `AIDirectorMarkerManagementComponent`
2. `AIDirectorPlayerManagementComponent` (cached on `playerManagementComponent`)
3. `AIDirectorWanderingHordeComponent`
4. `AIDirectorAirDropComponent`
5. `AIDirectorChunkEventComponent` (cached on `chunkEventComponent`)
6. `AIDirectorBloodMoonComponent` (cached on `bloodMoonComponent`)

## AIDirectorAirDropComponent : AIDirectorComponent
- `Tick(Double)` IL=75
- `SpawnAirDrop()` IL=59
- `SpawnSupplyCrate(Vector3,ChunkObserver)` IL=77

**Supply crate entity (`EntitySupplyCrate`, V3.1.0 b14):** `fallHitGround`
(IL=15) clamps the impact speed to 5 and forces the vertical fall component
to `max(fallMotion.y, -0.75)` before delegating to the base - the crate
always lands softly. `OnEntityDeath` (IL=30) removes the map marker
(`World.ObjectOnMapRemove(EnumMapObjectType 13, entityId)`), broadcasts
`NetPackageEntityMapMarkerRemove(13, entityId)` (channel 192) on the server,
and `DropBagServer()`s the loot. `OnEntityActivated` (IL=18) routes the
`search` command through `LockManager.LockRequestLocal(this, new
EntityLockContext(commandId, bag), 0)` - the crate opens via the same lock
system as loot bags. `canDespawn()` (IL=2) is **always false**: landed
crates persist until looted or removed.

More `EntitySupplyCrate` runtime (V3.1.0 b14):

- **Parachute flight:** `MoveEntityHeaded` (IL=35) adds
  `motion.y += ScalePhysicsAddConstant(world.Gravity * 0.95)` each tick while
  the parachute is active and the crate is not in water - the chute cuts gravity
  to **95%** (slow descent). `Update` (IL=39) swings the model while airborne:
  `localEulerAngles = (8*sin(t) - 4, 8*sin(t + 0.3) - 4 + startRotY, 0)`
  (`startRotY` captured in `Start` from `rotation.y`). `Awake` sets
  `hasAI = false` (no AI on crates). The ctor defaults `isSmokeOn = true` and
  `smokeTimeAfterLanding = 240`.
- **Spawn/load:** `PostInit` (IL=35) calls `ValidateResources` (IL=23: locates
  `crateT` under `SupplyCrateEntityPrefab` and `parachuteT` under
  `parachute_supplies` via `FindInChilds`), sets `gameObject.layer = 21`,
  re-enables the collider, and if `wasOnGround` (crate loaded landed from save)
  calls `StopSmokeAndLights()` and deactivates the parachute.
- **Smoke/lights:** `StopSmokeAndLights` (IL=77) turns off `loop` on every
  `ParticleSystem` under the `SupplySmoke`-tagged children and deactivates all
  `SupplyLit` children (lights). `RequiresChunkObserver` (IL=8) is `true` while
  airborne, and `isSmokeOn` once landed (the smoke keeps the crate's chunk
  observed until it goes off).
- **Loot UI:** `InitLocalActivationCommands` (IL=8) registers one `search`
  command; `AllowActivationCommand` (IL=20) allows it only when `bag != null`
  and alive; `GetActivationText` (IL=81) shows `lootTooltipNew` / `Empty` /
  `Touched` localized text prefixed with the Activate binding markup.
- **Map marker:** `HandleNavObject` (IL=64), gated on
  `GameStats.GetBool(AirDropMarker = 53)`: re-registers the `NavObject` from
  `EntityClass.NavObject` and, on the server, pushes
  `NetPackageNavObject(className, displayName, navPos + Origin.position, true,
  usingLocalizationId, entityId)` on channel 192.
- **Persistence/wire:** `Read`/`Write` (IL=20/17) carry `wasOnGround`,
  `closeParachuteInTicks`, `showParachuteInTicks`; the Read block is version
  **>= 11** gated. `IsSavedToFile` is `true`. `OnEntityUnload` (IL=17), when the
  unload reason is `Killed` and running on the server, calls
  `AIDirectorAirDropComponent.RemoveSupplyCrate(entityId)`.
- **Flavor trivials:** `GetMapObjectType` = `SupplyDrop` (13);
  `SetMotionMultiplier` is a no-op; `CanCollideWithBlocks` / `CanCollideWith` /
  `CanBePushed` / `isRadiationSensitive` / `get_IsValidAimAssistSnapTarget` are
  all `false`.

**Air drop flight logic (`AIAirDrop`, V3.1.0 b14):** `SpawnAirDrop`
(IL=59) builds an `AIAirDrop` (players + controller), whose `Tick` (IL=193)
drives the whole drop. `CreateFlightPaths` (IL=355) runs once:
`MakePlayerClusters` (IL=70) groups players within **30 m** (`Radius`,
`XZCenter`); `CalcSupplyDropMetrics` (IL=53) sizes the drop - 1..4 planes
(`max(1, min(4, rand(0..2) + 1))`), crates from `SelectCrateCount`
(min=max=1, balanced so `crates/planes` stays 1..3). Per path it picks a
random cluster and a random player inside it, sets
`crateY = FastMin(player.y + 180, 276)` (180 m up, capped), picks a drop
point at `XZCenter + RandomOnUnitCircle * RandomRange(30, 750)`, a random
flight direction, and `FindSafePoint` (IL=70) walks the perpendicular to
find Start/End **at least 600 m from every player** (squared-distance
check, clamped to the map via `ClampToMapExtents`). Crates are spaced along
the flight line, each with a staggered `Delay` and a `ChunkObserver` ref.
`Tick` first waits until every crate's chunk is loaded
(`GetChunkFromWorldPos` non-null), then per path: after `Delay` ->
`SpawnPlane`; each crate after its `Delay` ->
`controller.SpawnSupplyCrate(SpawnPos, ChunkRef)` (with the
`AIAirDrop: Spawned supply crate at ...` log); a path is removed when its
crates are gone, and `flightPaths = null` ends the drop.
`SpawnPlane` (IL=74) creates the plane
(`EntityClass.FromString("supplyPlane")`, yaw = `Angle(heading)`),
`SetDirectionToFly(dir, 20 * (len/120 + 10))` and
`world.SpawnEntityInWorld`.

**Plane entity (`EntitySupplyPlane`):** `SetDirectionToFly` (IL=12) stores
`motion = direction * 6` and `IsMovementReplicated = false` (server flies
the straight line); `OnUpdatePosition` (IL=49) advances
`position += motion * partialTicks`, counts `ticksToFly` down and
`MarkToUnload()` at 0, plays `SupplyDrops/Supply_Crate_Plane_lp` once, and
`SetAirBorne(true)`. `IsSavedToFile` and `IsDeadIfOutOfWorld` are both
false - the plane lives only for its flight budget.

**Far-draw trick:** `UpdateFarDraw` (IL=35) caches `mainCamera = Camera.main`
and lazily captures `planeMesh` from the child `MeshFilter`, then
`MoveBoundsInsideFrustrum(transform)` (IL=31) sets
`planeMesh.bounds = Bounds(zero, Vector3.one * |camera - plane| * 1.25)` - the
mesh bounds are inflated with distance so the far plane is never frustum-culled
while it crosses the sky. `Awake` and the ctor are base-only; `CanCollideWithBlocks`
is false (no collisions on the plane).

## AIDirectorBloodMoonComponent : AIDirectorComponent
- `Tick(Double)` IL=170

**`Tick(dt)` (IL=170):** base component tick, then `isBloodMoon =
IsBloodMoonTime(world.worldTime)`; on a rising edge `StartBloodMoon()`, on a
falling edge `EndBloodMoon()`. When **not** blood moon it watches the GameStats
int **58** (blood-moon day): a change stores `bmDay` / `bmDayLast = bmDay - 1`
and warns `Blood Moon day stat changed {0}`. When blood moon **and** GameStats
bool **24** are active: `delay -= dt`; every tracked player without a
`bloodMoonParty` that `IsSpawned()` joins one via `AddPlayerToParty`; then the
`parties` list is walked round-robin from `nextParty` (wrapping at Count): an
empty party gets `KillPartyZombies()`; the primary party (index == `nextParty`)
ticks `party.Tick(world, dt, canSpawn = delay <= 0)`; when it ticks, `delay =
1 / parties.Count` and `nextParty++` (one party spawns per delay window).

## AIDirectorBloodMoonParty : Object
- `Tick(World,Double,Boolean)` IL=162
- `SpawnZombie(World,EntityPlayer,Vector3,Vector3)` IL=181
- `CalcSpawnPos(World,Vector3,Vector3,Vector3&)` IL=28

**`Tick(world, dt, canSpawn)` (IL=162):** `InitParty()` on first tick
(`partyLevel < 0`); then each `ManagedZombie` counts `updateDelay -= dt` and at
`<= 0` resets it to **1.8** s and re-runs `SeekTarget` (a failed seek removes
the zombie). `partySpawner.Tick(dt)` advances the gamestage spawner. With
`canSpawn && partySpawner.canSpawn && partyMembers.Count > 0 &&
AIDirector.CanSpawn(1.9)`: on a `groupIndex` change it syncs the index, rotates
`spawnBaseDir += 120` (degrees) and recalcs `CalcBestDir(spawnBasePos)`; the
alive cap is `FastMin(partySpawner.maxAlive, enemyActiveMax)`; while
`zombies.Count < cap`, up to `FastMin(memberCount, 3)` round-robin players from
`nextPlayer` get `SpawnZombie(world, player, player.position,
spawnDirectionV)` (only when `IsPlayerATarget`), stopping at the first
successful spawn.

**`SpawnZombie(world, target, focusPos, radiusV)` (IL=181):** `CalcSpawnPos`
fails → false. Class pick:
`EntityGroups.GetRandomEntityFromGroupMaxTier(partySpawner.spawnGroupName,
EntityFactory.MaxEntityTier, ref lastClassId, ...)`; when the pick is an
attached entity, 50% of the time it is overridden to
`animalZombieVultureRadiated`; a `-1` pick logs
`Could not spawn an entity from group {0} within Sandbox Options Max Tier
Limit {1}.` and returns false. Spawns via
`EntityFactory.CreateEntity(id, pos)` (cast `EntityEnemy`) +
`SetSpawnerSource(3)` (Dynamic) + `SpawnEntityInWorld`, then flags
`IsHordeZombie = IsBloodMoon = bIsChunkObserver = true` and cuts
`timeStayAfterDeath /= 3`. **Bonus loot:** `bonusLootSpawnCount++`; when it
reaches `partySpawner.bonusLootEvery` it resets and scales
`lootDropProb *= GameStageDefinition.LootBonusScale`. Registers a
`ManagedZombie`, `SeekTarget`, `partySpawner.IncSpawnCount()`,
`AstarManager.AddLocation(spawnPos, 40)`, and logs
`BloodMoonParty: SpawnZombie grp {0}, cnt {1}, {2}, loot {3}, at player {4},
day/time {5} {6:D2}:{7:D2}`.

**`CalcSpawnPos(world, focusPos, radiusV, out spawnPos)` (IL=28):** rotates
`_radiusV` around `up` by `(RandomFloat - 0.5) * 90` degrees (±45) and runs
`GetMobRandomSpawnPosWithWater(focusPos + rotatedRadius, 0, 10, 30, false,
out)` - the ring 10-30 m around the focus.

**Party bookkeeping leaves:** `AddPlayerToParty(player)` (IL=55) first looks for
an existing party whose `IsMemberOfParty(entityId)` matches (and adds), else
walks the `parties` list calling `TryAddPlayer` (IL=34): the player joins the
first party with a member within **80 m** (sqr 6400), and a still-partyless
player gets `CreateNewParty`. `AddPlayer(player)` (IL=8) adds a member to the
party spawner and stamps `player.bloodMoonParty`. `RemovePlayer` (IL=24) drops
the player from the list and calls `PlayerLoggedOut` on every party.

## AIDirectorChunkData : Object

Per-chunk heat / event bag used by the chunk-event horde path.

**Fields:** `activityLevel` (single), `events` (`List<AIDirectorChunkEvent>`),
`cooldownDelay`, plus static delay constants (`cDataDelay`, `cDataLongDelay`,
`cDataNeighborDelay`, `cDataNeighborLongDelay`), `cVersion`.

- `Tick(Single)` IL=23 (returns whether still alive in the map)
- Persistence: `Write` emits version **2**, `activityLevel`, event count + each
  `AIDirectorChunkEvent.Write`, then `cooldownDelay`.

**`DecayEvents(elapsed)` (IL=61):** zeroes `activityLevel`, then per event:
`value -= value * (elapsed / duration)` (linear decay), `duration -= elapsed`;
an event with `duration <= 0` or `value <= 0` is removed from the list; the
survivors' values re-accumulate into `activityLevel` (so the chunk's activity
is the sum of its live events after decay).

**Cooldown values (verified literals):** `FindBestEventAndReset` (IL=44) picks
the max-`Value` event, then stamps `cooldownDelay = 240` (s) before
`ClearEvents()`. `SetLongDelay` (IL=4) stamps `cooldownDelay = 1320` (22 min).
`StartNeighborCooldown(isLong)` (IL=13) sets the delay to **180** s (short) or
**720** s (long), via `FastMax` against the current value.

## `AIDirectorChunkEvent` : Object

**Fields:** `EventType` (`EnumAIDirectorChunkEvent`), `Position` (`Vector3i`),
`Value`, `Duration`, `cVersion`.

**Wire (`Write` IL=32 / `Read` IL=39):**

| Order | Field | Type |
|---|---|---|
| 1 | version | `Int32` (**2** on write) |
| 2-4 | Position x,y,z | `Int32` each |
| 5 | Value | `Single` |
| 6 | EventType | `Byte` (enum) |
| 7 | Duration | `Single` |

## AIDirectorChunkEventComponent : `AIDirectorHordeComponent`

Scout / activity-driven hordes (see also [spawning.md](spawning.md)).

- `Tick(Double)` IL=79
- `TickActiveSpawns(Single)` IL=66
- `CheckToSpawn()` IL=18 / `CheckToSpawn(AIDirectorChunkData)` IL=46
- `SpawnScouts(Vector3)` IL=76
- nested `Horde` helper type (7 methods in method list)

**`Tick` body (verified):**

1. Base `AIDirectorComponent.Tick`.
2. Every **5 s** accumulated: `CheckToSpawn()`.
3. Walk `Dictionary<Int64, AIDirectorChunkData>`; `AIDirectorChunkData.Tick(dt)`;
   remove entries that expire.
4. `TickActiveSpawns(dt)`.

**`TickActiveSpawns` (IL=66):** reverse-iterate `scoutSpawnList`;
`AIScoutHordeSpawner.Update(world, dt)`; on true: log finished, `Cleanup`,
`RemoveAt`. Then reverse-iterate `hordeSpawnList`; `Horde.Tick(dt as double)`;
on true: log finished, `RemoveAt`. `HasAnySpawns` is only `hordeSpawnList.Count
> 0` (scouts not counted).

**`AIDirector.NotifyActivity` (IL=31):** no-op if `value <= 0`, or GameStats bool
**32** / **24** off, or `HeatMapSensitivityModifier <= 0`, or blood moon active, or
Twitch boss horde active. Else build `AIDirectorChunkEvent(type, pos,
value * HeatMapSensitivityModifier, duration)` and
`chunkEventComponent.NotifyEvent`.

**`AIDirector.NotifyNoise(instigator, pos, clipName, volumeScale)` (IL=84)** is
the sound-to-AI chain behind `OnSoundPlayedAtPosition` (IL=17, which resolves
the instigator entity first): `AIDirectorData.FindNoise(clipName)` fails for an
unknown clip (silent return); enemy instigators, `IsIgnoredByAI` entities, and
`EntityItem` throwable **decoys** are all excluded. The instigator's
`AIDirectorPlayerState` is looked up in `playerManagementComponent`; a
crouching player muffles the noise (`volumeScale *= noise.muffledWhenCrouched`).
`volume = noise.volume * volumeScale` feeds
`playerState.Player.Stealth.NotifyNoise(volume, noise.duration)`; when the
stealth system accepts it, `world.CheckSleeperVolumeNoise(pos)` wakes sleepers
in range. Finally, `noise.heatMapStrength > 0` raises a heat-map chunk event:
`NotifyActivity(EnumAIDirectorChunkEvent=3, worldToBlockPos(pos),
heatMapStrength * volumeScale, 240)`.

**`CheckToSpawn()` (IL=18):** FIFO pop one entry from `checkChunks` and call
`CheckToSpawn(chunkData)` (one chunk per 5 s pulse).

**`CheckToSpawn(AIDirectorChunkData)` (IL=46):** require GameStats 32+24;
`ActivityLevel >= 25`; `FindBestEventAndReset`; with **20%** random (and not
playtest) set spawn flag, `StartCooldownOnNeighbors`, `SetLongDelay`,
`SpawnScouts`. Otherwise neighbor cooldown only.

**`NotifyEvent` (IL=22):** `GetChunkDataFromPosition(pos, create=true)`; if ready
`AddEvent` and enqueue into `checkChunks` if not already listed.

**`SpawnScouts` (IL=76):** `FindScoutStartPos`; closest player within **120** m;
`CalcGameStageAround` → group name: `Scouts1` (&lt;45), `Scouts2` (&lt;85),
`ScoutsFeral` (&lt;125), else `ScoutsRadiated`; queue `AIScoutHordeSpawner` on
`scoutSpawnList`.

**`AIScoutHordeSpawner.Update` (IL=22):** finished (true) if no players, or
`SpawnUpdate` returns true and `hordeList` empty; else `UpdateHorde` and keep
(false).

**Scout internals:** `SpawnUpdate` (IL=129) is done when `!CanSpawn(1)` or the
`EntitySpawner` already has a current wave; it runs
`spawner.SpawnManually(world, WorldTimeToDays(worldTime), true, ...,
spawnedList)` and turns each spawned `EntityEnemy` into a scout
(`IsScoutZombie`, `IsBloodMoon = isBloodMoon`, horde flags) with a
`ZombieCommand` investigate order toward `CalcRandomPos(director, endPos, 6)`
(6000 ticks), logging `scout horde spawned '<zombie>'. Moving to point of
interest`. `UpdateHorde` (IL=229) drives the per-command wander/attack cycle;
when a scout finishes its leg it calls `spawnHordeNear` (IL=94): logs `Scout
spawned a zombie horde`, lazily `CreateHorde`s via the chunk-event component,
then with `canSpawnMore` spawns a **5**-zombie horde (a **12%** chance
subtracts one and, when the base spawner had a wave, resets it to
`numberToSpawnThisWave = 1` and re-runs `SpawnUpdate`, else bumps the wave
count), plays the zombie's `GetSoundAlert()` one-shot, `SetSpawnPos(target)`,
and keeps the horde active while `canSpawnMore || isSpawning`.
`CalcRandomPos` (IL=15) is `target + RandomOnUnitCircle * radius` (y = 0);
`Cleanup` (IL=27) releases the horde flags.

**Chunk-event leaves:** `GetChunkDataFromPosition(pos, createIfNeeded)` (IL=33)
keys the per-chunk bags by a **5x5-chunk district**
(`MakeChunkKey(toChunkXZ(x) / 5, toChunkXZ(z) / 5)`), creating the entry when
asked. `StartCooldownOnNeighbors(pos, isLong)` (IL=55) walks the static
`neighbors` offset array, get-or-creates each neighbor district's data and
calls `StartNeighborCooldown(isLong)` (the 180 s / 720 s cooldown table).
`CreateHorde(startPos)` (IL=10) appends a nested `Horde` to `hordeSpawnList`
and returns it. `Write` (IL=33) persists version **1**, the count, then per
entry the i64 district key + `AIDirectorChunkData.Write`; `Read` (IL=37) only
runs when the outer version is >= **5**, reading the inner version + count into
`AIDirectorChunkData.Read`. `Clear` (IL=7) empties `activeChunks` +
`checkChunks`; `GetActiveCount` (IL=4) is the dict count.

**`AIScoutHordeSpawner.SpawnUpdate` (IL=129):** require `CanSpawn(1)` and
`CurrentWave <= 0` else finished; `SpawnManually` (day, enemies on); for each
`EntityEnemy`: `IsHordeZombie`/`IsScoutZombie`/`bIsChunkObserver` true, BM flag
from spawner; `ZombieCommand` with `AttackDelay=**2**`, investigate
`CalcRandomPos(endPos, 6)` for **6000** ticks; clear `spawnedList`; finished
when `CurrentWave > 0`.

**`Horde.Tick` (IL=21):** if `_destroy` finished; else if nested
`AIHordeSpawner.Tick` finishes, `Cleanup` and clear `_horde`; never auto-finish
while spawner null (returns false).

**`UpdateHorde` (IL=229):** per command: dead scouts culled; if not attacking
and lost investigate / dead target, may `spawnHordeNear` then
`AttackDelay = **18**` s; investigate refresh uses **2000** / **6000** tick
lifetimes; when attacking, keep horde spawn pos on living scout.

**`spawnHordeNear` (IL=94):** ensure `IHorde` via
`AIDirectorChunkEventComponent.CreateHorde`; if `canSpawnMore`: base count **5**,
with **12%** chance reduce by 1 and either `SpawnUpdate` one extra wave or bump
`numberToSpawnThisWave`; `Horde.SpawnMore(count)`; play scout alert sound;
`SetSpawnPos(target)`.

**`CreateHorde` (IL=10):** `new Horde(this, startPos)` onto `hordeSpawnList`.

**`StartCooldownOnNeighbors` (IL=55):** map world pos to coarse cell
`toChunkXZ/5`; walk static `neighbors[]` pairs; ensure `activeChunks` entry;
`StartNeighborCooldown(isLong)` on each.

**`FindScoutStartPos` (IL=192):** random on unit circle × **80** with up to **15**
tries; radial band **16..40** from end; reject if any living player within
sqr **900** (30 m); require loaded chunks and `CanMobsSpawnAtPos`.

**`AIDirectorChunkData.Tick` (IL=23):** if `cooldownDelay > 0` subtract elapsed
and keep entry; else `DecayEvents`; keep entry while `EventCount > 0`.

**`AddEvent` (IL=46):** find existing event of same type (predicate); if none
append; else **add** `Value` and replace `Duration` with new event's duration;
always `activityLevel += event.Value`.

**Persistence + accessors:** `Write` (IL=35) emits inner version **2**,
`activityLevel` (f32), event count, each `AIDirectorChunkEvent.Write`, then
`cooldownDelay` (f32); `Read` (IL=36) mirrors it and only reads
`cooldownDelay` at inner version >= **2**. `get_IsReady` (IL=7) is
`cooldownDelay <= 0` (the spawn gate); `get_EventCount` / `GetEvent(index)`
(IL=4 / 5) expose the list; `get_ActivityLevel` (IL=3) is the field. The ctor
allocates the event list.

**`DecayEvents` (IL=61):** zero `activityLevel`; for each event:
`Value -= Value * (elapsed/Duration)`, `Duration -= elapsed`; remove if
Duration or Value ≤ 0; else re-sum Value into `activityLevel`.

**`FindBestEventAndReset` (IL=44):** pick max-`Value` event; set
`cooldownDelay = **240**` s; `ClearEvents()`; return best (may be null).

**Cooldown setters:**

| Method | IL | Delay |
|---|---:|---|
| `StartNeighborCooldown(false)` | 13 | max(current, **180** s) |
| `StartNeighborCooldown(true)` | 13 | max(current, **720** s) |
| `SetLongDelay` | 4 | **1320** s (hard set) |

## AIDirectorComponent : Object
- `Tick(Double)` IL=1 (virtual base)

## AIDirectorConstants : Object

Static constants carrier, **vestigial in V3.1.0** (verified against the full
assembly dump): declares 29 fields (`DebugOutput`, `kFileVersion`,
`kMaxSupplyCrates`, `kStealthSightDistanceMultiplier`,
`kStealthNighttimeSightDistanceMultiplier`, `kHordeMeterWarn1Threshold`,
`kHordeMeterWarn2Threshold`, `kHordeMeterWarnResetThreshold`,
`kHordeDaySpawnRangeMin/Max`, `kHordeNightSpawnRangeMin/Max`,
`kHordeMeterDecayDelay`, `kHordeMeterDecayRate`,
`kWanderingHordeGlobalStartTime`, `kSpawnWanderingHordeMin/Max`,
`kWanderingHordeGroupSize`, `kWanderingHordeSpawnDistance`,
`kWanderingHordeSpawnMinDistance`, `kWanderingHordePlayerClusterSize`,
`kSoundPriorityStart/Range`, `kScoutSpawnDistance`, `kScoutScreamGraceTime`,
`kScoutScreamAgainTime`, `kScoutSpawnAnotherScoutChance`,
`kScoutSummonedPerScream`, `kScoutSummonedTotal`), but only `DebugOutput` is
ever read or written: `ldsfld` appears solely in `ConsoleCmdAIDirectorDebug`
and `AIDirector` (the console `aidirector.debug` toggle), `stsfld` only in the
`.cctor` and the console command. Every other field is dead in V3.1.0: the
tuned numbers the components actually use are inline literals (wandering-horde
schedule `Random(12000..24000)`, chunk-event cooldowns 180/240/720/1320,
blood-moon party constants, etc. - see the sections above). The `.cctor`
(IL=3) sets only `DebugOutput = 1`.

## `AIDirectorData` : Object

Static noise table for smell / sound attraction.

**Fields:** `Dictionary<String, AIDirectorData/Noise> noisySounds`.

- `InitStatic()` IL=3
- `AddNoisySound(String, Noise)` IL=5
- `FindNoise(String, Noise&)` IL=11 (`TryGetValue`)

## AIDirectorEventsFromXml : MonoBehaviour
- `Update()` IL=1

## AIDirectorGameStagePartySpawner : Object
- `Tick(Double)` IL=52
- `CalcStageSpawnMax()` IL=30
- `IncSpawnCount()` / `DecSpawnCount` IL=7 / 15
- `get_canSpawn()` IL=11

Used by `AIHordeSpawner` and blood-moon party logic for stage-scaled counts.

**`Tick(Double)` (IL=52):** if no `spawnGroup`, return false (finished). Advance
stage when `worldTime >= nextStageTime` (if set) **or** when
`spawnCount >= numToSpawn` and `interval` countdown hits 0; then `groupIndex++`,
`SetupGroup()`. Return true while `spawnGroup != null` (still active).

**`get_canSpawn` (IL=11):** `spawnGroup != null && spawnCount < numToSpawn`.

**`IncSpawnCount` (IL=7):** `spawnCount++`.

**`SetupGroup` (IL=57):** `spawnGroup = stage.GetSpawnGroup(groupIndex)`; if
null, log groups done. Else `interval = spawnGroup.interval`;
`nextStageTime = duration>0 ? worldTime + duration*1000 : 0`;
`numToSpawn = ModifySpawnCountByGameDifficulty(spawnGroup.spawnCount)`;
`spawnCount = 0`.

**`get_maxAlive` (IL=9):** `spawnGroup.maxAlive` or **0** if no group.

**`ResetPartyLevel(mod)` (IL=13):** `level = CalcPartyLevel()`; if `mod != 0`,
`level %= mod`; `SetPartyLevel(level)`.

**`CalcPartyLevel` (instance IL=26):** collect each member `gameStage`; call
static `GameStageDefinition.CalcPartyLevel`.

**`GameStageDefinition.CalcPartyLevel(list)` (IL=35):** sort stages ascending;
from highest to lowest: `sum += stage * weight` then
`weight *= DiminishingReturns` (start `weight = StartingWeight`);
`FloorToInt(sum)`.

**Party leaves:** `SetPartyLevel(level)` (IL=123) applies the game-stage
scaling (`partyLevel *= gsScaling`), resets stage/group/spawn bookkeeping, looks
up `def.GetStage(level)`, and on a valid stage recomputes `stageSpawnMax` +
`SetupGroup()`; `bonusLootEvery = FastMax(stageSpawnMax /
GameStageDefinition.LootBonusMaxCount, LootBonusEvery)`; it logs
`Party of {0}, GS {1} ({2}), scaling {3}, enemy max {4}, bonus every {5}` and
per-member `Player id {0}, gameStage {1}`. `SetScaling(scaling)` (IL=11) is
`gsScaling = FastLerp(1, 2.5, (scaling - 1) / 3)`. `AddMember` (IL=22) dedupes
through the `memberIDs` hashset + members list; `RemoveMember(player, removeID)`
(IL=14) optionally clears the id; `DecSpawnCount(dec)` (IL=15) clamps at 0;
`get_IsDone` (IL=11) is `groupIndex > 0 && spawnGroup == null`.

**`GameStageDefinition` static defaults (`.cctor` IL=12):**
`DifficultyBonus=1`, `StartingWeight=1`, `DiminishingReturns=0.5`,
`DaysAliveChangeWhenKilled=2` (then empty `gameStages` dict).

**`CalcStageSpawnMax` (IL=30):** sum every `SpawnGroup.spawnCount` in the stage
(walks groups 0..Count-1; clobbers field `spawnGroup` during walk).

**`SetPartyLevel(_partyLevel)` (IL=123):** store `partyLevel`; then
`partyLevel = (int)(partyLevel * gsScaling)`; reset `stageSpawnMax`/`groupIndex`/
`spawnCount`; `stage = def.GetStage(_partyLevel)` (original arg, not scaled);
`stageSpawnMax = CalcStageSpawnMax()`; `SetupGroup()`;
`bonusLootEvery = max(stageSpawnMax / LootBonusMaxCount, LootBonusEvery)`.

**`ModifySpawnCountByGameDifficulty(count)` (IL=6, static):** if
`!EntityFactory.EnemySpawnMode` return **0**; else return `count` unchanged
(name does not scale by difficulty).

**`AIDirector.CanSpawn(_priority)` (IL=10):**
`GameStats.EnemyCount (12) < GamePrefs.MaxSpawnedZombies (99) * _priority`
(true = under cap; same formula as [spawning.md](spawning.md)).

## `AIDirectorHordeComponent` : AIDirectorComponent

Shared placement helpers for scout/wandering/chunk hordes.

| Method | IL | Role |
|---|---:|---|
| `FindTargets` | **459** | pick living `AIDirectorPlayerState` targets; compute start / pitStop / end; ground checks via `FindOnGroundPos` + `Chunk.CanMobsSpawnAtPos` |
| `FindScoutStartPos` | 192 | back-away start from end position |
| `FindOnGroundPos` | 131 | snap candidate to spawnable ground |

`FindTargets` pulls the player list exclusively from
`AIDirectorPlayerManagementComponent` (not a raw world player scan).

## AIDirectorMarkerManagementComponent : AIDirectorComponent
- `Tick(Double)` IL=7

**`Tick(dt)` (IL=7)** = base tick + `TickMarkers(dt)` (IL=43): reverse-iterate
the `markers` list; each `IAIDirectorMarker.Tick(dt)` advances, then the
marker is removed and `Release()`d back to its pool when `TimeToLive <= 0`
**or** its owning `Player` died - the smell/sound marker TTL sweep.

## AIDirectorPlayerInventory : ValueType

**Fields:** `List bag`, `List belt` (item id lists used for director interest).

Mirrored from clients via `AIDirector.UpdatePlayerInventory` /
`AIDirectorPlayerManagementComponent.UpdatePlayerInventory`.

**`NetPackagePlayerInventoryForAI`** (direction **1**, client to server) is
the wire carrier: `Setup(entity, inventory)` (IL=9) stores the entity id and
the inventory; `GetLength()` (IL=30) is `8 + 4 * (bag.Count + belt.Count)`;
`write` (IL=18) emits `entityId:i32` then both sets through
`WriteInventorySet` (IL=33: `count:i16`, 0 for a null list, then per entry
`AIDirectorPlayerInventory/ItemId.Write`), and `read` (IL=15) mirrors it
through `ReadInventorySet` (IL=25). `ProcessPackage` (IL=23) no-ops without
a world / `aiDirector`, else calls
`world.aiDirector.UpdatePlayerInventory(entityId, inventory)` - the client's
reduced item-id report that feeds director interest.

## AIDirectorPlayerManagementComponent : AIDirectorComponent

- `Tick(Double)` IL=7 → `TickPlayerStates` IL=24 → per-state `TickPlayerState` IL=6
- `UpdatePlayerInventory(Int32, AIDirectorPlayerInventory)` IL=11
- `UpdatePlayerInventory(EntityPlayerLocal)` IL=7

Owns the live `DictionaryList` `trackedPlayers` that horde targeting reads.
`TickPlayerState` only mirrors `Player.IsDead()` into `set_Dead` (no inventory
or underground work on this path).
`AddPlayer(player)` (IL=23) skips an already-tracked id, pools an
`AIDirectorPlayerState` and stores `Construct(player)` keyed by entity id;
`RemovePlayer(player)` (IL=21) removes the entry, `Reset()`s and returns the
state to the pool.

## `AIDirectorPlayerState` : Object

**Fields:** `EntityPlayer Player`, `AIDirectorPlayerInventory m_inventory`,
`Boolean m_dead`, plus underground-check constants
(`kCheckUndergroundTime`, `kNumBlocksUnderground`).

| Method | IL |
|---|---:|
| `Construct(EntityPlayer)` | 8 |
| `Reset` | 4 |
| `Cleanup` | 1 |
| `get/set Inventory` | 3 / 4 |
| `get/set Dead` | 3 / 4 |

`Dead` is consulted repeatedly inside `FindTargets` when building the living
target list.

## AIDirectorPooledMarker : MonoBehaviour
- `Update()` IL=1

## AIDirectorPrivateData : Object

## AIDirectorSmellMarker : Object
- `Tick(Double)` IL=71
- 22 methods in the type surface (pathing/smell bookkeeping); static noise names resolve through `AIDirectorData.FindNoise`

**`Tick(dt)` (IL=71):** decays `m_ttl` and `m_validTime` (both clamped at 0) and
advances `m_time` (capped at `m_lifetime`). The effective model:
`m_effectiveRadius = m_speed > 0 ? min(m_radius, m_speed * m_time) :
m_radius` (a smell cloud that expands from the source at `m_speed` up to its
`m_radius`), and `m_effectiveStrength = m_strength * (1 - m_time /
m_lifetime)` (linear strength decay over the lifetime).

## AIDirectorWanderingHordeComponent : `AIDirectorHordeComponent`
- `Tick(Double)` IL=17
- `TickActiveSpawns(Single)` IL=43
- `TickNextTime(UInt64&, SpawnType)` IL=74
- `StartSpawning(SpawnType)` IL=124
- `get_HasAnySpawns()` IL=6
- `get_OtherHordesAreActive()` IL=9: `SkyManager.IsBloodMoonVisible() ||
  Director.GetComponent<AIDirectorChunkEventComponent>().HasAnySpawns()` (other
  horde traffic suppresses a new wandering horde)
- `SetNextTime(SpawnType, UInt64)` IL=13: `Bandits` (0) writes
  `BanditNextTime`, `Horde` (1) writes `HordeNextTime`

**`Tick` (IL=17):** playtest → return; base tick; `TickActiveSpawns`;
`TickNextTime(HordeNextTime, type=1)` (horde schedule; bandit is separate).

**`TickActiveSpawns` (IL=43):** reverse-iterate `spawners`;
`AIWanderingHordeSpawner.Update`; on finish log + `Cleanup` + `RemoveAt`.

**`TickNextTime(nextTime, spawnType)` (IL=74):** if GameStats **32** or **24**
off, zero `nextTime` and return. If `nextTime == 0` and `worldTime > 28000`,
`ChooseNextTime`. Else if remaining hours (`(next-now)/1000`) &lt; **7**: if
other hordes active, push `nextTime` by `(7 - hours)*1000`; else if due and
players present `StartSpawning`, else `ChooseNextTime`.

**`ChooseNextTime` (IL=40):** type 0 bandit: `BanditNextTime = now +
Random(12000..24000) + 2000`. Type 1 horde: `HordeNextTime = now +
Random(12000..24000)` (no +2000).

**`StartSpawning` (IL=124 high-level):** log; `CleanupType`; require living
tracked players; on fail delay +4000; `FindTargets` → on fail delay +1000 and
`ChooseNextTime`; else create `AIWanderingHordeSpawner` and add to list
(+12000 residual schedule in IL).

**Leaves:** `InitNewGame` (IL=12) latches `isPlaytest = IsPlaytesting()` and
zeroes both next-times. `Write` (IL=12) persists `HordeNextTime` then
`BanditNextTime` (u64 each) after the base; `Read` (IL=16) mirrors and gates
`BanditNextTime` on version **> 3**. `CleanupType(type)` (IL=30) reverse-walks
the spawner list and `Cleanup()`s + removes matching-type spawners.
`LogTimes` (IL=17) logs `Next wandering - bandit {0}, horde {1}` via `LogAI`.

**`AIWanderingHordeSpawner`:** ctor (IL=76) picks the group name
`WanderingBandits` (type 0) / `WanderingHorde` (type 1), builds a
`AIDirectorGameStagePartySpawner` over the group, adds every target player as a
member, resets the party level (50 for hordes, 0 for bandits) and clears
members (pure level seeding). `Update` (IL=101): returns done when no players;
when `worldTime >= endTime` or the spawn phase finished with an empty command
list it fires `arrivedCallback` and finishes; a not-yet-spawning run registers
an `AstarManager.AddLocationLine(startPos, endPos, 64)`; otherwise
`UpdateHorde` drives the zombies. `UpdateSpawn` (IL=158): gates on
`AIDirector.CanSpawn(1)` + `spawner.Tick(dt)` + `canSpawn`, a 1 s `spawnDelay`,
a spawn point from `GetMobRandomSpawnPosWithWater(startPos, 1, 6, 15, true)`,
and `GetRandomEntityFromGroupMaxTier(spawnGroupName, MaxEntityTier, ref
lastClassId, isEnemy, isAnimal, null)` (-1 logs the max-tier warning and fails);
the created `EntityEnemy` becomes a horde zombie with an investigate order
toward the pit stop. `UpdateHorde(dt)` (IL=189) is the three-command state
machine per zombie (`Walk` → `Wander` → `Endstop`): the walk leg re-affirms the
pit-stop investigate target (divergence or an attack target drops the zombie
from control), the wander leg counts `WanderTime = 90 + RandomFloat * 4`
(refreshing the despawn timer), and the endstop leg targets
`RandomPos(endPos, 6)` and clears `IsHordeZombie`; any released zombie has
`bIsChunkObserver` cleared before `RemoveAt`. `Cleanup` (IL=24) releases every
remaining zombie's horde flags. `RandomPos` (IL=15) is
`target + RandomOnUnitCircle * radius` (y = 0).

## AIHordeSpawner : Object

Screamer / event horde runner (not an `AIDirectorComponent`, but driven from
director/spawn paths; see [spawning.md](spawning.md)).

**`Tick(Double)` (IL=228):**

1. Finished (true) if no players **or** `!AIDirector.CanSpawn(1)`.
2. First tick only (`!isInited`): bounds = `targetPos ± playerSearchBounds`;
   `GetEntitiesInBounds(EntityPlayer)`; `AddMember` if not `IsIgnoredByAI`.
   If `partyMembers.Count == 0`, return **false** (wait). Else `isInited=true`,
   `ResetPartyLevel(0)`, `ClearMembers()` (level sampled while members present).
3. Every tick: if `spawner.Tick(dt)` is **false**, finished (true). Party Tick
   true means still active.
4. If `!canSpawn` or `numSpawned >= numToSpawn`, return false (idle hold).
5. Else one spawn attempt: day `GetMobRandomSpawnPosWithWater` **45/55/45** else
   **55/70/55**; `GetRandomEntityFromGroupMaxTier(spawnGroupName,
   MaxEntityTier)`; `CreateEntity` + `SetSpawnerSource(Dynamic=3)` +
   `SpawnEntityInWorld`; `IsHordeZombie`/`bIsChunkObserver`; investigate
   `RandomPos(target, 3)` for **2400** ticks; `hordeList.Add`;
   `IncSpawnCount`; `numSpawned++`; return false.

**ctor (IL=20):** builds `spawner = new AIDirectorGameStagePartySpawner(world,
spawnerDefinition)` and stores `targetPos` + `playerSearchBounds`.
`get_isSpawning` (IL=4) is `spawner.canSpawn`; `Cleanup` (IL=25) clears
`IsHordeZombie` / `bIsChunkObserver` on every tracked zombie and empties
`hordeList`.

## AIDirectorZombieState : Object

`IMemoryPoolableObject` wrapper around a single `EntityEnemy m_zombie` field.
**Orphaned in V3.1.0** (verified): the type is referenced from nowhere else in
the full assembly dump - no `newobj`, no method call, no field use. It is a
leftover of an earlier managed-zombie design; the current `ManagedZombie`
entries in `AIDirectorBloodMoonParty` / `AIHordeSpawner` are a nested
`(EntityPlayer player, EntityEnemy zombie, Single updateDelay)` carrier with
their own iteration (see those sections). Methods: `Construct(EntityEnemy)`
(IL=5) stores the reference, `Reset()` (IL=4) nulls it, `Cleanup()` (IL=1) is
empty, `get_Zombie()` (IL=3) returns it.

## Network and save surfaces (verified)

### AIDirector save blob

`AIDirector.Save` (IL=7): writes version int **10**, then
`ComponentsSave` walks installed components and calls each `Write`.

`AIDirectorBloodMoonComponent.Write` (IL=20): base component write, then
`bmDayLast:i32`, `bmDay:i32`, `BloodMoonFrequency:i16`, `BloodMoonRange:i16`.
This blob rides `WorldState` nested `aiDirectorState` ([save-region.md](save-region.md)).

### Sleeper / bloodmoon packages

| Package | Wire | Process |
|---|---|---|
| `NetPackageSleeperWakeup` | `targetId:i32` | remote client: `EntityAlive.ConditionalTriggerSleeperWakeUp` |
| `NetPackageSleeperPose` | `targetId:i32`, `pose:u8` | sleeper pose sync |

**`NetPackageSleeperPose.ProcessPackage` (IL=23):** runs only on a
non-remote world (the server); it resolves the target `EntityAlive` and
calls `TriggerSleeperPose(pose, false)` - the sleeper's crouch/lie pose
applied when a client syncs a sleeper's animation state.
| `NetPackageSleeperPassiveChange` | EntityTargeted id only (`Setup(targetId)`) | remote: `IsSleeperPassive=false` |
| `NetPackageBloodmoonMusic` | `IsBloodMoonMusicEligible:bool` | sets `World.dmsConductor.IsBloodmoonMusicEligible` |
| `NetPackageHordeEvent` | `m_event`, `m_maxDist` | client `HandleHordeEvent` if in range |
| `NetPackageGameStats` | `len:i16` + `GameStats.Write` blob of **persistent** property decls (int/float/string/base64-string/bool) | client `readStatsCo` coroutine |

## Blood-moon window, party spawner and client-side FX (2026-08-06)

Status: **verified** against a full V3.1.0 b14 disassembly (2026-08-05 dump; line
numbers are from that dump; the tracked `il/` sets are the V3.1.0 corpus).

### Time and the blood-moon window

`GameUtils::WorldTimeToDays` (1925943) is `worldTime / 24000 + 1`, so the wire day
is 1-based and day N spans `[(N-1)*24000, N*24000)`. `GameUtils::DayTimeToWorldTime`
(1926175) is the inverse: `(day - 1) * 0x5dc0 + hours * 0x3e8 + minutes * 1000 / 60`.
`WorldTimeToHours` (1925958) is `(wt / 1000) % 24`; `WorldTimeToMinutes` (1925972)
is `(wt / 1000.0 * 60) % 60`. Any server-side day counter must subtract 1 before
encoding.

More time conversions: `DaysToWorldTime(day)` (IL=15) is `(day - 1) * 24000`
(0 for `day < 1`); `DaysToWorldTimeMidnight(day)` (IL=6) adds **16000** ticks
(16:00); `WorldTimeToTotalSeconds(wt)` (IL=4) is `wt * 3.6` (1 tick = 3.6 s at
the 1000-ticks-per-hour scale); `WorldTimeToTotalMinutes(wt)` (IL=7) is
`(uint)(wt * 0.06)` and `TotalMinutesToWorldTime(min)` (IL=7) divides by the
same 0.06; `WorldTimeToHourMinutesString(wt)` (IL=14) formats
`{hour:D2}:{minute:D2}` from `WorldTimeToElements`.

`GameUtils::IsBloodMoonTime(duskDawn, hour, bmDay, day)` (1926341) returns true
when `day == bmDay && hour >= duskHour`, **or** when
`day > 1 && day == bmDay + 1 && hour < dawnHour`. The blood moon therefore spans
dusk on `bmDay` to dawn on `bmDay+1`, crossing the midnight day rollover.
`GameUtils::WorldTimeToElements(wt)` (1925958) = `(wt/24000 + 1,
(wt/1000) % 24, (int)(wt * 0.06) % 60)` - the `(day, hour, minute)` tuple used
by the time gates.

`GameUtils::CalcDuskDawnHours` (1926249): a `DayLightLength` of 0 or 24 returns
(dusk 22, dawn 4); otherwise dusk starts at 22, is clamped to `DayLightLength` when
`DayLightLength > 22`, becomes `12 + DayLightLength/2` when `DayLightLength < 18`,
and dawn is `clamp(dusk - DayLightLength, 0, 23)`.

`World.DuskDawnInit` (IL=13) writes the dusk/dawn fields the gates read: it
loads `GameStats` `DayLightLength`, runs it through `CalcDuskDawnHours`, and
stores the pair into `World.DuskHour` / `World.DawnHour`.

`World.SetTimeJump(time, isSeek)` (IL=14) is the clock-jump entry: `SetTime`,
flags `SkyManager.bUpdateSunMoonNow`, and on the server calls
`AIDirectorBloodMoonComponent.TimeChanged(isSeek)` so the blood-moon schedule
re-evaluates against the jumped time (the seek flag marks an artificial jump).

### Schedule

`AIDirectorBloodMoonComponent::CalcNextDay` (412880) picks
`nextBM = bmDayLast + BloodMoonFrequency + GameRandom.RandomRange(0, BloodMoonRange+1)`.
The jitter is strictly **non-negative**, so a stock blood moon is never early
relative to the frequency multiple. `InitNewGame` (412068) seeds
`bmDayLast = ((currentDay - 1) / 7) * 7` with a literal 7, independent of
`BloodMoonFrequency`.

`Tick` (412099) also polls GameStats 58 while the blood moon is inactive and, if
the stat changed underneath it, resets `bmDay` and logs
`Blood Moon day stat changed {0}`: the server-side component itself follows an
externally set BloodMoonDay stat. It gates all party spawning on
`GameStats.GetBool(24)` (EnemySpawnMode).

There is **no `bloodmoon` console command in V3.1.0**. The only caller of
`SetForToday` is the gameevents sequence action
`GameEvent.SequenceActions.ActionSetHordeNight` (2573467), whose `keepBMDay`
property stashes the old `bmDay` into `bmDayNextOverride`.

### Start / end and the party spawner

**`IsBloodMoonTime(worldTime)` (IL=10):**
`GameUtils.IsBloodMoonTime(worldTime, (duskHour, dawnHour), bmDay)`.

**`StartBloodMoon` (IL=70):** log day; `ClearParties()`; clear
`IsBloodMoonDead` on every tracked player; `delay = 0`; for every world
`EntityEnemy` set `IsBloodMoon = true` and `timeStayAfterDeath /= 3`.

**`EndBloodMoon` (IL=73):** log; `isBloodMoon = false`; if `bmDayNextOverride > 0`
apply via `SetDay` and clear override; if current day &gt; `bmDay` stash
`bmDayLast` and `CalcNextDay(false)`; `ClearParties()`; for every `EntityEnemy`
clear `bIsChunkObserver`, `IsHordeZombie`, `IsBloodMoon` (no kill/despawn).

**`get_IsEmpty` (IL=9):** true when `partyMembers.Count == 0`.

**`KillPartyZombies` (IL=48):** `DecSpawnCount(zombies.Count)`; kill each live
non-despawned zombie with `DamageResponse.New(true)`; clear list.

**`ClearParties` (IL=25):** `nextParty = 0`; clear `parties` list; null every
player's `bloodMoonParty`.

**`SetDay(day)` (IL=45):** `GameStateManager.SetBloodMoonDay(day)` if present;
if day changed store `bmDay` and log freq/range.

**`CalcNextDay(isSeek)` (IL=82):** if `BloodMoonFrequency <= 0` set day **0**.
Else step = frequency + `RandomRange(0, range+1)`. Walk `bmDayLast` forward so
`bmDayLast + step` is after current day (clamp last ≥ 0). If `isSeek` and
current `bmDay` still in `[bmDayLast, bmDayLast+freq+range]` keep that day;
else `SetDay(computed)`.

`AIDirectorBloodMoonParty` constants (413090-413140): `cPartyJoinDistance` 80
(sq 6400), `cSightDist` 100, `cTeleportDist` 150 (sq 22500), `cSpawnPreferredArc`
120, `cSpawnAngle` 90, `cSpawnDistance` 40, `cSpawnMinRandDistance` 0,
`cSpawnMaxRandDistance` 10, `cSpawnMinPlayerDistance` 30. Component constants
(412041): `cPartyEnemyMax` 30, `cTimeStayAfterDeathScale` 3, `cSpawnDelay` 1.

**`AIDirector.AddEntity` / `RemoveEntity` (IL=10 each):** only players →
`AddPlayer` / `RemovePlayer`.

**`AIDirector.AddPlayer` (IL=9):**
`playerManagementComponent.AddPlayer` then `BloodMoonComponent.AddPlayer`.

**`PlayerManagement.AddPlayer` (IL=23):** if id not tracked, pool-alloc
`AIDirectorPlayerState.Construct` into `trackedPlayers`.

**`BloodMoonComponent.AddPlayer` (IL=5):** append component `players` list only.
Party attach is **`AddPlayerToParty` (IL=55):** if already member of a party
`AddPlayer`; else `TryAddPlayer` on each party (join if any member within
sqr **6400** = 80 m); else `CreateNewParty`.

**`TryAddPlayer` (IL=34):** walk `partyMembers`; if distSq ≤ **6400** call
`AddPlayer` (spawner `AddMember` + set `player.bloodMoonParty`) and true.

**`CreateNewParty` (IL=8):** `parties.Add(new BloodMoonParty(player, this,
BloodMoonEnemyCount))`.

**`BloodMoonParty..ctor` (IL=41):** zombies list; `spawnWorld`/`spawnBasePos` from
player; `partySpawner = new GameStagePartySpawner(world, "BloodMoonHorde")` +
`AddMember(player)`; set `player.bloodMoonParty`; random `spawnBaseDir` 0..359;
`groupIndex = -1`. Third ctor arg unused.

**`PlayerLoggedOut` (IL=16):** `RemoveMember(player, removeID=false)` (keeps id
in set); clamp `nextPlayer` into member count.

**`AIDirector.Tick` (IL=6):** `ComponentsTick` all components then `DebugTick`.

**`BloodMoonComponent.Tick` (IL=170):** base tick; recompute `isBloodMoon` via
`IsBloodMoonTime`; edge → `StartBloodMoon` / `EndBloodMoon`. If not BM, sync
`bmDay` from GameStats **58**. If BM and GameStats **24** (spawn enemies):
`delay -= dt`; ensure every spawned player has a party (`AddPlayerToParty`);
round-robin parties: empty → `KillPartyZombies` and maybe advance `nextParty`;
else `party.Tick(world, dt, canSpawn=(this==nextParty && delay<=0))`; on spawn
window success set `delay = 1/partyCount` and advance `nextParty`.

**`AIDirector.RemovePlayer` (IL=9):** PlayerManagement then BloodMoonComponent
remove.

**`PlayerManagement.RemovePlayer` (IL=21):** remove tracked state, `Reset`,
pool `Free`.

**`BloodMoonComponent.RemovePlayer` (IL=24):** remove from `players`; every
party `PlayerLoggedOut(player)`.

**`GameStagePartySpawner.AddMember` (IL=22):** ensure id in `memberIDs` and
player in `members` list.

**`RemoveMember(player, removeID)` (IL=14):** remove from `members`; if
`removeID` also drop from `memberIDs`.

`InitParty` (IL=49): `enemyActiveMax = min(30, BloodMoonEnemyCount *
partyMemberCount)`; scale factor `max(1, totalCount/enemyActiveMax)` then
`FastLerp(1, that, partyLevel/60)` into `SetScaling`; `SetPartyLevel(level)`;
`bonusLootSpawnCount = bonusLootEvery / 2`.

**`SetScaling(_scaling)` (IL=11):**
`gsScaling = FastLerp(1, 2.5, (_scaling - 1) / 3)` (clamps growth of stage
level via later `SetPartyLevel` multiply).

**`AIDirectorBloodMoonParty.Tick` (IL=162):** if `partyLevel < 0` `InitParty`.
Reverse walk zombies: `updateDelay -= dt`; when ≤0 reset to **1.8** and
`SeekTarget` (remove on false). Always `partySpawner.Tick(dt)`. If `_canSpawn`
and `canSpawn` and members &gt; 0 and `CanSpawn(1.9)`: on new `groupIndex`
add **120** to `spawnBaseDir` and `CalcBestDir(spawnBasePos)`. Cap alive at
`min(maxAlive, enemyActiveMax)`. Try up to `min(3, memberCount)` players via
rotating `nextPlayer`; first successful `SpawnZombie` stops the try loop.
Return true if a spawn attempt window ran.

**`CalcBestDir(basePos)` (IL=161):** score **16** directions at **22.5°** steps.
For each angle set `spawnDirectionV = forward*40` rotated; try **9**
`GetRandomSpawnPositionMinMaxToPosition(base+dir, 0, 10, 30, ...)` samples;
success count `s`; if `s > 0` score = `(s+2)/3`, and if
`|DeltaAngle(angle, spawnBaseDir)| <= 60` multiply score by **3**. Pick random
among max-score bins; store that bin's `spawnDirectionV`.

**`IsPlayerATarget(player)` (IL=29):** false if dead, not spawned, or
`entityId == -1`; false if `IsIgnoredByAI`; false if `Progression.Level <= 1`
or `IsBloodMoonDead`; else true (BM-valid living party member).

**`FindPartyTarget(fromPos)` (IL=46):** walk `partyMembers` reverse; among
`IsPlayerATarget` pick minimum `sqrMagnitude` to `fromPos`; null if none.

**`SeekTarget(ManagedZombie)` (IL=167):** false if zombie null/dead/despawned/no
GO. Prefer current `GetAttackTarget` player into `mz.player`; if not
`IsPlayerATarget`, `FindPartyTarget(zombie.pos)`. No player: if not
`IsPlayerAliveAndNear(pos, **60**)` → `Kill` false; else true (wander).
With player: horizontal distSq &gt; **22500** (150 m): `CalcSpawnPos` at player
with `spawnDirectionV`; if calc ok and zombie still not near any player **70** m:
50% → `DecSpawnCount(1)`, `lootDropProb=0`, `Kill` false; else teleport
`SetPosition` + `moveHelper.Stop`. Then if full distSq ≤ **10000** (100 m) **or**
attack target player differs from `mz.player`:
`SetAttackTarget(player, **1200**)` ticks; else clear old attack target and
`SetInvestigatePosition(player.pos, **1200**, true)`. Return true.

**`CalcSpawnPos` (IL=28):** rotate `_radiusV` by random yaw in **±45°**
(`(RandomFloat-0.5)*90` about up); focus+rotated radius into
`GetMobRandomSpawnPosWithWater(center, min=0, max=10, height=30, noWater=false)`.

`Tick` gates every spawn on `AIDirector::CanSpawn(1.9f)`: this is the 1.9x
`MaxSpawnedZombies` blood-moon budget the stock serverconfig comment refers to. On
each new spawn group it advances `spawnBaseDir` by +120 degrees and recomputes
`CalcBestDir`, which is why stock waves come from rotating directions.

**`get_BloodmoonZombiesRemain` (IL=6):** true if managed `zombies` list count
&gt; 0.

**`IsMemberOfParty(entityId)` (IL=5):** delegate to
`partySpawner.IsMemberOfParty` (`memberIDs` HashSet.Contains).

`SpawnZombie` (IL=181): `CalcSpawnPos` or fail. Pick class from
`GetRandomEntityFromGroupMaxTier(spawnGroupName, MaxEntityTier, lastClassId,
true, false, null)`. If target `AttachedToEntity` and `RandomFloat < 0.5`:
force class `animalZombieVultureRadiated` and skip bonus-loot counter path.
Missing class → log + false. Then `CreateEntity` → `SetSpawnerSource(3)`,
`SpawnEntityInWorld`, `IsHordeZombie=true`, `IsBloodMoon=true`,
`bIsChunkObserver=true`, `timeStayAfterDeath /= 3`. Non-vulture: increment
`bonusLootSpawnCount`; when `>= partySpawner.bonusLootEvery` reset counter and
`lootDropProb *= LootBonusScale`. Wrap `ManagedZombie`, `SeekTarget`,
`IncSpawnCount`, `AstarManager.AddLocation(pos, 40)`. Log day/time.
`bonusLootEvery = max(stageSpawnMax / LootBonusMaxCount, LootBonusEvery)`.

### Client-side FX: entirely local, driven by three values

`SkyManager::OnGameStatsChanged` (2042093) latches `SkyManager::bloodmoonDay` from
`EnumGameStats 58` (BloodMoonDay) and `duskTime`/`dawnTime` from
`EnumGameStats 42` (DayLightLength). `SkyManager::IsBloodMoonVisible` (2041922)
then tests `GameUtils::IsBloodMoonTime` with a **widened** window of
`(duskTime - 4, dawnTime + 2)`. The whole blood-moon sky FX is client-local: a
server only needs BloodMoonDay, DayLightLength and WorldTime to be correct.

The blood-moon warning is a pure client HUD effect with **no packet**:
`XUiC_CompassWindow` (~1574299) sets the clock text colour to FF0000 when
`GameStats[BloodMoonDay]` equals the client's current day and
`World::BloodMoonWarningHour <= hour`. `World::BloodMoonWarningHour` defaults to 8
in `World::.cctor` (1248240) and is otherwise set by
`SandboxOptionManager::SetupBloodMoonWarningTimes` (2502629) from SandboxOptions 50
to -1 (off), 8, or 18. `EnumGameStats.BloodMoonWarning` (61 / 0x3D) is read by
exactly one consumer, `GameSenseManager::SessionStarted` (1913041), the SteelSeries
LED integration: nothing in the HUD or sky reads it.

`DynamicMusic.Conductor.Update` (2593714/2593767/2593807) is the **only** sender of
`NetPackageBloodmoonMusic` in the whole assembly. Eligibility per player is
`(max gameStage across partyMembers > 1) AND (partySpawner not IsDone OR party
BloodmoonZombiesRemain)`; it is cached in `PlayerEligibleForBloodmoonCache` and
sent only on change, per-entity, with SendPackage flags 0xc0.
`NetPackageBloodmoonMusic::ProcessPackage` (807889) does nothing but assign
`World.dmsConductor.IsBloodmoonMusicEligible`.

The client applies `EntityAlive.IsBloodMoon` by dividing
`DismemberedPart.lifeTime` by 3 in `AvatarController` (59416 and 76551), but
`IsBloodMoon` is set only on the server-side entity and appears in **no** NetPackage
write, so on a dedicated server the client never learns it.

`NetPackageHordeEvent` now occupies 822185-822359 in this dump. There is still no
`GetPackage<NetPackageHordeEvent>()` anywhere, confirming the class is vestigial in
V3.1.0 b14.

### Where the options come from in V3.1.0

The shipped dedicated-server `serverconfig.xml` no longer exposes
`BloodMoonFrequency` / `BloodMoonRange` / `BloodMoonEnemyCount` as properties at
all: the only blood-moon line is `TwitchBloodMoonAllowed`. Those three come from
the `SandboxCode` string (default `AAAJABJACJADJARFBNC`) via
`SandboxOptionManager::UpdateInGameValuesWithSandboxOptions` (2501770), which
copies SandboxOptions 48/49/51 into the `AIDirectorBloodMoonComponent` statics.

`ConsoleCmdSetTime` (251838, help at 251877) accepts four forms: `settime day` =
day 1 12:00, `settime night` = day 2 00:00, `settime <time>` = raw world time where
1000 == one hour, and `settime <day> <hour> <minute>` with day>=1, hour<=23,
minute<=59.

**Console-debug leaves (all IL-verified):** `DebugTick()` (IL=7) and
`DebugFrameLateUpdate()` (IL=7) drive the two debug emitters when the
`debugSendNameInfoToPlayerIds` / `debugSendLatencyToPlayerIds` lists are
non-empty. `DebugToggleSendNameInfo(playerId)` (IL=45) toggles the player in
the name-info list, logs `DebugToggleSendNames {0} on/off` and on the off
side broadcasts `NetPackageDebug.Setup(3, -1, null)` (channel 192);
`DebugSendNameInfo()` (IL=110) is the throttled sender (a 5-tick
`debugNameInfoTicks` counter). `DebugToggleSendLatency(playerId)` (IL=52)
toggles the latency list, sending `NetPackageDebug.Setup(1, -1, null)` on
the off side (falling back to `DebugLatencyOff()` for the primary player);
`DebugLatencyOff()` (IL=42) destroys the `DebugLatency` child transform on
every `EntityAlive`. `DebugToggleFreezePos()` (IL=14) flips the static
`debugFreezePos` flag and logs it. `LogAIExtra(format, args)` (IL=6) routes
to `LogAI` only when `AIDirectorConstants.DebugOutput` is set.

---

## Related docs

| Doc | Role |
|---|---|
| [entity-ai.md](entity-ai.md) | AI throttle |
| [closed-gaps.md](closed-gaps.md) | Default components |
| [spawning.md](spawning.md) | Scout/screamer horde lifecycle |

## Changelog

- **2026-08-11:** Air-drop IL re-verified: SpawnAirDrop IL=59, SpawnSupplyCrate IL=77, Tick IL=75, AIAirDrop.Tick IL=193, CreateFlightPaths IL=355, MakePlayerClusters IL=70, CalcSupplyDropMetrics IL=53, FindSafePoint IL=70, SpawnPlane IL=74 (exact).
- **2026-08-11:** Supply-crate IL re-verified: PostInit IL=35, OnEntityActivated IL=18, canDespawn IL=2, MoveEntityHeaded IL=35, Update IL=39, ValidateResources IL=23, StopSmokeAndLights IL=77, RequiresChunkObserver IL=8, InitLocalActivationCommands IL=8, AllowActivationCommand IL=20, GetActivationText IL=81, HandleNavObject IL=64, OnEntityUnload IL=17 (exact).
- **2026-08-11:** Supply-plane IL re-verified: SetDirectionToFly IL=12, OnUpdatePosition IL=49, UpdateFarDraw IL=35, MoveBoundsInsideFrustrum IL=31 (exact).
- **2026-08-11:** Blood-moon IL re-verified: Tick(Double) IL=170, Tick(World,Double,Boolean) IL=162, SpawnZombie IL=181, CalcSpawnPos IL=28, AddPlayerToParty IL=55, TryAddPlayer IL=34, AddPlayer(Party) IL=8, RemovePlayer IL=24, AIDirectorChunkData.Tick(Single) IL=23, DecayEvents IL=61 (exact).
- **2026-08-11:** AIDirector core IL re-verified: Tick IL=6, ComponentsTick IL=21, DebugTick IL=7, CreateComponents IL=31, CanSpawn IL=10, UpdatePlayerInventory IL=5/6, GetActivityWorldTimeDelay IL=16, ComponentsInitNewGame IL=20, NotifyIntentToAttack IL=1, AddEntity IL=10, AddPlayer IL=9, RemovePlayer IL=9, GetComponent IL=19, Save IL=7 / ComponentsSave IL=21 / Load IL=14 / ComponentsLoad IL=22, NotifyNoise IL=84, NotifyActivity IL=31 (exact).
- **2026-08-11:** CreateComponents install order re-verified: Marker, Player, WanderingHorde, AirDrop, ChunkEvent, BloodMoon (IL_0001-0024, exact).
- **2026-08-11:** Sleeper IL re-verified: NetPackageSleeperPose.ProcessPackage IL=23 (exact).
- **2026-08-11:** Scout-horde IL re-verified (6): CheckToSpawn 18, NotifyEvent 22, AIScoutHordeSpawner.Update 22, SpawnUpdate 129, UpdateHorde 229, spawnHordeNear 94 (exact).
- **2026-08-11:** Zombie-sense IL re-verified: ChunkEventComponent.TickActiveSpawns IL=66, SpawnScouts IL=76, ChunkData.DecayEvents IL=61, FindBestEventAndReset IL=44 (exact).
- **2026-08-11:** Chunk-event IL re-verified: AIDirectorChunkEventComponent.Read IL=37, Write IL=33, Clear IL=7, CreateHorde IL=10, ChunkData.Tick IL=23 (exact).
- **2026-08-11:** Blood-moon party IL re-verified: CalcSpawnPos IL=28, TryAddPlayer IL=34, AddPlayer IL=8, Component.AddPlayerToParty IL=55 (exact).
- **2026-08-11:** Plane/blood-moon IL re-verified: SetDirectionToFly IL=12, OnUpdatePosition IL=49, UpdateFarDraw IL=35, BloodMoonComponent.Tick IL=170 (exact).
- **2026-08-11:** AIAirDrop IL re-verified: Tick IL=193, CreateFlightPaths IL=355, MakePlayerClusters IL=70, CalcSupplyDropMetrics IL=53 (exact).
- **2026-08-11:** Air-drop IL re-verified: AIDirectorAirDropComponent.SpawnAirDrop IL=59, SpawnSupplyCrate IL=77, canDespawn IL=2, MoveEntityHeaded IL=35 (exact).
- **2026-08-11:** AIDirector IL re-verified: NotifyNoise IL=84, NotifyActivity IL=31, AddEntity IL=10, GetComponent IL=19 (exact).
- **2026-08-10:** AIDirector IL sizes re-verified: CanSpawn IL=10, CreateComponents IL=31 (exact).
- **2026-08-09:** Depth pass: AIDirectorChunkData cooldown literals (240 / 1320
  long / 180-720 neighbor) + DecayEvents linear decay; AIDirectorConstants
  verified vestigial (only DebugOutput read/written, rest dead); AIDirectorZombieState
  verified orphaned (no references in full assembly).
- **2026-08-08:** AIScoutHordeSpawner internals: SpawnUpdate (IL=129)
  SpawnManually + scout flags + investigate; UpdateHorde cycle;
  spawnHordeNear (IL=94) 5-zombie horde with 12% wave-reset, sound alert,
  SetSpawnPos; CalcRandomPos; Cleanup release.
- **2026-08-08:** AIHordeSpawner ctor/cleanup: party-spawner build +
  playerSearchBounds; isSpawning = canSpawn; Cleanup releases horde flags.
- **2026-08-08:** AIDirectorChunkData persistence/accessors: Write v2
  (activity + events + cooldownDelay) / Read inner >= 2; IsReady cooldown gate;
  EventCount/GetEvent/ActivityLevel.
- **2026-08-08:** ChunkEventComponent leaves: 5x5 district keying
  (GetChunkDataFromPosition), StartCooldownOnNeighbors walk, CreateHorde
  append, Write v1 / Read outer-version >= 5, Clear/GetActiveCount; deduped
  the NotifyNoise/NotifyActivity summary to a pointer.
- **2026-08-08:** GameStagePartySpawner leaves: SetPartyLevel (IL=123)
  scaling + stage lookup + bonusLootEvery + party log; SetScaling FastLerp
  1..2.5; AddMember/RemoveMember dedupe; DecSpawnCount clamp; IsDone.
- **2026-08-08:** AIWanderingHordeSpawner: ctor group/party-level seeding;
  Update endTime/arrived + AddLocationLine(64); UpdateSpawn (IL=158) CanSpawn
  + spawnDelay + mob spawn + max-tier pick; UpdateHorde (IL=189) Walk/Wander/
  Endstop state machine (pit-stop re-affirm, 90+rnd*4 wander, RandomPos endstop
  6, horde flag release); Cleanup release.
- **2026-08-08:** WanderingHorde leaves: InitNewGame playtest latch + zeroed
  times; Write/Read persist Horde then Bandit next-times (version > 3 gate);
  CleanupType reverse-walk cleanup; LogTimes.
- **2026-08-08:** AIDirector core leaves: AddEntity/AddPlayer/RemovePlayer
  fan-out; GetComponent by FullName; Save version 10 + ComponentsSave/Load;
  Load Init on zero worldTime; NotifyNoise (IL=84) FindNoise lookup, crouch
  muffling, stealth gate + sleeper check, Sound (3) heat event 240 ticks;
  NotifyActivity gates (IsSpawnEnemies 24 + ZombieHordeMeter 32); blood-moon
  party bookkeeping (AddPlayerToParty/TryAddPlayer 80 m/AddPlayer/RemovePlayer).
- **2026-08-08:** AIDirectorPlayerManagementComponent AddPlayer (IL=23)
  pooled-state track on first sight; RemovePlayer (IL=21) reset + pool free.
- **2026-08-08:** EntitySupplyPlane far-draw: UpdateFarDraw (IL=35) mainCamera
  + planeMesh lazy, MoveBoundsInsideFrustrum (IL=31) mesh bounds inflated by
  |camera - plane| * 1.25 anti-cull; Awake/ctor base-only,
  CanCollideWithBlocks false.
- **2026-08-08:** EntitySupplyCrate rest: MoveEntityHeaded parachute gravity
  0.95 + Update airborne swing + PostInit layer 21 / ValidateResources /
  wasOnGround smoke off; StopSmokeAndLights SupplySmoke loop + SupplyLit off;
  RequiresChunkObserver airborne||isSmokeOn; ctor isSmokeOn true +
  smokeTimeAfterLanding 240; search command allow + GetActivationText
  lootTooltip* + binding markup; HandleNavObject GameStats 53 + NetPackageNavObject
  channel 192; Read/Write version >= 11 wasOnGround + parachute ticks;
  OnEntityUnload Killed -> RemoveSupplyCrate; trivials (CanCollideWithBlocks/
  CanBePushed false, IsSavedToFile true, GetMapObjectType 13).
- **2026-08-08:** AIAirDrop flight logic: Tick IL=193 wait-for-chunks then
  per-path plane + staggered crate spawns; CreateFlightPaths IL=355
  (MakePlayerClusters 30 m, CalcSupplyDropMetrics 1-4 planes, crateY
  min(player.y+180, 276), FindSafePoint >= 600 m from players,
  ClampToMapExtents); SpawnPlane IL=74 supplyPlane entity + SetDirectionToFly
  (20*(len/120+10) ticks); EntitySupplyPlane SetDirectionToFly IL=12
  (motion = dir*6, unreplicated) + OnUpdatePosition IL=49 (ticksToFly
  countdown -> MarkToUnload, engine loop, SetAirBorne).
- **2026-08-08:** Supply crate entity: fallHitGround IL=15 soft landing
  (speed clamp 5, vertical min -0.75); OnEntityDeath IL=30 map-marker
  removal (type 13) + NetPackageEntityMapMarkerRemove broadcast + DropBagServer;
  OnEntityActivated IL=18 search via LockManager LockRequestLocal;
  canDespawn IL=2 always false.
- **2026-08-07:** NotifyNoise (IL=84) sound-to-AI chain: noise-table lookup,
  enemy/ignored/decoy exclusions, crouch muffle, PlayerStealth.NotifyNoise ->
  CheckSleeperVolumeNoise, heat-map NotifyActivity(3, strength*scale, 240);
  OnSoundPlayedAtPosition (IL=17) entry.
- **2026-08-07:** SmellMarker.Tick (IL=71): ttl/validTime decay, time cap,
  effective radius min(radius, speed*time) expansion, effective strength
  strength*(1 - time/lifetime) linear decay.
- **2026-08-07:** MarkerManagementComponent TickMarkers (IL=43): reverse sweep,
  TTL <= 0 or dead owning player -> RemoveAt + Release to pool.
- **2026-08-07:** BloodMoon component+party bodies: Tick (IL=170) edge
  Start/End + stat 58 day change + round-robin party spawn window 1/Count;
  Party.Tick (IL=162) 1.8 s seek cadence + groupIndex 120 dir rotate +
  maxAlive cap + 3-player round robin; SpawnZombie (IL=181) group pick with
  vulture override + bonus loot every + timeStayAfterDeath/3 + log;
  CalcSpawnPos (IL=28) +-45 ring 10-30 m.
- **2026-08-07:** BloodmoonZombiesRemain list count; IsMemberOfParty partySpawner.
- **2026-08-07:** Wandering TickNextTime 28000/7h; ChooseNextTime 12k-24k;
  ClearParties; CalcNextDay; Start/EndBloodMoon; KillPartyZombies.
- **2026-08-07:** get_maxAlive; BM Tick 1.8s SeekTarget + nextPlayer; SetScaling;
  CalcBestDir 16 bins; InitParty; IsPlayerATarget; SeekTarget 1200
  formula; CalcStageSpawnMax; SetPartyLevel gsScaling; CanSpawn cap.
- **2026-08-07:** CalcSpawnPos ±45° radius + GetMobRandomSpawnPosWithWater 0/10/30;
  SeekTarget 60/150/70 m; Scout SpawnUpdate 6000; UpdateHorde 18s.
  and spawnHordeNear path.
- **2026-08-07:** AddEvent value merge; DecayEvents; FindBestEventAndReset
  cooldown 240 s; Flow/Evap damage packing cross-ref liquid.
- **2026-08-07:** SpawnScouts gamestage bands + 120 m player; NotifyEvent queue;
  ChunkData.Tick cooldown/decay.
- **2026-08-07:** NotifyActivity gates (GameStats 32/24, heat sensitivity, BM/
  Twitch skip); CheckToSpawn ActivityLevel 25 and 20% SpawnScouts.
- **2026-08-06:** Blood-moon window spans dusk on bmDay to dawn on bmDay+1
  (`GameUtils::IsBloodMoonTime`); `WorldTimeToDays` is 1-based; CalcDuskDawnHours
  branches; CalcNextDay jitter is non-negative and InitNewGame seeds on a literal
  7; StartBloodMoon/EndBloodMoon entity flag sweeps; AIDirectorBloodMoonParty
  constants, InitParty formulas, CanSpawn(1.9f) budget and the +120 degree spawn
  arc; SpawnZombie bonus-loot and chunk-observer effects; SkyManager /
  XUiC_CompassWindow client-local FX driven by GameStats 58 + 42 with no packet;
  Conductor as the only BloodmoonMusic sender; SandboxCode as the V3.1.0 source of
  Frequency/Range/EnemyCount; ConsoleCmdSetTime four forms; no `bloodmoon` command.

- **2026-07-28:** AIDirector save v10; bloodmoon/sleeper/GameStats packages.

- **2026-07-28:** CreateComponents order from IL; player state fields; chunk-event tick cadence; chunk-event wire; FindTargets; AIHordeSpawner radii; AIDirectorData noise map.
- **2026-07-19:** Related docs table.
