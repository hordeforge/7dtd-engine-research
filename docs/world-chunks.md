# World and chunk pipeline (dedicated V3.1.0)

**Owns:** world tick, generateTerrain trampoline, load/send (observer streaming), SetBlock path (generic engine).  
**Index math:** §2 below + [`terrain-height.md`](terrain-height.md).  
**Save path:** [`save-region.md`](save-region.md).  
**Product Streamed inject:** `7dtd-realworld/docs/realearth-runtime.md`.  
**Dumps:** `../il/loop-complete-v3.1.0/`, `../il/realearth-surfaces-v3.1.0/`, `../il/dedi-complete-v3.1.0/`.  
**Hub:** [`INDEX.md`](INDEX.md).

---

## 1. World tick entry

| Method | IL | Role |
|---|---:|---|
| `GameManager.gmUpdate` | **631** | Frame orchestration |
| `GameManager.UpdateTick` | **150** | Slice vs full tick |
| `World.OnUpdateTick` | **189** | Chunks, water splash, deco, block ticker, AIDirector, sleepers |
| `World.TickEntities` | **117** | Authority entity loop |
| `World.TickEntitiesSlice` | 5 / 37 | Partial entity work |
| `World.TickEntity` | **148** | Single entity authority tick |

Full tick (when timer ready): Flush → OnUpdateTick → TickEntities → LetBlocksFall → (not dedi) visibility → NetEntityDistribution → SendChunksToClients → optional SaveRandomChunks.

**`GameManager.UpdateTick` (IL=150) detail:** if `GameTimer.elapsedTicks == 0`
but players exist → only `TickEntitiesSlice` and return true (partial). Else
`TickEntitiesFlush`; `partial = (Time.time - lastTime) * 20`;
`OnUpdateTick(partial, activeChunks)`. Server: if `gameStateManager.OnUpdateTick`
false return false. Always `TickEntities(partial)` + `LetBlocksFall`. Non-dedi:
`SetEntitiesVisibleNearToLocalPlayer`. Server: `entityDistributer.OnUpdateEntities`,
`SendChunksToClients`; if `bSavingActive`: cache protected positions; every
**40** ticks `SaveRandomChunks(2, …)`; every **60 s** wall time
`SaveDecorations` + optional `EventPrefabs.Save`. Client: `updateSendClientPlayerPositionToServer`.
Rich presence every **1 s** wall.

**`TickEntitiesSlice` / `Flush`:** slice uses `tickEntitySliceCount` entities
from `tickEntityIndex` via `TickEntity(e, tickEntityPartialTicks)` then advances
index. Flush calls slice with full list count (drain remainder).

**`TickEntities(partial)` (IL=117 high-level):** rebuild `tickEntityList` from
world entities (primary local first ordering residual); if slice mode path not
used, tick all then `EntityActivityUpdate`; else set partial and flush.

**`SaveDecorations` (IL=3):** `DecoManager.Instance.Save()`.

**`DecoManager.UpdateTick` (IL=330 high-level):** drain locked queues:
`SAddDecoInfo` → `AddDecorationAt`; remove-pos list → `RemoveDecorationAt`;
rect resets → `ResetDecosInWorldRect`; chunk-key resets →
`ResetDecosForWorldChunk`. Then server: rebuild player list for deco interest
residual / coroutine path.

```mermaid
flowchart LR
  GMu[gmUpdate] --> UT[UpdateTick]
  UT --> OUT[OnUpdateTick]
  UT --> TE[TickEntities]
  UT --> FALL[LetBlocksFall]
  UT --> NET[NetEntityDistribution]
  UT --> SEND[SendChunksToClients]
  OUT --> AI[AIDirector / spawn / sleepers]
  SEND --> RF[RegionFileManager cache]
```

---

## 2. Chunk storage model

Summary (product-oriented deep write-up: ``realearth-surfaces.md``):

```mermaid
flowchart TB
  Y[block y] --> L["layer = y >> 2"]
  L --> ARR[m_BlockLayers layer]
  ARR --> IDX["idx = x + z*16 + y&3 * 256"]
  Y --> DENS[chnDensity same banding]
  XZ[x,z] --> TH["m_TerrainHeight x + z*16 byte"]
```

Live stock: `ChunkBlockYDim=256`, `ChunkBlockLayers=64`, `ChunkAreaDim=256` (XZ plane map size).

**Channel compaction:** the light and density channels compact whole layers:
`Chunk.CheckSameLight` (IL=4) / `CheckSameDensity` (IL=4) run the channel's
`CheckSameValue` pass, and `Chunk.HasSameDensityValue(y)` (IL=5) is
`chnDensity.HasSameValue(y)` - whether one `y` layer is a single value (the
fast-path storage probe; `PrefabChunk` stubs it false). The write is
`Chunk.SetDensity(x, y, z, density)` (IL=10): `chnDensity.Set(...)` with the
value widened to a `ulong` (`PrefabChunk` stubs no-op).
`Chunk.IsOnlyTerrain(y)` (IL=8) / `IsOnlyTerrainLayer(idx)` (IL=24) test the
layer's `bOnlyTerrain` compaction flag (out-of-range index → true, missing
layer → false; `PrefabChunk` stubs false).

**Block read surface (V3.1.0 b14):** `World.GetBlock(x, y, z)` (IL=13)
delegates to `ChunkCluster.GetBlock` and returns `BlockValue.Air` when the
`ChunkCache` is null (uninitialized world). `WorldBase.GetBlock(Vector3i)` /
`GetBlock(BlockValueRef)` (both IL=4) are the `IBlockAccess`
`DefaultGetBlock` implementations. `World.GetBlockData(pos)` (IL=10) is a
separate `Dictionary<Vector3i, object>` lookup (extra per-position data, not
the voxel word), written by `World.AddBlockData` (IL=6, dict `Add`) and
removed by `ClearBlockData` (IL=6, dict `Remove`). `WorldBiomes.GetBlockValueForName(name)` (IL=15) resolves an
item/block by name via `ItemClass.GetItem` and throws
`Block with name '...' not found!` on an empty result, else converts with
`ToBlockValue`. The cluster hop: `ChunkCluster.GetBlock(x, y, z)` (IL=21)
returns `Air` when `y >= 256` (out-of-height guard) or the chunk is missing,
else `chunk.GetBlock(toBlockXZ(x), y, toBlockXZ(z))`; `GetBlockEntities(key)`
(IL=59) sweeps every chunk's `IndexedBlocks[key]` positions and collects the
`BlockEntityData` (world-coordinate) for each; `GetBlockEntity(pos)` (IL=12)
returns null for a missing chunk; `GetBlockFaceTexture(pos, face, channel)`
(IL=23) returns `0` for a missing chunk, else the per-face texture index.
`Chunk.GetBlock(x, y, z)` (IL=100) is the voxel-read core: with
`IsInternalBlocksCulled` and inside it returns the lazily-resolved POI-filler
block (`bvPOIFiller` from `Constants.cPOIFillerBlock`); otherwise it reads
`m_BlockLayers[y >> 2].GetAt(...)` (error + rethrow on a missing layer) and
overlays the block's `damage` from `GetDamage`. `GetBlockNoDamage` (IL=73) is
the same without the damage overlay; `GetBlockId` (IL=17) returns the layer id
(0 for a missing layer); `GetBlockColumn` (IL=101) fills a vertical span with
the damage overlay.
`AddInsideDevicePosition(x, y, z, bv)` (IL=20) registers an inside position as
a `Vector3b` in `insideDevices` (+ hash set) and flips
`IsInternalBlocksCulled = true`; the `bv` parameter is never read in this
build. `isInside(x, y, z)` (IL=12) is the membership test
`insideDevicesHashSet.Contains(new Vector3b(x, y, z).GetHashCode())`.
`EnableInsideBlockEntities(on)` (IL=45) walks `insideDevices`, resolves each
world-pos key in `blockEntityStubs`, and `SetActive(on)` on the entity's
`gameObject` when it has a transform.
`EnableEntityBlocks(on, name)` (IL=51) toggles `blockEntityStubs` entries
whose (lowercased) transform name contains the (lowercased) filter, or all
entries when the filter is empty, returning the toggled count. The overlay itself is `Chunk.GetDamage(x, y, z)` (IL=8):
`(int)chnDamage.Get(...)` from the damage channel, written by
`Chunk.SetDamage` (IL=9): `chnDamage.Set(x, y, z, (long)damage)`.
The 64-bit texture word packs **eight 8-bit face indexes**
(`Chunk.Value64FullToIndex(word, face)` (IL=12) is
`(word >> (face * 8)) & 0xFF`; `TextureIdxToTextureFullValue64(idx)` (IL=43)
replicates the low byte across all eight slots).
`Chunk.SetBlockFaceTexture(x, y, z, face, texture, channel)` (IL=48) writes
one face slot: it reads the channel word, clears the face's 8 bits
(`& ~(0xFF << (face*8 & 63))`), ORs in the new byte, writes back, and sets
`isModified`. The read twin `Chunk.GetBlockFaceTexture` (IL=19) is
`(word >> (face*8 & 63)) & 0xFF`; the `PrefabChunk` variant (IL=29) uses
6-bit face slots (`face*6`, mask 63) against the prefab's stored texture.
`ChunkCluster.SetBlockFaceTexture(pos, face, textureIdx, channel)` (IL=61) is
the painted-texture write: chunk lookup (no-op on miss),
`Chunk.SetBlockFaceTexture(lx, ly, lz, face, textureIdx, channel)`, then
`chunkPosNeedsRegeneration`. The read side:
`GetTextureFullArray(pos)` (IL=22) is `TextureFullArray.Default` without the
chunk, else `chunk.GetTextureFullArray(lx, ly, lz, true)`; the
`BlockValueRef` overload (IL=17) returns Default for `None`/`Prop` types and
throws for anything else.
`World.worldToBlockPos(pos)` (IL=11) is the world-to-block conversion:
`new Vector3i(Fastfloor(x), Fastfloor(y), Fastfloor(z))` (floor, so the
negative half-space maps consistently).

