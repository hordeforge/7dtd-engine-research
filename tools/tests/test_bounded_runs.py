#!/usr/bin/env python3
"""Every child process the tools spawn is bounded, and the whole group dies.

`tooling.run_bounded()` is the one place mono, mcs, and `fetch_version.sh` are
launched from. Unbounded, a wedged child hangs the gate that spawned it instead
of failing it, and killing only the direct child would leave whatever it
spawned running with no parent. Pinned here, DLL-free and network-free:

  1. a command that outlives its bound reports the timeout rc and names itself
     in stderr, rather than blocking the caller;
  2. a grandchild of that command is gone once the bound expires, which is the
     group kill and not just the child;
  3. a command that finishes in time still passes through its real rc, stdout
     and stderr untouched;
  4. `RE_MONO_TIMEOUT` is read, and a value that is not a positive number of
     seconds fails loud instead of silently meaning "no bound".

Usage: python3 tools/tests/test_bounded_runs.py
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common
import tooling

GRANDCHILD_WAIT_S = 20.0
TIMEOUT_S = 2.0
SNIPPET = (
    "import subprocess, sys, time\n"
    "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(600)'])\n"
    "open(sys.argv[1], 'w').write(str(child.pid))\n"
    "time.sleep(600)\n"
)


def wait_gone(pid: int) -> bool:
    """Poll briefly for a pid to disappear. A zombie answers kill(0), so reap
    it opportunistically; this process is not its parent, so the check is a
    bound on the test, never a hang."""
    deadline = time.monotonic() + GRANDCHILD_WAIT_S
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        except PermissionError:
            # EPERM means the pid exists and belongs to another user, so it is
            # still running: reporting it gone here would turn a surviving
            # grandchild into a passing group-kill assertion.
            return False
        try:
            os.waitpid(pid, os.WNOHANG)
        except ChildProcessError:
            pass
        time.sleep(0.05)
    return False


def check_timeout_kills_group(tmp: Path) -> None:
    marker = tmp / "grandchild.pid"
    rc, _out, err = tooling.run_bounded(
        [sys.executable, "-c", SNIPPET, str(marker)],
        env=dict(os.environ),
        timeout=TIMEOUT_S,
    )
    assert rc == tooling.TIMEOUT_RC, f"timed-out command reported rc {rc}, not the timeout rc"
    assert sys.executable in err, f"timeout stderr does not name the command: {err!r}"
    assert marker.is_file(), "the child never wrote its grandchild pid, nothing to check"
    pid = int(marker.read_text(encoding="utf-8").strip())
    assert wait_gone(pid), f"grandchild {pid} survived the timeout: only the child was killed"


def check_passthrough() -> None:
    rc, out, err = tooling.run_bounded(
        [sys.executable, "-c", "import sys; print('hello'); sys.exit(3)"],
        env=dict(os.environ),
        timeout=60.0,
    )
    assert rc == 3, f"passthrough rc {rc}, expected the child's own 3"
    assert out.strip() == "hello", f"passthrough stdout {out!r}"
    assert err == "", f"passthrough stderr {err!r}"


def check_timeout_env() -> None:
    saved = os.environ.get(tooling.MONO_TIMEOUT_ENV)
    try:
        os.environ[tooling.MONO_TIMEOUT_ENV] = "12.5"
        assert tooling.mono_timeout() == 12.5
        for bad in ("nope", "0", "-1"):
            os.environ[tooling.MONO_TIMEOUT_ENV] = bad
            try:
                tooling.mono_timeout()
            except tooling.ConfigError:
                continue
            raise AssertionError(f"{tooling.MONO_TIMEOUT_ENV}={bad!r} did not fail loud")
        del os.environ[tooling.MONO_TIMEOUT_ENV]
        assert tooling.mono_timeout() == tooling.DEFAULT_MONO_TIMEOUT
    finally:
        if saved is None:
            os.environ.pop(tooling.MONO_TIMEOUT_ENV, None)
        else:
            os.environ[tooling.MONO_TIMEOUT_ENV] = saved


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="bounded-runs-", dir=_common.scratch_dir()) as td:
        check_timeout_kills_group(Path(td))
    check_passthrough()
    check_timeout_env()
    print("OK: a timed-out tool run is killed with its process group and reports the timeout")


if __name__ == "__main__":
    main()
