# NICE Plus build. `make` re-imports sources and rebuilds exports.
PY ?= python3
CYBERFIRE ?= ../cyberfire/operationaltechnology

.PHONY: all import import-nice import-attack import-cyberfire build check

all: import build

import: import-nice import-attack import-cyberfire

import-nice:
	$(PY) scripts/import_nice.py

import-attack:
	$(PY) scripts/import_attack_ics.py

# Optional: needs the sibling puzzles repo. The imported tags are committed,
# so `make build` works without it.
import-cyberfire:
	@if [ -d "$(CYBERFIRE)" ]; then $(PY) scripts/import_cyberfire.py --repo "$(CYBERFIRE)"; \
	else echo "skip import-cyberfire: $(CYBERFIRE) not found"; fi

build:
	$(PY) scripts/build.py

# Schema validation (needs requirements-dev.txt)
check:
	$(PY) scripts/check_schema.py
