#!/usr/bin/env bash
# Run the version-update tooling readiness bench from repo root.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
python3 tools/tests/bench_version_update_tooling.py