`ChunkCluster` coordinate helpers: `ToWorldPosition(local)` (IL=5) adds the
cluster `Position`; `ToLocalPosition(world)` (IL=29) subtracts it per
component; `ToLocalVector` (IL=2) is the identity (the cluster is axis
aligned); `ToLocalKey(key)` (IL=24) rebases a packed chunk key by
`toChunkXZ(FloorToInt(Position.x/z))` and repacks it. `IsOnBorder(chunk)`
(IL=32) is true only for fixed-size clusters, when the chunk X/Z sits on
`ChunkMinPos`/`ChunkMaxPos`. `Chunk.ToWorldPos()` (IL=14) is the chunk origin
`(m_X*16, m_Y*256, m_Z*16)`; the local-coord overloads (IL=20/16) add the
cell offset (note the y scale is **256**, the chunk Y-dim).
`Chunk.IsInChunk(Vector3)` (IL=30) is the local-bounds test: true iff
`0 <= x < 16`, `0 <= y < 256`, `0 <= z < 16` (same 256 y-scale). The
`Vector3i` counterpart `Chunk.ToLocalPosition(Vector3i)` (IL=23) folds a
world block coordinate into chunk-local in place by masking: `x & 15`,
`y & 255`, `z & 15`; the mask is exact because all three dimensions are
powers of two (16/256/16), so no division is needed.

---

## 3. Generation

```mermaid
flowchart TD
  GT[ChunkProviderGenerateWorld.generateTerrain<br/>IL=11 trampoline]
  GT --> IT[ITerrainGenerator.GenerateTerrain]
  IT --> TR[TerrainFromRaw / DTM / BiomeResource]
  TR --> HF[GetTerrainHeightAt float]
  TR --> HB["GetTerrainHeightByteAt: float+0.5 conv.u1"]
```

Interfaces are unpatchable; patch concrete generators / provider.

---

## 4. Load / unload / stream

| Surface | IL / note |
|---|---|
| `DetermineChunksToLoad` | **448** (gmUpdate; rings, diffs, cull; section 4.0.1) |
| `SendChunksToClients` | **216** (per-observer remove/load/reload/map packages) |
| `AddChunkObserver` | **15** (player join attaches stream target) |
| `ResendChunksToClients` | **55** (queue reload keys for remote observers) |
| `doCopyChunksToUnity` | 252; **skipped on dedicated** in gmUpdate |
| `SaveRandomChunks` | 99 |
| `ChunkCluster.AddChunkSync` / `UnloadChunk` / `RemoveChunk` | pipeline |
| `Chunk.OnLoad` / `OnUnload` | 97 / 188 |
| `RegionFileManager` | cache + cull + claim protect |

### 4.0 Client chunk streaming (verified)

**When:** every full `UpdateTick`, after `NetEntityDistribution.OnUpdateEntities`
(Xref V3.1.0 b14: sole caller of `SendChunksToClients` is `GameManager.UpdateTick`
IL_00E6). `NetPackageChunk.Setup` call sites (4): two from `SendChunksToClients`
(first-load and reload paths), plus flat/disc terrain `RebuildTerrain` paths that
re-push overwrite chunks. There is no side-thread `write` of the package body
outside the normal NetPackage serialize path (Xref `write` = 0 direct callers;
serialization is virtual dispatch from the connection writer).

**`ChunkManager.AddChunkObserver(pos, buildVisualMesh, viewDim,
entityIdToSendChunksTo)` (IL=15):** `new ChunkObserver(...)`, push onto
`m_ObservedEntities`, set `isInternalForceUpdate = true` (forces one full stream
pass for the new observer), return it. Attached at player join
([server-lifecycle.md](server-lifecycle.md) §3) and per stream-target.

**Force-update gate:** `IsForceUpdate()` (IL=8) =
`isInternalForceUpdate || isChunkClusterChanged` (read from gmUpdate before the
observer work); `ForceUpdate()` (IL=4) sets `isInternalForceUpdate = true`.
`RemoveChunkObserver(o)` (IL=29) finds the observer by `id` in
`m_ObservedEntities`, removes it and also sets `isInternalForceUpdate = true`.
`GroundAlignFrameUpdate()` (IL=42, once per frame when world running) alternates
`groundAlignIndex` 0/1 and runs `Block.GroundAlign(data)` over the corresponding
`groundAlignBlockLists` bucket, clearing it (ground-snap of placed block entity
data).

### 4.0a `SendChunksToClients` body (IL=216)

Per observer (`m_ObservedEntities`; skip when `entityIdToSendChunksTo == -1`),
using one shared `sendToClientPackages` list:

1. **Removes:** for each key in `chunksToRemove`: queue
   `NetPackageChunkRemove.Setup(key)`, drop the key from `chunksLoaded` and
   `chunksToReload`. Clear `chunksToRemove`. Flush immediately:
   `SendPackage(list, false, 0, entityIdToSendChunksTo, -1, null, 192, false)`,
   clear list.
2. **Loads:** walk `chunksToLoad.list` while the batch has fewer than **3**
   packages: `GetChunkSync(key)`; skip while the chunk is missing or
   `NeedsLightCalculation` (volatile read); else queue
   `NetPackageChunk.Setup(chunk, false)` (first load), add the key to
   `chunksLoaded`, remove from `chunksToLoad`. So at most **3 new chunks per
   observer per tick**.
3. **Reloads:** walk `chunksToReload` **backwards** (`Count-1 .. 0`); same
   existence/light gate; queue `NetPackageChunk.Setup(chunk, true)` and
   `RemoveAt(index)`.
4. **Map chunks:** if `mapDatabase` set: `GetMapChunkPackagesToSend()` appended.
5. Flush whatever accumulated (`SendPackage` as step 1) and clear.

**`ResendChunksToClients(chunks)` (IL=55):** for each observer with
`!bBuildVisualMeshAround` whose `entityIdToSendChunksTo` does **not** match a
local player (or no local players exist): `chunksToReload.AddRange(chunks)`.
So a terrain rebuild re-pushes overwrite chunks to remote observers while
local visual-mesh observers rebuild directly (used by `RebuildTerrain` paths).

### 4.0b Chunk load/unload lifecycle

**`World.IsPositionAvailable(position)` (IL=43)** is the placement gate: with a
`ChunkCache` present it walks `Vector3i.MIDDLE_AND_HORIZONTAL_DIRECTIONS_DIAGONAL`
scaled by **16** (the 3x3 chunk neighborhood around the block) and requires each
`GetChunkFromWorldPos` to be non-null and `GetAvailable()` - any missing or
busy chunk makes the position unavailable.

**`Chunk.OnLoadedFromCache` (IL=90):** `NeedsRegeneration = true`,
`isModified = true`; clear the volatile `InProgress*` flags
(Regeneration/Saving/Copying/Decorating/Lighting/Unloading) and the collision
mesh flags; clear `entityStubs`; for each of the 16 `entityLists`: move every
`IsSavedToFile()` entity into `entityStubs` as `EntityCreationData(entity,
true)` and clear the list (the stubs are re-spawned on next `OnLoad`).

**Coordinate helpers (`World.toChunk*`):** `toChunkXYZ(v)` (IL=14) is
`(x >> 4, y >> 8, z >> 4)` (16/256-block chunk units); `toChunkXYZCube(v)`
(IL=17) is `floor(v) >> 4` per axis (the 16-cube bucket); `toChunkXyzWorldPos`
(IL=17) masks the block coords back to world floats (`x & -16`, `y & -256`,
`z & -16`). `TryRetrieveAndRemovePendingDowngradeBlock(ref bv)` (IL=14)
consumes one entry from `pendingUpgradeDowngradeBlocks` when present (the
upgrade/downgrade batch hand-off).

