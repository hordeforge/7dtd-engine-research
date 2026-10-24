# NetPackage type inventory (V3.3.0 dedicated)

**Kind:** inventory table (not primary narrative).  
**Pin:** V **3.3.0 (b18)**; static top-level `NetPackage*` census **192** (+ `NetPackageManager` → 193 name-prefixed; see [coverage.md](../meta/coverage.md)).  
**Prefer:** [`protocol.md`](../network/protocol.md), [`protocol-packages.md`](../network/protocol-packages.md), [`protocol-frames.md`](../network/protocol-frames.md) (visual), [`network.md`](../network/network.md).  
**Wire bodies:** ordered `write()` field sequence per package in [`netpackage-bodies.md`](netpackage-bodies.md) (auto-extracted).  
**Raw:** [`../../il/netpackages-v3.3.0/`](../../il/netpackages-v3.3.0/), [`../../il/dedi-complete-v3.3.0/`](../../il/dedi-complete-v3.3.0/).  
**Hub:** [`INDEX.md`](../INDEX.md).

Count: **193** types with `NetPackage` name prefix in live dedi dump (192 wire-oriented types + manager/helpers as named in the table).

> **Census gap (2026-08-29, cross-pollinated from zdtd):** the type table below
> omits four wire packages that DO have extracted bodies in
> [netpackage-bodies.md](netpackage-bodies.md) and appear in the zdtd server's
> negotiated map: `NetPackageLight`, `NetPackageTreeFade`,
> `NetPackageDroneDataSync`, `NetPackageDroneParticleEffect`. The table's
> Methods/IL columns are not filled here because the rows are absent from the
> generator's source list; the census count above is the dump census, and the
> four names are real registered classes (bodies + `dedicated-leaves.md` /
> `vehicles-drones-turrets.md` references). The zdtd side also confirmed the
> name `NetPackageEntityFlags` is NOT a stock class (no dump/census hit; the
> stock package is `NetPackageEntityAliveFlags`) — it was removed from the
> zdtd map as an invented name.

