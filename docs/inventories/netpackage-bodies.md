# NetPackage wire-body catalog

**Kind:** auto-extracted per-package wire-body reference (ordered `write()` field
sequence). Not a hand-narrative; complements the annotated bodies in
[`../protocol-packages.md`](../protocol-packages.md) and the census in
[`netpackages.md`](netpackages.md).  
**Regenerate:** `mono tools/bin/WireBodies.exe "$ASM" docs/inventories/netpackage-bodies.md`.  
**Method:** [`../re-methodology.md`](../re-methodology.md).  
**Hub:** [`INDEX.md`](../INDEX.md).

Each row is one `BinaryWriter.Write(T)` or nested `.Write(writer)` in emit order.
**Source** is the nearest preceding field/getter (best-effort; inside a loop it
shows the element accessor, e.g. `Item`/`Current`). **Wire** is the on-the-wire
type. A **control-flow** note flags loops (a `(list/array count)` row is followed
by its per-element row(s)) and conditionals; for those, the flat sequence is the
backbone and the exact framing is in the per-package narrative where one exists.
The leading package handle (`base.write` -> `NetPackage.write`) is not repeated.

**Extractor limits (honest):** read-side-only fields (rare), values built by
arithmetic before a `Write`, and helper-delegated bodies may show `-` as the
source; nested `.Write` rows name the serializer type, whose own layout is in its
own doc/dump. Verify a load-bearing body against its `write`/`read` IL before
cloning.

Total packages with an extractable `write()` body: **183**.
Not listed (no own `write()` body - inherited serialization, abstract bases, enums, or helpers): `NetPackageDirection`, `NetPackageEncryptionRequest`, `NetPackageEntityAddExpServer`, `NetPackageEntityAddScoreServer`, `NetPackageEntitySetSkillLevelServer`, `NetPackageEntityTeleport`, `NetPackageEntry`, `NetPackageInfo`, `NetPackageInventoryKeepOpen`, `NetPackageLogger`, `NetPackageMeasure`, `NetPackageMetrics`, `NetPackagePlayerDisconnect`, `NetPackageSleeperPassiveChange`.

## NetPackage
`write` IL=6, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `PackageId` | u16 |

## NetPackageAddRemoveBuff
`write` IL=28, 6 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `buffName` | string |
| 3 | `duration` | f32 |
| 4 | `adding` | bool |
| 5 | `instigatorId` | i32 |
| 6 | `instigatorPos` | `StreamUtils.Write` |

## NetPackageAllyRequest
`write` IL=18, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `source` | `PlatformUserIdentifierExtensions.ToStream` |
| 2 | `target` | `PlatformUserIdentifierExtensions.ToStream` |
| 3 | `addAlly` | bool |

## NetPackageAllyResponse
`write` IL=26, 5 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `source` | `PlatformUserIdentifierExtensions.ToStream` |
| 2 | `target` | `PlatformUserIdentifierExtensions.ToStream` |
| 3 | `newStatus` | u8 |
| 4 | `allyEventSource` | u8 |
| 5 | `allyEventTarget` | u8 |

## NetPackageAnimateBlock
`write` IL=24, 5 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `blockPosition` | `StreamUtils.Write` |
| 2 | `animParamater` | string |
| 3 | `animType` | i32 |
| 4 | `animationInteger` | i32 |
| 5 | `animationBool` | bool |

## NetPackageAudio
`write` IL=53, 9 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `soundGroupName` | string |
| 2 | `play` | bool |
| 3 | `x` | f32 |
| 4 | `y` | f32 |
| 5 | `z` | f32 |
| 6 | `playOnEntity` | bool |
| 7 | `occlusion` | f32 |
| 8 | `volumeScale` | f32 |
| 9 | `signalOnly` | bool |

## NetPackageAudioPlayInHead
`write` IL=12, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `soundName` | string |
| 2 | `isUnique` | bool |

## NetPackageAuthConfirmation
`write` IL=4, 0 wire field(s).

_No BinaryWriter/nested Write calls detected (empty body: only the base handle, or fully helper-delegated)._

## NetPackageAuthState
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `stateKey` | string |

## NetPackageBag
`write` IL=19, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `ms` | u16 (list/array count) |

## NetPackageBiomeIntensity
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `bi` | `BiomeIntensity.Write` |

## NetPackageBlockLimitTracking
`write` IL=27, 2 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `amounts` | i32 (list/array count) |
| 2 | `Item` | i32 |

## NetPackageBlockTrigger
`write` IL=13, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `blockPos` | `StreamUtils.Write` |
| 2 | `rawData` | u32 |

## NetPackageBloodmoonMusic
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `IsBloodMoonMusicEligible` | bool |

## NetPackageBossEvent
`write` IL=53, 7 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `bossGroupID` | i32 |
| 2 | `eventType` | u8 |
| 3 | `bossGroupType` | u8 |
| 4 | `entityID` | i32 |
| 5 | `bossIcon1` | string |
| 6 | `minionIDs` | i32 (list/array count) |
| 7 | `Item` | i32 |

## NetPackageChat
`write` IL=63, 7 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `chatType` | u8 |
| 2 | `senderEntityId` | i32 |
| 3 | `msg` | string |
| 4 | `msgSender` | u8 |
| 5 | `bbMode` | u8 |
| 6 | `recipientEntityIds` | i32 (list/array count) |
| 7 | `Item` | i32 (list/array count) |

## NetPackageChunk
`write` IL=57, 5 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `bOverwriteExisting` | bool |
| 2 | `X` | i16 |
| 3 | `Y` | i16 |
| 4 | `Z` | i16 |
| 5 | `serializedData` | i32 (list/array count) |

## NetPackageChunkClusterInfo
`write` IL=36, 7 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `name` | string |
| 2 | `x` | i32 |
| 3 | `y` | i32 |
| 4 | `x` | i32 |
| 5 | `y` | i32 |
| 6 | `bInfinite` | bool |
| 7 | `pos` | `StreamUtils.Write` |

## NetPackageChunkRemove
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `chunkKey` | i64 |

## NetPackageChunkRemoveAll
`write` IL=4, 0 wire field(s).

_No BinaryWriter/nested Write calls detected (empty body: only the base handle, or fully helper-delegated)._

## NetPackageClientInfo
`write` IL=41, 4 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `playerIds` | u16 (list/array count) |
| 2 | `Item` | i32 |
| 3 | `Item` | i16 |
| 4 | `Item` | bool |

## NetPackageCloseAllWindows
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `_playerIdToClose` | i32 |

## NetPackageConfigFile
`write` IL=25, 4 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `name` | string |
| 2 | `data` | i32 |
| 3 | `data` | bytes[] |
| 4 | `-` | i32 |

## NetPackageConsoleCmdClient
`write` IL=31, 3 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `lines` | i32 (list/array count) |
| 2 | `Item` | string |
| 3 | `bExecute` | bool (list/array count) |

## NetPackageConsoleCmdServer
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `cmd` | string |

## NetPackageDamageEntity
`write` IL=172, 37 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `damageSrc` | u8 |
| 3 | `damageTyp` | u8 |
| 4 | `strength` | u16 |
| 5 | `hitDirection` | u8 |
| 6 | `hitBodyPart` | i16 |
| 7 | `movementState` | u8 |
| 8 | `bPainHit` | bool |
| 9 | `bFatal` | bool |
| 10 | `bCritical` | bool |
| 11 | `attackerEntityId` | i32 |
| 12 | `x` | f32 |
| 13 | `y` | f32 |
| 14 | `z` | f32 |
| 15 | `blockPos` | `StreamUtils.Write` |
| 16 | `hitTransformName` | string |
| 17 | `x` | f32 |
| 18 | `y` | f32 |
| 19 | `z` | f32 |
| 20 | `x` | f32 |
| 21 | `y` | f32 |
| 22 | `damageMultiplier` | f32 |
| 23 | `random` | f32 |
| 24 | `bIgnoreConsecutiveDamages` | bool |
| 25 | `bIsDamageTransfer` | bool |
| 26 | `bDismember` | bool |
| 27 | `bCrippleLegs` | bool |
| 28 | `bTurnIntoCrawler` | bool |
| 29 | `bonusDamageType` | u8 |
| 30 | `StunType` | u8 |
| 31 | `StunDuration` | f32 |
| 32 | `bFromBuff` | bool |
| 33 | `ArmorSlot` | u8 |
| 34 | `ArmorSlotGroup` | u8 |
| 35 | `ArmorDamage` | u16 |
| 36 | `attackingItem` | bool |
| 37 | `attackingItem` | `ItemValue.Write` |

## NetPackageDebug
`write` IL=34, 5 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `type` | i16 |
| 2 | `entityId` | i32 |
| 3 | `data` | i32 |
| 4 | `data` | i32 |
| 5 | `data` | bytes[] |

## NetPackageDecoResetWorldChunk
`write` IL=15, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `ms` | i32 (list/array count) |

