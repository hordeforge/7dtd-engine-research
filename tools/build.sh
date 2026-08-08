#!/usr/bin/env bash
# Build the RE dumpers in src/*.cs against Mono.Cecil.
# Output: tools/bin/*.exe (run with mono). Requires: mono (mcs), Mono.Cecil.dll.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$here"
mkdir -p bin

# Locate Mono.Cecil.dll: env override, then vendored, then known local copies.
cecil="${MONO_CECIL:-}"
if [[ -z "$cecil" ]]; then
  for c in \
    "$here/Mono.Cecil.dll" \
    "$HOME/.cache/zdtd/Mono.Cecil.dll" \
    "$HOME/Desktop/7dtd/7days-realworld/tools/network_protocol_inspector/bin/Release/net8.0/Mono.Cecil.dll" \
    "$HOME/Desktop/7dtd/7dtd-research/il/zdtd_re_tools/Mono.Cecil.dll"; do
    [[ -f "$c" ]] && cecil="$c" && break
  done
fi
if [[ -z "$cecil" || ! -f "$cecil" ]]; then
  echo "Mono.Cecil.dll not found. Set MONO_CECIL=/path/to/Mono.Cecil.dll, or restore it via:" >&2
  echo "  dotnet add package Mono.Cecil  (then point MONO_CECIL at the restored dll)" >&2
  exit 1
fi
cp -f "$cecil" bin/Mono.Cecil.dll
echo "using Mono.Cecil: $cecil"

# Primary tools (src/): general, maintained. IlFmt.cs is a shared helper compiled
# into each dumper that references it.
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
