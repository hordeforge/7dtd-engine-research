# Cluster E audit: server / loop / meta-systems (V3.0.1 dedicated)

**Scope:** docs/server-lifecycle.md, loop.md, loop-gmupdate.md, managers.md,
mod-loading.md, webserver.md, console-commands.md, twitch-integration.md,
parties-factions.md, verified against the stable DLL
(`~/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll`).
All commands below run from repo root with
`ASM="/home/maci/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll"`.

## Verdict

The loop / gmUpdate / managers / parties-factions material is highly accurate
(every checked IL size, constant, enum, and call order matched), but four MAJOR
errors survive in the newer 2026-07-23 docs: a misplaced permission gate in the
console dispatch, a stale console-command count (186 vs 187, `exportprefab`
missing), an EAC boot-gate claim built on strings that only exist in the
client-only gmUpdate UI block, and a mod-load pipeline that misattributes
`InitModCode` (and content patching) to `Mod.LoadMod`.

---

## Findings

### [F1] MAJOR — console-commands.md §2 (+ dispatch diagram): permission check is NOT in `executeCommand`

- **Claim:** "`executeCommand(line, senderInfo)` ... checks the sender's
  permission level against the command's required level, and runs `Execute` only
  if authorized"; state machine has `PermCheck --> Denied: sender level > required`.
- **Ground truth:** `mono tools/bin/DumpMethod.exe "$ASM" SdtdConsole executeCommand`
  (IL=149) contains **no permission lookup**: it tokenizes, calls
  `GetCommand`, checks only `IConsoleCommand::get_CanExecuteForDevice()` and
  `get_AllowedInMainMenu()`, then `IConsoleCommand::Execute(...)`. The actual
  per-command gate for remote players is
  `ConnectionManager::ServerConsoleCommand` (IL=125):
  `AdminTools::CommandAllowedFor(String[],ClientInfo)` →
  `SdtdConsole::ExecuteSync`, else `ldstr "Denying command '{0}' from client {1}"`
  (`DumpMethod.exe "$ASM" ConnectionManager ServerConsoleCommand`). The web path
  checks separately in `Webserver.WebAPI.APIs.Command::HandleRestPost` via
  `AdminCommands::GetCommandPermissionLevel` (Cecil caller scan:
  `mono scratch/Callers.exe "$ASM" AdminTools CommandAllowedFor` →
  only `ConnectionManager::ServerConsoleCommand`). Telnet/stdin connections reach
  `executeCommand` with **no per-command level check** (telnet is password-gated
  only: `TelnetConnection::authenticate`).
- **Fix:** move the permission gate out of the `executeCommand` state machine
  into the per-source layer (ServerConsoleCommand for in-game clients, Command
  API for web); state explicitly that telnet/stdin bypass per-command levels.

### [F2] MAJOR — console-commands.md header/§4/inventory: command count is 187, not 186; `exportprefab` missing

- **Claim:** "the 186-command contract"; "There are 186 concrete commands";
  inventory `docs/inventories/console-command-list.md` says "**186 commands.**"
  for "every ConsoleCmdAbstract subclass".
- **Ground truth:** Cecil subclass census (Mono.Cecil resolve over base chain):
  **189 subclasses, 2 abstract (`ConsoleCmdTeleportsAbs`, `ConsoleCmdTestSystemAbs`), 187 concrete**.
  Name-by-name diff of `getCommands()` ldstr values vs the inventory table shows
  exactly one command absent from the inventory: **`exportprefab`**
  (`ConsoleCmdExportPrefab`; primary name via
  `mono tools/bin/DumpMethod.exe "$ASM" ConsoleCmdExportPrefab .cctor` →
  `ldstr exportprefab`, stored in static `CommandName`, which is why an
  ldstr-in-getCommands extraction pass missed it).
- **Fix:** update all "186" occurrences to 187 and add `exportprefab` to the
  inventory; harden the regen script to resolve `ldsfld String ...::CommandName`.
- Sub-point (MINOR): §4 "plus mod-added ones like the web and optimizer
  commands" — the web commands (`Webserver.Commands.*`, `webtokens`,
  `webpermission`, `invalidatecaches`, `openiddebug`, `createwebuser`) are in
  the **base Assembly-CSharp**, not mod-added.

