# Build diff: V3.3.0-b18 -> V3.4.0-b10

Generated 2026-11-05T08:56:18Z by `tools/research_diff.py`.

## Source identity

| | old | new |
|---|---|---|
| label | V3.3.0-b18 | V3.4.0-b10 |
| file | `/home/maci/.cache/zdtd-scratch/sdtd_b18/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll` | `/home/maci/.cache/zdtd-scratch/sdtd_v340/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll` |
| sha256 | `e16ff9d539b8fbf64904c0bc090d502286a62464742a9396f0455936ad0beb87` | `00a962dbbb5ef1bb454368322221f9eb4148dc2d548ed2b77244f9bda5ecc167` |
| bytes | 11697152 | 11752960 |
| version | V 3.3.0 | V 3.4.0 |
| stock wire | V3.3.0 b18 | V3.4.0 b10 |
| Steam build | unknown | 26310339 |
| depot manifest | 294422_3031329678505041777.manifest | 294422_5022117301453546978.manifest |
| depot file SHA-1 | `0b225d6ef40f5f8864f5e2400ceea1248f9416cf` (matches the local file) | `ca3f75526c7229aa8b5c2f38c4781aa6afd421c3` (matches the local file) |

## Verdict

drift: yes (stock facts 10, census 6, type metadata 186, method signatures 309, enum members 26, method bodies 927, wire parity 1, depot manifest 1625)

## Reproduce

```bash
python3 tools/research_diff.py --old /home/maci/.cache/zdtd-scratch/sdtd_b18/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll --new /home/maci/.cache/zdtd-scratch/sdtd_v340/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll --parity-old workspace/outputs/parity/parity_b18.json --parity-new workspace/outputs/parity/parity_v3.4.0.json --steam-manifest-old .scratch/manifests/294422_3031329678505041777.manifest --steam-manifest-new /home/maci/.local/share/Steam/depotcache/294422_5022117301453546978.manifest
```

## 1. Stock facts (StockFacts.exe)

10 change(s) (added 0, changed 10, removed 0)

```
~ census.methods_with_body_top_level: 44534 -> 44747
~ census.top_level_types: 4447 -> 4468
~ network.netpackage_top_level_count: 192 -> 194
~ source_identity.assembly_csharp_dll_bytes: 11697152 -> 11752960
~ source_identity.assembly_csharp_dll_sha256: e16ff9d539b8fbf64904c0bc090d502286a62464742a9396f0455936ad0beb87 -> 00a962dbbb5ef1bb454368322221f9eb4148dc2d548ed2b77244f9bda5ecc167
~ update.dump_label_suffix: v3.3.0 -> v3.4.0
~ version.build: 18 -> 10
~ version.display: V 3.3.0 -> V 3.4.0
~ version.minor: 30 -> 40
~ version.stock_wire: V3.3.0 b18 -> V3.4.0 b10
```

## 2. Census (Census.exe)

6 change(s) (added 0, changed 6, removed 0)

```
~ AllMethodsWithBody: 53796 -> 54064
~ AllTypes (incl nested): 7501 -> 7549
~ MethodsWithBody (top-level): 44534 -> 44747
~ NetPackage* (incl nested): 197 -> 199
~ NetPackage* (top-level): 192 -> 194
~ TopLevelTypes: 4447 -> 4468
```

## 3. Type metadata (FullSurface.exe)

186 change(s) (added 72, changed 72, removed 42)

