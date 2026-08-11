# Tier-C continuous grind (8h target)

> **ARCHIVED (2026-08-11):** completed-session working notes (2026-08-07/08 grind). The live record is workspace/CHANGELOG.md; the current goal loop is the active TODO.

**Start:** 2026-08-07  
**Goal:** dump live V3.1.0 b14 IL → narrate high-value leaves → pin census → stock-check → commit; never-stop until interrupted.

## Loop
1. Dump batch of undoc/high-value methods
2. Skip already-narrated; document deltas only
3. Coverage + stock-check
4. Commit
5. Next batch

## In flight
- StartJumpSwimMotion (IL=131) water gate 0.65
- dropItemOnDeath, SetDead, NotifySleeperDeath
- ConditionalTriggerSleeperWakeUp
- SleeperVolume.Touch body (filter matched wrong overload)
- ProcessDamageResponseLocal residual holes

## Queues (rotate)
- entity-ai: wake, jump swim, ragdoll, see/cache
- combat: damage response holes, death drops
- sleeper: Touch full path
- net: rare package ProcessPackage
- managers: undoc tick leaves

## Commits this session
(append as we go)


## Progress log
- 95e87b6 StartJumpSwimMotion / KillLootContainer
- a33ebb7 DigUpdate phases
- bda930c CalcPartyLevel (spawning.md wipe bug)
- 2eff428 restore spawning.md
- SetRevengeTarget / IsInFrontOfMe next commit

- b089640 Push/area/side-step
- a36a49e door/entity/AttackPush
- next: SearchForDestroyPos commit


## Commits this session (partial)
- 6912ebf CanNavigatePath
- 02daace AddEnemyToWorld
- 89a6bb9 destroy-pos reuse
- 3d699ca BossEvent
- 2616b49 SearchForDestroyPos
- b089640 Push/area
- a36a49e door/entity
- e776463 IsAlert
- 577bc1c CheckBlocked


## Status checkpoint
- Commits since post-update dry-run (3b61d9c): 21+
- stock-check green; unaccounted 0
- Heavy EntityAlive/MoveHelper/package leaves closed this session
- Continue: remaining EntityAlive unmentioned (~100), World/GameManager leaves


## Checkpoint 2
- 25+ commits since dry-run
- stock-check green throughout
- Areas covered: MoveHelper full surface, EntityAlive helpers, World spawn/land/uncull, packages BossEvent
- Still open: CopyPropertiesFromEntityClass (huge), ClipBoundsMove, GroupFallingBlocks detail, FindSupportingBlockPos, more World unmentioned


## Checkpoint 3
- 33 commits since dry-run
- stock-check green; narrated 1488
- Loop/tick path, MoveHelper, land claims, spawn gates heavily filled
- Continue until interrupted


## Checkpoint 4
- 38 commits since post-update dry-run (3b61d9c)
- stock-check green; unaccounted 0; narrated ~1488
- Covered this long session: MoveHelper surface, EntityAlive helpers, World spawn/land/uncull/tick, GameStateManager, WorldBlockTicker, SpawnManagerDynamic, packages


## Checkpoint 5 (2026-08-07/08 continuation)
- ~55 commits since dry-run; stock-check green; narrated 1491
- Doc structure pass (f1e6a34): section numbering, D-order, stability-dump -> il/
- Tier-C depth: config-copy family (Entity/EntityAlive/Player/EAIManager + AI
  task parse), spawn sampler §6.1, ECD builder, SendChunksToClients §4.0a,
  pause save-on-pause, PlayerSpawnedInWorld, EntityVulture flight AI + helpers
  (D15), EntityClass prop table, GameStats/GamePrefs tables
- Next: keep rotating undoc leaves; refresh handoff tip each few commits
