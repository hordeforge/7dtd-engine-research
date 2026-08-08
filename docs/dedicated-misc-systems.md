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

## Entity sound dispatch (`Entity.PlayOneShot`, IL=38)

`PlayOneShot(clip, inHead, serverSignalOnly, isUnique, animEvent, volume)` is
the one-shot sound entry every server action uses: with `inHead` it plays in
the listener's head (`Audio.Manager.PlayInsidePlayerHead(clip, -1, 0, false,
isUnique)`); with `serverSignalOnly` false it is either a unique one-shot
(`Audio.Manager.Play(entity, clip, volume, true)`, optionally registering
the returned handle with the anim-event monitor for stop-on-anim) or a
broadcast to everyone nearby (`Audio.Manager.BroadcastPlay(entity, clip,
isUnique, volume)`). The `EntityPlayer` override (IL=16) additionally skips
while the player is a spectator unless `serverSignalOnly` - spectators hear
nothing local, but server-signaled sounds still flow. The matching stop is
`Entity.StopOneShot(clip)` (IL=5) = `Audio.Manager.BroadcastStop(entityId,
clip)`; `Entity.StopAnimatorAudio(type)` (IL=16) stops and removes the
`animatorAudioMonitoringDictionary[type]` handle registered by the
anim-event monitor.

Client-side fade-out record `Audio.Manager/SequenceStopper` (ctor IL=9) holds
`sequenceObjs` (a `List<AudioSource>`) plus `stopTime` - the pending audio-fade
descriptor consumed by `Audio.Manager`'s sequence-stop path.

---

## BlockRadiusEffect (player-local proximity buffs)

Blocks may carry a `BlockRadiusEffect[]` (`radiusSq`, `variable` buff name)
applied to nearby players. `EntityPlayerLocal.BlockRadiusEffectsTick`
(IL=83) is the scan: it rotates a `blockRadiusEffectsIndex` (0..2) and walks
the three chunks around the player's chunk, and for every `TileEntity` that
`IsActive(world)` with a non-null `Block.RadiusEffects` calls
`BlockRadiusEffectsApply(block, tePos)`. The apply (IL=58) clamps the TE
position's y toward the player's (`FastMoveTowards` step 1) and, per effect,
`AddBuff(effect.variable, -1, true, false, -1)` when the player is within
`radiusSq` and lacks the buff - the campfire-warmth style aura. The same
file also hosts `EntityPlayerLocal.ResetBiomeWeatherOnDeath` (IL=15):
`onNewBiomeEntered(null)`, `isIndoorsCurrent = true`, `WeatherBuffUpdate()`,
and clears `weatherBuff` / `weatherGroup` so a respawned player starts with
neutral weather state.

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

Registry leaves: `FromString(name)` (IL=3) is **`name.GetHashCode()`** (the
class id is the string hash, which is why callers pass the name and get an
id); `GetId(name)` (IL=30) is a linear scan over `EntityClass.list` by
`entityClassName` equality (-1 on miss); `GetEntityClass(id)` (IL=7) /
`GetEntityClassName(id)` (IL=10) are `TryGetValue` reads, the latter falling
back to the literal string `"null"`.
`GetEntityClassWithinMaxTier(ec, maxTier)` (IL=30) walks the
`GetPreviousTierEntity()` chain while `ec.EntityTier > maxTier`, warning
`EntityFactory CreateEntity: No entity within max tier ({0}) found for {1}`
and returning null when the chain runs out.

## EventsFromXml

Seasonal calendar loader (`events.xml`): parses `EventDefinition` date windows
and computes moving holidays in code (`EasterSunday`, `FirstSundayOfAdvent`,
`ThanksgivingDate`). `EventDefinition.Active` compares against `Now`, and the
consumers are server systems: `GameEventsFromXml`, the game-event requirement
`RequirementEventActive`, `XmlPatchConditionEvaluator` (seasonal XML patches),
and `ConsoleCmdForceEventDate` to override the date for testing. Complements
[game-events.md](game-events.md).

## Static-data XML loaders (misc)

The boot-time XML loaders that are not their own doc. All entry points are
6-IL coroutine factories (the real parse runs in the iterator's `MoveNext`)
except the weather loader, which is a real body:

- **`SoundsFromXml`**: `CreateSounds` (IL=6) is a coroutine entry (the
  `WorldStaticData` static-data chain pulls it via `ldftn`).
  `ParseNode(master, root)` (IL=70) collects the
  `ControllerVibrationAudioSourceExclusions` source names, then parses every
  `<SoundDataNode>` via `Parse` (IL=544): the group name is the node's first
  attribute, each child element is dispatched case-insensitively. `<noise>`
  fills `NoiseData` (volume / time / heat_map_strength / heat_map_time
  default 100 / muffled_when_crouched default 1); `<audioclip>` builds a
  `ClipSourceMap` (ClipName, AudioSourceName defaulting to the node's
  audiosource, Loop -> forceLoop, DistantClip / DistantSource,
  AltSound -> alt clip map, Subtitle -> subtitleID / hasSubtitle, profanity
  -> hasProfanity) and `PreloadBundle`s all four clip/source names; scalar
  children map to the group's fields (localcrouchvolumescale,
  crouchnoisescale, noisescale, maxvoices, maxVoicesPerEntity,
  prioritizeNewNodes, maxrepeatrate, immediate, sequence,
  runningvolumescale, lowestpitch, highestpitch, distantfadestart /
  distantfadeend, channel `mouth` = 0 else 1, priority, vibratecontroller,
  vibrationstrengthmultiply); `ignoredistancecheck` registers the group with
  `Audio.Manager.AddSoundToIgnoreDistanceCheckList`. A node with
  `vibratecontroller` still clears the flag when its audio source sits in
  the exclusions list, then `Audio.Manager.AddAudioData` stores the group.
  `ParseSubtitleNode` (IL=104) builds `SubtitleData` (name, contentLocId,
  speakerColor, speakerLocId) plus `SpeakerColors` (name = first attribute,
  color = last) and hands both lists to `Audio.Manager.AddSubtitleData`.
- **`WeatherSurvivalParametersFromXml.Load` (IL=121)** (from the
  `_LoadWeather` coroutine): throws `No element <weathersurvival> found!`
  on an empty root, collects `<property>` elements into a
  `DynamicProperties`, clears and rebuilds `WeatherManager` temperature
  offsets from each `TemperatureHeight` descendant (height / addDegrees ->
  `AddTemperatureOffSetHeight`), then reflects over the `WeatherParams`
  static class: every float field declared on it whose name exists in the
  properties is set via `SetValue(null, GetFloat(name))` - the XML-to-code
  binding is by field name.
- **Coroutine wrappers** (entry IL=6 each): `MaterialsFromXml.CreateMaterials`
  (from `WorldStaticData`), `MiscFromXml.Create` (called by
  `WorldStaticData.ReloadMisc` after `AnimationDelayData.InitStatic` /
  `AnimationGunjointOffsetData.InitStatic`, then
  `ThreadManager.RunCoroutineSync`), `MusicDataFromXml.Load` (from the
  `_LoadMusic` coroutine into the DynamicMusic pipeline), and
  `BiomeSpawningFromXml.Load` (from the `_LoadSpawning` coroutine into the
  `BiomeSpawningClass` list). The parse bodies are the compiler-generated
  `MoveNext` methods of each iterator.

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

Leaves (IL-verified): `GetData()` (IL=7) resolves the player record via
`GetPlayerDataFromEntityID(theEntity.entityId)`; `GetPos()` (IL=13) returns
`BedrollPos` or the `(0, int.MaxValue, 0)` sentinel; `Set(pos)` (IL=11) stores
the position and calls `ShowBedrollOnMap()`; `Clear()` (IL=8) delegates to
`PersistentPlayerData.ClearBedroll()`; `Count()` (IL=9) is 0 for the sentinel
else 1; `get_Item(idx)` (IL=3) ignores the index and returns `GetPos()`.

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

The `Next` overloads behind the int ranges are the .NET wrappers: `Next()`
(IL=3) = `InternalSample()`; `Next(max)` (IL=14) = `(int)(Sample() * max)`
with a negative-max `ArgumentOutOfRangeException`; `Next(min, max)` (IL=37)
validates `min <= max`, uses `(int)(Sample() * range)` when the range fits in
`int` and the two-draw `GetSampleForLargeRange` otherwise;
`NextBytes(buffer)` (IL=26) fills with `(byte)(InternalSample() % 256)`.

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

## DynamicProperties (the XML property bag)

`DynamicProperties` is the generic `name`/`value` bag every XML-defined object
carries (block properties, entity classes, vehicle parts, buffs, game events,
loot, quests - see each family doc). It is one struct with **six
dictionaries** (V3.1.0 b14 IL):

| Field | Type | Filled by |
|---|---|---|
| `Values` | `Dictionary<string,string>` | the `value` attribute of a `<property name="..." value="...">` |
| `Params1` / `Params2` | `Dictionary<string,string>` | optional `param1` / `param2` attributes |
| `Data` | `Dictionary<string,string>` | optional `data` attribute (semicolon `k=v` text) |
| `Classes` | `Dictionary<string, DynamicProperties>` | nested `<property class="...">` groups |
| `Array` | `Dictionary<string, List<Dictionary<string,string>>>` | `AddArray` item lists |

**XML ingestion:** `Parse(element, doValueReplace)` (IL=123) is the core. An
element carrying a `class` attribute resolves `GetOrCreateClass(name)`
(IL=17, creates on miss) and recurses its child `property` elements into that
class. A leaf property requires a `name` attribute (else throws `Attribute
'name' missing on property`) and `ValidateKey(name)` (IL=21, throws on an
empty key or one containing `.`), reads the `value` attribute (with
`doValueReplace` the value is passed through
`EntityClassesFromXml.ReplaceProperty`, IL=15: a value starting with `^` is a
token looked up in `sReplaceProperties`, see the `EntityClassesFromXml`
section above), stores non-empty `param1`/`param2`/`data` attributes into
their dictionaries, throws when the name collides with an existing class
(`Cannot create property '...': a class with the same name already exists.
Property and class names must be unique.`), and finally sets
`Values[name] = value`. `Add(element, doValueReplace)` (IL=5) delegates to
`Parse`; `AddArray(node)` (IL=70) builds `Array` from `<item>` child
elements (each item becomes a dict of its attributes; the list is cleared
before re-populating); static `Load(directory, name)` (IL=37) reads an
`XmlFile`, adds its root `property` elements without replacement, and returns
false (with `Log.Exception`) on failure.

**Accessors:** `GetValue(name)` (IL=10) is a bare `Values.TryGetValue`
(null on miss). `TryGetValue(name, out)` (IL=8) adds `ValidateKey`; the class
overload (IL=18) resolves `Classes[name]` and recurses, returning
false + null for a missing class. Typed reads default silently on miss and
parse failure: `GetString` (IL=9) returns `String.Empty` when absent;
`GetBool` (IL=13) parses with `StringParsers.TryParseBool` and discards the
parse result (a malformed bool reads `false`); `GetInt` (IL=13) uses
`Int32.TryParse`; `GetFloat` (IL=13) uses `StringParsers.TryParseFloat`.
The `Parse*` out-param family is the stricter twin: `ParseBool` (IL=26)
writes the parsed value on success but on failure logs
`Can't parse bool {0} '{1}'` (Warning) and keeps the caller's default;
`ParseString` (IL=9) writes only when the property exists.
`GetParam1(name)` (IL=10) is `Params1.TryGetValue`; `GetClass(name)` (IL=10)
is `Classes.TryGetValue`. Two localization oddities:
`GetLocalizedString(name)` (IL=9) is byte-identical to `GetString` (raw
value, no localization), while `ParseLocalizedString` (IL=12) is the one that
runs `Localization.Get(value, false, null)`.

