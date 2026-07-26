# Cluster A (wire/protocol) IL correctness audit - V3.0.1

**Verdict:** 1 CRITICAL, 0 MAJOR, 1 MINOR wire/protocol issue found. The rest of
the load-bearing wire claims spot-checked (~30) are correct against the DLL IL.

**Ground truth:** `Assembly-CSharp.dll` (V3.0.1 dedicated). All commands below run
from repo root with `ASM` = the stable dedicated-server DLL path. Raw dumps used:
`/tmp/census.txt` (NetProtocolCensus), `/tmp/enums.txt` (EnumList), `/tmp/np/`
(DumpNetPackages, 193 bodies).

---

## Findings

### [CRITICAL-1] WorldInfo `worldHashesData` wire layout is wrong (protocol-packages.md 4.2)

**Doc claim** (`docs/protocol-packages.md` 4.2, "NetPackageWorldInfo write order"):
```
worldHashesData : i32 len + byte[len]     // world file hashes blob
worldDataSize   : i64
```
This says the hash blob is a byte array preceded by an `i32` **byte-length** prefix.

**Ground truth.** The write emits the hashes as a raw `byte[]` with **no length
prefix at all**, and the read parses a **count-prefixed dictionary**, not opaque
bytes. The leading `i32` is an entry **count**, followed by `count x (string, u32)`
pairs.

`mono tools/bin/DumpNetPackages.exe "$ASM" /tmp/np` -> `/tmp/np/NetPackageWorldInfo_il.txt`

write (tail):
```
IL_0072: ldfld Boolean firstTimeJoin
IL_0077: Write(System.Boolean)
IL_007D: ldsfld Byte[] worldHashesData
IL_0082: Write(System.Byte[])        // BinaryWriter.Write(byte[]) => raw bytes, NO length prefix
IL_0088: ldsfld Int64 worldDataSize
IL_008D: Write(System.Int64)
```
read (the authoritative structure of those bytes):
```
IL_0070: ReadInt32()  -> stloc.0                              // COUNT of hash entries
IL_0077: newobj Dictionary`2<System.String,System.UInt32>     // worldFileHashes
loop count times:
  IL_0086: ReadString()  -> filename
  IL_008D: ReadUInt32()  -> hash
  Dictionary::Add(filename, hash)
