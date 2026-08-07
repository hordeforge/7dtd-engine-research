# Dedicated misc systems (V3.1.0)

**Owns:** a grab-bag of small dedicated systems each too small for its own doc:
gamestage groups, water-sim apply, boss/companion groups, admin users,
entitlements, XML loaders, chunk/block access interfaces, damage detail types,
player persistence bits, startup helper, nav object classes, multi-block
tracking, EAI tasks, block placement helpers, and drone weapons.
**Not:** the owning systems themselves (each section cross-links its family doc);
client UI, rendering, and Twitch client internals (see the out-of-scope list).
**Evidence:** `GameStageGroup`, `WaterSimulationApplyChanges`, `WaterUtils`,
`BossGroup`, `CompanionGroup`, `AdminUsers`, `EntitlementManager`,
`EntityClassesFromXml`, `EventsFromXml`, `IChunkAccess`, `IBlockAccess`,
`ChunkKey`, `WaterSimulationNative/ChunkHandle`, `DamageSourceEntity`,
`DamageMultiplier`, `HitInfoDetails`, `PersistentPlayerName`,
`EntityBedrollPositionList`, `GameStartupHelper`, `NavObjectClass`,
`MultiBlockManager/TrackedDataMap`, `OversizedBlockUtils`, `EAIRunawayWhenHurt`,
`EAIItemTask`, `BlockTracker`, `BlockPlacement`, `DroneWeapons` IL (dump locally
with `tools/src/DumpMethod`, git-ignored). **Hub:** [`INDEX.md`](INDEX.md).
**Method:** [`re-methodology.md`](re-methodology.md).

Every type below was confirmed dedicated-relevant by walking its callers
(`FindCallers`) back to server-side systems (world/managers/net packages), not
just by existing in the assembly. Types whose entire caller set is UI, avatar,
or render code are listed at the end instead.

---

## GameStageGroup

Static registry of named gamestage groups (`AddGameStageGroup`, `TryGet`,
`Groups`), populated by `GameStagesFromXml` from `gamestages.xml` during
`WorldStaticData` load. `CleanName`/`MakeDisplayName` normalize names for the
editor, but the runtime consumers are server spawn systems: `SleeperVolume` and
`PrefabVolumes.PrefabSleeperVolumeList` resolve a volume's gamestage group via
`TryGet` when deciding which sleeper spawn list applies at the players' current
gamestage. Complements [spawning.md](spawning.md) (sleeper volumes) and the
gamestage math there.

## Water sim apply: WaterSimulationApplyChanges, WaterUtils, ChunkHandle

`WaterSimulationApplyChanges` is the write-back stage of the server water
simulation (one per `ChunkCluster`, own thread via `ThreadLoop`). The sim
records per-chunk water changes through `ChangesForChunk/Writer.RecordChange`,
then `ApplyChanges(Chunk, ...)` commits them to chunk water data and
`SendUpdateToClients` ships a `NetPackageWaterSimChunkUpdate`;
`HasNetWorkLimitBeenReached` throttles the per-tick network budget, and
`RegionFileManager`/`NetPackageDeleteChunkData` call `DiscardChangesForChunks`
when chunks unload or reset. `WaterUtils` is the shared helper set:
`CanWaterFlowThrough(BlockValue)`, `GetWaterLevel`, voxel keys, and
`TryOpenChunkForUpdate` (safe chunk locking for the sim thread).

`ChunkHandle` is not a chunk-access type: it is
`WaterSimulationNative/ChunkHandle`, the per-chunk handle a `Chunk` gets via
`AssignWaterSimHandle` into the native water sim (`SetVoxelSolid`,
`SetWaterMass`, `WakeNeighbours`). All three complement the water pipeline in
[light-mesh-water.md](light-mesh-water.md) §4 (job graph, flow rules, net
backpressure, mass constants).

## BossGroup

Server-side container for a boss encounter: one boss entity plus minions,
created by the game-event actions `ActionSetupBossGroup` /
`ActionUpdateBossGroup` and driven by
`GameEventManager.HandleBossGroupUpdates`, which calls `BossGroup.ServerUpdate`
each tick. Key methods: `HandleAutoPull` and `HandleTeleportList` (keep the
group near players), `IsPlayerWithinServerRange`, `RefreshStats`,
`RemoveMinion`, `DespawnAll`. State is mirrored to clients through
`NetPackageBossEvent`; `GetBossNavClass`/`GetMinionNavClass` name the compass
icon classes clients display (see NavObjectClass below). Complements
[game-events.md](game-events.md).

