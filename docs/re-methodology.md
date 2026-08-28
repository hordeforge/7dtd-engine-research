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

**Live pin (V3.2.0 b9)** from `tools/data/stock_facts.json` / `Census.exe`
(regenerate after any game update with `make stock-sync`):

| Metric | V3.2.0 live | V3.1.0 (historical) | V3.0.1 baseline (historical) |
|---|---:|---:|---:|
| Top-level types | **4426** | 4414 | 4401 |
| Methods with body (top-level) | **44277** | 44107 | 43901 |
| All types (incl nested) | **7451** | 7432 | 7413 |
| `NetPackage*` types (excl `NetPackageManager`) | **195** | 193 | 193 |
| `GameManager.gmUpdate` IL | **631** | 631 | 631 |
| `WorldState.SaveLoad(Stream)` IL | **926** | 926 | 884 |
| Sim rate (`GameTimer`) | **20 Hz** | 20 Hz | 20 Hz |
| `CurrentSaveVersion` | **23** | 23 | (see save-region) |

A changed count is the first signal that a doc, not the game, is now wrong.
Do not quote the historical V3.1.0/V3.0.1 columns as "live dedi" after the 3.2 retarget.

### Mention depth: how thin is one "narrated" credit

A narrated tier built from name mentions has a known weakness: a type named
once in passing scores identically to one with a dedicated section. Measure
that depth instead of asserting it:

```bash
python3 tools/mention_depth.py
```

Live distribution over the narrative docs (DLL-free; distinct type-shaped
backtick-quoted identifiers):

| Mentions | Names | Share |
|---|---:|---:|
| exactly 1 | 6316 | 66% |
| 2-4 | 2395 | 25% |
| 5-19 | 709 | 7% |
| 20+ | 87 | 1% |

Two thirds of mentioned names appear exactly once: cross-reference density,
not explanation depth. Treat any narrated/catalogued percentage as an upper
bound and read [`inventories/coverage-report.md`](inventories/coverage-report.md)
(the generated four-tier view) for the reached-type split; `Coverage.exe`
emits the same histogram restricted to reached game types into that report.

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
mono bin/NetProtocolCensus.exe "$ASM" ../il/netpackages-v3.2.0/META.md
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
packages the diff flags. Clone implementation coverage belongs in the clone
repository, not this stock RE tool.

The package parity diff only covers `NetPackage` wire and enums. For a **full**
cross-version diff also run a per-method **signature** diff (emit
`Type::Method(params)` for every method-with-body in each build and `comm` them:
catches new/removed methods on existing types) and an **enum-member** diff (emit
`Enum.Member=value` and `comm`: catches inserted/renumbered enum values). The
held-entity feature ([items.md](items.md) § Held entities) and join analytics
([server-lifecycle.md](server-lifecycle.md) `PlayerJoinServerEventData`) in the V3.2.0
shipped surface were only visible through those two lenses, not the package parity alone.
Full delta map: [INDEX.md](INDEX.md) § V3.2.0 shipped delta map.

## 5c. Stock facts pin (hardcodes across docs + products)

Hardcoded stock values (version triple, TPS, challenge `0xCA`, chunk YDim,
`CurrentSaveVersion`, NetPackage count, behaviour pins: WaterLevel 62.88,
item-drop lifetime 300 s, per-frame load budget 50 ms, …) must not drift
independently in research narratives, loadgen, and zdtd. Single regenerable
table:

```bash
cd tools
./build.sh --skip-legacy
./stock-sync.sh                 # StockFacts.exe → data/stock_facts.json + pin check
./stock-sync.sh --check-only    # pin check without regenerating; still diffs
                                # facts vs the live DLL when it is installed
```

