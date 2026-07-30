# Wire package body catalog (V3.0.1, IL-derived)

**Owns:** per-`NetPackage` wire metadata (channel/compress/direction/auth) and
hand-annotated `read`/`write` byte layouts beyond the join-critical set in
[`protocol.md`](protocol.md).
**Not:** framing/join/challenge (that is [`protocol.md`](protocol.md)); visual
frames ([`protocol-frames.md`](protocol-frames.md)).
**Evidence:** dumped from the live `Assembly-CSharp.dll` with
[`../tools/`](../tools) (`DumpNetPackages`, `NetProtocolCensus`, `DumpType`);
raw output `il/netpackages-v3.0.1/` (git-ignored). Every field below traces to a
specific `BinaryWriter::Write`/`BinaryReader::Read` in the method body.
**Method:** [`re-methodology.md`](re-methodology.md) §4-5.

All widths little-endian. `string` = .NET 7-bit length prefix + UTF-8. `bool` =
1 byte. Length-prefixed `byte[]` = `Int32` length then bytes (`Read(buf,0,len)`).

---

## 1. Protocol-wide metadata census

Full table: `il/netpackages-v3.0.1/META.md` (193 packages). Regenerate with
`mono bin/NetProtocolCensus.exe "$ASM" ../il/netpackages-v3.0.1/META.md`.

**Per-package wire bodies:** this doc hand-annotates the load-bearing packages; the
**complete** ordered `write()` field sequence for every package (183 bodies + 61
nested serializers) is auto-extracted in
[`inventories/netpackage-bodies.md`](inventories/netpackage-bodies.md)
(`tools/src/WireBodies`).

### 1.1 Channels (correction to the "channel 0 only" assumption)

Most packages inherit the base **channel 0**. Exactly **6 override to
channel 1** (the bulk / terrain / map band):

| Channel-1 package | Role |
|---|---|
| `NetPackageChunk` | full chunk terrain push |
| `NetPackageChunkRemove` | chunk unload |
| `NetPackageMapChunks` | compressed map (minimap) tiles |
| `NetPackageDynamicMesh` | dynamic mesh (destroyed-block geometry) |
| `NetPackagePOIAround` | POI/prefab region data |
| `NetPackageWorldFolder` | world-folder file transfer |

`protocol.md` previously said game packages use channel 0 and treated other
channels as "later". Channel 1 is the real second band and it carries the
heaviest bodies. A clone must bind/route both channels.

### 1.2 Compressed packages

**8 packages set `get_Compress = 1`** (payload LZ-compressed regardless of the
envelope bot path): `NetPackageChunk`, `NetPackageMapChunks`,
`NetPackageDynamicMesh`, `NetPackagePOIAround`, `NetPackageConfigFile`,
`NetPackageDynamicClientArrive`, `NetPackageIdMapping`,
`NetPackageSignDataResponse`. So bulk terrain/map/config is compressed on the
wire even though the join handshake packets are not. This nuances
[`protocol.md`](protocol.md) §8 ("bots use uncompressed path"): true for the
join set, false for these bulk packages.

### 1.3 Direction tally

`NetPackageDirection`: `0 = Both`, `1 = ToServer`, `2 = ToClient`.
Of 193 packages: **66 ToClient, 33 ToServer, 7 Both (explicit), 87 inherit**
(base default = Both).

### 1.4 Pre-auth surface (`AllowedBeforeAuth = 1`)

Exactly **10 packages** may cross the wire before authentication. This is the
complete attack/handshake surface a server must accept pre-auth:

`NetPackagePackageIds`, `NetPackagePlayerLogin`, `NetPackagePlayerDenied`,
`NetPackageAuthConfirmation`, `NetPackageAuthState`, `NetPackageEAC`,
`NetPackageEncryptionRequest`, `NetPackageEncryptionPublicKey`,
`NetPackageEncryptionSharedKey`, `NetPackageKeyExchangeComplete`.

---

## 2. Encryption handshake (closes the `residuals.md` "encryption wire path")

All four packages are `AllowedBeforeAuth`. This is a public-key agreement that
establishes a symmetric session key + separate integrity key.

```mermaid
sequenceDiagram
  participant S as Server
  participant C as Client
  S->>C: NetPackageEncryptionRequest (empty)
  C->>S: NetPackageEncryptionPublicKey (params XML + hash + signed hash)
  Note over S,C: server verifies signature, derives shared secret
  S->>C: NetPackageEncryptionSharedKey (EncryptionKey, IntegrityKey)
  C->>S: NetPackageKeyExchangeComplete (wasSuccessful)
```

Bodies (from `write`):

**NetPackageEncryptionRequest** - empty body (id only). Server -> client trigger.

