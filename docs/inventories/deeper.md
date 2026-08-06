# DumpDeeper auto notes

**Kind:** auto dump notes (not primary narrative).
**Prefer:** [`entity-ai.md`](../entity-ai.md).
**Raw IL:** [`../il/deeper-v3.1.0/`](../../il/deeper-v3.1.0/) (`DEEPER.md` source).

---

## Deeper RE notes (V3.0.1 dedicated)

Generated UTC: 2026-07-18 04:55:06Z
Assembly: `~/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll`

Documentation only. No game IL redistribution as product.


## 1. All EAI* / UAI* task methods by IL size

- **846** `EAIApproachAndAttackTarget::Update()`
- **461** `EAIManager::MakeDebugName(EntityPlayer)`
- **317** `EAIDestroyArea::Continue()`
- **300** `UAIConsiderationPathBlocked::CanAttackBlocks(EntityAlive,Single,Single&,Vector3i&,BlockValue&)`
- **287** `EAIManager::GetType(String)`
- **281** `EAISetNearestEntityAsTarget::FindTarget()`
- **231** `UAIConsiderationBase::ComputeResponseCurve(Single)`
- **213** `EAIManager::CopyPropertiesFromEntityClass(EntityClass)`
- **209** `EAIDestroyArea::CanExecute()`
- **184** `EAISetNearestEntityAsTarget::FindTargetPlayer(Single)`
- **172** `EAIApproachAndAttackTarget::GetMoveToLocation(Single)`
- **171** `EAIDroneItemTask::DoMoveIntoAtkPos(EntityAlive,Single,Vector3,Single,Boolean,Single)`
- **170** `EAISetAsTargetIfHurt::CanExecute()`
- **166** `EAIRunawayFromEntity::FindEnemy()`
- **163** `EAIDroneItemModStunWeapon::Continue()`
- **151** `EAIDroneItemModHealWeapon::Continue()`
- **137** `EAITaskList::OnUpdateTasks()`
- **136** `EAILeap::CanExecute()`
- **134** `EAISetNearestEntityAsTarget::Continue()`
- **132** `EAIApproachAndAttackTarget::ToString()`
- **124** `UAIPackage::DecideAction(Context,UAIAction&,Object&)`
- **118** `EAIBreakBlock::AttackBlock()`
- **117** `EAIDroneItemTask::DoFleeFromTargetEntity(EntityAlive,Single,Single,Boolean,Single)`
- **116** `EAILook::Continue()`
- **111** `EAIDroneItemModStunWeapon::CanExecute()`
- **111** `EAIManager::ParseTasks(String,EAITaskList)`
- **111** `EAIPathTest::Update()`
- **110** `EAISetNearestCorpseAsTarget::CanExecute()`
- **107** `EAIMeleeAttackTarget::Update()`
- **107** `EAIRangedAttackTarget::Update()`
- **105** `EAIRunAway::Update()`
- **103** `EAIDroneItemTask::FollowPlannedPath(Single,Single,Boolean,Single)`
- **102** `UAIConsiderationBase::Init(Dictionary`2)`
- **99** `EAIDroneItemModHealWeapon::CanExecute()`
- **99** `EAISetNearestEntityAsTarget::SetData(Dictionary`2)`
- **97** `UAIBase::chooseAction(Context)`
- **96** `EAIManager::FallHitGround(Single)`
- **94** `EAIApproachDistraction::Update()`
- **94** `EAIWander::CanExecute()`
- **91** `EAISetNearestEntityAsTarget::SeekNoise(EntityPlayer)`
- **90** `UAITaskMoveToTarget::Start(Context)`
- **89** `EAIDodge::CanExecute()`
- **88** `EAIBlockIf::SetData(Dictionary`2)`
- **81** `EAIBreakBlock::CanExecute()`
- **76** `EAIApproachAndAttackTarget::SetData(Dictionary`2)`
- **72** `UAITaskAttackTargetBlock::Update(Context)`
- **72** `UAIAction::GetScore(Context,Object,Single)`
- **71** `EAITarget::check(EntityAlive)`
- **71** `UAIFromXml::parseActionNode(UAIPackage,XElement)`
- **71** `UAITaskAttackTargetEntity::Update(Context)`
- **70** `EAIApproachAndAttackTarget::CanExecute()`
- **70** `EAIMeleeAttackTarget::SetData(Dictionary`2)`
- **69** `EAIApproachAndAttackTarget::Start()`
- **69** `EAIMeleeAttackTarget::CanExecute()`
- **69** `EAIRangedAttackTarget::CanExecute()`
- **68** `EAIApproachSpot::Continue()`
- **64** `EAIRangedAttackTarget::SetData(Dictionary`2)`
- **63** `UAIFromXml::parseAIPackageNode(XElement)`
- **63** `UAIBase::updateAction(Context)`
- **62** `EAIBlockIf::CanExecute()`

## 2. Entity hierarchy live/update overrides (IL)

- `Entity::OnUpdateEntity` IL=84 base=MonoBehaviour
- `Entity::OnUpdatePosition` IL=225 base=MonoBehaviour
- `Entity::Update` IL=105 base=MonoBehaviour
- `EntityAlive::updateTasks` IL=125 base=Entity
- `EntityAlive::OnUpdateLive` IL=363 base=Entity
- `EntityAlive::OnUpdateEntity` IL=417 base=Entity
- `EntityAlive::OnUpdatePosition` IL=107 base=Entity
- `EntityAlive::Update` IL=170 base=Entity
- `EntityAnimal::OnUpdateLive` IL=57 base=EntityAlive
- `EntityAsyncManager::Update` IL=22 base=Object
- `EntityBackpack::OnUpdateEntity` IL=172 base=EntityItem
- `EntityBackpack::Update` IL=38 base=EntityItem
- `EntityBandit::updateTasks` IL=12 base=EntityHuman
- `EntityCar::OnUpdateLive` IL=73 base=EntityAlive
- `EntityCar::Update` IL=66 base=EntityAlive
- `EntityDrone::updateTasks` IL=139 base=EntityNPC
- `EntityDrone::OnUpdateEntity` IL=178 base=EntityNPC
- `EntityEnemyAnimal::updateTasks` IL=26 base=EntityEnemy
- `EntityFallingBlock::OnUpdateEntity` IL=344 base=Entity
- `EntityFallingBlock::Update` IL=147 base=Entity
- `EntityFallingBlocks::OnUpdateEntity` IL=302 base=Entity
- `EntityFallingBlocks::Update` IL=117 base=Entity
- `EntityFallingTree::OnUpdateEntity` IL=91 base=Entity
- `EntityHomerunGoal::Update` IL=247 base=Entity
- `EntityHuman::OnUpdateLive` IL=157 base=EntityEnemy
- `EntityItem::OnUpdateEntity` IL=114 base=Entity
- `EntityLootContainer::OnUpdateEntity` IL=46 base=EntityItem
- `EntityPlayer::OnUpdateEntity` IL=176 base=EntityAlive
- `EntityPlayer::Update` IL=179 base=EntityAlive
- `EntityPlayerLocal::OnUpdateLive` IL=879 base=EntityPlayer
- `EntityPlayerLocal::OnUpdateEntity` IL=153 base=EntityPlayer
- `EntityPlayerLocal::OnUpdatePosition` IL=182 base=EntityPlayer
- `EntityPlayerLocal::Update` IL=675 base=EntityPlayer
- `EntitySupplyCrate::OnUpdateEntity` IL=103 base=EntityAlive
- `EntitySupplyCrate::Update` IL=39 base=EntityAlive
- `EntitySupplyPlane::OnUpdatePosition` IL=49 base=Entity
- `EntitySwarm::OnUpdateLive` IL=37 base=EntityVulture
- `EntityTrader::OnUpdateLive` IL=315 base=EntityNPC
- `EntityTurret::OnUpdateEntity` IL=414 base=EntityAlive
- `EntityVehicle::updateTasks` IL=1 base=EntityAlive
- `EntityVehicle::Update` IL=166 base=EntityAlive
- `EntityVHelicopter::Update` IL=55 base=EntityDriveable
- `EntityVulture::updateTasks` IL=1344 base=EntityFlying
- `EntityZombieCop::OnUpdateEntity` IL=190 base=EntityZombie
- `EntityZombieDog::OnUpdateLive` IL=16 base=EntityEnemyAnimal

## 3. Dumped deep targets

- dumped `EntityMoveHelper::UpdateMoveHelper()` IL=1236
- dumped `EntityMoveHelper::SetMoveTo(Vector3,Boolean)` IL=29
- dumped `EntityMoveHelper::SetMoveTo(Vector3,Boolean,Single)` IL=27
- dumped `EntityMoveHelper::SetMoveTo(PathEntity,Single,Boolean)` IL=78
- dumped `EAIApproachAndAttackTarget::Update()` IL=846
- dumped `EAIApproachAndAttackTarget::CanExecute()` IL=70
- dumped `EAIApproachAndAttackTarget::Start()` IL=69
- dumped `EAIApproachAndAttackTarget::Continue()` IL=50
- dumped `EAIApproachAndAttackTarget::Reset()` IL=16
- dumped `EAISetNearestEntityAsTarget::CanExecute()` IL=27
- dumped `EAISetNearestEntityAsTarget::FindTarget()` IL=281
- dumped `EAISetNearestEntityAsTarget::FindTargetPlayer(Single)` IL=184
- dumped `EAIWander::Update()` IL=7
- dumped `EAIWander::Start()` IL=19
- dumped `EAIWander::CanExecute()` IL=94
- dumped `EAIRunAway::Update()` IL=105
- dumped `EAIRunAway::CanExecute()` IL=5
- dumped `EAIBreakBlock::Update()` IL=21
- dumped `EAIBreakBlock::AttackBlock()` IL=118
- dumped `EAIBreakBlock::CanExecute()` IL=81
- dumped `PathNavigate::UpdateNavigation()` IL=1
- dumped `PathNavigate::noPath()` IL=9
- dumped `PathNavigate::noPathAndNotPlanningOne()` IL=13
- dumped `ASPPathNavigate::UpdateNavigation()` IL=21
- dumped `ASPPathNavigate::pathFollow()` IL=160
- dumped `ASPPathNavigate::GetPathTo(PathInfo)` IL=19
- dumped `ASPPathNavigate::CreatePath()` IL=38
- dumped `AStarPathFinderThread::thread_Pathfinder(ThreadInfo)` IL=109
- dumped `AStarPathFinderThread::FindPath(EntityAlive,Vector3,Single,Boolean,EAIBase)` IL=42
- dumped `AStarPathFinderThread::GetPath(Int32)` IL=35
- dumped `EntityAlive::FindPath(Vector3,Single,Boolean,EAIBase)` IL=49
- dumped `EntityAlive::CheckDespawn()` IL=198
- dumped `EntityAlive::updateCurrentBlockPosAndValue()` IL=318
- dumped `EntityAlive::CanSee(Vector3)` IL=62
- dumped `EntityAlive::CanSeeStealth(Single,Single)` IL=21
- dumped `EntityAlive::CanSee(EntityAlive)` IL=5
- dumped `EntityAlive::SetCanSee(EntityAlive)` IL=5
- dumped `EntityAnimal::OnUpdateLive()` IL=57
- dumped `World::GetClosestPlayer(Single,Single,Single,Int32,Double)` IL=63
- dumped `World::GetClosestPlayer(Entity,Single,Boolean)` IL=7
- dumped `World::GetClosestPlayer(Vector3,Single,Boolean)` IL=57
- dumped `World::GetClosestPlayerSeen(EntityAlive,Single,Single)` IL=68
- dumped `World::GetEntitiesInBounds(Entity,Bounds)` IL=75
- dumped `World::GetEntitiesInBounds(Entity,Bounds,Boolean)` IL=75
- dumped `World::GetEntitiesInBounds(FastTags`1,Bounds,List`1)` IL=68
- dumped `World::GetEntitiesInBounds(Type,Bounds,List`1)` IL=69
- dumped `World::ClipBoundsMove(Entity,Bounds,Vector3,Vector3,Single)` IL=573
- dumped `World::AddFallingBlocks(IList`1)` IL=18
- dumped `World::AddFallingBlock(Vector3i,Boolean)` IL=38
- dumped `World::GroupFallingBlocks()` IL=292
- dumped `NetEntityDistributionEntry::updatePlayerList(List`1)` IL=509
- dumped `NetEntityDistributionEntry::updatePlayerEntity(EntityPlayer)` IL=222
- dumped `NetEntityDistributionEntry::SendToPlayers(NetPackage,Int32,Boolean,Int32)` IL=42
- dumped `NetEntityDistributionEntry::EncodePos(Vector3)` IL=20
- dumped `NetEntityDistributionEntry::EncodeRot(Vector3)` IL=7
- dumped `SpawnManagerBiomes::SpawnUpdate(String,Boolean,ChunkAreaBiomeSpawnData)` IL=441
- dumped `SpawnManagerBiomes::Update(String,Boolean,Object)` IL=9
- dumped `SpawnManagerBiomes::SpawnUpdate(String,Boolean,ChunkAreaBiomeSpawnData)` IL=441
- dumped `AIDirectorBloodMoonComponent::Tick(Double)` IL=170
- dumped `AIDirectorBloodMoonComponent::get_BloodMoonActive()` IL=3
- dumped `AIDirector::ComponentsTick(Double)` IL=21
- dumped `AIHordeSpawner::Tick(Double)` IL=210
- dumped `SleeperVolume::Tick(World)` IL=137
- dumped `SleeperVolume::UpdateSpawn(World)` IL=516
- dumped `SleeperVolume::DespawnAndReset(World)` IL=6
- dumped `SleeperVolume::Despawn(World)` IL=48
- dumped `SleeperVolume::CheckTouching(World,EntityPlayer)` IL=165
- dumped `DecoManager::UpdateTick(World)` IL=330
- dumped `WaterSplashCubes::Update()` IL=185
- dumped `ChunkManager::DetermineChunksToLoad()` IL=448
- dumped `ChunkManager::SendChunksToClients()` IL=216
- dumped `ChunkManager::ResendChunksToClients(HashSetLong)` IL=55
- dumped `ChunkManager::doCopyChunksToUnity()` IL=252
- dumped `DynamicMeshServer::Update()` IL=452
- dumped `GameTimer::updateTimer(Boolean)` IL=74
- dumped `EntitySeeCache::ClearIfExpired()` IL=17
- dumped `EntitySeeCache::CanSee(Entity)` IL=49
- dumped `EntitySeeCache::SetCanSee(Entity)` IL=7
- dumped `EntitySeeCache::SetCanSee(Entity)` IL=7
- dumped `EntityLookHelper::onUpdateLook()` IL=32
- dumped `EAITaskList::isBestTask(EAITaskEntry)` IL=38
- dumped `EAITaskList::areTasksCompatible(EAITaskEntry,EAITaskEntry)` IL=10
- dumped `EAITaskList::OnUpdateTasks()` IL=137
- dumped `UAIBase::Update(Context)` IL=18
- dumped `UAIBase::updateAction(Context)` IL=63
- dumped `UAIBase::addEntityTargetsToConsider(Context)` IL=58
- dumped `WorldBlockTicker::tickScheduled(GameRandom)` IL=151
- dumped `WorldBlockTicker::tickRandom(ArraySegment`1,GameRandom)` IL=97
- dumped `WorldBlockTicker::execute(WorldBlockTickerEntry,GameRandom,UInt64)` IL=24
- dumped `BlockLiquidv2::UpdateTick(WorldBase,Vector3i,BlockValue,Boolean,UInt64,GameRandom)` IL=1106
- dumped `BlockLiquidv2::UpdateTime()` IL=3
- dumped `GameManager::ExplodeGroupFrameUpdate()` IL=220
- dumped `GameManager::updateTimeOfDay()` IL=156
- dumped `GameManager::updateBlockParticles()` IL=65
- dumped `GameManager::updatePauseState()` IL=94
- dumped `ConnectionManager::ProcessPackages(INetConnection,NetPackageDirection,ClientInfo)` IL=116
- dumped `ConnectionManager::SendPackage(List`1,Boolean,Int32,Int32,Int32,Nullable`1,Int32,Boolean)` IL=168
- dumped `ConnectionManager::SendPackage(NetPackage,Boolean,Int32,Int32,Int32,Nullable`1,Int32,Boolean)` IL=100
- dumped `ConnectionManager::FlushClientSendQueues()` IL=28
- dumped `PowerManager::SetTileEntityUpdate(TileEntityPoweredBlock,Boolean)` IL=14
- dumped `PowerManager::Update()` IL=106
- dumped `VehicleManager::Update()` IL=297
- dumped `VehicleManager::UpdateVehicleWaypoints()` IL=22
- dumped `VehicleManager::UpdateVehicleWaypointsForPlayer(Int32)` IL=69
- dumped `DroneManager::Update()` IL=305
- dumped `DroneManager::UpdateWaypointsForAllPlayers()` IL=22
- dumped `DroneManager::UpdateWaypointsForPlayer(Int32)` IL=96
- dumped `<FindPaths>d__8::MoveNext` IL=87

## 4. Float/int constants in key methods (heuristic thresholds)

### `EntityAlive::FindPath` IL=49
- floats: -45, 45, 1225
- ints: 

### `EntityAlive::updateTasks` IL=125
- floats: 0, 1
- ints: 46

### `World::EntityActivityUpdate` IL=229
- floats: -1, 0, 0.1, 0.3, 1, 36, 64, 225, 625, 3025, 3.402823E+38
- ints: 20, 60

### `World::GetClosestPlayer` IL=63
- floats: -1
- ints: 

### `World::GetClosestPlayer` IL=7
- floats: 
- ints: 

### `World::GetClosestPlayer` IL=57
- floats: 0, 3.402823E+38
- ints: 

### `NetEntityDistributionEntry::updatePlayerList` IL=509
- floats: 0, 0.04, 2, 16
- ints: -256, -128, 10, 100, 128, 192, 256, 2147483647

### `EntityMoveHelper::UpdateMoveHelper` IL=1236
- floats: -1.5, -1.1, -0.86, -0.5, -0.25, -0.1, -0.01, 0, 0.0001, 0.0009, 0.001, 0.01, 0.01745329, 0.02, 0.021, 0.0225, 0.025, 0.03, 0.05, 0.06, 0.07, 0.1, 0.1089, 0.16, 0.2, 0.25, 0.3, 0.36, 0.4, 0.4225, 0.45, 0.5, 0.6, 0.64, 0.7, 0.8, 0.9, 1, 1.3, 1.4
- ints: -3, 12, 20, 40, 80, 160, 1082195968

### `EAIApproachAndAttackTarget::Update` IL=846
- floats: -8, -1.25, 0, 0.04, 0.05, 0.08, 0.1, 0.16, 0.2, 0.3, 0.35, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1, 1.095, 1.1, 2, 2.1, 2.5, 3, 4, 5, 8, 18, 20, 28, 30, 60, 90
- ints: 10, 11, 20, 25, 35, 40, 46, 60

### `EAIManager::Update` IL=16
- floats: 0.008333334, 10
- ints: 

### `EAITaskList::OnUpdateTasks` IL=137
- floats: 0, 0.05
- ints: 

### `SpawnManagerBiomes::SpawnUpdate` IL=441
- floats: 1, 2.5, 4, 40, 80
- ints: 13, 16, 28, 31, 48, 54, 70, 80, 129

### `SleeperVolume::Tick` IL=137
- floats: 
- ints: 

### `GameTimer::updateTimer` IL=74
- floats: 
- ints: 

### `ASPPathNavigate::pathFollow` IL=160
- floats: 0, 0.04, 0.15, 0.2, 0.33, 0.49, 0.6, 0.7, 0.9, 2
- ints: 


## 5. Spatial query callers (full)

### `GetClosestPlayer`

- `AIDirectorChunkEventComponent::SpawnScouts` → `World::GetClosestPlayer`
- `EntityAlive::CheckDespawn` → `World::GetClosestPlayer`
- `EntityVulture::FindTarget` → `World::GetClosestPlayer`
- `QuestEventManager::BlockDestroyed` → `World::GetClosestPlayer`
- `World::EntityActivityUpdate` → `World::GetClosestPlayer`
- `World::GetClosestPlayer` → `World::GetClosestPlayer`

_(6 caller types)_

### `GetEntitiesInBounds`

- `BlockSpawnEntity::UpdateTick` → `World::GetEntitiesInBounds`
- `TEFeatureStorage::UpdateTick` → `World::GetEntitiesInBounds`
- `AutoTurretFireController::findTarget` → `World::GetEntitiesInBounds`
- `MiniTurretFireController::findTarget` → `World::GetEntitiesInBounds`
- `MotionSensorController::hasTarget` → `World::GetEntitiesInBounds`
- `SpinningBladeTrapBladeController::Update` → `World::GetEntitiesInBounds`
- `Entity::OnUpdateEntity` → `World::GetEntitiesInBounds`
- `AIDirector::DebugSendNameInfo` → `World::GetEntitiesInBounds`
- `AIDirector::DebugSendLatency` → `World::GetEntitiesInBounds`
- `AIHordeSpawner::Tick` → `World::GetEntitiesInBounds`
- `EAIBreakBlock::AttackBlock` → `World::GetEntitiesInBounds`
- `EAIDodge::CanExecute` → `World::GetEntitiesInBounds`
- `EAIManager::FallHitGround` → `World::GetEntitiesInBounds`
- `EAIRunawayFromEntity::FindEnemy` → `World::GetEntitiesInBounds`
- `EAISetNearestEntityAsTarget::FindTarget` → `World::GetEntitiesInBounds`
- `EntityFallingBlock::OnUpdateEntity` → `World::GetEntitiesInBounds`
- `EntityFallingBlocks::OnUpdateEntity` → `World::GetEntitiesInBounds`
- `EntityHomerunGoal::Update` → `World::GetEntitiesInBounds`
- `EntityItem::tickDistraction` → `World::GetEntitiesInBounds`
- `EntityTrader::OnUpdateLive` → `World::GetEntitiesInBounds`
- `EntityVulture::updateTasks` → `World::GetEntitiesInBounds`
- `HasTrackedEntity::IsValid` → `World::GetEntitiesInBounds`
- `Prefab::CopyFromWorldWithEntities` → `Chunk::GetEntitiesInBounds`
- `ObjectiveInteractWithNPC::AddHooks` → `World::GetEntitiesInBounds`
- `SpawnManagerBiomes::SpawnUpdate` → `World::GetEntitiesInBounds`
- `TraderArea::GetTrader` → `World::GetEntitiesInBounds`
- `World::GetCollidingBounds` → `World::GetEntitiesInBounds`
- `World::GetEntitiesInBounds` → `Chunk::GetEntitiesInBounds`
- `World::GetEntitiesInBounds` → `Chunk::GetEntitiesInBounds`
- `World::GetEntitiesInBounds` → `Chunk::GetEntitiesInBounds`
- `World::GetEntitiesInBounds` → `Chunk::GetEntitiesInBounds`
- `PlayerMoveController::FindCameraSnapTarget` → `World::GetEntitiesInBounds`
- `UAIBase::addEntityTargetsToConsider` → `World::GetEntitiesInBounds`
- `RequirementNearbyEntities::CanPerform` → `World::GetEntitiesInBounds`
- `HomerunGoalController::Update` → `World::GetEntitiesInBounds`
- `ActionAddClosestEntityToGroup::OnPerformAction` → `World::GetEntitiesInBounds`
- `ActionAddEntitiesToGroup::OnPerformAction` → `World::GetEntitiesInBounds`
- `ActionDestroySafeZone::OnPerformAction` → `World::GetEntitiesInBounds`
- `ActionFillArea::OnPerformAction` → `World::GetEntitiesInBounds`
- `ActionFillSafeZone::OnPerformAction` → `World::GetEntitiesInBounds`
- `PlayerTracker::IsTraderAreaOpen` → `World::GetEntitiesInBounds`
- `PlayerTracker::determineTrader` → `World::GetEntitiesInBounds`
- `ThreatLevelUtility::GetThreatLevelOn` → `World::GetEntitiesInBounds`
- `ThreatLevelTracker::TickTrackThreatLevel` → `World::GetEntitiesInBounds`

_(44 caller types)_

### `FindPath`

- `EAIApproachAndAttackTarget::Update` → `EntityAlive::FindPath`
- `EAIApproachDistraction::updatePath` → `EntityAlive::FindPath`
- `EAIApproachSpot::updatePath` → `EntityAlive::FindPath`
- `EAIDestroyArea::Continue` → `EntityAlive::FindPath`
- `EAIPathTest::Update` → `PathFinderThread::FindPath`
- `EAIRunAway::Update` → `EntityAlive::FindPath`
- `EAITerritorial::Start` → `EntityAlive::FindPath`
- `EAIWander::Start` → `EntityAlive::FindPath`
- `EntityAlive::FindPath` → `PathFinderThread::FindPath`
- `EntityDrone::GetProjectedPath` → `PathFinderThread::FindPath`
- `UAITaskFleeFromTarget::Start` → `EntityAlive::FindPath`
- `UAITaskMoveToTarget::Start` → `EntityAlive::FindPath`
- `UAITaskWander::Start` → `EntityAlive::FindPath`

_(13 caller types)_

### `UpdateMoveHelper`

- `EntityAlive::updateTasks` → `EntityMoveHelper::UpdateMoveHelper`

_(1 caller types)_

### `AddFallingBlock`

- `EntityAlive::updateCurrentBlockPosAndValue` → `World::AddFallingBlock`
- `MultiBlockManager::UpdateOversizedStability` → `World::AddFallingBlock`
- `World::AddFallingBlocks` → `World::AddFallingBlock`
- `ActionBlockTriggerFall::ProcessChanges` → `World::AddFallingBlock`

_(4 caller types)_

### `SpawnUpdate`

- `AIScoutHordeSpawner::Update` → `AIScoutHordeSpawner::SpawnUpdate`
- `AIScoutHordeSpawner::spawnHordeNear` → `AIScoutHordeSpawner::SpawnUpdate`
- `SpawnManagerBiomes::Update` → `SpawnManagerBiomes::SpawnUpdate`

_(3 caller types)_

### `pathFollow`

- `ASPPathNavigate::UpdateNavigation` → `ASPPathNavigate::pathFollow`

_(1 caller types)_

### `SetPath`

- `EntityAlive::updateTasks` → `PathNavigate::SetPath`
- `EntityAlive::OnEntityUnload` → `PathNavigate::SetPath`

_(2 caller types)_

### `GetPathTo`

- `AStarPathFinderThread::thread_Pathfinder` → `PathNavigate::GetPathTo`

_(1 caller types)_


## 6. EntityAlive AI-related fields

- `aiActiveDelay` : Single
- `aiActiveScale` : Single
- `aiClosestPlayer` : EntityPlayer
- `aiClosestPlayerDistSq` : Single
- `aiManager` : EAIManager
- `AIPackages` : List`1
- `alertEnabled` : Boolean
- `alertTicks` : Int32
- `attackTarget` : EntityAlive
- `attackTargetClient` : EntityAlive
- `attackTargetLast` : EntityAlive
- `attackTargetTime` : Int32
- `bAimingGun` : Boolean
- `bMovementRunning` : Boolean
- `bReplicatedAlertFlag` : Boolean
- `crouchBendPerTarget` : Single
- `CurrentMovementTag` : FastTags`1
- `damagedTarget` : EntityAlive
- `distraction` : EntityItem
- `distractionResistance` : Single
- `distractionResistanceWithTarget` : Single
- `DistractionResistanceWithTargetTags` : FastTags`1
- `hasAI` : Boolean
- `investigatePos` : Vector3
- `investigatePositionTicks` : Int32
- `isAlert` : Boolean
- `isInvestigateAlert` : Boolean
- `isMoveDirAbsolute` : Boolean
- `IsSleeper` : Boolean
- `IsSleeperPassive` : Boolean
- `IsSleeping` : Boolean
- `jumpMovementFactor` : Single
- `landMovementFactor` : Single
- `lastSleeperPose` : Int32
- `lookAtPosition` : Vector3
- `lookHelper` : EntityLookHelper
- `moveDirection` : Vector3
- `moveHelper` : EntityMoveHelper
- `MovementTagClimbing` : FastTags`1
- `MovementTagDriving` : FastTags`1
- `MovementTagFalling` : FastTags`1
- `MovementTagFloating` : FastTags`1
- `MovementTagIdle` : FastTags`1
- `MovementTagJumping` : FastTags`1
- `MovementTagRunning` : FastTags`1
- `MovementTagSwimming` : FastTags`1
- `MovementTagSwimmingRun` : FastTags`1
- `MovementTagWalking` : FastTags`1
- `moveSpeed` : Single
- `moveSpeedAggro` : Single
- `moveSpeedAggroMax` : Single
- `moveSpeedNight` : Single
- `moveSpeedPanic` : Single
- `moveSpeedPanicMax` : Single
- `moveSpeedRandomness` : Single[]
- `navigator` : PathNavigate
- `notAlertDelayTicks` : Int32
- `notAlertedId` : String
- `painHitsFelt` : Single
- `painResistPercent` : Single
- `pendingDistraction` : EntityItem
- `pendingDistractionDistanceSq` : Single
- `pendingSleepTrigger` : Int32
- `renderFadeTarget` : Single
- `seeCache` : EntitySeeCache
- `sleeperLookDir` : Vector3
- `sleeperNoiseToSense` : Single
- `sleeperNoiseToSenseSoundChance` : Single
- `sleeperNoiseToWake` : Single
- `sleeperSightRange` : Single
- `SleeperSpawnLookDir` : Vector3
- `SleeperSpawnPosition` : Vector3
- `SleeperSupressLivingSounds` : Boolean
- `sleeperViewAngle` : Single
- `soundAlert` : String
- `soundAlertTicks` : Int32
- `soundDrownPain` : String
- `soundSleeperGroan` : String
- `soundSleeperSnore` : String
- `speedForwardTarget` : Single
- `speedForwardTargetStep` : Single
- `stepSoundDistanceRemaining` : Single
- `stepSoundRotYRemaining` : Single
- `targetAlertChanged` : Boolean
- `ticksToCheckSeenByPlayer` : Int32
- `utilityAIContext` : Context
- `wasSeenByPlayer` : Boolean

