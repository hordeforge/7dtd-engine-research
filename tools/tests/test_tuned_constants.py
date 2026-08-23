#!/usr/bin/env python3
"""Guard tuned game constants documented in the docs against the DLL.

The AI-director horde/placement/scheduling constants and the water-sim constants
are const fields in the game classes. A game patch that retunes them without
updating the doc fails here. The doc-side check requires the constant name and
value to appear in the owning doc (derived *Sq constants are value-only).

Usage: python3 tools/tests/test_tuned_constants.py <asm>
"""
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(TOOLS)
DOCS = os.path.join(REPO, "docs")

# family -> (doc, { const name: expected value })  (values from the V3.1.0 DLL)
CONSTS = {
    "AIDirectorBloodMoonParty": ("aidirector.md", {
        "cPartyJoinDistance": 80,
        "cPartyJoinDistanceSq": 6400,
        "cSightDist": 100,
        "cSightDistSq": 10000,
        "cSpawnAngle": 90,
        "cSpawnDistance": 40,
        "cSpawnMaxRandDistance": 10,
        "cSpawnMinPlayerDistance": 30,
        "cSpawnMinRandDistance": 0,
        "cSpawnPreferredArc": 120,
        "cTeleportDist": 150,
        "cTeleportDistSq": 22500,
    }),
    "AIDirectorBloodMoonComponent": ("aidirector.md", {
        "cPartyEnemyMax": 30,
        "cSpawnDelay": 1,
        "cTimeStayAfterDeathScale": 3,
    }),
    "AIDirectorWanderingHordeComponent": ("aidirector.md", {
        "cNextHourMin": 7,
    }),
    "AIWanderingHordeSpawner": ("aidirector.md", {
        "cInvestigateTime": 6000,
    }),
    "AIDirectorChunkData": ("aidirector.md", {
        "cCooldownDelay": 240,
        "cCooldownLongDelay": 1320,
        "cCooldownNeighborDelay": 180,
        "cCooldownNeighborLongDelay": 720,
        "cVersion": 2,
    }),
    "AIDirectorChunkEventComponent": ("aidirector.md", {
        "cActivityLevelToSpawn": 25,
        "cEventDelay": 5,
        "cSpawnChance": 0.2,
        "cVersion": 1,
    }),
    "AIDirectorHordeComponent": ("aidirector.md", {
        "cPitstopSideMin": 40,
        "cPitstopSideRange": 20,
        "cPlayerClosestDist": 30,
        "cSinglePlayerSkipPer": 0.3,
    }),
    "AIDirectorPlayerState": ("aidirector.md", {
        "kCheckUndergroundTime": 5,
        "kNumBlocksUnderground": 10,
    }),
    "AIDirectorSmellMarker": ("aidirector.md", {
        "kMax": 256,
    }),
    "AIDirector": ("aidirector.md", {
        "cActivityDuration": 720,
        "cActivityNoiseDuration": 240,
    }),
    "AIAirDrop": ("aidirector.md", {
        "cPlaneMetersPerSecond": 120,
        "kMinDropRange": 150,
        "kMaxDropRange": 700,
        "kMaxDropsPerPlane": 3,
        "kMinPlayerClusterRadius": 30,
        "kMaxPlayerClusterRadius": 70,
        "kMinPlaneFlightVector": 1500,
        "kMaxPlaneFlightVector": 2000,
        "kMinPlaneTangentPointRadius": 30,
        "kMaxPlaneTangentPointRadius": 750,
        "kSpawnYUp": 180,
    }),
    "AIDirectorAirDropComponent": ("aidirector.md", {
        "MinDayCount": 3,
        "MaxDayCount": 3,
        "MinTimeOfDay": 12000,
        "MaxTimeOfDay": 12000,
    }),
    "AstarVoxelGrid": ("raycast-pathing.md", {
        "cGridHeight": 320,
        "cCollisionMask": 1073807360,
        "cClimbMinHeight": 0.6,
        "cClimbMaxHeight": 1.51,
        "cDropOnTopHeight": 0.95,
        "cDropMaxHeight": 9.4,
        "cDoorPenalty": 2,
        "cConnectionPoolMax": 16,
        "cBlockerFlagLow": 15,
        "cBlockerFlagLow0": 1,
        "cBlockerFlagHigh": 240,
        "cBlockerFlagHigh0": 16,
        "cBlockerFlagHighLow": 255,
        "cBlockerFlagHighLow0": 17,
        "cBlockerFlagSlopeDir0": 256,
        "cBlockerFlagLadder": 8192,
        "cBlockerFlagDoor": 16384,
        "cBlockerFlagFloor": 4096,
    }),
    "Block": ("blocks.md", {
        "BlockFaceDrawn_Top": 1,
        "BlockFaceDrawn_Bottom": 2,
        "BlockFaceDrawn_North": 4,
        "BlockFaceDrawn_West": 8,
        "BlockFaceDrawn_South": 16,
        "BlockFaceDrawn_East": 32,
        "BlockFaceDrawn_All": 255,
        "BlockFaceDrawn_AllORD": 63,
        "BT_Sight": 1,
        "BT_Movement": 2,
        "BT_Bullets": 4,
        "BT_Rockets": 8,
        "BT_Melee": 16,
        "BT_Arrows": 32,
        "BT_All": 255,
        "BT_None": 0,
        "cPathSolid": 1,
        "cPathScan": -1,
    }),
    "AstarManager": ("raycast-pathing.md", {
        "cCharDiameter": 0.3,
        "cCharHeight": 1.8,
        "cGridXZSize": 76,
        "cGridY": -32,
        "cPlayerMergeDist": 19,
        "cPlayerMergeDistSq": 361,
        "cMoveDist": 10,
        "cUpdateDeltaTime": 0.1,
        "cLocationDuration": 4,
        "cLocationFindPer": 0.2,
    }),
    "BiomeType": ("chunk-providers.md", {
        "Snow": 1,
        "Forest": 2,
        "PineForest": 3,
        "Plains": 4,
        "Desert": 5,
        "Water": 6,
        "Radiated": 7,
        "Wasteland": 8,
        "burnt_forest": 9,
        "city": 10,
        "city_wasteland": 11,
        "wasteland_hub": 12,
        "caveFloor": 13,
        "caveCeiling": 14,
        "Any": 0,
    }),
    "BlockFaceFlag": ("blocks.md", {
        "Top": 1,
        "Bottom": 2,
        "North": 4,
        "West": 8,
        "South": 16,
        "East": 32,
        "Axials": 60,
        "Solid": 63,
        "All": 63,
        "None": 0,
    }),
    "BlockTags": ("blocks.md", {
        "GrowablePlant": 1,
        "Door": 2,
        "Window": 3,
        "TreeTrunk": 4,
        "Gore": 5,
        "Spike": 6,
        "ClosetDoor": 7,
        "None": 0,
    }),
    "BiomeLayout": ("world-generation.md", {
        "CenterForest": 0,
        "CenterWasteland": 1,
        "Circle": 2,
        "Circle2": 3,
        "Line": 4,
    }),
    "BlockedPlayerList": ("dedicated-leftovers.md", {
        "TimeoutHours": 168,
        "MaxBlockedPlayerEntries": 500,
        "MaxRecentPlayerEntries": 100,
        "Version": 1,
    }),
    "AbundanceLootModTypes": ("loot-economy.md", {
        "Food": 1,
        "Drinks": 2,
        "Ammo": 3,
        "Meds": 4,
        "Resources": 5,
        "Armor": 6,
        "Melee": 7,
        "Ranged": 8,
        "Dukes": 9,
        "Magazines": 10,
        "Books": 11,
        "None": 0,
    }),
    "AutoTurretFireController": ("vehicles-drones-turrets.md", {
        "baseConeDistance": 5.25,
        "baseConePitch": 22.5,
        "baseConeYaw": 22.5,
        "cTimeBetweenSoundDispatch": 1,
    }),
    "BladeTrapStates": ("dedicated-misc-systems.md", {
        "IsOff": 0,
        "RandomWaitToStart": 1,
        "IsStarting": 2,
        "IsOn": 3,
        "IsOnPartlyBroken": 4,
        "IsOnBroken": 5,
        "IsStopping": 6,
    }),
    "WeatherManager": ("weather-environment.md", {
        "BaseTemperature": 70,
        "cForceTempDefault": -100,
        "cGracePeriodWorldTime": 22000,
        "cLightningDelayMin": 30,
        "cLightningDelayMax": 60,
        "cStormWarningDuration": 60,
        "cWeatherTransitionSeconds": 10,
        "cVersion": 4,
    }),
    "EntityMoveHelper": ("entity-ai.md", {
        "cDoneXZDistSq": 0.0009,
        "cTempMoveDist": 0.4,
        "cMoveSlowDist": 0.6,
        "cMoveDirectDist": 0.65,
        "cCheckBlockedDist": 0.35,
        "cCheckBlockedRadius": 0.125,
        "cCheckSidestepDist": 0.35,
        "cCheckSidestepRadius": 0.1,
        "cDigAngleCos": 0.86,
        "cDigXZDistSq": 0.01,
        "cDigDiagonalXZDistSq": 2.25,
        "cDigMovedDist": 0.5,
        "cJumpUpXZDistSq": 0.16,
        "cUnreachJumpMin": 1.2,
        "cLadderXZDistSq": 0.1089,
        "cYawNextDist": 1.5,
        "cDestroyOtherAIDist": 20,
        "cDestroyRefreshAfter": 25,
        "cCollisionMask": 1082195968,
    }),
    "ChunkManager": ("world-chunks.md", {
        "cMaxChunksSupported": 100000,
        "cMaxChunksAroundPlayers": 15,
        "cMaxCGOsToUnloadPerFrame": 8,
        "cReloadPosY": -1,
        "MinLogThresholdSeconds": 1,
    }),
    "DroneManager": ("vehicles-drones-turrets.md", {
        "cSaveTime": 120,
        "cChangeSaveDelay": 10,
        "cMaxDrones": 500,
        "cMaxActiveDronePlayerRange": 32,
        "cVersion": 1,
    }),
    "BlockValue": ("blocks.md", {
        "RotationShift": 16,
        "Metadata3Shift": 21,
        "Metadata1Shift": 22,
        "Metadata2Shift": 26,
        "ChildShift": 30,
        "HasDecalShift": 31,
        "TypeMask": 65535,
        "RotationMax": 31,
        "MetadataMax": 15,
        "Metadata3Max": 1,
    }),
    "BlockValueV3": ("dedicated-leftovers.md", {
        "RotationShift": 15,
        "MetadataShift": 20,
        "Metadata2Shift": 24,
        "Metadata3Shift": 28,
        "TypeMask": 32767,
        "Metadata3Max": 3,
        "ChildShift": 30,
        "HasDecalShift": 31,
    }),
    "EntityAlive": ("entity-ai.md", {
        "cTraderTeleportCheckTime": 0.1,
        "cDamageImmunityOnRespawnSeconds": 1,
        "cSoundRandomMaxDist": 20,
        "kSnoreGroanMinCD": 20,
        "cSwimGravityPer": 0.025,
        "cSwimDrag": 0.91,
        "cSwimDragY": 0.91,
        "cSwimAnimDelay": 6,
        "CLIMB_LADDER_SPEED": 1234,
        "cWalkTypeFat": 1,
        "cWalkTypeCripple": 5,
        "cWalkTypeCrouch": 8,
        "cWalkTypeBandit": 15,
        "cWalkTypeCrawlFirst": 20,
        "cWalkTypeCrawler": 21,
        "cWalkTypeSpider": 22,
        "cWalkTypeSwim": -1,
    }),
    "EntityVulture": ("entity-ai.md", {
        "cTargetDistanceClose": 0.9,
        "cTargetDistanceMax": 80,
        "cTargetAttackOffsetY": -0.1,
        "cFlyingMinimumSpeed": 0.02,
        "cVomitMinRange": 3,
        "cAttackDelay": 18,
        "cBattleFatigueMin": 30,
        "cBattleFatigueMax": 60,
        "cBattleFatigueCooldownMin": 80,
        "cBattleFatigueCooldownMax": 180,
        "cCollisionMask": 1082195968,
    }),
    "Entity": ("spawning.md", {
        "EntityIdInvalid": -1,
        "cClientIdCreate": -1,
        "cClientIdStart": -2,
        "cClientIdNone": 0,
        "cIdCreatorIsServer": -2,
        "cIgnoreDamage": -1,
        "cKillAnythingDamage": 99999,
        "cPhysicsMasterTickRate": 2,
        "cWaterHeightScale": 1.1,
        "cAttachSlotNone": -1,
    }),
    "EntityDrone": ("vehicles-drones-turrets.md", {
        "cBaseFollowDistance": 5,
        "cCombatFollowRange": 10,
        "cAvoidRange": 2.5,
        "cMaxSpeedFlying": 15,
        "cFollowHoverHeight": 1,
        "cAttackEnterTime": 1,
        "cAttackExitTime": 1.5,
        "cOwnerFocusTime": 0.2,
        "cAddPathDist": 1.414,
        "cPathLayer": 1073807360,
        "cInitSuppressVOTime": 5,
        "cNotifyNeedsHealItemCooldown": 30,
        "cNotifyNeedsHealMaxNotifyCount": 2,
        "cSyncOwnerKey": 1,
        "cSyncInteractAndSecurity": 2,
        "cSyncLightMod": 64,
        "cSyncHealAllies": 256,
        "cSyncOrderState": 16384,
    }),
    "EntityVehicle": ("vehicles-drones-turrets.md", {
        "cDamageBlockScale": 0.05833333,
        "cDamageBlockMin": 5,
        "cDamageBlockVelReduction": 1.5,
        "cDamageBlockSelfPer": 2.5,
        "cDamageEntityScale": 12,
        "cDamageEntitySelfScale": 28,
        "cDamageTerrainSelfPer": 0.1,
        "cExitVelScale": 0.5,
        "cFuelItemScale": 25,
        "cKillEntityXPPer": 0.5,
        "cSleepTime": 3,
        "cVehicleCameraOffset": 1.8,
        "cVehicleCameraChaseSpeed": 7,
        "cSyncAttachment": 1,
        "cSyncItem": 4,
        "cSyncStorage": 8,
        "cSyncAllNonRates": 15,
        "cSyncLowRate": 16384,
        "cSyncHighRate": 32768,
        "cSyncSave": 16398,
        "cSyncLowRateAndNonRates": 16399,
        "cSyncReplicate": 49159,
        "cSyncLowRateDuration": 2,
        "cSyncHighRateDuration": 0.5,
    }),
    "DismembermentManager": ("combat-damage.md", {
        "cDefaultDetachLimbLifeTime": 10,
        "cDefaultDetachLimbMax": 25,
        "cDefaultDetachLimbCleanupCount": 5,
        "cMaxLimbsFromExplosiveDeath": 3,
        "MaxForce": 1.5,
    }),
    "DecoManager": ("world-chunks.md", {
        "cChunkSize": 128,
        "cUpdateDelay": 1,
        "cUpdateCoMaxTimeUs": 900,
        "FILEVERSION": 6,
    }),
    "EntityFactory": ("spawning.md", {
        "cFirstEntityID": 1,
        "StartEntityID": 171,
        "cNumberOfCachedFallingBlocks": 150,
        "cNumberOfCachedItems": 20,
    }),
    "DistantTerrain": ("client-side-surface.md", {
        "cWorldSizeX": 20000,
        "cWorldSizeZ": 20000,
        "DT_ViewDistance": 2000,
        "NbChunkToBeUpdated": 15,
        "MaxNbDChunkOnAsyncUpdate": 50,
    }),
    "FastWireNode": ("tile-entities-power.md", {
        "BASE_WIRE_RADIUS": 0.01,
        "BASE_MIN_WIRE_DIP": 0,
        "BASE_MAX_WIRE_DIP": 0.25,
        "NODE_COUNT": 15,
        "cLayerMaskRayCast": 65537,
    }),
    "WaterConstants": ("light-mesh-water.md", {
        "MIN_MASS": 195,
        "MIN_FLOW": 195,
        "MAX_MASS": 19500,
        "OVERFULL_MAX": 58500,
        "MIN_MASS_SIDE_SPREAD": 4875,
        "FLOW_SPEED": 0.5,
    }),
    "NetEntityDistribution": ("network.md", {
        "cHighPriorityRange": 5,
        "cLowPriorityRange": 18,
        "cLowestPriorityRange": 25,
        "priorityViewAngleMinDistance": 128,
        "lowestPriorityTick": 10,
        "lowPriorityTick": 6,
        "MobsUpdateTicks": 3,
    }),
    "SleeperVolume": ("spawning.md", {
        "cBedrollClearTime": 24000,
        "cDespawnDelay": 900,
        "cDespawnPassiveDelay": 200,
        "cPlayerInsideDelayTime": 1000,
        "cPlayerYOffset": 0.8,
        "cPassivePaddingXZ": -0.3,
        "cAttackPaddingXZ": -0.1,
        "cPassiveNoisePadding": 0.9,
        "cSpawnDelay": 2,
        "cSpawnPerTickMax": 2,
        "cFlagsQuestExclude": 1,
        "cFlagsPriority": 2,
        "cFlagsSpawning": 4,
        "cFlagsCleared": 8,
        "cFlagsHasScript": 16,
        "cTriggerFlagsMask": 7,
        "cRespawnNever": 4294967295,
    }),
    "ThreatLevelConstants": ("entity-ai.md", {
        "cMinThreatLevel": 0,
        "cSuspenseThreshold": 0.25,
        "cCombatReadyThreshold": 0.5,
        "cCombatThreshold": 0.75,
        "cMaxThreatLevel": 1,
    }),
    "StabilityCalculator": ("stability.md", {
        "cInfiniteSupport": 100000,
        "cSupportScale": 1.01,
        "isolatedBlockLimit": 1000,
        "maxIterations": 20,
        "stabilityQueueLimit": 200,
    }),
    "RegionFileManager": ("save-region.md", {
        "cHeadroomBytes": 5242880,
        "cMinimumByteAllowance": 20971520,
        "cMaxChunksToCull": 10000,
    }),
    "VehicleManager": ("vehicles-drones-turrets.md", {
        "cMaxVehicles": 500,
        "cSaveTime": 120,
        "cChangeSaveDelay": 10,
        "cVersion": 1,
    }),
    "PlayerStealth": ("entity-ai.md", {
        "cSmellRadiusMin": 10,
        "cSmellRadiusMax": 100,
        "cSmellBleedRadius": 25,
        "cSmellDysenteryRadius": 35,
        "cSmellEmitChance": 0.2,
        "cSmellEmitRate": 2,
        "cSmellCountMin": 5,
        "cSmellCountMax": 50,
        "cSmellRadiusPerSecondUp": 5,
        "cSmellRadiusPerSecondDown": 2,
        "cSmellEatRadiusPerSecondDown": 0.1428571,
        "cSmellDuration": 90,
        "cAttractEmitChance": 0.2,
        "cAttractEmitRate": 2,
        "cAttractRadiusMax": 100,
        "cSleeperNoiseHear": 360,
        "cSleeperNoiseDecay": 50,
        "cSleeperNoiseWaitTicks": 20,
        "cLightMpyBase": 0.32,
        "cLightLevelMax": 200,
        "cNextSoundPercent": 0.6,
    }),
    "SpawnManagerBiomes": ("spawning.md", {
        "cEnemyMinDistance": 28,
        "cEnemyMaxDistance": 54,
        "cAnimalMinDistance": 48,
        "cAnimalMaxDistance": 70,
    }),
    "Path": ("world-generation.md", {
        "CountryId": 1,
        "HighwayId": 2,
        "HighwayDirtId": 3,
        "WaterId": 4,
        "FreeId": 0,
        "HighwayBlendIdMask": 128,
        "cSingleLaneRadius": 4.5,
        "cShoulderWidth": 1,
        "cBlendDistHighway": 10,
        "cBlendDistCountry": 6,
        "cHeightSmoothDecreasePer": 0.3,
        "cHeightSmoothAverageBias": 8,
    }),
    "TurretTracker": ("vehicles-drones-turrets.md", {
        "cMaxTurrets": 500,
        "cSaveTime": 120,
        "cChangeSaveDelay": 10,
        "cVersion": 1,
    }),
    "MiniTurretFireController": ("vehicles-drones-turrets.md", {
        "baseConeDistance": 5.25,
        "baseConePitch": 22.5,
        "baseConeYaw": 22.5,
        "cSeekRayRadius": 0.05,
    }),
    "ThreatLevelTracker": ("entity-ai.md", {
        "cBaseIncrement": 0.0015,
        "cInactiveIncrement": 0.0625,
        "cSleeperIncrement": 0.03125,
        "cAlertIncrement": 0.125,
        "cTargetIncrement": 0.25,
    }),
    "ThreatLevelUtility": ("entity-ai.md", {
        "LOOKBACK": 300,
        "PLAYER_HOME_MINIMUM_DISTANCE": 50,
        "THREAT_PER_ENEMY": 0.03333334,
        "ZOMBIE_COMBAT_QUANTITY": 4,
    }),
    "Chunk": ("world-chunks.md", {
        "cAreaMasterSizeBlocks": 80,
        "cAreaMasterSizeChunks": 5,
        "cEntityListCount": 16,
        "cEntityListHeight": 16,
        "cTextureChannelCount": 1,
        "CurrentSaveVersion": 47,
        "SupportedSaveVersion": 32,
        "dbChunkX": 136,
        "dbChunkZ": 25,
    }),
    "World": ("world-chunks.md", {
        "cEdgeHard": 50,
        "cEdgeSoft": 80,
        "cEdgeMinWorldSize": 1024,
        "cWorldRWGBorder": 90,
        "cWorldNavExtent": 2900,
        "cCollCacheSize": 50,
        "cCollisionBlocks": 5,
        "cTraderPlacingProtection": 2,
        "SleeperVolumeWorldStateSaveVersion": 1,
        "TriggerVolumeWorldStateSaveVersion": 1,
        "WallVolumeWorldStateSaveVersion": 1,
    }),
    "ItemClass": ("items.md", {
        "cMaxActionNames": 5,
        "cActionUpdateCount": 3,
        "cGSStatScale": 0.005,
        "cGSStatMax": 163.835,
    }),
    "ItemActionAttack": ("items.md", {
        "cHitDefault": 1,
        "cHitElectricTrap": 2,
        "cHitHarvestParticles": 4,
        "cHitEffectOff": 8,
        "cHitToolBeltNotify": 1,
    }),
    "WorldBuilderConstants": ("world-generation.md", {
        "ForestBiomeWeightDefault": 13,
        "BurntForestBiomeWeightDefault": 18,
        "DesertBiomeWeightDefault": 22,
        "SnowBiomeWeightDefault": 23,
        "WastelandBiomeWeightDefault": 24,
        "PlainsWeightDefault": 4,
        "HillsWeightDefault": 4,
        "MountainsWeightDefault": 2,
    }),
    "WorldBuilder": ("world-generation.md", {
        "WorldTileSize": 1024,
        "TerrainTileSize": 256,
        "BiomeTileSize": 256,
        "RadTileSize": 32,
        "BiomeSizeDiv": 8,
        "terrainToBiomeTileScale": 1,
        "cPlayerSpawnsNeeded": 12,
        "groundHeight": 35,
        "HeightMax": 255,
    }),
    "PathingUtils": ("world-generation.md", {
        "PATHING_GRID_TILE_SIZE": 10,
        "stepSize": 10,
        "cNeighborsCount": 8,
        "cHeightCostScale": 0.2,
        "cRoadHighwayMaxStepH": 11,
        "cRoadCountryMaxStepH": 12,
    }),
    "GameManager": ("spawning.md", {
        "cMinSpawnDistanceFromTrader": 250,
        "cMaxSpawnDistanceFromTrader": 750,
    }),
    "SignDataManager": ("signs.md", {
        "cSignSyncBatchBytes": 1048576,
        "cMaxComplexity": 600,
        "cMaxCompStackIndex": 7,
        "cMaxUVStackIndex": 7,
        "baseDescriptorComplexity": 0.5,
    }),
    "Voxel": ("raycast-pathing.md", {
        "HM_Transparent": 1,
        "HM_LiquidOnly": 2,
        "HM_Moveable": 4,
        "HM_Bullet": 8,
        "HM_Rocket": 16,
        "HM_Arrows": 32,
        "HM_NotMoveable": 64,
        "HM_Melee": 128,
        "HM_FirstNotEmptyBlock": 256,
        "HM_All": 4095,
        "HM_IgnoreFragile": 4096,
    }),
    "RegionFileRaw": ("save-region.md", {
        "ChunksPerRegionPerDimension": 8,
        "ChunksPerRegion": 64,
        "fileHeaderLength": 11,
        "locationHeaderLength": 128,
        "reservedBytesPerEntry": 4,
        "CurrentVersion": 1,
        "FileHeaderMagicBytesLength": 3,
    }),
    "MapChunkDatabaseByRegion": ("save-region.md", {
        "CHUNK_DATA_LENGTH": 256,
        "CHUNK_TO_REGION_SHIFT": 5,
        "REGION_CHUNK_WIDTH": 32,
        "REGION_CHUNK_AREA": 1024,
    }),
    "WorldConstants": ("world-chunks.md", {
        "cDuskHour": 22,
        "ChunkAreaDim": 256,
        "ChunkBlockLayerHeight": 4,
        "ChunkBlockLayerHeightMask": 3,
        "ChunkBlockLayerHeightPow": 2,
        "ChunkBlockLayers": 64,
        "ChunkBlockXDim": 16,
        "ChunkBlockXDimM1": 15,
        "ChunkBlockXMask": 15,
        "ChunkBlockXPow": 4,
        "ChunkBlockYDim": 256,
        "ChunkBlockYDimM1": 255,
        "ChunkBlockYMask": 255,
        "ChunkBlockYPow": 8,
        "ChunkBlockZDim": 16,
        "ChunkBlockZDimM1": 15,
        "ChunkBlockZMask": 15,
        "ChunkBlockZPow": 4,
    }),
    "BlockLiquidv2": ("light-mesh-water.md", {
        "MAX_EMISSIONS": 3,
        "blockUpdatesPerSecond": 16,
        "AUTO_GENERATED": 8,
        "ZERO_EMISSIONS": 0,
        "ZERO_EVAPORATION": 0,
    }),
}

