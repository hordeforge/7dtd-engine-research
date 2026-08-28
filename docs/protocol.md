# Dedicated wire protocol (V3.2.0 pin; V3.1.0/V3.0.1-era goldens still cited)

**Current game pin:** V **3.2.0 (b9)**. Framing/join and most package bodies are stable from the V3.0.1 corpus; the TE outer wire and PackageIds VersionInformation (minor=20 build=9) are in [protocol-packages.md](protocol-packages.md). Loadgen dual fixtures cover both heads.


**Owns:** LiteNet framing, pre-auth challenge, PackageIds, join sequence, post-login enter-game package batch, `NetPackageRequestToSpawnPlayer` / RequestToSpawnPlayer/PlayerId/PlayerSpawnedInWorld, golden package body layouts.  
**Not:** the exhaustive per-package body catalog + protocol-wide metadata census (that is [`protocol-packages.md`](protocol-packages.md)); LiteNet event dispatch internals (closed 2026-08-10, [network.md](network.md) §4.0); EAC wire (residual).  
**Hub:** [INDEX.md](INDEX.md).  
**Visual frames (RFC bars + Mermaid):** [`protocol-frames.md`](protocol-frames.md).  
**Full package bodies + census (channels, compress, pre-auth, encryption handshake):** [`protocol-packages.md`](protocol-packages.md).  
**Clone use:** [ZIG_CLONE.md](../../zdtd-server/docs/ZIG_CLONE.md) · implementation [`../../zdtd-server/`](../../zdtd-server).  
**Replication policy:** [network.md](network.md).  
**Evidence:** `7dtd-loadgen` `PackageCodec.cs` / `JoinStateMachine.cs` / `GameJoinClient.cs` (live joins); `il/dedi-complete-v3.2.0/` NetPackage census; ConnectionManager dumps.

**Endianness:** little-endian (BinaryWriter / .NET). Strings: length-prefixed UTF-8 as .NET `BinaryWriter.Write(string)`.

> **Byte diagrams:** every golden package has an offset table + Mermaid field strip in  
> **[protocol-frames.md](protocol-frames.md)** (challenge, envelope, PackageIds, Login, PosAndRot, RelPos, AliveFlags, DamageEntity, …).

---

## 1. Ports and transport

| Item | Observed / stock |
|---|---|
| Game / Steam “connect” port | Often **ServerPort** (e.g. 26900) |
| LiteNetLib data port | **ServerPort + 2** (e.g. **26902**) on this install |
| Transport | UDP via **LiteNetLib** |
| Delivery for game pkgs | Reliable ordered (loadgen uses delivery **2**) |
| Password | serverconfig; encryption packages exist (path incomplete) |
| EAC | Off for bots and C# mods; `NetPackageEAC` residual |

Loadgen and RealEarth docs use 26902 for bots. Clone should bind the LiteNet listen port clients actually dial.

```mermaid
flowchart LR
  CLI[Stock client / loadgen]
  UDP[UDP LiteNet]
  CH[Challenge 0xCA]
  GP[Game packages channel 0]
  CLI --> UDP --> CH --> GP
```

---

## 2. Pre-auth challenge

