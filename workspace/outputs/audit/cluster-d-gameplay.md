# Cluster D audit: gameplay systems (items, blocks, crafting, loot, quests, progression, minevents, game-events, tile-entities-power)

**Verdict:** The nine docs are substantially correct against the V3.0.1 IL (serialization layouts, enum values, authority split, tick rates, and state-machine branches all check out), but `items.md` ships one wire-format error in the ItemValue Stats section (a dropped byte) plus a cluster of stale/conflicting leaf counts, and the sequence-requirements catalog mislabels five quest-requirement types as GameEvent leaves.

All commands below run from the repo root with:
`ASM="/home/maci/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll"`

---

## Findings

### F1 — CRITICAL — items.md §2 (ItemValue packing table, row 8 "Stats count")

> "| 8 | Stats count | `byte` | only if flags bit1; per stat two `i16` (raw value, then boosted value or `0`) |"

**Claim:** each Stats entry is two `i16`.
**Ground truth:** each entry is **one `byte` + two `i16`**. The IL writes the stat's `PassiveEffects` type id as a byte first, then `(isBoosted ? 0 : value)` as `i16`, then `(isBoosted ? value : 0)` as `i16`:

```
mono tools/bin/DumpMethod.exe "$ASM" ItemValue Write
  IL_013B: ldarg.1
  IL_013C: ldloc.s V_8
  IL_013E: ldfld PassiveEffects Stat::type
  IL_0143: callvirt System.Void System.IO.BinaryWriter::Write(System.Byte)   <- missing from doc
  ...
  IL_0175: callvirt System.Void System.IO.BinaryWriter::Write(System.Int16)
  IL_017D: callvirt System.Void System.IO.BinaryWriter::Write(System.Int16)
```

The section claims to be "authoritative for byte order"; a parser following the table desyncs by one byte per stat whenever flags bit1 is set. Also the two `i16` semantics are "unboosted-or-0, then boosted-or-0", not "raw value, then boosted value or 0" (the first `i16` is zeroed when the stat is boosted).
**Fix:** row 8 -> "per stat: `byte` PassiveEffects type, `i16` value (0 if boosted), `i16` boosted value (0 if not boosted)".

### F2 — MAJOR — items.md, header vs footer (ItemAction leaf count, internal contradiction)

> Header/Evidence: "41 concrete `ItemAction*` leaves" ... §4.1: "The 41 concrete `ItemAction*` leaves group into a handful of families."
> Footer: "**Leaf catalog:** ... (the 38 `ItemAction` leaves)."

Same file, two counts. The linked catalog `docs/inventories/item-actions.md` declares "**38 leaves.**" and contains exactly 38 rows (`grep -c '^| \`ItemAction' docs/inventories/item-actions.md` -> 38). DLL prefix count for cross-check: `mono tools/bin/MethodList.exe "$ASM" $SP/methods.txt; cut -d: -f1 $SP/methods.txt | sort -u | grep '^ItemAction' | grep -v 'Data\|Entry' | wc -l` -> 43 (includes abstract bases such as `ItemAction`, `ItemActionAttack`, `ItemActionUseOther` bases). Whichever denominator is intended, 41 and 38 cannot both be right in one doc.
**Fix:** recount concrete leaves from the assembly (abstractness-aware), use one number in header, §4.1, and footer.

### F3 — MAJOR — docs/inventories/sequence-requirements.md (referenced by game-events.md footer as "all 43 requirement leaves")

> game-events.md footer: "every instance in [`inventories/sequence-requirements.md`] (all 43 requirement leaves)."
> Catalog header: "Every `BaseRequirement` subclass (game-event gate ...). **43 leaves.**"

**Ground truth:** `GameEvent.SequenceRequirements` contains **39 types = 2 bases (`BaseRequirement`, `BaseOperationRequirement`) + 37 concrete leaves**, exactly as game-events.md §1/§4 itself states. Verified:

