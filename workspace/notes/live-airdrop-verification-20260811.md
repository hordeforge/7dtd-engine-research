# Live airdrop verification - 2026-08-11 (V3.1.0 b14 dedicated)

## Setup

- Stock dedicated server (loadgen wrapper `start_dedicated_navezgane.sh`,
  `RE_GAME_NAME=AirDropProbe`, `RE_DEDICATED_USERDATA=.../7dtd-loadgen-airdrop`,
  `RE_MAX_ZOMBIES=16`), Navezgane, telnet 8081 (password `retest`).
- World-time control: telnet `settime <day> <hour> <minute>` (1-based day;
  1- or 3-arg forms only, 4 args rejected). `gettime` reads it back.
- World time is **paused with zero connected players**; a connected but **dead**
  bot does not count either (SpawnAirDrop needs an alive tracked player).
- DayNightLength 60 -> ~400 world-time units per real second.

## Observed timeline (server log, game-seconds)

| Game time | Log line |
|---|---|
| 22.970 / 22.975 | `WRN Next Airdrop: 4 12:00` (init schedule: day 1 + gap 3) |
| 32.391 | `WRN Next Airdrop: 4 12:00` (frequency recompute) |
| 675.318 | `INF RequestToSpawnPlayer: 309, REFake1, 5` (fresh alive bot) |
| 675.337 | `WRN Next Airdrop: 7 12:00` (drop fired at day 4 12:00; reschedule = 4 + gap 3) |
| 675.384 | `INF AIAirDrop: Computed flight paths for 1 aircraft.` |
| 675.384 | `INF AIAirDrop: Waiting for supply crate chunk locations to load...` |
| 688.254 | `INF AIAirDrop: Spawned aircraft at ((1879.3, 241.0, 460.0)), heading ((-0.5, 0.8))` |
| 693.057 | `INF AIAirDrop: Spawned supply crate at (1572.2, 231.0, 936.3)` |
| 701.917 | `INF [ScriptOrder] entity 423 EntitySupplyCrate goActive=True` |

## Confirmed facts (see aidirector.md / dedicated-misc-systems.md)

- Schedule: `nextDay = WorldTimeToDays(t) + RandomRange(MinDayCount, MaxDayCount+1) - 1`,
  `nextTOD = RandomRange(MinTimeOfDay, MaxTimeOfDay+1)`, defaults 3/3/12000/12000.
- Gap is in {2, 3} days, not exactly 2: `GameRandom.Sample()` can be exactly
  1.0 (full-scale InternalSample), so `Next(1)` can draw 1 and
  `RandomRange(3, 4)` can return 4. Both observed draws hit 4.
- Drop requires at least one alive tracked player (`SpawnAirDrop` IL=59).
- `AirDropFrequency` (stat 51 / pref) is a no-op: no reader in the assembly,
  drop fired with it at 0.

## Teardown

Server killed via `dedicated.pid`; ports 26900/26902/8081 closed; no stray
processes. Probe userdata left in `~/.cache/7dtd-loadgen-airdrop/`.
