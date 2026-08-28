#!/usr/bin/env python3
"""Assert docs/coverage.md invariants: audit-table completeness + census pin match.

The audit table ("Audit status per doc") must list every narrative doc under
docs/ (root level), so a new or renamed doc cannot silently skip an audit
tier. The census table must match tools/data/stock_facts.json, so the
coverage map's headline numbers cannot drift from the pinned tool output.

Usage: python3 tools/tests/test_coverage_consistency.py
"""

import json
import os
import re

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(TOOLS)
DOCS = os.path.join(REPO, "docs")
COVERAGE = os.path.join(DOCS, "coverage.md")
FACTS = os.path.join(TOOLS, "data", "stock_facts.json")


def _coverage_text() -> str:
    with open(COVERAGE, encoding="utf-8") as f:
        return f.read()


def test_audit_table_lists_every_doc() -> None:
    text = _coverage_text()
    # audit rows are of the form "| [name.md](name.md) | tier |"; prose and
    # comma-separated table cells (e.g. the family table) do not match because
    # they do not put " |" immediately after the closing paren. Dots allowed so
    # versioned docs like changelog-3.2.0.md participate.
    audited = set(re.findall(r"\| \[([a-z0-9.\-]+\.md)\]\([^)]+\) \|", text))
    root_docs = {n for n in os.listdir(DOCS) if n.endswith(".md") and n != "INDEX.md"}
    missing = sorted(root_docs - audited)
    assert not missing, f"docs missing from coverage.md audit table: {missing}"


def test_census_table_matches_stock_facts() -> None:
    text = _coverage_text()
    with open(FACTS, encoding="utf-8") as f:
        facts = json.load(f)
    c = facts["census"]
    s = facts["save"]
    sim = facts["sim"]
    net = facts["network"]
    rows = {
        "Top-level types": c["top_level_types"],
        "Methods with body": c["methods_with_body_top_level"],
        "GameTimer Hz": sim["gametimer_instance_tps"],
        "gmUpdate IL": c["gmupdate_il"],
        "CurrentSaveVersion": s["current_save_version"],
    }
    for label, expected in rows.items():
        m = re.search(rf"\|\s*{re.escape(label)}\s*\|\s*(\d+)", text)
        assert m, f"census row {label!r} missing in coverage.md"
        assert int(m.group(1)) == expected, (
            f"coverage.md {label}={m.group(1)} but stock_facts.json says {expected}"
        )
    m = re.search(r"\|\s*WorldState\.SaveLoad\(Stream\) IL\s*\|\s*(\d+)", text)
    assert m, "WorldState.SaveLoad(Stream) census row missing in coverage.md"
    assert int(m.group(1)) == s["worldstate_saveload_stream_il"]
    # NetPackage row: "194 name-prefixed (193 + NetPackageManager)"
    m = re.search(r"\|\s*NetPackage\* types\s*\|\s*(\d+)", text)
    assert m, "NetPackage census row missing in coverage.md"
    assert int(m.group(1)) == net["netpackage_top_level_count"] + 1, (
        "coverage.md NetPackage count must be census count + NetPackageManager"
    )


if __name__ == "__main__":
    test_audit_table_lists_every_doc()
    test_census_table_matches_stock_facts()
    print("OK: coverage.md audit table complete; census rows match stock_facts.json")
