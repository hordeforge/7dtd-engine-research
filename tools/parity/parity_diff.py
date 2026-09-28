#!/usr/bin/env python3
"""Diff two stock ParitySurface snapshots.

Usage:
  parity_diff.py --help
  parity_diff.py old.json new.json  # what TFP changed between versions

Exit codes: 0 no wire drift (or `--help`), 1 wire/enum drift, 2 unusable input.
The report is the tool's output, so it goes to stdout; only the refusals and
the usage errors go to stderr, and `drift-check.sh` reads the report from
stdout with the exit code as the verdict.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tooling


def load(p: str) -> dict[str, Any]:
    path = Path(p)
    if not path.is_file():
        # A traceback here names a JSON decoder, not the argument the caller
        # got wrong; a missing snapshot is a usage error.
        print(f"parity_diff: snapshot not found: {path}", file=sys.stderr)
        raise SystemExit(2)
    try:
        data: dict[str, Any] = tooling.load_json(path)
    except (ValueError, OSError) as exc:
        print(f"parity_diff: unreadable snapshot {path}: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
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


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Diff two stock ParitySurface snapshots (NetPackage wire + enums).",
        epilog="exit 0 = no drift, 1 = wire/enum drift, 2 = unusable input",
    )
    ap.add_argument("old", help="older ParitySurface snapshot (JSON)")
    ap.add_argument("new", help="newer ParitySurface snapshot (JSON)")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        n = diff(load(args.old), load(args.new))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        # A snapshot that cannot be read is not a wire change: exit 2, so a
        # caller that reads 1 as drift (research_diff.py) does not report one.
        print(f"parity_diff: {exc}", file=sys.stderr)
        return 2
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
