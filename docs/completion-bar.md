# What "100% documented" means for this corpus

**Owns:** the honest definition of completion for stock dedicated RE, and how to
drive unaccounted → 0 after each game patch or doc edit.
**Not:** a claim that every IL instruction is prose-narrated.
**Hub:** [`INDEX.md`](INDEX.md). **Coverage tool:** [`coverage.md`](coverage.md),
[`inventories/coverage-report.md`](inventories/coverage-report.md).

---

## 1. Completion is tiered (do not collapse to one %)

| Tier | Meaning | Done when |
|---|---|---|
| **A. Managed map closed** | Every **reached game type** is narrated, catalogued, or classified OOS | `Coverage.exe` **unaccounted = 0** |
| **B. Dedi-critical behaviour closed** | Families 1-11 in [coverage.md](coverage.md): loop, wire, entities, world, save, net, managers, light/mesh/water, ModEvents | Status **Closed** + residual only non-IL |
| **C. Optional annotation depth** | Per-flag package framing, every console command prose, every TE subclass tick | Never "required" for interop; backlog only |
| **D. Non-IL residuals** | Unity order, native LiteNet/EAC, A* library, content XML, client UI | Listed in [residuals.md](residuals.md); **cannot** be closed by more managed RE |

**"100% of dedicated managed behaviour"** in this project means **A + B**.  
It does **not** mean C (infinite), and does **not** mean D (impossible from IL alone).

Narrated **37%** of the Coverage *base* is expected and healthy: the base
over-includes client UI and under-includes reflection; many types are correctly
**catalogued** or **classified**, not fully narrated.

---

## 2. After every game update or large doc edit

```bash
ASM="$HOME/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll"
cd tools && ./build.sh --skip-legacy
cd ..
make stock-sync          # pin JSON + sibling gates
MONO_PATH=tools/bin mono tools/bin/Coverage.exe "$ASM" docs docs/inventories/coverage-report.md
# read "Top undocumented" table; drive unaccounted to 0
```

For each unaccounted type:

1. Dump IL (`DumpType` / `DumpMethod` / `Xref`).
2. If dedi sim/wire: **narrate** in a family doc (backtick the type name).
3. If inventory-only leaf: add to the right `docs/inventories/*` with backticks.
4. If client/telemetry/third-party: add to [out-of-scope-surface.md](out-of-scope-surface.md).
5. Re-run Coverage until unaccounted = 0.

---

## 3. Current pin status (2026-08-07, regenerate to refresh)

| Check | How | Result |
|---|---|---|
| stock_facts vs live ASM | `make stock-check` | exit 0 (V 3.1.0 b14) |
| Unaccounted reached types | `Coverage.exe` | **0** (3699 game types; narrated 1479 / catalogued 830 / OOS 1392) |
| Families 1-11 | coverage.md Status column | Closed |
| Non-IL residuals | residuals.md §1 | Honest permanent list only |
| Tier A+B | this doc | **Met** for V3.1.0 b14 managed dedi bar |

Optional depth (C) still open by design: rare NetPackage per-flag framing,
full console-command prose beyond the catalog, TE subclass tick minutiae.

**Last cleanup that hit unaccounted=0:** `HeartbeatEventData` / `Helper` /
`TruncateStringSerializerConverter` classified OOS (client analytics; dedicated
skips heartbeat); `ConsoleCmdLogEnvironment` (`logenv`) added to console catalog.

### Tier-C depth progress (ongoing, never complete)

Closed in recent sessions (still optional, not required for A+B):

