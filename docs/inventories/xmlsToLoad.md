# WorldStaticData xmlsToLoad table (V3.1.0)

**Kind:** inventory of the stock config load table built in `WorldStaticData..cctor`
(IL=871). Each row is one `WorldStaticData/XmlLoadInfo` entry in `xmlsToLoad[]`.
**Basis:** IL of the static constructor (`tools/src/DumpMethod`); flags and delegates
read from the `XmlLoadInfo` ctor argument list. **Not** a runtime measurement of
which files exist on disk.
**Hub:** [`../INDEX.md`](../INDEX.md). **Narrative:** [`../mod-loading.md`](../mod-loading.md) §5.5.
**Method:** [`../re-methodology.md`](../re-methodology.md).

## Flag meanings (`XmlLoadInfo` ctor)

| Flag | Field | Meaning when true |
|---|---|---|
| **boot** | `LoadAtStartup` | included in the early startup filter of `LoadAllXmlsCo` / `Init` |
| **S2C** | `SendToClients` | compressed blob may be sent to joining clients (`SendXmlsToClient` path) |
| **reload** | `AllowReloadDuringGame` | eligible for `ReloadInGameXML` / admin reload hooks |
| **clientFile** | `LoadClientFile` | also treated as a client-local file entry (e.g. archetypes) |

Delegates:

| Column | Field |
|---|---|
| Load | `LoadMethod` (`Func<XmlFile,IEnumerator>`) |
| Cleanup | `CleanupMethod` (`Action`) |
| After | `ExecuteAfterLoad` (`Func<IEnumerator>`) |
| Reload | `ReloadDuringGameMethod` (`Action<XmlFile>`) |
| Loc | `LoadStepLocalizationKey` (progress UI string key) |

**Entry count:** **49** (array length from cctor; stored in `xmlsToLoad`).

**Dedi-relevant reading:** rows with **S2C** are the bulk of the config surface a
dedicated server loads and may ship to clients. Rows with neither **boot** nor
**S2C** still load on dedicated via the full `LoadAllXmlsCo` path unless a filter
restricts them (`gamestages`, `spawning`, `signs` are the main examples: load
server-side, not sent). Pure client UI rows (`XUi_*`, `loadingscreen`,
`subtitles`, `videos`) still appear in the table because the assembly is shared.

## Table (ctor order)

