# Review plan: 7DTD dedicated-server RE corpus

## Artifact
- **Identifier:** the reverse-engineering corpus in `/home/maci/Desktop/7dtd/7dtd-engine-research`
  (branch `re-corpus-audit-tooling`), plus its sibling consumer `../zdtd-server`.
- **Source type:** local repository. Markdown research corpus (`docs/`, 80 files) +
  C#/Mono.Cecil tooling (`tools/src/`) + Python test gates (`tools/tests/`).
- **Target of study:** the shipped, proprietary `Assembly-CSharp.dll` of 7 Days to Die
  V3.0.1 dedicated server (not redistributed; read locally).
- **Conflict of interest:** this artifact was produced by the reviewer (me) during the
  current session. Findings must therefore be independently re-derived from the DLL,
  not recalled, and an independent `reviewer` subagent is dispatched as a counterweight.

## Review criteria
| Criterion | What "good" means for THIS artifact |
|---|---|
| Novelty / contribution | Does it establish facts not otherwise available? Is the contribution the docs, the method, or the tooling? |
| Empirical rigor | Is every load-bearing claim traceable to a specific IL site, or is some of it inference? |
| Baselines | Is there an external check (a clone that must interoperate, cross-version diff, live capture)? |
| Reproducibility | Can a third party regenerate the numbers and the generated docs from their own game copy? |
| Claims validity | Are coverage/completeness claims (e.g. "100%") defined precisely enough to be falsifiable, and are they true under that definition? |
| Figures / tables | Are the wire tables, counts, and diagrams correct and internally consistent? |
| Metrics | Are the reported metrics (coverage %, counts, IL sizes) reproducible and honestly bounded? |
| Related work | Does it situate itself against the sibling repos and prior dumps, without scope bleed? |
| Writing quality | Single home per topic, honest hedging, no overstatement, house style respected. |

## Verification checks to perform
1. **Independent claim re-derivation:** pick load-bearing wire/behaviour claims and
   re-check them against the DLL with the committed tools (not from memory).
2. **Metric reproducibility:** re-run `Census`, `Coverage`; confirm the headline
   numbers in the docs match tool output exactly.
3. **Generated-doc reproducibility:** regenerate the auto-generated inventories and
   diff against the committed files.
4. **Test gates:** run `tools/tests/` and record pass/fail.
5. **Policy compliance:** confirm no game IL/DLL/assets are tracked in git.
6. **Consumer check:** confirm the sibling clone builds and its tests pass against the
   specs this corpus provides (an external, falsifiable consumer of the claims).
7. **Internal consistency:** broken links, duplicate ownership, contradictory counts.
8. **Honesty audit:** look for unfalsifiable or overstated claims, and for places where
   a limitation is asserted but not demonstrated.

## Deliverables
- Evidence: `workspace/outputs/.drafts/7dtd-re-corpus-review-evidence.md`
- Final review: `workspace/outputs/7dtd-re-corpus-review.md`