**NetPackageEncryptionPublicKey**
```text
ExchangePublicKeyParamsXml : string    // .NET public-key params as XML
Hash        : i32 len + byte[len]      // length-prefixed
SignedHash  : i32 len + byte[len]      // signature over Hash
```

**NetPackageEncryptionSharedKey**
```text
EncryptionKey : i32 len + byte[len]    // symmetric session key material
IntegrityKey  : i32 len + byte[len]    // separate MAC/integrity key
```

**NetPackageKeyExchangeComplete**
```text
wasSuccessful : bool
```

Failure is surfaced through `EKickReason` (see §6): `EncryptionFailure(19)`,
`EncryptionAgreementInvalidSignature(33)`, `EncryptionAgreementError(34)`. The
signed-hash + separate integrity-key shape indicates signature-verified key
agreement followed by authenticated symmetric encryption; the exact cipher and
KDF are in native/crypto library calls, not the package bodies (residual).

---

## 3. Terrain / chunk band (channel 1)

### 3.1 NetPackageChunk (ToClient, channel 1, compressed)

`write` order:
```text
bOverwriteExisting : bool
if bOverwriteExisting:
    chunkX : i16    // conv.i2 from Chunk.X
    chunkY : i16    // Chunk.Y
    chunkZ : i16    // Chunk.Z
dataLen : i32       // == serializedData.Length
data    : dataLen bytes   // Chunk.write() blob (same codec as save), then StreamCopy
```
The `data` blob is produced in `Setup()` by `Chunk::write(PooledBinaryWriter)`
into a pooled `serializedData` stream, so the chunk-serialization codec is shared
with the save path ([`save-region.md`](save-region.md)). `GetLength` = 14 +
serializedData.Length. `ProcessPackage` either overwrites an existing chunk
(unload -> reset -> re-read -> re-add) or adds a new chunk and flags
`NeedsRegeneration`.

### 3.2 NetPackageChunkRemove (ToClient, channel 1)
```text
chunkKey : i64      // WorldChunkCache key (packed x,z)
```


### 3.3 NetPackageMapChunks (ToClient, channel 1, compressed)

Minimap color tiles, not terrain. Produced by
`IMapChunkDatabase.GetMapChunkPackagesToSend` and appended in
`SendChunksToClients` when the observer has a `mapDatabase`
([world-chunks.md](world-chunks.md) section 4.0).

**Metadata:** channel **1**, `Compress=true`, direction **ToClient** (2).

**`write` order (IL=109):**
```text
entityId     : i32
count        : u16   // number of map pieces that will follow
// per piece (only pieces whose UInt16[] length == 256 are written):
  chunkDbKey : i32   // IMapChunkDatabase.ToChunkDBKey
  colors     : u16 x 256
```

If any piece has length != 256, the writer logs a warning, decrements the planned
count, and **rewinds** the stream to rewrite the `u16` count after the loop
(so a bad piece is omitted without leaving a stale count).

**`GetLength` (IL=24):** `4 + 8*chunkCount + 512*pieceCount` (entityId +
per-chunk key+pad estimate + 256 u16 colors). Not an exact wire length after
invalid-piece filtering.

**`Setup(entityId, List<int> chunks, List<ushort[]> mapPieces)`** copies both
lists.

**`ProcessPackage` (client, IL=26):** resolve `entityId` to `EntityPlayer`; if
that player has `ChunkObserver.mapDatabase`, call
`mapDatabase.Add(chunks, mapPieces)`.

**Producer (`MapChunkDatabase.GetMapChunkPackagesToSend`, IL=96):**

1. No-op (`null`) unless `bClientMapMiddlePositionUpdated` (set by map-position
   C2S path); then clear the flag.
2. Clear send lists. Convert `clientMapMiddlePosition` via `toChunkXZ`.
3. Scan a **17x17** window: offsets `dx,dz in [-8..+8]` (literal radius **8**).
4. For each key not yet in `chunksSent` and present in the fixed datastore:
   add db key + `UInt16[256]` colors; mark sent.
5. If any queued, `NetPackageMapChunks.Setup(playerId, toSendList, mapPiecesList)`.

`MapChunkDatabaseByRegion` (IL=123) is the same window under `m_regionsLock`,
looking up region+offset storage instead of the fixed DS.

**Related C2S:** `NetPackageMapPosition` (direction ToServer) carries
`entityId` + `mapMiddlePosition` and drives the middle-position update that
arms the next map send.


---

## 4. World state band

### 4.1 NetPackageWorldTime (ToClient)
```text
worldTime : u64
```

