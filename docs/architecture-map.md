# Architecture map: the dedicated server at a glance (V3.0.1)

**Owns:** the visual, whole-system view of what a headless 7 Days to Die server is
and how its parts connect: process lifecycle, the frame, the simulation core, the
wire, and persistence. This is the map you read **first**, then follow into the
subsystem doc that owns each box.
**Not:** the detail behind any single box (each has its own doc, linked from every
diagram); measured performance ([`../../7dtd-optimizer/docs/`](../../7dtd-optimizer/docs)).
**Evidence:** every box and edge below is drawn from the narratives in this corpus,
which are IL-derived. Where a number appears (IL size, tick rate, channel) it comes
from the owning doc.
**Hub:** [`INDEX.md`](INDEX.md). **Method:** [`re-methodology.md`](re-methodology.md).

---

## 1. The whole server in one picture

Five layers. Everything a dedicated server does is somewhere in here.

```mermaid
flowchart TB
  subgraph EXT[External]
    CL[Stock game clients]
    ADM[Admin: telnet / web dashboard]
    PLAT[Steam / EOS platform services]
  end

  subgraph TRANSPORT[Transport and session]
    LNL[LiteNetLib UDP<br/>vendored, native-adjacent]
    AUTH[Authorizer chain<br/>Native 400 - Crossplat 490 - EAC 600 - Enc 601 - Final 999]
    CONN[ConnectionManager<br/>ClientInfo registry]
  end

  subgraph WIRE[Wire protocol]
    PKG[NetPackage registry<br/>193 types, channel 0 bulk-band 1]
    ENC[Encryption handshake<br/>4 pre-auth packages]
  end

  subgraph SIM[Simulation core - the authority]
    GM[GameManager.gmUpdate<br/>631 IL, phases A-J]
    TICK[UpdateTick<br/>GameTimer 20 Hz]
    WORLD[World + ChunkCluster]
    ENT[Entities / AI / pathing]
    SUBS[Gameplay subsystems<br/>blocks, items, buffs, quests, power, spawning]
  end

  subgraph PERSIST[Persistence]
    REG[Region files + WorldState<br/>SaveLoad 884 IL]
    AUX[decoration.7dt, power.dat, factions.dat,<br/>players, prefabs.xml, dynamic mesh .group]
  end

  CL -->|UDP| LNL
  LNL --> AUTH
  AUTH --> CONN
  PLAT -.identity / tickets.-> AUTH
  CONN --> PKG
  PKG --> CONN
  ENC -.before auth.-> PKG
  PKG --> GM
  GM --> PKG
  ADM --> CONS[SdtdConsole + Webserver]
  CONS --> GM
  GM --> TICK
  TICK --> WORLD
  TICK --> ENT
  TICK --> SUBS
  WORLD --> REG
  ENT --> REG
  SUBS --> AUX
  WORLD --> AUX
```

**The one-line summary:** clients speak a versioned package protocol over
LiteNetLib; the server authenticates them through a staged authorizer chain, then
runs an authoritative 20 Hz simulation whose results are both replicated back over
the wire and flushed to region files.

---

## 2. Boot: process start to first tick

```mermaid
stateDiagram-v2
  [*] --> Boot: GameManager.StartGame(offline)
  Boot --> EacAdvisory: startGameCo reads GameServerInfo.EACEnabled (advisory log only)
  EacAdvisory --> StartAsServer
  StartAsServer --> Config: load XML config, mods (ModManager two-pass), sandbox options
  Config --> WorldLoad: createWorld then ChunkCluster.Init picks the provider (dedicated uses GenerateWorldFromRaw)
  WorldLoad --> Advertise: PrepareLocalServerInfo then TCP plus Steam/EOS/LAN announce
  Advertise --> Started: GameStateManager.InitGame(server)
  Started --> Frame: frame loop drives gmUpdate
  Frame --> Frame: players join, sim ticks
  Frame --> Shutdown: quit requested
  Shutdown --> [*]: SaveAndCleanupWorld
```

There is **no managed EAC integrity gate** on this path; the integrity-violation UI
lives in a client-only branch of `gmUpdate`
([`server-lifecycle.md`](server-lifecycle.md)).

---

## 3. The frame: gmUpdate phases A to J

Phase C is the load-bearing detail for a clone: it is where the client half lives,
and a dedicated server jumps straight over it.

