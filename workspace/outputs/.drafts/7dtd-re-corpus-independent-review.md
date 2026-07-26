# Independent adversarial review: 7dtd-research RE corpus (V3.0.1)

Reviewer: independent pass, no prior stake in the corpus. Subject assembly:
`/home/maci/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll`.
All commands below were run from the repo root on 2026-07-25.

## Verdict

**Two-tier quality. The micro-level wire reverse engineering is excellent and
independently verifiable; the macro-level "100% accounted for" coverage headline
is definitional sleight of hand over a distorted denominator and should not be
presented as a coverage result.** Every load-bearing wire claim I spot-checked
(NetPackageWorldInfo, EntityCreationData including its cited IL offsets, ItemValue,
ItemStack, NetPackageWorldInitInfo) reproduced exactly against fresh IL dumps, the
generated inventories regenerate byte-identical, and the sampled dead-code claims
survive Xref. But the coverage metric that headlines the corpus counts a type as
"narrated" if its name token appears anywhere in any doc (including auto-generated
catalogs and markdown table headers), and its "reached" base both includes 362
client-UI types that never run headless and excludes 186 of the 187 console
commands that demonstrably do. Fix the framing and this is a strong corpus; ship
the headline as-is and any informed reader who re-derives the numbers will
discount the whole repo.

Severity counts: 2 critical, 3 major, 5 minor. 1 item unverifiable.

## Strengths (all independently re-verified)

- **[S1] Wire-format accuracy is outstanding.** I dumped IL fresh and checked
  byte-for-byte:
  - `docs/protocol-packages.md` §5.1 (`EntityCreationData.write`): the
    three-section structure, all five entityClass branches, the itemClass branch
    jumping straight to the tail, and both gating details are exact. The doc's
    cited offsets are real: `brfalse IL_03C5` at IL_033F (networkWrite guard),
    `brfalse.s IL_03C5` at IL_03B2 (isSleeperPassive only when isSleeper), and
    the junk-drone pair sits after the guard at IL_03C5, exactly as claimed.
    (`mono tools/bin/DumpMethod.exe "$ASM" EntityCreationData write`)
  - The shared-count trap is real: `EntityCreationData.read` does one
    `ReadInt32` (IL_02C2) then `newarr BlockValue` / `newarr Vector3i` /
    `newarr TextureFullArray` from the same value with no second `ReadInt32`
    before IL_04AA; `TextureFullArray::Write` loops to the literal 1 writing one
    i64. Both match the doc.
  - §4.2 `NetPackageWorldInfo`: read IL parses `i32 count` then per-entry
    `{string, u32}` into `Dictionary<string,uint>` then `i64`, confirming the
    "count, NOT byte length" warning. Write order matches field-for-field.
  - §4.3 `NetPackageWorldInitInfo`: write IL=57 / read IL=58 exactly as stated;
    read ends after the two count-prefixed loops with no trailing length;
    `NetPackageWorldInitInfoRequest.read` IL=1 (empty body claim holds).
  - `docs/items.md` §2 (`ItemValue.Write`): marker 0/9, flags bit0 =
    `type >= Block.ItemsStartHere` with the id written minus `ItemsStartHere`
    (IL_0027..IL_0037), Stats triplet (type byte, value-or-0, boosted-or-0), the
    `isinst ItemClassModifier -> brtrue IL_0262` guard skipping both mod
    sections, Seed zeroed when type==0, TextureFullArray presence bool. All
    exact. `ItemStack.Write` clamp to 65535 confirmed.
- **[S2] Regeneration is genuinely push-button.** `Coverage.exe` and
  `WireBodies.exe` reproduce the committed `coverage-report.md` and
  `netpackage-bodies.md` byte-identically (diff clean). Both python gates pass.
  `Census.exe` reproduces the totals `full-surface.md` claims (7413 types,
  53011 method bodies, 193 top-level NetPackage*).
- **[S3] Sampled negative claims hold.** `docs/chunk-providers.md` says
  `ChunkBlockLayerLegacy` `Read`/`Write` and `ChunkBlockChannel.Convert` have no
  callers while its static index helpers stay live: Xref returns 0 call sites for
  all three, and RefScan shows the remaining 26 refs are exactly the static-helper
  callers the doc predicts (`Chunk::SetBlockRaw`, `RecalcHeights`, MeshGenerator*,
  PrefabChunk). `ChunkProviderParameter`: 0 external refs, matching "never
  constructed". This is careful, falsifiable dead-code work, not hand-waving.
- **[S4] The lab notebook is honest.** `workspace/CHANGELOG.md` self-reports a
  real regeneration trap (frame-entries 242 vs 244 nested-type drift) and the fix
  is verifiably in place (the regen test now prints 244). The
  hand-maintained-vs-regenerable distinction in `dedicated-leaves.md` and
  `out-of-scope-surface.md` headers is exactly the kind of maintenance honesty
  most corpora lack.