### [F3] MAJOR — server-lifecycle.md §1: EAC boot gate misattributed; cited strings live in the client-only gmUpdate UI block

- **Claim:** "Before the game starts it checks EAC integrity
  (`eacIntegrityViolation` / `eacUnableToPlayOnProtected`), then creates or
  loads the world"; state machine edge "EacCheck --> Abort: violation ->
  shutdown (eacIntegrityViolation)".
- **Ground truth:** Cecil ldstr scan
  (`mono scratch/FindStr.exe "$ASM" eacIntegrityViolation eacUnableToPlayOnProtected`)
  → both strings appear **only in `GameManager::gmUpdate()`**, at IL_026E /
  IL_029E, i.e. inside the client-only violation-message UI block between
  `IL_01F0: get_IsDedicatedServer / brtrue IL_0337` and IL_0337 — **skipped
  entirely on dedicated**. The boot coroutine
  (`DumpMethod.exe "$ASM" "startGameCo>d__138" MoveNext`, IL=378) checks
  `GameServerInfo::get_EACEnabled()` + `ldstr eacWarning`, then routes to
  `GameManager::StartAsServer`. No integrity-violation abort exists on the
  dedicated boot path in managed IL.
- **Fix:** replace the boot EacCheck/Abort edge with the actual
  `EACEnabled`/`eacWarning` check; move the violation-message strings to a
  client-only note (they are a per-frame gmUpdate UI popup, not a boot gate).

### [F4] MAJOR — mod-loading.md §1: `InitModCode` is not run by `Mod.LoadMod`; content patching is not part of `LoadMods`

- **Claim:** "then `Mod.LoadMod` runs `LoadAssemblies` (load each DLL via
  `loadAssembly`) **and `InitModCode`** ... Content patching (`LoadPatchStuff`,
  `LoadUiAtlases`, `LoadLocalizations`) merges XML, atlases, and localization"
  — diagram flows ASM → INIT → PATCH → DONE per mod inside `LoadMods`.
- **Ground truth:** `mono tools/bin/DumpMethod.exe "$ASM" ModManager ""`:
  `Mod::LoadMod()` (IL=69) calls only `LoadAssemblies` + `DetectContents`;
  `ModManager::LoadMods()` (IL=71) then runs a **second pass**
  (`ldstr "[MODS] Initializing mod code"`, loop `Mod::InitModCode()` at IL_00C7)
  after **all** mods' assemblies are loaded. `LoadPatchStuff` is called from
  `GameManager::Awake()` and `<startGameCo>d__138::MoveNext()` (Cecil caller
  scan), **not** from the LoadMods pipeline at all.
- **Fix:** split the pipeline into (a) per-mod scan+assembly load, (b) global
  InitModCode pass ("all DLLs load before any `InitMod` runs" — this matters
  for cross-mod type references), (c) content patch at game start from
  GameManager, outside LoadMods.
- Confirmed within same doc: EAC gate location is right —
  `Mod::LoadAssemblies` (IL=84) checks `ClientAntiCheatEnabled()` →
  `SkipLoadingWithAntiCheat` → state 3, `AntiCheatCompatible` → state 2, load
  failure → 5 (`DumpMethod.exe "$ASM" Mod LoadAssemblies`).

### [F5] MINOR — webserver.md §6: both non-token console command names are wrong

- **Claim:** commands `webpermissions` and `webcache invalidate`.
- **Ground truth:** `DumpMethod.exe "$ASM" WebPermissionsCmd getCommands` →
  single name `ldstr webpermission` (singular, no alias);
  `DumpMethod.exe "$ASM" InvalidateCachesCmd getCommands` →
  `ldstr invalidatecaches`. The console inventory has the correct names, so
  webserver.md is internally inconsistent with it.
- **Fix:** rename to `webpermission` and `invalidatecaches`.

### [F6] MINOR — webserver.md §3: REST API table is materially incomplete

