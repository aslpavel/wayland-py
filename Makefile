.PHONY: typecheck
typecheck:
	mypy --strict .
	pyright .

.PHONY: codegen
codegen:
	python -mwayland.codegen
