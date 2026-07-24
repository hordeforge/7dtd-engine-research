# Wire frames (visual) · 7DTD V3.0.1

**Owns:** left-to-right byte/field strips for envelope + golden packages (classic protocol style).  
**Companion:** narrative join/policy in [protocol.md](protocol.md).  
**Evidence:** loadgen `PackageCodec` · dedi-complete census.  
**Clone:** [`../../zdtd/`](../../zdtd).

## How to read these diagrams

Frames are drawn **left → right** in wire order (first byte on the left).  
Multi-row packages continue on the next line, still left → right.

```text
  offset →    0        1        2        3        4        5        …
              | field  | field           | field                    |
              +--------+-----------------+--------------------------+
```

| Convention | Value |
|---|---|
| Endianness | multi-byte integers/floats are **little-endian** |
| Packing | **no padding**; fields abut |
| `bool` | 1 byte |
| `string` | .NET BinaryWriter: 7-bit length + UTF-8 (variable width) |
| `pkgId` | dynamic; written as `ID` in diagrams |
| Units under bars | byte counts |

Mermaid `block-beta` strips are the same idea: one horizontal row, spans ≈ sizes. No nested boxes.

---

## 1. Challenge (raw, before game envelope)

17 bytes total. **Not** inside the channel envelope.

```text
 offset   0          1                                                              16
          +----------+---------------------------------------------------------------+
          |   0xCA   |                      Guid (16 bytes)                          |
          |  marker  |                                                               |
          +----------+---------------------------------------------------------------+
 size:        1      |                             16                                |
```

| Off | Len | Bits / meaning |
|---:|---:|---|
| 0 | 1 | Protocol marker `0xCA` (202) |
| 1 | 16 | Challenge Guid; client echoes **all 17 bytes** |

```mermaid
block-beta
  columns 17
  m["0xCA"]:1
  g["Guid ···"]:16
  style m fill:#c0392b,color:#fff
  style g fill:#2980b9,color:#fff
```

---

## 2. Game channel envelope + package stream

After challenge, every LiteNet game message is one horizontal stream:

```text
 offset   0     1              5      6      7        9
          +-----+--------------+------+------+---------+------------------//
          | ch  | payloadSize  | cmp  | enc  | pkgCount|  payload …        //
          | u8  |    i32 LE    | u8   | u8   |  u16 LE |  (payloadSize B)  //
          +-----+--------------+------+------+---------+------------------//
 size:      1   |      4       |  1   |  1   |    2    |  payloadSize
```

| Off | Len | Field | Protocol note |
|---:|---:|---|---|
| 0 | 1 | channel | bots use `0` |
| 1 | 4 | payloadSize | bytes that follow this 9-byte header |
| 5 | 1 | compressed | `0` = raw (golden path) |
| 6 | 1 | encrypted | `0` = clear (golden path) |
| 7 | 2 | pkgCount | number of inner packages in payload |
| 9 | * | payload | see §2.1 |

**Invariant:** `frame_len = 9 + payloadSize`.

```mermaid
block-beta
  columns 9
  ch["ch"]:1
  ps["payloadSize"]:4
  c["cmp"]:1
  e["enc"]:1
  n["pkgCount"]:2
  style ch fill:#8e44ad,color:#fff
  style ps fill:#2980b9,color:#fff
  style c fill:#7f8c8d,color:#fff
  style e fill:#7f8c8d,color:#fff
  style n fill:#16a085,color:#fff
```

### 2.1 Inner package (repeated `pkgCount` times inside payload)

Still left → right; consecutive packages are concatenated.

```text
 +----------------+----------+---------------------------//
 |   contentLen   |  pkgId   |  body                     //
 |    i32 LE      |  u16 LE  |  (contentLen − 2) bytes   //
 +----------------+----------+---------------------------//
        4         |    2     |     contentLen − 2
```

| Field | Protocol note |
|---|---|
| contentLen | size of **pkgId + body only** (not including contentLen itself) |
| pkgId | type id from PackageIds map |
| body | package-specific payload |

```text
 contentLen = 2 + body_len
```

