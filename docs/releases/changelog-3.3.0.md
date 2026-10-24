# V3.2.0 → V3.3.0 exact-difference changelog

**Hub:** [`INDEX.md`](../INDEX.md).

**Scope:** stock dedicated `Assembly-CSharp.dll`, 7 Days to Die.
**From:** V3.2.0 b10 (Major=3 Minor=20 Build=10), Steam build `24994542`, depot
manifest `1633674551820196085`, DLL sha256 `3737eedc...`, 11610624 bytes.
**To:** V3.3.0 b18 (Major=3 Minor=30 Build=18), Steam build `25661908`, depot
manifest `3031329678505041777`, DLL sha256 `e16ff9d5...`, 11697152 bytes.
**Current pin:** V3.3.0 b18.
**Method:** pairwise IL diff of the tracked V3.2.0 dump sets (`il/*-v3.2.0/`)
against freshly regenerated V3.3.0 sets (`il/*-v3.3.0/`), the eight-lens report
[`../../workspace/outputs/diffs/b10-to-v3.3.0-20261024.md`](../../workspace/outputs/diffs/b10-to-v3.3.0-20261024.md),
the machine pins in [`../../tools/data/stock_facts.json`](../../tools/data/stock_facts.json)
and [`../../tools/data/xml_pins.json`](../../tools/data/xml_pins.json), the wire
snapshots `workspace/outputs/parity/parity_b10.json` / `parity_b18.json`, and the
depot manifests of both builds (`steam_manifest.py --diff`).
**Honesty:** facts marked `verified` were read directly from IL in both dumps or
from the shipped file named beside them; `inferred` means the IL implies it but
no live probe confirmed it; `not decoded` names a gap that is still open.

---

## 1. Summary

The release is a subsystem rework, not a patch. The dedicated assembly gains 21
top-level types (+257 methods with body) while the wire registry loses three
packages net, and the largest single change is mechanical: every `Read`/`Write`
in the save and network paths moved from `BinaryReader`/`BinaryWriter` to
`PooledBinaryReader`/`PooledBinaryWriter` (342 changed signatures).

| Lens | b10 | b18 | Delta |
|---|---:|---:|---:|
| Top-level types | 4426 | 4447 | +21 |
| Type metadata rows | (all lenses) | (all lenses) | 167 added, 135 removed, 463 changed |
| Methods with body (top level) | 44277 | 44534 | +257 |
| Method signatures | | | 940 added, 643 removed, 342 changed |
| Enum members | | | 31 added, 16 removed, 34 renumbered |
| Method bodies (hash) | | | 2079 added, 1703 removed, 1514 changed |
| `NetPackage*` top-level types | 195 | 192 | -3 |
| Registered wire packages (ids 0..N-1) | 187 | 184 | 3 added, 6 removed, 4 rewired |
| `ParitySurface` package entries | 192 | 189 | as above; the extra entries carry a read/write pair without a registered id |
| gmUpdate IL instructions | 631 | 638 | +7 |
| `WorldState.SaveLoad(Stream)` IL | 926 | 926 | unchanged |
| `CurrentSaveVersion` | 23 | 23 | unchanged |
| LiteNetLib protocol id | 13 | 13 | unchanged |
| Depot files | 17639 | 17639 | 15 added, 59 changed, 0 removed |

Six themes account for the delta. Wire package lifecycle moved to the pooled
readers and two features (signs, locks) replaced their request/response pairs
with one-way pushes. A new sign subsystem owns sign data outside the tile
entity. The inventory/equipment model was rebuilt around a `Hand` and an
`ItemStackGrid`, with a thirteen-slot equipment list that now includes a
backpack. A new `AssetManagement` namespace owns asset loading. A new
`Services.Analytics` surface was added. The rest is the pooled-reader migration
plus new console commands, spawn-selection state and Burst path entry points.

## 2. Machine pins and census

All rows below are machine-checked: `make facts` prints them from
[`../../tools/data/stock_facts.json`](../../tools/data/stock_facts.json) and
`make stock-check` fails when the live bytes disagree.

