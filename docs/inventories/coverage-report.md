# RE coverage report (V3.0.1, auto-generated)

**Tool:** `tools/src/Coverage`. **Lens:** call-graph reachability from the
dedicated boot + tick drivers (devirtualized `callvirt`), cross-referenced
against docs name-mentions. Regenerate:
`mono tools/bin/Coverage.exe "$ASM" docs docs/inventories/coverage-report.md` (from the repo root, matching the other generated inventories).

## What this measures, and what it does not

**This is not a coverage metric.** It is *documentation-mention overlap on a static
call graph*, and both sides of the ratio are approximations. Read the caveats before
quoting any number here.

**The base (denominator) is wrong in both directions, by construction:**

- *Over-approximation:* `callvirt` is devirtualized to every override regardless of
  whether the receiver is ever instantiated on a server, so client-only trees get
  pulled in. This run has **498 XUi/XUiC_ client-UI types** inside the base even
  though a headless server renders nothing.
- *Under-approximation:* code reached only by **reflection** (XML-instantiated
  classes) is invisible. Interface dispatch IS devirtualized as of this version
  (that fix brought the console-command family in: **178 `ConsoleCmd*` types**
  are now in the base, against 1 before).

**The signal (numerator) is a mention, not an explanation.** A type counts as
*narrated* only if its name appears **backtick-quoted** in a hand-written narrative
doc. Backticks are required so prose and markdown table headers (`| Field |`,
`| Role |`, "Entry points") cannot credit real types named `Field`/`Entry`/`Data`.
Even so, one backticked cross-reference scores the same as a dedicated section.

The tiers are reported separately and deliberately **not summed into a headline**:

| Tier | Meaning |
|---|---|
| **narrated** | backticked in a narrative subsystem doc (the closest thing to real documentation) |
| **catalogued only** | backticked only in a generated `inventories/` catalog: enumerated, not explained |
| **classified** | listed in [out-of-scope-surface.md](../out-of-scope-surface.md) as not dedicated work |
| **unaccounted** | appears nowhere: the honest gap list |

## Totals

| Metric | Value |
|---|---:|
| Reached methods (with body) | 45236 |
| Reached types (incl. compiler-generated) | 7179 |
| Reached, non-generated | 6043 |
| ...third-party / BCL (System, Unity, Newtonsoft, ...) | 2355 (excluded from %) |
| ...**game types** (the RE surface) | **3688** |
| ...**narrated** (backticked in a narrative doc) | **1120 (30%)** |
| ...**catalogued only** (generated inventory, not narrated) | 734 |
| ...**classified** out-of-scope | 900 |
| ...**unaccounted** (appears nowhere) | 934 |
| of the base: XUi/XUiC_ client-UI types (over-approximation) | 498 |
| of the base: `ConsoleCmd*` (recovered by interface devirt) | 178 |

Third-party/BCL and obfuscated `#`-named types are excluded from the base.
**Do not add these rows together and present the sum as coverage.** "Narrated"
and "classified" are different epistemic states (reverse engineered vs judged
out of scope), and the base itself is the approximation described above.

## Per-namespace coverage (reached game types)

| Namespace | reached | narrated+catalogued+classified | remaining | % |
|---|---:|---:|---:|---:|
| `<global>` | 2926 | 2239 | 687 | 76% |
| `GameEvent` | 180 | 179 | 1 | 99% |
| `Platform` | 147 | 50 | 97 | 34% |
| `Twitch` | 109 | 76 | 33 | 69% |
| `DynamicMusic` | 47 | 9 | 38 | 19% |
| `Challenges` | 47 | 47 | 0 | 100% |
| `WorldGenerationEngineFinal` | 39 | 24 | 15 | 61% |
| `Discord` | 25 | 21 | 4 | 84% |
| `UAI` | 24 | 15 | 9 | 62% |
| `PrefabVolumes` | 16 | 16 | 0 | 100% |
| `GamePath` | 13 | 6 | 7 | 46% |
| `SandboxOptions` | 13 | 11 | 2 | 84% |
| `Audio` | 12 | 5 | 7 | 41% |
| `SDF` | 11 | 11 | 0 | 100% |
| `RaycastPathing` | 10 | 8 | 2 | 80% |
| `Webserver` | 10 | 8 | 2 | 80% |
| `XMLData` | 7 | 5 | 2 | 71% |
| `Quests` | 7 | 6 | 1 | 85% |
| `Services` | 6 | 3 | 3 | 50% |
| `ZXing` | 6 | 0 | 6 | 0% |
| `MapRendering` | 6 | 2 | 4 | 33% |
| `MusicUtils` | 5 | 3 | 2 | 60% |
| `BhvrAnalyticsServices` | 5 | 0 | 5 | 0% |
| `GearVariants` | 4 | 4 | 0 | 100% |
| `ConcurrentCollections` | 3 | 2 | 1 | 66% |
| `mumblelib` | 2 | 0 | 2 | 0% |
| `Force` | 2 | 0 | 2 | 0% |
| `WaterClippingTool` | 1 | 1 | 0 | 100% |
| `XMLEditing` | 1 | 0 | 1 | 0% |
| `SystemInformation` | 1 | 1 | 0 | 100% |
| `UnityEngineInternal` | 1 | 1 | 0 | 100% |
| `TriggerEffects` | 1 | 0 | 1 | 0% |
| `GUI_2` | 1 | 1 | 0 | 100% |

