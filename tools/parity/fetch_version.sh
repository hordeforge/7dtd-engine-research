#!/usr/bin/env bash
# Download a specific 7DTD Dedicated Server build via steamcmd and extract its
# parity surface, for diffing against another version. App 294420 (dedicated).
#
# Usage:
#   fetch_version.sh <branch|manifestid> [label]
# Examples:
#   fetch_version.sh public              # current stable
#   fetch_version.sh latest_experimental # exp branch
#   fetch_version.sh 1234567890123 v3.0  # a pinned depot manifest
#
# Produces: <OUT>/parity_<label>.json  (ParitySurface snapshot)
# steamcmd is installed to ~/.cache/zdtd-scratch/steamcmd if absent.
set -euo pipefail

BRANCH="${1:?usage: fetch_version.sh <branch|manifestid> [label]}"
LABEL="${2:-$BRANCH}"
APP=294420
DEPOT=294422 # dedicated server content depot
SCRATCH="${SCRATCH:-$HOME/.cache/zdtd-scratch}"
STEAMCMD="$SCRATCH/steamcmd"
INSTALL="$SCRATCH/sdtd_$LABEL"
OUT="${OUT:-$SCRATCH}"
SCRIPTDIR="$(cd "$(dirname "$0")" && pwd)"
CECIL="$SCRATCH/Mono.Cecil.dll"

# 1) steamcmd bootstrap (no host pollution; lives under scratch)
if [[ ! -x "$STEAMCMD/steamcmd.sh" ]]; then
  echo "[parity] installing steamcmd → $STEAMCMD"
  mkdir -p "$STEAMCMD"
  curl -sSL https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz \
    | tar -xz -C "$STEAMCMD"
fi

# 2) download the build (anonymous login works for dedicated server)
mkdir -p "$INSTALL"
if [[ "$BRANCH" =~ ^[0-9]{6,}$ ]]; then
  # pinned manifest: needs download_depot form
  "$STEAMCMD/steamcmd.sh" +login anonymous \
    +download_depot "$APP" "$DEPOT" "$BRANCH" +quit
  # steamcmd drops it under steamapps/content; copy DLL out
  SRC=$(find "$STEAMCMD/linux32/steamapps/content/app_$APP/depot_$DEPOT" \
        -name Assembly-CSharp.dll 2>/dev/null | head -1)
  cp -f "$SRC" "$INSTALL/Assembly-CSharp.dll"
else
  "$STEAMCMD/steamcmd.sh" +force_install_dir "$INSTALL" +login anonymous \
    +app_update "$APP" -beta "$BRANCH" validate +quit
fi

# 3) locate the DLL + extract the parity surface
DLL=$(find "$INSTALL" -name Assembly-CSharp.dll | head -1)
if [[ -z "$DLL" ]]; then echo "[parity] DLL not found in $INSTALL"; exit 1; fi
if [[ ! -f "$SCRATCH/ParitySurface.exe" ]]; then
  mcs -r:"$CECIL" "$SCRIPTDIR/ParitySurface.cs" -out:"$SCRATCH/ParitySurface.exe"
fi
mono "$SCRATCH/ParitySurface.exe" "$DLL" > "$OUT/parity_$LABEL.json"
echo "[parity] wrote $OUT/parity_$LABEL.json ($(wc -l < "$OUT/parity_$LABEL.json") lines)"
echo "[parity] diff:  python3 $SCRIPTDIR/parity_diff.py <old.json> $OUT/parity_$LABEL.json"