- **[S5] Stated limitations are mostly real, not performative.**
  `re-methodology.md` §7 names concrete non-IL residuals (script execution order,
  native plugins, XML semantics) and the docs actually route those to
  `residuals.md` instead of faking them.

## Critical

- **[C1] The "100% accounted for" headline is definitionally guaranteed and
  measures name-token presence, not documentation.**
  `docs/inventories/coverage-report.md` (Totals: "accounted for ... 2703 (100%)").
  Mechanism, from `tools/src/Coverage.cs` lines 100-110: the "narrated" set is
  every regex word token `[A-Za-z_][A-Za-z0-9_]+` in every `docs/**/*.md` except
  `coverage-report.md`; "classified" is the same over `out-of-scope-surface.md`.
  Consequences I measured (patched Coverage to dump per-type status, script in
  scratchpad `narration_audit.py`):
  - **593 of 1799 "narrated" types (33%) appear only in the auto-generated
    `docs/inventories/` catalogs**, never in a narrative subsystem doc. The
    report's own gloss ("**Narrated %** = reverse-engineered in a subsystem doc
    (the real depth metric)") is therefore false for a third of the set. The
    honest narrative figure is at most 1206/2703 = 45%, before subtracting prose
    collisions.
  - **Provable false positives from markdown table headers:** reached game types
    named `Field`, `Entry`, `Call`, `Data` are counted "narrated" because docs
    contain table headers like `| Field | Type | Role |` (save-region.md:49),
    `| Order | Call | Notes |` (loop-gmupdate.md:52), "Entry points"
    (loop-gmupdate.md:14). Verified by grep; none of these types is discussed
    anywhere.
  - The per-namespace table in the same file labels its column "documented" and
    shows 100% for every namespace, silently switching definition from
    "narrated" (66% headline) to "narrated OR classified". Two contradictory
    uses of "documented" in one generated file.
  - "Accounted for" for 230 of the classified types means: the name appears in a
    single comma-separated blob under "Utility / collections / infra" in
    `out-of-scope-surface.md` with no per-type justification. Reaching 100% under
    this definition requires only that someone paste the gap list into a doc.
  The number is not fake, but it is doing exactly the work the task suspected:
  a reader will take "100% accounted, 66% narrated" as coverage depth; the
  reproducible truth is "every reached type name appears somewhere; at most 45%
  are named in a narrative doc; an unmeasured smaller fraction are actually
  explained."
- **[C2] "Reachability is the ground truth for 'runs on a dedicated server'"
  (coverage-report.md preamble) is false in both directions, by construction of
  the tool.**
  - *Over-approximation:* `Coverage.cs` devirtualizes every `callvirt` to all
    overrides regardless of instantiation. Result: **362 `XUiC_*` client-UI
    types are in the "reached" base** of a headless server
    (`grep -c '^XUiC_' cov2.md.reached.tsv` = 362), which the corpus then has to
    classify away in `out-of-scope-surface.md` (421 "Client UI" types). The
    denominator inflates and the classification doc exists largely to mop up the
    tool's own over-approximation.
  - *Under-approximation:* the override map only walks `BaseType` chains, so
    **interface dispatch is never devirtualized**. Concrete casualty: the
    console command family. `docs/inventories/console-command-list.md` documents
    **187 commands**, all of which execute on a dedicated server, yet only ONE
    (`ConsoleCmdMem`) is in the 2703-type reached base
    (`grep '^ConsoleCmd' cov2.md.reached.tsv`). The corpus documents them anyway
    (good), but the "100% of the reachable surface" denominator silently excludes
    an entire executing family, and nothing in coverage-report.md discloses the
    interface-dispatch hole. Reflection-instantiated XML classes are similarly
    invisible unless separately called.
  Combined with C1 this means both the numerator and denominator of the headline
  metric are tool artifacts. The fix is framing, not tooling: state "name-mention
  over a devirtualized static call graph that over-includes client overrides and
  under-includes interface/reflection dispatch" in the Totals section, not buried
  as "an upper bound" in one clause.

## Major

- **[M1] The out-of-scope classification is name-triage presented next to
  verified work, and contains at least one dedicated-relevant type.**
  `docs/out-of-scope-surface.md` "Utility / collections / infra (230)" is a flat
  name list. `ClientPowerData` sits in it, but
  `mono tools/bin/Xref.exe "$ASM" ClientPowerData .ctor` shows it is constructed
  in `TileEntityPowerSource::.ctor` and `TileEntityPowerSource::read`, i.e. the
  power tile-entity serialization path that `docs/tile-entities-power.md` owns
  (and which never names it). The file itself admits the name classifier already
  misplaced 48 types (later promoted via RefScan). There is no evidence the
  remaining ~200 utility-bucket types received the referrer check the header
  says is required ("re-verify with RefScan ... before changing any
  classification" cuts both ways: the initial placements were never
  referrer-verified either).