```mermaid
block-beta
  columns 8
  cl["contentLen"]:4
  id["pkgId"]:2
  bd["body ···"]:2
  style cl fill:#d35400,color:#fff
  style id fill:#c0392b,color:#fff
  style bd fill:#27ae60,color:#fff
```

### 2.2 Empty body package (AuthConfirmation, RequestToEnterGame)

```text
 envelope: ch | payloadSize=6 | 0 | 0 | pkgCount=1
 payload:  contentLen=2 | pkgId=ID
 +-----+--------------+---+---+--------+----------------+----------+
 | ch  | payloadSize=6| 0 | 0 | count=1 | contentLen = 2 |  pkgId   |
 +-----+--------------+---+---+--------+----------------+----------+
    1         4         1   1     2             4            2
 frame_len = 15
```

```mermaid
block-beta
  columns 15
  ch["ch"]:1
  ps["ps=6"]:4
  z0["0"]:1
  z1["0"]:1
  n["n=1"]:2
  cl["cl=2"]:4
  id["ID"]:2
  style ch fill:#8e44ad,color:#fff
  style ps fill:#2980b9,color:#fff
  style cl fill:#d35400,color:#fff
  style id fill:#c0392b,color:#fff
```

---

## 3. Version blob (inside PackageIds body)

13 bytes, left → right:

```text
 +------+--------------+--------------+--------------+
 | rel  |    major     |    minor     |    build     |
 | u8   |    i32 LE    |    i32 LE    |    i32 LE    |
 +------+--------------+--------------+--------------+
     1         4              4              4
```

Golden live: `rel=1, major=3, minor=1, build=4` → display **`V 3.0.1`**.

```mermaid
block-beta
  columns 13
  r["rel"]:1
  maj["major"]:4
  min["minor"]:4
  b["build"]:4
  style r fill:#8e44ad,color:#fff
  style maj fill:#3498db,color:#fff
  style min fill:#1abc9c,color:#fff
  style b fill:#f39c12,color:#fff
```

---

## 4. PackageIds body (after envelope + pkgId)

Logical stream (variable length):

```text
 +-------------+----------+------------//-----------+--------+----------+
 |   Version   |  count   |  name[0] … name[count-1] | useEac | hasHost  |
 |   13 bytes  |  i32 LE  |  strings (BinaryWriter)  |  bool  |  bool    |
 +-------------+----------+------------//-----------+--------+----------+
       13      |    4     |         variable         |   1    |    1
```

| Segment | Meaning |
|---|---|
| Version | §3 |
| count | number of type names |
| name[i] | C# type name; **index i is pkgId i** |
| useEac | server EAC flag |
| hasHost | if true, more platform-user fields follow |

```mermaid
block-beta
  columns 12
  v["Version 13"]:3
  c["count"]:2
  names["type names × count"]:5
  eac["EAC"]:1
  host["host"]:1
  style v fill:#8e44ad,color:#fff
  style c fill:#2980b9,color:#fff
  style names fill:#27ae60,color:#fff
  style eac fill:#c0392b,color:#fff
  style host fill:#7f8c8d,color:#fff
```

Live head (hex, channel 0, one package, pkgId 0):

```text
00 | BC120000 | 00 | 00 | 0100 | B8120000 | 0000 | 01 03000000 01000000 04000000 | BD000000 | …
ch   ps=4796    c    e    n=1    contentLen  ID=0   version 1/3/1/4                    count=189
```

---

## 5. PlayerLogin body

Variable-width string stream (left → right):

```text
 +------+--------+-------+--------+-------+---------+----------+------------+
 | name | platU  | platT | crossU | crossT| verLong | compVer  | discordId  |
 | str  | stream | str   | stream | str   | str     | str      |   u64 LE   |
 +------+--------+-------+--------+-------+---------+----------+------------+
   var     var     var     var     var      var       var           8
```

### PlatformUser stream (embedded)

```text
 null:   +---+
         | 0 |
         +---+
          1

 present:+---+----+----------+---------+
         | 1 | 1  | platform | userId  |
         |tag|tag2|  string  | string  |
         +---+----+----------+---------+
           1   1       var        var
```

