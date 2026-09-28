#!/usr/bin/env bash
# Patch-drift check: compare the current game build against a stored baseline and
# report what changed (types, methods, enum members, NetPackage wire). Run after a
# game update; exits 1 if drift is detected (for cron/CI alerting), and fails
# closed with exit 2 if any axis cannot be measured (no partial comparison).
#
#   drift-check.sh [ASM]           # ASM defaults to the discovered dedicated DLL
#                                  # (SEVENDTD_ASM/SEVENDTD_DS_DIR, Steam roots)
#   BASELINE_DIR=... drift-check.sh
#   COMMITTED_BASELINE=... drift-check.sh  # where the shipped baseline lives
#   PARITY_BASELINE=... drift-check.sh   # committed wire snapshot (default below)
#   drift-check.sh --accept-baseline      # make the current build the local baseline
#
# Every axis has a committed baseline in workspace/outputs/baseline/ (and the
# wire axis one in workspace/outputs/parity/), so a fresh checkout gets a real
# drift verdict on the first run instead of "baseline created". The machine-local
# BASELINE_DIR takes precedence once it exists, and only while it carries the
# digest of the DLL it was taken from (see "local baseline provenance" below).
# Requires: mono (mcs), Mono.Cecil, the tools built (../build.sh).
set -uo pipefail
# sort/comm below compare baseline vs current listings byte-wise; both sides
# must collate identically, so pin the locale instead of inheriting the
# invoker's (C vs en_US.UTF-8 order differently and turn real drift into noise).
export LC_ALL=C
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  sed -n '2,/^[^#]/ { /^#/ { s/^#[[:space:]]\{0,1\}//; p; } }' "$0"
  exit 0
fi
accept=0
asm_arg=""
for arg in "$@"; do
  case "$arg" in
    --accept-baseline) accept=1 ;;
    -*) echo "usage: drift-check.sh [Assembly-CSharp.dll] [--accept-baseline]" >&2; exit 2 ;;
    *) [[ -z "$asm_arg" ]] || { echo "usage: drift-check.sh [Assembly-CSharp.dll] [--accept-baseline]" >&2; exit 2; }
       asm_arg="$arg" ;;
  esac
done
TOOLS="$(cd "$here/.." && pwd)"
ROOT="$(cd "$TOOLS/.." && pwd)"
BIN="$TOOLS/bin"
ASM="${asm_arg:-$(python3 "$TOOLS/asm_path.py")}"
BASELINE_DIR="${BASELINE_DIR:-$HOME/.cache/zdtd-scratch/drift-baseline}"
# Committed baselines for the studied build. A fresh checkout has no
# BASELINE_DIR, so every axis compares against these; the local dir wins as soon
# as it holds a snapshot of THIS build, and is seeded from the current build on
# the first run.
COMMITTED_BASELINE="${COMMITTED_BASELINE:-$ROOT/workspace/outputs/baseline}"
# Committed wire snapshot of the studied build. A fresh checkout has no
# BASELINE_DIR, so this is what makes the wire axis comparable on first run
# instead of silently creating a baseline and comparing nothing.
PARITY_BASELINE="${PARITY_BASELINE:-$ROOT/workspace/outputs/parity/parity_b10.json}"
CECIL="$BIN/Mono.Cecil.dll"
# Wall-clock bound on the helper builds and the snapshot runs below
# (tools/bounded-run.sh).
# shellcheck source=tools/bounded-run.sh
. "$TOOLS/bounded-run.sh"
# Digest of the DLL the local baseline was taken from. It is the cache key for
# that baseline: a snapshot of another build answers a different question.
BASELINE_STAMP="$BASELINE_DIR/source.sha256"

if [[ -z "$ASM" ]]; then
  echo "drift: no dedicated server found; install it, pass the DLL, or set ASM/SEVENDTD_ASM/SEVENDTD_DS_DIR" >&2
  exit 2
fi
[[ -f "$ASM" ]]   || { echo "drift: game DLL not found: $ASM" >&2; exit 2; }
[[ -f "$CECIL" ]] || { echo "drift: tools not built; run $TOOLS/build.sh" >&2; exit 2; }

