# Review: 7DTD dedicated-server reverse-engineering corpus

> **ARCHIVED (2026-08-11):** pre-V3.1.0-retarget research artifact; superseded by the current corpus. Historical record only.

**Artifact:** `/home/maci/Desktop/7dtd/7dtd-engine-research` (branch `re-corpus-audit-tooling`),
60 narrative docs + 20 inventory catalogs (26,087 lines, 176 diagrams), 16 maintained
Mono.Cecil tools, 2 Python gates, consumed by the sibling `../zdtd-server` clone.
**Subject of study:** the shipped 7 Days to Die V3.0.1 dedicated-server
`Assembly-CSharp.dll` (read locally; never redistributed).
**Review date:** 2026-07-24.
**Evidence:** `.drafts/7dtd-re-corpus-review-evidence.md`.
**Plan:** `.plans/7dtd-re-corpus-review-plan.md`.

> **Conflict of interest, stated up front.** I authored this artifact in the same
> session in which I am reviewing it. That is not a neutral position. Two mitigations
> were applied: (a) every finding below was re-derived from the DLL or from disk with
> a cited command rather than recalled, and (b) an independent `reviewer` subagent was
> dispatched with an explicitly adversarial brief. A reader should still weight this
> review accordingly and treat the *external* checks (§Reproducibility) as carrying
> more evidential value than my prose judgements.

---

## Summary Assessment

This is a **strong engineering artifact and a moderate research artifact.** Its
substance is real: the load-bearing wire and behavioural claims I re-checked all
hold against IL, the headline census numbers reproduce exactly, the policy boundary
(no redistributed game bytes) is clean, and an external consumer that must
byte-match a proprietary client passes its tests. The methodology chapter is
unusually good for this genre, and the corpus is honest about several things most
RE writeups quietly omit (dead code, dormant systems, client-vs-server ambiguity).

Its principal weakness is the **headline coverage metric, which does not measure what
it claims**. This review initially graded that as a Major framing problem; an
independent adversarial reviewer went further, and on re-checking its claims myself I
agree and have upgraded the finding to **Critical (C1)**. Both the numerator and the
denominator are artifacts of the measuring tool: generic-named types are credited as
"narrated" with zero deliberate references, auto-generated tables are counted as
narration, 319 client-UI types that provably never run headless are inside the
"reached" base, and the console-command subsystem the corpus documents in detail is
largely absent from that base because the tool never devirtualizes interface dispatch.
`coverage-report.md`'s assertion that "reachability is the ground truth for 'runs on a
dedicated server'" is false in both directions by the tool's own construction.

The second-order finding is more interesting than either: the project's own audit
trail shows a **high first-draft error rate**, including a wire-breaking error
authored an hour after the same agent correctly analysed the same IL. The artifact's
credibility rests substantially on its audit apparatus, not on the prose. That is a
legitimate result, and the corpus should say so more prominently than it does.

**Recommendation: Accept with revisions** (one Critical, see Recommendation). The
per-claim RE is sound and publishable as is; the coverage metric should be withdrawn
or rebuilt before it is cited.

---

## Strengths

1. **Claims are IL-traceable, and they survive independent re-checking.** Every
   spot-check I ran passed, including ones deliberately chosen to avoid the set given
   to the subagent: `NetPackageChunk` (bool + conditional i16 guard + i32 length),
   `NetPackageEncryptionPublicKey` (string + two length-prefixed byte arrays),
   `EnumDamageTypes.Suffocation = 16`. Two *nuanced* corrections also held:
   `Recipe.CanCraft` has exactly **one** call site and it is `XUiC_ItemActionList`
   (supporting the "split authority, not server-authoritative" correction), and
   `EntityBuffs.AddBuffNetwork` shows 2 send calls and **0** list mutations
   (supporting the "send side, not receive side" correction).

2. **The numbers reproduce.** All six census metrics pinned in `re-methodology.md` §1
   match `Census.exe` output exactly on a fresh run. This is the difference between a
   writeup and a measurement.

3. **An external, falsifiable consumer exists.** The `zdtd` clone implements these
   specs and must interoperate with the stock client; `zig build test` passes with 11
   tests in the `EntityCreationData` module alone. Wire errors surface as failing
   byte-offset assertions rather than as disagreements of opinion. Most RE writeups
   have no such oracle.

