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
| ...third-party / BCL (System, Unity, Newtonsoft, ...) | 1299 (excluded from %) |
| ...**game types** (the RE surface) | **2905** |
| ...game types name-mentioned in docs | **1274 (43%)** |
| ...game types not mentioned (gap floor) | 1631 |

The **game-type documented %** is the headline coverage number. Third-party/BCL
code the game calls into is reached but out of scope (never reverse-engineered).

## Per-namespace coverage (reached game types)

| Namespace | reached | documented | undocumented | % |
|---|---:|---:|---:|---:|
| `<global>` | 2376 | 1044 | 1332 | 43% |
| `GameEvent` | 178 | 118 | 60 | 66% |
| `Twitch` | 72 | 12 | 60 | 16% |
| `Challenges` | 45 | 14 | 31 | 31% |
| `Platform` | 31 | 12 | 19 | 38% |
| `UAI` | 22 | 16 | 6 | 72% |
| `Discord` | 22 | 2 | 20 | 9% |
| `PrefabVolumes` | 16 | 9 | 7 | 56% |
| `SharpEXR` | 12 | 1 | 11 | 8% |
| `ICSharpCode` | 12 | 0 | 12 | 0% |
| `DynamicMusic` | 11 | 4 | 7 | 36% |
| `WorldGenerationEngineFinal` | 10 | 9 | 1 | 90% |
| `SandboxOptions` | 10 | 1 | 9 | 10% |
| `SDF` | 10 | 4 | 6 | 40% |
| `GamePath` | 9 | 9 | 0 | 100% |
| `Audio` | 7 | 5 | 2 | 71% |
| `Quests` | 7 | 7 | 0 | 100% |
| `SteelSeries` | 7 | 0 | 7 | 0% |
| `RaycastPathing` | 7 | 1 | 6 | 14% |
| `MemoryPack` | 5 | 0 | 5 | 0% |
| `XMLData` | 4 | 2 | 2 | 50% |
| `UniLinq` | 4 | 2 | 2 | 50% |
| `Internal` | 4 | 0 | 4 | 0% |
| `KinematicCharacterController` | 4 | 1 | 3 | 25% |
| `Services` | 3 | 1 | 2 | 33% |
| `MusicUtils` | 3 | 0 | 3 | 0% |
| `#1d` | 3 | 0 | 3 | 0% |
| `GearVariants` | 3 | 0 | 3 | 0% |
| `#Re` | 2 | 0 | 2 | 0% |
| `ConcurrentCollections` | 1 | 0 | 1 | 0% |
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
| `XUiView` | <global> | 171 |
| `UILabel` | <global> | 136 |
| `NGUITools` | <global> | 111 |
| `XUiC_ItemStack` | <global> | 101 |
| `XUiController` | <global> | 98 |
| `ShapeModule` | <global> | 97 |
| `Half` | SharpEXR | 96 |
| `MainModule` | <global> | 93 |
| `XUiC_WorldGenerationWindow` | <global> | 92 |
| `XUiC_TextInput` | <global> | 89 |
| `MemoryPackReader` | MemoryPack | 87 |
| `UIPanel` | <global> | 82 |
| `UIWidget` | <global> | 78 |
| `XUiC_SignEditorWindow` | <global> | 77 |
| `UICamera` | <global> | 75 |
| `DiscordUser` | <global> | 72 |
| `XUiC_List`1` | <global> | 71 |
| `XUiC_DataManagement` | <global> | 69 |
| `KinematicCharacterMotor` | KinematicCharacterController | 68 |
| `XUiC_ComboBoxBase` | <global> | 67 |
| `BlockToolSelection` | <global> | 66 |
| `XUiC_MapArea` | <global> | 65 |
| `XUiC_OptionsTwitch` | <global> | 61 |
| `NGUIFont` | <global> | 61 |
| `SDCSUtils` | <global> | 59 |
| `XUiC_LightEditor` | <global> | 55 |
| `UIInput` | <global> | 53 |
| `NGUIMath` | <global> | 53 |
| `XUiC_NewGame` | <global> | 51 |
| `UIPopupList` | <global> | 50 |
| `XUiC_RecipeList` | <global> | 49 |
| `XUiC_ServerBrowserGamePrefSelectorCombo` | <global> | 47 |
| `XUiC_DropDown` | <global> | 46 |
| `DiscordSettings` | <global> | 46 |
| `XUiC_CustomCharacterWindowGroup` | <global> | 45 |
| `ObservableDictionary`2` | <global> | 44 |
| `XUiC_Radial` | <global> | 44 |
| `XUiC_WoPropsPOIMarker` | <global> | 44 |
| `XUiC_WoPropsSleeperVolume` | <global> | 44 |
| `UIDrawCall` | <global> | 44 |
| `XUiC_NewsWindow` | <global> | 43 |
| `XUiC_RecipeStack` | <global> | 43 |
| `XUiM_PlayerInventory` | <global> | 43 |
| `XUiV_LabelBase` | <global> | 43 |
| `NGUIText` | <global> | 43 |
| `DecCalc` | <global> | 43 |
| `DynamicMeshUnity` | <global> | 41 |
| `XUiC_SaveManagementPrompt` | <global> | 41 |
| `TwitchViewerData` | Twitch | 40 |
| `XUiV_Button` | <global> | 40 |
| `XUiC_NewContinueGameSettings` | <global> | 40 |
| `vp_ComponentPreset` | <global> | 40 |
| `XUiC_BasePartStack` | <global> | 39 |
| `ProfileSDF` | <global> | 38 |
| `XUiC_ServerBrowser` | <global> | 38 |
| `XUiC_TwitchEntryListWindow` | <global> | 38 |
| `DtdParserProxy` | <global> | 38 |
| `XUiC_GamePrefSelector` | <global> | 37 |
| `XUiC_AdvancedColorPicker` | <global> | 37 |
| `XUiC_ComboBoxList`1` | <global> | 37 |

