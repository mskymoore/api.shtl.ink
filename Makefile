.PHONY: docker-image install-dependencies lint-diff lint-in-place test test-failed

default: docker-image

build: install-dependencies test
	python3 -m build

docker-image:
	docker build -t shtl_ink .

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
