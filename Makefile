.PHONY: typecheck
typecheck:
	mypy --strict .
	pyright .

.PHONY: basic
basic:
	PYTHONPATH=. python ./examples/basic.py

.PHONY: codegen
codegen:
	python -mwayland.codegen
