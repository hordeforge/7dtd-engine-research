#!/usr/bin/env python3
"""Machine-checked XML data pins: key values from the operator's Data/Config.

StockFacts.exe pins DLL constants; this pins selected XML data values that
the corpus and zdtd's provenance register cite (the zombie HP ladder from
entityclasses.xml replace_passive_effect, etc.). Values are pinned against the
installed game so a data change (or wrong claim) fails the gate.

Usage:
  python3 tools/xml_pins.py                 # check committed pins vs install (needs --game-dir)
  python3 tools/xml_pins.py --game-dir DIR  # regenerate tools/data/xml_pins.json from DIR
  python3 tools/xml_pins.py --check         # check committed pins vs the pinned install path
"""
import argparse
import json
import os
import re
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(TOOLS)
PINS = os.path.join(TOOLS, "data", "xml_pins.json")

DEFAULT_GAME = os.path.expanduser(
    "~/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server"
)
CFG_ENTITIES = "Data/Config/entityclasses.xml"
CFG_TRADERS = "Data/Config/traders.xml"
CFG_BUFFS = "Data/Config/buffs.xml"

HEALTH_RE = re.compile(r'name="(health[A-Za-z0-9_]*)"\s*value="(\d+)"')


def extract(game_dir: str) -> dict:
    hp = {}
    epath = os.path.join(game_dir, CFG_ENTITIES)
    if os.path.isfile(epath):
        text = open(epath, encoding="utf-8", errors="replace").read()
        m = re.search(r"<replace_passive_effect>.*?</replace_passive_effect>", text, re.S)
        block = m.group(0) if m else ""
        for name, val in HEALTH_RE.findall(block):
            hp[name] = int(val)
    trader = {}
    tpath = os.path.join(game_dir, CFG_TRADERS)
    if os.path.isfile(tpath):
        ttext = open(tpath, encoding="utf-8", errors="replace").read()
        m = re.search(r"<traders\b[^>]*>", ttext)
        if m:
            for attr in ("buy_markup", "sell_markdown"):
                am = re.search(rf'\b{attr}="([^"]+)"', m.group(0))
                if am:
                    trader[attr] = float(am.group(1))
    buffs = {}
    bpath = os.path.join(game_dir, CFG_BUFFS)
    if os.path.isfile(bpath):
        btext = open(bpath, encoding="utf-8", errors="replace").read()
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--game-dir", default=DEFAULT_GAME)
    ap.add_argument("--check", action="store_true", help="verify committed pins vs the install")
    args = ap.parse_args()

    if not args.check:
        data = extract(args.game_dir)
        os.makedirs(os.path.dirname(PINS), exist_ok=True)
        with open(PINS, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"wrote {PINS} ({len(data['entityclasses_health'])} hp vars)")
        return 0

    live = extract(args.game_dir)
    if not os.path.isfile(PINS):
        print(f"FAIL: {PINS} missing (run xml_pins.py --game-dir first)")
        return 1
    committed = json.load(open(PINS, encoding="utf-8"))
    if live["entityclasses_health"] != committed["entityclasses_health"]:
        diffs = {
            k: (committed["entityclasses_health"].get(k), live["entityclasses_health"].get(k))
            for k in set(live["entityclasses_health"]) | set(committed["entityclasses_health"])
            if committed["entityclasses_health"].get(k) != live["entityclasses_health"].get(k)
        }
        print(f"FAIL: xml pins drift from install ({len(diffs)} diffs): {diffs}")
        return 1
    print(f"OK: xml pins match install ({len(committed['entityclasses_health'])} hp vars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
