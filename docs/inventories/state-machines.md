# State machine index

**Kind:** generated catalog of every lifecycle modelled as a mermaid
`stateDiagram` in this corpus, grouped by subsystem cluster, with the section
that owns it. Use it to answer "is this lifecycle modelled, and where".  
**Regenerate:** `mono tools/bin/StateMachines.exe docs docs/inventories/state-machines.md`.  
**Scope note:** this indexes the docs, it does not re-derive the machines from IL.
Each diagram's correctness is the owning doc's, and the state counts below are
counted from the diagram source (nodes on the left of a transition), so a state
that is only ever a target reads one lower.  
**Hub:** [`../INDEX.md`](../INDEX.md). **Visual overview:** [`../architecture-map.md`](../architecture-map.md).

**74 state machines** across **41 docs**.

## Entities, AI, combat (14)

| Lifecycle | Doc | States |
|---|---|---:|
| 2. Buff instance lifecycle (state machine) | [buffs.md](../buffs.md) | 6 |
| 2.3 `ProcessDamageResponseLocal` (IL=903) apply side effects | [combat-damage.md](../combat-damage.md) | 10 |
| 3.1 `OnEntityDeath` (IL=146) / `dropItemOnDeath` (IL=105) | [combat-damage.md](../combat-damage.md) | 9 |
| 2.0 Parent chain: `OnUpdateEntity` (IL=457) then `OnUpdateLive` (IL=363) | [entity-ai.md](../entity-ai.md) | 7 |
| Path request lifecycle | [entity-ai.md](../entity-ai.md) | 6 |
| 2. Survival over-time loop (state machine) | [entity-stats.md](../entity-stats.md) | 7 |
| 6b. The drone state machine | [raycast-pathing.md](../raycast-pathing.md) | 8 |
| 3. Per-chunk-area caps, cooldown, and kill attrition (`ChunkAreaBiomeSpawnData`) | [spawning.md](../spawning.md) | 5 |
| 5. Chunk-heat scouts and screamer hordes (state machine) | [spawning.md](../spawning.md) | 9 |
| 7. From decision to entity to client | [spawning.md](../spawning.md) | 8 |
| 2. Stealth and detection (state machine) | [stealth-smell.md](../stealth-smell.md) | 4 |
| 3. Smell and attraction (state machine) | [stealth-smell.md](../stealth-smell.md) | 5 |
| 3.3 Cross-package selection: last positive package wins | [uai.md](../uai.md) | 7 |
| 5.1 `updateAction` and the `ActionData` flags | [uai.md](../uai.md) | 7 |

## Frame and lifecycle (4)

| Lifecycle | Doc | States |
|---|---|---:|
| 2. Boot: process start to first tick | [architecture-map.md](../architecture-map.md) | 9 |
| 2. `gmUpdate` phases (631 IL, 6× IsDedicatedServer) | [loop.md](../loop.md) | 11 |
| 3.1 UpdateTick (150 IL) | [loop.md](../loop.md) | 11 |
| 2. ModEvents (managed hook surface) | [managers.md](../managers.md) | 13 |

## Gameplay systems (27)

| Lifecycle | Doc | States |
|---|---|---:|
| 5. Damage, upgrade, and downgrade lifecycle | [blocks.md](../blocks.md) | 9 |
| 7.3 Firing | [block-shapes.md](../block-shapes.md) | 3 |
| 2. Craft lifecycle (state machine) | [crafting-recipes.md](../crafting-recipes.md) | 7 |
| 3. Recipe unlock progression | [crafting-recipes.md](../crafting-recipes.md) | 2 |
| 2. Sequence lifecycle (state machine) | [game-events.md](../game-events.md) | 8 |
| 3. Action lifecycle (state machine) | [game-events.md](../game-events.md) | 10 |
| 5. Decisions and loops (nested control flow) | [game-events.md](../game-events.md) | 10 |
| 6. The action zoo: bases and representative leaves | [game-events.md](../game-events.md) | 3 |
| 5. Holding and using an item (server flow) | [items.md](../items.md) | 8 |
| 5. Holding and using an item (server flow) | [items.md](../items.md) | 5 |
| 2. Loot container generation lifecycle (state machine) | [loot-economy.md](../loot-economy.md) | 6 |
| 3. Trader inventory restock (state machine) | [loot-economy.md](../loot-economy.md) | 3 |
| 4. Trader open hours and the physical area (state machine) | [loot-economy.md](../loot-economy.md) | 3 |
| 6. Vending machines | [loot-economy.md](../loot-economy.md) | 4 |
| 2. XP and level-up (state machine) | [progression.md](../progression.md) | 5 |
| 3. Perk purchase (state machine) | [progression.md](../progression.md) | 5 |
| 2. Quest lifecycle (state machine) | [quests-challenges.md](../quests-challenges.md) | 5 |
| 3. Objective progress model (state machine) | [quests-challenges.md](../quests-challenges.md) | 4 |
| 6. Challenge lifecycle (state machine) | [quests-challenges.md](../quests-challenges.md) | 3 |
| 7. Challenge stages, groups, and daily rotation | [quests-challenges.md](../quests-challenges.md) | 4 |
| 3.4 Source on/off state and subtype tick table | [tile-entities-power.md](../tile-entities-power.md) | 5 |
| 4.3 `HandleRecipeQueue` / `cycleRecipeQueue` | [tile-entities-power.md](../tile-entities-power.md) | 6 |
| 5. Triggers and powered traps | [tile-entities-power.md](../tile-entities-power.md) | 5 |
| 5. Triggers and powered traps | [tile-entities-power.md](../tile-entities-power.md) | 5 |
| 4.2 The `Vehicle` model | [vehicles-drones-turrets.md](../vehicles-drones-turrets.md) | 4 |
| 5. Drones: follow, sentry, attack, heal | [vehicles-drones-turrets.md](../vehicles-drones-turrets.md) | 6 |
| 6.2 Powered turret block (AutoTurret) | [vehicles-drones-turrets.md](../vehicles-drones-turrets.md) | 3 |

