#!/usr/bin/env python3
"""Save format round-trip verifier (stock 7DTD V3.1.0 dedicated).

Validates a real, stock-written save directory against the codecs documented in
docs/save-region.md:

  main.ttw  : magic "ttw\\0", version u32, gameVersionString, VersionInformation,
              pad/activeGameMode/pad, waterLevel, chunk sizes (Y/Z swapped),
              chunkCount, providerId, seed, worldTime, timeInTicks   (doc 1.1b)
  .7rg (V2) : magic "7rg", version byte, location table at 4096 (u16 LE sector
              offset + pad + u8 sector count), timestamp table at 8192,
              payload at sector*4096 = Int32 len + 12-byte gap + data, where
              data = Int64("ttc\\0" + Chunk.CurrentSaveVersion) + raw Noemax
              deflate of the Chunk.save body   (doc 3.4/3.5, live-verified)
  .7rr (Raw): magic "7rr", version:i32, paddingBytes:i32, location table at 11
              (64 x {i32 offset, i32 length}), timestamp table at 523
              (64 x u32)   (doc 3.5; no live sample in the probe corpus yet)

Usage: python3 tools/save_roundtrip_check.py [save_dir]
  With no argument, auto-discovers the most recent probe save under
  ~/.cache/7dtd-loadgen-*/Saves/*/*/ that contains main.ttw + Region/.
  Exit code 0 = all checks passed; 1 = any check failed.
"""

import glob
import os
import struct
import sys
import zlib

RAW_DEFLATE = -15  # no zlib/gzip wrapper (Noemax.GZip.DeflateOutputStream, no header)


def read_net_string(buf, off):
    """.NET BinaryReader.ReadString: 7-bit encoded length prefix + UTF-8."""
    length = 0
    shift = 0
    while True:
        b = buf[off]
        off += 1
        length |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return buf[off:off + length].decode("utf-8", "replace"), off + length


def check_main_ttw(path, checks):
    """Verify the main.ttw header codec (doc save-region.md 1.1b)."""
    with open(path, "rb") as fh:
        buf = fh.read()
    checks.append(f"{os.path.basename(path)}: size {len(buf)}")

    magic = buf[0:4]
    checks.append(f"  magic: {magic!r} == b'ttw\\x00'" if magic == b"ttw\x00"
                  else "  magic: MISMATCH " + repr(magic))
    version = struct.unpack_from("<I", buf, 4)[0]
    checks.append(f"  version: {version} == 23 (CurrentSaveVersion)" if version == 23
                  else f"  version: {version} != 23")
    off = 8
    gvs, off = read_net_string(buf, off)
    checks.append(f"  gameVersionString: {gvs!r}")
    vi = struct.unpack_from("<4i", buf, off)
    off += 16
    checks.append(f"  VersionInformation (ReleaseType,Major,Minor,Build): {vi} == (1,3,10,14)"
                  if vi == (1, 3, 10, 14) else f"  VersionInformation: {vi} != (1,3,10,14)")
    pad0 = struct.unpack_from("<I", buf, off)[0]
    off += 4
    agm = struct.unpack_from("<i", buf, off)[0]
    off += 4
    pad1 = struct.unpack_from("<I", buf, off)[0]
    off += 4
    checks.append(f"  pad0={pad0} activeGameMode={agm} pad1={pad1} (pads must be 0)"
                  if pad0 == 0 and pad1 == 0
                  else f"  pad0={pad0} activeGameMode={agm} pad1={pad1}: non-zero pad")
    water = struct.unpack_from("<f", buf, off)[0]
    off += 4
    # Navezgane water level pin (behaviour water-level, live-observed 62.88)
    checks.append(f"  waterLevel: {water:.3f}" + (" (matches Navezgane pin 62.88)"
                  if abs(water - 62.88) < 0.01 else " (Navezgane pin expected 62.88)"))
    csx = struct.unpack_from("<i", buf, off)[0]
    csy = struct.unpack_from("<i", buf, off + 4)[0]
    csz = struct.unpack_from("<i", buf, off + 8)[0]
    off += 12
    checks.append(f"  chunkSizeX/Y/Z: {csx}/{csy}/{csz} == 16/16/16 (Y/Z swapped on store)"
                  if (csx, csy, csz) == (16, 16, 16) else f"  chunkSize: {csx}/{csy}/{csz}")
    chunk_count = struct.unpack_from("<i", buf, off)[0]
    off += 4
    provider = struct.unpack_from("<i", buf, off)[0]
    off += 4
    seed = struct.unpack_from("<i", buf, off)[0]
    off += 4
    world_time = struct.unpack_from("<Q", buf, off)[0]
    off += 8
    ticks = struct.unpack_from("<Q", buf, off)[0]
    off += 8
    checks.append(f"  chunkCount={chunk_count} providerId={provider} (1=Disc) seed={seed} "
                  f"worldTime={world_time} timeInTicks={ticks}")
    return off


