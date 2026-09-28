# RE tooling (7dtd-engine-research)

The single home for **stock-game reverse-engineering tooling**. Everything that
inspects the shipped `Assembly-CSharp.dll` (dumpers, census, protocol extractors,
version-diff, dump-regen tests) lives here and is tracked in git. Reimplementation
code and mods live in their own sibling repos; RE tooling does not.

Method (how to use these to reverse a system): [`../docs/meta/re-methodology.md`](../docs/meta/re-methodology.md).
Maintainer status and audit log: [`STATUS.md`](STATUS.md).

```
tools/
  tooling.py  shared paths (repo-root marker walk), scratch dir, file digests,
              assembly discovery: imported by tools and gates, never a CLI
  src/        general, maintained Mono.Cecil dumpers (prefer these)
  legacy/     per-family dumpers that generated the historical il/ dump sets
  steam/      acquire and verify stock builds: PICS build ids (steam_builds.py),
              depot manifests + per-file SHA-1s (steam_manifest.py), downloads
              (fetch_version.sh)
  parity/     compare builds: wire-surface snapshot + diff, drift-check.sh
  re-scratch/ one-off Zig reversers for on-disk file formats
  sandbox/    experimental asset extractors + zdtd Zig-table generators
              (extract_mesh_atlas.py -> atlas/*.xml -> gen_atlas_zig.py;
               extract_sandbox_tables.py -> sandbox_tables.json -> gen_zig_tables.py)
  data/       committed pins: cecil.pin, stock_facts.json, xml_pins.json, promoted-types.txt
  tests/      gate scripts (one executable per rule) + _common.py helpers
  build.sh    compiles src/ + parity/ParitySurface.cs (and best-effort legacy/) into bin/
  bounded-run.sh  sourced, not run: the wall-clock bound on every mono/mcs/
                  monodis child the shell entry points spawn
```

Three rules keep that shape honest, enforced by
[`tests/test_tools_layout.py`](tests/test_tools_layout.py): no maintained
module outside `tests/` imports the test package (shared helpers live in
`tooling.py`), and no `tools/*.py` at any depth, gate included, finds the repo
by counting parent directories (a module imports `tooling.REPO`/`TOOLS`/`DOCS`,
or `_common.REPO`/`TOOLS`/`DOCS` under `tests/`), and every `tools/*.py` is
named here.

Standalone entry points (no build step; make targets noted inline where wired):