- **[M2] Stale cross-doc status and count drift.**
  - `docs/coverage.md` family row 6 still lists "residual tail:
    EntityCreationData per-class" while `docs/protocol-packages.md` §8 marks the
    same item "fully extracted (56 fields, per-class branches)". One of these
    survived from an earlier draft (commit ca1ba42 closed it).
  - `docs/inventories/netpackages.md` line 5 says "183 packages + **60** nested
    serializers"; the generator output and `protocol-packages.md` line 25 say
    **61**. Trivial, but this is a corpus whose selling point is that counts are
    machine-checked.
- **[M3] The 66% narrated headline is not just an upper bound, it is the wrong
  population, and the disclosure is a single parenthetical.** coverage-report.md
  says "Name-mention is an upper bound on narration (a type named in passing
  counts)" but does not say that generated inventories feed the signal, that a
  third of the set has no narrative mention at all, or that markdown table
  headers count. Given the repo's own honesty standards (CHANGELOG, methodology
  doc), this under-disclosure is out of character and correctable in one
  paragraph plus a stricter tokenizer (exclude `docs/inventories/`, require
  backtick-quoted mentions).

## Minor

- **[m1]** `docs/out-of-scope-surface.md` says "Total out-of-scope reached types
  classified: **915**"; `coverage-report.md` says classified = **904**. The delta
  (11 types both narrated and classified) is explained in neither file.
- **[m2]** `docs/items.md` §2 ItemStack row: "itemValue ... only if count > 0".
  IL gates on `count != 0` (`brfalse.s IL_0031` on the raw field) and the u16 is
  the clamped value while the gate uses the unclamped field; a negative count
  would write a wrapped u16 and still emit the value. Cosmetic, but "write is
  truth" discipline should state the actual predicate.
- **[m3]** Working-tree hygiene: `tools/WeatherManager/`, `tools/SkyManager/`,
  `tools/AllyEvent/` etc. contain full per-type IL dumps of the entire assembly
  (88 namespace dirs under WeatherManager alone), evidently from tool runs with
  swapped output args. They are git-ignored via enumerated lines in
  `tools/.gitignore` (line 12) rather than deleted. Given the repo's "bulk IL
  only under git-ignored `il/`" policy, ignoring accidental dump trees by name
  instead of removing them invites a future accidental commit of game IL.
- **[m4]** `docs/inventories/dedicated-leaves.md` headline says "**88 leaf
  types**" but the file contains 136 leaf rows (88 grouped + 48 promoted). The
  promoted section is labeled, but the headline count contradicts the file's own
  row count at first read.
- **[m5]** Regeneration cwd conventions are inconsistent: coverage-report.md says
  `mono bin/Coverage.exe "$ASM" ../docs coverage-report.md` (run from
  inventories/), netpackage-bodies.md uses repo-root paths. Both work, but a
  third party following one doc's convention on the other file writes output to
  the wrong place.

## Reproducibility results (what I ran, what happened)

| Check | Command (from repo root, `$ASM` = dedicated Assembly-CSharp.dll) | Result |
|---|---|---|
| Coverage regen | `mono tools/bin/Coverage.exe "$ASM" docs <scratch>/coverage-report.md` then `diff` | **Byte-identical** to committed `docs/inventories/coverage-report.md`; stderr `reached methods=28374 game types=2703 documented=1799 (66%)` matches |
| WireBodies regen | `mono tools/bin/WireBodies.exe "$ASM" <scratch>/netpackage-bodies.md` then `diff` | **Byte-identical**; "183 packages, 61 nested serializers" |
| Test gate 1 | `python tools/tests/test_dedi_coverage_docs.py` | PASS (docs_checked=11, dump_sets=8, tools=8) |
| Test gate 2 | `python tools/tests/test_re_dump_regen.py` | PASS; recompiles legacy dumper via mcs, regenerates frame-entries (244 MB-update methods, matching the CHANGELOG fix) |
| Census | `mono tools/bin/Census.exe "$ASM"` | 7413 types / 53011 bodies / 193 top-level NetPackage*, matching `full-surface.md` and `engine-limitations.md` |
| IL spot-checks | `DumpMethod` on `EntityCreationData write/read`, `TextureFullArray Write`, `NetPackageWorldInfo write/read`, `NetPackageWorldInitInfo write/read`, `ItemValue Write`, `ItemStack Write` | All doc claims confirmed, including cited IL offsets (see S1) |
| Dead-code sample | `Xref.exe ... ChunkBlockLayerLegacy Read/Write`, `ChunkBlockChannel Convert`; `RefScan.exe` over 5 sampled types | 0 call sites for all three claimed-dead methods; ChunkProviderParameter 0 external refs; claims confirmed |
| Metric audit | Patched `Coverage.cs` copy (scratchpad `Coverage2.cs`) dumping per-type narration status + `narration_audit.py` | 593/1799 narrated only via generated inventories; `Field`/`Entry`/`Call`/`Data` false positives; 362 XUiC_* and only 1 ConsoleCmd* in reached base |

