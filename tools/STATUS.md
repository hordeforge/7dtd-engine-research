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