## NetPackageDecoResetWorldRect
`write` IL=15, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `ms` | i32 (list/array count) |

## NetPackageDecoUpdate
`write` IL=19, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `firstPackage` | bool |
| 2 | `ms` | i32 (list/array count) |

## NetPackageDeleteChunkData
`write` IL=27, 2 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `chunkKeys` | i32 (list/array count) |
| 2 | `Item` | i64 |

## NetPackageDiscordIdMappings
`write` IL=56, 7 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | bool |
| 2 | `entityId` | i32 |
| 3 | `remove` | bool |
| 4 | `discordId` | u64 |
| 5 | `entityIds` | i32 (list/array count) |
| 6 | `Item` | i32 |
| 7 | `Item` | u64 |

## NetPackageDiscordLobbySecret
`write` IL=12, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `lobbyType` | u8 |
| 2 | `lobbySecret` | `StreamUtils.Write` |

## NetPackageDroneDataSync
`write` IL=27, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `senderId` | i32 |
| 2 | `vehicleId` | i32 |
| 3 | `syncFlags` | u16 |
| 4 | `entityData` | u16 (list/array count) |

## NetPackageDroneParticleEffect
`write` IL=12, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `pe` | `ParticleEffect.Write` |
| 2 | `entityThatCausedIt` | i32 |

## NetPackageDropItemsContainer
`write` IL=42, 5 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `droppedByID` | i32 |
| 2 | `containerEntity` | string |
| 3 | `worldPos` | `StreamUtils.Write` |
| 4 | `items` | u16 |
| 5 | `items` | `ItemStack.Write` |

## NetPackageDynamicClientArrive
`write` IL=42, 4 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `Items` | i32 (list/array count) |
| 2 | `X` | i32 |
| 3 | `Z` | i32 |
| 4 | `UpdateTime` | i32 |

## NetPackageDynamicMesh
`write` IL=192, 5 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `X` | i32 |
| 2 | `Z` | i32 |
| 3 | `UpdateTime` | i32 |
| 4 | `Z` | i32 |
| 5 | `bytes` | bytes[] |

## NetPackageEAC
`write` IL=29, 2 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `data` | i32 |
| 2 | `data` | u8 |

## NetPackageEditorAddVolumeFromClient
`write` IL=31, 6 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `addType` | u8 |
| 2 | `volumeType` | u8 |
| 3 | `startPos` | `StreamUtils.Write` |
| 4 | `size` | `StreamUtils.Write` |
| 5 | `prefabInstanceId` | i16 |
| 6 | `existingIndex` | i16 |

## NetPackageEditorPrefabInstance
`write` IL=41, 9 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `changeType` | u8 |
| 2 | `id` | i32 |
| 3 | `boundingBoxPosition` | `StreamUtils.Write` |
| 4 | `boundingBoxSize` | `StreamUtils.Write` |
| 5 | `name` | string |
| 6 | `size` | `StreamUtils.Write` |
| 7 | `filename` | string |
| 8 | `localRotation` | i32 |
| 9 | `yOffset` | i32 |

## NetPackageEditorUpdateVolume
`write` IL=26, 5 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `changeType` | u8 |
| 2 | `prefabInstanceId` | i32 |
| 3 | `volumeId` | i32 |
| 4 | `VolumeType` | u8 |
| 5 | `volume` | `PrefabVolumeAbs.Write` |

## NetPackageEmitSmell
`write` IL=17, 2 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `EntityId` | i32 |
| 2 | `SmellName` | string |

## NetPackageEncryptionPublicKey
`write` IL=28, 5 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `ExchangePublicKeyParamsXml` | string |
| 2 | `Hash` | i32 |
| 3 | `Hash` | bytes[] |
| 4 | `SignedHash` | i32 |
| 5 | `SignedHash` | bytes[] |

## NetPackageEncryptionSharedKey
`write` IL=24, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `EncryptionKey` | i32 |
| 2 | `EncryptionKey` | bytes[] |
| 3 | `IntegrityKey` | i32 |
| 4 | `IntegrityKey` | bytes[] |

## NetPackageEntityAddExpClient
`write` IL=30, 5 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `xp` | i32 |
| 3 | `xpType` | i16 |
| 4 | `usedItem` | bool |
| 5 | `usedItem` | `ItemValue.Write` |

## NetPackageEntityAddScoreClient
`write` IL=27, 5 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `zombieKills` | i16 |
| 3 | `playerKills` | i16 |
| 4 | `otherTeamNumber` | i16 |
| 5 | `conditions` | i32 |

## NetPackageEntityAddVelocity
`write` IL=12, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `addVelocity` | `StreamUtils.Write` |

## NetPackageEntityAliveFlags
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `flags` | u16 |

## NetPackageEntityAnimationData
`write` IL=29, 2 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `animationParameterData` | i32 (list/array count) |
| 2 | `Item` | `AnimParamData.Write` |

## NetPackageEntityAttach
`write` IL=21, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `attachType` | u8 |
| 2 | `riderId` | i32 |
| 3 | `vehicleId` | i32 |
| 4 | `slot` | i16 |

## NetPackageEntityAwardKillServer
`write` IL=12, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `EntityId` | i32 |
| 2 | `KilledEntityId` | i32 |

## NetPackageEntityCollect
`write` IL=12, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `playerId` | i32 |

## NetPackageEntityLookAt
`write` IL=22, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `x` | i32 |
| 2 | `y` | i32 |
| 3 | `z` | i32 |

## NetPackageEntityMapMarkerRemove
`write` IL=24, 4 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `RemoveByType` | i32 |
| 2 | `entityId` | i32 |
| 3 | `position` | `StreamUtils.Write` |
| 4 | `mapObjectType` | i32 |

## NetPackageEntityPhysics
`write` IL=77, 15 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `Flags` | u16 |
| 2 | `EntityId` | i32 |
| 3 | `x` | f32 |
| 4 | `y` | f32 |
| 5 | `z` | f32 |
| 6 | `x` | f32 |
| 7 | `y` | f32 |
| 8 | `z` | f32 |
| 9 | `w` | f32 |
| 10 | `x` | f32 |
| 11 | `y` | f32 |
| 12 | `z` | f32 |
| 13 | `x` | f32 |
| 14 | `y` | f32 |
| 15 | `z` | f32 |

## NetPackageEntityPosAndRot
`write` IL=76, 12 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `x` | f32 |
| 2 | `y` | f32 |
| 3 | `z` | f32 |
| 4 | `bUseQRotation` | bool |
| 5 | `x` | f32 |
| 6 | `y` | f32 |
| 7 | `z` | f32 |
| 8 | `x` | f32 |
| 9 | `y` | f32 |
| 10 | `z` | f32 |
| 11 | `w` | f32 |
| 12 | `onGround` | bool |

## NetPackageEntityPrimeDetonator
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `id` | i32 |

## NetPackageEntityRagdoll
`write` IL=59, 9 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `flags` | u8 |
| 3 | `duration` | f32 |
| 4 | `bodyPart` | i16 |
| 5 | `forceVec` | `StreamUtils.Write` |
| 6 | `forceWorldPos` | `StreamUtils.Write` |
| 7 | `hipPos` | `StreamUtils.Write` |
| 8 | `mode` | u8 |
| 9 | `state` | u8 |

## NetPackageEntityRelPosAndRot
`write` IL=30, 5 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `x` | i16 |
| 2 | `y` | i16 |
| 3 | `z` | i16 |
| 4 | `onGround` | bool |
| 5 | `updateSteps` | i16 |

## NetPackageEntityRemove
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `reason` | u8 |

## NetPackageEntityRotation
`write` IL=54, 8 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `bUseQRotation` | bool |
| 2 | `x` | i16 |
| 3 | `y` | i16 |
| 4 | `z` | i16 |
| 5 | `x` | f32 |
| 6 | `y` | f32 |
| 7 | `z` | f32 |
| 8 | `w` | f32 |

## NetPackageEntitySetPartActive
`write` IL=20, 3 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `id` | i32 |
| 2 | `active` | bool |
| 3 | `partName` | string |

## NetPackageEntitySetSkillLevelClient
`write` IL=16, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `skill` | string |
| 3 | `level` | i32 |

## NetPackageEntitySpawn
`write` IL=9, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `es` | `EntityCreationData.write` |

## NetPackageEntitySpawnResponse
`write` IL=12, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `success` | bool |
| 2 | `itemValue` | `ItemValue.Write` |

## NetPackageEntitySpeeds
`write` IL=17, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `movementState` | u8 |
| 2 | `speedForward` | f32 |
| 3 | `speedStrafe` | f32 |

## NetPackageEntityStatChanged
`write` IL=25, 5 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `m_instigatorId` | i32 |
| 2 | `m_enumStat` | u8 |
| 3 | `m_value` | f32 |
| 4 | `m_max` | f32 |
| 5 | `m_maxModifier` | f32 |

