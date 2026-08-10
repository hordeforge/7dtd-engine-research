# Tile entities and the power system (dedicated V3.1.0)

**Owns:** the `TileEntity` model (the per-block state objects a chunk carries),
the `TileEntityType` registry and `InstantiateFromRead` factory, per-tick update
driving, and the electricity system (`PowerManager`, the `PowerItem` circuit
forest, sources, consumers, triggers, and powered traps). Covers how a workstation
or forge crafts, how a source feeds consumers over wires, and how a trigger arms
and fires a trap.
**Not:** the per-chunk binary chunk format and region files (owned by
[`save-region.md`](save-region.md)); the chunk load/unload/tick pipeline that
schedules the update (owned by [`world-chunks.md`](world-chunks.md)); the block
XML that supplies `RequiredPower`, fuel values, and recipes (content); the in-game
`XUiC_*` window controllers (client UI).
**Evidence:** `TileEntity*`, `PowerManager`, `PowerItem`, `Power*`,
`Chunk.UpdateTick` IL (19 `TileEntity*` types plus the power classes; dump locally
with `tools/src/DumpMethod`, git-ignored). **Hub:** [`INDEX.md`](INDEX.md).
**Method:** [`re-methodology.md`](re-methodology.md).

Tile entities are a core server codepath: they are ticked on the authority, saved
inside the chunk, and replicated to clients. The power graph is a second, global
structure that lives beside the chunks and is saved to its own file.

---

## 1. The TileEntity model

A `TileEntity` is a heap object attached to one block position that holds state a
`BlockValue` cannot: an inventory, crafting progress, an owner, a power link. Each
chunk owns its tile entities in `Chunk.tileEntities`, a `DictionaryList<Vector3i,
TileEntity>` keyed by chunk-local position. The base carries `chunkPos`
(local `Vector3i`), a read version, and `heapMapUpdateTime` (used to rate-limit
AI heat-map events), plus lock/owner and listener plumbing.

Ticking is driven from the world tick, not from any per-entity scheduler:

```mermaid
flowchart LR
  OUT["World.OnUpdateTick<br/>(per active chunk)"] --> CUT["Chunk.UpdateTick<br/>(profiler tag TeTick)"]
  CUT --> LOOP{"for te in Chunk.tileEntities.list"}
  LOOP --> TU["te.UpdateTick(world)"]
  TU --> WS["Workstation: fuel + recipe queue"]
  TU --> FG["Forge: smelt materials"]
  TU --> PW["Powered: relink PowerItem, wires"]
  TU --> VM["VendingMachine: rent expiry"]
```

`Chunk.UpdateTick` (**IL=26**, profiler tag `TeTick`) walks
`tileEntities.list` in order and calls `te.UpdateTick(world)` for each. Most
concrete types override it; the base is a no-op. So a chunk with
no active machines still pays a bounded loop over its tile-entity list.

**Per-subclass `UpdateTick` bodies (V3.1.0 b14, IL-verified):**

| Subclass | UpdateTick IL | What the body does (called methods) |
|---|---:|---|
| `TileEntity` (base) | 1 | no-op |
| `TEFeatureAbs` (base) | 1 | no-op (feature-level tick hook) |
| `TileEntityPoweredBlock` | 4 | thin passthrough: `TileEntityPowered::UpdateTick(world)` only (the block `ActivateBlock` calls live in `Activate`/`ActivateOnce`/`OnSetLocalChunkPosition`, not the tick) |
| `TileEntityPowered` | 26 | power base: `ConnectionManager.IsServer` gate; `Audio.Manager.Broadcast` + wire relink (`IPowered`/`PowerManager` calls); GUI tooltip on local |
| `TileEntityPowerSource` | 32 | power graph: `ClientPowerData` fuel/`CurrentFuel`/`IsOn`/`ItemSlots` refresh against the `Chunk.GetBlock` read, battery/consumption bookkeeping |
| `TEFeatureDoor` | 28 | auto-close: `Block.HandleTrigger` + `BlockTrigger.Unlock` with `isMultiBlock`/`multiBlockPos`/`shape` resolution; `Audio.Manager.BroadcastPlayByLocalPlayer` for open/close |
| `TEFeatureLandClaim` | 24 | claim upkeep: `Block.MaxDamage`/`damage` read, decay/repair bookkeeping, `ConnectionManager.SendPackage` for bounds sync |
| `TEFeatureStorage` | 84 | loot container: item/loot-stage processing, `EntityAlive.FireEvent` hooks, `Audio.Manager.BroadcastPlayByLocalPlayer` open sound |
| `TileEntityCollector` | 7 | dispatcher: base tick + `HandleUpdate(world)` (**IL=120**), which does mod-changed rescan, `Block.IsUnderwater` + sky-blocked checks, per-output-type `handleUpdateForOutputType` (fuel/production), and start/stop of the `ActivateSound`/`RunningSound` broadcasts |
| `TileEntityComposite` | 24 | composite: fan-out to the feature set via the `<>c__DisplayClass46_0` closure over `Block.GetBlockName`/`blockID` dispatch |
| `TileEntityForge` | 340 | smelt timer: `BlockValue.get_meta`/`set_meta` progression, `GameTimer.ticks` scheduling, `IGameManager.PlaySoundAtPositionServer` on completion |
| `TileEntityVendingMachine` | 25 | rent expiry: `GameUtils.WorldTimeToDays` against `TraderData`, `ClearVendingMachine` when the rental elapsed (see [loot-economy.md](loot-economy.md) §4) |
| `TileEntityWorkstation` | 134 | fuel + recipe queue: `Block.FuelValue`/`HeatMapStrength`, `BlockWorkstation.UpdateVisible` for the active work light |

The forge (340) and workstation (134) dominate per-tick cost; everything else is
a bounded flag/refresher body.

**`Chunk.GetBlockEntity` (V3.1.0 b14)** is the read side of the registry:
the `Vector3i` overload (IL=10) looks up `blockEntityStubs.dict` keyed by
`GameUtils.Vector3iToUInt64(pos)` (null when absent); the `Transform`
overload (IL=30) linearly scans `blockEntityStubs.list` for the matching
`BlockEntityData.transform` (null when absent). `PrefabChunk` stubs both as
null; `ChunkCluster.GetBlockEntity` (IL=12) resolves the chunk (null chunk →
null) and delegates.
`Chunk.AddEntityStub(ecd)` (IL=5) appends to `entityStubs`;
`AddEntityBlockStub(ecd)` (IL=21) keys `blockEntityStubs` by
`GameUtils.Vector3iToUInt64(pos)` and, when a stub already occupies the cell,
**queues the old stub into `blockEntityStubsToRemove`** before `Set`-ing the
replacement (the deferred-removal pattern that lets a model swap clean up the
old transform later);
`RemoveEntityBlockStub(pos)` (IL=30) removes by the packed key (queuing the
removed entry in `blockEntityStubsToRemove`, warning
`Entity block on pos {0} not found!` on a miss).
`EnableEntityBlocks(on, name)` (IL=51) toggles every `blockEntityStubs` entry
whose lowercased transform name contains the filter (empty filter matches all)
and returns the count. `AddInsideDevicePosition(x, y, z, bv)` (IL=20) records
a `Vector3b` in `insideDevices` (+ hash set) and sets
`IsInternalBlocksCulled = true` (the POI-filler culled path).
`EnableInsideBlockEntities(on)` (IL=45) walks `insideDevices`, resolves each
entry's stub by packed world key, and `SetActive(on)`s every stub with a
transform (returning the count).
`removeBlockEntitesMarkedForRemoval()` (IL=133) drains
`blockEntityStubsToRemove` + `propEntitiesToRemove`: with occlusion culling on
the transforms go through `OcclusionManager.RemoveChunkTransforms`; each stub
`Cleanup()`s and pools its transform; each prop destroys its `PropReference`
and pools the game object; both lists clear.

**`GameUtils.Vector3iToUInt64(v)` (IL=29)** is the position key pack behind
the dict: each axis becomes `(coord + 32768) & 0xFFFF` (a 16-bit field with a
32768 offset so negative coordinates survive), combined as
`x << 32 | y << 16 | z` - the same pack used on the wire in
[`chunk-providers.md`](chunk-providers.md) `packedPos:u64`.
`GameUtils.UInt64ToVector3i(v)` (IL=27) is the exact inverse: each axis is
`((v >> shift) & 0xFFFF) - 32768`.

**TE transfer on block change (`GameManager.ChangeBlocks`, IL=530):** after
`SetBlock`, the engine compares the pre-change TE (`oldTE`, read before the
write) with the post-change TE (`newTE`). On the server the old one first gets
`ReplacedBy(newBV, oldBV, newTE)`; if the new block is air, the TE is removed
via `Chunk.RemoveTileEntityAt`; otherwise, when `oldTE != newTE` and
`newTE != null`, `newTE.UpgradeDowngradeFrom(oldTE)` moves state across.

`UpgradeDowngradeFrom` overrides: the base (IL=3) destroys the other TE
(`_other.OnDestroy()`). `TileEntityComposite` (IL=34) copies `Owner` and fans
to each module's `UpgradeDowngradeFrom(composite)`. `TileEntityCollector`
(IL=73) clones `worldTimeTouched` and the other collector's `Items` (resized to
this container; a size mismatch logs `UpgradeDowngradeFrom: other.size=...`).
`TileEntityVendingMachine` (IL=29) copies `IsLocked`, owner,
`allowedUserIds`, and `passwordHash` from any `ILockable` source and
`setModified()`.

**`UseLocalVersioning` (IL=15):** false when `readVersion == -1` (Read not yet
called; logs `[TileEntity] read must be called before using this.`), else true
when `readVersion >= 18`; it is the local-format gate read after `Read`.

