"""Shared test prerequisites: game-assembly discovery + mono tool runner.

Every tools/tests script that drives the Mono.Cecil binaries needs the same
three things: locate the local dedicated Assembly-CSharp.dll, decide whether a
missing prerequisite means "nothing to assert here" (SKIP) versus "you have the
game, so regenerate" (FAIL), and invoke bin/*.exe with MONO_PATH wired.
Tests that compile an ad-hoc C# probe share compile_probe/run_probe.

Convention (mirrors test_re_dump_regen.py):
  - dedicated DLL absent            -> SKIP (machine-local, git-ignored inputs)
  - DLL present, bin tools missing  -> FAIL (fix: cd tools && ./build.sh)
"""

from __future__ import annotations

import ast
import atexit
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Paths and file digests live in tools/tooling.py so the tools themselves can
# import them without depending on this test package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tooling

# Re-exported so the gates keep one import surface (`_common.TOOLS`, ...); the
# shared definitions live in tools/tooling.py.
REPO = tooling.REPO
TOOLS = tooling.TOOLS
BIN = tooling.BIN
DOCS = tooling.DOCS
repo_root = tooling.repo_root
scratch_dir = tooling.scratch_dir
sha256_file = tooling.sha256_file
find_asm = tooling.find_asm
resolve_asm = tooling.resolve_asm

ROOT_MARKERS = ("Makefile", "AGENTS.md")


def doc(name: str) -> Path:
    """Path of a narrative doc by basename, wherever its subsystem folder sits.

    docs/ is grouped by subsystem (docs/network/protocol.md, ...); basenames stay
    unique across the tree, so a gate cites a doc by name and never by folder.
    """
    hits: list[Path] = sorted(DOCS.rglob(name))
    if len(hits) != 1:
        raise FileNotFoundError(f"{name}: {len(hits)} matches under {DOCS}")
    return hits[0]


# Private scratch dir for ad-hoc probe sources/binaries. A fixed name under a
# world-writable base would let any local user pre-create (or symlink) the file
# a later run compiles and executes; mkdtemp is 0700 and unique per process.
_PROBE_DIR: str | None = None


def probe_dir() -> Path:
    global _PROBE_DIR
    if _PROBE_DIR is None:
        _PROBE_DIR = tempfile.mkdtemp(prefix="probe-", dir=scratch_dir())
        atexit.register(shutil.rmtree, _PROBE_DIR, True)
    return Path(_PROBE_DIR)


def prereq(tool_names: list[str]) -> tuple[str, bool]:
    """Check run prerequisites for the named bin tools.

    Returns (message, is_skip): a missing dedicated DLL is a SKIP (nothing
    regenerable locally to assert); a missing built binary while the DLL is
    present is a FAIL carrying the build command.
    """
    if find_asm() is None:
        return (
            ("dedicated Assembly-CSharp.dll not found (set ASM=<path to Assembly-CSharp.dll>)"),
            True,
        )
    missing = [t for t in tool_names if not (BIN / t).is_file()]
    if missing:
        return (
            "bin tools not built: "
            + ", ".join(missing)
            + " (cd tools && ./build.sh --skip-legacy)",
            False,
        )
    if shutil.which("mono") is None:
        return "mono not on PATH", False
    return "", False


MONO_NOISE_PREFIXES = ("mono_thread_internal_set_priority:",)


def strip_mono_noise(text: str) -> str:
    """Drop mono's host startup chatter from captured stdout.

    Some mono builds print a thread-priority warning on stdout before any tool
    output ("mono_thread_internal_set_priority: unknown policy 5" on kernels
    whose scheduling policy mono does not know). Gates that parse stdout line
    by line must not read it as tool output.
    """
    if not text:
        return text
    return "".join(
        line for line in text.splitlines(keepends=True) if not line.startswith(MONO_NOISE_PREFIXES)
    )


def argparse_clis() -> list[Path]:
    """Maintained Python tools that parse arguments, discovered from the AST.

    Discovery, not a hand-kept list: a new CLI is covered by the help and
    argument-wiring gates the moment it exists. `ArgumentParser` is the marker
    (a help-only script has no `add_argument`).
    """
    found: list[Path] = []
    for path in sorted(TOOLS.rglob("*.py")):
        if "tests" in path.parts or "__pycache__" in path.parts:
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in {"ArgumentParser", "add_argument"}:
                found.append(path)
                break
    return found


def run_tool(exe: str, *args: str) -> tuple[int, str, str]:
    """Run bin/<exe> under mono with MONO_PATH pointing at tools/bin."""
    env = dict(os.environ, MONO_PATH=str(BIN))
    proc = subprocess.run(
        ["mono", str(BIN / exe), *args],
        capture_output=True,
        text=True,
        env=env,
    )
    return proc.returncode, strip_mono_noise(proc.stdout), proc.stderr


def compile_probe(cs_text: str, stem: str) -> str:
    """Write cs_text to a private tempdir as <stem>.cs, compile against
    bin/Mono.Cecil.dll.

    Returns the compiled exe path; a compile error raises (CalledProcessError).
    """
    d = probe_dir()
    exe = str(d / f"{stem}.exe")
    src = str(d / f"{stem}.cs")
    with open(src, "w") as f:
        f.write(cs_text)
    subprocess.run(["mcs", "-r:%s" % (BIN / "Mono.Cecil.dll"), src, "-out:" + exe], check=True)
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
    return strip_mono_noise(proc.stdout)