| Pin | b10 | b18 |
|---|---|---|
| `version.display` / `stock_wire` | V 3.2.0 / V3.2.0 b10 | V 3.3.0 / V3.3.0 b18 |
| `version.game_reset_revision` | 13 | 13 |
| `census.top_level_types` | 4426 | 4447 |
| `census.methods_with_body_top_level` | 44277 | 44534 |
| `census.gmupdate_il` | 631 | 638 |
| `network.netpackage_top_level_count` | 195 | 192 |
| `save.current_save_version` | 23 | 23 |
| `save.worldstate_saveload_stream_il` | 926 | 926 |
| `sim.constants_ticks_per_second` | 20 | 20 |
| `chunk.block_y_dim` / `block_layers` | 256 / 64 | 256 / 64 |
| `litenet.protocol_id` | 13 | 13 |
| `litenet.header_size` / `channeled_header_size` / `fragment_header_size` | 1 / 4 / 6 | 1 / 4 / 6 |
| `litenet.max_packet_size` / `initial_mtu` / `default_window_size` | 1432 / 1024 / 64 | 1432 / 1024 / 64 |
| `litenet.possible_mtu` | (row absent) | `[1024, 1164, 1392, 1404, 1424, 1432]` |
| `enums.game_stats_members` / `game_prefs_members` | 82 / 317 | 82 / 317 |
| `behaviour.world_water_level` | 62.88 | 62.88 |
| `behaviour.item_dropped_on_death_lifetime_s` | 300 | 300 |
| `behaviour.max_load_time_per_frame_ms` | 50 | 50 |
| `behaviour.max_party_size` | 8 | 8 |
| `xml: entityclasses.xml` sha256 | `0c95e733...` | `5f930212...` (415836 bytes) |
| `xml: traders.xml` sha256 | `06202f16...` | `b7d18604...` (67126 bytes) |
| `xml: buffs.xml` sha256 | `d6c714d7...` | `08345e0d...` (1036875 bytes) |

The `litenet.possible_mtu` row changed from absent to a six-value list, and the
whole `litenet.*` family moved in and out of `provenance.baked`. Both sides are
an artefact of the extraction, not of the build: `StockFacts` reads the sibling
`LiteNetLib.dll`, and the b10 side in this run is a copied assembly whose sibling
was not beside it. The b10 values were pinned from the live install when the pin
was recorded and none of them moved; only the reporting of which rows were baked
differs. Treat the b10 column of the `litenet.*` rows as the recorded pin, not as
a fresh measurement.

## 3. Non-managed content delta

Steam's own depot manifest for both builds gives the exact file set:
`steam_manifest.py --manifest 294422_3031329678505041777.manifest --diff
294422_1633674551820196085.manifest` reports 15 added, 0 removed, 59 changed.
`Assembly-CSharp.dll` is one of the 59; the rest are the data, audio and bundle
changes that belong with it.

**Added (15).**

| File | Bytes | Note |
|---|---:|---|
| `Data/Config/toolbelt.xml` | 343 | New config file; no b10 counterpart. |
| `Data/Addressables/Standalone/automatic_assets_dlc/halloweencosmetic.bundle` | 92931175 | Matches `EntitlementSetEnum.HalloweenCosmetic = 19`. |
| `Data/Addressables/Standalone/automatic_assets_dlc/oktoberfestcosmetic.bundle` | 116513737 | Matches `EntitlementSetEnum.OktoberfestCosmetic = 18`. |
| `Data/ItemIcons/armorKegBreaker{Boots,Gloves,Helmet,Outfit}.png` | 36447 / 29018 / 25215 / 38668 | New armour set. |
| `Data/ItemIcons/armorWraithWoodWitch{Boots,Gloves,Helmet,Outfit}.png` | 34749 / 28341 / 26660 / 34851 | New armour set. |
| `Data/ItemIcons/backpack{Small,Medium,Large}.png` | 32943 / 34981 / 35622 | Backpack item art; matches `EquipmentSlots.Backpack`. |
| `Data/ItemIcons/bookPackRat.png` | 46954 | New perk book icon. |

**Changed, configuration (17).** `items.xml` 2141821 → 2154063,
`Localization.csv` 16777812 → 16840111, `progression.xml` 385257 → 387251,
`recipes.xml` 274900 → 277478, `sounds.xml` 1540413 → 1542439,
`entityclasses.xml` 414216 → 415836, `loot.xml` 514046 → 514818,
`traders.xml` 66301 → 67126, `buffs.xml` 1036835 → 1036875,
`ui_display.xml` 109532 → 109860, and the seven `XUi_*` XML files (the
`XUi_InGame/windows.xml` grows by 6482 bytes; the sign windows live there).

