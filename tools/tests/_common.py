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
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

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
scratch_dir = tooling.scratch_dir
sha256_file = tooling.sha256_file
nfc = tooling.nfc
ConfigError = tooling.ConfigError
load_json = tooling.load_json
loads_json = tooling.loads_json
NonFiniteNumberError = tooling.NonFiniteNumberError


def resolve_asm(explicit: str | None) -> tuple[Path | None, str]:
    """`(path, label)`, with a broken override reported as the label.

    A gate prints the label when it skips, so a variable naming no assembly
    travels with the SKIP line instead of stopping the run in a traceback.
    """
    try:
        return tooling.resolve_asm(explicit)
    except tooling.ConfigError as exc:
        return None, str(exc)


def asm_from_argv() -> tuple[Path | None, str]:
    """`(path, label)` from the gate's optional first argument, else discovery."""
    return resolve_asm(sys.argv[1] if len(sys.argv) > 1 else None)


def run_cli(tool: Path | str, *args: str) -> "subprocess.CompletedProcess[str]":
    """Run a repo Python CLI in a subprocess with its output captured.

    Gates that drive a tool as a program (not an import) all want the same
    decoding, so it is decided once here rather than per gate.
    """
    return subprocess.run(
        [sys.executable, str(tool), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def find_asm() -> Path | None:
    """The discovered dedicated assembly, or None; a broken override says why.

    `tooling.find_asm` raises on a variable that names an install which is not
    there, because falling back to a probed root would verify a different build
    and call it a pass. A gate prints that reason on stderr and reports the
    verdict its own conventions ask for, so the operator sees the bad variable
    next to the SKIP or FAIL rather than in a traceback.
    """
    try:
        return tooling.find_asm()
    except tooling.ConfigError as exc:
        print(f"config: {exc}", file=sys.stderr)
        return None


def doc(name: str) -> Path:
    """Path of a narrative doc by basename, wherever its subsystem folder sits.

    docs/ is grouped by subsystem (docs/network/protocol.md, ...); basenames stay
    unique across the tree, so a gate cites a doc by name and never by folder.

    Both sides go through tooling.nfc: a doc committed from macOS carries an
    NFD filename, and a gate asking for the NFC spelling it was written with
    would otherwise find nothing and report a missing doc.
    """
    want = tooling.nfc(name)
    hits: list[Path] = sorted(p for p in DOCS.rglob("*.md") if tooling.nfc(p.name) == want)
    if len(hits) != 1:
        raise FileNotFoundError(f"{name}: {len(hits)} matches under {DOCS}")
    return hits[0]


def load_sibling(name: str) -> Any:
    """Import another tools/tests script as a module, by its script name.

    The tests are standalone scripts, not an importable package, so a test that
    borrows another's encoder imports it by file path.
    """
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(f"{name}.py"))
    assert spec is not None, name
    assert spec.loader is not None, name
    sibling: Any = importlib.util.module_from_spec(spec)
    sys.modules[name] = sibling
    spec.loader.exec_module(sibling)
    return sibling


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
    regenerable locally to assert); an override that names no assembly is a
    FAIL, because the run was pointed at an install and got none; a missing
    built binary while the DLL is present is a FAIL carrying the build command.
    """
    try:
        asm = tooling.find_asm()
    except tooling.ConfigError as exc:
        return (str(exc), False)
    if asm is None:
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
    rc, out, err = tooling.run_mono(exe, *args)
    return rc, strip_mono_noise(out), err


def compile_probe(cs_text: str, stem: str) -> str:
    """Write cs_text to a private tempdir as <stem>.cs, compile against
    bin/Mono.Cecil.dll.

    Returns the compiled exe path; a compile error raises (CalledProcessError).
    """
    d = probe_dir()
    exe = str(d / f"{stem}.exe")
    src = str(d / f"{stem}.cs")
    with open(src, "w", encoding="utf-8") as f:
        f.write(cs_text)
    subprocess.run(
        ["mcs", "-r:%s" % (BIN / "Mono.Cecil.dll"), src, "-out:" + exe],
        check=True,
        timeout=tooling.mono_timeout(),
    )
    return exe


def run_probe(exe: str, *args: str) -> str:
    """Run a compiled probe under mono with MONO_PATH wired; returns stdout.

    A wedged probe fails the gate through the shared bound rather than hanging
    it: a nonzero rc (including the timeout rc) raises here, which is what
    `check=True` used to do for the ordinary failure cases.
    """
    rc, out, err = tooling.run_bounded(["mono", exe, *args], env=tooling.mono_env())
    if rc != 0:
        raise subprocess.CalledProcessError(rc, ["mono", exe, *args], out, err)
    return strip_mono_noise(out)
