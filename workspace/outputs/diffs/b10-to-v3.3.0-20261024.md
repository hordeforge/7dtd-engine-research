# Build diff: b10 -> v3.3.0

Generated 2026-10-24T15:10:14Z by `tools/research_diff.py`.

## Source identity

| | old | new |
|---|---|---|
| label | b10 | v3.3.0 |
| file | `/home/maci/.cache/zdtd-scratch/sdtd_v3.2.0/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll` | `/home/maci/.cache/zdtd-scratch/sdtd_v3.3.0/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll` |
| sha256 | `3737eedc9f143d428a69030317428c45d342be4f11006a46d72bcd7b1d0fc64d` | `e16ff9d539b8fbf64904c0bc090d502286a62464742a9396f0455936ad0beb87` |
| bytes | 11610624 | 11697152 |
| version | V 3.2.0 | V 3.3.0 |
| stock wire | V3.2.0 b10 | V3.3.0 b18 |
| Steam build | 24994542 | 25661908 |
| depot manifest | not given | 294422_3031329678505041777.manifest |
| depot file SHA-1 | not checked | `0b225d6ef40f5f8864f5e2400ceea1248f9416cf` (matches the local file) |

## Verdict

drift: yes (stock facts 13, census 7, type metadata 765, method signatures 1925, enum members 81, method bodies 5296, wire parity 1, depot manifest 0)

## Reproduce

```bash
python3 tools/research_diff.py --old /home/maci/.cache/zdtd-scratch/sdtd_v3.2.0/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll --new /home/maci/.cache/zdtd-scratch/sdtd_v3.3.0/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll --label-old b10 --label-new v3.3.0 --buildid-old 24994542 --buildid-new 25661908 --parity-old workspace/outputs/parity/parity_b10.json --parity-new /home/maci/.cache/zdtd-scratch/parity_v3.3.0.json --steam-manifest-new /home/maci/.local/share/Steam/depotcache/294422_3031329678505041777.manifest
```

## 1. Stock facts (StockFacts.exe)

note: no LiteNetLib.dll beside the old assembly, so StockFacts pinned only litenet.protocol_id there; the other litenet.* rows are missing rather than changed

13 change(s) (added 0, changed 13, removed 0)

```
~ census.gmupdate_il: 631 -> 638
~ census.methods_with_body_top_level: 44277 -> 44534
~ census.top_level_types: 4426 -> 4447
~ litenet.possible_mtu: [] -> [1024, 1164, 1392, 1404, 1424, 1432]
~ network.netpackage_top_level_count: 195 -> 192
~ provenance.baked: ["litenet.protocol_id", "litenet.header_size", "litenet.channeled_header_size", "litenet.fragment_header_size", "litenet.max_sequence", "litenet.default_window_size", "litenet.possible_mtu", "litenet.initial_mtu", "litenet.max_packet_size"] -> []
~ source_identity.assembly_csharp_dll_bytes: 11610624 -> 11697152
~ source_identity.assembly_csharp_dll_sha256: 3737eedc9f143d428a69030317428c45d342be4f11006a46d72bcd7b1d0fc64d -> e16ff9d539b8fbf64904c0bc090d502286a62464742a9396f0455936ad0beb87
~ update.dump_label_suffix: v3.2.0 -> v3.3.0
~ version.build: 10 -> 18
~ version.display: V 3.2.0 -> V 3.3.0
~ version.minor: 20 -> 30
~ version.stock_wire: V3.2.0 b10 -> V3.3.0 b18
```

## 2. Census (Census.exe)

7 change(s) (added 0, changed 7, removed 0)

```
~ AllMethodsWithBody: 53418 -> 53796
~ AllTypes (incl nested): 7451 -> 7501
~ GameManager.gmUpdate IL: 631 -> 638
~ MethodsWithBody (top-level): 44277 -> 44534
~ NetPackage* (incl nested): 200 -> 197
~ NetPackage* (top-level): 195 -> 192
~ TopLevelTypes: 4426 -> 4447
```

## 3. Type metadata (FullSurface.exe)

765 change(s) (added 167, changed 463, removed 135)

