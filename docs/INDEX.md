# 7DTD dedicated RE documentation (generic engine)

**Owns:** hub for **generic** dedicated engine RE narratives + dump index.  
**Not:** RealEarth product status/lessons (`7dtd-realearth`, private companion project, not published).  
**Game:** V3.2.0 (b10) dedicated `Assembly-CSharp.dll`.  
**Policy:** research only. Do not redistribute game IL or managed DLLs.  
**Coverage bar:** dedicated-relevant **managed** surfaces. Open leftovers: [`residuals.md`](meta/residuals.md).

```text
docs/              this hub (INDEX.md)
docs/meta/         what the corpus covers, how it was derived, what IL cannot close
docs/releases/     per-release exact deltas
docs/loop/         frame and simulation loop
docs/entities/     entity tick, AI, pathing, survival stats
docs/world/        world gen, chunks, terrain, persistence, asset formats
docs/network/      wire protocol: framing, join, package bodies
docs/admin/        lifecycle, auth, console, web admin, mods, sandbox options
docs/gameplay/     the gameplay systems the server simulates
docs/content/      scripted content: events, quests, dialog, character data
docs/social/       chat, parties, third-party integration
docs/inventories/  raw method/call inventories backing the narratives
il/                regenerable Mono.Cecil dumps only (local; not in git)
oss-tools/         survey notes on third-party server tools/mods
7dtd-realearth/    RealEarth product docs (sibling repo, private companion, not published)
```

---


## Start here

| # | Doc | Use when |
|---|---|---|
| 0 | [`architecture-map.md`](meta/architecture-map.md) | **Start here.** Whole-system visual map: layers, boot, frame phases, sim core, wire, persistence |
| 1 | [`coverage.md`](meta/coverage.md) | Is engine family X documented? Which dump? |
| 2 | [`engine-limitations.md`](meta/engine-limitations.md) | What stock ceilings bind any dedicated server? (+ known stock defects) |
| 3 | [`loop.md`](loop/loop.md) | How the dedicated frame/sim runs |
| 4 | [`protocol.md`](network/protocol.md) | Wire framing, join, golden package bodies |
| 5 | [`protocol-frames.md`](network/protocol-frames.md) | Visual RFC/Mermaid byte frames per package |
| 6 | [`residuals.md`](meta/residuals.md) | What IL cannot close |
| 6b | [`completion-bar.md`](meta/completion-bar.md) | What "100% documented" means (tiers A-D) |

Campaign audit (V3.2.0 evidence + residual map): [`../workspace/outputs/docs-research-audit-20260803.md`](../workspace/outputs/docs-research-audit-20260803.md).

Live scheduled-event evidence (2026-08-11, stock V3.1.0 dedicated runs):
[air drop](../workspace/notes/live-airdrop-verification-20260811.md),
[wandering horde](../workspace/notes/live-horde-verification-20260811.md),
[blood-moon start](../workspace/notes/live-bloodmoon-verification-20260811.md);
the method (boot/settime/join/observe) is in [re-methodology.md](meta/re-methodology.md) 5e.

```mermaid
flowchart LR
  A[coverage] --> B[loop]
  B --> C[generic family docs]
  C --> D[il/ dumps]
  B --> E[residuals]
  C -.->|product only| RE[7dtd-realearth/docs]
```

---

## Reading paths

| Goal | Path |
|---|---|
| Whole engine map | coverage → loop → family docs → residuals |
| **Stock ceilings (any dedi)** | [engine-limitations.md](meta/engine-limitations.md) → loop (scaling laws: optimizer `measured-scaling.md`) |
| **Zig / custom dedi clone** | [ZIG_CLONE.md](../../zdtd-server/docs/ZIG_CLONE.md) → [protocol.md](network/protocol.md) → loop → network → world-chunks → save-region |
| Wire / join / golden packages | protocol → **protocol-frames** → **protocol-packages** → network → loadgen PackageCodec |
| How to reverse-engineer | **re-methodology** → [`../tools/`](../tools) → coverage |
| Re-run the zdtd provenance review | `../../zdtd-server/docs/provenance-review.md` (copy-paste prompt; picked up by `~/review-prompts` as `*-review.md`) |
| **Stock hardcode pin** | [`../tools/stock-sync.sh`](../tools/stock-sync.sh) → [`../tools/data/stock_facts.json`](../tools/data/stock_facts.json) (see re-methodology §5c) |
| Frame / gmUpdate | loop → loop-gmupdate → inventories/gmupdate-calls |
| Entities / AI / path | entity-ai → closed-gaps → aidirector |
| World / chunks / save | world-chunks → save-region → terrain-height |
| Net | network → closed-gaps |
| Light / mesh / water | light-mesh-water |
| **Tuned game constants (exact numbers)** | the owning topic doc (constants pinned by `tools/tests/test_tuned_constants.py`, 524 pins: horde geometry + airdrop schedule, block masks, entity ids, spawn rings, stealth, caps) |
| Managers / ModEvents | managers |
| **Live APM scale / bottlenecks / tuning** | optimization mod: `../../7dtd-server-optimizer/docs/` (measured-scaling, bottlenecks, runtime-tuning) |
| **RealEarth product limits** | `../../7dtd-realearth/docs/ENGINE_LIMITATIONS.md` |
| **RealEarth product hub** | `../../7dtd-realearth/docs/INDEX.md` |
| EfficientServer optim | [`../../7dtd-server-optimizer/docs/`](../../7dtd-server-optimizer/docs) |
| **Perf research → optim backlog** | [`../../7dtd-server-optimizer/docs/PERF_RESEARCH_BRIEF.md`](../../7dtd-server-optimizer/docs/PERF_RESEARCH_BRIEF.md) |

