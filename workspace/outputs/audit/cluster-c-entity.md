# Audit: Cluster C — entities / AI / combat / stats (V3.0.1 stable DLL)

**Verdict:** The nine docs are overwhelmingly accurate against the assembly (enums, IL sizes, constants, state machines, and wire bodies all check out), with ONE major error: buffs.md inverts the buff net-sync flow (`AddBuffNetwork`/`RemoveBuffNetwork` are send-side, and the server receive path re-broadcasts), plus four minor imprecisions.

All commands run from repo root with:
`ASM="/home/maci/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll"`

---

## Findings

### [F1] MAJOR — buffs.md §3 "Network sync" (and sequence diagram): buff net-sync direction inverted

> "`AddBuffNetwork`/`RemoveBuffNetwork` are the receive-side entry points (applied without re-broadcasting)"
> "CL->CL: AddBuffNetwork -> apply locally (no re-send)"

Both claims are wrong. Ground truth:

- `mono tools/bin/DumpMethod.exe "$ASM" EntityBuffs AddBuffNetwork` — IL=34: the body is
  `GetPackage<NetPackageAddRemoveBuff>()` → `Setup(entityId, name, duration, adding=1, instigatorId, instigatorPos)` →
  if `ConnectionManager.IsServer`: `SendPackage(..., attachedToEntityId, channel 192)` (`ldc.i4 192` at IL_0045), else `SendToServer`.
  It never touches the buff list. It is the **send** side. `RemoveBuffNetwork` (IL=34) is identical with `adding=0`.
- `mono tools/bin/DumpMethod.exe "$ASM" EntityBuffs AddBuff` — the 238-IL overload calls `AddBuffNetwork` (IL_01C6, IL_0281) when netSync applies; so AddBuff-with-netSync = apply locally + call the network **sender**.
- `mono tools/bin/DumpMethod.exe "$ASM" NetPackageAddRemoveBuff ProcessPackage` — IL=72(+): the actual receive entry point. On the server it **re-broadcasts first** (IL_0004–IL_0067: `IsServer` → rebuild package → `SendPackage(..., channel 192)`), then applies via `EntityBuffs::AddBuff(name, instigatorPos, instigatorId, netSync:false /*ldc.i4.0*/, false, duration)` or `RemoveBuff(name, instigatorId, false)`. A pure client applies without re-send only because its `IsServer` check fails.

**Fix:** rewrite §3: `AddBuff(netSync)`/`RemoveBuff(netSync)` call `AddBuffNetwork`/`RemoveBuffNetwork`, which *construct and send* `NetPackageAddRemoveBuff` (server → broadcast to entity observers on channel 192; client → SendToServer). The receive path is `NetPackageAddRemoveBuff.ProcessPackage`, which on the server relays the package to observers and then applies via `AddBuff`/`RemoveBuff` with `netSync=false`. Redraw the sequence diagram accordingly.

### [F2] MINOR — combat-damage.md §1: `EnumDamageSource` members overstated

> "a `DamageSource`: `EnumDamageSource` (external / internal / entity / ...)"

`grep "^EnumDamageSource" /tmp/.../enums.txt` (from `mono tools/bin/EnumList.exe "$ASM" ...`):
`EnumDamageSource.External=0`, `EnumDamageSource.Internal=1` — that is the entire enum. There is no "entity" member and no further values; the attacker entity id is a separate `DamageSource` field (`DamageSource::getEntityId()` exists, so that part of the sentence is fine).

**Fix:** "(External / Internal — the enum has only these two values)".

### [F3] MINOR — spawning.md §5: horde placement bands attributed to both spawners; scouts use different numbers

> "**Placement.** Mobs spawn at 45/55/45 m (day) or 55/70/55 m (night) via `GetMobRandomSpawnPosWithWater` ..."