```
~ <<OnActivated>g__UseItemWithAnimationCoroutine\: 0>d | - | class | Object | 5 | 6 | 145 -> 0>d | - | class | Object | 4 | 6 | 147
+ <>c__DisplayClass106_0 = - | struct | ValueType | 6 | 0 | 0
- <>c__DisplayClass108_0 = - | struct | ValueType | 5 | 0 | 0
~ <>c__DisplayClass109_0: - | class | Object | 2 | 2 | 20 -> - | class | Object | 1 | 2 | 9
+ <>c__DisplayClass112_0 = - | class | Object | 1 | 2 | 29
~ <>c__DisplayClass113_0: - | struct | ValueType | 1 | 0 | 0 -> - | struct | ValueType | 5 | 0 | 0
+ <>c__DisplayClass114_0 = - | class | Object | 2 | 2 | 20
- <>c__DisplayClass118_1 = - | class | Object | 2 | 2 | 42
+ <>c__DisplayClass120_0 = - | class | Object | 1 | 2 | 18
+ <>c__DisplayClass120_1 = - | class | Object | 2 | 2 | 42
- <>c__DisplayClass125_0 = - | class | Object | 2 | 2 | 17
+ <>c__DisplayClass127_0 = - | class | Object | 2 | 3 | 83
- <>c__DisplayClass134_0 = - | class | Object | 1 | 2 | 16
- <>c__DisplayClass138_0 = - | struct | ValueType | 6 | 0 | 0
- <>c__DisplayClass166_0 = - | class | Object | 2 | 2 | 21
- <>c__DisplayClass166_1 = - | class | Object | 1 | 2 | 8
+ <>c__DisplayClass167_0 = - | class | Object | 2 | 2 | 21
+ <>c__DisplayClass167_1 = - | class | Object | 1 | 2 | 8
- <>c__DisplayClass16_0`2 = - | class | Object | 1 | 2 | 10
- <>c__DisplayClass16_1`1 = - | class | Object | 1 | 2 | 13
- <>c__DisplayClass16_2`1 = - | class | Object | 1 | 2 | 26
+ <>c__DisplayClass175_0 = - | class | Object | 2 | 3 | 25
~ <>c__DisplayClass176_0: - | class | Object | 2 | 3 | 25 -> - | class | Object | 2 | 2 | 20
- <>c__DisplayClass177_0 = - | class | Object | 2 | 2 | 20
+ <>c__DisplayClass18_0`2 = - | class | Object | 1 | 2 | 10
+ <>c__DisplayClass18_1`1 = - | class | Object | 1 | 2 | 13
+ <>c__DisplayClass18_2`1 = - | class | Object | 1 | 2 | 26
+ <>c__DisplayClass18_3`2 = - | class | Object | 1 | 2 | 11
+ <>c__DisplayClass18_4`2 = - | class | Object | 1 | 2 | 12
- <>c__DisplayClass197_0 = - | class | Object | 1 | 2 | 7
+ <>c__DisplayClass198_0 = - | class | Object | 1 | 2 | 7
~ <>c__DisplayClass19_0: - | class | Object | 2 | 2 | 12 -> - | class | Object | 1 | 2 | 9
- <>c__DisplayClass19_0`2 = - | class | Object | 1 | 2 | 11
- <>c__DisplayClass203_0 = - | class | Object | 1 | 2 | 9
+ <>c__DisplayClass204_0 = - | class | Object | 1 | 2 | 9
- <>c__DisplayClass20_0`1 = - | class | Object | 1 | 2 | 13
+ <>c__DisplayClass211_0 = - | class | Object | 3 | 5 | 102
- <>c__DisplayClass215_0 = - | class | Object | 1 | 2 | 7
+ <>c__DisplayClass216_0 = - | class | Object | 1 | 2 | 7
- <>c__DisplayClass221_0 = - | class | Object | 2 | 2 | 12
... (725 more)
```

## 4. Method signatures (MethodList.exe)

1925 change(s) (added 940, changed 342, removed 643)