## NetPackageEntityStatsBuff
`write` IL=18, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `m_entityId` | i32 |
| 2 | `data` | i32 |
| 3 | `data` | bytes[] |

## NetPackageEntityStealth
`write` IL=12, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `id` | i32 |
| 2 | `data` | u16 |

## NetPackageEntityTargeted
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |

## NetPackageEntityVelocity
`write` IL=23, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `bAdd` | bool |
| 2 | `x` | f32 |
| 3 | `y` | f32 |
| 4 | `z` | f32 |

## NetPackageEntityWaypointList
`write` IL=39, 4 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `listType` | i16 |
| 2 | `positions` | i32 (list/array count) |
| 3 | `Item1` | i32 |
| 4 | `Item2` | `StreamUtils.Write` |

## NetPackageEventPrefab
`write` IL=13, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `operation` | u8 |
| 2 | `serializablePi` | `Serializable.Write` |

## NetPackageExplosionClient
`write` IL=60, 9 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `center` | `StreamUtils.Write` |
| 2 | `rotation` | `StreamUtils.Write` |
| 3 | `expType` | i16 |
| 4 | `blastPower` | u16 |
| 5 | `blastRadius` | u16 |
| 6 | `blockDamage` | u16 |
| 7 | `entityId` | i32 |
| 8 | `explosionChanges` | u16 (list/array count) |
| 9 | `Item` | `BlockChangeInfo.Write` |

## NetPackageExplosionInitiate
`write` IL=55, 10 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `worldPos` | `StreamUtils.Write` |
| 2 | `blockPos` | `StreamUtils.Write` |
| 3 | `rotation` | `StreamUtils.Write` |
| 4 | `explosionData` | u16 |
| 5 | `-` | bytes[] |
| 6 | `entityId` | i32 |
| 7 | `delay` | f32 |
| 8 | `bRemoveBlockAtExplPosition` | bool |
| 9 | `itemValueExplosive` | bool |
| 10 | `itemValueExplosive` | `ItemValue.Write` |

## NetPackageGameEventRequest
`write` IL=83, 12 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `eventName` | string |
| 2 | `entityID` | i32 |
| 3 | `extraData` | string |
| 4 | `tag` | string |
| 5 | `isTwitchEvent` | bool |
| 6 | `crateShare` | bool |
| 7 | `allowRefunds` | bool |
| 8 | `sequenceLink` | string |
| 9 | `variables` | u8 (list/array count) |
| 10 | `Item1` | string |
| 11 | `Item2` | string |
| 12 | `target` | `ActionTarget.Write` |

## NetPackageGameEventResponse
`write` IL=102, 14 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `eventName` | string |
| 2 | `targetEntityID` | i32 |
| 3 | `extraData` | string |
| 4 | `tag` | string |
| 5 | `responseType` | u8 |
| 6 | `entitySpawnedID` | i32 |
| 7 | `actionKey` | string |
| 8 | `index` | i32 |
| 9 | `blockList` | i32 |
| 10 | `blockList` | i32 (list/array count) |
| 11 | `Item` | `StreamUtils.Write` |
| 12 | `index` | i32 (list/array count) |
| 13 | `isDespawn` | bool |
| 14 | `blockPos` | `StreamUtils.Write` |

## NetPackageGameMessage
`write` IL=17, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `msgType` | u8 |
| 2 | `mainEntityId` | i32 |
| 3 | `secondaryEntityId` | i32 |

## NetPackageGameStats
`write` IL=15, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `ms` | i16 (list/array count) |

## NetPackageHoldingItem
`write` IL=16, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `holdingItemStack` | `ItemStack.Write` |
| 3 | `holdingItemIndex` | u8 |

## NetPackageHordeEvent
`write` IL=31, 5 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `m_event` | u8 |
| 2 | `Item` | f32 |
| 3 | `Item` | f32 |
| 4 | `Item` | f32 |
| 5 | `m_maxDist` | f32 |

## NetPackageIdMapping
`write` IL=18, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `name` | string |
| 2 | `data` | i32 |
| 3 | `data` | bytes[] |

## NetPackageInventoryDataRequest
`write` IL=12, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `keyHash` | `KeyHashPair.Write` |
| 2 | `managerToken` | `StreamUtils.Write` |

## NetPackageInventoryDataResponse
`write` IL=24, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `success` | bool |
| 2 | `errorMsg` | string |
| 3 | `inventoryKey` | `StreamUtils.Write` |
| 4 | `managerToken` | `StreamUtils.Write` |

## NetPackageInventoryTransactionRequest
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `tx` | `InventoryTransaction.Write` |

## NetPackageInventoryTransactionResponse
`write` IL=66, 6 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `inventories` | bool |
| 2 | `-` | i32 |
| 3 | `success` | bool |
| 4 | `keys` | i32 (list/array count) |
| 5 | `Item` | `StreamUtils.Write` |
| 6 | `Item` | bool |

## NetPackageItemActionEffects
`write` IL=52, 8 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `slotIdx` | u8 |
| 3 | `actionIdx` | u8 |
| 4 | `firingState` | u8 |
| 5 | `zero` | bool |
| 6 | `startPos` | `StreamUtils.Write` |
| 7 | `direction` | `StreamUtils.Write` |
| 8 | `userData` | i32 |

## NetPackageItemDrop
`write` IL=37, 8 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `itemStack` | `ItemStack.Write` |
| 2 | `dropPos` | `StreamUtils.Write` |
| 3 | `initialMotion` | `StreamUtils.Write` |
| 4 | `randomPosAdd` | `StreamUtils.Write` |
| 5 | `lifetime` | f32 |
| 6 | `entityId` | i32 |
| 7 | `clientInstanceId` | i32 |
| 8 | `bDropPosIsRelativeToHead` | bool |

## NetPackageItemReload
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |

## NetPackageKeyExchangeComplete
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `wasSuccessful` | bool |

## NetPackageLandClaimRepair
`write` IL=26, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `x` | i64 |
| 2 | `y` | i64 |
| 3 | `z` | i64 |
| 4 | `beginRepair` | bool |

## NetPackageLight
`write` IL=12, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `lightLevel` | f32 |

## NetPackageLobbyJoin
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `serverLobbyId` | `PlatformLobbyId.Write` |

## NetPackageLobbyRegisterClient
`write` IL=12, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `lobbyId` | `PlatformLobbyId.Write` |
| 2 | `overwriteExistingLobby` | bool |

## NetPackageLocalization
`write` IL=30, 4 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `seqNr` | i32 |
| 2 | `totalParts` | i32 |
| 3 | `data` | i32 |
| 4 | `data` | bytes[] |

## NetPackageLockRequest
`write` IL=62, 6 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `locking` | bool |
| 2 | `channel` | u16 |
| 3 | `targets` | i32 |
| 4 | `context` | string |
| 5 | `FullName` | string |
| 6 | `context` | `ILockContext.Write` |

## NetPackageLockResponse
`write` IL=74, 9 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `locking` | bool |
| 2 | `success` | bool |
| 3 | `errorMsg` | string |
| 4 | `isForceUnlocked` | bool |
| 5 | `channel` | u16 |
| 6 | `targets` | i32 |
| 7 | `context` | string |
| 8 | `FullName` | string |
| 9 | `context` | `ILockContext.Write` |

## NetPackageMapChunks
`write` IL=109, 5 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `Position` | u16 (list/array count) |
| 3 | `Item` | i32 |
| 4 | `-` | u16 |
| 5 | `BaseStream` | u16 (list/array count) |

## NetPackageMapPosition
`write` IL=12, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `mapMiddlePosition` | `StreamUtils.Write` |

## NetPackageMinEventFire
`write` IL=35, 6 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `selfEntityID` | i32 |
| 2 | `otherEntityID` | i32 |
| 3 | `eventType` | u8 |
| 4 | `eventPackageType` | u8 |
| 5 | `itemValue` | `ItemValue.Write` |
| 6 | `rawData` | u32 |

## NetPackageModifyCVar
`write` IL=21, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `m_entityId` | i32 |
| 2 | `cvarName` | string |
| 3 | `value` | f32 |
| 4 | `operation` | i16 |

## NetPackageNavObject
`write` IL=40, 7 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `navObjectClass` | string |
| 2 | `name` | string |
| 3 | `position` | `StreamUtils.Write` |
| 4 | `isAdd` | bool |
| 5 | `useOverrideColor` | bool |
| 6 | `usingLocalizationId` | bool |
| 7 | `entityId` | i32 |

## NetPackageNetMetrics
`write` IL=28, 5 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `enable` | bool |
| 2 | `duration` | f32 |
| 3 | `loop` | bool |
| 4 | `content` | string |
| 5 | `csv` | string |