**Changed, managed (5).** `Assembly-CSharp.dll`, `Assembly-CSharp-firstpass.dll`
(249344 → 256512), `BhvrAnalytics.dll` (24064 → 23552, the analytics SDK the new
`Services.Analytics` wraps), `NGUI.dll` (same size, different SHA-1) and
`Unity.Collections.dll` (same size, different SHA-1, the Burst job support).

**Changed, assets and mods (the remaining 37).** All 20 shipped cosmetic
bundles, `itemicons.bundle` (42583050 → 43112216), the entity/vehicle/sound
bundles, `shaders_assets_all.bundle` (30653253 → 32260225), `data.unity3d`
(47254327 → 47240425), the addressables `catalog.json`/`settings.json`, the
`Entities`/`trees` bundle manifests, and both shipped example mods
(`TFP_CommandExtensions` 18944 → 14336 plus its `ModInfo.xml`, and
`Xample_MarkersMod` 16896 → 17408 plus its `ModInfo.xml`).

### 2.1 Second measurement: CLI metadata tables

The numbers above come from the corpus's Mono.Cecil dumpers. The same two
assemblies read through REA's CLI metadata admission
(`inspect_managed_artifact`, static, nothing executed) agree table for table:
`TypeDef` 7451 → 7501 and `MethodDef` 56064 → 56440 are exactly the
`FullSurface` type count and the body-diff method count, which is the
cross-check that the two measurement paths are reading the same rows.

| Metadata table | b10 | b18 |
|---|---:|---:|
| `TypeDef` | 7451 | 7501 |
| `MethodDef` | 56064 | 56440 |
| `Field` | 43741 | 43956 |
| `Param` | 53243 | 53606 |
| `Property` | 6996 | 7162 |
| `Event` | 322 | 321 |
| `MemberRef` | 20846 | 21020 |
| `TypeRef` | 1692 | 1698 |
| `AssemblyRef` | 60 | 60 |
| `TypeSpec` | 5052 | 5106 |
| `GenericParam` | 942 | 971 |
| `NestedClass` | 3025 | 3054 |
| `CustomAttribute` | 57784 | 58813 |

`AssemblyRef` is unchanged at 60 and the assembly version is `0.0.0.0` in both,
so the release adds no new external managed dependency. The module MVID moved
(`aeec89b3-c160-4192-ab20-6c37094e85cf` → `7f5cc1f5-9e7e-45c1-9531-7cdad1777ebb`),
which is expected for any rebuild and is the only identity that is
build-local rather than content-derivable.

## 4. Wire protocol

### 4.1 Package registry

Registered wire packages are 187 (ids 0..186) in b10 and **184 (ids 0..183)** in
b18: three added, six removed, nothing renamed. `NetPackagePackageIds` stays
pinned at id 0 and the rest of the numbering is the order in which
`knownPackageTypes` is filled, which is `Assembly.GetTypes()` metadata order, so
a removal also renumbers everything after it.

| Package | b10 id | b18 id |
|---|---:|---:|
| `NetPackageLockTarget` | absent | **93** |
| `NetPackageSingleSignData` | absent | **144** |
| `NetPackageSignDelete` | absent | **145** |
| `NetPackageItemActionEffects` | 91 | 87 |
| `NetPackagePlayerEquipment` | 114 | 109 |
| `NetPackagePlayerInventory` | 116 | 111 |
| `NetPackageSignDataResponse` | 148 | 143 |

Every package from id 86 up moves by -3. Removed: `NetPackageInventoryDataRequest`,
`NetPackageInventoryDataResponse`, `NetPackageInventoryTransactionRequest`,
`NetPackageInventoryTransactionResponse`, `NetPackageLockRequest`,
`NetPackageLockResponse`. The ids are derived, not stored, and no live V3.3.0
join capture was taken, so the re-derived table is `inferred` from metadata
order even though the set membership is `verified`.

The census counts 192 top-level `NetPackage*` types (195 in b10). Eight of those
are not registered: the abstract base, the abstract `NetPackageEntityTargeted`,
the `NetPackageDirection` enum, `NetPackageLogger`, and the helper classes
`NetPackageEntry`, `NetPackageInfo`, `NetPackageMeasure`, `NetPackageMetrics`.
The framing census is unchanged: 5 packages override to channel 1, 8 set
`get_Compress`, 5 are allowed before auth, 5 are marked unreliable, and the
direction split is 65 any / 31 ToServer / 7 ToClient / 89 ToClient-with-broadcast.

### 4.2 Version handshake

