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
for k, val in d["behaviour"].items():
    print(f"  behaviour.{k} = {val}")
