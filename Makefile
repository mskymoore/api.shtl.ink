.PHONY: docker-image install-dependencies lint-diff lint-in-place test test-failed

default: build

build: install-dependencies
	python3 -m build

docker-image:
	docker build -t shtl-ink-api .

start-local-docker:
	docker run --rm -it -e APP_NAME -e BASE_URL -e FRONTEND_BASE_URL -e SUPERTOKENS_CONN_URI -e SUPERTOKENS_API_KEY -e COOKIE_DOMAIN -p 8000:8000/tcp shtl-ink-api:latest

install-dependencies:
	pip3 install -r requirements.txt

lint-diff:
	python3 -m autopep8 --recursive --aggressive --aggressive --diff .

lint-in-place:
	python3 -m autopep8 --recursive --aggressive --aggressive --in-place .

test:
	python3 -m pytest --verbose --cov-report term-missing --cov=shtl_ink_api shtl_ink/tests 

test-failed:
	python3 -m pytest --lf --verbose --cov=shtl_ink shtl_ink/tests
