# Tooling status

Maintainer log for the supported RE tooling surface. This records what was
checked, what is supported, and what still needs evidence. Detailed usage stays
in [README.md](README.md); research findings stay in `docs/`.

Status terms:

- **supported**: documented entry point with a build or runnable gate
- **experimental**: useful research code, but not a stable interface
- **archival**: retained only to reproduce historical dump sets

## Current surface

| Area | Status | Verification |
|---|---|---|
| `src/*.cs` | supported | `make tools`; warnings are errors |
| top-level `*.py` | supported | `make test-docs`, `make test`, or a named Make target |
| top-level `*.sh` | supported | `make lint`; workflow-specific checks in `make verify` and `make test` |
| `parity/` | supported | `make drift`; pure diff logic covered by the documented test suite |
| `tests/` | supported | executable gate scripts, enumerated by Make; not unittest discovery tests |
| `sandbox/` | experimental | lint plus focused safe-name, dependency-lock, and Zig-table gates |
| `re-scratch/` | experimental | one-off format probes; compile/run manually when revisiting the format |
| `legacy/` | archival | 12 canonical family dumpers, best-effort build; run from `regen.sh` |

## Log

### 2026-09-20

- `research_diff.py --pair` accepts a path to an assembly outside the install dir
  (a steamcmd scratch download, for example): the side is loaded directly and its
  report label comes from the version it reports, while the depot manifest and
  parity snapshot still resolve by SHA-1 and version name. `pair:` prints the
  derived label next to the input when they differ.
- The facts lens notes when a side has no sibling `LiteNetLib.dll` (that is how
  StockFacts pins the `litenet.*` rows), so a lone copied assembly shows those
  rows as missing rather than changed.

- `test_install_integrity.py` also asserts the installed build *is* the studied
  one: the appmanifest's build id and depot manifest must equal
  `tools/data/steam_builds.json`. An asset-only patch moves the installed build
  without changing the studied DLL's facts, so `make stock-check` would stay
  green while the docs cite the previous build; this gate notices and names the
  fix (`steam_builds.py --record` after review). Proved by temporarily setting
  the pin to the previous build id: the gate fails naming both ids, and
  restoring the pin returns it to green.

- `make install-check` runs the whole-install integrity check with the game root
  derived from `ASM`/`GAME_ROOT` (no triple-`dirname` to remember):
  `ARGS="--only Managed"` is the fast subset, `ARGS="--ignore platform.cfg"`
  skips runtime-written files. `post-update.sh --steam` now verifies the whole
  install rather than just `Managed`, and its hint names `--ignore` and the
  runtime cost; the step stays non-fatal and reports rc.