# sha256 of a file, or nothing when the host has neither digest tool.
file_digest() { # <path> -> hex digest on stdout, empty when uncomputable
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | cut -d' ' -f1
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | cut -d' ' -f1
  fi
}
ASM_DIGEST="$(file_digest "$ASM")"

# helper builders (compiled on demand into bin/)
build_helper() { # <name> <src>
  local exe="$BIN/$1.exe"
  # Freshness is the cache key: the helper is reused only while it is newer than
  # BOTH its source and the Mono.Cecil it was compiled against. Keying on the
  # source alone kept a helper built against an older cecil.dll in place, and it
  # then ran against an assembly it was not compiled for.
  [[ -f "$exe" && "$exe" -nt "$2" && "$exe" -nt "$CECIL" ]] && return 0
  # A failed helper build must not look like "no drift" on that axis; the run
  # fails closed below instead of comparing a partial surface. The compile lands
  # on a private staging copy and is renamed into place, so a concurrent
  # drift-check or `make census` never loads a half-written assembly. The
  # staging name is the FINAL one: mcs takes the assembly name and module MVID
  # from the -out path, so a mktemp name leaks into the exe and breaks
  # byte-identical rebuilds.
  local staged
  staged="$BIN/.staging/$1.exe"
  mkdir -p "$BIN/.staging"
  rm -f "$staged"
  if ! run_bounded mcs -nologo -pathmap:"$TOOLS=." -r:"$CECIL" "$2" -out:"$staged"; then
    rm -f "$staged"
    echo "drift: error: failed to compile $1.exe; refusing to compare an incomplete surface" >&2
    return 1
  fi
  mv -f "$staged" "$exe"
}
axis_fail=0
build_helper MethodList "$TOOLS/src/MethodList.cs" || axis_fail=1
# ParitySurface feeds the NetPackage wire diff below; build it like the other
# helpers so a fresh checkout gets the full drift report (not a silent skip).
build_helper ParitySurface "$here/ParitySurface.cs" || axis_fail=1
# Wall-clock bound on every snapshot tool below (tools/bounded-run.sh); a
# wedged Cecil walk must fail the axis, not hang the whole drift check.
run() { MONO_PATH="$BIN" run_bounded mono "$@"; }

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

# local baseline provenance
# The local baseline is a cache of the last reviewed snapshot and it outranks the
# committed one, so it is only a valid comparison target while it was taken from
# the DLL in hand. Nothing recorded that: after a patch the local snapshot
# silently won, and every axis reported patch-to-patch changes instead of drift
# from the studied pin the corpus cites. The digest of the source DLL is the
# cache key; a baseline whose stamp names another build (or names no build at
# all) is not used, and the committed baseline answers until it is re-accepted.
local_usable=0
local_present=0
[[ -n "$(ls -A "$BASELINE_DIR" 2>/dev/null)" ]] && local_present=1
if [[ -z "$ASM_DIGEST" ]]; then
  echo "drift: warning: no sha256 tool (sha256sum/shasum); the local baseline at $BASELINE_DIR cannot be provenance-checked" >&2
  local_usable=1
elif [[ -f "$BASELINE_STAMP" ]]; then
  stamp_digest="$(tr -d '[:space:]' < "$BASELINE_STAMP")"
  if [[ "$stamp_digest" == "$ASM_DIGEST" ]]; then
    local_usable=1
  else
    echo "drift: ignoring the local baseline at $BASELINE_DIR: it was taken from another build (${stamp_digest:0:12} != ${ASM_DIGEST:0:12})" >&2
    echo "drift: comparing against the committed baselines instead; re-accept this build with: drift-check.sh --accept-baseline" >&2
  fi
elif [[ "$local_present" -eq 1 ]]; then
  echo "drift: ignoring the unstamped local baseline at $BASELINE_DIR: which build it was taken from is unknown" >&2
  echo "drift: comparing against the committed baselines instead; re-accept this build with: drift-check.sh --accept-baseline" >&2
fi

