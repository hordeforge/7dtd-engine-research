# Raw dedicated-server IL dumps

Regenerable Mono.Cecil output from this repo's `tools/src/` + `tools/legacy/` dumpers (see [`../tools/README.md`](../tools/README.md)) against the local dedicated `Assembly-CSharp.dll`.

**Do not start here.** Human docs: [`../docs/INDEX.md`](../docs/INDEX.md) → [`../docs/coverage.md`](../docs/coverage.md).

Do not redistribute game assemblies or treat bulk IL as a product artifact.

Dump sets: loop/gmUpdate/deep/deeper/gaps/frame-entries/opt-scan, terrain-*, realearth-surfaces, dedi-complete. Full table: docs INDEX.

## V3.1.0 b14 working dump (not tracked here)

The dump sets in this directory are all **V3.0.1**. Work from 2026-08 onward
cites a **V3.1.0 b14** single-file dump that lives outside the repo:

```
/home/maci/.cache/zdtd-scratch/asm.il
```

Identity of the dump those citations were made against:

| Field | Value |
|---|---|
| Bytes | 134838448 |
| Lines | 2818835 |
| MD5 | 2e95dd525785cd95d0c2a4fcee7445fb |
| Source | dedicated `Assembly-CSharp.dll`, V3.1.0 b14 |

**Line numbers are only valid against that exact file.** A dump produced by a
different tool version or a different assembly will not line up, and the drift
between the V3.0.1 sets here and the V3.1.0 dump is roughly 3500 lines in the
NetPackage region. When a citation does not resolve, check the MD5 above before
concluding the claim is wrong.

A citation of the form `asm.il:NNNN` means the V3.1.0 file above. A citation of
the form `il/<set>-v3.0.1/...` means the tracked V3.0.1 sets in this directory.
