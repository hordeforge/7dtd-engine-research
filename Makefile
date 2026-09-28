# 7dtd-engine-research: stock RE tooling + pin gates.
ROOT := $(CURDIR)
TOOLS := $(ROOT)/tools
# The live dedicated build, resolved the way the Python tools resolve it:
# ASM / SEVENDTD_ASM / SEVENDTD_DS_DIR first, then every Steam library root of
# the host OS. tools/asm_path.py is that one resolution, so make, the shell
# entry points and the tools cannot answer with three different installs.
# stderr is dropped here because `make help` runs on a checkout with no game:
# the targets that need the DLL say so themselves.
ASM ?= $(shell python3 "$(TOOLS)/asm_path.py" 2>/dev/null)
# The install root holding Data/Config (the directory the depot manifest
# describes), the same install as the assembly above.
GAME_ROOT ?= $(shell python3 "$(TOOLS)/asm_path.py" --game-dir 2>/dev/null)
ASM_VARS := ASM, SEVENDTD_ASM, SEVENDTD_DS_DIR

.PHONY: install-check bench-bodydiff tools stock-sync stock-check post-update census drift test test-docs lint verify verify-live facts regen-check readiness help cross-links sibling-cites save-roundtrip save-roundtrip-all latest

help:
	@echo "Fresh clone, no game install? These need nothing but python3:"
	@echo "  make test-docs  - the CI gate (docs, links, pins, layout); DLL-free"
	@echo "  make lint       - static analysis (see its own version pins below)"
	@echo "  make tools      - build Mono.Cecil dumpers (tools/bin); needs mono + mcs"
	@echo "With a game install: make test, make verify. The DLL is discovered"
	@echo "(ASM, SEVENDTD_ASM, SEVENDTD_DS_DIR, then this OS's Steam roots);"
	@echo "ASM=/path/to/Assembly-CSharp.dll selects it explicitly."
	@echo "One gate at a time: python3 tools/tests/<gate>.py (all of them are listed"
	@echo "in tools/README.md)."
	@echo ""
	@echo "make tools        - build Mono.Cecil dumpers (tools/bin)"
	@echo "make lint         - static analysis: ruff check+format + mypy (Python) + shellcheck (shell)"
	@echo "make cross-links  - resolve every cross-repo .md link in the sibling workspace"
	@echo "make sibling-cites - verify every sibling repo's research citations resolve against docs/"
	@echo "make save-roundtrip - verify a real stock save against the documented codecs (main.ttw + region files)"
	@echo "make save-roundtrip-all - verify EVERY probe save + the shipped Navezgane world (full fleet round-trip)"
	@echo "make latest       - newest build vs the studied pin (ARGS=--check / --fetch / --verify-install Managed)"
	@echo "make install-check - every install file vs Steam's manifest (ARGS=\"--only Managed\" to keep it fast)"
	@echo "make stock-sync   - extract stock_facts.json from live DLL + pin check"
	@echo "make stock-check  - pin check only (committed JSON; also diffs facts vs the live DLL when present)"
	@echo "make facts        - view the machine-checked stock pins (census/save/behaviour)"
	@echo "make post-update  - after TFP patch: stock-sync + drift (tools/post-update.sh)"
	@echo "make census       - Census.exe against ASM"
	@echo "make drift        - parity drift-check vs baseline"
	@echo "make readiness    - version-update tooling readiness bench (0-100)"
	@echo "make bench-bodydiff - deterministic perf gate for the body-diff lens (perf instructions:u)"
	@echo "make test         - full suite (structural, stock-check, reach, inventories, surface, links)"
	@echo "make test-docs    - DLL-free corpus invariants (runs in CI)"
	@echo "make verify       - one-command gate: doc links, pins, readiness, facts, xml data (needs the live game)"
	@echo "make verify-live  - the body of verify, after its ASM preflight; run verify, not this"
	@echo "make regen-check  - regenerate-inventory check (needs mcs/mono + live DLL)"

tools:
	cd "$(TOOLS)" && ./build.sh --skip-legacy

stock-sync:
	cd "$(TOOLS)" && ASM="$(ASM)" ./stock-sync.sh

stock-check:
	cd "$(TOOLS)" && ./stock-sync.sh --check-only

