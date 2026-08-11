#!/usr/bin/env bash
# Regenerate tools/data/stock_facts.json from the live dedicated Assembly-CSharp.dll
# and verify research + sibling product pins still match.
#
#   ./stock-sync.sh              # extract + check
#   ./stock-sync.sh --check-only # only run check_stock_facts.py
#   ./stock-sync.sh --extract-only
#   ASM=/path/to/Assembly-CSharp.dll ./stock-sync.sh
#
# After a TFP patch: run this, fix any FAIL sites, commit stock_facts.json + pin edits.
# Full post-update path (facts + pins + optional drift): tools/post-update.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
BIN="$HERE/bin"
DATA="$HERE/data"
FACTS="$DATA/stock_facts.json"
ASM="${ASM:-$HOME/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll}"

MODE="all"
for arg in "$@"; do
  case "$arg" in
    --check-only) MODE="check" ;;
    --extract-only) MODE="extract" ;;
    -h|--help)
      sed -n '2,14p' "$0"
      exit 0
      ;;
  esac
done

extract() {
  if [[ ! -f "$ASM" ]]; then
    echo "stock-sync: game DLL not found: $ASM" >&2
    echo "  set ASM=... or install the dedicated server." >&2
    exit 2
  fi
  if [[ ! -f "$BIN/Mono.Cecil.dll" ]]; then
    echo "stock-sync: building tools (need Mono.Cecil)..."
    (cd "$HERE" && ./build.sh --skip-legacy)
  fi
  if [[ ! -f "$BIN/StockFacts.exe" ]] || [[ "$HERE/src/StockFacts.cs" -nt "$BIN/StockFacts.exe" ]]; then
    echo "stock-sync: compiling StockFacts.exe"
    mcs -nologo -r:"$BIN/Mono.Cecil.dll" "$HERE/src/StockFacts.cs" -out:"$BIN/StockFacts.exe"
  fi
  mkdir -p "$DATA"
  echo "stock-sync: extracting from $ASM"
  MONO_PATH="$BIN" mono "$BIN/StockFacts.exe" "$ASM" "$FACTS"
  # XML data pins (zombie HP ladder etc.) from the same install's Data/Config.
  python3 "$HERE/xml_pins.py" --game-dir "$(dirname "$(dirname "$ASM")")" >/dev/null && \
    echo "stock-sync: wrote $HERE/data/xml_pins.json"
  echo "stock-sync: wrote $FACTS"
}

check() {
  if [[ ! -f "$FACTS" ]]; then
    echo "stock-sync: no $FACTS; run without --check-only first" >&2
    exit 2
  fi
  python3 "$HERE/tests/check_stock_facts.py" --facts "$FACTS" --require-live
}

case "$MODE" in
  extract) extract ;;
  check) check ;;
  all) extract; check ;;
esac

# Optional drift hook for callers that set STOCK_SYNC_DRIFT=1 (post-update.sh).
if [[ "${STOCK_SYNC_DRIFT:-0}" == "1" ]]; then
  echo "stock-sync: STOCK_SYNC_DRIFT=1 -> parity/drift-check.sh"
  "$HERE/parity/drift-check.sh" "$ASM"
fi