### 4.2 NetPackageWorldInfo (join world descriptor)
`write` order:
```text
gameMode   : string
levelName  : string
gameName   : string
guid       : string
ppList present : bool
ppList     : PersistentPlayerList.Write (if present)
ticks      : u64
fixedSizeCC: bool
firstTimeJoin : bool
worldHashes : i32 count + count x { filename:string, hash:u32 }  // NOT a byte-length blob
worldDataSize   : i64
```

The leading `i32` on `worldHashes` is an **entry count**, not a byte length: the
`read` IL parses `count` then a `{ string filename, u32 hash }` pair per entry into
a `Dictionary<string,uint>`, then `worldDataSize:i64`. (The `write` side emits the
already-serialized dictionary bytes via `BinaryWriter.Write(byte[])`, but the count
prefix is inside that blob, so on the wire it reads as count + entries.) A clone that
treats the `i32` as a byte length desyncs the stream and misparses `worldDataSize`.

### 4.3 NetPackageWorldInitInfo (ToClient)
`write` order (both lists are count-prefixed; verified against `write` IL=57 /
`read` IL=58):
```text
eventPrefabs count : i32
  per entry        : PrefabInstance.Serializable.Write   // repeated count times
wallVolumes  count : i32
  per entry        : i32 (tuple Item1) + WallVolume.Write // repeated count times
```
There is **no separate trailing `dataLength`** (an earlier note listed one; the
read side reads only the two counts and their entries). `PrefabInstance.Serializable`
and `WallVolume` own their own field layout (dump locally with `tools/src/DumpType`).
The request form `NetPackageWorldInitInfoRequest` has an empty body (`write` IL=4).

---

## 5. Entity + gameplay band

### 5.0 NetPackageRequestToSpawnEntity (ToServer)

Client-authored spawn request (vehicle/turret/item place, falling tree, etc.).

```text
// body is only:
EntityCreationData.write(_bw, networkWrite=true)   // same codec as 5.1
```

- Direction **ToServer** (1). Channel base **0**.
- `Setup` stores `ecd`; `ProcessPackage` calls
  `IGameManager.RequestToSpawnEntityServer(ecd)` when world non-null.

**`GameManager.RequestToSpawnEntityServer` (IL=101):**

1. If **not** server: re-wrap as this package and `SendToServer` (host client
   path).
2. If `entityClass` hash equals `"fallingTree"`: scan live entities for an
   existing `EntityFallingTree` at the same `blockPos`; **return without spawn**
   if found (dedupe).
3. `EntityFactory.CreateEntity(ecd)`.
4. If result is `EntityBackpack`: find matching `PersistentPlayerData` by
   `RefPlayerId`, `AddDroppedBackpack(entityId, pos, worldMinutes)`.
5. `World.SpawnEntityInWorld(entity)` (registers + NetEntityDistribution tracks;
   clients later get `NetPackageEntitySpawn` via interest).

This is the **C2S place/create** path. The S2C visual/create for remote clients
is still `NetPackageEntitySpawn` (5.1), not a direct echo of this package.

### 5.1 NetPackageEntitySpawn (ToClient)
Body is a single `EntityCreationData.write(writer, networkWrite=true)`. The body is
**three ordered sections**: an unconditional header, an `entityClass`-switched
middle, and a convergence tail. The middle switch is the part a clone gets wrong
most easily (verified against the `write` IL branch structure, not the flat
catalog).

**(1) Unconditional header (every entity, ends at `spawnerSource`):**
```text
readFileVersion : byte
entityClass     : i32
id              : i32
lifetime        : f32
pos.x, pos.y, pos.z : f32 x3
rot.x, rot.y, rot.z : f32 x3
onGround        : bool
BodyDamage.Write
stats present   : bool  (+ EntityStats.Write if present)
deathTime       : i16
bag present     : bool  (+ Bag.Write if present)
homePosition.x,y,z : i32 x3
homeRange       : i16
spawnerSource   : byte   // EnumSpawnerSource 0..4  <- header ENDS here
```

**(2) `entityClass`-switched middle (mutually exclusive; a plain zombie/NPC/animal
writes NONE of these).** The switch compares `entityClass` (an int, the
`EntityClass.list` hash) against static class ids:

| If `entityClass ==` | Writes | Note |
|---|---|---|
| `EntityClass.itemClass` | `belongsPlayerId:i32`, `clientEntityId:i32`, `itemStack.Write`, `sbyte(0)` | dropped-item entity, then **jumps straight to the tail** (skips all rows below) |
| `EntityClass.fallingBlockClass` | `blockValues[0].rawData:u32`, `textureFullArrays[0].Write` | single falling block |
| `EntityClass.fallingBlocksClass` | `blockValues.Length:i32`, then `count x rawData:u32`, then `count x Vector3i`, then `count x TextureFullArray` | multi-block, see the shared-count note below |
| `EntityClass.fallingTreeClass` | `blockPos:Vector3i` (`StreamUtils.Write`), `fallTreeDir:Vector3` (`StreamUtils.Write`) | falling tree |
| `EntityClass.playerMaleClass` or `playerFemaleClass` | `holdingItem` (`ItemValue.Write`), `teamNumber:u8`, `entityName:string`, `skinTexture:string`, `playerProfile` present:`bool` (+ `PlayerProfile.Write`) | player character |
| anything else (zombie, animal, NPC, vehicle, ...) | nothing | goes straight to the tail |