| Topic | Doc |
|---|---|
| ASP FindPaths FIFO + `ldc.i4.8` drain | entity-ai §D3.7 |
| Interest exit = `NetPackageEntityRemove` / Unloaded | network §2.2 |
| `Chunk.NeedsSaving` predicate | world-chunks |
| BodyAnimator `defaultCullingMode` vs live cull | entity-ai addendum |
| Raw + sector region headers (`7rr` / `7rg`) | save-region §3.4-3.5 |
| `BuffManager` registry | buffs §1.1 |
| `ClientPowerData` stream modes | tile-entities-power §2.1 |
| Audio/Light/TreeFade/DroneParticle wire fields | protocol-packages §6.21 |
| Explosion Initiate/Client full field lists | protocol-packages §6.14-6.15 (already) |
| PowerItem subtype tick table + power.dat tails | tile-entities-power §3.4-3.5 |
| WireActions SetParent/RemoveParent/SendWires process | tile-entities-power §3.6 |
| Corrected toggle gate (not PowerChildren) | tile-entities-power §3.3 |
| EntitySpawnResponse ToClient process; EntityLookAt | protocol-packages §5.2 |
| SleeperVolume.Tick / UpdateSpawn / Despawn / PlayerTouched | entity-ai §D8.1-D8.4 |
| Workstation/Forge UpdateTick fuel+recipe IL | tile-entities-power §4 |
| Vending rental expiry; Composite feature tick | tile-entities-power §4.5 |
| Package process paths (Collect/Attach/ItemDrop/...) | protocol-packages §6.21.1-2 |
| EmitSmell ProcessPackage no-op | protocol-packages §6.21 |
| Broad §6.21 ProcessPackage authority table | protocol-packages §6.21.2 |
| MinEvent AddBuff/ModifyCVar/Explode Execute | minevents §7.1 |
| Collector/Light/trap TE write tails | tile-entities-power §4.6 |
| SpawnUpdate distance bands re-pin | entity-ai §D3.6 / spawning §2 |
| DamageEntity local early outs; AliveFlags process | protocol-packages §6.11 / §5.5.6 |
| StatChanged/StatsBuff/PlayerStats process IL | protocol-packages §6.16 |
| High-value console Execute IL table | console-commands §2.1 |
| UAIBase chooseAction/updateAction | entity-ai §5.3 |
| Workstation/PoweredTrigger write modes | tile-entities-power §4.6 |
| Quest/Party/GameEvent process IL re-pins | protocol-packages §6.17-6.18 |
| SetBlock + InventoryData hash cache process | protocol-packages §6.1 / §6.13 |
| PlayerInventory -> latestPlayerData | protocol-packages §5.4 |
| LandClaim/Sleeper/Deco/Sign/AddExp/Auth process | protocol-packages §6.19 / §2 / §6.21 |
| NetPackageChunk Process overwrite/add | protocol-packages §3.1 |
| TEFeature composite wire tails | tile-entities-power §4.7 |
| More MinEvent action leaves | minevents §7.1 |
| DamageEntity IL=236 gate order | combat-damage §2 |
| UAI Move/Wander/Attack task leaves | entity-ai §5.3 |
| OnUpdateTick order re-pin | loop §3.2 |
| OnUpdateEntity / OnUpdateLive phase order | entity-ai §2.0 |
| fireShot / DynamicMelee Execute re-pin | items §4.2 |
| EntityStats waitTicks phase machine | entity-stats §1.1 |
| EntityBuffs.Tick IL=179 | buffs §2 |
| BloodMoonComponent.Tick parties | spawning blood-moon section |
| ItemActionEat.consume IL=154 | items §4.2 |
| TickEntities slice formula exact | loop-gmupdate §5.1 |
| ServerConsoleCommand 6-step path | console-commands §2 |
| AddLevelExp IL=161 order | progression §2 |
| Manager Update behaviour re-pins | managers §1 / §1.1 |
| EAI leaf Update/CanExecute IL table | entity-ai §D2 |
| More package Process (chat/quest/score/kill/skill) | protocol-packages §6.21 / §2 |
| TickEntity + path apply helpers | entity-ai §7 |
| ChangeBlocks / SetBlocksOnClients | world-chunks §5.1 |
| Join Authorize/RequestToSpawn/SpawnEntity | server-lifecycle join path |
| GetDamageEntity/Block EffectManager tags | items §4.2 |
| CommandAllowedFor level compare | console-commands §2 |
| DisconnectClient / SavePlayerData order | network §1.3-1.4 |
| OnEntityDeath / dropItemOnDeath | combat-damage §3.1 |
| ItemDropServer 50/chunk cap | loot-economy §6b |
| InventoryTransaction.Apply hash/ops | items inventory section |
| Party AcceptInvite / CreateParty | parties-factions |
| AIDirector CreateComponents order | spawning / loop |
| AwardKill / SetDead | combat-damage §3.1 |
| SleeperVolume.OnTriggered | entity-ai §D8.2b |
| FireEvent fan-out order | minevents §3 |
| SetAttackTarget / SeeCache | entity-ai §5.1b |
| ExplosionServer/Client | protocol-packages §6.14-6.15 |
| explode AttackBlocks/Entities | protocol-packages §6.14 |
| LetBlocksFall create path | entity-ai §8 |
| BuffValue.DurationTick | buffs §2 |
| PlayerId / PlayerSpawnedInWorld packages | server-lifecycle join |
| CheckDespawn / player OnUpdateLive | entity-ai §5.1b |
| Explosion AttackBlocks/Entities | protocol-packages §6.14 |
| SaveWorld entry chain | save-region |
| canDespawn / unloadEntity | entity-ai §5.1b |
| AwardKill / AddScoreServer chain | combat-damage §3.1 |
| SimpleRPC holding activate/reset | protocol-packages §6.21 |
| ChatMessageServer / GameMessage | chat.md |
| SendPackage client filters | network §1.5 |
| GameTimer.updateTimer formula | entity-ai §D6 |
| ThreadManager main-thread drain | loop-gmupdate |
| Astar UpdateGraphs merge size 76 | loop.md |
| damageEntityLocal + ProcessDamageResponse | combat-damage §2.1-2.3 |
| EffectManager.GetValue stack | minevents §7.0 |
| ItemValue.FireEvent recursion | items §8 / minevents §7 |
| Sleeper TickSpawnCount + CheckSpawnPos | entity-ai §D8.1-D8.2 |
| Workstation HandleFuel re-pin | tile-entities-power §4.2 |
| EntityStatChanged / StatsBuff Process | entity-stats §5.1-5.2 |
| NetPackageTileEntity Process teBlockId | tile-entities-power §2 |
| QuestObjectiveUpdate event types | protocol-packages |
| UAI all 5 concrete task Start+Update | entity-ai §5.3 |
| More MinEvent leaves (exp/loot/rage/jam) | minevents §7.1 |
| GetLandClaimOwner self/ally/other + offline | server-lifecycle §3.1 |
| EntityTrader.OnUpdateLive open/greet/unload | loot-economy |
| LockRequestServer 5-target cap + maps | dedicated-leftovers §2.2 |
| ServerConsoleCommand 300-char reject | console-commands §2 |
| EntityAliveFlags process bit table | protocol-packages §5.5.6 |
| AddKillXP / SharedKillServer party XP | parties-factions §2.3 |
| EntityItem OnUpdateEntity lifetime | loot-economy §6b |
| DropItemsOnEvent harvest table | blocks §3 |
| PartyQuestChange HandlePlayer | parties-factions §2.3 |
| EAIApproachAndAttackTarget Update phases | entity-ai §D2 |
| EAI Break/Wander/RunAway/Ranged leaves | entity-ai §D2 |
| updateTasks freeze + GroupFallingBlocks | entity-ai §5.1b / §8 |
| FallingBlock crush damage + land drops | entity-ai §8 |
| Stability queueStabilityAvail cap 200 | stability.md |
| getMaxStabilityAround + ChangeStability | stability.md |
| TurretTracker 120s save; vehicle attach | vehicles-drones-turrets |
| World.CanPlaceBlockAt claim/trader/bounds | blocks §6 |
| IsLandProtectedBlock + bounds soft edge | server-lifecycle §3.1 |
| Chunk.SetBlockRaw silent write path | world-chunks §5.0 |
| DecoManager.UpdateTick thread queues | managers §1.1 |
| PlantGrowing + TorchHeatMap + WBT execute | blocks §7 / save-region §3.6 |
| NotifyActivity + CheckToSpawn 25/20% | aidirector.md |
| BlockLiquidv2 Emissions/ChangeToAir | light-mesh-water.md |
| ChangeThis pack + SpawnScouts bands | light-mesh-water / aidirector |
| Chunk activity AddEvent/Decay/240s | aidirector.md |
| Liquid Evap/Flow damage packing | light-mesh-water.md |
| Scout horde SpawnUpdate/UpdateHorde | aidirector.md |
| Drone idle/follow/sentry + turret findTarget | vehicles-drones-turrets |
| Turret shouldIgnoreTarget + Fire ammo | vehicles-drones-turrets |
| spawnHordeNear CreateHorde counts | aidirector.md |
| trackTarget/canHitEntity + FindScoutStartPos | vehicles / aidirector |
| Investigate pos + neighbor cooldown delays | entity-ai §D3.8 / aidirector |
| GetGroupPositions / DoMoveIntoFollowPos repath | vehicles-drones-turrets |
| TickActiveSpawns drain + heal medical 0.67 | aidirector / vehicles |
| Scout Update finish + Horde.Tick + CanAttack | aidirector / vehicles |
| AIHordeSpawner.Tick radii + Weapon cooldown | aidirector / vehicles |
| MachineGun/Stun/Heal Fire + PartySpawner Tick | vehicles / aidirector |
| SetupGroup duration*1000 + heal type priority | aidirector / vehicles |
| CanSpawn cap + SetPartyLevel gsScaling + teleport | aidirector / vehicles |
| CalcPartyLevel diminishing + setState transitions | aidirector / vehicles |
| get_gameStage formula + GameStage static defaults | progression / aidirector |
| GetLootStage POI/biome + passives 159/160 | loot-economy.md |
| Party GetHighestLootStage wrappers | loot-economy.md |
| getProbability passive 79 + SpawnLootItemsFromList | loot-economy.md |
| GetSandboxProb + RandomSpawnCount ±0.49 | loot-economy.md |
| RandomCountFromSandboxTags category table | loot-economy.md |
| GetCountMultiplier enum + BM weather storm defer | loot / weather |
| dropItemOnDeath passive 80 + BlockDestroyed 500 m | combat / quests |
| DropBagServer lootDrops vs bag paths | combat-damage.md |
| LootDropPick weighted + OnBlockStartsToFall Air | combat / stability |
| AttackEntites body mult + DamageRecord apply | protocol-packages §6.14 |
| explode ExplodeGroup delay=3 + FrameUpdate budget | protocol-packages §6.14 |
| Interest enter package order (Speeds/Velocity) | network.md §2.1 |
| EntityBuffs.Tick MinEvent 0/1/2/3 order | buffs.md |
| BuffClass.FireEvent canRun + StartSequence | buffs / game-events |
| SeekTarget kill distances + OnEntityUnload | aidirector / entity-ai |
| CalcSpawnPos + unloadEntity teardown pipeline | aidirector / entity-ai |
| CheckDespawn band table + horde canDespawn | entity-ai.md |
| AddBuff BuffStatus 0..5 + ResetDespawnTime | buffs / entity-ai |
| HasImmunity passive 197 + CanSee caches | buffs / entity-ai |
| FriendlyFireCheck PvP modes + CanEntityBeSeen LOS | buffs / entity-ai |
| GetSeeDistance/DetectUsScale + volume touch | entity-ai.md |
| CalcSenseScale FeralSense + CheckTouching pads | entity-ai.md |
| TouchGroup/Touch wake + GetClosestPlayerSeen | entity-ai.md |
| Sleeper wake/passive net + crouch detect | entity-ai.md |

Remaining catalogued-only mass is mostly console commands (catalog rows), residual
MinEvent presentation leaves, client-shared helpers. Further UAI is only
considerations / action scoring XML, not more task subclasses (only 5 exist).
Promote only when a clone or optim lever needs the behaviour.

---

## 4. Why literal "every behaviour" is impossible

| Surface | Why IL cannot finish it |
|---|---|
| Unity MB execution order | Prefab/project settings, not CIL |
| Entity GO `enabled` on pure dedi | Runtime observation |
| LiteNet native / EAC wire | Native / anti-cheat black box |
| A* Pathfinding Project internals | Third-party library |
| XML content (blocks, loot, buffs) | Data files, not loop IL |
| ModEvents who registers | Content/mod dependent |

These stay in [residuals.md](residuals.md). Closing them is product/ops/runtime
work, not more narrative RE.

---

## Changelog

- **2026-08-07:** Initial completion-bar definition after Coverage unaccounted=4 cleanup drive.
