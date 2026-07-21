# Gap-closing RE notes (V3.0.1)

**Kind:** auto dump notes (not primary narrative).  
**Prefer:** [`closed-gaps.md`](closed-gaps.md).  
**Raw IL:** [`../il/gaps-v3.0.1/`](../il/gaps-v3.0.1/).

UTC: 2026-07-16 10:36:51Z


## 1. GameTimer fields and initialization

### Fields of `GameTimer`
- `elapsedPartialTicks` : System.Single
- `elapsedTicks` : System.Int32
- `elapsedTicksD` : System.Double
- `lastMillis` : System.Int64
- `m_Instance` : GameTimer [static]
- `ms` : MicroStopwatch
- `ticks` : System.UInt64
- `ticksPerSecond` : System.Single
- `ticksSincePlayfieldLoaded` : System.UInt64

- dump `GameTimer::.ctor` IL=13
  - 1x `Object::.ctor`
  - 1x `new MicroStopwatch::.ctor`
  - 1x `GameTimer::Reset`
- dump `GameTimer::updateTimer` IL=74
  - 1x `GameTimer::Reset`
  - 1x `Stopwatch::get_ElapsedMilliseconds`
  - 1x `Time::get_timeScale`
- dump `GameTimer::Reset` IL=21
  - 1x `MicroStopwatch::ResetAndRestart`
- dump `GameTimer::get_Instance` IL=7
  - 1x `new GameTimer::.ctor`
- dump `GameTimer::get_Instance` IL=7
  - 1x `new GameTimer::.ctor`
### `GameTimer::.ctor` IL=13
- IL_0001 call System.Void System.Object::.ctor()
- IL_0008 stfld System.Single GameTimer::ticksPerSecond
- IL_0013 stfld MicroStopwatch GameTimer::ms
- IL_001B call System.Void GameTimer::Reset(System.UInt64)

## 2. AIDirector construction and component registration

- dump `AIDirector::.ctor` IL=16
  - 1x `new DictionaryList`2::.ctor`
  - 1x `new List`1::.ctor`
  - 1x `Object::.ctor`
  - 1x `AIDirector::CreateComponents`
  - 1x `AIDirector::Init`
- dump `AIDirector::.cctor` IL=9
  - 2x `new List`1::.ctor`
  - 1x `new MemoryStream::.ctor`
- dump `AIDirector::Init` IL=7
  - 1x `GameRandomManager::get_Instance`
  - 1x `GameRandomManager::CreateGameRandom`
  - 1x `AIDirector::ComponentsInitNewGame`
- dump `AIDirector::ComponentsInitNewGame` IL=20
  - 1x `List`1::get_Item`
  - 1x `AIDirectorComponent::InitNewGame`
  - 1x `List`1::get_Count`
- dump `AIDirector::CreateComponents` IL=31
  - 6x `AIDirector::CreateComponent`
  - 3x `AIDirector::GetComponent`
- dump `AIDirector::CreateComponent` IL=27
  - 1x `Type::GetTypeFromHandle`
  - 1x `Type::get_FullName`
  - 1x `Dictionary`2::ContainsKey`
  - 1x `new Exception::.ctor`
  - 1x `Activator::CreateInstance`
  - 1x `DictionaryList`2::Add`
- dump `AIDirector::AddEntity` IL=10
  - 1x `Object::op_Implicit`
  - 1x `AIDirector::AddPlayer`
- dump `AIDirector::AddPlayer` IL=9
  - 1x `AIDirectorPlayerManagementComponent::AddPlayer`
  - 1x `AIDirector::get_BloodMoonComponent`
  - 1x `AIDirectorBloodMoonComponent::AddPlayer`
- dump `AIDirector::Tick` IL=6
  - 1x `AIDirector::ComponentsTick`
  - 1x `AIDirector::DebugTick`
- dump `AIDirector::ComponentsTick` IL=21
  - 1x `List`1::get_Item`
  - 1x `AIDirectorComponent::Tick`
  - 1x `List`1::get_Count`
- dump `AIDirector::DebugTick` IL=7
  - 1x `List`1::get_Count`
  - 1x `AIDirector::DebugSendNameInfo`
- dump `AIDirector::ComponentsTick` IL=21
  - 1x `List`1::get_Item`
  - 1x `AIDirectorComponent::Tick`
  - 1x `List`1::get_Count`
#### newobj `AIDirector`
- `WorldState::SetFrom`
#### newobj `AIDirectorBloodMoonComponent`
#### newobj `AIDirectorChunkEventComponent`
#### newobj `AIDirectorWanderingHordeComponent`
#### newobj `AIDirectorAirDropComponent`
#### newobj `AIDirectorPlayerManagementComponent`
#### callers of `AIDirector::.ctor`
- `WorldState::SetFrom`
#### callers of `AIDirector::Tick`
- `World::OnUpdateTick`
### Fields of `AIDirector`
- `bloodMoonComponent` : AIDirectorBloodMoonComponent
- `cActivityDuration` : System.Single = 720 [static]
- `cActivityNoiseDuration` : System.Single = 240 [static]
- `cDebugSendNameInfoTickRate` : System.Int32 = 5 [static]
- `chunkEventComponent` : AIDirectorChunkEventComponent
- `cLatencyName` : System.String = DebugLatency [static]
- `components` : DictionaryList`2<System.String,AIDirectorComponent>
- `debugEntities` : System.Collections.Generic.List`1<Entity>
- `debugFreezePos` : System.Boolean [static]
- `debugNameInfoTicks` : System.Int32
- `debugSendLatencyToPlayerIds` : System.Collections.Generic.List`1<System.Int32> [static]
- `debugSendNameInfoToPlayerIds` : System.Collections.Generic.List`1<System.Int32> [static]
- `HeatMapSensitivityModifier` : System.Single [static]
- `latencyStream` : System.IO.MemoryStream [static]
- `playerManagementComponent` : AIDirectorPlayerManagementComponent
- `random` : GameRandom
- `World` : World


## 3. ASPPathNavigate path compute

- dump `ASPPathNavigate::GetPathTo` IL=19
  - 1x `ASPPathFinder::Cancel`
  - 1x `PathNavigate::canNavigate`
  - 1x `PathNavigate::CreatePath`
- dump `ASPPathNavigate::pathFollow` IL=160
  - 3x `Vector3::op_Subtraction`
  - 2x `PathPoint::ProjectToGround`
  - 2x `VectorMath::ClosestPointOnSegment`
  - 2x `Vector3::get_sqrMagnitude`
  - 2x `PathEntity::setCurrentPathIndex`
  - 1x `PathEntity::get_CurrentPoint`
  - 1x `Utils::FastAbs`
  - 1x `Entity::get_radius`
  - 1x `PathEntity::getCurrentPathIndex`
  - 1x `PathEntity::getCurrentPathLength`
  - 1x `Entity::IsInElevator`
  - 1x `Utils::FastMax`
  - 1x `PathEntity::get_NextPoint`
  - 1x `Plane::.ctor`
  - 1x `Plane::SameSide`
- dump `ASPPathNavigate::CreatePath` IL=38
  - 2x `PathFinder::Calculate`
  - 1x `new ASPPathFinder::.ctor`
  - 1x `Vector3::op_Multiply`
  - 1x `Vector3::op_Addition`
- dump `ASPPathNavigate::UpdateNavigation` IL=21
  - 2x `PathNavigate::noPath`
  - 1x `ASPPathNavigate::pathFollow`
  - 1x `EntityMoveHelper::SetMoveTo`
- dump `ASPPathNavigate::SetPath` IL=46
  - 2x `PathEntity::Destruct`
  - 1x `PathEntity::getCurrentPathLength`
  - 1x `ASPPathNavigate::ImprovePath`
- dump `PathNavigate::GetPathTo` IL=1
- dump `PathNavigate::GetPathToEntity` IL=1
- dump `PathNavigate::UpdateNavigation` IL=1
- dump `PathNavigate::SetPath` IL=2
- dump `PathNavigate::noPath` IL=9
  - 1x `PathEntity::isFinished`
- dump `PathNavigate::noPathAndNotPlanningOne` IL=13
  - 1x `PathNavigate::noPath`
  - 1x `PathFinderThread::IsCalculatingPath`
