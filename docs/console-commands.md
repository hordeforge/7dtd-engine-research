# Console and telnet command system (dedicated V3.1.0)

**Owns:** the server admin command surface: `SdtdConsole` (command registry +
dispatch), `ConsoleCmdAbstract` (the 187-command contract), the connection sources
(`TelnetConnection`, in-game console, and `WebConnection` from the web server), and
the permission gate.
**Not:** each command's own effect (187 leaf commands, content/feature specific);
the telnet TCP socket internals (native).
**Evidence:** `SdtdConsole`, `ConsoleCmdAbstract`, `ConsoleConnectionAbstract`,
`TelnetConnection` IL (dump locally with `tools/src/DumpMethod`, git-ignored).
**Hub:** [`INDEX.md`](INDEX.md). **Method:** [`re-methodology.md`](re-methodology.md).

The console is the primary way to administer a headless server (stdin, telnet, or
the web dashboard's Command API (`Webserver.WebAPI.APIs.Command`;
[webserver.md](webserver.md) section 6.0), so it is a core dedicated codepath.

---

## 1. Architecture

`SdtdConsole` is a singleton MonoBehaviour. At startup `RegisterCommands`
**reflection-discovers** every `IConsoleCommand` (i.e. `ConsoleCmdAbstract`
subclass) and registers each of its name aliases into a `SortedList<name, command>`
via `RegisterCommand`. A command's required access is its explicit entry in
`AdminCommands` (permissions) or, failing that, its `DefaultPermissionLevel`.

Multiple **connection sources** feed the same dispatcher (all implement
`IConsoleConnection` / extend `ConsoleConnectionAbstract`):

```mermaid
flowchart LR
  STDIN[Dedicated stdin] --> EX[SdtdConsole.ExecuteAsync / ExecuteSync]
  TEL[TelnetConnection] --> EX
  WEB[WebConnection -> Command API] --> EX
  GUI[GUIWindowConsole in-game] --> EX
  EX --> EC[executeCommand]
  EC --> OUT[Output -> back to the origin connection + LogCallback fan-out]
```

`RegisterServer(IConsoleServer)` lets the dedicated/telnet server attach; `Output`
+ `LogCallback` fan command results and log lines back to connected clients.

**`Update` pump (IL=60):** each frame, when `m_commandsToExecuteAsync` is
non-empty, executes **exactly one** queued async command under the list's
`Monitor` lock: builds a `CommandSenderInfo` (`IsLocalGame=false`,
`NetworkConnection = entry.sender`), runs
`executeCommand(command, senderInfo)` (exceptions logged via `Log.Exception`),
sends the result lines back through `entry.sender.SendLines`, and removes the
entry (`RemoveAt(0)`) - a FIFO one-per-frame drain, so N queued commands take N
frames on the main thread.

---

## 2. Command dispatch (state machine)

`ExecuteAsync`/`ExecuteSync` funnel into `executeCommand(line, senderInfo)`, which
tokenizes the line (quote-aware, `tokenizeCommand`), looks up the command by its
first token, gates on `CanExecuteForDevice` / `AllowedInMainMenu`, and runs
`Execute`. **`executeCommand` (IL=149) does not check the permission level** (it
has only the device/main-menu gates). The **per-command permission check lives
upstream** of it, at the trust boundary:

- **Networked client commands** go through
  `ConnectionManager.ServerConsoleCommand(cInfo, cmd)` (**IL=125**):
  1. If `cmd.Length > 300`: log warning (length + first 20 chars) and **return**
     (no package reply).
  2. Resolve command via `SdtdConsole.GetCommand`.
  3. If missing / `!CanExecuteForDevice`: reply `NetPackageConsoleCmdClient` error
     (`Unknown command` / device message).
  4. **`AdminTools.CommandAllowedFor(cmdNames, clientInfo)`** gate (null
     `adminTools` treated as deny).
  5. If `IsExecuteOnClient`: log and send command line back to client for local
     execute (`NetPackageConsoleCmdClient` with execute flag).
  6. Else `SdtdConsole.ExecuteSync(cmd, clientInfo)` and send output lines package.
  7. Denied: localized `msgServer25` permission error package.

`NetPackageConsoleCmdClient.ProcessPackage` (IL=19) is the client-side
executor: with the execute flag it runs `SdtdConsole.ExecuteSync(lines[0],
sender)` (the server-gated command re-executed locally, e.g. a UI command)
and shows the result via `GUIWindowConsole.AddLines`; without the flag it
just appends the carried output lines - the two halves of the round-trip.
  The web Command API applies the same `CommandAllowedFor` gate.
