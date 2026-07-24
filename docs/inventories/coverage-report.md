# RE coverage report (V3.0.1, auto-generated)

**Tool:** `tools/src/Coverage`. **Lens:** call-graph reachability from the
dedicated boot + tick drivers (devirtualized `callvirt`), cross-referenced
against docs name-mentions. Regenerate:
`mono bin/Coverage.exe "$ASM" ../docs coverage-report.md`.

**"Documented" = the type's simple name appears as a whole word in any
`docs/*.md`.** This is an *upper bound* on narrative coverage (a type named in
passing counts as documented), so treat the undocumented-reached list as the
honest floor of what still needs attention. Reachability is the ground truth for
"executes on a dedicated server".

## Totals

| Metric | Value |
|---|---:|
| Reached methods (with body) | 28374 |
| Reached types (incl. compiler-generated) | 4516 |
| Reached, non-generated | 4204 |
| ...third-party / BCL (System, Unity, Newtonsoft, ...) | 1495 (excluded from %) |
| ...**game types** (the RE surface) | **2709** |
| ...game types name-mentioned in docs | **1301 (48%)** |
| ...game types not mentioned (gap floor) | 1408 |

The **game-type documented %** is the headline coverage number. Third-party/BCL
code the game calls into is reached but out of scope (never reverse-engineered).

## Per-namespace coverage (reached game types)

| Namespace | reached | documented | undocumented | % |
|---|---:|---:|---:|---:|
| `<global>` | 2195 | 1067 | 1128 | 48% |
| `GameEvent` | 180 | 118 | 62 | 65% |
| `Twitch` | 78 | 13 | 65 | 16% |
| `Challenges` | 46 | 14 | 32 | 30% |
| `Platform` | 43 | 12 | 31 | 27% |
| `Discord` | 25 | 5 | 20 | 20% |
| `UAI` | 24 | 18 | 6 | 75% |
| `PrefabVolumes` | 16 | 9 | 7 | 56% |
| `WorldGenerationEngineFinal` | 12 | 10 | 2 | 83% |
| `DynamicMusic` | 11 | 4 | 7 | 36% |
| `SandboxOptions` | 10 | 1 | 9 | 10% |
| `SDF` | 10 | 4 | 6 | 40% |
| `GamePath` | 9 | 9 | 0 | 100% |
| `Audio` | 8 | 5 | 3 | 62% |
| `Quests` | 7 | 7 | 0 | 100% |
| `RaycastPathing` | 7 | 1 | 6 | 14% |
| `XMLData` | 5 | 2 | 3 | 40% |
| `GearVariants` | 4 | 0 | 4 | 0% |
| `Services` | 3 | 1 | 2 | 33% |
| `ConcurrentCollections` | 3 | 1 | 2 | 33% |
| `MusicUtils` | 3 | 0 | 3 | 0% |
| `#1d` | 3 | 0 | 3 | 0% |
| `#Re` | 2 | 0 | 2 | 0% |
| `SystemInformation` | 1 | 0 | 1 | 0% |
| `WaterClippingTool` | 1 | 0 | 1 | 0% |
| `GUI_2` | 1 | 0 | 1 | 0% |
| `#Qe` | 1 | 0 | 1 | 0% |
| `UnityEngineInternal` | 1 | 0 | 1 | 0% |

## Top undocumented reached types (by method count) - the gap list

These execute on a dedicated server but no doc names them. High method counts =
bigger unnarrated surface. (Many may be intentional residuals: support/utility
code, client-shared helpers. Cross-check against `residuals.md` before acting.)

| Type | Namespace | methods (reached-set) |
|---|---|---:|
| `XUiC_List`1` | <global> | 71 |
| `ObservableDictionary`2` | <global> | 44 |
| `XUiC_ComboBoxList`1` | <global> | 37 |
| `BlockValueV3` | <global> | 37 |
| `StringSpan` | <global> | 36 |
| `XUiC_SaveSpaceNeeded` | <global> | 36 |
| `XUiC_SignLayerGrid` | <global> | 36 |
| `XUiC_TriggerProperties` | <global> | 36 |
| `UIRect` | <global> | 36 |
| `NGuiAction` | <global> | 35 |
| `XUiV_Label` | <global> | 35 |
| `UIScrollView` | <global> | 35 |
| `XUiC_SandboxOptions` | <global> | 34 |
| `XUiC_ComboBoxEnum`1` | <global> | 34 |
| `AuthAndLoginManager` | <global> | 34 |
| `DynamicMusicManager` | <global> | 33 |
| `ConcurrentHashSet`1` | ConcurrentCollections | 33 |
| `UIBasicSprite` | <global> | 33 |
| `XUiC_BagContainer` | <global> | 32 |
| `XUiV_Window` | <global> | 32 |
| `XUiM_Recipes` | <global> | 32 |
| `ChunkProviderAbstract` | <global> | 32 |
| `SaveDataManagedPath` | <global> | 31 |
| `WaterDataHandle` | <global> | 31 |
| `SignCanvas` | <global> | 31 |
| `XUiC_OptionsDialogBase` | <global> | 31 |
| `XUiC_OptionsGeneral` | <global> | 31 |
| `XUiC_TraderWindow` | <global> | 31 |
| `XUiC_Paging` | <global> | 31 |
| `vp_Utility` | <global> | 31 |
| `XUiC_PlayersListEntry` | <global> | 31 |
| `EventDelegate` | <global> | 31 |
| `StringSpanDictionary`1` | <global> | 31 |
| `XUiM_Player` | <global> | 30 |
| `DynamicMeshChunkDataStorage`1` | <global> | 30 |
| `BaseSandboxOption` | SandboxOptions | 30 |
| `XUiC_CategoryList` | <global> | 30 |
| `ItemClassBlock` | <global> | 29 |
| `TwitchEventPreset` | Twitch | 29 |
| `XUiC_ServersList` | <global> | 29 |
| `XUiC_SkillList` | <global> | 29 |
| `XUiC_SpawnSelectionWindow` | <global> | 29 |
| `MeshDescription` | <global> | 29 |
| `MapObject` | <global> | 29 |
| `SaveInfoProvider` | <global> | 29 |
| `XUiV_TextureBased` | <global> | 29 |
| `XUiC_WindowSelector` | <global> | 28 |
| `XUiC_CreatePoi` | <global> | 28 |
| `XUiC_Creative2Window` | <global> | 28 |
| `XUiC_EquipmentStack` | <global> | 28 |
| `UITweener` | <global> | 28 |
| `XUiV_Grid` | <global> | 28 |
| `RaycastPathWorldUtils` | RaycastPathing | 27 |
| `XUiC_DiscordLogin` | <global> | 27 |
| `XUiC_LevelToolsGenericWindow` | <global> | 27 |
| `XUiC_SignGalleryWindow` | <global> | 27 |
| `XUiC_ItemInfoWindow` | <global> | 27 |
| `XUiC_SDCSPreviewWindow` | <global> | 27 |
| `UIProgressBar` | <global> | 27 |
| `MessageButton` | <global> | 26 |