**Entity-band tracking (`Chunk.AdJustEntityTracking`, IL=50):** with the
entity in the chunk, recomputes its y-band `floor(pos.y / 16)` (clamped
0..15) and, when it differs from `chunkPosAddedEntityTo.y`, removes the
entity from the old `entityLists[band]`, stores the new band, adds it to
the new list and marks the chunk modified - the per-16-block-band entity
bucket the unload/interest paths scan. `GetTileEntities` (IL=3) is the
`tileEntities` `DictionaryList`; `RemoveAllTileEntities` (IL=11) clears it
and flags the chunk modified when it was non-empty.

**Block iteration and density repair:** `LoopOverAllBlocks(delegate,
includeChilds, includeAirBlocks)` (IL=30) fans out to each
`ChunkBlockLayer.LoopOverAllBlocks` (IL=54), which walks the 1024 cells of
a layer, decodes `x = idx % 16`, `y = idx / 256 + layerY`,
`z = (idx % 256) / 16`, fills the damage word via `GetDamage`, and invokes
the delegate (skipping air / child blocks per the flags).
`RepairDensities` (IL=90) scans the whole chunk and forces terrain blocks
to density `-1` and non-terrain to `1` where they disagree, returning
whether anything changed. `CheckDensities(logAll)` (IL=129) collects
`DensityMismatchInformation` records for every disagreeing cell and warns
once per call. `ClearNeedsRegenerationAt(idx)` (IL=32) clears the
`m_NeedsRegenerationAtY` bit (Monitor-locked, volatile) for a single
y-band index.
`LoopOverAllBlocksCoroutine(delegate, includeChilds, includeAirBlocks)`
(IL=15) is the frame-sliced twin: the `<LoopOverAllBlocksCoroutine>d__345`
MoveNext (IL=69) runs the same per-layer fan-out but yields once per layer
to spread the sweep across frames.

**Chunk geometry/bounds leaves:** `updateBounds()` (IL=55) recomputes
`boundingBox = CalculateAABB(m_X, m_Y, m_Z)` and the world-corner literals
`worldPosIMin = (m_X << 4, m_Y << 8, m_Z << 4)` /
`worldPosIMax = worldPosIMin + (15, 255, 15)`.
`GetBlockWorldPosZ(z)` (IL=7) is `(m_Z << 4) + z`;
`GetSameDensityValue(y)` (IL=16) returns the `DensityTerrain` /
`DensityAir` sentinels outside the 0..255 band else
`chnDensity.GetSameValue(y)` (`PrefabChunk` overrides it with a constant 0).

**`Chunk.OnLoad(world)` (IL=97):** server side only: for each `entityStub`
whose id is not already present in the world → `SpawnEntityAsync(world, stub,
null)`; `removeExpiredCustomChunkDataEntries(worldTime)`; per block layer
`layer.OnLoad(world, x*16, layer*4, z*16)` which, under lock, fires
`Block.OnBlockLoaded` for every `notifyLoadUnloadCallbackBlocks` index; per
tile entity `TileEntity.OnLoad()`.

**`Chunk.OnUnload(world)` (IL=188):** `InProgressUnloading = true`; destroy the
`biomeParticles` list. Server side: drain `pendingEntityCreateOps` by calling
`EntityCreateHandle.WaitForComplete()` on a snapshot (async creation must finish
before unload, see [dedicated-leftovers.md](dedicated-leftovers.md) §12); per
`entityLists` bucket `world.UnloadEntities(list, false)`;
`removeExpiredCustomChunkDataEntries`; per tile entity `TileEntity.OnUnload(world)`;
`RemoveBlockEntityTransforms()`; per layer `layer.OnUnload(...)` firing
`Block.OnBlockUnloaded` (under lock); `waterSimHandle.Reset()`.

**Leaves:** `removeExpiredCustomChunkDataEntries(worldTime)` (IL=61) drops
`ChunkCustomData` entries whose `expiresInWorldTime <= worldTime` (calling
`ChunkCustomData.OnRemove`), collecting expired keys then removing them.
`ChunkBlockClearData` (subclass) carries a `BlockList<Vector3i>` and its
`OnRemove(chunk)` (IL=37) sets every listed position to air via
`chunk.SetBlock(world, x, y, z, Air, true, true, false, false, -1)` - the
expiry callback is what actually clears the blocks.
`World.UnloadEntities(list, force)` (IL=36) walks the list backward and calls
`unloadEntity(e, reason 1)` unless `!force && (e.bWillRespawn || attached-main
entity bWillRespawn)` (sleepers with a pending respawn and their attachments
survive a non-forced unload).

### Chunk dirty / save invalidation (blob-cache input)

**`Chunk.get_NeedsSaving` IL=20** returns true if any of:

| Condition | Field |
|---|---|
| Block/light/etc. dirty | `isModified == true` |
| Entities present | volatile `hasEntities == true` |
| Tile entities non-empty | `tileEntities.Count > 0` |
| Block triggers non-empty | `triggerData.Count > 0` |

So a chunk with **any TE or trigger** always needs saving, even if `isModified`
is false. Pure air + no entities can be clean.

**`isModified` writers (field Xref, V3.1.0 b14 sample):** set true (or cleared)
from block/light/water/texture mutators (`SetBlockRaw`, `SetLight`, `SetWater*`,
`SetTextureFull`, `FillBlockRaw`, …), TE add/remove, entity tracking adjust,
load/save/reset/ctor paths, and biome spawn count helpers. A network chunk blob
cache keyed only on "block version" is incomplete unless it also invalidates on
**TE / trigger / entity occupancy** changes that flip `NeedsSaving` or change
serialized TE payload inside `Chunk.write` / snapshot.

**Region snapshot gate** (save-region): `RegionFileChunkSnapshot.Update` skips
unless `saveIfUnchanged` or `Chunk.NeedsSaving` - same predicate as above.

**Observer model (`ChunkManager/ChunkObserver`):** created by
`AddChunkObserver(pos, bBuildVisualMeshAround, viewDim, entityIdToSendChunksTo)`
and stored in `m_ObservedEntities`. Join path sets
`entityIdToSendChunksTo = player.entityId` and `viewDim` from the clamped
client value ([protocol.md](protocol.md) section 5).

**Shared observers (`SharedChunkObserver` / `SharedChunkObserverCache`,
server-side):** the cache (`observers` dict keyed by chunk pos, `viewDim`,
own `chunkManager` ref) hands out refcounted `SharedChunkObserver` records
(`chunkPos`, `refCount`, `chunkRef: ChunkObserver`, back-refs to the cache
and its `RemoveObserver` hook). `GetSharedObserverForChunk(pos)` returns the
existing record (bumping `Reference()`) or creates one; `Dispose` decrements
and removes at zero. Multiple entities pin one observer for the same chunk
instead of each holding their own (`MovableSharedChunkObserver` per entity,
[loop.md](loop.md) entity tick; the cache itself is
`NoThreadingSemantics` on dedicated).

| Field | Role |
|---|---|
| `entityIdToSendChunksTo` | target client entity id; **`-1`** skips network send |
| `viewDim` | observation radius; bucket lists sized `viewDim + 2` |
| `bBuildVisualMeshAround` | local/visual observer (not a remote stream target for resend) |
| `chunksLoaded` | keys already sent |
| `chunksToLoad` | `BucketHashSetList` of keys still needed |
| `chunksToReload` | keys that must be resent with overwrite |
| `chunksToRemove` | keys to unload on the client |
| `chunksAround` | current around-set from `DetermineChunksToLoad` |
| `mapDatabase` | optional mini-map package source |

`DetermineChunksToLoad` (IL=448) is called from **`gmUpdate`** (not from
`UpdateTick`; sole Xref). It refreshes per-observer around-sets and diffs
`chunksToLoad` / `chunksToRemove`. It does **not** send packages. Full algorithm:
section 4.0.1.

**`SendChunksToClients` per observer with `entityIdToSendChunksTo != -1`:**

1. **Removes:** for each key in `chunksToRemove`, queue
   `NetPackageChunkRemove.Setup(key)`; drop from `chunksLoaded` and
   `chunksToReload`; clear `chunksToRemove`. If any, `ConnectionManager.SendPackage`
   list to that entity id (arg literal **192** on the bulk send path, same as other
   join S2C bulk).
2. **First-time loads:** walk `chunksToLoad.list`; `GetChunkSync`; **skip** while
   `Chunk.NeedsLightCalculation`; else `NetPackageChunk.Setup(chunk, bOverwrite=false)`,
   mark loaded, remove from to-load. **Stop filling when pending packages >= 3**
   (per-tick throttle for first loads).
3. **Reloads:** reverse-walk `chunksToReload`; same light gate;
   `Setup(chunk, bOverwrite=true)`; remove from reload list.
4. **Map:** if `mapDatabase` set, append
   `IMapChunkDatabase.GetMapChunkPackagesToSend()` when non-null
   (`MapChunkDatabase`: 17x17 window around client map middle after a
   position update; channel-1 compressed `NetPackageMapChunks`,
   [protocol-packages.md](protocol-packages.md) section 3.3).