```
~ AIDirector::ComponentsLoad: BinaryReader,Int32 -> PooledBinaryReader,Int32
~ AIDirector::ComponentsSave: BinaryWriter -> PooledBinaryWriter
~ AIDirector::Load: BinaryReader -> PooledBinaryReader
~ AIDirector::Save: BinaryWriter -> PooledBinaryWriter
~ AIDirectorAirDropComponent::Read: BinaryReader,Int32 -> PooledBinaryReader,Int32
~ AIDirectorAirDropComponent::Write: BinaryWriter -> PooledBinaryWriter
~ AIDirectorBloodMoonComponent::Read: BinaryReader,Int32 -> PooledBinaryReader,Int32
~ AIDirectorBloodMoonComponent::Write: BinaryWriter -> PooledBinaryWriter
~ AIDirectorChunkData::Read: BinaryReader,Int32 -> PooledBinaryReader,Int32
~ AIDirectorChunkData::Write: BinaryWriter -> PooledBinaryWriter
~ AIDirectorChunkEvent::Read: BinaryReader -> PooledBinaryReader
~ AIDirectorChunkEvent::Write: BinaryWriter -> PooledBinaryWriter
~ AIDirectorChunkEventComponent::Read: BinaryReader,Int32 -> PooledBinaryReader,Int32
~ AIDirectorChunkEventComponent::Write: BinaryWriter -> PooledBinaryWriter
~ AIDirectorComponent::Read: BinaryReader,Int32 -> PooledBinaryReader,Int32
~ AIDirectorComponent::Write: BinaryWriter -> PooledBinaryWriter
~ AIDirectorPlayerInventory/ItemId::Read: BinaryReader -> PooledBinaryReader
~ AIDirectorPlayerInventory/ItemId::Write: BinaryWriter -> PooledBinaryWriter
~ AIDirectorWanderingHordeComponent::Read: BinaryReader,Int32 -> PooledBinaryReader,Int32
~ AIDirectorWanderingHordeComponent::Write: BinaryWriter -> PooledBinaryWriter
~ ActionTarget::Read: BinaryReader -> PooledBinaryReader
~ ActionTarget::Write: BinaryWriter -> PooledBinaryWriter
~ AllyStore::Read: BinaryReader -> PooledBinaryReader
~ AllyStore::Write: BinaryWriter -> PooledBinaryWriter
+ AssetLoaderManager::.ctor = 
+ AssetLoaderManager::Add = AssetManager
+ AssetLoaderManager::Cleanup = 
+ AssetLoaderManager::Update = 
+ AssetManagement.AssetHandle`1::.ctor = AssetManager,String,AssetRequestTask`1
+ AssetManagement.AssetHandle`1::CreateInstance = 
+ AssetManagement.AssetHandle`1::IsComplete = 
+ AssetManagement.AssetHandle`1::IsValid = 
+ AssetManagement.AssetHandle`1::Release = 
+ AssetManagement.AssetHandle`1::WaitForComplete = 
+ AssetManagement.AssetHandle`1::get_Asset = 
+ AssetManagement.AssetManager::.ctor = 
+ AssetManagement.AssetManager::AcquireAsset = String,Boolean
+ AssetManagement.AssetManager::AcquireAssetAsync = String,Boolean
+ AssetManagement.AssetManagerLifetimed/Entry::.ctor = String,IAssetHandle
+ AssetManagement.AssetManagerLifetimed::.ctor = Int32,Double,Int32
... (1885 more)
```

## 5. Enum members (EnumList.exe)

81 change(s) (added 31, changed 34, removed 16)

```
- ActiveIndex.ALL_OFF = -1
- ActiveIndex.NOT_INITIALIZED = -2
- ESpawnWindowMode.Progress = 0
- ESpawnWindowMode.SpawnSelection = 1
+ EntitlementSetEnum.HalloweenCosmetic = 19
+ EntitlementSetEnum.OktoberfestCosmetic = 18
~ EntitlementSetEnum.TwitchCrackABookStoreGearHatCosmetic: 29 -> 31
~ EntitlementSetEnum.TwitchCrackABookStoreGearOutfitCosmetic: 21 -> 23
~ EntitlementSetEnum.TwitchMoPowerStoreGearHatCosmetic: 30 -> 32
~ EntitlementSetEnum.TwitchMoPowerStoreGearOutfitCosmetic: 22 -> 24
~ EntitlementSetEnum.TwitchPassNGasStoreGearHatCosmetic: 31 -> 33
~ EntitlementSetEnum.TwitchPassNGasStoreGearOutfitCosmetic: 23 -> 25
~ EntitlementSetEnum.TwitchPimpHatBlueCosmetic: 18 -> 20
~ EntitlementSetEnum.TwitchPimpHatPurpleCosmetic: 19 -> 21
~ EntitlementSetEnum.TwitchPopNPillsStoreGearHatCosmetic: 32 -> 34
~ EntitlementSetEnum.TwitchPopNPillsStoreGearOutfitCosmetic: 24 -> 26
~ EntitlementSetEnum.TwitchSavageCountryStoreGearHatCosmetic: 33 -> 35
~ EntitlementSetEnum.TwitchSavageCountryStoreGearOutfitCosmetic: 25 -> 27
~ EntitlementSetEnum.TwitchShamwayStoreGearHatCosmetic: 34 -> 36
~ EntitlementSetEnum.TwitchShamwayStoreGearOutfitCosmetic: 26 -> 28
~ EntitlementSetEnum.TwitchShotgunMessiahStoreGearHatCosmetic: 35 -> 37
~ EntitlementSetEnum.TwitchShotgunMessiahStoreGearOutfitCosmetic: 27 -> 29
~ EntitlementSetEnum.TwitchWatcherCosmetic: 20 -> 22
~ EntitlementSetEnum.TwitchWorkingStiffsStoreGearHatCosmetic: 36 -> 38
~ EntitlementSetEnum.TwitchWorkingStiffsStoreGearOutfitCosmetic: 28 -> 30
- EnumOperation.SetAbsolute = 0
- EnumOperation.SetAll = 2
- EnumOperation.SetRelative = 1
+ EquipmentSlotType.Armor = 1
+ EquipmentSlotType.BiomeGear = 2
+ EquipmentSlotType.Clothing = 3
+ EquipmentSlotType.None = 0
+ EquipmentSlots.Backpack = 12
~ EquipmentSlots.Count: 12 -> 13
~ EquipmentSlots.None: 12 -> 13
- HeldItemState.Holding = 2
- HeldItemState.Holstering = 3
- HeldItemState.None = 0
- HeldItemState.Unholstering = 1
+ HoldingMode.Bare = 1
... (41 more)
```

