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
    checks.append(f"  chunkCount={chunk_count} providerId={provider} (4=ChunkDataDriven, "
                  f"the Navezgane/RWG value; 1=Disc) seed={seed} "
                  f"worldTime={world_time} timeInTicks={ticks}")

    # --- full WorldState tail (version 23 gates; WorldState.SaveLoad IL=926) ---
    try:
        sp_ver = buf[off]
        off += 1
        sp_cnt = struct.unpack_from("<i", buf, off)[0]
        off += 4
        for _ in range(sp_cnt):
            if sp_ver == 2:
                off += 2  # legacy u16
            off += 12 + 4  # Vector3 + heading
            off += 8  # team + activeInGameMode
        next_id = struct.unpack_from("<i", buf, off)[0]
        off += 4
        sdl = struct.unpack_from("<q", buf, off)[0]
        off += 8
        checks.append(f"  spawnList(ver {sp_ver}, {sp_cnt}) nextEntityID={next_id} "
                      f"saveDataLimit={sdl}")
        blob_sizes = []
        for name in ("dynamicSpawnerState", "aiDirectorState"):
            ln = struct.unpack_from("<i", buf, off)[0]
            off += 4
            blob_sizes.append(ln)
            off += ln
        vol_sizes = []
        for name in ("sleeperVolumes", "triggerVolumes", "wallVolumes"):
            sv = struct.unpack_from("<i", buf, off)[0]
            off += 4
            ln = struct.unpack_from("<i", buf, off)[0]
            off += 4
            vol_sizes.append((sv, ln))
            off += ln
        checks.append(f"  blobs dyn={blob_sizes[0]} ai={blob_sizes[1]} "
                      f"volumes(v,bytes)={vol_sizes}")
        w_sz = struct.unpack_from("<i", buf, off)[0]
        off += 4
        checks.append(f"  weather size prefix {w_sz} (includes itself: {w_sz - 4} B payload)")
        if w_sz > 4:
            off += w_sz - 4
        guid, off = read_net_string(buf, off)
        checks.append(f"  guid: {guid[:8]}... len {len(guid)}")
        exact = off == len(buf)
        checks.append(f"  full WorldState parse {'byte-exact' if exact else 'MISMATCH'} "
                      f"({off}/{len(buf)})")
    except (struct.error, IndexError) as exc:
        checks.append(f"  WorldState tail parse error: {exc}")
    return off


def parse_chunk_body(body, name, idx, checks):
    """Fully parse a decompressed Chunk.save body (Chunk.write IL=601) and
    require it to consume the body byte-exactly.

    Returns (coords_ok, exact_ok). When entities or tile entities are present
    (variable-length nested formats not deep-parsed here), exact_ok is False
    with a reason recorded.
    """
    p = 0
    n = len(body)

    def need(k):
        return p + k <= n

    def rd(fmt, k):
        nonlocal p
        if not need(k):
            raise ValueError(f"truncated at {p}/{n}")
        v = struct.unpack_from(fmt, body, p)
        p += k
        return v

    x, y, z = rd("<iii", 12)
    ticks = rd("<Q", 8)[0]
    coords_ok = True
    # C# remainder semantics (Python % differs for negatives): r = a - trunc(a/b)*b
    x_mod = x - int(x / 32) * 32
    if x < 0:
        x_mod += 31
    z_mod = z - int(z / 32) * 32
    if z < 0:
        z_mod += 31
    if x_mod + z_mod * 32 != idx:
        coords_ok = False
        checks.append(f"  slot {idx}: stored chunk ({x},{z}) maps to slot "
                      f"{x_mod + z_mod * 32}, not {idx}")

    layers = 0
    for _ in range(64):
        if rd("<b", 1)[0]:
            layers += 1
            if rd("<b", 1)[0]:
                p += 1024
            else:
                p += 1
            if rd("<b", 1)[0]:
                p += 3072
    if not need(0):
        raise ValueError("truncated in layer block")

    def channel(bpv):
        nonlocal p
        for _ in range(64):
            flag = rd("<b", 1)[0]
            if flag == 0:
                p += bpv * 1024
            elif flag == 1:
                p += bpv
            else:
                raise ValueError(f"bad channel flag {flag}")

    channel(1)  # chnStability (file only)

    # Maps are written RAW: PooledBinaryWriter.Write(byte[]) (IL=14) emits no
    # length prefix. Sizes from Chunk.read IL=775: HeightMap 256, TerrainHeight
    # 256, TopSoilBroken 32 (version > 41), Biomes 256, BiomeIntensities 1536.
    p += 256 + 256 + 32 + 256 + 1536
    d_biome, am_biome = rd("<bb", 2)

    custom = rd("<H", 2)[0]
    for _ in range(custom):
        _, p = read_net_string(body, p)
        p += 8  # expiresInWorldTime u64
        p += 1  # isSavedToNetwork bool
        dlen = rd("<H", 2)[0]
        p += dlen  # data bytes

    # normal maps: 3 x 256 raw (no length prefix)
    p += 256 * 3

    channel(1)  # chnDensity
    channel(1)  # chnLight
    channel(2)  # chnDamage
    channel(6)  # chnTextures[0]
    channel(2)  # chnWater

    rd("<b", 1)  # NeedsLightCalculation

    entities = rd("<i", 4)[0]
    reason = ""
    if entities:
        reason += f"{entities} entities present (format not deep-parsed); "
        return coords_ok, False, reason
    te_count = rd("<i", 4)[0]
    if te_count:
        reason += f"{te_count} tile entities present (format not deep-parsed); "
        return coords_ok, False, reason
    rd("<b", 1)  # always false (file path)

    def volume():
        nonlocal p
        cnt = rd("<B", 1)[0]
        p += cnt * 4

    volume()  # sleeperVolumes
    volume()  # triggerVolumes
    volume()  # wallVolumes

    dev_count = rd("<h", 2)[0]
    for _ in range(dev_count):  # insideDevices runs: x, z, len, len y bytes
        xb, zb, ln = rd("<BBB", 3)
        p += ln

    rd("<b", 1)  # IsInternalBlocksCulled

    td_count = rd("<h", 2)[0]
    if td_count:
        reason += f"{td_count} triggerData present; "
        return coords_ok, False, reason
    for _ in range(td_count):
        p += 12  # Vector3i LocalChunkPos
        p += 2 + 1 + 1  # version u16 + NeedsTriggered byte + TriggersIndices count byte
        p += body[p - 1]
        p += 1  # TriggeredByIndices count byte
        p += body[p - 1]

    if p != n:
        raise ValueError(f"body parse ended at {p}/{n}")

    check_str = (f"  slot {idx}: chunk ({x},{z}) ticks={ticks} layers={layers}/64 "
                 f"biome=({d_biome},{am_biome}) custom={custom} "
                 f"entities=0 te=0 devices={dev_count} culled ok; byte-exact "
                 f"body parse ({n} B)")
    checks.append(check_str if coords_ok else check_str + " [coord mismatch above]")
    return coords_ok, True, ""


