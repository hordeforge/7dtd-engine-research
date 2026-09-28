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
  --repo limits the scan to one repo name; any other name is a usage error
  (exit 2), never an empty sweep reported as OK.
Exit 0 = all links resolve; 1 = at least one broken link; 2 = bad invocation.
"""

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tooling

# The optional #fragment suffix and the optional `"Title"` must both be
# matched (and stripped before the existence check): a link like
# ../repo/docs/x.md#section, or ../repo/docs/x.md "Surface", crosses the repo
# boundary just the same, and leaving either unmatched would print "OK: all
# links resolve" while that link was never checked.
LINK = re.compile(r"\]\(((?:\.\./)+[^)\s]+\.md(?:#[^)\s]*)?)(?:\s+[^)]*)?\)")
REPOS = [
    "7dtd-server-apm",
    "7dtd-fastconnect",
    "7dtd-loadgen",
    "7dtd-server-optimizer",
    "7dtd-playtest",
    "7dtd-realearth",
    "7dtd-engine-research",
    "7dtd-server-guard",
    "zdtd-server",
]
# VCS metadata and vendored trees: they hold no authored links, and walking a
# sibling's node_modules is pure cost. Dot-directories other than these are
# swept, because a sibling's .github/ is documentation.
SKIP_DIRS = {
    ".git",
    ".zig-cache",
    "node_modules",
    ".venv",
    "bin",
    "obj",
    "__pycache__",
    "target",
    "dist",
    "build",
}


def scan_repo(repo: str, only_name: str | None) -> tuple[int, int, int, list[str]]:
    """(external-link count, broken count, unreadable-file count, report lines)."""
    if not os.path.isdir(repo):
        return 0, 0, 0, []
    if only_name and os.path.basename(repo) != only_name:
        return 0, 0, 0, []
    total = 0
    broken = []
    unreadable = []
    for dirpath, dirnames, filenames in os.walk(repo):
        # Only VCS and vendored trees are skipped: dot-directories carry docs
        # (a sibling's .github/), and glob's recursive walk never matched them.
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.endswith(".md"):
                continue
            f = os.path.join(dirpath, name)
            try:
                with open(f, encoding="utf-8") as fh:
                    txt = fh.read()
            except OSError as exc:
                # A gate must not pass a file it could not read: its links were
                # never checked. Report and fail rather than silently skipping.
                unreadable.append(f"  UNREADABLE {f}: {exc}")
                continue
            for m in LINK.finditer(txt):
                p = os.path.normpath(os.path.join(dirpath, m.group(1).split("#", 1)[0]))
                if not p.startswith(os.path.normpath(repo) + os.sep):
                    total += 1
                    if not os.path.exists(p):
                        broken.append(f"  BROKEN {f}: {m.group(1)}")
    return total, len(broken), len(unreadable), broken + unreadable


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Resolve every cross-repo relative .md link from the sibling repos."
    )
    ap.add_argument(
        "--root",
        default=str(tooling.REPO.parent),
        help="workspace root holding the sibling repos (default: the parent of this repo)",
    )
    # A name outside REPOS matches no repo, so the sweep prints a per-repo
    # zero line and reports "OK: 0 cross-repo .md links all resolve": a typo
    # reads as a green gate. choices= makes argparse refuse it with the
    # candidate names and exit 2.
    ap.add_argument("--repo", choices=REPOS, help="limit the scan to one repo name")
    args = ap.parse_args()
    if args.repo and args.repo not in REPOS:
        print(
            f"cross_repo_links: unknown repo {args.repo!r}; known repos: " + ", ".join(REPOS),
            file=sys.stderr,
        )
        return 2
    root = args.root
    grand = 0
    bad_total = 0
    unread_total = 0
    for name in REPOS:
        total, bad, unreadable, rows = scan_repo(os.path.join(root, name), args.repo)
        grand += total
        bad_total += bad
        unread_total += unreadable
        for r in rows:
            print(r)
        print(
            f"{name}: {total} external .md links, {bad} broken"
            + (f", {unreadable} UNREADABLE" if unreadable else "")
        )
    if bad_total or unread_total:
        parts = [f"{bad_total} broken cross-repo links of {grand}"]
        if unread_total:
            parts.append(f"{unread_total} unreadable files (links unchecked)")
        print("FAIL: " + "; ".join(parts))
        return 1
    print(f"OK: {grand} cross-repo .md links all resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