# Quick view of the machine-checked stock pins (version, sim, behaviour).
facts:
	python3 "$(TOOLS)/facts.py"

# Every installed file against Steam's own manifest for the installed build.
# Reads the whole install (17.6 GB, about 11 s here); ARGS="--only Managed"
# narrows it to the research-critical managed payload, ARGS="--ignore platform.cfg"
# skips a file the server rewrites at runtime.
install-check:
	@test -d "$(GAME_ROOT)/7DaysToDieServer_Data/Managed" || { \
	  echo "install-check: no dedicated-server install root resolved (got '$(GAME_ROOT)' from ASM='$(ASM)');" >&2; \
	  echo "  set $(ASM_VARS), or pass GAME_ROOT=<install root>" >&2; \
	  exit 2; }
	python3 "$(TOOLS)/steam/steam_manifest.py" --verify "$(GAME_ROOT)" $(ARGS)

# Newest dedicated build from Steam PICS + the studied-build pin. ARGS=--check
# exits 1 when a build newer than the pin exists (cron/CI); ARGS=--fetch pulls it.
latest:
	python3 "$(TOOLS)/steam/steam_builds.py" $(ARGS)

post-update:
	cd "$(TOOLS)" && ASM="$(ASM)" ./post-update.sh

census: tools
	@test -f "$(ASM)" || { \
	  echo "census: no Assembly-CSharp.dll resolved (got '$(ASM)'); set $(ASM_VARS) or ASM=<path>" >&2; \
	  exit 2; }
	MONO_PATH="$(TOOLS)/bin" mono "$(TOOLS)/bin/Census.exe" "$(ASM)"
	python3 "$(TOOLS)/census-pct.py" "$(ASM)" --history "$(ROOT)/workspace/outputs/census-history.csv"
	@echo "--- machine-checked stock pins ---"
	python3 "$(TOOLS)/facts.py"

drift:
	cd "$(TOOLS)/parity" && ./drift-check.sh "$(ASM)"

readiness:
	python3 "$(TOOLS)/tests/bench_version_update_tooling.py"

# Perf gate for the one slow research lens: pins retired instructions and CPU
# time of asm_body_diff.py (wall is reported, not asserted). Needs perf
# permission for user-space counters + the local game DLLs; SKIPs otherwise.
bench-bodydiff:
	python3 "$(TOOLS)/tests/bench_asm_body_diff.py"

# Regenerate-inventory check: compiles legacy/DumpFrameEntries and re-derives
# the frame-entries inventories from the live DLL (needs mcs + mono).
regen-check:
	python3 "$(TOOLS)/tests/test_re_dump_regen.py"

# Static analysis gate: same commands in CI (ci.yml lint job). ruff reads
# ruff.toml and mypy reads mypy.ini at the repo root; format --check keeps the
# tree formatter-clean; shellcheck runs at its strictest severity. The ruff and
# mypy binaries must match the CI pins (single source of truth:
# .github/workflows/ci.yml), because their rules drift between releases.
lint:
	@for tool in ruff mypy; do \
	  expected=$$(sed -n "s/^ *uv tool install $$tool==\([0-9][0-9.]*\)/\1/p" .github/workflows/ci.yml | head -1); \
	  if [ -z "$$expected" ]; then \
	    echo "lint: cannot read the $$tool pin from .github/workflows/ci.yml" >&2; exit 2; \
	  fi; \
	  command -v $$tool >/dev/null 2>&1 || { \
	    echo "lint: $$tool not on PATH; install the CI pin: uv tool install $$tool==$$expected" >&2; exit 2; \
	  }; \
	  actual=$$($$tool --version | awk '{print $$2}'); \
	  if [ "$$actual" != "$$expected" ]; then \
	    echo "lint: local $$tool $$actual != CI pin $$tool==$$expected; align both together (.github/workflows/ci.yml)" >&2; exit 2; \
	  fi; \
	done; \
	command -v shellcheck >/dev/null 2>&1 || { \
	  echo "lint: shellcheck not on PATH; CI pins $(shell sed -n 's/^ *sc_ver=\([0-9][0-9.]*\)/\1/p' .github/workflows/ci.yml | head -1) (.github/workflows/ci.yml); any recent distro package is fine locally, e.g.: sudo apt install shellcheck" >&2; exit 2; \
	}
	ruff check .
	ruff format --check .
	mypy $$(git ls-files '*.py')
	for f in $$(git ls-files '*.sh'); do shellcheck --severity=style "$$f"; done