| Script | Purpose |
|---|---|
| `facts.py` | Quick view of the machine-checked stock pins (`make facts`). |
| `asm_path.py [--game-dir]` | Prints the dedicated-server `Assembly-CSharp.dll` in use, or with `--game-dir` the install root holding `Data/Config`. The one resolution behind `make`'s `ASM`/`GAME_ROOT`, `stock-sync.sh`, `post-update.sh` and `parity/drift-check.sh`, so the Makefile, the shell entry points and the Python tools cannot pick three different installs. Nothing found prints nothing and exits 0 (the caller's own guard reports it); an `ASM`/`SEVENDTD_ASM`/`SEVENDTD_DS_DIR` that points at no file exits 2 instead of falling through to a probed root. |
| `census-pct.py [asm] [docsDir] [--json] [--history FILE]` | Percentage view of the coverage census: narrated / catalogued / classified / unaccounted fractions of reached game types, plus the whole-assembly reached-type/method fractions. `--json` emits a machine-readable object; `--history FILE` records a dated row in the census-history CSV, one row per date, so a rerun replaces its own row. Runs `Coverage.exe` + `Census.exe` live (`make census`; Python 3, no build step). |
| `mention_depth.py [docsDir]` | DLL-free mention-depth histogram over the narrative docs: how many times each type-shaped backticked identifier occurs (exactly-1 / 2-4 / 5-19 / 20+). The depth behind any "narrated" fraction; published in [`../docs/meta/re-methodology.md`](../docs/meta/re-methodology.md) §1. `Coverage.exe` emits the reached-type version into the generated report and stamps that report with the studied build's version consts. A `docsDir` that is not a directory is a usage error (exit 2), not an all-zero table. |
| `shader_blob_dump.py <bundle> [--shader NAME] [--verbose]` | Decodes Shader (class 48) sub-program blobs from a stock UnityFS bundle and re-checks the documented layout: LZ4 per-platform blobs, the 12-byte record table, the code-blob record, and the 38-byte DX11 program-data header whose SRV/constant-buffer/sampler bytes are cross-checked against the DXBC `SHDR`/`SHEX` declaration opcodes. Exits non-zero on any disagreement; no assembly, no mono; exits 77 if UnityPy is absent. The byte-level decoders fail closed on a malformed blob (`ShaderBlobError`, or a `skipped` line for one undecodable sub-program); `tests/test_shader_blob_fuzz.py` gates that. Backs [`../docs/world/shader-subprogram-blob.md`](../docs/world/shader-subprogram-blob.md). Needs UnityPy from the pinned sandbox requirements (`uv pip install -r sandbox/requirements.txt`). |
| `save_roundtrip_check.py` | Verify real saves against the documented codecs (`make save-roundtrip[-all]`). |
| `cross_repo_links.py` | Cross-repo markdown link sweep (`make cross-links`). `--repo` takes one of the known sibling names; any other name exits 2 rather than reporting an empty sweep as OK. |
| `zdtd_cite_check.py` | Sibling-repo research citation check (`make sibling-cites`). `--repo` takes one of the known sibling names, with the same exit 2. |
| `xml_pins.py` | XML data pins vs the game dir (`make verify`). |
| `assignids_dump.py <Data/Config dir> <out.txt>` | Regenerates the zdtd `AssignIds` dump from a stock install (see [`assignids_dump.README.md`](assignids_dump.README.md)); backs the block-id tables in [`../docs/world/blocks.md`](../docs/world/blocks.md). |
| `steam_manifest.py --verify <game-dir>` | The install-integrity check behind `make install-check`: every shipped file against Steam's manifest for the installed build (17.6 GB in about 11 s here; `--only Managed` for the fast subset, `--ignore SUBSTR` for files the server rewrites at runtime). Roots and flags come from `ASM`/`GAME_ROOT`. |
| `sandbox/extract_preset_codes.py [xml] [tables]` | Decodes the six difficulty-preset `SandboxCode`s from the committed `sandbox/sandbox_presets.xml` and prints each option's per-difficulty value; stdlib-only, DLL-free. |
| `sandbox/try_extract_presets.py [game_dir] [--out FILE]` | Re-scans the shipped Unity bundles for the `sandbox_presets` TextAsset after a game update and writes it to `--out` (needs the pinned UnityPy); the re-extraction path for the committed XML above. |
| `steam/steam_builds.py [--check] [--fetch]` | Newest dedicated-server build (app 294420) from Steam's PICS app info: every branch's build id + depot 294422 manifest id, the local install's build id (Steam `appmanifest`), and the studied-build pin in [`data/steam_builds.json`](data/steam_builds.json). `--check` exits 1 when a build newer than the pin exists or the local install differs; `--print-fetch`/`--fetch` hand the manifest to `steam/fetch_version.sh` (a branch PICS does not list, e.g. `latest_experimental`, falls back to the branch form so steamcmd can still install it by name); `--verify-install [SUBSTR] [--ignore SUBSTR ...]` hashes local files against Steam's manifest for the installed build (a filter keeps it fast: `--verify-install Managed` is 149 files; without one it reads the whole install, 17.6 GB in about 11 s here), and `--check` fails on any mismatch or missing file; `--record` re-pins after a retarget and keeps the superseded pin in the file's `history` (capped, deduped by build id) so an older cached manifest can still be labelled after the Steam log rotates; `--from FILE` parses a saved payload offline. A `--pins FILE` that does not exist exits 2 (unless `--record` is there to write it), so a typo in the path cannot read as "no studied pin" and quietly skip the drift comparison. SteamDB has no public API and 403s scripted clients, so the machine path is Steam's own PICS. The table also marks each branch whose depot manifest is already cached locally (`cached`), so you can see which builds are diffable offline before fetching anything. `make latest`. |
| `steam/steam_manifest.py [--find SUBSTR] [--verify DIR]` | Steam's **own per-file checksums**, offline. The Steam client caches the depot manifest it installed from at `<steam>/depotcache/<depot>_<gid>.manifest`; the 7DTD dedicated depot (294422) one is plaintext protobuf (magic `0x71F617D0`), so every file's size, flags, whole-file SHA-1 and per-chunk SHA-1 are readable with no steamcmd, login, or network (SteamDB 403s scripted clients). `--find` prints the manifest row for a path, `--verify DIR [--only SUBSTR] [--ignore SUBSTR ...]` hashes local files against Steam's SHA-1s and exits 1 on missing/mismatched/short files (the ignored count is reported, never silent; a known runtime-written file such as `platform.cfg` carries an inline explanation), `--history` lists every cached build of the depot with the Steam build id paired from the client's `logs/content_log.txt` (falling back to the `studied`/`history` entries of `--pins FILE`, default [`data/steam_builds.json`](data/steam_builds.json)), `--list --json` emits the whole table, `--manifest FILE|GID|BUILDID` (and `--diff` likewise) reads any cached build by name instead of path, and `--diff OLD` (file, gid or build id) lists exactly which files changed between two cached builds with both SHA-1s and both build ids (the b10 vs b9 depot delta is 16 changed, 0 added, 0 removed). `--steam-root DIR` scans a non-default Steam tree. The whole install is 17.6 GB and verifies in about 11 s here (`make install-check`), so a narrower `--only` is only needed while iterating. |
| `research_diff.py --old <dll> --new <dll>` | One-pass build-to-build research report: source identity (bytes, sha256, version, Steam build when the sha matches the pin, plus a depot-provenance row giving Steam's own SHA-1 for each DLL and whether it matches the local file), a drift verdict, then the facts (`StockFacts.exe`, which notes when a side has no sibling `LiteNetLib.dll` so the `litenet.*` rows are missing rather than changed), census (`Census.exe`), per-type metadata (`FullSurface.exe`: added/removed types, kind/base/field/method/IL rows), method-signature (`MethodList.exe`), enum-member (`EnumList.exe`) and per-method body-hash (`asm_body_diff.py`) lenses, plus optional wire parity (`parity_diff.py` via `--parity-old/--parity-new`) and the non-managed content delta (`steam_manifest.py` via `--steam-manifest-old/--steam-manifest-new`). Writes a stamped Markdown report (default `workspace/outputs/diffs/<old>-to-<new>-<date>.md`, `--out -` for stdout), `--check` exits 1 on drift, `--json` prints the summary. The lenses are independent, so they run concurrently (`--jobs`, default `min(4, CPUs)`; `--jobs 1` is the sequential reference and renders a byte-identical report) with the long poles scheduled first so a cheap lens cannot hold a worker while the ~1.7 s body walk waits; report section order is fixed. `--pair OLD:NEW` (for example `--pair b9:b10`, raw Steam build ids `--pair 24911252:24994542`, or a path to an assembly outside the install dir such as a steamcmd scratch download, whose label comes from the version it reports) resolves both DLLs by the version each reports or through a build id's depot-manifest SHA-1, then matches each DLL's SHA-1 against the cached depot manifests, picks up the manifest-derived Steam build ids, and uses the committed `workspace/outputs/parity/parity_<label>.json` snapshots, so a known build pair is one command with nothing silent. The committed b9 to b10 report backs [`../docs/releases/changelog-3.2.0.md`](../docs/releases/changelog-3.2.0.md) §8. |
| `post-update.sh --steam` | Adds the Steam side to the post-patch path (opt-in, needs network): the published/installed build vs the studied pin, the local `Managed/` payload vs Steam's cached manifest, and the cached-build history, ending with the fetch/re-pin/report commands. Non-zero from that step is reported, not fatal, because the pin is expected to be behind until it is re-recorded. |
| `release.sh <vX.Y.Z> [--notes FILE] [--dry-run] [--skip-gates] [--resume]` | Cut a release: refuses a dirty worktree, an existing tag (local or origin), a branch behind `origin/main`, an unauthenticated `gh`, and a missing notes file; runs `make lint` plus `make test-docs` before tagging (`--skip-gates` skips both), then pushes `main` (only when HEAD is ahead of `origin/main`), tags annotated, pushes the tag and creates the GitHub release. `--dry-run` prints every step and writes nothing, and turns the worktree, behind-main and gh checks into notes; it also skips the gates and the `main` push, so it works on a CI runner where gh is installed but unauthenticated. `--resume` continues a run that stopped between steps: the tag must already exist and name `HEAD`, the steps that already landed are skipped, and the GitHub release is created only when `gh release view` does not find one, so a second resume leaves the same state as the first. Notes are required (`docs/releases/release-<version>.md` by default) because release prose is reviewed, not generated. The tag series (`v3.Y.0` corpus, `v0.Y.Z` tooling) and the tag history are in [`../docs/releases/release-contract.md`](../docs/releases/release-contract.md). |
| `regen.sh` | One-shot regeneration: builds the dumpers, re-dumps the canonical `il/` sets (the nine legacy families regen.sh maps, netpackages, surface, full), and refreshes the four generated committed inventories it names (`netpackage-bodies.md`, `console-command-list.tsv`, `state-machines.md`, `coverage-report.md`), ending with `make test`. The hand-maintained `docs/inventories/*` narratives are not regenerated. Needs `ASM=<dedicated Assembly-CSharp.dll>`. |

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
Mono.Cecil`). Mono.Cecil is the only third-party dependency of the C# tooling,
and it is **pinned**: build.sh checks the candidate's SHA-256 against
[`data/cecil.pin`](data/cecil.pin) and refuses a mismatch (every dumper links
and runs against that dll, so a silently swapped binary is a supply-chain risk).
After deliberately upgrading Cecil, review it and re-pin with
`./cecil-pin.sh /path/to/Mono.Cecil.dll`; `MONO_CECIL_UNVERIFIED=1` bypasses the
check for one build. `bin/`, the Cecil binary, and `*.exe` are
git-ignored and regenerable. Nothing here ships game bytes; point `ASM` at your
own copy:

Rebuilds are incremental: a target is recompiled only when a source (or the
staged Cecil) is newer than its exe, and the whole tree rebuilds when the
compiler or the pinned Cecil changes. build.sh is the only writer of `bin/`:
`drift-check.sh`, `stock-sync.sh` and `fetch_version.sh` run it instead of
compiling an exe themselves, so no script can leave an exe in place under a
weaker key than the toolchain stamp records. The `mcs`/`mono` versions, the Cecil
version, and Cecil's SHA-256 are written to `bin/buildinfo.txt` after a
successful build, and to `bin/.toolchain-stamp`, so a rebuild can be reproduced
and a toolchain swap cannot silently leave binaries from the previous compiler
in place. The compile and log order is pinned to `LC_ALL=C`, so it does not
follow the invoker's collation.

Two builds of one tree are byte-identical. `mcs` has no `-deterministic`, but
it takes the assembly name and the module MVID from the `-out` path, so every
compile targets `bin/.staging/<final-name>` and is renamed into place: a
`mktemp` `-out` name would land in the shipped assembly and make each rebuild
differ. Source paths are mapped out with `-pathmap`. `bin/buildinfo.txt` records
the digest of the Cecil actually linked in (`monocecil_sha256`) next to the pin
it was checked against (`monocecil_pinned_sha256`); the two differ only under
`MONO_CECIL_UNVERIFIED=1`.

```bash
ASM="$HOME/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll"
```

Run: `MONO_PATH=bin mono bin/<Tool>.exe ...` (Cecil resolves from `bin/`).

## Environment variables

The tools take no config file. Everything below is optional unless a row says
otherwise, and each one has a default that runs on a checkout with no game and
no setup. `tools/tests/test_env_vars_documented.py` fails if a variable the code
reads is missing from this table, or a row here names nothing the code reads.

| Variable | Read by | Default | Effect |
|---|---|---|---|
| `ASM` | every tool and gate that needs the live assembly (first of the three below) | probed Steam roots | The dedicated `Assembly-CSharp.dll` itself, or the install root holding `7DaysToDieServer_Data/Managed/`. Set to a path that holds no assembly the run stops with that message rather than probing on, so a pin run cannot verify a different build and pass. |
| `SEVENDTD_ASM` | same, after `ASM` | probed Steam roots | Alternative name for the same override. |
| `SEVENDTD_DS_DIR` | same, after `SEVENDTD_ASM` | probed Steam roots | Alternative name for the same override. |
| `GAME_ROOT` | `make` only (`install-check`, `save-roundtrip-all`) | `asm_path.py --game-dir` | The install root holding `Data/Config`, for a run that pins XML data. |
| `SEVENDTD_SERVER_DIR` | `make save-roundtrip-all` only | `$(GAME_ROOT)` | Install root used to find the shipped `worlds` for the full-fleet round trip. |
| `SOURCE_DATE_EPOCH` | every tool that stamps a committed artifact | wall clock (UTC) | Integer UTC epoch fixing that stamp, so re-running a tool over unchanged input rewrites the same bytes. A non-integer aborts. |
| `RE_MONO_TIMEOUT` | `tooling.run_bounded` (every mono, mcs and `fetch_version.sh` child) | 900 s | Wall-clock bound on a spawned tool. Non-numeric or non-positive aborts rather than meaning no bound. |
| `RE_STEAM_FETCH_TIMEOUT` | `steam_builds.py --fetch` | 21600 s (6 h) | Bound on a steamcmd download, far above the mono bound because a depot is gigabytes. Same validation as `RE_MONO_TIMEOUT`. |

Two more are read by the shell entry points only, and are named in each script's
own header: `MONO_CECIL` and `MONO_CECIL_UNVERIFIED` (`build.sh`, above),
`SCRATCH`, `OUT`, `STEAMCMD` and `STEAM_CONTENT` (`steam/fetch_version.sh`), and
`BASELINE_DIR`, `PARITY_BASELINE` and `COMMITTED_BASELINE`
(`parity/drift-check.sh`).

## Python dependencies

Everything under `tools/` runs on the stdlib except the `sandbox/` asset
extractors and `shader_blob_dump.py`, whose third-party imports (`dnfile`,
`dncil`, `UnityPy`) are hash-pinned in
[`sandbox/requirements.txt`](sandbox/requirements.txt)
(recompile from [`sandbox/requirements.in`](sandbox/requirements.in) with
`uv pip compile --generate-hashes requirements.in -o requirements.txt`).
Install into a venv with `uv pip install -r sandbox/requirements.txt`;
the hashes gate every download. Each `requirements.in` line carries a
compatible-release bound, so a recompile resolves inside the series the lock
was reviewed against instead of jumping to whatever is newest.

## 1. General dumpers (`src/`): prefer these

Small, parameterized, maintained. They supersede most of `legacy/`.

| Tool | Purpose |
|---|---|
| `StockFacts.exe <asm> [out.json]` | Small JSON of stock hardcodes (version, TPS, chunk dims, save version, NetPackage count, behaviour pins: WaterLevel 62.88, item-drop lifetime 300 s, per-frame load budget 50 ms). Feeds `data/stock_facts.json` + pin check. `extracted_utc` honors `SOURCE_DATE_EPOCH` (a non-integer aborts), so re-extracting an unchanged DLL reproduces the file byte for byte. |
| `Census.exe <asm>` | Whole-assembly ground-truth counts (types, methods-with-body, gmUpdate IL, WorldState.SaveLoad IL). Re-run after a game patch to re-check `docs/meta/coverage.md`. |
| `DumpMethod.exe <asm> <typeFilter> <methodFilter> [out]` | IL for any method by case-insensitive substring filters (nested types included). The workhorse; replaces most one-off legacy dumpers. |
| `DumpType.exe <asm> <outDir> <Type>...` | Fields + `read/write/Read/Write` bodies for wire payload structs (`EntityCreationData`, `BlockChangeInfo`, `ItemValue`, ...). |
| `DumpNetPackages.exe <asm> <outDir>` | Every `NetPackage*` wire surface (Setup/read/write/GetLength/ProcessPackage + trivial getters), one file per type + `INDEX.md`. |
| `NetProtocolCensus.exe <asm> <out>` | Per-package channel / compress / direction / delivery / before-auth table (`META.md`) + non-default summary. |
| `Xref.exe <asm> <Type> <Member> [--field]` (`<asm> --batch claims.tsv` for many pairs in one assembly pass) | **Exact** cross-reference: every site that calls `Type::Member`, or (with `--field`) reads/writes the field, attributed to the enclosing method and outermost owner type (so closure/iterator hits credit the real owner). Use this for server-vs-client classification. Supersedes the old `FindCallers.exe`, which ignored its method argument (it substring-matched only the type name against callee signatures, so it matched calls where the type was merely a parameter) and was blind to field access; that binary had no source and is quarantined outside the tree (a local `bin/FindCallers.exe.BROKEN-see-Xref`, in the git-ignored build dir). |
| `CmdMap.exe <asm> [out.tsv]` | Console-command registry as `primaryName -> TypeName` for every concrete `ConsoleCmdAbstract` subclass; follows the static-field name form (`exportprefab`) that an ldstr-only scan misses. Backs the Type column in [`../docs/inventories/console-command-list.md`](../docs/inventories/console-command-list.md). |
| `LeafInfo.exe <asm> <namesFile> <out.tsv>` | Per-type IL fingerprint (base class + declared body-method count + largest-body method names) for a list of type names; backs the [`../docs/inventories/dedicated-leaves.md`](../docs/inventories/dedicated-leaves.md) leaf catalog. |
| `Coverage.exe <asm> <docsDir> <out.md>` | Programmatic RE-coverage report: call-graph reachability from dedicated entry points vs docs name-mentions, per-namespace + top undocumented-reached gap list. Reports narrated / catalogued / classified / unaccounted as separate tiers (never summed), plus a mention-depth histogram over reached game types, and stamps the header with the studied build's `Constants.cVersion*` so a report cannot masquerade as another build's. Committable. Backs [`../docs/inventories/coverage-report.md`](../docs/inventories/coverage-report.md). |
| `Reach.exe <asm> <outFile>` | Reached types/methods from the same seed set as `Coverage.exe` (shared `src/Seeds.cs`), TSV output for cross-filtering against `surface-types.md`. `tests/test_reach_consistency.py` asserts Reach and Coverage report identical reached-method counts so the two lenses cannot drift. |
| `WireBodies.exe <asm> <out.md>` | Auto-extracted per-package wire-body catalog: ordered `write()` field/type sequence for every `NetPackage*` with an extractable body (185) + the nested serializers they delegate to (61). Committable. Backs [`../docs/inventories/netpackage-bodies.md`](../docs/inventories/netpackage-bodies.md). |
| `FullSurface.exe <asm> <outDir>` | Whole-assembly **metadata** map (all 7,451 types): namespace summary + per-type signatures/sizes, no IL bodies. Committable. Backs [`../docs/meta/full-surface.md`](../docs/meta/full-surface.md). |
| `DumpAll.exe <asm> <outDir> [ns]` | **Full local reversal**: every method body of every type, one file per type. Output is git-ignored (never redistribute); optional namespace prefix filter. |
| `RefScan.exe <asm> <typeNamesFile> [out.tsv]` | Batch reverse-reference scan: every site that references each listed type, attributed to its outermost owner type; bulk server-vs-client classification (see re-methodology §8b). Complements single-member `Xref`. |
| `StateMachines.exe <docsDir> <out.md>` | Indexes every mermaid `stateDiagram` in the docs tree with owning section + state count. Docs in, assembly not involved; backs [`../docs/inventories/state-machines.md`](../docs/inventories/state-machines.md). |
| `EnumList.exe <asm> <outFile>` | Emits `Enum.Member=value` for every enum member; feeds the drift-check enum diff. |
| `MethodList.exe <asm> <outFile>` | Emits `Type::Method(params)` for every method-with-body; feeds the drift-check method-surface diff. |

The no-build-step Python helpers (`census-pct.py`, `mention_depth.py`,
`shader_blob_dump.py`) are not `src/` tools; they are listed in the standalone
entry-points table at the top of this file.

`src/IlFmt.cs` is a shared IL formatter compiled into each (`IL_XXXX: opcode operand`,
fully-qualified operands, `IL_offset` branch targets: the corpus dump format).
`src/Seeds.cs` (shared reachability graph) and `src/AsmWalk.cs` (nested-type walk,
outermost-owner attribution, generic-arity strip) compile into each src/ tool the
same way; `StockFacts`/`MethodList`/`ParitySurface` are also compiled standalone
(`fetch_version.sh` runs `bin/ParitySurface.exe` directly) and must stay free of
them.

```bash
mono bin/Census.exe "$ASM"
mono bin/DumpNetPackages.exe "$ASM" ../il/netpackages-v3.2.0
mono bin/NetProtocolCensus.exe "$ASM" ../il/netpackages-v3.2.0/META.md
mono bin/DumpType.exe "$ASM" ../il/netpackages-v3.2.0 EntityCreationData BlockChangeInfo
mono bin/DumpMethod.exe "$ASM" GameManager gmUpdate
```

## 1b. Stock facts sync (cross-repo pins)

```bash
./stock-sync.sh                 # extract live DLL → data/stock_facts.json + check pins
./stock-sync.sh --check-only    # verify committed JSON vs docs/loadgen/zdtd + live DLL when present
python3 tests/check_stock_facts.py --require-live
```

Commit `data/stock_facts.json` when the game pin changes. The checker fails if
`docs/meta/coverage.md`, loadgen `GameVersion`, or zdtd `stock_wire` / challenge /
ticks disagree with the JSON. Values that could not be extracted from IL and
were published as hard-coded defaults are listed under `provenance.baked`; a
non-empty list always fails the pin check (re-extract against the live game).
See [`../docs/meta/re-methodology.md`](../docs/meta/re-methodology.md) §5c.

### After a TFP game update

Preferred one-shot path (facts + pin gate + optional surface drift):

```bash
./post-update.sh                # stock-sync then parity/drift-check.sh
./post-update.sh --no-drift     # extract + pins only
make post-update                # same from repo root
```

For the whole corpus (dump sets + committed inventories + gates), run
`ASM="<dll>" ./tools/regen.sh` instead of invoking each dumper by hand.

`stock_facts.json` also carries:
- `update.dump_label_suffix` / `update.dump_sets` for `il/<set>-<suffix>/` regen
- `pins.*` machine-checked path inventory
- `behaviour.*` high-value Constants hardcodes (mob spawner cap, sense memory, …)

Structural dump-set tests (`tests/test_dedi_coverage_docs.py`) derive folder
labels from `stock_facts` rather than hard-coding a line version. Readiness
bench: `make readiness` or `python3 tests/bench_version_update_tooling.py`.
Session notes for the readiness experiment: [`../workspace/autoresearch/`](../workspace/autoresearch/).

## 2. Legacy per-family dumpers (`legacy/`)

12 archival dumpers that generated the historical `il/` dump sets. Each emits a
whole family at once (many files + an auto-narrative). Kept for regenerating those
specific sets; for anything new, prefer `src/DumpMethod`/`src/DumpType`. `build.sh`
compiles them to `bin/legacy/` best-effort (all 12 build; a source that stops
compiling is reported, not fatal).

Canonical family dumpers (map to `il/` dump sets):

| Dumper | Dump set (`il/`) | Family |
|---|---|---|
| `DumpDediComplete` | `dedi-complete-v3.2.0/` | Complete dedicated managed surface + residual closers |
| `DumpGmUpdate` | `gmUpdate-v3.2.0/` | `GameManager.gmUpdate` / Update structure |
| `DumpFrameEntries` | `frame-entries-v3.2.0/` | Per-frame Update caller edges |
| `DumpDeep` | `deep-v3.2.0/` | Entity / AI / path / manager bodies + xrefs |
| `DumpDeeper` | `deeper-v3.2.0/` | Multi-subsystem deeper (EAI, MoveHelper, constants) |
| `DumpGaps` | `gaps-v3.2.0/` | Gap-closing (timer, AIDirector, ASP, net bands) |
| `DumpLoopComplete` | `loop-complete-v3.2.0/` | Loop + save + light surfaces |
| `DumpOptScan` | `opt-scan-v3.2.0/` | Large-method scan (hot-path candidates) |
| `DumpTerrain` | `terrain-*-v3.2.0/` | WorldConstants vertical dims + height APIs |
| `DumpRealEarthSurfaces` | `realearth-surfaces-v3.2.0/` | Chunk/Origin/PPL/region surfaces |
| `DumpAIDirector` | (aidirector) | AIDirector component types |
| `DumpSaveLight` | (save/light) | WorldState + light sites |

All 12 files in `legacy/` are canonical family dumpers (the table above). The 26
ad-hoc single-target helpers/finders that used to sit beside them (multiple
`DumpOne*`, `DumpNamed`, `Find*`, `ListMethods`, ...) were deleted after a
reference sweep: they were superseded by `src/DumpMethod`/`src/DumpType` and no
tool, test, or gate named them.

```bash
mono bin/legacy/DumpDediComplete.exe "$ASM" ../il/dedi-complete-v3.2.0
mono bin/legacy/DumpTerrain.exe "$ASM" ../il/terrain-v3.2.0
```

## 3. Cross-version parity (`parity/`)

Snapshots the whole wire surface to diffable JSON, so you can see exactly what The
Fun Pimps changed between game versions.

| File | Purpose |
|---|---|
| `parity/ParitySurface.cs` | Extract every `NetPackage` read/write call sequence + directions + selected enums into a stable JSON snapshot. |
| `steam/steam_builds.py` | Which builds exist, and which one this corpus studied: branch build ids + depot manifest ids from Steam PICS, local-install build id, drift verdict, and the `data/steam_builds.json` pin (build id + manifest + studied DLL sha256). |
| `steam/fetch_version.sh <branch\|manifest> [label]` | Download a specific dedicated build (app 294420) via operator-installed SteamCMD and atomically emit a validated `ParitySurface` snapshot. Set `STEAMCMD` when it is not on `PATH` (it also finds `$SCRATCH/steamcmd/steamcmd.sh`, the location the docs use). A failed steamcmd says what could not be fetched, names the app/depot ids, and exits 1 instead of leaking steamcmd's raw code. The branch, manifest id, and label are shape-checked before anything is downloaded: a branch may not start with `-` (steamcmd would read it as its own option), a manifest id must be all digits, and a label may not be a bare `.`/`..` (it names `parity_<label>.json`). |
| `parity/parity_diff.py old.json new.json` | Diff two stock snapshots (added/removed/wire-changed packages). |
| `../workspace/outputs/parity/parity_b9.json`, `parity_b10.json` | Committed ParitySurface snapshots for the two cached builds (produced with `MONO_PATH=tools/bin mono tools/bin/ParitySurface.exe <dll> | sed -n '/^{/,$p'`). `parity_diff.py` reports **0 added, 0 removed, 0 changed wire** between them, so the b9 to b10 claim of no NetPackage drift is machine-checked and a future build has a local baseline to diff against without a re-fetch. |
| `dump_diff.py old-full new-full [filter]` | Method-level diff of two `il/full-<version>/` dump trees: per-type added/removed/changed methods + field/base/interface drift. Used for the 3.1.0→3.2.0 diff; `filter` is a regex on the relative type path. |
| `asm_body_diff.py old.dll new.dll` | Pairwise method-body hash of two managed assemblies (Mono.Cecil). Catches same-size IL rewrites that FullSurface type-row diffs miss. Used to close the V3.2.0 b9→b10 completeness check. |

## 4. One-off reversers (`re-scratch/`)

Small standalone Zig programs used while reversing stock prefab `.tts` block ids
and texture channels. Run with `zig run re-scratch/<file>.zig -- <paths>`; inputs
are explicit. See `re-scratch/README.md`.

## 5. Tests (`tests/`)

| Test | Checks |
|---|---|
| `tests/test_tool_bootstrap.py` | The tool builder discovers distribution-provided Mono.Cecil assemblies in the standard `/usr/lib` and `/usr/local/lib` Mono GAC paths. |
| `tests/test_asm_discovery.py` | `tooling.asm_candidates` resolves the dedicated `Assembly-CSharp.dll` from every Steam library layout a supported host has (`%ProgramFiles(x86)%`, `%ProgramFiles%`, `%ProgramW6432%`, `~/.local/share/Steam`, `~/.steam/steam`, `~/.steam/root`, `~/Library/Application Support/Steam`), with `ASM`/`SEVENDTD_ASM`/`SEVENDTD_DS_DIR` outranking the probed roots. Fixtures per layout, so the whole matrix is checked on any host; stdlib-only, DLL-free. Each override variable set to a path holding no assembly raises `ConfigError` from `tooling.find_asm` (a probed install is planted alongside, so a silent fall-through would be caught), the gate-facing `_common` wrappers report that reason instead of tracing back, and an empty or unset variable still discovers normally. |
| `tests/test_tool_cli_usage.py` | Every maintained C# executable reports usage and exits 2 when required arguments are missing. Skips until the tools are built or Mono is available. |
| `tests/test_shell_cli_usage.py` | Supported shell entry points provide side-effect-free `--help`; strict no-positional commands reject unknown options. DLL-free. |
| `tests/test_release_script.py` | `release.sh` refuses a bad version, a missing notes file, unknown options and an existing tag, and its `--dry-run` prints the planned `git tag` / `gh release` steps while creating no tag. `--resume` is pinned in a throwaway git repository under the scratch tree (origin remote, stub `gh`): nothing tagged is refused, a run that pushed the tag and died before the release finishes on the first resume, a second resume creates nothing, and a tag pointing away from `HEAD` is refused. The real checkout is never written. DLL-free. |
| `tests/test_tools_layout.py` | The tool tree's structural rules: no maintained module outside `tools/tests/` imports the test package (shared paths, scratch and digests live in `tools/tooling.py`), no `tools/*.py` at any depth, gate included, locates the repo by counting parent directories, and every `tools/*.py` is named in this README. Static, DLL-free. |
| `tests/test_cli_args_wired.py` | Both directions of the CLI surface: every `args.<name>` a maintained Python tool reads is declared by an `add_argument` (removing a flag must not leave a stale `args.oldflag` on a branch the tests never reach, found after `steam_builds --url` was dropped and the live PICS path kept reading it), and every declared destination is read somewhere (no dead flag left behind by the same removal). `dest=` is honoured, `--help` is exempt, self-tested detector, files that rebind `args` are skipped and counted. Static, DLL-free. |
| `tests/test_python_cli_usage.py` | Every Python CLI discovered by AST under `tools/` (19 today) prints `--help` with exit 0 without importing its optional runtime packages, refuses an unknown flag with exit 2 and the usage line on stderr (never stdout, so a piped report stays clean), and is named in `tools/README.md`. A flag value the tool cannot act on is refused the same way, pinned for `--repo` on both link gates and `mention_depth.py`'s `docs_dir`: each used to answer a typo'd name or a missing path with an all-zero scan and exit 0, which reads as a green gate. Discovery replaced the hand-kept list, which had already drifted: `facts.py`, `census-pct.py`, `cross_repo_links.py`, `xml_pins.py`, and `zdtd_cite_check.py` were unchecked. DLL-free. |
| `tests/test_ilfmt_safe.py` | `IlFmt.Safe` (the filename sanitizer for assembly-supplied namespace/type names in DumpAll/DumpType/DumpNetPackages) never yields a fragment that escapes the dump out-dir: a crafted name of `.` or `..` is defused while namespace dots survive. Compiles a probe against `src/IlFmt.cs`; skips without mcs/mono. The fragment alphabet is ASCII letters, digits, `_` and `.`, so a non-ASCII name maps to the same file on every host and an astral character becomes two `_` (C# reads the name as UTF-16 code units, the Python twin matches it). |
| `tests/test_cecil_pin.py` | Mono.Cecil supply-chain pin: `data/cecil.pin` is well-formed, `build.sh` still enforces the SHA-256 gate, and any built `bin/Mono.Cecil.dll` matches it. |
| `tests/test_census_pct_history.py` | The committed `workspace/outputs/census-history.csv` carries exactly one header and no repeated date, recording the same row three times leaves the file byte-identical to one record, a same-date re-measure replaces its row instead of appending one, a missing header is restored rather than duplicated, and 8 concurrent `census-pct.py` runs over a fresh file produce one header and all 200 distinct rows (the whole read-modify-write is under an exclusive lock and lands through a temp-and-rename). The lock name hashes the NFC form of the path, escaped back to its raw bytes, so a decomposed and a composed spelling of one file share one lock and a name that is not valid UTF-8 does not raise. |
| `tests/test_json_pins_finite.py` | A committed pin file may not carry a value JSON cannot spell: `tooling.load_json` rejects `NaN`, `Infinity`, `-Infinity`, and a decimal literal that overflows binary64 (`1e999`), which `json.loads` accepts by default. The pin gate checks every number as `abs(got - want) > tol`, and that comparison is False on a NaN, so a NaN water level passed the gate written to catch it; the gate now fails at the load instead, and this test pins the rejection through `loads_json` and through `check_stock_facts.py` itself (asserted on the message, since a checkout without the Mono.Cecil dumpers fails that run for an unrelated reason). |
| `tests/test_dedi_coverage_docs.py` | Structural proof that the coverage docs, dump sets, and dumpers all exist and are IL-backed (no game constant is the pass condition). Detector self-tests prove the banned-phrase and IL-claim greps can fire. |
| `tests/check_stock_facts.py --require-live` | `tools/data/stock_facts.json` matches the live dedicated DLL (`make stock-check`): re-extracts via `bin/StockFacts.exe` and diffs every field, so a Steam-side build update fails with a named diff instead of passing silently. The facts-vs-DLL diff skips (with a note) on machines without the game; the docs/siblings checks always run. The pin file's declared `schema` is checked before any field is read. Baseline values (the build this corpus was written against) are one table per pin file (`PIN_BASELINE`, `XML_PIN_BASELINE`) rather than constants inside the individual comparisons, so a TFP patch that moves one is a named failure carrying the re-pin command. |
| `tests/test_reach_consistency.py` | Reach and Coverage report identical reached-method counts (shared `src/Seeds.cs`), so the two lenses cannot drift. Census bucket arithmetic sums. |
| `tests/test_surface_wellformed.py` | `full-surface.md` type rows sum to the 1,743,842 IL-instruction pin (per-type vs per-namespace totals must agree). |
| `tests/test_subclass_counts.py` | Per-leaf inventories (sequence-requirements 38, item-actions 38, quest-objectives 38, minevent-actions 71, block-behaviors 65, te-features 11, challenge-objectives 28+1, sequence-actions 123) match the DLL's concrete-subclass closures / namespace composition; six inventories' key-method fingerprints exist on the leaf or its base chain (args stripped; te-features' annotated prose excluded). |
| `tests/test_console_cmd_inventory.py` | Console-command inventory primary rows equal `CmdMap.exe` output exactly; alias rows are real registered names (getCommands ldstrs + cctor string-field values); the committed `console-command-list.tsv` equals fresh output; the Does column equals each `getDescription` (whitespace-normalized); the Perm column equals each `get_DefaultPermissionLevel` (blank = inherited). |
| `tests/test_gamestats_gameprefs_current.py` | `gamestats-gameprefs.md` EnumGameStats (82) + EnumGamePrefs (317) index tables equal the DLL's enum members by name, not just count. |
| `tests/test_inventory_type_existence.py` | Every type row in `dedicated-leaves.md` (370, existence) and `netpackages.md` (196, existence + base + method count + max method IL) resolves in the DLL; generic names normalized; `(not found)` markers tolerated. |
| `tests/test_entityclass_props_current.py` | `entityclass-props.md` 167 `ldstr`+`stsfld` pairs match the `EntityClass..cctor` exactly; IL=394 pin + 187 self-state. |
| `tests/test_il_citations.py` | Every parseable `Type::Method`/`Type.Method` + `IL=N` claim in the docs matches the DLL (any overload); dated changelog notes and shorthand-suffix types are skipped. Caught `GetCellsOnRay` 244->242 and `PersistentPlayerLogin` 5->37. |
| `tests/test_xref_claims.py` | Every `Xref=N` call-site claim in the docs (tight ``Type.Method (Xref=N)`` form) matches `Xref.exe` on the live DLL. |
| `tests/test_console_classification.py` | The console client-executable / dedicated-gate split (188 leaves; 83 `get_IsExecuteOnClient`, 84 either, 10 gated classes) matches a Cecil prologue probe over `CmdMap` rows. |
| `tests/test_netprotocol_census.py` | `NetProtocolCensus` re-derives the per-package census (195 packages; 5 channel-1, 8 compressed, 5 unreliable-delivery, 10 allowed-before-auth, 4 non-map) and the docs must match on every axis. |
| `tests/test_tuned_constants.py` | 535 tuned game constants across 68 families (AI-director horde/placement/cooldown + airdrop schedule, water-sim, block masks + BlockValue layouts, entity/walk-type ids, spawn rings, stealth/smell, vehicle/drone/turret, region/chunk/world, RWG, threat levels) pinned against the DLL and stated in the owning docs; completeness scan fails on any un-allowlisted const-rich class. |
| `tests/test_committed_inventories_current.py` | Generated inventories (`netpackage-bodies`, `coverage-report`, `state-machines`) are current against the live DLL; SKIPs when the local build differs from the stock_facts pin, since regenerating then would retarget the docs away from the studied build. |
| `tests/test_state_machines_current.py` | `state-machines.md` lifecycle tables are current against the live DLL (skips without mono or without the built `bin/StateMachines.exe`, so a stock CI checkout is CI-safe). |
| `tests/test_inventory_counts.py` | `docs/INDEX.md` inventory-count claims match each inventory's own self-stated count (12 claims). |
| `tests/test_readme_test_table.py` | Every test script run by `make test`/`test-docs`/`verify` is documented in this table, and every entry is a real file. |
| `tests/test_env_vars_documented.py` | Every environment variable the Python tools or the Makefile read is a row in the "Environment variables" table above, and every row is a variable something reads. The names come from an AST scan of the tools (`os.environ` reads plus the `_ENV`/`_VARS` constants they indirect through) and the Makefile's own variables, so a new knob cannot ship with a default nobody outside the diff knows. Names that are not configuration (make's own variables, `$HOME`) are a reviewed `NOT_CONFIG` list. DLL-free, network-free. |
| `tests/test_transport_closure_claims.py` | No stale native-LiteNetLib / unknown-peer-order claims in the docs. Pattern liveness self-tested. |
| `tests/test_coverage_consistency.py` | `docs/meta/coverage.md` audit table lists every narrative doc; census rows match `stock_facts.json`; every `**Current pin:**` banner in `docs/` names the pinned build (a stale banner is caught, a history mention is not). |
| `tests/test_promoted_types.py` | Every name in `data/promoted-types.txt` stays absent from `out-of-scope-surface.md`, so an inventory regeneration cannot silently revert the referrer-verified hand-corrections; the OOS maintenance note must still cite the input file. DLL-free. |
| `tests/test_stock_facts_baseline.py` | `check_stock_facts.py`'s baseline and schema gates are real: the committed pins hold every value in `PIN_BASELINE`/`XML_PIN_BASELINE`, a value that moves is reported by pin path with the re-pin command, a removed section reads as a missing pin rather than raising, float pins compare within `FLOAT_TOLERANCE` (so rounding noise is not drift), and `main()` refuses a pin file whose declared `schema` is not the one the gate reads. |
| `tests/test_doc_link_integrity.py` | Every doc reachable from `INDEX.md`; 0 dead internal links; every root doc carries the `**Hub:**` backlink; every `../` cross-repo link resolves to a real file (wrong-depth citations fail). Synthetic-tree self-tests prove orphan/dead detection. |
| `tests/test_save_roundtrip_robustness.py` | `save_roundtrip_check.py` degrades malformed/truncated saves to `"parse error"` FAIL verdicts instead of escaping a traceback (which would abort the remaining files' checks), and `--shipped` usage-errors with exit 2 when its path argument is missing or absent. Fixture-driven, DLL-free. |
| `tests/test_save_roundtrip_fuzz.py` | Seeded mutation fuzzer over every `save_roundtrip_check.py` parser surface (ttw, region V2/raw, chunk bodies, worldstate blobs, record files, nim): structure-aware valid seeds, then bit flips, truncations, splices, and count-field inflation. Asserts no exception escapes, per-call time budget (pins the spawnList-count hang fix), byte-exact lines never carry FAIL markers, deterministic re-parses, and the capped inflate round-trip/bomb contract. Deterministic seed, stdlib-only, DLL-free. |
| `tests/test_sandbox_safe_name.py` | `sandbox/safe_name.py` (the filename sanitizer for bundle-supplied TextAsset names in extract_mesh_atlas) never yields a fragment that escapes the atlas out-dir: crafted names of `.`, `..`, separators, or absolute paths are defused while namespace dots survive. Python twin of the `IlFmt.Safe` pin over the same ASCII alphabet; stdlib-only, DLL-free. |
| `tests/test_sandbox_requirements_sync.py` | `sandbox/requirements.txt` (the uv-compiled, sha256-hashed dependency lock for dnfile/dncil/UnityPy) stays in sync with `sandbox/requirements.in`: every declared dep is an exact pin in the lock with at least one hash, the locked version satisfies the bound `requirements.in` declares for it, no ranged/wildcard specifiers, and every entry the lock marks direct is declared. Also fails any non-stdlib import in `sandbox/*.py` or `shader_blob_dump.py` that `requirements.in` does not declare, so no tool rides in on an undeclared transitive. Mutation-tested against missing deps, stripped hashes, ghost directs, range specifiers, and undeclared imports; stdlib-only, DLL-free, network-free. |
| `tests/test_sandbox_preset_codes.py` | The built-in difficulty preset decoder resolves its committed inputs independently of the working directory, emits all six tiers, and rejects malformed codes. Stdlib-only, DLL-free. |
| `tests/test_sandbox_zig_tables.py` | Every float in `sandbox/sandbox_tables.json` emits from `gen_zig_tables.py` as the shortest Zig literal that re-parses to the identical binary32 value, so a fixed-precision round can never silently shift a stock sandbox default (binary32 successors of 0.5/1.0/2.0 are pinned as collapse probes), and `gen_atlas_zig.to_color5` packs the stock `(r*31+0.5)<<10 | (g*31+0.5)<<5 | (b*31+0.5)` RGB555 correctly at the boundaries (black, white, the `Color32(0,105,148)` water colour, the `Color.get_gray()` fallback at 16912, and out-of-range components clamped rather than wrapped by the 5-bit mask), so the two hand-typed minimap constants the generator emits are derived from the formula rather than typed beside it; stdlib-only, DLL-free. |
| `tests/test_xml_pins_gate.py` | `xml_pins.py --check` diffs every committed section (`entityclasses_health`, `traders_root`, `buffs_survival`) against the install, so drift in any pinned value fails; regeneration refuses to overwrite populated sections when a source file parses to nothing (wrong `--game-dir`, renamed config header). Synthetic Data/Config fixtures in a temp dir via `--pins`; DLL-free, never touches `tools/data`. |
| `tests/test_gate_unreadable_files.py` | The link/citation gates (`cross_repo_links.py`, `zdtd_cite_check.py`) FAIL with an explicit UNREADABLE line when a scanned file cannot be read, instead of silently skipping it (which would pass the gate while that file's links/citations were never checked). Dangling-symlink fixtures in a temp root (reported as not exercised where the host denies symlink creation, e.g. Windows without Developer Mode); clean-tree positive controls; DLL-free. |
| `tests/test_parity_diff.py` | Stock snapshot parity CLI: unchanged snapshots exit 0, wire drift exits 1, malformed/removed modes exit 2. DLL-free. |
| `tests/test_committed_diff_artifacts.py` | The committed evidence artifacts still equal what the tools emit: `parity_b9.json`/`parity_b10.json` are re-derived with `ParitySurface.exe` and compared field for field, and the `b9-to-b10-*.md` report is re-rendered through `research_diff.py --pair b9:b10` with `SOURCE_DATE_EPOCH` pinned to the stamp the committed report already carries, so the comparison is byte-for-byte. A second committed report FAILs rather than SKIPs. SKIPs unless the live DLL is the studied build, the retained backup is the report's baseline, and the cached manifests are present. Machine-local, needs mono. |
| `tests/test_fetch_version_fake_steamcmd.py` | `steam/fetch_version.sh` end to end with a recording fake steamcmd: the manifest form passes the manifest id through and publishes a snapshot identical to a direct `ParitySurface.exe` run on the same DLL, the branch form materialises the install per `-beta`, and a steamcmd that does nothing or fails exits non-zero without publishing a partial snapshot, and `steam_builds.py --fetch` hands the branch manifest through to the same script. A gid-to-DLL map in the fake (`<gid>=<path>;...`) fetches two builds in one run and asserts their snapshots equal the direct `ParitySurface` runs and that `parity_diff.py` reports no wire drift for the b9 to b10 pair. Malformed target/label shapes (a leading `-`, a space, a tab, a `..` segment, a bare-dot label, a trailing newline) are refused before any download is attempted, which runs DLL-free. Offline; SKIPs without mono/mcs, the pinned Cecil build, or the live DLL. |
| `tests/test_install_integrity.py` | Two invariants: the installed `Managed/` payload still matches Steam's cached depot manifest for the installed build (`steam_builds.py --check --verify-install Managed --json`, asserting 0 missing and 0 mismatch against the appmanifest's own manifest gid, which `make stock-check` does not cover), and the installed build id and manifest equal `tools/data/steam_builds.json`'s studied pin, so an asset-only TFP patch that moves the install without changing the studied DLL's facts cannot leave the docs citing the previous build. SKIPs when no manifest for the installed build is cached. Needs mono. |
| `tests/test_drift_committed_baseline.py` | `parity/drift-check.sh` compares the wire axis against the committed `workspace/outputs/parity/parity_b10.json` on a fresh checkout (no `BASELINE_DIR` yet), flags a perturbed snapshot with exit 1 and the package name, uses a machine-local baseline only while its recorded source digest matches the DLL in hand (a foreign or unstamped one is ignored in favour of the committed baseline), and fails closed with exit 2 naming the axis it could not baseline. Needs mono/mcs, the built tools, and the live DLL. |
| `tests/test_parity_drift_fail_closed.py` | Drift orchestration rejects an unreadable assembly with exit 2 and never creates an incomplete baseline. Skips unless the C# tools, Mono, and mcs are available. |
| `tests/test_re_dump_regen.py` | Compiles `legacy/DumpFrameEntries` and regenerates non-empty inventory dumps from the local dedicated DLL (needs install + mcs/mono). |
| `tests/test_steam_builds.py` | `steam/steam_builds.py` parses a fixture PICS payload (`--from`) and a fixture `appmanifest`, and returns the right verdicts: exit 0 on a match, 1 on branch or install drift, 2 on an unusable payload, missing pin, or unknown branch; `--print-fetch` emits exactly the `fetch_version.sh <manifest> <label>` line; an `appmanifest` whose `installdir` names a parent tree makes `--verify-install` refuse rather than hash outside the install; a PICS branch whose depot manifest gid is not numeric is refused rather than handed to `fetch_version.sh`; the committed pin names the build whose sha256 is pinned in `stock_facts.json`. Network-free, DLL-free. |
| `tests/test_steam_manifest.py` | `steam/steam_manifest.py` decodes fixture manifests built with a small wire-format encoder and checks the reader, finder, and verifier verdicts (ok / missing / size / SHA-1), the fail-closed paths (bad magic, truncated entry table), the `UNSAFE` verdict for a `..`/absolute entry name (a manifest is a file, so its names must not steer `--verify` outside the root the operator named), and `--json` metadata. When the machine has a cached 294422 manifest plus the installed DLL it also asserts Steam's SHA-1 for `Assembly-CSharp.dll` equals the local file. DLL-free, network-free. |
| `tests/test_steam_manifest_fuzz.py` | Seeded mutation fuzzer over `steam_manifest.py`'s hand-rolled protobuf reader (`read_manifest`): structure-aware valid manifest seeds (whole-file and per-chunk SHA-1 rows, empty and multi-chunk entries), then bit flips, truncation, key-wire-type mangling, length-field inflation, and unterminated varints. Asserts only `ManifestError` escapes, a per-call time budget (pins the bounded varint, which was an unbounded big-int shift loop), entry invariants (non-empty name, non-negative fields, 40-char lowercase-hex SHA-1, table-length arithmetic against the file), determinism, and a round-trip of the encoder's own output. Deterministic seed, stdlib-only, DLL-free, network-free. |
| `tests/test_shader_blob_fuzz.py` | Seeded mutation fuzzer over the byte-level decoders in `shader_blob_dump.py` (`parse_subprogram`, `parse_parameter_blob`/`build_parameter_blob`, `dxbc_chunks`, `input_semantics`, `expected_channels`, `shdr_declaration_counts`, `parse_bind_channels`): structure-aware seeds built from the documented record layouts (a sub-program header, a DXBC container with an ISGN input signature and an SHDR token stream, parameter blobs with constant buffers, nested structs, and all five entry kinds, a bind-channel block), then bit flips, truncation, count and pointer inflation, and sign flips on length fields. Asserts only `ShaderBlobError` escapes, a per-call time budget, that no record list outgrows the bytes that could hold it, determinism, and that a decoded parameter blob re-emits byte for byte and re-emitting is a fixed point. Deterministic seed, stdlib-only, DLL-free, UnityPy-free, seconds to run. |
| `tests/test_research_diff.py` | `research_diff.py` lens parsers and report renderer hold on fixtures: facts flatten skips the volatile stamp and input filename, method keys collapse `Type::Method(params)` to a signature diff, `cap` truncates with a counted tail, the rendered report carries identity/verdict/reproduce sections, a missing sha maps to no Steam build id, and the CLI exits 2 on missing or absent DLL arguments. DLL-free: the live b9→b10 `--pair` run at the end is a research artifact, so it is skipped (with the build command named) unless the built lenses and the retained stock backup are both present. |
| `tests/test_generation_stamp.py` | Every artifact stamp goes through `tooling.generation_stamp()`: `SOURCE_DATE_EPOCH` pins it (padded values accepted, non-integers raise rather than falling back to a stamp that would look recorded), an unset variable still yields a wall-clock UTC stamp, and an AST scan fails any tool that reads the clock for a stamp itself. The scan is self-tested against the seam, and the same rule covers `tools/src/*.cs`: a Mono clock read outside a method that consults `StampEnv` fails, so `extracted_utc` in `stock_facts.json` replays byte for byte. DLL-free, network-free. |
| `tests/test_bounded_runs.py` | `tooling.run_bounded()`, the single place the tools spawn mono, mcs, and `fetch_version.sh`, holds a wall-clock bound: a command that outlives `RE_MONO_TIMEOUT` (default 900 s) reports the timeout rc and names itself in stderr instead of hanging the gate, its grandchild dies with it (the process group is killed, not just the child), a command that finishes passes its own rc/stdout/stderr through untouched, and a non-numeric or non-positive `RE_MONO_TIMEOUT` fails loud rather than meaning "no bound". The shell entry points carry the same bound through `bounded-run.sh` (default 1800 s, whole seconds; a host with no GNU `timeout` warns and runs unbounded), and are pinned here too: the shell wrapper kills its own grandchild and rejects a bad `RE_MONO_TIMEOUT`, and a line scan of `tools/**/*.sh` fails any mono/mcs/monodis child that does not go through `run_bounded`, so a new dump call cannot come back unbounded. DLL-free, network-free. |
| `tests/test_text_encoding.py` | Every text boundary in the Python tooling names its encoding: an AST scan rejects `subprocess.run`/`Popen` in text mode without `encoding=`, and `open()`/`read_text()`/`write_text()` in text mode without one. A runtime half runs `tooling.run_bounded` under `LC_ALL=C` with PEP 538/540 coercion disabled against a child writing raw UTF-8, so the decode is the shared runner's and not the interpreter's locale default. DLL-free, network-free. |
| `tests/bench_version_update_tooling.py` | Version-update tooling benchmark (`make readiness`). Includes mutation checks of the Mono.Cecil pin gate. |
| `tests/bench_asm_body_diff.py` | Deterministic perf gate for the body-diff lens (`make bench-bodydiff`): median retired user-space instructions (`perf stat -e instructions:u`) and child CPU time of `asm_body_diff.py` over the retained stock backup vs the live DLL, asserted in a band against the recorded mono 6.12.0 baseline, plus a wall/CPU overlap check that fails if the two assembly walks stop running concurrently. SKIPs without the two assemblies, perf permission, or the recorded mono version. Instructions are load-independent; wall clock is reported, never asserted. |

Tests that need the local dedicated DLL or built binaries SKIP with a reason on
machines without them, and FAIL with the fix command when the DLL is present but
the prerequisite is missing (`make tools`). Nothing here asserts game constants
as pass conditions.

Every script in this table is runnable directly, so the edit-check loop during a
doc change can be a single gate instead of the whole suite:

```bash
python3 tests/test_doc_link_integrity.py    # one gate, no arguments
python3 tests/test_il_citations.py          # DLL-dependent scripts auto-discover
```

DLL-dependent scripts take an optional `<asm>` argument and otherwise resolve
the dedicated assembly from the `ASM` / `SEVENDTD_ASM` / `SEVENDTD_DS_DIR` env
vars or the standard Steam dedicated-server install paths: `%ProgramFiles(x86)%`,
`%ProgramFiles%` and `%ProgramW6432%` on Windows, `~/.local/share/Steam`,
`~/.steam/steam`, `~/.steam/root` on Linux, `~/Library/Application Support/Steam`
on macOS (`tools/tests/_common.py::find_asm`); with none found they print
`SKIP: assembly not found: ...` rather than silently passing.

The same resolution is what the Makefile's `ASM` and `GAME_ROOT`, and the
`ASM`-less runs of `stock-sync.sh`, `post-update.sh` and `parity/drift-check.sh`,
use: `python3 tools/asm_path.py [--game-dir]` prints it. An explicit variable
wins over the probed roots, and one that points at no file is refused, not traded
for a probed root: `tooling.find_asm` raises `ConfigError` naming the variable,
so a pin run pointed at a build that is not there stops instead of verifying
whatever Steam root the host happens to carry and printing a pass. The gates
turn that into their own verdict (`prereq` FAILs, a gate that skips says why),
and `asm_path.py` keeps its exit 2. `SEVENDTD_SERVER_DIR`
overrides the install root for `make save-roundtrip-all` only.

```bash
make test        # the full gate suite above
make stock-check # stock_facts pins vs live DLL + sibling pins
```

## Policy

Dumps land under `il/` and are **git-ignored** (may contain game IL excerpts;
never redistribute). The tooling here is tracked; the game DLL and the dumps are
not. Regenerate against your own game copy; re-run `Census` and the tests after
any game update to catch patch drift.