5. Send any remaining packages to the same entity id (again bulk flags **192**).

```mermaid
flowchart TD
  GMu[gmUpdate] --> DCL[DetermineChunksToLoad]
  DCL --> Obs[per ChunkObserver buckets]
  UT[UpdateTick full] --> SCT[SendChunksToClients]
  Obs --> SCT
  SCT --> Rem[ChunkRemove for chunksToRemove]
  SCT --> Load[Chunk Setup overwrite=false for toLoad]
  SCT --> Rel[Chunk Setup overwrite=true for toReload]
  SCT --> Map[optional map packages]
  Rem --> Send[SendPackage to entityId]
  Load --> Send
  Rel --> Send
  Map --> Send
```

**`NetPackageChunk` (channel 1, compressed):** `Setup` runs `Chunk.write` into a
pooled stream; `write` emits `bOverwriteExisting`, optional i16 x/y/z when
overwrite, i32 dataLen, blob. Client `ProcessPackage` either adds a new chunk or
unload/reset/re-read/re-add when overwriting. Codec shared with region save
([save-region.md](save-region.md), [protocol-packages.md](protocol-packages.md) section 3.1).

**`ResendChunksToClients(HashSetLong)`:** for each observer that is **not** a local
player visual mesh builder, append the given keys to `chunksToReload` so the next
`SendChunksToClients` re-pushes with overwrite (terrain rebuild paths call
`NetPackageChunk.Setup` directly as well). The long-key set's internal
`HashSetLong/PrimeHelper` (`ToPrime` / `CalcPrime` / `TestPrime`, 3 methods)
is the prime-table used for hash-bucket sizing.

### 4.0.1 `DetermineChunksToLoad` algorithm (verified)

**Caller:** `GameManager.gmUpdate` only (IL offset in inventory). Runs every
frame, before the full-tick path that may later call `SendChunksToClients`.

**Phase 0 - drain unloads (budget 8):**
`removeChunksToUnload(8)` walks `chunksToUnload` reverse under lock. For each
chunk: `EnterWriteLock`, set `InProgressUnloading`, skip if
`IsLockedExceptUnloading`, else remove from list, optional
`FreeChunkGameObject` when `IsDisplayed`, then `ChunkCluster.UnloadChunk`. Stops
after 8 successful free/unloads. Return count feeds phase-end CGO reclaim.

**Phase 1 - per observer, only when needed:**

Trigger if `isInternalForceUpdate` **or** `isChunkClusterChanged` **or** this
observer's chunk cell changed:

```text
cx = World.toChunkXZ(Fastfloor(position.x))   // >> 4
cz = World.toChunkXZ(Fastfloor(position.z))
curChunkPos = (cx, 0, cz)
```

When the cell (or force flags) changed:

1. **Rebuild `chunksAround`:** clear; for ring index `r = 0 .. viewDim+1`
   (exclusive upper bound `viewDim + 2`), for each offset in
   `rectanglesAroundPlayers[r]`, add key
   `MakeChunkKey(cx + ox, cz + oy)` into bucket `r`.
2. `RecalcHashSetList()` on `chunksAround` (flatten buckets to ordered `list`).
3. **Server only:**
   - `chunksToLoad` = per-bucket copy of `chunksAround` minus `chunksLoaded`
     (`ExceptWithHashSetLong` per bucket), then recalc.
   - `chunksToRemove` = `chunksLoaded` minus anything still in `chunksAround`
     (`UnionWith` loaded, then `ExceptTarget` around buckets).
   - Stamp `chunkGenerationTimestamps[key] = UtcNow` for every key now in
     `chunksToLoad.list`.

`rectanglesAroundPlayers` is built once in `ChunkManager.Init` (IL=104): array
length **15** (rings 0..14). Ring `r` holds the **hollow square** border offsets
where `max(|x|,|y|) == r` (both loops run `[-r..r]`; an offset is kept only if
it lies on the perimeter). That caps max useful `viewDim` near 13 for full ring
coverage (`viewDim+2 <= 15`). Manager-level
`m_ViewingChunkPositions` / `m_AllChunkPositions` / `m_CollisionChunkPositions`
are also 15-bucket `BucketHashSetList`s (ctor).

**Phase 2 - global union when any observer dirty (`loc.1`):**

Under `lockObject`:

1. Set volatile flags
   `isViewingOrCollisionPositionsChanged_threadCalc` and
   `_threadReg` so worker threads re-read positions.
2. Clear `m_AllChunkPositions` and `m_ViewingChunkPositions`.
3. For each bucket index and each observer with `viewDim+2` covering that
   bucket: union that observer's `chunksAround` bucket into `m_AllChunkPositions`;
   if `bBuildVisualMeshAround`, also union into `m_ViewingChunkPositions`.
4. Recalc both manager lists. Copy `m_AllChunkPositions.list` into
   `activeChunkSetArr`.
5. **Server:** rebuild `m_CollisionChunkPositions` =
   `m_All - m_Viewing` (per-bucket union then except), recalc.
6. **Server, non-fixed-size cluster:** under `chunksToUnload` lock, for every
   live cache key not in `m_AllChunkPositions` and not in DynamicMesh process/load
   queues: mark `InProgressUnloading`, queue into `chunksToUnload`, then
   `ChunkCluster.RemoveChunk` for each queued chunk.
7. If unload budget remaining (`8 - drained`),
   `recalcFreeChunkGameObjects(remaining, false)`.

**Always at end:** clear force/cluster flags; `calcThreadWaitHandle.Set()` to
wake `ChunkCalc` / related workers.

```mermaid
flowchart TD
  GMu[gmUpdate] --> Drain[removeChunksToUnload budget 8]
  Drain --> ObsLoop[per observer]
  ObsLoop --> Cell{chunk cell or force?}
  Cell -->|no| Next[next observer]
  Cell -->|yes| Rings[rebuild chunksAround from rings 0..viewDim+1]
  Rings --> Diff[server: toLoad and toRemove diffs]
  Diff --> Next
  Next --> Dirty{any dirty?}
  Dirty -->|yes| Union[lock: m_All and m_Viewing unions]
  Union --> Coll[collision = all - viewing]
  Coll --> Cull[queue out-of-range RemoveChunk]
  Dirty -->|no| Wake
  Cull --> Wake[calcThreadWaitHandle.Set]
```

**`BucketHashSetList`:** distance-ringed `HashSetLong` buckets plus a flattened
`list` rebuilt by `RecalcHashSetList` (bucket order 0..n, dedupe via
`elementsInList`). `SendChunksToClients` walks that flat `list` for first loads,
so nearer rings tend to stream first when buckets were filled ring-first.

### 4.1 Chunk progress flags (stock `InProgress*` volatiles)

Measured fields on `Chunk`: `InProgressCopying`, `Decorating`, `Lighting`, `Regeneration`, `Unloading`, `Saving`, `Networking`. Conceptual lifecycle (flags can overlap; not a single exclusive enum):

```mermaid
stateDiagram-v2
  [*] --> Needed
  Needed --> Loading: DetermineChunksToLoad / region read
  Loading --> Generating: generateTerrain
  Generating --> Decorating: decorators POI
  Decorating --> Lighting: LightChunk
  Lighting --> Stability: CalcStability
  Stability --> Ready: mesh regen when needed
  Ready --> Dirty: SetBlock / NeedsRegeneration
  Dirty --> Lighting: relight
  Dirty --> Stability: restab
  Dirty --> Ready: RegenerateChunk
  Ready --> Saving: SaveRandomChunks / unload flush
  Saving --> Ready
  Ready --> Unloading: out of range cull
  Unloading --> [*]
  Ready --> Networking: SendChunksToClients
  Networking --> Ready
```

