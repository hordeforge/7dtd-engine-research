# Console command catalog (V3.0.1)

**Kind:** per-command behavioral reference (name, permission, function) for every
`ConsoleCmdAbstract` subclass; function text is each command's own `getDescription`.  
**Framework:** dispatch / permissions / telnet in [`../console-commands.md`](../console-commands.md).  
**Regenerate:** extract `getCommands`/`getDescription`/`get_DefaultPermissionLevel` per command. Note: `exportprefab` holds its name in a static `CommandName` field (not an `ldstr` in `getCommands`), so a naive `ldstr`-only extractor misses it; it is included here.

Permission: blank = inherits default (0 = highest admin; higher number = less privileged).

**187 commands.**

| Command | Perm | Does |
|---|--:|---|
| `AccDecay` |  | Accuracy Decay for guns, show/hide/reset/<Decimal value> |
| `admin` |  | Manage user permission levels |
| `agemap` |  | Output debug map for chunk age/protection/save status. |
| `ai` |  | AI commands |
| `aiddebug` |  | Toggles AIDirector debug output. |
| `as` |  | (no description) |
| `audio` |  | Watch audio stats |
| `automation` | 1000 | Automation Script Runner |
| `automove` |  | Player auto movement |
| `ban` |  | Manage ban entries |
| `bents` |  | Switches block entities on/off or counts them |
| `buff` |  | Applies a buff to the local player |
| `buffplayer` |  | Apply a buff to a player |
| `camera` |  | Lock/unlock camera movement or load/save a specific camera position |
| `ccphysics` | 1000 | Enables or disables changes to CCPhysics layer interactions. Reloading the game session may be necessary to fully apply if changed. |
| `challenges` |  | Complete certain challenges |
| `chunkcache` | 1000 | shows all loaded chunks in cache |
| `chunkobserver` |  | Place a chunk observer on a given position. |
| `chunkreset` |  | resets the specified chunks |
| `commandpermission` |  | Manage command permission levels |
| `config` |  | Import/export config data from/to external file |
| `createwebuser` | 1000 | Create a web dashboard user account |
| `creativemenu` |  | enables/disables the creativemenu |
| `cvar` |  | Commands to set, get, track or list CVars. |
| `damagereset` |  | Reset damage on all blocks in the currently loaded POI |
| `debuff` |  | Removes a buff from the local player |
| `debuffplayer` |  | Remove a buff from a player |
| `debuggamestats` |  | GameStats commands |
| `debugjiggle` |  | (no description) |
| `debugmenu` |  | enables/disables the debugmenu |
| `debugpanels` |  | allows usage of debug display panels (F3 menu) via command console |
| `debugshot` | 1000 | Creates a screenshot with some debug information |
| `debugweather` | 1000 | Dumps internal weather state to the console. |
| `decomgr` | 1000 | "decomgr": Saves a debug texture visualising the DecoOccupiedMap. "decomgr state": Saves a debug texture visualising the location/state of all of the DecoObjects saved in decorations.7dtd. |
| `discord` |  | Toggle Discord debug window |
| `dms` |  | Gives control over Dynamic Music functionality. |
| `dynamicproperties` |  | Dynamic Properties debugging |
| `enablerendering` |  | Disable live map rendering |
| `exhausted` |  | Makes the player exhausted. |
| `expiryinfo` |  | Prints location and expiry day/time for the next [x] chunks set to expire. |
| `exportcurrentconfigs` | 1000 | Exports the current game config XMLs |
| `exportprefab` |  | Exports a prefab from a world area |
| `fallingblocks` | 1000 | FallingBlocks WIP Settings |
| `floatingorigin` |  | (no description) |
| `ForceEventDate` |  | Specify date for testing event dates |
| `fov` |  | Camera field of view |
| `ftw` |  | Log the fell through world debug information for testing purposes. |
| `gamestage` |  | Shows the gamestage of the local player |
| `getgamepref` | 1000 | Gets game preferences |
| `getgamestat` | 1000 | Gets game stats |
| `getlogpath` | 1000 | Get the path of the logfile the game currently writes to |
| `getoptions` | 1000 | Gets game options |
| `getsandboxoptions` | 1000 | Gets the current game's Sandbox Options |
| `gettime` | 1000 | Get the current game time |
| `gfx` | 1000 | Graphics commands |
| `givequest` |  | Gives a quest to the player or add to quest tier |
| `giveself` |  | usage: giveself itemName [qualityLevel= |
| `giveselfxp` |  | usage: giveselfxp 10000 |
| `givexp` |  | Give XP to a player |
| `graph` | 1000 | Draws graphs on screen |
| `help` | 1000 | Help on console and specific commands |
| `invalidatecaches` |  | Invalidate contents of web file caches |
| `jds` |  | Server junk drone commands. |
| `junkDrone` |  | Local player junk drone commands. |
| `kick` |  | Kicks user with optional reason. "kick playername reason" |
| `kickall` |  | Kicks all users with optional reason. "kickall reason" |
| `kill` |  | Kill a given entity |
| `killall` |  | Kill all entities |
| `lgo` |  | List all active game objects |
| `lights` |  | Light debugging |
| `listdlc` |  | List the available DLC and their current entitlement status. |
| `listents` |  | lists all entities |
| `listplayerids` | 1000 | Lists all players with their IDs for ingame commands |
| `listplayers` |  | lists all players |
| `listthreads` | 1000 | lists all threads |
| `loggamestate` |  | Log the current state of the game |
| `loglevel` |  | Telnet/Web only: Select which types of log messages are shown |
| `loot` | 1000 | Loot commands |
| `mapdata` |  | Writes some map data to an image |
| `mem` |  | Prints memory information and unloads resources or changes garbage collector |
| `memcl` | 1000 | Prints memory information on client and calls garbage collector |
| `memprofile` |  | Toggles screen Memory Profiler UI |
| `meshdatamanager` | 1000 | Toggle the MeshDataManager |
| `mumblepositionalaudio` |  | Mumble Positional Audio related tools |
| `na` |  | Test new HD stuff. |
| `networkclient` |  | Client side network commands |
| `networkserver` |  | Server side network commands |
| `newweathersurvival` |  | Enables/disables new weather survival |
| `occlusion` |  | Control OcclusionManager |
| `openiddebug` |  | enable/disable OpenID debugging |
| `overlap` |  | Toggle LocalPlayer's Character Controller Overlap Recovery |
| `overridemaxplayercount` |  | Override Max Server Player Count |
| `pathtest` |  | enable a path testing utility mode |
| `performanceprofiler` | 1000 | Performance Profiling Utility |
| `permissionsallowed` |  | Apply a mask to permissions for testing purposes (respects the existing conditions though). |
| `pirs` |  | tbd |
| `placeblockrotations` |  | Places all rotations of the currently held block |
| `placeblockshapes` |  | Places all shapes of the currently held variant helper block |
| `playerOwnedEntities` |  | Lists player owned entities. |
| `playervisitmap` |  | Teleports the player through a rectangular area with optional memory logging |
| `pois` |  | Switches distant POIs on/off |
| `poiwaypoints` |  | Adds waypoints for specified POIs. |
| `pplist` |  | Lists all PersistentPlayer data |
| `prefab` |  | Prefab commands |
| `prefabeditor` |  | Open the Prefab Editor |
| `prefabupdater` |  | (no description) |
| `profilenetwork` |  | Writes network profiling information |
| `profiler` |  | Utilities for collection profiling data from a variety of sources |
| `profiling` |  | Enable Unity profiling for 300 frames |
| `regionreset` |  | Resets chunks within a target region, or for the entire map. |
| `reloadentityclasses` |  | reloads entityclasses xml data. |
| `removequest` |  | usage: removequest questname |
| `rendermap` |  | render the current map to a file |
| `repairchunkdensity` |  | check and optionally fix densities of a chunk |
| `resetallstats` |  | Resets all achievement stats (and achievements when parameter is true) |
| `saveworld` |  | Saves the world manually. |
| `say` |  | Sends a message to all connected clients |
| `ScreenEffect` |  | Sets a screen effect |
| `sdcs` |  | Control entity sex, race, and variant |
| `sdminfo` |  | SaveDataManager Information |
| `setgamepref` |  | sets a game pref |
| `setgamestat` |  | sets a game stat |
| `settargetfps` |  | Set the target FPS the game should run at (upper limit) |
| `settempunit` | 1000 | Set the current temperature units. |
| `settime` |  | Set the current game time |
| `setwatervalue` |  | Sets the water value for all flow-permitting blocks within the current selection area, specified in the range of 0 (empty) to 1 (full). |
| `show` |  | Shows custom layers of rendering. |
| `showalbedo` |  | enables/disables display of albedo in gBuffer |
| `showchunkdata` |  | shows some date of the current chunk |
| `showClouds` |  | Artist command to show one layer of clouds. |
| `showhits` |  | Show hit entity info |
| `shownexthordetime` |  | Displays the wandering horde time |
| `shownormals` |  | enables/disables display of normal maps in gBuffer |
| `showspecular` |  | enables/disables display of specular values in gBuffer |
| `showswings` |  | Show melee swing arc rays |
| `showtriggers` |  | Sets the visibility of the block triggers. |
| `shutdown` |  | shuts down the game |
| `signeditordebug` | 1000 | Toggles visibility of the Sign Editor debug panel. |
| `signtexman` | 1000 | Allows enabling/disabling the Sign Texture Manager and configuring various baking settings. |
| `sleep` |  | Makes the main thread sleep for the given number of seconds (allows decimals) |
| `sleeper` |  | Drawn or list sleeper info |
| `smoothpoi` |  | Smoothens the POI |
| `smoothworldall` |  | Applies some batched smoothing commands. |
| `spawnairdrop` |  | Spawns an air drop |
| `spawnentity` |  | spawns an entity |
| `spawnentityat` |  | Spawns an entity at a give position |
| `spawnscouts` |  | Spawns zombie scouts |
| `SpawnScreen` |  | Display SpawnScreen |
| `spawnsupplycrate` |  | Spawns a supply crate where the player is |
| `spawnwandering` |  | Spawn wandering entities |
| `spectator` |  | enables/disables spectator mode |
| `spectrum` |  | Force a particular lighting spectrum. |
| `squarespiral` |  | Move the player chunk by chunk in a square spiral. Will start off paused and required un-pausing. Also gives god mode and flying at the start. |
| `stab` |  | stability |
| `starve` |  | Makes the player starve (optionally specify the amount of food you want to have in percent). |
| `switchview` |  | Switch between fpv and tpv |
| `SystemInfo` |  | List SystemInfo |
| `teleport` |  | Teleport the local player |
| `teleportplayer` |  | Teleport a given player |
| `teleportpoirelative` |  | Teleport the local player within the current POI |
| `testCensor` |  | Censorship testing toggle. |
| `testDismemberment` |  | Dismemberment testing toggle. |
| `testloop` |  | Test code in a loop |
| `testoccreport` |  | Test the occlusion manager self reporting to backtrace, requires Backtrace to be enabled at build creation |
| `thirsty` |  | Makes the player thirsty (optionally specify the amount of water you want to have in percent). |
| `tppoi` |  | Open POI Teleporter window |
| `traderarea` |  | ... |
| `transformdebug` |  | Transform Debugging |
| `trees` |  | Switches trees on/off |
| `twitch` |  | usage: twitch <command> <params> |
| `twitchadmin` |  | Twitch Admin Commands |
| `uioptions` | 1000 | Allows overriding of some options that control the presentation of the UI |
| `unlock` |  | Force unlock inventories for everyone or a specific player. |
| `version` |  | Get the currently running version of the game and loaded mods |
| `versionui` |  | Toggle version number display |
| `visitmap` |  | Visit an given area of the map. Optionally run the density check on each visited chunk. |
| `vpois` |  | (no description) |
| `weather` |  | Control weather settings |
| `weathersurvival` |  | Enables/disables weather survival |
| `webpermission` |  | Manage web permission levels |
| `webtokens` |  | Manage web tokens |
| `whitelist` |  | Manage whitelist entries |
| `worldchunkreset` |  | Resets all unprotected chunks across the world. |
| `wsmats` |  | Set material counts on workstations. |
| `xui` |  | Execute XUi operations |
| `zd` |  | (no description) |
| `zz` |  | (no description) |
