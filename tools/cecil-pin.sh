#!/usr/bin/env bash
# Re-pin tools/data/cecil.pin to a reviewed Mono.Cecil.dll.
# Run after deliberately upgrading Mono.Cecil (e.g. restored via
# `dotnet add package Mono.Cecil` at a new version). Review the source of the
# dll first: everything in tools/src compiles and runs against it.
#
# Usage: ./cecil-pin.sh /path/to/Mono.Cecil.dll
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dll="${1:?usage: cecil-pin.sh /path/to/Mono.Cecil.dll}"
[[ -f "$dll" ]] || { echo "cecil-pin: not found: $dll" >&2; exit 2; }
if command -v sha256sum >/dev/null 2>&1; then
  hash="$(sha256sum "$dll" | cut -d' ' -f1)"
else
  hash="$(shasum -a 256 "$dll" | cut -d' ' -f1)"
fi
ver="unknown"
if command -v monodis >/dev/null 2>&1; then
  ver="$(monodis --assembly "$dll" 2>/dev/null | awk '/^Version:/{print $2; exit}')"
fi

tmp="$(mktemp "$here/data/.cecil.pin.XXXXXX")"
trap 'rm -f "$tmp"' EXIT
cat > "$tmp" <<EOF
# Integrity pin for Mono.Cecil.dll, the only third-party dependency of this
# repo's RE tooling (compiled against by tools/build.sh, never redistributed).
# build.sh refuses a candidate whose SHA-256 differs; re-pin deliberately:
#   tools/cecil-pin.sh /path/to/Mono.Cecil.dll
version=$ver
sha256=$hash
EOF
mv "$tmp" "$here/data/cecil.pin"
trap - EXIT
echo "cecil-pin: pinned Mono.Cecil $ver ($hash) -> data/cecil.pin"
echo "cecil-pin: commit data/cecil.pin with the upgrade."
