#!/usr/bin/env python3
"""Assert the corpus pin invariants: audit table, census rows, pin banners.

The audit table ("Audit status per doc") must list every narrative doc under
docs/ (root level), so a new or renamed doc cannot silently skip an audit
tier. The census table must match tools/data/stock_facts.json, so the
coverage map's headline numbers cannot drift from the pinned tool output.
Every "**Current pin:**" banner must name the pinned build, so a doc cannot
quietly keep advertising a superseded one (this is how docs/network/network.md
came to claim a 3.1.0 pin after the corpus moved to 3.2.0).

Usage: python3 tools/tests/test_coverage_consistency.py
"""

import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOLS = _common.TOOLS
REPO = str(_common.REPO)
DOCS = str(_common.DOCS)
COVERAGE = _common.doc("coverage.md")
FACTS = TOOLS / "data" / "stock_facts.json"


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
    root_docs = {
        n
        for sub, _dirs, names in os.walk(DOCS)
        if os.path.basename(sub) != "inventories"
        for n in names
        if n.endswith(".md") and n != "INDEX.md"
    }
    missing = sorted(root_docs - audited)
    assert not missing, f"docs missing from coverage.md audit table: {missing}"


def test_census_table_matches_stock_facts() -> None:
    text = _coverage_text()
    facts = _common.load_json(FACTS)
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


def test_pin_banners_match_stock_facts() -> None:
    """No doc's current-pin banner may name a build other than the machine pin.

    Runs the check_stock_facts banner check over the real corpus, then over a
    synthetic tree with one stale banner, so the check cannot rot into a
    pass-because-it-does-nothing gate. The banner check is a pure function of
    stock_facts.json, so this is DLL-free even though its owner is not.
    """
    module = _common.load_module(TOOLS / "tests" / "check_stock_facts.py", "check_stock_facts")
    facts = _common.load_json(FACTS)

    errors: list[str] = []
    module.check_pin_banners(facts, errors)
    assert not errors, "current-pin banners disagree with stock_facts.json:\n" + "\n".join(errors)

    with tempfile.TemporaryDirectory(prefix="pin_banner_", dir=_common.scratch_dir()) as tmp:
        tree = Path(tmp)
        (tree / "good.md").write_text(
            f"**Current pin:** V **{facts['version']['display']} "
            f"(b{facts['version']['build']})**.\n",
            encoding="utf-8",
        )
        stale: list[str] = []
        module.check_pin_banners(facts, stale, root=tree)
        assert not stale, stale

        # A superseded build, and the right version with the wrong build, both fail.
        for banner, why in (
            ("**Current pin:** V **3.1.0 (b14)**.", "superseded build"),
            (
                f"**Current game pin:** V **{facts['version']['display']} (b1)**.",
                "wrong build for the right version",
            ),
        ):
            (tree / "good.md").write_text(banner + "\n", encoding="utf-8")
            stale = []
            module.check_pin_banners(facts, stale, root=tree)
            assert stale, f"stale banner accepted ({why}): {banner}"

        # History prose and section headings are not banners and must pass through.
        (tree / "good.md").write_text(
            "## 3. Current pin status\n\n"
            "the last live capture was V 3.1.0 b14; see changelog-3.1.0.md\n",
            encoding="utf-8",
        )
        stale = []
        module.check_pin_banners(facts, stale, root=tree)
        assert not stale, stale


if __name__ == "__main__":
    test_audit_table_lists_every_doc()
    test_census_table_matches_stock_facts()
    test_pin_banners_match_stock_facts()
    print(
        "OK: coverage.md audit table complete; census rows and current-pin "
        "banners match stock_facts.json"
    )
