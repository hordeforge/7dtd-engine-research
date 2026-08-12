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

    # 3. Cross-repo links (../sibling/...) must resolve to a real file. Wrong
    #    depth (e.g. ../../ from docs/ root when the sibling is ../) silently
    #    breaks the delivery loop, so resolve the full relative path.
    dead_x = []
    for sub, _dirs, names in os.walk(DOCS):
        for name in names:
            if not name.endswith(".md"):
                continue
            path = os.path.join(sub, name)
            text = open(path, encoding="utf-8").read()
            for m in re.finditer(r"\]\((\.\./[^)]+\.md)\)", text):
                target = os.path.normpath(os.path.join(sub, m.group(1)))
                # Sibling repo name = first non-".." path component (e.g. 7dtd-optimizer).
                parts = [p for p in m.group(1).split("/") if p not in ("", ".")]
                sibling = next((p for p in parts if p != ".."), None)
                if sibling is None:
                    continue
                # In a single-repo CI checkout the sibling repos are absent; skip
                # those links (verified by the cross-repo pass) instead of failing.
                correct_sibling = os.path.normpath(os.path.join(REPO, "..", sibling))
                if not os.path.isdir(correct_sibling):
                    continue
                if not os.path.isfile(target):
                    dead_x.append(f"{os.path.relpath(path, DOCS)} -> {m.group(1)}")
    if dead_x:
        raise AssertionError("broken cross-repo links:\n" + "\n".join(sorted(set(dead_x))[:15]))

    # 3b. Section references ([doc](path) §N[.M]) must resolve to a header in
    # the target doc (anchors drift when sections are renumbered).
    sect_pat = re.compile(r"\[[A-Za-z0-9_.-]+\.md\]\(([^)]*\.md)\)\s*§\s*([0-9]+(?:\.[0-9]+)?)")
    bad_sec = []
    n_sec = 0
    for sub, _dirs, names in os.walk(DOCS):
        for name in names:
            if not name.endswith(".md"):
                continue
            path = os.path.join(sub, name)
            text = open(path, encoding="utf-8").read()
            for m in sect_pat.finditer(text):
                target = os.path.normpath(os.path.join(sub, m.group(1)))
                sec = m.group(2)
                n_sec += 1
                # Single-repo CI checkout: skip cross-repo section refs whose
                # sibling repo is absent, exactly like the cross-repo link
                # check above (the delivery loop verifies them locally).
                parts = [p for p in m.group(1).split("/") if p not in ("", ".")]
                sibling = next((p for p in parts if p != ".."), None)
                if sibling is not None:
                    correct_sibling = os.path.normpath(os.path.join(REPO, "..", sibling))
                    if not os.path.isdir(correct_sibling):
                        continue
                if not os.path.isfile(target):
                    bad_sec.append(f"{os.path.relpath(path, DOCS)}: §{sec} -> {m.group(1)} (no file)")
                    continue
                hdr = re.compile(rf"^#{{1,4}} {re.escape(sec)}(?:[ .:]|$)")
                tlines = open(target, encoding="utf-8").read().splitlines()
                if not any(hdr.match(l) for l in tlines):
                    bad_sec.append(f"{os.path.relpath(path, DOCS)}: §{sec} -> {m.group(1)} (no header)")
    if bad_sec:
        raise AssertionError("broken section references:\n" + "\n".join(sorted(set(bad_sec))[:15]))

    # 4. Every root doc carries the canonical hub backlink ("**Hub:** INDEX.md").
    no_hub = sorted(
        d
        for d in doc_root
        if "**Hub:**" not in open(os.path.join(DOCS, d), encoding="utf-8").read()
    )
    if no_hub:
        raise AssertionError(f"docs missing **Hub:** backlink: {no_hub}")

    # 4b. Every inventory carries the hub backlink too (the auto-generated ones
    # emit it from WireBodies/Coverage; the hand-maintained ones carry it inline).
    inv_dir = os.path.join(DOCS, "inventories")
    no_hub_inv = sorted(
        n
        for n in os.listdir(inv_dir)
        if n.endswith(".md")
        and "**Hub:**" not in open(os.path.join(inv_dir, n), encoding="utf-8").read()
    )
    if no_hub_inv:
        raise AssertionError(f"inventories missing **Hub:** backlink: {no_hub_inv}")

    print(f"OK: {len(doc_root)} docs reachable from INDEX.md, 0 dead internal links ({len(all_docs)} doc files, {n_sec} section refs)")


if __name__ == "__main__":
    main()