```
grep '^GameEvent.SequenceRequirements' $SP/types.txt | wc -l          -> 39
grep '^GameEvent.SequenceRequirements' $SP/types.txt | grep -v Base | wc -l -> 37
```

The 43-row catalog reaches 43 by (a) listing the abstract `BaseOperationRequirement` as a "leaf" and (b) including five types that are **not** in `GameEvent.SequenceRequirements` at all: `RequirementBuff`, `RequirementGroup`, `RequirementHolding`, `RequirementLevel`, `RequirementWearing` are the `Quests.Requirements` quest-offer gates (quests-challenges.md family, different base contract with `SetupRequirement`/`CheckRequirement`). Diff evidence:

```
comm -23 catalog-names dll-GameEvent-requirement-names ->
  BaseOperationRequirement, RequirementBuff, RequirementGroup,
  RequirementHolding, RequirementLevel, RequirementWearing
```

**Fix:** split the catalog (37 GameEvent leaves; move the 5 quest requirements to a quest catalog or mark their namespace), and fix the "43 leaves" header and the game-events.md footer reference.

### F4 — MINOR — items.md §2 rows 9-10 (ItemClassModifier skip scope)

> "| 9 | Modifications count | `byte` | **skipped entirely if the ItemClass is an `ItemClassModifier`** ..."

The skip branch jumps past **both** the Modifications and the CosmeticMods sections (rows 9-10a), landing directly at `Activated`:

```
mono tools/bin/DumpMethod.exe "$ASM" ItemValue Write
  IL_0194: isinst ItemClassModifier
  IL_0199: brtrue IL_0262          <- IL_0262 is the Activated write
```

The table marks only row 9 as conditional; a mod-item record also has no CosmeticMods count byte.
**Fix:** annotate rows 10/10a with the same condition.

### F5 — MINOR — items.md §3 ("ItemClass.Init allocates Actions = new ItemAction[5]")

The `new ItemAction[5]` allocation is in `ItemClass..ctor`, not `Init`:

```
mono tools/bin/DumpMethod.exe "$ASM" ItemClass .ctor | grep -B2 'newarr ItemAction'
  IL_0209: ldc.i4.5
  IL_020A: newarr ItemAction
mono tools/bin/DumpMethod.exe "$ASM" ItemClass Init | grep -c 'newarr ItemAction'  -> 0
```

The 5-slot claim itself is correct.
**Fix:** "ItemClass's constructor allocates ...".

### F6 — MINOR — crafting-recipes.md §3 (RecipeLockTypes characterization)

> "`RecipeUnlockData` / `RecipeLockTypes` define how a recipe is unlocked (skill level, perk, or a learned schematic item)" and the diagram's "RecipeLockTypes (skill / perk / schematic)".

**Ground truth:** `RecipeLockTypes.None=0, Item=1, Skill=2, Quest=4` (`mono tools/bin/EnumList.exe "$ASM" $SP/enums.txt; grep RecipeLockTypes $SP/enums.txt`). There is no perk member and the doc omits `Quest`. (Perk/schematic granularity lives in the separate `UnlockTypes` enum: None/Perk/Book/Skill/Schematic/ChallengeGroup/Challenge/PrefabEditorInvalid.)
**Fix:** state the exact members (None/Item/Skill/Quest) and, if wanted, mention `UnlockTypes` for the perk/schematic distinction.

### F7 — MINOR — tile-entities-power.md §2 (base TileEntity write table)

> "| 1 | version | `u16` | current write version is **19** ..." / "| 3 | `heapMapUpdateTime` | `u64` | disk mode only; network mode stops after `chunkPos` |"

The table implies the version is always written and only field 3 is disk-only. Actually the **version is also disk-mode-only**: network mode writes only `chunkPos`:

```
mono tools/bin/DumpMethod.exe "$ASM" TileEntity write
  IL_0000: ldarg.2
  IL_0001: brtrue.s IL_0024        <- StreamModeWrite != Persistency
  IL_0004: ldc.i4.s 19             <- version, disk branch only
  ...
  IL_0024: (network branch: chunkPos only, then ret)
```

**Fix:** mark row 1 disk-mode-only as well.

### F8 — MINOR — quests-challenges.md Evidence header + §1 (stale counts, four instances)

- "`Quest` 90 method bodies": the doc's own cited census says **96** (`grep '^| Quest |' il/surface-v3.0.1/surface-types.md` -> methods=96; `grep -c '^Quest::' $SP/methods.txt` -> 96). `QuestEventManager` 159 is correct.
- "`BaseObjective` + 45 `Objective*` type rows": the DLL has 42 method-bearing `Objective*` types (incl. 2 modifiers, 1 data helper, 1 nested) plus 2 enums; the linked catalog says **38 leaves** (38 rows) and omits the two `ObjectiveModifier*` types the doc's §3 table lists. 45, 40 (§3 table), and 38 (catalog) cannot all be the same population.
- "+ 29 `ChallengeObjective*`": DLL has **28** concrete `Challenges.ChallengeObjective*` types (`grep 'ChallengeObjective' $SP/types.txt` -> 28 concrete + `BaseChallengeObjective`).
- "`BaseReward` (+ 12 `Reward*` rows)": DLL has **10** concrete quest reward leaves, exactly the 10 the doc's own §4 list names (`grep '^Reward' $SP/types.txt`; the extra top-level `Reward` class with `get_Cost`/`get_Id` is unrelated).

**Fix:** regenerate the counts from the census with a fixed rule (concrete leaves only, name the rule) and align §1, §3, §4, and the catalog.

### F9 — MINOR — minevents.md footer + docs/inventories/minevent-actions.md ("71 leaves")

> "every instance is enumerated in [`inventories/minevent-actions.md`] (all 71 triggered-effect leaves)."

The 71-row catalog counts three **abstract bases** as leaves: `MinEventActionTargetedBase`, `MinEventActionBuffModifierBase`, `MinEventActionSoundBase` appear as rows. DLL: 72 `MinEventAction*` types total, 4 bases (the three above + `MinEventActionBase`), so **68 concrete leaves**. Diff:

```
comm: in catalog but not in concrete-DLL set ->
  MinEventActionBuffModifierBase, MinEventActionSoundBase, MinEventActionTargetedBase
```

**Fix:** either retitle to "71 rows (68 leaves + 3 abstract bases)" or drop the bases from the leaf count.

### F10 — MINOR — items.md Evidence header ("103 `Item*` types")

Census cross-check gives 106 `Item*`-prefixed rows (`grep -c '^| Item' il/surface-v3.0.1/surface-types.md` -> 106); the method-bearing type list gives 112 including nested. The doc's 103 matches neither obvious counting rule. Not necessarily wrong (the census rule may exclude interfaces/nested), but the number is not reproducible from the cited source as stated. **Fix:** state the counting rule or regenerate.

---

## Spot-verified CONFIRMED

Serialization / packing:

