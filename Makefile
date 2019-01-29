
all: build

test:
	pip install -r requirements-test.txt
	tox

build:
	@echo "Build source and binary package..."
	@python setup.py sdist bdist_wheel

upload: build
	@echo "Upload package to PyPI..."
	@python setup.py upload

clean:
	@rm -rf build dist __pycache__ xueqiu.egg-info