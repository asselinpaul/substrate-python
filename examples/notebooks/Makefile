.DEFAULT_GOAL := help
SHELL := /bin/bash

default: help;

.PHONY: help
help:
	@echo "Substrate notebooks"
	@echo ""
	@echo "  ensure               Install dependencies"
	@echo "  update               Update substrate-python to the latest version"

poetry.lock: pyproject.toml
	poetry lock

ensure: poetry.lock
	poetry install --no-root

.PHONY: update
update:
	poetry cache clear pypi --all && poetry update substrate