**Structured data helpers:** `ParseData(data)` (IL=82) splits a
`;`-separated list of `k=v` pairs (or a single `k=v`) into a dict, logging
`ParseData error parsing {0}, {1}` on malformed input; `ParseKeyData(key)`
(IL=29) resolves `Data[key]` through `ParseData` (null when the key is
absent). `ParseStringFloatDictWithSubStringKey(prop, sep, source, out)`
(IL=47) walks a source dict and collects every key starting with
`prop + sep`: the substring after the separator becomes the output key
(empty subkeys skipped), the value is parsed as float
(`StringParsers.ParseFloat(v, 0, -1, 511)`).

**Copy with exclusions:** `CopyFrom(other, exclude)` (IL=78) copies
`Values`/`Params1`/`Params2`/`Data` via `copyDict` (IL=27, skipping keys
rejected by `copyKey`) and recurses `Classes`, creating missing destination
classes. `copyKey` (IL=43) rejects keys present in the exclude set and keys
that are a dotted-prefix of an excluded path (excluding `a.b` also excludes
`a`); per-class exclusion lists are derived by `GetNestedExclusions` (IL=42)
which keeps every `class.`-prefixed entry and strips the prefix. The `.`
path separator is exactly why `ValidateKey` bans dots in property names.
`Clear` (IL=16) empties `Values`, `Params1`, `Params2`, `Data`, and
`Classes` - but not `Array`.