- **Claim:** table of "Concrete APIs (each an `AbsRestApi`)" lists
  ServerState = ServerStats/SandboxSettings/KeyValueListAbs, WorldState =
  Player, GameData = Item/Mods.
- **Ground truth:** `MethodList.exe` type scan under `Webserver.WebAPI.APIs`:
  ServerState also contains **GamePrefs, GameStats, ServerInfo**; WorldState
  also **Animal, Bloodmoon, Hostile**; GameData also **EntityClass**; plus
  **OpenAPI** (and `LiveData.Animals`/`LiveData.Hostiles` feeding them).
  `KeyValueListAbs` is the abstract base of GamePrefs/GameStats/SandboxSettings,
  not an endpoint.
- **Fix:** regenerate the table from the type list; mark KeyValueListAbs as base.

### [F7] MINOR — webserver.md §1: handler table omits registered handlers and misstates the static mount

- **Claim:** handlers = ApiHandler /api, SessionHandler /session, SseHandler
  /sse, ItemIconHandler /itemicons, "static file / WebMods" at `/`.
- **Ground truth:** `DumpMethod.exe "$ASM" Web RegisterDefaultHandlers` (IL=60)
  registers **RewriteHandler "/" → "/files/"**, **RewriteHandler "/app" →
  "/files/index.html"**, SessionHandler "/session/", **UserStatusHandler
  "/userstatus"**, SseHandler "/sse/", **StaticHandler "/files/"** (DirectAccess
  + SimpleCache), ItemIconHandler "/itemicons/", ApiHandler "/api/". The static
  handler is mounted at `/files/`, reached via rewrites; `/userstatus` is
  missing from the doc.
- **Fix:** add RewriteHandler×2 + UserStatusHandler rows; correct static path.

### [F8] MINOR — parties-factions.md Evidence header: wrong owner cited for the `PartyActions` enum constants

- **Claim:** "enum constants for ... `NetPackagePartyData.PartyActions`" backing
  the §2.2 dispatch table that names entry 6 `JoinAutoParty`.
- **Ground truth:** two distinct nested enums exist (Cecil dump):
  `NetPackagePartyActions/PartyActions` has **JoinAutoParty=6** (this is the one
  `currentOperation` uses and the table matches); `NetPackagePartyData/PartyActions`
  has **AutoJoin=6**. As cited, the evidence enum does not contain the member
  name the table uses.
- **Fix:** cite `NetPackagePartyActions.PartyActions`; note the sibling enum's
  divergent member name.

### [F9] MINOR — managers.md §1: `EntityAsyncManager` listed in the "gmUpdate manager chain" table

- **Claim:** table titled "gmUpdate manager chain" (phase B, null-checked chain)
  includes `EntityAsyncManager | 22`.
- **Ground truth:** full gmUpdate dump (`DumpMethod.exe "$ASM" GameManager gmUpdate`):
  `EntityAsyncManager::Update()` is called **after** the game-started gate
  (pre-sim phase F, immediately before `GameTimer::updateTimer`), not in the
  phase-B chain — loop-gmupdate.md §2 Phase F places it correctly, so the two
  docs disagree.
- **Fix:** footnote it as phase-F, or move to a separate row group.

### Unverifiable within this audit (flagged, not graded)

- loop.md §3 "Measured confirmation (2026-07-21)" (20 Hz vs frame-rate
  independence, LiteNetLib thread pacing percentages) cites live measurements in
  `7dtd-optimizer/docs/RESULTS.md` §3k — file exists but the runtime numbers
  cannot be checked from IL. The static side (20 Hz constant, slice/flush
  structure) is confirmed below.
- webserver.md "413 methods": 72 top-level `Webserver.*` types confirmed
  exactly (Cecil census: all=87, named=82, topLevel=72); method count lands
  412–433 depending on nested/compiler-generated counting convention — treated
  as consistent, exact convention undocumented.
- twitch-integration.md §2 vote-window mechanics (client-side
  `TwitchVotingManager` behavior) — server-side package and gate verified; the
  client-hosted vote flow is out of dedicated IL scope as the doc itself states.

---

## Spot-verified CONFIRMED

Loop core (`mono tools/bin/DumpMethod.exe "$ASM" <Type> <Method>` unless noted):

