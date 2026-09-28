#!/usr/bin/env bash
# Regenerate tools/data/stock_facts.json from the live dedicated Assembly-CSharp.dll
# and verify research + sibling product pins still match.
#
#   ./stock-sync.sh              # extract + check
#   ./stock-sync.sh --check-only # only run check_stock_facts.py
#   ./stock-sync.sh --extract-only
#   ASM=/path/to/Assembly-CSharp.dll ./stock-sync.sh
#
# ASM is optional: without it the dedicated assembly is discovered from
# SEVENDTD_ASM / SEVENDTD_DS_DIR and the Steam install roots of this OS
# (tools/asm_path.py, the resolution the Python tools use).
#
# After a TFP patch: run this, fix any FAIL sites, commit stock_facts.json + pin edits.
# SOURCE_DATE_EPOCH=<epoch> pins the extracted_utc stamp, so re-running the
# extraction over an unchanged DLL reproduces stock_facts.json byte for byte
# instead of dirtying the tree with a new wall-clock second.
# Full post-update path (facts + pins + optional drift): tools/post-update.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN="$HERE/bin"
DATA="$HERE/data"
FACTS="$DATA/stock_facts.json"
# ASM unset: the same resolution the Python tools use (ASM/SEVENDTD_ASM/
# SEVENDTD_DS_DIR first, then every Steam root of this OS), so a Windows or
# macOS install is found without handing over a path. Empty when nothing is
# found; extract() and the drift hook below report it.
ASM="${ASM:-$(python3 "$HERE/asm_path.py")}"
# Wall-clock bound on the compiler and the extractor (tools/bounded-run.sh):
# either one wedged must fail the sync, not hold it open.
# shellcheck source=tools/bounded-run.sh
. "$HERE/bounded-run.sh"

MODE="all"
for arg in "$@"; do
  case "$arg" in
    --check-only)
      [[ "$MODE" == "all" ]] || { echo "stock-sync: choose one mode" >&2; exit 2; }
      MODE="check"
      ;;
    --extract-only)
      [[ "$MODE" == "all" ]] || { echo "stock-sync: choose one mode" >&2; exit 2; }
      MODE="extract"
      ;;
    -h|--help)
      sed -n '2,/^[^#]/ { /^#/ { s/^#[[:space:]]\{0,1\}//; p; } }' "$0"
      exit 0
      ;;
    *) echo "stock-sync: unknown argument: $arg" >&2; exit 2 ;;
  esac
done

extract() {
  # Put the previous pin pair back after a half-finished publish. A pin file
  # that did not exist before the run is removed, so the tree lands where it
  # started rather than half-refreshed.
  restore_pins() {
    local pair target backup
    for pair in "$FACTS:prev_stock_facts.json" "$DATA/xml_pins.json:prev_xml_pins.json"; do
      target="${pair%%:*}"
      backup="$tmpdir/${pair##*:}"
      if [[ -f "$backup" ]]; then
        cp -p "$backup" "$target"
      else
        rm -f "$target"
      fi
    done
    echo "stock-sync: publish failed; the previous pin pair was restored" >&2
  }
  if [[ -z "$ASM" ]]; then
    echo "stock-sync: no dedicated server found; install it or set ASM=..., SEVENDTD_ASM=... or SEVENDTD_DS_DIR=..." >&2
    exit 2
  fi
  if [[ ! -f "$ASM" ]]; then
    echo "stock-sync: game DLL not found: $ASM" >&2
    exit 2
  fi
  # build.sh owns bin/: it applies one freshness rule (source, the pinned
  # Mono.Cecil, and bin/.toolchain-stamp) to every exe. This script used to
  # compile StockFacts.exe itself on a weaker key that ignored the compiler, and
  # the exe it wrote then satisfied build.sh's own up-to-date check.
  echo "stock-sync: building tools..."
  (cd "$HERE" && ./build.sh --skip-legacy)
  if [[ ! -f "$BIN/StockFacts.exe" ]]; then
    echo "stock-sync: build.sh did not produce bin/StockFacts.exe" >&2
    exit 2
  fi
  mkdir -p "$DATA"
  tmpdir="$(mktemp -d "$DATA/.stock-sync.XXXXXX")"
  trap 'rm -rf "$tmpdir"' EXIT
  echo "stock-sync: extracting from $ASM"
  MONO_PATH="$BIN" run_bounded mono "$BIN/StockFacts.exe" "$ASM" "$tmpdir/stock_facts.json"
  # XML data pins (zombie HP ladder etc.) from the same install's Data/Config.
  if ! GAME_ROOT="$(python3 "$HERE/asm_path.py" --game-dir)"; then
    echo "stock-sync: $ASM is not inside a dedicated-server install, so the Data/Config pins cannot be read" >&2
    exit 2
  fi
  python3 "$HERE/xml_pins.py" --game-dir "$GAME_ROOT" --pins "$tmpdir/xml_pins.json" >/dev/null
  # Both pins are committed together and must describe the same install, so the
  # publish is one step: the staged pair is put aside, the new pair is moved in,
  # and a move that fails puts the previous pair back. Two plain `mv`s left a
  # window where a killed run left this build's stock_facts.json beside the
  # previous build's xml_pins.json, a pair no gate can tell from a deliberate
  # one until the next full sync.
  local staged
  for staged in "$tmpdir/stock_facts.json" "$tmpdir/xml_pins.json"; do
    if [[ ! -f "$staged" ]]; then
      echo "stock-sync: $staged was not written; nothing published" >&2
      exit 2
    fi
  done
  if [[ -f "$FACTS" ]]; then cp -p "$FACTS" "$tmpdir/prev_stock_facts.json"; fi
  if [[ -f "$DATA/xml_pins.json" ]]; then cp -p "$DATA/xml_pins.json" "$tmpdir/prev_xml_pins.json"; fi
  mv "$tmpdir/stock_facts.json" "$FACTS" || { restore_pins; exit 2; }
  mv "$tmpdir/xml_pins.json" "$DATA/xml_pins.json" || { restore_pins; exit 2; }
  rmdir "$tmpdir"
  trap - EXIT
  echo "stock-sync: wrote $FACTS"
  echo "stock-sync: wrote $DATA/xml_pins.json"
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

# Optional drift hook for manual callers: STOCK_SYNC_DRIFT=1 ./stock-sync.sh
# appends parity/drift-check.sh after extract+check. The usual orchestration is
# tools/post-update.sh, which calls drift-check.sh directly (and handles rc).
if [[ "${STOCK_SYNC_DRIFT:-0}" == "1" ]]; then
  echo "stock-sync: STOCK_SYNC_DRIFT=1 -> parity/drift-check.sh"
  "$HERE/parity/drift-check.sh" "$ASM"
fi
