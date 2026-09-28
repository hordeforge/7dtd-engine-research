#!/usr/bin/env bash
# Shared wall-clock bound for the child processes the shell entry points spawn
# (mono dumpers, mcs, monodis). Source it, do not run it:
#
#   . "$(dirname "${BASH_SOURCE[0]}")/bounded-run.sh"
#   run_bounded mono "$BIN/Census.exe" "$ASM"
#
# The same bound on the Python side is tooling.run_bounded(), and it exists for
# one reason: a wedged child must not outlive the run that started it. Cecil
# walking a malformed assembly, a runtime prompt on a bare mono, a compiler
# waiting on something: unbounded, that child holds the regen or the drift check
# open forever, and killing only the direct child would leave whatever it
# spawned still running. `timeout` puts the child in its own process group, so
# the signal on expiry reaches the grandchildren too, and the group is SIGKILLed
# after a grace period for a child that ignores the first signal.
#
# RE_MONO_TIMEOUT sets the bound in whole seconds, shared with the Python side.
# The default is 1800 where tooling.py uses 900: regen.sh drives DumpAll.exe
# over the whole assembly, which is not the per-tool census the 900 bound is
# sized for. A non-numeric or non-positive value fails loud here rather than
# silently meaning "no bound".
#
# Deliberately not wrapped here: steamcmd (tools/steam/fetch_version.sh), whose
# runtime is a depot download the operator paced, not a process that can wedge
# on a library walk.

# Seconds SIGTERM gets before the group is SIGKILLed. Same rule as
# RE_MONO_TIMEOUT below, and held to it for the same reason: the value reaches
# `timeout --kill-after=`, so a mistyped one is not a bound at all but a
# per-run failure of every command, named by timeout rather than here. Zero is
# a real setting (no grace, kill on expiry); negative is not a duration.
BOUNDED_KILL_GRACE_S="${BOUNDED_KILL_GRACE_S:-10}"
case "$BOUNDED_KILL_GRACE_S" in
  '' | *[!0-9]*)
    echo "BOUNDED_KILL_GRACE_S=$BOUNDED_KILL_GRACE_S: not a whole number of seconds" >&2
    exit 2
    ;;
esac
# Exit status `timeout` reports for an expired run.
BOUNDED_TIMEOUT_RC=124

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "usage: . \"\$(dirname \"\${BASH_SOURCE[0]}\")/bounded-run.sh\"" >&2
  echo "bounded-run.sh defines run_bounded for the shell entry points; sourcing it is the point" >&2
  exit 2
fi

RE_MONO_TIMEOUT="${RE_MONO_TIMEOUT:-1800}"
case "$RE_MONO_TIMEOUT" in
  '' | *[!0-9]*)
    echo "RE_MONO_TIMEOUT=$RE_MONO_TIMEOUT: not a whole number of seconds" >&2
    exit 2
    ;;
esac
if [[ "$RE_MONO_TIMEOUT" -lt 1 ]]; then
  echo "RE_MONO_TIMEOUT=$RE_MONO_TIMEOUT: must be at least 1 second" >&2
  exit 2
fi
export RE_MONO_TIMEOUT

# macOS ships no GNU timeout (coreutils installs it as gtimeout), and these
# scripts run there. A host with neither says so once and runs unbounded, rather
# than failing every regen over a missing optional tool; every other host gets
# the bound. The command is held in BOUNDED_TIMEOUT_CMD so run_bounded does not
# depend on the name being on PATH at call time.
BOUNDED_TIMEOUT_CMD=""
for candidate in timeout gtimeout; do
  if command -v "$candidate" >/dev/null 2>&1; then
    BOUNDED_TIMEOUT_CMD="$candidate"
    break
  fi
done
BOUNDED_HAS_TIMEOUT=0
if [[ -n "$BOUNDED_TIMEOUT_CMD" ]]; then
  BOUNDED_HAS_TIMEOUT=1
else
  echo "warning: no 'timeout' or 'gtimeout' on PATH; RE_MONO_TIMEOUT is not enforced for this run" >&2
  echo "  install coreutils (brew install coreutils) to bound every tool run" >&2
fi

# run_bounded CMD [ARG...] - run CMD under the bound, returning its own status,
# or BOUNDED_TIMEOUT_RC (with a line naming the command) when the bound expired.
run_bounded() {
  if [[ "$BOUNDED_HAS_TIMEOUT" == 0 ]]; then
    "$@"
    return $?
  fi
  local status=0
  "$BOUNDED_TIMEOUT_CMD" --kill-after="$BOUNDED_KILL_GRACE_S" "$RE_MONO_TIMEOUT" "$@" || status=$?
  if [[ "$status" == "$BOUNDED_TIMEOUT_RC" ]]; then
    printf '%s: %s exceeded %ss and its process group was killed\n' \
      "${0##*/}" "${1##*/}" "$RE_MONO_TIMEOUT" >&2
  fi
  return "$status"
}