SRC = r"""
using System;
using System.Globalization;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;
class TunedConsts {
  static void Main(string[] a) {
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(System.IO.Path.GetDirectoryName(System.IO.Path.GetFullPath(a[0])));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    foreach (var tn in a[1].Split(',')) {
      var t = asm.MainModule.GetTypes().FirstOrDefault(x => x.Name == tn);
      if (t == null) continue;
      foreach (var f in t.Fields.Where(f => f.HasConstant))
        Console.WriteLine(tn + "." + f.Name + "=" +
          Convert.ToString(f.Constant, CultureInfo.InvariantCulture));
      // static fields initialized in the .cctor (ldc/ldstr + stsfld)
      var cctor = t.Methods.FirstOrDefault(x => x.Name == ".cctor" && x.HasBody);
      if (cctor != null) {
        var ins = cctor.Body.Instructions;
        for (int i = 0; i < ins.Count - 1; i++) {
          if (ins[i + 1].OpCode.Code == Code.Stsfld) {
            var fr = ins[i + 1].Operand as FieldReference;
            if (fr != null && fr.DeclaringType.Name == tn) {
              object val = null;
              int j = i;
              var c = ins[j].OpCode.Code;
              // skip a trailing conv (u64/u8 statics: ldc.i4 12000; conv.i8; stsfld)
              if ((c == Code.Conv_I8 || c == Code.Conv_U8 || c == Code.Conv_I4 || c == Code.Conv_U4 ||
                   c == Code.Conv_I || c == Code.Conv_U || c == Code.Conv_R4 || c == Code.Conv_R8) && j > 0)
                c = ins[--j].OpCode.Code;
              if (c == Code.Ldc_I4 || c == Code.Ldc_I4_S || c == Code.Ldc_R4 || c == Code.Ldstr)
                val = ins[j].Operand;
              else if (c >= Code.Ldc_I4_0 && c <= Code.Ldc_I4_8)
                val = (int)(c - Code.Ldc_I4_0);
              else if (c == Code.Ldc_I4_M1)
                val = -1;
              if (val != null)
                Console.WriteLine(tn + "." + fr.Name + "=" +
                  Convert.ToString(val, CultureInfo.InvariantCulture));
            }
          }
        }
      }
    }
  }
}
"""
EXE = "/tmp/tunedconsts_check.exe"

