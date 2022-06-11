install-dependencies:
	pip3 install -r requirements.txt

lint-diff:
	python3 -m autopep8 --recursive --aggressive --aggressive --diff .

lint-in-place:
	python3 -m autopep8 --recursive --aggressive --aggressive --in-place .

test:
    python3 -m pytest --verbose --cov-report term-missing --cov=shtl_ink_api src/tests 

test-failed:
	python3 -m pytest --lf --verbose --cov=src src/tests
