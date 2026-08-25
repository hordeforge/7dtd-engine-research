#!/usr/bin/env python3
"""Machine-checked XML data pins: key values from the operator's Data/Config.

StockFacts.exe pins DLL constants; this pins selected XML data values that
the corpus and zdtd's provenance register cite (the zombie HP ladder from
entityclasses.xml replace_passive_effect, etc.). Values are pinned against the
installed game so a data change (or wrong claim) fails the gate. Every section
written to the pins file is verified by --check: a section that is extracted
and committed but never diffed against the install would let silent drift pass
as a green gate.

Usage:
  python3 tools/xml_pins.py [--pins FILE] --game-dir DIR  # regenerate pins from DIR
  python3 tools/xml_pins.py --check [--pins FILE]         # check committed pins vs the pinned install path
"""

import argparse
import json
import os
import re
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PINS = os.path.join(TOOLS, "data", "xml_pins.json")

# Every extracted section is part of the gate contract: --check diffs each one,
# and regeneration refuses to overwrite a populated section with an empty parse.
SECTIONS = ("entityclasses_health", "traders_root", "buffs_survival")

DEFAULT_GAME = os.path.expanduser(
    "~/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server"
)
CFG_ENTITIES = "Data/Config/entityclasses.xml"
CFG_TRADERS = "Data/Config/traders.xml"
CFG_BUFFS = "Data/Config/buffs.xml"

HEALTH_RE = re.compile(r'name="(health[A-Za-z0-9_]*)"\s*value="(\d+)"')


def extract(game_dir: str) -> dict:
    def read_if_present(path: str) -> str | None:
        if not os.path.isfile(path):
            return None
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()

    hp = {}
    epath = os.path.join(game_dir, CFG_ENTITIES)
    text = read_if_present(epath)
    if text is not None:
        m = re.search(r"<replace_passive_effect>.*?</replace_passive_effect>", text, re.S)
        block = m.group(0) if m else ""
        for name, val in HEALTH_RE.findall(block):
            hp[name] = int(val)
    trader = {}
    ttext = read_if_present(os.path.join(game_dir, CFG_TRADERS))
    if ttext is not None:
        m = re.search(r"<traders\b[^>]*>", ttext)
        if m:
            for attr in ("buy_markup", "sell_markdown"):
                am = re.search(rf'\b{attr}="([^"]+)"', m.group(0))
                if am:
                    trader[attr] = float(am.group(1))
    buffs = {}
    btext = read_if_present(os.path.join(game_dir, CFG_BUFFS))
    if btext is not None:
        # survival thresholds: StatComparePercCurrentToMax on Food/Water
        for stat in ("Food", "Water"):
            m = re.search(
                rf'StatComparePercCurrentToMax"[^>]*stat="{stat}"[^>]*operation="GT"[^>]*value="([^"]+)"',
                btext,
            )
            if m:
                buffs[f"{stat.lower()}_wellfed_threshold"] = float(m.group(1))
        buffs["hunger_buff"] = "buffStatusHungry01"
        buffs["thirst_buff"] = "buffStatusThirsty01"
    return {
        "sources": [CFG_ENTITIES, CFG_TRADERS, CFG_BUFFS],
        "entityclasses_health": hp,
        "traders_root": trader,
        "buffs_survival": buffs,
    }


def section_diffs(live: dict, committed: dict) -> list:
    """Per-key diffs across every pinned section (install value vs committed)."""
    diffs = []
    for sec in SECTIONS:
        lv, cv = live.get(sec) or {}, committed.get(sec) or {}
        for k in sorted(set(lv) | set(cv)):
            if lv.get(k) != cv.get(k):
                diffs.append(f"{sec}.{k}: install={lv.get(k)!r} pinned={cv.get(k)!r}")
    return diffs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--game-dir", default=DEFAULT_GAME)
    ap.add_argument("--check", action="store_true", help="verify committed pins vs the install")
    ap.add_argument(
        "--pins", default=DEFAULT_PINS, help="pins JSON path (default: tools/data/xml_pins.json)"
    )
    args = ap.parse_args()
    pins_path = args.pins

    if not args.check:
        epath = os.path.join(args.game_dir, CFG_ENTITIES)
        if not os.path.isfile(epath):
            print(
                f"error: {epath} not found; pass the dedicated-server root via --game-dir",
                file=sys.stderr,
            )
            return 2
        data = extract(args.game_dir)
        # A wrong --game-dir (or a renamed config section) must not wipe the
        # committed pins with empty values while reporting success. Same rule
        # for every section whose source file exists but parses to nothing.
        refusals = []
        if not data["entityclasses_health"]:
            refusals.append(f"no health* values parsed from {epath}")
        tpath = os.path.join(args.game_dir, CFG_TRADERS)
        if os.path.isfile(tpath) and not data["traders_root"]:
            refusals.append(
                f"{tpath} present but no buy_markup/sell_markdown parsed "
                "(traders <traders> header changed?)"
            )
        if refusals:
            for r in refusals:
                print(
                    f"error: {r}; refusing to overwrite {pins_path} with empty pins",
                    file=sys.stderr,
                )
            return 2
        os.makedirs(os.path.dirname(os.path.abspath(pins_path)), exist_ok=True)
        with open(pins_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1, sort_keys=True)
            f.write("\n")
        print(
            f"wrote {pins_path} ({len(data['entityclasses_health'])} hp vars, "
            f"{len(data['traders_root'])} trader attrs, "
            f"{len(data['buffs_survival'])} survival keys)"
        )
        return 0

    if not os.path.isdir(args.game_dir):
        print(f"error: game dir not found: {args.game_dir} (--game-dir)", file=sys.stderr)
        return 2
    live = extract(args.game_dir)
    if not os.path.isfile(pins_path):
        print(f"FAIL: {pins_path} missing (run xml_pins.py --game-dir first)")
        return 1
    try:
        with open(pins_path, encoding="utf-8") as fh:
            committed = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        # A corrupt pins file must read as a failed gate (with the repair
        # hint), not as a traceback with no verdict.
        print(f"FAIL: {pins_path}: {exc}")
        print("  regenerate with: python3 tools/xml_pins.py --game-dir <dir>")
        return 1
    diffs = section_diffs(live, committed)
    if diffs:
        print(f"FAIL: xml pins drift from install ({len(diffs)} diffs):")
        for d in diffs:
            print(f"  - {d}")
        return 1
    print(
        f"OK: xml pins match install ({len(committed.get('entityclasses_health', {}))} hp vars, "
        f"{len(committed.get('traders_root', {}))} trader attrs, "
        f"{len(committed.get('buffs_survival', {}))} survival keys)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
