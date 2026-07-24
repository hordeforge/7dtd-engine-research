const std = @import("std");
const linux = std.os.linux;

fn readAll(a: std.mem.Allocator, path: []const u8) ![]u8 {
    var z: [1024]u8 = undefined;
    @memcpy(z[0..path.len], path);
    z[path.len] = 0;
    const rc = linux.open(z[0..path.len :0].ptr, .{ .ACCMODE = .RDONLY }, 0);
    if (linux.errno(rc) != .SUCCESS) return error.OpenFailed;
    const fd: i32 = @intCast(rc);
    defer _ = linux.close(fd);
    const end = linux.lseek(fd, 0, linux.SEEK.END);
    const size: usize = @intCast(end);
    _ = linux.lseek(fd, 0, linux.SEEK.SET);
    const buf = try a.alloc(u8, size);
    var off: usize = 0;
    while (off < size) {
        const n = linux.read(fd, buf[off..].ptr, size - off);
        if (linux.errno(n) != .SUCCESS) return error.ReadFailed;
        if (n == 0) break;
        off += @intCast(n);
    }
    return buf[0..off];
}

pub fn main() !void {
    var gpa = std.heap.DebugAllocator(.{}){};
    const a = gpa.allocator();
    const data = try readAll(a, "/home/maci/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/Data/Prefabs/POIs/abandoned_house_07.tts");
    const sx: i32 = std.mem.readInt(i16, data[8..10], .little);
    const sy: i32 = std.mem.readInt(i16, data[10..12], .little);
    const sz: i32 = std.mem.readInt(i16, data[12..14], .little);
    const count: usize = @intCast(@as(i64, sx) * @as(i64, sy) * @as(i64, sz));
    std.debug.print("size {d}x{d}x{d} = {d}\n", .{ sx, sy, sz, count });

    var counts = std.AutoHashMap(u16, u32).init(a);
    var i: usize = 0;
    while (i < count) : (i += 1) {
        const raw = std.mem.readInt(u32, data[14 + i * 4 ..][0..4], .little);
        if (raw & 0x40000000 != 0) continue;
        const id: u16 = @truncate(raw & 0xFFFF);
        const gop = try counts.getOrPut(id);
        gop.value_ptr.* = (if (gop.found_existing) gop.value_ptr.* else 0) + 1;
    }

    const dump = try readAll(a, "/home/maci/Desktop/7dtd/zdtd/assets/fixtures/assignids_v314.txt");
    var names = std.AutoHashMap(u16, []const u8).init(a);
    var lines = std.mem.splitScalar(u8, dump, '\n');
    while (lines.next()) |ln| {
        if (ln.len == 0 or ln[0] == '#') continue;
        const tab = std.mem.indexOfScalar(u8, ln, '\t') orelse continue;
        const idv = std.fmt.parseInt(u16, ln[0..tab], 10) catch continue;
        try names.put(idv, ln[tab + 1 ..]);
    }

    var arr: std.ArrayList(struct { id: u16, n: u32 }) = .empty;
    var it = counts.iterator();
    while (it.next()) |e| try arr.append(a, .{ .id = e.key_ptr.*, .n = e.value_ptr.* });
    const E = @TypeOf(arr.items[0]);
    std.mem.sort(E, arr.items, {}, struct {
        fn lt(_: void, x: E, y: E) bool {
            return x.n > y.n;
        }
    }.lt);
    std.debug.print("distinct ids: {d}\n", .{arr.items.len});
    var shown: usize = 0;
    for (arr.items) |e| {
        if (shown >= 30) break;
        const nm = names.get(e.id) orelse "<NOT IN DUMP>";
        std.debug.print("  id {d:>6}  x{d:<6}  {s}\n", .{ e.id, e.n, nm });
        shown += 1;
    }
}
