# RE coverage report (V3.0.1, auto-generated)

**Tool:** `tools/src/Coverage`. **Lens:** call-graph reachability from the
dedicated boot + tick drivers (devirtualized `callvirt`), cross-referenced
against docs name-mentions. Regenerate:
`mono bin/Coverage.exe "$ASM" ../docs coverage-report.md`.

Each reached game type is **narrated** (named in a subsystem doc),
**classified** out-of-scope ([out-of-scope-surface.md](../out-of-scope-surface.md)),
or **unaccounted** (the honest gap). Name-mention is an upper bound on narration
(a type named in passing counts). Third-party/BCL and obfuscated `#`-types are
excluded from the base. Reachability is the ground truth for "runs on a dedicated server".

## Totals

| Metric | Value |
|---|---:|
| Reached methods (with body) | 28374 |
| Reached types (incl. compiler-generated) | 4516 |
| Reached, non-generated | 4196 |
| ...third-party / BCL (System, Unity, Newtonsoft, ...) | 1493 (excluded from %) |
| ...**game types** (the RE surface) | **2703** |
| ...**narrated** in a subsystem doc | **1754 (64%)** |
| ...**classified** out-of-scope ([out-of-scope-surface.md](../out-of-scope-surface.md)) | 949 |
| ...**accounted for** (narrated + classified) | **2703 (100%)** |
| ...still unaccounted (gap floor) | 0 |

**Narrated %** = reverse-engineered in a subsystem doc (the real depth metric).
**Accounted-for %** = narrated OR explicitly classified as out-of-scope, i.e. no
reached type is silently ignored. Third-party/BCL code is excluded from the base.

## Per-namespace coverage (reached game types)

| Namespace | reached | documented | undocumented | % |
|---|---:|---:|---:|---:|
| `<global>` | 2195 | 2195 | 0 | 100% |
| `GameEvent` | 180 | 180 | 0 | 100% |
| `Twitch` | 78 | 78 | 0 | 100% |
| `Challenges` | 46 | 46 | 0 | 100% |
| `Platform` | 43 | 43 | 0 | 100% |
| `Discord` | 25 | 25 | 0 | 100% |
| `UAI` | 24 | 24 | 0 | 100% |
| `PrefabVolumes` | 16 | 16 | 0 | 100% |
| `WorldGenerationEngineFinal` | 12 | 12 | 0 | 100% |
| `DynamicMusic` | 11 | 11 | 0 | 100% |
| `SandboxOptions` | 10 | 10 | 0 | 100% |
| `SDF` | 10 | 10 | 0 | 100% |
| `GamePath` | 9 | 9 | 0 | 100% |
| `Audio` | 8 | 8 | 0 | 100% |
| `Quests` | 7 | 7 | 0 | 100% |
| `RaycastPathing` | 7 | 7 | 0 | 100% |
| `XMLData` | 5 | 5 | 0 | 100% |
| `GearVariants` | 4 | 4 | 0 | 100% |
| `Services` | 3 | 3 | 0 | 100% |
| `ConcurrentCollections` | 3 | 3 | 0 | 100% |
| `MusicUtils` | 3 | 3 | 0 | 100% |
| `SystemInformation` | 1 | 1 | 0 | 100% |
| `WaterClippingTool` | 1 | 1 | 0 | 100% |
| `GUI_2` | 1 | 1 | 0 | 100% |
| `UnityEngineInternal` | 1 | 1 | 0 | 100% |

## Top undocumented reached types (by method count) - the gap list

These execute on a dedicated server but no doc names them. High method counts =
bigger unnarrated surface. (Many may be intentional residuals: support/utility
code, client-shared helpers. Cross-check against `residuals.md` before acting.)

| Type | Namespace | methods (reached-set) |
|---|---|---:|