```mermaid
block-beta
  columns 10
  n["name"]:1
  pu["platU"]:1
  pt["platT"]:1
  cu["crossU"]:1
  ct["crossT"]:1
  v["verLong"]:1
  cv["compVer"]:1
  d["discord u64"]:3
  style n fill:#3498db,color:#fff
  style pu fill:#9b59b6,color:#fff
  style d fill:#f39c12,color:#fff
```

---

## 6. RequestToSpawnPlayer body

```text
 +--------------+---------------------------//------------+----------------+
 | chunkViewDim |      PlayerProfile v5                   | nearEntityId   |
 |    i16 LE    |  ver i32 | strings/bools…               |    i32 LE      |
 +--------------+---------------------------//------------+----------------+
        2       |           variable                      |       4
```

Profile v5 order: `version=5 | archetype str | isMale | race str | variant u8 | hair | hairColor | mustache | chops | beard | eyeColor`.

```mermaid
block-beta
  columns 10
  cvd["viewDim i16"]:2
  pv["profile…"]:6
  near["nearId i32"]:2
  style cvd fill:#2980b9,color:#fff
  style pv fill:#8e44ad,color:#fff
  style near fill:#c0392b,color:#fff
```

---

## 7. EntityPosAndRot body (!bUseQ) · 30 bytes

```text
 0        4        8        12       16  17       21       25       29  30
 +--------+--------+--------+--------+---+--------+--------+--------+---+
 |entityId|   x    |   y    |   z    |q=0|  rotX  |  rotY  |  rotZ  | g |
 |  i32   |  f32   |  f32   |  f32   |u8 |  f32   |  f32   |  f32   |u8 |
 +--------+--------+--------+--------+---+--------+--------+--------+---+
      4        4        4        4     1      4        4        4     1
```

| Off | Len | Field | Notes |
|---:|---:|---|---|
| 0 | 4 | entityId | |
| 4 | 4 | pos.x | IEEE-754 f32 LE |
| 8 | 4 | pos.y | |
| 12 | 4 | pos.z | |
| 16 | 1 | bUseQRotation | `0` ⇒ Euler floats follow |
| 17 | 4 | rot.x | degrees as f32 |
| 21 | 4 | rot.y | |
| 25 | 4 | rot.z | |
| 29 | 1 | onGround | |
| 30 | | end | contentLen = **32** with pkgId |

```mermaid
block-beta
  columns 30
  e["eid"]:4
  x["x"]:4
  y["y"]:4
  z["z"]:4
  q["0"]:1
  rx["rX"]:4
  ry["rY"]:4
  rz["rZ"]:4
  g["g"]:1
  style e fill:#c0392b,color:#fff
  style x fill:#3498db,color:#fff
  style y fill:#3498db,color:#fff
  style z fill:#3498db,color:#fff
  style q fill:#7f8c8d,color:#fff
  style rx fill:#9b59b6,color:#fff
  style ry fill:#9b59b6,color:#fff
  style rz fill:#9b59b6,color:#fff
  style g fill:#27ae60,color:#fff
```

---

## 8. EntityRelPosAndRot body (!bUseQ) · 20 bytes

```text
 0        4  5    7    9    11   13   15   17 18     20
 +--------+--+----+----+----+----+----+----+--+------+
 |entityId|q0|rX  |rY  |rZ  | dx | dy | dz |g |steps |
 |  i32   |  |i16 |i16 |i16 |i16 |i16 |i16 |  | i16  |
 +--------+--+----+----+----+----+----+----+--+------+
      4    1   2    2    2    2    2    2   1    2
```

| Off | Len | Field | Notes |
|---:|---:|---|---|
| 0 | 4 | entityId | |
| 4 | 1 | bUseQRotation | `0` ⇒ i16 rot, **no** quat |
| 5 | 2 | rotX | packed: deg/360×256 → i16 |
| 7 | 2 | rotY | |
| 9 | 2 | rotZ | |
| 11 | 2 | dx | relative translation |
| 13 | 2 | dy | |
| 15 | 2 | dz | |
| 17 | 1 | onGround | |
| 18 | 2 | updateSteps | |
| 20 | | end | contentLen = **22** with pkgId |

