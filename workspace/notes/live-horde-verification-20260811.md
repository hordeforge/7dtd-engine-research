# Live wandering-horde verification - 2026-08-11 (V3.1.0 b14 dedicated)

## Setup

- Stock dedicated server (loadgen wrapper, `RE_GAME_NAME=HordeProbe`,
  `RE_DEDICATED_USERDATA=.../7dtd-loadgen-horde`, Navezgane), telnet 8081.
- One loadgen join bot; telnet `settime 5 0 0` (day 5 00:00, past the 28000
  world-time gate) then later `settime 5 23 0` (into the scheduled window).
- World time pauses with zero players; the bot drowns at Navezgane spawn in
  some sessions - a fresh join + immediate settime caught it alive.

## Observed timeline (game-seconds)

| Game time | Log line |
|---|---|
| 266.678 | `INF AIDirector: Wandering StartSpawning Horde` |
| 266.679 | `INF AIDirector: FindWanderingTargets at player '[type=EntityPlayer, name=EntityPlayer, id=239]', dist 53.66294` |
| 266.680 | `INF Party of 1, GS 1 (1), scaling 1, enemy max 5, bonus every 12` |
| 266.742 | `INF AIDirector: Spawned wandering horde (group wanderingHordeStageGS1, zombie [type=EntityZombie, name=zombieDarlene, id=352])` |
| 267.779 | `INF AIDirector: Spawned wandering horde (group wanderingHordeStageGS1, zombieBoe, id=407)` |
| 268.828 | `zombieDarlene id=408` |
| 269.877 | `zombieBoe id=409` |
| 270.938 | `zombieFemaleFat id=410` |
| 307.309 | `INF AIDirector: Wandering spawner finished Horde` |

## Confirmed facts (aidirector.md)

- The whole wandering-horde chain: world-time gate -> alive-player check ->
  `FindTargets` (~54 m target) -> gamestage group `wanderingHordeStageGS1` ->
  party-spawner scaling (GS 1, enemy max 5, bonus every 12) -> spawner finish.
- `settime <day> <hour> <minute>` jumps the world; the horde check runs on the
  next tick and fires when past the scheduled window with a living player.

## Teardown

Server killed via `dedicated.pid`; no stray processes/ports. Probe userdata in
`~/.cache/7dtd-loadgen-horde/`.