## CompanionGroup

Thin list wrapper (`Add`, `Remove`, `IndexOf`, indexer) held by
`EntityPlayer.Companions`, which lazily constructs it. **Still an unpopulated stub on V3.1.0 b14
(re-checked 2026-08-06):** `Add` and `Remove` have zero call sites anywhere in the
assembly, so the list is never filled and the only readers are
`XUiC_CompanionEntry*` (client view of an always-empty group). Treat it as
reserved surface for a companion feature, not as live server state.

## AdminUsers

Sub-store of `AdminTools` (the `serveradmin.xml` state): user entries
(`UserPermission`: platform id + permission level) and group entries
(`GroupPermission`, e.g. Steam groups with normal/moderator levels), with
`AddUser`/`AddGroup`/`Remove*`, XML round-trip (`ParseElement`, `Save`), and
the central query `GetUserPermissionLevel(ClientInfo)`. Callers show exactly
who enforces it: `ConsoleCmdAdmin`, the webserver session/permission handlers,
`PlayerSlotsAuthorizer`, `BansAndWhitelistAuthorizer`, and
`Platform.Steam.SteamGroupsAuthorizer` during login. Complements
[console-commands.md](console-commands.md) (command permission levels) and
[webserver.md](webserver.md) (web session permissions).

## EntitlementManager

Singleton gating DLC/cosmetic entitlement sets (`HasEntitlement`,
`GetSetForAsset`, `IsAvailableOnPlatform`, `CheckOverride`). Dedicated-relevant
because two server-side paths consult it: `XmlPatchConditionEvaluator`
implements a `has_entitlement` condition used while patching game XMLs (the
server patches and ships configs), and `Equipment.HasCosmeticUnlocked`
validates cosmetics on player equipment. Store/purchase methods (`OpenStore`)
are client-only paths. Complements [mod-loading.md](mod-loading.md) (XML
patching) and [platform-auth.md](platform-auth.md).

## EntityClassesFromXml

Loader that parses `entityclasses.xml` into the `EntityClass` registry
(`LoadMain` for base defs, `LoadAppend` for extends-append,
`ReplaceProperty` for token substitution), invoked from `WorldStaticData`
during server boot. Everything the server spawns (zombies, animals, vehicles,
drones) is typed by this table, including the reflective `EAIManager
.CreateInstance` AI task wiring (see EAI tasks below). Complements
[spawning.md](spawning.md) and [entity-stats.md](entity-stats.md).

## EventsFromXml

Seasonal calendar loader (`events.xml`): parses `EventDefinition` date windows
and computes moving holidays in code (`EasterSunday`, `FirstSundayOfAdvent`,
`ThanksgivingDate`). `EventDefinition.Active` compares against `Now`, and the
consumers are server systems: `GameEventsFromXml`, the game-event requirement
`RequirementEventActive`, `XmlPatchConditionEvaluator` (seasonal XML patches),
and `ConsoleCmdForceEventDate` to override the date for testing. Complements
[game-events.md](game-events.md).

## Chunk/block access interfaces: IChunkAccess, IBlockAccess, ChunkKey

`IChunkAccess` exposes `GetChunkFromWorldPos`/`GetChunkSync` with static
`Default*` helper implementations so `WorldBase`, `ChunkCluster`, and `Prefab`
share one lookup path; `IBlockAccess` layers `GetBlock`/`GetProp` on top.
Server-side callers include `LightProcessor`, `DynamicMeshChunkProcessor`,
game-event area actions (`ActionFillArea`, `ActionDestroySafeZone`), the A*
voxel grid, and `UAI.UAIConsiderationPathBlocked`. `ChunkKey` is the small
equatable (x,z) key struct used alongside the packed `Int64` keys from
`WorldChunkCache.MakeChunkKey` in chunk dictionaries. Complements
[world-chunks.md](world-chunks.md).

## Damage detail: DamageSourceEntity, DamageMultiplier, HitInfoDetails

