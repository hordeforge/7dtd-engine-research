# Entity and survival stats (dedicated V3.1.0)

**Owns:** the stat container and survival tick: `EntityStats` (base entity stats +
`Tick`), `PlayerEntityStats` (food / water / stamina / health over-time), and how
depletion drives damage.
**Not:** the felt-temperature / weather-survival cvar path (that is
[weather-environment.md](weather-environment.md)); the individual stat XML content;
the HUD (client).
**Evidence:** `EntityStats`, `PlayerEntityStats` IL (dump locally with
`tools/src/DumpMethod`, git-ignored). **Hub:** [`INDEX.md`](INDEX.md).
**Method:** [`re-methodology.md`](re-methodology.md).

Health, stamina, food, and water are simulated on the authoritative server entity,
so the survival loop is a per-tick dedicated codepath.

---

## 1. Model

| Type | Role |
|---|---|
| `EntityStats` | Base container on every `EntityAlive`: health and the core stats, `Tick(worldTime)` / `TickWait`, `Read`/`Write`, `UpdateSandboxOptions` (difficulty scaling) |
| `PlayerEntityStats` | Player extension adding the survival stats and their over-time updates (food, water, stamina, health regen) |

`EntityStats.Tick` runs on the server entity each sim step; `TickWait` handles the
throttled (per-`worldTime`) updates. Stats persist with the entity/player profile
([server-lifecycle.md](server-lifecycle.md)) and net-sync to the owning client.

### 1.1 `EntityStats.Tick` / `TickWait` phase machine (IL re-pin 2026-08-07)

**`Tick` (IL=27):** if entity remote **or** dead, return. Else `waitTicks++`; when
`waitTicks >= 10`, reset to 0. Always call `TickWait(worldTime)`.

**Base `TickWait` (IL=75)** uses `waitTicks` as a 10-phase round-robin (dt=0.5):

| waitTicks | Work |
|---:|---|
| 1 | `UpdateNPCStatsOverTime(0.5)` + `Health.Tick(0.5)` |
| 2 | if `Health.Changed` -> `SendStatChangePacket(Health)` + clear |
| 6 | net-sync wait: every 10 outer cycles, server sends
  `NetPackageEntityStatsBuff` flags **192**; client `SendToServer` |
| other | no-op in base |

**`PlayerEntityStats.TickWait` (IL=133)** expands the phases:

| waitTicks | Work |
|---:|---|
| 1 | `UpdateWeatherStats(0.5, worldTime, IsGodMode)` |
| 2 | `UpdatePlayerFoodOT` + `UpdatePlayerWaterOT` |
| 3 | `UpdatePlayerHealthOT` |
| 4 | `UpdatePlayerStaminaOT` |
| 5 | send changed Health/Stamina/Water/Food packets (`EnumStat` 0/1/8/7) |
| 6 | same `NetPackageEntityStatsBuff` cadence as base |

---

## 2. Survival over-time loop (state machine)

`PlayerEntityStats.TickWait` fans into the per-stat over-time methods:
`UpdatePlayerFoodOT`, `UpdatePlayerWaterOT`, `UpdatePlayerStaminaOT`,
`UpdatePlayerHealthOT`, and `UpdateWeatherStats` (temperature, detailed in
[weather-environment.md](weather-environment.md)). Food and water deplete with
time and activity; when they bottom out, health takes over-time damage; when the
player is fed and hydrated, health regenerates.

```mermaid
stateDiagram-v2
  [*] --> Healthy
  Healthy --> Depleting: UpdatePlayerFoodOT / UpdatePlayerWaterOT drain over time
  Depleting --> Fed: eat / drink -> food/water restored
  Fed --> Healthy: food and water above threshold
  Depleting --> Starving: food or water reaches 0
  Starving --> HealthDamage: UpdatePlayerHealthOT applies over-time damage
  HealthDamage --> Fed: eat / drink -> stop damage
  HealthDamage --> Dead: health reaches 0 -> EntityAlive death (server-lifecycle player respawn)
  Fed --> Regen: UpdatePlayerHealthOT regenerates health when well-fed
  Regen --> Healthy
  Dead --> [*]
```

- **Stamina** (`UpdatePlayerStaminaOT`): drains on exertion (sprint, attack,
  mining) and regenerates when idle; gates actions that require stamina.
- **Food / water** (`UpdatePlayer{Food,Water}OT`): deplete on a timer plus activity;
  consumables (via [items.md](items.md) / [buffs.md](buffs.md)) restore them.
- **Health** (`UpdatePlayerHealthOT`): regenerates when fed/hydrated, takes damage
  when starving/dehydrated; also the target of combat and environmental damage.
- **Temperature / weather survival:** `UpdateWeatherStats` computes felt
  temperature; the survival-cvar to buff path is documented in
  [weather-environment.md](weather-environment.md).

`UpdateNPCStatsOverTime` is the lighter non-player path (zombies/animals get the
base `EntityStats` tick without the full survival set).

---

## 3. Client / server split (honest)

The **authoritative stat values** (health, and the survival totals that gate death
and damage) live on the server entity and are net-synced. Some **felt-value
computation** (felt temperature, and the survival cvars weather turns into buffs)
runs on the owning client and is fed back, as documented in
[weather-environment.md](weather-environment.md); several felt-temperature helper
getters are stubbed on this dedicated build (see that doc). This doc owns the
server-side stat container and the food/water/stamina/health over-time model.

---

## 4. Dedicated relevance and residuals

- **Per-tick dedicated path:** every player's survival stats tick on the server;
  starvation damage and death are server-authoritative.
- **Residual / content:** the felt-temperature getters stubbed on the dedicated
  binary (weather doc); stat definitions and consumable effects are XML content;
  the HUD is client.

---

## 5. Network sync (verified)

| Package | Role |
|---|---|
| `NetPackageEntityStatChanged` | single stat value/baseMax/maxModifier + instigator |
| `NetPackageEntityStatsBuff` | full `EntityBuffs` blob for one entity |
| `NetPackagePlayerStats` | `EntityNetworkStats` snapshot (NED dirty path) |

Wire bodies: [protocol-packages.md](protocol-packages.md) section 6.16. Server
rebroadcasts stats/buffs/playerstats with bulk flags **192** after accept.

## Related docs

| Doc | Role |
|---|---|
| [weather-environment.md](weather-environment.md) | Temperature / weather-survival cvar to buff path |
| [buffs.md](buffs.md) | Buffs that modify stats and apply survival effects |
| [items.md](items.md) | Consumables that restore food/water/health |
| [entity-ai.md](entity-ai.md) | The entity update that ticks stats |
| [server-lifecycle.md](server-lifecycle.md) | Stats persisted with the profile; death/respawn |

## Changelog

- **2026-08-07:** EntityStats/PlayerEntityStats waitTicks phase tables (Tick IL=27,
  TickWait base 75 / player 133).
- **2026-07-28:** Stat/buff/playerstats network package pointers.

- **2026-07-23:** Initial entity/survival stats reversal (EntityStats tick, food/water/stamina/health over-time, client/server split) with state machine.