## NetPackageNPCQuestList
`write` IL=99, 14 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `npcEntityID` | i32 |
| 2 | `playerEntityID` | i32 |
| 3 | `eventType` | u8 |
| 4 | `tierLevel` | i32 |
| 5 | `questPacketEntries` | i32 |
| 6 | `questPacketEntries` | `QuestPacketEntry.write` |
| 7 | `questPacketEntries` | i32 |
| 8 | `tierLevel` | i32 |
| 9 | `removeIndex` | u8 |
| 10 | `tierLevel` | i32 |
| 11 | `questGiverPos` | `StreamUtils.Write` |
| 12 | `prefabPos` | `StreamUtils.Write` |
| 13 | `tierLevel` | i32 |
| 14 | `questGiverPos` | `StreamUtils.Write` |

## NetPackageOwnedEntitySync
`write` IL=20, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `ownerId` | i32 |
| 2 | `entityId` | i32 |
| 3 | `entityClassId` | i32 |
| 4 | `syncType` | u8 |

## NetPackagePackageIds
`write` IL=62, 7 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | `VersionInformation.Write` |
| 2 | `PackageMappings` | i32 |
| 3 | `Name` | string |
| 4 | `serverUseEAC` | bool |
| 5 | `hasHostUserAndToken` | bool |
| 6 | `Item1` | `PlatformUserIdentifierExtensions.ToStream` |
| 7 | `Item2` | string |

## NetPackageParticleEffect
`write` IL=20, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `pe` | `ParticleEffect.Write` |
| 2 | `entityThatCausedIt` | i32 |
| 3 | `forceCreation` | bool |
| 4 | `worldSpawn` | bool |

## NetPackagePartyActions
`write` IL=25, 4 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `currentOperation` | u8 |
| 2 | `invitedByEntityID` | i32 |
| 3 | `invitedEntityID` | i32 |
| 4 | `voiceLobbyId` | string |

## NetPackagePartyData
`write` IL=59, 8 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `PartyID` | i32 |
| 2 | `LeaderIndex` | u8 |
| 3 | `VoiceLobbyId` | string |
| 4 | `partyMembers` | i32 |
| 5 | `partyMembers` | i32 |
| 6 | `changedEntityID` | i32 |
| 7 | `partyAction` | u8 |
| 8 | `disbandParty` | bool |

## NetPackagePartyQuestChange
`write` IL=20, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `senderEntityID` | i32 |
| 2 | `objectiveIndex` | u8 |
| 3 | `isComplete` | bool |
| 4 | `questCode` | i32 |

## NetPackagePersistentPlayerPositions
`write` IL=38, 3 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `positions` | i32 (list/array count) |
| 2 | `Current` | `PlatformUserIdentifierExtensions.ToStream` |
| 3 | `-` | `StreamUtils.Write` |

## NetPackagePersistentPlayerState
`write` IL=13, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `m_reason` | u8 |
| 2 | `m_ppData` | `PersistentPlayerData.Write` |

## NetPackagePickupBlock
`write` IL=22, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `blockPos` | `StreamUtils.Write` |
| 2 | `rawData` | u32 |
| 3 | `playerId` | i32 |
| 4 | `persistentPlayerId` | `PlatformUserIdentifierExtensions.ToStream` |

## NetPackagePlayerData
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `playerDataFile` | `PlayerDataFile.WriteNetwork` |

## NetPackagePlayerDenied
`write` IL=25, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `reason` | i32 |
| 2 | `apiResponseEnum` | i32 |
| 3 | `banUntil` | i64 |
| 4 | `customReason` | string |

## NetPackagePlayerEquipment
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `equipment` | `Equipment.Write` |

## NetPackagePlayerId
`write` IL=21, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `id` | i32 |
| 2 | `teamNumber` | i16 |
| 3 | `playerDataFile` | `PlayerDataFile.WriteNetwork` |
| 4 | `chunkViewDim` | i32 |

## NetPackagePlayerInventory
`write` IL=107, 8 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `toolbelt` | bool |
| 2 | `bag` | bool |
| 3 | `bag` | `Bag.Write` |
| 4 | `equipment` | bool |
| 5 | `equipment` | i32 |
| 6 | `m_unlockedCosmetics` | i32 (list/array count) |
| 7 | `Item` | i32 |
| 8 | `dragAndDropItem` | bool (list/array count) |

## NetPackagePlayerInventoryForAI
`write` IL=18, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `m_entityId` | i32 |

## NetPackagePlayerLaserSight
`write` IL=19, 3 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `laserSightActive` | bool |
| 3 | `laserSightPosition` | `StreamUtils.Write` |

## NetPackagePlayerLogin
`write` IL=52, 8 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `playerName` | string |
| 2 | `Item1` | `PlatformUserIdentifierExtensions.ToStream` |
| 3 | `Item2` | string |
| 4 | `Item1` | `PlatformUserIdentifierExtensions.ToStream` |
| 5 | `Item2` | string |
| 6 | `version` | string |
| 7 | `compVersion` | string |
| 8 | `discordUserId` | u64 |

## NetPackagePlayerLoginAnswer
`write` IL=46, 7 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `bAllowed` | bool |
| 2 | `data` | string |
| 3 | `platformLobbyId` | `PlatformLobbyId.Write` |
| 4 | `Item1` | `PlatformUserIdentifierExtensions.ToStream` |
| 5 | `Item2` | string |
| 6 | `Item1` | `PlatformUserIdentifierExtensions.ToStream` |
| 7 | `Item2` | string |

## NetPackagePlayerQuestPositions
`write` IL=30, 3 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `questPositions` | i32 (list/array count) |
| 3 | `Current` | `QuestPositionData.Write` |

## NetPackagePlayerSetBackpackPosition
`write` IL=39, 4 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `playerId` | i32 |
| 2 | `positions` | u8 |
| 3 | `positions` | u8 (list/array count) |
| 4 | `Item` | `StreamUtils.Write` |

## NetPackagePlayerSpawnedInWorld
`write` IL=16, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `respawnReason` | i32 |
| 2 | `position` | `StreamUtils.Write` |
| 3 | `entityId` | i32 |

## NetPackagePlayerStats
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityNetworkStats` | `EntityNetworkStats.write` |

## NetPackagePlayerTwitchStats
`write` IL=26, 5 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `twitchEnabled` | bool |
| 2 | `twitchSafe` | bool |
| 3 | `twitchVoteLock` | u8 |
| 4 | `twitchVisionDisabled` | bool |
| 5 | `twitchActionsEnabled` | u8 |

## NetPackagePlayerVendingMachine
`write` IL=28, 5 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `userId` | `PlatformUserIdentifierExtensions.ToStream` |
| 2 | `x` | i32 |
| 3 | `y` | i32 |
| 4 | `z` | i32 |
| 5 | `removing` | bool |

## NetPackagePOIAround
`write` IL=15, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `ms` | i32 (list/array count) |

## NetPackagePOIWaypoint
`write` IL=31, 5 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `operation` | u8 |
| 2 | `entityId` | i32 |
| 3 | `prefabInstanceId` | i32 |
| 4 | `hiddenOnCompass` | bool |
| 5 | `prefabInstanceId` | i32 |

## NetPackageQuestEntitySpawn
`write` IL=16, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityType` | i32 |
| 2 | `gamestageGroup` | string |
| 3 | `entityIDQuestHolder` | i32 |

