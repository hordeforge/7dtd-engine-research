# NetPackage type inventory (V3.0.1 dedicated)

**Kind:** inventory table (not primary narrative).  
**Prefer:** [`protocol.md`](protocol.md), [`protocol-frames.md`](protocol-frames.md) (visual), [`network.md`](network.md).  
**Raw:** [`../il/dedi-complete-v3.0.1/DEDI_COMPLETE_auto.md`](../il/dedi-complete-v3.0.1/DEDI_COMPLETE_auto.md) §3.  
**Hub:** [`INDEX.md`](INDEX.md).

Count: **194** types with `NetPackage` name prefix in live dedi dump.

| Type | Base | Methods | Max method IL |
|---|---|---:|---:|
| `NetPackage` | Object | 18 | 49 |
| `NetPackageAddRemoveBuff` | NetPackage | 6 | 72 |
| `NetPackageAllyRequest` | NetPackage | 7 | 18 |
| `NetPackageAllyResponse` | NetPackage | 7 | 26 |
| `NetPackageAnimateBlock` | NetPackage | 11 | 52 |
| `NetPackageAudio` | NetPackageEntityTargeted | 7 | 206 |
| `NetPackageAudioPlayInHead` | NetPackage | 7 | 12 |
| `NetPackageAuthConfirmation` | NetPackage | 8 | 17 |
| `NetPackageAuthState` | NetPackage | 9 | 35 |
| `NetPackageBag` | NetPackage | 8 | 61 |
| `NetPackageBiomeIntensity` | NetPackage | 6 | 8 |
| `NetPackageBlockLimitTracking` | NetPackage | 6 | 27 |
| `NetPackageBlockTrigger` | NetPackage | 7 | 25 |
| `NetPackageBloodmoonMusic` | NetPackage | 7 | 14 |
| `NetPackageBossEvent` | NetPackage | 9 | 55 |
| `NetPackageChat` | NetPackage | 6 | 63 |
| `NetPackageChunk` | NetPackage | 10 | 126 |
| `NetPackageChunkClusterInfo` | NetPackage | 7 | 36 |
| `NetPackageChunkRemove` | NetPackage | 8 | 8 |
| `NetPackageChunkRemoveAll` | NetPackage | 7 | 8 |
| `NetPackageClientInfo` | NetPackage | 8 | 55 |
| `NetPackageCloseAllWindows` | NetPackage | 7 | 21 |
| `NetPackageConfigFile` | NetPackage | 8 | 25 |
| `NetPackageConsoleCmdClient` | NetPackage | 8 | 31 |
| `NetPackageConsoleCmdServer` | NetPackage | 7 | 10 |
| `NetPackageDamageEntity` | NetPackage | 6 | 172 |
| `NetPackageDebug` | NetPackage | 7 | 34 |
| `NetPackageDecoResetWorldChunk` | NetPackage | 8 | 39 |
| `NetPackageDecoResetWorldRect` | NetPackage | 8 | 58 |
| `NetPackageDecoUpdate` | NetPackage | 8 | 58 |
| `NetPackageDeleteChunkData` | NetPackage | 7 | 27 |
| `NetPackageDirection` | Enum | 0 | 0 |
| `NetPackageDiscordIdMappings` | NetPackage | 7 | 78 |
| `NetPackageDiscordLobbySecret` | NetPackage | 7 | 12 |
| `NetPackageDropItemsContainer` | NetPackage | 7 | 42 |
| `NetPackageDynamicClientArrive` | NetPackage | 10 | 42 |
| `NetPackageDynamicMesh` | DynamicMeshServerData | 14 | 192 |
| `NetPackageEAC` | NetPackage | 7 | 29 |
| `NetPackageEditorAddVolumeFromClient` | NetPackage | 8 | 31 |
| `NetPackageEditorPrefabInstance` | NetPackage | 7 | 58 |
| `NetPackageEditorUpdateVolume` | NetPackage | 6 | 42 |
| `NetPackageEmitSmell` | NetPackage | 6 | 17 |
| `NetPackageEncryptionPublicKey` | NetPackage | 7 | 64 |
| `NetPackageEncryptionRequest` | NetPackage | 6 | 4 |
| `NetPackageEncryptionSharedKey` | NetPackage | 7 | 35 |
| `NetPackageEntityAddExpClient` | NetPackage | 7 | 36 |
| `NetPackageEntityAddExpServer` | NetPackageEntityAddExpClient | 4 | 31 |
| `NetPackageEntityAddScoreClient` | NetPackage | 7 | 27 |
| `NetPackageEntityAddScoreServer` | NetPackageEntityAddScoreClient | 4 | 17 |
| `NetPackageEntityAddVelocity` | NetPackage | 7 | 12 |
| `NetPackageEntityAliveFlags` | NetPackageEntityTargeted | 6 | 109 |
| `NetPackageEntityAnimationData` | NetPackageEntityTargeted | 9 | 64 |
| `NetPackageEntityAttach` | NetPackage | 6 | 104 |
| `NetPackageEntityAwardKillServer` | NetPackage | 7 | 24 |
| `NetPackageEntityCollect` | NetPackage | 6 | 51 |
| `NetPackageEntityLookAt` | NetPackageEntityTargeted | 7 | 31 |
| `NetPackageEntityMapMarkerRemove` | NetPackage | 8 | 24 |
| `NetPackageEntityPhysics` | NetPackage | 7 | 87 |
| `NetPackageEntityPosAndRot` | NetPackageEntityTargeted | 7 | 76 |
| `NetPackageEntityPrimeDetonator` | NetPackage | 7 | 23 |
| `NetPackageEntityRagdoll` | NetPackage | 7 | 61 |
| `NetPackageEntityRelPosAndRot` | NetPackageEntityRotation | 7 | 94 |
| `NetPackageEntityRemove` | NetPackageEntityTargeted | 7 | 24 |
| `NetPackageEntityRotation` | NetPackageEntityTargeted | 7 | 73 |
| `NetPackageEntitySetPartActive` | NetPackage | 6 | 38 |
| `NetPackageEntitySetSkillLevelClient` | NetPackage | 7 | 22 |
| `NetPackageEntitySetSkillLevelServer` | NetPackageEntitySetSkillLevelClient | 4 | 26 |
| `NetPackageEntitySpawn` | NetPackageEntityTargeted | 7 | 60 |
| `NetPackageEntitySpawnResponse` | NetPackage | 6 | 153 |
| `NetPackageEntitySpeeds` | NetPackageEntityTargeted | 7 | 37 |
| `NetPackageEntityStatChanged` | NetPackageEntityTargeted | 7 | 88 |
| `NetPackageEntityStatsBuff` | NetPackage | 7 | 76 |
| `NetPackageEntityStealth` | NetPackage | 9 | 92 |
| `NetPackageEntityTargeted` | NetPackage | 6 | 28 |
| `NetPackageEntityTeleport` | NetPackageEntityPosAndRot | 4 | 60 |
| `NetPackageEntityVelocity` | NetPackageEntityTargeted | 7 | 53 |
| `NetPackageEntityWaypointList` | NetPackage | 6 | 39 |
| `NetPackageEntry` | Object | 1 | 3 |
| `NetPackageEventPrefab` | NetPackage | 7 | 48 |
| `NetPackageExplosionClient` | NetPackage | 7 | 60 |
| `NetPackageExplosionInitiate` | NetPackage | 7 | 55 |
| `NetPackageGameEventRequest` | NetPackage | 7 | 211 |
| `NetPackageGameEventResponse` | NetPackage | 10 | 135 |
| `NetPackageGameMessage` | NetPackage | 6 | 28 |
| `NetPackageGameStats` | NetPackage | 9 | 19 |
| `NetPackageHoldingItem` | NetPackage | 6 | 45 |
| `NetPackageHordeEvent` | NetPackage | 6 | 31 |
| `NetPackageIdMapping` | NetPackage | 8 | 18 |
| `NetPackageInfo` | Object | 1 | 3 |
| `NetPackageInventoryDataRequest` | NetPackage | 7 | 92 |
| `NetPackageInventoryDataResponse` | NetPackage | 7 | 30 |
| `NetPackageInventoryKeepOpen` | NetPackage | 6 | 6 |
| `NetPackageInventoryTransactionRequest` | NetPackage | 7 | 8 |
| `NetPackageInventoryTransactionResponse` | NetPackage | 7 | 66 |
| `NetPackageItemActionEffects` | NetPackage | 6 | 52 |
| `NetPackageItemDrop` | NetPackage | 7 | 37 |
| `NetPackageItemReload` | NetPackage | 6 | 18 |
| `NetPackageKeyExchangeComplete` | NetPackage | 7 | 8 |
| `NetPackageLandClaimRepair` | NetPackage | 6 | 33 |
| `NetPackageLobbyJoin` | NetPackage | 7 | 63 |
| `NetPackageLobbyRegisterClient` | NetPackage | 7 | 38 |
| `NetPackageLocalization` | NetPackage | 12 | 123 |
| `NetPackageLockRequest` | NetPackage | 8 | 69 |
| `NetPackageLockResponse` | NetPackage | 8 | 81 |
| `NetPackageLogger` | Object | 4 | 84 |
| `NetPackageManager` | Object | 16 | 70 |
| `NetPackageMapChunks` | NetPackage | 9 | 109 |
| `NetPackageMapPosition` | NetPackage | 7 | 31 |
| `NetPackageMeasure` | Object | 4 | 40 |
| `NetPackageMetrics` | Object | 16 | 501 |
| `NetPackageMinEventFire` | NetPackage | 8 | 45 |
| `NetPackageModifyCVar` | NetPackage | 6 | 25 |
| `NetPackageNavObject` | NetPackage | 9 | 77 |
| `NetPackageNetMetrics` | NetPackage | 7 | 28 |
| `NetPackageNPCQuestList` | NetPackage | 12 | 180 |
| `NetPackageOwnedEntitySync` | NetPackage | 7 | 34 |
| `NetPackagePackageIds` | NetPackage | 9 | 121 |
| `NetPackageParticleEffect` | NetPackage | 6 | 30 |
| `NetPackagePartyActions` | NetPackage | 6 | 176 |
| `NetPackagePartyData` | NetPackage | 7 | 243 |
| `NetPackagePartyQuestChange` | NetPackage | 7 | 83 |
| `NetPackagePersistentPlayerPositions` | NetPackage | 8 | 42 |
| `NetPackagePersistentPlayerState` | NetPackage | 7 | 13 |
| `NetPackagePickupBlock` | NetPackage | 6 | 41 |
| `NetPackagePlayerData` | NetPackage | 7 | 15 |
| `NetPackagePlayerDenied` | NetPackage | 10 | 31 |
| `NetPackagePlayerDisconnect` | NetPackagePlayerData | 4 | 9 |
| `NetPackagePlayerEquipment` | NetPackageEntityTargeted | 6 | 56 |
| `NetPackagePlayerId` | NetPackage | 7 | 21 |
| `NetPackagePlayerInventory` | NetPackage | 7 | 107 |
| `NetPackagePlayerInventoryForAI` | NetPackage | 9 | 33 |
| `NetPackagePlayerLaserSight` | NetPackage | 6 | 70 |
| `NetPackagePlayerLogin` | NetPackage | 8 | 52 |
| `NetPackagePlayerLoginAnswer` | NetPackage | 9 | 50 |
| `NetPackagePlayerQuestPositions` | NetPackage | 7 | 30 |
| `NetPackagePlayerSetBackpackPosition` | NetPackage | 7 | 39 |
| `NetPackagePlayerSpawnedInWorld` | NetPackage | 7 | 47 |
| `NetPackagePlayerStats` | NetPackageEntityTargeted | 7 | 70 |
| `NetPackagePlayerTwitchStats` | NetPackageEntityTargeted | 6 | 52 |
| `NetPackagePlayerVendingMachine` | NetPackage | 6 | 30 |
| `NetPackagePOIAround` | NetPackage | 9 | 156 |
| `NetPackagePOIWaypoint` | NetPackage | 7 | 39 |
| `NetPackageQuestEntitySpawn` | NetPackage | 9 | 37 |
| `NetPackageQuestEvent` | NetPackage | 17 | 368 |
| `NetPackageQuestGotoPoint` | NetPackage | 6 | 312 |
| `NetPackageQuestObjectiveUpdate` | NetPackage | 8 | 180 |
| `NetPackageQuestTreasurePoint` | NetPackage | 10 | 176 |
| `NetPackageRangeCheckDamageEntity` | NetPackage | 7 | 216 |
| `NetPackageRegionMetaData` | DynamicMeshServerData | 8 | 61 |
| `NetPackageRequestToEnterGame` | NetPackage | 6 | 7 |
| `NetPackageRequestToSpawnEntity` | NetPackage | 7 | 9 |
| `NetPackageRequestToSpawnPlayer` | NetPackage | 7 | 17 |
| `NetPackageSetAttackTarget` | NetPackageEntityTargeted | 6 | 24 |
| `NetPackageSetBlock` | NetPackage | 6 | 59 |
| `NetPackageSetBlockResponse` | NetPackage | 6 | 28 |
| `NetPackageSetBlockTexture` | NetPackage | 9 | 46 |
| `NetPackageSetProp` | NetPackage | 6 | 37 |
| `NetPackageSharedPartyKill` | NetPackage | 7 | 22 |
| `NetPackageSharedQuest` | NetPackage | 8 | 371 |
| `NetPackageShowToolbeltMessage` | NetPackage | 7 | 18 |
| `NetPackageSignDataRequest` | NetPackage | 6 | 5 |
| `NetPackageSignDataResponse` | NetPackage | 8 | 28 |
| `NetPackageSimpleChat` | NetPackage | 7 | 116 |
| `NetPackageSimpleRPC` | NetPackage | 6 | 17 |
| `NetPackageSleeperPassiveChange` | NetPackageEntityTargeted | 5 | 21 |
| `NetPackageSleeperPose` | NetPackage | 6 | 23 |
| `NetPackageSleeperWakeup` | NetPackage | 7 | 20 |
| `NetPackageSoundAtPosition` | NetPackage | 6 | 36 |
| `NetPackageTeleportPlayer` | NetPackage | 6 | 56 |
| `NetPackageTileEntity` | NetPackage | 8 | 90 |
| `NetPackageTraderData` | NetPackage | 9 | 50 |
| `NetPackageTurretSpawn` | NetPackage | 6 | 207 |
| `NetPackageTurretSync` | NetPackage | 7 | 27 |
| `NetPackageTwitchAccess` | NetPackage | 7 | 55 |
| `NetPackageTwitchVoteScheduling` | NetPackage | 6 | 16 |
| `NetPackageVehicleCount` | NetPackage | 6 | 16 |
| `NetPackageVehicleDataSync` | NetPackage | 7 | 113 |
| `NetPackageVehiclePositions` | NetPackage | 6 | 35 |
| `NetPackageVehicleSpawn` | NetPackage | 6 | 86 |
| `NetPackageWallVolume` | NetPackage | 7 | 16 |
| `NetPackageWallVolumeRemove` | NetPackage | 7 | 11 |
| `NetPackageWaterSet` | NetPackage | 11 | 36 |
| `NetPackageWaterSimChunkUpdate` | NetPackage | 12 | 65 |
| `NetPackageWaypoint` | NetPackage | 6 | 29 |
| `NetPackageWeather` | NetPackage | 8 | 59 |
| `NetPackageWireActions` | NetPackage | 7 | 163 |
| `NetPackageWireToolActions` | NetPackage | 6 | 254 |
| `NetPackageWorldAreas` | NetPackage | 7 | 31 |
| `NetPackageWorldFolder` | NetPackage | 19 | 93 |
| `NetPackageWorldInfo` | NetPackage | 8 | 83 |
| `NetPackageWorldInitInfo` | NetPackage | 7 | 58 |
| `NetPackageWorldInitInfoRequest` | NetPackage | 7 | 38 |
| `NetPackageWorldSpawnPoints` | NetPackage | 7 | 11 |
| `NetPackageWorldTime` | NetPackage | 7 | 9 |

## Clone annotation status

| Status | Packages |
|---|---|
| Golden body (loadgen) | EntityPosAndRot, EntityRelPosAndRot, EntityAliveFlags, EntityLookAt, DamageEntity, ExplosionInitiate, PlayerLogin, PackageIds, PlayerLoginAnswer, AuthConfirmation, RequestToEnterGame, RequestToSpawnPlayer, SimpleChat |
| Name only (this table) | all others |
| Residual / skip for M1 clone | EAC, Encryption*, Twitch*, Editor*, Discord* |

## Changelog

- **2026-07-20:** Generated from dedi-complete auto dump for zig-clone RE.
