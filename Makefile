
all: build

test:
	pip install -r requirements-test.txt
	tox

build:
	@echo "Compress index data..."
	@tar zcf xueqiu/index.dat xueqiu/data/*.csv
	@echo "Build source package..."
	@python setup.py -q sdist

upload: build
	@echo "Upload package to PyPI..."
	@twine upload dist/*

clean:
	@rm -rf build dist __pycache__ xueqiu.egg-info