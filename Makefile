.DEFAULT_GOAL := help
.PHONY: lint test test-cov fmt check clean help

lint:  ## Run ruff linter on tools/ and config/
	ruff check tools/ config/

test:  ## Run all tests
	pytest tests/ -v --tb=short

test-cov:  ## Run tests with coverage report
	pytest --cov=tools --cov=config tests/ --cov-report=term-missing

fmt:  ## Auto-format code with ruff
	ruff format tools/ config/ tests/

check: lint test  ## Run lint + test

clean:  ## Remove temporary and generated files
	rm -rf .tmp/ .coverage .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
