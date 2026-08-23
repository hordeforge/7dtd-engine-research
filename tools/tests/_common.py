"""Shared test prerequisites: game-assembly discovery + mono tool runner.

Every tools/tests script that drives the Mono.Cecil binaries needs the same
three things: locate the local dedicated Assembly-CSharp.dll, decide whether a
missing prerequisite means "nothing to assert here" (SKIP) versus "you have the
game, so regenerate" (FAIL), and invoke bin/*.exe with MONO_PATH wired.
Tests that compile an ad-hoc C# probe share compile_probe/run_probe.

Convention (mirrors test_re_dump_regen.py):
  - dedicated DLL absent            -> SKIP (machine-local, git-ignored inputs)
  - DLL present, bin tools missing  -> FAIL (actionable: cd tools && ./build.sh)
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
REPO = TOOLS.parent
BIN = TOOLS / "bin"


def find_asm() -> Path | None:
    """Return the local dedicated Assembly-CSharp.dll, or None when absent."""
    candidates: list[Path] = []
    for env in ("ASM", "SEVENDTD_ASM", "SEVENDTD_DS_DIR"):
        value = os.environ.get(env)
        if not value:
            continue
        p = Path(value)
        if p.is_file() and p.name.endswith(".dll"):
            candidates.append(p)
        else:
            candidates.append(
                p / "7DaysToDieServer_Data/Managed/Assembly-CSharp.dll"
            )
    home = Path.home()
    candidates.extend(
        [
            home
            / ".local/share/Steam/steamapps/common/"
            "7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll",
            home
            / ".steam/steam/steamapps/common/"
            "7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll",
        ]
    )
    return next((c for c in candidates if c.is_file()), None)


def resolve_asm(explicit: str | None) -> tuple[Path | None, str]:
    """Resolve the assembly from an explicit CLI arg, else discovery."""
    if explicit:
        p = Path(explicit)
        if p.is_file():
            return p, str(p)
        return None, str(p)
    found = find_asm()
    return found, (str(found) if found else "auto-discovery")


def prereq(tool_names: list[str]) -> tuple[str, bool]:
    """Check run prerequisites for the named bin tools.

    Returns (message, is_skip): a missing dedicated DLL is a SKIP (nothing
    regenerable locally to assert); a missing built binary while the DLL is
    present is an actionable FAIL.
    """
    if find_asm() is None:
        return (
            "dedicated Assembly-CSharp.dll not found "
            "(set ASM=<path to Assembly-CSharp.dll>)",
            True,
        )
    missing = [t for t in tool_names if not (BIN / t).is_file()]
    if missing:
        return (
            "bin tools not built: " + ", ".join(missing)
            + " (cd tools && ./build.sh --skip-legacy)",
            False,
        )
    if shutil.which("mono") is None:
        return "mono not on PATH", False
    return "", False


def run_tool(exe: str, *args: str) -> tuple[int, str, str]:
    """Run bin/<exe> under mono with MONO_PATH pointing at tools/bin."""
    env = dict(os.environ, MONO_PATH=str(BIN))
    proc = subprocess.run(
        ["mono", str(BIN / exe), *args],
        capture_output=True,
        text=True,
        env=env,
    )
    return proc.returncode, proc.stdout, proc.stderr


def compile_probe(cs_text: str, stem: str) -> str:
    """Write cs_text to /tmp/<stem>.cs, compile against bin/Mono.Cecil.dll.

    Returns the /tmp/<stem>.exe path; a compile error raises (CalledProcessError).
    """
    exe = f"/tmp/{stem}.exe"
    src = f"/tmp/{stem}.cs"
    with open(src, "w") as f:
        f.write(cs_text)
    subprocess.run(
        ["mcs", "-r:%s" % (BIN / "Mono.Cecil.dll"), src, "-out:" + exe], check=True
    )
    return exe


def run_probe(exe: str, *args: str) -> str:
    """Run a compiled probe under mono with MONO_PATH wired; returns stdout."""
    proc = subprocess.run(
        ["mono", exe, *args],
        capture_output=True,
        text=True,
        env=dict(os.environ, MONO_PATH=str(BIN)),
        check=True,
    )
    return proc.stdout