`Constants..cctor` becomes `(1, 3, 30, 18)`, the login strings carry `V 3.3.0`,
`NetPackagePackageIds` reports minor 30 build 18, and the server browser's GSI
string becomes `V.3.30.18`. A V3.2.0 client is rejected with the version
mismatch, which matters because the two blob packages below are not readable
across the boundary in either direction.

### 4.3 The blob packages

`NetPackagePlayerInventory` now carries three optional payloads and the drag
item. Each payload is `bool present`, then `i32 byteLength` and that many bytes
when present (`StreamUtils.WriteBlob`; `ReadBlob` returns an empty stream for a
length of zero or less). The blob contents are exactly the save serializers:

| Envelope | Blob | Body |
|---|---|---|
| `inventoryData` | `Inventory.Write` | `u8 1`, `ItemStackGrid`, `u8 selectedSlot` |
| `bagData` | `Bag.Write` | `u8 2`, `ItemStackGrid` |
| `equipmentData` | `Equipment.Write` | `u8 6`, `ItemStackGrid`, 13 cosmetic-slot `i32`s, unlocked-cosmetic count and ids |

`ItemStackGrid` itself is a versioned record: `u16 version 2`, `Vector2i`
container size, `i16 slot count`, that many `ItemStack` (u16 count plus
`ItemValue` version 9), `bool hasSlotLocks` plus `PackedBoolArray`,
`bool hasPreferences` plus `PreferenceTracker`, `u64 worldTimeTouched`, and
`bool playerOwned`. `NetPackagePlayerEquipment` carries one `equipmentData` blob
after its `NetPackageEntityTargeted` prefix.

`NetPackageItemActionEffects` changes only its slot field from `Byte` to
`SByte`: one byte either way, so that one is not a wire break.

`ProcessPackage` on the inventory package copies the received blobs into
`ClientInfo.latestPlayerData` and sets `bModifiedSinceLastSave`. It does not
decode, validate, hash or reconcile them; they reach the world later through
`PlayerDataFile.ToPlayer` (`FromBlob` then `Inventory.ReadInto`, `Bag.ReadInto`,
`Equipment.ReadInto`), with overflow items spilled on the ground. The b10
per-operation transaction gate is gone with the six packages, so the owning
client is the only serializer of its own containers.

### 4.4 Locks

`NetPackageLockRequest` and `NetPackageLockResponse` collapse into one
`NetPackageLockTarget`: an `i32 payloadLength` followed by the opaque
`LockManager` payload. The request side is `bool isLock`, `u16 channel`, a
count (the server accepts 1 to 5), an array of `WorldAddress`, and the per-target
`OnLockRequestLocal` attachments; the response side adds the success/error byte
and the `OnLockResponseServer` tails. `WorldAddress` is a `u8 WorldObjectType`
(`0` None, `1` TileEntity, `2` TEFeature, `3` Entity) followed by `Vector3i`,
`Vector3i` plus feature name, or an entity id, matching the object type.

The lock state is server-authoritative: `ProcessRequest` rejects a client role,
`singleLocks`/`sharedLocks` live on the server, and the server decides grant or
deny before dispatching the response. `LockTargetType` is gone, replaced by
`WorldObjectType`. `LockChannel` is nested per owner (`EntityTrader`
Interaction/Trade, `EntityVehicle` Interaction/Collect, plus the new
`LockChannel.Collect = 1`), and `IsSharedLock` decides whether a channel is
shared or exclusive.

### 4.5 Signs on the wire

`NetPackageSingleSignData` runs both directions: `string libraryId`,
`i32 byteLength`, then the `SignData` blob bytes when the length is positive.
`NetPackageSignDelete` runs both directions and carries a `GlobalSignId` stream,
which is `string libraryId` plus 16 raw guid bytes, unchanged from b10 apart
from the reader type. `NetPackageSignDataResponse` keeps its body
(`bool isLastBatch`, `i32 length`, bytes; ToClient, compressed); only its reader
changed (it uses `ReadExact` over a span) and `GetLength` was removed.
`NetPackageSignDataRequest` keeps an empty body and lost `GetLength` too. The
batch is `[i32 marker]` followed by `(string libraryId, SignData.Read)`
repeated.

A b10 client and a b18 server cannot exchange any of the six removed packages,
the lock package or the two blob packages; the version handshake refuses the
connection before that matters.

## 5. Inventory, equipment and items

### 5.1 Equipment

