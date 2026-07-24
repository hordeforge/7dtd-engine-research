# Dedicated leaf types (V3.0.1)

**Kind:** attribution index for small dedicated-relevant types that execute on a
headless server but are each too minor for their own doc: block-shape/placement
variants, item classes, AI considerations, loot/quest criteria, and the like. Each
is a reachable game type grouped under the subsystem doc that owns its concept.  
**Basis:** name-attributed over the reachability set (`tools/src/Coverage`); the
owning doc holds the framework. Verify a specific leaf against its IL before relying
on details.  
**Hub:** [`../INDEX.md`](../INDEX.md). **Method:** [`../re-methodology.md`](../re-methodology.md).

**88 leaf types**, grouped by owning subsystem.

## blocks / block-shapes (11)

`BlockPlacementPineLeaves`, `BlockPlacementPlate`, `BlockPlacementSpotlight`, `BlockPlacementTorch`, `BlockPlacementTowardsPlacer90`, `BlockPlacementTowardsPlacerInverted`, `BlockShapeBillboardComplex`, `BlockShapeBillboardDiagonal`, `BlockStatistics`, `BuildStabilityBlocks`, `DestroyBlockBehavior`

## buffs (1)

`BuffManager`

## combat-damage (2)

`AttackHitInfo`, `BodyParts`

## combat-damage / items (2)

`ApplyExplosionForce`, `StunBeamWeapon`

## entities (2)

`EntityAnimalSnake`, `EntityNetworkHoldingData`

## entity-ai / uai (11)

`AIFocusAim`, `AIFocusBody`, `AIFocusConditionDistance`, `EAIBlockingTargetTask`, `EAISetNearestEntityAsTargetSorter`, `UAIConsiderationSelfHealth`, `UAIConsiderationSelfVisible`, `UAIConsiderationTargetDistance`, `UAIConsiderationTargetHealth`, `UAIConsiderationTargetType`, `UAIConsiderationTargetVisible`

## game-events / minevents (3)

`GameEventFlag`, `SequenceLink`, `SequenceStopper`

## items (7)

`ItemActionDataVomit`, `ItemActionDynamicData`, `ItemActionDynamicMeleeData`, `ItemActionReplaceBlockData`, `ItemClassArmor`, `ItemId`, `ItemWorldData`

## light-mesh-water (3)

`WaterPoint`, `WaterStats`, `WaterStatsProfiler`

## loot-economy (8)

`BaseLootEntryRequirement`, `LootEntryRequirementBiome`, `LootEntryRequirementCVar`, `LootEntryRequirementProgression`, `LootEntryRequirementQuestTags`, `LootEntryRequirementRandomRoll`, `TraderStageTemplate`, `TraderStageTemplateGroup`

## quests-challenges (4)

`BaseQuestCriteria`, `QuestCriteriaPOIWithinDistance`, `QuestTierReward`, `SharedQuestEntry`

## sandbox-options / game-events (3)

`ModeGamePref`, `VariableStateGameInfoInt`, `VariableStateGameInfoString`

## save-persistence / save-region (3)

`BarRegion`, `BarRegionFloat`, `SaveDataLimitUtils`

## server-lifecycle (4)

`DirectoryPlayerId`, `PlayerCluster`, `SPlayerDisconnectedData`, `SSavePlayerDataData`

## signs (3)

`MethodSignature`, `SignBakeRequest`, `SignComplexityInfo`

## spawning (5)

`EntitySpawnerClassForDay`, `SPlayerSpawnedInWorldData`, `SPlayerSpawningData`, `SpawnEntry`, `SupplyCrateSpawn`

## tile-entities-power (1)

`PowerConsumerSingle`

## vehicles-drones-turrets (5)

`DroneLightManager`, `EModelDrone`, `ItemActionDataSpawnTurret`, `ItemActionDataSpawnVehicle`, `TurretEntitySorter`

## world-chunks / save-region (4)

`ChunkBlockClearData`, `ChunkGameObjectLayer`, `ChunkMemoryStreamReader`, `ChunkMemoryStreamWriter`

## world-generation / chunk-providers (6)

`BiomeBlockDecoration`, `EventPrefabsClient`, `GorePrefab`, `PrefabGameObject`, `PrefabGroupEntry`, `PrefabListData`

## Changelog

- **2026-07-24:** Initial dedicated-leaf attribution index (closes the coverage tail: small dedicated types now attributed to their owning subsystem doc).
