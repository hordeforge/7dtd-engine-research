#!/usr/bin/env bash
# Build the RE dumpers in src/*.cs against Mono.Cecil.
# Output: tools/bin/*.exe (run with mono). Requires: mono (mcs), Mono.Cecil.dll.
# Rebuilds are incremental: a target is recompiled only when a source is newer
# than its exe or bin/.toolchain-stamp no longer matches the compiler/Cecil in
# use. The toolchain that produced bin/ is recorded in bin/buildinfo.txt.
# Pass --skip-legacy to compile src/*.cs alone (legacy/ is a best-effort stage).
set -euo pipefail
# Compile and report in a fixed order regardless of the invoker's locale:
# the src/*.cs and legacy/*.cs globs below iterate in collation order, so a
# different LC_COLLATE would build (and log) in a different order.
export LC_ALL=C
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skip_legacy=0
for arg in "$@"; do
  case "$arg" in
    --skip-legacy) skip_legacy=1 ;;
    -h|--help) sed -n '2,/^[^#]/ { /^#/ { s/^#[[:space:]]\{0,1\}//; p; } }' "$0"; exit 0 ;;
    *) echo "build: unknown argument: $arg" >&2; exit 2 ;;
  esac
done
cd "$here"
# Every compiler and monodis run below is wall-clock bound and dies with its
# process group on expiry; a wedged mcs must fail the build, not hang it.
# shellcheck source=tools/bounded-run.sh
. "$here/bounded-run.sh"
# Every compile goes through bin/.staging/<final-name> and is renamed into
# place. The staging path must keep the FINAL basename: mcs derives the
# assembly name and the module MVID from the -out path, so a mktemp name
# (bin/.Xref.exe.AB12cd) leaks into the shipped exe and makes two builds of
# identical sources differ. bin/.staging is inside bin/, so the rename stays a
# same-filesystem atomic move.
mkdir -p bin/.staging

# Compiler prerequisite: mcs ships with the mono development packages; a bare
# mono runtime can run the dumpers but not compile them. Fail once, by name,
# instead of as a confusing per-file compiler-not-found error below.
if ! command -v mcs >/dev/null 2>&1; then
  echo "build: mcs (Mono C# compiler) not on PATH; install a mono development package, e.g.:" >&2
  echo "  sudo apt install mono-mcs   # or mono-devel / mono-complete" >&2
  exit 1
fi

# Integrity gate: compile only against the pinned Mono.Cecil (data/cecil.pin).
# Every dumper links and runs against this dll, so a swapped binary is a
# supply-chain risk; re-pin deliberately via ./cecil-pin.sh <dll> after review.
sha256_of() { # GNU coreutils, falling back to macOS shasum
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1
  else shasum -a 256 "$1" | cut -d' ' -f1; fi
}
pin_sha="$(sed -n 's/^sha256=//p' "$here/data/cecil.pin")"

# Candidates: env override, then vendored, then a previously verified copy in
# bin/, then known local copies, then the distribution's Mono GAC.
candidates=()
if [[ -n "${MONO_CECIL:-}" ]]; then
  candidates=("$MONO_CECIL")
else
  for c in \
    "$here/Mono.Cecil.dll" \
    "$here/bin/Mono.Cecil.dll" \
    "$HOME/.cache/zdtd/Mono.Cecil.dll" \
    /usr/lib/mono/gac/Mono.Cecil/*/Mono.Cecil.dll \
    /usr/local/lib/mono/gac/Mono.Cecil/*/Mono.Cecil.dll; do
    [[ -f "$c" ]] && candidates+=("$c")
  done
