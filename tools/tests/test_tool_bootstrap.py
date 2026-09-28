#!/usr/bin/env python3
"""Ensure the RE tool bootstrap discovers a normal system Mono.Cecil install."""

import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

ROOT = _common.REPO


def check_gac_probe_reads_a_path(build: str) -> None:
    """The GAC probe must answer with a path, or with nothing.

    `gacutil -l Mono.Cecil` lists identity lines and no path on a stock
    mono, so the probe once took their last field and returned
    "PublicKeyToken=...": a string that is never a file, silently dropped by
    the `-f` candidate test, leaving every host to fall through to the Linux
    GAC paths and the macOS/Windows GAC unfound. Pinned here against both
    shapes of gacutil output, with the expression read from build.sh so the
    test follows the script instead of restating it.
    """
    match = re.search(r"sed -n '(s/\^Path: //p)'", build)
    assert match is not None, "build.sh no longer parses the GAC probe out of gacutil"
    expression = match.group(1)
    identity_only = (
        "The following assemblies are installed into the GAC:\n"
        "Mono.Cecil, Version=0.11.1.0, Culture=neutral, PublicKeyToken=0738eb9f132ed756\n"
        "Number of items = 1\n"
    )
    gac_path = "/opt/mono gac/Mono.Cecil/0.11.1.0_abc/Mono.Cecil.dll"
    with_paths = identity_only.replace(
        "Number of items = 1\n",
        f"Path: {gac_path}\nNumber of items = 1\n",
    )
    with tempfile.TemporaryDirectory(prefix="gac-probe-", dir=_common.scratch_dir()) as td:
        for label, output, expected in (
            ("identity-only", identity_only, ""),
            ("with-paths", with_paths, gac_path),
        ):
            fixture = Path(td) / f"{label}.txt"
            fixture.write_text(output, encoding="utf-8")
            result = _common.run_cmd(["sed", "-n", expression, fixture], check=True)
            assert result.stdout.strip() == expected, (
                f"gacutil probe answered {result.stdout.strip()!r}, not {expected!r}"
            )


def main() -> None:
    build = (ROOT / "tools" / "build.sh").read_text(encoding="utf-8")
    docs = (ROOT / "tools" / "README.md").read_text(encoding="utf-8")
    check_gac_probe_reads_a_path(build)
    assert "/usr/lib/mono/gac/Mono.Cecil/*/Mono.Cecil.dll" in build
    assert "/usr/local/lib/mono/gac/Mono.Cecil/*/Mono.Cecil.dll" in build
    assert "$HOME/Desktop/" not in build
    # Every file build.sh compiles or copies into before renaming it into bin/
    # must live under this run's staging directory. A fixed
    # bin/.staging/<final-name> is one shared path, and two builds at once then
    # rm each other's staged file mid-compile and rename what is left into
    # bin/: measured with six concurrent rm/mcs/mv runs over one staged path,
    # four of the six landed no exe at all ("Cannot open assembly").
    assert 'staging_run="bin/.staging/run.$$"' in build, "build.sh stages no per-run directory"
    shared_stage = [
        line.strip()
        for line in build.splitlines()
        if re.search(r'\bstaged(_cecil)?="', line) and "staging_run" not in line
    ]
    assert not shared_stage, f"build.sh stages into a path shared between runs: {shared_stage}"
    assert 'mktemp "$here/data/.cecil.pin.' in (ROOT / "tools" / "cecil-pin.sh").read_text(
        encoding="utf-8"
    )
    regen = (ROOT / "tools" / "regen.sh").read_text(encoding="utf-8")
    assert 'ASM="$asm" ./tools/stock-sync.sh' in regen
    assert "regen: FAILED (one or more canonical legacy dump sets" in regen
    for script in ("post-update.sh", "stock-sync.sh"):
        path = ROOT / "tools" / script
        text = path.read_text(encoding="utf-8")
        assert "unknown argument" in text
        assert "choose one mode" in text
        assert _common.run_cmd([path, "--bad-option"], capture_output=True).returncode == 2
        assert (
            _common.run_cmd(
                [path, "--check-only", "--extract-only"], capture_output=True
            ).returncode
            == 2
        )
    post_update = (ROOT / "tools" / "post-update.sh").read_text(encoding="utf-8")
    assert post_update.count("DO_DRIFT=0") == 3
    stock_sync = (ROOT / "tools" / "stock-sync.sh").read_text(encoding="utf-8")
    assert 'mktemp -d "$DATA/.stock-sync.' in stock_sync
    assert '--pins "$tmpdir/xml_pins.json"' in stock_sync
    fetch = ROOT / "tools" / "steam" / "fetch_version.sh"
    fetch_text = fetch.read_text(encoding="utf-8")
    assert "curl " not in fetch_text
    assert 'python3 -m json.tool "$tmp"' in fetch_text
    assert _common.run_cmd([fetch, "public", "../escape"], capture_output=True).returncode == 2
    assert "standard Mono GAC" in docs
    print("OK: tool bootstrap searches the system Mono.Cecil GAC")


if __name__ == "__main__":
    main()
