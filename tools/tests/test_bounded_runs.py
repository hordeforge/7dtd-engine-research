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

The shell entry points (regen.sh, build.sh, stock-sync.sh, drift-check.sh,
fetch_version.sh) spawn the same tools, so they carry the same bound through
tools/bounded-run.sh. Pinned here too:

  5. the shell wrapper kills a grandchild on expiry, like the Python one;
  6. an invalid `RE_MONO_TIMEOUT` fails the sourcing script instead of running
     unbounded;
  7. every mono/mcs/monodis child in tools/*.sh goes through `run_bounded`, so
     a new dump call cannot come back unbounded.

Usage: python3 tools/tests/test_bounded_runs.py
"""

from __future__ import annotations

import contextlib
import os
import re
import subprocess
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
# A mono/mcs/monodis child, at the start of a command or behind a var assignment.
SHELL_CHILD_RE = re.compile(
    r"(?:^|[;&|(]\s*|\bthen\s+|\bdo\s+|\$\(\s*)((?:[\w./]*=\S*\s+)?)(mono|mcs|monodis)\s"
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
        # ChildProcessError: the pid was already reaped, so there is no child to
        # wait for and the loop keeps probing.
        with contextlib.suppress(ChildProcessError):
            os.waitpid(pid, os.WNOHANG)
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


def _bash(script: str) -> subprocess.CompletedProcess[str]:
    # The shell default is 1800 s, sized for a whole-assembly dump; the probe
    # needs the same short bound the Python checks use or it waits it out.
    return subprocess.run(
        ["bash", "-c", f'. "{_common.TOOLS}/bounded-run.sh"\n{script}'],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, tooling.MONO_TIMEOUT_ENV: str(int(TIMEOUT_S))},
        timeout=GRANDCHILD_WAIT_S + 30.0,
    )


def check_shell_wrapper_kills_group(tmp: Path) -> None:
    """The shell bound kills the group too, and names the expired command."""
    marker = tmp / "shell-grandchild.pid"
    result = _bash(f'run_bounded {sys.executable} -c "{SNIPPET}" {marker}')
    assert result.returncode == 124, (
        f"shell run_bounded returned {result.returncode}, not 124: {result.stderr}"
    )
    assert "exceeded" in result.stderr, f"shell timeout names nothing: {result.stderr!r}"
    assert marker.is_file(), "the shell-run child never wrote its grandchild pid"
    pid = int(marker.read_text(encoding="utf-8").strip())
    assert wait_gone(pid), f"grandchild {pid} survived the shell timeout: only the child was killed"


def check_shell_timeout_env_fails_loud() -> None:
    for bad in ("nope", "0"):
        result = subprocess.run(
            ["bash", "-c", f'. "{_common.TOOLS}/bounded-run.sh"; echo REACHED'],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env={**os.environ, tooling.MONO_TIMEOUT_ENV: bad},
            timeout=GRANDCHILD_WAIT_S,
        )
        assert result.returncode == 2, (
            f"RE_MONO_TIMEOUT={bad!r} returned {result.returncode}, not 2"
        )
        assert "REACHED" not in result.stdout, (
            f"RE_MONO_TIMEOUT={bad!r} did not stop the sourcing script"
        )


class _ShellScanner:
    """Splits shell source into code and quoted text, line by line.

    A `#` inside quotes is text, not a comment: `echo "# mcs has no
    -deterministic"` writes a comment to buildinfo.txt and spawns nothing, and
    reading it as a spawn is a false positive that sends the next maintainer
    looking for a bound that is not missing. Quote state carries across lines,
    because a multi-line `echo` leaves the next line inside the string.
    """

    def __init__(self) -> None:
        self.quote: str | None = None

    def code(self, line: str) -> str:
        """The part of the line outside quotes and before any comment."""
        end: int | None = None
        for index, char in enumerate(line):
            if self.quote is not None:
                if char == self.quote:
                    self.quote = None
            elif char in "'\"":
                self.quote = char
                end = index if end is None else end
            elif char == "#" and (index == 0 or line[index - 1].isspace()):
                end = index
                break
        return line if end is None else line[:end]


def check_shell_scripts_are_bounded() -> None:
    """No mono/mcs/monodis child in a shell entry point comes back unbounded."""
    for path in sorted(_common.TOOLS.rglob("*.sh")):
        if path.name == "bounded-run.sh":
            continue
        scanner = _ShellScanner()
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            code = scanner.code(line)
            if not code.strip():
                continue
            match = SHELL_CHILD_RE.search(code)
            if match is None:
                continue
            assert "run_bounded" in code, (
                f"{path.name}:{number} spawns {match.group(2)} with no wall-clock bound: {line.strip()}"
            )


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="bounded-runs-", dir=_common.scratch_dir()) as td:
        check_timeout_kills_group(Path(td))
        check_shell_wrapper_kills_group(Path(td))
    check_passthrough()
    check_timeout_env()
    check_shell_timeout_env_fails_loud()
    check_shell_scripts_are_bounded()
    print("OK: a timed-out tool run is killed with its process group and reports the timeout")


if __name__ == "__main__":
    main()