`EquipmentSlots` gains `Backpack = 12`; `Count` and `None` move from 12 to 13.
Slots 0..11 keep their numbers, so a b10 save's equipment reads back in the same
positions with slot 12 empty. `Equipment.GetSlotCount` now returns the grid
length, so every loop that iterates it (armor summation included) sees 13
entries. The new `EquipmentSlotExtensions.SlotType` maps 0..3 and 12 to
`EquipmentSlotType.Armor`, 4..7 to `BiomeGear`, 8..11 to `Clothing`, and 13 to
`None`, throwing on anything else.

The shipped gear is in `items.xml`: `backpackMaster` as a base template,
`backpackSmall`/`backpackMedium`/`backpackLarge` with `EquipSlot=Backpack`, and
the Oktoberfest `armorKegBreaker*` and Halloween `armorWraithWoodWitch*` sets.
`progression.xml` gains `craftingBackpack` (max level 100) with bag-size tier
unlocks, and PackMule's `CarryCapacity` values rise from 3/6/10/14/18 to
4/12/24/40/56. `recipes.xml` gains the three backpack recipes (10 s / 30 s /
60 s), and `loot.xml` gains `groupPlayerBackpacks` and widens the dropped-backpack
container from 7x10 to 8x15 (and `cntDropBag` from 9x10 to 8x15).

The bag itself: `Entity.MaxBagSize` is new (45 in the base constructor, 96 on the
player class in `entityclasses.xml`), the player's base `BagSize` moves 45 to 48,
and `EntityPlayer.CalcCurrentBackpackSize`/`UpdateBagpackSize`/
`shrinkBackpackMoveItems` resize it and spill items when backpack gear is
removed. The backpack items' `passive_effect` rows add 2..16, 18..32 and 34..48 by
tier, so the ladder is 50..64, 66..80 and 82..96.

### 5.2 Hand, grid and toolbelt

`ItemStackGrid` stops being a UI class and becomes the storage and
serialization core: it owns the holder, the slot locks (`PackedBoolArray`), the
preferences, the touched-world time, the `playerOwned` flag, the `Vector2i`
container size and the `StackLocationTypes` label, and it provides the
`SetItem`/`AddItem`/`ChangeCount`/`Compact`/`Sort`/`CopyFrom`/`Resize` family
that the old `ItemStack[]` helpers provided.

`Hand` is new and owns what `Inventory` used to hold inline: the toolbelt
binding, the per-slot `ItemInventoryData`, the bare-hand and transient data, the
`HoldingMode` (`Current`/`Bare`/`Transient`), the equipped and holstering models,
the quick-swap memory and the holster/unholster `TransitionRoutine`.
`HoldingMode` replaces `HeldItemState`. `Inventory.Hand` is the entry point;
`Inventory` keeps delegating wrappers (`get_holdingItem`, `SetHoldingItemIdx`,
`DecHoldingItem`, `Execute`, `ReleaseAll`, `ReconcileHeldItem`, `IsHandBusy`).
`ItemInventoryData` becomes the per-slot held instance
(`Create(EntityAlive, ItemStack, int)` replaces
`ItemClass.createItemInventoryData`) and builds its model through the new asset
handles.

The toolbelt count is data-driven. `ToolbeltConfig` (`SlotsPerBar`,
`BarsPerPage`, `PageCount`, `TotalSlots`) is parsed from the new
`Data/Config/toolbelt.xml` by `ToolbeltFromXml.ParseConfig`, and
`EntityPlayer.InitInventory` sizes the inventory from it. The shipped file sets
only `editorconfig` (10 slots per bar, 2 bars per page, 1 page, so 20 slots) and
states that `gameconfig` is unsupported, so stock play is 10 slots; the compiled
`PUBLIC_SLOTS`/`INVENTORY_SLOTS`/`DUMMY_SLOT_IDX`/`SHIFT_KEY_SLOT_OFFSET`
constants are gone.

`ItemStack` and `ItemValue` keep their record shape (`u16` count plus `ItemValue`
version 9), so every `items.xml`-derived fact (ids, quality, durability, mods,
cosmetic mods, metadata, stats) is unchanged. What changes is the container
framing around them.

### 5.3 Stack locations