| XmlName | Flags | Load | Cleanup | After | Reload | Loc key |
|---|---|---|---|---|---|---|
| `events` | boot, S2C | `EventsFromXml::Load(XmlFile)` | `EventsFromXml::Cleanup()` | `-` | `-` | `-` |
| `materials` | S2C | `WorldStaticData::LoadMaterials(XmlFile)` | `MaterialBlock::Cleanup()` | `WorldStaticData::LoadTextureAtlases()` | `-` | `loadActionMaterials` |
| `physicsbodies` | S2C | `PhysicsBodiesFromXml::Load(XmlFile)` | `PhysicsBodyLayout::Reset()` | `-` | `-` | `-` |
| `painting` | S2C | `BlockTexturesFromXML::CreateBlockTextures(XmlFile)` | `BlockTextureData::Cleanup()` | `-` | `-` | `-` |
| `shapes` | S2C, reload | `ShapesFromXml::LoadShapes(XmlFile)` | `-` | `-` | `-` | `-` |
| `blocks` | S2C, reload | `WorldStaticData::LoadBlocks(XmlFile)` | `WorldStaticData::CleanupBlocks()` | `-` | `-` | `loadActionBlocks` |
| `progression` | S2C, reload | `ProgressionFromXml::Load(XmlFile)` | `Progression::Cleanup()` | `-` | `-` | `-` |
| `buffs` | S2C, reload | `BuffsFromXml::CreateBuffs(XmlFile)` | `BuffManager::Cleanup()` | `-` | `BuffsFromXml::Reload(XmlFile)` | `-` |
| `misc` | S2C, reload | `WorldStaticData::LoadMisc(XmlFile)` | `AnimationDelayData::Cleanup()` | `-` | `WorldStaticData::ReloadMisc(XmlFile)` | `-` |
| `items` | S2C, reload | `WorldStaticData::LoadItems(XmlFile)` | `ItemClass::Cleanup()` | `-` | `WorldStaticData::ReloadItems(XmlFile)` | `loadActionItems` |
| `item_modifiers` | S2C, reload | `WorldStaticData::LoadItemModifiers(XmlFile)` | `-` | `WorldStaticData::LateInitItems()` | `WorldStaticData::ReloadItemModifiers(XmlFile)` | `-` |
| `entityclasses` | S2C | `EntityClassesFromXml::LoadMain(XmlFile)` | `EntityClass::Cleanup()` | `-` | `-` | `-` |
| `qualityinfo` | S2C | `QualityInfoFromXml::CreateQualityInfo(XmlFile)` | `QualityInfo::Cleanup()` | `-` | `-` | `-` |
| `sounds` | S2C | `SoundsFromXml::CreateSounds(XmlFile)` | `-` | `-` | `-` | `-` |
| `recipes` | S2C, reload | `WorldStaticData::LoadRecipes(XmlFile)` | `CraftingManager::ClearAllRecipes()` | `-` | `WorldStaticData::ReloadRecipes(XmlFile)` | `-` |
| `blockplaceholders` | S2C | `BlockPlaceholdersFromXml::Load(XmlFile)` | `BlockPlaceholderMap::Cleanup()` | `-` | `-` | `-` |
| `loot` | S2C, reload | `WorldStaticData::LoadLoot(XmlFile)` | `LootContainer::Cleanup()` | `-` | `WorldStaticData::ReloadLoot(XmlFile)` | `-` |
| `entitygroups` | S2C | `EntityGroupsFromXml::LoadEntityGroups(XmlFile)` | `EntityGroups::Cleanup()` | `-` | `-` | `-` |
| `utilityai` | S2C | `UAIFromXml::Load(XmlFile)` | `UAIFromXml::Cleanup()` | `-` | `-` | `-` |
| `vehicles` | S2C, reload | `VehiclesFromXml::Load(XmlFile)` | `Vehicle::Cleanup()` | `-` | `VehiclesFromXml::Reload(XmlFile)` | `-` |
| `rwgmixer` | boot | `WorldGenerationEngineFinal.WorldGenerationFromXml::Load(XmlFile)` | `WorldGenerationEngineFinal.WorldGenerationFromXml::Cleanup()` | `-` | `-` | `-` |
| `weathersurvival` | S2C | `WorldStaticData::LoadWeather(XmlFile)` | `-` | `-` | `-` | `-` |
| `archetypes` | boot, S2C, clientFile | `WorldStaticData::LoadSDCSArchetypes(XmlFile)` ([schema](../sdcs-character-gear.md)) | `-` | `-` | `-` | `-` |
| `challenges` | S2C, reload | `ChallengesFromXml::CreateChallenges(XmlFile)` | `WorldStaticData::CleanupChallenges()` | `-` | `-` | `-` |
| `quests` | S2C | `QuestsFromXml::CreateQuests(XmlFile)` | `-` | `-` | `-` | `-` |
| `traders` | S2C, reload | `WorldStaticData::LoadTraders(XmlFile)` | `TraderInfo::Cleanup()` | `-` | `-` | `-` |
| `npc` | S2C | `WorldStaticData::LoadNpc(XmlFile)` | `-` | `-` | `-` | `-` |
| `dialogs` | S2C | `DialogFromXml::Load(XmlFile)` | `Dialog::Cleanup()` | `-` | `-` | `-` |
| `ui_display` | S2C, reload | `WorldStaticData::LoadUIDisplayInfo(XmlFile)` | `UIDisplayInfoManager::Reset()` | `-` | `-` | `-` |
| `nav_objects` | S2C, reload | `NavObjectClassesFromXml::Load(XmlFile)` | `NavObjectClass::Reset()` | `-` | `-` | `-` |
| `gamestages` | - | `GameStagesFromXml::Load(XmlFile)` | `WorldStaticData::CleanupGamestages()` | `-` | `-` | `-` |
| `gameevents` | S2C, reload | `GameEventsFromXml::CreateGameEvents(XmlFile)` | `WorldStaticData::CleanupGameEvents()` | `-` | `-` | `-` |
| `twitch` | S2C, reload | `TwitchActionsFromXml::CreateTwitchActions(XmlFile)` | `WorldStaticData::CleanupTwitch()` | `-` | `-` | `-` |
| `twitch_events` | S2C, reload | `TwitchActionsFromXml::CreateTwitchEvents(XmlFile)` | `WorldStaticData::CleanupTwitchEvents()` | `-` | `-` | `-` |
| `dmscontent` | S2C | `DMSContentFromXml::Load(XmlFile)` | `-` | `-` | `-` | `-` |
| `XUi_Common/styles` | S2C | `XUiFromXml::Load(XmlFile)` | `-` | `-` | `-` | `-` |
| `XUi_Common/templates` | S2C | `XUiFromXml::Load(XmlFile)` | `-` | `-` | `-` | `-` |
| `XUi_InGame/styles` | S2C | `XUiFromXml::Load(XmlFile)` | `-` | `-` | `-` | `-` |
| `XUi_InGame/templates` | S2C | `XUiFromXml::Load(XmlFile)` | `-` | `-` | `-` | `-` |
| `XUi_InGame/windows` | S2C | `XUiFromXml::Load(XmlFile)` | `-` | `-` | `-` | `-` |
| `XUi_InGame/xui` | S2C | `XUiFromXml::Load(XmlFile)` | `-` | `-` | `-` | `-` |
| `biomes` | S2C | `WorldStaticData::LoadBiomes(XmlFile)` | `WorldBiomes::CleanupStatic()` | `-` | `-` | `-` |
| `worldglobal` | S2C, reload | `WorldGlobalFromXml::Load(XmlFile)` | `-` | `-` | `WorldGlobalFromXml::Reload(XmlFile)` | `-` |
| `spawning` | - | `WorldStaticData::LoadSpawning(XmlFile)` | `WorldStaticData::CleanupSpawning()` | `-` | `-` | `-` |
| `loadingscreen` | boot, reload | `XUiC_LoadingScreen::LoadXml(XmlFile)` | `-` | `-` | `-` | `-` |
| `subtitles` | boot | `SoundsFromXml::LoadSubtitleXML(XmlFile)` | `-` | `-` | `-` | `-` |
| `videos` | boot | `VideoFromXML::CreateVideos(XmlFile)` | `-` | `-` | `-` | `-` |
| `signs` | - | `SignDataManager::LoadDefaultLibrary(XmlFile)` | `-` | `-` | `-` | `-` |
| `sandbox_overrides` | boot, S2C | `SandboxOverridesFromXml::CreateOverrides(XmlFile)` | `-` | `-` | `-` | `-` |