**Flag/property leaves (all IL-verified):** `get_IsLocked()` (IL=34) is true
when any of `InProgressCopying` / `Decorating` / `Lighting` /
`Regeneration` / `Unloading` / `Saving` / `Networking` / `WaterSim` is set;
`get_IsLockedExceptUnloading()` (IL=30) drops the `Unloading` member;
`get_IsInitialized()` (IL=16) is `!NeedsLightCalculation &&
!InProgressDecorating && !InProgressUnloading`.
`get_NeedsRegeneration()` (IL=21) / `get_NeedsRegenerationAt()` (IL=19) are
the Monitor-locked reads of the volatile `m_NeedsRegenerationAtY` bitmask
(the `> 0` form vs the raw value); `set_NeedsRegenerationAt(value)` (IL=28)
ORs `1 << ((value >> 4) & 31)` (the 16-block Y-slice bit, matching the
delayed-regen layout); `set_NeedsRegeneration(value)` (IL=54) first frees
every mesh layer (zeroes `MeshLayerCount`, clears `m_layerIndexQueue`,
pool-frees `m_meshLayers`) under the layer lock, then under the regen lock
sets `m_NeedsRegenerationAtY = 65535` (all layers) or 0, mirroring
`NeedsRegenerationDebug`. `get_NeedsCopying()` (IL=3) is `HasMeshLayer()`;
`get_StopStabilityCalculation()` (IL=3) reads `stopStabilityCalculation`.
`get_ChunkPos()` (IL=8) builds `Vector3i(m_X, m_Y, m_Z)`; `set_ChunkPos(v)`
(IL=14) / `set_X(v)` / `set_Z(v)` (IL=9 each) clear `cachedToString`, store
the coordinate(s) and run `updateBounds()` (set_ChunkPos does not touch Y);
`get_Y()` (IL=3) reads `m_Y`; `ExitWriteLock()` (IL=4) releases the
`sync` `ReaderWriterLockSlim`.
`IsEmptyLayer(idx)` (IL=22) is true when `idx >= m_BlockLayers.Length` or
the layer is null with `chnWater.IsDefaultLayer(idx)` (`PrefabChunk`
overrides it with a constant 0); `GetSizeOfMesh(idx)` (IL=26) sums
`sizeOfMesh[channel][idx]` across channels (the mesh-budget read).

---

## 5. Mutation / dirty

| Method | IL | Role |
|---|---:|---|
| `ChunkCluster.SetBlock(Vector3i,…)` | **828** | Full set path |
| `ChunkCluster.SetBlockRaw` | 25 | Resolve chunk + local coords → `Chunk.SetBlockRaw` |
| `Chunk.SetBlockRaw` | **386** | Silent voxel write (detail below) |
| `chunkPosNeedsRegeneration` | **550** | Dirty mesh/light |
| `LightChunk` / `CalcStability` / `RegenerateChunk` | cluster | Fallout |

Prefer SetBlock over SetBlockRaw when mesh must update (product inject lesson).

**Delayed / batched regeneration.** During bulk edits (POI placement and
similar) the cluster coalesces regen requests instead of marking chunks one
by one: `ChunkPosNeedsRegeneration_DelayedStart` (IL=28) increments a
`delayedRegenCount` refcount and clears the batch dict on the 0->1
transition; while `delayedRegenCount > 0`, `chunkRegenerateAt(chunk, yPos)`
(IL=49) accumulates `delayedRegenChunks[chunk] |= 1 << ((yPos >> 4) & 31)`
(a 16-block Y-slice bitmask, the same layout `Chunk.FormatRegenerationLayers`
formats) instead of setting `NeedsRegenerationAt` directly;
`ChunkPosNeedsRegeneration_DelayedStop` (IL=48) decrements the refcount and,
on the 1->0 transition, flushes every accumulated mask through
`chunk.NeedsRegenerationOrBits(mask)` and clears the batch. So a prefab
write marks dirty layers in bulk and the real relight/remesh fallout runs
once when the batch ends.

**Chunk-loading / regeneration-state leaves:** `ChunkCluster.UpdateRegenerationState
(chunkKey, state)` (IL=33) returns immediately on a dedicated server, else
`chunkRegenerationHistories.GetOrAdd(key)` gets a per-chunk
`StateHistory<ChunkState>` and (under the monitor) `Add`s the state - the
client chunk-lifecycle history fed by `AddChunkSync` / `RemoveChunk` /
`UnloadChunk` / `RegenerateChunk`.
`SecondsSinceChunkStartedRegeneration(chunkKey)` /
`SecondsSinceChunkEndedRegeneration(chunkKey)` (IL=20 each) look up a
`(int, DateTime)` tuple in the `chunkRegenerationStartTimestamps` /
`chunkRegenerationEndTimestamps` concurrent dicts and return
`(startCount, (UtcNow - timestamp).TotalSeconds)`, or `(-1, -1)` on a miss.
`NotifyOnChunksFinishedLoading()` (IL=10) invokes
`OnChunksFinishedLoadingDelegates` when set (fired from `AddChunkSync`) and
latches `bFinishedLoadingDelegateCalled`.
`GetIndexedBlocks(name)` (IL=71, **0 call sites on b14**) scans
`GetChunkArrayCopySync`, skips chunks with `InProgressUnloading` (under the
chunk monitor), and collects `chunk.ToWorldPos(p)` for every entry of
`chunk.IndexedBlocks[name]` into one world-position list - the named
block-index query.

### 5.0 `Chunk.SetBlockRaw` (IL=386)

Silent in-chunk write used by load, falling, inject, and some TE paths:

1. If `y >= 255`: force Air write target.
2. Water path: if old/new is water or `CanWaterFlowThrough`, may recurse
   `SetBlockRaw` / `SetWater` and notify `waterSimHandle.SetVoxelSolid` with
   rotation faces.
3. Layer: `ChunkBlockLayer.GetAt` / `SetAt`; allocate layer if needed; preserve
   or clear damage for non-child air/solid transitions.
4. Index lists: update `IndexedBlocks` (remove old index type, add new if
   `FilterIndexType`, e.g. `lpblock`).
5. Heightmap: if air↔solid at column, `RecalcHeightAt`.
6. Random tick registry: under lock on `tickedBlocks`, Remove or Replace world
   pos when `IsRandomlyTick` transitions.
7. Flags: `bMapDirty`, `isModified`, `bEmptyDirty`; return previous BlockValue.

Does **not** fire light/mesh/stability RPC; callers that need those use full
`SetBlock` / `SetBlockRPC`.

### 5.0a `ChunkBlockLayer` storage (V3.1.0 b14)

Each of the 64 `ChunkBlockLayer` objects (one per 4-block Y band) stores the
block words with a **split-byte layout** and a same-value compression:

- `CalcOffset(x, y, z)` (IL=12) = `z*16 + x + (y & 3) * 256` - 1024 cells,
  the same sub-plane layout as `ChunkBlockChannel`
  ([`save-region.md`](save-region.md) §2).
- **Low byte:** `m_Lower8Bits : Byte[]` (1024) holds bits 0..7, compressed as
  `lower8BitSameValue : byte` when every cell shares it (array null).
- **Upper 24 bits:** `m_Upper24Bits : Byte[]` (3072 = 3 bytes per cell,
  little-endian) holds bits 8..31; allocated on demand and zero-cleared.

`GetAt(offs)` (IL=61) assembles `low | u24[3*offs]<<8 | u24[3*offs+1]<<16 |
u24[3*offs+2]<<24` into the `BlockValue` word and falls back to
`BlockValue.Air` when the type is out of `Block.list` range or resolves to a
null `Block` (corrupt save ids read as air). `SetAt(offs, fullBlock)`
(IL=294) writes the low byte, materializing the 8-bit array filled with the
old same value when a differing low byte arrives (pooled
`allocArray8Bit`/`allocArray24Bit` from `MemoryPools.poolCBLLower8BitArrCache`
/ `poolCBLUpper24BitArrCache`, Monitor-locked, capped at 10000 entries; both
arrays are 1024/3072-byte fresh allocs when the pool is empty).

**Per-layer bookkeeping maintained by `SetAt`:** `blockRefCount` and
`tickRefCount` (distinct block types / `IsRandomlyTick` blocks present) update
on type transitions, and a lock-guarded `notifyLoadUnloadCallbackBlocks`
`HashSet<int>` tracks ids needing `IsNotifyOnLoadUnload` callbacks. A
non-terrain block landing in the layer clears `bOnlyTerrain`;
`CheckOnlyTerrain()` (IL=153) re-derives it by scanning the 24-bit array for
all-zero upper words.

**Chunk map leaves (V3.1.0 b14):** `GetHeight(x, z)` (IL=9) reads
`m_HeightMap[z*16 + x]` (the 256-byte column-height byte map) and
`GetHeight(blockOffset)` (IL=5) is the direct index. `IsWater(x, y, z)`
(IL=9) is `GetWater(x, y, z).HasMass()`. `SetTopSoilBroken(x, z)` (IL=36)
sets a bit in the `m_bTopSoilBroken` bitfield
(`[idx/8] |= 1 << (idx%8 & 31)`, 32 bytes covering the 256 columns) - the
"topsoil disturbed" marker the terrain-dig/upgrade and explosion paths set
on affected columns.

**Water reads (V3.1.0 b14):** `Chunk.GetWater(x, y, z)` (IL=8) is
`WaterValue.FromRawData(chnWater.Get(x, y, z))` - the water cell decoded
from the `ChunkBlockChannel` storage (see
[`save-region.md`](save-region.md) §2); `ChunkCluster.GetWater(pos)`
(IL=23) returns `WaterValue.Empty` for `y >= 256` or a missing chunk, else
resolves the chunk and delegates through `toBlockXZ`.

**`Chunk.GetBlock(x, y, z)` (IL=100)** is the local block read: when
`IsInternalBlocksCulled` and the cell `isInside` a culled POI interior, it
returns the cached `bvPOIFiller` (lazily resolved from
`Constants.cPOIFillerBlock` by name on first use) - the placeholder that
reads as the "inside an un-entered POI" block; otherwise it reads the cell
from `m_BlockLayers[y >> 2]` (the `ChunkBlockLayer` storage above).

