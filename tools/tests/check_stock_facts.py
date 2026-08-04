#!/usr/bin/env python3
"""Fail if research docs / sibling product pins disagree with tools/data/stock_facts.json.

StockFacts.cs regenerates that JSON from the live Assembly-CSharp.dll. This script
only reads the committed (or just-regenerated) JSON and greps known pin sites.

Usage:
  python3 tools/tests/check_stock_facts.py
  python3 tools/tests/check_stock_facts.py --facts path/to/stock_facts.json
  python3 tools/tests/check_stock_facts.py --require-live   # fail if facts missing

Exit 0 = in sync (or soft-skip if no facts and not --require-live).
Exit 1 = mismatch.
Exit 2 = usage / missing required facts.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # 7dtd-research
WS = ROOT.parent  # 7dtd workspace
DEFAULT_FACTS = ROOT / "tools" / "data" / "stock_facts.json"


def load_facts(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def must_contain(label: str, text: str, needle: str, errors: list[str]) -> None:
    if needle not in text:
        errors.append(f"{label}: missing {needle!r}")


def must_match(label: str, text: str, pattern: str, errors: list[str]) -> None:
    if not re.search(pattern, text):
        errors.append(f"{label}: no match for /{pattern}/")


def check_research(facts: dict, errors: list[str]) -> None:
    v = facts["version"]
    display = v["display"]  # e.g. V 3.1.0
    major, minor, build = v["major"], v["minor"], v["build"]
    tps = facts["sim"]["constants_ticks_per_second"]
    ydim = facts["chunk"]["block_y_dim"]
    layers = facts["chunk"]["block_layers"]
    npkg = facts["network"]["netpackage_top_level_count"]
    save_ver = facts["save"].get("current_save_version")

    cov = read(ROOT / "docs" / "coverage.md")
    # Pin banner: V 3.1.0 (b14) or similar
    must_match(
        "docs/coverage.md pin",
        cov,
        rf"V\s*{re.escape(display.replace('V ', ''))}\s*\(b{build}\)|"
        rf"V\s*\*\*{re.escape(display.replace('V ', ''))}\s*\(b{build}\)\*\*",
        errors,
    )
    # Also accept "V **3.1.0 (b14)**" style already used
    if not re.search(rf"3\.1\.0.*b{build}|b{build}.*3\.1\.0|Major\s*=\s*{major}.*Minor\s*=\s*{minor}.*Build\s*=\s*{build}", cov, re.I | re.S):
        # softer: require major.minor.build triple somewhere
        if f"Major={major}" not in cov and f"Minor={minor}" not in cov:
            errors.append(
                f"docs/coverage.md: expected version pin for {display} b{build} "
                f"(Major={major} Minor={minor} Build={build})"
            )

    # Chunk dims
    if str(ydim) not in cov and f"ChunkBlockYDim={ydim}" not in cov:
        # coverage mentions ChunkBlockYDim=256 historically
        must_match("docs/coverage.md YDim", cov, rf"ChunkBlockYDim\s*=\s*{ydim}|YDim.*{ydim}", errors)

    closed = read(ROOT / "docs" / "closed-gaps.md")
    must_match("docs/closed-gaps.md GameTimer", closed, rf"ticksPerSecond\s*=\s*\*\*{tps}\*\*|GameTimer\({tps}|ticksPerSecond.*{tps}", errors)

    proto = read(ROOT / "docs" / "protocol.md")
    must_contain("docs/protocol.md challenge", proto, "0xCA", errors)
    must_match("docs/protocol.md version display", proto, re.escape(display) + r"|V 3\.1\.0", errors)

    if save_ver is not None:
        save = read(ROOT / "docs" / "save-region.md")
        must_match(
            "docs/save-region.md CurrentSaveVersion",
            save,
            rf"CurrentSaveVersion[`\s]*=?\s*\*\*{save_ver}\*\*|CurrentSaveVersion\s*=\s*{save_ver}",
            errors,
        )

    # NetPackage count in coverage/protocol family
    if str(npkg) not in cov and str(npkg) not in proto:
        inv = read(ROOT / "docs" / "protocol-packages.md")
        if str(npkg) not in inv:
            errors.append(f"research docs: NetPackage count {npkg} not mentioned in coverage/protocol/protocol-packages")


def check_loadgen(facts: dict, errors: list[str]) -> None:
    path = WS / "7dtd-loadgen" / "src" / "LoadGen" / "PackageCodec.cs"
    text = read(path)
    if not text:
        errors.append(f"loadgen missing: {path}")
        return
    v = facts["version"]
    # GameVersion = new(1, 3, 10, 14)
    pat = rf"GameVersion\s*=\s*new\s*\(\s*{v['release_type']}\s*,\s*{v['major']}\s*,\s*{v['minor']}\s*,\s*{v['build']}\s*\)"
    must_match("loadgen PackageCodec.GameVersion", text, pat, errors)
    must_contain("loadgen challenge marker comment or const", text, "0xCA", errors) if "Challenge" in text or "0xCA" in text else None
    if "0xCA" not in text and "202" not in text:
        # ChallengeChannelMarker = 202
        must_match("loadgen challenge", text, r"ChallengeChannelMarker\s*=\s*202|0xCA", errors)


def check_zdtd(facts: dict, errors: list[str]) -> None:
    ver_path = WS / "zdtd" / "src" / "version.zig"
    proto_path = WS / "zdtd" / "src" / "protocol.zig"
    ver = read(ver_path)
    proto = read(proto_path)
    if not ver:
        errors.append(f"zdtd missing: {ver_path}")
        return
    stock = facts["version"]["stock_wire"]
    must_match(
        "zdtd stock_wire",
        ver,
        rf'pub const stock_wire = "{re.escape(stock)}";',
        errors,
    )
    if not proto:
        errors.append(f"zdtd missing: {proto_path}")
        return
    tps = facts["sim"]["constants_ticks_per_second"]
    must_match(
        "zdtd ticks_per_second",
        proto,
        rf"pub const ticks_per_second: u32 = {tps};",
        errors,
    )
    ch = facts["network"]["challenge_marker"]
    must_match(
        "zdtd challenge_marker",
        proto,
        rf"pub const challenge_marker: u8 = 0x{ch:02X};|pub const challenge_marker: u8 = {ch};",
        errors,
    )
    ydim = facts["chunk"]["block_y_dim"]
    store = read(WS / "zdtd" / "src" / "world" / "store.zig")
    if store:
        must_match("zdtd y_dim", store, rf"pub const y_dim: i32 = {ydim};", errors)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--facts", type=Path, default=DEFAULT_FACTS)
    ap.add_argument(
        "--require-live",
        action="store_true",
        help="fail if stock_facts.json is missing (default: soft-skip)",
    )
    ap.add_argument("--skip-siblings", action="store_true", help="only check research docs")
    args = ap.parse_args()

    if not args.facts.is_file():
        msg = f"stock_facts.json not found at {args.facts}"
        if args.require_live:
            print(f"FAIL: {msg}", file=sys.stderr)
            print("  regenerate: tools/stock-sync.sh", file=sys.stderr)
            return 2
        print(f"SKIP: {msg} (run tools/stock-sync.sh to enable pin gate)")
        return 0

    facts = load_facts(args.facts)
    errors: list[str] = []

    check_research(facts, errors)
    if not args.skip_siblings:
        check_loadgen(facts, errors)
        check_zdtd(facts, errors)

    v = facts["version"]
    print(
        f"stock_facts: {v['display']} (b{v['build']}) "
        f"tps={facts['sim']['constants_ticks_per_second']} "
        f"netpkg={facts['network']['netpackage_top_level_count']} "
        f"ydim={facts['chunk']['block_y_dim']}"
    )
    if errors:
        print(f"FAIL: {len(errors)} pin mismatch(es)")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("OK: research + sibling pins match stock_facts.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
