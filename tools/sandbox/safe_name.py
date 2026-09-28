"""Filesystem-safe filename fragment for game/assembly-supplied names.

Python twin of tools/src/IlFmt.cs `Safe`: ASCII letters, digits, underscore and
dot pass; every other character becomes '_'. Dots survive so namespace-style
names stay readable, which means a fragment that is empty or wholly '.'/'..'
would combine into a parent-directory component under os.path.join; prefix
'_' to pin every fragment strictly below the caller's output directory.

ASCII only, where the C# twin reads the name as UTF-16 code units and would
take each surrogate half of an astral character separately: an astral
character becomes two '_' here for the same reason it does there. Letting
Unicode letters through made the output filename depend on the host: a name
macOS hands back decomposed is a different byte string on Linux, and a
filesystem that normalizes filenames folds two assets whose names differ only
in normalization onto one file, which then reads as a duplicate name. Names
are identifiers here, so the fragment is one fixed alphabet on every host.
"""

from __future__ import annotations

_ASCII_ALNUM = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
_BMP_MAX = 0xFFFF


def safe_name(s: str) -> str:
    parts: list[str] = []
    for c in s:
        parts.append("__" if ord(c) > _BMP_MAX else c if c in _ASCII_ALNUM or c in "_." else "_")
    t = "".join(parts)
    return f"_{t}" if not t or t in (".", "..") else t
