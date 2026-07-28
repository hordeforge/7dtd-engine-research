# Dedicated leftovers (V3.0.1)

**Owns:** the final batch of reached-but-undocumented server types: the
transactional-inventory orchestrator (`InventoryManager` + `LockEntry`), the
item-framework leaves that run server-side (`ItemClassBlock`, `ItemClassQuest`,
`ItemClassWaterContainer`), the `PrefabVolumes.*` list types, the
`PathAbstractions` search-path family, `BlockValueV3`, `AesEncryptAndMac`,
`EnumBodyPartHitExtensions`, `BaseOperationLootEntryRequirement`,
`PlayerInteractions`, `CraftCompleteData`, `EntityAsyncManager/EntityCreateHandle`, `NetEntityPackageQueue`,
entity/trader/vending `*LockContext` wire bags, `Prefab/PrefabChunk`,
`ShapesFromXml/ShapeCategory`, `DynamicPropertiesCache`, the `PhysicsBody*`
collider layout family, and the infra types `SdFileSystemInfo`,
`TrackedDataMap/SubsetAccessor`, `UpdateListenerMap`, `DynamicObserver`,
`PooledExpandableMemoryStream`. Also settles `DiscordManager/AuthAndLoginManager`.
**Not:** the owning systems (each section cross-links its family doc); anything
whose entire caller set is UI, editor, avatar, or client render code (listed at
the end); dead config (`EntityVBlimp`).
**Evidence:** IL of the types above plus their caller sets (`FindCallers` walked
back to server systems, world lifecycle, or net packages for every documented
type; dump locally with `tools/src/DumpMethod`, git-ignored), and the stock
`Data/Config` XML shipped with the dedicated server where reachability depends
on config. **Hub:** [`INDEX.md`](INDEX.md).
**Method:** [`re-methodology.md`](re-methodology.md).

Every type below was confirmed dedicated-relevant by walking its callers back
to server-side code, not just by existing in the assembly. Several types the
tasking expected to be client-only turned out to be dedicated (`PhysicsBody*`,
`SdFileSystemInfo`, `SubsetAccessor`, `UpdateListenerMap`, `DynamicObserver`,
`PooledExpandableMemoryStream`), and several expected-dedicated types turned out
to be client or dead and are reclassified at the end.

---

## 1. AuthAndLoginManager: the login manager that is not server login

The tasking flagged `AuthAndLoginManager` (34 methods) as "server-side login
orchestration sequencing the authorizer chain". The IL says otherwise: it is a
**nested type of `DiscordManager`** and orchestrates the local user's Discord
Social SDK sign-in, not player joins. Its surface is `LoginDiscordUser` (PC and
console variants), `LoginProvisionalAccount`, `LoginWithPlatformDefaultAccountType`,
`loginWithStoredTokens` / `refreshToken` (token exchange callbacks),
`UnmergeAccount`, `AbortAuth` and `Disconnect`, tracked through
`DiscordManager.Status` (`EDiscordStatus`: `NotInitialized`, `Disconnected`,
`Ready`, `Connecting`, `Disconnecting`) and `IsLoggingInWith`
(`EDiscordAccountType`: `None` / `Regular` / `Provisional`).

On a dedicated server none of it runs. Every login entry point is client UI
(`XUiC_DiscordWindow`, `XUiC_OptionsAudio`, `XUiC_DiscordLogin`) or one of two
`DiscordManager` hooks that both gate out headless:

```text
DiscordManager::.ctor      IL_00DD: call GameManager::get_IsDedicatedServer()
                           IL_00E2: brtrue.s IL_00FE   // skip Init(false)
DiscordManager::gameStarting IL_0034: call GameManager::get_IsDedicatedServer()
                           IL_0039: brtrue.s IL_0049   // skip Init + AutoLogin
```