- **ItemValue.Write full order** (items.md §2): empty sentinel `0` / marker `9`; flags byte bit0 = `type >= Block.ItemsStartHere` (id written minus `ItemsStartHere`), bit1 = `Stats[]` present; `type` u16; `UseTimes` f32; `Quality` u16; `Meta` int->u16; metadata count byte + only non-null `TypedMetadataValue` entries; mods/cosmetics as count byte + per-slot `bool` + recursive `ItemValue.Write`; `Activated` byte; `SelectedAmmoTypeIndex` byte; `Seed` u16 zeroed when `type==0`; `TextureFullArray` presence bool + `Write`; trailing `NameIdMapping.MarkIdUsed` bookkeeping; `No ItemClass entry for type` error path; static overload writes single `0` for null. — `mono tools/bin/DumpMethod.exe "$ASM" ItemValue Write` (modulo F1/F4 above).
- **ItemStack.Write** (items.md §2): count clamped to 65535, written u16; `itemValue` written only when `count > 0`. — `DumpMethod ItemStack Write`.
- **BlockValue packing** (blocks.md §2): `type`=bits0-15 (`& 0xFFFF`), `rotation`=`>>16 & 31`, `meta3`=`>>21 & 1`, `meta`=`>>22 & 15`, `meta2`=`>>26 & 15`, `ischild`=bit30 (`0x40000000`), `hasdecal`=bit31 (`0x80000000`); `Write` = `rawData` u32 + `damage` u16 (6 bytes), `Read` mirrors; `isair`=`type==0`; `isTerrain`=`(uint)(type-1) < 239`; `isWater`={240,241,242}; `parentx = meta - 8`. — `DumpMethod BlockValue Write|Read|get_*`.
- **Base TileEntity.write** version 19 / `chunkPos` / `heapMapUpdateTime` u64 (see F7 nuance). — `DumpMethod TileEntity write`.
- **PowerManager.Write/roots model** methods present (`PowerManager::Write`, `PowerItem::SetParent`, `CircularParentCheck` in MethodList). — `MethodList.exe` grep.

Authority claims:

- **`Recipe.CanCraft` is client-UI-called only**: sole call site is `XUiC_ItemActionList::SetCraftingActionList` (plus `CanCraftAny` from `XUiM_Recipes::HasIngredientsForRecipe`). — `mono tools/bin/FindCallers.exe "$ASM" Recipe CanCraft | grep 'Recipe::CanCraft'`.
- **`TransactionalInventory` exists and is the transaction target** (46 method-list references; `InventoryTransaction::AddOperation(TransactionalInventory,...)`, `NetPackageInventoryTransactionRequest/Response` present). — MethodList grep.
- **Workstation queue is TE-side**: `TileEntityWorkstation::HandleRecipeQueue`, `cycleRecipeQueue`, `AddCraftComplete` exist; `UpdateTick` computes `timePassed = (GameTimer.ticks - lastTickTime) / 20` clamped to `BurnTotalTimeLeft`. — `DumpMethod TileEntityWorkstation UpdateTick` (`ldc.r4 20; div`).
- **`LootManager.LootContainerOpened`** (loot-economy.md §2): gates in order `IsServer` -> `IsEditor` -> `bTouched`; sets `bTouched` + `worldTimeTouched`; fires MinEvent **101** before the roll (remote via `NetPackageMinEventFire`, local via `FireEvent`) and **100** after cloning stacks into `items[]`; rolls only if container empty; loot stage = `GetHighestPartyLootStage(LootStageMod, LootStageBonus)` unless `useUnmodifiedLootstage` -> `unModifiedGameStage`. — `DumpMethod LootManager LootContainerOpened` (`ldc.i4.s 101` @ IL_00C0/IL_00EE, `ldc.i4.s 100` @ IL_0179). Enum names: `onSelfLootContainer=100`, `onSelfOpenLootContainer=101`.
- **`TraderManager.TraderInventoryRequested`** interval snap `lastInventoryUpdate = (now / interval) * interval + 1` then `HandleFullReset`. — `DumpMethod TraderManager TraderInventoryRequested` (`div.un; mul; ldc.i4.1; conv.i8; add`).
- **`TileEntityVendingMachine.Rent`**: fresh rent `rentalEndDay = WorldTimeToDays(worldTime) + 30`, re-rent `rentalEndDay += 30`; `RentTimeRemaining = rentalEndDay - WorldTimeToDays(now)`; `CanRent` codes match `RentResult` enum (Allowed=0, AlreadyRented=1, AlreadyRentingVM=2, NotEnoughMoney=3). — `DumpMethod TileEntityVendingMachine Rent` + EnumList.
- **`EntityAlive.FireEvent` fan-out order** (minevents.md §3): EntityClass.Effects -> Progression -> ChallengeJournal -> Inventory -> Equipment -> Buffs, exactly. — `DumpMethod EntityAlive FireEvent`.
- **GameEvent server gate + protocol**: `BaseAction.PerformAction` IL=39 returns `RequirementsNotMet`(2) on first failed requirement else `OnPerformAction()`; `GameEventActionSequence.Update` IL=287; `ActionBaseSpawn.OnPerformAction` IL=829. — `DumpMethod` headers/bodies.

