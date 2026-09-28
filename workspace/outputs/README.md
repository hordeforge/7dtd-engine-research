# `workspace/outputs/`: research artifacts and pinned evidence

Two kinds of file live here, and only one of them is an output. Read this
before quoting anything from the directory, and before deleting it.

## Pinned inputs, read by gates

These are **inputs** to the check suite despite living under `outputs/`. They
are compared against the live build, so a run that regenerates one of them
without the matching install changes what the gates assert:

| Path | Read by | Holds |
|---|---|---|
| `baseline/` | `tools/parity/drift-check.sh` (`make drift`) | The studied build's census, type surface, method and enum dumps, one file per axis. |
| `parity/parity_b9.json`, `parity_b10.json` | `parity_diff.py`, `research_diff.py --pair`, `drift-check.sh` | `ParitySurface` wire snapshots of the two cached builds. |
| `diffs/b9-to-b10-20260920.md` | `tests/test_committed_diff_artifacts.py`, `docs/releases/changelog-3.2.0.md` | The eight-lens build-to-build report. One report per build pair; a rerun republishes over it. |
| `census-history.csv` | `make census` (`census-pct.py --history`), `tests/test_census_pct_history.py` | One dated row per census run, replaced in place on a same-date rerun. |

Regenerate them through the command the owning tool documents, never by hand
editing the file.

## One-shot reports

`audit/`, `audit2/`, `.drafts/` and `.plans/` hold the campaign audits and the
working notes behind them, and the loose `*-audit.md` files at this level are
the same kind of thing. They are read by people, not by gates; a claim in one
of them is evidence for the commit that added it, not a current fact.

`archive/` holds the pre-V3.1.0-retarget artifacts that every file in it marks
`> **ARCHIVED (2026-08-11)**`. They are kept to reproduce historical decisions
and are superseded by the current corpus; nothing reads them.

## Rules

- Research artifacts only. No product code and no source (see
  [`../../AGENTS.md`](../../AGENTS.md)).
- A file that a gate reads is a pin, not an output: it changes only with the
  tool that owns it, and a change to it ships with the build it describes.
- The corpus itself lives in [`../../docs/`](../../docs/); this directory is
  where a claim is recorded, not where it is published.