So the `Discord.Sdk.Client` is never constructed server-side and `AutoLogin` is
never invoked. What a dedicated server *does* run in this area is already
documented: `ClientInfo.DiscordUserId` is recorded during login and relayed by
`NetPackageDiscordIdMappings.ProcessPackage` (which validates the sender via
`ValidEntityIdForSender` and, `IsServer`, stamps the sender's `ClientInfo`), and
`FriendsAuthorizer.Authorize` consults `DiscordManager.GetUser(DiscordUserId)`
for friend checks in the authorizer chain. See
[platform-auth.md](platform-auth.md) §authorizers and
[protocol.md](protocol.md) §5 for where that sits in the join sequence;
join/kick orchestration itself is `AuthorizationManager`, already covered.
`AuthAndLoginManager` is therefore listed as client-only below.

---

## 2. InventoryManager and LockEntry

`InventoryManager` is the server-side registry for the `TransactionalInventory`
anti-dupe system ([items.md](items.md) §container moves): a lazy singleton
mapping `Guid` tokens to inventories (`TryGetTransactionalInventory`,
`ValidateToken`), creating them server-side (`CreateInventoryServer`), and
serializing them (`ReadInventory` / `WriteInventory` with `StreamMode`
versioning). Its wire endpoints run in server package handlers:
`NetPackageInventoryTransactionRequest.ProcessPackage` calls
`TransactionRequestServer(transaction, senderEntityId)` and
`NetPackageInventoryDataRequest/Response` resolve tokens for full-state sync;
`TransactionRequestLocal` short-circuits to the server path in single player.
`LockEntry` is the small value key of the related `LockManager` (ticked from
`GameManager.gmUpdate`, [loop-gmupdate.md](loop-gmupdate.md) §10): an
`ILockTarget` plus a `ushort` lock type with equality operators, used to hold
per-target access locks (vending machines, workstations, power blocks; trading
uses a shared lock, [loot-economy.md](loot-economy.md)). `ConnectionManager`
releases a client's locks on disconnect.

### 2.1 `ILockContext` bags (entity / trader / vending)

`LockManager` does not serialize locks as opaque tokens only: successful lock
acquisition carries a typed **`ILockContext`** payload that rides the lock
request/response path and is applied in `OnLockedServer` / `OnLockedLocal`.

| Nested type | Owner | Fields | Wire (`Write`/`Read`) |
|---|---|---|---|
| `Entity/EntityLockContext` | `Entity` | `Command` (string), `Bag`, `FirstTimeTouched` | string command; bool firstTouch; bool hasBag + optional `Bag.Write`/`Bag.Read` |
| `EntityTrader/EntityTraderLockContext` | `EntityTrader` | `Command`, `TraderData` (cloned on construct) | string command; bool hasTraderData + optional `TraderData.Write`/`Read` |
| `TileEntityVendingMachine/VendingMachineLockContext` | vending TE | `TraderData` only | always `TraderData.Write`/`Read` (construct clones) |

**Server apply (`OnLockedServer`, verified call patterns):**

- Generic entity: set `FirstTimeTouched`, attach `Bag`, `LootManager.LootBagOpened`.
- `EntityTrader`: `SetupActiveQuestsForPlayer`, `NetPackageNPCQuestList.SendQuestPacketsToPlayer`, `TraderManager.TraderInventoryRequested`, clone `TraderData` into the context.
- `TileEntityVendingMachine`: same trader-inventory request + clone into context.

**Local apply (`OnLockedLocal`)** opens client UI (`XUiC_BagStorageWindowGroup`,
trader window transitions, drone/vehicle `StartInteraction`) and always ends in
`LockManager.UnlockRequestLocal` when the interaction closes. Dedicated care is
the server half + the wire shape of the context; the UI open is client-only.

Complements [items.md](items.md) (bag), [loot-economy.md](loot-economy.md)
(trader lock), [npc-dialog.md](npc-dialog.md) (quest list on trader open).

## 3. ItemClass leaves: ItemClassBlock, ItemClassQuest, ItemClassWaterContainer

`ItemClassBlock` is the block-as-item bridge: `ItemClassesFromXml.CreateItemsFromBlocks`
constructs one per `Block` during config load (dedicated included), so every
block occupies an item id and can sit in inventories, loot, and creative lists.
`GetBlockValueFromItemValue` converts back for placement; the mesh/hold members
only matter client-side, but the id mapping and `ItemBlockInventoryData` are
load-bearing everywhere. `ItemClassQuest` is created per quest item by
`QuestsFromXml.ParseQuestItems` and registered in a static id table;
`ItemValue.ItemClass` redirects quest-item ids through `GetItemQuestById`, so
any server code resolving such an `ItemValue` hits it; its overrides pin the
policy bits (`CanStack` false, `KeepOnDeath`, container rules).
`ItemClassWaterContainer` adds a `MaxMass` property and overrides
`GetInitialMetadata`, which the server calls whenever such items are minted
(`ItemClass.CreateItemStacks` in loot, `TraderInfo.applyRandomDegradation`), so
freshly spawned water containers carry correct fill metadata. Complements
[items.md](items.md); `ItemClassTorch` did not make the cut (see out of scope).

## 4. PrefabVolumes list types (Wall / Trigger / Teleport / Info / Sleeper)

All five are `PrefabVolumeListAbs<TList, TVolume>` subclasses constructed in
`Prefab..ctor` for **every** loaded prefab, filled by `ReadFromProperties` from
the prefab's XML properties, and stamped into live chunks server-side via
`CopyVolumesIntoWorld` when the decorator places the POI. Confirmed server
consumers: `PrefabSleeperVolumeList` backs `Prefab.FindSleeperVolume`,
`CalcSleeperInfo` and `SleeperEventData.SetupData` (sleeper spawning,
[spawning.md](spawning.md)); `PrefabTriggerVolumeList` and
`PrefabSleeperVolumeList` are re-stamped by `World.ResetPOIS` on quest resets;
`PrefabTeleportVolumeList` is read/written by `TraderArea` (trader closing-time
teleport-out); `PrefabInfoVolumeList` backs `PrefabInstance.IsWithinInfoArea`;
`PrefabWallVolumeList` is load/copy only in the dedicated path. The
`AddNewVolume`/`SelectionBox` members are the editor half. Complements
[server-browser-prefabs.md](server-browser-prefabs.md) (prefab load pipeline).

## 5. PathAbstractions: SearchDefinition, SearchPathBasic/Saves/Mods/UserData

The static `PathAbstractions` class builds one `SearchDefinition` per asset
family in its `.cctor` (`WorldsSearchPaths`, `PrefabsSearchPaths`,
`PrefabImpostersSearchPaths`, stamps, and more), each an ordered array of
`SearchPath` strategies: `SearchPathSaves` (the save folder, e.g. `World`),
`SearchPathUserData` (platform user storage, e.g. `GeneratedWorlds`),
`SearchPathMods` (each loaded mod's subfolder, e.g. `Worlds`), and
`SearchPathBasic` (a fixed base like `Data/Worlds`). `SearchDefinition` resolves
names to `AbstractedLocation`s (`GetLocation`, `GetAvailablePathsList`,
`BuildLocation`) with a populate-on-demand cache (`PopulateCache` /
`InvalidateCache`) and mod-aware `EAbstractedLocationType`. Dedicated callers
are core: `GameManager`/`GameUtils` world resolution, `ChunkProviderDisc`,
`DynamicPrefabDecorator`, `BiomeIntensityMap`, and the prefab console commands.
Complements [save-persistence.md](save-persistence.md) and
[world-generation.md](world-generation.md), which already use these statics.

## 6. BlockValueV3

A `uint`-wrapping struct that preserves the **old** raw block-value bit layout
(type mask via `GetTypeMasked`, `rotation`, `meta`/`meta2`/`meta3`, decal bits,
child/parent link bits, water flags). Its one live consumer is
`Prefab.readBlockData`: for `.tts` prefab files with `_version < 18` each raw
word passes through `BlockValueV3.ConvertOldRawData(uint)` to be re-packed into
the current `BlockValue` layout. Since prefab block data is parsed server-side
when POIs are placed, this legacy shim is dedicated code on any world using
older prefabs. Complements [blocks.md](blocks.md) (current `BlockValue` layout)
and [server-browser-prefabs.md](server-browser-prefabs.md) (.tts reader).

## 7. AesEncryptAndMac

The managed symmetric channel cipher behind the join key exchange: `Aes.Create()`
plus `HMACSHA256`, exposing `EncryptionKey`/`IntegrityKey` and
`EncryptStream`/`DecryptStream` over `PooledExpandableMemoryStream` buffers
under a lock. `AntiCheatEncryptionAuthServer.SendSharedKey` news one per
joining client, RSA-encrypts (`RSAEncryptionPadding.Pkcs1`) the two keys with
the client's platform public key, ships them in
`NetPackageEncryptionSharedKey`, and parks the instance in
`pendingEncryptionModules` as the client's `IEncryptionModule`. The interface is
then invoked per message by `NetConnectionAbs.Encrypt/Decrypt`, which is why
direct callers of `EncryptStream` do not appear: it is pure interface dispatch.
Complements [protocol-packages.md](protocol-packages.md) §2 and
[platform-auth.md](platform-auth.md) §4.4 (handshake sequencing).

## 8. EnumBodyPartHitExtensions

Static helpers over the `EnumBodyPartHit` flags enum: `IsLeg`/`IsLeftLeg`/
`IsRightLeg`/`IsArm`, `IsMultiHit`, and the conversions `ToPrimary` /
`ToFlag` / `LowerToUpperLimb` between the flag form and `BodyPrimaryHit`.
Dedicated-relevant because the authoritative damage path uses them:
`EntityAlive.damageEntityLocal` and `ProcessDamageResponseLocal` branch on
`IsLeg` (leg-cripple logic) and `GetDismemberChance` keys its table on
`ToPrimary`. The same helpers also serve client avatar controllers, but the
server-side damage math is the reason they are in scope. Complements
[combat-damage.md](combat-damage.md).

## 9. BaseOperationLootEntryRequirement

Abstract comparison node for loot-entry gating: `Init(XElement)` parses an
operation, `LeftSide(EntityPlayer)`/`RightSide(EntityPlayer)` produce operands,
and `CheckRequirement(EntityPlayer)` applies the operator. Its concrete users
are the `LootEntryRequirement*` classes (`CVar`, `Progression`, `RandomRoll`,
`SandboxOption`) which the server evaluates against the opening player when
rolling loot group entries. Runs wherever loot lists are materialized, i.e. the
dedicated loot spawn path. Complements [loot-economy.md](loot-economy.md).

## 10. PlayerInteractions

Singleton that turns persistent-player events into `Platform.PlayerInteraction`
records for platform compliance ("played with" lists). On a dedicated server
`GameManager.StartAsServer` calls `JoinedMultiplayerServer(persistentPlayers)`
(it logs `[PlayerInteractions] JoinedMultplayerServer`, sic) and
`GameManager.PlayerSpawnedInWorld` calls `PlayerSpawnedInMultiplayerServer`;
`SaveAndCleanupWorld` unhooks and calls `Shutdown`. Each event fans out to
`PlatformManager.MultiPlatform.PlayerInteractionsRecorder` (null-guarded; a
no-op recorder on a Linux Steam dedicated) and raises `OnNewPlayerInteraction`,
which `Platform.BlockedPlayerList` subscribes to for blocked-player
resolution. Complements [platform-auth.md](platform-auth.md) (platform
abstraction) and [server-lifecycle.md](server-lifecycle.md) (StartAsServer /
SaveAndCleanupWorld hooks).

## 11. CraftCompleteData

Persistence record for a finished workstation craft: written and read only by
`TileEntityWorkstation` (`writeCraftCompleteData` / `readCraftCompleteData`,
with a `ReadLegacy` shim for old saves) and appended by
`TileEntityWorkstation.AddCraftComplete` / consumed by `CheckForCraftComplete`.
Because workstation tile entities live and persist server-side (crafting
continues while the owner is away), these records ride the tile-entity
read/write path on the dedicated. Complements
[tile-entities-power.md](tile-entities-power.md) and
[crafting-recipes.md](crafting-recipes.md).

## 12. EntityAsyncManager/`EntityCreateHandle` + `NetEntityPackageQueue`

The completion handle of the async entity-create pipeline: wraps a
`CreateEntityOperation` plus a callback, with `TryComplete` polled by
`EntityAsyncManager.Update` (phase F of the server loop,
[loop-gmupdate.md](loop-gmupdate.md) §2 / [managers.md](managers.md)) and a
blocking `WaitForComplete` for teardown. Server producers: `Chunk.SpawnEntityAsync`
tracks a `HashSet` of pending handles per chunk and `Chunk.OnUnload` drains
them via `WaitForComplete` so unload never races creation; `SleeperVolume`
spawns sleepers through it; `NetPackageEntitySpawn.ProcessPackage` uses it for
package-driven spawns.

**Create path (verified):** `StartCreateEntity(EntityCreationData, onComplete)`
builds `EntityFactory.CreateEntityAsync`, allocates `EntityCreateHandle`, stores
it in a pending `Dictionary<Int32, EntityCreateHandle>` by entity id, and enqueues
the handle for `Update` polling.

**Package hold-back:** entity-targeted packages can arrive before the entity
exists. `NetPackageEntityTargeted.ShouldProcess` asks
`NetEntityPackageQueue.HasPackagesForEntity`; if the entity is still pending,
`HandleSkipped` calls `EnqueueNetPackageForEntity`. When create finishes,
`EntityAsyncManager.OnCreateEntityRequestFinalized(id)` removes the handle and
calls `NetEntityPackageQueue.ProcessPackagesForEntity(id)`, which dequeues each
held `NetPackage`, runs `ProcessPackage(world, GameManager)`, and
`NetPackageManager.FreePackage`.

`NetEntityPackageQueue` itself:

| Method | IL | Behavior |
|---|---:|---|
| ctor | 10 | `Dictionary<int, Queue<NetPackage>>(64)` |
| `EnqueueNetPackageForEntity` | 18 | create per-entity queue capacity **10** if missing |
| `ProcessPackagesForEntity` | 20 | remove queue, drain + process + free |
| `Cleanup` | 28 | free all queued packages (world cleanup / load) |

```mermaid
flowchart LR
  Spawn[StartCreateEntity] --> H[EntityCreateHandle]
  H --> Pend[pending dict by id]
  Early[NetPackageEntityTargeted early] --> Q[NetEntityPackageQueue]
  Pend --> Done[OnCreateEntityRequestFinalized]
  Done --> Drain[ProcessPackagesForEntity]
  Q --> Drain
  Drain --> Proc[NetPackage.ProcessPackage]
```

Complements [spawning.md](spawning.md) and [network.md](network.md).

## 13. ShapesFromXml/ShapeCategory

Small record (name, localized label, order) parsed from `shapes.xml` by
`ShapesFromXml` into a static category dictionary during config load, which the
dedicated performs like any XML. `Block.Init` resolves each block's
`ShapeCategories` list from it, so the data is populated and attached
server-side; the only runtime consumers beyond that are the client shape-menu
windows (`XUiC_ShapesWindow`, `XUiC_Creative2Window`). In scope as loaded
config metadata, with that caveat. Complements [block-shapes.md](block-shapes.md).

## 14. DynamicPropertiesCache

Memory optimization behind `Block.Properties`: `Block.InitStatic` creates the
cache, `Block.LateInit` calls `Store(id, props)` to intern each block's
`DynamicProperties`, `Block.get_Properties` retrieves through `Cache(id)` /
`Retrieve`, and `Block.OnWorldUnloaded` calls `Cleanup`. Entirely inside the
server-side block registry lifecycle (`Stats` exists for diagnostics).
Complements [blocks.md](blocks.md).

## 15. PhysicsBodyLayout, PhysicsBodyInstance, PhysicsBodyColliderBase

Flagged "likely client ragdoll", but the callers say dedicated:
`physicsbodies.xml` is loaded via `WorldStaticData` (with `PhysicsBodyLayout.Reset`
on reload), `EntityClass.Init` resolves each entity's `PhysicsBody` layout by
name, and `EModelBase.SwitchModelAndView` (called from `EModelBase.InitCommon`
for every entity, server included) news a `PhysicsBodyInstance(transform,
layout, EnumColliderMode)` and drives `SetColliderMode`. These colliders are
the entity hitboxes the server's raycasts and damage code hit, not just ragdoll
dressing. `PhysicsBodyColliderBase` and its `Box/Capsule/Sphere/Null` subclasses
are the parsed collider definitions inside a layout. Complements
[combat-damage.md](combat-damage.md) (hit resolution) and
[entity-ai.md](entity-ai.md).

## 16. SdFileSystemInfo

The wrapper behind the `SdFile`/`SdDirectory`/`SdFileInfo` facade of
[save-persistence.md](save-persistence.md): holds a `FileSystemInfo` plus the
`IsManaged` flag and `SaveDataManagedPath` that route an entry through the
managed `ISaveDataManager` providers instead of raw `System.IO`. Dedicated
callers include `SaveDataManager`/`SaveDataManagerBase`, `GameIO`,
`PathAbstractions/SearchPath` cache population, `SaveInfoProvider`,
`MapChunkDatabaseByRegion`, `RegionFileAccessMultipleChunks`, and
`DynamicMeshManager` file scans; `Refresh`/`Reinitialize` support pooled reuse
during directory listing.

## 17. TrackedDataMap/SubsetAccessor

The "typed subset accessors" of `MultiBlockManager.TrackedDataMap`
([dedicated-misc-systems.md](dedicated-misc-systems.md) §TrackedDataMap) as a
concrete type: a struct enumerator/view over the shared
`Dictionary<Vector3i, TrackedBlockData>` restricted to one `HashSet<Vector3i>`
subset (oversized, cross-chunk, POI, terrain-aligned), exposing `ContainsKey`,
`TryGetValue`, indexer and enumeration without copying. Lives entirely inside
the server's multi-block tracking (`MultiBlockManager.MainThreadUpdate` in the
main loop, [loop.md](loop.md)). Complements [blocks.md](blocks.md).

## 18. UpdateListenerMap

Bidirectional registry inside `SignDataManager` mapping `GlobalSignId` to
`ISignRenderingDataUpdateListener`s (`RegisterListener`, `GetListeners`,
`GetIds`, `HasListeners`, `Clear`). The manager that owns and consults it on
sign-data updates is the dedicated-side sign library
([signs.md](signs.md)); the listeners themselves are client renderers, so on a
dedicated server the map is constructed and checked but stays empty
(`HasListeners` false). In scope as server-owned plumbing with that caveat.

## 19. DynamicObserver

Server-side helper of `DynamicMeshManager` ([dynamic-mesh.md](dynamic-mesh.md)
§CheckFallingObservers): `Start(position)` opens an observation volume after an
imposter-area update, `ContainsPoint(Vector3i)` filters block events, and
`HasFallingBlocks` reports whether unsupported blocks began falling inside it,
letting the manager defer work until physics settles; `Stop` releases it. Part
of the dedicated dynamic-mesh regeneration path (the manager is server-owned).

## 20. PooledExpandableMemoryStream

The pooled `MemoryStream` subclass handed out by
`MemoryPools.poolMemoryStream.AllocSync` all over the server hot path:
serializers for net packages (`NetPackageBag`, `NetPackageDecoUpdate`,
`NetPackageEntityStatsBuff`, drone data sync and more), `AesEncryptAndMac`
crypto buffers, `ChunkAreaBiomeSpawnData`, `NameIdMapping`, `FactionManager`,
`BlockLimitTracker`, `EventPrefabs`. `Reset`/`Cleanup` rewind and return the
buffer to the pool instead of freeing, and `Close`/`Dispose` are overridden to
route into the pool. Complements [protocol-packages.md](protocol-packages.md)
(package serialization) and [network.md](network.md).

---

## 21. Prefab/PrefabChunk

`PrefabChunk` is a nested **`IChunk`-shaped view** over a loaded `Prefab`
template (not a world chunk). `Prefab.GetChunk(x,z)` caches
`Dictionary<Int64, PrefabChunk>` keyed by `WorldChunkCache.MakeChunkKey`;
`GetChunks` materializes the full list for placement/copy paths.

Surface (54 methods): `GetBlock` / `GetWater` / `GetDensity` / `IsAir` /
`IsWater` / `GetTerrainHeight` / `GetBlockFaceTexture` / `GetTextureFull` /
`GetBlockColumn`, with `checkCoordinates` clamping local indices. Used when the
server copies prefab volumes into the world (`CopyIntoLocal` and friends in the
prefab/chunk provider path; see [chunk-providers.md](chunk-providers.md) and
[server-browser-prefabs.md](server-browser-prefabs.md)).

Complements [world-chunks.md](world-chunks.md) (real chunks) by making clear
this type is **template addressing**, not region persistence.

---

## Out of scope (verified client-only)

- **DiscordManager/AuthAndLoginManager**: Discord Social SDK sign-in for the
  local user; both dedicated-side triggers gate out on `IsDedicatedServer` and
  the SDK client is never initialized headless. Full verification in §1.
- **ItemClassTorch**: instantiated at `items.xml` parse (`meleeToolTorch`), but
  every override is held-item behavior on the holding client
  (`StartHolding`/`OnHoldingUpdate`/`StopHolding`, and `OnConvertToBlockValue`
  packing `ItemValue.UseTimes` into block `meta`/`meta2` inside the client-run
  `ItemActionPlaceAsBlock.ExecuteAction`); the server only sees the resulting
  block change ([items.md](items.md)).
- **EntityVBlimp**: dead in stock config. The `EntityVehicle` subclass exists
  (buoyant `PhysicsInputMove`, wheel force/steering stubs), and `vehicles.xml`
  still ships a `vehicleJokeblimp` tuning entry, but the matching
  `entity_class` in `entityclasses.xml` is commented out ("Kinda sorta works
  but is buggy"), so `EntityFactory` can never instantiate it. Modders can
  re-enable it; stock dedicated never reaches it
  ([vehicles-drones-turrets.md](vehicles-drones-turrets.md)).
- **`BlockSwitchController` / `BlockSwitchSingleController`**: MonoBehaviours on
  block-entity prefabs syncing lever/light visuals (`Start`, `UpdateLights`).
  The one server-side toucher, `TriggerManager.CheckPowerState`, fetches them
  via `Chunk.GetBlockEntity(...).transform.GetComponent<...>()`, which is
  null-guarded and null on a dedicated (no block-entity GameObjects). The
  authoritative trigger state lives in `TriggerManager` itself
  ([block-shapes.md](block-shapes.md) §triggers).
- **TimerEventData**: the hold-to-interact timer payload; every creation site
  (`Block.TakeItemWithTimer`, `BlockGameEvent`/`BlockQuestActivate.OnBlockActivated`,
  `Entity.ActivateEntityCommand`, `TEFeatureLockPickable`) immediately opens
  `XUiC_Timer.OpenTimer` on the interacting player's client; the server only
  sees the follow-up packages.
- **ChatTarget**: nested in `XUiC_Chat`; client chat-target dropdown records
  (`Send`, `IsValid`). Server chat routing is in [chat.md](chat.md).
- **GameOptionValue**: nested in `XUiC_GamePrefSelector` and the
  `XUiC_ServerBrowserGamePref*` controls; client option-UI value records
  ([sandbox-options.md](sandbox-options.md) covers the server side).
- **SandboxOptionValue / SandboxPresetInfo / SandboxPresetGroupData**: UI
  records nested in or consumed only by `XUiC_SandBoxOptionEntry` and
  `XUiC_SandboxPresetSelector`. The server-side option/preset model
  (`SandboxOptions.*`, `SandboxOptionValueSet`, `SandboxOptionPreset`,
  `LoadPresets` on dedicated) is already documented in
  [sandbox-options.md](sandbox-options.md).
- **POIBoundsSideHelper**: trigger-collider walls spawned by `POIBoundsHelper`
  for `ObjectivePOIStayWithin`, a quest objective that runs on the owning
  player's client ([quests-challenges.md](quests-challenges.md) §5).
- **PoiSizeInfo**: `XUiC_CreatePoi` editor UI record.
- **PrefabMarkerEntry**: `XUiC_PrefabMarkerList` editor UI record.
- **ChunkPreviewData / ChunkPreviewManager**: prefab-preview visualization
  (`SetChunkGoVisiblity`, preview GameObjects) fed by
  `DynamicMeshPrefabPreviewThread`; editor/console preview tooling beside the
  dynamic-mesh code, not the server regeneration path of
  [dynamic-mesh.md](dynamic-mesh.md).
- **FlatArea / FlatAreaManager**: flat-area records over the deco occupied map.
  The only runtime consumer is `ObjectiveRandomGoto.CalculateRandomPositionFromFlatAreas`
  (client quest objective); no caller of `DefineFlatAreas` exists in the
  dedicated assembly and the server touches it only via `World.Cleanup` and a
  `DecoManager` debug texture dump.
- **AutomationRunner / AutomationScript**: QA scripting harness
  (`ExecutePerfSession`, `GetPlayer`, script steps). Dedicated touchpoints are
  `GameEntrypoint.FirstFrameInit -> AutomationRunner.InitialiseLogging` and
  `ConsoleCmdAutomation`; dev-only tooling, no gameplay role.
- **NGuiAction / MessageButton**: legacy NGUI action wrappers and
  `XUiC_MessageBoxWindowGroup` button records; UI. **EventDelegate** is not
  even in `Assembly-CSharp` (it lives in `NGUI.dll`).
- **BuffEntityUINotification**: HUD buff notification record. Note it **is**
  constructed server-side, unconditionally, in `PlayerEntityStats.EntityBuffAdded`
  off the server buff tick ([buffs.md](buffs.md)); the allocation is simply inert
  there because only the client HUD reads it. Listed here as no-server-behavior
  rather than never-server-executed.
- **SaveDataLimitUIHelper**: save-allowance display helper for `XUiC_NewGame` /
  `XUiC_WorldGenerationWindow`; the enforcement lives in
  [save-persistence.md](save-persistence.md).

## Dedicated stragglers (brief)

Small dedicated-relevant types that extend an already-owned subsystem:

- **`VariableState*` family** (`VariableStateAbs` base + `VariableStateCVar`,
  `VariableStateGameStat`, `VariableStateGamePref`, `VariableStateGameInfoBool/Int/String`,
  `VariableStateBinding`, `VariableStateParamBinding`, `VariableStateSimpleLookupAbs`,
  `VariableStateLegacyBinding`): a value-binding abstraction that resolves a named
  value from a **server-authoritative source** (a CVar, a `GameStats` entry, a
  `GamePrefs` entry, or a `GameInfo` string/int/bool). Used by the game-event /
  sequence system (and the data-binding UI) to read live game state; the state
  sources are owned by [game-events.md](game-events.md), [entity-stats.md](entity-stats.md),
  and [sandbox-options.md](sandbox-options.md).
- **`Archetype`** (10 methods): entity archetype record (the character-preset model
  behind `PlayerProfile` / entity variant selection at spawn), tied to
  [protocol-packages.md](protocol-packages.md) §5.1 (EntityCreationData) and
  [spawning.md](spawning.md).
- **`WorldRayHitInfo`** (4): the result struct of a server world raycast (hit
  block/entity/transform), used by the damage/interaction paths in
  [combat-damage.md](combat-damage.md).
- **`TurretInventory` / `VehicleInventory`**: the specialized inventory holders for
  turrets and vehicles ([vehicles-drones-turrets.md](vehicles-drones-turrets.md)),
  built on the same `Bag`/`ItemStack` shapes as [items.md](items.md).
- **`ThreadRegion`**: the per-thread region work unit of the dynamic-mesh save
  pipeline ([dynamic-mesh.md](dynamic-mesh.md) §4).
- **`PathNodePool`** (`WorldGenerationEngineFinal`): a pooled path-node allocator
  used during RWG road/path routing ([world-generation.md](world-generation.md)).

## Changelog

- **2026-07-28:** ILockContext bags; EntityCreateHandle + NetEntityPackageQueue hold-back; PrefabChunk IChunk view.

- **2026-07-24:** Final leftovers batch: 19 dedicated sections covering ~30
  types (caller-verified), `AuthAndLoginManager` investigated and reclassified as
  client-only Discord SDK login, `EntityVBlimp` confirmed dead in stock config,
  `PhysicsBody*` and five infra types reclassified into dedicated scope.