The 45/55/45 and 55/70/55 bands exist only in the screamer path:
`mono tools/bin/DumpMethod.exe "$ASM" AIHordeSpawner Tick` — `IsDaytime()` at IL_0151, then `ldc.i4.s 45/55/45` (IL_0164–0168) or `ldc.i4.s 55/70/55` (IL_0182–0186) into `GetMobRandomSpawnPosWithWater`.
The chunk-heat scout spawner's position callback uses different constants:
`mono tools/bin/DumpMethod.exe "$ASM" '<>c__DisplayClass10_0' '<SpawnUpdate>b__1'` —
`GetMobRandomSpawnPosWithWater(startPos, 0, 8, 10, true, out pos)` (ldc.i4.0 / ldc.i4.8 / ldc.i4.s 10), no day/night branch.

**Fix:** scope the 45/55/45 // 55/70/55 bullet to `AIHordeSpawner` (screamer); note scouts spawn via `EntitySpawner.SpawnManually` with a 0..8 band (depth 10) callback.

### [F4] MINOR — vehicles-drones-turrets.md §1: EntityVehicle/EntityDriveable relationship inverted

> "| `EntityVehicle` (`EntityDriveable` subtype) | `EntityAlive` | ..."

`mono tools/bin/DumpType.exe "$ASM" <out> EntityVehicle EntityDriveable`:
`EntityVehicle (base EntityAlive)`; `EntityDriveable (base EntityVehicle)`.
`EntityDriveable` is a subclass **of** `EntityVehicle`, not the other way round.

**Fix:** "`EntityVehicle` (base of `EntityDriveable`)".

### [F5] MINOR — vehicles-drones-turrets.md §5: method name spelling

> "`SpawnFollowingDronesForPlayer` teleports a player's Follow-order drones to them on join"

Actual assembly name (game-code typo): `DroneManager::SpawnFollowingDronesForPLayer(Int32,World)`
(`grep SpawnFollowingDrones methods.txt` from `MethodList.exe`). Exact-name searches against the doc spelling fail.

**Fix:** quote the assembly spelling `SpawnFollowingDronesForPLayer` (sic).

### Unverifiable from IL (flagged, not graded)

- entity-ai.md addenda (2026-07-21/23): measured numbers (19.9 ms/frame animator slice, 22.1 us/zombie/tick, fence/WAIT analysis, `deltaPosition` 0-forever wedge). These are live-probe measurements referencing optimizer RESULTS, clearly marked as measured; not checkable against the DLL. Structural anchors that ARE checkable were verified: `EModelBase.Init` gates `AvatarControllerDummy` on `RootMotion`/`HasRagdoll` (`DumpMethod EModelBase Init`), and the chain `AvatarRootMotion.OnAnimatorMove` / `AvatarController.NotifyAnimatorMove` / `EntityAlive.NotifyRootMotion` / `AvatarController.SyncAnimParameters` all exist (MethodList).
- entity-ai.md D3.4/D3.5 label their float lists as hypotheses/"exact semantics need line-level read"; constants themselves verified (see CONFIRMED list).

---

## Spot-verified CONFIRMED

Enums (`mono tools/bin/EnumList.exe "$ASM" /tmp/enums.txt` + grep):
- `EnumDamageTypes.Suffocation=16` (combat-damage §1); full table None=0..Special=29, COUNT=30.
- `EnumSpawnerSource`: Biome=1, StaticSpawner=2, Dynamic=3 (spawning §1).
- `EnumRemoveEntityReason`: Undef=0 Unloaded=1 Killed=2 Despawned=3 Captured=4 (spawning §3).
- `EnumGameStats.EnemyCount=12`, `AnimalCount=13`, `IsSpawnEnemies=24`, `ZombieHordeMeter=32`; `EnumGamePrefs.MaxSpawnedZombies=99`, `MaxSpawnedAnimals=129`, `DebugStopEnemiesMoving=46` (spawning §1/§9, entity-ai §3.1).
- `eWayPointListType.Vehicle=0 / Drone=1`; `TurretState Asleep/Awake/Overheated = 0/1/2` (vehicles §3/§6).

