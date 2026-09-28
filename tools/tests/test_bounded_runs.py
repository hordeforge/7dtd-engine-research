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
     seconds fails loud instead of silently meaning "no bound";
  5. a host with no process group (Windows) still kills the child on expiry
     instead of raising out of the timeout path;
  6. a grandchild that survives that kill and holds the pipes open cannot turn
     the bound back into a hang, and the parent's descriptors are released;
  7. an interrupt out of the wait kills the group too, since the child is in
     its own session and the signal never reached it;
  8. `BOUNDED_KILL_GRACE_S` follows the same rule, with zero a real setting;
  9. a gate that spawns a child bounds it, so a wedged tool fails a gate
     instead of hanging it.

The shell entry points (regen.sh, build.sh, stock-sync.sh, drift-check.sh,
fetch_version.sh) spawn the same tools, so they carry the same bound through
tools/bounded-run.sh. Pinned here too:

 10. the shell wrapper kills a grandchild on expiry, like the Python one;
 11. an invalid `RE_MONO_TIMEOUT` fails the sourcing script instead of running
     unbounded;
 12. every mono/mcs/monodis child in tools/*.sh goes through `run_bounded`, so
     a new dump call cannot come back unbounded.

Usage: python3 tools/tests/test_bounded_runs.py
"""

from __future__ import annotations

import ast
import contextlib
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common
import tooling

GRANDCHILD_WAIT_S = 20.0
# Long enough for the child to start a grandchild and write its pid before the
# bound expires: on a loaded host a bare interpreter start alone can take longer
# than 2 s, and the marker read then fails for want of a race the test means to
# win, not for want of a kill.
TIMEOUT_S = 10.0
# The subprocess callables that start a child.
SUBPROCESS_CALLS = {"run", "Popen", "call", "check_call", "check_output"}
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
# A quoted span is one argument, so a tool named inside it is text, not a spawn.
QUOTED_RE = re.compile(r"""'[^']*'|"[^"]*\"""")


def child_start_s() -> float:
    """Wall time for one bare child start on this host."""
    start = time.monotonic()
    subprocess.run([sys.executable, "-c", "pass"], check=True, timeout=60)
    return time.monotonic() - start


def probe_bound_s() -> float:
    """The bound the group-kill probes run under.

    It has to clear the child's own cold start several times over. A fixed
    2 s bound expires on a loaded or slow host before the probe has written
    the grandchild pid, and the gate then reports a missing marker for what is
    really a slow interpreter start: the probe measures the host, not the
    wrapper it is there to check.
    """
    return max(TIMEOUT_S, child_start_s() * 3.0 + 1.0)


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
        timeout=probe_bound_s(),
    )
    assert rc == tooling.TIMEOUT_RC, f"timed-out command reported rc {rc}, not the timeout rc"
    assert sys.executable in err, f"timeout stderr does not name the command: {err!r}"
    assert marker.is_file(), "the child never wrote its grandchild pid, nothing to check"
    pid = int(marker.read_text(encoding="utf-8").strip())
    assert wait_gone(pid), f"grandchild {pid} survived the timeout: only the child was killed"


def open_fd_count() -> int:
    """Descriptors this process holds, or -1 where /proc does not exist."""
    if not os.path.isdir("/proc/self/fd"):
        return -1
    return len(os.listdir("/proc/self/fd"))


def check_pipes_are_released_without_a_group(tmp: Path) -> None:
    """A survivor holding the pipes cannot turn the bound back into a hang.

    On a host with no process group the kill reaches the direct child alone, and
    the grandchild it spawned keeps the inherited write ends open. The read of a
    killed child is bounded for exactly that case, and when the bound expires it
    is abandoned with both pipes closed: the parent's descriptors come back and
    the call returns the timeout rc instead of blocking forever.
    """
    if getattr(os, "killpg", None) is None:
        return
    marker = tmp / "pipe-holder.pid"
    before = open_fd_count()
    killpg = os.killpg
    del os.killpg
    started = time.monotonic()
    try:
        rc, _out, err = tooling.run_bounded(
            [sys.executable, "-c", SNIPPET, str(marker)],
            env=dict(os.environ),
            timeout=probe_bound_s(),
        )
    finally:
        os.killpg = killpg
    elapsed = time.monotonic() - started
    # The grandchild outlived the kill on purpose, so it is this run's to reap.
    assert marker.is_file(), "the child never wrote its grandchild pid"
    with contextlib.suppress(OSError):
        os.kill(int(marker.read_text(encoding="utf-8").strip()), signal.SIGKILL)
    assert rc == tooling.TIMEOUT_RC, f"the unkillable-pipe case reported rc {rc}: {err}"
    budget = probe_bound_s() + 2 * tooling.POST_KILL_TIMEOUT + GRANDCHILD_WAIT_S
    assert elapsed < budget, f"the kill path blocked {elapsed:.1f}s, past its {budget:.0f}s budget"
    after = open_fd_count()
    assert before == -1 or after <= before, (
        f"the abandoned read left {after - before} more descriptors open ({before} -> {after})"
    )


def check_interrupt_kills_group(tmp: Path) -> None:
    """An interrupt out of the wait kills the group, like the timeout does.

    The child runs in its own session, so a Ctrl-C at the gate never reaches it:
    without a kill on the unwind the tool outlives the run that started it, and
    the two pipe descriptors stay open with it.
    """
    marker = tmp / "interrupt-grandchild.pid"
    real = subprocess.Popen.communicate
    calls: list[int] = []

    def interrupt_the_first_read(
        self: subprocess.Popen[str], *args: Any, **kwargs: Any
    ) -> tuple[str, str]:
        # Raised out of the wait rather than delivered by a signal: a real
        # Ctrl-C is not reproducible here (the child is in its own session, and
        # 3.14's Popen wait defers the signal past the wait), and what is under
        # test is what the unwind does, not how the exception arrived.
        calls.append(1)
        if len(calls) == 1:
            deadline = time.monotonic() + GRANDCHILD_WAIT_S
            while not marker.is_file() and time.monotonic() < deadline:
                time.sleep(0.05)
            raise KeyboardInterrupt
        return real(self, *args, **kwargs)

    subprocess.Popen.communicate = interrupt_the_first_read  # type: ignore[method-assign]
    try:
        tooling.run_bounded(
            [sys.executable, "-c", SNIPPET, str(marker)],
            env=dict(os.environ),
            timeout=probe_bound_s() * 4,
        )
    except KeyboardInterrupt:
        pass
    else:
        raise AssertionError("the interrupt never landed inside the wait")
    finally:
        subprocess.Popen.communicate = real  # type: ignore[method-assign]
    assert len(calls) == 2, f"the unwind drained the pipes {len(calls) - 1} times, not once"
    assert marker.is_file(), "the child never started, nothing was interrupted"
    pid = int(marker.read_text(encoding="utf-8").strip())
    assert wait_gone(pid), f"grandchild {pid} survived the interrupt: the child was left running"


def check_kill_group_fallback() -> None:
    """Without a process group (Windows), the bound still kills the child.

    A host with no `os.killpg` used to reach `os.killpg` and raise
    AttributeError out of the timeout path, so a wedged tool turned a reported
    timeout into a crashed gate. The fallback is pinned here by removing the
    attribute for the duration of the call, which is what the Windows host
    looks like to this code.
    """
    calls: list[int] = []

    class _Child:
        pid = 4242

        def kill(self) -> None:
            calls.append(self.pid)

    killpg = getattr(os, "killpg", None)
    if killpg is not None:
        del os.killpg
    try:
        tooling.kill_child_group(_Child())  # type: ignore[arg-type]
    finally:
        if killpg is not None:
            os.killpg = killpg
    assert calls == [4242], f"the no-process-group path killed {calls}, not the child"


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


def _bash(script: str, bound: float) -> subprocess.CompletedProcess[str]:
    # The shell default is 1800 s, sized for a whole-assembly dump; the probe
    # needs a short bound or it waits it out. The variable is whole seconds.
    return subprocess.run(
        ["bash", "-c", f'. "{_common.TOOLS}/bounded-run.sh"\n{script}'],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, tooling.MONO_TIMEOUT_ENV: str(max(1, round(bound)))},
        timeout=GRANDCHILD_WAIT_S + 30.0,
    )


def check_shell_wrapper_kills_group(tmp: Path) -> None:
    """The shell bound kills the group too, and names the expired command."""
    marker = tmp / "shell-grandchild.pid"
    result = _bash(f'run_bounded {sys.executable} -c "{SNIPPET}" {marker}', probe_bound_s())
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


def check_kill_grace_env_fails_loud() -> None:
    """The SIGKILL grace takes the same rule, and 0 is a real setting.

    The value reaches `timeout --kill-after=`, so a mistyped one is not a bound
    at all but a failure of every command the wrapper runs, named by `timeout`
    rather than by the script that took the value.
    """
    for bad in ("nope", "-1", "1.5"):
        result = subprocess.run(
            ["bash", "-c", f'. "{_common.TOOLS}/bounded-run.sh"; echo REACHED'],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env={**os.environ, "BOUNDED_KILL_GRACE_S": bad},
            timeout=GRANDCHILD_WAIT_S,
        )
        assert result.returncode == 2, (
            f"BOUNDED_KILL_GRACE_S={bad!r} returned {result.returncode}, not 2"
        )
        assert "REACHED" not in result.stdout, (
            f"BOUNDED_KILL_GRACE_S={bad!r} did not stop the sourcing script"
        )
    # Zero is a duration with no grace, and an empty value is an unset one:
    # both take the `:-` default the whole script is written in.
    for value, want in (("0", "0"), ("", "10")):
        result = subprocess.run(
            ["bash", "-c", f'. "{_common.TOOLS}/bounded-run.sh"; echo $BOUNDED_KILL_GRACE_S'],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env={**os.environ, "BOUNDED_KILL_GRACE_S": value, tooling.MONO_TIMEOUT_ENV: "2"},
            timeout=GRANDCHILD_WAIT_S,
        )
        assert result.returncode == 0, f"BOUNDED_KILL_GRACE_S={value!r}: {result.stderr!r}"
        assert result.stdout.strip() == want, (
            f"BOUNDED_KILL_GRACE_S={value!r} resolved to {result.stdout!r}, want {want!r}"
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


def spawns_a_tool(stripped: str) -> bool:
    """True when a source line launches mono/mcs/monodis as a command.

    Two things only ever name a tool in a shell entry point without running
    one: a comment, and a string being written out. `build.sh` records
    `mcs=$mcs_ver` and a comment mentioning mcs in `bin/buildinfo.txt`; reading
    either as a spawn fails the gate on a line that spawns nothing. Command
    substitution in the argument is the exception, because there the tool runs.
    """
    if stripped.startswith("#"):
        return False
    word = stripped.split(None, 1)[0] if stripped else ""
    if word in ("echo", "printf") and "$(" not in stripped and "`" not in stripped:
        return False
    return SHELL_CHILD_RE.search(stripped) is not None


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
            # A tool named inside a quoted substitution runs, and the scanner
            # reads quoted text as text, so the quote-stripped line and then
            # the raw line are the fallback sources.
            source, match = code, SHELL_CHILD_RE.search(code)
            if match is None:
                unquoted = QUOTED_RE.sub("", line)
                source, match = unquoted, SHELL_CHILD_RE.search(unquoted)
            if match is None and spawns_a_tool(line.strip()):
                source, match = line, SHELL_CHILD_RE.search(line)
            if match is None:
                continue
            assert "run_bounded" in source, (
                f"{path.name}:{number} spawns {match.group(2)} with no wall-clock bound: {line.strip()}"
            )


# A write naming a tool, a comment naming a tool, and the real spawn forms.
DETECTOR_CASES = (
    ('echo "mcs=$mcs_ver"', False),
    ('echo "# name, and the source paths are mapped out; mcs has no"', False),
    ('echo "installed: $(mcs --version)"', True),
    ("# mcs is only needed for the legacy dumpers", False),
    ('mcs_ver="$(run_bounded mcs --version 2>/dev/null)"', True),
    ("mcs -nologo -out:bin/Census.exe src/Census.cs", True),
)


def check_spawn_detector() -> None:
    """The text-write exemption must not hide a real spawn."""
    for line, want in DETECTOR_CASES:
        got = spawns_a_tool(line)
        assert got == want, f"spawns_a_tool({line!r}) is {got}, want {want}"


def check_gate_children_are_bounded() -> None:
    """No child a gate spawns comes back unbounded.

    A gate is a tool: `tooling.run_bounded` and `tools/bounded-run.sh` bound
    every child the tools start, and a gate that called `subprocess.run` with
    no `timeout=` had no bound at all, so a wedged tool hung the gate instead
    of failing it. A call that passes its own `timeout=` is bounded, so the
    check is on the call rather than the module.

    The two perf benches are exempt: their whole job is a run long enough to
    measure, so a bound would be the thing under test rather than its guard.
    """
    exempt = {"test_bounded_runs.py", "bench_asm_body_diff.py", "bench_version_update_tooling.py"}
    offenders: list[str] = []
    for path in sorted(_common.TOOLS.rglob("tests/*.py")):
        if path.name in exempt or path.name == "_common.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (isinstance(func, ast.Attribute) and func.attr in SUBPROCESS_CALLS):
                continue
            if any(kw.arg == "timeout" for kw in node.keywords):
                continue
            if isinstance(func.value, ast.Name) and func.value.id == "subprocess":
                offenders.append(f"{path.name}:{node.lineno} subprocess.{func.attr}() is unbounded")
    assert not offenders, "\n".join(offenders)


def check_shell_gtimeout_fallback(tmp: Path) -> None:
    """macOS has no `timeout`; coreutils installs it as `gtimeout`.

    The Platforms section of tools/README.md promises that fallback, so a
    source that only probes `timeout` leaves every regen on macOS unbounded
    while the docs say it is bounded. Driven with a PATH holding only the
    `gtimeout` stub, so the probe has to find that name to pass.
    """
    stub_dir = tmp / "fakebin"
    stub_dir.mkdir()
    stub = stub_dir / "gtimeout"
    stub.write_text('#!/bin/bash\necho "GTIMEOUT $*"\nshift 2\n"$@"\n', encoding="utf-8")
    os.chmod(stub, 0o755)
    bash = shutil.which("bash")
    assert bash is not None, "no bash on PATH to source the wrapper with"
    result = subprocess.run(
        [
            bash,
            "-c",
            (
                f'. "{_common.TOOLS}/bounded-run.sh"\n'
                '[[ "$BOUNDED_HAS_TIMEOUT" == 1 ]] || { echo "gtimeout not found"; exit 1; }\n'
                "run_bounded echo child-ran"
            ),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={"PATH": str(stub_dir), "RE_MONO_TIMEOUT": "30"},
        timeout=GRANDCHILD_WAIT_S,
    )
    assert result.returncode == 0, f"the shell bound did not fall back to gtimeout: {result.stderr}"
    assert "GTIMEOUT" in result.stdout, f"gtimeout was not the bound used: {result.stdout!r}"
    assert "child-ran" in result.stdout, f"the child never ran: {result.stdout!r}"


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="bounded-runs-", dir=_common.scratch_dir()) as td:
        check_timeout_kills_group(Path(td))
        check_shell_wrapper_kills_group(Path(td))
        check_shell_gtimeout_fallback(Path(td))
        check_pipes_are_released_without_a_group(Path(td))
        check_interrupt_kills_group(Path(td))
    check_passthrough()
    check_kill_group_fallback()
    check_timeout_env()
    check_shell_timeout_env_fails_loud()
    check_kill_grace_env_fails_loud()
    check_spawn_detector()
    check_shell_scripts_are_bounded()
    check_gate_children_are_bounded()
    print("OK: a timed-out tool run is killed with its process group and reports the timeout")


if __name__ == "__main__":
    main()