IL_00A9: ReadInt64()  -> worldDataSize
```

So the actual on-wire body from `firstTimeJoin` onward is:
```
worldFileHashes : i32 count, then count x { filename : string, hash : u32 }
worldDataSize   : i64
```
A clone implementing the documented "i32 len + byte[len]" would read the entry
count as a byte length, consume that many raw bytes (instead of string/u32 pairs),
desync the stream, and misparse `worldDataSize`. This breaks join for any client
built from the doc.

**Fix.** Replace the two lines in 4.2 with the count-prefixed dictionary form
above (i32 count + count x (string filename, u32 hash), then i64 worldDataSize).
Note the write side serializes a pre-baked `worldHashesData` static blob that
already contains that exact `[i32 count][ (string,u32) x count ]` structure, which
is why write uses `Write(byte[])` while read reconstructs the dictionary.

---

### [MINOR-1] "193 wire packages" overcounts by ~6 non-wire helper types (protocol.md 4; network.md 3; inventories/netpackages.md)

**Doc claim.** `docs/protocol.md` 4: "**194** `NetPackage*` types = **193 wire
packages + `NetPackageManager`**". Repeated verbatim in `docs/network.md` 3.

**Ground truth.** The `194 = 193 + Manager` arithmetic is internally consistent
(`comm` of census names vs the inventory table differs only by `NetPackageManager`),
but 6 of the 193 are **not wire packages** - they are name-prefixed helpers that
appear all-`inherit` in the census because they do not derive from `NetPackage`:

`mono tools/bin/NetProtocolCensus.exe "$ASM" /tmp/census.txt`; `grep -E 'NetPackageDirection|NetPackageEntry|NetPackageInfo|NetPackageLogger|NetPackageMeasure|NetPackageMetrics' /tmp/census.txt`
```
| NetPackageDirection | inherit | inherit | inherit | inherit | inherit |   (base: Enum)
| NetPackageEntry     | inherit | inherit | inherit | inherit | inherit |   (base: Object)
| NetPackageInfo      | inherit | inherit | inherit | inherit | inherit |   (base: Object)
| NetPackageLogger    | inherit | inherit | inherit | inherit | inherit |   (base: Object)
| NetPackageMeasure   | inherit | inherit | inherit | inherit | inherit |   (base: Object)
| NetPackageMetrics   | inherit | inherit | inherit | inherit | inherit |   (base: Object)
```
Bases confirmed by `docs/inventories/netpackages.md` (rows: `NetPackageDirection|Enum`,
`NetPackageEntry|Object`, `NetPackageInfo|Object`, `NetPackageLogger|Object`,
`NetPackageMeasure|Object`, `NetPackageMetrics|Object`). Subtracting these 6 plus
the abstract `NetPackage` base leaves ~186 actual wire package classes.

**Impact:** cosmetic count/label imprecision, not wire-breaking. It does not
affect any documented body.

**Fix.** Either say "194 `NetPackage*`-named types (193 excluding `NetPackageManager`;
~186 are actual wire packages, the rest are the base class plus Enum/Object helper
types)", or footnote that the census counts by name prefix.

---

## Spot-verified CONFIRMED (load-bearing claims checked against IL)

Census/enum tooling:
- **Channel-1 set (6):** protocol-packages.md 1.1 and protocol.md 9 list Chunk,
  ChunkRemove, MapChunks, DynamicMesh, POIAround, WorldFolder - exact match.
  `awk` over `/tmp/census.txt` chan col.
- **Compressed set (8):** protocol-packages.md 1.2 - Chunk, MapChunks, DynamicMesh,
  POIAround, ConfigFile, DynamicClientArrive, IdMapping, SignDataResponse - exact
  match to census Compress=1.
- **Before-auth set (10):** protocol-packages.md 1.4 - PackageIds, PlayerLogin,
  PlayerDenied, AuthConfirmation, AuthState, EAC, EncryptionRequest,
  EncryptionPublicKey, EncryptionSharedKey, KeyExchangeComplete - exact match to
  census BeforeAuth=1.
- **Direction tally:** protocol-packages.md 1.3 "66 ToClient, 33 ToServer, 7 Both
  (explicit), 87 inherit" - census dir col: `2`=66, `1`=33, `0`=7, inherit=87. Exact.
- **Package count reconciliation:** 194 inventory rows = 193 census names +
  `NetPackageManager` (`comm -13` diff). Consistent across protocol.md/network.md.

Enums (`/tmp/enums.txt` from `EnumList.exe`):
- **EChatType:** 0 Global, 1 Friends, 2 Party, 3 Whisper, 4 Discord (chat.md 1). Exact.
- **EnumGameMessages:** 0 PlainTextLocal..6 BlockedPlayerAlert (chat.md 3). Exact.
- **EMessageSender:** None=0, Server=1, SenderIdAsPlayer=2 (chat.md). Exact.
- **eSetBlockResponse:** Success=0, PowerBlockLimitExceeded=1,
  StorageBlockLimitExceeded=2 (protocol-packages.md 6.2, 7). Exact.
- **EnumSpawnerSource:** Unknown=0, Biome=1, StaticSpawner=2, Dynamic=3, Delete=4
  (protocol-packages.md 5.1, 7). Exact.
- **EKickReason:** 35 values (0..34); all "notable" values cited in
  protocol-packages.md 7 (4 VersionMismatch, 5 PlayerLimitExceeded, 6 Banned,
  7 NotOnWhitelist, 11 EacViolation, 18 UnknownNetPackage, 19 EncryptionFailure,
  33 EncryptionAgreementInvalidSignature, 34 EncryptionAgreementError) match. Exact.
- **EPlatformIdentifier:** None,Local,EOS,Steam,XBL,PSN,EGS,LAN,Count = 0..8
  (platform-auth.md 2.1). Exact order.

Wire bodies (`/tmp/np/*_il.txt` write/read IL, and `DumpMethod.exe`):
- **NetPackageChat** body: chatType(u8 conv.u1), senderEntityId(i32), msg(string),
  msgSender(u8), bbMode(u8), recipientEntityIds(i32 count + count x i32).
  write IL=63 matches chat.md 1 exactly; read symmetric.
- **NetPackageEncryptionPublicKey:** ExchangePublicKeyParamsXml(string),
  Hash(i32 len + byte[]), SignedHash(i32 len + byte[]). Matches protocol-packages.md 2.
- **NetPackageEncryptionSharedKey:** EncryptionKey(i32 len + byte[]),
  IntegrityKey(i32 len + byte[]). Match.
- **NetPackageKeyExchangeComplete:** wasSuccessful(bool). Match.
- **NetPackageEncryptionRequest:** write IL=4 (base only) = empty body. Match.
- **NetPackageChunkRemove:** chunkKey(i64). Match (protocol-packages.md 3.2).
- **NetPackageWorldTime:** worldTime(u64). Match (4.1).
- **NetPackageChunk:** bOverwriteExisting(bool), if set chunkX/Y/Z(i16 conv.i2 x3),
  dataLen(i32 = serializedData length), data via StreamUtils::StreamCopy;
  GetLength = 14 + serializedData.Length (ldc.i4.s 14 + get_Length). Match (3.1).
- **BlockChangeInfo::Write:** BlockValueRef.Write, changedByEntityId(i32),
  flags(byte packed from bChangeBlockValue/bChangeDensity/bForceDensity/bUpdateLight/
  bChangeDamage/bChangeTexture), then if bChangeBlockValue BlockValue.Write, if
  bChangeDensity density(sbyte), if bChangeTexture TextureFullArray.Write. Match (6.1).
  `mono tools/bin/DumpMethod.exe "$ASM" BlockChangeInfo Write`
- **NetPackageSetBlock:** persistentPlayerId via PlatformUserIdentifierExtensions::
  ToStream, blockChanges count(i16), each BlockChangeInfo.Write, localPlayerThatChanged
  (i32). Match (6.1).
- **NetPackageSetBlockResponse:** response(u16 conv.u2). Match (6.2).
- **NetPackageHoldingItem:** entityId(i32), holdingItemStack(ItemStack.Write),
  holdingItemIndex(byte). Match (5.3).
- **NetPackagePlayerInventory:** toolbelt present(bool)+GameUtils::WriteItemStack,
  bag present(bool)+Bag.Write, equipment present(bool)+slot count(i32)+unlockedCosmetics,
  dragAndDropItem(ItemStack.Write). Match (5.4).
- **NetPackageEntitySpawnResponse:** success(bool), itemValue(ItemValue.Write). Match (5.2).
- **NetPackagePlayerDenied / KickPlayerData:** reason(i32), apiResponseEnum(i32),
  banUntil(i64), customReason(string). Match (7).
- **EntityCreationData::write** header: readFileVersion(byte), entityClass(i32),
  id(i32), lifetime(f32), pos xyz(f32 x3), rot xyz(f32 x3), onGround(bool),
  BodyDamage.Write, stats present(bool)+EntityStats.Write, deathTime(i16 conv.i2),
  bag present(bool)+Bag.Write, homePosition xyz(i32 x3), homeRange(i16 conv.i2),
  spawnerSource(byte conv.u1), belongsPlayerId(i32), clientEntityId(i32),
  itemStack(ItemStack.Write). Full header match (5.1). `DumpMethod EntityCreationData write` IL=358.
- **NetPackageDamageEntity::write** (protocol.md 6.5): all 30+ fields verified in
  order incl. blockPos via StreamUtils::Write(Vector3i), armor tail
  (ArmorSlot u8, ArmorSlotGroup u8, ArmorDamage u16), attackingItem present(bool)+
  ItemValue.Write. Full match.
- **NetPackagePackageIds::write:** VersionInformation.Write, count(i32),
  count x string, serverUseEac(bool), hasHostUserAndToken(bool), platform user via
  ToStream + token string. Structural match (protocol.md 4).
- **NetPackagePlayerLogin::write:** playerName(string), platformUser(ToStream)+
  token(string), crossplatform(ToStream)+token(string), versionLong(string),
  compVersionLong(string), discordUserId(u64). Match (protocol.md 5).
- **NetPackageEntityPosAndRot:** base entityId(i32) + xyz(f32 x3) + bUseQRotation(bool)
  + rot branch + onGround; body size 30 consistent. Match (protocol.md 6.1).
- **NetPackageEntityAliveFlags:** base entityId(i32) + flags(u16) => body 6. Match (6.3).
  (Bit-name labels in 6.3 are loadgen-sourced, not a DLL enum; the u16 field itself
  is confirmed.)
- **NetPackageEntityLookAt:** base entityId(i32) + lookX/Y/Z(i32, conv.i4 from float).
  Match (6.4).
- **NetPackageRequestToSpawnPlayer:** chunkViewDim(i16 conv.i2), PlayerProfile.Write,
  nearEntityId(i32). Match (protocol.md 5).
- **Empty bodies:** NetPackageRequestToEnterGame write IL=4, NetPackageAuthConfirmation
  write IL=4 (base only). Match (protocol.md 5).
- **PlatformUserIdentifierExtensions::ToStream** (BinaryWriter overload): present(byte),
  if present version(byte), platform(string), userId(string); null => single byte then
  stop. Token is written separately by the login package. Matches platform-auth.md 2.1
  "Identity + ticket wire layout" (token appended by the package, as the prose states).
- **ConnectionManager::Update** IL=215 (network.md 1 "IL~=215", frame-entries.md row).
  `DumpMethod ConnectionManager Update`.

Envelope/framing (protocol.md 3, protocol-frames.md 2): challenge 17 bytes
(0xCA marker + 16-byte Guid); game envelope channel(u8) / payloadSize(i32) /
compressed(u8) / encrypted(u8) / pkgCount(u16) / payload; inner
contentLen(i32)+pkgId(u16)+body; frame_len = 9 + payloadSize; contentLen =
2 + body_len. Consistent between protocol.md and protocol-frames.md (loadgen-derived;
the envelope itself lives in native LiteNet, not in a managed write() body, so it is
cross-checked for internal consistency, not against a DLL method).

## Not verifiable from the DLL (flagged honestly)
- Live id-map "189 entries", live hex capture head, port 26902: runtime/capture
  facts, not in the DLL. Left as-is; internally consistent.
- EntityAliveFlags bit names, LiteNet native framing, encryption cipher/KDF: doc
  already marks these loadgen/native/residual.