```
- <>c__DisplayClass112_0 = - | class | Object | 1 | 2 | 29
~ <>c__DisplayClass113_0: - | struct | ValueType | 5 | 0 | 0 -> - | class | Object | 1 | 2 | 29
~ <>c__DisplayClass56_0: - | struct | ValueType | 4 | 0 | 0 -> - | class | Object | 2 | 3 | 75
+ <>c__DisplayClass56_1 = - | class | Object | 2 | 2 | 15
- <>c__DisplayClass743_0 = - | class | Object | 1 | 2 | 9
+ <>c__DisplayClass744_0 = - | class | Object | 1 | 2 | 9
- <GiveRewardsLater>d__129 = - | class | Object | 4 | 6 | 92
+ <GiveRewardsLater>d__130 = - | class | Object | 4 | 6 | 92
- <LogDlcEntitlementsAnalytic>d__11 = - | class | Object | 2 | 6 | 110
+ <LogDlcEntitlementsAnalytic>d__15 = - | class | Object | 2 | 6 | 110
- <LoginEventAnalyticCoroutine>d__10 = - | class | Object | 3 | 6 | 104
+ <LoginEventAnalyticCoroutine>d__14 = - | class | Object | 3 | 6 | 104
- <WaitAll>d__26 = - | class | Object | 5 | 7 | 104
+ <WaitAll>d__28 = - | class | Object | 5 | 7 | 104
+ <closeInventoryLater>d__21 = - | class | Object | 3 | 6 | 58
- <closeInventoryLater>d__24 = - | class | Object | 3 | 6 | 58
+ <closeInventoryLater>d__34 = - | class | Object | 3 | 6 | 58
- <closeInventoryLater>d__38 = - | class | Object | 3 | 6 | 58
~ <execute>d__5: - | class | Object | 6 | 6 | 827 -> - | class | Object | 5 | 6 | 757
~ <handleShuffle>d__4: - | class | Object | 4 | 6 | 221 -> - | class | Object | 4 | 6 | 217
- <resetHeadLater>d__763 = - | class | Object | 3 | 6 | 71
+ <resetHeadLater>d__764 = - | class | Object | 3 | 6 | 71
~ <startGameCo>d__139: - | class | Object | 5 | 6 | 393 -> - | class | Object | 5 | 6 | 365
- <trackLater>d__117 = - | class | Object | 4 | 6 | 129
+ <trackLater>d__118 = - | class | Object | 4 | 6 | 129
~ <worldInfoCo>d__198: - | class | Object | 20 | 7 | 730 -> - | class | Object | 20 | 7 | 729
~ ActionAddSkillPoints: GameEvent.SequenceActions | class | ActionBaseClientAction | 2 | 5 | 47 -> GameEvent.SequenceActions | class | ActionBaseClientAction | 2 | 5 | 127
- AdjustHeights_0000B9CB$BurstDirectCall = WorldGenerationEngineFinal | class | Object | 2 | 6 | 40
- AdjustHeights_0000B9CB$PostfixBurstDelegate = WorldGenerationEngineFinal | delegate | MulticastDelegate | 0 | 0 | 0
+ AdjustHeights_0000BADF$BurstDirectCall = WorldGenerationEngineFinal | class | Object | 2 | 6 | 40
+ AdjustHeights_0000BADF$PostfixBurstDelegate = WorldGenerationEngineFinal | delegate | MulticastDelegate | 0 | 0 | 0
~ AdminWebUsers: Webserver.Permissions | class | AdminSectionAbs | 1 | 11 | 229 -> Webserver.Permissions | class | AdminSectionAbs | 1 | 11 | 239
~ AuthAndLoginManager: - | class | Object | 6 | 34 | 1088 -> - | class | Object | 6 | 34 | 1093
~ Block: - | class | Object | 307 | 180 | 8425 -> - | class | Object | 307 | 180 | 8403
~ BlockShapeNew: - | class | BlockShape | 15 | 49 | 6178 -> - | class | BlockShape | 15 | 49 | 6170
+ BodyFit = GearVariants | class | Object | 3 | 1 | 12
- CalcPathBounds_0000B87B$BurstDirectCall = WorldGenerationEngineFinal | class | Object | 2 | 6 | 42
- CalcPathBounds_0000B87B$PostfixBurstDelegate = WorldGenerationEngineFinal | delegate | MulticastDelegate | 0 | 0 | 0
+ CalcPathBounds_0000B98F$BurstDirectCall = WorldGenerationEngineFinal | class | Object | 2 | 6 | 42
+ CalcPathBounds_0000B98F$PostfixBurstDelegate = WorldGenerationEngineFinal | delegate | MulticastDelegate | 0 | 0 | 0
... (146 more)
```

