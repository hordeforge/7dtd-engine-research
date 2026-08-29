# Runtime hot-patch of the YDim expand (feasibility)

**Owns:** whether the `ChunkBlockYDim` 256→32768 expand can be applied at
runtime (mod DLL + Harmony transpiler / MonoMod) instead of the shipped
`EngineHeightPatcher.exe` disk tool. Product side:
[`7dtd-realearth/docs/HEIGHT_LIMITS.md`](../../7dtd-realearth/docs/HEIGHT_LIMITS.md).
Hub: [INDEX.md](INDEX.md).

## 1. Why the disk patcher exists

`WorldConstants.ChunkBlockYDim` is a **`const`** (field `HasConstant`), not a
mutable static. There is no field storage to `SetValue`; the value 256 is
baked as `ldc.i4` literals into the IL of every consumer. The patcher rewrites
those literals in two passes:

- constant table rewrites (9 sites: `ChunkBlockYDim`, `ChunkBlockYPow`,
  `ChunkBlockYDimM1`, `ChunkBlockLayers`, density dims/masks, `cMaxHeight`)
- IL `Ldc` rewrites (76 sites) across a fixed list of methods

`Field.SetValue` cannot change a `const`; only IL rewriting can. Hence
"expand = disk patch" in the product docs.

## 2. The hot-patch hypothesis

> If a transpiler patch is installed while the game is still in the main menu
> (no world loaded), none of the 76 sites have JIT'd yet, so Harmony
> transpilers (which rewrite the body at JIT time) would catch all of them.

### 2.1 What the game ships

`Mods/0_TFP_Harmony/` carries the full runtime-rewrite stack: `0Harmony.dll`,
`MonoMod.Core.dll`, `MonoMod.RuntimeDetour.dll`, `MonoMod.Utils.dll`,
`Mono.Cecil*.dll`. The engine itself uses MonoMod dynamic methods at runtime
(`GameManager:DMD<...>` wrappers in logs), so a runtime rewriter is not foreign
to this process.

### 2.2 JIT timing evidence (V3.2.0 IL dump)

- **Main menu is clean:** `MainMenuMono*` (all 6 variants) reference **zero**
  of `Chunk`, `WorldConstants`, `GenerateTerrain`, `GetTerrainHeight*`. None of
  the 26 Y-bound method names or 6 layer-storage types JIT at menu time.
- **World/chunk types construct at world load:** `World..ctor` (IL=122),
  `World::Init` (IL=41), and `ChunkProviderGenerateWorld.Init` are the first
  construction points; chunk methods are called from there.
- **Const-inlining consumers beyond the patch set** (`VoxelMesh`,
  `BlockShapeNew/Cube`, `XUiC_MaterialStack/InfoWindow`, `WorldState`) reference
  WorldConstants, but for *other* consts (dims used in UI math, `cTimePerHour`)
  - not the Y-bound sites. They are irrelevant to a Y-only transpiler unless
  they also inline a Y literal (they do not: the patcher's 26-name list is
  authoritative for Y bounds).

### 2.3 Residual risks (why disk patch stays the product default)

1. **Other mods / load order.** A Harmony transpiler only rewrites methods that
   have not yet JIT'd when the patch is applied. If any other loaded mod (or the
   game's own boot path) touches one of the 26 methods before our patch installs,
   that method JITs with 256 baked in → half-patched engine (silent corruption,
   not a clean crash). Mod load order is not guaranteed.
2. **Patch surface parity.** The transpiler must rewrite exactly the same sites
   as the patcher (9 constant-table + 76 IL). Any miss = inconsistent columns.
   The disk patcher has a `--verify` sha256 marker; a transpiler has no
   equivalent post-hoc verification that every site was caught.
3. **Rollback.** Disk patch: `make engine-restore` + Steam-Verify recovery. Hot
   patch: no clean undo once a method has run.
4. **Layer-storage allocation.** `ChunkBlockLayer`/`UnsafeChunkData` allocate
   `[YDim/LayerHeight]` arrays at construction; the transpiler must hit the
   constructors *before the first chunk allocates*. This is the same JIT-race as
   (1), just earlier.

## 3. Verdict

The menu-time hypothesis is **supported by the IL evidence**: with a transpiler
installed from `IModApi.InitMod` (pre-world), the 26 Y-bound methods and 6
storage types should all still be un-JIT'd, so a full hot patch is plausible on
a single-mod, known-load-order install. It is not safe as the general product
path because load order and other mods can JIT a site early, and there is no
verification/rollback story. The disk patcher remains the product default; the
hot patch is a viable experiment/fallback for controlled environments.

## 4. Implementation sketch (if pursued)

```csharp
// Harmony transpiler per target method, e.g.:
[HarmonyPatch(typeof(Chunk), "SetDensity")]
static IEnumerable<CodeInstruction> Transpile(IEnumerable<CodeInstruction> il)
{
    foreach (var i in il)
    {
        if (i.opcode == OpCodes.Ldc_I4 && (int)i.operand == 256) i.operand = 32768;
        else if (i.opcode == OpCodes.Ldc_I4_S && (sbyte)i.operand == 255) i.operand = 32767;
        yield return i;
    }
}
// + 25 more method patches, 6 storage-type ctor patches, and the constant table
// sites. A shared helper maps YDim -> YPow/masks/layers/volume-bits exactly like
// EngineHeightPatcher.SetYDim (single source of truth).
```

Verification hook: after the first chunk constructs, compare
`WorldConstantsProbe.ChunkBlockYDim` (reads the const → still reports 256, but
`Chunk` density array lengths / `GetDensity` behavior are the real check) or
inject a probe that inspects an allocated chunk's layer count. Failing that,
treat the hot patch as experimental and keep `engine-verify` on the disk
patcher.

## 5. Related

- [terrain-height.md](terrain-height.md) - stock vs expanded constants, measured
- [mod-loading.md](mod-loading.md) - `IModApi.InitMod` runs pre-world
- [chunk-providers.md](chunk-providers.md) - chunk construction/lifetime
- `7dtd-realearth/tools/engine_patcher/Program.cs` - authoritative Y-bound lists