| Piece | Role |
|---|---|
| `tools/src/StockFacts.cs` | Cecil extract from live `Assembly-CSharp.dll` **and the sibling `LiteNetLib.dll`** (protocol/MTU/header pins) |
| `tools/data/stock_facts.json` | **Committed** facts table (schema 1) |
| `tools/tests/check_stock_facts.py` | Greps research docs + sibling pins against JSON (incl. zdtd's provenance register carrying the pinned WaterLevel); with `--require-live` also re-extracts via `bin/StockFacts.exe` and diffs every field against the local DLL, so build drift fails with a named field list (skipped on machines without the game) |
| `tools/stock-sync.sh` | extract + check wrapper |
| `tools/facts.py` / `make facts` | Quick view of the machine-checked pins |
| `tools/xml_pins.py` | Machine-checked XML data pins (entityclasses HP ladder, traders.xml economy, buffs survival thresholds) from `Data/Config`; regenerated by `stock-sync`, asserted by `check_stock_facts` |

After a game update: prefer `tools/post-update.sh` (or `make post-update`), which
runs `stock-sync.sh` then §5b `drift-check.sh`. Fix any FAIL pin sites, commit the
new JSON together with doc/code pin edits. Pair with §5b `drift-check.sh` for full
surface drift; stock-sync is the **small constant** gate, not a replacement for
parity dumps.

## 5d. Corpus self-verification (the gates that keep the docs honest)

Beyond the pins, the corpus is machine-checked against the live DLL so a game
patch or a careless edit cannot silently drift the docs:

| Gate | What it verifies |
|---|---|
| `make test` (25 checks) | the full local suite: reach/coverage consistency, committed-inventory currency (`WireBodies`/`Coverage`/`StateMachines` regeneration), surface well-formedness, doc-link + section-ref integrity, inventory count claims, and the DLL-side guards below |
| `tests/test_subclass_counts.py` | per-leaf inventory counts (sequence-requirements 38, item-actions 38, quest-objectives 38, minevent-actions 71, block-behaviors 65, te-features 11, challenge-objectives 28+1, sequence-actions 123) match the concrete-subclass closures / namespace composition |
| `tests/test_console_cmd_inventory.py` | console catalog primary rows == `CmdMap.exe` output, alias rows are real names, the committed `.tsv` is current, and every Does-column description equals `getDescription` |
| `tests/test_console_classification.py` | the console client-executable / dedicated-gate split (188 leaves; 83 `get_IsExecuteOnClient`, 84 either, 10 `IsDedicatedServer`-gated classes listed in console-commands.md 6) matches a Cecil prologue probe over the `CmdMap` population |
| `tests/test_il_citations.py` | **every** parseable `Type::Method` + `IL=N` claim in the docs (2367 claims, incl. dated "(exact)" re-verification notes) matches some overload of the method in the live DLL; approximate IL claims (a tilde form) are banned |
| `tests/test_xref_claims.py` | every `Xref=N` call-site claim in the docs (5, tight ``Type.Method (Xref=N)`` form, backtick-gapped) matches `Xref.exe` against the live DLL |
| `tests/test_inventory_type_existence.py` | every type row in `dedicated-leaves.md` (371) and `netpackages.md` (194, incl. base/method-count/max-IL columns and top-level completeness) resolves in the DLL |
| `tests/test_entityclass_props_current.py`, `test_gamestats_gameprefs_current.py` | EntityClass `.cctor` prop pairs (167) and the EnumGameStats/EnumGamePrefs member-name tables (82/317) equal the DLL |
| `tests/test_tuned_constants.py` | **524 tuned game constants** (AI director horde/placement/cooldown + airdrop schedule, water sim, block masks + `BlockValue` bit layouts, entity/walk-type ids, spawn rings, stealth/smell, vehicle/drone/turret, region/chunk/world, RWG, threat levels) pinned against the DLL and stated in the owning doc; a **completeness scan** fails on any const-rich class (>= 4 numeric consts) that is neither pinned nor allowlisted |
| dump-mirror guards in `test_dedi_coverage_docs.py` | `deeper.md`/`gaps.md`/`opt-scan.md`/`loop-complete.md` bodies equal their regenerated dump masters (gaps with the >4-line raw-IL elision policy); every `il/` reference resolves; `tools/bin` exes are not older than `tools/src` |
| `test_re_dump_regen.py` | `frame-entries`/`gmupdate-calls`/`manager-updates` committed bodies equal the regenerated dumper output |

This loop's findings: 6 stale V3.0.1-era inventories regenerated (deeper, gaps,
opt-scan, loop-complete, frame-entries, manager-updates), 5 stale doc claims
fixed (SaveLoad 884→926, GetCellsOnRay 244→242, PersistentPlayerLogin 5→37,
3 netpackages max-IL values, residuals §8→§4), 4 unresolvable base markers
resolved, and the wire docs **live-verified**: a real join against a stock
V3.2.0 dedicated server produced the exact documented PackageIds framing
(`[ch][size][comp][enc][cnt]`, VersionInformation 1/3/10/14, map count 0xBD=189)
and pre-auth stage strings (`authstate_nativeplatform` / `authstate_encryption`
/ `authstate_authenticated`).

Product rules (still enforced in those repos):

- loadgen: `PackageCodec.GameVersion` + golden-wire fixtures
- zdtd: `version.zig stock_wire`, `protocol.zig` challenge/ticks, AssignIds embed tests
- never bare NetPackage **numeric** ids on production send paths (`lint-wire.sh`)

## 5e. Live event verification (scheduled stock behavior)

IL pins a schedule; a live run proves it. The stock dedicated server can be
driven deterministically for scheduled events (proven 2026-08-11 for the air
drop, the wandering horde, and the blood-moon start; evidence notes in
`workspace/notes/`):

