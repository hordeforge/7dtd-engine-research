# How to reverse-engineer the 7DTD dedicated server

**Owns:** the RE method itself: toolchain, dumping, and how to read managed IL
back into wire layouts / system behaviour. This is the "how", the family docs
are the "what".
**Tooling:** [`../tools/`](../tools) (tracked). Raw output: `il/` (git-ignored).
**Hub:** [`INDEX.md`](INDEX.md).

The target is the shipped managed assembly `Assembly-CSharp.dll` (Unity 2022
Mono, ~4400 top-level types). We do not decompile to C#; we dump **CIL** with
Mono.Cecil and read it directly. IL is unambiguous about wire byte order, field
types, and control flow, which is exactly what protocol and cost RE needs.

---

## 0. Toolchain

| Need | Tool | Note |
|---|---|---|
| Read assembly metadata + IL | **Mono.Cecil** | `AssemblyDefinition.ReadAssembly` |
| Compile the dumpers | `mcs` (Mono C#) | old `mcs`: no local functions, use static helpers |
| Run the dumpers | `mono` | `MONO_PATH=bin mono bin/Tool.exe` |
| Whole-file disassembly (spot checks) | `monodis`, `ikdasm` | cross-check a single method |

Full tool catalog (general `src/`, per-family `legacy/`, `parity/`, `re-scratch/`,
`tests/`): [`../tools/README.md`](../tools/README.md).

Nothing in this repo ships game bytes. Point `ASM` at your own install:

```bash
ASM="$HOME/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll"
cd tools && ./build.sh
```

If you target the **live** managed DLL, stop the server first.

---

## 1. Orient: census before depth

Start from ground-truth counts so later claims are checkable and patch drift is
visible:

```bash
mono bin/Census.exe "$ASM"
```

**Live pin (V3.1.0 b14)** from `tools/data/stock_facts.json` / `Census.exe`
(regenerate after any game update with `make stock-sync`):

| Metric | V3.1.0 live | V3.0.1 baseline (historical) |
|---|---:|---:|
| Top-level types | **4414** | 4401 |
| Methods with body (top-level) | **44107** | 43901 |
| All types (incl nested) | **7432** | 7413 |
| `NetPackage*` types (excl `NetPackageManager`) | **193** | 193 |
| `GameManager.gmUpdate` IL | **631** | 631 |
| `WorldState.SaveLoad(Stream)` IL | **926** | 884 |
| Sim rate (`GameTimer`) | **20 Hz** | 20 Hz |
| `CurrentSaveVersion` | **23** | (see save-region) |

A changed count is the first signal that a doc, not the game, is now wrong.
Do not quote the historical V3.0.1 column as "live dedi" after the 3.1 retarget.

---

## 2. Dump a method

Substring filters over type and method name (nested types included):

```bash
mono bin/DumpMethod.exe "$ASM" GameManager gmUpdate
mono bin/DumpMethod.exe "$ASM" NetPackageChunk write out.txt
```

Output line format (the whole corpus uses it):

```text
IL_0009: ldfld Boolean NetPackageChunk::bOverwriteExisting
IL_000E: callvirt System.Void System.IO.BinaryWriter::Write(System.Boolean)
```

`IL_XXXX` is the byte offset (also used as the branch-target label), then the
opcode, then a fully-qualified operand.

---

## 3. Read IL: the patterns you actually need

You do not need every opcode. Ninety percent of RE here is recognizing a few
shapes.

**Stack discipline.** CIL is a stack machine. `ldarg.0` = `this`; `ldarg.1` =
first real arg. A field store reads as: push target, push value, `stfld`.

| IL shape | Means |
|---|---|
| `ldarg.0; ldarg.1; callvirt ...ReadInt32(); stfld X` | read a field X off the wire |
| `ldarg.1; ldarg.0; ldfld X; callvirt ...Write(Int32)` | write field X to the wire |
| `conv.i2` / `conv.u1` before a `Write` | field is stored wider than it is sent (e.g. `int` sent as `i16`) |
| `brfalse`/`brtrue` on a bool field | an **optional / conditional** wire section follows |
| `callvirt ...Read(byte[],0,len)` after a length `ReadInt32` | length-prefixed byte array |
| `call Foo::Write(BinaryWriter)` | a nested struct; dump `Foo` next |

**Trivial getters** are `ldc.i4.N; ret`. That is how per-package channel,
compression, direction, and delivery constants are read (see §5).

---

## 4. Reconstruct a wire layout (the core loop)

For any serialized type, the **`write` method is authoritative for byte order**;
`read` must mirror it and confirms field widths. Procedure:

1. Dump the type's `read` + `write` (`DumpType.exe` for non-packages,
   `DumpNetPackages.exe` for packages).
