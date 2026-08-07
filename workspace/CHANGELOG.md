# Workspace changelog — lab notebook

Append-only research log. Not release notes. Each entry: date, active slug/objective,
what changed / what was tried, verification state (`verified` / `unverified` /
`blocked` / `inferred`), and the next recommended step. Read recent entries before
resuming substantial work. Do not log trivial one-shot tasks.

---
## 2026-08-07 — tier-C: CreateNewParty and RemovePlayer pool

Done (V3.1.0 b14 IL):
- CreateNewParty: BloodMoonParty(player, component, BloodMoonEnemyCount).
- RemovePlayer: management Reset+Free; BM players list + all parties PlayerLoggedOut.
- AddMember/RemoveMember: members list + optional memberIDs hash.
---
## 2026-08-07 — tier-C: AIDirector AddPlayer and BM party join

Done (V3.1.0 b14 IL):
- AIDirector.Add/RemoveEntity: players only.
- AddPlayer -> PlayerManagement tracked state + BloodMoonComponent players list.
- AddPlayerToParty / TryAddPlayer: join within sqr 6400 (80 m) or CreateNewParty.
---
## 2026-08-07 — tier-C: NetEntityDistribution SEnts and Remove

Done (V3.1.0 b14 IL):
- SEnts table: Player/Vehicle infinite; Enemy/NPC 80; Item 64; Falling 120; Supply 1200; Turret 60.
- Add: type match -> entry; player updates all entries.
- Remove: reason 1 unload vs destroy packages; AIDirector.AddEntity players only.
---
## 2026-08-07 — tier-C: SpawnEntityInWorld and BuffValue ticks

Done (V3.1.0 b14 IL):
- SpawnEntityInWorld: map/Entities/chunk; EntityAlives; vehicle/drone/turret track; audio/weather/light; net Add; player list; AIDirector.
- BuffValue.DurationTick: updateRate gate; Tick -> BuffClass.Tick or Remove.
---
## 2026-08-07 — tier-C: DamageEntity consecutive 30 and resist bank

Done (V3.1.0 b14 IL):
- DamageEntity: type 26 limb cleanup; consecutive ignore 30 ticks non-Internal; FF; entityFlags&2 block; god.
- Passive 161 attacking-item bonus mult; passive 40 resist fraction into accumulatedDamageResisted.
---
## 2026-08-07 — tier-C: pathFollow radii and ImprovePath

Done (V3.1.0 b14 IL):
- pathFollow: arrive max(0.15/0.33/0.49, radius*0.6); swim 0.9/0.7; elevator dy 0.2; advance sq 0.04.
- ImprovePath: ProjectToGround all; first-step snap if dy < 0.6.
- IsPathUsageBlocked default false; hasHome max>=0; detachHome -1.
---
## 2026-08-07 — tier-C: CheckPath and moveSpeed passives

Done (V3.1.0 b14 IL):
- EAIManager.CheckPath: reject if any executing task IsPathUsageBlocked.
- GetSeeDistance: distance - seeOffset.
- GetMoveSpeed: night/BM passive 133 moveSpeedNight else 135 moveSpeed.
- GetMoveSpeedAggro: night/BM 134 aggroMax else 133 aggro; Panic always 134.
- ASP SetPath ImprovePath; UpdateNavigation pathFollow + SetMoveTo path.
---
## 2026-08-07 — tier-C: EAILeap SetMoveTo and RandomPositionGenerator

Done (V3.1.0 b14 IL):
- EAILeap.CanExecute: limb/blocked/path; leapDist 2.8..jumpMax; y band; clear ray.
- SetMoveTo: aggro speed; expiry 10 (pos) / 40 (path); Stop clears path.
- CalcInDir/Around swim retry; CalcAway 80 deg; CalcAround 30 air/home tries.
---
## 2026-08-07 — tier-C: DestroyArea ApproachSpot and Dodge

Done (V3.1.0 b14 IL):
- DestroyArea.CanExecute: CanBreakBlocks; unreachable/pathCostScale long-path gates; sample focus.
- ApproachSpot: investigate + supporting block; path 40+R20; scout AddLocationLine 32.
- Dodge: tag bounds + IsAnimationToDodge; look head first half.
- isWithinHomeDistance: max<0 always; else home distSq.
---
## 2026-08-07 — tier-C: BreakBlock AttackBlock and FindEnemy

Done (V3.1.0 b14 IL):
- AttackBlock: zombie ally +0.2 in 1.7x1.5x1.7; delay (0.25+r*0.8[+0.5 unreachable]+0.75)*20; hitDelegate.
- FindEnemy: type bounds by see distance; CanSee/stealth nearest.
- RunAway.Update: path end 1.21; pathTicks 60 FindPath.
---
## 2026-08-07 — tier-C: EAITarget.check Wander and Ranged CanExecute

Done (V3.1.0 b14 IL):
- EAITarget.check: home distance; optional CanSee; player CanSeeStealth.
- EAIWander.CanExecute: lookTime/stun/fade+120 ticks; executePercent; CalcInDir 90.
- EAIRangedAttackTarget: cooldown; IsAttackValid; limbs; InRange+CanSee; Update anim states UseHoldingItem.
---
## 2026-08-07 — tier-C: EAISetAsTargetIfHurt and Approach CanExecute

Done (V3.1.0 b14 IL):
- EAIApproachAndAttackTarget.CanExecute: sleep/stun/jump; targetClasses assignable + chaseTimeMax.
- EAISetAsTargetIfHurt: revenge type filters; 66% keep attack; else SearchRadius*0.35 investigate + clear revenge.
- CalcInvestigateTicks: ticks / passive 183 (self Tags).
---
## 2026-08-07 — tier-C: EntityActivityUpdate top-N and cloth radii

Done (V3.1.0 b14 IL):
- EntityActivityUpdate: clear aiClosest; assign closest player; sort; N=FastClamp(60/P,4,20).
- Scale bands 1.0 / 0.3 / 0.1 at 64/225; jiggle under 36.
- Cloth: 625 (25 m) / 3025 (55 m) when AimingGun; skip attached others.
---
## 2026-08-07 — tier-C: EntityDied ClearedUpdate and AddScore weights

Done (V3.1.0 b14 IL):
- NotifySleeperVolumesEntityDied: lock + EntityDied all volumes.
- EntityDied: remove respawnMap/list; ClearedUpdate if not spawning.
- ClearedUpdate: pref 88 days * 24000 -> respawnTime; wasCleared.
- GetMaxAttackTime: 10 ticks.
- AddScore: GameStats 28/29/30 weights; achievements 6/7/10/14; HandleClientDeath nop.
---
## 2026-08-07 — tier-C: ClientKill OnDeathUpdate FireEvent

Done (V3.1.0 b14 IL):
- NotifySleeperDeath: server sleeper -> NotifySleeperVolumesEntityDied.
- ClientKill: SetDead; Buffs.OnDeath crushing default; Progression.OnDeath; OnEntityDeath; celebrate passive 181.
- OnDeathUpdate: deathUpdateTime++; DeadBodyHitPoints force stay; particleOnDestroy.
- FireEvent: class Effects, Progression, challenges, inv, equip, Buffs.
- SetCVar: Buffs.SetCustomVar netSync true.
---
## 2026-08-07 — tier-C: SetRevengeTarget and AwardKill magnum

Done (V3.1.0 b14 IL):
- SetRevengeTarget: revengeTimer 500 when non-null.
- DamagedByEntity: EAIDestroyArea.Stop.
- SetStun/ClearStun: CurrentStun + _stunned cvar.
- Kill: NotifySleeperDeath; death sound; ClientKill.
- AwardKill: type 1/2 counters; magnum44 score flag 2; AddScoreServer.
---
## 2026-08-07 — tier-C: UseHoldingItem and path FindPath enqueue

Done (V3.1.0 b14 IL):
- UseHoldingItem: attack-anim gate; IsAttackValid; attack sound on release; attackingTime=60; ExecuteAction.
- AStar FindPath: Monitor lock + wait handle pulse; ASP FindPath: no lock overwrite.
---
## 2026-08-07 — tier-C: CanSee ray and Attack target-now

Done (V3.1.0 b14 IL):
- CanSee(Vector3): view cone + 0.2 origin pull; Voxel.Raycast clear LOS.
- CanSeeStealth: light threshold FastLerp by dist/sightRange.
- Attack: UseHoldingItem(0); timeout day/night; GetTargetIfAttackedNow range+0.3 and E_BP_/E_Vehicle.
---
## 2026-08-07 — tier-C: CheckDespawn source bands and IsAttackValid

Done (V3.1.0 b14 IL):
- CheckDespawn: remote/chunk-observer unload; 20-tick cadence; source 1/2/3 early and switch bands (48/80/96/128 m; 60/80/100/1800 ticks).
- IsAttackValid: electrocute/stun 1-2; attack prevented; painResist>=1 free; hasBeenAttackedTime gate; hit anim.
- GetAttackTargetLocal remote uses attackTargetClient.
---
## 2026-08-07 — tier-C: isBestTask MutexBits and OnUpdateEntity path

Done (V3.1.0 b14 IL):
- areTasksCompatible: MutexBits AND == 0.
- isBestTask: higher priority non-continuous blocks; incompatible lower/equal blocks.
- OnUpdateEntity: Buffs.Tick then OnUpdateLive then inventory; radiation damage residual.
- get_maxAlive: spawnGroup.maxAlive.
---
## 2026-08-07 — tier-C: GetAliveCount and BloodMoonParty.Tick

Done (V3.1.0 b14 IL):
- GetAliveCount: sum(groupCounts)-numSpawned+respawnMap.Count.
- FindLabel: command==2 name match.
- SetScaling: FastLerp(1,2.5,(s-1)/3).
- BloodMoonParty.Tick: updateDelay 1.8 SeekTarget; CanSpawn 1.9; +120 baseDir; min(3,members) spawn tries.
---
## 2026-08-07 — tier-C: MinScript.Tick opcodes and CalcBestDir bins

Done (V3.1.0 b14 IL):
- MinScript.Tick: sleep 0.05 steps; cmds 1 log, 2 nop, 3 loop, 4 sleep, 40 sound, 50 AddSpawnCount, 51 wait alive, 52 trigger.
- CalcBestDir: 16x22.5 deg; 9 samples; score (s+2)/3; *3 if within 60 of spawnBaseDir; random among max.
- InitParty IL=49 confirmed scaling path.
---
## 2026-08-07 — tier-C: IsPlayerATarget and MinScript.Run

Done (V3.1.0 b14 IL):
- IsPlayerATarget: dead/spawned/id; IgnoreAI; Level<=1 or IsBloodMoonDead reject.
- FindPartyTarget: reverse partyMembers nearest sqr among targets.
- MinScript.Run: store player/countScale; curIndex=0 sleep=0; IsRunning curIndex>=0.
---
## 2026-08-07 — tier-C: SeekTarget 1200 and SleeperVolume.Reset

Done (V3.1.0 b14 IL):
- SeekTarget: 150 m teleport/kill branch; 100 m SetAttackTarget 1200; else investigate 1200; lootDropProb=0 on cull.
- SleeperVolume.Reset: full field clear table + CancelPendingSpawns + minScript.Reset.
- Census pin narrated 1480 / catalogued 829 / unaccounted 0.
---
## 2026-08-07 — tier-C: UpdatePlayerTouched mult and SpawnZombie vulture

Done (V3.1.0 b14 IL):
- UpdatePlayerTouched: early return gates; quest SpawnMultiplier * difficultyTierScale; banditTag 0.2; default counts 5..6; minScript.Run.
- TriggerSleeperPose: pose!=5 physicsHeight 0.85; look dir from spawn; ResumeSleeperPose.
- Static padding chunk/trigger/unpadding; difficultyTierScale len 7.
- SpawnZombie IL=181: mounted 50% animalZombieVultureRadiated skips bonus loot; Astar 40.
---
## 2026-08-07 — tier-C: SleeperVolume.Spawn async and SetSleeper helpers

Done (V3.1.0 b14 IL):
- Spawn: pos +0.502/0.501; zombieArlene fallback; ExcludesWalkType fail; async create + pending maps; TickSpawnCount++.
- CompletePendingSpawns WaitForComplete; CancelPendingSpawns Destroy RootTransform.
- Despawn only sleeping respawnMap entities; DespawnAndReset = Despawn+Reset.
- SetSleeper pathCostScale+0.2; SetSleeperSight defaults; SetSleeperHearing 1/percent scale.
---
## 2026-08-07 — tier-C: CanSleeperSpawn floor/solid and CalcGameStageAround

Done (V3.1.0 b14 IL):
- Chunk.CanSleeperSpawnAtPos: below must collide; cell not collide/solid.
- CalcGameStageAround: players within 100 m same prefab; CalcPartyLevel.
- AddSpawnCount: RandomRange min..max fractional ceil; min>0 forces at least 1.
- RemoveSpawnAvailable: linear remove by index value.
---
## 2026-08-07 — tier-C: FindFathestSpawn and ResetSpawnsAvailable

Done (V3.1.0 b14 IL):
- FindFathestSpawnFromPlayers: max of min-player-dist among CanSleeperSpawnAtPos points.
- ResetSpawnsAvailable: skip spawnMode 2 unless infestedTag refresh.
- CanSleeperSpawnAtPos: chunk local CanSleeperSpawnAtPos.
- GetGameStageAround: CalcGameStageAround.
---
## 2026-08-07 — tier-C: SpawnPointIsHidden rays and stealth setters

Done (V3.1.0 b14 IL):
- SpawnPointIsHidden: center+0.5; pose5 offsets; per-player head rays layer 71; any clear LOS fails hidden.
- SetSmellRadiusTarget: radius/eating/sheltered; radius<0 clears.
- SetClientLevels + SetBarColor green/alert UI.
---
## 2026-08-07 — tier-C: SmellCountItems radius and EntityStealth bits

Done (V3.1.0 b14 IL):
- SmellCountItems: drag+inventory+bag ItemClass.Smell*count, min 50.
- SmellCountToRadius: (count-5)/45 Lerp 10..100.
- SetSmellEat: eatRadius+dist cap 100, ticks 1800.
- NetPackageEntityStealth: server smell-target vs crouch; client SetClientLevels.
---
## 2026-08-07 — tier-C: SmellUpdateItemsAndBlood wet and shelter

Done (V3.1.0 b14 IL):
- SmellTickWet: _wetnessrate cvar accumulates smellWet when >= 0.01.
- SmellClear: zero radius/eat/wet/sheltered fields.
- SmellUpdateItemsAndBlood: wet>=3 or dead clears; dysenterySmell -> SetSmellEat(35); items radius; shelter *0.2.
---
## 2026-08-07 — tier-C: CheckSleeperVolumeNoise and Attract/Smell ticks

Done (V3.1.0 b14 IL):
- CheckSleeperVolumeNoise: GameStats 24; y+0.1; per-volume CheckNoise.
- CheckNoise: hasPassives AABB pad 0.9; TouchGroup(null, true) unless mode 1.
- AttractTickServer: every 40 ticks stress cvar radius; 20% roll; attract timeout 80.
- SmellTickServer outline: radius ease, cvar smell, emit flags 6 every 40 ticks.
- FindNoise: noisySounds TryGetValue.
---
## 2026-08-07 — tier-C: NotifyNoise heat map and AddNoise sort

Done (V3.1.0 b14 IL):
- AddNoise: insert sorted descending by volume.
- NotifyNoise (PlayerStealth): duration*20 ticks; vol>=11 sleeper wait 20; soft cap 60+(v-60)^1.4; passive 88; sleeperNoiseVolume max 360.
- AIDirector.NotifyNoise: ignore enemies/decoys; crouch muffling; CheckSleeperVolumeNoise; heat NotifyActivity type 3 duration 240.
- OnSoundPlayedAtPosition -> NotifyNoise.
---
## 2026-08-07 — tier-C: CalcVolume noise formula and stealth light

Done (V3.1.0 b14 IL):
- CalcVolume: 0.6 successive decay, (sum*2.35)^0.86 * 1.5 * passive 88.
- NoiseCleanup: decrement ticks or RemoveAt.
- GetStealthLightLevel: y+1.68 sample + moving lights; selfLight out.
- BlockTrigger.OnTriggered: flag + Block.OnTriggered + clear values.
- SleeperVolume.OnTriggered: already D8.2b (triggerState + UpdatePlayerTouched).
---
## 2026-08-07 — tier-C: PlayerStealth.TickServer and PrefabTriggerData

Done (V3.1.0 b14 IL):
- SleeperWokeUp: zero all targetTasks executeTime.
- SleeperWakeup/PassiveChange Process: remote-only apply.
- TickServer: speedAverage, light crouch 0.6, cvars _lightlevel/_noiselevel, passive 89, lightLevel 0..200.
- PrefabTriggerData.Trigger: BlockTrigger.OnTriggered + SleeperVolume.OnTriggered by index.
---
## 2026-08-07 — tier-C: sleeper wake net and crouch detect

Done (V3.1.0 b14 IL):
- ConditionalTriggerSleeperWakeUp: clear sleep/passive; pose -1/-2; SleeperWokeUp; NetPackageSleeperWakeup 192.
- SetSleeperActive: clear passive only; NetPackageSleeperPassiveChange 192.
- CanSleeperAttackDetect: crouch Lerp(3,15,lightAttackPercent) distance gate.
- TriggerManager.TriggerBlocks: PrefabTriggerData for BlockTrigger/TriggerVolume.
---
## 2026-08-07 — tier-C: TouchGroup/Touch wake and GetClosestPlayerSeen

Done (V3.1.0 b14 IL):
- TouchGroup: same groupId fan-out Touch; solo Touch.
- Touch setActive: stealth detect wake+SetAttackTarget 400; trigger4 wake; wandering countdown 10.
- Touch !setActive: playerTouchedToUpdate, ticksUntilDespawn 900/200, respawnTime bump.
- CheckTrigger: unpadding vs triggerPadding; home delay +24000; UncullPOI.
- TriggerVolume.Touch: isTriggered + TriggerBlocks.
- GetClosestPlayerSeen: lightLevel >= lightMin and CanSee.
---
## 2026-08-07 — tier-C: CalcSenseScale FeralSense and volume CheckTouching

