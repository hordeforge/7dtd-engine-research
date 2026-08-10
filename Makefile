# 7dtd-research: stock RE tooling + pin gates.
ROOT := $(CURDIR)
TOOLS := $(ROOT)/tools
ASM ?= $(HOME)/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll

.PHONY: tools stock-sync stock-check post-update census drift test readiness help

help:
	@echo "make tools        - build Mono.Cecil dumpers (tools/bin)"
	@echo "make stock-sync   - extract stock_facts.json from live DLL + pin check"
	@echo "make stock-check  - pin check only (committed JSON)"
	@echo "make post-update  - after TFP patch: stock-sync + drift (tools/post-update.sh)"
	@echo "make census       - Census.exe against ASM"
	@echo "make drift        - parity drift-check vs baseline"
	@echo "make readiness    - version-update tooling readiness bench (0-100)"
	@echo "make test         - structural + stock-check (no live dump regen)"

tools:
	cd "$(TOOLS)" && ./build.sh --skip-legacy

stock-sync:
	cd "$(TOOLS)" && ASM="$(ASM)" ./stock-sync.sh

stock-check:
	cd "$(TOOLS)" && ./stock-sync.sh --check-only

post-update:
	cd "$(TOOLS)" && ASM="$(ASM)" ./post-update.sh

census: tools
	@test -f "$(ASM)" || (echo "ASM not found: $(ASM)"; exit 2)
	MONO_PATH="$(TOOLS)/bin" mono "$(TOOLS)/bin/Census.exe" "$(ASM)"
	python3 "$(TOOLS)/census-pct.py" "$(ASM)"

drift:
	cd "$(TOOLS)/parity" && ./drift-check.sh "$(ASM)"

readiness:
	python3 "$(TOOLS)/tests/bench_version_update_tooling.py"

test:
	python3 "$(TOOLS)/tests/test_dedi_coverage_docs.py" || true
	python3 "$(TOOLS)/tests/check_stock_facts.py" --require-live
	python3 "$(TOOLS)/tests/test_reach_consistency.py" "$(ASM)"
	python3 "$(TOOLS)/tests/test_committed_inventories_current.py" "$(ASM)"
	python3 "$(TOOLS)/tests/test_transport_closure_claims.py"
	python3 "$(TOOLS)/tests/test_coverage_consistency.py"
	python3 "$(TOOLS)/tests/test_doc_link_integrity.py"

# CI variant: the corpus-invariant gates that need no live DLL or mono.
# The full `make test` additionally needs the installed game assembly.
test-docs:
	python3 "$(TOOLS)/tests/test_dedi_coverage_docs.py"
	python3 "$(TOOLS)/tests/test_transport_closure_claims.py"
	python3 "$(TOOLS)/tests/test_coverage_consistency.py"
	python3 "$(TOOLS)/tests/test_doc_link_integrity.py"