**Serialization:** `Deserialize(reader, out value)` (IL=214) is the
generated MemoryPack v1 formatter with a 6-property header, reading in order
`Values`, `Params1`, `Params2`, `Data`, `Classes`, `Array` (a partial count
reads only those fields; a null target is allocated). The writer mirrors the
same order, so any save/wire boundary that carries a `DynamicProperties`
(block entity data, quest state, entity classes) uses exactly these six
fields.

**Remaining leaves (all IL-verified):** `ParseByte(name, ref byte)` (IL=26)
is the byte twin of the `Parse*` family (writes on `TryParseUInt8` success,
else warns `Can't parse byte {0} '{1}'` and keeps the default);
`ParseColorHex(name, ref Color)` (IL=10) runs `StringParsers.ParseHexColor`
over the value when present; `TryParseRange(name, IntRange/FloatRange)`
(IL=22 each) parses through `StringParsers.TryParseRange(..., '-')` and
falls back to the given default. `SetParam1(name, param1)` (IL=29) validates
the key, ensures a null `Values` entry, and sets/creates the `Params1`
entry (the 3-arg overload routes through `GetOrCreateClass`);
`TryGetParam1(name, out)` (IL=8) is `ValidateKey` +
`Params1.TryGetValue`; the class overload (IL=18) returns false + null on a
missing class. `RegisterFormatter()` (IL=25) lazily registers the
`MemoryPack` formatters for `DynamicProperties`, `DynamicProperties[]`,
`Dictionary<string,string>`, `Dictionary<string,DynamicProperties>`, the
nested `Dictionary<string, List<Dictionary<string,string>>>`, and
`List<Dictionary<string,string>>` (guarded by `IsRegistered`).
`PrettyPrint()` (IL=9) / `PrettyPrint(sb, indent)` (IL=133) renders the bag
for logs: a `Properties:` header with sorted `name={0}, value={1}` rows
(plus `, param1=` / `, param2=` / `, fields=` suffixes when the dicts hold
the key), then a `Classes:` header with one recursive block per class under
a deeper indent.

## StringParsers (the text-to-value contract)

`StringParsers` is the shared text parser behind XML properties, net strings,
and console input (the `Get*`/`Parse*` accessors above call into it). The API
is two-tier: `Parse*` throws on malformed input, `TryParse*` returns a bool
and leaves the out value at the caller's default. Every numeric parser exists
with a substring overload `(String input, Int32 startIndex, Int32 endIndex,
NumberStyles style)`; the short overloads fix the defaults:

- **float / double** short overloads call `(0, -1, 511)` - whole string,
  styles **511** = every `NumberStyles` flag except `AllowHexSpecifier` (512).
- **integer** short overloads call `(0, -1, 7)` - whole string, styles **7** =
  `AllowLeadingWhite | AllowTrailingWhite | AllowLeadingSign`. Integers never
  accept decimal points, exponents, thousands separators, or currency
  (verified on `TryParseSInt32` IL=7 and `TryParseFloat` IL=7).

**The internal engines** (V3.1.0 b14 IL): `internalParseDouble` (IL=632)
rejects `AllowHexSpecifier` outright (throws `ArgumentException: Double
doesn't support parsing with 'AllowHexSpecifier'`), rejects style values
above 511, and writes the failure exception into an out `Exception` when
parsing for real, returning bool in try mode; negative `endIndex` means
`Length - 1`, and out-of-range indexes throw `ArgumentException` quoting the
input (`_startIndex ({0}) out of range (input='{1}')`).
`internalParseBool` (IL=180) trims whitespace inside `[start, end]`, then
compares the substring against `Boolean.TrueString` / `Boolean.FalseString`
with `Ordinal` or `OrdinalIgnoreCase` per the flag - **only `True`/`False`
forms parse** (no `1`/`0`); a mismatch throws `FormatException: Value is not
equivalent to either TrueString or FalseString (input='...')`.
`internalParseInt64` (+ Advanced) is the same shape for the whole signed and
unsigned integer family (`Parse/TryParseSInt8..64`, `UInt8..64`).

**Float range guard:** `ParseFloat` (IL=19) parses as double, then throws
`OverflowException` when the value sits more than ~3.61e29 above
`float.MaxValue` (roughly 1e-9 relative) and is not positive infinity, else
`conv.r4`. `TryParseFloat` (IL=33) mirrors this with out = 0 / false.

