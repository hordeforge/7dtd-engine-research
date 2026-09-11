# State machine index

**Kind:** generated catalog of every lifecycle modelled as a mermaid
`stateDiagram` in this corpus, grouped by subsystem cluster, with the section
that owns it. Use it to answer "is this lifecycle modelled, and where".  
**Regenerate:** `mono tools/bin/StateMachines.exe docs docs/inventories/state-machines.md`.  
**Scope note:** this indexes the docs, it does not re-derive the machines from IL.
Each diagram's correctness is the owning doc's, and the state counts below are
counted from the diagram source (nodes on the left of a transition), so a state
that is only ever a target reads one lower.  
**Hub:** [`../INDEX.md`](../INDEX.md). **Visual overview:** [`../meta/architecture-map.md`](../meta/architecture-map.md).

**74 state machines** across **41 docs**.

## Content and scripting (8)

| Lifecycle | Doc | States |
|---|---|---:|
| 2. Sequence lifecycle (state machine) | [content/game-events.md](../content/game-events.md) | 8 |
| 3. Action lifecycle (state machine) | [content/game-events.md](../content/game-events.md) | 10 |
| 5. Decisions and loops (nested control flow) | [content/game-events.md](../content/game-events.md) | 10 |
| 6. The action zoo: bases and representative leaves | [content/game-events.md](../content/game-events.md) | 3 |
| 2. Quest lifecycle (state machine) | [content/quests-challenges.md](../content/quests-challenges.md) | 5 |
| 3. Objective progress model (state machine) | [content/quests-challenges.md](../content/quests-challenges.md) | 4 |
| 6. Challenge lifecycle (state machine) | [content/quests-challenges.md](../content/quests-challenges.md) | 3 |
| 7. Challenge stages, groups, and daily rotation | [content/quests-challenges.md](../content/quests-challenges.md) | 4 |

## Entities, AI and pathing (9)

| Lifecycle | Doc | States |
|---|---|---:|
| 4. Net interest package selection (decoded) | [entities/closed-gaps.md](../entities/closed-gaps.md) | 7 |
| 2.0 Parent chain: `OnUpdateEntity` (IL=457) then `OnUpdateLive` (IL=363) | [entities/entity-ai.md](../entities/entity-ai.md) | 7 |
| Path request lifecycle | [entities/entity-ai.md](../entities/entity-ai.md) | 6 |
| 2. Survival over-time loop (state machine) | [entities/entity-stats.md](../entities/entity-stats.md) | 7 |
| 6b. The drone state machine | [entities/raycast-pathing.md](../entities/raycast-pathing.md) | 8 |
| 2. Stealth and detection (state machine) | [entities/stealth-smell.md](../entities/stealth-smell.md) | 4 |
| 3. Smell and attraction (state machine) | [entities/stealth-smell.md](../entities/stealth-smell.md) | 5 |
| 3.3 Cross-package selection: last positive package wins | [entities/uai.md](../entities/uai.md) | 7 |
| 5.1 `updateAction` and the `ActionData` flags | [entities/uai.md](../entities/uai.md) | 7 |

## Frame and lifecycle (3)

| Lifecycle | Doc | States |
|---|---|---:|
| 2. `gmUpdate` phases (631 IL, 6× IsDedicatedServer) | [loop/loop.md](../loop/loop.md) | 11 |
| 3.1 UpdateTick (150 IL) | [loop/loop.md](../loop/loop.md) | 11 |
| 2. ModEvents (managed hook surface) | [loop/managers.md](../loop/managers.md) | 13 |

## Gameplay systems (24)

| Lifecycle | Doc | States |
|---|---|---:|
| 2. Buff instance lifecycle (state machine) | [gameplay/buffs.md](../gameplay/buffs.md) | 6 |
| 2.3 `ProcessDamageResponseLocal` (IL=903) apply side effects | [gameplay/combat-damage.md](../gameplay/combat-damage.md) | 10 |
| 3.1a Kill XP server flow (V3.2.0 rework) | [gameplay/combat-damage.md](../gameplay/combat-damage.md) | 9 |
| 2. Craft lifecycle (state machine) | [gameplay/crafting-recipes.md](../gameplay/crafting-recipes.md) | 7 |
| 3. Recipe unlock progression | [gameplay/crafting-recipes.md](../gameplay/crafting-recipes.md) | 2 |
| 5. Holding and using an item (server flow) | [gameplay/items.md](../gameplay/items.md) | 8 |
| 5. Holding and using an item (server flow) | [gameplay/items.md](../gameplay/items.md) | 5 |
| 2. Loot container generation lifecycle (state machine) | [gameplay/loot-economy.md](../gameplay/loot-economy.md) | 6 |
| 3. Trader inventory restock (state machine) | [gameplay/loot-economy.md](../gameplay/loot-economy.md) | 3 |
| 4. Trader open hours and the physical area (state machine) | [gameplay/loot-economy.md](../gameplay/loot-economy.md) | 3 |
| 6. Vending machines | [gameplay/loot-economy.md](../gameplay/loot-economy.md) | 4 |
| 2. XP and level-up (state machine) | [gameplay/progression.md](../gameplay/progression.md) | 5 |
| 3. Perk purchase (state machine) | [gameplay/progression.md](../gameplay/progression.md) | 5 |
| 3. Per-chunk-area caps, cooldown, and kill attrition (`ChunkAreaBiomeSpawnData`) | [gameplay/spawning.md](../gameplay/spawning.md) | 5 |
| 5. Chunk-heat scouts and screamer hordes (state machine) | [gameplay/spawning.md](../gameplay/spawning.md) | 9 |
| 7. From decision to entity to client | [gameplay/spawning.md](../gameplay/spawning.md) | 8 |
| 3.4 Source on/off state and subtype tick table | [gameplay/tile-entities-power.md](../gameplay/tile-entities-power.md) | 5 |
| 4.3 `HandleRecipeQueue` / `cycleRecipeQueue` | [gameplay/tile-entities-power.md](../gameplay/tile-entities-power.md) | 6 |
| 5. Triggers and powered traps | [gameplay/tile-entities-power.md](../gameplay/tile-entities-power.md) | 5 |
| 5. Triggers and powered traps | [gameplay/tile-entities-power.md](../gameplay/tile-entities-power.md) | 5 |
| 4.2 The `Vehicle` model | [gameplay/vehicles-drones-turrets.md](../gameplay/vehicles-drones-turrets.md) | 4 |
| 5. Drones: follow, sentry, attack, heal | [gameplay/vehicles-drones-turrets.md](../gameplay/vehicles-drones-turrets.md) | 6 |
| 6.2 Powered turret block (AutoTurret) | [gameplay/vehicles-drones-turrets.md](../gameplay/vehicles-drones-turrets.md) | 3 |
| 2.1 Storm state machine (per biome) | [gameplay/weather-environment.md](../gameplay/weather-environment.md) | 4 |