`XUiC_ItemStack/StackLocationTypes` gained `None = 0`, moving every existing
member up by one (`Backpack` 0 to 1, `ToolBelt` 1 to 2, ... `Collector` 12 to 13).
That enum is a routing and UI label only: `ItemStackGrid` stores its location as
an `Address` (`WorldAddress` plus a byte key), `Bag.Read` takes the location from
the caller, and no `NetPackage` writes it. The only IL change is the constructor
literal at the call sites that build a bag or inventory, so a b10 save loads
unchanged and is rewritten in the new form on the next save.

### 5.4 What the client now owns

The server no longer validates inventory operations one at a time. The client
serializes `inventoryData`, `bagData` and `equipmentData` and pushes them; the
server applies them through `PlayerDataFile.ToPlayer`. `Equipment.Apply`,
`Equipment.Clone` and the transaction classes are gone. Mods and tools that
patched the b10 transaction gate have nothing to patch; a mod that wants to
validate inventory changes now has to do it at the blob boundary.

## 6. Save and on-disk formats

**The on-disk formats did change, and it is not the reader migration.**
`PooledBinaryReader` and `PooledBinaryWriter` already existed in b10
(`PooledBinaryWriter`'s IL is identical; the reader gained one helper,
`ReadExact(Span<byte>)`). They are a pooling layer over the framework classes:
`MemoryPools.poolBinaryReader`/`poolBinaryWriter`, capacity 100, a 128-byte
scratch buffer and char buffer each, and the same little-endian, 1-byte `bool`,
7-bit-length-prefixed UTF-8 encoding. `Dispose` does not flush the base stream,
and the checked save paths dispose the real stream in their own `finally`
(`WorldState.SaveLoad(String)` through a `BufferedStream`, `PlayerDataFile.Save`
through `SdFile`), so no pooled-writer data-loss window was found.

The format changes are explicit per-record version bumps plus a new
length-prefixed sub-blob container, `StreamUtils::WriteBlob`/`ReadBlob`
(`i32 length` then the bytes) with the `ToBlob`/`FromBlob`/`GetBlobData` helpers
(`StreamUtils` grows from 41 to 46 methods, 1056 to 1163 IL).

| Record | b10 | b18 | What changed |
|---|---:|---:|---|
| `WorldState.CurrentSaveVersion` (`main.ttw`) | 23 | **23** | unchanged |
| Chunk payload preamble (`ttc\0` + u32) | 47 | **47** | unchanged; `Chunk.read` floor stays 32 |
| `EntityCreationData` (chunk entity + `.ttp` ecd) | 37 | **38** | the bag is now `bool hasBagData` + an `i32`-length blob instead of an inline `Bag` |
| `TEFeatureStorage` (container tile entities) | 18 | **20** | scalar fields replaced by `ItemStackGrid`; b18 reads 19 and below through the old layout |
| `Bag` | 1 | **2** | wraps `ItemStackGrid` |
| `Equipment` | 4 | **6** | wraps the grid; b10's version-4 record takes the legacy 12-slot branch |
| `Quest.FileVersion` | 8 | **9** | new quest record |
| `PlayerDataFile` (`.ttp` header) | 59 | **62** | three blobs (`inventoryData`, `bagData`, `equipmentData`) instead of the inline containers |
| `Decoration` / blockmappings / multiblocks | 6 / 1 / 6 | unchanged | |
| Region container (`RegionFile*`, `.7rg`) | | unchanged | whole-file IL identical |
| `PlayerMetaInfo` (`.ttp` sidecar) | | unchanged | |

Compatibility is one-way. A b18 server reads a b10 world: the live check booted
b18 on a b10 `main.ttw` and logged `WRN Loaded world file from different
version: 'V 3.2.0 (b10)'` before `StartGame done`, with no load errors, and the
chunk-level legacy gates (`EntityCreationData >= 35`, `TEFeatureStorage < 19`,
`Bag` versions, `Equipment <= 5`, `.ttp` 59/60/61) read the old shapes. A b10
server cannot read a b18 world: its `>= 35` branch would read the blob length as
a `Bag` version byte. Any downgrade path must refuse, not attempt.

The remaining save-surface change is the new sign subsystem's own files, which
are not part of `WorldState`: `<save>/Player/<libraryId>.signs` (container
version 3, magic `PSGN`, 32-byte header, `i32`-length records) and
`<save>/deletedSigns.dat` (version 1, magic `DSGN`, up to 10000 `GlobalSignId`
records plus an overflow flag). `SignStoreIO` validates magic, version window,
payload length and CRC-32, writes through a `.bak` rename, and copies an
unreadable file aside as `.loadFailed`.

