# Dedicated leaf types (V3.1.0)

**Kind:** per-leaf reference for small dedicated-relevant types that execute on a
headless server but are each too minor for their own doc. Each row is a reachable
game type grouped under the subsystem doc that owns its concept, with its base class,
role, and behavioral method fingerprint. Substantive groups (AI, loot, items,
spawning, quests, combat) also get full prose in their owning doc; a few rows are
**client-only** (reachable but their work is client-side), marked and cross-narrated.  
**Basis:** base + fingerprint are IL-derived (`tools/src/LeafInfo`); roles are IL-verified
for the narrated groups, else the humanized name. Verify a leaf against its IL first.  
**Maintenance:** tool-assisted but **hand-maintained**, not push-button. The base
and fingerprint columns come from `tools/src/LeafInfo`, and the promoted section was
derived with `tools/src/RefScan`, but the roles and the owner grouping were written
by hand. Regenerate the *columns* if the game updates; do not regenerate the file
wholesale, or the referrer-verified promotions and the IL-verified roles are lost.  
**Hub:** [`../INDEX.md`](../INDEX.md). **Method:** [`../re-methodology.md`](../re-methodology.md).

**88 leaf types** in the base catalog below, plus the promoted sections further down (the file's total row count is higher; see those sections for provenance).

## blocks / block-shapes (11)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `BlockPlacementPineLeaves` | Block Placement Pine Leaves | `BlockPlacement` | OnPlaceBlock |
| `BlockPlacementPlate` | Block Placement Plate | `BlockPlacement` | OnPlaceBlock |
| `BlockPlacementSpotlight` | Block Placement Spotlight | `BlockPlacement` | OnPlaceBlock |
| `BlockPlacementTorch` | Block Placement Torch | `BlockPlacement` | OnPlaceBlock |
| `BlockPlacementTowardsPlacer90` | Block Placement Towards Placer90 | `BlockPlacement` | OnPlaceBlock |
| `BlockPlacementTowardsPlacerInverted` | Block Placement Towards Placer Inverted | `BlockPlacement` | OnPlaceBlock |
| `BlockShapeBillboardComplex` | Block Shape Billboard Complex | `BlockShapeBillboardAbstract` | renderFull |
| `BlockShapeBillboardDiagonal` | Block Shape Billboard Diagonal | `BlockShapeBillboardAbstract` | renderFull |
| `BlockStatistics` | Block Statistics | `ValueType` | Clear |
| `BuildStabilityBlocks` | Build Stability Blocks | `Object` | RegisterWhenDone |
| `DestroyBlockBehavior` | Destroy Block Behavior | `Object` | (fields only) |

## buffs (1)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `BuffManager` | Buff Manager | `Object` | Cleanup, GetBuff, AddBuff |

## combat-damage (2)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `AttackHitInfo` | mutable hit-result carrier (block half + entity half) threaded through DamageBlock | `Object` | (fields only) |
| `BodyParts` | **client-only**: avatar render-rig held-item attach holder | `Object` | (fields only) |

## combat-damage / items (2)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `ApplyExplosionForce` | **client-only**: explosion debris/ragdoll knockback MonoBehaviour | `MonoBehaviour` | Explode |
| `StunBeamWeapon` | drone stun-beam: sets _droneStunDamage cvar + buffShocked (server), particles (client) | `Weapon` | Fire, Init |

## entities (2)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `EntityAnimalSnake` | Entity Animal Snake | `EntityEnemyAnimal` | GetAttackTargetHitPosition |
| `EntityNetworkHoldingData` | Entity Network Holding Data | `Object` | (fields only) |

## entity-ai / uai (11)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `AIFocusAim` | resolves a world-space aim point from the target body per AIAimFocusOffset (bandit-only) | `ValueType` | GetActiveFocus |
| `AIFocusBody` | resolves a body yaw toward the target (bandit / EAIPathTest) | `ValueType` | GetActiveFocus, TryGetValue, GetActiveFocusForPriority |
| `AIFocusConditionDistance` | expiry condition that disables a focus beyond ConditionalDistanceSq | `ValueType` | IsFocusDisabled |
| `EAIBlockingTargetTask` | no-op latch blocking target re-acquisition while an entity walks home | `EAIBase` | Init, CanExecute, Continue |
| `EAISetNearestEntityAsTargetSorter` | IComparer sorting target candidates nearest-first by distance | `Object` | Compare |
| `UAIConsiderationSelfHealth` | utility-AI score of own health fraction (dormant in stock) | `UAIConsiderationBase` | Init, GetScore |
| `UAIConsiderationSelfVisible` | utility-AI score of self-exposure to the target (dormant) | `UAIConsiderationBase` | GetScore |
| `UAIConsiderationTargetDistance` | utility-AI linear ramp over squared target distance (dormant) | `UAIConsiderationBase` | GetScore, Init |
| `UAIConsiderationTargetHealth` | utility-AI score of target vitality / block-hp fraction (dormant) | `UAIConsiderationBase` | GetScore |
| `UAIConsiderationTargetType` | utility-AI binary type-name filter on the candidate (dormant) | `UAIConsiderationBase` | GetScore, Init |
| `UAIConsiderationTargetVisible` | utility-AI binary line-of-sight to the candidate (dormant) | `UAIConsiderationBase` | GetScore |

## game-events / minevents (3)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `GameEventFlag` | Game Event Flag | `Object` | (fields only) |
| `SequenceLink` | Sequence Link | `Object` | CheckLink |
| `SequenceStopper` | Sequence Stopper | `Object` | (fields only) |

## items (7)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `ItemActionDataVomit` | runtime state for the AI cop-spit vomit attack | `ItemActionDataLauncher` | (fields only) |
| `ItemActionDynamicData` | animation-driven melee sweep state (ray + per-swing hit dedupe) | `ItemActionAttackData` | (fields only) |
| `ItemActionDynamicMeleeData` | adds the player swing-phase machine to the dynamic melee state | `ItemActionDynamicData` | (fields only) |
| `ItemActionReplaceBlockData` | ranged replace/paint state that lands as server BlockChangeInfo | `ItemActionDataRanged` | (fields only) |
| `ItemClassArmor` | armor ItemClass (equip slot, armor group, cosmetic, keep-on-death) | `ItemClass` | Init, CanEquip, KeepOnDeath |
| `ItemId` | (id,count) Int16 pair, the AI director tracked-inventory record | `ValueType` | FromStack, Write, Read |
| `ItemWorldData` | dropped-item world context (EntityItem, owner id) for the on-world hooks | `Object` | (fields only) |

## light-mesh-water (3)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `WaterPoint` | Water Point | `ValueType` | (fields only) |
| `WaterStats` | Water Stats | `ValueType` | Sum, ResetFrame |
| `WaterStatsProfiler` | Water Stats Profiler | `Object` | SampleTick |

## loot-economy (8)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `BaseLootEntryRequirement` | abstract per-LootEntry gate (CheckRequirement), ANDed in the server loot roll | `Object` | CheckRequirement, Init |
| `LootEntryRequirementBiome` | passes when the player standing-biome is in the list | `BaseLootEntryRequirement` | Init, CheckRequirement |
| `LootEntryRequirementCVar` | compares a player cvar against a value via the operation comparator | `BaseOperationLootEntryRequirement` | Init, LeftSide, RightSide |
| `LootEntryRequirementProgression` | compares a progression level against a value via operation | `BaseOperationLootEntryRequirement` | Init, LeftSide, RightSide |
| `LootEntryRequirementQuestTags` | passes when the active quest tags overlap the requirement | `BaseLootEntryRequirement` | Init, CheckRequirement |
| `LootEntryRequirementRandomRoll` | compares a lerped random roll against a value via operation | `BaseOperationLootEntryRequirement` | Init, LeftSide, RightSide |
| `TraderStageTemplate` | {Min,Max,Quality} trader-stage range record (server-loaded, client-UI evaluated) | `Object` | IsWithin |
| `TraderStageTemplateGroup` | named OR-list of trader-stage templates (server-loaded, client-UI evaluated) | `Object` | IsWithin |

## quests-challenges (4)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `BaseQuestCriteria` | base quest-availability check (own checks are true stubs) | `Object` | CheckForQuestGiver, CheckForPlayer, HandleVariables |
| `QuestCriteriaPOIWithinDistance` | POI-in-range criteria, hardcoded false in V3.0.1 (dead) | `BaseQuestCriteria` | CheckForQuestGiver |
| `QuestTierReward` | Tier + rewards, paid once on a faction quest-tier increase | `Object` | GiveRewards |
| `SharedQuestEntry` | party-shared quest offer entry in the QuestJournal | `Object` | Clone |

## sandbox-options / game-events (3)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `ModeGamePref` | mode-scoped pref record {GamePref, ValueType, DefaultValue}; ctor prefers the `DeviceFlag` 2 entry of deviceDefaults, else the plain default (server-lifecycle §2.1) | `ValueType` | .ctor |
| `VariableStateGameInfoInt` | **client-only** binding var: `GameServerInfo.GetValue(GameInfoInt)` (LocalServerInfo when server, LastGameServerInfo when client) | `VariableStateSimpleLookupAbs` | getCurrentValue, get_VarName |
| `VariableStateGameInfoString` | **client-only** binding var: `GameServerInfo.GetValue(GameInfoString)`, same server/client source split | `VariableStateSimpleLookupAbs` | getCurrentValue, get_VarName |

## save-persistence / save-region (3)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `BarRegion` | **client-only** `XUiC_DataManagementBar` region record `{Start, Size, End = Start + Size}` (int64), static `None = (0, 0)` | `ValueType` | .ctor, Equals |
| `BarRegionFloat` | **client-only** `XUiC_SizeBar` region record `{Start, Size, End = Start + Size}` (float), static `None = (0, 0)` | `ValueType` | .ctor, Equals |
| `SaveDataLimitUtils` | Save Data Limit Utils | `Object` | CalculatePlayerMapSize |

## server-lifecycle (4)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `DirectoryPlayerId` | Directory Player Id | `Object` | (fields only) |
| `PlayerCluster` | Player Cluster | `Object` | (fields only) |
| `SPlayerDisconnectedData` | S Player Disconnected Data | `ValueType` | (fields only) |
| `SSavePlayerDataData` | S Save Player Data Data | `ValueType` | (fields only) |

## signs (3)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `MethodSignature` | **client-only** `ObjectMessaging` method-key record: lazy hash = ReturnType hash XORed with each argument-type hash | `Object` | GetHashCode |
| `SignBakeRequest` | Sign Bake Request | `ValueType` | CompareTo |
| `SignComplexityInfo` | Sign Complexity Info | `ValueType` | TryGetLayerComplexityInfo |

## spawning (5)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `EntitySpawnerClassForDay` | day-indexed EntitySpawnerClass schedule read by EntitySpawner | `Object` | Day, AddForDay, Count |
| `SPlayerSpawnedInWorldData` | in-process PlayerSpawnedInWorld ModEvents payload (not a wire struct) | `ValueType` | (fields only) |
| `SPlayerSpawningData` | in-process PlayerSpawning ModEvents payload (not a wire struct) | `ValueType` | (fields only) |
| `SpawnEntry` | per-game-event spawned-entity record (forces aggressive spawns near players) | `Object` | HandleUpdate |
| `SupplyCrateSpawn` | pending air-drop crate queued by AIAirDrop.CreateFlightPaths | `Object` | (fields only) |

## tile-entities-power (1)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `PowerConsumerSingle` | Power Consumer Single | `PowerItem` | HandlePowerUpdate, SetValuesFromBlock |

## vehicles-drones-turrets (5)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `DroneLightManager` | Drone Light Manager | `MonoBehaviour` | InitMaterials, DisableMaterials, getLightEffect |
| `EModelDrone` | E Model Drone | `EModelBase` | Init, createAvatarController |
| `ItemActionDataSpawnTurret` | Item Action Data Spawn Turret | `ItemActionAttackData` | (fields only) |
| `ItemActionDataSpawnVehicle` | Item Action Data Spawn Vehicle | `ItemActionAttackData` | (fields only) |
| `TurretEntitySorter` | Turret Entity Sorter | `Object` | isNearer, DistanceSqr, Compare |

## world-chunks / save-region (4)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `ChunkBlockClearData` | Chunk Block Clear Data | `ChunkCustomData` | OnRemove |
| `ChunkGameObjectLayer` | Chunk Game Object Layer | `Object` | Cleanup, Init, Reset |
| `ChunkMemoryStreamReader` | Chunk Memory Stream Reader | `MemoryStream` | Close |
| `ChunkMemoryStreamWriter` | Chunk Memory Stream Writer | `MemoryStream` | Init, Close |

## world-generation / chunk-providers (6)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `BiomeBlockDecoration` | biomes.xml runtime chunk deco/resource rule | `Object` | GetRandomRotation |
| `EventPrefabsClient` | **client-effect only** (allocated server-side): `World.LoadWorld` constructs it on both sides, but `TryAdd`/`Remove` are called only from the ToClient `NetPackageEventPrefab` / `NetPackageWorldInitInfo` handlers, so it stays empty on a dedicated server | `Object` | Remove, TryAdd |
| `GorePrefab` | **client-only**: gore object spawn-sound MonoBehaviour | `RootTransformRefEntity` | Start |
| `PrefabGameObject` | **client-only**: POI imposter mesh holder (LOD) | `Object` | (fields only) |
| `PrefabGroupEntry` | **client-only**: prefab-editor UI list row | `XUiListEntry`1` | CompareTo, MatchesSearch |
| `PrefabListData` | QuestEventManager runtime POI-by-difficulty-tier bucketing | `Object` | AddPOI, ShuffleDifficulty |


---

## Promoted from out-of-scope (referrer-verified)

These were first classified out-of-scope by a **name heuristic** and later found to
have server-only referrers by a batch reverse-reference scan (`tools/src/RefScan`).
Name is a poor signal here: `ClientAmmoData` is turret state on a server tile
entity, `StreamReadSizeMarker` is wire-framing infrastructure, and `ClientLobbyManager`
sits in the server authorizer path. Referrers are the evidence column.

### aidirector / spawning (2)

| Leaf | Base | Key methods | Server referrers |
|---|---|---|---|
| `ManagedZombie` | `Object` | (fields only) | `AIDirectorBloodMoonParty` |
| `SupplyCrateCache` | `Object` | (fields only) | `AIDirectorAirDropComponent`, `RegionFileManager` |

### dynamic-mesh (1)

| Leaf | Base | Key methods | Server referrers |
|---|---|---|---|
| `DynamicMeshChunkDataStorage` | `(not found)` | (fields only) | `NetPackageDynamicMesh` |

### entity-ai / entities (6)

| Leaf | Base | Key methods | Server referrers |
|---|---|---|---|
| `AIFocus` | `(not found)` | (fields only) | `EntityBandit` |
| `AttachedToEntitySlotInfo` | `Object` | (fields only) | `Entity`, `EntityAlive`, `EntityVehicle` |
| `FallBehavior` | `Object` | (fields only) | `EntityAlive`, `EntityHuman` |
| `NetworkStatChange` | `Object` | (fields only) | `EntityAlive` |
| `SEntityKilledData` | `ValueType` | (fields only) | `EntityAlive` |
| `ServerHelper` | `Object` | SetupForServer | `EntityAlive` |

### entity-stats (1)

| Leaf | Base | Key methods | Server referrers |
|---|---|---|---|
| `ModifierValuesAndSources` | `Object` | (fields only) | `EntityStats`, `PassiveEffect`, `PlayerEntityStats` |

### items (10)

| Leaf | Base | Key methods | Server referrers |
|---|---|---|---|
| `ChannelMask` | `ValueType` | ToggleChannel, IncludesChannel, SetExclusiveChannel | `ItemActionTextureBlock` |
| `CollectWaterActionData` | `ItemActionAttackData` | (fields only) | `ItemActionCollectWater` |
| `CollectWaterUtils` | `Object` | CollectWater, GenerateCollectionPositions | `ItemActionCollectWater` |
| `ConnectPowerData` | `ItemActionAttackData` | (fields only) | `ItemActionConnectPower`, `ItemActionDisconnectPower`, `NetPackageWireToolActions` |
| `DumpWaterActionData` | `ItemActionAttackData` | (fields only) | `ItemActionDumpWater` |
| `FeedInventoryData` | `ItemActionAttackData` | (fields only) | `ItemActionUseOther` |
| `InventoryDataMelee` | `ItemActionAttackData` | (fields only) | `ItemActionMelee` |
| `InventoryDataRepair` | `ItemActionAttackData` | (fields only) | `ItemActionRepair` |
| `OnActivateItemGameObjectReference` | `MonoBehaviour` | IsActivated, ActivateItem | `ItemClassTimeBomb`, `ItemClassTorch` |
| `PerlinNoise` | `Object` | Noise, Noise, Lattice, FBM | `ItemActionRanged` |

### managers / loop (4)

| Leaf | Base | Key methods | Server referrers |
|---|---|---|---|
| `EntityItemLifetimeComparer` | `Object` | Compare | `GameManager` |
| `ExplodeGroup` | `Object` | (fields only) | `GameManager` |
| `SChatMessageData` | `ValueType` | (fields only) | `GameManager` |
| `SGameMessageData` | `ValueType` | (fields only) | `GameManager` |

### platform-auth (2)

| Leaf | Base | Key methods | Server referrers |
|---|---|---|---|
| `ClientAuthenticateServerContext` | `Object` | DisconnectNoCrossplay, DisconnectNoCrossplay, Success | `ConnectionManager` |
| `ClientLobbyManager` | `Object` | RegisterLobbyClient, OnClientDisconnected, TryGetLobbyId | `AuthorizationManager`, `NetPackageLobbyRegisterClient` |

### save-region / server-lifecycle (4)

| Leaf | Base | Key methods | Server referrers |
|---|---|---|---|
| `LongSetGroups` | `Object` | RemoveGroupedKeys, MergeOrCreateGroup, Clear, TryGetGroup | `RegionFileManager` |
| `ProtectedBackpack` | `ValueType` | (fields only) | `PersistentPlayerData`, `RegionFileManager` |
| `ProtectedPositionCache` | `Object` | ClearAll | `RegionFileManager` |
| `RegionExtensions` | `Dictionary`2` | (fields only) | `RegionFileAccessMultipleChunks` |

### spawning (1)

| Leaf | Base | Key methods | Server referrers |
|---|---|---|---|
| `PList` | `(not found)` | (fields only) | `EntitySpawner` |

### tile-entities-power (1)

| Leaf | Base | Key methods | Server referrers |
|---|---|---|---|
| `LegacyState` | `ValueType` | (fields only) | `TileEntityComposite`, `TileEntityLegacyUtils` |

### vehicles-drones-turrets (5)

| Leaf | Base | Key methods | Server referrers |
|---|---|---|---|
| `ClientAmmoData` | `Object` | (fields only) | `AutoTurretFireController`, `TileEntityPoweredRangedTrap` |
| `ClientTriggerData` | `Object` | (fields only) | `TileEntityPoweredTrigger` |
| `FireControllerUtils` | `Object` | SpawnParticleEffect | `AutoTurretFireController` |
| `Motor` | `Object` | (fields only) | `EntityVehicle` |
| `Wheel` | `Object` | (fields only) | `EntityVGyroCopter`, `EntityVHelicopter`, `EntityVJeep` |

### wire / serialization (protocol-packages) (6)

| Leaf | Base | Key methods | Server referrers |
|---|---|---|---|
| `BitConverterLE` | `Object` | GetULongBytes, UIntFromBytes, GetUIntBytes, ULongFromBytes | `PooledBinaryReader`, `PooledBinaryWriter` |
| `ByteLengthUtils` | `Object` | GetBinaryWriter7BitEncodedIntLength, GetBinaryWriterLength | `NetPackagePlayerLoginAnswer` |
| `NetPackageInformation` | `(not found)` | (fields only) | `NetPackageManager` |
| `StreamReadSizeMarker` | `ValueType` | (fields only) | `PooledBinaryReader`, `TileEntityComposite` |
| `StreamWriteSizeMarker` | `ValueType` | (fields only) | `PooledBinaryWriter` |
| `UnknownNetPackageException` | `Exception` | (fields only) | `NetPackageManager` |

### world-chunks (2)

| Leaf | Base | Key methods | Server referrers |
|---|---|---|---|
| `GroupBounds` | `ValueType` | IsWithinSize | `World` |
| `VolumeKey` | `ValueType` | (fields only) | `World` |

### world-generation (1)

| Leaf | Base | Key methods | Server referrers |
|---|---|---|---|
| `MinHeapBinned` | `ValueType` | Add, ExtractFirst, Reset, Init | `WorldGenerationEngineFinal.PathingUtils` |

### world-generation / chunk-providers (2)

| Leaf | Base | Key methods | Server referrers |
|---|---|---|---|
| `PlaceholderTarget` | `ValueType` | (fields only) | `BlockPlaceholderMap` |
| `PrefabVolumeListAbs` | `Object` | (fields only) | `DynamicPrefabDecorator`, `EntityPlayer`, `PrefabData` |

---

## Promoted from out-of-scope, round 2 (dominance rule)

An independent review found the out-of-scope bucket had never been referrer-verified
and named `ClientPowerData` as a counter-example. Re-sweeping with `tools/src/RefScan`
confirmed it (14 `TileEntityPowerSource` referrers including `read`/`write`) and
exposed a flaw in the earlier promotion rule: it required **zero** client referrers, so
a type that is overwhelmingly server-side but touched once by a UI window stayed
misclassified. The rule is now **dominance** (server referrers outnumber client ones).

### dynamic-mesh (7)

| Leaf | Server referrers |
|---|---|
| `DisabledImposterChunkManager` | DynamicMeshManager |
| `DyMeshRegionLoadRequest` | DynamicMeshManager, DynamicMeshRegionDataStorage |
| `DynamicMeshChunkDataStorage` | DynamicMeshBuilderManager, DynamicMeshChunkProcessor |
| `DynamicMeshChunkDataWrapper` | DynamicMeshChunkDataStorage, DynamicMeshChunkProcessor |
| `DynamicMeshVoxelLoad` | DynamicMeshChunkProcessor, DynamicMeshItem |
| `MeshCalculations` | DynamicMeshChunkProcessor, DynamicMeshVoxelRegionLoad |
| `TerrainSubMesh` | DynamicMeshChunkProcessor, DynamicMeshFile |

### entity-ai / uai (1)

| Leaf | Server referrers |
|---|---|
| `AIFocus` | EntityBandit |

### managers (1)

| Leaf | Server referrers |
|---|---|
| `ModEvent` | ConnectionManager, EntityAlive, GameManager |

### protocol-packages (1)

| Leaf | Server referrers |
|---|---|
| `NetPackageInformation` | NetPackageManager |

### spawning (1)

| Leaf | Server referrers |
|---|---|
| `PList` | EntitySpawner |

### tile-entities-power (2)

| Leaf | Server referrers |
|---|---|
| `ClientPowerData` | TileEntityPowerSource (ctor, read, write) |
| `TileEntityExtensions` | EntityMoveHelper, GameManager, NetPackageLandClaimRepair |

### vehicles-drones-turrets (1)

| Leaf | Server referrers |
|---|---|
| `CollisionCallForward` | EntityTurret, EntityVehicle |

### world-chunks / chunk-providers (1)

| Leaf | Server referrers |
|---|---|
| `WorldGridCompressedData` | ChunkProviderGenerateWorldFromRaw, World |

### world-generation / chunk-providers (4)

| Leaf | Server referrers |
|---|---|
| `Cell` | Prefab |
| `PrefabVolumeAbs` | DynamicPrefabDecorator, Prefab, NetPackageEditorUpdateVolume |
| `PrefabVolumeListAbs` | DynamicPrefabDecorator, EntityPlayer, Prefab |
| `SimpleBitStream` | Prefab |
## Changelog

- **2026-07-26:** Round-2 promotion of 19 gameplay types out of the out-of-scope bucket after an independent review showed it was never referrer-verified; promotion rule changed from zero-client-referrers to server-dominance.
- **2026-07-24:** Added 48 types promoted out of the out-of-scope classification after a referrer scan (`tools/src/RefScan`) showed server-only referrers; name-based classification had put them in the wrong bucket.
- **2026-07-24:** Promoted to a full per-leaf reference (IL-derived base + fingerprint via `tools/src/LeafInfo`); substantive groups (AI/loot/items/spawning/quests/combat) narrated in prose in their owning docs, client-only leaves marked.

## Promoted unaccounted server surface (2026-07-28)

Types that were in the Coverage unaccounted set, confirmed **server-dominant** (or
reflection/XML-reached) by `tools/src/RefScan`, and not already in the leaf catalog.
Fingerprints from `tools/src/LeafInfo`. Roles are name-derived; verify against IL
before treating a row as a behavioral claim. Infra collections are classified in
[`out-of-scope-surface.md`](../out-of-scope-surface.md) instead.

### aidirector / spawning (5)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `AIDirectorPlayerState` | AIDirector Player State | `Object` | Construct, Reset, Cleanup |
| `Horde` | Horde | `Object` | SpawnMore, Tick, Destroy, SetSpawnPos |
| `AIDirectorData` | AIDirector Data | `Object` | FindNoise, Cleanup, AddNoisySound, InitStatic |
| `AIDirectorChunkEvent` | AIDirector Chunk Event | `Object` | Read, Write |
| `AIDirectorHordeComponent` | AIDirector Horde Component | `AIDirectorComponent` | FindTargets, FindScoutStartPos, FindOnGroundPos |

### blocks (11)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `BlockNodeMap` | Block Node Map | `Object` | Refresh, PopulateFromFile, TryGetValue, PopulateFromRoot |
| `BlockSwitchController` | Block Switch Controller | `MonoBehaviour` | UpdateLights, SetState, Start |
| `ShapeCategory` | Shape Category | `Object` | CompareTo, CompareTo |
| `BlockSwitchSingleController` | Block Switch Single Controller | `MonoBehaviour` | SetState, SetState, Start |
| `BlockingQueue` | Blocking Queue | `Object` | (generic/nested; see IL) |
| `POIBoundsSideHelper` | POIBounds Side Helper | `MonoBehaviour` | SetSize, OnTriggerEnter, OnTriggerExit, Setup |
| `BlockActivationCommand` | Block Activation Command | `ValueType` | (fields only) |
| `BlockPlacementDrawBridge` | Block Placement Draw Bridge | `BlockPlacementTowardsPlacer` | LimitRotation |
| `BlockPlacementTowardsPlacer` | Block Placement Towards Placer | `BlockPlacement` | OnPlaceBlock |
| `BlockData` | Block Data | `Object` | (fields only) |
| `BlockData` | Block Data | `Object` | (fields only) |

### entities (11)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `EntityLockContext` | Entity Lock Context | `Object` | Write, Read |
| `EntityInstanceAssets` | Entity Instance Assets | `Object` | Load, WaitForComplete, Release, OnPrefabLoaded |
| `EntityCreateHandle` | Entity Create Handle | `Object` | TryComplete, WaitForComplete |
| `AutoMove` | Auto Move | `Object` | Update, StartOrbit, StartLine, StartRelative |
| `EntityTraderLockContext` | Entity Trader Lock Context | `Object` | Read, Write |
| `PhysicsBodyColliderConfiguration` | Physics Body Collider Configuration | `Object` | Read, Write, vecFromString, vecToString |
| `PhysicsBodyInstance` | Physics Body Instance | `Object` | bindCollider, GetTransformForColliderTag, SetColliderMode, BindColliders |
| `VendingMachineLockContext` | Vending Machine Lock Context | `Object` | Read, Write |
| `EntityFlying` | Entity Flying | `EntityEnemy` | MoveEntityHeaded, IsAirBorne |
| `EntityZombie` | Entity Zombie | `EntityHuman` | (fields only) |
| `EAITaskEntry` | EAITask Entry | `Object` | (fields only) |

### items / traders (22)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `PreviewData` | Preview Data | `Object` | GetDisplayValues |
| `Bonuses` | Bonuses | `ValueType` | (fields only) |
| `FuelType` | Fuel Type | `Object` | (fields only) |
| `InventoryBase` | Inventory Base | `Object` | (fields only) |
| `ItemActionDataCatapult` | Item Action Data Catapult | `ItemActionDataLauncher` | (fields only) |
| `ItemActionDataSpawnEntity` | Item Action Data Spawn Entity | `ItemActionAttackData` | (fields only) |
| `ItemActionDataZoom` | Item Action Data Zoom | `ItemActionData` | (fields only) |
| `MyInventoryData` | My Inventory Data | `ItemActionAttackData` | (fields only) |
| `MyInventoryData` | My Inventory Data | `ItemActionAttackData` | (fields only) |
| `MyInventoryData` | My Inventory Data | `ItemActionAttackData` | (fields only) |
| `MyInventoryData` | My Inventory Data | `ItemActionAttackData` | (fields only) |
| `MyInventoryData` | My Inventory Data | `ItemActionAttackData` | (fields only) |
| `MyInventoryData` | My Inventory Data | `ItemActionAttackData` | (fields only) |
| `MyInventoryData` | My Inventory Data | `ItemActionAttackData` | (fields only) |
| `MyInventoryData` | My Inventory Data | `ItemActionAttackData` | (fields only) |
| `MyInventoryData` | My Inventory Data | `ItemActionAttackData` | (fields only) |
| `MyInventoryData` | My Inventory Data | `ItemActionAttackData` | (fields only) |
| `TierItemGroup` | Tier Item Group | `Object` | (fields only) |
| `TraderItem` | Trader Item | `Object` | (fields only) |
| `TraderItemEntry` | Trader Item Entry | `Object` | (fields only) |
| `TraderItemGroup` | Trader Item Group | `Object` | (fields only) |
| `WorkstationData` | Workstation Data | `Object` | (fields only) |

### light-mesh-water (6)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `WaterSimulationCalcFlows` | Water Simulation Calc Flows | `ValueType` | ProcessFlows, ProcessFlowSide, ProcessFlowBelow, ProcessGroundWaterFlowSide |
| `WaterNeighborCacheNative` | Water Neighbor Cache Native | `ValueType` | TryGetNeighbor, SetChunk, SetVoxel, InitializeCache |
| `WaterSimulationPreProcess` | Water Simulation Pre Process | `ValueType` | Execute, WakeNeighbor, WakeNeighbor, TryTrackChunk |
| `WaterSimulationApplyFlows` | Water Simulation Apply Flows | `ValueType` | Execute, WakeNeighbor, WakeNeighbor |
| `WaterConstants` | Water Constants | `Object` | GetStableMassBelow |
| `WaterSimulationPostProcess` | Water Simulation Post Process | `ValueType` | Execute |

### mixed server surface (52)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `PrefabChunk` | Prefab Chunk | `Object` | checkCoordinates, IsAir, GetTerrainHeight, GetBlockFaceTexture |
| `PrefabHelpers` | Prefab Helpers | `Object` | smoothChunk, SimplifyPrefab, mergePrefab, combine |
| `Vector2i` | Vector2i | `ValueType` | Normalize, Distance, DistanceSqr, DistanceSqrInt |
| `ProfilerUtils` | Profiler Utils | `Object` | GetAvailableMetricsCsv, AppendLastValue, CalculateTextureSizeBytes, CalculateUnsafeParallelHashMapBytes |
| `EnumDecoAllowedExtensions` | Enum Deco Allowed Extensions | `Object` | ToStringInternal, ToStringFriendlyCached, WithStreetOnly, IsNothing |
| `SmartArray` | Smart Array | `Object` | set, get, clear, read |
| `RingBuffer` | Ring Buffer | `Object` | (generic/nested; see IL) |
| `ArrayWithOffset` | Array With Offset | `Object` | (generic/nested; see IL) |
| `ProceduralGridMover` | Procedural Grid Mover | `Object` | UpdateGraph, PointToGraphSpace, UpdateGraphCoroutine |
| `UnsafeBitArraySetIndicesEnumerator` | Unsafe Bit Array Set Indices Enumerator | `ValueType` | MoveNext, Reset, Dispose |
| `UpdatePhysics` | Update Physics | `Object` | MoveNext, Dispose, Reset |
| `Contextual` | Contextual | `Object` | DoesWorldExist, FindWorld, FindActiveWorld, FindDownloadedRemoteWorld |
| `ReadOnlyListWrapper` | Read Only List Wrapper | `Object` | (generic/nested; see IL) |
| `RegionData` | Region Data | `Object` | Load, Save, SetChunkData, GetChunkData |
| `ThreadInfo` | Thread Info | `Object` | WaitForEnd, RequestTermination, TerminationRequested, HasTerminated |
| `VoxelNode` | Voxel Node | `LevelGridNode` | UpdateRecursiveG, ClearCustomConnections, Reset, Cleanup |
| `HitLocation` | Hit Location | `TargetedCompareRequirementBase` | ParseXAttribute, IsValid, GetInfoStrings |
| `IOUtils` | IOUtils | `Object` | HashUint, CalcHashSync, CalcHashCoroutine, CalcCrcCoroutine |
| `NoThreadingSemantics` | No Threading Semantics | `Object` | InterlockedAdd, Synchronize, Synchronize |
| `ProfilerGameUtils` | Profiler Game Utils | `Object` | TryGetFlyingPlayer, WaitForSingleChunkToLoad, WaitForSingleChunkToLoad, WaitForChunksAroundObserverToLoad |
| `WaveReader` | Wave Reader | `Object` | Read, Cleanup |
| `BackedArrays` | Backed Arrays | `Object` | CreateSingleView, Create |
| `CompareItemMetaFloat` | Compare Item Meta Float | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute |
| `RegionItemData` | Region Item Data | `Object` | Update, Update |
| `CatalystConvert` | Catalyst Convert | `Object` | Convert |
| `ColorMappingData` | Color Mapping Data | `Object` | (fields only) |
| `LNLAuthConnectionState` | LNLAuth Connection State | `Object` | (fields only) |
| `ParsingMethodData` | Parsing Method Data | `Object` | TryGetDelegateForSourceType |
| `TaskGroup` | Task Group | `Object` | (fields only) |
| `TierSpec` | Tier Spec | `ValueType` | (fields only) |
| `TraderComparer` | Trader Comparer | `Object` | Compare |
| `Trajectory` | Trajectory | `Object` | Calculate, SuggestVelocity_CustomArc |
| `UnlockData` | Unlock Data | `Object` | (fields only) |
| `VoxeChunkInfo` | Voxe Chunk Info | `Object` | IsEmpty |
| `Arrays` | Arrays | `Object` | (fields only) |
| `AsyncItem` | Async Item | `Object` | (fields only) |
| `FunctionDefinition` | Function Definition | `Object` | (fields only) |
| `GroupOffsets` | Group Offsets | `ValueType` | WithOffsets |
| `ILockable` | ILockable | `` | GetHashForPassword |
| `Location` | Location | `Object` | (fields only) |
| `Node` | Node | `Object` | (fields only) |
| `ProfilerCaptureUtils` | Profiler Capture Utils | `Object` | CreateMemoryProfiler |
| `SBlockPosValue` | SBlock Pos Value | `ValueType` | (fields only) |
| `SEnts` | SEnts | `ValueType` | (fields only) |
| `SGameStartingData` | SGame Starting Data | `ValueType` | (fields only) |
| `SItemDropProb` | SItem Drop Prob | `ValueType` | (fields only) |
| `SNetPackageInfo` | SNet Package Info | `ValueType` | (fields only) |
| `SPlayerJoinedGameData` | SPlayer Joined Game Data | `ValueType` | (fields only) |
| `SpawnGroup` | Spawn Group | `Object` | (fields only) |
| `ThreadRegeneratingData` | Thread Regenerating Data | `Object` | (fields only) |
| `TrackedBlockData` | Tracked Block Data | `ValueType` | (fields only) |
| `Triangle` | Triangle | `ValueType` | (fields only) |

### network / protocol (6)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `NetConnectionStatistics` | Net Connection Statistics | `Object` | GetPackageTypes, RegisterReceivedPackage, RegisterSentPackage, GetStats |
| `NetConnectionSteam` | Net Connection Steam | `NetConnectionAbs` | Task_CommWriter, Task_CommReader, InitStreams, AppendToReaderStream |
| `NetPackageLight` | Net Package Light | `NetPackage` | ProcessPackage, write, read, Setup |
| `NetPackageTreeFade` | Net Package Tree Fade | `NetPackage` | ProcessPackage, write, Setup, read |
| `NetPackageDroneParticleEffect` | Net Package Drone Particle Effect | `NetPackage` | ProcessPackage, read, write, Setup |
| `NetEntityPackageQueue` | Net Entity Package Queue | `Object` | Cleanup, ProcessPackagesForEntity, EnqueueNetPackageForEntity, HasPackagesForEntity |

### quests / dialog (4)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `QuestEvent` | Quest Event | `Object` | Clone, HandleEvent, ParseProperties |
| `TrackingHandler` | Tracking Handler | `Object` | HandleTracking, Update, RemoveTrackingEntry, AddTrackingEntry |
| `PlayerQuestData` | Player Quest Data | `Object` | (fields only) |
| `DialogResponseEntry` | Dialog Response Entry | `BaseResponseEntry` | (fields only) |

### requirements / predicates (26)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `StatCompareAbs` | Stat Compare Abs | `TargetedCompareRequirementBase` | ParseXAttribute, GetInfoStrings, IsValid |
| `ArmorGroupCount` | Armor Group Count | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute, GetInfoStrings |
| `ArmorGroupLowestQuality` | Armor Group Lowest Quality | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute, GetInfoStrings |
| `BlockHasTags` | Block Has Tags | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute, GetInfoStrings |
| `BlockStandingOn` | Block Standing On | `TargetedCompareRequirementBase` | ParseXAttribute, IsValid, GetInfoStrings |
| `CVarCompare` | CVar Compare | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute, GetInfoStrings |
| `HasAttachedPrefab` | Has Attached Prefab | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute, GetInfoStrings |
| `HoldingItemHasTags` | Holding Item Has Tags | `TargetedCompareRequirementBase` | ParseXAttribute, IsValid, GetInfoStrings |
| `IsLookingAtBlock` | Is Looking At Block | `RequirementBase` | ParseXAttribute, IsValid, raycast |
| `ItemHasTags` | Item Has Tags | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute, GetInfoStrings |
| `NotHasBuff` | Not Has Buff | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute, GetInfoStrings |
| `PerksUnlocked` | Perks Unlocked | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute, GetInfoStrings |
| `PlayerItemCount` | Player Item Count | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute, GetInfoStrings |
| `ProgressionLevel` | Progression Level | `TargetedCompareRequirementBase` | IsValid, GetInfoStrings, ParseXAttribute |
| `RecipeUnlocked` | Recipe Unlocked | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute, GetInfoStrings |
| `RequirementItemModTier` | Requirement Item Mod Tier | `RequirementBase` | IsValid, ParseXAttribute, GetInfoStrings |
| `TriggerHasTags` | Trigger Has Tags | `TargetedCompareRequirementBase` | ParseXAttribute, IsValid, GetInfoStrings |
| `WornItemMods` | Worn Item Mods | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute, GetInfoStrings |
| `WornItems` | Worn Items | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute, GetInfoStrings |
| `EntityHasMovementTag` | Entity Has Movement Tag | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute |
| `EntityHasStanceTag` | Entity Has Stance Tag | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute |
| `EntityTagCompare` | Entity Tag Compare | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute |
| `IsStatAtMax` | Is Stat At Max | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute |
| `PlayerItemCountByTags` | Player Item Count By Tags | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute |
| `ProjectileHasTags` | Projectile Has Tags | `TargetedCompareRequirementBase` | IsValid, ParseXAttribute |
| `IsLookingAtEntity` | Is Looking At Entity | `IsLookingAtBlock` | ParseXAttribute |

### save / chunks (15)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `MapVisitor` | Map Visitor | `Object` | Stop, chunkXZtoBlockXZ, Start, chunkPosToBlockPos |
| `CachedStream` | Cached Stream | `Object` | EnterLock, ExitLock, Commit, Dispose |
| `SlotSizeData` | Slot Size Data | `Object` | UpdateLargestPriorityFileSize, SetFileSize, RemoveFileSize, RemoveFileSizes |
| `RegionFileSectorBased` | Region File Sector Based | `RegionFile` | Get, GetLocationInfo, SetLocationInfo, GetOffsetFromXz |
| `RegionFile` | Region File | `Object` | ConstructFullFilePath, ToShort, GetPositionAndPath, FromShort |
| `WorldBlockTickerEntry` | World Block Ticker Entry | `Object` | Write, Read, GetChunkKey, ToHashCode |
| `ChunkSnapshotUtil` | Chunk Snapshot Util | `Object` | LoadChunk, Free, TakeSnapshot, WriteSnapshot |
| `RegionFileChunkSnapshot` | Region File Chunk Snapshot | `Object` | Update, Write, Reset, Cleanup |
| `RegionFileFactoryRaw` | Region File Factory Raw | `Object` | CreateSnapshotUtil, CreateRegionFileAccess, CreateDebugUtil |
| `RegionFileFactorySectorBased` | Region File Factory Sector Based | `Object` | CreateSnapshotUtil, CreateRegionFileAccess, CreateDebugUtil |
| `SharedChunkObserverCache` | Shared Chunk Observer Cache | `Object` | removeChunkObserver, GetSharedObserverForChunk |
| `RegionFileChunkReader` | Region File Chunk Reader | `Object` | readIntoLoadStream, WriteBackup |
| `ScopedChunkAccess` | Scoped Chunk Access | `Object` | GetChunkReadAccess, GetChunkWriteAccess, GetChunkWriteAccess |
| `RegionFileChunkWriter` | Region File Chunk Writer | `Object` | WriteStreamCompressed |
| `RegionFilePlatform` | Region File Platform | `Object` | CreateFactory |

### uai / pathing (8)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `TraversalProvider` | Traversal Provider | `Object` | CanTraverse, CanTraverseConnection, GetTraversalCost |
| `TraversalProviderNoBreak` | Traversal Provider No Break | `Object` | CanTraverseConnection, CanTraverse, GetTraversalCost |
| `Context` | Context | `Object` | (fields only) |
| `FloodFillNodeScore` | Flood Fill Node Score | `Object` | (fields only) |
| `NearestEntitySorter` | Nearest Entity Sorter | `Object` | Compare |
| `PathNode` | Path Node | `ValueType` | Set |
| `RaycastNodeInfo` | Raycast Node Info | `Object` | (fields only) |
| `PathInfoSingleTarget` | Path Info Single Target | `PathInfo` | (fields only) |

### worldgen / sandbox / ops (35)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `FlatArea` | Flat Area | `Object` | IsValid, GetPositions, GetRandomPosition, IsInArea |
| `Builder` | Builder | `Object` | Build, SetPropId, SetPosition, SetRotation |
| `SandboxOptionValueSetBool` | Sandbox Option Value Set Bool | `SandboxOptionValueSet` | GetBoolIndex, GetBoolValue, GetDisplayAtIndex, IsValidIndex |
| `SandboxOptionValueSetInt` | Sandbox Option Value Set Int | `SandboxOptionValueSet` | GetDisplayAtIndex, GetIntIndex, GetIntValue, IsValidIndex |
| `WebCommandResult` | Web Command Result | `Object` | SendLines, GetDescription, SendLine, SendLog |
| `IntRange` | Int Range | `ValueType` | IsSet, RandomInclusive, Random |
| `Param` | Param | `Object` | FrameUpdate, SetTarget, Clamp, Set |
| `PoiMapElement` | Poi Map Element | `Object` | GetRandomDecal, GetRandomBlockOnTop, GetDecal |
| `ServerDateTimeRequest` | Server Date Time Request | `Object` | SwapEndianness, FetchNtpTimeAsync, GetNtpTimeAsync |
| `Stage` | Stage | `Object` | GetSpawnGroup, AddSpawnGroup |
| `District` | District | `Object` | Init |
| `Writer` | Writer | `ValueType` | Dispose, RecordChange |
| `IBiomeProvider` | IBiome Provider | `` | GetBiomeOrSubAt, Cleanup |
| `OutputType` | Output Type | `Object` | safeParseInt |
| `PlayerSpawn` | Player Spawn | `ValueType` | IsTooClose |
| `RandomCountyNameGenerator` | Random County Name Generator | `Object` | GetName |
| `TranslationData` | Translation Data | `ValueType` | (fields only) |
| `WorldCreationData` | World Creation Data | `Object` | Apply |
| `BiomePrefabDecoration` | Biome Prefab Decoration | `Object` | (fields only) |
| `BiomeStats` | Biome Stats | `Object` | (fields only) |
| `BiomeTypeData` | Biome Type Data | `Object` | (fields only) |
| `Config` | Config | `ValueType` | (fields only) |
| `ExitConnection` | Exit Connection | `Object` | (fields only) |
| `Force` | Force | `Object` | (fields only) |
| `LoadingStats` | Loading Stats | `Object` | (fields only) |
| `Noise` | Noise | `ValueType` | (fields only) |
| `OperationData` | Operation Data | `Object` | (fields only) |
| `POIWeightData` | POIWeight Data | `Object` | (fields only) |
| `PoiMapBlock` | Poi Map Block | `Object` | (fields only) |
| `PoiMapDecal` | Poi Map Decal | `Object` | (fields only) |
| `Sample` | Sample | `ValueType` | (fields only) |
| `TileGroup` | Tile Group | `Object` | (fields only) |
| `TownshipData` | Township Data | `Object` | (fields only) |
| `TownshipSpawnInfo` | Township Spawn Info | `Object` | (fields only) |
| `WildernessPathInfo` | Wilderness Path Info | `Object` | (fields only) |

### xml loaders (15)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `XmlFile` | Xml File | `Object` | load, load, SerializeToString, GetXpathResultsInList |
| `XmlPatcher` | Xml Patcher | `Object` | singlePatch, PatchXml, ReadPatchXmlWithFixedModFolders, redeclarationLog |
| `BiomeImageLoader` | Biome Image Loader | `ValueType` | BiomeIdToColor32, GetBiomeId, BiomeValueFromARGB32, BiomeValueFromRGBA32 |
| `EntityGroupsFromXml` | Entity Groups From Xml | `Object` | parseGroup, parseTextBasedList, parseElementBased, addEntity |
| `SoundsFromXml` | Sounds From Xml | `Object` | Parse, ParseSubtitleNode, ParseNode, CreateSounds |
| `BuffsFromXml` | Buffs From Xml | `Object` | ParseBuff, clearBuffValueLinks, CreateBuffs, Reload |
| `ItemModificationsFromXml` | Item Modifications From Xml | `Object` | parseItem, ParseModifier, ParseNode, Load |
| `XmlPatchException` | Xml Patch Exception | `Exception` | buildMessage |
| `BiomeSpawningFromXml` | Biome Spawning From Xml | `Object` | Load |
| `EntitySpawnerClassesFromXml` | Entity Spawner Classes From Xml | `Object` | LoadEntitySpawnerClasses |
| `MaterialsFromXml` | Materials From Xml | `Object` | CreateMaterials |
| `MusicDataFromXml` | Music Data From Xml | `Object` | Load |
| `WeatherSurvivalParametersFromXml` | Weather Survival Parameters From Xml | `Object` | Load |
| `XmlLoadInfo` | Xml Load Info | `Object` | XmlFileExists |
| `MiscFromXml` | Misc From Xml | `Object` | Create |