### Key engine state machines (generic)

| Lifecycle | Doc |
|---|---|
| gmUpdate phases A-J | [loop.md](loop/loop.md) §2 |
| UpdateTick slice vs full | [loop.md](loop/loop.md) §3 |
| AI LOD + path request | [entity-ai.md](entities/entity-ai.md) |
| Chunk InProgress lifecycle | [world-chunks.md](world/world-chunks.md) §4 |
| Net package bands | [network.md](network/network.md) §2 |
| World save/load | [save-region.md](world/save-region.md) §1 |
| Origin FixedUpdate (dedi no-op) | [loop.md](loop/loop.md) §1 / §12 |

Product Streamed state machines (tiles, inject gate, SoloSlide): see product ``realearth-runtime.md``.

---

## Subsystem map

One folder per subsystem; each doc is the single home for its topic. Raw
method/call inventories back them and are listed under [Inventories](#inventories-not-primary-reading).

### Meta and method (`docs/meta/`)

What the corpus covers, how it was derived, and what managed IL cannot close.

| Doc | Role |
|---|---|
| [architecture-map.md](meta/architecture-map.md) | Whole-system visual map and subsystem ownership index |
| [coverage.md](meta/coverage.md) | Family → narrative → dump map; census numbers |
| [full-surface.md](meta/full-surface.md) | Whole-assembly map (all 88 namespaces) + coverage ledger toward 100% |
| [residuals.md](meta/residuals.md) | What managed IL cannot close (the only open-item list) |
| [out-of-scope-surface.md](meta/out-of-scope-surface.md) | Reached-but-out-of-scope types classified by category (the boundary map) |
| [client-side-surface.md](meta/client-side-surface.md) | Client-executed surface (XUi, client-only subsystems) narrated for the census; authoritative classification in out-of-scope-surface.md |
| [engine-limitations.md](meta/engine-limitations.md) | Generic stock ceilings (sim, net, AI, height, GC, ops) |
| [re-methodology.md](meta/re-methodology.md) | How to RE: toolchain, dumping, reading IL into wire layouts |
| [completion-bar.md](meta/completion-bar.md) | What "100% documented" means (tiers A-D) |
| [dedicated-misc-systems.md](meta/dedicated-misc-systems.md) | Grab-bag of small dedicated systems (gamestage groups, water apply, boss/companion, admin users, entitlements, AI tasks, ...) |
| [dedicated-leftovers.md](meta/dedicated-leftovers.md) | Final leftovers batch (inventory manager, search paths, prefab volumes, physics bodies, infra types; AuthAndLoginManager verdict) |

### Release deltas (`docs/releases/`)

Per-release exact deltas, each mapping a shipped change to the doc that owns it.

| Doc | Role |
|---|---|
| [changelog-3.0.0.md](releases/changelog-3.0.0.md) | V3.0.0 Dead Hot Summer feature inventory mapped to RE homes |
| [changelog-3.1.0.md](releases/changelog-3.1.0.md) | V3.1.0 Henpocalypse feature inventory mapped to RE homes |
| [changelog-3.2.0.md](releases/changelog-3.2.0.md) | V3.1.0 -> V3.2.0 exact IL-verified delta (+ per-fact homes, §9) |

### Frame and simulation loop (`docs/loop/`)

The dedicated frame and simulation loop, and the managers it drives.

| Doc | Role |
|---|---|
| [loop.md](loop/loop.md) | Peers, gmUpdate, UpdateTick, subsystem scale |
| [loop-gmupdate.md](loop/loop-gmupdate.md) | gmUpdate phase narrative (detail under loop.md §2) |
| [managers.md](loop/managers.md) | Manager Update ILs + ModEvents fields |

### Entities, AI and pathing (`docs/entities/`)

The per-entity tick: AI, pathing, movement and survival stats.

| Doc | Role |
|---|---|
| [entity-ai.md](entities/entity-ai.md) | TickEntity → AI → path + thresholds |
| [entity-movement.md](entities/entity-movement.md) | Move chain + physics surface: MoveHelper → Entity::Move → CC collision, gravity, friction |
| [entity-stats.md](entities/entity-stats.md) | Entity + survival stats: health/food/water/stamina over-time, damage |
| [raycast-pathing.md](entities/raycast-pathing.md) | Raycast path generator + steering (junk-drone travel; A* handoff) |
| [aidirector.md](entities/aidirector.md) | AIDirector type inventory |
| [uai.md](entities/uai.md) | Utility AI (UseAIPackages branch): packages, considerations, tasks, decision cycle |
| [stealth-smell.md](entities/stealth-smell.md) | Stealth/noise/smell: server detection inputs driving zombie sensing |
| [closed-gaps.md](entities/closed-gaps.md) | Timer 20 Hz, AIDirector install, ASP→A*, net bands |

### World, terrain and persistence (`docs/world/`)

World generation, chunk lifecycle, terrain, persistence and the asset formats behind them.

| Doc | Role |
|---|---|
| [world-chunks.md](world/world-chunks.md) | Gen, load/send, SetBlock, chunk flags |
| [world-generation.md](world/world-generation.md) | RWG world create pipeline: WorldBuilder stages, threading, outputs |
| [chunk-providers.md](world/chunk-providers.md) | ChunkProvider* (dedicated = GenerateWorldFromRaw) + decoration layer |
| [terrain-height.md](world/terrain-height.md) | WorldConstants, height APIs, expand pin |
| [hot-patch-height.md](world/hot-patch-height.md) | Whether the `ChunkBlockYDim` 256 -> 32768 expand can be hot-patched at runtime |
| [save-region.md](world/save-region.md) | WorldState, chunk write/read (incl. 64-layer loop), RegionFile* |
| [save-persistence.md](world/save-persistence.md) | Save path/slot model + SaveInfoProvider (dedicated runs the System.IO placeholder) |
| [light-mesh-water.md](world/light-mesh-water.md) | Light, stability, mesh, water, deco |
| [stability.md](world/stability.md) | Stability calculator / falling blocks: StabilityInitializer spread/clear, GetBlockStability BFS, EntityFallingBlock landing |
| [dynamic-mesh.md](world/dynamic-mesh.md) | Dynamic mesh: destroyed-geometry regen, threading, DynamicMeshes/ persistence, channel-1 streaming |
| [blocks.md](world/blocks.md) | Block framework: BlockValue bitfield, virtual surface, damage/upgrade, block-change flow |
| [block-shapes.md](world/block-shapes.md) | BlockShape rotation model + BlockTrigger firing chain |
| [texture-atlas.md](world/texture-atlas.md) | Block texture-atlas metadata + minimap color chain: uvmapping XML in meshdescriptions_assets_all.bundle, CalcChunkColors → GetMapColor → ToColor5 (map chunks) |
| [texture-atlas-unityfs.md](world/texture-atlas-unityfs.md) | UnityFS container layout of meshdescriptions_assets_all.bundle (backs texture-atlas.md) |
| [shader-subprogram-blob.md](world/shader-subprogram-blob.md) | Shader (class 48) sub-program blob: LZ4 per-platform blobs, 12-byte record table, code-blob record, and the 38-byte DX11 program-data header before the DXBC |

### Networking and wire protocol (`docs/network/`)

LiteNet framing, the join sequence and every package body.

| Doc | Role |
|---|---|
| [network.md](network/network.md) | ConnectionManager, NetEntity, NetPackage census, interest bands |
| [protocol.md](network/protocol.md) | LiteNet envelope, challenge, join, golden entity packages |
| [protocol-frames.md](network/protocol-frames.md) | RFC-style + Mermaid byte frames per package |
| [protocol-packages.md](network/protocol-packages.md) | Per-package body catalog, channel/compress/auth census, encryption handshake |

### Server lifecycle, auth and ops (`docs/admin/`)

Boot to shutdown, platform auth, the console and web admin, mods and sandbox options.

| Doc | Role |
|---|---|
| [server-lifecycle.md](admin/server-lifecycle.md) | Boot -> world load -> run -> save/shutdown; game state + game modes; player persistence + land claims |
| [platform-auth.md](admin/platform-auth.md) | Platform identity + server join auth (Steam/EOS), EAC/EOS managed wrappers |
| [console-commands.md](admin/console-commands.md) | Console/telnet command system: registry, dispatch + permissions, telnet auth |
| [webserver.md](admin/webserver.md) | Web admin server: HTTP pipeline, auth/session, permissions, REST, SSE |
| [mod-loading.md](admin/mod-loading.md) | Mod discovery + DLL load pipeline, EAC gate, ModEvents lifecycle |
| [sandbox-options.md](admin/sandbox-options.md) | Sandbox/game-option type system + sandbox-code codec |
| [server-browser-prefabs.md](admin/server-browser-prefabs.md) | GameServerInfo advertisement + prefab-instance persistence |

### Gameplay systems (`docs/gameplay/`)

The gameplay systems the dedicated server simulates.

| Doc | Role |
|---|---|
| [spawning.md](gameplay/spawning.md) | Entity spawning: biome/dynamic/horde/scout sources, caps, spawn->despawn |
| [combat-damage.md](gameplay/combat-damage.md) | Damage pipeline: DamageSource, armor/health apply, death + kill award |
| [buffs.md](gameplay/buffs.md) | Buff system: EntityBuffs tick, BuffValue lifecycle, tag/death removal, net sync |
| [items.md](gameplay/items.md) | Item framework: ItemValue packing, ItemClass/Actions, use lifecycle, inventory, durability |
| [crafting-recipes.md](gameplay/crafting-recipes.md) | Recipe model, CanCraft validation, craft-queue lifecycle, unlock progression |
| [tile-entities-power.md](gameplay/tile-entities-power.md) | Tile entities + power graph: storage, PowerManager tick, workstations/forges, traps |
| [loot-economy.md](gameplay/loot-economy.md) | Loot generation + respawn, traders (restock/hours/pricing), vending rent |
| [vehicles-drones-turrets.md](gameplay/vehicles-drones-turrets.md) | Vehicles (client-authoritative motion), drones + turrets (server behavior), waypoints |
| [weather-environment.md](gameplay/weather-environment.md) | Server-authoritative weather sim, storm state machine, temperature survival |
| [progression.md](gameplay/progression.md) | Player XP/level, skill points, perk purchase, calculated level |
| [signs.md](gameplay/signs.md) | Writable signs (AuthoredText) + layered drawing model + moderation |
| [map-objects.md](gameplay/map-objects.md) | Map/compass markers: MapObject + NavObject registries (client-derived) |

### Content and scripting (`docs/content/`)

Scripted content: events, quests, dialog and character data.

| Doc | Role |
|---|---|
| [game-events.md](content/game-events.md) | Scripted-event interpreter: sequences, actions, requirements, decisions, loops |
| [minevents.md](content/minevents.md) | Triggered-effect framework: FireEvent dispatch, action/requirement/target model |
| [quests-challenges.md](content/quests-challenges.md) | Quest + challenge template/instance lifecycles, objectives, rewards, QuestEventManager |
| [sdcs-character-gear.md](content/sdcs-character-gear.md) | SDCS skinned character system: archetype/items.xml authoring contracts, asset-path grammar, rig-stitching pipeline (client-executed, server-loaded data) |
| [npc-dialog.md](content/npc-dialog.md) | Trader/NPC dialog tree + requirement gating + quest-data records |

### Social and integrations (`docs/social/`)

Chat, parties and factions, and third-party integration.

| Doc | Role |
|---|---|
| [chat.md](social/chat.md) | Chat: NetPackageChat wire, server channel routing, system messages |
| [parties-factions.md](social/parties-factions.md) | Parties (session), faction standing matrix, ally handshake |
| [twitch-integration.md](social/twitch-integration.md) | Twitch: server action/vote execution via game events (connection is client residual) |

## Inventories (not primary reading)

| Doc | Prefer instead |
|---|---|
| [inventories/frame-entries.md](inventories/frame-entries.md) | loop.md |
| [inventories/gmupdate-calls.md](inventories/gmupdate-calls.md) | loop-gmupdate.md |
| [inventories/manager-updates.md](inventories/manager-updates.md) | managers.md |
| [inventories/loop-complete.md](inventories/loop-complete.md) | loop.md, save-region.md |
| [inventories/deeper.md](inventories/deeper.md) | entity-ai.md |
| [inventories/gaps.md](inventories/gaps.md) | closed-gaps.md |
| [inventories/opt-scan.md](inventories/opt-scan.md) | 7dtd-server-optimizer [OPTIMIZATION_CANDIDATES.md](../../7dtd-server-optimizer/docs/OPTIMIZATION_CANDIDATES.md) |
| [inventories/netpackages.md](inventories/netpackages.md) | protocol.md, protocol-packages.md, network.md |
| [inventories/netpackage-bodies.md](inventories/netpackage-bodies.md) | protocol-packages.md (auto-extracted wire bodies; regenerate with WireBodies.exe) |
| [inventories/coverage-report.md](inventories/coverage-report.md) | coverage.md (auto-generated reachability vs doc-mention coverage) |
| [inventories/state-machines.md](inventories/state-machines.md) | index of all 74 modelled lifecycles, grouped by cluster (generated) |
| [inventories/te-features.md](inventories/te-features.md) | tile-entities-power.md (11 TEFeatureAbs leaves) |
| [inventories/challenge-objectives.md](inventories/challenge-objectives.md) | challenges (28 objective leaves; client-tracked) |
| [inventories/sequence-actions.md](inventories/sequence-actions.md) | game-events.md (123 SequenceAction leaves) |
| [inventories/dedicated-leaves.md](inventories/dedicated-leaves.md) | small dedicated leaf types attributed to their owning subsystem (88) |
| [inventories/block-behaviors.md](inventories/block-behaviors.md) | blocks.md (65 Block leaves) |
| [inventories/item-actions.md](inventories/item-actions.md) | items.md (38 ItemAction leaves) |
| [inventories/minevent-actions.md](inventories/minevent-actions.md) | minevents.md (71 triggered-effect leaves) |
| [inventories/console-command-list.md](inventories/console-command-list.md) | console-commands.md (188 commands, with descriptions) |
| [inventories/xmlsToLoad.md](inventories/xmlsToLoad.md) | mod-loading.md (49 WorldStaticData XmlLoadInfo rows) |
| [inventories/entityclass-props.md](inventories/entityclass-props.md) | entity-ai.md D8.6-D8.7 (187 EntityClass prop-name constants from the cctor) |
| [inventories/gamestats-gameprefs.md](inventories/gamestats-gameprefs.md) | every doc that cites `GameStats[i]` / `GamePrefs.Get*(i)` (82 + 317 index rows) |
| [inventories/quest-objectives.md](inventories/quest-objectives.md) | quests-challenges.md (38 objectives) |
| [inventories/sequence-requirements.md](inventories/sequence-requirements.md) | game-events.md (37 concrete requirements) |

---

## Dump sets (`il/`)

Generic engine dumps plus surfaces dump consumed by RealEarth product docs.

| Directory | Focus | Used by |
|---|---|---|
| gmUpdate / frame-entries / deep / deeper / gaps / loop-complete / opt-scan / dedi-complete | Generic loop RE | research narratives |
| full-v3.2.0 | **Canonical whole-assembly IL dump** (7451 types; DumpAll, pipe-safe) | the IL-citation sweep, every `docs/*.md` claim |
| surface-v3.2.0 | FullSurface metadata (surface-types + surface-namespaces; whole-assembly IL totals) | full-surface.md, test_surface_wellformed |
| netpackages-v3.2.0 | NetPackage body dumps + protocol META | protocol-packages.md, RE_GAP_CLOSURE |
| stability-v3.2.0 | Stability calculator / falling blocks | stability.md |
| terrain-v3.2.0 | Stock vs expanded height | research + product |
| realearth-surfaces-v3.2.0 | Chunk, Origin, PPL, region | product realearth-surfaces.md |

Policy: [`../il/README.md`](../il/README.md).

---

## Tools

**All RE tooling lives in this repo:** [`../tools/`](../tools) (tracked). Full
catalog: [`../tools/README.md`](../tools/README.md). How to RE:
[`re-methodology.md`](meta/re-methodology.md).

| Group | What |
|---|---|
| `tools/src/` | General maintained dumpers: `Census`, `DumpMethod`, `DumpType`, `DumpNetPackages`, `NetProtocolCensus`, `FullSurface` (whole-assembly metadata), `DumpAll` (full local IL) |
| `tools/legacy/` | 38 dumpers (12 canonical per-family + ad-hoc helpers) that generated the `il/` dump sets (`DumpDediComplete`, `DumpGmUpdate`, `DumpTerrain`, ...) |
| `tools/parity/` | Cross-version wire-surface snapshot + diff (steamcmd) |
| `tools/re-scratch/` | One-off Zig reversers for on-disk formats |
| `tools/tests/` | Dump-regen + coverage regression tests |

```bash
# Build once, then run (stop the game if targeting the live Managed DLL)
cd tools && ./build.sh
ASM="$HOME/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll"
mono bin/Census.exe "$ASM"
mono bin/DumpNetPackages.exe "$ASM" ../il/netpackages-v3.2.0
mono bin/legacy/DumpDediComplete.exe "$ASM" ../il/dedi-complete-v3.2.0
```

Gates: `make test` (full suite, needs the live DLL), `make test-docs` (DLL-free corpus invariants; runs in CI on every push), `make stock-check` (pins vs live DLL + siblings), `make regen-check` (dump-regeneration check), `make facts` (machine-checked stock pins).  
IL policy: [`../il/README.md`](../il/README.md).

Host topology (not IL): [`../../7dtd-server-optimizer/docs/HOST_TUNING.md`](../../7dtd-server-optimizer/docs/HOST_TUNING.md).  
Live scale laws: [measured-scaling.md](../../7dtd-server-optimizer/docs/measured-scaling.md).

---

## Version policy and IL citation convention

**Policy: track the latest stock release only.** The corpus is regenerated
against each new dedicated `Assembly-CSharp.dll` and the previous version's sets
are deleted in the same change, so a citation can never quietly refer to an old
build. Regenerate before deleting: an assembly that is no longer installed
cannot be dumped again.

**Current pin:** V **3.2.0 b10**. Every tracked set in [`../il/`](../il/) is
V3.2.0; the V3.1.0 sets were retained for the 3.1.0→3.2.0 diff and the V3.0.1
sets were removed on 2026-08-06.

| Citation form | Means |
|---|---|
| `il/<set>-v3.2.0/...` | the tracked V3.2.0 dump sets |
| `asm.il:NNNN` | a V3.2.0 single-file dump kept outside the repo, identified by MD5 in [`../il/README.md`](../il/README.md) |

Mentions of V3.0.1 and V3.1.0 in these documents are deliberate history (what
changed between releases, what a prior corpus measured), not stale pins. Line
numbers written before 2026-08-06 may still be V3.0.1 numbers, which drift from
the V3.2.0 dump by roughly 3500 lines in the NetPackage region.

Per-release delta maps (which doc owns each shipped change) live with the release they describe: [`changelog-3.2.0.md`](releases/changelog-3.2.0.md) §9, [`changelog-3.1.0.md`](releases/changelog-3.1.0.md), [`changelog-3.0.0.md`](releases/changelog-3.0.0.md).

---

## Companion repos

Reimplementation, optimization and product work consume the RE here and live in
their own repos ([`../AGENTS.md`](../AGENTS.md) doc scope). Cost measurements,
lever catalogs and tuning knobs belong to the mod that ships them.

### Zig clone (`zdtd-server/docs/`)

| Doc | Role |
|---|---|
| [ZIG_CLONE.md](../../zdtd-server/docs/ZIG_CLONE.md) | Clone architecture built from the wire/loop RE: module map, M0-M6 milestones |
| [PROVENANCE.md](../../zdtd-server/docs/PROVENANCE.md) | Provenance ledger: every behavior/perk/value to its stock source (file map 187/187, constants, divergence register; gated by zdtd `tools/provenance_scan.py`) |

### Optimization mod (`7dtd-server-optimizer/docs/`)

Bottlenecks, algorithm cost anatomy, APM scaling laws, GC/FPS tuning, allocation
reuse and aggressive levers.

| Doc | Role |
|---|---|
| [measured-scaling.md](../../7dtd-server-optimizer/docs/measured-scaling.md) | Live APM scaling laws |
| [bottlenecks.md](../../7dtd-server-optimizer/docs/bottlenecks.md) | Consolidated ranked bottleneck catalog (super-linear walls, bad data structures, serial stages) |
| [algorithms.md](../../7dtd-server-optimizer/docs/algorithms.md) | Every hot-subsystem algorithm + data structure (path scan, net interest, chunk RLE, Boehm GC, spatial queries) |
| [aggressive-optimizations.md](../../7dtd-server-optimizer/docs/aggressive-optimizations.md) | Unsafe/beyond-Harmony lever catalog: risk classes, per-cost targets, gain/risk hierarchy |
| [runtime-tuning.md](../../7dtd-server-optimizer/docs/runtime-tuning.md) | Process knobs: Boehm GC env, GC.Collect gate, ModEvents lifecycle, settargetfps |
| [allocation-reuse.md](../../7dtd-server-optimizer/docs/allocation-reuse.md) | Buffer reuse / preallocation to cut churn; what is pooled vs what still churns |

---

### RealEarth product (`7dtd-realearth/docs/`, private, not published)

| Topic | File (product `7dtd-realearth/docs/`, private, not published) |
|---|---|
| Streamed runtime lessons | `realearth-runtime.md` |
| Engine surfaces used by RealEarth | `realearth-surfaces.md` |
| Adversarial review catalog | `realearth-review.md` |
| Product status Done/Partial | `MODIFICATIONS.md` |
| Lon/lat dual coords | `LON_LAT.md` |
| Absolute → inject path | `ABSOLUTE_STREAMING.md` |
| Product hub | `INDEX.md` |

---

## Changelog

- **2026-09-11:** Corpus restructured into subsystem folders. `docs/` was 72 flat
  files; it is now one folder per subsystem (`meta`, `releases`, `loop`, `entities`,
  `world`, `network`, `admin`, `gameplay`, `content`, `social`) beside `inventories/`,
  with every internal and cross-repo link repointed and the hub's subsystem map
  rebuilt from the layout. Re-filed on the way: the release changelogs into
  `releases/`, `sandbox-options`/`server-browser-prefabs` into `admin/`,
  `npc-dialog` into `content/`, `signs`/`map-objects` into `gameplay/`, and the
  two census grab-bags (`dedicated-misc-systems`, `dedicated-leftovers`) into
  `meta/`. Gates now resolve a doc by basename (`_common.doc()`), the link gate
  walks the whole tree and resolves every link against its own folder, and
  `StateMachines` clusters by folder. Hub order also changed: map first (Start
  here, reading paths, subsystem map), history last; the V3.2.0/V3.1.0 shipped-delta
  maps moved to [changelog-3.2.0.md](releases/changelog-3.2.0.md) §9 and
  [changelog-3.1.0.md](releases/changelog-3.1.0.md) § Per-fact homes; the "One home
  per topic" table was dropped as a duplicate of the subsystem tables (its omissions
  were audit finding F23); every cross-repo pointer folded into `## Companion repos`.
