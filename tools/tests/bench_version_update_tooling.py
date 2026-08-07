#!/usr/bin/env python3
"""Benchmark: version-update tooling readiness (0-100, higher better).

Measures how well research tooling keeps pins/data honest across a TFP release,
without redownloading Steam builds. Components:

  current_pin_green     stock-check OK on committed facts (gate)
  no_soft_literals      checker has no hard-coded 3.x version soft paths
  mutation_facts_fail   mutated facts version fails pin check (true positive)
  mutation_doc_fail     docs missing current pin fail pin check
  schema_breadth        stock_facts has required hardcode groups
  update_entrypoint     single script/make target covers extract+check(+drift hook)
  tooling_hardcode_debt fewer version literals in tooling sources (not dump path docs)

Prints one line: version_update_readiness=<float>
Also prints component breakdown on stderr / trailing lines for logs.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
FACTS = TOOLS / "data" / "stock_facts.json"
CHECKER = TOOLS / "tests" / "check_stock_facts.py"


def run_checker(facts: Path, *, skip_siblings: bool = True) -> tuple[int, str]:
    cmd = [sys.executable, str(CHECKER), "--facts", str(facts), "--require-live"]
    if skip_siblings:
        cmd.append("--skip-siblings")
    p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode, out


def score_current_pin_green() -> tuple[float, str]:
    if not FACTS.is_file():
        return 0.0, "missing stock_facts.json"
    code, out = run_checker(FACTS, skip_siblings=False)
    if code == 0 and "OK:" in out:
        return 1.0, "stock-check green"
    return 0.0, f"stock-check failed rc={code}"


def score_no_soft_literals() -> tuple[float, str]:
    text = CHECKER.read_text(encoding="utf-8", errors="replace")
    # Soft paths that ignore live facts and hard-code current line versions.
    bad_patterns = [
        r"V 3\\\\\.1\\\\\.0",
        r"V 3\\.1\\.0",
        r'(?<![\\w])3\\.1\\.0(?![\\w])',
        r'"3\.1\.0"',
        r"'3\.1\.0'",
        r"V3\.0\.1-only",  # ok as historical comment if not used as accept path
    ]
    # Count only non-comment code lines that accept a fixed version without using display/build vars.
    soft_hits = []
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # Acceptable: comments about V3.0.1 stale layouts
        if "3.1.0" in line or r"3\.1\.0" in line:
            # bad if it is a regex/accept path not built from variables
            if "display" in line or "pin_display" in line or "re.escape" in line:
                # still bad if it ORs a fixed literal after a dynamic one
                if re.search(r"\|V 3\\\\?\.1\\\\?\.0|\\|V 3\\.1\\.0", line):
                    soft_hits.append(i)
            else:
                soft_hits.append(i)
    if not soft_hits:
        return 1.0, "no soft version literals in checker code"
    # Partial credit if few
    n = len(soft_hits)
    s = max(0.0, 1.0 - 0.25 * n)
    return s, f"soft_literal_lines={soft_hits[:8]}"


def score_mutation_facts_fail() -> tuple[float, str]:
    if not FACTS.is_file():
        return 0.0, "no facts"
    facts = json.loads(FACTS.read_text(encoding="utf-8"))
    # Mutate version so pins should fail if checker is facts-driven
    facts["version"]["major"] = 99
    facts["version"]["minor"] = 0
    facts["version"]["build"] = 1
    facts["version"]["display"] = "V 99.0.0"
    facts["version"]["stock_wire"] = "V99.0.0 b1"
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "facts.json"
        path.write_text(json.dumps(facts, indent=2), encoding="utf-8")
        code, out = run_checker(path, skip_siblings=True)
    if code != 0:
        return 1.0, "mutated facts correctly fail"
    return 0.0, "mutated facts still pass (checker not version-sensitive)"


def score_mutation_doc_fail() -> tuple[float, str]:
    """Copy docs to temp is hard; instead mutate facts census numbers and require fail."""
    if not FACTS.is_file():
        return 0.0, "no facts"
    facts = json.loads(FACTS.read_text(encoding="utf-8"))
    facts.setdefault("census", {})
    facts["census"]["top_level_types"] = 1
    facts["census"]["methods_with_body_top_level"] = 1
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "facts.json"
        path.write_text(json.dumps(facts, indent=2), encoding="utf-8")
        code, out = run_checker(path, skip_siblings=True)
    if code != 0 and ("top-level" in out.lower() or "methods with body" in out.lower() or "pin mismatch" in out.lower()):
        return 1.0, "mutated census correctly fails"
    if code != 0:
        return 0.7, "fails but message not census-specific"
    return 0.0, "mutated census still passes"


def score_schema_breadth() -> tuple[float, str]:
    if not FACTS.is_file():
        return 0.0, "no facts"
    facts = json.loads(FACTS.read_text(encoding="utf-8"))
    required_paths = [
        ("version", "major"),
        ("version", "minor"),
        ("version", "build"),
        ("version", "display"),
        ("version", "stock_wire"),
        ("sim", "constants_ticks_per_second"),
        ("network", "netpackage_top_level_count"),
        ("network", "challenge_marker"),
        ("chunk", "block_y_dim"),
        ("chunk", "block_layers"),
        ("save", "current_save_version"),
        ("census", "top_level_types"),
        ("census", "methods_with_body_top_level"),
        ("tile_entity_package", "present"),
    ]
    # Bonus hardcodes that help post-update (optional weight)
    bonus_paths = [
        ("network", "default_port"),
        ("save", "worldstate_saveload_stream_il"),
        ("census", "gmupdate_il"),
        ("consumers",),
        # Future: behavioural constants group
        ("behaviour",),
        ("update",),
        ("pins",),
    ]
    ok = 0
    for path in required_paths:
        cur = facts
        good = True
        for k in path:
            if not isinstance(cur, dict) or k not in cur:
                good = False
                break
            cur = cur[k]
        if good:
            ok += 1
    base = ok / len(required_paths)
    bonus_ok = 0
    for path in bonus_paths:
        cur = facts
        good = True
        for k in path:
            if not isinstance(cur, dict) or k not in cur:
                good = False
                break
            cur = cur[k]
        if good:
            bonus_ok += 1
    bonus = 0.15 * (bonus_ok / len(bonus_paths))
    s = min(1.0, base * 0.85 + bonus)
    return s, f"required={ok}/{len(required_paths)} bonus={bonus_ok}/{len(bonus_paths)}"


def score_update_entrypoint() -> tuple[float, str]:
    stock = (TOOLS / "stock-sync.sh").read_text(encoding="utf-8", errors="replace")
    make = (ROOT / "Makefile").read_text(encoding="utf-8", errors="replace")
    readme = (TOOLS / "README.md").read_text(encoding="utf-8", errors="replace")
    points = 0.0
    notes = []
    if "check_stock_facts" in stock or "stock_facts" in stock:
        points += 0.25
        notes.append("stock-sync extracts/checks")
    if re.search(r"drift|parity", stock, re.I):
        points += 0.25
        notes.append("stock-sync hooks drift")
    elif re.search(r"^drift:|post-update|version-update", make, re.M):
        points += 0.15
        notes.append("make has drift/post-update")
    if (TOOLS / "tests" / "post_update_checklist.sh").is_file() or (
        TOOLS / "post-update.sh"
    ).is_file() or re.search(r"post-update|version-update", make):
        points += 0.25
        notes.append("post-update entrypoint exists")
    if re.search(r"stock-sync|After a TFP|game update", readme):
        points += 0.15
        notes.append("README documents update path")
    if "make stock-sync" in readme or "stock-sync.sh" in readme:
        points += 0.10
        notes.append("README names stock-sync")
    return min(1.0, points), ", ".join(notes) or "no update orchestration"


def score_tooling_hardcode_debt() -> tuple[float, str]:
    """Lower debt in .py/.sh/.cs (exclude README dump path tables and stock_facts)."""
    pats = [re.compile(r"3\.1\.0"), re.compile(r"V3\.0\.1"), re.compile(r"\bb14\b")]
    hits = 0
    files = 0
    skip_names = {
        "bench_version_update_tooling.py",  # detector itself mentions example versions
        "stock_facts.json",
    }
    for p in TOOLS.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in {".py", ".sh", ".cs"}:
            continue
        if "bin" in p.parts or p.name in skip_names:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        files += 1
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("//") or s.startswith("#"):
                continue
            # Inline comments on code lines: strip trailing comment before match.
            code = re.split(r"\s+#|\s+//", line, maxsplit=1)[0]
            # Fallback labels / format templates are not pin debt.
            if re.search(r"v0\.0\.0|v\{disp\}|dump_label_suffix|V\{0\}", code):
                continue
            for pat in pats:
                if pat.search(code):
                    hits += 1
                    break
    # 0 hits => 1.0; each hit costs 0.08
    s = max(0.0, 1.0 - 0.08 * hits)
    return s, f"code_version_literal_hits={hits} files_scanned={files}"


def main() -> int:
    weights = {
        "current_pin_green": 0.20,
        "no_soft_literals": 0.15,
        "mutation_facts_fail": 0.20,
        "mutation_doc_fail": 0.15,
        "schema_breadth": 0.15,
        "update_entrypoint": 0.10,
        "tooling_hardcode_debt": 0.05,
    }
    scorers = {
        "current_pin_green": score_current_pin_green,
        "no_soft_literals": score_no_soft_literals,
        "mutation_facts_fail": score_mutation_facts_fail,
        "mutation_doc_fail": score_mutation_doc_fail,
        "schema_breadth": score_schema_breadth,
        "update_entrypoint": score_update_entrypoint,
        "tooling_hardcode_debt": score_tooling_hardcode_debt,
    }
    total = 0.0
    details = []
    for name, w in weights.items():
        s, note = scorers[name]()
        total += w * s
        details.append(f"  {name}: {s:.3f} (w={w}) — {note}")
    readiness = round(100.0 * total, 2)
    print(f"version_update_readiness={readiness}")
    for d in details:
        print(d)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