Nothing failed to reproduce. The reproducibility story is the corpus's strongest
asset; the criticism is about what the reproduced numbers mean, not whether they
reproduce.

## Unverifiable / blocked

- **EntityVBlimp "dead in stock config"** (`docs/dedicated-leftovers.md` §Out of
  scope): the code-side half is consistent (RefScan: no code references), but the
  claim rests on `entityclasses.xml` having the entity commented out. XML content
  ships inside game data archives I did not extract in this pass: **inferred
  plausible, not verified here**.
- **Per-type correctness of the ~200 unpromoted "Utility / collections / infra"
  classifications**: verifying all of them needs a full RefScan sweep (the same
  one that already moved 48 types). I checked one (ClientPowerData) and it is
  questionable (M1); the rest are **unverified**, and the corpus should not imply
  otherwise.
- **Runtime claims pinned to live-server observation** (e.g. "Live pin
  (2026-07-18 dedi)" in coverage.md, loadgen "golden wire" evidence in
  protocol.md): these depend on artifacts outside this repo
  (`7dtd-loadgen`, `zdtd`); not re-run in this review.

## Inline annotations

> "| ...**accounted for** (narrated + classified) | **2703 (100%)** |"
**[C1] CRITICAL:** "Accounted for" means the type's name token appears somewhere
in the docs tree. 593 of the 1799 "narrated" appear only in generated catalogs;
`Field`, `Entry`, `Call`, `Data` are "narrated" by markdown table headers. The
100% is achievable by pasting the gap list into any doc, and effectively was
(out-of-scope name blobs).

> "**Narrated %** = reverse-engineered in a subsystem doc (the real depth metric)."
**[C1/M3] CRITICAL:** False for at least a third of the set (inventory-only
mentions). Honest narrative-doc figure is at most 45%, itself still an upper
bound over prose collisions.

> "Reachability is the ground truth for \"runs on a dedicated server\"."
**[C2] CRITICAL:** The reached set contains 362 XUiC_* client-UI types (devirt
over-approximation) and omits 186 of 187 documented console commands (interface
dispatch is never devirtualized in Coverage.cs). Neither direction is disclosed
here.

> "| Namespace | reached | documented | undocumented | % |" (all rows 100%)
**[C1] MAJOR:** "documented" in this table means narrated-or-classified, while
the Totals table's 66% uses narrated-only. Same word, two definitions, same file.

> "Total out-of-scope reached types classified: **915**." vs coverage-report's "904"
**[m1] MINOR:** 11-type discrepancy (double-counted narrated+classified) explained
in neither document.

> "`ChunkBlockLayerLegacy` serialization and `ChunkProviderParameter` identified as dead code."
**[S3] VERIFIED:** Xref confirms 0 call sites for Read/Write/Convert;
ChunkProviderParameter has 0 external refs; the doc correctly separates the live
static index helpers. Model example of a falsifiable dead-code claim.

> "residual tail: EntityCreationData per-class, DynamicMesh/POIAround, Quest/Party" (coverage.md)
**[M2] MAJOR:** Contradicted by protocol-packages.md §8 ("fully extracted") and
the verified §5.1 table. Draft residue.

> "`AIFocus`1`, `ActivitySecret`, ... `ClientPowerData`, ..." (out-of-scope utility blob)
**[M1] MAJOR:** `ClientPowerData` is constructed in `TileEntityPowerSource::.ctor`
and `::read` (Xref), i.e. the documented power-sync path. A name blob is
classification, not verification, and this entry appears misclassified.

> "itemValue | `ItemValue.Write` | **only if count > 0**" (items.md §2)
**[m2] MINOR:** IL predicate is `count != 0` on the unclamped field.

> "**88 leaf types**, grouped by owning subsystem." (dedicated-leaves.md)
**[m4] MINOR:** File contains 136 leaf rows (88 + 48 promoted).

## Sources

- Assembly: `/home/maci/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll` (local, V3.0.1 dedicated)
- All other evidence: files and tools inside `/home/maci/Desktop/7dtd/7dtd-research` as cited above; scratch artifacts (patched Coverage2.cs, audit scripts, IL dumps) in the session scratchpad.