Three carriers on the server damage path. `DamageSourceEntity` extends the
damage source with the attacker entity id plus hit transform name/position and
hit UV, flowing through `NetPackageDamageEntity` /
`NetPackageRangeCheckDamageEntity` into `EntityPlayer`/`Explosion`/
`BlockDamage`. `DamageMultiplier` is the per-item material-tag multiplier map
parsed from item `DynamicProperties`, net-serialized (`Read`/`Write`) and
consulted by `ItemActionAttack`, melee/ranged actions, turret and drone fire
controllers. `HitInfoDetails` is the voxel-accurate hit record (block value,
water value, prop ref via nested `VoxelData`/`PropData`) filled by the `Voxel`
raycast and copied through attack, placement, and vehicle code. All complement
[combat-damage.md](combat-damage.md) and [raycast-pathing.md](raycast-pathing.md).

## PersistentPlayerName

Wrapper around a player's `AuthoredText` name inside `PersistentPlayerData`:
`Update(name, PlatformUserIdentifierAbs)` on login, `SetCollisionSuffix` to
disambiguate duplicate names, and `SafeDisplayName` for sanitized output.
Server callers are `PersistentPlayerList` and `GameManager` (login/rename
paths); the many `XUiC_*` callers are just display. Complements
[server-lifecycle.md](server-lifecycle.md) and
[save-persistence.md](save-persistence.md).

## EntityBedrollPositionList

Per-player list of bedroll positions that writes through to
`PersistentPlayerData` (`Set` fetches `GetData()` first, so the position
persists with the player record). Server consumers: `EntitySpawner` and
`World`/`GameManager` respawn logic (spawn-near-bedroll),
`PlayerDataFile`, and `DynamicMeshManager` (bedroll chunk protection).
Complements [save-persistence.md](save-persistence.md) and
[spawning.md](spawning.md).

## GameStartupHelper

Dedicated boot-time helper: `ParseCommandLine`/`parseRawCommandline`,
`LoadConfigFile` (the `serverconfig.xml` path), `InitGamePrefs` +
`ApplyParsedGamePrefs`, and `SetDedicatedServerSettings` (logs level, game
name, max players from `GamePrefs`). Linux-specific checks (`checkLinuxLimits`,
`checkOpenFilesLimit`, `checkMaxMapCount`) verify ulimits and
`vm.max_map_count` before world load, shelling out via
`tryExecuteProcessTerminal`. Called from `GameEntrypoint` and
`Platform.PlatformApplicationManager`. Complements
[server-lifecycle.md](server-lifecycle.md) and
[sandbox-options.md](sandbox-options.md).

Leaves (all V3.1.0 b14 IL):

- **`ParseCommandLine(args)` (IL=82):** parse raw `key=value` args; a
  `configfile` value gets `.xml` appended when it has no dot and is loaded via
  `LoadConfigFile` (failure → false). Every remaining pair is applied with
  `ParsePref(key, value, false, true)`. Dedicated: `parsedGamePrefs[139
  (NoGraphicsMode)] = true`. **Dedicated without a loaded config file →
  error banner ("No server config file loaded ...") + `Application.Quit()` +
  false** - the dedicated server refuses to run without `-configfile`.
- **`LoadConfigFile(filename)` (IL=146):** relative paths are prefixed with
  `GameIO.GetApplicationPath() + "/"`; missing file → error banner +
  `Application.Quit()` + false. Parse with `SdXDocument.Load`; walk the
  `<ServerSettings>` property elements into a `DynamicProperties`; every key
  must have a value ("Value not set" error) and is applied via
  `ParsePref(key, value, quitOnError=true, false)`; success logs
  "Parsing server configfile successfully completed" and sets
  `bConfigFileLoaded = true`.
- **`ParsePref(name, value, quitOnError, ignoreCase)` (IL=74):** empty name →
  config error; a matching `LaunchPrefs.All()` entry → `ParseLaunchPref`;
  else `EnumUtils.TryParse<EnumGamePrefs>` → `ParseGamePref`; unknown →
  config error when quitting, else a warning (command-line args that are not
  config properties are ignored); exceptions → config error. Both pref parsers
  store into `parsedGamePrefs` for `ApplyParsedGamePrefs` to commit.
  `ParseGamePref` (IL=24) uses `GamePrefs.Parse` (IL=45), the typed
  string→object conversion by `PropertyDecl.type` (Int32 TryParse default 0 /
  Float / Bool / String; unknown pref → null) and reports
  `Could not parse config value '{value}'` on failure.
