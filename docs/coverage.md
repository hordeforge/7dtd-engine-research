# Dedicated-server engine coverage map (V3.0.1)

**Owns:** family → narrative → dump checklist.  
**Hub:** [`INDEX.md`](INDEX.md).  
**Residuals:** [`residuals.md`](residuals.md).

**Bar:** 100% of dedicated-relevant **managed** surfaces in `Assembly-CSharp.dll`.  
**Not in bar:** Unity native, native net plugins, EAC wire protocol, client-only UI.

**Live pin (2026-07-18 dedi):** stock `ChunkBlockYDim=256`, `ChunkBlockLayers=64`. Expanded dumps in `terrain-v3.0.1` are historical.  
**Runtime pin:** Unity 2022 Mono (Boehm `libmonobdwgc-2.0.so`, conservative non-generational STW GC), sim target 20 TPS. GC / FPS / lifecycle knobs: [`runtime-tuning.md`](runtime-tuning.md).

```mermaid
flowchart TB
  IDX[INDEX.md hub]
  IDX --> COV[coverage.md this map]
  IDX --> LOOP[loop.md frame/sim]
  IDX --> RES[residuals.md non-IL only]
  COV --> FAM[family narratives]
  FAM --> IL[research/il dump sets]
  LOOP --> FAM
```

---

## Family → narrative → dump

| # | Family | Narrative | Dump evidence | Status |
|---|---|---|---|---|
| 1 | Frame / gmUpdate | [loop.md](loop.md), [loop-gmupdate.md](loop-gmupdate.md) | il/gmUpdate-v3.0.1/, il/frame-entries-v3.0.1/ | Closed |
| 2 | Timers / dual entity tick | loop.md §3, [entity-ai.md](entity-ai.md), [closed-gaps.md](closed-gaps.md) | il/gaps-v3.0.1/, il/deep-v3.0.1/, il/dedi-complete-v3.0.1/ | Closed |
| 3 | World / chunks | [world-chunks.md](world-chunks.md) | il/dedi-complete-v3.0.1/, il/loop-complete-v3.0.1/, il/realearth-surfaces-v3.0.1/ | Closed |
| 4 | Terrain / height | [terrain-height.md](terrain-height.md), [realearth-surfaces.md](../../7days-realworld/docs/realearth-surfaces.md) | il/terrain-*-v3.0.1/, il/realearth-surfaces-v3.0.1/ | Closed |
| 5 | Entities / AI / path | [entity-ai.md](entity-ai.md), [aidirector.md](aidirector.md) | il/deep-v3.0.1/, il/deeper-v3.0.1/, il/gaps-v3.0.1/ | Closed |
| 6 | Networking | [network.md](network.md), [protocol.md](protocol.md), closed-gaps.md | il/gaps-v3.0.1/, il/dedi-complete-v3.0.1/, loadgen golden wire | Closed (framing/join/hot bodies); full 194 bodies open |
| 7 | Save / region | [save-region.md](save-region.md) | il/loop-complete-v3.0.1/, il/realearth-surfaces-v3.0.1/, il/dedi-complete-v3.0.1/ | Closed |
| 8 | Origin / claims | [realearth-surfaces.md](../../7days-realworld/docs/realearth-surfaces.md) | il/realearth-surfaces-v3.0.1/, il/dedi-complete-v3.0.1/ | Closed |
| 9 | Managers | [managers.md](managers.md) | il/dedi-complete-v3.0.1/, il/loop-complete-v3.0.1/ | Closed |
| 10 | Light / mesh / water | [light-mesh-water.md](light-mesh-water.md) | il/dedi-complete-v3.0.1/, il/realearth-surfaces-v3.0.1/ | Closed |
| 11 | ModEvents | [managers.md](managers.md) | il/dedi-complete-v3.0.1/ | Closed (names; subscribers residual) |
| 12 | Runtime APM scale | [measured-scaling.md](measured-scaling.md) | live APM | Closed (measured) |
| 13 | Runtime / GC / FPS knobs | [runtime-tuning.md](runtime-tuning.md) | live symbols / env, IL spot-checks | Closed (measured) |

**RealEarth product** (not generic research ownership): [`../../7days-realworld/docs/INDEX.md`](../../7days-realworld/docs/INDEX.md) (`realearth-runtime`, `realearth-surfaces`, `realearth-review`, MODIFICATIONS).

**Stock limitation maps:** generic dedi ceilings → [engine-limitations.md](engine-limitations.md); RealEarth 1:1 Earth blockers → [`../../7days-realworld/docs/ENGINE_LIMITATIONS.md`](../../7days-realworld/docs/ENGINE_LIMITATIONS.md).

**Custom / Zig dedi clone:** architecture → [zig-clone.md](zig-clone.md); wire → [protocol.md](protocol.md).

---

## Census (live dedi)

| Metric | Value |
|---|---:|
| Top-level types | 4401 |
| Methods with body | 43901 |
| NetPackage* types | ~196 |
| GameTimer Hz | 20 |
| gmUpdate IL | 631 |
| WorldState.SaveLoad(Stream) IL | 884 |

---

## Use / regenerate

1. Find family row above.  
2. Open the **narrative** for measured facts (many include Mermaid **flowcharts** and **state machines**).  
3. Open the cited `research/il/...` path for IL text.  
4. Anything still open → [residuals.md](residuals.md) with a **non-IL reason**.

### Diagram convention

| Kind | Use for |
|---|---|
| `flowchart` | Call graphs, peer Updates, data pipelines |
| `stateDiagram-v2` | Lifecycles: tiles, inject gate, SoloSlide, Origin, AI LOD, path, chunk flags, net packages, save |

Jump list of state machines: [INDEX.md](INDEX.md) (Key state machines).  
Dump tools and commands: [INDEX.md](INDEX.md) Tools section only.  
Product Streamed machines: [`../../7days-realworld/docs/INDEX.md`](../../7days-realworld/docs/INDEX.md) (Key state machines).

## Changelog

- **2026-07-18:** Origin/claims + ModEvents rows link full paths; product hub callout.
## Related docs

| Doc | Role |
|---|---|
| [INDEX.md](INDEX.md) | Hub |
| [residuals.md](residuals.md) | Non-IL residuals |
| [INDEX.md](../../7days-realworld/docs/INDEX.md) | Product RealEarth |

## Changelog

- **2026-07-19:** Related docs table.