test:
	python3 "$(TOOLS)/tests/test_tool_bootstrap.py"
	python3 "$(TOOLS)/tests/test_ilfmt_safe.py"
	python3 "$(TOOLS)/tests/test_cecil_pin.py"
	python3 "$(TOOLS)/tests/test_dedi_coverage_docs.py"
	python3 "$(TOOLS)/tests/check_stock_facts.py" --require-live
	python3 "$(TOOLS)/tests/test_reach_consistency.py" "$(ASM)"
	python3 "$(TOOLS)/tests/test_committed_inventories_current.py" "$(ASM)"
	python3 "$(TOOLS)/tests/test_surface_wellformed.py" "$(ASM)"
	python3 "$(TOOLS)/tests/test_transport_closure_claims.py"
	python3 "$(TOOLS)/tests/test_coverage_consistency.py"
	python3 "$(TOOLS)/tests/test_promoted_types.py"
	python3 "$(TOOLS)/tests/test_doc_link_integrity.py"
	python3 "$(TOOLS)/tests/test_save_roundtrip_robustness.py"
	python3 "$(TOOLS)/tests/test_save_roundtrip_fuzz.py"
	python3 "$(TOOLS)/tests/test_state_machines_current.py"
	python3 "$(TOOLS)/tests/test_inventory_counts.py"
	python3 "$(TOOLS)/tests/test_subclass_counts.py" "$(ASM)"
	python3 "$(TOOLS)/tests/test_console_cmd_inventory.py" "$(ASM)"
	python3 "$(TOOLS)/tests/test_console_classification.py" "$(ASM)"
	python3 "$(TOOLS)/tests/test_gamestats_gameprefs_current.py" "$(ASM)"
	python3 "$(TOOLS)/tests/test_inventory_type_existence.py" "$(ASM)"
	python3 "$(TOOLS)/tests/test_entityclass_props_current.py" "$(ASM)"
	python3 "$(TOOLS)/tests/test_il_citations.py" "$(ASM)"
	python3 "$(TOOLS)/tests/test_xref_claims.py" "$(ASM)"
	python3 "$(TOOLS)/tests/test_fetch_version_fake_steamcmd.py"
	python3 "$(TOOLS)/tests/test_committed_diff_artifacts.py"
	python3 "$(TOOLS)/tests/test_drift_committed_baseline.py"
	python3 "$(TOOLS)/tests/test_install_integrity.py"
	python3 "$(TOOLS)/tests/test_netprotocol_census.py" "$(ASM)"
	python3 "$(TOOLS)/tests/test_tuned_constants.py" "$(ASM)"

# CI variant: the corpus-invariant gates that need no live DLL, mono, local
# il/ dumps, or the realworld sibling. test_dedi_coverage_docs.py stays in the
# local `make test` (it needs the git-ignored il/ dump sets).
test-docs:
	python3 "$(TOOLS)/tests/test_tool_bootstrap.py"
	python3 "$(TOOLS)/tests/test_asm_discovery.py"
	python3 "$(TOOLS)/tests/test_tool_cli_usage.py"
	python3 "$(TOOLS)/tests/test_shell_cli_usage.py"
	python3 "$(TOOLS)/tests/test_python_cli_usage.py"
	python3 "$(TOOLS)/tests/test_cli_args_wired.py"
	python3 "$(TOOLS)/tests/test_tools_layout.py"
	python3 "$(TOOLS)/tests/test_release_script.py"
	python3 "$(TOOLS)/tests/test_cecil_pin.py"
	python3 "$(TOOLS)/tests/test_census_pct_history.py"
	python3 "$(TOOLS)/tests/test_transport_closure_claims.py"
	python3 "$(TOOLS)/tests/test_coverage_consistency.py"
	python3 "$(TOOLS)/tests/test_promoted_types.py"
	python3 "$(TOOLS)/tests/test_doc_link_integrity.py"
	python3 "$(TOOLS)/tests/test_save_roundtrip_robustness.py"
	python3 "$(TOOLS)/tests/test_save_roundtrip_fuzz.py"
	python3 "$(TOOLS)/tests/test_sandbox_safe_name.py"
	python3 "$(TOOLS)/tests/test_sandbox_requirements_sync.py"
	python3 "$(TOOLS)/tests/test_sandbox_preset_codes.py"
	python3 "$(TOOLS)/tests/test_sandbox_zig_tables.py"
	python3 "$(TOOLS)/tests/test_xml_pins_gate.py"
	python3 "$(TOOLS)/tests/test_gate_unreadable_files.py"
	python3 "$(TOOLS)/tests/test_parity_diff.py"
	python3 "$(TOOLS)/tests/test_parity_drift_fail_closed.py"
	python3 "$(TOOLS)/tests/test_steam_builds.py"
	python3 "$(TOOLS)/tests/test_steam_manifest.py"
	python3 "$(TOOLS)/tests/test_steam_manifest_fuzz.py"
	python3 "$(TOOLS)/tests/test_research_diff.py"
	python3 "$(TOOLS)/tests/test_generation_stamp.py"
	python3 "$(TOOLS)/tests/test_bounded_runs.py"
	python3 "$(TOOLS)/tests/test_state_machines_current.py"
	python3 "$(TOOLS)/tests/test_inventory_counts.py"
	python3 "$(TOOLS)/tests/test_readme_test_table.py"