## 7. World tick-related fields

- `areaMasterChunksToLock` : Dictionary`2
- `biomeSpawnManager` : SpawnManagerBiomes
- `chunksToRegenerate` : HashSetList`1
- `chunksToUncull` : HashSetList`1
- `clientLastEntityId` : Int32
- `dynamicSpawnManager` : SpawnManagerDynamic
- `entitiesWithinAABBExcludingEntity` : List`1
- `EntityAlives` : List`1
- `entityAsyncManager` : EntityAsyncManager
- `entityDistributer` : NetEntityDistribution
- `EntityLoadedDelegates` : OnEntityLoadedDelegate
- `EntityUnloadedDelegates` : OnEntityUnloadedDelegate
- `fallingBlocks` : Queue`1
- `fallingBlockSet` : HashSet`1
- `fallingGroups` : Queue`1
- `Last4Spawned` : List`1
- `livingEntitiesWithinAABBExcludingEntity` : List`1
- `m_ChunkManager` : ChunkManager
- `m_LocalPlayerEntity` : EntityPlayerLocal
- `m_lpChunkList` : List`1
- `m_SharedChunkObserverCache` : SharedChunkObserverCache
- `netEntityPackageQueue` : NetEntityPackageQueue
- `newlyLoadedChunksThisUpdate` : List`1
- `nextSleeperVolumeId` : Int32
- `playerEntityUpdateCount` : Int32
- `sleeperVolumeMap` : Dictionary`2
- `sleeperVolumes` : Dictionary`2
- `SleeperVolumeWorldStateSaveVersion` : Int32
- `tickEntityFrameCount` : Int32
- `tickEntityFrameCountAverage` : Single
- `tickEntityIndex` : Int32
- `tickEntityList` : List`1
- `tickEntityPartialTicks` : Single
- `tickEntitySliceCount` : Int32
- `worldBlockTicker` : WorldBlockTicker

## 8. PathFinderThread / ASP / AStar fields

### PathFinderThread
- `Instance` : GamePath.PathFinderThread
### ASPPathFinderThread
- `coroutine` : UnityEngine.Coroutine
- `entityWaitQueue` : HashSetList`1<System.Int32>
- `finishedPaths` : System.Collections.Generic.Dictionary`2<System.Int32,GamePath.PathInfo>
### AStarPathFinderThread
- `threadInfo` : ThreadManager/ThreadInfo
- `writerThreadWaitHandle` : System.Threading.AutoResetEvent
- `entityWaitQueue` : HashSetList`1<System.Int32>
- `finishedPaths` : System.Collections.Generic.Dictionary`2<System.Int32,GamePath.PathInfo>

## 9. NetPackage* constructed in NetEntityDistributionEntry

- `NetPackageEntityAliveFlags::Setup`
- `NetPackageEntityPosAndRot::Setup`
- `NetPackageEntityRelPosAndRot::Setup`
- `NetPackageEntityRemove::Setup`
- `NetPackageEntityRotation::Setup`
- `NetPackageEntitySpawn::Setup`
- `NetPackageEntitySpeeds::Setup`
- `NetPackageEntityTeleport::Setup`
- `NetPackageEntityVelocity::Setup`
- `NetPackageManager::GetPackage`
- `NetPackagePlayerEquipment::Setup`
- `NetPackagePlayerStats::Setup`
- `NetPackagePlayerTwitchStats::Setup`
- `via updatePlayerEntity → NetPackageEntityAliveFlags::Setup`
- `via updatePlayerEntity → NetPackageEntityRemove::Setup`
- `via updatePlayerEntity → NetPackageEntitySpeeds::Setup`
- `via updatePlayerEntity → NetPackageEntityVelocity::Setup`
- `via updatePlayerEntity → NetPackagePlayerEquipment::Setup`
- `via updatePlayerEntity → NetPackagePlayerStats::Setup`
- `via updatePlayerEntity → NetPackagePlayerTwitchStats::Setup`
- `via updatePlayerList → NetPackageEntityAliveFlags::Setup`
- `via updatePlayerList → NetPackageEntityPosAndRot::Setup`
- `via updatePlayerList → NetPackageEntityRelPosAndRot::Setup`
- `via updatePlayerList → NetPackageEntityRotation::Setup`
- `via updatePlayerList → NetPackageEntityTeleport::Setup`
- `via updatePlayerList → NetPackageEntityVelocity::Setup`
- `via updatePlayerList → NetPackagePlayerEquipment::Setup`
- `via updatePlayerList → NetPackagePlayerStats::Setup`
- `via updatePlayerList → NetPackagePlayerTwitchStats::Setup`

## 10. EntityMoveHelper.UpdateMoveHelper call breakdown

### `EntityMoveHelper::UpdateMoveHelper` IL=1236
- 9x `GameRandom::get_RandomFloat`
- 4x `EntityMoveHelper::ResetStuckCheck`
- 4x `Mathf::Sqrt`
- 4x `EntityMoveHelper::StartJump`
- 3x `EntityMoveHelper::ClearBlocked`
- 3x `EntityMoveHelper::DigStart`
- 2x `EntityMoveHelper::StopMove`
- 2x `EntityAlive::SetMoveForwardWithModifiers`
- 2x `Mathf::Atan2`
- 2x `Utils::FastLerp`
- 2x `Mathf::Sin`
- 2x `Mathf::Cos`
- 2x `Vector3::op_Multiply`
- 2x `EntityAlive::Attack`
- 2x `Object::op_Implicit`
- 1x `MathUtils::NormalizeAxis`
- 1x `CharacterControllerAbstract::GetHeight`
- 1x `CharacterControllerAbstract::GetRadius`
- 1x `EntityAlive::get_Jumping`
- 1x `Entity::IsInElevator`
- 1x `Utils::FastMax`
- 1x `AvatarController::IsRootMotionForced`
- 1x `EntityMoveHelper::ClearTempMove`
- 1x `AvatarController::IsAnimationWithMotionRunning`
- 1x `EntityAlive::get_sleepingOrWakingUp`
- 1x `EnumEntityStunTypeExtensions::CanMove`
- 1x `EModelBase::get_IsRagdollActive`
- 1x `EntityAlive::SetMoveForward`
- 1x `EntityMoveHelper::DigUpdate`
- 1x `Mathf::MoveTowardsAngle`
- 1x `EModelBase::ClearLookAt`
- 1x `Utils::DeltaAngle`
- 1x `Utils::FastAbs`
- 1x `EntityAlive::get_IsRunning`
- 1x `Utils::FastMin`


## 11. EAIApproachAndAttackTarget.Update call breakdown

### `EAIApproachAndAttackTarget::Update` IL=846
- 6x `EAIBase::get_RandomFloat`
- 4x `Vector3::op_Subtraction`
- 4x `Object::op_Inequality`
- 3x `Vector3::get_zero`
- 3x `PathFinderThread::IsCalculatingPath`
- 3x `EntityAlive::GetMoveSpeedAggro`
- 3x `EntityAlive::FindPath`
- 3x `Object::op_Equality`
- 3x `Vector3::op_Multiply`
- 2x `Vector3::get_sqrMagnitude`
- 2x `Utils::FastAbs`
- 2x `EntityAlive::SetLookPosition`
- 2x `PathNavigate::noPathAndNotPlanningOne`
- 2x `Vector3::op_Addition`
- 2x `BodyDamage::get_HasLimbs`
- 2x `EntityAlive::RotateTo`
- 2x `EAIBase::GetRandom`
- 2x `Entity::GetHeight`
- 2x `EAIApproachAndAttackTarget::GetMoveToLocation`
- 2x `EntityAlive::GetDamagedTarget`
- 2x `EntityAlive::ClearDamagedTarget`
- 2x `Object::op_Implicit`
- 2x `EntityAlive::Attack`
- 1x `Entity::SetPosition`
- 1x `EntityAlive::ResumeSleeperPose`
- 1x `EAIManager::GetTargetTasks`
- 1x `List`1::get_Item`
- 1x `EntityAlive::SetAttackTarget`
- 1x `EntityAlive::PlayGiveUpSound`
- 1x `EntityMoveHelper::SetFocusPos`
- 1x `Entity::getBellyPosition`
- 1x `Entity::PlayOneShot`
- 1x `Entity::DamageEntity`
- 1x `Vector3::.ctor`
- 1x `Color::get_white`


