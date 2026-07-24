# Dedicated leaf types (V3.0.1)

**Kind:** per-leaf reference for small dedicated-relevant types that execute on a
headless server but are each too minor for their own doc: block-shape/placement
variants, item classes, AI considerations, loot/quest criteria, and the like. Each
row is a reachable game type grouped under the subsystem doc that owns its concept,
with its base class and the behavioral method fingerprint that distinguishes it.  
**Basis:** base + fingerprint are IL-derived (`tools/src/LeafInfo`); the **role** is
the humanized type name. The owning doc holds the framework; verify a specific leaf
against its IL before relying on details.  
**Hub:** [`../INDEX.md`](../INDEX.md). **Method:** [`../re-methodology.md`](../re-methodology.md).

**88 leaf types**, grouped by owning subsystem. Columns: leaf, role, base class, key methods (largest declared bodies).

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
| `AttackHitInfo` | Attack Hit Info | `Object` | (fields only) |
| `BodyParts` | Body Parts | `Object` | (fields only) |

## combat-damage / items (2)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `ApplyExplosionForce` | Apply Explosion Force | `MonoBehaviour` | Explode |
| `StunBeamWeapon` | Stun Beam Weapon | `Weapon` | Fire, Init |

## entities (2)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `EntityAnimalSnake` | Entity Animal Snake | `EntityEnemyAnimal` | GetAttackTargetHitPosition |
| `EntityNetworkHoldingData` | Entity Network Holding Data | `Object` | (fields only) |

## entity-ai / uai (11)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `AIFocusAim` | AI Focus Aim | `ValueType` | GetActiveFocus |
| `AIFocusBody` | AI Focus Body | `ValueType` | GetActiveFocus, TryGetValue, GetActiveFocusForPriority |
| `AIFocusConditionDistance` | AI Focus Condition Distance | `ValueType` | IsFocusDisabled |
| `EAIBlockingTargetTask` | EAI Blocking Target Task | `EAIBase` | Init, CanExecute, Continue |
| `EAISetNearestEntityAsTargetSorter` | EAI Set Nearest Entity As Target Sorter | `Object` | Compare |
| `UAIConsiderationSelfHealth` | UAI Consideration Self Health | `UAIConsiderationBase` | Init, GetScore |
| `UAIConsiderationSelfVisible` | UAI Consideration Self Visible | `UAIConsiderationBase` | GetScore |
| `UAIConsiderationTargetDistance` | UAI Consideration Target Distance | `UAIConsiderationBase` | GetScore, Init |
| `UAIConsiderationTargetHealth` | UAI Consideration Target Health | `UAIConsiderationBase` | GetScore |
| `UAIConsiderationTargetType` | UAI Consideration Target Type | `UAIConsiderationBase` | GetScore, Init |
| `UAIConsiderationTargetVisible` | UAI Consideration Target Visible | `UAIConsiderationBase` | GetScore |

## game-events / minevents (3)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `GameEventFlag` | Game Event Flag | `Object` | (fields only) |
| `SequenceLink` | Sequence Link | `Object` | CheckLink |
| `SequenceStopper` | Sequence Stopper | `Object` | (fields only) |

## items (7)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `ItemActionDataVomit` | Item Action Data Vomit | `ItemActionDataLauncher` | (fields only) |
| `ItemActionDynamicData` | Item Action Dynamic Data | `ItemActionAttackData` | (fields only) |
| `ItemActionDynamicMeleeData` | Item Action Dynamic Melee Data | `ItemActionDynamicData` | (fields only) |
| `ItemActionReplaceBlockData` | Item Action Replace Block Data | `ItemActionDataRanged` | (fields only) |
| `ItemClassArmor` | Item Class Armor | `ItemClass` | Init, CanEquip, KeepOnDeath |
| `ItemId` | Item Id | `ValueType` | FromStack, Write, Read |
| `ItemWorldData` | Item World Data | `Object` | (fields only) |

## light-mesh-water (3)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `WaterPoint` | Water Point | `ValueType` | (fields only) |
| `WaterStats` | Water Stats | `ValueType` | Sum, ResetFrame |
| `WaterStatsProfiler` | Water Stats Profiler | `Object` | SampleTick |

## loot-economy (8)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `BaseLootEntryRequirement` | Base Loot Entry Requirement | `Object` | CheckRequirement, Init |
| `LootEntryRequirementBiome` | Loot Entry Requirement Biome | `BaseLootEntryRequirement` | Init, CheckRequirement |
| `LootEntryRequirementCVar` | Loot Entry Requirement C Var | `BaseOperationLootEntryRequirement` | Init, LeftSide, RightSide |
| `LootEntryRequirementProgression` | Loot Entry Requirement Progression | `BaseOperationLootEntryRequirement` | Init, LeftSide, RightSide |
| `LootEntryRequirementQuestTags` | Loot Entry Requirement Quest Tags | `BaseLootEntryRequirement` | Init, CheckRequirement |
| `LootEntryRequirementRandomRoll` | Loot Entry Requirement Random Roll | `BaseOperationLootEntryRequirement` | Init, LeftSide, RightSide |
| `TraderStageTemplate` | Trader Stage Template | `Object` | IsWithin |
| `TraderStageTemplateGroup` | Trader Stage Template Group | `Object` | IsWithin |

## quests-challenges (4)

| Leaf | Role | Base | Key methods |
|---|---|---|---|
| `BaseQuestCriteria` | Base Quest Criteria | `Object` | CheckForQuestGiver, CheckForPlayer, HandleVariables |
| `QuestCriteriaPOIWithinDistance` | Quest Criteria POI Within Distance | `BaseQuestCriteria` | CheckForQuestGiver |
| `QuestTierReward` | Quest Tier Reward | `Object` | GiveRewards |
| `SharedQuestEntry` | Shared Quest Entry | `Object` | Clone |

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
| `EntitySpawnerClassForDay` | Entity Spawner Class For Day | `Object` | Day, AddForDay, Count |
| `SPlayerSpawnedInWorldData` | S Player Spawned In World Data | `ValueType` | (fields only) |
| `SPlayerSpawningData` | S Player Spawning Data | `ValueType` | (fields only) |
| `SpawnEntry` | Spawn Entry | `Object` | HandleUpdate |
| `SupplyCrateSpawn` | Supply Crate Spawn | `Object` | (fields only) |

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
| `BiomeBlockDecoration` | Biome Block Decoration | `Object` | GetRandomRotation |
| `EventPrefabsClient` | Event Prefabs Client | `Object` | Remove, TryAdd |
| `GorePrefab` | Gore Prefab | `RootTransformRefEntity` | Start |
| `PrefabGameObject` | Prefab Game Object | `Object` | (fields only) |
| `PrefabGroupEntry` | Prefab Group Entry | `XUiListEntry`1` | CompareTo, MatchesSearch |
| `PrefabListData` | Prefab List Data | `Object` | AddPOI, ShuffleDifficulty |

## Changelog

- **2026-07-24:** Promoted from a name index to a full per-leaf reference (IL-derived base + method fingerprint via `tools/src/LeafInfo`).