def check_decoration_7dt(path, checks):
    """Verify decoration.7dt: version byte 6 + i32 count + 17-byte records
    (packedPos u64 + realYPos f32 + bv.rawData u32 + state u8)."""
    with open(path, "rb") as fh:
        data = fh.read()
    name = os.path.basename(path)
    ver = data[0]
    cnt = struct.unpack_from("<i", data, 1)[0]
    expect = 5 + cnt * 17
    ok = ver == 6 and expect == len(data)
    checks.append(f"{name}: version byte {ver} count {cnt} "
                  f"{'byte-exact' if ok else f'MISMATCH ({expect} expected, {len(data)} got)'} "
                  f"(17 B records: packedPos u64 + realYPos f32 + rawData u32 + state u8)")
    if cnt and ok:
        pos, ry, raw, state = struct.unpack_from("<QfIB", data, 5)
        checks.append(f"  first record: packedPos={pos} realY={ry:.1f} raw=0x{raw:x} state={state}")


def check_nim_mapping(path, checks):
    """Verify *.nim id-name mapping: u32 version + u32 count + (u32 id + u8
    nameLen + name), byte-exact."""
    with open(path, "rb") as fh:
        data = fh.read()
    name = os.path.basename(path)
    ver, cnt = struct.unpack_from("<II", data, 0)
    p = 8
    ids = set()
    try:
        for _ in range(cnt):
            bid = struct.unpack_from("<I", data, p)[0]
            ids.add(bid)
            nl = data[p + 4]
            p += 5 + nl
    except (struct.error, IndexError):
        p = -1
    ok = p == len(data)
    checks.append(f"{name}: version {ver} count {cnt} unique_ids {len(ids)} "
                  f"{'byte-exact' if ok else f'MISMATCH (consumed {p}/{len(data)})'}")


def check_multiblocks_7dt(path, checks):
    """Verify multiblocks.7dt: version byte 6 + i32 count + 17-byte records
    (Vector3i pos + rawData u32 + trackingTypeFlags u8). MultiBlockManager
    SaveIfDirty IL=107."""
    with open(path, "rb") as fh:
        data = fh.read()
    name = os.path.basename(path)
    ver = data[0]
    cnt = struct.unpack_from("<i", data, 1)[0]
    expect = 5 + cnt * 17
    ok = ver == 6 and expect == len(data)
    checks.append(f"{name}: version byte {ver} count {cnt} "
                  f"{'byte-exact' if ok else f'MISMATCH ({expect} expected, {len(data)} got)'} "
                  f"(17 B records: Vector3i + rawData u32 + flags u8)")
    if cnt and ok:
        x, y, z, raw, flags = struct.unpack_from("<iiiIB", data, 5)
        checks.append(f"  first record: pos=({x},{y},{z}) raw=0x{raw:x} flags={flags}")


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
        try:
            coords_ok, exact_ok, reason = parse_chunk_body(dec, name, idx, checks)
        except (ValueError, struct.error) as exc:
            checks.append(f"  slot {idx}: body parse error: {exc}")
            continue
        if exact_ok and coords_ok:
            ok += 1
        elif reason:
            checks.append(f"  slot {idx}: {reason}")
    checks.append(f"  full body round-trip: {ok}/{len(slots)} chunks parse byte-exactly "
                  f"(coords + layers + maps + channels + volumes + devices)")


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

    deco = os.path.join(save_dir, "decoration.7dt")
    if os.path.exists(deco):
        check_decoration_7dt(deco, checks)
    mb = os.path.join(save_dir, "multiblocks.7dt")
    if os.path.exists(mb):
        check_multiblocks_7dt(mb, checks)
    for nim in ("blockmappings.nim", "itemmappings.nim"):
        np_ = os.path.join(save_dir, nim)
        if os.path.exists(np_):
            check_nim_mapping(np_, checks)

    print("\n".join(checks))
    failed = any(("MISMATCH" in c or "VIOLATED" in c or " != " in c or "failed" in c
                  or "MISSING" in c or "bounds" in c or "too short" in c or "!= expected" in c
                  or "parse error" in c)
                 for c in checks)
    print(f"\n{'FAIL' if failed else 'PASS'}: {len(checks)} checks")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
