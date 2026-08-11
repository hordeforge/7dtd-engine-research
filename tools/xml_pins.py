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
CFG = "Data/Config/entityclasses.xml"

HEALTH_RE = re.compile(r'name="(health[A-Za-z0-9_]*)"\s*value="(\d+)"')


def extract(game_dir: str) -> dict:
    path = os.path.join(game_dir, CFG)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"missing {path}")
    text = open(path, encoding="utf-8", errors="replace").read()
    # only the replace_passive_effect block (the HP variable ladder)
    m = re.search(r"<replace_passive_effect>.*?</replace_passive_effect>", text, re.S)
    block = m.group(0) if m else ""
    hp = {}
    for name, val in HEALTH_RE.findall(block):
        hp[name] = int(val)
    return {"source": f"{CFG} <replace_passive_effect>", "entityclasses_health": hp}


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
