# What "100% documented" means for this corpus

**Owns:** the honest definition of completion for stock dedicated RE, and how to
drive unaccounted → 0 after each game patch or doc edit.
**Not:** a claim that every IL instruction is prose-narrated.
**Hub:** [`INDEX.md`](INDEX.md). **Coverage tool:** [`coverage.md`](coverage.md),
[`inventories/coverage-report.md`](inventories/coverage-report.md).

---

## 1. Completion is tiered (do not collapse to one %)

| Tier | Meaning | Done when |
|---|---|---|
| **A. Managed map closed** | Every **reached game type** is narrated, catalogued, or classified OOS | `Coverage.exe` **unaccounted = 0** |
| **B. Dedi-critical behaviour closed** | Families 1-11 in [coverage.md](coverage.md): loop, wire, entities, world, save, net, managers, light/mesh/water, ModEvents | Status **Closed** + residual only non-IL |
| **C. Optional annotation depth** | Per-flag package framing, every console command prose, every TE subclass tick | Never "required" for interop; backlog only |
| **D. Non-IL residuals** | Unity order, native LiteNet/EAC, A* library, content XML, client UI | Listed in [residuals.md](residuals.md); **cannot** be closed by more managed RE |

**"100% of dedicated managed behaviour"** in this project means **A + B**.  
It does **not** mean C (infinite), and does **not** mean D (impossible from IL alone).

Narrated **37%** of the Coverage *base* is expected and healthy: the base
over-includes client UI and under-includes reflection; many types are correctly
**catalogued** or **classified**, not fully narrated.

---

## 2. After every game update or large doc edit

```bash
ASM="$HOME/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll"
cd tools && ./build.sh --skip-legacy
cd ..
make stock-sync          # pin JSON + sibling gates
MONO_PATH=tools/bin mono tools/bin/Coverage.exe "$ASM" docs docs/inventories/coverage-report.md
# read "Top undocumented" table; drive unaccounted to 0
```

For each unaccounted type:

1. Dump IL (`DumpType` / `DumpMethod` / `Xref`).
2. If dedi sim/wire: **narrate** in a family doc (backtick the type name).
3. If inventory-only leaf: add to the right `docs/inventories/*` with backticks.
4. If client/telemetry/third-party: add to [out-of-scope-surface.md](out-of-scope-surface.md).
5. Re-run Coverage until unaccounted = 0.

---

## 3. Current pin status (2026-08-07, regenerate to refresh)

| Check | How | Result |
|---|---|---|
| stock_facts vs live ASM | `make stock-check` | exit 0 (V 3.1.0 b14) |
| Unaccounted reached types | `Coverage.exe` | **0** (3699 game types; narrated 1415 / catalogued 892 / OOS 1392) |
| Families 1-11 | coverage.md Status column | Closed |
| Non-IL residuals | residuals.md §1 | Honest permanent list only |
| Tier A+B | this doc | **Met** for V3.1.0 b14 managed dedi bar |

Optional depth (C) still open by design: rare NetPackage per-flag framing,
full console-command prose beyond the catalog, TE subclass tick minutiae.

**Last cleanup that hit unaccounted=0:** `HeartbeatEventData` / `Helper` /
`TruncateStringSerializerConverter` classified OOS (client analytics; dedicated
skips heartbeat); `ConsoleCmdLogEnvironment` (`logenv`) added to console catalog.

### Tier-C depth progress (ongoing, never complete)

Closed in recent sessions (still optional, not required for A+B):

| Topic | Doc |
|---|---|
| ASP FindPaths FIFO + `ldc.i4.8` drain | entity-ai §D3.7 |
| Interest exit = `NetPackageEntityRemove` / Unloaded | network §2.2 |
| `Chunk.NeedsSaving` predicate | world-chunks |
| BodyAnimator `defaultCullingMode` vs live cull | entity-ai addendum |
| Raw + sector region headers (`7rr` / `7rg`) | save-region §3.4-3.5 |
| `BuffManager` registry | buffs §1.1 |
| `ClientPowerData` stream modes | tile-entities-power §2.1 |
| Audio/Light/TreeFade/DroneParticle wire fields | protocol-packages §6.21 |
| Explosion Initiate/Client full field lists | protocol-packages §6.14-6.15 (already) |

Remaining catalogued-only mass is mostly console commands (catalog rows), MinEvent/
Quest/Action leaves (inventories), client-shared helpers, and dormant UAI. Promote
only when a clone or optim lever needs the behaviour.

---

## 4. Why literal "every behaviour" is impossible

| Surface | Why IL cannot finish it |
|---|---|
| Unity MB execution order | Prefab/project settings, not CIL |
| Entity GO `enabled` on pure dedi | Runtime observation |
| LiteNet native / EAC wire | Native / anti-cheat black box |
| A* Pathfinding Project internals | Third-party library |
| XML content (blocks, loot, buffs) | Data files, not loop IL |
| ModEvents who registers | Content/mod dependent |

These stay in [residuals.md](residuals.md). Closing them is product/ops/runtime
work, not more narrative RE.

---

## Changelog

- **2026-08-07:** Initial completion-bar definition after Coverage unaccounted=4 cleanup drive.