- **`ApplyParsedGamePrefs()` (IL=57):** `parsedGamePrefs` missing → "Expected
  parsed game prefs." + quit + false; else `GamePrefs.SetObject` each parsed
  (enum, value) and clear the dict. Dedicated: `GameUtils.ValidateGameName(pref
  31)` (IL=41: trimmed == original, non-empty, every char passes
  `ValidateGameNameInput` IL=46: `A-Z a-z 0-9 _ -`, `.` only after the first
  char); invalid → banner ("GameName is empty or contains invalid characters.
  Allowed characters: A-Z, a-z, 0-9, dot (.), underscore (_), dash (-) and
  space ( )") + quit + false; valid → `SetDedicatedServerSettings()` + true.
- **`InitGamePrefs()` (IL=36):** log `Last played version: {pref 34}`; set
  `GamePrefs[34 (GameVersion)] = Constants.cVersionInformation.LongStringNoBuild`;
  `initGamePrefsOk = ApplyParsedGamePrefs()`.
- **`SetDedicatedServerSettings()` (IL=51):** log level / game name / max
  players / game mode / crossplay from prefs; then for every existing
  `EnumGamePrefs` value `SetPersistent(pref, false)` (nothing persists to the
  registry on dedicated); `OpenMainMenuAfterAwake = false`.

## NavObjectClass

Registry of compass/map/on-screen icon classes loaded from `nav_objects.xml`
(`NavObjectClassesFromXml.Load`, in the `WorldStaticData` table, so the
dedicated server parses it as part of config load/sync). Rendering is client
work, but server systems reference classes by name: `BossGroup` exposes
`GetBossNavClass`/`GetMinionNavClass` for `NetPackageBossEvent`, and
`AIDirectorAirDropComponent.RefreshCrates` registers supply-crate nav objects
through `NavObjectManager.RegisterNavObject`. Documented here for the name
flow only; the visual side is out of scope. Complements
[aidirector.md](aidirector.md) (air drops) and
[game-events.md](game-events.md).

## TrackedDataMap (MultiBlockManager)

Nested map inside `MultiBlockManager`: `Vector3i -> TrackedBlockData` with
`AddOrMergeTrackedData(pos, blockValue, bounds, TrackingTypeFlags)` and typed
subset accessors (`OversizedBlocks`, `CrossChunkMultiBlocks`, `PoiMultiBlocks`,
`TerrainAlignedBlocks`). Oversized blocks are additionally binned per chunk
(`AddOversizedBlockToChunkBins`) so chunk load/unload can restore or drop
their tracking. This is the server's authority on which placed blocks span
chunks or exceed one cell. Complements [blocks.md](blocks.md) and
[block-shapes.md](block-shapes.md).

## OversizedBlockUtils

Pure geometry helpers for oversized/rotated block bounds: world/local matrix
from position + rotation, world-aligned extents, corner enumeration, and
`EnumerateOverlappingCells` yielding every grid cell an oversized block's
bounds touch. Server callers: `MultiBlockManager` (tracking above),
`AstarManager`/`AstarVoxelGrid` (pathing blockers), and `DecoUtils`
(decoration clearance). Complements [blocks.md](blocks.md) and
[raycast-pathing.md](raycast-pathing.md).

## EAI tasks: EAIRunawayWhenHurt, EAIItemTask

Two entity AI tasks that run in the server-side EAI tick.
`EAIRunawayWhenHurt` extends `EAIRunAway` with a `lowHealthPercent` threshold
(`SetData` from entityclasses props); it has no direct callers because EAI
tasks are instantiated reflectively via `EAIManager.CreateInstance(String)`
from `ai_task` properties and dispatched virtually (`CanExecute`/`Update`).
`EAIItemTask` is the base for item-using AI, subclassed by `EAIDroneItemTask`
for drone behavior. Complements [entity-ai.md](entity-ai.md).

## BlockTracker and BlockLimitTracker

`BlockTracker` is a bounded position set (`CanAdd`, `TryAddBlock`,
`RemoveBlock`) with `PooledBinaryReader/Writer` persistence. Its only consumer
is `BlockLimitTracker`, the server enforcement of per-type placed-block limits:
initialized in `GameManager.StartAsServer`, checked in `Chunk` and
`BlockToolSelection` via `CanAddBlock(..., eSetBlockResponse&)`, persisted with
its own save thread, and mirrored to clients through
`NetPackageBlockLimitTracking`. Complements [blocks.md](blocks.md).

## BlockPlacement

Strategy base class resolving where and how a block lands when placed:
`OnPlaceBlock(...)` returns a `Result` (position, face, rotated `BlockValue`)
and `LimitRotation` clamps rotation modes (45-degree support check included).
Subclasses (`BlockPlacementDoor`, `BlockPlacementTowardsPlacer*`, etc.) are
selected per block; callers include `Block`, `ItemActionPlaceAsBlock`,
`GameUtils`, and the placement console commands, so the same resolution code
runs wherever a block is placed, including server-driven paths. Complements
[blocks.md](blocks.md).

## Drone weapons: HealBeamWeapon, MachineGunWeapon

Nested classes of `DroneWeapons`, driven by `EntityDrone`, which the server
simulates like other entities (see
[vehicles-drones-turrets.md](vehicles-drones-turrets.md)).
`HealBeamWeapon` is the medic module: `findNeededHealType` inspects the target
(`isTargetBleeding`, `isTargetInNeedOfMedical`), `getHealingItemStack` consumes
matching healing items from the drone's inventory, `Fire(EntityAlive)` applies
the heal. `MachineGunWeapon` is the gun module: `Fire`/`_fireWeapon` with
`GetDamageEntity`/`GetDamageBlock` computing damage from the installed weapon
item, feeding the standard damage path in
[combat-damage.md](combat-damage.md).

---

## WorldStats (prefab density budget)

`WorldStats` carries a prefab's mesh-complexity stats (triangles, vertices,
lights), parsed from the prefab's `DynamicProperties` by
`WorldStats.FromProperties`. It looks like editor telemetry, and most of its
consumers are (`CaptureWorldStats`, the editor XUi windows), but one number is
load-bearing on a dedicated server: `PrefabData.Init` computes

