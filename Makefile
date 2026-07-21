.PHONY: test lint check

test:
	pytest

lint:
	ruff check .

check: lint test
