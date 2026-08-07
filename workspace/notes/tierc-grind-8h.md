# Tier-C continuous grind (8h target)

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
