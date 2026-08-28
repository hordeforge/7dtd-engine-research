# V3.0.0 "Dead Hot Summer" changelog digest (feature inventory + RE map)

**Hub:** [`INDEX.md`](INDEX.md).
**Version:** V3.0.0 stable (2026-07-16) → V3.0.1 b4 (2026-07-22, hotfix line).
Major=3 Minor=0; the V3.0.1 b4 build was the corpus baseline before V3.1.0,
and its facts were re-verified on V3.1.0/V3.2.0 ([coverage.md](coverage.md)).
**Source:** official V3.0 Dead Hot Summer release notes
([7daystodie.com](https://7daystodie.com/v3-0-dead-hot-summer-release-notes)).
**Purpose:** feature inventory for RE/implementation planning. Digest, not a
full narrative: each row points at the corpus home or marks content/backlog.
The exact 3.1.0→3.2.0 delta is [`changelog-3.2.0.md`](changelog-3.2.0.md).

## Feature inventory

| Feature (official) | RE home / implementation note | Status |
|---|---|---|
| **150 sandbox customization options** | `SandboxOptions/` namespace: `SandboxOptionManager.SetupOptions` catalog, `SandboxOptions` enum (317 members in 3.2.0), per-option value sets, `GameStats` backing ([sandbox-options.md](sandbox-options.md); machine-pinned in [gamestats-gameprefs.md](inventories/gamestats-gameprefs.md)). Implement: enum member + `SetupOptions` entry + codec string; `ApplyOptions`/`AdjustItemsForSandboxOptions` application pass. | covered |
| **Sandbox preset creation + sharing (codes)** | `SandboxOptionPreset`, preset store + codec (`sandbox-code` string → option/value pairs), `ConsoleCmdGetSandboxOptions`/`SetSandboxOptions`, `SavePresetToFile` ([sandbox-options.md](sandbox-options.md) § presets; the 3.2.0 build reworked the display API with `languageName`). Implement: the preset codec is the clone-critical part - one char-escaped key/value list, 6 official preset tiers (sandbox preset decoder is gate-tested). | covered |
| **Item Magnitude (boosted stats on looted weapons/tools/mod parts)** | `ItemValue` Stats array wire: per stat `byte PassiveEffects type + i16 value + i16 boosted value` (items.md §2 row 8) - the "boosted" slot is where Magnitude lives. Loot rolling in `LootContainer.SpawnItem` (3.2.0 added the `LootMaxTier` clamp). Implement: roll boosted stats at loot time, carry the triple on the wire, clamp with `LootMaxTier`. | covered (mechanism) |
| **Progressive quality mods** (Q1-Q6 mod parts) | Mod quality rides `ItemValue.Quality` for installed mods ([items.md](items.md) §2/§6); mod rolling in `ItemClass` mod-slot logic. Implement: quality-aware mod install; simple on/off mods stay single-version. | covered |
| **Combine Station** (merge similar items, alternative repair; "highest % stat wins") | `TEFeatureCombine` TE ([tile-entities-power.md](tile-entities-power.md) § features), `ItemActionCombine` + `ItemActionEntryCombine`, `XUiC_CombineGrid`, `ItemValue.WasCombined` flag bit (3.2.0; items.md §7.1). Implement: read both item stat triples, pick max boosted %, write result + `cFlagsWasCombined`; the 3.2.0 UI rework added the explicit combine button. | covered |
| **Repair & degradation options** (repair method, permanent repair degradation 5-25%, death degradation/permanent max-durability loss) | `ItemValue` durability model (UseTimes/MaxUseTimes), `AdjustForSandboxOptions` perma-degradation switch, `ItemAction` repair through the crafting queue ([items.md](items.md) §7). Implement: repair method enum + degradation % options feed the durability math. | covered |
| **Sign-Tech system** (POI signage overhaul, sign tools) | Full sign stack: `SignData` layer tree, `SignLibrary` identity/storage, `NetPackageSignDataRequest/Response` wire, `AuthoredText` moderation ([signs.md](signs.md)). Implement: sign-data download protocol + `AuthoredText` validation before rendering. | covered |
| **Customizable crosshair** | client UI (`XUiC_*` crosshair bindings); no server surface. | content |
| **Redesigned main menu, 60+ new POIs, cosmetic outfit** | content / Unity assets / prefabs. | content |

## V3.0.1 hotfix digest (managed-relevant)

V3.0.1 b4 was the corpus's original baseline; its deltas vs V3.0.0 are not
narrated per-fix here (the corpus documents the resulting state, not the
hotfix history). Notable server-relevant items from the V3.0.1 notes that the
corpus still reflects: save-version migration hardening (`CurrentSaveVersion`
baked into [save-region.md](save-region.md) §1), sandbox preset fixes
(sandbox-options.md), and wire/join stabilization captured in
[protocol.md](protocol.md) V3.0.1-era goldens.

## RE guidance

- V3.0 is where the **sandbox + preset codec** and **combine/Magnitude item
  math** entered the game; V3.1.0/V3.2.0 only extended them. A clone that
  targets the current wire must implement: the preset codec (machine-gated),
  the ItemValue stat triple, `TEFeatureCombine` merge math, and the
  `WasCombined` flag.
- The sign-data wire (`NetPackageSignDataRequest/Response`) and `AuthoredText`
  moderation are the only V3.0 systems with a dedicated download protocol
  ([signs.md](signs.md)) - prioritize them for wire compatibility.
- Day/night and enemy/animal density splits arrived in V3.1.0, not V3.0;
  V3.0 had the single-pair density/respawn options.

## Related

- V3.1.0 (Henpocalypse) inventory: [`changelog-3.1.0.md`](changelog-3.1.0.md).
- Exact delta to 3.2.0: [`changelog-3.2.0.md`](changelog-3.2.0.md).
