.DEFAULT_GOAL := help
.PHONY: help install dev ingest index ask eval eval-retrieval api ui check lint fmt types test ci clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Editable install with dev extras
	python -m pip install -e ".[dev]"

dev: ## Dev install with optional adapters
	python -m pip install -e ".[dev,qdrant]"

ingest: ## Parse, clean and chunk data/corpus/
	python scripts/ingest.py --input $${CI_CORPUS_DIR:-data/corpus} --out data/chunks.jsonl

validate-corpus: ## Corpus validation report
	python scripts/ingest.py --input $${CI_CORPUS_DIR:-data/corpus} --validate

index: ## Embed and index chunks
	python scripts/index.py --chunks data/chunks.jsonl

ask: ## Ask a coverage question — make ask QUESTION="..." DATE_OF_LOSS=YYYY-MM-DD
	python scripts/ask.py --question "$(QUESTION)" $(if $(DATE_OF_LOSS),--date-of-loss $(DATE_OF_LOSS),)

eval: ## Run the full golden evaluation suite
	python scripts/evaluate.py --suite golden

eval-retrieval: ## Retrieval-only evaluation (tuning — dev set)
	python scripts/evaluate.py --suite dev --stage retrieval

api: ## Serve the API with reload
	uvicorn coverage_intel.api.app:app --reload --host $${CI_API_HOST:-127.0.0.1} --port $${CI_API_PORT:-8000}

ui: ## Launch the frontend
	cd ui && npm run dev

lint: ## ruff check
	ruff check src tests scripts

fmt: ## ruff format
	ruff format src tests scripts

types: ## mypy
	mypy src

test: ## pytest
	pytest -q

check: lint types test ## Lint + type-check + test

ci: check ## Everything CI runs

clean: ## Remove build artifacts and caches
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
