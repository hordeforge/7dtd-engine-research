#!/usr/bin/env bash
# Autoresearch benchmark wrapper for version-update tooling readiness.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
python3 tools/tests/bench_version_update_tooling.py
