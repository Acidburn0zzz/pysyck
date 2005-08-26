
.PHONY: default build force install test clean

PYTHON=/usr/bin/python
TEST=

default: build README.html

build:
	${PYTHON} setup.py build

force:
	${PYTHON} setup.py build -f

install: build
	${PYTHON} setup.py install

test: build
	${PYTHON} tests/test_build.py -v ${TEST}

clean:
	${PYTHON} setup.py clean -a

README.html: README.txt
	rest2html --embed-stylesheet --stylesheet-path=/usr/share/python-docutils/stylesheets/default.css README.txt README.html

