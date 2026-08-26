#!/usr/bin/env python3
"""Pin sandbox.safe_name: bundle-supplied asset names stay inside the out-dir.

extract_mesh_atlas.py writes <m_Name>.xml for every TextAsset in a game
bundle; m_Name comes from the file, not the filesystem. safe_name is the
Python twin of src/IlFmt.cs Safe (see tests/test_ilfmt_safe.py): separators
and hostile characters become '_', dots survive for namespace-style names,
and a fragment that is empty or wholly '.'/'..' is prefixed so os.path.join
can never produce a parent-directory component. Stdlib only, DLL-free.
"""

from __future__ import annotations

import importlib.util
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOLS = _common.TOOLS

_spec = importlib.util.spec_from_file_location("safe_name", TOOLS / "sandbox" / "safe_name.py")
assert _spec is not None
assert _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
safe_name = _mod.safe_name

# (hostile name, expected sanitized fragment) -- mirrors the IlFmt cases.
CASES = [
    ("..", "_.."),
    (".", "_."),
    ("../x", ".._x"),
    ("/etc/passwd", "_etc_passwd"),
    ("Foo/Bar\\Baz", "Foo_Bar_Baz"),
    ("MeshDescription.MetaData", "MeshDescription.MetaData"),  # dots survive
    ("ta_grassxml", "ta_grassxml"),
    ("a:b<c>", "a_b_c_"),
    ("", "_"),
]


def main() -> int:
    base = TOOLS.parent / ".scratch" / "sandbox-safe-name"
    base.mkdir(parents=True, exist_ok=True)
    root = f"{base.resolve()}{os.sep}"

    bad = False
    fragments: dict[str, str] = {}
    for name, _ in CASES:
        frag = safe_name(name)
        fragments[name] = frag
        full = os.path.realpath(os.path.join(str(base), frag + ".xml"))
        if not full.startswith(root):
            print(f"FAIL: {name!r} -> {frag!r} escapes {base}", file=sys.stderr)
            bad = True
    for name, want in CASES:
        if fragments[name] != want:
            print(
                f"FAIL: safe_name({name!r}) = {fragments[name]!r}, want {want!r}", file=sys.stderr
            )
            bad = True
    if bad:
        return 1
    print(
        f"OK: sandbox.safe_name contains all {len(CASES)} hostile fragments "
        f"below the out dir; dots preserved"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