Done (V3.1.0 b14 IL):
- CalcSenseScale: FeralSense 1=day, 2=dark, 3=always -> 1 else 0.
- SleeperVolume.CheckTouching: y+0.8; hasPassives pad 0.3; trigger pad 0.1; TouchGroup.
- TriggerVolume.CheckTouching: y+0.8 strict AABB then Touch.
- GetClosestPlayer: distMax<0 => inf; dead match + Spawned; min distSq.
---
## 2026-08-07 — tier-C: GetSeeDistance senseScale and DetectUsScale

Done (V3.1.0 b14 IL):
- GetSeeDistance: sleeperSightRange vs sightRangeBase * (1 + CalcSenseScale*feralSense).
- DetectUsScale: 0.3 after 60s in DifficultyTier>=1 prefab vs Dynamic EntityEnemy.
- IsInViewCone: sleeperLookDir/sleeperViewAngle vs look vector.
- CheckSleeperVolumeTouching: GameStats 24 gate; chunk sleeper list + lock.
- CheckTriggerVolumeTrigger: chunk trigger list + lock (no EnemySpawnMode gate).
---
## 2026-08-07 — tier-C: FriendlyFireCheck PvP modes and CanEntityBeSeen

Done (V3.1.0 b14 IL):
- EntityPlayer.FriendlyFireCheck: GameStats 23 modes 0/1/2 ally/stranger gates.
- CanEntityBeSeen: see distance * DetectUsScale, view cone, ray mask -1612492829.
- CheckSleeperTriggers: sleeper + trigger volumes on server alive players.
- EntityAlive.HasImmunity always false.
---
## 2026-08-07 — tier-C: HasImmunity passive 197 and CanSee caches

Done (V3.1.0 b14 IL):
- HasImmunity: dead+RemoveOnDeath; parent HasImmunity; passive 197 roll; infection InfectionChance.
- CanSee: positive/negative HashSet caches; CanEntityBeSeen; client-controlled updates lastTimeSeenAPlayer.
- Base FriendlyFireCheck always true (IL=2).
---
## 2026-08-07 — tier-C: AddBuff BuffStatus gates and ResetDespawnTime

Done (V3.1.0 b14 IL):
- AddBuff IL=238: status 0 success, 1 unknown, 2 immune, 3 FF, 4 editor, 5 gamestat; stack event 4.
- Despawn/ForceDespawn; ResetDespawnTime clears ticksNoPlayerAdjacent + seeCache seen time.
---
## 2026-08-07 — tier-C: CheckDespawn distance/timer bands

Done (V3.1.0 b14 IL):
- CheckDespawn every 20 ticks: 130/20 m far-flag; bands 48/80/96/128 m with 60/80/100/1800 tick timers.
- EntityEnemy.canDespawn: horde zombies stay while players online.
---
## 2026-08-07 — tier-C: CalcSpawnPos and unloadEntity pipeline

Done (V3.1.0 b14 IL):
- CalcSpawnPos: radius yaw ±45°; GetMobRandomSpawnPosWithWater 0/10/30.
- MarkToUnload: EntityAlive copies timeStayAfterDeath -> deathUpdateTime.
- unloadEntity: delegates, OnEntityUnload, dict/map/chunk, vehicle/drone/turret, NED/path/AIDirector.
- RemoveBuff: mark Remove + optional RemoveBuffNetwork.
---
## 2026-08-07 — tier-C: SeekTarget kill gates and OnEntityUnload

Done (V3.1.0 b14 IL):
- SeekTarget: 60 m no-player kill; 150 m / 70 m repath; 50% DecSpawnCount kill.
- OnEntityUnload: OcclusionManager + clear navigator/look/move/see.
- RemoveEntity MarkToUnload+unloadEntity; EntityRemove Process always RemoveEntity.
- BuffClass.canRun Requirements.IsValid.
---
## 2026-08-07 — tier-C: BuffClass.FireEvent canRun and StartSequence

Done (V3.1.0 b14 IL):
- BuffClass.FireEvent: Effects null / canRun gate then MinEffectController.FireEvent.
- StartSequence: StartTime = Time.time only.
---
## 2026-08-07 — tier-C: EntityBuffs.Tick MinEvent order

Done (V3.1.0 b14 IL):
- Tick: Invalid drop; Finished->event 2; Remove->event 3; Start event 0; Tick; Update event 1.
- FireEvent skips paused; CanExecute Requirements.IsValid or true.
---
## 2026-08-07 — tier-C: interest enter package order

Done (V3.1.0 b14 IL):
- updatePlayerEntity enter: Spawn, AliveFlags, PlayerStats/Twitch/Equipment, Speeds, optional Velocity.
- Census pins: narrated 1479 / catalogued 830 / unaccounted 0.
---
## 2026-08-07 — tier-C: explode ExplodeGroup delay and FrameUpdate

Done (V3.1.0 b14 IL):
- explode: ExplodeGroup delay=3; IsExplosionAffected fallings; heat map OnSoundPlayedAtPosition.
- ExplodeGroupFrameUpdate: budget max(1,min(n,20*0.73^n)); DropItems 0.5; fallingBlock velocity.
---
## 2026-08-07 — tier-C: AttackEntites body mult and DamageRecord

Done (V3.1.0 b14 IL):
- AttackEntites: passives 20/21/22; Legs/Head/ChestExplosionDamageMultiplier; DamageRecord sum.
- Apply: DismemberChance 0.5; damage vs 0.1 maxHealth; center sqr 0.67; stun bands 0.6/0.85.
---
## 2026-08-07 — tier-C: LootDropPick weighted and OnBlockStartsToFall

Done (V3.1.0 b14 IL):
- LootDropPick: <2 entries -> [0]; else cumulative weight RandomFloat pick entityClass.
- OnBlockStartsToFall base: SetBlockRPC Air; tree/composite overrides.
---
## 2026-08-07 — tier-C: DropBagServer lootDrops vs bag

Done (V3.1.0 b14 IL):
- DropBagServer: server-only; y+0.9; class lootDrops pick OR DroppedLootContainer from bag.
- quests BlockDestroyed changelog pin; dropItemOnDeath passive 80 already committed.
---
## 2026-08-07 — tier-C: dropItemOnDeath passive 80 and BlockDestroyed

Done (V3.1.0 b14 IL):
- dropItemOnDeath: passive 80 scales lootDropProb from killer hold; * LootBagChance; DropBagServer roll.
- BlockDestroyed: BlockDestroy event; HandleTrigger via closest player within 500 m.
---
## 2026-08-07 — tier-C: GetCountMultiplier enum and BM weather defer

Done (V3.1.0 b14 IL):
- GetCountMultiplierFromSandbox: types 1..11 map to count modifiers; else -1.
- CalcGlobalWeatherType: bloodMoon + push stormWorldTime by 5000 when near.
---
## 2026-08-07 — tier-C: RandomCountFromSandboxTags category table

Done (V3.1.0 b14 IL):
- RandomCountFromSandboxTags: food/drink/ammo/medical/junk/armor/melee/ranged/dukes/mag/books modifiers.
- RandomCountFromSandbox: abundanceType mult then RandomSpawnCount.
---
## 2026-08-07 — tier-C: GetSandboxProb and RandomSpawnCount

Done (V3.1.0 b14 IL):
- GetSandboxProb: treasureTags -> TreasureMapChance else 1.
- RandomSpawnCount: RandomRange(min-0.49,max+0.49)*abundance with frac ceil.
---
## 2026-08-07 — tier-C: getProbability and SpawnLootItemsFromList

Done (V3.1.0 b14 IL):
- getProbability: requirements, lootProbTemplate stage bands, passive 79, GetSandboxProb.
- SpawnLootItemsFromList: numToSpawn -1 all, weighted unique pick, sandbox counts.
- MemberCountInRange: other members Distance < GameStats 54.
---
## 2026-08-07 — tier-C: party highest loot stage wrappers

Done (V3.1.0 b14 IL):
- GetHighestPartyLootStage -> Party.GetHighestLootStage max over members.
- GetHighestLootStage: max GetLootStage(containerMod, containerBonus).
---
## 2026-08-07 — tier-C: GetLootStage POI/biome formula

Done (V3.1.0 b14 IL):
- GetLootStage: POITierMod/Bonus, biome LootStageMod/Bonus/Min/Max, passives 159/160, GameStats 66 clamp, GlobalLootStageModifier.
- SharedPartyKill: server SharedKillServer scale 1; client SharedKillClient.
- EntityAddExpServer: AddLevelExp only when isEntityRemote with _xpOther type 8.
---
## 2026-08-07 — tier-C: get_gameStage formula and GameStage statics

Done (V3.1.0 b14 IL):
- EntityPlayer.get_gameStage: daysLived clamp to Level, biome/quest mods, passive 157, GlobalGameStageModifier.
- GameStageDefinition.cctor: DifficultyBonus=1, StartingWeight=1, DiminishingReturns=0.5, DaysAliveChangeWhenKilled=2.
---
## 2026-08-07 — tier-C: CalcPartyLevel diminishing returns and setState

Done (V3.1.0 b14 IL):
- CalcPartyLevel: sort, weighted sum high-to-low with StartingWeight/DiminishingReturns.
- CalcStageSpawnMax: sum group spawnCounts.
- checkTeleportPos 32 m success log; setState lastState + owned clear + heal clear.
- CanSpawn named EnemyCount / MaxSpawnedZombies.
---
## 2026-08-07 — tier-C: CanSpawn cap, SetPartyLevel scaling, teleportState

Done (V3.1.0 b14 IL):
- CanSpawn: GameStats 12 < GamePrefs 99 * priority.
- SetPartyLevel: gsScaling; GetStage uses unscaled arg; bonusLootEvery.
- ModifySpawnCountByGameDifficulty: EnemySpawnMode off -> 0 only.
- teleportState: Teleport state, closest free group slot, Idle.
- targetCanBeHealed / isTargetBleeding; empty exitAttack/onHealDone.
---
## 2026-08-07 — tier-C: SetupGroup and heal type priority

Done (V3.1.0 b14 IL):
- SetupGroup: interval, nextStageTime=worldTime+duration*1000, difficulty-scaled numToSpawn.
- ResetPartyLevel: CalcPartyLevel then optional mod remainder.
- findNeededHealType: types 2/3/4 priority for medical vs bleeding.
- TeleportOutOfRange: exit attack/heal then teleportState.
---
## 2026-08-07 — tier-C: drone weapon Fire paths and PartySpawner Tick

Done (V3.1.0 b14 IL):
- MachineGunWeapon: passives 16/11/199/200/9/7, raycast Hit, ammo, UseTimes.
- StunBeam: _droneStunDamage quality cvar + buffShocked.
- HealBeam: inventory UseOther action1 + buffJunkDroneHealCooldownEffect.
- AIDirectorGameStagePartySpawner Tick/canSpawn/IncSpawnCount; isValidDronePos NaN.
---
## 2026-08-07 — tier-C: AIHordeSpawner.Tick and Weapon cooldown

Done (V3.1.0 b14 IL):
- AIHordeSpawner.Tick IL=228: party init, day 45/55/45 night 55/70/55, one spawn/tick, investigate 2400.
- Weapon.Fire stores target + RefreshCooldown (actionTime+cooldown).
- VehicleDataSync Process: ReadSyncData; server GetSyncFlagsReplicated + SendPackage 192.
---
## 2026-08-07 — tier-C: scout Update finish, Horde.Tick, drone CanAttack

Done (V3.1.0 b14 IL):
- AIScoutHordeSpawner.Update finish: no players or SpawnUpdate done + empty horde.
- SpawnUpdate: AttackDelay=2, IsHorde/Scout/chunkObserver flags, 6000 investigate.
- Horde.Tick: _destroy or nested AIHordeSpawner finish/Cleanup.
- CanAttack bans Heal/Attack/Shutdown; Weapon.canFire = cooldown<=0.
- updateTransitionState heal server path and cooldown refresh.
---
## 2026-08-07 — tier-C: TickActiveSpawns drain and heal medical gate

Done (V3.1.0 b14 IL):
- TickActiveSpawns reverse scout/horde lists; HasAnySpawns = horde only.
- CheckToSpawn FIFO one chunk per 5 s pulse.
- HealBeamWeapon need: max-HealDamageThreshold or <0.67 ModifiedMax; medicalRegHealthAmount==0.
- IsAttackValid: activeWeapon.canFire.
---
## 2026-08-07 — tier-C: drone group slots and follow repath

Done (V3.1.0 b14 IL):
- GetGroupPositions: 5 horizontal slots from chest/look; ScanVolume fallback.
- DoMoveIntoFollowPos: GetPath when empty; repath seekDist+1 / +1.414; success dist.
- TickPlayerState: Dead mirror only from Player.IsDead.
---
## 2026-08-07 — tier-C: investigate pos and neighbor cooldown delays

Done (V3.1.0 b14 IL):
- Set/ClearInvestigatePosition; alert ticks (20-35)*20, zombie half.
- StartNeighborCooldown 180/720 s; SetLongDelay 1320 s; drone underwater surface seek.
---
## 2026-08-07 — tier-C: trackTarget ranges, canHitEntity, FindScoutStartPos

Done (V3.1.0 b14 IL):
- trackTarget chest/head lerp + yaw/pitch range gates.
- canHitEntity raycast E_ tag must match target.
- FindScoutStartPos 80 m ring, 15 tries, 30 m player avoid; neighbor cooldown grid.
---
## 2026-08-07 — tier-C: turret ignore flags, Fire ammo, spawnHordeNear

Done (V3.1.0 b14 IL):
- shouldIgnoreTarget: ally/party/owner/stranger/enemy flags; always skip traders/turrets/drones.
- Fire: passives 16/11, rayCount Hit path, AmmoCount--, UseTimes.
- spawnHordeNear: CreateHorde, base 5, 12% reduce, SpawnMore; healTargetServer.
---
## 2026-08-07 — tier-C: scout horde update and drone state IL

Done (V3.1.0 b14 IL):
- Scout SpawnUpdate: CanSpawn, investigate 6000 ticks, random pos radius 6.
- UpdateHorde: AttackDelay 18s, investigate 2000/6000, spawnHordeNear.
- Drone idle/follow/sentry distance gates; MiniTurret findTarget raycast.
---
## 2026-08-07 — tier-C: chunk activity decay and liquid Flow/Evap packing

Done (V3.1.0 b14 IL):
- AddEvent merges same-type Value; DecayEvents proportional; best event cooldown 240s.
- Evap damage 0..45; Flow = damage-50; PhysicsWakeNear 20 m wake.
---
## 2026-08-07 — tier-C: liquid ChangeThis pack and SpawnScouts bands

Done (V3.1.0 b14 IL):
- ChangeThis: rotation 8, meta2 emissions, damage=evap+flow, WBT 60/1/1000.
- CheckUpdate rate limit; CheckDeepWater 6-stack; NotifyEvent checkChunks.
- SpawnScouts 120 m player, Scouts1/2/Feral/Radiated by gamestage.
---
## 2026-08-07 — tier-C: NotifyActivity gates and liquid Emissions/ChangeToAir

Done (V3.1.0 b14 IL):
- NotifyActivity: GameStats 32/24, heat mod, skip BM/Twitch; chunk NotifyEvent.
- CheckToSpawn: ActivityLevel 25, 20% SpawnScouts + neighbor cooldown.
- BlockLiquidv2 Emissions rotation/meta2; ChangeToAir splash+WBT; HasHoles.
---
## 2026-08-07 — tier-C: PlantGrowing, TorchHeatMap, WorldBlockTicker execute

Done (V3.1.0 b14 IL):
- PlantGrowing lightLevelGrow, CanGrowOn, biome type remap, meta grow-on-top.
- TorchHeatMap AIDirector.NotifyActivity enum 6 strength*0.4 duration 720.
- WBT execute type-match; AddScheduled replace; Chunk.UpdateTick TE-only.
---
## 2026-08-07 — tier-C: DecoManager.UpdateTick thread queues and ring

Done (V3.1.0 b14 IL):
- Drain add/remove/reset queues under lock; checkDelayTicks reset to 20.
- Player deco-chunk ring via GamePrefs 173; start UpdateDecorationsCo.
---
## 2026-08-07 — tier-C: Chunk.SetBlockRaw silent write path

Done (V3.1.0 b14 IL):
- SetBlockRaw IL=386: y>=255 air, water flow, IndexedBlocks, heightmap, tickedBlocks.
- Dirty flags bMapDirty/isModified/bEmptyDirty; no light/mesh/stability RPC.
---
## 2026-08-07 — tier-C: IsLandProtectedBlock and map-edge soft bounds

Done (V3.1.0 b14 IL):
- IsLandProtectedBlock: primary lpblock, deadZone, self allow, ally keystone flag.
- InBoundsForPlayersPercent: edge inset 50 / span 80, min axis, threshold 0.5.
---
## 2026-08-07 — tier-C: World.CanPlaceBlockAt claim and trader gates

Done (V3.1.0 b14 IL):
- CanPlaceBlockAt: trader area, InBoundsForPlayersPercent 0.5, GameStats 1/44 claim ring.
- CanPickupBlockAt: trader deny then CanPlaceBlockAt(traderAllowed=false).
---
## 2026-08-07 — tier-C: getMaxStabilityAround and vehicle attach

Done (V3.1.0 b14 IL):
- getMaxStabilityAround: AllDirections, StabilitySupport max, bFromDownwards.
- ChangeStability recursive stab-1 with non-support cap 1.
- TurretTracker.Update save every 120s; Attach/Detach seat pose and driver flags.
---
## 2026-08-07 — tier-C: Stability queueStabilityAvail cap 200

Done (V3.1.0 b14 IL):
- BlockPlacedAt enqueues avail recompute only when queue count < 200.
- BlockRemovedAt neighbor re-queue uses the same 200 hard cap.
---
## 2026-08-07 — tier-C: FallingBlock crush damage and land drops

Done (V3.1.0 b14 IL):
- AddFallingBlock dedupe/stability/oversized gates; OnBlockStartsToFall -> Air.
- FallingBlock/Blocks hit damage min(40, massKg*-vy*0.05)*passive 164, max 3 hits.
- Land: vel^2 < 0.0625; DropItemsOnEvent; SetDead.
---
## 2026-08-07 — tier-C: updateTasks freeze and GroupFallingBlocks BFS

Done (V3.1.0 b14 IL):
- updateTasks GamePrefs[46] freeze (non-drone); aiActiveDelay LOD; path apply order.
- EAIManager interestDistance FastMoveTowards(10, 1/120).
- GroupFallingBlocks 6-neighbor BFS size clamp; CreateFallingBlockGroup spawn.
---
## 2026-08-07 — tier-C: EAI BreakBlock/Wander/RunAway/Ranged/FindTarget leaves

