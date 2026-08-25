#!/usr/bin/env python3
"""Diff two stock ParitySurface snapshots.

Usage:
  parity_diff.py old.json new.json  # what TFP changed between versions
"""

import json
import sys


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def diff(old, new):
    o, n = old["packages"], new["packages"]
    added = sorted(set(n) - set(o))
    removed = sorted(set(o) - set(n))
    changed = []
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
    enum_changed = 0
    for e in sorted(set(new["enums"]) | set(old.get("enums", {}))):
        ov = old.get("enums", {}).get(e)
        nv = new["enums"].get(e)
        if ov != nv:
            enum_changed += 1
            print(f"  {e}: {ov} -> {nv}")
    return len(added) + len(removed) + len(changed) + enum_changed


if __name__ == "__main__":
    if len(sys.argv) == 3:
        n = diff(load(sys.argv[1]), load(sys.argv[2]))
        sys.exit(1 if n else 0)
    else:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