```text
DensityScore = (WorldStats.TotalVertices + 50000) / 100000
```

and `DensityScore` is read by the RWG placement code
(`WorldGenerationEngineFinal.PrefabManager` prefab-by-district selection and
`WorldGenerationEngineFinal.StreetTile.SpawnMarkerPartsAndPrefabs`, which carries a
`totalDensityLeft` budget). Since a dedicated server runs RWG at world creation
([world-generation.md](world-generation.md)), prefab vertex counts do influence
which POIs get placed and how many fit in a tile's budget.

Worth noting as a **method caveat**: these are *field* reads inside lambda
closures, so a caller sweep over method calls does not surface them (see
[re-methodology.md](re-methodology.md) on the limits of caller-based
classification). They were found by scanning the disassembly for
`ldfld ... PrefabData::DensityScore`.

---

## Out of scope (verified client-only)

- **WireManager**: pooled wire visuals, not the electrical graph. It
  instantiates `Prefabs/WireNode` GameObjects, handles wire pulse effects for
  `ItemActionConnectPower` holding and camera windows. `GameManager.createWorld`
  does call `WireManager.Init()` unguarded on the dedicated server (pool
  allocation only), but the sole gameplay caller `TileEntityPowered.DrawWires`
  early-outs when the block has no render transform, which is the dedicated
  case. The actual wiring graph is the `PowerItem` parent/child net in
  [tile-entities-power.md](tile-entities-power.md).
- **DismemberedPart**: detached-limb visual (prefab spawn, fade, transform
  follow); all callers are `Avatar*Controller` render classes via
  `DismembermentManager`. The authoritative body damage flags stay on
  `EntityAlive` ([combat-damage.md](combat-damage.md)).
- **RaidEvent, BitsUsedEvent**: Twitch EventSub payload DTOs consumed only by
  `Twitch.TwitchManager`, which runs in the streamer's client
  ([twitch-integration.md](twitch-integration.md); the server side is just the
  `NetPackageTwitchAccess` permission check).
- **WorldStats**: see the dedicated section above. (Previously listed here as
  client-only; that was wrong, its vertex count feeds an RWG density budget.)