Done (V3.1.0 b14 IL):
- EAIBreakBlock ally damageBoost +0.2 and attack delay formula.
- EAIWander CanExecute 120 no-player / executePercent / CalcInDir 90.
- EAIRunAway path end 1.21 and pathTicks 60; panic speed subclasses.
- EAIRangedAttackTarget look/SeekYaw then UseHoldingItem state machine.
- FindTarget see-distance, breadcrumb 15/24, bounds expand +4.
---
## 2026-08-07 — tier-C: EAIApproachAndAttackTarget Update phases

Done (V3.1.0 b14 IL):
- Home return FindPath 0.8 aggro, homeTimeout 0.05, give-up + sleeper pose.
- Relocate/target vel EMA; eat DamageEntity 35; chase FindPath + CanSee look.
- CanExecute sleep/stun/jump-swim and targetClasses chaseTimeMax.
---
## 2026-08-07 — tier-C: DropItemsOnEvent and PartyQuestChange

Done (V3.1.0 b14 IL):
- DropItemsOnEvent IL=246 drop table, stick place vs ItemDropServer, scrap half.
- PartyQuestChange fan-out; HandlePlayer location rect or 15 m; ChangeStatus.
---
## 2026-08-07 — tier-C: EntityItem OnUpdateEntity lifetime and collect

Done (V3.1.0 b14 IL):
- OnUpdateEntity: lifetime -= 0.05, ground counter 10, distraction/Y death.
- OnCollectServer: RemoveEntity reason 2 only.
---
## 2026-08-07 — tier-C: AddKillXP and SharedKillServer party XP split

Done (V3.1.0 b14 IL):
- AddKillXP: ExperienceValue, passive 193, modifier, GetPartyXP, _xpFromKill.
- SharedKillServer: same base XP; other members within GameStats[54]; _xpFromParty.
- Killer skipped in SharedKill loop; SharedKillClient quest EntityKilled hook.
---
## 2026-08-07 — tier-C: console 300-char reject, EntityAliveFlags bits

Done (V3.1.0 b14 IL):
- ServerConsoleCommand rejects cmd length > 300 before resolve; deny msgServer25.
- EntityAliveFlags Process bit setters corrected (god DataItem, alert remote-only).
---
## 2026-08-07 — tier-C: LockRequestServer 5-target cap and lock maps

Done (V3.1.0 b14 IL):
- LockRequestServer IL=239: stale unlock, max 5 targets, single vs shared maps.
- CanLockOnServer gate; OnLockedServer; NetPackageLockResponse flags 192.
- ForceUnlockLockTarget walks single+shared holders and force-unlocks.
---
## 2026-08-07 — tier-C: EntityTrader OnUpdateLive + DropContent multi-bag

Done (V3.1.0 b14 IL):
- EntityTrader.OnUpdateLive IL=315 quest list, 10m bounds unload/greet, open-close.
- DropContentInLootContainerServer multi-bag by loot container size, y+0.25.
---
## 2026-08-07 — tier-C: GetLandClaimOwner self/ally/other + offline hours

Done (V3.1.0 b14 IL):
- Outer GetLandClaimOwner GameStats[1] off / trader area / claim size GameStats[44].
- Per-chunk lpblock primary TEFeatureLandClaim; deadZone half-extent.
- Enum self=1 ally=2 other=3; IsLandProtectionValidForPlayer GameStats[46]*24h.
---
## 2026-08-07 — tier-C: MinEvent GiveExp, loot override, rage, jam

Done (V3.1.0 b14 IL):
- GiveExp/GiveSkillExp AddLevelExp + dirty flags; SetProgressionLevel max/-1.
- AwardChallenge/QuestStat EntityPlayerLocal only via QuestEventManager.
- SetItemInSlot armor EquipSlot gate; ResetHeldItem; SetHeldItemJammed metadata.
- Rage StartRage/StopRage on EntityHuman; SetOverrideLoot server comma list.
---
## 2026-08-07 — tier-C: full UAI task Start+Update table (5 types)

Done (V3.1.0 b14 IL):
- Enumerated all concrete UAITask* types (only 5).
- Start+Update for MoveToTarget, Wander, AttackTargetEntity/Block, FleeFromTarget.
- Flee sets home area radius 10 on path end; Attack dual Attack(false/true) pattern.
---
## 2026-08-07 — tier-C: EntityStatChanged, StatsBuff, TE Process, QuestObjective

Done (V3.1.0 b14 IL):
- EntityStatChanged Process IL=88 self-echo skip, Health FireEvent 9, rebroadcast.
- EntityStatsBuff Process IL=76 remote Buffs.Read + server flags 192 fan-out.
- NetPackageTileEntity Process IL=103 teBlockId drop + stream mode + rebroadcast.
- QuestObjectiveUpdate eventType 0/1/2; HandlePlayer distance 15 treasure count.
---
## 2026-08-07 — tier-C: sleeper TickSpawnCount, CheckSpawnPos, HandleFuel re-pin

Done (V3.1.0 b14 IL):
- TickSleeperVolumes zeros TickSpawnCount under lock; Tick gates UpdateSpawn <2.
- CheckSpawnPos chunk readiness; FindSpawnIndex hidden + farthest fallback.
- HandleFuel: not-burning early return; 0.01s quantize; fuel[0] consume path.
- Corrected mid-wave restart: vanished mapped entity (GetEntity null), not live.
---
## 2026-08-07 — tier-C: damageEntityLocal, ProcessDamage, EffectManager.GetValue

Done (V3.1.0 b14 IL):
- damageEntityLocal IL=484 DR build (armor, dismember, StunProne/Knee thresholds).
- ProcessDamageResponse IL=86 net fan-out; ProcessDamageResponseLocal IL=903.
- EffectManager.GetValue IL=372 stack; ItemValue.FireEvent IL=107 recursion.
---
## 2026-08-07 — tier-C: GameTimer formula, ThreadManager drain, Astar merge 76

Done (V3.1.0 b14 IL):
- GameTimer.updateTimer IL=74 stopwatch/timeScale/ticksPerSecond formula.
- ThreadManager.UpdateMainThreadTasks double-buffer swap + invoke.
- EntityEnemyAnimal electrocute early-out; Astar UpdateGraphs Merge size 76.
---
## 2026-08-07 — tier-C: SimpleRPC, ChatMessageServer, SendPackage, OnDeathUpdate

Done (V3.1.0 b14 IL):
- SimpleRPC IL=59 holding activate/reset + track fan-out.
- ChatMessageServer IL=195 mod interrupt + recipient fan-out; GameMessage 61.
- SendPackage list IL=168 attached/range filters.
- OnDeathUpdate corpse DeadBodyHitPoints path.
---
## 2026-08-07 — tier-C: canDespawn, unloadEntity, AwardKill/AddScore chain

Done (V3.1.0 b14 IL):
- canDespawn IL=14 (not client/dynamic/sleeping); Despawn IsDespawned;
  unloadEntity IL=216 full remove path.
- GameManager.AwardKill remote package vs QuestEvent; AddScoreServer remote/
  local fan-out; EntityAlive.AddScore counters/GameStats.
---
## 2026-08-07 — tier-C: CheckDespawn, player OnUpdateLive, explosion attack, save chain

Done (V3.1.0 b14 IL):
- CheckDespawn IL=198 (20-tick sample, 130m/80m bands); IsInFrontOfMe half-angle;
  EntityPlayer.OnUpdateLive see-clear + sleeper triggers.
- Explosion.AttackBlocks 553 / AttackEntites 691 EffectManager radii.
- SaveWorld → ChunkProvider.SaveAll → RegionFileManager; players.xml.
---
## 2026-08-07 — tier-C: explode AttackBlocks, LetBlocksFall, DurationTick, join pkgs

Done (V3.1.0 b14 IL):
- GameManager.explode IL=194 AttackBlocks/Entities + ExplosionClient S2C.
- LetBlocksFall group/single falling entity create path.
- BuffValue.DurationTick UpdateRateTicks.
- NetPackagePlayerId / PlayerSpawnedInWorld process.
---
## 2026-08-07 — tier-C: FireEvent fan-out, SetAttackTarget, explosions, falling

Done (V3.1.0 b14 IL):
- FireEvent IL=57 full fan-out (class/progression/challenge/inv/equip/buffs).
- SetAttackTarget IL=70 net package; SeeCache clear every 30 ticks.
- ExplosionServer delay/coroutine; ExplosionClient force+ChangeBlocks.
- AddFallingBlock hashset dedupe + DynamicMesh observer.
---
## 2026-08-07 — tier-C: AwardKill, SetDead, sleeper OnTriggered, Respawn

Done (V3.1.0 b14 IL):
- AwardKill IL=66 score path; SetDead Health=0; OnTriggered IL=14;
  EntityPlayer.Respawn outline.
---
## 2026-08-07 — tier-C: inventory Apply, party accept, AIDirector components

Done (V3.1.0 b14 IL):
- InventoryTransaction.Apply IL=126 InitialHash/ops/Finalize; RequestServer unlock.
- Party.ServerHandleAcceptInvite IL=89; PartyManager.CreateParty IL=24.
- AIDirector.CreateComponents IL=31 fixed list; GameStateManager.OnUpdateTick 198.
---
## 2026-08-07 — tier-C: death loot path and ItemDropServer chunk cap

Done (V3.1.0 b14 IL):
- combat-damage §3.1: OnEntityDeath AwardKill/ModEvents/dropItemOnDeath.
- loot-economy §6b: ItemDropServer IL=268 with 50 EntityItem/chunk cull;
  DropContentInLootContainerServer IL=104 bag spawn.
---
## 2026-08-07 — tier-C: DisconnectClient and SavePlayerData order

Done (V3.1.0 b14 IL):
- network: DisconnectClient IL=184 ordered disconnect/save/party/quest/unlock;
  SavePlayerData IL=91 + ModEvents.SavePlayerData.
---
## 2026-08-07 — tier-C: join spawn/auth path, damage tags, CommandAllowedFor

Done (V3.1.0 b14 IL):
- server-lifecycle: Authorize IL=47, RequestToSpawnPlayer 496, PlayerSpawnedInWorld
  127, SpawnEntityInWorld 178.
- items: GetDamageEntity/Block FastTags + EffectManager + MaxIncomingDamage.
- console-commands: CommandAllowedFor userLevel <= cmdLevel.
---
## 2026-08-07 — tier-C: TickEntity order, path apply helpers, ChangeBlocks

Done (V3.1.0 b14 IL):
- entity-ai §7: TickEntity IL=148 chunk membership + OnUpdateEntity gates;
  LookHelper pitch damp; ASPPathNavigate Update/SetPath; MoveHelper 1236 pointer.
- world-chunks §5.1: ChangeBlocks IL=530 multi-block apply; SetBlocksOnClients 192.
---
## 2026-08-07 — tier-C: more package Process (chat/quest/score/kill/skill)

Done (V3.1.0 b14 IL):
- EntityRemove, SimpleChat, SharedQuest, AwardKill, SetSkillLevel, AddScore,
  MapChunks, ConfigFile, WorldSpawnPoints, KeyExchangeComplete, PlayerDisconnect
  process notes; census 1454/853.
---
## 2026-08-07 — tier-C: EAI leaf Update/CanExecute IL table

Done (V3.1.0 b14 IL):
- entity-ai §D2: ApproachAndAttack 846/CanExecute 70, RangedAttack 107,
  RunAway 105, Wander.CanExecute 94, DestroyArea 60, ApproachSpot 40,
  Dodge 27, Wander/Leap Update 7.
---
## 2026-08-07 — tier-C: manager Update behaviour re-pins

Done (V3.1.0 b14 IL):
- managers: Vehicle/Drone unloaded ECD reconcile; QuestEvent objectives;
  Turret 120s / Faction 60s save; GameEvent Handle* chain; Power 0.16/120;
  WorldBlockTicker scheduled+random; SendChunksToClients remove/send.
---
## 2026-08-07 — tier-C: TickEntities slice math, console path, AddLevelExp

Done (V3.1.0 b14 IL):
- loop-gmupdate: exact TickEntities EMA/span/25/sliceCount formula.
- console-commands: ServerConsoleCommand IL=125 ordered steps.
- progression: AddLevelExp IL=161 bonus + recursive apply order.
---
## 2026-08-07 — tier-C: stats waitTicks, buffs Tick, blood moon, eat consume

Done (V3.1.0 b14 IL):
- entity-stats §1.1: waitTicks 10-phase TickWait (base + PlayerEntityStats).
- buffs: EntityBuffs.Tick IL=179 Invalid/Finished/Remove walk.
- spawning: AIDirectorBloodMoonComponent.Tick IL=170 party path.
- items: ItemActionEat.consume IL=154 quest/smell/refund.
- tile-entities: Chunk.UpdateTick IL=26 TeTick confirmation.
---
## 2026-08-07 — tier-C: OnUpdateEntity/Live phases + fireShot/melee

Done (V3.1.0 b14 IL):
- entity-ai §2.0: OnUpdateEntity IL=457 then OnUpdateLive IL=363 ordered work.
- items §4.2: fireShot IL=482 raycast/hit path; DynamicMelee ExecuteAction IL=210.
- server-lifecycle: PlayerLoginRPC Authorize changelog.
---
## 2026-08-07 — tier-C: DamageEntity gates, UAI tasks, OnUpdateTick order

Done (V3.1.0 b14 IL):
- combat-damage: DamageEntity IL=236 consecutive/FF/god/dead/mult/local apply.
- entity-ai: UAITaskMoveToTarget/Wander/AttackTargetEntity Update leaves.
- loop: OnUpdateTick always/server order re-pin.
- server-lifecycle: PlayerLoginRPC -> AuthorizationManager.Authorize.
---
## 2026-08-07 — tier-C: Chunk process + TEFeature wire + MinEvent leaves

Done (V3.1.0 b14 IL):
- NetPackageChunk Process IL=126 (overwrite unload/read vs add NeedsRegeneration).
- TEFeatureLockable/Storage/Signable/AreaRepair Write tails.
- MinEvent CallGameEvent, AddHealth, Ragdoll, AddProgressionLevel, ModifyStat,
  ShowToolbeltMessage Execute notes.
---
## 2026-08-07 — tier-C: landclaim/sleeper/deco/auth/addExp process re-pins

Done (V3.1.0 b14 IL):
- LandClaimRepair, PersistentPlayerState, SleeperWakeup, GameStats, DecoUpdate,
  SignDataRequest, DynamicMesh, AddExp Server/Client, AuthConfirmation,
  EncryptionRequest process notes; still-open table honesty update.
---
## 2026-08-07 — tier-C: SetBlock + inventory hash cache process

Done (V3.1.0 b14 IL):
- SetBlock Process IL=59 (ValidUser/Entity, SetBlocksOnClients, ChangeBlocks,
  DynamicMesh ChunkChanged); SetBlockResponse tooltips.
- InventoryDataRequest hash short-circuit vs full item dump; Response UpdateInventory.
- PlayerInventory applies to Sender.latestPlayerData + dirty flag.
---
## 2026-08-07 — tier-C: workstation/trigger wire + quest/party/gameevent process

Done (V3.1.0 b14 IL):
- tile-entities-power: Workstation.write IL=246 stream modes; PoweredTrigger.write
  IL=138 TriggerType tails.
- protocol-packages: PartyActions/Data, QuestEvent/Objective/EntitySpawn,
  TraderData, NPCQuestList, GameEventRequest/Response, BossEvent,
  EntityWaypointList Process IL sizes and authority notes.
---
## 2026-08-07 — tier-C: UAIBase chooseAction/updateAction

Done (V3.1.0 b14 IL):
- entity-ai §5.3: UAIBase.Update IL=18, chooseAction IL=97 (package DecideAction
  weighted pick), updateAction IL=63 (Init/Start/Update/Reset task chain).
- residuals/completion-bar census refresh (narrated 1439 / catalogued 868).
---
## 2026-08-07 — tier-C: high-value console Execute IL table

Done (V3.1.0 b14 IL):
- console-commands §2.1: KillAll, SpawnEntity, Teleport, SetTime, SaveWorld,
  Shutdown, Mem, Weather, Get/SetGamePref, CreateWebUser, LogGameState Execute
  sizes and authority notes.
---
## 2026-08-07 — tier-C: DamageEntity early outs + AliveFlags/stat process

Done (V3.1.0 b14 IL):
- DamageEntity Process IL=172 local-player discard gates (typ 15; ambient 1/25).
- AliveFlags Process IL=109 apply + server rebroadcast 192.
- StatChanged IL=88, StatsBuff IL=76, PlayerStats IL=70 process notes.
---
## 2026-08-07 — tier-C: collector/light/trap TE wire + spawn bands re-pin

Done (V3.1.0 b14 IL):
- tile-entities-power §4.6: Collector write IL=278, Light IL=48, RangedTrap
  stream modes, MeleeTrap owner-only.
- entity-ai §D3.6: SpawnUpdate distance/rect numbers cross-linked to spawning.md.
---
## 2026-08-07 — tier-C: more ProcessPackage + MinEvent action leaves

Done (V3.1.0 b14 IL):
- protocol-packages §6.21: process targets for ragdoll/velocity/speeds/stealth/
  anim/part/owned/equipment/item-fx/reload/cvar/drop-container/sound/particle/
  game-message/wall-volume/score/close-windows; dedupe FX table rows.
- minevents §7.1: AddBuff IL=211, ModifyCVar IL=154, Explode IL=83 (server
  ExplosionServer), presentation residual note.
---
## 2026-08-07 — tier-C: package ProcessPackage paths (Collect/Attach/...)

Done (V3.1.0 b14 IL):
- protocol-packages §6.21 process notes for EntityCollect, EntityAttach
  (AttachType 0-3), ItemDrop, PickupBlock, SetBlockTexture, SimpleRPC,
  HordeEvent, PrimeDetonator, SetAttackTarget; EmitSmell Process IL=1 no-op.
---
## 2026-08-07 — tier-C: workstation/forge ticks + sleeper spawn/despawn

Objective: keep optional depth moving (never-stop C grind).

Done (V3.1.0 b14 IL):
- tile-entities-power §4: Workstation UpdateTick IL=134 path, HandleFuel,
  HandleRecipeQueue/cycleRecipeQueue, Forge IL=340 fuel-tick melt, Vending
  rental expiry, Composite feature tick, Powered dirty flags.