**Shared-count trap (fallingBlocks).** The multi-block branch writes **one**
`i32` length and then **three** arrays: `blockValues` (`u32` each),
`blockPositions` (`Vector3i` = 3x `i32` each), and `textureFullArrays`
(`TextureFullArray.Write` = exactly one `i64` each, its loop bound is the literal
1). No second length is emitted, and `EntityCreationData.read` allocates all three
arrays from that same value without reading another `Int32`. A clone must treat the
three arrays as the same length; writing a length before the positions or textures
desyncs the stream. The single-block `fallingBlockClass` branch has no count at all:
it is just `rawData:u32` then one `i64`.

**(3) Convergence tail (every entity):**
```text
entityData    : u16 length + bytes[]     // serialized extra blob (usually empty)
traderData present : bool  (+ TraderData.Write)
if networkWrite:                          // true for NetPackageEntitySpawn
    sleeperPose : byte
    isSleeper   : bool
    spawnById   : i32
    spawnByName : string
    spawnByAllowShare : bool
    headState   : byte
    overrideSize / overrideHeadSize : f32 x2
    isDancing   : bool
    if isSleeper:                         // ONLY when isSleeper is true
        isSleeperPassive : bool
// the junk-drone extras are OUTSIDE the networkWrite guard:
if entityClass == EntityClass.junkDroneClass:
    belongsPlayerId : i32
    orderState      : i32
```

Two gating details a clone must honour (both cost stream sync if missed):
`isSleeperPassive` is written **only when `isSleeper` is true** (`brfalse` at
IL_03B2 skips it), and the trailing `belongsPlayerId` + `orderState` pair is
**junk-drone-only and sits after the `networkWrite` block**, not inside it (the
`networkWrite` guard at IL_033F jumps to the same junk-drone test at IL_03C5).
Writing `isSleeperPassive` unconditionally adds a phantom byte to every non-sleeper
spawn; writing `belongsPlayerId` for every entity adds four, and omitting
`orderState` truncates drone spawns.

So `belongsPlayerId`/`clientEntityId`/`itemStack` are **item-entity fields, not
header fields**; a zombie spawn writes header + tail with the middle empty. The flat
per-write sequence in
[`inventories/netpackage-bodies.md`](inventories/netpackage-bodies.md) is the union
of all branches; use the switch above for the real per-class body. (Cross-checked
against the [zdtd](../../zdtd/docs/) clone's zombie spawn, which correctly writes the
empty middle.)

### 5.1.1 Wire envelope and client process

`NetPackageEntitySpawn` extends `NetPackageEntityTargeted`:

```text
// NetPackageEntityTargeted.write then ECD:
entityId : i32     // Setup copies EntityCreationData.id
// then EntityCreationData.write(_bw, networkWrite=true)  // full body in 5.1
```

- Direction **ToClient** (2). Channel inherits base **0** (not channel 1).
- `Setup(EntityCreationData)`: `NetPackageEntityTargeted.Setup(es.id)` + store `es`.
- Sole Setup caller: `NetEntityDistributionEntry.getSpawnPacket` (entity
  replication first-seen path).

**`ProcessPackage` (IL=60):**

1. No-op if world null.
2. If **not** server and `es.clientEntityId != 0`: for each local player whose
   `entityId == es.belongsPlayerId`, call
   `World.ChangeClientEntityIdToServer(clientEntityId, es.id)` and **return**
   (id remap only; no second create).
3. Else: `world.entityAsyncManager.StartCreateEntity(es, callback)` (async
   factory; callback owned by a display-class closure).

So S2C spawn is **async create**, not a synchronous `EntityFactory.CreateEntity`
on the package thread. The ECD body layout remains the clone-critical surface
(section 5.1 header/middle/tail).

### 5.2 NetPackageEntitySpawnResponse (ToServer)
```text
success   : bool
itemValue : ItemValue.Read/Write
```

**Client `ProcessPackage` (IL=153)** (local player only): tags the item as
`vehicle` / `drone` / `turretRanged|turretMelee`. On **success**: clear the
matching `ItemActionSpawnVehicle` / `ItemActionSpawnTurret` preview when the
holding item matches, `Inventory.DecItem` by 1, play `placeblock`. On
**failure**: tooltip `uiCannotAddVehicle` / `uiCannotAddDrone` /
`uiCannotAddTurret`. Server authority for the place still lives on the
placement / `RequestToSpawnEntity` path; this package is the client inventory
ack.

