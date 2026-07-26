# Cluster B audit: world / terrain / mesh / save (V3.0.1 stable dedicated DLL)

**Verdict:** Six of seven docs verify cleanly at the IL level (every checked IL size, constant, enum, wire layout, and formula matched); `dynamic-mesh.md` §4 has one CRITICAL defect: its on-disk region format is reverse-engineered from a dead legacy code path and does not match the bytes the live server writes.

ASM = `/home/maci/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll`.
Custom one-off scanners (RefScan = all instruction operands incl. `ldftn`; LitScan = `ldc.i4*` literals; FieldRefScan; StrScan = `ldstr`; ConstScan = const fields; ILSize = instruction counts) were compiled against `tools/bin/Mono.Cecil.dll` in the session scratchpad; every claim below cites the command run.

---

## Findings

### F1 CRITICAL (format-breaking) — dynamic-mesh.md §4 "Region persistence": the documented `.group` format is dead code; the live format is different bytes

**Claim:** "`WriteRegion` writes a **version tag `160`** (`Int32`), the distinct chunk count, each chunk `Vector3i` position, then the serialized voxel meshes. The geometry is written by width-specialized writers (`Write16BitVoxelMeshes` / `Write32BitVoxelMeshes` ... `WriteVoxelMeshesWithTerrain` ...) ... `WriteRegionHeaderData` writes a separate header." Table: "Region group | `<MeshLocation><key>.group` | `DynamicMeshRegion.Path`, `DynamicMeshFile.WriteRegion`". Read side: "`DynamicMeshFile.LoadRegionGameObjectSync`, ..."

**Ground truth:**
- `mono RefScan.exe "$ASM" WriteRegion` -> only two hits: `DynamicMeshFile::WriteRegion [call] -> WriteRegion` and `WriteRegionHeaderData [call] -> WriteRegionHeaderData` (retry self-recursion). Neither method has any external caller, including via delegates (`ldftn` scanned).
- `mono RefScan.exe "$ASM" WriteVoxelMeshesWithTerrain` -> only its own lambda. `mono RefScan.exe "$ASM" LoadRegionGameObjectSync` -> zero references. The whole `DynamicMeshFile` region write/read cluster (incl. `Write16BitVoxelMeshes`, reached only from the dead `WriteVoxelMeshes` chain) is unreachable in this DLL.
- The live `.group` producer (`mono tools/bin/FindCallers.exe "$ASM" SaveRegion` + `DumpMethod DynamicMeshRegionDataStorage SaveRegion`, IL=69): `DynamicMeshChunkProcessor.RegenerateRegion -> DynamicMeshRegionDataStorage.SaveRegion` opens `DynamicMeshRegionDataWrapper.Path()` (`"{0}.group"`, key from `WorldChunkCache.MakeChunkKey`), wraps it in `newobj Noemax.GZip.DeflateOutputStream` (IL_0032), and calls `DynamicMeshVoxelRegionLoad::SaveRegionToFile` (IL=7) = `WriteOpaqueMesh(bw, opaque)` + `WriteTerrainVoxelMeshesToDisk(bw, terrain)`. **No version tag, no chunk-position table, deflate-compressed.**
- The live read side (`DumpMethod DynamicMeshRegionDataStorage LoadRegion`, IL=167): `SdFile.OpenRead -> DynamicMeshVoxelRegionLoad::LoadRegionFromFile`, error string "`. Deleting corrupted file.`" lives here.
- The literal 160 exists in this DLL only in the two dead methods plus unrelated geometry code: `mono LitScan.exe "$ASM" 160 DynamicMesh`.

**Fix:** Rewrite §4 around `DynamicMeshRegionDataStorage.SaveRegion/SaveItem/LoadRegion` + `DynamicMeshVoxelRegionLoad` (deflate stream, opaque mesh + terrain mesh payload; item data via `DynamicMeshChunkData.Write`: X, OffsetY, Z, EndY, MinTerrainHeight, UpdateTime, MainBiome, TerrainHeight list, ...). Move the `WriteRegion`/version-160 material to a clearly-labeled "dead legacy path" note or delete it. The retry-count claims (5/10) are true of the dead bodies only.

### F2 MAJOR (wrong-behavior) — dynamic-mesh.md §4: `WriteRegion` is mis-described even as a body

