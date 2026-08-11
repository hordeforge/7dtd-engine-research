# 7dtd-research: stock RE tooling + pin gates.
ROOT := $(CURDIR)
TOOLS := $(ROOT)/tools
ASM ?= $(HOME)/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll

.PHONY: tools stock-sync stock-check post-update census drift test readiness help cross-links

help:
	@echo "make tools        - build Mono.Cecil dumpers (tools/bin)"
	@echo "make cross-links  - resolve every cross-repo .md link in the sibling workspace"
	@echo "make stock-sync   - extract stock_facts.json from live DLL + pin check"
	@echo "make stock-check  - pin check only (committed JSON)"
	@echo "make facts        - view the machine-checked stock pins (census/save/behaviour)"
	@echo "make post-update  - after TFP patch: stock-sync + drift (tools/post-update.sh)"
	@echo "make census       - Census.exe against ASM"
	@echo "make drift        - parity drift-check vs baseline"
	@echo "make readiness    - version-update tooling readiness bench (0-100)"
	@echo "make test         - full suite (structural, stock-check, reach, inventories, surface, links)"
	@echo "make test-docs    - DLL-free corpus invariants (runs in CI)"
	@echo "make verify       - one-command gate: doc links, pins, readiness, facts, xml data"
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

post-update:
	cd "$(TOOLS)" && ASM="$(ASM)" ./post-update.sh

census: tools
	@test -f "$(ASM)" || (echo "ASM not found: $(ASM)"; exit 2)
	MONO_PATH="$(TOOLS)/bin" mono "$(TOOLS)/bin/Census.exe" "$(ASM)"
	python3 "$(TOOLS)/census-pct.py" "$(ASM)" --history "$(ROOT)/workspace/outputs/census-history.csv"
	@echo "--- machine-checked stock pins ---"
	python3 "$(TOOLS)/facts.py"

drift:
	cd "$(TOOLS)/parity" && ./drift-check.sh "$(ASM)"

readiness:
	python3 "$(TOOLS)/tests/bench_version_update_tooling.py"

# Regenerate-inventory check: compiles legacy/DumpFrameEntries and re-derives
# the frame-entries inventories from the live DLL (needs mcs + mono).
regen-check:
	python3 "$(TOOLS)/tests/test_re_dump_regen.py"

test:
	python3 "$(TOOLS)/tests/test_dedi_coverage_docs.py"
	python3 "$(TOOLS)/tests/check_stock_facts.py" --require-live
	python3 "$(TOOLS)/tests/test_reach_consistency.py" "$(ASM)"
	python3 "$(TOOLS)/tests/test_committed_inventories_current.py" "$(ASM)"
	python3 "$(TOOLS)/tests/test_surface_wellformed.py" "$(ASM)"
	python3 "$(TOOLS)/tests/test_transport_closure_claims.py"
	python3 "$(TOOLS)/tests/test_coverage_consistency.py"
	python3 "$(TOOLS)/tests/test_doc_link_integrity.py"
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
	python3 "$(TOOLS)/tests/test_netprotocol_census.py" "$(ASM)"
	python3 "$(TOOLS)/tests/test_tuned_constants.py" "$(ASM)"

# CI variant: the corpus-invariant gates that need no live DLL, mono, local
# il/ dumps, or the realworld sibling. test_dedi_coverage_docs.py stays in the
# local `make test` (it needs the git-ignored il/ dump sets).
test-docs:
	python3 "$(TOOLS)/tests/test_transport_closure_claims.py"
	python3 "$(TOOLS)/tests/test_coverage_consistency.py"
	python3 "$(TOOLS)/tests/test_doc_link_integrity.py"
	python3 "$(TOOLS)/tests/test_state_machines_current.py"
	python3 "$(TOOLS)/tests/test_inventory_counts.py"
	python3 "$(TOOLS)/tests/test_readme_test_table.py"

# Everything in one command: doc gates (no DLL), pins, readiness, facts view.
# make test (the DLL-dependent suite) is separate: it needs the live game.
verify: test-docs stock-check readiness facts
	@test -f "$(ASM)" || (echo "ASM not found: $(ASM) (make verify needs the live game)"; exit 2)
	python3 "$(TOOLS)/xml_pins.py" --check --game-dir "$$(dirname "$$(dirname "$$(dirname "$(ASM)")")")"
	@echo "verify: ALL GATES GREEN (doc links, pins, readiness, facts, xml data)"

cross-links:
	python3 "$(TOOLS)/cross_repo_links.py"
