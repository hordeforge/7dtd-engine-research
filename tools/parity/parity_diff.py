#!/usr/bin/env python3
"""Diff two stock ParitySurface snapshots.

Usage:
  parity_diff.py --help
  parity_diff.py old.json new.json  # what TFP changed between versions

Exit codes: 0 no wire drift (or `--help`), 1 wire/enum drift, 2 unusable input.
"""

import json
import sys
from pathlib import Path
from typing import Any


def load(p: str) -> dict[str, Any]:
    path = Path(p)
    if not path.is_file():
        # A traceback here names a JSON decoder, not the argument the caller
        # got wrong; a missing snapshot is a usage error.
        print(f"parity_diff: snapshot not found: {path}", file=sys.stderr)
        raise SystemExit(2)
    with open(p, encoding="utf-8") as fh:
        data: dict[str, Any] = json.load(fh)
    return data


def diff(old: dict[str, Any], new: dict[str, Any]) -> int:
    o, n = old["packages"], new["packages"]
    added = sorted(set(n) - set(o))
    removed = sorted(set(o) - set(n))
    changed: list[str] = []
    for k in sorted(set(o) & set(n)):
        if (
            o[k]["read"] != n[k]["read"]
            or o[k]["write"] != n[k]["write"]
            or o[k]["dir"] != n[k]["dir"]
        ):
            changed.append(k)
    print("=== PACKAGE DIFF ===")
    print(f"added ({len(added)}):", ", ".join(added) or "-")
    print(f"removed ({len(removed)}):", ", ".join(removed) or "-")
    print(f"changed wire ({len(changed)}):")
    for k in changed:
        print(f"  {k}")
        if o[k]["dir"] != n[k]["dir"]:
            print(f"    dir {o[k]['dir']} -> {n[k]['dir']}")
        if o[k]["read"] != n[k]["read"]:
            print(f"    read OLD {o[k]['read']}")
            print(f"    read NEW {n[k]['read']}")
        if o[k]["write"] != n[k]["write"]:
            print(f"    write OLD {o[k]['write']}")
            print(f"    write NEW {n[k]['write']}")
    # enum drift
    print("=== ENUM DIFF ===")
    old_enums = old.get("enums", {})
    new_enums = new.get("enums", {})
    enum_changed = 0
    for e in sorted(set(old_enums) | set(new_enums)):
        ov = old_enums.get(e)
        nv = new_enums.get(e)
        if ov != nv:
            enum_changed += 1
            print(f"  {e}: {ov} -> {nv}")
    return len(added) + len(removed) + len(changed) + enum_changed


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        sys.exit(0)
    if len(sys.argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    try:
        n = diff(load(sys.argv[1]), load(sys.argv[2]))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        # A snapshot that cannot be read is not a wire change: exit 2, so a
        # caller that reads 1 as drift (research_diff.py) does not report one.
        print(f"parity_diff: {exc}", file=sys.stderr)
        sys.exit(2)
    sys.exit(1 if n else 0)