- **Telnet / stdin / dedicated-console input** call `executeCommand` directly and
  therefore **bypass per-command permission levels** (they are already a trusted
  local operator channel).

```mermaid
stateDiagram-v2
  [*] --> Source
  Source --> PermCheck: networked client (ServerConsoleCommand) / web API
  Source --> Received: telnet / stdin / local console (no per-command level check)
  PermCheck --> Denied: AdminTools.CommandAllowedFor false
  PermCheck --> Received: allowed
  Received --> Tokenized: tokenizeCommand (quote-aware split)
  Tokenized --> Empty: no tokens -> ignore
  Tokenized --> Lookup: GetCommand(name)
  Lookup --> NotFound: unknown -> "unknown command" output
  Lookup --> DeviceGate: command found
  DeviceGate --> Blocked: CanExecuteForDevice / AllowedInMainMenu false
  DeviceGate --> Running: gates pass
  Running --> Output: command.Execute(params, senderInfo)
  Running --> Errored: Execute throws -> logged
  Output --> [*]
  Denied --> [*]
  Blocked --> [*]
  NotFound --> [*]
  Empty --> [*]
```

**Permission levels** follow the 7DTD admin convention (lower number = more
privileged; 0 is highest). `AdminCommands.IsPermissionDefined` decides whether a
command has an explicit level; otherwise its `DefaultPermissionLevel` applies. The
level is enforced by `AdminTools.CommandAllowedFor` on the networked/web path, not
inside `executeCommand`.

**`CommandAllowedFor` (IL=12):**  
`allowed = !(GetCommandPermissionLevel(cmdNames) < GetUserPermissionLevel(client))`  
i.e. user level must be **≤** command required level (lower/equal is more
privileged). `IsExecuteOnClient`, `AllowedInMainMenu`, and `AllowedDeviceTypes`
gate **where** a command may run (device/menu), independently of **who** may run it.

### 2.1 High-value admin `Execute` leaves (IL re-pin 2026-08-07)

Catalog of all names: [inventories/console-command-list.md](inventories/console-command-list.md).
Selected dedi-critical Execute bodies:

| Command type | Execute IL | Behaviour |
|---|---:|---|
| `ConsoleCmdKillAll` | 92 | Optional `alive` / `all` filters; walk world entities; `Entity.DamageEntity` with large strength; log damage lines |
| `ConsoleCmdSpawnEntity` | 280 | Lists players/entity numbers when short args; otherwise builds spawn near player/pos via entity class lookup (large help/list branch) |
| `ConsoleCmdTeleport` | 141 | **Client-only** for local player (`"use teleportplayer instead"` on remote); offset/player destination via `ConsoleCmdTeleportsAbs.ExecuteTeleport` |
| `ConsoleCmdSetTime` | 145 | `day` / `night` presets via `GameUtils.DayTimeToWorldTime`, or raw u64 parse; multi-arg day/hour/min variants |
| `ConsoleCmdSaveWorld` | 12 | If server: `SaveLocalPlayerData` + `SaveWorld`; output `World saved` |
| `ConsoleCmdShutdown` | 5 | Output `Shutting server down...` then `Application.Quit()` |
| `ConsoleCmdMem` | 480 | Subcommands: `gc` (GC stats / incremental collector), editor/mem dump branches (large) |
| `ConsoleCmdWeather` | 465 | Dumps biome weather / WeatherManager state; mutator subcommands for weather params |
| `ConsoleCmdGetGamePrefs` | 73 | Optional filter string; lists allowed prefs `GamePref.X = value` via `prefAccessAllowed` |
| `ConsoleCmdSetGamePref` | 58 | `GamePrefs.Parse` + `SetObject`; errors on bad pref/value |
| `ConsoleCmdCreateWebUser` | 96 | In-game console only; server builds registration token/URL for web dashboard user |
| `ConsoleCmdLogGameState` | 97 | 1-2 args; optional bool; client restriction on second param |
| `ConsoleCmdAdmin` | 70 | `add` / `remove` / `addgroup` / `removegroup` / `list` on `AdminTools.Users`: `ExecuteAdd` parses name/id via `ConsoleHelper.ParseParamPartialNameOrId` + int level -> `AdminUsers.AddUser(name, id, level)`; `ExecuteAddGroup` -> `AdminUsers.AddGroup(name, groupId, regularLevel, moderatorLevel)`; `ExecuteList` prints the `Defined User/Group Permissions:` tables |
| `ConsoleCmdWhitelist` | 70 | Same subcommand shape on `AdminTools.Whitelist` (`AdminWhitelist`): `ExecuteAdd` resolves an entity id / player name / user id (`" is not a valid entity id, player name or user id."`), group variant validates the steam group id |
| `ConsoleCmdPermissionsAllowed` | 134 | `i/info` / `g/grant` / `rev/revoke` / `res/resolve` subcommands over the permission table (span-based dispatch, `Unknown sub-command:` fallback) |
| `ConsoleCmdCVar` | 65 | `get` / `set` / `track` / `list` subcommands; `ExecuteGet` resolves the player by id (`Could not find player matching ID {0}.`) and reads a CVar |
| `ConsoleCmdGetSandboxOptions` | 20 | Optional bool arg; `LogOptions(GameStats.GetString(71), flag, LogType)` |
| `ConsoleCmdSaveDataManagerInfo` | 20 | Builds `AppendSaveDataManagerInfo` + `AppendSaveGameProviderInfo` text and `Log.Out`s it |
| `ConsoleCmdVisitPois` | 10 (+87) | Client-oriented POI tour: `start` / `pause` / `reset` subcommands teleport the local player through the decorator's prefabs (`No local player! (Are you in-game?)` on a dedi console) |
| `ConsoleCmdJunkDrone` | 289 | Player-owned drone control: `debuglog` / `help` / `log` (`logPlayerOwnedDrones`) / `unstuck` (teleport; falls back to `jds unstuck` server-side hint) / `clear` (`clearDronesForPlayer`) |
| `ConsoleCmdServerJunkDrone` | 289+ | The server-side twin of `ConsoleCmdJunkDrone` (same subcommand surface, operates on the server drone registry) |
| `ConsoleCmdPrefab` | 492 | Prefab-editor tool (`Command has to be run while in Prefab Editor!`): `load` / `save` / `simplify` / `simplify1` subcommands |
| `ConsoleCmdChallenges` | 65 | Client-only (`Cannot execute {0} on dedicated server, please execute as a client`): `list/l` / `complete/c` / `groups/g` subcommands |

