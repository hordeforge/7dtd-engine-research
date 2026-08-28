# V3.1.0 → V3.2.0 exact-difference changelog

**Hub:** [`INDEX.md`](INDEX.md).

**Scope:** stock dedicated `Assembly-CSharp.dll`, 7 Days to Die.
**From:** V3.1.0 b14 (Major=3 Minor=10 Build=14, "Henpocalypse").
**To:** V3.2.0 b9 (Major=3 Minor=20 Build=9).
**Method:** pairwise IL diff of the tracked V3.1.0 dump sets (`il/*-v3.1.0/`)
against freshly regenerated V3.2.0 sets (`il/*-v3.2.0/`), plus the machine
pins in [`tools/data/stock_facts.json`](../tools/data/stock_facts.json) and
[`tools/data/xml_pins.json`](../tools/data/xml_pins.json).
**Date:** 2026-08-28. All IL line counts are exact from the dumps.
**Honesty:** facts marked `verified` were read directly from IL in both dumps;
`inferred` means the IL implies it but no live probe confirmed it. Official
feature names come from the V3.2.0 Stable Steam announcement (2026-08-25).

---

## 1. Machine pins (verified)

| Pin | V3.1.0 | V3.2.0 | Note |
|---|---:|---:|---|
| Version display | `V 3.1.0` | `V 3.2.0` | `Constants.cVersionMajor/Minor/Build` (cctor IL: minor 10→20, build 14→9) |
| Wire version | `V3.1.0 b14` | `V3.2.0 b9` | |
| Top-level types (Census) | 4414 | **4426** | +12 |
| Methods with body (top-level) | 44107 | **44277** | +170 |
| All types (incl. nested) | 7451 | 7451 | census; unchanged shape |
| NetPackage* top-level | 193 | **195** | +3 added, −1 removed |
| WorldState.SaveLoad(Stream) IL | 926 | 926 | unchanged |
| GameManager.gmUpdate IL | 631 | 631 | unchanged |
| TPS / tick duration | 20 / 0.05 s | 20 / 0.05 s | unchanged |
| Default port / max MP | 26900 / 8 | 26900 / 8 | unchanged |
| Challenge marker / size | 0xCA / 17 | 0xCA / 17 | unchanged |
| Chunk dims | 256 / 64 / 16 | 256 / 64 / 16 | unchanged |
| CurrentSaveVersion | 23 | 23 | **save format unchanged** |
| game_reset_revision | 13 | 13 | unchanged |
| XML data pins (`xml_pins.json`) | — | byte-identical | zombie HP ladder, trader economy, survival thresholds unchanged |
| EnumGameStats / EnumGamePrefs | 82 / 317 | 82 / 317 | unchanged |

Everything else pinned by `stock_facts.json` (sim, network, chunk, save,
behaviour, enums, litenet) is unchanged. The 3.2.0 build is a **bug-fix /
QoL patch**: no save, chunk, or core-loop format change.

## 2. Type-level diff (verified)

- **+70 type files** in the full dump, **−51**, **7381 common** (115 changed).
- Most additions/removals are compiler-generated churn: async state machines
  renumbered (`_d__N` → `_d__N+1`) because the parent method's IL grew, Burst
  `BurstDirectCall`/`PostfixBurstDelegate` pairs renamed by new hash, and
  `_PrivateImplementationDetails` blob ids regenerated (every byte blob that
  changed content gets a new hash name).
- **Real new types (V3.2.0):**
  - `NetPackagePOIMetadataRequest`, `NetPackagePOIMetadataResponse` (wire)
  - `NetPackageConfirmSpawnEntity` (wire)
  - `PrefabInstance.POIMetadata` (wire record)
  - `IDesignatedArea`, `DesignatedAreaStore<T>` (incl. `<>c`), `DecoSuppressArea`
  - `TraderDoorController`, `TEFeatureDoor.HonkOpenTypes`
  - `EntityPlayerLocal.SpawnRequest`
  - `ItemActionEntryCombine`
  - `ActionBlockDoorState.OpenDoorStates`, `ActionBaseBlockAction.<UpdateBlocks>d__30`
  - `XUiBindingHelper`
  - `DynamicPrefabDecorator.<CopyWorldPrefabHeightsIntoHeightMap>d__97`,
    `.<Load>d__24`, `.<RequestWorldPOIMetadataFromServer>d__34`
