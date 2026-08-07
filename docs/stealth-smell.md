# Stealth, noise, and smell (dedicated V3.1.0)

**Owns:** the server-authoritative detection-input system: `PlayerStealth`
(light-based stealth, accumulated noise, and the item/blood/food smell that attracts
zombies), the values that feed sleeper/zombie sensing, and their net sync.
**Not:** the AI decision that consumes them ([entity-ai.md](entity-ai.md) CanSee /
sleeper wake); the stealth HUD meter (client); XML tuning content.
**Evidence:** `PlayerStealth` IL (`TickServer` 430, `SmellTickServer` 257; dump
locally with `tools/src/DumpMethod`, git-ignored). **Hub:** [`INDEX.md`](INDEX.md).
**Method:** [`re-methodology.md`](re-methodology.md).

The server computes every player's visibility, audibility, and scent each tick;
those are the inputs zombie and sleeper AI use to detect and hunt the player, so
this is a core per-tick dedicated codepath.

---

## 1. Model

Each `EntityPlayer` has a `PlayerStealth` (`Init(player)`). It maintains three
things, all computed on the server in `TickServer` and fanned to the owning client:

| Value | Method | Meaning |
|---|---|---|
| **Light level** (`_lightlevel`) | `TickServer` | How visible the player is (ambient + held light) |
| **Noise volume** (`_noiselevel`) | `CalcVolume` + `NotifyNoise`/`AddNoise` | How audible recent actions are (accumulated events that decay) |
| **Smell radius** | `SmellTickServer` | How far the player's scent attracts zombies |

`SetClientLevels(lightLevel, noiseVolume, isAlert)` pushes the computed stealth to
the client (the HUD meter, `ValuePercentUI` / `ValueColorUI` / `SetBarColor`);
`Read`/`Write` persist and net-sync the state.

**Ambient light source:** `Entity.GetBrightness(t)` (IL=53) samples the light at
a head-ish point: it resolves the chunk from `position` (a missing chunk
returns 0), samples at
`floor(pos.y - yOffset + (boundingBox.max.y - boundingBox.min.y) * 0.66)` -
66% up the entity's bounding box - and returns
`world.GetLightBrightness(...)` (the chunk light grid from
[`light-mesh-water.md`](light-mesh-water.md)).

---

## 2. Stealth and detection (state machine)

`TickServer` resolves the current light + noise into a stealth value; sleeper and
zombie AI read it (e.g. `CanSleeperAttackDetect(entity)`) to decide whether the
player is noticed. High light or a loud noise event raises detectability toward
`isAlert`.

```mermaid
stateDiagram-v2
  [*] --> Hidden
  Hidden --> Hidden: TickServer -> low light + noise decays (NoiseCleanup)
  Hidden --> Noticeable: high _lightlevel (lit area / light source) or NotifyNoise event
  Noticeable --> Detected: CanSleeperAttackDetect true -> sleeper wakes / zombie senses (entity-ai.md)
  Noticeable --> Hidden: move to shadow + noise decays
  Detected --> Alert: isAlert -> AI hunts (SetBarColor red)
  Alert --> Noticeable: break line-of-sight + quiet down
  Alert --> Detected: still sensed
```

Noise is event-driven: actions call `NotifyNoise(volume, duration)`, which
`AddNoise` queues with a tick lifetime; `CalcVolume` sums the live events and
`NoiseCleanup` expires them, so a single loud action (gunshot, sprint) spikes
audibility then fades.

**`PlayerStealth.NotifyNoise(volume, duration)` (IL=71)** is the intake behind
that chain: `volume <= 0` returns false. It queues the event
(`AddNoise(noises, volume, (int)(duration * 20))` ticks); a `volume >= 11`
event arms `sleeperNoiseWaitTicks = 20`. For the sleeper side the volume is
shaped - `v = volume`, but `volume > 60` becomes
`60 + (volume - 60) ^ 1.4` (superlinear for very loud events) - then scaled by
passive **88** via `EffectManager.GetValue` and accumulated into
`sleeperNoiseVolume`. The return value is the sleeper-wake signal: true once
the accumulator reaches **360** (clamped), which is what makes
`AIDirector.NotifyNoise` call `world.CheckSleeperVolumeNoise`.

**`PlayerStealth.AddNoise(list, volume, ticks)` (IL=35)** keeps the event list
sorted by **descending volume**: it walks until the first entry with volume
`<=` the new event and inserts there (append when the new event is smallest).
`CalcVolume` reads the head of this sorted list, so the loudest live events
dominate the audible level.

