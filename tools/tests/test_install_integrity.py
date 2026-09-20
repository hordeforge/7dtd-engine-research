#!/usr/bin/env python3
"""The installed managed payload must be Steam's bytes, and the installed build must be the studied one.

`make stock-check` re-extracts the studied DLL's facts and would catch a patched
`Assembly-CSharp.dll`, but nothing in the suite looked at the rest of the
managed payload: a hand-built `LiteNetLib.dll` or an experiment left in
`Managed/` changes wire and runtime research without failing any gate. The
cached depot manifest has SHA-1s for all of it, so this gate asks the build tool
for the verdict (`--check --verify-install Managed`) and asserts a clean install.

It also asserts the installed build *is* the studied one: the appmanifest's
build id and depot manifest must equal `tools/data/steam_builds.json`. An
asset-only TFP patch moves the installed build without changing the studied
DLL's facts, so `make stock-check` would stay green while every doc still cites
the previous build; this is the gate that notices, and the fix is to review and
re-record the pin (`steam_builds.py --record`).

SKIPs when the manifest for the installed build is not cached (steamcmd
installs, or a machine that never ran the Steam client).

Usage: python3 tools/tests/test_install_integrity.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOL = _common.TOOLS / "parity" / "steam_builds.py"


def main() -> None:
    if _common.find_asm() is None:
        print("SKIP: dedicated Assembly-CSharp.dll not found")
        return
    if shutil.which("mono") is None or not (_common.BIN / "Mono.Cecil.dll").is_file():
        print("SKIP: steam_builds needs mono and the built tools")
        return
    result = subprocess.run(
        [sys.executable, str(TOOL), "--check", "--verify-install", "Managed", "--json"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 2 and "no cached manifest" in result.stderr:
        print("SKIP: no cached depot manifest for the installed build")
        return
    assert result.returncode == 0, (result.stdout[-400:], result.stderr[-400:])
    payload = json.loads(result.stdout)
    integrity = payload.get("integrity")
    assert integrity, payload
    assert integrity["missing"] == 0, integrity
    assert integrity["mismatch"] == 0, integrity
    assert integrity["ok"] > 0, integrity
    installed = payload["installed"]["manifest"]
    assert installed, payload["installed"]
    assert installed in integrity["manifest"], (installed, integrity)

    pins = json.loads((_common.TOOLS / "data" / "steam_builds.json").read_text(encoding="utf-8"))
    studied = pins["studied"]
    assert payload["installed"]["buildid"] == studied["buildid"], (
        f"installed build {payload['installed']['buildid']} != studied pin "
        f"{studied['buildid']}; review the new build, then re-record the pin with "
        "steam_builds.py --record"
    )
    assert installed == studied["manifest"], (
        f"installed manifest {installed} != studied pin {studied['manifest']}; "
        "review the new build, then re-record the pin with steam_builds.py --record"
    )
    print(
        f"OK: managed payload matches Steam's manifest "
        f"({integrity['ok']} files, build {payload['installed']['buildid']})"
    )


if __name__ == "__main__":
    main()
