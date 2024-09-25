.PHONY: test
test:
	python -munittest discover

.PHONY: typecheck
typecheck:
	mypy --strict . || true
	pyright . || true

.PHONY: codegen
codegen:
	python -mwayland.codegen

.PHONY: coverage
coverage:
	coverage run -m unittest discover
	coverage html

.PHONY: basic
basic:
	PYTHONPATH=. python ./examples/basic.py

.PHONY: metaballs
metaballs:
	PYTHONPATH=. python ./examples/metaballs.py

.PHONY: globals
globals:
	PYTHONPATH=. python ./examples/globals.py
