# Tier-C grind handoff / TODO

**Updated:** 2026-08-08 ~13:20 UTC
**Repo:** `7dtd-research` (cwd this tree)  
**Pin:** V **3.1.0 (b14)** via `tools/data/stock_facts.json`  
**Managed bar:** tiers A+B met (unaccounted **0**). This grind is **tier C only**.

## Mission

Never-stop loop:

```text
dump live ASM IL → narrate only deltas → census/pins → stock-check → commit
```

Do **not** touch `zdtd` product code unless the user re-opens that lane.  
No em dashes. No AI attribution in commits.

## Current tip

| Item | Value |
|---|---|
| HEAD (at handoff write) | `2b7dcc7` entityclass-props verify |
| Commits since dry-run `3b61d9c` | ~1350 |
| stock-check | green expected |
| Coverage (last pin text) | narrated 1846 / catalogued 558 / classified 1295 / unaccounted **0** |
| Session plan | `workspace/notes/tierc-grind-8h.md` |
| Lab notebook | `workspace/CHANGELOG.md` |

2026-08-08 final-stretch notes: full protocol-packages §6.x wire sweep
(6.1/6.2/6.9-6.22; every claimed write/process IL size exact); Coverage census
re-verified (1846/558/1295, unaccounted 0, report in sync); INDEX structure
coherence (all docs linked, no dead links); netpackage inventory reconciled
(193 census / 182 own-write bodies; 8 write-less or inherited-write packages
covered narratively); minevents §7.0a catalog spot-checked (26 claims exact,
67 TargetedCompareRequirementBase leaves confirmed, IsBloodMoon IsValid IL
fixed 17 -> 11); console command catalog verified census-correct (187 commands
+ 2 alias rows; Coverage credits bare simple names, namespaced full names in
the Type cell break the count). **DumpAll fix:** the tool silently clobbered
757 of 7432 types (filename collisions among compiler-generated nested types;
Cecil reports empty Namespace for nested types of namespaced parents). Fixed
by full declaring-chain scoping + outermost-namespace dir; fresh runs now
produce exactly 7432 files, 0 missing, 0 extra (verified vs a new
ListAllTypes.exe audit tool). Canonical `il/full-v3.1.0/` and `/tmp/full-il.txt`
regenerated clean.

