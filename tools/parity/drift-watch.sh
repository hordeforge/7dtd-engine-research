#!/usr/bin/env bash
# Watch the dedicated-server DLL and run drift-check whenever Steam rewrites it
# (i.e. on a game update). Appends a timestamped report to the log. Foreground;
# run under nohup/systemd for persistence.
#   drift-watch.sh [ASM] [LOGFILE]
set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASM="${1:-$HOME/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll}"
LOG="${2:-$HOME/.cache/zdtd-scratch/drift.log}"
echo "[drift-watch] watching $ASM (log: $LOG)"
if command -v inotifywait >/dev/null 2>&1; then
  while inotifywait -e close_write,move_self,create "$(dirname "$ASM")" 2>/dev/null | grep -q "$(basename "$ASM")"; do
    { echo "==== drift $(cat /proc/uptime | cut -d. -f1)s uptime ===="; bash "$here/drift-check.sh" "$ASM"; } >> "$LOG" 2>&1
  done
else # portable mtime-poll fallback (no inotify-tools)
  last=""
  while sleep 300; do
    cur="$(stat -c %Y "$ASM" 2>/dev/null || echo 0)"
    [[ "$cur" != "$last" && -n "$last" ]] && { echo "==== drift (mtime change) ===="; bash "$here/drift-check.sh" "$ASM"; } >> "$LOG" 2>&1
    last="$cur"
  done
fi