**Registry writes:** `Chunk.AddTileEntity(te)` (IL=7) is
`tileEntities.Set(te.localChunkPos, te)`; `GetTileEntity(localPos)` (IL=11)
is the matching `TryGetValue` read (null on miss). Both remove paths flag `isModified`
and wrap `OnRemove(world)` between `IsRemoving = true` / false:
`RemoveTileEntityAt(world, pos)` (IL=28) looks up by local position and
`RemoveTileEntity(world, te)` (IL=29) by the entity's own local pos.

### 1.1 Type registry and factory

`TileEntityType` is a byte-valued enum. `TileEntity.InstantiateFromRead` reads the
type tag and switches (`type - 3`) to `newobj` the concrete class, else logs
`Dropping TE with unknown/outdated type` and returns null. `GetTileEntityType` on
each class returns its tag (authoritative for the write side).

| Tag | Enum name | Concrete class (instantiated) |
|---:|---|---|
| 3 | Collector | `TileEntityCollector` |
| 7 | VendingMachine | `TileEntityVendingMachine` |
| 8 | Forge | `TileEntityForge` |
| 12 | Workstation | `TileEntityWorkstation` |
| 15 | Powered | `TileEntityPoweredBlock` |
| 16 | PowerSource | `TileEntityPowerSource` |
| 17 | PowerRangeTrap | `TileEntityPoweredRangedTrap` |
| 18 | Light | `TileEntityLight` |
| 19 | Trigger | `TileEntityPoweredTrigger` |
| 20 | Sleeper | `TileEntitySleeper` |
| 21 | PowerMeleeTrap | `TileEntityPoweredMeleeTrap` |
| 25 | Composite | `TileEntityComposite` |

The enum also defines `None(0)`, `LandClaim(4)`, `Loot(5)`, `Trader(6)`,
`Campfire(9)`, `SecureLoot(10)`, `SecureDoor(11)`, `Sign(13)`, `GoreBlock(14)`,
`SecureLootSigned(22)`, and `Taskboard(27)`. These tags have **no dedicated class
in the factory switch**: loot containers, secure loot, doors, signs, and similar
older tile entities are now feature modules on `TileEntityComposite` (type 25),
which precomputes its capabilities from a `TileEntityCompositeData` block template
and dispatches per-feature commands. So there is no standalone
`TileEntityLootContainer` / `TileEntitySecureLootContainer` class in this build;
those roles live inside the composite type.

The class hierarchy of the powered branch:

```mermaid
flowchart TB
  TE[TileEntity] --> TPW[TileEntityPowered]
  TE --> TWS[TileEntityWorkstation]
  TE --> TFG[TileEntityForge]
  TE --> TVM[TileEntityVendingMachine]
  TE --> TSL[TileEntitySleeper]
  TE --> TCO[TileEntityComposite]
  TE --> TCL[TileEntityCollector]
  TPW --> TPB[TileEntityPoweredBlock]
  TPW --> TPS[TileEntityPowerSource]
  TPB --> TLT[TileEntityLight]
  TPB --> TPT[TileEntityPoweredTrigger]
  TPB --> TMT[TileEntityPoweredMeleeTrap]
  TPB --> TRT[TileEntityPoweredRangedTrap]
```

---

## 2. Serialization and storage

Tile entities are **not** stored in a table of their own: they are written inside
the chunk blob, so their lifetime and disk location are the chunk's (see
[`save-region.md`](save-region.md) step 5 of `Chunk.write`, and
[`world-chunks.md`](world-chunks.md)). `Chunk.write` emits the tile-entity count,
then for each: the `GetTileEntityType` byte, then `te.write`. `Chunk.read` mirrors
this, calling `TileEntity.InstantiateFromRead(type)` per entry.

The base `TileEntity.write` / `read` is short and branches on the stream mode
(disk versus network):

| Order | Field | Width | Note |
|---|---|---|---|
| 1 | version | `u16` | current write version is **19**; read supports legacy `<= 18` (skips a stale `int`), `> 1` reads the heat-map time |
| 2 | `chunkPos` | `Vector3i` | chunk-local position (`StreamUtils.Write`) |
| 3 | `heapMapUpdateTime` | `u64` | disk mode only; network mode stops after `chunkPos` |

Each subclass chains to the base then appends its own body (inventories, owner,
flags, power data). `TileEntityLegacyUtils.TryReadLegacyType` is consulted first
during instantiate so older saves upgrade cleanly.

Replication uses `NetPackageTileEntity` (V3.1.0 wire; [protocol-packages.md](protocol-packages.md) §6.12; write IL=27 / read IL=24):

```text
handle : u8              // Setup default 255 when omitted
teWorldPos : Vector3i
teBlockId : i32          // V3.1.0 (absent on V3.0.1)
payloadLen : i32         // V3.1.0 (was u16 on V3.0.1)
payload : payloadLen bytes   // TileEntity.write(network stream mode)
```

`Setup(te, streamMode[, handle])` writes the TE into a pooled stream in the
requested mode. `ProcessPackage` (**IL=103**):

1. `GetTileEntity(teWorldPos)`; if null return.
2. If live block type != `teBlockId`: log warning and **drop** (stale TE after
   block change).
3. `SetHandle(handle)`; under lock on pooled stream, `te.read(reader,
   StreamModeRead 2 if remote world else 1)`.
4. `NotifyListeners()`; if server: `SetChunkModified`, then rebroadcast
   `Setup(te, StreamModeWrite=2, handle)` with flags **192** and optional
   position for interest (world-center pos when non-zero).

Because write is mode-aware, the network form omits disk-only heat-map time and
can include live `isPowered` (subclass bodies; see composite features inventory).

```mermaid
flowchart LR
  subgraph Chunk blob (save-region)
    CW[Chunk.write] --> CNT[te count]
    CNT --> TAG[type byte + te.write]
  end
  subgraph Network
    NP[NetPackageTileEntity.Setup<br/>StreamModeWrite=network] --> PP[ProcessPackage on peer]
  end
  TE[TileEntity state] --> CW
  TE --> NP
```

---

### 2.1 `ClientPowerData` and `TileEntityPowerSource` stream modes

`TileEntityPowerSource` (TE type 16) holds a nested `ClientPowerData` mirror used
for network and UI fuel/slot sync. Fields (DumpType):

| Field | Width | Role |
|---|---|---|
| `IsOn` | bool | generator/panel powered state |
| `MaxFuel` / `CurrentFuel` | u16 | generator only (`PowerItemTypes.Generator` = 5) |
| `SolarInput` | u16 | solar only (`PowerItemTypes.SolarPanel` = 6); maps from `PowerSolarPanel.InputFromSun` |
| `MaxOutput` / `LastOutput` | u16 | `PowerSource.MaxOutput` / `LastPowerUsed` |
| `AddedFuel` | u16 | client→server fuel add; cleared after apply |
| `SendSlots` | bool | whether `ItemSlots` follow on ToServer |
| `ItemSlots` | `ItemStack[]` | fuel/battery inventory slots |

`StreamModeWrite` / `StreamModeRead` enum order: **Persistency=0**, **ToServer/FromClient=1**,
**ToClient/FromServer=2** (DumpType field order).

**`TileEntityPowerSource.write` IL=98** (after base `TileEntityPowered.write`):

| Mode | Payload |
|---|---|
| **Persistency (0)** | `u16` **18** (local version stamp when not network) |
| **ToServer (1)** | `bUserAccessing:bool`, `AddedFuel:u16` (then zeroed), `SendSlots:bool`, if true `GameUtils.WriteItemStack(ItemSlots)` and clear `SendSlots` |
| **ToClient (2)** | `hasPowerSource:bool`; if true: `IsOn:bool`; if Generator: `MaxFuel:u16`, `CurrentFuel:u16`; if Solar: `InputFromSun:u16`; `WriteItemStack(Stacks)`; `MaxOutput:u16`; `LastPowerUsed:u16` |

**`read` IL=158** mirrors: ensures `ClientData` non-null; **FromClient (1)** applies
`AddedFuel` into `PowerGenerator.CurrentFuel` (clamped to `MaxFuel`), may
`SetSlots` from `ItemSlots`, `SetModified()`; **FromServer (2)** fills `ClientData`
IsOn/fuel/solar/slots/MaxOutput/LastOutput for UI. Disk path uses base TE versioning.

This is the wire shape inside `NetPackageTileEntity` payloads for power sources,

### 2.2 The `TileEntityComposite` envelope (V3.1.0 b14)

`TileEntityComposite` (TE type 25) wraps its feature modules in a versioned,
size-marked envelope (`write` IL=74 / `read` IL=479 with the save-id
`blockIdMapping`):

| Field | Width | Note |
|---|---|---|
| base `TileEntity` preamble | - | version u16 + chunkPos (+ heapMapUpdateTime on disk) |
| version | u16 | **18** on disk (Save mode); `UseLocalVersioning` reads/writes a local u16 on net; legacy path uses `GetLegacyForkVersion` |
| outer size marker | i32 | `ReserveSizeMarker(4)` / `FinalizeSizeMarker` |
| `blockId` | i32 | `teData.Block.blockID`; on read remapped through `blockIdMapping[blockId]` when provided; the resolved `Block.list` entry must be a `BlockCompositeTileEntity` (else `Log.Error` + skip) |
| owner | `PlatformUserIdentifier` | null in edit mode (`GameManager.IsEditMode`) |
| `featureCount` | u8 | `modulesInternalOrder.Length` |
| per feature | | `i32 NameHash` (`TileEntityFeatureData.NameHash`), per-feature i32 size marker, `ITileEntityFeature.Write/Read` payload |