## NetPackageQuestEvent
`write` IL=205, 24 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityID` | i32 |
| 2 | `prefabPos` | `StreamUtils.Write` |
| 3 | `eventType` | u8 |
| 4 | `questTags` | string |
| 5 | `questCode` | i32 |
| 6 | `SubscribeTo` | bool |
| 7 | `FetchModeType` | u8 |
| 8 | `SharedWithList` | u8 |
| 9 | `SharedWithList` | u8 |
| 10 | `SharedWithList` | i32 |
| 11 | `blockIndex` | string |
| 12 | `eventName` | string |
| 13 | `SharedWithList` | u8 |
| 14 | `SharedWithList` | u8 |
| 15 | `SharedWithList` | i32 |
| 16 | `activateList` | u8 |
| 17 | `activateList` | u8 (list/array count) |
| 18 | `Item` | `StreamUtils.Write` |
| 19 | `extraData` | u64 (list/array count) |
| 20 | `questID` | string |
| 21 | `SharedWithList` | u8 |
| 22 | `SharedWithList` | u8 |
| 23 | `SharedWithList` | i32 |
| 24 | `factionPointOverride` | i32 |

## NetPackageQuestGotoPoint
`write` IL=52, 10 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `playerId` | i32 |
| 2 | `questCode` | i32 |
| 3 | `GotoType` | u8 |
| 4 | `questTags` | string |
| 5 | `x` | i32 |
| 6 | `y` | i32 |
| 7 | `size` | `StreamUtils.Write` |
| 8 | `difficulty` | u8 |
| 9 | `biomeFilterType` | u8 |
| 10 | `biomeFilter` | string |

## NetPackageQuestObjectiveUpdate
`write` IL=21, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `senderEntityID` | i32 |
| 2 | `questCode` | i32 |
| 3 | `eventType` | u8 |
| 4 | `blockPos` | `StreamUtils.Write` |

## NetPackageQuestTreasurePoint
`write` IL=59, 12 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `ActionType` | u8 |
| 2 | `questCode` | i32 |
| 3 | `position` | `StreamUtils.Write` |
| 4 | `playerId` | i32 |
| 5 | `distance` | f32 |
| 6 | `offset` | i32 |
| 7 | `treasureRadius` | f32 |
| 8 | `blocksPerReduction` | i32 |
| 9 | `questCode` | i32 |
| 10 | `position` | `StreamUtils.Write` |
| 11 | `treasureOffset` | `StreamUtils.Write` |
| 12 | `useNearby` | bool |

## NetPackageRangeCheckDamageEntity
`write` IL=216, 39 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `damageStr` | u8 |
| 3 | `damageTyp` | u8 |
| 4 | `x` | f32 |
| 5 | `y` | f32 |
| 6 | `z` | f32 |
| 7 | `maxRangeSq` | f32 |
| 8 | `strength` | i16 |
| 9 | `bCritical` | bool |
| 10 | `attackerEntityId` | i32 |
| 11 | `dirX` | f32 |
| 12 | `dirY` | f32 |
| 13 | `dirZ` | f32 |
| 14 | `hitTransformName` | string |
| 15 | `x` | f32 |
| 16 | `y` | f32 |
| 17 | `z` | f32 |
| 18 | `uvHitx` | f32 |
| 19 | `uvHity` | f32 |
| 20 | `damageMultiplier` | f32 |
| 21 | `bIgnoreConsecutiveDamages` | bool |
| 22 | `bIsDamageTransfer` | bool |
| 23 | `bonusDamageType` | u8 |
| 24 | `particleName` | string |
| 25 | `x` | f32 |
| 26 | `y` | f32 |
| 27 | `z` | f32 |
| 28 | `x` | f32 |
| 29 | `y` | f32 |
| 30 | `z` | f32 |
| 31 | `particleLight` | f32 |
| 32 | `r` | f32 |
| 33 | `g` | f32 |
| 34 | `b` | f32 |
| 35 | `a` | f32 |
| 36 | `particleSound` | string |
| 37 | `buffActions` | u8 (list/array count) |
| 38 | `Item` | string |
| 39 | `buffActions` | u8 (list/array count) |

## NetPackageRegionMetaData
`write` IL=43, 5 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `X` | i32 |
| 2 | `Z` | i32 |
| 3 | `ChunksWithData` | i32 (list/array count) |
| 4 | `x` | i32 |
| 5 | `y` | i32 |

## NetPackageRequestToEnterGame
`write` IL=4, 0 wire field(s).

_No BinaryWriter/nested Write calls detected (empty body: only the base handle, or fully helper-delegated)._

## NetPackageRequestToSpawnEntity
`write` IL=9, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `ecd` | `EntityCreationData.write` |

## NetPackageRequestToSpawnPlayer
`write` IL=17, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `chunkViewDim` | i16 |
| 2 | `playerProfile` | `PlayerProfile.Write` |
| 3 | `nearEntityId` | i32 |

## NetPackageSetAttackTarget
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `m_targetId` | i32 |

## NetPackageSetBlock
`write` IL=37, 4 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `persistentPlayerId` | `PlatformUserIdentifierExtensions.ToStream` |
| 2 | `blockChanges` | i16 (list/array count) |
| 3 | `Item` | `BlockChangeInfo.Write` |
| 4 | `localPlayerThatChanged` | i32 |

## NetPackageSetBlockResponse
`write` IL=9, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `response` | u16 |

## NetPackageSetBlockTexture
`write` IL=24, 5 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `blockPos` | `StreamUtils.Write` |
| 2 | `blockFace` | u8 |
| 3 | `idx` | u8 |
| 4 | `playerIdThatChanged` | i32 |
| 5 | `channel` | u8 |

## NetPackageSetProp
`write` IL=37, 4 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `m_persistentPlayerId` | `PlatformUserIdentifierExtensions.ToStream` |
| 2 | `m_propChanges` | i16 (list/array count) |
| 3 | `Item` | `PropChangeInfo.Write` |
| 4 | `m_localPlayerThatChanged` | i32 |

## NetPackageSharedPartyKill
`write` IL=20, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityTypeID` | i32 |
| 2 | `xp` | i32 |
| 3 | `entityID` | i32 |
| 4 | `killerID` | i32 |

## NetPackageSharedQuest
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `sharedQuestData` | `SharedQuestData.write` |

## NetPackageShowToolbeltMessage
`write` IL=12, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `toolbeltMessage` | string |
| 2 | `sound` | string |

## NetPackageSignDataRequest
`write` IL=4, 0 wire field(s).

_No BinaryWriter/nested Write calls detected (empty body: only the base handle, or fully helper-delegated)._

## NetPackageSignDataResponse
`write` IL=28, 3 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `isLastBatch` | bool |
| 2 | `data` | i32 |
| 3 | `data` | bytes[] |

## NetPackageSimpleChat
`write` IL=44, 3 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `msg` | string |
| 2 | `recipientEntityIds` | i32 (list/array count) |
| 3 | `Item` | i32 (list/array count) |

## NetPackageSimpleRPC
`write` IL=12, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `type` | u8 |

## NetPackageSleeperPose
`write` IL=12, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `m_targetId` | i32 |
| 2 | `m_pose` | u8 |

## NetPackageSleeperWakeup
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `m_targetId` | i32 |

## NetPackageSoundAtPosition
`write` IL=25, 5 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `pos` | `StreamUtils.Write` |
| 2 | `audioClipName` | string |
| 3 | `mode` | u8 |
| 4 | `distance` | i32 |
| 5 | `entityId` | i32 |

## NetPackageTeleportPlayer
`write` IL=56, 8 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `x` | f32 |
| 2 | `y` | f32 |
| 3 | `z` | f32 |
| 4 | `HasValue` | bool |
| 5 | `x` | f32 |
| 6 | `y` | f32 |
| 7 | `z` | f32 |
| 8 | `onlyIfNotFlying` | bool |

## NetPackageTileEntity
`write` IL=23, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `handle` | u8 |
| 2 | `teWorldPos` | `StreamUtils.Write` |
| 3 | `ms` | u16 (list/array count) |

## NetPackageTraderData
`write` IL=38, 5 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | bool |
| 2 | `entityId` | i32 |
| 3 | `tePosition` | `StreamUtils.Write` |
| 4 | `traderData` | bool |
| 5 | `traderData` | `TraderData.Write` |

## NetPackageTreeFade
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |

## NetPackageTurretSpawn
`write` IL=24, 5 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityType` | i32 |
| 2 | `pos` | `StreamUtils.Write` |
| 3 | `rot` | `StreamUtils.Write` |
| 4 | `itemValue` | `ItemValue.Write` |
| 5 | `entityThatPlaced` | i32 |

## NetPackageTurretSync
`write` IL=20, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityId` | i32 |
| 2 | `targetEntityId` | i32 |
| 3 | `isOn` | bool |
| 4 | `itemValue` | `ItemValue.Write` |

## NetPackageTwitchAccess
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `hasAccess` | bool |

## NetPackageTwitchVoteScheduling
`write` IL=4, 0 wire field(s).

_No BinaryWriter/nested Write calls detected (empty body: only the base handle, or fully helper-delegated)._

## NetPackageVehicleCount
`write` IL=16, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `vehicleCount` | i32 |
| 2 | `turretCount` | i32 |
| 3 | `droneCount` | i32 |

## NetPackageVehicleDataSync
`write` IL=27, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `senderId` | i32 |
| 2 | `vehicleId` | i32 |
| 3 | `syncFlags` | u16 |
| 4 | `entityData` | u16 (list/array count) |

## NetPackageVehiclePositions
`write` IL=35, 3 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `positions` | i32 (list/array count) |
| 2 | `Item1` | i32 |
| 3 | `Item2` | `StreamUtils.Write` |

## NetPackageVehicleSpawn
`write` IL=24, 5 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `entityType` | i32 |
| 2 | `pos` | `StreamUtils.Write` |
| 3 | `rot` | `StreamUtils.Write` |
| 4 | `itemValue` | `ItemValue.Write` |
| 5 | `entityThatPlaced` | i32 |

## NetPackageWallVolume
`write` IL=12, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `id` | i32 |
| 2 | `wallVolume` | `WallVolume.Write` |

## NetPackageWallVolumeRemove
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `index` | i32 |

## NetPackageWaterSet
`write` IL=36, 3 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `senderEntityId` | i32 |
| 2 | `changes` | u16 (list/array count) |
| 3 | `Item` | `WaterSetInfo.Write` |

## NetPackageWaterSimChunkUpdate
`write` IL=15, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `sendLength` | i32 |
| 2 | `sendLength` | bytes[] |

