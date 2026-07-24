# RE tooling (7dtd-research)

The single home for **stock-game reverse-engineering tooling**. Everything that
inspects the shipped `Assembly-CSharp.dll` (dumpers, census, protocol extractors,
version-diff, dump-regen tests) lives here and is tracked in git. Reimplementation
code and mods live in their own sibling repos; RE tooling does not.

Method (how to use these to reverse a system): [`../docs/re-methodology.md`](../docs/re-methodology.md).

```
tools/
  src/        general, maintained Mono.Cecil dumpers (prefer these)
  legacy/     per-family dumpers that generated the historical il/ dump sets
  parity/     cross-version wire-surface snapshot + diff (steamcmd)
  re-scratch/ one-off Zig reversers for on-disk file formats
  tests/      dump-regen + coverage regression tests
  build.sh    compiles src/ (and best-effort legacy/) into bin/
```

## Build

```bash
cd tools
./build.sh                 # -> bin/*.exe + bin/legacy/*.exe (+ bin/Mono.Cecil.dll)
./build.sh --skip-legacy   # only the general src/ tools
```

Requires `mono` (`mcs`) and a `Mono.Cecil.dll` (build.sh searches known local
copies; override with `MONO_CECIL=/path/to/Mono.Cecil.dll`, or restore via
`dotnet add package Mono.Cecil`). `bin/`, the Cecil binary, and `*.exe` are
git-ignored and regenerable. Nothing here ships game bytes; point `ASM` at your
own copy:

```bash
ASM="$HOME/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll"
```

Run: `MONO_PATH=bin mono bin/<Tool>.exe ...` (Cecil resolves from `bin/`).

## 1. General dumpers (`src/`): prefer these

Small, parameterized, maintained. They supersede most of `legacy/`.

| Tool | Purpose |
|---|---|
| `Census.exe <asm>` | Whole-assembly ground-truth counts (types, methods-with-body, gmUpdate IL, WorldState.SaveLoad IL). Re-run after a game patch to re-check `docs/coverage.md`. |
| `DumpMethod.exe <asm> <typeFilter> <methodFilter> [out]` | IL for any method by case-insensitive substring filters (nested types included). The workhorse; replaces most one-off legacy dumpers. |
| `DumpType.exe <asm> <outDir> <Type>...` | Fields + `read/write/Read/Write` bodies for wire payload structs (`EntityCreationData`, `BlockChangeInfo`, `ItemValue`, ...). |
| `DumpNetPackages.exe <asm> <outDir>` | Every `NetPackage*` wire surface (Setup/read/write/GetLength/ProcessPackage + trivial getters), one file per type + `INDEX.md`. |
| `NetProtocolCensus.exe <asm> <out>` | Per-package channel / compress / direction / delivery / before-auth table (`META.md`) + non-default summary. |
| `LeafInfo.exe <asm> <namesFile> <out.tsv>` | Per-type IL fingerprint (base class + declared body-method count + largest-body method names) for a list of type names; backs the [`../docs/inventories/dedicated-leaves.md`](../docs/inventories/dedicated-leaves.md) leaf catalog. |
| `Coverage.exe <asm> <docsDir> <out.md>` | Programmatic RE-coverage report: call-graph reachability from dedicated entry points vs docs name-mentions, per-namespace + top undocumented-reached gap list. Committable. Backs [`../docs/inventories/coverage-report.md`](../docs/inventories/coverage-report.md). |
| `WireBodies.exe <asm> <out.md>` | Auto-extracted per-package wire-body catalog: ordered `write()` field/type sequence for every `NetPackage*` (183) + the nested serializers they delegate to (60). Committable. Backs [`../docs/inventories/netpackage-bodies.md`](../docs/inventories/netpackage-bodies.md). |
| `FullSurface.exe <asm> <outDir>` | Whole-assembly **metadata** map (all 7,413 types): namespace summary + per-type signatures/sizes, no IL bodies. Committable. Backs [`../docs/full-surface.md`](../docs/full-surface.md). |
| `DumpAll.exe <asm> <outDir> [ns]` | **Full local reversal**: every method body of every type, one file per type. Output is git-ignored (never redistribute); optional namespace prefix filter. |

`src/IlFmt.cs` is a shared IL formatter compiled into each (`IL_XXXX: opcode operand`,
fully-qualified operands, `IL_offset` branch targets: the corpus dump format).

```bash
mono bin/Census.exe "$ASM"
mono bin/DumpNetPackages.exe "$ASM" ../il/netpackages-v3.0.1
mono bin/NetProtocolCensus.exe "$ASM" ../il/netpackages-v3.0.1/META.md
mono bin/DumpType.exe "$ASM" ../il/netpackages-v3.0.1 EntityCreationData BlockChangeInfo
mono bin/DumpMethod.exe "$ASM" GameManager gmUpdate
```

