.DEFAULT_GOAL := help
POETRY = poetry run

.PHONY: help
help: ## Shows this help text
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: clean
clean: ## Removes project virtual env
	rm -rf .venv cdk.out build dist **/*.egg-info .pytest_cache node_modules .coverage

.PHONY: install
install: ## Install the project dependencies and pre-commit using Poetry.
	poetry install --with lint,test
	${POETRY} pre-commit install --hook-type pre-commit --hook-type commit-msg --hook-type pre-push

## @ test
.PHONY: test
test: ## Run tests coverage
	${POETRY} python -m pytest
coverage:
	${POETRY} pytest --cov=. --cov-report=html tests.py

## @ lint
.PHONY: lint_black flake mypy lint_isort lint
lint_black:
	${POETRY} black --check .
flake:
	${POETRY} flake8 ${FLAKE8_FLAGS} .
mypy:
	${POETRY} mypy .
lint_isort:
	${POETRY} isort ${ISORT_FLAGS} --check .
lint: lint_black flake mypy lint_isort ## roda analise estatica: black, flake, mypy e isort

## @ format
.PHONY: black isort format
black:
	${POETRY} black .
isort:
	${POETRY} isort ${ISORT_FLAGS} .
format: isort black ## roda formatacao nos arquivos da pasta usando black e isort

.PHONY: check
check: ## Check code style and quality using flake8
	${POETRY} flake8 .