**The separator scanner:** `GetSeparatorPositions(input, sep, expected,
start, end)` (IL=182) fills a `SeparatorPositions` struct (`Sep1..Sep4` +
`TotalFound`) by successive `IndexOf` scans, stopping early once
`TotalFound == expected` (so `expected` is how many separators the caller
wants); it validates `expected > 0`, non-null input, and the index range.
`findOther(pos&, input, other)` (IL=16) is a one-char consumer (if
`input[pos] == other`, advance `pos`, return true) used by the bool
tokenizer.

**Structured parsers built on the scanner:**

| Parser | IL | Contract |
|---|---|---|
| `ParseVector3(input, start, end)` | 93 | strips a surrounding `(...)` pair, then requires **2** commas (else zero vector); three floats with styles 511 |
| `ParseVector3(input, defaultValue)` | 71 | 0 commas -> `(v, def, def)`; 1 comma -> `(v1, v2, def)`; 2 -> `(v1, v2, v3)` |
| `ParseVector3i(input, start, end, errorOnFailure)` | 72 | int triple; the bool controls error vs silent failure |
| `ParseQuaternion(input)` | 53 | **3** commas required (else identity); `Quaternion(x, y, z, w)` |
| `ParseColor` -> `TryParseColor` | 8 / 112 | `RGBA(...)`-wrapped or bare, **2 or 3** commas (3 or 4 floats) -> `Color(r,g,b)` (alpha 1) or `Color(r,g,b,a)`; `ParseColor` falls back to white, `TryParseColor` to false |
| `ParseMinMaxCount(int)` / `(float)` | 61 / 61 | **0 or 1** comma (else throws `Parsing error count (input='...')`): single value -> min = max = value; pair -> (min, max); int styles 7, float 511 |
| `ParseMinMaxCount(input)` | 46 | returns a `Vector2(x = min, y = max)` normalized by `Mathf.Min/Max`; zero vector when not exactly one comma |
| `ParseList(input, sep, parserFunc)` | 53 | `IndexOf`-loop split; each segment parsed by `Func<string,int,int,T>` over `(input, start, end)` |

The two face-mask parsers `ParseWaterFlowMask` / `ParseCoverFaceMask` are
documented with their consumers in [`block-shapes.md`](block-shapes.md) §5.

## Localization (the CSV text pipeline)

`Localization` (all IL-verified) loads `Data/Config/Localization.csv` into a
`Dictionary<string, string[]>` (`mDictionary` keyed by the localization key,
each value one row across the language columns) plus a case-insensitive
twin. `LoadAndSelectLanguage(forceReload)` (IL=14) nulls the dicts when
forcing, lazily runs `loadBaseDictionaries()` (IL=25: clears
`allLanguages` / `patchedCells`, news the dicts, `loadCsv(GameIO.GetGameDir
("Data/Config") + "/Localization.csv", false)`, then `updateLanguages()` +
`WriteCsv()`), and finishes with `selectLanguage()` (IL=32: resolves
`defaultLanguageIndex` / `currentLanguageIndex` via
`findUserLanguageColumns(KEY row, RequestedLanguage)` (IL=45, the `english`
column + the user column, -1s on an empty header), broadcasts `OnLocalize`
to UIRoot, invokes `LanguageSelected(ActiveLanguage)`, and returns
`currentLanguageIndex >= 0`).
`loadCsv(bytes, patch, serverData)` (IL=166) parses with a `ByteReader` /
`ReadCSV`, requiring a `KEY` first cell (else
`Invalid localization CSV file...`); non-patch clears both dicts, patch
builds a column-translation table against the existing header (validating
each new column against `languageHeaderMatcher`, `context`-prefixed
columns allowed, and locating the `UsedInMainMenu` column), then feeds every
row to `addCsv` (IL=201): a missing key warns
`Localization: Entry missing a key!`, a duplicate warns
`Localization: Duplicate key "..." found!`, and patch rows merge into the
existing entry (resizing, marking `patchedCells`, skipping server-data cells
in the `UsedInMainMenu` column).
`LoadPatchDictionaries(modName, folder, loadingInGame)` (IL=26) merges
`{folder}/Localization.csv` (`[MODS] Loading localization from mod:` /
`Could not load localization from` logs), then `updateLanguages()` +
`selectLanguage()`; `LoadServerPatchDictionary(data)` (IL=14) is the
`NetPackageLocalization` receive side (error `Could not load localization
from server!`); `ReloadBaseLocalization()` (IL=3) is `LoadAndSelectLanguage
(true)`; `checkLoaded(throwExc)` (IL=15) lazily loads and throws
`Localization could not be loaded` when forced.
`updateLanguages()` (IL=36) rebuilds `allLanguages` and
`languageToColumnIndex` from the KEY row; `get_TotalKeys()` (IL=5) is the
dict count; `get_ActiveLanguage()` (IL=17) is
`allLanguages[currentLanguageIndex]` with an `english` fallback;
`getLanguageEntry(entry, column, out result, prefix)` (IL=38) returns the
cell, prefixing it when `LocalizationChecks` is on.
`FormatListAnd(items)` / `FormatListOr(items)` (IL=7 each) build a localized
list via `formatListX` using the `listAnd*` / `listOr*` keys (two / start /
middle / end templates).

## ParticleEffect (FX data + spawn / audio)

`ParticleEffect` is the serializable FX record every `NetPackageParticleEffect`
carries (wire census: [`protocol-packages.md`](protocol-packages.md)). The
dedicated server's role is **scheduling and audio**, not rendering: the FX
prefab is instantiated only on clients, but the spawn call registers the
effect's sound with the AI director so zombies hear it.

**Data model + wire layout (`Read` IL=53):**