### 5.3 NetPackageHoldingItem (ToClient)
```text
entityId         : i32
holdingItemStack : ItemStack.Write
holdingItemIndex : byte
```

### 5.4 NetPackagePlayerInventory
```text
toolbelt present : bool  (+ ItemStack[] count-prefixed if present)
bag present      : bool  (+ Bag.Write if present)
equipment present: bool  (+ Equipment: slot count i32 + unlockedCosmetics list ...)
dragAndDropItem  : ItemStack.Write
```


### 5.5 Entity motion package family (ToClient / Both)

Selection thresholds live in [network.md](network.md) section 2 (encoded
`EncodePos` space). Inheritance:

```text
NetPackageEntityTargeted
  NetPackageEntityPosAndRot          // absolute float pos/rot
    NetPackageEntityTeleport         // same wire; different ProcessPackage
  NetPackageEntityRotation           // encoded rot or quaternion
    NetPackageEntityRelPosAndRot     // rotation + i16 dPos + onGround + steps
  NetPackageEntityVelocity           // bAdd + motion f32x3
  NetPackageEntityAliveFlags         // u16 bitfield
```

#### 5.5.1 `NetPackageEntityPosAndRot` (write IL=76)

```text
entityId : i32          // EntityTargeted
pos.x,y,z : f32 x3      // absolute world position
bUseQRotation : bool
if !bUseQRotation:
  rot.x,y,z : f32 x3    // euler degrees
else:
  qrot.x,y,z,w : f32 x4
onGround : bool
```

`Setup(Entity)` copies `position`, `rotation`, `qrotation`, `onGround`,
`IsQRotationUsed()`.

`ProcessPackage` (IL=61): `ValidEntityIdForSender`; skip if attached main entity
is local primary player; set `entity.serverPos = EncodePos(pos)`;
`SetPosAndRotFromNetwork` / `SetPosAndQRotFromNetwork` with **3** update steps;
set `onGround`.

#### 5.5.2 `NetPackageEntityTeleport` (extends PosAndRot)

- **No own `write`**: inherits PosAndRot body (`Setup` calls base Setup).
- `GetLength` returns literal **20** (hint only; actual length follows PosAndRot).
- `ProcessPackage` (IL=60): same id checks; `serverPos = EncodePos(pos)`;
  `SetPosAndRotFromNetwork(pos, rot, steps=0)`; then hard
  `SetPosition(pos,true)`, `SetRotation(rot)`, `SetLastTickPos(pos)`,
  `onGround`. Missing entity logs `Discarding ... for entity Id=`.

Use for large encoded jumps (±256+); client snaps rather than interpolates.

#### 5.5.3 `NetPackageEntityRotation` (write IL=54)

```text
entityId : i32
bUseQRotation : bool
if !bUseQRotation:
  rot.x,y,z : i16 x3    // EncodeRot units (rot*256/360)
else:
  qrot.x,y,z,w : f32 x4
```

#### 5.5.4 `NetPackageEntityRelPosAndRot` (write IL=30)

Extends Rotation write, then:

```text
// after Rotation body:
dPos.x,y,z : i16 x3     // encoded delta (1/32 block)
onGround : bool
updateSteps : i16
```

`ProcessPackage` (IL=94): `serverPos += dPos`; world pos = `serverPos / 32`;
decode rot as `(rot_i * 360) / 256`; apply with `updateSteps` via
`SetPosAndRotFromNetwork` / Q variant; set `onGround`. Same attached-primary skip.

#### 5.5.5 `NetPackageEntityVelocity` (write IL=23)

```text
entityId : i32
bAdd : bool
motion.x,y,z : f32 x3   // Setup clamps each axis to [-8, 8]
```

#### 5.5.6 `NetPackageEntityAliveFlags` (write IL=8)

```text
entityId : i32
flags : u16
```

Bit packing from `Setup` (IL=91), OR into flags:

| Bit | Value | Source |
|---:|---:|---|
| 2 | 4 | `AimingGun` |
| 3 | 8 | `Spawned` |
| 4 | 16 | `Jumping` |
| 5 | 32 | `IsBreakingBlocks` |
| 6 | 64 | `IsAlert` |
| 7 | 128 | inventory flashlight on |
| 8 | 256 | `IsGodMode` |
| 9 | 512 | `IsCrouching` |

### 5.6 `NetPackagePlayerData` (ToServer)

Periodic client save of local player blob (not the join ECD).

```text
// body:
PlayerDataFile.WriteNetwork(writer)   // full player file network codec
```

