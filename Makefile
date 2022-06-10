lint-diff:
	python3 -m autopep8 --recursive --aggressive --aggressive --diff .

lint-in-place:
	python3 -m autopep8 --recursive --aggressive --aggressive --in-place .

test:
	python3 -m pytest -v question_1_test.py