## 4. Method signatures (MethodList.exe)

309 change(s) (added 269, changed 0, removed 40)

```
+ CosmeticSet::.ctor = 
+ CosmeticSetRegistrar::RegisterAddressablePrefixes = 
+ CosmeticSetRegistrar::RegisterCosmeticMappings = 
+ CosmeticSets::.cctor = 
+ DroneManager::RecoverDroneForPlayer = EntityPlayer
+ EffectGroupDescription::get_GetDescriptionKey = 
+ EntityAlive::MoveEntityHeadedFlying = Vector3,Boolean
- EntityDrone::Move = Vector3,Single
+ EntityDrone::MoveEntityHeadedFlying = Vector3,Boolean
+ EntityDrone::MoveTo = Vector3,Single
+ GearVariants.BodyFit::.ctor = 
+ GearVariants.GearFitEntry::.ctor = 
+ GearVariants.GearFitMatrixSO/CopyResult::.cctor = 
+ GearVariants.GearFitMatrixSO/CopyResult::.ctor = Int32,Int32,Boolean
+ GearVariants.GearFitMatrixSO::.ctor = 
+ GearVariants.GearFitMatrixSO::AddEntry = PartFitTable,String,String
+ GearVariants.GearFitMatrixSO::ClampToValidOptions = Gender,GearPart,Func`2
+ GearVariants.GearFitMatrixSO::ClearFits = Gender,GearPart,String
+ GearVariants.GearFitMatrixSO::CopyFits = Gender,GearPart,String,String,String,CopyMode,ISet`1
+ GearVariants.GearFitMatrixSO::EnsureRegistry = 
+ GearVariants.GearFitMatrixSO::EnumerateFits = Gender,GearPart
+ GearVariants.GearFitMatrixSO::FitCount = Gender,GearPart,String
+ GearVariants.GearFitMatrixSO::GetFits = Gender,GearPart,String
+ GearVariants.GearFitMatrixSO::GetGenderTables = Gender
+ GearVariants.GearFitMatrixSO::GetVariant = Gender,GearPart,String,String
+ GearVariants.GearFitMatrixSO::GetVariantOrEmpty = String,String,String,String
+ GearVariants.GearFitMatrixSO::HasNonBaseVariant = ISet`1
+ GearVariants.GearFitMatrixSO::InvalidateIndexes = 
+ GearVariants.GearFitMatrixSO::IsEmpty = GearFitEntry
+ GearVariants.GearFitMatrixSO::ParseGender = String
+ GearVariants.GearFitMatrixSO::ParsePart = String
+ GearVariants.GearFitMatrixSO::PruneIfEmpty = PartFitTable,GearFitEntry
+ GearVariants.GearFitMatrixSO::PruneKey = Gender,GearPart,String
+ GearVariants.GearFitMatrixSO::PruneOrphans = Gender,GearPart,HashSet`1
+ GearVariants.GearFitMatrixSO::SetFit = Gender,GearPart,String,String,String,String,String
+ GearVariants.GearFitMatrixSO::SetFitInline = GearFitEntry,String,String,String
+ GearVariants.GearFitMatrixSO::SetFitMany = Gender,GearPart,String,String,IEnumerable`1,String
+ GearVariants.GearFitMatrixSO::TotalFitCount = Gender,GearPart
+ GearVariants.GearFitMatrixSO::VariantIn = GearFitEntry,String
+ GearVariants.GearFitMatrixSO::get_Instance = 
... (269 more)
```

## 5. Enum members (EnumList.exe)

26 change(s) (added 20, changed 0, removed 6)

```
+ CopyMode.Merge = 1
+ CopyMode.Replace = 0
+ EntitlementSetEnum.PopNPillsStore = 44
+ EntitlementSetEnum.RedRidingRogue = 41
+ EntitlementSetEnum.ScarletScoundrel = 39
+ EntitlementSetEnum.ShotgunMessiahStore = 45
- EntitlementSetEnum.TwitchPopNPillsStoreGearHatCosmetic = 34
- EntitlementSetEnum.TwitchPopNPillsStoreGearOutfitCosmetic = 26
- EntitlementSetEnum.TwitchShotgunMessiahStoreGearHatCosmetic = 37
- EntitlementSetEnum.TwitchShotgunMessiahStoreGearOutfitCosmetic = 29
- EntitlementSetEnum.TwitchWorkingStiffsStoreGearHatCosmetic = 38
- EntitlementSetEnum.TwitchWorkingStiffsStoreGearOutfitCosmetic = 30
+ EntitlementSetEnum.WorkingStiffsStore = 42
+ EntitlementSetEnum.WraithWoodWitch = 40
+ Gender.Female = 1
+ Gender.Male = 0
+ SkillTransactionType.Earn = 0
+ SkillTransactionType.Refund = 2
+ SkillTransactionType.Spend = 1
+ changeTypes.Learn = 0
+ changeTypes.Unlearn = 1
+ triggerReasons.ConditionAquired = 1
+ triggerReasons.ConditionRemoved = 2
+ triggerReasons.ConditionReset = 3
+ triggerReasons.PlayerDeath = 4
+ triggerReasons.ServerStartState = 0
```

## 6. Method bodies (asm_body_diff.py)

927 change(s) (added 522, changed 159, removed 246)

```
methods bak=56440 live=56716 added=522 removed=246 body-changed=159
 + __JobReflectionRegistrationOutput__694501564::System.Void __JobReflectionRegistrationOutput__694501564::CreateJobReflectionData() a39e734cdbf4fa72	11
 + __JobReflectionRegistrationOutput__694501564::System.Void __JobReflectionRegistrationOutput__694501564::EarlyInit() b04ec722187abe16	2
 + ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$BurstDirectCall::System.IntPtr ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$BurstDirectCall::GetFunctionPointer() b2bbda53ced4fe48	7
 + ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$BurstDirectCall::System.Void ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$BurstDirectCall::.cctor() aafadb429bf91410	2
 + ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$BurstDirectCall::System.Void ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$BurstDirectCall::Constructor() 1f03a6d5d2e8585d	4
 + ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$BurstDirectCall::System.Void ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$BurstDirectCall::GetFunctionPointerDiscard(System.IntPtr&) 062023d53731fc29	11
 + ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$BurstDirectCall::System.Void ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$BurstDirectCall::Initialize() 4f2d892d6af40690	1
 + ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$BurstDirectCall::System.Void ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$BurstDirectCall::Invoke(Unity.Collections.NativeArray`1<UnityEngine.Color32>&,Unity.Collections.NativeArray`1<UnityEngine.Color32>&,System.Int32,System.Int32) 9f47a2ea87b1d8c3	19
 + ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$PostfixBurstDelegate::System.IAsyncResult ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$PostfixBurstDelegate::BeginInvoke(Unity.Collections.NativeArray`1<UnityEngine.Color32>&,Unity.Collections.NativeArray`1<UnityEngine.Color32>&,System.Int32,System.Int32,System.AsyncCallback,System.Object) -	0
 + ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$PostfixBurstDelegate::System.Void ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$PostfixBurstDelegate::.ctor(System.Object,System.IntPtr) -	0
 + ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$PostfixBurstDelegate::System.Void ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$PostfixBurstDelegate::EndInvoke(System.IAsyncResult) -	0
 + ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$PostfixBurstDelegate::System.Void ChunkProviderGenerateWorldFromRaw/RoadSmooth_000056ED$PostfixBurstDelegate::Invoke(Unity.Collections.NativeArray`1<UnityEngine.Color32>&,Unity.Collections.NativeArray`1<UnityEngine.Color32>&,System.Int32,System.Int32) -	0
 + CosmeticSet::System.Void CosmeticSet::.ctor() 7e8c7cea1d6bab21	6
 + CosmeticSetRegistrar::System.Void CosmeticSetRegistrar::RegisterAddressablePrefixes() 41caaed963cce2cd	53
 + CosmeticSetRegistrar::System.Void CosmeticSetRegistrar::RegisterCosmeticMappings() 6a01d89d09acde3d	94
 + CosmeticSets::System.Void CosmeticSets::.cctor() 4f0018a2264782aa	184
 + DroneManager/<>c__DisplayClass37_0::System.Boolean DroneManager/<>c__DisplayClass37_0::<RemoveActiveDrone>b__0(EntityPlayer) a7467c447b0084fe	6
 + DroneManager/<>c__DisplayClass37_0::System.Void DroneManager/<>c__DisplayClass37_0::.ctor() 65526d2dc6a35785	3
 + DroneManager::EntityDrone DroneManager::RecoverDroneForPlayer(EntityPlayer) ff3728a22f0e6328	157
 + EffectGroupDescription::System.String EffectGroupDescription::get_GetDescriptionKey() a287e92f15ef6466	3
 + EntityAlive/<>c__DisplayClass744_0::System.Boolean EntityAlive/<>c__DisplayClass744_0::<GetOwnedEntity>b__0(OwnedEntityData) 18ede18d9d6b9c59	6
 + EntityAlive/<>c__DisplayClass744_0::System.Void EntityAlive/<>c__DisplayClass744_0::.ctor() 65526d2dc6a35785	3
 + EntityAlive/<resetHeadLater>d__764::System.Boolean EntityAlive/<resetHeadLater>d__764::MoveNext() 3126f9aa48f7943b	56
 + EntityAlive/<resetHeadLater>d__764::System.Object EntityAlive/<resetHeadLater>d__764::System.Collections.Generic.IEnumerator<System.Object>.get_Current() 3f86b07997eeae77	3
 + EntityAlive/<resetHeadLater>d__764::System.Object EntityAlive/<resetHeadLater>d__764::System.Collections.IEnumerator.get_Current() 3f86b07997eeae77	3
 + EntityAlive/<resetHeadLater>d__764::System.Void EntityAlive/<resetHeadLater>d__764::.ctor(System.Int32) 3e37a50f12cca8f7	6
 + EntityAlive/<resetHeadLater>d__764::System.Void EntityAlive/<resetHeadLater>d__764::System.Collections.IEnumerator.Reset() f3afe16cfde67b4e	2
 + EntityAlive/<resetHeadLater>d__764::System.Void EntityAlive/<resetHeadLater>d__764::System.IDisposable.Dispose() 4f2d892d6af40690	1
 + EntityAlive::System.Void EntityAlive::MoveEntityHeadedFlying(UnityEngine.Vector3,System.Boolean) 5c8af4c803130ff6	53
 + EntityDrone::System.Void EntityDrone::MoveEntityHeadedFlying(UnityEngine.Vector3,System.Boolean) 2f0bb1776cec1c3b	29
 + EntityDrone::System.Void EntityDrone::MoveTo(UnityEngine.Vector3,System.Single) 4feea7f119036376	15
 + GearVariants.BodyFit::System.Void GearVariants.BodyFit::.ctor() c9617fa276f66fd9	12
 + GearVariants.GearFitEntry::System.Void GearVariants.GearFitEntry::.ctor() 86f92f97a9ecac5f	12
 + GearVariants.GearFitMatrixSO/<>c::System.Boolean GearVariants.GearFitMatrixSO/<>c::<HasNonBaseVariant>b__19_0(System.String) d80e2d087c20947d	5
 + GearVariants.GearFitMatrixSO/<>c::System.Collections.Generic.IEnumerable`1<GearVariants.BodyFit> GearVariants.GearFitMatrixSO/<>c::<EnumerateFits>b__29_0(GearVariants.GearFitEntry) afec1c05cbb377b9	3
 + GearVariants.GearFitMatrixSO/<>c::System.Int32 GearVariants.GearFitMatrixSO/<>c::<TotalFitCount>b__30_0(GearVariants.GearFitEntry) 5d50170f7afa90af	4
 + GearVariants.GearFitMatrixSO/<>c::System.ValueTuple`3<System.String,System.String,System.String> GearVariants.GearFitMatrixSO/<>c::<EnumerateFits>b__29_1(GearVariants.GearFitEntry,GearVariants.BodyFit) 2102f803674e3b03	8
 + GearVariants.GearFitMatrixSO/<>c::System.Void GearVariants.GearFitMatrixSO/<>c::.cctor() 2288fed0dded2f37	3
 + GearVariants.GearFitMatrixSO/<>c::System.Void GearVariants.GearFitMatrixSO/<>c::.ctor() 65526d2dc6a35785	3
