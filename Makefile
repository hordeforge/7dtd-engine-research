# 7dtd-research: stock RE tooling + pin gates.
ROOT := $(CURDIR)
TOOLS := $(ROOT)/tools
ASM ?= $(HOME)/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/7DaysToDieServer_Data/Managed/Assembly-CSharp.dll

.PHONY: tools stock-sync stock-check census drift test help

help:
	@echo "make tools        - build Mono.Cecil dumpers (tools/bin)"
	@echo "make stock-sync   - extract stock_facts.json from live DLL + pin check"
	@echo "make stock-check  - pin check only (committed JSON)"
	@echo "make census       - Census.exe against ASM"
	@echo "make drift        - parity drift-check vs baseline"
	@echo "make test         - structural + stock-check (no live dump regen)"

tools:
	cd "$(TOOLS)" && ./build.sh --skip-legacy

stock-sync:
	cd "$(TOOLS)" && ASM="$(ASM)" ./stock-sync.sh

stock-check:
	cd "$(TOOLS)" && ./stock-sync.sh --check-only

census: tools
	@test -f "$(ASM)" || (echo "ASM not found: $(ASM)"; exit 2)
	MONO_PATH="$(TOOLS)/bin" mono "$(TOOLS)/bin/Census.exe" "$(ASM)"

drift:
	cd "$(TOOLS)/parity" && ./drift-check.sh "$(ASM)"

test:
	python3 "$(TOOLS)/tests/test_dedi_coverage_docs.py" || true
	python3 "$(TOOLS)/tests/check_stock_facts.py" --require-live
