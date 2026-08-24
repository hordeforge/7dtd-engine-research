#!/usr/bin/env bash
# One-shot regeneration of every committed inventory + git-ignored dump set.
# Run after a game update or after changing tools/src, then re-check docs:
#   ASM=".../Assembly-CSharp.dll" ./tools/regen.sh
# Leaves the working tree with fresh dumps (il/, git-ignored) and refreshed
# committed inventories (docs/inventories/*). Follow up with `make test`.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(dirname "$here")"
asm="${ASM:?set ASM to the dedicated Assembly-CSharp.dll path}"

step() { printf '\n== %s ==\n' "$*"; }

step "build tools"
(cd "$here" && ./build.sh)

step "Census (ground-truth counts)"
MONO_PATH="$here/bin" mono "$here/bin/Census.exe" "$asm" 2>&1 | head -10

step "stock facts (live pin)"
(cd "$root" && ./tools/stock-sync.sh)

step "NetPackage wire surface + companion types"
MONO_PATH="$here/bin" mono "$here/bin/DumpNetPackages.exe" "$asm" "$root/il/netpackages-v3.1.0"
MONO_PATH="$here/bin" mono "$here/bin/DumpType.exe" "$asm" "$root/il/netpackages-v3.1.0" \
     EntityCreationData ItemValue ItemStack BlockChangeInfo

step "full surface metadata (committable)"
MONO_PATH="$here/bin" mono "$here/bin/FullSurface.exe" "$asm" "$root/il/surface-v3.1.0"

step "full local IL reversal (git-ignored)"
MONO_PATH="$here/bin" mono "$here/bin/DumpAll.exe" "$asm" "$root/il/full-v3.1.0"

step "wire-body catalog (committed)"
MONO_PATH="$here/bin" mono "$here/bin/WireBodies.exe" "$asm" "$root/docs/inventories/netpackage-bodies.md"

step "console-command registry"
MONO_PATH="$here/bin" mono "$here/bin/CmdMap.exe" "$asm" "$root/docs/inventories/console-command-list.tsv" || true

step "NetPackage channel/compress census (META)"
MONO_PATH="$here/bin" mono "$here/bin/NetProtocolCensus.exe" "$asm" "$root/il/netpackages-v3.1.0/META.md"

step "state-machine index (committed)"
MONO_PATH="$here/bin" mono "$here/bin/StateMachines.exe" "$root/docs" "$root/docs/inventories/state-machines.md"

step "RE coverage report (committed)"
MONO_PATH="$here/bin" mono "$here/bin/Coverage.exe" "$asm" "$root/docs" "$root/docs/inventories/coverage-report.md"

step "legacy per-family dumpers"
# explicit tool -> output-dir mapping (dirs are lowercase in il/)
declare -A legacy_dirs=(
  [DumpDediComplete]=dedi-complete-v3.1.0
  [DumpDeep]=deep-v3.1.0
  [DumpDeeper]=deeper-v3.1.0
  [DumpGaps]=gaps-v3.1.0
  [DumpFrameEntries]=frame-entries-v3.1.0
  [DumpLoopComplete]=loop-complete-v3.1.0
  [DumpOptScan]=opt-scan-v3.1.0
  [DumpTerrain]=terrain-v3.1.0
  [DumpRealEarthSurfaces]=realearth-surfaces-v3.1.0
)
# Legacy dumps stay best-effort (archival tools, superseded by src/), but a
# failed run must be reported like build.sh does for unbuildable sources:
# a silently missing dump set would look identical to a clean regeneration.
for t in "${!legacy_dirs[@]}"; do
  exe="$here/bin/legacy/$t.exe"
  [[ -f "$exe" ]] || { echo "skip $t (missing)"; continue; }
  if ! out="$(MONO_PATH="$here/bin" mono "$exe" "$asm" "$root/il/${legacy_dirs[$t]}" 2>&1)"; then
    printf 'regen: warning: %s dump FAILED:\n%s\n' "$t" "$out" >&2
    legacy_fail=1
  fi
done
if [[ "${legacy_fail:-0}" == "1" ]]; then
  echo "regen: warning: one or more legacy dumps failed; their il/ sets may be stale or absent" >&2
fi

step "consistency + gates"
(cd "$root" && make test)

echo
echo "Regeneration done. Re-check docs/coverage.md census numbers and commit"
echo "the refreshed committed inventories (docs/inventories/*)."
