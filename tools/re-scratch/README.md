# re-scratch: one-off reversing tools

Small standalone Zig programs used while reverse-engineering the stock 7DTD
client wire and file formats. Run with `zig run <file>.zig`.

| Tool | What it dumps |
|---|---|
| `ttsdump.zig` | Distinct block-type ids in a prefab `.tts`, cross-referenced against an AssignIds name dump (found the `woodShapes:*` house ids). |
| `texdump.zig` | The sparse texture channel of a `.tts` (per-cell `textureFull` paint), used to prove paint-driven shape blocks carry material `0x61` (wood). |
| `dem_probe.zig` | Probe a Copernicus GLO-30 COG tile (elevation sanity check). |
| `chunk_size.zig` | Scratch size math for the stock chunk wire. |

Paths come from `argv` (`zig run <file>.zig -- <paths>`); nothing here reads a
hardcoded install location. These tools use raw Linux syscalls and only build
on Linux targets.