- Ran the first whole-install integrity check (`steam_manifest.py --verify <game
  dir>`): 17,532 files, 17.6 GB, about 11 s, and exactly one difference,
  `platform.cfg` (67 bytes locally against the manifest's 71). Both cached
  manifests ship the same 71-byte file, so Steam's manifest-diff update never
  noticed the local edit and never restored it.
- `--ignore SUBSTR` (repeatable) on both `steam_manifest.py --verify` and
  `steam_builds.py --verify-install` skips such runtime-written paths and
  reports the ignored count rather than hiding it: the full install then reads
  "17532 ok, 0 missing, 0 mismatch, 1 ignored". The filter applies after
  `--only`, so `--only Managed --ignore platform.cfg` reports 0 ignored.

- `research_diff.py` schedules its lenses longest-first (`bodies` 1.7 s, then
  `metadata` 1.1 s; the rest under 0.4 s) while keeping the fixed report order,
  so a cheap lens no longer holds a worker while the body walk waits. Report p50
  over the real pair: 2567 ms to 2197 ms. Content is unchanged (the
  committed-artifact gate re-derives the report, and `--jobs 1` still renders a
  byte-identical section order).

- `test_cli_args_wired.py` now checks the CLI surface in both directions: a read
  with no declaration (the stale-flag bug) and a declaration nothing reads (a
  dead flag, the other half of the same removal). `dest=` is honoured and the
  detector is self-tested both ways; proven by dropping a probe tool with an
  unread `--dead` flag, which fails by name, and removing it restores green.
- `steam_manifest.py` owns the depot-entry lookups (`assembly_entry`,
  `assembly_sha1`, `manifest_for_gid`); `research_diff.py` had three copies of
  the `Managed/Assembly-CSharp.dll` entry search across its provenance and
  `--pair` resolution paths.

- `post-update.sh --steam` folds the Steam side into the documented post-patch
  path (opt-in, so the default run stays offline): published/installed build vs
  the studied pin, local `Managed/` vs Steam's cached manifest, the cached-build
  history, and the fetch/re-pin/delta-report commands as next steps. A non-zero
  rc from that step is reported with the reason, not fatal, since the pin is
  expected to be behind until re-recorded. The shell help gate now also asserts
  the flag is documented and unknown options still exit 2.

- `research_diff.py` gained a per-type metadata lens (`FullSurface.exe`):
  added/removed types plus changed kind/base/field-count/method-count/IL rows,
  which no other lens covered. Over the real b9/b10 pair it reports exactly the
  three documented changes (`RequestDetails` fields 4 to 6, and the Burst
  job-reflection type rename as one added plus one removed), so the
  changelog-3.2.0 section 8 metadata claim is now machine-checked by the report.
  The two 0.5 s `FullSurface` runs overlap with the body walk, so the report p50
  stays at 2567 ms (was 2585 ms).

- `research_diff.py` runs its independent lenses concurrently (`--jobs`, default
  `min(4, CPUs)`): the report p50 over the real b9/b10 pair dropped 3352 ms to
  2585 ms with `--jobs 4` (per-lens: body diff 1.66 s, method lists 0.33 s,
  census 0.20 s, depot 0.14 s, rest under 0.1 s). `--jobs 1` is the reference and
  renders a byte-identical report; the `--jobs` flag is stripped from the
  reproduce line like `--out`/`--json`, so the report stays deterministic.
  `tests/test_research_diff.py` asserts the jobs=1 versus default equality.

- Added `tests/test_install_integrity.py`: the live suite now asserts the whole
  installed `Managed/` payload still matches Steam's cached depot manifest for the
  installed build, not just the studied `Assembly-CSharp.dll` that `make
  stock-check` re-extracts. It drives `steam_builds.py --check --verify-install
  Managed --json` and requires 0 missing / 0 mismatch against the appmanifest's
  own manifest gid; SKIPs when that manifest is not cached. Proved to fire by
  pointing `--install-dir` at a one-file copy: `FAIL local install differs from
  Steam's manifest (1 mismatch, 148 missing)`, exit 1.

- `docs/INDEX.md` now carries a "Committed research artifacts" table (the parity
  snapshots, the b9 to b10 report, the Steam build pins) with what each proves
  and how to regenerate it, the `tools/parity/` row names the Steam build and
  manifest tools, and the gates line lists `make latest ARGS="--check
  --verify-install Managed"`, `make drift`, and `make bench-bodydiff`. The
  `make latest` help line names the integrity flag too.

- `research_diff.py --pair` also accepts raw Steam build ids
  (`--pair 24911252:24994542`): the id resolves through its cached depot
  manifest's SHA-1 to a local DLL, and the parity snapshots fall back to the
  resolved build's version name (`parity_b9.json`), so a build-id pair measures
  all eight lenses just like `b9:b10`.
- `research_diff.py` reports depot provenance: the identity table gained `depot
  manifest` and `depot file SHA-1` rows, the latter Steam's own SHA-1 for that DLL
  with a match/mismatch against the local file, so the report itself states that the
  bytes compared are the bytes Steam shipped for those builds. A mismatch prints a
  WARNING and marks the cell; an absent manifest reads `not checked`. The committed
  b9 to b10 report was regenerated with both cells matching.
- `steam_builds.py --verify-install [SUBSTR]` hashes local files against Steam's
  manifest for the installed build (gid taken from the appmanifest, falling back to
  the selected branch), and `--check` now fails on any mismatch or missing file, so
  `make latest ARGS="--check --verify-install Managed"` answers "studied build and
  stock managed bytes" in one command. A filter keeps it fast (149 files for
  `Managed`); without one it reads the whole install. The install directory comes
  from the appmanifest's `installdir` or `--install-dir`.