# Const-rich classes (>= 4 numeric const fields) that are intentionally NOT
# pinned: animation/UI/render/noise/enum internals (client-side or data-shape),
# or families pinned elsewhere (stock_facts.json / other gates). A NEW tuned
# family added by a game patch fails the completeness check until it is either
# pinned here or explicitly allowed.
CONST_ALLOWLIST = {
    "AdminWebModules", "AvatarController", "Cell", "ConsoleCmdProfileNetwork",
    "Constants", "DefaultSignData", "DeviceFlags", "EAIApproachSpot",
    "EModelBase", "EntityPlayerLocal", "Explosion", "Fluctuating",
    "GameLightManager", "GameObjectPool", "GameRenderManager", "HashSetLong",
    "ItemActionTerrainTool", "KinematicCharacterMotor", "LightLODHeld",
    "LightManager", "Manager", "Mask", "MeshDescription", "MeshGenerator",
    "MetricConversion", "OcclusionManager", "OpenSimplex2", "OpenSimplex2S",
    "PerformanceProfiler", "PlatformOptimizations", "PlatformUserManager",
    "PlayerMoveController", "PrefabPreviewManager", "ReflectionManager",
    "SignalProcessing", "SignDataManager", "SleeperVolumeToolManager",
    "StreetTile", "TextureDynamicLoader", "TileEntityWorkstation", "Transvoxel",
    "UnixLinkFile", "UpscalerMode", "vp_Layer", "WaterDebugRendererLayer",
    "XUiC_MapArea", "XUiC_Radial", "TriggerEffectManager", "RegionFileSectorBased",
    "AIDirectorConstants", "Chunk", "ItemActionAttack", "ItemClass",
}

