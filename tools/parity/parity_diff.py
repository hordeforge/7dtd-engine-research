#!/usr/bin/env python3
"""Diff two ParitySurface snapshots and/or report zdtd coverage.

Usage:
  parity_diff.py old.json new.json          # what TFP changed between versions
  parity_diff.py --coverage new.json GAMEDIR # what zdtd handles vs stock
"""
import json, sys, re, subprocess, os

def load(p): return json.load(open(p))

def diff(old, new):
    o, n = old["packages"], new["packages"]
    added = sorted(set(n) - set(o))
    removed = sorted(set(o) - set(n))
    changed = []
    for k in sorted(set(o) & set(n)):
        if o[k]["read"] != n[k]["read"] or o[k]["write"] != n[k]["write"] or o[k]["dir"] != n[k]["dir"]:
            changed.append(k)
    print(f"=== PACKAGE DIFF ===")
    print(f"added ({len(added)}):", ", ".join(added) or "-")
    print(f"removed ({len(removed)}):", ", ".join(removed) or "-")
    print(f"changed wire ({len(changed)}):")
    for k in changed:
        print(f"  {k}")
        if o[k]["dir"] != n[k]["dir"]: print(f"    dir {o[k]['dir']} -> {n[k]['dir']}")
        if o[k]["read"] != n[k]["read"]:
            print(f"    read OLD {o[k]['read']}")
            print(f"    read NEW {n[k]['read']}")
        if o[k]["write"] != n[k]["write"]:
            print(f"    write OLD {o[k]['write']}")
            print(f"    write NEW {n[k]['write']}")
    # enum drift
    print(f"=== ENUM DIFF ===")
    for e in sorted(set(new["enums"]) | set(old.get("enums", {}))):
        ov = old.get("enums", {}).get(e); nv = new["enums"].get(e)
        if ov != nv: print(f"  {e}: {ov} -> {nv}")
    return len(added) + len(removed) + len(changed)

def coverage(new, gamedir):
    # which packages zdtd's game.zig handles + which our default_mappings names
    src = os.path.join(gamedir, "src/server/game.zig")
    txt = open(src).read()
    handled = set(re.findall(r'std\.mem\.eql\(u8, name, "(NetPackage\w+)"\)', txt))
    stock = set(new["packages"])
    # weight by direction: dir 1 (ToServer) = client sends it, must handle
    tosrv = {k for k,v in new["packages"].items() if v["dir"] == 1}
    missing_c2s = sorted(tosrv - handled)
    print(f"=== ZDTD COVERAGE ===")
    print(f"stock packages: {len(stock)}  handled in game.zig: {len(handled & stock)}")
    print(f"client->server (dir=1) packages: {len(tosrv)}")
    print(f"UNHANDLED client->server ({len(missing_c2s)}):")
    for k in missing_c2s: print(f"  {k}  read={new['packages'][k]['read'][:80]}")

if __name__ == "__main__":
    if sys.argv[1] == "--coverage":
        coverage(load(sys.argv[2]), sys.argv[3])
    else:
        n = diff(load(sys.argv[1]), load(sys.argv[2]))
        sys.exit(1 if n else 0)
