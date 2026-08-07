# Autoresearch: version-update tooling readiness

Session artifacts for the bounded experiment that improved post-TFP-update
tooling. Durable tooling lives under `tools/`; this directory only keeps the
metric log and session notes.

## Config

| Field | Value |
|---|---|
| Optimization target | `version_update_readiness` (0-100, **higher better**) |
| Benchmark | `workspace/autoresearch/run.sh` → `tools/tests/bench_version_update_tooling.py` |
| Files in scope | `tools/src/StockFacts.cs`, `tools/tests/check_stock_facts.py`, `tools/stock-sync.sh`, `tools/post-update.sh`, `tools/parity/*`, `tools/data/stock_facts.json`, `Makefile`, `tools/README.md` |
| Environment | local (merged to `main` as `f28ec62`) |
| Max iterations | 20 |
| Baseline | **83.04** |
| Best | **100.0** (iteration 5) |

## Metric components (weighted)

| Component | Weight | Final |
|---|---:|---:|
| current_pin_green | 0.20 | 1.0 |
| no_soft_literals | 0.15 | 1.0 |
| mutation_facts_fail | 0.20 | 1.0 |
| mutation_doc_fail | 0.15 | 1.0 |
| schema_breadth | 0.15 | 1.0 |
| update_entrypoint | 0.10 | 1.0 |
| tooling_hardcode_debt | 0.05 | 1.0 |

## Iterations

| # | Score | Decision | Hypothesis |
|---:|---:|---|---|
| 0 | 83.04 | baseline | measure |
| 1 | 90.54 | keep | remove fixed 3.1.0 soft paths in checker |
| 2 | 94.04 | keep | post-update.sh + make + STOCK_SYNC_DRIFT hook |
| 3 | 98.96 | keep | DUMP_SETS from stock_facts; update schema group |
| 4 | 99.68 | keep | pins group; clear remaining docstring literal |
| 5 | 100.0 | keep | behaviour Constants extract via cctor FieldInt/R4 |

## Stop reason

Metric ceiling reached with stock-check still green. Remaining work is
operational (run `make post-update` on the next TFP build, re-Dump changed
families, expand pin sites as needed).

## Deliverables (in `tools/`)

- `tools/post-update.sh` + `make post-update`
- facts-driven version pins in `check_stock_facts.py`
- `stock_facts` schema: `update`, `pins`, `behaviour`
- dump-set tests use `dump_label_suffix()` from facts
- bench: `tools/tests/bench_version_update_tooling.py`

## Re-run

```bash
./workspace/autoresearch/run.sh
# or
make readiness
```

Results append path: `workspace/autoresearch/results.jsonl` (session log only;
bench prints score to stdout).