- **2026-09-11:** Stale facts found by the full suite and refreshed against the live
  V3.2.0 b10 assembly: whole-assembly IL total 1,740,737 -> **1,743,842**
  ([full-surface.md](meta/full-surface.md)); registered wire packages 189 -> **191** and
  the channel-1/compressed census (POIAround out, POIMetadataResponse in)
  ([network.md](network/network.md) §3, [protocol-packages.md](network/protocol-packages.md));
  six drifted IL citations (`ConnectionManager.Update` 228->231, `Entity.Detach` 79->92,
  `ItemActionAttack.Hit` 1614->1564, `TraderArea.IsWithinProtectArea` 47->59,
  `EAIRunawayFromEntity.FindEnemy` 166->136, `EntityAlive.updateCurrentBlockPosAndValue`
  318->341); the dumper-generated inventories re-spliced from the current dumps; the
  removed-in-V3.2.0 `TraderComparer` rows dropped from the leaf inventories. New:
  `NetPackageDamageEntity`'s `flags:u32` bit layout is now documented where the package
  body is defined, and its 11 `cFlags*` constants are pinned by `test_tuned_constants`.
- **2026-08-24:** [shader-subprogram-blob.md](world/shader-subprogram-blob.md) adds the `ParserBindChannels` block that closes every code-blob record, with the mesh-channel to shader-input mapping; a record without it is refused by the runtime.
- **2026-08-24:** [shader-subprogram-blob.md](world/shader-subprogram-blob.md) adds the parameter blob (the binding table Unity keeps instead of the stripped DXBC `RDEF` chunk), round-tripped byte for byte over 3403 stock records, and the parallel index space between `m_ParameterBlobIndices` and `m_PlayerSubPrograms`.
- **2026-08-24:** New page [shader-subprogram-blob.md](world/shader-subprogram-blob.md): Shader (class 48) compiled-code container, including the 38-byte DX11 program-data header decoded over 7366 sub-programs (`tools/shader_blob_dump.py`). Method added as [re-methodology.md](meta/re-methodology.md) 7b.
- **2026-08-22:** Wire the texture-atlas docs into the hub (section D rows; the docs shipped in 24c8199 without INDEX or audit-table entries).
- **2026-08-11:** Tools section now names both gates (`make test` full suite, `make test-docs` CI variant); research CI added (`.github/workflows/ci.yml`); reading-path table links the zdtd provenance ledger (`zdtd-server/docs/PROVENANCE.md`).
- **2026-08-10:** LiteNetLib join-churn race closed as a managed defect
  ([network.md](network/network.md) §4.0: `UnsyncedEvents=true` + receive-thread
  `Clients.List` enumeration; ramp workaround validated), `NetPackageMinEventFire`
  null-itemValue NRE documented + audited as the unique reachable instance-callvirt
  write defect ([protocol-packages.md](network/protocol-packages.md) §6.23), stock-defects
  section added to [engine-limitations.md](meta/engine-limitations.md), ModEvents
  subscriber baseline pinned in [managers.md](loop/managers.md) §2, stale
  native-LiteNetLib labels purged corpus-wide, regression test wired into
  `make test`.
