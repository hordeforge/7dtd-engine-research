#!/usr/bin/env python3
"""Assert the docs wiki invariants: full INDEX reachability + no dead internal links.

The wiki cross-linking pass (2026-08-09) established: every doc under docs/
is reachable from docs/INDEX.md by following internal .md links, and no doc
links to a non-existent sibling doc. A new doc that fails to link INDEX, or a
doc that references a renamed/missing doc, breaks the hub - this test catches
it before the corpus drifts.

Usage: python3 tools/tests/test_doc_link_integrity.py
"""
import os
import re
from collections import deque

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(TOOLS)
DOCS = os.path.join(REPO, "docs")
LINK_RE = re.compile(r"\]\(([^)]+\.md)")


def collect():
    """Return ({doc_basename: [link basenames]}, {doc_basename} of docs/ root)."""
    out = {}
    doc_root = set()
    for sub, is_root in (("", True), ("inventories", False)):
        d = os.path.join(DOCS, sub)
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            if not name.endswith(".md"):
                continue
            path = os.path.join(d, name)
            targets = []
            for m in LINK_RE.finditer(open(path, encoding="utf-8").read()):
                tgt = m.group(1)
                if tgt.startswith(("http", "../", "/")):
                    continue  # external or cross-repo; not this check
                targets.append(os.path.basename(tgt))
            out[name] = targets
            if is_root:
                doc_root.add(name)
    return out, doc_root


def main():
    graph, doc_root = collect()
    all_docs = set(graph)

    # 1. BFS reachability from INDEX.md (docs/ only, not inventories).
    start = "INDEX.md"
    if start not in graph:
        raise AssertionError("docs/INDEX.md missing")
    reachable = {start}
    q = deque([start])
    while q:
        cur = q.popleft()
        for t in graph.get(cur, []):
            if t in doc_root and t not in reachable:
                reachable.add(t)
                q.append(t)
    orphan = sorted(doc_root - reachable)
    if orphan:
        raise AssertionError(f"docs not reachable from INDEX.md: {orphan}")

    # 2. No dead internal links (any target basename must exist somewhere in docs/ or docs/inventories/).
    dead = []
    for src, targets in graph.items():
        for t in targets:
            if t not in all_docs:
                dead.append(f"{src} -> {t}")
    if dead:
        raise AssertionError("dead internal doc links:\n" + "\n".join(sorted(set(dead))[:20]))

    # 3. Every root doc carries the canonical hub backlink ("**Hub:** INDEX.md").
    no_hub = sorted(
        d
        for d in doc_root
        if "**Hub:**" not in open(os.path.join(DOCS, d), encoding="utf-8").read()
    )
    if no_hub:
        raise AssertionError(f"docs missing **Hub:** backlink: {no_hub}")

    print(f"OK: {len(doc_root)} docs reachable from INDEX.md, 0 dead internal links ({len(all_docs)} doc files)")


if __name__ == "__main__":
    main()
