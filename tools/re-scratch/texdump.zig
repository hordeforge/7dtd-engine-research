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
    const version = std.mem.readInt(u32, data[4..8], .little);
    const sx: i32 = std.mem.readInt(i16, data[8..10], .little);
    const sy: i32 = std.mem.readInt(i16, data[10..12], .little);
    const sz: i32 = std.mem.readInt(i16, data[12..14], .little);
    const count: usize = @intCast(@as(i64, sx) * @as(i64, sy) * @as(i64, sz));
    std.debug.print("version {d}  size {d}x{d}x{d} = {d}\n", .{ version, sx, sy, sz, count });

    var pos: usize = 14 + count * 4; // after blocks u32 plane
    // density sbyte[count]
    if (data.len >= pos + count) pos += count;
    // damage u16[count] when version>8
    if (version > 8 and data.len >= pos + count * 2) pos += count * 2;
    std.debug.print("texture channel starts at {d} (file {d})\n", .{ pos, data.len });

    // texture sparse: bitstream then i64 per set bit
    if (version >= 10 and pos + 4 <= data.len) {
        const n = std.mem.readInt(i32, data[pos..][0..4], .little);
        std.debug.print("bitstream bytes: {d}\n", .{n});
        const bits = data[pos + 4 ..][0..@intCast(n)];
        var texpos = pos + 4 + @as(usize, @intCast(n));
        var set: usize = 0;
        var shown: usize = 0;
        var bit_i: usize = 0;
        const total = bits.len * 8;
        while (bit_i < total) : (bit_i += 1) {
            const byte = bits[bit_i / 8];
            const bit: u3 = @intCast(bit_i % 8);
            if ((byte >> bit) & 1 == 0) continue;
            if (texpos + 8 > data.len) break;
            const tf = std.mem.readInt(u64, data[texpos..][0..8], .little);
            texpos += 8;
            set += 1;
            if (shown < 12 and tf != 0) {
                // unpack 6 faces (assume 6x ~ bytes or bitfields)
                std.debug.print("  painted cell offset {d}: textureFull=0x{x} faces=[{d},{d},{d},{d},{d},{d}]\n", .{
                    bit_i, tf,
                    tf & 0x3f,        (tf >> 6) & 0x3f,  (tf >> 12) & 0x3f,
                    (tf >> 18) & 0x3f, (tf >> 24) & 0x3f, (tf >> 30) & 0x3f,
                });
                shown += 1;
            }
        }
        std.debug.print("total painted cells (set bits with i64): {d}\n", .{set});
    }
}