Verification sweep completed after that: every docs/*.md IL claim spot-checked
in 2-3 batches (entity-ai, items, vehicles, aidirector, spawning, world-chunks,
blocks, tile-entities, dedicated-misc, combat, loot/quests/progression,
network/save/weather, mod/twitch/chunk-providers, stealth/crafting/game-events,
map-objects, sandbox/buffs, light/entity-stats/stability, leftovers/parties,
loop, protocol join/spawn, signs/webserver, platform-auth, npc-dialog,
world-gen, terrain-height, dynamic-mesh, chat/server-lifecycle, save-region,
save-persistence, crafting, raycast-pathing, buffs, items 3rd, etc.). All
exact. Additional stale-value fixes: ConnectionManager.Update 215->228
(network.md x2 + manager-updates), WorldState.SetFrom 164->203 (save-region
x2), World.GetTerrainHeight 21->19, loop diagram OnUpdateEntity 417->457,
closed-gaps + terrain-height SaveLoad 884->926, terrain-height heightmap pair
49/63->132/74. Netpackage bodies inventory IL-verified field-by-field
(EntityRemove, PlayerId, ExplosionInitiate 9 fields); gmupdate-calls 182 rows
and frame-entries 244 rows confirmed; 0xCA marker found in the LiteNetLib auth
wrapper. Census unchanged 1846/558/1295, unaccounted 0, report in sync. Final
state: tree clean at the closing commit, `make test` + `make stock-check`
green, 2205+ commits.

2026-08-07/08 session notes: doc structure pass (f1e6a34) - fixed duplicate
section numbers (server-lifecycle, quests-challenges, managers, save-region),
ordered entity-ai D8.x sections, moved `docs/stability-dump/` raw IL to
git-ignored `il/stability-v3.1.0/`, removed root junk dirs. Tier-C batch since:
config-copy family (Entity D8.6a / EntityAlive D8.6 / EAIManager D8.7 / AI task
parse), spawn sampler (spawning §6.1), ECD builder (spawning §7), chunk
streaming (world-chunks §4.0a), join/disconnect (server-lifecycle §3.2), pause
(loop-gmupdate Phase A2), PlayerSpawnedInWorld full body, EntityVulture flight
AI + helpers (entity-ai D15), two new reference inventories
(entityclass-props.md, gamestats-gameprefs.md). Census: narrated 1491.

2026-08-08 continuation: 40+ more tier-C commits - EntityClass.Init phase
map (D8.6b), CreateEntityOperation.CompleteEntity (spawning §7), GameMode
family (InitGame/StartRound/GameStats bootstrap table + survival overrides),
Stat.Tick/regen + SetChangedFlag, EntityVulture D15 (already), airdrop family
(CreateFlightPaths/SpawnPlane/Tick/crate/plane), chunk load/unload lifecycle
(world-chunks §4.0b), GameUtils time pins, Constants pins, several small
resolver leaves. Census: narrated 1496 / unaccounted 0.

2026-08-08 late continuation (3h turn): 57 more tier-C commits. Dead/inert
sweep (full-IL body-verified, 0-ref): LiveStats, DynamicMeshDataQueue<T>,
DynamicMeshRegionBuilder, Prefab.Cells<T>, World.ClipBoundsMove (IL=573),
ServerUpdates channel, TList/TQueue, OneToOneDictionary, CollectionDebugWrapper,
ParsingConverters, SimplexNoise, OpenSimplex2/2S, IEnumerableExtensions,
BinaryReaderExtensions (UniLinq + ObservableDictionary refuted as dead - both
live). Wire corrections from the rebuilt WireBodies.exe: NetPackageDamageEntity
bIgnorePartyShare (IL=176), EntityCreationData stressAmount f32 tail (read v36+),
NetPackageTileEntity teBlockId. Families narrated: AdminBlacklist sub-store +
telnet login lockout, GameStatsBridge, shared chunk observers, TripWireController,
minevent requirement catalog complete (67 leaves, misleading names corrected:
IsBloodMoon=SkyManager, InSafeZone=TwitchSafe, IsAlly=IsFriendOfLocalPlayer,
IsOnLadder=IsInElevator), Twitch requirement gates / viewer-points ledger /
action-queue records / vote+cooldown presets / spawn-entry records / TwitchActionManager,
OOS hygiene (HasParticle un-classified, 15 Twitch server records moved out,
third-party families named). Census: narrated 1845 / unaccounted 0.

2026-08-08 late-late continuation: verification/closure sweep reached
absolute completion - uncovered server-relevant types = 0 at every threshold
(n>=5, n>=3, n>=2). Closed the last IL-closable open item (stability
clear/unspread mechanics), refreshed the full-surface census (7432 types /
53235 methods / 1,740,737 IL / 89 namespaces across 4 docs), reconciled all
OOS doc counts (supplement sections now match their lists; total 1168),
verified every leaf-catalog key-method/referrer/base claim (1 real error
fixed: SpawnEntry HandleUpdate), and verified all remaining doc structural
claims (game-events 179/1014, quests 7/48, Twitch 117, Webserver 72/413,
largest-maxIL order). Census: narrated 1846 / unaccounted 0.
## Resume checklist (next agent / next turn)

1. `cd /home/maci/Desktop/7dtd/7dtd-research && git status && git log --oneline -5`
2. Read this file + tail of `workspace/CHANGELOG.md`
3. Confirm ASM path exists:
   `~/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll`
4. Optional: `make stock-check` (must stay green)
5. Prefer **gap-fill** over re-doc: many leaves already narrated
6. After each batch: update family doc + completion-bar row + CHANGELOG → commit

## Dump tooling

```bash
ASM="$HOME/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll"
MONO_PATH=tools/bin mono tools/bin/DumpMethod.exe "$ASM" TypeName MethodName /tmp/nXXX_Type_Method.txt
# rebuild tools only if DumpMethod missing:
# (cd tools && ./build.sh --skip-legacy)
make stock-check
# optional census refresh:
# MONO_PATH=tools/bin mono tools/bin/Coverage.exe "$ASM" docs docs/inventories/coverage-report.md
```

Scratch dumps live under `/tmp/nNNN_*` (not committed). Recent batches: `n189` spawn helpers, `n190` join/save, `n191` loot/inventory/disconnect (pending narrate).

## Immediate TODO (next commits)

### Batch A: document `/tmp/n191_*` (dumped, not all committed)

- [x] `DropContentOfLootContainerServer` (IL=99) → `docs/loot-economy.md`
  - server-only; lock reject; DroppedEntityClass override; LootContainerOpened if !bTouched; clone items into EntityLootContainer; SetEmpty
- [x] `CheckDestroyTileEntity` (IL=37) → loot-economy / TE
  - ITileEntityLootable + ShouldDestroyOnClose → drop + DamageBlock MaxDamage
- [x] `doSendLocalPlayerData` (IL=25) / `doSendLocalInventory` (IL=40) → network or server-lifecycle
  - server: SaveLocalPlayerData; client: NetPackagePlayerData / conditional NetPackagePlayerInventory flags
- [x] `FinishGameMessageServer` (IL=69) → chat / game-events
  - ModEvents.GameMessage interruptible; DisplayGameMessage; rebroadcast flags **192** unless result==2
- [x] `HandleFirstSpawnInteractions` (IL=116) → parties or server-lifecycle (mostly local client)
  - type==2 only; block message; auto party invite if pref **235** + ally
- [x] `IsSafeToDisconnect` (IL=27) → server-lifecycle
  - offline true; prefab edit NeedsSaving false; require game started && !starting && !disconnectingLater
- [x] `CalculatePersistentPlayerCount` (IL=64) → save-region / lifecycle
  - scan `Player/` names strip extension; unique into `persistentPlayerIds`

### Batch B: high-value undoc / thin leaves (rotate)

**Entity / move / combat**

- [x] `EntityAlive.updateStepSound` (IL=107) if not fully narrated
- [x] `NetEntityDistributionEntry.updatePlayerList` (IL=509) interest rebuild
- [x] `ProcessDamageResponseLocal` deep residual branches only if holes remain
- [x] `ClientKill` / `AwardKill` / `OnEntityDeath` residual detail
- [x] `dropItemOnDeath` full path
- [x] `StartJumpSwimMotion` water y-clamp formula (partially done)

**Sleeper / stealth**

- [x] `SleeperVolume.Touch` correct overload body
- [x] `ConditionalTriggerSleeperWakeUp` residual
- [x] `NotifySleeperDeath` if thin

**World / blocks**

- [x] `GameManager.ChangeBlocks` (IL=530) phase map if not complete
- [x] `SetBlocksOnClients` thin wrapper confirm
- [ ] land-claim / stability / falling residual leaves only if undoc

**Net packages**

- [ ] rare `ProcessPackage` conditionals still thin in protocol-packages
- [ ] any NetPackage with incomplete body table in inventories/netpackages.md

**Managers**

- [ ] undoc tick leaves from `docs/inventories/gmupdate-calls.md` cross-check
- [ ] AIDirector residual scout/heat edges only if not already in aidirector.md

### Batch C: hygiene (periodic, not every commit)

- [ ] Re-run Coverage when large doc batches land; refresh completion-bar census line
- [ ] `make stock-check` green
- [ ] No em/en dashes in edited docs
- [ ] Avoid re-documenting closed A+B families without new IL facts
- [ ] On real TFP version bump only: `make post-update` (do not rebaseline drift casually)

## Doc ownership map (where to write)

| Leaf family | Doc |
|---|---|
| Spawn position / bedroll / CanMobsSpawn | `docs/spawning.md` |
| Join / save / disconnect / GM lifecycle | `docs/server-lifecycle.md` |
| Entity AI / sleeper / ragdoll / attack timeouts | `docs/entity-ai.md` |
| Damage / dismember / crawler | `docs/combat-damage.md` |
| Loot drop containers / TE destroy | `docs/loot-economy.md` |
| Interest / SendToPlayers / inventory packages | `docs/network.md` |
| Package bodies | `docs/protocol-packages.md` |
| Power / TE | `docs/tile-entities-power.md` |
| Save files | `docs/save-region.md` |
| Block damage / upgrade / downgrade / placeholder map | `docs/blocks.md` |
| Tier-C progress rows | `docs/completion-bar.md` |
| Honest permanent non-IL | `docs/residuals.md` |

## Commit message pattern

```text
Tier-C: <short leaf names>

Document <behaviour summary> from live V3.1.0 b14 IL.
```

User git identity only. No co-authored / AI lines.

## Stop conditions

| Condition | Action |
|---|---|
| User interrupts | stop after finishing current commit + update this handoff |
| stock-check red | fix pins before more narrative |
| Live game version ≠ b14 | stop grind; run post-update path |
| Accidental doc wipe | restore from git immediately (see spawning.md incident) |

## Out of scope for this grind

- zdtd implementation
- EfficientServer default-on new levers without APM
- Path admission / AnimatorEmergency default-on (measured worse / unproven)
- Redistributing ASM or bulk `il/` dumps
- Claiming "100% of all IL" (tier C is infinite by design)

## Suggested next single action

Document **Batch A** from `/tmp/n191_*` into loot-economy + server-lifecycle + network, pin completion-bar, stock-check, commit, then dump next undoc batch from GameManager/World/EntityAlive leaves still missing from docs.

## Session continuity notes

- Autoresearch version-update tooling already at readiness **100**; parked under `workspace/autoresearch/`
- Post-update dry-run report: `workspace/outputs/post-update-dry-run-20260807.md`
- Do not invent optim patches; RE only unless user asks product lane
