# Optimization scan RE (V3.0.1)

**Kind:** auto dump notes (not primary narrative).  
**Prefer:** [`../../7dtd-optimizer/docs/OPTIMIZATION_CANDIDATES.md`](../../7dtd-optimizer/docs/OPTIMIZATION_CANDIDATES.md).  
**Raw IL:** [`../il/opt-scan-v3.0.1/`](../il/opt-scan-v3.0.1/).

Generated: 2026-07-16 10:19:44Z
Assembly: `/home/maci/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll`


## Largest methods (IL count): scan selected type name prefixes

- **4090** `DistantChunkMap::SetChunkTrigger(Int32)`
- **3604** `DynamicMeshConsoleCmd::Execute(List`1,CommandSenderInfo)`
- **2291** `BlockShapeNew::renderFace(Vector3i,BlockValue,Vector3,BlockFace,Vector3[],LightingAround,TextureFullArray,VoxelMesh[],MeshPurpose)`
- **2136** `Block::Init()`
- **2119** `DistantChunk::calculateEdgeInformation(Single,Single,Single,Int32,Single,Single,Single,Single,Single,Single,Single[])`
- **1778** `DynamicMeshFile::InitTiles()`
- **1662** `MeshGeneratorMC2::build(Vector3,Vector3i,Vector3i,VoxelMesh,Vector3i)`
- **1613** `MeshGeneratorPrefab::build(Vector3,Vector3i,Vector3i,VoxelMesh)`
- **1509** `EntityVehicle::PhysicsFixedUpdate()`
- **1447** `EntityClass::Init()`
- **1360** `MeshGeneratorMC2::BuildMipBorder(Int32,Int32,Int32&,Int32&,VoxelMesh)`
- **1344** `EntityVulture::updateTasks()`
- **1236** `EntityMoveHelper::UpdateMoveHelper()`
- **1208** `Prefab::UpdateInsideOutside(Vector3i,Vector3i)`
- **1122** `EntityAlive::CopyPropertiesFromEntityClass()`
- **1106** `BlockLiquidv2::UpdateTick(WorldBase,Vector3i,BlockValue,Boolean,UInt64,GameRandom)`
- **1083** `MeshGenerator::CreateMesh(Vector3i,Vector3,Vector3i,Vector3i,VoxelMesh[],Boolean,Boolean)`
- **1032** `ChunkProviderGenerateWorldFromRaw/<Init>d__17::MoveNext IL=1032`
- **1019** `MeshGenerator::RenderTopWater(BlockValue,Vector3[],VoxelMesh[],Vector3i,Vector3i,Boolean)`
- **961** `WorldEnvironment::CreateUnityTerrainOld(String,Int32,Int32,Int32,List`1,Int32,Single,Int32,Boolean,Action`1)`
- **918** `ChunkProviderGenerateWorldFromRaw/<processFiles>d__34::MoveNext IL=918`
- **903** `EntityAlive::ProcessDamageResponseLocal(DamageResponse)`
- **884** `WorldState::SaveLoad(Stream,Boolean,Boolean,Boolean)`
- **883** `WorldBiomeProviderFromImage::loadSplatMaps(String,Int32)`
- **879** `EntityPlayerLocal::OnUpdateLive()`
- **871** `WorldStaticData::.cctor()`
- **860** `AstarVoxelGrid::CheckHeights(Vector3)`
- **846** `EAIApproachAndAttackTarget::Update()`
- **834** `ItemActionConnectPower::OnHoldingUpdate(ItemActionData)`
- **829** `ActionBaseSpawn::OnPerformAction()`
- **828** `ChunkCluster::SetBlock(Vector3i,Boolean,BlockValue,Boolean,SByte,Boolean,Boolean,Boolean,Boolean,Int32)`
- **815** `GameManager/<StartAsServer>d__166::MoveNext IL=815`
- **812** `ConsoleCmdChunkReset/<execute>d__5::MoveNext IL=812`
- **775** `Chunk::read(PooledBinaryReader,UInt32,Boolean)`
- **774** `WorldDecoratorPOIFromImage/<InitData>d__15::MoveNext IL=774`
- **771** `BlocksFromXml::CreateBlock(Boolean,String,DynamicProperties)`
- **769** `DistantChunkMap::.ctor(Vector2,Single[],Single[],Int32[],Int32[],Int32[],Int32,DelegateGetTerrainHeight,WorldCreationData,GameObject,Vector3[])`
- **747** `MeshGeneratorMC2::ChooseTriangulation(Int32,Int32,Int32,Int32,Int32,UInt16[])`
- **742** `ChunkProviderGenerateWorldFromRaw/<FillOccupiedMap>d__42::MoveNext IL=742`
- **741** `DistantChunk::ActivateObject(Boolean)`
- **735** `EntityVehicle::OnCollisionForward(Transform,Collision,Boolean)`
- **721** `DynamicMeshFile/<ReadMeshTerrainCoroutine>d__58::MoveNext IL=721`
- **717** `DynamicMeshFile/<ReadMeshCoroutine>d__53::MoveNext IL=717`
- **715** `Prefab::CopyBlocksIntoChunkNoEntities(World,Chunk,Vector3i,Boolean,FastTags`1)`
- **705** `WorldBuilder::SmoothRoadTerrainTask$BurstManaged(Data&,NativeArray`1&,NativeArray`1&,Int32)`
- **700** `World/<LoadWorld>d__73::MoveNext IL=700`
- **694** `WorldBiomes::parseBiome(Byte,Byte,String,XElement,Boolean)`
- **685** `EntityPlayerLocal::guiDrawCrosshair(NGuiWdwInGameHUD,Boolean)`
- **680** `Prefab::CopyIntoLocal(ChunkCluster,Vector3i,Boolean,Boolean,FastTags`1)`
- **675** `EntityPlayerLocal::Update()`
- **670** `GameManager/<worldInfoCo>d__196::MoveNext IL=670`
- **667** `DistantChunk::calculateMeshTangents(DChunkSquareMesh)`
- **666** `BlockCollector::Init()`
- **665** `Prefab::readBlockData(PooledBinaryReader,UInt32,Int32[],Boolean)`
- **652** `WorldBuilder::generateTerrainFeature(String,GenerationSelections,Boolean)`
- **647** `PrefabPreviewManager::UpdateDisplay()`
- **639** `EntityFactory/CreateEntityOperation::CompleteEntity IL=639`
- **631** `GameManager::gmUpdate()`
- **629** `PrefabLODManager::UpdateDisplay(EntityPlayerLocal)`
- **628** `DistantChunkMap::ComputeChunkPos(Int32,Int32,Int32)`
- **627** `TileEntityCollector::read(PooledBinaryReader,StreamModeRead)`
- **623** `AstarVoxelGrid::RecalculateCell(Int32,Int32,Boolean,Boolean)`
- **620** `WorldGenerationFromXml/<Load>d__2::MoveNext IL=620`
- **616** `Chunk::OnDisplayBlockEntities(World,Transform,ChunkCluster)`
- **608** `DynamicMeshDebugConsoleCmd::Execute(List`1,CommandSenderInfo)`
- **608** `AstarVoxelGrid::CalculateConnections(Int32,Int32,Int32)`
- **607** `DistantChunkMap::createBaseDataMeshFold(DistantChunkMapInfo)`
- **606** `MeshGeneratorMC2::CreateMesh(Vector3i,Vector3,Vector3i,Vector3i,VoxelMesh[],Boolean,Boolean)`
- **603** `DynamicMeshChunkProcessor::CopyChunkFromWorld(Chunk,DynamicMeshChunkData,Boolean)`
- **601** `Chunk::write(PooledBinaryWriter,Boolean)`
- **588** `Prefab/<ToTransform>d__278::MoveNext IL=588`
- **578** `DynamicMeshManager::OnGUI()`
- **573** `World::ClipBoundsMove(Entity,Bounds,Vector3,Vector3,Single)`
- **553** `EntityPlayerLocal::SetMoveState(MoveState,Boolean)`
- **550** `ChunkCluster::chunkPosNeedsRegeneration(Chunk,Int32,Int32,Int32,Boolean)`
- **545** `EntityTrader::PopulateActiveQuests(EntityPlayer,Int32,Int32)`
- **541** `XUiC_VehicleFrameWindow::GetBindingValueInternal(String&,String)`
- **540** `ConsoleCmdServerJunkDrone::Execute(List`1,CommandSenderInfo)`
- **533** `VoxelMesh::AddQuadWithCracks(Vector3,Color,Vector3,Color,Vector3,Color,Vector3,Color,Rect,Rect,Boolean)`
- **532** `ChunkProviderGenerateFlat/<Init>d__9::MoveNext IL=532`

## Dumped method inventory

- `World::AddFallingBlocks` IL=18 → World_AddFallingBlocks_IList_1_calls.md
- `World::AddFallingBlock` IL=38 → World_AddFallingBlock_Vector3i_Boolean_calls.md
- `World::AddFallingBlocks` IL=18 → World_AddFallingBlocks_IList_1_calls.md
- `World::GroupFallingBlocks` IL=292 → World_GroupFallingBlocks_calls.md
- `World::CreateFallingBlockGroup` IL=107 → World_CreateFallingBlockGroup_List_1_calls.md
- `World::LetBlocksFall` IL=220 → World_LetBlocksFall_calls.md
- `World::GetClosestPlayer` IL=63 → World_GetClosestPlayer_Single_Single_Single_Int32_Double_calls.md
- `World::GetClosestPlayer` IL=7 → World_GetClosestPlayer_Entity_Single_Boolean_calls.md
- `World::GetClosestPlayer` IL=57 → World_GetClosestPlayer_Vector3_Single_Boolean_calls.md
- `World::GetClosestPlayerSeen` IL=68 → World_GetClosestPlayerSeen_EntityAlive_Single_Single_calls.md
- `World::GetEntitiesInBounds` IL=75 → World_GetEntitiesInBounds_Entity_Bounds_calls.md
- `World::GetEntitiesInBounds` IL=75 → World_GetEntitiesInBounds_Entity_Bounds_Boolean_calls.md
- `World::GetEntitiesInBounds` IL=68 → World_GetEntitiesInBounds_FastTags_1_Bounds_List_1_calls.md
- `World::GetEntitiesInBounds` IL=69 → World_GetEntitiesInBounds_Type_Bounds_List_1_calls.md
- `World::TickSleeperVolumes` IL=34 → World_TickSleeperVolumes_calls.md
- `World::ClearCaches` IL=13 → World_ClearCaches_calls.md
- `World::SaveWorldState` IL=16 → World_SaveWorldState_calls.md
- `WorldBlockTicker::Tick` IL=20 → WorldBlockTicker_Tick_ArraySegment_1_EntityPlayer_GameRandom_calls.md
- `WorldBlockTicker::tickScheduled` IL=151 → WorldBlockTicker_tickScheduled_GameRandom_calls.md
- `WorldBlockTicker::tickRandom` IL=97 → WorldBlockTicker_tickRandom_ArraySegment_1_GameRandom_calls.md
- `WorldBlockTicker::tickChunkRandom` IL=97 → WorldBlockTicker_tickChunkRandom_Chunk_GameRandom_calls.md
- `WorldBlockTicker::tickScheduled` IL=151 → WorldBlockTicker_tickScheduled_GameRandom_calls.md
- `WorldBlockTicker::tickRandom` IL=97 → WorldBlockTicker_tickRandom_ArraySegment_1_GameRandom_calls.md
- `SpawnManagerBiomes::Update` IL=9 → SpawnManagerBiomes_Update_String_Boolean_Object_calls.md
- `SpawnManagerBiomes::SpawnUpdate` IL=441 → SpawnManagerBiomes_SpawnUpdate_String_Boolean_ChunkAreaBiomeSpawnData_calls.md
- `SpawnManagerBiomes::SpawnUpdate` IL=441 → SpawnManagerBiomes_SpawnUpdate_String_Boolean_ChunkAreaBiomeSpawnData_calls.md
- `SpawnManagerBiomes::Update` IL=9 → SpawnManagerBiomes_Update_String_Boolean_Object_calls.md
- `SpawnManagerBiomes::SpawnUpdate` IL=441 → SpawnManagerBiomes_SpawnUpdate_String_Boolean_ChunkAreaBiomeSpawnData_calls.md
- `AIDirector::ComponentsTick` IL=21 → AIDirector_ComponentsTick_Double_calls.md
- `AIDirector::Tick` IL=6 → AIDirector_Tick_Double_calls.md
- `AIDirector::ComponentsTick` IL=21 → AIDirector_ComponentsTick_Double_calls.md
- `AIDirector::DebugTick` IL=7 → AIDirector_DebugTick_calls.md
- `AIDirector::DebugTick` IL=7 → AIDirector_DebugTick_calls.md
- `SleeperVolume::Tick` IL=137 → SleeperVolume_Tick_World_calls.md
- `SleeperVolume::get_IsTriggerAndNoRespawn` IL=14 → SleeperVolume_get_IsTriggerAndNoRespawn_calls.md
- `SleeperVolume::UpdatePlayerTouched` IL=172 → SleeperVolume_UpdatePlayerTouched_World_EntityPlayer_calls.md
- `SleeperVolume::CheckTouching` IL=165 → SleeperVolume_CheckTouching_World_EntityPlayer_calls.md
- `DecoManager::UpdateTick` IL=330 → DecoManager_UpdateTick_World_calls.md
- `DecoManager::UpdateTick` IL=330 → DecoManager_UpdateTick_World_calls.md
- `DecoManager::UpdateDecorationsCo` IL=6 → DecoManager_UpdateDecorationsCo_calls.md
- `ChunkManager::SendChunksToClients` IL=216 → ChunkManager_SendChunksToClients_calls.md
- `ChunkManager::ResendChunksToClients` IL=55 → ChunkManager_ResendChunksToClients_HashSetLong_calls.md
- `ChunkManager::DetermineChunksToLoad` IL=448 → ChunkManager_DetermineChunksToLoad_calls.md
- `ChunkManager::CopyChunksToUnity` IL=13 → ChunkManager_CopyChunksToUnity_calls.md
- `ChunkManager::doCopyChunksToUnity` IL=252 → ChunkManager_doCopyChunksToUnity_calls.md
- `ChunkManager::GroundAlignFrameUpdate` IL=42 → ChunkManager_GroundAlignFrameUpdate_calls.md
- `ChunkManager::ReloadAllChunks` IL=41 → ChunkManager_ReloadAllChunks_calls.md
- `NetEntityDistribution::OnUpdateEntities` IL=322 → NetEntityDistribution_OnUpdateEntities_calls.md
- `NetEntityDistributionEntry::updatePlayerEntity` IL=222 → NetEntityDistributionEntry_updatePlayerEntity_EntityPlayer_calls.md
- `NetEntityDistributionEntry::updatePlayerEntities` IL=19 → NetEntityDistributionEntry_updatePlayerEntities_List_1_calls.md
- `NetEntityDistributionEntry::updatePlayerList` IL=509 → NetEntityDistributionEntry_updatePlayerList_List_1_calls.md
- `NetEntityDistributionEntry::SendFullUpdateNextTick` IL=4 → NetEntityDistributionEntry_SendFullUpdateNextTick_calls.md
- `NetEntityDistributionEntry::updatePlayerList` IL=509 → NetEntityDistributionEntry_updatePlayerList_List_1_calls.md
- `NetEntityDistributionEntry::updatePlayerEntity` IL=222 → NetEntityDistributionEntry_updatePlayerEntity_EntityPlayer_calls.md
- `NetEntityDistributionEntry::SendToPlayers` IL=42 → NetEntityDistributionEntry_SendToPlayers_NetPackage_Int32_Boolean_Int32_calls.md
- `EntityAlive::FindPath` IL=49 → EntityAlive_FindPath_Vector3_Single_Boolean_EAIBase_calls.md
- `EntityAlive::updateTasks` IL=125 → EntityAlive_updateTasks_calls.md
- `EntityAlive::OnUpdateLive` IL=363 → EntityAlive_OnUpdateLive_calls.md
- `EntityAlive::GetSpeedModifier` IL=3 → EntityAlive_GetSpeedModifier_calls.md
- `EntityPlayer::OnUpdateLive` IL=13 → EntityPlayer_OnUpdateLive_calls.md
- `EntityPlayer::OnUpdateEntity` IL=176 → EntityPlayer_OnUpdateEntity_calls.md
- `PathNavigate::UpdateNavigation` IL=1 → PathNavigate_UpdateNavigation_calls.md
- `PathNavigate::SetPath` IL=2 → PathNavigate_SetPath_PathInfo_Single_calls.md
- `PathNavigate::GetPathTo` IL=1 → PathNavigate_GetPathTo_PathInfo_calls.md
- `PathNavigate::GetPathToEntity` IL=1 → PathNavigate_GetPathToEntity_PathInfo_EntityAlive_calls.md
- `ASPPathNavigate::UpdateNavigation` IL=21 → ASPPathNavigate_UpdateNavigation_calls.md
- `ASPPathNavigate::GetPathTo` IL=19 → ASPPathNavigate_GetPathTo_PathInfo_calls.md
- `ASPPathNavigate::CreatePath` IL=38 → ASPPathNavigate_CreatePath_calls.md
- `AstarManager::UpdateGraphs` IL=185 → AstarManager_UpdateGraphs_Single_calls.md
- `AstarManager::Init` IL=18 → AstarManager_Init_GameObject_calls.md
- `AstarManager::OriginChanged` IL=34 → AstarManager_OriginChanged_calls.md
- `DynamicMeshServer::Update` IL=452 → DynamicMeshServer_Update_calls.md
- `DynamicMeshManager::UpdateDistantTerrainBounds` IL=116 → DynamicMeshManager_UpdateDistantTerrainBounds_TileArea_1_Config_calls.md
- `DynamicMeshManager::UpdateDynamicPrefabDecoratorRegions` IL=56 → DynamicMeshManager_UpdateDynamicPrefabDecoratorRegions_DynamicMeshRegion_calls.md
- `DynamicMeshManager::UpdateDynamicPrefabDecoratorRegion` IL=120 → DynamicMeshManager_UpdateDynamicPrefabDecoratorRegion_DynamicMeshRegion_calls.md
- `DynamicMeshManager::OriginUpdate` IL=10 → DynamicMeshManager_OriginUpdate_calls.md
- `DynamicMeshManager::Update` IL=404 → DynamicMeshManager_Update_calls.md
- `DynamicMeshManager::AddUpdateData` IL=16 → DynamicMeshManager_AddUpdateData_Vector3i_Boolean_Boolean_calls.md
- `DynamicMeshManager::AddUpdateData` IL=14 → DynamicMeshManager_AddUpdateData_Int32_Int32_Boolean_Boolean_calls.md
- `DynamicMeshManager::AddUpdateData` IL=138 → DynamicMeshManager_AddUpdateData_Int64_Boolean_Boolean_Boolean_Int32_calls.md
- `DynamicMeshManager::ProcessItemMeshGeneration` IL=6 → DynamicMeshManager_ProcessItemMeshGeneration_calls.md
- `DynamicMeshManager::ProcessChunkRegionRequests` IL=6 → DynamicMeshManager_ProcessChunkRegionRequests_calls.md
- `ConnectionManager::ProcessPackages` IL=116 → ConnectionManager_ProcessPackages_INetConnection_NetPackageDirection_ClientInfo_calls.md
- `ConnectionManager::FlushClientSendQueues` IL=28 → ConnectionManager_FlushClientSendQueues_calls.md
- `ConnectionManager::UpdatePings` IL=20 → ConnectionManager_UpdatePings_calls.md
- `ConnectionManager::SendPackage` IL=168 → ConnectionManager_SendPackage_List_1_Boolean_Int32_Int32_Int32_Nullable_1_Int32_Boolean_calls.md
- `ConnectionManager::SendPackage` IL=100 → ConnectionManager_SendPackage_NetPackage_Boolean_Int32_Int32_Int32_Nullable_1_Int32_Boolean_calls.md
- `GameTimer::updateTimer` IL=74 → GameTimer_updateTimer_Boolean_calls.md
- `GameTimer::Reset` IL=21 → GameTimer_Reset_UInt64_calls.md
- MISSING `EntityActivity`
- `WaterSplashCubes::Update` IL=185 → WaterSplashCubes_Update_calls.md
- `MultiBlockManager::MainThreadUpdate` IL=5 → MultiBlockManager_MainThreadUpdate_calls.md
- `MultiBlockManager::UpdateTrackedBlockData` IL=126 → MultiBlockManager_UpdateTrackedBlockData_Vector3i_BlockValue_Boolean_calls.md
- `MultiBlockManager::MainThreadUpdate` IL=5 → MultiBlockManager_MainThreadUpdate_calls.md
- `MultiBlockManager::UpdateAlignment` IL=60 → MultiBlockManager_UpdateAlignment_calls.md
- `MultiBlockManager::UpdateOversizedStability` IL=65 → MultiBlockManager_UpdateOversizedStability_calls.md
- `MultiBlockManager::UpdateProfilerCounters` IL=1 → MultiBlockManager_UpdateProfilerCounters_calls.md
- `MultiBlockManager::<UpdateAlignment>g__AllOverlappedChunksAreReady|46_0` IL=56 → MultiBlockManager__UpdateAlignment_g__AllOverlappedChunksAreReady|46_0_RectInt_calls.md
- `MultiBlockManager::<UpdateAlignment>g__TryAlignBlock|46_1` IL=54 → MultiBlockManager__UpdateAlignment_g__TryAlignBlock|46_1_Vector3i_TrackedBlockData_calls.md
- `MultiBlockManager::<UpdateOversizedStability>g__AllOverlappedChunksAreSyncedAndInitialized|61_0` IL=45 → MultiBlockManager__UpdateOversizedStability_g__AllOverlappedChunksAreSyncedAndInitialized|61_0_RectInt_calls.md
- `MultiBlockManager::<UpdateOversizedStability>g__IsOversizedBlockStable|61_1` IL=93 → MultiBlockManager__UpdateOversizedStability_g__IsOversizedBlockStable|61_1_Vector3i_TrackedBlockData_calls.md
- `PowerManager::SetTileEntityUpdate` IL=14 → PowerManager_SetTileEntityUpdate_TileEntityPoweredBlock_Boolean_calls.md
- `PowerManager::Update` IL=106 → PowerManager_Update_calls.md
- `VehicleManager::Update` IL=297 → VehicleManager_Update_calls.md
- `VehicleManager::UpdateVehicleWaypoints` IL=22 → VehicleManager_UpdateVehicleWaypoints_calls.md
- `VehicleManager::UpdateVehicleWaypointsForPlayer` IL=69 → VehicleManager_UpdateVehicleWaypointsForPlayer_Int32_calls.md
- `DroneManager::Update` IL=305 → DroneManager_Update_calls.md
- `DroneManager::UpdateWaypointsForAllPlayers` IL=22 → DroneManager_UpdateWaypointsForAllPlayers_calls.md
- `DroneManager::UpdateWaypointsForPlayer` IL=96 → DroneManager_UpdateWaypointsForPlayer_Int32_calls.md
- `FactionManager::Update` IL=43 → FactionManager_Update_calls.md
- `QuestEventManager::Update` IL=127 → QuestEventManager_Update_calls.md
- `QuestEventManager::AddObjectiveToBeUpdated` IL=10 → QuestEventManager_AddObjectiveToBeUpdated_BaseObjective_calls.md
- `QuestEventManager::RemoveObjectiveToBeUpdated` IL=11 → QuestEventManager_RemoveObjectiveToBeUpdated_BaseObjective_calls.md
- `QuestEventManager::AddObjectiveToBeUpdated` IL=10 → QuestEventManager_AddObjectiveToBeUpdated_BaseChallengeObjective_calls.md
- `QuestEventManager::RemoveObjectiveToBeUpdated` IL=11 → QuestEventManager_RemoveObjectiveToBeUpdated_BaseChallengeObjective_calls.md
- `QuestEventManager::AddTrackerToBeUpdated` IL=10 → QuestEventManager_AddTrackerToBeUpdated_TrackingHandler_calls.md
- `QuestEventManager::RemoveTrackerToBeUpdated` IL=11 → QuestEventManager_RemoveTrackerToBeUpdated_TrackingHandler_calls.md
- `QuestEventManager::AddTrackerToBeUpdated` IL=4 → QuestEventManager_AddTrackerToBeUpdated_ChallengeTrackingHandler_calls.md
- `QuestEventManager::RemoveTrackerToBeUpdated` IL=4 → QuestEventManager_RemoveTrackerToBeUpdated_ChallengeTrackingHandler_calls.md
- `QuestEventManager::SubscribeToUpdateEvent` IL=48 → QuestEventManager_SubscribeToUpdateEvent_Int32_Vector3_calls.md
- `QuestEventManager::UnSubscribeToUpdateEvent` IL=61 → QuestEventManager_UnSubscribeToUpdateEvent_Int32_Vector3_calls.md
- `QuestEventManager::UpdateBlocks` IL=6 → QuestEventManager_UpdateBlocks_List_1_calls.md
- `QuestEventManager::UpdateTreasureBlocksPerReduction` IL=23 → QuestEventManager_UpdateTreasureBlocksPerReduction_Int32_Int32_calls.md
- `GameEventManager::Update` IL=25 → GameEventManager_Update_Single_calls.md
- `GameEventManager::HandleSpawnUpdates` IL=148 → GameEventManager_HandleSpawnUpdates_Single_calls.md
- `GameEventManager::HandleActionUpdates` IL=79 → GameEventManager_HandleActionUpdates_calls.md
- `GameEventManager::HandleBlockUpdates` IL=53 → GameEventManager_HandleBlockUpdates_Single_calls.md
- `GameEventManager::SendBlockDamageUpdate` IL=32 → GameEventManager_SendBlockDamageUpdate_Vector3i_calls.md
- `GameEventManager::HandleEventFlagUpdates` IL=58 → GameEventManager_HandleEventFlagUpdates_Single_calls.md
- `GameEventManager::HandleFlagBuffUpdates` IL=69 → GameEventManager_HandleFlagBuffUpdates_GameEventFlagTypes_Single_calls.md
- `GameEventManager::UpdateBossGroupType` IL=54 → GameEventManager_UpdateBossGroupType_Int32_BossGroupTypes_calls.md
- `GameEventManager::HandleBossGroupUpdates` IL=66 → GameEventManager_HandleBossGroupUpdates_Single_calls.md
- `GameEventManager::UpdateCurrentBossGroup` IL=95 → GameEventManager_UpdateCurrentBossGroup_EntityPlayerLocal_calls.md
- `ThreadManager::UpdateMainThreadTasks` IL=64 → ThreadManager_UpdateMainThreadTasks_calls.md
- `ThreadManager::add_LateUpdateEv` IL=18 → ThreadManager_add_LateUpdateEv_Action_calls.md
- `ThreadManager::remove_LateUpdateEv` IL=18 → ThreadManager_remove_LateUpdateEv_Action_calls.md
- `ThreadManager::LateUpdate` IL=7 → ThreadManager_LateUpdate_calls.md
- `MemoryPools::Cleanup` IL=55 → MemoryPools_Cleanup_calls.md
- MISSING `Physics`

## ASPPathFinderThread nested state machine methods

- nested `GamePath.ASPPathFinderThread/<FindPaths>d__8`
  - `.ctor` IL=6 → _FindPaths_d__8_.ctor_Int32_calls.md
  - `System.IDisposable.Dispose` IL=1 → _FindPaths_d__8_System.IDisposable.Dispose_calls.md
  - `MoveNext` IL=87 → _FindPaths_d__8_MoveNext_calls.md
  - `System.Collections.Generic.IEnumerator<System.Object>.get_Current` IL=3 → _FindPaths_d__8_System.Collections.Generic.IEnumerator_System.Object_.get_Current_calls.md
  - `System.Collections.IEnumerator.Reset` IL=2 → _FindPaths_d__8_System.Collections.IEnumerator.Reset_calls.md
  - `System.Collections.IEnumerator.get_Current` IL=3 → _FindPaths_d__8_System.Collections.IEnumerator.get_Current_calls.md

## AStarPathFinderThread.thread_Pathfinder (exists, not default Init)

- `thread_Pathfinder` IL=109
- `IsCalculatingPath` IL=21
- `FindPath` IL=42
- `GetPath` IL=35
- `RemovePathsFor` IL=30

## Cross-refs (callers)

### Callers of `World::GetClosestPlayer`

- `AIDirectorChunkEventComponent::SpawnScouts`
- `EntityAlive::CheckDespawn`
- `EntityVulture::FindTarget`
- `QuestEventManager::BlockDestroyed`
- `World::EntityActivityUpdate`
- `World::GetClosestPlayer`

### Callers of `World::AddFallingBlock`

- `EntityAlive::updateCurrentBlockPosAndValue`
- `MultiBlockManager::UpdateOversizedStability`
- `World::AddFallingBlocks`
- `ActionBlockTriggerFall::ProcessChanges`

### Callers of `World::AddFallingBlocks`


### Callers of `World::GetEntitiesInBounds`

- `BlockSpawnEntity::UpdateTick`
- `TEFeatureStorage::UpdateTick`
- `AutoTurretFireController::findTarget`
- `MiniTurretFireController::findTarget`
- `MotionSensorController::hasTarget`
- `SpinningBladeTrapBladeController::Update`
- `Entity::OnUpdateEntity`
- `AIDirector::DebugSendNameInfo`
- `AIDirector::DebugSendLatency`
- `AIHordeSpawner::Tick`
- `EAIBreakBlock::AttackBlock`
- `EAIDodge::CanExecute`
- `EAIManager::FallHitGround`
- `EAIRunawayFromEntity::FindEnemy`
- `EAISetNearestEntityAsTarget::FindTarget`
- `EntityFallingBlock::OnUpdateEntity`
- `EntityFallingBlocks::OnUpdateEntity`
- `EntityHomerunGoal::Update`
- `EntityItem::tickDistraction`
- `EntityTrader::OnUpdateLive`
- `EntityVulture::updateTasks`
- `HasTrackedEntity::IsValid`
- `ObjectiveInteractWithNPC::AddHooks`
- `SpawnManagerBiomes::SpawnUpdate`
- `TraderArea::GetTrader`
- `World::GetCollidingBounds`
- `PlayerMoveController::FindCameraSnapTarget`
- `UAIBase::addEntityTargetsToConsider`
- `RequirementNearbyEntities::CanPerform`
- `HomerunGoalController::Update`

### Callers of `EntityAlive::FindPath`

- `EAIApproachAndAttackTarget::Update`
- `EAIApproachDistraction::updatePath`
- `EAIApproachSpot::updatePath`
- `EAIDestroyArea::Continue`
- `EAIRunAway::Update`
- `EAITerritorial::Start`
- `EAIWander::Start`
- `UAITaskFleeFromTarget::Start`
- `UAITaskMoveToTarget::Start`
- `UAITaskWander::Start`

### Callers of `GameManager::get_IsDedicatedServer`

- `DismembermentManager::SpawnParticleEffect`
- `BlockCollector::OnBlockDestroyedBy`
- `BlockParticle::Init`
- `BlockParticle::OnBlockLoaded`
- `BlockParticle::removeParticles`

### Field `aiActiveScale` ops

- `EntityAlive::updateTasks` ldfld
- `World::EntityActivityUpdate` stfld

### Field `fallingBlocks` ops

- `World::.ctor` stfld
- `World::ClearFallingBlocksForChunks` ldfld
- `World::AddFallingBlock` ldfld
- `World::LetBlocksFall` ldfld

### Calls matching `GC::Collect`

- `Block::LateInitAll` → `GC::Collect`
- `ConsoleCmdMem::Execute` → `GC::Collect`
- `DynamicMeshConsoleCmd::Execute` → `GC::Collect`
- `EntityAnimalRabbit::OnEntityActivated` → `Entity::Collect`
- `EntityDrone::pickup` → `Entity::Collect`
- `EntityItem::OnEntityActivated` → `Entity::Collect`
- `EntityTurret::OnEntityActivated` → `Entity::Collect`
- `EntityVehicle::OnEntityActivated` → `Entity::Collect`
- `OcclusionManager::WriteListToDisk` → `GC::Collect`
- `GameManager::gmUpdate` → `GC::Collect`
- `GameManager::Cleanup` → `GC::Collect`
- `GameManager::PlayerDisconnected` → `GC::Collect`
- `GameManager::ReportUnusedAssets` → `GC::Collect`
- `WorldStaticData::CollectGarbage` → `GC::Collect`
- `GCUtils::PostUnload` → `GC::Collect`

### Calls matching `Physics::SyncTransforms`

- `GameManager::gmUpdate` → `Physics::SyncTransforms`
- `vp_FPController::FixedMove` → `Physics::SyncTransforms`
- `vp_FPController::SmoothMove` → `Physics::SyncTransforms`
- `vp_FPController::SetPosition` → `Physics::SyncTransforms`
- `KinematicCharacterSystem::Simulate` → `Physics::SyncTransforms`

### Calls matching `GetClosestPlayer`

- `AIDirectorChunkEventComponent::SpawnScouts` → `World::GetClosestPlayer`
- `EntityAlive::CheckDespawn` → `World::GetClosestPlayer`
- `EntityVulture::FindTarget` → `World::GetClosestPlayer`
- `QuestEventManager::BlockDestroyed` → `World::GetClosestPlayer`
- `World::EntityActivityUpdate` → `World::GetClosestPlayer`
- `World::GetClosestPlayer` → `World::GetClosestPlayer`

### Calls matching `SendChunksToClients`

- `GameManager::UpdateTick` → `ChunkManager::SendChunksToClients`


## newobj density in selected hot methods (alloc pressure hint)

- `EntityAlive::updateTasks` IL=125 newobj=0 box=0 calls=20
- `EntityAlive::OnUpdateLive` IL=363 newobj=0 box=0 calls=40
- `EntityAlive::OnUpdateEntity` IL=417 newobj=0 box=0 calls=39
- `World::TickEntities` IL=117 newobj=0 box=0 calls=13
- `World::TickEntity` IL=148 newobj=0 box=0 calls=23
- `World::EntityActivityUpdate` IL=229 newobj=1 box=0 calls=32
- `World::LetBlocksFall` IL=220 newobj=0 box=0 calls=42
- `World::OnUpdateTick` IL=189 newobj=0 box=0 calls=44
- `EAITaskList::OnUpdateTasks` IL=137 newobj=0 box=0 calls=17
- `NetEntityDistribution::OnUpdateEntities` IL=322 newobj=0 box=0 calls=47
- `DecoManager::UpdateTick` IL=330 newobj=1 box=0 calls=49
- `ChunkManager::SendChunksToClients` IL=216 newobj=0 box=0 calls=37
- `GameManager::gmUpdate` IL=631 newobj=1 box=2 calls=182
- `GameManager::UpdateTick` IL=150 newobj=0 box=0 calls=29
- `ConnectionManager::Update` IL=215 newobj=2 box=0 calls=40
- `DynamicMeshManager::Update` IL=404 newobj=1 box=0 calls=83
- `ASPPathFinderThread::FindPath` IL=17 newobj=1 box=0 calls=2
- `ASPPathFinderThread::FindPath` IL=22 newobj=1 box=0 calls=3
- `ASPPathFinderThread::FindPath` IL=14 newobj=0 box=0 calls=2
- `AStarPathFinderThread::thread_Pathfinder` IL=109 newobj=0 box=0 calls=20

## Interesting static/instance fields (name heuristics)

- `CharacterConstruct::gearPathLookup` : Dictionary`2
- `CharacterConstruct::headgearPathLookup` : Dictionary`2
- `AvatarController::sleeperPoseHash` : Int32
- `AvatarController::sleeperTriggerHash` : Int32
- `AvatarController::sleeperIdleSitHash` : Int32
- `AvatarController::sleeperIdleSideRightHash` : Int32
- `AvatarController::sleeperIdleSideLeftHash` : Int32
- `AvatarController::sleeperIdleBackHash` : Int32
- `AvatarController::sleeperIdleStomachHash` : Int32
- `AvatarController::sleeperIdleStandHash` : Int32
- `AvatarController::cSleeperPoseMove` : Int32
- `AvatarController::cSleeperPoseAwake` : Int32
- `AvatarController::cSleeperPoseSit` : Int32
- `AvatarController::cSleeperPoseSideRight` : Int32
- `AvatarController::cSleeperPoseSideLeft` : Int32
- `AvatarController::cSleeperPoseBack` : Int32
- `AvatarController::cSleeperPoseStomach` : Int32
- `AvatarController::cSleeperPoseStand` : Int32
- `DismembermentManager::cGibCapsMatPath` : String
- `DismembermentManager::cGibCapsMatRadPath` : String
- `DismembermentManager::cDebugAxisPath` : String
- `DismemberedPartData::prefabPath` : String
- `DismemberedPartData::particlePaths` : String[]
- `DismemberedPartData::dismemberMatPath` : String
- `Block::PropCanMobsSpawnOn` : String
- `Block::PropCanPlayersSpawnOn` : String
- `Block::CanMobsSpawnOn` : Boolean
- `Block::CanPlayersSpawnOn` : Boolean
- `Block::cPathScan` : Int32
- `Block::cPathSolid` : Int32
- `Block::PathType` : Int32
- `Block::PathOffsetX` : Single
- `Block::PathOffsetZ` : Single
- `Block::IsSleeperBlock` : Boolean
- `BlockQuestActivate::cMetaSpawned` : Int32
- `BlockSleeper::PropSpawnGroup` : String
- `BlockSleeper::PropSpawnMode` : String
- `BlockSleeper::spawnGroup` : String
- `BlockSleeper::spawnMode` : eMode
- `BlockSpawnEntity::spawnClasses` : String[]
- `BlockShapeModelEntity::cMissingPrefabEntityPath` : String
- `BlockShapeModelEntity::modelNameWithPath` : String
- `BlockShapeNew::boundsPathOffsetRotations` : Vector2[]
- `ConsoleCmdCreateWebUser::registrationPagePath` : String
- `ConsoleCmdPathTest::aiPathTest` : EAIPathTest
- `ConsoleCmdPathTest::recalculatePath` : Boolean
- `ConsoleCmdPlayerVisitMap::logFilePath` : String
- `DynamicMeshManager::NextFallingCheck` : DateTime
- `DynamicMeshSettings::_maxViewDistance` : Int32
- `WaveCleanUp::FilePath` : String
- `Entity::bWillRespawn` : Boolean
- `Entity::spawnerSource` : EnumSpawnerSource
- `Entity::spawnerSourceBiomeIdHash` : Int32
- `Entity::spawnerSourceChunkKey` : Int64
- `Entity::IsDespawned` : Boolean
- `Entity::spawnByAllowShare` : Boolean
- `Entity::spawnById` : Int32
- `Entity::spawnByName` : String
- `AIAirDrop::kSpawnYUp` : Int32
- `AIAirDrop::flightPaths` : List`1
- `AIAirDrop::spawningCrates` : Boolean
- `AIDirector::bloodMoonComponent` : AIDirectorBloodMoonComponent
- `AIDirectorBloodMoonComponent::cSpawnDelay` : Single
- `AIDirectorBloodMoonComponent::isBloodMoon` : Boolean
- `AIDirectorBloodMoonComponent::BloodMoonFrequency` : Int32
- `AIDirectorBloodMoonComponent::BloodMoonRange` : Int32
- `AIDirectorBloodMoonComponent::BloodMoonEnemyCount` : Int32
- `AIDirectorBloodMoonParty::cSpawnPreferredArc` : Int32
- `AIDirectorBloodMoonParty::cSpawnAngle` : Single
- `AIDirectorBloodMoonParty::cSpawnDistance` : Single
- `AIDirectorBloodMoonParty::cSpawnMinRandDistance` : Int32
- `AIDirectorBloodMoonParty::cSpawnMaxRandDistance` : Int32
- `AIDirectorBloodMoonParty::cSpawnMinPlayerDistance` : Int32
- `AIDirectorBloodMoonParty::partySpawner` : AIDirectorGameStagePartySpawner
- `AIDirectorBloodMoonParty::spawnWorld` : World
- `AIDirectorBloodMoonParty::spawnBasePos` : Vector3
- `AIDirectorBloodMoonParty::spawnBaseDir` : Int32
- `AIDirectorBloodMoonParty::spawnDirectionV` : Vector3
- `AIDirectorBloodMoonParty::bonusLootSpawnCount` : Int32
- `AIDirectorChunkEventComponent::cActivityLevelToSpawn` : Single
- `AIDirectorChunkEventComponent::cSpawnChance` : Single
- `AIDirectorChunkEventComponent::scoutSpawnList` : List`1
- `AIDirectorChunkEventComponent::hordeSpawnList` : List`1
- `AIDirectorChunkEventComponent::spawnDelay` : Single
- `AIDirectorConstants::kHordeDaySpawnRangeMin` : Int32
- `AIDirectorConstants::kHordeDaySpawnRangeMax` : Int32
- `AIDirectorConstants::kHordeNightSpawnRangeMin` : Int32
- `AIDirectorConstants::kHordeNightSpawnRangeMax` : Int32
- `AIDirectorConstants::kSpawnWanderingHordeMin` : Int32
- `AIDirectorConstants::kSpawnWanderingHordeMax` : Int32
- `AIDirectorConstants::kWanderingHordeSpawnDistance` : Single
- `AIDirectorConstants::kWanderingHordeSpawnMinDistance` : Single
- `AIDirectorConstants::kScoutSpawnDistance` : Int32
- `AIDirectorConstants::kScoutSpawnAnotherScoutChance` : Single
- `AIDirectorGameStagePartySpawner::stageSpawnMax` : Int32
- `AIDirectorGameStagePartySpawner::spawnGroup` : SpawnGroup
- `AIDirectorGameStagePartySpawner::spawnCount` : Int32
- `AIDirectorGameStagePartySpawner::numToSpawn` : Int32
- `AIDirectorWanderingHordeComponent::spawners` : List`1
- `AIHordeSpawner::spawner` : AIDirectorGameStagePartySpawner
- `AIHordeSpawner::numToSpawn` : Int32
