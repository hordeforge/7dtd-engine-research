const std = @import("std");
const dem = @import("dem");
pub fn main() !void {
    var gpa = std.heap.DebugAllocator(.{}){};
    const a = gpa.allocator();
    var f: dem.Fetcher = undefined;
    f.init(a, "/home/maci/.cache/zdtd-scratch");
    defer f.deinit();
    const out = try a.alloc(f32, 1024 * 1024);
    defer a.free(out);
    try f.innerTile(45, 6, 3, 0, out);
    const e = out[612 * 1024 + 24];
    std.debug.print("Mont Blanc area elevation: {d:.0} m (expect 2000-4800)\n", .{e});
    var max: f32 = 0;
    for (out) |v| { if (!std.math.isNan(v) and v > max) max = v; }
    std.debug.print("tile max: {d:.0} m\n", .{max});
}
