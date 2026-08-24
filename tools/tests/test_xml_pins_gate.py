#!/usr/bin/env python3
"""xml_pins.py verifies every committed section against the live install.

The pin gate extracts three sections (entityclasses_health, traders_root,
buffs_survival), commits all three to tools/data/xml_pins.json, and downstream
consumers cite values from each. The --check diff used to cover only
entityclasses_health, so trader-markup or buff-threshold drift passed as a
green gate; regeneration likewise wiped only-guarded sections. These fixtures
pin the full-section contract with synthetic Data/Config XML:

  - regenerate writes every section and --check passes on an unchanged install
  - drift in ANY section fails --check (traders, buffs, health)
  - regeneration refuses to overwrite populated sections when a source file
    parses to nothing (wrong --game-dir or renamed config section)

Runs entirely in a temp dir via --pins/--game-dir; never touches tools/data.

Usage: python3 tools/tests/test_xml_pins_gate.py
"""

import json
import os
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(TOOLS, "xml_pins.py")

ENTITYCLASSES = """<configs>
  <replace_passive_effect>
    <property name="healthSlim" value="125"/>
    <property name="healthSlimFeral" value="500"/>
    <property name="healthBrute" value="950"/>
  </replace_passive_effect>
</configs>
"""

TRADERS = """<traders buy_markup="3.0" sell_markdown="0.2">
</traders>
"""

BUFFS = """<buffs>
  <requirement name="wellfed" action="StatComparePercCurrentToMax" stat="Food" operation="GT" value="0.52"/>
  <requirement name="hydrated" action="StatComparePercCurrentToMax" stat="Water" operation="GT" value="0.52"/>
</buffs>
"""


def run(*argv):
    proc = subprocess.run([sys.executable, SCRIPT, *argv], capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def write_config(game_dir, name, text):
    cfg = os.path.join(game_dir, "Data", "Config")
    os.makedirs(cfg, exist_ok=True)
    with open(os.path.join(cfg, name), "w", encoding="utf-8") as f:
        f.write(text)


def build_install(game_dir):
    write_config(game_dir, "entityclasses.xml", ENTITYCLASSES)
    write_config(game_dir, "traders.xml", TRADERS)
    write_config(game_dir, "buffs.xml", BUFFS)


def main():
    bad = []
    with tempfile.TemporaryDirectory(prefix="xml-pins-gate-") as tmp:
        game = os.path.join(tmp, "game")
        pins = os.path.join(tmp, "pins.json")
        build_install(game)

        # 1. Regenerate writes all sections.
        rc, out = run("--game-dir", game, "--pins", pins)
        if rc != 0:
            bad.append(f"regenerate failed on well-formed install (rc={rc}):\n{out}")
        else:
            with open(pins, encoding="utf-8") as f:
                data = json.load(f)
            for sec, want in [
                ("entityclasses_health", {"healthSlim": 125}),
                ("traders_root", {"buy_markup": 3.0, "sell_markdown": 0.2}),
                ("buffs_survival", {"food_wellfed_threshold": 0.52}),
            ]:
                for k, v in want.items():
                    if data.get(sec, {}).get(k) != v:
                        bad.append(f"{sec}.{k}={data.get(sec, {}).get(k)!r} != {v!r}")

        # 2. Unchanged install passes --check.
        rc, out = run("--check", "--game-dir", game, "--pins", pins)
        if rc != 0:
            bad.append(f"--check failed on unchanged install (rc={rc}):\n{out}")

        # 3. Trader drift must FAIL (the gap this suite pins: the check used to
        #    diff only entityclasses_health and trader drift passed silently).
        write_config(game, "traders.xml", TRADERS.replace('buy_markup="3.0"', 'buy_markup="2.5"'))
        rc, out = run("--check", "--game-dir", game, "--pins", pins)
        if rc != 1 or "traders_root.buy_markup" not in out:
            bad.append(f"trader drift not detected (rc={rc}):\n{out}")

        # 4. Buff-threshold drift must FAIL too.
        write_config(game, "traders.xml", TRADERS)
        write_config(
            game,
            "buffs.xml",
            BUFFS.replace(
                'stat="Food" operation="GT" value="0.52"', 'stat="Food" operation="GT" value="0.6"'
            ),
        )
        rc, out = run("--check", "--game-dir", game, "--pins", pins)
        if rc != 1 or "buffs_survival.food_wellfed_threshold" not in out:
            bad.append(f"buff drift not detected (rc={rc}):\n{out}")

        # 5. Health drift still FAILS.
        write_config(game, "buffs.xml", BUFFS)
        write_config(
            game,
            "entityclasses.xml",
            ENTITYCLASSES.replace('name="healthSlim" value="125"', 'name="healthSlim" value="400"'),
        )
        rc, out = run("--check", "--game-dir", game, "--pins", pins)
        if rc != 1 or "entityclasses_health.healthSlim" not in out:
            bad.append(f"health drift not detected (rc={rc}):\n{out}")

        # 6. Wrong game dir (no parseable health values) refuses to wipe pins.
        write_config(game, "entityclasses.xml", ENTITYCLASSES)
        with open(pins, encoding="utf-8") as f:
            before = f.read()
        empty_game = os.path.join(tmp, "empty-game")
        os.makedirs(os.path.join(empty_game, "Data", "Config"))
        write_config(empty_game, "entityclasses.xml", "<configs></configs>\n")
        rc, out = run("--game-dir", empty_game, "--pins", pins)
        if rc != 2 or "refusing to overwrite" not in out:
            bad.append(f"empty-health regenerate not refused (rc={rc}):\n{out}")

        # 7. traders.xml present but its pinned header gone -> refuse to wipe.
        write_config(empty_game, "traders.xml", "<traders>\n</traders>\n")
        rc, out = run("--game-dir", empty_game, "--pins", pins)
        if rc != 2 or "refusing to overwrite" not in out:
            bad.append(f"trader-wipe regenerate not refused (rc={rc}):\n{out}")
        with open(pins, encoding="utf-8") as f:
            if f.read() != before:
                bad.append("committed pins were modified by refused regenerations")

    if bad:
        print("FAIL: xml_pins gate")
        for b in bad:
            print("  - " + b)
        return 1
    print("OK: xml_pins verifies every section; drift fails; refusals leave pins intact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
