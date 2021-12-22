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

.PHONY: basic
basic:
	PYTHONPATH=. python ./examples/basic.py

.PHONY: metaballs
metaballs:
	PYTHONPATH=. python ./examples/metaballs.py

