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

%: ./examples/%.py
	PYTHONPATH=. python $<