# Everything in one command: doc gates (no DLL), pins, readiness, facts view.
# make test (the DLL-dependent suite) is separate: it needs the live game.
# The prerequisites re-derive the committed pins from the live DLL, so a clone
# without one has to be turned away before they run, not after a minute of
# gates have failed with unrelated pin-mismatch noise. `make test-docs` is the
# no-DLL path; the error says so.
verify:
	@test -f "$(ASM)" || { \
	  echo "verify: no Assembly-CSharp.dll resolved (got '$(ASM)')" >&2; \
	  echo "verify: this gate re-checks committed pins against a live game install." >&2; \
	  echo "verify: point it at yours ($(ASM_VARS), or ASM=/path/to/Assembly-CSharp.dll)," >&2; \
	  echo "verify: or run 'make test-docs' for the DLL-free gate CI runs." >&2; \
	  exit 2; }
	@$(MAKE) --no-print-directory verify-live

verify-live: test-docs stock-check readiness facts
	@test -n "$(GAME_ROOT)" || { \
	  echo "verify: ASM='$(ASM)' is not under a dedicated-server install root;" >&2; \
	  echo "verify: pass GAME_ROOT=<install root> for the Data/Config pins." >&2; \
	  exit 2; }
	python3 "$(TOOLS)/xml_pins.py" --check --game-dir "$(GAME_ROOT)"
	@echo "verify: ALL GATES GREEN (doc links, pins, readiness, facts, xml data)"

cross-links:
	python3 "$(TOOLS)/cross_repo_links.py"

sibling-cites:
	python3 "$(TOOLS)/zdtd_cite_check.py"

# Not in `make test`: needs a stock-written probe save (created by the live
# sessions, e.g. ~/.cache/7dtd-loadgen-*/Saves/*/*/); fails gracefully if none.
save-roundtrip:
	python3 "$(TOOLS)/save_roundtrip_check.py"

# Every probe save plus the TFP-shipped Navezgane world header. Fails on the
# first broken save; skips gracefully when no probe saves exist.
save-roundtrip-all:
	@fail=0; found=0; \
	for d in $$HOME/.cache/7dtd-loadgen-*/Saves/*/*/; do \
	  [ -f "$$d/main.ttw" ] || continue; found=1; \
	  echo "== $$(basename "$$d")"; \
	  python3 "$(TOOLS)/save_roundtrip_check.py" "$$d" >/dev/null || fail=1; \
	done; \
	[ "$$found" = 1 ] || echo "no probe saves found (run a live session first)"; \
	server="$${SEVENDTD_SERVER_DIR:-$(GAME_ROOT)}"; \
	[ -n "$$server" ] || { \
	  echo "save-roundtrip-all: no dedicated-server install root; set $(ASM_VARS) or SEVENDTD_SERVER_DIR" >&2; \
	  exit 2; }; \
	echo "== shipped Navezgane"; \
	python3 "$(TOOLS)/save_roundtrip_check.py" --shipped "$$server/Data/Worlds/Navezgane" >/dev/null || fail=1; \
	exit $$fail
