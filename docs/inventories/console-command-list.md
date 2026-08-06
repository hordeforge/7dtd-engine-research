# Console command catalog (V3.1.0)

**Kind:** per-command behavioral reference (name, permission, function) for every
`ConsoleCmdAbstract` subclass; function text is each command's own `getDescription`.  
**Framework:** dispatch / permissions / telnet in [`../console-commands.md`](../console-commands.md).  
**Regenerate:** `mono tools/bin/CmdMap.exe "$ASM"` emits the `command -> type` mapping (it follows the static-field form, so `exportprefab`, whose name lives in a static `CommandName` field rather than an `ldstr`, is not missed); descriptions and permissions come from each command's `getDescription` / `get_DefaultPermissionLevel`. The **Type** column exists so the coverage tool can see these types: the rows are command *names*, and without the type name all 187 read as undocumented.

Permission: blank = inherits default (0 = highest admin; higher number = less privileged).

**187 commands.**

| Command | Type | Perm | Does |
|---|---|---|---|
| `AccDecay` | `ConsoleCmdAccDecay` |  | Accuracy Decay for guns, show/hide/reset/<Decimal value> |
| `admin` | `ConsoleCmdAdmin` |  | Manage user permission levels |
| `agemap` | `ConsoleCmdSaveChunkAgeMap` |  | Output debug map for chunk age/protection/save status. |
| `ai` | `ConsoleCmdAI` |  | AI commands |
| `aiddebug` | `ConsoleCmdAIDirectorDebug` |  | Toggles AIDirector debug output. |
| `as` | `AdminSpeedConsoleCmd` (alias) |  | (no description) |
| `audio` | `ConsoleCmdAudioManager` |  | Watch audio stats |
| `automation` | `ConsoleCmdAutomation` | 1000 | Automation Script Runner |
| `automove` | `ConsoleCmdAutoMove` |  | Player auto movement |
| `ban` | `ConsoleCmdBan` |  | Manage ban entries |
| `bents` | `ConsoleCmdBents` |  | Switches block entities on/off or counts them |
| `buff` | `ConsoleCmdBuff` |  | Applies a buff to the local player |
| `buffplayer` | `ConsoleCmdBuffPlayer` |  | Apply a buff to a player |
| `camera` | `ConsoleCmdCamera` |  | Lock/unlock camera movement or load/save a specific camera position |
| `ccphysics` | `ConsoleCmdCCPhysics` | 1000 | Enables or disables changes to CCPhysics layer interactions. Reloading the game session may be necessary to fully apply if changed. |
| `challenges` | `ConsoleCmdChallenges` |  | Complete certain challenges |
| `chunkcache` | `ConsoleCmdChunkCache` | 1000 | shows all loaded chunks in cache |
| `chunkobserver` | `ConsoleCmdPlaceObserver` |  | Place a chunk observer on a given position. |
| `chunkreset` | `ConsoleCmdChunkReset` |  | resets the specified chunks |
| `commandpermission` | `ConsoleCmdCommandPermissions` |  | Manage command permission levels |
| `config` | `ConsoleCmdConfig` |  | Import/export config data from/to external file |
| `createwebuser` | `ConsoleCmdCreateWebUser` | 1000 | Create a web dashboard user account |
| `creativemenu` | `ConsoleCmdCreativeMenu` |  | enables/disables the creativemenu |
| `cvar` | `ConsoleCmdCVar` |  | Commands to set, get, track or list CVars. |
| `damagereset` | `ConsoleCmdDamageReset` |  | Reset damage on all blocks in the currently loaded POI |
| `debuff` | `ConsoleCmdDebuff` |  | Removes a buff from the local player |
| `debuffplayer` | `ConsoleCmdDebuffPlayer` |  | Remove a buff from a player |
| `debuggamestats` | `ConsoleCmdDebugGameStats` |  | GameStats commands |
| `debugjiggle` | `ConsoleCmdDebugJiggle` |  | (no description) |
| `debugmenu` | `ConsoleCmdDebugMenu` |  | enables/disables the debugmenu |
| `debugpanels` | `ConsoleCmdDebugPanels` |  | allows usage of debug display panels (F3 menu) via command console |
| `debugshot` | `ConsoleCmdDebugShot` | 1000 | Creates a screenshot with some debug information |
| `debugweather` | `ConsoleCmdDebugWeather` | 1000 | Dumps internal weather state to the console. |
| `decomgr` | `ConsoleCmdDecoMgr` | 1000 | "decomgr": Saves a debug texture visualising the DecoOccupiedMap. "decomgr state": Saves a debug texture visualising the location/state of all of the DecoObjects saved in decorations.7dtd. |
| `discord` | `ConsoleCmdDiscord` |  | Toggle Discord debug window |
| `dms` | `ConsoleCmdDMS` |  | Gives control over Dynamic Music functionality. |
| `dynamicproperties` | `ConsoleCmdDynamicProperties` |  | Dynamic Properties debugging |
| `enablerendering` | `EnableRendering` |  | Disable live map rendering |
| `exhausted` | `ConsoleCmdExhausted` |  | Makes the player exhausted. |
| `expiryinfo` | `ConsoleCmdPrintChunkExpiryInfo` |  | Prints location and expiry day/time for the next [x] chunks set to expire. |
| `exportcurrentconfigs` | `ConsoleCmdExportCurrentConfigs` | 1000 | Exports the current game config XMLs |
| `exportprefab` | `ConsoleCmdExportPrefab` |  | Exports a prefab from a world area |
| `fallingblocks` | `ConsoleCmdFallingBlocks` | 1000 | FallingBlocks WIP Settings |
| `floatingorigin` | `ConsoleCmdFloatingOrigin` |  | (no description) |
| `ForceEventDate` | `ConsoleCmdForceEventDate` |  | Specify date for testing event dates |
| `fov` | `ConsoleCmdFov` |  | Camera field of view |
| `ftw` | `ConsoleCmdLogFellThroughWorldDebugInfo` |  | Log the fell through world debug information for testing purposes. |
| `gamestage` | `ConsoleCmdGameStage` |  | Shows the gamestage of the local player |
| `getgamepref` | `ConsoleCmdGetGamePrefs` | 1000 | Gets game preferences |
| `getgamestat` | `ConsoleCmdGetGameStats` | 1000 | Gets game stats |
| `getlogpath` | `ConsoleCmdGetLogfilePath` | 1000 | Get the path of the logfile the game currently writes to |
| `getoptions` | `ConsoleCmdGetOptions` | 1000 | Gets game options |
| `getsandboxoptions` | `ConsoleCmdGetSandboxOptions` | 1000 | Gets the current game's Sandbox Options |
| `gettime` | `ConsoleCmdGetTime` | 1000 | Get the current game time |
| `gfx` | `ConsoleCmdGfx` | 1000 | Graphics commands |
| `givequest` | `ConsoleCmdGiveQuest` |  | Gives a quest to the player or add to quest tier |
| `giveself` | `ConsoleCmdGiveQualityItem` |  | usage: giveself itemName [qualityLevel= |
| `giveselfxp` | `ConsoleCmdSelfExp` |  | usage: giveselfxp 10000 |
| `givexp` | `ConsoleCmdGiveXp` |  | Give XP to a player |
| `graph` | `ConsoleCmdGraph` | 1000 | Draws graphs on screen |
| `help` | `ConsoleCmdHelp` | 1000 | Help on console and specific commands |
| `invalidatecaches` | `InvalidateCachesCmd` |  | Invalidate contents of web file caches |
| `jds` | `ConsoleCmdServerJunkDrone` |  | Server junk drone commands. |
| `junkDrone` | `ConsoleCmdJunkDrone` |  | Local player junk drone commands. |
| `kick` | `ConsoleCmdKick` |  | Kicks user with optional reason. "kick playername reason" |
| `kickall` | `ConsoleCmdKickAll` |  | Kicks all users with optional reason. "kickall reason" |
| `kill` | `ConsoleCmdKill` |  | Kill a given entity |
| `killall` | `ConsoleCmdKillAll` |  | Kill all entities |
| `lgo` | `ConsoleCmdListGameObjects` |  | List all active game objects |
| `lights` | `ConsoleCmdLights` |  | Light debugging |
| `listdlc` | `ConsoleCmdListDLC` |  | List the available DLC and their current entitlement status. |
| `listents` | `ConsoleCmdListEntities` |  | lists all entities |
| `listplayerids` | `ConsoleCmdListPlayerIds` | 1000 | Lists all players with their IDs for ingame commands |
| `listplayers` | `ConsoleCmdListPlayers` |  | lists all players |
| `listthreads` | `ConsoleCmdListThreads` | 1000 | lists all threads |
| `logenv` | `ConsoleCmdLogEnvironment` |  | Log the process environment variables |
| `loggamestate` | `ConsoleCmdLogGameState` |  | Log the current state of the game |
| `loglevel` | `ConsoleCmdLogLevel` |  | Telnet/Web only: Select which types of log messages are shown |
| `loot` | `ConsoleCmdLoot` | 1000 | Loot commands |
| `mapdata` | `ConsoleCmdMapData` |  | Writes some map data to an image |
| `mem` | `ConsoleCmdMem` |  | Prints memory information and unloads resources or changes garbage collector |
| `memcl` | `ConsoleCmdMemCl` | 1000 | Prints memory information on client and calls garbage collector |
| `memprofile` | `ConsoleCmdMemoryProfiler` |  | Toggles screen Memory Profiler UI |
| `meshdatamanager` | `ConsoleCmdMeshDataManager` | 1000 | Toggle the MeshDataManager |
| `mumblepositionalaudio` | `ConsoleCmdMumblePositionalAudio` |  | Mumble Positional Audio related tools |
| `na` | `ConsoleCmdNewAvatarTest` |  | Test new HD stuff. |
| `networkclient` | `ConsoleCmdNetworkClient` |  | Client side network commands |
| `networkserver` | `ConsoleCmdNetworkServer` |  | Server side network commands |
| `newweathersurvival` | `ConsoleCmdNewWeatherSurvival` |  | Enables/disables new weather survival |
| `occlusion` | `ConsoleCmdOcclusion` |  | Control OcclusionManager |
| `openiddebug` | `EnableOpenIDDebug` |  | enable/disable OpenID debugging |
| `overlap` | `ConsoleCmdOverlapRecovery` |  | Toggle LocalPlayer's Character Controller Overlap Recovery |
| `overridemaxplayercount` | `ConsoleCmdOverrideServerMaxPlayerCount` |  | Override Max Server Player Count |
| `pathtest` | `ConsoleCmdPathTest` |  | enable a path testing utility mode |
| `performanceprofiler` | `ConsoleCmdPerformanceProfiler` | 1000 | Performance Profiling Utility |
| `permissionsallowed` | `ConsoleCmdPermissionsAllowed` |  | Apply a mask to permissions for testing purposes (respects the existing conditions though). |
| `pirs` | `ConsoleCmdPIRS` |  | tbd |
| `placeblockrotations` | `ConsoleCmdPlaceBlockRotations` |  | Places all rotations of the currently held block |
| `placeblockshapes` | `ConsoleCmdPlaceBlockShapes` |  | Places all shapes of the currently held variant helper block |
| `playerOwnedEntities` | `ConsoleCmdLogOwnedEntities` |  | Lists player owned entities. |
| `playervisitmap` | `ConsoleCmdPlayerVisitMap` |  | Teleports the player through a rectangular area with optional memory logging |
| `pois` | `ConsoleCmdPois` |  | Switches distant POIs on/off |
| `poiwaypoints` | `ConsoleCmdPOIWaypoints` |  | Adds waypoints for specified POIs. |
| `pplist` | `ConsoleCmdPPList` |  | Lists all PersistentPlayer data |
| `prefab` | `ConsoleCmdPrefab` |  | Prefab commands |
| `prefabeditor` | `ConsoleCmdPrefabEditor` |  | Open the Prefab Editor |
| `prefabupdater` | `ConsoleCmdPrefabUpdater` |  | (no description) |
| `profilenetwork` | `ConsoleCmdProfileNetwork` |  | Writes network profiling information |
| `profiler` | `ConsoleCmdProfiler` |  | Utilities for collection profiling data from a variety of sources |
| `profiling` | `ConsoleCmdProfiling` |  | Enable Unity profiling for 300 frames |
| `regionreset` | `ConsoleCmdRegionReset` |  | Resets chunks within a target region, or for the entire map. |
| `reloadentityclasses` | `ConsoleCmdReloadEntityClasses` |  | reloads entityclasses xml data. |
| `removequest` | `ConsoleCmdRemoveQuest` |  | usage: removequest questname |
| `rendermap` | `RenderMap` |  | render the current map to a file |
| `repairchunkdensity` | `ConsoleCmdRepairChunkDensity` |  | check and optionally fix densities of a chunk |
| `resetallstats` | `ConsoleCmdResetAchievementStats` |  | Resets all achievement stats (and achievements when parameter is true) |
| `saveworld` | `ConsoleCmdSaveWorld` |  | Saves the world manually. |
| `say` | `ConsoleCmdServerMessage` |  | Sends a message to all connected clients |
| `ScreenEffect` | `ConsoleCmdScreenEffect` |  | Sets a screen effect |
| `sdcs` | `ConsoleCmdSDCS` |  | Control entity sex, race, and variant |
| `sdminfo` | `ConsoleCmdSaveDataManagerInfo` |  | SaveDataManager Information |
| `setgamepref` | `ConsoleCmdSetGamePref` |  | sets a game pref |
| `setgamestat` | `ConsoleCmdSetGameStat` |  | sets a game stat |
| `settargetfps` | `ConsoleCmdSetTargetFps` |  | Set the target FPS the game should run at (upper limit) |
| `settempunit` | `ConsoleCmdSetTempUnit` | 1000 | Set the current temperature units. |
| `settime` | `ConsoleCmdSetTime` |  | Set the current game time |
| `setwatervalue` | `ConsoleCmdSetWaterValue` |  | Sets the water value for all flow-permitting blocks within the current selection area, specified in the range of 0 (empty) to 1 (full). |
| `show` | `ConsoleCmdShow` |  | Shows custom layers of rendering. |
| `showalbedo` | `ConsoleCmdShowAlbedo` |  | enables/disables display of albedo in gBuffer |
| `showchunkdata` | `ConsoleCmdShowChunkData` |  | shows some date of the current chunk |
| `showClouds` | `ConsoleCmdShowClouds` |  | Artist command to show one layer of clouds. |
| `showhits` | `ConsoleCmdShowHits` |  | Show hit entity info |
| `shownexthordetime` | `ConsoleCmdAIDirectorShowNextWanderingHordeTime` |  | Displays the wandering horde time |
| `shownormals` | `ConsoleCmdShowNormals` |  | enables/disables display of normal maps in gBuffer |
| `showspecular` | `ConsoleCmdShowSpecular` |  | enables/disables display of specular values in gBuffer |
| `showswings` | `ConsoleCmdShowSwings` |  | Show melee swing arc rays |
| `showtriggers` | `ConsoleCmdShowTriggers` |  | Sets the visibility of the block triggers. |
| `shutdown` | `ConsoleCmdShutdown` |  | shuts down the game |
| `signeditordebug` | `ConsoleCmdSignEditorDebug` | 1000 | Toggles visibility of the Sign Editor debug panel. |
| `signtexman` | `ConsoleCmdSignTextureManager` | 1000 | Allows enabling/disabling the Sign Texture Manager and configuring various baking settings. |
| `sleep` | `ConsoleCmdSleep` |  | Makes the main thread sleep for the given number of seconds (allows decimals) |
| `sleeper` | `ConsoleCmdSleeper` |  | Drawn or list sleeper info |
| `smoothpoi` | `ConsoleCmdSmoothPOI` |  | Smoothens the POI |
| `smoothworldall` | `ConsoleCmdSmoothWorldAll` |  | Applies some batched smoothing commands. |
| `spawnairdrop` | `ConsoleCmdAIDirectorSpawnAirDrop` |  | Spawns an air drop |
| `spawnentity` | `ConsoleCmdSpawnEntity` |  | spawns an entity |
| `spawnentityat` | `ConsoleCmdSpawnEntityAt` |  | Spawns an entity at a give position |
| `spawnscouts` | `ConsoleCmdAIDirectorSpawnScouts` |  | Spawns zombie scouts |
| `SpawnScreen` | `ConsoleCmdSpawnScreen` |  | Display SpawnScreen |
| `spawnsupplycrate` | `ConsoleCmdAIDirectorSpawnSupplyCrate` |  | Spawns a supply crate where the player is |
| `spawnwandering` | `ConsoleCmdAIDirectorSpawnHorde` |  | Spawn wandering entities |
| `spectator` | `ConsoleCmdSpectatorMode` |  | enables/disables spectator mode |
| `spectrum` | `ConsoleCmdSpectrum` |  | Force a particular lighting spectrum. |
| `squarespiral` | `ConsoleCmdSquareSpiral` |  | Move the player chunk by chunk in a square spiral. Will start off paused and required un-pausing. Also gives god mode and flying at the start. |
| `stab` | `ConsoleCmdStab` |  | stability |
| `starve` | `ConsoleCmdStarve` |  | Makes the player starve (optionally specify the amount of food you want to have in percent). |
| `switchview` | `ConsoleCmdSwitchView` |  | Switch between fpv and tpv |
| `SystemInfo` | `ConsoleCmdSystemInfo` |  | List SystemInfo |
| `teleport` | `ConsoleCmdTeleport` |  | Teleport the local player |
| `teleportplayer` | `ConsoleCmdTeleportPlayer` |  | Teleport a given player |
| `teleportpoirelative` | `ConsoleCmdTeleportPoiRelative` |  | Teleport the local player within the current POI |
| `testCensor` | `ConsoleCmdCensor` |  | Censorship testing toggle. |
| `testDismemberment` | `ConsoleCmdDismemberment` |  | Dismemberment testing toggle. |
| `testloop` | `ConsoleCmdTestLoop` |  | Test code in a loop |
| `testoccreport` | `ConsoleCmdBugReportOcclusionManager` |  | Test the occlusion manager self reporting to backtrace, requires Backtrace to be enabled at build creation |
| `thirsty` | `ConsoleCmdThirsty` |  | Makes the player thirsty (optionally specify the amount of water you want to have in percent). |
| `tppoi` | `ConsoleCmdTeleportPoi` |  | Open POI Teleporter window |
| `traderarea` | `ConsoleCmdTraderArea` |  | ... |
| `transformdebug` | `ConsoleCmdTransformDebug` |  | Transform Debugging |
| `trees` | `ConsoleCmdTrees` |  | Switches trees on/off |
| `twitch` | `ConsoleCmdTwitchCommand` |  | usage: twitch <command> <params> |
| `twitchadmin` | `ConsoleCmdTwitchAdminCommand` |  | Twitch Admin Commands |
| `uioptions` | `ConsoleCmdUIOptions` | 1000 | Allows overriding of some options that control the presentation of the UI |
| `unlock` | `ConsoleCommandUnlockInventories` |  | Force unlock inventories for everyone or a specific player. |
| `version` | `ConsoleCmdVersion` |  | Get the currently running version of the game and loaded mods |
| `versionui` | `ConsoleCmdVersionUi` |  | Toggle version number display |
| `visitmap` | `ConsoleCmdVisitMap` |  | Visit an given area of the map. Optionally run the density check on each visited chunk. |
| `vpois` | `ConsoleCmdVisitPois` |  | (no description) |
| `weather` | `ConsoleCmdWeather` |  | Control weather settings |
| `weathersurvival` | `ConsoleCmdWeatherSurvival` |  | Enables/disables weather survival |
| `webpermission` | `WebPermissionsCmd` |  | Manage web permission levels |
| `webtokens` | `WebTokens` |  | Manage web tokens |
| `whitelist` | `ConsoleCmdWhitelist` |  | Manage whitelist entries |
| `worldchunkreset` | `ConsoleCmdWorldChunkReset` |  | Resets all unprotected chunks across the world. |
| `wsmats` | `ConsoleCmdWorkstationMaterials` |  | Set material counts on workstations. |
| `xui` | `ConsoleCmdXui` |  | Execute XUi operations |
| `zd` | `DynamicMeshDebugConsoleCmd` (alias) |  | (no description) |
| `zz` | `DynamicMeshConsoleCmd` (alias) |  | (no description) |