- **2026-08-09:** Wiki cross-linking pass: added hub backlinks (`**Hub:**
  INDEX.md`) to the 5 docs missing one; fixed `client-side-surface.md` orphan
  (was 0 incoming, now INDEX row + narrated-twin links from out-of-scope-surface
  and coverage); linked every bare `doc.md` / `§N` prose reference; added
  Related docs sections to completion-bar, dedicated-leftovers,
  dedicated-misc-systems, out-of-scope-surface. Result: 0 orphans, every doc
  links INDEX, all 63 reachable from INDEX (BFS), 801 links / 12.7 per doc,
  no dead links.
- **2026-08-09:** Docs consistency pass: consolidated 22 docs' duplicate
  `## Changelog` runs into single sections (no content change); fixed the
  broken non-table row in the reading-paths table; repointed `zig-clone.md`
  links to the actual `ZIG_CLONE.md` (7 docs); normalized `## Related` ->
  `## Related docs`; removed stale git-ignored `coverage-report*.gaps.tsv`
  scratch from inventories/. Dead-link audit: all 1,611 links resolve.
- **2026-08-08:** Namespace count corrected to 89 in the full-surface row (7432 types / 53235 methods / 1,740,737 IL).
- **2026-08-06:** Nine dated addendums from a full V3.1.0 b14 re-dump (2026-08-05):
  quests (template inheritance, objective Write shapes, fail-soft Quest::Read),
  loot-economy (trader S2C delivery paths, ToServer-only TraderData, client-side
  pricing), aidirector (blood-moon window and party spawner, client-local FX),
  world-generation (prefab rotation direction, .blocks.nim id space, YOffset),
  spawning (AIDirectorConstants, SpawnManagerBiomes, gamestage indirection),
  items (stack defaults, fuel time, InventoryTransaction wire), progression
  (progressionData blob, XP curve, V3.1.0 death penalty), world-chunks (stability
  on clients, DamageBlock repair/upgrade, subbiome deco), network (package
  registry, direction gate, per-package channel/compress/reliability, GSI version
  format). Line numbers in those sections are from the 2026-08-05 dump and drift
  from the tracked `il/` V3.1.0 sets.