| Field | Wire | Note |
|---|---|---|
| `ParticleId` | i32 | the effect id; `ToId(name)` (IL=3) is **`name.GetHashCode()`** |
| `pos` | Vector3 | `StreamUtils.ReadVector3` |
| `rot` | Quaternion | `StreamUtils.ReadQuaterion` |
| `color` | Color32 | `StreamUtils.ReadColor32` |
| `soundName` | string | empty string normalized to **null** |
| `additionalHitSoundName` | string | empty -> null |
| `volumeScale` | f32 | |
| `parentEntityId` | i32 | -1 = world-space |
| `attachment` | u8 | `None=0 / Head=1 / Pelvis=2` |

`NetPackageParticleEffect` appends `entityThatCausedIt:i32`,
`forceCreation:bool`, `worldSpawn:bool` after the effect record.

**`GameManager.SpawnParticleEffectServer(pe, entityId, forceCreation,
worldSpawn)` (IL=41):** no-op without a world; spawns through
`ParticleEffect.SpawnParticleEffect` (which on a dedicated host returns
immediately - only the audio registration survives), then: a non-server caller
sends `NetPackageParticleEffect` to the server, while the server broadcasts it
to all (flags 192). The receiving clients run
`SpawnParticleEffectClient` (IL=7) / `...ForceCreation` (IL=6), which just
call the local spawn.

**`FireControllerUtils.SpawnParticleEffect(pe, entityId)` (IL=40)** is the
fire-block spawn twin: on a server that is not dedicated it calls
`GameManager.SpawnParticleEffectClient(pe, entityId, false, true)`; on a
client it `Setup`s a `NetPackageParticleEffect` and sends it to the server;
on a dedicated server (or as the final fallback) it broadcasts the package
on channel **192** to everyone (`SendPackage(... -1, -1, entityId, -1,
channel 192, ...)`). The dedicated host therefore ships the fire FX to all
clients without ever instantiating it locally.

**`ParticleEffect.SpawnParticleEffect(pe, entityThatCausedIt, forceCreation,
isWorldPos)` (IL=339):** the client-side instantiation; the server-relevant
parts are:

- **Audio -> AI noise:** `PlaySoundInServer(entityId, pos, soundName,
  volume)` (IL=18) runs on the server for `soundName` and
  `additionalHitSoundName`: a non-empty name goes to
  `world.aiDirector.OnSoundPlayedAtPosition(entityId, pos, soundName,
  volume)` - a particle effect with a sound is a **noise event** for the
  zombie hearing model. `PlaySoundInClient` is the render-side twin.
- **Dedicated short-circuit:** `GameManager.IsDedicatedServer()` returns null
  before any prefab work; the host never instantiates FX.
- **Entity-bound effects:** with `entityThatCausedIt != -1` and
  `!forceCreation`, the spawn tracks instances per entity in the static
  `entityParticles : Dictionary<int, List<EntityData>>` and enforces a
  **4-instance cap per (entity, ParticleId)**: a 4th concurrent instance
  removes the oldest before spawning. Pruned entries (destroyed transforms)
  are dropped on every spawn.
- **Instancing:** `GetDynamicTransform(ParticleId)` (the loaded prefab) is
  instantiated at `pos`/`rot` (`isWorldPos` subtracts `Origin.position`),
  `color` is applied to renderers without a `ParticleSystem`, and a non-zero
  `opqueTextureId` swaps `_MainTex`/`_BumpMap` to the mesh-0 texture atlas.
  `GetParentTransform()` (IL=58) resolves `parentEntityId` from
  `world.Entities` and, per `attachment`, `emodel.GetHeadTransform()`
  (Head) / `GetPelvisTransform()` (Pelvis).

`Init()` (IL=10) roots everything at the `/Particles` GameObject
(`RootT` + `Origin.Add`) and clears `entityParticles`; `IsAvailable(name)`
(IL=5) = `loadedTs.ContainsKey(ToId(name))`.

## FastTags (the tag bitmask)

`FastTags<TTagGroup>` is the shared tag set used across the engine for
"is this tagged X" checks (item tags, entity groups, buff tags, quest tags,
`MovementTagIdle`, `ignoreWhenHeld`, loot tags; each `TagGroup` - e.g.
`TagGroup.Global` - is its own registry). V3.1.0 b14 IL:

**Storage:** the value is a `UInt64[] bits` with a **single-bit fast path**:
a one-bit tag stores the bit number in the `singleBit` field instead of an
array. The bit allocation itself is **lazy and global per group**: `GetBit`
(IL=56) trims the name, looks it up in the static
`tags : CaseInsensitiveStringDictionary<int>` (name -> bit), and on a miss
assigns the next free bit via `Interlocked.Increment(next)` - first-use order,
thread-safe - registering both `tags` and the reverse
`bitTags : Dictionary<int,string>` and growing the cached all-ones tag
`allInternal` (every word `0xFFFFFFFFFFFFFFFF`) to cover it. So a tag has no
fixed number; it is whatever bit it first got.

**Construction:** `GetTag(name)` (IL=3) is the single-bit ctor;
`Parse("a,b,c")` (IL=90) splits on `,`, resolves each name with `GetBit`, and
ORs them into a fresh `UInt64[]` through a lock-guarded scratch buffer
(`maskList` under `Monitor`, cleared after use). `SetBit(bit, extended)`
(IL=18) = `extended[bit >> 6] |= 1 << (bit & 63)`. `CombineTags` ORs two to
five sets: the 2-arg is `op_BitwiseOr` (IL=4); the 3/4/5-arg forms allocate a
max-length array and OR word-by-word. `Remove(other)` (IL=138) is the
bitwise-AND-NOT.

**Tests:** `Test_Bit(bit)` (IL=46) handles empty / single-bit / array paths
with a bounds check; `Test_AllSet(other)` (IL=99) is the subset test (`this
& other == other`, with single-bit fast paths); `Test_AnySet(other)` (IL=70)
is overlap; `Test_IsOnlyBit(bit)` asks whether the set is exactly that one
bit. `get_IsEmpty()` (IL=34) = `singleBit <= 0` and every word zero;
`get_all()` (IL=2) returns the cached `allInternal`. Reverse mapping:
`GetTagNames()` (IL=78) walks each set bit through `bitTags` (single-bit path
included); `ToString()` (IL=34) is the comma-joined names, so a parsed tag
round-trips to the same string it was built from.

