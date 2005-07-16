
.PHONY: default build install test clean

PYTHON=/usr/bin/python
TEST=

default: build

build:
	${PYTHON} setup.py build

install: build
	${PYTHON} setup.py install

test: build
	${PYTHON} tests/test_build.py ${TEST}

clean:
	${PYTHON} setup.py clean -a

