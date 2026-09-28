#!/usr/bin/env python3
"""Quick view of the machine-checked stock pins.

Usage: python3 tools/facts.py   (or make facts)
Reads tools/data/stock_facts.json and prints the pin + behaviour facts that
StockFacts.exe extracts from the live DLL and check_stock_facts asserts.
"""

import argparse
import pathlib
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tooling


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Print the machine-checked stock pins (census/save/xml/behaviour)."
    )
    ap.parse_args()
    try:
        return show()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        # ValueError covers both JSONDecodeError and tooling's
        # NonFiniteNumberError; KeyError is a pin file missing a section the
        # display below reads unconditionally, and TypeError is one whose top
        # level is not an object. All four mean the same thing to a reader: the
        # committed pins are unreadable, not absent.
        print(f"facts: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


def load_pins(name: str) -> dict[str, Any]:
    """One committed pin file as an object, or the error main() reports."""
    doc = tooling.load_json(tooling.TOOLS / "data" / name)
    if not isinstance(doc, dict):
        raise TypeError(f"{name}: top level is {type(doc).__name__}, not an object")
    return doc


def show() -> int:
    d = load_pins("stock_facts.json")
    v = d["version"]
    print(f"pin: {v['display']} (b{v['build']}) tps={d['sim']['constants_ticks_per_second']}")
    c = d.get("census", {})
    s = d.get("save", {})
    print(
        f"  census: top_types={c.get('top_level_types')} methods={c.get('methods_with_body_top_level')} gmupdate_il={c.get('gmupdate_il')}"
    )
    print(
        f"  save: current_save_version={s.get('current_save_version')} saveload_il={s.get('worldstate_saveload_stream_il')}"
    )
    xp = tooling.TOOLS / "data" / "xml_pins.json"
    if xp.is_file():
        xd = load_pins("xml_pins.json")
        hp = xd.get("entityclasses_health", {})
        if hp:
            print(
                f"  xml: healthSlim={hp.get('healthSlim')} feral={hp.get('healthSlimFeral')} infernal={hp.get('healthSlimInfernal')} ({len(hp)} vars)"
            )
        tr = xd.get("traders_root", {})
        if tr:
            print(
                f"  xml: traders buy_markup={tr.get('buy_markup')} sell_markdown={tr.get('sell_markdown')}"
            )
        bs = xd.get("buffs_survival", {})
        if bs:
            print(
                f"  xml: survival well-fed threshold {bs.get('food_wellfed_threshold')} ({bs.get('hunger_buff')}/{bs.get('thirst_buff')})"
            )
    en = d.get("enums", {})
    if en:
        print(
            f"  enums: GameStats={en.get('game_stats_members')} GamePrefs={en.get('game_prefs_members')}"
        )
    lite = d.get("litenet", {})
    if lite:
        print(
            f"  litenet: protocol={lite.get('protocol_id')} header={lite.get('header_size')} mtu={lite.get('possible_mtu')} max_packet={lite.get('max_packet_size')}"
        )
    for k, val in d["behaviour"].items():
        print(f"  behaviour.{k} = {val}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
