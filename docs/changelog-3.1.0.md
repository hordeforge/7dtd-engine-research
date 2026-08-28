# V3.1.0 "Henpocalypse" changelog digest (feature inventory + RE map)

**Hub:** [`INDEX.md`](INDEX.md).
**Version:** V3.1.0 b14 (Major=3 Minor=10 Build=14). Stable 2026-07-27
("Henpocalypse"; MP-invite hotfix b14 shipped with the stable branch).
**Sources:** Steam announcement "V3.1.0 Henpocalypse Stable Release - MP
Invite Bug Hotfixed" + its "V3.1.0 b14 Changelog" section.
**Purpose:** feature inventory for RE/implementation planning. This is a
digest, not a full RE narrative: every row points at the corpus home where the
managed surface is actually documented, or marks the item as content/backlog.
The exact 3.1.0→3.2.0 delta is [`changelog-3.2.0.md`](changelog-3.2.0.md).

## Feature inventory

| Feature (official) | RE home / implementation note | Status |
|---|---|---|
| **Chicken farming**: sneak up on wild chickens, grab/carry them, defend them, place in a Chicken Coop | Held-entity grab is the `ItemClassHeldEntity` family + `EntityAlive.InitLocalActivationCommands`/`OnEntityActivated("grab")` ([items.md](items.md) § Held entities). Implement: entity spawn/despawn with a holder, `NetPackagePlayerId`-style sync for the held slot. | covered |
| **Chicken Coop workstation** with 3 tool slots: Brooding Lamp (production/maturation speed), Chicken Run (-50% feed), Nesting Box (breeding + nesting slots) | Composite TE with slots; the coop knobs map to sandbox options ([tile-entities-power.md](tile-entities-power.md), [sandbox-options.md](sandbox-options.md) § Crafting). Implement: `TEFeature` slot inventory + per-option production tick. | covered |
| **Chicken Stress event** (stress to 100% → drop chicken + stage event; sandbox-tunable) | Sandbox option `ChickenStressEvent` + `FullChickenStressEvent` ([sandbox-options.md](sandbox-options.md) §3); client FX via game events. Implement: stress accumulation on the held-entity side, event dispatch via `GameEventManager`. | covered |
| **Chicken recipes**: Rekt's Chicken Feed (corn + rotting flesh), jerky/stew recipes | content (`recipes.xml`); no managed delta. | content |
| **New sandbox options**: `ChickenCoopTime`, `ChickenCoopOutput`, `ChickenCoopInput`, `ChickenStressEvent`, `InfectionChance`, `HungerMultiplier`, `ThirstMultiplier`, `StackSizeMultiplier` (stack cap 30000) | `SandboxOptionManager.SetupOptions` catalog + `SandboxOptions` enum + preset codec ([sandbox-options.md](sandbox-options.md) §2-3, [inventories/gamestats-gameprefs.md](inventories/gamestats-gameprefs.md)). Implement: option enum member → codec string → `ApplyOptions` path; `StackSizeMultiplier` caps `ItemClass.Stacknumber` (items.md). | covered |
| **Biome density/respawn split into day/night + enemy/animal** | The `SandboxOptions` day/night pairs + `GameStats` backing ([sandbox-options.md](sandbox-options.md), [inventories/gamestats-gameprefs.md](inventories/gamestats-gameprefs.md)); drives `SpawnManagerBiomes` day/night budgets. Implement: two budgets per biome instead of one. | covered |
| **Big Beak cosmetic outfit** | content (cosmetic DLC). | content |
| **Diamond Blade Tip mod** in trader/loot lists | content (items/loot XML). | content |
| **Discord**: DM-notification audible option, cancel-login/unlink buttons | client UI + platform SDK; dedi surface is only `DiscordManager` (minimal; see [dedicated-misc-systems.md](dedicated-misc-systems.md)). | content / dedi-minimal |
| **4 new loading-screen images** | content (Unity assets). | content |

## b14 hotfix digest (managed-relevant subset)

| Fix (official) | RE note | Status |
|---|---|---|
| "Player inventory data could be sent to server when nothing had changed" | The inventory transaction **hash guard**: `NetPackageInventoryDataRequest/Response` keyHash+Guid; body `InventoryTransaction.Write` ([items.md](items.md) § Inventory transactions). Implement: hash the container state, skip unchanged sends. | covered |
| "Celebration Sandbox Option no longer blocks shared XP" | Party-share XP path: `GameManager.SharedKillServer` / `EntityAlive.PartyShareKillServer` (3.2.0 rework; [combat-damage.md](combat-damage.md) §3.1a). Implement: only the killer's own XP is scaled by celebration; share is not. | covered |
| "EOS exception in TileEntityNetPackage during POI reset" | EOS guard in the TE-net/POI-reset path; present in the dump, no dedicated prose. | backlog ([residuals.md](residuals.md) §1) |
| "Serverside EXC related to memory stream" | pooled-stream guard; no dedicated prose. | backlog |
| "Corruption when rapidly loading/unloading multiple chunks" | chunk-streaming edge-case fix; no dedicated prose. | backlog |
| "RequirementItemModTier did not check for null in slots" | item-mod tier requirement null guard; no dedicated prose. | backlog |
| Remaining b14 fixes (workstation UI, controller icons, server filter paging, prefab editor, invites, audio NRE, etc.) | client/UI/content; out of dedi scope. | content |

## RE guidance

- The held-entity/chicken surface is the V3.1.0 headline managed feature; its
  wire is `EntityCreationData` + held-item sync (items.md § Held entities).
  A clone needs the grab activation command list and the held-entity item
  classes; no new NetPackage was added for it.
- Every new sandbox option is one `SandboxOptions` enum member + one
  `SetupOptions` entry + a codec string; the enum-index list is
  machine-pinned at 317 members in 3.2.0 (unchanged since 3.1.0).
- Day/night density split means `SpawnManagerBiomes` reads two budget pairs;
  the sim budget math itself did not change in 3.1.0.

## Related

- Exact delta to 3.2.0: [`changelog-3.2.0.md`](changelog-3.2.0.md) §5a.
- V3.0.0 (Dead Hot Summer) feature inventory: [`changelog-3.0.0.md`](changelog-3.0.0.md).
