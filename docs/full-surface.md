# Whole-assembly surface map and coverage ledger (V3.0.1)

**Owns:** the 100%-of-the-assembly structural map (every namespace, with type /
method / IL counts) and the honest ledger of how much has a hand-written narrative.
**Not:** the IL bodies themselves (policy: not redistributed, see below).
**Regenerate:** `tools/src/FullSurface` (committed metadata) + `tools/src/DumpAll`
(full local IL). **Hub:** [`INDEX.md`](INDEX.md).

## Scope and the two hard limits on "document 100% in minute detail"

The shipped `Assembly-CSharp.dll` is **7,413 types (incl. nested), 53,011 methods with bodies,
1,734,742 IL instructions**, across 87 namespaces (regenerate with
`tools/src/Census` and `FullSurface`). Two constraints shape what this repo can
honestly hold:

1. **Redistribution / copyright.** A complete minute-detail transcription of
   1.73M IL instructions is a full copy of The Fun Pimps' proprietary game. This
   repo's standing policy (README, [`../il/README.md`](../il/README.md),
   [`../AGENTS.md`](../AGENTS.md)) is: **no game code or bulk IL is distributed;
   docs quote at most a few disassembly lines for commentary.** So the full IL is
   dumped **locally and git-ignored** (`il/`, regenerable from your own game copy),
   never committed. What is committed is *metadata about* the code (this map,
   signatures, sizes, call graphs) and *transformative analysis* (the narratives).
2. **Effort.** Hand-written minute detail for 53k methods is a multi-person-year
   effort, not a single pass. This ledger makes coverage a tracked, incremental
   goal rather than a false "done" claim.

**How to reverse 100% locally** (nothing here ships game bytes):

```bash
cd tools && ./build.sh
ASM="$HOME/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll"
mono bin/FullSurface.exe "$ASM" ../il/surface-v3.0.1          # committable metadata
mono bin/DumpAll.exe    "$ASM" ../il/full-v3.0.1              # full IL, git-ignored (all 7413 types)
mono bin/DumpAll.exe    "$ASM" ../il/full-v3.0.1 GamePath     # or one namespace
```

`il/full-v3.0.1/` after a full run is the 100% reversal: one `<Type>.il.txt` per
type, every method body. It is git-ignored on purpose.

## The assembly by functional cluster

All 87 namespaces grouped by role. Counts are methods-with-body / IL from
`surface-namespaces.md` (regenerate to refresh). `<global>` (6,276 types /
45,222 methods / 1.52M IL) is 85% of the code and is split by subsystem in the
narrated docs below, not by namespace.

| Cluster | Namespaces | Coverage status |
|---|---|---|
| **Dedicated sim core** | `<global>` (GameManager, World, Chunk*, Entity*, EntityAlive, Tick*, managers, save) | **Narrated** for the dedicated hot path (see ledger); rest of `<global>` enumerated in `il/surface-v3.0.1/surface-types.md` (local) |
| **Networking / wire** | `<global>` NetPackage*/ConnectionManager/NetEntity* | **Narrated** (protocol, protocol-frames, protocol-packages, network): 193 packages + framing + encryption |
| **Pathfinding** | `GamePath`, `RaycastPathing` | **Narrated** ([entity-ai.md](entity-ai.md) §6 ASP wrapper, [closed-gaps.md](closed-gaps.md) ASP->A*); Aron Granberg A* library internals third-party residual |
| **Utility AI** | `UAI` | **Narrated** ([uai.md](uai.md)): packages, considerations, tasks, decision/selection cycle |
| **World generation** | `WorldGenerationEngineFinal`, `PrefabVolumes`, `SDF` | **Narrated** ([world-generation.md](world-generation.md)); `MapRendering`/clipping tools client-render residual |
| **Content: events / quests / challenges** | `GameEvent.*`, `Quests`, `Challenges` | **Narrated** ([game-events.md](game-events.md), [quests-challenges.md](quests-challenges.md)) |
| **Audio / music** | `Audio`, `DynamicMusic*` (5 ns), `MusicUtils*`, `mumblelib`, `TriggerEffects` | Out of dedicated scope (client-only) |
| **Twitch integration** | `Twitch*` (3 ns) | **Narrated** ([twitch-integration.md](twitch-integration.md)) for the server action/vote slice; connection client-hosted residual |
| **Web admin API** | `Webserver*` (14 ns) | **Narrated** ([webserver.md](webserver.md)): pipeline, auth/session, permissions, REST host, SSE |
| **Data / XML pipeline** | `XMLData.*` (6 ns), `XMLEditing` | Not narrated (content parse; XML semantics are content, not loop IL) |
| **Platform / auth / transport** | `Platform.*` (14 ns incl EOS/Steam/XBL/PSN/LAN) | **Narrated** ([platform-auth.md](platform-auth.md)) for the server auth path; native SDK crypto/anticheat residual |
| **Rendering / graphics libs** | `SharpEXR*` (4 ns), `JBooth.MicroSplat`, `PI.NGSS`, `PostEffects`, `ShinyScreenSpace*`, `GearVariants`, `GUI_2`, `Assets.DuckType.Jiggle` | Out of dedicated scope (client render) |
| **Character controller / physics** | `KinematicCharacterController` | Client/movement; server uses the character-controller path (entity-ai) |
| **Analytics / services / modinfo** | `Services*`, `Services.Analytics.Events`, `ModInfo` | Not narrated (telemetry / metadata) |
| **Bundled third-party libraries** | `UniLinq`, `ICSharpCode.WpfDesign.XamlDom`, `ConcurrentCollections`, `Microsoft.CodeAnalysis`, `SandboxOptions`, `System.*` | Not game logic (vendored libs); out of scope by definition |