- **Real removed types (V3.2.0):**
  - `NetPackagePOIAround` (wire; replaced by the POI metadata packages)
  - `DynamicPrefabDecorator.TraderComparer` (binary search replaced by
    `DesignatedAreaStore`)
  - `ItemClassHeldEntity.<waitForEntitySpawn>d__57` (async spawn wait removed)
  - `DownloadableContentValidator.<CheckDlcPurchases>d__8` (Steam),
    `Helper.<LoginEventAnalyticCoroutine>d__3` (analytics)
  - `XUiC_CharacterCosmeticsListWindow.<>c__DisplayClass10_0`

Full new/removed lists: regenerable with
`tools/dump_diff.py` + `comm` on `il/full-v3.1.0/` vs `il/full-v3.2.0/`.

## 3. Wire changes (all verified from read/write/ProcessPackage IL)

### 3.1 NetPackageDamageEntity — packed flags + KillXPScale (breaking)

The single most important wire change. `write` IL 176→144, `read` 163→131,
`Setup` 141→235, `ProcessPackage` 172→226.

- Ten booleans (`bPainHit`, `bFatal`, `bCritical`, `bIgnoreConsecutiveDamages`,
  `bDismember`, `bCrippleLegs`, `bTurnIntoCrawler`, `bFromBuff`,
  `bIgnorePartyShare`, `canHitSpecialBodyParts`) are packed into one
  **`UInt32 flags`** bitfield written right after `entityId`.
- `bIsDamageTransfer` is **removed** (no replacement bit).
- `KillXPScale` (`Single`, from `DamageSource.KillXPScale`) is **added** before
  `damageMultiplier`.
- `attackerEntityId` moved up (after `movementState`, was after `bCritical`).
- Flag bits (from `Setup` IL `or` constants; also `cFlags*` static fields):

| Bit | Mask | Meaning |
|---|---|---|
| 0 | 0x001 | canHitSpecialBodyParts |
| 1 | 0x002 | CrippleLegs |
| 2 | 0x004 | Critical |
| 3 | 0x008 | Dismember |
| 4 | 0x010 | Fatal |
| 5 | 0x020 | FromBuff |
| 6 | 0x040 | IgnoreConsecutiveDamages |
| 7 | 0x080 | IgnorePartyShare |
| 8 | 0x100 | PainHit |
| 9 | 0x200 | TurnIntoCrawler |
| 10 | 0x400 | TrapKillXP (new) |

New wire order: `entityId:i32, flags:u32, damageSrc:u8, damageTyp:u8,
strength:u16, hitDirection:u8, hitBodyPart:i16, movementState:u8,
attackerEntityId:i32, dirV:3×f32, blockPos:Vector3i, hitTransformName:string,
hitTransformPosition:3×f32, uvHit:2×f32, KillXPScale:f32, damageMultiplier:f32,
random:f32, bonusDamageType:u8, StunType:u8, StunDuration:f32, ArmorSlot:u8,
ArmorSlotGroup:u8, ArmorDamage:u16, attackingItem:bool+ItemValue`.
A V3.1.0 peer cannot parse a V3.2.0 body. Docs: [protocol.md](protocol.md) §6.5,
[protocol-packages.md](protocol-packages.md) §6.11.

### 3.2 POI metadata: NetPackagePOIAround removed, Request/Response added

- **Removed** `NetPackagePOIAround` (S2C, channel 1, compressed, blob of nearby
  prefab dictionaries built by the server on demand).
- **Added** `NetPackagePOIMetadataRequest` (C2S, empty body, direction 1):
  `ProcessPackage` calls
  `DynamicPrefabDecorator.SendPOIMetadataToClient(Sender)`.
