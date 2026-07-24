# 7dtd-ServerTools research notes (optimizer lens)

**Repo:** https://github.com/dmustanger/7dtd-ServerTools  
Clone location: external, not tracked in this repo. (GitHub tip as of clone; README last touch **2023-10-04**)  
**Upstream status:** README says project **moved to Bitbucket** (`obsessive-coder/sevendaystodie-servertools`). GitHub is a frozen mirror / historical tree.  
**Target:** dedicated server admin mega-mod (net48, Harmony, Fody/Costura).  
**Purpose of this note:** what still matters for **EfficientServer / sim performance research**, not a full feature catalog.

---

## 1. What ServerTools is (and is not)

| Is | Is not |
|---|---|
| Large modular **ops + economy + anti-cheat + QoL** suite | A dedicated **AI/mesh performance** optim like EfficientServer |
| Heavy use of **ModEvents** + **runtime Harmony** (`AccessTools`) | Gateway/net rewrite (unlike NAIWAZI ServerKit) |
| Config-flagged tools under `ServerTools/src/Tools/*` | V3.0-validated against current `Assembly-CSharp` (assume rot) |
| Author: ObsessiveCoder / dmustanger lineage | Something to install blindly on V3.0.1 |

**Bottom line for us:** outdated as a product, still useful as a **catalog of server-side load sources and Harmony attachment points** that real public servers used for years.

---

## 2. Architecture patterns (worth copying style, not features)

### Entry / lifecycle (`Api.cs`)

```text
IModApi.InitMod
  → ModEvents.GameAwake / GameStartDone / GameShutdown
  → PlayerLogin / PlayerSpawnedInWorld / ChatMessage / PlayerDisconnected
  → LoadProcess.Load() after GameStartDone
  → dedicated-only guards: GameManager.IsDedicatedServer
```

- Config path under `UserDataFolder/ServerTools` or install `Mods/ServerTools`.  
- Shutdown path stops custom timers, unloads WebAPI, optional AutoRestart.  
- Matches our “dedicated-only + soft lifecycle” preference.

### Runtime Harmony (`Harmony/RunTimePatch.cs` + `Injections.cs`)

- Harmony id: `com.github.servertools.patch`  
- **Manual** `AccessTools.Method` + `harmony.Patch` (not only attribute patches)  
- On missing target: **log and continue** (same soft-fail idea as EfficientServer `PatchAllSafe`)  
- Try/catch in every injection with `[SERVERTOOLS] Error in …`

**Harmony targets in this tree** (complete list from `RunTimePatch.cs`):

| Type | Method | Hook | Purpose (admin suite) |
|---|---|---|---|
| `PlayerSlotsAuthorizer` | `Authorize` | Prefix | Reserved slots when full |
| `ConnectionManager` | `ServerConsoleCommand` | Postfix | Console command log |
| `NetPackageSetBlock` | `ProcessPackage` | Prefix | Block change / anti-cheat path |
| `World` | `AddFallingBlock` | Prefix | **Falling block remover** |
| `GameManager` | `Cleanup` | Finalizer | Force process kill on shutdown |
| `GameManager` | `CollectEntityServer` | Prefix | No vehicle pickup option |
| `GameManager` | `OpenTileEntityAllowed` | Pre/Post | Container access rules |
| `GameManager` | `PlayerSpawnedInWorld` | Postfix | Spawn hooks |
| `EntityAlive` | `SetDead` / `OnAddedToWorld` / `OnEntityDeath` | Pre/Post | Death / spawn side effects |
| `NetPackagePlayerInventory` | `ProcessPackage` | Pre/Post | Inventory / dupe checks |
| `ClientInfoCollection` | `GetForNameOrId` | Prefix | Name lookup tweak |
| `NetPackageDamageEntity` | `ProcessPackage` | Prefix | Damage detector |
| `ClientInfo` | `SendPackage` | Postfix | Outbound package inspection |
| `PersistentPlayerList` | `PlaceLandProtectionBlock` | Prefix | Claim limits |
| `NetPackageEntityAttach` | `ProcessPackage` | Prefix | Vehicle/drone attach |
| `GameManager` | `ExplosionServer` | Prefix | Explosion gating |
| `LootManager` | `LootContainerOpened` | Prefix | Loot open rules |
| `NetPackageTileEntity` | `Setup` | Postfix | TE stream |
| `GameManager` | `DropContentOfLootContainerServer` | Prefix | Bag drops |
| `GameManager` | `SavePlayerData` | Postfix | Save-side hooks |
| `BlockLandClaim` | `HandleDeactivatingCurrentLandClaims` | Prefix | Claim deactivate |
| `Log` | `Out(string)` | Prefix | Log filter / OutputLogBlocker |
| `UserIdentifierXbl` | `WriteCustomData` | Prefix | Xbox id quirks |
| `ChunkProviderGenerateWorld` | `RemoveChunks` | Prefix | Chunk removal / reset assist |