Before normal packages, server sends **raw** 17 bytes (not the channel envelope).  
**Frame diagram:** [protocol-frames.md §1](protocol-frames.md#1-challenge-raw-before-game-envelope).

```text
[0]    = 0xCA   // PackageCodec.ChallengeChannelMarker = 202
[1..16] = Guid  // 16 bytes
```

Client **echoes** the same 17 bytes. Constants: `ChallengeSize = 17`.

---

## 3. Game message envelope (after challenge)

**Frame diagram:** [protocol-frames.md §2](protocol-frames.md#2-game-channel-envelope--package-stream).

From `NetConnectionSimple` / `NetworkServerLiteNetLib` RE (loadgen comments + golden assert):

```text
LiteNetLib payload (reservedHeaderBytes = 1):

offset 0: channel:u8              // game channel 0 for most packages
offset 1: payloadSize:i32         // bytes after this envelope header
offset 5: compressed:u8           // 0 = uncompressed path used by bots
offset 6: encrypted:u8            // 0 when unencrypted
offset 7: pkgCount:u16            // number of inner packages
offset 9: payload begins
  for each package:
    contentLen:i32                // size of (pkgId + body) ONLY
    pkgId:u16
    body: contentLen-2 bytes
```

**Rule:** `contentLen = 2 + body.Length` (excludes the contentLen field).  
Stock write: `length = end - start - 4` in WriteToStream.

Outer size check:

```text
framed.Length == 1 + 8 + payloadSize
```

Constants:

| Name | Value |
|---|---:|
| ReservedHeaderBytes | 1 |
| OuterEnvelopeAfterChannel | 8 |
| Uncompressed / unencrypted | 0 / 0 |

### Live capture head (PackageIds, channel 0)

Hex prefix validated in loadgen golden (V3.0.1-era capture; V3.1.0 re-captured
in-session 2026-08-11 - only the version triple differs). The 3.2.0 b9
PackageIds head was not re-captured live this cycle; by the same packing the
version triple is minor=20 (0x14) build=9 (0x09), everything else identical:

```text
V3.1.0 live:  00 BC 12 00 00  00 00  01 00  B8 12 00 00  00 00  01 03 00 00 00  0A 00 00 00  0E 00 00 00  BD 00 00 00  14 ...
V3.0.1 era:  00 BC 12 00 00  00 00  01 00  B8 12 00 00  00 00  01 03 00 00 00  01 00 00 00  04 00 00 00  BD 00 00 00  ...
ch payload=0x12BC  c e  cnt=1  content=0x12B8  pkgId=0
version (V3.1.0): release=1 major=3 minor=10 build=14
version (V3.0.1): release=1 major=3 minor=1 build=4
map count: 0xBD = 189   first name: len 0x14 "NetPackagePackageIds"
```

Display version packing: `VersionLongString` → **`V 3.2.0`** for Minor=20 Build=9 (see loadgen; Constants.cVersion*).

---

## 4. Dynamic package ID map

`NetPackageManager` maps **type name string → u16 id** at runtime.

Server → client: **`NetPackagePackageIds`** body:

```text
Version (release:u8, major:i32, minor:i32, build:i32)
count:i32
count × string  // type names in id order (index = id)
serverUseEac:bool
hasHostUserAndToken:bool (+ optional platform user blobs)
```

Client must use **server-advertised** ids for all later packages. Do not hard-code ids across game versions.

DLL census (V3.0.1, `tools/bin/Census.exe`): **194** `NetPackage*`-prefixed types =
**193 + `NetPackageManager`** (the registry). The **189** in the live id-map are the
actual registered wire packages; the remaining ~4-6 of the 193 are name-prefixed
helpers (`NetPackageDirection` [enum], `Logger`, `Metrics`, ...), not wire packages.

### Family counts (census)

| Family | Approx count |
|---|---:|
| Entity* | 32 |
| Player* | 16 |
| Quest/Party* | 12 |
| Chunk* | 8 |
| World/Tile* | 9 |
| Auth/Crypto* | 6 |
| Inventory* | 5 |
| Other | ~106 |

Largest maxIL (complexity signal, not wire size): Metrics, SharedQuest, QuestEvent, QuestGotoPoint, WireToolActions, PartyData, RangeCheckDamageEntity, GameEventRequest, TurretSpawn, Audio, DynamicMesh, …

Full name list: `il/dedi-complete-v3.2.0/DEDI_COMPLETE_auto.md` §3.

---

## 5. Join sequence (server responsibilities)

```mermaid
stateDiagram-v2
  [*] --> AcceptLiteNet
  AcceptLiteNet --> SendChallenge
  SendChallenge --> WaitEcho
  WaitEcho --> SendPackageIds
  SendPackageIds --> WaitLogin
  WaitLogin --> Auth: PlayerLogin
  Auth --> Answer: PlayerLoginAnswer allowed
  Auth --> Deny: PlayerDenied
  Answer --> AssignId: PlayerId / spawn data
  AssignId --> WaitSpawnReq
  WaitSpawnReq --> Spawn: RequestToSpawnPlayer
  Spawn --> InWorld: PlayerSpawnedInWorld + chunks
  InWorld --> InWorld: entity + chunk stream
```

Client stages (loadgen enum):  
`UdpOpen → LiteNetConnected → ChallengeReceived → ChallengeReplied → PackageIdsReceived → LoginSent → LoginAnswered → PlayerIdReceived → SpawnedInWorld → Joined`.

### Login body (PlayerLogin)

```text
playerName:string
platformUser + token   // PlatformUserIdentifier stream
crossplatform user + token
versionLong:string     // e.g. "V 3.0.1"
compVersionLong:string
discordUserId:u64
```

Platform user stream (loadgen): `0` if null; else `1,1,platform:string,id:string`.

### RequestToSpawnPlayer

```text
chunkViewDim:i16
PlayerProfile v5:
  version:i32 = 5
  archetype:string
  isMale:bool
  race:string
  variant:u8
  hair, hairColor, mustache, chops, beard, eyeColor: strings
nearEntityId:i32
```

### Empty bodies

| Package | Body |
|---|---|
| AuthConfirmation | empty (id only) |
| RequestToEnterGame | empty |

### Post-login: `RequestToEnterGame` server sequence (IL=248)

Client sends empty `NetPackageRequestToEnterGame` after accepting
`PlayerLoginAnswer`. Server entry is a thin coroutine wrapper
(`GameManager.RequestToEnterGame` IL=9 -> `MoveNext` IL=**248**). Ordered work
(verified call sequence):

1. `ModEvents` `SPlayerJoinedGameData` (mod hook).
2. Yield `PlatformUserManager.ResolveUserBlockedCoroutine` for the player.
3. If platform-blocked: `NetPackagePlayerDenied` with
   `EKickReason.ManualKick` (**10**), empty custom reason; stop.
4. If `persistentPlayerCount + 1 > **100**`: `PlayerDenied` with
   `EKickReason.PersistentPlayerDataExceeded` (**31**); stop.
5. `PersistentPlayerList.NetworkCloneRelevantForPlayer`.
6. Two `NetPackageIdMapping` sends (`"blocks"`, `"items"` string keys + byte maps).
7. Yield `NetPackageLocalization.StartSendingPacketsToClient`.
8. `WorldStaticData.SendXmlsToClient` (config S2C; [mod-loading.md](mod-loading.md) section 5.6).
9. `NetPackageWorldInfo` (world name/seed/guid + relevant PPL + time bits).
10. `NetPackageChunkClusterInfo` for the primary `ChunkCluster`
    (`ProcessPackage` IL=13 -> `GameManager.ChunkClusterInfo`).
11. `NetPackageWorldSpawnPoints` (`GameManager.GetSpawnPointList`).
12. `NetPackageWorldAreas` (`World.TraderAreas`).
13. `NetPackageGameStats` (`GameStats.Instance`).

After this batch the client proceeds to `RequestToSpawnPlayer` / in-world
streaming (state machine above). Auth terminal steps that precede this request
are in [platform-auth.md](platform-auth.md) section 3 (`playerAllowed`).

```mermaid
flowchart TD
  PLA[PlayerLoginAnswer allowed] --> RTEG[RequestToEnterGame empty]
  RTEG --> Block{platform blocked?}
  Block -->|yes| Deny1[PlayerDenied ManualKick=10]
  Block -->|no| Cap{PPL count > 100?}
  Cap -->|yes| Deny2[PlayerDenied PersistentPlayerDataExceeded=31]
  Cap -->|no| Maps[IdMapping blocks+items]
  Maps --> Loc[Localization packets]
  Loc --> Xml[SendXmlsToClient]
  Xml --> WI[WorldInfo]
  WI --> CC[ChunkClusterInfo]
  CC --> SP[SpawnPoints]
  SP --> Areas[WorldAreas traders]
  Areas --> GS[GameStats]
  GS --> SpawnReq[RequestToSpawnPlayer]
```

### `PlayerLoginAnswer` body (server write, IL=46)

| Order | Field |
|---|---|
| 1 | base package header |
| 2 | `bAllowed` : bool |
| 3 | `data` : string (`LocalServerInfo.ToString()` when allowed) |
| 4 | `platformLobbyId` : `PlatformLobbyId.Write` |
| 5 | platform user : `PlatformUserIdentifier.ToStream` + ticket string |
| 6 | crossplatform user : same |

On the client, `ProcessPackage` calls `ConnectionManager.PlayerAllowed(...)` when
`bAllowed`, else `PlayerDenied(data)`.

### Post-spawn request: `RequestToSpawnPlayer` (server, IL=496)

Client sends after the enter-game batch. Package process is a thin forwarder to
`GameManager.RequestToSpawnPlayer(cInfo, chunkViewDim, playerProfile, nearEntityId)`.

**Wire (C2S):**

| Order | Field |
|---|---|
| 1 | base header |
| 2 | `chunkViewDim` : i16 |
| 3 | `PlayerProfile.Write` (v5 layout, see above) |
| 4 | `nearEntityId` : i32 |

**Server work (verified):**

1. Clamp `chunkViewDim` to `[max(4, pref190), min(12, pref190)]` where pref190 is
   `GamePrefs.GetInt(190)` itself clamped to 4..12, then clamp the client value into that range.
2. `PlayerDataFile.Load` under `getPersistentPlayerID` / `CombinedString`; clear
   `lastSpawnPosition` to `Undef`.
3. Entity id: reuse `PlayerDataFile.id` if loaded and not `-1` and free; else
   allocate `EntityFactory.nextEntityID` (and reallocate if that id is already live).
4. Spawn position selection (first success wins):
   - If `GameStats` bool **25** (`IsSpawnNearOtherPlayer`): for each player with
     `TeamNumber == 0`, try `FindRandomSpawnPointNearPlayer(..., radius 15, ...)`.
     The IL's `teamNumber` local is written exactly once with **0**, so the scan
     matches unteamed players only (the joining team is not restored here;
     `NetPackagePlayerId.Setup` also passes team **0**).
   - Else if `nearEntityId != -1` and spawn-near-friend mode != 0:
     up to 15 tries of `GetRandomSpawnPositionMinMaxToPosition` (min **40**, max **150**,
     land-claim aware); mode **2** (`AllowSpawnNearFriend.InForest`) keeps the
     candidate only when the biome is `BiomeType` **2..3 = Forest / PineForest**
     (other biomes rejected).
   - Else if still undef: `SpawnPointList.GetRandomSpawnPosition`.
5. Build `EntityCreationData` (class from profile, id, team, pos/rot); copy saved
   `entityData` stream when `bLoaded`.
6. `EntityFactory.CreateEntity` -> `EntityPlayer`; `isEntityRemote = true`.
7. `Respawn(EnterMultiplayer=4)` if new file, else `Respawn(JoinMultiplayer=5)`.
8. `PlayerDataFile.ToPlayer`.
9. Persistent player: get or `CreatePlayerData` / `Update`, set `LastLogin` +
   `EntityId`, `MapPlayer`, `SavePersistentPlayerData`.
10. `ConnectionManager.SetClientEntityId` + **`NetPackagePlayerId`** to the client
    (`id`, `teamNumber` i16, `PlayerDataFile.WriteNetwork`, `chunkViewDim`).
11. `AIDirectorAirDropComponent.RefreshCrates(entityId)`.
12. `World.SpawnEntityInWorld(player)`.
13. `ChunkManager.AddChunkObserver(pos, false, chunkViewDim, entityId)` on the player.
14. `IMapChunkDatabase.TryCreateOrLoad` for the player's map DB.
15. `DispatchPlayerEvent` + broadcast `NetPackagePersistentPlayerState` (reason **0** new / **1** update).
16. `ModEvents.PlayerSpawning` (`SPlayerSpawningData`).

**Note:** `GameManager.PlayerSpawnedInWorld` is **not** called from this method.
Chunk terrain for the new observer is **not** sent inside this method either:
steady `UpdateTick` -> `SendChunksToClients` streams `NetPackageChunk` on channel 1
([world-chunks.md](world-chunks.md) section 4.0).
It runs later when the client (or local controller) sends
`NetPackagePlayerSpawnedInWorld` (server validates `ValidEntityIdForSender`,
runs `PlayerSpawnedInWorld`, rebroadcasts the package).

```mermaid
flowchart TD
  Req[RequestToSpawnPlayer] --> Load[PlayerDataFile.Load]
  Load --> Id[allocate or reuse entity id]
  Id --> Pos[spawn position selection]
  Pos --> Create[CreateEntity EntityPlayer remote]
  Create --> Respawn[Respawn Enter/Join Multiplayer]
  Respawn --> ToP[PlayerDataFile.ToPlayer]
  ToP --> PPL[PersistentPlayerList map/save]
  PPL --> Pid[NetPackagePlayerId]
  Pid --> World[SpawnEntityInWorld]
  World --> Obs[AddChunkObserver + map DB]
  Obs --> Hook[ModEvents.PlayerSpawning]
  Hook --> Later[later: PlayerSpawnedInWorld package]
```

### `NetPackagePlayerId` body (S2C write, IL=21)

| Order | Field |
|---|---|
| 1 | base header |
| 2 | `id` : i32 |
| 3 | `teamNumber` : i16 |
| 4 | `PlayerDataFile.WriteNetwork` |
| 5 | `chunkViewDim` : i32 |

Client `ProcessPackage` -> `GameManager.PlayerId(...)`.

### `NetPackagePlayerSpawnedInWorld` body (IL=16)

| Order | Field |
|---|---|
| 1 | base header |
| 2 | `respawnReason` : i32 (`RespawnType`) |
| 3 | `position` : `Vector3i` via `StreamUtils.Write` |
| 4 | `entityId` : i32 |

`RespawnType`: 0 NewGame, 1 LoadedGame, 2 Died, 3 Teleport, 4 EnterMultiplayer,
5 JoinMultiplayer, 6 Unknown.

Server `PlayerSpawnedInWorld` (IL=127): require live `EntityPlayer`; on
`Died`+remote call `SetAlive`; join/enter multiplayer may
`DisplayGameMessage`; `PlayerInteractions.PlayerSpawnedInMultiplayerServer`;
on server for join/enter/new/loaded paths refresh vehicle/drone waypoints and
`SpawnFollowingDronesForPLayer`; fire `ModEvents.PlayerSpawnedInWorld`;
`OnClientSpawned` action; log.

---

## 6. Entity motion packages (golden sizes)

**Visual layouts (RFC + Mermaid):** [protocol-frames.md §7-§12](protocol-frames.md#7-entityposandrot-body-buseq--30-bytes).

### 6.1 NetPackageEntityPosAndRot (!bUseQRotation)

| Field | Type |
|---|---|
| entityId | i32 |
| x,y,z | f32 ×3 |
| bUseQRotation | bool = false |
| rotX,Y,Z | f32 ×3 |
| onGround | bool |

**Body size = 30** bytes.

### 6.2 NetPackageEntityRelPosAndRot (!bUseQ)

Inherits targeted + rotation branch:

| Field | Type | Notes |
|---|---|---|
| entityId | i32 | |
| bUseQRotation | bool false | if true: 4×f32 quat instead of rot i16 |
| rotX,Y,Z | i16 ×3 | packed: deg/360×256 clamped 0..255 |
| dx,dy,dz | i16 ×3 | relative position |
| onGround | bool | |
| updateSteps | i16 | |

**Body size = 20**; contentLen with pkgId = **22**.  
When bUseQ=true, body = **30**.

Stock selection thresholds (server outbound): [network.md](network.md) §2.

### 6.3 NetPackageEntityAliveFlags

| Field | Type |
|---|---|
| entityId | i32 |
| flags | u16 |

**Body size = 6.**

Flag bits (literals from live DLL, loadgen):

| Bit | Name |
|---:|---|
| 1 | ApproachingEnemy |
| 2 | ApproachingPlayer |
| 4 | AimingGun |
| 8 | Spawned |
| 16 | Jumping |
| 32 | BreakingBlocks |
| 64 | IsAlert |
| 128 | FlashlightOn |
| 256 | GodMode |
| 512 | Crouching |

### 6.4 NetPackageEntityLookAt

```text
entityId:i32
lookX,Y,Z:i32   // floats cast to int on write
```

### 6.5 NetPackageDamageEntity (write order)

Used for suicide / drown / external kill bots. Order from IL (V3.2.0 b9,
`write` IL=144; the V3.1.0 layout wrote ten separate booleans and a
`bIsDamageTransfer` field that no longer exists):

```text
entityId:i32
flags:u32          // packed bitfield, see below (V3.2.0 new; replaces 10 bools)
damageSource:u8      // 0 External, 1 Internal
damageType:u8        // 3 Bashing, 16 Suffocation, 26 Suicide, …
strength:u16
hitDirection:u8
hitBodyPart:i16
movementState:u8
attackerEntityId:i32
dirV: 3×f32
blockPos: 3×i32
hitTransformName:string
hitTransformPosition: 3×f32
uvHit: 2×f32
KillXPScale:f32    // V3.2.0 new (DamageSource.KillXPScale)
damageMultiplier:f32
random:f32
bonusDamageType:u8
StunType:u8
StunDuration:f32
ArmorSlot:u8
ArmorSlotGroup:u8
ArmorDamage:u16
attackingItem present:bool (+ item if true)
```

`flags` bit assignments (from `Setup` IL, inline `or` constants; also exposed
as `cFlags*` static fields used by `read`):

| Bit | Mask | Meaning (source field) |
|---|---|---|
| 0 | 0x001 | canHitSpecialBodyParts (`DamageSource.canHitSpecialBodyParts`) |
| 1 | 0x002 | CrippleLegs (`DamageResponse.CrippleLegs`) |
| 2 | 0x004 | Critical (`DamageResponse.Critical`) |
| 3 | 0x008 | Dismember (`DamageResponse.Dismember`) |
| 4 | 0x010 | Fatal (`DamageResponse.Fatal`) |
| 5 | 0x020 | FromBuff (`DamageSource.BuffClass != null`) |
| 6 | 0x040 | IgnoreConsecutiveDamages (`DamageSource.IsIgnoreConsecutiveDamages()`) |
| 7 | 0x080 | IgnorePartyShare (`DamageSource.bIgnorePartyShare`) |
| 8 | 0x100 | PainHit (`DamageResponse.PainHit`) |
| 9 | 0x200 | TurnIntoCrawler (`DamageResponse.TurnIntoCrawler`) |
| 10 | 0x400 | TrapKillXP (`DamageSource.bTrapKillXP`, V3.2.0 new) |

V3.1.0 wire compat: the old layout interleaved `bFatal`/`bCritical` after
`movementState` and wrote `bIgnoreConsecutiveDamages`, `bIsDamageTransfer`,
`bDismember`, `bCrippleLegs`, `bTurnIntoCrawler`, `bPainHit`, `bFromBuff`,
`bIgnorePartyShare` as individual bools near the tail, with `attackerEntityId`
after `bCritical` and `damageMultiplier` before `random`. The 3.2.0 build packs
all but `bIsDamageTransfer` into `flags`, moves `attackerEntityId` up, and adds
`KillXPScale` (f32) before `damageMultiplier`. This is a **wire-breaking
change**: a V3.1.0 peer cannot parse a V3.2.0 `DamageEntity` body.


### 6.6 NetPackageExplosionInitiate (dynamite)

worldPos 3xf32, blockPos Vector3i, rotation quat, nested `ExplosionData.ToByteArray` (u16 len + bytes), entityId, delay, removeBlock flag, optional ItemValue.
Full layout: [protocol-packages.md](protocol-packages.md) sections 6.14-6.15.

---

## 7. Server send API shapes (managed)

`ConnectionManager.SendPackage` (overload):

```text
SendPackage(NetPackage, bool, int, int, int, Vector3?, int, bool)
SendPackage(List<NetPackage>, ...)  // batch
```

`ClientInfo.SendPackage`, `FlushClientSendQueues`, `ProcessPackages(INetConnection, NetPackageDirection, ClientInfo)`.

`NetPackageManager.ParsePackage(PooledBinaryReader, ClientInfo)`, `GetPackage<T>()` pooling, `IdMappingsReceived(string[])`.

Replication path: [network.md](network.md) §4b (per-player rebuild vs broadcast).

---

## 8. Compression / encryption

| Flag | Bot path | Full server |
|---|---|---|
| compressed | 0 | Set per-package: **8 packages** force `get_Compress = 1` (bulk terrain/map/config), see [protocol-packages.md](protocol-packages.md) §1.2 |
| encrypted | 0 | Public-key handshake decoded: [protocol-packages.md](protocol-packages.md) §2 |

Clone M1: uncompressed, unencrypted only. The join handshake packets are
uncompressed, but chunk/map/config packages are LZ-compressed even on the bot
path (they set `get_Compress` themselves). The encryption handshake
(`EncryptionRequest -> EncryptionPublicKey -> EncryptionSharedKey ->
KeyExchangeComplete`) is now mapped; the cipher/KDF primitives remain native
(residual).

**Live-observed pre-auth order (2026-08-11 in-session capture):**
`PackageIds` → client `PlayerLogin` → `AuthState` `authstate_nativeplatform`
→ `AuthState` `authstate_encryption` → `AuthConfirmation` (empty body) →
`AuthState` `authstate_authenticated` → traffic switches to encrypted
(channel framing `enc=1`), then `PlayerLoginAnswer` + the chunk/map stream.
The `AuthState.stateKey` values are stage strings; all three observed values
match the documented agreement flow. `DiscordIdMappings` arrives right after
`PlayerLoginAnswer` (body 5 bytes = `entityId:u32` + `remove:bool` shape when
`entityId > 0`).

---

## 9. Channels

Loadgen uses **channel 0** for game packages. Challenge is **outside** the envelope (raw 0xCA).

Most packages inherit **channel 0**, but exactly **6 override to channel 1** (the
bulk/terrain/map band): `NetPackageChunk`, `NetPackageChunkRemove`,
`NetPackageMapChunks`, `NetPackageDynamicMesh`, `NetPackagePOIAround`,
`NetPackageWorldFolder`. These carry the heaviest bodies and several are
compressed (`get_Compress = 1`). A clone must route both channels. Full census
and per-package channel/compress/direction/auth: [`protocol-packages.md`](protocol-packages.md) §1.

---

## 10. Validation tools

```bash
# From 7dtd-loadgen (after build)
./src/LoadGen/bin/Release/net8.0/7dtd-loadgen --golden-wire
# Live join against stock or clone on 26902
make join
```

**Live-validated 2026-08-11** (stock V3.1.0 dedicated): the loadgen codec parsed
a real join end-to-end (challenge → PackageIds → auth stages → PlayerLoginAnswer
→ spawn), and the captured PackageIds bytes match the golden layouts above. The
`RECV` hex logs in a join run are the wire evidence; decode them against
§3 and §8.

**Codec-vs-corpus cross-check (2026-08-11):** the loadgen `PackageCodec`'s
`BuildPlayerLogin` (8 fields), `BuildPlayerLoginAnswer` (7 fields), and the
empty-body `BuildAuthConfirmation`/`BuildRequestToEnterGame` layouts equal the
IL-derived bodies in
[`inventories/netpackage-bodies.md`](inventories/netpackage-bodies.md) exactly -
the reference implementation and the RE corpus agree on the login handshake
packages.

Any Zig clone should pass the same golden sizes for PosAndRot / RelPos / AliveFlags / envelope, then accept loadgen probe.

---

## 11. RE backlog (protocol)

Status refreshed 2026-08-10 (rows re-verified against the current
[`protocol-packages.md`](protocol-packages.md) sections):

| Priority | Item | Why | Status |
|---:|---|---|---|
| P0 | NetPackageChunk body | Client terrain | **Done** ([protocol-packages.md](protocol-packages.md) §3.1) |
| P0 | EntitySpawn / SpawnResponse | Visible zombies/players | **Done** (§5.1-5.2: header + entityClass-switched middle incl. shared-count trap + tail) |
| P0 | WorldInfo / WorldTime / WorldInit* | Client world ready | WorldInfo/WorldTime **done**; WorldInitInfo **done** (§4.3 + WorldFolder §6.22) |
| P1 | SetBlock / SetBlockResponse | Building | **Done** (§6) |
| P1 | PlayerInventory / HoldingItem | Play loop | **Done** (§5.3-5.4) |
| P1 | ChunkRemove* | Unload | **Done** (§3.2) |
| P2 | Encryption handshake | Public servers | **Done** (§2); cipher/KDF native (residual) |
| P2 | TileEntity / vehicles | Features | **Done** (§6.12, §6.21) |
| P3 | Quest/Party/Twitch | Completeness | Quest/Party **done** (§6.17-6.18); Twitch server slice in twitch-integration.md |
| residual | EAC | Out of scope | Residual |
| residual | LiteNet event dispatch | Closed 2026-08-10 ([network.md](network.md) §4.0) | Closed |

---

## Related docs

| Doc | Role |
|---|---|
| **[protocol-frames.md](protocol-frames.md)** | **Visual frame catalog (RFC + Mermaid)** |
| **[protocol-packages.md](protocol-packages.md)** | **Per-package body catalog + metadata census + encryption handshake** |
| [re-methodology.md](re-methodology.md) | How the bodies were derived from IL |
| [ZIG_CLONE.md](../../zdtd-server/docs/ZIG_CLONE.md) | Clone architecture |
| [network.md](network.md) | Interest + scale |
| [closed-gaps.md](closed-gaps.md) | Package band thresholds |
| [engine-limitations.md](engine-limitations.md) | Net ceilings |
| [inventories/netpackages.md](inventories/netpackages.md) | All type names |
| DEDI_COMPLETE auto §3 | Full package name list |
| loadgen PackageCodec | Golden implementations |

## Changelog

- **2026-08-28:** V3.2.0 pin: version display V 3.2.0; §6.5 NetPackageDamageEntity rewritten (packed flags table + KillXPScale; V3.1.0 bool layout retained as compat note).
- **2026-08-11:** Join IL re-verified: RequestToEnterGame IL=9 + <RequestToEnterGame>d__195.MoveNext IL=248, ChunkClusterInfo.ProcessPackage IL=13, NetPackagePlayerLoginAnswer.write IL=46, NetPackagePlayerId.write IL=21, NetPackagePlayerSpawnedInWorld.write IL=16, PlayerSpawnedInWorld IL=127 (exact).
- **2026-08-10:** RE-backlog table refreshed: TileEntity/vehicles + Quest/Party
  rows closed (were "Open", covered by §6.12/§6.21/§6.17-6.18).
- **2026-08-08:** Live wire verification: booted the native Linux dedicated server (V3.1.0) and ran the `7dtd-loadgen` client (built from these wire docs) through a full join against both the modded and the stock server (`challengesOk=1`, `logins=1`, `joined entity=102`); the golden layouts match observed traffic end-to-end. Server bound TCP+UDP 26900/26902.
- **2026-08-08:** NetPackageDamageEntity wire: added bIgnorePartyShare:bool (between bFromBuff and ArmorSlot).
- **2026-07-28:** `RequestToSpawnPlayer` server path, `PlayerId`/`PlayerSpawnedInWorld` bodies, RespawnType.

- **2026-07-28:** `RequestToEnterGame` package sequence, deny reasons 10/31, `PlayerLoginAnswer` write fields.

- **2026-07-23:** §11 backlog status updated after the protocol-packages.md body pass.
- **2026-07-20:** Link visual protocol-frames catalog (RFC bars + Mermaid block-beta).
- **2026-07-20:** Initial protocol narrative from loadgen golden wire + dedi-complete census.