## 2. Legacy per-family dumpers (`legacy/`)

39 archival dumpers that generated the historical `il/` dump sets. Each emits a
whole family at once (many files + an auto-narrative). Kept for regenerating those
specific sets; for anything new, prefer `src/DumpMethod`/`DumpType`. `build.sh`
compiles them to `bin/legacy/` best-effort (**37 build; 2 are pre-corrupted:
`DumpGmUpdate`, `DumpExtra2`, use `DumpMethod`/`DumpType` instead**).

Canonical family dumpers (map to `il/` dump sets):

| Dumper | Dump set (`il/`) | Family |
|---|---|---|
| `DumpDediComplete` | `dedi-complete-v3.0.1/` | Complete dedicated managed surface + residual closers |
| `DumpGmUpdate` | `gmUpdate-v3.0.1/` | `GameManager.gmUpdate` / Update structure |
| `DumpFrameEntries` | `frame-entries-v3.0.1/` | Per-frame Update caller edges |
| `DumpDeep` | `deep-v3.0.1/` | Entity / AI / path / manager bodies + xrefs |
| `DumpDeeper` | `deeper-v3.0.1/` | Multi-subsystem deeper (EAI, MoveHelper, constants) |
| `DumpGaps` | `gaps-v3.0.1/` | Gap-closing (timer, AIDirector, ASP, net bands) |
| `DumpLoopComplete` | `loop-complete-v3.0.1/` | Loop + save + light surfaces |
| `DumpOptScan` | `opt-scan-v3.0.1/` | Large-method scan (hot-path candidates) |
| `DumpTerrain` | `terrain-*-v3.0.1/` | WorldConstants vertical dims + height APIs |
| `DumpRealEarthSurfaces` | `realearth-surfaces-v3.0.1/` | Chunk/Origin/PPL/region surfaces |
| `DumpAIDirector` | (aidirector) | AIDirector component types |
| `DumpSaveLight` | (save/light) | WorldState + light sites |

The remaining `legacy/*.cs` (`DumpMethod(ByName)`, `DumpType(s)`, `DumpOne(Method)`,
`DumpNamed`, `DumpNested`, `DumpNodes`, `DumpReg`, `DumpMgr`, `DumpScan`, `DumpIter`,
`DumpFull`, `DumpAstar`, `DumpAuth`, `DumpVoxel`, `DumpTps`, `DumpTypeBases`,
`DumpExtra*`, `Find{FieldWrite,Log,Sub,Type}`, `ListMethods`) are ad-hoc single-target
helpers/finders, superseded by `src/DumpMethod` and `src/DumpType`.

```bash
mono bin/legacy/DumpDediComplete.exe "$ASM" ../il/dedi-complete-v3.0.1
mono bin/legacy/DumpTerrain.exe "$ASM" ../il/terrain-v3.0.1
```

## 3. Cross-version parity (`parity/`)

Snapshots the whole wire surface to diffable JSON, so you can see exactly what The
Fun Pimps changed between game versions and measure clone coverage.

| File | Purpose |
|---|---|
| `parity/ParitySurface.cs` | Extract every `NetPackage` read/write call sequence + directions + selected enums into a stable JSON snapshot. |
| `parity/fetch_version.sh <branch\|manifest> [label]` | Download a specific dedicated build (app 294420) via steamcmd and emit its `ParitySurface` snapshot. |
| `parity/parity_diff.py old.json new.json` | Diff two snapshots (added/removed/wire-changed packages). `--coverage new.json GAMEDIR` reports clone-vs-stock coverage. |

## 4. One-off reversers (`re-scratch/`)

Small standalone Zig programs used while reversing the client wire and on-disk
file formats (prefab `.tts` block ids and texture channels, DEM tiles, chunk size
math). Run with `zig run re-scratch/<file>.zig`; paths inside are hardcoded to a
local install. See `re-scratch/README.md`.

## 5. Tests (`tests/`)

| Test | Checks |
|---|---|
| `tests/test_re_dump_regen.py` | Compiles `legacy/DumpFrameEntries` and regenerates non-empty inventory dumps from the local dedicated DLL (needs install + mcs/mono). |
| `tests/test_dedi_coverage_docs.py` | Structural proof that the coverage docs, dump sets, and dumpers all exist and are IL-backed (no game constant is the pass condition). |

```bash
uv run python tools/tests/test_dedi_coverage_docs.py   # structural gate
uv run python tools/tests/test_re_dump_regen.py        # regen check
```

## Policy

Dumps land under `il/` and are **git-ignored** (may contain game IL excerpts;
never redistribute). The tooling here is tracked; the game DLL and the dumps are
not. Regenerate against your own game copy; re-run `Census` and the tests after
any game update to catch patch drift.
