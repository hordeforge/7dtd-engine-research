"""Shared helpers for the RE tools and their gates, importing no other tool.

The repo root is found by walking up for the marker pair (`Makefile` +
`AGENTS.md`) instead of counting parent directories, so a script or module that
moves within the tree keeps pointing at the same checkout. Everything that needs
a repo path, the scratch base, or a file digest imports it from here: tools do
not reach into `tests/`, and gates import the same module the tools do.

`tools/tests/_common.py` re-exports these and adds the test-only helpers
(assembly discovery, mono runners, probe compilation).

Every environment variable the tools read is resolved here, with one rule for
each: an override that names an install is honoured or refused, never traded
for a discovered one, and a bound that is not a positive number raises
ConfigError rather than meaning "no bound". A tool that reads configuration
any other way re-derives those rules, which is how they drift apart.

`generation_stamp()` is the one clock the tools that stamp a committed artifact
read, so `SOURCE_DATE_EPOCH` makes their output replayable byte-for-byte.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import signal
import subprocess
import unicodedata
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT_MARKERS = ("Makefile", "AGENTS.md")
_HASH_CHUNK = 1 << 20
STAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
STAMP_ENV = "SOURCE_DATE_EPOCH"
MONO_TIMEOUT_ENV = "RE_MONO_TIMEOUT"
DEFAULT_MONO_TIMEOUT = 900.0
TIMEOUT_RC = 124

# The dedicated server is a Steam app, and Steam installs to a different tree
# per OS, so discovery probes every known root rather than assuming the Linux
# one. Windows names its roots through the environment; on Linux/macOS those
# variables are absent, and on Windows the lookup is case-insensitive, so one
# list covers every host.
STEAM_ROOT_ENV = ("ProgramFiles(x86)", "ProgramFiles", "ProgramW6432")
STEAM_ROOTS_HOME = (
    ".local/share/Steam",  # Linux default
    ".steam/steam",  # Linux, older default
    ".steam/root",  # Linux, ~/.steam symlink to the real root
    "Library/Application Support/Steam",  # macOS
)
STEAM_COMMON = ("steamapps", "common")
GAME_DIR = "7 Days to Die Dedicated Server"
MANAGED = ("7DaysToDieServer_Data", "Managed")
ASM_NAME = "Assembly-CSharp.dll"
ASM_VARS = ("ASM", "SEVENDTD_ASM", "SEVENDTD_DS_DIR")


class ConfigError(RuntimeError):
    """An environment variable names something that is not there.

    A caller that reads configuration through this module gets the failure
    here rather than a value it cannot use: the alternative is a fallback that
    answers with a different install, a default that looks like an operator's
    choice, or a downstream error naming the wrong thing.
    """


class StampError(RuntimeError):
    """A pinned generation stamp is set to something that is not an epoch."""


def positive_seconds(name: str, default: float) -> float:
    """A wall-clock bound in seconds from the environment.

    Unset means the documented default; a value that is not a positive number
    raises ConfigError rather than being read as "no bound" or "no timeout",
    because a mistyped bound silently turns a hung child into a hung gate.
    Shared by every timeout the tools take, so the rule and the message are the
    same whichever variable was set.
    """
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        seconds = float(raw.strip())
    except ValueError as exc:
        raise ConfigError(f"{name}={raw!r} is not a number of seconds") from exc
    if seconds <= 0:
        raise ConfigError(f"{name}={raw!r} must be positive")
    return seconds


def repo_root() -> Path:
    """Nearest ancestor holding every root marker."""
    here = Path(__file__).resolve()
    for directory in here.parents:
        if all((directory / marker).is_file() for marker in ROOT_MARKERS):
            return directory
    raise RuntimeError(f"repo root ({', '.join(ROOT_MARKERS)}) not found above {here}")


REPO = repo_root()
TOOLS = REPO / "tools"
BIN = TOOLS / "bin"
DOCS = REPO / "docs"


def nfc(s: str) -> str:
    """A name as every gate keys it: Unicode NFC.

    A doc basename is an identity the corpus resolves against from three
    sources that need not agree on spelling: the filename the author created,
    the link text typed into another doc, and a citation pasted from a
    sibling repo. macOS filesystems store and hand back NFD, so the same word
    arrives in two spellings, and byte equality then reports a live doc as a
    dead link (or the reverse). NFC is the form docs are written in, so both
    sides are normalized before they are compared rather than asking the
    author which form their filesystem handed them.
    """
    return unicodedata.normalize("NFC", s)


class NonFiniteNumberError(ValueError):
    """A JSON document carried NaN or Infinity, which JSON cannot represent."""


def _reject_non_finite(literal: str) -> float:
    raise NonFiniteNumberError(
        f"JSON contains the non-finite literal {literal}; JSON has no spelling for it, "
        "and a pin that carries one compares false against every tolerance check "
        "(NaN - 62.88 is NaN, and NaN > 1e-6 is False)"
    )


def _finite_float(literal: str) -> float:
    """`parse_float` hook: a decimal literal that overflows binary64 is also a
    value JSON cannot round-trip, and it becomes inf silently otherwise."""
    value = float(literal)
    if value in (float("inf"), float("-inf")):
        raise NonFiniteNumberError(f"JSON number {literal} overflows to infinity")
    return value


def loads_json(text: str) -> Any:
    """`json.loads` that refuses NaN, +/-Infinity, and literals that overflow.

    Python accepts those by default, and the C# extractor writes NaN for a
    float constant that is not finite. Every numeric pin in the corpus is
    checked as `abs(got - want) > tol`, which a NaN passes silently, so the
    artifact has to be rejected at the load instead of at each comparison.
    """
    return json.loads(text, parse_constant=_reject_non_finite, parse_float=_finite_float)


def load_json(path: Path) -> Any:
    return loads_json(path.read_text(encoding="utf-8"))


def scratch_dir() -> Path:
    """Disk-backed base for temp trees, under the gitignored `.scratch/`.

    The system temp dir is tmpfs on the dev machines, so probe binaries,
    fixture trees and regenerated inventories would be charged to RAM.
    """
    path = REPO / ".scratch" / "tmp"
    path.mkdir(parents=True, exist_ok=True)
    return path


def steam_roots(env: Mapping[str, str], home: Path) -> list[Path]:
    """Steam library roots to probe, in the order the host is most likely to use."""
    roots = [Path(env[name]) for name in STEAM_ROOT_ENV if env.get(name)]
    roots.extend(home / relative for relative in STEAM_ROOTS_HOME)
    return roots


def override_path(value: str) -> Path:
    """The assembly an override names: the file itself, or under an install root.

    A value that is not an existing `.dll` is read as the install root holding
    `7DaysToDieServer_Data/Managed/`, so one variable covers both forms the
    README documents.
    """
    path = Path(value)
    if path.is_file() and path.suffix.lower() == ".dll":
        return path
    return path.joinpath(*MANAGED, ASM_NAME)


def env_candidates(env: Mapping[str, str]) -> list[tuple[str, Path]]:
    """`(variable, path)` for every ASM_VARS override, in the documented order.

    An override is either the assembly itself or the install root holding
    `7DaysToDieServer_Data/Managed/`. The pair is kept so a caller can report
    which variable resolved to what, and can tell an override apart from a root
    that discovery probed.
    """
    overrides: list[tuple[str, Path]] = []
    for name in ASM_VARS:
        value = env.get(name)
        if not value:
            continue
        overrides.append((name, override_path(value)))
    return overrides


def asm_candidates(env: Mapping[str, str], home: Path) -> list[Path]:
    """Every path `find_asm` may resolve to, explicit overrides first.

    Split out from `find_asm` so the per-OS layout is testable on a host that
    only has one of them.
    """
    candidates = [path for _, path in env_candidates(env)]
    candidates.extend(
        root.joinpath(*STEAM_COMMON, GAME_DIR, *MANAGED, ASM_NAME)
        for root in steam_roots(env, home)
    )
    return candidates


def find_asm() -> Path | None:
    """The local dedicated `Assembly-CSharp.dll`, or None when absent.

    Shared by the tools (a diff needs the live install) and the gates (a missing
    DLL means SKIP, not FAIL), so both agree on what "the local install" means.

    A variable that names an install is honoured or refused: with `ASM` (or
    `SEVENDTD_ASM` / `SEVENDTD_DS_DIR`) set to a path that holds no assembly,
    this raises ConfigError instead of probing on and answering with whatever
    Steam root the host happens to carry. A pin run pointed at a build that is
    not there has to stop; silently verifying a different build reads exactly
    like a green one.
    """
    for name in ASM_VARS:
        value = os.environ.get(name)
        if not value:
            continue
        path = override_path(value)
        if not path.is_file():
            raise ConfigError(
                f"{name}={value} holds no assembly (looked for {path}); unset it to "
                f"use the Steam install roots probed on this host"
            )
    candidates = asm_candidates(os.environ, Path.home())
    return next((candidate for candidate in candidates if candidate.is_file()), None)


def game_dir(asm: Path) -> Path | None:
    """The dedicated-server install root a resolved assembly sits in.

    `<root>/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll` -> `<root>`, the
    directory that holds `Data/Config`, so every XML pin reads one install.
    None for an assembly that is not under that layout (a copied DLL, a fixture),
    because the caller then has to be told rather than handed a wrong root.
    """
    tail = Path(*MANAGED, ASM_NAME)
    count = len(tail.parts)
    if asm.parts[-count:] != tail.parts:
        return None
    return Path(*asm.parts[: len(asm.parts) - count])


def resolve_asm(explicit: str | None) -> tuple[Path | None, str]:
    """Resolve the assembly from an explicit CLI argument, else discovery."""
    if explicit:
        path = Path(explicit)
        if path.is_file():
            return path, str(path)
        return None, str(path)
    found = find_asm()
    return found, (str(found) if found else "auto-discovery")


def generation_stamp() -> str:
    """UTC stamp (`2026-09-20T04:46:00Z`) for a generated artifact.

    Every tool that stamps a committed artifact (the build-diff report, the
    census history row, the studied-build pin) reads the clock here, so a run
    can be replayed byte-for-byte: set `SOURCE_DATE_EPOCH` to the integer UTC
    epoch the artifact should carry and the output becomes a pure function of
    its inputs, down to the date in a default output filename. Unset, the wall
    clock is used, which is what an interactive run wants. A value that is not
    an integer raises rather than silently falling back, because a mistyped
    stamp would otherwise be written into a committed file and look recorded.
    """
    raw = os.environ.get(STAMP_ENV)
    if raw is None:
        return datetime.now(timezone.utc).strftime(STAMP_FORMAT)
    try:
        seconds = int(raw.strip())
    except ValueError as exc:
        raise StampError(f"{STAMP_ENV}={raw!r} is not an integer UTC epoch") from exc
    return datetime.fromtimestamp(seconds, tz=timezone.utc).strftime(STAMP_FORMAT)


def sha256_file(path: Path) -> str:
    """Streaming SHA-256 of a file (assemblies are ~11 MB, reports larger)."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(_HASH_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mono_env() -> dict[str, str]:
    """Process environment with MONO_PATH wired at tools/bin.

    Every dumper links Mono.Cecil from there, so mono needs the hint to load it.
    """
    env = dict(os.environ)
    env["MONO_PATH"] = str(BIN)
    return env


