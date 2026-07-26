# Audit: docs/save-persistence.md + docs/chunk-providers.md vs Assembly-CSharp IL

**Verdict: 4 issues (1 CRITICAL, 2 MAJOR, 1 MINOR).** Both docs are otherwise
highly accurate; every dead-code, provider-selection, and caller claim I checked
reproduced exactly in the IL. All commands below were run against the stable
dedicated DLL (`ASM="/home/maci/.local/share/Steam/steamapps/common/7 Days to Die
Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll"`). A full IL
dump used for grepping lives at `~/.cache/7dtd-audit/all-il.txt`
(`mono tools/bin/DumpMethod.exe "$ASM" "" "" ~/.cache/7dtd-audit/all-il.txt`,
53011 method bodies).

---

## Findings

### F1. CRITICAL (format) — chunk-providers.md §5: DecoObject.Write field list omits `realYPos`

> "`DecoObject` is `{Vector3i pos, float realYPos, BlockValue bv, DecoState
> state}` (`Write` serializes pos as packed uint64, raw block data, state byte,
> and registers the block in the save's `NameIdMapping`)."

The serialized record enumeration skips a 4-byte field. Ground truth
(`grep -A40 '^// DecoObject::Write' ~/.cache/7dtd-audit/all-il.txt`):

```
IL_0007: call System.UInt64 GameUtils::Vector3iToUInt64(Vector3i)   // pos, u64
IL_0013: ldfld Single DecoObject::realYPos
IL_0019: callvirt Write(System.Single)                              // realYPos, f32  <-- omitted
IL_0025: ldfld UInt32 BlockValue::rawData
IL_002A: callvirt Write(System.UInt32)                              // rawData, u32
IL_0031: ldfld DecoState DecoObject::state
IL_0037: callvirt Write(System.Byte)                                // state, u8
```

Actual record order: `u64 pos, f32 realYPos, u32 rawData, u8 state`, then the
NameIdMapping registration. Anyone parsing `decoration.7dt` records from the
doc's sentence misaligns by 4 bytes after the first field. **Fix:** insert
"`realYPos` float" between the packed pos and raw block data in the Write list.

### F2. MAJOR (wrong behavior) — chunk-providers.md §3.1/§4.1: base Init runs FIRST, not last

> §3.1: "Subclass Inits run their file loading first and call this via `<>n__0` (§4)."
> §4.1: "`Init` (coroutine `<Init>d__17`, calling base Init at the end) ..."

Both statements invert the order. Ground truth
(`sed -n '783205,783245p' ~/.cache/7dtd-audit/all-il.txt`,
`ChunkProviderGenerateWorldFromRaw/<Init>d__17::MoveNext` IL=1032): state 0 is

```
IL_0066: ...state 0 entry...
IL_0080: call System.Collections.IEnumerator ChunkProviderGenerateWorldFromRaw::<>n__0(World)
IL_0085: stfld Object <Init>d__17::<>2__current   // yield return base.Init(_world)
```

i.e. `yield return base.Init(_world)` is the FIRST statement; all file loading
(dtm/.raw at IL_013B+, biomes at IL_040C, splats, `RegionFileManager` ctor at
IL_08F1) happens afterwards. Same for `ChunkProviderGenerateWorldFromImage/<Init>d__6`
(`<>n__0` at IL_003D in state 0; `sed -n '781130,781175p'`). Corroboration: the
`GenerateChunks` thread started by base Init guards
`if (m_RegionFileManager == null) return 15` (`DumpMethod "$ASM"
ChunkProviderGenerateWorld GenerateChunksThread`, IL_0008-IL_0012), which only
makes sense because the thread starts before the subclass creates the region
manager. **Fix:** state that base Init (prefab decorator, spawn points,
GenerateChunks thread) is yielded first, then the subclass loads its files; the
thread idles on the null region manager until the subclass finishes.

### F3. MAJOR (wrong behavior) — chunk-providers.md §4.4: GenerateFlat does NOT delete the region dir

> "deletes any stale save region dir and `decoration.7dt` on Init"

Only `decoration.7dt` is deleted. Ground truth
(`ChunkProviderGenerateFlat/<Init>d__9::MoveNext` IL=532, lines 778785-779238 of
the full dump): `SdFile::Delete(GetSaveGameDir() + "/decoration.7dt")` at
IL_012F, but the region dir is only existence-checked:

```
IL_013A: callvirt System.Boolean WorldBase::IsEditor()
IL_0141: call System.String GameIO::GetSaveGameRegionDir()
IL_0146: call System.Boolean SdDirectory::Exists(System.String)
IL_014B: ldc.i4.0 / ceq          // bool = IsEditor() || !Exists(regionDir)
...
IL_015D: brfalse.s IL_0199       // gates the playtest-prefab load branch
```

`grep -c "Delete" ` over the whole MoveNext body returns 1 (the decoration.7dt
delete); there is no `SdDirectory::Delete` anywhere in `ChunkProviderGenerateFlat`
(checked all 13 method bodies, lines 778312-779238). **Fix:** "deletes stale
`decoration.7dt`; the save region dir is only existence-checked (together with
IsEditor) to decide whether to load the playtest prefab into the cluster."

### F4. MINOR (label) — save-persistence.md §2.2: `IsParentOf` IL count

> "`IsParentOf`/`GetChildPath`/`TryGetParentPath` (string-segment operations on
> the normalized form, IL=42/9/33)"

`SaveDataManagedPath::IsParentOf` is IL=6; the IL=42 body is the
compiler-generated local function `<IsParentOf>g__IsParentOfInternal|28_0`
(`grep '^// SaveDataManagedPath::' ~/.cache/7dtd-audit/all-il.txt`). GetChildPath=9
and TryGetParentPath=33 are correct. **Fix:** "IL=6 (helper 42)/9/33".

---

## Spot-verified CONFIRMED

### save-persistence.md

- **Dedicated always runs SaveDataManager_Placeholder; management never activates.**
  `SaveDataUtils/<InitStaticCoroutine>d__17::MoveNext` IL=96 (dump lines
  704762-704858): `s_isManagementEnabled = (MultiPlatform.SaveGameProvider != null)`
  (IL_004C), null branch → `SaveDataManager_Placeholder::Instance` (IL_009E).
  The only call to `AbsPlatform::set_SaveGameProvider` in the entire assembly is
  in `Platform.AbsPlatform::Destroy` (`FindCallers.exe "$ASM" AbsPlatform
  set_SaveGameProvider` + full-dump grep for the call and for
  `stfld ...<SaveGameProvider>k__BackingField`: setter body only). So the flag
  stays false on dedicated.
- **`TryGetManagedPath` IL=47 with immediate false when management disabled**
  (IL_0000-IL_000B); `IsManaged` IL=16 same guard; group 2 = relative path.
- **Regex options 536** (`ldc.i4 536` twice in `UpdatePaths` IL=61) =
  Compiled(8)|Singleline(16)|CultureInvariant(512); patterns `^(?:`,
  `(?:$|[\\/](?<2>.*)$)`, `(?:$|[\\/])` all present as `ldstr`.
- **SaveDataType table:** enum values 0-3 (`EnumList`), `GetPathRaw` IL=26 returns
  ``/`Saves`/`SavesLocal`/`GeneratedWorlds`, `GetSlotPathDepth` IL=19 returns
  0/2/1/1 (`DumpMethod "$ASM" SaveDataTypeExtensions ""`).
- **Path model IL sizes:** ctor(String,Boolean)=64, TryFormatPath=106,
  GetSaveDataType=50, GetSlotPathRange=77, GetPathRelativeToSlotRange=54,
  GetOriginalPath=6 and its body is exactly
  `Path.Combine(s_saveDataRootPathPrefix, PathRelativeToRoot)` →
  `GameIO.GetNormalizedPath`.
- **SaveDataSlot `d` sentinel:** ctor(SaveDataType,StringSpan) IL=54 contains
  `ldstr /d` twice plus the "Expected slot path to be" guard strings.
- **`.bup` backup mapping:** `GetBackupPath` IL=6 appends literal `.bup`;
  `GetRestorePath` IL=24 checks `EndsWith(".bup")` and throws otherwise;
  `InitRestoreBackups` IL=67 scans `ldstr *.bup`.
- **`SaveDataManager_Minimal` has no callers:** full-dump grep for
  `SaveDataManager_Minimal` outside its own type = only self (`get_Instance`
  ctor call). `SetSaveDataManagerOverride`/`SetSaveDataPrefsOverride`: no
  in-assembly call sites (FindCallers + grep).
- **Placeholder is System.IO pass-through:** `ManagedFileOpen` IL=7 =
  `File.Open(GetOriginalPath(), ...)`.
- **`IsPriorityFilePath` IL=17:** `Type == Saves(1)` && `PathRelativeToSlot`
  IndexOf("Region") == 0.
- **`AppliesSaveSizeLimit`:** SaveDataManager returns 1; base and placeholder
  return 0 (all IL=2).
- **5 MiB reserve:** `SaveInfoProvider::GetPlatformReservedSizeBytes` IL=3 =
  `ldc.i4 5242880; conv.i8`.
- **`UsesDataLimit` IL=4 = `storage == Roaming(1)`**; `UserDataStorageType`
  DeviceLocal=0/Roaming=1 (EnumList).
- **Prefs selection:** `LaunchPrefs.PlayerPrefsFile` constructed with default
  `DeviceFlags::IsCurrent(24)` (dump line 1316846ff); DeviceFlag 24 =
  XBoxSeriesS(8)|XBoxSeriesX(16) (EnumList). File variant builds
  `Path.Join(GetUserGameDataDir(), "prefs.cfg")` → `SaveDataPrefsFile`; else
  `SaveDataPrefsUnity.INSTANCE`. `.cctor` installs `SaveDataPrefsUninitialized.INSTANCE`.
- **`SaveDataUtils.Destroy` caller:** only
  `Platform.PlatformApplicationManager::RestartProcess` (dump line 1790028).
- **Boot wiring:** `GameEntrypoint/<EntrypointCoroutineInternal>d__9::MoveNext`
  yields `SaveDataUtils::InitStaticCoroutine()` (line 1270195).
- **GameIO:** `GetSaveGameDir()` IL=8 = GamePrefs.GetString(33) + GetString(31) +
  GetInt(294); EnumGamePrefs GameWorld=33, GameName=31, GameSaveStorageType=294
  (EnumList).
- **§6 caller table:** CommitAsync called from `World::Save` (after
  `WorldState::Save` at IL_006C/IL_0089), `GamePrefs::Save`,
  `XUiC_DataManagement`/`XUiC_MainMenu`/SandboxOptionManager (UI);
  `ISaveDataManager::Cleanup` from `GameManager::Cleanup` and
  `SaveDataUtils::Destroy`; `ClearResources` from `startGameCo` (plus
  `worldInfoCo`, client join, and `XUiC_DMWorldsList` sibling);
  Register/Deregister from `RegionFileManager::.ctor`/`::Cleanup`;
  `AppliesSaveSizeLimit` from `RegionFileManager::DoSaveChunks`; `sdminfo` is
  `ConsoleCmdSaveDataManagerInfo::getCommands` (`ldstr sdminfo`).
- **SaveInfoProvider:** Instance=6, RefreshIfDirty=194, ProcessLocalWorlds=136,
  ProcessLocalWorldSaves(storage)=254, ProcessSaveEntry=182 (reads `/main.ttw`,
  `archived.flag`, warns except `WorldEditor`/`PrefabEditor`),
  ProcessPlayerEntries=206 (walks `/Player`), ProcessRemoteWorldSaves(storage)=276
  (reads `RemoteWorldInfo.xml` in `worldInfoCo`-adjacent path);
  `xuiDmConflicted`/`xuiDmDeleted` strings in `ProcessLocalWorldSaves`;
  `WorldEntryInfo::ShouldBeMovedWithSave` IL=16 = UsesDataLimit(target) &&
  Moveable && storage differs. `EAbstractedLocationType` UserDataPath=2, Mods=3,
  GameData=4 (EnumList).

### chunk-providers.md

- **Provider selection (the KEY claim):**
  `ChunkCluster/<Init>d__45::MoveNext` IL=148 (`DumpMethod "$ASM" "Init>d__45"
  MoveNext`): `switch(providerId - 1)` → 1: `ChunkProviderDisc`; 2:
  `ChunkProviderGenerateWorldFromImage`; 3: `IsFixedSize ? ChunkProviderDummy :
  ChunkProviderGenerateWorldFromRaw(..., true, true)`; 4:
  `ChunkProviderGenerateWorldFromRaw(..., false, false)`; 5/6: nothing
  (dead enum entries); 7: `ChunkProviderGenerateFlat`. FromRaw ctor signature is
  `(String,AbstractedLocation,Boolean _bClientMode,Boolean _bFixedWaterLevel)`.
  `EnumChunkProviderId` values 0-7 exactly as tabled (EnumList).
- **GetProviderId overrides:** Disc→1, Image→2, Raw→4, Flat→7 (all IL=2,
  `ldc.i4.N`); base `ChunkProviderAbstract::GetProviderId` IL=2 → 0; base
  `GetChunkProtectionLevel` IL=2 → 0.
- **Dedicated = FromRaw:** `World/<LoadWorld>d__73::MoveNext` IL_0566-IL_057B:
  `IsServer ? worldState.providerId : 3`; `WorldState::.ctor` defaults
  `providerId = 1` (Disc) at IL_0012.
- **Interface call map:** callvirt sites for Update/SaveAll/StopUpdate+Cleanup/
  UnloadChunk/SaveRandomChunks/RebuildTerrain resolve to `GameManager::gmUpdate`,
  `ChunkCluster::Save`, `ChunkCluster::Cleanup` (2 calls), `ChunkCluster::UnloadChunk`,
  `GameManager::UpdateTick`, `World::RebuildTerrain` — exactly the doc's list.
- **GenerateChunksThread:** `World.GetNextChunkToProvide()` → fallback
  `DynamicMeshThread.GetNextChunkToLoad()` → `ldc.i4.s 15` idle return (15 ms),
  guard `m_RegionFileManager == null → 15`.
- **`RequestChunk`:** bClientMode early `ret` (IL_0006-IL_0008), enqueues
  `WorldChunkCache.MakeChunkKey` under the list SyncRoot; the ONLY external
  caller of `IChunkProvider::RequestChunk(Int32,Int32)` in 53k method bodies is
  `TerrainMapGenerator::GenerateTerrain` (full-dump grep).
- **`ChunkManager::GetNextChunkToProvide`:** scans `m_AllChunkPositions` bucket
  list, then `IChunkProvider::GetRequestedChunks()`.
- **GenerateSingleChunk pipeline:** ContainsChunkSync skip → RegionFileManager
  GetChunkSync reuse → `MemoryPools.PoolChunks` alloc →
  `Utils::RandomFromSeedOnPos` → `generateTerrain` → NeedsDecoration+
  NeedsLightCalculation vs clear+NeedsRegeneration →
  `DynamicPrefabDecorator::DecorateChunk` → `AddChunkSync` →
  `OnChunkSyncedAndDecorated` (IL=4, exactly
  `WaterSimulationNative.InitializeChunk`) → `updateDecorationsWherePossible` →
  `isModified` store in the force path; pool free on failure.
- **`updateDecorationsWherePossible`:** tryToDecorate on chunk, (x-1,z), (x,z-1),
  (x-1,z-1) (three `ldc.i4.1; sub` neighbor fetches).
- **`decorate`:** +1/+1 neighbor GetChunkSync ×3 with early ret, four
  `InProgressDecorating` stores, `updateDecosAllowedForChunk`,
  `IWorldDecorator::DecorateChunkOverlapping`, `OnDecorated`, `ResetStability`,
  `RefreshSunlight`, `OnChunkSyncedAndDecorated`.
- **Slope/height constants:** `Vector3.Cross` normal; `normal.y < 0.55 →
  SetDecoAllowedSlopeAt(2=Steep)`, `< 0.65 → (1=Sloped)` (EnumDecoAllowedSlope
  Steep=2, Sloped=1); terrain height `ldc.i4 253` comparisons and water check →
  `SetDecoAllowedAt(..., 255)` with `EnumDecoAllowed.Nothing=255` (EnumList).
- **`SaveRandomChunks`:** `ldc.i4 400` tick age compare and
  `RandomFloat < ldc.r4 0.3` gate, `InProgressSaving` volatile store,
  `RegionFileManager::SaveChunkSnapshot`.
- **`UpdateDecorations` caller:** `ChunkManager::task_Lighting` (dump line 773818).
- **SaveAll:** editor branch saves spawn points/prefabs; game branch
  `RegionFileManager::MakePersistent(cc,false)` + `WaitSaveDone` +
  `EventPrefabs::Save`.
- **Reset plumbing:** RequestChunkReset/ResetAllChunks/ResetRegion/
  IterateChunkExpiryTimes/MainThreadCacheProtectedPositions all IL≤8 forwards to
  `m_RegionFileManager`; callers = `ConsoleCmdChunkReset`,
  `ChunkResetCommandHelpers::ExecuteReset`, `GameEvent...ActionResetRegions`,
  `GameManager::ResetUnprotectedChunksOnLoad`,
  `QuestEventManager::FinishTreasureQuest`, `ConsoleCmdPrintChunkExpiryInfo`
  (full-dump caller mapping) — exactly the doc's list.
- **FromRaw Init contents:** `<Init>d__17` IL=1032: `.raw` preference,
  `HeightMapUtils::ConvertDTMToHeightData` for `.tga`, `.png` fallback,
  `WorldBiomeProviderFromImage`, `splat3/4_processed.png` + `_half.png`,
  `TerrainFromRaw::Init(HeightMap, IBiomeProvider, seed)`,
  `RegionFileManager` ctor, `EventPrefabs`, `MultiBlockManager::Initialize`;
  overrides GetWorldExtent/GetWorldSize/GetHeight/GetPOIBlockIdOverride/
  GetPOIHeightOverride/FillOccupiedMap/GetChunkProtectionLevel all present;
  `GetWaterChunks16x16` consumed by `World/<LoadWorld>d__73`.
- **Disc Init:** `RegionFileManager::GetAllChunkKeys` loop + `FillBiomeId` +
  `AddChunkSync` + `CopyAllPrefabsIntoWorld`; Dummy `UnloadChunk` IL=4 =
  `MemoryPools.PoolChunks.FreeSync`.
- **Dead code:** `ChunkBlockLayerLegacy::Read`/`::Write` — zero call sites;
  `ChunkBlockChannel::Convert(ChunkBlockLayerLegacy[])` — zero call sites; no
  `newobj ChunkBlockLayerLegacy` anywhere; `ChunkBlockChannel::Read` gates old
  format on `_version <= 34` (`ldc.i4.s 34; ble.un`); static
  `ChunkBlockLayerLegacy::CalcOffset` live in MeshGenerator/MC2 and many others.
  `ChunkProviderParameter`: never `newobj`'d (only its List<> ctor);
  `GetParameters()` has no in-assembly callers (only System.Reflection
  homonyms). All confirmed via full-dump grep.
- **Distant deco:** `DecoChunk::ToDecoChunkPos` divides by 128 (both overloads);
  `MakeKey16` IL=8 = `x<<16 | (z & 0xFFFF)`; `DecoState` 0/1/2 (EnumList);
  `DecoManager.IsEnabled = (_levelName != "Empty")` in LoadWorld (IL_0532);
  `OnWorldLoaded` d__36: DecoOccupiedMap ctor → `IChunkProvider::FillOccupiedMap`
  → `/decoration.7dt` + `TryLoad` → `FileBackedDecoOccupiedMap` → server-gated
  `RandomFromSeedOnPos` random decoration; `EnumDecoOccupied` members 0-8 as
  listed. Callers: `GameManager/<RequestToEnterGame>d__194` →
  `SendDecosToClient`; `RegionFileManager::<RemoveChunks>g__RemoveChunk|116_0` and
  `NetPackageDecoResetWorldChunk::ProcessPackage` → `ResetDecosForWorldChunk`;
  `BlockShapeDistantDeco(Tree)::OnBlockAdded/OnBlockLoaded/OnBlockRemoved` and
  `ChunkCluster::SetBlock` → DecoManager add/remove/SetBlock;
  `ChunkCluster::addDistantDecorationBlocks` → `GetDecorationsOnChunk`;
  `NetPackageDecoUpdate`/`NetPackageDecoResetWorldRect` types exist (MethodList).
- **Support types:** `ChunkCacheNeighborBlocks` constructed in
  `ChunkCluster/<Init>d__45` (IL_003C) and `DynamicMeshChunkProcessor::Init`;
  `ChunkCoordinates` stored as `EntityAlive::homePosition` in
  `EntityAlive::Awake` (IL_003F).
- **Cross-doc:** no contradictions with save-region.md / world-chunks.md /
  world-generation.md on providerId, FromRaw role, or constants (grep of those
  docs).

## Not verified (out of scope / no tooling)

- Runtime log strings and behavior of console builds (real `SaveDataManager`
  commit thread semantics beyond IL structure) — IL structure matches the doc
  but no console platform provider exists in this assembly to observe.
- `SaveDataPrefsFile` escaping details ("escaped key/value text store") — not
  dumped; low risk.
