#!/usr/bin/env python3
"""tooling.asm_candidates: the dedicated install is found on every Steam OS.

The dedicated server ships as a Steam app, and Steam's library root differs per
OS (Program Files on Windows, ~/Library/Application Support on macOS, ~/.local
or ~/.steam on Linux). Discovery probes all of them, so the cases below build a
tree per layout and assert the assembly resolves without the operator handing
over ASM. Stdlib only, no DLL, no game install.

Usage: python3 tools/tests/test_asm_discovery.py
"""

from __future__ import annotations

import os
import sys
import tempfile
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


def check_roots(home: Path) -> None:
    """Every OS layout probed at once, all from one fake environment."""
    roots: dict[str, str] = {
        name: str(home.parent / "steam" / name) for name in tooling.STEAM_ROOT_ENV
    }
    roots.update({layout: str(home / layout) for layout in tooling.STEAM_ROOTS_HOME})
    planted = [_install(Path(root)) for root in roots.values()]

    candidates = tooling.asm_candidates(roots, home)
    missing = [str(dll) for dll in planted if dll not in candidates]
    if missing:
        print(f"FAIL: no candidate for Steam roots: {missing}", file=sys.stderr)
    if len(roots) != len(tooling.STEAM_ROOT_ENV) + len(tooling.STEAM_ROOTS_HOME):
        print("FAIL: a declared Steam root was not exercised", file=sys.stderr)


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


def main() -> int:
    bad = False
    with tempfile.TemporaryDirectory(prefix="asm-discovery-", dir=_common.scratch_dir()) as td:
        base = Path(td)
        home = base / "home"
        home.mkdir()
        check_roots(home)
        if not check_overrides(home):
            bad = True
    if not check_shared_roots():
        bad = True
    if bad:
        return 1
    total = len(tooling.STEAM_ROOT_ENV) + len(tooling.STEAM_ROOTS_HOME)
    print(f"OK: assembly discovery covers {total} Steam roots and both override forms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
