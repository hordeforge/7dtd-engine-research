#!/usr/bin/env python3
"""Verify sibling-repo RESEARCH citations resolve against this corpus.

The sibling repos (zdtd-server, 7dtd-server-optimizer, 7dtd-loadgen,
7dtd-realearth, 7dtd-server-apm) map their values and behaviors back to the stock
dedicated server through the research docs. This gate extracts every EXPLICIT research
citation - an `RE:` marker or a `7dtd-engine-research/docs/` path prefix - from each
sibling and checks the cited file exists in this repo's docs/. Bare names of a
sibling's OWN docs are not research citations and are ignored (resolved
against that repo's docs/ + root + zdtd-server docs/adr).

Usage: python3 tools/zdtd_cite_check.py [--root <workspace>]
  --root defaults to the parent of this repo (the sibling layout root).
Exit 0 when every research citation resolves; 1 with the broken list otherwise.
"""

import argparse
import os
import re
import sys

REPOS = [
    "zdtd-server",
    "7dtd-server-optimizer",
    "7dtd-loadgen",
    "7dtd-realearth",
    "7dtd-server-apm",
]
RES_PATH = re.compile(r"(?:(?:\.\./)*7dtd-engine-research/docs/)([A-Za-z0-9][A-Za-z0-9_-]+\.md)")
BARE_AFTER_RE = re.compile(
    r"RE(?::|\s+)(?:../7dtd-engine-research/docs/)?([A-Za-z0-9][A-Za-z0-9_-]+\.md)"
)
BARE = re.compile(r"(?<![\w./-])([A-Za-z0-9][A-Za-z0-9_-]+\.md)(?![A-Za-z0-9])")
# Known non-citation bare names: report/artifact filenames emitted by tools
# (not references to docs that must resolve).
ALLOW_BARE = {"csharp_bridge.md", "compare.md", "REPORT.md", "CONSOLIDATED.md", "bench-stock.md"}
SKIP_DIRS = {
    ".git",
    ".zig-cache",
    ".claude",
    "zig-pkg",
    "node_modules",
    ".venv",
    "bin",
    "obj",
    "__pycache__",
    "target",
    "dist",
    "build",
    ".pytest_cache",
    ".uv-cache",
    ".cache",
}
SRC_EXTS = {".zig", ".cs", ".rs", ".py", ".ts", ".js", ".go"}


def docs_dir() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")


def known_doc_names() -> set:
    """Every docs/ filename in this repo (top level + nested inventories),
    resolved once.

    The scan tests every citation against this set; an isfile per match made
    the walk pay one syscall per citation over whole sibling repos. Nested
    trees count: docs/inventories/netpackage-bodies.md is a research doc, so
    an `RE netpackage-bodies.md` marker must resolve against its basename.
    """
    ddir = docs_dir()
    names = set()
    try:
        for _dirpath, dirnames, filenames in os.walk(ddir):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for n in filenames:
                if n.endswith(".md"):
                    names.add(n)
    except OSError:
        return set()
    return names


def collect_local(root: str, into: set) -> None:
    """Every repo-local doc name across the fleet (roots, the full docs/ tree
    incl. nested dirs like docs/reviews/, and docs/adr names prefix-stripped),
    so cross-repo-local references resolve."""
    for d in os.listdir(root):
        if d.endswith(".md"):
            into.add(d)
    ddir = os.path.join(root, "docs")
    if os.path.isdir(ddir):
        for _dirpath, dirnames, filenames in os.walk(ddir):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if fn.endswith(".md"):
                    into.add(fn)
        adr = os.path.join(ddir, "adr")
        if os.path.isdir(adr):
            for d in os.listdir(adr):
                if d.endswith(".md"):
                    into.add(re.sub(r"^\d+-", "", d))


def scan(root: str, local: set, docs: set) -> tuple[int, list[str]]:
    total = 0
    broken = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not (fn.endswith(".md") or any(fn.endswith(e) for e in SRC_EXTS)):
                continue
            p = os.path.join(dirpath, fn)
            try:
                with open(p, encoding="utf-8", errors="replace") as fh:
                    txt = fh.read()
            except OSError:
                continue
            for pat in (RES_PATH, BARE_AFTER_RE):
                for m in pat.finditer(txt):
                    total += 1
                    if m.group(1) not in docs:
                        broken.append(f"{p}: cites {m.group(1)}")
            # src files: a bare `X.md` name must be a research doc or a
            # repo-local doc (incl. zdtd docs/adr stripped).
            if any(fn.endswith(e) for e in SRC_EXTS):
                for m in BARE.finditer(txt):
                    name = m.group(1)
                    if name in local or name in ALLOW_BARE:
                        continue
                    total += 1
                    if name not in docs:
                        broken.append(f"{p}: cites {name} (not a research doc)")
    return total, broken


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root",
        default=os.path.normpath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
        ),
    )
    ap.add_argument("--repo")
    args = ap.parse_args()
    grand = 0
    bad_total = 0
    local = set()
    docs = known_doc_names()
    for name in REPOS:
        repo_dir = os.path.join(args.root, name)
        if not os.path.isdir(repo_dir):
            print(f"{name}: sibling repo directory absent, skipped")
            continue
        collect_local(repo_dir, local)
    for name in REPOS:
        repo_dir = os.path.join(args.root, name)
        if not os.path.isdir(repo_dir):
            continue
        if args.repo and name != args.repo:
            continue
        total, broken = scan(repo_dir, local, docs)
        grand += total
        bad_total += len(broken)
        for b in broken:
            print("BROKEN: " + b)
        print(f"{name}: {total} explicit research citations, {len(broken)} broken")
    if bad_total:
        print(f"FAIL: {bad_total} broken research citations of {grand}")
        return 1
    print(f"OK: {grand} explicit sibling research citations all resolve against docs/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
