#!/usr/bin/env python3
"""Ensure the RE tool bootstrap discovers a normal system Mono.Cecil install."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    build = (ROOT / "tools" / "build.sh").read_text(encoding="utf-8")
    docs = (ROOT / "tools" / "README.md").read_text(encoding="utf-8")
    assert "/usr/lib/mono/gac/Mono.Cecil/*/Mono.Cecil.dll" in build
    assert "/usr/local/lib/mono/gac/Mono.Cecil/*/Mono.Cecil.dll" in build
    assert "standard Mono GAC" in docs
    print("OK: tool bootstrap searches the system Mono.Cecil GAC")


if __name__ == "__main__":
    main()