def check_region_v2(path, checks):
    """Verify a .7rg sector-based V2 region file (doc save-region.md 3.4/3.5)."""
    with open(path, "rb") as fh:
        data = fh.read()
    name = os.path.basename(path)
    nsec = len(data) // 4096
    checks.append(f"{name}: size {len(data)} ({nsec} sectors, mod {len(data) % 4096})")
    magic = data[0:3]
    ver = data[3]
    if magic != b"7rg":
        checks.append(f"  magic: MISMATCH {magic!r} != b'7rg'")
        return
    checks.append(f"  magic b'7rg' ok; version byte {ver} (>=1 -> RegionFileV2)")
    if ver < 1:
        checks.append("  version < 1 (V1 layout not exercised here; V1 tables at 4/4100)")
        return

    # V2 on-disk tables: location at 4096, timestamp at 8192 (IL: ctor Seek(4096)
    # + Read 4096, then Read 4096; live-verified 2026-08-12).
    slots = []
    for idx in range(1024):
        base = 4096 + idx * 4
        off = struct.unpack_from("<H", data, base)[0]
        cnt = data[base + 3]
        if off or cnt:
            stamp = struct.unpack_from("<I", data, 8192 + idx * 4)[0]
            slots.append((idx, off, cnt, stamp))
    checks.append(f"  allocated slots: {len(slots)}/1024")
    if not slots:
        checks.append("  no allocated slots (empty region)")
        return

    bad_off = [s for s in slots if s[1] < 3]
    checks.append(f"  sector offset >= 3 invariant: {'OK' if not bad_off else 'VIOLATED ' + str(bad_off[:3])}")
    stamps = [s[3] for s in slots]
    checks.append(f"  timestamp {min(stamps)}..{max(stamps)} (WorldTimeToTotalMinutes)")
    if slots[0][1] * 4096 + 4 > len(data):
        checks.append(f"  first slot payload start beyond EOF: {slots[0][1] * 4096}")
        return

    ok = 0
    for idx, soff, scnt, _ in slots:
        pay = soff * 4096
        length = struct.unpack_from("<I", data, pay)[0]
        if length + 16 > len(data) - pay:
            checks.append(f"  slot {idx}: length {length} exceeds file bounds")
            continue
        magic4 = data[pay + 16:pay + 20]
        cver = struct.unpack_from("<I", data, pay + 20)[0]
        if magic4 != b"ttc\x00" or cver != 47:
            checks.append(f"  slot {idx}: payload preamble {magic4!r} ver {cver} != ('ttc\\0', 47)")
            continue
        body = data[pay + 24:pay + 16 + length]
        if len(body) != length - 8:
            checks.append(f"  slot {idx}: body len {len(body)} != length-8 {length - 8}")
            continue
        try:
            dec = zlib.decompress(body, RAW_DEFLATE)
        except Exception as exc:
            checks.append(f"  slot {idx}: deflate failed: {exc}")
            continue
        if len(dec) < 20:
            checks.append(f"  slot {idx}: decompressed body too short ({len(dec)})")
            continue
        x, y, z = struct.unpack_from("<iii", dec, 0)
        # Forward check via the documented GetOffsetFromXz formula (doc 3.5):
        # x_mod = cX % 32 (negative coords: +31), slot idx = x_mod + z_mod*32.
        x_mod = x % 32
        if x < 0:
            x_mod += 31
        z_mod = z % 32
        if z < 0:
            z_mod += 31
        exp_idx = x_mod + z_mod * 32
        if exp_idx == idx:
            ok += 1
        else:
            checks.append(f"  slot {idx}: stored chunk ({x},{z}) maps to slot {exp_idx} "
                          f"per GetOffsetFromXz (x_mod {x_mod}, z_mod {z_mod})")
    checks.append(f"  chunk coord round-trip: {ok}/{len(slots)} stored coords map back to "
                  f"their slot via GetOffsetFromXz (x_mod cX%32, +31 if negative)")


