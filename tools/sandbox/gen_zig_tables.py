#!/usr/bin/env python3
"""Generate src/assets/sandbox_data.zig in zdtd from sandbox_tables.json.

The value sets and per-option records come from the stock DLL
(SandboxOptionManager.SetupOptions IL + <PrivateImplementationDetails> FieldRVA
arrays); see docs/sandbox-options.md and extract_sandbox_tables.py in this
repo. zdtd embeds them at comptime so the server can decode an operator's
sandbox code without re-extraction; the JSON here is the source of truth.

Usage: python3 gen_zig_tables.py sandbox_tables.json ../zdtd-server/src/assets/sandbox_data.zig
"""

import json
import struct
import sys
from json import dumps as zstr


def f32(x: float) -> float:
    """`x` rounded to the nearest IEEE-754 binary32 value (Zig `f32` width)."""
    return struct.unpack("<f", struct.pack("<f", x))[0]


def val_literal(v):
    """JSON value -> Zig literal; floats as the shortest decimal that
    re-parses to the same binary32 value.

    A fixed-precision round loses f32 values that sit further than half an
    ulp from any 6-decimal number (binary32 1.0000001 would emit as 1.0).
    """
    if isinstance(v, float):
        want = f32(v)
        for digits in range(10):
            r = round(v, digits)
            if f32(r) == want:
                return repr(r)
        return repr(want)
    return str(v)


def emit(json_path: str, out_path: str) -> None:
    t = json.load(open(json_path, encoding="utf-8"))
    vs = t["valuesets"]
    opts = t["options"]

    out = []
    out.append("//! Stock sandbox value-set and option tables, generated from")
    out.append("//! `../7dtd-engine-research/tools/sandbox/sandbox_tables.json` by")
    out.append("//! `../7dtd-engine-research/tools/sandbox/gen_zig_tables.py` (do not hand-edit).")
    out.append("//! Source of truth: `SandboxOptionManager.SetupOptions` IL of the stock")
    out.append("//! V3.1.0 b14 dedicated server (docs/sandbox-options.md §2.1/§3 in the")
    out.append("//! 7dtd-engine-research repo). Decode contract: code := 'A' + 3-letter groups")
    out.append("//! (2-letter base-26 option id + 1-letter value-set index).")
    out.append("")
    out.append("pub const Kind = enum(u8) { float, int, boolean };")
    out.append("")
    out.append("pub const ValueSet = struct {")
    out.append("    name: []const u8,")
    out.append("    kind: Kind,")
    out.append("    floats: []const f32,")
    out.append("    ints: []const i32,")
    out.append("};")
    out.append("")
    out.append("pub const Option = struct {")
    out.append(
        "    /// SandboxOptions enum value (wire-stable; the codec addresses options by it)."
    )
    out.append("    id: u16,")
    out.append("    /// SandboxOptions enum member name.")
    out.append("    name: []const u8,")
    out.append("    set_name: []const u8,")
    out.append("    kind: Kind,")
    out.append("    default_f: f32,")
    out.append("    default_i: i32,")
    out.append("};")
    out.append("")
    out.append("/// All 65 value sets (stock data).")
    out.append("pub const value_sets = [_]ValueSet{")
    for name in sorted(vs):
        v = vs[name]
        if v["type"] == "float":
            floats = ", ".join(val_literal(x) for x in v["values"])
            out.append(
                f"    .{{ .name = {zstr(name)}, .kind = .float, .floats = &.{{ {floats} }}, .ints = &.{{}} }},"
            )
        elif v["type"] == "int":
            ints = ", ".join(val_literal(x) for x in v["values"])
            out.append(
                f"    .{{ .name = {zstr(name)}, .kind = .int, .floats = &.{{}}, .ints = &.{{ {ints} }} }},"
            )
        else:
            out.append(
                f"    .{{ .name = {zstr(name)}, .kind = .boolean, .floats = &.{{}}, .ints = &.{{}} }},"
            )
    out.append("};")
    out.append("")
    out.append("/// All 165 options, in id order (stock data).")
    out.append("pub const options = [_]Option{")
    for o in opts:
        d = o["default"]
        if o["type"] == "float":
            df = val_literal(d if d is not None else 0.0)
            di = "0"
        elif o["type"] == "int":
            df = "0.0"
            di = str(d if d is not None else 0)
        else:
            df = "0.0"
            di = "0"
        kind = "float" if o["type"] == "float" else ("int" if o["type"] == "int" else "boolean")
        out.append(
            f"    .{{ .id = {o['id']}, .name = {zstr(o['name'])}, "
            f".set_name = {zstr(o['valueset'])}, .kind = .{kind}, "
            f".default_f = {df}, .default_i = {di} }},"
        )
    out.append("};")
    out.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"wrote {out_path}: {len(vs)} value sets, {len(opts)} options")


if __name__ == "__main__":
    emit(sys.argv[1], sys.argv[2])