- `GameManager::gmUpdate` **IL=631**, **14 locals, 1 exception handler**
  (Cecil MethInfo), **6×** `get_IsDedicatedServer`, **182 call instructions**
  (matches `inventories/gmupdate-calls.md`, last call IL_0843
  `GameObjectPool::FrameUpdate`); dedicated skip `IL_01F0 brtrue IL_0337`;
  destroy queue under `Monitor.Enter/Exit`; game-started gate →
  `GameTimer::Reset` + ret; phase order incl. `updateTimer(bool)` fed by
  IsDedicatedServer + player count, `UpdateTick`, `CopyChunksToUnity` inside
  dedicated-skipped branch, `ConsoleCmdMem.GetStats`, `SaveWorldState` /
  `NameIdMapping.SaveIfDirty` / `EventPrefabs.Save`,
  `NetPackagePersistentPlayerPositions`, dedicated `GC::Collect()`,
  `SGameUpdateData.Invoke` epilogue. Phase-B manager order matches both docs
  exactly (Quest → Trigger → TwitchVoteScheduler → TwitchManager → GameEvent →
  Power → Party → Vehicle → Drone → Dismemberment → TurretTracker → RaycastPath
  → Token → TrajectorySimulation → Faction → NavObject → BlockedPlayerList →
  PrefabEditMode → TriggerEffect → SpeedTree → `ThreadManager::UpdateMainThreadTasks`).
- `GameManager`: `Update` IL=3, `UpdateTick` IL=150 (returns `Boolean` — the
  documented abort), `FixedUpdate` IL=5, `LateUpdate` IL=18
  (`ThreadManager.LateUpdate` + `MeshDataManager.LateUpdate`).
- `UpdateTick` ordered body matches §3.1 exactly: slice-only branch
  (`TickEntitiesSlice` when timer not ready ∧ players>0) vs full tick
  (`TickEntitiesFlush` → `World.OnUpdateTick` → `GameStateManager.OnUpdateTick`
  (server) → `TickEntities` → `LetBlocksFall` → not-dedicated
  `SetEntitiesVisibleNearToLocalPlayer` → server `NetEntityDistribution.OnUpdateEntities`
  → `SendChunksToClients` → `MainThreadCacheProtectedPositions` /
  `SaveRandomChunks` / `SaveDecorations` / `EventPrefabs.Save` → rich presence).
- **GameTimer 20 Hz:** `DumpMethod.exe "$ASM" GameTimer get_Instance` →
  `ldc.r4 20` → `.ctor(Single)` → `ticksPerSecond`.
- `World::OnUpdateTick` IL=189; always-path (WaterSplashCubes, DecoManager,
  MultiBlockManager, DynamicMusic.Conductor non-editor, POI uncull), `IsServer`
  gate, `WorldBlockTicker::Tick`, **`ldc.i4.s 20` + `rem.un`** area-master spawn
  cadence, `SpawnManagerAbstract::Update`, `AIDirector::Tick`,
  `TickSleeperVolumes` last.
- Entity pipeline: `TickEntities` IL=117 (EMA `ldc.r4 0.8`/`0.2`, base
  `ldc.i4.s 25`), `TickEntitiesSlice()` IL=5 / `(Int32)` IL=37,
  `TickEntitiesFlush` IL=6, `TickEntity` IL=148, `EntityActivityUpdate` IL=229
  with **64→1.0, 225→0.3, else 0.1** and cloth **625/3025** (all `ldc.r4`
  present); `EntityAlive::OnUpdateEntity` 417, `OnUpdateLive` 363,
  `updateTasks` 125, `EntityMoveHelper::UpdateMoveHelper` 1236,
  `EAITaskList::OnUpdateTasks` `ldc.r4 0.05` ×2,
  `EAIApproachAndAttackTarget::Update` has exactly 3 `FindPath` call sites,
  `EntityAlive::FindPath` `ldc.r4 1225`, ASP drain budget `ldc.i4.8` in
  `<FindPaths>d__8::MoveNext`.
