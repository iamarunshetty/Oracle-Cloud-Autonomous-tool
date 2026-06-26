# Oracle Fusion Access Manager – Makefile
# Requires: make (Windows: choco install make  or use Git Bash)
# All commands should be run from the repository root.

PYTHON ?= python
PIP    ?= pip
VENV   ?= .venv

.PHONY: help venv install run test lint build-exe package clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'

venv:  ## Create virtual environment
	$(PYTHON) -m venv $(VENV)
	@echo "Activate with: source $(VENV)/bin/activate  (Linux/macOS)"
	@echo "            or: .\\$(VENV)\\Scripts\\activate  (Windows)"

install:  ## Install Python dependencies
	$(PIP) install -r requirements.txt

run:  ## Launch the desktop application
	$(PYTHON) main.py

test:  ## Run unit tests
	$(PYTHON) -m pytest tests/ -v

lint:  ## Run linter (ruff)
	$(PYTHON) -m ruff check app/ tests/ main.py

build-exe:  ## Build single-file Windows EXE with PyInstaller
	$(PIP) install pyinstaller
	pyinstaller --noconfirm FusionAccessManager.spec

package:  ## (Windows + Inno Setup) Create installer EXE
	@echo "Run Inno Setup Compiler on installer.iss"
	@echo "  ISCC installer.iss"

templates:  ## (Re)generate Excel template files
	$(PYTHON) -m app.services.template_generator

clean:  ## Remove build artefacts
	rm -rf dist/ build/ __pycache__ .pytest_cache
	find . -name "*.pyc" -delete