- `parity/drift-check.sh` now compares the NetPackage wire axis against the
  committed `workspace/outputs/parity/parity_b10.json` when its own baseline dir
  has no `parity.json` (a fresh checkout), so the first `make drift` gives a
  verdict instead of only creating a baseline; `PARITY_BASELINE` overrides it. The
  update advice names the baseline actually in force. Gated by
  `tests/test_drift_committed_baseline.py` (fresh baseline compared, perturbed
  snapshot detected with exit 1, absent snapshot stays quiet).
- Added `tests/test_committed_diff_artifacts.py`: the committed parity snapshots and
  the b9 to b10 report are re-derived and compared, so an artifact cited by the docs
  cannot silently go stale after a lens or format change (the report had to be
  regenerated by hand when the depot lens was added). Only the `Generated <stamp>`
  line is normalised; it SKIPs unless the live DLL is the studied build, the backup
  is the report's baseline, the cached manifests are present, and exactly one
  committed report exists. Proved by appending a line to the report: rc 1 naming it.
- `research_diff.py` reproduce line no longer carries the output/summary flags, and
  `--out -` writes the report with `sys.stdout.write` so stdout equals the file byte
  for byte (the gate above compares them).
- Replaced the hand-kept Python-CLI list in `tests/test_python_cli_usage.py` with
  AST discovery (`_common.argparse_clis`), shared with `test_cli_args_wired.py`. The
  old list had already drifted: `facts.py`, `census-pct.py`, `cross_repo_links.py`,
  `xml_pins.py`, and `zdtd_cite_check.py` were unchecked. The gate now covers 18
  discovered CLIs, each of which must print `--help` without its optional runtime
  dependencies and be named in `tools/README.md`; the two undocumented sandbox
  preset scripts were added to the table. Detector liveness is asserted (a known
  tool is found, nothing under `tests/` is scanned) and proven by an undocumented
  probe file, which fails the gate by name.
- `research_diff.py --pair OLD:NEW` (e.g. `--pair b9:b10`) resolves a known build pair
  in one command: candidate DLLs are matched on the version each reports, the
  cached depot manifest is matched on the DLL's own SHA-1 (which also supplies the
  Steam build id), and the committed parity snapshots are picked up by label.
  Nothing is silent: a `pair:` line names each resolved file, manifest and build
  id. The committed b9 to b10 report was regenerated through it, so its identity
  table now shows Steam builds 24911252 and 24994542 and its reproduce line is
  `python3 tools/research_diff.py --pair b9:b10`.
- Committed `workspace/outputs/parity/parity_b9.json` and `parity_b10.json`
  (ParitySurface snapshots for the two cached builds). `parity_diff.py` reports
  0 added / 0 removed / 0 changed wire between them, so changelog-3.2.0 section 8's
  no-NetPackage-drift claim is machine-checked and the next patch has a local
  baseline. The b9 to b10 report was regenerated with all eight lenses measured
  (wire parity now "no change" instead of "not measured"). The fake steamcmd
  learned a gid-to-DLL map so one run reproduces both snapshots.
- `research_diff.py` gained the depot-manifest lens (`--steam-manifest-old` /
  `--steam-manifest-new`), so one report carries the managed delta and the
  non-managed content delta; the committed b9 to b10 report was regenerated with
  it. The fake-steamcmd test also covers `steam_builds.py --fetch` handing the
  branch manifest through to `fetch_version.sh`.
- Added `tests/test_fetch_version_fake_steamcmd.py`: `parity/fetch_version.sh` had no
  test because it needs SteamCMD and a multi-GB depot. A recording fake steamcmd
  (logs argv, materialises a DLL from the live install into the content or install
  dir) now exercises the manifest form (manifest id passed through, published
  snapshot identical to a direct `ParitySurface.exe` run on the same bytes), the
  branch form, and both fail-closed paths (a steamcmd that does nothing or exits
  non-zero must not publish a partial snapshot). Offline; wired into `make test`.
- Documented the non-managed content lens in `docs/meta/re-methodology.md` 5b-ii:
  depot-manifest `--history`/`--find`/`--verify`/`--diff`, the b9 to b10 result
  (16 changed files, matching the client log), and the mtime-window caveat.
