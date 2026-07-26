# Audit: leaf-narration subsections (nine docs, added 2026-07-24)

**Verdict:** One CRITICAL wire-breaking error in `protocol-packages.md` §5.1 (the convergence tail flattens two conditionals and drops a field); every other new subsection audited is accurate against the V3.0.1 assembly, including all three hard-verify claims (UAI dormancy, trader-stage client-only evaluation, POIWithinDistance dead return). Two MINOR label issues.

Scope: only subsections added in f9a7031..HEAD (`git diff f9a7031..HEAD -- docs/<doc>`). ASM = `/home/maci/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll`. Config = `.../Dedicated Server/Data/Config`.

## Findings

### F1 - CRITICAL (wire-breaking) - protocol-packages.md §5.1, "(3) Convergence tail (every entity)"

**Claim (doc code block):** inside `if networkWrite:` the tail ends
```text
isDancing   : bool
isSleeperPassive : bool
belongsPlayerId  : i32
```
i.e. `isSleeperPassive` unconditional, `belongsPlayerId` unconditional and inside the networkWrite guard, and nothing after it.

**Ground truth:** `mono tools/bin/DumpMethod.exe "$ASM" EntityCreationData write`
- `isSleeperPassive` is written **only when `isSleeper` is true**: IL_03B1 `ldfld Boolean EntityCreationData::isSleeper` / IL_03B7 `brfalse.s IL_03C5` skips IL_03BB `ldfld Boolean EntityCreationData::isSleeperPassive`.
- The trailing `belongsPlayerId` is **junkDrone-only** and sits **outside** the networkWrite guard: IL_03C5-IL_03D0 `ldfld entityClass / ldsfld Int32 EntityClass::junkDroneClass / bne.un.s IL_03EA`; the networkWrite `brfalse` at IL_033F targets IL_03C5, so the junkDrone block runs even when `networkWrite=false`.
- The junkDrone block writes **two** i32 fields: `belongsPlayerId` (IL_03D4) **and `orderState`** (IL_03E0). `orderState` is absent from the doc.
- Read side is symmetric: `DumpMethod EntityCreationData read` shows IL_04FD `ldfld isSleeper / brfalse.s IL_0510` gating `isSleeperPassive`, and IL_0516 `ldsfld EntityClass::junkDroneClass / bne.un.s IL_053F` gating `belongsPlayerId` + `orderState`.

**Impact:** a clone implementing the tail from this doc reads 1 phantom byte on every non-sleeper spawn and 4 phantom bytes on every non-drone spawn (stream desync on essentially every `NetPackageEntitySpawn`), and truncates drone spawns by 4 bytes. The header and the entityClass-switched middle are correct (see CONFIRMED list); only the tail block is wrong.

**Fix:** replace the last three lines of the tail block with:
```text
    isDancing   : bool
    if isSleeper: isSleeperPassive : bool
# after the networkWrite block, ALWAYS evaluated (both write modes):
if entityClass == EntityClass.junkDroneClass:
    belongsPlayerId : i32
    orderState      : i32
```

### F2 - MINOR (label) - entity-ai.md "Focus + target-selection leaves"

**Claim:** "(stock lists slot it at `AITarget-2`)" for `EAIBlockingTargetTask`.

