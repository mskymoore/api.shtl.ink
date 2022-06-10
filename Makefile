install-dependencies:
	pip3 install -r requirements.txt

lint-diff:
	python3 -m autopep8 --recursive --aggressive --aggressive --diff .

lint-do:
	python3 -m autopep8 --recursive --aggressive --aggressive --in-place .

test:
	python3 -m pytest --verbose --cov=src src/tests

