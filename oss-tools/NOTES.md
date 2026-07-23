# Open-source 7DTD tools survey (optimizer lens)

**Date:** 2026-07-16  
**Scope:** public GitHub (and related) tools cloned locally (not tracked here; see source links below), plus prior notes on ServerTools and NAIWAZI.  
**Purpose:** extract **architecture and performance lessons** for EfficientServer / APM / loadgen, not a product catalog or install guide.

**Already covered in dedicated notes:**

| Topic | Path |
|---|---|
| NAIWAZI ServerKit (paid GS+Gateway, free AC/Bot) | [`naiwazi.md`](naiwazi.md) |
| ServerTools (dmustanger / ObsessiveCoder) | [`servertools.md`](servertools.md) |

**Local clones (this survey):**

| Clone | Upstream | Tip seen at clone |
|---|---|---|
| `oss-IceCoffee-ServerKit` | https://github.com/1249993110/7DaysToDie-ServerKit | 2025-10-08 |
| `oss-SphereII` | https://github.com/SphereII/SphereII.Mods | 2026-07-13 (3.0 line) |
| `oss-CSMM` | https://github.com/CatalysmsServerManager/7-days-to-die-server-manager | 2025-12-03 |
| `oss-MVirus` | https://github.com/TheNormalnij/7DTD-MVirus | 2025-03-11 |
| `oss-OCB-Electricity` | https://github.com/OCB7D2D/OCBElectricityOverhaul | 2025-10-27 |
| `oss-OCB-StopFuel` | https://github.com/OCB7D2D/OCBStopFuelWaste | 2024-07-05 |
| `oss-lag-shield` | https://github.com/jonathan-robertson/lag-shield | 2022-07-22 (A20) |
| `oss-BackupMod` | https://github.com/jonathan-robertson/BackupMod | 2022-09-17 |
| `oss-discord-log-hook` | https://github.com/jonathan-robertson/7dtd-discord-log-hook | 2025-07-04 (EOL for 2.0+) |
| `oss-Allocs` | Allocs server_fixes package (binaries + web UI; no full C# tree here) | N/A |

---

## 1. Landscape map (what each tool is for)

```text
                    ┌─────────────────────────────┐
                    │  In-process dedicated DLL   │
                    │  (Harmony / IModApi)        │
                    └──────────────┬──────────────┘
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
    ┌──────▼──────┐         ┌──────▼──────┐         ┌──────▼──────┐
    │ SIM / AI    │         │ ADMIN / AC  │         │ CONTENT     │
    │ optim       │         │ economy QoL │         │ gameplay    │
    └──────┬──────┘         └──────┬──────┘         └──────┬──────┘
           │                       │                       │
   EfficientServer          ServerTools suite         SphereII packs
   (this workspace)         IceCoffee (live)          OCB electricity
   IceCoffee *commented*    lag-shield (ping)         OCB StopFuel
   NAIWAZI optim (closed)   Allocs commands
                            MVirus (mod transfer)

                    ┌─────────────────────────────┐
                    │  Out-of-process ops         │
                    └──────────────┬──────────────┘
                                   │
              CSMM (Node + worker + DB + Discord)
              NAIWAZI Gateway (closed, network split)
              BackupMod (save zip; in-process but I/O)
              discord-log-hook (webhook observability)
```

**Hard rule for our stack:** EfficientServer stays in the **SIM / AI optim** column. Ops, AC, economy, content, and external panels stay out of that DLL. APM measures; loadgen stresses; host tuning is ops.

---

## 2. IceCoffee 7DaysToDie-ServerKit — **highest optim research value**

**What it is:** open-source dedicated **web panel + REST + SQLite + admin functions** (TianYi / LSTY lineage). MIT, actively maintained into late 2025. Depends on TFP Harmony + Allocs-style map/web pieces.

**What it is not:** a shipping AI/mesh optim product. The interesting optim experiments live under `HarmonyPatchers/PerformanceTuning/` and are **entirely commented out**.

### 2.1 Live optim-adjacent code (enabled)

| Feature | Where | Lesson |
|---|---|---|
| **Falling block → air** | `WorldPatcher.Before_AddFallingBlock` + runtime Harmony from `GlobalSettings.EnableFallingBlockProtection` | Same fidelity trade as ServerTools: kill collapse sim. Optional, config-gated. |
| **Auto zombie cleanup** | `GlobalSettings.OnEntitySpawned`: full entity list count, console-remove over threshold | Crude population cap. Full list walk on spawn is expensive at scale; prefer budgeted / event counters. |
| **Main-thread marshaling** | `ModApi.MainThreadSyncContext` capture at `InitMod`; `Utils.ExecuteConsoleCommand(..., inMainThread)` | **Gold pattern** for any web/async side: never touch Unity world from worker without `Send`/`Post`. |
| **Runtime Harmony toggle** | `GlobalSettings.OnSettingsChanged` Patch/Unpatch | Feature flags that **install/uninstall** patches without restart (good for A/B if safe). |
| **Manual GC console** | `Commands/GarbageCollection.cs` (`GC.Collect` ×2 + finalizers) | Ops diagnostic only. Not a perf strategy; can hitch. |
| **Heap in API** | `ServerController` exposes `GC.GetTotalMemory(false)` | Cheap metric for panels; APM already should own deeper GC. |
| **Empty world A* skip** | commented `AstarManagerPatcher` only inits path threads when world ≠ `"Empty"` | Niche loadgen/empty-map win; not V3 production path. |

### 2.2 Commented PerformanceTuning experiments (do not ship blindly)

All under `src/SdtdServerKit/HarmonyPatchers/PerformanceTuning/`. **Every file is full-line-commented.** Treat as **design fossils**, not validated V3 patches.

#### A) Concurrent path finder (`ASPPathFinderThread` + `AstarManagerPatcher`)

- Subclasses stock `PathFinderThread`.  
- `ConcurrentHashSet` wait queue + `ConcurrentDictionary` of `PathInfo`.  
- Worker: `Task.Factory.StartNew(..., LongRunning)` loop; dequeues entity ids; `Task.Run` per path `navigator.GetPathTo`.  
- `Thread.Sleep(20)` between queue drains.  
- Replaces A* init to start this thread.

**Why interesting:** same problem space as EfficientServer path **admission** and as NAIWAZI marketing “entity independent threads.”  

**Why dangerous:**

- Path results still need main-thread-safe consumption; race on entity/nav state is classic desync/crash.  
- Unbounded `Task.Run` per path can stampede the thread pool under blood moon.  
- Sleep(20) is a latency floor, not a budget.  

**Our takeaway:** prefer **admission control and less path requests** (SIM_PARALLELISM / OPTIMIZATION_IDEAS) over replacing the path thread wholesale. If ever re-tried: fixed worker count, bounded queue, drop/merge far requests, soft-fail Harmony, measure with APM.

#### B) `ConnectionManager.SendPackage` Parallel.ForEach (`ConnectionManagerPatcher`)

- Fan-out package enqueue across clients with `Parallel.ForEach`.  
- Also sketched for multi-package and `FlushClientSendQueues`.  
- Only slightly less wild piece left in comments: parallel `UpdatePings`.

**Why interesting:** net send is on the ARCHITECTURE lag list; NAIWAZI claimed bandwidth cuts (different mechanism: gateway).  

**Why dangerous:**

- LiteNetLib / connection objects rarely tolerate concurrent `AddToSendQueue` / flush.  
- Ordering and channel 0/1 semantics matter.  
- Parallelism over a few dozen clients is often **slower** than a tight loop.

**Our takeaway:** research **interest management / package LOD** (fewer packages), not parallel send, unless profiling proves serial fan-out dominant and API is proven thread-safe.

#### C) Parallel EAI task list (`EAITaskListPatcher`)

- Replaces `EAITaskList.OnUpdateTasks` with `Parallel.ForEach` over tasks + locks on `executingTasks`.  
- Still runs `action.Update()` serially afterward.

**Why interesting:** acknowledges AI task update cost.  

**Why dangerous:** EAI and world queries are main-thread / Unity-unsafe in practice; locks do not fix that. This is the textbook “thread the AI” trap SIM_PARALLELISM rejects.

**Our takeaway:** **do less AI** (LOD, delays, caps), not Parallel.ForEach EAI.

#### D) Async damage package fan-out (`EntityAlivePatcher`)

- Local damage applied immediately; tracked-player damage package on `Task.Run`.

**Risk:** ordering vs death/despawn; network side effects off-main-thread. Leave alone.

#### E) Async `PlayerDataFile.Save` (`PlayerDataFilePatcher`)

- `Task.Run` write tmp → bak → final with per-player-name lock and pooled binary writer.

**Why interesting:** save hitches are real (ARCHITECTURE).  

**Why dangerous:** concurrent read of in-flight player data; incomplete write on crash; double-save races.  

**Our takeaway:** schedule saves, avoid save during APM windows, host storage tuning. Async save only with clear ownership snapshot (copy on main, write on worker). Not default EfficientServer scope.

#### F) Offload `NetPackageSetBlock` / texture / trigger (`NetPackagePatcher`)

- `Task.Run` + `MainThreadSyncContext.Post` back for `ChangeBlocks`.  
- Parallel `DynamicMeshManager.ChunkChanged` sketch.

**Lesson:** they correctly remembered **commit on main thread**. Still high risk for block authority. Prefer not touching block apply path for pure optim.

### 2.3 Engineering patterns worth copying

| Pattern | IceCoffee | EfficientServer / workspace |
|---|---|---|
| Capture `SynchronizationContext` at init | Yes | Any future async helper; APM bridge already careful |
| Config-gated Harmony Patch/Unpatch | Yes | Feature groups; optional runtime toggle is nice-to-have |
| Soft admin features separate from optim | Mostly (optim dead) | Keep optim DLL pure |
| Falling-block air swap | Live flag | Research candidate only |
| Full entity scans for cleanup | Live | Prefer counters / budgets |

### 2.4 Score for EfficientServer

| Steal / study | Leave |
|---|---|
| Main-thread sync context idiom | Parallel EAI / Parallel SendPackage as-is |
| Falling-block optional trade | Auto zombie full-list on spawn |
| Concurrent pathfinder as **cautionary design** | Shipping ASPPathFinderThread |
| Runtime patch toggle idea | Web panel, economy, OWIN stack |

---

## 3. SphereII Mods — **content giant, dedi stubs**

**What it is:** large multi-mod collection (SCore, NPCs, winter, challenges, …) still landing **3.0** commits (tip 2026-07). Primary value is **gameplay/content Harmony**, not dedicated FPS.

### SphereII Dedicated Tweaks (`Mods/SphereII Dedicated Tweaks`)

Source is essentially a **stub**:

- `DediPatchesInit` → `harmony.PatchAll`.  
- Active patch: `EntityClass.Init` Prefix that **returns true** after a dedicated check (no property stripping).  
- Commented historical idea: strip material swaps / force placeholder models on dedicated so the headless process does not load heavy client assets.

**Lesson:**

- Dedicated can skip **client-only asset work** if something still runs Init paths for models.  
- Stock dedicated already avoids much client rendering; measure before re-adding model stripping.  
- “Dedicated Tweaks” as a name is aspirational; **do not assume** SphereII ships real AI/path optims.

### Rest of SphereII

- Heavy NPC / AI content (SCore, NPC Add On) **increases** sim cost when used.  
- Useful as **stress content** for loadgen (more AI types), not as optim reference.  
- Soft-fail / multi-mod coexistence lessons live in their docs; still retarget after game updates.

**Score:** low direct optim value; high awareness that **content mods dominate CPU** and can invalidate EfficientServer A/B if mixed into baselines.

---

## 4. Allocs server_fixes — **ops foundation, not sim**

**Local:** binary mods (`Allocs_CommandExtensions`, `Allocs_CommonFunc`, `Allocs_WebAndMapRendering`) + `server_fixes.tar.gz`. No full C# source in this clone.

**Role in ecosystem:**

- Console extensions, map rendering, web server hooks.  
- IceCoffee **requires** TFP/Allocs map + web pieces.  
- CSMM and many panels talk to servers via telnet/web APIs that this generation popularized.

**Optim lesson:** map tile generation and web handlers can steal CPU/IO if misconfigured (zoom, refresh, many viewers). Keep **map rendering off or rate-limited** during APM baselines. Not EfficientServer work.

---

## 5. CSMM (Catalysm Server Manager) — **out-of-process ops**

**What it is:** Node.js Sails app + workers + MySQL/MariaDB + Discord. Self-host web manager.

**Features that touch “performance” only as ops policy:**

- High ping kicker, country ban, timed commands, auto world save  
- Analytics charts: online players, server FPS, RAM  
- Player tracking (location/inventory) via server queries  

**Architecture lesson:**

- Heavy admin logic **outside** the game process is the correct split for ops (aligns with NAIWAZI gateway idea at product level, without claiming CSMM rewrites net protocol).  
- Polling `gettime` / `mem` / FPS via telnet still costs the dedicated process; **sample rate** matters for APM contamination.

**Score:** product inspiration for **control plane vs data plane**; zero Harmony AI code to port.

---

## 6. MVirus — **mod content delivery, net bandwidth class**

**What it is:** server→client **mod file transfer** (HTTP internal server, external HTTP, or in-band net streams). Custom `NetPackageMVirus*` packages + stream pool.

**Relevance:**

- Join-time bandwidth and main-thread/package load during large mod packs.  
- Design: prefer **HTTP offload** over in-game net stream for bulk files (README explicitly rates in-band as poor).  
- Compression + cache options.

**Lesson for scale notes:**

- Stock game already ships config/XML; custom bulk transfer is a **different channel**.  
- EfficientServer should not own mod CDN.  
- If loadgen/join stress includes MVirus-scale assets, separate that scenario from pure AI tick tests.

**Patterns worth noting:** stream pooling, static vs active compression, IPv6 hooks, clear EAC incompatibility.

---

## 7. OCB Electricity Overhaul — **tile-entity / power tick cost**

**What it is:** deeper power grid sim (multi-source, batteries, solar curve). Author states it is **not optimized**, recalculates a lot per tick, and extra fields sync MP.

**Measured self-check in code** (`OcbPowerManager`):

```csharp
var watch = Stopwatch.StartNew();
// ... power update ...
if (watch.Elapsed.TotalMilliseconds > 20)
    Log.Warning("PowerManager took " + ms + " ms");
```

**Lessons:**

1. **Content systems can become main-thread budgets** (20 ms is a large fraction of a 50 ms “20 FPS” tick).  
2. In-process **Stopwatch around a subsystem** is a cheap APM cousin for mod authors (and for us when validating a patch group).  
3. Extra MP fields on power sources = bandwidth + serialize cost; same class as “net LOD” research.  
4. EfficientServer must not fight power mods; document **compatibility**: heavy TE grids change baselines.

**OCB StopFuelWaste:** small Harmony on `TileEntityWorkstation.HandleFuel` to stop fuel burn when idle. **Micro sim save**, gameplay fidelity change. Pattern: **conditional skip of stock update work** when state is idle (same spirit as AI LOD: do not run expensive path when outcome is null).

---

## 8. jonathan-robertson micro-mods

### lag-shield (High Ping Kicker extracted)

- Login + ~30 s checks; failure budget → kick → temp ban.  
- Config under savegame JSON; full console config (host-friendly).  
- Based on ServerTools High Ping Kicker.

**Lesson:** bad RTT clients amplify lag for everyone (author claim; plausible for prediction/combat). Ops tool. Loadgen bots need immunity. Not sim optim.

### BackupMod

- Scheduled zip of saves; DI-style modules; skip-if-empty; archive retention.  
- **Save I/O hitches** during backup windows corrupt APM windows if not scheduled.

**Lesson:** coordinate backup/save with measurement windows (ServerTools AutoSave lesson again).

### discord-log-hook (EOL for 2.0+)

- Harmony/log hook → Discord webhooks for WARN/ERR + rolling context.  
- Observability, not optim. Pattern: **async outbound HTTP** so Discord never blocks tick (verify still true if forked).

---

## 9. Cross-tool matrix (optimizer relevance)

| Tool | Layer | Sim CPU | Net | I/O | Steal for EfficientServer? |
|---|---|---|---|---|---|
| **IceCoffee (live)** | Admin + flags | Falling-block, zombie cap | — | backups | Falling-block research; main-thread sync |
| **IceCoffee (commented PT)** | Experimental | Path/EAI parallel sketches | Parallel send | Async PDF save | Study + reject default ship |
| **ServerTools** | Admin mega | Falling-block, entity cleanup | package AC | autosave | Same as NOTES.md |
| **NAIWAZI** | Gateway + closed optim | claimed thread split | claimed BW cut | GW-held saves | Architecture fantasy; no free optim DLL |
| **SphereII Dedi** | Stub | maybe asset skip | — | — | Almost nothing live |
| **Allocs** | Map/web | map tiles | web | map disk | Keep off during APM |
| **CSMM** | External panel | — | telnet poll | DB | Control plane split |
| **MVirus** | Mod CDN | — | join bulk | HTTP | Scenario isolation |
| **OCB Electricity** | Content TE | power Update budget | TE sync | power save | Subsystem Stopwatch pattern; baseline risk |
| **OCB StopFuel** | Content TE | skip idle fuel | — | — | “Skip work when idle” pattern |
| **lag-shield** | Ops net | indirect (kick laggy) | kick | — | Ops only |
| **BackupMod** | Ops I/O | hitch windows | — | zip saves | Schedule vs APM |
| **discord-log-hook** | Ops obs | — | webhooks | — | Non-blocking logs |

---

## 10. Recurring patterns (what the ecosystem actually does)

### 10.1 Patterns that **reduce work** (good)

1. **Falling block → air** (ServerTools, IceCoffee live): delete physics/entity path.  
2. **Entity / vehicle / underground purge** (ServerTools): shorten entity list.  
3. **Population hard cap** (IceCoffee zombie cleanup): crude but real.  
4. **Skip idle TE work** (StopFuel): conditional early-out.  
5. **Kick high ping** (ServerTools, lag-shield, CSMM): shrink bad clients.  
6. **World radius / chunk reset** (ServerTools): bound geography / bloat.

These align with EfficientServer philosophy: **LOD, caps, admission, less work** before threads.

### 10.2 Patterns that **move work off main thread** (risky fossils)

1. Parallel path / Parallel EAI / Parallel SendPackage (IceCoffee commented).  
2. Task.Run damage / block package processing (IceCoffee commented).  
3. Async player save without snapshot (IceCoffee commented).  
4. NAIWAZI marketing “entity independent threads” (closed, unmeasured here).

Ecosystem history: people **try** threading hot paths, then **comment it out** or sell closed binaries. That is strong evidence the hard part is **correctness**, not inventing Parallel.ForEach.

### 10.3 Patterns that **move work out of process** (ops-correct)

1. CSMM workers + DB.  
2. NAIWAZI Gateway process (closed).  
3. MVirus external HTTP for bulk files.  
4. Discord webhooks for logs.

EfficientServer is **in-process by design**. Do not grow a second process unless the project mission changes.

### 10.4 Observability patterns

1. Subsystem Stopwatch + warn threshold (OCB).  
2. Heap/FPS in APIs and panels (IceCoffee, CSMM, ServerTools FPS cmd).  
3. Discord on WARN/ERR (discord-log-hook).  

Our split remains better: **APM owns measurement**, EfficientServer stays free of profiler UI.

---

## 11. What to add to EfficientServer / research backlog

Evidence-gated only (same rules as `OPTIMIZATION_IDEAS.md`).  
Threading / extract-sim / full hot-path catalog: [`../../7dtd-optimizer/docs/SIM_PARALLELISM.md`](../../7dtd-optimizer/docs/SIM_PARALLELISM.md) §5–7.

### Promote for **measurement experiments**

| Experiment | Source inspiration | Notes |
|---|---|---|
| Optional falling-block air (or separate micro-mod) | ServerTools + IceCoffee | Blood moon base collapse scenarios |
| Path **admission** (max new paths/frame, priority) | Inverse of IceCoffee ASPPathFinderThread | Less queue, not more parallel GetPathTo |
| Idle early-out audit for TE-heavy servers | OCB StopFuel spirit | Only if APM shows TE family |
| Closest-player / AI scale cache TTL | Existing ideas + zombie-cap crude form | Prefer cache over full entity scans |
| Save/backup blackout windows in APM protocol | BackupMod + ServerTools AutoSave | Method, not a patch |

### Explicitly **do not** port

| Idea | Why |
|---|---|
| Parallel.ForEach EAI | Unity/world thread safety |
| Parallel SendPackage | Connection API safety, tiny N |
| Unbounded Task.Run path workers | Thread pool stampede |
| Full IceCoffee / ServerTools admin surface | Wrong DLL mission |
| NAIWAZI Gateway reimplementation | Product; closed; out of EfficientServer scope |
| MVirus / Allocs web | Wrong layer |
| Manual GC as optim | Hitch generator |

### Soft process lessons

| Lesson | Apply |
|---|---|
| Soft-fail missing Harmony targets | Keep PatchAllSafe / optional groups |
| Feature flag per concern | efficientserver.json groups |
| Dedicated-only | Keep DedicatedOnly |
| Runtime Patch/Unpatch optional | Nice for A/B if state reset is safe |
| MainThreadSyncContext if any async | Copy IceCoffee idiom carefully |
| Content mods change baselines | Document incompat / isolate loadgen packs |
| Comment-out history is a signal | Prefer measure + less work over heroic threads |

---

## 12. Comparison to prior research

| Axis | NAIWAZI | ServerTools | IceCoffee | This OSS set overall |
|---|---|---|---|---|
| Source | Closed optim + free AC/Bot | Full admin C# (frozen GH) | Full admin C# + dead PT | Spread: admin, content, ops |
| Net architecture | Gateway split | Stock + package AC | Stock + web panel | MVirus CDN; CSMM poll |
| Path/AI threading | Marketing claims | None | Commented concurrent path + Parallel EAI | Nobody ships clean parallel AI OSS |
| Falling blocks | Unknown in free pkgs | Yes | Yes (live) | Confirmed ecosystem standard trade |
| Fit for EfficientServer | Architecture curiosity | Few sim levers | Best open optim fossils | Confirms less-work doctrine |

**Bottom line:** public open source is rich in **admin panels, content, and ops policy**. It is poor in **validated sim optimizers**. The only recurring **sim** lever across ServerTools and IceCoffee is **do less** (falling blocks, cleanup, caps). Ambitious threading lives as **commented code** or **closed products**. That validates this workspace’s EfficientServer approach: Harmony LOD/admission first, threads only with jobs + safe commit and APM proof.

---

## 13. Clone hygiene

- Cloned trees are **research mirrors** (kept outside this repo); do not install wholesale onto measurement dedicated.  
- Expect API rot (lag-shield A20, BackupMod 2022, ServerTools GH 2023). SphereII and IceCoffee are fresher but still not V3.0.1-certified here.  
- Do not redistribute game assemblies from any `References/` or `sdk/` folders.  
- Paid NAIWAZI packages remain out of scope (see naiwazi NOTES).

---

## Changelog

- **2026-07-16:** Link SIM_PARALLELISM §5–7 for extract/threading/hot-path home.
- **2026-07-16:** Survey IceCoffee PerformanceTuning (commented), live falling-block/zombie-cap/main-thread sync; SphereII Dedicated Tweaks stub; Allocs binaries; CSMM; MVirus; OCB Electricity + StopFuel; lag-shield; BackupMod; discord-log-hook. Cross-matrix and EfficientServer backlog notes.
