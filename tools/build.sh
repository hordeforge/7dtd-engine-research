#!/usr/bin/env bash
# Build the RE dumpers in src/*.cs against Mono.Cecil.
# Output: tools/bin/*.exe (run with mono). Requires: mono (mcs), Mono.Cecil.dll.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$here"
mkdir -p bin

# Locate Mono.Cecil.dll: env override, then vendored, then known local copies,
# then a previous verified copy in bin/ (re-checked by the pin gate below).
cecil="${MONO_CECIL:-}"
if [[ -z "$cecil" ]]; then
  for c in \
    "$here/Mono.Cecil.dll" \
    "$here/bin/Mono.Cecil.dll" \
    "$HOME/.cache/zdtd/Mono.Cecil.dll" \
    "$HOME/Desktop/7dtd/7dtd-realworld/tools/network_protocol_inspector/bin/Release/net8.0/Mono.Cecil.dll" \
    "$HOME/Desktop/7dtd/7dtd-research/il/zdtd_re_tools/Mono.Cecil.dll" \
    /usr/lib/mono/gac/Mono.Cecil/*/Mono.Cecil.dll \
    /usr/local/lib/mono/gac/Mono.Cecil/*/Mono.Cecil.dll; do
    [[ -f "$c" ]] && cecil="$c" && break
  done
fi
if [[ -z "$cecil" || ! -f "$cecil" ]]; then
  echo "Mono.Cecil.dll not found. Set MONO_CECIL=/path/to/Mono.Cecil.dll, or restore it via:" >&2
  echo "  install your distribution's Mono.Cecil package, or use dotnet add package Mono.Cecil" >&2
  echo "  (then point MONO_CECIL at the restored dll)" >&2
  exit 1
fi

# Integrity gate: compile only against the pinned Mono.Cecil (data/cecil.pin).
# Every dumper links and runs against this dll, so a swapped binary is a
# supply-chain risk; re-pin deliberately via ./cecil-pin.sh <dll> after review.
sha256_of() { # GNU coreutils, falling back to macOS perl shasum
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1
  else shasum -a 256 "$1" | cut -d' ' -f1; fi
}
pin_sha="$(sed -n 's/^sha256=//p' "$here/data/cecil.pin")"
got_sha="$(sha256_of "$cecil")"
if [[ "$got_sha" != "$pin_sha" ]]; then
  if [[ "${MONO_CECIL_UNVERIFIED:-0}" == "1" ]]; then
    echo "WARNING: Mono.Cecil hash mismatch, building UNVERIFIED (MONO_CECIL_UNVERIFIED=1)" >&2
  else
    echo "Mono.Cecil.dll failed the integrity pin (data/cecil.pin):" >&2
    echo "  want $pin_sha" >&2
    echo "  got  $got_sha" >&2
    echo "  at   $cecil" >&2
    echo "Re-pin after reviewing the new dll: ./cecil-pin.sh \"$cecil\"" >&2
    exit 1
  fi
fi
if [[ ! -s bin/Mono.Cecil.dll ]] || ! cmp -s "$cecil" bin/Mono.Cecil.dll; then
  cp -f "$cecil" bin/Mono.Cecil.dll
fi
if command -v monodis >/dev/null 2>&1; then
  ver="$(monodis --assembly bin/Mono.Cecil.dll 2>/dev/null | awk '/^Version:/{print $2; exit}')"
  echo "using Mono.Cecil $ver: $cecil"
else
  echo "using Mono.Cecil: $cecil"
fi

# Primary tools (src/): general, maintained. IlFmt.cs (IL formatting) and
# Seeds.cs (reachability seeds shared by Coverage/Reach) are compiled into
# every src/ dumper.
shared=("src/IlFmt.cs" "src/Seeds.cs")
for f in src/*.cs; do
  [[ " ${shared[*]} " == *" $f "* ]] && continue
  name="$(basename "$f" .cs)"
  mcs -nologo -r:bin/Mono.Cecil.dll "$f" "${shared[@]}" -out:"bin/$name.exe" 2>&1 | grep -v '^$' || true
  echo "built bin/$name.exe"
done

# Legacy per-family dumpers (legacy/): archival, superseded by src/. Each compiles
# to its own exe (class names collide across files, so never combined). Best-effort:
# some legacy sources predate this mcs and may not rebuild; failures are reported,
# not fatal. Pass --skip-legacy to skip this stage.
if [[ "${1:-}" != "--skip-legacy" && -d legacy ]]; then
  mkdir -p bin/legacy
  ok=0; fail=0; failed=""
  for f in legacy/*.cs; do
    name="$(basename "$f" .cs)"
    if mcs -nologo -r:bin/Mono.Cecil.dll "$f" -out:"bin/legacy/$name.exe" >/dev/null 2>&1; then
      ok=$((ok+1))
    else
      fail=$((fail+1)); failed="$failed $name"
    fi
  done
  echo "legacy: $ok built, $fail need repair:${failed:- none}"
fi
echo "done. run e.g.:  mono bin/Census.exe \"\$ASM\""