- Direction **ToServer** (1).
- `Setup(EntityPlayer)`: `new PlayerDataFile().FromPlayer(player)`.
- `ProcessPackage`: `ValidEntityIdForSender(playerDataFile.id)`; then
  `GameManager.SavePlayerData(Sender, playerDataFile)`.

Disk layout of `PlayerDataFile` (`ttp\0` + version **59**) is in
[save-region.md](save-region.md) section 1.3; this package is the C2S transport
only (`WriteNetwork` = `Write` + `PlayerMetaInfo`).


---

## 6. Building band

### 6.1 NetPackageSetBlock (ToServer/ToClient)
```text
persistentPlayerId present : bool (=0 in golden) (+ PlatformUserIdentifierAbs if 1)
blockChanges count : i16
blockChanges[count] : BlockChangeInfo.Write each
localPlayerThatChanged : i32
```

**BlockChangeInfo.Write** order:
```text
BlockValueRef.Write          // packed world block position + ref
changedByEntityId : i32
flags : byte                 // bit-packed: bChangeBlockValue, bChangeDensity,
                             //   bForceDensity, bUpdateLight, bChangeDamage, bChangeTexture
if bChangeBlockValue: BlockValue.Write
if bChangeDensity:    density : sbyte
if bChangeTexture:    TextureFullArray.Write
```

### 6.2 NetPackageSetBlockResponse (ToClient)
```text
response : u16    // eSetBlockResponse: 0 Success, 1 PowerBlockLimitExceeded,
                  //                    2 StorageBlockLimitExceeded
```

---

### 6.9 NetPackageWaterSimChunkUpdate (ToClient)

Jobified water sim stream ([light-mesh-water.md](light-mesh-water.md) section 4).
Direction **ToClient** (2).

**Outer wire (`write` IL=15):**
```text
sendLength : i32
sendBytes  : sendLength bytes   // prebuilt payload
```

**Inner payload** (built by Setup/AddChange/Finalize, then copied to `sendBytes`):
```text
chunkX : i32
chunkZ : i32
count  : i32                    // rewritten in FinalizeSend at lengthStreamPos
// count times:
  voxelIndex : u16              // local packed index
  mass       : u16              // WaterValue.Write = mass only
```

Pipeline:

1. `SetupForSend(Chunk)`: pool stream+writer; write X/Z; reserve count=0.
2. `AddChange(u16, WaterValue)`: write index + mass; `numVoxelUpdates++`.
3. `FinalizeSend`: seek to count slot, write `numVoxelUpdates`; copy stream to
   pooled `sendBytes`; free writer/stream.
4. `ProcessPackage` (client): read X/Z/count from pooled stream; for each entry
   `changeApplier.GetChangeWriter(key).RecordChange(index, WaterValue)`.

### 6.10 NetPackageWaterSet

Manual/console multi-cell set (not the continuous sim stream).

```text
senderEntityId : i32
count          : u16
// count times WaterSetInfo:
  worldPos     : Vector3i (via WaterSetInfo.Write)
  waterData    : WaterValue (mass u16)
```

**`ProcessPackage` (IL=29):** if server, rebroadcast package with bulk flags
**192** excluding sender (`SendPackage` entity exclude = senderEntityId); then
`ApplyChanges(ChunkCache)`: delayed regen start, per cell
`ChunkCluster.SetWater` + `World.HandleWaterLevelChanged`, delayed regen stop.

---

### 6.11 NetPackageDamageEntity

Authoritative damage event for clients (and some C2S external paths). Full field
order also in [protocol.md](protocol.md) section 6.5; re-verified against
`write` IL=172.

```text
entityId : i32
damageSrc : u8          // EnumDamageSource
damageTyp : u8          // EnumDamageTypes
strength : u16
hitDirection : u8
hitBodyPart : i16
movementState : u8
bPainHit, bFatal, bCritical : bool x3
attackerEntityId : i32
dirV : f32 x3
blockPos : Vector3i
hitTransformName : string
hitTransformPosition : f32 x3
uvHit : f32 x2
damageMultiplier : f32
random : f32
bIgnoreConsecutiveDamages, bIsDamageTransfer : bool x2
bDismember, bCrippleLegs, bTurnIntoCrawler : bool x3
bonusDamageType : u8
StunType : u8
StunDuration : f32
bFromBuff : bool
ArmorSlot : u8
ArmorSlotGroup : u8
ArmorDamage : u16
attackingItem present : bool (+ ItemValue.Write if true)
```

`Setup(targetId, DamageResponse)` (IL=141) flattens `DamageResponse` + nested
`DamageSource` into those fields. `ProcessPackage` (IL=168): rebuild
`DamageSource`/`DamageResponse`, `FireAttackedEvents`, `ProcessDamageResponse`
on the target entity (apply path owned by [combat-damage.md](combat-damage.md)).

