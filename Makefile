.PHONY: codegen
codegen:
	python -mwayland.codegen

.PHONY: typecheck
typecheck:
	mypy --strict .
	pyright .