## Counts

| Set | Count |
|---|---:|
| Total entries | 49 |
| boot | 7 |
| S2C | 42 |
| reload | 19 |
| clientFile | 1 |
| no S2C (server-only or shared-local) | 7 |

## Call path (verified)

| Caller | Callee | Role |
|---|---|---|
| `GameManager.StartAsServer` | `WorldStaticData.LoadAllXmlsCo` | dedi boot config load |
| `WorldStaticData.Init` / `ReloadAllXmlsSync` | `LoadAllXmlsCo` | init + full reload |
| `WorldStaticData.getLoadInfoForName` | table scan | lookup by `XmlName` (IL=31) |
| `WorldStaticData.Reset(nameSubstring)` | cleanup + optional reload | partial reset (IL=52) |
| `WorldStaticData.ReloadInGameXML` | per-entry reload delegates | in-game reload (IL=88) |

Patching after stock load: [`../mod-loading.md`](../mod-loading.md) §5 (`XmlPatcher`).

**S2C shipping detail:** [`../mod-loading.md`](../mod-loading.md) §5.6
(`RequestToEnterGame` → `SendXmlsToClient` → `NetPackageConfigFile`; Deflate cache).

## Changelog

- **2026-07-28:** Initial table from `WorldStaticData..cctor` (49 `XmlLoadInfo` entries).
- **2026-07-28:** Link §5.6 S2C send path.