**`PlayerStealth.CalcVolume()` (IL=68)** is the audible-level formula: it sums
the event volumes with **geometric decay** (`sum = Σ noises[i].volume × 0.6^i`,
the i-th entry weighted `0.6^i`), then shapes the stored `noiseVolume` as
`((sum × 2.35) ^ 0.86) × 1.5`, finally scaled by passive **88** via
`EffectManager.GetValue`. The method returns the raw weighted `sum`; the shaped
value feeds the detection thresholds.

**`PlayerStealth.NoiseCleanup()` (IL=43)** is the expiry sweep: it walks the
noise list and decrements each entry's `ticks`, removing entries once they
reach **1** - the fade-out half of the event-driven lifecycle.

---

## 3. Smell and attraction (state machine)

`SmellTickServer` builds a smell radius from what the player carries and does, and
`AttractTickServer` pulls nearby zombies toward a heavily-scented player. Smell
grows from carried food/raw meat items (`SmellCountItems`, `SmellUpdateItemsAndBlood`),
bleeding (`SmellUpdateItemsAndBlood`), eating (`SmellTickEat` / `SetSmellEat`), and
wetness (`SmellTickWet`); being sheltered reduces it.

**`PlayerStealth.SmellCountItems()` (IL=110)** is the carried-smell total: it
sums `ItemClass.Smell * count` over the drag-and-drop window stack (local
player UI), every non-empty toolbelt slot, and every non-empty bag slot, then
clamps the sum to **50** and returns it as an int.

```mermaid
stateDiagram-v2
  [*] --> Odorless
  Odorless --> Building: SmellCountItems / bleeding / eating / wet -> SetSmellRadiusTarget
  Building --> Smelly: radius grows toward target (SmellCountToRadius)
  Smelly --> Attracting: AttractTickServer -> zombies in radius drawn in (SmellApplyMode)
  Smelly --> Fading: drop smelly items / stop eating / sheltered -> SmellClear
  Fading --> Odorless
  Attracting --> Fading: scent source removed
```

`SetSmellRadiusTarget(radius, eating, sheltered)` sets the goal radius; the actual
radius eases toward it, so stashing raw meat or getting indoors shrinks the scent
over time rather than instantly.

---

## 4. Dedicated relevance and residuals

- **Per-tick dedicated path:** `TickServer`, `SmellTickServer`, and
  `AttractTickServer` run on the server for every player; the results are the
  authoritative detection inputs for AI.
- **Consumer:** zombie/sleeper sensing in [entity-ai.md](entity-ai.md) reads the
  stealth value and `CanSleeperAttackDetect`.
- **Residual / client:** the stealth HUD meter and bar color (client); light-probe
  sampling detail; XML stealth/smell tuning is content.

---

## Related docs

| Doc | Role |
|---|---|
| [entity-ai.md](entity-ai.md) | AI sensing/CanSee that consumes stealth; sleeper wake |
| [items.md](items.md) | Carried items that generate smell |
| [buffs.md](buffs.md) | Buffs/perks that modify stealth (from progression) |
| [weather-environment.md](weather-environment.md) | Wetness that affects smell |
| [spawning.md](spawning.md) | Sleeper volumes woken by detection |

## Changelog

- **2026-08-07:** PlayerStealth.SmellCountItems (IL=110): ItemClass.Smell *
  count over drag + toolbelt + bag, clamp 50, int return.
- **2026-08-07:** Entity.GetBrightness (IL=53): ambient light sample at 66%
  box height (pos.y - yOffset + height*0.66), missing chunk -> 0.
- **2026-08-07:** PlayerStealth.NoiseCleanup (IL=43): per-entry ticks
  decrement, remove at 1 - the fade-out half of the noise lifecycle.
- **2026-08-07:** PlayerStealth.CalcVolume (IL=68): sum with 0.6^i geometric
  weights, stored noiseVolume = ((sum*2.35)^0.86)*1.5 * passive 88; returns
  raw weighted sum.
- **2026-08-07:** PlayerStealth.AddNoise (IL=35): volume-descending insertion
  into the event list - CalcVolume reads the head so loudest events dominate.
- **2026-08-07:** PlayerStealth.NotifyNoise (IL=71): volume<=0 false, AddNoise
  duration*20 ticks, volume>=11 arms sleeperNoiseWaitTicks=20, >60 superlinear
  60+(v-60)^1.4, passive 88 scale, sleeperNoiseVolume >= 360 true (sleeper-wake
  signal).
- **2026-07-23:** Initial stealth/noise/smell reversal (PlayerStealth server tick, light+noise detection, item/blood/food smell attraction) with state machines.
