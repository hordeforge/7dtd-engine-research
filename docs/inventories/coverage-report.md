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
| ...**narrated** (backticked in a narrative doc) | **1319 (35%)** |
| ...**catalogued only** (generated inventory, not narrated) | 973 |
| ...**classified** out-of-scope | 1396 |
| ...**unaccounted** (appears nowhere) | 0 |
| of the base: XUi/XUiC_ client-UI types (over-approximation) | 498 |
| of the base: `ConsoleCmd*` (recovered by interface devirt) | 178 |

Third-party/BCL and obfuscated `#`-named types are excluded from the base.
**Do not add these rows together and present the sum as coverage.** "Narrated"
and "classified" are different epistemic states (reverse engineered vs judged
out of scope), and the base itself is the approximation described above.

## Per-namespace coverage (reached game types)

| Namespace | reached | narrated+catalogued+classified | remaining | % |
|---|---:|---:|---:|---:|
| `<global>` | 2926 | 2926 | 0 | 100% |
| `GameEvent` | 180 | 180 | 0 | 100% |
| `Platform` | 147 | 147 | 0 | 100% |
| `Twitch` | 109 | 109 | 0 | 100% |
| `DynamicMusic` | 47 | 47 | 0 | 100% |
| `Challenges` | 47 | 47 | 0 | 100% |
| `WorldGenerationEngineFinal` | 39 | 39 | 0 | 100% |
| `Discord` | 25 | 25 | 0 | 100% |
| `UAI` | 24 | 24 | 0 | 100% |
| `PrefabVolumes` | 16 | 16 | 0 | 100% |
| `GamePath` | 13 | 13 | 0 | 100% |
| `SandboxOptions` | 13 | 13 | 0 | 100% |
| `Audio` | 12 | 12 | 0 | 100% |
| `SDF` | 11 | 11 | 0 | 100% |
| `RaycastPathing` | 10 | 10 | 0 | 100% |
| `Webserver` | 10 | 10 | 0 | 100% |
| `XMLData` | 7 | 7 | 0 | 100% |
| `Quests` | 7 | 7 | 0 | 100% |
| `Services` | 6 | 6 | 0 | 100% |
| `ZXing` | 6 | 6 | 0 | 100% |
| `MapRendering` | 6 | 6 | 0 | 100% |
| `MusicUtils` | 5 | 5 | 0 | 100% |
| `BhvrAnalyticsServices` | 5 | 5 | 0 | 100% |
| `GearVariants` | 4 | 4 | 0 | 100% |
| `ConcurrentCollections` | 3 | 3 | 0 | 100% |
| `mumblelib` | 2 | 2 | 0 | 100% |
| `Force` | 2 | 2 | 0 | 100% |
| `WaterClippingTool` | 1 | 1 | 0 | 100% |
| `XMLEditing` | 1 | 1 | 0 | 100% |
| `SystemInformation` | 1 | 1 | 0 | 100% |
| `UnityEngineInternal` | 1 | 1 | 0 | 100% |
| `TriggerEffects` | 1 | 1 | 0 | 100% |
| `GUI_2` | 1 | 1 | 0 | 100% |

## Triage of the unaccounted set

As of 2026-07-28 the unaccounted tier is driven to **zero** by (1) crediting
`Type.Member` backtick forms as type mentions, (2) a supplementary out-of-scope
classification for client/platform/vendored/infra types that live in `<global>`,
and (3) leaf-cataloguing the RefScan server-dominant remainder. A zero here means
every reached game type is narrated, catalogued, or classified - **not** that every
type has a full behavioral narrative. Read the four tiers separately.

## Top undocumented reached types (by method count) - the gap list

These execute on a dedicated server but no doc names them. High method counts =
bigger unnarrated surface. (Many may be intentional residuals: support/utility
code, client-shared helpers. Cross-check against `residuals.md` before acting.)

| Type | Namespace | methods (reached-set) |
|---|---|---:|