```mermaid
flowchart TB
  A["A. Frame prologue"] --> B["B. Optional singleton managers<br/>null-checked chain"]
  B --> C["C. Client UI / EAC / cursor"]
  C -->|IsDedicatedServer: SKIPPED| D
  C -->|client| D["D. Destroy queue (locked)"]
  D --> E{"E. Game started?"}
  E -->|no| J
  E -->|yes| F["F. Pre-sim world-adjacent work<br/>EntityAsyncManager, GameTimer"]
  F --> G["G. UpdateTick - THE SIM CORE"]
  G --> H["H. Post-tick presentation / chunks / explode"]
  H --> I["I. Memory / GC / save / packages<br/>server branches"]
  I --> J["J. Epilogue"]
```

Manager tick chain in phase B (each null-checked, so a disabled feature costs
nothing): `TwitchManager`, `DroneManager`, `VehicleManager`, `TriggerEffectManager`,
`QuestEventManager`, `TokenManager`, `PowerManager`, `DismembermentManager`,
`FactionManager`, `NavObjectManager`, `GameEventManager`, `TriggerManager`,
`RaycastPathManager`. `EntityAsyncManager` is **phase F**, not B
([`managers.md`](managers.md)).

---

## 4. Simulation core: what one tick actually does

```mermaid
flowchart LR
  TICK["UpdateTick<br/>GameTimer 20 Hz"] --> WT[World tick]
  WT --> CH["Chunks<br/>load / decorate / save"]
  WT --> ENTS["TickEntities<br/>slice or full"]
  ENTS --> AI["AI: EAI task lists<br/>+ A* path requests"]
  ENTS --> BUFF["Buffs tick<br/>duration, stat recalc"]
  ENTS --> STAT["Survival stats"]
  WT --> TE["Tile entities<br/>+ PowerManager 6.25 Hz"]
  WT --> SPAWN["Spawning: 5 sources<br/>into World.SpawnEntityInWorld"]
  WT --> GE["Game events / quests / challenges"]
  CH --> ND["NetEntityDistribution<br/>observer-gated replication"]
  ENTS --> ND
  TE --> ND
  SPAWN --> ND
  ND --> OUT["ToClient packages"]
```

The **authority rule**: the server owns block state, entity state, damage, loot, and
persistence. Clients predict movement and render. The notable exceptions the corpus
found are documented rather than smoothed over: crafting is **split authority**
(`CanCraft` runs client-side; the server validates the inventory transaction), and
client inventory is client-authoritative in practice.

---

## 5. Wire: how a client and this server converse

```mermaid
sequenceDiagram
  participant C as Client
  participant S as Server
  C->>S: LiteNetLib connect (password = connect key)
  S->>C: challenge + NetPackagePackageIds (server-advertised id map)
  opt encryption enabled
    S->>C: EncryptionRequest
    C->>S: EncryptionPublicKey (params, hash, signed hash)
    S->>C: EncryptionSharedKey
    C->>S: KeyExchangeComplete
  end
  C->>S: PlayerLogin (identity, platform tokens, version)
  Note over S: authorizer chain runs. On failure the server sends PlayerDenied with an EKickReason
  S->>C: PlayerLoginAnswer, WorldInfo, ConfigFile
  C->>S: RequestToEnterGame / RequestToSpawnPlayer
  S->>C: PlayerSpawnedInWorld, chunks (channel 1, compressed), entity spawns
  loop steady state
    C->>S: input, block changes, inventory transactions
    S->>C: authoritative entity/block/stat updates
  end
```

Two bands: **channel 0** for everything by default, **channel 1** for the six bulk
packages (`Chunk`, `ChunkRemove`, `MapChunks`, `DynamicMesh`, `POIAround`,
`WorldFolder`). Eight packages self-compress. Exactly ten are legal before auth,
which is the entire pre-auth attack surface
([`protocol-packages.md`](protocol-packages.md)).

---

## 6. Persistence: what lands on disk

```mermaid
flowchart LR
  SIM[Simulation state] --> WS["WorldState main.ttw<br/>SaveLoad 884 IL"]
  SIM --> RF["Region files<br/>chunk blocks + entities"]
  SIM --> DEC["decoration.7dt<br/>DecoObject records"]
  SIM --> PWR["power.dat<br/>PowerManager root forest"]
  SIM --> FAC["factions.dat"]
  SIM --> PLR["player files<br/>profile, inventory, journal"]
  SIM --> PRE["prefabs.xml<br/>POI decorations"]
  SIM --> DM["dynamic mesh .group<br/>deflate-compressed"]
```

Note the trap the corpus documents: the dynamic-mesh `.group` writer people expect
(`DynamicMeshFile.WriteRegion`, version 160) is **dead code**; the live path is
deflate-compressed through `DynamicMeshRegionDataStorage.SaveRegion`.

---

## 7. Subsystem ownership map