Per-namespace counts: `il/surface-v3.0.1/surface-namespaces.md` (regenerate).
Per-type inventory (all 7,413, names + sizes, no bodies): `surface-types.md` (local).

## Coverage ledger (hand-written narrative)

The narrated corpus targets **the dedicated-relevant managed surface** (the
project's stated bar, [`coverage.md`](coverage.md)), which is the dedicated sim
core + wire protocol, a small but load-bearing slice of the 7,413 types.

| Subsystem | Narrative | Depth |
|---|---|---|
| Frame / sim loop | [loop.md](loop.md), [loop-gmupdate.md](loop-gmupdate.md) | Deep (gmUpdate 631 IL fully mapped) |
| Entities / AI / path | [entity-ai.md](entity-ai.md), [aidirector.md](aidirector.md), [closed-gaps.md](closed-gaps.md) | Deep (tick chain, thresholds, EAI) |
| World / chunks | [world-chunks.md](world-chunks.md) | Deep |
| Terrain / height | [terrain-height.md](terrain-height.md) | Deep |
| Save / region | [save-region.md](save-region.md) | Deep (SaveLoad 884 IL) |
| Light / mesh / water | [light-mesh-water.md](light-mesh-water.md) | Deep |
| Managers / ModEvents | [managers.md](managers.md) | Method-level |
| Networking / wire | [network.md](network.md), [protocol.md](protocol.md), [protocol-frames.md](protocol-frames.md), [protocol-packages.md](protocol-packages.md) | Deep (193 packages, framing, encryption) |
| Web admin server | [webserver.md](webserver.md) | Deep (HTTP pipeline, auth/session, permissions, REST, SSE) |
| Console / telnet admin | [console-commands.md](console-commands.md) | Deep (registry, dispatch, permission gate, telnet auth) |
| Server lifecycle / persistence | [server-lifecycle.md](server-lifecycle.md) | Deep (boot, game state + **game modes** §2.1, player data, land claims, shutdown) |
| Buffs / effects | [buffs.md](buffs.md) | Deep (tick lifecycle, duration/stack, net sync) |
| Game events / scripted content | [game-events.md](game-events.md) | Deep (sequence/action/requirement/decision/loop state machines) |
| Platform auth / join | [platform-auth.md](platform-auth.md) | Deep (identity, server auth flow, EAC/EOS managed boundary) |
| Entity spawning | [spawning.md](spawning.md) | Deep (5 spawn sources, caps/attrition, observer-gated client spawn) |
| Tile entities + power | [tile-entities-power.md](tile-entities-power.md) | Deep (TE storage/tick, power graph 6.25Hz, crafting, traps) |
| Chat / system messages | [chat.md](chat.md) | Deep (wire, channel routing, system messages) |
| Vehicles / drones / turrets | [vehicles-drones-turrets.md](vehicles-drones-turrets.md) | Deep (registries, motion authority, drone/turret state machines) |
| World generation (RWG) | [world-generation.md](world-generation.md) | Deep (WorldBuilder stage pipeline, threading, outputs) |
| Weather / environment | [weather-environment.md](weather-environment.md) | Deep (server sim, storm machine, temperature survival) |
| Crafting / recipes | [crafting-recipes.md](crafting-recipes.md) | Deep (recipe model, validation, queue, unlock) |
| MinEvent triggered effects | [minevents.md](minevents.md) | Deep (FireEvent dispatch, 111 triggers, action/target/requirement model) |
| Loot / traders / economy | [loot-economy.md](loot-economy.md) | Deep (loot gen/respawn, trader restock/hours/pricing, vending) |
| Quests / challenges | [quests-challenges.md](quests-challenges.md) | Deep (template/instance, objective + reward lifecycles) |
| Progression / skills | [progression.md](progression.md) | Deep (XP/level-up, perk purchase, calculated level) |
| Blocks framework | [blocks.md](blocks.md) | Deep (BlockValue bitfield, virtual surface, damage/upgrade, change flow) |
| Entity / survival stats | [entity-stats.md](entity-stats.md) | Deep (health/food/water/stamina over-time, starvation) |
| Stealth / noise / smell | [stealth-smell.md](stealth-smell.md) | Deep (server light/noise/smell detection inputs) |
| Items framework | [items.md](items.md) | Deep (ItemValue packing, ItemAction contract, use/durability, inventory) |
| Combat / damage | [combat-damage.md](combat-damage.md) | Deep (DamageSource, apply pipeline, death/kill) |
| Twitch integration | [twitch-integration.md](twitch-integration.md) | Server slice (action/vote execution via game events); connection client residual |
| Mod loading / ModEvents | [mod-loading.md](mod-loading.md) | Deep (load pipeline, EAC gate, hook lifecycle) |
| Experimental delta (vs V3.0.1) | [experimental-delta.md](experimental-delta.md) | NetPackageTileEntity wire change + held-entity feature |
| Dynamic mesh | [dynamic-mesh.md](dynamic-mesh.md) | Deep (server regen threading, persistence, channel-1 flow control) |
| Parties / factions / allies | [parties-factions.md](parties-factions.md) | Deep (party lifecycle, faction standing matrix, ally handshake) |

**Honest coverage (dedicated subsystems narrated + leaves enumerated):** every
major subsystem a headless server runs is hand-narrated, and its leaf families are
enumerated in the catalogs. That spans the hot path (loop, entity/AI,
world/chunks/terrain/save, wire protocol) **and** the full server surface:
lifecycle/boot/persistence + game modes, platform auth, console/telnet, web admin,
chat, spawning, buffs, entity/survival stats, combat/damage, blocks, items,
crafting, loot/traders, tile-entities + power, vehicles/drones/turrets, weather,
progression, game events, quests/challenges, MinEvent effects, utility AI, world
generation, and the server slice of Twitch. See the ledger table above (23 new
narratives this pass, 158 diagrams corpus-wide).

**Caveat (not "every method"), with the honest numbers.** The reachability pass
reaches ~45k methods / 3,775 game types, far more than any per-method narration could
cover. As of the current [coverage report](inventories/coverage-report.md):
**1,318 (35%) are narrated** in a narrative doc, 974 are catalogued only, 1,396 are
classified out of scope, and **0 are unaccounted**................ Server-side support and
utility code that the reachable set includes but no narrative singles out
(e.g. `Configuration.*` parsing, `StringParsers`, `TEFeatureAbs` helpers) is
captured at the framework level, not with a dedicated section each.

Read those numbers with the report's own caveats: the base over-includes client UI
(devirtualization is instantiation-blind) and under-includes reflection-instantiated
code, and "narrated" means a backticked mention, not necessarily an explanation. So
"complete" here means **the dedicated subsystems are narrated and their leaves
enumerated**, which is a much narrower claim than "the reachable surface is
documented". Earlier revisions of this file quoted a "100% accounted for" figure;
that number summed narration with out-of-scope triage over a distorted base and has
been withdrawn.

Individual leaf **blocks** (e.g. `BlockMine`, `BlockLiquidSource`, `BlockSpawnEntity`) and **tile-entity features** (`TEFeatureLandClaim`, ...) are instances of the documented `Block.UpdateTick` surface ([blocks.md](blocks.md)) and the tile-entity feature framework ([tile-entities-power.md](tile-entities-power.md)); the frameworks own them, so they are covered without a doc each.

**What is NOT narrated is genuinely not a dedicated codepath:** client rendering
(`SharpEXR`, `MicroSplat`, `PI.NGSS`, post effects, `MapRendering`, GUI), audio /
music, editor/clipping tools, and vendored third-party libraries. These are
enumerated in the surface map (`surface-types.md`) but do not run on a headless
server. Native residuals (LiteNetLib transport, EAC/EOS crypto + anticheat, Unity
physics/jobs, Aron Granberg A\*) are managed-wrapped where the server touches them
and listed in [residuals.md](residuals.md).

## Coverage roadmap (dedicated subsystems: done)

All dedicated-server **subsystems** are narrated and their leaves enumerated (see
the ledger). The remaining surface is out-of-scope by policy (client render, audio,
editor, vendored libs), native residual, or server-side support/utility code
captured at the enumeration level (see the caveat above); those are enumerated, not
hand-narrated, by design. Future work is
maintenance: after a game update, regenerate `Census` + `FullSurface`, diff the
per-namespace counts, and re-verify the affected narratives.

## Related docs

| Doc | Role |
|---|---|
| [coverage.md](coverage.md) | Dedicated-relevant managed family checklist |
| [residuals.md](residuals.md) | What managed IL cannot close |
| [re-methodology.md](re-methodology.md) | How to reverse any of the above |
| [`../tools/README.md`](../tools/README.md) | `FullSurface` + `DumpAll` + the dumpers |
| [`../il/README.md`](../il/README.md) | Why the full IL stays local |