### 6.12 NetPackageTileEntity

Live TE replication (not the chunk-blob type+body list).

```text
handle : u8             // Setup default 255 when omitted
teWorldPos : Vector3i
payloadLen : u16
payload : payloadLen bytes   // TileEntity.write(network stream mode)
```

`Setup(te, streamMode[, handle])` (IL=27): `te.ToWorldPos()`, write TE into pooled
stream via `TileEntity.write(writer, streamMode)`.

`ProcessPackage` (IL=90):

1. `World.GetTileEntity(teWorldPos)`; no-op if missing.
2. `SetHandle(handle)`.
3. Under lock on package stream: `te.read(reader, StreamModeRead)` with mode
   **2** if not remote world else **1**.
4. `NotifyListeners()`.
5. If server: `SetChunkModified()`; rebroadcast `NetPackageTileEntity.Setup(te,
   StreamModeWrite=2, handle)` with bulk flags **192** and optional world-center
   position for interest.

Base TE network write omits disk-only heat-map time; see
[tile-entities-power.md](tile-entities-power.md) section 2.

### 6.13 Inventory transaction packages

Server-authoritative container moves ([items.md](items.md)).

#### Request (ToServer)

```text
// body:
InventoryTransaction.Write(tx)
```

`ProcessPackage` (IL=8): `InventoryManager.TransactionRequestServer(tx, Sender.entityId)`.

**`InventoryTransaction.Write` (IL=75):**

```text
inventoryCount : i32
// per inventory:
  inventoryKey : Guid
  initialHash : i32
  finalHash : i32
  opCount : i32
  // opCount x InventoryOperation.Write
```

**`TransactionRequestServer` (IL=46):** must be server; `tx.Apply(secretToken)`;
on success `ValidateFinalHashes`; on failure log + `LockManager.ForceUnlockByPlayer`;
on success for non-primary player send `NetPackageInventoryTransactionResponse`
(flags 192) with success=true and null inventory lists (minimal ack).

#### Response (ToClient)

```text
// empty keys/inventories fast path:
success=false implied path: bool false, count 0
// full:
success : bool
count : i32
// count times:
  key : Guid
  hasStacks : bool
  if hasStacks: ItemStack.WriteArray
```

Client `ProcessPackage` is currently a no-op (`ret` IL=1) on this build; server
still emits the ack for remote players.

#### Data request / response (related)

`NetPackageInventoryDataRequest`: `KeyHashPair` + `managerToken` Guid.
`NetPackageInventoryDataResponse`: success, errorMsg, inventoryKey Guid,
`ItemStack[]`, managerToken; client updates `TransactionalInventory` on success.

### 6.14 NetPackageExplosionInitiate (ToServer)

Client/server-placed explosives. `ProcessPackage` → `IGameManager.ExplosionServer(...)`.

```text
worldPos : Vector3          // StreamUtils
blockPos : Vector3i
rotation : Quaternion       // StreamUtils
explosionBlobLen : u16
explosionBlob : bytes       // ExplosionData.ToByteArray()
entityId : i32
delay : f32
bRemoveBlockAtExplPosition : bool
item present : bool (+ ItemValue.Write)
```

Also summarized in [protocol.md](protocol.md) section 6.6.

### 6.15 NetPackageExplosionClient (ToClient)

Authoritative blast FX + block change list for clients.

```text
center : Vector3
rotation : Quaternion
expType : i16
blastPower : u16
blastRadius : u16
blockDamage : u16
entityId : i32
changeCount : u16
// changeCount x BlockChangeInfo.Write
```

`ProcessPackage` → `IGameManager.ExplosionClient(...)`.

### 6.16 Stat / buff sync packages

#### `NetPackageEntityStatChanged` (extends EntityTargeted)

```text
entityId : i32
instigatorId : i32
enumStat : u8
value : f32
baseMax : f32
maxModifier : f32
```

`ProcessPackage`: apply to `Stat` via `GetStat`; optional MinEvent on health;
server re-sends to tracked players via `NetEntityDistribution`.

#### `NetPackageEntityStatsBuff`

```text
entityId : i32
dataLen : i32
data : dataLen bytes     // EntityBuffs.Write / Read blob
```

`Setup` can serialize live buffs if data null. Client remote entities apply
`EntityBuffs.Read`; server rebroadcasts (flags 192, exclude self).

#### `NetPackagePlayerStats` (extends EntityTargeted)

```text
entityId : i32
EntityNetworkStats.write(...)
```

`Setup` fills `EntityNetworkStats` from entity. Server may stamp sender player
name, `ToEntity` + `EnqueueNetworkStats`, rebroadcast excluding sender (192).

