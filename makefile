.PHONY: format lint typecheck test

format:
	black src
	isort src

lint:
	flake8 src

typecheck:
	mypy src

test:
	pytest tests
