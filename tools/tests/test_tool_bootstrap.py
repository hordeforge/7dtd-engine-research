#!/usr/bin/env python3
"""Ensure the RE tool bootstrap discovers a normal system Mono.Cecil install."""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    build = (ROOT / "tools" / "build.sh").read_text(encoding="utf-8")
    docs = (ROOT / "tools" / "README.md").read_text(encoding="utf-8")
    assert "/usr/lib/mono/gac/Mono.Cecil/*/Mono.Cecil.dll" in build
    assert "/usr/local/lib/mono/gac/Mono.Cecil/*/Mono.Cecil.dll" in build
    assert "$HOME/Desktop/" not in build
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
        assert subprocess.run([path, "--bad-option"], capture_output=True).returncode == 2
        assert (
            subprocess.run([path, "--check-only", "--extract-only"], capture_output=True).returncode
            == 2
        )
    post_update = (ROOT / "tools" / "post-update.sh").read_text(encoding="utf-8")
    assert post_update.count("DO_DRIFT=0") == 3
    stock_sync = (ROOT / "tools" / "stock-sync.sh").read_text(encoding="utf-8")
    assert 'mktemp -d "$DATA/.stock-sync.' in stock_sync
    assert '--pins "$tmpdir/xml_pins.json"' in stock_sync
    fetch = ROOT / "tools" / "parity" / "fetch_version.sh"
    fetch_text = fetch.read_text(encoding="utf-8")
    assert "curl " not in fetch_text
    assert 'python3 -m json.tool "$tmp"' in fetch_text
    assert subprocess.run([fetch, "public", "../escape"], capture_output=True).returncode == 2
    assert "standard Mono GAC" in docs
    print("OK: tool bootstrap searches the system Mono.Cecil GAC")


if __name__ == "__main__":
    main()