## MemoryPools (the object pool surface)

`MemoryPools` is the static registry of the engine's object and array pools;
`MemoryPooledObject<T>` is the pool primitive behind every
`AllocSync`/`FreeSync` call site (chunks, `CBCLayer`, `GameRandom`, network
streams, `VoxelMeshLayer`, ...). V3.1.0 b14 IL:

**`MemoryPooledObject<T>` is a stack-style free list** (`List<T> pool` +
`int poolSize` free count). `Alloc(bReset)` (IL=33): with the pool empty it
returns `Activator.CreateInstance<T>()` (a fresh object); otherwise it pops
the top slot (`pool[--poolSize]`) and clears the slot (`pool[poolSize] =
default(T)`); when `bReset` and the item implements `IMemoryPoolableObject`
it runs `Reset()`. `AllocSync(bReset)` (IL=20) wraps `Alloc` in a
`Monitor.Enter/Exit(pool)` critical section - the pools are safe for the
path/worker threads. `Free` pushes back onto the list; the `FreeSync`
overloads (`T`, `IList<T>`, `Queue<T>`) are the locked twins.
`Cleanup()` (IL=43) calls `IMemoryPoolableObject.Cleanup()` on every
non-null pooled item, clears the list, and zeroes the count.
`GetPoolSize()` (IL=3) is the free count; `SetCapacity(n)` sets the list
capacity and `maxCapacity`.

**`MemoryPools.InitStatic(usePools)` (IL=45)** sizes the main object pools
(capacity 0 when `usePools == false`, which makes every `Alloc` fresh):

| Pool | Type | Capacity |
|---|---|---|
| `PoolChunks` | `Chunk` | 1000 |
| `poolCBL` | `ChunkBlockLayer` | 50000 |
| `poolVML` | `VoxelMeshLayer` | 1000 |
| `poolCGOL` | `ChunkGameObjectLayer` | 1000 |
| `poolMS` | `PooledMemoryStream` | 40 |
| `poolCBC` | `CBCLayer` | 50000 |

The full static set (`.cctor`) adds the second stream pool
`poolMemoryStream` (the net hot path, see
[`dedicated-leftovers.md`](dedicated-leftovers.md)), `poolBinaryReader` /
`poolBinaryWriter`, `poolNameIdMapping`, the `MemoryPooledArray<T>` family
(`poolVector3`, `poolVector4`, `poolVector2`, `poolInt`, `poolUInt16`,
`poolFloat`, `poolColor`, `poolByte`), the `poolCBLUpper24BitArrCache` /
`poolCBLLower8BitArrCache` `List` caches, and a `DynamicObjectPool s_pool`.

## StreamUtils (the binary wire/save primitives)

`StreamUtils` is the static helper layer behind every
`StreamUtils.Read*` / `Write` call in the wire and save layouts
(`protocol-packages.md`, `save-region.md`, this file). Two layers:
`BinaryReader`/`BinaryWriter` helpers (component-wise) and raw
`Stream` / `byte[]` readers. V3.1.0 b14 IL:

**Vectors and quaternions:** `ReadVector3` (IL=8) = 3 x `ReadSingle`;
`ReadVector3i` (IL=8) = 3 x `ReadInt32`; `ReadQuaterion` (IL=10) = 4 x
`ReadSingle` (the API misspelling is in the assembly); Vector2 / Vector2i
follow the same pattern. The `Write(BinaryWriter, ...)` twins write the
components in the same order, so every vector/quaternion field in a package
body is plain little-endian components.

**Color32 packing:** `ReadColor32` (IL=39) reads **one `u32`** and unpacks it
RGBA byte order (`R = v >> 24`, `G = v >> 16`, `B = v >> 8`, `A = v`), each
divided by 255 into a `Color`. `WriteColor32` (IL=34) packs
`r*255 << 24 | g*255 << 16 | b*255 << 8 | a*255` and writes the `u32` - so a
color on the wire is always 4 bytes with red in the high byte.

**Null-flagged strings:** `ReadString` (IL=8) reads a `bool` first - `false`
means **null**, `true` means a .NET length-prefixed string; `Write(BinaryWriter,
String)` (IL=11) mirrors it. This is the "null-string" convention seen across
package bodies (e.g. `ParticleEffect.soundName` normalizes `""` to null).

**Guid:** `ReadGuid` (IL=18) reads exactly 16 bytes into a span (a short read
throws `EndOfStreamException: Failed to read 16 bytes for Guid`) and builds
`new Guid(span)`; the writer emits the 16 raw bytes.

**Varints:** `Read7BitEncodedInt` (IL=37) is the classic 7-bit varint (max 5
bytes, `FormatException: Illegal encoding for 7 bit encoded int` past 35
bits); `Write7BitEncodedInt` (IL=24) / `Write7BitEncodedSignedInt` (IL=70)
and the signed reader are the encoders.

**Raw integers:** `ReadInt32(Stream)` (IL=28) assembles four little-endian
bytes; `ReadInt32(Byte[], ref offset)` (IL=56) and `ReadByte(Byte[], ref
offset)` (IL=12) read from an in-memory buffer advancing the index;
`Write(Stream, Int32)` (IL=31) / `Write(Byte[], Int32, ref offset)` (IL=67)
write little-endian, and the `Int16`/`UInt16`/`Int64` variants follow.

**Stream helpers:** `StreamCopy` (IL=42/48) copies a stream in chunks through
a caller temp buffer (with optional exact-length and flush);
`WriteStreamToFile` (IL=15/16) dumps a stream to a file (optional length),
the dump path used for save/backup artifacts.