- **Added** `NetPackagePOIMetadataResponse` (S2C, compressed, direction 2):
  `List<PrefabInstance.POIMetadata>`. Record layout (read ctor IL=35):
  `position:Vector3i, size:Vector3i, rotation:u8, tier:u8 (Prefab.DifficultyTier),
  traderArea:bool (Prefab.bTraderArea), prefabName:string, tags:string (Poi tags),
  questTags:string (Global tags)`.
- Client trigger: `DynamicPrefabDecorator.RequestWorldPOIMetadataFromServer()`;
  server handler `ProcessPOIMetadataReceived`; companion `World.GetTraderAreaOuterAt`,
  `DynamicPrefabDecorator.GetTraderOuterAtPosition`.
- Official note: "Custom POI's should be pushed to client from server (server
  pushes a minimal metadata package to client)".
- Docs: [protocol-packages.md](protocol-packages.md) § POI metadata.

### 3.3 NetPackageConfirmSpawnEntity (new) + EntityCreationData tail

- **Added** `NetPackageConfirmSpawnEntity` (S2C, `GetLength=20`):
  `createdEntityId:i64` (Int32 field, conv.i8) + `key:bytes[16]`
  (Guid.ToByteArray). Client `ProcessPackage` (IL=24):
  `EntityPlayerLocal.HandleRequestedEntitySpawn(key, entity)` (new method).
- `EntityCreationData` gained `requestedBy:Int32` + `requestKey:Guid`, written
  at the very end of the spawn body (after `stressAmount`), always emitted by
  `write` (IL=372, was 362), consumed by `read` only when
  `readFileVersion >= 37` (read IL=528, was 507).
- Server side: new `GameManager.SpawnEntityServer(ecd)`; 
  `RequestToSpawnEntityServer` IL 101→37 (delegates). Client side:
  `EntityPlayerLocal.SpawnRequest` type + `HandleRequestedEntitySpawn`.
- Docs: [protocol-packages.md](protocol-packages.md) §5.1/§5.1.2,
  [spawning.md](spawning.md).

### 3.4 ItemValue: Activated byte → Flags bitfield (wire-compatible)

- `ItemValue.Activated` (byte field) replaced by `Flags` (byte bitfield) +
  constants `cFlagsActivated` (1) and `cFlagsWasCombined` (2).
  `get_Activated` = `Flags & 1`, `get_WasCombined` = `Flags & 2` (new);
  `set_Activated` masks with 0xFE. Same wire position/width → **not breaking**.
- Drives the Combine Station rework: combined items carry `WasCombined`.
- Docs: [items.md](items.md) §2 row 11, §7.1.

### 3.5 Compress/channel census (META)

8 compressed packages in both versions; the set changed by
`NetPackagePOIAround` → `NetPackagePOIMetadataResponse`.
`NetPackageConfirmSpawnEntity` inherits channel/compress; direction 2.

## 4. Features (IL evidence + official release notes)

### 4.1 Trader doors open via vehicle horn ("HONK HONK!!!")

- `TEFeatureDoor`: new props `PropHonkOpenType`/`PropHonkOpenDistance` →
  fields `HonkOpenType` (enum `None, Trader, TraderOuter, LandClaim, Both, All`)
  + `HonkOpenDistance` (Single). `SetBlockEntityData` IL 10→104 (registers with
  `TraderDoorController`), new `OnUnload` (unregisters).
- `TraderDoorController` (new MonoBehaviour): static `ControllerDictionary` by
  door position; `OnTriggerEnter/Exit` detect vehicles in the door trigger
  volume; `Activate()` = locked (`TEFeatureLockable`) → ret, else
  `SetOpen(!IsOpen(), true)`.
- `Vehicle.GetHornEventName()` (new) = `onHonkEvent`; `EntityVehicle.UseHorn`
  plays horn + fires the honk game event. `ActionBlockDoorState` gained
  `OpenDoorStates setOpen` (with `traderOnly`, `animate` props) and
  `AllowInTrader()`.
