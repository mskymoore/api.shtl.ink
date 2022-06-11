ZIP_FILE=py_url_shortener.zip
VIRTUAL_ENVIRONMENT=.env
TEST_DB=url_records.db

install-dependencies:
	pip3 install -r requirements.txt

lint-diff:
	python3 -m autopep8 --recursive --aggressive --aggressive --diff .

lint-in-place:
	python3 -m autopep8 --recursive --aggressive --aggressive --in-place .

run-api:
	. .env/bin/activate
	uvicorn src.api.app:app --reload

test:
	if test -e [[ $(TEST_DB) ]];then rm $(TEST_DB);fi
    python3 -m pytest --verbose --cov-report term-missing --cov=src src/tests 

test-failed:
	python3 -m pytest --lf --verbose --cov=src src/tests

zip:
	if test -e [[ $(ZIP_FILE) ]];then rm $(ZIP_FILE);fi

	rm -rf __pycache__ src/__pycache__ src/question_1/__pycache__ src/question_2/__pycache__ src/models/__pycache__ src/tests/__pycache__
	zip -r py_url_shortener  * -x *.db .*