```mermaid
block-beta
  columns 20
  e["eid"]:4
  q["0"]:1
  rx["rX"]:2
  ry["rY"]:2
  rz["rZ"]:2
  dx["dx"]:2
  dy["dy"]:2
  dz["dz"]:2
  g["g"]:1
  s["st"]:2
  style e fill:#c0392b,color:#fff
  style q fill:#7f8c8d,color:#fff
  style rx fill:#9b59b6,color:#fff
  style ry fill:#9b59b6,color:#fff
  style rz fill:#9b59b6,color:#fff
  style dx fill:#2980b9,color:#fff
  style dy fill:#2980b9,color:#fff
  style dz fill:#2980b9,color:#fff
  style g fill:#27ae60,color:#fff
  style s fill:#d35400,color:#fff
```

### Same package, bUseQ = 1 · body 30 bytes

```text
 +--------+--+------------------+--+----+
 |entityId|q1| qx qy qz qw (4×f32) |dPos| g |steps|
 |  i32   |  |       16 bytes      |6B  |1B | i16 |
 +--------+--+---------------------+----+---+-----+
      4    1            16            6   1    2   = 30
```

Do **not** emit both Euler i16 and quat on the same write.

---

## 9. EntityAliveFlags body · 6 bytes

```text
 +--------+--------+
 |entityId| flags  |
 |  i32   |  u16   |
 +--------+--------+
      4        2
```

```mermaid
block-beta
  columns 6
  e["entityId"]:4
  f["flags"]:2
  style e fill:#c0392b,color:#fff
  style f fill:#f39c12,color:#fff
```

### flags u16 (bit 0 = LSB, left in this bit row is bit 0)

```text
 bit:  0   1   2   3   4   5   6   7   8   9  10…15
      +---+---+---+---+---+---+---+---+---+---+----
      | E | P | G | S | J | B | A | F |Gm | C | 0…
      +---+---+---+---+---+---+---+---+---+---+----
 E  ApproachingEnemy   0x0001
 P  ApproachingPlayer  0x0002
 G  AimingGun          0x0004
 S  Spawned            0x0008
 J  Jumping            0x0010
 B  BreakingBlocks     0x0020
 A  IsAlert            0x0040
 F  FlashlightOn       0x0080
 Gm GodMode            0x0100
 C  Crouching          0x0200
```

```mermaid
block-beta
  columns 10
  b0["E"]:1
  b1["P"]:1
  b2["Aim"]:1
  b3["Sp"]:1
  b4["J"]:1
  b5["Br"]:1
  b6["Al"]:1
  b7["Fl"]:1
  b8["Gd"]:1
  b9["Cr"]:1
  style b3 fill:#27ae60,color:#fff
  style b4 fill:#e74c3c,color:#fff
  style b9 fill:#3498db,color:#fff
```

---

## 10. EntityLookAt body · 16 bytes

```text
 +--------+--------+--------+--------+
 |entityId| lookX  | lookY  | lookZ  |
 |  i32   |  i32   |  i32   |  i32   |
 +--------+--------+--------+--------+
      4        4        4        4
```

(Look floats are cast to int on write.)

```mermaid
block-beta
  columns 16
  e["eid"]:4
  x["lX"]:4
  y["lY"]:4
  z["lZ"]:4
  style e fill:#c0392b,color:#fff
  style x fill:#1abc9c,color:#fff
  style y fill:#1abc9c,color:#fff
  style z fill:#1abc9c,color:#fff
```

---

## 11. DamageEntity body (prefix, left → right)

Fixed head through `blockPos` (then variable string + tail; see protocol.md for full tail):

```text
 0        4  5  6    8  9   11 12 13 14 15       19              31              43
 +--------+--+--+----+--+---+--+--+--+--+--------+---------------+---------------+
 |entityId|s |t |str |hd|bp |ms|p |f |c |attacker|    dirV 3×f32 | blockPos 3×i32|
 |  i32   |u8|u8|u16 |u8|i16|u8|… bools…|  i32   |      12 B     |     12 B      |
 +--------+--+--+----+--+---+--+--+--+--+--------+---------------+---------------+
```

