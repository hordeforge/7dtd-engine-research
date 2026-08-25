#!/usr/bin/env python3
"""Ensure the RE tool bootstrap discovers a normal system Mono.Cecil install."""

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
        text = (ROOT / "tools" / script).read_text(encoding="utf-8")
        assert "unknown argument" in text
        assert "choose one mode" in text
    assert "standard Mono GAC" in docs
    print("OK: tool bootstrap searches the system Mono.Cecil GAC")


if __name__ == "__main__":
    main()
