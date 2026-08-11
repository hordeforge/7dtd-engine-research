#!/usr/bin/env python3
"""Quick view of the machine-checked stock pins.

Usage: python3 tools/facts.py   (or make facts)
Reads tools/data/stock_facts.json and prints the pin + behaviour facts that
StockFacts.exe extracts from the live DLL and check_stock_facts asserts.
"""
import json
import os

TOOLS = os.path.dirname(os.path.abspath(__file__))
facts_path = os.path.join(TOOLS, "data", "stock_facts.json")
d = json.load(open(facts_path, encoding="utf-8"))
v = d["version"]
print(f"pin: {v['display']} (b{v['build']}) tps={d['sim']['constants_ticks_per_second']}")
c = d.get("census", {})
s = d.get("save", {})
print(f"  census: top_types={c.get('top_level_types')} methods={c.get('methods_with_body_top_level')} gmupdate_il={c.get('gmupdate_il')}")
print(f"  save: current_save_version={s.get('current_save_version')} saveload_il={s.get('worldstate_saveload_stream_il')}")
xp = os.path.join(TOOLS, "data", "xml_pins.json")
if os.path.isfile(xp):
    xd = json.load(open(xp, encoding="utf-8"))
    hp = xd.get("entityclasses_health", {})
    if hp:
        print(f"  xml: healthSlim={hp.get('healthSlim')} feral={hp.get('healthSlimFeral')} infernal={hp.get('healthSlimInfernal')} ({len(hp)} vars)")
    tr = xd.get("traders_root", {})
    if tr:
        print(f"  xml: traders buy_markup={tr.get('buy_markup')} sell_markdown={tr.get('sell_markdown')}")
    bs = xd.get("buffs_survival", {})
    if bs:
        print(f"  xml: survival well-fed threshold {bs.get('food_wellfed_threshold')} ({bs.get('hunger_buff')}/{bs.get('thirst_buff')})")
lite = d.get("litenet", {})
if lite:
    print(f"  litenet: protocol={lite.get('protocol_id')} header={lite.get('header_size')} mtu={lite.get('possible_mtu')} max_packet={lite.get('max_packet_size')}")
for k, val in d["behaviour"].items():
    print(f"  behaviour.{k} = {val}")
