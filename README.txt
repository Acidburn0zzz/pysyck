
============================================================
PySyck: Python bindings for the Syck YAML parser and emitter
============================================================

:Author: Kirill Simonov
:Contact: xi@resolvent.net
:Web site: http://xitology.org/pysyck/

.. contents::

Overview
========

YAML_ is a data serialization format designed for human readability and
interaction with scripting languages.

Syck_ is an extension for reading and writing YAML in scripting languages. Syck
provides bindings to the Python_ programming language, but they are somewhat
limited and leak memory.

PySyck_ is aimed to update the current Python bindings for Syck. The new
bindings will provide wrappers for the Syck emitter and give access to the bare
Parser tree. Hopefully it will not leak memory as well.

.. _YAML: http://yaml.org/
.. _Syck: http://whytheluckystiff.net/syck/
.. _Python: http://python.org/
.. _PySyck: http://xitology.org/pysyck/

Requirements
============

PySyck requires Syck 0.55 or higher and Python 2.3 or higher. Python 2.2 is
supported to some extent.

Installation
============

PySyck requires Syck version 0.55 or higher. If you install it from source, unpack
the source tarball and type::

    $ python setup.py install

Windows binaries for Python 2.2, 2.3, and 2.4 are provided.

Usage
=====

FIXME: Documentation is always needed, but also hard to write...

Development and Bug Reports
===========================

You may check out the PySyck_ source code from `PySyck SVN repository`_.

If you find a bug in PySyck_, please file a bug report to `PySyck BTS`_. You
may review open bugs on `the list of active tickets`_.

.. _PySyck SVN repository: http://svn.xitology.org/pysyck/
.. _PySyck BTS: http://trac.xitology.org/pysyck/newticket
.. _the list of active tickets: http://trac.xitology.org/pysyck/report/1

Author and Copyright
====================

The PySyck_ module was written by `Kirill Simonov`_.

PySyck_ is released under the BSD license as Syck_ itself.

.. _Kirill Simonov: mailto:xi@resolvent.net