| Off | Len | Field | Protocol bits |
|---:|---:|---|---|
| 0 | 4 | entityId | target |
| 4 | 1 | damageSource | 0 External, 1 Internal |
| 5 | 1 | damageType | 3 Bash, 16 Suffocation (drown), 26 Suicide, … |
| 6 | 2 | strength | u16 |
| 8 | 1 | hitDirection | |
| 9 | 2 | hitBodyPart | i16 |
| 11 | 1 | movementState | |
| 12 | 1 | bPainHit | |
| 13 | 1 | bFatal | |
| 14 | 1 | bCritical | |
| 15 | 4 | attackerEntityId | |
| 19 | 12 | dirV | 3×f32 |
| 31 | 12 | blockPos | 3×i32 |
| 43 | * | hitTransformName + tail | var |

```mermaid
block-beta
  columns 16
  e["eid"]:3
  s["src"]:1
  t["typ"]:1
  st["str"]:2
  hd["hd"]:1
  bp["bp"]:2
  ms["ms"]:1
  b["pfc"]:2
  a["atk"]:3
  style e fill:#c0392b,color:#fff
  style s fill:#d35400,color:#fff
  style t fill:#d35400,color:#fff
  style b fill:#e74c3c,color:#fff
  style a fill:#8e44ad,color:#fff
```

---

## 12. ExplosionInitiate body (segments, L→R)

```text
 +-------------+-------------+----------------+------------------+------------------//
 | worldPos    | blockPos    | rotation quat  | blobLen + blob   | eid · delay · …  //
 |  3×f32 = 12 |  3×i32 = 12 |  4×f32 = 16    | u16 + data       | rest of package  //
 +-------------+-------------+----------------+------------------+------------------//
```

```mermaid
block-beta
  columns 12
  w["worldPos 12"]:3
  b["blockPos 12"]:3
  r["quat 16"]:3
  bl["blob"]:2
  t["tail"]:1
  style w fill:#3498db,color:#fff
  style b fill:#2980b9,color:#fff
  style r fill:#9b59b6,color:#fff
  style bl fill:#d35400,color:#fff
```

---

## 13. Full frame: one RelPos on the wire (35 bytes)

Envelope + single RelPos body (channel 0, cleartext):

```text
body=20  contentLen=22  payloadSize=26  frame=35

 0  1           5  6  7     9           13    15                    35
 +--+-----------+--+--+-----+-----------+-----+---------------------+
 |ch|payloadSize|0 |0 | n=1 | contentLen|pkgId| RelPos body 20 B    |
 |0 |    26     |  |  |     |    22     | ID  |                     |
 +--+-----------+--+--+-----+-----------+-----+---------------------+
  1      4       1  1   2        4        2            20
```

```mermaid
block-beta
  columns 12
  ch["ch"]:1
  ps["ps=26"]:2
  z["00"]:1
  n["n=1"]:1
  cl["cl=22"]:2
  id["ID"]:1
  body["RelPos body 20 B"]:4
  style ch fill:#8e44ad,color:#fff
  style ps fill:#2980b9,color:#fff
  style cl fill:#d35400,color:#fff
  style id fill:#c0392b,color:#fff
  style body fill:#27ae60,color:#fff
```

---

## 14. Server package selection (policy, not bytes)

Outbound choice thresholds (for implementers), as a **horizontal decision strip** of outcomes:

```text
 delta large ──► Teleport ──► PosAndRot ──► RelPos ──► Velocity ──► Flags ──► (none)
   |≥256 axis|    |≥128/age|    |small|      |motion|    |dirty|
```

Details: [network.md](network.md) §2.

---

## 15. Adding a package

1. Measure write order and sizes.  
2. Draw **one L→R strip** with offsets on top and sizes under the bar.  
3. Optional: matching flat `block-beta` (`columns = body_len`).  
4. Note `contentLen = 2 + body_len`.  
5. Link from [protocol.md](protocol.md).

---

## Related

| Doc | Role |
|---|---|
| [protocol.md](protocol.md) | Join SM, narrative |
| [network.md](network.md) | Interest / scaling |
| [inventories/netpackages.md](inventories/netpackages.md) | Type census |
| loadgen PackageCodec | Golden builders |

## Changelog

- **2026-07-20:** Rewrite as left-to-right protocol strips (RFC bars + flat Mermaid); drop nested box diagrams.
- **2026-07-20:** Initial visual catalog.
