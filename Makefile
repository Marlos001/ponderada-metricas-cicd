.PHONY: install lint typecheck test test-fast test-expanded test-slow test-failing collect charts clean

PYTHON ?= $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python; fi)
PYTEST ?= $(PYTHON) -m pytest

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

lint:
	$(PYTHON) -m ruff check .

typecheck:
	$(PYTHON) -m mypy src scripts

test:
	$(PYTEST) --junitxml=artifacts/pytest-results.xml

test-fast:
	$(PYTEST) -m "not slow and not expanded and not experimental_failure" --junitxml=artifacts/pytest-results.xml

test-expanded:
	$(PYTEST) -m "not slow and not experimental_failure" --junitxml=artifacts/pytest-results.xml

test-slow:
	$(PYTEST) -m "not experimental_failure" --junitxml=artifacts/pytest-results.xml

test-failing:
	ENABLE_EXPERIMENTAL_FAILURE=1 $(PYTEST) -m "experimental_failure" --junitxml=artifacts/pytest-results.xml

collect:
	$(PYTHON) scripts/collect_metrics.py --owner Marlos001 --repo ponderada-metricas-cicd --workflow ci.yml

collect-local:
	$(PYTHON) scripts/collect_metrics.py --owner Marlos001 --repo ponderada-metricas-cicd --workflow ci.yml --artifacts-dir . --local-artifacts-only

charts:
	$(PYTHON) scripts/generate_charts.py --input data/pipeline_metrics.csv --output-dir charts

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage coverage.xml artifacts/*.xml charts/*.png
