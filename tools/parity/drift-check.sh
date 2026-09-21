#!/usr/bin/env bash
# Patch-drift check: compare the current game build against a stored baseline and
# report what changed (types, methods, enum members, NetPackage wire). Run after a
# game update; exits 1 if drift is detected (for cron/CI alerting), and fails
# closed with exit 2 if any axis cannot be measured (no partial comparison).
#
#   drift-check.sh [ASM]           # ASM defaults to the local stable dedicated DLL
#   BASELINE_DIR=... drift-check.sh
#   PARITY_BASELINE=... drift-check.sh   # committed wire snapshot (default below)
#
# Every axis has a committed baseline in workspace/outputs/baseline/ (and the
# wire axis one in workspace/outputs/parity/), so a fresh checkout gets a real
# drift verdict on the first run instead of "baseline created". The machine-local
# BASELINE_DIR takes precedence once it exists.
# Requires: mono (mcs), Mono.Cecil, the tools built (../build.sh).
set -uo pipefail
# sort/comm below compare baseline vs current listings byte-wise; both sides
# must collate identically, so pin the locale instead of inheriting the
# invoker's (C vs en_US.UTF-8 order differently and turn real drift into noise).
export LC_ALL=C
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  sed -n '2,10p' "$0"
  exit 0
fi
[[ $# -le 1 ]] || { echo "usage: drift-check.sh [Assembly-CSharp.dll]" >&2; exit 2; }
TOOLS="$(cd "$here/.." && pwd)"
BIN="$TOOLS/bin"
ASM="${1:-$HOME/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll}"
BASELINE_DIR="${BASELINE_DIR:-$HOME/.cache/zdtd-scratch/drift-baseline}"
# Committed baselines for the studied build. A fresh checkout has no
# BASELINE_DIR, so every axis compares against these; the local dir wins as soon
# as it exists, and is seeded from the current build on the first run.
COMMITTED_BASELINE="${COMMITTED_BASELINE:-$TOOLS/../workspace/outputs/baseline}"
# Committed wire snapshot of the studied build. A fresh checkout has no
# BASELINE_DIR, so this is what makes the wire axis comparable on first run
# instead of silently creating a baseline and comparing nothing.
PARITY_BASELINE="${PARITY_BASELINE:-$TOOLS/../workspace/outputs/parity/parity_b10.json}"
CECIL="$BIN/Mono.Cecil.dll"

[[ -f "$ASM" ]]   || { echo "drift: game DLL not found: $ASM" >&2; exit 2; }
[[ -f "$CECIL" ]] || { echo "drift: tools not built; run $TOOLS/build.sh" >&2; exit 2; }

# helper builders (compiled on demand into bin/)
build_helper() { # <name> <src>
  local exe="$BIN/$1.exe"
  [[ -f "$exe" && "$exe" -nt "$2" ]] && return 0
  # A failed helper build must not look like "no drift" on that axis; the run
  # fails closed below instead of comparing a partial surface.
  if ! mcs -nologo -r:"$CECIL" "$2" -out:"$exe"; then
    echo "drift: error: failed to compile $1.exe; refusing to compare an incomplete surface" >&2
    return 1
  fi
}
axis_fail=0
build_helper MethodList "$TOOLS/src/MethodList.cs" || axis_fail=1
# ParitySurface feeds the NetPackage wire diff below; build it like the other
# helpers so a fresh checkout gets the full drift report (not a silent skip).
build_helper ParitySurface "$here/ParitySurface.cs" || axis_fail=1
run() { MONO_PATH="$BIN" mono "$@"; }

mkdir -p "$BASELINE_DIR"
# Snapshot dirs hold whole-assembly surface dumps; the system temp dir is tmpfs
# here, so stage them on disk under the gitignored .scratch/.
SCRATCH="$(cd "$TOOLS/.." && pwd)/.scratch/tmp"
mkdir -p "$SCRATCH"
cur="$(mktemp -d "$SCRATCH/drift.XXXXXX")"
trap 'rm -rf "$cur"' EXIT
# snapshot the current build: census, per-type surface, methods, enums, parity
run "$BIN/Census.exe" "$ASM" > "$cur/census.txt" || {
  echo "drift: error: Census.exe failed; census not compared" >&2
  axis_fail=1
}
run "$BIN/FullSurface.exe" "$ASM" "$cur/surface" >/dev/null || {
  echo "drift: error: FullSurface.exe failed; types not compared" >&2
  axis_fail=1
}
if [[ -f "$BIN/MethodList.exe" ]]; then
  run "$BIN/MethodList.exe" "$ASM" "$cur/methods.txt" || {
    echo "drift: error: MethodList.exe failed; methods not compared" >&2
    axis_fail=1
  }
else
  echo "drift: error: MethodList.exe unavailable; methods not compared" >&2
  axis_fail=1
fi
if [[ -f "$BIN/EnumList.exe" ]]; then
  run "$BIN/EnumList.exe" "$ASM" "$cur/enums.txt" || {
    echo "drift: error: EnumList.exe failed; enums not compared" >&2
    axis_fail=1
  }
else
  echo "drift: error: EnumList.exe unavailable; enums not compared" >&2
  axis_fail=1
fi
# Mono may print "mono_thread_internal_set_priority..." on stdout; keep only JSON.
if [[ -f "$BIN/ParitySurface.exe" ]]; then
  run "$BIN/ParitySurface.exe" "$ASM" 2>/dev/null | sed -n '/^{/,$p' > "$cur/parity.json"
  # Reject empty/non-JSON captures so parity_diff does not throw.
  if ! python3 -m json.tool "$cur/parity.json" >/dev/null 2>&1; then
    echo "drift: error: ParitySurface output is not valid JSON; packages not compared" >&2
    rm -f "$cur/parity.json"
    axis_fail=1
  fi
else
  echo "drift: error: ParitySurface.exe unavailable; packages not compared" >&2
  axis_fail=1
fi

if [[ "$axis_fail" -ne 0 ]]; then
  echo "drift: INCOMPLETE (one or more axes failed)" >&2
  exit 2
fi

# Per-axis baseline: the machine-local dir wins, then the committed one. An axis
# with neither is reported as unmeasured instead of silently passing.
pick_base() { # <relative path> -> path to use, or nothing
  if [[ -f "$BASELINE_DIR/$1" ]]; then printf '%s\n' "$BASELINE_DIR/$1"
  elif [[ -f "$COMMITTED_BASELINE/$1" ]]; then printf '%s\n' "$COMMITTED_BASELINE/$1"; fi
}
base_census="$(pick_base census.txt)"
base_types="$(pick_base surface/surface-types.md)"
base_methods="$(pick_base methods.txt)"
base_enums="$(pick_base enums.txt)"
base_parity="$(pick_base parity.json)"
[[ -n "$base_parity" ]] || base_parity="$PARITY_BASELINE"

echo "drift: baseline local=$BASELINE_DIR"
[[ -n "$base_census" && "$base_census" == "$COMMITTED_BASELINE"/* ]] && \
  echo "drift: using the committed baselines in $COMMITTED_BASELINE (no local one yet)"

drift=0
missing=""
sec() { echo; echo "== $1 =="; }
# Both the axis baselines and the committed wire snapshot count as committed.
note_committed() {
  case "$1" in
    "$COMMITTED_BASELINE"/*|"$PARITY_BASELINE") echo "  (committed baseline)" ;;
  esac
  return 0
}

if [[ -n "$base_census" ]]; then
  sec "census"
  note_committed "$base_census"
  diff "$base_census" "$cur/census.txt" && echo "  (unchanged)" || drift=1
else
  missing="$missing census"
fi

if [[ -n "$base_types" ]]; then
  sec "types (added/removed)"
  note_committed "$base_types"
  tlist() { awk -F'|' 'NR>3{gsub(/ /,"",$2);print $2}' "$1" | grep -vE '\$|<>|__' | sort -u; }
  added=$(comm -13 <(tlist "$base_types") <(tlist "$cur/surface/surface-types.md"))
  removed=$(comm -23 <(tlist "$base_types") <(tlist "$cur/surface/surface-types.md"))
  [[ -n "$added" ]]   && { echo "  ADDED:";   echo "$added"   | awk '{print "    +" $0}'; drift=1; } || echo "  no new types"
  [[ -n "$removed" ]] && { echo "  REMOVED:"; echo "$removed" | awk '{print "    -" $0}'; drift=1; }
else
  missing="$missing types"
fi

if [[ -n "$base_methods" ]]; then
  sec "methods (added/removed on existing+new types)"
  note_committed "$base_methods"
  ma=$(comm -13 <(sort -u "$base_methods") <(sort -u "$cur/methods.txt") | grep -cvE '\$|<>|__|b__|g__' || true)
  mr=$(comm -23 <(sort -u "$base_methods") <(sort -u "$cur/methods.txt") | grep -cvE '\$|<>|__|b__|g__' || true)
  echo "  +$ma methods / -$mr methods"; [[ "$ma" -gt 0 || "$mr" -gt 0 ]] && drift=1
else
  missing="$missing methods"
fi

if [[ -n "$base_enums" ]]; then
  sec "enum members (added/removed)"
  note_committed "$base_enums"
  ea=$(comm -13 <(sort -u "$base_enums") <(sort -u "$cur/enums.txt") | grep -vE '_0000')
  er=$(comm -23 <(sort -u "$base_enums") <(sort -u "$cur/enums.txt") | grep -vE '_0000')
  [[ -n "$ea" ]] && { echo "  ADDED:";   echo "$ea" | awk '{print "    +" $0}'; drift=1; }
  [[ -n "$er" ]] && { echo "  REMOVED:"; echo "$er" | awk '{print "    -" $0}'; drift=1; }
  [[ -z "$ea" && -z "$er" ]] && echo "  (unchanged)"
else
  missing="$missing enums"
fi

if [[ -f "$base_parity" && -f "$cur/parity.json" ]]; then
  sec "NetPackage wire (added/removed/changed)"
  note_committed "$base_parity"
  python3 "$here/parity_diff.py" "$base_parity" "$cur/parity.json" || drift=1
else
  missing="$missing wire"
fi

if [[ -n "$missing" ]]; then
  echo
  echo "drift: no baseline for:$missing (neither $BASELINE_DIR nor $COMMITTED_BASELINE)" >&2
  if [[ ! -f "$BASELINE_DIR/surface/surface-types.md" ]]; then
    cp -r "$cur/." "$BASELINE_DIR/"
    echo "drift: seeded the local baseline at $BASELINE_DIR; those axes compare from the next run" >&2
  fi
  [[ "$drift" -eq 0 ]] && drift=2
fi

echo
if [[ "$drift" -eq 0 ]]; then
  echo "drift: NONE (build matches baseline)"
else
  echo "drift: DETECTED. After review, refresh the baseline that flagged it:"
  echo "  local:     cp -r $cur/. $BASELINE_DIR/"
  echo "  committed: cp <the current file> $COMMITTED_BASELINE/<axis>   # commit with the pin edits"
  echo "Then re-verify affected narratives (see docs/meta/re-methodology.md §5b)."
fi
exit $drift