- **BaseItemActionEntry** and **ItemActionEntryRepair/Scrap/Craft/Use/Assemble**:
  these are the client craft-menu UI actions (constructed from
  `XUiController`, activated by `XUiC_ItemActionList`), not server crafting
  logic. They mutate the local crafting queue/inventory UI; the server sees
  only the resulting inventory/recipe traffic
  ([crafting-recipes.md](crafting-recipes.md), [items.md](items.md)).

## GameRandom (the shared RNG primitive surface)

`GameRandom` wraps the underlying `Random` instance; every public method is a
thin `NextDouble()` / `Next(int)` wrapper (V3.1.0 b14 IL):

| Method | IL | Value |
|---|---|---|
| `RandomFloat` | 4 | `(float)NextDouble()` - uniform in [0, 1) |
| `RandomRange(float maxExclusive)` | 7 | `(float)(NextDouble() * max)` - [0, max) |
| `RandomRange(float min, float maxExclusive)` | 12 | `(float)(NextDouble() * (max - min) + min)` |
| `RandomRange(int maxExclusive)` | 4 | `Next(max)` - [0, max) |
| `RandomRange(int min, int maxExclusive)` | 8 | `Next(max - min) + min` - [min, max) |

Float ranges are **max-exclusive** like the int ones. Every gameplay caller
(AIDirector components, spawners, loot rolls, party/group picks) funnels
through these, so a single seeded `GameRandom` instance drives each
deterministic subsystem.

Instances come from `GameRandomManager` (a pooled factory):
`CreateGameRandom()` (IL=5) seeds from the manager's `baseSeed`, and
`CreateGameRandom(seed)` (IL=8) allocates a pooled `GameRandom` via
`MemoryPooledObject<GameRandom>.AllocSync(false)` then `SetSeed(seed)`.
Callers include `AIDirector.Init`, `GameEventManager`'s ctor, `ItemValue`'s
procedural-seed ctor, `DynamicMusicManager.Init`, and `EModelInstanceAssets.Load`.

**The generator itself is the classic .NET `Random` (Knuth subtractive),
implemented inline** (V3.1.0 b14 IL): `InternalSample()` (IL=61) advances a
56-entry `SeedArray` with wrap-around indices `inext`/`inextp` (both reset to
1 at 56), computes `value = SeedArray[inext] - SeedArray[inextp]` with the
`int.MaxValue` clamp and `+ int.MaxValue` re-wrap for negatives, stores and
returns. `Sample()` (IL=6) is `InternalSample() * 4.6566128752458E-10`
(2^-31) giving [0, 1); `PeekSample()` (IL=50) computes the same value without
storing; `GetSampleForLargeRange()` (IL=22) draws twice (flipping the sign
from the second draw's parity) and normalizes `(value + 2147483646) /
4294967293` for the wide `Next(min, max)` range. Seeding is the .NET
constructor verbatim (`SetSeed` IL=4 -> `InternalSetSeed` IL=118): `abs(seed)`
with `int.MinValue` mapped to `int.MaxValue`, `mj = 161803398 - seed` into
`SeedArray[55]`, `(21*i) % 55` index scramble with the `mk = mj - mk` walk, 5
mixing passes over all 56 entries, then `inext = 0`, `inextp = 21`. A seeded
`GameRandom` therefore reproduces sequences identical to `System.Random` with
the same seed - deterministic and portable.

## Changelog

- **2026-08-07:** GameRandom algorithm: classic .NET Random (Knuth
  subtractive) inline - 56-entry SeedArray, inext/inextp wrap, Sample()*2^-31,
  PeekSample non-advancing, GetSampleForLargeRange double-draw; sequences
  reproducible from seed (portable).
- **2026-08-07:** GameRandomManager pooled factory: CreateGameRandom()
  baseSeed + AllocSync(false) + SetSeed; callers AIDirector.Init,
  GameEventManager ctor, ItemValue ctor, DynamicMusicManager.Init,
  EModelInstanceAssets.Load.
- **2026-08-07:** GameRandom surface: RandomFloat / RandomRange float+int
  overloads all NextDouble()/Next(int) wrappers, max-exclusive; single seeded
  instance drives deterministic subsystems.
- **2026-07-24:** Initial batch reversal of small dedicated systems (19
  sections, caller-verified); client-only reclassifications listed above.