def mono_timeout() -> float:
    """Seconds a spawned tool may run before it is killed, from the env.

    A wedged mono (a malformed assembly driving Cecil into a long walk, a
    runtime prompt) otherwise blocks the gate that spawned it forever, so the
    bound lives here and every runner shares it. `RE_MONO_TIMEOUT` raises it
    for a slow host; a non-numeric or non-positive value fails loud rather than
    silently meaning "no bound".
    """
    return positive_seconds(MONO_TIMEOUT_ENV, DEFAULT_MONO_TIMEOUT)


def run_bounded(
    command: list[str], *, env: dict[str, str], timeout: float | None = None
) -> tuple[int, str, str]:
    """Run a tool to completion under a wall-clock bound -> (rc, stdout, stderr).

    The child gets its own process group and a timeout, and the whole group is
    killed on expiry: killing only the direct child would orphan whatever it
    spawned. A timeout reports TIMEOUT_RC rather than raising, so a caller that
    already handles a nonzero rc reports the failure instead of unwinding.
    """
    limit = mono_timeout() if timeout is None else timeout
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        start_new_session=True,
    )
    try:
        out, err = proc.communicate(timeout=limit)
    except subprocess.TimeoutExpired:
        _kill_group(proc)
        out, err = proc.communicate()
        return TIMEOUT_RC, out, f"{command[0]} exceeded {limit:g}s and was killed\n{err}"
    return proc.returncode, out, err


def _kill_group(proc: "subprocess.Popen[str]") -> None:
    """SIGKILL the child's process group, so grandchildren die with it."""
    # ProcessLookupError: the group is already gone, which is the state asked for.
    with contextlib.suppress(ProcessLookupError):
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)


def run_mono(exe: str | Path, *args: str) -> tuple[int, str, str]:
    """Run a mono exe (path or a name inside tools/bin) -> (rc, stdout, stderr)."""
    target = exe if os.sep in str(exe) else BIN / str(exe)
    return run_bounded(["mono", str(target), *args], env=mono_env())
