# RE tooling (7dtd-engine-research)

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
  sandbox/    experimental asset extractors (mesh-atlas XMLs, zdtd Zig-table generators)
  data/       committed pins: cecil.pin, stock_facts.json, xml_pins.json, promoted-types.txt
  tests/      dump-regen + coverage regression tests
  build.sh    compiles src/ (and best-effort legacy/) into bin/
```

Standalone Python entry points (no build step; each wired to a make target):

| Script | Purpose |
|---|---|
| `facts.py` | Quick view of the machine-checked stock pins (`make facts`). |
| `census-pct.py` | Percentage view of the coverage census (`make census`). |
| `save_roundtrip_check.py` | Verify real saves against the documented codecs (`make save-roundtrip[-all]`). |
| `cross_repo_links.py` | Cross-repo markdown link sweep (`make cross-links`). |
| `zdtd_cite_check.py` | Sibling-repo research citation check (`make sibling-cites`). |
| `xml_pins.py` | XML data pins vs the game dir (`make verify`). |

## Build

```bash
cd tools
./build.sh                 # -> bin/*.exe + bin/legacy/*.exe (+ bin/Mono.Cecil.dll)
./build.sh --skip-legacy   # only the general src/ tools
./cecil-pin.sh <dll>       # re-pin data/cecil.pin after a reviewed Cecil upgrade
```

Requires `mono` (`mcs`) and a `Mono.Cecil.dll` (build.sh searches known local
copies and the standard Mono GAC under `/usr/lib` or `/usr/local/lib`; override
with `MONO_CECIL=/path/to/Mono.Cecil.dll`, or restore via `dotnet add package
Mono.Cecil`). Mono.Cecil is this repo's only third-party dependency, and it is
**pinned**: build.sh checks the candidate's SHA-256 against
[`data/cecil.pin`](data/cecil.pin) and refuses a mismatch (every dumper links
and runs against that dll, so a silently swapped binary is a supply-chain risk).
After deliberately upgrading Cecil, review it and re-pin with
`./cecil-pin.sh /path/to/Mono.Cecil.dll`; `MONO_CECIL_UNVERIFIED=1` bypasses the
check for one build. `bin/`, the Cecil binary, and `*.exe` are
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
| `StockFacts.exe <asm> [out.json]` | Small JSON of stock hardcodes (version, TPS, chunk dims, save version, NetPackage count, behaviour pins: WaterLevel 62.88, item-drop lifetime 300 s, per-frame load budget 50 ms). Feeds `data/stock_facts.json` + pin check. |
| `Census.exe <asm>` | Whole-assembly ground-truth counts (types, methods-with-body, gmUpdate IL, WorldState.SaveLoad IL). Re-run after a game patch to re-check `docs/coverage.md`. |
| `DumpMethod.exe <asm> <typeFilter> <methodFilter> [out]` | IL for any method by case-insensitive substring filters (nested types included). The workhorse; replaces most one-off legacy dumpers. |
| `DumpType.exe <asm> <outDir> <Type>...` | Fields + `read/write/Read/Write` bodies for wire payload structs (`EntityCreationData`, `BlockChangeInfo`, `ItemValue`, ...). |
| `DumpNetPackages.exe <asm> <outDir>` | Every `NetPackage*` wire surface (Setup/read/write/GetLength/ProcessPackage + trivial getters), one file per type + `INDEX.md`. |
| `NetProtocolCensus.exe <asm> <out>` | Per-package channel / compress / direction / delivery / before-auth table (`META.md`) + non-default summary. |
| `Xref.exe <asm> <Type> <Member> [--field]` | **Exact** cross-reference: every site that calls `Type::Member`, or (with `--field`) reads/writes the field, attributed to the enclosing method and outermost owner type (so closure/iterator hits credit the real owner). Use this for server-vs-client classification. Supersedes the old `FindCallers.exe`, which ignored its method argument (it substring-matched only the type name against callee signatures, so it matched calls where the type was merely a parameter) and was blind to field access; that binary had no source and has been quarantined as `bin/FindCallers.exe.BROKEN-see-Xref`. |
| `CmdMap.exe <asm> [out.tsv]` | Console-command registry as `primaryName -> TypeName` for every concrete `ConsoleCmdAbstract` subclass; follows the static-field name form (`exportprefab`) that an ldstr-only scan misses. Backs the Type column in [`../docs/inventories/console-command-list.md`](../docs/inventories/console-command-list.md). |
| `LeafInfo.exe <asm> <namesFile> <out.tsv>` | Per-type IL fingerprint (base class + declared body-method count + largest-body method names) for a list of type names; backs the [`../docs/inventories/dedicated-leaves.md`](../docs/inventories/dedicated-leaves.md) leaf catalog. |
| `Coverage.exe <asm> <docsDir> <out.md>` | Programmatic RE-coverage report: call-graph reachability from dedicated entry points vs docs name-mentions, per-namespace + top undocumented-reached gap list. Committable. Backs [`../docs/inventories/coverage-report.md`](../docs/inventories/coverage-report.md). |
| `Reach.exe <asm> <outFile>` | Reached types/methods from the same seed set as `Coverage.exe` (shared `src/Seeds.cs`), TSV output for cross-filtering against `surface-types.md`. `tests/test_reach_consistency.py` asserts Reach and Coverage report identical reached-method counts so the two lenses cannot drift. |
| `WireBodies.exe <asm> <out.md>` | Auto-extracted per-package wire-body catalog: ordered `write()` field/type sequence for every `NetPackage*` with an extractable body (183) + the nested serializers they delegate to (60). Committable. Backs [`../docs/inventories/netpackage-bodies.md`](../docs/inventories/netpackage-bodies.md). |
| `FullSurface.exe <asm> <outDir>` | Whole-assembly **metadata** map (all 7,432 types): namespace summary + per-type signatures/sizes, no IL bodies. Committable. Backs [`../docs/full-surface.md`](../docs/full-surface.md). |
| `DumpAll.exe <asm> <outDir> [ns]` | **Full local reversal**: every method body of every type, one file per type. Output is git-ignored (never redistribute); optional namespace prefix filter. |
| `RefScan.exe <asm> <typeNamesFile> [out.tsv]` | Batch reverse-reference scan: every site that references each listed type, attributed to its outermost owner type; bulk server-vs-client classification (see re-methodology §8b). Complements single-member `Xref`. |
| `StateMachines.exe <docsDir> <out.md>` | Indexes every mermaid `stateDiagram` in the docs tree with owning section + state count. Docs in, assembly not involved; backs [`../docs/inventories/state-machines.md`](../docs/inventories/state-machines.md). |
| `EnumList.exe <asm> <outFile>` | Emits `Enum.Member=value` for every enum member; feeds the drift-check enum diff. |
| `MethodList.exe <asm> <outFile>` | Emits `Type::Method(params)` for every method-with-body; feeds the drift-check method-surface diff. |
| `ListAllTypes.exe <asm> <outFile>` | One-off audit helper: every type FullName sorted to a file (used to audit DumpAll completeness). |
| `census-pct.py [asm] [docsDir] [--json] [--history FILE]` | Percentage view of the coverage census: narrated / catalogued / classified / unaccounted fractions of reached game types, plus the whole-assembly reached-type/method fractions. `--json` emits a machine-readable object; `--history FILE` appends a dated row to the census-history CSV. Lives in `tools/`, runs `Coverage.exe` + `Census.exe` live (Python 3, no build step). |

`src/IlFmt.cs` is a shared IL formatter compiled into each (`IL_XXXX: opcode operand`,
fully-qualified operands, `IL_offset` branch targets: the corpus dump format).

```bash
mono bin/Census.exe "$ASM"
mono bin/DumpNetPackages.exe "$ASM" ../il/netpackages-v3.1.0
mono bin/NetProtocolCensus.exe "$ASM" ../il/netpackages-v3.1.0/META.md
mono bin/DumpType.exe "$ASM" ../il/netpackages-v3.1.0 EntityCreationData BlockChangeInfo
mono bin/DumpMethod.exe "$ASM" GameManager gmUpdate
```

## 1b. Stock facts sync (cross-repo pins)

```bash
./stock-sync.sh                 # extract live DLL → data/stock_facts.json + check pins
./stock-sync.sh --check-only    # verify committed JSON vs docs/loadgen/zdtd
python3 tests/check_stock_facts.py --require-live
```

Commit `data/stock_facts.json` when the game pin changes. The checker fails if
`docs/coverage.md`, loadgen `GameVersion`, or zdtd `stock_wire` / challenge /
ticks disagree with the JSON. Values that could not be extracted from IL and
were published as hard-coded defaults are listed under `provenance.baked`; a
non-empty list always fails the pin check (re-extract against the live game).
See [`../docs/re-methodology.md`](../docs/re-methodology.md) §5c.

### After a TFP game update

Preferred one-shot path (facts + pin gate + optional surface drift):

```bash
./post-update.sh                # stock-sync then parity/drift-check.sh
./post-update.sh --no-drift     # extract + pins only
make post-update                # same from repo root
```

`stock_facts.json` also carries:
- `update.dump_label_suffix` / `update.dump_sets` for `il/<set>-<suffix>/` regen
- `pins.*` machine-checked path inventory
- `behaviour.*` high-value Constants hardcodes (mob spawner cap, sense memory, …)

Structural dump-set tests (`tests/test_dedi_coverage_docs.py`) derive folder
labels from `stock_facts` rather than hard-coding a line version. Readiness
bench: `make readiness` or `python3 tests/bench_version_update_tooling.py`.
Session notes for the readiness experiment: [`../workspace/autoresearch/`](../workspace/autoresearch/).

## 2. Legacy per-family dumpers (`legacy/`)

39 archival dumpers that generated the historical `il/` dump sets. Each emits a
whole family at once (many files + an auto-narrative). Kept for regenerating those
specific sets; for anything new, prefer `src/DumpMethod`/`DumpType`. `build.sh`
compiles them to `bin/legacy/` best-effort (**37 build; 2 are pre-corrupted:
`DumpGmUpdate`, `DumpExtra2`, use `DumpMethod`/`DumpType` instead**).

Canonical family dumpers (map to `il/` dump sets):

| Dumper | Dump set (`il/`) | Family |
|---|---|---|
| `DumpDediComplete` | `dedi-complete-v3.1.0/` | Complete dedicated managed surface + residual closers |
| `DumpGmUpdate` | `gmUpdate-v3.1.0/` | `GameManager.gmUpdate` / Update structure |
| `DumpFrameEntries` | `frame-entries-v3.1.0/` | Per-frame Update caller edges |
| `DumpDeep` | `deep-v3.1.0/` | Entity / AI / path / manager bodies + xrefs |
| `DumpDeeper` | `deeper-v3.1.0/` | Multi-subsystem deeper (EAI, MoveHelper, constants) |
| `DumpGaps` | `gaps-v3.1.0/` | Gap-closing (timer, AIDirector, ASP, net bands) |
| `DumpLoopComplete` | `loop-complete-v3.1.0/` | Loop + save + light surfaces |
| `DumpOptScan` | `opt-scan-v3.1.0/` | Large-method scan (hot-path candidates) |
| `DumpTerrain` | `terrain-*-v3.1.0/` | WorldConstants vertical dims + height APIs |
| `DumpRealEarthSurfaces` | `realearth-surfaces-v3.1.0/` | Chunk/Origin/PPL/region surfaces |
| `DumpAIDirector` | (aidirector) | AIDirector component types |
| `DumpSaveLight` | (save/light) | WorldState + light sites |

The remaining `legacy/*.cs` (`DumpMethod(ByName)`, `DumpType(s)`, `DumpOne(Method)`,
`DumpNamed`, `DumpNested`, `DumpNodes`, `DumpReg`, `DumpMgr`, `DumpScan`, `DumpIter`,
`DumpFull`, `DumpAstar`, `DumpAuth`, `DumpVoxel`, `DumpTps`, `DumpTypeBases`,
`DumpExtra*`, `Find{FieldWrite,Log,Sub,Type}`, `ListMethods`) are ad-hoc single-target
helpers/finders, superseded by `src/DumpMethod` and `src/DumpType`.

```bash
mono bin/legacy/DumpDediComplete.exe "$ASM" ../il/dedi-complete-v3.1.0
mono bin/legacy/DumpTerrain.exe "$ASM" ../il/terrain-v3.1.0
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
| `tests/test_tool_bootstrap.py` | The tool builder discovers distribution-provided Mono.Cecil assemblies in the standard `/usr/lib` and `/usr/local/lib` Mono GAC paths. |
| `tests/test_cecil_pin.py` | Mono.Cecil supply-chain pin: `data/cecil.pin` is well-formed, `build.sh` still enforces the SHA-256 gate, and any built `bin/Mono.Cecil.dll` matches it. |
| `tests/test_dedi_coverage_docs.py` | Structural proof that the coverage docs, dump sets, and dumpers all exist and are IL-backed (no game constant is the pass condition). Detector self-tests prove the banned-phrase and IL-claim greps can fire. |
| `tests/check_stock_facts.py --require-live` | `tools/data/stock_facts.json` matches the live dedicated DLL (`make stock-check`): re-extracts via `bin/StockFacts.exe` and diffs every field, so a Steam-side build update fails with a named diff instead of passing silently. The facts-vs-DLL diff skips (with a note) on machines without the game; the docs/siblings checks always run. |
| `tests/test_reach_consistency.py` | Reach and Coverage report identical reached-method counts (shared `src/Seeds.cs`), so the two lenses cannot drift. Census bucket arithmetic sums. |
| `tests/test_surface_wellformed.py` | `full-surface.md` type rows sum to the 1,740,737 IL-instruction pin (per-type vs per-namespace totals must agree). |
| `tests/test_subclass_counts.py` | Per-leaf inventories (sequence-requirements 38, item-actions 38, quest-objectives 38, minevent-actions 71, block-behaviors 65, te-features 11, challenge-objectives 28+1, sequence-actions 123) match the DLL's concrete-subclass closures / namespace composition; six inventories' key-method fingerprints exist on the leaf or its base chain (args stripped; te-features' annotated prose excluded). |
| `tests/test_console_cmd_inventory.py` | Console-command inventory primary rows equal `CmdMap.exe` output exactly; alias rows are real registered names (getCommands ldstrs + cctor string-field values); the committed `console-command-list.tsv` equals fresh output; the Does column equals each `getDescription` (whitespace-normalized); the Perm column equals each `get_DefaultPermissionLevel` (blank = inherited). |
| `tests/test_gamestats_gameprefs_current.py` | `gamestats-gameprefs.md` EnumGameStats (82) + EnumGamePrefs (317) index tables equal the DLL's enum members by name, not just count. |
| `tests/test_inventory_type_existence.py` | Every type row in `dedicated-leaves.md` (371, existence) and `netpackages.md` (194, existence + base + method count + max method IL) resolves in the DLL; generic names normalized; `(not found)` markers tolerated. |
| `tests/test_entityclass_props_current.py` | `entityclass-props.md` 167 `ldstr`+`stsfld` pairs match the `EntityClass..cctor` exactly; IL=394 pin + 187 self-state. |
| `tests/test_il_citations.py` | Every parseable `Type::Method`/`Type.Method` + `IL=N` claim in the docs matches the DLL (any overload); dated changelog notes and shorthand-suffix types are skipped. Caught `GetCellsOnRay` 244->242 and `PersistentPlayerLogin` 5->37. |
| `tests/test_xref_claims.py` | Every `Xref=N` call-site claim in the docs (tight ``Type.Method (Xref=N)`` form) matches `Xref.exe` on the live DLL. |
| `tests/test_console_classification.py` | The console client-executable / dedicated-gate split (188 leaves; 83 `get_IsExecuteOnClient`, 84 either, 10 gated classes) matches a Cecil prologue probe over `CmdMap` rows. |
| `tests/test_netprotocol_census.py` | `NetProtocolCensus` re-derives the per-package census (193 packages; 6 channel-1, 8 compressed, 5 not-before-auth, 4 non-map) and the docs must match on all four axes. |
| `tests/test_tuned_constants.py` | 524 tuned game constants across ~56 families (AI-director horde/placement/cooldown + airdrop schedule, water-sim, block masks + BlockValue layouts, entity/walk-type ids, spawn rings, stealth/smell, vehicle/drone/turret, region/chunk/world, RWG, threat levels) pinned against the DLL and stated in the owning docs; completeness scan fails on any un-allowlisted const-rich class. |
| `tests/test_committed_inventories_current.py` | Generated inventories (`netpackage-bodies`, `coverage-report`, `state-machines`) are current against the live DLL. |
| `tests/test_state_machines_current.py` | `state-machines.md` lifecycle tables are current against the live DLL (skips without mono; CI-safe). |
| `tests/test_inventory_counts.py` | `docs/INDEX.md` inventory-count claims match each inventory's own self-stated count (11 claims). |
| `tests/test_readme_test_table.py` | Every test script run by `make test`/`test-docs`/`verify` is documented in this table, and every entry is a real file. |
| `tests/test_transport_closure_claims.py` | No stale native-LiteNetLib / unknown-peer-order claims in the docs. Pattern liveness self-tested. |
| `tests/test_coverage_consistency.py` | `docs/coverage.md` audit table lists every narrative doc; census rows match `stock_facts.json`. |
| `tests/test_doc_link_integrity.py` | Every doc reachable from `INDEX.md`; 0 dead internal links; every root doc carries the `**Hub:**` backlink; every `../` cross-repo link resolves to a real file (wrong-depth citations fail). Synthetic-tree self-tests prove orphan/dead detection. |
| `tests/test_save_roundtrip_robustness.py` | `save_roundtrip_check.py` degrades malformed/truncated saves to `"parse error"` FAIL verdicts instead of escaping a traceback (which would abort the remaining files' checks), and `--shipped` usage-errors with exit 2 when its path argument is missing or absent. Fixture-driven, DLL-free. |
| `tests/test_re_dump_regen.py` | Compiles `legacy/DumpFrameEntries` and regenerates non-empty inventory dumps from the local dedicated DLL (needs install + mcs/mono). |
| `tests/bench_version_update_tooling.py` | Version-update tooling benchmark (`make readiness`). Includes mutation checks of the Mono.Cecil pin gate. |

Tests that need the local dedicated DLL or built binaries SKIP with a reason on
machines without them, and FAIL with the fix command when the DLL is present but
the prerequisite is missing (`make tools`). Nothing here asserts game constants
as pass conditions.

```bash
make test        # the full gate suite above
make stock-check # stock_facts pins vs live DLL + sibling pins
```

## Policy

Dumps land under `il/` and are **git-ignored** (may contain game IL excerpts;
never redistribute). The tooling here is tracked; the game DLL and the dumps are
not. Regenerate against your own game copy; re-run `Census` and the tests after
any game update to catch patch drift.