AIDirector (aidirector.md):
- `DumpMethod AIDirector CanSpawn` — IL=10: `GameStats.GetInt(12) < GamePrefs.GetInt(99) * priority` exactly as spawning.md §1 states.
- `DumpMethod AIDirector .ctor` / `WorldState SetFrom` — `newobj AIDirector::.ctor(World)` in SetFrom; ctor calls `CreateComponents`.
- `DumpMethod AIDirector CreateComponents` — order Marker, PlayerManagement, WanderingHorde, AirDrop, ChunkEvent, BloodMoon (matches diagram M1–M6).
- `DumpMethod AIDirector Tick` — IL=6 = `ComponentsTick` + `DebugTick`.
- Every IL count in the doc re-checked and exact: CanSpawn 10, UpdatePlayerInventory 5/6, AirDrop Tick 75 / SpawnAirDrop 59 / SpawnSupplyCrate 77, BloodMoon Tick 170, BloodMoonParty 162/165/28, ChunkData Tick 23, ChunkEvent Tick 79 / TickActiveSpawns 66 / HasAnySpawns 6 / CheckToSpawn 18 & 46 / SpawnScouts 76, Component Tick 1, GameStagePartySpawner 52/30/7/15/canSpawn 11, HordeComponent bases (`DumpType`: ChunkEvent & WanderingHorde : AIDirectorHordeComponent : AIDirectorComponent), Marker Tick 7, PlayerManagement Tick 7 & UPI 11/7, SmellMarker Tick 71, WanderingHorde 17/43/124/6, EventsFromXml Update 1, PooledMarker Update 1.

entity-ai.md:
- `DumpMethod EntityAlive updateTasks` — IL=125; pref 46 early-out excepting `EntityDrone`; `CheckDespawn`; `seeCache.ClearIfExpired`; `UseAIPackages` EAI/UAI select; `aiActiveDelay -= aiActiveScale`, reset 1.0; `PathFinderThread.GetPath` + nav + move + look after the gate (§3 fully correct).
- `DumpMethod World EntityActivityUpdate` — 64 / 225 / 0.3 / 0.1 / 36 / 625 / 3025 / ints 20, 60, 4 all present (§4, D3.1).
- `DumpMethod EntityAlive OnUpdateLive` — gate chain AttachedToEntity, IsRemote, IsDead, IsClientControlled, hasAI → `updateTasks` (§2).
- `DumpMethod EAIManager Update` — IL=16; `FastMoveTowards(interestDistance, 10, 0.008333334)`; targetTasks + tasks (§5.1).
- `DumpMethod EAITaskList OnUpdateTasks` — IL=137; 0.05 step ×2 (§5.2, D3.3).
- `DumpMethod EntityAlive FindPath` — IL=49; 1225; ±45 (D3.2).
- `DumpMethod ASPPathFinderThread FindPaths` + `DumpMethod '<FindPaths>d__8' MoveNext` — coroutine state machine `d__8`, `entityWaitQueue`/`finishedPaths`, `GetPathTo`, `ldc.i4.8` drain cap (§6, D3.7 "≤8 per slice").
- `DumpMethod AstarManager Init` — `AddComponent<AstarManager>` + `newobj ASPPathFinderThread` + `StartWorkerThreads` (→ `StartCoroutine`, IL=7): production path is ASP (§6.1, D5).
- `DumpType ASPPathFinderThread / AStarPathFinderThread` — fields exactly as D5 (coroutine vs threadInfo + writerThreadWaitHandle; shared HashSetList + Dictionary).
- IL sizes: OnUpdateEntity 417, OnUpdateLive 363, OnUpdatePosition 107, EntityMoveHelper.UpdateMoveHelper 1236, EntityVulture.updateTasks 1344, EntityFallingBlock 344, EntityFallingBlocks 302, EntityTrader.OnUpdateLive 315, EntityTurret.OnUpdateEntity 414, EntityDrone.updateTasks 139, EntityEnemyAnimal 26, EntityBandit 12, EntityVehicle.updateTasks 1 (`ret`), EntityZombieDog.OnUpdateLive 16, EAIApproachAndAttackTarget.Update 846 (with exactly 3 `FindPath` call sites: `grep -c FindPath` = 3), EAIDestroyArea.Continue 317, EAISetNearestEntityAsTarget.FindTarget 281 / FindTargetPlayer 184, EAIRunAway.Update 105, EAIBreakBlock.AttackBlock 118, LetBlocksFall 220, GroupFallingBlocks 292, NetEntityDistribution.OnUpdateEntities 322, WorldBlockTicker.Tick 20, TickSleeperVolumes 34, DecoManager.UpdateTick 330, PowerManager.Update 106, VehicleManager.Update 297, DroneManager.Update 305, TurretTracker.Update 45, QuestEventManager 127, FactionManager 43, GameEventManager 25, DynamicMeshServer.Update 452, ChunkManager.DetermineChunksToLoad 448, ASPPathNavigate.pathFollow 160, GameTimer.updateTimer(Boolean) exists.
- D3.5/D3.6 constants: `DumpMethod NetEntityDistributionEntry updatePlayerList` contains 0.04, 2, 16, 128, 192, 256; `SpawnManagerBiomes SpawnUpdate` contains 1, 2.5, 4, 40, 80.

