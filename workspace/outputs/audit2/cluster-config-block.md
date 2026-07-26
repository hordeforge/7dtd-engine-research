# Audit: sandbox-options.md / server-browser-prefabs.md / block-shapes.md (stable V3.0.1 IL)

**Verdict:** All three docs are substantially correct against the assembly IL. The sandbox-code codec, every hard count, and the server/client attributions verify exactly. One MAJOR format error (the `.ins` bit-index formula is wrong) and one MAJOR behavioral error (the `getsandboxoptions` bool argument is misdescribed), plus three MINOR inaccuracies. No CRITICAL findings.

All commands below were run from the repo root with
`ASM="/home/maci/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll"`.
`DumpAll.exe "$ASM" <dir>` was used to produce a full per-type IL tree for global greps; two ad-hoc Mono.Cecil scripts (BlobDump / NestedDump, compiled in the session scratchpad against `tools/bin/Mono.Cecil.dll`) decoded static-array init blobs and nested-type method bodies that `DumpMethod.exe` cannot reach.

---

## Findings

### [F1] MAJOR - server-browser-prefabs.md section 3.3 (`PrefabInsideDataFile`): wrong bit-index formula

**Claim:** "A bit-set marking which prefab-local positions are 'inside' the building (index `x + z*size.x + y*size.x*size.z`, one bit each)".

**Ground truth:** `DumpAll` -> `PrefabInsideDataFile.il.txt`, `Add(Int32 x,Int32 y,Int32 z)` (IL=22) and `Contains(Int32 x,Int32 y,Int32 z)` (IL=40) both compute:

```
IL_000A: ldarg.1          // x
IL_000B: ldarg.2          // y
IL_000C..IL_0017: ldflda size; ldfld Vector3i::x; mul   // y * size.x
IL_0018: add
IL_0019: ldarg.3          // z
IL_001A..IL_0031: * size.x; * size.y                    // z * size.x * size.y
IL_0032: add
```

i.e. **`x + y*size.x + z*size.x*size.y`**. The caller `Prefab::IsInsidePrefab(Int32 _x,Int32 _y,Int32 _z)` (Prefab.il.txt IL_0073-IL_007C) passes coordinates in natural x,y,z order (with rotation swizzles that stay semantic), so the doc's formula is not a call-site convention; it is simply wrong. Any external tool implementing the `.ins` layout from this doc would mis-index every bit. The rest of section 3.3 (version byte 2, `int32` count, v1 byte triplets vs v2 raw bit array, the "Probably outdated ins file, please re-save to fix" message) verifies exactly.

**Fix:** change the index expression to `x + y*size.x + z*size.x*size.y`.

### [F2] MAJOR - sandbox-options.md section 8.1 (`getsandboxoptions`): the optional bool argument does NOT route output to the log

**Claim:** "an optional bool argument routes output to the log instead of the console."

**Ground truth:** `DumpAll` -> `ConsoleCmdGetSandboxOptions.il.txt`:

```
// Execute(...):
IL_0013: call StringParsers::ParseBool(...)   // parsed from _params[0]
IL_001C: ldc.i4.s 71
IL_001E: call GameStats::GetString(EnumGameStats)
IL_0023: ldloc.0                              // parsed bool -> _showAll
IL_0024: ldc.i4.1                             // _logToConsole = TRUE, hardcoded
IL_0025: call ConsoleCmdGetSandboxOptions::LogOptions(String,Boolean,Boolean)
```

`LogOptions(String _code, Boolean _showAll, Boolean _logToConsole)`: the bool argument is **`_showAll`** (print all options, not only changed ones); the command always prints to console. `GetHelp` even carries the string `" [show all]"`. The only log-routed call is `GameManager/<startGameCo>d__138::MoveNext -> LogOptions(...)` (found via `FindCallers.exe "$ASM" ConsoleCmdGetSandboxOptions LogOptions`), which is startup logging, not the console command. Everything else in section 8.1 verifies: `getsandboxoptions`/`gso`, permission 1000, description string, reads `GameStats.GetString(71)`, decodes into a scratch preset via `LoadOptionsFromCode(code, preset)`.