4. **Methodology is documented well enough to transfer.** `re-methodology.md` §8b in
   particular ("classify by referrer, not by name"; "a negative result needs the
   stronger tool") is a genuine methodological contribution, and it was written
   *because* the project got it wrong first.

5. **Honest about negative and awkward results.** The corpus states that utility AI is
   shipped but dormant, that `QuestCriteriaPOIWithinDistance` is hardcoded dead, that
   the dynamic-mesh region format it originally documented was dead code, and that
   `AuthAndLoginManager` is Discord sign-in rather than the join auth its name
   suggests. These are the findings a motivated author would be tempted to bury.

6. **Policy discipline.** 0 tracked binaries or IL dumps across 158 tracked files;
   `tools/.gitignore` was hardened after ~46k raw dump files were found sitting in the
   tools tree. Commit provenance is clean (single human author, no AI attribution).

---

## Critical Issues

### C1. The coverage metric measures a tool artifact, not documentation coverage

Raised by the independent reviewer; **I re-verified every mechanism below myself
before accepting it**, and it supersedes what this review first filed as a Major
framing issue. Four independent defects compound, two in the numerator and two in the
denominator:

**Numerator inflated**
1. **Generic-named types are credited with zero deliberate references.** Real reached
   game types named `Field`, `Entry`, and `Data` exist. Each is counted as "narrated"
   because those words occur in prose and markdown table headers. Deliberate
   (backticked) references to them across the whole corpus: **0, 0, 0**.
2. **Auto-generated tables count as narration.** `Coverage.cs` excludes only its own
   `coverage-report.md` (line 106) and routes `out-of-scope-surface.md` to the
   classified bucket (line 107). The other two machine-generated catalogs,
   `dedicated-leaves.md` and `netpackage-bodies.md`, are therefore scored as
   "narrated in a subsystem doc". I measured **536 identifiers that appear only in
   those generated files and never in hand-written prose** (the independent reviewer
   counts 593 by a type-level basis; either way the effect is large).

**Denominator wrong in both directions**
3. **Over-inclusion:** **319 `XUiC_*` client-UI types** sit inside the "reached" base.
   The walk devirtualizes `callvirt` across the entire class-override map
   unconditionally, so one virtual call drags in UI trees that a headless server
   provably never executes.
4. **Under-inclusion:** **0 `ConsoleCmd*` types** appear in the classification, because
   the override map is built purely from class inheritance (`t.BaseType` walk) and
   `Coverage.cs` contains **no handling of interface dispatch** (`grep -c
   'IConsoleCommand|Execute'` -> 0). Console commands dispatch through
   `IConsoleCommand.Execute`, so the 187-command subsystem this corpus documents in
   detail, and which unambiguously runs on a dedicated server, is largely missing from
   the set the metric is computed over.

**Consequence.** "100% accounted for" and the 66% narrated figure are not coverage
measurements. The honest narrative figure is **at most ~45%** once generated-catalog
credit is removed, over a base that is simultaneously padded with client UI and
missing a documented server subsystem. The specific sentence in
`coverage-report.md` that "**Reachability is the ground truth for 'runs on a dedicated
server'**" is false in both directions.

**Fix (any one is acceptable, in descending preference):** (a) withdraw the headline
number and publish reachability as a *lead-generation* tool rather than a coverage
metric; (b) rebuild it, excluding generated docs from the narrated set, requiring a
backticked reference, adding interface-dispatch devirtualization, and gating the base
on a dedicated-execution filter; or (c) retain it but relabel prominently as
"tool-reachable token overlap, not coverage", with the defects listed inline.

**Note on this review's own reliability:** I graded this Major on first pass and only
reached Critical after an adversarial second opinion forced a re-check. That is the
same failure mode the artifact itself exhibits (M2), reproduced inside its review.

---

## Major Issues

### M1. (Superseded by C1) Mention-depth of the narrated set

"**100% accounted for**" is a composite of *narrated* (1,799) and *classified
out-of-scope* (904). Two problems compound:

- **"Narrated" = any whole-word name mention** in a non-generated doc. Measured
  distribution over type-looking names in hand-written docs:

  | Mentions | Count | Share |
  |---|---:|---:|
  | exactly 1 | 3,939 | 48% |
  | 2-4 | 2,817 | 34% |
  | 5-19 | 1,102 | 13% |
  | 20+ | 235 | 2% |

  A type named once in a cross-reference scores identically to one with a dedicated
  section.
- **"Accounted for" bundles two very different epistemic states**: "we reverse
  engineered this" and "we decided this is out of scope". Summing them to 100% invites
  the reading "the server is fully documented", which is not what was shown.

The corpus *does* disclose the upper-bound nature in prose. It never quantifies it.
This finding stands on its own (depth is shallow even for correctly-counted types) but
is **subsumed by C1**, which shows the counted set is itself wrong. **Fix:** publish
this histogram alongside whatever replaces the headline metric.

### M2. Audit history implies unaudited prose should be treated as provisional

Two independent audit passes were run. The **second**, over docs already written
carefully, still found **3 CRITICAL + 8 MAJOR + 13 MINOR** errors. One CRITICAL was a
wire-breaking `EntityCreationData` tail error written by the same agent that had
correctly analysed that exact IL shortly before. A later pass found generator/doc
drift (frame-entries emitting 242 against an audited 244) that would have silently
reverted a fix.

This is not a defect *list* (all are fixed); it is a statement about **reliability of
the production process**. The corpus presents its conclusions with fairly uniform
confidence, when the evidence says first-draft claims in this genre carry a
materially higher error rate than audited ones. **Fix:** mark per-doc audit status
(audited / unaudited / auto-generated) so readers can weight accordingly.

### M3. Two inventories are hand-corrected but sit alongside generated ones

`dedicated-leaves.md` and `out-of-scope-surface.md` were machine-generated and then
hand-corrected (48 referrer-verified promotions). A naive regeneration silently
reverts that work. This was caught and both now carry an explicit maintenance note,
which is the right mitigation, but the underlying fragility remains: the corpus mixes
push-button and hand-maintained artifacts in one directory with similar headers.
**Fix:** either commit the promotion list as tool input so regeneration is faithful,
or move hand-maintained catalogs out of `inventories/`.

---

## Minor Issues

- **m1.** `coverage.md`'s "189 in live id-map" is a runtime observation with no
  reproducible artifact. Correctly flagged in-doc; still unverifiable here.
- **m2.** `experimental-delta.md` is pinned to a 2026-07-23 diff and cannot currently
  be refreshed (see Reproducibility). It self-labels as provisional, which is
  adequate, but the pin date should appear in the title, not only the body.
- **m3.** The "narrated" proxy counts names appearing in *any* doc including the
  changelog-like sections; a stricter proxy (name appearing in a doc that `Owns:` the
  relevant subsystem) would be more faithful and is cheap to implement.
- **m4.** Ownership overlap is plausible but unproven: `Owns:` headers mention
  entity-ish scope in 4 docs and block-ish scope in 3. These are likely legitimate
  facets (AI vs stats vs entities), but no explicit disjointness check exists.

---

## Reproducibility and Verification

| Check | Result | Evidence |
|---|---|---|
| Census metrics vs pinned baseline | **PASS 6/6 exact** | `Census.exe` vs `re-methodology.md` §1 |
| Independent wire spot-checks | **PASS 3/3** | Chunk, EncryptionPublicKey, EnumDamageTypes |
| Nuanced authority claims | **PASS 2/2** | `Recipe.CanCraft` (1 call site, client UI); `AddBuffNetwork` (2 sends, 0 list mutations) |
| Structural gate | **PASS** | `test_dedi_coverage_docs.py`: docs 11, dump sets 8, tools 8 |
| Dump-regen gate | **PASS** | `test_re_dump_regen.py` (exit 0, non-empty regeneration) |
| External consumer | **PASS** | `../zdtd-server` `zig build test` green, 11 ECD tests |
| Policy (no game bytes tracked) | **PASS** | 0 of 158 tracked files are IL/DLL/EXE |
| Link/format hygiene | **PASS** | 0 broken links, 0 odd fences, 0 em dashes, INDEX complete |
| Experimental-delta refresh | **Verification: BLOCKED** | `steamcmd` not installed; a fresh `latest_experimental` pull needs Steam credentials. External dependency + user decision, **not** a corpus defect. |
| "189 live id-map" | **Verification: BLOCKED** | runtime-only observation; no static artifact to re-derive from |
| Independent adversarial review | **Delivered; findings folded in** | `.drafts/7dtd-re-corpus-independent-review.md`. Verdict "two-tier quality": micro-level wire RE excellent and reproduced exactly; macro-level coverage headline is "definitional sleight of hand over a distorted denominator". 2 critical, 3 major, 5 minor, 1 unverifiable. It reported **zero reproduction failures**: generated inventories regenerated byte-identical, both test gates pass. Its central criticism became **C1** after I re-verified each mechanism. |

---

## Inline Annotations

- **`docs/inventories/coverage-report.md` → Totals table.** "accounted for … 100%"
  needs the depth histogram adjacent, or a rename. See M1.
- **`docs/re-methodology.md` §8b.** Strongest section in the corpus. The two failure
  modes (field access invisible to call sweeps; closure hits credited to the wrong
  owner) plus "a negative claim needs the stronger tool" are transferable beyond this
  game. Keep and lead with it.
- **`docs/protocol-packages.md` §4.2 (WorldInfo).** Correctly distinguishes the
  entry-count prefix from a byte length and explains the desync consequence. Good
  model for how a wire correction should be written.
- **`docs/protocol-packages.md` §5.1 (EntityCreationData).** Now a three-section model
  (header / `entityClass` switch / networkWrite tail) with two explicit traps
  (`isSleeperPassive` sleeper-gated; junk-drone extras outside the guard) and the
  shared-count note for `fallingBlocks`. This section previously contained a
  wire-breaking error; its current form is the corpus's best worked example.
- **`docs/items.md` §2 (ItemValue packing).** Declares itself "authoritative for byte
  order" (appropriate for a table that a clone parses), and it survived two audits
  after the stat-type byte was added.
- **`docs/dedicated-misc-systems.md` → WorldStats.** Good example of a corrected
  classification: promoted out of "client-only" once a *field* read (`DensityScore`)
  was found feeding RWG placement. Cites the methodological cause.
- **`docs/out-of-scope-surface.md` header.** The maintenance note is necessary; see M3
  for why the arrangement is still fragile.

---

## Recommendation

**Accept with revisions.** The split verdict matters and both halves should be
reported together:

- **The per-claim reverse engineering is sound and can stand as published.** Every
  wire and behavioural claim checked by me and by the independent reviewer held
  against fresh IL, including cited IL offsets. Reproduction had **zero** failures
  across both reviewers. The external clone passes. This is the bulk of the artifact.
- **The coverage metric should be withdrawn or rebuilt before anyone cites it** (C1).
  It is not a coverage measurement, and one sentence in `coverage-report.md` asserts
  the opposite of what the tool does.

Required revisions, in priority order:

1. **C1 - fix or withdraw the coverage headline.** Minimum acceptable action: delete
   the "reachability is the ground truth" sentence and relabel the number. Preferred:
   rebuild per C1's fix list (exclude generated docs, require backticked references,
   devirtualize interface dispatch, filter the base to plausibly-dedicated code).