**`Chunk.recalcIndexedBlocks()` (IL=26)** clears `IndexedBlocks` and rebuilds
it from every layer (`ChunkBlockLayer.AddIndexedBlocks` per layer, 64 of
them). `saveBlockIds()` (IL=53) marks every in-chunk block id used in
`Block.nameIdMapping` under its lock (the save-id bookkeeping that lets a save
remap ids on load, mirroring `ItemValue.Write`).

**Density setters:** `ChunkCluster.SetDensity(pos, density, isForceDensity)`
(IL=14) routes through the full
`SetBlock(pos, false, Air, true, density, false, false, false, false, -1)`
(the terrain mutation with the normal dirty/notify path). The raw twin
`SetDensityRaw(pos, density)` (IL=27) writes `Chunk.SetDensity(lx, ly, lz,
density)` directly (missing chunk → no-op).

**Neighbor notification:** `ChunkCluster.notifyBlocksOfNeighborChange(worldPos,
newBV, oldBV)` (IL=23) fans `notifyBlockOfNeighborChange` to all six
`Vector3i.AllDirections` offsets. The single-cell version (IL=24) skips remote
worlds, reads the neighbor's current block, and for non-air blocks calls
`Block.OnNeighborBlockChange(world, neighborPos, neighborBV, changedPos, newBV,
oldBV)` - the hook behind water flow, plant updates, rails, and spike /
mechanical neighbor reactions.

### 5.0b Uncull and trader lookup helpers

**`World.UncullChunk(chunk)` (IL=8):** if `IsInternalBlocksCulled`, add to
`chunksToUncull` set (async uncull queue).

**`World.UncullPOI(prefab)` (IL=26):** `prefab.AddChunksToUncull(world, set)`;
on success log POI name + bbox and return true.

**`updateChunksToUncull` (IL=191):** if queue empty return. Restart
`msUnculling` stopwatch; clear `chunksToRegenerate`. Reverse-walk
`chunksToUncull`: drop if `InProgressUnloading`; else
`RestoreCulledBlocks` → remove from uncull queue → add to regenerate set; for
neighbor faces from restore flags (W/E/N/S bits) enqueue neighbor chunks for
regenerate. Stop when `msUnculling.ElapsedMilliseconds ≥ **5**` (5 ms budget;
continues next frames).

**`World.GetTraderAreaAt(pos)` (IL=14):**
`ChunkProvider.GetDynamicPrefabDecorator().GetTraderAtPosition(pos, 0)` or null.

**`World.IsWorldEvent(event)` (IL=7):** only event **0** is implemented → returns
`isEventBloodMoon`; any other event → false.

**`World.CheckEntityCollisionWithBlocks(entity)` (IL=19):** if
`!CanCollideWithBlocks` return; if chunk cache overlaps entity AABB,
`ChunkCluster.CheckCollisionWithBlocks`.

**`World.CanPlaceLandProtectionBlockAt(pos, player)` (IL=138 high-level):** if
GameStats **1** != 1 allow always; require `InBoundsForPlayersPercent ≥ 0.5`;
scan nearby chunks using claim size stats **44/45**; reject when
`IsLandProtectedBlock` conflicts.

**`InBoundsForPlayersPercent(pos)` (IL=100):** if world extent width &lt; **1024**
return **1**. Else distance-to-edge soft bands: 50 m hard margin + 80 m fade on
x and z from world center; return min of clamped x/z fractions (1 = deep
interior, 0 = at edge).

**`IsLandProtectedBlock(chunk, pos, relative, claimSize, deadZone, forKeystone)`
(IL=104 high-level):** walk chunk `IndexedBlocks["lpblock"]` primary land-claim
TEs; if within deadZone of claim and owner valid: self not protected against
self; ally within claimSize only when `forKeystone`; else protected → true.

**`AdjustBoundsForPlayers(ref pos, padPercent)` (IL=112):** if world extent
width &lt; **1024** or max.x == 0 return false (no clamp). Shrink min/max by
`50 + 80*padPercent` on xz; clamp pos into that box; return true if any
coordinate was clamped.

**`FindSupportingBlockPos(pos)` (IL=175 high-level):** if block at pos movement-
blocked or elevator → return pos. Check y+1 elevator. If y−1 elevator or blocked
→ return. Else direction octant from pos to block center (`supportOrder` table);
walk neighbor offsets for a movement-blocked support block and return its
center.

### 5.1 `GameManager.ChangeBlocks` (IL=530) / `SetBlocksOnClients` (IL=13)

Authoritative multi-block apply used by `NetPackageSetBlock` Process:

1. Lock; resolve `PersistentPlayerData` for the changer (local or list lookup).
2. Walk `List<BlockChangeInfo>`: collect touched `ChunkCluster`s; delayed regen
   start per cluster.
3. Per change: density/air/terrain shape checks; `GetBlock` vs new type;
   `SetBlockValue` / full `ChunkCluster.SetBlock(...)` overload; top-soil break
   on neighbor chunks; `UncullChunk`; child-block TE cleanup.
4. Delayed regen stop after list.

**Top-soil break bitmap:** `Chunk.IsTopSoil(x, z)` (IL=31) /
`SetTopSoilBroken(x, z)` (IL=36) pack one bit per column in the 32-byte
`m_bTopSoilBroken` array (index `(x + z*16) / 8`, bit `(x + z*16) % 8`):
`IsTopSoil` answers the bit clear, `SetTopSoilBroken` sets it (dug soil no
longer regrows top soil). `GetTopSoil` (IL=3) exposes the array, `SetTopSoil`
(IL=21) copies a full list in, and `GetTopMostTerrainHeight` (IL=28) is the
max of the `m_TerrainHeight` heightmap bytes. `PrefabChunk` stubs
`IsTopSoil` / `SetTopSoilBroken` as false / no-op.

**`GameManager.SetBlocksRPC(changes, persistentPlayerId)` (IL=29)** is the
commit+replicate wrapper: `ChangeBlocks(persistentPlayerId, changes)`, then
`NetPackageSetBlock.Setup(persistentLocalPlayer, changes, dedicated ? -1 :
myPlayerId)`; on the server `SetBlocksOnClients(-1, package)`, else
`SendToServer`.

`SetBlocksOnClients(exceptEntityId, package)` (IL=13):
`ConnectionManager.SendPackage(package, false, -1, exceptEntityId, -1, null,
**192**, false)` excluding the placing entity.

**Props are the sibling path.** `GameManager.ChangeProps(persistentPlayerId,
propsToChange)` (IL=121): lock `ccChanged`; per `PropChangeInfo` require the
chunk (`GetChunkSync` on `ChunkPos`), bail out of the batch on a miss; then
`ChunkCluster.SetProp(ChunkPos, PropId, Position, Rotation, Scale, BlockValue)`
applies the nullable tuple. Touched clusters get
`ChunkPosNeedsRegeneration_DelayedStart` around the batch and
`_DelayedStop` after it. `SetPropsRPC(changes, persistentPlayerId)` (IL=29)
commits, then mirrors `NetPackageSetProp` (`Setup(persistentLocalPlayer,
changes, dedicated ? -1 : myPlayerId)`) to `SetPropsOnClients(-1, package)` on
the server or `SendToServer`; `SetPropsOnClients(exceptEntityId, package)`
(IL=13) fans out on channel **192** excluding the entity.

**The delayed-regen pair:** `ChunkPosNeedsRegeneration_DelayedStop` (IL=48)
decrements the cluster's `delayedRegenCount`; when it reaches 0 it applies the
buffered `(Chunk, bits)` pairs under lock via `Chunk.NeedsRegenerationOrBits`
and clears `delayedRegenChunks`. The matching `_DelayedStart` increments the
count, so nested multi-batch edits defer the regen flags until the last batch
finishes.

```mermaid
stateDiagram-v2
  [*] --> Clean
  Clean --> Dirty: SetBlock / inject
  Dirty --> Lighting: LightChunk
  Dirty --> Stability: CalcStability
  Lighting --> MeshRegen: RegenerateChunk
  Stability --> MeshRegen
  MeshRegen --> Clean
  Dirty --> Clean: SetBlockRaw only no mesh path risk
```

---

## 6. Block tickers / falling

| System | IL | Note |
|---|---:|---|
| `WorldBlockTicker` tickScheduled / tickRandom | 151 / 97 | From OnUpdateTick server path |

**`WorldBlockTicker.Tick` (IL=20):** require `bTickingActive` and server: run
`tickScheduled` then `tickRandom`.

**Chunk tick gate:** `Chunk.get_NeedsTicking` (IL=13) is
`tileEntities.Count > 0 || sleeperVolumes.Count > 0` - the per-chunk reason to
run the TE tick loop at all. `GetTickRefCount(layerIdx)` (IL=13) reads a
layer's `tickRefCount` (0 for a missing layer).