## 7. New subsystems and other surfaces

### 7.1 Signs

Signs are the largest feature of the release, and they are additive: neither
build has a `TileEntitySign`, the text sign (`TEFeatureSignable` +
`AuthoredText`) and the canvas composite tile entity (`TEFeatureCanvas`) are
unchanged apart from the lock rewrite, and V3.3.0 adds player-authored drawing
libraries on top.

`SignData` gains an `int32` blob version (3) ahead of its fields and a `sharing`
byte after the four next-id ints. The reader accepts versions 1 to 3 and rejects
anything else; a blob that is not version 3 is re-serialized on load. The XML
form gains an optional `sharing` attribute, written only when the value is not
`Private`.

Server state lives in `SignDataManager`: `playerSignStates` (per library),
`signLibraries` (the merged libraries) and `sessionDeletedSignIds`. The player
libraries persist through `PlayerSignStore` (one file per player library), the
deletions through `DeletedSignStore`. Writes are debounced at 60 s per library
and flushed synchronously by `SaveAndCleanupWorld`, which now waits on the async
write task. A store that fails to load is preserved and its library is
write-blocked for the session so it is not overwritten.

`SignSharing` is `Private=0`, `Selectable=1`, `Copyable=2`. It is enforced
client-side only: no server method reads it. The gallery shows other players'
signs only to allies, and copy/select gating happens in `XUiC_SignInfoWindow`.

Three findings matter to server operators and belong here rather than buried in
the code:

1. **Upload has no sender check.** `NetPackageSingleSignData` processing calls
   `SignDataManager.ProcessSignReceived`, which never reads `NetPackage.Sender`,
   and `StorePlayerSignBlob` validates only that the library id parses as a
   player id. A client can write a sign blob into another player's library
   (a new guid, or overwriting an existing one the blob names) with any sharing
   value, and the server persists it and relays it to the other clients.
2. **The join download ships every player library.** `SendSignDataToClient`
   filters only the local libraries (`[D]`, `[I]`, `[U]`); player libraries are
   sent to every joining client, private ones included. The stock UI hides them
   from non-allies afterwards, but the bytes are already on the client.