### 6.17 Social / admin / lock / quest spawn packages

Cross-links to family docs; wire verified this pass.

#### `NetPackageChat`

```text
chatType : u8
senderEntityId : i32
msg : string
msgSender : u8
bbMode : u8
recipientCount : i32
// recipientCount x i32 entity ids
```

Server `ProcessPackage` → `ChatMessageServer`; client → `ChatMessageClient`.
Routing is recipient-list based ([chat.md](chat.md)).

#### `NetPackageConsoleCmdServer` / `Client`

See [console-commands.md](console-commands.md) section 3: server carries a single
`cmd` string; client carries `lineCount` strings + `bExecute`.

#### `NetPackageLockRequest` / `Response`

See [dedicated-leftovers.md](dedicated-leftovers.md) section 2.2: locking bool,
channel u16, target identifying infos, context type name + body.

#### `NetPackagePartyActions` / `PartyData`

Already in [parties-factions.md](parties-factions.md) section 3. Re-verified:
Actions write is `op:u8, invitedBy:i32, invited:i32, voiceLobbyId:string` (no
member array). Data write includes member id array.

#### `NetPackageQuestEntitySpawn` (ToServer)

```text
entityType : i32          // -1 means resolve from gamestageGroup
gamestageGroup : string
entityIDQuestHolder : i32
```

`ProcessPackage`: if `entityType == -1`, resolve random class from
`GameStageDefinition` using quest holder's `PartyGameStage`; then
`QuestActionSpawnEnemy.SpawnQuestEntity(type, holderId, null)`.

## 7. Reference enums (IL constants)

**NetPackageDirection:** 0 Both, 1 ToServer, 2 ToClient.

**eSetBlockResponse:** 0 Success, 1 PowerBlockLimitExceeded,
2 StorageBlockLimitExceeded.

**EnumSpawnerSource:** 0 Unknown, 1 Biome, 2 StaticSpawner, 3 Dynamic, 4 Delete.

**EKickReason** (35 values; deny reasons in `NetPackagePlayerDenied`). Notable:
4 VersionMismatch, 5 PlayerLimitExceeded, 6 Banned, 7 NotOnWhitelist,
11 EacViolation, 18 UnknownNetPackage, 19 EncryptionFailure,
10 ManualKick (also used for platform-blocked enter), 26 BadMTUPackets (ConnectionManager bad-packet threshold 3/s),
31 PersistentPlayerDataExceeded (PPL cap 100 on RequestToEnterGame),
33 EncryptionAgreementInvalidSignature, 34 EncryptionAgreementError. Full list in
`il/netpackages-v3.0.1/` enum dump.

**NetPackagePlayerDenied** body (`KickPlayerData`):
```text
reason          : i32   // EKickReason
apiResponseEnum : i32
banUntil        : i64   // DateTime ticks
customReason    : string
```

---

## 8. Still open (honest)

| Item | State |
|---|---|
| `EntityCreationData` class-conditional tail | fully extracted (56 fields, per-class branches) in [inventories/netpackage-bodies.md](inventories/netpackage-bodies.md) + §5.1 table |
| Bulk-package compression codec (LZ variant) | flag known; byte codec in native/StreamUtils (residual) |
| Encryption cipher/KDF | handshake bodies decoded; crypto primitives native (residual) |
| Quest/Party/Twitch families | not yet annotated (low priority) |
| `NetPackageDynamicMesh`, `POIAround` bodies | channel/compress known; bodies not annotated |

---

## Related docs

| Doc | Role |
|---|---|
| [protocol.md](protocol.md) | Framing, challenge, join, golden motion bodies |
| [protocol-frames.md](protocol-frames.md) | Visual byte frames |
| [re-methodology.md](re-methodology.md) | How these were derived |
| [network.md](network.md) | Interest / replication / bands |
| [residuals.md](residuals.md) | Non-IL residuals |
| [../tools/README.md](../tools/README.md) | Dumpers that generated this |

## Changelog

- **2026-07-28:** Chat/console/lock/quest-spawn package wire summaries; party re-verify.

- **2026-07-28:** Inventory transaction wire + server apply; explosion initiate/client; stat/buff/playerstats packages.

- **2026-07-28:** NetPackageDamageEntity full wire; NetPackageTileEntity handle/pos/payload + server rebroadcast.

- **2026-07-28:** Entity motion family (PosAndRot/Teleport/Rel/Rot/Velocity/AliveFlags); PlayerData C2S.

- **2026-07-28:** RequestToSpawnEntity server create; WaterSimChunkUpdate inner payload; WaterSet rebroadcast.

- **2026-07-28:** MapChunks + EntitySpawn process paths.
