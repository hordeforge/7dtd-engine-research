"""Shared helpers for the RE tools and their gates, importing no other tool.

The repo root is found by walking up for the marker pair (`Makefile` +
`AGENTS.md`) instead of counting parent directories, so a script or module that
moves within the tree keeps pointing at the same checkout. Everything that needs
a repo path, the scratch base, or a file digest imports it from here: tools do
not reach into `tests/`, and gates import the same module the tools do.

`tools/tests/_common.py` re-exports these and adds the test-only helpers
(assembly discovery, mono runners, probe compilation).

`generation_stamp()` is the one clock the tools that stamp a committed artifact
read, so `SOURCE_DATE_EPOCH` makes their output replayable byte-for-byte.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT_MARKERS = ("Makefile", "AGENTS.md")
_HASH_CHUNK = 1 << 20
STAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
STAMP_ENV = "SOURCE_DATE_EPOCH"


class StampError(RuntimeError):
    """A pinned generation stamp is set to something that is not an epoch."""


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


def scratch_dir() -> Path:
    """Disk-backed base for temp trees, under the gitignored `.scratch/`.

    The system temp dir is tmpfs on the dev machines, so probe binaries,
    fixture trees and regenerated inventories would be charged to RAM.
    """
    path = REPO / ".scratch" / "tmp"
    path.mkdir(parents=True, exist_ok=True)
    return path


def find_asm() -> Path | None:
    """The local dedicated `Assembly-CSharp.dll`, or None when absent.

    Shared by the tools (a diff needs the live install) and the gates (a missing
    DLL means SKIP, not FAIL), so both agree on what "the local install" means.
    """
    candidates: list[Path] = []
    for env in ("ASM", "SEVENDTD_ASM", "SEVENDTD_DS_DIR"):
        value = os.environ.get(env)
        if not value:
            continue
        path = Path(value)
        if path.is_file() and path.name.endswith(".dll"):
            candidates.append(path)
        else:
            candidates.append(path / "7DaysToDieServer_Data/Managed/Assembly-CSharp.dll")
    home = Path.home()
    candidates.extend(
        [
            home / ".local/share/Steam/steamapps/common/"
            "7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll",
            home / ".steam/steam/steamapps/common/"
            "7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll",
        ]
    )
    return next((candidate for candidate in candidates if candidate.is_file()), None)


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


def run_mono(exe: str | Path, *args: str) -> tuple[int, str, str]:
    """Run a mono exe (path or a name inside tools/bin) -> (rc, stdout, stderr)."""
    target = exe if os.sep in str(exe) else BIN / str(exe)
    proc = subprocess.run(
        ["mono", str(target), *args],
        capture_output=True,
        text=True,
        env=mono_env(),
    )
    return proc.returncode, proc.stdout, proc.stderr
