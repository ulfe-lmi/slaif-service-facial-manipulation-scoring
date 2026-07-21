.PHONY: test lint check serve

test:
	pytest

lint:
	ruff check .

check: lint test

serve:
	uvicorn slaif_fms.api:app --host 0.0.0.0 --port 8000 --workers 1