COMPLETE_SRC = r"""
using System;
using System.Linq;
using Mono.Cecil;
class ConstComplete {
  static void Main(string[] a) {
    var asm = AssemblyDefinition.ReadAssembly(a[0]);
    foreach (var t in asm.MainModule.GetTypes().Where(t => !t.Name.Contains("<") && !t.IsEnum)) {
      var cs = t.Fields.Where(f => f.HasConstant && (f.Constant is int || f.Constant is float || f.Constant is double)).ToList();
      if (cs.Count >= 4)
        Console.WriteLine(t.Name);
    }
  }
}
"""


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: test_tuned_constants.py <asm>", file=sys.stderr)
        return 2
    asm = sys.argv[1]
    src = "/tmp/tunedconsts_check.cs"
    with open(src, "w") as f:
        f.write(SRC)
    subprocess.run(
        ["mcs", "-r:%s" % os.path.join(TOOLS, "bin", "Mono.Cecil.dll"), src, "-out:" + EXE],
        check=True,
    )
    env = dict(os.environ)
    env["MONO_PATH"] = os.path.join(TOOLS, "bin")
    out = subprocess.run(
        ["mono", EXE, asm, ",".join(CONSTS)], capture_output=True, text=True, env=env, check=True,
    ).stdout
    dll = {}
    for line in out.splitlines():
        cls, _, rest = line.partition(".")
        name, _, val = rest.partition("=")
        dll[(cls, name)] = val

    bad = []
    for cls, (doc_name, consts) in CONSTS.items():
        doc = open(os.path.join(DOCS, doc_name), encoding="utf-8").read()
        for name, want in consts.items():
            have = dll.get((cls, name))
            if have is None:
                bad.append(f"{cls}.{name}: missing from DLL")
            elif have != str(want):
                bad.append(f"{cls}.{name}: DLL {have} != expected {want}")
            # the doc must state the name (and ideally the value); derived *Sq
            # constants and grouped mask families (cBlockerFlag*, BlockFaceDrawn_*,
            # BT_*, cPath*, *Max width bounds) are value-only
            grouped = (name.endswith("Sq") or name.startswith("cBlockerFlag")
                       or name.startswith("BlockFaceDrawn") or name.startswith("BT_")
                       or name.startswith("cPath") or name.endswith("Max")
                       or name.startswith("cWalkType") or name.startswith("cSync")
                       or name.startswith("ChunkBlock") or name.startswith("HM_"))
            if not grouped and not re.search(rf"`?{name}`?", doc):
                bad.append(f"{doc_name}: does not mention {name}")
            if str(want) not in doc:
                bad.append(f"{doc_name}: does not state {want} (for {name})")

    # completeness: every const-rich class (>= 4 numeric consts) must be pinned
    # or allowlisted - a new tuned family from a game patch fails here
    with open("/tmp/constcomplete_check.cs", "w") as f:
        f.write(COMPLETE_SRC)
    subprocess.run(
        ["mcs", "-r:%s" % os.path.join(TOOLS, "bin", "Mono.Cecil.dll"),
         "/tmp/constcomplete_check.cs", "-out:/tmp/constcomplete_check.exe"],
        check=True,
    )
    cenv = dict(os.environ)
    cenv["MONO_PATH"] = os.path.join(TOOLS, "bin")
    cout = subprocess.run(
        ["mono", "/tmp/constcomplete_check.exe", asm], capture_output=True, text=True, env=cenv, check=True,
    ).stdout
    pinned_fams = set(CONSTS.keys())
    for fam in cout.splitlines():
        fam = fam.strip()
        if fam and fam not in pinned_fams and fam not in CONST_ALLOWLIST:
            bad.append(f"const-rich class `{fam}` is neither pinned nor allowlisted (pin it or add to CONST_ALLOWLIST)")
    if bad:
        for b in bad[:25]:
            print("FAIL:", b)
        if len(bad) > 25:
            print(f"...and {len(bad) - 25} more")
        return 1
    n = sum(len(d) for _, d in CONSTS.values())
    print(f"OK: {n} tuned constants pinned in the DLL and stated in the docs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