## Meta and method (2)

| Lifecycle | Doc | States |
|---|---|---:|
| 2. Boot: process start to first tick | [meta/architecture-map.md](../meta/architecture-map.md) | 9 |
| Diagram convention | [meta/coverage.md](../meta/coverage.md) | 0 |

## Ops and admin (9)

| Lifecycle | Doc | States |
|---|---|---:|
| 2. Command dispatch (state machine) | [admin/console-commands.md](../admin/console-commands.md) | 12 |
| 3. Telnet connection (state machine) | [admin/console-commands.md](../admin/console-commands.md) | 6 |
| 2. Mod load-state (state machine) | [admin/mod-loading.md](../admin/mod-loading.md) | 7 |
| 3. Server join validation: the authorizer chain | [admin/platform-auth.md](../admin/platform-auth.md) | 6 |
| 1. Boot sequence (state machine) | [admin/server-lifecycle.md](../admin/server-lifecycle.md) | 9 |
| 2. Game state and rounds (`GameStateManager`) | [admin/server-lifecycle.md](../admin/server-lifecycle.md) | 4 |
| 3. Player join and persistence (state machine) | [admin/server-lifecycle.md](../admin/server-lifecycle.md) | 11 |
| 2. Authentication and session (state machine) | [admin/webserver.md](../admin/webserver.md) | 6 |
| 5. Server-Sent Events (SSE) lifecycle (state machine) | [admin/webserver.md](../admin/webserver.md) | 4 |

## Social and integration (5)

| Lifecycle | Doc | States |
|---|---|---:|
| 2. Server routing (state machine) | [social/chat.md](../social/chat.md) | 5 |
| 2.1 Membership lifecycle (state machine) | [social/parties-factions.md](../social/parties-factions.md) | 5 |
| 4. Faction and relationship model | [social/parties-factions.md](../social/parties-factions.md) | 5 |
| 5.1 Handshake (state machine) | [social/parties-factions.md](../social/parties-factions.md) | 4 |
| 2. Voting and action execution (state machine) | [social/twitch-integration.md](../social/twitch-integration.md) | 7 |

## Wire and session (2)

| Lifecycle | Doc | States |
|---|---|---:|
| 2. Entity replication (from UpdateTick) | [network/network.md](../network/network.md) | 8 |
| 5. Join sequence (server responsibilities) | [network/protocol.md](../network/protocol.md) | 11 |

## World, chunks, persistence (12)

| Lifecycle | Doc | States |
|---|---|---:|
| 5. Damage, upgrade, and downgrade lifecycle | [world/blocks.md](../world/blocks.md) | 9 |
| 7.3 Firing | [world/block-shapes.md](../world/block-shapes.md) | 3 |
| 3.6 Lifecycle | [world/chunk-providers.md](../world/chunk-providers.md) | 7 |
| 3.1 Builder processor lifecycle | [world/dynamic-mesh.md](../world/dynamic-mesh.md) | 7 |
| 5.2 The server send loop | [world/dynamic-mesh.md](../world/dynamic-mesh.md) | 9 |
| 1. Light | [world/light-mesh-water.md](../world/light-mesh-water.md) | 4 |
| 4.6 Apply thread and wire | [world/light-mesh-water.md](../world/light-mesh-water.md) | 5 |
| 3. `SaveDataUtils` lifecycle: manager and prefs selection | [world/save-persistence.md](../world/save-persistence.md) | 10 |
| 1.1 World save state machine (managed) | [world/save-region.md](../world/save-region.md) | 7 |
| 4.1 Chunk progress flags (stock `InProgress*` volatiles) | [world/world-chunks.md](../world/world-chunks.md) | 11 |
| 5.2 Network-mode `Chunk.write` body layout (V3.2.0) | [world/world-chunks.md](../world/world-chunks.md) | 5 |
| 4.1 Coroutine driver and worker task | [world/world-generation.md](../world/world-generation.md) | 8 |

## Changelog

- **2026-07-26:** Initial generated index of all modelled lifecycles.
