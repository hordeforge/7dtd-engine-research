"""Filesystem-safe filename fragment for game/assembly-supplied names.

Python twin of tools/src/IlFmt.cs `Safe`: letters, digits, underscore and dot
pass; every other character becomes '_'. Dots survive so namespace-style
names stay readable, which means a fragment that is empty or wholly '.'/'..'
would combine into a parent-directory component under os.path.join; prefix
'_' to pin every fragment strictly below the caller's output directory.
"""
from __future__ import annotations


def safe_name(s: str) -> str:
    t = "".join(c if c.isalnum() or c in "_." else "_" for c in s)
    return f"_{t}" if not t or t in (".", "..") else t