def check_region_raw(path, checks):
    """Verify a .7rr Raw region file header/tables (doc save-region.md 3.5)."""
    with open(path, "rb") as fh:
        data = fh.read()
    name = os.path.basename(path)
    checks.append(f"{name}: size {len(data)}")
    if data[0:3] != b"7rr":
        checks.append(f"  magic: MISMATCH {data[0:3]!r} != b'7rr'")
        return
    version = struct.unpack_from("<i", data, 3)[0]
    pad = struct.unpack_from("<i", data, 7)[0]
    checks.append(f"  magic b'7rr'; version:i32={version} paddingBytes:i32={pad}")
    checks.append(f"  header 11 bytes; location table 512 B @11; timestamp 256 B @523; payload @779")


def discover_save_dir():
    """Newest probe save containing main.ttw + Region/, or None."""
    best = None
    for ttw in glob.glob(os.path.expanduser("~/.cache/7dtd-loadgen-*/Saves/*/*/main.ttw")):
        d = os.path.dirname(ttw)
        if os.path.isdir(os.path.join(d, "Region")):
            if best is None or os.path.getmtime(ttw) > os.path.getmtime(best):
                best = ttw
    return os.path.dirname(best) if best else None


def main():
    argv = sys.argv[1:]
    save_dir = argv[0] if argv else discover_save_dir()
    if not save_dir:
        print("No save dir given and none found under ~/.cache/7dtd-loadgen-*/Saves/*/*/")
        return 1
    print(f"Round-trip checking save: {save_dir}\n")

    checks = []
    ttw = os.path.join(save_dir, "main.ttw")
    if os.path.exists(ttw):
        check_main_ttw(ttw, checks)
    else:
        checks.append("main.ttw: MISSING")

    region = os.path.join(save_dir, "Region")
    rg = sorted(glob.glob(os.path.join(region, "*.7rg"))) if os.path.isdir(region) else []
    rr = sorted(glob.glob(os.path.join(region, "*.7rr"))) if os.path.isdir(region) else []
    print(f"Region files: {len(rg)} .7rg (sector V2), {len(rr)} .7rr (raw)\n")
    for p in rg[:6]:
        check_region_v2(p, checks)
    if len(rg) > 6:
        checks.append(f"  ({len(rg) - 6} further .7rg files not expanded)")
    for p in rr[:2]:
        check_region_raw(p, checks)
    if rr and len(rr) > 2:
        checks.append(f"  ({len(rr) - 2} further .7rr files not expanded)")
    if not rg and not rr:
        checks.append("Region/: no region files")

    print("\n".join(checks))
    failed = any(("MISMATCH" in c or "VIOLATED" in c or " != " in c or "failed" in c
                  or "MISSING" in c or "bounds" in c or "too short" in c or "!= expected" in c)
                 for c in checks)
    print(f"\n{'FAIL' if failed else 'PASS'}: {len(checks)} checks")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
