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
| `legacy/` | archival | best-effort build; canonical family dumpers run from `regen.sh` |

## Log

### 2026-09-20

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
  ShellCheck) and all 38 archival dumpers build against the pinned Cecil.
- The live-DLL `make test` suite passed its first four gates, then correctly
  rejected the installed V3.1.0 b4 DLL because the corpus is pinned to b14 (13
  reported pin differences). A matching b14 DLL is not installed locally, so
  the remaining live gates are not verified in this session.
