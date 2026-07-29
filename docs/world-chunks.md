# World and chunk pipeline (dedicated V3.0.1)

**Owns:** world tick, generateTerrain trampoline, load/send (observer streaming), SetBlock path (generic engine).  
**Index math:** §2 below + [`terrain-height.md`](terrain-height.md).  
**Save path:** [`save-region.md`](save-region.md).  
**Product Streamed inject:** `7days-realworld/docs/realearth-runtime.md`.  
**Dumps:** `../il/loop-complete-v3.0.1/`, `../il/realearth-surfaces-v3.0.1/`, `../il/dedi-complete-v3.0.1/`.  
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
| `DetermineChunksToLoad` | **448** (per-observer buckets, unload set) |
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
(Xref: sole caller of `SendChunksToClients` is `GameManager.UpdateTick`).

**Observer model (`ChunkManager/ChunkObserver`):** created by
`AddChunkObserver(pos, bBuildVisualMeshAround, viewDim, entityIdToSendChunksTo)`
and stored in `m_ObservedEntities`. Join path sets
`entityIdToSendChunksTo = player.entityId` and `viewDim` from the clamped
client value ([protocol.md](protocol.md) section 5).

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

`DetermineChunksToLoad` (IL=448) refreshes per-observer around-sets and
populate/diff `chunksToLoad` / unload candidates (bucket hash sets + locks). It
does not itself send packages.

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
   `IMapChunkDatabase.GetMapChunkPackagesToSend()` when non-null.
5. Send any remaining packages to the same entity id (again bulk flags **192**).

```mermaid
flowchart TD
  UT[UpdateTick] --> DCL[DetermineChunksToLoad]
  DCL --> Obs[per ChunkObserver buckets]
  UT --> SCT[SendChunksToClients]
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
`NetPackageChunk.Setup` directly as well).

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

---

## 5. Mutation / dirty

| Method | IL | Role |
|---|---:|---|
| `ChunkCluster.SetBlock(Vector3i,…)` | **828** | Full set path |
| `ChunkCluster.SetBlockRaw` | 25 | Silent |
| `chunkPosNeedsRegeneration` | **550** | Dirty mesh/light |
| `LightChunk` / `CalcStability` / `RegenerateChunk` | cluster | Fallout |

Prefer SetBlock over SetBlockRaw when mesh must update (product inject lesson).

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
| `AddFallingBlock` / `LetBlocksFall` | 38 / 220 | Collapse storms |
| `EntityFallingBlock` OnUpdateEntity | 300+ | Entity cost |

## Related docs

| Doc | Role |
|---|---|
| [protocol-packages.md](protocol-packages.md) | `NetPackageChunk` / `WorldInfo` wire |
| [protocol.md](protocol.md) | join path that attaches chunk observers |
| [network.md](network.md) | UpdateTick placement of SendChunks |
| [save-region.md](save-region.md) | Chunk write/read; blob codec shared with NetPackageChunk |
| [terrain-height.md](terrain-height.md) | YDim / height |
| `realearth-surfaces.md` | Product surfaces |

## Changelog

- **2026-07-28:** `SendChunksToClients` per-observer remove/load/reload/map pipeline; ChunkObserver fields; 3-package first-load throttle.

- **2026-07-19:** Related docs table.
- **2026-07-18:** Chunk/world family narrative consolidating loop + surfaces RE.