2. Walk `write` top to bottom. Each `BinaryWriter::Write(T)` emits one field of
   width `T`, in order. Note `conv.*` casts (stored width != wire width).
3. Every `brfalse/brtrue` on a bool marks a conditional block; record the guard.
4. Every `call SomeType::Write` is a nested struct; recurse into it.
5. Cross-check against `read`: same order, same widths, opposite direction.
6. Write the layout as an offset table. Fixed-size prefixes get exact offsets;
   variable parts (strings, arrays, nested structs) get "then" ordering.

.NET conventions that fix the ambiguous cases: little-endian; `Write(string)` is
a 7-bit length prefix then UTF-8; `bool` is one byte; arrays are usually an
explicit `Int32` count (or length) then elements.

Worked example (`NetPackageChunk`): `write` emits `bOverwriteExisting:bool`,
then `if(bOverwriteExisting){ chunkX,chunkY,chunkZ : i16 (conv.i2 from Chunk.X/Y/Z) }`,
then `dataLen:i32`, then the serialized chunk blob. That is the entire terrain
push body, read straight from the two methods. See
[`protocol.md`](protocol.md) for the annotated packages.

**Automated first pass (`tools/src/WireBodies`).** Doing step 2 by hand for all 183
packages is slow, so `WireBodies` walks every `NetPackage*` `write()` (and the
nested serializers they delegate to) and emits the ordered field/type sequence to
[`inventories/netpackage-bodies.md`](inventories/netpackage-bodies.md). It captures
the flat backbone (each `Write(T)` and nested `.Write`), tags list-count rows, and
flags loop/conditional bodies. It does **not** resolve exactly which optional flag
gates which section, so treat its output as the scaffold and confirm a load-bearing
body against `write`/`read` IL before cloning. Regenerate:
`mono bin/WireBodies.exe "$ASM" ../docs/inventories/netpackage-bodies.md`.

---

## 5. Protocol-wide sweeps

Per-package behaviour lives in trivial overrides. Rather than open 193 files,
census the constants:

```bash
mono bin/NetProtocolCensus.exe "$ASM" ../il/netpackages-v3.1.0/META.md
```

This resolves each `get_Channel` / `get_Compress` / `get_PackageDirection` /
`get_ReliableDelivery` / `get_AllowedBeforeAuth` to its constant. `inherit`
means the package uses the base default; `expr` means the getter is computed at
runtime (open it by hand). This is how the channel bands, the compressed-package
set, and the pre-auth surface were found. Enum values (e.g.
`NetPackageDirection` 0=Both/1=ToServer/2=ToClient) come from
`DumpMethod`-adjacent enum reads or a two-line Cecil field-constant dump.

---

## 5b. Cross-version parity (patch drift)

The dumpers above annotate one build. To see what a game update changed, snapshot
the whole wire surface to JSON and diff:

```bash
tools/parity/fetch_version.sh public v3.0.1     # steamcmd pull + ParitySurface snapshot
tools/parity/fetch_version.sh latest_experimental exp
tools/parity/parity_diff.py parity_v3.0.1.json parity_exp.json   # added/removed/changed packages
```