**`tickScheduled` (IL=151):** lock; process up to **100** due entries from
`scheduledTicksSorted` (stop at first future `scheduledTime`). If chunk area not
loaded: reschedule +**30..45** random ticks when chunk exists; else drop. If
loaded: `execute(entry)`.

**`tickRandom` (IL=97):** rebuild key list from active chunks when index
exhausted; `randomTickCountPerFrame = max(1, activeCount/100)`; each frame
`tickChunkRandom` that many. Per chunk: skip if needs light; require ≥ **1200**
ticks since `LastTimeRandomTicked`; for each ticked block pos call
`Block.UpdateTick(..., random=true)` unless already scheduled.

**`RestoreCulledBlocks` (IL=58):** walk `insideDevices` reverse; OR face flags
for devices on chunk edges (x=0 → 8, x=15 → 32, z=0 → 4, z=15 → 16); clear
`IsInternalBlocksCulled`; return flags.

**`WorldBlockTicker.execute(entry, rnd, ticksIfLoaded)` (IL=24):** if live block
type still matches entry `blockID`, call
`Block.UpdateTick(world, pos, bv, random=false, ticksIfLoaded, rnd)`.

**`AddScheduledBlockUpdate(pos, blockId, ticks)` (IL=39):** no-op if blockId 0;
build entry at `GameTimer.ticks + ticks`; under lock replace existing same
hash then `add(entry)`.

**Chunk-load schedule restore (`World.OnChunkAdded` / `OnChunkBeforeRemove` /
`updateChunkAddedRemovedCallbacks`):** `OnChunkAdded(chunk)` (IL=20) records
the chunk key in the locked `newlyLoadedChunksThisUpdate` list; the first
step of `World.OnUpdateTick` (loop.md §3.2), `updateChunkAddedRemovedCallbacks`
(IL=67), drains it in reverse, calling `Chunk.OnLoad(world)` for chunks that
are present and no longer `NeedsDecoration`, then on the server
`worldBlockTicker.OnChunkAdded(world, chunk, rand)`.
`WorldBlockTicker.OnChunkAdded` (IL=93) is the schedule restore: it pops the
`wbt.sch` entry from the chunk's custom data, reads the count and per-entry
tick data via a pooled reader (`WorldBlockTickerEntry.Read`), and under the
ticker lock re-adds future entries (`scheduledTime > GameTimer.ticks`) or
executes overdue ones immediately with the elapsed delay.
`OnChunkBeforeRemove(chunk)` (IL=31) drops the key from
`newlyLoadedChunksThisUpdate`, calls `worldBlockTicker.OnChunkRemoved(chunk)`,
and `GameManager.Instance.prefabLODManager.TriggerUpdate()`.
| `AddFallingBlock` / `LetBlocksFall` | 38 / 220 | Collapse storms |
| `AddFallingBlock` detail | 38 | HashSet dedupe; skip child/air/`StabilityIgnore`/oversized (unless include); `DynamicMeshManager.AddFallingBlockObserver`; enqueue `fallingBlocks` |
| `EntityFallingBlock` OnUpdateEntity | 300+ | Entity cost |

## Stability, falling blocks, DamageBlock and deco subbiomes (2026-08-06)

Status: **verified** against a full V3.1.0 b14 disassembly (2026-08-05 dump; line
numbers are from that dump; the tracked `il/` sets are the V3.1.0 corpus).

### Stability runs on clients too

`GameStats::initPropertyDecl` (1919111) builds 78 `PropertyDecl`s with ctor order
`(EnumGameStats name, bool bPersistent, EnumType type, object defaultValue)`. Array
index 52 is `(stat 55 = ChunkStabilityEnabled, bPersistent = FALSE, type 3 = bool,
default TRUE)` at 1919743. It is correctly absent from the persistent Write blob,
which means **every client keeps chunk stability enabled from its own default
regardless of what the server sends.**

`ChunkCluster::Init` (1125631-1125637) constructs **both** a `StabilityCalculator`
(`stabilityCalcMainThread`) and a `StabilityInitializer`
(`stabilityCalcLightingThread`) and calls `StabilityCalculator::Init` whenever
`world.GetGameManager() != null`, i.e. on clients too, not only on the server.

`ChunkCluster::LightChunk` (1127022) calls `ChunkCluster::CalcStability` (1127044),
which runs `StabilityInitializer::DistributeStability` plus
`Chunk::CheckSameStability` for every chunk. That is why `bNetwork = true` can skip
the stability channel on the wire: the receiving client recomputes the whole plane
locally.

`ChunkCluster::SetBlock` (~1128420-1128620) calls
`StabilityCalculator::BlockPlacedAt` / `BlockRemovedAt` (with `Block::StabilityFull`
as the flag) for the block and for every `multiBlockPos` cell, on the client as
well as the server.

`ChunkCluster::ClearStabilityForChunks(chunks)` (IL=9) is the teardown twin:
`stabilityCalcMainThread.ClearChunkStabilityQueues(chunks)` plus
`world.ClearFallingBlocksForChunks(chunks)` (drops pending falls for the
unloading set).

`StabilityCalculator/UpdatePhysics` (1095820-1095900) is a coroutine gated on
`GameStats.GetBool(EnumGameStats.ChunkStabilityEnabled)` at IL_0014 and on
`StabilityCalculator::bRunning`; when it runs it pushes every unstable position
into `World::AddFallingBlock` (IL_00ad).

`GameManager::UpdateTick` (1881893) calls `World::LetBlocksFall()` at IL_00a5
**outside** the `ConnectionManager.IsServer` guard that wraps
`GameStateManager::OnUpdateTick` just above it, so clients run the falling-block
pump too. `World::LetBlocksFall` is at 1239773, `World::AddFallingBlock` at
1239718, and the entity comes from `EntityFactory::CreateEntity` with
`EntityClass::FromString("fallingBlock")` at 1240000.
`EntityFallingBlocks::Enabled` (220106) is a separate toggle for the grouped
variant.

### DamageBlock is the repair, upgrade and downgrade path

`Block::DamageBlock` (96545) computes `newDamage = blockValue.damage +
_damagePoints` (IL_00bf) and branches on the sign:

- `newDamage < 0` and `Block::UpgradeBlock` is not air (IL_00d9-IL_0128):
  **replaces** the block with `UpgradeBlock`, converting rotation via
  `Block::convertRotation`, copying meta and zeroing damage. Block upgrading is
  over-repair, not a separate operation.
- `newDamage < 0` with no `UpgradeBlock` (IL_0197): clamps damage to 0 and
  SetBlockRPCs.
- IL_01b1 onward is the `Stage2Health` downgrade path.

`ItemActionRepair` (657520) drives repair by calling `Block::DamageBlock` with the
repair amount **negated** (IL_056f `neg`), so the resulting C2S
`NetPackageSetBlock` always carries the new **lower** absolute `BlockValue.damage`.
A server must never treat a wire damage value below the stored one as a delta to
add. The repair amount is `Utils::FastMin(repairAmount, blockValue.damage)` at
IL_0216-IL_0228; the XP event is `_xpFromRepairBlock` (657572).

### Deco density comes from subbiomes, not the top-level list

`WorldBiomeProviderFromImage::GetBiomeOrSubAt` (1303341) resolves `GetBiomeAt` then
`GetSubBiomeIdxAt` (noise) and returns `BiomeDefinition::subbiomes[idx]` when the
index is >= 0. `DecoManager::decorateChunkRandom` calls it **per cell** (1266039)
and samples that **subbiome's** `m_DistantDecoBlocks` (1266052). Sampling only the
top-level biome's `<decorations>` list misses where essentially all the real tree
probability mass lives in stock `biomes.xml` (pine_forest top-level rows are prob
.001-.007; the subbiome lists carry treeJuniper4m .06, treeDeadTree01 .07,
treeDeadPineLeaf .08).

`blocks.xml` ships `IsDistantDecoration` on only three blocks: `treeMaster` (true,
inherited by everything extending it), `resourceRock01` (false) and `treeCactus01`
(true). `BiomeDefinition::AddDecoBlock` (1249700-1249740) uses that flag to build
`m_DistantDecoBlocks`, so the effective distant-deco species set is "anything whose
Extends chain reaches treeMaster, plus treeCactus01, minus resourceRock01".

### Weather packages are keyed strictly by biomeId

`WeatherManager::ClientProcessPackages` (2054217) does
`WorldBiomes::TryGetBiome(biomeId)`, then
`BiomeDefinition::SetWeatherGroup(groupIndex)`, then
`WeatherManager::FindBiomeWeather(biomeId)` and `WeatherPackage::CopyTo`. Entries
for a biomeId the client does not have are skipped silently, and it early-returns
if two weather packages arrive in the same `Time.frameCount`.

---

## Related docs

