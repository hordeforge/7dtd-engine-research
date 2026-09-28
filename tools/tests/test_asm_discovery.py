#!/usr/bin/env python3
"""tooling.asm_candidates: the dedicated install is found on every Steam OS.

The dedicated server ships as a Steam app, and Steam's library root differs per
OS (Program Files on Windows, ~/Library/Application Support on macOS, ~/.local
or ~/.steam on Linux). Discovery probes all of them, so the cases below build a
tree per layout and assert the assembly resolves without the operator handing
over ASM. `tools/asm_path.py` prints that resolution for the Makefile and the
shell entry points, and the cases cover it: the assembly, the install root with
`--game-dir`, and an override that points at nothing failing rather than falling
through to a probed root. Stdlib only, no DLL, no game install.

Usage: python3 tools/tests/test_asm_discovery.py
"""

from __future__ import annotations

import contextlib
import os
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common
import tooling


def _install(root: Path) -> Path:
    """Create <root>/<steamapps/common/game>/<Managed>/Assembly-CSharp.dll."""
    dll = root.joinpath(*tooling.STEAM_COMMON, tooling.GAME_DIR, *tooling.MANAGED, tooling.ASM_NAME)
    dll.parent.mkdir(parents=True, exist_ok=True)
    dll.write_bytes(b"MZ")
    return dll


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"MZ")
    return path


def check_roots(home: Path) -> bool:
    """Every OS layout probed at once, all from one fake environment."""
    # Keys are the literal env / home-layout names asm_candidates resolves, so
    # a name duplicated across the two constant lists collapses here and the
    # count check below is what catches it.
    roots: dict[str, str] = {
        name: str(home.parent / "steam" / name) for name in tooling.STEAM_ROOT_ENV
    }
    roots.update({layout: str(home / layout) for layout in tooling.STEAM_ROOTS_HOME})
    planted = [_install(Path(root)) for root in roots.values()]

    ok = True
    candidates = tooling.asm_candidates(roots, home)
    missing = [str(dll) for dll in planted if dll not in candidates]
    if missing:
        print(f"FAIL: no candidate for Steam roots: {missing}", file=sys.stderr)
        ok = False
    declared = len(tooling.STEAM_ROOT_ENV) + len(tooling.STEAM_ROOTS_HOME)
    if len(roots) != declared:
        print(
            f"FAIL: a declared Steam root was not exercised: {len(roots)} probed, {declared} declared",
            file=sys.stderr,
        )
        ok = False
    return ok


def check_overrides(home: Path) -> bool:
    """An env var wins over a probed root, as a file or as an install directory."""
    base = home.parent
    explicit = _touch(base / "explicit" / "Assembly-CSharp.dll")
    expand_root = base / "install-root"
    expanded = _touch(expand_root.joinpath(*tooling.MANAGED, tooling.ASM_NAME))
    probed = _install(home / tooling.STEAM_ROOTS_HOME[-1])

    by_file = tooling.asm_candidates({"ASM": str(explicit)}, home)
    by_dir = tooling.asm_candidates({"SEVENDTD_DS_DIR": str(expand_root)}, home)
    ok = True
    if by_file[0] != explicit:
        print(f"FAIL: ASM file override is not first: {by_file[:1]}", file=sys.stderr)
        ok = False
    if expanded not in by_dir:
        print(f"FAIL: directory override not expanded: {by_dir[:1]}", file=sys.stderr)
        ok = False
    if by_file[-1] != probed:
        print(f"FAIL: a probed root did not follow the overrides: {by_file[-1:]}", file=sys.stderr)
        ok = False
    return ok


def check_shared_roots() -> bool:
    """The Steam tools scan the same root list, so a new layout is honoured twice."""
    sys.path.insert(0, str(_common.TOOLS / "steam"))
    import steam_manifest

    roots = tooling.steam_roots(os.environ, Path.home())
    ok = True
    if not set(roots) <= set(steam_manifest.STEAM_ROOTS):
        print("FAIL: steam_manifest.STEAM_ROOTS dropped a shared root", file=sys.stderr)
        ok = False
    return ok


def check_game_dir() -> bool:
    """`tooling.game_dir` maps an install assembly to its root, and refuses a loose one."""
    root = Path("/srv/7 Days to Die Dedicated Server")
    managed = root.joinpath(*tooling.MANAGED, tooling.ASM_NAME)
    loose = Path("/scratch/Assembly-CSharp.dll")
    ok: bool = tooling.game_dir(managed) == root
    if not ok:
        print(
            f"FAIL: game_dir of an install assembly: {tooling.game_dir(managed)}", file=sys.stderr
        )
    if tooling.game_dir(loose) is not None:
        print(f"FAIL: game_dir invented a root for {loose}", file=sys.stderr)
        ok = False
    return ok