- dump `ASPPathFinder::Calculate` IL=333
  - 5x `Vector3::op_Subtraction`
  - 3x `new OnPathDelegate::.ctor`
  - 2x `List`1::ToArray`
  - 2x `MultiTargetPath::Construct`
  - 2x `new TraversalProviderNoBreak::.ctor`
  - 1x `Object::op_Equality`
  - 1x `XPath::Construct`
  - 1x `ABPath::Construct`
  - 1x `RandomPath::Construct`
  - 1x `FleePath::Construct`
  - 1x `Entity::get_height`
  - 1x `new TraversalProvider::.ctor`
  - 1x `GameRandom::get_RandomFloat`
  - 1x `AstarPath::StartPath`
### type `GamePath.AStarPathFinderThread` base=PathFinderThread
- `thread_Pathfinder` IL=109
- `FindPath` IL=42
- `GetPath` IL=35
- `RemovePathsFor` IL=30
- `Cleanup` IL=24
- `IsCalculatingPath` IL=21
- `.ctor` IL=15
- `StartWorkerThreads` IL=14
- `GetQueueCount` IL=5
- `GetFinishedCount` IL=4

### type `GamePath.ASPPathFinder` base=PathFinder
- `OnPathFinished` IL=461
- `Calculate` IL=333
- `IsLineClear` IL=85
- `.ctor` IL=21
- `Cancel` IL=7

### type `GamePath.ASPPathFinderThread` base=PathFinderThread
- `FindPath` IL=22
- `GetPath` IL=19
- `FindPath` IL=17
- `FindPath` IL=14
- `.ctor` IL=11
- `Cleanup` IL=11
- `RemovePathsFor` IL=10
- `StartWorkerThreads` IL=7
- `FindPaths` IL=6
- `GetQueueCount` IL=5
- `IsCalculatingPath` IL=5
- `GetFinishedCount` IL=4

### type `GamePath.PathFinder` base=Object
- `.ctor` IL=15
- `Calculate` IL=1
- `Destruct` IL=1

### type `GamePath.PathFinderThread` base=Object
- `.ctor` IL=3
- `GetFinishedCount` IL=2
- `GetQueueCount` IL=2
- `IsCalculatingPath` IL=2
- `GetPath` IL=2
- `StartWorkerThreads` IL=1
- `Cleanup` IL=1
- `FindPath` IL=1
- `FindPath` IL=1
- `FindPath` IL=1
- `RemovePathsFor` IL=1


## 4. NetEntityDistributionEntry.updatePlayerList structure

### Annotated `NetEntityDistributionEntry::updatePlayerList` IL=509

```
IL_0001: ldfld System.Boolean NetEntityDistributionEntry::firstUpdateDone
IL_0006: brfalse.s IL_0020
IL_0009: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_000F: ldfld UnityEngine.Vector3 NetEntityDistributionEntry::lastTrackedEntityPos
IL_0014: callvirt System.Single Entity::GetDistanceSq(UnityEngine.Vector3)
IL_0019: ldc.r4 16
IL_001E: ble.un.s IL_003F
IL_0022: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0027: ldfld UnityEngine.Vector3 Entity::position
IL_003A: call System.Void NetEntityDistributionEntry::updatePlayerEntities(System.Collections.Generic.List`1<EntityPlayer>)
IL_0040: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0045: ldfld System.Boolean Entity::usePhysicsMaster
IL_004A: brfalse.s IL_0091
IL_004D: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0052: ldfld System.Boolean Entity::isPhysicsMaster
IL_0057: brfalse.s IL_0090
IL_005B: ldfld System.Int32 NetEntityDistributionEntry::updateCounter
IL_006B: ldfld System.Int32 NetEntityDistributionEntry::updatTickCounter
IL_0071: brtrue.s IL_0090
IL_0074: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0079: callvirt NetPackageEntityPhysics Entity::PhysicsMasterSetupBroadcast()
IL_0080: brfalse.s IL_0090
IL_0086: ldc.i4 192
IL_008B: call System.Void NetEntityDistributionEntry::SendToPlayers(NetPackage,System.Int32,System.Boolean,System.Int32)
IL_0090: ret
IL_0093: ldfld System.Int32 NetEntityDistributionEntry::sendFullUpdateAfterTicks
IL_00A0: ldfld System.Int32 NetEntityDistributionEntry::priorityLevel
IL_00A5: brfalse.s IL_00B4
IL_00A8: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_00AD: callvirt System.Boolean Entity::IsAirBorne()
IL_00B2: br.s IL_00B5
IL_00B7: ldfld System.Int32 NetEntityDistributionEntry::priorityLevel
IL_00BC: brfalse.s IL_00C1
IL_00BF: br.s IL_00C2
IL_00C5: ldfld System.Int32 NetEntityDistributionEntry::updateCounter
IL_00D2: brtrue.s IL_0126
IL_00D5: ldfld System.Int32 NetEntityDistributionEntry::priorityLevel
IL_00DE: switch IL_00F1,IL_0106,IL_0116
IL_00EF: br.s IL_0126
IL_00F2: ldfld System.Int32 NetEntityDistributionEntry::updateCounter
IL_00F8: ldfld System.Int32 NetEntityDistributionEntry::updatTickCounter
IL_0104: br.s IL_0126
IL_0107: ldfld System.Int32 NetEntityDistributionEntry::updateCounter
IL_0114: br.s IL_0126
IL_0117: ldfld System.Int32 NetEntityDistributionEntry::updateCounter
IL_011C: ldc.i4.s 10
IL_0123: ldc.i4.s 10
IL_0127: brfalse IL_05BF
IL_012D: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0132: ldfld UnityEngine.Vector3 Entity::position
IL_0137: call Vector3i NetEntityDistributionEntry::EncodePos(UnityEngine.Vector3)
IL_0141: ldfld Vector3i NetEntityDistributionEntry::encodedPos
IL_0146: call Vector3i Vector3i::op_Subtraction(Vector3i,Vector3i)
IL_014F: ldfld System.Int32 Vector3i::x
IL_0155: call System.Single Utils::FastAbs(System.Single)
IL_015A: ldc.r4 2
IL_015F: bge.s IL_01A1
IL_0163: ldfld System.Int32 Vector3i::y
IL_0169: call System.Single Utils::FastAbs(System.Single)
IL_016E: ldc.r4 2
IL_0173: bge.s IL_01A1
IL_0177: ldfld System.Int32 Vector3i::z
IL_017D: call System.Single Utils::FastAbs(System.Single)
IL_0182: ldc.r4 2
IL_0187: bge.s IL_01A1
IL_018A: ldfld System.Boolean NetEntityDistributionEntry::encodedOnGround
IL_0190: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0195: ldfld System.Boolean Entity::onGround
IL_019F: br.s IL_01A2
IL_01A5: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_01AA: ldfld UnityEngine.Vector3 Entity::rotation
IL_01AF: call Vector3i NetEntityDistributionEntry::EncodeRot(UnityEngine.Vector3)
IL_01B9: ldfld Vector3i NetEntityDistributionEntry::encodedRot
IL_01BE: call Vector3i Vector3i::op_Subtraction(Vector3i,Vector3i)
IL_01C7: ldfld System.Int32 Vector3i::x
IL_01CD: call System.Single Utils::FastAbs(System.Single)
IL_01D2: ldc.r4 2
IL_01D7: bge.s IL_0206
IL_01DB: ldfld System.Int32 Vector3i::y
IL_01E1: call System.Single Utils::FastAbs(System.Single)
IL_01E6: ldc.r4 2
IL_01EB: bge.s IL_0206
IL_01EF: ldfld System.Int32 Vector3i::z
IL_01F5: call System.Single Utils::FastAbs(System.Single)
IL_01FA: ldc.r4 2
IL_0204: br.s IL_0207
IL_0210: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0215: ldfld System.Boolean Entity::IsMovementReplicated
IL_021A: brfalse IL_03E0
IL_0220: ldfld System.Int32 NetEntityDistributionEntry::updatTickCounter
IL_0226: bne.un.s IL_0236
IL_0229: ldc.i4 2147483647
IL_0238: ldfld System.Int32 Vector3i::x
IL_023D: ldc.i4 -256
IL_0242: blt.s IL_028A
IL_0246: ldfld System.Int32 Vector3i::x
IL_024B: ldc.i4 256
IL_0250: bge.s IL_028A
IL_0254: ldfld System.Int32 Vector3i::y
IL_0259: ldc.i4 -256
IL_025E: blt.s IL_028A
IL_0262: ldfld System.Int32 Vector3i::y
IL_0267: ldc.i4 256
IL_026C: bge.s IL_028A
IL_0270: ldfld System.Int32 Vector3i::z
IL_0275: ldc.i4 -256
IL_027A: blt.s IL_028A
IL_027E: ldfld System.Int32 Vector3i::z
IL_0283: ldc.i4 256
IL_0288: blt.s IL_02A8
IL_0291: call TPackage NetPackageManager::GetPackage<NetPackageEntityTeleport>()
IL_0297: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_029C: callvirt NetPackageEntityTeleport NetPackageEntityTeleport::Setup(Entity)
IL_02A3: br IL_03E0
IL_02AA: ldfld System.Int32 Vector3i::x
IL_02AF: ldc.i4.s -128
IL_02B1: blt.s IL_02FD
IL_02B5: ldfld System.Int32 Vector3i::x
IL_02BA: ldc.i4 128
IL_02BF: bge.s IL_02FD
IL_02C3: ldfld System.Int32 Vector3i::y
IL_02C8: ldc.i4.s -128
IL_02CA: blt.s IL_02FD
IL_02CE: ldfld System.Int32 Vector3i::y
IL_02D3: ldc.i4 128
IL_02D8: bge.s IL_02FD
IL_02DC: ldfld System.Int32 Vector3i::z
IL_02E1: ldc.i4.s -128
IL_02E3: blt.s IL_02FD
IL_02E7: ldfld System.Int32 Vector3i::z
IL_02EC: ldc.i4 128
IL_02F1: bge.s IL_02FD
IL_02F4: ldfld System.Int32 NetEntityDistributionEntry::sendFullUpdateAfterTicks
IL_02F9: ldc.i4.s 100
IL_02FB: ble.s IL_031B
IL_0304: call TPackage NetPackageManager::GetPackage<NetPackageEntityPosAndRot>()
IL_030A: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_030F: callvirt NetPackageEntityPosAndRot NetPackageEntityPosAndRot::Setup(Entity)
IL_0316: br IL_03E0
IL_0320: brfalse.s IL_0364
IL_0322: call TPackage NetPackageManager::GetPackage<NetPackageEntityRelPosAndRot>()
IL_0328: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_032D: ldfld System.Int32 Entity::entityId
IL_0337: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_033C: ldfld UnityEngine.Quaternion Entity::qrotation
IL_0342: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0347: ldfld System.Boolean Entity::onGround
IL_034D: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0352: callvirt System.Boolean Entity::IsQRotationUsed()
IL_0358: callvirt NetPackageEntityRelPosAndRot NetPackageEntityRelPosAndRot::Setup(System.Int32,Vector3i,Vector3i,UnityEngine.Quaternion,System.Boolean,System.Boolean,System.Int32)
IL_0362: br.s IL_03E0
IL_0366: brfalse.s IL_03AA
IL_0368: call TPackage NetPackageManager::GetPackage<NetPackageEntityRelPosAndRot>()
IL_036E: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0373: ldfld System.Int32 Entity::entityId
IL_037D: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0382: ldfld UnityEngine.Quaternion Entity::qrotation
IL_0388: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_038D: ldfld System.Boolean Entity::onGround
IL_0393: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0398: callvirt System.Boolean Entity::IsQRotationUsed()
IL_039E: callvirt NetPackageEntityRelPosAndRot NetPackageEntityRelPosAndRot::Setup(System.Int32,Vector3i,Vector3i,UnityEngine.Quaternion,System.Boolean,System.Boolean,System.Int32)
IL_03A8: br.s IL_03E0
IL_03AC: brfalse.s IL_03E0
IL_03AE: call TPackage NetPackageManager::GetPackage<NetPackageEntityRotation>()
IL_03B4: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_03B9: ldfld System.Int32 Entity::entityId
IL_03C1: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_03C6: ldfld UnityEngine.Quaternion Entity::qrotation
IL_03CC: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_03D1: callvirt System.Boolean Entity::IsQRotationUsed()
IL_03D6: callvirt NetPackageEntityRotation NetPackageEntityRotation::Setup(System.Int32,Vector3i,UnityEngine.Quaternion,System.Boolean)
IL_03E1: ldfld System.Boolean NetEntityDistributionEntry::shouldSendMotionUpdates
IL_03E6: brfalse IL_046F
IL_03EC: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_03F1: ldfld UnityEngine.Vector3 Entity::motion
IL_03F7: ldfld UnityEngine.Vector3 NetEntityDistributionEntry::lastTrackedEntityMotion
IL_03FC: call UnityEngine.Vector3 UnityEngine.Vector3::op_Subtraction(UnityEngine.Vector3,UnityEngine.Vector3)
IL_0405: call System.Single UnityEngine.Vector3::get_sqrMagnitude()
IL_040E: ldc.r4 0.04
IL_0413: bgt.s IL_0435
IL_0417: ldc.r4 0
IL_041C: ble.un.s IL_046F
IL_041F: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0429: call UnityEngine.Vector3 UnityEngine.Vector3::get_zero()
IL_042E: call System.Boolean UnityEngine.Vector3::Equals(UnityEngine.Vector3)
IL_0433: brfalse.s IL_046F
IL_0437: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_043C: ldfld UnityEngine.Vector3 Entity::motion
IL_0447: call TPackage NetPackageManager::GetPackage<NetPackageEntityVelocity>()
IL_044D: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0452: ldfld System.Int32 Entity::entityId
IL_0458: ldfld UnityEngine.Vector3 NetEntityDistributionEntry::lastTrackedEntityMotion
IL_045E: callvirt NetPackageEntityVelocity NetPackageEntityVelocity::Setup(System.Int32,UnityEngine.Vector3,System.Boolean)
IL_0465: ldc.i4 192
IL_046A: call System.Void NetEntityDistributionEntry::SendToPlayers(NetPackage,System.Int32,System.Boolean,System.Int32)
IL_0471: brfalse.s IL_0484
IL_047A: ldfld System.Int32 NetEntityDistributionEntry::trackingDistanceThreshold
IL_047F: call System.Void NetEntityDistributionEntry::SendToPlayers(NetPackage,System.Int32,System.Boolean,System.Int32)
IL_0485: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0494: call System.Boolean UnityEngine.Object::op_Inequality(UnityEngine.Object,UnityEngine.Object)
IL_0499: brfalse.s IL_04CF
IL_049D: ldfld System.Boolean EntityAlive::bEntityAliveFlagsChanged
IL_04A2: brfalse.s IL_04CF
IL_04A5: call TPackage NetPackageManager::GetPackage<NetPackageEntityAliveFlags>()
IL_04AC: callvirt NetPackageEntityAliveFlags NetPackageEntityAliveFlags::Setup(EntityAlive)
IL_04B2: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_04B7: ldfld System.Int32 Entity::entityId
IL_04BD: ldc.i4 192
IL_04C2: call System.Void NetEntityDistributionEntry::SendToPlayers(NetPackage,System.Int32,System.Boolean,System.Int32)
IL_04D0: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_04DF: call System.Boolean UnityEngine.Object::op_Inequality(UnityEngine.Object,UnityEngine.Object)
IL_04E4: brfalse.s IL_051A
IL_04E8: ldfld System.Boolean EntityAlive::bPlayerStatsChanged
IL_04ED: brfalse.s IL_051A
IL_04F0: call TPackage NetPackageManager::GetPackage<NetPackagePlayerStats>()
IL_04F7: callvirt NetPackagePlayerStats NetPackagePlayerStats::Setup(EntityAlive)
IL_04FD: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0502: ldfld System.Int32 Entity::entityId
IL_0508: ldc.i4 192
IL_050D: call System.Void NetEntityDistributionEntry::SendToPlayers(NetPackage,System.Int32,System.Boolean,System.Int32)
IL_051D: call System.Boolean UnityEngine.Object::op_Inequality(UnityEngine.Object,UnityEngine.Object)
IL_0522: brfalse.s IL_0558
IL_0526: ldfld System.Boolean EntityAlive::bPlayerTwitchChanged
IL_052B: brfalse.s IL_0558
IL_052E: call TPackage NetPackageManager::GetPackage<NetPackagePlayerTwitchStats>()
IL_0535: callvirt NetPackagePlayerTwitchStats NetPackagePlayerTwitchStats::Setup(EntityAlive)
IL_053B: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0540: ldfld System.Int32 Entity::entityId
IL_0546: ldc.i4 192
IL_054B: call System.Void NetEntityDistributionEntry::SendToPlayers(NetPackage,System.Int32,System.Boolean,System.Int32)
IL_055B: call System.Boolean UnityEngine.Object::op_Inequality(UnityEngine.Object,UnityEngine.Object)
IL_0560: brfalse.s IL_0596
IL_0564: ldfld System.Boolean EntityAlive::bPlayerEquipmentChanged
IL_0569: brfalse.s IL_0596
IL_056C: call TPackage NetPackageManager::GetPackage<NetPackagePlayerEquipment>()
IL_0573: callvirt NetPackagePlayerEquipment NetPackagePlayerEquipment::Setup(EntityAlive)
IL_0579: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_057E: ldfld System.Int32 Entity::entityId
IL_0584: ldc.i4 192
IL_0589: call System.Void NetEntityDistributionEntry::SendToPlayers(NetPackage,System.Int32,System.Boolean,System.Int32)
IL_0598: brfalse.s IL_05B3
IL_05A4: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_05A9: ldfld System.Boolean Entity::onGround
IL_05B5: brfalse.s IL_05BF
IL_05C0: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_05C6: callvirt System.Void Entity::SetAirBorne(System.Boolean)
IL_05CB: ret
```

### Annotated `NetEntityDistributionEntry::updatePlayerEntity` IL=222

```
IL_0002: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0007: call System.Boolean UnityEngine.Object::op_Equality(UnityEngine.Object,UnityEngine.Object)
IL_000C: brfalse.s IL_000F
IL_000E: ret
IL_0015: ldfld System.Single UnityEngine.Vector3::x
IL_0020: ldfld System.Int32 Vector3i::x
IL_0025: ldc.i4.s 32
IL_0030: ldfld System.Single UnityEngine.Vector3::z
IL_003B: ldfld System.Int32 Vector3i::z
IL_0040: ldc.i4.s 32
IL_004D: ldfld System.Int32 NetEntityDistributionEntry::trackingDistanceThreshold
IL_0053: ldfld System.Int32 NetEntityDistributionEntry::trackingDistanceThreshold
IL_005F: brfalse IL_0228
IL_0065: ldfld System.Collections.Generic.HashSet`1<EntityPlayer> NetEntityDistributionEntry::trackedPlayers
IL_006B: callvirt System.Boolean System.Collections.Generic.HashSet`1<EntityPlayer>::Contains(!0)
IL_0070: brtrue IL_027B
IL_0076: ldfld System.Collections.Generic.HashSet`1<EntityPlayer> NetEntityDistributionEntry::trackedPlayers
IL_007C: callvirt System.Boolean System.Collections.Generic.HashSet`1<EntityPlayer>::Add(!0)
IL_0082: ldsfld T SingletonMonoBehaviour`1<ConnectionManager>::Instance
IL_0088: call NetPackage NetEntityDistributionEntry::getSpawnPacket()
IL_008F: ldfld System.Int32 Entity::entityId
IL_009F: ldc.i4 192
IL_00A5: callvirt System.Void ConnectionManager::SendPackage(NetPackage,System.Boolean,System.Int32,System.Int32,System.Int32,System.Nullable`1<UnityEngine.Vector3>,System.Int32,System.Boolean)
IL_00AB: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_00B7: call System.Boolean UnityEngine.Object::op_Implicit(UnityEngine.Object)
IL_00BC: brfalse IL_0180
IL_00C1: ldsfld T SingletonMonoBehaviour`1<ConnectionManager>::Instance
IL_00C6: call TPackage NetPackageManager::GetPackage<NetPackageEntityAliveFlags>()
IL_00CC: callvirt NetPackageEntityAliveFlags NetPackageEntityAliveFlags::Setup(EntityAlive)
IL_00D3: ldfld System.Int32 Entity::entityId
IL_00E3: ldc.i4 192
IL_00E9: callvirt System.Void ConnectionManager::SendPackage(NetPackage,System.Boolean,System.Int32,System.Int32,System.Int32,System.Nullable`1<UnityEngine.Vector3>,System.Int32,System.Boolean)
IL_00F4: brfalse IL_0180
IL_00F9: ldsfld T SingletonMonoBehaviour`1<ConnectionManager>::Instance
IL_00FE: call TPackage NetPackageManager::GetPackage<NetPackagePlayerStats>()
IL_0104: callvirt NetPackagePlayerStats NetPackagePlayerStats::Setup(EntityAlive)
IL_010B: ldfld System.Int32 Entity::entityId
IL_011B: ldc.i4 192
IL_0121: callvirt System.Void ConnectionManager::SendPackage(NetPackage,System.Boolean,System.Int32,System.Int32,System.Int32,System.Nullable`1<UnityEngine.Vector3>,System.Int32,System.Boolean)
IL_0126: ldsfld T SingletonMonoBehaviour`1<ConnectionManager>::Instance
IL_012B: call TPackage NetPackageManager::GetPackage<NetPackagePlayerTwitchStats>()
IL_0131: callvirt NetPackagePlayerTwitchStats NetPackagePlayerTwitchStats::Setup(EntityAlive)
IL_0138: ldfld System.Int32 Entity::entityId
IL_0148: ldc.i4 192
IL_014E: callvirt System.Void ConnectionManager::SendPackage(NetPackage,System.Boolean,System.Int32,System.Int32,System.Int32,System.Nullable`1<UnityEngine.Vector3>,System.Int32,System.Boolean)
IL_0153: ldsfld T SingletonMonoBehaviour`1<ConnectionManager>::Instance
IL_0158: call TPackage NetPackageManager::GetPackage<NetPackagePlayerEquipment>()
IL_015E: callvirt NetPackagePlayerEquipment NetPackagePlayerEquipment::Setup(EntityAlive)
IL_0165: ldfld System.Int32 Entity::entityId
IL_0175: ldc.i4 192
IL_017B: callvirt System.Void ConnectionManager::SendPackage(NetPackage,System.Boolean,System.Int32,System.Int32,System.Int32,System.Nullable`1<UnityEngine.Vector3>,System.Int32,System.Boolean)
IL_0181: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0186: ldfld EModelBase Entity::emodel
IL_018C: brtrue.s IL_0191
IL_018F: br.s IL_01A7
IL_0191: ldfld AvatarController EModelBase::avatarController
IL_0197: brtrue.s IL_019C
IL_019A: br.s IL_01A7
IL_019D: ldfld System.Int32 Entity::entityId
IL_01A2: call System.Void AvatarController::SyncAnimParameters(System.Int32)
IL_01A7: ldsfld T SingletonMonoBehaviour`1<ConnectionManager>::Instance
IL_01AC: call TPackage NetPackageManager::GetPackage<NetPackageEntitySpeeds>()
IL_01B2: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_01B7: callvirt NetPackageEntitySpeeds NetPackageEntitySpeeds::Setup(Entity)
IL_01BE: ldfld System.Int32 Entity::entityId
IL_01CE: ldc.i4 192
IL_01D4: callvirt System.Void ConnectionManager::SendPackage(NetPackage,System.Boolean,System.Int32,System.Int32,System.Int32,System.Nullable`1<UnityEngine.Vector3>,System.Int32,System.Boolean)
IL_01DA: ldfld System.Boolean NetEntityDistributionEntry::shouldSendMotionUpdates
IL_01DF: brfalse IL_027B
IL_01E4: ldsfld T SingletonMonoBehaviour`1<ConnectionManager>::Instance
IL_01E9: call TPackage NetPackageManager::GetPackage<NetPackageEntityVelocity>()
IL_01EF: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_01F4: ldfld System.Int32 Entity::entityId
IL_01FA: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_01FF: ldfld UnityEngine.Vector3 Entity::motion
IL_0205: callvirt NetPackageEntityVelocity NetPackageEntityVelocity::Setup(System.Int32,UnityEngine.Vector3,System.Boolean)
IL_020C: ldfld System.Int32 Entity::entityId
IL_021C: ldc.i4 192
IL_0222: callvirt System.Void ConnectionManager::SendPackage(NetPackage,System.Boolean,System.Int32,System.Int32,System.Int32,System.Nullable`1<UnityEngine.Vector3>,System.Int32,System.Boolean)
IL_0227: ret
IL_0229: ldfld System.Collections.Generic.HashSet`1<EntityPlayer> NetEntityDistributionEntry::trackedPlayers
IL_022F: callvirt System.Boolean System.Collections.Generic.HashSet`1<EntityPlayer>::Contains(!0)
IL_0234: brfalse.s IL_027B
IL_0237: ldfld System.Collections.Generic.HashSet`1<EntityPlayer> NetEntityDistributionEntry::trackedPlayers
IL_023D: callvirt System.Boolean System.Collections.Generic.HashSet`1<EntityPlayer>::Remove(!0)
IL_0243: ldsfld T SingletonMonoBehaviour`1<ConnectionManager>::Instance
IL_0248: call TPackage NetPackageManager::GetPackage<NetPackageEntityRemove>()
IL_024E: ldfld Entity NetEntityDistributionEntry::trackedEntity
IL_0253: ldfld System.Int32 Entity::entityId
IL_0259: callvirt NetPackageEntityRemove NetPackageEntityRemove::Setup(System.Int32,EnumRemoveEntityReason)
IL_0260: ldfld System.Int32 Entity::entityId
IL_0270: ldc.i4 192
IL_0276: callvirt System.Void ConnectionManager::SendPackage(NetPackage,System.Boolean,System.Int32,System.Int32,System.Int32,System.Nullable`1<UnityEngine.Vector3>,System.Int32,System.Boolean)
IL_027B: ret
```

### Annotated `NetEntityDistributionEntry::EncodePos` IL=20

```
IL_0001: ldfld System.Single UnityEngine.Vector3::x
IL_0006: ldc.r4 32
IL_000C: ldc.r4 0.5
IL_0013: ldfld System.Single UnityEngine.Vector3::y
IL_0018: ldc.r4 32
IL_001E: ldc.r4 0.5
IL_0025: ldfld System.Single UnityEngine.Vector3::z
IL_002A: ldc.r4 32
IL_0030: ldc.r4 0.5
IL_0036: newobj System.Void Vector3i::.ctor(System.Single,System.Single,System.Single)
IL_003B: ret
```

### Annotated `NetEntityDistributionEntry::EncodeRot` IL=7

```
IL_0001: ldc.r4 256
IL_0006: call UnityEngine.Vector3 UnityEngine.Vector3::op_Multiply(UnityEngine.Vector3,System.Single)
IL_000B: ldc.r4 360
IL_0010: call UnityEngine.Vector3 UnityEngine.Vector3::op_Division(UnityEngine.Vector3,System.Single)
IL_0015: newobj System.Void Vector3i::.ctor(UnityEngine.Vector3)
IL_001A: ret
```


## 5. Entity dedicated activity signals

- dump `Entity::OnAddedToWorld` IL=1
- dump `Entity::SetDead` IL=54
  - 3x `Component::get_gameObject`
  - 2x `Object::op_Inequality`
  - 2x `GameObject::set_layer`
  - 1x `Manager::DestroySoundsForEntity`
  - 1x `IAIDirectorMarker::Release`
  - 1x `EModelBase::HasRagdoll`
  - 1x `Object::op_Implicit`
  - 1x `GameObject::SetActive`
  - 1x `EModelBase::SetDead`
- dump `Entity::updateTransform` IL=183
  - 7x `Component::get_transform`
  - 5x `Time::get_deltaTime`
  - 4x `Transform::get_position`
  - 3x `Vector3::op_Subtraction`
  - 3x `Vector3::Lerp`
  - 3x `Transform::set_position`
  - 3x `Vector3::get_up`
  - 2x `Object::op_Inequality`
  - 2x `Object::op_Implicit`
  - 2x `Transform::get_eulerAngles`
  - 2x `new Vector3::.ctor`
  - 2x `Transform::set_eulerAngles`
  - 1x `Entity::ApplyFixedUpdate`
  - 1x `EModelBase::get_IsRagdollOn`
  - 1x `Time::get_fixedDeltaTime`
  - 1x `Vector3::Dot`
  - 1x `Quaternion::AngleAxis`
  - 1x `Quaternion::op_Multiply`
  - 1x `Mathf::Atan2`
  - 1x `Mathf::DeltaAngle`
- dump `Entity::get_positionUpdateMovementType` IL=2
- dump `Entity::Update` IL=105
  - 2x `Enumerator::get_Current`
  - 2x `KeyValuePair`2::get_Value`
  - 2x `Enumerator::MoveNext`
  - 2x `IDisposable::Dispose`
  - 1x `Entity::IsDead`
  - 1x `Entity::animateYaw`
  - 1x `Entity::PhysicsMasterTargetFrameUpdate`
  - 1x `Entity::updateTransform`
  - 1x `new MovableSharedChunkObserver::.ctor`
  - 1x `MovableSharedChunkObserver::SetPosition`
  - 1x `MovableSharedChunkObserver::Dispose`
  - 1x `Dictionary`2::get_Count`
  - 1x `new List`1::.ctor`
  - 1x `Dictionary`2::GetEnumerator`
  - 1x `Handle::IsPlaying`
  - 1x `Handle::Stop`
  - 1x `KeyValuePair`2::get_Key`
  - 1x `List`1::Add`
  - 1x `List`1::GetEnumerator`
  - 1x `Dictionary`2::Remove`
- dump `Entity::updateTransform` IL=183
  - 7x `Component::get_transform`
  - 5x `Time::get_deltaTime`
  - 4x `Transform::get_position`
  - 3x `Vector3::op_Subtraction`
  - 3x `Vector3::Lerp`
  - 3x `Transform::set_position`
  - 3x `Vector3::get_up`
  - 2x `Object::op_Inequality`
  - 2x `Object::op_Implicit`
  - 2x `Transform::get_eulerAngles`
  - 2x `new Vector3::.ctor`
  - 2x `Transform::set_eulerAngles`
  - 1x `Entity::ApplyFixedUpdate`
  - 1x `EModelBase::get_IsRagdollOn`
  - 1x `Time::get_fixedDeltaTime`
  - 1x `Vector3::Dot`
  - 1x `Quaternion::AngleAxis`
  - 1x `Quaternion::op_Multiply`
  - 1x `Mathf::Atan2`
  - 1x `Mathf::DeltaAngle`
- dump `Entity::FixedUpdate` IL=71
  - 3x `Object::op_Implicit`
  - 2x `Vector3::op_Multiply`
  - 1x `Entity::ApplyFixedUpdate`
  - 1x `Rigidbody::get_velocity`
  - 1x `Rigidbody::set_velocity`
  - 1x `Rigidbody::get_angularVelocity`
  - 1x `Rigidbody::set_angularVelocity`
  - 1x `Vector3::op_Addition`
  - 1x `Transform::get_position`
  - 1x `Vector3::Lerp`
  - 1x `Transform::get_rotation`
  - 1x `Quaternion::Euler`
  - 1x `Quaternion::Slerp`
  - 1x `Transform::SetPositionAndRotation`
  - 1x `EntityAlive::CrouchHeightFixedUpdate`
- dump `Entity::ApplyFixedUpdate` IL=77
  - 2x `Transform::get_position`
  - 2x `Vector3::op_Subtraction`
  - 2x `Transform::get_rotation`
  - 1x `Object::op_Implicit`
  - 1x `Vector3::get_sqrMagnitude`
  - 1x `Vector3::op_Addition`
  - 1x `Entity::SetPosition`
  - 1x `Transform::set_position`
  - 1x `Component::get_transform`
  - 1x `Vector3::Distance`
  - 1x `Quaternion::Angle`
  - 1x `Mathf::Abs`
  - 1x `Quaternion::get_eulerAngles`
- dump `Entity::PhysicsMasterTargetFrameUpdate` IL=52
  - 1x `Time::get_deltaTime`
  - 1x `Vector3::Lerp`
  - 1x `Entity::SetPosition`
  - 1x `Quaternion::Lerp`
  - 1x `Vector3::op_Subtraction`
  - 1x `Rigidbody::set_position`
  - 1x `Rigidbody::set_rotation`
- dump `Entity::CalcFixedUpdateTimeScaleConstants` IL=6
  - 1x `Time::get_deltaTime`
- dump `Entity::UpdateFall` IL=43
  - 1x `Entity::fallHitGround`
- dump `Entity::OnUpdatePosition` IL=225
  - 3x `Object::op_Implicit`
  - 3x `Entity::SetPosition`
  - 3x `Mathf::LerpAngle`
  - 1x `EModelBase::get_IsRagdollOn`
  - 1x `Entity::get_positionUpdateMovementType`
  - 1x `Vector3::MoveTowards`
  - 1x `Time::get_deltaTime`
  - 1x `Time::get_fixedDeltaTime`
  - 1x `Vector3::Lerp`
  - 1x `Vector3::op_Equality`
  - 1x `Object::op_Inequality`
  - 1x `Vector3::op_Subtraction`
  - 1x `Transform::set_position`
  - 1x `Quaternion::Lerp`
  - 1x `new Vector3::.ctor`
  - 1x `Entity::SetRotation`
  - 1x `Entity::IsDead`
  - 1x `Entity::IsClientControlled`
  - 1x `Entity::IsDeadIfOutOfWorld`
  - 1x `EntityDrone::NotifyOffTheWorld`
- dump `Entity::OnUpdateEntity` IL=84
  - 2x `List`1::get_Count`
  - 1x `Entity::isEntityStatic`
  - 1x `Entity::TickInWater`
  - 1x `Entity::PlayOneShot`
  - 1x `Entity::IsDead`
  - 1x `Entity::CanBePushed`
  - 1x `Entity::GetPushBoundsVertical`
  - 1x `BoundsUtils::ExpandBounds`
  - 1x `World::GetEntitiesInBounds`
  - 1x `List`1::get_Item`
  - 1x `Entity::OnPushEntity`
- dump `Entity::UpdateActivationCommands` IL=125
  - 1x `Object::op_Inequality`
  - 1x `Time::get_frameCount`
  - 1x `Entity::GetActivationCommands`
  - 1x `Object::op_Equality`
  - 1x `String::op_Implicit`
  - 1x `Entity::AllowActivationCommand`
- dump `Entity::CanUpdateEntity` IL=77
  - 2x `IChunk::GetAvailable`
  - 2x `World::toChunkXZ`
  - 1x `World::worldToBlockPos`
  - 1x `WorldBase::GetChunkFromWorldPos`
  - 1x `IChunk::get_X`
  - 1x `IChunk::get_Z`
  - 1x `WorldBase::GetChunkSync`
- dump `Entity::FixedUpdate` IL=71
  - 3x `Object::op_Implicit`
  - 2x `Vector3::op_Multiply`
  - 1x `Entity::ApplyFixedUpdate`
  - 1x `Rigidbody::get_velocity`
  - 1x `Rigidbody::set_velocity`
  - 1x `Rigidbody::get_angularVelocity`
  - 1x `Rigidbody::set_angularVelocity`
  - 1x `Vector3::op_Addition`
  - 1x `Transform::get_position`
  - 1x `Vector3::Lerp`
  - 1x `Transform::get_rotation`
  - 1x `Quaternion::Euler`
  - 1x `Quaternion::Slerp`
  - 1x `Transform::SetPositionAndRotation`
  - 1x `EntityAlive::CrouchHeightFixedUpdate`
- dump `Entity::ApplyFixedUpdate` IL=77
  - 2x `Transform::get_position`
  - 2x `Vector3::op_Subtraction`
  - 2x `Transform::get_rotation`
  - 1x `Object::op_Implicit`
  - 1x `Vector3::get_sqrMagnitude`
  - 1x `Vector3::op_Addition`
  - 1x `Entity::SetPosition`
  - 1x `Transform::set_position`
  - 1x `Component::get_transform`
  - 1x `Vector3::Distance`
  - 1x `Quaternion::Angle`
  - 1x `Mathf::Abs`
  - 1x `Quaternion::get_eulerAngles`
- dump `Entity::CalcFixedUpdateTimeScaleConstants` IL=6
  - 1x `Time::get_deltaTime`
### Fields of `Entity`
- `activationCommands` : EntityActivationCommand[]
- `addedToChunk` : System.Boolean
- `adjacentPositions` : Vector3i[]
- `animatorAudioMonitoringDictionary` : System.Collections.Generic.Dictionary`2<Entity/StopAnimatorAudioType,Audio.Handle>
- `assets` : EntityInstanceAssets
- `attachedEntities` : Entity[]
- `AttachedToEntity` : Entity
- `bag` : Bag
- `bAirBorne` : System.Boolean
- `bDead` : System.Boolean
- `belongsPlayerId` : System.Int32
- `bInElevator` : System.Boolean
- `bIsChunkObserver` : System.Boolean
- `boundingBox` : UnityEngine.Bounds
- `bWasDead` : System.Boolean
- `bWillRespawn` : System.Boolean
- `cachedTags` : FastTags`1<TagGroup/Global>
- `canCCMove` : System.Boolean
- `cAttachSlotNone` : System.Int32 = -1 [static]
- `cClientIdCreate` : System.Int32 = -1 [static]
- `cClientIdNone` : System.Int32 = 0 [static]
- `cClientIdStart` : System.Int32 = -2 [static]
- `chunkPosAddedEntityTo` : Vector3i
- `cIdCreatorIsServer` : System.Int32 = -2 [static]
- `cIgnoreDamage` : System.Int32 = -1 [static]
- `cKillAnythingDamage` : System.Int32 = 99999 [static]
- `clientEntityId` : System.Int32
- `collAABB` : System.Collections.Generic.List`1<UnityEngine.Bounds>
- `collisionFlags` : UnityEngine.CollisionFlags
- `compassDownIcon` : System.String
- `compassIcon` : System.String
- `compassUpIcon` : System.String
- `count` : System.Int32
- `cPhysicsMasterTickRate` : System.Int32 = 2 [static]
- `customCmds` : EntityActivationCommand[]
- `cWaterHeightScale` : System.Single = 1.1 [static]
- `distanceClimbed` : System.Single
- `distanceSwam` : System.Single
- `distanceWalked` : System.Single
- `emodel` : EModelBase
- `entityClass` : System.Int32
- `entityCollisionReduction` : System.Single
- `entityFlags` : EntityFlags
- `entityId` : System.Int32
- `EntityIdInvalid` : System.Int32 = -1 [static]
- `entityType` : EntityType
- `fallDistance` : System.Single
- `fallLastMotion` : UnityEngine.Vector3
- `fallLastY` : System.Single
- `fallVelY` : System.Single
- `firstUpdate` : System.Boolean
- `groundSurface` : Entity/MoveHitSurface
- `HasDeathAnim` : System.Boolean
- `hitMove` : UnityEngine.Vector3
- `InstanceCount` : System.Int32 [static]
- `interpolateTargetQRot` : System.Int32
- `interpolateTargetRot` : System.Int32
- `inWaterLevel` : System.Single
- `inWaterPercent` : System.Single
- `isCCDelayed` : System.Boolean
- `isCollided` : System.Boolean
- `isCollidedHorizontally` : System.Boolean
- `isCollidedVertically` : System.Boolean
- `IsDespawned` : System.Boolean
- `isEntityRemote` : System.Boolean
- `IsFlyMode` : DataItem`1<System.Boolean>
- `IsGodMode` : DataItem`1<System.Boolean>
- `isHeadUnderwater` : System.Boolean
- `isIgnoredByAI` : System.Boolean
- `isInWater` : System.Boolean
- `isMotionSlowedDown` : System.Boolean
- `IsMovementReplicated` : System.Boolean
- `IsNoCollisionMode` : DataItem`1<System.Boolean>
- `isPhysicsMaster` : System.Boolean
- `isRotateToGround` : System.Boolean
- `IsRotateToGroundFlat` : System.Boolean
- `IsStuck` : System.Boolean
- `isSwimming` : System.Boolean
- `isUnloaded` : System.Boolean
- `isUpdatePosition` : System.Boolean
- `kAddFixedUpdateTimeScale` : System.Single
- `lastTickPos` : UnityEngine.Vector3[]
- `lastUpdateActivationCommandsPlayerId` : System.Int32
- `lastUpdateFrameOfActivationCommands` : System.Int32
- `lastUpdateHadEnabledActivationCommands` : System.Boolean
- `lifetime` : System.Single
- `lootDropProb` : System.Single
- `lootList` : System.String
- `m_characterController` : CharacterControllerAbstract
- `m_marker` : IAIDirectorMarker
- `mapIcon` : System.String
- `markedForUnload` : System.Boolean
- `ModelTransform` : UnityEngine.Transform
- `motion` : UnityEngine.Vector3
- `motionMultiplier` : System.Single
- `movableChunkObserver` : MovableSharedChunkObserver
- `MovementState` : System.Int32
- `nativeCollider` : UnityEngine.Collider
- `NavObject` : NavObject
- `onGround` : System.Boolean
- `physicsAngVel` : UnityEngine.Vector3
- `physicsBaseHeight` : System.Single
- `physicsBasePos` : UnityEngine.Vector3
- `physicsCapsuleCollider` : UnityEngine.CapsuleCollider
- `physicsColliderLowerY` : System.Single
- `physicsColliderRadius` : System.Single
- `physicsHeight` : System.Single
- `physicsHeightScale` : System.Single
- `physicsMasterFromPos` : UnityEngine.Vector3
- `physicsMasterFromRot` : UnityEngine.Quaternion
- `physicsMasterSendPos` : UnityEngine.Vector3
- `physicsMasterSendRot` : UnityEngine.Quaternion
- `physicsMasterTargetElapsed` : System.Single
- `physicsMasterTargetPos` : UnityEngine.Vector3
- `physicsMasterTargetRot` : UnityEngine.Quaternion
- `physicsMasterTargetTime` : System.Single
- `physicsPos` : UnityEngine.Vector3
- `physicsPosMoveDistance` : System.Single
- `physicsRB` : UnityEngine.Rigidbody
- `physicsRBT` : UnityEngine.Transform
- `physicsRot` : UnityEngine.Quaternion
- `physicsTargetPos` : UnityEngine.Vector3
- `PhysicsTransform` : UnityEngine.Transform
- `physicsVel` : UnityEngine.Vector3
- `position` : UnityEngine.Vector3
- `prevPos` : UnityEngine.Vector3
- `prevRotation` : UnityEngine.Vector3
- `projectedMove` : System.Single
- `qrotation` : UnityEngine.Quaternion
- `rand` : GameRandom
- `RootMotion` : System.Boolean
- `RootTransform` : UnityEngine.Transform
- `rotateToGroundPitch` : System.Single
- `rotateToGroundPitchVel` : System.Single
- `rotation` : UnityEngine.Vector3
- `scaledExtent` : UnityEngine.Vector3
- `serverPos` : Vector3i
- `serverRot` : Vector3i
- `spawnByAllowShare` : System.Boolean
- `spawnById` : System.Int32
- `spawnByName` : System.String
- `spawnerSource` : EnumSpawnerSource
- `spawnerSourceBiomeIdHash` : System.Int32
- `spawnerSourceChunkKey` : System.Int64
- `speedForward` : System.Single
- `speedForwardSent` : System.Single
- `speedSentTicks` : System.Int32
- `speedStrafe` : System.Single
- `speedStrafeSent` : System.Single
- `speedVertical` : System.Single
- `stepHeight` : System.Single
- `targetPos` : UnityEngine.Vector3
- `targetQRot` : UnityEngine.Quaternion
- `targetRot` : UnityEngine.Vector3
- `tickPositionLerpMultiplier` : System.Single [static]
- `tickPositionMoveTowardsMaxDistance` : System.Single [static]
- `ticksExisted` : System.Int32
- `trackerIcon` : System.String
- `unloadReason` : EnumRemoveEntityReason
- `updatePositionLerpTimeScale` : System.Single [static]
- `updateRotationLerpTimeScale` : System.Single [static]
- `usePhysicsMaster` : System.Boolean
- `wasFixedUpdate` : System.Boolean
- `wasOnGround` : System.Boolean
- `waterLevelDirOffsets` : System.Single[] [static]
- `world` : World
- `WorldTimeBorn` : System.UInt64
- `yawSeekAngle` : System.Single
- `yawSeekAngleEnd` : System.Single
- `yawSeekTime` : System.Single
- `yawSeekTimeMax` : System.Single
- `yOffset` : System.Single
- `ySize` : System.Single

#### field `isEntityRemote`
- `Animator3PRangedReloadState::OnStateEnter` ldfld
- `AnimatorMeleeAttackState::OnStateExit` ldfld
- `AnimatorRangedReloadState::OnStateEnter` ldfld
- `AnimatorStateRaycast::OnStateEnter` ldfld
- `AvatarAnimalController::StartAnimationAttack` ldfld
- `AvatarAnimalController::LateUpdate` ldfld
- `AvatarBanditController::Update` ldfld
- `AvatarController::_setTrigger` ldfld
- `AvatarController::_resetTrigger` ldfld
- `AvatarController::_setFloat` ldfld
- `AvatarController::_setBool` ldfld
- `AvatarController::_setInt` ldfld
- `AvatarController::SetDataFloat` ldfld
- `AvatarController::updateNetworkAnimData` ldfld
- `AvatarMultiBodyController::SetInRightHand` ldfld
- `AvatarMultiBodyController::_setTrigger` ldfld
- `AvatarMultiBodyController::_resetTrigger` ldfld
- `AvatarMultiBodyController::_setFloat` ldfld
- `AvatarMultiBodyController::_setBool` ldfld
- `AvatarMultiBodyController::_setInt` ldfld
- `AvatarZombieController::Update` ldfld
- `GameObjectAnimalAnimation::Update` ldfld
- `LegacyAvatarController::Update` ldfld
- `EntityStats::Tick` ldfld
- `NetPackageEntityStatChanged::ProcessPackage` ldfld
- `NetPackageEntityStatsBuff::ProcessPackage` ldfld
- `ConsoleCmdGiveXp::Execute` ldfld
- `ConsoleCmdListEntities::Execute` ldflda
- `ConsoleCmdListPlayers::Execute` ldfld
- `ConsoleCmdLogGameState::WriteEntities` ldfld
- `ConsoleCmdLogGameState::WritePlayers` ldfld
- `Entity::Awake` stfld
- `Entity::Update` ldfld
- `Entity::updateTransform` ldfld
- `Entity::AddCharacterController` ldfld
- `Entity::OnUpdatePosition` ldfld
- `Entity::OnUpdateEntity` ldfld
- `Entity::OnLoadedFromEntityCache` ldfld
- `Entity::AttachEntityToSelf` ldfld
- `Entity::DetachEntity` stfld
- `Entity::AttachToEntity` ldfld
- `Entity::Detach` ldfld
- `EntityAlive::ApplySpawnState` ldfld
- `EntityAlive::OnUpdatePosition` ldfld
- `EntityAlive::OnUpdateEntity` ldfld
- `EntityAlive::KillLootContainer` ldfld
- `EntityAlive::NotifySleeperDeath` ldfld
- `EntityAlive::set_JetpackActive` ldfld
- `EntityAlive::set_JetpackWearing` ldfld
- `EntityAlive::set_ParachuteWearing` ldfld
- `EntityAlive::set_Crouching` ldfld
- `EntityAlive::set_Jumping` ldfld
- `EntityAlive::set_Climbing` ldfld
- `EntityAlive::StartAnimAction` ldfld
- `EntityAlive::ContinueAnimAction` ldfld
- `EntityAlive::set_SpecialAttack` ldfld
- `EntityAlive::set_SpecialAttack2` ldfld
- `EntityAlive::set_Electrocuted` ldfld
- `EntityAlive::set_IsEating` ldfld
- `EntityAlive::SetVehicleAnimation` ldfld
- `EntityAlive::set_Died` ldfld
- `EntityAlive::set_Score` ldfld
- `EntityAlive::set_KilledZombies` ldfld
- `EntityAlive::set_KilledPlayers` ldfld
- `EntityAlive::set_TeamNumber` ldfld
- `EntityAlive::SetEntityName` ldfld
- `EntityAlive::set_DeathHealth` ldfld
- `EntityAlive::set_Spawned` ldfld
- `EntityAlive::set_IsBreakingBlocks` ldfld
- `EntityAlive::set_CurrentHeadState` ldfld
- `EntityAlive::OnUpdateLive` ldfld
- `EntityAlive::checkForTeleportOutOfTraderArea` ldfld
- `EntityAlive::EndJump` ldfld
- `EntityAlive::Update` ldfld
- `EntityAlive::OnDeathUpdate` ldfld
- `EntityAlive::MoveEntityHeaded` ldfld
- `EntityAlive::SetAlive` ldfld
- `EntityAlive::DamageEntity` ldfld
- `EntityAlive::damageEntityLocal` ldfld
- `EntityAlive::FireAttackedEvents` ldfld
- `EntityAlive::ProcessDamageResponse` ldfld
- `EntityAlive::ProcessDamageResponseLocal` ldfld
- `EntityAlive::OnEntityDeath` ldfld
- `EntityAlive::CheckDespawn` ldfld
- `EntityAlive::GetAttackTargetLocal` ldfld
- `EntityAlive::SetAttackTarget` ldfld
- `EntityAlive::get_IsAlert` ldfld
- `EntityAlive::updateSpeedForwardAndStrafe` ldfld
- `EntityAlive::OnAddedToWorld` ldfld
- `EntityAlive::AttachToEntity` ldfld
- `EntityAlive::Detach` ldfld
- `EntityAlive::SetSpawnByData` ldfld
- `EntityBackpack::OnUpdateEntity` ldfld
- `EntityBackpack::RemoveBackpack` ldfld
- `EntityCar::OnUpdateLive` ldfld
- `EntityCar::SetRotation` ldfld
- `EntityCar::OnEntityDeath` ldfld
- `EntityDrone::updatePartyBuffs` ldfld
- `EntityEnemy::PostInit` ldfld
- `EntityEnemy::OnEntityTargeted` ldfld
- `EntityFallingBlock::Awake` ldfld
- `EntityFallingBlock::InitLocation` ldfld
- `EntityFallingBlock::Update` ldfld
- `EntityFallingBlock::OnUpdateEntity` ldfld
- `EntityFallingBlock::updateTransform` ldfld
- `EntityFallingBlock::OnContactEvent` ldfld
- `EntityFallingBlocks::Awake` ldfld
- `EntityFallingBlocks::InitLocation` ldfld
- `EntityFallingBlocks::Update` ldfld
- `EntityFallingBlocks::OnUpdateEntity` ldfld
- `EntityFallingBlocks::updateTransform` ldfld
- `EntityFallingBlocks::OnContactEvent` ldfld
- `EntityFallingTree::Awake` ldfld
- `EntityFallingTree::SetBlockPos` ldfld
- `EntityFallingTree::Collide` ldfld
- `EntityFallingTree::CreateMesh` ldfld
- `EntityFallingTree::OnUpdateEntity` ldfld
- `EntityFallingTree::DestroyTree` ldfld
- `EntityFallingTree::updateTransform` ldfld
- `EntityFallingTree::MarkToUnload` ldfld
- `EntityHuman::OnUpdateLive` ldfld
- `EntityHuman::ProcessDamageResponseLocal` ldfld
- `EntityItem::OnUpdateEntity` ldfld
- `EntityPlayer::set_TwitchEnabled` ldfld
- `EntityPlayer::set_TwitchSafe` ldfld
- `EntityPlayer::set_TwitchVoteLock` ldfld
- `EntityPlayer::set_TwitchVisionDisabled` ldfld
- `EntityPlayer::set_TwitchActionsEnabled` ldfld
- `EntityPlayer::set_IsSpectator` ldfld
- `EntityPlayer::set_markerPosition` ldfld
- `EntityPlayer::set_RentedVMPosition` ldfld
- `EntityPlayer::get_IsAdmin` ldfld
- `EntityPlayer::OnUpdateEntity` ldfld
- `EntityPlayer::CheckPosition` ldfld
- `EntityPlayer::AddKillXP` ldfld
- `EntityPlayerLocal::Awake` stfld
- `EntityPlayerLocal::OnUpdateLive` ldfld
- `EntitySupplyCrate::CanUpdateEntity` ldfld
- `EntitySupplyPlane::OnUpdatePosition` ldfld
- `EntityTrader::OnEntityTargeted` ldfld
- `EntityTrader::PlayVoiceSetEntry` ldfld
- `EntityVehicle::Init` ldfld
- `EntityVehicle::PhysicsFixedUpdate` ldfld
- `EntityVehicle::updateTransform` ldfld
- `EntityVehicle::SetPosition` ldfld
- `EntityVehicle::SetRotation` ldfld
- `EntityVehicle::AddRelativeForce` ldfld
- `EntityVehicle::AddForce` ldfld
- `EntityVehicle::GetVelocityPerSecond` ldfld
- `EntityVehicle::VelocityFlip` ldfld
- `EntityVehicle::GetCameraOffset` ldfld
- `EntityVehicle::SetVehicleDriven` ldfld
- `EntityVehicle::AttachEntityToSelf` ldfld
- `EntityVehicle::DetachEntity` ldfld
- `EntityVehicle::OnCollisionForward` ldfld
- `EntityVehicle::ProcessDamageResponseLocal` ldfld
- `EntityZombieCop::OnUpdateEntity` ldfld
- `EntityZombieCop::ProcessDamageResponseLocal` ldfld
- `EntityZombieDog::OnUpdateLive` ldfld
- `PlayerStealth::TickServer` ldfld
- `PlayerStealth::SmellTickServer` ldfld
- `EModelBase::InitRigidBodies` ldfld
- `EModelBase::DoRagdoll` ldfld
- `EModelBase::BlendRagdoll` ldfld
- `EModelBase::FrameUpdateRagdoll` ldfld
- `EModelBase::SwitchModelAndView` ldfld
- `Equipment::SetCosmeticSlot` ldfld
- `Equipment::SetCosmeticSlot` ldfld
- `Equipment::ClearCosmeticSlots` ldfld
- `Equipment::ApplyTempCosmeticSlot` ldfld
- `Equipment::SetSlotItem` ldfld
- `Explosion::AttackEntites` ldfld
- `ExplosionDamageArea::OnTriggerEnter` ldfld
- `Inventory::setHeldItemByIndex` ldfld
- `Inventory::AddItem` ldfld
- `Inventory::AddItemAtSlot` ldfld
- `Inventory::updateHoldingItem` ldfld
- `Inventory::TryStackItem` ldfld
- `Inventory::TryTakeItem` ldfld
- `ItemActionAttack::Hit` ldfld
- `ItemActionCatapult::ReloadGun` ldfld
- `ItemActionLauncher::ReloadGun` ldfld
- `ItemActionRanged::ReloadGun` ldfld
- `ItemActionRanged::ItemActionEffects` ldfld
- `ItemActionRanged::onHoldingEntityFired` ldfld
- `ItemActionThrownWeapon::ItemActionEffects` ldfld
- `ItemActionThrownWeapon::ExecuteAction` ldfld
- `ItemActionZoom::IsHUDDisabled` ldfld
- `ItemClass::OnHoldingUpdate` ldfld
- `ItemClass::StopHolding` ldfld
- `ItemClassTimeBomb::OnHoldingItemActivated` ldfld
- `ItemClassTimeBomb::OnHoldingUpdate` ldfld
- `ItemClassTimeBomb::OnHoldingReset` ldfld
- `ProjectileMoveScript::checkCollision` ldfld
- `ProjectileMoveScript::OnDestroy` ldfld
- `ThrownWeaponMoveScript::checkCollision` ldfld
- `ThrownWeaponMoveScript::OnDestroy` ldfld
- `LootManager::LootContainerOpened` ldfld
- `LootManager::LootBagOpened` ldfld
- `EntityBuffs::AddBuff` ldfld
- `EntityBuffs::SetCustomVar` ldfld
- `MinEventActionBuffModifierBase::Remove` ldfld
- `MinEventActionAddBuff::Execute` ldfld
- `MinEventActionModifyCVar::Execute` ldfld
- `MinEventActionRemoveCVar::Execute` ldfld
- `MinEventActionAddPartTPV::CanExecute` ldfld
- `MinEventActionGiveSkillExp::Execute` ldfld
- `MinEventActionGiveExp::Execute` ldfld
- `MinEventActionSetProgressionLevel::Execute` ldfld
- `MinEventActionAddProgressionLevel::Execute` ldfld
- `NetPackageEntityAddExpServer::ProcessPackage` ldfld
- `NetPackageEntitySetSkillLevelServer::ProcessPackage` ldfld
- `NetPackageEntityAliveFlags::ProcessPackage` ldfld
- `NetPackageEntityAnimationData::ProcessPackage` ldfld
- `PrefabLODManager::FrameUpdate` ldfld
- `RegionFileManager::RemovePersistentDataForChunks` ldfld
- `World::TickEntity` ldfld
- `DecoManager::UpdateTick` ldfld
- `VPEngine::playSound` ldfld
- `VPEngine::stopSound` ldfld
- `VPHeadlight::PlaySound` ldfld
- `VPPedals::playSound` ldfld
- `GameManager::updateSendClientPlayerPositionToServer` ldfld
- `GameManager::RequestToSpawnPlayer` stfld
- `GameManager::PlayerSpawnedInWorld` ldfld
- `GameManager::ItemDropServer` ldfld
- `GameManager::AddScoreServer` ldfld
- `GameManager::AwardKill` ldfld
- `PlayerDataFile::ToPlayer` ldfld
- `POIWaypoint::TrySet` ldfld
- `POIWaypoint::Remove` ldfld
- `POIWaypoint::ClearAll` ldfld
- `HomerunData::AddScoreDisplay` ldfld
- `HomerunData::RemoveScoreDisplay` ldfld
- `ActionEjectFromVehicle::PerformTargetAction` ldfld
- `ActionRemoveVehicles::HandleRemoveData` ldfld
#### field `bWillRespawn`
- `EntityDrone::initWorldValues` stfld
- `EntityPlayer::Awake` stfld
- `ConnectionManager::DisconnectClient` stfld
- `World::TickEntity` ldfld
- `World::UnloadEntities` ldfld
### Annotated `EntityFactory::CreateEntity` IL=5

```
IL_0002: call EntityCreationData EntityFactory::SetupEntityCreationData(System.Int32,UnityEngine.Vector3)
IL_0007: call Entity EntityFactory::CreateEntity(EntityCreationData)
IL_000C: ret
```

### Annotated `EntityFactory::CreateEntity` IL=6

```
IL_0003: call EntityCreationData EntityFactory::SetupEntityCreationData(System.Int32,UnityEngine.Vector3,UnityEngine.Vector3)
IL_0008: call Entity EntityFactory::CreateEntity(EntityCreationData)
IL_000D: ret
```

### Annotated `EntityFactory::CreateEntity` IL=7

```
IL_0004: call EntityCreationData EntityFactory::SetupEntityCreationData(System.Int32,System.Int32,UnityEngine.Vector3,UnityEngine.Vector3)
IL_0009: call Entity EntityFactory::CreateEntity(EntityCreationData)
IL_000E: ret
```

### Annotated `EntityFactory::CreateEntity` IL=17

```
IL_0001: ldsfld System.Int32 EntityFactory::nextEntityID
IL_000E: call ItemValue ItemValue::get_None()
IL_0016: ldc.r4 3.402823E+38
IL_001F: call EntityCreationData EntityFactory::SetupEntityCreationData(System.Int32,System.Int32,ItemValue,System.Int32,UnityEngine.Vector3,UnityEngine.Vector3,System.Single,System.Int32,System.Int32,System.String)
IL_0024: call Entity EntityFactory::CreateEntity(EntityCreationData)
IL_0029: ret
```

### Annotated `EntityFactory::CreateEntity` IL=14

```
IL_0012: call EntityCreationData EntityFactory::SetupEntityCreationData(System.Int32,System.Int32,BlockValue[],TextureFullArray[],System.Int32,UnityEngine.Vector3,UnityEngine.Vector3,System.Single,System.Int32,System.Int32,System.String)
IL_0017: call Entity EntityFactory::CreateEntity(EntityCreationData)
IL_001C: ret
```

### Annotated `EntityFactory::CreateEntity` IL=7

```
IL_0002: call EntityFactory/CreateEntityOperation EntityFactory/CreateEntityOperation::Start(EntityCreationData,System.Boolean)
IL_0008: callvirt System.Void EntityFactory/CreateEntityOperation::CompleteEntity()
IL_000D: ldfld Entity EntityFactory/CreateEntityOperation::entity
IL_0012: ret
```

### `EntityCreationData`
- `read` IL=500
- `write` IL=358
- `.ctor` IL=310
- `.ctor` IL=204
- `ApplyToEntity` IL=169
- `writeXml` IL=88
- `.ctor` IL=49
- `readXml` IL=47
### `EntityFactory`
- `GetEntityType` IL=137
- `FindOrCreateTransform` IL=52
- `Init` IL=49
- `SetupEntityCreationData` IL=36
- `SetupEntityCreationData` IL=31

## 5b. set_enabled / SetActive near Entity spawn

- `Entity::SetupBounds` -> `Collider::set_enabled`
- `Entity::AddCharacterController` -> `Collider::set_enabled`
- `Entity::PhysicsPause` -> `GameObject::SetActive`
- `Entity::PhysicsResume` -> `GameObject::SetActive`
- `Entity::SetDead` -> `GameObject::SetActive`
- `Entity::SetTransformActive` -> `GameObject::SetActive`
- `EntityAlive::OnCollisionForward` -> `Collider::set_enabled`
- `EntityAlive::SetPartActive` -> `GameObject::SetActive`
- `EntityPlayerLocal::onSpawnStateChanged` -> `Behaviour::set_enabled`
- `EntityPlayerLocal::AfterPlayerRespawn` -> `Behaviour::set_enabled`
- `XUiC_WorldToolsWindow::BtnLevelStartPoint_Controller_OnPress` -> `SelectionBoxManager::SetActive`
- `vp_Pickup::Respawn` -> `Renderer::set_enabled`

## 6. ProtocolManager / net stack

### Fields of `ProtocolManager`
- `<CurrentMode>k__BackingField` : ProtocolManager/NetworkType
- `<HasRunningServers>k__BackingField` : System.Boolean
- `clients` : System.Collections.Generic.List`1<INetworkClient>
- `currentConnectionAttemptIndex` : System.Int32
- `currentGameServerInfo` : GameServerInfo
- `servers` : System.Collections.Generic.List`1<INetworkServer>

- dump `ProtocolManager::Update` IL=35
  - 2x `List`1::get_Item`
  - 2x `List`1::get_Count`
  - 1x `INetworkServer::Update`
  - 1x `INetworkClient::Update`
- dump `ProtocolManager::LateUpdate` IL=35
  - 2x `List`1::get_Item`
  - 2x `List`1::get_Count`
  - 1x `INetworkServer::LateUpdate`
  - 1x `INetworkClient::LateUpdate`
- dump `ProtocolManager::LateUpdate` IL=35
  - 2x `List`1::get_Item`
  - 2x `List`1::get_Count`
  - 1x `INetworkServer::LateUpdate`
  - 1x `INetworkClient::LateUpdate`
- dump `ProtocolManager::StartServers` IL=106
  - 2x `PlatformManager::get_MultiPlatform`
  - 2x `IPlatform::get_User`
  - 2x `IUserClient::get_UserStatus`
  - 2x `PermissionsManager::IsMultiplayerAllowed`
  - 2x `PermissionsManager::CanHostMultiplayer`
  - 2x `String::Format`
  - 2x `ProtocolManager::set_CurrentMode`
  - 2x `Log::Error`
  - 2x `List`1::get_Item`
  - 2x `ProtocolManager::set_HasRunningServers`
  - 2x `List`1::get_Count`
  - 1x `Log::Warning`
  - 1x `ProtocolManager::StartOfflineServer`
  - 1x `Log::Out`
  - 1x `ProtocolManager::SetupProtocols`
  - 1x `GamePrefs::GetInt`
  - 1x `INetworkServer::StartServer`
  - 1x `INetworkServer::StopServer`
  - 1x `EnumUtils::ToStringCached`
  - 1x `String::Concat`
- dump `ConnectionManager::UpdatePings` IL=20
  - 1x `ReadOnlyCollection`1::get_Item`
  - 1x `ClientInfo::UpdatePing`
  - 1x `ReadOnlyCollection`1::get_Count`
- dump `ConnectionManager::Update` IL=215
  - 4x `ConnectionManager::ProcessPackages`
  - 3x `INetConnection::IsDisconnected`
  - 2x `Time::get_time`
  - 2x `ClientInfoCollection::get_Count`
  - 2x `CountdownTimer::HasPassed`
  - 2x `GameManager::get_World`
  - 2x `CountdownTimer::ResetAndRestart`
  - 2x `INetConnection::FlushSendQueue`
  - 1x `ProtocolManager::Update`
  - 1x `ConnectionManager::get_IsServer`
  - 1x `ReadOnlyCollection`1::get_Item`
  - 1x `INetworkServer::GetBadPacketCount`
  - 1x `new KickPlayerData::.ctor`
  - 1x `GameUtils::KickPlayerForClientInfo`
  - 1x `ConnectionManager::FlushClientSendQueues`
  - 1x `ConnectionManager::ClientCount`
  - 1x `ConnectionManager::UpdatePings`
  - 1x `NetPackageManager::GetPackage`
  - 1x `NetPackageClientInfo::Setup`
  - 1x `ConnectionManager::SendPackage`
- dump `ConnectionManager::LateUpdate` IL=4
  - 1x `ProtocolManager::LateUpdate`
- dump `ConnectionManager::ProcessPackages` IL=116
  - 3x `Log::Error`
  - 3x `String::Format`
  - 3x `Log::Warning`
  - 3x `GameManager::get_World`
  - 2x `Int32::ToString`
  - 2x `List`1::get_Count`
  - 1x `INetConnection::GetPackages`
  - 1x `List`1::get_Item`
  - 1x `String::Concat`
  - 1x `NetPackage::get_PackageDirection`
  - 1x `NetPackage::get_AllowedBeforeAuth`
  - 1x `NetPackage::ShouldProcess`
  - 1x `NetPackage::ProcessPackage`
  - 1x `NetPackageManager::FreePackage`
  - 1x `NetPackage::HandleSkipped`
- dump `ConnectionManager::SendPackage` IL=168
  - 3x `List`1::get_Item`
  - 3x `List`1::get_Count`
  - 2x `GameManager::get_World`
  - 2x `World::IsEntityInRange`
  - 2x `NetPackage::get_Channel`
  - 2x `INetConnection::FlushSendQueue`
  - 1x `NetPackage::RegisterSendQueue`
  - 1x `ReadOnlyCollection`1::get_Item`
  - 1x `Nullable`1::get_HasValue`
  - 1x `Nullable`1::get_Value`
  - 1x `INetConnection::AddToSendQueue`
  - 1x `NetPackage::get_FlushQueue`
  - 1x `ReadOnlyCollection`1::get_Count`
  - 1x `NetPackage::SendQueueHandled`
- dump `ConnectionManager::SendPackage` IL=100
  - 2x `GameManager::get_World`
  - 2x `World::IsEntityInRange`
  - 2x `NetPackage::get_Channel`
  - 1x `NetPackage::RegisterSendQueue`
  - 1x `ReadOnlyCollection`1::get_Item`
  - 1x `Nullable`1::get_HasValue`
  - 1x `Nullable`1::get_Value`
  - 1x `INetConnection::AddToSendQueue`
  - 1x `NetPackage::get_FlushQueue`
  - 1x `INetConnection::FlushSendQueue`
  - 1x `ReadOnlyCollection`1::get_Count`
  - 1x `NetPackage::SendQueueHandled`
- dump `ConnectionManager::FlushClientSendQueues` IL=28
  - 2x `INetConnection::FlushSendQueue`
  - 1x `ReadOnlyCollection`1::get_Item`
  - 1x `ReadOnlyCollection`1::get_Count`
### Types containing LiteNet or NetManager
- `NetworkClientLiteNetLib`
- `NetworkCommonLiteNetLib`
- `NetworkServerLiteNetLib`

## 7. AntiCheat / EAC surface

### `AntiCheatEncryptionAuthServer`
- `SendSharedKey` IL=114
- `CompleteKeyExchange` IL=73
- `TryStartKeyExchange` IL=24
- `Stop` IL=21
- `Start` IL=14
- `.cctor` IL=11
- `CancelKeyExchange` IL=6
- `OnClientDisconnected` IL=4
- `.ctor` IL=3
### `AntiCheatEncryptionAuthClient`
- `StartKeyExchange` IL=62
- `CompleteKeyExchange` IL=55
- `.ctor` IL=3
- `GetSigningKey` IL=2
### `EacAuthorizer`
- `ServerStart` IL=17
- `Authorize` IL=15
- `ServerStop` IL=10
- `get_AuthorizerActive` IL=9
- `authPlayerEacSuccessfulCallback` IL=9
- `Disconnect` IL=9
- `kickPlayerCallback` IL=7
- `.ctor` IL=3
- `get_Order` IL=2
- `get_AuthorizerName` IL=2
### `AntiCheatEncryptionAgreementAuthorizer`
- `Authorize` IL=57
- `ServerStart` IL=12
- `KeyExchangeCompleted` IL=9
- `KeyExchangeFailed` IL=7
- `ServerStop` IL=6
- `.ctor` IL=3
- `get_Order` IL=2
- `get_AuthorizerName` IL=2
- `get_StateLocalizationKey` IL=2
### `NetPackageEAC`
- `write` IL=29
- `read` IL=27
- `ProcessPackage` IL=25
- `GetLength` IL=12
- `Setup` IL=11
- `.ctor` IL=3
- `get_AllowedBeforeAuth` IL=2
### `NetPackageWireActions`
- `ProcessPackage` IL=163
- `GetPoweredTileEntity` IL=53
- `write` IL=45
- `read` IL=38
- `Setup` IL=11
- `.ctor` IL=6
- `GetLength` IL=2
### `QuestEvent_ItemValueActionEvent`
### `RegionFileAccessAbstract`
- `ExtractKey` IL=53
- `MakeFilename` IL=26
- `.ctor` IL=3
- `GetChunkByteCount` IL=2
- `GetTotalByteCount` IL=2
- `Close` IL=1
- `OptimizeLayouts` IL=1
### `RegionFileAccessMultipleChunks`
- `ReadDirectory` IL=130
- `ClearCache` IL=73
- `Remove` IL=69
- `GetChunkByteCount` IL=69
- `GetTotalByteCount` IL=68
- `GetRFC` IL=64
- `RemoveRegionFromCache` IL=58
- `OptimizeLayouts` IL=50
- `GetInputStream` IL=34
- `Write` IL=20
### `RegionFileAccessRaw`
- `OpenRegionFile` IL=20
- `GetRegionCoords` IL=17
- `ReadDirectory` IL=6
- `.ctor` IL=3
- `get_ChunksPerRegionPerDimension` IL=2
### `RegionFileAccessSectorBased`
- `GetRegionCoords` IL=17
- `ReadDirectory` IL=6
- `OpenRegionFile` IL=6
- `.ctor` IL=3
- `get_ChunksPerRegionPerDimension` IL=2
### `TileAreaConfig`
- `checkCoordinates` IL=101
### `TileAreaCache`1`
- `Cache` IL=80
- `PromoteEntry` IL=27
- `get_Item` IL=26
- `get_Item` IL=23
- `.ctor` IL=18
- `Cleanup` IL=10
- `get_Config` IL=3
### `ScopedChunkWriteAccess`
- `.ctor` IL=11
- `Dispose` IL=8
- `set_Chunk` IL=4
- `get_Chunk` IL=3
### `CreativeActionEntryFavorite`
- `OnActivated` IL=35
- `.ctor` IL=13
### `ServiceActionEntryRent`
- `OnDisabledActivate` IL=50
- `.ctor` IL=12
- `OnActivated` IL=11
- `RefreshEnabled` IL=8
### `Twitch.OnGameEventVoteAction`
### `GameEvent.SequenceActions.BaseAction`
- `GetTextWithElements` IL=87
- `HandleAssignFrom` IL=70
- `Clone` IL=62
- `HandleTemplateInit` IL=60
- `PerformAction` IL=39
- `ParseProperties` IL=28
- `set_Owner` IL=25
- `SetActionKeyData` IL=23
- `AddRequirement` IL=15
- `TeleportEntity` IL=12
### `GameEvent.SequenceActions.ActionTwitchChallengeAction`
- `ParseProperties` IL=14
- `CloneChildSettings` IL=10
- `OnClientPerform` IL=7
- `.ctor` IL=6
- `.cctor` IL=5
### `Platform.IAntiCheatClient`
### `Platform.IAntiCheatEncryption`
### `Platform.IAntiCheatServer`
### `Platform.MaxResultsReachedCallback`
### `Platform.EOS.AntiCheatClientCS`
- `EncryptStream` IL=97
- `DecryptStream` IL=90
- `ConnectToServer` IL=55
- `HandleMessageFromServer` IL=45
- `DisconnectFromServer` IL=32
- `handleMessageToServer` IL=27
- `Activate` IL=26
- `Deactivate` IL=13
- `.ctor` IL=9
### `Platform.EOS.AntiCheatClientManager`
- `apiInitialized` IL=73
- `ConnectToServer` IL=67
- `WaitForRemoteAuth` IL=59
- `DisconnectFromServer` IL=33
- `HandleMessageFromServer` IL=28
- `GetUnhandledViolationMessage` IL=21
- `handleClientIntegrityViolated` IL=19
- `Init` IL=16
- `EncryptStream` IL=13
- `DecryptStream` IL=13
### `Platform.EOS.AntiCheatClientP2P`
- `handlePeerActionRequired` IL=94
- `ConnectToServer` IL=86
- `Activate` IL=85
- `HandleMessageFromPeer` IL=53
- `Deactivate` IL=50
- `BeginSession` IL=46
- `EndSession` IL=34
- `handlePeerAuthStateChange` IL=31
- `add_OnRemoteAuthComplete` IL=28
- `.ctor` IL=26
### `Platform.EOS.AntiCheatCommon`
- `IntPtrToClientInfo` IL=23
- `Init` IL=22
- `ClientInfoToIntPtr` IL=4
- `.cctor` IL=3
### `Platform.EOS.AntiCheatServer`
- `EncryptStream` IL=103
- `StartServer` IL=99
- `DecryptStream` IL=96
- `addCallbacks` IL=76
- `handleMessageToClient` IL=76
- `RegisterUser` IL=73
- `handleClientAction` IL=70
- `removeCallbacks` IL=56
- `HandleMessageFromClient` IL=55
- `FreeUser` IL=44
### `Platform.EOS.AntiCheatServerP2P`
- `RegisterUser` IL=83
- `AddCallbacks` IL=76
- `handlePeerActionRequired` IL=74
- `handleMessageToPeer` IL=67
- `StartServer` IL=65
- `HandleMessageFromClient` IL=58
- `FreeUser` IL=44
- `StopServer` IL=43
- `apiInitialized` IL=32
- `GetHostUserIdAndToken` IL=31
### `EAccessModifier`

## 8. MonoBehaviour Update classification (heuristic)

### Likely dedicated-relevant (33)
- `AutoTurretController`
- `AutoTurretFireController`
- `ConnectionManager`
- `DynamicMeshManager`
- `ElectricWireController`
- `Entity`
- `EntityAlive`
- `EntityBackpack`
- `EntityCar`
- `EntityDrone`
- `EntityFallingBlock`
- `EntityFallingBlocks`
- `EntityHomerunGoal`
- `EntityItem`
- `EntitySupplyCrate`
- `EntityVehicle`
- `EntityVHelicopter`
- `EnvironmentAudioManager`
- `GameManager`
- `HazardDamageController`
- `MiniTurretFireController`
- `MotionSensorController`
- `Origin`
- `SdtdConsole`
- `SelectionBox`
- `SelectionBoxManager`
- `SkyManager`
- `SpinningBladeTrapBladeController`
- `SpinningBladeTrapController`
- `SpotlightController`
- `WaterEvaporationManager`
- `WireNode`
- `WorldEnvironment`

### Likely client/editor (96)
- `AudioPlayer`
- `AvatarAnimalController`
- `AvatarBanditController`
- `AvatarController`
- `AvatarControllerDummy`
- `AvatarLocalPlayerController`
- `AvatarMultiBodyController`
- `AvatarNpcController`
- `AvatarSDCSController`
- `AvatarUMAController`
- `AvatarZombieController`
- `CameraControl`
- `CameraMatrixOverride`
- `CharacterGazeController`
- `CharacterShaderLODControl`
- `ControllerCamera`
- `ControllerGUI`
- `EyeLidController`
- `FaceSpriteAtCamera`
- `FeatherFlutter`
- `FlexibleCursor`
- `FreeCamera`
- `GUIFPS`
- `GUIWindowManager`
- `LagPosition`
- `LegacyAvatarController`
- `LightLODHeld`
- `LocalPlayerUI`
- `MainMenuMono`
- `MuzzleFlash`
- `NGSS_Directional`
- `NGSS_Local`
- `NGuiHUDText`
- `NGuiPanelFade`
- `NGuiUIFollowTarget`
- `NGuiWdwDebugPanels`
- `NguiWdwTerrainEditor`
- `NGUIWindowManager`
- `PlayerMoveController`
- `PlayerReflectionProbe`
- `ScreenEffects`
- `ScreenshotData`
- `ScreenSpaceParticleAspectScaler`
- `ShaderGlobalsHelper`
- `SoftCursor`
- `SplashScreenScript`
- `UICursor`
- `UIItemSlot`
- `UISliderColors`
- `UpdateLightOnPlayers`
- `vp_3rdPersonWeaponAim`
- `vp_AngleBob`
- `vp_Billboard`
- `vp_Bob`
- `vp_BodyAnimator`
- `vp_Climb`
- `vp_Component`
- `vp_Debris`
- `vp_DoomsDayDevice`
- `vp_Explosion`
- `vp_FootstepManager`
- `vp_FPBodyAnimator`
- `vp_FPCamera`
- `vp_FPController`
- `vp_FPEarthquake`
- `vp_FPInput`
- `vp_FPInteractManager`
- `vp_FPPlayerDamageHandler`
- `vp_FPSDemo1`
- `vp_FPSDemo2`
- `vp_FPSDemo3`
- `vp_FPSDemoPlaceHolderMessenger`
- `vp_FPWeapon`
- `vp_FPWeaponMeleeAttack`
- `vp_Grab`
- `vp_ItemPickup`
- `vp_MovingPlatform`
- `vp_MuzzleFlash`
- `vp_Pickup`
- `vp_PulsingLight`
- ... +16

### Unclassified / mixed (77)
- `AIDirectorEventsFromXml`
- `AIDirectorPooledMarker`
- `AnimationParameters`
- `AnimationTestSceneTools`
- `AttachmentTestSceneTools`
- `AudioMixerManager`
- `AudioSourceLifetimeSwitch`
- `BackgroundMusicMono`
- `bleedingScale`
- `BlendshapeTestSceneTools`
- `BoundaryProjector`
- `CharacterConstruct`
- `CloneToTransform`
- `ContactShadows`
- `ControllerDebugLabel`
- `ControllerDebugMacros`
- `CustomController`
- `DamageText`
- `DangerRoomEnvironmentSim`
- `DebugDrawNormals`
- `DebugLines`
- `DelayedLightIgnition`
- `Detonator`
- `DroneBeamParticle`
- `DroneRunningLight`
- `EModelBase`
- `EModelSDCS`
- `EntityNewStyleAvatar` (both hints)
- `EntityPlayer` (both hints)
- `EntityPlayerLocal` (both hints)
- `EyeAdv_AutoDilation`
- `Fluctuating`
- `FrameRateLimiter`
- `GameObjectAnimalAnimation`
- `GlitterLight`
- `HomerunGoalController`
- `Jiggle`
- `JunkSledgeFireController`
- `KinematicCharacterSystem`
- `LagRotation`
- `LightAnim`
- `LightFlicker`
- `LightViewer`
- `LookAtTarget`
- `ModelViewerCam`
- `MumblePositionalAudio`
- `ObjectiveRallyPointData`
- `PanWithMouse`
- `ParticleLifetimeSwitch`
- `PlayIdleAnimations`
- `POIBoundsHelper`
- `PrefabInstanceGizmo`
- `ProceduralAnimation`
- `ProjectileMoveScript`
- `QuestGeneratorController`
- `RagdollWhenHit`
- `ReadProceduralTextureExample`
- `ReflectiveWater`
- `Rotate`
- `RotateObject`
- `RotatingText`
- `ScriptBase`
- `SkinnedCollisionHelper`
- `SkinningTestSceneTools`
- `SmartTextMesh`
- `Spin`
- `TextureDynamicLoader`
- `TextureLoadingManager`
- `ThrownWeaponMoveScript`
- `TimeRotateObject`
- `TransformDebug`
- `TurnTable`
- `UnityMemoryProfilerLabel`
- `UpdateLightOnChunkMesh`
- `WindowAutoYaw`
- `WindowDragTilt`
- `WireFrameSphere`

## 9. Server start path (AIDirector / Astar / managers)

- dump `GameManager::StartAsServer` IL=9
  - 1x `new <StartAsServer>d__166::.ctor`
- dump `GameManager::StartGame` IL=21
  - 2x `GameSparksManager::Instance`
  - 1x `Time::set_timeScale`
  - 1x `GamePrefs::Set`
  - 1x `PlatformManager::get_MultiPlatform`
  - 1x `IPlatform::get_UserDataRoaming`
  - 1x `IUserDataRoaming::ValidateRoamingMode`
  - 1x `Object::op_Inequality`
  - 1x `GameSparksManager::PrepareNewSession`
  - 1x `GameManager::startGameCo`
  - 1x `MonoBehaviour::StartCoroutine`
- dump `GameManager::startGameCo` IL=9
  - 1x `new <startGameCo>d__138::.ctor`
- dump `GameManager::createWorld` IL=18
  - 1x `new <createWorld>d__214::.ctor`
- dump `GameManager::Awake` IL=354
  - 14x `GameManager::get_IsDedicatedServer`
  - 8x `Log::Out`
  - 4x `RoamingPrefs::get_Store`
  - 4x `GamePrefs::get_Instance`
  - 4x `GamePrefs::Save`
  - 3x `Object::FindAnyObjectByType`
  - 3x `Component::get_gameObject`
  - 2x `Application::get_isFocused`
  - 2x `String::Concat`
  - 2x `QualitySettings::set_vSyncCount`
  - 2x `EnumGamePrefGroup::NeedsReset`
  - 2x `EnumGamePrefGroup::Reset`
  - 2x `GameObject::AddComponent`
  - 2x `ThreadManager::RunCoroutineSync`
  - 2x `GamePrefs::GetBool`
  - 2x `Object::op_Implicit`
  - 2x `Resources::UnloadAsset`
  - 1x `new <>c__DisplayClass125_0::.ctor`
  - 1x `GameEntrypoint::get_EntrypointSuccess`
  - 1x `new MicroStopwatch::.ctor`
#### callers of `AstarManager::Init`
#### callers of `AIDirector::.ctor`
- `WorldState::SetFrom`
