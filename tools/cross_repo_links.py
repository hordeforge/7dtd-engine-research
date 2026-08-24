#!/usr/bin/env python3
"""Cross-repo relative-link sweep for the 7dtd workspace.

Scans every *.md in the sibling repos next to 7dtd-engine-research (7dtd-server-apm,
7dtd-fastconnect, 7dtd-loadgen, 7dtd-server-optimizer, 7dtd-playtest, 7dtd-realearth,
7dtd-engine-research, 7dtd-server-guard, zdtd-server) and resolves every relative
markdown link that crosses the owning repo's boundary (a `../` chain leaving
the repo root). Broken links are reported with the owning file.

The local layout is the canonical one (`<workspace>/<repo>/`), so a link is
resolved against the file's directory, not the repo root - a repo-root file
needs `../7dtd-engine-research/...`, a docs/ file needs `../../7dtd-engine-research/...`.

Usage: python3 tools/cross_repo_links.py [--root <workspace>] [--repo NAME]
  --root defaults to the parent of this repo (the sibling layout root).
  --repo limits the scan to one repo name.
Exit 0 = all links resolve; 1 = at least one broken link.
"""
import argparse
import glob
import os
import re
import sys

LINK = re.compile(r"\]\(((?:\.\./)+[^) ]+\.md)\)")
REPOS = [
    "7dtd-server-apm", "7dtd-fastconnect", "7dtd-loadgen", "7dtd-server-optimizer",
    "7dtd-playtest", "7dtd-realearth", "7dtd-engine-research", "7dtd-server-guard",
    "zdtd-server",
]


def scan_repo(repo: str, only_name: str | None) -> tuple[int, int, list[str]]:
    if not os.path.isdir(repo):
        return 0, 0, []
    if only_name and os.path.basename(repo) != only_name:
        return 0, 0, []
    total = 0
    broken = []
    for f in glob.glob(os.path.join(repo, "**", "*.md"), recursive=True):
        if ".git" in f:
            continue
        base = os.path.dirname(f)
        try:
            with open(f, encoding="utf-8") as fh:
                txt = fh.read()
        except OSError:
            continue
        for m in LINK.finditer(txt):
            p = os.path.normpath(os.path.join(base, m.group(1)))
            if not p.startswith(os.path.normpath(repo) + os.sep):
                total += 1
                if not os.path.exists(p):
                    broken.append(f"  BROKEN {f}: {m.group(1)}")
    return total, len(broken), broken


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
    ap.add_argument("--repo")
    args = ap.parse_args()
    root = args.root
    grand = 0
    bad_total = 0
    for name in REPOS:
        total, bad, rows = scan_repo(os.path.join(root, name), args.repo)
        grand += total
        bad_total += bad
        for r in rows:
            print(r)
        print(f"{name}: {total} external .md links, {bad} broken")
    if bad_total:
        print(f"FAIL: {bad_total} broken cross-repo links of {grand}")
        return 1
    print(f"OK: {grand} cross-repo .md links all resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
