SHELL=/bin/bash

clean:
	-rm -f *.pyc MANIFEST
	-rm -rf build dist

install:
	python setup.py install

upload:
	python setup.py sdist
	twine upload dist/*
