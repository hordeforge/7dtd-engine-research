#!/usr/bin/env python3
"""Pin sandbox gen_zig_tables float literals: every emitted f32 round-trips.

gen_zig_tables.py turns the stock sandbox_tables.json floats (binary32 values
read out of Assembly-CSharp RVA data) into Zig `f32` comptime literals that
zdtd embeds as its source of truth. The old emitter formatted through a fixed
`round(v, 6)`, which silently collapses any f32 that sits further than half an
ulp from a 6-decimal number (binary32 1.0000001 -> "1.0"): the generated table
then disagrees with the stock DLL while looking plausible. This gate asserts,
for every float in the pinned dataset and for known hostile probes, that
float(x) of the emitted literal is bit-identical at binary32 width. Stdlib
only, DLL-free, network-free.

Usage: python3 tools/tests/test_sandbox_zig_tables.py
"""

from __future__ import annotations

import importlib.util
import json
import struct
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "gen_zig_tables", TOOLS / "sandbox" / "gen_zig_tables.py"
)
assert _spec is not None
assert _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
f32 = _mod.f32
val_literal = _mod.val_literal


def next_f32_up(x: float) -> float:
    """Smallest binary32 value greater than `x` (`x` must be positive)."""
    bits = struct.unpack("<I", struct.pack("<f", x))[0]
    return struct.unpack("<f", struct.pack("<I", bits + 1))[0]


def dataset_floats() -> list[float]:
    t = json.loads((TOOLS / "sandbox" / "sandbox_tables.json").read_text(encoding="utf-8"))
    vals: list[float] = []
    for v in t["valuesets"].values():
        if v["type"] == "float":
            vals.extend(float(x) for x in v["values"])
    for o in t["options"]:
        if o["type"] == "float" and o["default"] is not None:
            vals.append(float(o["default"]))
    return vals


def main() -> int:
    bad = []

    # Every pinned stock value must emit a literal that parses back to the
    # identical binary32 bits.
    n = 0
    for x in dataset_floats():
        lit = val_literal(x)
        if f32(float(lit)) != f32(x):
            bad.append(f"sandbox_tables value {x!r} emitted {lit!r}, not f32-exact")
        n += 1
    if n == 0:
        bad.append("no floats found in sandbox_tables.json (extractor broke?)")

    # Hostile probes: exact f32 successors of clean decimals. Each sits more
    # than half an ulp from any 6-decimal number, so the legacy round(v, 6)
    # emitter collapsed all of them onto the base decimal; all must survive.
    for base in (0.5, 1.0, 2.0, 16.0):
        x = next_f32_up(base)
        lit = val_literal(x)
        if f32(float(lit)) != x:
            bad.append(f"probe {x!r} collapsed to literal {lit!r}")

    # Non-float passthrough stays plain.
    if val_literal(7) != "7":
        bad.append(f"int literal changed: {val_literal(7)!r}")

    if bad:
        print("FAIL: gen_zig_tables float round-trip")
        for b in bad:
            print("  - " + b)
        return 1
    print(f"OK: {n} sandbox table floats + hostile probes emit f32-exact Zig literals")
    return 0


if __name__ == "__main__":
    sys.exit(main())
