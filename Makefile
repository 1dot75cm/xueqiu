
all: build

test:
	pip install -r requirements-test.txt
	tox

build:
	@echo "Build source and binary package..."
	@python setup.py -q sdist bdist_wheel

upload: build
	@echo "Upload package to PyPI..."
	@twine upload dist/*

clean:
	@rm -rf build dist __pycache__ xueqiu.egg-info