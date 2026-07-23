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
*(raw IL listing elided for publication - regenerate locally with the Cecil dump tools; see INDEX.md)*
```

### Annotated `NetEntityDistributionEntry::updatePlayerEntity` IL=222

```
*(raw IL listing elided for publication - regenerate locally with the Cecil dump tools; see INDEX.md)*
```

### Annotated `NetEntityDistributionEntry::EncodePos` IL=20

```
*(raw IL listing elided for publication - regenerate locally with the Cecil dump tools; see INDEX.md)*
```

### Annotated `NetEntityDistributionEntry::EncodeRot` IL=7

```
*(raw IL listing elided for publication - regenerate locally with the Cecil dump tools; see INDEX.md)*
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
*(raw IL listing elided for publication - regenerate locally with the Cecil dump tools; see INDEX.md)*
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
