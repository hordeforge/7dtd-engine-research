# Dedicated leaf types (V3.0.1)

**Kind:** per-leaf reference for small dedicated-relevant types that execute on a
headless server but are each too minor for their own doc. Each row is a reachable
game type grouped under the subsystem doc that owns its concept, with its base class,
role, and behavioral method fingerprint. Substantive groups (AI, loot, items,
spawning, quests, combat) also get full prose in their owning doc; a few rows are
**client-only** (reachable but their work is client-side), marked and cross-narrated.  
**Basis:** base + fingerprint are IL-derived (`tools/src/LeafInfo`); roles are IL-verified
for the narrated groups, else the humanized name. Verify a leaf against its IL first.  
**Hub:** [`../INDEX.md`](../INDEX.md). **Method:** [`../re-methodology.md`](../re-methodology.md).

**88 leaf types**, grouped by owning subsystem.

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
| `ModeGamePref` | Mode Game Pref | `ValueType` | (fields only) |
| `VariableStateGameInfoInt` | Variable State Game Info Int | `VariableStateSimpleLookupAbs` | getCurrentValue |
| `VariableStateGameInfoString` | Variable State Game Info String | `VariableStateSimpleLookupAbs` | getCurrentValue |

## save-persistence / save-region (3)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `BarRegion` | Bar Region | `ValueType` | (fields only) |
| `BarRegionFloat` | Bar Region Float | `ValueType` | (fields only) |
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
| `MethodSignature` | Method Signature | `Object` | (fields only) |
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
## Changelog

- **2026-07-24:** Added 48 types promoted out of the out-of-scope classification after a referrer scan (`tools/src/RefScan`) showed server-only referrers; name-based classification had put them in the wrong bucket.
- **2026-07-24:** Promoted to a full per-leaf reference (IL-derived base + fingerprint via `tools/src/LeafInfo`); substantive groups (AI/loot/items/spawning/quests/combat) narrated in prose in their owning docs, client-only leaves marked.