- **2026-09-05:** Pin bumped to **V3.2.0 (b10)** after Steam dedicated/client
  download (app 294420 buildid 24994542). Census unchanged; managed delta only
  `Platform.EOS.RemoteFileStorage` cancel path ([changelog-3.2.0.md](releases/changelog-3.2.0.md)
  §8). Sibling version pins bumped in `7dtd-loadgen` and `zdtd-server`.
- **2026-08-28:** Retarget corpus to **V3.2.0 (b9)**: regenerated all dump
  sets + committed inventories + `stock_facts.json`/`xml_pins.json` from the
  live dedicated build; diffed every type against the retained V3.1.0 sets
  (exact 3.1.0→3.2.0 delta: [`changelog-3.2.0.md`](releases/changelog-3.2.0.md)); wire
  facts updated for `NetPackageDamageEntity` (packed flags + KillXPScale),
  POI metadata packages (POIAround removed), `NetPackageConfirmSpawnEntity` +
  `EntityCreationData.requestedBy/requestKey`, `ItemValue.Flags`; feature docs
  updated (trader-door honk, combine, kill-XP rework, Timid AI, deco
  suppression); § V3.2.0 shipped delta map added (V3.1.0 map kept as history).
  Sibling pins (loadgen `GameVersion`, zdtd `stock_wire`) intentionally NOT
  bumped here; the siblings pull the new facts from this repo.
