#
# containerlog
#

PKG_NAME    := containerlog
PKG_VERSION := $(shell poetry version | awk '{print $$2}')

.PHONY: clean fmt github-tag lint version help
.DEFAULT_GOAL := help

clean:  ## Clean up build artifacts
	rm -rf build/ dist/ *.egg-info htmlcov/ .coverage* .pytest_cache/ \
		containerlog/__pycache__ tests/__pycache__ site/

fmt:  ## Automatic source code formatting
	pre-commit run --all-files

github-tag:  ## Create and push a GitHub tag with the current version
	git tag -a ${PKG_VERSION} -m "${PKG_NAME} version ${PKG_VERSION}"
	git push -u origin ${PKG_VERSION}

lint:  ## Run linting checks on the project source code
	poetry run flake8 containerlog tests benchmarks
	poetry run mypy containerlog
	poetry check

test:  ## Run the project unit tests
	poetry run pytest -s -vv --cov-report html --cov-report term-missing --cov containerlog

version:  ## Print the package version
	@echo "${PKG_VERSION}"

help:  ## Print usage information
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort


# Jenkins CI Pipeline Targets
.PHONY: unit-test pypi-release

setup:
	poetry install

unit-test: test

pypi-release:
	poetry publish --build -u __token__ -p "${TWINE_PASSWORD}"
