#!/usr/bin/env python3
"""Mention-depth distribution over the hand-written narrative docs.

Counts how many times each backticked identifier occurs across narrative
docs (docs/**/*.md, excluding generated inventories/, the out-of-scope
classification, and the tool-written coverage report). Identifiers with a
leading uppercase are treated as type-shaped. The result is the depth
behind any "narrated" fraction: a type named once in passing scores
identically to one with a dedicated section, so narrated % is an upper
bound and this table is its actual shape.

Coverage.exe emits the type-level version of this table (restricted to
reached game types) into docs/inventories/coverage-report.md; this script
is the DLL-free corpus-level view and needs no assembly.

Usage: python3 tools/mention_depth.py [docsDir]
  docsDir defaults to this repo's docs/. A path that is not a directory is a
  usage error (exit 2): os.walk would yield nothing and the all-zero table
  would read as a corpus with no mentions.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections.abc import Callable, Iterator
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tooling

DEFAULT_DOCS = str(tooling.DOCS)

# Same token rule as tools/src/Coverage.cs: credit the leading identifier of
# a backticked token (`Type`, `Type.Member`, `Type::Member`).
TOKEN = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)(?:[./:][^`]*)?`")


def narrative_docs(docs_dir: str) -> Iterator[str]:
    for root, dirs, files in os.walk(docs_dir):
        norm = root.replace(os.sep, "/")
        if norm.endswith("/inventories"):
            # Prune, not just skip: a subdirectory of inventories/ is as
            # generated as the directory itself.
            dirs[:] = []
            continue
        for fn in files:
            if not fn.endswith(".md"):
                continue
            if fn in ("out-of-scope-surface.md", "coverage-report.md"):
                continue
            yield os.path.join(root, fn)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Mention-depth histogram over the narrative docs (DLL-free corpus view)."
    )
    ap.add_argument(
        "docs_dir",
        nargs="?",
        default=DEFAULT_DOCS,
        help=f"docs directory to scan (default: this repo's {DEFAULT_DOCS})",
    )
    args = ap.parse_args(argv)
    # A path that is not a directory makes os.walk yield nothing, so the table
    # comes out all zeroes and reads as a corpus with no mentions. Refuse the
    # argument instead, the way dump_diff.py refuses a bad dump dir.
    if not os.path.isdir(args.docs_dir):
        print(
            f"mention_depth: docs_dir is not a directory: {args.docs_dir}",
            file=sys.stderr,
        )
        return 2
    counts: dict[str, int] = {}
    files = 0
    for path in narrative_docs(args.docs_dir):
        files += 1
        with open(path, encoding="utf-8") as fh:
            for m in TOKEN.finditer(fh.read()):
                name = m.group(1)
                if name[0].isupper():  # type-shaped; lowercase words are prose/IL ops
                    counts[name] = counts.get(name, 0) + 1

    buckets: list[tuple[str, Callable[[int], bool]]] = [
        ("exactly 1", lambda n: n == 1),
        ("2-4", lambda n: 2 <= n <= 4),
        ("5-19", lambda n: 5 <= n <= 19),
        ("20+", lambda n: n >= 20),
    ]
    names = sorted(counts.values())
    print(
        f"Mention depth over {files} narrative docs "
        f"({len(names)} distinct type-shaped identifiers, "
        f"{sum(names)} mentions total)"
    )
    print("| Mentions | Names | Share |")
    print("|---|---:|---:|")
    total = len(names)
    for label, pred in buckets:
        n = sum(1 for c in names if pred(c))
        share = f"{100 * n / total:.0f}%" if total else "0%"
        print(f"| {label} | {n} | {share} |")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