- `EntityVehicle` field change: the string props `PropOnHonkEvent`/`onHonkEvent`
  are **removed**; new fields `HornActivation` (`TraderDoorController`
  reference, set while interacting with a door trigger) + `lastHonkEventTime`
  (honk cooldown). `Entity.Detach` clears the `XUiC_InteractionPrompt` text
  when the vehicle had a live `HornActivation` — the "close enough to honk"
  onscreen prompt (§4.9).
- Official notes: horn opens outer trader doors; new `oldWoodDoorNoHonk` door
  variant for trader interiors; Rekt/Hugh/Joel interiors switched to it.
- Docs: [tile-entities-power.md](tile-entities-power.md),
  [vehicles-drones-turrets.md](vehicles-drones-turrets.md).

### 4.2 Combine Station UI rework + combine marking

- New `ItemActionEntryCombine`; `XUiC_CombineGrid` reworked: `result` stack
  with live durability/icon bindings, explicit `btnCombine` button (+17 new
  binding methods); `ItemValue.WasCombined` marking (§3.4).
- Official notes: combine station UI rework, "plus" indicator for combined
  items, explicit combine button.
- Docs: [items.md](items.md) §7.1.

### 4.3 Kill XP rework (trap XP + party share)

- New `DamageSource.bTrapKillXP` + `KillXPScale` fields (ride the
  DamageEntity wire, §3.1); ctor IL 23→26 / 26→29.
- New `EntityAlive.AwardKillXPServer` (IL=62): no XP for buff kills, killer
  must be a distinct player; `scale = KillXPScale`; when `bTrapKillXP`:
  `scale *= EffectManager.GetValue(PassiveEffects.ElectricalTrapXP = 169,
  killer.holdingItem, ...)`; then `EntityPlayer.AddKillXP(this, AttackingItem,
  scale)`.
- New `EntityAlive.PartyShareKillServer` (IL=47): skips when
  `bIgnorePartyShare` or `bTrapKillXP` or `(int)KillXPScale != 1` or
  (BuffClass non-null and `Buffs.GetCustomVar("ETrapHit") == 1`); else
  `GameManager.SharedKillServer(victimId, killerId, 1.0)`.
- Call-site consolidation: in V3.1.0 `EntityPlayer.AddKillXP` was called from
  `BlockProjectileMoveScript`, `EntityVehicle`, `Explosion`,
  `ItemActionAttack`, `EntityBuffs`; in V3.2.0 only `EntityAlive` (via
  `ClientKill`) and `EntityBuffs` call it. `ClientKill` IL 216→205,
  `EntityPlayer.AddKillXP` IL 99→89.
- Not in the official notes verbatim; inferred intent: trap kills scale XP via
  the killer's `ElectricalTrapXP` passive and do not party-share.
- Docs: [combat-damage.md](combat-damage.md) §3.1a.

### 4.4 Timid animals / runaway AI

- `EntityFlags.Timid = 32` **added** (between Edible=16 and All).
- `EAIRunawayFromEntity` reworked: `targetClasses` (class-list) +
  `minSneakDistance` removed; now `flags`/`safeFlags` (EntityFlags),
  `safeDistance` + new `dangerDistance`, `entityList`; `SetData` IL 50→34,
  `FindEnemy` IL 166→136, `CanExecute` IL 12→11.
- Official notes: "Timid animals have improved threat detection" and
  "Rabbits running too slow" (rabbits are `Timid`; the `dangerDistance`
  threshold and flag-based `FindEnemy` change when they start fleeing).
- Docs: [entity-ai.md](entity-ai.md) § EAIRunawayFromEntity.

### 4.5 Decoration suppression (AllowDecorations)

- New `DecoSuppressArea`, `IDesignatedArea`, `DesignatedAreaStore<T>`;
  `DynamicPrefabDecorator` swapped `traderAreas` list + `TraderComparer` for
  `DesignatedAreaStore` `traderStore` + `decoSuppressStore`; new
  `AddDecoSuppressArea`, `ClearDecoSuppressAreas`, `IsWithinDecoSuppressArea`,
  `IsDecorationSuppressedAt`, `GetTraderOuterAtPosition`.