**Read resilience (IL=479):** modules are initialized from the block first
when absent (`InitModulesFromBlock`). The **legacy path** (version < 17)
requires the stream feature count to equal the current definition (else
`Legacy composite TE ... has {N} features in stream but current definition
has {M}. Skipping TE payload.`) and matches each module position by
`NameHash`; the **modern path** (>= 17) resolves each hash through
`teData.GetFeatureIndex` - an unknown hash logs
`Block ... no longer defines feature hash 0x... Skipping payload.` and skips,
a module read failure is caught (`Module read failed for feature ...`) and
logged, and every level (`outer`, per-feature) validates its size marker
(`ValidateSizeMarker`), erroring on mismatch
(`... failed size validation: expected {0} B, read {1} B`). The per-feature
body layouts are in §4.7 below.
not a separate NetPackage type.

---

## 3. The power graph and PowerManager

Electricity is a **separate global structure** from the chunk store. `PowerManager`
(a singleton) holds a forest of `PowerItem` nodes wired parent to child, and saves
it to `power.dat` in the save directory, independent of any chunk file. A
`TileEntityPowered` in a chunk only holds a link to its `PowerItem` plus a cached
copy of its wire list and parent position; on load it reconnects by world position.

### 3.1 PowerManager structures

| Field | Type | Role |
|---|---|---|
| `Circuits` | `List<PowerItem>` | the **roots** of the forest (re-parenting removes a node from here) |
| `PowerSources` | `List<PowerSource>` | roots that generate power, ticked first |
| `PowerTriggers` | `List<PowerTrigger>` | trigger nodes, ticked after sources |
| `PowerItemDictionary` | `Dictionary<Vector3i, PowerItem>` | O(1) lookup by world position |

**Graph edit leaves:** `FindPowerItems(predicate, results)` (IL=25) filters
(the wire-node `Vector3EqualityComparer` singleton is the position comparer
`WireNode`/`WireManager` use for wire-point containment checks on their
`List<Vector3>` points).
the `PowerItemDictionary` values into the result list.
`GetPowerItemByWorldPos(pos)` (IL=12) is the dictionary lookup (null on
miss); `SetTileEntityUpdate(te, shouldUpdate)` (IL=14) adds/removes the TE
on the per-frame `ClientUpdateList`; `LogChildren(item)` (IL=65) prints
the tree `{indent}{item}({depth}) - Pos:{pos} | Powered:{bool}` recursively
(the `logpower`-style debug). `TileEntityPoweredBlock.OnSetLocalChunkPosition`
(IL=37) re-runs `Block.ActivateBlock(world, pos, bv, IsPowered, IsPowered)`
on the server when a chunk (re)loads the TE - the power-state relink.
`RemovePowerNode(node)` (IL=61) detaches every child
(`SetParent(child, null)`), then the node itself, and removes it from
`Circuits` plus `PowerSources` / `PowerTriggers` by type and from the
dictionary - the full teardown. `RemoveChild(child)` (IL=14) detaches the
child from its parent's `Children` and re-adds it as a circuit root (the
un-wire action). `savePowerDataThreaded` (IL=31) is the 120 s save worker:
pooled stream to `{saveDir}/power.dat` with a `.bak` backup first.
`TileEntityPowerSource.HasSlottedItems` (IL=24) is any non-empty slot;
`TryAddItemToSlot` (IL=50) delegates to `PowerSource.TryAddItemToSlot` on
the server, else writes into the client `ClientData.ItemSlots` (setting
`SendSlots`) when the source is off.

`PowerItemTypes` is the node kind (`PowerItem.CreateItem` is the factory):

| Value | Type | Node class |
|---:|---|---|
| 1 | Consumer | `PowerConsumer` (lamps, most powered blocks) |
| 2 | ConsumerToggle | `PowerConsumerToggle` (switch-gated) |
| 3 | Trigger | `PowerTrigger` |
| 4 | Timer | `PowerTimerRelay` |
| 5 | Generator | `PowerGenerator` |
| 6 | SolarPanel | `PowerSolarPanel` |
| 7 | BatteryBank | `PowerBatteryBank` |
| 8 | RangedTrap | `PowerRangedTrap` |
| 9 | ElectricWireRelay | `PowerElectricWireRelay` |
| 10 | TripWireRelay | `PowerTripWireRelay` |
| 11 | PressurePlate | `PowerPressurePlate` |

Generators, solar panels, and battery banks are `PowerSource` subtypes (they can
be roots); everything else consumes or relays.

### 3.2 The tick

`PowerManager.Update` runs only on the server, only with a started game and at
least one player, and only every **0.16 s** (about 6.25 Hz, decoupled from the
20 Hz sim tick). Per interval it updates every source, then every trigger; it
flushes queued client updates every frame; and it saves `power.dat` on a
background thread every 120 s.

```mermaid
flowchart TB
  U[PowerManager.Update] --> G{server + game started + players?}
  G -->|no| RET[return]
  G -->|yes| T{updateTime elapsed 0.16s?}
  T -->|no| CU
  T -->|yes| S[for each PowerSource: Update]
  S --> TR[for each PowerTrigger: CachedUpdateCall]
  TR --> CU[flush ClientUpdateList -> ClientUpdate]
  U --> SV{saveTime elapsed 120s?}
  SV -->|yes| ST[SavePowerManager on thread]
```

### 3.3 Source to consumer distribution

Distribution is a greedy depth-first walk from each source. A source generates up
to `MaxPower`, then offers `min(MaxOutput, CurrentPower)` to its children. Each
child takes `min(RequiredPower, available)`, marks itself powered only if it got
its **full** requirement, and passes the remainder down its own subtree. When the
budget hits zero the walk stops, so nodes nearer the source win.

```mermaid
flowchart TB
  SRC["PowerSource.HandleSendPower"] --> GEN["generate: CurrentPower up to MaxPower<br/>(TickPowerGeneration)"]
  GEN --> BUD["budget = min(MaxOutput, CurrentPower)"]
  BUD --> HPR["child.HandlePowerReceived(ref budget)"]
  HPR --> TAKE["consumed = min(RequiredPower, budget)"]
  TAKE --> POW{"consumed == RequiredPower?"}
  POW -->|yes| ON["isPowered = true"]
  POW -->|no| OFF["isPowered = false"]
  ON --> DEC["budget -= consumed"]
  OFF --> DEC
  DEC --> MORE{"budget > 0 and PowerChildren()?"}
  MORE -->|yes| REC["recurse into each child"]
  MORE -->|no| STOP["stop this branch"]
  REC --> HPR
  SRC --> DRAIN["CurrentPower -= LastPowerUsed"]
```

`PowerItem.PowerChildren` (base IL=2) always returns **true**. Subtypes do **not**
override it for the common switch/trigger cases on V3.1.0 b14 (verified: no
`PowerConsumerToggle.PowerChildren` method; `PowerTrigger.PowerChildren` also
returns true). Branch gating is therefore **not** via `PowerChildren`:

| Gate | Where | Effect |
|---|---|---|
| **Full requirement** | `HandlePowerReceived` | `isPowered = (consumed == RequiredPower)`; partial power blacks the node |
| **Toggle switch** | `PowerConsumerToggle.HandlePowerUpdate` | TE `Activate` uses `isPowered && isToggled`; children still get `HandlePowerUpdate(parentIsOn)` |
| **Trigger active** | `PowerTrigger.HandlePowerUpdate` | non-trigger children only updated when `get_IsActive()`; trigger children always get parent-trigger link |
| **Solar light** | `PowerSolarPanel.HandleSendPower` | early-out if `!HasLight` (after periodic `CheckLightLevel`) |

When a node's `isPowered` flips, `IsPoweredChanged` + `TileEntity.SetModified` run
so state is saved and replicated.

### 3.4 Source on/off state and subtype tick table

A source that is on generates and distributes; if it should auto turn off (a
generator with `CurrentFuel == 0`) it zeroes its power and flips off. Solar does
not use `ShouldAutoTurnOff` for daylight; it gates inside `HandleSendPower`.

```mermaid
stateDiagram-v2
  [*] --> Off
  Off --> On: player switches on (IsOn = true)
  On --> Generating: CurrentPower < MaxPower -> TickPowerGeneration
  Generating --> Distributing: offer min(MaxOutput, CurrentPower) to children
  Distributing --> On: LastPowerUsed drained from CurrentPower
  On --> AutoOff: ShouldAutoTurnOff (generator fuel empty)
  AutoOff --> Off: CurrentPower = 0, IsOn = false
  On --> Off: player switches off
```

**`PowerSource.Update` IL=28:** `HandleSendPower()` then, if `hasChangesLocal`,
`HandlePowerUpdate(IsOn)` on each child and clear the flag.

**`PowerSource.HandleSendPower` IL=86** (base path):

1. Return if `!IsOn`.
2. If `CurrentPower < MaxPower`: virtual `TickPowerGeneration()`; if above max, clamp.
3. If `ShouldAutoTurnOff()`: `CurrentPower=0`, `IsOn=false`.
4. If `hasChangesLocal`: `budget = min(MaxOutput, CurrentPower)`; for each child
   `HandlePowerReceived(ref budget)`; accumulate `LastPowerUsed`.
5. `CurrentPower -= LastPowerUsed`.