Which doc owns which box above. Use this as the navigation index.

```mermaid
flowchart TB
  subgraph M[Meta and method]
    m1[re-methodology] --- m2[coverage] --- m3[full-surface] --- m4[residuals]
  end
  subgraph L[Loop]
    l1[loop] --- l2[loop-gmupdate] --- l3[managers]
  end
  subgraph N[Wire]
    n1[protocol] --- n2[protocol-packages] --- n3[protocol-frames] --- n4[network] --- n5[platform-auth]
  end
  subgraph W[World]
    w1[world-chunks] --- w2[chunk-providers] --- w3[world-generation] --- w4[terrain-height]
    w5[save-region] --- w6[save-persistence] --- w7[light-mesh-water] --- w8[dynamic-mesh]
  end
  subgraph E[Entities]
    e1[entity-ai] --- e2[uai] --- e3[aidirector] --- e4[spawning]
    e5[entity-stats] --- e6[buffs] --- e7[combat-damage] --- e8[stealth-smell] --- e9[raycast-pathing]
  end
  subgraph G[Gameplay]
    g1[blocks] --- g2[block-shapes] --- g3[items] --- g4[crafting-recipes]
    g5[loot-economy] --- g6[quests-challenges] --- g7[progression] --- g8[minevents]
    g9[game-events] --- g10[tile-entities-power] --- g11[vehicles-drones-turrets] --- g12[npc-dialog]
  end
  subgraph O[Ops and edges]
    o1[server-lifecycle] --- o2[console-commands] --- o3[webserver] --- o4[mod-loading]
    o5[sandbox-options] --- o6[server-browser-prefabs] --- o7[chat] --- o8[parties-factions]
    o9[twitch-integration] --- o10[signs] --- o11[map-objects] --- o12[experimental-delta]
  end
```

Full per-doc index with audit status: [`coverage.md`](coverage.md). Leaf catalogs and
generated inventories: [`INDEX.md`](INDEX.md).

---

## 7b. Every modelled lifecycle

The diagrams above are the system's skeleton. The behaviour lives in **74 state
machines** spread across 42 docs, indexed in
[`inventories/state-machines.md`](inventories/state-machines.md) and grouped there by
the same clusters used below.

```mermaid
flowchart TB
  SM["74 state machines"] --> C1["Gameplay systems<br/>27"]
  SM --> C2["Ops, admin, integrations<br/>15"]
  SM --> C3["Entities, AI, combat<br/>14"]
  SM --> C4["World, chunks, persistence<br/>10"]
  SM --> C5["Frame and lifecycle<br/>4"]
  SM --> C6["Wire and session<br/>4"]
  C1 --> G1["quests, loot, power, items,<br/>crafting, game events, vehicles"]
  C2 --> G2["console, webserver, mods,<br/>parties, twitch, server lifecycle"]
  C3 --> G3["buffs, damage, death, AI run gate,<br/>UAI cycle, spawning, drone states"]
  C4 --> G4["chunk load, save, dynamic mesh,<br/>weather, world gen"]
  C5 --> G5["gmUpdate phases, tick slice,<br/>manager chain, boot"]
  C6 --> G6["join handshake, encryption,<br/>chat routing, interest"]
```

The index is regenerated by `tools/src/StateMachines`, so a new diagram appears in it
automatically and a removed one disappears. It indexes the docs rather than
re-deriving the machines, so each entry is only as good as its owning doc.

---

## 8. What is deliberately NOT on this map

A headless server never runs these, so they appear nowhere above even though the
assembly contains them: client UI (`XUi*`/NGUI), rendering and meshing for display,
audio and dynamic music, input, the Discord Social SDK, and the prefab/world editor.
The boundary is enumerated in
[`out-of-scope-surface.md`](out-of-scope-surface.md), and the reachability caveats
(why some of that code still shows up in a static call graph) are in
[`inventories/coverage-report.md`](inventories/coverage-report.md).

---

## Related docs

| Doc | Role |
|---|---|
| [INDEX.md](INDEX.md) | Hub: every doc, grouped |
| [coverage.md](coverage.md) | Per-doc audit status and family map |
| [loop.md](loop.md) | The frame in depth |
| [protocol.md](protocol.md) | Wire framing and join in depth |
| [full-surface.md](full-surface.md) | Whole-assembly namespace map |
| [out-of-scope-surface.md](out-of-scope-surface.md) | What the server does not run |

## Changelog

- **2026-07-26:** Initial whole-system visual map (layers, boot, frame phases, sim core, wire conversation, persistence, ownership index), drawn from the existing IL-derived narratives.