# Replace the local baseline with the current snapshot, re-stamped with the
# source digest. The copy is staged beside the dir and the two are swapped by
# rename, so the dir only ever holds a complete snapshot of one build. Merging
# into the old dir would leave files from a different build sitting in the dir
# the next run treats as this build's; emptying it in place would instead leave
# a window where a concurrent run (cron vs `make post-update`) sees a half-copied
# baseline under a stamp that still names this build, and reports its verdict
# against it. The swap leaves one window where the dir is absent, and an absent
# baseline is the case every reader already falls back to the committed one for.
reset_baseline() {
  local staged="$BASELINE_DIR.staged.$$" retired="$BASELINE_DIR.retired.$$"
  rm -rf "$staged" "$retired"
  mkdir -p "$staged"
  cp -R "$cur/." "$staged/"
  [[ -n "$ASM_DIGEST" ]] && printf '%s\n' "$ASM_DIGEST" > "$staged/source.sha256"
  if [[ -d "$BASELINE_DIR" ]]; then mv "$BASELINE_DIR" "$retired"; fi
  if ! mv "$staged" "$BASELINE_DIR"; then
    # The old snapshot goes back rather than leaving no baseline at all.
    [[ -d "$retired" ]] && mv "$retired" "$BASELINE_DIR"
    return 1
  fi
  rm -rf "$retired"
}

if [[ "$accept" -eq 1 ]]; then
  # --accept-baseline replaces the dir it is pointed at; a root or empty
  # BASELINE_DIR would take the whole filesystem with it.
  case "$BASELINE_DIR" in
    /|"") echo "drift: refusing to --accept-baseline into BASELINE_DIR='$BASELINE_DIR'" >&2; exit 2 ;;
  esac
  if ! reset_baseline; then
    echo "drift: error: could not replace the local baseline at $BASELINE_DIR" >&2
    exit 2
  fi
  echo "drift: local baseline at $BASELINE_DIR is now the current build"
  exit 0
fi

# Per-axis baseline: the machine-local dir wins, then the committed one. An axis
# with neither is reported as unmeasured instead of silently passing.
pick_base() { # <relative path> -> path to use, or nothing
  if [[ "$local_usable" -eq 1 && -f "$BASELINE_DIR/$1" ]]; then printf '%s\n' "$BASELINE_DIR/$1"
  elif [[ -f "$COMMITTED_BASELINE/$1" ]]; then printf '%s\n' "$COMMITTED_BASELINE/$1"; fi
}
base_census="$(pick_base census.txt)"
base_types="$(pick_base surface/surface-types.md)"
base_methods="$(pick_base methods.txt)"
base_enums="$(pick_base enums.txt)"
base_parity="$(pick_base parity.json)"
[[ -n "$base_parity" ]] || base_parity="$PARITY_BASELINE"

echo "drift: baseline local=$BASELINE_DIR"
if [[ "$local_usable" -eq 0 && "$local_present" -eq 1 && -n "$base_census" && "$base_census" == "$COMMITTED_BASELINE"/* ]]; then
  echo "drift: using the committed baselines in $COMMITTED_BASELINE (the local one is not this build's)"
elif [[ -n "$base_census" && "$base_census" == "$COMMITTED_BASELINE"/* ]]; then
  echo "drift: using the committed baselines in $COMMITTED_BASELINE (no local one yet)"
fi

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
  if [[ "$local_usable" -eq 0 || ! -f "$BASELINE_DIR/surface/surface-types.md" ]]; then
    reset_baseline
    echo "drift: seeded the local baseline at $BASELINE_DIR; those axes compare from the next run" >&2
  fi
  [[ "$drift" -eq 0 ]] && drift=2
fi

echo
if [[ "$drift" -eq 0 ]]; then
  echo "drift: NONE (build matches baseline)"
else
  echo "drift: DETECTED. After review, refresh the baseline that flagged it:"
  echo "  local:     drift-check.sh --accept-baseline   # re-stamps $BASELINE_DIR with this build"
  echo "  committed: cp <the current file> $COMMITTED_BASELINE/<axis>   # commit with the pin edits"
  echo "Then re-verify affected narratives (see docs/meta/re-methodology.md §5b)."
fi
exit $drift