3. **Deletion is the only ownership-checked operation.** `NetPackageSignDelete`
   walks a four-branch matrix (invalid id, `[D]`, local library, another
   player's library, prefab library outside the prefab editor) before removing
   the blob. `DeletedSignStore` keeps only the id set and an overflow flag: no
   timestamp, no actor, no reason, and no `Services.Analytics` event. Successful
   deletions are not logged; rejected ones warn.

### 7.2 Asset management

`AssetManagement` is a reference-counting handle layer above the existing
loader, not a replacement: `LoadManager` and `DataLoader` are byte-identical, so
the Addressables/AssetBundle paths and the `xmlsToLoad` table are untouched.
`AssetManager::AcquireAsset` calls `LoadManager::LoadAsset<T>` and wraps the
request task; `AssetManagerLifetimed` keeps `LinkedList<Entry>` with a usage
count and a dereference time and expires entries past its timeout;
`AssetManagers::Initialize` creates one manager with `(softMax 0, timeout 5.0,
hardMax int.MaxValue)` and stores it in `AssetManagers.Items`.

`GameManager.StartGame` initializes it and `gmUpdate` gained
`AssetLoaderManager::Update` as call 11 (631 to 638 IL). The only consumer is
`ItemClass::GetModelHandle` for item meshes, replacing the b10 permanent
`renderGameObject` cache with acquire/create/release and a 5 s idle release. On a
dedicated server the driver runs but iterates an empty list while nothing is
tracked; whether a dedicated host ever acquires an item mesh was not proven.

### 7.3 Analytics

`BhvrAnalytics` is not new, but the dedicated server now sends more of it: 143
added methods, 5 new event DTOs, and new send sites. `Services.Analytics.
EventTypes::.cctor` goes from 9 to 14 entries (`quest_added` 3, `player_death` 2,
`quest_removed` 2, `equipment_usage` 0, `quest_progression` 4) and
`player_join_server` moves to schema 3. Transport is batched HTTPS through the
`BhvrAnalyticsMS` client (`POST /analytics/v1/batch`, plus the one/healthcheck/
DLQ paths), not the game wire. `player_death` carries inventory, position, biome,
POI id and name, and party locations. There is no managed opt-out: the endpoint
comes from the `BhvrAnalyticsSettings` asset, `Helper::IsDevConfig()` returns
false on a dedicated server, and only the dev host literal is present in
`data.unity3d`. The release host was not decoded, and transmission was not
observed; both are `not decoded`.

### 7.4 Console commands

`CmdMap.exe` reports 190 primary commands (188 in b10). `give` and `listitems`
(alias `li`) are added; nothing is removed or renamed. Both inherit
`DefaultPermissionLevel` 0, the most privileged level. `give` drops one item
stack at the named player's feet with a 60 s lifetime and clamps the quality
argument to at most 6 (default 6); `listitems` prints the item names that
contain a substring. The client-executable / dedicated-gated split is unchanged
at 83 / 84 / 10.

### 7.5 Spawn selection and pathing

No server-side change. `ESpawnWindowMode` is removed and
`XUiC_SpawnSelectionWindow` carries its own mode now; `RespawnProgress` gains
`WaitingForUI = 9` and `WaitingForWorld = 10` and renames member 6 to
`WaitingForSpawnChunk`. All of it is client respawn UI. The Burst
`*_BurstDirectCall`/`*_PostfixBurstDelegate` pairs the diff reports are not new
types: they exist in both builds and only the method-hash suffix changed, with
identical instruction sizes, and they belong to world generation rather than
runtime pathing. `RaycastPathing`, `AstarVoxelGrid`, `AstarManager` and
`PathFinderThread` have no delta, so no documented pathing cost claim is
invalidated.

## 8. Per-fact homes (delta map)

| Topic | Home |
|---|---|
| Machine pin (version, census, TPS, save version) | [`../../tools/data/stock_facts.json`](../../tools/data/stock_facts.json), [coverage.md](../meta/coverage.md), [re-methodology.md](../meta/re-methodology.md) §1 |
| Package registry, ids, the six removed packages, the blob bodies, the lock rework, the sign packages | [protocol.md](../network/protocol.md), [protocol-packages.md](../network/protocol-packages.md), [network.md](../network/network.md) |
| Equipment slots, backpack, hand/grid, toolbelt config, the inventory blobs, the removed transaction gate | [items.md](../gameplay/items.md), [progression.md](../gameplay/progression.md), [loot-economy.md](../gameplay/loot-economy.md), [crafting-recipes.md](../gameplay/crafting-recipes.md), [combat-damage.md](../gameplay/combat-damage.md) |
| Per-record save versions, the blob container, pooled readers, sign stores, downgrade refusal | [save-region.md](../world/save-region.md), [save-persistence.md](../world/save-persistence.md), [world-chunks.md](../world/world-chunks.md), [dedicated-misc-systems.md](../meta/dedicated-misc-systems.md) |
| Signs: data model, stores, sharing, ownership, wire | [signs.md](../gameplay/signs.md), [parties-factions.md](../social/parties-factions.md) §5.4, §7.1 above |
| Asset handles, analytics, console commands, spawn UI, Burst suffixes | [managers.md](../loop/managers.md), [architecture-map.md](../meta/architecture-map.md), [server-lifecycle.md](../admin/server-lifecycle.md), [console-commands.md](../admin/console-commands.md), [dedicated-leftovers.md](../meta/dedicated-leftovers.md), [engine-limitations.md](../meta/engine-limitations.md), [raycast-pathing.md](../entities/raycast-pathing.md), [spawning.md](../gameplay/spawning.md) |

## 9. Unknowns left open

- Server-side validation of the composite tile-entity writeback a client sends
  after picking a canvas design (claim ownership, lock token). Owned by the
  tile-entity feature sync, not decoded here.
- Whether a hostile client can poison a prefab sign library through
  `AddSignToLibraryLocal`; the path exists in IL and the persistence path for
  prefab libraries was not traced.
- Sign upload size and complexity limits: `cMaxComplexity = 600` is a render
  budget, and no server-side check was found.
- Whether the b18 readers accept the older internal serializer version bytes
  (`ItemStackGrid` version 0/1, `PlayerDataFile` 61, `Equipment` version 5);
  both builds have read branches for them but neither has a writer.
- The release analytics host, and whether a dedicated host transmits at all.
- Whether a dedicated host ever acquires an item mesh, and the per-prefab
  `CellPool` native-memory budget.
- A live V3.3.0 join capture, so the registered-id table remains inferred from
  metadata order.
- Chunk-level b10-save read on a materialised world: the legacy gates are read,
  not exercised against a real b10 chunk file.