| Type | Tick / override | Generation / auto-off (IL) |
|---|---|---|
| `PowerSource` | `Update` -> `HandleSendPower` | base `TickPowerGeneration` empty (IL=1-ish); `ShouldAutoTurnOff` always **false** (IL=2) |
| `PowerGenerator` | same | `TickPowerGeneration` IL=30: if room and `CurrentFuel>0`, burn **1** fuel, add `OutputPerFuel` to `CurrentPower`. `ShouldAutoTurnOff` = (`CurrentFuel == 0`) |
| `PowerSolarPanel` | **override** `HandleSendPower` IL=111 | Every **2 s** (`lightUpdateTime`) call `CheckLightLevel`: `Chunk.GetLight(..., LIGHT_TYPE=1)` into `sunLight`; `HasLight = (sunLight==15 && World.IsDaytime())`. On light loss: zero power + `HandleDisconnect`. Only if `HasLight`: same generate/distribute as base. `TickPowerGeneration` IL=8: if `HasLight`, `CurrentPower = MaxOutput` (full fill, not incremental) |
| `PowerBatteryBank` | `Update` IL=22 | If has **Parent** and incoming power: while on, `AddPowerToBatteries(LastInputAmount)` then return (does **not** run base source distribute). If root (no parent): `PowerSource.Update`. `TickPowerGeneration` IL=76: discharge batteries by raising `ItemValue.UseTimes`, add `n * OutputPerCharge` to `CurrentPower`. `HandlePowerReceived` IL=89: when on, take `min(InputPerTick, available)` into batteries, then pass remainder to children |
| `PowerConsumer` | `HandlePowerUpdate` IL=51 | `Activate(isPowered && parentIsOn)`; edge `ActivateOnce`; always recurse children if `PowerChildren()` |
| `PowerConsumerToggle` | `HandlePowerUpdate` IL=53 | Activate uses `isPowered && parentIsOn && isToggled`; still recurses children with **parent** `isOn` (toggle does not cut child power budget; only local TE activation) |
| `PowerConsumerSingle` | `HandlePowerUpdate` IL=41 | one-shot `ActivateOnce` on rising edge of `isPowered`; recurse children |
| `PowerTrigger` | `CachedUpdateCall` IL=77 (from manager) + `HandlePowerUpdate` IL=72 | Manager path only for types 1 and 3..4 band: edge-detect trigger, delay/duration timers via `Time.time`, `HandleDisconnectChildren` when duration ends. `get_IsActive`: type 0 uses `isTriggered`; else `isActive \|\| parentTriggered` |
| `PowerTimerRelay` | `CachedUpdateCall` IL=12 | every **1 s** (`updateTime`) call `CheckForActiveChange` |
| `PowerElectricWireRelay` | (consumer) | no extra fields; pure consumer relay |
| `PowerTripWireRelay` | (trigger) | no extra fields beyond `PowerTrigger`; the tripwire `TripWireController` MonoBehaviour is added by `TileEntityPowered` on the wire node's GameObject (`TileEntityParent` / `TileEntityChild` / `WireNode` fields) and fires `checkIfTriggered` from `OnTriggerEnter` / `OnTriggerStay`: it resolves the collider's `EntityAlive` (self, parent, then children fallbacks; driver-less vehicles ignored) and, gated on `ConnectionManager.IsServer` + `TileEntityParent.IsPowered()`, sets `TileEntityChild.IsTriggered = true` |
| `PowerPressurePlate` | (trigger) | fields `pressed` / `lastPressed` |
| `PowerRangedTrap` | (consumer) | slots + `TargetType` + `isLocked` on disk; TE activate path via consumer |

`PowerManager.Update` IL=106: early-out if no world/players; **server + game
started** only for the 0.16 s source/trigger loop and 120 s save; **every frame**
flushes `ClientUpdateList` -> `TileEntityPoweredBlock.ClientUpdate` (also on
client connection path).

### 3.5 Graph persistence and subtype disk tails

Path `{SaveGameDir}/power.dat`. `SavePowerManager` (IL=41) serializes via `Write`
into a pooled stream and starts thread `powerDataSave`; the worker copies any
existing file to `power.dat.bak` then `StreamUtils.WriteStreamToFile`.
`LoadPowerManager` (IL=70) opens `power.dat`, else `power.dat.bak`.

**`PowerManager.Write` (IL=35) / `Read` (IL=34):**

```text
fileVersion : u8          // PowerManager.FileVersion
rootCount : i32           // Circuits.Count
// per root:
  powerItemType : u8
  PowerItem.write / read (recursive)
```

**`PowerItem.write` (IL=55) recursive:**

```text
blockId : u16
position : Vector3i
hasParent : bool
if hasParent: parentPos : Vector3i
childCount : u8
// per child: powerItemType:u8 + PowerItem.write
```

**Subtype write tails** (after base `PowerItem` / `PowerSource` / `PowerTrigger`):

| Type | Extra disk fields |
|---|---|
| `PowerSource` | `CurrentPower:u16`, `IsOn:bool`, `Stacks` (`WriteItemStack`) |
| `PowerGenerator` | + `CurrentFuel:u16` |
| `PowerSolarPanel` | + `sunLight:u8` (only if file version >= 2 on read) |
| `PowerConsumerToggle` | + `isToggled:bool` |
| `PowerTrigger` | `TriggerType:u8`; if type==0: `isTriggered:bool` else `isActive:bool`; if type!=0: delay:u8, duration:u8, `delayStartTime:f32`, `powerTime:f32`; if type==3: `TargetType:i32` |
| `PowerTimerRelay` | + `StartTime:u8`, `EndTime:u8` |
| `PowerRangedTrap` | `isLocked:bool`, `Stacks`, `TargetType:i32` |

`Read` rebuilds with `CreateItem` per node and `AddPowerNode`, which registers
the node in `Circuits`, in `PowerSources` / `PowerTriggers` if applicable, and in
`PowerItemDictionary`; `SetParent` enforces no cycles via `CircularParentCheck` and
pulls a re-parented node out of the roots list.

### 3.6 Wire edit package (`NetPackageWireActions`)

Write IL=45 / read IL=38 / ProcessPackage IL=163.

```text
currentOperation : u8   // WireActions: 0 SetParent, 1 RemoveParent, 2 SendWires
tileEntityPosition : Vector3i
childCount : u8
// childCount x Vector3i wireChildren
wiringEntityID : i32    // omitted when operation == SendWires (2)
```

**Server process** (`ConnectionManager.IsServer`):

| Op | Behaviour |
|---|---|
| **SetParent (0)** | Resolve/create `PowerItem` for `tileEntityPosition` and first `wireChildren[0]`; `PowerManager.SetParent(child, parent)`; refresh wire TE data (`CreateWireDataFromPowerItem` / `SendWireData` / `RemoveWires` / `DrawWires`) on old parent and new parent |
| **RemoveParent (1)** | `RemoveSelfFromParent` on item at position; refresh former parent's wire TE |
| **SendWires (2)** | (falls through to client path only in this method) |

**Client path:** if op is **SendWires**, `IPowered.SetWireData(wireChildren)` on TE at
position (visual wire list only).

---

### 3.7 Block wrappers: which block owns which tile entity

Each power block's `CreateTileEntity` pins the runtime `TileEntity*` class
and its `PowerItemType` / `TriggerType` identity (the identity keys the
subtype behaviour of §3.4). The `PowerItemType` literals seen in the
wrappers: speaker **1**, spotlight **2**, generator **5**, solar panel **6**,
battery bank **7**, launcher **8**, electric wire **9**, trip wire **10**.

**Read side (`TileEntityPoweredTrigger.CreatePowerItem`, IL=95):** the
trigger TE resolves its own identity back from the block at its position:
`BlockPressurePlate` -> TriggerType **1**, `BlockMotionSensor` -> **3**,
`BlockTripWire` -> **4**, `BlockTimerRelay` -> **2**, `BlockSwitch` -> **0**
(the run-time mirror of the wrapper table below), then instantiates the
matching power item: `PowerTimerRelay` (2), `PowerTripWireRelay` (4),
`PowerTrigger` (3, with `TriggerPowerDuration = 1` and `TriggerPowerDelay
= 0` defaults), `PowerPressurePlate` (1) or a plain `PowerTrigger`.

- **Sources** (`TileEntityPowerSource`): `BlockBatteryBank` (PowerItemType
  7), `BlockGenerator` (5) and `BlockSolarPanel` (6) all lazily resolve
  `SlotItemName` into the `slotItem` class and hand it to the TE (IL=19
  each). `BlockSolarPanel.CanPlaceBlockAt` (IL=28) additionally requires
  sky light >= 15 (`ChunkCache.GetLight(pos + up, SkyLight)`) on top of the
  base placement check: panels only go where the sky is exposed.
- **Consumers** (`TileEntityPoweredBlock`): `BlockSpeaker` (PowerItemType
  1) reads a `PlaySound` property in `Init` (IL=16) and `ActivateBlock`
  (IL=53) stores the on/off bit in block meta bit 1, `SetBlockRPC`s the
  change and runs `Audio.Manager.BroadcastPlay` / `BroadcastStop` of that
  sound at the block position (looping ambient).
  `BlockSpeakerTrader` (Init IL=42) is a plain `Block`: it only parses
  `OpenSound` / `CloseSound` / `WarningSound` and plays them from
  `PlayOpen` / `PlayClose` / `PlayWarning` (trader-door ambience, no power
  graph).
  `BlockSpotlight` (PowerItemType 2) is the richest consumer wrapper:
  `OnBlockActivated` (IL=127) handles the `light` (toggles meta bit 1 and
  the TE's `IsToggled`), `aim` (sets `AimingGun` and
  `LockManager.LockRequestLocal` on the TE) and `take` (block
  `takeItemWithTimer` with `BlockPowered.TakeDelay`) commands, resolving
  multiblock children to the parent first; `updateState` (IL=249) writes
  the on/off meta bit with `switch_up` / `switch_down` head sounds, lazily
  creates the TE (`WindowGroupToOpen = XUiC_PoweredSpotlightWindowGroup.ID`),
  initializes a `SpotlightController` from the block properties,
  instantiates shared materials per renderer for `_EmissionColor`
  white/black, and drives the `MainLight` child's `LightLOD.SwitchOnOff`.