| Doc | Role |
|---|---|
| [protocol-packages.md](protocol-packages.md) | `NetPackageChunk` / `WorldInfo` wire |
| [protocol.md](protocol.md) | join path that attaches chunk observers |
| [network.md](network.md) | UpdateTick placement of SendChunks |
| [save-region.md](save-region.md) | Chunk write/read; blob codec shared with NetPackageChunk |
| [terrain-height.md](terrain-height.md) | YDim / height |
| `realearth-surfaces.md` | Product surfaces |

**Catalogued-leaf index (narrated for the coverage census):**

| Leaf | base | key methods |
|---|---|---|
| `ChunkGameObject` | MonoBehaviour | CheckLODs, SetChunk, StartCopyMeshLayer, SetStatic |
| `ChunkPreviewManager` | Object | SetWorldPosition, IsPositionInArea, Update, SetChunkGoVisiblity |
| `ChunkQueue` | Object | Add, Remove, Contains, Clear |
| `ChunkSnapshotUtil` | Object | LoadChunk, Free, TakeSnapshot, WriteSnapshot |
| `FlatArea` | Object | IsValid, GetPositions, GetRandomPosition, IsInArea |
| `PrefabHelpers` | Object | smoothChunk, SimplifyPrefab, mergePrefab, combine |
| `PrefabVolumeAbs` |  |  |
| `RegionData` |  |  |
| `RegionExtensions` |  |  |
| `RegionFileAccessRaw` | RegionFileAccessMultipleChunks | OpenRegionFile, GetRegionCoords, ReadDirectory, get_ChunksPerRegionPerDimension |
| `RegionFileAccessSectorBased` | RegionFileAccessMultipleChunks | GetRegionCoords, ReadDirectory, OpenRegionFile, get_ChunksPerRegionPerDimension |

**Server-relevant classified leaves (re-narrated for the coverage census):**

| Leaf | base | key methods |
|---|---|---|
| `ChunkPreviewData` | Object | set_WorldPosition, set_PrefabInstance, set_PrefabData |
| `ChunkVertexLayer` | Object | Reset, setYPosAt, setAt |
| `PrefabMarkerEntry` | XUiListEntry`1<XUiC_PrefabMarkerList/PrefabMarkerEntry> | CompareTo, MatchesSearch, get_Marker |
| `WorldMove` | ValueType | PerformMove, get_CountOfAssociatedSavesInSameStorage, get_IsReady |
| `WorldPreviewTerrain` | Object | createMesh, GenerateTerrain, destroyTerrain |

**`TileAreaConfig`** (ValueType): tile-area geometry config with `checkCoordinates` bounds validation (reached via the tile-area reflection path).

## Changelog

- **2026-08-11:** Chunk/block-data IL re-verified: AddBlockData IL=6, ClearBlockData IL=6, GetBlockValueForName IL=15, Chunk.GetBlock IL=100 (exact).
- **2026-08-10:** Chunk/block-read IL re-verified (6): HasSameDensityValue 5, SetDensity 10, IsOnlyTerrain 8, World.GetBlock 13, GetBlockData 10, ChunkCluster.GetBlock 21 (exact).
- **2026-08-10:** GameManager.UpdateTick IL=150, DecoManager.UpdateTick IL=330 re-verified (exact).
- **2026-08-08:** Catalogued-leaf index added (narrates the family's remaining
  catalogued leaves for the coverage census).

- **2026-08-08:** Shared chunk observers (SharedChunkObserver/SharedChunkObserverCache): refcounted per-chunk observer sharing.
- **2026-08-08:** Delayed/batched regeneration (5): DelayedStart (IL=28)
  refcount + batch clear, chunkRegenerateAt (IL=49) Y-slice bitmask
  accumulation (1 << (yPos>>4 & 31)), DelayedStop (IL=48) flush via
  NeedsRegenerationOrBits.

- **2026-08-08:** ChunkBlockClearData leaf: BlockList<Vector3i>, OnRemove
  (IL=37) airs every listed pos via Chunk.SetBlock (the expiry callback).
- **2026-08-08:** Chunk.GetBlock IL=100: POI-filler culling (IsInternalBlocksCulled + isInside -> cached bvPOIFiller from cPOIFillerBlock), else m_BlockLayers[y>>2] read.
- **2026-08-08:** Water reads: Chunk.GetWater IL=8 FromRawData(chnWater);
  ChunkCluster.GetWater IL=23 y>=256/missing-chunk Empty + toBlockXZ
  delegate.
- **2026-08-08:** Chunk map leaves: GetHeight IL=9 m_HeightMap[z*16+x];
  IsWater IL=9 GetWater().HasMass(); SetTopSoilBroken IL=36
  m_bTopSoilBroken bitfield (32 bytes, idx/8 bit idx%8).
- **2026-08-08:** ChunkBlockLayer storage (5.0a): split-byte layout
  (m_Lower8Bits + lower8BitSameValue compression, m_Upper24Bits 3 bytes/cell),
  CalcOffset IL=12 1024-cell sub-planes; GetAt IL=61 word assembly + Air
  fallback; SetAt IL=294 materialize-on-differing-low-byte, pooled
  alloc/free (10000 cap); blockRefCount/tickRefCount + notifyLoadUnload
  HashSet bookkeeping; bOnlyTerrain + CheckOnlyTerrain IL=153 scan.
- **2026-08-07:** World.worldToBlockPos (IL=11) floor-based Vector3i
  conversion; restored a sentence dropped in an intermediate edit.
- **2026-08-07:** ChunkCluster read hops: GetBlock (IL=21) y>=256 Air guard +
  null-chunk Air; GetBlockEntities (IL=59) IndexedBlocks sweep; GetBlockEntity
  (IL=12) null on missing chunk; GetBlockFaceTexture (IL=23) 0 on missing chunk.
- **2026-08-07:** Block read surface: World.GetBlock (IL=13) null-cache Air +
  ChunkCluster delegate, WorldBase.GetBlock IBlockAccess defaults (IL=4),
  GetBlockData dict (IL=10), WorldBiomes.GetBlockValueForName (IL=15) name
  resolve + not-found throw.
- **2026-08-07:** DecoManager.UpdateTick add/remove/rect/chunk drain.
- **2026-08-07:** WorldBlockTicker.execute type match; AddScheduledBlockUpdate.
- **2026-08-07:** WorldBlockTicker scheduled 100 cap; random 1200 ticks; RestoreCulledBlocks flags.
- **2026-08-07:** UpdateTick IL=150 slice/full; save 40 ticks; deco 60s; SetBlocksOnClients 192.
- **2026-08-07:** TickEntitiesSlice/Flush; TickEntities list rebuild;
  SaveDecorations DecoManager.
- **2026-08-07:** updateChunksToUncull RestoreCulledBlocks + 5 ms budget.
- **2026-08-07:** FindSupportingBlockPos supportOrder; AdjustBoundsForPlayers pad clamp.
- **2026-08-07:** InBoundsForPlayersPercent 50/80; IsLandProtectedBlock lpblock deadZone.
- **2026-08-07:** CheckEntityCollisionWithBlocks; CanPlaceLandProtectionBlockAt 0.5 bounds.
- **2026-08-07:** Chunk.SetBlockRaw IL=386 (y cap, water, IndexedBlocks, heightmap,
  tickedBlocks, dirty flags).
- **2026-08-07:** UncullChunk/UncullPOI; GetTraderAreaAt decorator; IsWorldEvent
  only blood-moon (0).
- **2026-08-07:** ChangeBlocks IL=530 / SetBlocksOnClients IL=13 authority path.

- **2026-08-07:** `Chunk.get_NeedsSaving` predicate (isModified | hasEntities | TE | triggers) for blob-cache invalidation notes.
- **2026-08-06:** ChunkStabilityEnabled is non-persistent with default true, so
  clients keep stability on regardless of the server; ChunkCluster::Init builds a
  StabilityCalculator on clients too and LightChunk recomputes the plane (why
  bNetwork skips the channel); GameManager::UpdateTick runs LetBlocksFall outside
  the IsServer guard; Block::DamageBlock sign branches carry repair, UpgradeBlock
  and Stage2Health downgrade, and ItemActionRepair negates the amount so the wire
  damage is the new lower absolute; DecoManager samples per-cell subbiome
  m_DistantDecoBlocks via GetBiomeOrSubAt and IsDistantDecoration is set on only
  three blocks; WeatherManager::ClientProcessPackages keys strictly on biomeId.

- **2026-07-28:** Map package producer pointer (MapChunkDatabase 17x17 window).
- **2026-07-28:** `DetermineChunksToLoad` full algorithm: 15 hollow rings, per-observer diffs, global unions, unload budget 8.
- **2026-07-28:** `SendChunksToClients` per-observer remove/load/reload/map pipeline; ChunkObserver fields; 3-package first-load throttle.

- **2026-07-19:** Related docs table.
- **2026-07-18:** Chunk/world family narrative consolidating loop + surfaces RE.