**Binary/stream utility leaves:** `BitConverterLE` is the little-endian raw
converter (`GetUIntBytes` IL=56, `GetULongBytes` IL=112, `GetBytes(float)`
IL=5) that `PooledBinaryReader` / `PooledBinaryWriter` use for the pooled
serialization layer. `StreamWriteSizeMarker` (fields `Position` +
`EMarkerSize`) is the "write a size placeholder, patch it later" record
`PooledBinaryWriter` hands out, and `Quest` / `QuestJournal` use it to
reserve the byte-length slot of a serialized payload. `ByteLengthUtils` pre-computes writer sizes
(`GetBinaryWriter7BitEncodedIntLength` IL=22, `GetBinaryWriterLength`
IL=9). `SimpleBitStream` is the bit accumulator (`Add(bool)` IL=42,
`GetNext` IL=41, `Reset` IL=13, byte/bit cursors plus a `Write(BinaryWriter)`)
that `Prefab` uses to pack per-cell flags. `IOUtils.CalcHashSync` (IL=23) /
`CalcHashCoroutine` (IL=18) / `CalcCrcCoroutine` (IL=15) hash or CRC a file
within a per-frame byte budget; `AdminTools` and `StockFileHashes` use it
for the world-file integrity checks. `WaveReader` (a WAV stream reader,
`Read(float[])` IL=54) loads audio assets, client-side.

## Threading-semantics and collider config leaves

- **`IMapChunkDatabase/DirectoryPlayerId`** (fields `file`, `dir`): the
  per-player directory record of the async map-chunk database, built by
  `GameManager` when a player's map data is saved/loaded (`SavePlayerData`
  on the dedicated path queues the map-chunk DB save task). The minimap
  producer side is [protocol-packages.md](protocol-packages.md) §3.3.
- **`NoThreadingSemantics`** (`Synchronize` / `InterlockedAdd` stubs): the
  `IThreadingSemantics` fallback with no real locking; `World` builds its
  `SharedChunkObserverCache(chunkManager, 3, new NoThreadingSemantics())`
  with it, so the shared chunk-observer cache uses plain synchronous access
  on the main thread.
- **`PhysicsBodyColliderConfiguration`** (`Read` IL=160 / `Write` IL=100 /
  `vecToString` / `vecFromString`): the XML collider config record the
  `PhysicsBodyBoxCollider` / `PhysicsBodyCapsuleCollider` read (center /
  size / radius / height vectors serialized as strings); the base
  `PhysicsBodyColliderBase.enableRigidBody` (IL=40) toggles the entity
  rigidbody, so the config only matters where entity physics bodies are
  instantiated.

## Discord ID mapping package

`NetPackageDiscordIdMappings.ProcessPackage` (IL=58) carries the Discord
Social-SDK user mapping (the stock-side surface of the third-party SDK).
The single-entry form validates `ValidEntityIdForSender`, stores
`sender.DiscordUserId` on the server, and hands off to
`DiscordManager.UserMappingReceived(entityId, remove, discordId, false)`.
The multi-list form errors
`[Discord] Received invalid User ID mapping package` on a length mismatch
(and `[Discord] Received User ID mapping package on server with multiple
entries` when a multi-entry form hits the server) before
`DiscordManager.UserMappingsReceived(ids, discordIds)`.

## GameUtils time and kick helpers

- **Time formatting:** `WorldTimeToString(worldTime)` (IL=19) is
  `"{day} {hour:D2}:{minute:D2}"` from `WorldTimeToElements`;
  `WorldTimeDeltaToString` (IL=21) is the same with `day - 1` (the
  "time until" display used by horde/event timers).
- **Force disconnect:** `ForceDisconnect()` (IL=9) builds a
  `KickPlayerData(EKickReason 28, 0, DateTime default, "")` and delegates
  to `ForceDisconnect(KickPlayerData)` (IL=6), which starts the
  `ForceDisconnectRoutine(0.5, data)` coroutine - the delayed-kick path
  (the 0.5 s grace before the connection drops).

## TaskManager (the game-code async task layer)

A small scheduling layer on top of `ThreadManager.AddSingleTask`
([loop.md](loop.md)); `GameManager` calls `TaskManager.Init` at startup and
`Destroy` on shutdown. The model:

- **`Schedule(execute, complete)` / `Schedule(group, execute, complete)`
  (IL=16 each):** wrap the two `Action`s in a `TaskManager/Task` (fields
  `Group`, `Execute`, `Complete`), run `OnTaskCreated` (which walks the
  group + parent chain Interlocked-incrementing each `TaskGroup.pending`),
  and post `Execute` to the thread pool via
  `ThreadManager.AddSingleTask(Execute, task, null, false)`.
- **`Execute(TaskInfo)` (IL=17):** the worker entry: invokes `task.Execute`;
  a task with a `Complete` callback is queued into the
  `TaskManager.tasks` `WorkBatch` (drained on the main thread), otherwise
  `OnTaskCompleted` runs immediately.
- **`Update()` (IL=6):** the main-thread drain: `tasks.DoWork(CompleteTask)`.
  `CompleteTask` (IL=9) invokes `Complete` then `OnTaskCompleted`.