- Peers: `ConnectionManager::Update` IL=215 (ProtocolManager.Update,
  per-client kick + `ProcessPackages` ×2 + `FlushClientSendQueues`,
  `UpdatePings`), `LateUpdate` IL=4 → `ProtocolManager::LateUpdate`;
  `DynamicMeshManager::Update` IL=404; `SdtdConsole::Update` IL=60;
  `Origin::FixedUpdate` IL=256 with `IsDedicatedServer → brtrue IL_0018: ret`;
  `WorldEnvironment::Update` IL=83; `ProtocolManager::Update` IL=35;
  `LoadManager::Update` IL=56; `AstarManager::UpdateGraphs` IL=185.
- Subsystem IL table (loop.md §4–12): `SpawnManagerBiomes::SpawnUpdate` 441,
  `SleeperVolume::Tick` 137, `UpdatePlayerTouched` 172, `CheckTouching` 165,
  `AIDirectorBloodMoonComponent::Tick` 170, `AIDirector::ComponentsTick` 21,
  `NetEntityDistribution::OnUpdateEntities` 322,
  `NetEntityDistributionEntry::updatePlayerList` 509 / `updatePlayerEntity` 222,
  `ChunkManager::DetermineChunksToLoad` 448 / `SendChunksToClients` 216 /
  `doCopyChunksToUnity` 252, `ChunkProviderGenerateWorld::SaveRandomChunks` 99,
  `DynamicMeshServer::Update` 452, `MeshDataManager::LateUpdate` 5,
  `DecoManager::UpdateTick` 330, `WaterSplashCubes::Update` 185,
  `MultiBlockManager::MainThreadUpdate` 5, `WorldBlockTicker::tickScheduled` 151
  / `tickRandom` 97, `WorldState::SaveLoad(Stream,…)` 884,
  `SkyManager::Update` 456, `GameLightManager::UpdateLightFrameUpdate` 159,
  falling blocks `AddFallingBlock` 38 / `GroupFallingBlocks` 292 /
  `LetBlocksFall` 220 / `EntityFallingBlock(s)::OnUpdateEntity` 344/302.
- Net thresholds (loop.md §6.2): `updatePlayerList` constants `ldc.r4 16`,
  `ldc.r4 2`, `±256`, `128/-128`, `ldc.i4.s 100`, `ldc.r4 0.04` all present.
- `AIDirector::CreateComponents` install order exactly Marker → Player →
  WanderingHorde → AirDrop → ChunkEvent → BloodMoon.
- Managers table (managers.md §1), every value re-dumped: TwitchManager
  **1585** (`Twitch.TwitchManager::Update(Single)`), Drone 305, Vehicle 297,
  TriggerEffect 216, QuestEvent 127, Token 121, Power 106, Dismemberment 60,
  BlockedPlayerList 59, TurretTracker 45, Faction 43, NavObject 42,
  GameEventManager 25 (`Update(Single)`), Trigger 23, EntityAsync 22,
  RaycastPath 5, PartyManager 4 (body = `PartyVoice::Update()` only),
  `ThreadManager::UpdateMainThreadTasks` 64.
- **ModEvents fields** (managers.md §2): `DumpType.exe` → exactly the 22
  documented fields; interruptible set = {MainMenuOpening, PlayerLogin,
  GameMessage, ChatMessage} as documented.
- **Enums** (`EnumList.exe "$ASM" scratch/enums.txt`): `EModLoadState`
  0–6 exactly as tabled; `EKickReason` 0–29 present; `EChatType.Party=2`;
  `EnumGameStats.PartySharedKillRange=54`, `AutoParty=56`;
  `Relationship` Hate 0 / Dislike 200 / Neutral 400 / Like 600 / Love 800 /
  Leader 1001; `AllyStatus` 0–3 and `AllyEvent` 0–10 exactly as documented;
  `NetPackagePartyActions/PartyActions` 0–7 with JoinAutoParty=6.