**Fix:** "an optional bool argument switches from changed-only to showing all options; output always goes to the console (the log-routing variant of `LogOptions` is only used by `startGameCo` at server start)."

### [F3] MINOR - sandbox-options.md section 8: `GameModeAbstract.Init` does not write `GameStats.SandboxPreset (70)`

**Claim:** "`GameModeAbstract.Init` copies pref 296 into `EnumGameStats.SandboxCode (71)` (with `SandboxPreset = 70` alongside)."

**Ground truth:** `DumpMethod.exe "$ASM" GameModeAbstract Init`: exactly one string stat write,

```
IL_026E: ldc.i4.s 71
IL_0270: ldc.i4 296
IL_0275: call GamePrefs::GetString(EnumGamePrefs)
IL_027A: call GameStats::Set(EnumGameStats,System.String)
```

A whole-assembly grep of the DumpAll tree for `ldc.i4.s 70` preceding `GameStats::Set(EnumGameStats,System.String)` finds writers only in `GameStats.il.txt` (property-table defaults) and `XUiC_ServerInfo.il.txt` (client UI). No code copies pref 295 into stat 70 in `GameModeAbstract.Init`. The stat exists (`EnumGameStats.SandboxPreset=70` per EnumList); the "alongside" copy does not.

**Fix:** drop the parenthetical, or reword to "(`EnumGameStats.SandboxPreset = 70` exists but is not written here)".

### [F4] MINOR - sandbox-options.md section 5: GamePrefs mirror lists seven names for "six values", and `DayNightLength` is not one of them

**Claim:** "the pass also mirrors six values into the legacy `GamePrefs` (`DayNightLength`, `BlockDamagePlayer`, `BlockDamageAI`, `BlockDamageAIBM`, `LootAbundance`, `LootRespawnDays`, `XPMultiplier`)".

**Ground truth:** `DumpMethod.exe "$ASM" SandboxOptionManager UpdateInGameValuesWithSandboxOptions` contains exactly six `GamePrefs::Set` calls (IL_0717-IL_0747), targets 111, 84, 85, 86, 87, 88 = `XPMultiplier`, `BlockDamagePlayer`, `BlockDamageAI`, `BlockDamageAIBM`, `LootAbundance`, `LootRespawnDays` (ids per EnumList). `DayNightLength` is not mirrored into GamePrefs by this pass. (The matching `GameStats::Set` block writes 60/59/73/74/75/76 from the same locals, plus further stats; the not-client gate at IL_0701-IL_0715 verifies.)

**Fix:** remove `DayNightLength` from the list (the count then matches "six").

### [F5] MINOR (polish) - server-browser-prefabs.md section 3.4: `StartAsClient` is not a no-op

**Claim:** "`GameManager.createWorld` calls `StartAsServer()` when `ConnectionManager.IsServer`, else `StartAsClient()` (a no-op)."

**Ground truth:** `PrefabInstanceClientManager::StartAsClient()` (IL=4) executes `clientPrefabs.Clear()`. Trivial, but not a no-op; the branch itself and every `StartAsServer` subscription (decorator `OnPrefabLoaded/Changed/Removed`, `PrefabEditModeManager.OnPrefabChanged`, `GameManager.OnClientSpawned -> sendAllPrefabs`) verify exactly (`_createWorld_d__214.il.txt` IL_0550-IL_056D; `PrefabInstanceClientManager.il.txt`). The headline claim of the section, "server-side despite its name", is **confirmed**.

**Fix:** "(only clears the client-side mirror list)".

### [F6] MINOR (polish) - block-shapes.md section 2: `BlockShapeNew.Rotate` wraps, it does not clamp

