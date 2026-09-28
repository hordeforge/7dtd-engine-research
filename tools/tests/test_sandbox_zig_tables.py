#!/usr/bin/env python3
"""Pin the sandbox Zig generators: every emitted f32 round-trips, and the
atlas RGB555 packing matches the stock formula it documents.

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

import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOLS = _common.TOOLS

_mod = _common.load_module(TOOLS / "sandbox" / "gen_zig_tables.py", "gen_zig_tables")
f32 = _mod.f32
val_literal = _mod.val_literal

_atlas = _common.load_module(TOOLS / "sandbox" / "gen_atlas_zig.py", "gen_atlas_zig")
to_color5 = _atlas.to_color5


def next_f32_up(x: float) -> float:
    """Smallest binary32 value greater than `x` (`x` must be positive)."""
    bits = struct.unpack("<I", struct.pack("<f", x))[0]
    value: float = struct.unpack("<f", struct.pack("<I", bits + 1))[0]
    return value


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


def atlas_color_bad() -> list[str]:
    """The stock `(r*31+0.5)<<10 | (g*31+0.5)<<5 | (b*31+0.5)` RGB555 packing.

    gen_atlas_zig emits two hand-typed constants beside that formula
    (water, and the Color.get_gray() fallback). Both are now derived from the
    same function, so a constant cannot contradict the derivation its own
    comment states: 0.5 scales to 16 per channel, which is 16912, not the
    16816 the file carried (that is 16,13,16, a green channel the formula
    cannot produce). Out-of-range components are clamped instead of masked, so
    a component above 1.0 does not wrap past 31 and back to 0.
    """
    out: list[str] = []
    for label, got, want in (
        ("water Color32(0,105,148)", to_color5(0.0, 105 / 255, 148 / 255), 434),
        ("Color.get_gray() 0.5", to_color5(0.5, 0.5, 0.5), 16912),
        ("black", to_color5(0.0, 0.0, 0.0), 0),
        ("white", to_color5(1.0, 1.0, 1.0), 32767),
        ("component above 1.0 clamps, not wraps", to_color5(1.5, 0.0, 0.0), 31744),
        ("component below 0.0 clamps", to_color5(-0.5, 0.0, 0.0), 0),
    ):
        if got != want:
            out.append(f"{label}: packed {got}, want {want}")
    return out


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

    bad.extend(atlas_color_bad())

    if bad:
        print("FAIL: sandbox Zig generator")
        for b in bad:
            print("  - " + b)
        return 1
    print(
        f"OK: {n} sandbox table floats + hostile probes emit f32-exact Zig literals; "
        "atlas RGB555 constants match the stock packing"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