## 12. SpawnManagerBiomes.SpawnUpdate call breakdown

### `SpawnManagerBiomes::SpawnUpdate` IL=441
- 7x `List`1::get_Count`
- 5x `List`1::get_Item`
- 3x `FastTags`1::get_IsEmpty`
- 2x `FastTags`1::Test_AnySet`
- 1x `AIDirector::CanSpawn`
- 1x `AIDirector::get_BloodMoonComponent`
- 1x `AIDirectorBloodMoonComponent::get_BloodMoonActive`
- 1x `GameStats::GetInt`
- 1x `GamePrefs::GetInt`
- 1x `WorldBase::GetPlayers`
- 1x `EntityAlive::get_Spawned`
- 1x `Rect::.ctor`
- 1x `Rect::Overlaps`
- 1x `World::GetRandomSpawnPositionInAreaMinMaxToPlayers`
- 1x `WorldBiomes::GetBiome`
- 1x `DictionarySave`2::get_Item`
- 1x `World::IsDaytime`
- 1x `WorldBase::GetGameRandom`
- 1x `Chunk::GetWorldPos`
- 1x `World::GetPOIsAtXZ`
- 1x `Prefab::get_Tags`
- 1x `FastTags`1::op_BitwiseOr`
- 1x `GameRandom::RandomRange`
- 1x `Utils::FastMin`
- 1x `EntityGroups::IsEnemyGroup`
- 1x `ChunkAreaBiomeSpawnData::GetDelayWorldTime`
- 1x `EntitySpawner::ModifySpawnCountByGameDifficulty`
- 1x `ChunkAreaBiomeSpawnData::ResetRespawn`
- 1x `ChunkAreaBiomeSpawnData::CanSpawn`
- 1x `Bounds::.ctor`
- 1x `Type::GetTypeFromHandle`
- 1x `World::GetEntitiesInBounds`
- 1x `List`1::Clear`
- 1x `EntityGroups::GetRandomFromGroup`
- 1x `ChunkAreaBiomeSpawnData::DecMaxCount`


## 13. NetEntityDistributionEntry.updatePlayerList call breakdown

### `NetEntityDistributionEntry::updatePlayerList` IL=509
- 10x `NetPackageManager::GetPackage`
- 7x `NetEntityDistributionEntry::SendToPlayers`
- 6x `Utils::FastAbs`
- 4x `Object::op_Inequality`
- 3x `Entity::IsQRotationUsed`
- 2x `Vector3i::op_Subtraction`
- 2x `NetPackageEntityRelPosAndRot::Setup`
- 1x `Entity::GetDistanceSq`
- 1x `NetEntityDistributionEntry::updatePlayerEntities`
- 1x `Entity::PhysicsMasterSetupBroadcast`
- 1x `Entity::IsAirBorne`
- 1x `NetEntityDistributionEntry::EncodePos`
- 1x `NetEntityDistributionEntry::EncodeRot`
- 1x `NetPackageEntityTeleport::Setup`
- 1x `NetPackageEntityPosAndRot::Setup`
- 1x `NetPackageEntityRotation::Setup`
- 1x `Vector3::op_Subtraction`
- 1x `Vector3::get_sqrMagnitude`
- 1x `Vector3::get_zero`
- 1x `Vector3::Equals`
- 1x `NetPackageEntityVelocity::Setup`
- 1x `NetPackageEntityAliveFlags::Setup`
- 1x `NetPackagePlayerStats::Setup`
- 1x `NetPackagePlayerTwitchStats::Setup`
- 1x `NetPackagePlayerEquipment::Setup`
- 1x `Entity::SetAirBorne`


## 14. DynamicMeshServer.Update call breakdown

### `DynamicMeshServer::Update` IL=452
- 9x `Int32::ToString`
- 4x `String::Concat`
- 3x `ConcurrentQueue`1::TryDequeue`
- 3x `Enumerable::FirstOrDefault`
- 3x `DateTime::get_Now`
- 3x `Log::Out`
- 3x `ConcurrentDictionary`2::get_Count`
- 2x `Log::Warning`
- 2x `List`1::get_Count`
- 2x `Mathf::Pow`
- 2x `ConcurrentQueue`1::get_Count`
- 2x `Object::ToString`
- 2x `Time::get_time`
- 1x `DynamicMeshContainer::ToDebugLocation`
- 1x `List`1::Add`
- 1x `List`1::get_Item`
- 1x `ConnectionManager::ClientCount`
- 1x `DynamicMeshChunkDataStorage`1::ManuallyReleaseBytes`
- 1x `Nullable`1::get_Value`
- 1x `DateTime::op_Subtraction`
- 1x `TimeSpan::get_TotalMilliseconds`
- 1x `List`1::RemoveAt`
- 1x `DynamicMeshSyncRequest::TryGetData`
- 1x `NetPackageManager::GetPackage`
- 1x `NetPackageDynamicMesh::Setup`
- 1x `ConnectionManager::SendPackage`
- 1x `DynamicMeshSyncRequest::get_SecondsAttempted`
- 1x `List`1::Remove`
- 1x `Dictionary`2::get_Values`
- 1x `ValueCollection::GetEnumerator`
- 1x `Enumerator::get_Current`
- 1x `DynamicMeshClientConnection::get_TriggerSend`
- 1x `ConcurrentDictionary`2::ContainsKey`
- 1x `GameManager::get_World`
- 1x `WorldBase::GetPlayers`


## 15. ChunkManager.DetermineChunksToLoad call breakdown

### `ChunkManager::DetermineChunksToLoad` IL=448
- 5x `List`1::get_Item`
- 5x `BucketHashSetList::Clear`
- 5x `BucketHashSetList::RecalcHashSetList`
- 4x `List`1::get_Count`
- 3x `BucketHashSetList::Add`
- 3x `HashSetLong::UnionWithHashSetLong`
- 2x `Utils::Fastfloor`
- 2x `World::toChunkXZ`
- 2x `ConnectionManager::get_IsServer`
- 2x `HashSetLong::ExceptWithHashSetLong`
- 2x `Enumerator::get_Current`
- 2x `Enumerator::MoveNext`
- 2x `IDisposable::Dispose`
- 2x `Monitor::Enter`
- 2x `Monitor::Exit`
- 1x `ChunkManager::removeChunksToUnload`
- 1x `Vector3i::.ctor`
- 1x `Vector3i::op_Inequality`
- 1x `WorldChunkCache::MakeChunkKey`
- 1x `HashSetLong::Clear`
- 1x `BucketHashSetList::ExceptTarget`
- 1x `List`1::GetEnumerator`
- 1x `DateTime::get_UtcNow`
- 1x `ConcurrentDictionary`2::set_Item`
- 1x `List`1::CopyTo`
- 1x `WorldChunkCache::GetChunkKeysCopySync`
- 1x `HashSetLong::GetEnumerator`
- 1x `BucketHashSetList::Contains`
- 1x `ConcurrentHashSet`1::Contains`
- 1x `ChunkQueue::Contains`
- 1x `WorldChunkCache::GetChunkSync`
- 1x `HashSetList`1::Add`
- 1x `ChunkCluster::RemoveChunk`
- 1x `ChunkManager::recalcFreeChunkGameObjects`
- 1x `EventWaitHandle::Set`


## 16. GameTimer.updateTimer structure

### `GameTimer::updateTimer` IL=74
- 1x `GameTimer::Reset`
- 1x `Stopwatch::get_ElapsedMilliseconds`
- 1x `Time::get_timeScale`

constants floats: 