Also `AddFallingBlocks` (plural list) implemented in `Injections` (bulk path).

**Optimizer takeaway:** ServerTools is a textbook **NetPackage + World + GameManager** hook surface for **policy**, not for AI LOD. Our EfficientServer targets (`World.EntityActivityUpdate`, `EntityAlive.updateTasks`, mesh) are a **different layer**.

### Timers (`PersistentOperations/Timers.cs`)

- Core timer **1 s**; half-second timer for player checks.  
- Background work on 2s / 5s / 10s / 20s / 1m / 5m ticks.  
- `EntityCleanup.EntityCheck()` and `HighPingKicker.Exec()` run on those schedules.

**Takeaway:** heavy full-entity scans on a **timer**, not every frame. Fine for ops; if we ever do population maintenance, prefer **budgeted** scans and measure with APM (timer work still hits main thread if it touches Unity APIs).

### Modular flags

`ActiveTools` / config enable dozens of independent tools. Same modularity lesson as EfficientServer feature groups: **one flag, independent enable, log enable/disable**.

---

## 3. Tools with **performance relevance**

Ranked for EfficientServer / dedicated load research.

### 3.1 Falling block remover - **high relevance**

**Files:** `Tools/FallingBlocks/FallingBlocks.cs`, `Injections.AddFallingBlock(s)_Prefix`

**Behavior:**

- When enabled, on `World.AddFallingBlock` / bulk list: if block is not air/child/stability-ignore, **`SetBlockRPC(..., Air)`** instead of allowing normal falling-entity path.  
- Logs when bulk removals exceed `Max_Blocks` (default 10) with nearest player context.

**Why it matters for optim research:**

- Falling blocks / collapse can spike **physics + entity** work (ARCHITECTURE lag list: block physics family).  
- This is a **fidelity trade**: delete collapse simulation to save CPU.  
- EfficientServer today does **not** touch this; worth a **measured experiment** (blood moon base collapse scenarios) if APM shows falling-block related stacks.

**Risk:** changes building collapse / trap gameplay; must be optional and evidence-gated.

### 3.2 Entity cleanup - **medium relevance (ops)**

**File:** `Tools/EntityCleanup/EntityCleanup.cs`

**Behavior (timer-driven full `World.Entities.list` walk):**

- Remove **falling trees** after second sighting  
- Remove entities with **Y &lt; 0** (zombies/animals/vehicles/items)  
- Optional purge of **bicycles / minibikes / motorcycles / jeeps / gyros / drones**

**Why relevant:**

- Reduces **entity list length** and stray physics (underground, abandoned vehicles).  
- Same class of “do less sim” as AI LOD, but **content-policy** heavy (deleting player vehicles).

**Not** something to bake into EfficientServer without explicit product scope. Good as a **loadgen scenario lever** (“spawn junk entities, measure, cleanup”).

### 3.3 FPS target - **low / diagnostic**

**File:** `Tools/FPS/Fps.cs`

- Chat command reports `GameManager.Instance.fps.Counter`  
- Can set `GameManager.Instance.waitForTargetFPS.TargetFPS` (default fallback 20)

**Relevant only as:**

- Confirmation stock has a **target FPS wait** knob on dedicated  
- Not an optim; can **hurt** if set too high/low without understanding headless loop  

EfficientServer should not fight this; APM should measure tick time, not chat FPS claims.

### 3.4 Auto save world - **medium (I/O hitch)**

**File:** `Tools/AutoSaveWorld/*`

- Scheduled world saves (ops).  

**Relevance:** save spikes are on ARCHITECTURE lag list. Coordinated save intervals matter for APM baselines (don’t compare mid-save vs quiet). Not Harmony AI work.

### 3.5 High ping kicker - **ops / net quality**

**File:** `Tools/HighPingKicker/*`

- Kick clients over `Max_Ping` with violation counters + immunity XML.  

**Relevance:** reduces **bandwidth and far-player sim pressure** by removing bad connections. Product/ops decision, not sim optim. Loadgen bots often need immunity.