- Fixed the stale `args.url` left in `steam_builds.py` by dropping `--url` (the
  live PICS path crashed; the tests only exercised `--from`) and added
  `tests/test_cli_args_wired.py`: every `args.<name>` a maintained Python tool
  reads must be declared by an `add_argument` in the same file. The detector is
  self-tested and provably fires on the reintroduced bug; files that rebind the
  name `args` are skipped and counted (3 today).
- Applied the ponytail-audit deletions after a fresh reference sweep: removed the
  26 superseded ad-hoc legacy helpers (`DumpOne*`, `DumpNamed`, `DumpNested`,
  `DumpNodes`, `DumpReg`, `DumpMgr`, `DumpScan`, `DumpIter`, `DumpFull`,
  `DumpAstar`, `DumpAuth`, `DumpVoxel`, `DumpTps`, `DumpType(s)`,
  `DumpTypeBases`, `DumpExtraSurfaces`, `Find{FieldWrite,Log,Sub,Type}`,
  `ListMethods`, `DumpMethods`, `DumpMethodByName`), `src/ListAllTypes.cs`, and
  the dead `save_roundtrip_check.discover_save_dir`. `legacy/` is now the 12
  canonical family dumpers that `regen.sh` and the docs actually name, and
  `build.sh` prunes `bin/legacy/*.exe` whose source is gone so a deleted dumper
  cannot stay runnable. Also dropped `steam_builds --url` (nobody set it),
  merged its two `stock_facts.json` loaders into one, and dropped
  `research_diff.Source.buildid_from` (assigned, never read).
- `steam_builds.py --record` now keeps superseded pins in the pin file's
  `history` (capped at 10, deduped by build id), and the default report prints
  an `earlier builds:` line. `steam_manifest.py` reads the same file via
  `--pins` as a fallback for gid-to-build-id labelling when the client log has
  rotated. `data/steam_builds.json` seeded with b9 (build id 24911252, gid
  1712639873522480804).

- Added `research_diff.py` (supported): one-pass build-to-build report over the
  maintained lenses (facts, census, method signatures, enum members, method
  bodies, optional wire parity), stamped with both inputs' bytes, sha256,
  version and Steam build id (mapped through the `steam_builds.json` pin).
  Writes `workspace/outputs/diffs/<old>-to-<new>-<date>.md`, `--check` exits 1
  on drift, `--json` prints the summary. Ran it on the retained b9 backup vs the
  live b10 DLL: it independently reproduces the documented delta (version 9 to
  10, six `Platform.EOS.RemoteFileStorage` body changes, the Burst job-reflection
  rename, zero census/signature/enum drift). Report committed and linked from
  `docs/releases/changelog-3.2.0.md` §8. Gated by `tests/test_research_diff.py`
  (fixture parsers + renderer + CLI contract, DLL-free).