## NetPackageWaypoint
`write` IL=17, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `waypoint` | `Waypoint.Write` |
| 2 | `inviteMode` | u8 |
| 3 | `inviterEntityId` | i32 |

## NetPackageWeather
`write` IL=53, 4 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `biomeId` | u8 |
| 2 | `groupIndex` | u8 |
| 3 | `remainingSeconds` | u8 |
| 4 | `param` | f32 |

## NetPackageWireActions
`write` IL=45, 5 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `currentOperation` | u8 |
| 2 | `tileEntityPosition` | `StreamUtils.Write` |
| 3 | `wireChildren` | u8 (list/array count) |
| 4 | `Item` | `StreamUtils.Write` |
| 5 | `wiringEntityID` | i32 (list/array count) |

## NetPackageWireToolActions
`write` IL=17, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `currentOperation` | u8 |
| 2 | `tileEntityPosition` | `StreamUtils.Write` |
| 3 | `entityID` | i32 |

## NetPackageWorldAreas
`write` IL=31, 3 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | u8 |
| 2 | `traders` | i16 (list/array count) |
| 3 | `Item` | `TraderArea.Write` |

## NetPackageWorldFolder
`write` IL=30, 4 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `seqNr` | i32 |
| 2 | `totalParts` | i32 |
| 3 | `data` | i32 |
| 4 | `data` | bytes[] |

## NetPackageWorldInfo
`write` IL=52, 11 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `gameMode` | string |
| 2 | `levelName` | string |
| 3 | `gameName` | string |
| 4 | `guid` | string |
| 5 | `ppList` | bool |
| 6 | `ppList` | `PersistentPlayerList.Write` |
| 7 | `ticks` | u64 |
| 8 | `fixedSizeCC` | bool |
| 9 | `firstTimeJoin` | bool |
| 10 | `-` | bytes[] |
| 11 | `-` | i64 |

## NetPackageWorldInitInfo
`write` IL=57, 5 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `eventPrefabs` | i32 (list/array count) |
| 2 | `Current` | `Serializable.Write` |
| 3 | `wallVolumes` | i32 (list/array count) |
| 4 | `Item2` | i32 |
| 5 | `-` | `WallVolume.Write` |

## NetPackageWorldInitInfoRequest
`write` IL=4, 0 wire field(s).

_No BinaryWriter/nested Write calls detected (empty body: only the base handle, or fully helper-delegated)._

## NetPackageWorldSpawnPoints
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `spawnPoints` | `SpawnPointList.Write` |

## NetPackageWorldTime
`write` IL=8, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `worldTime` | u64 |

---

# Nested serializers referenced by the packages above

## ActionTarget
`Write` IL=23, 3 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `Type` | u8 |
| 2 | `Position` | `StreamUtils.Write` |
| 3 | `BlockValueReference` | `BlockValueRef.Write` |

## AnimParamData
`Write` IL=31, 5 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `NameHash` | i32 |
| 2 | `ValueType` | u8 |
| 3 | `IntValue` | bool |
| 4 | `FloatValue` | f32 |
| 5 | `IntValue` | i32 |

## Bag
`Write` IL=71, 8 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | u8 |
| 2 | `-` | u16 |
| 3 | `-` | `ItemStack.Write` |
| 4 | `LockedSlots` | bool |
| 5 | `LockedSlots` | `PackedBoolArray.Write` |
| 6 | `Touched` | bool |
| 7 | `preferences` | bool |
| 8 | `preferences` | `PreferenceTracker.Write` |

## BiomeIntensity
`Write` IL=45, 8 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `biomeId0` | u8 |
| 2 | `intensity0` | u8 |
| 3 | `biomeId1` | u8 |
| 4 | `intensity1` | u8 |
| 5 | `biomeId2` | u8 |
| 6 | `intensity2` | u8 |
| 7 | `biomeId3` | u8 |
| 8 | `intensity3` | u8 |

## BlockChangeInfo
`Write` IL=89, 6 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `blockValueRef` | `BlockValueRef.Write` |
| 2 | `changedByEntityId` | i32 |
| 3 | `bChangeTexture` | u8 |
| 4 | `blockValue` | `BlockValue.Write` |
| 5 | `density` | i8 |
| 6 | `textureFull` | `TextureFullArray.Write` |

## EntityNetworkStats
`write` IL=104, 22 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `killed` | i32 |
| 2 | `holdingItemStack` | `ItemStack.Write` |
| 3 | `holdingItemIndex` | u8 |
| 4 | `deathHealth` | i32 |
| 5 | `teamNumber` | u8 |
| 6 | `attachedToEntityId` | i32 |
| 7 | `entityName` | string |
| 8 | `isPlayer` | bool |
| 9 | `killedZombies` | i32 |
| 10 | `killedPlayers` | i32 |
| 11 | `experience` | i32 |
| 12 | `level` | i32 |
| 13 | `totalItemsCrafted` | u32 |
| 14 | `distanceWalked` | f32 |
| 15 | `longestLife` | f32 |
| 16 | `currentLife` | f32 |
| 17 | `totalTimePlayed` | f32 |
| 18 | `vehiclePose` | i32 |
| 19 | `isSpectator` | bool |
| 20 | `hasProgression` | bool |
| 21 | `progressionsData` | i16 |
| 22 | `progressionsData` | bytes[] |

## EntityCreationData
`write` IL=358, 56 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | u8 |
| 2 | `entityClass` | i32 |
| 3 | `id` | i32 |
| 4 | `lifetime` | f32 |
| 5 | `x` | f32 |
| 6 | `y` | f32 |
| 7 | `z` | f32 |
| 8 | `x` | f32 |
| 9 | `y` | f32 |
| 10 | `z` | f32 |
| 11 | `onGround` | bool |
| 12 | `bodyDamage` | `BodyDamage.Write` |
| 13 | `stats` | bool |
| 14 | `stats` | `EntityStats.Write` |
| 15 | `deathTime` | i16 |
| 16 | `bag` | bool |
| 17 | `bag` | `Bag.Write` |
| 18 | `x` | i32 |
| 19 | `y` | i32 |
| 20 | `z` | i32 |
| 21 | `homeRange` | i16 |
| 22 | `spawnerSource` | u8 |
| 23 | `belongsPlayerId` | i32 |
| 24 | `clientEntityId` | i32 |
| 25 | `itemStack` | `ItemStack.Write` |
| 26 | `-` | i8 |
| 27 | `rawData` | u32 |
| 28 | `textureFullArrays` | `TextureFullArray.Write` |
| 29 | `blockValues` | i32 |
| 30 | `rawData` | u32 |
| 31 | `blockPositions` | `StreamUtils.Write` |
| 32 | `textureFullArrays` | `TextureFullArray.Write` |
| 33 | `blockPos` | `StreamUtils.Write` |
| 34 | `fallTreeDir` | `StreamUtils.Write` |
| 35 | `holdingItem` | `ItemValue.Write` |
| 36 | `teamNumber` | u8 |
| 37 | `entityName` | string |
| 38 | `skinTexture` | string |
| 39 | `playerProfile` | bool |
| 40 | `playerProfile` | `PlayerProfile.Write` |
| 41 | `entityData` | u16 (list/array count) |
| 42 | `entityData` | bytes[] |
| 43 | `traderData` | bool |
| 44 | `traderData` | `TraderData.Write` |
| 45 | `sleeperPose` | u8 |
| 46 | `isSleeper` | bool |
| 47 | `spawnById` | i32 |
| 48 | `spawnByName` | string |
| 49 | `spawnByAllowShare` | bool |
| 50 | `headState` | u8 |
| 51 | `overrideSize` | f32 |
| 52 | `overrideHeadSize` | f32 |
| 53 | `isDancing` | bool |
| 54 | `isSleeperPassive` | bool |
| 55 | `belongsPlayerId` | i32 |
| 56 | `orderState` | i32 |

## Equipment
`Write` IL=77, 6 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | u8 |
| 2 | `m_slots` | `ItemValue.Write` |
| 3 | `m_cosmeticSlots` | i32 |
| 4 | `Item` | i32 |
| 5 | `m_unlockedCosmetics` | i32 (list/array count) |
| 6 | `Item` | i32 |

## InventoryTransaction
`Write` IL=75, 7 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `InventoryOps` | i32 (list/array count) |
| 2 | `InventoryOps` | i32 (list/array count) |
| 3 | `Key` | `StreamUtils.Write` |
| 4 | `InitialHash` | i32 |
| 5 | `FinalHash` | i32 |
| 6 | `Ops` | i32 (list/array count) |
| 7 | `Current` | `InventoryOperation.Write` |

## ItemStack
`Write` IL=20, 2 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `count` | u16 |
| 2 | `itemValue` | `ItemValue.Write` |

## ItemValue
`Write` IL=10, 2 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | u8 |
| 2 | `-` | `ItemValue.Write` |

