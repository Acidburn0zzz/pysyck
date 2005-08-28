
.PHONY: default build force install test clean	\
	dist-win dist-win-2.2 dist-win-2.3 dist-win-2.4

PYTHON=/usr/bin/python
TEST=
PARAMETERS=

default: build README.html

build:
	${PYTHON} setup.py build ${PARAMETERS}

force:
	${PYTHON} setup.py build -f ${PARAMETERS}

install: build
	${PYTHON} setup.py install ${PARAMETERS}

test: build
	${PYTHON} tests/test_build.py -v ${TEST}

clean:
	${PYTHON} setup.py clean -a

dist-win: dist-win-2.2 dist-win-2.3 dist-win-2.4

dist-win-2.2: PYTHON=/c/Python22/python
dist-win-2.2: PARAMETERS=--compiler=mingw32
dist-win-2.2:
	${PYTHON} setup.py build ${PARAMETERS}
	${PYTHON} setup.py bdist_wininst

dist-win-2.3: PYTHON=/c/Python23/python
dist-win-2.3: PARAMETERS=--compiler=mingw32
dist-win-2.3:
	${PYTHON} setup.py build ${PARAMETERS}
	${PYTHON} setup.py bdist_wininst --skip-build --target-version=2.3

dist-win-2.4: PYTHON=/c/Python24/python
dist-win-2.4: PARAMETERS=--compiler=mingw32
dist-win-2.4:
	${PYTHON} setup.py build ${PARAMETERS}
	${PYTHON} setup.py bdist_wininst --skip-build --target-version=2.4

README.html: README.txt
	rest2html --embed-stylesheet --stylesheet-path=/usr/share/python-docutils/stylesheets/default.css README.txt README.html