- Added `parity/steam_manifest.py` (supported): reads the Steam client's
  cached depot manifest (`<steam>/depotcache/<depot>_<gid>.manifest`) and gives
  Steam's own per-file checksums offline. For the dedicated depot 294422 the
  file is plaintext protobuf (magic `0x71F617D0`, entry table length at offset
  4), so `--find` prints a path's size + SHA-1 and `--verify DIR [--only SUBSTR]`
  hashes local files against Steam's SHA-1s (exit 1 on missing/short/mismatch);
  `--list --json` emits the 17624-entry table and `--manifest FILE` reads an
  older cached build; `--history` lists every cached build of the depot with the
  Steam build id paired from the client's `logs/content_log.txt`; `--diff OLD.manifest`
  labels both ends with their build id and lists the per-file delta between two
  cached builds with both SHA-1s (b10 vs b9: 16 changed, 0 added, 0 removed,
  matching the client's content_log line). `steam_builds.py` imports the same cache
  lookup and marks each branch `cached`, with an `offline-diffable: N of M` line, so
  the branch table answers which builds can be diffed without a fetch. This is the
  checksum source SteamDB cannot provide (it
  403s scripted clients and has no API). Gated by `tests/test_steam_manifest.py`
  (fixture manifests + a real-cache integration check when present).
- Profiled the research diff loop and cut its dominant cost. `asm_body_diff.py`
  now hashes method bodies zero-allocation (one buffer and one SHA256 per
  assembly instead of per-instruction BitConverter/UTF8/ToArray) and walks the
  two assemblies on two threads with a hasher instance each (no shared mutable
  state). Measured on the b9 backup vs the live b10 DLL: retired instructions
  44.2e9 -> 41.8e9, `asm_body_diff` wall p50 2370 -> 1565 ms, `research_diff`
  p50 3182 -> 2364 ms, byte-identical report output. Gated by
  `tests/bench_asm_body_diff.py` (`make bench-bodydiff`).
- Made the local `make test` suite runnable again on hosts where mono prints
  `mono_thread_internal_set_priority: unknown policy 5` on stdout before any
  tool output: `tests/test_ilfmt_safe.py` parsed those lines as tab-separated
  probe rows. `tests/_common.strip_mono_noise` now drops the startup chatter
  in `run_tool`/`run_probe`, and the probe gate filters its direct mono call.
  Full 25-gate live `make test` green afterwards.
- Added `parity/steam_builds.py` (supported): newest dedicated-server build from
  Steam's PICS app info (branch build ids + depot 294422 manifest ids), the local
  install's build id from its `appmanifest`, and the studied-build pin in
  `data/steam_builds.json` (branch, build id, manifest, version, DLL sha256).
  `--check` fails (1) on a newer build or a stale install, `--print-fetch`/`--fetch`
  hand the manifest to `fetch_version.sh` (an unlisted branch such as
  `latest_experimental` falls back to the branch form), `--record` re-pins. SteamDB has no
  public API and 403s scripted clients, so the machine path is PICS; the human
  page stays linked in the docstring. Wired as `make latest` and gated by
  `tests/test_steam_builds.py` (fixture PICS + appmanifest, network-free).
- `asm_body_diff.py` now stamps both inputs with their byte size and sha256
  before the body-hash report, so a diff can be attributed to exact bytes (and
  back to a Steam build id through the `steam_builds.json` pin).

### 2026-09-06

- Added `asm_body_diff.py` (supported): pairwise Mono.Cecil method-body hash of
  two managed assemblies; catches same-size IL rewrites FullSurface type-row
  diffs miss. Wired into `test_python_cli_usage.py`. Fixed `dump_diff.py` usage
  string (`vdiff.py` → `dump_diff.py`). Re-verified b10 claims against EOS.dll
  `Result` enum (`ldc.i4.s 20` = `NoChange`, not `AlreadyPending`) and
  `EFileDownloadResult.Other` for cancel completion.

### 2026-09-05

- Retargeted hub pins to V3.2.0 b10 after a Steam dedicated/client download
  (app 294420 buildid 24994542). Census unchanged; managed delta confined to
  `Platform.EOS.RemoteFileStorage` cancel path (see `docs/releases/changelog-3.2.0.md`
  §8). Re-extracted `stock_facts.json` (xml pins byte-identical). Sibling
  version pins bumped in `7dtd-loadgen` PackageCodec and `zdtd-server`
  `src/version.zig`.

### 2026-08-28

- Retargeted the whole corpus to the V3.2.0 b9 dedicated build: regenerated all
  `il/*-v3.2.0/` dump sets and the committed inventories (`netpackage-bodies.md`,
  `console-command-list.tsv`, `state-machines.md`, `coverage-report.md`) via
  `regen.sh` (pin check fails by design until docs re-pinned; dump steps then
  run), re-extracted `stock_facts.json` + `xml_pins.json` (xml pins byte-identical).
- Added `dump_diff.py` (supported, top-level): method-level diff of two
  `il/full-<version>/` trees; used for the exact 3.1.0->3.2.0 diff (115 changed
  types, 70 new, 51 removed files). Ruff + mypy `--strict` clean; smoke-tested
  against the retained 3.1.0 sets.

### 2026-08-26

- Inventoried all tracked C#, Python, shell, and Zig tooling source across the
  supported, experimental, archival, and test surfaces.
- Confirmed the maintained C# surface builds warning-clean against pinned
  Mono.Cecil 0.11.5.0 (`make tools`: 19 executables).
- Confirmed all DLL-free product gates pass (`make test-docs`: 22 scripts).
- Found and removed two stale Ruff suppressions in
  `sandbox/try_extract_presets.py`; they made the documented lint gate fail.
- Replaced that probe's developer-specific `/home/maci` default with a portable
  home-relative Steam path while preserving its optional path argument.
- Removed two obsolete `$HOME/Desktop/7dtd/...` Cecil lookup special cases from
  `build.sh`; supported discovery is now the explicit override, local/cache
  copies, and standard system GAC locations.
- Made `cecil-pin.sh` replace its reviewed integrity pin atomically, preventing
  interruption from truncating the existing pin.
- Made `xml_pins.py` use the same atomic replacement guarantee for generated
  JSON pins.
- Removed the clone-source coverage mode from `parity_diff.py`; the supported
  parity tool now compares stock snapshots only, matching repository scope.
- Added a focused parity CLI regression gate for unchanged, changed, and invalid
  invocations.
- Corrected stale `re-scratch` documentation that still described the removed
  probes and claimed hardcoded input paths.
- Productized the sandbox difficulty-preset extractor: defaults resolve beside
  the script, XML uses the standard parser, malformed codes fail explicitly,
  option defaults come from the extracted tables, and a DLL-free gate covers
  all six tiers plus malformed input.
- Made `parity/drift-check.sh` fail closed with exit 2 when any census, type,
  method, enum, or package axis cannot be measured; incomplete snapshots can no
  longer create a baseline or report no drift. Temporary snapshots now clean up
  through an exit trap.
- Fixed `regen.sh` to forward its required `ASM` path into `stock-sync.sh`;
  non-default regeneration can no longer dump one build while pinning another.
- Made full regeneration fail when any of its nine canonical archival dumpers
  is missing or fails, instead of printing a successful completion over stale
  dump sets.
- Made `post-update.sh` and `stock-sync.sh` reject unknown arguments and
  conflicting modes, preventing a mistyped check-only invocation from falling
  through to extraction.
- Hardened `parity/fetch_version.sh`: it no longer downloads and executes
  unverified SteamCMD, reuses the repository's pinned Cecil build, rejects
  path-like labels, supports an explicit Steam content root for manifest
  downloads, and atomically publishes only valid JSON snapshots.
- Made stock pin extraction transactional: `stock_facts.json` and
  `xml_pins.json` are now generated in a temporary directory and replace the
  committed pair only after both extractors succeed.
- Aligned `post-update.sh` mode behavior with its interface: `--check-only` and
  `--extract-only` no longer run an additional drift pass.
- Scope audit found `sandbox/gen_zig_tables.py` and `gen_atlas_zig.py` generate
  clone-owned source. Moving them requires coordinated edits in `zdtd-server`,
  whose generated files and provenance docs point back here; they remain pending
  rather than breaking that regeneration path from this repository alone.
- Made `sandbox/extract_sandbox_tables.py` reject empty option/value-set
  extraction and replace generated JSON atomically.
- Standardized missing-argument behavior across all 20 maintained C# CLIs:
  usage goes to stderr and exits 2. A runtime gate inventories `src/` plus
  `ParitySurface` so new maintained commands inherit the contract.
- Added side-effect-free `--help` across seven supported shell CLIs and strict
  option rejection to `build.sh` and `regen.sh`, with a DLL-free interface gate.
- Made the dnfile and UnityPy extractors expose help without optional packages
  installed and report missing dependencies as usage errors. Atlas extraction
  now supports `--out-dir`, stages a complete non-empty result, rejects filename
  collisions, removes stale XMLs, and replaces each output atomically.
- Tightened the future-update sandbox-preset scanner to target the exact client
  `sandbox_presets` TextAsset, require a unique match, and atomically save only
  when `--out` is explicit.
- Removed an inert three-line Zig fragment and a non-building RealEarth DEM
  probe from `re-scratch/`; the two remaining stock `.tts` probes build.
- Kept the executable-script test model. Converting 33 purpose-built gates to
  unittest/pytest would add churn without improving the supported Make interface.
- Confirmed the full static gate passes (`make lint`: Ruff check/format plus
  ShellCheck) and all 12 archival dumpers build against the pinned Cecil (the 26
  superseded ad-hoc helpers were deleted).
- The live-DLL `make test` suite passed its first four gates, then correctly
  rejected the installed V3.1.0 b4 DLL because the corpus is pinned to b14 (13
  reported pin differences). A matching b14 DLL is not installed locally, so
  the remaining live gates are not verified in this session.