- Parties: `Party::IsFull` `Count == 8`; `AddPlayer` `ldc.i4.8`;
  `GetPartyXP` = `startingXP * (1 - 0.1 * MemberCountInRange)` (IL=15, exact);
  `MemberCountInRange` uses `ldc.i4.s 54` GameStats range and skips self;
  `PartyManager::CreateParty` IsServer-gated + `++nextPartyID`;
  `ServerHandleAutoJoinParty` → `GetParty(1)`; `RemovePlayer` single-member
  auto-remove with `ldc.i4.s 56` AutoParty exception;
  `PlayerMoveController::updateRespawn` `ldc.i4.s 56` → ServerHandleAutoJoinParty;
  `NetPackagePartyActions::ProcessPackage` `switch` 8 targets, **9×** IsServer;
  wire layouts of `NetPackagePartyActions::write` (op u8, 2×i32, string),
  `NetPackagePartyData::write` (i32, byte-narrowed LeaderIndex, string, count +
  members, changedEntityID, action u8, bool; `get_PackageDirection`→2;
  `ProcessPackage` returns on server), `NetPackageSharedPartyKill` (4×i32;
  server → `SharedKillServer(.., 1.0)`) all match field-for-field. Body counts
  PartyManager 9 / Party 38 / FactionManager 19 / Faction 9 / AllyStore 20 /
  PartyQuests 18 exact (`MethodList.exe` grep).
- Factions: `FactionManager::.ctor` `newarr Faction[255]`; `Faction::.ctor`
  `float[255]` init `ldc.r4 400`; `AddFaction` start indices `ldc.i4.0` /
  `ldc.i4.8`; `GetRelationshipValue` null→400, same-faction→800;
  `GetRelationshipTier` thresholds 200/400/600/800/1001;
  `ModifyRelationship` clamp 0..1000 with 255 sentinel; `Update` IsServer +
  IsGameStarted + `ldc.r4 60` save timer; `Save` → thread `factionDataSave`,
  `factions.dat` + `.bak`; `Load` falls back to `.bak`.
- Allies: `AllyStore` full method set incl. `ComputeTransition(AllyStatus,
  Boolean, AllyStatus&, AllyEvent&, AllyEvent&)`; `SetStatus` writes mirrored
  pairs (1/1, 2/3); `NetPackageAllyRequest::write` = source/target ToStream +
  bool, `ProcessPackage` → `ProcessAllyRequest`; `NetPackageAllyResponse::write`
  = ids + newStatus + two AllyEvents.
- Lifecycle: `StartGame(Boolean)` → `startGameCo` → `StartAsServer` →
  `GameStateManager::InitGame` + `createWorld(...)` (coroutine dumps);
  `GameStateManager` members (`InitGame`, `OnUpdateTick`, `nextRound`,
  `SetBloodMoonDay`, `IsGameStarted`, `GetGameMode`, `GetModeName`) and all 8
  documented `GameMode*` classes + `GameMode::InitGameModeDict` /
  `GetGameModeForId/Name`, `GameModeAbstract::Init/ResetGamePrefs` exist;
  `PlayerSpawnedInWorld(ClientInfo, RespawnType, Vector3i, Int32)`;
  `PlayerDataFile` Load/Save/Read/Write/ToPlayer/FromPlayer/WriteNetwork/
  ReadNetwork with `.bak` rollback strings; `PersistentPlayerList` land-claim
  quartet; `SaveAndCleanupWorld` calls `PlayerInputRecordingSystem::AutoSave`,
  `QuestEventManager::HandleAllPlayersDisconnect`, `SaveWorld`; reached from
  `OnApplicationQuit` → `ApplicationQuitCo` → `Disconnect`/`StopServers`
  (Cecil caller scan: `ConnectionManager::StopServers` /
  `DisconnectFromServer` are the callers); `IsStartingGame` /
  `waitForGameStart` / `OnWorldChanged` event exist.
- Mod loading: `ModManager` LoadMods/loadModsFromFolder/GetLoadedMods/
  GetLoadedAssemblies/GetModForAssembly/GetFailedMods/GameEnded and `Mod`
  LoadDefinitionFromFolder/LoadMod/LoadAssemblies/loadAssembly/InitModCode all
  exist; `loadModsFromFolder` = scan sorted dirs → `LoadDefinitionFromFolder` →
  `LoadMod`; `InitModCode` reflects `IModApi` over `Assembly::GetTypes()` and
  calls `InitMod(Mod)`; EAC gate in `LoadAssemblies` maps to states 2/3/5
  exactly as the EModLoadState table says.
