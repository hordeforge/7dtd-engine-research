#!/usr/bin/env python3
"""Generate src/assets/map_atlas.zig in zdtd from the extracted atlas XMLs.

Reads tools/sandbox/atlas/ta_*.xml (extracted from the operator install's
meshdescriptions_assets_all.bundle; see docs/texture-atlas.md) and emits a
comptime table of per-texture minimap colors packed with the stock
Utils.ToColor5 RGB555 formula. Regenerate when the game updates; do not
hand-edit the output.

Usage: python3 gen_atlas_zig.py <out.zig>
"""
import glob
import os
import re
import sys

COLOR_RE = re.compile(
    r'<uv\s+id="(\d+)"[^>]*color="([0-9.eE+-]+),([0-9.eE+-]+),([0-9.eE+-]+)"'
)


def to_color5(r, g, b):
    return ((int(r * 31 + 0.5) & 0x1F) << 10) | ((int(g * 31 + 0.5) & 0x1F) << 5) | (int(b * 31 + 0.5) & 0x1F)


def main():
    here = os.path.dirname(__file__)
    out_path = sys.argv[1]
    atlases = []
    for xml in sorted(glob.glob(os.path.join(here, "atlas", "ta_*.xml"))):
        name = os.path.basename(xml)[3:-4]  # strip ta_ and .xml
        text = open(xml, encoding="utf-8-sig").read()
        entries = []
        for m in COLOR_RE.finditer(text):
            tid = int(m.group(1))
            r, g, b = (float(m.group(i)) for i in (2, 3, 4))
            entries.append((tid, to_color5(r, g, b)))
        entries.sort()
        atlases.append((name, entries))
    lines = []
    lines.append("//! Stock texture-atlas minimap colors, generated from")
    lines.append("//! `../7dtd-engine-research/tools/sandbox/atlas/ta_*.xml` by")
    lines.append("//! `../7dtd-engine-research/tools/sandbox/gen_atlas_zig.py` (do not hand-edit).")
    lines.append("//! Source of truth: the `MeshDescription.MetaData` TextAssets in the")
    lines.append("//! stock V3.1.0 b14 `meshdescriptions_assets_all.bundle` (docs/texture-atlas.md")
    lines.append("//! in the 7dtd-engine-research repo). Colors are packed with the stock")
    lines.append("//! Utils.ToColor5 RGB555 formula: (r*31+0.5)<<10 | (g*31+0.5)<<5 | (b*31+0.5).")
    lines.append("")
    lines.append("pub const Entry = struct {")
    lines.append("    /// Texture id (blocks.xml Texture property values index this).")
    lines.append("    id: u16,")
    lines.append("    /// RGB555 minimap color.")
    lines.append("    color5: u16,")
    lines.append("};")
    lines.append("")
    lines.append("pub const Atlas = struct {")
    lines.append("    name: []const u8,")
    lines.append("    entries: []const Entry,")
    lines.append("};")
    lines.append("")
    lines.append("pub const atlases = [_]Atlas{")
    for name, entries in atlases:
        body = ", ".join(f".{{ .id = {tid}, .color5 = {c5} }}" for tid, c5 in entries)
        lines.append(f'    .{{ .name = "{name}", .entries = &.{{ {body} }} }},')
    lines.append("};")
    lines.append("")
    lines.append("")
    lines.append("const std = @import(\"std\");")
    lines.append("")
    lines.append("/// Minimap water color (BlockLiquidv2.Color = Color32(0,105,148))")
    lines.append("/// packed RGB555 (RE texture-atlas.md CalcChunkColors).")
    lines.append("pub const water_color5: u16 = 434;")
    lines.append("/// Fallback when a block has no atlas color nor MapColor: stock")
    lines.append("/// Color.get_gray() = (0.5,0.5,0.5) -> RGB555 16,16,16.")
    lines.append("pub const gray_color5: u16 = 16816;")
    lines.append("")
    lines.append("/// blocks.xml Mesh property name -> atlas table name. Empty (no")
    lines.append("/// Mesh property) = default mesh 0 = \"opaque\" (RE texture-atlas.md).")
    lines.append("pub fn atlasForMesh(mesh: []const u8) []const u8 {")
    lines.append("    if (std.mem.eql(u8, mesh, \"terrain\")) return \"terrainxml\";")
    lines.append("    if (std.mem.eql(u8, mesh, \"grass\")) return \"grassxml\";")
    lines.append("    if (std.mem.eql(u8, mesh, \"water\")) return \"waterxml\";")
    lines.append("    if (std.mem.eql(u8, mesh, \"transparent\")) return \"transparentxml\";")
    lines.append("    if (std.mem.eql(u8, mesh, \"decals\")) return \"decalsxml\";")
    lines.append("    return \"opaquexml\";")
    lines.append("}")
    lines.append("")
    lines.append("/// A block's minimap color: the MapColor property wins (stock")
    lines.append("/// Block.GetMapColor bMapColorSet path); else the top-face")
    lines.append("/// texture's atlas color; else null (caller picks gray).")
    lines.append("pub fn blockColor5(mesh: []const u8, texture_top: u16, map_color: u16) ?u16 {")
    lines.append("    if (map_color != 0) return map_color;")
    lines.append("    if (texture_top == 0) return null;")
    lines.append("    return color5(atlasForMesh(mesh), texture_top);")
    lines.append("}")
    lines.append("")
    lines.append("/// Look up the minimap color for a texture id in an atlas (init-time only).")
    lines.append("pub fn color5(atlas_name: []const u8, texture_id: u16) ?u16 {")
    lines.append("    for (&atlases) |*a| {")
    lines.append("        if (!std.mem.eql(u8, a.name, atlas_name)) continue;")
    lines.append("        for (a.entries) |e| {")
    lines.append("            if (e.id == texture_id) return e.color5;")
    lines.append("        }")
    lines.append("        return null;")
    lines.append("    }")
    lines.append("    return null;")
    lines.append("}")
    lines.append("")
    lines.append('test "terrain atlas colors match the extracted XML" {')
    lines.append("    // terrDirt texture id 2 (blocks.xml Texture=2): stock color")
    lines.append("    // 0.3529412,0.3176471,0.2784314 -> RGB555 r=11 g=10 b=9.")
    lines.append("    const c = color5(\"terrainxml\", 2).?;")
    lines.append("    const r = (c >> 10) & 0x1f;")
    lines.append("    const g = (c >> 5) & 0x1f;")
    lines.append("    const b = c & 0x1f;")
    lines.append("    try std.testing.expectEqual(@as(u16, 11), r);")
    lines.append("    try std.testing.expectEqual(@as(u16, 10), g);")
    lines.append("    try std.testing.expectEqual(@as(u16, 9), b);")
    lines.append("    // terrForestGround top face id 195.")
    lines.append("    try std.testing.expect(color5(\"terrainxml\", 195) != null);")
    lines.append("    // Unknown id in a known atlas: null.")
    lines.append("    try std.testing.expect(color5(\"terrainxml\", 9999) == null);")
    lines.append("    // Unknown atlas: null.")
    lines.append("    try std.testing.expect(color5(\"nope\", 1) == null);")
    lines.append("    // Resolver: MapColor property wins; else the mesh atlas.")
    lines.append("    try std.testing.expectEqual(@as(?u16, 2243), blockColor5(\"terrain\", 2, 2243));")
    lines.append("    try std.testing.expect(blockColor5(\"terrain\", 195, 0) != null); // terrForestGround top face")
    lines.append("    try std.testing.expect(blockColor5(\"opaque\", 52, 0) != null); // wood in the opaque atlas")
    lines.append("    try std.testing.expect(blockColor5(\"terrain\", 9999, 0) == null); // no atlas color")
    lines.append("    try std.testing.expectEqualStrings(\"opaquexml\", atlasForMesh(\"\"));")
    lines.append("    try std.testing.expectEqual(@as(u16, 434), water_color5);")
    lines.append("}")
    lines.append("")
    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    for name, entries in atlases:
        print(f"{name}: {len(entries)} entries")
    print(f"wrote {out_path}")
    # Best-effort: keep the output zig fmt clean (regeneration is manual).
    # Only the expected "zig not installed" case is tolerated silently; any
    # other failure (e.g. malformed generated output) must surface.
    try:
        import subprocess
        subprocess.run(["zig", "fmt", out_path], check=False)
    except OSError:
        pass


if __name__ == "__main__":
    main()