- **Triggers** (`TileEntityPoweredTrigger`): `BlockPressurePlate` sets
  `TriggerType` **1**, `BlockTimerRelay` **2**, `BlockMotionSensor` **3**
  (IL=6 each), `BlockTripWire` **4** plus PowerItemType 10 (IL=9); the
  trigger behaviour lives in the TE ticks of §3.4 / §5.
- **Traps**: `BlockLauncher` (PowerItemType 8,
  `TileEntityPoweredRangedTrap`): `InstantiateProjectile` (IL=188) bails
  unless the TE is unlocked, on the server `DecrementAmmo` (unlocking and
  `SetModified` when empty), clones the ammo class model onto the block
  transform, adds a `BlockProjectileMoveScript` (itemProjectile,
  itemValueProjectile, the `ItemActionProjectile` from action slot 0 or 1,
  `ProjectileOwnerID` from the TE) and fires it at the block position plus
  (0.5, 0.5, 0.5) along the transform forward, `BroadcastPlay(playSound)`
  on the server. `BlockElectricWire` (PowerItemType 9,
  `TileEntityPoweredMeleeTrap`) parses `BrokenPercentage` (default 0.25,
  clamped 0..1) in `Init` (IL=25), the chance a damaged wire stays
  non-conductive.
- **`BlockRallyMarker`** is a quest block, not a power block:
  `OnBlockActivated` (IL=29) with command `activate` calls
  `QuestEventManager.HandleRallyMarkerActivate(player, pos, blockValue)`
  when `QuestJournal.HasQuestAtRallyPosition(pos, true)` finds an
  un-activated rally quest and the player has no active quest
  ([quests-challenges.md](quests-challenges.md)).

---

## 4. Workstation and forge crafting

### 4.1 `TileEntityWorkstation.UpdateTick` (IL=134)

Fields: `fuel` / `input` / `tools` / `toolsNet` / `output` (`ItemStack[]`),
`queue` (`RecipeQueueItem[]`), `lastTickTime:u64`, `currentBurnTimeLeft:f32`,
`isBurning`, `isBesideWater`, `isModuleUsed:bool[]`, `CraftCompleteList`.

**Workstation accessors (all IL-verified):** `CanOperate` (IL=3) is
`isBurning`. `AcceptsMaterial(material)` (IL=31) matches
`material.ForgeCategory` (case-insensitive) against `materialNames`.
`getFuelTime(stack)` (IL=46) reads `FuelValue` for an item or `Block.FuelValue`
for a block; `GetFuelTime` (IL=11) is `ItemClass.GetFuelValue(iv)`.
`getTotalFuelSeconds` (IL=41) sums `GetFuelValue * count` over the fuel
slots. `hasRecipeInQueue` (IL=31) is any `queue` entry with
`Multiplier > 0` and a non-null `Recipe`. `InputIsEmpty` (IL=57): the
`input.length - materialNames.length` non-material slots must be empty and
the material slots must each hold `count >= 10` of a real item (the
workstation refuses to run on tiny partial loads).
`readItemStackArray(br, ref stack)` (IL=59/54) reads the count byte,
resizes, and reads the `ItemStack`s - skipping the actual reads while
`bWaitingForServerResponse` / `bUserAccessing` (the net-optimized read).
`SetDataFromNet` (IL=20) copies `toolsNet` into `tools` when they differ
(`visibleChanged = true`) and refreshes the visible tools.

`isModuleUsed[3]` is the **fuel module** gate used throughout the tick (index 3
checked before fuel math and before final `isBurning` clear).

Ordered path (verified):

1. Early continue only when fuel module off **and** no recipe in queue **and** not burning.
2. `timePassed = (GameTimer.ticks - lastTickTime) / 20` (seconds at 20 TPS).
3. If fuel module on: `timePassed = min(timePassed, BurnTotalTimeLeft)` so craft
   cannot outrun remaining burn seconds.
4. `isBesideWater = TileEntity.IsByWater(world, pos)`; if burning and beside water
   force `isBurning = false`.
5. `UpdateLightState(world, block)` (block glow).
6. If fuel module: `HandleFuel(world, timePassed)`.
7. If `block.HeatMapStrength > 0` and `IsCrafting`: `emitHeatMapEvent` (AIDirector).
8. `HandleRecipeQueue(timePassed)` then `HandleMaterialInput(timePassed)`.
9. If fuel module and burning but `BurnTotalTimeLeft <= 0`: force `isBurning = false`.
10. Store `lastTickTime = GameTimer.ticks`.
11. `setModified()` if fuel module on or queue non-empty or burning; `UpdateVisible()`.

**`TileEntity.emitHeatMapEvent(world, eventType)` (IL=48)** is the shared
heat contribution: when `world.worldTime < heapMapLastTime` (time rewound)
it resets `heapMapUpdateTime = 0`, and once `world.worldTime >=
heapMapUpdateTime` with an AIDirector present it calls
`NotifyActivity(eventType, ToWorldPos(), block.HeatMapStrength, 720)`, then
records `heapMapLastTime = worldTime` and
`heapMapUpdateTime = worldTime + AIDirector.GetActivityWorldTimeDelay()` -
the emission cadence follows the global activity delay (`GameStats` 11,
[`aidirector.md`](aidirector.md)), so hot TEs report at most once per delay
window, and the 720 is the heat-duration ticks (36 s at 20 TPS) for the
`NotifyActivity` call.

```mermaid
flowchart TB
  UT[Workstation.UpdateTick IL=134] --> DT["timePassed = (ticks - lastTickTime) / 20"]
  DT --> CLAMP["fuel module: min with BurnTotalTimeLeft"]
  CLAMP --> WATER["IsByWater -> may force isBurning off"]
  WATER --> LIGHT[UpdateLightState]
  LIGHT --> FUEL["HandleFuel if isModuleUsed[3]"]
  FUEL --> HEAT{HeatMapStrength > 0 and IsCrafting?}
  HEAT -->|yes| EMIT[emitHeatMapEvent]
  HEAT -->|no| QUEUE
  EMIT --> QUEUE[HandleRecipeQueue]
  QUEUE --> MAT[HandleMaterialInput]
  MAT --> MOD[setModified if active]
```

### 4.2 `HandleFuel` (IL=105)

- If not burning: return false (no heat emit).
- If burning: `emitHeatMapEvent(world, enum 0)` then burn loop:
  - Subtract `_timePassed` from `currentBurnTimeLeft`; quantize to 0.01 s via
    `FloorToInt(burn * 100) / 100`.
  - While burn time negative and total fuel seconds remain: consume one unit from
    `fuel[0]` (or `cycleFuelStacks` when count 0), add `GetFuelTime(stack)`,
    invoke `FuelChanged` if subscribed.
  - If total fuel seconds and current burn both exhausted: clamp burn to 0.
- Returns whether any fuel state changed.

**`BlockCollector/FuelType`** (ctor IL=41) is the fuel-class definition: the
comma-separated `ftDef` string splits so element 0 becomes `Name` and the
rest become the `Items[]` list (trimmed) - the "what burns in a collector"
map that `TileEntityCollector` / `BlockCollector` read (see the collector
stream tails below).

**`BlockCollector/CatalystConvert`** (`Convert(ItemStack)` IL=23) is the
catalyst rule: when the input stack is non-empty and its item class name
equals `convertFrom`, the output is `new ItemStack(GetItem(convertTo),
count)` - the collector's catalyst-to-output conversion, used by
`TileEntityCollector` / `XUiC_CollectorFuelGrid`.

**`WorkstationData`** is the workstation display config record
(`WorkstationName`, `WorkstationIcon`, `CraftIcon`, `CraftActionName`,
`WorkstationWindow`, plus the `OpenSound` / `CloseSound` / `CraftSound` /
`CraftCompleteSound` audio ids): `BlockWorkstation` owns one instance
(ctor from name + `DynamicProperties`) that `CraftingManager` and the
workstation UI read, and `ConsoleCmdWorkstationMaterials` prints.

### 4.3 `HandleRecipeQueue` / `cycleRecipeQueue`

`HandleRecipeQueue`: no-op while `bUserAccessing`. Active slot is last non-empty
queue entry. Requires fuel module off **or** `isBurning`. Decrements
`CraftingTimeLeft` by `timePassed`. When `CraftingTimeLeft <= 0` and
`Multiplier > 0`:

- Build output `ItemStack` from `Recipe.itemValueType` / `Recipe.count` / quality.
- `ItemStack.AddToItemStackArray(output, ...)`.
- `AddCraftComplete(StartingEntityId, item, recipeName, scrapName?, craftExpGain, count)`.
- Analytics: `GameSparksCollector.IncrementCounter` (client/telemetry; no-op harm on dedi).
- `Multiplier--`; reset `CraftingTimeLeft += OneItemCraftTime`.
- If `Multiplier == 0`: `cycleRecipeQueue()` (shift queue down, clear tail, mark next
  `IsCrafting` if Multiplier and Recipe present).