- **Boot** the stock server via the 7dtd-loadgen wrapper
  (`scripts/start_dedicated_navezgane.sh`); telnet on 8081 (password `retest`).
- **World time** pauses with zero connected players - join a loadgen bot
  (`LOADGEN_MODE=join LOADGEN_COUNT=1`) to advance the sim, and note the bot
  may drown at Navezgane spawn (a fresh join + immediate settime catches it
  alive). `settime` takes 1 arg (`day`/`night`/raw u64) or 3 (day hour
  minute); other counts rejected. Rate ~400 world units/s (DayNightLength 60).
- **Observe** the game log (the wrapper's logfile path): scheduled events log
  at INFO/WRN (e.g. `Next Airdrop:`, `BloodMoon starting for day N`,
  `AIDirector: Wandering StartSpawning Horde`). Read runtime state directly
  via `gettime` and `getgamestat <name>` (e.g. `getgamestat AirDropFrequency`
  -> 3 on a 0-config server - the sandbox option default, not the pref).
- **The live run is the arbiter of IL readings**: it caught the option-driven
  nature of the airdrop schedule (`SetupAirDropTimeRanges` overrides the cctor
  day-counts; the observed 3-day gap vs the cctor-derived 2-day gap) and the
  alive-player requirement (a dead bot holds the drop).

## 6. Cost / loop RE (non-protocol systems)

Same tools, different questions. For hot-path anatomy:

- Dump the driver (`gmUpdate`, `*Manager.Update`, `TickEntity`) and follow the
  `call`/`callvirt` fan-out. IL instruction count is a rough complexity proxy,
  not a cost measurement.
- Distinguish **structure** (what the IL proves: call graph, branch conditions,
  data structures, allocation sites) from **cost** (what only a profiler
  proves). Never state a percentage or big-O as "measured" from IL alone; that
  belongs to APM/profiler artifacts. See
  [`measured-scaling.md`](../../7dtd-server-optimizer/docs/measured-scaling.md) and [`bottlenecks.md`](../../7dtd-server-optimizer/docs/bottlenecks.md).
- Allocation RE: look for `newobj`, `newarr`, boxing, and LINQ closures in hot
  methods ([allocation-reuse.md](../../7dtd-server-optimizer/docs/allocation-reuse.md)).

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

## 7b. Asset file formats: the parser is the specification

Unity asset containers are not in `Assembly-CSharp.dll` at all - they are read
by the native engine - so §4's `ldfld`/`Write` loop has nothing to bite on.
The method that works instead, used to decode
[`shader-subprogram-blob.md`](shader-subprogram-blob.md):

1. **Find the open-source parsers first, and read them as a specification.**
   Every reader of a format is a spec someone already paid for. Prefer two
   independent ones: agreement is corroboration, and disagreement tells you
   exactly which field is version-dependent. For Unity that means
   [UnityPy](https://github.com/K0lb3/UnityPy),
   [AssetStudio](https://github.com/Perfare/AssetStudio),
   [AssetRipper](https://github.com/AssetRipper/AssetRipper) and
   [USCSandbox](https://github.com/nesrak1/USCSandbox). Search the **format**
   and the **artifact** by name, not your framing of the problem.
2. **Notice what the parsers skip.** A parser that seeks past a region has not
   decoded it, it has stepped over it. Those regions are where the open
   questions live, and no amount of re-reading the parser will answer them.
3. **Decode a skipped region by correlating it against something already
   understood.** Dump the region across the whole corpus and test candidate
   meanings against a quantity you can compute independently - here, the
   declaration opcodes in the shader bytecode the header describes.
4. **Prove the assignment is discriminated, not coincidental.** Report how
   often the *wrong* pairings match too. A field that matches 100% while its
   neighbours match 5% is decoded; three fields that all match is a tautology
   if they are all the same number.
5. **Widen the sample before believing it.** One bundle is not the format. The
   shader header looked like six constant bytes across two sub-programs and
   resolved into four distinct fields only at 7366.
6. **Chase every exception individually.** The four sub-programs that broke
   the rule each *confirmed* a field once inspected. An exception waved off as
   noise is a field you have not found yet.
7. **Track the tool, not the dump** (rule 2): a reproduction script in
   `tools/` that re-derives and re-checks the claim, so the next game version
   re-verifies it in one command.

Status such work earns: `verified` for a field measured over the corpus with
the wrong pairings excluded, `inferred` for one that only bounds another
quantity, and an explicit **not decoded** for regions that stay opaque. Do not
launder the third into the first.

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
| [`shader-subprogram-blob.md`](shader-subprogram-blob.md) | Shader (class 48) compiled-code container |
| [`texture-atlas-unityfs.md`](texture-atlas-unityfs.md) | UnityFS container + SerializedFile tables |
| [`INDEX.md`](INDEX.md) | Hub |
