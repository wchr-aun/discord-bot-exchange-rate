.PHONY: test

test:
	PYTHONPATH=. pytest tests/

staging:
	python ./main.py