**Claim:** version 160, "the distinct chunk count, **each chunk `Vector3i` position**, then **the serialized voxel meshes**".

**Ground truth** (`mono tools/bin/DumpMethod.exe "$ASM" DynamicMeshFile WriteRegion`, IL=159):
- Per chunk it writes only `Vector3i::x` and `Vector3i::z` (two `i32`, IL_00B3-IL_00C6) — **no y**.
- After the chunk list it writes `CreateDate.Ticks` as `i64` (IL_00E6-IL_00F1) — omitted by the doc.
- It then reads `BaseStream.Position`, pops it, and returns. **It writes no voxel meshes and never opens a file** (no `GetCreateStream`/`SdFile` call in the body; it fills a pooled `MemoryStream` and discards it). `WriteRegionHeaderData` (IL=133) is the variant that opens `DynamicMeshRegion::get_Path()` via `GetCreateStream` — i.e. it writes to the same `.group` path, not "a separate header".

**Fix:** If the legacy description is kept at all, correct the field list (x,z pairs; ticks; no geometry; no disk write) and drop the "separate header" sentence.

### F3 MINOR (label) — dynamic-mesh.md §4: corrupted-file log attribution

**Claim:** "`DynamicMeshRegion` logs 'Corrupted region. Adding for regen' **and** 'Deleting corrupted file'".
**Ground truth:** `mono StrScan.exe "$ASM" "Corrupted region"` -> `DynamicMeshRegion::OnCorrupted` (correct); `mono StrScan.exe "$ASM" "Deleting corrupted"` -> `DynamicMeshRegionDataStorage::LoadRegion` (not `DynamicMeshRegion`).
**Fix:** attribute the second string to `DynamicMeshRegionDataStorage.LoadRegion`.

### F4 MINOR (label) — dynamic-mesh.md §4: `MeshLocation` is set in `Awake`, not `Init`

**Claim:** "`DynamicMeshManager.Init` sets `DynamicMeshFile.MeshLocation` to `GameIO.GetSaveGameDir() + "/DynamicMeshes/"` ..."
**Ground truth:** `mono StrScan.exe "$ASM" "DynamicMeshes"` -> `DynamicMeshManager::Awake` (and `<DelayStartForWorldLoad>d__162`); `DumpMethod DynamicMeshManager Awake` shows `GetSaveGameLocalDir`/`GetSaveGameDir` -> `stsfld DynamicMeshFile::MeshLocation`. `DynamicMeshManager::Init()` exists but is not the site.
**Fix:** say `Awake` (path values themselves are correct).

### F5 MINOR (count) — evidence-line method/type counts don't reproduce

**Claims:** dynamic-mesh.md: "`DynamicMeshRegion` 98 [methods]", "`DynamicMeshServer` + pooled types 35"; world-generation.md: "`WorldGenerationEngineFinal.*` IL (64 types / 489 method bodies)", "`SDF.*` (12 / 49)".
**Ground truth:** `grep -c "^DynamicMeshRegion::" methods.txt` (MethodList.exe) = 67 declared methods; Cecil count incl. nested/compiler-generated types = 104 bodies (CountScan) — neither is 98. `WorldGenerationEngineFinal.`: 43 named types / 432 named bodies, or 127 types / 688 bodies incl. compiler-generated — neither is 64/489. `SDF.`: 11 named types (12 only if a compiler-generated type is counted), 49 methods (matches). By contrast `DynamicMeshManager` 91, `DynamicMeshThread` 40, `DynamicMeshFile` 40, `DynamicMeshBuilderManager` 18, and `PrefabVolumes` 16/158 all reproduce exactly.
**Fix:** re-derive the off counts with the same tool as the others, or state the counting convention. ("35" for server+pooled types is unverifiable without knowing which pooled types were summed.)

---

## Spot-verified CONFIRMED