- Webserver: 72 top-level `Webserver.*` types (Cecil census);
  `Web::HandleRequest` IL=139 re-arms `BeginGetContext` first, `503` before
  auth, `DoAuthentication(request, WebConnection&)`, `ldstr sid` cookie with
  path `/`, `/app` redirect, `400`, `ApplyPathHandler`;
  `ApplyPathHandler` → `IsAuthorizedForHandler` → `403`; `ApiHandler
  ::HandleRequest` 403/500; reflection discovery via `apiFoundCallback`;
  `ConnectionHandler::IsLoggedIn(String, IPAddress)` and
  `LogIn(IPAddress, String, PlatformUserIdentifierAbs, PlatformUserIdentifierAbs)`
  match the documented session/IP binding; `SessionHandler` HandleUserPassLogin /
  HandleSteamLogin / HandleSteamVerification / HandleUserIdLogin / HandleLogout;
  `OpenID` fields = `Regex steamIdUrlMatcher` + pinned `caCert` /
  `caIntermediateCert` X509Certificate2, `Validate(HttpListenerRequest)` +
  `GetOpenIdLoginUrl`; `SseHandler` `ldstr events`, 400 paths,
  `AbsEvent::AddListener(SseClient)`, `QueueProcessThread` + `SignalSendQueue`,
  `Shutdown`; `Web` has exactly 3 CustomSamplers (auth/cookie/handler),
  `ServerInitialized`, `SendLog`, `LogBuffer`; `WebCommandResult` and
  `WebConnection` (IConsoleConnection surface: SendLine/SendLines/GetDescription)
  exist.
- Console/telnet: `SdtdConsole` RegisterCommands (reflection over
  `IConsoleCommand` via `ReflectionHelpers::FindTypesImplementingBase`),
  RegisterCommand into `SortedList<String,IConsoleCommand>`, ExecuteAsync/
  ExecuteSync/executeCommand/tokenizeCommand/RegisterServer/Output;
  `AdminCommands::IsPermissionDefined` + `GetCommandPermissionLevel` exist;
  telnet: `TelnetConnection` HandlerThread/handleReading/submitInput
  (`ldstr exit` → close, else `SdtdConsole::ExecuteAsync`), `authenticate` with
  `TelnetConsole::RegisterFailedLogin`, strings "Please enter password:",
  "Password incorrect, please enter password:", "Too many failed login
  attempts!", "Logon successful." all present.
- Twitch: **117 top-level `Twitch.*` types** (Cecil census, matches doc);
  `TwitchIRCClient`, `Twitch.PubSub.TwitchPubSub`, `TwitchAuthentication`,
  `ExtensionManager`/`ExtensionListener`/`ExtensionCommandPoller`,
  `TwitchVotingManager`, `TwitchActionsFromXml` all exist; gmUpdate calls
  `TwitchVoteScheduler::Update(deltaTime)` then
  `TwitchManager::Update(unscaledDeltaTime)`;
  `NetPackageTwitchVoteScheduling::ProcessPackage` gates on `IsServer`;
  `NetPackageGameEventRequest::ProcessPackage` → `GameEventManager::HandleAction`.

## Sources

- Ground-truth DLL: `/home/maci/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll` (V3.0.1 stable, 2025-07-17 build)
- Repo toolkit: `tools/bin/DumpMethod.exe`, `DumpType.exe`, `EnumList.exe`, `MethodList.exe` (+ ad-hoc Mono.Cecil scanners in session scratchpad: subclass census, ldstr locator, caller scan, method-body stats)
- Audited docs: `docs/server-lifecycle.md`, `docs/loop.md`, `docs/loop-gmupdate.md`, `docs/managers.md`, `docs/mod-loading.md`, `docs/webserver.md`, `docs/console-commands.md`, `docs/twitch-integration.md`, `docs/parties-factions.md`, `docs/inventories/console-command-list.md`, `docs/inventories/gmupdate-calls.md`