## Triage of the unaccounted set (2026-07-26)

A manual sample of the unaccounted list found it is **dominated by client, editor,
and vendored code that happens to live in the `<global>` namespace**, where the
namespace-based library filter cannot reach it: `PrefabEditModeManager` (editor),
`CursorControllerAbs` (client input), `NCalcLexer` / `BindingNcalcFunctions`
(vendored expression parser), `GameSenseManager` (SteelSeries peripherals),
`DistantTerrain` (render), `SaveDataMergedPlatformSaveGameIOProvider` (console
platform). These need per-type classification, not new reverse engineering.

So the honest reading of the number below is **not** "N undocumented server
systems". It is a work queue whose largest bucket is classification debt.

## Top undocumented reached types (by method count) - the gap list

These execute on a dedicated server but no doc names them. High method counts =
bigger unnarrated surface. (Many may be intentional residuals: support/utility
code, client-shared helpers. Cross-check against `residuals.md` before acting.)

| Type | Namespace | methods (reached-set) |
|---|---|---:|
| `Client` | Discord.Sdk | 158 |
| `Utils` | <global> | 110 |
| `Manager` | Audio | 69 |
| `Client` | <global> | 64 |
| `PrefabEditModeManager` | <global> | 62 |
| `Extensions` | <global> | 62 |
| `TList`1` | <global> | 58 |
| `PrefabChunk` | <global> | 54 |
| `UIFont` | <global> | 52 |
| `NCalcLexer` | <global> | 52 |
| `SaveDataMergedPlatformSaveGameIOProvider` | <global> | 47 |
| `BindingNcalcFunctions` | <global> | 47 |
| `DynamicMeshChunkData` | <global> | 45 |
| `Localization` | <global> | 40 |
| `MeshGenerator` | <global> | 40 |
| `XUiC_OptionsVideo` | <global> | 39 |
| `GameOptionsManager` | <global> | 38 |
| `GameSenseManager` | <global> | 37 |
| `DistantTerrain` | <global> | 37 |
| `CursorControllerAbs` | <global> | 37 |
| `NGuiAction` | <global> | 35 |
| `NetworkServerSteam` | Platform.Steam | 33 |
| `NetworkServerEos` | Platform.EOS | 33 |
| `XUiFromXml` | <global> | 33 |
| `PlatformUserManager` | Platform | 32 |
| `XUiM_Recipes` | <global> | 32 |
| `Call` | Discord.Sdk | 32 |
| `GameObjectPool` | <global> | 31 |
| `WaterDataHandle` | <global> | 31 |
| `ChunkBlockLayer` | <global> | 31 |
| `EventDelegate` | <global> | 31 |
| `PerformanceProfiler` | <global> | 30 |
| `SessionsHost` | Platform.EOS | 30 |
| `Stat` | <global> | 30 |
| `NCalcParser` | <global> | 29 |
| `UserBase` | Platform.EOS | 28 |
| `XUiC_InGameDebugMenu` | <global> | 28 |
| `GameRenderManager` | <global> | 28 |
| `LightManager` | <global> | 27 |
| `FastWireNode` | <global> | 27 |
| `MessageButton` | <global> | 26 |
| `NetworkClientSteam` | Platform.Steam | 26 |
| `LightLOD` | <global> | 26 |
| `PubSubSubscriptionRedemptionMessage` | Twitch.PubSub | 26 |
| `EAIManager` | <global> | 25 |
| `AchievementData` | Platform | 25 |
| `Vector2i` | <global> | 24 |
| `PrefabHelpers` | <global> | 24 |
| `BaseItemActionEntry` | <global> | 24 |
| `NetworkClientEos` | Platform.EOS | 24 |
| `Handle` | <global> | 24 |
| `ParticleEffect` | <global> | 23 |
| `XmlFile` | <global> | 23 |
| `HeightMapUtils` | <global> | 23 |
| `AIDirectorSmellMarker` | <global> | 22 |
| `UIAtlas` | <global> | 22 |
| `PrefabVolumeManager` | <global> | 22 |
| `Log` | <global> | 21 |
| `ActionTarget` | <global> | 21 |
| `LobbyHost` | Platform.Steam | 21 |