Full per-command description strings remain in the inventory catalog; this table is
the **server-effect** pin for operators and clone fidelity.

---

## 3. Telnet connection (state machine)

`TelnetConsole` accepts TCP clients; each becomes a `TelnetConnection` with its own
`HandlerThread`. If telnet auth is enabled the connection must present the password
before any command runs; failed attempts are counted (`RegisterFailedLogin`) and the
connection is dropped after too many. The lockout is per endpoint:
`loginAttemptsPerIP` (`Dictionary<Int32, LoginAttempts>` keyed by the
connection's `EndPointHash`) with the console's `maxLoginAttempts` /
`blockTimeSeconds` settings. `LoginAttempts` (fields `count` / `lastAttempt`)
implements the window: `LogAttempt()` (IL=14) stamps `lastAttempt = Now`,
increments `count`, and returns `count < maxLoginAttempts` (still allowed);
`IsBanned()` (IL=20) resets `count = 0` when `(Now - lastAttempt).TotalSeconds`
exceeds `blockTimeSeconds` (the window expired), then returns
`count == maxLoginAttempts`. `AcceptClient` runs `IsBanned()` on the new
endpoint before creating the connection, so a banned IP is refused outright
until the window lapses.

```mermaid
stateDiagram-v2
  [*] --> Connected
  Connected --> AwaitingPassword: authEnabled -> "Please enter password:"
  Connected --> Authenticated: authEnabled == false
  AwaitingPassword --> Authenticated: authenticate(line) ok -> "Logon successful."
  AwaitingPassword --> AwaitingPassword: wrong -> RegisterFailedLogin -> "Password incorrect"
  AwaitingPassword --> Closed: too many failures -> "Too many failed login attempts!"
  Authenticated --> CommandLoop: handleReading / submitInput
  CommandLoop --> Execute: line -> SdtdConsole.ExecuteAsync(line, this)
  Execute --> CommandLoop
  CommandLoop --> Closed: line == "exit"
  CommandLoop --> Closed: socket closed / ConnectionUsable false
  Closed --> [*]
```

`HandlerThread` (IL=66) loops while usable: `handleReading` then
`handleWriting`, returns **25** (ms sleep) on success or **-1** to stop.
`handleReading` (IL=60) drains `TcpClient.Available` into a char buffer; CR/LF
ends a line via `submitInput`. `submitInput` sends the completed line to the
dispatcher (so a telnet client and the web Command API reach the exact same
`executeCommand`). `LoginMessage` emits the password prompt; `IsAuthenticated`
gates the command loop.

---

## 4. Network packages (verified)

Admin commands over the game connection (not telnet) use two packages.

**`NetPackageConsoleCmdServer` (ToServer, write IL=8):**

```text
cmd : string
```

`ProcessPackage` → `ConnectionManager.ServerConsoleCommand(Sender, cmd)` (IL=125):
length-guard long commands (log first 20 chars); resolve command; if missing or
not `CanExecuteForDevice`, push error lines via `NetPackageConsoleCmdClient`;
if `IsExecuteOnClient`, forward the cmd string to the client with `bExecute=true`;
else `AdminTools.CommandAllowedFor` then `SdtdConsole.ExecuteSync` and return
output lines with `bExecute=false`.

**`NetPackageConsoleCmdClient` (ToClient, write IL=31):**

```text
lineCount : i32
// lineCount x string
bExecute : bool
```

`ProcessPackage` (client): if `bExecute`, `SdtdConsole.ExecuteSync(lines[0])` and
show results; else only `GUIWindowConsole.AddLines(lines)` (server pushing
output).

Telnet/stdin bypass these packages (section 2).

## 5. The command contract (`ConsoleCmdAbstract`)

Every command subclasses `ConsoleCmdAbstract` and provides:

| Member | Role |
|---|---|
| `GetCommands()` | name + aliases (first is `PrimaryCommand`) |
| `Execute(params, senderInfo)` | the effect (abstract; per-command) |
| `DefaultPermissionLevel` | required access when not explicitly configured |
| `GetDescription()` / `GetHelp()` | `help` output |
| `IsExecuteOnClient` / `AllowedInMainMenu` / `AllowedDeviceTypes` | run-context gates |

There are **188** concrete commands in the V3.1.0 catalog (e.g. `admin`, `whitelist`,
`help`, `cvar`, `logenv`, `prefab`, `loot`, `visitmap`, `profiler`). This count includes
the web-dashboard commands (`webtokens`, `webpermission`, `invalidatecaches`,
`createwebuser`, `openiddebug`), which ship in the **base `Assembly-CSharp`**, not as a
mod. Mods can register additional commands at runtime above this baseline. The catalog
enumerates every leaf ([inventories/console-command-list.md](inventories/console-command-list.md));
this doc owns the framework, not each leaf command's full prose.

---

## 6. Dedicated relevance and residuals

- **Core dedicated surface:** stdin, telnet, and the web Command API all dispatch
  through `SdtdConsole.executeCommand` on the server.
- **Shared with the web server:** `WebConnection` (`Webserver`) is a console
  connection, so the web dashboard's Command endpoint is this system with an HTTP
  front (see [webserver.md](webserver.md) §3).
- **Residual:** telnet TCP socket internals; the in-game `GUIWindowConsole` UI
  (client-only); individual command effects (feature/content).

---

## Related docs

| Doc | Role |
|---|---|
| [webserver.md](webserver.md) | Web dashboard, whose Command API reuses this dispatcher |
| [managers.md](managers.md) | Other in-process managers |
| [full-surface.md](full-surface.md) | Where this sits in the whole-assembly map |
| [re-methodology.md](re-methodology.md) | How this was reversed |

**Leaf catalog:** every instance is enumerated in [`inventories/console-command-list.md`](inventories/console-command-list.md) (all 187 commands with descriptions).

## Changelog

- **2026-08-07:** SdtdConsole.Update (IL=60) one-command-per-frame FIFO drain:
  Monitor lock, CommandSenderInfo from entry.sender, executeCommand +
  Log.Exception, SendLines, RemoveAt(0).
- **2026-08-07:** ServerConsoleCommand 300-char reject; null adminTools deny;
  msgServer25 deny string.
- **2026-08-07:** CommandAllowedFor IL=12 level compare; ServerConsoleCommand
  IL=125 step list.
- **2026-08-07:** §2.1 high-value admin Execute IL table (killall/spawn/teleport/
  settime/save/shutdown/mem/weather/gamepref/webuser/loggamestate).
- **2026-07-28:** WebAPI Command endpoint cross-link.

- **2026-07-28:** Telnet HandlerThread 25ms loop; ServerConsoleCommand permission/client-exec path.

- **2026-07-28:** NetPackageConsoleCmdServer/Client wire bodies.

- **2026-07-23:** Initial console/telnet command-system reversal (registry, dispatch + permission gate, telnet auth) with state machines.