## QuestPacketEntry
`write` IL=21, 5 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `QuestID` | string |
| 2 | `QuestLocation` | `StreamUtils.Write` |
| 3 | `QuestSize` | `StreamUtils.Write` |
| 4 | `POIName` | string |
| 5 | `TraderPos` | `StreamUtils.Write` |

## SharedQuestData
`write` IL=63, 13 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `sharedByEntityID` | i32 |
| 2 | `questEvent` | u8 |
| 3 | `questCode` | i32 |
| 4 | `questID` | string |
| 5 | `poiName` | string |
| 6 | `position` | `StreamUtils.Write` |
| 7 | `size` | `StreamUtils.Write` |
| 8 | `returnPos` | `StreamUtils.Write` |
| 9 | `questGiverID` | i32 |
| 10 | `sharedWithEntityID` | i32 |
| 11 | `questCode` | i32 |
| 12 | `questCode` | i32 |
| 13 | `sharedWithEntityID` | i32 |

## WaterSetInfo
`Write` IL=9, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `worldPos` | `StreamUtils.Write` |
| 2 | `waterData` | `WaterValue.Write` |

## ParticleEffect
`Write` IL=47, 8 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `ParticleId` | i32 |
| 2 | `pos` | `StreamUtils.Write` |
| 3 | `rot` | `StreamUtils.Write` |
| 4 | `soundName` | string |
| 5 | `additionalHitSoundName` | string |
| 6 | `volumeScale` | f32 |
| 7 | `parentEntityId` | i32 |
| 8 | `attachment` | u8 |

## PersistentPlayerData
`Write` IL=205, 28 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `PrimaryId` | `PlatformUserIdentifierExtensions.ToStream` |
| 2 | `NativeId` | `PlatformUserIdentifierExtensions.ToStream` |
| 3 | `PlayGroup` | u8 |
| 4 | `AuthoredName` | `AuthoredText.ToStream` |
| 5 | `Ticks` | i64 |
| 6 | `x` | i32 |
| 7 | `y` | i32 |
| 8 | `z` | i32 |
| 9 | `EntityId` | i32 |
| 10 | `LPBlocks` | i32 (list/array count) |
| 11 | `backpacksByID` | i32 (list/array count) |
| 12 | `x` | i32 |
| 13 | `y` | i32 |
| 14 | `z` | i32 |
| 15 | `Key` | i32 (list/array count) |
| 16 | `x` | i32 |
| 17 | `y` | i32 |
| 18 | `z` | i32 |
| 19 | `Timestamp` | u32 |
| 20 | `x` | i32 |
| 21 | `y` | i32 |
| 22 | `z` | i32 |
| 23 | `QuestPositions` | i32 (list/array count) |
| 24 | `Current` | `QuestPositionData.Write` |
| 25 | `OwnedVendingMachinePositions` | i32 (list/array count) |
| 26 | `x` | i32 |
| 27 | `y` | i32 |
| 28 | `z` | i32 |

## PersistentPlayerList
`Write` IL=73, 8 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `Players` | i32 (list/array count) |
| 2 | `Value` | `PersistentPlayerData.Write` |
| 3 | `m_lpBlockMap` | i32 (list/array count) |
| 4 | `x` | i32 |
| 5 | `y` | i32 |
| 6 | `z` | i32 |
| 7 | `PrimaryId` | `PlatformUserIdentifierExtensions.ToStream` |
| 8 | `Allies` | `AllyStore.Write` |

## PlatformLobbyId
`Write` IL=12, 2 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `PlatformIdentifier` | u8 |
| 2 | `LobbyId` | string |

## PlatformUserIdentifierExtensions
`ToStream` IL=27, 1 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | `PlatformUserIdentifierExtensions.ToStream` |

## PlayerDataFile
`Write` IL=372, 53 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `ecd` | `EntityCreationData.write` |
| 2 | `selectedInventorySlot` | u8 |
| 3 | `bag` | `Bag.Write` |
| 4 | `alreadyCraftedList` | u16 (list/array count) |
| 5 | `Current` | string |
| 6 | `-` | u8 |
| 7 | `selectedSpawnPointKey` | i64 |
| 8 | `-` | bool |
| 9 | `-` | i16 |
| 10 | `bLoaded` | bool |
| 11 | `x` | i32 |
| 12 | `y` | i32 |
| 13 | `z` | i32 |
| 14 | `heading` | f32 |
| 15 | `id` | i32 |
| 16 | `playerKills` | i32 |
| 17 | `zombieKills` | i32 |
| 18 | `deaths` | i32 |
| 19 | `score` | i32 |
| 20 | `equipment` | `Equipment.Write` |
| 21 | `unlockedRecipeList` | u16 (list/array count) |
| 22 | `Current` | string |
| 23 | `-` | u16 |
| 24 | `markerPosition` | `StreamUtils.Write` |
| 25 | `markerHidden` | bool |
| 26 | `bCrouchedLocked` | bool |
| 27 | `craftingData` | `CraftingData.Write` |
| 28 | `favoriteRecipeList` | u16 (list/array count) |
| 29 | `Current` | string |
| 30 | `totalItemsCrafted` | u32 |
| 31 | `distanceWalked` | f32 |
| 32 | `longestLife` | f32 |
| 33 | `gameStageBornAtWorldTime` | u64 |
| 34 | `waypoints` | `WaypointCollection.Write` |
| 35 | `questJournal` | `QuestJournal.Write` |
| 36 | `deathUpdateTime` | i32 |
| 37 | `currentLife` | f32 |
| 38 | `bDead` | bool |
| 39 | `-` | u8 |
| 40 | `bModdedSaveGame` | bool |
| 41 | `challengeJournal` | `ChallengeJournal.Write` |
| 42 | `rentedVMPosition` | `StreamUtils.Write` |
| 43 | `rentalEndDay` | i32 |
| 44 | `progressionData` | i32 (list/array count) |
| 45 | `buffData` | i32 (list/array count) |
| 46 | `stealthData` | i32 (list/array count) |
| 47 | `favoriteCreativeStacks` | u16 (list/array count) |
| 48 | `Item` | u16 |
| 49 | `favoriteShapes` | u16 (list/array count) |
| 50 | `Item` | string |
| 51 | `ownedEntities` | u16 (list/array count) |
| 52 | `Item` | `OwnedEntityData.Write` |
| 53 | `totalTimePlayed` | f32 (list/array count) |

## PlayerProfile
`Write` IL=69, 11 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | i32 |
| 2 | `archetype` | string |
| 3 | `isMale` | bool |
| 4 | `raceName` | string |
| 5 | `variantNumber` | u8 |
| 6 | `hairName` | string |
| 7 | `hairColor` | string |
| 8 | `mustacheName` | string |
| 9 | `chopsName` | string |
| 10 | `beardName` | string |
| 11 | `eyeColor` | string |

## Serializable
`Write` IL=17, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `id` | i32 |
| 2 | `prefabName` | string |
| 3 | `position` | `StreamUtils.Write` |
| 4 | `rotation` | u8 |

## PrefabVolumeAbs
`Write` IL=13, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `Used` | bool |
| 2 | `startPos` | `StreamUtils.Write` |
| 3 | `size` | `StreamUtils.Write` |

## PropChangeInfo
`Write` IL=107, 9 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `x` | i32 |
| 2 | `y` | i32 |
| 3 | `HasValue` | u8 |
| 4 | `Value` | i32 |
| 5 | `Value` | `StreamUtils.Write` |
| 6 | `Value` | `StreamUtils.Write` |
| 7 | `Value` | `StreamUtils.Write` |
| 8 | `rawData` | u32 |
| 9 | `damage` | u16 |

## QuestPositionData
`Write` IL=13, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `questCode` | i32 |
| 2 | `positionDataType` | i32 |
| 3 | `blockPosition` | `StreamUtils.Write` |

## SpawnPointList
`Write` IL=25, 3 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | u8 |
| 2 | `-` | i32 (list/array count) |
| 3 | `Item` | `SpawnPoint.Write` |

## StreamUtils
`Write` IL=71, 0 wire field(s).

_No BinaryWriter/nested Write calls detected (empty body: only the base handle, or fully helper-delegated)._

## TraderArea
`Write` IL=111, 16 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `x` | i32 |
| 2 | `y` | i32 |
| 3 | `z` | i32 |
| 4 | `x` | i16 |
| 5 | `y` | i16 |
| 6 | `z` | i16 |
| 7 | `x` | i8 |
| 8 | `y` | i8 |
| 9 | `z` | i8 |
| 10 | `TeleportVolumes` | u8 (list/array count) |
| 11 | `x` | i8 |
| 12 | `y` | i8 |
| 13 | `z` | i8 |
| 14 | `x` | u8 |
| 15 | `y` | u8 |
| 16 | `z` | u8 |

## TraderData
`Write` IL=15, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `TraderID` | i32 |
| 2 | `lastInventoryUpdate` | u64 |
| 3 | `-` | u8 |

## KeyHashPair
`Write` IL=9, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `Key` | `StreamUtils.Write` |
| 2 | `Hash` | i32 |

