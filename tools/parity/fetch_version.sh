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
# Requires SteamCMD installed by the operator (`STEAMCMD=/path/to/steamcmd.sh`).
set -euo pipefail

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  sed -n '2,11p' "$0"
  exit 0
fi
[[ $# -le 2 ]] || { echo "usage: fetch_version.sh <branch|manifestid> [label]" >&2; exit 2; }
BRANCH="${1:?usage: fetch_version.sh <branch|manifestid> [label]}"
LABEL="${2:-$BRANCH}"
[[ "$LABEL" =~ ^[A-Za-z0-9._-]+$ ]] || {
  echo "[parity] invalid label (allowed: letters, digits, dot, underscore, hyphen): $LABEL" >&2
  exit 2
}
APP=294420
DEPOT=294422 # dedicated server content depot
SCRATCH="${SCRATCH:-$HOME/.cache/zdtd-scratch}"
INSTALL="$SCRATCH/sdtd_$LABEL"
OUT="${OUT:-$SCRATCH}"
SCRIPTDIR="$(cd "$(dirname "$0")" && pwd)"
TOOLS="$(cd "$SCRIPTDIR/.." && pwd)"
BIN="$TOOLS/bin"
CECIL="$BIN/Mono.Cecil.dll"
PARITY_EXE="$BIN/ParitySurface.exe"

# 1) Resolve an operator-installed SteamCMD. Do not download and execute tools
# inside a research script; package installation and provenance are external.
if [[ -n "${STEAMCMD:-}" ]]; then
  STEAMCMD_BIN="$STEAMCMD"
elif command -v steamcmd >/dev/null 2>&1; then
  STEAMCMD_BIN="$(command -v steamcmd)"
elif [[ -x "$SCRATCH/steamcmd/steamcmd.sh" ]]; then
  STEAMCMD_BIN="$SCRATCH/steamcmd/steamcmd.sh"
else
  echo "[parity] steamcmd not found; install it or set STEAMCMD=/path/to/steamcmd.sh" >&2
  exit 2
fi
[[ -x "$STEAMCMD_BIN" ]] || { echo "[parity] not executable: $STEAMCMD_BIN" >&2; exit 2; }

# 2) download the build (anonymous login works for dedicated server)
mkdir -p "$INSTALL"
if [[ "$BRANCH" =~ ^[0-9]{6,}$ ]]; then
  # pinned manifest: needs download_depot form
  # An unpublished manifest, or one from another app, makes steamcmd exit
  # non-zero; without this the script died with steamcmd's raw code (14) instead
  # of saying what failed. The message names the ids and the likely causes.
  if ! "$STEAMCMD_BIN" +login anonymous \
      +download_depot "$APP" "$DEPOT" "$BRANCH" +quit; then
    echo "[parity] steamcmd could not download depot manifest $BRANCH (app $APP depot $DEPOT):" >&2
    echo "  an unpublished or other-app manifest id fails here, and a retired build may be gone." >&2
    echo "  list published ids with tools/parity/steam_builds.py --json." >&2
    exit 1
  fi
  # steamcmd drops it under steamapps/content; copy DLL out
  # -print -quit: stop at the first hit; piping a full depot walk into head
  # would SIGPIPE find and pipefail+set -e would abort before the error check.
  # || true: a missing depot dir must reach the friendly message, not die silently.
  STEAM_CONTENT="${STEAM_CONTENT:-$(dirname "$STEAMCMD_BIN")/steamapps/content}"
  SRC="$(find "$STEAM_CONTENT/app_$APP/depot_$DEPOT" \
        -name Assembly-CSharp.dll -print -quit 2>/dev/null || true)"
  if [[ -z "$SRC" ]]; then
    echo "[parity] no Assembly-CSharp.dll from depot manifest $BRANCH under $STEAM_CONTENT (set STEAM_CONTENT if SteamCMD uses another root)" >&2
    exit 1
  fi
  cp -f "$SRC" "$INSTALL/Assembly-CSharp.dll"
else
  if ! "$STEAMCMD_BIN" +force_install_dir "$INSTALL" +login anonymous \
      +app_update "$APP" -beta "$BRANCH" validate +quit; then
    echo "[parity] steamcmd could not install branch $BRANCH (app $APP):" >&2
    echo "  a password-gated or misspelled beta branch fails here; check the branch name" >&2
    echo "  against tools/parity/steam_builds.py output." >&2
    exit 1
  fi
fi

# 3) locate the DLL + extract the parity surface
DLL="$(find "$INSTALL" -name Assembly-CSharp.dll -print -quit || true)"
if [[ -z "$DLL" ]]; then echo "[parity] DLL not found in $INSTALL"; exit 1; fi
if [[ ! -f "$CECIL" ]]; then
  "$TOOLS/build.sh" --skip-legacy
fi
if [[ ! -f "$PARITY_EXE" || "$SCRIPTDIR/ParitySurface.cs" -nt "$PARITY_EXE" ]]; then
  mcs -nologo -warn:4 -warnaserror -r:"$CECIL" "$SCRIPTDIR/ParitySurface.cs" -out:"$PARITY_EXE"
fi
mkdir -p "$OUT"
target="$OUT/parity_$LABEL.json"
tmp="$(mktemp "$OUT/.parity_$LABEL.XXXXXX")"
trap 'rm -f "$tmp"' EXIT
mono "$PARITY_EXE" "$DLL" 2>/dev/null | sed -n '/^{/,$p' > "$tmp"
python3 -m json.tool "$tmp" >/dev/null
mv "$tmp" "$target"
trap - EXIT
echo "[parity] wrote $target ($(wc -l < "$target") lines)"
echo "[parity] diff:  python3 $SCRIPTDIR/parity_diff.py <old.json> $OUT/parity_$LABEL.json"