fi
if (( ${#candidates[@]} == 0 )); then
  echo "Mono.Cecil.dll not found. Set MONO_CECIL=/path/to/Mono.Cecil.dll, or restore it via:" >&2
  echo "  install your distribution's Mono.Cecil package, or use dotnet add package Mono.Cecil" >&2
  echo "  (then point MONO_CECIL at the restored dll)" >&2
  exit 1
fi

# Prefer whichever candidate matches the pin: a distro GAC rebuild has the same
# assembly version but different bytes, and must not shadow the reviewed copy.
cecil=""
for c in "${candidates[@]}"; do
  [[ "$(sha256_of "$c")" == "$pin_sha" ]] && { cecil="$c"; break; }
done
if [[ -z "$cecil" ]]; then
  cecil="${candidates[0]}"
  if [[ "${MONO_CECIL_UNVERIFIED:-0}" == "1" ]]; then
    echo "WARNING: no Mono.Cecil matches the pin, building UNVERIFIED (MONO_CECIL_UNVERIFIED=1)" >&2
  else
    echo "No Mono.Cecil.dll matches the integrity pin (data/cecil.pin):" >&2
    echo "  want $pin_sha" >&2
    for c in "${candidates[@]}"; do echo "  got  $(sha256_of "$c")  $c" >&2; done
    echo "Re-pin after reviewing the dll you intend to use:" >&2
    echo "  ./cecil-pin.sh \"${candidates[0]}\"" >&2
    exit 1
  fi
fi
if [[ ! -s bin/Mono.Cecil.dll ]] || ! cmp -s "$cecil" bin/Mono.Cecil.dll; then
  # Stage and rename: a concurrent `make census` or drift-check must not load a
  # half-copied assembly, which reads as "cannot open assembly" rather than as
  # the build race it is.
  staged_cecil="bin/.staging/Mono.Cecil.dll"
  if cp -f "$cecil" "$staged_cecil"; then
    mv -f "$staged_cecil" bin/Mono.Cecil.dll
  else
    rm -f "$staged_cecil"
    exit 1
  fi
fi
cecil_ver="unknown"
if command -v monodis >/dev/null 2>&1; then
  # No early `exit` in the awk: monodis keeps writing after the Version line, and
  # an awk that exits there SIGPIPEs it, which pipefail turns into a spurious
  # build failure.
  cecil_ver="$(run_bounded monodis --assembly bin/Mono.Cecil.dll 2>/dev/null | awk '/^Version:/ && !seen {v=$2; seen=1} END {print v}')"
  [[ -n "$cecil_ver" ]] || cecil_ver="unknown"
  echo "using Mono.Cecil $cecil_ver: $cecil"
else
  echo "using Mono.Cecil: $cecil"
fi

# Toolchain record. Mono.Cecil is pinned by digest; the compiler is not (it is a
# host package), so stamp what produced bin/ and force a full rebuild whenever
# the compiler or the pinned Cecil changes. Without this a toolchain upgrade
# silently leaves every exe from the previous compiler in place.
mcs_ver="$(run_bounded mcs --version 2>/dev/null | sed -n '1s/.*version \([0-9][0-9.]*\).*/\1/p')"
[[ -n "$mcs_ver" ]] || mcs_ver="unknown"
mono_ver="unknown"
if command -v mono >/dev/null 2>&1; then
  # "Mono JIT compiler version 6.12.0.123 (2024-02)": take the dotted version,
  # not the trailing date field.
  mono_ver="$(run_bounded mono --version 2>/dev/null | sed -n '1s/.*version \([0-9][0-9.]*\).*/\1/p')"
  [[ -n "$mono_ver" ]] || mono_ver="unknown"
fi
stamp_file="bin/.toolchain-stamp"
# The digest of the assembly actually linked in, not the pin: an
# MONO_CECIL_UNVERIFIED=1 build links something the pin does not name, and a
# stamp that claims otherwise both hides the swap and lets the next run treat
# exes built against the other dll as current.
cecil_actual_sha="$(sha256_of bin/Mono.Cecil.dll)"
stamp_now="mcs=$mcs_ver mono=$mono_ver cecil=$cecil_ver cecil_sha256=$cecil_actual_sha"
# Compared by content, not mtime: the stamp is rewritten at the end of every
# successful run, and a run that rebuilt one target must not mark the exes it
# did not touch as stale. A mismatch (new compiler, re-pinned Cecil, missing
# stamp after a failed run) rebuilds everything.
force_rebuild=0
if [[ "$(cat "$stamp_file" 2>/dev/null || true)" != "$stamp_now" ]]; then
  force_rebuild=1
fi

# A target is stale unless its exe exists and is newer than every input. The
# toolchain dimension is covered by force_rebuild, not here.
up_to_date() { # <exe> <input>...
  [[ "$force_rebuild" -eq 0 ]] || return 1
  local exe="$1"
  [[ -f "$exe" ]] || return 1
  shift
  local input
  for input in "$@"; do
    [[ "$exe" -nt "$input" ]] || return 1
  done
  return 0
}

# Primary tools (src/): general, maintained. IlFmt.cs (IL formatting),
# Seeds.cs (reachability seeds shared by Coverage/Reach) and AsmWalk.cs
# (assembly-walk helpers shared by the scanners) are compiled into every src/
# dumper. StockFacts/MethodList/ParitySurface are ALSO compiled standalone by
# stock-sync.sh / drift-check.sh, so those three must stay free of the shared files.
shared=("src/IlFmt.cs" "src/Seeds.cs" "src/AsmWalk.cs")
for f in src/*.cs; do
  [[ " ${shared[*]} " == *" $f "* ]] && continue
  name="$(basename "$f" .cs)"
  if up_to_date "bin/$name.exe" "$f" "${shared[@]}" bin/Mono.Cecil.dll; then
    echo "up to date bin/$name.exe"
    continue
  fi
  # src/ is the maintained surface: a compile failure here must stop the build,
  # otherwise tests keep running against a stale exe that predates the breakage.
  # -warn:4 -warnaserror: the tree compiles warning-clean at max severity; keep
  # it that way (new warnings fail the build instead of scrolling past).
  # Compiling under the final basename in bin/.staging and renaming into place
  # keeps a concurrent build or gate from loading a half-written exe, leaves the
  # previous one intact when the compile fails, and keeps the assembly name and
  # MVID identical across rebuilds.
  staged="bin/.staging/$name.exe"
  rm -f "$staged"
  if ! out="$(run_bounded mcs -nologo -warn:4 -warnaserror -pathmap:"$here=." -r:bin/Mono.Cecil.dll "$f" "${shared[@]}" -out:"$staged" 2>&1)"; then
    [[ -n "$out" ]] && printf '%s\n' "$out" >&2
    rm -f "$staged"
    echo "build: FAILED bin/$name.exe (compiler output above)" >&2
    exit 1
  fi
  mv -f "$staged" "bin/$name.exe"
  [[ -n "$out" ]] && printf '%s\n' "$out"
  echo "built bin/$name.exe"
done

# Legacy per-family dumpers (legacy/): archival, superseded by src/. Each compiles
# to its own exe (class names collide across files, so never combined). Best-effort:
# some legacy sources predate this mcs and may not rebuild; failures are reported,
# not fatal. Pass --skip-legacy to skip this stage.
if [[ "$skip_legacy" -eq 0 && -d legacy ]]; then
  mkdir -p bin/legacy
  # Drop exes whose source is gone: a stale bin/legacy/*.exe from a deleted
  # dumper would otherwise stay runnable and look supported.
  for exe in bin/legacy/*.exe; do
    [[ -e "$exe" ]] || continue
    name="$(basename "$exe" .exe)"
    [[ -f "legacy/$name.cs" ]] || { rm -f "$exe"; echo "legacy: removed stale bin/legacy/$name.exe (no legacy/$name.cs)"; }
  done
  ok=0; fail=0; failed=""
  for f in legacy/*.cs; do
    name="$(basename "$f" .cs)"
    if up_to_date "bin/legacy/$name.exe" "$f" bin/Mono.Cecil.dll; then
      ok=$((ok+1))
      continue
    fi
    if staged="bin/.staging/$name.exe" && rm -f "$staged" &&
      run_bounded mcs -nologo -pathmap:"$here=." -r:bin/Mono.Cecil.dll "$f" -out:"$staged" >/dev/null 2>&1; then
      mv -f "$staged" "bin/legacy/$name.exe"
      ok=$((ok+1))
    else
      rm -f "$staged"
      fail=$((fail+1)); failed="$failed $name"
    fi
  done
  # ok counts up-to-date targets as well as freshly compiled ones, so the line
  # reads "current", not "built".
  echo "legacy: $ok current, $fail need repair:${failed:- none}"
fi

# Recorded last, and only because every stage above succeeded: a failed build
# must leave the old stamp in place so the next run rebuilds rather than
# trusting exes from the previous toolchain.
printf '%s\n' "$stamp_now" > "$stamp_file"
{
  echo "# toolchain that produced tools/bin (regenerable: rerun tools/build.sh)"
  echo "mcs=$mcs_ver"
  echo "mono=$mono_ver"
  echo "monocecil_version=$cecil_ver"
  echo "monocecil_sha256=$cecil_actual_sha"
  echo "monocecil_pinned_sha256=$pin_sha"
  echo "# byte-identical across rebuilds: the output basename, not the mktemp"
  echo "# name, and the source paths are mapped out (-pathmap); mcs has no"
  echo "# -deterministic, so do not reintroduce a random -out basename."
  echo "deterministic=yes"
} > bin/buildinfo.txt
echo "done. run e.g.:  mono bin/Census.exe \"\$ASM\""