### 3.6 Hordes tool - **anti-pattern for optim**

**File:** `Tools/Hordes/Hordes.cs`

- If not blood moon, player count ≥ threshold, zombie count low → **`AIScoutHordeSpawner.CreateHorde`**  

**Relevance:** **increases** AI load. Useful only as a **stressor** for APM/loadgen, never as an EfficientServer feature.

### 3.7 Chunk / region reset - **world management**

**Files:** `ChunkReset`, `RegionReset`, load-time reset during login kick  

**Relevance:** can reduce long-term world bloat (saves, TE, sleeper density in abandoned areas). Orthogonal to runtime AI LOD; ops-heavy, save-destructive.

### 3.8 World radius - **bounds geography**

Timer-driven; keeps players inside a radius (reduces **chunk union** if enforced). Aligns with scale notes (bounded hot geography). Ops/game-design, not Harmony AI.

### 3.9 Blood moon tools / warrior / moans - **gameplay**

Mostly events and chat; not sim optim.

---

## 4. Anti-cheat / package hooks (context only)

ServerTools shares the **NAIWAZI-adjacent** idea of watching **NetPackage\*** paths:

- `NetPackageSetBlock`, `NetPackageDamageEntity`, `NetPackagePlayerInventory`, attach, TE, explosions  

Purpose is **grief/dupe/damage policy**, not bandwidth optim.  

**EfficientServer boundary:** do not mix AC into the optim DLL (same as workspace split APM vs EfficientServer).

---

## 5. What is **not** useful for the optimizer

| Area | Why ignore for EfficientServer |
|---|---|
| Bank / shop / auction / wallet / lottery | Economy |
| Homes / lobby / market / waypoints / travel | Teleport QoL |
| Clan / chat colors / MOTD / votes | Social |
| Discord / web panel / interactive map | Ops UI (Allocs-era integration) |
| Hardcore / prayer / confetti / big head | Gameplay gimmicks |
| Most of 100+ console commands | Admin surface |

Do not import this surface area.

---

## 6. Engineering lessons for EfficientServer

| Lesson | ServerTools evidence | Apply how |
|---|---|---|
| Soft-fail Harmony | Missing method → log, continue | Keep `PatchAllSafe` / optional groups |
| Dedicated-only | `IsDedicatedServer` gates | Keep `DedicatedOnly` |
| Feature flags | One tool = one enable | One EfficientServer config block per concern |
| Prefer less work over threads | Falling blocks → air; entity purge | Prefer LOD/caps before threading |
| Timer vs frame | Cleanup on multi-second ticks | Never full entity scan every frame |
| Package hooks for policy only | Damage/block packages | Stay out of AC in optim |
| Target rot | Tree frozen ~A21 era APIs | Always rebuild against live Managed |
| Process.Kill on Cleanup | Aggressive shutdown | Avoid unless ops requires; document |

---

## 7. Candidate experiments (only if APM asks)

1. **Falling-block storm:** script collapse / blood moon base damage → measure entity/physics time → optional EfficientServer or separate micro-mod “fall to air” behind a flag.  
2. **Entity list bloat:** spawn many items/vehicles → EntityCleanup-like unload → measure tick delta (loadgen scenario, not default optim).  
3. **Save hitch isolation:** AutoSave-like schedule vs random saves during APM compare windows.  
4. **Do not** port Hordes or economy systems.

---

## 8. Version / install caution

- GitHub README: last detailed update **Oct 2023**; development claimed on **Bitbucket**.  
- Expect **broken Harmony targets** on V3.0.1 without retarget.  
- Costura embeds deps into `ServerTools.dll` (different from our “don’t ship second Harmony”).  
- Installing full ServerTools on a research dedicated will **pollute** APM baselines (timers, package hooks, chat). Prefer isolated test or code reading only.

---

## 9. Summary for EfficientServer roadmap

| Steal | Leave |
|---|---|
| Soft-fail runtime patching style | Entire admin suite |
| Falling-block CPU tradeoff as **research** | Vehicle purge as default |
| Timer-budgeted maintenance mindset | Hordes spawner |
| Modular enable flags | Web/Discord/economy |
| NetPackage as **policy** surface (know it exists) | Implementing AC |

ServerTools is a **historical public-server kitchen sink**. For optim, only a few blades cut sim cost; the rest is community ops DNA.

---

## Changelog

- **2026-07-16:** Clone GitHub tree; inventory Harmony targets; score tools for optimizer relevance; note Bitbucket move / 2023 freeze.