- entity-ai §D8.2-D8.4: SleeperVolume UpdateSpawn IL=516, Despawn IL=48
  (sleeping-only unload), UpdatePlayerTouched IL=172.

Coverage unaccounted remains 0.
---
## 2026-08-07 — tier-C: PowerItem subtype ticks, WireActions, sleeper Tick, LookAt

Objective: continue optional annotation depth (tier C) after A+B complete.

Done (verified live V3.1.0 b14 IL):
- tile-entities-power: full PowerItem subtype tick table; corrected claim that
  PowerConsumerToggle.PowerChildren returns isToggled (it does not override;
  gate is HandlePowerUpdate Activate only); power.dat subtype tails;
  NetPackageWireActions SetParent/RemoveParent/SendWires process §3.6.
- protocol-packages: EntitySpawnResponse marked ToClient (client inventory ack);
  EntityLookAt int-truncated Vector3; WireActions field/process pointer.
- entity-ai §D8.1: SleeperVolume.Tick phase order from IL=137.

Coverage unaccounted remains 0. stock-check expected green.
---
## 2026-08-07 — tier-C depth: power ClientData, sector 7rg, BuffManager, audio fields

Objective: continue optional annotation depth after A+B complete (unaccounted=0).

Done (verified live V3.1.0 b14 IL):
- tile-entities-power §2.1: ClientPowerData + StreamMode write/read tables.
- save-region §3.4: sector 7rg open/version byte/V1 header 8196 layout.
- buffs §1.1: BuffManager registry.
- protocol-packages: HoldingItem carrier EntityNetworkHoldingData; Audio/Light/
  TreeFade/DroneParticle field detail in §6.21.
- items: EntityNetworkHoldingData pointer; completion-bar tier-C progress table.

Coverage unaccounted remains 0. stock-check green.
---
## 2026-08-07 — completion bar + unaccounted=0 + Raw 11-byte header

Objective: drive Coverage unaccounted to 0 and define honest "100%" (tiers A+B).

Done (verified live V3.1.0 b14):
- Coverage: unaccounted **0** (was 4). Closed via OOS analytics types + `logenv` catalog.
- server-lifecycle: analytics heartbeat 300s client-only (dedicated skips).
- out-of-scope-surface: HeartbeatEventData, Helper, TruncateStringSerializerConverter.
- inventories/console-command-list: `logenv` / ConsoleCmdLogEnvironment.
- save-region: Raw 11-byte header `7rr` + version:i32 + paddingBytes:i32.
- completion-bar.md + INDEX link; residuals §3 refreshed.
- console-commands: catalog count 188.

Verification: Coverage.exe unaccounted=0; make stock-check exit 0.
---
## 2026-08-07 — research: path drain, interest exit, chunk dirty, animator culling init

Objective: continue stock RE only (no zdtd). Close optim-facing research gaps
from PERF brief §7 without inventing levers.

Done (verified live V3.1.0 b14 ASM):
- entity-ai §D3.7: ASP FindPaths MoveNext re-pin (FIFO list[0], ldc.i4.8, no priority).
- network §2.2: interest exit = NetPackageEntityRemove reason Unloaded (ldc.i4.1).
- world-chunks: Chunk.get_NeedsSaving = isModified|hasEntities|TE|triggers.
- entity-ai addendum: BodyAnimator defaultCullingMode=AlwaysAnimate vs live CullUpdateTransforms.
- closed-gaps path section: drain re-pin + pointer to path BM measure (default-off).

Verification: DumpMethod FindPaths>d__8 MoveNext; updatePlayerEntity; get_NeedsSaving;
BodyAnimator.initBodyAnimator; EnumRemoveEntityReason DumpType.
---
## 2026-08-06 — hygiene + optim evidence handoff

- residuals §5: optimizer residual pointer notes Clone/chunk ownership closed.
- Sibling hygiene (separate trees): apm/loadgen measured-scaling + zig-clone link
  text/href fixed to optimizer/zdtd homes; optimizer PERF brief consumed research
  triage; optimizer .gitignore ignores local /server/ drop.
---
## 2026-08-06 — RE annotation + optim evidence (research-only)

Objective: close the location-table bit-packing residual and record stock IL
facts the optimizer brief still treats as open research (Clone / chunk encode),
without leaving 7dtd-research scope.

Done (verified against live V3.1.0 b14 ASM):
- **save-region §3.5:** Raw location = Int32[128] pairs + UInt32[64] stamps;
  on-disk 11 + 512 + 256 = 779 payload base; sector slot = LE u16 sectorIndex +
  unused byte + u8 sectorLength (ToShort/FromShort); timestamp via BitConverter
  on same slot base.
- **residuals:** region packing residual closed; closed-items row added.
- **items.md:** ItemStack.Clone Xref triage (162 sites; ~56 XUi; dedi mass TE +
  inventory + net Setup).
- **engine-limitations / world-chunks:** Clone fan-out + SendChunks ownership
  (sole UpdateTick caller; Setup from SendChunks + RebuildTerrain).

Verification: DumpMethod Get/SetLocationInfo, ToShort/FromShort, SaveHeaderData;
Xref ItemStack.Clone + ChunkManager.SendChunksToClients; make stock-check.

State: verified. Path admission already closed in closed-gaps (not re-opened).
---
## 2026-08-06 — research-docs-corpus hygiene + structure

Objective: fix all open findings from `workspace/outputs/research-docs-corpus-audit.md`
and improve hub structure for V3.1.0 (b14).

Done (verified):
- Inventory titles: gmupdate-calls.md, netpackages.md → V3.1.0 pins + correct il paths.
- INDEX: new **V3.1.0 shipped delta map** (replaces retired experimental-delta prose).
- Replaced vague "delta removed" pointers in network, coverage, re-methodology,
  sandbox-options, server-browser-prefabs with concrete topic links.
- sandbox-options §2: day/night Biome*Density/Respawn + ChickenCoop* / InfectionChance /
  Hunger/Thirst/StackSize multipliers (string-confirmed in live ASM).
- dynamic-mesh WriteRegion: Xref re-closed as self-retry only (no external callers).
- residuals closed-items row for WriteRegion; INDEX inventories prefer protocol-packages.

Verification: `make stock-check` exit 0; `make test` exit 0; INDEX orphans 0;
broken links in touched files 0; em dashes 0.

State: verified. Next: optional commit.
---
## 2026-08-05 — stock-re-corpus audit fixes

Objective: fix all problems surfaced by `workspace/outputs/stock-re-corpus-audit.md`
(paper/code audit of our RE corpus vs tools/consumers/live ASM).

Done (verified):
- **Critical wire:** `docs/tile-entities-power.md` NetPackageTileEntity layout
  now teBlockId:i32 + payloadLen:i32, write IL=27 / read IL=24 (matches
  protocol-packages §6.12 + live DumpMethod).
- **High census drift:** `docs/coverage.md` live census table → 4414 / 44107 /
  SaveLoad 926 / CurrentSaveVersion 23 (was stale 4401/43901/884 under 3.1 banner).
- **Framing:** README, protocol-packages, protocol-frames, loop-gmupdate titles/pins
  to V3.1.0 (b14); re-methodology §1 shows live vs historical V3.0.1 columns.
- **Gate:** `tools/tests/check_stock_facts.py` now fails on stale coverage census
  numbers, README pin, and TE layout (teBlockId/i32 + rejects u16-only TE fence).

Verification: `make stock-check` exit 0; `make test` exit 0 (dedi coverage docs +
stock-check --require-live). Live DumpMethod TE write still IL=27 (prior audit).

State: verified. Next: optional commit of doc+gate fixes; re-run Coverage.exe only
if unaccounted tier needs a fresh cite.
---
## 2026-07-23 — re-audit-extend (audit all docs + extend RE + consolidate tooling)

Objective: audit all docs; do more RE (systems + wire protocol); consolidate RE
tooling into this repo; document how to RE; add stock-research policy to sibling
AGENTS.md.

Done (verified against live V3.0.1 Assembly-CSharp.dll):
- **Tooling consolidated -> tracked `tools/`** (`src/` general Cecil dumpers +
  build.sh; user added `parity/` version-diff + `re-scratch/` Zig one-offs).
  Census/DumpMethod/DumpType/DumpNetPackages/NetProtocolCensus built and smoke-tested.
- **New RE (wire):** dumped all 193 NetPackage bodies + metadata census
  (`il/netpackages-v3.0.1/`, git-ignored). Decoded Chunk, ChunkRemove, WorldTime,
  WorldInfo, EntitySpawn(+EntityCreationData header), EntitySpawnResponse,
  SetBlock(+BlockChangeInfo), SetBlockResponse, HoldingItem, PlayerInventory,
  and the full 4-package encryption handshake (closes residual). Findings:
  6 channel-1 packages, 8 compressed, 10 pre-auth. -> `docs/protocol-packages.md`.
- **Docs:** new `docs/re-methodology.md` (how to RE) + `docs/protocol-packages.md`;
  updated protocol/coverage/residuals/network/engine-limitations/INDEX/README;
  new `AGENTS.md`. Verified: census 4401/43901/631/884 match; corrected NetPackage
  count fork (~196 -> 194 = 193 wire + NetPackageManager); fixed 3 broken
  protocol-frames anchors.
- **Sibling AGENTS.md:** added stock-research policy block to all 7 siblings +
  top-level; fixed stale `research/` -> `7dtd-research/` paths.