## VersionInformation
`Write` IL=18, 4 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `ReleaseType` | u8 |
| 2 | `Major` | i32 |
| 3 | `Minor` | i32 |
| 4 | `Build` | i32 |

## WallVolume
`Write` IL=34, 7 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | u8 |
| 2 | `x` | i32 |
| 3 | `y` | i32 |
| 4 | `z` | i32 |
| 5 | `x` | i32 |
| 6 | `y` | i32 |
| 7 | `z` | i32 |

## Waypoint
`Write` IL=57, 13 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `pos` | `StreamUtils.Write` |
| 2 | `icon` | string |
| 3 | `icon` | string |
| 4 | `name` | `AuthoredText.ToStream` |
| 5 | `bTracked` | bool |
| 6 | `hiddenOnCompass` | bool |
| 7 | `ownerId` | `PlatformUserIdentifierExtensions.ToStream` |
| 8 | `lastKnownPositionEntityId` | i32 |
| 9 | `bIsAutoWaypoint` | bool |
| 10 | `bUsingLocalizationId` | bool |
| 11 | `inviterEntityId` | i32 |
| 12 | `hiddenOnMap` | bool |
| 13 | `lastKnownPositionEntityType` | i32 |

## BlockValueRef
`Write` IL=23, 3 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `Type` | u8 |
| 2 | `BlockPosition` | `StreamUtils.Write` |
| 3 | `PropReference` | `PropRef.Write` |

## PackedBoolArray
`Write` IL=16, 0 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

_No BinaryWriter/nested Write calls detected (empty body: only the base handle, or fully helper-delegated)._

## PreferenceTracker
`Write` IL=65, 4 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `PlayerID` | i32 |
| 2 | `toolbelt` | bool |
| 3 | `equipment` | bool |
| 4 | `bag` | bool |

## BlockValue
`Write` IL=10, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `rawData` | u32 |
| 2 | `damage` | u16 |

## TextureFullArray
`Write` IL=22, 1 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `FixedElementField` | i64 |

## BodyDamage
`Write` IL=12, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | i32 |
| 2 | `damageType` | i32 |
| 3 | `Flags` | u32 |

## EntityStats
`Write` IL=8, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | i32 |
| 2 | `Health` | `Stat.Write` |

## InventoryOperation
`Write` IL=29, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `Operation` | i16 |
| 2 | `Stack` | `ItemStack.Write` |
| 3 | `Index` | i32 |

## WaterValue
`Write` IL=5, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `mass` | u16 |

## AuthoredText
`ToStream` IL=22, 4 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | u8 |
| 2 | `-` | u8 |
| 3 | `Text` | string |
| 4 | `Author` | `PlatformUserIdentifierExtensions.ToStream` |

## AllyStore
`Write` IL=101, 4 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `Current` | i32 |
| 2 | `Key` | `PlatformUserIdentifierExtensions.ToStream` |
| 3 | `Key` | `PlatformUserIdentifierExtensions.ToStream` |
| 4 | `Value` | u8 |

## CraftingData
`Write` IL=39, 3 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | u16 |
| 2 | `RecipeQueueItems` | u8 |
| 3 | `RecipeQueueItems` | `RecipeQueueItem.Write` |

## WaypointCollection
`Write` IL=61, 3 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | u8 |
| 2 | `list` | u16 (list/array count) |
| 3 | `Item` | `Waypoint.Write` |

## QuestJournal
`Write` IL=138, 11 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | u8 |
| 2 | `TraderPOIs` | u8 (list/array count) |
| 3 | `Item` | `StreamUtils.Write` |
| 4 | `TradersByFaction` | u8 (list/array count) |
| 5 | `Current` | i32 |
| 6 | `Item` | i32 (list/array count) |
| 7 | `Item` | `StreamUtils.Write` |
| 8 | `quests` | u16 (list/array count) |
| 9 | `Item` | `Quest.Write` |
| 10 | `TraderData` | u8 (list/array count) |
| 11 | `Item` | `QuestTraderData.Write` |

## ChallengeJournal
`Write` IL=103, 7 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | u8 |
| 2 | `Challenges` | i32 (list/array count) |
| 3 | `Item` | `Challenge.Write` |
| 4 | `ChallengeGroups` | i32 (list/array count) |
| 5 | `Name` | string |
| 6 | `LastUpdateDay` | i32 |
| 7 | `ChallengeGroups` | string (list/array count) |

## OwnedEntityData
`Write` IL=37, 6 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `Id` | i32 |
| 2 | `ClassId` | i32 |
| 3 | `saveFlags` | u16 |
| 4 | `x` | i32 |
| 5 | `y` | i32 |
| 6 | `z` | i32 |

## SpawnPoint
`Write` IL=13, 3 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `spawnPosition` | `SpawnPosition.Write` |
| 2 | `team` | i32 |
| 3 | `activeInGameMode` | i32 |

## PropRef
`Write` IL=9, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `ChunkPos` | `StreamUtils.Write` |
| 2 | `PropId` | i32 |

## Stat
`Write` IL=24, 6 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | i32 |
| 2 | `m_value` | f32 |
| 3 | `m_maxModifier` | f32 |
| 4 | `m_baseMax` | f32 |
| 5 | `m_originalBaseMax` | f32 |
| 6 | `m_originalValue` | f32 |

## RecipeQueueItem
`Write` IL=82, 12 wire field(s).

> Control-flow: conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | u16 |
| 2 | `Multiplier` | i16 |
| 3 | `IsCrafting` | bool |
| 4 | `CraftingTimeLeft` | f32 |
| 5 | `RepairItem` | bool |
| 6 | `RepairItem` | `ItemValue.Write` |
| 7 | `AmountToRepair` | u16 |
| 8 | `Quality` | u8 |
| 9 | `StartingEntityId` | i32 |
| 10 | `OneItemCraftTime` | f32 |
| 11 | `Recipe` | bool |
| 12 | `Recipe` | `Recipe.Write` |

## Quest
`Write` IL=186, 22 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `ID` | string |
| 2 | `CurrentQuestVersion` | u8 |
| 3 | `-` | u8 |
| 4 | `CurrentState` | u8 |
| 5 | `SharedOwnerID` | i32 |
| 6 | `QuestGiverID` | i32 |
| 7 | `Tracked` | bool |
| 8 | `CurrentPhase` | u8 |
| 9 | `QuestCode` | i32 |
| 10 | `Item` | `BaseObjective.Write` |
| 11 | `DataVariables` | u8 (list/array count) |
| 12 | `Key` | string |
| 13 | `Value` | string |
| 14 | `PositionData` | u8 (list/array count) |
| 15 | `Key` | u8 |
| 16 | `Value` | `StreamUtils.Write` |
| 17 | `RallyMarkerActivated` | bool |
| 18 | `FinishTime` | u64 |
| 19 | `Rewards` | i32 (list/array count) |
| 20 | `Item` | `BaseReward.Write` |
| 21 | `QuestFaction` | u8 (list/array count) |
| 22 | `QuestProgressDay` | i32 |

## QuestTraderData
`Write` IL=85, 8 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `TraderPOI` | `StreamUtils.Write` |
| 2 | `CompletedPOIByTier` | u8 (list/array count) |
| 3 | `Current` | u8 |
| 4 | `Item` | i32 (list/array count) |
| 5 | `Item` | `StreamUtils.Write` |
| 6 | `TradersSentTo` | u8 (list/array count) |
| 7 | `Item` | `StreamUtils.Write` |
| 8 | `resetDay` | i32 (list/array count) |

## Challenge
`Write` IL=43, 6 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | u8 |
| 2 | `Name` | string |
| 3 | `ChallengeState` | u8 |
| 4 | `AutoCompleted` | bool |
| 5 | `-` | u8 |
| 6 | `ObjectiveList` | i32 (list/array count) |

## SpawnPosition
`Write` IL=23, 5 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | u16 |
| 2 | `x` | f32 |
| 3 | `y` | f32 |
| 4 | `z` | f32 |
| 5 | `heading` | f32 |

## Recipe
`Write` IL=56, 9 wire field(s).

> Control-flow: loop(s) present (count-prefixed list/array); conditional branch(es) present. Flat sequence below is the backbone.

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `Version` | u16 |
| 2 | `itemValueType` | i32 |
| 3 | `count` | i32 |
| 4 | `IsScrap` | bool |
| 5 | `craftingTime` | f32 |
| 6 | `craftExpGain` | i32 |
| 7 | `craftingArea` | string |
| 8 | `ingredients` | i32 (list/array count) |
| 9 | `Item` | `ItemStack.Write` |

## BaseObjective
`Write` IL=8, 2 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `-` | u8 |
| 2 | `CurrentValue` | u8 |

## BaseReward
`Write` IL=5, 1 wire field(s).

| # | Source (field/getter) | Wire |
|---:|---|---|
| 1 | `RewardIndex` | u8 |

