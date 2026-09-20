#!/usr/bin/env bash
# Post-TFP-update orchestration for stock RE pins and surface drift.
#
# After installing a new dedicated build:
#   ./tools/post-update.sh              # extract stock_facts + pin check + drift
#   ./tools/post-update.sh --no-drift   # extract + pin only
#   ./tools/post-update.sh --check-only # pin check only (no extract)
#   ./tools/post-update.sh --steam      # also Steam build id + install integrity
#   ASM=/path/to/Assembly-CSharp.dll ./tools/post-update.sh
#
# --steam adds the Steam side (needs network for the PICS branch table): the
# published/installed build vs the studied pin, and every installed file vs
# Steam's cached manifest (the whole install, about 11 s; use
# steam_builds.py --verify-install Managed for the fast subset). It is opt-in so the default path stays offline, and
# its non-zero rc is reported, not fatal: right after an update the pin is
# expected to be behind until it is re-recorded.
#
# Exit non-zero if pin check fails. Drift may also exit non-zero when baseline
# exists and surface changed (expected after a real update; re-baseline after
# reviewing). Does not regenerate bulk IL dumps (manual / Dump* tools).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASM="${ASM:-$HOME/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll}"

DO_DRIFT=1
DO_STEAM=0
MODE="all"
for arg in "$@"; do
  case "$arg" in
    --no-drift) DO_DRIFT=0 ;;
    --steam) DO_STEAM=1 ;;
    --check-only)
      [[ "$MODE" == "all" ]] || { echo "post-update: choose one mode" >&2; exit 2; }
      MODE="check"
      DO_DRIFT=0
      ;;
    --extract-only)
      [[ "$MODE" == "all" ]] || { echo "post-update: choose one mode" >&2; exit 2; }
      MODE="extract"
      DO_DRIFT=0
      ;;
    -h|--help)
      sed -n '2,18p' "$0"
      exit 0
      ;;
    *) echo "post-update: unknown argument: $arg" >&2; exit 2 ;;
  esac
done

echo "post-update: ASM=$ASM"
echo "post-update: step stock-sync ($MODE)"
case "$MODE" in
  check)   "$HERE/stock-sync.sh" --check-only ;;
  extract) "$HERE/stock-sync.sh" --extract-only ;;
  all)     ASM="$ASM" "$HERE/stock-sync.sh" ;;
esac

if [[ "$DO_DRIFT" -eq 1 ]]; then
  echo "post-update: step drift-check"
  # drift-check exits 0 on first baseline create; non-zero when surface drifted.
  set +e
  "$HERE/parity/drift-check.sh" "$ASM"
  drift_rc=$?
  set -e
  if [[ $drift_rc -ne 0 ]]; then
    echo "post-update: drift-check rc=$drift_rc (review baseline under \$BASELINE_DIR or ~/.cache/zdtd-scratch/drift-baseline)" >&2
    echo "post-update: pin check already passed; fix docs/pins then re-baseline if intentional." >&2
    exit "$drift_rc"
  fi
fi

if [[ "$DO_STEAM" -eq 1 ]]; then
  echo "post-update: step steam build + install integrity"
  set +e
  python3 "$HERE/parity/steam_builds.py" --check --verify-install
  steam_rc=$?
  set -e
  if [[ $steam_rc -ne 0 ]]; then
    echo "post-update: steam check rc=$steam_rc (expected when the pin is behind the" >&2
    echo "  published/installed build, or when a managed file differs from Steam's" >&2
    echo "  manifest; review before re-pinning and before trusting a diff." >&2
    echo "  runtime-written files (platform.cfg) can be excluded with --ignore SUBSTR;" >&2
    echo "  the full verify reads the whole install, ~11 s here)" >&2
  fi
  echo "post-update: step cached builds"
  python3 "$HERE/parity/steam_manifest.py" --history || true
fi

echo "post-update: done (stock facts + pins$([ "$DO_DRIFT" -eq 1 ] && echo ' + drift' || true)$([ "$DO_STEAM" -eq 1 ] && echo ' + steam' || true))"
echo "post-update: next manual steps:"
echo "  - make census   # refresh live counts if needed"
echo "  - re-run Dump* into il/<label>/ only for changed families"
echo "  - commit tools/data/stock_facts.json + pin site edits together"
echo "  - new build?  python3 tools/parity/steam_builds.py --fetch          # pull it"
echo "                python3 tools/parity/steam_builds.py --record         # re-pin"
echo "                python3 tools/research_diff.py --pair <old>:<new>     # delta report"
echo "                python3 tools/parity/steam_manifest.py --diff <old.manifest>  # content delta"