- **2026-08-06:** Corpus hygiene pass after research-docs-corpus audit: inventory titles
  (gmupdate-calls, netpackages) retitled to V3.1.0; vague "delta removed" pointers
  replaced by this § V3.1.0 shipped delta map + topic links; sandbox catalog names
  day/night density + chicken coop knobs; dynamic-mesh WriteRegion dead path re-closed
  with Xref (self-retry only).
- **2026-08-02:** Retarget hub to V3.1.0 (b14) Henpocalypse; experimental-delta promoted to shipped (later retired into topic docs + delta map above).

- **2026-07-23:** Narratives regrouped into topical clusters (A meta/method, B loop, C entities/AI, D world/terrain/save, E net/wire); fixed aidirector second H1.
- **2026-07-23:** zig-clone.md moved to `zdtd-server/docs/` (reimplementation design, not stock RE).
- **2026-07-23:** Scope split: optimization-mod docs (bottlenecks, algorithms, measured-scaling, runtime-tuning, allocation-reuse, aggressive-optimizations) moved to `7dtd-server-optimizer/docs/`; this repo keeps stock-game RE only (see [`../AGENTS.md`](../AGENTS.md) doc scope).
- **2026-07-23:** protocol-packages.md (per-package body catalog, channel/compress/auth census, encryption handshake); re-methodology.md (how to RE); RE tooling consolidated into tracked `../tools/`.
- **2026-07-20:** protocol-frames.md visual wire catalog (RFC + Mermaid).
- **2026-07-20:** protocol.md + zig-clone.md (wire RE + Zig high-perf clone architecture).
- **2026-07-19:** Added engine-limitations.md (generic dedi ceilings); reading path + topic table.
- **2026-07-19:** Related docs on family narratives; inventory Prefer headers completed.
- **2026-07-18:** Product RealEarth links as full paths; Tools section with regenerate example + test gate.
- **2026-07-18:** Split ownership: RealEarth docs moved to `7days-realworld/docs/`; research keeps generic engine only.
- **2026-07-18:** State machines, mermaid, kebab-case rename/merge of research narratives.