`ParitySurface.cs` records each package's read/write `BinaryReader`/`BinaryWriter`
call sequence, so a changed wire layout shows up as a changed call string even
when the field names are stable. This is the fastest drift check: re-snapshot
after every update, diff against the pinned baseline, and only re-annotate the
packages the diff flags. Coverage mode (`--coverage new.json GAMEDIR`) reports
what a clone handles vs stock.

The package parity diff only covers `NetPackage` wire and enums. For a **full**
cross-version diff also run a per-method **signature** diff (emit
`Type::Method(params)` for every method-with-body in each build and `comm` them:
catches new/removed methods on existing types) and an **enum-member** diff (emit
`Enum.Member=value` and `comm`: catches inserted/renumbered enum values). The
held-entity feature ([items.md](items.md) § Held entities) and join analytics
([server-lifecycle.md](server-lifecycle.md) `PlayerJoinServerEventData`) in the V3.1.0
shipped surface were only visible through those two lenses, not the package parity alone.
Full delta map: [INDEX.md](INDEX.md) § V3.1.0 shipped delta map.

## 5c. Stock facts pin (hardcodes across docs + products)

Hardcoded stock values (version triple, TPS, challenge `0xCA`, chunk YDim,
`CurrentSaveVersion`, NetPackage count, …) must not drift independently in
research narratives, loadgen, and zdtd. Single regenerable table:

```bash
cd tools
./build.sh --skip-legacy
./stock-sync.sh                 # StockFacts.exe → data/stock_facts.json + pin check
./stock-sync.sh --check-only    # CI / pre-commit without touching the DLL
```

| Piece | Role |
|---|---|
| `tools/src/StockFacts.cs` | Cecil extract from live `Assembly-CSharp.dll` |
| `tools/data/stock_facts.json` | **Committed** facts table (schema 1) |
| `tools/tests/check_stock_facts.py` | Greps research docs + sibling pins against JSON |
| `tools/stock-sync.sh` | extract + check wrapper |

After a game update: prefer `tools/post-update.sh` (or `make post-update`), which
runs `stock-sync.sh` then §5b `drift-check.sh`. Fix any FAIL pin sites, commit the
new JSON together with doc/code pin edits. Pair with §5b `drift-check.sh` for full
surface drift; stock-sync is the **small constant** gate, not a replacement for
parity dumps.

Product rules (still enforced in those repos):

- loadgen: `PackageCodec.GameVersion` + golden-wire fixtures
- zdtd: `version.zig stock_wire`, `protocol.zig` challenge/ticks, AssignIds embed tests
- never bare NetPackage **numeric** ids on production send paths (`lint-wire.sh`)

## 6. Cost / loop RE (non-protocol systems)

Same tools, different questions. For hot-path anatomy:

- Dump the driver (`gmUpdate`, `*Manager.Update`, `TickEntity`) and follow the
  `call`/`callvirt` fan-out. IL instruction count is a rough complexity proxy,
  not a cost measurement.
- Distinguish **structure** (what the IL proves: call graph, branch conditions,
  data structures, allocation sites) from **cost** (what only a profiler
  proves). Never state a percentage or big-O as "measured" from IL alone; that
  belongs to APM/profiler artifacts. See
  [`measured-scaling.md`](../../7dtd-optimizer/docs/measured-scaling.md) and [`bottlenecks.md`](../../7dtd-optimizer/docs/bottlenecks.md).
- Allocation RE: look for `newobj`, `newarr`, boxing, and LINQ closures in hot
  methods ([allocation-reuse.md](../../7dtd-optimizer/docs/allocation-reuse.md)).

---

## 7. What IL cannot answer

Some things are genuinely not in the managed method bodies. Keep these in
[`residuals.md`](residuals.md), not faked from IL:

- Unity script execution order and which GameObjects stay enabled (project /
  prefab settings, runtime observation).
- Native plugins: LiteNetLib transport internals, the Boehm GC, Aron Granberg
  A\* internals, EAC/EOS wire.
- Content semantics (XML blocks/items/biomes): data, not loop IL.

---

## 8. Discipline

