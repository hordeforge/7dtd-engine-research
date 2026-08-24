#!/usr/bin/env bash
# Patch-drift check: compare the current game build against a stored baseline and
# report what changed (types, methods, enum members, NetPackage wire). Run after a
# game update; exits non-zero if drift is detected (for cron/CI alerting).
#
#   drift-check.sh [ASM]           # ASM defaults to the local stable dedicated DLL
#   BASELINE_DIR=... drift-check.sh
#
# First run with no baseline snapshots writes them and reports "baseline created".
# Requires: mono (mcs), Mono.Cecil, the tools built (../build.sh).
set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS="$(cd "$here/.." && pwd)"
BIN="$TOOLS/bin"
ASM="${1:-$HOME/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll}"
BASELINE_DIR="${BASELINE_DIR:-$HOME/.cache/zdtd-scratch/drift-baseline}"
CECIL="$BIN/Mono.Cecil.dll"

[[ -f "$ASM" ]]   || { echo "drift: game DLL not found: $ASM" >&2; exit 2; }
[[ -f "$CECIL" ]] || { echo "drift: tools not built; run $TOOLS/build.sh" >&2; exit 2; }

# helper builders (compiled on demand into bin/)
build_helper() { # <name> <src>
  local exe="$BIN/$1.exe"
  [[ -f "$exe" && "$exe" -nt "$2" ]] && return 0
  # A failed helper build must not look like "no drift" on that axis; say so.
  if ! mcs -nologo -r:"$CECIL" "$2" -out:"$exe"; then
    echo "drift: warning: failed to compile $1.exe; its drift axis will be skipped" >&2
    return 1
  fi
}
build_helper MethodList "$TOOLS/src/MethodList.cs"
# ParitySurface feeds the NetPackage wire diff below; build it like the other
# helpers so a fresh checkout gets the full drift report (not a silent skip).
build_helper ParitySurface "$here/ParitySurface.cs"
run() { MONO_PATH="$BIN" mono "$@"; }

mkdir -p "$BASELINE_DIR"
cur="$(mktemp -d)"
# snapshot the current build: census, per-type surface, methods, enums, parity
run "$BIN/Census.exe"           "$ASM" > "$cur/census.txt" || \
  echo "drift: warning: Census.exe failed; census diff unreliable" >&2
run "$BIN/FullSurface.exe"      "$ASM" "$cur/surface" >/dev/null || \
  echo "drift: warning: FullSurface.exe failed; type drift unreliable" >&2
if [[ -f "$BIN/MethodList.exe" ]]; then
  run "$BIN/MethodList.exe" "$ASM" "$cur/methods.txt" || \
    echo "drift: warning: MethodList.exe failed; method diff unreliable" >&2
else
  echo "drift: warning: MethodList.exe unavailable; method drift NOT compared" >&2
fi
if [[ -f "$BIN/EnumList.exe" ]]; then
  run "$BIN/EnumList.exe"   "$ASM" "$cur/enums.txt"   || \
    echo "drift: warning: EnumList.exe failed; enum diff unreliable" >&2
else
  echo "drift: warning: EnumList.exe unavailable; enum drift NOT compared" >&2
fi
# Mono may print "mono_thread_internal_set_priority..." on stdout; keep only JSON.
if [[ -f "$BIN/ParitySurface.exe" ]]; then
  run "$BIN/ParitySurface.exe" "$ASM" 2>/dev/null | sed -n '/^{/,$p' > "$cur/parity.json"
  # Reject empty/non-JSON captures so parity_diff does not throw.
  if ! python3 -m json.tool "$cur/parity.json" >/dev/null 2>&1; then
    echo "drift: warning: ParitySurface output not valid JSON; skipping package wire diff" >&2
    rm -f "$cur/parity.json"
  fi
else
  echo "drift: warning: ParitySurface.exe unavailable; package wire drift NOT compared" >&2
fi

if [[ ! -f "$BASELINE_DIR/surface/surface-types.md" ]]; then
  cp -r "$cur/." "$BASELINE_DIR/"
  rm -rf "$cur"
  echo "drift: baseline created at $BASELINE_DIR (no comparison this run)"; exit 0
fi

drift=0
sec() { echo; echo "== $1 =="; }
sec "census"
diff "$BASELINE_DIR/census.txt" "$cur/census.txt" && echo "  (unchanged)" || drift=1
sec "types (added/removed)"
tlist() { awk -F'|' 'NR>3{gsub(/ /,"",$2);print $2}' "$1/surface/surface-types.md" | grep -vE '\$|<>|__' | sort -u; }
added=$(comm -13 <(tlist "$BASELINE_DIR") <(tlist "$cur"))
removed=$(comm -23 <(tlist "$BASELINE_DIR") <(tlist "$cur"))
[[ -n "$added" ]]   && { echo "  ADDED:";   echo "$added"   | awk '{print "    +" $0}'; drift=1; } || echo "  no new types"
[[ -n "$removed" ]] && { echo "  REMOVED:"; echo "$removed" | awk '{print "    -" $0}'; drift=1; }
if [[ -f "$BASELINE_DIR/methods.txt" && -f "$cur/methods.txt" ]]; then
  sec "methods (added/removed on existing+new types)"
  ma=$(comm -13 <(sort -u "$BASELINE_DIR/methods.txt") <(sort -u "$cur/methods.txt") | grep -cvE '\$|<>|__|b__|g__' || true)
  mr=$(comm -23 <(sort -u "$BASELINE_DIR/methods.txt") <(sort -u "$cur/methods.txt") | grep -cvE '\$|<>|__|b__|g__' || true)
  echo "  +$ma methods / -$mr methods"; [[ "$ma" -gt 0 || "$mr" -gt 0 ]] && drift=1
fi
if [[ -f "$BASELINE_DIR/enums.txt" && -f "$cur/enums.txt" ]]; then
  sec "enum members (added/removed)"
  ea=$(comm -13 <(sort -u "$BASELINE_DIR/enums.txt") <(sort -u "$cur/enums.txt") | grep -vE '_0000')
  er=$(comm -23 <(sort -u "$BASELINE_DIR/enums.txt") <(sort -u "$cur/enums.txt") | grep -vE '_0000')
  [[ -n "$ea" ]] && { echo "  ADDED:";   echo "$ea" | awk '{print "    +" $0}'; drift=1; }
  [[ -n "$er" ]] && { echo "  REMOVED:"; echo "$er" | awk '{print "    -" $0}'; drift=1; }
  [[ -z "$ea" && -z "$er" ]] && echo "  (unchanged)"
fi
if [[ -f "$BASELINE_DIR/parity.json" && -f "$cur/parity.json" ]]; then
  sec "NetPackage wire (added/removed/changed)"
  python3 "$here/parity_diff.py" "$BASELINE_DIR/parity.json" "$cur/parity.json" || drift=1
fi
echo
if [[ "$drift" -eq 0 ]]; then echo "drift: NONE (build matches baseline)"; else
  echo "drift: DETECTED. Update baseline after review:  cp -r $cur/. $BASELINE_DIR/"
  echo "Then re-verify affected narratives (see docs/re-methodology.md §5b for the workflow)."; fi
rm -rf "$cur"
exit $drift