**`CheckForCraftComplete(player)` (IL=55) delivers finished crafts to the
owner** (called on the workstation's client-UI open): it walks
`CraftCompleteList` backward and, for each entry whose `CrafterEntityID`
matches the player, unlocks the scrapped-item cosmetic
(`equipment.UnlockCosmeticItem(GetItemClass(ItemScrapped))`), calls
`player.GiveExp(entry)` (the `_xpFromCrafting` grant, see
[crafting-recipes.md](crafting-recipes.md)), removes the entry, and marks the
TE modified - so a player who crafted at a workstation and walked away gets
the cosmetic unlock and XP when they next open it.

```mermaid
stateDiagram-v2
  [*] --> Idle
  Idle --> Queued: add recipe (Multiplier, CraftingTimeLeft = OneItemCraftTime)
  Queued --> Burning: fuel module off OR isBurning
  Burning --> Burning: CraftingTimeLeft -= timePassed
  Burning --> ItemDone: CraftingTimeLeft <= 0
  ItemDone --> Burning: output + AddCraftComplete, Multiplier--, reset timer
  ItemDone --> Advance: Multiplier == 0
  Advance --> Burning: cycleRecipeQueue
  Advance --> Idle: queue empty
  Burning --> Paused: fuel exhausted or beside water
  Paused --> Burning: fuel replenished
```

**Workstation queue/timer leaves (all IL-verified):**
`ResetCraftingQueue()` (IL=42) fills every `queue` slot with an empty
`RecipeQueueItem` (null recipe, 0 multiplier / times, not crafting);
`ResetTickTime()` (IL=5) stamps `lastTickTime = GameTimer.Instance.ticks`;
`ClearSlotTimersForInputs()` (IL=19) zeroes `currentMeltTimesLeft[]` and
`GetTimerForSlot(slot)` (IL=13) reads it (0 out of range).
`IsToolsSame(tools)` (IL=37) is same-length element-wise stack equality;
`OutputEmpty()` (IL=23) is every output slot empty;
`get_IsEmpty()` (IL=31) is no recipe in the queue and `isEmpty` across fuel /
tools / output plus `InputIsEmpty()` (IL=57: the first
`input.Length - materialNames.Length` slots empty, the material tail empty
or count < 10); `get_IsCrafting()` (IL=15) is
`hasRecipeInQueue() && (isModuleUsed[3] ? isBurning : true)`;
`get_BurnTimeLeft()` (IL=3) reads `currentBurnTimeLeft`.
`readRecipeStackArray(reader, version, ref queueStack)` (IL=79) reads the
count byte, reallocates the queue on a length change, and per entry runs
`RecipeQueueItem.Read` (version >= 50) or `ReadLegacy`; with
`bWaitingForServerResponse` it consumes the entries into a scratch item
instead (the client keeps its pending queue untouched).

### 4.4 `TileEntityForge.UpdateTick` (IL=340)

Separate type (not a workstation subclass). Fuel is **tick-integer** based:
`fuelInStorageInTicks`, `fuelInForgeInTicks`, `burningItemValue`.

**Forge accessors (all IL-verified):** `GetFuelLeft(worldTimeInTicks)`
(IL=30) is `fuelInForgeInTicks / 20`, minus the ticks elapsed since
`lastTickTimeDataCalculated` when that is set (clamped at 0) - the
"seconds of burn remaining" the UI reads. `GetMetalForgedSoFar(tickTime)`
(IL=45) is `moldedMetalSoFar + elapsed * 0.1` (0.1 metal per tick),
clamped to `metalInForge` while operating or to `outputWeight` otherwise.
`GetInputWeight` / `GetOutputWeight` / `GetBurningItemValue` (IL=3 each)
are the `inputMetal` / `outputWeight` / `burningItemValue` fields.

Path:

1. `recalcStats()`; if first tick (`lastTickTime == 0`) seed from `GameTimer.ticks`.
2. `dtTicks` from timer delta; `updateLightState`.
3. While storage or forge fuel ticks remain: `emitHeatMapEvent` (enum 1 while hot).
4. Consume forge fuel: `fuelInForgeInTicks -= min(dt, fuelInForge)` style drain;
   when empty, `moveDown(fuel)`, take next stack, set `burningItemValue`,
   `fuelInForgeInTicks = ItemClass.GetFuelValue(item) * 20` (seconds->ticks at 20 TPS),
   decrement stack count / Clear when empty.
5. Material melt: when `outputWeight` path active, rate uses `0.1` mold factor;
   `moveDown(input)`, add `ItemClass.GetWeight()` into `metalInForge`, consume input.
6. `recalcStats()`; light update when forge fuel hits zero.

### 4.5 Other TE ticks (IL-sized)

| Type | UpdateTick | Behaviour |
|---|---:|---|
| `TileEntityPowered` | 26 | If transform: `wiresDirty` -> `DrawWires`; `activateDirty` -> `Activate(PowerItem.IsPowered)` |
| `TileEntityPoweredBlock` | 4 | base only |
| `TileEntityVendingMachine` | 25 | Non-player-owned rentable: if `rentalEndDay <= WorldTimeToDays(worldTime)` -> `ClearVendingMachine` |
| `TileEntityComposite` | 24 | For each `modulesInternalOrder`: `ITileEntityFeature.UpdateTick` |
| Loot / Sign / Trader | (none) | No override; base no-op |
| `TileEntityCollector` | (large) | Converter slots; see §4.6 wire |
| `TileEntityLight` | (none / presentation) | Light params on disk/net; see §4.6 |
| `TileEntityPoweredRangedTrap` | (powered) | Ammo + target mask; see §4.6 |
| `TileEntityPoweredMeleeTrap` | (powered) | owner only on wire |

### 4.6 Collector, light, trap stream tails

#### `TileEntityCollector.write` (IL=278)

After base TE write + version u16 (persist path):

```text
lastWorldTimes.count : u16
// per entry: key:string, worldTime:u64
fillDataLookup.count : u16
// per entry: key:string, slot:u32, fillTime:u32, fillTimeLeft:u32
isUnderwater : bool
isBlocked : bool
outOfFuel.count : u16
// per entry: key:string, flag:u8
isFull.count : u16
// per entry: key:string, flag:u8
// then four ItemStack arrays (count:i16 + ItemStack.Write each):
//   itemsInternal, modSlotsInternal, fuelSlotsInternal, catalystSlotsInternal
```

**`TileEntityCollector` conversion loop (all IL-verified):**
`handleUpdateForOutputType(world, outputType, slotIndices)` (IL=233) is the
per-output tick. It resolves the `FuelType` via `collector.GetFuelType(
outputType.Fuel)`, sets `outOfFuel[name] = !(getMaxProductionCount > 0)`
and `isFull[name] = getFirstFreeIndex(slotIndices) < 0`, and latches
`wasDisabled` (calling `setModified()` on the disabled -> enabled edge).
It then folds the elapsed world time into the conversion budget:
`convertTime = GetSandboxModifiedTime((worldTime - lastWorldTimes[name]) *
getCurrentConvertSpeed)` (a negative result keeps the raw value and flags
"keep going"). Per conversion: a `FillData(name, slot, fillTimeLeft)` is
created with the first free slot and `RandomRange(MinConvertTime,
MaxConvertTime)`; while the budget covers `fillTimeLeft` it places
`newItem(outputType, fuelType)` into `Items[slot]`, removes the FillData,
re-picks the next free index and refreshes the `isFull` / `outOfFuel` /
`isDisabled` flags; otherwise the remainder is subtracted from
`fillTimeLeft` (0 budget left). The loop exits when disabled or the budget
runs out.
Supporting reads: `getCurrentConvertCount(outputType)` (IL=52) is the
catalyst-driven per-batch count (`catalystCount * CatalystMultipliers[name]`
when `UsesCatalyst` and the multiplier is positive, else
`HasModCount ? ModdedConvertCountMultiplier : 1`, run through
`GetSandboxModifiedOutput`); `getCurrentConvertSpeed(outputType)` (IL=9) is
`HasModSpeed ? ModdedConvertSpeedMultiplier : 1`; `getCatalystCount()`
(IL=57) counts non-empty catalyst slots whose item name is in
`collector.CatalystTypes`; `getFuelCount(fuelType)` (IL=30) sums
`getFuelSlotFuelCount` (IL=35, the stack count when its item name is in
`fuelType.Items`) across the fuel slots; `getMaxProductionCount(outputType,
fuelType)` (IL=29) reduces the convert count while `fuelCost` is affordable
(no cap when `!UsesFuel`); `fuelCost(outputType, count)` plus
`getAdditionalFuelCost` (IL=3, `outputType.AdditionalFuelCost`) size the
fuel burn. `newItem(outputType, fuelType)` (IL=36) burns the fuel
(`removeFuel`, IL=67, draining fuel slots) and builds
`ItemStack(HasModConvert ? OutputItemModded : OutputItem, count)`;
`dropItems(list)` (IL=22) is
`DropContentInLootContainerServer(-1, "DroppedLootContainer",
ToWorldCenterPos() + 0.9 y, list, true, null)`.
`isDisabled(outputType)` (IL=16) is `isBlocked || outOfFuel || isUnderwater
|| isFull`; `anyEnabled()` (IL=39) is any output not disabled;
`resetTimeValues(outputType)` (IL=9) stamps `lastWorldTimes[name] =
worldTime`; `GetSlotOutputType(slot)` (IL=9) /
`GetSlotFillData(slot)` (IL=28) / `IsCurrentStack(slot)` (IL=26) resolve the
slot-facing output type and the live `FillData` for a slot.

**`BlockCollector` config/leaf methods (all IL-verified):**
`addTileEntity(world, chunk, pos, bv)` (IL=13) news the `TileEntityCollector`,
sets its `localChunkPos` + `SetWorldTime()` and adds it to the chunk;
`removeTileEntity` (IL=7) is `chunk.RemoveTileEntityAt<TileEntityCollector>`.
`OnBlockEntityTransformBeforeActivated` (IL=11) chains the base then
`UpdateVisible(world, pos)`.
`GetSandboxModifiedFuelNeeded(cost)` (IL=28) scales the fuel cost by the
collector type's `XUiM_Recipes` input factor (Apiary /
DewCollector / ChickenCoop); `modifyTime(time, modifier)` (IL=16) is
`time / modifier` (or -1 when the modifier is 0, disabling the output).
The `outputs` / `catalystTypes` / `fuelTypes` string arrays (with their
sprite / atlas twins) and the grid-height / title / mod-transform fields are
plain field accessors the collector UI reads.