Enums (all via `EnumList.exe` + grep):

- `Block/DestroyedResult`: None=0, Keep=1, Downgrade=2, Remove=3; base `Block.OnBlockDestroyedBy` IL=2 = `ldc.i4.2; ret` (returns Downgrade).
- `TileEntityType`: Collector=3, VendingMachine=7, Forge=8, Workstation=12, Powered=15, PowerSource=16, PowerRangeTrap=17, Light=18, Trigger=19, Sleeper=20, PowerMeleeTrap=21, Composite=25; classless tags None(0)/LandClaim(4)/Loot(5)/Trader(6)/Campfire(9)/SecureLoot(10)/SecureDoor(11)/Sign(13)/GoreBlock(14)/SecureLootSigned(22)/Taskboard(27) all present. `InstantiateFromRead` switches on `type - 3` with exactly the 12 claimed `newobj` targets and logs `Dropping TE with unknown/outdated type` otherwise; `TileEntityLegacyUtils.TryReadLegacyType` consulted first. — `DumpMethod TileEntity InstantiateFromRead`.
- `PowerItemTypes` 1..11 exactly as tabled; `PowerTrigger/TriggerTypes` Switch=0..TripWire=4.
- `QuestState` 0-4, `ObjectiveStates` 0-4, `ChallengeStates` 0-2, `ReceiveStages` 0-2, `CompletionTypes` AutoComplete=0/TurnIn=1, `QuestEventTypes` (TryRallyMarker=0, LockPOI=7, UnlockPOI=8, ClearSleeper=9, SetupFetch=12, FinishManagedQuest=14, ResetTraderQuests=16).
- `MinEventTypes`: 111 named values 0..110 + COUNT=111 (112 rows); `SourceParentType` ItemClass=1..ChallengeGroup=7; MinEvent `TargetTypes` self=0..selfOtherPlayers=5; ranged-trap mask Self=1/Allies=2/Strangers=4/Zombies=8.
- `BaseAction/ActionCompleteStates` 0-3, `SpawnUpdateTypes` 0-2, `NetPackageGameEventResponse/ResponseTypes` (Denied=0, Approved=1, TwitchRefundNeeded=3, EntitySpawned=5..BlockDamaged=11, ClientSequenceAction=12, Completed=13).
- Pref/stat ids: `EnumGamePrefs.DayNightLength=60`, `LootAbundance=87`, `LootRespawnDays=88`; `SandboxOptions.TraderSellPrices=130`, `TraderBuyPrices=131`; `PassiveEffects.EconomicValue=76`, `BarteringBuying=148`, `BarteringSelling=149`; `EnumGameStats.BloodMoonDay=58`; `TraderHourPresets` Default=0..AlwaysOpen=6; `eSetBlockResponse` Success=0 / PowerBlockLimitExceeded=1 / StorageBlockLimitExceeded=2.

Tick rates / state machines:

- **PowerManager.Update** (tile-entities-power.md §3.2): early-outs on null world / zero players; `IsServer` + `IsGameStarted` gate; countdown timer reset to **0.16** (`ldc.r4 0.16`) around the source loop (`PowerSource::Update`) then trigger loop (`PowerTrigger::CachedUpdateCall`); save timer reset to **120** (`ldc.r4 120`) -> `SavePowerManager()` on background-thread check; `ClientUpdateList` flushed every call. ~6.25 Hz claim is exactly 1/0.16. — `DumpMethod PowerManager Update`.
- **Block tick**: base `Block.GetTickRate` = `ldc.i4.s 10` (returns 10); `BlockPlantGrowing.UpdateTick` IL=239 as cited. — `DumpMethod Block GetTickRate`.
- **Damage engine**: `Block.DamageBlock` IL=12 forwards to `OnBlockDamaged` (IL=497, `_recDepth`); `ChunkCluster::InvokeOnBlockDamagedDelegates` exists; `ChunkCluster.SetBlock` heavy overload IL=828; `Block.Init` IL=2136, `LateInit` IL=275 as cited. — `DumpMethod` headers.
- **CanPlaceBlockAt**: rejects `y > 253` (`ldc.i4 253; ble`), multiblock footprint must stay `< 254` (`ldc.i4 254; blt`). — `DumpMethod Block CanPlaceBlockAt`.
- **Item degradation** (items.md §7): `HandleDegradation` no-ops when `ItemMaxDegrationAmount == 0`, seeds `DurabilityModifier` metadata at 1.0, subtracts `ItemMaxDegrationAmount` per call, floors at **0.05** via `Mathf.Max`. — `DumpMethod ItemAction HandleDegradation`.
- **Action slots** (items.md §3-4): `Inventory.GetHoldingPrimary` = `Actions[0]`, `GetHoldingSecondary` = `Actions[1]`; `ItemClass.StartHolding` loops slots `< 3`; `ItemClass.ExecuteAction` gates `ItemActionDynamicMelee` on the opposite slot's `IsActionRunning` (checks both `actionData[0]` and `actionData[1]`). — `DumpMethod Inventory GetHoldingPrimary|GetHoldingSecondary`, `ItemClass StartHolding|ExecuteAction`.

Structure / negative claims:

- **No `BlockLoot` / `BlockSecureLoot` / `BlockLandClaim` / `TileEntityLootContainer` classes** (blocks.md §8, loot-economy.md §1, tile-entities-power.md §1.1): zero matches in the full type list; `TEFeatureStorage`, `TileEntityComposite`, `TileEntityCompositeData` present. — types.txt grep.
- **Census-backed counts that do match**: `Block*` = 138 types; TileEntity census rows = 19 (incl. the `TileEntityType` enum, matching "19 TileEntity* types"); `QuestEventManager` = 159 bodies; `Quests`+`Quests.Requirements` = 7 types / 48 bodies; `Challenges` = 48 census types; GameEvent namespaces = 132 SequenceActions + 39 SequenceRequirements + 2 Decisions + 3 Loops + 3 GameEventHelpers = 179 types; block-behaviors catalog 65 rows = its header. — census + methods.txt greps.
- **Workstation/forge/trader/quest methods cited all exist** (`TEFeatureStorage.UpdateTick/Reset`, `LootManager.LootBagOpened`, `EntityTrader.TransitionToNextWindow`, `QuestEventManager.HandlePlayerDisconnect`, `Quest.StartQuest/AdvancePhase/CloseQuest`, `Progression.AddLevelExp/SpendSkillPoints`, `TileEntityPowered.InitializePowerData`, `WorldBase.SetBlockRPC`, `Inventory.DecHoldingItem/GetBestQuickSwapSlot`, `ItemActionEat.consume`, `ItemActionRanged.ConsumeAmmo`, `ItemAction.getBuffActions/ExecuteBuffActions`, `ItemValue.FireEvent`). — MethodList grep.

Not independently verified (flagged, not asserted wrong): backpack-vs-workstation queue *tick location* beyond the `CanCraft` caller evidence (the client-side `RecipeQueueItem` tick loop itself was not traced); `XUiM_Trader` price formula constants beyond the passive-effect ids; `ChallengeJournal`/daily-rotation internals; the census counting rule behind "103 Item* types" (F10).