- `WorldDecoratorBlocksFromBiome.decoratePrefabs` gained
  `_chunkOverlapsSuppressArea` parameter (was `_chunkOverlapsTrader`).
- `Prefab` property set changed: `cProp_AllowTopSoilDecorations` removed
  (official: "Removed obsolete prefab property AllowTopSoilDecorations"),
  `AllowDecorations` added (official: "Property 'AllowDecorations' to separate
  world decoration in POIs from TraderArea setting").
- Docs: [world-generation.md](world-generation.md), [spawning.md](spawning.md).

### 4.6 Challenges / quests

- `Challenge.CompleteChallenge(forceRedeem, giveReward, forceComplete)` and
  `HandleComplete(showTooltip, forceComplete)` gained `forceComplete`;
  `Redeem()` IL 27→111. `ChallengeBaseTrackedItemObjective`,
  `ChallengeObjectiveCraft/Gather*/Kill*/WindowOpen`, `BaseChallengeObjective`
  changed by 1-2 IL (re-entry guard).
- Docs: [quests-challenges.md](quests-challenges.md).

### 4.7 Sandbox options / analytics

- No sandbox option added/removed (`SetupOptions` IL 3857→3865, same strings).
- `SandboxOptionValueSet{Bool,Float,Int}.GetDisplayAtIndex` gained a
  `languageName` parameter; `BaseSandboxOption` gained
  `GetDefaultValueText(languageName)` / `GetValueTextFromIndex(index, languageName)`.
- Analytics: `Helper` gained `GetSandboxSettingsDelta(preset)` (sends sandbox
  preset deltas), `GetSaveID`, `GetServerPlayerCount`, `LogDlcEntitlementsAnalytic`;
  `HeartbeatEventData` gained `PlayerCount` (nullable); `BaseEventData` gained
  `Platform`/`Provider`; `LoginEventData` moved Platform/Provider to base.

### 4.8 DLC / entitlement

- `DownloadableContentValidator` (Steam + Local) gained
  `GetAcquiredDate(EntitlementSetEnum)` + `GetEntitlementSetId(EntitlementSetEnum)`;
  `EntitlementManager` same. `Platform.Shared.Utils` gained `IsFamilyShare()`;
  Steam `DownloadableContentValidator.Init` stores `IPlatform _owner`.
- `XUiC_DlcList` / `XUiC_CharacterCosmeticsListWindow` re-pinned; new cosmetic
  DLC content per official notes ("New Free Cosmetic Skins & DLC" era content).

### 4.9 Fixes (IL-visible)

- `Entity.Detach` IL 79→92 — **new:** if the detached entity is an
  `EntityVehicle` with a live `HornActivation` (`TraderDoorController`), clear
  the `XUiC_InteractionPrompt` text ("close enough to honk" prompt); also the
  likely NRE guard for the horn-prompt/exit path ("NRE when exiting game after
  client drops Chicken").
- `EntityPlayer.AddKillXP` IL 99→89 — XP award path reworked
  (`NetPackageEntityAddExpClient.Setup(...)` with `XPTypes`); part of §4.3 and
  the "Permadeade does not grant Base Skill Points upon death" fix (the
  skill-point grant rides the same award path).
- `LootContainer.SpawnItem` IL 391→394 + `TraderInfo.SpawnItem` IL 232→235 —
  **Loot/Trader Max Tier clamp guard** (`LootMaxTier != -1` / `TraderMaxTier
  != -1` branch before the tier clamp), the "Loot Max Tier clamps user mods"
  fix. (The cotton loot/trader changes are XML content, no IL delta.)
- `SleeperVolume`: `WakeAttackLater` coroutine renumbered d104→d105; new
  DisplayClass102; `EntityAlive.updateCurrentBlockPosAndValue` IL 318→341
  (chunk visibility pass). Official: "Optimized sleeper spawn checks for
  player visibility when players are far".
- `EntityPlayerLocal.IsOnLadder()` (new) — chicken-stress-ladder fix.
- `BlockProjectileMoveScript.checkCollision` IL 299→250 — demolition-zombie
  client-damage explosion fix.
- `ItemClassHeldEntity.updateTimer` IL 227→232 — chicken toolbelt fix.
- `Platform.EOS.SessionsClient.searchFinishedCallback` IL 280→283 — the
  "Failed to search EOS servers popup" fix.
- `Inventory.GetLightLevel` / `syncHeldItem` IL changes; `Equipment.SetSlotItem`
  same-size change; `PlayerMoveController.Update` IL 2706→2735,
  `updateRespawn` 1209→1215; `Localization.UnloadUnusedLanguages` IL 114→106;
  `Platform.Steam.Constants` cctor change; `DamageSource` fields
  `bTrapKillXP`/`KillXPScale` (§4.3).

### 4.10 StockFileHashes — all regenerated

Every entry in the `StockFileHashes` cctor blob has new
`_PrivateImplementationDetails` byte-hash ids — the anti-cheat stock file hash
table was regenerated for the new content (expected for any content patch).

## 5. Official V3.2.0 changelog (TFP, for cross-reference)

Source: Steam announcement "V3.2.0 Stable" (2026-08-25). Items with IL
evidence above are marked; the rest are content/XML-level and produce no
managed-code delta:

**Added:** new buff icons for chicken stress events; custom POIs pushed to
client (server pushes a minimal metadata package) — §3.2; vehicle horn opens
trader outer doors — §4.1; new door variant `oldWoodDoorNoHonk` — §4.1;
`AllowDecorations` property — §4.5.

**Changed:** cooking pot/grill/anvil requirement logic (no managed delta —
XML requirements); campfire `IsTerrainDecoration=false` (XML);
auto turrets no longer support stability / can't be placed on walls (XML
item/entity classes; no managed delta); junk loot + trader inventory cotton
(XML loot/trader lists; no managed delta — the +3 IL in
`LootContainer`/`TraderInfo.SpawnItem` is the Max-Tier clamp, §4.9);
timid animals improved threat detection — §4.4; some Chinese localization
strings (content); optimized sleeper spawn checks — §4.9; screamer spawns
commented out in entitygroups.xml (XML); interior trader doors switched to
`oldWoodDoorNoHonk` (XML/prefabs); removed obsolete `AllowTopSoilDecorations` — §4.5.

**Fixed:** NRE exiting game after client drops Chicken — §4.9 (`Entity.Detach`
prompt cleanup); chicken stress on ladder — §4.9; chickens moved between
toolbelt slots — §4.9; unable to craft lower-tier items after unlock
(no managed delta found — recipe-unlock data is XML); demolition zombies not
exploding from client damage — §4.9; rabbits running too slow — §4.4
(`dangerDistance`/runaway rework; no speed constant delta); permadeath base
skill points — §4.9 (`AddKillXP` rework); Loot Max Tier clamps user mods —
§4.9 (`LootMaxTier`/`TraderMaxTier` guards); entities causing blocks to
collapse during chunk resets (no managed delta located; likely
`World.ResetPOIS` coroutine re-flow, d__378→d__379, not individually
attributed); failed EOS server search popup — §4.9; trader progression stuck
(no managed delta located); cave_05 quest boundaries inside POI (no managed
delta located; `Quest`/`QuestsFromXml` changed 1-2 IL, not individually
attributed).

### 5a. V3.1.0 (Henpocalypse) official changelog cross-check

Source: Steam announcement "V3.1.0 Henpocalypse Stable Release" (2026-07-27)
+ its "V3.1.0 b14 Changelog". Ran so prior-release items are not silently
carried into the 3.2.0 corpus without a status. Full feature inventory with
RE/implementation pointers: [`changelog-3.1.0.md`](changelog-3.1.0.md).
Managed-relevant items and their corpus home:

| V3.1.0 official item | Status |
|---|---|
| Chicken farming: catch/carry (held entities), coop workstation, stress events | **covered** — [items.md](items.md) § Held entities, [tile-entities-power.md](tile-entities-power.md), [sandbox-options.md](sandbox-options.md) |
| New sandbox options (ChickenCoopTime/Output/Input, ChickenStressEvent, InfectionChance, HungerMultiplier, ThirstMultiplier, StackSizeMultiplier) + day/night + enemy/animal density/respawn split | **covered** — [sandbox-options.md](sandbox-options.md) §2-3, INDEX delta map |
| Diamond Blade Tip mod in trader/loot lists | content (XML) |
| Discord DM-audible / cancel-login / unlink | client UI + platform SDK; dedi surface only via `DiscordManager` (minimal, see [dedicated-misc-systems.md](dedicated-misc-systems.md)) |
| Fix: "Player inventory data could be sent to server when nothing had changed" | **covered** — the inventory transaction hash guard ([items.md](items.md) § Inventory transactions; `NetPackageInventoryDataRequest/Response` keyHash+Guid, protocol-packages.md) |
| Fix: "Celebration Sandbox Option no longer blocks shared XP" | **covered** — the party-share XP path (`PartyShareKillServer`, §4.3 / combat-damage.md §3.1a) |
| Fix: "EOS exception in TileEntityNetPackage during POI reset" | **not narrated** — the EOS exception guard in the TE-net/POI-reset path is present in the 3.2.0 dump but has no dedicated prose; see residuals.md (annotation backlog) |
| Fix: "Serverside EXC related to memory stream" | **not narrated** — pooled-stream guard; no dedicated prose (annotation backlog) |
| Fix: "Corruption when rapidly loading/unloading multiple chunks" | **not narrated** — chunk streaming edge-case fix; no dedicated prose (annotation backlog) |
| Fix: "RequirementItemModTier did not check for null in slots" | **not narrated** — item-mod tier requirement null guard (annotation backlog) |
| Remaining b14 hotfix entries (workstation UI, controller icons, server filter paging, prefab editor, invites, etc.) | client/UI/content; out of dedi scope |

## 6. What did NOT change (verified)

- Save format: `CurrentSaveVersion` 23, `WorldState.SaveLoad` IL 926, TE
  versions, `EntityCreationData` `readFileVersion` gates unchanged (except the
  new ≥37 tail).
- Core loop: `gmUpdate` 631 IL, tick 20 TPS, frame order, net pump position.
- World/chunk constants: dims, layers, water level 62.88, heightmaps.
- Challenge marker 0xCA, LiteNetLib pins (protocol 13, MTU 1432, PossibleMtu
  1024-1432), default port 26900, max MP 8, EAC-adjacent structures.
- XML data pins byte-identical (zombie HP ladder, trader economy, survival
  thresholds, `xmlsToLoad`).
- `NetPackageTileEntity` (V3.1.0 change from 3.0.1) unchanged on 3.2.0.
- Console command registry (`CmdMap.exe` output, committed
  `docs/inventories/console-command-list.tsv`) byte-identical: no commands
  added, removed, or re-registered.
- `StockFileHashes` content *changed* (all blob ids regenerated) but the
  table shape (count, names) is unchanged.

## 7. Reproduce

```bash
# baseline (3.1.0 dumps already in il/, git-ignored)
# dump 3.2.0:
ASM=".../Assembly-CSharp.dll" ./tools/regen.sh   # (fails at pin check by design; dump steps then run)
# or the manual equivalent used for this diff: /tmp/dump320.sh steps
# diff:
python3 tools/dump_diff.py il/full-v3.1.0 il/full-v3.2.0 '.*'   # method-level
comm -13 <(cd il/full-v3.1.0 && find . -name '*.il.txt' | sort) \
         <(cd il/full-v3.2.0 && find . -name '*.il.txt' | sort)  # new types
# facts:
mono tools/bin/StockFacts.exe "$ASM" /tmp/facts.json
python3 -c '...'  # diff vs tools/data/stock_facts.json
```

`tools/data/stock_facts.json` + `xml_pins.json` were re-extracted from the
live 3.2.0 b9 install on 2026-08-28; the pinned facts diff vs the committed
3.1.0 artifact is exactly the table in §1.