def run_resolver(env: dict[str, str], *args: str) -> tuple[int, str]:
    """Run tools/asm_path.py with `env` as the whole environment but PATH."""
    result = subprocess.run(
        [sys.executable, str(_common.TOOLS / "asm_path.py"), *args],
        env={"PATH": os.environ.get("PATH", "")} | env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    return result.returncode, result.stdout.strip()


def check_resolver() -> bool:
    """The printable resolution the Makefile and the shell entry points call.

    Three shapes matter: the discovered install prints its assembly, the same
    run with --game-dir prints the root holding Data/Config, and an override
    that points at nothing exits 2 instead of falling through to whatever the
    host happens to have installed.
    """
    ok = True
    with tempfile.TemporaryDirectory(prefix="asm-resolver-", dir=_common.scratch_dir()) as td:
        base = Path(td)
        dll = _install(base / "steam")
        env = {
            "SEVENDTD_DS_DIR": str(
                base
                / "steam"
                / tooling.STEAM_COMMON[0]
                / tooling.STEAM_COMMON[1]
                / tooling.GAME_DIR
            )
        }
        rc, out = run_resolver(env)
        if (rc, out) != (0, str(dll)):
            print(f"FAIL: resolver assembly: rc={rc} out={out!r}, want {dll}", file=sys.stderr)
            ok = False
        rc, out = run_resolver(env, "--game-dir")
        want = base / "steam" / tooling.STEAM_COMMON[0] / tooling.STEAM_COMMON[1] / tooling.GAME_DIR
        if (rc, out) != (0, str(want)):
            print(f"FAIL: resolver game dir: rc={rc} out={out!r}, want {want}", file=sys.stderr)
            ok = False
        rc, out = run_resolver({"ASM": str(base / "absent" / "Assembly-CSharp.dll")})
        if rc != 2 or out:
            print(
                f"FAIL: a missing ASM override must fail, not fall through: rc={rc} {out!r}",
                file=sys.stderr,
            )
            ok = False
    return ok


def check_broken_override() -> bool:
    """`tooling.find_asm` raises rather than answering with another install.

    The gates are the reason: a pin run pointed at a build that is not there
    would otherwise discover whatever Steam root the host carries, verify that
    build's pins, and print a pass. Every override variable is checked, with
    and without a probed install present, and the gate-facing wrappers must
    turn the raise into a message instead of a traceback.
    """
    ok = True
    with tempfile.TemporaryDirectory(prefix="asm-override-", dir=_common.scratch_dir()) as td:
        base = Path(td)
        home = base / "home"
        home.mkdir()
        # A probed install is present, so a silent fall-through would find it.
        _install(home / tooling.STEAM_ROOTS_HOME[-1])
        for name in tooling.ASM_VARS:
            for value in (base / "absent", base / "absent" / tooling.ASM_NAME):
                with env_var(name, str(value)):
                    try:
                        tooling.find_asm()
                    except tooling.ConfigError as exc:
                        if name not in str(exc) or str(value) not in str(exc):
                            print(
                                f"FAIL: {exc} names neither the variable nor the path",
                                file=sys.stderr,
                            )
                            ok = False
                        continue
                    print(f"FAIL: {name}={value} fell through to another install", file=sys.stderr)
                    ok = False
                # The gate wrappers answer with the reason, not a traceback.
                with env_var(name, str(value)):
                    if _common.find_asm() is not None:
                        print(
                            f"FAIL: _common.find_asm used another install for {name}",
                            file=sys.stderr,
                        )
                        ok = False
                    path, label = _common.resolve_asm(None)
                    if path is not None or name not in label:
                        print(
                            f"FAIL: _common.resolve_asm label for {name}: {label!r}",
                            file=sys.stderr,
                        )
                        ok = False
        # No override at all: discovery answers without raising, whatever this
        # host has installed, and an empty value is not read as an override.
        for unset in ("", None):
            with env_var("ASM", unset):
                try:
                    asm = tooling.find_asm()
                except tooling.ConfigError as exc:
                    print(f"FAIL: ASM={unset!r} raised {exc}", file=sys.stderr)
                    ok = False
                    continue
                if asm is not None and base in asm.parents:
                    print(f"FAIL: ASM={unset!r} resolved to a fixture path: {asm}", file=sys.stderr)
                    ok = False
    return ok


@contextlib.contextmanager
def env_var(name: str, value: str | None) -> "Iterator[None]":
    """Set (or clear, for None) one environment variable for the block."""
    saved = os.environ.get(name)
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value
    try:
        yield
    finally:
        if saved is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = saved


def main() -> int:
    bad = False
    with tempfile.TemporaryDirectory(prefix="asm-discovery-", dir=_common.scratch_dir()) as td:
        base = Path(td)
        home = base / "home"
        home.mkdir()
        if not check_roots(home):
            bad = True
        if not check_overrides(home):
            bad = True
    if not check_shared_roots():
        bad = True
    if not check_game_dir():
        bad = True
    if not check_resolver():
        bad = True
    if not check_broken_override():
        bad = True
    if bad:
        return 1
    total = len(tooling.STEAM_ROOT_ENV) + len(tooling.STEAM_ROOTS_HOME)
    print(f"OK: assembly discovery covers {total} Steam roots and both override forms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