- **`WaitOnGroup(group)` (IL=16):** the synchronous barrier: asserts the
  caller is the main thread ("`TaskManager.WaitOnGroup should only be
  called from the main thread.`"), then loops `Update()` + `Thread.Sleep(1)`
  until `TaskGroup.Pending` is false - how startup/shutdown paths wait for
  a scheduled batch to finish.
- **`TaskGroup`:** a parent link + an Interlocked `pending` counter
  (`get_Pending` IL=8 reads it via `CompareExchange`), so `WaitOnGroup` on
  a parent group also covers every child group's tasks.

## ModEvents payload structs (the `S*` data carriers)

`ModEvents` registers each game-event hook with a dedicated payload struct
(namespace `ModEvents/`); every struct is fields + a storing ctor, so the
"payload shape" is the whole contract. The event registry and firing sites
live in [mod-loading.md](mod-loading.md) / [loop.md](loop.md) (field
inventory in [managers.md](managers.md)); the interrupt semantics of the
interruptible pair are in [chat.md](chat.md) §3.

| Struct | Ctor fields | Carried by |
|---|---|---|
| `SChatMessageData` (ctor IL=19) | `ClientInfo`, `ChatType` (`EChatType`), `SenderEntityId`, `Message`, `MainName`, `RecipientEntityIds` (`List<int>`) | `ModEventInterruptible<SChatMessageData>` |
| `SGameMessageData` (ctor IL=13) | `ClientInfo`, `MessageType` (`EnumGameMessages`), `MainName`, `SecondaryName` | `ModEventInterruptible<SGameMessageData>` |
| `SGameStartingData` (ctor IL=4) | `AsServer` (`bool`) | `ModEvent<SGameStartingData>` |
| `SPlayerDisconnectedData` (ctor IL=7) | `ClientInfo`, `GameShuttingDown` (`bool`) | `ModEvent<SPlayerDisconnectedData>` |
| `SSavePlayerDataData` (ctor IL=7) | `ClientInfo`, `PlayerDataFile` | `ModEvent<SSavePlayerDataData>` |
| `SEntityKilledData` (ctor IL=7) | `KilledEntitiy` (sic), `KillingEntity` | `ModEvent<SEntityKilledData>` |

`SNetPackageInfo` (ctor IL=11) is not a ModEvents payload: `Id`, `Size`,
`Tick` (`UInt64`) are the per-package stats record `ConsoleCmdProfileNetwork`
(the `net` console command) reads for the packet histogram.

## Changelog

- **2026-08-08:** Entity.StopAnimatorAudio (IL=16) monitored-handle stop +
  removal.
## Changelog

- **2026-08-08:** Entity.StopOneShot (IL=5) BroadcastStop complement.
## Changelog

- **2026-08-08:** Entity.PlayOneShot (IL=38) dispatch: PlayInsidePlayerHead /
  unique Play with anim-event monitor / BroadcastPlay; EntityPlayer (IL=16)
  spectator skip unless serverSignalOnly.
## Changelog

- **2026-08-08:** BlockRadiusEffect: EntityPlayerLocal.BlockRadiusEffectsTick
  (IL=83) 3-chunk rotating scan + BlockRadiusEffectsApply (IL=58) radiusSq
  buff apply; ResetBiomeWeatherOnDeath (IL=15) weather cvar reset.
## Changelog

- **2026-08-08:** EntityBedrollPositionList leaves: GetData via entity id;
  GetPos sentinel (0, int.MaxValue, 0); Set -> ShowBedrollOnMap; Clear ->
  ClearBedroll; Count 0/1; get_Item ignores idx.
- **2026-08-08:** StreamUtils primitives: ReadVector3/3i/Quaterion
  component-wise LE; Color32 one-u32 RGBA packing (ReadColor32 IL=39,
  WriteColor32 IL=34); null-flagged ReadString IL=8; ReadGuid 16-byte span +
  EndOfStream; 7-bit varint pair; Read/Write Int32 LE + Byte[] ref-offset
  variants; StreamCopy chunked copy + WriteStreamToFile.
- **2026-08-08:** MemoryPools surface: MemoryPooledObject stack free list
  (Alloc IL=33 pop + Activator fallback + IMemoryPoolableObject.Reset,
  AllocSync/FreeSync Monitor locks, Cleanup IL=43, SetCapacity);
  InitStatic IL=45 capacities (PoolChunks 1000, poolCBL/poolCBC 50000,
  poolMS 40, ...); full .cctor set (poolMemoryStream, binary reader/writer,
  MemoryPooledArray family, CBL bit caches, DynamicObjectPool).
- **2026-08-08:** FastTags bitmask: UInt64[] + singleBit fast path; lazy
  per-group bit registry (GetBit IL=56, Interlocked.Increment first-use
  order, tags/bitTags + allInternal growth); Parse comma-split via locked
  scratch; CombineTags 2..5 OR forms; Test_Bit/AllSet/AnySet/IsOnlyBit;
  Remove; GetTagNames/ToString reverse mapping.
- **2026-08-08:** ParticleEffect record: wire layout (Read IL=53 - ParticleId
  = name hash, pos/rot/color32, sound names null-normalized, volumeScale,
  parentEntityId, attachment u8); SpawnParticleEffectServer IL=41 client/
  server split + channel 192 broadcast; SpawnParticleEffect IL=339 audio ->
  AIDirector.OnSoundPlayedAtPosition noise events, dedicated short-circuit,
  4-instance-per-entity cap, origin-relative world spawn; GetParentTransform
  IL=58 head/pelvis attachment resolve.
- **2026-08-08:** StringParsers contract: Parse vs TryParse, substring
  overloads, float default styles 511 vs integer default 7; internalParseBool
  True/False-only (Ordinal/IgnoreCase), internalParseDouble hex rejection,
  float overflow guard ~1e-9 above float.MaxValue; GetSeparatorPositions /
  SeparatorPositions / findOther scanner; vector/quaternion/color/min-max
  table (paren strip, comma counts, defaults); ParseList Func4 splitter.
- **2026-08-08:** DynamicProperties bag: six dicts (Values/Params1/Params2/
  Data/Classes/Array), Parse IL=123 (class recursion, ValidateKey dot ban,
  ^-token ReplaceProperty, name/class collision throw), AddArray IL=70,
  Load IL=37; Get* silent defaults vs Parse* Warning; ParseData/ParseKeyData,
  ParseStringFloatDictWithSubStringKey; CopyFrom/copyKey dotted-path
  exclusions; Clear skips Array; MemoryPack 6-field Deserialize.
- **2026-08-07:** GameRandom Next overloads: Next() InternalSample; Next(max)
  Sample()*max with negative throw; Next(min,max) range check + large-range
  fallback; NextBytes InternalSample()%256.
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