**Ground truth:** `grep -n "BlockingTargetTask" "$CONFIG/entityclasses.xml"` -> lines 5272, 5401 are `AITarget-2`, but line 5029 is `<property name="AITarget-3" value="BlockingTargetTask"/>` (that entity's `AITarget-2` is `BlockIf`), and lines 574/5131/5219 slot it inside pipe-separated task-list strings. The mutex-ordering conclusion (above `SetNearestEntityAsTarget`) still holds in all forms.

**Fix:** say "stock lists slot it above `SetNearestEntityAsTarget` (usually `AITarget-2`, sometimes `AITarget-3` after a `BlockIf`)".

### F3 - MINOR (label) - world-generation.md "Prefab/decoration data leaves"

**Claim:** `BiomeBlockDecoration.GetRandomRotation` "folds values 4..7 up by +24 into the extended-rotation range".

**Ground truth:** `mono tools/bin/DumpMethod.exe "$ASM" BiomeBlockDecoration GetRandomRotation` -> IL_0014 `ldc.i4.4 / sub` then IL_0017 `ldc.i4.s 24 / add`: values 4..7 map to 24..27, a net offset of **+20** (rebase at 24), not "+24". The parenthetical IL quote in the doc is correct; the prose number contradicts it.

**Fix:** "remaps values 4..7 to 24..27 (`sub 4`, `add 24`)".

## Spot-verified CONFIRMED

**protocol-packages.md §5.1 (everything except the tail defects in F1)** - `DumpMethod EntityCreationData write` + `DumpMethod NetPackageEntitySpawn write`:
- `NetPackageEntitySpawn.write` passes `ldc.i4.1` -> `networkWrite=true`.
- Header order and types exact through `spawnerSource` (IL_0000-IL_0143), incl. version byte constant 35, stats/bag presence bools.
- Middle is a mutually exclusive `entityClass` compare chain against `EntityClass.itemClass` / `fallingBlockClass` / `fallingBlocksClass` / `fallingTreeClass` / `playerMaleClass`+`playerFemaleClass` (IL_0148-IL_02EC); itemClass branch writes `belongsPlayerId:i32, clientEntityId:i32, ItemStack.Write, sbyte(0)` then `br IL_02F1` (tail); fallingBlocks writes count + per-block rawData, then `blockPositions` and `textureFullArrays` loops with no separate counts; player branch is `ItemValue.Write, teamNumber:u8, entityName:string, skinTexture:string, playerProfile bool (+Write)`; any other class falls through to the tail writing nothing.
- Tail `entityData` u16+bytes and `traderData` bool(+Write) unconditional; networkWrite block order `sleeperPose, isSleeper, spawnById, spawnByName, spawnByAllowShare, headState, overrideSize, overrideHeadSize, isDancing` exact.

**uai.md "Consideration leaves" (key dormancy claim)**:
- `grep -n "AIPackages" "$CONFIG/entityclasses.xml"` -> only lines 6472/6526 (`npcSurvivorTemplate`/`npcSurvivorRanged`); comment scan `awk 'NR<=6472 && /<!--/{o=NR} /-->/{c=NR}'` -> last `<!--` opens at 6458, last `-->` before it closes at 6457, and the block closes after 6526: both entries are **inside an XML comment**. `grep -rl npcSurvivor "$CONFIG"` -> only entityclasses.xml + Localization.csv. "Live code but dormant in stock V3.0.1" CONFIRMED.
- `DumpMethod UAIConsiderationSelfHealth GetScore`: NaN sentinel -> `GetMaxHealth()`, then `(Health - min)/(max - min)`. CONFIRMED.
- `DumpMethod UAIConsiderationTargetDistance GetScore/Init/.ctor`: `Clamp01(Max(0, distSq - min)/(max - min))` over `UAIUtils.DistanceSqr`, entity + Vector3 branches, else 0; Init squares parsed min and max (`mul` on self); ctor default `max = 9126f`. CONFIRMED.
- `DumpMethod UAIConsiderationTargetHealth GetScore`: entity `Health/GetMaxHealth`; Vector3 `(Block.MaxDamage - BlockValue.damage)/MaxDamage`; else 0. CONFIRMED.
- `DumpMethod UAIConsiderationTargetType GetScore/Init`: Init `String.Split(char, ...)` on `type`; per entry `Type.GetType` + `IsAssignableFrom` vs candidate class, Vector3 -> `BlockValue.Block` type; else 0. CONFIRMED.
- `DumpMethod UAIConsiderationSelfVisible GetScore`: `(1 - headDistSq/GetSeeDistance()^2) * (target.CanEntityBeSeen(Self) ? 1 : 0)`; 0 for non-entity. CONFIRMED.
- `DumpMethod UAIConsiderationTargetVisible GetScore`: `Self.CanEntityBeSeen(entity)` / `Self.CanSee(vector3)`; else 0. CONFIRMED.

**loot-economy.md "Loot-entry requirement + trader-stage leaves"**:
- `FindCallers LootEntry HasRequirements` -> exactly `LootContainer::SpawnAllItemsFromList` and `LootContainer::getProbability`; body ANDs `BaseLootEntryRequirement::CheckRequirement`. CONFIRMED.
- `DumpMethod LootFromXml ParseLootEntryRequirement` -> `ldstr LootEntryRequirement` prefix. CONFIRMED.
- `DumpMethod BaseOperationLootEntryRequirement CheckRequirement` -> LeftSide/RightSide + 18-target switch (3 aliases per op), default `ldc.i4.1` (unrecognized operation passes). CONFIRMED.
- `DumpMethod` on the five leaves: Biome `ContainsCaseInsensitive(biomes, biomeStandingOn.m_sBiomeName)`; CVar `Buffs.GetCustomVar` (0 if player null) vs `ParseFloat(valueText)`; Progression `GetProgressionValue(...).GetCalculatedLevel` (0 fallback); QuestTags false without `ActiveQuest` else `Test_AnySet`; RandomRoll `Mathf.Lerp(minMax.x, minMax.y, GameEventManager.Current.Random.RandomFloat)` vs `GameEventManager.GetFloatValue(player, valueText, 0)`. All CONFIRMED. Sixth sibling `LootEntryRequirementSandboxOption` exists (4 methods in MethodList output).
- `FindCallers TraderStageTemplate IsWithin` + `TraderStageTemplateGroup IsWithin` -> only evaluators are `XUiC_TraderWindow::FilterByName` (x2 sites) and `XUiC_CategoryList::SetupCategoriesBasedOnItems`; parse side only `TradersFromXml::ParseTraderStageTemplate*`; no server restock caller. `DumpMethod TraderStageTemplate IsWithin` -> Min/Max/Quality each `-1` = any, group is OR. **Client-only-evaluation claim CONFIRMED.**

**items.md "Item leaf types"**:
- `MethodList` + `DumpMethod AIDirectorPlayerInventory.ItemId Write` -> nested `AIDirectorPlayerInventory/ItemId`, writes `id` and `count` each `conv.i2` -> Int16; `TrackedItemsFromBag`/`TrackedItemsFromInventory`/`OrderIndependantEquals` present. **Not-the-general-item-id claim CONFIRMED.**
- `FindCallers ItemClass CreateWorldData` -> sole caller `EntityItem::PostInit`. CONFIRMED.
- Nesting + bases via ctor dumps: `ItemActionVomit/ItemActionDataVomit : ItemActionLauncher/ItemActionDataLauncher`; `ItemActionDynamic/ItemActionDynamicData : ItemActionAttackData`; `ItemActionDynamicMelee/ItemActionDynamicMeleeData : ItemActionDynamicData`; `ItemActionReplaceBlock/ItemActionReplaceBlockData : ItemActionRanged/ItemActionDataRanged`. CONFIRMED. `DumpMethod ItemActionVomit ExecuteAction` touches `warningTime`-family fields + `PlayOneShot`. CONFIRMED.
- `DumpMethod ItemClassArmor Init` ldstr set: ArmorGroup, EquipSlot, IsCosmetic, KeepOnDeath, AllowUnEquip, AutoEquip, ReplaceByTag. CONFIRMED.

**spawning.md "Spawn config leaves"**:
- `DumpMethod EntitySpawnerClassForDay Day` -> wrap via `rem` over `Count - 1` with 0 remapped to `Count - 1`, clamp to `Count - 1`, null entries fall back to index 0. CONFIRMED (incl. the odd `Count - 1` modulo).
- `DumpMethod SpawnEntry HandleUpdate` -> `GetClosestPlayer(entity, 500f, false)` + `SetAttackTarget(target, 1000)`. CONFIRMED.
- `DumpMethod AIAirDrop Tick` -> iterates `AIAirDrop/SupplyCrateSpawn`, decrements `SupplyCrateSpawn::Delay`, uses `SpawnPos`. CONFIRMED.
- `FindCallers` on both `ModEvents/SPlayerSpawningData::.ctor` (only `GameManager::RequestToSpawnPlayer`) and `ModEvents/SPlayerSpawnedInWorldData::.ctor` (only `GameManager::PlayerSpawnedInWorld`); both are nested ValueTypes with no serializer -> in-process payloads, not wire structs. CONFIRMED.

**world-generation.md "Prefab/decoration data leaves"**:
- `FindCallers PrefabListData AddPOI` -> built/filled only by `QuestEventManager::SetupTraderPrefabList`, shuffled by `GetPrefabsForTrader` -> quest-tier bucketing, not RWG. CONFIRMED.
- `FindCallers EventPrefabsClient TryAdd` -> `NetPackageEventPrefab::ProcessPackage`, `NetPackageWorldInitInfo::ProcessPackage`, ctor in `World/<LoadWorld>d__73::MoveNext`. CONFIRMED client-side receiver.

**quests-challenges.md "Quest criteria + reward leaves"**:
- `DumpMethod QuestCriteriaPOIWithinDistance CheckForQuestGiver` -> IL=9: `Int32.TryParse(Value)` result **popped**, then `ldc.i4.0 / ret`. **Hardcoded-false dead-code claim CONFIRMED**; additionally `grep -ci poiwithindistance "$CONFIG/quests.xml"` = 0, so no stock quest even references it. `DumpMethod BaseQuestCriteria CheckForQuestGiver/CheckForPlayer` -> `ldc.i4.1 / ret` stubs. CONFIRMED.
- `FindCallers QuestTierReward GiveRewards` -> only `QuestEventManager::HandleNewCompletedQuest`, whose IL compares `GetCurrentFactionTier` before/after and pays per matching `QuestTierReward::Tier`. CONFIRMED.

**combat-damage.md "Combat leaf types"**:
- `DumpMethod ApplyExplosionForce Explode` -> `ldc.r4 20` (power), `ldc.r4 1.75` (radius), `ldc.i4 1024` collider array, `OverlapSphereNonAlloc`, `AddExplosionForce(..., 3)` upwards; `FindCallers ApplyExplosionForce Explode` -> only `GameManager::ExplosionClient`. **Client-only claim CONFIRMED.**
- `DumpMethod DroneWeapons.StunBeamWeapon Fire` -> `ldstr _droneStunDamage` + `ItemValue::Quality`, `ldstr buffShocked`; `FindCallers StunBeamWeapon .ctor` -> only `EntityDrone::LoadMods`. CONFIRMED.
- `ItemActionAttack/AttackHitInfo` nesting per MethodList; `DumpMethod ItemActionAttack Hit` references all doc-named fields (`blockBeingDamaged, hitRef, bBlockHit, hardnessScale, itemsToDrop, bHarvestTool, entityHit, damageGiven, bKilled, isCriticalHit, materialCategory, WeaponTypeTag`); `Block::DamageBlock/OnBlockDamaged` signatures thread it, with `BlockMine`/`BlockBladeTrap` overrides. CONFIRMED. `BodyAnimator/BodyParts::.ctor(Transform,Transform)` exists per MethodList. CONFIRMED.

**entity-ai.md "Focus + target-selection leaves"**:
- `DumpMethod EAIBlockingTargetTask .ctor/CanExecute/Continue/Init` -> IL 3+3+3+7 = 16 total; `Init` sets `MutexBits=1`; CanExecute/Continue return `canExecute`. CONFIRMED.
- `DumpMethod EAIApproachAndAttackTarget Update` -> sets `canExecute=1` when `homeTimeout <= 0` (IL_014B-IL_0183) and `canExecute=0` + homeTimeout reset when `entityTarget.GetDamagedTarget() == theEntity` (IL_080B-IL_0858). CONFIRMED.
- `DumpMethod EAISetNearestEntityAsTargetSorter Compare` (IL=22, ascending `GetDistanceSq`); `FindCallers ... .ctor` -> `EAISetNearestEntityAsTarget::Init`, `EAISetNearestCorpseAsTarget::Init`, `EntityVulture::SetSleeper`. CONFIRMED (doc says 22 IL).
- `FindCallers AIFocusAim GetActiveFocus` -> only `EntityBandit::{updateTasks,GetAimTarget,GetHeadLookTarget}`; `FindCallers AIFocusBody GetActiveFocus` -> `EntityBandit::CalcStrafeYawOffset`; `FindCallers AIFocusBody .ctor` -> `EAIPathTest::Update`. **Bandit-only (+EAIPathTest) claim CONFIRMED.** `DumpMethod AIFocusAim GetActiveFocus` references belly/chest/head position getters + `AIAimFocusOffset` + `IsFocusDisabled`; `DumpMethod AIFocusConditionDistance IsFocusDisabled` -> 0 disables the check, missing anchor returns false (never disables), farther-than-`ConditionalDistanceSq` -> disabled. CONFIRMED.