#### `TileEntityLight.write` (IL=48)

After base + version u16:

```text
LightIntensity : f32
LightRange : f32
LightColor : Color32 (StreamUtils.WriteColor32)
LightType : u8
LightAngle : f32
LightShadows : u8
LightState : u8
Rate : f32
Delay : f32
```

#### `TileEntityPoweredRangedTrap.write` (IL=74)

After `TileEntityPoweredBlock.write`:

| Mode | Payload |
|---|---|
| **Persistency (0)** | version **u16=18**, `ownerID` (`PlatformUserIdentifier.ToStream`) |
| **ToServer (1)** | owner (always after base); then `bUserAccessing:bool`, `IsLocked:bool`, `ClientData.SendSlots:bool` (+ `WriteItemStack(ItemSlots)` if set, clear flag), `TargetType:i32` |
| **ToClient (2)** | owner; `hasPowerRangedTrap:bool`; if true: `IsLocked`, `WriteItemStack(PowerRangedTrap.Stacks)`; always `TargetType:i32` |

**`TileEntityPoweredRangedTrap` accessor leaves (all IL-verified):** the
server/client split is uniform: `get_TargetType()` (IL=12) reads
`(PowerItem as PowerRangedTrap).TargetType` on the server else
`ClientData.TargetType` (`set_TargetType` IL=14 writes the matching side);
`get_ItemSlots()` (IL=12) reads `PowerRangedTrap.Stacks` / `ClientData.ItemSlots`
(`set_ItemSlots` IL=16 delegates to `PowerRangedTrap.SetSlots` on the server
and flags `SetModified`); `set_IsLocked` (IL=16) likewise mirrors
`PowerRangedTrap.IsLocked` / `ClientData.IsLocked` + `SetModified`.
`get_AmmoItems()` (IL=40) lazily derives the ammo classes from the block at
the TE position (`BlockLauncher.AmmoItemName` or `BlockRanged.AmmoItemName`
via `ParseItemClassesFromString`). The target flags (IL=7 each) are the
`TargetType` bit tests: `Self = 1`, `Allies = 2`, `Strangers = 4`,
`Zombies = 8`. `get_OwnerEntityID()` (IL=9) lazily runs `SetOwnerEntityID()`
(IL=27: `persistentPlayers.GetPlayerData(ownerID)?.EntityId`, -1 on a miss)
when the cached id is -1; `set_OwnerEntityID` (IL=4) is the plain field
write. `TileEntityPoweredBlock.get_PowerUsed()` (IL=8) is
`IsToggled ? base.PowerUsed : 0`, and `set_IsToggled(value)` (IL=24)
forwards to `PowerConsumerToggle.IsToggled` on the server, always stores
`isToggled` and flags `SetModified`.

#### `TileEntityPoweredMeleeTrap.write` (IL=15)

After powered-block base: version u16 (persist) + `ownerID` ToStream only.

#### `TileEntityWorkstation.write` (IL=246)

After base TE write, always writes version **byte 50**, then branches on
`StreamModeWrite`:

| Mode | Payload (summary) |
|---|---|
| **Persistency (0)** | `lastTickTime:u64`; `writeItemStackArray` for fuel/input/tools/output; `writeRecipeStackArray(50)`; `writeCraftCompleteData(50)`; `isBurning:bool`; `currentBurnTimeLeft:f32`; module/material burn array (`byte` count + f32s); `isPlayerPlaced:bool`; toolsNet stacks |
| **ToServer (1)** | fuel/input/tools/output arrays; recipe + craft-complete (50); `isBurning`; burn time; module burns; `isPlayerPlaced` (no `lastTickTime` first; network path) |
| **ToClient (2)** | similar stack/recipe/burn mirror for UI; includes `lastTickTime` late in path |

Exact stack order matches fields: fuel, input, tools, output (persist also writes
toolsNet). Recipe queue and craft-complete use versioned helpers with constant
**50** (matches workstation format generation).

#### `TileEntityPoweredTrigger.write` (IL=138)

After `TileEntityPowered.write`:

1. Persist: version **u16=18**.
2. `TriggerType:u8`.
3. If type == **Motion (3)**: `ownerID` ToStream.
4. Network modes (`streamMode != 0`):
   - Non-switch types: `ClientData.Property1/2:u8`, `ResetTrigger:bool` (then clear).
   - Motion (3): `TargetType:i32`.
   - TripWire (4): wire-related bool from power item path.
   - TimerRelay (2): start/end time bytes from timer relay.

### 4.7 Composite `TEFeature*` wire tails

`TileEntityExtensions.TryGetSelfOrFeature<T>(te, out typed)` (IL=53) is the
typed-access helper: null input -> default + false; `te is T` -> the TE
itself; `te is TileEntityComposite` -> `GetFeature<T>()` on the composite;
`te is ITileEntityFeature` -> `GetFeature<T>()` on the feature's `Parent`
composite; otherwise default + false. `GetSelfOrFeature` (IL=6) is the same
call with the bool discarded - this is how callers reach a storage / door /
sign feature whether they hold the composite or the feature directly.

**Composite capability/command plumbing:** `PrecomputeCapabilities`
(IL=43) ORs `OverridesPhysicalChecks` and the `TriggerRole` across
`modulesCustomOrder` (a feature implementing `IFeaturePhysicalCapabilities`
or `IFeatureTriggerCapability` lifts the flag onto the composite).
`SplitFullCommandName` (IL=28) splits `"module:command"` at the first
colon into the module and command `ReadOnlyMemory` halves (false when no
colon). `UpdateBlockActivationCommands` (IL=124) refreshes the activation
commands once per frame (a `frameCount` gate): every command starts
enabled; a `IFeatureTriggerCapability`-prefixed command is enabled only in
the editor, and any other command delegates to the owning feature's
`AllowBlockActivationCommand`, tracking `lastUpdateHadEnabledCommands`.

`TileEntityComposite` ticks each `ITileEntityFeature` in `modulesInternalOrder`
(§4.5). Feature Write/Read used inside composite TE payloads:

| Feature | Write IL | Disk/net tail |
|---|---:|---|
| `TEFeatureLockable` | 42 | version u16 (persist); `locked:bool`; count:i32 + `allowedUserIds` ToStream each; `passwordHash:string` |
| `TEFeatureStorage` | 108 | version u16; optional loot-list string; `containerSize` u16x2; playerStorage/touched flags; items: i16 count + `ItemStack.Write` each; slot-lock packed bools |
| `TEFeatureSignable` | 25 | version u16; `AuthoredText.ToStream(signText)` |
| `TEFeatureAreaRepair` | 10 | version u16 only (state mostly live `isRepairing`) |
| `TEFeatureDoor` | 23 | disk: version u16 **18** + `isOpen:bool`; net: `isOpen` + `animateOnSync` (cleared after write). `CanOpen(ref canPickToOpen)` (IL=29): open -> true; `canPickToOpen = lockpickFeature?.NeedsLockpicking()`; `lockFeature.IsLocked()` -> false |

Land-claim repair package drives `TEFeatureAreaRepair.RepairAll` (protocol
§6.19). Storage/lock features are the composite replacement for classic
`TileEntitySecureLootContainer` in V3.1.0 where the composite TE type is used.
`TEFeatureStorage.CountItem(class)` (IL=33) sums `count` over matching
`ItemClass` slots; `AddItem(stack)` (IL=29) writes the first empty slot via
`UpdateSlot` + `SetModified` (false when full).

**`TEFeatureLockable` command leaves:** `InitBlockActivationCommands` (IL=37)
registers the `lock`, `unlock`, and `keypad` `BlockActivationCommand`s (all
order 1 with the feature data). `AllowBlockActivationCommand` (IL=93) gates
them: non-owning modules pass through; for its own commands the local actor
must be owner or a party ally (`Allies.IsAlly(parent.Owner, localUser)`):
`lock` shows when unlocked, `unlock` when locked (owner or editor), `keypad`
only for the owner when the actor is allowed, there is no password, or the lock
is off. `get_TriggerRole` (IL=2) is the constant role **1**;
`OnBlockTriggered` (IL=10) unlocks the feature when `triggeredBy.Unlock` is
set.
`CheckPasswordHash(hash, user)` (IL=24): owner or no password -> true; a
matching hash adds the user to `allowedUserIds` (SetModified) and returns
true; `IsLocked` (IL=3) is the `locked` field, `HasPassword` (IL=6) is
`!IsNullOrEmpty(passwordHash)`.

---

## 5. Triggers and powered traps

A `TileEntityPoweredTrigger` wraps a `PowerTrigger` whose `TriggerType` selects the
sensing model:

| TriggerType | Value | Behavior |
|---|---:|---|
| Switch | 0 | manual on/off, no auto reset |
| PressurePlate | 1 | fires while an entity stands on it |
| TimerRelay | 2 | passes power inside a configured time window |
| Motion | 3 | fires on an entity entering the sensor volume |
| TripWire | 4 | fires when the wire is crossed |

A trigger gates power to its subtree on being active. `PowerTrigger` adds a
**delay** (arm time before it activates) and a **duration** (how long it stays
active after firing), both driven by `CachedUpdateCall` off the PowerManager tick:

```mermaid
stateDiagram-v2
  [*] --> Idle
  Idle --> Armed: triggered (motion / plate / wire) -> record lastPowerTime, start delay
  Armed --> Active: Time.time - lastPowerTime >= delayStartTime -> isActive = true, SetupDurationTime
  Active --> Active: still triggered (parentTriggered) holds it on
  Active --> Cooldown: powerTime elapsed and not held
  Cooldown --> Idle: isActive = false, HandleDisconnectChildren, power removed
  Active --> SingleUseDisable: single-use trigger consumed
  SingleUseDisable --> [*]
```

While a trigger is active it lets the source's power reach the downstream trap.
A powered trap is a consumer: `TileEntityPoweredRangedTrap` (`PowerRangedTrap`
node) and `TileEntityPoweredMeleeTrap` fire only while they receive their full
required power. The ranged trap consumes ammo per shot (`DecrementAmmo`,
`CurrentAmmoItem`) and filters victims by a target mask
(`TargetSelf` / `TargetAllies` / `TargetStrangers` / `TargetZombies`); the melee
trap sweeps its blades against entities in range. Both stop when power is cut or
(ranged) ammo runs out.

```mermaid
stateDiagram-v2
  [*] --> Unpowered
  Unpowered --> Armed: HandlePowerReceived gives full RequiredPower (isPowered = true)
  Armed --> Firing: target in range and matches target mask
  Firing --> Cooldown: shot fired (ranged: DecrementAmmo) / blade swing done
  Cooldown --> Armed: attack interval elapsed, still powered
  Firing --> OutOfAmmo: ranged trap ammo empty
  OutOfAmmo --> Armed: reloaded
  Armed --> Unpowered: power cut (trigger inactive or source off)
  Firing --> Unpowered: power cut
```

`TileEntityPowered.read` stores the trap's own wire list (`wireDataList`), parent
position, `PowerItemType`, and `isPlayerPlaced`, and in network mode the live
`isPowered` bit, so a client renders the correct wires and on/off glow without
recomputing the graph. On the server, `InitializePowerData` looks up (or creates)
the matching `PowerItem` by world position and links the two.

---

## 6. Other tile entities

- **`TileEntityVendingMachine`**: an owned trader box. `UpdateTick` checks a
  rentable machine against the world day and calls `ClearVendingMachine` when
  `rentalEndDay` passes, so an expired rental empties itself. Owner, rent window
  (`RentTimeRemaining`, `RentalEndDay`), and stock are serialized with the chunk.
- **`TileEntitySleeper`**: marks a sleeper (spawn) volume anchor. It stores sensing
  parameters only: `PriorityMultiplier`, `SightAngle`, `SightRange`,
  `HearingPercent`. The volume logic and spawns are owned by the AI director and
  world sleeper streams (see [`save-region.md`](save-region.md) sleeper volumes and
  [`entity-ai.md`](entity-ai.md)); this tile entity is just the per-block record.
- **`TileEntityLight`**: a `TileEntityPoweredBlock` that toggles a light with its
  power state.
- **`TileEntityComposite`**: the modern data-driven tile entity. It builds feature
  modules from a `TileEntityCompositeData` block template, precomputes trigger and
  physical-override capabilities, and routes activation commands to the module that
  owns them. Loot, secure loot, doors, and signs are expressed this way.

---

## 7. Dedicated relevance and residuals

- **Authority and save:** tile-entity `UpdateTick`, power distribution, and both
  save paths (chunk blob for tile entities, `power.dat` for the graph) run on the
  dedicated server. Clients receive `NetPackageTileEntity` updates and the
  serialized power state; they do not own the graph.
- **Two independent stores:** losing a chunk file loses that chunk's machines;
  losing `power.dat` loses the wiring topology while the machines survive in their
  chunks. The two are reconciled on load by `InitializePowerData` matching
  positions.
- **Content (residual):** `RequiredPower`, fuel values, recipe times, trap ammo,
  trigger delay/duration options, and composite feature templates come from block
  and recipe XML, not from these method bodies.
- **Client-only (residual):** the `XUiC_PowerSource*`, `XUiC_Workstation*`, and
  wire-drawing paths (`DrawWires`) are UI and rendering; on a headless server they
  are skipped behind `ConnectionManager.IsServer` checks.

---

## Wire tool packages

`NetPackageWireActions` / `NetPackageWireToolActions` edit the power wire graph
(protocol-packages 6.21; Process IL=163 on WireActions).

## Related docs

| Doc | Role |
|---|---|
| [save-region.md](save-region.md) | Chunk blob (where tile entities are written) and the power save directory |
| [world-chunks.md](world-chunks.md) | The tick pipeline that calls `Chunk.UpdateTick` |
| [entity-ai.md](entity-ai.md) | Sleeper volumes and AI heat-map events emitted by workstations |
| [protocol.md](protocol.md) | Net package framing (`NetPackageTileEntity` replication) |
| [managers.md](managers.md) | Other in-process managers alongside `PowerManager` |
| [full-surface.md](full-surface.md) | Where this family sits in the whole-assembly map |
| [re-methodology.md](re-methodology.md) | How this was reversed |

**Catalogued-leaf index (narrated for the coverage census):**

| Leaf | base | key methods |
|---|---|---|
| `ElectricWireController` | MonoBehaviour | touched, Init, DamageSelf, Update |
| `TEFeatureCombine` | TEFeatureAbs | ShowUI, OnBlockActivated, Init, GetActivationText |
| `TEFeatureExplodable` | TEFeatureAbs | Explode, Init, OnBlockDestroyedBy, OnAdded |
| `TEFeaturePickup` | TEFeatureAbs | AllowBlockActivationCommand, OnBlockActivated, Read, InitBlockActivationCommands |
| `WireFrameSphere` | MonoBehaviour | RenderCircleOnPlane, Update, Start, KillWF |

## Changelog

- **2026-08-10:** PowerManager IL sizes re-verified: AddPowerNode IL=31, RemovePowerNode IL=61, SavePowerManager IL=41, LoadPowerManager IL=70 (exact).
- **2026-08-10:** Chunk.GetBlockEntity IL sizes re-verified: Vector3i overload IL=10, Transform overload IL=30; Chunk.UpdateTick IL=26, TileEntityCollector.HandleUpdate IL=120 (exact).
- **2026-08-08:** Catalogued-leaf index added (narrates the family's remaining
  catalogued leaves for the coverage census).

- **2026-08-08:** TripWireController trigger MonoBehaviour (collider -> IsTriggered on server).
- **2026-08-08:** TileEntityWorkstation.CheckForCraftComplete (IL=55):
  per-owner CraftCompleteList delivery, cosmetic unlock, GiveExp, TE
  modified flag.

- **2026-08-08:** TileEntity.emitHeatMapEvent (IL=48): heapMapLastTime
  rewind reset, GetActivityWorldTimeDelay cadence, NotifyActivity(...,
  block.HeatMapStrength, 720) 36 s heat; IsActive base true, Forge meta > 0,
  Workstation IsBurning.

- **2026-08-08:** TileEntityComposite envelope (2.2): write IL=74 / read
  IL=479 - version u16 18, outer + per-feature i32 size markers, blockId
  via blockIdMapping remap + BlockCompositeTileEntity check, owner (null in
  edit mode), featureCount u8, per-feature NameHash; legacy (<17) count/hash
  match vs modern GetFeatureIndex dispatch, skip-on-unknown, caught module
  read failures, ValidateSizeMarker checks.
- **2026-08-08:** Chunk.AddEntityBlockStub (IL=21): UInt64-keyed
  blockEntityStubs Set with old-stub queueing into blockEntityStubsToRemove
  on cell collision (deferred model-swap cleanup).
- **2026-08-07:** GameUtils.Vector3iToUInt64 (IL=29): 16-bit offset-packed
  x<<32|y<<16|z position key.
- **2026-08-07:** Chunk.GetBlockEntity: Vector3i (IL=10) UInt64-keyed dict,
  Transform (IL=30) linear scan, PrefabChunk null, ChunkCluster (IL=12)
  resolve + delegate.
- **2026-08-07:** Chunk.UpdateTick IL=26 TeTick list walk; TEFeature write tails
  (§4.7); Workstation/PoweredTrigger/Collector/Light/trap write tails.
- **2026-08-07:** NetPackageTileEntity Process IL=103 teBlockId drop + stream
  mode 2 remote / 1 local + server rebroadcast.
- **2026-08-07:** HandleFuel early-out when not burning (no heat emit); burn
  quantize 0.01 s; fuel[0] consume + cycleFuelStacks.
- **2026-08-07:** Workstation UpdateTick/HandleFuel/HandleRecipeQueue IL paths;
  Forge fuel-tick melt path; Vending rental expiry; Composite feature tick;
  Powered TE dirty flags.
- **2026-08-07:** PowerItem subtype tick table (gen/solar/battery/trigger/toggle),
  corrected PowerChildren/isToggled gate claim, subtype power.dat tails,
  NetPackageWireActions SetParent/RemoveParent/SendWires process.
- **2026-08-07:** `ClientPowerData` field table + `TileEntityPowerSource` write/read by
  StreamMode (Persistency / ToServer / ToClient) from IL=98/158.
- **2026-07-28:** power.dat field-level Write/Read tree codec + threaded save.

- **2026-07-28:** NetPackageTileEntity wire + server rebroadcast path.

- **2026-07-23:** Initial tile-entity and power-system reversal (TileEntity model + type factory, chunk-owned serialization, PowerManager tick and greedy source-to-consumer distribution, workstation/forge crafting lifecycle, trigger and powered-trap state machines).