- **`write` is truth for byte order; `read` confirms widths.** If they disagree,
  you misread one; re-dump.
- **Trace every claim to an instruction.** A field in a doc must map to a
  specific `ldfld`/`Write` pair.
- **Regenerate, do not hand-edit dumps.** Patch drift is real; re-run the tool.
- **Census first, after every game update**, and diff against the table in §1.
- **Run the regression tests** after a game update or a tooling change:
  `tools/tests/test_dedi_coverage_docs.py` (docs + dump sets + dumpers exist,
  IL-backed) and `tools/tests/test_re_dump_regen.py` (a dumper still regenerates
  non-empty output from the live DLL).
- **Prove coverage with reachability**, not just name sweeps: `tools/src/Reach`
  walks the call graph from `GameManager.StartAsServer`/`gmUpdate`/tick drivers
  (devirtualizing `callvirt`), and any reached Assembly-CSharp type no doc references
  is a candidate gap. This found `PlayerStealth` after the name sweeps missed it.
- Dumps stay in `il/` (git-ignored). Tooling and narratives are tracked.

### 8b. Caller sweeps: the two failure modes

"Is this type server-side or client-side?" is usually answered with a caller sweep,
and that answer is only as good as the sweep. Two traps, both of which produced
wrong claims in this corpus before being caught by audit:

1. **Method-call sweeps miss field access.** A type can be load-bearing on the
   server purely through a field that someone reads. `WorldStats` was classified
   "nothing server-side reads them" on a call sweep, but `PrefabData.Init` stores
   `DensityScore = (WorldStats.TotalVertices + 50000) / 100000`, and RWG prefab
   placement reads that field. Use `tools/src/Xref --field` for field access.
2. **Hits inside closures belong to the outer method.** Lambdas and iterators
   compile into `<>c__DisplayClass*` / `<...>d__*` types, so a naive sweep credits
   the closure, not the real owner, and the site looks like nothing. `Xref` walks
   out to the outermost declaring type and prints it.

A third, tool-specific trap: the retired `FindCallers.exe` **ignored its method
argument entirely** and substring-matched only the type name against callee
signatures, so it also reported calls where the type merely appeared as a parameter
or return type. Any classification made with it is weak evidence; re-check with
`tools/src/Xref`, which matches the member exactly:

```bash
mono bin/Xref.exe "$ASM" EntityBuffs AddBuffNetwork          # exact call sites
mono bin/Xref.exe "$ASM" PrefabData DensityScore --field     # field reads/writes
```

Rule of thumb: **a negative result ("no server callers") is a much stronger claim
than a positive one, so it needs the stronger tool.** Before writing "client-only",
run both the call and the field form.

**Do not classify by name.** An out-of-scope sweep done by type-name heuristic put 48
server types in the wrong bucket, because the name lies often enough to matter:
`ClientAmmoData` is turret state on a server tile entity, `StreamReadSizeMarker` is
wire-framing infrastructure, `ClientLobbyManager` sits in the server authorizer
chain, and `ClientTriggerData` belongs to `TileEntityPoweredTrigger`. The reliable
signal is **who references it**: `tools/src/RefScan` takes a list of type names and
reports every referencing site attributed to its outermost owner, in one assembly
pass. A type whose referrers are all `XUiC_*`/render/editor is genuinely client; a
type referenced only from `GameManager`/`World`/`NetPackage*`/`TileEntity*` is not,
whatever it is called.

```bash
mono bin/RefScan.exe "$ASM" types.txt refs.tsv    # batch reverse references
```

---

## Related docs

| Doc | Role |
|---|---|
| [`../tools/README.md`](../tools/README.md) | Tool reference + build |
| [`protocol.md`](protocol.md) | Wire framing + annotated package bodies |
| [`protocol-frames.md`](protocol-frames.md) | Visual byte frames |
| [`coverage.md`](coverage.md) | Family -> narrative -> dump map |
| [`residuals.md`](residuals.md) | What IL cannot close |
| [`INDEX.md`](INDEX.md) | Hub |