uai.md (all quirks reproduced from IL):
- `DumpMethod UAIBase .cctor` — `MaxEntitiesToConsider=5`, `MaxWaypointsToConsider=5`, `ActionChoiceDelay=0.2` (§8).
- `DumpMethod UAIBase Update` — IL=18, two-rate driver, `updateTimer -= Time.deltaTime` (§2).
- `DumpMethod UAIBase chooseAction` — IL=97: best-score local set to 0 at IL_0000 and **never re-stored in the loop** (`ble.un` against it each iteration) → "last positive package wins" quirk verified; same-instance `beq` skip; `Stop`(Started)+`Reset`(Initialized) then Action/Target/TaskIndex=0 (§3.3).
- `DumpMethod UAIAction GetScore` — IL=72(+): empty considerations → weight; empty tasks → 0; `ldc.i4.1 / ldc.i4.1 <n> div sub conv.r4` = **integer-division compensation** quirk verified; early-out uses `score<0 || score<min` (§3.2).
- `DumpMethod UAIPackage DecideAction` — both loops guarded by `ble` against Max*ToConsider (doc's "up to 6 scored" reading consistent); `min` argument is literally `ldc.r4 0` at both `GetScore` call sites ("dead pruning branch" verified).
- `DumpMethod UAIConsiderationBase ComputeResponseCurve` — IL=231, 10-way switch (10 CurveTypes), constants 1000 (logistic), 0.05/0.5 (logit), 0.01 (normal), 6.28 (bounce) present (§4).
- `DumpMethod UAIConsiderationTargetDistance .ctor` — `ldc.r4 9126` (§8).
- `DumpMethod UAITaskWander Start` — hardcodes 10 (`CalcAround(10,10)`), ignoring `max_distance` (§5.2).
- DumpAll UAI → "23 types / 95 method bodies" — matches the doc's evidence line verbatim; `stfld ActionData::Failed` only in `ActionData` (ClearData) and `UAITaskFleeFromTarget`, and **no** `ldfld ...Failed` anywhere (dormant-field claim, §5.1).
- `DumpMethod EntityAlive InitPostCommon` — UseAIPackages → `hasAI=true`, copies `EntityClass.AIPackages`, `newobj UAI.Context` (§1); `EntityClass.Init` parses `PropAIPackages` → `AIPackages[]`.
- Shipped XML: `Data/Config/utilityai.xml` has exactly the four packages named; `entityclasses.xml` `AIPackages` properties (lines 6472/6526) sit inside a `<!-- ... -->` block (verified by reading lines 6455-6480) — stock-dormant claim confirmed (§9).

spawning.md:
- `DumpMethod SpawnManagerBiomes SpawnUpdate` (IL=441): CanSpawn(1.0)-fail or BloodMoonActive demotes enemy→animals (IL_001D-004B); animal gate `GameStats(13) < GamePrefs(129)`; per-player Rect(pos-40, pos-40, 80, 80).Overlaps(area); enemy 28/54 vs animal 48/70 band select on `_isSpawnEnemy` (IL_00E9-00FD); `FastMin(5, count)` group scan from random start; `groupsEnabledFlags` bitmask from POI `poiTags`/`noPOITags` on first pass (`checkedPOITags`); `EDaytime` match; respawn delay → `ResetRespawn` (with `ModifySpawnCountByGameDifficulty` for enemies); `ChunkAreaBiomeSpawnData.CanSpawn`; anti-stack `GetEntitiesInBounds(Entity, Bounds(pos, size 4×2.5×4))` → ret if non-empty; `GetRandomFromGroup` fail → `DecMaxCount`+ret; `IncCount` → `SetupEntityCreationData` → `Chunk.SpawnEntityAsync` with callback (§2 every box checked).
- `DumpMethod SpawnManagerBiomes OnEntitySpawned` — `SetSpawnerSource(Biome=1, masterChunkKey, biomeIdHash)`.
- `DumpMethod SpawnManagerBiomes OnEntityUnloaded` (IL=63): Undef/Unloaded → ret (slot kept); Biome-source only; Despawned → DecCount(killed=false); Killed + EntityHuman past `timeToDie` → DecCount(false), else DecCount(true); other reasons → DecCount(true) — §3 state machine exact.
- `DumpMethod ChunkAreaBiomeSpawnData write` — version byte 2, count byte (FastMin 255), per entry `idHash:i32`, `(maxCount<<8)|count` as u16, `delayWorldTime:u64` — persisted wire form exact. `DecCount` — count-- floored 0; killed also maxCount-- floored 0. `ResetRespawn` — `respawnDelayInWorldTime * RandomRange(0.9, 1.1)`.
- `DumpMethod World OnUpdateTick` — per-area `GetChunkBiomeSpawnData`/`IsSpawnNeeded` → `biomeSpawnManager.Update`; `dynamicSpawnManager.Update`; `SpawnManagerBiomes.Update` forwards to SpawnUpdate unless `GameUtils.IsPlaytesting`.
- `DumpMethod EntitySpawner SpawnManually` (IL=499): 24000 ×2 (day math), 0.2 wave-restart factor, `totalAlive`, difficulty scaling, `GetRandomFromGroup`, source-tag select `2`/`3` before `SetSpawnerSource` (§4). `DumpType EntitySpawnerClass` — all §4 tuning fields present verbatim.
- `DumpMethod SpawnManagerDynamic Update` — `IsDaytime` early-out, `lastDaySpawned`, position callback `<Update>b__8_1` with 64/96 (§4).
- `DumpMethod AIDirectorChunkEventComponent Tick` — `spawnDelay` re-armed to 5 (5 s cadence); `CheckToSpawn(AIDirectorChunkData)` — GameStats 32 (`ZombieHordeMeter`) & 24 (`IsSpawnEnemies`), activity threshold `ldc.r4 25`, 20% roll `ldc.r4 0.2` (§5).
- `DumpMethod AIDirectorChunkEventComponent SpawnScouts` — 120 m, `Scouts1` <45, `Scouts2` <85, `ScoutsFeral` <125, else `ScoutsRadiated` (§5).
- `DumpMethod AIHordeSpawner Tick` — "Screamer spawned {0} from {1}", `SetSpawnerSource(3)`, `SpawnEntityInWorld`, `IsHordeZombie=1`, `bIsChunkObserver=1`, `SetInvestigatePosition(pos, 2400, true)`, `IncSpawnCount` (§5). `Cleanup` clears IsHordeZombie + bIsChunkObserver.
- `DumpMethod SpawnPointList GetRandomSpawnPosition` — signature `(World, Nullable<...>, Int32, Int32)`, `ldc.i4.s 100` tries, `SpawnPosition.Undef` fallback (§6).
- `DumpMethod World SpawnEntityInWorld` — `AddEntityToMap`, `NetEntityDistribution.Add`, `AIDirector.AddEntity`, and **no** send/broadcast call in body (§7 "does not broadcast" confirmed).

combat-damage.md:
- MethodList: `EntityAlive::DamageEntity(DamageSource,Int32,Boolean,Single)` (matches doc's 4-arg description), `ProcessDamageResponse`, `ProcessDamageResponseLocal`, `OnEntityDeath`, `SetDead`; `DamageSource::AffectedByArmor`, `GetEntityDamageBodyPart`, `GetEntityDamageBodyPartAndEquipmentSlot(Entity,EnumBodyPartHit&,EquipmentSlots&)`.
- `DumpMethod EntityAlive DamageEntity` — IsDead early-out; `damageEntityLocal` (IL=484) resolves body part, `AffectedByArmor`, `DamageResponse.ArmorDamage` (§2 flow supported).
- `DumpMethod NetPackageDamageEntity ProcessPackage` — reads entityId/damageSrc/damageTyp/attackerEntityId, resolves entity (§3 funnel claim supported).

entity-stats.md:
- MethodList: `EntityStats` Tick(UInt64)/TickWait(UInt64)/Read/Write/UpdateSandboxOptions/UpdateNPCStatsOverTime; `PlayerEntityStats` TickWait + UpdatePlayerFoodOT/WaterOT/StaminaOT/HealthOT(Single) + UpdateWeatherStats — every named method exists with the described split.

buffs.md (non-§3 parts):
- `DumpMethod EntityStats EntityBuffRemoved` — IL=1 `ret` (base no-op) and `PlayerEntityStats::EntityBuffRemoved` IL=63 loops `buffChangedDelegates` → `IEntityBuffsChanged.EntityBuffRemoved` (+ notification cleanup) — the §2 base-vs-override claim is exactly right.
- `DumpMethod EntityBuffs Tick` — IL=179: `BuffValue.Tick`, `set_Remove`/`get_Remove`, `RemoveAt`, `EntityStats::EntityBuffRemoved` on drop (§2 lifecycle).
- MethodList: AddBuff ×2 / RemoveBuff / RemoveBuffsByTag / RemoveDeathBuffs(FastTags) / HasBuffByTag / AddCustomVar / GetCustomVar; `BuffClass.DurationMax`, `GetModifiedValueData(..., ValueSourceType, ..., PassiveEffects, ..., FastTags)`; `BuffValue.DurationInTicks` property + `DurationTick()` + Update/Remove flags — §1 model confirmed.

stealth-smell.md:
- `DumpMethod PlayerStealth TickServer` — IL=430 and `SmellTickServer` — IL=257, both exactly as the doc's evidence line states.
- MethodList: Init(EntityPlayer), CalcVolume, NotifyNoise(Single,Single), AddNoise, NoiseCleanup, CanSleeperAttackDetect(EntityAlive), SetClientLevels(Single,Single,Boolean), ValuePercentUI/ValueColorUI/SetBarColor, Read/Write, SmellTickServer/SmellTickEat/SmellTickWet/SmellCountItems/SmellUpdateItemsAndBlood/SetSmellEat/SetSmellRadiusTarget(Int32,Boolean,Boolean)/SmellCountToRadius/SmellApplyMode/SmellClear, AttractTickServer — every method named in the doc exists with matching arity.

vehicles-drones-turrets.md:
- `DumpMethod VehicleManager write` — chars 'v'(118) 'd'(100) 'a'(97) + byte 0, version byte 1, i32 count, ECD records (§1 signature claim exact); Save/SaveThread → `vehicleDataSave` thread, `vehicles.dat` + `.bak`; DroneManager/TurretTracker → `droneDataSave`/`turretDataSave`.
- `CanAddMoreVehicles` / `CanAddMoreDrones` / `CanAddMoreTurrets` — all IL=9: DeviceFlag 56 → count < 500, else always true (§2 cap claim exact).
- `VehicleManager Update` — `IsChunkAreaCollidersLoaded`, `ldc.r4 0.002` Y nudge, `SpawnEntityInWorld`, `ldc.r4 120` save re-arm; `TriggerSave` — `Min(saveTime, 10)`; ctor `ldc.r4 120` (§1/§2).
- `PhysicsWakeNear` — `ldc.r4 400` (20 m sq) + `EntityVehicle.AddForce(..., ForceMode)` (§2).
- `DroneManager Update` — `sqrMagnitude > 1024` AND `GetState() != 5` (Shutdown) AND `OrderState != 1` (Sentry) → `TeleportOutOfRange` (§2 bullet exact, and confirms State.Shutdown=5 / Orders.Sentry=1).
- `DumpMethod EntityDrone updateState` — IL=27: 0.05 step; switch mapping 0→idle, 1→sentry, 2→follow, 3→heal, 4→attack, 5/6→no-op — §5 state-value table exact. `updateTransitionState` — sentinel `ldc.i4.8` (§5). FollowMode/SentryMode/ToggleOrderState/TeleportIfFollowing/healTargetServer/ClearAllDronesForPlayer all exist.
- `DumpMethod EntityVehicle PhysicsFixedUpdate` — IL=1509; `isEntityRemote` branch → `Rigidbody.isKinematic=true`, `Vector3.Lerp(..., 0.5)`, `Quaternion.Slerp(..., 0.3)` (§4.3 client-authoritative motion claim exact).
- `DumpMethod NetPackageVehicleSpawn write` — field order entityType:i32, pos:Vector3, rot:Vector3, ItemValue.Write, entityThatPlaced:i32 (§7 row exact); `ProcessPackage` — `ValidEntityIdForSender`, `CanAddMoreVehicles`, `CreateEntity`, owner from `ClientInfo.InternalId`, `SpawnEntityInWorld` (§4.1).
- `DumpMethod NetPackageTurretSync write` — entityId, targetEntityId, isOn, itemValue (§7 row exact).
- `DumpMethod EntityTurret OnUpdateEntity` — PassiveEffects 9, 74 (with `ldc.r4 10` base → `maxOwnerDistance`), 75; `NetPackageTurretSync.Setup` sent on `ldc.i4 192` (§6.1 exact).
- `DumpMethod MiniTurretFireController Fire` — IL=554, early-out unless `IsServer && entityTurret != null && IsOn` (§6.1 authority claim exact). `AutoTurretFireController Fire` — `IsLocked` + `IsServer` gates (§6.2). `JunkSledgeFireController` exists.
- Packages `NetPackageVehicleCount`, `NetPackageVehiclePositions`, `NetPackageVehicleDataSync`, `NetPackageEntityWaypointList(Setup(eWayPointListType, List))`, `NetPackageTurretSpawn`, `EntityDrone/NetPackageDroneDataSync` all exist (MethodList).
- Bases: `EntityTurret : EntityAlive`, `EntityDrone : EntityNPC : EntityAlive` (DumpType) — as documented (modulo F4).

Cross-doc consistency: spawning.md §1's `AIDirector.CanSpawn` formula, GamePref ids (99/129), and the aidirector.md component inventory agree with each other and the IL; entity-ai.md §D3.7's drain-8 agrees with uai.md §5.2's "shared 8-per-slice path drain"; no stale counts found between the nine docs.
