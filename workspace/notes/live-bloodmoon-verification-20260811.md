# Live blood-moon start verification - 2026-08-11 (V3.1.0 b14 dedicated)

## Setup

- Stock dedicated server (loadgen wrapper, `RE_GAME_NAME=BMProbe`, Navezgane),
  telnet 8081.
- `settime 7 21 59` applied while the world was **paused** (no players), then a
  loadgen bot joined: the sim advanced from 21:59 and crossed dusk (22:00) with
  the bot fresh-alive.

## Observed timeline (game-seconds)

| Game time | Log line |
|---|---|
| 24.539 | `INF BloodMoon SetDay: day 7, last day 0, freq 7, range 0` (bmDay computed at init) |
| 210.542 | `INF BloodMoon starting for day 7` |
| 210.544 | `INF Party of 1, GS 1 (1), scaling 1, enemy max 2, bonus every 12` |
| 210.544 | `INF Party members:` |
| 210.544 | `INF Player id 267, gameStage 1` |
| 236.788 | `INF BloodMoon starting for day 7` (re-log on the second join) |

## Confirmed facts (aidirector.md)

- The blood moon starts at dusk (22:00, `IsBloodMoonTime` with duskHour 22) on
  the computed bmDay (day 7 from `freq 7` - the loadgen config's
  `BloodMoonFrequency=0` still yielded freq 7 in the SetDay log).
- `StartBloodMoon` creates the party and logs the budget line: day-7 enemy max
  2 (vs the wandering horde's 5), bonus every 12.
- No BM zombies spawned before the bot drowned (Navezgane spawn water) - the
  start event is what was pinned.

## Teardown

Server killed via `dedicated.pid`; no stray processes/ports. Probe userdata in
`~/.cache/7dtd-loadgen-bm/`.