## 6. Method bodies (asm_body_diff.py)

5296 change(s) (added 2079, changed 1514, removed 1703)

```
methods bak=56064 live=56440 added=2079 removed=1703 body-changed=1514
 + __JobReflectionRegistrationOutput__4075401495::System.Void __JobReflectionRegistrationOutput__4075401495::CreateJobReflectionData() a39e734cdbf4fa72	11
 + __JobReflectionRegistrationOutput__4075401495::System.Void __JobReflectionRegistrationOutput__4075401495::EarlyInit() d7368f5a0c697158	2
 + ActionTarget::ActionTarget ActionTarget::Read(PooledBinaryReader) b9dec1d7f65275bb	23
 + ActionTarget::System.Void ActionTarget::Write(PooledBinaryWriter) d2bf178d1082d120	23
 + AIDirector::System.Void AIDirector::ComponentsLoad(PooledBinaryReader,System.Int32) 6276d121cca5ded1	22
 + AIDirector::System.Void AIDirector::ComponentsSave(PooledBinaryWriter) 3fe9dca7327ecbb7	21
 + AIDirector::System.Void AIDirector::Load(PooledBinaryReader) 5cd4f4835b43f015	14
 + AIDirector::System.Void AIDirector::Save(PooledBinaryWriter) 319583c326644625	7
 + AIDirectorAirDropComponent::System.Void AIDirectorAirDropComponent::Read(PooledBinaryReader,System.Int32) 34154786a9a5913e	83
 + AIDirectorAirDropComponent::System.Void AIDirectorAirDropComponent::Write(PooledBinaryWriter) 13a0c921c02bae5c	72
 + AIDirectorBloodMoonComponent::System.Void AIDirectorBloodMoonComponent::Read(PooledBinaryReader,System.Int32) 810e40ad53650a02	38
 + AIDirectorBloodMoonComponent::System.Void AIDirectorBloodMoonComponent::Write(PooledBinaryWriter) b26f3084ee320b52	20
 + AIDirectorChunkData::System.Void AIDirectorChunkData::Read(PooledBinaryReader,System.Int32) 2d0314a64e69e640	36
 + AIDirectorChunkData::System.Void AIDirectorChunkData::Write(PooledBinaryWriter) bf7f669d2beef8e3	35
 + AIDirectorChunkEvent::AIDirectorChunkEvent AIDirectorChunkEvent::Read(PooledBinaryReader) 0066244d4e5020b3	39
 + AIDirectorChunkEvent::System.Void AIDirectorChunkEvent::Write(PooledBinaryWriter) c9417163f71a04b1	32
 + AIDirectorChunkEventComponent::System.Void AIDirectorChunkEventComponent::Read(PooledBinaryReader,System.Int32) 6dae63c096e512fe	37
 + AIDirectorChunkEventComponent::System.Void AIDirectorChunkEventComponent::Write(PooledBinaryWriter) 53e11f13a3003988	33
 + AIDirectorComponent::System.Void AIDirectorComponent::Read(PooledBinaryReader,System.Int32) 4f2d892d6af40690	1
 + AIDirectorComponent::System.Void AIDirectorComponent::Write(PooledBinaryWriter) 4f2d892d6af40690	1
 + AIDirectorPlayerInventory/ItemId::AIDirectorPlayerInventory/ItemId AIDirectorPlayerInventory/ItemId::Read(PooledBinaryReader) c748ae3dbbd53717	10
 + AIDirectorPlayerInventory/ItemId::System.Void AIDirectorPlayerInventory/ItemId::Write(PooledBinaryWriter) e291939fa4a0ba47	11
 + AIDirectorWanderingHordeComponent::System.Void AIDirectorWanderingHordeComponent::Read(PooledBinaryReader,System.Int32) db647972e6cb9cf7	16
 + AIDirectorWanderingHordeComponent::System.Void AIDirectorWanderingHordeComponent::Write(PooledBinaryWriter) 7309bfbd9763c12c	12
 + AllyStore::System.Void AllyStore::Read(PooledBinaryReader) 2ee6fa5eb96a66f0	35
 + AllyStore::System.Void AllyStore::Write(PooledBinaryWriter) ad5b04718efd4277	101
 + AssetLoaderManager::System.Void AssetLoaderManager::.ctor() 39fa8bfbf16375b6	9
 + AssetLoaderManager::System.Void AssetLoaderManager::Add(AssetManagement.AssetManager) 3c8dd043fece4333	5
 + AssetLoaderManager::System.Void AssetLoaderManager::Add(AssetManagement.AssetManagerLifetimed) 428b23e79aa9a70e	9
 + AssetLoaderManager::System.Void AssetLoaderManager::Cleanup() e8d117ca86ea9771	23
 + AssetLoaderManager::System.Void AssetLoaderManager::Update() 17083dbbb5198960	17
 + AssetManagement.AssetHandle`1::AssetManagement.InstanceHandle`1<T> AssetManagement.AssetHandle`1::CreateInstance() 8166b62c105f3423	30
 + AssetManagement.AssetHandle`1::System.Boolean AssetManagement.AssetHandle`1::IsComplete() 1fa19b237a148f1d	9
 + AssetManagement.AssetHandle`1::System.Boolean AssetManagement.AssetHandle`1::IsValid() 3ded692e6cbd800e	5
 + AssetManagement.AssetHandle`1::System.Void AssetManagement.AssetHandle`1::.ctor(AssetManagement.AssetManager,System.String,LoadManager/AssetRequestTask`1<T>) 8bbf205f34cc08ac	12
 + AssetManagement.AssetHandle`1::System.Void AssetManagement.AssetHandle`1::Release() 0c7cbde81c2cf6d9	21
 + AssetManagement.AssetHandle`1::System.Void AssetManagement.AssetHandle`1::WaitForComplete() c3152983ea1038a7	8
 + AssetManagement.AssetHandle`1::T AssetManagement.AssetHandle`1::get_Asset() 9490de0aafd616b3	11
 + AssetManagement.AssetManager::AssetManagement.AssetHandle`1<T> AssetManagement.AssetManager::AcquireAsset(System.String,System.Boolean) 736772c452bf1aee	24
... (5257 more)
```

## 7. Wire parity (parity_diff.py)

1 change(s) (changed 1)

```
=== PACKAGE DIFF ===
added (3): NetPackageLockTarget, NetPackageSignDelete, NetPackageSingleSignData
removed (6): NetPackageInventoryDataRequest, NetPackageInventoryDataResponse, NetPackageInventoryTransactionRequest, NetPackageInventoryTransactionResponse, NetPackageLockRequest, NetPackageLockResponse
changed wire (4):
  NetPackageItemActionEffects
    read OLD ReadInt32;ReadByte;ReadByte;ReadByte;ReadBoolean;SU.ReadVector3;SU.ReadVector3;ReadInt32;
    read NEW ReadInt32;ReadSByte;ReadByte;ReadByte;ReadBoolean;SU.ReadVector3;SU.ReadVector3;ReadInt32;
  NetPackagePlayerEquipment
    read OLD NetPackageEntityTargeted.read;Equipment.Read;
    read NEW NetPackageEntityTargeted.read;SU.ReadBlob;
    write OLD NetPackageEntityTargeted.write;Equipment.Write;
    write NEW NetPackageEntityTargeted.write;SU.WriteBlob;
  NetPackagePlayerInventory
    read OLD ReadBoolean;ReadBoolean;Bag.Read;ReadBoolean;ReadInt32;ReadInt32;ReadInt32;ReadBoolean;
    read NEW ReadBoolean;SU.ReadBlob;ReadBoolean;SU.ReadBlob;ReadBoolean;SU.ReadBlob;ReadBoolean;
    write OLD NetPackage.write;Write;Write;Bag.Write;Write;Write;Write;Write;Write;
    write NEW NetPackage.write;Write;SU.WriteBlob;Write;SU.WriteBlob;Write;SU.WriteBlob;Write;
  NetPackageSignDataResponse
    read OLD ReadBoolean;ReadInt32;ReadBytes;
    read NEW ReadBoolean;ReadInt32;
=== ENUM DIFF ===
```

## 8. Depot manifest (steam_manifest.py)

not measured: pass --steam-manifest-old and --steam-manifest-new