IL sizes (all via `mono ILSize.exe "$ASM" <claims>`; identical numbers from `DumpMethod` headers):
- `DynamicMeshManager.Update`=404, `DynamicMeshServer.Update`=452 (dynamic-mesh.md, light-mesh-water.md)
- `WorldState.SaveLoad`=884, `SetFrom`=164, `Save(String)`=21, `GameManager.SaveWorld`=7, `Chunk.write`=601 / `read`=775 / `save`=14 / `load`=9, `ChunkBlockChannel.Write`=120 / `Read`=151, `PersistentPlayerList.Write`=73, `SaveLocalPlayerData`=45, `SaveAndCleanupWorld`=499, `SaveRandomChunks`=99, `World.SaveDecorations`=3 (save-region.md)
- `gmUpdate`=631, `UpdateTick`=150, `OnUpdateTick`=189, `TickEntities`=117, `TickEntitiesSlice`=5/37, `TickEntity`=148, `DetermineChunksToLoad`=448, `SendChunksToClients`=216, `doCopyChunksToUnity`=252 (all three on `ChunkManager`; doc doesn't claim a type), `ChunkCluster.SetBlock`=828, `SetBlockRaw`=25, `chunkPosNeedsRegeneration`=550, `Chunk.OnLoad`=97 / `OnUnload`=188, `WorldBlockTicker.tickScheduled`=151 / `tickRandom`=97, `AddFallingBlock`=38, `LetBlocksFall`=220 (world-chunks.md)
- Whole light/stability/mesh/water/deco table in light-mesh-water.md: `LightProcessor.LightChunk`=53, `RefreshSunlightAtLocalPos`=107, `RefreshLightAtLocalPos`=128, `SpreadLight`=116, `UnspreadLight`=125, `GenerateSunlight`=27, `Chunk.RefreshSunlight`=112, `GameLightManager`=159/175, `MeshGeneratorMC2.calcLights`=289 / `CreateMesh`=606, `StabilityCalculator` 293/266/216/126/125, `StabilityInitializer` 152/154/127/136/72, `MeshDataManager.LateUpdate`=5, `WaterSimulationNative.Update`=229 / `InitializeChunk`=51 / `Step`=16, `WaterEvaporationManager.UpdateEvaporation`=317, `WaterSplashCubes.Update`=185, `DecoManager.UpdateTick`=330, `updateDecosAllowedForChunk`=306, `generateTerrain`=11
- world-generation.md: `GenerateTask`=203, `GenerateBiomeTiles`=436, `GenerateTerrainTiles`=385, `GenerateBaseStamps`=167, `TownPlanner.Plan`=817, `spawnWildernessPrefab`=623, `SpawnMarkerPartsAndPrefabs`=1410, `GetWorldPath`=7, `<GenerateData>d__120::MoveNext`=211, `<GenerateBaseStamps>b__142_1`=1 (the empty radTask lambda, name and size exact); terrain-height.md: `TerrainGeneratorWithBiomeResource.GenerateTerrain`=424 ("~424"), `TerrainMapGenerator.GenerateTerrain`=549, `WorldBuilder.GenerateTerrain`=128 / `generateTerrainFeature`=652 ("128-652")
- `WorldBuilder` type stats: fields=116, methods=97, total IL=7090 — exact (`mono CountScan.exe "$ASM" WorldGenerationEngineFinal.WorldBuilder`)

Constants (`mono ConstScan.exe "$ASM" <Type>` unless noted):
- `RegionFileRaw`: ChunksPerRegionPerDimension=8, ChunksPerRegion=64, fileHeaderLength=11, locationHeaderLength=128, timestampHeaderLength=64, sectorsStartOffset=779, reservedBytesPerEntry=4, CurrentVersion=1
- `RegionFileManager`: cChunkFileExt=".ttc", all seven protection margins=1
- `Chunk`: CurrentSaveVersion=47, SupportedSaveVersion=32; `Chunk.read` throws "Chunk version ... not supported!" below 32 (`DumpMethod Chunk read`: `ldc.i4.s 32` guard)
- `WorldConstants` stock: ChunkBlockYDim=256, YPow=8, YDimM1/YMask=255, ChunkBlockLayers=64, ChunkDensityYDim=256, ChunkAreaDim=256; `ChunkProviderGenerateWorldFromRaw.cMaxHeight`=255
- `WeatherManager`: cGracePeriodWorldTime=22000, cVersion=4, cForceTempDefault=-100
- `DynamicMeshServer.MaxActiveSyncs`=10 (`.cctor` `ldc.i4.s 10`), 20 s drop ("Sync waited more than 20 seconds. Removing..." in `Update`); `NetPackageDynamicMesh.MaxMessageSize`=2097152 (`LitScan 2097152`)
- `DynamicMeshThread.SetDefaultThreads` (IL=13): exactly `min(8, max(procCount-2, 1))` then `min(..., MaxDyMeshData+1)`; `GenerationThread` self-pacing `NextRun` +500 ms (paused/null manager) / +300 ms (all queues empty) as `ldc.r8`; 100 ms startup wait sleep in `<StartThread>b__70_0`

Serialization / wire bodies:
- `Chunk.write` (IL=601): m_X, m_Y, m_Z (`i32`), SavedInWorldTicks (`u64`), layer loop bound `ldc.i4.s 64`, `chnStability` channel, then `m_HeightMap`, `m_TerrainHeight`, further byte maps, custom data, 5+ `ChunkBlockChannel.Write` calls, entities, tile entities — doc order confirmed. `ChunkBlockChannel` layer literal 1024 in Read/Write (`LitScan 1024 ChunkBlockChannel`)
- `WorldState.SaveLoad` (IL=884): `Monitor.Enter`/`Exit`, **exactly 59** `ReadWrite*` calls (`grep -c ReadWrite`), `WeatherManager.Save/Load` gated on `ConnectionManager.IsServer`, Guid generate-if-empty; `SetFrom` contains one `ldc.i4 256`
- `NetPackageDynamicMesh`: Channel=1, Compress=true, Direction=0=Both (`NetPackageDirection.Both=0` in enums.txt); write order X:i32, Z:i32, UpdateTime:i32, len:i32, bytes; `ProcessPackage` (IL=24): IsServer -> `ClientReadyForNextMesh`, else `AddDataFromServer(X,Z)` + empty package `SendToServer`; client cache path `MeshLocation + X + "," + Z + ".mesh"` in `read`
- `NetPackageDynamicClientArrive`: Channel=0, Compress=true, Direction=1=ToServer; write = count:i32 then per item X:i32, Z:i32, UpdateTime:i32
- `NetPackageWeather`: Direction=2=ToClient; per biome byte biomeId, byte groupIndex, byte remainingSeconds, float32 param loop, **no count prefix**; `ProcessPackage` IL=1 (`ret`); `WeatherManager::currentWeather` has zero store sites and `WeatherPackage::CopyTo` zero callers (FieldRefScan/RefScan) — the "dedicated receive side is a stub" claims are exactly right
- `HeightMapUtils.SaveHeightMapRAW(Stream,Single[],Single)`: `(h + offset) * 257`, `FastClamp(0, 65535)`, low byte then `>>8` (uint16 LE); `serializeRawHeightmap` passes offset `-1` -> `(h-1)*257` as documented
- `serializeRWGTTW`: `new WorldState()`, `SetFrom(world, (EnumChunkProviderId)4)`, `ResetDynamicData`, `Save(stream)`; map_info keys incl. `Cracks` present in `serializeDynamicProperties`

Behavior / structure:
- `DynamicMeshManager.Update` step order (guard `CONTENT_ENABLED`, `ChunksToRemove` drain, `ProcessItemMeshGeneration`/`ProcessChunkRegionRequests` coroutines, `DestroyObjects`/`CheckFallingObservers`, `IsServer -> DynamicMeshServer.Update`, `ShowOrHidePrefabs`, `ReadyForCollection`/`ChunkReadyForCollection` collection, `RegionsAvailableToLoad`, `UpdateData` promotion) — all present in that order in the IL
- `ChunkChanged(BlockValueRef,Int32,Int32)` exists; border test uses `& 15` (four sites)
- `DynamicMeshBuilderManager.HandleResult` calls `DyMeshData::AddToCache` (RefScan) — dedicated cache-bytes claim
- `GenerationThread` pipeline order: `HandleRegionLoads` -> `CheckBuilders` -> `SetNextChunkToLoad` -> `ProcessRegionRegenRequests` -> `ProcessMeshGenerationRequests` -> queue processing
- `UpdateTick` full-tick call order: `TickEntitiesFlush` -> `World.OnUpdateTick` -> `TickEntities` -> `LetBlocksFall` -> `SendChunksToClients` -> `IChunkProvider.SaveRandomChunks`
- Chunk indexing: `ChunkBlockLayer.GetAt` = `x + (z<<4) + (y&3)*256`, layer select `y>>2` (`Chunk.GetBlockNoDamage`); `World.toBlockY` = `y & 255`; `Chunk.RefreshSunlight` contains `ldc.i4 255`; 255/256 ceiling sites exist in `LightProcessor`, `MeshGeneratorMC2`, `Chunk.ResetStability*` (LitScan)
- Height API signatures: `Byte World.GetTerrainHeight(i,i)`, `Single World.GetHeightAt(f,f)`, `Byte Chunk.Get/SetTerrainHeight`, `Byte/Single GetTerrainHeightByteAt/At` on `TerrainFromDTM`/`TerrainFromRaw`/`TerrainGeneratorWithBiomeResource`, `Int32 MeshGeneratorMC2.GetTerrainHeight`; byte conversion is `+0.5` then `conv.u1` (SigScan + DumpMethod). ("Prefab" in the table = `MeshGeneratorPrefab::GetTerrainHeight`.)
- Weather: `WorldEnvironment.Update -> WeatherManager.FrameUpdate -> GenerateWeatherServerFrameUpdate` + per-biome `BiomeWeather.FrameUpdate`; `GameManager.updateTimeOfDay -> SendPackages`; `CalcGlobalTemperature` literals 0.01/-5/clamp01/-7.5; `BiomeWeather.FrameUpdate` freezing split at 32 and visible-precip 0.3/0.7; `ServerTimeUpdate` pins `int.MaxValue` (3 sites) with "stormbuild"/"storm" transitions on `stormState`; `PlayerEntityStats.GetOutsideTemperature` = `ldc.r4 70; ret`, `WeatherManager.GetTemperature`/`GetWindSpeed` = `ldc.r4 0; ret`; "Prefabs/WeatherManager" loaded in `GameManager.<createWorld>`; `Constants.cSendWorldTickTimeToClients` exists
- World generation: `MainMenuMono.Start/startDedicatedServer/startGeneration` exist; abort string "...world likely was never successfully generated!" in `<startGeneration>d__16`; `GetGeneratedWorldName` = `RandomCountyNameGenerator.GetName(seedName.GetHashCode() + worldSize)` (IL=6, exact); ctor defaults WaterHeight=30, WorldSize=8192, Seed=12345; biome weights 13/18/22/23/24 into the five `*BiomeWeight` fields; `WorldSizeDistDiv` branch chain 2500->4, 3500->3, 4500->2, else 1; `GenerateTerrainFromTiles` called with (plains,1024), (hills,512), (mountains,256); 12-player-spawn top-up (`ldc.i4.s 12` minus `playerSpawns.Count`); `radiationLayer` written only in ctor, read only by `DrawBiomeRadStampsToMaps` lambda (all-clear radiation claim holds); "RWG final in {0}:{1:00}, r={2:x}" log string
- Enums (grep `/scratch/enums.txt` from `EnumList.exe`): `DynamicMeshBuilderStatus` Ready..Error incl. the four Starting* states and PreviewComplete/Stopped; `MarkerTypes` POISpawn=1/RoadExit=2/PartSpawn=3; WGF `BiomeType` forest=0..wasteland=4, waterDebug=6; `TerrainType` plains=0/hills=1/mountains=2; `GenerationSelections` None..Many=0..3; `SdfTagType` End=0..Binary=7, Unknown=-1; `EnumGamePrefs` GameWorld=33, WorldGenSeed=171, WorldGenSize=172; `EnumChunkProviderId` 4=ChunkDataDriven; SDF filenames `gameOptions.sdf`/`sdcs_profiles.sdf` present as literals
- File naming: `.group` = `MeshLocation + key + ".group"` (`DynamicMeshRegion.get_Path`), `.raw` via `DynamicMeshRegionDataWrapper.RawPath` "{0}.raw" — table paths correct even though the stated producer (F1) is not

Not independently verified (out of scope for this DLL): terrain-height.md "Expanded" column (16384/4096/16383 — historical patched binary, not the stable DLL); Unity script-execution-order claims (engine-side, not in IL); Burst-native bodies.
