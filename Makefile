ZIP_FILE=mineralWearEval.zip

install-dependencies:
	pip3 install -r requirements.txt

lint-diff:
	python3 -m autopep8 --recursive --aggressive --aggressive --diff .

lint-do:
	python3 -m autopep8 --recursive --aggressive --aggressive --in-place .

test:
	python3 -m pytest --verbose --cov-report term-missing --cov=src src/tests 

test-failed:
	python3 -m pytest --lf --verbose --cov=src src/tests

zip:
	if test -e [[ $(ZIP_FILE) ]];then rm $(ZIP_FILE);fi

	rm -rf __pycache__ src/__pycache__ src/question_1/__pycache__ src/question_2/__pycache__ src/models/__pycache__ src/tests/__pycache__
	zip -r mineralWearEval  * -x *.db .*