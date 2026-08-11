#!/usr/bin/env python3
"""Verify zdtd's RESEARCH citations resolve against this corpus.

zdtd's provenance (docs/PROVENANCE.md ledger + inline comments across src/)
maps every value and behavior back to the stock dedicated server through the
research docs. This gate extracts only EXPLICIT research citations - an
`RE:` marker or a `7dtd-research/docs/` path prefix - and checks the cited
file exists in this repo's docs/. Bare names of zdtd's OWN docs (GAP_ANALYSIS,
docs/adr/00XX, etc.) are not research citations and are ignored.

Usage: python3 tools/zdtd_cite_check.py [--zdtd <path>]
  --zdtd defaults to ../../zdtd (the sibling layout root).
Exit 0 when every research citation resolves; 1 with the broken list otherwise.
"""
import argparse
import os
import re
import sys

# An explicit research citation: an "RE:" marker optionally followed by a
# research path, or a bare `docs/X.md` behind `7dtd-research/`. The capture is
# the full doc name token.
RE_MARK = re.compile(r"RE(?::|\s+)")
RES_PATH = re.compile(
    r"(?:(?:\.\./)*7dtd-research/docs/)([A-Za-z0-9][A-Za-z0-9_-]+\.md)"
)
BARE_AFTER_RE = re.compile(r"RE(?::|\s+)(?:../7dtd-research/docs/)?([A-Za-z0-9][A-Za-z0-9_-]+\.md)")
# any bare .md name in a src comment (doc-name token; no path prefix).
BARE = re.compile(r"(?<![\w./-])([A-Za-z0-9][A-Za-z0-9_-]+\.md)")


def docs_dir() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")


def scan(root: str) -> tuple[int, list[str]]:
    total = 0
    broken = []
    # zdtd-local doc names (docs/ root + docs/adr/ with the NNNN- prefix
    # stripped) resolve inside zdtd, not the research corpus.
    local = set()
    for d in os.listdir(os.path.join(root, "docs")):
        if d.endswith(".md"):
            local.add(d)
    # zdtd root .md files (AGENTS.md, README.md, TODO.md, ...) are zdtd-local.
    for d in os.listdir(root):
        if d.endswith(".md"):
            local.add(d)
    adr = os.path.join(root, "docs", "adr")
    if os.path.isdir(adr):
        for d in os.listdir(adr):
            if d.endswith(".md"):
                local.add(d)
                stripped = re.sub(r"^\d+-", "", d)
                local.add(stripped)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", ".zig-cache", ".claude", "zig-pkg")]
        for fn in filenames:
            if not (fn.endswith(".zig") or fn.endswith(".md")):
                continue
            p = os.path.join(dirpath, fn)
            try:
                txt = open(p, encoding="utf-8").read()
            except OSError:
                continue
            # explicit research paths (anywhere in the text)
            for m in RES_PATH.finditer(txt):
                total += 1
                if not os.path.isfile(os.path.join(docs_dir(), m.group(1))):
                    broken.append(f"{p}: cites {m.group(1)}")
            # bare name directly after an RE: marker (the provenance convention)
            for m in BARE_AFTER_RE.finditer(txt):
                total += 1
                if not os.path.isfile(os.path.join(docs_dir(), m.group(1))):
                    broken.append(f"{p}: cites {m.group(1)}")
            # src/**.zig: a bare `X.md` name is unambiguous - it must be a
            # research doc, a zdtd-local doc, or a zdtd ADR (stripped).
            if fn.endswith(".zig"):
                for m in BARE.finditer(txt):
                    name = m.group(1)
                    if name in local:
                        continue
                    total += 1
                    if not os.path.isfile(os.path.join(docs_dir(), name)):
                        broken.append(f"{p}: cites {name} (not a research doc)")
    return total, broken


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zdtd", default=os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "zdtd")))
    args = ap.parse_args()
    total, broken = scan(args.zdtd)
    for b in broken:
        print("BROKEN: " + b)
    if broken:
        print(f"FAIL: {len(broken)} of {total} research citations do not resolve")
        return 1
    print(f"OK: {total} explicit zdtd research citations all resolve against docs/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