**Claim:** "`Rotate` clamps to 0..23".

**Ground truth:** `BlockShapeNew::Rotate(Boolean,Int32)` (IL=21): after +/-1, `>23 -> 0` and `<0 -> 23`. That is a wraparound cycle over 0..23, not a clamp (clamping would pin 24+ at 23). Same section's other claims all verify (see CONFIRMED list).

**Fix:** "wraps within 0..23".

---

## Spot-verified CONFIRMED

### sandbox-options.md

- **152 options, enum 0..151 + `Max=152`:** `EnumList.exe` -> 153 `SandboxOptions.*` members, min `RangedDamage=0`, `Max=152`. (Doc's namespace-qualified name `SandboxOptions.SandboxOptions` dumps as flat `SandboxOptions.<member>`.)
- **74 float / 46 int / 32 bool, 16 `DisabledOptionsOnValue` links, 152 `AddSandboxOption` calls:** `DumpMethod.exe "$ASM" SandboxOptionManager SetupOptions` -> `grep -c` on `newobj SandboxOptionFloat::.ctor` = 74, `SandboxOptionInt` = 46, `SandboxOptionBoolean` = 32, `DisabledOptionsOnValue::.ctor` = 16, `AddSandboxOption` = 152.
- **63 value sets:** same dump, `newobj ...ValueSet*::.ctor` = 2 bool + 23 float + 38 int = 63, all `Dictionary::Add`ed to `ValueSets` inside `SetupOptions` (`InitValueSets` only iterates and calls `Init()`).
- **8 categories:** `ldstr` counts in SetupOptions: General 29, Entities 21, World 23, Resources 25, Crafting 19, Traders 14, Tasks 10, Misc 11 = 152 exactly.
- **No `SandboxOptionString` type:** `MethodList.exe` type census shows only `SandboxOptions.SandboxOption{Float,Int,Boolean}`; `OptionTypes` = {Invalid=0, Int=1, Float=2, String=3, Bool=4} per EnumList, String slot unused. Confirmed as claimed.
- **`DamageValues` array:** Cecil blob decode of `<PrivateImplementationDetails>::D6D7F237...` = `0 0.25 0.35 0.5 0.65 0.75 0.85 1 1.25 1.5 2 2.5 3` - byte-for-byte the doc's list.
- **Membership validation:** `SandboxOptionFloat::SetValue` bails unless `GetFloatIndex(v) != -1`; `SetValueFromIndex` falls back to `DefaultValue` on invalid index (NestedDump of both bodies).
- **Codec (CRITICAL check, passes):** `LoadOptionsFromCode(String)` IL: `ResetAllToDefault()` first; `code[0] != currentVersion -> return false`; `Substring(1)`; `Length/3` groups; per group `Substring(i*3,2)` -> `Alpha2ToIndex` (`(c0-65)*26 + (c1-65)`, "AA"=0), char at `i*3+2` -> `AlphaToIndex` (`c-65`); unknown ids skipped via `SandboxOptionsDict.ContainsKey`; `SetValueFromIndex` applies. `currentVersion` = `ldc.i4.s 65` (`'A'`) in the cctor. `saveOptionsToCode` = version char + `IndexToAlpha2`/`IndexToAlpha` per `PresetValues` entry; `SaveCurrentToPreset` filters on `IsChanged` (only changed options emitted). Stock `serverconfig.xml` line 103 ships `SandboxCode="AAAJABJACJADJARFBNC"` with the Adventurer comment; decoding by the verified algorithm yields exactly six changed options (options 0,1,2,3 -> index 9; 17 -> index 5; 39 -> index 2), matching "six changed options".
- **119 static fields:** `UpdateInGameValuesWithSandboxOptions` has 121 `stsfld` instructions, 119 distinct targets (TraderInfo::VendingResetIntervalInTicks and GlobalResetIntervalInTicks appear twice). `Physics::set_gravity` from `originalGravity` present.
- **GamePrefs bridge:** `GamePrefs::GetInt` IL_0000 = `ldsfld sandboxReferences; ldelem.ref; ... callvirt BaseSandboxOption::GetIntValue()` exactly as quoted. `GameStats::SetupSandboxReferences` special-cases stat 59 -> option 2 (`BlockDamagePlayer` -> `BlockDamage`) and stat 75 -> option 78 (`LootAbundance` -> `GlobalLootCount`); `Enum::TryParse<SandboxOptions>` drives the generic path.
- **Pref/stat ids:** `SandboxPreset=295`, `SandboxCode=296` (EnumGamePrefs); `SandboxPreset=70`, `SandboxCode=71` (EnumGameStats) - all per EnumList.
- **Dedicated flow:** `<StartAsServer>d__166::MoveNext` contains the exact warning string "Sandbox Option Manager not initialized before starting server, ...", `LoadOptionsFromCode(GamePrefs.GetString(296))`, `UpdateInGameValuesWithSandboxOptions`, then `PrepareLocalServerInfo`. `GameModeAbstract.Init` copies pref 296 -> stat 71 (see F3 for the parenthetical). `EntityPlayerLocal::AfterPlayerRespawn` decodes `GameStats.GetString(71)` + runs the update pass (two call sites).
- **Init path:** `FindCallers` shows `GameEntrypoint/<EntrypointCoroutineInternal>d__9` is the sole caller of `SandboxOptionManager::Init` and of `GamePrefs::SetupSandboxReferences`.
- **Overrides:** `SandboxOverridesFromXml.Reload -> CreateOverrides`; the coroutine calls `RemoveOverrides()` then parses `preset` / `sandbox_override` elements -> `AddOverride`. `GetFloat` returns `GetDefaultFloatValue()` when the id is in `overrideList`, 0 on unknown id.
- **Admin surface:** webserver `SandboxSettings.il.txt` (Webserver.WebAPI.APIs.ServerState) has `code`/`onlyChanged`/`detailed` params, defaults to `GameStats.GetString(71)`. Command catalog (`docs/inventories/console-command-list.md` line 66) lists `getsandboxoptions` at permission 1000 - cross-doc consistent.
- **Per-entity slice:** `EntityStats::UpdateSandboxOptions` writes `Stat::GainSandboxModifier`/`LossSandboxModifier`; `EntityPlayer` reads `GetFloat(SandboxOptions)` live in the StartJumpMotion region (EntityPlayer.il.txt line 1744).

### server-browser-prefabs.md

- **Enum counts 20/54/17:** EnumList: `GameInfoString` 20 (all names match the doc's list, ids 0..19), `GameInfoInt` 54 (0..53, `JarRefund=53`), `GameInfoBool` 17 (all listed names present).
- **Searchable arrays 10/45/13 including exact membership:** `GameServerInfo::.cctor` -> `ldc.i4.s 10/45/13` + `newarr`; Cecil blob decode: `SearchableStringInfos` = [5,2,8,12,13,14,16,9,17,19] = LevelName, GameHost, SteamID, Region, Language, UniqueId, CombinedNativeId, ServerVersion, PlayGroup, SandboxCode - exactly the doc's list in order. `BoolInfosInGameTags` = [0,2,3,7,9,10,11,12,1,15,4,5,16] - exactly the doc's 13 in order. `IntInfosInGameTags` 45 entries incl. Port(0), CurrentPlayers(1), MaxPlayers(2), FreePlayerSlots(3), CurrentServerTime(23), WorldSize(46) + the sandbox ruleset.
- **`BuildGameServerInfo` (IL=520 - the doc's IL size matches exactly):** crossplay cap: dedicated + pref 27 -> `ldc.i4.8; GamePrefs.GetInt(26); bge` else warn `CROSSPLAY INCOMPATIBLE VALUE: PLAYER COUNT GREATER THAN MAX OF {0}` (format arg 8); pref 261 (`IgnoreEOSSanctions`) -> second warning; failure -> `CROSSPLAY DISABLED FOR SESSION` + `GamePrefs.Set(27,false)`. EAC: `IsDedicatedServer ? GetBool(109) : GetBool(28)` -> `GameInfoBool 4`. `AllowCrossplay(15)` additionally requires `PermissionsManager::IsCrossplayAllowed()`. `GameType`="7DTD", visibility pref 169 gated by `IsMultiplayerAllowed`, `StockFileHashes::HasStockXMLs` / `ModManager::AnyConfigModActive` for stock flags.
- **Steam:** `<RegisterGame>d__14`: `GameServer::Init(IPAddress.Any, GameInfoInt.Port, GameInfoInt.Port, eServerMode=2, Constants.SteamVersionNr)` - both ports from `GameInfoInt 0` as claimed; `SetDedicatedServer/SetModDir/SetProduct/SetGameDescription/SetMaxPlayerCount/SetPasswordProtected/SetMapName/SetServerName/LogOnAnonymous`; `GetValue(43)==2 -> "Making server public" + SetAdvertiseServerActive(true)`. `MasterServerAnnouncer::Update` pumps `GameServer.RunCallbacks()` and warns above 25 ms (`ElapsedMicroseconds/1000 > 25`); gametags rebuilt via `NetworkUtils::BuildGameTags` on a CountdownTimer -> `SetGameTags`.
- **Gametags encoding:** `BuildGameTags` IL: `Write7BitEncodedSignedInt` per `IntInfosInGameTags` entry in array order, then bools packed `bit |= value << (i % 8)` flushed every 8 (LSB-first), `Convert.ToBase64String`. Exactly as documented.
- **EOS:** `SessionsHost` contains `"GameHost"` session name, pref 272 bucket with `"<WeDontCare>"` fallback and `"CertQA"` special-case, `IAntiCheatServer::ServerEacEnabled()`, `RegisterUser`/`UnregisterUser`; permission mapping IL: visibility 2 -> 0 (`PublicAdvertised`), 1 -> 1, else 1 (`JoinViaPresence`) - matches. `getBoolsString` builds the comma-separated bool attribute.
- **`matchesFilters` absent in stable:** zero hits in the full `MethodList.exe` output and in `SessionsClient.il.txt`. Consistent with experimental-delta.md section 6, which also carries `GetOptionNameValueDictionaryFromPreset` (likewise absent from stable MethodList - that "does not exist in stable" claim checks out too).
- **TCP info port:** `ServerInformationTcpProvider`: `BufferSize` init `ldc.i4 32768`; `TcpListener(IPAddress.Any, GamePrefs.GetInt(18))`; `SendTimeout=50`; `LingerOption`; `GameServerInfo.ToString(true)`; the exact oversize warning string; `ProtocolManager::GetGamePortsString` appends `"/TCP"` to pref 18.
- **`PrefabInstance.Serializable`:** NestedDump: reader/writer = `Int32 id, String prefabName, Vector3i position (StreamUtils), Byte rotation` = 17 bytes + string. Confirmed.
- **Decorator:** created by `ChunkProviderGenerateWorld/<Init>d__22`, `ChunkProviderDisc/<Init>d__11`, `ChunkProviderGenerateFlat/<Init>d__9`; `<Load>d__23` parses `/prefabs.xml`, `y_is_groundlevel`, `PrefabCache::GetPrefabRotated`, `TraderArea::.ctor(Vector3i,Vector3i,Vector3i,PrefabTeleportVolumeList)`; `DecorateChunk` called from `ChunkProviderGenerateWorld`; `NetPackageWorldInitInfoRequest` answers with `EventPrefabs::GetPrefabsSerialized()`.
- **`PrefabInstanceClientManager` is server-side:** `<createWorld>d__214` IL_0550: `ConnectionManager.IsServer ? StartAsServer() : StartAsClient()`; `StartAsServer` subscribes exactly the five events documented; `sendAllPrefabs` walks `DynamicPrefabDecorator::GetWorldPrefabs` and sends `NetPackageEditorPrefabInstance` + `PrefabVolumeListAbs::SendAllVolumesToClient`. Headline claim confirmed (see F5 for the no-op nit).

### block-shapes.md

- **Shape census:** MethodList census: `BlockShape` + exactly 17 `BlockShape*` subclasses, matching the doc's catalog row-for-row. `Block::.ctor` news a `BlockShapeCube` (Block.il.txt IL_0182); `BlocksFromXml` resolves `ldstr "BlockShape"` + `ReflectionHelpers::GetTypeWithPrefix`, default `BlockShapeNew` + `ldstr "@:Shapes/Cube.fbx"`.
- **Rotation bands:** base `BlockShape::RotateY` = `(rotation + n) & 15` (IL: `add; ldc.i4.s 15; and`). `BlockShapeCube::RotateY` wraps within 0..3 / 4..7 / 8..11; `BlockShapeRotatedAbstract::RotateY` adds the 12..15 band (constants 12/15 in the fourth band branch). `BlockShapeNew`: `rotations` is `Byte[3,28]` (cctor `ldc.i4.3; ldc.i4.s 28`), `RotateY` = `rotations[n-1, rotation]` with left = `4 - n`; `CalcRotation` cycles 24..27 for rotation >= 24; `rotationsToQuats` is `Quaternion[32]` (cctor `ldc.i4.s 32; newarr Quaternion`); `convertRotationCached[rotation, face]` field exists and backs `GetRotatedBlockFace`. `BlockShapeModelEntity` calls `BlockShapeNew::GetRotationStatic`. `BlockShapeBillboardPlant::GetRotation` = `AngleAxis(20 * rotation, up)` with `& 3` masking in its Rotate paths. `MirrorY`: base = two `RotateY` calls; MethodList shows exactly one override, `BlockShapeModelEntity::MirrorY`.
- **Collision contract:** `BlockShape::GetStepHeight` = `IsCollideMovement ? 1f : 0f`; `IsMovementBlocked` = `GetStepHeight > 0.5f` (IL literal `ldc.r4 0.5; cgt`). `FindCallers Block IsMovementBlocked` (filtered) = AstarVoxelGrid::CheckHeights/RecalculateCell, EntityMoveHelper::{CheckJumpBlocked,GetExistingDestroyPos,IsABlockSideOpen}, RandomPositionGenerator::{CalcAround,CalcPositionInDirection}, plus World/UAI - the doc's caller list confirmed.
- **BlockFace / flags:** EnumList: `BlockFace` Top=0..East=5, Middle=6, None=255; `BlockFaceFlag` 1/2/4/8/16/32, All=Solid=63, Axials=60. `BlockFaceFlags::RotateFlags` IL: pass-through for mask==0, mask==63, or rotation>23; otherwise per-face `faceRotShiftValues[rotation*6 + face]` signed shift. Exactly as documented.
- **`BlockShapeModelEntity` lifecycle:** `newobj BlockEntityData::.ctor(BlockValue,Vector3i)` -> `Chunk::AddEntityBlockStub`; `Prefab::TransientSleeperBlockIncrement`; `SleeperVolumeToolManager::UnRegisterSleeperBlock`; `GetDamageStateIndex`/`UpdateDamageState` present. `BlockShapeDistantDeco` registers with `DecoManager`. `BlockShapeTerrain` is the only `IsTerrain()` override (MethodList).
- **Trigger chain (all IL-verified):** `Block::HandleTrigger`: `IsClient -> NetPackageBlockTrigger.Setup + SendToServer`, else `Chunk::GetBlockTrigger` -> `TriggerManager::TriggerBlocks(player, player.prefab, trigger)`. `NetPackageBlockTrigger::get_PackageDirection` = `ldc.i4.1` = `NetPackageDirection.ToServer`; `ProcessPackage` re-enters `Block::HandleTrigger` server-side. `TriggerManager::TriggerBlocks` -> `PrefabTriggerData::Trigger`; fan-out iterates `TriggersIndices`, invokes `BlockTrigger::OnTriggered` listeners and `SleeperVolume::OnTriggered`; `UpdateBlocks` -> `WorldBase::SetBlocksRPC` (single batched commit). `TriggerVolume` Touch path calls `TriggerBlocks(...,TriggerVolume)` (TriggerVolume.il.txt line 171).
- **Latch semantics:** `SetTriggeredValueFlag` toggles (Contains -> Remove else Add). `CheckIsTriggered` AND mode: any listened channel absent -> false; OR mode (`UseOrForMultipleTriggers`): returns true as soon as one listened channel is absent - the doc's deliberately-flagged odd semantics reproduce the IL exactly. On fire: `Block::OnTriggered` then `TriggeredValues.Clear()`.
- **Persistence + deferred:** `BlockTrigger::Write` emits `ldc.i4.5` version (writer v5), `Read` gates on `currentVersion >= 5`; `Chunk.il.txt` contains both `BlockTrigger::Read`/`Write` call sites. `PrefabTriggerData` sets `needsTriggerTimer = 3f` (`ldc.r4 3`) and `AddToUpdateList`; `TriggeredStates` = NotTriggered=0 / NeedsTriggered=1 / HasTriggered=2. `World::ResetPOIS` coroutine calls `PrefabInstance::ResetBlocksAndRebuild` and `TriggerManager::RefreshTriggers`; `RefreshTriggersInContainingPoi` referenced from `PrefabInstance` and `QuestGeneratorController`. `MinScript::Tick` calls `TriggerManager::Trigger(EntityPlayer,PrefabInstance,Byte)`.
- **Consumers:** `get_AllowBlockTriggers` base returns `ldc.i4.0`; overrides = BlockActivate, BlockActivateSingle, BlockActivateSwitch, BlockGameEvent, BlockHazard, BlockLight, BlockQuestActivate, BlockTrapDoor, BlockTriggerDowngrade, BlockCompositeTileEntity - the doc's ten, exactly. `BlockActivateSwitch::OnTriggerAddedFromPrefab` sets meta bit 0 only when `HasAnyTriggeredBy()` is false (IL `meta & ~1 | (hasTriggeredBy ? 0 : 1)`), as documented. `GameEvent.SequenceActions.ActionBlockTriggerFall/Mines` exist and are indeed a different system.
- **MeshPurpose:** EnumList = World/Drop/Hold/Local/Preview/SimplifiedCollisionOnly (0..5), matching the doc.

### Cross-doc consistency

- blocks.md rotation bits 16..20 (`0x001F0000`) match block-shapes.md's 0..31 rotation-band model.
- experimental-delta.md section 6 lists `SessionsClient.matchesFilters` and `GetOptionNameValueDictionaryFromPreset` as experimental-only; both are absent from the stable MethodList - the three docs' "experimental-only" cross-references are mutually consistent.
- console-commands.md does not name `getsandboxoptions` in prose, but its command catalog (`inventories/console-command-list.md:66`) carries it at permission 1000 - consistent with sandbox-options.md section 8.1 (modulo finding F2).
- platform-auth.md hand-off points (`GameServerInitialized` gating, EOS identity attributes) match what `<StartAsServer>d__166` and `SessionsHost` actually do.

## Sources

- Local only: the stable dedicated `Assembly-CSharp.dll` at the path above, repo tools (`DumpMethod`, `MethodList`, `EnumList`, `FindCallers`, `DumpAll` + Mono.Cecil), stock `serverconfig.xml` in the dedicated-server install, and the repo docs named per finding. No web sources consulted.
