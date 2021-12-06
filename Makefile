pip-install:
	python3 -m pip install -r requirements.txt

poetry-install:
	poetry install

build:
	poetry build

update-requirements:
	poetry export --without-hashes > requirements.txt

test:
	python3 run_all_test.py

.PHONY: all test clean
