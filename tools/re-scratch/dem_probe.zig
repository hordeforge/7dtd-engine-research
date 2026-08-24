const std = @import("std");
const dem = @import("dem");
pub fn main(init: std.process.Init.Minimal) !void {
    var gpa = std.heap.DebugAllocator(.{}){};
    const a = gpa.allocator();
    var argv = init.args.iterate();
    _ = argv.next(); // program name
    const cache_dir = argv.next() orelse {
        std.debug.print("usage: dem_probe <scratch-cache-dir>\n", .{});
        return error.Usage;
    };
    var f: dem.Fetcher = undefined;
    f.init(a, cache_dir);
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
