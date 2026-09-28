#!/usr/bin/env python3
"""assignids_dump.py: the block-id pipeline must reproduce the fixed pins.

The tool regenerates the AssignIds table that backs the id columns in
`docs/world/blocks.md` and the zdtd fixture beside it, so a wrong id there is
a wrong claim in the corpus, not a bad dump. The pins are already fixed by
`Block.fixedBlockIds` and are stated in the tool's own README: air=0,
terrStone=1, water=240, terrWaterPOI=241, waterdata=242. Everything else
follows the stock `assignLeftOverBlocks` order, and the two id bands it scans
(terrain from 0, everything else from 255) are the property a synthetic
fixture can pin without a stock install.

The fixtures are hand-written blocks.xml/shapes.xml in a temp dir, so the
expectations are the pipeline's own rules rather than whatever a live install
holds. The shapes a group expands to, the Bulletproof subset, the terrain band
and the generator band are each checked against a value worked out by hand.

Usage: python3 tools/tests/test_assignids_dump.py
"""

from __future__ import annotations

import functools
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOL = _common.TOOLS / "assignids_dump.py"
run = functools.partial(_common.run_cli, TOOL)

SHAPES = """<?xml version="1.0"?>
<shapes>
  <shape name="Cube" />
  <shape name="Wall" />
  <shape name="Bprof" tag="Bulletproof" />
  <shape name="TerrainShape" />
</shapes>
"""
# Order matters twice over: the group expansion takes every shape in document
# order, and a self-closing block element (no <property> children) must not
# borrow the next block's Shape.
BLOCKS = """<?xml version="1.0"?>
<blocks>
  <block name="air" />
  <block name="terrStone">
    <property name="Shape" value="Terrain" />
    <property name="Material" value="stone" />
  </block>
  <block name="terrWood" />
  <block name="terrFence">
    <property name="Shape" value="Terrain" />
  </block>
  <block name="cntWoodenChestClosed" shapes="All" />
  <block name="woodWall" shapes="Bulletproof" />
  <block name="water" />
  <block name="terrWaterPOI" />
  <block name="waterdata" />
</blocks>
"""


def ids(out: str) -> dict[str, int]:
    rows: dict[str, int] = {}
    for line in Path(out).read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        number, name = line.split("\t", 1)
        assert name not in rows, f"{name} took two ids in one run: {rows[name]} and {number}"
        rows[name] = int(number)
    return rows


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="assignids-", dir=_common.scratch_dir()) as td:
        cfg = Path(td) / "Config"
        cfg.mkdir()
        (cfg / "shapes.xml").write_text(SHAPES, encoding="utf-8")
        (cfg / "blocks.xml").write_text(BLOCKS, encoding="utf-8")
        out = Path(td) / "assignids.txt"

        result = run(str(cfg), str(out))
        assert result.returncode == 0, result
        rows = ids(str(out))

        # The fixed table is the whole point of the pin: these five ids come
        # from Block.cctor, not from the scan, so no arrangement of the
        # document can move them.
        for name, want in (("air", 0), ("water", 240), ("terrWaterPOI", 241), ("waterdata", 242)):
            assert rows.get(name) == want, f"{name} is {rows.get(name)}, not the fixed {want}"
        # The first free id above 0 goes to the first non-fixed terrain block.
        # A self-closing block element has no properties to read a Shape out
        # of, so terrWood is not terrain: matching its body to the next
        # </block> would hand it that block's Shape and put it in the wrong
        # band. The terrain band therefore holds exactly the two blocks that
        # declare Shape=Terrain.
        assert rows.get("terrStone") == 1, rows
        assert rows.get("terrFence") == 2, rows
        assert rows.get("terrWood") == 255, rows
        # Every shape a group expands to is emitted, in shapes.xml document
        # order, and the group block itself takes no id.
        assert rows.get("cntWoodenChestClosed:Cube") == 256, rows
        assert rows.get("cntWoodenChestClosed:Wall") == 257, rows
        assert rows.get("cntWoodenChestClosed:Bprof") == 258, rows
        assert rows.get("cntWoodenChestClosed:TerrainShape") == 259, rows
        assert "cntWoodenChestClosed" not in rows, rows
        # A Bulletproof group takes only the tagged shape, and the ids continue
        # from where the previous block left off rather than restarting.
        assert rows.get("woodWall:Bprof") == 260, rows
        assert "woodWall:Cube" not in rows, rows
        # Nothing lands in the reserved band above 242 and below the 255 the
        # generator band starts at.
        assert not [i for i in rows.values() if 242 < i < 255], rows
        assert len(rows) == len(set(rows.values())), "two names took one id"
        # The emitted file carries the pins in its header, so a reader of the
        # artifact (not the tool) can see what it was regenerated from.
        header = Path(out).read_text(encoding="utf-8").splitlines()[:2]
        assert any("air=0" in line for line in header), header

        # Rerunning over the same input is the same table, byte for byte.
        again = Path(td) / "again.txt"
        assert run(str(cfg), str(again)).returncode == 0
        assert again.read_text(encoding="utf-8") == out.read_text(encoding="utf-8"), (
            "a second run over the same input produced a different table"
        )

        # A group naming a shape set the pipeline does not know is a hard stop,
        # not a block silently emitted with no variants.
        bad_cfg = Path(td) / "BadConfig"
        bad_cfg.mkdir()
        (bad_cfg / "shapes.xml").write_text(SHAPES, encoding="utf-8")
        (bad_cfg / "blocks.xml").write_text(
            '<blocks><block name="x" shapes="Nonesuch" /></blocks>', encoding="utf-8"
        )
        unknown = run(str(bad_cfg), str(Path(td) / "bad.txt"))
        assert unknown.returncode != 0, unknown
        assert "Nonesuch" in unknown.stderr, unknown.stderr
        assert not (Path(td) / "bad.txt").exists(), "a refused run still wrote its output file"

        # A directory that is not a Data/Config is a usage error naming the
        # file it is missing, not a run that writes an empty table.
        empty_cfg = Path(td) / "Empty"
        empty_cfg.mkdir()
        not_config = run(str(empty_cfg), str(Path(td) / "nope.txt"))
        assert not_config.returncode == 2, not_config
        assert "no blocks.xml" in not_config.stderr, not_config.stderr
        assert not (Path(td) / "nope.txt").exists(), "a refused run still wrote its output file"
        # The usage line is stderr with exit 2, so `--help` stays the one
        # stdout path.
        usage = run()
        assert usage.returncode == 2, usage
        assert usage.stdout == "", usage.stdout
        assert "assignids_dump.py" in usage.stderr, usage.stderr
        helped = run("--help")
        assert helped.returncode == 0, helped
        assert "Usage: assignids_dump.py" in helped.stdout, helped.stdout
    print("OK: assignids_dump reproduces the fixed block ids and both id bands")


if __name__ == "__main__":
    main()
