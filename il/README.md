# Raw dedicated-server IL dumps

Regenerable Mono.Cecil output from this repo's `tools/src/` + `tools/legacy/` dumpers (see [`../tools/README.md`](../tools/README.md)) against the local dedicated `Assembly-CSharp.dll`.

**Do not start here.** Human docs: [`../docs/INDEX.md`](../docs/INDEX.md) → [`../docs/coverage.md`](../docs/coverage.md).

Do not redistribute game assemblies or treat bulk IL as a product artifact.

Dump sets: dedi-complete, deep, deeper, gaps, frame-entries, gmUpdate,
loop-complete, opt-scan, terrain-*, realearth-surfaces, plus the src/-generated
netpackages / surface / full sets. Full table: docs INDEX.

## Version policy: latest release only

These dumps track the **latest stock release**, currently **V3.1.0 b14**. When
the game updates, regenerate every set against the new dedicated
`Assembly-CSharp.dll` and delete the previous version's sets in the same change,
so there is only ever one corpus and a citation cannot silently refer to an old
one.

The V3.0.1 sets were removed on 2026-08-06 after the V3.1.0 sets were generated
and verified. They are not recoverable from this machine (the 3.0.1 assembly is
no longer installed), which is the reason to regenerate before deleting, never
after.

Regenerate with the dedicated assembly path in `$ASM`:

```sh
ASM=".../7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll"
mono tools/bin/DumpNetPackages.exe "$ASM" il/netpackages-v3.1.0
mono tools/bin/DumpType.exe "$ASM" il/netpackages-v3.1.0 \
     EntityCreationData ItemValue ItemStack BlockChangeInfo
mono tools/bin/FullSurface.exe "$ASM" il/surface-v3.1.0
mono tools/bin/DumpAll.exe     "$ASM" il/full-v3.1.0
for t in DumpDediComplete DumpDeep DumpDeeper DumpGaps DumpFrameEntries \
         DumpLoopComplete DumpOptScan DumpTerrain DumpRealEarthSurfaces; do
  mono "tools/bin/legacy/$t.exe" "$ASM" "il/<set>-v3.1.0"
done
```

`DumpNetPackages` emits only `NetPackage*` types, so the four companion types
above have to be dumped explicitly or citations to `EntityCreationData` break.

**Sanity check after a regeneration:** `EntityCreationData_il.txt` must contain
`stressAmount`. That field is the V3.1.0 addition which takes the written field
count from 35 to 36; if it is absent, the dump came from an older assembly.

## Single-file working dump

Some citations use the form `asm.il:NNNN`, which is a single-file dump of the
same assembly kept outside the repo:

```
/home/maci/.cache/zdtd-scratch/asm.il
```

| Field | Value |
|---|---|
| Bytes | 134838448 |
| Lines | 2818835 |
| MD5 | 2e95dd525785cd95d0c2a4fcee7445fb |
| Source | dedicated `Assembly-CSharp.dll`, V3.1.0 b14 |

Line numbers are valid only against that exact file. When a citation does not
resolve, check the MD5 before concluding the claim is wrong. Citations written
before 2026-08-06 may still carry V3.0.1 line numbers, which drift from this
dump by roughly 3500 lines in the NetPackage region.