## Ops, admin, integrations (14)

| Lifecycle | Doc | States |
|---|---|---:|
| 4. Net interest package selection (decoded) | [closed-gaps.md](../closed-gaps.md) | 7 |
| 2. Command dispatch (state machine) | [console-commands.md](../console-commands.md) | 12 |
| 3. Telnet connection (state machine) | [console-commands.md](../console-commands.md) | 6 |
| Diagram convention | [coverage.md](../coverage.md) | 0 |
| 2. Mod load-state (state machine) | [mod-loading.md](../mod-loading.md) | 7 |
| 2.1 Membership lifecycle (state machine) | [parties-factions.md](../parties-factions.md) | 5 |
| 4. Faction and relationship model | [parties-factions.md](../parties-factions.md) | 5 |
| 5.1 Handshake (state machine) | [parties-factions.md](../parties-factions.md) | 4 |
| 1. Boot sequence (state machine) | [server-lifecycle.md](../server-lifecycle.md) | 9 |
| 2. Game state and rounds (`GameStateManager`) | [server-lifecycle.md](../server-lifecycle.md) | 4 |
| 3. Player join and persistence (state machine) | [server-lifecycle.md](../server-lifecycle.md) | 11 |
| 2. Voting and action execution (state machine) | [twitch-integration.md](../twitch-integration.md) | 7 |
| 2. Authentication and session (state machine) | [webserver.md](../webserver.md) | 6 |
| 5. Server-Sent Events (SSE) lifecycle (state machine) | [webserver.md](../webserver.md) | 4 |

## Wire and session (4)

| Lifecycle | Doc | States |
|---|---|---:|
| 2. Server routing (state machine) | [chat.md](../chat.md) | 5 |
| 2. Entity replication (from UpdateTick) | [network.md](../network.md) | 8 |
| 3. Server join validation: the authorizer chain | [platform-auth.md](../platform-auth.md) | 6 |
| 5. Join sequence (server responsibilities) | [protocol.md](../protocol.md) | 11 |

## World, chunks, persistence (11)

| Lifecycle | Doc | States |
|---|---|---:|
| 3.6 Lifecycle | [chunk-providers.md](../chunk-providers.md) | 7 |
| 3.1 Builder processor lifecycle | [dynamic-mesh.md](../dynamic-mesh.md) | 7 |
| 5.2 The server send loop | [dynamic-mesh.md](../dynamic-mesh.md) | 9 |
| 1. Light | [light-mesh-water.md](../light-mesh-water.md) | 4 |
| 4.6 Apply thread and wire | [light-mesh-water.md](../light-mesh-water.md) | 5 |
| 3. `SaveDataUtils` lifecycle: manager and prefs selection | [save-persistence.md](../save-persistence.md) | 10 |
| 1.1 World save state machine (managed) | [save-region.md](../save-region.md) | 7 |
| 2.1 Storm state machine (per biome) | [weather-environment.md](../weather-environment.md) | 4 |
| 4.1 Chunk progress flags (stock `InProgress*` volatiles) | [world-chunks.md](../world-chunks.md) | 11 |
| 5.2 Network-mode `Chunk.write` body layout (V3.1.0) | [world-chunks.md](../world-chunks.md) | 5 |
| 4.1 Coroutine driver and worker task | [world-generation.md](../world-generation.md) | 8 |

## Changelog

- **2026-07-26:** Initial generated index of all modelled lifecycles.