| Type | Base | Methods | Max method IL |
|---|---|---:|---:|
| `NetPackage` | Object | 18 | 49 |
| `NetPackageAddRemoveBuff` | NetPackage | 5 | 72 |
| `NetPackageAllyRequest` | NetPackage | 6 | 18 |
| `NetPackageAllyResponse` | NetPackage | 6 | 26 |
| `NetPackageAnimateBlock` | NetPackage | 10 | 52 |
| `NetPackageAudio` | NetPackageEntityTargeted | 6 | 206 |
| `NetPackageAudioPlayInHead` | NetPackage | 6 | 12 |
| `NetPackageAuthConfirmation` | NetPackage | 7 | 17 |
| `NetPackageAuthState` | NetPackage | 8 | 35 |
| `NetPackageBag` | NetPackage | 7 | 62 |
| `NetPackageBiomeIntensity` | NetPackage | 5 | 8 |
| `NetPackageBlockLimitTracking` | NetPackage | 5 | 27 |
| `NetPackageBlockTrigger` | NetPackage | 6 | 25 |
| `NetPackageBloodmoonMusic` | NetPackage | 6 | 14 |
| `NetPackageBossEvent` | NetPackage | 8 | 55 |
| `NetPackageChat` | NetPackage | 5 | 63 |
| `NetPackageChunk` | NetPackage | 9 | 126 |
| `NetPackageChunkClusterInfo` | NetPackage | 6 | 36 |
| `NetPackageChunkRemove` | NetPackage | 7 | 8 |
| `NetPackageChunkRemoveAll` | NetPackage | 6 | 8 |
| `NetPackageClientInfo` | NetPackage | 7 | 55 |
| `NetPackageCloseAllWindows` | NetPackage | 6 | 21 |
| `NetPackageConfigFile` | NetPackage | 7 | 25 |
| `NetPackageConfirmSpawnEntity` | NetPackage | 6 | 24 |
| `NetPackageConsoleCmdClient` | NetPackage | 7 | 31 |
| `NetPackageConsoleCmdServer` | NetPackage | 6 | 10 |
| `NetPackageDamageEntity` | NetPackage | 5 | 235 |
| `NetPackageDebug` | NetPackage | 6 | 34 |
| `NetPackageDecoResetWorldChunk` | NetPackage | 7 | 39 |
| `NetPackageDecoResetWorldRect` | NetPackage | 7 | 58 |
| `NetPackageDecoUpdate` | NetPackage | 7 | 58 |
| `NetPackageDeleteChunkData` | NetPackage | 6 | 27 |
| `NetPackageDirection` | Enum | 0 | 0 |
| `NetPackageDiscordIdMappings` | NetPackage | 6 | 78 |
| `NetPackageDiscordLobbySecret` | NetPackage | 6 | 12 |
| `NetPackageDropItemsContainer` | NetPackage | 6 | 42 |
| `NetPackageDynamicClientArrive` | NetPackage | 9 | 42 |
| `NetPackageDynamicMesh` | DynamicMeshServerData | 13 | 192 |
| `NetPackageEAC` | NetPackage | 6 | 29 |
| `NetPackageEditorAddVolumeFromClient` | NetPackage | 7 | 31 |
| `NetPackageEditorPrefabInstance` | NetPackage | 6 | 58 |
| `NetPackageEditorUpdateVolume` | NetPackage | 5 | 42 |
| `NetPackageEmitSmell` | NetPackage | 5 | 17 |
| `NetPackageEncryptionPublicKey` | NetPackage | 6 | 35 |
| `NetPackageEncryptionRequest` | NetPackage | 5 | 4 |
| `NetPackageEncryptionSharedKey` | NetPackage | 6 | 31 |
| `NetPackageEntityAddExpClient` | NetPackage | 6 | 36 |
| `NetPackageEntityAddExpServer` | NetPackageEntityAddExpClient | 4 | 31 |
| `NetPackageEntityAddScoreClient` | NetPackage | 6 | 27 |
| `NetPackageEntityAddScoreServer` | NetPackageEntityAddScoreClient | 4 | 17 |
| `NetPackageEntityAddVelocity` | NetPackage | 6 | 12 |
| `NetPackageEntityAliveFlags` | NetPackageEntityTargeted | 5 | 99 |
| `NetPackageEntityAnimationData` | NetPackageEntityTargeted | 8 | 64 |
| `NetPackageEntityAttach` | NetPackage | 5 | 104 |
| `NetPackageEntityAwardKillServer` | NetPackage | 6 | 24 |
| `NetPackageEntityCollect` | NetPackage | 5 | 51 |
| `NetPackageEntityLookAt` | NetPackageEntityTargeted | 6 | 31 |
| `NetPackageEntityMapMarkerRemove` | NetPackage | 7 | 24 |
| `NetPackageEntityPhysics` | NetPackage | 6 | 87 |
| `NetPackageEntityPosAndRot` | NetPackageEntityTargeted | 6 | 76 |
| `NetPackageEntityPrimeDetonator` | NetPackage | 6 | 23 |
| `NetPackageEntityRagdoll` | NetPackage | 6 | 61 |
| `NetPackageEntityRelPosAndRot` | NetPackageEntityRotation | 6 | 94 |
| `NetPackageEntityRemove` | NetPackageEntityTargeted | 6 | 24 |
| `NetPackageEntityRotation` | NetPackageEntityTargeted | 6 | 73 |
| `NetPackageEntitySetPartActive` | NetPackage | 5 | 38 |
| `NetPackageEntitySetSkillLevelClient` | NetPackage | 6 | 22 |
| `NetPackageEntitySetSkillLevelServer` | NetPackageEntitySetSkillLevelClient | 4 | 26 |
| `NetPackageEntitySpawn` | NetPackageEntityTargeted | 6 | 60 |
| `NetPackageEntitySpawnResponse` | NetPackage | 5 | 153 |
| `NetPackageEntitySpeeds` | NetPackageEntityTargeted | 6 | 37 |
| `NetPackageEntityStatChanged` | NetPackageEntityTargeted | 6 | 88 |
| `NetPackageEntityStatsBuff` | NetPackage | 6 | 76 |
| `NetPackageEntityStealth` | NetPackage | 8 | 92 |
| `NetPackageEntityTargeted` | NetPackage | 6 | 28 |
| `NetPackageEntityTeleport` | NetPackageEntityPosAndRot | 3 | 60 |
| `NetPackageEntityVelocity` | NetPackageEntityTargeted | 6 | 53 |
| `NetPackageEntityWaypointList` | NetPackage | 5 | 39 |
| `NetPackageEntry` | Object | 1 | 3 |
| `NetPackageEventPrefab` | NetPackage | 6 | 48 |
| `NetPackageExplosionClient` | NetPackage | 6 | 60 |
| `NetPackageExplosionInitiate` | NetPackage | 6 | 55 |
| `NetPackageGameEventRequest` | NetPackage | 6 | 211 |
| `NetPackageGameEventResponse` | NetPackage | 9 | 135 |
| `NetPackageGameMessage` | NetPackage | 5 | 28 |
| `NetPackageGameStats` | NetPackage | 8 | 19 |
| `NetPackageHoldingItem` | NetPackage | 5 | 45 |
| `NetPackageHordeEvent` | NetPackage | 5 | 31 |
| `NetPackageIdMapping` | NetPackage | 7 | 18 |
| `NetPackageInfo` | Object | 1 | 3 |
| `NetPackageInventoryKeepOpen` | NetPackage | 5 | 6 |
| `NetPackageItemActionEffects` | NetPackage | 5 | 52 |
| `NetPackageItemDrop` | NetPackage | 6 | 37 |
| `NetPackageItemReload` | NetPackage | 5 | 18 |
| `NetPackageKeyExchangeComplete` | NetPackage | 6 | 8 |
| `NetPackageLandClaimRepair` | NetPackage | 5 | 33 |
| `NetPackageLobbyJoin` | NetPackage | 6 | 63 |
| `NetPackageLobbyRegisterClient` | NetPackage | 6 | 38 |
| `NetPackageLocalization` | NetPackage | 11 | 123 |
| `NetPackageLockTarget` | NetPackage | 7 | 46 |
| `NetPackageLogger` | Object | 4 | 84 |
| `NetPackageManager` | Object | 16 | 70 |
| `NetPackageMapChunks` | NetPackage | 8 | 109 |
| `NetPackageMapPosition` | NetPackage | 6 | 31 |
| `NetPackageMeasure` | Object | 3 | 40 |
| `NetPackageMetrics` | Object | 16 | 501 |
| `NetPackageMinEventFire` | NetPackage | 7 | 45 |
| `NetPackageModifyCVar` | NetPackage | 5 | 26 |
| `NetPackageNPCQuestList` | NetPackage | 11 | 180 |
| `NetPackageNavObject` | NetPackage | 8 | 77 |
| `NetPackageNetMetrics` | NetPackage | 6 | 28 |
| `NetPackageOwnedEntitySync` | NetPackage | 6 | 34 |
| `NetPackagePOIMetadataRequest` | NetPackage | 6 | 6 |
| `NetPackagePOIMetadataResponse` | NetPackage | 7 | 34 |
| `NetPackagePOIWaypoint` | NetPackage | 6 | 39 |
| `NetPackagePackageIds` | NetPackage | 8 | 121 |
| `NetPackageParticleEffect` | NetPackage | 5 | 30 |
| `NetPackagePartyActions` | NetPackage | 5 | 176 |
| `NetPackagePartyData` | NetPackage | 6 | 243 |
| `NetPackagePartyQuestChange` | NetPackage | 6 | 83 |
| `NetPackagePersistentPlayerPositions` | NetPackage | 7 | 42 |
| `NetPackagePersistentPlayerState` | NetPackage | 6 | 13 |
| `NetPackagePickupBlock` | NetPackage | 5 | 41 |
| `NetPackagePlayerData` | NetPackage | 6 | 15 |
| `NetPackagePlayerDenied` | NetPackage | 9 | 31 |
| `NetPackagePlayerDisconnect` | NetPackagePlayerData | 4 | 9 |
| `NetPackagePlayerEquipment` | NetPackageEntityTargeted | 5 | 61 |
| `NetPackagePlayerId` | NetPackage | 6 | 22 |
| `NetPackagePlayerInventory` | NetPackage | 6 | 61 |
| `NetPackagePlayerInventoryForAI` | NetPackage | 8 | 33 |
| `NetPackagePlayerLaserSight` | NetPackage | 5 | 70 |
| `NetPackagePlayerLogin` | NetPackage | 7 | 52 |
| `NetPackagePlayerLoginAnswer` | NetPackage | 8 | 50 |
| `NetPackagePlayerQuestPositions` | NetPackage | 6 | 30 |
| `NetPackagePlayerSetBackpackPosition` | NetPackage | 6 | 39 |
| `NetPackagePlayerSpawnedInWorld` | NetPackage | 6 | 47 |
| `NetPackagePlayerStats` | NetPackageEntityTargeted | 6 | 70 |
| `NetPackagePlayerTwitchStats` | NetPackageEntityTargeted | 5 | 52 |
| `NetPackagePlayerVendingMachine` | NetPackage | 5 | 30 |
| `NetPackageQuestEntitySpawn` | NetPackage | 8 | 37 |
| `NetPackageQuestEvent` | NetPackage | 16 | 368 |
| `NetPackageQuestGotoPoint` | NetPackage | 5 | 312 |
| `NetPackageQuestObjectiveUpdate` | NetPackage | 7 | 180 |
| `NetPackageQuestTreasurePoint` | NetPackage | 9 | 176 |
| `NetPackageRangeCheckDamageEntity` | NetPackage | 6 | 216 |
| `NetPackageRegionMetaData` | DynamicMeshServerData | 7 | 61 |
| `NetPackageRequestToEnterGame` | NetPackage | 5 | 7 |
| `NetPackageRequestToSpawnEntity` | NetPackage | 6 | 9 |
| `NetPackageRequestToSpawnPlayer` | NetPackage | 6 | 17 |
| `NetPackageSetAttackTarget` | NetPackageEntityTargeted | 5 | 24 |
| `NetPackageSetBlock` | NetPackage | 5 | 59 |
| `NetPackageSetBlockResponse` | NetPackage | 5 | 28 |
| `NetPackageSetBlockTexture` | NetPackage | 8 | 46 |
| `NetPackageSetProp` | NetPackage | 5 | 37 |
| `NetPackageSharedPartyKill` | NetPackage | 6 | 22 |
| `NetPackageSharedQuest` | NetPackage | 7 | 380 |
| `NetPackageShowToolbeltMessage` | NetPackage | 6 | 18 |
| `NetPackageSignDataRequest` | NetPackage | 5 | 5 |
| `NetPackageSignDataResponse` | NetPackage | 7 | 28 |
| `NetPackageSignDelete` | NetPackage | 5 | 122 |
| `NetPackageSimpleChat` | NetPackage | 6 | 116 |
| `NetPackageSimpleRPC` | NetPackage | 5 | 17 |
| `NetPackageSingleSignData` | NetPackage | 5 | 34 |
| `NetPackageSleeperPassiveChange` | NetPackageEntityTargeted | 4 | 21 |
| `NetPackageSleeperPose` | NetPackage | 5 | 23 |
| `NetPackageSleeperWakeup` | NetPackage | 6 | 20 |
| `NetPackageSoundAtPosition` | NetPackage | 5 | 36 |
| `NetPackageTeleportPlayer` | NetPackage | 5 | 56 |
| `NetPackageTileEntity` | NetPackage | 7 | 103 |
| `NetPackageTraderData` | NetPackage | 8 | 50 |
| `NetPackageTurretSpawn` | NetPackage | 5 | 207 |
| `NetPackageTurretSync` | NetPackage | 6 | 27 |
| `NetPackageTwitchAccess` | NetPackage | 6 | 55 |
| `NetPackageTwitchVoteScheduling` | NetPackage | 5 | 16 |
| `NetPackageVehicleCount` | NetPackage | 5 | 16 |
| `NetPackageVehicleDataSync` | NetPackage | 6 | 113 |
| `NetPackageVehiclePositions` | NetPackage | 5 | 35 |
| `NetPackageVehicleSpawn` | NetPackage | 5 | 86 |
| `NetPackageWallVolume` | NetPackage | 6 | 16 |
| `NetPackageWallVolumeRemove` | NetPackage | 6 | 11 |
| `NetPackageWaterSet` | NetPackage | 10 | 36 |
| `NetPackageWaterSimChunkUpdate` | NetPackage | 12 | 65 |
| `NetPackageWaypoint` | NetPackage | 5 | 29 |
| `NetPackageWeather` | NetPackage | 7 | 59 |
| `NetPackageWireActions` | NetPackage | 6 | 163 |
| `NetPackageWireToolActions` | NetPackage | 5 | 254 |
| `NetPackageWorldAreas` | NetPackage | 6 | 31 |
| `NetPackageWorldFolder` | NetPackage | 18 | 93 |
| `NetPackageWorldInfo` | NetPackage | 7 | 83 |
| `NetPackageWorldInitInfo` | NetPackage | 6 | 58 |
| `NetPackageWorldInitInfoRequest` | NetPackage | 6 | 38 |
| `NetPackageWorldSpawnPoints` | NetPackage | 6 | 8 |
| `NetPackageWorldTime` | NetPackage | 6 | 9 |

## Clone annotation status

| Status | Packages |
|---|---|
| Golden body (loadgen) | EntityPosAndRot, EntityRelPosAndRot, EntityAliveFlags, EntityLookAt, DamageEntity, ExplosionInitiate, PlayerLogin, PackageIds, PlayerLoginAnswer, AuthConfirmation, RequestToEnterGame, RequestToSpawnPlayer, SimpleChat |
| Name only (this table) | all others |
| Residual / skip for M1 clone | EAC, Encryption*, Twitch*, Editor*, Discord* |

## Changelog

- **2026-07-20:** Generated from dedi-complete auto dump for zig-clone RE.

- **2026-10-24:** Table regenerated from the V3.3.0 (b18) assembly: 193 rows (was 196). Three packages added (`NetPackageLockTarget`, `NetPackageSingleSignData`, `NetPackageSignDelete`) and six removed (the two inventory-data, two inventory-transaction and the lock request/response packages), all under the same names and bases the wire delta uses ([changelog-3.3.0.md](../releases/changelog-3.3.0.md) §4).