- **Audit:** `workspace/outputs/re-audit-extend-doc-audit.md` (26 findings).
  Objective numeric/link fixes applied. NOT auto-fixed (need author decision on
  which value is authoritative): bottlenecks.md self-contradiction vs its own
  O(N^2.26) correction (#2), chunk 56-60% vs 5% (#3), algorithms/zig-clone
  interest framing (#4), GC knob honored/not (#5), heap-size forks 5.6/6.9/7 GB (#6).

Verification: 0 broken internal links; 0 em dashes in new content; il/ dumps and
tools/bin git-ignored. State: wire RE verified from IL; audit analytical
contradictions surfaced, unresolved by design.
Next: author decides the 5 analytical audit contradictions; optionally annotate
EntityCreationData per-class tail and DynamicMesh/POIAround bodies.

## 2026-07-23 (cont.) — scope split + reconciliation

- **Scope boundary enforced.** Moved 6 optimization-mod docs to `7dtd-optimizer/docs/`:
  bottlenecks, algorithms, measured-scaling, runtime-tuning, allocation-reuse,
  aggressive-optimizations. Rewrote 89 cross-repo links (both directions);
  0 broken after. INDEX restructured (movers now an "optimization-mod companion"
  section, dropped from one-home table). AGENTS.md gained a "Doc scope" section
  defining stock-RE-only membership.
- **Stock-RE reconciliations applied:** F16 damageType 16 = Suffocation (verified
  `EnumDamageTypes` in DLL; fixed protocol-frames "Drown"); F8 terrain-height
  dump table relabeled (expanded = historical, live = stock per coverage pin);
  F14 stale `research/` paths fixed in protocol/zig-clone/terrain-height;
  F1 counts already fixed. F17 (2 channels) now substantiated (channel 1 real).
- **Deferred to optimizer repo (per user):** F2-F7, F13, F15 (contradictions
  inside the moved docs) travel with them.
- **Editorial cleanups** (F18-F21, F25, F26) dispatched to subagent.
- **Review finding:** `zig-clone.md` (clone/zig signal 77) is reimplementation
  architecture that `zdtd/` links to as its design doc. Flagged for possible move
  to `zdtd/`; NOT moved (zdtd currently references it as external architecture,
  needs user confirm). All other stay-docs are legitimately stock RE.
- Next: after editorial subagent, finish F24 (coverage family 8 note) + F14 sweep
  of network/loop/entity-ai/loop-gmupdate/coverage; final cross-repo link check.

## 2026-07-23 (cont.) — reconciliation complete

- Editorial subagent done (F18-F21, F26): all changelog blocks deduped to 1,
  loop.md fence fixed, entity-ai/deeper single-H1, AI-LOD phrasing aligned.
- Finished stock-RE fixes: F14 (all `research/` paths normalized), F24 (coverage
  family-8 = private-companion narrative), F10 (residuals policy allows
  annotation-backlog), F22 (oss-tools em dashes; **0 em dashes repo-wide**),
  coverage family-6 net status updated for protocol-packages.
- Sibling inbound links to moved docs repointed (apm, loadgen, zdtd, realworld,
  optimizer's own docs): 20 links. **0 broken links across both repos.**
- Audit resolution log appended to re-audit-extend-doc-audit.md.
- State: verified. OPEN DECISION: zig-clone.md (reimpl architecture) -> move to
  zdtd/ or keep as research-to-clone bridge? Not moved pending user confirm.
- DEFERRED to optimizer repo (travel with moved docs): F2-F7, F12, F13, F15.

## 2026-07-23 (cont.) — doc hierarchy review

Reviewed information architecture across all 18 narratives + 8 inventories.
Findings: no orphans (every doc in-degree >= 1), every doc referenced by INDEX,
every doc has a clear H1 + Owns identity. Two structural fixes: aidirector.md had
a real second H1 (merge artifact) -> demoted to H2; INDEX "Generic engine
narratives" was a flat ~16-row list in arbitrary order -> regrouped into 5
topical clusters (A meta/method, B loop/sim, C entities/AI, D world/terrain/save,
E net/wire) + F optimizer companion, each doc listed once. Kept docs/ physically
flat (21 files) with grouped INDEX: standard for this size, avoids breaking 100+
links for marginal gain. 0 broken links, all docs exactly 1 H1 (fence-aware).

## 2026-07-23 (cont.) — RE tooling consolidation + documentation

- **All RE tooling now in `7dtd-research/tools/`** (was split across optimizer/tools
  + il/zdtd_re_tools). Moved 39 legacy per-family dumpers -> `tools/legacy/`, the 2
  RE tests -> `tools/tests/`; removed `7dtd-optimizer/tools/` entirely (orphaned
  .exe/Cecil cleaned). build.sh now builds src/ + best-effort legacy/ (37/39 build;
  DumpGmUpdate + DumpExtra2 pre-corrupted, superseded by src/DumpMethod).
- Fixed moved tests' paths (Cecil in bin/, dumpers in legacy/); both PASS:
  test_dedi_coverage_docs "OK", test_re_dump_regen regenerates non-empty output.
- Updated optimizer refs (AGENTS, DEVELOPMENT, ARCHITECTURE, OPTIMIZATION_CANDIDATES)
  to point at ../../7dtd-research/tools/. INDEX + re-methodology + tools/README
  rewritten as the complete tool+process catalog. 0 broken links across all repos.
- Dispatched fresh full doc audit (re-audit-2) after the restructure; fixes pending.

## 2026-07-23 (cont.) — re-audit-2 fully resolved

Fresh full audit (re-audit-2-doc-audit.md, 26 findings) after the restructure.
All oracle numbers passed; findings were stale-structure debris + scope leakage.
All High/Medium/Low fixed (split: lead did scope/structure/High; subagent did the
mechanical batch). Highlights: stale `7dtd-optimizer/tools/` regen recipes ->
`tools/legacy/` + build.sh (loop-gmupdate, terrain-height, entity-ai, closed-gaps);
il/README dumper attribution corrected; closed-gaps §9 Region/WorldState "open" ->
closed (only sector codec residual); optimization-lever content in entity-ai
§11-12 + loop-gmupdate §9 + network §4b trimmed to optimizer pointers; entity-ai
duplicate section numbering -> D1-D14; README reframed stock-only. Verified: 0
broken links (3 repos), 0 em/en dashes, all docs single-H1, coverage gate passes.
State: verified.

Note: the L3 fix (dropping "(IL=1585)" from managers.md) removed the file's only
`IL=` token, which test_dedi_coverage_docs keys on -> caught by re-running the
gate; fixed by adding a column caption ("Update IL column is ... e.g. TwitchManager
IL=1585"). Both gates green.

## 2026-07-23 (cont.) — whole-assembly surface map (the "100%" request)

User asked to "reverse 100% of the game code and document in minute detail."
Two hard limits: (1) redistribution/copyright - a full transcription of 1.73M IL
instructions is a copy of TFP's proprietary game, which this repo's policy and
.gitignore forbid (docs quote few lines only); (2) effort - 53,011 method bodies
is not a single-pass hand narrative. Refused the literal ask (won't commit a full
game copy or fabricate coverage); delivered the honest maximum:
- `tools/src/FullSurface.cs` - committable whole-assembly METADATA census (all
  7,413 types: namespace/kind/base/signatures/IL sizes, no bodies).
- `tools/src/DumpAll.cs` - full LOCAL IL reversal (every method body, one file per
  type) into git-ignored `il/full-v3.0.1/`; proven on GamePath (18 types/112 methods).
- `docs/full-surface.md` - committed map of all 87 namespaces by functional cluster
  + honest coverage ledger (dedicated hot path deeply narrated = low-single-digit %
  of 7,413 types but the surfaces that run every tick) + roadmap + regen instructions.
Measured scope: 7,413 types / 53,011 methods-with-body / 1,734,742 IL / 87 ns;
`<global>` = 6,276 types (85%). Verified: dumps git-ignored, tool sources tracked,
0 broken links, 0 em dashes, coverage gate green.

## 2026-07-23 (cont.) — reversing dedicated codepaths toward 100% (batch 1)

Incremental narrative coverage of dedicated-server subsystems beyond the hot path,
each as transformative analysis (minimal IL quotes, policy-compliant) with mermaid
for every state machine (user requirement).
- **webserver.md** (lead): Web admin server. HTTP pipeline, auth/session +
  Steam OpenID, reflection REST host, permission model, SSE lifecycle. 6 diagrams.
- **console-commands.md** (lead): SdtdConsole registry + dispatch + permission gate,
  telnet auth (N-strike lockout), shared with web Command API. 3 diagrams.
- In flight (4 researcher subagents): UAI, GameEvent sequence framework,
  world-generation, platform-auth. Each writes one docs/<slug>.md with state-machine
  diagrams; lead integrates (INDEX cluster F + full-surface ledger) + verifies.
- New tools: FullSurface (committable whole-assembly metadata) + DumpAll (full local
  IL); docs/full-surface.md holds the 87-namespace map + coverage ledger.
Verified: 2 new docs 0 em dashes / 0 broken links / 9 mermaid; dumps git-ignored.
Next: integrate the 4 subagent docs; then <global> subsystems (spawn, vehicles,
buffs, weather, chat, persistence).

## 2026-07-23 (cont.) — dedicated codepaths batch 2

Lead-written + verified (0 em/en dashes, 0 bulk IL, state-machine diagrams):
- webserver.md (6), console-commands.md (3), server-lifecycle.md (4), buffs.md (2).
Integrated subagent: uai.md (3 diagrams; found UAI stock-dormant + IL quirks).
In flight (6 researchers): game-events, world-generation, platform-auth, spawning,
vehicles-drones-turrets, tile-entities-power.
Coverage ledger (full-surface.md) updated: web, console, lifecycle, buffs, UAI ->
Narrated. Remaining dedicated: weather/sky, chat, loot/traders, game-modes, quests,
blocks/items + ItemAction + MinEvent frameworks, crafting, power (if not in tile-ent).
Next: integrate the 6 in-flight docs as they land; dispatch batch 3.

## 2026-07-23 (cont.) — dedicated codepaths batch 3

Integrated (verified 0 em/en, 0 bulk IL, state machines): platform-auth (5),
spawning (5), tile-entities-power (10), vehicles-drones-turrets (7),
game-events (6). Lead-written: chat (1); game modes folded into server-lifecycle §2.1.
In flight (7 researchers): world-generation, weather-environment, loot-economy,
quests-challenges, blocks, minevents, items.
Narrated dedicated subsystems now: web, console, lifecycle+game-modes, buffs, chat,
UAI, game-events, platform-auth, spawning, tile-entities+power, vehicles/drones/turrets.
Remaining after batch 3: item-actions detail (in items), crafting/recipes,
damage/combat consolidation, then full-corpus consistency+link+diagram audit.

## 2026-07-23 (cont.) — dedicated codepaths COMPLETE

All dedicated-server codepaths are now hand-narrated (transformative analysis,
full IL kept local/git-ignored per policy). 23 new subsystem docs this campaign
(11 lead-written, 12 via researcher subagents, all lead-verified + integrated):
  webserver, console-commands, server-lifecycle (+game modes), platform-auth, chat,
  spawning, buffs, entity-stats, combat-damage, blocks, items, crafting-recipes,
  loot-economy, tile-entities-power, vehicles-drones-turrets, weather-environment,
  progression, game-events, quests-challenges, minevents, uai, world-generation,
  twitch-integration.
Plus the pre-existing hot-path + wire docs. Coverage ledger (full-surface.md)
flipped every dedicated cluster to Narrated; out-of-scope surface (client render,
audio, editor, vendored libs) + native residuals honestly enumerated, not narrated.

New tooling: FullSurface (whole-assembly metadata census) + DumpAll (full local IL).
One subagent auto-committed world-generation.md; reset --mixed to keep the corpus
uniformly uncommitted (user commits when ready).

FINAL AUDIT (43 docs): 0 em/en dashes, 0 broken links (repo-wide), all single-H1,
mermaid fences balanced, 0 orphans, 145 state-machine/flow diagrams. Every state
machine has a mermaid diagram (user requirement). State: verified.

## 2026-07-23 (cont.) — dedicated codepaths COMPLETE (verified by gap analysis)

The premature "complete" claim was re-verified by systematic gap analysis, which
found real misses (good). Closed them:
- Manager sweep (136 *Manager types), UpdateTick/OnUpdateTick sweep, and
  IsDedicatedServer-gated sweep against all docs.
- Real gaps found + closed: mod-loading.md (ModManager pipeline + EAC gate),
  dynamic-mesh.md (server regen/threading/streaming, subagent), parties-factions.md
  (party/faction/ally, subagent).
- Confirmed non-gaps (honest): ProjectileManager (client MoveScript; ranged combat
  in items/combat-damage), SignDataManager/WireManager (client render), leaf blocks
  + TE features (framework-covered), and platform-service wrappers (PermissionsManager
  host-gate, GeneratedTextManager text-filter, ServerListManager browser) -> noted in
  residuals.md as native/platform residuals.

Experimental build (user ask): fetched latest_experimental via steamcmd (17.6 GB),
ParitySurface + parity_diff + census diff vs V3.0.1. ONE wire change
(NetPackageTileEntity: +teBlockId i32, payload len u16->i32) + new held-entity feature
(ItemClassHeldEntity/WildChicken, stress/freakout/drop) + new join-event + console cmd.
Reversed into docs/experimental-delta.md.

FINAL: 47 narrative docs, 156 state-machine/flow diagrams, 0 em/en dashes, 0 broken
links repo-wide, all single-H1, no orphans. Every dedicated-server codepath is
hand-narrated with diagrams; out-of-scope (client render/audio/editor/vendored) and
native residuals honestly enumerated. State: verified. DEDICATED CODEPATHS DONE.

## 2026-07-23 (cont.) — reachability verification + stealth gap

User challenge "did you fully reverse everything the server needs" -> ran a deeper
"heavy unreferenced types" lens which found a real miss: PlayerStealth (server
stealth/noise/smell detection, TickServer 430 IL). Wrote docs/stealth-smell.md.
Then built the definitive lens: tools/src/Reach.cs (call-graph reachability from
GameManager.StartAsServer/gmUpdate/tick drivers, devirtualizing callvirt).
Reached 28,374 methods / 4,516 types. Cross-filtered to Assembly-CSharp game types:
every reachable SUBSYSTEM is documented; reachable-undocumented remainder is
utility/data plumbing, framework leaves (blocks/items/TE-features/game-events),
client/editor/render, or platform residuals (Discord). Added two borderline notes:
TransactionalInventory (server inventory anti-dupe) -> items.md; SaveDataManager
(platform save-file layer) -> save-region.md. Noted the reachability lens in
re-methodology. Corpus: 48 docs, 158 diagrams, 0 broken/dashes/badH1.
Honest status: no uncovered dedicated subsystem remains under 4 converging lenses
(managers, tick-methods, dedi-gated, reachability); full method-body IL is 100%
reversible locally (DumpAll) but not transcribed by policy; leaves covered by
framework not exhaustively.

## 2026-07-23 (cont.) — leaf-enumeration catalogs

Completed the enumeration layer beneath the framework narratives: generated 4
metadata catalogs under inventories/ (names + base + IL, no bodies) so every leaf
instance is listed, not just the contract:
- block-behaviors.md (91 Block leaves), item-actions.md (84 ItemAction/Class),
  minevent-actions.md (73 action/requirement), console-command-list.md (179 commands).
Registered in INDEX inventories; cross-linked from blocks/items/minevents/
console-commands. 427 leaves catalogued. Corpus clean (0 broken/dashes/badH1).
Coverage now complete at both levels: subsystems narrated + leaves enumerated.

## 2026-07-23 (cont.) — leaf catalogs made transitively accurate + extended

Corrected the leaf catalogs to use transitive inheritance (was direct-base only, which
over/under-counted). Accurate counts: block-behaviors 65, item-actions 38,
minevent-actions 71, console-command-list 189; added quest-objectives 38,
sequence-requirements 42. 6 catalogs, 443 leaves enumerated by real inheritance.
Fixed the now-stale counts in INDEX + framework cross-links. Corpus: 48 narratives +
14 inventories = 62 docs, 158 diagrams, 0 broken/dashes/badH1.
Coverage complete + accurate at both levels (subsystems narrated, leaves enumerated).

## 2026-07-24 — per-leaf behavioral pass

Took the enumeration catalogs to per-leaf BEHAVIORAL descriptions (user request):
- console-command-list.md: 186 commands, each with the game's own getDescription
  (extracted via a new CmdDesc tool: name + permission + function).
- block-behaviors (65), item-actions (38), minevent-actions (71), quest-objectives (38),
  sequence-requirements (43): each leaf gets a function (humanized name + base role +
  code-derived hint) + its base subclass + key overridden methods (behavioral
  fingerprint), via a generic Hint extractor over transitive subclasses.
441 leaves now behaviorally described (commands at full fidelity from shipped
descriptions; others name+code-derived, honestly labeled). 0 broken/dashes.
Corpus: 48 narratives + 14 inventories.

## 2026-07-24 — peer-review resolution (new docs)

Ran a peer-review pass (reviewer lens) over the freshly written narratives and
applied every finding, each re-verified against IL before the edit:

WRONG/MAJOR (fixed, IL-checked):
- chat.md §2: routing is **recipient-list based**, not channel-based. Rewrote the
  state machine: recipientEntityIds non-empty -> targeted send, else broadcast;
  EChatType is carried for display, server does not re-derive party/friends
  membership; ModEvents.ChatMessage hook; no command-prefix branch in
  ChatMessageServer.
- parties-factions.md §2.3: party chat sender supplies recipientEntityIds; server
  routes by the list, not by re-deriving membership.
- crafting-recipes.md: reframed to **split authority** (not server-authoritative).
  CanCraft runs client-side (XUiC_ItemActionList); backpack queue is client-ticked;
  workstation TE queue is server-ticked; server's authority is the inventory
  transaction (TransactionalInventory anti-dupe) + the workstation TE.
- experimental-delta.md §4: CVarOperation + the `CVarOperation _operation` param are
  **pre-existing in stable V3.0.1** (SetCustomVar IL=126); exp only adds a trailing
  `bool _forceSendToClients` (IL 126->130). Prior "new cvar ops" claim was wrong.
- experimental-delta.md §1: added the missed `WorldState.SaveLoad` 884->926 IL delta.
- Stripped `</invoke>` tool-artifact lines from dynamic-mesh/platform-auth/
  loot-economy/weather-environment.md (EOF residue).

MINOR (count/label drift, fixed against ground truth):
- console-commands.md "190" -> 186 (matches its own catalog).
- minevents.md dropped the precise "72 concrete" (72 types incl. abstract bases);
  now references the catalog.
- items.md dropped the imprecise "~122 Item*/~92 ItemAction*" name-prefix counts;
  now points to the enumerated item-actions catalog.
- dynamic-mesh.md: retry bounds differ by method (IL-verified): WriteRegion up to 5,
  WriteRegionHeaderData up to 10 (was conflated as "both 5").
- vehicles-drones-turrets.md: persistence signature `vda\0` (was `vd.a\0`).
- buffs.md: base `EntityStats.EntityBuffRemoved` is a no-op (IL=1, ret); the real
  work is the PlayerEntityStats override fanning to buffChangedDelegates (IL=63).
- mod-loading.md: added the real 7-member `EModLoadState` enum and noted the state
  diagram traces load-pipeline phases (mapped to the enum), not the members 1:1.

Corpus health after fixes: 0 em/en-dashes, 0 tool artifacts, 0 broken intra-doc
links (multi-H1 hits are bash comments inside code fences, false positives). All
review findings resolved. Verification state: verified (each fix traced to IL from
the stable V3.0.1 dedicated DLL). Next: optional zdtd gap implementation on request.

## 2026-07-24 - full corpus audit + remediation

Ran a full audit of all 63 docs (49 narratives + 14 catalogs, ~17.8k lines) + tooling:
deterministic mechanical/policy pass (lead) + 7 parallel per-cluster IL-verification
reviews (`workspace/outputs/audit/cluster-*.md`; synthesis in
`workspace/outputs/re-audit-full.md`). ~400 load-bearing claims spot-verified
CONFIRMED against the shipped DLL. Mechanical/policy: CLEAN (no IL/DLL tracked,
gitignore correct, no over-quoting, full INDEX registration, 0 broken links/dashes/
artifacts, 158 balanced diagrams). Census numbers reconcile (4401 top-level vs 7413
all-types, both correct).

Findings found AND fixed (each independently re-verified against IL before edit):
- **CRITICAL x3:** (1) `protocol-packages.md` §4.2 `NetPackageWorldInfo` tail was
  `i32 len+byte[]`; real wire is `i32 count + count x {string,u32} + i64` (leading
  i32 is an entry count). (2) `dynamic-mesh.md` §4 documented DEAD code
  (`WriteRegion` version-160, no callers); live path is
  `DynamicMeshRegionDataStorage.SaveRegion` deflate-compressed, no version tag,
  rewrote §4. (3) `items.md` §2 ItemValue Stats entry dropped the leading `byte`
  PassiveEffects type (3 fields/entry, not 2), and i16 semantics corrected.
- **MAJOR x11:** buffs.md net-sync direction inverted (AddBuffNetwork is send-side,
  ProcessPackage re-broadcasts); console permission is `ConnectionManager.
  ServerConsoleCommand -> AdminTools.CommandAllowedFor`, not `executeCommand`
  (telnet/stdin bypass); console 186->187 (+`exportprefab`, static CommandName);
  server-lifecycle EAC integrity "gate" is client-only gmUpdate UI (not a dedicated
  boot gate); mod-loading InitModCode is a separate 2nd pass in ModManager.LoadMods
  (LoadPatchStuff runs from GameManager.Awake); items ItemAction 41->38;
  sequence-requirements 43->37 concrete (5 rows were `Quests.Requirements.*`);
  combat EnumDamageSource only External/Internal; full-surface "every codepath
  narrated" softened to subsystem+leaf coverage; frame-entries 242->244 (2 nested).
- **MINOR (~12):** 193 wire-package nuance (189 registered + name-prefixed helpers);
  spawning bands attributed to screamer path only (scouts 0/8/10); vehicles
  EntityVehicle/EntityDriveable subtype inversion + `SpawnFollowingDronesForPLayer`
  casing; webserver `webpermission`/`invalidatecaches` names; managers
  EntityAsyncManager is phase F; re-methodology NetProtocolCensus cwd + AGENTS.md
  `tools/bin/Census.exe`; blocks `~131` top-level Block* count.

Propagated the two wire corrections (WorldInfo, ItemValue) + the dynamic-mesh live
path to `../zdtd/docs/RE_GAP_CLOSURE.md` §2 so the clone matches. Verification
state: **verified** (every fix traces to a cited IL command on the stable V3.0.1
dedicated DLL). Post-fix corpus health: 0 dashes/artifacts/broken-links, 158
balanced diagrams. Nothing committed. Next: optional remaining MINOR table-
completeness (webserver REST/handler tables) on request.

## 2026-07-24 (cont.) - completeness-gap closure

Closed every completeness gap surfaced by the full audit, each verified against the
stable V3.0.1 DLL:

- **webserver.md §3 REST API table** was materially incomplete (sampled, not
  enumerated). Rebuilt from the full `Webserver.WebAPI.APIs.*` type list: ServerState
  now `ServerStats/ServerInfo/GamePrefs/GameStats/SandboxSettings` (with
  `KeyValueListAbs` marked as the abstract base, not an endpoint); WorldState now
  `Player/Animal/Bloodmoon/Hostile`; GameData now `Item/Mods/EntityClass`; added the
  top-level `Command/LogApi/OpenAPI`.
- **webserver.md §1 handler table** rebuilt from `Web.RegisterDefaultHandlers`
  (IL=60) in registration order: added the two `RewriteHandler`s (`/`->`/files/`,
  `/app`->`/files/index.html`) and `UserStatusHandler` (`/userstatus`), and corrected
  the static mount to `StaticHandler /files/` (DirectAccess+SimpleCache). Flowchart
  updated to match.
- **webserver.md §6** completed to all 5 base-game web console commands (added
  `createwebuser`, `openiddebug`); fixed the console-commands.md §4 note that wrongly
  called the web commands "mod-added" (they ship in base Assembly-CSharp, in the 187).
- **coverage.md** "189 in live id-map" reframed honestly: 194 name-prefixed types is
  the verifiable static census; ~189 registered wire packages; the exact 189 is a
  runtime observation, not reproducible from static IL.
- **residuals.md** classified the reachable-but-unnarrated code the audit flagged:
  added the Discord GameSDK integration (`DiscordManager`, 140 methods, client social
  feature, not a dedicated codepath) and server-side support/utility code
  (`Configuration.*`/`StringParsers`/`TEFeatureAbs`, enumeration-level). Fixed a
  dangling empty table row in the §1 table.
- **protocol-packages.md §4.3** `NetPackageWorldInitInfo` was "partially annotated";
  completed from write IL=57/read IL=58: eventPrefabs (i32 count + `PrefabInstance.
  Serializable.Write` entries), wallVolumes (i32 count + {i32, `WallVolume.Write`}
  entries); removed the phantom trailing `dataLength`; noted the empty-body request
  form.
- **items.md** stale "MinEvent own doc pending" -> links to the now-existing
  minevents.md; fixed an awkward doubled parenthetical.
- Confirmed `pirs`'s `tbd` description is the game's own `getDescription` text (a
  faithful mirror, not our gap).

Post-fix health: 0 dashes/broken-links/dangling-rows/odd-fences, 158 diagrams, and
**zero remaining deliberate-incompleteness markers** across docs/. Verification:
verified (IL-cited). Nothing committed.

## 2026-07-24 (cont.) - wire-body long tail closed (full per-package catalog)

Closed the one honestly-open area from the audit: exhaustive per-package wire bodies.
Rather than hand-reverse 145 undocumented `write()` bodies (slow, error-prone), built
an extractor and generated a complete catalog:

- **New tool `tools/src/WireBodies.cs`** (`bin/WireBodies.exe`): walks every
  `NetPackage*` `write()` IL and emits the ordered wire field/type sequence (each
  `BinaryWriter.Write(T)` and nested `.Write(writer)`), tags list-count rows, flags
  loop/conditional bodies, and transitively expands the nested serializers packages
  delegate to. Handles lowercase `write`/`WriteNetwork` nested serializers and skips
  the base-package handle chain. Built clean under mcs 6.12.
- **New committed catalog `docs/inventories/netpackage-bodies.md`**: 183 package
  bodies + 60 nested serializers (EntityCreationData, EntityNetworkStats, Bag,
  ItemStack, EntityStats, PlayerProfile, TraderData, ...). Validated against
  hand-reversed bodies: WorldInfo, Chat, EntityRotation, PartyData, ItemStack all
  match exactly. The 6 zero-field packages confirmed genuinely empty (IL=4, handle
  only). Transformative metadata only (field order + types, no raw IL).
- **EntityCreationData class-conditional tail (the headline complex body) fully
  extracted**: 56 fields incl. the falling-block / EntityAlive-common / player /
  generic-blob / trader / sleeper branches. Documented the branch groups in
  `protocol-packages.md` §5.1 (was "partially decoded").
- **Wired in**: registered in INDEX; referenced from protocol-packages.md (top +
  §5.1), netpackages.md, residuals.md (body-catalog residual now **Closed**);
  documented the tool in re-methodology.md §4 and tools/README.md §1.
- Fixed a stray INDEX cross-ref ("43 requirements" -> "37 concrete") left over from
  the sequence-requirements audit fix.

Extractor limits stated honestly in the catalog header: it gives the flat backbone,
not which optional flag gates which section (loop/conditional framing needs the
per-package narrative). Post-work health: 0 dashes/broken-links/odd-fences, INDEX
registration complete, 243 catalog sections all with a table or empty-note.
Verification: verified (auto-extracted from stable V3.0.1 DLL; spot-checked vs
hand-reversed bodies). Nothing committed.

## 2026-07-24 (cont.) - preserve work + coverage tool + zdtd item-drop

Two-part follow-through on the corpus:

**Preserved in git** on branch `re-corpus-audit-tooling`, 3 commits (140 files,
no game IL, human author, no AI attribution, no em dashes): scope/restructure;
the RE documentation corpus (new narratives + audit corrections + completeness +
the two auto-generated catalogs); the RE tooling. Hardened `tools/.gitignore` so
the ~46k raw IL dump files under `tools/` (BiomeWeather/Weather*/SkyManager/...)
can never be committed. `workspace/` left untracked (local lab notebook).

**New `tools/src/Coverage`** (answering "programmatic coverage report?"): runs
call-graph reachability from the dedicated entry points, splits reached types into
game vs third-party/BCL, and cross-references game types against docs name-mentions.
Headline: 28,374 reached methods; 2,709 reached game types; 1,301 (48%) name-
mentioned (an upper bound). Backs `docs/inventories/coverage-report.md`; the top
undocumented-reached list is dominated by client UI (XUi/NGUI), correctly out of
scope.

**zdtd clone gap implemented** (item-drop entity spawn) after a cross-check that
turned up a real doc bug: `EntityCreationData.write` was documented with
`belongsPlayerId`/`clientEntityId`/`itemStack` as unconditional header fields, but
the IL shows they are the **itemClass branch only** (entity_class == hash("item")).
Rewrote `protocol-packages.md` §5.1 into the correct 3-section structure (header /
entityClass switch / networkWrite tail), verified branch-by-branch against
`EntityCreationData.write` IL. The switch also covers fallingBlock(s)/fallingTree
(block arrays) and playerMale/Female (holdingItem/profile); a zombie writes an empty
middle (so zdtd's existing zombie path was correct all along). Implemented the
itemClass branch in `zdtd/src/wire/stock_entity.zig` (`item_drop` SpawnOpts) with a
byte-offset round-trip test (verified via break-and-revert that it executes; the
full `zig build test` suite is green). Updated `zdtd/docs/RE_GAP_CLOSURE.md`.
Verification: verified (IL-cited; zdtd test passing).

## 2026-07-24 (cont.) - document undocumented dedicated subsystems (coverage 48% -> 52%)

User: "document all undocumented things." Scoped honestly: of 1,408 reached-but-
undocumented game types, ~1,330 are out of the repo's bar (client UI/NGUI, Discord
GameSDK, 3rd-party, data-structure generics, creative tools, render/audio). The
genuinely dedicated-relevant surface was ~80 types in ~8 subsystems. Fanned out 8
parallel researcher agents, each reversing its cluster from IL and writing a doc:

- **save-persistence.md** - SaveDataManagedPath slot/type/path model + SaveInfoProvider;
  key finding: a dedicated server always runs the System.IO `SaveDataManager_Placeholder`
  (management never activates without a console SaveGameProvider).
- **chunk-providers.md** - ChunkProviderAbstract + concretes (dedicated = GenerateWorldFromRaw
  id 4) + the two-layer decoration system; flagged ChunkBlockLayerLegacy as dead code.
- **inventories/te-features.md** - the 11 concrete TEFeatureAbs leaves (Storage, Lockable,
  Door, LandClaim, Signable, ...) with their serialized state.
- **raycast-pathing.md** - RaycastPathing + steering; junk-drone-exclusive, and the
  FloodFillEntityPathGenerator is debug-only (`jd debugrecon`); production drones use the
  A* handoff + raycast waypoint validation.
- **block-shapes.md** - BlockShape rotation model (4-band + 24-orientation) + the full
  BlockTrigger firing chain (client -> NetPackageBlockTrigger -> TriggerManager).
- **sandbox-options.md** - 152 typed sandbox options + the sandbox-code string codec +
  the StartAsServer fan-out into 119 static gameplay fields.
- **server-browser-prefabs.md** - GameServerInfo advertisement (TCP/Steam/EOS/LAN) +
  prefab-instance persistence; PrefabInstanceClientManager is server-side despite its name.
- **inventories/challenge-objectives.md** - 28 ChallengeObjective leaves; client-tracked
  (server persists the journal blob + runs the reward GameEvent).

All 8 registered in INDEX, IL-verified by the agents, health-clean (single H1, 0 dashes,
0 broken links, 0 tool artifacts). Coverage re-run: 1,301 -> 1,425 documented game types
(48% -> 52%), 1,284 still undocumented (the remainder is dominated by client UI / 3rd-party,
i.e. out-of-scope). Extended tools/src/Coverage to emit a full gap sidecar (git-ignored).
Verification: verified (agents cite IL commands; coverage reproducible).

## 2026-07-24 (cont.) - drive dedicated coverage to 100% accounted-for

User: "DO NOT STOP UNTIL YOU COVER 100%." Interpreted honestly: every reached game
type must be either narrated (a subsystem doc) or explicitly classified (out-of-scope),
so nothing is silently dropped. Result: **2703 reached game types, 100% accounted for
(0 unaccounted)** - 1747 (64%) narrated, 956 classified out-of-scope.

New docs (fan-out, IL-verified, with honest reclassification):
- inventories/sequence-actions.md (123 GameEvent.SequenceAction leaves)
- signs.md (writable/drawing sign system + moderation)
- map-objects.md (MapObject + NavObject marker registries; client-derived)
- npc-dialog.md (trader/NPC dialog tree + quest-data records)
- dedicated-misc-systems.md (19 small dedicated systems; WireManager etc. reclassified client)
- dedicated-leftovers.md (final tail; AuthAndLoginManager exposed as DiscordManager
  nested Social-SDK sign-in, NOT join auth, both dedicated triggers early-out)
- inventories/dedicated-leaves.md (88 small dedicated leaf types attributed to owners)
- out-of-scope-surface.md (956 reached-but-out-of-scope types classified by category:
  UI/render/audio/input/twitch/discord/platform/services/editor/3rd-party/util)

Coverage tool hardened along the way (all real methodology bugs):
- split narrated vs classified vs accounted-for (keeps the depth metric honest)
- excluded the tool's OWN coverage-report.md from the scan (was a feedback loop)
- normalized generic-arity backtick names (List`1 -> List) for matching
- excluded obfuscated #-named compiler types from the base

Honest scoping throughout: "1408 undocumented" was ~1330 out-of-scope (client UI,
Discord GameSDK, 3rd-party, generics, render/audio); the genuinely dedicated surface
was documented, the rest explicitly classified. Every reached dedicated codepath is
now narrated; the boundary of what the server does NOT run is enumerated. Corpus: 80
docs. Health: 0 dashes/broken-links/odd-fences, INDEX complete. Verification: verified
(agents cite IL; coverage reproducible and now stable at 100% accounted-for).

## 2026-07-24 (cont.) - promote dedicated leaves to a full per-leaf reference

Turned inventories/dedicated-leaves.md from a bare name index into a real per-leaf
catalog (parity with the other leaf catalogs): each of the 88 leaves now shows its
IL-derived base class + behavioral method fingerprint (largest declared bodies) +
role, grouped by owning subsystem. Added tools/src/LeafInfo (base + fingerprint
extractor for a list of type names). Coverage unchanged (still 100% accounted); this
is a depth promotion, not a metric change. Health clean.

## 2026-07-24 (cont.) - deepen substantive leaf groups into prose

Took the substantive dedicated-leaf groups from fingerprint rows to full prose in
their owning docs (5 parallel agents, IL-verified):
- entity-ai.md + uai.md: AIFocus* (bandit-only), EAI latch/sorter (live), and the
  6 UAIConsideration* scorers (live code but dormant in stock - no entity uses AIPackages)
- loot-economy.md: 5 LootEntryRequirement* server loot gates + TraderStageTemplate*
  (server-loaded but client-UI evaluated)
- items.md: ItemActionData* runtime state (Vomit=AI spit, DynamicMelee=swing machine,
  ReplaceBlock=server BlockChangeInfo), ItemClassArmor, ItemId, ItemWorldData
- spawning.md + world-generation.md: spawn config + prefab data; flagged GorePrefab/
  PrefabGroupEntry/PrefabGameObject/EventPrefabsClient as client-only
- quests-challenges.md + combat-damage.md: quest criteria/rewards (QuestCriteriaPOIWithinDistance
  is DEAD, hardcoded false) + combat leaves (BodyParts/ApplyExplosionForce client-only)

Folded the IL-verified roles back into inventories/dedicated-leaves.md (real role per
leaf, client-only rows marked). Added tools/src/LeafInfo (base+fingerprint extractor).
Coverage steady at 100% accounted; health clean. The trivial-variant groups
(BlockPlacement* etc.) stay at fingerprint depth by design.

## 2026-07-24 (cont.) - second audit: the session's own new docs

The 16 docs + 9 modified docs written this session had never been audited (the
earlier audit covered only the pre-existing corpus). Ran the same 6-cluster
adversarial pass over them. Found and fixed **3 CRITICAL + 8 MAJOR + 13 MINOR**;
~250 load-bearing claims re-confirmed. Reports: workspace/outputs/audit2/.

CRITICAL (all independently re-verified by the lead before fixing):
- **protocol-packages.md 5.1 (my own error).** The EntityCreationData convergence
  tail was wrong three ways: `isSleeperPassive` listed unconditional (it is written
  only when `isSleeper`, brfalse at IL_03B2); trailing `belongsPlayerId` placed
  inside the networkWrite block (it is junkDrone-only and sits AFTER that guard);
  and `orderState:i32` omitted entirely. A clone would desync on nearly every
  EntitySpawn. Note: I had this right in analysis earlier in the session and still
  wrote it wrong - the audit is what caught it. zdtd's implementation was correct.
- **chunk-providers.md:** DecoObject.Write omitted `realYPos:f32`; real
  decoration.7dt record is packedPos:u64, realYPos:f32, rawData:u32, state:u8.
- **dedicated-misc-systems.md:** "nothing server-side reads WorldStats" is false;
  TotalVertices feeds PrefabData.DensityScore, read by RWG prefab placement
  (PrefabManager.GetPrefabWithDistrict, StreetTile.SpawnMarkerPartsAndPrefabs).
  Promoted from the out-of-scope list to a real section.

MAJOR: NavObject RequirementTypes 9 -> all 14 members; PrefabInsideDataFile `.ins`
index is x + y*size.x + z*size.x*size.y (doc had y/z swapped); getsandboxoptions bool
is a show-all flag not log routing; ChunkProvider Init yields base Init FIRST;
GenerateFlat deletes only decoration.7dt; CompanionGroup Add/Remove have zero call
sites (unpopulated stub, was written up as live server state);
BuffEntityUINotification IS constructed server-side (inert, not never-executed);
sequence-actions closure is 137 not 132 (missing the XML-wired DecisionIf/LoopFor/
LoopWhile control-flow verbs, in sibling namespaces).

MINOR (13): "channel 192" was wrong in 3 docs (192 is SendPackage's `_range` arg;
these packages have no get_Channel override so they ride channel 0) - I introduced
that one earlier this session too; challenge base not IL-abstract; quests-challenges
29 -> 28 + intermediate; BlockShapeNew.Rotate wraps not clamps; IsParentOf IL=6;
BiomeBlockDecoration rotation is +20 rebase-at-24; sandbox GamePrefs mirror list;
StartAsClient clears clientPrefabs; EAIBlockingTargetTask also at AITarget-3; plus
map-objects/npc-dialog caller and package-effect corrections.

**Tooling defect found and fixed.** `FindCallers.exe` - the tool every
server-vs-client claim leaned on - **ignored its method argument entirely**
(substring-matched only the type name against callee signatures, so it matched calls
where the type was just a parameter) and was blind to field access. It had no source
in tools/src (orphaned binary). Verified empirically, quarantined it, and wrote
`tools/src/Xref.cs`: exact call OR field cross-reference, attributing hits inside
lambda/iterator closures to the outermost owner type. Validated: it recovers all 8
DensityScore field sites the old tool missed. Documented both failure modes in
re-methodology.md 8b with the rule that a negative ("no server callers") claim needs
the stronger tool.

Health after fixes: 0 broken links / dashes / odd fences, INDEX complete, coverage
steady at 100% accounted, zdtd tests still green.

## 2026-07-24 (cont.) - re-verify negative claims with exact xref; 48 promotions

Closed the caveat left by the FindCallers defect: every "client-only" / "dead code"
/ "no server callers" claim in the corpus rested on a tool that ignored its method
argument and could not see field access.

Built `tools/src/RefScan` (batch reverse-reference scan: one assembly pass over a
list of type names, every referencing site attributed to its outermost owner) and
re-verified in two sweeps:

1. **The 26 explicit negative claims in the narratives.** Almost all held. Two were
   imprecise and are fixed:
   - `SignCanvas` was listed flatly in the "client-only render pipeline", but its
     nested `SignCanvas.CanvasState.Read/Write` is called from the **server**
     `TEFeatureCanvas` persistence (signs.md's own 6 already documented that, so the
     doc contradicted itself). Now split: MonoBehaviour/decal rendering is client,
     CanvasState is server-persisted.
   - `EventPrefabsClient` marked "client-only" though `World.LoadWorld` constructs it
     on both sides; only its ToClient handlers populate it. Reworded to
     "client-effect only (allocated server-side)".

2. **The 948 types in out-of-scope-surface.md**, which had been classified by a
   **name heuristic** and never by callers. RefScan found 53 with server-only
   referrers; after excluding the legitimate cases (server code referencing a UI
   window or a generic collection), **48 were genuinely misclassified** and are now
   promoted into inventories/dedicated-leaves.md, grouped by owning subsystem with
   their server referrers as the evidence column. The name lies more than expected:
   `ClientAmmoData` is turret state on a server tile entity, `StreamReadSizeMarker`
   is wire-framing infrastructure, `ClientLobbyManager` sits in the server authorizer
   chain, `ClientTriggerData` belongs to `TileEntityPoweredTrigger`.

Coverage moves the honest way: **narrated 1747 -> 1799 (64% -> 66%)**, classified
falls to 915, still 100% accounted / 0 unaccounted. Documented the lesson in
re-methodology 8b: do not classify by name, classify by referrer; and a negative
claim needs the stronger tool. Health clean.

## 2026-07-24 (cont.) - sweep the older docs' negative claims (clean result)

Extended the referrer verification to the whole corpus with a much broader claim
net (older docs phrase these differently: "no-op on dedicated", "sole caller",
"vestigial", "inert", "render-side", "editor-only", plus the exclusivity forms).
48 claim/type pairs across 19 docs, 29 of them not covered by the earlier sweep.

**Result: no substantive errors in the older docs.** Breakdown:
- **23 dead-code claims independently confirmed**: RefScan finds zero external
  referrers for each (`ChunkProviderParameter`, `SaveDataManager_Minimal`,
  `EntityVBlimp`, `TriggerEffects`, the unused MinEvent/GameEvent action verbs,
  the unused `EnumMapObjectType` values, ...).
- **18 confirmed by client referrers** (the claim and the reference set agree).
- **7 flagged, all 7 false positives** on inspection: `EntitySpawner` at
  map-objects.md is the *enum value* `EnumMapObjectType.EntitySpawner`, not the
  spawner class; `NetPackageWorldInfo`'s server referrers are the *send* side while
  the doc claims only the *receiver* (`worldInfoCo`) is client; the rest
  (`ApplyExplosionForce`, `ChunkProviderDummy`, `EventPrefabsClient`,
  `StunBeamWeapon`, `AttackHitInfo`) were already accurately nuanced.
- **3 exclusivity claims verified exactly** with Xref: `ApplyExplosionForce.Explode`
  has exactly one call site (`GameManager.ExplosionClient`), `BlockTracker`'s only
  referrer is `BlockLimitTracker`, `SpawnEntry.HandleUpdate` is its only method.

One ambiguity tightened: combat-damage.md's changelog said "flagging the client-only
pieces" after listing four leaves, but only two of them are client-only; now named
explicitly so the line cannot be misread.

Contrast with the earlier out-of-scope sweep (48 misclassifications) is the useful
signal: **hand-written narrative claims held up; the machine-generated name-based
classification did not.** Coverage steady at 100% accounted, health clean.

## 2026-07-24 (cont.) - zdtd: remaining EntityCreationData branches

Experimental refresh is **blocked**: `steamcmd` is not installed and a fresh
`latest_experimental` pull needs Steam credentials (a user decision; installing
steamcmd would also pollute the host). experimental-delta.md stays pinned and is
already honestly caveated as provisional. Did the actionable item instead.

Implemented the ECD branches that protocol-packages.md 5.1 specifies but zdtd
lacked, all IL-verified:
- **player** (playerMale/playerFemale): holdingItem, teamNumber:u8,
  entityName/skinTexture:string, playerProfile(bool + PlayerProfile **v5**:
  i32 version, archetype, isMale, raceName, variantNumber:byte, hair/hairColor/
  mustache/chops/beard/eyeColor strings)
- **fallingTree**: blockPos (StreamUtils Vector3i = 3x i32) + fallTreeDir
  (Vector3 = 3x f32), both layouts verified rather than assumed
- **junk-drone tail**: belongsPlayerId + orderState, correctly placed AFTER the
  networkWrite block (the guard jumps to the same test, ECD IL_033F -> IL_03C5)

Every class-name string came from the `EntityClass.Init` ldstr literals
(`item`, `fallingBlock`, `fallingBlocks`, `fallingTree`, `playerMale`,
`playerFemale`, `entityJunkDrone`) rather than being guessed; `fallingTree` was a
guess that the IL then confirmed.

**Latent bug found and closed:** `buildEntitySpawnStock` accepted any
`entity_class` but only emitted the zombie/item bodies, so passing a player or
falling class silently produced a body missing its middle section, corrupt on the
wire. Unimplemented classes now return an error; a failed send beats a desync.
9 tests, each verified to actually execute by break-and-revert. zdtd docs
(MISSING_FEATURES, STATUS, PACKAGES, RE_GAP_CLOSURE) updated; suite green.

## 2026-07-24 (cont.) - zdtd: fallingBlock/fallingBlocks branches (ECD complete)

Closed the last two EntityCreationData class branches, both read from the write IL
rather than guessed:
- **fallingBlock** (single): `blockValues[0].rawData:u32` then `textureFullArrays[0]`.
  `TextureFullArray.Write` turns out to emit **exactly one i64** (its loop bound is
  the literal 1, and `Read` takes a count but stores only index 0).
- **fallingBlocks** (multi): `count:i32`, then `count x rawData:u32`, then
  `count x Vector3i`, then `count x i64`.

**Shared-count trap, now documented in protocol-packages.md 5.1:** the multi-block
branch writes only ONE length even though three arrays follow, and
`EntityCreationData.read` allocates `blockValues`, `blockPositions` and
`textureFullArrays` from that same value without reading a second `Int32`. A clone
that emits a length before the positions or textures desyncs. zdtd's API therefore
takes a single slice of blocks and derives the count, making the invariant
unrepresentable-if-violated.

EntityCreationData is now complete in the clone: all six class branches (zombie/NPC
empty middle, itemClass, fallingBlock, fallingBlocks, fallingTree, player) plus the
junk-drone tail. 11 tests, each proven to execute by break-and-revert; suite green.
zdtd docs updated (MISSING_FEATURES, PACKAGES, RE_GAP_CLOSURE now mark the package
complete).

## 2026-07-24 (cont.) - run the repo's own tests; fix a regeneration trap

Ran `tools/tests/` for the first time this session (having added 6 tools and ~20
docs without doing so). Both gates pass, but the regen test surfaced a real
**reproducibility trap**:

- `test_re_dump_regen.py` printed "MB update methods: **242**" while the audited
  `inventories/frame-entries.md` says **244**. Cause: `legacy/DumpFrameEntries`
  enumerated `MainModule.Types` only, so it never saw the two nested frame entries
  (`PerformanceProfiler/FrameTimeCapture`, `XUiC_ItemActionEntry/TimedAction`) that
  the audit added by hand. Regenerating the doc would have **silently reverted the
  fix**. Patched the dumper to recurse nested types and qualify their names; it now
  emits 244 and a normalized diff of (type, method, IL) tuples against the committed
  doc is **identical**.

Audited the other generated docs for the same doc-vs-generator drift:
- `netpackage-bodies.md` (WireBodies) and `coverage-report.md` (Coverage): genuinely
  push-button, no drift.
- `console-command-list.md`: already carries an honest caveat that an ldstr-only
  extractor misses `exportprefab`.
- `dedicated-leaves.md` and `out-of-scope-surface.md`: these were generated then
  **hand-corrected** (the 48 referrer-verified promotions). A naive regeneration
  would undo that, so both now state their maintenance model explicitly rather than
  implying they are regenerable.

Health clean; coverage unchanged at 100% accounted.

## 2026-07-26 - fix all docs against the review findings

Acted on the `/review` output: my own review (1 critical after upgrade, 3 major,
4 minor) plus the independent adversarial reviewer (2 critical, 3 major, 5 minor).

**C1/C2 - the coverage metric measured a tool artifact. Rebuilt `tools/src/Coverage`:**
- **Interface-dispatch devirtualization added.** The override map only walked
  `BaseType`, so families dispatching through an interface were invisible: exactly
  1 of the 187 documented console commands was in the base. Now **178** are, and the
  base grew 2703 -> **3775** game types.
- **Narration now requires a backticked mention**, killing false positives where real
  types named `Field`/`Entry`/`Data` were credited because markdown table headers
  contain those words (0 deliberate references to any of them).
- **Generated catalogs no longer count as narration.** `inventories/` is now its own
  "catalogued only" tier; previously ~536 identifiers appearing solely in generated
  tables scored as "narrated in a subsystem doc".
- **The summed headline is gone.** Four tiers are reported separately (narrated 1120 /
  catalogued 548 / classified 913 / **unaccounted 1193**) with an explicit "this is not
  a coverage metric" preamble documenting both the over-approximation (498 XUi types
  in the base) and the under-approximation (reflection still invisible).
- Honest result: the corpus went from claiming "100% accounted, 66% narrated" to
  showing **29% narrated with 1193 unaccounted**. The old number is withdrawn in
  full-surface.md and coverage.md.

**Reviewer M1 - the out-of-scope bucket was never referrer-verified.** It named
`ClientPowerData` as a counter-example; confirmed (14 `TileEntityPowerSource`
referrers incl. `read`/`write`). Re-swept all 905 classified types and found my
earlier promotion rule was itself flawed: it required **zero** client referrers, so a
type that is overwhelmingly server-side but touched once by a UI window stayed
misclassified. Rule changed to **server-dominance**; 19 gameplay types promoted. Also
corrected the infra category, which implied "never runs on a server" when many of
those types *are* called by server code and are out of scope for being infrastructure
rather than gameplay.

**Other fixes:** stale `EntityCreationData` residual row in coverage.md; 60 -> 61
nested serializers in netpackages.md/INDEX; ItemStack predicate stated as the raw-field
`brfalse` rather than "count > 0"; dedicated-leaves headline count vs row count;
regeneration cwd convention aligned to repo-root.

**Policy (reviewer m3):** 46,606 raw game-IL files were sitting under `tools/`,
ignored by an enumerated name list. Moved them under the wholesale-ignored `il/`
(not deleted) and replaced the name list with a policy statement plus catch-all, so a
future dump landing in `tools/` cannot be committed by omission.

**Reproducibility (my M3):** the hand-corrections to the out-of-scope classification
are now a committed tool input, `tools/data/promoted-types.txt` (62 names), so a
regeneration can honour them instead of silently reverting them.

**Evidence weighting (my M2):** `coverage.md` now carries a per-doc **audit status**
table (audited pass 1 / pass 2 / not independently audited / generated), because the
second audit found 3 critical + 8 major in already-careful prose.

Verification: 0 broken links / dashes / odd fences, INDEX complete, both gates pass,
external `zdtd` consumer still green.

## 2026-07-26 (cont.) - finish the base definition; re-triage

**(1) Base definition finished.** The previous fix left the same bug class present:
87 vendored third-party types (1,259 methods) were still counted as game code.
Added `LiteNetLib` (53 types, the UDP transport already listed as a residual),
`Antlr` (21) and `NCalc` (13) to the library exclusion, alongside System/UnityEngine.

**Console commands now visible to the metric.** The catalog listed command *names*
(`admin`) while the metric matches *type* names (`ConsoleCmdAdmin`), so all 187 read
as undocumented. New tool `tools/src/CmdMap` emits `command -> type` for every
concrete `ConsoleCmdAbstract` subclass, following the static-field name form so
`exportprefab` is not missed; the catalog gained a **Type** column (187/187 mapped,
the last three being aliases: `as` -> AdminSpeedConsoleCmd, `zd`/`zz` -> the
DynamicMesh console cmds).

Net effect on the honest numbers: base 3775 -> **3688**, catalogued 548 -> **734**,
unaccounted 1193 -> **934**. Narrated is unchanged at 1120 (**30%**).

**(2) Re-triage of the remaining 934.** Sampled and bucketed: 522 "other", 142
twitch/discord/platform, 117 client UI, 53 audio, 49 generic infra, 41 render, 10
editor. Inspecting the "other" bucket shows it is dominated by **client, editor and
vendored code that lives in the `<global>` namespace**, where namespace-based
filtering cannot reach it (`PrefabEditModeManager`, `CursorControllerAbs`,
`NCalcLexer`, `BindingNcalcFunctions`, `GameSenseManager`, `DistantTerrain`,
`SaveDataMergedPlatformSaveGameIOProvider`). This triage note is emitted by the
generator itself so it survives regeneration, and it states plainly that the number
is **classification debt, not undocumented server systems**.

Verification: 0 broken links / dashes / odd fences, both gates pass, zdtd green.

## 2026-07-26 (cont.) - whole-system visual map

Added `docs/architecture-map.md`: the top-level view the corpus lacked. It had 176
per-subsystem diagrams but no single picture of how the pieces connect, so a reader
had to assemble the system mentally from 60 docs.

Seven diagrams, all drawn from existing IL-derived narratives (nothing new asserted):
five-layer system map (transport / wire / sim / persistence / external), boot
lifecycle, the gmUpdate A-J frame with the dedicated skip over phase C marked, the
sim core fan-out, the join conversation as a sequence, the persistence fan-out, and
a subsystem-ownership index. Clickable nodes route into the owning doc.

It also carries the corpus's hard-won corrections rather than an idealised picture:
no managed EAC boot gate, crafting is split authority, client inventory is
client-authoritative, and the dynamic-mesh writer people expect is dead code.
Registered as entry 0 in INDEX ("start here").

Also fixed during backup verification: both `git bundle` calls had run from the zdtd
directory (a stray `cd` earlier in the same shell), so the research repo had **no
backup** despite the command reporting success. Recreated from the correct cwd and
verified by listing refs (main + re-corpus-audit-tooling). Removed a stray 2.2 MB
`MethodList` dump written to a mistyped filename in the repo root.

## 2026-07-26 (cont.) - mermaid 8.6 compatibility fix

The architecture map failed to render in a viewer pinned to **mermaid 8.6** (reported
against the Wire sequence diagram). Root cause was newer-mermaid syntax throughout:

- `Note over S: authorizer chain; failure -> PlayerDenied ...` used a **semicolon**
  (a statement separator in mermaid 8.x) *and* a bare `->` inside note text (parsed
  as an arrow). This was the reported failure.
- `<-->` bidirectional edges (3 uses), `A & B --> C & D` multi-node edges (3 uses),
  and 10 `click` directives: all newer-mermaid features.
- Bare `->` inside three more labels (two stateDiagram transitions, one flowchart
  node) had the same arrow-parsing hazard as the note.

All rewritten to conservative syntax that parses on 8.6: explicit single edges,
no `&` fan-out, no `click`, and prose instead of arrows inside labels. Verified by
sweeping the extracted mermaid blocks for every risky construct (all now 0).

Published the map as a rendered artifact, rebuilt programmatically **from** the
fixed markdown (blocks extracted, HTML-escaped, injected) so the two cannot drift;
verified 7/7 diagrams byte-identical to the doc.

## 2026-07-26 - state-machine mapping + corpus-wide mermaid 8.6 sweep

**Objective:** "make sure all state machines are mapped and visualized", then finish
the 8.6 compatibility fix beyond the architecture map.

**State machines.** Inventoried every `stateDiagram` in the corpus and found one gap:
`raycast-pathing.md` named the drone state machine in prose with no diagram. Recovered
the real `EntityDrone/State` enum from IL (`Idle=0, Sentry=1, Follow=2, Heal=3,
Attack=4, Shutdown=5, NoClip=6, Teleport=7, None=8`) and established that
`SetState(State next, bool sync)` is the sole mutator (15 call sites), so the
transition set is closed rather than sampled. Added as §6b.

New tool `tools/src/StateMachines.cs` indexes every state diagram with its owning
doc + section + state count and emits `docs/inventories/state-machines.md`:
**74 state machines across 42 docs**, grouped into 6 clusters (Gameplay 27, Ops 15,
Entities 14, World 10, Frame 4, Wire 4). Registered in INDEX; overview added as
`architecture-map.md` §7b. Regeneration is byte-stable (verified: md5 unchanged).

**Mermaid 8.6 sweep beyond the map.** The earlier fix covered `architecture-map.md`
only. A corpus-wide scan of all 185 diagrams found 17 further `;` hits, which
triage split into two classes:

- *Legitimate, left untouched:* `;` inside `classDiagram` bodies (valid syntax,
  `sandbox-options.md`), `;` terminating HTML entities (`&lt;` etc.), `;` used as a
  deliberate flowchart statement separator, and `&` inside quoted labels.
- *Real breakages, fixed:* `;` inside **unquoted** label/note text in 11 lines
  (buffs, items, loot-economy x3, parties-factions x2, quests-challenges, webserver,
  world-generation) - the same class as the reported failure; three `A & B -->`
  fan-outs (server-browser-prefabs, signs, world-generation) rewritten as explicit
  single edges; and four labels in `npc-dialog.md` containing a literal `\n`
  (not valid in a mermaid label) converted to `<br/>`.

Discipline note: the earlier instinct was to mass-strip `->` from labels. The
evidence did not support it - dozens of diagrams carry `->` inside labels and render
fine, and the one reported failure carried a `;`. The semicolon was the breaker.
Scoped the edit to what the evidence justified.

**Verification:** corpus-wide risky-construct sweep over all 185 diagrams now
reports 0 hazards. Both repo gates green (`test_dedi_coverage_docs.py` OK, 11 docs /
8 dump sets / 8 tools; `test_re_dump_regen.py` OK, 244 MB update methods, matching
the audited count after the nested-type recursion patch). Doc health: 82 docs, 0 em
dashes, 0 odd fences, 0 docs missing from INDEX, 0 real broken links (the single
regex hit in `save-persistence.md:109` is a regex in backticks, not a link).
Also removed 16 empty leftover directories under `tools/` from the earlier IL move.

**Next:** experimental-delta refresh remains BLOCKED (needs `steamcmd` plus the
user's Steam credentials for a `latest_experimental` pull); `experimental-delta.md`
stays pinned/provisional. Push remains BLOCKED (no remote on either repo; creating
one is the user's call given the content). Local bundle backups at
`~/.cache/7dtd-backups/`.

## 2026-07-28 - close classification debt (unaccounted -> 0)

Continued the RE completeness push after the state-machine map.

**Coverage mention matcher fixed.** `tools/src/Coverage` only credited bare
`` `TypeName` `` tokens, so forms used throughout the corpus (`EAIManager.Update`,
`ChunkBlockLayer.Write`, `NetEntityDistributionEntry.updatePlayerList`) never
counted as narration. Expanded the regex to credit the leading identifier in
`` `Type.Member` `` / `` `Type::Member` `` / `` `Type/Nested` `` backtick forms.
Effect on the honest tiers: narrated **1120 -> 1248 (33%)**, catalogued
**734 -> 1029**, unaccounted **934 -> 731** before any new classification.

**Classification debt closed.** Remaining unaccounted types were triaged with
`tools/src/RefScan` (server vs client dominance) and split:

- **494** client/platform/vendored/infra types appended as a *supplementary*
  section in `docs/out-of-scope-surface.md` (base hand-curated lists left
  byte-stable; earlier in-place rewrite attempt corrupted arity markers and was
  reverted).
- **216** server-dominant / reflection-XML types leaf-catalogued under
  `docs/inventories/dedicated-leaves.md` ("Promoted unaccounted server surface"),
  fingerprinted with `tools/src/LeafInfo`.
- A handful of already-narrated bare mentions (`AIDirectorPlayerState`,
  `RegionFileRaw`, `WorldBlockTicker`, ...) backticked in their owning docs.

**Result (Coverage report):** game types 3688; narrated **1248 (33%)**;
catalogued 1029; classified 1411; **unaccounted 0**. Zero unaccounted means every
reached game type is narrated, catalogued, or classified - **not** that every
type has a full behavioral narrative. The four tiers remain separate; the old
"100% accounted" headline stays withdrawn.

Also updated the generator triage note and the stale numbers in `full-surface.md`.

**Verification:** `test_dedi_coverage_docs.py` OK; `test_re_dump_regen.py` OK
(244 MB update methods); 0 em dashes; INDEX complete.

**Still blocked:** experimental-delta refresh (steamcmd + credentials);
push (no remotes).

## 2026-07-28 - water sim pipeline narrative

Picked the highest-value remaining server surface after classification closed:
the jobified water simulation (only a one-table stub in `light-mesh-water.md`
plus a short apply-stage note in `dedicated-misc-systems.md`).

**IL pass (DumpMethod + Xref, V3.0.1 dedi):**
- Callers: `GameManager.gmUpdate` -> `WaterSimulationNative.Step` and
  `WaterEvaporationManager.UpdateEvaporation`; apply via
  `WaterSimulationApplyChanges.ThreadLoop` -> `ApplyChanges`.
- `WaterSimulationNative.Update` (IL=229): early exits (init/pause/net budget),
  then `IJob` PreProcess -> `IJobParallelFor` CalcFlows -> ApplyFlows ->
  `IJob` PostProcess, `JobHandle.Complete`, harvest `HasFlows` into
  `ChangesForChunk.Writer.RecordChange`.
- Flow rules in `ProcessFlows` (IL=265): solid deactivate, groundwater sides,
  `ProcessFlowBelow` / `ProcessOverfull` (const **19500**) / four
  `ProcessFlowSide` with cross-chunk `EnqueueFlow`.
- Mass model: `WaterValue` is `UInt16 mass`; percent uses 195 / 15600 / 15405;
  `GetStableMassBelow` = min(sum, 19500); flow-through when
  `Block.WaterFlowMask != 63`.
- Net: `HasNetWorkLimitBeenReached` compares `NetPackageMeasure.totalSent` to
  `networkMaxBytesPerSecond`; send path builds `NetPackageWaterSimChunkUpdate`
  for `clientsNearChunkBuffer`.

Expanded `docs/light-mesh-water.md` §4 with diagrams + method map; cross-linked
from `dedicated-misc-systems.md`. Coverage still **unaccounted=0** after regen.

**Verification:** dedi coverage gate OK; 0 em dashes; mermaid hazard scan clean
on new blocks.

## 2026-07-28 - region runtime path + AIDirector depth

Second depth round after water.

### Region / ticker (`save-region.md` §3)
- `RegionFileManager`: no `Update` call sites; save is task-driven from
  `cacheChunk` / world save into `DoSaveChunks` (IL=292).
- Load ladder in `GetChunkSync` (IL=178): live cache → pending snapshot →
  pending dirty chunk → save dir → load dir.
- Snapshot blob: magic bytes `ttc\0` (116,116,99,0) + `UInt32` version **47**
  + `Chunk.save`; writer path Deflate via `Noemax.GZip.DeflateOutputStream`.
- `RegionFileRaw.WriteData` re-confirms `sectorsStartOffset` **779**.
- `WorldBlockTicker.Tick` dual path: `tickScheduled` (cap 100/call) +
  `tickRandom` (`max(n/100,1)` chunks/frame, 1200-tick per-chunk gate).
- `WorldBlockTickerEntry` wire: u8x3 local pos, u16 blockId, u64 time, trailing
  u16 written and discarded on read.

### AIDirector (`aidirector.md`)
- `CreateComponents` order verified from IL (Marker, Player, WanderingHorde,
  AirDrop, ChunkEvent, BloodMoon) with cached fields.
- `AIDirectorPlayerState` fields + dead/inventory accessors; management ticks
  the state list that `FindTargets` (IL=459) reads.
- Chunk-event component: 5 s `CheckToSpawn`, per-chunk `AIDirectorChunkData`
  map, active spawns; chunk-event wire version 2.
- `AIDirectorData` noise dictionary; `AIHordeSpawner.Tick` radii 45..55.

Coverage after regen: narrated **1269 (34%)**, unaccounted **0**. Gates green.

## 2026-07-28 - lock contexts, async spawn queue, PrefabChunk

Third depth round.

- **ILockContext bags** in `dedicated-leftovers.md` §2.1: `EntityLockContext`
  (command + bag + firstTouch), `EntityTraderLockContext` (command + TraderData),
  `VendingMachineLockContext` (TraderData). Server `OnLockedServer` paths open
  loot/trader inventory and clone trader data; wire shapes from Write/Read IL.
- **EntityCreateHandle + NetEntityPackageQueue**: early entity-targeted packages
  queue (cap 10) until `OnCreateEntityRequestFinalized` drains via
  `ProcessPackagesForEntity`.
- **Prefab/PrefabChunk**: IChunk view over prefab templates, cached by chunk key.

Coverage: narrated **1273 (34%)**, unaccounted **0**.

## 2026-07-28 - config XML xpath patch pipeline + MapVisitor

Fourth depth round.

- Expanded `mod-loading.md` §5: `WorldStaticData.LoadAllXmlsCo` and
  `ModManager.LoadPatchStuff` callers; `XmlFile` load/xpath/serialize surface;
  `XmlPatcher.singlePatch` method registry; full `XmlPatchMethods` operation
  catalog (set/append/insert/remove/csv/conditional/include) with
  `@modfolder:` rewrite.
- Documented `MapVisitor` as console-only AABB chunk walk (`ConsoleCmdVisitMap`).

Coverage still unaccounted **0**.

## 2026-07-28 - connection transport threads + session crypto layout

Fifth depth round.

- Expanded `network.md` §4: `NetConnectionSteam` vs `NetConnectionSimple` reader/writer
  threads, queue types, 2 MiB streams, 4 KiB copy buffers.
- Documented transform order: send compress-then-encrypt; recv decrypt-then-decompress.
- Simple path framing (Int32 length + flags + UInt16) and double-buffer serialize lists.
- `AesEncryptAndMac` EncryptStream/DecryptStream layout (IV, AES, HMAC verify).
- Tightened `residuals.md` encryption row: session transform is managed; residual is
  RSA wrap / crypto providers below BCL.

Coverage: narrated **1280 (34%)**, unaccounted **0**.

## 2026-07-28 - WorldStaticData xmlsToLoad census + ConnectionManager.Update

Sixth depth round.

- New inventory `docs/inventories/xmlsToLoad.md`: **49** `XmlLoadInfo` rows from
  `WorldStaticData..cctor` (IL=871) with boot/S2C/reload/clientFile flags and
  load/cleanup/after/reload delegates. Counts: boot 7, S2C 42, reload 19, clientFile 1.
- `mod-loading.md` §5.5 points at the table; notes server-only rows
  (`gamestages`, `spawning`, `signs`) and after-hooks (materials atlases,
  item LateInit).
- `network.md` §1.1-1.3: `ConnectionManager.Update` order, bad-packet kick when
  `GetBadPacketCount >= 3` → `EKickReason.BadMTUPackets` (26), dual-channel
  `ProcessPackages` (disallow ToClient), `DisconnectClient` highlights.
- `protocol-packages.md` EKickReason notables gain BadMTUPackets=26.

Coverage: narrated **1281 (34%)**, unaccounted **0**.

## 2026-07-28 - config S2C ship path + authorizer Order re-verify

Seventh depth round.

- `mod-loading.md` §5.6: Deflate cache via `cacheSingleXml` (minified serialize +
  `DeflateOutputStream`), `SendXmlsToClient` from `RequestToEnterGame` (after
  localization packets), `NetPackageConfigFile` wire (ToClient, Compress=true,
  name + length-prefixed bytes or -1), client `ReceivedConfigFile` /
  `EClientFileState`.
- Re-verified all 19 authorizer `get_Order` literals from IL (incl. Steam 430/470);
  noted `Init` reflection + `SortedList` wiring in `platform-auth.md`.

Coverage still unaccounted **0**.

## 2026-07-28 - playerAllowed + RequestToEnterGame package sequence

Eighth depth round.

- `platform-auth.md`: full `playerAllowed` (IL=156) steps; dedicated empty
  identity tuples; `UpgradeToFullConnection` = `InitStreams(true)` +
  `allowCompression`; Accepted/Denied callbacks.
- `protocol.md`: post-login `RequestToEnterGame` ordered S2C batch (block check
  ManualKick=10, PPL cap 100 -> reason 31, IdMapping, localization, configs,
  WorldInfo, cluster, spawns, areas, GameStats); `PlayerLoginAnswer` write layout.
- `network.md`: `ProtocolManager` as thin INetworkServer/Client pump only.

Coverage still unaccounted **0**.

## 2026-07-28 - RequestToSpawnPlayer join path

Ninth depth round.

- `protocol.md`: full `RequestToSpawnPlayer` server path (IL=496): view-dim clamp,
  PDF load, entity id reuse/alloc, spawn position order (team-near / friend-near
  40..150 / SpawnPointList), CreateEntity, RespawnType 4 vs 5, PlayerId package,
  SpawnEntityInWorld, chunk observer, PPL broadcast, PlayerSpawning mod event.
  Documented that `PlayerSpawnedInWorld` is a **later** client package (IL=127),
  not called from RequestToSpawnPlayer. Added PlayerId and PlayerSpawnedInWorld
  wire bodies + RespawnType enum.
- `server-lifecycle.md`: state machine split EntityCreated -> IdSent -> Spawned.
- `spawning.md`: join-path bullet clarifying timing vs ModEvents payloads.

Coverage: narrated **1294 (35%)**; unaccounted **0**.

## 2026-07-28 - client chunk streaming pipeline

Tenth depth round.

- `world-chunks.md` section 4.0: `ChunkObserver` fields; `SendChunksToClients`
  remove/load/reload/map order; skip while `NeedsLightCalculation`; **3** first-load
  packages per observer per tick; `ResendChunksToClients` reload queue.
- `network.md` / `protocol.md` cross-links: join attaches observer; steady
  UpdateTick streams channel-1 compressed chunks.

Coverage: narrated **1295 (35%)**, unaccounted **0**.

## 2026-07-28 - DetermineChunksToLoad around-set algorithm

Eleventh depth round.

- `world-chunks.md` section 4.0.1: `gmUpdate` caller; unload budget **8**;
  hollow-square rings via `rectanglesAroundPlayers[0..14]`; per-observer
  `chunksAround` / `chunksToLoad` / `chunksToRemove` diffs; manager
  `m_All` / `m_Viewing` / `m_Collision` unions; out-of-range `RemoveChunk`.
- Corrected streaming diagram: DCL is **not** under `UpdateTick`.
- `loop.md` table points at section 4.0.1.

Coverage: narrated **1295 (35%)**, unaccounted **0**.

## 2026-07-28 - entity spawn, map tiles, chunk provide

Twelfth depth round (all three deferred leaves).

- `protocol-packages.md` section 3.3: `NetPackageMapChunks` wire (entityId, u16
  count, 256x u16 colors), invalid-size rewind, channel 1 compressed.
- `MapChunkDatabase.GetMapChunkPackagesToSend`: 17x17 window after map-middle
  update; ByRegion variant under lock.
- section 5.1.1: EntitySpawn envelope via EntityTargeted; async
  `EntityAsyncManager.StartCreateEntity`; clientEntityId remap branch.
- section 5.2: SpawnResponse client inventory ack (vehicle/drone/turret).
- `chunk-providers.md`: `GetNextChunkToProvide` snapshot under lock, ring-order
  miss, pop last requested, Int64.MaxValue sentinel; thread sleep 15/0.
- `world-chunks.md`: map producer pointer from SendChunksToClients.

Coverage: narrated **1299 (35%)**, unaccounted **0**.

## 2026-07-28 - NED interest, place-spawn, water wire, DM queue

Thirteenth depth round (all four deferred leaves).

- `network.md` 2.1: EncodePos (*32+0.5) / EncodeRot (*256/360); priority bands
  25/324/625 with 16384 view gate; `IntHashMap` entry store.
- `protocol-packages.md` 5.0: `RequestToSpawnEntity` + server create (falling-tree
  dedupe, backpack persist, SpawnEntityInWorld).
- 6.9/6.10: WaterSimChunkUpdate outer/inner payload; WaterSet rebroadcast+Apply.
- `light-mesh-water.md`, `spawning.md`, `entity-ai.md`, `chunk-providers.md`,
  `dynamic-mesh.md`: cross-links and GetNextChunkToLoad sentinel queue.

Coverage: narrated **1301 (35%)**, unaccounted **0**.

## 2026-07-28 - motion packages, PlayerData, path clamps, main.ttw

Fourteenth depth round (four leaves in one pass).

- `protocol-packages.md` 5.5: PosAndRot / Teleport / Rotation / RelPosAndRot /
  Velocity / AliveFlags wire and process; 5.6 PlayerData C2S SavePlayerData.
- `network.md`: decode notes (serverPos/32, rot*360/256).
- `entity-ai.md` 6.2-6.3: FindPath distSq 1225 and Y ±45 clamps; ASP coalesce;
  base PathFinderThread.FindPath no-op.
- `save-region.md` 1.1-1.2: main.ttw magic ttw\0; version gate; Load
  .bak / .ext.bak cascade; Save .bak pre-write.

Coverage: narrated **1302 (35%)**, unaccounted **0**.

## 2026-07-28 - PlayerDataFile, damage wire, TE package, weather blob

Fifteenth depth round (four leaves concurrent).

- `save-region.md` 1.3: PlayerDataFile `ttp\0` + version **59**, tmp/bak save,
  WriteNetwork = Write + PlayerMetaInfo; major Write sections.
- `protocol-packages.md` 6.11: NetPackageDamageEntity full field order (IL=172)
  + ProcessPackage apply entry; 6.12 NetPackageTileEntity handle/pos/u16 payload
  + server rebroadcast flags 192.
- `tile-entities-power.md` / `combat-damage.md`: cross-links.
- `weather-environment.md`: ReadWriteData IL=193 (v4, GamePrefs 60 gate, per-biome
  storm/params); Load buffer vs ApplyLoad.

Coverage: narrated **1303 (35%)**, unaccounted **0**.

## 2026-07-28 - inventory tx, power.dat, explosions, stat sync

Sixteenth depth round (four leaves concurrent).

- `protocol-packages.md` 6.13-6.16: InventoryTransaction wire + server apply;
  ExplosionInitiate/Client; EntityStatChanged / StatsBuff / PlayerStats.
- `items.md`: hash-validated TransactionRequestServer path.
- `tile-entities-power.md` 3.5: power.dat field-level tree codec + threaded save.
- `entity-stats.md` / `buffs.md`: network package pointers.
- `protocol.md` 6.6: explosion layout pointer.

Coverage: narrated **1309 (35%)**, unaccounted **0**.

## 2026-07-28 - chat/console/lock packages and region free-list

Seventeenth depth round (four residual leaves concurrent).

- `save-region.md`: RegionFileRaw.FindBestFreeSpace exact-fit then best-fit over
  usedSectors from offset 779; residual table closed.
- `dedicated-leftovers.md` 2.2: NetPackageLockRequest/Response wire;
  ForceUnlockByPlayer.
- `console-commands.md` section 3: ConsoleCmdServer/Client package bodies.
- `protocol-packages.md` 6.17: chat, console, lock, party re-verify,
  QuestEntitySpawn.
- `chat.md` / `parties-factions.md`: IL cross-links.

Coverage: narrated **1318 (35%)**, unaccounted **0**.

## 2026-07-28 - trader/quest packages and telnet console path

Eighteenth depth round (four residual leaves concurrent).

- `loot-economy.md`: NetPackageTraderData wire (entity vs TE) + server CopyFrom.
- `quests-challenges.md` section 8: QuestObjectiveUpdate, QuestEvent envelope,
  NPCQuestList type tails.
- `npc-dialog.md` / `parties-factions.md`: NPCQuestList write IL; ally write ILs.
- `console-commands.md`: Telnet HandlerThread 25ms + handleReading; ServerConsoleCommand
  permission/client-exec branches.
- `protocol-packages.md` 6.18: trader/quest package summaries.

Coverage: narrated **1319 (35%)**, unaccounted **0**.

## 2026-07-28 - QuestEvent tails, web Command, claims, sleeper/BM packages

Nineteenth depth round (four residual leaves concurrent).

- `quests-challenges.md` section 8: full QuestEventTypes 0..16 wire tails from
  write IL switch (header + per-type extras).
- `webserver.md` 6.0: WebAPI.APIs.Command GET/POST + WebConnection session.
- `server-lifecycle.md` section 4: LandClaimRepair, PersistentPlayerState/Positions.
- `aidirector.md`: AIDirector.Save v10; BloodMoonComponent fields; sleeper wake/
  pose/passive + BloodmoonMusic + GameStats packages.
- `protocol-packages.md` 6.19: package summaries; console WebAPI cross-link.

Coverage: narrated **1326 (35%)**, unaccounted **0**.

## 2026-07-28 - GameStats census, PPD write, sector V1/V2, map/sign/deco

Twentieth depth round (four residual leaves concurrent).

- `sandbox-options.md` 6.1: EnumGameStats 0..81; GameStats.Write persistent typed
  stream (no per-field ids).
- `server-lifecycle.md` 4.1: PersistentPlayerData.Write binary order (ids, LP
  blocks, backpacks, bedroll, quest positions, vending).
- `save-region.md` 3.4: RegionFileV1/V2 WriteData (4096 sectors, headers
  8196/12288, free alloc).
- `protocol-packages.md` 6.20: Weather, MapMarkerRemove, POIWaypoint, SignData*,
  DecoUpdate; map-objects/signs IL notes.

Coverage: narrated **1328 (36%)**, unaccounted **0**.

## 2026-07-28 - bulk residual package catalog (all 193 named)

Twenty-first depth round: close remaining NetPackage narrative gaps.

- `protocol-packages.md` section 6.21: entity/player/item/world/FX/misc package
  wire table (EntityRemove, Physics, ItemDrop, WireActions, HordeEvent, scores,
  RequestToSpawnPlayer name pin, ...).
- Cross-links: entity-ai, items, tile-entities-power, aidirector, managers.
- `residuals.md`: package narrative residual reduced; region sector residual
  narrowed to optional bit packing.
- `coverage.md`: networking residual text points at 6.21 + body inventory.

All **193** census package type names now appear in narrative docs (0 missing).

Coverage: narrated **1393 (37%)**, catalogued 901,
classified 1394, unaccounted **0**.

## 2026-07-28 - PPL list save, DM/POI/Nav packages, ally binary

Twenty-second depth round.

- `server-lifecycle.md` 4.2: PersistentPlayerList binary (players + lp map +
  Allies) and players.xml path.
- `protocol-packages.md` 6.22: DynamicMesh, POIAround, NavObject,
  EntityWaypointList bodies.
- `parties-factions.md`: AllyStore.Write pair layout.
- `entity-ai.md`: SleeperVolume.Tick IL=137.
- `map-objects.md`: NetPackageNavObject fields.

Coverage: narrated **1393 (37%)**, unaccounted **0**.

## 2026-07-28 - managed RE corpus complete (honest residuals only)

Stopping condition for continuous depth: no further dedi-critical managed surface
remains unmapped without a non-IL residual reason.

- All 193 NetPackage names in narrative docs; sections 6.21-6.22 bulk + DM/POI/Nav/Boss
- PersistentPlayerList save, GameStats, region V1/V2, join/spawn/stream paths closed
- residuals.md section 3: managed corpus status; open items are non-IL only

Coverage: narrated **1393 (37%)**, catalogued 901,
classified 1394, unaccounted **0**.

Blocked still: experimental-delta (steamcmd), push (no remotes).

## 2026-08-02 - V3.1.0 (b14) Henpocalypse research retarget

**Verified pin:** Constants Major=3 Minor=10 Build=14 -> `V 3.1.0 (b14)`.
Steam dedicated buildid 24436799. Official: Henpocalypse release notes.

**Census (live ASM):** types 4414, methods-with-body 44107, gmUpdate IL=631
(unchanged), WorldState.SaveLoad=926, NetPackage wire=193. Matches former
experimental-delta provisional numbers.

**Docs:**
- Promoted experimental-delta to **shipped V3.1.0** status.
- NetPackageTileEntity wire: teBlockId:i32 + payloadLen i32 (was u16).
- Held-entity / grab notes on items + entity-ai; join analytics on server-lifecycle.
- Classified 4 new XUi leaves OOS; unaccounted **0**.
- Bulk narrative pin V3.0.1 -> V3.1.0 (historical il/*-v3.0.1 dump names kept).
- Workspace AGENTS + MODDING_BEST_PRACTICES + sibling pins.

**Coverage:** narrated 1400 (37%), catalogued 901, classified 1398, unaccounted 0.

**Next:** rebuild EfficientServer against 3.1.0 ASM; stress APM optional; zdtd TE
reader must accept teBlockId.

## 2026-08-02 - WorldState.SaveLoad V3.1.0 field re-diff

IL=926 on live ASM; `CurrentSaveVersion=23`. Documented version gates for
structured VersionInformation (v>14), sleeper/trigger/wall `*VolumesSaveVersion`
(v>=23), weatherManagerState blob (v>=22). No new top-level WorldState fields
beyond those gates. save-region.md §1.1 updated.

## 2026-08-02 - V3.1.0 follow-ups closed

1. **zdtd TE wire** (`ef97257`): outer NetPackageTileEntity teBlockId:i32 +
   payloadLen:i32 in stock_te.zig; 197/197 tests pass.
2. **WorldState.SaveLoad** (`f6647ef`): IL=926, CurrentSaveVersion=23, volume
   save-version ints + weather/VersionInformation gates documented.
3. **loadgen PackageIds** (`loadgen`): dual live head fixtures 3.0.1 + 3.1.0
   (captured maps=189, minor=10 build=14). golden-wire PASS.

Subagents with forced anthropic models failed (no API key); executed in-session.