... (888 more)
```

## 7. Wire parity (parity_diff.py)

1 change(s) (changed 1)

```
=== PACKAGE DIFF ===
added (2): NetPackageDroneRecoveryRequest, NetPackageDroneRecoveryResponse
removed (0): -
changed wire (0):
=== ENUM DIFF ===
```

## 8. Depot manifest (steam_manifest.py)

1625 change(s) (added 76, changed 1547, removed 2)

```
gid 3031329678505041777 -> 5022117301453546978
~ 7DaysToDieServer_Data\Managed\AmplifyShaderEditor.Samples.BuiltIn.dll: size 14336 -> 14336; sha1 ac44457649e69832da638f0ad7f9fdc1514b9cb0 -> a75a10c32a11047391fcf84e0d0e9c3f9ddbd0dc
~ 7DaysToDieServer_Data\Managed\Assembly-CSharp-firstpass.dll: size 256512 -> 264704; sha1 65ef5d5780448b22a6adfa61b8ffe1001fdb51f0 -> d7d1e34b4b842c147c6fb5608c505dcabbc57594
~ 7DaysToDieServer_Data\Managed\Assembly-CSharp.dll: size 11697152 -> 11752960; sha1 0b225d6ef40f5f8864f5e2400ceea1248f9416cf -> ca3f75526c7229aa8b5c2f38c4781aa6afd421c3
~ 7DaysToDieServer_Data\Managed\AstarPathfindingProject.dll: size 532480 -> 532480; sha1 009856f0c0a0d9953b16db716bd3ed6ffa680918 -> 238c97dea839a64b6b0ba9d3da895d10f3a8c9dc
~ 7DaysToDieServer_Data\Managed\BhvrAnalytics.dll: size 23552 -> 23552; sha1 b96161bbc30ad8f1f278486f8d1fd1708f02f2ad -> d37bbdf9d98211eeb9745ce1fa5fd5652438ac9d
~ 7DaysToDieServer_Data\Managed\Discord.Sdk.dll: size 166400 -> 166912; sha1 02adf2b3a8f8889ce3707bb219da0a5965c6ee1e -> 36b8d7fd52d9717422fbc9939ab6e8efd9cdb06a
~ 7DaysToDieServer_Data\Managed\EOS.dll: size 1122816 -> 1123328; sha1 cb641c38853a61a36519ef3cf6604e5c0bd721e3 -> f322e5d69a6485c14c8a071fb2db6e11736dfdfd
~ 7DaysToDieServer_Data\Managed\HBAO.Demo.Runtime.dll: size 6144 -> 6144; sha1 df3d5e5e8fd689e9ddde3707d5ef0993739f1c10 -> 2fe8f7e807629f8e34be42f5744f42b03a587339
~ 7DaysToDieServer_Data\Managed\HBAO.Runtime.dll: size 40960 -> 40960; sha1 4fb2d761dbb241d4c9aa49f9e364d4501792c5b4 -> 4f26be8a6640fcc8e8e1a8a2910d8d7a1957f967
~ 7DaysToDieServer_Data\Managed\InControl.Examples.dll: size 30208 -> 30208; sha1 f9cd4152b0f9c48a39661550cfe3d5e242242d92 -> b861ff7283020b8bd58d9013e4b1ef3a3343f485
~ 7DaysToDieServer_Data\Managed\InControl.dll: size 656896 -> 656896; sha1 39233ebf32adefdb26466ba196ce9b05cafe3278 -> 27b3cbc5f9b4cab6e2db0f32397a0b7ad19d3785
~ 7DaysToDieServer_Data\Managed\LiteNetLib.dll: size 117248 -> 117248; sha1 a39221b0885f1500f914f888c72c5ecd3dc6f73e -> 14890ff2caf62e048c5143553e58eee80dfac069
~ 7DaysToDieServer_Data\Managed\LogLibrary.dll: size 10752 -> 10752; sha1 1e9efb37a69574603311403f327abb3b797608f2 -> 65cfecc857b4fb46732bb8cb3e12982a37e45a95
~ 7DaysToDieServer_Data\Managed\MemoryPack.dll: size 189440 -> 189440; sha1 bd44405014f96dcce713fb5016e1b53347a02d10 -> 6acca881303152e5580634172c7f4ff4c8d077a8
~ 7DaysToDieServer_Data\Managed\NCalc.dll: size 130048 -> 130048; sha1 4212576a37020eb2eddcabb4ce4f0ade04debc7c -> 59c908720b0748193b555a6f4f1485b983a11bea
~ 7DaysToDieServer_Data\Managed\NGUI.dll: size 397824 -> 397824; sha1 094ee372bfcb245b59291be1680ecb7d9240a9ba -> c9c2d90fb5003edb1f0a93d6b9aa4e2004b32747
~ 7DaysToDieServer_Data\Managed\ScreenSpaceReflections.dll: size 38400 -> 38400; sha1 6e53595541cc8f56ad4ab6c585f082c56c264daf -> 2cbe0e0008e2e46a9b9e6bedcbb24f6b4be6809e
~ 7DaysToDieServer_Data\Managed\SpaceWizards_HttpListener.dll: size 149504 -> 149504; sha1 f36dfb030784159929a3568cca128877403dfcf0 -> 617812ae56dece2e6a267abaaad49433377223a6
~ 7DaysToDieServer_Data\Managed\Unity.Addressables.dll: size 111104 -> 111104; sha1 0cc908b37d2829f97f2a3cfb743c62d4450868c8 -> 8169789b4143e25db0dcf3bd320d1487ffbd4d30
~ 7DaysToDieServer_Data\Managed\Unity.Animation.Rigging.DocCodeExamples.dll: size 6144 -> 6144; sha1 205cfe4cbac0f8a9bf6e6bfe9fe2312874622411 -> 987548cea895697617ce44909d009d407aec5af3
~ 7DaysToDieServer_Data\Managed\Unity.Animation.Rigging.dll: size 113664 -> 113664; sha1 9d1478c402530f00128eef564118a1bca3b458b9 -> 9bdd9e0a3a6463d8ca8ea9f8883de56e3da44d73
~ 7DaysToDieServer_Data\Managed\Unity.Burst.dll: size 304640 -> 304640; sha1 666e749ad848126ace430e15914ee078487a237d -> 991b063a69c4492bc4b528ca1cd6c7a55a6440f1
~ 7DaysToDieServer_Data\Managed\Unity.Collections.dll: size 446976 -> 446976; sha1 385644e40fe67a0183737eb80f56381c9ee2458c -> af64e6df5efcd93b232fa773fc61ed0f6c0fdde7
~ 7DaysToDieServer_Data\Managed\Unity.Mathematics.dll: size 741376 -> 741376; sha1 d97878d3c9cfd579b25f4133cca4a604adcfe696 -> 247b644b0c1b17ccb5f653456be941b169581dd2
~ 7DaysToDieServer_Data\Managed\Unity.MemoryProfiler.dll: size 7168 -> 7168; sha1 2979f90caf4095e66009d053aa8796cda317b563 -> 3cf14a4ce1825af8a810441d83d07077142e5240
~ 7DaysToDieServer_Data\Managed\Unity.Postprocessing.Runtime.dll: size 187904 -> 187904; sha1 a197d721d1fcc26c62d1fbf118750b6826064db6 -> 5a8e7ddef28bc909f9fe0c1d8c05c08899bac7ad
~ 7DaysToDieServer_Data\Managed\Unity.Profiling.Core.dll: size 10240 -> 10240; sha1 19dd3f3690f84000a20a1884988fabaa503b74ad -> 5818634c998b7efaa484caf8788299bdd3b46c4c
~ 7DaysToDieServer_Data\Managed\Unity.ResourceManager.dll: size 143872 -> 143872; sha1 4424a818edf8f513f151e08adb9e89edc13a2d1f -> e85075d1e0be5ff83fe0eaa055309d47095dc392
~ 7DaysToDieServer_Data\Managed\Unity.ScriptableBuildPipeline.dll: size 9216 -> 9216; sha1 621f56ac8030ab0f7a9bc751cba83ee3903a77fa -> 3e9878d7f88413af3a607f4817241e7b2e14d46f
~ 7DaysToDieServer_Data\Managed\Unity.TerrainTools.dll: size 5632 -> 5632; sha1 0da907cd35eb55831481c992d356cc15ff41a5ff -> dbfc6620c55d344246686fa76df94da567cf487a
~ 7DaysToDieServer_Data\Managed\Unity.TextMeshPro.dll: size 380928 -> 380928; sha1 5b34f6e1b362565551bcbcc7711f73e08ddbd90b -> b2429c18df92b85ac67736f92f8a7237f383016e
~ 7DaysToDieServer_Data\Managed\UnityEngine.UI.dll: size 264704 -> 264704; sha1 fe802b8d5d29f48aa4c704cec96d4883386820cd -> 588aae21dba4f2f124eea6086fb1d546c55f69ad
~ 7DaysToDieServer_Data\Managed\com.rlabrecque.steamworks.net.dll: size 406016 -> 406016; sha1 886adde8acbd5493ed9a5d886a23ad5f890c407e -> 0bc5264e745e651cd2f708c85bf72798e761d5f3
~ 7DaysToDieServer_Data\Managed\com.thenakeddev.dlss.Runtime.dll: size 5120 -> 5632; sha1 955816cd148a9012c4401796ede11a01daddb161 -> 3c6471bca00be6c75493e3e54455d4f3cec4aa3b
~ 7DaysToDieServer_Data\Managed\com.thenakeddev.fsr.Runtime.BIRP.dll: size 14336 -> 14336; sha1 ec8f40c45231fbedc0aeffd4fc85a29bc6307c71 -> 6363c9ac8155bddeb1ba2b6fe52607321b4992a4
~ 7DaysToDieServer_Data\Managed\com.thenakeddev.fsr.Runtime.dll: size 44032 -> 44032; sha1 0e6eb51e6e69f4c79d53be7decdbd5d9c35beeca -> ec2f2443e47c3a66eaf0f0a6f7d9c1f2c63fc525
~ 7DaysToDieServer_Data\Plugins\lib_burst_generated.so: size 650528 -> 650528; sha1 949d2587a8fda880f81e35511b1178187cc2c7d0 -> 24748671d3398c0ddbefe89a4290c124aa9b3908
~ 7DaysToDieServer_Data\RuntimeInitializeOnLoads.json: size 1611 -> 1773; sha1 2e253c6ec443a22fb3dc1a36918a15d687ea82de -> ca95a8be23cf1691ec9aa2f2697a527e851a1ba5
~ 7DaysToDieServer_Data\StreamingAssets\aa\AddressablesLink\link.xml: size 15723 -> 16338; sha1 6f8482fbff13b4610c695ba48fd4ad057a637094 -> 5ef9bb4f95e3e9452d10ed4196b34132a054acee
... (1586 more)
```