2. **M2 - expose per-doc audit status**, so unaudited prose is visibly weaker evidence.
   The project's own error history justifies this, and so does this review's own
   first-pass miss on C1.
3. **M3 - make the promotion list a tool input** so the hand-corrected inventories are
   faithfully regenerable.
4. **M1 - publish the mention-depth histogram** alongside whatever replaces the metric.

Not required, but highest-value next work: refresh the experimental delta once
`steamcmd`/credentials are available, since a stale diff is the one part of the corpus
that decays on its own.

Not required, but the highest-value next work: refresh the experimental delta once
`steamcmd`/credentials are available, since a stale diff is the one part of the
corpus that decays on its own.

---

## Sources

All local; no external URLs were needed for this review.

- Artifact root: `/home/maci/Desktop/7dtd/7dtd-engine-research`
- Docs reviewed: `docs/*.md` (60), `docs/inventories/*.md` (20), notably
  `docs/re-methodology.md`, `docs/protocol-packages.md`, `docs/items.md`,
  `docs/coverage.md`, `docs/inventories/coverage-report.md`,
  `docs/out-of-scope-surface.md`, `docs/inventories/dedicated-leaves.md`,
  `docs/dedicated-misc-systems.md`, `docs/crafting-recipes.md`, `docs/buffs.md`
- Tooling: `tools/src/{Census,Coverage,Xref,RefScan,LeafInfo,WireBodies,DumpMethod,EnumList}.cs`,
  `tools/tests/{test_dedi_coverage_docs,test_re_dump_regen}.py`
- Lab notebook: `workspace/CHANGELOG.md` (31 dated entries)
- External consumer: `/home/maci/Desktop/7dtd/zdtd` (`zig build test`)
- Subject assembly (read-only, not redistributed):
  `/home/maci/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll`
- Evidence notes: `workspace/outputs/.drafts/7dtd-re-corpus-review-evidence.md`
- Independent adversarial review: `workspace/outputs/.drafts/7dtd-re-corpus-independent-review.md`
