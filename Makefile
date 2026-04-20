# Default tests run with make test and make quick-tests
NOSE_TESTS?=tests gxformat2
# Default environment for make tox
ENV?=py39
# Extra arguments supplied to tox command
ARGS?=
# Location of virtualenv used for development.
VENV?=.venv
# Source virtualenv to execute command (flake8, sphinx, twine, etc...)
IN_VENV=if [ -f $(VENV)/bin/activate ]; then . $(VENV)/bin/activate; fi;
# TODO: add this upstream as a remote if it doesn't already exist.
UPSTREAM?=galaxyproject
SOURCE_DIR?=gxformat2
BUILD_SCRIPTS_DIR=scripts
DEV_RELEASE?=0
VERSION?=$(shell DEV_RELEASE=$(DEV_RELEASE) python $(BUILD_SCRIPTS_DIR)/print_version_for_release.py $(SOURCE_DIR) $(DEV_RELEASE))
DOC_URL?=https://gxformat2.readthedocs.org
PROJECT_NAME?=gxformat2
UPSTREAM_REPO?=$(UPSTREAM)/$(PROJECT_NAME)
PROJECT_URL?=https://github.com/$(UPSTREAM_REPO)
TEST_DIR?=tests
DOCS_DIR?=docs

.PHONY: clean-pyc clean-build docs clean

help:
	@egrep '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

setup-venv: ## setup a development virutalenv in current directory
	if command -v uv > /dev/null 2>&1; then \
		uv sync --group test --group lint --group mypy --group docs; \
	else \
		if [ ! -d $(VENV) ]; then \
			python3 -m venv $(VENV); \
		fi; \
		$(IN_VENV) pip install -r requirements.txt && pip install -r dev-requirements.txt; \
	fi

setup-pre-commit: ## install pre-commit hook (uses .pre-commit-config.yaml if present, else the .sample)
	@if [ -f .pre-commit-config.yaml ]; then \
		$(IN_VENV) pre-commit install; \
	else \
		$(IN_VENV) pre-commit install --config .pre-commit-config.yaml.sample; \
	fi

lint: ## check style with ruff, flake8, black, and mypy
	uv run --group lint isort --check --diff .
	uv run --group lint ruff check
	uv run --group lint flake8
	uv run --group lint black --check --diff .
	uv run --group mypy mypy gxformat2
	SKIP_JAVA=1 SKIP_TYPESCRIPT=1 GXFORMAT2_SCHEMA_BUILD_DRY_RUN=1 bash build_schema.sh

lint-docs: ready-docs
	$(IN_VENV) $(MAKE) -C $(DOCS_DIR) clean
	$(IN_VENV) $(MAKE) -C $(DOCS_DIR) html 2>&1 | python $(BUILD_SCRIPTS_DIR)/lint_sphinx_output.py

test: ## run tests with the default Python (faster than tox)
	uv run --group test pytest tests/

tox: ## run tests with tox in the specified ENV
	$(IN_VENV) tox -e $(ENV) -- $(ARGS)

coverage: ## check code coverage quickly with the default Python
	coverage run --source $(SOURCE_DIR) -m pytest $(TEST_DIR)
	coverage report -m
	coverage html
	open htmlcov/index.html || xdg-open htmlcov/index.html

ready-docs:
	rm -f docs/$(SOURCE_DIR).rst
	rm -f docs/modules.rst
	$(IN_VENV) sphinx-apidoc -f -o docs/ $(SOURCE_DIR)

docs: ready-docs ## generate Sphinx HTML documentation, including API docs
	$(IN_VENV) $(MAKE) -C docs clean
	$(IN_VENV) $(MAKE) -C docs html

_open-docs:
	open docs/_build/html/index.html || xdg-open docs/_build/html/index.html

open-docs: docs _open-docs ## generate Sphinx HTML documentation and open in browser

open-rtd: docs ## open docs on readthedocs.org
	open $(DOC_URL) || xdg-open $(PROJECT_URL)

open-project: ## open project on github
	open $(PROJECT_URL) || xdg-open $(PROJECT_URL)

dist: clean ## package
	$(IN_VENV) python -m build
	$(IN_VENV) twine check dist/*
	ls -l dist

commit-version: ## Update version and history, commit.
	$(IN_VENV) DEV_RELEASE=$(DEV_RELEASE) python $(BUILD_SCRIPTS_DIR)/commit_version.py $(SOURCE_DIR) $(VERSION)

new-version: ## Mint a new version
	$(IN_VENV) DEV_RELEASE=$(DEV_RELEASE) python $(BUILD_SCRIPTS_DIR)/new_version.py $(SOURCE_DIR) $(VERSION)

check-release: ## pre-release checklist: venv, clean tree, history entries, lint, lint-docs
	@echo "==> checking $(VENV) exists"
	@test -d $(VENV) || \
		(echo "ERROR: $(VENV) does not exist; run 'make setup-venv'"; exit 1)
	@echo "==> checking working tree is clean"
	@test -z "$$(git status --porcelain)" || \
		(echo "ERROR: working tree has uncommitted changes or untracked files"; git status --short; exit 1)
	@echo "==> checking UPSTREAM remote '$(UPSTREAM)' points to $(UPSTREAM_REPO)"
	@git remote get-url $(UPSTREAM) 2>/dev/null | grep -q "$(UPSTREAM_REPO)" || \
		(echo "ERROR: remote '$(UPSTREAM)' missing or not pointing to $(UPSTREAM_REPO)."; \
		 echo "  Fix:      git remote add $(UPSTREAM) git@github.com:$(UPSTREAM_REPO).git"; \
		 echo "  Or fork:  make check-release UPSTREAM=<name> UPSTREAM_REPO=<owner>/<repo>"; exit 1)
	@echo "==> checking HISTORY.rst has entries under current .devN header"
	@$(IN_VENV) python $(BUILD_SCRIPTS_DIR)/check_history_entries.py
	@echo "==> make clean && make lint && make lint-docs"
	@$(MAKE) clean
	@$(MAKE) lint
	@$(MAKE) lint-docs
	@echo "==> check-release OK"

release-local: commit-version new-version

push-release: ## Push a tagged release to github
	git push $(UPSTREAM) main
	git push --tags $(UPSTREAM)

release: release-local push-release ## package, review, and upload a release

add-history: ## Reformat HISTORY.rst with data from Github's API
	$(IN_VENV) python $(BUILD_SCRIPTS_DIR)/bootstrap_history.py --acknowledgements

format:
	uv run --group lint isort .
	uv run --group lint black .

mypy:
	uv run --group mypy mypy gxformat2
