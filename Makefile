SHELL=/bin/bash

clean:
	-rm -f *.pyc MANIFEST
	-rm -rf build dist

test:
	PYTHONPATH=`pwd` python2.6 test_mprop.py
	PYTHONPATH=`pwd` python2.7 test_mprop.py
	PYTHONPATH=`pwd` python3.3 test_mprop.py
	PYTHONPATH=`pwd` python3.4 test_mprop.py
	PYTHONPATH=`pwd` python3.5 test_mprop.py
	PYTHONPATH=`pwd` python3.6 test_mprop.py

install:
	python setup.py install

upload:
	python3.11 setup.py sdist | \
		grep 'mprop-[.0-9]*' | \
		awk '{print $$2}' | \
		head -n1 | \
		xargs -I REP python3.11 -m twine upload "dist/REP.tar.gz"
